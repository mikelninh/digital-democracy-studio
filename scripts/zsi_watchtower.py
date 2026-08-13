from __future__ import annotations
import difflib,hashlib,json,re,urllib.request
from datetime import datetime,timezone
from html.parser import HTMLParser
from pathlib import Path
R=Path(__file__).resolve().parents[1];W=R/'zero-suffering-intelligence'/'watchtower';S=W/'sources.json';D=W/'snapshots';O=W/'status.json';C=W/'claim-review-status.json';E=W/'events.json';UA='ZSI-Watchtower/0.9'
class T(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.skip=0;self.p=[]
 def handle_starttag(self,t,a):
  if t.lower() in {'script','style','noscript','svg'}:self.skip+=1
 def handle_endtag(self,t):
  if t.lower() in {'script','style','noscript','svg'} and self.skip:self.skip-=1
 def handle_data(self,d):
  if not self.skip and d.strip():self.p.append(d.strip())
def clean(b,ch='utf-8'):
 p=T();p.feed(b.decode(ch,errors='replace'));s='\n'.join(p.p);s=re.sub(r'[ \t]+',' ',s);s=re.sub(r'Abgerufen am \d{2}\.\d{2}\.\d{4} um \d{1,2}:\d{2} Uhr','Abgerufen am [volatile]',s);return re.sub(r'\n{2,}','\n',s).strip()
def fetch(u):
 q=urllib.request.Request(u,headers={'User-Agent':UA,'Accept':'text/html,application/xhtml+xml,*/*;q=0.8'})
 with urllib.request.urlopen(q,timeout=35) as r:
  b=r.read();t=r.headers.get_content_type();ch=r.headers.get_content_charset() or 'utf-8';x=clean(b,ch) if t in {'text/html','application/xhtml+xml'} else b.decode(ch,errors='replace').strip();return x,{'http_status':getattr(r,'status',200),'content_type':t}
def h(x):return hashlib.sha256(x.encode()).hexdigest()
def load(p,d):
 try:return json.loads(p.read_text()) if p.exists() else d
 except:return d
def main():
 now=datetime.now(timezone.utc).replace(microsecond=0).isoformat();D.mkdir(parents=True,exist_ok=True);reg=json.loads(S.read_text());old=load(C,{'claims':{}}).get('claims',{});review={k:v for k,v in old.items() if v.get('status')=='needs_review'};events=load(E,{'events':[]}).get('events',[]);rows=[]
 for s in reg['sources']:
  sid=s['source_id'];p=D/f'{sid}.txt';prev=p.read_text().rstrip('\n') if p.exists() else '';ph=h(prev) if prev else None;row={'source_id':sid,'title':s['title'],'category':s['category'],'url':s['url'],'checked_at':now,'claim_ids':s.get('claim_ids',[]),'previous_sha256':ph}
  try:
   cur,meta=fetch(s['url']);ch=h(cur);base=not p.exists();sus=bool(prev) and len(prev)>=500 and len(cur)<max(250,int(len(prev)*.25));row.update(meta)
   if sus:row.update({'sha256':ch,'status':'fetch_suspect','character_count':len(cur),'expected_character_count':len(prev),'warning':'retrieved content collapsed; prior snapshot preserved; claims not flagged'})
   else:
    changed=not base and ph!=ch;di=list(difflib.unified_diff(prev.splitlines(),cur.splitlines(),fromfile='previous',tofile='current',lineterm='',n=1))[:80] if changed else [];row.update({'sha256':ch,'status':'baseline_created' if base else ('changed' if changed else 'unchanged'),'diff':di,'character_count':len(cur)});p.write_text(cur)
    if changed:
     eid=hashlib.sha256(f'{sid}:{ph}:{ch}'.encode()).hexdigest()[:16];ev={'event_id':eid,'source_id':sid,'title':s['title'],'detected_at':now,'claim_ids':s.get('claim_ids',[]),'diff':di,'review_status':'needs_review'}
     if not any(z.get('event_id')==eid for z in events):events.insert(0,ev)
     for cid in s.get('claim_ids',[]):review[cid]={'status':'needs_review','source_id':sid,'detected_at':now,'event_id':eid}
  except Exception as ex:row.update({'status':'fetch_failed','error':f'{type(ex).__name__}: {ex}'})
  rows.append(row)
 out={'schema':'zsi.watchtower/status-0.9','generated_at':now,'sources_total':len(rows),'unchanged':sum(x['status']=='unchanged' for x in rows),'changed':sum(x['status']=='changed' for x in rows),'baselines_created':sum(x['status']=='baseline_created' for x in rows),'fetch_suspect':sum(x['status']=='fetch_suspect' for x in rows),'fetch_failed':sum(x['status']=='fetch_failed' for x in rows),'claims_needing_review':sorted(review),'sources':rows};O.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');C.write_text(json.dumps({'schema':'zsi.watchtower/claim-review-status-0.9','generated_at':now,'claims':review},ensure_ascii=False,indent=2)+'\n');E.write_text(json.dumps({'schema':'zsi.watchtower/events-0.9','events':events[:100]},ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['sources_total','unchanged','changed','fetch_suspect','fetch_failed']},indent=2))
if __name__=='__main__':main()
