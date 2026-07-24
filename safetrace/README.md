# SafeTrace v1.0 — Pilot-Ready Public-Interest Investigation Infrastructure

**Victim-centred. Evidence-led. Human-reviewed. Germany first.**

> Empathy for every victim. Evidence for every claim. Due process for every accused. Accountability for every proven crime.

SafeTrace helps citizens and qualified investigators understand fragmented public records without turning correlations, allegations or economic relationships into automated accusations.

## Public portal

**https://mikelninh.github.io/digital-democracy-studio/safetrace/**

## What is implemented

- **v0.3 Source Engine** — official-source snapshots, SHA-256 receipts, parser versions and change detection.
- **v0.4 Political Money Graph** — provenance-first relationship records that never treat sequence as causation.
- **v0.5 Human Review Desk** — supporting and contradicting evidence, reviewer decisions, legal and right-of-reply gates.
- **v0.6 Arms & Influence Monitor** — structured authority, procurement, benefit, oversight and human-consequence records.
- **v0.7 Monitoring & Alerts** — material-change and missed-deadline proposals that cannot alter public status without approval.
- **v0.8 Investigator Case Packs** — public-redacted PDF and machine-readable JSON exports.
- **v0.9 Governance** — default-deny roles, tamper-evident audit records, threat model, incident response and executable readiness controls.
- **v1.0 Controlled Pilot Framework** — measurable quality, safety and impact gates plus a partner operating template.
- **Case 004 Law Fairness Monitor** — sourced distributional analysis with political attribution and no ideological black-box score.

## Exact release status

**SafeTrace v1.0 is pilot-ready for public and synthetic evaluation. It is not authorised for real victim data or restricted partner deployment.**

The synthetic benchmark is transparent test data, not claimed real-world impact. A live pilot remains blocked until there is:

- a named qualified partner and narrowly scoped case type;
- production authentication, encryption and secrets management;
- independent security assessment and remediation;
- partner-specific privacy documentation, lawful basis and retention controls;
- qualified legal/editorial approval;
- observed partner measurements replacing synthetic fixtures.

## Investigation OS foundation

The next build sequence is now documented as an operating system rather than a collection of disconnected features:

- [SafeTrace Constitution](CONSTITUTION.md)
- [Investigation OS operating model](INVESTIGATION_OS.md)
- [Release history](ROADMAP.md)
- [Future roadmap v1.2–v10.0](FUTURE_ROADMAP.md)

The immediate engineering target is **v1.2: Case Charter plus a unified evidence model**. Long-term stages proceed through controlled partner validation, production hardening, federated collaboration, open evidence standards, cross-jurisdiction packs and independently governed public infrastructure.

## Non-negotiable boundaries

- No hacking, credential testing, covert access, impersonation, harassment or doxxing.
- No automated guilt decisions, public suspect lists, publication or referrals.
- Every material claim keeps its source, evidence state and review trail.
- Facts, court findings, official allegations, analytical red flags and unresolved gaps remain separate.
- Private addresses and unnecessary personal data are not republished.
- Corrections remain visible.

## Run the release gates

```bash
python -m pip install reportlab
python -m unittest discover -s safetrace/source_engine/tests -v
python -m unittest discover -s safetrace/political_money/tests -v
python -m unittest discover -s safetrace/review_desk/tests -v
python -m unittest discover -s safetrace/arms_monitor/tests -v
python -m unittest discover -s safetrace/monitoring/tests -v
python -m unittest discover -s safetrace/case_packs/tests -v
python -m unittest discover -s safetrace/law_fairness/tests -v
python -m unittest discover -s safetrace/governance/tests -v
python -m unittest discover -s safetrace/pilot/tests -v
python -m unittest discover -s safetrace/v1/tests -v
python -m safetrace.v1.cli --root . --output safetrace/v1/status.json
```

## Career positioning

> **AI Engineer for Public-Interest Investigations** — building evidence-grounded systems that structure unorganised records, preserve provenance, expose accountability gaps and help human investigators produce reviewable conclusions.
