# SafeTrace v1.4 — Claim Ledger 2.0

**Victim-centred. Evidence-led. Human-reviewed. Germany first.**

> Empathy for every victim. Evidence for every claim. Due process for every accused. Accountability for every proven crime.

SafeTrace helps citizens and qualified investigators understand fragmented public records without turning correlations, allegations or economic relationships into automated accusations.

## Public portal

**https://mikelninh.github.io/digital-democracy-studio/safetrace/**

## What is implemented

- **v0.3–v1.0** — source snapshots, political-money and arms records, human review, monitoring, case packs, governance and pilot gates.
- **Case 004 Law Fairness Monitor** — sourced distributional analysis with political attribution.
- **v1.2 Unified Evidence Foundation** — Case Charter, shared evidence model, data zones and Case 001–004 migrations.
- **v1.3 Source Registry and Evidence Vault** — reviewed source catalogue, immutable originals, receipt chains, manifests, retention and verified recovery.
- **v1.4 Claim Ledger 2.0** — versioned claims, vault-backed evidence links, dynamic review gates, reviewer separation, contradiction handling, visible corrections and automatic publication invalidation.

## What v1.4 proves

- Material claims cannot publish without evidence, red-team and independent publication review.
- Identity-sensitive claims add an identity gate.
- Sensitive claims, allegations and material discussion of people add legal and right-of-reply gates.
- Contradicting evidence must be explicitly addressed by red-team review.
- Evidence links must match a Source Registry identity, Vault receipt, object hash and exact anchor.
- A corrected claim creates a new sequential version and makes publications using the superseded version `stale`.
- Existing Case 001–004 claims are preserved but receive `migrated_pending_evidence_backfill`; they are not automatically republished.

## Exact release status

**SafeTrace v1.4 is ready for vault-backed public-source and synthetic claim workflows. It is not authorised for real victim, witness or restricted partner data.**

Existing public cases remain visible as legacy outputs, but future Claim Ledger publication requires Evidence Vault backfill and the full review graph.

## Core documents

- [Constitution](CONSTITUTION.md)
- [Investigation OS](INVESTIGATION_OS.md)
- [Release history](ROADMAP.md)
- [Roadmap v1.2–v10.0](FUTURE_ROADMAP.md)
- [v1.2 unified model](core/README.md)
- [v1.3 Evidence Vault](evidence_vault/README.md)
- [v1.4 Claim Ledger](claim_ledger/README.md)

## Run the v1.4 gates

```bash
python -m pip install reportlab
python -m unittest discover -s safetrace/core/tests -v
python -m safetrace.core.migration_report --root safetrace --output safetrace/core/migration-report.json
python -m unittest discover -s safetrace/evidence_vault/tests -v
python -m safetrace.evidence_vault.build_release_artifacts --safetrace-root safetrace --output-root safetrace/evidence_vault/artifacts
python -m unittest discover -s safetrace/claim_ledger/tests -v
python -m safetrace.claim_ledger.contracts --write safetrace/claim_ledger/artifacts/claim-ledger-contracts-1.4.json
python -m safetrace.claim_ledger.build_release_artifacts --safetrace-root safetrace --output-root safetrace/claim_ledger/artifacts
python -m safetrace.v1.cli --root . --output safetrace/v1/status.json
```

## Next engineering milestone

**v1.5 — Auditable Agent Task Queue and evaluation harness:** bounded agents produce structured proposals into the Claim Ledger, never approved claims or autonomous publications.

## Non-negotiable boundaries

- No hacking, credential testing, covert access, impersonation, harassment or doxxing.
- No automated guilt decisions, public suspect lists, publication or referrals.
- Facts, court findings, official allegations, analytical red flags and unresolved gaps remain separate.
- Private addresses and unnecessary personal data are not republished.
- Corrections remain visible.
