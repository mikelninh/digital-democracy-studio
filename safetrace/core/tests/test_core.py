from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from safetrace.core.adapters import adapt_arms_case, adapt_monitoring_proposal, adapt_political_money_graph, adapt_review_claim, adapt_source_engine, bundle_from_arms_case, bundle_from_case_pack, bundle_from_law_fairness, bundle_from_political_money_graph
from safetrace.core.charter import CaseAcceptanceWizard
from safetrace.core.compatibility import compatibility_issues
from safetrace.core.model import AgentTask, Case, CaseCharter, Claim, Evidence, InvestigationBundle, Publication, Review, Risk, Source
from safetrace.core.schema import schema_document, serialised_schema
from safetrace.core.vocabularies import BASELINE_PROHIBITED_METHODS
NOW="2026-07-24T00:00:00+00:00"

def bundle(sensitivity="public",contradict=False):
 ch=CaseCharter("charter:test","test","Bounded accountability case","What do the identified official records establish about the bounded decision?","The question affects public spending and tests whether official accountability records are complete.","Germany","lead","editor",NOW,"accepted",("One decision",),("Unsupported criminal allegations",),("primary official records",),("citizens",),(Risk("risk:misread","misinterpretation","A relationship may be mistaken for unlawful conduct.","medium","high","Show evidence state, limitations and alternatives.","editor"),),tuple(sorted(BASELINE_PROHIBITED_METHODS)),("public","sensitive_internal"),"Only reviewed public records may be published; no automated accusation, contact or referral.",sensitivity!="public")
 c=Case("test",ch.id,ch.title,"Germany","active",NOW,NOW,ch.public_interest_rationale,ch.publication_boundary); s=Source("source","Official record","Authority","https://example.org/record","official_record","primary_official","Germany",NOW)
 ev=[Evidence("ev:s",c.id,s.id,"supporting","The official record states the decision.",NOW,"page 1")]
 if contradict:ev.append(Evidence("ev:c",c.id,s.id,"contradicting","A later note qualifies the record.",NOW,"page 2"))
 r=Review("review",c.id,"claim","claim","approved","human","editor","The wording is limited and contradictions were considered.",NOW,"approved" if sensitivity!="public" else "not_required","completed" if sensitivity!="public" else "not_required",contradict)
 cl=Claim("claim",c.id,"The official record documents the bounded public decision.","verified_fact",sensitivity,"human",True,tuple(x.id for x in ev),NOW,(r.id,))
 p=Publication("pub",c.id,"public_redacted","published",(cl.id,),(r.id,),ch.publication_boundary,NOW,NOW)
 return InvestigationBundle(c,ch,sources=[s],evidence=ev,claims=[cl],reviews=[r],publications=[p])

class ModelTests(unittest.TestCase):
 def test_round_trip(self):
  b=bundle(contradict=True); self.assertEqual(InvestigationBundle.from_dict(b.to_dict()).to_dict(),b.to_dict())
 def test_missing_anchor_blocks(self):
  b=bundle(); b.evidence[0]=Evidence(**{**b.evidence[0].__dict__,"source_anchor":None}); self.assertRaisesRegex(ValueError,"lacks source anchor",b.validate)
 def test_human_review_blocks(self):
  b=bundle(); b.claims[0]=Claim(**{**b.claims[0].__dict__,"review_ids":()}); self.assertRaisesRegex(ValueError,"without human approval",b.validate)
 def test_sensitive_claim_gate(self):
  b=bundle("internal"); b.reviews[0]=Review(**{**b.reviews[0].__dict__,"legal_review":"pending"}); self.assertRaisesRegex(ValueError,"requires legal approval",b.validate)
 def test_contradiction_gate(self):
  b=bundle(contradict=True); b.reviews[0]=Review(**{**b.reviews[0].__dict__,"contradictory_evidence_addressed":False}); self.assertRaisesRegex(ValueError,"ignores contradicting evidence",b.validate)
 def test_agent_tool_and_zone_gates(self):
  b=bundle(); b.agent_tasks.append(AgentTask("bad",b.case.id,"Publish without approval","explainer","queued",("claim",),("publish_publicly",),"public","proposal/1","test","1","human",NOW)); self.assertRaisesRegex(ValueError,"prohibited tools",b.validate)
  b=bundle(); b.charter=CaseCharter(**{**b.charter.__dict__,"permitted_data_zones":("public",)}); b.agent_tasks.append(AgentTask("zone",b.case.id,"Read restricted evidence","reader","queued",("source",),("read_source",),"restricted_partner","proposal/1","test","1","human",NOW)); self.assertRaisesRegex(ValueError,"data-zone ceiling",b.validate)

