# Frontend Information Architecture Standard

This document defines the default UI/UX standard for Digital Democracy Studio / SafeTrace products.

## Principle

**The interface is part of the evidence system.**

A correct backend can still produce an unusable or misleading product if the frontend gives every fact the same visual weight, hides the answer in metadata, or makes users read tiny text.

The frontend should reduce cognitive load without hiding uncertainty.

## The six-layer investigation hierarchy

### 1. Conclusion
Answer the user's actual question first.

Examples:
- `Requested delay enacted: YES`
- `Direct causation: NOT PROVEN`
- `Ownership cannot yet be established`

Keep this short, large and visually dominant.

### 2. Reason
One or two sentences explaining why the conclusion matters and the core basis for it.

Do not dump the evidence ledger here.

### 3. Evidence
Show only the strongest evidence needed to understand the conclusion. Prefer a timeline, relationship graph or 2–4 key facts over a wall of cards.

Every material evidence item should have a clear `Why?`, `Evidence`, or `Check source` interaction.

### 4. Original source
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

### 5. Confidence / gap
Separate:
- known;
- inferred;
- disputed;
- missing;
- stale/version-sensitive.

Do not let a yellow warning compete visually with the core answer unless the uncertainty changes the decision.

### 6. Next move
Always answer: **what is the highest-value next step?**

One recommended next action is better than six equal buttons.

---

## Progressive disclosure

### Default screen
The first viewport should normally contain only:
- the question / target;
- the answer;
- the single most useful explanation;
- one primary visual or evidence summary;
- the next action.

### Second layer
Opened by interaction:
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

Use contrast, spacing, size and grouping to communicate priority.

A page should not look like twelve equally important cards.

Preferred pattern:

**One answer**
→ **one main visual / timeline / graph**
→ **one next action**
→ deeper evidence on demand.

Whitespace is functional. Empty space is preferable to stuffing metadata into every corner.

---

## Investigation page template

### Header
Small product identity + case status (`REAL PUBLIC-SOURCE CASE`, retrieval date).

### Hero
Question + 1-sentence context. Avoid giant marketing copy that pushes the result below the fold.

### Verdict
2–3 large, plain-language claims maximum.

Example:

`Advocacy documented — YES`

`Requested delay enacted — YES`

`Lobbying caused it — NOT PROVEN`

### Main evidence
One chronological timeline or graph.

Each node has `Check source`.

### Evidence drawer
Large readable text. Original source link is obvious. Source limitation is shown directly next to support.

### What remains unknown
Short explicit list, not a warning dashboard.

### Next move
One recommended investigation step plus optional alternatives behind `More`.

---

## Five-second test

Give the rendered page to someone unfamiliar with the project for five seconds, then ask:

1. What is this page about?
2. What did it find?
3. What is uncertain?
4. What can you click to verify it?
5. What should happen next?

If these answers are unclear, the page is not done.

---

## UI review checklist

A frontend PR should not be considered finished unless a reviewer confirms:

- [ ] purpose understandable in 5 seconds;
- [ ] conclusion visible without scrolling on common laptop viewport;
- [ ] body text comfortably readable at 100% browser zoom;
- [ ] no meaningful text below minimum font sizes;
- [ ] no information wall of equally weighted cards;
- [ ] evidence progressively disclosed;
- [ ] every consequential claim can reach an original source;
- [ ] uncertainty is explicit;
- [ ] one clear primary next action;
- [ ] mobile layout manually inspected;
- [ ] real Chromium/browser QA performed;
- [ ] screenshot artifacts reviewed visually.

## Final rule

**If the frontend feels busy, reduce information before reducing font size.**
