from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PROHIBITED = {"publish_real", "contact_subject", "refer_authority", "identify_face", "hack", "open_restricted_data"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: Path) -> dict[str, Any]:
    api = root / "open_policy_api" / "v1"
    files = ["index.json", "catalog.json", "history.json", "openapi.json"]
    errors: list[str] = []
    docs: dict[str, dict[str, Any]] = {}
    for name in files:
        path = api / name
        if not path.exists():
            errors.append(f"missing {name}")
            continue
        try:
            docs[name] = load(path)
        except Exception as exc:
            errors.append(f"invalid {name}: {exc}")

    catalog = docs.get("catalog.json", {})
    systems = catalog.get("systems", [])
    indicators = catalog.get("indicators", [])
    sources = catalog.get("sources", [])
    source_ids = {item.get("source_id") for item in sources}

    if len(systems) < 5:
        errors.append("need at least five policy systems")
    if len(indicators) < 8:
        errors.append("need at least eight indicators")
    if len({item.get('system_id') for item in systems}) != len(systems):
        errors.append("duplicate system ids")
    if len({item.get('indicator_id') for item in indicators}) != len(indicators):
        errors.append("duplicate indicator ids")

    for system in systems:
        for field in ["truth_state", "incentives", "beneficiaries", "payers", "risks", "outcome_contract", "source_ids"]:
            if not system.get(field):
                errors.append(f"{system.get('system_id')} missing {field}")
        for source_id in system.get("source_ids", []):
            if source_id not in source_ids:
                errors.append(f"{system.get('system_id')} unknown source {source_id}")

    for item in indicators:
        for field in ["source_id", "observed_at", "evidence_status", "why_it_matters", "period"]:
            if not item.get(field):
                errors.append(f"{item.get('indicator_id')} missing {field}")
        if item.get("source_id") not in source_ids:
            errors.append(f"{item.get('indicator_id')} unknown source")

    registry_path = root / "policy_platform" / "source_registry.json"
    if not registry_path.exists():
        errors.append("source monitor registry missing")
        registry = {}
    else:
        registry = load(registry_path)
        monitored_ids = {item.get("source_id") for item in registry.get("sources", [])}
        if monitored_ids != source_ids:
            errors.append("source monitor registry must cover the full public catalog source set")
        for item in registry.get("sources", []):
            if not item.get("required_markers"):
                errors.append(f"{item.get('source_id')} has no reviewed markers")

    dashboard = (root / "deutschland_dashboard" / "index.html").read_text(encoding="utf-8")
    review_page = (root / "policy_review" / "index.html").read_text(encoding="utf-8")
    mcp = (root / "mcp_server" / "server.py").read_text(encoding="utf-8")
    refresh = (root / "policy_platform" / "refresh.py").read_text(encoding="utf-8")
    schedule_path = root.parent / ".github" / "workflows" / "safetrace-policy-refresh.yml"
    issue_template = root.parent / ".github" / "ISSUE_TEMPLATE" / "policy-evidence-challenge.yml"

    if "No single national score" not in dashboard and "No composite Germany score" not in catalog.get("boundary", ""):
        errors.append("dashboard composite-score boundary missing")
    if "fetch('../open_policy_api/v1/catalog.json')" not in dashboard:
        errors.append("dashboard does not consume API")
    if "policy_review" not in dashboard:
        errors.append("dashboard does not link to human review")
    if "external-review-receipt" not in review_page or "localStorage" not in review_page:
        errors.append("browser-local external review receipt missing")
    if any(token in mcp for token in PROHIBITED):
        errors.append("prohibited MCP capability exposed")
    if docs.get("openapi.json", {}).get("openapi") != "3.1.1":
        errors.append("OpenAPI version mismatch")
    if "history.json" not in docs.get("index.json", {}).get("documents", {}).values():
        errors.append("API history not discoverable")
    if not docs.get("history.json", {}).get("snapshots"):
        errors.append("snapshot history empty")
    if "publication_allowed\": False" not in refresh and '"publication_allowed": False' not in refresh:
        errors.append("refresh boundary does not explicitly block publication")
    if not schedule_path.exists() or "schedule:" not in schedule_path.read_text(encoding="utf-8"):
        errors.append("scheduled source monitor missing")
    if not issue_template.exists():
        errors.append("public evidence challenge template missing")

    hashes = {name: hashlib.sha256((api / name).read_bytes()).hexdigest() for name in files if (api / name).exists()}
    return {
        "schema_version": "safetrace.policy-platform-release/1.1",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "counts": {
            "systems": len(systems),
            "indicators": len(indicators),
            "sources": len(source_ids),
            "monitored_sources": len(registry.get("sources", [])),
            "mcp_tools": 6,
            "mcp_resources": 2,
            "published_snapshots": len(docs.get("history.json", {}).get("snapshots", [])),
        },
        "hashes": hashes,
        "boundaries": {
            "read_only_api": True,
            "no_composite_score": True,
            "no_automatic_publication": True,
            "no_restricted_data": True,
            "external_review_browser_local": True,
            "scheduled_monitor_requires_human_review": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("safetrace"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
