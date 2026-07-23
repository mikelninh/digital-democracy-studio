# SafeTrace Incident Response

## Trigger events

An incident includes suspected unauthorised access, source or audit-log tampering, accidental publication of personal data, a materially false entity link, an unsupported sensitive allegation, or loss of evidence integrity.

## Immediate actions

1. Stop affected publication, export and monitoring jobs.
2. Preserve logs, source receipts, generated artefacts and relevant configuration.
3. Restrict access to the smallest response group.
4. Record the incident in a separate append-only response log.
5. Assess whether a victim, witness, private person or ongoing investigation could be harmed.

## Triage

Classify severity by:

- sensitivity of exposed or corrupted data;
- number of affected records or people;
- public reach;
- reversibility;
- effect on evidence integrity;
- legal or contractual notification duties.

## Containment and correction

- Revoke affected credentials and rotate secrets.
- Remove public access without deleting preserved evidence.
- Rebuild outputs from trusted source snapshots.
- Publish a visible correction when a public claim was affected.
- Notify an affected partner and qualified legal/privacy contact under the agreed procedure.

## Recovery

A system or case returns to service only after the cause is understood, remediation is tested, audit integrity is verified, and an authorised reviewer signs the recovery decision.

## Learning

The post-incident review records what happened, why controls failed, which records and people were affected, what was corrected, and which release gate must change. Serious incidents automatically block expansion of the pilot.

## Prototype limitation

No real victim or restricted partner data may enter the public prototype, so formal GDPR notification procedures must be completed with a qualified partner and legal/privacy adviser before a live pilot.
