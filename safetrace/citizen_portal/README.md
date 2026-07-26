# SafeTrace Citizen Portal v0.3

**Public-source investigations for everyone — without automatic accusations.**

The portal lets citizens:

- test a proposed case with the TRACE priority model;
- inspect high-potential candidate cases and their primary sources;
- submit a structured public-source case;
- see why a case is prioritised, narrowed, deferred or rejected;
- distinguish priority, evidence strength and publication readiness;
- follow corrections, replies and impact over time.

## TRACE

1. **Test** — concrete, falsifiable, publicly relevant question.
2. **Register** — primary sources, dates, definitions and provenance.
3. **Assemble** — supporting evidence, counterevidence, timeline and alternatives.
4. **Challenge** — strongest opposing case, right of reply, privacy and harm review.
5. **Evaluate** — bounded verdict, next action, impact contract and correction path.

## Priority model

Six dimensions are scored from 0 to 5:

- possible harm;
- access to primary evidence;
- actionability;
- urgency;
- public value;
- ability to investigate fairly.

Safety and capacity penalties can lower or block a case. The score never evaluates truth, guilt, scandal or the moral worth of the person submitting it.

- **24–30:** prioritise;
- **18–23:** accept only with a bounded data sprint;
- **12–17:** clarify or conduct a preliminary check;
- **0–11:** do not accept or refer elsewhere.

## Public-alpha boundaries

Allowed:

- official documents and public registers;
- court decisions and public datasets;
- public company or organisation statements;
- public parliamentary and administrative records;
- clearly licensed or lawfully quotable material.

Not allowed:

- confidential or leaked documents;
- private addresses, health data or login credentials;
- covert access, impersonation, hacking or doxxing;
- unverified naming of private individuals;
- automatic guilt decisions or publication;
- emergency reports that should go directly to police, veterinary authorities or emergency services.

## Citizen moderation flow

1. automated completeness and safety checks;
2. human triage and duplicate search;
3. visible TRACE score with reasons;
4. bounded case charter or transparent rejection;
5. source registry and counterevidence search;
6. right of reply where a person or organisation could be harmed;
7. editorial/domain/legal review according to risk;
8. publication, correction, closure or referral;
9. impact review after 30, 90 and 365 days.

## Current release state

- public-source intake: enabled;
- sensitive intake: disabled;
- automatic publication: disabled;
- automatic guilt decisions: disabled;
- public candidate radar: enabled;
- citizen-local scoring: enabled;
- independent review still required for sensitive publication.

## Candidate radar

[`candidates.json`](candidates.json) contains current discovery candidates. A candidate is not an allegation and has not necessarily been accepted as a full investigation.
