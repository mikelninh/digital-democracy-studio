# Public-source retention and Evidence Vault hand-off

## Scope

The alpha retains and verifies **public sources only**. Confidential or leaked material is prohibited until a qualified partner environment exists.

## Registry record

Every source receives:

- stable source ID;
- case ID;
- publisher and title;
- canonical URL;
- publication date where known;
- access date;
- data zone (`public`);
- expected content type;
- snapshot state;
- SHA-256 hash when original bytes are retained;
- parser or extraction version;
- human reviewer.

## Snapshot states

- `registry_only_snapshot_pending`;
- `original_retained_hash_verified`;
- `moved_or_unavailable`;
- `fetch_error`;
- `material_change_pending_review`.

## Storage rule

Original bytes must be stored content-addressably in the existing SafeTrace Evidence Vault or a reviewed equivalent. Derived text never replaces the original. A changed webpage creates a new receipt; it does not overwrite history.

## Publication gate

A registry-only URL may support an early public-status brief. A sensitive or consequential finding should not be labelled fully vault-backed until original bytes and hashes are retained and independently checked.

## Copyright and minimisation

Retain only what is necessary for verification and lawful audit. Public display should prefer short quotations, source links and derived claim anchors rather than republishing complete protected works.

## Current status

The v0.2 registry is implemented. Original-byte backfill is still pending for the seven new cases and remains visible in `source_registry.json`.
