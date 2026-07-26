# Spuren im System — Staffel Tierwohl v0.2

**Öffentliche Belege. Faire Prüfung. Messbare Veränderung.**

`Spuren im System` is the storytelling layer. The TRACE Loop is the investigation method underneath it.

## Case names

| Case | Story title | Research title |
|---|---|---|
| 012 | **Die unsichtbaren Toten** | Bundesweite Mortalitätsdaten in der Tierhaltung |
| 013 | **Die Kamera-Lücke** | Schwellenwerte für Videoüberwachung in Schlachtbetrieben |
| 014 | **Die Reise ohne Zeugen** | Kontrolle von Tiertransporten bis zum Zielort |
| 015 | **Das Rätsel der zehn Kontrollen** | Berliner Kontrollzahlen: 26 oder 36? |
| 016 | **Die Route der falschen Pässe** | Illegaler Hunde- und Katzenhandel nach Deutschland |
| 017 | **Die geheime Versuchszahl** | Transparenz bei militärischen Tierversuchen |
| 018 | **Das Label mit den blinden Flecken** | Reichweite der Tierhaltungskennzeichnung |

Creative titles may create curiosity. The factual research title and bounded verdict remain visible beside them.

## TRACE

1. **Test** — concrete, falsifiable, relevant and safely investigable question.
2. **Register** — sources, dates, definitions and retention status.
3. **Assemble** — supporting evidence, counterevidence and alternatives.
4. **Challenge** — strongest counterposition, harm review and right of reply.
5. **Evaluate** — bounded verdict, action, impact, monitoring and correction.

## Priority test

Six dimensions receive 0–5 points:

- possible harm;
- evidence access;
- actionability;
- urgency;
- public value;
- fairness and review capacity.

The score ranks public value and investigability. It never represents truth, guilt or publication readiness.

Current result:

- **29/30:** Cases 013, 018 and 012;
- **26/30:** Cases 014, 015 and 016;
- **22/30:** Case 017, requiring a bounded data and security review first.

Run:

```bash
python safetrace/animal_welfare_series/prioritize.py --json
```

## Impact

[`impact_log.json`](impact_log.json) records separate 30, 90 and 365 day checkpoints for:

1. evidence impact;
2. accountability impact;
3. behaviour or policy impact;
4. animal outcome impact.

Reach remains separate from animal-welfare outcomes.

## Governance implemented

See [`governance/README.md`](governance/README.md).

Implemented now:

- editorial, animal-welfare and legal/privacy review packets;
- conflict declaration and pass/block decisions;
- correction, complaint and appeal routes;
- standard right-of-reply packets;
- public-source registry and Evidence Vault hand-off;
- accessibility and comprehension protocol;
- partner criteria for sensitive material;
- dedicated GitHub forms;
- fail-closed CI checks.

Still requires real external work:

- named independent reviewers;
- original-byte and hash backfill for all sources;
- external accessibility and comprehension tests;
- a named qualified partner for sensitive material.

A template does not count as a completed review.

## Public participation

Supported:

- browser-local prioritiser;
- Public-Source case proposals;
- factual corrections;
- complaints and harm concerns;
- attributable independent reviews.

Not supported:

- non-public documents;
- personal or medical details;
- private addresses;
- automatic accusation, naming or publication;
- operational case referral.

## Release checks

```bash
python safetrace/animal_welfare_series/prioritize.py --json
python safetrace/animal_welfare_series/accessibility_check.py
python safetrace/animal_welfare_series/validate.py
```

Static accessibility checks target WCAG 2.2 AA structure but do not claim conformance. External testing is still required.

## Next actions

1. Ask LAGeSo to clarify Case 015.
2. Prepare the 16-state data request for Case 012.
3. Obtain threshold coverage data for Case 013.
4. Build the demand-to-law matrix for Case 018.
5. Recruit one reviewer for each independent track.
6. Test the prioritiser with five citizens.
7. Backfill source snapshots and hashes.
8. Publish a 30-day findings note.
