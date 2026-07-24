from __future__ import annotations

import argparse
import json
from pathlib import Path

from safetrace.core.vocabularies import SOURCE_RANKS
from .vocabularies import *


def obj(properties: dict, required: list[str]) -> dict:
    return {"type":"object","additionalProperties":False,"properties":properties,"required":required}

def string(enum=None):
    value={"type":"string"}
    if enum is not None:value["enum"]=sorted(enum)
    return value

def nullable(schema):return {"anyOf":[schema,{"type":"null"}]}
def array(schema):return {"type":"array","items":schema}

OBJECT_REF=obj({"sha256":string(),"object_key":string(),"byte_length":{"type":"integer","minimum":0},"content_type":string(),"kind":string(OBJECT_KINDS),"sensitivity":string(FIELD_SENSITIVITIES)},["sha256","object_key","byte_length","content_type","kind"])
REGISTRY_ENTRY=obj({"source_id":string(),"title":string(),"publisher":string(),"canonical_url":string(),"source_type":string(),"source_rank":string(SOURCE_RANKS),"jurisdiction":string(),"update_cadence":string(UPDATE_CADENCES),"connector_id":string(),"connector_version":string(),"parser_id":string(),"parser_version":string(),"expected_content_types":array(string()),"retention_policy_id":string(),"reviewed_by":string(),"reviewed_at":string(),"review_state":string(REGISTRY_REVIEW_STATES),"data_zone":string(DATA_ZONES),"enabled":{"type":"boolean"},"notes":string(),"metadata":{"type":"object"}},["source_id","title","publisher","canonical_url","source_type","source_rank","jurisdiction","update_cadence","connector_id","connector_version","parser_id","parser_version","expected_content_types","retention_policy_id","reviewed_by","reviewed_at"])
RETENTION_POLICY=obj({"policy_id":string(),"name":string(),"applies_to":array(string(OBJECT_KINDS)),"minimum_days":nullable({"type":"integer","minimum":0}),"expiry_action":string(RETENTION_ACTIONS),"legal_hold":{"type":"boolean"},"reviewed_by":string(),"reviewed_at":string()},["policy_id","name","applies_to","minimum_days","expiry_action","legal_hold","reviewed_by","reviewed_at"])
RECEIPT=obj({"receipt_id":string(),"source_id":string(),"acquired_at":string(),"object":OBJECT_REF,"normalized_sha256":string(),"connector_id":string(),"connector_version":string(),"parser_id":string(),"parser_version":string(),"registry_revision":string(),"changed":{"type":"boolean"},"material_changed":{"type":"boolean"},"receipt_hash":string(),"previous_receipt_id":nullable(string()),"previous_receipt_hash":nullable(string()),"resolved_url":nullable(string()),"metadata":{"type":"object"},"schema_version":{"const":RECEIPT_SCHEMA_VERSION}},["receipt_id","source_id","acquired_at","object","normalized_sha256","connector_id","connector_version","parser_id","parser_version","registry_revision","changed","material_changed","receipt_hash"])
MANIFEST=obj({"manifest_id":string(),"operation":string(TRANSFORM_OPERATIONS),"created_at":string(),"tool_id":string(),"tool_version":string(),"input_receipt_ids":array(string()),"input_object_hashes":array(string()),"outputs":array(OBJECT_REF),"parameters":{"type":"object"},"manifest_hash":string(),"case_id":nullable(string()),"human_approved_by":nullable(string()),"schema_version":{"const":MANIFEST_SCHEMA_VERSION}},["manifest_id","operation","created_at","tool_id","tool_version","input_receipt_ids","input_object_hashes","outputs","parameters","manifest_hash"])


def document()->dict:
    return {"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"https://mikelninh.github.io/digital-democracy-studio/safetrace/evidence_vault/schemas/evidence-vault-contracts-1.3.json","title":"SafeTrace Evidence Vault Contracts v1.3","$defs":{"ObjectRef":OBJECT_REF,"RegistryEntry":REGISTRY_ENTRY,"RetentionPolicy":RETENTION_POLICY,"VaultReceipt":RECEIPT,"TransformationManifest":MANIFEST},"type":"object","additionalProperties":False,"properties":{"schema_version":{"const":SCHEMA_VERSION},"registry":{"type":"object","properties":{"schema_version":{"const":REGISTRY_SCHEMA_VERSION},"policies":array({"$ref":"#/$defs/RetentionPolicy"}),"sources":array({"$ref":"#/$defs/RegistryEntry"})},"required":["schema_version","policies","sources"]},"receipt":{"$ref":"#/$defs/VaultReceipt"},"manifest":{"$ref":"#/$defs/TransformationManifest"}},"required":["schema_version"]}

def serialised()->str:return json.dumps(document(),ensure_ascii=False,separators=(",",":"),sort_keys=True)+"\n"

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--write",type=Path);p.add_argument("--check",type=Path);a=p.parse_args(); expected=document()
    if a.write:a.write.parent.mkdir(parents=True,exist_ok=True);a.write.write_text(serialised(),encoding="utf-8")
    if a.check:
        if json.loads(a.check.read_text())!=expected:raise SystemExit("Committed Evidence Vault contracts differ from generated contracts")
    if not a.write and not a.check:print(json.dumps(expected,ensure_ascii=False,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
