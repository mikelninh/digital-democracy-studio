"""Fail-closed validation for Spuren im System · Tierwohl."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from prioritize import DIMENSIONS, compute_score, decision_for

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "cases.json"
INDEX = ROOT / "index.html"
SOURCE_REGISTRY = ROOT / "governance" / "source_registry.json"
REPLY_PACKETS = ROOT / "governance" / "right_of_reply_packets.json"
IMPACT_LOG = ROOT / "impact_log.json"

REQUIRED_GOVERNANCE_FILES = (
    ROOT / "governance" / "README.md",
    ROOT / "governance" / "REVIEW_PROTOCOL.md",
    ROOT / "governance" / "MODERATION_AND_COMPLAINTS.md",
    ROOT / "governance" / "RIGHT_OF_REPLY.md",
    ROOT / "governance" / "SOURCE_RETENTION.md",
    ROOT / "governance" / "ACCESSIBILITY_AND_COMPREHENSION.md",
    ROOT / "governance" / "SENSITIVE_TIPS_PARTNER_GATE.md",
)

REQUIRED_CASE_FIELDS = {
    "id",
    "issue",
    "slug",
    "story_title",
    "story_deck",
    "title",
    "status",
    "verdict",
    "evidence_strength",
    "impact_potential",
    "urgency",
    "priority",
    "publication_readiness",
    "review_status",
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

REQUIRED_REVIEW_KEYS = {
    "editorial",
    "animal_welfare_domain",
    "legal_privacy",
    "right_of_reply",
}


def fail(message: str) -> None:
    raise ValueError(message)


def valid_https_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        fail(f"{path.relative_to(ROOT)} is missing")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain an object")
    return value


def validate() -> dict[str, object]:
    for path in (CATALOG, INDEX, SOURCE_REGISTRY, REPLY_PACKETS, IMPACT_LOG):
        if not path.exists():
            fail(f"{path.relative_to(ROOT)} is missing")
    for path in REQUIRED_GOVERNANCE_FILES:
        if not path.exists():
            fail(f"governance file missing: {path.name}")

    data = load_json(CATALOG)
    if data.get("schema") != "safetrace.animal-welfare-series/0.2":
        fail("unexpected schema identifier")
    if data.get("series_name") != "Spuren im System":
        fail("unexpected series name")
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) != 7:
        fail("catalog must contain exactly seven cases")

    ids: set[str] = set()
    issues: set[int] = set()
    story_titles: set[str] = set()
    source_ids: set[str] = set()
    source_count = 0
    priority_results: list[dict[str, object]] = []

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            fail(f"case {index} is not an object")
        missing = REQUIRED_CASE_FIELDS - case.keys()
        if missing:
            fail(f"{case.get('id', index)} missing fields: {sorted(missing)}")

        case_id = case["id"]
        if not isinstance(case_id, str) or case_id in ids:
            fail(f"invalid or duplicate case id: {case_id}")
        ids.add(case_id)

        issue = case["issue"]
        if not isinstance(issue, int) or issue <= 0 or issue in issues:
            fail(f"invalid or duplicate issue for {case_id}")
        issues.add(issue)

        story_title = case["story_title"]
        if not isinstance(story_title, str) or len(story_title.strip()) < 8:
            fail(f"{case_id} requires a meaningful story title")
        if story_title in story_titles:
            fail(f"duplicate story title: {story_title}")
        story_titles.add(story_title)

        if not isinstance(case["story_deck"], str) or len(case["story_deck"]) < 40:
            fail(f"{case_id} story deck is too short")

        for score_field in ("evidence_strength", "impact_potential", "urgency"):
            score = case[score_field]
            if not isinstance(score, int) or not 1 <= score <= 5:
                fail(f"{case_id} has invalid {score_field}: {score}")

        priority = case["priority"]
        if not isinstance(priority, dict):
            fail(f"{case_id} priority must be an object")
        dimensions = {name: priority.get(name) for name in DIMENSIONS}
        penalties = priority.get("penalties")
        if not isinstance(penalties, dict):
            fail(f"{case_id} penalties must be an object")
        calculated = compute_score(dimensions, penalties)
        if priority.get("total") != calculated:
            fail(f"{case_id} priority total mismatch")
        expected_decision = decision_for(calculated)
        if priority.get("decision") != expected_decision:
            fail(f"{case_id} priority decision mismatch")
        if not isinstance(priority.get("rationale"), str) or len(priority["rationale"]) < 30:
            fail(f"{case_id} priority rationale is missing")
        priority_results.append(
            {
                "case_id": case_id,
                "score": calculated,
                "decision": expected_decision,
                "publication_readiness": case["publication_readiness"],
            }
        )

        review_status = case["review_status"]
        if not isinstance(review_status, dict) or not REQUIRED_REVIEW_KEYS <= review_status.keys():
            fail(f"{case_id} review status is incomplete")
        if any(value == "complete" for value in review_status.values()):
            fail(f"{case_id} must not fabricate completed independent review")

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
            for field in (
                "story_title",
                "story_deck",
                "title",
                "verdict",
                "publish_line",
                "next_action",
                "win_win_win",
            )
        ).lower()
        for phrase in PROHIBITED_PHRASES:
            if phrase in combined_text:
                fail(f"{case_id} contains prohibited unsupported wording: {phrase}")

        for source in case["sources"]:
            if not isinstance(source, dict):
                fail(f"{case_id} has a non-object source")
            for key in ("source_id", "publisher", "title", "date", "url"):
                if not source.get(key):
                    fail(f"{case_id} source missing {key}")
            if source["source_id"] in source_ids:
                fail(f"duplicate source id: {source['source_id']}")
            source_ids.add(source["source_id"])
            if not valid_https_url(source["url"]):
                fail(f"{case_id} source is not a valid HTTPS URL: {source['url']}")
            source_count += 1

    registry = load_json(SOURCE_REGISTRY)
    registry_sources = registry.get("sources")
    if not isinstance(registry_sources, list):
        fail("source registry requires a sources list")
    registry_ids = {entry.get("source_id") for entry in registry_sources if isinstance(entry, dict)}
    if registry_ids != source_ids:
        fail("source registry IDs do not match case catalog")
    for entry in registry_sources:
        if entry.get("data_zone") != "public":
            fail(f"{entry.get('source_id')} is outside the public data zone")
        if entry.get("snapshot_status") not in {
            "registry_only_snapshot_pending",
            "original_retained_hash_verified",
            "moved_or_unavailable",
            "fetch_error",
            "material_change_pending_review",
        }:
            fail(f"{entry.get('source_id')} has invalid snapshot status")
        if entry.get("snapshot_status") == "original_retained_hash_verified":
            digest = entry.get("sha256")
            if not isinstance(digest, str) or len(digest) != 64:
                fail(f"{entry.get('source_id')} lacks a valid SHA-256 digest")

    packets = load_json(REPLY_PACKETS).get("packets")
    if not isinstance(packets, list) or {p.get("case_id") for p in packets} != ids:
        fail("right-of-reply packets must cover every case")
    if any(p.get("status") == "sent" and not p.get("delivery_receipt") for p in packets):
        fail("sent right-of-reply packet lacks delivery receipt")

    impact_cases = load_json(IMPACT_LOG).get("cases")
    if not isinstance(impact_cases, list) or {p.get("case_id") for p in impact_cases} != ids:
        fail("impact log must cover every case")
    for record in impact_cases:
        if record.get("events") != []:
            fail("v0.2 must not fabricate impact events")

    html = INDEX.read_text(encoding="utf-8")
    required_html_markers = (
        "Spuren im System",
        "Staffel Tierwohl",
        "Citizen Case Prioritizer",
        "Der TRACE Loop",
        "Impact ohne Selbsttäuschung",
        "Korrektur melden",
        "Beschwerde einreichen",
        "keine vertraulichen",
        "cases.json",
        "governance/README.md",
    )
    for marker in required_html_markers:
        if marker not in html:
            fail(f"index.html missing marker: {marker}")
    if "fonts.googleapis.com" in html or "fonts.gstatic.com" in html:
        fail("index.html must not request third-party fonts")

    return {
        "schema": data["schema"],
        "series": data["series_name"],
        "cases": len(cases),
        "sources": source_count,
        "source_snapshots_pending": sum(
            1
            for entry in registry_sources
            if entry.get("snapshot_status") == "registry_only_snapshot_pending"
        ),
        "priority_results": sorted(
            priority_results,
            key=lambda item: (-int(item["score"]), str(item["case_id"])),
        ),
        "all_cases_have_unknowns": True,
        "all_cases_have_impact_metrics": True,
        "review_packets_implemented": True,
        "independent_reviews_completed": 0,
        "sensitive_uploads_enabled": False,
        "automatic_publication_enabled": False,
        "status": "valid",
    }


def main() -> int:
    try:
        result = validate()
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
