from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from .model import AccountabilityCase, Event, SourceRef


def build(baseline_path: Path, output_path: Path) -> dict:
    raw = json.loads(baseline_path.read_text(encoding="utf-8"))
    sources = {key: SourceRef(**value) for key, value in raw["sources"].items()}
    events = []
    for item in raw["events"]:
        source_key = item.pop("source_key")
        events.append(Event(source=sources[source_key], **item))
    case = AccountabilityCase(
        events=events,
        unresolved_questions=raw["unresolved_questions"],
        **raw["case"],
    )
    payload = case.to_dict()
    payload["summary"] = {
        "events_by_type": dict(Counter(event.type for event in events)),
        "verified_events": sum(event.evidence_state == "verified_fact" for event in events),
        "unresolved_questions": len(case.unresolved_questions),
        "actual_deliveries_recorded": sum(event.type == "delivery" for event in events),
        "operational_use_records": sum(event.type == "operational_use" for event in events),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, default=Path(__file__).parent / "data/baseline.json")
    parser.add_argument("--output", type=Path, default=Path("artifacts/arms-monitor/baseline.json"))
    args = parser.parse_args()
    build(args.baseline, args.output)


if __name__ == "__main__":
    main()
