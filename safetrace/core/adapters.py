from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable
from .model import AgentTask, Claim, Correction, Entity, Event, Evidence, Publication, Relationship, Review, Snapshot, Source
from .vocabularies import LEGACY_EVIDENCE_STATE_MAP, LEGACY_NODE_TYPE_MAP

def _get(v:Any,k:str,d:Any=None)->Any: return v.get(k,d) if isinstance(v,dict) else getattr(v,k,d)
def _tuple(v:Any)->tuple:
    if v is None:return ()
    return v if isinstance(v,tuple) else tuple(v) if isinstance(v,(list,set,frozenset)) else (v,)
def _now(v:str|None=None)->str:return v or datetime.now(timezone.utc).isoformat()
def _slug(v:str)->str:return re.sub(r"[^a-z0-9]+","-",v.lower()).strip("-") or "unknown"
def _rank(t:str,p:str="")->str:
    v=f"{t} {p}".lower()
    if any(x in v for x in ("official","government","parliament","court","register","ministry","greco","oecd")):return "primary_official"
    if any(x in v for x in ("firsthand","statement","interview")):return "primary_firsthand"
    return "authoritative_secondary"
def _state(v:str|None)->str:return LEGACY_EVIDENCE_STATE_MAP.get(v or "verified_fact","unresolved_gap")
def _source(item:Any, jurisdiction:str, fallback_id:str|None=None, checked_at:str|None=None)->Source:
    sid=_get(item,"id",_get(item,"source_id",fallback_id)); url=_get(item,"url",_get(item,"source_url",_get(item,"canonical_url")))
    if not sid or not url:raise ValueError("Legacy source requires id and URL")
    title=_get(item,"title",_get(item,"source_title",sid)); pub=_get(item,"publisher","Unknown publisher"); typ=_get(item,"source_type","official_record")
    return Source(str(sid),str(title),str(pub),str(url),str(typ),_rank(str(typ),str(pub)),jurisdiction,_get(item,"checked_at",_get(item,"retrieved_or_checked_at",checked_at)))

@dataclass
class AdaptedRecords:
    sources:list[Source]=field(default_factory=list); snapshots:list[Snapshot]=field(default_factory=list); entities:list[Entity]=field(default_factory=list); relationships:list[Relationship]=field(default_factory=list); events:list[Event]=field(default_factory=list); claims:list[Claim]=field(default_factory=list); evidence:list[Evidence]=field(default_factory=list); reviews:list[Review]=field(default_factory=list); publications:list[Publication]=field(default_factory=list); corrections:list[Correction]=field(default_factory=list); agent_tasks:list[AgentTask]=field(default_factory=list)
    def merge(self,other:"AdaptedRecords"):
        for n in self.__dataclass_fields__:
            cur=getattr(self,n); known={x.id for x in cur}; cur.extend(x for x in getattr(other,n) if x.id not in known)
        return self

def adapt_source_engine(*,case_id:str,jurisdiction:str,source_definition:Any|None=None,snapshot_receipt:Any|None=None)->AdaptedRecords:
    if source_definition is None and snapshot_receipt is None:raise ValueError("Source definition or snapshot receipt is required")
    s=_source(source_definition or snapshot_receipt,jurisdiction,_get(snapshot_receipt,"source_id"),_get(snapshot_receipt,"retrieved_at"))
    if snapshot_receipt is None:return AdaptedRecords(sources=[s])
    s=Source(**{**s.__dict__,"canonical_url":_get(snapshot_receipt,"canonical_url",s.canonical_url),"checked_at":_get(snapshot_receipt,"retrieved_at",s.checked_at)})
    digest=str(_get(snapshot_receipt,"sha256"))
    snap=Snapshot(f"snapshot:{s.id}:{digest[:12]}",s.id,str(_get(snapshot_receipt,"retrieved_at")),str(_get(snapshot_receipt,"content_type")),int(_get(snapshot_receipt,"byte_length",0)),digest,str(_get(snapshot_receipt,"normalized_sha256")),str(_get(snapshot_receipt,"parser_version")),str(_get(snapshot_receipt,"raw_path")),None,bool(_get(snapshot_receipt,"changed",False)))
    return AdaptedRecords(sources=[s],snapshots=[snap])

