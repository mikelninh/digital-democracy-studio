from __future__ import annotations

import argparse
import html
import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import asdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from safetrace.claim_ledger.ledger import ClaimLedger
from safetrace.claim_ledger.model import (
    ClaimVersion,
    EvidenceLink,
    LedgerClaim,
    VaultEvidenceRef,
)
from safetrace.evidence_vault.model import RegistryEntry, RetentionPolicy
from safetrace.evidence_vault.registry import SourceRegistry
from safetrace.evidence_vault.vault import EvidenceVault

CASE_ID = "case-005"
SCHEMA_VERSION = "safetrace.real-case-release/1.0"
DEFAULT_ACQUIRED_AT = "2026-07-24T12:00:00+00:00"
USER_AGENT = "SafeTrace-Public-Source-Research/1.0 (+https://mikelninh.github.io/digital-democracy-studio/safetrace/)"


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)


def normalize_text(payload: bytes) -> str:
    decoded = payload.decode("utf-8", errors="replace")
    parser = TextExtractor()
    parser.feed(decoded)
    text = html.unescape(" ".join(parser.parts)).replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip()


def fetch_source(url: str, *, attempts: int = 3, timeout: int = 35) -> tuple[bytes, str, str]:
    last_error: Exception | None = None
    for attempt in range(attempts):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
                "Accept-Language": "de-DE,de;q=0.9,en;q=0.6",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read()
                content_type = response.headers.get_content_type() or "application/octet-stream"
                return payload, content_type, response.geturl()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to acquire {url}: {last_error}")


def load_config(root: Path) -> dict[str, Any]:
    return json.loads((root / "sources.json").read_text(encoding="utf-8"))


def build_registry(config: dict[str, Any]) -> SourceRegistry:
    review = config["acquisition_review"]
    policy = RetentionPolicy(
        policy_id="retain-public-originals",
        name="Retain official public originals and receipts",
        applies_to=("original", "normalized", "parsed", "extraction", "export"),
        minimum_days=None,
        expiry_action="retain",
        legal_hold=False,
        reviewed_by=review["reviewed_by"],
        reviewed_at=review["reviewed_at"],
    )
    entries = []
    for source in config["sources"]:
        entries.append(
            RegistryEntry(
                source_id=source["source_id"],
                title=source["title"],
                publisher=source["publisher"],
                canonical_url=source["canonical_url"],
                source_type=source["source_type"],
                source_rank=source["source_rank"],
                jurisdiction=source["jurisdiction"],
                update_cadence=source["update_cadence"],
                connector_id="safetrace-http-public",
                connector_version="1.0",
                parser_id="safetrace-html-text",
                parser_version="1.0",
                expected_content_types=tuple(source["expected_content_types"]),
                retention_policy_id=policy.policy_id,
                reviewed_by=review["reviewed_by"],
                reviewed_at=review["reviewed_at"],
                notes=source["anchor"],
                metadata={"required_markers": source["required_markers"]},
            )
        )
    return SourceRegistry(entries, [policy])


