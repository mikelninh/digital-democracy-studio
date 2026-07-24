from __future__ import annotations

import dataclasses
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from safetrace.core.vocabularies import SOURCE_RANKS
from .vocabularies import *

_SHA = re.compile(r"^[0-9a-f]{64}$")


def _req(value: str, name: str, minimum: int = 1) -> None:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise ValueError(f"{name} is required")


def _enum(value: str, allowed, name: str) -> None:
    if value not in allowed:
        raise ValueError(f"Unsupported {name}: {value}")


def _time(value: str, name: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be ISO-8601") from exc


def _sha(value: str, name: str) -> None:
    if not isinstance(value, str) or not _SHA.fullmatch(value.lower()):
        raise ValueError(f"{name} must be a SHA-256 hex digest")


def canonical_json(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def as_plain(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {f.name: as_plain(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {str(k): as_plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [as_plain(v) for v in value]
    return value


@dataclass(frozen=True)
class RegistryEntry:
    source_id: str
    title: str
    publisher: str
    canonical_url: str
    source_type: str
    source_rank: str
    jurisdiction: str
    update_cadence: str
    connector_id: str
    connector_version: str
    parser_id: str
    parser_version: str
    expected_content_types: tuple[str, ...]
    retention_policy_id: str
    reviewed_by: str
    reviewed_at: str
    review_state: str = "approved"
    data_zone: str = "public"
    enabled: bool = True
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        for value, name in (
            (self.source_id, "Source id"), (self.title, "Source title"),
            (self.publisher, "Publisher"), (self.source_type, "Source type"),
            (self.jurisdiction, "Jurisdiction"), (self.connector_id, "Connector id"),
            (self.connector_version, "Connector version"), (self.parser_id, "Parser id"),
            (self.parser_version, "Parser version"), (self.retention_policy_id, "Retention policy id"),
            (self.reviewed_by, "Reviewer"),
        ):
            _req(value, name)
        if not self.canonical_url.startswith("https://"):
            raise ValueError("Registry canonical_url must use HTTPS")
        _enum(self.source_rank, SOURCE_RANKS, "source rank")
        _enum(self.update_cadence, UPDATE_CADENCES, "update cadence")
        _enum(self.review_state, REGISTRY_REVIEW_STATES, "registry review state")
        _enum(self.data_zone, DATA_ZONES, "registry data zone")
        _time(self.reviewed_at, "Registry reviewed_at")
        if self.review_state != "approved":
            raise ValueError("Acquisition registry entries must be human-approved")
        if self.data_zone != ALLOWED_ACQUISITION_ZONE:
            raise ValueError("v1.3 acquisition is restricted to reviewed public sources")
        if not self.expected_content_types:
            raise ValueError("Expected content types are required")


@dataclass(frozen=True)
class RetentionPolicy:
    policy_id: str
    name: str
    applies_to: tuple[str, ...]
    minimum_days: int | None
    expiry_action: str
    legal_hold: bool
    reviewed_by: str
    reviewed_at: str

    def validate(self) -> None:
        _req(self.policy_id, "Retention policy id")
        _req(self.name, "Retention policy name")
        _req(self.reviewed_by, "Retention reviewer")
        _time(self.reviewed_at, "Retention reviewed_at")
        _enum(self.expiry_action, RETENTION_ACTIONS, "retention action")
        if not self.applies_to:
            raise ValueError("Retention policy must apply to at least one object kind")
        for kind in self.applies_to:
            _enum(kind, OBJECT_KINDS, "object kind")
        if self.minimum_days is not None and self.minimum_days < 0:
            raise ValueError("minimum_days cannot be negative")
        if "original" in self.applies_to and self.expiry_action == "delete_derived":
            raise ValueError("Original source objects cannot use delete_derived")


@dataclass(frozen=True)
class ObjectRef:
    sha256: str
    object_key: str
    byte_length: int
    content_type: str
    kind: str
    sensitivity: str = "public"

    def validate(self) -> None:
        _sha(self.sha256, "Object hash")
        _req(self.object_key, "Object key")
        if not isinstance(self.byte_length, int) or self.byte_length < 0:
            raise ValueError("Object byte_length must be non-negative")
        _req(self.content_type, "Object content type")
        _enum(self.kind, OBJECT_KINDS, "object kind")
        _enum(self.sensitivity, FIELD_SENSITIVITIES, "object sensitivity")


@dataclass(frozen=True)
class VaultReceipt:
    receipt_id: str
    source_id: str
    acquired_at: str
    object: ObjectRef
    normalized_sha256: str
    connector_id: str
    connector_version: str
    parser_id: str
    parser_version: str
    registry_revision: str
    changed: bool
    material_changed: bool
    receipt_hash: str
    previous_receipt_id: str | None = None
    previous_receipt_hash: str | None = None
    resolved_url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: str = RECEIPT_SCHEMA_VERSION

    def validate(self) -> None:
        _req(self.receipt_id, "Receipt id")
        _req(self.source_id, "Receipt source id")
        _time(self.acquired_at, "Receipt acquired_at")
        self.object.validate()
        if self.object.kind != "original":
            raise ValueError("Vault receipts must point to original source objects")
        _sha(self.normalized_sha256, "Normalized hash")
        _sha(self.registry_revision, "Registry revision")
        _sha(self.receipt_hash, "Receipt hash")
        for value, name in (
            (self.connector_id, "Connector id"), (self.connector_version, "Connector version"),
            (self.parser_id, "Parser id"), (self.parser_version, "Parser version"),
        ):
            _req(value, name)
        if bool(self.previous_receipt_id) != bool(self.previous_receipt_hash):
            raise ValueError("Previous receipt id and hash must appear together")
        if self.previous_receipt_hash:
            _sha(self.previous_receipt_hash, "Previous receipt hash")
        if self.schema_version != RECEIPT_SCHEMA_VERSION:
            raise ValueError("Unexpected receipt schema version")

    def unsigned_payload(self) -> dict[str, Any]:
        payload = as_plain(self)
        payload.pop("receipt_hash", None)
        return payload

    def expected_hash(self) -> str:
        return sha256_payload(self.unsigned_payload())


@dataclass(frozen=True)
class TransformationManifest:
    manifest_id: str
    operation: str
    created_at: str
    tool_id: str
    tool_version: str
    input_receipt_ids: tuple[str, ...]
    input_object_hashes: tuple[str, ...]
    outputs: tuple[ObjectRef, ...]
    parameters: dict[str, Any]
    manifest_hash: str
    case_id: str | None = None
    human_approved_by: str | None = None
    schema_version: str = MANIFEST_SCHEMA_VERSION

    def validate(self) -> None:
        _req(self.manifest_id, "Manifest id")
        _enum(self.operation, TRANSFORM_OPERATIONS, "transformation operation")
        _time(self.created_at, "Manifest created_at")
        _req(self.tool_id, "Tool id")
        _req(self.tool_version, "Tool version")
        if not self.input_receipt_ids and not self.input_object_hashes:
            raise ValueError("Transformation requires at least one input")
        if not self.outputs:
            raise ValueError("Transformation requires at least one output")
        for value in self.input_object_hashes:
            _sha(value, "Input object hash")
        for output in self.outputs:
            output.validate()
            if output.kind == "original":
                raise ValueError("Transformations cannot create original objects")
        if self.operation in {"redact", "export"} and not self.human_approved_by:
            raise ValueError("Redaction and export manifests require human approval")
        _sha(self.manifest_hash, "Manifest hash")
        if self.schema_version != MANIFEST_SCHEMA_VERSION:
            raise ValueError("Unexpected transformation schema version")

    def unsigned_payload(self) -> dict[str, Any]:
        payload = as_plain(self)
        payload.pop("manifest_hash", None)
        return payload

    def expected_hash(self) -> str:
        return sha256_payload(self.unsigned_payload())


@dataclass(frozen=True)
class SourceCheck:
    check_id: str
    source_id: str
    checked_at: str
    result: str
    requested_url: str
    resolved_url: str | None
    http_status: int | None
    content_type: str | None
    raw_sha256: str | None
    normalized_sha256: str | None
    message: str

    def validate(self) -> None:
        _req(self.check_id, "Check id")
        _req(self.source_id, "Check source id")
        _time(self.checked_at, "Check checked_at")
        _enum(self.result, CHECK_RESULTS, "check result")
        if not self.requested_url.startswith("https://"):
            raise ValueError("Check requested_url must use HTTPS")
        if self.raw_sha256:
            _sha(self.raw_sha256, "Check raw hash")
        if self.normalized_sha256:
            _sha(self.normalized_sha256, "Check normalized hash")
        _req(self.message, "Check message")


@dataclass(frozen=True)
class SourceAlert:
    alert_id: str
    source_id: str
    created_at: str
    kind: str
    severity: str
    summary: str
    check_id: str
    receipt_id: str | None = None
    public_effect: str = "none_until_human_review"

    def validate(self) -> None:
        _req(self.alert_id, "Alert id")
        _req(self.source_id, "Alert source id")
        _time(self.created_at, "Alert created_at")
        _enum(self.kind, ALERT_KINDS, "alert kind")
        _enum(self.severity, ALERT_SEVERITIES, "alert severity")
        _req(self.summary, "Alert summary")
        _req(self.check_id, "Alert check id")
        if self.public_effect != "none_until_human_review":
            raise ValueError("Source alerts cannot directly change public status")


@dataclass(frozen=True)
class Tombstone:
    tombstone_id: str
    object_hash: str
    object_key: str
    reason: str
    approved_by: str
    deleted_at: str
    tombstone_hash: str

    def validate(self) -> None:
        _req(self.tombstone_id, "Tombstone id")
        _sha(self.object_hash, "Tombstone object hash")
        _req(self.object_key, "Tombstone object key")
        _req(self.reason, "Deletion reason", 10)
        _req(self.approved_by, "Deletion approver")
        _time(self.deleted_at, "Deletion timestamp")
        _sha(self.tombstone_hash, "Tombstone hash")


@dataclass(frozen=True)
class BackupEntry:
    relative_path: str
    sha256: str
    byte_length: int

    def validate(self) -> None:
        _req(self.relative_path, "Backup path")
        _sha(self.sha256, "Backup hash")
        if self.byte_length < 0:
            raise ValueError("Backup size cannot be negative")


@dataclass(frozen=True)
class BackupManifest:
    backup_id: str
    created_at: str
    entries: tuple[BackupEntry, ...]
    manifest_hash: str
    schema_version: str = BACKUP_SCHEMA_VERSION

    def validate(self) -> None:
        _req(self.backup_id, "Backup id")
        _time(self.created_at, "Backup created_at")
        if not self.entries:
            raise ValueError("Backup manifest cannot be empty")
        for entry in self.entries:
            entry.validate()
        _sha(self.manifest_hash, "Backup manifest hash")
        if self.schema_version != BACKUP_SCHEMA_VERSION:
            raise ValueError("Unexpected backup schema version")

    def unsigned_payload(self) -> dict[str, Any]:
        payload = as_plain(self)
        payload.pop("manifest_hash", None)
        return payload

    def expected_hash(self) -> str:
        return sha256_payload(self.unsigned_payload())
