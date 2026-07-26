from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
CASE_PATH = ROOT / "case_051.json"
HTML_PATH = ROOT / "index.html"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    data = json.loads(CASE_PATH.read_text(encoding="utf-8"))

    if data.get("id") != "CAND-051":
        fail("unexpected case id")
    if data.get("lifecycle") != "scoping":
        fail("case must remain scoped, not active")
    if data["publication"]["readiness"] != "scoping":
        fail("publication readiness must remain scoping")
    if data["impact_contract"]["status"] != "not_measurable_yet":
        fail("impact must not be presented as already measurable")
    if data["need"]["total"] != sum(
        data["need"][key]
        for key in ("severity", "scale", "urgency", "vulnerability", "public_value", "overlookedness")
    ):
        fail("need score arithmetic mismatch")
    if data["feasibility"]["total"] != sum(
        data["feasibility"][key]
        for key in ("source_access", "falsifiability", "jurisdiction_clarity", "safety_legality", "capacity")
    ):
        fail("feasibility score arithmetic mismatch")

    evidence = data["evidence"]
    for key in ("verified_claims", "unknowns", "counterevidence", "sources"):
        if not evidence.get(key):
            fail(f"missing evidence field: {key}")

    if len(evidence["sources"]) < 5:
        fail("at least five diverse public sources required")
    publishers = {source["publisher"] for source in evidence["sources"]}
    if len(publishers) < 5:
        fail("source publisher diversity is insufficient")
    for source in evidence["sources"]:
        parsed = urlparse(source["url"])
        if parsed.scheme != "https" or not parsed.netloc:
            fail(f"invalid source URL: {source['url']}")
        if source["receipt_status"] not in {"url_only", "snapshot_retained", "hashed_and_reviewed"}:
            fail("invalid receipt status")

    fairness = data["fairness"]
    if not fairness.get("strongest_counterposition") or not fairness.get("alternative_explanations"):
        fail("fairness panel incomplete")
    if not fairness.get("publication_harms"):
        fail("publication harms must be explicit")

    action = data["action_contract"]
    for key in ("target_actor", "exact_ask", "internal_owner", "deliverable", "deadline", "stop_condition"):
        if not action.get(key):
            fail(f"action contract missing: {key}")
    if "verdrängt keinen" not in action["stop_condition"]:
        fail("active portfolio capacity boundary missing")

    dimensions = data.get("family_security_index", {}).get("dimensions", [])
    if len(dimensions) != 7:
        fail("Family Security Index must have exactly seven dimensions")

    html = HTML_PATH.read_text(encoding="utf-8")
    required_markers = [
        "Der Kinderwunsch im Wartestand",
        "kein Geburtenziel",
        "Family Security Index",
        "Die Menschheit stirbt",
        "Reproduktive Freiheit",
        "Scoping",
    ]
    for marker in required_markers:
        if marker.lower() not in html.lower():
            fail(f"public page missing marker: {marker}")

    prohibited = [
        "frauen müssen mehr kinder",
        "kinderlose sind schuld",
        "menschheit stirbt in diesem jahrhundert aus",
        "automatisch veröffentlichen",
    ]
    combined = (CASE_PATH.read_text(encoding="utf-8") + "\n" + html).lower()
    for phrase in prohibited:
        if phrase in combined:
            fail(f"prohibited unsupported/coercive wording: {phrase}")

    print("PASS: Family Security Case 051 is bounded, sourced, fair and remains scoped.")


if __name__ == "__main__":
    main()
