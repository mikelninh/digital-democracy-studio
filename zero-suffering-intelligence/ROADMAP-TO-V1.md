# Zero Suffering Intelligence — Roadmap to V1.0

Updated: 2026-08-13

## Release principle

The V1 software shell is live as a Release Candidate. The `seed corpus / RC` label remains until the evidence-coverage and external-review gates are met.

## Shipped capabilities

- [x] v0.1 — public front door: Impact → Power → Evidence → Change
- [x] v0.2 — clickable graph + Evidence Inspector
- [x] v0.3 — search, filters and Path Mode
- [x] v0.4 — public Claim Ledger with stable IDs, boundaries, correction state and exports
- [x] v0.5 — Animal Impact Mirror without a guilt score
- [x] v0.6 — frozen 40-case Entity Resolution benchmark
- [x] v0.7a — Investigation OS text intake → candidate claims → human keep/reject → export
- [x] v0.8/0.9 — automated Watchtower: scheduled fetch → normalized snapshot → SHA-256 → diff/suspect retrieval classification → claim-review queue
- [x] Research Ops — Cases #001–003, Watchtower, resolver metrics and governance in one public view

## Current measurable state

- Reviewed organisations: **1 / 10**. Westfleisch and PHW are active research cases, not counted as fully reviewed.
- Verified atomic claims: **25 / 100** plus one explicit open-gap record.
- Deep-dive investigations: **1 / 3**; Cases #002 and #003 are active.
- Entity Resolution benchmark: **40 / 40** frozen pair tests.
- Resolver baseline: **Precision 90.48% · Recall 95.00% · F1 92.68% · Accuracy 92.50%**, with 3 visible errors.
- Resolver correction run on the **same frozen benchmark**: **100% Precision / Recall / F1**, with 0 errors. This is regression repair after inspecting failures, **not holdout or production accuracy**.
- Watchtower: **14** primary/official sources, scheduled every six hours.
- Latest clean Watchtower control run: **14 unchanged · 0 changed · 0 suspect · 0 failed · 0 claims needing review**.
- Watchtower reliability failures documented and repaired: snapshot serialization noise, volatile timestamps, temporal source versioning and bot/challenge-page collapse.
- Right of Reply: **3** request bundles drafted, **0 sent**.
- External reviewers: **0 / 3**.
- Hardest PFG edge: named farm → exact slaughterhouse remains unproven and is published as an explicit evidence boundary.

## Next

- [ ] create an unseen Entity Resolution holdout benchmark before making generalization claims
- [ ] v0.7b — URL/document intake + preserved source record + candidate entity extraction + Claim Ledger proposal
- [ ] send Right-of-Reply requests only after explicit human approval and record response states
- [ ] v0.9 — 3 external reviewers challenge real cases; publish failures/corrections
- [ ] grow Westfleisch and PHW to reviewed profiles and add 7 more organisations
- [ ] grow 25 verified claims → 50 → 100 without padding
- [ ] continue pursuing the exact PFG farm → slaughterhouse receipt or document why it is inaccessible

## V1.0 evidence gates

### Coverage
- [ ] 10 major organisations with reviewed public profiles
- [ ] 3 deep-dive investigations
- [ ] 100+ human-reviewed atomic public claims
- [ ] at least one fully sourced farm → intermediary → facility → legal entity → product/brand path, or a published source-backed account of why the missing hop remains inaccessible

### Evidence integrity
- [x] stable claim IDs and explicit boundaries
- [x] source URL/type, accessed date and review state
- [x] historical/current values coexist as temporal versions
- [x] correction and reliability events remain visible
- [x] Right-of-Reply workflow is operationally represented
- [ ] Right-of-Reply requests sent and response states recorded
- [ ] procedural-status vocabulary tested across multiple real enforcement/regulatory cases

### Entity resolution
- [x] 40 deliberately messy frozen benchmark pairs
- [x] precision/recall/F1 published
- [x] false positives and false negatives published
- [x] baseline failures corrected and before/after metrics published
- [ ] unseen holdout benchmark published

### Product usefulness / reality test
- [x] claim/case exports, search and responsive public UI
- [ ] external Journalist test
- [ ] external Citizen comprehension test
- [ ] external Fairness test
- [ ] at least 3 external reviewers use ZSI on real questions
- [ ] their failures, corrections and unresolved disputes are logged

## V1.0 definition

**Zero Suffering Intelligence V1.0 is a public evidence infrastructure for understanding who affects animals, how power flows through the food system, what can be proven, where uncertainty remains, and where change has the highest leverage.**

It is not a guilt ranking and not an allegation engine.
