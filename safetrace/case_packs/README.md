# SafeTrace v0.8 — Investigator Case Packs

SafeTrace case packs turn a reviewed public case into two portable outputs:

- A human-readable PDF for investigators, editors, public officials and partner organisations.
- A machine-readable JSON document conforming to `schema.json`.

## First complete pack

**Case 001 — Germany's 14 Anti-Corruption Promises**

The public-redacted edition contains:

- Executive summary with the official four / six / four status totals.
- Dated chronology.
- Fourteen reviewed recommendation findings.
- Evidence state and source anchor for every finding.
- Responsible-institution navigation with an explicit editorial-mapping limitation.
- The unresolved March 2026 GRECO progress-report question.
- Official source manifest.
- Human review and redaction metadata.
- Explicit legal and evidentiary limitations.

It contains no victim, witness, private-address or other sensitive personal data.

## Generate

```bash
python -m pip install -r safetrace/case_packs/requirements.txt
python -m safetrace.case_packs.generate_case_pack \
  --data-dir safetrace/source_engine/data \
  --json-output artifacts/case-packs/SafeTrace_Case_001_v0.8.json \
  --pdf-output artifacts/case-packs/SafeTrace_Case_001_v0.8.pdf
```

## Test

```bash
python -m unittest discover -s safetrace/case_packs/tests -v
```

## Editions

### Public redacted

Designed for public transparency. It minimises personal data and excludes sensitive evidence.

### Restricted partner

Not yet enabled. A future partner edition should additionally include retained source bytes, SHA-256 receipts, access logs, redaction records, chain-of-custody events and partner-specific legal controls.

## Boundary

The case pack is an auditable research output, not a certified court exhibit, police report or legal conclusion. Investigators remain responsible for authentication, admissibility and procedural use.
