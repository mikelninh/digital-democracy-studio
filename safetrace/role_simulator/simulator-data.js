window.SAFETRACE_SIMULATOR_DATA = {
  "schemaVersion": "safetrace.role-simulator/1.1",
  "release": "v1.8-companion-role-simulator-real-case-audit",
  "boundary": {
    "simulationOnly": true,
    "browserLocalState": true,
    "productionAuthentication": false,
    "realPublication": false,
    "restrictedData": false,
    "notice": "Source records, synthetic fixtures and vault-backed originals are different evidence classes. Decisions made here never alter SafeTrace records or publish anything."
  },
  "views": ["overview", "sources", "claims", "graph", "timeline", "agents", "review", "publish", "audit"],
  "roles": [
    {
      "id": "citizen", "name": "Bürger:in", "short": "Verstehen und hinterfragen",
      "description": "Prüfe politische Aussagen, Quellenstatus und Unsicherheit.", "accent": "lime",
      "allowedViews": ["overview", "sources", "claims", "graph", "timeline", "audit"],
      "allowedActions": ["inspect_source", "inspect_claim", "answer_comprehension", "flag_unclear"],
      "dailyQuestion": "Kann ich erkennen, was belegt, synthetisch, prognostiziert oder noch ungeprüft ist?"
    },
    {
      "id": "investigator", "name": "Investigator:in", "short": "Quellen und Claims aufbauen",
      "description": "Formuliere begrenzte Claims und fordere nachvollziehbare Agentenvorschläge an.", "accent": "blue",
      "allowedViews": ["overview", "sources", "claims", "graph", "timeline", "agents", "review", "audit"],
      "allowedActions": ["create_source_candidate", "draft_claim", "run_agent", "submit_for_review", "add_limitation"],
      "dailyQuestion": "Welche Aussage kann ich mit welchem exakten Beleg wirklich vertreten?"
    },
    {
      "id": "evidence_manager", "name": "Evidence Manager", "short": "Originale und Provenienz sichern",
      "description": "Prüfe Originaldatei, Hash, Abrufzeit, Content-Type und Quellenanker.", "accent": "amber",
      "allowedViews": ["overview", "sources", "claims", "timeline", "audit"],
      "allowedActions": ["approve_source", "simulate_acquisition", "verify_hash", "attach_anchor", "mark_backfill"],
      "dailyQuestion": "Existiert ein echtes Original mit Receipt oder lediglich ein Source Record?"
    },
    {
      "id": "reviewer", "name": "Skeptische:r Reviewer:in", "short": "Behauptungen zu widerlegen versuchen",
      "description": "Suche Gegenbelege, alternative Erklärungen und Übertreibungen.", "accent": "violet",
      "allowedViews": ["overview", "sources", "claims", "graph", "timeline", "agents", "review", "audit"],
      "allowedActions": ["approve_review", "request_changes", "reject_claim", "address_contradiction", "add_rationale"],
      "dailyQuestion": "Welche Quelle oder alternative Erklärung könnte den Claim schwächen?"
    },
    {
      "id": "legal_reviewer", "name": "Legal & Harm Review", "short": "Recht, Fairness und Schaden prüfen",
      "description": "Prüfe Rechtsstatus, Zuschreibung, Verhältnismäßigkeit und Schaden.", "accent": "rose",
      "allowedViews": ["overview", "sources", "claims", "graph", "timeline", "review", "publish", "audit"],
      "allowedActions": ["approve_legal", "request_redaction", "require_right_of_reply", "block_harm", "classify_legal_status"],
      "dailyQuestion": "Ist die Formulierung genauso vorsichtig wie der tatsächliche Beweisstatus?"
    },
    {
      "id": "publisher", "name": "Publisher", "short": "Nur vollständig geprüfte Aussagen freigeben",
      "description": "Kontrolliere Originale, Review-Gates, Limitationen und sichtbare Korrekturen.", "accent": "green",
      "allowedViews": ["overview", "sources", "claims", "timeline", "review", "publish", "audit"],
      "allowedActions": ["request_publication", "approve_publication", "block_publication", "mark_stale", "publish_correction"],
      "dailyQuestion": "Sind Originale, Claims und unabhängige menschliche Entscheidungen vollständig?"
    }
  ],
  "cases": [
    {
      "id": "case-001", "number": "001", "title": "GRECO: Deutschlands Antikorruptions-Versprechen",
      "subtitle": "Reale öffentliche Dokumente, aber im Simulator noch keine nachgewiesenen Original-Receipts.",
      "kind": "real source records · evidence backfill required", "language": "de",
      "summary": "Der Fall strukturiert GRECO-Empfehlungen. Frühere Simulatorangaben von 14/14 Originalen waren nicht durch Case-spezifische Vault-Receipts belegt und wurden korrigiert.",
      "question": "Welche GRECO-Empfehlungen sind dokumentiert erfüllt, teilweise erfüllt oder offen?",
      "status": "real_records_publication_blocked",
      "publication": {"allowedInSimulation": false, "label": "Publikation blockiert", "reason": "Drei Source Records sind vorhanden; Case-spezifische Originaldateien und Receipts sind im Simulator nicht nachgewiesen."},
      "readiness": {"sources": 3, "originals": 0, "claims": 3, "humanReviewed": 3, "openBlockers": 1},
      "sources": [
        {"id": "greco-evaluation", "title": "GRECO Evaluationsbericht Deutschland", "publisher": "Council of Europe / GRECO", "type": "official source record", "zone": "public", "state": "backfill_required", "anchor": "Empfehlungen und Begründungen"},
        {"id": "greco-compliance", "title": "GRECO Compliance Report", "publisher": "Council of Europe / GRECO", "type": "official source record", "zone": "public", "state": "backfill_required", "anchor": "Umsetzungsstatus je Empfehlung"},
        {"id": "german-response", "title": "Deutsche Umsetzungsdokumente", "publisher": "Bundestag / Bundesregierung", "type": "official source record", "zone": "public", "state": "backfill_required", "anchor": "Gesetzliche und organisatorische Maßnahmen"}
      ],
      "claims": [
        {"id": "c1-1", "text": "GRECO veröffentlicht überprüfbare Empfehlungen und spätere Compliance-Bewertungen zu Deutschland.", "status": "verified_repository_record", "verdict": "supported", "material": true, "supporting": ["greco-evaluation", "greco-compliance"], "contradicting": [], "limitation": "Die Originaldokumente müssen vor Neuveröffentlichung in den Vault übernommen werden.", "reviewState": "repository_consistency_only"},
        {"id": "c1-2", "text": "Formale Umsetzung beweist automatisch, dass Korruptionsrisiken praktisch beseitigt sind.", "status": "analytical_red_flag", "verdict": "rejected", "material": true, "supporting": [], "contradicting": ["greco-compliance"], "limitation": "Formale Umsetzung und praktische Wirkung müssen getrennt gemessen werden.", "reviewState": "repository_consistency_only"},
        {"id": "c1-3", "text": "Öffentliche Compliance-Berichte ermöglichen institutionelle Kontrolle.", "status": "bounded_claim", "verdict": "supported", "material": false, "supporting": ["greco-compliance", "german-response"], "contradicting": [], "limitation": "Nutzen hängt von Aktualität, Vollständigkeit und Verständlichkeit ab.", "reviewState": "repository_consistency_only"}
      ],
      "timeline": [
        {"date": "Evaluation", "title": "Empfehlungen veröffentlicht", "detail": "GRECO dokumentiert Anforderungen."},
        {"date": "Follow-up", "title": "Deutschland meldet Maßnahmen", "detail": "Umsetzungsschritte werden zugeordnet."},
        {"date": "Compliance", "title": "Umsetzung bewertet", "detail": "Status und Lücken werden dokumentiert."}
      ],
      "graph": {"nodes": [{"id":"greco","label":"GRECO","type":"institution"},{"id":"germany","label":"Deutschland","type":"jurisdiction"},{"id":"recommendations","label":"Empfehlungen","type":"policy"},{"id":"measures","label":"Maßnahmen","type":"event"}], "edges": [{"from":"greco","to":"recommendations","label":"veröffentlicht"},{"from":"recommendations","to":"germany","label":"adressiert"},{"from":"germany","to":"measures","label":"meldet"},{"from":"measures","to":"greco","label":"wird geprüft von"}]},
      "agents": [{"name":"Reader","proposal":"Ordne Empfehlungen exakten Passagen zu.","risk":"Status ohne Kontext vereinfachen"},{"name":"Chronologist","proposal":"Erstelle Dokumentversionen.","risk":"spätere Dokumente rückwirkend fehlinterpretieren"},{"name":"Skeptic","proposal":"Trenne formale Umsetzung von Wirkung.","risk":"Einzelfälle übergewichten"}],
      "tasks": {
        "citizen":["Prüfe Source Record versus Original.","Erkläre Umsetzung versus Wirkung.","Markiere eine unklare Formulierung."],
        "investigator":["Formuliere eine begrenzte Frage.","Simuliere Reader und Skeptic.","Sende einen Claim mit Limitation in Review."],
        "evidence_manager":["Prüfe die drei Source Records.","Simuliere Receipts.","Bestätige, dass der echte Backfill offen bleibt."],
        "reviewer":["Versuche den Wirkungsclaim zu widerlegen.","Adressiere Gegenargumente.","Entscheide mit Begründung."],
        "legal_reviewer":["Prüfe institutionelle Zuschreibung.","Vermeide persönliche Schuldbehauptungen.","Halte Veröffentlichung blockiert."],
        "publisher":["Kontrolliere 0/3 Originale.","Öffne den Blocker.","Dokumentiere das NO-GO."]
      },
      "comprehension": {"question":"Was beweist ein Source Record ohne Original-Receipt?","options":["Eine vollständig verifizierte Quelle","Dass eine Quelle identifiziert wurde, aber Original und Hash noch fehlen","Dass eine Person schuldig ist"],"correct":1,"explanation":"Ein Source Record ist ein Recherchehinweis, kein unveränderbarer Originalbeleg."}
    },
    {
      "id": "case-002", "number": "002", "title": "Politisches Geld: Verbindung oder gekaufte Entscheidung?",
      "subtitle": "Synthetischer Fall zur Trennung von Verbindung und Kausalität.", "kind": "synthetic training fixture", "language": "de",
      "summary": "Alle Akteure und Dokumente sind erfunden. Der Fall trainiert sichere Kausalitätssprache.",
      "question": "Welche Verbindungen sind dokumentiert, und welche Ursache ist nicht belegt?", "status": "training_ready",
      "publication": {"allowedInSimulation": true, "label": "Nur Trainingsfreigabe", "reason": "Vollständig synthetisch; keine reale Veröffentlichung."},
      "readiness": {"sources": 4, "originals": 4, "claims": 3, "humanReviewed": 3, "openBlockers": 0},
      "sources": [
        {"id":"donation-register","title":"Synthetischer Spenden-Eintrag","publisher":"Training Registry","type":"synthetic","zone":"synthetic","state":"retained","anchor":"Betrag und Datum"},
        {"id":"meeting-register","title":"Synthetischer Treffen-Eintrag","publisher":"Training Registry","type":"synthetic","zone":"synthetic","state":"retained","anchor":"Teilnehmende und Thema"},
        {"id":"policy-paper","title":"Synthetisches Positionspapier","publisher":"Organisation Alpha","type":"synthetic","zone":"synthetic","state":"retained","anchor":"Interessen"},
        {"id":"decision-record","title":"Synthetischer Beschluss","publisher":"Training Parliament","type":"synthetic","zone":"synthetic","state":"retained","anchor":"Abstimmung"}
      ],
      "claims": [
        {"id":"c2-1","text":"Eine synthetische Spende ist dokumentiert.","status":"training_fact","verdict":"supported","material":true,"supporting":["donation-register"],"contradicting":[],"limitation":"Kein realer Akteur.","reviewState":"approved_training"},
        {"id":"c2-2","text":"Ein späteres synthetisches Treffen ist dokumentiert.","status":"training_fact","verdict":"supported","material":true,"supporting":["meeting-register","policy-paper"],"contradicting":[],"limitation":"Nähe beweist keine Ursache.","reviewState":"approved_training"},
        {"id":"c2-3","text":"Die Spende kaufte den Beschluss.","status":"analytical_red_flag","verdict":"rejected","material":true,"supporting":[],"contradicting":["decision-record"],"limitation":"Keine Quelle belegt eine Gegenleistung.","reviewState":"approved_training"}
      ],
      "timeline":[{"date":"T1","title":"Spende","detail":"Synthetisch dokumentiert."},{"date":"T2","title":"Treffen","detail":"Ohne Kausalitätsaussage."},{"date":"T3","title":"Beschluss","detail":"Separat dokumentiert."}],
      "graph":{"nodes":[{"id":"a","label":"Organisation Alpha","type":"synthetic"},{"id":"b","label":"Partei Beta","type":"synthetic"},{"id":"m","label":"Treffen","type":"event"},{"id":"d","label":"Beschluss","type":"decision"}],"edges":[{"from":"a","to":"b","label":"spendete an"},{"from":"a","to":"m","label":"nahm teil"},{"from":"b","to":"m","label":"nahm teil"},{"from":"b","to":"d","label":"stimmte über"}]},
      "agents":[{"name":"Linker","proposal":"Verbinde nur mit Identifikatoren.","risk":"Namensähnlichkeit"},{"name":"Chronologist","proposal":"Zeige Reihenfolge ohne Ursache.","risk":"post hoc"},{"name":"Skeptic","proposal":"Suche alternative Gründe.","risk":"fehlende Daten überinterpretieren"}],
      "tasks":{"citizen":["Prüfe Graphkanten.","Finde den Kausalitätsfehler.","Erkläre Verbindung versus Ursache."],"investigator":["Erstelle neutrale Timeline.","Simuliere Linker.","Sende begrenzten Claim."],"evidence_manager":["Prüfe Trainingsmarker.","Simuliere Hashes.","Bestätige synthetische Zone."],"reviewer":["Versuche Kausalität zu belegen.","Dokumentiere die Lücke.","Verwerfe den Claim."],"legal_reviewer":["Prüfe Reputationsrisiko.","Verlange Nicht-Kausalität.","Bestätige synthetische Akteure."],"publisher":["Prüfe rejected Claim.","Prüfe Trainingshinweis.","Simuliere Trainingsfreigabe."]},
      "comprehension":{"question":"Was beweisen die drei Ereignisse?","options":["Eine gekaufte Entscheidung","Dokumentierte Trainingsereignisse ohne Kausalitätsbeweis","Eine Straftat"],"correct":1,"explanation":"Verbindung und Ursache bleiben getrennt."}
    },
    {
      "id": "case-003", "number": "003", "title": "Waffen: Genehmigt, geliefert oder eingesetzt?",
      "subtitle": "Synthetischer Fall zur Trennung von Entscheidungsstufen.", "kind": "synthetic training fixture", "language": "de",
      "summary": "Budget, Beschaffung, Genehmigung, Lieferung und Nutzung werden getrennt modelliert.",
      "question": "Welche Stufe ist dokumentiert und welche darf nicht abgeleitet werden?", "status": "training_ready",
      "publication": {"allowedInSimulation": true, "label": "Nur Trainingsfreigabe", "reason": "Vollständig synthetisch, keine operativen Daten."},
      "readiness": {"sources": 5, "originals": 5, "claims": 4, "humanReviewed": 4, "openBlockers": 0},
      "sources":[
        {"id":"budget-record","title":"Synthetischer Haushalt","publisher":"Training Government","type":"synthetic","zone":"synthetic","state":"retained","anchor":"Budget"},
        {"id":"procurement-record","title":"Synthetischer Vertrag","publisher":"Training Procurement","type":"synthetic","zone":"synthetic","state":"retained","anchor":"Vertrag"},
        {"id":"export-approval","title":"Synthetische Genehmigung","publisher":"Training Authority","type":"synthetic","zone":"synthetic","state":"retained","anchor":"Umfang"},
        {"id":"delivery-record","title":"Synthetischer Liefernachweis","publisher":"Training Logistics","type":"synthetic","zone":"synthetic","state":"retained","anchor":"Menge"},
        {"id":"oversight-report","title":"Synthetischer Kontrollbericht","publisher":"Training Oversight","type":"synthetic","zone":"synthetic","state":"retained","anchor":"Endverbleib"}
      ],
      "claims":[
        {"id":"c3-1","text":"Eine Exportgenehmigung wurde erteilt.","status":"training_fact","verdict":"supported","material":true,"supporting":["export-approval"],"contradicting":[],"limitation":"Noch keine Lieferung.","reviewState":"approved_training"},
        {"id":"c3-2","text":"Ein Teil wurde laut Trainingsnachweis geliefert.","status":"training_fact","verdict":"supported","material":true,"supporting":["delivery-record"],"contradicting":[],"limitation":"Keine Nutzungsaussage.","reviewState":"approved_training"},
        {"id":"c3-3","text":"Die Genehmigung beweist Konfliktnutzung.","status":"analytical_red_flag","verdict":"rejected","material":true,"supporting":[],"contradicting":["export-approval","oversight-report"],"limitation":"Nutzung benötigt eigene Belege.","reviewState":"approved_training"},
        {"id":"c3-4","text":"Endverbleibsfragen bleiben offen.","status":"unresolved_gap","verdict":"supported","material":false,"supporting":["oversight-report"],"contradicting":[],"limitation":"Offene Frage ist kein Missbrauchsbeweis.","reviewState":"approved_training"}
      ],
      "timeline":[{"date":"T1","title":"Budget","detail":"Finanzielle Ermächtigung."},{"date":"T2","title":"Beschaffung","detail":"Vertrag."},{"date":"T3","title":"Genehmigung","detail":"Noch keine Lieferung."},{"date":"T4","title":"Lieferung","detail":"Noch keine Nutzung."},{"date":"T5","title":"Kontrolle","detail":"Offene Fragen."}],
      "graph":{"nodes":[{"id":"authority","label":"Behörde","type":"synthetic"},{"id":"company","label":"Hersteller","type":"synthetic"},{"id":"approval","label":"Genehmigung","type":"decision"},{"id":"delivery","label":"Lieferung","type":"event"},{"id":"use","label":"Nutzung","type":"unverified"}],"edges":[{"from":"authority","to":"approval","label":"erteilt"},{"from":"approval","to":"company","label":"betrifft"},{"from":"company","to":"delivery","label":"liefert"},{"from":"delivery","to":"use","label":"beweist NICHT"}]},
      "agents":[{"name":"Legal Status","proposal":"Klassifiziere jede Stufe.","risk":"Stufen vermischen"},{"name":"Guardian","proposal":"Entferne operative Details.","risk":"Gefährdung"},{"name":"Skeptic","proposal":"Suche Einschränkungen.","risk":"Abwesenheit als Gegenbeweis"}],
      "tasks":{"citizen":["Ordne Stufen.","Prüfe rejected Claim.","Erkläre offene Frage."],"investigator":["Erstelle Events.","Simuliere Agents.","Formuliere sicheren Claim."],"evidence_manager":["Prüfe Anker getrennt.","Simuliere Hashes.","Bestätige keine Live-Daten."],"reviewer":["Prüfe unzulässige Ableitung.","Adressiere Kontext.","Entscheide mit Rationale."],"legal_reviewer":["Klassifiziere Status.","Prüfe Gefährdung.","Blockiere Übertreibung."],"publisher":["Prüfe Stufentrennung.","Prüfe keine operativen Details.","Simuliere Trainingsfreigabe."]},
      "comprehension":{"question":"Was folgt aus einer Exportgenehmigung?","options":["Lieferung","Behördliche Erlaubnis; Lieferung und Nutzung brauchen eigene Belege","Rechtswidrige Nutzung"],"correct":1,"explanation":"Jede Stufe braucht einen eigenen Beleg."}
    },
    {
      "id": "case-004", "number": "004", "title": "Gesetzes-Fairness: Macht Merz Politik für Reiche?",
      "subtitle": "Realer Repository-Referenzfall mit fehlenden Originaldateien.", "kind": "real reviewed records · 0/11 originals", "language": "de",
      "summary": "Unternehmensentlastungen, Grundsicherung und Familienleistungen werden verglichen. Die Source Records sind real; eine neue SafeTrace-Publikation ist nicht zertifiziert.",
      "question": "Welche Maßnahmen entlasten Unternehmen, welche verschärfen Bedingungen und welche Zuschreibungen sind falsch?", "status": "technical_reference_publication_blocked",
      "publication": {"allowedInSimulation": false, "label": "Publikation blockiert", "reason": "Elf Source Records, aber 0/11 unveränderte Originaldateien im Case-004-Evidence-Vault."},
      "readiness": {"sources": 11, "originals": 0, "claims": 5, "humanReviewed": 5, "openBlockers": 3},
      "sources":[
        {"id":"bundestag-investment","title":"Investitionsprogramm","publisher":"Deutscher Bundestag","type":"official source record","zone":"public","state":"backfill_required","anchor":"Gesetz und Abstimmung"},
        {"id":"bmf-programme","title":"BMF-Unternehmensentlastungen","publisher":"BMF","type":"official source record","zone":"public","state":"backfill_required","anchor":"Abschreibung und Körperschaftsteuer"},
        {"id":"bmas-security","title":"Grundsicherung und Regelsätze","publisher":"BMAS","type":"official source record","zone":"public","state":"backfill_required","anchor":"Pflichten und Regelsätze"},
        {"id":"bundestag-family","title":"Familienleistung 2024","publisher":"Deutscher Bundestag","type":"official source record","zone":"public","state":"backfill_required","anchor":"Beschlusszeitpunkt"},
        {"id":"ifo-analysis","title":"Ökonomische Analyse","publisher":"ifo Institut","type":"analysis record","zone":"public","state":"backfill_required","anchor":"Modellwirkungen"}
      ],
      "claims":[
        {"id":"c4-1","text":"Die Regierung Merz beschloss erhebliche Unternehmensentlastungen.","status":"repository_reviewed","verdict":"supported","material":true,"supporting":["bundestag-investment","bmf-programme","ifo-analysis"],"contradicting":[],"limitation":"Langzeitverteilung nicht gemessen.","reviewState":"repository_consistency_only"},
        {"id":"c4-2","text":"Merz kürzte 2026 Regelsätze nominal.","status":"repository_reviewed","verdict":"not_supported","material":true,"supporting":[],"contradicting":["bmas-security"],"limitation":"Nominal unverändert ist nicht reale Kaufkraftstabilität.","reviewState":"repository_consistency_only"},
        {"id":"c4-3","text":"Neue Regeln erhöhen Pflichten und mögliche finanzielle Risiken.","status":"repository_reviewed","verdict":"supported","material":true,"supporting":["bmas-security"],"contradicting":[],"limitation":"Reale Wirkung muss gemessen werden.","reviewState":"repository_consistency_only"},
        {"id":"c4-4","text":"Die Merz-Regierung beschloss die Kindergelderhöhung 2026.","status":"repository_reviewed","verdict":"not_supported","material":true,"supporting":[],"contradicting":["bundestag-family"],"limitation":"Beschluss erfolgte 2024.","reviewState":"repository_consistency_only"},
        {"id":"c4-5","text":"Merz macht ausschließlich Politik für Reiche.","status":"analytical_red_flag","verdict":"partly_supported","material":true,"supporting":["bundestag-investment","bmf-programme","bmas-security"],"contradicting":["bundestag-family"],"limitation":"Ausschließlich ist nicht gedeckt.","reviewState":"repository_consistency_only"}
      ],
      "timeline":[{"date":"Dez. 2024","title":"Kindergeld beschlossen","detail":"Vor Merz-Regierung."},{"date":"Juli 2025","title":"Abschreibung","detail":"Unternehmensentlastung."},{"date":"Jan. 2026","title":"259 Euro","detail":"Inkrafttreten."},{"date":"Juli 2026","title":"Grundsicherung","detail":"Strengere Pflichten."},{"date":"2028–2032","title":"Körperschaftsteuer","detail":"Schrittweise Senkung."}],
      "graph":{"nodes":[{"id":"government","label":"Regierung Merz","type":"government"},{"id":"business","label":"Unternehmen","type":"group"},{"id":"security","label":"Grundsicherung","type":"group"},{"id":"families","label":"Familien","type":"group"},{"id":"prior","label":"Vorherige Legislatur","type":"government"}],"edges":[{"from":"government","to":"business","label":"entlastet"},{"from":"government","to":"security","label":"verschärft Bedingungen"},{"from":"prior","to":"families","label":"beschloss Erhöhung"},{"from":"government","to":"families","label":"nicht Urheber dieses Beschlusses"}]},
      "agents":[{"name":"Quant","proposal":"Trenne direkt und modelliert.","risk":"Prognose als Wirkung"},{"name":"Legal Status","proposal":"Trenne beschlossen und in Kraft.","risk":"Urheberschaft verwechseln"},{"name":"Skeptic","proposal":"Prüfe ausschließlich.","risk":"Gegenmaßnahme übergewichten"},{"name":"Guardian","proposal":"Kein moralischer Gesamtscore.","risk":"Werturteil als Messung"}],
      "tasks":{"citizen":["Vergleiche Verdikte.","Prüfe Attribution.","Markiere fehlende Information."],"investigator":["Prüfe Source IDs.","Simuliere Agents.","Sende Claim zur Review."],"evidence_manager":["Prüfe 0/11.","Simuliere eine Acquisition.","Behalte Gesamtblocker."],"reviewer":["Prüfe ausschließlich.","Trenne nominal und real.","Entscheide ohne Originale zu ignorieren."],"legal_reviewer":["Prüfe Zuschreibung.","Keine Korruption behaupten.","Blockiere Neuveröffentlichung."],"publisher":["Kontrolliere 0/11.","Öffne Blocker.","Dokumentiere NO-GO."]},
      "comprehension":{"question":"Warum ist die Kindergelderhöhung nicht Merz zuzurechnen?","options":["Familien profitieren nie","Sie wurde 2024 beschlossen und 2026 wirksam","Kindergeld ist kein Gesetz"],"correct":1,"explanation":"Inkrafttreten und Urheberschaft sind getrennt."}
    },
    {
      "id": "case-005", "number": "005", "title": "Wer beschloss die Kindergelderhöhung auf 259 Euro?",
      "subtitle": "Erster echter Live-Source-Publikationskandidat.", "kind": "real official-source candidate", "language": "de",
      "summary": "Vier amtliche Primärquellen werden live abgerufen, gehasht und zu vier vault-backed Claims verbunden. Bis CI-Acquisition und deine drei Review-Gates abgeschlossen sind, bleibt der Fall blockiert.",
      "question": "Beschloss die Regierung Merz die Erhöhung oder lag der Beschluss vor ihrem Amtsantritt?", "status": "live_acquisition_and_human_review_pending",
      "publication": {"allowedInSimulation": false, "label": "Review-Kandidat", "reason": "Live-Receipts und Named Human Evidence-, Red-Team- und Publication-Review müssen erfolgreich abgeschlossen sein."},
      "readiness": {"sources": 4, "originals": 0, "claims": 4, "humanReviewed": 0, "openBlockers": 2},
      "sources":[
        {"id":"case005-bundestag-decision-2024","title":"Bundestagsbeschluss vom 19. Dezember 2024","publisher":"Deutscher Bundestag","type":"primary official · live acquisition","zone":"public","state":"backfill_required","anchor":"Beschlussdatum, 259 Euro, Wirkung ab 1. Januar 2026"},
        {"id":"case005-bundesregierung-implementation-2026","title":"Neuregelungen Januar 2026","publisher":"Bundesregierung","type":"primary official · live acquisition","zone":"public","state":"backfill_required","anchor":"259 Euro ab Januar 2026"},
        {"id":"case005-bkgg-current-law","title":"BKGG § 6","publisher":"Bundesministerium der Justiz / Bundesamt für Justiz","type":"primary official · live acquisition","zone":"public","state":"backfill_required","anchor":"259 Euro pro Kind und Monat"},
        {"id":"case005-merz-government-start","title":"Beginn der Regierung Merz","publisher":"Bundesregierung","type":"primary official · live acquisition","zone":"public","state":"backfill_required","anchor":"Amtsbeginn 6. Mai 2025"}
      ],
      "claims":[
        {"id":"c5-1","text":"Das Kindergeld beträgt seit 1. Januar 2026 monatlich 259 Euro.","status":"live_verification_pending","verdict":"supported","material":true,"supporting":["case005-bundesregierung-implementation-2026","case005-bkgg-current-law"],"contradicting":[],"limitation":"Betrag und Inkrafttreten sagen noch nichts über Urheberschaft.","reviewState":"awaiting_live_receipts"},
        {"id":"c5-2","text":"Der Bundestag beschloss die Erhöhung am 19. Dezember 2024.","status":"live_verification_pending","verdict":"supported","material":true,"supporting":["case005-bundestag-decision-2024"],"contradicting":[],"limitation":"Beschluss wird getrennt von späterer Umsetzung bewertet.","reviewState":"awaiting_live_receipts"},
        {"id":"c5-3","text":"Die Regierung Merz trat am 6. Mai 2025 ihr Amt an.","status":"live_verification_pending","verdict":"supported","material":true,"supporting":["case005-merz-government-start"],"contradicting":[],"limitation":"Amtsbeginn bewertet keine sonstige Familienpolitik.","reviewState":"awaiting_live_receipts"},
        {"id":"c5-4","text":"Die Erhöhung auf 259 Euro war keine neu beschlossene Maßnahme der Regierung Merz.","status":"live_verification_pending","verdict":"supported","material":true,"supporting":["case005-bundestag-decision-2024","case005-merz-government-start","case005-bundesregierung-implementation-2026"],"contradicting":[],"limitation":"Die Merz-Regierung administriert geltendes Recht; andere Maßnahmen sind separat zu prüfen.","reviewState":"awaiting_live_receipts"}
      ],
      "timeline":[{"date":"19.12.2024","title":"Bundestagsbeschluss","detail":"Erhöhung mit Wirkung zum 1. Januar 2026."},{"date":"06.05.2025","title":"Regierung Merz beginnt","detail":"Nach dem Beschluss."},{"date":"01.01.2026","title":"259 Euro treten in Kraft","detail":"Auszahlung und Gesetzeshöhe."}],
      "graph":{"nodes":[{"id":"bundestag","label":"Deutscher Bundestag","type":"institution"},{"id":"decision","label":"Beschluss 19.12.2024","type":"decision"},{"id":"merz","label":"Regierung Merz","type":"government"},{"id":"effective","label":"259 Euro ab 01.01.2026","type":"measure"}],"edges":[{"from":"bundestag","to":"decision","label":"beschließt"},{"from":"decision","to":"effective","label":"wird wirksam"},{"from":"merz","to":"effective","label":"administriert geltendes Recht"}]},
      "agents":[{"name":"Reader","proposal":"Prüfe Pflichtpassagen live.","risk":"Seitenänderung"},{"name":"Legal Status","proposal":"Trenne Beschluss, Amtsbeginn und Inkrafttreten.","risk":"Attribution"},{"name":"Skeptic","proposal":"Suche alternative Urheberschaftsdeutung.","risk":"Verwaltung mit Gesetzgebung verwechseln"},{"name":"Guardian","proposal":"Begrenze Verdict auf diese Maßnahme.","risk":"Pauschalurteil"}],
      "tasks":{"citizen":["Prüfe die Timeline.","Beantworte Attribution.","Bewerte Verständlichkeit."],"investigator":["Prüfe vier Quellenmarker.","Simuliere Agents.","Sende Claims zur Review."],"evidence_manager":["Warte auf Live-CI-Receipts.","Vergleiche Hashes.","Prüfe genaue Anker."],"reviewer":["Prüfe alle vier Claims.","Suche Gegenargumente.","Gib Rationale ab."],"legal_reviewer":["Prüfe politische Zuschreibung.","Begrenze auf diese Maßnahme.","Prüfe keine Reputationsübertreibung."],"publisher":["Verlange 4/4 Receipts.","Verlange 12/12 Review-Gates.","Blockiere bis alles erfüllt ist."]},
      "comprehension":{"question":"Wer beschloss die Erhöhung auf 259 Euro?","options":["Regierung Merz im Jahr 2026","Der Bundestag am 19. Dezember 2024","Unbekannt"],"correct":1,"explanation":"Der Beschluss lag vor dem Amtsantritt der Regierung Merz; wirksam wurde er 2026."}
    }
  ]
};
