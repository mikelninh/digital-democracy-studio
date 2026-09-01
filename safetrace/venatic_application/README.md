# Venatic application package

One-link proof-of-work package for the **Junior Intelligence Analyst** application.

## Primary experience

`index.html`

The page is intentionally not a generic portfolio. It tells one evidence-backed story:

1. a deliberately messy 28-source synthetic case;
2. blind first-pass analysis scored against hidden gold;
3. five-source evidence-budget decision;
4. final assessment;
5. source-independence and hypothesis discipline;
6. how the project was built using an outcome → constraints → agents → verification loop.

## Verified benchmark

The underlying `safetrace/venatic_challenge` benchmark is CI-tested separately.

- Initial sources: 18
- Optional sources: 10
- Optional acquisition budget: 5
- Blind first pass: **95/100**
- Budgeted pass: **100/100**
- Critical failures: **0**

These are synthetic benchmark scores, not claims of production analyst performance.

## Package files

### Reviewer-facing
- `index.html` — the one-link application experience
- `APPLICATION_NOTE.md` — why this proof exists and what it demonstrates
- `PRODUCT_ARCHITECT_STORY.md` — how the work was directed and verified

### Submission-ready
- `APPLICATION_MESSAGE.md` — concise application message
- `CV_TAILORING.md` — targeted headline, profile, project bullets and skills ordering
- `WALKTHROUGH.md` — 90-second demo script

### Candidate prep
- `INTERVIEW_PREP.md` — likely analyst questions mapped to concrete proof
- `SEND_CHECKLIST.md` — final claims, links and submission QA

## Quality gate

`.github/workflows/venatic-application.yml` runs a real Chromium browser against the page and verifies:

- the core application story renders;
- the four-stage case interaction works;
- an ownership edge opens the correct evidence;
- the research-budget view surfaces circular reporting;
- the final assessment preserves an unresolved item;
- screenshots are uploaded as CI artifacts.

The goal is to review a **working product increment**, not merely the HTML diff.

## Boundary

All allegations and entities inside the Meridian Atlas challenge are synthetic. The separate Venatic live-source boundary case is used only to demonstrate evidence acquisition and fail-closed behavior; no unsupported ownership or risk allegation is made about Venatic or any real person.
