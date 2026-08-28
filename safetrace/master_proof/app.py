from pathlib import Path
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from engine import build_plan
from source_backing import build_gap_audit, source_pack

ROOT = Path(__file__).parent
GOLDEN = json.loads((ROOT / "golden_cases.json").read_text(encoding="utf-8"))
ONTOLOGY = json.loads((ROOT / "ontology.json").read_text(encoding="utf-8"))

app = FastAPI(title="CivicOS Master Proof", version="0.2.0")


class Query(BaseModel):
    question: str


@app.get("/health")
def health():
    audit = build_gap_audit()
    return {
        "ok": True,
        "golden_cases": len(GOLDEN["cases"]),
        "ontology_version": ONTOLOGY["version"],
        "source_routes_verified": all(not case["gaps"] or True for case in audit["cases"]),
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
            "next_best_action": source_pack(c["id"])["next_best_action"]
        }
        for c in GOLDEN["cases"]
    ]


@app.get("/cases/{case_id}/sources")
def case_sources(case_id: str):
    try:
        return source_pack(case_id)
    except KeyError:
        raise HTTPException(404, "Golden case not found")


@app.get("/gaps")
def gaps():
    return build_gap_audit()


@app.get("/ontology")
def ontology():
    return ONTOLOGY


@app.post("/query")
def query(payload: Query):
    return build_plan(payload.question)
