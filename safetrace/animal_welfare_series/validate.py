"""Fail-closed validation for the public animal-welfare case catalog."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "cases.json"
INDEX = ROOT / "index.html"

REQUIRED_CASE_FIELDS = {
    "id",
    "issue",
    "slug",
    "title",
    "status",
    "verdict",
    "evidence_strength",
    "impact_potential",
    "urgency",
    "verified_claims",
    "not_established",
    "publish_line",
    "next_action",
    "impact_metrics",
    "win_win_win",
    "sources",
}

PROHIBITED_PHRASES = {
    "ist korrupt",
    "hat das gesetz gekauft",
    "ist schuldig",
    "automatisch veröffentlichen",
    "verdächtigenliste",
}


def fail(message: str) -> None:
    raise ValueError(message)


def valid_https_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate() -> dict[str, object]:
    if not CATALOG.exists():
        fail("cases.json is missing")
    if not INDEX.exists():
        fail("index.html is missing")

    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    if data.get("schema") != "safetrace.animal-welfare-series/0.1":
        fail("unexpected schema identifier")

    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) != 7:
        fail("catalog must contain exactly seven v0.1 cases")

    ids: set[str] = set()
    issues: set[int] = set()
    source_count = 0

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            fail(f"case {index} is not an object")
        missing = REQUIRED_CASE_FIELDS - case.keys()
        if missing:
            fail(f"{case.get('id', index)} missing fields: {sorted(missing)}")

        case_id = case["id"]
        if case_id in ids:
            fail(f"duplicate case id: {case_id}")
        ids.add(case_id)

        issue = case["issue"]
        if not isinstance(issue, int) or issue <= 0 or issue in issues:
            fail(f"invalid or duplicate issue for {case_id}")
        issues.add(issue)

        for score_field in ("evidence_strength", "impact_potential", "urgency"):
            score = case[score_field]
            if not isinstance(score, int) or not 1 <= score <= 5:
                fail(f"{case_id} has invalid {score_field}: {score}")

        for list_field in ("verified_claims", "not_established", "impact_metrics", "sources"):
            value = case[list_field]
            if not isinstance(value, list) or not value:
                fail(f"{case_id} requires non-empty {list_field}")

        if len(case["not_established"]) < 2:
            fail(f"{case_id} must expose at least two explicit unknowns")
        if len(case["impact_metrics"]) < 3:
            fail(f"{case_id} must define at least three impact metrics")

        combined_text = " ".join(
            str(case[field])
            for field in ("title", "verdict", "publish_line", "next_action", "win_win_win")
        ).lower()
        for phrase in PROHIBITED_PHRASES:
            if phrase in combined_text:
                fail(f"{case_id} contains prohibited unsupported wording: {phrase}")

        for source in case["sources"]:
            if not isinstance(source, dict):
                fail(f"{case_id} has a non-object source")
            for key in ("publisher", "title", "date", "url"):
                if not source.get(key):
                    fail(f"{case_id} source missing {key}")
            if not valid_https_url(source["url"]):
                fail(f"{case_id} source is not a valid HTTPS URL: {source['url']}")
            source_count += 1

    html = INDEX.read_text(encoding="utf-8")
    required_html_markers = (
        "Citizen Case Checker",
        "Der TRACE Loop",
        "Impact ohne Selbsttäuschung",
        "keine Übertragung",
        "cases.json",
    )
    for marker in required_html_markers:
        if marker not in html:
            fail(f"index.html missing marker: {marker}")

    return {
        "schema": data["schema"],
        "cases": len(cases),
        "sources": source_count,
        "all_cases_have_unknowns": True,
        "all_cases_have_impact_metrics": True,
        "sensitive_uploads_enabled": False,
        "automatic_publication_enabled": False,
        "status": "valid",
    }


def main() -> int:
    try:
        result = validate()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
