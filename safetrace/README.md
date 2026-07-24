# SafeTrace v1.8 — Independent Review Readiness

**Victim-centred. Evidence-led. Human-reviewed. Germany first.**

> Empathy for every victim. Evidence for every claim. Due process for every accused. Accountability for every proven crime.

SafeTrace helps citizens and qualified investigators understand fragmented public records without turning correlations, allegations or AI output into automated accusations.

## Public portal

**https://mikelninh.github.io/digital-democracy-studio/safetrace/**

## Interactive test lab

**https://mikelninh.github.io/digital-democracy-studio/safetrace/role_simulator/**

The browser-local Role Simulator lets one person replay Cases 001–004 as:

- Citizen;
- Investigator;
- Evidence Manager;
- Skeptical Reviewer;
- Legal & Harm Reviewer;
- Publisher.

It supports role-filtered views, claims, sources, graph, timeline, bounded agents, review decisions, publication gates, comprehension checks and a local audit trail. It makes no network requests, publishes nothing and stores only local browser state.

## Shipped stack

- **v0.3–v1.0** — public investigation prototype and controlled-pilot gates.
- **v1.2** — unified Case Charter and evidence model.
- **v1.3** — Source Registry and tamper-evident Evidence Vault.
- **v1.4** — Claim Ledger, human review gates and visible corrections.
- **v1.5** — twelve bounded proposal workers and adversarial evaluations.
- **v1.6** — role-controlled Investigation Desk and verifiable audit trail.
- **v1.7** — complete Case 004 technical reference workflow without false re-certification.
- **v1.8** — hashed external-review packets, finding register, dry-run exercises, source-backfill plan and consent-based study protocols.
- **v1.8 Companion** — browser-local Role Simulator for six roles and four public/synthetic cases.

## What v1.8 proves

- Seven independent review disciplines are formally scoped: editorial, privacy, legal, security, domain, accessibility and public comprehension.
- Every review packet records exact artifact hashes, questions, expected findings, conflict declaration and go/no-go output.
- Every external review slot remains unassigned until a real reviewer identity exists.
- Critical and high blockers remain visible in a structured finding register.
- Three synthetic exercises test hostile source content, publication correction and evidence recovery procedures.
- Workflow and comprehension study protocols require consent, minimise collected data and define stopping rules.
- All eleven Case 004 sources have a controlled original-byte backfill plan requiring renewed human review.
- Backfill never triggers automatic publication.

## Exact release status

**SafeTrace v1.8 is ready to invite qualified independent reviewers. It has not been independently reviewed or externally approved.**

Current review state:

- external reviews completed: **0**;
- external approvals: **0**;
- conflict declarations received: **0**;
- unresolved critical findings: **at least 1**;
- partner identified: **no**;
- partner-pilot gate open: **no**;
- restricted-data gate open: **no**.

The Role Simulator demonstrates intended UX and authorisation boundaries. It is not production authentication, an operational investigation database or permission to process restricted data.

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
- [v1.8 Review Readiness](review_readiness/README.md)
- [Role Simulator](role_simulator/README.md)

## Run the v1.8 gates

```bash
python -m pip install reportlab
python -m unittest discover -s safetrace/review_readiness/tests -v
python -m safetrace.review_readiness.contracts --write safetrace/review_readiness/artifacts/review-readiness-contracts-1.8.json
python -m safetrace.review_readiness.build_review_pack --safetrace-root safetrace --output-root safetrace/review_readiness/artifacts
python -m unittest discover -s safetrace/role_simulator/tests -v
python -m safetrace.role_simulator.validate --root safetrace/role_simulator --output safetrace/role_simulator/artifacts/role-simulator-report.json
python -m safetrace.v1.cli --root . --output safetrace/v1/status.json
```

## Next engineering milestone

**v1.9 — Isolated pilot environment preparation** may proceed only after real external findings exist. It must not open restricted data merely because infrastructure code was written.

## Non-negotiable boundaries

- No hacking, credential testing, covert access, impersonation, harassment or doxxing.
- No autonomous guilt decisions, suspect lists, publication, contact or referrals.
- No fabricated reviewer identities, approvals, study results or partner impact.
- Facts, court findings, official allegations, analytical red flags and unresolved gaps remain separate.
- Private addresses and unnecessary personal data are not republished.
- Corrections remain visible.
