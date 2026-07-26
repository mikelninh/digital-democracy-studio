"""Fail-closed validation for the SafeTrace Citizen Portal candidate radar."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "candidates.json"
INDEX = ROOT / "index.html"

REQUIRED = {
    "id", "topic", "story_title", "research_question", "scores", "total",
    "decision", "evidence_state", "first_sprint", "sources"
}
DIMENSIONS = {"harm", "evidence", "actionability", "urgency", "public_value", "fairness"}
PROHIBITED = {"ist korrupt", "ist schuldig", "hat gekauft", "automatisch veröffentlichen"}


def fail(message: str) -> None:
    raise ValueError(message)


def https(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate() -> dict[str, object]:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    if data.get("schema") != "safetrace.citizen-portal/0.3":
        fail("unexpected schema")
    candidates = data.get("candidates")
    if not isinstance(candidates, list) or len(candidates) < 10:
        fail("candidate radar must contain at least ten candidates")

    ids: set[str] = set()
    high_priority = 0
    sources = 0
    for candidate in candidates:
        missing = REQUIRED - candidate.keys()
        if missing:
            fail(f"candidate missing fields: {sorted(missing)}")
        if candidate["id"] in ids:
            fail(f"duplicate id: {candidate['id']}")
        ids.add(candidate["id"])

        scores = candidate["scores"]
        if set(scores) != DIMENSIONS:
            fail(f"{candidate['id']} has wrong score dimensions")
        if any(not isinstance(v, int) or not 0 <= v <= 5 for v in scores.values()):
            fail(f"{candidate['id']} has invalid score")
        calculated = sum(scores.values())
        if candidate["total"] != calculated:
            fail(f"{candidate['id']} total mismatch: {candidate['total']} != {calculated}")
        if calculated >= 24:
            high_priority += 1

        text = " ".join(str(candidate[k]) for k in ("story_title", "research_question", "first_sprint")).lower()
        for phrase in PROHIBITED:
            if phrase in text:
                fail(f"{candidate['id']} contains unsupported wording: {phrase}")

        if not candidate["sources"]:
            fail(f"{candidate['id']} has no sources")
        for source in candidate["sources"]:
            for key in ("publisher", "title", "date", "url"):
                if not source.get(key):
                    fail(f"{candidate['id']} source missing {key}")
            if not https(source["url"]):
                fail(f"{candidate['id']} source is not HTTPS")
            sources += 1

    html = INDEX.read_text(encoding="utf-8")
    for marker in (
        "TRACE Prioritizer", "Case Radar", "keine Übertragung",
        "Sensibler Intake deaktiviert", "automatische Veröffentlichung"
    ):
        if marker.lower() not in html.lower():
            fail(f"index missing safety marker: {marker}")

    return {
        "status": "valid",
        "candidates": len(candidates),
        "high_priority_candidates": high_priority,
        "sources": sources,
        "sensitive_intake_enabled": False,
        "automatic_publication_enabled": False,
        "automatic_guilt_decisions_enabled": False,
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
