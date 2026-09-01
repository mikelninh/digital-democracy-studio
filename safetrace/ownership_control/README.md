# SafeTrace Ownership & Control

**Question:** Who owns and controls this company — what can we prove, and what should an analyst verify next?

## Problem

Ownership evidence is fragmented across registries, filings, agreements and jurisdictions. A graph is easy to draw; a defensible conclusion is harder. Identities can be ambiguous, indirect percentages can be miscalculated, voting rights can differ from equity, and missing evidence can look deceptively complete.

## Solution

SafeTrace turns reviewed evidence into a bounded ownership/control work product:

**target identity → evidence-backed relationships → indirect ownership → voting/control → rule-scoped candidates → evidence inspection → unresolved gaps → next collection action**

Propagation stops on ambiguous identities, missing percentages, non-established edges and cycles. Every propagated relationship carries its source and anchor.

## Use

Proof-of-work for enhanced due diligence, corporate investigations, ownership-network research, sanctions/financial-crime screening preparation, asset tracing and litigation support.

It is not an accusation engine. UBO candidates are analytical candidates under a configured rule, and screening handoffs are research leads — not legal UBO or sanctions conclusions.

## Application-facing Intelligence Desk

The generated UI is driven by the same `result.json` and case evidence used by the engine and CI:

**executive answer → ownership map → click relationship → source proof → analyst brief → unresolved gap → best next action**

### Deterministic golden case

Proves indirect ownership maths, multiple-path aggregation, separate voting rights, documented non-equity control, evidence lineage, and fail-closed cycle/identity/missing-percentage behavior.

### Live Venatic boundary

The live public-source run establishes the company but not an authoritative shareholder list. Correct output:

- **0** ownership edges;
- **0** UBO candidates;
- **0** screening handoffs;
- explicit shareholder / beneficial-ownership collection gap.

## Browser proof

GitHub Actions opens the generated production workspace in Chromium and verifies the real analyst interaction:

- graph renders;
- executive answer and analyst brief render;
- an ownership relationship can be clicked;
- its evidence source and anchor open;
- a no-ownership case renders the fail-closed empty state.

CI captures overview, evidence-open and empty-state screenshots.

## Run

```bash
python -m safetrace.ownership_control.production \
  --case safetrace/ownership_control/fixtures/golden_case.json \
  --out artifacts/ownership-control/golden
```

Open `artifacts/ownership-control/golden/index.html`.

## Boundary

Economic ownership, voting rights and other control are separate evidence dimensions. Consequential conclusions require human review and applicable jurisdiction-specific rules.