def adapt_political_money_graph(graph:Any,*,case_id:str,jurisdiction:str="Germany")->AdaptedRecords:
    r=AdaptedRecords(); sources={}; evidence={}
    def provenance(items:Iterable[Any],rid:str)->tuple[str,...]:
        ids=[]
        for i,p in enumerate(items):
            s=_source(p,jurisdiction); sources[s.id]=s; eid=f"evidence:{rid}:{i}"; evidence[eid]=Evidence(eid,case_id,s.id,"supporting",f"Legacy Political Money provenance for {rid}.",_now(_get(p,"retrieved_or_checked_at")),_get(p,"source_anchor") or "record-level provenance",metadata={"legacy_evidence_state":_get(p,"evidence_state")}); ids.append(eid)
        return tuple(ids)
    for n in _get(graph,"nodes",[]):
        ids=provenance(_get(n,"provenance",()),f"entity:{_get(n,'id')}")
        r.entities.append(Entity(str(_get(n,"id")),case_id,LEGACY_NODE_TYPE_MAP.get(str(_get(n,"type")),"other"),str(_get(n,"label")),attributes=dict(_get(n,"attributes",{})),source_ids=tuple(evidence[x].source_id for x in ids)))
    for e in _get(graph,"edges",[]):
        ids=provenance(_get(e,"provenance",()),f"relationship:{_get(e,'id')}")
        r.relationships.append(Relationship(str(_get(e,"id")),case_id,str(_get(e,"type")),str(_get(e,"source")),str(_get(e,"target")),ids,"confirmed",str(_get(e,"interpretation","documented_relationship_only")),attributes=dict(_get(e,"attributes",{}))))
    r.sources=list(sources.values()); r.evidence=list(evidence.values()); return r

def adapt_review_claim(c:Any,*,case_id:str,jurisdiction:str="Germany")->AdaptedRecords:
    r=AdaptedRecords(); sources={}; eids=[]
    for x in _get(c,"evidence",[]):
        s=_source(x,jurisdiction); sources[s.id]=s; eid=str(_get(x,"id")); r.evidence.append(Evidence(eid,case_id,s.id,str(_get(x,"role")),str(_get(x,"summary")),_now(),_get(x,"source_anchor") or "legacy evidence reference")); eids.append(eid)
    d=_get(c,"decision"); reviews=[]
    if d is not None:
        rid=f"review:{_get(c,'id')}"; r.reviews.append(Review(rid,case_id,"claim",str(_get(c,"id")),str(_get(d,"outcome")),f"legacy:{_slug(str(_get(d,'reviewer_role')))}",str(_get(d,"reviewer_role")),str(_get(d,"rationale")),str(_get(d,"decided_at")),str(_get(d,"legal_review","not_required")),str(_get(d,"right_of_reply","not_required")),bool(_get(d,"contradictory_evidence_addressed",False)))); reviews.append(rid)
    corrections=[]
    for i,x in enumerate(_get(c,"correction_history",[])):
        cid=str(x.get("id",f"correction:{_get(c,'id')}:{i}")); r.corrections.append(Correction(cid,case_id,"claim",str(_get(c,"id")),str(x.get("description",x.get("change","Legacy correction recorded."))),str(x.get("reason","Migrated from visible legacy correction history.")),str(x.get("corrected_at",x.get("timestamp",_now()))),tuple(x.get("source_ids",[])),True)); corrections.append(cid)
    approved=d is not None and _get(d,"outcome")=="approved"
    r.claims.append(Claim(str(_get(c,"id")),case_id,str(_get(c,"text")),_state(_get(c,"evidence_state")),"internal" if _get(c,"sensitivity")=="sensitive" else "public",str(_get(c,"origin")),approved,tuple(eids),_now(),tuple(reviews),tuple(corrections)))
    r.sources=list(sources.values()); return r

