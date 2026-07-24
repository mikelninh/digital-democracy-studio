from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluation import run_golden_suite
from .model import AgentTaskSpec, SourceAnchor
from .queue import AgentQueue
from .workers import PROFILES

NOW = "2026-07-24T09:00:00+00:00"


def safe_output(agent_type: str) -> dict:
    base = {
        "proposal_kind": agent_type,
        "summary": f"Bounded synthetic {agent_type} proposal.",
    }
    if agent_type == "linker":
        base["entity_links"] = [
            {
                "left": "Entity A",
                "right": "Entity A",
                "match_state": "candidate",
                "independent_identifiers": ["register id", "official name"],
            }
        ]
    elif agent_type == "claim_compiler":
        base.update(
            {
                "claim": "A bounded synthetic claim.",
                "policy_origin": "current_record",
                "attributed_to_current_government": False,
            }
        )
    elif agent_type == "skeptic":
        base.update({"known_contradiction": False, "contradictions": []})
    elif agent_type == "legal_status":
        base.update({"source_stage": "announced", "status": "announced"})
    elif agent_type == "guardian":
        base.update({"safety_result": "pass", "blocked_intents": []})
    return base


def build(output_root: Path) -> dict:
    queue = AgentQueue()
    runs = []
    for index, (agent_type, profile) in enumerate(sorted(PROFILES.items())):
        spec = AgentTaskSpec(
            f"task:release:{agent_type}",
            "case:synthetic-agent-queue",
            f"Produce a bounded synthetic proposal for the {agent_type} worker.",
            agent_type,
            tuple(sorted(profile.allowed_tools)),
            "public",
            "safetrace.agent.input/1",
            profile.output_schema,
            "deterministic-release-worker",
            "release-v1",
            60,
            min(50, profile.max_budget_cents),
            "reviewer:release",
            (f"fixture:{agent_type}",),
            NOW,
        )
        queue.submit(spec)
        run = queue.start(
            spec.id,
            {"agent_type": agent_type, "fixture": index},
            NOW,
        )
        anchors = (
            ()
            if agent_type in {"scout", "archivist", "guardian"}
            else (
                SourceAnchor(
                    "source:synthetic",
                    "fixture paragraph",
                    "receipt:synthetic",
                    "a" * 64,
                ),
            )
        )
        proposal, receipt = queue.complete(
            run.id,
            safe_output(agent_type),
            anchors,
            tuple(sorted(profile.allowed_tools)),
            1,
            100 + index,
            "2026-07-24T09:00:01+00:00",
        )
        runs.append(
            {
                "agent_type": agent_type,
                "proposal_status": proposal.status,
                "trace_key": receipt.trace_key,
                "input_hash": receipt.input_hash,
                "output_hash": receipt.output_hash,
            }
        )

    evaluation = run_golden_suite()
    metrics = queue.metrics()
    traceable = all(
        item["trace_key"] and item["input_hash"] and item["output_hash"]
        for item in runs
    )
    result = {
        "schema_version": "safetrace.agent-queue-release/1.5",
        "status": (
            "pass"
            if len(runs) == 12
            and traceable
            and metrics["auto_approved"] == 0
            and metrics["awaiting_human"] == 12
            and evaluation["status"] == "pass"
            and evaluation["unsafe_accepted"] == 0
            else "fail"
        ),
        "workers": {"implemented": sorted(PROFILES), "count": len(PROFILES)},
        "synthetic_runs": runs,
        "metrics": metrics,
        "evaluation": evaluation,
        "boundaries": {
            "proposal_only": True,
            "autonomous_publication": False,
            "autonomous_contact": False,
            "autonomous_referral": False,
            "restricted_partner_data": False,
        },
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "release-report.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("safetrace/agent_queue/artifacts"),
    )
    args = parser.parse_args()
    result = build(args.output_root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
