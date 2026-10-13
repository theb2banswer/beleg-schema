#!/usr/bin/env python3
"""Ruft die Quellen aus sources.yaml ab und legt jede neue Fassung als Text ab (Beleg-Schema).

    python fetch.py            # abrufen und Dateien schreiben, nichts committen
    python fetch.py --commit   # zusätzlich committen (so läuft es in der Action)

Ablauf je Lauf:
1. Alle Quellen abrufen. Der erste Abruf einer Quelle ist ihre Baseline. Danach wird
   eine Datei nur neu geschrieben, wenn sich der Text (sha256) oder bei arXiv die
   Version geändert hat. Fehler überschreiben nie.
2. Bericht: CHANGELOG.md, status.json, Zusammenfassung für die Action
   ($GITHUB_STEP_SUMMARY), Ausgabe changed_g und issue.md für das Issue. Liegt das
   Aktualisierungsdatum einer Seite nach dem Lesedatum, steht das in der Zusammenfassung.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import requests
import trafilatura
import yaml

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "sources"
CHANGELOG = ROOT / "CHANGELOG.md"
STATUS = ROOT / "status.json"
ISSUE = ROOT / "issue.md"

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9,de;q=0.8"}
TIMEOUT = 45
TODAY = dt.datetime.now(dt.timezone.utc).date().isoformat()
WATCHED = {"G0", "G1", "G2", "sammlung"}  # Änderungen an diesen Gewichten öffnen ein Issue
DIFF_LIMIT = 6000  # Zeichen je Quelle im Issue


class FetchError(Exception):
    """Abruf gescheitert; der Text ist der Status für status.json."""


@dataclass
class Result:
    slug: str
    gewicht: str
    outcome: str = "ok"  # ok | neu | geändert | fehlgeschlagen
    detail: str = ""
    page_updated: str | None = None
    version: str | None = None
    diff: str = ""
    plus: int = 0
    minus: int = 0
    changelog: list[str] = field(default_factory=list)


# --- Abruf und Extraktion -------------------------------------------------


def get(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    except requests.Timeout:
        raise FetchError("timeout")
    except requests.ConnectionError as e:
        raise FetchError(f"keine Verbindung ({type(e).__name__})")
    if r.status_code >= 400:
        raise FetchError(f"HTTP {r.status_code}")
    r.encoding = r.encoding if r.encoding and r.encoding.lower() != "iso-8859-1" else r.apparent_encoding
    return r.text


def extract(html: str, url: str) -> str:
    # Klartext ohne HTML-Gerüst (z. B. raw.githubusercontent.com) unverändert übernehmen,
    # trafilatura würde ihn verwerfen.
    if not re.search(r"<(html|head|body)\b", html[:4096], re.IGNORECASE):
        lines = [line.rstrip() for line in html.strip().splitlines()]
        if len("\n".join(lines)) < 200:
            raise FetchError("kein Text extrahiert")
        return "\n".join(lines) + "\n"
    text = trafilatura.extract(
        html,
        url=url,
        output_format="markdown",
        include_formatting=True,
        include_tables=True,
        include_links=False,
        include_comments=False,
        include_images=False,
    )
    if not text or len(text.strip()) < 200:
        raise FetchError("kein Text extrahiert")
    lines = [line.rstrip() for line in text.strip().splitlines()]
    return "\n".join(lines) + "\n"


MONTHS = {
    m: i
    for i, names in enumerate(
        [
            ("january", "januar"), ("february", "februar"), ("march", "märz"), ("april",),
            ("may", "mai"), ("june", "juni"), ("july", "juli"), ("august",),
            ("september",), ("october", "oktober"), ("november",), ("december", "dezember"),
        ],
        start=1,
    )
    for m in names
}


def to_iso(raw: str) -> str | None:
    raw = raw.strip()
    try:
        if m := re.fullmatch(r"(\d{4})-(\d{2})-(\d{2}).*", raw):
            return dt.date(*map(int, m.groups())).isoformat()
        if m := re.fullmatch(r"(\d{1,2})\.\s?(\d{1,2})\.\s?(\d{4})", raw):
            d, mo, y = map(int, m.groups())
            return dt.date(y, mo, d).isoformat()
        if m := re.fullmatch(r"(\d{1,2})\.\s?([A-Za-zäÄ]+)\s(\d{4})", raw):
            return dt.date(int(m[3]), MONTHS[m[2].lower()], int(m[1])).isoformat()
        if m := re.fullmatch(r"([A-Za-z]+)\s(\d{1,2}),?\s(\d{4})", raw):
            return dt.date(int(m[3]), MONTHS[m[1].lower()], int(m[2])).isoformat()
    except (KeyError, ValueError):
        return None
    return None


DATE = r"(\d{4}-\d{2}-\d{2}|\d{1,2}\.\s?\d{1,2}\.\s?\d{4}|\d{1,2}\.\s?[A-Za-zäÄ]+\s\d{4}|[A-Z][a-z]+\s\d{1,2},?\s\d{4})"


def markers(html: str, url: str) -> tuple[str | None, str | None]:
    """page_updated und version aus dem HTML."""
    version = None
    if "arxiv.org/abs/" in url:
        found = [int(v) for v in re.findall(r"\[v(\d+)\]", html)]
        version = f"v{max(found)}" if found else None

    visible = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    if "developers.google.com" in url:
        m = re.search(r"Last updated (\d{4}-\d{2}-\d{2}) UTC", visible)
        return (m[1] if m else None), version

    for pattern in (
        rf"(?:[Aa]ktualisiert|[Zz]uletzt aktualisiert)(?: am)?:?\s*{DATE}",
        rf"(?:[Ll]ast updated|[Uu]pdated)(?: on)?:?\s*{DATE}",
    ):
        if (m := re.search(pattern, visible)) and (iso := to_iso(m[1])):
            return iso, version
    for pattern in (
        r'property="article:modified_time"\s+content="([^"]+)"',
        r'content="([^"]+)"\s+property="article:modified_time"',
        r'"dateModified"\s*:\s*"([^"]+)"',
    ):
        if (m := re.search(pattern, html)) and (iso := to_iso(m[1])):
            return iso, version
    return None, version


# --- Dateien ---------------------------------------------------------------


def read_source(slug: str) -> tuple[dict, str] | None:
    path = SOURCES / f"{slug}.md"
    if not path.exists():
        return None
    _, front, text = path.read_text(encoding="utf-8").split("---\n", 2)
    return yaml.safe_load(front), text.lstrip("\n")


def write_source(src: dict, text: str, page_updated, version) -> None:
    meta = {
        "slug": src["slug"],
        "url": src["url"],
        "link": link_url(src),
        "gewicht": src["gewicht"],
        "gelesen": src["gelesen"],
        "fetched": TODAY,
        "sha256": sha(text),
        "page_updated": page_updated,
        "version": version,
    }
    front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True)
    (SOURCES / f"{src['slug']}.md").write_text(f"---\n{front}---\n\n{text}", encoding="utf-8")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def link_url(src: dict) -> str | None:
    """Optionaler Link auf die Zeile in der eigenen Wissensbasis (Wiki, Tabelle, Datenbank)."""
    return src.get("link") or None


def diff_stats(old: str, new: str, slug: str) -> tuple[str, int, int]:
    lines = list(
        difflib.unified_diff(
            old.splitlines(), new.splitlines(), f"{slug} vorher", f"{slug} jetzt", lineterm="", n=1
        )
    )
    plus = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
    minus = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
    return "\n".join(lines), plus, minus


CHANGELOG_HEAD = """# Änderungsprotokoll

