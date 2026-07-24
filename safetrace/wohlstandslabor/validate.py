from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

EXPECTED_POLICIES = {"citizen-capital", "energy-abundance", "anchor-customer", "ai-robotics-dividend"}
EXPECTED_LENSES = {"all", "household", "worker", "founder", "future", "climate", "budget"}
SCORE_KEYS = {"simplicity", "productivity", "fairness", "resilience", "evidence"}


def load_data(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"window\.SAFETRACE_WOHLSTAND_DATA\s*=\s*(\{.*\})\s*;\s*", raw, re.DOTALL)
    if not match:
        raise ValueError("data.js must contain one JSON object assignment")
    return json.loads(match.group(1))


def validate(root: Path) -> dict[str, Any]:
    data = load_data(root / "data.js")
    html = (root / "index.html").read_text(encoding="utf-8")
    policies = data.get("policies", [])
    policy_ids = {p.get("id") for p in policies}
    lens_ids = {l.get("id") for l in data.get("lenses", [])}
    checks = {
        "policy_set_exact": policy_ids == EXPECTED_POLICIES,
        "lens_set_exact": lens_ids == EXPECTED_LENSES,
        "same_facts_boundary": data.get("boundary", {}).get("noPartyPersuasion") is True,
        "browser_local": "localStorage" in html and "fetch(" not in html and "XMLHttpRequest" not in html,
        "two_surfaces": all(x in html for x in ("Labor", "3‑Minuten‑Brief", "briefView", "labView")),
        "capital_calculator_bounded": data.get("boundary", {}).get("noInvestmentAdvice") is True and "keine Anlageberatung" in html,
        "all_policies_sourced": all(len(p.get("sources", [])) >= 2 and all(s.get("url", "").startswith("https://") for s in p["sources"]) for p in policies),
        "all_policy_dimensions": all(set(p.get("scores", {})) == SCORE_KEYS and all(0 <= value <= 100 for value in p["scores"].values()) for p in policies),
        "all_incentive_maps_complete": all(p.get("incentive") and p.get("beneficiaries") and p.get("payers") and p.get("risks") and p.get("better") for p in policies),
        "snapshot_is_explicit": data.get("snapshotDate") == "2026-07-24" and "Snapshot" in html,
        "no_real_publication_claim": data.get("boundary", {}).get("simulationOnly") is True and "keine echte Veröffentlichung" in html,
    }
    return {
        "schema_version": "safetrace.wohlstandslabor-report/0.1",
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "counts": {"policies": len(policies), "lenses": len(data.get("lenses", [])), "sources": sum(len(p.get("sources", [])) for p in policies)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).parent)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate(args.root)
    encoded = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
