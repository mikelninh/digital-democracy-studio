from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.parse import urlparse

from safetrace.intelligence_casework import company_live_resilient as resilient
from safetrace.intelligence_casework.company_live import MAX_SOURCE_BYTES, fetch_source as direct_fetch

RETRYABLE_HTTP = {429, 500, 502, 503, 504}


def fetch_with_retry(
    url: str,
    allowed_hosts: set[str],
    *,
    timeout: int = 25,
    attempts: int = 3,
    base_fetch: Callable[..., tuple[bytes, str, str]] = direct_fetch,
    sleeper: Callable[[float], None] = time.sleep,
) -> tuple[bytes, str, str]:
    """Retry transient public-source failures; never retry explicit access denials."""
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            return base_fetch(url, allowed_hosts, timeout=timeout)
        except HTTPError as exc:
            last = exc
            if exc.code not in RETRYABLE_HTTP or attempt == attempts - 1:
                raise
            sleeper(float(2**attempt))
        except (TimeoutError, ConnectionError) as exc:
            last = exc
            if attempt == attempts - 1:
                raise
            sleeper(float(2**attempt))
    assert last is not None
    raise last


def browser_fetch(url: str, allowed_hosts: set[str], *, timeout: int = 25) -> tuple[bytes, str, str]:
    """Render explicitly approved client-side public pages. This is not used to bypass HTTP 403 sources."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in allowed_hosts:
        raise ValueError(f"URL is outside reviewed HTTPS allowlist: {url}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - deployment dependency check
        raise RuntimeError("browser acquisition requested but Playwright is not installed") from exc

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(
                user_agent="SafeTrace-Research-Browser/2.3 (+public-evidence-acquisition)",
                viewport={"width": 1365, "height": 900},
            )
            response = page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
            if response and response.status >= 400:
                raise HTTPError(url, response.status, f"Browser HTTP {response.status}", hdrs=None, fp=None)
            try:
                page.wait_for_load_state("networkidle", timeout=min(timeout, 10) * 1000)
            except Exception:
                # Some sites keep analytics/network connections open; DOM content remains usable.
                pass
            page.wait_for_timeout(500)
            final_url = page.url
            final = urlparse(final_url)
            if final.scheme != "https" or final.hostname not in allowed_hosts:
                raise ValueError(f"browser redirect escaped reviewed allowlist: {final_url}")
            payload = page.content().encode("utf-8")
            if not payload or len(payload) > MAX_SOURCE_BYTES:
                raise ValueError(f"browser-rendered source size invalid: {url}")
            return payload, "text/html", final_url
        finally:
            browser.close()


def canonicalize_address(value: str) -> str:
    """Collapse presentation differences without erasing substantive address components."""
    text = re.sub(r"\s+", " ", value).strip(" ,.;")
    text = text.replace("Kirchstr.", "Kirchstraße").replace("Kirchstrasse", "Kirchstraße")
    text = re.sub(r",?\s*Germany$", "", text, flags=re.IGNORECASE).strip(" ,")
    text = re.sub(r"\s*•\s*", " ", text)
    text = re.sub(r"\s*,\s*", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+(\d{5}\s+Berlin)$", r", \1", text)
    return text


def build_production_fetch(case: dict[str, Any]) -> Callable[..., tuple[bytes, str, str]]:
    browser_hosts = {
        (urlparse(source["url"]).hostname or "").lower()
        for source in case["sources"]
        if source.get("browser_rendered", False)
    }

    def production_fetch(url: str, allowed_hosts: set[str], *, timeout: int = 25) -> tuple[bytes, str, str]:
        host = (urlparse(url).hostname or "").lower()
        if host in browser_hosts:
            # Explicit case-level approval: use a browser because the public page is client-rendered.
            return browser_fetch(url, allowed_hosts, timeout=timeout)
        return fetch_with_retry(url, allowed_hosts, timeout=timeout)

    return production_fetch


def build_production_normalizer(base_normalizer: Callable[[dict[str, Any]], dict[str, Any]]) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def normalise(fact: dict[str, Any]) -> dict[str, Any]:
        item = base_normalizer(fact)
        if item.get("status") == "extracted" and item.get("field") == "address" and item.get("value"):
            item["value"] = canonicalize_address(str(item["value"]))
        return item
    return normalise


def investigate_production(case_path: Path, out_dir: Path, *, now: str | None = None) -> dict[str, Any]:
    case = json.loads(case_path.read_text(encoding="utf-8"))
    original_fetch = resilient.fetch_source
    original_normalise = resilient._normalise_live_fact
    resilient.fetch_source = build_production_fetch(case)
    resilient._normalise_live_fact = build_production_normalizer(original_normalise)
    try:
        result = resilient.investigate_resilient(case_path, out_dir, now=now)
    finally:
        resilient.fetch_source = original_fetch
        resilient._normalise_live_fact = original_normalise
    result["run"]["acquisition_adapter"] = "direct_retry_plus_explicit_browser_render/2.3"
    (out_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run production public-source company acquisition with retries and explicit browser rendering.")
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("artifacts/intelligence-casework/live-company"))
    parser.add_argument("--minimum-sources", type=int, default=1)
    parser.add_argument("--minimum-claims", type=int, default=1)
    args = parser.parse_args()
    result = investigate_production(args.case, args.out)
    print(json.dumps(result["metrics"], indent=2))
    print("\nSOURCE STATUS")
    for source in result["sources"]:
        print(
            f"- {source['id']}: {source['acquisition_status']} http={source['http_status']} "
            f"facts={source['facts_extracted']} missing={','.join(source['required_not_found']) or '-'} "
            f"error={source['error'] or '-'}"
        )
    print("\n", result["bottom_line"])
    if result["integrity"]["status"] != "pass":
        return 1
    if result["metrics"]["sources_acquired"] < args.minimum_sources:
        return 2
    if result["metrics"]["claims"] < args.minimum_claims:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
