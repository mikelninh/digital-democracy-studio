# SafeTrace Ownership & Control

Evidence-backed ownership tracing that keeps **economic ownership**, **voting rights** and **other control** separate.

## Why this exists

A company graph is easy to draw and dangerously easy to overclaim. The production boundary propagates an ownership or voting percentage only when:

1. the target entity identity is `confirmed`;
2. the ownership edge is `established`;
3. the owner identity is `confirmed`;
4. the relevant percentage is explicitly present; and
5. the edge carries source evidence with an anchor.

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
- a screening handoff containing only confirmed natural-person rule candidates;
- JSON, Markdown and analyst HTML outputs.

UBO candidates are deliberately labelled `candidate_under_configured_rule`. They are **not** final legal UBO determinations. Screening handoff records are research leads for a separate authoritative screening stage; they are **not sanctions matches**.

## Golden case

`fixtures/golden_case.json` is synthetic and deliberately exercises:

- Alice → 60% of Holding One → 70% of Target = **42%** indirect interest;
- a second independent Alice path adds **6%**, producing **48% economic ownership**;
- voting percentages differ and produce **50% documented voting-path aggregate**;
- Carol owns only **5%**, but has a documented board-appointment right, producing a separate control signal.

Run the production path:

```bash
python -m safetrace.ownership_control.production \
  --case safetrace/ownership_control/fixtures/golden_case.json \
  --out artifacts/ownership-control/golden
```

## Live-company boundary

`from_live_company.py` connects the live public-company pipeline to the production ownership/control boundary.

If a live investigation resolves the company but does **not** acquire authoritative shareholder evidence, the adapter creates:

- the confirmed target company identity;
- **zero fabricated ownership edges**;
- **zero UBO candidates**;
- **zero screening handoff records**;
- an explicit shareholder / beneficial-ownership collection gap.

That is the intended result for the current Venatic investigation until a reviewed shareholder document is acquired.

## Screening handoff

When the configured ownership/control rule produces a candidate, only a `confirmed` natural person can enter `screening_handoff`. The handoff includes the candidate's stable identifiers where available and the rule grounds that caused the handoff.

Ownership & Control does not perform or claim the sanctions result itself. The next stage must screen those records against authoritative lists at decision time and preserve the resulting evidence separately.

## Guardrails

- Unresolved target identity blocks production graph propagation.
- Ambiguous owner identities stop propagation.
- Candidate or contradictory edges stop propagation.
- Missing percentages remain unknown.
- Economic ownership is never substituted for voting rights.
- Control rights are reported separately.
- Circular ownership is detected and excluded from naive recursion.
- Absence of a shareholder record is never treated as absence of shareholders.
- Screening handoff is not a sanctions match.
- Every consequential conclusion requires human review.
