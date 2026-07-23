# SafeTrace Roadmap — v0.3 to v1.0

The roadmap prioritises trustworthiness before scale. A feature does not count as complete merely because the interface exists; its evidence, security and review process must also work.

## v0.3 — Source Engine

**Goal:** turn Case 001 into a reproducible, auditable investigation rather than a curated page.

### Deliverables

- Connector for the official GRECO Germany evaluation and compliance pages.
- Connector for OECD integrity indicators and country notes.
- Source snapshots with retrieval timestamp, canonical URL, content hash and parser version.
- Change detection showing what changed between official versions.
- Source health dashboard for unavailable, moved or materially changed records.
- Complete 14-recommendation tracker with owner, deadline, status, evidence and unresolved question.
- Exportable source manifest.

### Exit test

A reviewer can reproduce every visible Case 001 status from the retained official snapshots and identify exactly which parser and human decision produced it.

---

## v0.4 — Political Money Graph

**Goal:** make documented influence relationships understandable without implying causation.

### Deliverables

- Bundestag large-donation importer.
- Lobby Register Open Data/API importer.
- Versioned entity resolution for companies, associations, people, parties and public institutions.
- Relationship provenance: every graph edge explains its identifier, source and confidence.
- Timeline view for donations, declared policy interests, meetings, legislative events, contracts and official outcomes.
- Gap view showing missing meeting disclosures, unresolved entity matches and inaccessible records.
- Side-by-side source inspection.

### Exit test

A citizen can inspect a donation, understand the officially documented surrounding relationships and clearly see that no causal conclusion has been established.

---

## v0.5 — Review Desk

**Goal:** keep humans responsible for conclusions and publication.

### Deliverables

- Claim-by-claim editorial review queue.
- Supporting and contradicting evidence attached to the same claim.
- Separate fields for fact, official allegation, analytical inference and unresolved gap.
- Reviewer identity, decision, rationale and timestamp.
- Correction history and public changelog.
- Right-of-reply workflow for organisations or people materially discussed.
- Legal-review gate for sensitive publication.

### Exit test

No sensitive claim can reach the public monitor without a recorded human decision, source trail and correction path.

---

## v0.6 — Arms & Influence Monitor

**Goal:** trace formal decisions, economic beneficiaries, oversight and human consequences using neutral standards.

### Deliverables

- Import German arms-export reports and parliamentary records.
- Import major procurement and budget records.
- Contractor, subcontractor and beneficial-ownership mapping where lawfully available.
- Lobbying, donation and revolving-door connections sourced from official registers.
- Clear distinction between authorisation, contract, delivery and operational use.
- End-use control, diversion, audit, litigation and human-rights source fields.
- Citizen page answering: what was decided, who had authority, who benefited, what risks were assessed and what remains unknown.

### Exit test

A reviewer can follow one major decision from formal authority to documented oversight without SafeTrace describing lawful profit, advocacy or temporal proximity as corruption.

---

## v0.7 — Monitoring and Alerts

**Goal:** let AI reduce information overload while humans decide significance.

### Deliverables

- Scheduled official-source checks.
- Deduplication and material-change detection.
- Suggested case updates with source quotations and confidence.
- Human approval before public status changes.
- Alerts for missed deadlines, new judgments, new disclosures and corrected records.
- Public “last checked / last changed / last reviewed” fields.

### Exit test

The system catches a real official update, proposes the correct affected claims and publishes nothing until a reviewer approves it.

---

## v0.8 — Investigator Case Packs

**Goal:** make SafeTrace outputs useful beyond the public dashboard.

### Deliverables

- Human-readable PDF case summary.
- Machine-readable JSON conforming to a published schema.
- Evidence inventory and source manifest.
- Chronology, entity graph and financial/decision trail.
- Confidence, legal-status and review labels.
- Redacted public edition and restricted partner edition.
- Explicit statement of limitations and unresolved questions.

### Exit test

A qualified investigator can understand the evidence package without reverse-engineering the dashboard, while every conclusion remains traceable to a source and reviewer.

---

## v0.9 — Security and Governance Readiness

**Goal:** prepare for a controlled real-world partnership without accepting uncontrolled sensitive submissions.

### Deliverables

- Authentication and role-based access control.
- Encryption in transit and at rest.
- Data minimisation, retention and deletion policies.
- Consent and lawful-basis records.
- Threat model and incident-response plan.
- Audit logs and access review.
- Defamation, privacy, evidence-handling and journalistic/legal review.
- Independent security assessment.
- Governance charter and conflict-of-interest policy.

### Exit test

Independent reviewers agree that the defined pilot data, users and workflows can be handled within the documented risk controls.

---

## v1.0 — Controlled Partner Pilot

**Goal:** prove that SafeTrace improves real accountability work for one qualified organisation.

### Candidate partners

- Investigative journalism or data teams.
- Anti-corruption or transparency organisations.
- Fraud prevention and victim-support teams.
- Public-sector digital investigation or forensic units.
- Academic public-interest technology labs.

### Deliverables

- One formally scoped partner and case type.
- Signed roles, data boundaries and escalation routes.
- Trained reviewers and documented operating procedure.
- Measured time saved, evidence completeness and reviewer accuracy.
- False-connection and correction metrics.
- Pilot retrospective with public lessons where safe.
- Go/no-go decision for broader deployment.

### v1.0 success measures

- Every published material claim has a primary source or explicitly justified secondary source.
- 100% of sensitive publications have human review.
- No automated guilt classifications.
- Corrections are visible and measurable.
- The pilot partner reports a meaningful improvement in investigation or review workflow.
- No serious privacy or security incident.

## What is deliberately out of scope before v1.0

- Open public uploads of sensitive victim evidence.
- Automated naming of alleged criminals.
- Facial-recognition identification.
- Covert investigation or contact with subjects.
- Predictive “corruption scores” for people.
- Publishing private addresses or unnecessary personal data.
- Fully automated referrals to police, prosecutors or media.