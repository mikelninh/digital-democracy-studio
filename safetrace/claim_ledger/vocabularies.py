SCHEMA_VERSION="safetrace.claim-ledger/1.4"
CLAIM_STATUSES=frozenset({"draft","review","publishable","published","corrected","withdrawn","migrated_pending_evidence_backfill"})
EVIDENCE_ROLES=frozenset({"supporting","contradicting","context"})
PROVENANCE_MODES=frozenset({"vault_receipt","legacy_reference"})
REVIEW_GATES=frozenset({"identity","evidence","red_team","legal","right_of_reply","publication","correction"})
TASK_STATUSES=frozenset({"pending","approved","rejected","needs_changes","waived"})
PUBLICATION_STATUSES=frozenset({"draft","published","stale","withdrawn"})
CORRECTION_TYPES=frozenset({"factual","attribution","context","source","wording","withdrawal"})
