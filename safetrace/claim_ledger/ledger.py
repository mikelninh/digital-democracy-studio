from __future__ import annotations

from dataclasses import replace

from .model import (
    ClaimVersion,
    GateResult,
    LedgerClaim,
    LedgerCorrection,
    LedgerPublication,
    ReviewDecision,
    ReviewTask,
    VaultEvidenceRef,
)


def required_gates(version: ClaimVersion, material: bool) -> tuple[str, ...]:
    gates = ["evidence", "red_team", "publication"]
    if version.metadata.get("identity_sensitive") or version.metadata.get("person_entity_ids"):
        gates.insert(0, "identity")
    if (
        version.sensitivity != "public"
        or version.evidence_state in {"official_allegation", "analytical_red_flag"}
        or version.metadata.get("materially_discusses_person")
    ):
        gates.extend(["legal", "right_of_reply"])
    if version.version > 1:
        gates.append("correction")
    return tuple(dict.fromkeys(gates))


class ClaimLedger:
    def __init__(self, vault_index: dict[str, VaultEvidenceRef] | None = None):
        self.vault_index = vault_index or {}
        self.claims: dict[str, LedgerClaim] = {}
        self.tasks: dict[str, ReviewTask] = {}
        self.decisions: dict[str, ReviewDecision] = {}
        self.publications: dict[str, LedgerPublication] = {}
        self.corrections: dict[str, LedgerCorrection] = {}

    def add_claim(self, claim: LedgerClaim) -> None:
        if claim.id in self.claims:
            raise ValueError("Claim already exists")
        claim.validate(self.vault_index)
        self.claims[claim.id] = claim

    def queue_reviews(self, claim_id: str, assignees: dict[str, str], created_at: str) -> list[ReviewTask]:
        claim = self.claims[claim_id]
        version = claim.versions[claim.current_version]
        queued = []
        for gate in required_gates(version, claim.material):
            if gate not in assignees:
                raise ValueError(f"Missing assignee for {gate}")
            task_id = f"task:{claim_id}:v{version.version}:{gate}"
            task = ReviewTask(task_id, claim_id, version.version, gate, assignees[gate], "pending", created_at, True)
            task.validate()
            self.tasks[task_id] = task
            queued.append(task)
        claim.status = "review"
        claim.updated_at = created_at
        return queued

    def decide(
        self,
        task_id: str,
        reviewer_id: str,
        outcome: str,
        rationale: str,
        decided_at: str,
        contradictory_evidence_addressed: bool = False,
    ) -> ReviewDecision:
        task = self.tasks[task_id]
        decision = ReviewDecision(
            f"decision:{task_id}",
            task_id,
            reviewer_id,
            outcome,
            rationale,
            decided_at,
            contradictory_evidence_addressed,
        )
        decision.validate()
        self.decisions[task_id] = decision
        self.tasks[task_id] = replace(task, status=outcome)
        return decision

    def evaluate(self, claim_id: str, version: int | None = None) -> GateResult:
        claim = self.claims[claim_id]
        number = version or claim.current_version
        record = claim.versions[number]
        blockers: list[str] = []
        gates = required_gates(record, claim.material)
        try:
            record.validate(self.vault_index)
        except ValueError as exc:
            blockers.append(str(exc))
        if not record.vault_backed:
            blockers.append("Claim evidence is not fully backed by Evidence Vault receipts")
        for gate in gates:
            task_id = f"task:{claim_id}:v{number}:{gate}"
            task = self.tasks.get(task_id)
            decision = self.decisions.get(task_id)
            if not task:
                blockers.append(f"Missing {gate} review task")
                continue
            if not decision or decision.outcome not in {"approved", "waived"}:
                blockers.append(f"{gate} review is not approved")
            if record.sensitivity != "public" and decision and decision.reviewer_id == claim.researcher_id:
                blockers.append(f"Sensitive claim reviewer separation failed at {gate}")
            if gate == "publication" and decision and decision.reviewer_id == claim.researcher_id:
                blockers.append("Material publication reviewer must differ from researcher")
        contradictions = any(link.role == "contradicting" for link in record.evidence_links)
        red_team = self.decisions.get(f"task:{claim_id}:v{number}:red_team")
        if contradictions and (not red_team or not red_team.contradictory_evidence_addressed):
            blockers.append("Contradicting evidence was not addressed by red-team review")
        result = GateResult(not blockers, tuple(blockers), gates)
        if result.ready and number == claim.current_version:
            claim.status = "publishable"
        return result

    def publish(self, publication: LedgerPublication) -> LedgerPublication:
        publication.validate()
        for claim_id, version in publication.claim_versions:
            if self.claims[claim_id].case_id != publication.case_id:
                raise ValueError("Publication mixes cases")
            result = self.evaluate(claim_id, version)
            if not result.ready:
                raise ValueError("; ".join(result.blockers))
        publication.status = "published"
        self.publications[publication.id] = publication
        for claim_id, version in publication.claim_versions:
            if version == self.claims[claim_id].current_version:
                self.claims[claim_id].status = "published"
        return publication

    def correct(
        self,
        claim_id: str,
        new_version: ClaimVersion,
        correction_type: str,
        reason: str,
        approved_by: str,
        corrected_at: str,
    ) -> LedgerCorrection:
        claim = self.claims[claim_id]
        old_version = claim.current_version
        if (
            new_version.claim_id != claim_id
            or new_version.version != old_version + 1
            or new_version.supersedes_version != old_version
        ):
            raise ValueError("Correction version must supersede current version")
        new_version.validate(self.vault_index)
        claim.versions[new_version.version] = new_version
        claim.current_version = new_version.version
        claim.status = "review"
        claim.updated_at = corrected_at
        invalidated = []
        for publication in self.publications.values():
            if publication.status == "published" and (claim_id, old_version) in publication.claim_versions:
                publication.status = "stale"
                publication.stale_reason = (
                    f"Claim {claim_id} corrected from v{old_version} to v{new_version.version}"
                )
                invalidated.append(publication.id)
        correction = LedgerCorrection(
            f"correction:{claim_id}:v{old_version}-v{new_version.version}",
            claim_id,
            old_version,
            new_version.version,
            correction_type,
            reason,
            approved_by,
            corrected_at,
            True,
            tuple(invalidated),
        )
        correction.validate()
        self.corrections[correction.id] = correction
        return correction

    def summary(self) -> dict:
        return {
            "schema_version": "safetrace.claim-ledger/1.4",
            "claims": len(self.claims),
            "claim_versions": sum(len(claim.versions) for claim in self.claims.values()),
            "review_tasks": len(self.tasks),
            "review_decisions": len(self.decisions),
            "publications": len(self.publications),
            "stale_publications": sum(1 for publication in self.publications.values() if publication.status == "stale"),
            "visible_corrections": sum(1 for correction in self.corrections.values() if correction.visible),
            "vault_backed_current_claims": sum(
                1
                for claim in self.claims.values()
                if claim.versions[claim.current_version].vault_backed
            ),
            "pending_evidence_backfill": sum(
                1 for claim in self.claims.values() if claim.status == "migrated_pending_evidence_backfill"
            ),
        }
