from __future__ import annotations

from .model import RegistryEntry, SourceAlert, SourceCheck, VaultReceipt


def assess_check(entry: RegistryEntry, check: SourceCheck, *, previous: VaultReceipt | None = None, current: VaultReceipt | None = None) -> SourceAlert:
    entry.validate()
    check.validate()
    if check.source_id != entry.source_id:
        raise ValueError("Source check does not match registry entry")
    kind = "no_change"
    severity = "info"
    summary = "No material source change detected."
    if check.result == "moved" or (check.resolved_url and check.resolved_url != entry.canonical_url):
        kind, severity, summary = "source_moved", "warning", "The reviewed source resolved to a different canonical location."
    elif check.result == "unavailable":
        kind, severity, summary = "source_unavailable", "high", "The reviewed source was unavailable and requires human follow-up."
    elif check.result == "error":
        kind, severity, summary = "fetch_error", "warning", "The source check failed and no public status may change automatically."
    elif check.content_type and check.content_type not in entry.expected_content_types:
        kind, severity, summary = "content_type_mismatch", "high", "The source returned an unexpected content type."
    elif current and previous and current.material_changed:
        kind, severity, summary = "material_change", "warning", "The normalized source content changed and requires human review."
    alert = SourceAlert(
        alert_id=f"alert:{check.check_id}:{kind}",
        source_id=entry.source_id,
        created_at=check.checked_at,
        kind=kind,
        severity=severity,
        summary=summary,
        check_id=check.check_id,
        receipt_id=current.receipt_id if current else None,
    )
    alert.validate()
    return alert
