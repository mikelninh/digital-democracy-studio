from __future__ import annotations

import argparse
import json
from pathlib import Path

from .collection import prioritize
from .run_initial import build_submission_with_available, initial_source_ids


def run_budgeted(case: dict, limit: int | None = None) -> tuple[dict, list[dict]]:
    ranked = prioritize(case, limit=limit)
    selected = [row["source_id"] for row in ranked]
    available = initial_source_ids(case) | set(selected)
    submission = build_submission_with_available(case, available, optional_sources_selected=selected)
    submission["collection_plan"] = ranked
    return submission, ranked


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the evidence-budget Venatic Analyst Challenge.")
    parser.add_argument("--case", type=Path, default=Path(__file__).with_name("case_v002.json"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--plan-out", type=Path)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    case = json.loads(args.case.read_text(encoding="utf-8"))
    submission, ranked = run_budgeted(case, limit=args.limit)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(submission, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.plan_out:
        args.plan_out.parent.mkdir(parents=True, exist_ok=True)
        args.plan_out.write_text(json.dumps(ranked, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"selected": [r["source_id"] for r in ranked], "plan": ranked}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
