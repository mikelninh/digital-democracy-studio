# SafeTrace v1.3 — Source Registry and Evidence Vault

SafeTrace v1.3 provides a trustworthy system of record for reviewed public sources and their transformations. It stores original bytes by SHA-256, issues append-only receipts, detects material changes, records every transformation and verifies that backups restore exactly.

**Boundary:** v1.3 handles reviewed public sources and synthetic fixtures only. It does not authorise real victim, witness or restricted partner evidence.

## What works

### Reviewed Source Registry

Every source records:

- stable source id;
- publisher, jurisdiction and source hierarchy;
- canonical HTTPS URL;
- update cadence;
- connector and parser versions;
- expected content types;
- retention policy;
- named reviewer and review time;
- public data-zone boundary.

Draft, unreviewed or non-public acquisition entries are rejected.

### Content-addressed Evidence Vault

Original bytes are stored under their SHA-256 hash. Existing objects cannot be overwritten with different content. Every acquisition produces a receipt containing:

- raw and normalized hashes;
- byte length and content type;
- registry revision;
- connector and parser versions;
- previous receipt id and hash;
- raw-change and material-change states.

Receipts form a tamper-evident chain per source.

### Transformation manifests

Parsing, normalization, extraction, redaction and export create explicit manifests with input receipts, input hashes, output hashes, tool versions and parameters. Redaction and export require a named human approver.

### Health and monitoring

The source-health layer distinguishes:

- no material change;
- material change;
- moved source;
- unavailable source;
- fetch error;
- unexpected content type.

Alerts have no public effect until human review.

### Retention, deletion and recovery

- Original evidence cannot be deleted through the v1.3 derived-object workflow.
- Derived deletion requires a reason, named approver and visible tombstone.
- Retention planning never auto-deletes originals.
- Backups list every file, hash and byte length.
- Restore verifies the manifest and every entry before copying.
- Vault integrity checks receipts, chains, objects, manifests and tombstones.

## Run

```bash
python -m unittest discover -s safetrace/evidence_vault/tests -v
python -m safetrace.evidence_vault.contracts \
  --check safetrace/evidence_vault/schemas/evidence-vault-contracts-1.3.json
python -m safetrace.evidence_vault.build_release_artifacts \
  --safetrace-root safetrace \
  --output-root safetrace/evidence_vault/artifacts
```

Bootstrap the reviewed registry separately:

```bash
python -m safetrace.evidence_vault.cli bootstrap \
  --safetrace-root safetrace \
  --registry-root artifacts/evidence-vault/registry \
  --report artifacts/evidence-vault/bootstrap-report.json
```

Verify a vault:

```bash
python -m safetrace.evidence_vault.cli verify \
  --registry artifacts/evidence-vault/registry/current.json \
  --vault artifacts/evidence-vault/vault \
  --output artifacts/evidence-vault/integrity-report.json
```

## Release evidence

The CI release fixture:

1. bootstraps the central registry from the existing Case 001–004 source records;
2. stores two versions of an explicitly synthetic source;
3. confirms the receipt chain and material-change alert;
4. records a parsed derived object through a transformation manifest;
5. verifies vault integrity;
6. creates and restores a full backup;
7. verifies the restored vault independently.

## Next milestone

**v1.4 — Claim Ledger 2.0:** one review and correction workflow across all cases, using the Source Registry and Evidence Vault as the only authoritative source layer.
