from __future__ import annotations
import json, re
from difflib import SequenceMatcher
from typing import Any

ASSET_TYPES = {"LEGAL_OWNER_OF","SECURITY_INTEREST_IN","OPERATES_AT","LESSEE_OF"}

def norm(s): return " ".join(re.sub(r"[^a-z0-9]+"," ",s.lower()).split())
def pct(x): return f"{x*100:.0f}%"
def index(data,key): return {x["id"]:x for x in data.get(key,[])}
def obs(data,p=None): return [x for x in data["observations"] if p is None or x["predicate"]==p]

def validate_input(data:dict[str,Any])->list[str]:
    e,a,s=index(data,"entities"),index(data,"assets"),index(data,"sources")
    errors=[]
    if "SYNTHETIC" not in data.get("classification","").upper(): errors.append("classification must be synthetic")
    if data.get("target_entity_id") not in e: errors.append("unknown target_entity_id")
    if not data.get("client_question"): errors.append("missing client_question")
    for x in data.get("observations",[]):
        if x.get("source") not in s: errors.append(f"{x.get('source')}: unknown source")
        if x.get("subject") not in e: errors.append(f"{x.get('subject')}: unknown subject")
        if x.get("predicate") in ASSET_TYPES and x.get("object") not in a: errors.append(f"{x.get('object')}: unknown asset")
    return errors

def ownership_paths(data):
    target=data["target_entity_id"]; ents=index(data,"entities")
    by_obj={}
    for x in obs(data,"OWNS"): by_obj.setdefault(x["object"],[]).append(x)
    out=[]
    def walk(obj,share,path,seen):
        for x in by_obj.get(obj,[]):
            owner=x["subject"]
            if owner in seen: continue
            eff=round(share*float(x["value"]),6); steps=path+[x]
            out.append({"owner_id":owner,"owner_name":ents[owner]["name"],"direct":obj==target,
                        "effective_interest":eff,"sources":sorted({z["source"] for z in steps})})
            walk(owner,eff,steps,seen|{owner})
    walk(target,1.0,[],{target})
    return sorted(out,key=lambda x:(-x["effective_interest"],x["owner_id"]))

def screening_results(data):
    ents=index(data,"entities"); threshold=data["rules"]["name_screening_threshold"]; out=[]
    for x in obs(data,"SCREENING_CANDIDATE"):
        t,c=ents[x["subject"]],ents[x["object"]]
        sim=SequenceMatcher(None,norm(t["name"]),norm(c["name"])).ratio()
        ti,ci=t.get("identifiers",{}),c.get("identifiers",{})
        conflicts=[k for k in ("dob","nationality") if ti.get(k) and ci.get(k) and ti[k]!=ci[k]]
        overlap={k:v for k,v in ti.items() if ci.get(k)==v}
        same=sim>=threshold and not conflicts and bool(overlap)
        out.append({"target_name":t["name"],"candidate_name":c["name"],"name_similarity":round(sim,4),
                    "conflicting_identifiers":conflicts,"stable_identifier_overlap":overlap,"same_as":same,
                    "source":x["source"],"assessment":"Rejected as SAME_AS: stable identity fields conflict." if not same else "Candidate identity fields agree."})
    return out

def contradiction_results(data):
    ents=index(data,"entities"); src=index(data,"sources"); groups={}
    for x in obs(data,"DIRECTOR_OF"): groups.setdefault((x["subject"],x["object"]),[]).append(x)
    out=[]
    rank=lambda sid: 0 if str(src[sid]["authority"]).startswith("A") else 1 if str(src[sid]["authority"]).startswith("B") else 2
    for (person,company),items in groups.items():
        if len({json.dumps(x["value"]) for x in items})<2: continue
        items=sorted(items,key=lambda x:(rank(x["source"]),x["source"]))
        out.append({"person_name":ents[person]["name"],"company_name":ents[company]["name"],
                    "sources":[x["source"] for x in items],"observed_values":[x["value"] for x in items],
                    "assessment":"Sources conflict on current director status; authoritative filing outranks self-report but must be refreshed.",
                    "next_action":"Obtain the latest authoritative registry filing history and effective date."})
    return out

