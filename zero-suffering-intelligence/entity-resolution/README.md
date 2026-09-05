# SafeTrace Entity Resolution

**Evidence-first identity resolution with an explicit human-review state.**

Entity resolution is consequential in investigations: a false merge can attach the wrong ownership, sanctions, payment or risk evidence to an entity. SafeTrace therefore treats `SAME_AS` as something to prove, not a fuzzy-name convenience.

## Decision contract

The v12 resolver returns one of three outcomes:

- `merge` — enough evidence for an automatic same-entity proposal;
- `separate` — enough evidence to keep identities distinct;
- `review` — plausible or conflicting evidence that should be resolved by an analyst rather than forced into yes/no.

Every decision also returns an evidence contract containing the normalised identity labels, legal forms, group markers, stable identifiers and address relationship used by the resolver.

## Why v12 exists

The previous v11 benchmark was deliberately kept honest.

After tuning on the 40-case development set, v11 scored perfectly there, but the first frozen 30-case holdout exposed three failures:

- two false separations (`Sprehe Unternehmensgruppe` / `Sprehe Gruppe`; `DMK GmbH` / `DMK G.m.b.H.`),
- one false merge (`DMK GmbH` / `DMK Group`).

That holdout remains untouched. Its published out-of-sample result is:

| Metric | v11 holdout-v1 |
|---|---:|
| Precision | 0.9231 |
| Recall | 0.8571 |
| F1 | 0.8889 |
| Accuracy | 0.9000 |

Once those failures were inspected, holdout-v1 could no longer be used as an unseen evaluation for a repaired resolver. v12 therefore uses a fresh frozen holdout-v2.

## v12 frozen holdout-v2

The fresh set contains **40 developer-authored cases** spanning punctuation, transliteration, typos, subsidiaries, holding/group identities, conflicting addresses, conflicting legal forms, stable identifiers and deliberately ambiguous pairs.

The first frozen evaluation produced:

| Metric | v12 holdout-v2 |
|---|---:|
| Auto-merge precision | **1.0000** |
| Merge recall, counting review as not auto-merged | **0.8947** |
| Merge F1 | **0.9444** |
| Automatic decision coverage | **0.8500** |
| Accuracy on automatically decided cases | **1.0000** |
| Review rate | **0.1500** |
| False automatic merges | **0** |
| False automatic separations | **0** |

The important result is not “100% accuracy”. The system **refused to auto-decide 6/40 ambiguous cases**. On the 34 cases it did decide automatically, there were no false merge/separate decisions in this frozen set.

That is the intended operating trade-off: prefer a visible `review` state over a confident identity error when evidence is insufficient.

## What the review cases teach us

The routed cases include:

- same base name but conflicting legal forms (`AG` vs `GmbH`, `BV` vs `NV`, `SARL` vs `SA`),
- translation-like near names without authoritative alias evidence,
- distinctive names with missing address corroboration,
- high character similarity without independent identity evidence.

These are exactly the cases where an analyst should inspect registry identifiers, temporal filings, addresses, directors or other authoritative evidence before asserting `SAME_AS`.

## Verification

Run the regression suite and frozen evaluation:

```bash
python scripts/test_zsi_entity_resolver_v12.py
python scripts/zsi_entity_holdout_v2.py
```

Key artefacts:

```text
scripts/zsi_entity_resolver_v12.py
scripts/test_zsi_entity_resolver_v12.py
scripts/zsi_entity_holdout_v2.py
zero-suffering-intelligence/entity-resolution/holdout-v2.json
zero-suffering-intelligence/entity-resolution/results-holdout-v2.json
.github/workflows/zsi-entity-holdout-v2.yml
```

## Evaluation guardrail

This is **developer-authored evaluation**, not independent external validation. The resolver and holdout are visible and reproducible, but the benchmark author is not an independent evaluator.

The rule is explicit:

> If v12 is changed after inspecting holdout-v2 outcomes, the next unbiased score requires a new frozen holdout-v3.

Do not tune against v2 and then market the improved v2 number as unseen performance.

## Production path

A production-grade resolver would extend this proof with authoritative registry identifiers, temporal company records, address/director evidence, confidence calibration on representative domain data, analyst override logging, drift monitoring and independent evaluation.

The principle remains:

> **Resolve when the evidence is strong. Abstain when it is not. Preserve the reason either way.**
