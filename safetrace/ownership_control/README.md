# SafeTrace Ownership & Control

An evidence-first corporate intelligence workflow for answering a deceptively simple question:

> **Who owns and controls this company — what can we prove, and what should an analyst verify next?**

## The problem

Ownership and control evidence is fragmented across registries, shareholder filings, corporate records, agreements and source systems. The hard part is not drawing a graph. It is deciding which identities and relationships are actually established, calculating indirect interests correctly, keeping voting/control separate from equity, and preserving what remains unknown.

## The solution

SafeTrace converts reviewed evidence into a defensible ownership/control work product:

1. confirm the target identity;
2. ingest evidence-backed ownership relationships;
3. propagate direct and indirect economic ownership;
4. calculate voting rights separately;
5. surface documented non-equity control signals;
6. block ambiguous identities, missing percentages and cycles;
7. identify natural-person candidates under a configurable analytical rule;
8. hand confirmed candidates to a separate authoritative screening stage;
9. show the exact source and anchor behind every relationship;
10. preserve unresolved gaps and recommend the next evidence to collect.

## Who would use it

Designed as proof-of-work for:

- enhanced due diligence;
- corporate and individual investigations;
- ownership-network research;
- sanctions / financial-crime screening preparation;
- asset tracing and litigation support.

It is intentionally **not** an accusation engine. A risk indicator, fuzzy identity candidate, ownership threshold or screening handoff is never promoted into a legal or sanctions conclusion without the necessary evidence and human review.

## Application-facing experience

The generated **SafeTrace Intelligence Desk** is task-first:

**Case → executive answer → ownership map → click relationship → source proof → UBO/control candidates → unresolved gaps → best next collection action**

The UI is rendered from the same `result.json` contract used by the engine and CI. It is not a separate mockup.

## Proof cases

### Deterministic golden case

The synthetic golden case demonstrates:

- `60% × 70% = 42%` indirect ownership;
- aggregation across multiple independent ownership paths;
- economic ownership and voting rights producing different results;
- a documented control right creating a rule-scoped candidate below the equity threshold;
- complete evidence chains for propagated relationships;
- cycle, identity and missing-percentage fail-closed behavior.

### Live Venatic boundary case

The live public-source Venatic investigation confirms a more important negative behavior: when the reviewed evidence establishes the company but **does not establish its shareholder list**, the ownership layer emits:

- zero ownership edges;
- zero UBO candidates;
- zero screening handoffs;
- one explicit shareholder / beneficial-ownership collection gap.

Missing evidence stays missing.

## Browser verification

GitHub Actions opens the generated production workspace in Chromium and verifies that an analyst can see the computed ownership graph, read the executive answer, click a relationship, open its evidence view and inspect the supporting source/anchor. It separately verifies the fail-closed empty state when ownership is not established.

The browser proof captures three states as CI artifacts:

- investigation overview;
- relationship evidence opened;
- fail-closed empty ownership state.

## Run locally

```bash
python -m safetrace.ownership_control.production \
  --case safetrace/ownership_control/fixtures/golden_case.json \
  --out artifacts/ownership-control/golden
```

Then open `artifacts/ownership-control/golden/index.html`.

## Analytical boundary

Economic ownership, voting rights and other control are separate evidence dimensions. UBO candidates are candidates under a configured analytical rule, not definitive legal beneficial-owner determinations. Consequential conclusions require human review and the applicable jurisdiction-specific rules.
