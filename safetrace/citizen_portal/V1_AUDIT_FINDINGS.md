# SafeTrace v1.0 readiness audit — findings

**Audit scope:** all 39 current SafeTrace records

- 7 opened Tierwohl cases;
- 14 Tierwohl and wildlife Radar candidates;
- 18 candidates across Kinder im System, Schutzlücken and Zwischen den Zuständigkeiten.

The audit is reproducible through `audit_v1.py` and the `SafeTrace v1 readiness audit` GitHub Actions workflow.

## Measured result

| Check | Result |
|---|---:|
| Records tested | 39 |
| Records with at least one public source | 39 |
| Records relying on exactly one source | 29 |
| Priority score 24 or higher | 38 |
| Priority score 29 or higher | 21 |
| Records with a research action or first sprint | 39 |
| Records with a named action owner | 0 |
| Records with both deadline and stop condition | 0 |
| Records listing possible impact metrics | 7 |
| Records with complete operational impact contract | 0 |
| Records with explicit unknowns | 7 |
| Records with a win-win-win path | 7 |
| Records with defined publication readiness | 7 |

## Priority distribution

- 30 points: 11 records
- 29 points: 10 records
- 28 points: 8 records
- 27 points: 2 records
- 26 points: 5 records
- 25 points: 2 records
- 22 points: 1 record

The current score is therefore useful as a relevance filter but weak as a portfolio-ranking mechanism. It identifies almost everything as urgent enough to accept.

## Action clarity

The audit uses a provisional 0–5 action-clarity check:

1. action text exists;
2. a concrete research verb exists;
3. a defined output such as a matrix, tracker, dataset or request exists;
4. an internal owner exists;
5. deadline and stop condition exist.

Result:

- clarity 1/5: 5 records;
- clarity 2/5: 27 records;
- clarity 3/5: 7 records;
- clarity 4–5/5: 0 records.

This does not mean the current actions are bad. It means they are instructions, not yet managed commitments.

## Is impact measurable?

### Conceptually: partly

The seven opened Tierwohl cases list useful possible metrics such as:

- official corrections;
- data coverage;
- control rates;
- waiting or processing times;
- violations, injuries or mortality;
- policy and implementation reach.

### Operationally: not yet

No current record binds all five required fields:

- baseline;
- target;
- data source;
- responsible owner;
- measurement cadence.

The honest current state is therefore:

> **Potential impact is visible. Actual impact is not yet operationally measurable.**

SafeTrace can already measure Reach and some Evidence Impact after actions begin. It cannot yet claim System or Outcome Impact without completing the impact contracts and collecting later evidence.

## Is it clear what to do?

### At research level: yes

Every case has a next action or first sprint.

### At operating level: no

The current records usually do not say:

- who owns the task;
- which institution must answer or act;
- what exact deliverable is due;
- by what date;
- when to stop, pause, refer or close;
- which metric changes the verdict or demonstrates progress.

That is the most important gap for v0.4.

## Fairness finding

The opened Tierwohl cases already show strong discipline:

- verified claims and unknowns are separated;
- no automatic corruption or guilt inference;
- win-win-win paths are described;
- publication and review states are visible.

The 32 Radar candidates do not yet carry the same fields. They are safe as discovery cards, but they are not ready to become active investigations until migrated into a Case Contract.

## Source finding

Twenty-nine records currently rely on one source. A single authoritative source may be enough to verify a narrow starting fact, especially an official data gap. It is generally not enough for:

- causal claims;
- national implementation judgments;
- outcome claims;
- claims about motive or responsibility;
- comparative performance conclusions.

v1.0 should label single-source leads visibly and require either corroboration or a narrowly bounded verdict.

## What the current tool does well

- discovers overlooked public-interest questions;
- keeps questions falsifiable;
- prioritises vulnerable groups and possible harm;
- uses public primary sources;
- prevents scores from being presented as guilt;
- creates compelling story framing;
- proposes a plausible first research move.

## What the next version must fix

1. Separate Need, Feasibility, Publication Readiness and Impact Readiness.
2. Enforce maximum five active investigations.
3. Require Case Contracts before candidates enter active work.
4. Assign owner, target actor, deliverable, deadline and stop condition.
5. Require unknowns and counterevidence on every accepted case.
6. Add baseline, target, source, cadence and attribution to impact tracking.
7. Show single-source dependency and source diversity.
8. Create explicit close, refer and refute paths.
9. Measure user comprehension of priority versus verdict.
10. Publish actions and subsequent responses, not only initial findings.

## Audit conclusion

> **SafeTrace is already a strong civic discovery and framing tool. It is not yet a complete impact operating system.**

The next version should invest less in finding additional high-scoring cases and more in moving a deliberately small portfolio through action, response, correction, publication and measurable follow-up.
