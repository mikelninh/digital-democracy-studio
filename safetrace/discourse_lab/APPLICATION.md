# Application proof · Investigative Data / AI / OSINT

## Two-minute interview walkthrough

1. **The question (20 seconds):** “A safety statistic appears across several voices. Is it independently confirmed or simply repeated?”
2. **Network (30 seconds):** Click the 42% claim; show the four fictional organisations and the chain behind the cited briefing.
3. **Evidence desk (40 seconds):** Open `S3` and `S4`. Explain that the claim exists but the figure cannot be independently reproduced from the available source record.
4. **Judgement (20 seconds):** Contrast the limitation with the next investigative step. Do **not** infer coordinated manipulation or real-world impact.
5. **Engineering (30 seconds):** Show `pipeline.py`, `server.py`, tests and source JSON; evidence identifiers and citations survive export. Describe what would need to change before real-data ingestion.

## Fit with mission-aligned teams

| Team | Demonstrable proof | Honest limit |
| --- | --- | --- |
| Investigative data / OSINT engineering | Data modelling, network exploration, source lineage, explainable case packets, reproducibility | Corpus is fictional; no live crawler or external sources |
| Integrity / trust and safety | Differentiate signal from attribution, clear uncertainty and human review | No platform production integration or moderation accuracy evaluation |
| Financial crime / fraud | Same pattern of evidence vs hypothesis; source and entity IDs, human-in-loop workflow | Not a transaction monitoring model or actual AML case history |
| Public-interest AI | Calm UX, accessibility-oriented interaction, reproducible public-interest methodology | No impact or partners claimed |
| Applied AI / RAG | Foundation for source-grounded retrieval with precise anchors | Lexical search only; no LLM, RAG or MCP integrated in this demo |

## CV bullet (English)

**Built SafeTrace Discourse Investigation Lab**, an interactive public-interest investigation work sample combining an evidence graph, traceable claims, source provenance and human-review notes. Added a Python validation/retrieval pipeline, a read-only FastAPI API and automated integrity checks; used a clearly labelled synthetic corpus to test source repetition without unsupported causal or coordination claims.

## Short introduction for a hiring manager

> I enjoy turning complicated, fragmented information into tools that help people ask better questions. This small SafeTrace demo shows how I approach that: make the source chain visible, separate repeated claims from independent evidence, design for a human reviewer, and be explicit about what the data cannot establish. I'd love to bring that combination of Python engineering, rapid prototyping and evidence-conscious product thinking to investigative data work.

## Best next genuine technical milestone

Replace a single synthetic source with an appropriately licensed and verified real public dataset. Record URL, fetched-at timestamp, original bytes or checksum, exact quote anchor, terms/license, correction/update policy and an immutable provenance manifest. **Do not silently mix fictional and real sources.** Then evaluate retrieval and false linkage on a separately authored test set. Real data ingestion must be human approved and lawful.
