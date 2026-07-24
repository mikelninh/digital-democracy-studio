from __future__ import annotations
from typing import Any
from .adapters import AdaptedRecords, _get, _now, _source, _state, _tuple, adapt_arms_case, adapt_political_money_graph
from .model import Case, CaseCharter, Claim, Event, Evidence, InvestigationBundle, Publication, Review, Risk
from .vocabularies import BASELINE_PROHIBITED_METHODS, SCHEMA_VERSION

def charter(case_id,title,jurisdiction,question,purpose,created_at):
    if not question.endswith("?"): question=question.rstrip(".")+"?"
    return CaseCharter(f"charter:{case_id}",case_id,title,question,purpose if len(purpose)>=30 else purpose+" This bounded public-interest case remains subject to human review.",jurisdiction,"migrated_case_owner","migrated_editorial_owner",created_at,"accepted",("Reviewed legacy case records and their documented scope",),("Private-person investigation and unsupported criminal allegations",),("primary official records","reviewed legacy SafeTrace outputs"),("citizens","organisations materially discussed"),(Risk(f"risk:{case_id}:misinterpretation","misinterpretation","Documented association or sequence may be mistaken for proof of unlawful conduct.","medium","high","Preserve evidence states, limitations and publication boundaries during migration.","migrated_editorial_owner"),),tuple(sorted(BASELINE_PROHIBITED_METHODS)),("public",),"Public official records only; no automated accusation, publication, contact or referral.")
def make_case(ch,title,jurisdiction,created,boundary,tags=()): return Case(ch.case_id,ch.id,title,jurisdiction,"active",created,created,ch.public_interest_rationale,boundary,tags)

def bundle_from_case_pack(pack:dict[str,Any])->InvestigationBundle:
    raw=pack["case"]; cid=str(raw["id"]); created=str(pack.get("generated_at",_now())); ch=charter(cid,str(raw["title"]),str(raw.get("jurisdiction","Germany")),f"What do the reviewed public records establish about {raw['title']}?",str(raw.get("purpose","Make a bounded public accountability question reproducible from reviewed evidence.")),created); case=make_case(ch,ch.title,ch.jurisdiction,created,ch.publication_boundary,("legacy-case-pack",)); r=AdaptedRecords()
    for x in pack.get("source_manifest",[]):
        try:r.sources.append(_source(x,case.jurisdiction,checked_at=created))
        except ValueError:pass
    ids=[x.id for x in r.sources]
    if not ids:raise ValueError("Case pack migration requires at least one source")
    preferred=next((x for x in ids if "compliance" in x),ids[0])
    for i,x in enumerate(pack.get("chronology",[])):
        sid=str(x.get("source_id",preferred)); sid=sid if sid in ids else preferred; eid=f"evidence:chronology:{i}"; title=str(x.get("event")); r.evidence.append(Evidence(eid,cid,sid,"supporting" if x.get("evidence_state")=="verified_fact" else "context",title,created,str(x.get("source_anchor","chronology record")))); r.events.append(Event(f"event:chronology:{i}",cid,"deadline" if "deadline" in title.lower() else "other",str(x.get("date")),title,_state(x.get("evidence_state")),(eid,)))
    review=pack.get("review",{}); when=str(review.get("reviewed_at") or review.get("decided_at") or created); claims=[]; reviews=[]
    for i,x in enumerate(pack.get("findings",[])):
        claim=str(x.get("id",f"claim:finding:{i}")); sid=str(x.get("source_id",preferred)); sid=sid if sid in ids else preferred; eid=f"evidence:{claim}"; rid=f"review:{claim}"; statement=str(x.get("statement",x.get("title"))); r.evidence.append(Evidence(eid,cid,sid,"supporting",statement,created,str(x.get("source_anchor","finding source anchor")))); r.reviews.append(Review(rid,cid,"claim",claim,"approved","legacy:case-pack-reviewer",str(review.get("reviewer_role","editorial_reviewer")),str(review.get("rationale","Migrated from a validated public-redacted case pack.")),when,contradictory_evidence_addressed=bool(review.get("contradictory_evidence_addressed",True)))); r.claims.append(Claim(claim,cid,statement,_state(x.get("evidence_state")),"public","imported_official_record",True,(eid,),created,(rid,),limitations=_tuple(x.get("limitations")),metadata={"official_status":x.get("official_status")})); claims.append(claim); reviews.append(rid)
    r.publications.append(Publication(f"publication:{pack.get('pack_id',cid)}",cid,str(pack.get("edition","public_redacted")),"published",tuple(claims),tuple(reviews),ch.publication_boundary,created,created)); b=InvestigationBundle(case,ch,**r.__dict__); b.validate(); return b

