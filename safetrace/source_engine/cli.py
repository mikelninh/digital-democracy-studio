from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .engine import SnapshotStore, load_sources, snapshot_all


def main() -> None:
    parser = argparse.ArgumentParser(description="Snapshot SafeTrace official sources")
    parser.add_argument("--registry", type=Path, default=Path(__file__).parent / "data/sources.json")
    parser.add_argument("--output", type=Path, default=Path("artifacts/source-snapshots"))
    args = parser.parse_args()

    sources = load_sources(args.registry)
    receipts = snapshot_all(sources, SnapshotStore(args.output))
    print(json.dumps([asdict(item) for item in receipts], indent=2))


if __name__ == "__main__":
    main()
