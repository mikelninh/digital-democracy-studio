window.SAFETRACE_WOHLSTAND_DATA = {
  "schemaVersion": "safetrace.wohlstandslabor/0.1",
  "snapshotDate": "2026-07-24",
  "boundary": {
    "publicSourcesOnly": true,
    "simulationOnly": true,
    "browserLocalState": true,
    "noInvestmentAdvice": true,
    "noPartyPersuasion": true,
    "notice": "Gleiche Fakten, unterschiedliche Lebenslagen. Perspektiven verändern Reihenfolge und Fragen, niemals Quellen oder Befunde."
  },
  "principles": [
    "Einfacher: weniger Sonderregeln, klare Standards und automatische Verfahren.",
    "Produktiver: mehr Wert pro Stunde, nicht bloß mehr Kontrolle oder Arbeitszeit.",
    "Gerechter: breite Teilhabe an Einkommen, Chancen und produktivem Kapital.",
    "Messbar: jedes Gesetz erhält Ausgangswert, Ziel, Frist, Verteilung und Abbruchregel.",
    "Korrigierbar: Gegenbelege und Fehlentwicklungen bleiben sichtbar."
  ],
  "lenses": [
    {"id":"all","name":"Gemeinsames Lagebild","description":"Priorisiert gesamtgesellschaftliche Wirkung."},
    {"id":"household","name":"Haushalt & Lebenshaltung","description":"Was verändert Kosten, Sicherheit und verfügbares Einkommen?"},
    {"id":"worker","name":"Arbeit & Aufstieg","description":"Was verändert Löhne, Qualifikation, Arbeitsqualität und Übergänge?"},
    {"id":"founder","name":"Gründung & Mittelstand","description":"Was verändert Investition, Skalierung, Beschaffung und Bürokratie?"},
    {"id":"future","name":"Junge & kommende Generationen","description":"Was wird vererbt: Vermögen, Schulden, Infrastruktur oder Risiken?"},
    {"id":"climate","name":"Klima & Resilienz","description":"Was verändert Emissionen, Energiesicherheit und Anpassungsfähigkeit?"},
    {"id":"budget","name":"Steuerzahler & Staatsfähigkeit","description":"Was kostet es, was spart es und kann der Staat es umsetzen?"}
  ],
  "policies": [
    {
      "id":"citizen-capital",
      "title":"Bürgerkapital für alle",
      "status":"Reform beschlossen; Start der neuen privaten Altersvorsorge 2027. Frühstart-Rente noch in Umsetzung.",
      "verdict":"Richtige Richtung, aber noch zu teuer, zu anbieterzentriert und zu wenig automatisch.",
      "summary":"Deutschland öffnet die geförderte Altersvorsorge für ETF- und Fondsdepots, führt Standardprodukte ein und fördert Beiträge proportional. Kinder sollen ab sechs Jahren staatlich finanziertes Startkapital erhalten.",
      "facts":[
        "Das neue Altersvorsorgedepot kann ohne Garantie geführt werden und erlaubt Fonds beziehungsweise ETFs.",
        "Das Standarddepot soll Entscheidungen vereinfachen; die Effektivkosten sind gesetzlich begrenzt.",
        "Die Frühstart-Rente sieht zehn Euro pro Monat für Kinder vom sechsten bis zum 18. Lebensjahr vor.",
        "Für Kinder ohne eröffnetes Depot ist eine kollektive Auffanglösung vorgesehen."
      ],
      "incentive":"Sparen und langfristiger Kapitalbesitz werden gefördert; Anbieter konkurrieren um staatlich privilegierte Vorsorgeverträge.",
      "beneficiaries":["Langfristig Sparende","Familien mit Kindern","Menschen mit kleinen regelmäßigen Beiträgen","Kapitalmarktanbieter"],
      "payers":["Bundeshaushalt über Zulagen","Sparer über Produktkosten","Spätere Steuerzahler bei unzureichender Alterssicherung"],
      "risks":["Kostenobergrenze kann weiterhin deutlich über sehr günstigen Welt-ETFs liegen","Freiwillige Anmeldung erzeugt Teilnahmeunterschiede","Produktvielfalt kann neue Komplexität schaffen","Politische Regeln können später verändert werden"],
      "better":[
        "Automatisches Bürgerdepot bei Geburt oder erster Steuer-ID, Opt-out statt Opt-in.",
        "Öffentlicher Defaultfonds mit globaler Diversifikation und Zielkosten unter 0,25 Prozent jährlich.",
        "Rechtlich individuelles Eigentum, unabhängig vom Staatshaushalt und nicht für andere Zwecke entziehbar.",
        "Progressive staatliche Einzahlungen: mehr für einkommensarme Kinder, gleiches Produkt für alle.",
        "Ein einziges digitales Konto mit freiem Anbieterwechsel und standardisierten Daten."
      ],
      "scores":{"simplicity":62,"productivity":72,"fairness":68,"resilience":70,"evidence":76},
      "lensPriority":{"all":95,"household":92,"worker":86,"founder":58,"future":100,"climate":30,"budget":83},
      "sources":[
        {"label":"BMF: Reform der geförderten privaten Altersvorsorge","url":"https://www.bundesfinanzministerium.de/Content/DE/FAQ/reform-der-privaten-altersvorsorge.html"},
        {"label":"BMF: Frühstart-Rente","url":"https://www.bundesfinanzministerium.de/Content/DE/FAQ/fruehstart-rente.html"},
        {"label":"Bundesregierung: Eckpunkte Frühstart-Rente","url":"https://www.bundesregierung.de/breg-de/aktuelles/kabinett-fruehstart-rente-2399880"}
      ]
    },
    {
      "id":"energy-abundance",
      "title":"Saubere und günstige Energie im Überfluss",
      "status":"Starker Ausbau, aber große Kapazitäts-, Netz-, Flexibilitäts- und Preis-Gaps bleiben.",
      "verdict":"Erzeugung wächst; Netze, Speicher, flexible Nachfrage und gesicherte Leistung hinken hinterher.",
      "summary":"Deutschland hat 2025 rund 21 GW erneuerbare Leistung hinzugebaut. Gleichzeitig gehören Haushalts- und Gewerbestrompreise weiterhin zu den höchsten in der EU, und die Netzreserve steigt.",
      "facts":[
        "Solar lag Ende 2025 bei 117 GW gegenüber 215 GW Ziel für 2030.",
        "Wind an Land lag bei 68,1 GW gegenüber 115 GW Ziel für 2030.",
        "Wind auf See lag bei 9,5 GW gegenüber mindestens 30 GW Ziel für 2030.",
        "Für Winter 2026/27 wurden 7,407 GW Netzreserve bestätigt; für 2028/29 8,274 GW.",
        "Deutschland hatte im zweiten Halbjahr 2025 EU-weit den zweithöchsten Haushaltsstrompreis und den höchsten Preis für die betrachtete Gruppe nichtprivater Verbraucher."
      ],
      "incentive":"Förderung beschleunigt erneuerbare Erzeugung; Engpässe und Netzentgelte belohnen jedoch nicht überall systemdienliche Standorte und Flexibilität.",
      "beneficiaries":["Erneuerbaren-Projektierer","Netz- und Speicheranbieter","Elektrifizierte Haushalte bei sinkenden Gesamtkosten","Industrie bei verlässlichen Langfristpreisen"],
      "payers":["Netznutzer über Entgelte","Steuerzahler über Förder- und Entlastungsprogramme","Regionen mit Infrastrukturbelastung","Unternehmen bei hohen Strompreisen"],
      "risks":["Erzeugung ohne Netze führt zu Abregelung und Redispatch","Dauerhafte Subventionen konservieren ineffiziente Strukturen","Lokale Akzeptanz sinkt ohne faire Beteiligung","Dunkelflauten bleiben ohne flexible gesicherte Leistung teuer"],
      "better":[
        "Netz, Erzeugung, Speicher und flexible Nachfrage in gemeinsamen regionalen Auktionen planen.",
        "Dynamische Tarife und einfache Smart-Meter-Standards für alle Haushalte.",
        "Schnellere Genehmigungen mit verbindlichen Fristen und digitaler Einmal-Dateneingabe.",
        "Bürgerkapital direkt an Wind-, Solar-, Speicher- und Netzprojekten beteiligen.",
        "Gesicherte Leistung technologieoffen beschaffen, aber emissions- und verfügbarkeitsbasiert bezahlen."
      ],
      "gaps":[
        {"label":"Solar","current":117,"target":215,"unit":"GW"},
        {"label":"Wind an Land","current":68.1,"target":115,"unit":"GW"},
        {"label":"Wind auf See","current":9.5,"target":30,"unit":"GW"}
      ],
      "scores":{"simplicity":42,"productivity":70,"fairness":54,"resilience":63,"evidence":88},
      "lensPriority":{"all":100,"household":100,"worker":80,"founder":95,"future":96,"climate":100,"budget":88},
      "sources":[
        {"label":"Bundesnetzagentur: Ausbau Erneuerbarer Energien 2025","url":"https://www.bundesnetzagentur.de/SharedDocs/Pressemitteilungen/DE/2026/20260108_EEG.html"},
        {"label":"Bundesnetzagentur: Netzreserve 2026/27","url":"https://www.bundesnetzagentur.de/SharedDocs/Pressemitteilungen/DE/2026/20260522_Netzreserve.html"},
        {"label":"Eurostat: Strompreise zweites Halbjahr 2025","url":"https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20260508-2"}
      ]
    },
    {
      "id":"anchor-customer",
      "title":"Der Staat als erster guter Kunde",
      "status":"Politisches Ziel und erste Infrastruktur vorhanden; messbare Startup-Beschaffung noch unzureichend sichtbar.",
      "verdict":"Extrem großer Hebel, sofern Beschaffung nach Wirkung statt nach Lastenheft und Anbietergröße erfolgt.",
      "summary":"Öffentliche Beschaffung bewegt jährlich einen dreistelligen Milliardenbetrag. Die Bundesregierung will stärker als Ankerkunde für KI, souveräne Cloud und innovative Start-ups auftreten.",
      "facts":[
        "Das öffentliche Beschaffungsvolumen wird vom Wirtschaftsministerium auf mindestens 300 Milliarden Euro jährlich geschätzt.",
        "Der Bund will öffentliche Rechenbedarfe bündeln und als Ankerkunde das heimische KI-Ökosystem unterstützen.",
        "KOINNO und der KOINNOvationsplatz verbinden öffentliche Bedarfe mit innovativen Anbietern.",
        "Die Regierung kündigt geänderte Ausschreibungsmodalitäten und mehr offene Standards an."
      ],
      "incentive":"Ein erster öffentlicher Referenzkunde senkt Markteintrittsrisiken und kann private Nachfrage auslösen.",
      "beneficiaries":["Start-ups und KMU","Verwaltungen mit besseren Werkzeugen","Bürger durch bessere Dienste","Europäische digitale Souveränität"],
      "payers":["Öffentliche Haushalte","Verwaltungen durch Umstellungs- und Lernkosten","Anbieter durch Vergabeaufwand"],
      "risks":["Pilotitis ohne Skalierung","Vergaben an bekannte Großanbieter trotz Innovationssprache","Vendor Lock-in","Automatisierung schlechter Prozesse statt echter Neugestaltung"],
      "better":[
        "Ein Prozent jedes geeigneten IT-Beschaffungsbudgets für messbare Challenge-Verträge reservieren.",
        "Kleine bezahlte Discovery-Phasen, danach gestufte Verträge nach nachgewiesener Wirkung.",
        "Offene Schnittstellen, Datenportabilität und Exit-Pläne verpflichtend machen.",
        "Ergebnisse, Kosten, Zeitersparnis und Abbruchgründe öffentlich dokumentieren.",
        "Ein bundesweiter Katalog wiederverwendbarer, geprüfter AI-Komponenten."
      ],
      "scores":{"simplicity":58,"productivity":92,"fairness":72,"resilience":76,"evidence":60},
      "lensPriority":{"all":92,"household":50,"worker":78,"founder":100,"future":90,"climate":65,"budget":96},
      "sources":[
        {"label":"BMWE: Innovation im öffentlichen Beschaffungswesen","url":"https://www.bmwk.de/Redaktion/DE/Artikel/Technologie/innovation-beschaffungswesen.html"},
        {"label":"Bundesregierung: Staat als Ankerkunde für KI","url":"https://www.bundesregierung.de/breg-de/aktuelles/bundeskanzler-friedrich-merz-trifft-nvidia-ceo-jensen-huang-deutschland-mit-fuehrungsanspruch-bei-kuenstlicher-intelligenz-2354238"},
        {"label":"BMDS: Start-ups und Staatsmodernisierung","url":"https://bmds.bund.de/themen/digitale-wirtschaft/start-ups"}
      ]
    },
    {
      "id":"ai-robotics-dividend",
      "title":"AI- und Robotik-Dividende",
      "status":"Technologie und Nachfrage wachsen; gesellschaftliche Verteilungsregeln sind noch offen.",
      "verdict":"Der Produktivitätshebel ist enorm. Ohne breites Eigentum, Weiterbildung und Wettbewerb kann er Ungleichheit verschärfen.",
      "summary":"AI und Robotik können knappe Facharbeit ergänzen, Verwaltung und Mittelstand produktiver machen und Energie, Gesundheit und Produktion optimieren. Entscheidend ist, wer Systeme besitzt und wer an den Gewinnen beteiligt wird.",
      "facts":[
        "Energieunternehmen suchen aktuell Rollen in Data Science, Data Engineering, Conversational AI und AI-Transformation.",
        "Die Bundesregierung will KI-Compute ausbauen und öffentliche Nachfrage als Ankerkunde bündeln.",
        "Agentische Systeme sollen definierte Verwaltungsabläufe innerhalb klarer Leitplanken unterstützen."
      ],
      "incentive":"Unternehmen investieren, wenn AI messbar Kosten senkt oder Qualität erhöht; Beschäftigte kooperieren eher, wenn sie an Produktivitätsgewinnen beteiligt sind.",
      "beneficiaries":["Unternehmen mit guter Datenbasis","Beschäftigte mit ergänzenden Fähigkeiten","Menschen mit Zugang zu besseren Diensten","Eigentümer produktiver Systeme"],
      "payers":["Beschäftigte in verdrängten Tätigkeiten","Organisationen mit schlechter Transformation","Steuerzahler bei ineffektiver Förderung","Gesellschaft bei Konzentration von Macht"],
      "risks":["Automatisierung ohne Prozessneugestaltung","Monopolbildung","Überwachung am Arbeitsplatz","Qualifikations- und Eigentumslücke","Energie- und Rechenbedarf"],
      "better":[
        "AI-Einführung mit messbarem Mitarbeitergewinn verbinden: Zeit, Lohn, Beteiligung oder Weiterbildung.",
        "Robotik-as-a-Service für Mittelstand, Pflege, Bau und Landwirtschaft kofinanzieren.",
        "Öffentliche und genossenschaftliche Datentreuhänder für sichere sektorale Datennutzung.",
        "Offene Evaluationen: Qualität, Fehler, Energieverbrauch und Verteilungswirkung.",
        "Bürgerfonds hält breit gestreute Produktivkapital-Anteile statt einzelne politische Unternehmenswetten."
      ],
      "scores":{"simplicity":55,"productivity":96,"fairness":55,"resilience":78,"evidence":66},
      "lensPriority":{"all":96,"household":68,"worker":100,"founder":100,"future":100,"climate":75,"budget":80},
      "sources":[
        {"label":"Bundesregierung: Agentische KI und Staat als Ankerkunde","url":"https://www.bundesregierung.de/breg-de/service/newsletter-und-abos/bulletin/bmds-jahrestagung-dbb-2402536"},
        {"label":"E.ON: Data Scientist Flex Trading","url":"https://jobs.eon.com/de/job/Data-Scientist-Flex-Trading-Strategy-Development-f_m_d-Essen/245210"},
        {"label":"Siemens Energy: Project Lead AI Transformation","url":"https://jobs.siemens-energy.com/en_US/jobs/FolderDetailApplied?folderId=295764"}
      ]
    }
  ],
  "brief": {
    "edition":"#001",
    "title":"Wohlstand entsteht, wenn Produktivität und Eigentum breit wachsen.",
    "readingMinutes":3,
    "mustKnow":[
      "Die Altersvorsorge öffnet sich für kostengünstigere Kapitalmarktprodukte, bleibt aber freiwillig und anbieterzentriert.",
      "Der Ausbau erneuerbarer Leistung ist stark; Netze, Flexibilität und Preise bleiben der Engpass.",
      "Der Staat will Ankerkunde für KI werden. Entscheidend ist, ob aus Piloten skalierte, offene und messbar bessere Dienste entstehen."
    ],
    "watchNext":[
      "Tatsächliche Effektivkosten der neuen Standarddepots ab 2027.",
      "Jährlicher Solar-, Onshore- und Offshore-Zubau gegenüber dem erforderlichen Pfad.",
      "Anteil innovativer Start-ups an öffentlichen Digital- und KI-Aufträgen.",
      "Produktivitätsgewinn und Verteilung bei AI- und Robotikprojekten."
    ]
  }
};
