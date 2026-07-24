# SafeTrace v1.6 — Internal Investigation Desk Foundation

**Victim-centred. Evidence-led. Human-reviewed. Germany first.**

> Empathy for every victim. Evidence for every claim. Due process for every accused. Accountability for every proven crime.

SafeTrace helps citizens and qualified investigators understand fragmented public records without turning correlations, allegations or AI output into automated accusations.

## Public portal

**https://mikelninh.github.io/digital-democracy-studio/safetrace/**

## Shipped stack

- **v0.3–v1.0** — public investigation prototype and controlled-pilot gates.
- **Case 004** — Germany-first Law Fairness Monitor.
- **v1.2** — unified Case Charter and evidence model.
- **v1.3** — reviewed Source Registry and tamper-evident Evidence Vault.
- **v1.4** — versioned Claim Ledger, review gates and visible corrections.
- **v1.5** — twelve bounded proposal workers and adversarial evaluations.
- **v1.6** — role-controlled Investigation Desk, public-export separation and hash-chained audit trail.

## What v1.6 proves

- Eleven internal views: Inbox, Cases, Sources, Claims, Graph, Timeline, Review, Publish, Corrections, Agents and Audit.
- Seven least-privilege roles: Intake Researcher, Investigator, Evidence Manager, Reviewer, Legal Reviewer, Publisher and Admin.
- Every action requires an authenticated session context, role permission and sufficient data-zone access.
- Record creators cannot perform final review.
- Publication requesters cannot approve their own publication.
- Agent proposals enter `awaiting_human` and can only be accepted for further review.
- Public export includes only approved public claims and excludes internal comments, team tasks and agent proposals.
- Corrections make an existing publication visibly `stale`.
- Consequential actions create a verifiable hash-chained audit trail.
- Chat and spreadsheets are explicitly not authoritative systems of record.

## Exact release status

**SafeTrace v1.6 is ready for deterministic public-source and synthetic internal workflow evaluation. The authorisation model uses synthetic authenticated sessions; production identity, MFA, session revocation, tenant isolation and restricted partner processing are not configured.**

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

## Run the v1.6 gates

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
python -m unittest discover -s safetrace/investigation_desk/tests -v
python -m safetrace.investigation_desk.build_release_artifacts --output-root safetrace/investigation_desk/artifacts
python -m safetrace.v1.cli --root . --output safetrace/v1/status.json
```

## Next engineering milestone

**v1.7 — Complete Case 004 reference workflow:** backfill official source bytes, run the Gesetzes-Fairness case through the Desk, create reviewed graph/timeline and public case pack, benchmark manual versus assisted work and test citizen comprehension.

## Non-negotiable boundaries

- No hacking, credential testing, covert access, impersonation, harassment or doxxing.
- No autonomous guilt decisions, suspect lists, publication, contact or referrals.
- Facts, court findings, official allegations, analytical red flags and unresolved gaps remain separate.
- Private addresses and unnecessary personal data are not republished.
- Corrections remain visible.
