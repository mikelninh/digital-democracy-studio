"""Fail-closed validation for the SafeTrace Citizen Portal and season radars."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "candidates.json"
SOCIAL = ROOT / "social_seasons.json"
INDEX = ROOT / "index.html"
SEASONS_PAGE = ROOT / "seasons.html"

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


def validate_candidate(candidate: dict[str, object], ids: set[str]) -> tuple[int, int]:
    missing = REQUIRED - candidate.keys()
    if missing:
        fail(f"candidate missing fields: {sorted(missing)}")
    candidate_id = str(candidate["id"])
    if candidate_id in ids:
        fail(f"duplicate id: {candidate_id}")
    ids.add(candidate_id)

    scores = candidate["scores"]
    if not isinstance(scores, dict) or set(scores) != DIMENSIONS:
        fail(f"{candidate_id} has wrong score dimensions")
    if any(not isinstance(v, int) or not 0 <= v <= 5 for v in scores.values()):
        fail(f"{candidate_id} has invalid score")
    calculated = sum(scores.values())
    if candidate["total"] != calculated:
        fail(f"{candidate_id} total mismatch: {candidate['total']} != {calculated}")

    text = " ".join(str(candidate[k]) for k in ("story_title", "research_question", "first_sprint")).lower()
    for phrase in PROHIBITED:
        if phrase in text:
            fail(f"{candidate_id} contains unsupported wording: {phrase}")

    source_list = candidate["sources"]
    if not isinstance(source_list, list) or not source_list:
        fail(f"{candidate_id} has no sources")
    for source in source_list:
        if not isinstance(source, dict):
            fail(f"{candidate_id} has invalid source")
        for key in ("publisher", "title", "date", "url"):
            if not source.get(key):
                fail(f"{candidate_id} source missing {key}")
        if not https(str(source["url"])):
            fail(f"{candidate_id} source is not HTTPS")

    return (1 if calculated >= 24 else 0, len(source_list))


def validate() -> dict[str, object]:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    if data.get("schema") != "safetrace.citizen-portal/0.3":
        fail("unexpected citizen portal schema")
    discovery = data.get("candidates")
    if not isinstance(discovery, list) or len(discovery) < 10:
        fail("candidate radar must contain at least ten candidates")

    social = json.loads(SOCIAL.read_text(encoding="utf-8"))
    if social.get("schema") != "safetrace.social-seasons/0.1":
        fail("unexpected social season schema")
    seasons = social.get("seasons")
    if not isinstance(seasons, list) or len(seasons) != 3:
        fail("social radar must contain exactly seasons 2 to 4")

    expected_titles = {"Kinder im System", "Schutzlücken", "Zwischen den Zuständigkeiten"}
    actual_titles = {str(season.get("title")) for season in seasons if isinstance(season, dict)}
    if actual_titles != expected_titles:
        fail(f"unexpected season titles: {sorted(actual_titles)}")

    ids: set[str] = set()
    high_priority = 0
    sources = 0
    total_candidates = 0

    for candidate in discovery:
        if not isinstance(candidate, dict):
            fail("invalid candidate object")
        high, count = validate_candidate(candidate, ids)
        high_priority += high
        sources += count
        total_candidates += 1

    season_candidates = 0
    for season in seasons:
        if not isinstance(season, dict) or not all(season.get(key) for key in ("id", "title", "subtitle")):
            fail("season metadata is incomplete")
        candidates = season.get("candidates")
        if not isinstance(candidates, list) or len(candidates) < 5:
            fail(f"{season.get('id')} requires at least five candidates")
        for candidate in candidates:
            if not isinstance(candidate, dict):
                fail("invalid social candidate object")
            high, count = validate_candidate(candidate, ids)
            high_priority += high
            sources += count
            total_candidates += 1
            season_candidates += 1

    if season_candidates != 18:
        fail(f"seasons 2 to 4 must contain 18 candidates, found {season_candidates}")

    html = INDEX.read_text(encoding="utf-8")
    for marker in (
        "TRACE Prioritizer", "Case Radar", "keine Übertragung",
        "Sensibler Intake deaktiviert", "automatische Veröffentlichung"
    ):
        if marker.lower() not in html.lower():
            fail(f"index missing safety marker: {marker}")

    season_html = SEASONS_PAGE.read_text(encoding="utf-8")
    for marker in ("Staffeln 2 bis 4", "social_seasons.json", "Schuldvorwurf", "Fair-Play-Standard"):
        if marker.lower() not in season_html.lower():
            fail(f"season page missing marker: {marker}")

    return {
        "status": "valid",
        "total_candidates": total_candidates,
        "animal_and_wildlife_candidates": len(discovery),
        "social_season_candidates": season_candidates,
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
