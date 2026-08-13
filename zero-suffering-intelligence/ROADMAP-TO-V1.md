# Zero Suffering Intelligence — Roadmap to V1.0

Updated: 2026-08-13

## Release principle

Ship public capabilities, then measure them against reality. The V1 software shell is live as a Release Candidate; the `seed corpus / RC` label stays until the evidence and external-review gates are met.

## Shipped capabilities

- [x] v0.1 — public front door: Impact → Power → Evidence → Change
- [x] v0.2 — clickable graph + Evidence Inspector
- [x] v0.3 — search, status filters and Path Mode
- [x] v0.4 — public Claim Ledger with stable claim IDs, source type, review state, boundaries, correction state and shareable claim hashes
- [x] v0.5 — Animal Impact Mirror alpha without a guilt score
- [x] v0.6 — frozen 40-case Entity Resolution benchmark with reproducible metrics and visible errors
- [x] v0.7a — Investigation OS text intake: source text → atomic candidate claims → human keep/reject → export
- [x] v0.8 — automated Watchtower: scheduled source fetch → normalized snapshot → SHA-256 → diff → affected claim review queue
- [x] Research Ops — Cases #001–003, Watchtower state, Entity Resolution metrics and governance links in one public view

## Current measurable state

- Reviewed organisations: **1 / 10** (PFG/Tönnies); Westfleisch and PHW are active research cases, not yet counted as fully reviewed.
- Verified atomic claims: **25 / 100** plus one explicit open-gap record.
- Deep-dive investigations: **1 / 3**; Cases #002 and #003 are active.
- Entity Resolution benchmark: **40 / 40** frozen pair tests.
- Resolver metrics: **Precision 90.48% · Recall 95.00% · F1 92.68% · Accuracy 92.50%**.
- Visible resolver errors: **3** (2 false positives, 1 false negative).
- Watchtower: **14** primary/official sources configured, scheduled every six hours.
- Right of Reply: **3** request bundles drafted, **0 sent**.
- External reviewers: **0 / 3**.

## Next

- [ ] v0.7b — URL/document intake + preserved source record + candidate entity extraction + Claim Ledger proposal
- [ ] resolve Entity Resolution ER-009, ER-031 and ER-032; rerun the frozen benchmark and publish before/after metrics
- [ ] send Right-of-Reply requests only after explicit human approval and record response status
- [ ] v0.9 — external reality test: 3 real reviewers challenge the system; publish failures and corrections
- [ ] complete the hardest PFG supply-chain edge or publish a source-backed account of why the exact destination remains inaccessible

## V1.0 evidence gates

### Coverage
- [ ] 10 major organisations with reviewed public profiles
- [ ] 3 deep-dive investigations
- [ ] 100+ human-reviewed atomic public claims
- [ ] at least one fully sourced farm → intermediary → facility → legal entity → product/brand path, or an explicit published account of why the final hop remains inaccessible

### Evidence integrity
- [x] public verified claims use stable claim IDs
- [x] public claim records carry source URL/type, accessed date, review state and an explicit boundary
- [x] historical/current values can coexist as temporal claim versions rather than silently overwriting history
- [x] correction and internal reliability events remain visible
- [x] Right-of-Reply workflow is documented and operationally represented
- [ ] Right-of-Reply requests have been sent and response states recorded for consequential company profiles
- [ ] procedural status vocabulary is tested across multiple real regulatory/enforcement cases

### Entity resolution
- [x] 40 deliberately messy frozen benchmark pair tests
- [x] precision/recall/F1 published from a reproducible runner
- [x] false positives and false negatives published
- [x] no production merge is justified solely by shared address or group membership
- [ ] human corrections to the three benchmark errors are implemented and before/after metrics published

### Product usefulness
- [x] public claim export
- [x] basic source/entity/claim search
- [x] responsive public interface
- [ ] Journalist test validated by an external journalist/researcher
- [ ] Citizen comprehension test validated externally
- [ ] Fairness test validated with an investigated organisation or independent reviewer

### Reliability / external test
- [x] first Watchtower reliability failures were logged instead of hidden
- [x] benchmark metrics and errors are public product data
- [ ] at least 3 external reviewers use the system on real questions
- [ ] their failures, corrections and unresolved disputes are logged

## V1.0 definition

**Zero Suffering Intelligence V1.0 is a public evidence infrastructure for understanding who affects animals, how power flows through the food system, what can be proven, where uncertainty remains, and where change has the highest leverage.**

It is not a guilt ranking and not an allegation engine.
