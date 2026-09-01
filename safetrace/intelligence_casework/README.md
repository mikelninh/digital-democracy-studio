# SafeTrace Intelligence Casework

A portfolio-grade analyst workflow for corporate investigations, enhanced due diligence and evidence-first OSINT.

> **Synthetic training case. No real person or company is accused of wrongdoing.** The case is deliberately constructed to exercise the same reasoning problems that appear in real investigations while keeping the public demo safe and reproducible.

## The question

**Who controls the target company, what material risks are visible in the supplied record, and what should an analyst verify next?**

This module turns fragmented records into an analyst-defensible answer rather than an opaque risk score.

## Why this exists

The wider SafeTrace repository already has an Evidence Vault, Claim Ledger, Investigation Desk, review gates, source provenance and entity resolution. This casework layer composes those primitives into the artefact a business-intelligence or investigations team actually consumes:

1. a bounded client question;
2. a source map with authority/relevance/freshness grading;
3. resolved and unresolved identities;
4. a corporate ownership/control graph;
5. atomic claims with exact evidence and limitations;
6. contradiction and negative-evidence handling;
7. sanctions-screening triage that separates a fuzzy-name lead from a confirmed identity;
8. prioritised gaps and next investigative steps;
9. a concise written intelligence assessment; and
10. a human-review boundary for consequential conclusions.

## Case V-001 — Northstar Components

The synthetic case spans Germany, the UK, the UAE and Poland. It contains:

- a 70/30 target-company ownership split;
- a second-layer 60/40 ownership structure;
- a nominee shareholder that leaves part of beneficial ownership unresolved;
- a director-status contradiction between an official filing and an archived company page;
- a supplier agreement followed by a payment instruction to a different legal entity;
- a near-name sanctions-screening candidate that must **not** be collapsed into `SAME_AS` because date of birth and nationality conflict; and
- a bounded no-hit court-record result that is explicitly not treated as proof of absence.

The correct analytical output is deliberately nuanced: there are reasons for **enhanced due diligence**, but the evidence does not support an allegation of sanctions evasion, fraud or other wrongdoing.

## Entity-resolution evidence

The existing resolver has two intentionally separate evaluations:

- **40-case development benchmark:** precision 1.000, recall 1.000, F1 1.000 after inspecting and repairing baseline failures.
- **30-case frozen holdout:** precision 0.9231, recall 0.8571, F1 0.8889, accuracy 0.9000.

The holdout has three visible failures. Those failures stay visible because a credible investigation system needs to know when automation should defer to an analyst. The next unbiased resolver score requires a fresh holdout after any repair.

See:

- `../../zero-suffering-intelligence/entity-resolution/results-v11.json`
- `../../zero-suffering-intelligence/entity-resolution/results-holdout-v1.json`

## Analyst rules demonstrated

### Identity

- `SAME_AS` is consequential.
- Name similarity alone is not identity.
- Parent, subsidiary, brand, operating unit, nominee and historical group label remain distinct unless the evidence establishes otherwise.
- Conflicts and unresolved identity are represented, not silently normalised away.

### Sources

A simple source grade makes judgement inspectable:

- **Authority A:** authoritative public filing / court / regulator record.
- **Authority B:** supplied primary business record with provenance but not independently authoritative.
- **Authority C:** self-report, archive or other source requiring corroboration.

Authority is not truth. A high-authority source can be stale; a low-authority source can contain the clue that prompts a better search. Relevance and freshness are therefore graded separately.

### Risk language

The demo keeps these statements distinct:

- **fact:** supported by cited evidence;
- **contradiction:** two sources cannot both describe the same current state without explanation;
- **gap:** a material point is unresolved;
- **risk indicator:** a fact pattern worth verifying;
- **allegation:** a claim attributed to a source, not adopted as fact;
- **finding:** an analyst conclusion supported to the required standard.

An anomalous payment route is **not** automatically fraud. A sanctions-name hit is **not** automatically a sanctioned person. A nominee shareholder is **not** automatically illicit ownership.

## Files

- `data/case_v001.json` — complete structured case fixture.
- `ANALYST_MEMO_V001.md` — finished intelligence assessment.
- `index.html` — browser demo for rapid review.
- `validate_case.py` — deterministic quality gates for the case fixture.
- `tests/test_case_v001.py` — regression tests for the core analytical invariants.

## Run

From the repository root:

```bash
python safetrace/intelligence_casework/validate_case.py
python -m unittest safetrace.intelligence_casework.tests.test_case_v001 -v
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/safetrace/intelligence_casework/
```

## Definition of done

The proof is good enough to show an investigations team when a reviewer can answer, in under five minutes:

- What is the client question?
- What do we actually know?
- Which source supports each material statement?
- Which identities were merged, rejected or left unresolved, and why?
- What contradicts the leading assessment?
- What is a fact versus a risk indicator?
- What remains unknown?
- What is the highest-value next research action?
- Can I reproduce the conclusion without trusting the model?

If any of those answers is hidden behind an AI score, the proof is not finished.
