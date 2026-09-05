from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Literal

FreshnessDecision = Literal["allow", "verify_first", "block"]


@dataclass(frozen=True)
class FreshnessGate:
    module: str
    decision: FreshnessDecision
    data_as_of: str | None
    verified_against: str | None
    reason: str
    safe_fallback: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _parse_year(value: str | None) -> int | None:
    if not value:
        return None
    for token in value.replace("/", "-").split("-"):
        if token.isdigit() and len(token) == 4:
            return int(token)
    return None


def gate_rule_dependent_tool(
    *,
    module: str,
    data_as_of: str | None,
    verified_against: str | None = None,
    today: date | None = None,
    max_age_years: int = 0,
) -> FreshnessGate:
    """Fail closed when a rule-dependent tool cannot prove current parameters.

    `max_age_years=0` means the bundled parameters must be verified for the
    current year. This is intentionally conservative for benefits/law.
    """
    today = today or datetime.utcnow().date()
    data_year = _parse_year(data_as_of)
    verified_year = _parse_year(verified_against)
    if data_year is None:
        return FreshnessGate(
            module=module,
            decision="block",
            data_as_of=data_as_of,
            verified_against=verified_against,
            reason="No machine-readable freshness date is attached to this rule-dependent module.",
            safe_fallback="Use current authoritative sources/manual official calculator instead of the bundled computation."
        )
    effective_year = max(data_year, verified_year or data_year)
    if today.year - effective_year > max_age_years:
        return FreshnessGate(
            module=module,
            decision="verify_first",
            data_as_of=data_as_of,
            verified_against=verified_against,
            reason=f"Bundled parameters are not verified for {today.year}.",
            safe_fallback="Show the tool result only as a stale hypothesis or route the user to the current official calculator/source."
        )
    return FreshnessGate(
        module=module,
        decision="allow",
        data_as_of=data_as_of,
        verified_against=verified_against,
        reason="Rule-dependent parameters are verified within the configured freshness window.",
        safe_fallback="None required."
    )


def master_freshness_status(today: date | None = None) -> dict[str, Any]:
    today = today or datetime.utcnow().date()
    gates = [
        gate_rule_dependent_tool(module="WohngeldMCP", data_as_of="2024-2025", today=today),
        gate_rule_dependent_tool(module="ElterngeldMCP", data_as_of="2024-2025", today=today),
        gate_rule_dependent_tool(module="PublicMoneyMCP", data_as_of="2025", today=today),
    ]
    return {
        "today": today.isoformat(),
        "gates": [gate.to_dict() for gate in gates],
        "all_current": all(gate.decision == "allow" for gate in gates),
        "principle": "Stale structured tools may help generate hypotheses, but they cannot silently override current authoritative sources."
    }
