SCHEMA_VERSION = "safetrace.agent-queue/1.5"

TASK_STATUSES = frozenset({
    "queued", "running", "proposal_ready", "awaiting_human",
    "accepted_for_review", "rejected", "needs_changes", "failed", "cancelled",
})
RUN_STATUSES = frozenset({"running", "completed", "failed", "cancelled"})
PROPOSAL_STATUSES = frozenset({"awaiting_human", "accepted_for_review", "rejected", "needs_changes"})
DECISION_OUTCOMES = frozenset({"accepted_for_review", "rejected", "needs_changes"})

FORBIDDEN_OUTPUT_KEYS = frozenset({
    "publish", "publish_publicly", "contact_subject", "refer_authority",
    "automated_referral", "guilt_score", "suspect_list", "facial_identity",
})
FORBIDDEN_OUTPUT_INTENTS = frozenset({
    "publish", "contact_subject", "refer_authority", "accuse_person",
    "identify_face", "automated_guilt",
})
ANCHOR_REQUIRED_AGENTS = frozenset({
    "reader", "linker", "chronologist", "claim_compiler", "skeptic",
    "quant", "legal_status", "watchtower", "explainer",
})
