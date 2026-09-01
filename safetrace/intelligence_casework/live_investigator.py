from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parent
DEFAULT_CASE = ROOT / "fixtures" / "live_case.json"
DEFAULT_OUT = ROOT / "artifacts" / "live_investigation"


def stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}:{digest}"


def normalise_name(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\b(gmbh|ltd|limited|llc|ag|inc|corp|co|sarl|bv|plc)\b", "", value)
    return re.sub(r"\s+", " ", value).strip()


@dataclass
class Source:
    id: str
    title: str
    publisher: str
    source_type: str
    authority: float
    freshness: float
    text: str
    anchor: str


@dataclass
class Entity:
    id: str
    name: str
    entity_type: str
    jurisdiction: str | None = None
    identifiers: Dict[str, str] | None = None


@dataclass
class Relationship:
    source: str
    target: str
    kind: str
    confidence: float
    evidence: List[str]
    status: str = "verified"
    note: str | None = None


@dataclass
class Finding:
    id: str
    title: str
    assessment: str
    severity: str
    confidence: float
    evidence: List[str]
    caveat: str
    next_step: str
    status: str = "open"


def load_case(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_sources(case: Dict[str, Any]) -> List[Source]:
    return [Source(**s) for s in case["sources"]]


def build_entities(case: Dict[str, Any]) -> List[Entity]:
    return [Entity(**e) for e in case["entities"]]


def entity_index(entities: Iterable[Entity]) -> Dict[str, Entity]:
    return {e.id: e for e in entities}


def resolve_aliases(case: Dict[str, Any], entities: List[Entity]) -> Tuple[List[Relationship], List[Dict[str, Any]]]:
    rels: List[Relationship] = []
    decisions: List[Dict[str, Any]] = []
    idx = entity_index(entities)
    for item in case.get("alias_candidates", []):
        left, right = idx[item["left"]], idx[item["right"]]
        name_match = normalise_name(left.name) == normalise_name(right.name)
        id_left = left.identifiers or {}
        id_right = right.identifiers or {}
        shared_ids = {k: v for k, v in id_left.items() if id_right.get(k) == v}
        conflicts = {k: (v, id_right[k]) for k, v in id_left.items() if k in id_right and id_right[k] != v}
        if shared_ids and not conflicts:
            status = "same_as"
            confidence = 0.99
        elif conflicts:
            status = "not_same_as"
            confidence = 0.99
        elif name_match:
            status = "related_to_review"
            confidence = 0.55
        else:
            status = "unresolved"
            confidence = 0.35
        decisions.append({
            "left": left.id,
            "right": right.id,
            "status": status,
            "confidence": confidence,
            "shared_identifiers": shared_ids,
            "conflicting_identifiers": conflicts,
            "evidence": item.get("evidence", []),
        })
        if status == "same_as":
            rels.append(Relationship(left.id, right.id, "SAME_AS", confidence, item.get("evidence", [])))
        elif status == "not_same_as":
            rels.append(Relationship(left.id, right.id, "NOT_SAME_AS", confidence, item.get("evidence", []), status="rejected"))
    return rels, decisions


def build_relationships(case: Dict[str, Any]) -> List[Relationship]:
    return [Relationship(**r) for r in case.get("relationships", [])]


def calculate_indirect_ownership(case: Dict[str, Any]) -> List[Dict[str, Any]]:
    direct = case.get("ownership", [])
    pct: Dict[Tuple[str, str], float] = {(x["owner"], x["owned"]): float(x["percent"]) for x in direct}
    results: List[Dict[str, Any]] = []
    for a in direct:
        for b in direct:
            if a["owned"] != b["owner"]:
                continue
            percent = float(a["percent"]) * float(b["percent"]) / 100.0
            results.append({
                "owner": a["owner"],
                "through": a["owned"],
                "owned": b["owned"],
                "percent": round(percent, 2),
                "evidence": sorted(set(a.get("evidence", []) + b.get("evidence", []))),
                "interpretation": "economic_interest_not_necessarily_control",
            })
    return results


def detect_contradictions(case: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "subject": c["subject"],
            "field": c["field"],
            "values": c["values"],
            "evidence": c["evidence"],
            "status": "unresolved",
            "next_step": c["next_step"],
        }
        for c in case.get("contradictions", [])
    ]


def sanctions_screen(case: Dict[str, Any], idx: Dict[str, Entity]) -> List[Dict[str, Any]]:
    results = []
    for s in case.get("sanctions_screening", []):
        subject = idx[s["subject"]]
        candidate = idx[s["candidate"]]
        conflicts = []
        for field in ("dob", "nationality", "passport", "registry_id"):
            a = (subject.identifiers or {}).get(field)
            b = (candidate.identifiers or {}).get(field)
            if a and b and a != b:
                conflicts.append(field)
        result = "rejected_match" if conflicts else "manual_review"
        results.append({
            "subject": subject.id,
            "candidate": candidate.id,
            "name_similarity": s["name_similarity"],
            "result": result,
            "conflicting_identifiers": conflicts,
            "evidence": s.get("evidence", []),
            "conclusion": "No sanctions linkage established." if conflicts else "Insufficient evidence to clear or confirm.",
        })
    return results


def make_findings(case: Dict[str, Any], indirect: List[Dict[str, Any]], screening: List[Dict[str, Any]], contradictions: List[Dict[str, Any]]) -> List[Finding]:
    findings: List[Finding] = []
    for spec in case.get("finding_rules", []):
        if spec["rule"] == "payment_route_changed":
            findings.append(Finding(
                id=spec["id"], title=spec["title"], assessment=spec["assessment"], severity="medium",
                confidence=0.88, evidence=spec["evidence"], caveat="A changed beneficiary is a verification trigger, not proof of fraud or evasion.",
                next_step=spec["next_step"]
            ))
        elif spec["rule"] == "unresolved_ubo":
            findings.append(Finding(
                id=spec["id"], title=spec["title"], assessment=spec["assessment"], severity="medium",
                confidence=0.82, evidence=spec["evidence"], caveat="The economic chain is documented only to the nominee entity; the ultimate beneficial owner is not established.",
                next_step=spec["next_step"]
            ))
    for item in indirect:
        findings.append(Finding(
            id=stable_id("finding", f"{item['owner']}->{item['owned']}"),
            title="Indirect economic interest identified",
            assessment=f"{item['owner']} has a documented {item['percent']}% indirect economic interest in {item['owned']} via {item['through']}.",
            severity="info", confidence=0.97, evidence=item["evidence"],
            caveat="Economic interest does not by itself establish de facto control.",
            next_step="Check voting rights, shareholder agreements, reserved matters and board appointment rights."
        ))
    for s in screening:
        findings.append(Finding(
            id=stable_id("finding", f"screen:{s['subject']}:{s['candidate']}"),
            title="Sanctions homonym rejected" if s["result"] == "rejected_match" else "Sanctions candidate requires review",
            assessment=s["conclusion"], severity="info" if s["result"] == "rejected_match" else "high",
            confidence=0.98 if s["result"] == "rejected_match" else 0.55, evidence=s["evidence"],
            caveat="Name similarity alone is not identity evidence.", next_step="Preserve the screening record and re-screen on material identity changes."
        ))
    for c in contradictions:
        findings.append(Finding(
            id=stable_id("finding", f"contradiction:{c['subject']}:{c['field']}"), title="Contradictory source records",
            assessment=f"Conflicting values remain for {c['subject']} / {c['field']}: {', '.join(c['values'])}.", severity="medium",
            confidence=0.99, evidence=c["evidence"], caveat="Neither value is promoted to fact until the contradiction is resolved.", next_step=c["next_step"]
        ))
    return findings


def score_source(source: Source) -> float:
    return round((source.authority * 0.7) + (source.freshness * 0.3), 3)


def render_report(case: Dict[str, Any], findings: List[Finding], indirect: List[Dict[str, Any]], screening: List[Dict[str, Any]], contradictions: List[Dict[str, Any]]) -> str:
    material = [f for f in findings if f.severity in {"high", "medium"}]
    lines = [
        f"# Intelligence Assessment — {case['case']['title']}", "",
        f"**Question:** {case['case']['question']}", "",
        "## Executive judgement", "",
        case['case']['executive_judgement'], "",
        "## Key findings", ""
    ]
    for f in findings:
        lines += [f"### {f.title}", f"- Assessment: {f.assessment}", f"- Confidence: {f.confidence:.0%}", f"- Severity: {f.severity}", f"- Evidence: {', '.join(f.evidence)}", f"- Caveat: {f.caveat}", f"- Next step: {f.next_step}", ""]
    lines += ["## Priority collection plan", ""]
    for i, item in enumerate(case['case']['priority_collection_plan'], 1):
        lines.append(f"{i}. {item}")
    lines += ["", "## Bottom line", "", f"{len(material)} material issues require follow-up. No finding is promoted beyond its evidence boundary; unresolved ownership, contradictions and screening ambiguity remain explicit."]
    return "\n".join(lines) + "\n"


def run(case_path: Path, out_dir: Path) -> Dict[str, Any]:
    case = load_case(case_path)
    sources = build_sources(case)
    entities = build_entities(case)
    idx = entity_index(entities)
    alias_rels, alias_decisions = resolve_aliases(case, entities)
    rels = build_relationships(case) + alias_rels
    indirect = calculate_indirect_ownership(case)
    contradictions = detect_contradictions(case)
    screening = sanctions_screen(case, idx)
    findings = make_findings(case, indirect, screening, contradictions)

    source_rows = [dict(asdict(s), quality_score=score_source(s)) for s in sources]
    result = {
        "schema_version": "safetrace.live-investigation/1.0",
        "case": case["case"],
        "entities": [asdict(e) for e in entities],
        "relationships": [asdict(r) for r in rels],
        "entity_resolution": alias_decisions,
        "indirect_ownership": indirect,
        "sanctions_screening": screening,
        "contradictions": contradictions,
        "findings": [asdict(f) for f in findings],
        "sources": source_rows,
        "metrics": {
            "sources_reviewed": len(sources),
            "entities": len(entities),
            "relationships": len(rels),
            "findings": len(findings),
            "material_findings": sum(1 for f in findings if f.severity in {"high", "medium"}),
            "contradictions": len(contradictions),
            "sanctions_false_positives_rejected": sum(1 for x in screening if x["result"] == "rejected_match"),
            "unresolved_items": len(contradictions) + sum(1 for f in findings if "not established" in f.caveat.lower() or "requires follow-up" in f.next_step.lower()),
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "report.md").write_text(render_report(case, findings, indirect, screening, contradictions), encoding="utf-8")
    (out_dir / "graph.json").write_text(json.dumps({"entities": result["entities"], "relationships": result["relationships"]}, indent=2), encoding="utf-8")
    (out_dir / "findings.json").write_text(json.dumps(result["findings"], indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a bounded, evidence-first intelligence investigation.")
    parser.add_argument("--case", type=Path, default=DEFAULT_CASE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    result = run(args.case, args.out)
    print(json.dumps(result["metrics"], indent=2))


if __name__ == "__main__":
    main()
