# Impact-Mission 001 — Arbeit. Teilhabe. Energie.

Eine kleine öffentliche Deutschland-Mission mit drei Indikatoren:

1. **Arbeitslosenquote**
2. **Armutsgefährdungsquote**
3. **Ausbau Windenergie an Land**

Live: <https://mikelninh.github.io/digital-democracy-studio/impact-mission/>

## Zweck

Die Mission macht Richtung, Tempo, Datenalter und Messgrenzen sichtbar. Sie ist kein Regierungsranking und behauptet keine Kausalität zwischen einer Maßnahme und einem Ergebnis.

## Aktueller Datenstand

| Indikator | Wert | Zeitraum | Einordnung |
|---|---:|---|---|
| Arbeitslosenquote | 6,2 % | Juni 2026 | Monatlich leicht gesunken, gegenüber Vorjahr unverändert |
| Armutsgefährdungsquote | 16,1 % | 2025 | +0,6 Prozentpunkte gegenüber 2024 |
| Wind an Land | 70,051 GW installiert | Juni 2026 | 1,943 GW Nettozubau im ersten Halbjahr; Zielpfad deutlich verfehlt |

## Quellen

- Bundesagentur für Arbeit: Arbeitsmarkt im Juni 2026
- Statistisches Bundesamt: Endergebnisse EU-SILC 2025
- Bundesnetzagentur / Marktstammdatenregister: Statistik zur Stromerzeugungsleistung, Juni 2026

Die konkreten Quellen-URLs, Veröffentlichungsdaten, Werte und Caveats stehen maschinenlesbar in [`data/indicators.json`](data/indicators.json).

## Statuslogik

- **on_track**: Messwert bewegt sich in die gewünschte Richtung und liegt auf einem belastbaren Zielpfad.
- **stable**: keine klare Verbesserung gegenüber dem relevanten Vergleich.
- **wrong_direction**: Messwert bewegt sich entgegen der gewünschten Richtung.
- **off_track**: ein offizieller Zielpfad besteht, das beobachtete Tempo reicht derzeit nicht aus.

Die sozialen Indikatoren erhalten bewusst keine frei erfundenen 2030-Zielwerte. Dort wird zunächst die Richtung gegenüber dem Vorjahr bewertet. Beim Windindikator wird das gesetzliche Ausbauziel von 115 GW bis 2030 verwendet.

## Rechenweg Wind an Land

- Installierte Leistung Juni 2026: **70,051 GW**
- Ziel 2030: **115 GW**
- Verbleibende Lücke: **44,949 GW**
- Erforderlicher monatlicher Nettozubau laut Bundesnetzagentur: rund **832 MW**
- Erforderlicher Zubau Januar bis Juni 2026: **4,992 GW**
- Tatsächlicher Nettozubau Januar bis Juni 2026: **1,943 GW**
- Erfüllung des Halbjahres-Zielpfads: rund **39 %**

## Methodische Grenzen

- Die BA-Arbeitslosenquote ist nicht identisch mit der ILO-Erwerbslosenquote.
- Die Armutsgefährdungsquote misst relative Einkommensarmut unter 60 % des nationalen Medians; sie bildet nicht jede materielle oder soziale Notlage ab.
- Daten aus dem Marktstammdatenregister können wegen gesetzlicher Registrierungsfristen nachträglich ergänzt werden.
- Ein Trend zeigt zunächst nur eine Veränderung. Die Zuschreibung zu einzelnen Gesetzen, Haushalten, Parteien oder Institutionen erfordert eine gesonderte Evidenzprüfung.

## Nächste Ausbaustufe

- automatische, prüfbare Datenaktualisierung;
- historische Zeitreihen statt nur aktueller Werte;
- regionale Aufschlüsselung nach Bundesland;
- Vorläuferindikatoren wie Vermittlungsdauer, Wohnkostenbelastung und Windgenehmigungen;
- Quellenbelege mit Abrufzeit, Hash und sichtbarer Änderungshistorie;
- öffentliche Challenge- und Korrekturfunktion.
