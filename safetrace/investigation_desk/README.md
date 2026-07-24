# SafeTrace v1.6 — Internal Investigation Desk Foundation

The Investigation Desk is the authoritative internal workflow layer connecting the Case Charter, Evidence Vault, Claim Ledger and Agent Queue.

It is deliberately separate from the public portal. Chat messages and spreadsheets are not treated as the system of record.

## Implemented views

- Inbox
- Cases
- Sources
- Claims
- Graph
- Timeline
- Review
- Publish
- Corrections
- Agents
- Audit

## Roles and least privilege

- Intake Researcher
- Investigator
- Evidence Manager
- Reviewer
- Legal Reviewer
- Publisher
- Admin

Every action checks:

- an authenticated session context;
- role permission;
- session data-zone ceiling;
- case and record state;
- independent review or publication approval where required.

The v1.6 release uses synthetic authenticated sessions to verify the authorisation model. It does **not** claim that a production identity provider, MFA, session revocation or partner tenant isolation is already configured.

## Workflow guarantees

- cases enter through intake and explicit acceptance;
- records can only be added to active cases;
- agent output enters as `awaiting_human` and can only be accepted for further review;
- record creators cannot perform their own final review;
- publication requesters cannot approve their own publication;
- only approved public claims can enter a public export;
- internal comments, tasks and agent proposals are excluded from public export;
- corrections make published items visibly stale;
- consequential actions create hash-chained audit events;
- the complete audit chain is independently verifiable.

## Run locally

```bash
python -m unittest discover -s safetrace/investigation_desk/tests -v
python -m safetrace.investigation_desk.contracts --write safetrace/investigation_desk/artifacts/investigation-desk-contracts-1.6.json
python -m safetrace.investigation_desk.build_release_artifacts --output-root safetrace/investigation_desk/artifacts
```

## Truthful boundary

v1.6 provides deterministic workflow records, authorisation policy, role-filtered read models, public-export separation and auditability for public-source and synthetic fixtures.

Still required before restricted partner use:

- production authentication and MFA;
- secure session and secrets management;
- tenant isolation;
- encrypted production storage;
- independent penetration testing;
- partner-specific lawful basis, DPIA, retention and deletion controls;
- qualified legal/editorial operating approval.

## Next

v1.7 will run Case 004 through the complete Desk path and benchmark manual versus SafeTrace-assisted work without lowering evidence or review standards.