Neueste Einträge oben. Zeilen: hinzugekommen / entfallen gegenüber der vorigen Fassung.

| Datum | Quelle | Art | Zeilen | page_updated | Link |
|---|---|---|---|---|---|
"""


def changelog_row(src: dict, art: str, plus: int = 0, minus: int = 0, page_updated=None) -> str:
    link = f"[Link]({link_url(src)})" if link_url(src) else "–"
    zeilen = f"+{plus} / −{minus}" if plus or minus else "–"
    return f"| {TODAY} | {src['slug']} | {art} | {zeilen} | {page_updated or '–'} | {link} |"


def prepend_changelog(rows: list[str]) -> None:
    """Neue Zeilen direkt unter die Tabellenüberschrift, die neueste ganz oben."""
    if not rows:
        return
    content = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else CHANGELOG_HEAD
    head, sep, rest = content.partition("|---|---|---|---|---|---|\n")
    CHANGELOG.write_text(head + sep + "\n".join(reversed(rows)) + "\n" + rest, encoding="utf-8")


# --- Git -------------------------------------------------------------------


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def commit(message: str) -> str | None:
    git("add", "sources", "CHANGELOG.md", "status.json")
    if not git("status", "--porcelain", "sources", "CHANGELOG.md", "status.json").strip():
        return None
    git("commit", "-q", "-m", message)
    return git("rev-parse", "HEAD").strip()


# --- Live-Abruf ------------------------------------------------------------


def live(src: dict, status: dict) -> Result:
    slug = src["slug"]
    res = Result(slug, src["gewicht"])
    before = status.get(slug, {}).get("status")
    try:
        html = get(src["url"])
        text = extract(html, src["url"])
    except FetchError as e:
        res.outcome, res.detail = "fehlgeschlagen", str(e)
        if before != str(e):
            status[slug] = {"status": str(e), "since": TODAY}
            if before in (None, "ok"):
                res.changelog.append(changelog_row(src, f"nicht erreichbar ({e})"))
        return res

    res.page_updated, res.version = markers(html, src["url"])
    if before != "ok":
        status[slug] = {"status": "ok", "since": TODAY}
        if before is not None:
            res.changelog.append(changelog_row(src, "wieder erreichbar", page_updated=res.page_updated))

    existing = read_source(slug)
    if existing is None:
        write_source(src, text, res.page_updated, res.version)
        res.outcome, res.plus = "neu", len(text.splitlines())
        res.changelog.append(changelog_row(src, "neu", res.plus, 0, res.page_updated))
        return res

    meta, old = existing
    new_version = bool(res.version and res.version != meta.get("version"))
    if meta.get("sha256") == sha(text) and not new_version:
        return res

    res.diff, res.plus, res.minus = diff_stats(old, text, slug)
    art = f"neue Version {res.version}" if new_version else "geändert"
    res.outcome, res.detail = "geändert", art
    write_source(src, text, res.page_updated, res.version)
    res.changelog.append(changelog_row(src, art, res.plus, res.minus, res.page_updated))
    return res


# --- Bericht ---------------------------------------------------------------


def seit_gelesen(page_updated: str | None, gelesen: str | None) -> str:
    """Vergleicht das Aktualisierungsdatum der Seite mit dem Lesedatum."""
    if not gelesen:
        return "–"
    if not page_updated:
        return "kein Datum auf der Seite"
    return "**nach dem Lesen aktualisiert**" if page_updated > gelesen else "unverändert laut Datum"


def report(results: list[Result], sources: dict, commit_sha: str | None) -> list[str]:
    rows = ["| Quelle | Gewicht | Ergebnis | page_updated | Version | gelesen | Seit gelesen |", "|---|---|---|---|---|---|---|"]
    for r in results:
        ergebnis = {"ok": "ok, unverändert", "neu": "neu", "geändert": f"**{r.detail}** (+{r.plus} / −{r.minus})"}.get(
            r.outcome, f"**fehlgeschlagen:** {r.detail}"
        )
        gelesen = sources[r.slug].get("gelesen")
        rows.append(
            f"| {r.slug} | {r.gewicht} | {ergebnis} | {r.page_updated or '–'} | {r.version or '–'} "
            f"| {gelesen or '–'} | {seit_gelesen(r.page_updated, gelesen)} |"
        )
    summary = f"## Quellen-Abruf {TODAY}\n\n" + "\n".join(rows) + "\n"
    print(summary)
    if path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(path, "a", encoding="utf-8") as f:
            f.write(summary)

    watched = [r for r in results if r.outcome == "geändert" and r.gewicht in WATCHED]
    repo = os.environ.get("GITHUB_REPOSITORY")
    parts = [
        "Diese Quellen haben sich seit der letzten abgelegten Fassung geändert. "
        "Quelle neu lesen, die Aussage in der Wissensbasis prüfen (Zuletzt bestätigt, Kernzahl), dann das Issue schließen. "
        "Bei einer Sammlung (gewicht „sammlung“) die neuen Einträge sichten; in die Wissensbasis kommt eine Zahl "
        "nur mit gelesener Primärquelle, nie mit der Sammlung als Beleg.\n"
    ]
    for r in watched:
        src = sources[r.slug]
        link = f"https://github.com/{repo}/commit/{commit_sha}" if repo and commit_sha else "–"
        diff = r.diff if len(r.diff) <= DIFF_LIMIT else r.diff[:DIFF_LIMIT] + "\n… (gekürzt, vollständig im Commit)"
        parts.append(
            f"## {r.slug} ({r.gewicht})\n\n- Art: {r.detail}, +{r.plus} / −{r.minus} Zeilen\n"
            f"- page_updated: {r.page_updated or '–'}\n- Quelle: {src['url']}\n"
            f"- Link: {link_url(src) or '–'}\n- Commit: {link}\n\n```diff\n{diff}\n```\n"
        )
    if watched:
        ISSUE.write_text("\n".join(parts), encoding="utf-8")
    elif ISSUE.exists():
        ISSUE.unlink()
    if path := os.environ.get("GITHUB_OUTPUT"):
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"changed_g={', '.join(r.slug for r in watched)}\n")
    return [r.slug for r in watched]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true", help="Änderungen committen")
    parser.add_argument("--only", nargs="*", help="nur diese Slugs (zum Testen)")
    args = parser.parse_args()

    sources = {s["slug"]: s for s in yaml.safe_load((ROOT / "sources.yaml").read_text(encoding="utf-8"))}
    for s in sources.values():
        s["gelesen"] = str(s["gelesen"]) if s.get("gelesen") else None
    selected = [sources[s] for s in args.only] if args.only else list(sources.values())
    SOURCES.mkdir(exist_ok=True)
    if not CHANGELOG.exists():
        CHANGELOG.write_text(CHANGELOG_HEAD, encoding="utf-8")
    if not STATUS.exists():
        STATUS.write_text("{}\n", encoding="utf-8")
    status = json.loads(STATUS.read_text(encoding="utf-8"))

    results = []
    for src in selected:
        res = live(src, status)
        results.append(res)
        print(f"{src['slug']}: {res.outcome} {res.detail}".rstrip(), file=sys.stderr)

    STATUS.write_text(json.dumps(status, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    prepend_changelog([row for r in results for row in r.changelog])

    changed = [r.slug for r in results if r.changelog]
    commit_sha = commit(f"Quellen-Update {TODAY}: {', '.join(changed)}") if args.commit and changed else None

    report(results, sources, commit_sha)
    if all(r.outcome == "fehlgeschlagen" for r in results):
        print("Alle Quellen fehlgeschlagen.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