def bundle_from_political_money_graph(graph)->InvestigationBundle:
    m=dict(_get(graph,"metadata",{})); legacy=str(m.get("case_id","case-002")); cid="case-002" if legacy=="political-money-dvag-2026" else legacy; title=str(m.get("title","Political Money Explorer")); when=str(m.get("reviewed_at") or _now()); boundary=str(m.get("publication_boundary") or "Documented donations, registrations and declared interests only; no unsupported causal or criminal conclusion."); ch=charter(cid,title,"Germany","Which donations, lobby registrations and declared policy interests are documented in official records?","Make officially documented political-finance relationships inspectable without treating association or sequence as proof of unlawful influence.",when); ch=CaseCharter(**{**ch.__dict__,"publication_boundary":boundary}); b=InvestigationBundle(make_case(ch,title,"Germany",when,boundary,("political-money",f"legacy-id:{legacy}")),ch,**adapt_political_money_graph(graph,case_id=cid).__dict__); b.validate(); return b

def bundle_from_arms_case(raw)->InvestigationBundle:
    legacy=str(_get(raw,"id","case-003")); cid="case-003" if legacy=="arms-monitor-germany-baseline" else legacy; title=str(_get(raw,"title","Arms & Influence Monitor")); jurisdiction=str(_get(raw,"jurisdiction","Germany")); boundary=str(_get(raw,"publication_boundary") or "Public official records only; authorisation, contract, delivery and operational use remain separate."); when=_now(); ch=charter(cid,title,jurisdiction,"What formal authority, procurement, export, delivery and oversight events are documented in the public record?","Trace formal arms and defence decisions without turning lawful approvals, contracts, profits or temporal proximity into accusations of corruption or unlawful use.",when); ch=CaseCharter(**{**ch.__dict__,"publication_boundary":boundary}); b=InvestigationBundle(make_case(ch,title,jurisdiction,when,boundary,("arms-accountability",f"legacy-id:{legacy}")),ch,**adapt_arms_case(raw,case_id=cid).__dict__); b.validate(); return b

def bundle_from_law_fairness(p:dict[str,Any])->InvestigationBundle:
    cid=str(p["case_id"]); when=str(p.get("last_reviewed_at") or _now()); ch=charter(cid,str(p["title"]),str(p.get("jurisdiction","Germany")),str(p["question"]),str(p.get("overall_explanation",p.get("publication_boundary",""))),when); case=make_case(ch,ch.title,ch.jurisdiction,when,ch.publication_boundary,("law-fairness","case-004")); r=AdaptedRecords()
    for x in p.get("sources",[]):r.sources.append(_source(x,case.jurisdiction,checked_at=when))
    src={x.id for x in r.sources}; by_measure={}
    for x in p.get("measures",[]):
        mid=str(_get(x,"id")); eids=[]
        for i,sid in enumerate(str(y) for y in _get(x,"source_ids",[]) if str(y) in src):
            eid=f"evidence:{mid}:{i}"; r.evidence.append(Evidence(eid,cid,sid,"supporting",str(_get(x,"description")),when,"measure-level official source")); eids.append(eid)
        by_measure[mid]=eids; status=str(_get(x,"status")); r.events.append(Event(f"event:{mid}",cid,"measure_effective",str(_get(x,"effective_date")),str(_get(x,"title")),_state(_get(x,"evidence_state")),tuple(eids),legal_status=status if status in {"announced","enacted","in_force","expired"} else "not_applicable",attributes={"origin":_get(x,"origin"),"attributable_to_current_government":_get(x,"attributable_to_current_government"),"impacts":[getattr(y,"__dict__",y) for y in _get(x,"impacts",[])],"unresolved_questions":list(_get(x,"unresolved_questions",[]))}))
    claims=[]; reviews=[]
    for x in p.get("claim_tests",[]):
        cid2=str(_get(x,"id")); mids=[str(y) for y in _get(x,"measure_ids",[])]; eids=tuple(y for mid in mids for y in by_measure.get(mid,[])); rid=f"review:{cid2}"; verdict=str(_get(x,"verdict")); r.reviews.append(Review(rid,cid,"claim",cid2,"approved","legacy:law-fairness-reviewer","editorial_reviewer","Migrated from the reviewed Case 004 public assessment with political attribution preserved.",when,contradictory_evidence_addressed=True)); r.claims.append(Claim(cid2,cid,str(_get(x,"claim")),"verified_fact" if verdict in {"supported","not_supported"} else "analytical_red_flag","public","human",True,eids,when,(rid,),limitations=(str(_get(x,"reasoning")),),metadata={"legacy_verdict":verdict,"measure_ids":mids})); claims.append(cid2); reviews.append(rid)
    r.publications.append(Publication(f"publication:{cid}",cid,"public_redacted","published",tuple(claims),tuple(reviews),ch.publication_boundary,when,when)); b=InvestigationBundle(case,ch,**r.__dict__); b.validate(); return b

def bundle_summary(b:InvestigationBundle)->dict[str,Any]:
    b.validate(); return {"schema_version":SCHEMA_VERSION,"case_id":b.case.id,"records":{n:len(getattr(b,n)) for n in ("sources","snapshots","entities","relationships","events","claims","evidence","reviews","publications","corrections","agent_tasks")}}
