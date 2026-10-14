# SafeTrace · Discourse Investigation Lab

> **One origin ≠ three confirmations.** A shareable, evidence-first OSINT / public-discourse work sample by Michael Ninh.

This is a **standalone, fully fictional case** built as a focused companion to SafeTrace's existing Evidence Vault, Claim Ledger, entity-resolution pipeline, human review gates and Investigation Desk. It does not replace or claim production integration with those modules.

## What reviewers can actually do

1. Explore a clickable network of **7 fictional organisations, 5 claims and 9 fictional sources** (21 nodes).
2. Follow **20 synthetic messages** to underlying source identifiers and exact text anchors.
3. Compare corroboration with **source-chain repetition**, uncertainty and contradictory documents.
4. Search, filter and inspect claims, original excerpts and what the evidence does **not** prove.
5. Write a session-local analyst note, then **export a Markdown case brief** with citations and caveats.
6. Read a deterministic Python evidence retrieval and validation pipeline, plus optional read-only FastAPI API.

## Run the interactive demo

The easiest way is to **open `index.html`** directly. The demonstration uses local JavaScript and an embedded JSON-derived fixture, so no server or internet connection is needed.

For a local HTTP server:

```bash
cd safetrace-discourse-lab
python -m http.server 8000
# http://localhost:8000/
```

Or use the companion `safetrace-discourse-lab-demo.html` in the downloadable package, a completely self-contained single-file copy of the interface.

## Run the Python / FastAPI proof

```bash
python -m unittest discover -s tests -v
python pipeline.py            # deterministic case summary
python evaluation.py          # synthetic sanity checks
python -m pip install -r requirements.txt
uvicorn server:app --reload   # GET /api/health, /api/summary, /api/claims/c2, /api/search?q=42%25
```

The **static website does not call this API**, and GitHub Pages cannot host FastAPI. The API is a separate, runnable engineering demonstration using the same case contract.

### Honest evaluation

- Case integrity / evidence-link / abstention checks: **10/10 automated Python unit tests pass** locally.
- Transparent lexical retriever: **7/7 developer-authored synthetic queries** hit their expected source at rank 1.
- **Not** a real-world retrieval benchmark, not independently validated, and not ML/LLM performance.
- Browser smoke test script is supplied in `tests/browser_qa.py` but **has not been successfully executed in this environment** because Chromium navigation was blocked. Do not claim it passed.

## Investigative example

The fictional mobility programme quotes a **42% decline in reported near misses**. Four organisations pass on the number, but the early messages all cite a **single briefing (`S3`, Finding 3)**. The supplied data-request correspondence (`S4`) does not contain the measurements necessary to reproduce the figure. A later note (`S9`) maps the citation chain but adds no new measurements.

The correct output is **unverified**, not "proven impact" or "coordinated misinformation". The next question is to obtain the junction-level methods and observations. Equally, €8.4m **authorised** is not €8.4m **spent**; survey concerns do not prove design omissions; a design does not prove construction.

## Architecture

```text
           FIXED SYNTHETIC CASE / public-style records
                               │
                  data/corpus.json (source of truth)
                               │
               build_data.py → data/corpus.js
                               │
                HTML + CSS + plain JavaScript
          graph / source desk / notes / Markdown export
                               │
          Static GitHub Pages or no-dependency local file

      ┌──────────────────────────────────────────────┐
      │ Optional Python backend (read-only)           │
      │ pipeline.py: validation, packets, retrieval   │
      │ server.py: typed FastAPI response endpoints    │
      │ tests/: source lineage and ethical guardrails  │
      └──────────────────────────────────────────────┘
```

All content is locally authored **test data**. There is no real web acquisition, authenticated OSINT extraction, LLM deployment, embedding search, fact-checking against the internet, or MCP connector in this version. These could be added behind source licensing, reproducible acquisition receipts, evaluation, privacy review and human approval.

## Core design principles

- **No automated accusations:** graph connections indicate citations, not coordination, corruption, influence or wrongdoing.
- **Evidence is not a conclusion:** source anchors, provenance and limitations remain visible.
- **No personal data:** all actors are fictional organisations, not private individuals.
- **No fake authority:** "Official-style record" is an invented teaching fixture, not a government record.
- **Human-review state:** a notebook note does not update the canonical evidence, approve a claim or publish.
- **No network calls or analytics:** the browser demo runs entirely client side.
- **Correctness over sophistication:** deterministic retrieval is accurately described; no claims of shipping a RAG model just because the project is AI-adjacent.

## Integration path into SafeTrace

Suggested repository destination: `safetrace/discourse_lab/`. Keep the current source model intact. Later adapters may map `sources → Evidence Vault`, `claims → Claim Ledger`, `actors → Evidence Graph`, and `reviews → Investigation Desk`, but only after explicit schemas, rights, retention and workflow verification. For a live GitHub Pages link, merge the new folder and open `/digital-democracy-studio/safetrace/discourse_lab/`.

**This is an engineering and UX portfolio proof, not an operational investigative product.**


## Verified Berlin source catalogue (2026-10-14)

Open [`public_sources/`](public_sources/) for a separate, interactive source-lineage mini-case built from documented official pages of Abgeordnetenhaus Berlin, PARDOK, Bundestag, and Berlin Open Data. It is **not an acquired parliamentary document corpus**, and does not imply live API reliability or independent corroboration from multiple links to the same publisher.

The catalogue includes exact primary URLs, anchor locations, limitations, an evidence graph, claim inspection and a local Markdown export. Data licence: **Parlamentsdokumentation, Abgeordnetenhaus von Berlin — Datenlizenz Deutschland Namensnennung 2.0**; project summaries are modified/derived. Official record PDFs and third-party rights have additional restrictions.

Run public-source contract checks:

```bash
cd public_sources && python -m unittest test_audit -v && python audit.py
```

A future data-acquisition iteration should use PARDOK's official read-only API, an appropriately obtained key, bounded queries, a raw response hash, licence notes, retention and human review. This work sample does not yet execute those requests.
