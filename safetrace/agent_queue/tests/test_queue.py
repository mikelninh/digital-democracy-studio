from __future__ import annotations

import unittest

from safetrace.agent_queue.evaluation import run_golden_suite
from safetrace.agent_queue.model import AgentTaskSpec, SourceAnchor
from safetrace.agent_queue.queue import AgentQueue
from safetrace.agent_queue.workers import PROFILES

NOW = "2026-07-24T10:00:00+00:00"


def spec(
    agent: str = "claim_compiler",
    tools=None,
    zone: str = "public",
    budget: int = 10,
    timeout: int = 30,
) -> AgentTaskSpec:
    profile = PROFILES[agent]
    return AgentTaskSpec(
        f"task:{agent}",
        "case:test",
        "Create a bounded proposal for testing.",
        agent,
        tuple(tools if tools is not None else profile.allowed_tools),
        zone,
        "input/1",
        profile.output_schema,
        "deterministic-test",
        "prompt-v1",
        timeout,
        budget,
        "reviewer:test",
        ("fixture:1",),
        NOW,
    )


class QueueTests(unittest.TestCase):
    def test_unknown_and_forbidden_tools_are_denied(self) -> None:
        with self.assertRaisesRegex(ValueError, "prohibited tools"):
            AgentQueue().submit(spec("scout", ("publish_publicly",)))
        with self.assertRaisesRegex(ValueError, "unapproved tools"):
            AgentQueue().submit(spec("scout", ("read_database",)))

    def test_data_zone_budget_and_timeout_are_bounded(self) -> None:
        with self.assertRaisesRegex(ValueError, "data-zone ceiling"):
            AgentQueue().submit(spec("watchtower", zone="restricted_partner"))
        with self.assertRaisesRegex(ValueError, "budget"):
            AgentQueue().submit(spec("scout", budget=9999))
        with self.assertRaisesRegex(ValueError, "timeout"):
            AgentQueue().submit(spec("scout", timeout=9999))

    def test_output_is_proposal_only_and_traceable(self) -> None:
        queue = AgentQueue()
        task = spec()
        queue.submit(task)
        run = queue.start(task.id, {"x": 1}, NOW)
        anchors = (SourceAnchor("source:1", "page 1"),)
        proposal, receipt = queue.complete(
            run.id,
            {"claim": "Bounded claim", "attributed_to_current_government": False},
            anchors,
            tuple(task.allowed_tools),
            2,
            250,
            "2026-07-24T10:00:01+00:00",
        )
        self.assertEqual(proposal.status, "awaiting_human")
        self.assertEqual(queue.metrics()["auto_approved"], 0)
        self.assertEqual(receipt.model_id, task.model_id)
        self.assertTrue(receipt.trace_key)

    def test_agent_cannot_self_approve_or_publish(self) -> None:
        queue = AgentQueue()
        task = spec()
        queue.submit(task)
        run = queue.start(task.id, {"x": 1}, NOW)
        with self.assertRaisesRegex(ValueError, "mark its own output"):
            queue.complete(
                run.id,
                {"claim": "Unsafe", "publishable": True},
                (SourceAnchor("source:1", "page 1"),),
                tuple(task.allowed_tools),
                1,
                10,
                "2026-07-24T10:00:01+00:00",
            )

    def test_human_decision_rejects_agent_reviewer(self) -> None:
        queue = AgentQueue()
        task = spec()
        queue.submit(task)
        run = queue.start(task.id, {"x": 1}, NOW)
        proposal, _ = queue.complete(
            run.id,
            {"claim": "Bounded", "attributed_to_current_government": False},
            (SourceAnchor("source:1", "page 1"),),
            tuple(task.allowed_tools),
            1,
            10,
            "2026-07-24T10:00:01+00:00",
        )
        with self.assertRaisesRegex(ValueError, "Agent cannot act as human reviewer"):
            queue.decide(
                proposal.id,
                "agent:guardian",
                "accepted_for_review",
                "This rationale is sufficiently detailed.",
                NOW,
            )

    def test_golden_suite_blocks_regressions(self) -> None:
        report = run_golden_suite()
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["unsafe_accepted"], 0)
        self.assertEqual(report["passed"], report["total"])


if __name__ == "__main__":
    unittest.main()
