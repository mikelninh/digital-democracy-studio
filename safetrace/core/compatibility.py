"""Conservative JSON-schema compatibility checks for SafeTrace core releases."""

from __future__ import annotations

from typing import Any


def compatibility_issues(previous: dict[str, Any], current: dict[str, Any]) -> list[str]:
    """Report changes that would reject documents valid under the previous schema.

    This intentionally checks only the subset SafeTrace controls: object properties,
    required fields, enum values, item schemas and primitive type changes.
    """

    issues: list[str] = []

    def walk(old: Any, new: Any, path: str) -> None:
        if not isinstance(old, dict) or not isinstance(new, dict):
            return

        old_type = old.get("type")
        new_type = new.get("type")
        if old_type and new_type and old_type != new_type:
            issues.append(f"{path}: type changed from {old_type!r} to {new_type!r}")

        old_enum = set(old.get("enum", []))
        new_enum = set(new.get("enum", []))
        if old_enum and new_enum and not old_enum.issubset(new_enum):
            removed = sorted(old_enum - new_enum)
            issues.append(f"{path}: enum values removed: {removed}")

        old_required = set(old.get("required", []))
        new_required = set(new.get("required", []))
        added_required = sorted(new_required - old_required)
        if added_required:
            issues.append(f"{path}: new required fields: {added_required}")

        old_properties = old.get("properties", {})
        new_properties = new.get("properties", {})
        if isinstance(old_properties, dict) and isinstance(new_properties, dict):
            removed_properties = sorted(set(old_properties) - set(new_properties))
            if removed_properties:
                issues.append(f"{path}: properties removed: {removed_properties}")
            for name in sorted(set(old_properties) & set(new_properties)):
                walk(old_properties[name], new_properties[name], f"{path}.{name}")

        if "items" in old and "items" in new:
            walk(old["items"], new["items"], f"{path}[]")

        old_defs = old.get("$defs", {})
        new_defs = new.get("$defs", {})
        if isinstance(old_defs, dict) and isinstance(new_defs, dict):
            removed_defs = sorted(set(old_defs) - set(new_defs))
            if removed_defs:
                issues.append(f"{path}: definitions removed: {removed_defs}")
            for name in sorted(set(old_defs) & set(new_defs)):
                walk(old_defs[name], new_defs[name], f"{path}.$defs.{name}")

    walk(previous, current, "$")
    return issues


def assert_backward_compatible(previous: dict[str, Any], current: dict[str, Any]) -> None:
    issues = compatibility_issues(previous, current)
    if issues:
        raise ValueError("Backward-incompatible SafeTrace schema change:\n- " + "\n- ".join(issues))
