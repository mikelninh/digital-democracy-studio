from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from safetrace.core.vocabularies import DATA_ZONES, DATA_ZONE_ORDER, FORBIDDEN_AGENT_TOOLS
from .vocabularies import DECISION_OUTCOMES, SCHEMA_VERSION


def required(value: str, name: str, minimum: int = 1) -> None:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise ValueError(f"{name} is required")


def iso(value: str, name: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be ISO-8601") from exc


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def plain(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {field.name: plain(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [plain(item) for item in value]
    return value


@dataclass(frozen=True)
class WorkerProfile:
    agent_type: str
    purpose: str
    allowed_tools: frozenset[str]
    max_data_zone: str
    max_timeout_seconds: int
    max_budget_cents: int
    output_schema: str

    def validate(self) -> None:
        required(self.agent_type, "Agent type")
        required(self.purpose, "Worker purpose", 10)
        required(self.output_schema, "Output schema")
        if self.max_data_zone not in DATA_ZONES:
            raise ValueError("Unsupported worker data zone")
        bad = self.allowed_tools & FORBIDDEN_AGENT_TOOLS
        if bad:
            raise ValueError(f"Worker profile includes prohibited tools: {sorted(bad)}")


@dataclass(frozen=True)
class AgentTaskSpec:
    id: str
    case_id: str
    purpose: str
    agent_type: str
    allowed_tools: tuple[str, ...]
    max_data_zone: str
    input_schema: str
    output_schema: str
    model_id: str
    prompt_version: str
    timeout_seconds: int
    budget_cents: int
    human_approver: str
    input_refs: tuple[str, ...]
    created_at: str

    def validate(self, profiles: dict[str, WorkerProfile]) -> None:
        for value, name in (
            (self.id, "Task id"), (self.case_id, "Case id"),
            (self.purpose, "Task purpose"), (self.input_schema, "Input schema"),
            (self.output_schema, "Output schema"), (self.model_id, "Model id"),
            (self.prompt_version, "Prompt version"),
            (self.human_approver, "Human approver"),
        ):
            required(value, name)
        iso(self.created_at, "Task created_at")
        if self.agent_type not in profiles:
            raise ValueError(f"Unsupported agent type: {self.agent_type}")
        profile = profiles[self.agent_type]
        profile.validate()
        requested = set(self.allowed_tools)
        bad = requested & FORBIDDEN_AGENT_TOOLS
        if bad:
            raise ValueError(f"Agent task requests prohibited tools: {sorted(bad)}")
        unknown = requested - set(profile.allowed_tools)
        if unknown:
            raise ValueError(f"Agent task requests unapproved tools: {sorted(unknown)}")
        if self.max_data_zone not in DATA_ZONES:
            raise ValueError("Unsupported task data zone")
        if DATA_ZONE_ORDER[self.max_data_zone] > DATA_ZONE_ORDER[profile.max_data_zone]:
            raise ValueError("Agent task exceeds worker data-zone ceiling")
        if not 1 <= self.timeout_seconds <= profile.max_timeout_seconds:
            raise ValueError("Agent task timeout exceeds worker ceiling")
        if not 0 <= self.budget_cents <= profile.max_budget_cents:
            raise ValueError("Agent task budget exceeds worker ceiling")
        if not self.input_refs:
            raise ValueError("Agent task requires traceable input refs")


@dataclass
class AgentTask:
    spec: AgentTaskSpec
    status: str = "queued"
    current_run_id: str | None = None


@dataclass(frozen=True)
class SourceAnchor:
    source_id: str
    anchor: str
    receipt_id: str | None = None
    object_hash: str | None = None

    def validate(self) -> None:
        required(self.source_id, "Source id")
        required(self.anchor, "Source anchor")


@dataclass
class AgentRun:
    id: str
    task_id: str
    status: str
    started_at: str
    input_hash: str
    trace_key: str
    completed_at: str | None = None
    output_hash: str | None = None
    tool_calls: tuple[str, ...] = ()
    cost_cents: int = 0
    latency_ms: int = 0
    error: str | None = None


@dataclass
class AgentProposal:
    id: str
    task_id: str
    run_id: str
    agent_type: str
    status: str
    output: dict[str, Any]
    anchors: tuple[SourceAnchor, ...]
    created_at: str
    safety_flags: tuple[str, ...] = ()
    human_decision_id: str | None = None


@dataclass(frozen=True)
class HumanDecision:
    id: str
    proposal_id: str
    reviewer_id: str
    outcome: str
    rationale: str
    decided_at: str

    def validate(self) -> None:
        required(self.id, "Decision id")
        required(self.proposal_id, "Proposal id")
        required(self.reviewer_id, "Reviewer")
        required(self.rationale, "Decision rationale", 10)
        iso(self.decided_at, "Decision timestamp")
        if self.outcome not in DECISION_OUTCOMES:
            raise ValueError("Unsupported decision outcome")
        if self.reviewer_id.startswith("agent:"):
            raise ValueError("Agent cannot act as human reviewer")


@dataclass(frozen=True)
class RunReceipt:
    run_id: str
    task_id: str
    model_id: str
    prompt_version: str
    input_hash: str
    output_hash: str
    tool_calls: tuple[str, ...]
    cost_cents: int
    latency_ms: int
    started_at: str
    completed_at: str
    trace_key: str


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    category: str
    expected: str
    observed: str
    passed: bool
    blocker: str | None = None


def empty_contract() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "tasks": [],
        "runs": [],
        "proposals": [],
        "decisions": [],
        "receipts": [],
    }
