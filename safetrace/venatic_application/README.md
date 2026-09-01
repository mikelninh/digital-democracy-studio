# Venatic application package

One-link proof-of-work package for the **Junior Intelligence Analyst** application.

## Front door — real investigation hub

`index.html`

The reviewer now chooses between three genuine public-source investigations:

1. `real/` — **Meat industry & policy influence**
   - advocacy objective: documented
   - requested delay: enacted
   - lobbying causation: not established

2. `defence/` — **Defence Money Map**
   - Bundeswehr / Rheinmetall 155mm framework ceiling: up to €8.5bn
   - disclosed initial call-off: around €880m
   - company economics, public-market ownership and lobbying mapped separately
   - no claim that lobbying caused the award or that the full framework ceiling has been spent

3. `shadow-fleet/` — **Shadow Fleet temporal entity resolution**
   - same tankers resolved across changing UK/EU/Ukrainian names by stable IMO identifiers
   - ownership and management records kept time-bounded rather than collapsed into one timeless fact
   - current natural-person UBO remains unresolved from the selected sources

## Information architecture — product correctness

Every investigation presents information in this order:

**Conclusion → Reason → Evidence → Original source → Confidence / gap → Next move**

The reviewer should understand the main answer before seeing deep metadata. Source IDs, authority metadata, limitations and exact record locations stay one click away in the evidence drawer.

Shared UI rules live in:

- `/AGENTS.md`
- `/docs/FRONTEND_INFORMATION_ARCHITECTURE.md`
- `assets/investigation.css`

Readability is tested in Chromium on desktop and mobile. The product rule is explicit: **reduce simultaneous information before reducing font size.**

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

## Trust standard

For real investigations:

1. **Authenticity** — identify the original record or authoritative publication.
2. **Integrity** — preserve retrieval/version information and, where appropriate, hashes or snapshots.
3. **Provenance** — record who published the evidence and where it came from.
4. **Authority** — distinguish official/primary records from first-party and secondary sources.
5. **Evidence** — preserve the exact record/location supporting the finding.
6. **Inference** — expose how the evidence supports the bounded conclusion.
7. **Human authority** — consequential conclusions remain reviewable by a person.
8. **Audit** — keep the evidence and reasoning trail inspectable.

**No finding without provenance. No consequential inference without a visible evidence boundary.**

## Quality gates

`.github/workflows/venatic-real-investigation.yml` now browser-tests:

- the three-case hub;
- each real case's conclusion-first hierarchy;
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
