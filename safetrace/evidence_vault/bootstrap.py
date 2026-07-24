from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .model import RegistryEntry, RetentionPolicy
from .registry import SourceRegistry

REVIEWED_AT = "2026-07-24T00:00:00+00:00"


def _rank(source_type: str, publisher: str) -> str:
    text=f"{source_type} {publisher}".lower()
    if any(word in text for word in ("official","bundestag","bundeswehr","ministry","government","greco","oecd","register")):
        return "primary_official"
    return "authoritative_secondary"


def _entry(source_id: str, title: str, publisher: str, url: str, source_type: str, *, parser: str = "reviewed_json_v1", expected: tuple[str,...] = ("text/html", "application/pdf"), cadence: str = "weekly") -> RegistryEntry:
    return RegistryEntry(source_id,title,publisher,url,source_type,_rank(source_type,publisher),"Germany",cadence,"safetrace.reviewed-http","1.3.0",parser,"1.0",expected,"retain-public-originals","SafeTrace maintainer",REVIEWED_AT,"approved","public",True,"Bootstrapped from an existing reviewed SafeTrace case source.")


def collect_existing_sources(safetrace_root: Path) -> SourceRegistry:
    entries: dict[str,RegistryEntry]={}
    source_file=safetrace_root/"source_engine/data/sources.json"
    if source_file.exists():
        for raw in json.loads(source_file.read_text(encoding="utf-8"))["sources"]:
            expected=(raw.get("expected_content_type") or "text/html",)
            entries[raw["source_id"]]=_entry(raw["source_id"],raw["title"],raw["publisher"],raw["url"],raw["source_type"],parser=raw.get("parser","source_engine_v1"),expected=expected)
    seed=safetrace_root/"political_money/data/seed.json"
    if seed.exists():
        for raw in json.loads(seed.read_text(encoding="utf-8"))["sources"].values():
            entries[raw["source_id"]]=_entry(raw["source_id"],raw["source_title"],"Deutscher Bundestag",raw["source_url"],"official_registry_or_disclosure")
    arms=safetrace_root/"arms_monitor/data/baseline.json"
    if arms.exists():
        for raw in json.loads(arms.read_text(encoding="utf-8"))["sources"].values():
            entries[raw["id"]]=_entry(raw["id"],raw["title"],raw["publisher"],raw["url"],"official_record")
    fairness=safetrace_root/"law_fairness/data/case_004.json"
    if fairness.exists():
        for raw in json.loads(fairness.read_text(encoding="utf-8"))["sources"]:
            entries[raw["id"]]=_entry(raw["id"],raw["title"],raw["publisher"],raw["url"],raw["source_type"])
    claims=safetrace_root/"review_desk/data/claims.json"
    if claims.exists():
        for claim in json.loads(claims.read_text(encoding="utf-8"))["claims"]:
            for raw in claim.get("evidence",[]):
                entries.setdefault(raw["source_id"],_entry(raw["source_id"],raw["source_title"],"Reviewed public source",raw["source_url"],"reviewed_evidence_source"))
    policy=RetentionPolicy("retain-public-originals","Retain reviewed public originals",("original","normalized","parsed","extraction","redacted","export"),None,"retain",False,"SafeTrace maintainer",REVIEWED_AT)
    return SourceRegistry(entries.values(),[policy])


def build_bootstrap_report(safetrace_root: Path, registry_root: Path) -> dict[str,Any]:
    registry=collect_existing_sources(safetrace_root)
    revision=registry.save(registry_root)
    source_ids=[x.source_id for x in sorted(registry.entries,key=lambda x:x.source_id)]
    return {"schema_version":"safetrace.registry-bootstrap/1.3","status":"pass" if len(source_ids)>=10 else "fail","registry_revision":revision,"sources":len(registry.entries),"minimum_expected_sources":10,"policies":len(registry.policies),"source_ids":source_ids,"boundary":"Reviewed public sources only; this registry does not authorise restricted or victim-sensitive acquisition."}
