from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from safetrace.case_packs.generate_case_pack import build_pack, make_pdf, validate_pack


class CasePackTests(unittest.TestCase):
    @property
    def data_dir(self) -> Path:
        return Path(__file__).parents[2] / "source_engine/data"

    def test_case_001_has_complete_reviewed_findings(self) -> None:
        pack = build_pack(self.data_dir, generated_at="2026-07-23T21:33:00+00:00")
        self.assertEqual(len(pack["findings"]), 14)
        self.assertEqual(
            (
                pack["executive_summary"]["implemented_satisfactorily"],
                pack["executive_summary"]["partly_implemented"],
                pack["executive_summary"]["not_implemented"],
            ),
            (4, 6, 4),
        )
        self.assertTrue(all(item["source_anchor"] for item in pack["findings"]))
        self.assertTrue(all(item["evidence_state"] == "verified_fact" for item in pack["findings"]))

    def test_public_redacted_pack_rejects_sensitive_data_flags(self) -> None:
        pack = build_pack(self.data_dir)
        pack["redaction_profile"]["private_addresses_included"] = True
        with self.assertRaises(ValueError):
            validate_pack(pack)

    def test_pdf_and_json_ready_pack_can_be_generated(self) -> None:
        pack = build_pack(self.data_dir)
        with tempfile.TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "case-001.pdf"
            make_pdf(pack, pdf_path)
            self.assertTrue(pdf_path.exists())
            self.assertGreater(pdf_path.stat().st_size, 5_000)
            self.assertTrue(pdf_path.read_bytes().startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
