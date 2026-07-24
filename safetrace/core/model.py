from __future__ import annotations

import dataclasses, re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Iterable

from .vocabularies import *

_SHA = re.compile(r"^[0-9a-f]{64}$")

def text(v: str, name: str, n: int = 1) -> None:
    if not isinstance(v, str) or len(v.strip()) < n: raise ValueError(f"{name} is required")
def enum(v: str, values: Iterable[str], name: str) -> None:
    if v not in values: raise ValueError(f"Unsupported {name}: {v}")
def iso(v: str | None, name: str, required: bool = True) -> None:
    if v is None:
        if required: raise ValueError(f"{name} is required")
        return
    try: datetime.fromisoformat(v.replace("Z", "+00:00"))
    except (TypeError, ValueError) as e: raise ValueError(f"{name} must be ISO-8601") from e
def day(v: str, name: str) -> None:
    if not re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", v): raise ValueError(f"{name} must be YYYY, YYYY-MM or YYYY-MM-DD")
    p=v.split("-")
    if len(p)>1 and not 1<=int(p[1])<=12: raise ValueError(f"{name} contains an invalid month")
    if len(p)==3:
        try: date.fromisoformat(v)
        except ValueError as e: raise ValueError(f"{name} must be a valid date") from e
def sha(v: str, name: str) -> None:
    if not isinstance(v,str) or not _SHA.fullmatch(v.lower()): raise ValueError(f"{name} must be a SHA-256 hex digest")
def plain(v: Any) -> Any:
    if dataclasses.is_dataclass(v): return {f.name: plain(getattr(v,f.name)) for f in dataclasses.fields(v)}
    if isinstance(v,dict): return {str(k):plain(x) for k,x in v.items()}
    if isinstance(v,(tuple,list,set,frozenset)): return [plain(x) for x in v]
    return v
def indexed(items, name):
    out={}
    for x in items:
        if x.id in out: raise ValueError(f"Duplicate {name} id: {x.id}")
        out[x.id]=x
    return out

@dataclass(frozen=True)
class Risk:
    id:str; category:str; description:str; likelihood:str; severity:str; mitigation:str; owner:str
    def validate(self):
        text(self.id,"Risk id"); enum(self.category,RISK_CATEGORIES,"risk category"); enum(self.likelihood,RISK_LEVELS,"risk likelihood"); enum(self.severity,RISK_LEVELS,"risk severity"); text(self.description,"Risk description",10); text(self.mitigation,"Risk mitigation",10); text(self.owner,"Risk owner")

@dataclass(frozen=True)
class CaseCharter:
    id:str; case_id:str; title:str; research_question:str; public_interest_rationale:str; jurisdiction:str; case_owner:str; editorial_owner:str; created_at:str
    status:str="draft"; scope_inclusions:tuple[str,...]=(); scope_exclusions:tuple[str,...]=(); expected_source_types:tuple[str,...]=(); affected_groups:tuple[str,...]=(); risks:tuple[Risk,...]=(); prohibited_methods:tuple[str,...]=field(default_factory=lambda:tuple(sorted(BASELINE_PROHIBITED_METHODS))); permitted_data_zones:tuple[str,...]=("public",); publication_boundary:str="Public official records only; no automated accusation, publication or referral."; legal_review_required:bool=False; constitution_ref:str=CONSTITUTION_REF; constitution_version:str=CONSTITUTION_VERSION
    def validate(self):
        for v,n,m in [(self.id,"Charter id",1),(self.case_id,"Case id",1),(self.title,"Case title",5),(self.research_question,"Research question",20),(self.public_interest_rationale,"Public-interest rationale",30),(self.jurisdiction,"Jurisdiction",1),(self.case_owner,"Case owner",1),(self.editorial_owner,"Editorial owner",1),(self.publication_boundary,"Publication boundary",20)]: text(v,n,m)
        if not self.research_question.strip().endswith("?"): raise ValueError("Research question must be framed as a question")
        iso(self.created_at,"Charter created_at"); enum(self.status,CHARTER_STATUSES,"charter status")
        if not self.scope_inclusions: raise ValueError("At least one scoped inclusion is required")
        if not self.scope_exclusions: raise ValueError("At least one scoped exclusion is required")
        if not self.expected_source_types: raise ValueError("Expected source types are required")
        if not self.affected_groups: raise ValueError("Affected groups are required")
        for r in self.risks: r.validate()
        missing=BASELINE_PROHIBITED_METHODS-set(self.prohibited_methods)
        if missing: raise ValueError(f"Charter omits baseline prohibited methods: {sorted(missing)}")
        if not self.permitted_data_zones: raise ValueError("At least one permitted data zone is required")
        for z in self.permitted_data_zones: enum(z,DATA_ZONES,"data zone")
        if self.constitution_ref!=CONSTITUTION_REF: raise ValueError("Case Charter must reference the SafeTrace Constitution")
        if self.constitution_version!=CONSTITUTION_VERSION: raise ValueError("Unsupported Constitution version")

