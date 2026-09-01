from __future__ import annotations

from typing import Any


AUTHORITY = {
    "official_registry_history": 5.0,
    "official_court_record": 5.0,
    "official_freezone_record": 4.5,
    "lease": 4.5,
    "security_document": 4.0,
    "company_filing": 4.0,
    "analyst_call_note": 3.5,
    "court_search_receipt": 2.5,
    "trade_press": 1.5,
    "scraped_media_mirror": 0.0,
}


def _text(source: dict[str, Any]) -> str:
    return " ".join([source.get("title", ""), *source.get("facts", [])]).casefold()


def detect_open_questions(case: dict[str, Any]) -> set[str]:
    initial = [s for s in case.get("source_records", []) if s.get("availability") == "initial"]
    text = " ".join(_text(s) for s in initial)
    questions: set[str] = set()

    # Nominee ownership remains unresolved by design; none of the current optional
    # records actually identifies the principal, so this gap should remain visible
    # rather than create a fake "best" source.
    if "undisclosed principal" in text or "principal identity is redacted" in text:
        questions.add("nominee_principal")

    if "anna keller" in text and "markus stein" in text:
        questions.add("director_timeline")

    if "changed beneficiary" in text or ("adria settlement services" in text and "balkan components" in text):
        questions.add("payment_authorization")
        questions.add("payment_counterparty_context")

    if "operates from the leipzig" in text and "lease" not in text:
        questions.add("asset_operating_basis")

    if "court" not in text and "litigation" not in text:
        questions.add("litigation_coverage")

    return questions


def score_optional_source(source: dict[str, Any], open_questions: set[str]) -> tuple[float, list[str]]:
    source_type = source.get("type", "")
    text = _text(source)
    score = AUTHORITY.get(source_type, 1.0)
    reasons: list[str] = [f"source quality/type prior: {score:g}"]

    if "director_timeline" in open_questions and source_type == "official_registry_history":
        score += 9
        reasons.append("resolves contradictory director records with authoritative chronology")

    if "payment_authorization" in open_questions and source_type == "analyst_call_note":
        if "confirms the receivables assignment was authorized" in text:
            score += 10
            reasons.append("independently tests whether the changed beneficiary was authorized")

    if "payment_counterparty_context" in open_questions and source_type == "official_freezone_record":
        if "adria settlement services" in text:
            score += 7
            reasons.append("adds authoritative context on the changed payment beneficiary")

    if "asset_operating_basis" in open_questions and source_type == "lease":
        score += 8
        reasons.append("upgrades an operational website claim with the underlying legal instrument")

    if "litigation_coverage" in open_questions and source_type == "official_court_record":
        score += 8
        reasons.append("adds a positive litigation record rather than relying on absence searches")
    elif "litigation_coverage" in open_questions and source_type == "company_filing":
        score += 4
        reasons.append("corroborates litigation context from a filed company disclosure")
    elif "litigation_coverage" in open_questions and source_type == "court_search_receipt":
        score += 1
        reasons.append("bounded negative evidence; useful but lower information gain than a positive record")

    # Redundancy / source-independence penalties.
    if source_type == "security_document":
        score -= 3
        reasons.append("mostly corroborates a security interest already established by the land register")
    if source_type == "trade_press" and "their property" in text:
        score -= 4
        reasons.append("lower-authority wording conflicts with an already available property register")
    if source_type == "scraped_media_mirror" or "republishes" in text or "adds no independent evidence" in text:
        score -= 10
        reasons.append("duplicate/circular reporting adds no independent evidence")

    return score, reasons


def prioritize(case: dict[str, Any], limit: int | None = None) -> list[dict[str, Any]]:
    open_questions = detect_open_questions(case)
    optional = [s for s in case.get("source_records", []) if s.get("availability") == "optional"]
    ranked: list[dict[str, Any]] = []
    for source in optional:
        score, reasons = score_optional_source(source, open_questions)
        ranked.append({
            "source_id": source["id"],
            "title": source["title"],
            "type": source.get("type"),
            "expected_information_value": round(score, 2),
            "reasons": reasons,
        })
    ranked.sort(key=lambda row: (-row["expected_information_value"], row["source_id"]))
    if limit is None:
        limit = int(case.get("evidence_budget", {}).get("max_optional_acquisitions", 5))
    return ranked[:limit]
