# SafeTrace Ownership & Control

Evidence-backed ownership tracing that keeps **economic ownership**, **voting rights** and **other control** separate.

## Why this exists

A company graph is easy to draw and dangerously easy to overclaim. This module propagates an ownership or voting percentage only when:

1. the ownership edge is `established`;
2. the owner identity is `confirmed`;
3. the relevant percentage is explicitly present; and
4. the edge carries source evidence with an anchor.

Anything else becomes a visible blocked path or collection gap.

## Output contract

For a target entity, the engine produces:

- direct and indirect economic-ownership paths;
- multiple-path aggregation;
- separate voting-rights paths;
- documented non-equity control signals;
- rule-scoped UBO candidates;
- cycles and blocked paths;
- a complete `Show me why` evidence chain;
- JSON, Markdown and analyst HTML outputs.

UBO candidates are deliberately labelled `candidate_under_configured_rule`. They are **not** final legal UBO determinations.

## Golden case

`fixtures/golden_case.json` is synthetic and deliberately exercises:

- Alice → 60% of Holding One → 70% of Target = **42%** indirect interest;
- a second independent Alice path adds **6%**, producing **48% economic ownership**;
- voting percentages differ and produce **50% documented voting-path aggregate**;
- Carol owns only **5%**, but has a documented board-appointment right, producing a separate control signal.

Run it:

```bash
python -m safetrace.ownership_control.engine \
  --case safetrace/ownership_control/fixtures/golden_case.json \
  --out artifacts/ownership-control/golden
```

## Live-company boundary

`from_live_company.py` connects the live public-company pipeline to this engine.

If a live investigation resolves the company but does **not** acquire authoritative shareholder evidence, the adapter creates:

- the confirmed target company identity;
- **zero fabricated ownership edges**;
- an explicit shareholder / beneficial-ownership collection gap.

That is the intended result for the current Venatic investigation until a reviewed shareholder document is acquired.

## Guardrails

- Ambiguous identities stop propagation.
- Candidate or contradictory edges stop propagation.
- Missing percentages remain unknown.
- Economic ownership is never substituted for voting rights.
- Control rights are reported separately.
- Circular ownership is detected and excluded from naive recursion.
- Absence of a shareholder record is never treated as absence of shareholders.
- Every consequential conclusion requires human review.
