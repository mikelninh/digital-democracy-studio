from __future__ import annotations
import argparse, dataclasses, json, types
from dataclasses import MISSING
from pathlib import Path
from typing import Any, get_args, get_origin, get_type_hints
from . import model
from .vocabularies import *

CLASSES=(model.Risk,model.CaseCharter,model.Case,model.Source,model.Snapshot,model.Entity,model.Evidence,model.Relationship,model.Event,model.Claim,model.Review,model.Publication,model.Correction,model.AgentTask,model.InvestigationBundle)
ENUMS={
("Risk","category"):RISK_CATEGORIES,("Risk","likelihood"):RISK_LEVELS,("Risk","severity"):RISK_LEVELS,
("CaseCharter","status"):CHARTER_STATUSES,("CaseCharter","permitted_data_zones"):DATA_ZONES,
("Case","status"):CASE_STATUSES,("Source","source_rank"):SOURCE_RANKS,("Source","access_status"):SOURCE_ACCESS_STATES,("Source","sensitivity"):FIELD_SENSITIVITIES,("Snapshot","sensitivity"):FIELD_SENSITIVITIES,("Entity","entity_type"):ENTITY_TYPES,("Entity","sensitivity"):FIELD_SENSITIVITIES,("Evidence","role"):EVIDENCE_ROLES,("Evidence","sensitivity"):FIELD_SENSITIVITIES,("Relationship","relationship_type"):RELATIONSHIP_TYPES,("Relationship","confidence"):RELATIONSHIP_CONFIDENCE,("Relationship","sensitivity"):FIELD_SENSITIVITIES,("Event","event_type"):EVENT_TYPES,("Event","evidence_state"):EVIDENCE_STATES,("Event","legal_status"):LEGAL_STATUSES,("Event","sensitivity"):FIELD_SENSITIVITIES,("Claim","evidence_state"):EVIDENCE_STATES,("Claim","sensitivity"):FIELD_SENSITIVITIES,("Claim","origin"):EVIDENCE_ORIGINS,("Claim","legal_status"):LEGAL_STATUSES,("Review","subject_type"):SUBJECT_TYPES,("Review","outcome"):REVIEW_OUTCOMES,("Review","legal_review"):LEGAL_REVIEW_STATES,("Review","right_of_reply"):RIGHT_OF_REPLY_STATES,("Publication","edition"):PUBLICATION_EDITIONS,("Publication","status"):PUBLICATION_STATUSES,("Correction","subject_type"):SUBJECT_TYPES,("AgentTask","agent_type"):AGENT_TYPES,("AgentTask","status"):AGENT_TASK_STATUSES,("AgentTask","max_data_zone"):DATA_ZONES,
}

def type_schema(t:Any)->dict[str,Any]:
    if dataclasses.is_dataclass(t):return {"$ref":f"#/$defs/{t.__name__}"}
    origin=get_origin(t); args=get_args(t)
    if origin in (list,tuple,set,frozenset):return {"type":"array","items":type_schema(args[0]) if args else {}}
    if origin is dict:return {"type":"object","additionalProperties":type_schema(args[1]) if len(args)>1 else {}}
    if origin in (types.UnionType,):return {"anyOf":[type_schema(x) for x in args]}
    if origin is not None and str(origin).endswith("Union"):return {"anyOf":[type_schema(x) for x in args]}
    if t is str:return {"type":"string"}
    if t is int:return {"type":"integer"}
    if t is bool:return {"type":"boolean"}
    if t in (Any,object):return {}
    if t is type(None):return {"type":"null"}
    return {}

def class_schema(c:type)->dict[str,Any]:
    hints=get_type_hints(c); props={}; required=[]
    for f in dataclasses.fields(c):
        s=type_schema(hints.get(f.name,Any)); values=ENUMS.get((c.__name__,f.name))
        if values:
            if s.get("type")=="array":s["items"]={"type":"string","enum":sorted(values)}
            else:s={"type":"string","enum":sorted(values)}
        props[f.name]=s
        if f.default is MISSING and f.default_factory is MISSING:required.append(f.name)
    return {"type":"object","additionalProperties":False,"properties":props,"required":required}

def generate_schema()->dict[str,Any]:
    root=class_schema(model.InvestigationBundle)
    root.update({"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"https://mikelninh.github.io/digital-democracy-studio/safetrace/core/schemas/safetrace-core-1.2.schema.json","title":"SafeTrace Unified Investigation Bundle v1.2","description":"Machine-readable evidence, review, publication and agent-task model governed by the SafeTrace Constitution."})
    root["properties"]["schema_version"]={"const":SCHEMA_VERSION}
    root["$defs"]={c.__name__:class_schema(c) for c in CLASSES if c is not model.InvestigationBundle}
    return root

def schema_document()->dict[str,Any]:
    return generate_schema()

def serialised_schema()->str:
    return json.dumps(generate_schema(),ensure_ascii=False,separators=(",",":"),sort_keys=True)+"\n"

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--write",type=Path); p.add_argument("--check",type=Path); a=p.parse_args(); expected=generate_schema()
    if a.write:a.write.parent.mkdir(parents=True,exist_ok=True); a.write.write_text(serialised_schema(),encoding="utf-8")
    if a.check:
        actual=json.loads(a.check.read_text(encoding="utf-8"))
        if actual!=expected:raise SystemExit("Committed SafeTrace core schema differs from generated schema")
    if not a.write and not a.check:print(json.dumps(expected,ensure_ascii=False,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
