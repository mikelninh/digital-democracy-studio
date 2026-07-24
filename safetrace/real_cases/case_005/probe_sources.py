from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from .build_case import USER_AGENT, normalize_text


def main() -> int:
    root = Path(__file__).parent
    config = json.loads((root / "sources.json").read_text(encoding="utf-8"))
    failures: list[str] = []
    for source in config["sources"]:
        source_id = source["source_id"]
        url = source["canonical_url"]
        print(f"PROBE_START {source_id} {url}", flush=True)
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
                "Accept-Language": "de-DE,de;q=0.9,en;q=0.6",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                payload = response.read()
                content_type = response.headers.get_content_type() or "application/octet-stream"
                resolved = response.geturl()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            failures.append(f"{source_id}:fetch:{type(exc).__name__}:{exc}")
            print(f"PROBE_FAIL {failures[-1]}", flush=True)
            continue
        text = normalize_text(payload).casefold()
        missing = [
            marker for marker in source["required_markers"]
            if re.sub(r"\s+", " ", marker).casefold() not in text
        ]
        print(
            f"PROBE_RESPONSE {source_id} status=200 content_type={content_type} bytes={len(payload)} resolved={resolved}",
            flush=True,
        )
        if content_type != "text/html":
            failures.append(f"{source_id}:content_type:{content_type}")
            print(f"PROBE_FAIL {failures[-1]}", flush=True)
        elif missing:
            failures.append(f"{source_id}:missing_markers:{missing}")
            print(f"PROBE_FAIL {failures[-1]}", flush=True)
        else:
            print(f"PROBE_PASS {source_id} markers={len(source['required_markers'])}", flush=True)
    if failures:
        print("PROBE_SUMMARY FAIL", flush=True)
        for failure in failures:
            print(f" - {failure}", flush=True)
        return 2
    print("PROBE_SUMMARY PASS sources=4", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
