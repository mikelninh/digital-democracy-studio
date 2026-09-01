from __future__ import annotations

import argparse
import json
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
    render_html,
    render_report,
)


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
            facts = extract_facts(source, text)
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
                tool_id="safetrace.html-text", tool_version="2.1",
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
        except Exception as exc:  # network/markup failures are explicit case evidence
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

    for source in source_results:
        if source["acquisition_status"] != "acquired":
            unresolved.append({
                "field": f"source_access:{source['id']}",
                "title": f"Source unavailable: {source['title']}",
                "reason": source["error"],
                "next_step": "Retry through an approved connector or retrieve the source manually and preserve it in the Evidence Vault.",
                "status": "source_unavailable",
            })

    integrity = vault.verify_integrity()
    acquired = [s for s in source_results if s["acquisition_status"] == "acquired"]
    failed_required = [f for f in all_facts if f["status"] == "required_not_found"]
    executive = case["case"]["executive_judgement_template"].format(
        claims=len(claims), contradictions=len(contradictions), unresolved=len(unresolved)
    )
    bottom = (
        f"The live run requested {len(source_results)} reviewed public sources, acquired {len(acquired)}, and produced {len(claims)} bounded facts. "
        f"It recorded {len(source_results) - len(acquired)} source-access failure(s), {len(contradictions)} contradiction(s), and {len(unresolved)} unresolved item(s). "
        "No missing shareholder, ownership, sanctions, misconduct or control conclusion is inferred from absence of evidence."
    )
    result = {
        "schema_version": "safetrace.live-company-investigation/2.1",
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
            "unresolved_questions": len(unresolved),
            "required_extractions_missing": len(failed_required),
        },
        "boundary": "Public-source research only. Source failures are surfaced, not hidden. Extraction is evidence retrieval, not an allegation or automated compliance decision. Missing facts remain unresolved.",
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    (out_dir / "index.html").write_text(render_html(result), encoding="utf-8")
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
        print(f"- {s['id']}: {s['acquisition_status']} http={s['http_status']} facts={s['facts_extracted']} error={s['error'] or '-'}")
    print("\n", result["bottom_line"])
    if result["integrity"]["status"] != "pass":
        return 1
    if result["metrics"]["sources_acquired"] < args.minimum_sources:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
