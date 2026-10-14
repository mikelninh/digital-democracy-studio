/* SafeTrace Discourse Investigation Lab — static, reproducible, no telemetry. */
(() => {
'use strict';
const d = window.SAFETRACE_DATA;
if (!d) { document.getElementById('inspectorContent').textContent = 'Case data is unavailable.'; return; }
const byId = (arr, id) => arr.find(item => item.id === id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const state = { selection: {kind:'claim', id:'c2'}, mode:'all', query:'', issuesOnly:false, reviews:{} };
const el = id => document.getElementById(id);
const sourceFor = id => byId(d.sources,id);
const claimFor = id => byId(d.claims,id);
const actorFor = id => byId(d.actors,id);
const classFor = stance => ['contested','qualified','unverified'].includes(stance) ? stance : 'unverified';
const labelFor = stance => ({contested:'Contradicted / qualified',qualified:'Supported with limits',unverified:'Unverified'})[stance] || 'Needs review';
const relatedClaims = (kind,id) => kind==='actor' ? d.claims.filter(c=>c.actors.includes(id)) : d.claims.filter(c=>[...c.support,...c.counter].includes(id));

el('metricPosts').textContent=d.posts.length;
el('metricActors').textContent=d.actors.length;
el('metricClaims').textContent=d.claims.length;
el('metricSources').textContent=d.sources.length;

function toast(msg) { const t=el('toast');t.textContent=msg;t.hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>t.hidden=true,3200); }
function select(kind,id,scroll=false){ state.selection={kind,id}; render(); if(scroll) el('evidence').scrollIntoView({behavior:'smooth',block:'center'}); }
function evidenceButton(id,role='support'){ const s=sourceFor(id); if(!s)return '';return `<button class="evidence-item" data-select-source="${esc(id)}"><strong><span class="source-tag">${role==='counter'?'CHALLENGE':'SOURCE'} · ${esc(id.toUpperCase())}</span>${esc(s.title)}</strong><span>${esc(s.kind)} · ${esc(s.date)} · ${esc(s.anchor)} ↗</span></button>`; }
function postsForClaim(id){return d.posts.filter(p=>p.claim===id);}
function renderInspector(){
 const host=el('inspectorContent'); const {kind,id}=state.selection;
 if(kind==='claim') {
  const c=claimFor(id);if(!c)return;
  const count=postsForClaim(id).length, cited=new Set(postsForClaim(id).map(p=>p.source)).size;
  const reviewed=state.reviews[id];
  host.innerHTML=`<span class="chip ${classFor(c.stance)}">● ${labelFor(c.stance)}</span><h3>${esc(c.label)}</h3><p class="summary">${esc(c.full)}</p><div class="claim-finding"><b>What we can say</b><div>${esc(c.finding)}</div></div><span class="micro-label">SOURCE CHAIN · ${count} MESSAGES / ${cited} CITED SOURCE${cited===1?'':'S'}</span>${c.support.map(id=>evidenceButton(id)).join('')}${c.counter.map(id=>evidenceButton(id,'counter')).join('')}<span class="micro-label">WHAT THIS DOES NOT PROVE</span><div class="limitation">${esc(c.limitation)}</div><span class="micro-label">NEXT VERIFIABLE MOVE</span><p class="next-action">↗ ${esc(c.next)}</p><div class="review-box"><label class="micro-label" for="reviewInput" style="margin-top:4px">YOUR ANALYST NOTE · LOCAL ONLY</label><textarea id="reviewInput" maxlength="1600" placeholder="Record a missing source, alternative explanation or next question…">${esc(reviewed?.note || '')}</textarea><div class="review-controls"><button class="button green small" id="saveReview">Save review note</button>${reviewed?'<button class="button outline small" id="clearReview">Clear note</button>':''}</div><p class="review-note">${reviewed?'Saved in this browser session. Included in export.':'Human judgement is not automated. No data is sent.'}</p></div>`;
  el('saveReview').addEventListener('click',()=>{const note=el('reviewInput').value.trim();if(!note){toast('Write a note first.');return;}state.reviews[id]={note,at:new Date().toISOString()};renderInspector();toast('Analyst note saved for this session.');});
  if(reviewed)el('clearReview').addEventListener('click',()=>{delete state.reviews[id];renderInspector();toast('Analyst note cleared.');});
 } else if(kind==='source'){
  const s=sourceFor(id);if(!s)return;const claims=relatedClaims(kind,id);
  host.innerHTML=`<span class="chip qualified">◉ DOCUMENT / ${esc(s.id.toUpperCase())}</span><h3>${esc(s.title)}</h3><p class="summary">${esc(s.kind)} · ${esc(s.date)} · pinpoint: ${esc(s.anchor)}. This fictional excerpt is the complete supplied source passage for the demo.</p><span class="micro-label">EXACT EVIDENCE ANCHOR</span><blockquote class="source-quote">“${esc(s.excerpt)}”</blockquote><span class="micro-label">EVIDENCE LIMIT</span><div class="limitation">${esc(s.limitation)}</div><span class="micro-label">CITED BY ${claims.length} CLAIM${claims.length===1?'':'S'}</span>${claims.map(c=>`<button class="evidence-item" data-select-claim="${esc(c.id)}"><strong>${esc(c.label)} ↗</strong><span>${esc(labelFor(c.stance))}</span></button>`).join('')}<p class="review-note">Synthetic source ID: ${esc(s.id)} / ${esc(s.anchor)}. No real URL is implied.</p>`;
 } else {
  const a=actorFor(id);if(!a)return;const claims=relatedClaims(kind,id);const posts=d.posts.filter(p=>p.actor===id);
  host.innerHTML=`<span class="chip qualified">◉ ACTOR / ${esc(a.kind.toUpperCase())}</span><h3>${esc(a.name)}</h3><p class="summary">Fictional organisation in a deliberately simulated debate. ${posts.length} messages reference ${claims.length} claim${claims.length===1?'':'s'}.</p><span class="micro-label">CLAIMS THIS ORGANISATION REFERENCED</span>${claims.map(c=>`<button class="evidence-item" data-select-claim="${esc(c.id)}"><strong>${esc(c.label)} ↗</strong><span>${esc(labelFor(c.stance))}</span></button>`).join('')}<span class="micro-label">SAMPLE MESSAGES</span>${posts.map(p=>`<div class="evidence-item"><strong>${esc(p.date)} · ${esc(p.id.toUpperCase())}</strong><span>${esc(p.text)}</span></div>`).join('')}<div class="limitation">Mentioning the same claim does not establish coordination, endorsement, wrongdoing or shared ownership.</div>`;
 }
 host.querySelectorAll('[data-select-source]').forEach(b=>b.addEventListener('click',()=>select('source',b.dataset.selectSource)));
 host.querySelectorAll('[data-select-claim]').forEach(b=>b.addEventListener('click',()=>select('claim',b.dataset.selectClaim)));
}
function renderClaimGrid(){
 let claims=d.claims.filter(c=>`${c.label} ${c.full} ${c.topic}`.toLowerCase().includes(state.query));
 if(state.issuesOnly) claims=claims.filter(c=>c.stance!=='qualified');
 el('claimGrid').innerHTML=claims.length?claims.map(c=>`<button class="claim-card ${state.selection.kind==='claim'&&state.selection.id===c.id?'current':''}" data-card="${esc(c.id)}"><span class="number">${esc(c.id.toUpperCase())} / ${esc(c.topic.toUpperCase())}</span><span class="chip ${classFor(c.stance)}">${esc(labelFor(c.stance))}</span><h3>${esc(c.label)}</h3><span class="claim-foot">${esc(postsForClaim(c.id).length)} messages <span class="arrow">↗</span></span></button>`).join(''):'<p>No matching claims. Try another search.</p>';
 el('claimGrid').querySelectorAll('[data-card]').forEach(b=>b.addEventListener('click',()=>select('claim',b.dataset.card,true)));
}
const coords={};
d.actors.forEach((a,i)=>{coords[a.id]={x:112,y:41+i*56,kind:'actor',label:a.name};});
d.claims.forEach((c,i)=>{coords[c.id]={x:401,y:48+i*83,kind:'claim',label:c.label};});
d.sources.forEach((s,i)=>{coords[s.id]={x:690,y:22+i*46.7,kind:'source',label:s.title};});
const edges=[];d.claims.forEach(c=>{c.actors.forEach(a=>edges.push({from:a,to:c.id,kind:'actor'}));[...c.support,...c.counter].forEach(s=>edges.push({from:c.id,to:s,kind:'source'}));});
const colors={actor:'#5b9675',claim:'#d2a06d',source:'#7299b8'};
const ns='http://www.w3.org/2000/svg';
function svg(tag,attrs={},parent){const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(parent)parent.appendChild(e);return e;}
function renderGraph(){
 const g=el('graph');g.replaceChildren();const mode=state.mode,selected=state.selection.id;
 const visibleEdges=edges.filter(e=>mode==='all'||e.kind=== (mode==='sources'?'source':'actor'));
 const related=new Set([selected]);visibleEdges.forEach(e=>{if(e.from===selected)related.add(e.to);if(e.to===selected)related.add(e.from);});
 // Selecting a source/actor also highlights its neighbouring claims in the other view.
 edges.forEach(e=>{if(e.from===selected)related.add(e.to);if(e.to===selected)related.add(e.from);});
 const lines=svg('g',{},g);
 visibleEdges.forEach(e=>{const a=coords[e.from],b=coords[e.to],mid=(a.x+b.x)/2;const focus=e.from===selected||e.to===selected;svg('path',{d:`M${a.x},${a.y} C${mid},${a.y} ${mid},${b.y} ${b.x},${b.y}`,class:`graph-edge ${focus?'focus':'faded'}`,opacity:focus?'1':'.48'},lines);});
 const nodes=svg('g',{},g);
 Object.entries(coords).forEach(([id,n])=>{
  const faded=!related.has(id);const radius=n.kind==='claim'?19:12.5;
  const group=svg('g',{class:`graph-node ${faded?'faded':''} ${selected===id?'selected':''}`,tabindex:'0',role:'button','aria-label':`Inspect ${n.kind} ${n.label}`,transform:`translate(${n.x} ${n.y})`},nodes);
  svg('circle',{r:radius+7,class:'outer-ring'},group);
  svg('circle',{r:radius,fill:colors[n.kind]},group);
  const t=svg('text',{x:'0',y:n.kind==='claim'?'4':'3.7',fill:'#fff',style:'fill:#fff;font-size:10px;font-weight:800'},group);
  t.textContent=n.kind==='actor'?'A':n.kind==='source'?'S':id.slice(1);
  const txt=svg('text',{x:0,y:n.kind==='source'?28:n.kind==='claim'?34:27,class:'small-label'},group);
  const max=n.kind==='claim'?20:18;txt.textContent=n.label.length>max?n.label.slice(0,max-1)+'…':n.label;
  group.addEventListener('click',()=>select(n.kind,id));
  group.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();select(n.kind,id);}});
  const title=svg('title',{},group);title.textContent=n.label;
 });
}
function render(){renderGraph();renderInspector();renderClaimGrid();}
function exportReport(){
 const lines=[`# SafeTrace / Discourse Investigation Lab`,``, `**Case:** ${d.case.id} — ${d.case.title}`,`**Data:** 100% fictional training case; not real allegations.`,`**Exported:** ${new Date().toISOString()}`,``,`## Observations`,``];
 for(const c of d.claims){lines.push(`### ${c.id.toUpperCase()} — ${c.label}`,`- Original assertion: ${c.full}`,`- Classification: ${labelFor(c.stance)}`,`- Evidence-bounded assessment: ${c.finding}`,`- What it does NOT prove: ${c.limitation}`,`- Next step: ${c.next}`,`- Cited source trail (not necessarily confirmatory): ${c.support.map(id=>id.toUpperCase()+' '+sourceFor(id).anchor).join('; ') || 'none'}`,`- Challenges / counterevidence: ${c.counter.map(id=>id.toUpperCase()+' '+sourceFor(id).anchor).join('; ') || 'none'}`,`- Analyst note: ${state.reviews[c.id]?.note || 'No analyst note recorded'}`,``);}
 lines.push('## Source register','');d.sources.forEach(s=>lines.push(`- **${s.id.toUpperCase()} · ${s.anchor}:** ${s.title} (${s.date}; ${s.kind}). Exact excerpt: “${s.excerpt}” Limit: ${s.limitation}`));
 lines.push('','## Ethical boundary','This dataset is entirely fictional. Source repetition is not independent corroboration. No guilt, coordination, regulatory judgement or causal effect is inferred automatically. Any real-world use requires provenance, rights review and human oversight.');
 const url=URL.createObjectURL(new Blob([lines.join('\n')],{type:'text/markdown;charset=utf-8'}));
 const a=document.createElement('a');a.href=url;a.download='safetrace-case-001-brief.md';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),5000);toast('Case brief exported with source anchors and review notes.');
}
el('startTour').addEventListener('click',()=>select('claim','c2',true));
el('resetGraph').addEventListener('click',()=>{state.mode='all';document.querySelectorAll('.seg').forEach(s=>s.classList.toggle('active',s.dataset.graph==='all'));select('claim','c2');toast('Network reset to the original source-chain question.');});
document.querySelectorAll('[data-graph]').forEach(b=>b.addEventListener('click',()=>{state.mode=b.dataset.graph;document.querySelectorAll('[data-graph]').forEach(x=>x.classList.toggle('active',x===b));renderGraph();}));
el('claimSearch').addEventListener('input',e=>{state.query=e.target.value.toLowerCase().trim();renderClaimGrid();});
el('openIssuesOnly').addEventListener('click',()=>{state.issuesOnly=!state.issuesOnly;el('openIssuesOnly').setAttribute('aria-pressed',String(state.issuesOnly));renderClaimGrid();});
el('exportButton').addEventListener('click',exportReport);
document.querySelectorAll('.side-nav a').forEach(a=>a.addEventListener('click',()=>{document.querySelectorAll('.side-nav a').forEach(x=>x.classList.remove('active'));a.classList.add('active');}));
render();
})();
