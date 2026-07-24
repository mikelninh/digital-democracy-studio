"""SafeTrace v1.6 internal Investigation Desk foundation."""

from .desk import InvestigationDesk
from .views import build_view, workspace_manifest

__all__ = ["InvestigationDesk", "build_view", "workspace_manifest"]
