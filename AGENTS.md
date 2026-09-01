# Agent instructions — Digital Democracy Studio

## Frontend work: non-negotiable information architecture

Any agent creating or changing a user-facing page MUST treat information architecture and UI/UX as part of correctness, not decoration.

A powerful backend is not a successful product if the user cannot understand the result quickly.

Before shipping frontend work, follow `docs/FRONTEND_INFORMATION_ARCHITECTURE.md`.

### Default investigation hierarchy

For investigation, evidence, policy, legal, health, trust or decision-support interfaces, present information in this order:

1. **Conclusion** — What did we find?
2. **Reason** — Why does it matter / why do we think this?
3. **Evidence** — Which exact record establishes it?
4. **Original source** — Can the user independently verify it?
5. **Confidence / gap** — What is not proven, missing or stale?
6. **Next move** — What should the analyst/user investigate or do next?

Deep technical detail, metadata, hashes, source IDs, schemas, logs and secondary evidence belong behind progressive disclosure unless they are the user's current task.

### Readability minimums

- Default body copy: **17–18px desktop**, **16–17px mobile**.
- Supporting text: never below **14px** for meaningful content.
- Labels / metadata: never below **12px**; avoid all-caps microtext for paragraphs.
- Buttons and interactive controls: **15–16px** text with generous hit areas.
- Comfortable line height: **1.5–1.7** for body copy.
- Long-form text width: approximately **55–75 characters** per line.
- Do not use tiny typography to make more information fit on screen. Remove, group or disclose information instead.

### Product rule

**Progressive disclosure over information density.**

The default view should answer the user's primary question in seconds. Detailed evidence must remain one click away, not all visible at once.

### Frontend review gate

Before declaring a UI complete, verify:

- A first-time user can state the page's purpose within 5 seconds.
- The primary conclusion is visually dominant.
- There is one obvious next action.
- Important content is comfortably readable without zooming.
- Evidence is inspectable down to the original source.
- Unknowns and limitations are visible but not competing with the main answer.
- Mobile does not become a vertical wall of equally weighted cards.
- The page has been browser-tested and visually reviewed, not only string-tested.

If the page feels overloaded, **do not solve it by shrinking typography**. Reduce simultaneous information and strengthen hierarchy.
