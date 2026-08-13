from __future__ import annotations

import difflib
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WT = ROOT / "zero-suffering-intelligence" / "watchtower"
SOURCES_FILE = WT / "sources.json"
SNAPSHOT_DIR = WT / "snapshots"
STATUS_FILE = WT / "status.json"
CLAIM_STATUS_FILE = WT / "claim-review-status.json"

USER_AGENT = "ZeroSufferingIntelligence-Watchtower/0.8 (+https://github.com/mikelninh/digital-democracy-studio)"
MAX_DIFF_LINES = 80


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            text = data.strip()
            if text:
                self.parts.append(text)


def normalise_html(raw: bytes, charset: str = "utf-8") -> str:
    text = raw.decode(charset, errors="replace")
    parser = VisibleTextParser()
    parser.feed(text)
    visible = "\n".join(parser.parts)
    visible = re.sub(r"[ \t]+", " ", visible)
    visible = re.sub(r"\n{2,}", "\n", visible)
    return visible.strip()


def fetch_text(url: str) -> tuple[str, dict]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=35) as response:
        raw = response.read()
        content_type = response.headers.get_content_type()
        charset = response.headers.get_content_charset() or "utf-8"
        if content_type in {"text/html", "application/xhtml+xml"}:
            text = normalise_html(raw, charset)
        else:
            text = raw.decode(charset, errors="replace")
            text = re.sub(r"[ \t]+", " ", text).strip()
        meta = {
            "http_status": getattr(response, "status", 200),
            "content_type": content_type,
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
        }
        return text, meta


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def diff_summary(old: str, new: str) -> list[str]:
    if not old:
        return []
    lines = list(
        difflib.unified_diff(
            old.splitlines(),
            new.splitlines(),
            fromfile="previous",
            tofile="current",
            lineterm="",
            n=1,
        )
    )
    return lines[:MAX_DIFF_LINES]


def main() -> int:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    WT.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    registry = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    source_results: list[dict] = []
    claim_review: dict[str, dict] = {}

    for source in registry.get("sources", []):
        source_id = source["source_id"]
        snapshot_path = SNAPSHOT_DIR / f"{source_id}.txt"
        previous = snapshot_path.read_text(encoding="utf-8") if snapshot_path.exists() else ""
        previous_hash = sha256_text(previous) if previous else None

        result = {
            "source_id": source_id,
            "title": source["title"],
            "category": source["category"],
            "url": source["url"],
            "checked_at": now,
            "claim_ids": source.get("claim_ids", []),
            "previous_sha256": previous_hash,
        }

        try:
            current, meta = fetch_text(source["url"])
            current_hash = sha256_text(current)
            baseline = not snapshot_path.exists()
            changed = (not baseline) and (previous_hash != current_hash)

            result.update(meta)
            result["sha256"] = current_hash
            result["status"] = "baseline_created" if baseline else ("changed" if changed else "unchanged")
            result["diff"] = diff_summary(previous, current) if changed else []
            result["character_count"] = len(current)

            snapshot_path.write_text(current + "\n", encoding="utf-8")

            if changed:
                for claim_id in source.get("claim_ids", []):
                    claim_review[claim_id] = {
                        "status": "needs_review",
                        "reason": f"Source changed: {source_id}",
                        "source_id": source_id,
                        "detected_at": now,
                    }
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
            result["status"] = "fetch_failed"
            result["error"] = f"{type(exc).__name__}: {exc}"
        except Exception as exc:  # keep one broken source from aborting the whole watchtower
            result["status"] = "fetch_failed"
            result["error"] = f"{type(exc).__name__}: {exc}"

        source_results.append(result)

    summary = {
        "schema": "zsi.watchtower/status-0.8",
        "generated_at": now,
        "sources_total": len(source_results),
        "unchanged": sum(r["status"] == "unchanged" for r in source_results),
        "changed": sum(r["status"] == "changed" for r in source_results),
        "baselines_created": sum(r["status"] == "baseline_created" for r in source_results),
        "fetch_failed": sum(r["status"] == "fetch_failed" for r in source_results),
        "claims_needing_review": sorted(claim_review),
        "sources": source_results,
    }
    STATUS_FILE.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CLAIM_STATUS_FILE.write_text(
        json.dumps(
            {
                "schema": "zsi.watchtower/claim-review-status-0.8",
                "generated_at": now,
                "claims": claim_review,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps({k: summary[k] for k in ["sources_total", "unchanged", "changed", "baselines_created", "fetch_failed", "claims_needing_review"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
