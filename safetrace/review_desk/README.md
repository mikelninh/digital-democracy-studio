# SafeTrace v0.5 — Human Review Desk

The Review Desk prevents AI output from becoming public truth merely because it sounds plausible.

## Claim-level workflow

Each claim records:

- Exact wording.
- Evidence state.
- Ordinary or sensitive classification.
- Human, imported or AI-suggested origin.
- Supporting, contradicting and contextual evidence.
- Human decision, rationale and timestamp.
- Legal-review state.
- Right-of-reply state.
- Correction history.
- Explicit publication blockers.

## Publication rules

An ordinary claim requires supporting evidence and an approved human decision.

A sensitive claim additionally requires:

- Approved legal review.
- A completed or declined right-of-reply process.
- Contradictory evidence to be explicitly addressed.

Rejected and blocked claims remain visible in the internal review report. They are excluded from the public claims feed.

## Demonstration

The seed queue contains:

1. An approved verified claim about the reviewed EUR 340,000 donation slice.
2. An approved verified claim about Lobby Register entry R005553.
3. A rejected AI-suggested causal allegation because no evidence establishes that donations purchased a policy outcome.

## Build and test

```bash
python -m unittest discover -s safetrace/review_desk/tests -v
python -m safetrace.review_desk.evaluate
```

## Still required before real sensitive publication

- Independent editorial and legal reviewers.
- Authentication and reviewer identity controls.
- Immutable decision logs.
- Notification and right-of-reply delivery records.
- Corrections workflow with downstream export invalidation.
