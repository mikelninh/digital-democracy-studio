from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_REVIEW_STATES = {"approved_public_baseline", "approved_public_update"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build(data_dir: Path, output: Path) -> dict:
    recommendations = load_json(data_dir / "recommendations.json")
    sources = load_json(data_dir / "sources.json")
    review = load_json(data_dir / "review.json")
    unresolved = load_json(data_dir / "unresolved_questions.json")

    if review["state"] not in ALLOWED_REVIEW_STATES:
        raise RuntimeError("Public status generation blocked: review approval is missing")
    if len(recommendations["recommendations"]) != 14:
        raise RuntimeError("Expected exactly 14 GRECO recommendations")

    counts = Counter(item["status"] for item in recommendations["recommendations"])
    expected = {"implemented_satisfactorily": 4, "partly_implemented": 6, "not_implemented": 4}
    if dict(counts) != expected:
        raise RuntimeError(f"Unexpected GRECO status totals: {dict(counts)}")

    generated_at = datetime.now(timezone.utc).isoformat()
    public = {
        "schema_version": "safetrace.public-status/0.3",
        "release": "v0.3-source-engine",
        "generated_at": generated_at,
        "case": {
            "id": "case-001",
            "title": "Germany's 14 Anti-Corruption Promises",
            "jurisdiction": "Germany",
            "evidence_state": "verified_official_record",
            "summary": counts,
            "recommendations": recommendations["recommendations"],
            "unresolved_questions": unresolved["questions"],
        },
        "sources": sources["sources"],
        "review": review,
        "publication_rule": (
            "SafeTrace reports GRECO's official implementation status. It does not infer "
            "criminal conduct or individual guilt from institutional non-compliance."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return public


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent / "data")
    parser.add_argument("--output", type=Path, default=Path(__file__).parents[1] / "public/data/case-001.json")
    args = parser.parse_args()
    build(args.data_dir, args.output)


if __name__ == "__main__":
    main()
