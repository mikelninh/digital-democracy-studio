from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .model import RegistryEntry, RetentionPolicy, canonical_json
from .vocabularies import REGISTRY_SCHEMA_VERSION


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        Path(name).replace(path)
    finally:
        Path(name).unlink(missing_ok=True)


class SourceRegistry:
    def __init__(self, entries: Iterable[RegistryEntry], policies: Iterable[RetentionPolicy]):
        self.entries = list(entries)
        self.policies = list(policies)
        self.validate()

    def validate(self) -> None:
        ids: set[str] = set()
        policy_ids: set[str] = set()
        for policy in self.policies:
            policy.validate()
            if policy.policy_id in policy_ids:
                raise ValueError(f"Duplicate retention policy: {policy.policy_id}")
            policy_ids.add(policy.policy_id)
        if not policy_ids:
            raise ValueError("At least one retention policy is required")
        for entry in self.entries:
            entry.validate()
            if entry.source_id in ids:
                raise ValueError(f"Duplicate source id: {entry.source_id}")
            ids.add(entry.source_id)
            if entry.retention_policy_id not in policy_ids:
                raise ValueError(f"Unknown retention policy for source {entry.source_id}")

    def get(self, source_id: str) -> RegistryEntry:
        for entry in self.entries:
            if entry.source_id == source_id:
                return entry
        raise KeyError(source_id)

    def policy(self, policy_id: str) -> RetentionPolicy:
        for policy in self.policies:
            if policy.policy_id == policy_id:
                return policy
        raise KeyError(policy_id)

    def to_dict(self) -> dict:
        self.validate()
        return {
            "schema_version": REGISTRY_SCHEMA_VERSION,
            "policies": [asdict(item) for item in sorted(self.policies, key=lambda x: x.policy_id)],
            "sources": [asdict(item) for item in sorted(self.entries, key=lambda x: x.source_id)],
        }

    def revision(self) -> str:
        import hashlib
        return hashlib.sha256(canonical_json(self.to_dict())).hexdigest()

    def save(self, root: str | Path) -> str:
        root = Path(root)
        revision = self.revision()
        payload = json.dumps(self.to_dict(), ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        _atomic_write(root / "revisions" / f"{revision}.json", payload)
        _atomic_write(root / "current.json", payload)
        return revision

    @classmethod
    def load(cls, path: str | Path) -> "SourceRegistry":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("schema_version") != REGISTRY_SCHEMA_VERSION:
            raise ValueError("Unsupported Source Registry schema")
        entries = []
        for raw in payload.get("sources", []):
            data = dict(raw)
            data["expected_content_types"] = tuple(data.get("expected_content_types", []))
            entries.append(RegistryEntry(**data))
        policies = []
        for raw in payload.get("policies", []):
            data = dict(raw)
            data["applies_to"] = tuple(data.get("applies_to", []))
            policies.append(RetentionPolicy(**data))
        return cls(entries, policies)
