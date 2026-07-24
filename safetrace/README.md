# SafeTrace v1.7 — Case 004 Technical Reference Workflow

**Victim-centred. Evidence-led. Human-reviewed. Germany first.**

> Empathy for every victim. Evidence for every claim. Due process for every accused. Accountability for every proven crime.

SafeTrace helps citizens and qualified investigators understand fragmented public records without turning correlations, allegations or AI output into automated accusations.

## Public portal

**https://mikelninh.github.io/digital-democracy-studio/safetrace/**

## Shipped stack

- **v0.3–v1.0** — public investigation prototype and controlled-pilot gates.
- **v1.2** — unified Case Charter and evidence model.
- **v1.3** — Source Registry and tamper-evident Evidence Vault.
- **v1.4** — Claim Ledger, review gates and visible corrections.
- **v1.5** — twelve bounded proposal workers and adversarial evaluations.
- **v1.6** — role-controlled Investigation Desk and audit trail.
- **v1.7** — Case 004 technical reference flow with graph, timeline, reviewed claims, agent proposals, JSON/PDF, monitoring, benchmark and comprehension instruments.

## What v1.7 proves

- The real Case 004 repository dataset contains 11 source records, 5 measures and 5 claim tests.
- All source records, measures, affected groups, impact relationships and claims can be represented in the Investigation Desk.
- All five claim tests receive independent human consistency review.
- Skeptic, Quant, Legal Status and Guardian outputs remain proposals accepted only for human review.
- The complete workflow generates all eleven Desk views and a valid audit chain.
- A machine-readable JSON reference pack, human-readable PDF and monitoring manifest are generated.
- The controlled operation-count benchmark exceeds the 30% fixture target.
- An eight-question comprehension instrument covers facts, forecasts, legal status, attribution, nominal/real effects, causation and value judgments.

## Exact release status

**SafeTrace v1.7 completes the deterministic technical reference workflow. It does not authorise a newly verified Case 004 publication.**

Current honest blockers:

- retained original source bytes: **0 of 11**;
- observed human workflow-time study: **not completed**;
- external citizen-comprehension participants: **0**;
- real partner impact claimed: **no**.

The existing Gesetzes-Fairness page remains an editorial legacy output. The v1.7 reference package is not a substitute for immutable original-source backfill and renewed review.

## Core documents

- [Constitution](CONSTITUTION.md)
- [Investigation OS](INVESTIGATION_OS.md)
- [Release history](ROADMAP.md)
- [Roadmap v1.2–v10.0](FUTURE_ROADMAP.md)
- [v1.2 unified model](core/README.md)
- [v1.3 Evidence Vault](evidence_vault/README.md)
- [v1.4 Claim Ledger](claim_ledger/README.md)
- [v1.5 Agent Queue](agent_queue/README.md)
- [v1.6 Investigation Desk](investigation_desk/README.md)
- [v1.7 Case 004 reference](case_004_reference/README.md)

## Run the v1.7 gates

```bash
python -m pip install reportlab
python -m unittest discover -s safetrace/case_004_reference/tests -v
python -m safetrace.case_004_reference.contracts --write safetrace/case_004_reference/artifacts/case-004-reference-contracts-1.7.json
python -m safetrace.case_004_reference.build_reference --safetrace-root safetrace --output-root safetrace/case_004_reference/artifacts
python -m safetrace.v1.cli --root . --output safetrace/v1/status.json
```

## Next engineering milestone

**v1.8 — Independent review readiness:** source-byte backfill tooling, review packets, methodology/security/legal review checklists and an externally executable comprehension and workflow-study protocol.

## Non-negotiable boundaries

- No hacking, credential testing, covert access, impersonation, harassment or doxxing.
- No autonomous guilt decisions, suspect lists, publication, contact or referrals.
- Facts, court findings, official allegations, analytical red flags and unresolved gaps remain separate.
- Private addresses and unnecessary personal data are not republished.
- Corrections remain visible.
