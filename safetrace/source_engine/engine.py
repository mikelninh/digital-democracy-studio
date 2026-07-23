from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import tempfile
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

PARSER_VERSION = "safetrace-source-engine/0.3.0"
USER_AGENT = "SafeTrace/0.3 (+https://github.com/mikelninh/digital-democracy-studio)"


@dataclass(frozen=True)
class SourceDefinition:
    source_id: str
    title: str
    url: str
    publisher: str
    source_type: str
    parser: str
    expected_content_type: str | None = None


@dataclass(frozen=True)
class SnapshotReceipt:
    source_id: str
    title: str
    publisher: str
    source_type: str
    canonical_url: str
    retrieved_at: str
    content_type: str
    byte_length: int
    sha256: str
    normalized_sha256: str
    parser_version: str
    raw_path: str
    previous_sha256: str | None
    changed: bool


Fetcher = Callable[[str], tuple[bytes, str]]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def normalize_for_change_detection(payload: bytes, content_type: str) -> bytes:
    """Reduce harmless HTML whitespace noise while leaving PDFs and other bytes intact."""
    if "html" not in content_type.lower():
        return payload
    text = payload.decode("utf-8", errors="replace")
    text = re.sub(r"\s+", " ", text).strip()
    return text.encode("utf-8")


def default_fetcher(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf,*/*"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:  # nosec B310: registry URLs are reviewed
        payload = response.read()
        content_type = response.headers.get_content_type() or "application/octet-stream"
        return payload, content_type


def _safe_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _extension(content_type: str, url: str) -> str:
    if "pdf" in content_type.lower():
        return ".pdf"
    if "html" in content_type.lower():
        return ".html"
    guessed = mimetypes.guess_extension(content_type.split(";", 1)[0].strip())
    return guessed or Path(url).suffix or ".bin"


class SnapshotStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _source_dir(self, source_id: str) -> Path:
        directory = self.root / source_id
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def latest_receipt(self, source_id: str) -> dict | None:
        receipts = sorted(self._source_dir(source_id).glob("*.receipt.json"))
        if not receipts:
            return None
        return json.loads(receipts[-1].read_text(encoding="utf-8"))

    def snapshot(
        self,
        source: SourceDefinition,
        *,
        fetcher: Fetcher = default_fetcher,
        retrieved_at: datetime | None = None,
    ) -> SnapshotReceipt:
        payload, content_type = fetcher(source.url)
        if not payload:
            raise ValueError(f"Source {source.source_id} returned an empty payload")
        if source.expected_content_type and source.expected_content_type not in content_type:
            raise ValueError(
                f"Source {source.source_id} returned {content_type!r}; "
                f"expected {source.expected_content_type!r}"
            )

        retrieved_at = retrieved_at or utc_now()
        raw_hash = sha256_bytes(payload)
        normalized_hash = sha256_bytes(normalize_for_change_detection(payload, content_type))
        previous = self.latest_receipt(source.source_id)
        previous_hash = previous.get("sha256") if previous else None
        changed = previous_hash is not None and previous_hash != raw_hash

        stamp = _safe_timestamp(retrieved_at)
        source_dir = self._source_dir(source.source_id)
        raw_name = f"{stamp}-{raw_hash[:12]}{_extension(content_type, source.url)}"
        receipt_name = f"{stamp}-{raw_hash[:12]}.receipt.json"
        raw_path = source_dir / raw_name
        receipt_path = source_dir / receipt_name

        with tempfile.NamedTemporaryFile(dir=source_dir, delete=False) as temporary:
            temporary.write(payload)
            temporary_path = Path(temporary.name)
        temporary_path.replace(raw_path)

        receipt = SnapshotReceipt(
            source_id=source.source_id,
            title=source.title,
            publisher=source.publisher,
            source_type=source.source_type,
            canonical_url=source.url,
            retrieved_at=retrieved_at.isoformat(),
            content_type=content_type,
            byte_length=len(payload),
            sha256=raw_hash,
            normalized_sha256=normalized_hash,
            parser_version=PARSER_VERSION,
            raw_path=str(raw_path.relative_to(self.root)),
            previous_sha256=previous_hash,
            changed=changed,
        )
        receipt_path.write_text(
            json.dumps(asdict(receipt), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return receipt


def load_sources(path: str | Path) -> list[SourceDefinition]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [SourceDefinition(**item) for item in payload["sources"]]


def snapshot_all(
    sources: Iterable[SourceDefinition],
    store: SnapshotStore,
    *,
    fetcher: Fetcher = default_fetcher,
) -> list[SnapshotReceipt]:
    return [store.snapshot(source, fetcher=fetcher) for source in sources]
