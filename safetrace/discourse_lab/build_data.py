"""Build the fixed, fictional demonstration corpus.
This is a hand-authored teaching case, not a web scraper."""
import json
from pathlib import Path

ROOT=Path(__file__).parent
actors=[
 ('a1','Civic Mobility Office','Public unit'),
 ('a2','Streets for All','Advocacy group'),
 ('a3','Neighbourhood Access Collective','Community organisation'),
 ('a4','City Budget Observatory','Civic watchdog'),
 ('a5','Mobility Forward Institute','Research group'),
 ('a6','Transit Workers Council','Professional association'),
 ('a7','Metro Bulletin','Local publisher'),
]
sources=[
 ('s1','Mobility Programme Allocation Register','Official-style record','2026-02-12','§2.1','The 2026 programme authorises up to €8.4 million for crossings, cycle links and accessibility measures. Authorisation is not evidence of expenditure.','Budget authority is not spending; synthetic and not attributable to any real government.'),
 ('s2','Quarterly Outlay Note','Finance-style record','2026-06-30','Table 2','Of €8.4 million authorised, €1.9 million had been disbursed by the end of Q2. Further commitments and eventual outlays were not determined here.','Interim period; not a final annual accounting.'),
 ('s3','Six Junction Safety Brief','Briefing memo','2026-03-14','Finding 3','A 42% fall in reported near misses was observed across six monitored junctions over the stated pilot period. The memo does not include raw counts or sampling details.','No raw measurements or causal identification; changes might reflect reporting behaviour.'),
 ('s4','Pilot Data Request Reply','Correspondence','2026-04-09','Response 1','The underlying junction-level observations were not included in this response. We cannot independently reproduce the stated 42% figure from the supplied materials.','Absence in this supplied reply is not proof the data do not exist.'),
 ('s5','Access Concerns Survey','Community survey','2026-05-18','Question 6','Among 210 self-selected respondents, 46 described difficulties reaching or crossing at least one planned junction.','Convenience sample with self-selection; cannot estimate citywide prevalence.'),
 ('s6','Crossing Design Summary','Project drawing','2026-05-26','Drawings A–D','Four illustrated crossings include proposed kerb ramps. The drawings do not establish their installation or suitability in the completed works.','Design intent only; construction inspection not available.'),
 ('s7','Consultation Snapshot','Meeting summary','2026-04-23','Item 4','Of 210 recorded responses in the consultation, 68% preferred calmer pedestrian crossings. Recruitment was not designed to produce a representative sample.','Non-representative responses and ambiguous question wording.'),
 ('s8','Commuter Journey Announcement','Press material','2026-07-12','Headline','Selected travellers reported journeys up to 60% faster following pilot changes; no measurement methodology or comparator is provided.','Marketing-style claim; cannot generalise to a wider population.'),
 ('s9','Editorial Source-Chain Note','Research note','2026-07-19','Trace 1','Three separate organisations repeated the 42% near-miss figure, each pointing back to the same Six Junction Safety Brief. These are not three independent measurements.','A shared citation chain does not establish coordination or intent.'),
]
claims=[
 dict(id='c1',label='€8.4m already spent',full='The programme has already spent €8.4 million.',stance='contested',topic='Public spending',support=['s1'],counter=['s2'],actors=['a4','a7','a1'],date='2026-06-30',finding='The amount was authorised, not shown as spent. An interim note reports €1.9m disbursed.',limitation='Final spending after Q2 is outside this corpus.',next='Request the latest audited expenditure ledger and reconcile commitments with outlays.',severity='high'),
 dict(id='c2',label='42% fewer near misses',full='The changes reduced near misses by 42%.',stance='unverified',topic='Safety',support=['s3','s9'],counter=['s4'],actors=['a1','a2','a5','a7'],date='2026-07-19',finding='A single briefing is the origin of this figure; downstream repetition does not add independent confirmation.',limitation='Raw counts, protocol and confounders are not available. A causal improvement is not established.',next='Seek junction-level numerator/denominator data, methods, baseline dates and independent replication.',severity='high'),
 dict(id='c3',label='No accessibility provision',full='The redesign includes no accessibility measures.',stance='contested',topic='Accessibility',support=['s5'],counter=['s6'],actors=['a3','a6','a7'],date='2026-05-26',finding='People raised access concerns, yet the plans depict kerb ramps. Neither proves on-site outcomes.',limitation='Survey selection bias and no independent as-built access audit.',next='Compare completed crossings against design and interview affected access groups.',severity='medium'),
 dict(id='c4',label='68% backed safer crossings',full='68% of consulted respondents preferred calmer crossings.',stance='qualified',topic='Participation',support=['s7'],counter=[],actors=['a1','a2','a7'],date='2026-04-23',finding='The percentage is documented for the consultation responses, not a representative citywide sample.',limitation='Cannot extrapolate to all residents or infer approval of every design choice.',next='Publish sample method and collect a representative follow-up survey.',severity='low'),
 dict(id='c5',label='Travel times cut by 60%',full='The changes make all commutes 60% faster.',stance='unverified',topic='Mobility',support=['s8'],counter=[],actors=['a5','a1','a7'],date='2026-07-12',finding='The originating announcement describes selected journeys “up to” 60% faster, not all journeys.',limitation='No validated comparator, sample or method in the available material.',next='Obtain anonymised before-and-after journey samples and the measurement protocol.',severity='medium'),
]
posts=[]
seq=1
post_specs=[
 ('2026-02-18','a1','c1','Programme budget confirmed at €8.4m.','s1'),
 ('2026-03-17','a1','c2','Early briefing says near misses down 42%.','s3'),
 ('2026-03-20','a2','c2','A 42% drop deserves attention.','s3'),
 ('2026-03-27','a5','c2','Pilot highlights 42% fewer reported near misses.','s3'),
 ('2026-04-02','a7','c2','Three voices repeat the same 42% figure.','s3'),
 ('2026-04-25','a2','c4','68% of respondents wanted calmer crossings.','s7'),
 ('2026-04-28','a1','c4','Consultation records 68% in favour of calmer crossings.','s7'),
 ('2026-05-01','a7','c4','A local consultation puts support at 68%.','s7'),
 ('2026-05-20','a3','c3','Access concerns raised by dozens of respondents.','s5'),
 ('2026-05-22','a6','c3','Workers ask how accessible the crossings will be.','s5'),
 ('2026-05-28','a1','c3','Proposed designs include kerb ramps.','s6'),
 ('2026-06-06','a7','c3','Plans and survey give a more complicated picture.','s6'),
 ('2026-07-01','a4','c1','Question: was the whole €8.4m actually spent?','s2'),
 ('2026-07-03','a7','c1','€8.4m budget versus €1.9m paid: different numbers.','s2'),
 ('2026-07-07','a1','c1','Quarterly outlays are distinct from authorised funding.','s2'),
 ('2026-07-12','a5','c5','Selected commuters report up to 60% faster trips.','s8'),
 ('2026-07-13','a1','c5','Pilot news notes journeys up to 60% faster.','s8'),
 ('2026-07-15','a7','c5','Where does the 60% journey claim come from?','s8'),
 ('2026-07-19','a7','c2','Tracing the 42% figure finds one original memo.','s9'),
 ('2026-07-20','a3','c3','Design plans do not show what was installed.','s6'),
]
for date,actor,claim,text,source in post_specs:
    posts.append(dict(id=f'p{seq:02}',date=date,actor=actor,claim=claim,text=text,source=source));seq+=1
case=dict(id='SYN-DL-001',title='When a statistic outruns its source',subtitle='A fictional city mobility debate',description='Follow five claims through public-style records, repeated messages and unresolved questions.',dataset='Entirely synthetic. No real organisation or place is depicted.',updated='2026-10-14',scope='Public-discourse mapping, source lineage, cautious entity linking and human review')
fixture={'case':case,'actors':[dict(id=i,name=n,kind=k) for i,n,k in actors],
 'sources':[dict(id=i,title=t,kind=k,date=d,anchor=a,excerpt=e,limitation=l) for i,t,k,d,a,e,l in sources],
 'claims':claims,'posts':posts}
(ROOT/'data'/'corpus.json').write_text(json.dumps(fixture,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'data'/'corpus.js').write_text('/* Generated from corpus.json; run python build_data.py to regenerate. */\nwindow.SAFETRACE_DATA = '+json.dumps(fixture,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print(len(actors),'actors',len(sources),'sources',len(claims),'claims',len(posts),'posts')
