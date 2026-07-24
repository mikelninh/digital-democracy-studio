from __future__ import annotations

import hashlib
import json
import os
import shutil
import tarfile
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .health import assess_check
from .model import (
    BackupEntry, BackupManifest, ObjectRef, SourceAlert, SourceCheck,
    Tombstone, TransformationManifest, VaultReceipt, as_plain, sha256_payload,
)
from .registry import SourceRegistry


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def normalize_payload(payload: bytes, content_type: str) -> bytes:
    if "html" not in content_type.lower() and "text" not in content_type.lower():
        return payload
    text = payload.decode("utf-8", errors="replace")
    return " ".join(text.split()).encode("utf-8")


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in value)


def atomic_write(path: Path, payload: bytes) -> None:
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


class EvidenceVault:
    def __init__(self, root: str | Path, registry: SourceRegistry):
        self.root = Path(root)
        self.registry = registry
        for name in ("objects/sha256", "receipts", "manifests", "checks", "alerts", "tombstones", "backups"):
            (self.root / name).mkdir(parents=True, exist_ok=True)

    def object_path(self, digest: str) -> Path:
        return self.root / "objects/sha256" / digest[:2] / digest[2:4] / digest

    def _write_object(self, payload: bytes, *, content_type: str, kind: str, sensitivity: str = "public") -> ObjectRef:
        digest = sha256_bytes(payload)
        path = self.object_path(digest)
        if path.exists():
            if sha256_bytes(path.read_bytes()) != digest:
                raise RuntimeError("Existing content-addressed object is corrupt")
        else:
            atomic_write(path, payload)
        ref = ObjectRef(digest, str(path.relative_to(self.root)), len(payload), content_type, kind, sensitivity)
        ref.validate()
        return ref

    def _receipt_path(self, receipt_id: str) -> Path:
        return self.root / "receipts" / f"{safe_name(receipt_id)}.json"

    def _manifest_path(self, manifest_id: str) -> Path:
        return self.root / "manifests" / f"{safe_name(manifest_id)}.json"

    def _load_receipt_payload(self, path: Path) -> VaultReceipt:
        raw = json.loads(path.read_text(encoding="utf-8"))
        obj = ObjectRef(**raw.pop("object"))
        return VaultReceipt(object=obj, **raw)

    def receipt(self, receipt_id: str) -> VaultReceipt:
        path = self._receipt_path(receipt_id)
        if not path.exists():
            raise KeyError(receipt_id)
        receipt = self._load_receipt_payload(path)
        receipt.validate()
        return receipt

    def receipts(self, source_id: str | None = None) -> list[VaultReceipt]:
        result=[]
        for path in sorted((self.root / "receipts").glob("*.json")):
            receipt=self._load_receipt_payload(path)
            if source_id is None or receipt.source_id==source_id:
                result.append(receipt)
        return sorted(result,key=lambda x:x.acquired_at)

    def latest_receipt(self, source_id: str) -> VaultReceipt | None:
        items=self.receipts(source_id)
        return items[-1] if items else None

    def acquire(self, source_id: str, payload: bytes, content_type: str, *, acquired_at: str | None = None, resolved_url: str | None = None, normalized_payload: bytes | None = None, metadata: dict[str, Any] | None = None) -> tuple[VaultReceipt, SourceAlert]:
        entry=self.registry.get(source_id)
        entry.validate()
        if not entry.enabled:
            raise ValueError("Source is disabled")
        if content_type not in entry.expected_content_types:
            raise ValueError(f"Unexpected content type for {source_id}: {content_type}")
        if not payload:
            raise ValueError("Cannot acquire empty source payload")
        acquired_at=acquired_at or utc_now()
        normalized_payload=normalized_payload if normalized_payload is not None else normalize_payload(payload,content_type)
        obj=self._write_object(payload,content_type=content_type,kind="original")
        normalized_hash=sha256_bytes(normalized_payload)
        previous=self.latest_receipt(source_id)
        changed=previous is not None and previous.object.sha256!=obj.sha256
        material=previous is not None and previous.normalized_sha256!=normalized_hash
        rid=f"receipt:{source_id}:{acquired_at}:{obj.sha256[:12]}"
        draft=VaultReceipt(rid,source_id,acquired_at,obj,normalized_hash,entry.connector_id,entry.connector_version,entry.parser_id,entry.parser_version,self.registry.revision(),changed,material,"0"*64,previous.receipt_id if previous else None,previous.receipt_hash if previous else None,resolved_url or entry.canonical_url,metadata or {})
        receipt=VaultReceipt(**{**draft.__dict__,"receipt_hash":draft.expected_hash()})
        receipt.validate()
        path=self._receipt_path(rid)
        encoded=json.dumps(as_plain(receipt),ensure_ascii=False,indent=2,sort_keys=True).encode()+b"\n"
        if path.exists():
            if path.read_bytes()!=encoded:
                raise RuntimeError("Receipt id collision or attempted overwrite")
        else:
            atomic_write(path,encoded)
        result="moved" if receipt.resolved_url!=entry.canonical_url else "available"
        check=SourceCheck(f"check:{rid}",source_id,acquired_at,result,entry.canonical_url,receipt.resolved_url,200,content_type,obj.sha256,normalized_hash,"Source acquired and stored with an immutable receipt.")
        self.record_check(check)
        alert=assess_check(entry,check,previous=previous,current=receipt)
        self.record_alert(alert)
        return receipt,alert

    def record_check(self, check: SourceCheck) -> None:
        check.validate()
        atomic_write(self.root/"checks"/f"{safe_name(check.check_id)}.json",json.dumps(asdict(check),ensure_ascii=False,indent=2,sort_keys=True).encode()+b"\n")

    def record_alert(self, alert: SourceAlert) -> None:
        alert.validate()
        atomic_write(self.root/"alerts"/f"{safe_name(alert.alert_id)}.json",json.dumps(asdict(alert),ensure_ascii=False,indent=2,sort_keys=True).encode()+b"\n")

    def record_unavailable(self, source_id: str, *, checked_at: str | None = None, message: str = "Source unavailable") -> SourceAlert:
        entry=self.registry.get(source_id)
        checked_at=checked_at or utc_now()
        check=SourceCheck(f"check:{source_id}:{checked_at}",source_id,checked_at,"unavailable",entry.canonical_url,None,None,None,None,None,message)
        self.record_check(check)
        alert=assess_check(entry,check)
        self.record_alert(alert)
        return alert

    def transform(self, *, operation: str, input_receipt_ids: Iterable[str], input_object_hashes: Iterable[str], outputs: Iterable[tuple[bytes,str,str,str]], tool_id: str, tool_version: str, created_at: str | None = None, parameters: dict[str,Any] | None = None, case_id: str | None = None, human_approved_by: str | None = None) -> TransformationManifest:
        receipt_ids=tuple(input_receipt_ids)
        object_hashes=tuple(input_object_hashes)
        for rid in receipt_ids:
            self.receipt(rid)
        for digest in object_hashes:
            if not self.object_path(digest).exists():
                raise ValueError(f"Unknown input object: {digest}")
        refs=tuple(self._write_object(payload,content_type=content_type,kind=kind,sensitivity=sensitivity) for payload,content_type,kind,sensitivity in outputs)
        created_at=created_at or utc_now()
        mid=f"manifest:{operation}:{created_at}:{sha256_payload([x.sha256 for x in refs])[:12]}"
        draft=TransformationManifest(mid,operation,created_at,tool_id,tool_version,receipt_ids,object_hashes,refs,parameters or {},"0"*64,case_id,human_approved_by)
        manifest=TransformationManifest(**{**draft.__dict__,"manifest_hash":draft.expected_hash()})
        manifest.validate()
        path=self._manifest_path(mid)
        encoded=json.dumps(as_plain(manifest),ensure_ascii=False,indent=2,sort_keys=True).encode()+b"\n"
        if path.exists():
            if path.read_bytes()!=encoded:
                raise RuntimeError("Manifest id collision or attempted overwrite")
        else:
            atomic_write(path,encoded)
        return manifest

    def _load_manifest(self,path:Path)->TransformationManifest:
        raw=json.loads(path.read_text())
        raw["input_receipt_ids"]=tuple(raw["input_receipt_ids"])
        raw["input_object_hashes"]=tuple(raw["input_object_hashes"])
        raw["outputs"]=tuple(ObjectRef(**x) for x in raw["outputs"])
        return TransformationManifest(**raw)

    def tombstones(self)->dict[str,Tombstone]:
        out={}
        for p in (self.root/"tombstones").glob("*.json"):
            t=Tombstone(**json.loads(p.read_text()))
            t.validate()
            out[t.object_hash]=t
        return out

    def delete_derived(self, digest: str, *, reason: str, approved_by: str, deleted_at: str | None = None) -> Tombstone:
        if any(r.object.sha256==digest for r in self.receipts()):
            raise ValueError("Original source objects cannot be deleted by v1.3")
        path=self.object_path(digest)
        if not path.exists():
            raise FileNotFoundError(digest)
        referenced=False
        for mp in (self.root/"manifests").glob("*.json"):
            manifest=self._load_manifest(mp)
            if any(o.sha256==digest for o in manifest.outputs):
                referenced=True
                break
        if not referenced:
            raise ValueError("Only derived objects recorded in a transformation manifest may be deleted")
        deleted_at=deleted_at or utc_now()
        draft={"tombstone_id":f"tombstone:{digest[:16]}:{deleted_at}","object_hash":digest,"object_key":str(path.relative_to(self.root)),"reason":reason,"approved_by":approved_by,"deleted_at":deleted_at}
        tomb=Tombstone(**draft,tombstone_hash=sha256_payload(draft))
        tomb.validate()
        path.unlink()
        atomic_write(self.root/"tombstones"/f"{tomb.tombstone_hash}.json",json.dumps(asdict(tomb),ensure_ascii=False,indent=2,sort_keys=True).encode()+b"\n")
        return tomb

    def verify_integrity(self) -> dict[str,Any]:
        errors=[]
        checked_objects=0
        checked_receipts=0
        checked_manifests=0
        tomb=self.tombstones()
        for p in (self.root/"objects/sha256").glob("*/*/*"):
            if p.is_file():
                checked_objects+=1
                if sha256_bytes(p.read_bytes())!=p.name:
                    errors.append(f"object_hash_mismatch:{p}")
        receipts={r.receipt_id:r for r in self.receipts()}
        for r in receipts.values():
            checked_receipts+=1
            if r.expected_hash()!=r.receipt_hash:
                errors.append(f"receipt_hash_mismatch:{r.receipt_id}")
            if r.previous_receipt_id:
                prev=receipts.get(r.previous_receipt_id)
                if not prev:
                    errors.append(f"missing_previous_receipt:{r.receipt_id}")
                elif prev.receipt_hash!=r.previous_receipt_hash:
                    errors.append(f"receipt_chain_mismatch:{r.receipt_id}")
            path=self.object_path(r.object.sha256)
            if not path.exists():
                errors.append(f"missing_original_object:{r.receipt_id}")
            elif sha256_bytes(path.read_bytes())!=r.object.sha256:
                errors.append(f"receipt_object_mismatch:{r.receipt_id}")
        for p in (self.root/"manifests").glob("*.json"):
            checked_manifests+=1
            try:
                m=self._load_manifest(p)
                m.validate()
            except Exception as exc:
                errors.append(f"invalid_manifest:{p.name}:{exc}")
                continue
            if m.expected_hash()!=m.manifest_hash:
                errors.append(f"manifest_hash_mismatch:{m.manifest_id}")
            for rid in m.input_receipt_ids:
                if rid not in receipts:
                    errors.append(f"manifest_missing_receipt:{m.manifest_id}:{rid}")
            for digest in m.input_object_hashes:
                if not self.object_path(digest).exists() and digest not in tomb:
                    errors.append(f"manifest_missing_input:{m.manifest_id}:{digest}")
            for out in m.outputs:
                path=self.object_path(out.sha256)
                if not path.exists() and out.sha256 not in tomb:
                    errors.append(f"manifest_missing_output:{m.manifest_id}:{out.sha256}")
                elif path.exists() and sha256_bytes(path.read_bytes())!=out.sha256:
                    errors.append(f"manifest_output_mismatch:{m.manifest_id}:{out.sha256}")
        return {"schema_version":"safetrace.vault-integrity/1.3","status":"pass" if not errors else "fail","objects_checked":checked_objects,"receipts_checked":checked_receipts,"manifests_checked":checked_manifests,"tombstones":len(tomb),"errors":errors}

    def plan_retention(self, *, as_of: str | None = None) -> list[dict[str, Any]]:
        now = datetime.fromisoformat((as_of or utc_now()).replace("Z", "+00:00"))
        receipts = {r.receipt_id: r for r in self.receipts()}
        plans: dict[str, dict[str, Any]] = {}
        for receipt in receipts.values():
            entry = self.registry.get(receipt.source_id)
            policy = self.registry.policy(entry.retention_policy_id)
            plans[receipt.object.sha256] = {"object_hash": receipt.object.sha256, "object_kind": "original", "source_id": receipt.source_id, "policy_id": policy.policy_id, "action": "retain", "reason": "Original evidence is retained; v1.3 never auto-deletes originals."}
        for path in (self.root / "manifests").glob("*.json"):
            manifest = self._load_manifest(path)
            source_ids = {receipts[rid].source_id for rid in manifest.input_receipt_ids if rid in receipts}
            for output in manifest.outputs:
                actions=[]
                for source_id in source_ids:
                    entry=self.registry.get(source_id)
                    policy=self.registry.policy(entry.retention_policy_id)
                    if policy.legal_hold or policy.minimum_days is None:
                        actions.append(("retain", policy.policy_id, "Policy retains the derived object or a legal hold applies."))
                    else:
                        age=(now-datetime.fromisoformat(manifest.created_at.replace("Z", "+00:00"))).days
                        action=policy.expiry_action if age>=policy.minimum_days else "retain"
                        actions.append((action,policy.policy_id,f"Derived object age is {age} days; minimum is {policy.minimum_days}."))
                action="retain" if any(a[0]=="retain" for a in actions) else (actions[0][0] if actions else "review")
                plans[output.sha256]={"object_hash":output.sha256,"object_kind":output.kind,"source_ids":sorted(source_ids),"policy_ids":sorted({a[1] for a in actions}),"action":action,"reason":" ".join(a[2] for a in actions) or "No source-specific policy resolved; human review required."}
        return [plans[key] for key in sorted(plans)]

    def _backup_entries(self)->tuple[BackupEntry,...]:
        entries=[]
        for path in sorted(self.root.rglob("*")):
            if path.is_file() and "backups" not in path.relative_to(self.root).parts:
                payload=path.read_bytes()
                entries.append(BackupEntry(str(path.relative_to(self.root)),sha256_bytes(payload),len(payload)))
        return tuple(entries)

    def create_backup(self, output: str|Path, *, created_at: str | None = None) -> BackupManifest:
        report=self.verify_integrity()
        if report["status"]!="pass":
            raise RuntimeError("Cannot back up a vault that fails integrity verification")
        created_at=created_at or utc_now()
        entries=self._backup_entries()
        unsigned={"backup_id":f"backup:{created_at}","created_at":created_at,"entries":[asdict(x) for x in entries],"schema_version":"safetrace.backup-manifest/1.3"}
        manifest=BackupManifest(unsigned["backup_id"],created_at,entries,sha256_payload(unsigned))
        manifest.validate()
        output=Path(output)
        output.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory() as d:
            md=Path(d)/"backup-manifest.json"
            md.write_text(json.dumps(as_plain(manifest),ensure_ascii=False,indent=2,sort_keys=True)+"\n")
            with tarfile.open(output,"w:gz") as tar:
                tar.add(md,arcname="backup-manifest.json")
                for entry in entries:
                    tar.add(self.root/entry.relative_path,arcname=f"vault/{entry.relative_path}")
        return manifest

    @staticmethod
    def restore_backup(archive: str|Path, destination: str|Path) -> BackupManifest:
        archive=Path(archive)
        destination=Path(destination)
        if destination.exists() and any(destination.iterdir()):
            raise ValueError("Restore destination must be empty")
        destination.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory() as d:
            tmp=Path(d)
            with tarfile.open(archive,"r:gz") as tar:
                for member in tar.getmembers():
                    resolved=(tmp/member.name).resolve()
                    if not str(resolved).startswith(str(tmp.resolve())):
                        raise ValueError("Unsafe backup path")
                tar.extractall(tmp,filter="data")
            raw=json.loads((tmp/"backup-manifest.json").read_text())
            raw["entries"]=tuple(BackupEntry(**x) for x in raw["entries"])
            manifest=BackupManifest(**raw)
            manifest.validate()
            if manifest.expected_hash()!=manifest.manifest_hash:
                raise ValueError("Backup manifest hash mismatch")
            for entry in manifest.entries:
                src=tmp/"vault"/entry.relative_path
                if not src.exists() or sha256_bytes(src.read_bytes())!=entry.sha256:
                    raise ValueError(f"Backup entry failed verification: {entry.relative_path}")
                dest=destination/entry.relative_path
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(src,dest)
        return manifest
