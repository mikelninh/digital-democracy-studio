from __future__ import annotations

import argparse
import json
from pathlib import Path

from safetrace.law_fairness.model import build_public_assessment, load_case


def build(case_path: Path, output: Path) -> dict:
    case = load_case(case_path)
    payload = build_public_assessment(case)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the SafeTrace law fairness public assessment")
    parser.add_argument(
        "--case",
        type=Path,
        default=Path("safetrace/law_fairness/data/case_004.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("safetrace/law_fairness/public_status.json"),
    )
    args = parser.parse_args()
    build(args.case, args.output)


if __name__ == "__main__":
    main()
