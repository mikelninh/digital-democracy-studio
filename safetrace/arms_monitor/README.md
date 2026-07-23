# SafeTrace v0.6 — Arms & Influence Monitor

The monitor makes German defence procurement and arms-export decisions understandable without turning lawful approvals, contracts, profits or policy disagreement into accusations of corruption.

## Non-negotiable stage distinctions

SafeTrace records these as separate event types:

- Policy or budget authority.
- Parliamentary approval.
- Procurement contract.
- Production activity.
- Export authorisation.
- Delivery.
- Planned delivery.
- Operational use.

An export authorisation does not prove delivery. A contract does not prove operational use. A planned date is not presented as a completed event.

## Current official baseline

- Approximately EUR 13.1 billion in German arms-export authorisations during 2025.
- Approximately EUR 5.6 billion for war weapons and EUR 7.5 billion for other military goods.
- Approximately EUR 2.3 billion authorised for Ukraine, the largest named recipient.
- A MEKO A-200 DEU timeline from initial consideration through construction activity, parliamentary financing approval and planned handover.

The monitor currently contains no confirmed delivery or operational-use record for the events in this baseline.

## First unresolved oversight question

The Bundeswehr states that construction activity for MEKO A-200 DEU began before the final parliamentary financing approval and describes this as unusual because approval is normally a prerequisite.

SafeTrace asks what contractual, pre-contractual or risk-bearing arrangement enabled that sequence. It does not conclude that the sequence was unlawful or corrupt.

## Build and test

```bash
python -m unittest discover -s safetrace/arms_monitor/tests -v
python -m safetrace.arms_monitor.build_monitor
```

## Next increments

- Add procurement contract and amendment records where officially available.
- Connect contractor and ownership data with provenance.
- Add lobbying, donation and revolving-door records through the existing graph and Review Desk.
- Add end-use, diversion, audit, litigation and human-rights evidence fields.
- Seek direct clarification from responsible institutions through formal, reviewable questions.
