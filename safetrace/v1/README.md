# SafeTrace v1.0 — Pilot-Ready Release

The v1 release integrates the complete prototype stack:

1. source snapshots and change detection;
2. political-money relationship graph;
3. human review desk;
4. arms and influence monitor;
5. monitored change proposals;
6. investigator PDF/JSON case packs;
7. governance, RBAC and tamper-evident audit records;
8. measurable controlled-pilot gates.

## Exact status

**SafeTrace v1.0 is ready for public and synthetic evaluation. It is not authorised for real victim data or a restricted partner deployment.**

Run the integrated release check:

```bash
python -m safetrace.v1.cli --root . --output safetrace/v1/status.json
```

The command succeeds only when all modules exist, synthetic governance gates pass, the synthetic benchmark passes, and the live-partner gate correctly remains closed.

## Why this is v1.0

The end-to-end public workflow now exists: sources can be retained and compared, structured records can be connected, claims can be reviewed, monitoring can propose changes, case packs can be exported, and readiness can be measured. The next milestone is external validation, not another internal feature number.
