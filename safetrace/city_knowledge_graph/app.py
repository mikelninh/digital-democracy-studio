from pathlib import Path
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="SafeTrace City Knowledge Graph", version="0.1.0")
GRAPH = json.loads((Path(__file__).parent / "graph.json").read_text(encoding="utf-8"))
NODES = {n["id"]: n for n in GRAPH["nodes"]}

class Query(BaseModel):
    question: str


def neighbours(node_id: str):
    out = []
    for e in GRAPH["edges"]:
        if e["from"] == node_id:
            out.append({"direction":"out","edge":e,"node":NODES[e["to"]]})
        elif e["to"] == node_id:
            out.append({"direction":"in","edge":e,"node":NODES[e["from"]]})
    return out

@app.get("/health")
def health():
    return {"ok": True, "nodes": len(GRAPH["nodes"]), "edges": len(GRAPH["edges"])}

@app.get("/graph")
def graph():
    return GRAPH

@app.get("/entities/{node_id}")
def entity(node_id: str):
    if node_id not in NODES:
        raise HTTPException(404, "Entity not found")
    return {"entity": NODES[node_id], "relationships": neighbours(node_id)}

@app.post("/query")
def query(q: Query):
    text = q.question.lower()
    if "baum" in text or "fäll" in text:
        service = NODES["service-tree-permit"]
        authority = NODES["ba-mitte"]
        rule = NODES["rule-baumschutz"]
        return {
            "answer": "For the demo case in Berlin-Mitte, the relevant service is Baumfällgenehmigung; the Bezirksamt Mitte is represented as the responsible authority and the Berliner Baumschutzverordnung as the governing rule.",
            "confidence": "bounded-demo",
            "entities": [service, authority, rule],
            "evidence": [
                {"claim":"responsible authority","source":authority["source"]},
                {"claim":"governing rule","source":rule["source"]},
                {"claim":"service reference","source":service["source"]}
            ],
            "human_review": True,
            "note": "Synthetic proof: authority/service mappings must be validated against current official records before operational use."
        }
    if "straße" in text or "gehweg" in text or "sondernutzung" in text:
        return {
            "answer": "The graph links special use of public road land to the Bezirksamt Mitte and the Berliner Straßengesetz for this synthetic case.",
            "confidence": "bounded-demo",
            "entities": [NODES["service-special-use"], NODES["ba-mitte"], NODES["rule-berlstrg"]],
            "human_review": True
        }
    return {
        "answer": "No sufficiently grounded path was found in the demo graph.",
        "confidence": "low",
        "entities": [],
        "human_review": True
    }
