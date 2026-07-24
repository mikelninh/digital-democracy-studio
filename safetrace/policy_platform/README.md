# SafeTrace Policy Platform v0.1

A fast, truthful foundation for the long-term v4/v5 direction:

- **Open Policy API:** versioned static JSON and OpenAPI 3.1.1
- **MCP:** official Python SDK, read-only stdio server, six tools and two resources
- **Deutschland Dashboard:** sourced indicators with dates, definitions, targets and visible uncertainty

## Deliberate boundaries

- no single Germany score;
- no automatic policy recommendation;
- forecasts remain distinct from observations;
- working policy models remain distinct from official facts;
- no write, publication, contact, referral or restricted-data capability;
- API snapshots are versioned and hashable.

## Validate

```bash
python -m unittest discover -s safetrace/policy_platform/tests -v
python -m safetrace.policy_platform.validate \
  --root safetrace \
  --output safetrace/policy_platform/artifacts/release-report.json
```
