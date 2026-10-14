"""Deterministic, evidence-bounded case analysis for SafeTrace's fictional demo.

This is *not* a machine-learning model and does not ingest the internet.
Potential LLM-based enrichment must remain a proposal until implemented and evaluated.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CASE_PATH = ROOT / "data" / "corpus.json"


def load_case(path: Path = CASE_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_case(case: dict[str, Any]) -> list[str]:
    """Validate referential integrity and evidentiary claims; return violations."""
    errors: list[str] = []
    for table in ("actors", "sources", "claims", "posts"):
        rows = case.get(table)
        if not isinstance(rows, list):
            errors.append(f"{table}: missing list")
            continue
        ids = [row.get("id") for row in rows]
        if len(ids) != len(set(ids)) or not all(ids):
            errors.append(f"{table}: missing or duplicate IDs")
    actors = {x["id"] for x in case.get("actors", [])}
    claims = {x["id"] for x in case.get("claims", [])}
    sources = {x["id"] for x in case.get("sources", [])}
    for source in case.get("sources", []):
        if not all(source.get(k) for k in ("title", "excerpt", "anchor", "limitation", "date")):
            errors.append(f"source {source.get('id')} lacks evidence anchor or limitation")
    for c in case.get("claims", []):
        if c.get("stance") not in {"contested", "unverified", "qualified"}:
            errors.append(f"claim {c.get('id')}: invalid evidentiary state")
        if not c.get("limitation") or not c.get("next") or not c.get("finding"):
            errors.append(f"claim {c.get('id')}: no limitation, finding or next step")
        for sid in c.get("support", []) + c.get("counter", []):
            if sid not in sources:
                errors.append(f"claim {c.get('id')}: unknown source {sid}")
        for aid in c.get("actors", []):
            if aid not in actors:
                errors.append(f"claim {c.get('id')}: unknown actor {aid}")
    for post in case.get("posts", []):
        for key, allowed in (("actor", actors), ("claim", claims), ("source", sources)):
            if post.get(key) not in allowed:
                errors.append(f"post {post.get('id')}: unknown {key} {post.get(key)}")
        if not post.get("date") or not post.get("text"):
            errors.append(f"post {post.get('id')}: missing date/text")
    return errors


def claim_packet(case: dict[str, Any], claim_id: str) -> dict[str, Any]:
    """Return the complete bounded source trail for one claim, without synthesis."""
    claim = next((c for c in case["claims"] if c["id"] == claim_id), None)
    if claim is None:
        raise KeyError(claim_id)
    sources = {s["id"]: s for s in case["sources"]}
    return {
        "claim": claim,
        "cited_evidence": [sources[k] for k in claim["support"]],
        "challenging_evidence": [sources[k] for k in claim["counter"]],
        "messages": [p for p in case["posts"] if p["claim"] == claim_id],
        "conclusion_type": "developer_authored_synthetic_example",
        "human_review_required": True,
    }


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[\w€%]+", text.casefold()))


def search_sources(case: dict[str, Any], query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Transparent lexicon retrieval, not embedding/LLM RAG."""
    wanted = tokens(query)
    if not wanted or limit < 1:
        return []
    results = []
    for source in case["sources"]:
        title_tokens = tokens(source["title"])
        excerpt_tokens = tokens(source["excerpt"])
        hits = (wanted & title_tokens) | (wanted & excerpt_tokens)
        score = 3 * len(wanted & title_tokens) + len(wanted & excerpt_tokens)
        if score:
            results.append({
                "source_id": source["id"],
                "title": source["title"],
                "score": score,
                "query_token_matches": sorted(hits),
                "anchor": source["anchor"],
                "exact_excerpt": source["excerpt"],
                "limitation": source["limitation"],
            })
    return sorted(results, key=lambda r: (-r["score"], r["source_id"]))[:limit]


def discourse_summary(case: dict[str, Any]) -> dict[str, Any]:
    """Separate volume (post counts) from evidence independence (source lineage)."""
    errors = validate_case(case)
    if errors:
        raise ValueError("Case validation failed:\n" + "\n".join(errors))
    by_claim = Counter(p["claim"] for p in case["posts"])
    summaries = []
    for claim in case["claims"]:
        cited = {p["source"] for p in case["posts"] if p["claim"] == claim["id"]}
        actors = {p["actor"] for p in case["posts"] if p["claim"] == claim["id"]}
        summaries.append({
            "claim_id": claim["id"],
            "claim": claim["label"],
            "message_count": by_claim[claim["id"]],
            "distinct_organisations": len(actors),
            "distinct_cited_document_ids": len(cited),
            "cited_document_ids": sorted(cited),
            "evidence_state": claim["stance"],
            "needs_human_review": True,
            "limitation": claim["limitation"],
        })
    return {
        "case_id": case["case"]["id"],
        "fixture_type": "fully_synthetic",
        "claim_count": len(case["claims"]),
        "organisation_count": len(case["actors"]),
        "source_count": len(case["sources"]),
        "message_count": len(case["posts"]),
        "claims": summaries,
        "interpretation_warning": "Document-count and message-count do not indicate independent measurements, coordination or causation.",
    }


if __name__ == "__main__":
    print(json.dumps(discourse_summary(load_case()), indent=2, ensure_ascii=False))