class CharterSchemaTests(unittest.TestCase):
 def test_template_and_restricted_gate(self):
  w=CaseAcceptanceWizard(); ch=w.from_payload(w.template(case_id="case-x")); self.assertTrue(w.evaluate(ch).accepted)
  ch=CaseCharter(**{**ch.__dict__,"permitted_data_zones":("public","restricted_partner")}); self.assertFalse(w.evaluate(ch).accepted)
 def test_schema_is_committed_and_compatibility_is_conservative(self):
  path=Path(__file__).parents[1]/"schemas/safetrace-core-1.2.schema.json"; self.assertEqual(path.read_text(),serialised_schema()); self.assertEqual(json.loads(path.read_text()),schema_document())
  self.assertTrue(compatibility_issues({"type":"string","enum":["a","b"]},{"type":"string","enum":["a"]}))
  self.assertTrue(compatibility_issues({"type":"object","properties":{"id":{"type":"string"}},"required":["id"]},{"type":"object","properties":{"id":{"type":"string"},"x":{"type":"string"}},"required":["id","x"]}))

class AdapterTests(unittest.TestCase):
 def test_source_hashes_and_monitoring_gate(self):
  s=SimpleNamespace(source_id="s",title="Source",url="https://example.org/s",publisher="Authority",source_type="official_record",parser="html"); r=SimpleNamespace(source_id="s",canonical_url=s.url,retrieved_at=NOW,content_type="text/html",byte_length=1,sha256="a"*64,normalized_sha256="b"*64,parser_version="0.3",raw_path="raw",changed=False); out=adapt_source_engine(case_id="c",jurisdiction="Germany",source_definition=s,snapshot_receipt=r); self.assertEqual(out.snapshots[0].sha256,"a"*64)
  p=SimpleNamespace(id="p",source_id="s",created_at=NOW,summary="Official source changed and needs human review.",review_state="pending_review",affected_claims=[]); task=adapt_monitoring_proposal(p,case_id="c").agent_tasks[0]; self.assertEqual(task.status,"awaiting_human"); self.assertNotIn("publish",task.allowed_tools)
 def test_relationship_and_review_provenance(self):
  prov=SimpleNamespace(source_id="s",source_url="https://example.org/s",source_title="Disclosure",retrieved_or_checked_at=NOW,evidence_state="verified_official_record",source_anchor="row 1"); g=SimpleNamespace(nodes=[SimpleNamespace(id="a",type="organisation",label="A",attributes={},provenance=(prov,)),SimpleNamespace(id="b",type="political_party",label="B",attributes={},provenance=(prov,))],edges=[SimpleNamespace(id="e",type="donated_to",source="a",target="b",attributes={},provenance=(prov,),interpretation="documented_relationship_only")]); out=adapt_political_money_graph(g,case_id="c"); self.assertEqual(out.evidence[0].source_anchor,"row 1"); self.assertTrue(out.relationships[0].evidence_ids)
  ev=SimpleNamespace(id="ev",role="supporting",source_id="s",source_url="https://example.org/s",source_title="Source",summary="Supports claim",source_anchor="p1"); d=SimpleNamespace(outcome="approved",reviewer_role="editor",rationale="Limited to source.",decided_at=NOW,legal_review="not_required",right_of_reply="not_required",contradictory_evidence_addressed=False); c=SimpleNamespace(id="cl",text="Limited source-backed claim.",evidence_state="verified_fact",sensitivity="ordinary",origin="human",evidence=[ev],decision=d,correction_history=[]); self.assertEqual(adapt_review_claim(c,case_id="c").reviews[0].outcome,"approved")
 def test_arms_stage_distinction(self):
  s=SimpleNamespace(id="s",url="https://example.org/s",title="Export",publisher="Authority",checked_at=NOW,anchor="table"); e=SimpleNamespace(id="e",type="export_authorisation",date="2026",title="Authorisation",evidence_state="verified_fact",source=s,actor="Authority",recipient_or_beneficiary="Recipient",amount_eur="1",status="recorded",attributes={"delivered":False}); c=SimpleNamespace(id="c",jurisdiction="Germany",events=[e],unresolved_questions=[]); self.assertFalse(adapt_arms_case(c).events[0].attributes["delivered"])

class ExistingCases(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.root=Path(__file__).parents[2]
  if not (cls.root/"source_engine").exists():raise unittest.SkipTest("legacy repository modules absent")
 def test_all_existing_cases_migrate(self):
  from safetrace.case_packs.generate_case_pack import build_pack
  from safetrace.political_money.build_graph import build as graph
  from safetrace.arms_monitor.build_monitor import build as arms
  from safetrace.law_fairness.model import load_case
  b1=bundle_from_case_pack(build_pack(self.root/"source_engine/data",generated_at=NOW)); self.assertEqual((b1.case.id,len(b1.claims)),("case-001",14))
  with tempfile.TemporaryDirectory() as d:
   b2=bundle_from_political_money_graph(graph(self.root/"political_money/data/seed.json",Path(d)/"g.json")); b3=bundle_from_arms_case(arms(self.root/"arms_monitor/data/baseline.json",Path(d)/"a.json"))
  b4=bundle_from_law_fairness(load_case(self.root/"law_fairness/data/case_004.json")); self.assertEqual({b1.case.id,b2.case.id,b3.case.id,b4.case.id},{"case-001","case-002","case-003","case-004"}); [x.validate() for x in (b1,b2,b3,b4)]
if __name__=="__main__":unittest.main()