def adapt_arms_case(c:Any,*,case_id:str|None=None)->AdaptedRecords:
    r=AdaptedRecords(); cid=case_id or str(_get(c,"id")); jurisdiction=str(_get(c,"jurisdiction","Germany")); sources={}; entities={}
    def entity(label):
        if not label:return None
        eid=f"entity:{_slug(label)}"; entities.setdefault(eid,Entity(eid,cid,"organisation",label)); return eid
    for x in _get(c,"events",[]):
        sr=_get(x,"source"); s=_source(sr,jurisdiction); sources[s.id]=s; evid=f"evidence:{_get(x,'id')}"; r.evidence.append(Evidence(evid,cid,s.id,"supporting",f"Source record supporting {_get(x,'title')}.",_now(_get(sr,"checked_at")),_get(sr,"anchor") or "record-level source"))
        a=entity(_get(x,"actor")); t=entity(_get(x,"recipient_or_beneficiary")); attrs=dict(_get(x,"attributes",{}));
        if _get(x,"amount_eur") is not None:attrs["amount_eur"]=str(_get(x,"amount_eur"))
        attrs.setdefault("status",_get(x,"status","recorded"))
        r.events.append(Event(str(_get(x,"id")),cid,str(_get(x,"type")),str(_get(x,"date")),str(_get(x,"title")),_state(_get(x,"evidence_state")),(evid,),(a,) if a else (),(t,) if t else (),attributes=attrs))
    for i,q in enumerate(_get(c,"unresolved_questions",[])):
        sid=next(iter(sources),None)
        if not sid:continue
        evid=f"evidence:unresolved:{i}"; r.evidence.append(Evidence(evid,cid,sid,"context",str(q.get("safe_interpretation")),_now(),"legacy unresolved-question record")); r.claims.append(Claim(str(q.get("id",f"claim:unresolved:{i}")),cid,str(q.get("question",q.get("safe_interpretation"))),_state(q.get("evidence_state")),"public","human",False,(evid,),_now(),limitations=(str(q.get("safe_interpretation")),)))
    r.sources=list(sources.values()); r.entities=list(entities.values()); return r

def adapt_monitoring_proposal(p:Any,*,case_id:str)->AdaptedRecords:
    status={"pending_review":"awaiting_human","approved":"accepted","rejected":"rejected","not_required":"proposal_ready"}.get(str(_get(p,"review_state")),"proposal_ready")
    task=AgentTask(f"agent-task:{_get(p,'id')}",case_id,str(_get(p,"summary")),"watchtower",status,(str(_get(p,"source_id")),),("read_official_source","compare_snapshot","propose_claim_update"),"public","safetrace.change-proposal/0.7","deterministic_monitoring_adapter","legacy-v0.7",str(_get(p,"reviewer_role") or "assigned_editorial_reviewer"),str(_get(p,"created_at")),_get(p,"reviewed_at") if status in {"accepted","rejected"} else None,str(_get(p,"id")),{"legacy_kind":_get(p,"kind"),"affected_claims":list(_get(p,"affected_claims",[])),"public_effect":_get(p,"public_effect")})
    return AdaptedRecords(agent_tasks=[task])

def bundle_from_case_pack(pack):
    from .bundles import bundle_from_case_pack as f; return f(pack)
def bundle_from_political_money_graph(graph):
    from .bundles import bundle_from_political_money_graph as f; return f(graph)
def bundle_from_arms_case(case):
    from .bundles import bundle_from_arms_case as f; return f(case)
def bundle_from_law_fairness(payload):
    from .bundles import bundle_from_law_fairness as f; return f(payload)
def bundle_summary(bundle):
    from .bundles import bundle_summary as f; return f(bundle)
