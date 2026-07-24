# SafeTrace Role Simulator

The Role Simulator is a browser-local companion to SafeTrace v1.8. It lets one person test the investigation workflow from several perspectives without creating users, processing restricted data or changing any real SafeTrace record.

## Roles

- Citizen
- Investigator
- Evidence Manager
- Skeptical Reviewer
- Legal & Harm Reviewer
- Publisher

Each role receives a different set of views, actions, tasks and decision prompts.

## Cases

- **Case 001:** GRECO anti-corruption recommendations and implementation status.
- **Case 002:** synthetic political-money graph that separates documented relationships from unsupported causal claims.
- **Case 003:** synthetic arms-decision workflow separating budget, procurement, export approval, delivery, end use and alleged use.
- **Case 004:** the German Law Fairness reference case, including its honest publication blocker: 0 of 11 original source files have been backfilled into the v1.7 Evidence Vault workflow.

## What can be tested

- role and case switching;
- role-filtered navigation;
- source inspection and simulated acquisition receipts;
- claim evidence, contradictions and limitations;
- graph and timeline interpretation;
- bounded agent runs that remain `awaiting_human`;
- independent review and legal/harm decisions with rationale;
- successful training-only publication gates;
- fail-closed Case 004 publication;
- local audit history;
- comprehension questions;
- reset and replay from another role.

## Storage and privacy

All interactions are stored in the browser through `localStorage`. The simulator:

- makes no network requests;
- creates no account;
- sends no data to SafeTrace or GitHub;
- changes no repository record;
- publishes nothing;
- accepts no victim, witness or restricted partner data.

The acquisition receipts, agent receipts, decisions and publication results are explicitly simulated.

## Run

Open `index.html` through the SafeTrace GitHub Pages site or any simple static server.

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/safetrace/role_simulator/
```

## Validate

```bash
python -m unittest discover -s safetrace/role_simulator/tests -v
```

The release tests verify six roles, four cases, safe role capabilities, complete scenario structure, both successful and blocked training publication paths, explicit causal/stage boundaries, accessibility markers and the absence of network requests.

## Truthful boundary

This simulator demonstrates the intended user experience and authorisation logic. It is **not** production authentication, an operational investigation database, an external-model service, a completed independent review or permission to process restricted data.
