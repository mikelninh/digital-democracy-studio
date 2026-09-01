from __future__ import annotations

import csv
import io
import json
import re
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

from safetrace.evidence_vault.model import RegistryEntry, RetentionPolicy
from safetrace.evidence_vault.registry import SourceRegistry
from safetrace.evidence_vault.vault import EvidenceVault

UKSL_SOURCE_ID = "uk-fcdo-sanctions-list-csv"
UKSL_URL = "https://sanctionslist.fcdo.gov.uk/docs/UK-Sanctions-List.csv"
ALLOWED_HOSTS = {"sanctionslist.fcdo.gov.uk"}
MAX_SOURCE_BYTES = 128 * 1024 * 1024
EXPECTED_CONTENT_TYPES = (
    "text/csv",
    "application/csv",
    "application/octet-stream",
    "application/vnd.ms-excel",
    "text/plain",
)


def _norm(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).split())


def _content_type(header: str | None) -> str:
    return (header or "application/octet-stream").split(";", 1)[0].strip().lower()


def build_registry(*, reviewed_at: str, reviewed_by: str = "portfolio-maintainer") -> SourceRegistry:
    policy = RetentionPolicy(
        policy_id="retain-public-sanctions-source",
        name="Retain public sanctions source originals",
        applies_to=("original", "parsed", "extraction"),
        minimum_days=None,
        expiry_action="retain",
        legal_hold=False,
        reviewed_by=reviewed_by,
        reviewed_at=reviewed_at,
    )
    entry = RegistryEntry(
        source_id=UKSL_SOURCE_ID,
        title="UK Sanctions List — CSV",
        publisher="Foreign, Commonwealth & Development Office",
        canonical_url=UKSL_URL,
        source_type="official_sanctions_list",
        source_rank="primary_official",
        jurisdiction="GB",
        update_cadence="daily",
        connector_id="safetrace.http-public-source",
        connector_version="1.0",
        parser_id="safetrace.uksl-csv",
        parser_version="1.0",
        expected_content_types=EXPECTED_CONTENT_TYPES,
        retention_policy_id=policy.policy_id,
        reviewed_by=reviewed_by,
        reviewed_at=reviewed_at,
        notes="Official FCDO UK Sanctions List CSV. Candidate retrieval only; identity conclusions require analyst review.",
    )
    return SourceRegistry([entry], [policy])


