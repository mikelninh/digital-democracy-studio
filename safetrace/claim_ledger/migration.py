from __future__ import annotations

from pathlib import Path
from typing import Any

from safetrace.core.migration_report import build_existing_bundles
from .ledger import ClaimLedger
from .model import ClaimVersion, EvidenceLink, LedgerClaim

MIGRATED_AT = "2026-07-24T05:00:00+00:00"


def migrate_bundle(bundle) -> ClaimLedger:
    ledger = ClaimLedger()
    sources = {source.id: source for source in bundle.sources}
    evidence = {item.id: item for item in bundle.evidence}
    for core_claim in bundle.claims:
        links = []
        for index, evidence_id in enumerate(core_claim.evidence_ids):
            item = evidence[evidence_id]
            source = sources[item.source_id]
            links.append(
                EvidenceLink(
                    id=f"legacy-link:{core_claim.id}:v1:{index}",
                    claim_id=core_claim.id,
                    version=1,
                    role=item.role,
                    provenance_mode="legacy_reference",
                    source_id=item.source_id,
                    anchor=item.source_anchor or "Legacy evidence anchor not yet backfilled into the Evidence Vault",
                    summary=item.summary,
                    added_by="safetrace-v1.4-migration",
                    added_at=MIGRATED_AT,
                    legacy_url=source.canonical_url,
                )
            )
        version = ClaimVersion(
            claim_id=core_claim.id,
            version=1,
            text=core_claim.text,
            evidence_state=core_claim.evidence_state,
            legal_status=core_claim.legal_status,
            sensitivity=core_claim.sensitivity,
            created_by="safetrace-v1.4-migration",
            created_at=MIGRATED_AT,
            evidence_links=tuple(links),
            limitations=tuple(core_claim.limitations) + (
                "Migrated from a reviewed legacy SafeTrace record; original source bytes must be backfilled into the Evidence Vault before new publication.",
            ),
            metadata={
                "legacy_review_ids": list(core_claim.review_ids),
                "legacy_correction_ids": list(core_claim.correction_ids),
                "migration_status": "requires_vault_backfill",
            },
        )
        claim = LedgerClaim(
            id=core_claim.id,
            case_id=bundle.case.id,
            researcher_id="safetrace-v1.4-migration",
            material=core_claim.material,
            status="migrated_pending_evidence_backfill",
            current_version=1,
            created_at=MIGRATED_AT,
            updated_at=MIGRATED_AT,
            versions={1: version},
        )
        ledger.add_claim(claim)
    return ledger


def build_migration_report(safetrace_root: Path) -> dict[str, Any]:
    bundles = build_existing_bundles(safetrace_root)
    cases = {}
    total = 0
    for case_id, bundle in sorted(bundles.items()):
        ledger = migrate_bundle(bundle)
        count = len(ledger.claims)
        total += count
        blocked = sum(1 for claim in ledger.claims.values() if not ledger.evaluate(claim.id).ready)
        cases[case_id] = {
            "claims_imported": count,
            "claims_blocked_pending_vault_backfill": blocked,
            "published_automatically": 0,
        }
    return {
        "schema_version": "safetrace.claim-ledger-migration/1.4",
        "status": "pass" if set(cases) == {"case-001", "case-002", "case-003", "case-004"} and total > 0 else "fail",
        "cases": cases,
        "total_claims_imported": total,
        "automatic_publications": 0,
        "boundary": (
            "Existing claims are preserved but remain blocked for new publication until their original evidence is acquired and verified through the Evidence Vault."
        ),
    }
