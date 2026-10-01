from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Iterable


@dataclass(frozen=True)
class EvidenceReceipt:
    id: str
    source: str
    source_type: str
    retrieved_at: str
    valid_from: str | None = None
    valid_to: str | None = None
    excerpt_hash: str | None = None
    reviewer_state: str = "machine_proposed"


@dataclass(frozen=True)
class Claim:
    id: str
    subject_id: str
    predicate: str
    object_id: str
    status: str
    evidence_ids: tuple[str, ...]
    valid_from: str | None = None
    valid_to: str | None = None
    confidence: float = 0.0
    reviewer_state: str = "machine_proposed"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def claims_conflict(a: Claim, b: Claim) -> bool:
    """Conservative conflict rule for functional-looking predicates.

    Two claims conflict only if they describe the same subject and predicate,
    assert different objects, and their validity periods may overlap.
    """
    if a.subject_id != b.subject_id or a.predicate != b.predicate:
        return False
    if a.object_id == b.object_id:
        return False
    return periods_may_overlap(a.valid_from, a.valid_to, b.valid_from, b.valid_to)


def periods_may_overlap(
    a_from: str | None,
    a_to: str | None,
    b_from: str | None,
    b_to: str | None,
) -> bool:
    # Unknown bounds are treated conservatively as potentially overlapping.
    if a_to is not None and b_from is not None and a_to < b_from:
        return False
    if b_to is not None and a_from is not None and b_to < a_from:
        return False
    return True


def contradiction_pairs(claims: Iterable[Claim]) -> list[dict]:
    items = list(claims)
    out: list[dict] = []
    for i, left in enumerate(items):
        for right in items[i + 1 :]:
            if claims_conflict(left, right):
                out.append({
                    "type": "CONTRADICTS",
                    "left_claim": left.id,
                    "right_claim": right.id,
                    "review_state": "human_review_required",
                    "reason": "same subject + predicate, different object, overlapping/unknown validity"
                })
    return out


def explain_claim(claim: Claim, receipts: Iterable[EvidenceReceipt]) -> dict:
    by_id = {receipt.id: receipt for receipt in receipts}
    evidence = [asdict(by_id[eid]) for eid in claim.evidence_ids if eid in by_id]
    missing = [eid for eid in claim.evidence_ids if eid not in by_id]
    return {
        "claim": asdict(claim),
        "evidence": evidence,
        "missing_evidence_ids": missing,
        "promotion_allowed": bool(evidence) and not missing and claim.reviewer_state in {"human_verified", "machine_proposed"},
        "why": "Every supported claim must point to inspectable evidence receipts; unresolved or conflicting claims remain visible."
    }
