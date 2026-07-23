from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

from .model import Edge, Graph, Node, Provenance


def provenance(source: dict, *, state: str = "verified_official_record") -> Provenance:
    return Provenance(
        source_id=source["source_id"],
        source_url=source["source_url"],
        source_title=source["source_title"],
        retrieved_or_checked_at=source["retrieved_or_checked_at"],
        evidence_state=state,
        source_anchor=source.get("source_anchor"),
    )


def build(seed_path: Path, output_path: Path) -> dict:
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    donation_source = provenance(seed["sources"]["donations_2026"])
    lobby_source = provenance(seed["sources"]["lobby_entry"])
    match_source = provenance(seed["sources"]["lobby_entry"], state="human_reviewed_match")

    organisation = seed["organisation"]
    lobby = seed["lobby_entry"]
    nodes = [
        Node(
            id=organisation["id"],
            type="organisation",
            label=organisation["label"],
            attributes={"entity_match": organisation["entity_match"]},
            provenance=(donation_source, lobby_source),
        ),
        Node(
            id=lobby["id"],
            type="lobby_entry",
            label=lobby["label"],
            attributes={"register_number": lobby["register_number"]},
            provenance=(lobby_source,),
        ),
    ]

    parties: dict[str, str] = {}
    for item in seed["donations"]:
        parties[item["party_id"]] = item["party"]
    nodes.extend(
        Node(id=party_id, type="political_party", label=label, provenance=(donation_source,))
        for party_id, label in sorted(parties.items())
    )
    nodes.extend(
        Node(
            id=item["id"],
            type="policy_interest",
            label=item["label"],
            provenance=(lobby_source,),
        )
        for item in seed["declared_policy_interests"]
    )

    edges = [
        Edge(
            id="edge:dvag-registered-r005553",
            type="registered_as",
            source=organisation["id"],
            target=lobby["id"],
            attributes={
                "match_state": "human_reviewed_match",
                "match_basis": organisation["entity_match"]["basis"],
            },
            provenance=(match_source,),
        )
    ]
    for item in seed["donations"]:
        edges.append(
            Edge(
                id=f"edge:{item['id']}",
                type="donated_to",
                source=organisation["id"],
                target=item["party_id"],
                attributes={
                    "amount_eur": item["amount_eur"],
                    "received_date": item["received_date"],
                    "reported_date": item["reported_date"],
                    "document": item["document"],
                },
                provenance=(donation_source,),
            )
        )
    for item in seed["declared_policy_interests"]:
        edges.append(
            Edge(
                id=f"edge:r005553:{item['id']}",
                type="declares_interest_in",
                source=lobby["id"],
                target=item["id"],
                provenance=(lobby_source,),
            )
        )

    total = sum(Decimal(item["amount_eur"]) for item in seed["donations"])
    graph = Graph(
        nodes=list(nodes),
        edges=edges,
        metadata={
            "case_id": seed["case_id"],
            "title": seed["title"],
            "reviewed_at": seed["reviewed_at"],
            "publication_boundary": seed["publication_boundary"],
            "donation_total_eur": format(total, ".2f"),
            "donation_count": len(seed["donations"]),
            "party_count": len(parties),
            "privacy": "Private home addresses are omitted from the public graph.",
        },
    )
    payload = graph.to_dict()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=Path, default=Path(__file__).parent / "data/seed.json")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "data/graph.json")
    args = parser.parse_args()
    build(args.seed, args.output)


if __name__ == "__main__":
    main()
