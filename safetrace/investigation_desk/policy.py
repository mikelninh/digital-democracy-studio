from __future__ import annotations

from .model import SessionContext
from .vocabularies import ACTIONS, ROLE_PERMISSIONS, ROLE_VIEWS, VIEWS


def require_action(session: SessionContext, action: str) -> None:
    session.validate()
    if action not in ACTIONS:
        raise PermissionError(f"Unknown Desk action: {action}")
    if action not in ROLE_PERMISSIONS[session.role]:
        raise PermissionError(f"Role {session.role} cannot perform {action}")


def require_view(session: SessionContext, view: str) -> None:
    session.validate()
    if view not in VIEWS:
        raise PermissionError(f"Unknown Desk view: {view}")
    if view not in ROLE_VIEWS[session.role]:
        raise PermissionError(f"Role {session.role} cannot view {view}")


def require_zone(session: SessionContext, record_zone: str) -> None:
    session.validate()
    if record_zone == "sensitive_internal" and session.data_zone_ceiling != "sensitive_internal":
        raise PermissionError("Session cannot access sensitive-internal records")
