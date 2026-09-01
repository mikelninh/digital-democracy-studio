# SafeTrace — Venatic Analyst Challenge

A deliberately difficult intelligence-analysis benchmark designed around the work of a technology-driven investigations team.

> **Can an analyst turn fragmented, contradictory records into a defensible answer — quickly, without overclaiming?**

This is not a generic OSINT demo. It is a scored casework exercise for ownership/control research, enhanced due diligence, sanctions triage, asset tracing and source-critical reporting.

## Why this challenge exists

Venatic Intelligence publicly describes two tightly coupled capabilities:

1. **Investigative tradecraft** across forensic analysis, asset tracing, reputational risk, enhanced due diligence, litigation support and special situations.
2. **Technology for massive, fragmented and unstructured datasets**, including integrating disparate sources, resolving entities and mapping hidden networks.

The challenge sits exactly at that intersection: the software may accelerate acquisition, structuring and calculation, but the analyst must own the conclusion.

## The analyst question

> **Who ultimately owns or controls Meridian Atlas Trading GmbH, is the apparent sanctions connection real, which assets can be attributed with defensible evidence, what material risk indicators are supported, and what should be investigated next?**

All people, companies, records and allegations in the challenge are synthetic.

## What makes the pack difficult

The pack contains 28 synthetic records across Germany, the United Kingdom, the UAE, Cyprus and Serbia. It deliberately includes:

- subsidiaries and holding companies across jurisdictions;
- spelling variants and transliterations;
- stale and contradictory director records;
- nominee ownership with an unresolved natural person;
- direct and indirect economic ownership with different voting rights;
- a sanctions homonym with strong name similarity but conflicting identity attributes;
- an invoice beneficiary change that looks suspicious but has an innocent alternative explanation;
- an asset used by the group but legally owned by a different entity;
- a lender security interest that must not be collapsed into asset ownership;
- a court-record no-hit that is bounded negative evidence, not proof of no litigation;
- duplicated documents, low-quality media claims and one deliberately misleading source;
- dated evidence so the analyst has to reason temporally, not just merge facts.

## The six decisions

A submission must answer six things clearly:

1. **Ownership & control** — direct and indirect economic interests, voting rights and non-equity control kept separate.
2. **Sanctions identity** — whether the candidate is the same person, not merely a fuzzy-name match.
3. **Asset attribution** — legal owner, security interest, lessee/operator and group association kept distinct.
4. **Risk findings** — only claims supported by evidence, with confidence, caveat and next step.
5. **Contradictions & unknowns** — unresolved questions must remain visible.
6. **Collection plan** — the next evidence should be prioritized by expected decision value, not by browsing volume.

## Gold scoring

The benchmark is scored out of 100:

| Dimension | Points |
|---|---:|
| Ownership/control accuracy | 25 |
| Entity resolution & sanctions judgement | 20 |
| Asset attribution | 15 |
| Evidence/provenance quality | 15 |
| Analytical writing & bounded claims | 10 |
| Contradictions / uncertainty handling | 10 |
| Next-best collection plan | 5 |

### Critical-fail penalties

Any of the following is a major failure even if the rest of the answer sounds polished:

- promoting the sanctions homonym to `SAME_AS` despite conflicting DOB/nationality/passport evidence;
- calling the payment-beneficiary change fraud, money laundering or sanctions evasion without additional proof;
- treating nominee ownership as if the natural-person UBO were known;
- treating use/possession of an asset as legal ownership;
- treating lender security as ownership;
- treating a court no-hit as proof that no litigation exists;
- claiming beneficial ownership is complete when the shareholder chain has an unresolved gap;
- silently dropping a contradictory official record.

## Blind mode

The candidate-facing case pack does **not** expose `gold_answer.json`.

The scoring workflow receives:

- the analyst submission;
- the hidden gold answer;
- deterministic critical-fail rules;
- source IDs cited by the submission.

This makes the benchmark useful for both human analysts and assisted workflows.

## Evidence-budget mode

A second mode limits the analyst to a small number of additional collection actions after the initial pack.

The objective becomes:

> **Maximize decision quality per source acquired.**

This tests research judgement under a deadline rather than rewarding endless browsing.

## Case replay

Every run should eventually preserve a replayable sequence:

`question → hypotheses → sources opened → entity decisions → claims changed → contradictions resolved/unresolved → final memo`

The replay is important because a correct answer produced through reckless reasoning is not a trustworthy workflow.

## What we want to show in the application

The final public experience should take under 90 seconds to understand:

1. Open the case.
2. See the executive answer.
3. Explore the ownership/network graph.
4. Click any relationship to inspect source proof.
5. See the sanctions false positive rejected.
6. See asset roles kept separate.
7. See unresolved gaps and the next best collection action.
8. Open the client-ready memo.
9. Open the scorecard and see where the system could still fail.

The message is simple:

> **SafeTrace does not replace investigative judgement. It makes that judgement faster, inspectable and harder to overstate.**

## Next build stages

- [ ] Generate the 28-document synthetic case pack.
- [ ] Add hidden `gold_answer.json` and deterministic evaluator.
- [ ] Connect the pack to Ownership & Control and Intelligence Casework engines.
- [ ] Add temporal network + asset / payment relationships.
- [ ] Add hypothesis board and collection-priority scoring.
- [ ] Add browser-tested analyst challenge UI.
- [ ] Add case replay and red-team view.
- [ ] Add scorecard: accuracy, evidence coverage, overclaim penalties and unresolved-gap recall.
- [ ] Produce the final two-page client memo and a 90-second application walkthrough.

## Boundary

Everything in this benchmark is synthetic. The purpose is to demonstrate research method, engineering quality and analytical judgement without making real-world allegations about people or companies.
