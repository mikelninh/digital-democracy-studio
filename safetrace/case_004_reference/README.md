# SafeTrace v1.7 — Case 004 Technical Reference Workflow

This release runs the German Law Fairness Monitor through the Investigation Desk as a complete **technical reference case**.

It does not turn the existing editorial dataset into freshly verified source evidence. The repository currently contains eleven reviewed source records but no retained original source bytes for Case 004 in the Evidence Vault.

## Implemented reference flow

- loads the reviewed Case 004 dataset;
- registers 11 sources in the Desk;
- creates timeline events for 5 policy measures;
- creates affected-group entities and impact relationships;
- creates 5 versioned claim-test records with complete source-reference coverage;
- completes an independent human consistency review for all 5 claims;
- runs Skeptic, Quant, Legal Status and Guardian proposals into human review;
- builds all 11 Investigation Desk views;
- verifies the complete Desk audit chain;
- generates a machine-readable JSON reference pack;
- generates a human-readable PDF reference pack;
- creates a source monitoring manifest;
- creates a citizen-comprehension test instrument;
- runs a deterministic workflow-operation benchmark.

## What remains blocked

### Original evidence backfill

- reviewed source records: **11**
- retained original source bytes: **0**
- new public publication allowed: **no**

The technical reference pack retains source URLs and the SHA-256 hash of the reviewed repository dataset. It is not a substitute for immutable copies of the underlying official records.

### Real workflow impact

The benchmark compares deterministic workflow-operation counts and exceeds the 30% target in the fixture. It is not observed staff time and is not claimed as partner impact.

### Citizen comprehension

The eight-question instrument covers:

- facts versus forecasts;
- enacted versus in-force status;
- political attribution;
- nominal versus real change;
- direct versus indirect effects;
- association versus causation;
- bounded verdicts;
- evidence versus value judgment.

No external participant has completed the instrument yet.

## Run locally

```bash
python -m pip install reportlab
python -m unittest discover -s safetrace/case_004_reference/tests -v
python -m safetrace.case_004_reference.contracts --write safetrace/case_004_reference/artifacts/case-004-reference-contracts-1.7.json
python -m safetrace.case_004_reference.build_reference --safetrace-root safetrace --output-root safetrace/case_004_reference/artifacts
```

## Truthful status

v1.7 completes the deterministic technical reference workflow. A newly verified public Case 004 release remains blocked until original source bytes are retained and re-reviewed. Real time savings and citizen comprehension remain unmeasured external outcomes.
