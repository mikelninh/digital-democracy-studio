from __future__ import annotations

import argparse
import json
from pathlib import Path

from safetrace.evidence_vault.build_release_artifacts import demo_registry
from safetrace.evidence_vault.vault import EvidenceVault
from .ledger import ClaimLedger
from .migration import build_migration_report
from .model import ClaimVersion, EvidenceLink, LedgerClaim, LedgerPublication, VaultEvidenceRef

NOW = "2026-07-24T06:00:00+00:00"


def vault_index(vault: EvidenceVault) -> dict[str, VaultEvidenceRef]:
    return {
        receipt.receipt_id: VaultEvidenceRef(
            receipt.receipt_id,
            receipt.source_id,
            receipt.object.sha256,
        )
        for receipt in vault.receipts()
    }


def approve_current(ledger: ClaimLedger, claim_id: str, *, created_at: str) -> dict:
    claim = ledger.claims[claim_id]
    version = claim.versions[claim.current_version]
    gates = ["identity", "evidence", "red_team", "legal", "right_of_reply", "publication", "correction"]
    assignees = {gate: f"reviewer:{gate}" for gate in gates}
    tasks = ledger.queue_reviews(claim_id, assignees, created_at)
    for task in tasks:
        ledger.decide(
            task.id,
            task.assignee_id,
            "approved",
            "The claim wording, evidence status, source anchors, limitations and required safeguards were reviewed.",
            created_at,
            contradictory_evidence_addressed=task.gate == "red_team",
        )
    result = ledger.evaluate(claim_id, version.version)
    return {"ready": result.ready, "blockers": list(result.blockers), "required_gates": list(result.required_gates)}


def build(safetrace_root: Path, output_root: Path) -> dict:
    vault = EvidenceVault(safetrace_root / "evidence_vault/artifacts/demo-vault", demo_registry())
    receipts = vault.receipts("synthetic:vault-demo")
    if len(receipts) < 2:
        raise RuntimeError("v1.4 release fixture requires the v1.3 Evidence Vault fixture")
    current_receipt = receipts[-1]
    index = vault_index(vault)
    ledger = ClaimLedger(index)

    evidence_v1 = (
        EvidenceLink(
            "link:fixture:v1:supporting",
            "claim:fixture",
            1,
            "supporting",
            "vault_receipt",
            current_receipt.source_id,
            "synthetic document — version statement",
            "The synthetic document records version two.",
            "researcher:fixture",
            NOW,
            current_receipt.receipt_id,
            current_receipt.object.sha256,
        ),
        EvidenceLink(
            "link:fixture:v1:contradicting",
            "claim:fixture",
            1,
            "contradicting",
            "vault_receipt",
            current_receipt.source_id,
            "synthetic document — earlier wording",
            "The earlier fixture wording requires explicit red-team consideration.",
            "researcher:fixture",
            NOW,
            current_receipt.receipt_id,
            current_receipt.object.sha256,
        ),
    )
    version1 = ClaimVersion(
        "claim:fixture",
        1,
        "The reviewed synthetic source currently records version two.",
        "verified_fact",
        "not_applicable",
        "public",
        "researcher:fixture",
        NOW,
        evidence_v1,
        limitations=("Synthetic fixture only; this is not claimed real-world evidence.",),
    )
    claim = LedgerClaim(
        "claim:fixture",
        "case:synthetic-ledger",
        "researcher:fixture",
        True,
        "draft",
        1,
        NOW,
        NOW,
        {1: version1},
    )
    ledger.add_claim(claim)
    first_gate = approve_current(ledger, claim.id, created_at=NOW)
    publication1 = LedgerPublication(
        "publication:fixture:v1",
        claim.case_id,
        ((claim.id, 1),),
        "draft",
        NOW,
        NOW,
    )
    ledger.publish(publication1)

    evidence_v2 = (
        EvidenceLink(
            "link:fixture:v2:supporting",
            claim.id,
            2,
            "supporting",
            "vault_receipt",
            current_receipt.source_id,
            "synthetic document — corrected statement",
            "The corrected claim narrows the wording to the exact reviewed fixture.",
            "researcher:fixture",
            "2026-07-24T06:30:00+00:00",
            current_receipt.receipt_id,
            current_receipt.object.sha256,
        ),
    )
    version2 = ClaimVersion(
        claim.id,
        2,
        "The reviewed synthetic fixture contains the text ‘Version two’.",
        "verified_fact",
        "not_applicable",
        "public",
        "researcher:fixture",
        "2026-07-24T06:30:00+00:00",
        evidence_v2,
        limitations=("Synthetic fixture only; wording was corrected for precision.",),
        supersedes_version=1,
    )
    correction = ledger.correct(
        claim.id,
        version2,
        "wording",
        "The initial statement was broader than the exact synthetic source wording.",
        "reviewer:correction",
        "2026-07-24T06:30:00+00:00",
    )
    second_gate = approve_current(ledger, claim.id, created_at="2026-07-24T06:35:00+00:00")
    publication2 = LedgerPublication(
        "publication:fixture:v2",
        claim.case_id,
        ((claim.id, 2),),
        "draft",
        "2026-07-24T06:40:00+00:00",
        "2026-07-24T06:40:00+00:00",
    )
    ledger.publish(publication2)

    migration = build_migration_report(safetrace_root)
    summary = ledger.summary()
    result = {
        "schema_version": "safetrace.claim-ledger-release/1.4",
        "status": "pass" if (
            first_gate["ready"]
            and second_gate["ready"]
            and publication1.status == "stale"
            and publication2.status == "published"
            and correction.visible
            and migration["status"] == "pass"
            and migration["automatic_publications"] == 0
        ) else "fail",
        "synthetic_fixture": {
            "first_version_gate": first_gate,
            "second_version_gate": second_gate,
            "first_publication_status_after_correction": publication1.status,
            "second_publication_status": publication2.status,
            "visible_correction": correction.visible,
            "invalidated_publications": list(correction.invalidated_publication_ids),
            "ledger_summary": summary,
        },
        "existing_case_migration": migration,
        "truthful_boundary": (
            "Existing claims are migrated but blocked for new publication until original evidence is backfilled into the Evidence Vault. The publishable demonstration uses synthetic vault-backed evidence only."
        ),
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "release-report.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--safetrace-root", type=Path, default=Path("safetrace"))
    parser.add_argument("--output-root", type=Path, default=Path("safetrace/claim_ledger/artifacts"))
    args = parser.parse_args()
    result = build(args.safetrace_root, args.output_root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
