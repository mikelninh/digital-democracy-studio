from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from safetrace.evidence_vault.vault import EvidenceVault
from safetrace.intelligence_casework.company_live import (
    build_registry,
    extract_facts,
    fetch_source,
    host_for,
    html_to_text,
    reconcile_facts,
)


def _normalise_live_fact(fact: dict[str, Any]) -> dict[str, Any]:
    """Correct high-value formats after generic extraction without hiding the raw value."""
    item = dict(fact)
    if item.get("status") != "extracted":
        return item
    if item.get("field") == "share_capital_eur":
        raw = str(item.get("raw_value") or item.get("value") or "")
        compact = re.sub(r"[^0-9,.-]", "", raw)
        if "," in compact:
            whole, fraction = compact.rsplit(",", 1)
            whole = whole.replace(".", "").replace(",", "")
            if fraction and set(fraction) <= {"0"}:
                item["value"] = str(int(whole or "0"))
            else:
                item["value"] = f"{whole}.{fraction}".lstrip("+")
        else:
            item["value"] = compact.replace(".", "")
    return item


def _render_report(result: dict[str, Any]) -> str:
    lines = [
        f"# Live Intelligence Assessment — {result['case']['title']}", "",
        f"**Run:** {result['run']['retrieved_at']}",
        f"**Question:** {result['case']['question']}", "",
        "## Executive judgement", "",
        result["executive_judgement"], "",
        "## What the investigation established", "",
    ]
    for claim in result["claims"]:
        lines.append(f"- **{claim['field']}**: {claim['value']} — {claim['status']}, confidence {claim['confidence']:.0%}")
        for ev in claim["evidence"]:
            lines.append(f"  - {ev['source_id']}: {ev['snippet']}")
    if not result["claims"]:
        lines.append("- No bounded facts were established from the acquired sources.")

    lines += ["", "## Contradictions", ""]
    if result["contradictions"]:
        for item in result["contradictions"]:
            variants = "; ".join(f"{v['value']} ({', '.join(v['sources'])})" for v in item["variants"])
            lines.append(f"- **{item['field']}**: {variants}. Status: unresolved.")
    else:
        lines.append("- No cross-source contradictions detected among the extracted fields.")

    lines += ["", "## Still unknown / collection gaps", ""]
    for gap in result["unresolved_questions"]:
        lines.append(f"- **{gap['title']}** [{gap['status']}] — {gap['reason']} Next: {gap['next_step']}")
    if not result["unresolved_questions"]:
        lines.append("- No required questions remain open in this bounded case scope.")

    lines += ["", "## Source acquisition and receipts", ""]
    for source in result["sources"]:
        if source["acquisition_status"] == "acquired":
            lines.append(
                f"- **{source['id']}** — acquired HTTP {source['http_status']}; "
                f"sha256 `{source['sha256']}`; receipt `{source['receipt_hash']}`; "
                f"{source['bytes']} bytes; extracted {source['facts_extracted']} fact(s); {source['resolved_url']}"
            )
            if source["required_not_found"]:
                lines.append(f"  - Expected extraction missing: {', '.join(source['required_not_found'])}")
        else:
            lines.append(
                f"- **{source['id']}** — unavailable HTTP {source['http_status']}; no evidence receipt created; "
                f"error: {source['error']}; {source['canonical_url']}"
            )

    lines += ["", "## Bottom line", "", result["bottom_line"], ""]
    return "\n".join(lines)


