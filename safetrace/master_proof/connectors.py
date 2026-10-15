from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).parent
REGISTRY = json.loads((ROOT / "source_registry.json").read_text(encoding="utf-8"))

MAX_BYTES = 2_000_000
DEFAULT_TIMEOUT_SECONDS = 12


@dataclass(frozen=True)
class FetchReceipt:
    source_id: str
    url: str
    fetched_at: str
    status_code: int
    content_type: str
    sha256: str
    bytes_read: int
    truncated: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SourceFetchError(RuntimeError):
    pass


def _registered_source(source_id: str) -> dict[str, Any]:
    try:
        return REGISTRY["sources"][source_id]
    except KeyError as exc:
        raise SourceFetchError(f"Unknown or non-allowlisted source: {source_id}") from exc


def fetch_official_source(
    source_id: str,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    max_bytes: int = MAX_BYTES,
) -> tuple[FetchReceipt, bytes]:
    """Fetch only an allowlisted source from source_registry.json.

    This deliberately does not accept arbitrary URLs. A source must first be
    reviewed and registered. The raw bytes can be retained by an Evidence Vault;
    the receipt is safe to pass downstream to claims/evals.
    """
    source = _registered_source(source_id)
    url = source["url"]
    request = Request(
        url,
        headers={
            "User-Agent": "CivicOS-Master-Proof/0.2 (+source-backed public-interest demo)",
            "Accept": "text/html,application/xhtml+xml,application/json,text/plain,application/xml;q=0.9,*/*;q=0.1",
        },
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:  # nosec B310: URL is registry allowlisted
            status = int(getattr(response, "status", 200))
            content_type = response.headers.get("Content-Type", "")
            body = response.read(max_bytes + 1)
    except Exception as exc:  # network/HTTP errors are surfaced, never converted to evidence
        raise SourceFetchError(f"Fetch failed for {source_id}: {exc}") from exc

    truncated = len(body) > max_bytes
    if truncated:
        body = body[:max_bytes]
    receipt = FetchReceipt(
        source_id=source_id,
        url=url,
        fetched_at=datetime.now(timezone.utc).isoformat(),
        status_code=status,
        content_type=content_type,
        sha256=hashlib.sha256(body).hexdigest(),
        bytes_read=len(body),
        truncated=truncated,
    )
    return receipt, body


def connector_manifest() -> list[dict[str, Any]]:
    """Expose reviewed connectors without touching the network."""
    return [
        {
            "source_id": source_id,
            "url": source["url"],
            "publisher": source["publisher"],
            "kind": source["kind"],
            "mode": "allowlisted_http",
            "requires_auth_or_special_access": source_id in {"transparenzregister"},
        }
        for source_id, source in REGISTRY["sources"].items()
    ]
