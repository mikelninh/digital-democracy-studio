SCHEMA_VERSION = "safetrace.investigation-desk/1.6"

ROLES = frozenset({
    "intake_researcher", "investigator", "evidence_manager",
    "reviewer", "legal_reviewer", "publisher", "admin",
})
VIEWS = frozenset({
    "inbox", "cases", "sources", "claims", "graph", "timeline",
    "review", "publish", "corrections", "agents", "audit",
})
CASE_STATUSES = frozenset({"draft", "triage", "active", "paused", "closed", "rejected"})
TASK_STATUSES = frozenset({"open", "in_progress", "blocked", "done", "cancelled"})
REVIEW_STATES = frozenset({"draft", "pending", "approved", "rejected", "needs_changes"})
PUBLICATION_STATES = frozenset({"draft", "requested", "approved", "published", "stale", "withdrawn"})
RECORD_KINDS = frozenset({
    "source", "claim", "entity", "relationship", "event", "agent_proposal",
})
DATA_ZONES = frozenset({"public", "sensitive_internal"})

ACTIONS = frozenset({
    "create_case", "accept_case", "reject_case", "pause_case", "close_case",
    "add_source", "add_claim", "add_entity", "add_relationship", "add_event",
    "assign_task", "comment", "submit_review", "decide_review",
    "queue_agent_proposal", "accept_agent_proposal_for_review", "reject_agent_proposal",
    "request_publication", "approve_publication", "publish", "correct_publication",
    "view_audit", "export_public",
})

ROLE_PERMISSIONS = {
    "intake_researcher": frozenset({"create_case", "add_source", "comment", "assign_task"}),
    "investigator": frozenset({
        "create_case", "accept_case", "pause_case", "close_case", "add_source",
        "add_claim", "add_entity", "add_relationship", "add_event", "assign_task",
        "comment", "submit_review", "queue_agent_proposal",
        "accept_agent_proposal_for_review", "reject_agent_proposal", "request_publication",
    }),
    "evidence_manager": frozenset({"add_source", "comment", "assign_task", "submit_review"}),
    "reviewer": frozenset({"comment", "decide_review", "reject_agent_proposal"}),
    "legal_reviewer": frozenset({"comment", "decide_review"}),
    "publisher": frozenset({
        "comment", "approve_publication", "publish", "correct_publication", "export_public",
    }),
    "admin": ACTIONS,
}

ROLE_VIEWS = {
    "intake_researcher": frozenset({"inbox", "cases", "sources"}),
    "investigator": VIEWS - {"audit"},
    "evidence_manager": frozenset({"cases", "sources", "claims", "timeline", "review", "agents"}),
    "reviewer": frozenset({"cases", "sources", "claims", "graph", "timeline", "review", "corrections"}),
    "legal_reviewer": frozenset({"cases", "sources", "claims", "timeline", "review", "corrections"}),
    "publisher": frozenset({"cases", "claims", "review", "publish", "corrections"}),
    "admin": VIEWS,
}
