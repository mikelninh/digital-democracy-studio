from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .bootstrap import build_bootstrap_report
from .model import RegistryEntry, RetentionPolicy
from .registry import SourceRegistry
from .vault import EvidenceVault

NOW="2026-07-24T02:00:00+00:00"


def demo_registry() -> SourceRegistry:
    entry=RegistryEntry("synthetic:vault-demo","Synthetic Evidence Vault fixture","SafeTrace test suite","https://example.org/safetrace-vault-demo","synthetic_fixture","context_only","Test","manual","fixture-connector","1.3","fixture-parser","1.0",("text/html",),"retain-demo","SafeTrace CI",NOW)
    policy=RetentionPolicy("retain-demo","Retain synthetic release fixture",("original","normalized","parsed","extraction","redacted","export"),None,"retain",False,"SafeTrace CI",NOW)
    return SourceRegistry([entry],[policy])


def build(safetrace_root: Path, output_root: Path) -> dict:
    registry_root=output_root/"registry"
    report=build_bootstrap_report(safetrace_root,registry_root)
    demo_root=output_root/"demo-vault"
    if demo_root.exists():
        shutil.rmtree(demo_root)
    registry=demo_registry()
    vault=EvidenceVault(demo_root,registry)
    first,_=vault.acquire("synthetic:vault-demo",b"<p>Version one</p>","text/html",acquired_at=NOW)
    second,alert=vault.acquire("synthetic:vault-demo",b"<p>Version two</p>","text/html",acquired_at="2026-07-24T03:00:00+00:00")
    manifest=vault.transform(operation="parse",input_receipt_ids=(second.receipt_id,),input_object_hashes=(second.object.sha256,),outputs=((b'{"version":2}',"application/json","parsed","public"),),tool_id="fixture-parser",tool_version="1.0",created_at="2026-07-24T03:05:00+00:00")
    integrity=vault.verify_integrity()
    backup=output_root/"evidence-vault-backup.tar.gz"
    backup_manifest=vault.create_backup(backup,created_at="2026-07-24T04:00:00+00:00")
    restored=output_root/"restored-vault"
    if restored.exists():
        shutil.rmtree(restored)
    EvidenceVault.restore_backup(backup,restored)
    restored_integrity=EvidenceVault(restored,registry).verify_integrity()
    result={"schema_version":"safetrace.evidence-vault-release/1.3","status":"pass" if report["status"]=="pass" and integrity["status"]=="pass" and restored_integrity["status"]=="pass" and alert.kind=="material_change" else "fail","registry":report,"demo":{"receipts":2,"receipt_chain_verified":second.previous_receipt_hash==first.receipt_hash,"material_change_alert":alert.kind,"transformation_manifest":manifest.manifest_id,"integrity":integrity,"backup_manifest_hash":backup_manifest.manifest_hash,"restore_integrity":restored_integrity,"retention_plan":vault.plan_retention(as_of="2026-07-25T00:00:00+00:00")},"truthful_boundary":"Synthetic vault fixture and reviewed public source registry only; no real victim or restricted partner evidence."}
    output_root.mkdir(parents=True,exist_ok=True)
    (output_root/"release-report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--safetrace-root",type=Path,default=Path("safetrace"))
    p.add_argument("--output-root",type=Path,default=Path("safetrace/evidence_vault/artifacts"))
    a=p.parse_args()
    result=build(a.safetrace_root,a.output_root)
    print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))
    return 0 if result["status"]=="pass" else 2
if __name__=="__main__":raise SystemExit(main())
