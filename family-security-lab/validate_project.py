from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load(name: str) -> dict:
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def main() -> None:
    case = load("case_051.json")
    evidence = load("evidence_map_de_v0_1.json")
    policies = load("policy_matrix_v0_1.json")

    if case.get("id") != "CAND-051":
        fail("unexpected case id")
    if case.get("lifecycle") != "scoping":
        fail("standalone project must not silently become an active investigation")
    if case.get("impact_contract", {}).get("status") != "not_measurable_yet":
        fail("outcome impact must not be claimed before evaluation")

    dimensions = case.get("family_security_index", {}).get("dimensions", [])
    if len(dimensions) != 7:
        fail("Family Security Index must contain seven dimensions")

    indicators = evidence.get("indicators", [])
    if len(indicators) != 12:
        fail("evidence map v0.1 must contain twelve indicators")
    ids = [item.get("id") for item in indicators]
    if len(ids) != len(set(ids)):
        fail("duplicate evidence indicator ids")
    if not any(item.get("status") == "data_gap" for item in indicators):
        fail("data gaps must remain explicit")
    if len(evidence.get("priority_data_gaps", [])) != 7:
        fail("expected seven priority data gaps")

    interventions = policies.get("interventions", [])
    if len(interventions) != 8:
        fail("policy matrix v0.1 must contain eight interventions")
    for item in interventions:
        for key in ("barrier", "mechanism", "evidence_state", "leading_metrics", "family_outcomes", "pilot", "risks"):
            if not item.get(key):
                fail(f"policy {item.get('id')} missing {key}")
    if len([item for item in interventions if item.get("priority") == "A"]) != 4:
        fail("expected exactly four priority-A policy tests")

    required_files = [
        "README.md",
        "PROJECT.md",
        "METHODOLOGY.md",
        "ROADMAP.md",
        "index.html",
        "evidence.html",
    ]
    for relative in required_files:
        if not (ROOT / relative).is_file() or not (ROOT / relative).read_text(encoding="utf-8").strip():
            fail(f"missing or empty project artifact: {relative}")

    combined = "\n".join((ROOT / name).read_text(encoding="utf-8").lower() for name in required_files)
    for marker in ("family security", "wahlfreiheit", "keine staatliche soll-kinderzahl", "data gap"):
        if marker not in combined:
            fail(f"missing public boundary marker: {marker}")

    prohibited = (
        "frauen müssen mehr kinder",
        "kinderlose sind schuld",
        "geburten um jeden preis",
    )
    for phrase in prohibited:
        if phrase in combined:
            fail(f"coercive wording detected: {phrase}")

    print("PASS: Family Security Lab is a complete, bounded standalone project.")


if __name__ == "__main__":
    main()
