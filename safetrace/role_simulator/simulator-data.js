window.SAFETRACE_SIMULATOR_DATA = {
  "schemaVersion": "safetrace.role-simulator/1.0",
  "release": "v1.8-companion-role-simulator",
  "boundary": {
    "simulationOnly": true,
    "browserLocalState": true,
    "productionAuthentication": false,
    "realPublication": false,
    "restrictedData": false,
    "notice": "Public-source and synthetic training simulation. Decisions made here never alter SafeTrace records or publish anything."
  },
  "views": ["overview", "sources", "claims", "graph", "timeline", "agents", "review", "publish", "audit"],
  "roles": [
    {
      "id": "citizen",
      "name": "Bürger:in",
      "short": "Verstehen und hinterfragen",
      "description": "Prüfe politische Aussagen, öffne Quellen und teste, ob Status, Zuschreibung und Unsicherheit verständlich sind.",
      "accent": "lime",
      "allowedViews": ["overview", "sources", "claims", "graph", "timeline", "audit"],
      "allowedActions": ["inspect_source", "inspect_claim", "answer_comprehension", "flag_unclear"],
      "dailyQuestion": "Kann ich erkennen, was belegt, prognostiziert oder wertend ist?"
    },
    {
      "id": "investigator",
      "name": "Investigator:in",
      "short": "Quellen und Claims aufbauen",
      "description": "Strukturiere Recherchefragen, fordere Agentenvorschläge an und sende präzise Claims in die menschliche Review-Warteschlange.",
      "accent": "blue",
      "allowedViews": ["overview", "sources", "claims", "graph", "timeline", "agents", "review", "audit"],
      "allowedActions": ["create_source_candidate", "draft_claim", "run_agent", "submit_for_review", "add_limitation"],
      "dailyQuestion": "Welche Behauptung kann ich mit welchem exakten Beleg wirklich vertreten?"
    },
    {
      "id": "evidence_manager",
      "name": "Evidence Manager",
      "short": "Originale und Provenienz sichern",
      "description": "Prüfe Quellenidentität, Originaldatei, Hash, Abrufzeit, Content-Type und genaue Anker, bevor Evidenz nutzbar wird.",
      "accent": "amber",
      "allowedViews": ["overview", "sources", "claims", "timeline", "audit"],
      "allowedActions": ["approve_source", "simulate_acquisition", "verify_hash", "attach_anchor", "mark_backfill"],
      "dailyQuestion": "Könnte eine unabhängige Person exakt dieselbe Quelle und Passage wiederfinden?"
    },
    {
      "id": "reviewer",
      "name": "Skeptische:r Reviewer:in",
      "short": "Behauptungen zu widerlegen versuchen",
      "description": "Vergleiche supporting und contradicting evidence, verlange Einschränkungen und entscheide unabhängig vom ursprünglichen Autor.",
      "accent": "violet",
      "allowedViews": ["overview", "sources", "claims", "graph", "timeline", "agents", "review", "audit"],
      "allowedActions": ["approve_review", "request_changes", "reject_claim", "address_contradiction", "add_rationale"],
      "dailyQuestion": "Welche alternative Erklärung oder Gegenquelle könnte diesen Claim schwächen?"
    },
    {
      "id": "legal_reviewer",
      "name": "Legal & Harm Review",
      "short": "Recht, Fairness und Schaden prüfen",
      "description": "Prüfe Rechtsstatus, Identität, Notwendigkeit, Verhältnismäßigkeit, personenbezogene Daten und gegebenenfalls Right of Reply.",
      "accent": "rose",
      "allowedViews": ["overview", "sources", "claims", "graph", "timeline", "review", "publish", "audit"],
      "allowedActions": ["approve_legal", "request_redaction", "require_right_of_reply", "block_harm", "classify_legal_status"],
      "dailyQuestion": "Ist die Formulierung genauso vorsichtig wie der tatsächliche Beweisstatus?"
    },
    {
      "id": "publisher",
      "name": "Publisher",
      "short": "Nur vollständig geprüfte Aussagen freigeben",
      "description": "Kontrolliere alle Gates, Unterschiede zur vorherigen Version, sichtbare Korrekturen und die Trennung interner und öffentlicher Daten.",
      "accent": "green",
      "allowedViews": ["overview", "sources", "claims", "timeline", "review", "publish", "audit"],
      "allowedActions": ["request_publication", "approve_publication", "block_publication", "mark_stale", "publish_correction"],
      "dailyQuestion": "Sind alle materiellen Claims reproduzierbar geprüft und alle Grenzen für die Öffentlichkeit sichtbar?"
    }
  ],
  "cases": [
    {
      "id": "case-001",
      "number": "001",
      "title": "GRECO: Deutschlands Antikorruptions-Versprechen",
      "subtitle": "Welche Empfehlungen sind dokumentiert, umgesetzt oder weiterhin offen?",
      "kind": "public-record reference",
      "language": "de",
      "summary": "Der Referenzfall strukturiert 14 GRECO-Empfehlungen als überprüfbare Aufgaben mit Quellen, Status und Grenzen. Er bewertet institutionelle Umsetzung, nicht die persönliche Schuld einzelner Menschen.",
      "question": "Welche GRECO-Empfehlungen an Deutschland sind anhand öffentlicher Dokumente nachweisbar erfüllt, teilweise erfüllt oder offen?",
      "status": "reviewed_public_pack",
      "publication": {"allowedInSimulation": true, "label": "Trainingsfreigabe möglich", "reason": "Öffentlich redigierter Referenzfall; die Simulation verändert keine echte Veröffentlichung."},
      "readiness": {"sources": 14, "originals": 14, "claims": 3, "humanReviewed": 3, "openBlockers": 0},
      "sources": [
        {"id": "greco-evaluation", "title": "GRECO Evaluationsbericht Deutschland", "publisher": "Council of Europe / GRECO", "type": "primary", "zone": "public", "state": "retained", "anchor": "Empfehlungen und Begründungen"},
        {"id": "greco-compliance", "title": "GRECO Compliance Report", "publisher": "Council of Europe / GRECO", "type": "primary", "zone": "public", "state": "retained", "anchor": "Umsetzungsstatus je Empfehlung"},
        {"id": "german-response", "title": "Deutsche Umsetzungs- und Gesetzesdokumente", "publisher": "Bundestag / Bundesregierung", "type": "primary", "zone": "public", "state": "retained", "anchor": "Gesetzliche und organisatorische Maßnahmen"}
      ],
      "claims": [
        {"id": "c1-1", "text": "Der Fall verfolgt 14 öffentlich dokumentierte GRECO-Empfehlungen.", "status": "verified_fact", "verdict": "supported", "material": true, "supporting": ["greco-evaluation", "greco-compliance"], "contradicting": [], "limitation": "Die Anzahl allein sagt nichts über Qualität oder Wirksamkeit der Umsetzung aus.", "reviewState": "approved"},
        {"id": "c1-2", "text": "Ein formell umgesetzter Schritt beweist automatisch, dass Korruptionsrisiken praktisch beseitigt sind.", "status": "analytical_red_flag", "verdict": "not_supported", "material": true, "supporting": [], "contradicting": ["greco-compliance"], "limitation": "Formale Umsetzung und praktische Wirkung müssen getrennt gemessen werden.", "reviewState": "approved"},
        {"id": "c1-3", "text": "Öffentliche Fortschrittsberichte erlauben eine nachvollziehbare institutionelle Kontrolle.", "status": "verified_fact", "verdict": "supported", "material": false, "supporting": ["greco-compliance", "german-response"], "contradicting": [], "limitation": "Transparenz hängt von Aktualität, Vollständigkeit und Vergleichbarkeit der Berichte ab.", "reviewState": "approved"}
      ],
      "timeline": [
        {"date": "Evaluation", "title": "Empfehlungen veröffentlicht", "detail": "GRECO dokumentiert Anforderungen und Begründungen."},
        {"date": "Follow-up", "title": "Deutschland meldet Maßnahmen", "detail": "Gesetze und organisatorische Schritte werden zugeordnet."},
        {"date": "Compliance", "title": "Umsetzung wird bewertet", "detail": "Status und verbleibende Lücken werden dokumentiert."}
      ],
      "graph": {
        "nodes": [
          {"id": "greco", "label": "GRECO", "type": "institution"},
          {"id": "germany", "label": "Deutschland", "type": "jurisdiction"},
          {"id": "recommendations", "label": "14 Empfehlungen", "type": "policy"},
          {"id": "measures", "label": "Umsetzungsmaßnahmen", "type": "event"}
        ],
        "edges": [
          {"from": "greco", "to": "recommendations", "label": "veröffentlicht"},
          {"from": "recommendations", "to": "germany", "label": "adressiert"},
          {"from": "germany", "to": "measures", "label": "meldet"},
          {"from": "measures", "to": "greco", "label": "wird geprüft von"}
        ]
      },
      "agents": [
        {"name": "Reader", "proposal": "Ordne jede Empfehlung dem exakten Compliance-Abschnitt zu.", "risk": "Status ohne Kontext vereinfachen"},
        {"name": "Chronologist", "proposal": "Erstelle eine Versionstimeline je Empfehlung.", "risk": "spätere Dokumente rückwirkend fehlinterpretieren"},
        {"name": "Skeptic", "proposal": "Suche Fälle, in denen formale Umsetzung keine praktische Wirkung zeigt.", "risk": "anekdotische Gegenbeispiele übergewichten"}
      ],
      "tasks": {
        "citizen": ["Öffne einen unterstützten und einen nicht unterstützten Claim.", "Erkläre den Unterschied zwischen formaler Umsetzung und Wirkung.", "Markiere eine Formulierung als unklar oder verständlich."],
        "investigator": ["Wähle eine Empfehlung und formuliere eine begrenzte Forschungsfrage.", "Lass Reader und Chronologist Vorschläge erzeugen.", "Sende einen Claim mit sichtbarer Limitation in Review."],
        "evidence_manager": ["Prüfe Publisher, Content-Type und Anker der Compliance-Quelle.", "Simuliere Hash-Verifikation und hänge den Quellenanker an.", "Bestätige, dass keine vertraulichen Daten benötigt werden."],
        "reviewer": ["Versuche den Wirkungs-Claim zu widerlegen.", "Adressiere mindestens eine alternative Erklärung.", "Genehmige, ändere oder verwerfe mit Begründung."],
        "legal_reviewer": ["Prüfe, ob Institutionen oder Personen unangemessen beschuldigt werden.", "Bestätige die Trennung von Empfehlung, Status und Schuld.", "Gib den Claim frei oder verlange eine vorsichtigere Formulierung."],
        "publisher": ["Kontrolliere 3/3 Human Reviews und Quellenabdeckung.", "Prüfe den öffentlichen Diff und die sichtbaren Limitationen.", "Führe eine simulierte Trainingsfreigabe durch."]
      },
      "comprehension": {"question": "Was beweist ein Status ‚formal umgesetzt‘?", "options": ["Dass jede Korruptionsgefahr beseitigt ist", "Dass ein dokumentierter Umsetzungsschritt vorliegt, dessen Wirkung separat geprüft werden muss", "Dass eine Person schuldig ist"], "correct": 1, "explanation": "SafeTrace trennt formale Umsetzung, tatsächliche Wirkung und persönliche Verantwortung."}
    },
    {
      "id": "case-002",
      "number": "002",
      "title": "Politisches Geld: Dokumentierte Verbindung oder gekaufte Entscheidung?",
      "subtitle": "Spenden, Treffen und Interessen darstellen, ohne Kausalität zu erfinden.",
      "kind": "synthetic training fixture",
      "language": "de",
      "summary": "Ein synthetischer Übungsfall zeigt, wie dokumentierte Beziehungen als Graph erfasst werden, während die unbelegte Behauptung einer gekauften politischen Entscheidung ausdrücklich zurückgewiesen wird.",
      "question": "Welche Verbindungen sind dokumentiert, und welche kausalen Schlussfolgerungen wären durch die vorhandenen Quellen nicht gedeckt?",
      "status": "training_ready",
      "publication": {"allowedInSimulation": true, "label": "Redigierte Trainingsfreigabe möglich", "reason": "Alle Personen und Organisationen sind synthetisch; Kausalität wird ausdrücklich nicht behauptet."},
      "readiness": {"sources": 4, "originals": 4, "claims": 3, "humanReviewed": 3, "openBlockers": 0},
      "sources": [
        {"id": "donation-register", "title": "Synthetischer Parteispenden-Eintrag", "publisher": "Training Registry", "type": "structured_record", "zone": "synthetic", "state": "retained", "anchor": "Betrag, Datum, Empfänger"},
        {"id": "meeting-register", "title": "Synthetischer Treffen-Eintrag", "publisher": "Training Registry", "type": "structured_record", "zone": "synthetic", "state": "retained", "anchor": "Teilnehmende, Datum, Thema"},
        {"id": "policy-paper", "title": "Synthetisches Positionspapier", "publisher": "Organisation Alpha", "type": "secondary", "zone": "synthetic", "state": "retained", "anchor": "deklarierte politische Interessen"},
        {"id": "decision-record", "title": "Synthetischer Beschluss", "publisher": "Training Parliament", "type": "primary", "zone": "synthetic", "state": "retained", "anchor": "Beschlusstext und Abstimmung"}
      ],
      "claims": [
        {"id": "c2-1", "text": "Eine Spende von Organisation Alpha an Partei Beta ist im Trainingsregister dokumentiert.", "status": "verified_fact", "verdict": "supported", "material": true, "supporting": ["donation-register"], "contradicting": [], "limitation": "Der Eintrag beweist weder Gegenleistung noch Einfluss.", "reviewState": "approved"},
        {"id": "c2-2", "text": "Ein späteres Treffen zu demselben Politikfeld ist dokumentiert.", "status": "verified_fact", "verdict": "supported", "material": true, "supporting": ["meeting-register", "policy-paper"], "contradicting": [], "limitation": "Zeitliche oder thematische Nähe beweist keine Ursache.", "reviewState": "approved"},
        {"id": "c2-3", "text": "Die Spende kaufte den späteren Beschluss.", "status": "analytical_red_flag", "verdict": "rejected", "material": true, "supporting": [], "contradicting": ["decision-record"], "limitation": "Es gibt keine Quelle, die eine Gegenleistung oder kausale Steuerung belegt.", "reviewState": "approved"}
      ],
      "timeline": [
        {"date": "T1", "title": "Spende dokumentiert", "detail": "Betrag und Empfänger werden als Fakt erfasst."},
        {"date": "T2", "title": "Treffen dokumentiert", "detail": "Thema und Beteiligte werden ohne Kausalitätsaussage gespeichert."},
        {"date": "T3", "title": "Beschluss dokumentiert", "detail": "Abstimmung und Inhalt werden separat erfasst."}
      ],
      "graph": {
        "nodes": [
          {"id": "alpha", "label": "Organisation Alpha", "type": "organisation"},
          {"id": "beta", "label": "Partei Beta", "type": "party"},
          {"id": "meeting", "label": "Dokumentiertes Treffen", "type": "event"},
          {"id": "decision", "label": "Späterer Beschluss", "type": "decision"}
        ],
        "edges": [
          {"from": "alpha", "to": "beta", "label": "spendete an"},
          {"from": "alpha", "to": "meeting", "label": "nahm teil"},
          {"from": "beta", "to": "meeting", "label": "nahm teil"},
          {"from": "beta", "to": "decision", "label": "stimmte über"}
        ]
      },
      "agents": [
        {"name": "Linker", "proposal": "Verbinde Einträge nur über zwei unabhängige Identifikatoren.", "risk": "ähnliche Namen fälschlich zusammenführen"},
        {"name": "Chronologist", "proposal": "Zeige Reihenfolge ohne Ursache-Pfeil.", "risk": "zeitliche Nähe als Einfluss darstellen"},
        {"name": "Skeptic", "proposal": "Suche alternative Gründe für den Beschluss.", "risk": "fehlende Daten als Beweis der Unschuld missverstehen"}
      ],
      "tasks": {
        "citizen": ["Öffne den Graphen und lies alle Kantenbeschriftungen.", "Entscheide, welcher Claim eine unzulässige Kausalität behauptet.", "Erkläre den Unterschied zwischen Verbindung und Einflussbeweis."],
        "investigator": ["Erstelle eine Timeline ohne kausale Sprache.", "Lass Linker einen unsicheren Match vorschlagen und lehne Überkonfidenz ab.", "Sende einen begrenzten Verbindungs-Claim in Review."],
        "evidence_manager": ["Prüfe Datum, Betrag und Registeranker.", "Simuliere die Hash-Prüfung aller vier Trainingsquellen.", "Kennzeichne sämtliche Daten klar als synthetisch."],
        "reviewer": ["Versuche den gekauften-Beschluss-Claim mit den vorhandenen Quellen zu belegen.", "Dokumentiere, warum der Belegpfad nicht reicht.", "Verwerfe den Kausalitäts-Claim mit Rationale."],
        "legal_reviewer": ["Prüfe die reputationsschädigende Wirkung der Kausalitätsbehauptung.", "Verlange explizite Nicht-Kausalitäts-Sprache.", "Bestätige, dass nur synthetische Akteure verwendet werden."],
        "publisher": ["Prüfe, dass der abgelehnte Claim nicht als Fakt erscheint.", "Kontrolliere den Hinweis ‚synthetischer Trainingsfall‘.", "Führe eine redigierte Trainingsfreigabe durch."]
      },
      "comprehension": {"question": "Was beweisen Spende, Treffen und späterer Beschluss gemeinsam?", "options": ["Automatisch eine gekaufte Entscheidung", "Dokumentierte Ereignisse, die eine weitere Untersuchung rechtfertigen können, aber allein keine Kausalität beweisen", "Automatisch einen Straftatbestand"], "correct": 1, "explanation": "Ereignisse und Beziehungen werden dokumentiert; Einfluss oder Rechtsverstoß brauchen zusätzliche Belege."}
    },
    {
      "id": "case-003",
      "number": "003",
      "title": "Waffen & Einfluss: Genehmigt, beschafft, geliefert oder eingesetzt?",
      "subtitle": "Entscheidungsstufen sauber trennen und gefährliche Übertreibungen blockieren.",
      "kind": "synthetic training fixture",
      "language": "de",
      "summary": "Der Übungsfall trennt politische Position, Budget, Beschaffung, Exportgenehmigung, tatsächliche Lieferung, Endverbleib und mögliche Nutzung. Keine Stufe wird automatisch aus einer anderen abgeleitet.",
      "question": "Welche Stufe ist dokumentiert, und welche spätere Stufe darf daraus noch nicht als Fakt behauptet werden?",
      "status": "training_ready",
      "publication": {"allowedInSimulation": true, "label": "Redigierte Trainingsfreigabe möglich", "reason": "Synthetische Daten, keine Live-Positionen und keine gefährdeten Personen."},
      "readiness": {"sources": 5, "originals": 5, "claims": 4, "humanReviewed": 4, "openBlockers": 0},
      "sources": [
        {"id": "budget-record", "title": "Synthetischer Haushaltsbeschluss", "publisher": "Training Government", "type": "primary", "zone": "synthetic", "state": "retained", "anchor": "Budgettitel"},
        {"id": "procurement-record", "title": "Synthetischer Beschaffungsvertrag", "publisher": "Training Procurement Office", "type": "primary", "zone": "synthetic", "state": "retained", "anchor": "Vertragsgegenstand"},
        {"id": "export-approval", "title": "Synthetische Exportgenehmigung", "publisher": "Training Authority", "type": "primary", "zone": "synthetic", "state": "retained", "anchor": "Genehmigungsumfang"},
        {"id": "delivery-record", "title": "Synthetischer Liefernachweis", "publisher": "Training Logistics", "type": "primary", "zone": "synthetic", "state": "retained", "anchor": "Lieferdatum und Menge"},
        {"id": "oversight-report", "title": "Synthetischer Kontrollbericht", "publisher": "Training Oversight Body", "type": "primary", "zone": "synthetic", "state": "retained", "anchor": "Endverbleib und Grenzen"}
      ],
      "claims": [
        {"id": "c3-1", "text": "Für System A wurde eine Exportgenehmigung erteilt.", "status": "verified_fact", "verdict": "supported", "material": true, "supporting": ["export-approval"], "contradicting": [], "limitation": "Eine Genehmigung ist noch kein Liefernachweis.", "reviewState": "approved"},
        {"id": "c3-2", "text": "Ein Teil der genehmigten Menge wurde später geliefert.", "status": "verified_fact", "verdict": "supported", "material": true, "supporting": ["delivery-record"], "contradicting": [], "limitation": "Der Nachweis sagt nichts über konkrete Nutzung aus.", "reviewState": "approved"},
        {"id": "c3-3", "text": "Die Exportgenehmigung beweist, dass das System im Konflikt eingesetzt wurde.", "status": "analytical_red_flag", "verdict": "rejected", "material": true, "supporting": [], "contradicting": ["export-approval", "oversight-report"], "limitation": "Für eine Nutzungsaussage wären unabhängige, genaue und nicht taktisch gefährliche Belege nötig.", "reviewState": "approved"},
        {"id": "c3-4", "text": "Der Kontrollbericht enthält offene Fragen zum Endverbleib.", "status": "unresolved_gap", "verdict": "supported", "material": false, "supporting": ["oversight-report"], "contradicting": [], "limitation": "Eine offene Frage ist weder Beweis für Missbrauch noch Beweis für ordnungsgemäße Nutzung.", "reviewState": "approved"}
      ],
      "timeline": [
        {"date": "T1", "title": "Budgetentscheidung", "detail": "Finanzielle Ermächtigung wird dokumentiert."},
        {"date": "T2", "title": "Beschaffung", "detail": "Vertrag wird separat vom Export erfasst."},
        {"date": "T3", "title": "Exportgenehmigung", "detail": "Genehmigter Umfang, noch keine Lieferung."},
        {"date": "T4", "title": "Liefernachweis", "detail": "Gelieferte Menge, noch keine Nutzungsaussage."},
        {"date": "T5", "title": "Kontrollbericht", "detail": "Endverbleib und offene Lücken."}
      ],
      "graph": {
        "nodes": [
          {"id": "authority", "label": "Genehmigungsbehörde", "type": "institution"},
          {"id": "company", "label": "Hersteller Gamma", "type": "organisation"},
          {"id": "approval", "label": "Exportgenehmigung", "type": "decision"},
          {"id": "delivery", "label": "Teil-Lieferung", "type": "event"},
          {"id": "use", "label": "Konkrete Nutzung", "type": "unverified"}
        ],
        "edges": [
          {"from": "authority", "to": "approval", "label": "erteilt"},
          {"from": "approval", "to": "company", "label": "betrifft"},
          {"from": "company", "to": "delivery", "label": "liefert laut Nachweis"},
          {"from": "delivery", "to": "use", "label": "beweist NICHT"}
        ]
      },
      "agents": [
        {"name": "Legal Status", "proposal": "Klassifiziere jede Stufe separat.", "risk": "Genehmigung und Lieferung vermischen"},
        {"name": "Guardian", "proposal": "Entferne taktisch gefährliche Orts- und Zeitdetails.", "risk": "öffentliche Transparenz mit operativer Gefährdung verwechseln"},
        {"name": "Skeptic", "proposal": "Suche Belege, die Liefer- oder Nutzungsaussagen einschränken.", "risk": "Abwesenheit von Belegen als Gegenbeweis darstellen"}
      ],
      "tasks": {
        "citizen": ["Ordne Genehmigung, Lieferung und Nutzung in die richtige Reihenfolge.", "Öffne den abgelehnten Nutzung-Claim.", "Erkläre, warum eine offene Endverbleibsfrage keine Schuldfeststellung ist."],
        "investigator": ["Erstelle für jede Stufe einen eigenen Event-Record.", "Lass Legal Status und Guardian Vorschläge erzeugen.", "Formuliere einen Claim ohne taktische Details."],
        "evidence_manager": ["Prüfe Genehmigungsumfang und Lieferanker getrennt.", "Simuliere Hash-Verifikation aller Trainingsdokumente.", "Bestätige, dass keine Live-Positionsdaten gespeichert werden."],
        "reviewer": ["Prüfe, ob aus der Genehmigung unzulässig auf Nutzung geschlossen wird.", "Adressiere den Kontrollbericht als Kontext, nicht als Schuldbeweis.", "Entscheide mit sichtbarer Rationale."],
        "legal_reviewer": ["Klassifiziere Rechts- und Verfahrensstatus jeder Stufe.", "Prüfe Gefährdung durch operative Details.", "Verlange gegebenenfalls Redaktion oder blockiere die Aussage."],
        "publisher": ["Prüfe, dass Genehmigung, Lieferung und Nutzung getrennt bleiben.", "Kontrolliere, dass keine taktischen Details exportiert werden.", "Führe eine redigierte Trainingsfreigabe durch."]
      },
      "comprehension": {"question": "Was folgt sicher aus einer Exportgenehmigung?", "options": ["Dass geliefert wurde", "Dass das genehmigte Exportvorhaben behördlich erlaubt wurde; Lieferung und Nutzung brauchen eigene Belege", "Dass das System rechtswidrig eingesetzt wurde"], "correct": 1, "explanation": "SafeTrace modelliert Genehmigung, Lieferung, Endverbleib und Nutzung als getrennte Stufen."}
    },
    {
      "id": "case-004",
      "number": "004",
      "title": "Gesetzes-Fairness: Macht Merz Politik für Reiche?",
      "subtitle": "Direkte Wirkungen, Bedingungen, Prognosen und politische Herkunft getrennt bewerten.",
      "kind": "reviewed repository reference",
      "language": "de",
      "summary": "Der Fall vergleicht Unternehmensentlastungen, Grundsicherungsregeln und Familienleistungen. Das vorläufige Gesamturteil lautet teilweise gestützt, während pauschale oder falsch zugeschriebene Aussagen abgelehnt werden.",
      "question": "Welche Maßnahmen entlasten Unternehmen, welche erhöhen Bedingungen für Grundsicherungsbeziehende, und welche Aussagen werden der falschen Regierung zugerechnet?",
      "status": "technical_reference_publication_blocked",
      "publication": {"allowedInSimulation": false, "label": "Publikation blockiert", "reason": "Elf Source Records sind strukturiert, aber die unveränderten Originaldateien sind für den v1.7-Neu-Review noch 0/11 im Evidence Vault."},
      "readiness": {"sources": 11, "originals": 0, "claims": 5, "humanReviewed": 5, "openBlockers": 3},
      "sources": [
        {"id": "bundestag-investment", "title": "Bundestagsdokumente zum Investitionsprogramm", "publisher": "Deutscher Bundestag", "type": "primary", "zone": "public", "state": "backfill_required", "anchor": "Gesetz, Abstimmung und fiskalische Wirkung"},
        {"id": "bmf-programme", "title": "Informationen des Bundesfinanzministeriums", "publisher": "BMF", "type": "primary", "zone": "public", "state": "backfill_required", "anchor": "Abschreibung und Körperschaftsteuer"},
        {"id": "bmas-security", "title": "Grundsicherungs- und Regelsatzdokumente", "publisher": "BMAS", "type": "primary", "zone": "public", "state": "backfill_required", "anchor": "Pflichten, Sanktionen und Regelsätze"},
        {"id": "bundestag-family", "title": "Bundestagsbeschluss Familienleistung 2024", "publisher": "Deutscher Bundestag", "type": "primary", "zone": "public", "state": "backfill_required", "anchor": "Beschlusszeitpunkt der Kindergelderhöhung"},
        {"id": "ifo-analysis", "title": "Ökonomische Analyse des Investitionsprogramms", "publisher": "ifo Institut", "type": "analysis", "zone": "public", "state": "backfill_required", "anchor": "modellierte Wirkungen und Grenzen"}
      ],
      "claims": [
        {"id": "c4-1", "text": "Die Regierung Merz entlastet profitable Unternehmen erheblich.", "status": "verified_fact", "verdict": "supported", "material": true, "supporting": ["bundestag-investment", "bmf-programme", "ifo-analysis"], "contradicting": [], "limitation": "Langfristige Verteilung auf Eigentümer, Beschäftigte und Konsumenten ist noch nicht gemessen.", "reviewState": "approved_repository_consistency"},
        {"id": "c4-2", "text": "Merz hat 2026 die Grundsicherungs-Regelsätze nominal gekürzt.", "status": "verified_fact", "verdict": "not_supported", "material": true, "supporting": [], "contradicting": ["bmas-security"], "limitation": "Nominal unverändert ist nicht dasselbe wie reale Kaufkraftstabilität.", "reviewState": "approved_repository_consistency"},
        {"id": "c4-3", "text": "Die Regierung erhöht Pflichten und mögliche finanzielle Risiken für Menschen in der Grundsicherung.", "status": "verified_fact", "verdict": "supported", "material": true, "supporting": ["bmas-security"], "contradicting": [], "limitation": "Tatsächliche Häufigkeit und soziale Wirkung müssen nach Inkrafttreten empirisch gemessen werden.", "reviewState": "approved_repository_consistency"},
        {"id": "c4-4", "text": "Die Regierung Merz hat das Kindergeld 2026 erhöht.", "status": "verified_fact", "verdict": "not_supported", "material": true, "supporting": [], "contradicting": ["bundestag-family"], "limitation": "Die Erhöhung trat 2026 in Kraft, wurde aber bereits 2024 beschlossen.", "reviewState": "approved_repository_consistency"},
        {"id": "c4-5", "text": "Merz macht ausschließlich Politik für Reiche und kürzt ausschließlich bei Kindern und armen Familien.", "status": "analytical_red_flag", "verdict": "partly_supported", "material": true, "supporting": ["bundestag-investment", "bmf-programme", "bmas-security"], "contradicting": ["bundestag-family"], "limitation": "Der Verteilungskonflikt ist teilweise belegt; die Wörter ‚ausschließlich‘ und pauschale Kürzungsbehauptungen sind nicht gedeckt.", "reviewState": "approved_repository_consistency"}
      ],
      "timeline": [
        {"date": "Dez. 2024", "title": "Kindergelderhöhung beschlossen", "detail": "Vor Amtsantritt der Regierung Merz."},
        {"date": "Juli 2025", "title": "Degressive Abschreibung beginnt", "detail": "Direkte steuerliche Liquiditätswirkung für förderfähige Investitionen."},
        {"date": "Jan. 2026", "title": "Kindergeld steigt und Regelsätze bleiben nominal gleich", "detail": "Politische Herkunft und reale Kaufkraft getrennt betrachten."},
        {"date": "Juli 2026", "title": "Neue Grundsicherung tritt in Kraft", "detail": "Strengere Pflichten und mögliche Minderungen; Wirkung noch zu messen."},
        {"date": "2028–2032", "title": "Körperschaftsteuer sinkt schrittweise", "detail": "Direkte Unternehmensentlastung; indirekte Effekte bleiben Prognose."}
      ],
      "graph": {
        "nodes": [
          {"id": "government", "label": "Regierung Merz", "type": "government"},
          {"id": "business", "label": "Profitable Unternehmen", "type": "affected_group"},
          {"id": "basic-security", "label": "Grundsicherungs-Haushalte", "type": "affected_group"},
          {"id": "families", "label": "Familien", "type": "affected_group"},
          {"id": "prior", "label": "Vorherige Legislatur", "type": "government"}
        ],
        "edges": [
          {"from": "government", "to": "business", "label": "beschloss direkte Entlastungen"},
          {"from": "government", "to": "basic-security", "label": "verschärfte Bedingungen"},
          {"from": "prior", "to": "families", "label": "beschloss Kindergelderhöhung"},
          {"from": "government", "to": "families", "label": "darf diese Maßnahme nicht neu beanspruchen"}
        ]
      },
      "agents": [
        {"name": "Quant", "proposal": "Trenne direkte Geldwirkung von modellierten Langzeitwirkungen.", "risk": "Prognose als gemessene Wirkung darstellen"},
        {"name": "Legal Status", "proposal": "Trenne beschlossen, in Kraft und zukünftig wirksam.", "risk": "Inkrafttreten mit politischer Urheberschaft verwechseln"},
        {"name": "Skeptic", "proposal": "Suche Gegenbelege zu ‚ausschließlich‘ und falscher Attribution.", "risk": "eine einzelne Gegenmaßnahme als Widerlegung des gesamten Verteilungskonflikts behandeln"},
        {"name": "Guardian", "proposal": "Vermeide moralischen Gesamtscore und mache Unsicherheit sichtbar.", "risk": "Werturteil als objektive Messung ausgeben"}
      ],
      "tasks": {
        "citizen": ["Vergleiche die fünf Claim-Verdicts.", "Beantworte die Attribution-Frage zur Kindergelderhöhung.", "Markiere, welche Information dir für ein persönliches Fairnessurteil noch fehlt."],
        "investigator": ["Wähle einen Claim und prüfe alle zugeordneten Quellen-IDs.", "Lass Quant, Skeptic und Legal Status Vorschläge erzeugen.", "Ergänze eine klare Limitation und sende zur Review."],
        "evidence_manager": ["Öffne den Source-Backfill-Status 0/11.", "Simuliere den Erwerb einer Originaldatei samt Hash und Anchor.", "Beobachte, dass eine einzelne Quelle den Publikationsblocker nicht vollständig löst."],
        "reviewer": ["Prüfe das Wort ‚ausschließlich‘ gegen supporting und contradicting evidence.", "Trenne nominale und reale Kürzung.", "Entscheide mit Rationale, ohne die fehlenden Originalbytes zu ignorieren."],
        "legal_reviewer": ["Prüfe politische Zuschreibung und wertende Formulierungen.", "Bestätige, dass keine Korruption oder illegale Einflussnahme behauptet wird.", "Halte Neuveröffentlichung bis zum Evidence-Backfill blockiert."],
        "publisher": ["Kontrolliere 5/5 Reviews, aber auch 0/11 Originale.", "Öffne alle Publikationsblocker.", "Versuche zu publizieren und dokumentiere den korrekten NO-GO-Grund."]
      },
      "comprehension": {"question": "Warum wird die Kindergelderhöhung nicht der Regierung Merz zugerechnet?", "options": ["Weil Familien nie profitieren", "Weil die Erhöhung zwar 2026 wirksam wurde, aber bereits 2024 beschlossen wurde", "Weil Kindergeld kein Gesetz ist"], "correct": 1, "explanation": "Zeitpunkt des Inkrafttretens und politische Urheberschaft sind getrennte Tatsachen."}
    }
  ]
};
