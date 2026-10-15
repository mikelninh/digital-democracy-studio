# SafeTrace — Entity Resolution Mode

A small, inspectable proof that SafeTrace can turn noisy public records into canonical organisation identities **without hiding why two records were merged**.

## What this proves

The benchmark contains **40 deliberately messy organisation records across 10 ground-truth entities**. Variants include legal suffixes, abbreviations, OCR errors, translations, changed formatting, addresses, directors, domains and subsidiaries.

The dangerous cases are intentional: a subsidiary may share a brand/root domain with its parent, but SafeTrace must **not** collapse them into one legal entity.

## Decision policy

- **auto_merge** — score >= 0.72. Safe enough to canonicalise automatically.
- **human_review** — score >= 0.58 and < 0.72. Evidence is plausible but insufficient.
- **reject** — score < 0.58. Keep entities separate.

Every score exposes its evidence: name similarity, exact/root domain, address similarity, postcode, director overlap and source provenance. The resolver is deterministic and uses only Python's standard library so reviewers can inspect the logic quickly.

## Benchmark result

With the checked-in v1 dataset:

- **Precision: 1.000**
- **Recall: 0.900**
- **F1: 0.947**
- **0 false-positive auto-merges**
- 54 true-positive auto-merges out of 60 true matching pairs

This benchmark is synthetic and intentionally small. The point is not to claim production-grade entity resolution; it is to demonstrate the architecture, evaluation discipline, evidence trail and conservative failure policy.

## Run it

```bash
cd safetrace/entity_resolution
python resolver.py
```

Run the regression tests with:

```bash
python -m pytest test_resolver.py
```

Open `demo.html` for a portfolio-friendly explanation of the benchmark and inspectable example decisions.

## Why this belongs in SafeTrace

Entity resolution is upstream of investigation quality. If two records from a tender, company register or scraped document refer to the same organisation, SafeTrace should be able to join them. If they only *look* related — for example a parent company and subsidiary — the system should preserve that distinction.

> No merge without evidence. No uncertainty hidden.

## Next production steps

1. Add blocking/candidate generation for large corpora.
2. Add registry identifiers (Handelsregister/LEI/VAT) as high-confidence features.
3. Learn thresholds on a labelled real-world dataset instead of hand-tuning.
4. Add temporal features for address/director changes.
5. Represent `same_as`, `subsidiary_of`, `director_of` and `located_at` as explicit graph edges.
6. Persist reviewer corrections as labelled training/evaluation data.
