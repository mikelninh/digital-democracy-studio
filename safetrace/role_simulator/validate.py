from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PROHIBITED_ACTIONS = {
    "publish_real",
    "contact_subject",
    "refer_authority",
    "identify_face",
    "hack",
    "open_restricted_data",
}
EXPECTED_ROLES = {
    "citizen",
    "investigator",
    "evidence_manager",
    "reviewer",
    "legal_reviewer",
    "publisher",
}
EXPECTED_CASES = {"case-001", "case-002", "case-003", "case-004"}
EXPECTED_VIEWS = {
    "overview", "sources", "claims", "graph", "timeline",
    "agents", "review", "publish", "audit",
}


def load_data(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    match = re.fullmatch(
        r"window\.SAFETRACE_SIMULATOR_DATA\s*=\s*(\{.*\})\s*;\s*",
        raw,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError("simulator-data.js must contain a single JSON object assignment")
    return json.loads(match.group(1))


def validate(root: Path) -> dict[str, Any]:
    data = load_data(root / "simulator-data.js")
    html = (root / "index.html").read_text(encoding="utf-8")
    roles = data.get("roles", [])
    cases = data.get("cases", [])
    role_ids = {role.get("id") for role in roles}
    case_ids = {case.get("id") for case in cases}
    views = set(data.get("views", []))
    boundary = data.get("boundary", {})

    unsafe_roles = {
        role.get("id"): sorted(PROHIBITED_ACTIONS.intersection(role.get("allowedActions", [])))
        for role in roles
        if PROHIBITED_ACTIONS.intersection(role.get("allowedActions", []))
    }
    incomplete_cases: list[str] = []
    for case in cases:
        complete = (
            len(case.get("sources", [])) >= 3
            and len(case.get("claims", [])) >= 3
            and len(case.get("timeline", [])) >= 3
            and len(case.get("graph", {}).get("nodes", [])) >= 4
            and len(case.get("graph", {}).get("edges", [])) >= 3
            and len(case.get("agents", [])) >= 3
            and set(case.get("tasks", {})) == EXPECTED_ROLES
            and all(source.get("zone") in {"public", "synthetic"} for source in case.get("sources", []))
            and all(claim.get("limitation") for claim in case.get("claims", []))
        )
        if not complete:
            incomplete_cases.append(case.get("id", "unknown"))

    case_004 = next((case for case in cases if case.get("id") == "case-004"), {})
    publishable = [case.get("id") for case in cases if case.get("publication", {}).get("allowedInSimulation")]
    blocked = [case.get("id") for case in cases if not case.get("publication", {}).get("allowedInSimulation")]
    local_only = (
        "localStorage" in html
        and "fetch(" not in html
        and "XMLHttpRequest" not in html
        and "simulator-data.js" in html
    )
    accessible = all(
        fragment in html
        for fragment in (
            'lang="de"',
            'aria-label="Hauptnavigation"',
            'aria-live="polite"',
            "Fall und Rolle zurücksetzen",
        )
    )
    truthful_boundary = (
        boundary.get("simulationOnly") is True
        and boundary.get("browserLocalState") is True
        and boundary.get("productionAuthentication") is False
        and boundary.get("realPublication") is False
        and boundary.get("restrictedData") is False
    )
    case_004_closed = (
        case_004.get("publication", {}).get("allowedInSimulation") is False
        and case_004.get("readiness", {}).get("sources") == 11
        and case_004.get("readiness", {}).get("originals") == 0
    )

    checks = {
        "roles_exact": role_ids == EXPECTED_ROLES,
        "cases_exact": case_ids == EXPECTED_CASES,
        "views_exact": views == EXPECTED_VIEWS,
        "unsafe_roles_absent": not unsafe_roles,
        "all_cases_complete": not incomplete_cases,
        "truthful_boundary": truthful_boundary,
        "browser_local_only": local_only,
        "accessibility_basics": accessible,
        "case_004_fail_closed": case_004_closed,
        "contains_success_path": bool(publishable),
        "contains_blocked_path": blocked == ["case-004"],
    }
    return {
        "schema_version": "safetrace.role-simulator-report/1.0",
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "counts": {
            "roles": len(roles),
            "cases": len(cases),
            "views": len(views),
            "publishable_training_cases": len(publishable),
            "blocked_training_cases": len(blocked),
        },
        "role_ids": sorted(role_ids),
        "case_ids": sorted(case_ids),
        "unsafe_roles": unsafe_roles,
        "incomplete_cases": incomplete_cases,
        "publication_paths": {"training_only": publishable, "blocked": blocked},
        "boundaries": {
            "simulation_only": True,
            "browser_local_state": True,
            "network_requests": False,
            "production_authentication": False,
            "real_publication": False,
            "restricted_data": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the SafeTrace Role Simulator")
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
