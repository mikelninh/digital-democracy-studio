from __future__ import annotations

from typing import Any

from .desk import InvestigationDesk
from .model import SessionContext, ViewSnapshot, plain
from .policy import require_view, require_zone


def _visible_records(desk: InvestigationDesk, session: SessionContext, kind: str | None = None):
    records = []
    for record in desk.records.values():
        if kind and record.kind != kind:
            continue
        try:
            require_zone(session, record.data_zone)
        except PermissionError:
            continue
        records.append(record)
    return records


def build_view(
    desk: InvestigationDesk,
    session: SessionContext,
    view: str,
    generated_at: str,
) -> ViewSnapshot:
    require_view(session, view)
    items: list[dict[str, Any]] = []
    blockers: list[str] = []

    if view == "inbox":
        items = [
            {
                "type": "case",
                "id": case.id,
                "title": case.title,
                "status": case.status,
                "question": case.question,
            }
            for case in desk.cases.values()
            if case.status in {"draft", "triage"}
        ]
        items += [
            {
                "type": "agent_proposal",
                "id": record.id,
                "case_id": record.case_id,
                "title": record.title,
                "status": record.status,
            }
            for record in _visible_records(desk, session, "agent_proposal")
            if record.status == "awaiting_human"
        ]
    elif view == "cases":
        items = [plain(case) for case in desk.cases.values()]
    elif view == "sources":
        items = [plain(record) for record in _visible_records(desk, session, "source")]
    elif view == "claims":
        items = [plain(record) for record in _visible_records(desk, session, "claim")]
    elif view == "graph":
        items = [
            plain(record)
            for record in _visible_records(desk, session)
            if record.kind in {"entity", "relationship"}
        ]
    elif view == "timeline":
        items = [plain(record) for record in _visible_records(desk, session, "event")]
        items.sort(key=lambda item: str(item.get("payload", {}).get("date", "")))
    elif view == "review":
        items = [
            plain(record)
            for record in _visible_records(desk, session)
            if record.review_state in {"pending", "needs_changes"}
        ]
        if not items:
            blockers.append("No records currently require review")
    elif view == "publish":
        items = [plain(request) for request in desk.publications.values()]
        for request in desk.publications.values():
            if request.status == "requested":
                blockers.append(f"Publication awaiting approval: {request.id}")
            if request.status == "stale":
                blockers.append(f"Publication is stale: {request.id}")
    elif view == "corrections":
        items = [
            plain(request)
            for request in desk.publications.values()
            if request.status in {"stale", "withdrawn"} or request.stale_reason
        ]
    elif view == "agents":
        items = [plain(record) for record in _visible_records(desk, session, "agent_proposal")]
    elif view == "audit":
        items = [plain(event) for event in desk.audit]
        verification = desk.verify_audit_chain()
        if verification["status"] != "pass":
            blockers.extend(verification["errors"])
    else:
        raise ValueError(f"Unsupported view: {view}")

    return ViewSnapshot(
        view,
        session.subject_id,
        generated_at,
        tuple(items),
        tuple(blockers),
    )


def workspace_manifest(
    desk: InvestigationDesk,
    session: SessionContext,
    generated_at: str,
) -> dict[str, Any]:
    from .vocabularies import ROLE_VIEWS

    snapshots = {
        view: plain(build_view(desk, session, view, generated_at))
        for view in sorted(ROLE_VIEWS[session.role])
    }
    return {
        "schema_version": "safetrace.desk-workspace/1.6",
        "subject_id": session.subject_id,
        "role": session.role,
        "identity_provider": session.identity_provider,
        "generated_at": generated_at,
        "views": snapshots,
        "authoritative_system": "SafeTrace Investigation Desk",
        "chat_is_authoritative": False,
        "spreadsheet_is_authoritative": False,
        "public_portal_is_logically_separate": True,
    }
