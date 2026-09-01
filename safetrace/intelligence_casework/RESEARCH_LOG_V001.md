# Research Log V-001

**Case:** Northstar Components — ownership, payment-route and screening review  
**Status:** Synthetic training fixture  
**Purpose:** Make the analytical path reproducible and handoff-ready. This log records what was searched, why it mattered, what was found, what was not established and the next best source.

## Research discipline

A useful investigation log is not a diary of browser tabs. Every step should answer one of four questions:

1. **Identity** — are these records about the same legal or natural person?
2. **Relationship** — what ownership, management, financial or commercial link is actually evidenced?
3. **Risk** — which fact pattern warrants deeper verification, without turning a signal into an allegation?
4. **Gap** — what material question remains unresolved, and which source is most likely to resolve it?

Searches are preserved at the level needed for another analyst to reproduce the work. Consequential conclusions require a source record and an atomic claim, not merely a note in this log.

## Log

| Step | Question | Search / collection pattern | Result | Evidence | Analytical decision | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | What is the target's legal identity? | Exact legal name + registration number in authoritative DE corporate records | Synthetic filing identifies Northstar Components GmbH | S1 | Resolve target as E1 | Build shareholder chain |
| 02 | Who directly owns the target? | Shareholder / capital section of target filing | Meridian 70%; Alder 30% | S1 | Create two `OWNS` edges; do not infer UBO | Resolve both shareholders independently |
| 03 | Is Meridian the same entity as similarly named records? | Exact company number first; name variants second | Stable synthetic GB identifier resolves E2 | S2 | Merge variants only where stable identifier agrees | Extract Meridian shareholders |
| 04 | Who owns Meridian? | Confirmation statement / statement of capital | Asterion 60%; Helix 40% | S2 | Create sourced upstream ownership edges | Resolve Asterion and Helix separately |
| 05 | Can the Northstar indirect interests be calculated? | Trace documented equity percentages only | Asterion 42%; Helix 28% indirect economic interest | S1, S2 | State arithmetic; do not equate automatically with practical control | Search for voting/control arrangements if material |
| 06 | Who is behind Helix Nominees? | Supplied filing set + beneficial-owner fields | Natural person not established in supplied record | S4 | Preserve as material gap | Seek current authoritative BO/PSC data or client-authorised KYC |
| 07 | Is the named director current? | Corporate filing history + archived leadership page | Sources conflict | S1, S5 | Mark contradiction; weight official source more highly but avoid definitive current-status claim | Retrieve latest filing history/effective date |
| 08 | What is the supplier relationship? | Contract party names, registration details, account details | Eastbridge is named supplier and original payment counterparty | S6 | Resolve E6 and relationship to target | Compare later payment instructions |
| 09 | Did payment details change? | Compare supplied contract with later payment instruction | Later instruction requests payment to Oriole Settlement Services FZE | S6, S7 | Flag discrepancy only; no fraud inference | Authenticate instruction and beneficiary-account ownership |
| 10 | Is Oriole the same company as Eastbridge or a documented affiliate? | Legal identifiers, address, directors, explicit contract references | No supplied evidence establishes `SAME_AS` or group relationship | S6, S7 | Keep entities separate | Seek rationale / agency / settlement agreement |
| 11 | Does director name produce a sanctions candidate? | Normalised name + transliteration / fuzzy candidate generation | Marek Vostryk candidate returned | S8 | Candidate enters review queue; not a finding | Compare DOB, nationality and stable identifiers |
| 12 | Is the sanctions candidate the same person? | Field-by-field identity comparison | DOB and nationality conflict; no stable identifier overlap | S8 | Reject `SAME_AS`; retain auditable rejected candidate | Refresh against authoritative live lists in real engagement |
| 13 | Is there adverse litigation in the supplied court fixture? | Target legal name + identifier in bounded synthetic docket set | No adverse finding returned | S9 | Record bounded negative evidence, not universal absence | Expand jurisdictions / aliases only if case scope requires |
| 14 | What alternative explanations fit the payment anomaly? | Structured hypothesis check | Legitimate settlement agent, factoring, treasury arrangement, error or misconduct remain possible | S6, S7 | Avoid causal conclusion | Collect evidence that discriminates among hypotheses |
| 15 | What is the next best use of analyst time? | Rank unresolved questions by decision impact × resolvability | BO gap and payment authority rank first | Case synthesis | Produce priority collection plan | Handoff / client request list |

## Search-pattern library

The following patterns are deliberately generic so they can be adapted to the jurisdiction and data source available in a real engagement.

### Corporate identity

- `"<exact legal name>" "<registration number>"`
- `"<exact legal name>" director`
- `"<exact legal name>" shareholder`
- legal-name variants including diacritics, transliterations, historical names and legal-suffix variants
- stable identifier first; fuzzy name matching only for candidate generation

### Ownership and control

- target filing → direct shareholders → resolve each shareholder → repeat upstream
- distinguish `OWNS`, `CONTROLS`, `DIRECTOR_OF`, `BRAND_OF`, `SUBSIDIARY_OF`, `NOMINEE_FOR` and `RELATED_TO`
- calculate indirect economic interest separately from control
- record the as-of date for every ownership edge

### Litigation / regulation

- exact legal name + registration number where searchable
- exact legal name + regulator / court / enforcement vocabulary relevant to the jurisdiction
- search aliases and historical names only after they are independently resolved
- preserve no-hit scope: database, jurisdiction, search fields, date and aliases used

### Media archives

- exact legal name and directors first
- event-specific terms second
- archive date and original publication date separately
- treat media as a lead or corroborating source unless the underlying primary record is unavailable and the report itself is the relevant fact

### Screening

- candidate generation can use name normalisation and fuzzy matching
- resolution must compare available DOB, nationality, identifiers, addresses, roles and temporal fit
- record why a candidate was accepted, rejected or left unresolved
- current authoritative datasets must be refreshed at the point of a real consequential decision

## Source hierarchy for this case

The source hierarchy is **question-dependent**, not a universal truth score.

For legal corporate identity and filed ownership, current authoritative registry records normally outrank company web pages and aggregators. For the fact that a company publicly represented somebody as a director on a particular date, an archived company page may itself be primary evidence. For the authenticity of a payment instruction, neither a registry nor a web page replaces direct verification through a known counterparty channel.

That distinction prevents a simplistic "official source always wins" rule from obscuring what each source is actually capable of proving.

## Handoff state

Another analyst can continue V-001 without repeating completed work by starting with four unresolved tasks:

1. identify the natural-person owner(s), if any, behind Helix's relevant stake;
2. authenticate the beneficiary change and establish Oriole's commercial role/account ownership;
3. retrieve fresh director filing history; and
4. refresh authoritative sanctions screening at decision time.

Anything beyond those steps should be justified by what the new evidence changes. The aim is not maximum browsing. It is **minimum sufficient research for a defensible decision**.
