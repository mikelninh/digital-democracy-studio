from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from safetrace.arms_monitor.build_monitor import build
from safetrace.arms_monitor.model import Event, SourceRef


SOURCE = SourceRef(
    id="official",
    url="https://example.test/official",
    title="Official source",
    publisher="Authority",
    checked_at="2026-07-23",
)


class ArmsMonitorTests(unittest.TestCase):
    def test_baseline_preserves_stage_distinctions(self) -> None:
        baseline = Path(__file__).parents[1] / "data/baseline.json"
        with tempfile.TemporaryDirectory() as directory:
            payload = build(baseline, Path(directory) / "monitor.json")
        self.assertEqual(payload["summary"]["verified_events"], 6)
        self.assertEqual(payload["summary"]["unresolved_questions"], 1)
        self.assertEqual(payload["summary"]["actual_deliveries_recorded"], 0)
        self.assertEqual(payload["summary"]["operational_use_records"], 0)
        export = next(event for event in payload["events"] if event["type"] == "export_authorisation")
        self.assertFalse(export["attributes"]["delivered"])
        planned = next(event for event in payload["events"] if event["type"] == "planned_delivery")
        self.assertEqual(planned["status"], "planned")

    def test_authorisation_cannot_claim_delivery(self) -> None:
        event = Event(
            id="event:test",
            type="export_authorisation",
            date="2026-01-01",
            title="Authorisation",
            evidence_state="verified_fact",
            source=SOURCE,
            attributes={"delivered": True},
        )
        with self.assertRaises(ValueError):
            event.validate()

    def test_planned_delivery_cannot_be_recorded_as_actual(self) -> None:
        event = Event(
            id="event:planned",
            type="planned_delivery",
            date="2030-01-01",
            title="Future delivery",
            evidence_state="verified_fact",
            source=SOURCE,
            status="recorded",
        )
        with self.assertRaises(ValueError):
            event.validate()


if __name__ == "__main__":
    unittest.main()
