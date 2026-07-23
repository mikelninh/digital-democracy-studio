from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any

ALLOWED_NODE_TYPES = {"organisation", "political_party", "lobby_entry", "policy_interest"}
ALLOWED_EDGE_TYPES = {"donated_to", "registered_as", "declares_interest_in"}
ALLOWED_EVIDENCE_STATES = {"verified_official_record", "human_reviewed_match"}


@dataclass(frozen=True)
class Provenance:
    source_id: str
    source_url: str
    source_title: str
    retrieved_or_checked_at: str
    evidence_state: str = "verified_official_record"
    source_anchor: str | None = None

    def validate(self) -> None:
        if not self.source_id or not self.source_url.startswith("https://"):
            raise ValueError("Every graph fact requires a stable source id and HTTPS URL")
        if self.evidence_state not in ALLOWED_EVIDENCE_STATES:
            raise ValueError(f"Unsupported evidence state: {self.evidence_state}")


@dataclass(frozen=True)
class Node:
    id: str
    type: str
    label: str
    attributes: dict[str, Any] = field(default_factory=dict)
    provenance: tuple[Provenance, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        if self.type not in ALLOWED_NODE_TYPES:
            raise ValueError(f"Unsupported node type: {self.type}")
        if not self.id or not self.label:
            raise ValueError("Node id and label are required")
        for item in self.provenance:
            item.validate()


@dataclass(frozen=True)
class Edge:
    id: str
    type: str
    source: str
    target: str
    attributes: dict[str, Any] = field(default_factory=dict)
    provenance: tuple[Provenance, ...] = field(default_factory=tuple)
    interpretation: str = "documented_relationship_only"

    def validate(self) -> None:
        if self.type not in ALLOWED_EDGE_TYPES:
            raise ValueError(f"Unsupported edge type: {self.type}")
        if not self.provenance:
            raise ValueError("Every edge requires provenance")
        for item in self.provenance:
            item.validate()
        if self.type == "donated_to":
            amount = Decimal(str(self.attributes.get("amount_eur", "0")))
            if amount <= 0:
                raise ValueError("Donation amount must be positive")
            if not self.attributes.get("received_date"):
                raise ValueError("Donation received date is required")


@dataclass
class Graph:
    nodes: list[Node]
    edges: list[Edge]
    metadata: dict[str, Any]

    def validate(self) -> None:
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Duplicate node ids")
        known = set(node_ids)
        edge_ids: set[str] = set()
        for node in self.nodes:
            node.validate()
        for edge in self.edges:
            edge.validate()
            if edge.id in edge_ids:
                raise ValueError(f"Duplicate edge id: {edge.id}")
            edge_ids.add(edge.id)
            if edge.source not in known or edge.target not in known:
                raise ValueError(f"Unknown edge endpoint: {edge.id}")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": "safetrace.political-money-graph/0.4",
            "metadata": self.metadata,
            "nodes": [asdict(node) for node in self.nodes],
            "edges": [asdict(edge) for edge in self.edges],
        }
