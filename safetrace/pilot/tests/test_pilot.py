from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from safetrace.pilot.model import evaluate_pilot, load_pilot
from safetrace.pilot.run_pilot import build_public_report


class PilotTests(unittest.TestCase):
    @property
    def pilot_path(self) -> Path:
        return Path(__file__).parents[1] / "data/synthetic_pilot.json"

    def test_synthetic_fixture_passes_but_is_not_real_world_validated(self) -> None:
        pilot = load_pilot(self.pilot_path)
        result = evaluate_pilot(pilot)
        self.assertEqual(result.decision, "GO_SYNTHETIC")
        self.assertFalse(result.real_world_validated)
        self.assertEqual(result.passed_gates, result.total_gates)

    def test_false_link_blocks_the_pilot(self) -> None:
        pilot = load_pilot(self.pilot_path)
        changed = replace(pilot, metrics=replace(pilot.metrics, false_entity_links=1))
        result = evaluate_pilot(changed)
        self.assertEqual(result.decision, "NO_GO_LIVE")
        self.assertFalse(next(item for item in result.gates if item.id == "false_links").passed)

    def test_public_report_is_explicitly_synthetic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = build_public_report(self.pilot_path, Path(directory))
            status = json.loads((Path(directory) / "status.json").read_text(encoding="utf-8"))
            page = (Path(directory) / "index.html").read_text(encoding="utf-8")
            self.assertEqual(payload, status)
            self.assertFalse(status["pilot"]["real_world_validation"])
            self.assertIn("synthetic benchmark", page.lower())


if __name__ == "__main__":
    unittest.main()
