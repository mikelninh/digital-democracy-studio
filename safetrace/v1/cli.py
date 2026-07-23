from __future__ import annotations

import argparse
from pathlib import Path

from safetrace.v1.release import write_release_status


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SafeTrace v1.0 pilot readiness")
    parser.add_argument("--root", type=Path, default=Path(__file__).parents[2])
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "status.json")
    args = parser.parse_args()
    payload = write_release_status(args.root, args.output)
    if not payload["release_ready"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
