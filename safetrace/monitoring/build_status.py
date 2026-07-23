from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .model import deadline_proposal


def build(config_path: Path, output_path: Path) -> dict:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    proposals = []
    for item in config.get("deadline_monitors", []):
        proposal = deadline_proposal(
            item_id=item["id"],
            source_id=item["id"],
            deadline=date.fromisoformat(item["deadline"]),
            checked_on=date.fromisoformat(item["last_manual_check"]),
            unresolved="unresolved" in item["state"],
            source_url=item["source_url"],
            careful_interpretation=item["careful_interpretation"],
        )
        if proposal:
            proposals.append(proposal.to_dict())
    payload = {
        "schema_version": "safetrace.monitor-status/0.7",
        "configured_at": config["configured_at"],
        "cadence": config["cadence"],
        "source_count": len(config["sources"]),
        "sources": config["sources"],
        "proposals": proposals,
        "public_change_count": sum(item["can_change_public_status"] for item in proposals),
        "publication_rule": config["publication_rule"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path(__file__).parent / "data/monitors.json")
    parser.add_argument("--output", type=Path, default=Path("artifacts/monitoring/status.json"))
    args = parser.parse_args()
    build(args.config, args.output)


if __name__ == "__main__":
    main()
