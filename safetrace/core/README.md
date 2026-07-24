# SafeTrace v1.2 — Unified Evidence Foundation

SafeTrace v1.2 turns the existing investigation modules into one coherent, versioned system of record. It does **not** expand the live-data boundary: public and synthetic work remain allowed; restricted partner or victim-sensitive work remains blocked.

## What is implemented

- A machine-readable **Case Charter** governed by `safetrace/CONSTITUTION.md`.
- A deterministic **Case Acceptance Wizard** with explicit blockers, warnings and required reviewers.
- Unified records for:
  - `Case`
  - `Source`
  - `Snapshot`
  - `Entity`
  - `Relationship`
  - `Event`
  - `Claim`
  - `Evidence`
  - `Review`
  - `Publication`
  - `Correction`
  - `AgentTask`
- Controlled vocabularies for evidence state, source rank, legal status, relationship type, data zone and sensitivity.
- Cross-reference validation and publication gates.
- A committed JSON Schema generated from code and checked for drift.
- Conservative schema-compatibility checks for later releases.
- Adapters for the Source Engine, Political Money Graph, Review Desk, Arms Monitor, Monitoring proposals, Case Packs and Law Fairness Monitor.
- A migration report that loads the actual Case 001–004 repository data and validates each case against `safetrace.core/1.2`.

## Core safety properties

The model rejects:

- material claims without supporting, anchored evidence;
- relationships or events with missing evidence references;
- publication without recorded human approval;
- sensitive publication without legal review and right-of-reply handling;
- ignored contradicting evidence;
- hidden corrections;
- agent tasks that request publishing, covert contact, impersonation, hacking, facial identification or automated referral;
- agent tasks that exceed the Case Charter's data-zone ceiling;
- Case Charters that omit the baseline prohibited methods.

## Run

```bash
python -m unittest discover -s safetrace/core/tests -v
python -m safetrace.core.schema --check safetrace/core/schemas/safetrace-core-1.2.schema.json
python -m safetrace.core.migration_report \
  --root safetrace \
  --output artifacts/core/migration-report.json
```

Create a Case Charter template:

```bash
python -m safetrace.core.charter --template --case-id case-005
```

Evaluate a charter:

```bash
python -m safetrace.core.charter \
  --evaluate safetrace/core/examples/case_charter.example.json
```

## Version policy

`SCHEMA_VERSION` is `safetrace.core/1.2`.

Future releases must:

1. preserve old properties and enum values unless a deliberate major migration is approved;
2. avoid adding required fields in a backward-compatible minor release;
3. regenerate the committed schema through `safetrace.core.schema`;
4. run the existing-case migration report;
5. document and test every adapter or migration.

## Boundary

This foundation is suitable for reviewed public records and synthetic evaluation. It is not permission to accept real victim evidence, witness data, unrestricted personal data or production partner operations.