@dataclass(frozen=True)
class Case:
    id:str; charter_id:str; title:str; jurisdiction:str; status:str; created_at:str; updated_at:str; summary:str; publication_boundary:str; tags:tuple[str,...]=()
    def validate(self):
        text(self.id,"Case id"); text(self.charter_id,"Charter id"); text(self.title,"Case title"); text(self.jurisdiction,"Jurisdiction"); enum(self.status,CASE_STATUSES,"case status"); iso(self.created_at,"Case created_at"); iso(self.updated_at,"Case updated_at"); text(self.summary,"Case summary",20); text(self.publication_boundary,"Publication boundary",20)

@dataclass(frozen=True)
class Source:
    id:str; title:str; publisher:str; canonical_url:str; source_type:str; source_rank:str; jurisdiction:str; checked_at:str|None=None; access_status:str="available"; sensitivity:str="public"; metadata:dict[str,Any]=field(default_factory=dict)
    def validate(self):
        text(self.id,"Source id"); text(self.title,"Source title"); text(self.publisher,"Source publisher")
        if not self.canonical_url.startswith("https://"): raise ValueError("Source canonical_url must use HTTPS")
        text(self.source_type,"Source type"); enum(self.source_rank,SOURCE_RANKS,"source rank"); text(self.jurisdiction,"Source jurisdiction"); iso(self.checked_at,"Source checked_at",False); enum(self.access_status,SOURCE_ACCESS_STATES,"source access status"); enum(self.sensitivity,FIELD_SENSITIVITIES,"source sensitivity")

@dataclass(frozen=True)
class Snapshot:
    id:str; source_id:str; retrieved_at:str; content_type:str; byte_length:int; sha256:str; normalized_sha256:str; parser_version:str; storage_uri:str; previous_snapshot_id:str|None=None; changed:bool=False; sensitivity:str="public"
    def validate(self):
        text(self.id,"Snapshot id"); text(self.source_id,"Snapshot source_id"); iso(self.retrieved_at,"Snapshot retrieved_at"); text(self.content_type,"Snapshot content_type")
        if not isinstance(self.byte_length,int) or self.byte_length<0: raise ValueError("Snapshot byte_length must be a non-negative integer")
        sha(self.sha256,"Snapshot sha256"); sha(self.normalized_sha256,"Snapshot normalized_sha256"); text(self.parser_version,"Snapshot parser_version"); text(self.storage_uri,"Snapshot storage_uri"); enum(self.sensitivity,FIELD_SENSITIVITIES,"snapshot sensitivity")

@dataclass(frozen=True)
class Entity:
    id:str; case_id:str; entity_type:str; label:str; identifiers:dict[str,str]=field(default_factory=dict); attributes:dict[str,Any]=field(default_factory=dict); source_ids:tuple[str,...]=(); sensitivity:str="public"
    def validate(self):
        text(self.id,"Entity id"); text(self.case_id,"Entity case_id"); enum(self.entity_type,ENTITY_TYPES,"entity type"); text(self.label,"Entity label"); enum(self.sensitivity,FIELD_SENSITIVITIES,"entity sensitivity")

@dataclass(frozen=True)
class Evidence:
    id:str; case_id:str; source_id:str; role:str; summary:str; created_at:str; source_anchor:str|None=None; snapshot_id:str|None=None; quote:str|None=None; sensitivity:str="public"; metadata:dict[str,Any]=field(default_factory=dict)
    def validate(self):
        text(self.id,"Evidence id"); text(self.case_id,"Evidence case_id"); text(self.source_id,"Evidence source_id"); enum(self.role,EVIDENCE_ROLES,"evidence role"); text(self.summary,"Evidence summary",10); iso(self.created_at,"Evidence created_at"); enum(self.sensitivity,FIELD_SENSITIVITIES,"evidence sensitivity")