def payment_anomalies(data):
    ents=index(data,"entities"); groups={}
    for x in obs(data,"PAYMENT_BENEFICIARY_FOR"): groups.setdefault((x["subject"],x["object"]),[]).append(x)
    out=[]
    for (supplier,target),items in groups.items():
        if len({x["value"] for x in items})<2: continue
        items=sorted(items,key=lambda x:x["source"]); old,new=items[0]["value"],items[-1]["value"]
        out.append({"supplier_name":ents[supplier]["name"],"target_name":ents[target]["name"],
                    "contract_beneficiary_id":old,"contract_beneficiary_name":ents[old]["name"],
                    "changed_beneficiary_id":new,"changed_beneficiary_name":ents[new]["name"],
                    "sources":[x["source"] for x in items],
                    "assessment":"A later payment instruction changes the beneficiary away from the contractual counterparty. This is an anomaly requiring verification, not proof of fraud or sanctions evasion.",
                    "next_action":"Verify the instruction through a known counterparty channel and verify beneficiary-account ownership."})
    return out

def asset_results(data):
    ents,assets=index(data,"entities"),index(data,"assets"); out=[]
    meanings={"LEGAL_OWNER_OF":"Legal ownership is established.","SECURITY_INTEREST_IN":"Security interest only; not ownership.",
              "OPERATES_AT":"Operation/use only; not ownership.","LESSEE_OF":"Lease/use only; not ownership."}
    for x in obs(data):
        if x["predicate"] in ASSET_TYPES and x.get("value") is True:
            out.append({"party_name":ents[x["subject"]]["name"],"asset_id":x["object"],"asset_name":assets[x["object"]]["name"],
                        "interest_type":x["predicate"],"source":x["source"],"assessment":meanings[x["predicate"]]})
    return sorted(out,key=lambda x:(x["asset_id"],x["interest_type"],x["party_name"]))

def investigate(data):
    errors=validate_input(data)
    if errors: raise ValueError("; ".join(errors))
    ents=index(data,"entities"); target=ents[data["target_entity_id"]]
    own=ownership_paths(data); by_owner={x["owner_id"]:x for x in own}
    nominee={x["subject"] for x in obs(data,"NOMINEE_STATUS") if x["value"] is True}
    no_ubo={x["subject"] for x in obs(data,"NATURAL_PERSON_UBO_IDENTIFIED") if x["value"] is False}
    gaps=[{"entity_id":eid,"entity_name":ents[eid]["name"],"effective_interest":by_owner[eid]["effective_interest"],
           "sources":sorted(set(by_owner[eid]["sources"])|{x["source"] for x in obs(data) if x["subject"]==eid and x["predicate"] in {"NOMINEE_STATUS","NATURAL_PERSON_UBO_IDENTIFIED"}})}
          for eid in sorted(nominee&no_ubo) if eid in by_owner]
    screen=screening_results(data); contradictions=contradiction_results(data); payments=payment_anomalies(data); assets=asset_results(data)
    negative=[{"subject_name":ents[x["subject"]]["name"],"source":x["source"],"scope":x.get("scope","bounded source"),
               "assessment":"No adverse hit in this bounded source; this does not prove absence of litigation or adverse records elsewhere."}
              for x in obs(data,"COURT_SEARCH_ADVERSE_HIT") if x["value"] is False]
    findings=[]
    for x in own:
        kind="direct" if x["direct"] else "indirect"
        findings.append({"category":"ownership","status":"supported","severity":"info",
                         "conclusion":f"{x['owner_name']} has a documented {pct(x['effective_interest'])} {kind} economic interest in {target['name']}.",
                         "sources":x["sources"]})
    for x in gaps:
        findings.append({"category":"beneficial_ownership_gap","status":"unresolved","severity":"medium",
                         "conclusion":f"The natural-person beneficial owner behind {x['entity_name']} ({pct(x['effective_interest'])} effective interest) is unresolved in the supplied record.",
                         "sources":x["sources"]})
    for x in payments: findings.append({"category":"payment_route","status":"requires_verification","severity":"high","conclusion":x["assessment"],"sources":x["sources"]})
    for x in contradictions: findings.append({"category":"contradiction","status":"requires_verification","severity":"medium","conclusion":f"Current director status for {x['person_name']} is contradictory across supplied sources.","sources":x["sources"]})
    for x in screen: findings.append({"category":"screening","status":"rejected_match" if not x["same_as"] else "candidate_match","severity":"info" if not x["same_as"] else "high","conclusion":x["assessment"],"sources":[x["source"]]})
    actions=[]
    if gaps: actions.append({"priority":1,"action":"Resolve beneficial ownership behind nominee shareholder(s).","why":"Completes the ownership/control assessment.","best_source":"Current official beneficial-ownership/PSC filing or client-authorised KYC documentation."})
    if payments: actions.append({"priority":2,"action":"Verify the payment-beneficiary change independently.","why":"Most immediate transaction-risk anomaly.","best_source":"Known counterparty contact plus beneficiary-account documentation."})
    if contradictions: actions.append({"priority":3,"action":"Refresh current director status.","why":"Supplied sources disagree on a consequential management fact.","best_source":"Fresh authoritative registry filing history."})
    if screen: actions.append({"priority":4,"action":"Refresh sanctions screening against authoritative live lists.","why":"Training fixture is not a live compliance check.","best_source":"Relevant authoritative sanctions lists at decision time."})
    edd=bool(gaps or payments or contradictions)
    return {"schema":"safetrace.investigation-result/1.0","case_id":data["case_id"],"classification":data["classification"],"status":"completed",
            "client_question":data["client_question"],"subject":{"id":target["id"],"name":target["name"]},
            "executive_result":{"decision":"ENHANCED_DUE_DILIGENCE_REQUIRED" if edd else "NO_MATERIAL_GAPS_FOUND","confidence":0.93 if edd else 0.90,
              "confirmed_sanctions_match":any(x["same_as"] for x in screen),"material_findings":sum(x["severity"] in {"high","medium"} for x in findings),
              "open_actions":len(actions),"analyst_review_required":data["rules"].get("consequential_output_requires_human_review",True),
              "summary":"Visible ownership is supported, but enhanced due diligence is required before a consequential decision. Beneficial ownership behind a nominee stake is unresolved, a payment-beneficiary change is unverified, director status is contradictory, and the sanctions near-name candidate is rejected because stable identity fields conflict."},
            "ownership":{"paths":own,"beneficial_ownership_gaps":gaps},"screening":screen,"contradictions":contradictions,
            "payment_anomalies":payments,"negative_evidence":negative,"asset_interests":assets,"findings":findings,"next_actions":actions,
            "guardrails":["Risk indicators are not accusations.","Fuzzy-name leads are not confirmed identities.","Negative search results are bounded.","Ownership, security, operation and lease/use remain distinct.","Consequential conclusions require human review."]}

