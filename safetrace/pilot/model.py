from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

PILOT_TYPES = {"synthetic_benchmark", "restricted_partner"}
DATA_CLASSES = {"public", "synthetic", "restricted_partner"}
DECISIONS = {"GO_SYNTHETIC", "NO_GO_LIVE", "GO_LIVE"}


@dataclass(frozen=True)
class PilotMetrics:
    baseline_minutes: float
    safetrace_minutes: float
    material_claims: int
    sourced_material_claims: int
    human_reviewed_material_claims: int
    sensitive_publications: int
    sensitive_publications_human_reviewed: int
    false_entity_links: int
    corrections_hidden: int
    serious_privacy_incidents: int
    autonomous_guilt_decisions: int
    reviewer_comprehension_score: float

    @property
    def time_saved_ratio(self) -> float:
        if self.baseline_minutes <= 0:
            raise ValueError("Baseline minutes must be positive")
        return max(0.0, 1.0 - self.safetrace_minutes / self.baseline_minutes)

    @property
    def source_coverage(self) -> float:
        return self.sourced_material_claims / self.material_claims if self.material_claims else 1.0

    @property
    def human_review_coverage(self) -> float:
        return (
            self.human_reviewed_material_claims / self.material_claims
            if self.material_claims
            else 1.0
        )

    def validate(self) -> None:
        if self.safetrace_minutes < 0:
            raise ValueError("SafeTrace minutes cannot be negative")
        if self.sourced_material_claims > self.material_claims:
            raise ValueError("Sourced claims cannot exceed material claims")
        if self.human_reviewed_material_claims > self.material_claims:
            raise ValueError("Reviewed claims cannot exceed material claims")
        if self.sensitive_publications_human_reviewed > self.sensitive_publications:
            raise ValueError("Reviewed sensitive publications cannot exceed total")
        if not 0 <= self.reviewer_comprehension_score <= 1:
            raise ValueError("Comprehension score must be between zero and one")


@dataclass(frozen=True)
class PilotDefinition:
    pilot_id: str
    pilot_type: str
    label: str
    case_id: str
    data_classification: str
    named_partner: str | None
    real_world_validation: bool
    metrics: PilotMetrics
    notes: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if self.pilot_type not in PILOT_TYPES:
            raise ValueError(f"Unsupported pilot type: {self.pilot_type}")
        if self.data_classification not in DATA_CLASSES:
            raise ValueError(f"Unsupported data class: {self.data_classification}")
        self.metrics.validate()
        if self.pilot_type == "synthetic_benchmark":
            if self.real_world_validation:
                raise ValueError("Synthetic benchmark cannot claim real-world validation")
            if self.data_classification not in {"public", "synthetic"}:
                raise ValueError("Synthetic benchmark cannot use restricted data")
        if self.pilot_type == "restricted_partner" and not self.named_partner:
            raise ValueError("A restricted partner pilot requires a named partner")


@dataclass(frozen=True)
class GateResult:
    id: str
    passed: bool
    observed: float | int | str
    target: float | int | str
    explanation: str


@dataclass(frozen=True)
class PilotEvaluation:
    pilot_id: str
    decision: str
    real_world_validated: bool
    passed_gates: int
    total_gates: int
    gates: list[GateResult]
    limitations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_pilot(pilot: PilotDefinition) -> PilotEvaluation:
    pilot.validate()
    metrics = pilot.metrics
    gates = [
        GateResult("time_saved", metrics.time_saved_ratio >= 0.30, round(metrics.time_saved_ratio, 4), 0.30, "At least 30% workflow time reduction."),
        GateResult("source_coverage", metrics.source_coverage == 1.0, round(metrics.source_coverage, 4), 1.0, "Every material claim has a source."),
        GateResult("human_review", metrics.human_review_coverage == 1.0, round(metrics.human_review_coverage, 4), 1.0, "Every material claim is human reviewed."),
        GateResult("sensitive_review", metrics.sensitive_publications_human_reviewed == metrics.sensitive_publications, metrics.sensitive_publications_human_reviewed, metrics.sensitive_publications, "All sensitive publications receive human review."),
        GateResult("false_links", metrics.false_entity_links == 0, metrics.false_entity_links, 0, "No false entity link in the evaluated set."),
        GateResult("visible_corrections", metrics.corrections_hidden == 0, metrics.corrections_hidden, 0, "Corrections are never hidden."),
        GateResult("privacy", metrics.serious_privacy_incidents == 0, metrics.serious_privacy_incidents, 0, "No serious privacy incident."),
        GateResult("no_automated_guilt", metrics.autonomous_guilt_decisions == 0, metrics.autonomous_guilt_decisions, 0, "No autonomous guilt decision."),
        GateResult("comprehension", metrics.reviewer_comprehension_score >= 0.80, round(metrics.reviewer_comprehension_score, 4), 0.80, "Reviewers understand evidence status and limitations."),
    ]
    all_passed = all(item.passed for item in gates)

    if pilot.pilot_type == "synthetic_benchmark":
        decision = "GO_SYNTHETIC" if all_passed else "NO_GO_LIVE"
        limitations = [
            "Results are synthetic benchmark measurements, not partner-validated impact.",
            "No real victim, witness or restricted partner data was processed.",
            "A live pilot remains blocked by partner, security, privacy and legal gates.",
        ]
    else:
        decision = "GO_LIVE" if all_passed and pilot.real_world_validation else "NO_GO_LIVE"
        limitations = [] if decision == "GO_LIVE" else ["Live deployment requires completed real-world validation."]

    if decision not in DECISIONS:
        raise AssertionError("Unexpected pilot decision")

    return PilotEvaluation(
        pilot_id=pilot.pilot_id,
        decision=decision,
        real_world_validated=pilot.real_world_validation,
        passed_gates=sum(item.passed for item in gates),
        total_gates=len(gates),
        gates=gates,
        limitations=limitations,
    )


def load_pilot(path: str | Path) -> PilotDefinition:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    metrics = PilotMetrics(**payload.pop("metrics"))
    return PilotDefinition(metrics=metrics, **payload)
