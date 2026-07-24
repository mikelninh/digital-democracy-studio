# SafeTrace Future Roadmap — v1.2 to v10.0

This roadmap describes capability maturity, not permission to investigate more people or handle more sensitive data. Every stage inherits the SafeTrace Constitution and may be paused when evidence, privacy, security, legal or governance controls are insufficient.

## Guiding sequence

1. Standardise the evidence model.
2. Make one small team reliable.
3. Prove usefulness with one qualified partner.
4. Harden a single-organisation deployment.
5. Enable carefully controlled collaboration.
6. Standardise interoperability.
7. Expand jurisdictions only with local expertise.
8. Build durable public infrastructure and independent governance.

---

# Phase I — Investigation OS foundation

## v1.2 — Constitution, Case Charter and Unified Evidence Model

### Build

- Adopt `CONSTITUTION.md` as the governing product policy.
- Define JSON schemas and Python models for Case, Source, Snapshot, Entity, Relationship, Event, Claim, Evidence, Review, Publication, Correction and AgentTask.
- Add a Case Acceptance Wizard and machine-readable Case Charter.
- Add source hierarchy and evidence-status dictionaries.
- Define data zones and field-level sensitivity labels.
- Create schema migrations and compatibility tests for existing modules.

### Exit criteria

- All existing SafeTrace cases can be represented without losing provenance or review information.
- Every new case has a bounded question, owner, public-interest rationale, risk assessment and prohibited methods.
- No material claim exists outside the unified Claim model.

## v1.3 — Source Registry and Evidence Vault

### Build

- Central source registry with authority, cadence, connector, parser and health state.
- Content-addressed source storage with SHA-256 receipts.
- Transformation and redaction manifests.
- Restore tests, retention rules and deletion workflow.
- Dead-link, moved-source and parser-drift alerts.
- Reproducible source bundles for approved public cases.

### Exit criteria

- A reviewer can reproduce a case from retained source records.
- Original records and transformations are distinguishable.
- Backup restoration and deletion procedures pass tests.

## v1.4 — Claim Ledger and Review Desk 2.0

### Build

- One claim ledger across every case type.
- Queues for entity review, evidence review, red team, legal review, right of reply, publication and correction.
- Supporting, contradicting and contextual evidence displayed together.
- Required reviewer separation for sensitive claims.
- Public correction and version history.

### Exit criteria

- No consequential claim can bypass required reviews.
- Contradictory evidence cannot be silently removed.
- Every publication is generated from approved Claim versions.

## v1.5 — Agent Task Queue and Evaluation Harness

### Build

- Bounded AgentTask schema with purpose, permitted tools, data-zone limit, inputs, outputs, model, prompt version, budget and approver.
- Agents: Scout, Archivist, Reader, Linker, Chronologist, Claim Compiler, Skeptic, Quant, Legal Status, Guardian, Watchtower and Explainer.
- Golden evaluation datasets for extraction, entity resolution, attribution, contradiction discovery and harmful-output prevention.
- Replayable agent runs and cost/latency tracking.
- Default-deny tool permissions.

### Exit criteria

- Every agent run is reproducible and auditable.
- Agent output is treated as a proposal, never an approved fact.
- Safety and quality regressions fail CI.

## v1.6 — Internal Investigation Desk Alpha

### Build

- A single authenticated workspace with Inbox, Cases, Sources, Claims, Graph, Timeline, Review, Publish and Corrections.
- Role-based views and least-privilege permissions.
- Search across retained public records and approved internal notes.
- Task assignment, comments, reviewer decisions and audit timeline.
- Public portal remains physically and logically separated.

### Exit criteria

- A small team can complete one public-record case without using disconnected spreadsheets or chat logs as the system of record.
- All important decisions appear in the audit trail.

## v1.7 — End-to-End Reference Case

### Build

- Use Case 004, the German Law Fairness Monitor, as the reference implementation.
- Complete ingestion, claim ledger, political attribution, household scenarios, red-team review, public explanation, PDF/JSON export and monitoring.
- Run citizen-comprehension tests.
- Compare manual and SafeTrace-assisted review time.

