# SafeTrace Money Flow Atlas

A source-backed distribution layer for one deceptively simple question:

> Where is the money, where does it flow, who benefits, who is still missed, and what should be tested next?

## Product hierarchy

Every screen follows the repo frontend rule:

**Conclusion → Reason → Evidence → Original source → Gap → Next move**

The default view intentionally separates three concepts that are often mixed together:

1. **Wealth stock** — who owns accumulated net wealth?
2. **Money flow** — how do returns, taxes, transfers, subsidies and public budgets move resources?
3. **Outcome** — after those flows, who is still at risk of poverty or material insecurity?

A fourth layer turns observation into testable policy work:

4. **Distribution optimizer** — which intervention is expected to reduce the poverty gap most per euro, while preserving work incentives and exposing uncertainty?

## What “live” means

This project does **not** and should not attempt to expose private bank transactions.

- Selected ECB Distributional Wealth Accounts series are requested from the public ECB data API in the browser.
- If the API is unavailable, the UI falls back to the last verified snapshot in `snapshot.json`.
- Budget, poverty, subsidy and benefit-take-up figures update according to their official reporting cadence.
- Every metric carries a reporting period and an original-source link.

A green-looking dashboard is never allowed to make stale data appear real-time.

## Current evidence snapshot

Checked 2026-09-01.

- ECB DWA Q4 2025: adjusted German household net wealth ≈ €19.918tn.
- ECB DWA Q4 2025: top 10% share = 59.48%; bottom 50% level ≈ €431.9bn (~2.17% of total, derived).
- Bundesbank Q1 2026: household financial assets €9.490tn; average real financial-asset return remained positive only for the wealthiest 10% in that quarter.
- Destatis EU-SILC 2025: 13.3m people / 16.1% at risk of poverty; 21.2% at risk of poverty or social exclusion.
- Federal budget 2026: €524.540bn; BMAS €197.341bn / 37.62%.
- 30th Federal Subsidy Report: estimated 2026 subsidy volume €77.8bn.
- 2026 participation-benefit analysis: around 18% take-up for ages 6–14 and 12% for ages 15–17 in the analysed eligible groups.

## Analytical boundaries

- Net wealth is not disposable income.
- A ministry budget is not a measure of how much reaches poor households.
- A subsidy is not automatically wasteful or regressive.
- Aggregate wealth is not a liquid tax base.
- A scale calculator is not a revenue forecast or poverty microsimulation.
- Correlation between wealth, lobbying, public spending or policy outcomes is not causation.

## Distribution Score — next data contract

Every programme, subsidy, tax expenditure or proposed reform should eventually expose:

- eligible population;
- recipient population / take-up;
- gross and net fiscal cost;
- benefit incidence by disposable-income decile;
- benefit incidence by wealth group where feasible;
- poverty-gap reduction;
- material-deprivation effect;
- effective marginal tax / benefit withdrawal rates;
- administrative burden;
- uncertainty and evidence quality;
- source lineage and reporting period.

Unknowns remain `UNKNOWN`; the system must never invent a beneficiary distribution because the budget line exists.

## Recommended first experiment

Start with an existing benefit where eligible people are demonstrably missed.

1. estimate eligibility;
2. compare eligible vs reached;
3. calculate the unclaimed value where defensible;
4. identify data already held by government;
5. design pre-filled / automatic access with minimum additional evidence;
6. measure take-up before and after;
7. publish the evidence trail and distributional result.

This creates a measurable route from **money exists** to **money reaches the person it was intended to help**.
