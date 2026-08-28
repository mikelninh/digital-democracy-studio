from pathlib import Path
import json
from fastapi import FastAPI
from pydantic import BaseModel

from engine import build_plan

ROOT = Path(__file__).parent
GOLDEN = json.loads((ROOT / "golden_cases.json").read_text(encoding="utf-8"))
ONTOLOGY = json.loads((ROOT / "ontology.json").read_text(encoding="utf-8"))

app = FastAPI(title="CivicOS Master Proof", version="0.1.0")


class Query(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"ok": True, "golden_cases": len(GOLDEN["cases"]), "ontology_version": ONTOLOGY["version"]}


@app.get("/cases")
def cases():
    return [{"id": c["id"], "persona": c["persona"], "domain": c["domain"], "question": c["question"]} for c in GOLDEN["cases"]]


@app.get("/ontology")
def ontology():
    return ONTOLOGY


@app.post("/query")
def query(payload: Query):
    return build_plan(payload.question)
