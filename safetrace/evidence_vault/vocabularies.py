from __future__ import annotations

SCHEMA_VERSION = "safetrace.evidence-vault/1.3"
REGISTRY_SCHEMA_VERSION = "safetrace.source-registry/1.3"
RECEIPT_SCHEMA_VERSION = "safetrace.vault-receipt/1.3"
MANIFEST_SCHEMA_VERSION = "safetrace.transformation-manifest/1.3"
BACKUP_SCHEMA_VERSION = "safetrace.backup-manifest/1.3"
INTEGRITY_SCHEMA_VERSION = "safetrace.vault-integrity/1.3"

REGISTRY_REVIEW_STATES = frozenset({"draft", "approved", "rejected"})
UPDATE_CADENCES = frozenset({"hourly", "daily", "weekly", "monthly", "quarterly", "annual", "manual"})
SOURCE_HEALTH_STATES = frozenset({"healthy", "moved", "unavailable", "error", "content_type_mismatch", "not_checked"})
CHECK_RESULTS = frozenset({"available", "moved", "unavailable", "error"})
ALERT_KINDS = frozenset({"no_change", "material_change", "source_moved", "source_unavailable", "fetch_error", "content_type_mismatch"})
ALERT_SEVERITIES = frozenset({"info", "warning", "high"})
OBJECT_KINDS = frozenset({"original", "normalized", "parsed", "extraction", "redacted", "export"})
TRANSFORM_OPERATIONS = frozenset({"normalize", "parse", "extract", "redact", "export"})
RETENTION_ACTIONS = frozenset({"retain", "review", "delete_derived"})
DATA_ZONES = frozenset({"public", "sensitive_internal"})
FIELD_SENSITIVITIES = frozenset({"public", "internal", "personal", "special_category", "victim_witness", "secret"})

# v1.3 deliberately accepts only reviewed public-source acquisition.
ALLOWED_ACQUISITION_ZONE = "public"
