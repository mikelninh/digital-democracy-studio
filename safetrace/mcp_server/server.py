from __future__ import annotations
import json
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).resolve().parents[1] / "open_policy_api" / "v1" / "catalog.json"

def _catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

def _list_systems(domain: str | None = None) -> list[dict[str, Any]]:
    items = _catalog()["systems"]
    return [item for item in items if domain is None or item["domain"] == domain]

def _get_system(system_id: str) -> dict[str, Any]:
    for item in _list_systems():
        if item["system_id"] == system_id:
            return item
    raise KeyError(f"Unknown policy system: {system_id}")

def _list_indicators(domain: str | None = None) -> list[dict[str, Any]]:
    items = _catalog()["indicators"]
    return [item for item in items if domain is None or item["domain"] == domain]

def _get_indicator(indicator_id: str) -> dict[str, Any]:
    for item in _list_indicators():
        if item["indicator_id"] == indicator_id:
            return item
    raise KeyError(f"Unknown indicator: {indicator_id}")

def _search(query: str) -> list[dict[str, Any]]:
    needle=query.strip().casefold()
    if len(needle)<2: raise ValueError("query must contain at least two characters")
    out=[]
    for kind,key,id_key in [("system","systems","system_id"),("source","sources","source_id"),("indicator","indicators","indicator_id")]:
        for item in _catalog()[key]:
            if needle in json.dumps(item,ensure_ascii=False).casefold():
                out.append({"type":kind,"id":item[id_key],"title":item.get("title",item[id_key])})
    return out

def _compare(system_ids: list[str]) -> dict[str, Any]:
    if not 2 <= len(system_ids) <= 5: raise ValueError("compare between two and five systems")
    systems=[_get_system(item) for item in system_ids]
    return {"systems":[{"system_id":s["system_id"],"title":s["title"],"status":s["status"],"beneficiaries":s["beneficiaries"],"payers":s["payers"],"risks":s["risks"],"metric":s["outcome_contract"]["metric"]} for s in systems],"warning":"This is a structured comparison, not a single score or policy recommendation."}

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # Allows offline validation of the pure query layer.
    FastMCP = None

mcp = FastMCP("SafeTrace Open Policy") if FastMCP else None

if mcp:
    @mcp.tool()
    def list_policy_systems(domain: str | None = None) -> str:
        """List read-only policy systems, optionally filtered by domain."""
        return json.dumps(_list_systems(domain), ensure_ascii=False, indent=2)

    @mcp.tool()
    def get_policy_system(system_id: str) -> str:
        """Get truth, incentive, distribution, risk and outcome fields for one system."""
        return json.dumps(_get_system(system_id), ensure_ascii=False, indent=2)

    @mcp.tool()
    def list_germany_indicators(domain: str | None = None) -> str:
        """List sourced Germany dashboard indicators without a composite national score."""
        return json.dumps(_list_indicators(domain), ensure_ascii=False, indent=2)

    @mcp.tool()
    def get_germany_indicator(indicator_id: str) -> str:
        """Get one indicator including date, source and evidence status."""
        return json.dumps(_get_indicator(indicator_id), ensure_ascii=False, indent=2)

    @mcp.tool()
    def search_policy_evidence(query: str) -> str:
        """Search systems, sources and indicators. This does not infer guilt or publish claims."""
        return json.dumps(_search(query), ensure_ascii=False, indent=2)

    @mcp.tool()
    def compare_policy_systems(system_ids: list[str]) -> str:
        """Compare two to five systems without collapsing trade-offs into a single score."""
        return json.dumps(_compare(system_ids), ensure_ascii=False, indent=2)

    @mcp.resource("policy://catalog")
    def policy_catalog() -> str:
        """Read the complete versioned policy-system catalog."""
        return json.dumps(_list_systems(), ensure_ascii=False, indent=2)

    @mcp.resource("policy://germany/indicators")
    def germany_indicators() -> str:
        """Read all current Germany dashboard indicators."""
        return json.dumps(_list_indicators(), ensure_ascii=False, indent=2)

def main() -> None:
    if mcp is None:
        raise SystemExit('Install the official MCP Python SDK: pip install "mcp[cli]"')
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
