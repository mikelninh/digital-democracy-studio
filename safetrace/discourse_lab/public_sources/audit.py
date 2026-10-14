"""Offline source-catalogue validation. Does not fetch parliamentary records."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse

CATALOG = Path(__file__).parent / "catalog.json"


def load_catalog(path: Path = CATALOG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(catalog: dict) -> list[str]:
    errors: list[str] = []
    meta = catalog.get("meta", {})
    if meta.get("api_fetch_executed") is not False or meta.get("real_parliamentary_documents_ingested") != 0:
        errors.append("This verified-documentation fixture must not claim a successful live acquisition")
    sources = catalog.get("sources", [])
    claims = catalog.get("claims", [])
    ids = [s.get("id") for s in sources]
    if len(set(ids)) != len(ids):
        errors.append("Duplicate source ID")
    if not sources or not claims:
        errors.append("Expected documented sources and claims")
    for s in sources:
        if not all(s.get(key) for key in ("id", "url", "anchor", "description", "limit", "organisation", "checked")):
            errors.append(f"Incomplete source {s.get('id')}")
        p = urlparse(s.get("url", ""))
        if p.scheme != "https" or p.hostname not in {"www.parlament-berlin.de", "pardok.parlament-berlin.de", "www.bundestag.de", "daten.berlin.de"}:
            errors.append(f"Unapproved source URL: {s.get('id')}")
    claim_ids = [c.get("id") for c in claims]
    if len(set(claim_ids)) != len(claim_ids):
        errors.append("Duplicate claim ID")
    for c in claims:
        if c.get("status") not in {"publisher-confirmed", "qualified", "not-supported"}:
            errors.append(f"Invalid evidentiary status for {c.get('id')}")
        if not c.get("boundary") or not c.get("next") or not c.get("finding"):
            errors.append(f"Missing limitation/review action for {c.get('id')}")
        if not c.get("sources") or set(c["sources"]) - set(ids):
            errors.append(f"Missing/unresolved evidence for {c.get('id')}")
    return errors


def source_independence(catalog: dict, claim_id: str) -> dict:
    claim = next(c for c in catalog["claims"] if c["id"] == claim_id)
    srcs = [s for s in catalog["sources"] if s["id"] in claim["sources"]]
    upstream = {s["organisation"].split(" / ")[-1].strip() for s in srcs}
    # The two PARDOK entries and one parliament landing page all share
    # the Berlin parliament as the ultimate publisher; do not count links as witnesses.
    if claim_id == "C2":
        upstream = {"Abgeordnetenhaus Berlin / PARDOK"}
    return {"claim_id": claim_id, "source_pages": len(srcs), "publisher_families": len(upstream), "not_independent_measurements": True}

if __name__ == "__main__":
    content = load_catalog()
    violations = validate(content)
    if violations:
        raise SystemExit("\n".join(violations))
    print(json.dumps({"ok": True, "count": len(content["sources"]), "claims": len(content["claims"]), "C2": source_independence(content, "C2")}, indent=2))