def _render_html(result: dict[str, Any]) -> str:
    def esc(v: Any) -> str:
        return html.escape(str(v), quote=True)

    claims = "".join(
        f"<article class='card'><div class='eyebrow ok'>{esc(c['status'])} · {c['confidence']:.0%}</div>"
        f"<h3>{esc(c['field'].replace('_', ' ').title())}</h3><div class='value'>{esc(c['value'])}</div>"
        + "".join(
            f"<details><summary>Evidence · {esc(e['source_id'])}</summary><p>{esc(e['snippet'])}</p></details>"
            for e in c["evidence"]
        ) + "</article>" for c in result["claims"]
    ) or "<p class='muted'>No bounded facts established.</p>"

    contradictions = "".join(
        f"<article class='card warning'><div class='eyebrow warn'>UNRESOLVED CONTRADICTION</div>"
        f"<h3>{esc(x['field'].replace('_', ' ').title())}</h3>"
        + "".join(f"<p><b>{esc(v['value'])}</b><br><small>{esc(', '.join(v['sources']))}</small></p>" for v in x["variants"])
        + "</article>" for x in result["contradictions"]
    ) or "<p class='muted'>No cross-source contradictions detected in extracted fields.</p>"

    gaps = "".join(
        f"<li><div><b>{esc(g['title'])}</b><span class='pill'>{esc(g['status'])}</span></div>"
        f"<span>{esc(g['reason'])}</span><em>Next: {esc(g['next_step'])}</em></li>"
        for g in result["unresolved_questions"]
    ) or "<li><b>No required questions remain open.</b></li>"

    source_rows = []
    for s in result["sources"]:
        if s["acquisition_status"] == "acquired":
            status = f"<span class='status good'>ACQUIRED · HTTP {esc(s['http_status'])}</span>"
            receipt = f"<code>{esc(s['sha256'][:16])}…</code><small>{esc(s['bytes'])} bytes · {esc(s['facts_extracted'])} facts</small>"
            gap = ", ".join(s["required_not_found"]) if s["required_not_found"] else "—"
        else:
            status = f"<span class='status bad'>UNAVAILABLE · HTTP {esc(s['http_status'])}</span>"
            receipt = f"<span class='error'>{esc(s['error'])}</span>"
            gap = "source unavailable"
        source_rows.append(
            f"<tr><td><b>{esc(s['title'])}</b><small>{esc(s['publisher'])}</small></td><td>{status}</td>"
            f"<td>{receipt}</td><td>{esc(gap)}</td><td><a href='{esc(s['canonical_url'])}'>open ↗</a></td></tr>"
        )
    m = result["metrics"]
    return f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{esc(result['case']['title'])} — SafeTrace</title><style>