@dataclass(frozen=True)
class Relationship:
    id:str; case_id:str; relationship_type:str; source_entity_id:str; target_entity_id:str; evidence_ids:tuple[str,...]; confidence:str; interpretation:str="documented_relationship_only"; valid_from:str|None=None; valid_to:str|None=None; sensitivity:str="public"; attributes:dict[str,Any]=field(default_factory=dict)
    def validate(self):
        text(self.id,"Relationship id"); text(self.case_id,"Relationship case_id"); enum(self.relationship_type,RELATIONSHIP_TYPES,"relationship type"); text(self.source_entity_id,"Relationship source entity"); text(self.target_entity_id,"Relationship target entity")
        if not self.evidence_ids: raise ValueError("Every relationship requires evidence")
        enum(self.confidence,RELATIONSHIP_CONFIDENCE,"relationship confidence"); text(self.interpretation,"Relationship interpretation"); enum(self.sensitivity,FIELD_SENSITIVITIES,"relationship sensitivity")

@dataclass(frozen=True)
class Event:
    id:str; case_id:str; event_type:str; date:str; title:str; evidence_state:str; evidence_ids:tuple[str,...]; actor_entity_ids:tuple[str,...]=(); target_entity_ids:tuple[str,...]=(); legal_status:str="not_applicable"; sensitivity:str="public"; attributes:dict[str,Any]=field(default_factory=dict)
    def validate(self):
        text(self.id,"Event id"); text(self.case_id,"Event case_id"); enum(self.event_type,EVENT_TYPES,"event type"); day(self.date,"Event date"); text(self.title,"Event title"); enum(self.evidence_state,EVIDENCE_STATES,"event evidence state")
        if not self.evidence_ids: raise ValueError("Every event requires evidence")
        enum(self.legal_status,LEGAL_STATUSES,"event legal status"); enum(self.sensitivity,FIELD_SENSITIVITIES,"event sensitivity")
        if self.event_type=="planned_delivery" and self.attributes.get("status") not in {None,"planned"}: raise ValueError("A planned delivery must remain labelled planned")
        if self.event_type=="export_authorisation" and self.attributes.get("delivered") is True: raise ValueError("An export authorisation cannot itself prove delivery")

@dataclass(frozen=True)
class Claim:
    id:str; case_id:str; text:str; evidence_state:str; sensitivity:str; origin:str; material:bool; evidence_ids:tuple[str,...]; created_at:str; review_ids:tuple[str,...]=(); correction_ids:tuple[str,...]=(); legal_status:str="not_applicable"; updated_at:str|None=None; limitations:tuple[str,...]=(); metadata:dict[str,Any]=field(default_factory=dict)
    def validate(self):
        text(self.id,"Claim id"); text(self.case_id,"Claim case_id"); text(self.text,"Claim text",10); enum(self.evidence_state,EVIDENCE_STATES,"claim evidence state"); enum(self.sensitivity,FIELD_SENSITIVITIES,"claim sensitivity"); enum(self.origin,EVIDENCE_ORIGINS,"claim origin"); iso(self.created_at,"Claim created_at"); iso(self.updated_at,"Claim updated_at",False); enum(self.legal_status,LEGAL_STATUSES,"claim legal status")

@dataclass(frozen=True)
class Review:
    id:str; case_id:str; subject_type:str; subject_id:str; outcome:str; reviewer_id:str; reviewer_role:str; rationale:str; decided_at:str; legal_review:str="not_required"; right_of_reply:str="not_required"; contradictory_evidence_addressed:bool=False
    def validate(self):
        text(self.id,"Review id"); text(self.case_id,"Review case_id"); enum(self.subject_type,SUBJECT_TYPES,"review subject type"); text(self.subject_id,"Review subject id"); enum(self.outcome,REVIEW_OUTCOMES,"review outcome"); text(self.reviewer_id,"Reviewer id"); text(self.reviewer_role,"Reviewer role"); text(self.rationale,"Review rationale",10); iso(self.decided_at,"Review decided_at"); enum(self.legal_review,LEGAL_REVIEW_STATES,"legal review state"); enum(self.right_of_reply,RIGHT_OF_REPLY_STATES,"right-of-reply state")

@dataclass(frozen=True)
class Publication:
    id:str; case_id:str; edition:str; status:str; claim_ids:tuple[str,...]; review_ids:tuple[str,...]; boundary:str; created_at:str; published_at:str|None=None; correction_ids:tuple[str,...]=()
    def validate(self):
        text(self.id,"Publication id"); text(self.case_id,"Publication case_id"); enum(self.edition,PUBLICATION_EDITIONS,"publication edition"); enum(self.status,PUBLICATION_STATUSES,"publication status"); text(self.boundary,"Publication boundary",20); iso(self.created_at,"Publication created_at"); iso(self.published_at,"Publication published_at",False)
        if self.status=="published" and self.published_at is None: raise ValueError("Published publication requires published_at")

