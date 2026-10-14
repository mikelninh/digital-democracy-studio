"""Optional local FastAPI read-only evidence API for the same static case.

Not deployed on GitHub Pages, which hosts the standalone browser experience.
Run: uvicorn server:app --reload (from this directory)
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pipeline import load_case, claim_packet, discourse_summary, search_sources

app = FastAPI(title="SafeTrace Discourse Lab", version="1.0.0", description="Synthetic, read-only investigative evidence API")
fixture = load_case()


@app.get("/api/health")
def health():
    return {"status": "ok", "dataset": "synthetic", "public_impact_claimed": False}


@app.get("/api/summary")
def summary():
    return discourse_summary(fixture)


@app.get("/api/claims/{claim_id}")
def claim(claim_id: str):
    try:
        return claim_packet(fixture, claim_id)
    except KeyError as exc:
        raise HTTPException(404, "Unknown claim") from exc


@app.get("/api/search")
def search(q: str = Query(min_length=1, max_length=120)):
    return {"query": q, "results": search_sources(fixture, q)}


app.mount("/", StaticFiles(directory=".", html=True), name="frontend")
