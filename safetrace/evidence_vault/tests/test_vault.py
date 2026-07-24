from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from safetrace.evidence_vault.bootstrap import collect_existing_sources
from safetrace.evidence_vault.contracts import document as contracts_document, serialised as contracts_serialised
from safetrace.evidence_vault.health import assess_check
from safetrace.evidence_vault.model import RegistryEntry, RetentionPolicy, SourceCheck
from safetrace.evidence_vault.registry import SourceRegistry
from safetrace.evidence_vault.vault import EvidenceVault

NOW="2026-07-24T02:00:00+00:00"


def registry() -> SourceRegistry:
    entry=RegistryEntry(
        "source:test","Test official source","Test Authority","https://example.org/source","official_record","primary_official","Germany","daily",
        "reviewed-http","1.3","html-parser","1.0",("text/html",),"retain-public-originals","editor",NOW,
    )
    policy=RetentionPolicy("retain-public-originals","Retain public sources",("original","normalized","parsed","extraction","redacted","export"),None,"retain",False,"editor",NOW)
    return SourceRegistry([entry],[policy])


class ContractTests(unittest.TestCase):
    def test_committed_contracts_match_generator(self):
        path=Path(__file__).parents[1]/"schemas/evidence-vault-contracts-1.3.json"
        self.assertEqual(path.read_text(),contracts_serialised())
        self.assertEqual(json.loads(path.read_text()),contracts_document())


class RegistryTests(unittest.TestCase):
    def test_requires_reviewed_public_source(self):
        valid=registry()
        self.assertEqual(valid.get("source:test").review_state,"approved")
        bad=RegistryEntry(**{**valid.entries[0].__dict__,"review_state":"draft"})
        self.assertRaisesRegex(ValueError,"human-approved",SourceRegistry,[bad],valid.policies)
        bad=RegistryEntry(**{**valid.entries[0].__dict__,"data_zone":"sensitive_internal"})
        self.assertRaisesRegex(ValueError,"reviewed public sources",SourceRegistry,[bad],valid.policies)

    def test_revision_and_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            r=registry()
            revision=r.save(d)
            loaded=SourceRegistry.load(Path(d)/"current.json")
            self.assertEqual(revision,loaded.revision())
            self.assertTrue((Path(d)/"revisions"/f"{revision}.json").exists())


class VaultTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.registry=registry()
        self.vault=EvidenceVault(self.root/"vault",self.registry)

    def tearDown(self):
        self.temp.cleanup()

    def test_content_addressed_receipt_chain_and_material_change(self):
        first,alert=self.vault.acquire("source:test",b"<p>Hello world</p>","text/html",acquired_at=NOW)
        self.assertEqual(alert.kind,"no_change")
        self.assertFalse(first.changed)
        self.assertEqual(first.receipt_hash,first.expected_hash())
        same,_=self.vault.acquire("source:test",b"<p>Hello world</p>","text/html",acquired_at="2026-07-24T03:00:00+00:00")
        self.assertFalse(same.changed)
        self.assertEqual(same.previous_receipt_hash,first.receipt_hash)
        changed,alert=self.vault.acquire("source:test",b"<p>Hello brave world</p>","text/html",acquired_at="2026-07-24T04:00:00+00:00")
        self.assertTrue(changed.changed)
        self.assertTrue(changed.material_changed)
        self.assertEqual(alert.kind,"material_change")
        self.assertEqual(self.vault.verify_integrity()["status"],"pass")

    def test_receipt_tampering_is_detected(self):
        receipt,_=self.vault.acquire("source:test",b"evidence","text/html",acquired_at=NOW)
        path=self.vault._receipt_path(receipt.receipt_id)
        raw=json.loads(path.read_text())
        raw["metadata"]={"tampered":True}
        path.write_text(json.dumps(raw))
        report=self.vault.verify_integrity()
        self.assertEqual(report["status"],"fail")
        self.assertTrue(any("receipt_hash_mismatch" in x for x in report["errors"]))

    def test_transform_requires_approval_for_redaction(self):
        receipt,_=self.vault.acquire("source:test",b"Original text","text/html",acquired_at=NOW)
        with self.assertRaisesRegex(ValueError,"human approval"):
            self.vault.transform(operation="redact",input_receipt_ids=(receipt.receipt_id,),input_object_hashes=(receipt.object.sha256,),outputs=((b"Redacted","text/plain","redacted","public"),),tool_id="redactor",tool_version="1",created_at=NOW)
        manifest=self.vault.transform(operation="redact",input_receipt_ids=(receipt.receipt_id,),input_object_hashes=(receipt.object.sha256,),outputs=((b"Redacted","text/plain","redacted","public"),),tool_id="redactor",tool_version="1",created_at="2026-07-24T03:00:00+00:00",human_approved_by="editor")
        self.assertEqual(manifest.manifest_hash,manifest.expected_hash())
        self.assertEqual(self.vault.verify_integrity()["status"],"pass")

    def test_deletion_is_tombstoned_and_original_is_protected(self):
        receipt,_=self.vault.acquire("source:test",b"Original","text/html",acquired_at=NOW)
        manifest=self.vault.transform(operation="parse",input_receipt_ids=(receipt.receipt_id,),input_object_hashes=(receipt.object.sha256,),outputs=((b"Parsed","application/json","parsed","public"),),tool_id="parser",tool_version="1",created_at="2026-07-24T03:00:00+00:00")
        with self.assertRaisesRegex(ValueError,"Original source objects"):
            self.vault.delete_derived(receipt.object.sha256,reason="Should not delete original",approved_by="editor")
        tomb=self.vault.delete_derived(manifest.outputs[0].sha256,reason="Derived test artifact expired after documented review.",approved_by="editor",deleted_at="2026-07-24T04:00:00+00:00")
        self.assertFalse(self.vault.object_path(tomb.object_hash).exists())
        self.assertEqual(self.vault.verify_integrity()["status"],"pass")

    def test_backup_restore_verifies_every_entry(self):
        self.vault.acquire("source:test",b"Backup evidence","text/html",acquired_at=NOW)
        archive=self.root/"backup.tar.gz"
        manifest=self.vault.create_backup(archive,created_at="2026-07-24T05:00:00+00:00")
        restored=self.root/"restored"
        loaded=EvidenceVault.restore_backup(archive,restored)
        self.assertEqual(manifest.manifest_hash,loaded.manifest_hash)
        restored_vault=EvidenceVault(restored,self.registry)
        self.assertEqual(restored_vault.verify_integrity()["status"],"pass")

    def test_retention_plan_never_auto_deletes_originals(self):
        receipt,_=self.vault.acquire("source:test",b"Retention evidence","text/html",acquired_at=NOW)
        manifest=self.vault.transform(operation="parse",input_receipt_ids=(receipt.receipt_id,),input_object_hashes=(receipt.object.sha256,),outputs=((b"Derived","text/plain","parsed","public"),),tool_id="parser",tool_version="1",created_at="2026-07-24T03:00:00+00:00")
        plan={item["object_hash"]:item for item in self.vault.plan_retention(as_of="2026-08-24T00:00:00+00:00")}
        self.assertEqual(plan[receipt.object.sha256]["action"],"retain")
        self.assertEqual(plan[manifest.outputs[0].sha256]["action"],"retain")

    def test_unavailable_moved_and_content_type_alerts(self):
        unavailable=self.vault.record_unavailable("source:test",checked_at=NOW)
        self.assertEqual(unavailable.kind,"source_unavailable")
        entry=self.registry.get("source:test")
        check=SourceCheck("check:moved","source:test",NOW,"moved",entry.canonical_url,"https://example.org/new",301,"text/html",None,None,"Permanent redirect")
        self.assertEqual(assess_check(entry,check).kind,"source_moved")
        check=SourceCheck("check:type","source:test",NOW,"available",entry.canonical_url,entry.canonical_url,200,"application/pdf",None,None,"Unexpected response")
        self.assertEqual(assess_check(entry,check).kind,"content_type_mismatch")


class ExistingSourceBootstrap(unittest.TestCase):
    def test_existing_case_sources_bootstrap(self):
        root=Path(__file__).parents[2]
        if not (root/"source_engine").exists():
            self.skipTest("legacy SafeTrace modules absent")
        r=collect_existing_sources(root)
        self.assertGreaterEqual(len(r.entries),10)
        self.assertEqual(len({x.source_id for x in r.entries}),len(r.entries))
        self.assertTrue(all(x.review_state=="approved" for x in r.entries))

if __name__=="__main__":unittest.main()
