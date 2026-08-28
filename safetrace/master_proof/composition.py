from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
GOLDEN = json.loads((ROOT / "golden_cases.json").read_text(encoding="utf-8"))
CONTRACTS = json.loads((ROOT / "module_contracts.json").read_text(encoding="utf-8"))["modules"]
CASES = {case["id"]: case for case in GOLDEN["cases"]}

# Shared infrastructure may satisfy a capability even when a golden fixture did
# not originally name the repo explicitly. This is composition, not ownership.
SHARED_MODULES = ["JudgeMCP", "CivicMCPToolkit", "OpenAction", "WohngeldMCP", "ElterngeldMCP"]


def providers_for(capability: str, preferred: list[str] | None = None) -> list[dict[str, Any]]:
    preferred = preferred or []
    ordered = list(dict.fromkeys([*preferred, *SHARED_MODULES, *CONTRACTS.keys()]))
    providers = []
    for module_name in ordered:
        module = CONTRACTS.get(module_name)
        if not module or capability not in module.get("capabilities", []):
            continue
        providers.append({
            "module": module_name,
            "repository": module["repository"],
            "adapter_state": module["adapter_state"],
            "role": module["role"],
            "limitations": module.get("limitations", [])
        })
    return providers


def compose_case(case_id: str) -> dict[str, Any]:
    if case_id not in CASES:
        raise KeyError(case_id)
    case = CASES[case_id]
    required = case["expected"]["capabilities"]
    preferred = case["modules"]
    bindings: list[dict[str, Any]] = []
    missing: list[str] = []
    for capability in required:
        providers = providers_for(capability, preferred)
        if not providers:
            missing.append(capability)
            bindings.append({"capability": capability, "status": "missing", "providers": []})
        else:
            bindings.append({
                "capability": capability,
                "status": "covered",
                "selected_provider": providers[0],
                "alternatives": providers[1:]
            })

    provider_names = sorted({
        binding["selected_provider"]["module"]
        for binding in bindings
        if binding["status"] == "covered"
    })
    adapter_risks = [
        {
            "module": name,
            "adapter_state": CONTRACTS[name]["adapter_state"],
            "limitations": CONTRACTS[name].get("limitations", [])
        }
        for name in provider_names
        if CONTRACTS[name]["adapter_state"] not in {"local_component", "shared_infrastructure"}
    ]
    return {
        "case_id": case_id,
        "question": case["question"],
        "capabilities_required": len(required),
        "capabilities_covered": len(required) - len(missing),
        "coverage": round((len(required) - len(missing)) / len(required), 4) if required else 1.0,
        "missing_capabilities": missing,
        "bindings": bindings,
        "modules_used": provider_names,
        "adapter_risks": adapter_risks,
        "composition_ready": not missing
    }


def portfolio_graph() -> dict[str, Any]:
    cases = [compose_case(case["id"]) for case in GOLDEN["cases"]]
    capability_count = sum(case["capabilities_required"] for case in cases)
    covered = sum(case["capabilities_covered"] for case in cases)
    module_usage: dict[str, int] = {}
    for case in cases:
        for module in case["modules_used"]:
            module_usage[module] = module_usage.get(module, 0) + 1
    return {
        "cases": cases,
        "cases_composition_ready": sum(1 for case in cases if case["composition_ready"]),
        "total_cases": len(cases),
        "capability_coverage": round(covered / capability_count, 4) if capability_count else 1.0,
        "module_usage": [
            {"module": module, "cases": count, "repository": CONTRACTS[module]["repository"]}
            for module, count in sorted(module_usage.items(), key=lambda item: (-item[1], item[0]))
        ],
        "principle": "One platform contract; independently tested modules; explicit adapters and limitations."
    }


if __name__ == "__main__":
    print(json.dumps(portfolio_graph(), ensure_ascii=False, indent=2))
