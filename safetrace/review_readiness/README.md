# SafeTrace v1.8 — Independent Review Readiness

SafeTrace v1.8 prepares a structured, reproducible dossier for independent review. It does not claim that any external reviewer has approved SafeTrace.

## Seven review disciplines

- Investigative editorial
- Privacy
- Legal
- Security
- Domain expertise
- Accessibility
- Public comprehension

Each review packet contains:

- a bounded scope;
- SHA-256 hashes for the reviewed artifacts;
- discipline-specific questions;
- expected structured findings;
- a required conflict-of-interest declaration;
- a written go/no-go recommendation;
- a public-disclosure recommendation.

Every external review slot begins `unassigned`. A slot cannot become `completed` without a real external reviewer identity.

## Finding register

The release deliberately records unresolved blockers rather than declaring readiness:

- **Critical:** production identity, MFA and session revocation are not configured.
- **High:** Case 004 original source bytes are not retained.
- **High:** no independent security assessment or penetration test is complete.
- **High:** no partner-specific lawful basis, DPIA or retention terms exist.
- **Medium:** accessibility audit, citizen study and observed workflow benchmark remain incomplete.

The partner and restricted-data gates remain closed while critical or high findings are unresolved.

## Exercises

v1.8 creates three synthetic dry-run exercises:

1. Prompt-injection and hostile-source threat modelling.
2. Incorrect entity-link publication incident and correction.
3. Evidence-storage outage and verified recovery.

These exercises expose procedure gaps. They are not independently observed security certifications.

## External study protocols

Two consent-based protocols are prepared:

- qualified workflow benchmark;
- citizen comprehension study.

The protocols minimise collected data, define prohibited fields, metrics and stopping rules. Their status is `ready_for_ethics_privacy_review`; v1.8 cannot approve them itself.

## Case 004 source backfill

All eleven official and analytical source records receive a controlled acquisition plan requiring:

- original bytes;
- SHA-256 receipt;
- retrieval timestamp and content type;
- parser manifest;
- exact claim anchors;
- renewed human review.

Backfill never triggers automatic publication.

## Artifacts

```bash
python -m unittest discover -s safetrace/review_readiness/tests -v
python -m safetrace.review_readiness.contracts --write safetrace/review_readiness/artifacts/review-readiness-contracts-1.8.json
python -m safetrace.review_readiness.build_review_pack --safetrace-root safetrace --output-root safetrace/review_readiness/artifacts
```

Generated outputs:

- review-readiness report;
- seven review packets;
- finding register;
- Case 004 source-backfill plan;
- study protocols;
- human-readable PDF dossier.

## Truthful status

**Ready to invite qualified independent reviewers. Not independently reviewed, externally approved, partner-pilot ready or authorised for restricted data.**

v1.9 may begin only after real reviewers return findings and the appropriate owners remediate them. Code completion alone does not open the pilot gate.
