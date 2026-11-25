"""Prüft vorlage/aussagen.csv (oder eine andere Datei) gegen die Regeln aus dem README.

Fehler (Exit-Code 1):
  - Gewicht oder Konfidenz außerhalb von G0 bis G5 und C1 bis C3
  - Status nicht aktiv, Beobachtung oder zurückgezogen
  - Regel 8: von einem Agenten bewertet, C1, aber nicht G0
  - zurückgezogen ohne Grund in Notiz oder Quelle

Hinweise (kein Fehler):
  - aktiv und seit mehr als sechs Monaten nicht bestätigt (überfällig)
  - ohne Geltungsbereich

Aufruf: python pruefen.py [datei.csv]
"""

import csv
import os
import sys
from datetime import date, timedelta

GEWICHTE = {f"G{i}" for i in range(6)}
KONFIDENZ = {"C1", "C2", "C3"}
STATUS = {"aktiv", "Beobachtung", "zurückgezogen"}
UEBERFAELLIG = timedelta(days=183)


def pruefen(pfad: str) -> int:
    fehler, hinweise = [], []
    heute = date.today()
    with open(pfad, encoding="utf-8", newline="") as f:
        zeilen = list(csv.DictReader(f))

    for nr, z in enumerate(zeilen, start=2):  # Zeile 1 ist die Kopfzeile
        name = (z.get("Aussage") or "").strip()[:60]
        g = (z.get("Quellengewicht") or "").strip()
        c = (z.get("Konfidenz") or "").strip()
        s = (z.get("Status") or "").strip()
        wer = (z.get("Geprüft von") or "").strip()

        if g not in GEWICHTE:
            fehler.append(f"Zeile {nr} ({name}): Quellengewicht „{g}“ unbekannt")
        if c not in KONFIDENZ:
            fehler.append(f"Zeile {nr} ({name}): Konfidenz „{c}“ unbekannt")
        if s not in STATUS:
            fehler.append(f"Zeile {nr} ({name}): Status „{s}“ unbekannt")
        if wer == "Agent" and c == "C1" and g != "G0":
            fehler.append(f"Zeile {nr} ({name}): Agent-Bewertung höchstens C2 bis zur Durchsicht (Regel 8)")
        if s == "zurückgezogen" and not ((z.get("Notiz") or "").strip() or (z.get("Quelle") or "").strip()):
            fehler.append(f"Zeile {nr} ({name}): zurückgezogen ohne Grund")

        if not (z.get("Geltungsbereich") or "").strip():
            hinweise.append(f"Zeile {nr} ({name}): kein Geltungsbereich")
        bestaetigt = (z.get("Zuletzt bestätigt") or "").strip()
        if s == "aktiv" and bestaetigt:
            try:
                if heute - date.fromisoformat(bestaetigt) > UEBERFAELLIG:
                    hinweise.append(f"Zeile {nr} ({name}): überfällig, zuletzt bestätigt {bestaetigt}")
            except ValueError:
                fehler.append(f"Zeile {nr} ({name}): Datum „{bestaetigt}“ nicht im Format JJJJ-MM-TT")

    publizierbar = sum(
        1 for z in zeilen
        if (z.get("Quellengewicht") or "").strip() in {"G0", "G1", "G2"} and (z.get("Status") or "").strip() == "aktiv"
    )
    agent_offen = sum(1 for z in zeilen if (z.get("Geprüft von") or "").strip() == "Agent")

    bericht = [
        f"## Beleg-Schema: {pfad}",
        f"{len(zeilen)} Aussagen, {publizierbar} publizierbar, {agent_offen} mit offener Durchsicht.",
        "",
    ]
    bericht += ["### Fehler", *[f"- {x}" for x in fehler], ""] if fehler else ["Keine Fehler.", ""]
    if hinweise:
        bericht += ["### Hinweise", *[f"- {x}" for x in hinweise], ""]
    text = "\n".join(bericht)
    print(text)

    zusammenfassung = os.environ.get("GITHUB_STEP_SUMMARY")
    if zusammenfassung:
        with open(zusammenfassung, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(pruefen(sys.argv[1] if len(sys.argv) > 1 else "vorlage/aussagen.csv"))