@dataclass(frozen=True)
class Correction:
    id:str; case_id:str; subject_type:str; subject_id:str; description:str; reason:str; corrected_at:str; source_ids:tuple[str,...]=(); visible:bool=True
    def validate(self):
        text(self.id,"Correction id"); text(self.case_id,"Correction case_id"); enum(self.subject_type,SUBJECT_TYPES,"correction subject type"); text(self.subject_id,"Correction subject id"); text(self.description,"Correction description",10); text(self.reason,"Correction reason",5); iso(self.corrected_at,"Correction corrected_at")
        if not self.visible: raise ValueError("Corrections must remain visible")

@dataclass(frozen=True)
class AgentTask:
    id:str; case_id:str; purpose:str; agent_type:str; status:str; input_refs:tuple[str,...]; allowed_tools:tuple[str,...]; max_data_zone:str; output_schema:str; model:str; prompt_version:str; human_approver:str; created_at:str; completed_at:str|None=None; output_ref:str|None=None; metadata:dict[str,Any]=field(default_factory=dict)
    def validate(self):
        text(self.id,"Agent task id"); text(self.case_id,"Agent task case_id"); text(self.purpose,"Agent task purpose",10); enum(self.agent_type,AGENT_TYPES,"agent type"); enum(self.status,AGENT_TASK_STATUSES,"agent task status"); enum(self.max_data_zone,DATA_ZONES,"agent data zone"); text(self.output_schema,"Agent output schema"); text(self.model,"Agent model"); text(self.prompt_version,"Agent prompt version"); text(self.human_approver,"Agent human approver"); iso(self.created_at,"Agent task created_at"); iso(self.completed_at,"Agent task completed_at",False)
        bad=set(self.allowed_tools)&FORBIDDEN_AGENT_TOOLS
        if bad: raise ValueError(f"Agent task requests prohibited tools: {sorted(bad)}")

