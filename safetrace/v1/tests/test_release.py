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
            "monitoring", "case_packs", "governance", "pilot",
        ]:
            (root / "safetrace" / component).mkdir(parents=True, exist_ok=True)
        governance = source_root / "governance/data/readiness.json"
        pilot = source_root / "pilot/data/synthetic_pilot.json"
        (root / "safetrace/governance/data").mkdir(parents=True, exist_ok=True)
        (root / "safetrace/pilot/data").mkdir(parents=True, exist_ok=True)
        (root / "safetrace/governance/data/readiness.json").write_text(
            governance.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (root / "safetrace/pilot/data/synthetic_pilot.json").write_text(
            pilot.read_text(encoding="utf-8"), encoding="utf-8"
        )

    def test_release_is_pilot_ready_but_not_live_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            status = validate_repository(root)
            self.assertTrue(status["release_ready"])
            self.assertFalse(status["live_partner_ready"])
            self.assertIn("not authorised", status["truthful_status"])

    def test_status_file_is_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            output = root / "status.json"
            write_release_status(root, output)
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8"))["release"],
                "v1.0-pilot-ready",
            )


if __name__ == "__main__":
    unittest.main()
