from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

VALID_STATUSES = {"enacted", "in_force", "announced", "expired"}
VALID_ORIGINS = {
    "merz_coalition",
    "prior_legislature",
    "preexisting_statutory_formula",
    "mixed_or_unclear",
}
VALID_EVIDENCE_STATES = {
    "verified_fact",
    "court_established",
    "official_allegation",
    "analytical_red_flag",
    "unresolved_gap",
    "corrected_or_disproved",
}
VALID_EFFECTS = {
    "positive",
    "negative",
    "neutral",
    "mixed",
    "conditional",
    "uncertain",
}
VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_VERDICTS = {"supported", "partly_supported", "not_supported", "unresolved"}


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    publisher: str
    url: str
    source_type: str

    def validate(self) -> None:
        if not self.id or not self.title or not self.publisher:
            raise ValueError("Source id, title and publisher are required")
        if not self.url.startswith("https://"):
            raise ValueError(f"Source {self.id} must use HTTPS")


@dataclass(frozen=True)
class ImpactChannel:
    dimension: str
    group: str
    effect: str
    confidence: str
    directness: str
    explanation: str

    def validate(self) -> None:
        if self.effect not in VALID_EFFECTS:
            raise ValueError(f"Unsupported effect: {self.effect}")
        if self.confidence not in VALID_CONFIDENCE:
            raise ValueError(f"Unsupported confidence: {self.confidence}")
        if self.directness not in {"direct", "indirect"}:
            raise ValueError(f"Unsupported directness: {self.directness}")
        if not self.dimension or not self.group or not self.explanation:
            raise ValueError("Impact dimension, group and explanation are required")


@dataclass(frozen=True)
class Measure:
    id: str
    title: str
    status: str
    effective_date: str
    origin: str
    attributable_to_current_government: bool
    evidence_state: str
    description: str
    source_ids: tuple[str, ...]
    impacts: tuple[ImpactChannel, ...]
    unresolved_questions: tuple[str, ...]

    def validate(self, known_sources: set[str]) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Unsupported measure status: {self.status}")
        if self.origin not in VALID_ORIGINS:
            raise ValueError(f"Unsupported origin: {self.origin}")
        if self.evidence_state not in VALID_EVIDENCE_STATES:
            raise ValueError(f"Unsupported evidence state: {self.evidence_state}")
        if not self.source_ids:
            raise ValueError(f"Measure {self.id} requires at least one source")
        unknown = set(self.source_ids) - known_sources
        if unknown:
            raise ValueError(f"Measure {self.id} has unknown sources: {sorted(unknown)}")
        if self.origin in {"prior_legislature", "preexisting_statutory_formula"} and self.attributable_to_current_government:
            raise ValueError(f"Inherited measure {self.id} cannot be attributed to the current government")
        for impact in self.impacts:
            impact.validate()


@dataclass(frozen=True)
class ClaimTest:
    id: str
    claim: str
    verdict: str
    reasoning: str
    measure_ids: tuple[str, ...]

    def validate(self, known_measures: set[str]) -> None:
        if self.verdict not in VALID_VERDICTS:
            raise ValueError(f"Unsupported verdict: {self.verdict}")
        if not self.claim or not self.reasoning:
            raise ValueError("Claim and reasoning are required")
        unknown = set(self.measure_ids) - known_measures
        if unknown:
            raise ValueError(f"Claim {self.id} references unknown measures: {sorted(unknown)}")


def _impact_from_dict(item: dict[str, Any]) -> ImpactChannel:
    return ImpactChannel(**item)


def _measure_from_dict(item: dict[str, Any]) -> Measure:
    return Measure(
        id=item["id"],
        title=item["title"],
        status=item["status"],
        effective_date=item["effective_date"],
        origin=item["origin"],
        attributable_to_current_government=item["attributable_to_current_government"],
        evidence_state=item["evidence_state"],
        description=item["description"],
        source_ids=tuple(item["source_ids"]),
        impacts=tuple(_impact_from_dict(impact) for impact in item["impacts"]),
        unresolved_questions=tuple(item.get("unresolved_questions", [])),
    )


def load_case(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    sources = [Source(**item) for item in payload["sources"]]
    for source in sources:
        source.validate()
    source_ids = {source.id for source in sources}
    if len(source_ids) != len(sources):
        raise ValueError("Source ids must be unique")

    measures = [_measure_from_dict(item) for item in payload["measures"]]
    for measure in measures:
        measure.validate(source_ids)
    measure_ids = {measure.id for measure in measures}
    if len(measure_ids) != len(measures):
        raise ValueError("Measure ids must be unique")

    claims = [
        ClaimTest(
            id=item["id"],
            claim=item["claim"],
            verdict=item["verdict"],
            reasoning=item["reasoning"],
            measure_ids=tuple(item["measure_ids"]),
        )
        for item in payload["claim_tests"]
    ]
    for claim in claims:
        claim.validate(measure_ids)

    if payload["methodology"].get("aggregate_fairness_score") is not None:
        raise ValueError("SafeTrace does not publish a single aggregate fairness score")

    return {
        **payload,
        "sources": sources,
        "measures": measures,
        "claim_tests": claims,
    }


def build_public_assessment(case: dict[str, Any]) -> dict[str, Any]:
    measures: list[Measure] = case["measures"]
    claims: list[ClaimTest] = case["claim_tests"]
    sources: list[Source] = case["sources"]

    direct_impacts = [impact for measure in measures for impact in measure.impacts if impact.directness == "direct"]
    indirect_impacts = [impact for measure in measures for impact in measure.impacts if impact.directness == "indirect"]
    current_government = [measure for measure in measures if measure.attributable_to_current_government]
    inherited = [measure for measure in measures if not measure.attributable_to_current_government]

    return {
        "schema_version": "safetrace.law-fairness/1.0",
        "case_id": case["case_id"],
        "title": case["title"],
        "jurisdiction": case["jurisdiction"],
        "last_reviewed_at": case["last_reviewed_at"],
        "question": case["question"],
        "methodology": case["methodology"],
        "summary": {
            "measures_reviewed": len(measures),
            "current_government_measures": len(current_government),
            "inherited_or_formula_measures": len(inherited),
            "direct_impacts": len(direct_impacts),
            "indirect_impacts": len(indirect_impacts),
            "overall_claim_verdict": case["overall_claim_verdict"],
            "overall_explanation": case["overall_explanation"],
        },
        "measures": [
            {
                "id": measure.id,
                "title": measure.title,
                "status": measure.status,
                "effective_date": measure.effective_date,
                "origin": measure.origin,
                "attributable_to_current_government": measure.attributable_to_current_government,
                "evidence_state": measure.evidence_state,
                "description": measure.description,
                "source_ids": list(measure.source_ids),
                "impacts": [impact.__dict__ for impact in measure.impacts],
                "unresolved_questions": list(measure.unresolved_questions),
            }
            for measure in measures
        ],
        "claim_tests": [
            {
                "id": claim.id,
                "claim": claim.claim,
                "verdict": claim.verdict,
                "reasoning": claim.reasoning,
                "measure_ids": list(claim.measure_ids),
            }
            for claim in claims
        ],
        "documented_influence_activity": case.get("documented_influence_activity", []),
        "sources": [source.__dict__ for source in sources],
        "publication_boundary": case["publication_boundary"],
    }
