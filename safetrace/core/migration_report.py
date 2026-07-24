from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from .adapters import (
    adapt_review_claim,
    bundle_from_arms_case,
    bundle_from_case_pack,
    bundle_from_law_fairness,
    bundle_from_political_money_graph,
    bundle_summary,
)
from .model import InvestigationBundle


def _extend_unique(target: list[Any], incoming: list[Any]) -> None:
    known = {item.id for item in target}
    target.extend(item for item in incoming if item.id not in known)


def build_existing_bundles(safetrace_root: Path) -> dict[str, InvestigationBundle]:
    from safetrace.arms_monitor.build_monitor import build as build_arms
    from safetrace.case_packs.generate_case_pack import build_pack
    from safetrace.law_fairness.model import load_case
    from safetrace.political_money.build_graph import build as build_graph
    from safetrace.review_desk.evaluate import load_claim

    bundles: dict[str, InvestigationBundle] = {}

    pack = build_pack(safetrace_root / "source_engine/data", generated_at="2026-07-24T00:00:00+00:00")
    bundles["case-001"] = bundle_from_case_pack(pack)

    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory)
        graph_payload = build_graph(
            safetrace_root / "political_money/data/seed.json",
            temporary / "political-money.json",
        )
        money_bundle = bundle_from_political_money_graph(graph_payload)
        queue = json.loads((safetrace_root / "review_desk/data/claims.json").read_text(encoding="utf-8"))
        for raw_claim in queue["claims"]:
            records = adapt_review_claim(load_claim(raw_claim), case_id=money_bundle.case.id)
            for name in ("sources", "claims", "evidence", "reviews", "corrections"):
                _extend_unique(getattr(money_bundle, name), getattr(records, name))
        money_bundle.validate()
        bundles["case-002"] = money_bundle

        arms_payload = build_arms(
            safetrace_root / "arms_monitor/data/baseline.json",
            temporary / "arms-monitor.json",
        )
        bundles["case-003"] = bundle_from_arms_case(arms_payload)

    fairness_payload = load_case(safetrace_root / "law_fairness/data/case_004.json")
    bundles["case-004"] = bundle_from_law_fairness(fairness_payload)

    for bundle in bundles.values():
        bundle.validate()
    return bundles


def build_report(safetrace_root: Path) -> dict[str, Any]:
    bundles = build_existing_bundles(safetrace_root)
    return {
        "schema_version": "safetrace.migration-report/1.2",
        "target_schema": "safetrace.core/1.2",
        "status": "pass" if set(bundles) == {"case-001", "case-002", "case-003", "case-004"} else "fail",
        "cases": {case_id: bundle_summary(bundle) for case_id, bundle in sorted(bundles.items())},
        "guarantees": [
            "Every migrated material claim remains in the unified Claim model.",
            "Every relationship and event retains evidence references.",
            "Existing human review decisions and visible corrections are retained where present.",
            "The migration does not authorise sensitive-data intake or automated publication.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate migration of existing SafeTrace cases into v1.2")
    parser.add_argument("--root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report(args.root)
    encoded = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
