# SafeTrace v0.3 Source Engine

This package makes Case 001 reproducible instead of relying only on a manually curated page.

## What it does

- Maintains a reviewed registry of primary official sources.
- Downloads exact source bytes when run in a networked environment.
- Stores immutable raw snapshots and JSON receipts.
- Records canonical URL, retrieval timestamp, content type, size, SHA-256, normalised hash and parser version.
- Detects changes against the previous snapshot.
- Builds a public Case 001 JSON feed only when an explicit human-review state is present.
- Validates the official GRECO total: four implemented, six partly implemented and four not implemented.

## Run locally

```bash
python -m unittest discover -s safetrace/source_engine/tests -v
python -m safetrace.source_engine.build_public_status
python -m safetrace.source_engine.cli --output artifacts/source-snapshots
```

The snapshot command requires internet access. Raw downloaded source material is written to `artifacts/`, which is intentionally not committed. GitHub Actions retains it as a workflow artifact instead.

## Public boundary

The source engine records institutional compliance statuses. It does not infer bribery, corruption, unlawful influence or individual guilt.
