from __future__ import annotations
import difflib, hashlib, json, re, urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; WT=ROOT/'zero-suffering-intelligence'/'watchtower'; SOURCES=WT/'sources.json'; SNAP=WT/'snapshots'; STATUS=WT/'status.json'; CLAIMS=WT/'claim-review-status.json'; EVENTS=WT/'events.json'; UA='ZeroSufferingIntelligence-Watchtower/0.8 (+https://github.com/mikelninh/digital-democracy-studio)'
class Text(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.skip=0; self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower() in {'script','style','noscript','svg'}: self.skip+=1
    def handle_endtag(self,tag):
        if tag.lower() in {'script','style','noscript','svg'} and self.skip: self.skip-=1
    def handle_data(self,data):
        if not self.skip and data.strip(): self.parts.append(data.strip())
def clean(raw,charset='utf-8'):
    p=Text(); p.feed(raw.decode(charset,errors='replace')); s='\n'.join(p.parts); s=re.sub(r'[ \t]+',' ',s); s=re.sub(r'Abgerufen am \d{2}\.\d{2}\.\d{4} um \d{1,2}:\d{2} Uhr','Abgerufen am [volatile]',s); return re.sub(r'\n{2,}','\n',s).strip()
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'text/html,application/xhtml+xml,*/*;q=0.8'})
    with urllib.request.urlopen(req,timeout=35) as r:
        raw=r.read(); typ=r.headers.get_content_type(); charset=r.headers.get_content_charset() or 'utf-8'; txt=clean(raw,charset) if typ in {'text/html','application/xhtml+xml'} else raw.decode(charset,errors='replace').strip(); return txt,{'http_status':getattr(r,'status',200),'content_type':typ,'etag':r.headers.get('ETag'),'last_modified':r.headers.get('Last-Modified')}
def sha(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()
def load(path,fallback):
    try: return json.loads(path.read_text(encoding='utf-8')) if path.exists() else fallback
    except Exception: return fallback
def diff(a,b): return list(difflib.unified_diff(a.splitlines(),b.splitlines(),fromfile='previous',tofile='current',lineterm='',n=1))[:80]
def main():
    now=datetime.now(timezone.utc).replace(microsecond=0).isoformat(); SNAP.mkdir(parents=True,exist_ok=True); registry=json.loads(SOURCES.read_text(encoding='utf-8')); old=load(CLAIMS,{'claims':{}}).get('claims',{}); review={k:v for k,v in old.items() if v.get('status')=='needs_review'}; events=load(EVENTS,{'events':[]}).get('events',[]); results=[]
    for src in registry.get('sources',[]):
        sid=src['source_id']; path=SNAP/f'{sid}.txt'; previous=path.read_text(encoding='utf-8').rstrip('\n') if path.exists() else ''; ph=sha(previous) if previous else None; row={'source_id':sid,'title':src['title'],'category':src['category'],'url':src['url'],'checked_at':now,'claim_ids':src.get('claim_ids',[]),'previous_sha256':ph}
        try:
            current,meta=fetch(src['url']); ch=sha(current); baseline=not path.exists(); changed=not baseline and ph!=ch; d=diff(previous,current) if changed else []; row.update(meta); row.update({'sha256':ch,'status':'baseline_created' if baseline else ('changed' if changed else 'unchanged'),'diff':d,'character_count':len(current)}); path.write_text(current,encoding='utf-8')
            if changed:
                eid=hashlib.sha256(f'{sid}:{ph}:{ch}'.encode()).hexdigest()[:16]; ev={'event_id':eid,'source_id':sid,'title':src['title'],'detected_at':now,'previous_sha256':ph,'sha256':ch,'claim_ids':src.get('claim_ids',[]),'diff':d,'review_status':'needs_review'}
                if not any(x.get('event_id')==eid for x in events): events.insert(0,ev)
                for cid in src.get('claim_ids',[]): review[cid]={'status':'needs_review','reason':f'Source changed: {sid}','source_id':sid,'detected_at':now,'event_id':eid}
        except Exception as exc: row.update({'status':'fetch_failed','error':f'{type(exc).__name__}: {exc}'})
        results.append(row)
    summary={'schema':'zsi.watchtower/status-0.8','generated_at':now,'sources_total':len(results),'unchanged':sum(r['status']=='unchanged' for r in results),'changed':sum(r['status']=='changed' for r in results),'baselines_created':sum(r['status']=='baseline_created' for r in results),'fetch_failed':sum(r['status']=='fetch_failed' for r in results),'claims_needing_review':sorted(review),'sources':results}; STATUS.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); CLAIMS.write_text(json.dumps({'schema':'zsi.watchtower/claim-review-status-0.8','generated_at':now,'claims':review},ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); EVENTS.write_text(json.dumps({'schema':'zsi.watchtower/events-0.8','events':events[:100]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({k:summary[k] for k in ['sources_total','unchanged','changed','baselines_created','fetch_failed']},indent=2))
if __name__=='__main__': main()
