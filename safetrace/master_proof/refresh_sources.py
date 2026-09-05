from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from connectors import SourceFetchError, connector_manifest, fetch_official_source

ROOT = Path(__file__).parent


def refresh_all(output_root: Path, *, retain_raw: bool = True) -> dict[str, Any]:
    """Fetch every allowlisted public source and produce a non-promoting evidence pack.

    A successful fetch creates a SHA-256 receipt. When `retain_raw` is true the
    exact public response bytes are stored under the CI artifact directory. No
    snapshot/claim is updated automatically; a failed or changed source remains
    a review signal rather than becoming current truth.
    """
    output_root.mkdir(parents=True, exist_ok=True)
    raw_dir = output_root / "raw"
    if retain_raw:
        raw_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for item in connector_manifest():
        source_id = item["source_id"]
        if item.get("requires_auth_or_special_access"):
            results.append({
                "source_id": source_id,
                "status": "skipped_access_required",
                "publisher": item["publisher"],
                "url": item["url"],
                "promoted": False,
            })
            continue
        try:
            receipt, body = fetch_official_source(source_id)
        except SourceFetchError as exc:
            results.append({
                "source_id": source_id,
                "status": "fetch_failed",
                "publisher": item["publisher"],
                "url": item["url"],
                "error": str(exc),
                "promoted": False,
            })
            continue

        raw_path: str | None = None
        if retain_raw:
            target = raw_dir / f"{source_id}.bin"
            target.write_bytes(body)
            raw_path = str(target.relative_to(output_root))
        results.append({
            "source_id": source_id,
            "status": "fetched",
            "publisher": item["publisher"],
            "url": item["url"],
            "receipt": receipt.to_dict(),
            "raw_artifact": raw_path,
            "promoted": False,
        })

    fetched = sum(1 for result in results if result["status"] == "fetched")
    failed = sum(1 for result in results if result["status"] == "fetch_failed")
    skipped = sum(1 for result in results if result["status"].startswith("skipped"))
    report = {
        "schema_version": "civicos.source-refresh/0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_count": len(results),
        "fetched": fetched,
        "failed": failed,
        "skipped": skipped,
        "promotion_policy": "never automatic",
        "human_review_required_for_snapshot_update": True,
        "results": results,
    }
    (output_root / "refresh-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "source-refresh")
    parser.add_argument("--no-raw", action="store_true")
    args = parser.parse_args()
    report = refresh_all(args.output, retain_raw=not args.no_raw)
    print(json.dumps({
        "status": "complete",
        "fetched": report["fetched"],
        "failed": report["failed"],
        "skipped": report["skipped"],
        "promotion_policy": report["promotion_policy"],
    }, indent=2))


if __name__ == "__main__":
    main()
