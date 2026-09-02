# Venatic application package

One-link proof-of-work package for the **Junior Intelligence Analyst** application.

## Front door — experience first

`safetrace/venatic_application/index.html`

The reviewer should not arrive at a wall of project explanation.

The intended journey is:

1. **Take the analyst challenge** — make a judgement on a synthetic adversarial case before seeing the answer.
2. **Choose a real investigation** — policy influence, defence money or shadow-fleet asset tracing.
3. **Inspect the evidence** — click relationships, dates, identities and claims.
4. **Open the original source** — every material conclusion remains independently verifiable.
5. **Find the biggest gap** — see what is unresolved rather than reading false certainty.
6. **Choose the next move** — identify which source would most change the assessment.
7. **Only then inspect the machinery** — benchmark, architecture, source contracts and CI.

## Real investigations

1. `real/` — **Meat industry & policy influence**
   - research question: did a documented industry ask contribute to a later policy delay?
   - advocacy objective: documented
   - requested delay: enacted
   - lobbying causation: not established

2. `defence/` — **Defence Money Map**
   - research question: where does a major public procurement opportunity actually go, and what can we prove about influence around it?
   - Bundeswehr / Rheinmetall 155mm framework ceiling: up to €8.5bn
   - disclosed initial call-off: around €880m
   - company economics, public-market ownership and lobbying mapped separately
   - no claim that lobbying caused the award or that the full framework ceiling has been spent

3. `shadow-fleet/` — **Shadow Fleet temporal entity resolution**
   - research question: can a sanctioned tanker disappear from name-only screening after changing names and management?
   - same tankers resolved across changing UK/EU/Ukrainian names by stable IMO identifiers
   - ownership and management records kept time-bounded rather than collapsed into one timeless fact
   - current natural-person UBO remains unresolved from the selected sources

## Information architecture — product correctness

Every investigation follows this structure:

**Question → Current assessment → Why → Evidence → Original source → Gap → Next move.**

`Current assessment` replaces `Conclusion` when the work remains open. The page should never feel as if the answer existed before the investigation began.

The reviewer should understand the question first, then either interact with evidence or see a compact best-supported answer. Deep metadata remains one click away.

Shared UI rules live in:

- `/AGENTS.md`
- `/docs/FRONTEND_INFORMATION_ARCHITECTURE.md`
- `assets/investigation.css`

Readability is tested in Chromium on desktop and mobile. The product rule is explicit: **reduce simultaneous information before reducing font size.**

## Proof-of-work design standard

For this application, proof should feel like an analyst workspace rather than a portfolio essay.

The reviewer should be able to:

- make an ownership judgement;
- compare identity records;
- inspect source-backed relationships;
- spot a sanctions false positive;
- distinguish asset owner / operator / lender roles;
- see where copied reporting is not independent corroboration;
- understand which evidence would be collected next.

The benchmark challenge already implements this interaction pattern and should be treated as the strongest entry experience, not as hidden technical appendix material.

## Source contract

`real_case.schema.json` defines the minimum evidence record:

- publisher
- authority
- source type
- original URL
- exact location
- what the source establishes
- what it does not establish
- retrieval date

The shared `assets/source-drawer.js` renders this contract consistently across real cases.

## Benchmark lab — synthetic adversarial investigation

`benchmark/index.html` and `safetrace/venatic_challenge/`

The Meridian Atlas challenge remains synthetic by design so the system can be scored against a known hidden answer and deliberately adversarial edge cases.

- Initial sources: 18
- Optional sources: 10
- Optional acquisition budget: 5
- Blind first pass: **95/100**
- Budgeted pass: **100/100**
- Critical failures: **0**

These are synthetic benchmark scores, not claims of production analyst performance.

## Technical proof

`technical/index.html`

Shows the architecture, evaluation design, code map and CI evidence underneath the reviewer-facing experiences.

The technical proof is intentionally secondary. A reviewer should first experience the investigation, then inspect how it was built if they care.

## Trust standard

For real investigations:

1. **Authenticity** — identify the original record or authoritative publication.
2. **Integrity** — preserve retrieval/version information and, where appropriate, hashes or snapshots.
3. **Provenance** — record who published the evidence and where it came from.
4. **Authority** — distinguish official/primary records from first-party and secondary sources.
5. **Evidence** — preserve the exact record/location supporting the finding.
6. **Inference** — expose how the evidence supports the bounded current assessment.
7. **Human authority** — consequential conclusions remain reviewable by a person.
8. **Audit** — keep the evidence and reasoning trail inspectable.

**No finding without provenance. No consequential inference without a visible evidence boundary.**

## Quality gates

`.github/workflows/venatic-real-investigation.yml` browser-tests:

- the question-first hub;
- each real case's current-assessment hierarchy;
- evidence-drawer links and limitation language;
- minimum readable typography;
- desktop screenshots;
- mobile screenshots;
- source-registry integrity.

`.github/workflows/venatic-application.yml` separately protects the synthetic benchmark.

The broader SafeTrace release workflow protects the shared evidence infrastructure.

## Boundaries

Lobbying is lawful and routine democratic activity. Expenditure, membership, access, timing or policy overlap do not by themselves establish corruption, quid-pro-quo conduct, political control or procurement causation.

A framework contract ceiling is not money already spent. Company-wide revenue, profit and dividends are not automatically attributable to one public contract.

A vessel name is not a stable asset identity. Historical owner/manager records are not automatically the current state.

## North star

**Do not tell the reviewer I can investigate. Let them investigate with me.**
