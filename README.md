# Beleg-Schema: ein Punktesystem für alles, was man dir erzählt

Framework X ist schneller. Diese UX-Regel gilt immer. So wirst du in ChatGPT empfohlen. Alle sagen es mit derselben Sicherheit, und die Hälfte widerspricht sich.

Dieses Repository enthält das Schema, mit dem ich seit 2026 jede Aussage in meiner Wissensbasis bewerte, dazu eine Vorlage zum Nachbauen und ein Skript, das die Quellen monatlich prüft. Das Schema ist frei verwendbar (MIT). Die Daten, die ich damit bewerte, stehen nicht hier.

Von [Oliver Bock](https://theb2banswer.de), The B2B Answer. Entstanden für die Frage, welche Ratschläge zur Sichtbarkeit in ChatGPT belegt sind. Funktioniert für jedes Feld, in dem viel behauptet wird.

## Das Schema

Jede Aussage bekommt vier Angaben.

### 1. Quellengewicht: woher kommt die Aussage?

| Gewicht | Bedeutung | Beispiel |
|---|---|---|
| **G0** | Plattformdoktrin, Primärquelle gelesen | Offizielle Dokumentation des Herstellers oder der Plattform |
| **G1** | Eigene Messung | Eigener Benchmark, eigene Stichprobe, Rohdaten und Skript liegen vor |
| **G2** | Fremdstudie mit geprüfter Primärquelle | Studie, deren Methode und Daten ich selbst gelesen habe |
| **G3** | Anbieterforschung oder teilweise geprüft | Studie eines Anbieters, der mit dem Ergebnis etwas verkauft; Primärdaten nicht einsehbar |
| **G4** | Praktiker- oder Kundenaussage im Einzelfall | „Bei uns hat das funktioniert“ |
| **G5** | Sekundär oder ungeprüft | Gehört, gelesen, weitererzählt |

Publizierbar ist nur G0 bis G2. Alles andere bleibt intern, mit Etikett.

### 2. Konfidenz: wie sicher bin ich?

| Konfidenz | Bedeutung |
|---|---|
| **C1** belegt | Mindestens eine Quelle G0 bis G2, keine Gegenbelege |
| **C2** plausibel | Mehrere G3/G4-Quellen in dieselbe Richtung, oder eine G2-Quelle mit Einschränkungen |
| **C3** Vermutung | Eine Quelle, oder Quellen widersprechen sich |

Gewicht und Konfidenz sind getrennt. Eine eigene Messung (G1) mit kleiner Stichprobe kann C2 sein. Eine Anbieterstudie (G3), die drei andere bestätigen, auch.

### 3. Zwei Daten

- **Erstbeobachtung:** wann die Aussage zum ersten Mal auftauchte.
- **Zuletzt bestätigt:** wann ich sie zuletzt gegen eine Quelle geprüft habe. Älter als sechs Monate ohne Bestätigung: Status auf „Beobachtung“.

### 4. Status

`aktiv` · `Beobachtung` · `zurückgezogen`. Zurückgezogene Aussagen bleiben stehen, mit Grund. Sie sind die wertvollsten Zeilen, weil sie zeigen, was sich als falsch herausgestellt hat.

## Die Regeln dazu

1. Jede Zahl kommt aus einer Quelle, die ich benennen kann. Keine Zahl ohne Datum.
2. Zu gut oder zu schlecht heißt: erst die Methode prüfen, dann berichten. 100 Prozent, 0 von 24, ein Sprung um das Zehnfache sind Anlässe für eine Kontrollmessung mit einem zweiten Werkzeug.
3. Vergleiche nur mit denselben Fragen und demselben Instrument.
4. Jede Messung trägt eine Methodenzeile: Datum, Stichprobe, Läufe, Instrument, Grenzen.
5. Jeder Messfehler bekommt eine Zeile im Fehlerlog, eine je Ursache, damit er nicht zweimal passiert.

## Vorlage

`vorlage/aussagen.csv` ist eine Tabelle mit den Spalten Aussage, Quellengewicht, Konfidenz, Erstbeobachtung, Zuletzt bestätigt, Status, Quelle, Notiz und drei Beispielzeilen. In Notion, Airtable oder einer Tabellenkalkulation importieren, Gewicht und Konfidenz als Auswahlfelder anlegen, fertig.

Nützliche Ansichten: „Überfällig“ (aktiv, Zuletzt bestätigt älter als sechs Monate, älteste zuerst) und „Publizierbar“ (G0 bis G2, aktiv).

## Quellen monatlich prüfen

`fetch.py` ruft die Seiten aus `sources.yaml` ab, legt den Text unter `sources/` ab und schreibt eine neue Fassung nur, wenn sich der Inhalt geändert hat. Die GitHub Action läuft am 1. jedes Monats. Ändert sich eine Quelle mit Gewicht G0, G1 oder G2, öffnet sie ein Issue mit dem Diff. Dann: Quelle neu lesen, Aussage prüfen, „Zuletzt bestätigt“ setzen, Issue schließen.

```
pip install -r requirements.txt
python fetch.py          # abrufen, nichts committen
python fetch.py --commit # so läuft es in der Action
```

Eine Quelle ist eine Zeile in `sources.yaml` mit `slug`, `url`, `gewicht`, `gelesen` und optional `link` auf die Zeile in der eigenen Wissensbasis. `sources/` liegt hier leer; der erste Lauf füllt es.

## Was hier nicht steht

Die 139 bewerteten Aussagen zur Sichtbarkeit in ChatGPT, die Messdaten dahinter und die vollständige Quellenliste. Das Schema ist die Methode, die Daten sind die Arbeit.

## Vortrag

„404 Beleg not found: Ein Punktesystem für alles, was man mir erzählt“, eingereicht für den Digital Crafts Day 2027 in Weiden. Fragen und Erfahrungen mit dem Schema gern als Issue hier oder an oliver@theb2banswer.de.
