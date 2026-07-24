# SafeTrace v1.3 — Reviewed Source Registry and Evidence Vault

**Victim-centred. Evidence-led. Human-reviewed. Germany first.**

> Empathy for every victim. Evidence for every claim. Due process for every accused. Accountability for every proven crime.

SafeTrace helps citizens and qualified investigators understand fragmented public records without turning correlations, allegations or economic relationships into automated accusations.

## Public portal

**https://mikelninh.github.io/digital-democracy-studio/safetrace/**

## What is implemented

- **v0.3 Source Engine** — official-source snapshots, parser versions and change detection.
- **v0.4 Political Money Graph** — provenance-first relationships without unsupported causal claims.
- **v0.5 Human Review Desk** — contradictions, reviewer decisions, legal and right-of-reply gates.
- **v0.6 Arms & Influence Monitor** — authority, procurement, benefit, oversight and stage distinctions.
- **v0.7 Monitoring & Alerts** — proposals that cannot alter public status without approval.
- **v0.8 Investigator Case Packs** — public-redacted PDF and machine-readable JSON exports.
- **v0.9 Governance** — default-deny roles, tamper-evident audit records, threat model and incident response.
- **v1.0 Controlled Pilot Framework** — measurable safety and impact gates.
- **Case 004 Law Fairness Monitor** — sourced distributional analysis with political attribution.
- **v1.2 Unified Evidence Foundation** — Case Charter, common evidence model, data zones and migrations for Cases 001–004.
- **v1.3 Source Registry and Evidence Vault** — reviewed source catalogue, content-addressed originals, receipt chains, transformation manifests, health alerts, retention controls and verified recovery.

## What v1.3 proves

The release gate builds evidence instead of relying on a claim that storage is safe:

1. Existing Case 001–004 source records bootstrap a reviewed central registry.
2. Original bytes are stored under their SHA-256 hash and cannot be silently overwritten.
3. Every acquisition records registry revision, connector/parser version, raw and normalized hashes and the previous receipt hash.
4. Material changes, moved sources, unavailable sources and unexpected content types become distinct human-review alerts.
5. Parsing, extraction, redaction and export produce explicit transformation manifests; redaction and export require named human approval.
6. Original source objects cannot be deleted through the derived-object workflow.
7. Derived deletion requires a reason, approver and visible tombstone.
8. Backups enumerate every path, hash and byte length; restore verifies every entry before acceptance.

## Exact release status

**SafeTrace v1.3 is ready for reviewed public-source and synthetic investigation workflows. It is not authorised for real victim, witness or restricted partner data.**

A live pilot remains blocked until a qualified partner, production authentication and encryption, independent security assessment, partner-specific privacy documentation, qualified legal/editorial approval and observed partner measurements exist.

## Investigation OS documents

- [SafeTrace Constitution](CONSTITUTION.md)
- [Investigation OS operating model](INVESTIGATION_OS.md)
- [Release history](ROADMAP.md)
- [Roadmap v1.2–v10.0](FUTURE_ROADMAP.md)
- [Unified v1.2 model](core/README.md)
- [v1.3 Evidence Vault](evidence_vault/README.md)

## Run the release gates

```bash
python -m pip install reportlab
python -m unittest discover -s safetrace/core/tests -v
python -m safetrace.core.schema --check safetrace/core/schemas/safetrace-core-1.2.schema.json
python -m safetrace.core.migration_report --root safetrace --output safetrace/core/migration-report.json
python -m unittest discover -s safetrace/evidence_vault/tests -v
python -m safetrace.evidence_vault.contracts --check safetrace/evidence_vault/schemas/evidence-vault-contracts-1.3.json
python -m safetrace.evidence_vault.build_release_artifacts --safetrace-root safetrace --output-root safetrace/evidence_vault/artifacts
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

**v1.4 — Claim Ledger 2.0:** one authoritative review and correction workflow across every case, anchored exclusively to Source Registry and Evidence Vault records.

## Non-negotiable boundaries

- No hacking, credential testing, covert access, impersonation, harassment or doxxing.
- No automated guilt decisions, public suspect lists, publication or referrals.
- Every material claim keeps its source, evidence state and review trail.
- Facts, court findings, official allegations, analytical red flags and unresolved gaps remain separate.
- Private addresses and unnecessary personal data are not republished.
- Corrections remain visible.

## Career positioning

> **AI Engineer for Public-Interest Investigations** — building evidence-grounded systems that structure unorganised records, preserve provenance, expose accountability gaps and help human investigators produce reviewable conclusions.
