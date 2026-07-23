from __future__ import annotations

import argparse
import json
from pathlib import Path

from .model import Claim, Decision, EvidenceRef


def load_claim(raw: dict) -> Claim:
    evidence = [EvidenceRef(**item) for item in raw.get("evidence", [])]
    decision = Decision(**raw["decision"]) if raw.get("decision") else None
    return Claim(
        id=raw["id"],
        text=raw["text"],
        evidence_state=raw["evidence_state"],
        sensitivity=raw["sensitivity"],
        origin=raw["origin"],
        evidence=evidence,
        decision=decision,
        correction_history=raw.get("correction_history", []),
    )


def evaluate(queue_path: Path, public_output: Path, review_output: Path) -> tuple[dict, dict]:
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    claims = [load_claim(item) for item in queue["claims"]]
    evaluated = [claim.to_dict() for claim in claims]
    public_claims = [item for item in evaluated if item["publication"]["publishable"]]

    review_report = {
        "schema_version": "safetrace.review-report/0.5",
        "case_id": queue["case_id"],
        "summary": {
            "total": len(evaluated),
            "publishable": len(public_claims),
            "blocked": len(evaluated) - len(public_claims),
        },
        "claims": evaluated,
    }
    public_feed = {
        "schema_version": "safetrace.public-claims/0.5",
        "case_id": queue["case_id"],
        "claims": public_claims,
        "publication_boundary": "Only claims that passed the recorded human publication gate appear here.",
    }
    public_output.parent.mkdir(parents=True, exist_ok=True)
    review_output.parent.mkdir(parents=True, exist_ok=True)
    public_output.write_text(json.dumps(public_feed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review_output.write_text(json.dumps(review_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return public_feed, review_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, default=Path(__file__).parent / "data/claims.json")
    parser.add_argument("--public-output", type=Path, default=Path("artifacts/review/public-claims.json"))
    parser.add_argument("--review-output", type=Path, default=Path("artifacts/review/review-report.json"))
    args = parser.parse_args()
    evaluate(args.queue, args.public_output, args.review_output)


if __name__ == "__main__":
    main()
