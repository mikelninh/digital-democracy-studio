# SafeTrace — Venatic technical proof

This is the technical layer behind the [application investigation](../).

## Architecture

```text
source record
  → preserved evidence / identity resolution
  → established entity relationships
  → ownership / voting / control calculations
  → bounded findings + explicit unknowns
  → analyst workspace
  → hidden-gold evaluation + browser CI
```

## Shortest code paths

- [`../../ownership_control/README.md`](../../ownership_control/README.md) — architecture and fail-closed rules
- [`../../ownership_control/engine.py`](../../ownership_control/engine.py) — relationship propagation and calculations
- [`../../ownership_control/production.py`](../../ownership_control/production.py) — production identity/screening boundary
- [`../../venatic_challenge/README.md`](../../venatic_challenge/README.md) — 28-record adversarial benchmark
- [`../../venatic_challenge/evaluate.py`](../../venatic_challenge/evaluate.py) — hidden-gold evaluator
- [`../../venatic_challenge/collection.py`](../../venatic_challenge/collection.py) — evidence-budget prioritisation
- [`../../venatic_challenge/source_independence.py`](../../venatic_challenge/source_independence.py) — circular-reporting/source-independence logic
- [`../../../.github/workflows/venatic-application.yml`](../../../.github/workflows/venatic-application.yml) — browser-tested investigation journey
- [`../../../.github/workflows/venatic-analyst-challenge.yml`](../../../.github/workflows/venatic-analyst-challenge.yml) — benchmark gate
- [`../../../.github/workflows/ownership-control.yml`](../../../.github/workflows/ownership-control.yml) — ownership/live-boundary gate

## Measured synthetic benchmark

- 28 records across 5 jurisdictions
- blind first pass: **95/100**
- after a five-source research budget: **100/100**
- **0 critical failures** under the benchmark's fail rules

These are synthetic-case results, not claims of production analyst accuracy or legal determinations.

## Product boundary

The system is designed to stop where evidence stops. An unresolved nominee principal remains unknown; a fuzzy sanctions name match is not an identity match; legal ownership, operation and lender security remain separate relationships.
