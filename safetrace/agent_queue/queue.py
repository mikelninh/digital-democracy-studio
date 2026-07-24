from __future__ import annotations

from typing import Any, Iterator

from .model import (
    AgentProposal,
    AgentRun,
    AgentTask,
    AgentTaskSpec,
    HumanDecision,
    RunReceipt,
    SourceAnchor,
    digest,
    iso,
    plain,
)
from .vocabularies import (
    ANCHOR_REQUIRED_AGENTS,
    FORBIDDEN_OUTPUT_INTENTS,
    FORBIDDEN_OUTPUT_KEYS,
    SCHEMA_VERSION,
)
from .workers import PROFILES


def _walk(value: Any, path: str = "output") -> Iterator[tuple[str, str, Any]]:
    if isinstance(value, dict):
        for key, item in value.items():
            yield path, str(key), item
            yield from _walk(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk(item, f"{path}[{index}]")


def validate_proposal(
    agent_type: str,
    output: dict[str, Any],
    anchors: tuple[SourceAnchor, ...],
) -> list[str]:
    blockers: list[str] = []
    if not isinstance(output, dict):
        return ["Agent output must be an object proposal"]

    for path, key, value in _walk(output):
        if key in FORBIDDEN_OUTPUT_KEYS and value not in (False, None, [], {}):
            blockers.append(f"Forbidden output key at {path}.{key}")
        if key in {"intent", "action", "next_action"} and str(value) in FORBIDDEN_OUTPUT_INTENTS:
            blockers.append(f"Forbidden output intent: {value}")
        if key in {"approved", "verified", "publishable"} and value is True:
            blockers.append("Agent cannot mark its own output approved or publishable")

    if agent_type in ANCHOR_REQUIRED_AGENTS and not anchors:
        blockers.append("Agent proposal requires exact source anchors")
    for anchor in anchors:
        try:
            anchor.validate()
        except ValueError as exc:
            blockers.append(str(exc))

    if agent_type == "linker":
        for link in output.get("entity_links", []):
            if (
                link.get("match_state") == "confirmed"
                and len(link.get("independent_identifiers", [])) < 2
            ):
                blockers.append(
                    "False entity link risk: confirmed match lacks two independent identifiers"
                )

    if agent_type == "claim_compiler":
        if (
            output.get("policy_origin")
            in {"prior_legislature", "preexisting_statutory_formula"}
            and output.get("attributed_to_current_government") is True
        ):
            blockers.append(
                "Political attribution error: inherited measure attributed to current government"
            )

    if (
        agent_type == "skeptic"
        and output.get("known_contradiction") is True
        and not output.get("contradictions")
    ):
        blockers.append("Known contradiction was not surfaced")

    if (
        agent_type == "legal_status"
        and output.get("source_stage") == "announced"
        and output.get("status") in {"enacted", "in_force", "convicted", "final_judgment"}
    ):
        blockers.append(
            "Legal status overstatement: announced source cannot prove final status"
        )

    return blockers


class AgentQueue:
    def __init__(self, profiles=None):
        self.profiles = profiles or PROFILES
        self.tasks: dict[str, AgentTask] = {}
        self.runs: dict[str, AgentRun] = {}
        self.proposals: dict[str, AgentProposal] = {}
        self.decisions: dict[str, HumanDecision] = {}
        self.receipts: dict[str, RunReceipt] = {}

    def submit(self, spec: AgentTaskSpec) -> AgentTask:
        spec.validate(self.profiles)
        if spec.id in self.tasks:
            raise ValueError("Task already exists")
        self.tasks[spec.id] = AgentTask(spec)
        return self.tasks[spec.id]

    def start(
        self,
        task_id: str,
        input_payload: dict[str, Any],
        started_at: str,
    ) -> AgentRun:
        task = self.tasks[task_id]
        if task.status != "queued":
            raise ValueError("Only queued tasks can start")
        iso(started_at, "Run started_at")
        input_hash = digest(input_payload)
        trace_key = digest({"task": plain(task.spec), "input_hash": input_hash})
        run_id = f"run:{task_id}:{input_hash[:12]}"
        run = AgentRun(run_id, task_id, "running", started_at, input_hash, trace_key)
        self.runs[run_id] = run
        task.status = "running"
        task.current_run_id = run_id
        return run

    def complete(
        self,
        run_id: str,
        output: dict[str, Any],
        anchors: tuple[SourceAnchor, ...],
        tool_calls: tuple[str, ...],
        cost_cents: int,
        latency_ms: int,
        completed_at: str,
    ) -> tuple[AgentProposal, RunReceipt]:
        run = self.runs[run_id]
        task = self.tasks[run.task_id]
        spec = task.spec
        if run.status != "running":
            raise ValueError("Run is not active")
        iso(completed_at, "Run completed_at")

        tools = set(tool_calls)
        unapproved = tools - set(spec.allowed_tools)
        if unapproved:
            raise ValueError(f"Run used unapproved tools: {sorted(unapproved)}")
        if cost_cents > spec.budget_cents:
            raise ValueError("Run exceeded task budget")
        if latency_ms > spec.timeout_seconds * 1000:
            raise ValueError("Run exceeded task timeout")

        anchor_tuple = tuple(anchors)
        blockers = validate_proposal(spec.agent_type, output, anchor_tuple)
        if blockers:
            run.status = "failed"
            run.completed_at = completed_at
            run.error = "; ".join(blockers)
            task.status = "failed"
            raise ValueError(run.error)

        output_hash = digest(output)
        run.status = "completed"
        run.completed_at = completed_at
        run.output_hash = output_hash
        run.tool_calls = tuple(tool_calls)
        run.cost_cents = cost_cents
        run.latency_ms = latency_ms

        proposal = AgentProposal(
            f"proposal:{run.id}",
            spec.id,
            run.id,
            spec.agent_type,
            "awaiting_human",
            output,
            anchor_tuple,
            completed_at,
        )
        self.proposals[proposal.id] = proposal
        task.status = "awaiting_human"

        receipt = RunReceipt(
            run.id,
            spec.id,
            spec.model_id,
            spec.prompt_version,
            run.input_hash,
            output_hash,
            tuple(tool_calls),
            cost_cents,
            latency_ms,
            run.started_at,
            completed_at,
            run.trace_key,
        )
        self.receipts[run.id] = receipt
        return proposal, receipt

    def decide(
        self,
        proposal_id: str,
        reviewer_id: str,
        outcome: str,
        rationale: str,
        decided_at: str,
    ) -> HumanDecision:
        proposal = self.proposals[proposal_id]
        decision = HumanDecision(
            f"decision:{proposal_id}",
            proposal_id,
            reviewer_id,
            outcome,
            rationale,
            decided_at,
        )
        decision.validate()
        self.decisions[decision.id] = decision
        proposal.status = outcome
        proposal.human_decision_id = decision.id
        self.tasks[proposal.task_id].status = outcome
        return decision

    def metrics(self) -> dict[str, Any]:
        decisions = list(self.decisions.values())
        return {
            "schema_version": SCHEMA_VERSION,
            "tasks": len(self.tasks),
            "runs": len(self.runs),
            "proposals": len(self.proposals),
            "receipts": len(self.receipts),
            "awaiting_human": sum(
                proposal.status == "awaiting_human"
                for proposal in self.proposals.values()
            ),
            "accepted_for_review": sum(
                decision.outcome == "accepted_for_review" for decision in decisions
            ),
            "rejected": sum(decision.outcome == "rejected" for decision in decisions),
            "needs_changes": sum(
                decision.outcome == "needs_changes" for decision in decisions
            ),
            "auto_approved": 0,
            "total_cost_cents": sum(receipt.cost_cents for receipt in self.receipts.values()),
            "mean_latency_ms": (
                round(
                    sum(receipt.latency_ms for receipt in self.receipts.values())
                    / len(self.receipts),
                    2,
                )
                if self.receipts
                else 0
            ),
        }
