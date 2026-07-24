# SafeTrace Investigation OS

This document defines how a small public-interest online investigation team works day to day: roles, agents, case gates, tools, data zones and quality controls.

## Operating objective

Turn a bounded public-interest question into a reproducible, human-reviewed answer while minimising harm and preserving uncertainty.

## Human team

- **Case Lead / Investigative Editor** — owns scope, public-interest test, prioritisation, fairness and publication.
- **OSINT Researcher** — builds source maps, verifies chronology and documents gaps.
- **Investigation Engineer** — builds connectors, provenance, search, graphs, exports, evaluations and agent workflows.
- **Data and Financial Analyst** — analyses budgets, taxes, benefits, procurement, ownership and distributional effects.
- **Legal and Editorial Reviewer** — reviews evidentiary language, privacy, right of reply and publication risk.
- **Security and Privacy Lead** — owns access, encryption, retention, deletion, audit review and incident response.

One person may initially cover several roles, but the researcher of a sensitive claim may not be its sole final approver.

## Daily agents

Agents return structured proposals. They never autonomously publish, accuse, refer or contact subjects.

- **Scout** — discovers official sources, datasets, judgments and disclosures.
- **Archivist** — stores original bytes, hashes, retrieval metadata and parser versions.
- **Reader** — extracts proposed entities, dates, amounts, decisions and exact source anchors.
- **Linker** — proposes entity matches and relationships; consequential matches require official identifiers or human confirmation.
- **Chronologist** — builds timelines and identifies inconsistencies without treating sequence as causation.
- **Claim Compiler** — creates atomic claims with evidence states, limitations and review requirements.
- **Skeptic** — searches for contradictions, alternative explanations, inherited decisions and unsupported causal wording.
- **Quant** — models direct fiscal and distributional effects while separating forecasts from measured outcomes.
- **Legal Status Agent** — distinguishes proposal, enactment, entry into force, allegation, charge, judgment, appeal and final judgment.
- **Guardian** — flags private addresses, vulnerable people, children, health data, witnesses and tactically sensitive conflict information.
- **Watchtower** — detects source changes, deadlines and judgments but cannot change public status.
- **Explainer** — produces layered citizen explanations without changing evidence status.

## Case lifecycle

### Gate 0 — Case acceptance

Required artefact: **Case Charter** with bounded question, public-interest rationale, expected sources, affected people, risks, prohibited methods, named owner and possible outcomes.

A valid result may be: “The available evidence does not establish the allegation.”

### Gate 1 — Source map

Register primary and secondary sources, authority, access method, cadence, limitations and parser state.

### Gate 2 — Collection and preservation

Retain source bytes and provenance receipts before transformation. Earlier versions are never silently replaced.

### Gate 3 — Extraction

Agents return structured proposals with exact anchors. Anchorless extraction cannot enter the reviewed evidence ledger.

### Gate 4 — Entity resolution

Consequential identity matches require official identifiers or documented human evidence. Uncertainty remains visible.

### Gate 5 — Claim ledger

Every material assertion becomes an atomic claim with evidence state, supporting and contradicting material, limitations and reviewers.

### Gate 6 — Red team

The Skeptic Agent and a human reviewer attempt to disprove, narrow or reframe important claims.

### Gate 7 — Legal, privacy and harm review

Check necessity, proportionality, identity, vulnerable-person risk, right of reply, legal status and publication language.

### Gate 8 — Publication

Only approved records enter public outputs. Every output includes provenance, review time, limitations, correction route and version.

### Gate 9 — Monitoring and correction

Monitor source changes, judgments, disclosures, deadlines and statements. Preserve public correction history.

## Core tools

1. **Case Registry** — charter, owner, state, risks, data zone and deadlines.
2. **Source Registry** — canonical definitions, hierarchy, connector, health and retention.
3. **Evidence Vault** — original records, hashes, transformations, redactions and audit events.
4. **Unified Evidence Model** — Case, Source, Snapshot, Entity, Relationship, Event, Claim, Evidence, Review, Publication, Correction and AgentTask.
5. **Claim Ledger** — atomic versioned claims with evidence and reviewer decisions.
6. **Relationship Graph** — sourced edges with certainty, temporal scope and reviewer.
7. **Timeline Workbench** — dated events with provenance and alternative dates.
8. **Review Desk** — identity, evidence, red-team, legal, right-of-reply, publication and correction queues.
9. **Agent Task Queue** — bounded inputs, permissions, data zones, schemas, model and prompt versions, timeout and approver.
10. **Public Case Builder** — dashboard, timeline, graph, sources, methodology, PDF, JSON and corrections.
11. **Law Fairness Simulator** — transparent household scenarios, budget effects and political attribution.
12. **Conflict and Arms Protocol** — separates policy, budget, procurement, export, delivery, alleged use, consequences and legal assessment.

## Data zones

### Zone 1 — Public

Official records, public registers, judgments and approved public outputs.

### Zone 2 — Sensitive internal

Uncertain matches, unpublished analysis, reviewer notes and pre-publication drafts.

### Zone 3 — Restricted

Victim, witness, whistleblower or partner-restricted information. Zone 3 stays disabled until external security, legal and governance gates are satisfied.

## Daily operating rhythm

1. Watchtower produces the morning change brief.
2. Case Lead triages: ignore, monitor, update or propose a new case.
3. Research sprint collects, preserves and structures sources.
4. Claim Compiler and Linker produce proposals.
5. Skeptic and Red Reviewer challenge consequential claims.
6. Legal, privacy and harm review occurs before publication.
7. Decisions, corrections and monitoring changes enter the audit log.

## Definition of done

A material claim is done only when it has precise wording, evidence status, source anchor, contradiction review, identity confidence, limitations, human approval, harm review and correction path.

A case is done only when its question is answered or responsibly left unresolved, all consequential claims are reproducible, alternatives are shown, public language is understandable, exports agree and monitoring remains active.
