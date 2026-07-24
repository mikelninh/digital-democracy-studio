# SafeTrace v1.4 — Claim Ledger 2.0

Claim Ledger 2.0 is the authoritative workflow for consequential statements. A claim is no longer a paragraph inside a report: it is a versioned object with exact evidence links, required review gates, decisions, corrections and downstream publication state.

**Boundary:** reviewed public sources and synthetic fixtures only. Existing Case 001–004 claims are migrated, but they are blocked for new publication until their original evidence is backfilled into the Evidence Vault.

## What is enforced

### Versioned claims

Every claim version records:

- exact wording;
- evidence and legal status;
- sensitivity;
- researcher;
- supporting, contradicting and contextual evidence;
- source anchor;
- Evidence Vault receipt and object hash, or an explicit legacy-reference state;
- limitations;
- version ancestry.

### Dynamic review graph

Every material claim requires:

- evidence review;
- red-team review;
- independent publication review.

Additional gates are added when relevant:

- identity review for identity-sensitive claims;
- legal review and right of reply for sensitive claims, allegations, analytical red flags or material discussion of people;
- correction review for replacement versions.

### Separation of duties

Sensitive claim reviewers may not be the researcher. The final publication reviewer for a material claim must be independent from the researcher.

### Contradicting evidence

A claim containing contradicting evidence cannot pass unless the red-team decision explicitly records that the contradiction was addressed.

### Corrections and invalidation

A correction:

1. creates a sequential new claim version;
2. remains visible;
3. records type, reason, approver and time;
4. marks every publication using the superseded version as `stale`;
5. requires a complete new review graph before republication.

### Honest legacy migration

Cases 001–004 are imported into one ledger without pretending their historic URLs are already Evidence Vault receipts. They receive the status:

`migrated_pending_evidence_backfill`

They remain unavailable for new publication until the original source bytes are acquired and verified through v1.3.

## Run

```bash
python -m unittest discover -s safetrace/claim_ledger/tests -v
python -m safetrace.claim_ledger.contracts \
  --write safetrace/claim_ledger/artifacts/claim-ledger-contracts-1.4.json
python -m safetrace.claim_ledger.build_release_artifacts \
  --safetrace-root safetrace \
  --output-root safetrace/claim_ledger/artifacts
```

## Release evidence

The deterministic release fixture demonstrates:

- a synthetic vault-backed claim;
- supporting and contradicting evidence;
- all required review gates;
- independent approval;
- publication of version 1;
- visible correction to version 2;
- automatic invalidation of the old publication;
- a second full review and republication;
- migration of Cases 001–004 with zero automatic publication.

## Next milestone

**v1.5 — Auditable Agent Task Queue and evaluation harness.** Agents will produce structured proposals into the Claim Ledger, never approved claims or autonomous publications.
