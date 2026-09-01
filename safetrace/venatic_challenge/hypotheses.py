from __future__ import annotations

from typing import Any


HYPOTHESES = [
    {
        "id": "H1",
        "statement": "Mihailo Petrović is the sanctioned Mikhail Petrovich.",
        "support": ["S09", "S27"],
        "disconfirm": ["S07", "S08"],
        "initial_status": "rejected",
        "final_status": "rejected",
        "reason": "The allegation rests on name similarity; DOB, nationality and passport all conflict.",
    },
    {
        "id": "H2",
        "statement": "The changed payment beneficiary is unauthorized diversion.",
        "support": ["S14"],
        "disconfirm": ["S15", "S25"],
        "initial_status": "unresolved",
        "final_status": "rejected",
        "reason": "The invoice is a verification trigger. An assignment notice exists initially; independent supplier verification later confirms authorization.",
    },
    {
        "id": "H3",
        "statement": "Meridian Atlas Trading legally owns the Leipzig logistics site.",
        "support": ["S26"],
        "disconfirm": ["S17", "S19"],
        "initial_status": "rejected",
        "final_status": "rejected",
        "reason": "The land register identifies Atlas Property SPV GmbH as legal owner; operation and lease do not transfer ownership.",
    },
    {
        "id": "H4",
        "statement": "The conflicting director records indicate simultaneous concealed management.",
        "support": ["S01", "S16"],
        "disconfirm": ["S28"],
        "initial_status": "unresolved",
        "final_status": "rejected",
        "reason": "The apparent contradiction is temporal: the official filing history shows Markus Stein ceased before Anna Keller was appointed.",
    },
    {
        "id": "H5",
        "statement": "The natural-person principal behind Cedar Nominees is established.",
        "support": [],
        "disconfirm": ["S11", "S12"],
        "initial_status": "rejected",
        "final_status": "rejected",
        "reason": "The supplied nominee records explicitly leave the principal undisclosed. The gap must remain unresolved.",
    },
    {
        "id": "H6",
        "statement": "Mihailo Petrović has a material indirect economic and voting interest in Meridian Atlas Trading.",
        "support": ["S02", "S05", "S06", "S07"],
        "disconfirm": [],
        "initial_status": "supported",
        "final_status": "supported",
        "reason": "The documented chain produces 36.4% indirect economic interest and 30.8% indirect voting interest.",
    },
]


def build_board(available_source_ids: set[str]) -> list[dict[str, Any]]:
    final_round = any(source_id in available_source_ids for source_id in {"S25", "S28", "S19"})
    board: list[dict[str, Any]] = []
    for hypothesis in HYPOTHESES:
        support = [source_id for source_id in hypothesis["support"] if source_id in available_source_ids]
        disconfirm = [source_id for source_id in hypothesis["disconfirm"] if source_id in available_source_ids]
        status = hypothesis["final_status"] if final_round else hypothesis["initial_status"]
        board.append({
            "id": hypothesis["id"],
            "statement": hypothesis["statement"],
            "status": status,
            "supporting_evidence": support,
            "disconfirming_evidence": disconfirm,
            "reason": hypothesis["reason"],
            "boundary": "Hypothesis status is an analytical state, not a legal finding. New evidence may change it.",
        })
    return board
