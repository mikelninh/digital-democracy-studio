from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from safetrace.v1.release import validate_repository, write_release_status


class ReleaseTests(unittest.TestCase):
    def _make_repository(self, root: Path) -> None:
        source_root = Path(__file__).parents[2]
        for component in [
            "source_engine", "political_money", "review_desk", "arms_monitor",
            "monitoring", "case_packs", "governance", "pilot", "law_fairness", "core", "evidence_vault",
        ]:
            (root / "safetrace" / component).mkdir(parents=True, exist_ok=True)
        governance = source_root / "governance/data/readiness.json"
        pilot = source_root / "pilot/data/synthetic_pilot.json"
        core_schema = source_root / "core/schemas/safetrace-core-1.2.schema.json"
        vault_contracts = source_root / "evidence_vault/schemas/evidence-vault-contracts-1.3.json"
        (root / "safetrace/governance/data").mkdir(parents=True, exist_ok=True)
        (root / "safetrace/pilot/data").mkdir(parents=True, exist_ok=True)
        (root / "safetrace/core/schemas").mkdir(parents=True, exist_ok=True)
        (root / "safetrace/evidence_vault/schemas").mkdir(parents=True, exist_ok=True)
        (root / "safetrace/evidence_vault/artifacts").mkdir(parents=True, exist_ok=True)
        (root / "safetrace/governance/data/readiness.json").write_text(governance.read_text(encoding="utf-8"), encoding="utf-8")
        (root / "safetrace/pilot/data/synthetic_pilot.json").write_text(pilot.read_text(encoding="utf-8"), encoding="utf-8")
        (root / "safetrace/core/schemas/safetrace-core-1.2.schema.json").write_text(core_schema.read_text(encoding="utf-8"), encoding="utf-8")
        (root / "safetrace/evidence_vault/schemas/evidence-vault-contracts-1.3.json").write_text(vault_contracts.read_text(encoding="utf-8"), encoding="utf-8")
        (root / "safetrace/core/migration-report.json").write_text(
            json.dumps({"status":"pass","target_schema":"safetrace.core/1.2","cases":{case_id:{} for case_id in ("case-001","case-002","case-003","case-004")}}), encoding="utf-8"
        )
        (root / "safetrace/evidence_vault/artifacts/release-report.json").write_text(
            json.dumps({
                "status":"pass",
                "registry":{"status":"pass","sources":20,"minimum_expected_sources":10},
                "demo":{
                    "receipt_chain_verified":True,
                    "material_change_alert":"material_change",
                    "integrity":{"status":"pass"},
                    "restore_integrity":{"status":"pass"},
                },
            }), encoding="utf-8"
        )

    def test_release_is_ready_but_not_live_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self._make_repository(root)
            status=validate_repository(root)
            self.assertTrue(status["release_ready"])
            self.assertFalse(status["live_partner_ready"])
            self.assertTrue(status["components"]["evidence_vault"])
            self.assertEqual(status["evidence_vault"]["release_evidence"]["status"],"pass")
            self.assertIn("not authorised",status["truthful_status"])

    def test_missing_or_failed_vault_report_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self._make_repository(root)
            report=root/"safetrace/evidence_vault/artifacts/release-report.json"
            report.unlink()
            self.assertFalse(validate_repository(root)["release_ready"])
            report.write_text(json.dumps({"status":"fail"}),encoding="utf-8")
            self.assertFalse(validate_repository(root)["release_ready"])

    def test_status_file_is_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self._make_repository(root)
            output=root/"status.json"
            write_release_status(root,output)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["release"],"v1.3-reviewed-source-registry-and-evidence-vault")


if __name__ == "__main__":
    unittest.main()