@dataclass
class InvestigationBundle:
    case:Case; charter:CaseCharter; sources:list[Source]=field(default_factory=list); snapshots:list[Snapshot]=field(default_factory=list); entities:list[Entity]=field(default_factory=list); relationships:list[Relationship]=field(default_factory=list); events:list[Event]=field(default_factory=list); claims:list[Claim]=field(default_factory=list); evidence:list[Evidence]=field(default_factory=list); reviews:list[Review]=field(default_factory=list); publications:list[Publication]=field(default_factory=list); corrections:list[Correction]=field(default_factory=list); agent_tasks:list[AgentTask]=field(default_factory=list); schema_version:str=SCHEMA_VERSION
    def validate(self):
        if self.schema_version!=SCHEMA_VERSION: raise ValueError(f"Unsupported schema version: {self.schema_version}")
        self.charter.validate(); self.case.validate()
        if self.charter.case_id!=self.case.id or self.case.charter_id!=self.charter.id: raise ValueError("Case and Charter are not linked")
        groups={n:indexed(getattr(self,n),n) for n in ("sources","snapshots","entities","relationships","events","claims","evidence","reviews","publications","corrections","agent_tasks")}
        for n in groups:
            for x in getattr(self,n): x.validate()
        for n in ("entities","relationships","events","claims","evidence","reviews","publications","corrections","agent_tasks"):
            for x in getattr(self,n):
                if x.case_id!=self.case.id: raise ValueError(f"Cross-case record detected: {x.id}")
        src,snap,ent,rel,evt,clm,evi,rev,pub,cor,task=(groups[n] for n in ("sources","snapshots","entities","relationships","events","claims","evidence","reviews","publications","corrections","agent_tasks"))
        for x in self.snapshots:
            if x.source_id not in src: raise ValueError(f"Snapshot references unknown source: {x.id}")
            if x.previous_snapshot_id and x.previous_snapshot_id not in snap: raise ValueError(f"Snapshot references unknown previous snapshot: {x.id}")
        for x in self.evidence:
            if x.source_id not in src: raise ValueError(f"Evidence references unknown source: {x.id}")
            if x.snapshot_id and x.snapshot_id not in snap: raise ValueError(f"Evidence references unknown snapshot: {x.id}")
        for x in self.entities:
            u=set(x.source_ids)-set(src)
            if u: raise ValueError(f"Entity {x.id} references unknown sources: {sorted(u)}")
        for x in self.relationships:
            if x.source_entity_id not in ent or x.target_entity_id not in ent: raise ValueError(f"Relationship has unknown endpoint: {x.id}")
            u=set(x.evidence_ids)-set(evi)
            if u: raise ValueError(f"Relationship {x.id} has unknown evidence: {sorted(u)}")
        for x in self.events:
            u=set(x.evidence_ids)-set(evi)
            if u: raise ValueError(f"Event {x.id} has unknown evidence: {sorted(u)}")
            u=(set(x.actor_entity_ids)|set(x.target_entity_ids))-set(ent)
            if u: raise ValueError(f"Event {x.id} has unknown entities: {sorted(u)}")
        for x in self.claims:
            if set(x.evidence_ids)-set(evi): raise ValueError(f"Claim {x.id} has unknown evidence")
            if set(x.review_ids)-set(rev): raise ValueError(f"Claim {x.id} has unknown reviews")
            if set(x.correction_ids)-set(cor): raise ValueError(f"Claim {x.id} has unknown corrections")
            if x.material:
                supporting=[evi[i] for i in x.evidence_ids if evi[i].role=="supporting"]
                if not supporting: raise ValueError(f"Material claim lacks supporting evidence: {x.id}")
                if any(not y.source_anchor for y in supporting): raise ValueError(f"Material claim supporting evidence lacks source anchor: {x.id}")
        subjects={"case":{self.case.id},"source":set(src),"entity":set(ent),"relationship":set(rel),"event":set(evt),"claim":set(clm),"publication":set(pub)}
        for x in self.reviews:
            if x.subject_id not in subjects[x.subject_type]: raise ValueError(f"Review references unknown subject: {x.id}")
        for x in self.corrections:
            if x.subject_id not in subjects[x.subject_type]: raise ValueError(f"Correction references unknown subject: {x.id}")
            if set(x.source_ids)-set(src): raise ValueError(f"Correction {x.id} references unknown sources")
        for x in self.publications:
            if set(x.claim_ids)-set(clm) or set(x.review_ids)-set(rev) or set(x.correction_ids)-set(cor): raise ValueError(f"Publication {x.id} has unknown references")
            if x.status in {"approved","published"}: self._publication_gate(x,clm,evi,rev)
        ceiling=max(DATA_ZONE_ORDER[z] for z in self.charter.permitted_data_zones)
        for x in self.agent_tasks:
            if DATA_ZONE_ORDER[x.max_data_zone]>ceiling: raise ValueError(f"Agent task exceeds Charter data-zone ceiling: {x.id}")
    def _publication_gate(self,p,claims,evidence,reviews):
        for cid in p.claim_ids:
            c=claims[cid]; approvals=[reviews[r] for r in c.review_ids if reviews[r].outcome=="approved"]
            if not approvals: raise ValueError(f"Publication includes claim without human approval: {c.id}")
            contradictions=[evidence[i] for i in c.evidence_ids if evidence[i].role=="contradicting"]
            if contradictions and not any(r.contradictory_evidence_addressed for r in approvals): raise ValueError(f"Publication ignores contradicting evidence: {c.id}")
            if c.sensitivity!="public":
                if not any(r.legal_review=="approved" for r in approvals): raise ValueError(f"Sensitive claim requires legal approval: {c.id}")
                if not any(r.right_of_reply in {"completed","declined"} for r in approvals): raise ValueError(f"Sensitive claim requires right-of-reply handling: {c.id}")
    def to_dict(self): self.validate(); return plain(self)
    @classmethod
    def from_dict(cls,p):
        tup=lambda x:tuple(x or [])
        cd=dict(p["charter"]); [cd.__setitem__(k,tup(cd.get(k))) for k in ("scope_inclusions","scope_exclusions","expected_source_types","affected_groups","prohibited_methods","permitted_data_zones")]; cd["risks"]=tuple(Risk(**x) for x in cd.get("risks",[]))
        ca=dict(p["case"]); ca["tags"]=tup(ca.get("tags"))
        def many(C,n,fields=()):
            out=[]
            for raw in p.get(n,[]):
                d=dict(raw)
                for f in fields:d[f]=tup(d.get(f))
                out.append(C(**d))
            return out
        b=cls(case=Case(**ca),charter=CaseCharter(**cd),sources=many(Source,"sources"),snapshots=many(Snapshot,"snapshots"),entities=many(Entity,"entities",("source_ids",)),relationships=many(Relationship,"relationships",("evidence_ids",)),events=many(Event,"events",("evidence_ids","actor_entity_ids","target_entity_ids")),claims=many(Claim,"claims",("evidence_ids","review_ids","correction_ids","limitations")),evidence=many(Evidence,"evidence"),reviews=many(Review,"reviews"),publications=many(Publication,"publications",("claim_ids","review_ids","correction_ids")),corrections=many(Correction,"corrections",("source_ids",)),agent_tasks=many(AgentTask,"agent_tasks",("input_refs","allowed_tools")),schema_version=p.get("schema_version",SCHEMA_VERSION)); b.validate(); return b