### Exit criteria

- 100% material-claim provenance and human review.
- At least 30% workflow-time reduction in a controlled internal test.
- Citizens can distinguish enacted facts, forecasts, political attribution and value judgments.

## v1.8 — External Expert Review

### Build

- Review by an investigative journalist, privacy professional, qualified lawyer, security specialist and domain expert.
- Threat-model workshop and tabletop incident exercise.
- Accessibility and comprehension testing.
- Publish findings and remediation status where safe.

### Exit criteria

- No unresolved critical security or publication-risk finding.
- Documented decision on which data zones remain disabled.

## v1.9 — Partner Pilot Environment

### Build

- Isolated tenant for one qualified partner.
- Production authentication, encryption, secret management, access review and backups.
- Partner-specific DPIA/lawful basis, retention, deletion, roles and escalation.
- Training, operating procedure and pilot measurement plan.
- Zone 3 remains disabled unless explicitly approved.

### Exit criteria

- Written go/no-go approval from security, privacy, legal/editorial and partner leads.

---

# Phase II — Controlled real-world validation

## v2.0 — Qualified Partner Pilot

### Build

- Run one narrowly scoped case workflow with one qualified organisation.
- Measure time, evidence completeness, reviewer accuracy, false links, correction rate, comprehension and incidents.
- Compare against the partner’s baseline process.
- Publish a safe retrospective and expansion decision.

### Exit criteria

- 100% source coverage and human approval for material publication.
- Zero autonomous guilt decisions.
- Zero serious privacy or security incidents.
- False entity links do not increase.
- Meaningful partner workflow improvement and explicit desire to continue.

## v2.1 — Team Operations

- Case portfolios, workload management and reviewer availability.
- Structured handovers and absence coverage.
- Conflict-of-interest declarations per case.
- Service-level targets for urgent corrections and safety incidents.

## v2.2 — Connector Platform

- Tested connectors for Bundestag, Bundesrat, federal ministries, courts, GRECO/OECD, Lobby Register, party donations, procurement and company disclosures.
- Connector contracts, fixtures and health dashboards.
- Manual import remains available when automation is unreliable.

## v2.3 — Evidence Search and Retrieval

- Hybrid lexical/semantic search with strict source citations.
- Query logs, access rules and reproducibility.
- No model-generated answer without source-backed retrieval.

## v2.4 — Graph and Timeline Workbench

- Versioned entity identities and relationship evidence.
- Confidence calibrated against reviewed benchmarks.
- Side-by-side source inspection and alternative graph hypotheses.

## v2.5 — Law Fairness Engine

- Transparent household scenarios and fiscal-distribution analysis.
- Distinguish direct effects, behavioural assumptions and measured outcomes.
- Versioned rules and reproducible calculations.
- No single ideological fairness score.

## v2.6 — Political Money Explorer Production Beta

- Reliable donation and lobbying imports.
- Entity resolution review queue.
- Meeting, legislative and contract timelines.
- Persistent warning that documented sequence is not proven causation.

## v2.7 — Arms and Conflict Accountability Protocol

- Decision-chain model from budget to procurement, export, delivery, end-use evidence and legal assessment.
- Conflict-sensitive publication review.
- No live tactical information or exposure of vulnerable people.

## v2.8 — Public Comprehension and Accessibility

- Plain-language, multilingual and accessible public pages.
- Comprehension tests for evidence status and limitations.
- Public feedback and correction intake without open sensitive-evidence uploads.

## v2.9 — Operational Reliability

- Observability, runbooks, recovery targets, load tests, dependency inventory and vulnerability management.
- Quarterly access reviews and incident exercises.

---

# Phase III — Production-grade single-organisation system

## v3.0 — SafeTrace Production Platform

A production-ready deployment for one qualified organisation or tightly governed internal team.

### Required capabilities

- Stable unified evidence model and migration policy.
- Strong authentication, tenant and role controls.
- Encrypted evidence storage and tested recovery.
- Complete auditability of agents and humans.
- Reliable connectors and monitoring.
- Formal publication, correction and incident procedures.
- Independent security assessment.
- Demonstrated real-world usefulness across multiple bounded cases.

