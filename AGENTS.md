# Agent instructions — Digital Democracy Studio

## Frontend work: non-negotiable information architecture

Any agent creating or changing a user-facing page MUST treat information architecture and UI/UX as part of correctness, not decoration.

A powerful backend is not a successful product if the user cannot understand the research question quickly, inspect the evidence or experience the judgement involved.

Before shipping frontend work, follow `docs/FRONTEND_INFORMATION_ARCHITECTURE.md`.

### Default investigation hierarchy

For investigation, evidence, policy, legal, health, trust or decision-support interfaces, present information in this order:

1. **Question / mandate** — What exactly are we trying to establish?
2. **Current assessment** — What does the best available evidence support right now?
3. **Why** — What is the smallest reasoning chain that explains the assessment?
4. **Evidence** — Which records, relationships, dates or contradictions matter?
5. **Original source** — Can the user independently verify them?
6. **Gap / uncertainty** — What is not proven, missing, disputed or stale?
7. **Next move** — Which next source or action would most change the assessment?

Prefer `Current assessment` or `What we found` over `Conclusion` when the investigation remains open.

Deep technical detail, metadata, hashes, source IDs, schemas, logs and secondary evidence belong behind progressive disclosure unless they are the user's current task.

### Proof-of-work experience rule

For hiring proofs and demos, do not render a README as a website.

Whenever possible, let the reviewer:

- inspect a relationship;
- compare two records;
- make an identity or evidence judgement;
- reveal a contradiction;
- open the original source;
- compare their call with the analyst assessment;
- see the strongest remaining gap and best next research move.

The preferred reviewer journey is:

**Challenge → Explore → Decide → Reveal → Verify → Find the gap → Choose the next move.**

The technical architecture should be available, but secondary to the experience.

### Readability minimums

- Default body copy: **17–18px desktop**, **16–17px mobile**.
- Supporting text: never below **14px** for meaningful content.
- Labels / metadata: never below **12px**; avoid all-caps microtext for paragraphs.
- Buttons and interactive controls: **15–16px** text with generous hit areas.
- Comfortable line height: **1.5–1.7** for body copy.
- Long-form text width: approximately **55–75 characters** per line.
- Do not use tiny typography to make more information fit on screen. Remove, group or disclose information instead.

### Product rule

**Progressive disclosure over information density. Experience over exposition.**

The default view should make the research question obvious in seconds. Evidence and reasoning should become visible through interaction rather than appearing as a wall of explanation.

### Frontend review gate

Before declaring a UI complete, verify:

- A first-time user can state the research question within 5 seconds.
- The current assessment is clearly bounded and labelled.
- There is something meaningful to click, inspect, compare or decide.
- There is one obvious highest-value next research action.
- Important content is comfortably readable without zooming.
- Evidence is inspectable down to the original source.
- Unknowns and limitations are visible without becoming a disclaimer wall.
- Mobile does not become a vertical wall of equally weighted cards.
- The page has been browser-tested and visually reviewed, not only string-tested.

If the page feels overloaded, **do not solve it by shrinking typography**. Reduce simultaneous information and strengthen hierarchy.

## Final proof rule

**Do not tell the reviewer I can investigate. Let them investigate with me.**
