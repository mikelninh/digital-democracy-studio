# SafeTrace Threat Model

## Protected interests

SafeTrace must protect victims and witnesses, prevent unsupported accusations, preserve source provenance, and keep reviewers accountable for consequential decisions.

## Trust boundaries

1. Public official sources and public dashboards.
2. Automated source-fetching and parsing jobs.
3. Draft analytical records and entity suggestions.
4. Human editorial and legal review.
5. Restricted partner data and exports — not enabled in the public prototype.

## Main threats

| Threat | Example | Required defence |
|---|---|---|
| Source poisoning | A page is replaced or manipulated after collection | Canonical URL, retrieval time, raw bytes, SHA-256 receipt, previous-version comparison |
| Identity collision | Two people or companies with similar names are merged | Stable identifiers, corroborating records, versioned entity decisions, human approval |
| AI overstatement | A correlation is described as corruption or guilt | Evidence-state labels, publication gate, contradiction review, no autonomous publication |
| Evidence tampering | A review or access event is altered after the fact | Append-only hash-chained audit events and independent storage in a live system |
| Sensitive-data exposure | Victim, witness or private-address data reaches the public edition | Data classification, redaction profiles, least privilege, retention limits, release checks |
| Insider misuse | An authorised user searches or exports records without purpose | Role-based access, purpose limitation, audit review, access expiry, incident response |
| Prompt or document injection | A source document instructs an AI agent to ignore policy | Treat source text as untrusted data, isolate extraction, allow-listed tools, schema validation |
| Availability failure | An official source disappears or changes location | Retained snapshots, source-health status, explicit unavailable-state handling |
| Legal harm | A person is named on insufficient evidence | Proportional language, right of reply, legal review, visible corrections |

## Current prototype boundary

The public repository is suitable only for public and synthetic evaluation. It does not provide production authentication, encrypted restricted storage, secrets management, independent penetration testing or partner-specific privacy/legal approval.

Those are hard blockers for restricted partner or victim-sensitive data, not optional future polish.