### Explicit boundary

v3.0 is not a mass-surveillance platform, automated law-enforcement system or public accusation engine.

---

# Phase IV — Controlled collaboration

## v4.0 — Federated Partner Collaboration

### Goal

Allow qualified organisations to collaborate without creating one uncontrolled central evidence pool.

### Build

- Strong tenant isolation.
- Case-level sharing agreements and purpose restrictions.
- Encrypted, revocable evidence sharing.
- Shared claims with independent reviewer decisions.
- Provenance preserved across organisational boundaries.
- Partner trust registry and incident coordination.

### Exit criteria

- A partner can share only explicitly approved records and revoke future access.
- Cross-tenant access tests and independent assessment pass.

## v5.0 — Open Evidence Interoperability Standard

### Goal

Make trustworthy evidence packages portable between approved tools and institutions.

### Build

- Published schemas for source receipts, claims, reviews, corrections and case packs.
- SDKs, command-line validation and conformance tests.
- Signed exports and verification tools.
- Read-only APIs and carefully scoped MCP tools for approved public data.
- Import/export mappings for journalism, research and civic-tech systems.

### Boundary

Interoperability never removes the receiving organisation’s duty to verify evidence, lawfulness and publication risk.

---

# Phase V — International and ecosystem maturity

## v6.0 — Multilingual and Cross-Jurisdiction Packs

### Build

- Jurisdiction modules written with local experts.
- Source hierarchies, legal-status vocabularies and publication rules per jurisdiction.
- Multilingual extraction evaluations and human translation review.
- Conflict-sensitive and human-rights investigation protocols.

### Exit criteria

- No jurisdiction launches without local legal/editorial expertise and evaluation data.

## v7.0 — Public-Interest Investigation Network

### Build

- Partner directory and certified deployment profiles.
- Shared public-source connector commons.
- Training curriculum for researchers and reviewers.
- Independent ethics, security and methodology advisory board.
- Public aggregate impact dashboard with correction and incident reporting.

### Boundary

Network growth is subordinate to partner quality, governance and safety.

---

# Phase VI — Durable civic infrastructure

## v8.0 — Resilient Evidence Infrastructure

### Build

- Multi-region encrypted archives for approved public records.
- Disaster recovery, cryptographic transparency logs and reproducible public snapshots.
- Long-term format preservation and dependency independence.
- Organisational continuity plans and funding reserves.

## v9.0 — Independent Evidence Commons

### Goal

Create durable public-interest infrastructure that does not depend on one founder, company, party or funder.

### Build

- Independent non-profit or public-benefit governance structure.
- Transparent funding and conflict policies.
- Community and expert representation.
- Grants for public-interest connectors, investigations and local-language modules.
- Open research datasets containing only legally and ethically publishable material.

## v10.0 — Accountable Global Public Infrastructure

### Vision

SafeTrace becomes a mature, independently governed public-interest evidence infrastructure used by qualified journalists, researchers, civil-society organisations and public institutions across jurisdictions.

### v10.0 means

- proven positive impact across diverse, independently evaluated workflows;
- public and partner trust earned through visible corrections and incident accountability;
- interoperable evidence standards and reproducible public archives;
- strong local governance rather than one central worldview;
- sustainable funding without editorial capture;
- continuous independent security, legal, ethical and human-rights oversight;
- citizens can inspect how consequential public claims were sourced, challenged and corrected.

### v10.0 explicitly does not mean

- global surveillance;
- automated determination of guilt;
- secret scoring of people;
- unrestricted intelligence sharing;
- replacing courts, journalism, democratic institutions or human judgment.

---

# Release governance

A release requires:

1. documented user and public-interest need;
2. threat and harm assessment;
3. tests and evaluation results;
4. privacy and legal review proportional to the data;
5. human-operability and correction procedures;
6. truthful public release notes;
7. rollback or shutdown capability.

Features may move to a later version, but safeguards may not be deferred to one.
