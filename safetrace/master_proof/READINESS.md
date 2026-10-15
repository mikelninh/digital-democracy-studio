# CivicOS Master Proof — Readiness

> **North star:** Given what is known right now, what is the most useful thing I can do next — and why?

CivicOS is currently a **source-backed, regression-tested master proof**, not a production public service.

## What is proven now

| Layer | Proof state | Evidence |
|---|---|---|
| Golden experiences | ✅ 12 source-backed workflows | `golden_cases.json`, `golden_experiences.json`, CI |
| Official-source backing | ✅ dated snapshots for every golden case | `source_registry.json`, `source_snapshots.json` |
| Safe source acquisition | ✅ allowlisted connector + SHA-256 receipt contract | `connectors.py` |
| Cross-repo composition | ✅ every required capability must have a named provider | `module_contracts.json`, `composition.py` |
| Claims + provenance | ✅ evidence receipts and missing-evidence visibility | `claim_ledger.py` |
| Contradictions | ✅ overlapping incompatible claims escalate | `claim_ledger.py`, CI |
| Entity resolution | ✅ synthetic benchmark, 0 false-positive auto-merges | `../entity_resolution/` |
| Privacy default | ✅ hash-and-discard proof contract; personal export gated | `evidence_vault.py` |
| Freshness | ✅ stale rule-dependent tools fail into verification | `freshness_gate.py` |
| Change impact | ✅ rule → service → candidate-case proof graph; no auto outcome changes | `dependency_graph.json`, `change_impact.py` |
| Human authority | ✅ consequential action stays behind approval boundaries | ontology/runtime tests |
| Product experience | ✅ all 12 cases selectable with Why?, sources, gaps and must-not rules | `demo.html` |

## What is deliberately **not** claimed

- not a legal-advice service;
- not an official entitlement calculator;
- not a fraud/corruption finding engine;
- not a complete German public-finance database;
- not a complete municipal ontology;
- not a production evidence vault;
- not an autonomous government decision-maker;
- not validated yet on representative real-user outcomes.

## Remaining production gaps, ranked

### P0 — evidence freshness + secure case data

1. **Execute current official-source fetches in each real run** and retain the fetched original plus immutable receipt.
2. **Encrypted evidence storage with identity/access controls, deletion/retention jobs and redaction UX.** The current proof intentionally hashes and discards raw personal bytes by default.
3. **Domain/security review** for legal, benefits, harassment, procurement and public-sector operator workflows.

### P1 — vertical data depth

4. **Benefits:** verify/update rule parameters against current official sources before numeric entitlement output; compose Wohngeld/KiZ/other benefits without double counting.
5. **Company/register investigations:** authorised, terms-compliant retrieval for records that require authentication/access justification; persist temporal identifiers.
6. **Public money/procurement:** recipient-level payment/award ingestion, canonical identifiers and cross-source normalisation.
7. **Policy change:** expand rule-to-service dependency coverage and parse promulgation/effective dates automatically.

### P2 — real-world proof

8. Recruit qualified reviewers and real users for anonymised cases.
9. Turn every reviewer correction into a regression fixture.
10. Measure outcomes: time-to-next-action, evidence completeness, correction rate, false-positive rate, successful routing and user comprehension.

## Existing projects as independently tested modules

CivicOS does not copy all repositories into one codebase. It composes capabilities:

- **GitLaw** — legal retrieval, paragraph graph and citation verification
- **PrüfPilot** — typed document intake and evidence completeness
- **SafeVoice** — digital-evidence intake/hashing/case packaging
- **Public Money MCP** — deterministic federal-budget tools
- **Citizen Agents** — monitored public-source changes
- **Wohngeld MCP / Elterngeld MCP** — domain calculators behind freshness gates
- **Judge MCP** — composable evaluation
- **Digital Worker Factory / CasePilot** — tool/evidence/policy/approval runtime
- **OpenAction** — shared constraints, ownership, approval receipts and next-action coordination
- **SafeTrace Entity Resolution** — identity vs relationship resolution
- **Civic MCP Toolkit** — tracing/logging/error envelopes for MCP tools

The contract is:

```text
question / event
    ↓
source + case intake
    ↓
entities + relationships
    ↓
rules + responsibility
    ↓
claims + evidence + contradictions
    ↓
current constraint
    ↓
most useful next action + Why?
    ↓
policy / freshness / privacy gates
    ↓
human approval where consequential
    ↓
audit + evaluation + replay
```

**One product experience. Many independently testable capabilities.**
