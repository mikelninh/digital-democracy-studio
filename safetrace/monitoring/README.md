# SafeTrace v0.7 — Monitoring & Alerts

SafeTrace monitoring reduces information overload without giving automation authority to rewrite the public record.

## Monitoring flow

1. Fetch and retain the official source.
2. Compare exact and normalised SHA-256 hashes.
3. Create a change proposal with the affected source and possible claims.
4. Require a human reviewer to inspect the diff.
5. Publish only an approved update with a visible changelog.

A detected change has `public_effect: none_until_human_approval`.

## What is configured

Six official sources across:

- Germany's GRECO and OECD integrity status.
- Bundestag large-donation disclosures.
- Lobby Register entry R005553.
- German arms-export authorisations.
- MEKO A-200 DEU procurement updates.

The first deadline monitor tracks GRECO's request for a German progress report by 31 March 2026. The public absence of a newer report is recorded as an unresolved publication/status gap, not proof that Germany did not submit one.

## Change semantics

- A changed raw hash with the same normalised hash may be formatting noise.
- A changed normalised hash creates a pending human-review proposal.
- A missed unresolved deadline creates a pending alert proposal.
- No pending proposal can modify public status.

## Build and test

```bash
python -m unittest discover -s safetrace/monitoring/tests -v
python -m safetrace.monitoring.build_status
```

## Operational limitation

GitHub Actions schedules are committed, but repository-side workflow execution and history must be independently verified. Cross-run source-state persistence is not yet production-grade; v0.9 must establish durable state, authentication and audit controls.
