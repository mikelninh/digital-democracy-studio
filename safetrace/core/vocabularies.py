"""Controlled vocabularies for the SafeTrace v1.2 evidence model."""

from __future__ import annotations

SCHEMA_VERSION = "safetrace.core/1.2"
CONSTITUTION_REF = "safetrace/CONSTITUTION.md"
CONSTITUTION_VERSION = "1.0"

EVIDENCE_STATES = frozenset(
    {
        "verified_fact",
        "court_established",
        "official_allegation",
        "analytical_red_flag",
        "unresolved_gap",
        "corrected_or_disproved",
    }
)
EVIDENCE_ROLES = frozenset({"supporting", "contradicting", "context"})
EVIDENCE_ORIGINS = frozenset({"human", "ai_suggested", "imported_official_record"})

SOURCE_RANKS = frozenset(
    {
        "primary_official",
        "primary_firsthand",
        "authoritative_secondary",
        "reputable_secondary",
        "context_only",
    }
)
SOURCE_ACCESS_STATES = frozenset({"available", "moved", "unavailable", "restricted", "archived"})

DATA_ZONES = frozenset({"public", "sensitive_internal", "restricted_partner"})
FIELD_SENSITIVITIES = frozenset(
    {"public", "internal", "personal", "special_category", "victim_witness", "secret"}
)

CASE_STATUSES = frozenset({"draft", "triage", "accepted", "active", "paused", "closed", "rejected"})
CHARTER_STATUSES = frozenset({"draft", "accepted", "rejected", "paused"})

REVIEW_OUTCOMES = frozenset({"approved", "rejected", "needs_changes"})
LEGAL_REVIEW_STATES = frozenset({"not_required", "pending", "approved", "rejected"})
RIGHT_OF_REPLY_STATES = frozenset({"not_required", "pending", "completed", "declined", "not_contacted"})

PUBLICATION_STATUSES = frozenset({"draft", "approved", "published", "withdrawn"})
PUBLICATION_EDITIONS = frozenset({"internal", "public_redacted", "restricted_partner"})

LEGAL_STATUSES = frozenset(
    {
        "not_applicable",
        "announced",
        "draft",
        "proposed",
        "cabinet_approved",
        "parliamentary_stage",
        "enacted",
        "in_force",
        "suspended",
        "expired",
        "challenged",
        "investigation_open",
        "charged",
        "acquitted",
        "convicted",
        "appeal_pending",
        "final_judgment",
    }
)

ENTITY_TYPES = frozenset(
    {
        "person",
        "organisation",
        "political_party",
        "public_institution",
        "company",
        "association",
        "registry_entry",
        "policy_topic",
        "location",
        "other",
    }
)
RELATIONSHIP_TYPES = frozenset(
    {
        "donated_to",
        "registered_as",
        "declares_interest_in",
        "owns",
        "employed_by",
        "member_of",
        "met_with",
        "lobbied_on",
        "awarded_contract",
        "approved",
        "authorised",
        "paid",
        "benefited_from",
        "audited",
        "investigated",
        "ruled_on",
        "related_to",
    }
)
RELATIONSHIP_CONFIDENCE = frozenset({"confirmed", "high", "medium", "low", "possible_unconfirmed"})

EVENT_TYPES = frozenset(
    {
        "policy_or_budget_authority",
        "parliamentary_approval",
        "procurement_contract",
        "production_activity",
        "export_authorisation",
        "delivery",
        "planned_delivery",
        "operational_use",
        "donation",
        "lobby_registration",
        "meeting",
        "legislative_event",
        "court_event",
        "publication",
        "deadline",
        "source_change",
        "measure_effective",
        "other",
    }
)

SUBJECT_TYPES = frozenset({"case", "source", "entity", "relationship", "event", "claim", "publication"})
AGENT_TYPES = frozenset(
    {
        "scout",
        "archivist",
        "reader",
        "linker",
        "chronologist",
        "claim_compiler",
        "skeptic",
        "quant",
        "legal_status",
        "guardian",
        "watchtower",
        "explainer",
        "migration",
    }
)
AGENT_TASK_STATUSES = frozenset(
    {"queued", "running", "proposal_ready", "awaiting_human", "accepted", "rejected", "failed", "cancelled"}
)
FORBIDDEN_AGENT_TOOLS = frozenset(
    {
        "publish",
        "publish_publicly",
        "contact_subject",
        "impersonate",
        "refer_authority",
        "automated_referral",
        "identify_face",
        "credential_test",
        "hack",
    }
)

RISK_CATEGORIES = frozenset(
    {
        "privacy",
        "physical_safety",
        "reputational_harm",
        "legal",
        "source_integrity",
        "security",
        "bias",
        "misinterpretation",
        "conflict_sensitivity",
        "other",
    }
)
RISK_LEVELS = frozenset({"low", "medium", "high", "critical"})

BASELINE_PROHIBITED_METHODS = frozenset(
    {
        "hacking",
        "credential_testing",
        "impersonation",
        "doxxing",
        "covert_contact",
        "facial_identification",
        "automated_guilt",
        "automated_referral",
    }
)

LEGACY_EVIDENCE_STATE_MAP = {
    "verified_official_record": "verified_fact",
    "human_reviewed_match": "verified_fact",
    "verified_fact": "verified_fact",
    "court_established": "court_established",
    "official_allegation": "official_allegation",
    "analytical_red_flag": "analytical_red_flag",
    "unresolved_gap": "unresolved_gap",
    "corrected_or_disproved": "corrected_or_disproved",
}

LEGACY_NODE_TYPE_MAP = {
    "organisation": "organisation",
    "political_party": "political_party",
    "lobby_entry": "registry_entry",
    "policy_interest": "policy_topic",
}

DATA_ZONE_ORDER = {"public": 0, "sensitive_internal": 1, "restricted_partner": 2}
