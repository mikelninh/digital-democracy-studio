document.addEventListener('DOMContentLoaded', () => {
  const svg = document.querySelector('.graph');
  const graphCard = document.querySelector('.graphcard');
  if (!svg || !graphCard) return;

  const live = document.querySelector('.live');
  if (live) live.textContent = 'Public alpha · v0.2';

  const nodes = [
    {
      title: 'Betrieb Mucke', type: 'Farm', status: 'verified', confidence: 'high',
      claim: 'Tönnies Livestock publicly profiles Betrieb Mucke as a long-term partner; the farm describes collaboration including offtake arrangements.',
      source: 'Tönnies Livestock — Landwirtschaft im Dialog',
      url: 'https://toennies-livestock.de/landwirtschaft-im-dialog/',
      boundary: 'This does not prove that animals from Betrieb Mucke went to a specific slaughterhouse.'
    },
    {
      title: 'Betrieb Mertens', type: 'Farm', status: 'verified', confidence: 'high',
      claim: 'Tönnies Livestock publicly profiles Betrieb Mertens as a partner farm in piglet rearing and pig finishing.',
      source: 'Tönnies Livestock — Landwirtschaft im Dialog',
      url: 'https://toennies-livestock.de/landwirtschaft-im-dialog/',
      boundary: 'This does not prove a specific slaughter destination or shipment.'
    },
    {
      title: 'Tönnies Livestock', type: 'Company / intermediary', status: 'verified', confidence: 'high',
      claim: 'Tönnies Livestock describes itself as a livestock marketing business within the Tönnies system, handling relationships with producers and finishers.',
      source: 'Tönnies Livestock — Über uns',
      url: 'https://toennies-livestock.de/ueber-uns/',
      boundary: 'Group membership does not by itself prove where a particular animal was slaughtered.'
    },
    {
      title: 'Tönnies / Premium Food Group', type: 'Corporate group', status: 'verified', confidence: 'high',
      claim: 'Premium Food Group is the holding-level name used for the former Tönnies Group; group materials describe its meat and processing activities.',
      source: 'Premium Food Group — company history',
      url: 'https://premiumfoodgroup.de/en/group/history/',
      boundary: 'A group-level relationship is not automatically a legal-entity-level claim. Entity resolution remains explicit.'
    },
    {
      title: 'Lobbying + policy', type: 'Influence lane', status: 'verified', confidence: 'high',
      claim: 'A group-linked central-services entity appears in the German Bundestag Lobbyregister, including named policy initiatives.',
      source: 'Deutscher Bundestag — Lobbyregister R000472',
      url: 'https://www.lobbyregister.bundestag.de/suche/R000472/76599',
      boundary: 'Lobbying activity is not evidence that a policy outcome was caused or purchased by the company.'
    },
    {
      title: 'Competition record', type: 'Authority record', status: 'verified', confidence: 'high',
      claim: 'The Bundeskartellamt documented and prohibited a proposed acquisition of Vion assets by a Tönnies group company in 2025.',
      source: 'Bundeskartellamt — Tönnies / Vion decision',
      url: 'https://www.bundeskartellamt.de/SharedDocs/Meldung/DE/Pressemitteilungen/2025/06_12_2025_Vion_Toennies.html',
      boundary: 'This is a competition-law record, not an animal-welfare finding.'
    },
    {
      title: 'Exact slaughter destination', type: 'Research gap', status: 'open', confidence: 'unknown',
      claim: 'We have not yet found a public primary source proving the exact slaughterhouse destination for either named farm relationship.',
      source: 'Open research question',
      url: '',
      boundary: 'We deliberately do not infer a destination from geography, group membership or plausibility.'
    }
  ];

  const edges = [
    {
      title: 'Betrieb Mucke → Tönnies Livestock', status: 'verified', confidence: 'high',
      claim: 'A named farm relationship is publicly described by Tönnies Livestock.',
      source: 'Tönnies Livestock — Landwirtschaft im Dialog',
      url: 'https://toennies-livestock.de/landwirtschaft-im-dialog/',
      boundary: 'Relationship ≠ proof of a particular shipment or destination.'
    },
    {
      title: 'Betrieb Mertens → Tönnies Livestock', status: 'verified', confidence: 'high',
      claim: 'A named farm relationship is publicly described by Tönnies Livestock.',
      source: 'Tönnies Livestock — Landwirtschaft im Dialog',
      url: 'https://toennies-livestock.de/landwirtschaft-im-dialog/',
      boundary: 'Relationship ≠ proof of a particular shipment or destination.'
    },
    {
      title: 'Tönnies Livestock → Tönnies / PFG', status: 'verified', confidence: 'high',
      claim: 'The livestock business describes itself as part of the wider Tönnies system.',
      source: 'Tönnies Livestock — Über uns',
      url: 'https://toennies-livestock.de/ueber-uns/',
      boundary: 'This does not collapse separate legal entities into one entity.'
    },
    {
      title: 'Group → Lobbying lane', status: 'verified', confidence: 'high',
      claim: 'A group-linked central-services entity is registered in the Bundestag Lobbyregister.',
      source: 'Deutscher Bundestag — Lobbyregister R000472',
      url: 'https://www.lobbyregister.bundestag.de/suche/R000472/76599',
      boundary: 'Registered lobbying ≠ proof of causal influence on a policy outcome.'
    },
    {
      title: 'Group → Competition record', status: 'verified', confidence: 'high',
      claim: 'A Tönnies group company appears in an official Bundeskartellamt merger-control decision.',
      source: 'Bundeskartellamt',
      url: 'https://www.bundeskartellamt.de/SharedDocs/Meldung/DE/Pressemitteilungen/2025/06_12_2025_Vion_Toennies.html',
      boundary: 'Competition enforcement is a separate evidentiary lane from animal-welfare enforcement.'
    },
    {
      title: 'Farm relationship → exact slaughter destination', status: 'open', confidence: 'unknown',
      claim: 'The physical farm-to-facility hop remains unresolved in public primary sources.',
      source: 'Research gap',
      url: '',
      boundary: 'No destination is asserted until a shipment, audit, supplier-programme or facility source proves it.'
    }
  ];

  const explorer = document.createElement('div');
  explorer.className = 'graph-explorer';
  graphCard.parentNode.insertBefore(explorer, graphCard);
  explorer.appendChild(graphCard);

  const inspector = document.createElement('aside');
  inspector.className = 'evidence-inspector';
  inspector.innerHTML = `
    <div class="micro">EVIDENCE INSPECTOR</div>
    <h3>Click a node or line.</h3>
    <p class="inspector-lead">Every relationship should tell you what we know, where it comes from, and what it does <strong>not</strong> prove.</p>
    <div class="inspector-tip">Tip: the wide invisible hit-area makes the thin graph lines clickable too.</div>`;
  explorer.appendChild(inspector);

  const hint = document.createElement('div');
  hint.className = 'graph-hint';
  hint.textContent = 'Interactive · click nodes or connections';
  graphCard.prepend(hint);

  const esc = (value) => String(value || '')
    .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;').replaceAll("'", '&#039;');

  function showEvidence(item, original) {
    document.querySelectorAll('.graph .selected').forEach(el => el.classList.remove('selected'));
    if (original) original.classList.add('selected');
    const open = item.status === 'open';
    inspector.innerHTML = `
      <div class="micro">${open ? 'OPEN RESEARCH EDGE' : 'EVIDENCE RECEIPT'}</div>
      <div class="inspector-badges"><span class="badge ${open ? 'badge-open' : ''}">${esc(item.status)}</span><span class="badge badge-neutral">confidence · ${esc(item.confidence)}</span></div>
      <h3>${esc(item.title)}</h3>
      <p class="claim">${esc(item.claim)}</p>
      <div class="source"><b>Source</b><br>${esc(item.source)}${item.url ? `<br><a href="${esc(item.url)}" target="_blank" rel="noopener">Show me the receipt ↗</a>` : ''}</div>
      <div class="boundary"><b>What this does NOT prove</b><br>${esc(item.boundary)}</div>
      ${open ? '<div class="research-call">Have a primary source that closes this gap? This is exactly the evidence we are looking for.</div>' : ''}`;
  }

  const NS = 'http://www.w3.org/2000/svg';
  const originalLines = [...svg.querySelectorAll('line.edge')];
  const originalRects = [...svg.querySelectorAll('rect.node')];

  originalLines.forEach((line, i) => {
    const hit = document.createElementNS(NS, 'line');
    ['x1','y1','x2','y2'].forEach(a => hit.setAttribute(a, line.getAttribute(a)));
    hit.setAttribute('class', 'edge-hit');
    hit.setAttribute('tabindex', '0');
    hit.setAttribute('role', 'button');
    hit.setAttribute('aria-label', edges[i]?.title || 'Graph connection');
    const activate = () => showEvidence(edges[i], line);
    hit.addEventListener('click', activate);
    hit.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(); } });
    svg.appendChild(hit);
  });

  originalRects.forEach((rect, i) => {
    const hit = document.createElementNS(NS, 'rect');
    ['x','y','width','height','rx','ry'].forEach(a => { if (rect.hasAttribute(a)) hit.setAttribute(a, rect.getAttribute(a)); });
    hit.setAttribute('class', 'node-hit');
    hit.setAttribute('tabindex', '0');
    hit.setAttribute('role', 'button');
    hit.setAttribute('aria-label', nodes[i]?.title || 'Graph entity');
    const activate = () => showEvidence(nodes[i], rect);
    hit.addEventListener('click', activate);
    hit.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(); } });
    svg.appendChild(hit);
  });

  showEvidence(edges[0], originalLines[0]);
});
