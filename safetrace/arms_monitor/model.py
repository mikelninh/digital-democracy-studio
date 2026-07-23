from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any

EVENT_TYPES = {
    "policy_or_budget_authority",
    "parliamentary_approval",
    "procurement_contract",
    "production_activity",
    "export_authorisation",
    "delivery",
    "planned_delivery",
    "operational_use",
}
EVIDENCE_STATES = {"verified_fact", "analytical_red_flag", "unresolved_gap"}


@dataclass(frozen=True)
class SourceRef:
    id: str
    url: str
    title: str
    publisher: str
    checked_at: str
    anchor: str | None = None

    def validate(self) -> None:
        if not self.id or not self.url.startswith("https://"):
            raise ValueError("A stable source id and HTTPS URL are required")


@dataclass(frozen=True)
class Event:
    id: str
    type: str
    date: str
    title: str
    evidence_state: str
    source: SourceRef
    actor: str | None = None
    recipient_or_beneficiary: str | None = None
    amount_eur: str | None = None
    status: str = "recorded"
    attributes: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.type not in EVENT_TYPES:
            raise ValueError(f"Unsupported event type: {self.type}")
        if self.evidence_state not in EVIDENCE_STATES:
            raise ValueError(f"Unsupported evidence state: {self.evidence_state}")
        self.source.validate()
        if self.amount_eur is not None and Decimal(self.amount_eur) < 0:
            raise ValueError("Amounts cannot be negative")
        if self.type == "planned_delivery" and self.status != "planned":
            raise ValueError("A planned delivery must remain labelled planned")
        if self.type == "delivery" and self.status == "planned":
            raise ValueError("A planned event cannot be represented as an actual delivery")
        if self.type == "export_authorisation" and self.attributes.get("delivered") is True:
            raise ValueError("An export authorisation cannot itself prove delivery")


@dataclass
class AccountabilityCase:
    id: str
    title: str
    jurisdiction: str
    publication_boundary: str
    events: list[Event]
    unresolved_questions: list[dict[str, Any]] = field(default_factory=list)

    def validate(self) -> None:
        ids: set[str] = set()
        for event in self.events:
            event.validate()
            if event.id in ids:
                raise ValueError(f"Duplicate event id: {event.id}")
            ids.add(event.id)
        for question in self.unresolved_questions:
            if question.get("evidence_state") not in {"analytical_red_flag", "unresolved_gap"}:
                raise ValueError("Unresolved questions must remain labelled as gaps or red flags")
            if not question.get("safe_interpretation"):
                raise ValueError("Every unresolved question requires a careful interpretation")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": "safetrace.arms-accountability/0.6",
            "id": self.id,
            "title": self.title,
            "jurisdiction": self.jurisdiction,
            "publication_boundary": self.publication_boundary,
            "events": [asdict(event) for event in self.events],
            "unresolved_questions": self.unresolved_questions,
        }
