from pathlib import Path
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from composition import compose_case, portfolio_graph
from connectors import SourceFetchError, connector_manifest, fetch_official_source
from engine import build_plan
from source_backing import build_gap_audit, source_pack

ROOT = Path(__file__).parent
GOLDEN = json.loads((ROOT / "golden_cases.json").read_text(encoding="utf-8"))
ONTOLOGY = json.loads((ROOT / "ontology.json").read_text(encoding="utf-8"))
MODULES = json.loads((ROOT / "module_contracts.json").read_text(encoding="utf-8"))

app = FastAPI(title="CivicOS Master Proof", version="0.3.0")


class Query(BaseModel):
    question: str


@app.get("/health")
def health():
    audit = build_gap_audit()
    graph = portfolio_graph()
    return {
        "ok": True,
        "golden_cases": len(GOLDEN["cases"]),
        "ontology_version": ONTOLOGY["version"],
        "module_contract_version": MODULES["version"],
        "source_routes_verified": all(case["source_routes_verified"] for case in audit["cases"]),
        "source_snapshots_present": audit["source_backed_golden_cases"],
        "composed_cases": graph["cases_composition_ready"],
        "capability_coverage": graph["capability_coverage"],
        "production_ready": audit["production_ready"]
    }


@app.get("/cases")
def cases():
    return [
        {
            "id": c["id"],
            "persona": c["persona"],
            "domain": c["domain"],
            "question": c["question"],
            "next_best_action": source_pack(c["id"])["next_best_action"],
            "composition": compose_case(c["id"])
        }
        for c in GOLDEN["cases"]
    ]


@app.get("/cases/{case_id}/sources")
def case_sources(case_id: str):
    try:
        return source_pack(case_id)
    except KeyError:
        raise HTTPException(404, "Golden case not found")


@app.get("/cases/{case_id}/composition")
def case_composition(case_id: str):
    try:
        return compose_case(case_id)
    except KeyError:
        raise HTTPException(404, "Golden case not found")


@app.get("/modules")
def modules():
    return MODULES


@app.get("/composition")
def composition():
    return portfolio_graph()


@app.get("/sources")
def sources():
    return connector_manifest()


@app.post("/sources/{source_id}/fetch")
def fetch_source(source_id: str):
    """Fetch one reviewed official source and return a cryptographic receipt.

    Raw content is intentionally not returned by this endpoint. A production
    Evidence Vault should retain it under explicit retention/access rules.
    """
    try:
        receipt, _ = fetch_official_source(source_id)
    except SourceFetchError as exc:
        raise HTTPException(502, str(exc))
    return {"status": "fetched", "receipt": receipt.to_dict()}


@app.get("/gaps")
def gaps():
    return build_gap_audit()


@app.get("/ontology")
def ontology():
    return ONTOLOGY


@app.post("/query")
def query(payload: Query):
    return build_plan(payload.question)
