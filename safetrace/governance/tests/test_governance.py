from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path

from safetrace.governance.model import (
    AuditLog,
    Control,
    evaluate_readiness,
    is_authorized,
    load_governance,
)


class GovernanceTests(unittest.TestCase):
    @property
    def readiness_path(self) -> Path:
        return Path(__file__).parents[1] / "data/readiness.json"

    def test_rbac_is_default_deny(self) -> None:
        self.assertTrue(is_authorized("reviewer", "review_claim"))
        self.assertFalse(is_authorized("researcher", "approve_sensitive"))
        self.assertFalse(is_authorized("unknown", "read_public"))

    def test_audit_log_detects_tampering(self) -> None:
        log = AuditLog()
        first = log.append(
            event_id="evt-1",
            actor_role="reviewer",
            action="review_claim",
            resource_id="claim-1",
            outcome="approved",
            occurred_at="2026-07-24T10:00:00+00:00",
        )
        log.append(
            event_id="evt-2",
            actor_role="public_reader",
            action="read_public",
            resource_id="case-001",
            outcome="allowed",
            occurred_at="2026-07-24T10:01:00+00:00",
        )
        valid, errors = log.verify()
        self.assertTrue(valid, errors)
        log.events[0] = replace(first, outcome="changed-after-the-fact")
        valid, errors = log.verify()
        self.assertFalse(valid)
        self.assertIn("event[0] event hash mismatch", errors)

    def test_synthetic_pilot_is_ready_but_live_partner_is_blocked(self) -> None:
        controls, boundaries = load_governance(self.readiness_path)
        synthetic = evaluate_readiness(controls, boundaries["synthetic_evaluation"])
        restricted = evaluate_readiness(controls, boundaries["restricted_partner"])
        self.assertTrue(synthetic.ready, synthetic.blockers)
        self.assertFalse(restricted.ready)
        self.assertGreaterEqual(len(restricted.blockers), 4)

    def test_control_evidence_is_required(self) -> None:
        control = Control(
            id="X",
            domain="security",
            description="Example",
            status="implemented",
            required_for=["synthetic_evaluation"],
            owner_role="security_admin",
            evidence=[],
        )
        with self.assertRaises(ValueError):
            control.validate()


if __name__ == "__main__":
    unittest.main()