def fetch_public_source(url: str = UKSL_URL, *, timeout: int = 25, max_bytes: int = MAX_SOURCE_BYTES) -> tuple[bytes, str, str]:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("source URL is not on the reviewed HTTPS allowlist")
    req = urllib.request.Request(url, headers={"User-Agent": "SafeTrace-Intelligence-Casework/1.0 (+public-source-research)"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        final_url = response.geturl()
        final = urlparse(final_url)
        if final.scheme != "https" or final.hostname not in ALLOWED_HOSTS:
            raise ValueError("source redirected outside the reviewed allowlist")
        content_type = _content_type(response.headers.get("Content-Type"))
        if content_type not in EXPECTED_CONTENT_TYPES:
            raise ValueError(f"unexpected content type: {content_type}")
        length = response.headers.get("Content-Length")
        if length and int(length) > max_bytes:
            raise ValueError("source exceeds maximum permitted size")
        payload = response.read(max_bytes + 1)
        if len(payload) > max_bytes:
            raise ValueError("source exceeds maximum permitted size")
        if not payload:
            raise ValueError("source returned empty payload")
        return payload, content_type, final_url


def parse_uksl_csv(payload: bytes) -> list[dict]:
    text = payload.decode("utf-8-sig", errors="strict")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("UKSL CSV has no header")
    fields = {str(x).strip().lstrip("\ufeff") for x in reader.fieldnames if x}
    required = {"Unique ID", "Name 6", "Name type", "Individual, Entity, Ship"}
    missing = required - fields
    if missing:
        raise ValueError(f"UKSL CSV missing required fields: {sorted(missing)}")
    records = []
    for raw in reader:
        row = {(k or "").strip().lstrip("\ufeff"): (v or "").strip() for k, v in raw.items()}
        unique_id = row.get("Unique ID", "")
        if not unique_id:
            continue
        parts = [row.get(f"Name {i}", "") for i in range(1, 6)] + [row.get("Name 6", "")]
        full_name = " ".join(x for x in parts if x and x.lower() not in {"n/a", "na"}).strip()
        if not full_name:
            continue
        records.append({
            "unique_id": unique_id,
            "name": full_name,
            "name_type": row.get("Name type", ""),
            "record_type": row.get("Individual, Entity, Ship", ""),
            "dob": row.get("D.O.B", ""),
            "nationality": row.get("Nationality(/ies)", ""),
            "regime": row.get("Regime Name", ""),
            "sanctions_imposed": row.get("Sanctions Imposed", ""),
            "last_updated": row.get("Last Updated", ""),
        })
    if not records:
        raise ValueError("UKSL CSV produced no designation records")
    return records


def name_score(query: str, candidate: str) -> float:
    q, c = _norm(query), _norm(candidate)
    if not q or not c:
        return 0.0
    if q == c:
        return 1.0
    seq = SequenceMatcher(None, q, c).ratio()
    qt, ct = set(q.split()), set(c.split())
    dice = 2 * len(qt & ct) / (len(qt) + len(ct)) if qt and ct else 0.0
    subset = 0.98 if len(qt) >= 2 and qt.issubset(ct) else 0.0
    return round(max(seq, dice, subset), 4)


def screen_records(records: list[dict], query: str, *, dob: str | None = None, nationality: str | None = None, threshold: float = 0.65, limit: int = 10) -> list[dict]:
    best: dict[str, dict] = {}
    for record in records:
        score = name_score(query, record["name"])
        if score < threshold:
            continue
        conflicts, supports = [], []
        if dob and record.get("dob"):
            (supports if _norm(dob) == _norm(record["dob"]) else conflicts).append("dob")
        if nationality and record.get("nationality"):
            qn, rn = _norm(nationality), _norm(record["nationality"])
            (supports if qn and qn in rn else conflicts).append("nationality")
        candidate = {
            **record,
            "name_score": score,
            "identifier_support": supports,
            "identifier_conflicts": conflicts,
            "identity_status": "REVIEW_REQUIRED",
            "analyst_rule": "A list-name candidate is not automatically the same person or entity as the subject.",
        }
        existing = best.get(record["unique_id"])
        if existing is None or candidate["name_score"] > existing["name_score"]:
            best[record["unique_id"]] = candidate
    return sorted(best.values(), key=lambda x: (-x["name_score"], x["unique_id"]))[:limit]


def acquire_live_uksl(*, query: str, vault_root: Path, reviewed_at: str, dob: str | None = None, nationality: str | None = None) -> dict:
    registry = build_registry(reviewed_at=reviewed_at)
    vault = EvidenceVault(vault_root, registry)
    payload, content_type, resolved_url = fetch_public_source()
    receipt, alert = vault.acquire(
        UKSL_SOURCE_ID,
        payload,
        content_type,
        resolved_url=resolved_url,
        metadata={"purpose": "intelligence_casework_live_screening", "query": query},
    )
    records = parse_uksl_csv(payload)
    parsed_payload = (json.dumps(records, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    manifest = vault.transform(
        operation="parse",
        input_receipt_ids=[receipt.receipt_id],
        input_object_hashes=[receipt.object.sha256],
        outputs=[(parsed_payload, "application/json", "parsed", "public")],
        tool_id="safetrace.uksl-csv",
        tool_version="1.0",
        parameters={"records": len(records)},
        case_id="LIVE-UKSL-SCREEN",
    )
    candidates = screen_records(records, query, dob=dob, nationality=nationality)
    integrity = vault.verify_integrity()
    return {
        "schema": "safetrace.live-source-screening/1.0",
        "source": {
            "source_id": UKSL_SOURCE_ID,
            "publisher": "Foreign, Commonwealth & Development Office",
            "canonical_url": UKSL_URL,
            "resolved_url": resolved_url,
            "content_type": content_type,
            "object_sha256": receipt.object.sha256,
            "receipt_id": receipt.receipt_id,
            "receipt_hash": receipt.receipt_hash,
            "material_change_state": alert.kind,
            "registry_revision": receipt.registry_revision,
            "parser_manifest_id": manifest.manifest_id,
        },
        "query": {"name": query, "dob": dob, "nationality": nationality},
        "records_parsed": len(records),
        "candidates": candidates,
        "candidate_count": len(candidates),
        "identity_decision": "HUMAN_REVIEW_REQUIRED" if candidates else "NO_CANDIDATE_ABOVE_THRESHOLD",
        "integrity": integrity,
        "boundary": "Candidate retrieval from the live authoritative list only. No identity match or compliance decision is auto-confirmed.",
    }
