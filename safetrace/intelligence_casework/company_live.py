from __future__ import annotations

import argparse
import html
import json
import re
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from safetrace.evidence_vault.model import RegistryEntry, RetentionPolicy
from safetrace.evidence_vault.registry import SourceRegistry
from safetrace.evidence_vault.vault import EvidenceVault

MAX_SOURCE_BYTES = 8 * 1024 * 1024
EXPECTED_CONTENT_TYPES = ("text/html", "text/plain", "application/xhtml+xml")


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._ignore = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self._ignore += 1
        elif tag.lower() in {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "section", "article", "tr", "td", "th"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self._ignore:
            self._ignore -= 1
        elif tag.lower() in {"p", "div", "li", "h1", "h2", "h3", "h4", "section", "article", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._ignore:
            self.parts.append(data)

    def text(self) -> str:
        raw = html.unescape("".join(self.parts)).replace("\xa0", " ")
        lines = [re.sub(r"\s+", " ", line).strip() for line in raw.splitlines()]
        return "\n".join(line for line in lines if line)


def html_to_text(payload: bytes) -> str:
    text = payload.decode("utf-8", errors="replace")
    parser = TextExtractor()
    parser.feed(text)
    return parser.text()


def content_type(value: str | None) -> str:
    return (value or "application/octet-stream").split(";", 1)[0].strip().lower()


def host_for(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def fetch_source(url: str, allowed_hosts: set[str], *, timeout: int = 25) -> tuple[bytes, str, str]:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in allowed_hosts:
        raise ValueError(f"URL is outside reviewed HTTPS allowlist: {url}")
    req = urllib.request.Request(url, headers={
        "User-Agent": "SafeTrace-Intelligence-Casework/2.0 (+evidence-first-public-research)",
        "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.1",
    })
    with urllib.request.urlopen(req, timeout=timeout) as response:
        final_url = response.geturl()
        final = urlparse(final_url)
        if final.scheme != "https" or final.hostname not in allowed_hosts:
            raise ValueError(f"redirect escaped reviewed allowlist: {final_url}")
        ctype = content_type(response.headers.get("Content-Type"))
        if ctype not in EXPECTED_CONTENT_TYPES:
            raise ValueError(f"unexpected content type {ctype} for {url}")
        length = response.headers.get("Content-Length")
        if length and int(length) > MAX_SOURCE_BYTES:
            raise ValueError(f"source too large: {url}")
        payload = response.read(MAX_SOURCE_BYTES + 1)
        if len(payload) > MAX_SOURCE_BYTES:
            raise ValueError(f"source exceeds maximum size: {url}")
        if not payload:
            raise ValueError(f"empty source: {url}")
        return payload, ctype, final_url


def build_registry(case: dict[str, Any], reviewed_at: str) -> SourceRegistry:
    policy = RetentionPolicy(
        policy_id="retain-live-company-public-sources",
        name="Retain public company investigation originals",
        applies_to=("original", "parsed", "extraction"),
        minimum_days=None,
        expiry_action="retain",
        legal_hold=False,
        reviewed_by="portfolio-maintainer",
        reviewed_at=reviewed_at,
    )
    entries = []
    for source in case["sources"]:
        entries.append(RegistryEntry(
            source_id=source["id"],
            title=source["title"],
            publisher=source["publisher"],
            canonical_url=source["url"],
            source_type=source["source_type"],
            source_rank=source["source_rank"],
            jurisdiction=source.get("jurisdiction"),
            update_cadence=source.get("update_cadence", "unknown"),
            connector_id="safetrace.http-public-company-source",
            connector_version="2.0",
            parser_id="safetrace.html-text",
            parser_version="2.0",
            expected_content_types=EXPECTED_CONTENT_TYPES,
            retention_policy_id=policy.policy_id,
            reviewed_by="portfolio-maintainer",
            reviewed_at=reviewed_at,
            notes=source.get("notes", "Reviewed public source; conclusions remain bounded to extracted evidence."),
        ))
    return SourceRegistry(entries, [policy])


def context_snippet(text: str, start: int, end: int, radius: int = 120) -> str:
    lo = max(0, start - radius)
    hi = min(len(text), end + radius)
    return re.sub(r"\s+", " ", text[lo:hi]).strip()


def normalise_fact(field: str, value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip(" ,.;:\n\t")
    if field == "address":
        return value.replace("Kirchstr.", "Kirchstraße").replace("Kirchstrasse", "Kirchstraße")
    if field == "register_id":
        return re.sub(r"\s+", " ", value.upper())
    if field == "share_capital_eur":
        digits = re.sub(r"[^0-9]", "", value)
        if len(digits) >= 2 and value.endswith("00"):
            digits = digits[:-2]
        return digits
    if field == "incorporation_date":
        return value
    return value


def extract_facts(source: dict[str, Any], text: str) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for rule in source.get("extract", []):
        flags = re.IGNORECASE | re.MULTILINE
        matches = list(re.finditer(rule["pattern"], text, flags))
        if not matches:
            if rule.get("required", False):
                facts.append({
                    "field": rule["field"], "status": "required_not_found", "value": None,
                    "source_id": source["id"], "evidence": None, "confidence": 0.0,
                })
            continue
        for match in matches[: rule.get("max_matches", 1)]:
            value = match.group(rule.get("group", 1)) if match.groups() else match.group(0)
            facts.append({
                "field": rule["field"],
                "status": "extracted",
                "value": normalise_fact(rule["field"], value),
                "raw_value": value.strip(),
                "source_id": source["id"],
                "evidence": context_snippet(text, match.start(), match.end()),
                "confidence": float(rule.get("confidence", source.get("authority", 0.7))),
            })
    return facts


def reconcile_facts(facts: list[dict[str, Any]], sources: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for fact in facts:
        if fact["status"] == "extracted" and fact.get("value"):
            grouped.setdefault(fact["field"], []).append(fact)
    claims, contradictions = [], []
    for field, rows in sorted(grouped.items()):
        values: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            values.setdefault(row["value"], []).append(row)
        if len(values) == 1:
            value, support = next(iter(values.items()))
            claims.append({
                "field": field,
                "value": value,
                "status": "corroborated" if len({x["source_id"] for x in support}) > 1 else "single_source",
                "confidence": round(max(x["confidence"] for x in support), 2),
                "evidence": [{"source_id": x["source_id"], "snippet": x["evidence"]} for x in support],
            })
        else:
            variants = []
            for value, support in values.items():
                max_authority = max(float(sources[x["source_id"]].get("authority", 0.5)) for x in support)
                variants.append({"value": value, "max_source_authority": max_authority, "sources": [x["source_id"] for x in support]})
            contradictions.append({
                "field": field,
                "status": "unresolved",
                "variants": sorted(variants, key=lambda x: (-x["max_source_authority"], x["value"])),
                "rule": "Do not silently choose among conflicting live sources. Prefer authoritative records only after analyst verification.",
            })
    return claims, contradictions


def render_report(result: dict[str, Any]) -> str:
    lines = [
        f"# Live Intelligence Assessment — {result['case']['title']}", "",
        f"**Run:** {result['run']['retrieved_at']}",
        f"**Question:** {result['case']['question']}", "",
        "## Executive judgement", "",
        result["executive_judgement"], "",
        "## Verified / bounded facts", "",
    ]
    for claim in result["claims"]:
        lines.append(f"- **{claim['field']}**: {claim['value']} — {claim['status']}, confidence {claim['confidence']:.0%}")
        for ev in claim["evidence"]:
            lines.append(f"  - {ev['source_id']}: {ev['snippet']}")
    if result["contradictions"]:
        lines += ["", "## Contradictions", ""]
        for item in result["contradictions"]:
            variants = "; ".join(f"{v['value']} ({', '.join(v['sources'])})" for v in item["variants"])
            lines.append(f"- **{item['field']}**: {variants}. Status: unresolved.")
    lines += ["", "## Unresolved questions", ""]
    for gap in result["unresolved_questions"]:
        lines.append(f"- **{gap['title']}** — {gap['reason']} Next: {gap['next_step']}")
    lines += ["", "## Source receipts", ""]
    for source in result["sources"]:
        lines.append(f"- {source['id']} — HTTP {source['http_status']} equivalent success; sha256 `{source['sha256']}`; {source['bytes']} bytes; {source['resolved_url']}")
    lines += ["", "## Bottom line", "", result["bottom_line"], ""]
    return "\n".join(lines)


def render_html(result: dict[str, Any]) -> str:
    def esc(v: Any) -> str:
        return html.escape(str(v), quote=True)

    claim_cards = "".join(
        f"<article class='card'><div class='eyebrow'>{esc(c['status'])} · {c['confidence']:.0%}</div><h3>{esc(c['field'].replace('_',' ').title())}</h3><div class='value'>{esc(c['value'])}</div>"
        + "".join(f"<details><summary>{esc(e['source_id'])}</summary><p>{esc(e['snippet'])}</p></details>" for e in c["evidence"])
        + "</article>" for c in result["claims"]
    )
    contradiction_cards = "".join(
        f"<article class='card warn'><div class='eyebrow'>UNRESOLVED CONTRADICTION</div><h3>{esc(x['field'].replace('_',' ').title())}</h3>"
        + "".join(f"<p><b>{esc(v['value'])}</b><br><small>{esc(', '.join(v['sources']))}</small></p>" for v in x["variants"])
        + "</article>" for x in result["contradictions"]
    ) or "<p class='muted'>No cross-source contradictions detected in extracted fields.</p>"
    gaps = "".join(f"<li><b>{esc(g['title'])}</b><span>{esc(g['reason'])}</span><em>{esc(g['next_step'])}</em></li>" for g in result["unresolved_questions"])
    sources = "".join(f"<tr><td>{esc(s['title'])}</td><td>{esc(s['publisher'])}</td><td>{esc(s['bytes'])}</td><td><code>{esc(s['sha256'][:16])}…</code></td><td><a href='{esc(s['resolved_url'])}'>source</a></td></tr>" for s in result["sources"])
    m = result["metrics"]
    return f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{esc(result['case']['title'])} — SafeTrace</title><style>
:root{{--bg:#07100f;--panel:#0e1917;--panel2:#13211f;--line:#263a36;--text:#f1f7f5;--muted:#9bb0aa;--accent:#96e8c4;--warn:#f5c46b}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 Inter,ui-sans-serif,system-ui,-apple-system,sans-serif}}main{{max-width:1180px;margin:auto;padding:48px 24px 80px}}.top{{display:flex;gap:28px;justify-content:space-between;align-items:flex-start;border-bottom:1px solid var(--line);padding-bottom:28px}}h1{{font-size:clamp(36px,6vw,72px);line-height:.96;margin:8px 0 18px;letter-spacing:-.055em;max-width:850px}}h2{{font-size:26px;margin:52px 0 18px;letter-spacing:-.025em}}h3{{margin:8px 0 12px;font-size:17px}}.kicker,.eyebrow{{text-transform:uppercase;letter-spacing:.12em;font-size:11px;color:var(--accent);font-weight:800}}.judgement{{font-size:19px;max-width:900px;color:#dbe9e5}}.metrics{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:28px}}.metric,.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px}}.metric b{{font-size:30px;display:block}}.metric span,.muted,small{{color:var(--muted)}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}}.value{{font-size:24px;font-weight:750;letter-spacing:-.025em;margin-bottom:14px}}details{{border-top:1px solid var(--line);padding:9px 0}}summary{{cursor:pointer;color:var(--accent)}}details p{{color:var(--muted);font-size:13px}}.warn{{border-color:#735f36}}.warn .eyebrow{{color:var(--warn)}}ul.gaps{{list-style:none;padding:0;display:grid;gap:10px}}.gaps li{{padding:16px 18px;background:var(--panel2);border-left:3px solid var(--warn);display:grid;gap:4px}}.gaps span{{color:var(--muted)}}.gaps em{{font-style:normal;color:var(--warn)}}table{{width:100%;border-collapse:collapse;background:var(--panel);border-radius:14px;overflow:hidden}}td,th{{padding:12px 14px;border-bottom:1px solid var(--line);text-align:left}}th{{color:var(--muted);font-size:12px}}a{{color:var(--accent)}}code{{font-size:12px}}@media(max-width:800px){{.metrics{{grid-template-columns:repeat(2,1fr)}}.grid{{grid-template-columns:1fr}}.top{{display:block}}table{{font-size:12px}}}}
</style></head><body><main><section class='top'><div><div class='kicker'>SafeTrace · Live public-source investigation</div><h1>{esc(result['case']['title'])}</h1><p class='judgement'>{esc(result['executive_judgement'])}</p><p class='muted'>Retrieved {esc(result['run']['retrieved_at'])}. Every displayed fact opens to its evidence snippet; absent evidence stays absent.</p></div></section><div class='metrics'><div class='metric'><b>{m['sources_acquired']}</b><span>live sources</span></div><div class='metric'><b>{m['facts_extracted']}</b><span>extractions</span></div><div class='metric'><b>{m['claims']}</b><span>bounded facts</span></div><div class='metric'><b>{m['contradictions']}</b><span>contradictions</span></div><div class='metric'><b>{m['unresolved_questions']}</b><span>open questions</span></div></div><h2>What the investigation found</h2><div class='grid'>{claim_cards}</div><h2>Contradictions</h2><div class='grid'>{contradiction_cards}</div><h2>Still unknown</h2><ul class='gaps'>{gaps}</ul><h2>Evidence receipts</h2><table><thead><tr><th>Source</th><th>Publisher</th><th>Bytes</th><th>SHA-256</th><th></th></tr></thead><tbody>{sources}</tbody></table><h2>Bottom line</h2><p class='judgement'>{esc(result['bottom_line'])}</p></main></body></html>"""


def investigate(case_path: Path, out_dir: Path, *, now: str | None = None) -> dict[str, Any]:
    case = json.loads(case_path.read_text(encoding="utf-8"))
    retrieved_at = now or datetime.now(timezone.utc).isoformat()
    source_map = {x["id"]: x for x in case["sources"]}
    allowed_hosts = {host_for(x["url"]) for x in case["sources"]}
    registry = build_registry(case, retrieved_at)
    vault = EvidenceVault(out_dir / "vault", registry)
    all_facts: list[dict[str, Any]] = []
    source_results: list[dict[str, Any]] = []

    for source in case["sources"]:
        payload, ctype, resolved = fetch_source(source["url"], allowed_hosts)
        receipt, alert = vault.acquire(source["id"], payload, ctype, resolved_url=resolved, metadata={"case_id": case["case"]["id"]})
        text = html_to_text(payload) if ctype in {"text/html", "application/xhtml+xml"} else payload.decode("utf-8", errors="replace")
        facts = extract_facts(source, text)
        all_facts.extend(facts)
        parse_payload = (json.dumps({"text_sha256": sha256(text.encode()).hexdigest(), "characters": len(text)}, sort_keys=True) + "\n").encode()
        vault.transform(operation="parse", input_receipt_ids=[receipt.receipt_id], input_object_hashes=[receipt.object.sha256], outputs=[(parse_payload, "application/json", "parsed", "public")], tool_id="safetrace.html-text", tool_version="2.0", parameters={"characters": len(text)}, case_id=case["case"]["id"])
        source_results.append({
            "id": source["id"], "title": source["title"], "publisher": source["publisher"],
            "canonical_url": source["url"], "resolved_url": resolved, "content_type": ctype,
            "bytes": len(payload), "sha256": receipt.object.sha256, "receipt_hash": receipt.receipt_hash,
            "material_change_state": alert.kind, "http_status": 200,
            "facts_extracted": sum(1 for f in facts if f["status"] == "extracted"),
            "required_not_found": [f["field"] for f in facts if f["status"] == "required_not_found"],
        })

    claims, contradictions = reconcile_facts(all_facts, source_map)
    claim_fields = {c["field"] for c in claims}
    contradiction_fields = {c["field"] for c in contradictions}
    unresolved = []
    for question in case.get("required_questions", []):
        if question["field"] not in claim_fields and question["field"] not in contradiction_fields:
            unresolved.append({**question, "status": "not_established"})
    for contradiction in contradictions:
        spec = next((q for q in case.get("required_questions", []) if q["field"] == contradiction["field"]), None)
        if spec:
            unresolved.append({**spec, "status": "contradictory_sources"})

    integrity = vault.verify_integrity()
    failed_required = [f for f in all_facts if f["status"] == "required_not_found"]
    executive = case["case"]["executive_judgement_template"].format(
        claims=len(claims), contradictions=len(contradictions), unresolved=len(unresolved)
    )
    bottom = (
        f"The live run acquired {len(source_results)} reviewed public sources and produced {len(claims)} bounded facts. "
        f"It left {len(contradictions)} cross-source contradiction(s) and {len(unresolved)} required question(s) unresolved. "
        "No missing shareholder, ownership, sanctions, misconduct or control conclusion is inferred from absence of evidence."
    )
    result = {
        "schema_version": "safetrace.live-company-investigation/2.0",
        "case": case["case"],
        "run": {"retrieved_at": retrieved_at, "mode": "live_public_sources", "allowlisted_hosts": sorted(allowed_hosts)},
        "sources": source_results,
        "facts": all_facts,
        "claims": claims,
        "contradictions": contradictions,
        "unresolved_questions": unresolved,
        "executive_judgement": executive,
        "bottom_line": bottom,
        "integrity": integrity,
        "metrics": {
            "sources_acquired": len(source_results),
            "facts_extracted": sum(1 for f in all_facts if f["status"] == "extracted"),
            "claims": len(claims),
            "contradictions": len(contradictions),
            "unresolved_questions": len(unresolved),
            "required_extractions_missing": len(failed_required),
        },
        "boundary": "Public-source research only. Extraction is evidence retrieval, not an allegation or automated compliance decision. Missing facts remain unresolved.",
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    (out_dir / "index.html").write_text(render_html(result), encoding="utf-8")
    return result


def main() -> int:
    p = argparse.ArgumentParser(description="Acquire reviewed live public company sources and generate evidence-backed casework.")
    p.add_argument("--case", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("artifacts/intelligence-casework/live-company"))
    args = p.parse_args()
    result = investigate(args.case, args.out)
    print(json.dumps(result["metrics"], indent=2))
    print(result["bottom_line"])
    if result["integrity"]["status"] != "pass":
        return 1
    if result["metrics"]["required_extractions_missing"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
