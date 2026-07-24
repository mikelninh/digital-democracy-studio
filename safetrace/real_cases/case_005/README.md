# SafeTrace Case 005 — Wer hat die Kindergelderhöhung auf 259 Euro beschlossen?

Case 005 is the first deliberately small **real-source publication candidate** built after the Role Simulator.

## Research question

Did the Merz government newly decide the increase of German child benefit to EUR 259 in 2026, or did the legal decision predate its term?

## Official source chain

1. **Deutscher Bundestag** — parliamentary decision on 19 December 2024 and the increase effective 1 January 2026.
2. **Bundesregierung** — implementation notice that EUR 259 is paid from January 2026.
3. **Bundesagentur für Arbeit / Familienkasse** — current official benefit information stating EUR 259 per child and month.
4. **Bundesregierung** — the Merz government entered office on 6 May 2025.

The release builder downloads the live official pages, stores their original bytes in the Evidence Vault, creates SHA-256 receipts, verifies required passages and creates parsed transformation manifests.

## Bounded verdict

> The increase to EUR 259 took effect on 1 January 2026, but the Bundestag had already passed it on 19 December 2024. The Merz government entered office on 6 May 2025. The increase is therefore not a newly enacted Merz-government measure.

This does **not** imply that the Merz government has no family policies or no role in administering existing law. Those are separate questions.

## Publication state

The source-acquisition CI may establish:

- four official originals retained;
- four immutable receipts;
- required source passages present;
- four vault-backed claims;
- valid Evidence Vault integrity.

It may **not** self-publish. Evidence, red-team and publication review remain assigned to Michael Ninh and pending until he reviews the acquired evidence.

## Impact measurement

The generated public draft contains a consent-based, browser-local test measuring:

- time to answer;
- correct political attribution before and after reading;
- confidence before and after reading;
- clarity rating.

Results are downloaded as JSON. Nothing is transmitted automatically and no aggregate real-world impact is claimed until actual sessions are collected and analysed.

## Build

```bash
python -m safetrace.real_cases.case_005.build_case \
  --output-root safetrace/real_cases/case_005/artifacts
```

The live build fails closed when an official page is unavailable, returns the wrong content type or no longer contains the required material passages.
