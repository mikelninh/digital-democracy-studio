# Zero Suffering Intelligence — Roadmap to V1.0

Updated: 2026-08-14

## Release principle

The V1 software shell is live as a Release Candidate. The `RC` label remains until the external-review and fairness gates are met. Coverage gates are shown separately from product/reality-test gates so users can see exactly what is done and what is not.

## What `Reviewed v1` means

A reviewed-v1 organisation has been checked across the same ten lanes:

`Scale · Farms/Suppliers · Facilities · Brands · Retail · Public Money · Procurement · Lobbying · Regulatory history · Transition`

Every lane ends in one of four states:

- **Verified** — a source carries the published claim.
- **Partial** — part of the relationship is proven; an important hop remains open.
- **Checked · open** — the lane was searched in the defined first-pass source set, but no publishable claim was established. This is not evidence of absence.
- **Verified · narrow** — verified only for the stated legal entity, period, threshold or procedural context.

Reviewed v1 does **not** mean fully mapped, complete or morally ranked.

## Shipped capabilities

- [x] Public front door: Impact → Power → Evidence → Change
- [x] Clickable graph + Evidence Inspector
- [x] Search, filters and Path Mode
- [x] Public Claim Ledger with stable IDs, source links, boundaries, correction state and exports
- [x] Animal Impact Mirror without a guilt score
- [x] Ten-case reviewed-v1 explorer with explicit next actions
- [x] Investigation OS human-review intake
- [x] Automated Watchtower: scheduled fetch → normalized snapshot → SHA-256 → diff/suspect classification → claim-review queue
- [x] Research Ops: cases, Watchtower, Entity Resolution and governance in one view
- [x] Frozen Entity Resolution regression benchmark and separate unseen holdout

## Current measurable state

- Reviewed organisations: **10 / 10**.
- Reviewed-v1 cases: **10** (`ZSI-CASE-001` through `ZSI-CASE-010`).
- Verified atomic public claims: **109** plus explicit research-gap records. The **100+ claim gate is met**.
- Original deep-dive requirement: **3 / 3 met**, with seven additional reviewed-v1 organisation cases now added.
- Entity Resolution regression benchmark: **40 / 40** frozen pair tests.
- Resolver baseline on that 40-case set: **Precision 90.48% · Recall 95.00% · F1 92.68% · Accuracy 92.50%**, with 3 visible errors.
- Same-set correction run after inspecting those errors: **100% Precision / Recall / F1**. This is regression repair, not an unbiased generalization result.
- Separate unseen holdout: **30 frozen cases · Precision 92.31% · Recall 85.71% · F1 88.89% · Accuracy 90.00%**, with 3 visible errors. Holdout-v1 must not be tuned and then re-reported as unseen.
- Watchtower: **14** primary/official sources scheduled every six hours. Latest verified clean control state: **14 unchanged · 0 changed · 0 suspect · 0 failed · 0 claims needing review**.
- Right of Reply: **3** request bundles drafted, **0 sent**. Cases #004–010 still need request bundles.
- External reviewers: **0 / 3**.
- Hardest PFG edge: named farm → exact slaughterhouse remains unproven and is published as an explicit evidence boundary rather than inferred.

## Ten reviewed organisations

1. Premium Food Group / Tönnies — `ZSI-CASE-001`
2. Westfleisch SCE mbH — `ZSI-CASE-002`
3. PHW-Gruppe / WIESENHOF — `ZSI-CASE-003`
4. Danish Crown Germany — `ZSI-CASE-004`
5. Müller Gruppe — `ZSI-CASE-005`
6. Plukon Germany — `ZSI-CASE-006`
7. Rothkötter Unternehmensgruppe — `ZSI-CASE-007`
8. Sprehe Gruppe — `ZSI-CASE-008`
9. Arla / former DMK Group — `ZSI-CASE-009`
10. Hochwald Foods — `ZSI-CASE-010`

## V1.0 evidence gates

### Coverage
- [x] 10 major organisations with reviewed public profiles
- [x] 3 deep-dive investigations (10 reviewed-v1 cases now exist)
- [x] 100+ human-reviewed atomic public claims (109 verified)
- [x] explicit published evidence boundary for the unresolved PFG named-farm → exact-slaughterhouse hop; the preferred stronger outcome remains a fully sourced end-to-end chain

### Evidence integrity
- [x] stable claim IDs and explicit boundaries
- [x] source URL/type, accessed date and review state
- [x] historical/current values can coexist as temporal versions
- [x] correction and Watchtower reliability events remain visible
- [x] Right-of-Reply workflow is operationally represented
- [ ] Right-of-Reply bundles exist for all ten consequential company profiles
- [ ] Right-of-Reply requests have been sent with explicit human approval and response states recorded
- [ ] procedural-status vocabulary is externally reviewed across multiple regulatory/enforcement cases

### Entity resolution
- [x] 40 deliberately messy frozen regression-benchmark pairs
- [x] baseline precision/recall/F1 and failures published
- [x] same-set regression repair published separately
- [x] 30-case unseen holdout frozen before first evaluation
- [x] unseen holdout metrics and all 3 failures published
- [ ] if resolver rules are changed after inspecting holdout-v1, create a fresh holdout-v2 before claiming a new unbiased score

### Product usefulness / reality test
- [x] claim/case exports, source search and responsive public UI
- [x] user-facing explanations answer: What am I seeing? What does it mean? What can I do next?
- [ ] external Journalist test
- [ ] external Citizen comprehension test
- [ ] external Fairness test
- [ ] at least 3 independent reviewers use ZSI on real questions
- [ ] their failures, corrections and unresolved disputes are logged publicly

## Next highest-value work

1. **External reality test:** recruit 3 independent reviewers and give them concrete research questions without a walkthrough.
2. **Right of Reply:** prepare bundles for Cases #004–010; send all consequential case requests only after explicit human approval.
3. **Complete receipt chain:** continue searching for one named farm → intermediary → facility → legal entity → product/brand/customer path.
4. **Watchtower expansion:** grow from 14 sources to the high-value primary/official sources underpinning the ten reviewed cases.
5. **Investigation OS v0.7b:** URL/document → preserved source → candidate entities/claims → human review → Claim Ledger proposal.

## V1.0 definition

**Zero Suffering Intelligence V1.0 is public evidence infrastructure for understanding who affects animals, how power flows through the food system, what can be proven, where uncertainty remains, and where change has the highest leverage.**

It is not a guilt ranking and not an allegation engine.