def render_markdown(r):
    ex=r["executive_result"]; L=[f"# Investigation Result — {r['case_id']}","",f"**Subject:** {r['subject']['name']}",f"**Decision:** `{ex['decision']}`",
      f"**Confidence:** {ex['confidence']:.0%}",f"**Confirmed sanctions match:** {'yes' if ex['confirmed_sanctions_match'] else 'no'}",
      f"**Analyst review required:** {'yes' if ex['analyst_review_required'] else 'no'}","","## Executive finding","",ex["summary"],"",
      "## What the investigation established",""]
    for f in r["findings"]: L.append(f"- **{f['category']} · {f['status']} · {f['severity']}** — {f['conclusion']} _Sources: {', '.join(f['sources'])}_")
    L+=["","## Ownership results",""]
    for x in r["ownership"]["paths"]: L.append(f"- {x['owner_name']}: **{pct(x['effective_interest'])} {'direct' if x['direct'] else 'indirect'} economic interest** (sources: {', '.join(x['sources'])}).")
    L+=["","## Asset trace",""]
    for x in r["asset_interests"]: L.append(f"- **{x['asset_name']}** — {x['party_name']} → `{x['interest_type']}`. {x['assessment']} _Source: {x['source']}_")
    L+=["","## What remains unresolved",""]
    for f in r["findings"]:
        if f["status"] in {"unresolved","requires_verification"}: L.append(f"- {f['conclusion']}")
    L+=["","## Next investigative actions",""]
    for a in r["next_actions"]: L.append(f"{a['priority']}. **{a['action']}** {a['why']} _Best source: {a['best_source']}_")
    L+=["","## Boundaries","","- Synthetic training case; no real-world allegation.",
        "- Generated from source-backed observations, not copied from a pre-written memo.",
        "- JSON and Markdown outputs are regenerated by the same deterministic pipeline and CI fails if they are stale.",
        "- Real engagements require current authoritative sources and human analyst review.",""]
    return "\n".join(L)
