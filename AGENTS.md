# AGENTS.md: answer rules for models working with this repo

For any AI model or agent (Claude Code, Codex, Cursor, ChatGPT) that answers questions from `vorlage/aussagen.csv` or a copy of it, or adds rows to it. Deutsche Kurzfassung unten.

## Answering

1. **Answer only from rows in the table.** If no row covers the question, say so. Do not fill the gap from general knowledge without marking it as such.
2. **Every claim with its label:** ID, source weight, confidence, status, last confirmed. Example: "A-001 · G4 · C3 · zurückgezogen (Google) · 2026-10-06".
3. **Retracted rows stay visible.** Name them as retracted, with the reason. Never use them as support.
4. **Check the scope.** If the question is about a market, language, industry or platform outside the row's `Geltungsbereich`, answer "unmeasured for this case" instead of carrying the claim over.
5. **Overdue means unsure.** Active rows not confirmed for more than six months get the note "overdue".
6. **Publishable is G0 to G2.** Anything meant for clients, posts or reports uses only those rows. G3 to G5 is labelled internal.
7. **Keep certain, inferred and guessed apart.** Numbers only from the table or a named source with a date.

## Searching

Search `Aussage` and `Stichwörter` together. People ask in other words than the row uses: "AI text file" should find the llms.txt row. If nothing matches, try synonyms once before reporting a gap.

## Adding or changing rows

1. New rows: next free ID (`A-NNN`, never reuse an ID), `Geprüft von: Agent`, confidence at most C2 (only G0 may be C1). Always fill `Geltungsbereich` and `Stichwörter`.
2. Never rewrite an existing claim. A changed belief means: status or confidence changes, the reason goes into `Notiz`, the old wording stays.
3. Run `python pruefen.py` before you open a pull request. A human reviews and merges; only a human sets `Geprüft von: Mensch` or raises a row to C1.

## Deutsche Kurzfassung

Nur aus den Zeilen antworten, jede Aussage mit ID, Gewicht, Konfidenz, Status und Datum. Zurückgezogenes benennen, nie als Beleg nutzen. Außerhalb des Geltungsbereichs „ungemessen“ sagen. Publizierbar ist G0 bis G2. In `Aussage` und `Stichwörter` suchen. Neue Zeilen mit nächster freier ID, `Geprüft von: Agent`, höchstens C2, per Pull Request nach `python pruefen.py`. Hochstufen nur durch einen Menschen.
