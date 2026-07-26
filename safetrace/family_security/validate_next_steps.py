from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
EVIDENCE = json.loads((ROOT / "evidence_map_de_v0_1.json").read_text(encoding="utf-8"))
POLICY = json.loads((ROOT / "policy_matrix_v0_1.json").read_text(encoding="utf-8"))
HTML = (ROOT / "next_steps.html").read_text(encoding="utf-8")


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    indicators = EVIDENCE.get("indicators", [])
    if len(indicators) < 10:
        fail("evidence map must contain at least ten indicators")
    ids = [item.get("id") for item in indicators]
    if len(ids) != len(set(ids)):
        fail("duplicate evidence ids")
    if len(EVIDENCE.get("priority_data_gaps", [])) != 7:
        fail("exactly seven priority data gaps required")

    valid_states = {"verified_starting_fact", "verified_context_indicator", "verified_but_stale", "data_gap"}
    for item in indicators:
        if item.get("status") not in valid_states:
            fail(f"invalid evidence state for {item.get('id')}")
        if not item.get("interpretation") or not item.get("limitation"):
            fail(f"interpretation/limitation missing for {item.get('id')}")
        source = item.get("source")
        if item.get("status") == "data_gap":
            if item.get("value") is not None:
                fail(f"data gap must have null value: {item.get('id')}")
        else:
            if not source:
                fail(f"sourced indicator missing source: {item.get('id')}")
            parsed = urlparse(source.get("url", ""))
            if parsed.scheme != "https" or not parsed.netloc:
                fail(f"invalid source url: {item.get('id')}")

    interventions = POLICY.get("interventions", [])
    if len(interventions) != 8:
        fail("exactly eight policy tests required")
    policy_ids = [item.get("id") for item in interventions]
    if len(policy_ids) != len(set(policy_ids)):
        fail("duplicate policy ids")
    if sum(1 for item in interventions if item.get("priority") == "A") < 3:
        fail("at least three priority-A tests required")
    for item in interventions:
        for key in ("barrier", "mechanism", "evidence_state", "leading_metrics", "family_outcomes", "pilot", "risks"):
            if not item.get(key):
                fail(f"policy field missing: {item.get('id')} / {key}")

    required_markers = [
        "Vom Kinderwunsch zur planbaren Familie",
        "Methodische Grenze",
        "Politiktests",
        "Datenlücken",
        "kein sechster aktiver Fall",
    ]
    for marker in required_markers:
        if marker.lower() not in HTML.lower():
            fail(f"next steps page missing marker: {marker}")

    prohibited = [
        "frauen müssen mehr kinder",
        "babybonus löst",
        "menschheit stirbt aus",
        "geburtenrate beweist kausal",
    ]
    combined = json.dumps(EVIDENCE, ensure_ascii=False).lower() + json.dumps(POLICY, ensure_ascii=False).lower() + HTML.lower()
    for phrase in prohibited:
        if phrase in combined:
            fail(f"unsupported or coercive phrase found: {phrase}")

    print("PASS: Family Security evidence map, data gaps and policy tests are bounded and valid.")


if __name__ == "__main__":
    main()
