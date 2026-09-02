# Frontend Information Architecture Standard

This document defines the default UI/UX standard for Digital Democracy Studio / SafeTrace products.

## Principle

**The interface is part of the evidence system.**

A correct backend can still produce an unusable or misleading product if the frontend gives every fact the same visual weight, hides the research question, or makes users read a report before they understand the investigation.

The frontend should reduce cognitive load without hiding uncertainty.

For proof-of-work experiences, the goal is not merely to explain the project. It is to let the reviewer **experience the judgement**: inspect, compare, make a call, reveal evidence and understand what remains unresolved.

## The seven-layer investigation hierarchy

### 1. Question / mandate
Start with the exact question being investigated.

Examples:
- `Did industry advocacy contribute to this policy delay?`
- `Where does this procurement money actually go?`
- `Are these differently named vessels the same physical asset?`

The question frames the scope and prevents an answer from appearing pre-baked.

### 2. Current assessment
Give the best-supported answer currently available.

Prefer `Current assessment`, `What we found`, or `Best-supported answer` over `Conclusion` when the investigation remains open.

Examples:
- `Advocacy documented: YES`
- `Requested delay enacted: YES`
- `Direct causation: NOT PROVEN`
- `Current beneficial owner: UNRESOLVED`

Keep this short, large and visually dominant.

### 3. Why
Show the smallest reasoning chain needed to understand the assessment.

Prefer a timeline, relationship path, comparison or 2–4 decisive facts over explanatory paragraphs.

### 4. Evidence
Let the user inspect the material records that support or challenge the assessment.

Whenever possible, make evidence interactive:
- click a relationship;
- inspect a timeline event;
- compare two identities;
- reveal a contradiction;
- make a judgement before showing the analyst answer.

The reviewer should learn by interacting, not by reading a feature inventory.

### 5. Original source
Evidence detail should expose:
- publisher;
- authority level;
- source type;
- exact location / page / section / record ID;
- relevant date/version;
- what it establishes;
- what it does **not** establish;
- direct original-source link.

The user must never need to trust a model-generated paraphrase when the original can be inspected.

### 6. Gap / uncertainty
Separate:
- known;
- inferred;
- disputed;
- missing;
- stale/version-sensitive.

Make the **biggest open gap** easy to find. Do not bury it in legalistic caveats.

### 7. Next move
Always answer: **what evidence would most change the assessment?**

One high-value next research move is better than six equal buttons.

---

## Proof-of-work experience pattern

A hiring proof should not feel like a project README rendered as a website.

Default reviewer journey:

1. **Challenge me** — make a judgement on a small adversarial case.
2. **Show me a real case** — choose a question that is interesting without setup.
3. **Let me inspect** — click relationships, dates or claims to open evidence.
4. **Show me the analyst call** — reveal the current assessment after the evidence is understandable.
5. **Show me where it could be wrong** — expose the strongest gap or competing explanation.
6. **Show me the next move** — identify the highest-value next source.
7. **Only then show the machinery** — benchmark, schemas, CI, provenance and architecture.

**Do not tell the reviewer that the system is rigorous when you can let them test its rigour.**

---

## Progressive disclosure

### Default screen
The first viewport should normally contain only:
- the research question / target;
- a one-line context;
- either a small interaction or the current assessment;
- one primary action.

### Second layer
Opened by interaction:
- reasoning path;
- timeline details;
- graph relationships;
- source comparison;
- contradictions;
- alternative hypotheses.

### Third layer
Expert / audit detail:
- hashes;
- evidence IDs;
- raw metadata;
- retrieval receipts;
- schema fields;
- logs;
- evaluation traces.

These are crucial for trust, but usually harmful in the default view.

---

## Typography and readability

Do not shrink typography to fit information.

Recommended minimums:

| Element | Desktop | Mobile |
| --- | ---: | ---: |
| Body | 17–18px | 16–17px |
| Important supporting text | 16–18px | 16px |
| Secondary metadata | 13–14px | 13–14px |
| Labels | 12–13px | 12–13px |
| Button text | 15–16px | 15–16px |
| H1 | 44–64px | 36–48px |
| H2 | 30–42px | 28–36px |
| H3 | 20–26px | 19–24px |

Additional rules:
- body line height 1.5–1.7;
- headings 1.0–1.2;
- 55–75 characters per line for reading text;
- avoid long uppercase strings;
- avoid low-contrast grey for important evidence;
- do not use 9–11px text for meaningful content.

---

## Visual hierarchy

A page should not look like twelve equally important cards.

Preferred pattern:

**One question**
→ **one assessment or interaction**
→ **one main visual / timeline / graph**
→ **one explicit gap**
→ **one next move**
→ deeper evidence on demand.

Whitespace is functional. Empty space is preferable to stuffing metadata into every corner.

---

## Investigation page template

### Header
Small product identity + case status (`REAL PUBLIC-SOURCE CASE`, retrieval date).

### Hero — Question
Exact research question + one-sentence context. Avoid marketing copy that pushes the investigation below the fold.

### Current assessment
2–3 plain-language findings maximum.

Example:

`Advocacy documented — YES`

`Requested delay enacted — YES`

`Lobbying caused it — NOT PROVEN`

### Why
One chronological timeline, graph, comparison or compact reasoning path.

### Evidence
Clickable evidence in the main visual. Each material node has `Check source`, `Why?` or an equivalent affordance.

### Evidence drawer
Large readable text. Original source link is obvious. Source limitation is shown directly next to support.

### Biggest open gap
One explicit unresolved issue or strongest competing explanation.

### Next move
One recommended investigation step. Explain what new evidence would change the assessment.

---

## Five-second test

Give the rendered page to someone unfamiliar with the project for five seconds, then ask:

1. What question is being investigated?
2. What is the current answer, if shown?
3. What can you click or test?
4. What remains uncertain?
5. What evidence should be collected next?

If these answers are unclear, the page is not done.

## Thirty-second proof test

A proof-of-work page should also answer:

1. Did I **do something**, or only read?
2. Did I encounter a non-obvious judgement call?
3. Could I inspect an original source?
4. Did the interface make uncertainty clearer rather than merely adding caveats?
5. Did I learn something memorable about the candidate's way of thinking?

If not, the proof is still too passive.

---

## UI review checklist

A frontend PR should not be considered finished unless a reviewer confirms:

- [ ] research question understandable in 5 seconds;
- [ ] current assessment is clearly labelled as current/bounded rather than omniscient;
- [ ] reviewer has something meaningful to inspect, compare or decide;
- [ ] body text comfortably readable at 100% browser zoom;
- [ ] no meaningful text below minimum font sizes;
- [ ] no information wall of equally weighted cards;
- [ ] evidence progressively disclosed;
- [ ] every consequential claim can reach an original source;
- [ ] strongest uncertainty / gap is explicit;
- [ ] one clear highest-value next research move;
- [ ] technical proof is secondary to the investigative experience;
- [ ] mobile layout manually inspected;
- [ ] real Chromium/browser QA performed;
- [ ] screenshot artifacts reviewed visually.

## Final rules

**Question → Current assessment → Why → Evidence → Original source → Gap → Next move.**

**If the frontend feels busy, reduce information before reducing font size.**

**Do not tell the reviewer I can investigate. Let them investigate with me.**
