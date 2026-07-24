# SafeTrace v1.5 — Auditable Agent Task Queue

**Victim-centred. Evidence-led. Human-reviewed. Germany first.**

> Empathy for every victim. Evidence for every claim. Due process for every accused. Accountability for every proven crime.

SafeTrace helps citizens and qualified investigators understand fragmented public records without turning correlations, allegations or AI output into automated accusations.

## Public portal

**https://mikelninh.github.io/digital-democracy-studio/safetrace/**

## Shipped stack

- **v0.3–v1.0** — source snapshots, political-money and arms records, review, monitoring, case packs, governance and controlled-pilot gates.
- **Case 004** — Germany-first Law Fairness Monitor.
- **v1.2** — unified Case Charter and evidence model with Case 001–004 migrations.
- **v1.3** — reviewed Source Registry and tamper-evident Evidence Vault.
- **v1.4** — versioned Claim Ledger, dynamic review gates and visible corrections.
- **v1.5** — twelve bounded proposal workers, default-deny execution, replayable run receipts and adversarial evaluation gates.

## What v1.5 proves

- Every task fixes its purpose, tools, data-zone ceiling, schemas, model, prompt version, timeout, budget and human approver.
- Scout, Archivist, Reader, Linker, Chronologist, Claim Compiler, Skeptic, Quant, Legal Status, Guardian, Watchtower and Explainer have separate allowlists.
- Every completed run records input/output hashes, tools, cost, latency and a deterministic trace key.
- Every successful output starts as `awaiting_human`; a human may only accept it for further review, reject it or request changes.
- Unknown tools, forbidden actions, data-zone escalation, budget/timeout overruns and agents acting as reviewers are blocked.
- Consequential proposals require exact source anchors.
- False entity links, political attribution errors, missed contradictions, legal-status overstatement and harmful publication suggestions fail release-blocking Golden Cases.
- The release invariant is **zero autonomous approval, publication, contact, referral or guilt decisions**.

## Exact release status

**SafeTrace v1.5 is ready for deterministic public-source and synthetic agent workflow evaluation. It is not a production model orchestration service and is not authorised for real victim, witness or restricted partner data.**

## Core documents

- [Constitution](CONSTITUTION.md)
- [Investigation OS](INVESTIGATION_OS.md)
- [Release history](ROADMAP.md)
- [Roadmap v1.2–v10.0](FUTURE_ROADMAP.md)
- [v1.2 unified model](core/README.md)
- [v1.3 Evidence Vault](evidence_vault/README.md)
- [v1.4 Claim Ledger](claim_ledger/README.md)
- [v1.5 Agent Queue](agent_queue/README.md)

## Run the v1.5 gates

```bash
python -m pip install reportlab
python -m unittest discover -s safetrace/core/tests -v
python -m safetrace.core.migration_report --root safetrace --output safetrace/core/migration-report.json
python -m unittest discover -s safetrace/evidence_vault/tests -v
python -m safetrace.evidence_vault.build_release_artifacts --safetrace-root safetrace --output-root safetrace/evidence_vault/artifacts
python -m unittest discover -s safetrace/claim_ledger/tests -v
python -m safetrace.claim_ledger.build_release_artifacts --safetrace-root safetrace --output-root safetrace/claim_ledger/artifacts
python -m unittest discover -s safetrace/agent_queue/tests -v
python -m safetrace.agent_queue.build_release_artifacts --output-root safetrace/agent_queue/artifacts
python -m safetrace.v1.cli --root . --output safetrace/v1/status.json
```

## Next engineering milestone

**v1.6 — Investigation Desk foundation:** one internal workflow surface for case intake, sources, claims, timelines, graphs, review queues, publications, corrections and agent proposals—without pretending authentication or restricted-data readiness already exists.

## Non-negotiable boundaries

- No hacking, credential testing, covert access, impersonation, harassment or doxxing.
- No autonomous guilt decisions, suspect lists, publication, contact or referrals.
- Facts, court findings, official allegations, analytical red flags and unresolved gaps remain separate.
- Private addresses and unnecessary personal data are not republished.
- Corrections remain visible.
