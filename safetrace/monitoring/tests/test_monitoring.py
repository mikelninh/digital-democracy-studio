from __future__ import annotations

import unittest
from datetime import date

from safetrace.monitoring.model import SnapshotState, compare_snapshots, deadline_proposal


def snapshot(source_id: str, raw: str, normalised: str, checked: str) -> SnapshotState:
    return SnapshotState(
        source_id=source_id,
        canonical_url="https://example.test/official",
        checked_at=checked,
        raw_sha256=raw * 64,
        normalized_sha256=normalised * 64,
        parser_version="parser/1",
    )


class MonitoringTests(unittest.TestCase):
    def test_normalised_change_requires_human_review(self) -> None:
        proposal = compare_snapshots(
            snapshot("source", "a", "a", "2026-07-20"),
            snapshot("source", "b", "b", "2026-07-23"),
            created_at="2026-07-23T12:00:00Z",
        )
        self.assertEqual(proposal.review_state, "pending_review")
        self.assertFalse(proposal.can_change_public_status())

    def test_raw_html_noise_can_be_no_material_change(self) -> None:
        proposal = compare_snapshots(
            snapshot("source", "a", "c", "2026-07-20"),
            snapshot("source", "b", "c", "2026-07-23"),
            created_at="2026-07-23T12:00:00Z",
        )
        self.assertEqual(proposal.kind, "no_change")
        self.assertEqual(proposal.review_state, "not_required")

    def test_passed_unresolved_deadline_creates_pending_alert(self) -> None:
        proposal = deadline_proposal(
            item_id="greco-progress-report-2026",
            source_id="greco-germany-fifth-round-page",
            deadline=date(2026, 3, 31),
            checked_on=date(2026, 7, 23),
            unresolved=True,
            source_url="https://www.coe.int/en/web/greco/evaluations/germany",
            careful_interpretation="No newer public report does not prove that Germany failed to submit one.",
        )
        self.assertIsNotNone(proposal)
        assert proposal is not None
        self.assertEqual(proposal.kind, "deadline_passed_unresolved")
        self.assertFalse(proposal.can_change_public_status())


if __name__ == "__main__":
    unittest.main()
