from __future__ import annotations

import argparse
import html
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SUPPORTED_ENTITY_KINDS = {"person", "company", "trust", "other"}
SUPPORTED_RESOLUTION = {"confirmed", "candidate", "ambiguous", "unresolved"}
SUPPORTED_EDGE_STATUS = {"established", "candidate", "contradictory", "not_established"}
DEFAULT_CONTROL_RIGHTS = {
    "board_appointment",
    "board_majority",
    "veto",
    "dominant_influence",
    "contractual_control",
}


def _index(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in items}


def _pct(value: float | None) -> str:
    if value is None:
        return "unknown"
    number = f"{value * 100:.2f}".rstrip("0").rstrip(".")
    return f"{number}%"


def _threshold_hit(value: float | None, policy: dict[str, Any]) -> bool:
    if value is None:
        return False
    threshold = float(policy.get("ubo_threshold", 0.25))
    operator = policy.get("ubo_threshold_operator", "gt")
    if operator == "gt":
        return value > threshold
    if operator == "gte":
        return value >= threshold
    raise ValueError("ubo_threshold_operator must be 'gt' or 'gte'")


def validate_case(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entities = _index(data.get("entities", []))
    sources = _index(data.get("sources", []))
    target = data.get("target_entity_id")
    if target not in entities:
        errors.append("target_entity_id must reference an entity")

    for entity in data.get("entities", []):
        if entity.get("kind") not in SUPPORTED_ENTITY_KINDS:
            errors.append(f"{entity.get('id')}: unsupported entity kind")
        if entity.get("resolution_status", "unresolved") not in SUPPORTED_RESOLUTION:
            errors.append(f"{entity.get('id')}: unsupported resolution_status")

    edge_ids: set[str] = set()
    for edge in data.get("ownership_edges", []):
        eid = edge.get("id")
        if not eid or eid in edge_ids:
            errors.append(f"{eid or '<missing>'}: ownership edge id must be unique")
        edge_ids.add(eid)
        if edge.get("owner_id") not in entities:
            errors.append(f"{eid}: unknown owner_id")
        if edge.get("target_id") not in entities:
            errors.append(f"{eid}: unknown target_id")
        if edge.get("status", "not_established") not in SUPPORTED_EDGE_STATUS:
            errors.append(f"{eid}: unsupported edge status")
        for field in ("economic_pct", "voting_pct"):
            value = edge.get(field)
            if value is not None and not 0 <= float(value) <= 1:
                errors.append(f"{eid}: {field} must be between 0 and 1")
        evidence = edge.get("evidence", [])
        if edge.get("status") == "established" and not evidence:
            errors.append(f"{eid}: established edge requires evidence")
        for ev in evidence:
            if ev.get("source_id") not in sources:
                errors.append(f"{eid}: evidence references unknown source {ev.get('source_id')}")
            if not ev.get("anchor"):
                errors.append(f"{eid}: evidence requires an anchor")

    policy = data.get("policy", {})
    threshold = float(policy.get("ubo_threshold", 0.25))
    if not 0 <= threshold <= 1:
        errors.append("ubo_threshold must be between 0 and 1")
    if policy.get("ubo_threshold_operator", "gt") not in {"gt", "gte"}:
        errors.append("ubo_threshold_operator must be 'gt' or 'gte'")
    return errors


def _cycle_findings(data: dict[str, Any]) -> list[dict[str, Any]]:
    edges = [e for e in data.get("ownership_edges", []) if e.get("status") == "established"]
    adjacency: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for edge in edges:
        adjacency[edge["owner_id"]].append((edge["target_id"], edge["id"]))

    cycles: set[tuple[str, ...]] = set()
    stack_nodes: list[str] = []
    stack_edges: list[str] = []
    active: dict[str, int] = {}

    def canonical(edge_cycle: list[str]) -> tuple[str, ...]:
        if not edge_cycle:
            return tuple()
        rots = [tuple(edge_cycle[i:] + edge_cycle[:i]) for i in range(len(edge_cycle))]
        return min(rots)

    def dfs(node: str) -> None:
        active[node] = len(stack_nodes)
        stack_nodes.append(node)
        for nxt, edge_id in adjacency.get(node, []):
            if nxt in active:
                start = active[nxt]
                cycles.add(canonical(stack_edges[start:] + [edge_id]))
                continue
            stack_edges.append(edge_id)
            dfs(nxt)
            stack_edges.pop()
        stack_nodes.pop()
        active.pop(node, None)

    for entity_id in sorted(_index(data.get("entities", []))):
        if entity_id not in active:
            dfs(entity_id)

    return [
        {
            "status": "unresolved",
            "type": "ownership_cycle",
            "edge_ids": list(cycle),
            "reason": "Circular ownership prevents naive recursive propagation. The cycle is excluded from UBO aggregation until reviewed.",
        }
        for cycle in sorted(cycles)
    ]


def _walk_paths(data: dict[str, Any], metric: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    entities = _index(data["entities"])
    target = data["target_entity_id"]
    incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in data.get("ownership_edges", []):
        incoming[edge["target_id"]].append(edge)

    complete: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []

    def walk(current: str, factor: float, path: list[dict[str, Any]], seen: set[str]) -> None:
        for edge in incoming.get(current, []):
            owner_id = edge["owner_id"]
            base = {
                "owner_id": owner_id,
                "owner_name": entities[owner_id]["name"],
                "metric": metric,
                "edge_ids": [x["id"] for x in path + [edge]],
                "evidence": [
                    {**ev, "edge_id": x["id"]}
                    for x in path + [edge]
                    for ev in x.get("evidence", [])
                ],
            }
            if owner_id in seen:
                blocked.append({**base, "status": "blocked_cycle", "reason": "Path revisits an entity and is not propagated."})
                continue
            if edge.get("status") != "established":
                blocked.append({**base, "status": f"blocked_{edge.get('status', 'not_established')}", "reason": "Ownership propagation requires an established edge."})
                continue
            resolution = entities[owner_id].get("resolution_status", "unresolved")
            if resolution != "confirmed":
                blocked.append({**base, "status": f"blocked_identity_{resolution}", "reason": "Ownership propagation requires a confirmed owner identity."})
                continue
            value = edge.get(metric)
            if value is None:
                blocked.append({**base, "status": f"blocked_missing_{metric}", "reason": f"{metric} is not established for this edge."})
                continue

            effective = round(factor * float(value), 12)
            full_path = path + [edge]
            complete.append({**base, "status": "established", "effective_pct": effective, "direct": current == target})
            walk(owner_id, effective, full_path, seen | {owner_id})

    walk(target, 1.0, [], {target})
    return complete, blocked


def _aggregate_paths(paths: list[dict[str, Any]], entities: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in paths:
        grouped[path["owner_id"]].append(path)

    out: list[dict[str, Any]] = []
    for owner_id, rows in grouped.items():
        total = round(sum(float(row["effective_pct"]) for row in rows), 12)
        out.append({
            "owner_id": owner_id,
            "owner_name": entities[owner_id]["name"],
            "owner_kind": entities[owner_id]["kind"],
            "resolution_status": entities[owner_id].get("resolution_status", "unresolved"),
            "aggregate_pct": total,
            "path_count": len(rows),
            "paths": sorted(rows, key=lambda r: (r["edge_ids"], r["effective_pct"])),
            "integrity_warning": "aggregate_exceeds_100_percent" if total > 1.0000001 else None,
        })
    return sorted(out, key=lambda row: (-row["aggregate_pct"], row["owner_id"]))


def _direct_control_signals(data: dict[str, Any]) -> list[dict[str, Any]]:
    entities = _index(data["entities"])
    target = data["target_entity_id"]
    configured = set(data.get("policy", {}).get("control_rights", sorted(DEFAULT_CONTROL_RIGHTS)))
    out: list[dict[str, Any]] = []
    for edge in data.get("ownership_edges", []):
        rights = sorted(configured.intersection(edge.get("control_rights", [])))
        if edge.get("target_id") == target and edge.get("status") == "established" and rights and entities[edge["owner_id"]].get("resolution_status") == "confirmed":
            out.append({
                "controller_id": edge["owner_id"],
                "controller_name": entities[edge["owner_id"]]["name"],
                "rights": rights,
                "status": "established_control_signal",
                "edge_id": edge["id"],
                "evidence": edge.get("evidence", []),
                "boundary": "A documented control right is a control signal. Legal control/UBO status remains jurisdiction- and rule-dependent.",
            })
    return out


def investigate(data: dict[str, Any]) -> dict[str, Any]:
    errors = validate_case(data)
    if errors:
        raise ValueError("; ".join(errors))

    entities = _index(data["entities"])
    target = entities[data["target_entity_id"]]
    policy = {
        "ubo_threshold": 0.25,
        "ubo_threshold_operator": "gt",
        "control_rights_establish_candidate": True,
        "control_rights": sorted(DEFAULT_CONTROL_RIGHTS),
        **data.get("policy", {}),
    }

    cycles = _cycle_findings(data)
    economic_paths, economic_blocked = _walk_paths(data, "economic_pct")
    voting_paths, voting_blocked = _walk_paths(data, "voting_pct")
    economic = _aggregate_paths(economic_paths, entities)
    voting = _aggregate_paths(voting_paths, entities)
    economic_by_id = {row["owner_id"]: row for row in economic}
    voting_by_id = {row["owner_id"]: row for row in voting}
    control_signals = _direct_control_signals({**data, "policy": policy})
    controls_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for signal in control_signals:
        controls_by_id[signal["controller_id"]].append(signal)

    candidate_ids: set[str] = set()
    candidates: list[dict[str, Any]] = []
    for entity in data["entities"]:
        if entity["kind"] != "person" or entity.get("resolution_status") != "confirmed":
            continue
        owner_id = entity["id"]
        econ = economic_by_id.get(owner_id, {}).get("aggregate_pct")
        vote = voting_by_id.get(owner_id, {}).get("aggregate_pct")
        rights = controls_by_id.get(owner_id, [])
        grounds: list[str] = []
        if _threshold_hit(econ, policy):
            grounds.append("economic_ownership_threshold")
        if _threshold_hit(vote, policy):
            grounds.append("voting_rights_threshold")
        if rights and policy.get("control_rights_establish_candidate", True):
            grounds.append("documented_control_right")
        if grounds:
            candidate_ids.add(owner_id)
            why_paths = []
            for row in (economic_by_id.get(owner_id), voting_by_id.get(owner_id)):
                if row:
                    why_paths.extend(row["paths"])
            candidates.append({
                "entity_id": owner_id,
                "name": entity["name"],
                "status": "candidate_under_configured_rule",
                "grounds": grounds,
                "economic_pct": econ,
                "voting_pct": vote,
                "control_signals": rights,
                "why": {
                    "paths": why_paths,
                    "policy": {
                        "threshold": policy["ubo_threshold"],
                        "operator": policy["ubo_threshold_operator"],
                        "control_rights_establish_candidate": policy["control_rights_establish_candidate"],
                    },
                },
                "boundary": "Candidate under the configured analytical rule; not a definitive legal beneficial-owner determination.",
            })

    unresolved: list[dict[str, Any]] = []
    unresolved.extend(cycles)
    for row in economic_blocked + voting_blocked:
        unresolved.append({
            "type": "blocked_path",
            "metric": row["metric"],
            "owner_id": row["owner_id"],
            "owner_name": row["owner_name"],
            "status": row["status"],
            "reason": row["reason"],
            "edge_ids": row["edge_ids"],
            "evidence": row["evidence"],
        })
    for gap in data.get("collection_gaps", []):
        unresolved.append({**gap, "status": gap.get("status", "not_established")})

    established_economic_edges = [e for e in data.get("ownership_edges", []) if e.get("status") == "established" and e.get("economic_pct") is not None]
    missing_vote_edges = [e["id"] for e in established_economic_edges if e.get("voting_pct") is None]
    if missing_vote_edges:
        unresolved.append({
            "type": "voting_data_gap",
            "status": "not_established",
            "edge_ids": missing_vote_edges,
            "reason": "Economic ownership is documented on these edges, but voting rights are not. No equality is inferred.",
        })

    source_ids = sorted({ev["source_id"] for edge in data.get("ownership_edges", []) for ev in edge.get("evidence", [])})
    result = {
        "schema_version": "safetrace.ownership-control/1.0",
        "case_id": data["case_id"],
        "classification": data.get("classification", "unspecified"),
        "subject": {"id": target["id"], "name": target["name"], "kind": target["kind"]},
        "policy": policy,
        "economic_ownership": economic,
        "voting_rights": voting,
        "control_signals": control_signals,
        "ubo_candidates": sorted(candidates, key=lambda x: x["name"]),
        "unresolved": unresolved,
        "source_ids_used": source_ids,
        "metrics": {
            "entities": len(data["entities"]),
            "ownership_edges": len(data.get("ownership_edges", [])),
            "established_edges": sum(e.get("status") == "established" for e in data.get("ownership_edges", [])),
            "economic_paths": len(economic_paths),
            "voting_paths": len(voting_paths),
            "control_signals": len(control_signals),
            "ubo_candidates": len(candidates),
            "cycles": len(cycles),
            "blocked_paths": len(economic_blocked) + len(voting_blocked),
            "unresolved_items": len(unresolved),
        },
        "decision_boundary": {
            "ownership_established": bool(economic),
            "voting_control_established": bool(voting),
            "beneficial_ownership_complete": not unresolved and bool(candidate_ids),
            "human_review_required": True,
            "statement": "Economic ownership, voting rights and other control are separate evidence dimensions. Missing evidence remains unknown.",
        },
        "guardrails": [
            "No ownership percentage is inferred from a company name, role or website mention.",
            "Ambiguous or unresolved identities block downstream ownership propagation.",
            "Candidate or contradictory ownership edges do not propagate.",
            "Economic ownership is not assumed to equal voting rights.",
            "Control rights are reported separately from equity.",
            "Cycles are surfaced and excluded from naive recursive aggregation.",
            "UBO candidates are rule-scoped analytical candidates, not final legal determinations.",
        ],
    }
    return result


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# Ownership & Control — {result['subject']['name']}", "",
        f"**Case:** `{result['case_id']}`", f"**Schema:** `{result['schema_version']}`", "**Human review required:** yes", "",
        "## Executive result", "",
        f"- Economic ownership paths: **{result['metrics']['economic_paths']}**",
        f"- Voting-rights paths: **{result['metrics']['voting_paths']}**",
        f"- Documented control signals: **{result['metrics']['control_signals']}**",
        f"- UBO candidates under configured rule: **{result['metrics']['ubo_candidates']}**",
        f"- Unresolved items: **{result['metrics']['unresolved_items']}**", "", "## Economic ownership", "",
    ]
    for row in result["economic_ownership"]:
        lines.append(f"- **{row['owner_name']}** — {_pct(row['aggregate_pct'])} aggregate economic interest across {row['path_count']} path(s).")
        for path in row["paths"]:
            lines.append(f"  - Why: {' → '.join(path['edge_ids'])} = {_pct(path['effective_pct'])}; evidence: " + ", ".join(f"{ev['source_id']}#{ev['anchor']}" for ev in path["evidence"]))
    if not result["economic_ownership"]:
        lines.append("- Not established.")

    lines += ["", "## Voting rights", ""]
    for row in result["voting_rights"]:
        lines.append(f"- **{row['owner_name']}** — {_pct(row['aggregate_pct'])} documented voting-rights path aggregate.")
    if not result["voting_rights"]:
        lines.append("- Not established. Economic ownership is not substituted for missing voting evidence.")

    lines += ["", "## Other control", ""]
    for signal in result["control_signals"]:
        lines.append(f"- **{signal['controller_name']}** — {', '.join(signal['rights'])}. _Evidence: " + ", ".join(f"{ev['source_id']}#{ev['anchor']}" for ev in signal["evidence"]) + "_")
    if not result["control_signals"]:
        lines.append("- No documented control-right signal established in the supplied evidence.")

    lines += ["", "## UBO candidates under configured rule", ""]
    for candidate in result["ubo_candidates"]:
        lines.append(f"- **{candidate['name']}** — {', '.join(candidate['grounds'])}; economic {_pct(candidate['economic_pct'])}; voting {_pct(candidate['voting_pct'])}.")
    if not result["ubo_candidates"]:
        lines.append("- None established from the supplied evidence. This does not prove that no beneficial owner exists.")

    lines += ["", "## Still unknown / blocked", ""]
    for item in result["unresolved"]:
        lines.append(f"- **{item.get('type', 'gap')} · {item.get('status', 'unresolved')}** — {item.get('reason', 'Not established.')}")
    if not result["unresolved"]:
        lines.append("- No unresolved item in this bounded case.")

    lines += ["", "## Boundary", "", result["decision_boundary"]["statement"], "", "The output is an evidence-backed analytical work product. Consequential or legal UBO/control conclusions require human review and the applicable jurisdiction-specific rules.", ""]
    return "\n".join(lines)


def render_html(result: dict[str, Any]) -> str:
    esc = lambda x: html.escape(str(x), quote=True)
    metrics = result["metrics"]
    ownership = "".join(
        f"<article class='card'><div class='eyebrow'>{esc(row['owner_kind'])}</div><h3>{esc(row['owner_name'])}</h3><div class='value'>{esc(_pct(row['aggregate_pct']))}</div><p>{row['path_count']} evidence-backed path(s)</p>"
        + "".join("<details><summary>Show me why</summary><p>" + esc(" → ".join(path["edge_ids"])) + " = " + esc(_pct(path["effective_pct"])) + "</p><ul>" + "".join(f"<li>{esc(ev['source_id'])} · {esc(ev['anchor'])}</li>" for ev in path["evidence"]) + "</ul></details>" for path in row["paths"])
        + "</article>" for row in result["economic_ownership"]
    ) or "<p class='muted'>Economic ownership not established.</p>"
    candidates = "".join(
        f"<article class='card candidate'><div class='eyebrow'>RULE-SCOPED CANDIDATE</div><h3>{esc(c['name'])}</h3><p>{esc(', '.join(c['grounds']))}</p><p>Economic: <b>{esc(_pct(c['economic_pct']))}</b> · Voting: <b>{esc(_pct(c['voting_pct']))}</b></p><small>{esc(c['boundary'])}</small></article>"
        for c in result["ubo_candidates"]
    ) or "<p class='muted'>No UBO candidate established from supplied evidence.</p>"
    gaps = "".join(f"<li><b>{esc(x.get('type','gap'))}</b><span>{esc(x.get('status','unresolved'))}</span><p>{esc(x.get('reason','Not established.'))}</p></li>" for x in result["unresolved"]) or "<li>No unresolved item in this bounded case.</li>"
    control_cards: list[str] = []
    for signal in result["control_signals"]:
        evidence_items = "".join(f"<li>{esc(ev['source_id'])} · {esc(ev['anchor'])}</li>" for ev in signal["evidence"])
        control_cards.append(f"<article class='card'><h3>{esc(signal['controller_name'])}</h3><div class='value smallvalue'>{esc(', '.join(signal['rights']))}</div><details><summary>Show me why</summary><ul>{evidence_items}</ul></details></article>")
    controls = "".join(control_cards) or "<p class='muted'>No documented non-equity control signal.</p>"

    return f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Ownership & Control — {esc(result['subject']['name'])}</title><style>
:root{{--bg:#07100f;--panel:#0e1917;--panel2:#13211f;--line:#263a36;--text:#f1f7f5;--muted:#9bb0aa;--accent:#96e8c4;--warn:#f4c36a}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 Inter,system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:52px 24px 88px}}h1{{font-size:clamp(42px,7vw,78px);line-height:.94;letter-spacing:-.055em;margin:8px 0 18px}}h2{{margin:52px 0 18px;font-size:27px}}h3{{margin:8px 0}}.kicker,.eyebrow{{text-transform:uppercase;letter-spacing:.12em;font-size:11px;font-weight:800;color:var(--accent)}}.lead{{font-size:19px;max-width:900px;color:#dbe9e5}}.metrics{{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin:28px 0}}.metric,.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px}}.metric b{{display:block;font-size:30px}}.metric span,.muted,small{{color:var(--muted)}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}}.value{{font-size:28px;font-weight:780}}.smallvalue{{font-size:18px}}details{{border-top:1px solid var(--line);padding:9px 0;margin-top:12px}}summary{{cursor:pointer;color:var(--accent)}}.candidate{{border-color:#567664}}ul.gaps{{list-style:none;padding:0;display:grid;gap:10px}}.gaps li{{background:var(--panel2);border-left:3px solid var(--warn);padding:15px 18px}}.gaps span{{margin-left:10px;color:var(--warn);font-size:12px}}.boundary{{margin-top:48px;border:1px solid var(--line);border-radius:14px;padding:20px;background:var(--panel2)}}@media(max-width:820px){{.metrics{{grid-template-columns:repeat(2,1fr)}}.grid{{grid-template-columns:1fr}}}}
</style></head><body><main><div class='kicker'>SafeTrace · Ownership & Control</div><h1>{esc(result['subject']['name'])}</h1><p class='lead'>Trace economic ownership, voting rights and documented control separately. Every propagated conclusion carries its evidence chain; ambiguous identities and missing edges stop propagation.</p><div class='metrics'><div class='metric'><b>{metrics['entities']}</b><span>entities</span></div><div class='metric'><b>{metrics['established_edges']}</b><span>established edges</span></div><div class='metric'><b>{metrics['economic_paths']}</b><span>economic paths</span></div><div class='metric'><b>{metrics['voting_paths']}</b><span>voting paths</span></div><div class='metric'><b>{metrics['ubo_candidates']}</b><span>UBO candidates</span></div><div class='metric'><b>{metrics['unresolved_items']}</b><span>open items</span></div></div><h2>Economic ownership</h2><div class='grid'>{ownership}</div><h2>Other documented control</h2><div class='grid'>{controls}</div><h2>UBO candidates under configured rule</h2><div class='grid'>{candidates}</div><h2>Still unknown / blocked</h2><ul class='gaps'>{gaps}</ul><div class='boundary'><div class='eyebrow'>Decision boundary</div><p>{esc(result['decision_boundary']['statement'])}</p><p class='muted'>Analytical candidates are not final legal UBO determinations. Human review and applicable jurisdiction-specific rules are required.</p></div></main></body></html>"""


def run_case(case_path: Path, out_dir: Path) -> dict[str, Any]:
    data = json.loads(case_path.read_text(encoding="utf-8"))
    result = investigate(data)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "report.md").write_text(render_markdown(result), encoding="utf-8")
    (out_dir / "index.html").write_text(render_html(result), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Trace evidence-backed ownership and control.")
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("artifacts/ownership-control"))
    args = parser.parse_args()
    result = run_case(args.case, args.out)
    print(json.dumps(result["metrics"], indent=2))
    print(f"UBO candidates: {[x['name'] for x in result['ubo_candidates']]}")
    if any(x.get("integrity_warning") for x in result["economic_ownership"]):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
