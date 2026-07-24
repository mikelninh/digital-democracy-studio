# SafeTrace v1.2 — Unified Evidence Foundation

**Victim-centred. Evidence-led. Human-reviewed. Germany first.**

> Empathy for every victim. Evidence for every claim. Due process for every accused. Accountability for every proven crime.

SafeTrace helps citizens and qualified investigators understand fragmented public records without turning correlations, allegations or economic relationships into automated accusations.

## Public portal

**https://mikelninh.github.io/digital-democracy-studio/safetrace/**

## What is implemented

- **v0.3 Source Engine** — official-source snapshots, SHA-256 receipts, parser versions and change detection.
- **v0.4 Political Money Graph** — provenance-first relationships without unsupported causal claims.
- **v0.5 Human Review Desk** — evidence roles, contradictions, reviewer decisions, legal and right-of-reply gates.
- **v0.6 Arms & Influence Monitor** — authority, procurement, benefit, oversight and stage distinctions.
- **v0.7 Monitoring & Alerts** — change proposals that cannot alter public status without approval.
- **v0.8 Investigator Case Packs** — public-redacted PDF and machine-readable JSON exports.
- **v0.9 Governance** — default-deny roles, tamper-evident audit records, threat model and incident response.
- **v1.0 Controlled Pilot Framework** — measurable safety and impact gates.
- **Case 004 Law Fairness Monitor** — sourced distributional analysis with political attribution.
- **v1.2 Unified Evidence Foundation** — Case Charter, shared evidence model, controlled vocabularies, data zones, compatibility checks and migrations for Cases 001–004.

## v1.2 foundation

The Investigation OS now uses one shared model for:

`Case`, `Source`, `Snapshot`, `Entity`, `Relationship`, `Event`, `Claim`, `Evidence`, `Review`, `Publication`, `Correction`, and `AgentTask`.

The release gate verifies that:

- every new case has a bounded, approved Case Charter;
- material claims have anchored supporting evidence;
- human review remains required before publication;
- sensitive claims retain legal and right-of-reply gates;
- agent tasks cannot exceed their authorised tools or data zone;
- schema drift and backward-incompatible changes are detected;
- existing Cases 001–004 migrate into the unified model.

## Exact release status

**SafeTrace v1.2 is ready for public and synthetic investigation workflows. It is not authorised for real victim data or restricted partner deployment.**

A live pilot remains blocked until there is a qualified partner, production authentication and encryption, independent security assessment, partner-specific privacy documentation, qualified legal/editorial approval and observed partner measurements.

## Investigation OS documents

- [SafeTrace Constitution](CONSTITUTION.md)
- [Investigation OS operating model](INVESTIGATION_OS.md)
- [Release history](ROADMAP.md)
- [Roadmap v1.2–v10.0](FUTURE_ROADMAP.md)
- [v1.2 core model](core/README.md)

## Run the release gates

```bash
python -m pip install reportlab
python -m unittest discover -s safetrace/core/tests -v
python -m safetrace.core.schema --check safetrace/core/schemas/safetrace-core-1.2.schema.json
python -m safetrace.core.migration_report --root safetrace --output safetrace/core/migration-report.json
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

## Next engineering milestone

**v1.3: Source Registry and Evidence Vault** — a content-addressed, reproducible system of record for original sources, snapshots, transformations, retention and recovery.

## Non-negotiable boundaries

- No hacking, credential testing, covert access, impersonation, harassment or doxxing.
- No automated guilt decisions, public suspect lists, publication or referrals.
- Every material claim keeps its source, evidence state and review trail.
- Facts, court findings, official allegations, analytical red flags and unresolved gaps remain separate.
- Private addresses and unnecessary personal data are not republished.
- Corrections remain visible.

## Career positioning

> **AI Engineer for Public-Interest Investigations** — building evidence-grounded systems that structure unorganised records, preserve provenance, expose accountability gaps and help human investigators produce reviewable conclusions.