def acquire_sources(
    config: dict[str, Any],
    output_root: Path,
    *,
    fixture_dir: Path | None,
    acquired_at: str,
) -> tuple[EvidenceVault, dict[str, dict[str, Any]]]:
    registry = build_registry(config)
    registry.save(output_root / "registry")
    vault = EvidenceVault(output_root / "vault", registry)
    evidence: dict[str, dict[str, Any]] = {}

    for source in config["sources"]:
        source_id = source["source_id"]
        if fixture_dir:
            path = fixture_dir / f"{source_id}.html"
            payload = path.read_bytes()
            content_type = "text/html"
            resolved_url = source["canonical_url"]
        else:
            payload, content_type, resolved_url = fetch_source(source["canonical_url"])

        if content_type != "text/html":
            raise ValueError(f"Unexpected content type for {source_id}: {content_type}")
        parsed_text = normalize_text(payload)
        folded = parsed_text.casefold()
        missing_markers = [
            marker for marker in source["required_markers"]
            if re.sub(r"\s+", " ", marker).casefold() not in folded
        ]
        if missing_markers:
            raise ValueError(f"Required markers missing for {source_id}: {missing_markers}")

        receipt, alert = vault.acquire(
            source_id,
            payload,
            content_type,
            acquired_at=acquired_at,
            resolved_url=resolved_url,
            normalized_payload=parsed_text.encode("utf-8"),
            metadata={"marker_count": len(source["required_markers"]), "case_id": CASE_ID},
        )
        manifest = vault.transform(
            operation="parse",
            input_receipt_ids=(receipt.receipt_id,),
            input_object_hashes=(receipt.object.sha256,),
            outputs=((parsed_text.encode("utf-8"), "text/plain", "parsed", "public"),),
            tool_id="safetrace-html-text",
            tool_version="1.0",
            created_at=acquired_at,
            parameters={"whitespace_normalized": True, "scripts_removed": True},
            case_id=CASE_ID,
        )
        evidence[source_id] = {
            "source_id": source_id,
            "title": source["title"],
            "publisher": source["publisher"],
            "canonical_url": source["canonical_url"],
            "resolved_url": resolved_url,
            "anchor": source["anchor"],
            "receipt_id": receipt.receipt_id,
            "receipt_hash": receipt.receipt_hash,
            "object_hash": receipt.object.sha256,
            "byte_length": receipt.object.byte_length,
            "content_type": receipt.object.content_type,
            "parsed_object_hash": manifest.outputs[0].sha256,
            "required_markers_verified": len(source["required_markers"]),
            "source_alert": alert.kind,
        }
    return vault, evidence


def evidence_link(
    *, claim_id: str, link_id: str, source_id: str, role: str,
    evidence: dict[str, dict[str, Any]], summary: str, anchor: str,
) -> EvidenceLink:
    item = evidence[source_id]
    return EvidenceLink(
        id=link_id,
        claim_id=claim_id,
        version=1,
        role=role,
        provenance_mode="vault_receipt",
        source_id=source_id,
        anchor=anchor,
        summary=summary,
        added_by="safetrace-research-agent",
        added_at=DEFAULT_ACQUIRED_AT,
        receipt_id=item["receipt_id"],
        object_hash=item["object_hash"],
    )


