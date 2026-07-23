# SafeTrace Incident Response Plan

## Status

Draft for tabletop testing. It has not yet been exercised against a deployed sensitive-data system.

## Severity

### SEV-1 — Critical

Confirmed or credible exposure, alteration or loss of sensitive evidence; compromised privileged account; active attacker; unsafe public disclosure; or incident that may endanger a victim or witness.

### SEV-2 — High

Unauthorised access attempt with material risk, malware detection, integrity-check failure, broken access boundary, or major availability loss.

### SEV-3 — Moderate

Failed job, parser error, source outage, erroneous public status or other event without current evidence of sensitive-data exposure.

## Immediate response

1. Protect people first. Escalate any immediate physical danger to the qualified partner and competent emergency channel.
2. Stop the affected processing path without deleting evidence.
3. Preserve logs, hashes, timestamps, credentials state and relevant system snapshots.
4. Revoke or rotate affected credentials and isolate compromised components.
5. Name one incident commander and open a timestamped incident record.
6. Notify the partner's security, legal and data-protection contacts using the agreed matrix.
7. Do not contact an investigation subject or publish details without partner approval.

## Evidence handling during an incident

- Preserve originals and record every emergency action.
- Use read-only or forensic copies where feasible.
- Do not overwrite suspicious files, logs or snapshots.
- Document who accessed what, when and why.
- Record hash changes and explain expected transformations.
- Separate verified facts from working hypotheses.

## Decision points

The incident team determines, with qualified reviewers:

- Whether personal data were affected.
- Whether notification duties and deadlines apply.
- Whether victims, witnesses, partners, authorities or affected organisations must be informed.
- Whether public material must be corrected, withdrawn or marked under review.
- Whether case packs or referrals generated from affected data must be invalidated.

## Recovery

Recovery requires:

- Identified root cause or documented containment rationale.
- Restored system from a trusted state.
- Revalidated evidence hashes and access permissions.
- Re-run of affected extraction and review outputs where necessary.
- Explicit security and partner approval before sensitive processing resumes.

## Post-incident review

Within the partner-agreed timeframe:

- Publish an internal timeline and root-cause analysis.
- Record what detection worked or failed.
- Identify affected claims, exports and recipients.
- Assign corrective controls and owners.
- Test the fix.
- Preserve a public correction or transparency note where safe and appropriate.

## Required exercises before v1.0

- Compromised reviewer account.
- Malicious evidence upload.
- Accidental public exposure.
- False entity match already included in an export.
- Loss of the primary evidence store.
- Model provider or connector data-handling incident.

A plan is not considered implemented until a tabletop exercise has been completed, gaps recorded and remediation approved.