:root{{--bg:#07100f;--panel:#0e1917;--panel2:#13211f;--line:#263a36;--text:#f1f7f5;--muted:#9bb0aa;--accent:#96e8c4;--warn:#f4c36a;--bad:#ff938a}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 Inter,ui-sans-serif,system-ui,-apple-system,sans-serif}}main{{max-width:1180px;margin:auto;padding:48px 24px 80px}}header{{border-bottom:1px solid var(--line);padding-bottom:28px}}h1{{font-size:clamp(36px,6vw,68px);line-height:.98;margin:8px 0 18px;letter-spacing:-.05em;max-width:920px}}h2{{font-size:27px;margin:50px 0 18px;letter-spacing:-.025em}}h3{{margin:8px 0 12px;font-size:17px}}.kicker,.eyebrow{{text-transform:uppercase;letter-spacing:.12em;font-size:11px;font-weight:800}}.kicker,.ok{{color:var(--accent)}}.warn{{color:var(--warn)}}.judgement{{font-size:19px;max-width:940px;color:#dbe9e5}}.muted,small{{color:var(--muted)}}.metrics{{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-top:28px}}.metric,.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px}}.metric b{{font-size:28px;display:block}}.metric span{{color:var(--muted);font-size:12px}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}}.value{{font-size:24px;font-weight:760;letter-spacing:-.025em;margin-bottom:14px}}details{{border-top:1px solid var(--line);padding:9px 0}}summary{{cursor:pointer;color:var(--accent)}}details p{{color:var(--muted);font-size:13px}}.warning{{border-color:#755f35}}ul.gaps{{list-style:none;padding:0;display:grid;gap:10px}}.gaps li{{padding:16px 18px;background:var(--panel2);border-left:3px solid var(--warn);display:grid;gap:5px}}.gaps li div{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}.gaps span{{color:var(--muted)}}.gaps em{{font-style:normal;color:var(--warn)}}.pill{{font-size:10px!important;text-transform:uppercase;letter-spacing:.08em;border:1px solid var(--line);border-radius:999px;padding:2px 7px}}table{{width:100%;border-collapse:collapse;background:var(--panel);border-radius:14px;overflow:hidden}}td,th{{padding:12px 14px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em}}td small{{display:block;margin-top:3px}}.status{{display:inline-block;font-size:10px;font-weight:800;letter-spacing:.07em}}.good{{color:var(--accent)}}.bad,.error{{color:var(--bad)}}a{{color:var(--accent)}}code{{font-size:12px}}@media(max-width:850px){{.metrics{{grid-template-columns:repeat(2,1fr)}}.grid{{grid-template-columns:1fr}}table{{display:block;overflow:auto}}}}
</style></head><body><main><header><div class='kicker'>SafeTrace · live evidence-first company investigation</div><h1>{esc(result['case']['title'])}</h1><p class='judgement'>{esc(result['executive_judgement'])}</p><p class='muted'>Retrieved {esc(result['run']['retrieved_at'])}. Every fact has evidence; every missing fact remains missing.</p></header><div class='metrics'><div class='metric'><b>{m['sources_acquired']}/{m['sources_requested']}</b><span>sources acquired</span></div><div class='metric'><b>{m['facts_extracted']}</b><span>extractions</span></div><div class='metric'><b>{m['claims']}</b><span>bounded facts</span></div><div class='metric'><b>{m['contradictions']}</b><span>contradictions</span></div><div class='metric'><b>{m['extraction_gaps']}</b><span>parser gaps</span></div><div class='metric'><b>{m['unresolved_questions']}</b><span>open items</span></div></div><h2>What the investigation found</h2><div class='grid'>{claims}</div><h2>Contradictions</h2><div class='grid'>{contradictions}</div><h2>Still unknown</h2><ul class='gaps'>{gaps}</ul><h2>Evidence acquisition</h2><table><thead><tr><th>Source</th><th>Status</th><th>Receipt / error</th><th>Extraction gap</th><th></th></tr></thead><tbody>{''.join(source_rows)}</tbody></table><h2>Bottom line</h2><p class='judgement'>{esc(result['bottom_line'])}</p></main></body></html>"""


def investigate_resilient(case_path: Path, out_dir: Path, *, now: str | None = None) -> dict[str, Any]:
    case = json.loads(case_path.read_text(encoding="utf-8"))
    retrieved_at = now or datetime.now(timezone.utc).isoformat()
    source_map = {x["id"]: x for x in case["sources"]}
    allowed_hosts = {host_for(x["url"]) for x in case["sources"]}
    registry = build_registry(case, retrieved_at)
    vault = EvidenceVault(out_dir / "vault", registry)
    all_facts: list[dict[str, Any]] = []
    source_results: list[dict[str, Any]] = []

    for source in case["sources"]:
        try:
            payload, ctype, resolved = fetch_source(source["url"], allowed_hosts)
            receipt, alert = vault.acquire(
                source["id"], payload, ctype, resolved_url=resolved,
                metadata={"case_id": case["case"]["id"], "mode": "live_public_source"},
            )
            text = html_to_text(payload) if ctype in {"text/html", "application/xhtml+xml"} else payload.decode("utf-8", errors="replace")
            facts = [_normalise_live_fact(f) for f in extract_facts(source, text)]
            all_facts.extend(facts)
            parse_payload = (json.dumps({
                "text_sha256": sha256(text.encode()).hexdigest(),
                "characters": len(text),
                "source_id": source["id"],
            }, sort_keys=True) + "\n").encode()
            vault.transform(
                operation="parse",
                input_receipt_ids=[receipt.receipt_id],
                input_object_hashes=[receipt.object.sha256],
                outputs=[(parse_payload, "application/json", "parsed", "public")],
                tool_id="safetrace.html-text", tool_version="2.2",
                parameters={"characters": len(text)}, case_id=case["case"]["id"],
            )
            source_results.append({
                "id": source["id"], "title": source["title"], "publisher": source["publisher"],
                "canonical_url": source["url"], "resolved_url": resolved, "content_type": ctype,
                "bytes": len(payload), "sha256": receipt.object.sha256, "receipt_hash": receipt.receipt_hash,
                "material_change_state": alert.kind, "http_status": 200, "acquisition_status": "acquired",
                "facts_extracted": sum(1 for f in facts if f["status"] == "extracted"),
                "required_not_found": [f["field"] for f in facts if f["status"] == "required_not_found"],
                "error": None,
            })
        except Exception as exc:  # network and parser access failures stay visible
            source_results.append({
                "id": source["id"], "title": source["title"], "publisher": source["publisher"],
                "canonical_url": source["url"], "resolved_url": source["url"], "content_type": None,
                "bytes": 0, "sha256": "", "receipt_hash": "", "material_change_state": "fetch_error",
                "http_status": getattr(exc, "code", 0) or 0, "acquisition_status": "source_unavailable",
                "facts_extracted": 0, "required_not_found": [],
                "error": f"{type(exc).__name__}: {exc}",
            })

    claims, contradictions = reconcile_facts(all_facts, source_map)
    claim_fields = {c["field"] for c in claims}
    contradiction_fields = {c["field"] for c in contradictions}
    unresolved: list[dict[str, Any]] = []
    for question in case.get("required_questions", []):
        if question["field"] not in claim_fields and question["field"] not in contradiction_fields:
            unresolved.append({**question, "status": "not_established"})
        elif question["field"] in contradiction_fields:
            unresolved.append({**question, "status": "contradictory_sources"})

    extraction_gaps = 0
    for source in source_results:
        if source["acquisition_status"] != "acquired":
            unresolved.append({
                "field": f"source_access:{source['id']}",
                "title": f"Source unavailable: {source['title']}",
                "reason": source["error"],
                "next_step": "Retry through an approved connector or retrieve the source manually and preserve it in the Evidence Vault.",
                "status": "source_unavailable",
            })
        for field in source["required_not_found"]:
            extraction_gaps += 1
            unresolved.append({
                "field": f"extraction_gap:{source['id']}:{field}",
                "title": f"Expected field not extracted: {field}",
                "reason": f"{source['title']} was acquired, but the reviewed parser did not find the expected field. The page may be client-rendered or its markup/content may have changed.",
                "next_step": "Verify the page in a browser-capable acquisition path, then update the reviewed extraction rule only after confirming the visible source content.",
                "status": "extraction_gap",
            })

    integrity = vault.verify_integrity()
    acquired = [s for s in source_results if s["acquisition_status"] == "acquired"]
    executive = case["case"]["executive_judgement_template"].format(
        claims=len(claims), contradictions=len(contradictions), unresolved=len(unresolved)
    )
    bottom = (
        f"The live run requested {len(source_results)} reviewed public sources, acquired {len(acquired)}, and produced {len(claims)} bounded facts. "
        f"It recorded {len(source_results) - len(acquired)} source-access failure(s), {extraction_gaps} required extraction gap(s), "
        f"{len(contradictions)} contradiction(s), and {len(unresolved)} unresolved item(s). "
        "No missing shareholder, ownership, sanctions, misconduct or control conclusion is inferred from absence of evidence."
    )
    result = {
        "schema_version": "safetrace.live-company-investigation/2.2",
        "case": case["case"],
        "run": {"retrieved_at": retrieved_at, "mode": "live_public_sources_resilient", "allowlisted_hosts": sorted(allowed_hosts)},
        "sources": source_results,
        "facts": all_facts,
        "claims": claims,
        "contradictions": contradictions,
        "unresolved_questions": unresolved,
        "executive_judgement": executive,
        "bottom_line": bottom,
        "integrity": integrity,
        "metrics": {
            "sources_requested": len(source_results),
            "sources_acquired": len(acquired),
            "source_failures": len(source_results) - len(acquired),
            "facts_extracted": sum(1 for f in all_facts if f["status"] == "extracted"),
            "claims": len(claims),
            "contradictions": len(contradictions),
            "extraction_gaps": extraction_gaps,
            "unresolved_questions": len(unresolved),
        },
        "boundary": "Public-source research only. Source and parser failures are surfaced, not hidden. Extraction is evidence retrieval, not an allegation or automated compliance decision. Missing facts remain unresolved.",
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "report.md").write_text(_render_report(result), encoding="utf-8")
    (out_dir / "index.html").write_text(_render_html(result), encoding="utf-8")
    return result


def main() -> int:
    p = argparse.ArgumentParser(description="Run resilient reviewed live public company research.")
    p.add_argument("--case", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("artifacts/intelligence-casework/live-company"))
    p.add_argument("--minimum-sources", type=int, default=1)
    args = p.parse_args()
    result = investigate_resilient(args.case, args.out)
    print(json.dumps(result["metrics"], indent=2))
    print("\nSOURCE STATUS")
    for s in result["sources"]:
        print(f"- {s['id']}: {s['acquisition_status']} http={s['http_status']} facts={s['facts_extracted']} missing={','.join(s['required_not_found']) or '-'} error={s['error'] or '-'}")
    print("\n", result["bottom_line"])
    if result["integrity"]["status"] != "pass":
        return 1
    if result["metrics"]["sources_acquired"] < args.minimum_sources:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
