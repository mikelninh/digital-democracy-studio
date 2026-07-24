from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .model import WorkerProfile


PROFILES = {
    "scout": WorkerProfile(
        "scout",
        "Find candidate public sources without making findings.",
        frozenset({"search_public_sources", "read_public_source"}),
        "public", 120, 100, "safetrace.agent.scout/1",
    ),
    "archivist": WorkerProfile(
        "archivist",
        "Acquire and register reviewed public-source snapshots.",
        frozenset({"read_public_source", "snapshot_public_source", "hash_content"}),
        "public", 180, 100, "safetrace.agent.archivist/1",
    ),
    "reader": WorkerProfile(
        "reader",
        "Extract bounded passages with exact source anchors.",
        frozenset({"read_vault_object", "extract_text", "cite_anchor"}),
        "sensitive_internal", 180, 150, "safetrace.agent.reader/1",
    ),
    "linker": WorkerProfile(
        "linker",
        "Propose entity links while preserving uncertainty.",
        frozenset({"read_entities", "read_evidence", "propose_entity_link"}),
        "sensitive_internal", 180, 150, "safetrace.agent.linker/1",
    ),
    "chronologist": WorkerProfile(
        "chronologist",
        "Propose dated events and timeline ordering.",
        frozenset({"read_events", "read_evidence", "propose_timeline"}),
        "sensitive_internal", 180, 150, "safetrace.agent.chronologist/1",
    ),
    "claim_compiler": WorkerProfile(
        "claim_compiler",
        "Draft bounded claim proposals from anchored evidence.",
        frozenset({"read_evidence", "read_claims", "propose_claim"}),
        "sensitive_internal", 240, 200, "safetrace.agent.claim/1",
    ),
    "skeptic": WorkerProfile(
        "skeptic",
        "Search for contradictions, alternatives and missing evidence.",
        frozenset({"read_claims", "read_evidence", "propose_contradiction"}),
        "sensitive_internal", 240, 200, "safetrace.agent.skeptic/1",
    ),
    "quant": WorkerProfile(
        "quant",
        "Calculate transparent metrics from reviewed datasets.",
        frozenset({"read_public_dataset", "calculate", "propose_metric"}),
        "sensitive_internal", 240, 200, "safetrace.agent.quant/1",
    ),
    "legal_status": WorkerProfile(
        "legal_status",
        "Classify formal legal or policy status from official records.",
        frozenset({"read_official_source", "classify_legal_status"}),
        "sensitive_internal", 180, 150, "safetrace.agent.legal-status/1",
    ),
    "guardian": WorkerProfile(
        "guardian",
        "Test proposals against privacy, harm and publication boundaries.",
        frozenset({"read_proposal", "run_safety_checks"}),
        "sensitive_internal", 180, 150, "safetrace.agent.guardian/1",
    ),
    "watchtower": WorkerProfile(
        "watchtower",
        "Compare source receipts and propose material-change reviews.",
        frozenset({"read_source_receipts", "compare_snapshot", "propose_change"}),
        "public", 180, 100, "safetrace.agent.watchtower/1",
    ),
    "explainer": WorkerProfile(
        "explainer",
        "Draft plain-language explanations from approved claims only.",
        frozenset({"read_approved_claims", "draft_explanation"}),
        "public", 180, 150, "safetrace.agent.explainer/1",
    ),
}

for worker_profile in PROFILES.values():
    worker_profile.validate()


@dataclass(frozen=True)
class BoundedWorker:
    profile: WorkerProfile
    executor: Callable[[dict[str, Any]], dict[str, Any]]

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.executor(payload)


def profile(agent_type: str) -> WorkerProfile:
    return PROFILES[agent_type]
