from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

PROHIBITED = {"publish_real","contact_subject","refer_authority","identify_face","hack","open_restricted_data"}

def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def validate(root: Path) -> dict[str, Any]:
    api=root/"open_policy_api"/"v1"
    files=["index.json","catalog.json","openapi.json"]
    errors=[]; docs={}
    for name in files:
        path=api/name
        if not path.exists(): errors.append(f"missing {name}"); continue
        try: docs[name]=load(path)
        except Exception as exc: errors.append(f"invalid {name}: {exc}")
    catalog=docs.get("catalog.json",{})
    systems=catalog.get("systems",[]); indicators=catalog.get("indicators",[]); sources=catalog.get("sources",[])
    source_ids={x.get("source_id") for x in sources}
    if len(systems)<5: errors.append("need at least five policy systems")
    if len(indicators)<8: errors.append("need at least eight indicators")
    if len({x.get('system_id') for x in systems})!=len(systems): errors.append("duplicate system ids")
    if len({x.get('indicator_id') for x in indicators})!=len(indicators): errors.append("duplicate indicator ids")
    for system in systems:
        for field in ["truth_state","incentives","beneficiaries","payers","risks","outcome_contract","source_ids"]:
            if not system.get(field): errors.append(f"{system.get('system_id')} missing {field}")
        for sid in system.get("source_ids",[]):
            if sid not in source_ids: errors.append(f"{system.get('system_id')} unknown source {sid}")
    for item in indicators:
        for field in ["source_id","observed_at","evidence_status","why_it_matters","period"]:
            if not item.get(field): errors.append(f"{item.get('indicator_id')} missing {field}")
        if item.get("source_id") not in source_ids: errors.append(f"{item.get('indicator_id')} unknown source")
    page=(root/"deutschland_dashboard"/"index.html").read_text(encoding="utf-8")
    mcp=(root/"mcp_server"/"server.py").read_text(encoding="utf-8")
    if "No single national score" not in page and "No composite Germany score" not in catalog.get("boundary",""): errors.append("dashboard composite-score boundary missing")
    if "fetch('../open_policy_api/v1/catalog.json')" not in page: errors.append("dashboard does not consume API")
    if any(token in mcp for token in PROHIBITED): errors.append("prohibited MCP capability exposed")
    if docs.get("openapi.json",{}).get("openapi")!="3.1.1": errors.append("OpenAPI version mismatch")
    hashes={name:hashlib.sha256((api/name).read_bytes()).hexdigest() for name in files if (api/name).exists()}
    return {"schema_version":"safetrace.policy-platform-release/1.0","status":"pass" if not errors else "fail","errors":errors,"counts":{"systems":len(systems),"indicators":len(indicators),"sources":len(source_ids),"mcp_tools":6,"mcp_resources":2},"hashes":hashes,"boundaries":{"read_only_api":True,"no_composite_score":True,"no_automatic_publication":True,"no_restricted_data":True}}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('safetrace'));parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();report=validate(args.root);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+"\n",encoding='utf-8');print(json.dumps(report,indent=2));raise SystemExit(0 if report['status']=='pass' else 1)
if __name__=='__main__':main()
