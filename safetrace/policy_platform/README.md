# SafeTrace Policy Platform v0.2

The platform now has two distinct cycles:

1. **Published, versioned public snapshot**
   - Open Policy API
   - read-only MCP
   - Deutschland Dashboard
   - snapshot history
2. **Unpublished official-source review candidate**
   - weekly acquisition of ten known official pages
   - retained original bytes and SHA-256 receipts
   - reviewed-marker change detection
   - GitHub Actions evidence artifact
   - named human review issue when a material change is detected

## What this enables

A citizen or external reviewer can now inspect each indicator against its official source, record an approval or challenge, export a browser-local review receipt, and submit a concrete public evidence challenge.

## Boundaries

- The monitor checks known URLs; it does not yet guarantee discovery of every newer official release.
- A changed source or missing marker never updates the public catalog automatically.
- No review decision alone proves a policy outcome.
- No composite Germany score is created.

## Validate locally

```bash
python -m unittest discover -s safetrace/policy_platform/tests -v
python -m safetrace.policy_platform.validate \
  --root safetrace \
  --output safetrace/policy_platform/artifacts/release-report.json
```

## Run the official-source monitor

```bash
python -m safetrace.policy_platform.refresh \
  --root safetrace \
  --output safetrace/policy_platform/artifacts/source-monitor
```
