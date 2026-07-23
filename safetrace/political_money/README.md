# SafeTrace v0.4 — Political Money Graph

The Political Money Graph connects official donation disclosures and official lobbying records while preserving the difference between documented association and proven causation.

## First public slice

The reviewed seed connects:

- Five DVAG donation disclosures from January and February 2026.
- Four recipient parties.
- The organisation's official Lobby Register entry, R005553.
- Selected declared policy interests from that register entry.

The seed totals EUR 340,000. Private addresses published in the source records are deliberately omitted.

## Relationship vocabulary

The graph currently permits only:

- `donated_to`
- `registered_as`
- `declares_interest_in`

Every edge requires provenance. The graph rejects donation edges without a positive amount, received date and official source.

It deliberately has no edge named `influenced`, `bought`, `corrupted` or `caused`.

## Build and test

```bash
python -m unittest discover -s safetrace/political_money/tests -v
python -m safetrace.political_money.build_graph
```

## Next v0.4 increments

- Parse all corporate and organisational donations from official annual pages.
- Use Lobby Register API V2 for exact register-number retrieval and version history.
- Add entity-match proposals that remain unpublished until human approval.
- Add timelines for legislative projects and published official meetings.
- Show gaps and ambiguous matches rather than silently joining them.

## Publication boundary

A donation is a verified financial event. A lobby entry is a verified registration event. A declared policy interest is a verified declaration. Their coexistence does not establish bribery, unlawful influence or a causal link to any government decision.
