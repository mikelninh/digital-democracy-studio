from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .model import CaseCharter, Risk
from .vocabularies import BASELINE_PROHIBITED_METHODS

CASE_ACCEPTANCE_QUESTIONS = (
    {"id": "research_question", "question": "What exactly are we trying to establish?", "required": True},
    {"id": "public_interest_rationale", "question": "Why does answering this matter to the public?", "required": True},
    {"id": "scope_inclusions", "question": "Which decisions, dates, actors and records are in scope?", "required": True},
    {"id": "scope_exclusions", "question": "What is explicitly out of scope?", "required": True},
    {"id": "expected_source_types", "question": "Which primary and secondary sources should exist?", "required": True},
    {"id": "affected_groups", "question": "Who could benefit, be harmed or be misidentified?", "required": True},
    {"id": "risks", "question": "What privacy, legal, security and harm risks exist?", "required": True},
    {"id": "prohibited_methods", "question": "Which methods are forbidden for this case?", "required": True},
    {"id": "publication_boundary", "question": "What may and may not be published?", "required": True},
)


@dataclass(frozen=True)
class AcceptanceResult:
    accepted: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    required_reviews: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CaseAcceptanceWizard:
    """Deterministic intake gate. It cannot accept restricted work by itself."""

    def questions(self) -> tuple[dict[str, Any], ...]:
        return CASE_ACCEPTANCE_QUESTIONS

    def evaluate(self, charter: CaseCharter) -> AcceptanceResult:
        blockers: list[str] = []
        warnings: list[str] = []
        required_reviews: list[str] = ["case_lead", "editorial"]

        try:
            charter.validate()
        except ValueError as exc:
            blockers.append(str(exc))
            return AcceptanceResult(False, tuple(blockers), tuple(warnings), tuple(required_reviews))

        if len(charter.research_question) > 320:
            blockers.append("Research question is too broad; split it into a bounded question")
        if len(charter.scope_inclusions) > 12:
            warnings.append("Large scope: consider splitting the case into phases")
        if not any("official" in item.lower() or "primary" in item.lower() for item in charter.expected_source_types):
            warnings.append("No explicit primary or official source type is expected")
        if not charter.risks:
            blockers.append("At least one case-specific risk and mitigation is required")
        if any(risk.severity in {"high", "critical"} for risk in charter.risks):
            required_reviews.extend(["security_privacy", "legal_editorial"])
        if charter.legal_review_required:
            required_reviews.append("legal_editorial")
        if "restricted_partner" in charter.permitted_data_zones:
            blockers.append(
                "Restricted-partner data cannot be authorised by the intake wizard; an approved partner environment is required"
            )
        if charter.status == "accepted" and blockers:
            blockers.append("Accepted status is inconsistent with unresolved blockers")
        if charter.case_owner == charter.editorial_owner:
            warnings.append("Case and editorial ownership are not separated")

        required_reviews = list(dict.fromkeys(required_reviews))
        return AcceptanceResult(not blockers, tuple(blockers), tuple(warnings), tuple(required_reviews))

    def template(self, *, case_id: str = "case-new") -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "id": f"charter:{case_id}",
            "case_id": case_id,
            "title": "Bounded public-interest investigation",
            "research_question": "Which documented public decisions and records answer the bounded accountability question?",
            "public_interest_rationale": "Explain the concrete public benefit, affected population and accountability gap in at least one paragraph.",
            "jurisdiction": "Germany",
            "case_owner": "named_case_lead",
            "editorial_owner": "named_editorial_reviewer",
            "created_at": now,
            "status": "draft",
            "scope_inclusions": ["Named decision, period and public records"],
            "scope_exclusions": ["Private-person investigation and unsupported criminal allegations"],
            "expected_source_types": ["primary official records", "authoritative secondary analysis"],
            "affected_groups": ["citizens", "organisations materially discussed"],
            "risks": [
                {
                    "id": "risk:misinterpretation",
                    "category": "misinterpretation",
                    "description": "Documented relationships may be mistaken for proof of unlawful conduct.",
                    "likelihood": "medium",
                    "severity": "high",
                    "mitigation": "Separate facts, allegations, analytical gaps and causal claims in every output.",
                    "owner": "named_editorial_reviewer",
                }
            ],
            "prohibited_methods": sorted(BASELINE_PROHIBITED_METHODS),
            "permitted_data_zones": ["public"],
            "publication_boundary": "Public official records only; no automated accusation, publication, referral or private-address disclosure.",
            "legal_review_required": False,
            "constitution_ref": "safetrace/CONSTITUTION.md",
            "constitution_version": "1.0",
        }

    def from_payload(self, payload: dict[str, Any]) -> CaseCharter:
        data = dict(payload)
        data["scope_inclusions"] = tuple(data.get("scope_inclusions", []))
        data["scope_exclusions"] = tuple(data.get("scope_exclusions", []))
        data["expected_source_types"] = tuple(data.get("expected_source_types", []))
        data["affected_groups"] = tuple(data.get("affected_groups", []))
        data["prohibited_methods"] = tuple(data.get("prohibited_methods", []))
        data["permitted_data_zones"] = tuple(data.get("permitted_data_zones", []))
        data["risks"] = tuple(Risk(**item) for item in data.get("risks", []))
        return CaseCharter(**data)


def main() -> int:
    parser = argparse.ArgumentParser(description="SafeTrace Case Acceptance Wizard")
    parser.add_argument("--template", action="store_true", help="Print a machine-readable Case Charter template")
    parser.add_argument("--case-id", default="case-new")
    parser.add_argument("--evaluate", type=Path, help="Evaluate a Case Charter JSON file")
    args = parser.parse_args()

    wizard = CaseAcceptanceWizard()
    if args.template:
        print(json.dumps(wizard.template(case_id=args.case_id), ensure_ascii=False, indent=2))
        return 0
    if args.evaluate:
        payload = json.loads(args.evaluate.read_text(encoding="utf-8"))
        charter = wizard.from_payload(payload)
        result = wizard.evaluate(charter)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.accepted else 2
    parser.error("Use --template or --evaluate")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