def build_ledger(evidence: dict[str, dict[str, Any]]) -> tuple[ClaimLedger, dict[str, Any]]:
    vault_index = {
        item["receipt_id"]: VaultEvidenceRef(
            item["receipt_id"], source_id, item["object_hash"]
        )
        for source_id, item in evidence.items()
    }
    ledger = ClaimLedger(vault_index)
    created_at = DEFAULT_ACQUIRED_AT

    definitions = [
        {
            "id": "case005-claim-amount",
            "text": "Das Kindergeld beträgt seit dem 1. Januar 2026 monatlich 259 Euro pro Kind.",
            "legal_status": "in_force",
            "links": [
                ("case005-bundesregierung-implementation-2026", "supporting", "Die Bundesregierung beschreibt die automatische Erhöhung ab Januar 2026 auf 259 Euro.", "Abschnitt Familie"),
                ("case005-bkgg-current-law", "supporting", "§ 6 Absatz 1 BKGG nennt aktuell 259 Euro pro Kind und Monat.", "§ 6 Absatz 1 BKGG"),
            ],
            "limitations": ("Die Aussage beschreibt Höhe und Inkrafttreten, nicht die politische Urheberschaft.",),
        },
        {
            "id": "case005-claim-decision",
            "text": "Der Deutsche Bundestag beschloss die Erhöhung auf 259 Euro am 19. Dezember 2024.",
            "legal_status": "enacted",
            "links": [
                ("case005-bundestag-decision-2024", "supporting", "Der Bundestag dokumentiert Beschlussdatum und Erhöhung mit Wirkung zum 1. Januar 2026.", "Abschnitt Bundestag erhöht Kindergeld"),
            ],
            "limitations": ("Die Abstimmung zeigt den parlamentarischen Beschluss; sie bewertet nicht die spätere Umsetzungspolitik.",),
        },
        {
            "id": "case005-claim-government-start",
            "text": "Die Bundesregierung unter Bundeskanzler Friedrich Merz trat am 6. Mai 2025 ihr Amt an.",
            "legal_status": "not_applicable",
            "links": [
                ("case005-merz-government-start", "supporting", "Die Bundesregierung dokumentiert Wahl, Ernennung und Beginn der Amtszeit am 6. Mai 2025.", "Abschnitt Neue Bundesregierung im Amt"),
            ],
            "limitations": ("Der Amtsbeginn sagt allein nichts über spätere familienpolitische Maßnahmen aus.",),
        },
        {
            "id": "case005-claim-attribution",
            "text": "Die Kindergelderhöhung auf 259 Euro war keine neu beschlossene Maßnahme der Regierung Merz, weil der parlamentarische Beschluss vor deren Amtsantritt lag.",
            "legal_status": "in_force",
            "links": [
                ("case005-bundestag-decision-2024", "supporting", "Der Beschluss erfolgte am 19. Dezember 2024.", "Beschluss und Inkrafttreten"),
                ("case005-merz-government-start", "supporting", "Die Merz-Regierung begann erst am 6. Mai 2025.", "Beginn der Amtszeit"),
                ("case005-bundesregierung-implementation-2026", "context", "Die Leistung wurde ab Januar 2026 in der neuen Höhe ausgezahlt.", "Umsetzung ab Januar 2026"),
            ],
            "limitations": ("Die Regierung Merz setzte geltendes Recht administrativ fort; andere Familienmaßnahmen dieser Regierung sind separat zu bewerten.",),
        },
    ]

    review_candidate: dict[str, Any] = {"claims": [], "reviewer": "Michael Ninh", "status": "awaiting_named_human_review"}
    assignees = {
        "evidence": "michael-ninh",
        "red_team": "michael-ninh",
        "publication": "michael-ninh",
    }
    for definition in definitions:
        links = tuple(
            evidence_link(
                claim_id=definition["id"],
                link_id=f"link:{definition['id']}:{index}",
                source_id=source_id,
                role=role,
                evidence=evidence,
                summary=summary,
                anchor=anchor,
            )
            for index, (source_id, role, summary, anchor) in enumerate(definition["links"], start=1)
        )
        version = ClaimVersion(
            claim_id=definition["id"],
            version=1,
            text=definition["text"],
            evidence_state="verified_fact",
            legal_status=definition["legal_status"],
            sensitivity="public",
            created_by="safetrace-research-agent",
            created_at=created_at,
            evidence_links=links,
            limitations=definition["limitations"],
            metadata={"public_interest": "political_attribution", "identity_sensitive": False},
        )
        claim = LedgerClaim(
            id=definition["id"],
            case_id=CASE_ID,
            researcher_id="safetrace-research-agent",
            material=True,
            status="draft",
            current_version=1,
            created_at=created_at,
            updated_at=created_at,
            versions={1: version},
        )
        ledger.add_claim(claim)
        tasks = ledger.queue_reviews(claim.id, assignees, created_at)
        gate = ledger.evaluate(claim.id)
        review_candidate["claims"].append({
            "claim_id": claim.id,
            "text": version.text,
            "limitations": list(version.limitations),
            "vault_backed": version.vault_backed,
            "required_gates": list(gate.required_gates),
            "current_blockers": list(gate.blockers),
            "tasks": [asdict(task) for task in tasks],
            "evidence": [asdict(link) for link in links],
        })
    return ledger, review_candidate


def public_draft(evidence: dict[str, dict[str, Any]], review: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "safetrace.public-fact-check-draft/1.0",
        "case_id": CASE_ID,
        "title": "Wer hat die Kindergelderhöhung auf 259 Euro beschlossen?",
        "verdict": "Nicht die Regierung Merz: Der Bundestag beschloss die Erhöhung bereits am 19. Dezember 2024; sie trat am 1. Januar 2026 in Kraft.",
        "status": "source_verified_awaiting_named_human_review",
        "publication_allowed": False,
        "source_count": len(evidence),
        "original_receipt_count": len(evidence),
        "claim_count": len(review["claims"]),
        "sources": list(evidence.values()),
        "claims": review["claims"],
        "correction_policy": "Visible corrections and source-version history are mandatory.",
        "impact_measurement": {
            "mode": "consent_based_local_session_export",
            "metrics": ["time_to_answer_seconds", "correct_attribution_before", "correct_attribution_after", "confidence_before", "confidence_after", "clarity_rating"],
            "network_submission": False,
            "aggregate_results_observed": 0,
        },
    }


