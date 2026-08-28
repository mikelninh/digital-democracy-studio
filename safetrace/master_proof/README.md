# CivicOS Master Proof

**Evidence-to-action infrastructure for consequential public questions.**

CivicOS connects messy inputs to entities, relationships, rules, evidence, uncertainty, safe next actions and replayable audit trails. The master proof is intentionally modular: existing projects remain independently testable and connect through explicit contracts rather than being collapsed into one monolith.

## Product contract

```text
question / event / document
        ↓
entity + relationship resolution
        ↓
rule / service / responsibility retrieval
        ↓
claim ledger + evidence receipts
        ↓
contradiction + uncertainty checks
        ↓
proposed next action
        ↓
policy gate + human approval
        ↓
audit + regression case
```

**AI may interpret and propose. Authority remains outside the model.**

## Existing projects as modules

- **SafeTrace** → evidence provenance, investigations, claims, public-interest guardrails
- **SafeTrace Entity Resolution** → explainable identity matching and ambiguity review
- **GitLaw** → German-law retrieval, paragraph graph, citation verification, MCP
- **SafeVoice** → structured sensitive evidence intake and case packaging
- **Public Money MCP** → budget and audit tools
- **Citizen Agents** → monitored public-source changes with logs and human review
- **Digital Worker Factory / CasePilot** → tool contracts, policy gates, approval, replay and evaluation
- **PrüfPilot** → evidence-first document extraction and review
- **City Knowledge Graph** → municipal services, responsibilities and governing rules

## Universal ontology

Every first-class object has provenance, temporal validity and review state. Relationships are evidence-backed objects too; a relationship is never treated as true merely because a model emitted it.

Core entities: `Person`, `Organisation`, `Authority`, `Department`, `Service`, `Law`, `Provision`, `Case`, `Claim`, `Evidence`, `Decision`, `Contract`, `Payment`, `Project`, `Action`.

Core relations: `SAME_AS`, `RELATED_TO`, `PART_OF`, `DIRECTOR_OF`, `RESPONSIBLE_FOR`, `GOVERNED_BY`, `SUPPORTED_BY`, `CONTRADICTS`, `FUNDED_BY`, `PAID_TO`, `CONTRACTED_TO`, `REQUIRES`, `DECIDED_BY`, `AFFECTS`.

## Golden cases

The first suite contains 12 synthetic, high-value citizen and accountability workflows. They are not claims about real people or organisations and are not presented as a statistically representative ranking of German public-service demand.

Each case defines:

- the user question
- expected actors/entities
- expected evidence and rules
- uncertainty or contradiction that must stay visible
- the safest useful next action
- actions the system is forbidden to take autonomously
- which existing project/module should provide each capability

Run the deterministic contract checks with:

```bash
python safetrace/master_proof/test_master_proof.py
```

## What completion means

The master proof is complete when the same interface can demonstrate citizen, investigator and government-operator cases while preserving the same evidence contract:

> identify the actors → retrieve the rules → connect the evidence → expose uncertainty → propose a next action → show exactly why.

Real production use still requires live-source connectors, privacy/security review, domain-expert validation and real-user evaluation. Synthetic gold cases prove architecture and regression discipline, not legal correctness or entitlement eligibility in an individual real case.
