from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from safetrace.intelligence_casework.live_evidence import acquire_live_uksl


def main() -> int:
    p = argparse.ArgumentParser(description="Acquire the live FCDO UK Sanctions List, preserve it in the Evidence Vault, and return analyst-review candidates.")
    p.add_argument("--query", required=True)
    p.add_argument("--dob")
    p.add_argument("--nationality")
    p.add_argument("--vault", type=Path, default=Path("artifacts/intelligence-casework/live-vault"))
    p.add_argument("--output", type=Path, default=Path("artifacts/intelligence-casework/live-screening.json"))
    args = p.parse_args()
    reviewed_at = datetime.now(timezone.utc).isoformat()
    result = acquire_live_uksl(query=args.query, dob=args.dob, nationality=args.nationality, vault_root=args.vault, reviewed_at=reviewed_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS: live authoritative sanctions source acquired and screened")
    print("  source sha256:", result["source"]["object_sha256"])
    print("  receipt hash:", result["source"]["receipt_hash"])
    print("  records parsed:", result["records_parsed"])
    print("  candidates:", result["candidate_count"])
    print("  identity decision:", result["identity_decision"])
    for item in result["candidates"][:3]:
        print(f"  candidate: {item['unique_id']} | {item['name']} | score={item['name_score']:.4f} | status={item['identity_status']} | conflicts={','.join(item['identifier_conflicts']) or 'none'} | support={','.join(item['identifier_support']) or 'none'}")
    if result["integrity"]["status"] != "pass":
        print("FAIL: evidence vault integrity check failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
