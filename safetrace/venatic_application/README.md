# Venatic application package

One-link proof-of-work package for the **Junior Intelligence Analyst** application.

## Information architecture

The application deliberately separates **real-world investigation** from **synthetic evaluation**.

### 1. Flagship — real public-source investigation

`real/index.html`

**Question:** Did the German meat industry get the policy change it wanted — and can the public record prove why?

The real case uses official Bundestag lobbying disclosures, official legislative material and clearly-labelled first-party records. Every material conclusion follows the same reviewer-visible chain:

**Conclusion → Reason → Evidence → Original source → Authority/exact location → Gap → Next move**

The core conclusion is intentionally bounded:

- documented lobbying activity: **supported**;
- policy alignment: **supported**;
- direct lobbying causation: **not established**.

A reviewer never has to trust an AI-generated finding: each evidence drawer links to the original public source and states what that source does **not** prove.

### 2. Benchmark lab — synthetic adversarial investigation

`index.html` and `safetrace/venatic_challenge/`

The Meridian Atlas challenge remains synthetic by design so the system can be tested against a known hidden answer and deliberately adversarial edge cases.

- Initial sources: 18
- Optional sources: 10
- Optional acquisition budget: 5
- Blind first pass: **95/100**
- Budgeted pass: **100/100**
- Critical failures: **0**

These are synthetic benchmark scores, not claims of production analyst performance.

### 3. Technical proof

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

- `.github/workflows/venatic-real-investigation.yml` browser-tests the real case, evidence drawers, authority/location metadata and original-source links.
- `.github/workflows/venatic-application.yml` browser-tests the synthetic analyst challenge.
- the broader SafeTrace release workflow protects the shared evidence infrastructure.

## Boundary

Lobbying is a lawful and routine part of democratic policymaking. A disclosed lobbying project, expenditure, membership, meeting, statement or policy overlap is not evidence by itself of corruption, quid-pro-quo conduct, political control or improper influence.

The real case is designed to make that distinction visible rather than imply more than public records establish.