def write_html(path: Path, draft: dict[str, Any]) -> None:
    sources = "".join(
        f'<article class="source"><b>{html.escape(item["publisher"])}</b><h3>{html.escape(item["title"])}</h3><p>{html.escape(item["anchor"])}</p><code>{item["object_hash"][:20]}…</code><a href="{html.escape(item["canonical_url"])}" rel="noopener" target="_blank">Amtliche Quelle öffnen</a></article>'
        for item in draft["sources"]
    )
    claims = "".join(
        f'<article class="claim"><span>VAULT-BACKED · REVIEW AUSSTEHEND</span><h3>{html.escape(item["text"])}</h3><p>{html.escape(item["limitations"][0])}</p></article>'
        for item in draft["claims"]
    )
    page = f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SafeTrace Case 005</title><style>
    :root{{--bg:#efeee8;--paper:#fffdf7;--ink:#171a17;--muted:#667068;--green:#315d48;--lime:#d9ef8d;--line:#d9d7ce}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,system-ui,sans-serif;line-height:1.5}}header,main,footer{{max-width:1120px;margin:auto;padding:24px}}header{{display:flex;justify-content:space-between}}a{{color:inherit}}.hero{{padding:70px 24px 38px}}h1{{font-size:clamp(3rem,8vw,7rem);line-height:.92;letter-spacing:-.06em;margin:.2em 0}}.verdict{{font-size:1.3rem;max-width:850px}}.status{{display:inline-block;background:#fff1cf;padding:7px 11px;border-radius:999px;font-weight:800}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}}.source,.claim,.study{{background:var(--paper);border:1px solid var(--line);padding:22px;border-radius:18px}}.source a{{display:block;margin-top:14px;font-weight:800}}code{{display:block;color:var(--muted);font-size:.75rem}}.claim span{{font-size:.7rem;color:var(--green);font-weight:900;letter-spacing:.08em}}section{{padding:36px 24px}}button{{border:0;border-radius:11px;padding:11px 15px;background:var(--ink);color:white;font-weight:800;cursor:pointer}}select,input{{padding:9px;border:1px solid var(--line);border-radius:9px}}.study label{{display:block;margin:12px 0}}#result{{white-space:pre-wrap;background:#18221c;color:#dce7df;padding:14px;border-radius:12px;margin-top:14px}}@media(max-width:700px){{.grid{{grid-template-columns:1fr}}}}</style></head><body>
    <header><b>SafeTrace · Real Case Lab</b><a href="../../role_simulator/">Rollen-Simulator</a></header>
    <main><div class="hero"><span class="status">QUELLEN VERIFIZIERT · MENSCHLICHE FREIGABE AUSSTEHEND</span><h1>Wer erhöhte das Kindergeld?</h1><p class="verdict">{html.escape(draft["verdict"])}</p><p>Vier amtliche Originalseiten wurden im Evidence Vault gespeichert und gehasht. Die Veröffentlichung bleibt blockiert, bis Michael den Evidence-, Red-Team- und Publication-Check bewusst abschließt.</p></div>
    <section><h2>Amtliche Quellen</h2><div class="grid">{sources}</div></section>
    <section><h2>Prüfbare Claims</h2><div class="grid">{claims}</div></section>
    <section><div class="study"><h2>Impact-Test</h2><p>Diese Messung bleibt lokal. Lade das Ergebnis anschließend als JSON herunter; es wird nichts übertragen.</p><label>Vor dem Lesen: Wer beschloss die Erhöhung?<select id="before"><option value="">Bitte wählen</option><option>Regierung Merz</option><option>Bundestag im Dezember 2024</option><option>Unklar</option></select></label><label>Confidence vorher (1–5)<input id="confBefore" type="number" min="1" max="5" value="3"></label><label>Nach dem Lesen: Wer beschloss die Erhöhung?<select id="after"><option value="">Bitte wählen</option><option>Regierung Merz</option><option>Bundestag im Dezember 2024</option><option>Unklar</option></select></label><label>Confidence nachher (1–5)<input id="confAfter" type="number" min="1" max="5" value="4"></label><label>Verständlichkeit (1–5)<input id="clarity" type="number" min="1" max="5" value="4"></label><button id="download">Anonymes Sitzungsresultat herunterladen</button><pre id="result" aria-live="polite"></pre></div></section></main><footer>Keine Telemetrie · keine Cookies · keine echte Publikationsentscheidung in dieser Seite</footer>
    <script>const started=Date.now();document.getElementById('download').onclick=()=>{{const payload={{schema_version:'safetrace.impact-session/1.0',case_id:'case-005',duration_seconds:Math.round((Date.now()-started)/1000),correct_attribution_before:document.getElementById('before').value==='Bundestag im Dezember 2024',correct_attribution_after:document.getElementById('after').value==='Bundestag im Dezember 2024',confidence_before:Number(document.getElementById('confBefore').value),confidence_after:Number(document.getElementById('confAfter').value),clarity_rating:Number(document.getElementById('clarity').value),consent:'local_export_only',created_at:new Date().toISOString()}};const text=JSON.stringify(payload,null,2);document.getElementById('result').textContent=text;const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{{type:'application/json'}}));a.download='safetrace-case005-impact-session.json';a.click();URL.revokeObjectURL(a.href)}};</script></body></html>'''
    path.write_text(page, encoding="utf-8")


def build(root: Path, output_root: Path, *, fixture_dir: Path | None, acquired_at: str) -> dict[str, Any]:
    config = load_config(root)
    output_root.mkdir(parents=True, exist_ok=True)
    vault, evidence = acquire_sources(config, output_root, fixture_dir=fixture_dir, acquired_at=acquired_at)
    ledger, review = build_ledger(evidence)
    integrity = vault.verify_integrity()
    draft = public_draft(evidence, review)
    report = {
        "schema_version": SCHEMA_VERSION,
        "case_id": CASE_ID,
        "status": "pass" if integrity["status"] == "pass" and len(evidence) == 4 else "fail",
        "source_acquisition": {
            "official_sources": len(evidence),
            "original_receipts": len(evidence),
            "all_markers_verified": all(item["required_markers_verified"] >= 1 for item in evidence.values()),
        },
        "vault_integrity": integrity,
        "claim_ledger": ledger.summary(),
        "review": {
            "status": review["status"],
            "named_reviewer": review["reviewer"],
            "claims": len(review["claims"]),
            "pending_review_tasks": sum(len(item["tasks"]) for item in review["claims"]),
        },
        "publication": {
            "allowed": False,
            "reason": "Named human evidence, red-team and publication review are pending.",
            "public_draft_generated": True,
        },
        "truthful_status": "Four official originals are vault-backed and marker-verified. The fact-check is a publishable candidate, not yet a published SafeTrace finding, because named human review is pending.",
    }
    for name, payload in (
        ("evidence-index.json", {"schema_version": "safetrace.case005-evidence/1.0", "sources": evidence}),
        ("review-candidate.json", review),
        ("public-draft.json", draft),
        ("release-report.json", report),
    ):
        (output_root / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_html(output_root / "index.html", draft)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Acquire and build SafeTrace real Case 005")
    parser.add_argument("--root", type=Path, default=Path(__file__).parent)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--fixture-dir", type=Path)
    parser.add_argument("--acquired-at", default=DEFAULT_ACQUIRED_AT)
    args = parser.parse_args()
    datetime.fromisoformat(args.acquired_at.replace("Z", "+00:00"))
    report = build(args.root, args.output_root, fixture_dir=args.fixture_dir, acquired_at=args.acquired_at)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
