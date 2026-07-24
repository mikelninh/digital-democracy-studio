from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

USER_AGENT = "SafeTrace-Policy-Source-Monitor/0.2 (+https://mikelninh.github.io/digital-democracy-studio/safetrace/)"


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)


def normalize_html(payload: bytes) -> str:
    parser = TextExtractor()
    parser.feed(payload.decode("utf-8", errors="replace"))
    text = html.unescape(" ".join(parser.parts)).replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip()


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fetch(url: str, attempts: int = 3, timeout: int = 35) -> tuple[bytes, str]:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
                    "Accept-Language": "de-DE,de;q=0.9,en;q=0.5",
                },
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                content_type = response.headers.get_content_type() or "application/octet-stream"
                if content_type not in {"text/html", "application/xhtml+xml"}:
                    raise ValueError(f"unexpected content type {content_type}")
                return response.read(), response.geturl()
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"could not acquire {url}: {last_error}")


@dataclass
class SourceResult:
    source_id: str
    publisher: str
    canonical_url: str
    resolved_url: str | None
    status: str
    object_hash: str | None
    byte_length: int | None
    marker_count: int
    missing_markers: list[str]
    error: str | None


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_source_catalog(registry: dict[str, Any], catalog: dict[str, Any]) -> list[str]:
    catalog_sources = {item["source_id"]: item for item in catalog.get("sources", [])}
    errors: list[str] = []
    for item in registry.get("sources", []):
        current = catalog_sources.get(item.get("source_id"))
        if current is None:
            errors.append(f"registry source missing from catalog: {item.get('source_id')}")
        elif current.get("url") != item.get("url"):
            errors.append(f"URL mismatch for {item.get('source_id')}")
    return errors


def build_review_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# SafeTrace official-source review candidate",
        "",
        f"Run: `{report['run_id']}`",
        f"Created: {report['created_at']}",
        f"Overall status: **{report['status']}**",
        "",
        "This monitor never publishes changes. A named human must inspect originals, markers and any changed hashes.",
        "",
        "## Sources",
        "",
    ]
    for source in report["sources"]:
        icon = "✅" if source["status"] == "verified" else "⚠️"
        lines.extend(
            [
                f"### {icon} {source['source_id']}",
                f"- Publisher: {source['publisher']}",
                f"- Status: `{source['status']}`",
                f"- SHA-256: `{source.get('object_hash') or 'unavailable'}`",
                f"- Missing markers: {', '.join(source.get('missing_markers', [])) or 'none'}",
                f"- Error: {source.get('error') or 'none'}",
                "",
            ]
        )
    lines.extend(
        [
            "## Named human review",
            "",
            "- [ ] Each official page opens and matches its publisher",
            "- [ ] Every required passage is present or the source rule is deliberately revised",
            "- [ ] Material content changes are explained",
            "- [ ] Forecasts, observations and targets remain distinct",
            "- [ ] Candidate values are not published without a reviewed catalog diff",
            "- [ ] Correction/history entry is prepared before publication",
            "",
        ]
    )
    return "\n".join(lines)


def run(root: Path, output: Path, fixture_dir: Path | None = None) -> dict[str, Any]:
    registry = load_json(root / "policy_platform" / "source_registry.json")
    catalog_path = root / "open_policy_api" / "v1" / "catalog.json"
    catalog = load_json(catalog_path)
    run_time = datetime.now(timezone.utc)
    run_id = run_time.strftime("%Y%m%dT%H%M%SZ")
    output.mkdir(parents=True, exist_ok=True)
    source_dir = output / "sources"
    receipt_dir = output / "receipts"
    source_dir.mkdir(exist_ok=True)
    receipt_dir.mkdir(exist_ok=True)

    config_errors = compare_source_catalog(registry, catalog)
    source_results: list[SourceResult] = []

    for source in registry.get("sources", []):
        source_id = source["source_id"]
        try:
            if fixture_dir is not None:
                payload = (fixture_dir / f"{source_id}.html").read_bytes()
                resolved_url = source["url"]
            else:
                payload, resolved_url = fetch(source["url"])
            text = normalize_html(payload)
            folded = text.casefold()
            missing = [marker for marker in source.get("required_markers", []) if marker.casefold() not in folded]
            object_hash = sha256(payload)
            (source_dir / f"{source_id}.html").write_bytes(payload)
            receipt = {
                "schema_version": "safetrace.source-monitor-receipt/1.0",
                "source_id": source_id,
                "publisher": source["publisher"],
                "canonical_url": source["url"],
                "resolved_url": resolved_url,
                "acquired_at": run_time.isoformat(),
                "object_hash": object_hash,
                "byte_length": len(payload),
                "required_markers": source.get("required_markers", []),
                "missing_markers": missing,
            }
            (receipt_dir / f"{source_id}.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            source_results.append(
                SourceResult(
                    source_id=source_id,
                    publisher=source["publisher"],
                    canonical_url=source["url"],
                    resolved_url=resolved_url,
                    status="verified" if not missing else "material_change_requires_review",
                    object_hash=object_hash,
                    byte_length=len(payload),
                    marker_count=len(source.get("required_markers", [])),
                    missing_markers=missing,
                    error=None,
                )
            )
        except Exception as exc:
            source_results.append(
                SourceResult(
                    source_id=source_id,
                    publisher=source["publisher"],
                    canonical_url=source["url"],
                    resolved_url=None,
                    status="acquisition_failed",
                    object_hash=None,
                    byte_length=None,
                    marker_count=len(source.get("required_markers", [])),
                    missing_markers=[],
                    error=str(exc),
                )
            )

    changed = [item for item in source_results if item.status != "verified"]
    report = {
        "schema_version": "safetrace.source-monitor-report/1.0",
        "run_id": run_id,
        "created_at": run_time.isoformat(),
        "status": "review_required" if changed or config_errors else "verified_no_material_marker_change",
        "publication_allowed": False,
        "catalog_sha256": sha256(catalog_path.read_bytes()),
        "config_errors": config_errors,
        "counts": {
            "sources": len(source_results),
            "verified": sum(item.status == "verified" for item in source_results),
            "review_required": len(changed),
        },
        "sources": [item.__dict__ for item in source_results],
        "boundaries": {
            "no_automatic_publication": True,
            "known_url_monitor_not_latest_release_discovery": True,
            "named_human_review_required": True,
            "original_bytes_retained_in_run_artifact": True,
        },
    }
    (output / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "review.md").write_text(build_review_markdown(report), encoding="utf-8")
    (output / "github-output.txt").write_text(
        f"review_required={'true' if report['status'] == 'review_required' else 'false'}\n"
        f"verified={report['counts']['verified']}\n"
        f"source_count={report['counts']['sources']}\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("safetrace"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixture-dir", type=Path)
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()
    report = run(args.root, args.output, args.fixture_dir)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_review and report["status"] == "review_required":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
