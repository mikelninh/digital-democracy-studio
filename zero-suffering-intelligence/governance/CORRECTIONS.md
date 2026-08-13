# Zero Suffering Intelligence — Corrections

Updated: 2026-08-13

## Public correction standard

A correction must preserve the audit trail. We do not silently replace a consequential factual claim once it has been published.

Each correction record should contain:

- correction ID;
- affected claim ID(s);
- reported by;
- received date;
- original claim/version;
- corrected or superseding claim;
- reason;
- evidence used;
- reviewer;
- resolution status;
- publication date.

## Statuses

`reported` → `under_review` → `accepted` / `partly_accepted` / `rejected_with_reason` → `published`

A source update detected by Watchtower uses `needs_review`; it is **not** an automatic correction.

## Current correction log

No external correction has yet been received.

### Internal reliability event — WT-2026-08-13-001

During the first automated Watchtower iteration, snapshot serialization added a trailing newline. Hashes were therefore different on the next run even when the normalized page content was effectively unchanged. This created false-positive source-change flags.

Resolution: normalize stored snapshots before hashing and retain review events separately. The error is documented because reliability failures are part of the evidence system.

The same run also surfaced a separate, meaningful update to the current PFG Central Services Lobbyregister entry. That change is being treated as a real review event rather than being discarded with the false positives.
