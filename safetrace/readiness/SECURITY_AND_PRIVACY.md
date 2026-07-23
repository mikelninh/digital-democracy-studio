# SafeTrace Security and Privacy Baseline

## Status

This is a design baseline, not an independent security certification or legal opinion.

Sensitive evidence intake remains disabled.

## Principles

SafeTrace uses the following operating principles for any future controlled pilot:

1. **Purpose limitation and data minimisation** — collect only the information required for the agreed case workflow.
2. **Storage limitation** — define deletion, archival and legal-hold rules before collection begins.
3. **Privacy by design and by default** — public editions are redacted; restricted information is not public merely because it exists in an official or submitted record.
4. **Risk-appropriate security** — access, encryption, recovery and monitoring controls reflect the potential harm to victims, witnesses, investigation subjects and partners.
5. **Human responsibility** — AI may extract and propose; humans authorise sensitive publication, referral and identity resolution.
6. **No uncontrolled model exposure** — sensitive evidence must not be sent to an external model provider unless the partner-approved processing terms, data flow and safeguards explicitly allow it.

These principles align with GDPR requirements including data minimisation, storage limitation, integrity and confidentiality, data protection by design and risk-appropriate security. The exact legal basis and controller/processor roles must be determined with a qualified partner and data-protection reviewer.

## Proposed pilot architecture

### Public zone

- Public dashboards and redacted case packs.
- Official public sources only.
- No authentication required for public content.
- No secret or personal data.

### Restricted investigation zone

- Strong authentication with phishing-resistant multi-factor authentication.
- Role-based access and least privilege.
- Separate roles for intake, investigator, reviewer, legal reviewer, security administrator and auditor.
- Encryption in transit and at rest using managed keys.
- Per-case access grants and periodic access review.
- Tamper-evident audit events for upload, read, export, review, redaction, deletion and referral.
- No public internet indexing.

### Processing zone

- Malware scanning and file-type validation before evidence enters the case workspace.
- Immutable original object plus separately versioned working copies.
- Hashes recorded before extraction or transformation.
- AI processing against redacted or minimised content where possible.
- Model, prompt, parser and tool versions attached to generated outputs.
- No autonomous publication or authority referral.

## Primary threat actors

- External attackers seeking victim, witness or investigation data.
- Investigation subjects seeking deletion, alteration or early warning.
- Insiders exceeding legitimate access.
- Abusive submitters attempting to frame or harass others.
- Automated scraping and denial-of-service actors.
- Supply-chain compromise in dependencies, hosting, model providers or data connectors.

## High-impact threats

| Threat | Harm | Required mitigations before pilot |
|---|---|---|
| Account takeover | Exposure or destruction of sensitive evidence | Phishing-resistant MFA, session controls, alerts, recovery process |
| Evidence tampering | False findings or unusable evidence | Immutable originals, hashes, audit logs, restricted write paths |
| False identity linkage | Harm to uninvolved people | Exact identifiers, human entity review, ambiguity states, correction path |
| Prompt or document injection | AI follows hostile evidence instructions | Content isolation, tool allowlists, untrusted-content labelling, output review |
| Malicious upload | Malware or parser compromise | Sandboxed processing, file limits, scanning, patched parsers |
| Insider misuse | Unauthorised browsing or disclosure | Least privilege, per-case access, audit review, separation of duties |
| Provider data leakage | Sensitive data retained or reused externally | Approved processing terms, minimisation, provider controls, local processing where needed |
| Public overstatement | Defamation, unfairness or damaged investigation | Review Desk, legal gate, right of reply, evidence-state labels |
| Loss or outage | Victims and investigators lose access or evidence | Encrypted backups, recovery objectives, tested restoration |

## Required external assurance

The project maintainer cannot independently certify:

- The deployed system's penetration resistance.
- GDPR compliance for an undefined partner workflow.
- Whether a data-protection impact assessment is legally required or sufficient.
- Defamation, journalistic privilege, evidentiary admissibility or reporting duties.

Those determinations require qualified independent reviewers and the actual pilot partner, purposes, data and deployment.

## Official reference points

- EU General Data Protection Regulation, particularly Articles 5, 25, 32 and 35.
- BfDI guidance and question frameworks for privacy-conscious AI use.
- BSI IT-Grundschutz and federal logging/detection guidance.

The repository references these standards as design inputs, not as a claim of certification.
