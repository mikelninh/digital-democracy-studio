# SafeTrace v1.5 — Auditable Agent Task Queue

SafeTrace agents are bounded proposal workers. They do not publish, contact subjects, refer cases, identify people from faces or decide guilt.

## Implemented workers

- **Scout** — finds candidate public sources.
- **Archivist** — proposes reviewed source acquisition and hashing.
- **Reader** — extracts bounded passages with exact anchors.
- **Linker** — proposes uncertain entity links.
- **Chronologist** — proposes dated timeline events.
- **Claim Compiler** — drafts bounded claim proposals.
- **Skeptic** — searches for contradictions and alternative explanations.
- **Quant** — performs transparent calculations on reviewed data.
- **Legal Status** — distinguishes announced, proposed, enacted and final states.
- **Guardian** — checks privacy, harm and publication boundaries.
- **Watchtower** — proposes reviews for material source changes.
- **Explainer** — drafts plain-language text from approved claims only.

## Every task records

- purpose and case;
- agent type;
- exact allowed tools;
- maximum data zone;
- input and output contracts;
- model identifier and prompt version;
- timeout and cost budget;
- human approver;
- traceable input references.

## Every completed run records

- input and output hashes;
- task contract trace key;
- model and prompt version;
- tools actually used;
- cost and latency;
- exact source anchors;
- proposal status.

Every successful agent output starts as `awaiting_human`. A human may accept it **for further review**, reject it or request changes. Acceptance is not publication approval.

## Default-deny rules

The queue blocks:

- unknown or unapproved tools;
- `publish`, `contact_subject`, `refer_authority`, facial identification and hacking tools;
- data-zone escalation;
- budget or timeout overruns;
- self-declared approval, verification or publishability;
- consequential proposals without exact source anchors;
- confirmed entity links without two independent identifiers;
- attribution of inherited measures to the current government;
- final legal status inferred from an announcement;
- known contradictions that the Skeptic fails to surface;
- agents acting as human reviewers.

## Evaluation harness

The release suite includes Golden Cases for:

- extraction;
- entity resolution;
- political attribution;
- contradiction discovery;
- legal status;
- harmful publication suggestions;
- missing provenance;
- unknown tools;
- data-zone escalation;
- safe public explanation.

A quality or safety regression blocks the release.

## Run locally

```bash
python -m unittest discover -s safetrace/agent_queue/tests -v
python -m safetrace.agent_queue.contracts --write safetrace/agent_queue/artifacts/agent-queue-contracts-1.5.json
python -m safetrace.agent_queue.build_release_artifacts --output-root safetrace/agent_queue/artifacts
```

## Truthful boundary

v1.5 is a deterministic, testable execution and evaluation foundation for public-source and synthetic workflows. It does not yet run external model providers in production and does not authorise restricted partner, victim or witness data.
