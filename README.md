# Beleg-Schema: a scoring system for everything people tell you

*English summary first. The full German version follows below.*

Framework X is faster. This UX rule always applies. This is how you get recommended in ChatGPT. Everyone says it with the same confidence, and half of them contradict each other.

This repo holds the schema I use to score every claim in my knowledge base, a template to copy, and a script that re-checks the sources every month. The schema is free to use (MIT). The data I score with it is not here.

By [Oliver Bock](https://theb2banswer.de), The B2B Answer. Built to answer which advice on visibility in ChatGPT is actually backed. Works for any field where a lot gets claimed.

## The schema in short

Every claim gets:

- **Source weight G0 to G5:** G0 platform doctrine read at the source · G1 own measurement · G2 third-party study with the primary source checked · G3 vendor research or partly checked · G4 single practitioner or client account · G5 secondhand or unchecked. Only G0 to G2 is publishable.
- **Confidence C1 to C3:** C1 proven (disclosed method and a clear mechanism, plus several independent voices or an own measurement over at least 30 days, no counter-evidence) · C2 plausible · C3 hunch. Weight and confidence are separate.
- **Scope:** where the claim holds (market, language, industry, platform) and where it was never measured.
- **Promotion and expiry condition:** what would lift it to C1, and what would kill it.
- **Two dates and a status:** first seen, last confirmed, `aktiv` · `Beobachtung` · `zurückgezogen`. Retracted claims stay, with the reason.

## The rules in short

1. Every number has a named source and a date.
2. Too good or too bad means: check the method first.
3. Compare only with the same questions and the same instrument.
4. Every measurement carries a method line: date, sample, runs, instrument, the instrument's bias, limits.
5. One fehlerlog line per cause of a measurement error.
6. List questions to AI systems ("Which vendors …") count as a measurement only after at least five runs per question.
7. Count sources, not channels. Sources that cite each other count 1.5 at most together. Whoever profits from the claim counts half.
8. Anything an AI agent scored counts as C2 at most until a human has checked it. Only G0 is exempt.
9. When a source or measurement changes a belief, one line in a changed-my-mind log. Append only.
10. Numbers come from code over the full dataset, and row count and row sum are printed against the total before anything is interpreted. Search Console, Ahrefs and any capped API return only the top rows.

## Worked example

Claim: "An llms.txt file gets you into AI search."

1. **First seen** in vendor and agency posts: G3 to G5, C3.
2. **Checked at the source:** Google's guide on generative AI in Search says Google Search doesn't use llms.txt or other special AI files. That is G0.
3. **Result:** for Google Search the claim is retracted, with the G0 counter-evidence as the reason. Scope matters: the Google source says nothing about ChatGPT or Perplexity, so for those the claim stays C3 and unmeasured.
4. **Expiry and promotion:** reopen for Google if Google's documentation changes (the monthly fetch opens an issue). For other systems it would need an own measurement before it moves.

The row is in `vorlage/aussagen.csv`.

## Template and script

`vorlage/aussagen.csv` is comma-separated, UTF-8, German headers. Import into Notion, Airtable or a spreadsheet. `fetch.py` pulls the pages in `sources.yaml` monthly and opens an issue when a G0 to G2 source changes. Details in German below.

## Using it on GitHub

Keep your claims as a CSV in a repo and GitHub does the rest:

- **Table view:** GitHub renders the CSV as a searchable table, with history per row through the commit log.
- **Human check as pull request:** an agent opens a PR with new rows (`Geprüft von: Agent`, at most C2). You review, raise the confidence, merge. The PR is the record of rule 8.
- **Automatic check:** `pruefen.py` runs on every push and PR and once a month. It fails on invalid values and on agent rows above C2, and lists overdue rows and rows without scope in the job summary.
- **Source changes as issues:** the monthly `fetch.py` run opens an issue when a G0 to G2 source changes.

---

# Beleg-Schema: ein Punktesystem für alles, was man dir erzählt

Framework X ist schneller. Diese UX-Regel gilt immer. So wirst du in ChatGPT empfohlen. Alle sagen es mit derselben Sicherheit, und die Hälfte widerspricht sich.

Dieses Repository enthält das Schema, mit dem ich seit 2026 jede Aussage in meiner Wissensbasis bewerte, dazu eine Vorlage zum Nachbauen und ein Skript, das die Quellen monatlich prüft. Das Schema ist frei verwendbar (MIT). Die Daten, die ich damit bewerte, stehen nicht hier.

Von [Oliver Bock](https://theb2banswer.de), The B2B Answer. Entstanden für die Frage, welche Ratschläge zur Sichtbarkeit in ChatGPT belegt sind. Funktioniert für jedes Feld, in dem viel behauptet wird.

## Das Schema

Jede Aussage bekommt sechs Angaben.

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
| **C1** belegt | Offengelegte Methode und klarer Mechanismus, dazu mehrere unabhängige Stimmen oder eine eigene Messung über mindestens 30 Tage; keine Gegenbelege. Plattformdoktrin (G0) reicht für das, was die Plattform über sich selbst sagt. |
| **C2** plausibel | Mehrere G3/G4-Quellen in dieselbe Richtung, oder eine G2-Quelle mit Einschränkungen |
| **C3** Vermutung | Eine Quelle, oder Quellen widersprechen sich |

Gewicht und Konfidenz sind getrennt. Eine eigene Messung (G1) mit kleiner Stichprobe kann C2 sein. Eine Anbieterstudie (G3), die drei andere bestätigen, auch.

### 3. Geltungsbereich

Wo die Aussage gilt (Markt, Sprache, Branche, Plattform) und wo sie nie gemessen wurde. Die meisten Aussagen sind nicht falsch, sondern aus einem anderen Markt übernommen.

### 4. Aufstieg und Verfall

Was die Aussage auf C1 heben würde und was sie streicht. So wird aus einer Note ein Test, den man wiederholen kann.

### 5. Zwei Daten

- **Erstbeobachtung:** wann die Aussage zum ersten Mal auftauchte.
- **Zuletzt bestätigt:** wann ich sie zuletzt gegen eine Quelle geprüft habe. Älter als sechs Monate ohne Bestätigung: Status auf „Beobachtung“.

### 6. Status

`aktiv` · `Beobachtung` · `zurückgezogen`. Zurückgezogene Aussagen bleiben stehen, mit Grund. Sie sind die wertvollsten Zeilen, weil sie zeigen, was sich als falsch herausgestellt hat.

## Die Regeln dazu

1. Jede Zahl kommt aus einer Quelle, die ich benennen kann. Keine Zahl ohne Datum.
2. Zu gut oder zu schlecht heißt: erst die Methode prüfen, dann berichten. 100 Prozent, 0 von 24, ein Sprung um das Zehnfache sind Anlässe für eine Kontrollmessung mit einem zweiten Werkzeug.
3. Vergleiche nur mit denselben Fragen und demselben Instrument.
4. Jede Messung trägt eine Methodenzeile: Datum, Stichprobe, Läufe, Instrument, Schlagseite des Instruments, Grenzen.
5. Jeder Messfehler bekommt eine Zeile im Fehlerlog, eine je Ursache, damit er nicht zweimal passiert.
6. Listenfragen an KI-Systeme („Welche Anbieter …“) zählen erst nach mindestens fünf Läufen je Frage als Messung. Markenfragen („Wer ist …“) sind stabil, Listenfragen nicht.
7. Quellen zählen, nicht Kanäle. Dieselbe Person mit derselben Aussage auf LinkedIn, im Podcast und im Blog ist eine Stimme. Quellen, die sich gegenseitig zitieren, zählen zusammen höchstens anderthalb. Wer an der Aussage verdient, zählt halb. Vor jedem „alle sagen das“ fragen: Wer würde widersprechen? Gibt es niemanden, ist es keine Übereinstimmung, sondern eine Blase.
8. Was ein KI-Agent bewertet hat, zählt bis zur Durchsicht durch einen Menschen höchstens C2. Ausgenommen ist nur Plattformdoktrin (G0).
9. Ändert eine Quelle oder Messung eine Überzeugung, kommt eine Zeile ins Umgestimmt-Log: Datum, Auslöser, vorher, nachher. Nur anhängen, nie umschreiben.
10. Zahlen kommen aus Code über den vollständigen Datensatz, und Zeilenzahl und Zeilensumme stehen gegen die Gesamtsumme, bevor gedeutet wird. Search Console, Ahrefs und jede gekappte Schnittstelle liefern nur die oberen Zeilen.

## Durchgerechnetes Beispiel

Aussage: „Eine llms.txt bringt dich in die KI-Suche.“

1. **Erstbeobachtung** in Beiträgen von Anbietern und Agenturen: G3 bis G5, C3.
2. **An der Quelle geprüft:** Googles Leitfaden zu generativer KI in der Suche sagt, Google Search nutzt llms.txt und andere besondere KI-Dateien nicht. Das ist G0.
3. **Ergebnis:** Für Google Search ist die Aussage zurückgezogen, mit dem G0-Gegenbeleg als Grund. Der Geltungsbereich zählt: Die Google-Quelle sagt nichts über ChatGPT oder Perplexity. Dort bleibt die Aussage C3 und ungemessen.
4. **Aufstieg und Verfall:** Für Google wieder öffnen, wenn sich Googles Dokumentation ändert (der Monatslauf öffnet dann ein Issue). Für andere Systeme braucht es erst eine eigene Messung.

## Vorlage

`vorlage/aussagen.csv` ist eine Tabelle, getrennt mit Komma, UTF-8 (in Excel über „Daten > Aus Text/CSV“ öffnen), mit den Spalten Aussage, Quellengewicht, Konfidenz, Geltungsbereich, Aufstieg wenn, Verfällt wenn, Erstbeobachtung, Zuletzt bestätigt, Status, Geprüft von (Mensch oder Agent), Quelle, Notiz und vier Beispielzeilen, darunter das Beispiel oben. In Notion, Airtable oder einer Tabellenkalkulation importieren, Gewicht und Konfidenz als Auswahlfelder anlegen, fertig.

Nützliche Ansichten: „Überfällig“ (aktiv, Zuletzt bestätigt älter als sechs Monate, älteste zuerst), „Publizierbar“ (G0 bis G2, aktiv) und „Durchsicht offen“ (Geprüft von Agent).

## Mit GitHub arbeiten

Die Aussagen liegen als CSV in einem Repository, GitHub übernimmt den Rest:

- **Tabellenansicht:** GitHub zeigt die CSV als durchsuchbare Tabelle, mit Verlauf je Zeile über die Commits.
- **Durchsicht als Pull Request:** Ein Agent legt neue Zeilen per PR an (`Geprüft von: Agent`, höchstens C2). Du prüfst, hebst die Konfidenz, mergst. Der PR ist der Nachweis für Regel 8.
- **Automatische Prüfung:** `pruefen.py` läuft bei jedem Push und PR auf `vorlage/` und einmal im Monat (`.github/workflows/pruefen.yml`). Es bricht ab bei ungültigen Werten, bei Agent-Zeilen über C2 und bei zurückgezogenen Zeilen ohne Grund. Überfällige Zeilen und Zeilen ohne Geltungsbereich stehen als Hinweis in der Zusammenfassung des Laufs.
- **Quellenänderung als Issue:** Der Monatslauf von `fetch.py` öffnet ein Issue, wenn sich eine Quelle mit G0 bis G2 ändert (siehe unten).

```
python pruefen.py                    # prüft vorlage/aussagen.csv
python pruefen.py meine-aussagen.csv # eigene Datei
```

Für die eigene Wissensbasis: Datei kopieren, im Workflow den Pfad ändern, Repository privat lassen.

## Quellen monatlich prüfen

`fetch.py` ruft die Seiten aus `sources.yaml` ab, legt den Text unter `sources/` ab und schreibt eine neue Fassung nur, wenn sich der Inhalt geändert hat. Die GitHub Action läuft am 1. jedes Monats. Ändert sich eine Quelle mit Gewicht G0, G1 oder G2, öffnet sie ein Issue mit dem Diff. Dann: Quelle neu lesen, Aussage prüfen, „Zuletzt bestätigt“ setzen, Issue schließen.

```
pip install -r requirements.txt
python fetch.py          # abrufen, nichts committen
python fetch.py --commit # so läuft es in der Action
```

Eine Quelle ist eine Zeile in `sources.yaml` mit `slug`, `url`, `gewicht`, `gelesen` und optional `link` auf die Zeile in der eigenen Wissensbasis. Als Beispiel stehen drei Seiten von Google Search Central darin; ihr abgerufener Text liegt unter `sources/`.

## Lizenz

Schema, Vorlage und Skripte: MIT (siehe `LICENSE`). Die Texte unter `sources/` sind Abrufe von Google Search Central, © Google, lizenziert unter [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); die Quelle steht oben in jeder Datei. Sie fallen nicht unter die MIT-Lizenz.

## Was hier nicht steht

Die 139 bewerteten Aussagen zur Sichtbarkeit in ChatGPT, die Messdaten dahinter und die vollständige Quellenliste. Das Schema ist die Methode, die Daten sind die Arbeit.
