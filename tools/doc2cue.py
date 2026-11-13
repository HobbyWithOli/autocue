#!/usr/bin/env python3
"""Turn a script (Markdown exported from a Claude Doc, or any Markdown) into an HWO Autocue script.

Usage:
  python3 tools/doc2cue.py SOURCE.md [--title "Ep 2 — Knights"] [--slug ep2-knights] [--all]

- Keeps only the "## Script" section when the doc has one (drops "At a glance", voice notes,
  shot list and so on). --all keeps everything after the title.
- Section headings (## or ###) become autocue sections; "— 0:00 to 0:15" timings show beside them.
- Paragraphs that are wholly *italic* become notes (B-roll, on-screen text), which the app can hide.
- [Square brackets] are highlighted as things to fill in on the day.
- Writes scripts/<slug>.md and adds/updates the entry in scripts/index.json.
"""
import argparse, datetime, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")


def slugify(s):
    s = s.lower().replace("&", "and")
    s = re.sub(r"[—–]", "-", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:60].strip("-") or "script"


def convert(md, keep_all=False):
    md = md.replace("\r", "").replace("&#32;", " ")
    title = ""
    m = re.search(r"^#\s+(.+)$", md, re.M)
    if m:
        title = m.group(1).strip()
        md = md[m.end():]
    body = md
    if not keep_all:
        sec = re.search(r"^##\s+Script\s*$", md, re.M | re.I)
        if sec:
            rest = md[sec.end():]
            nxt = re.search(r"^##\s+(?!#)", rest, re.M)
            body = rest[: nxt.start()] if nxt else rest
    out = []
    for block in re.split(r"\n\s*\n", body):
        b = block.strip()
        if not b:
            continue
        if re.match(r"^times are targets", b, re.I):
            continue
        b = re.sub(r"^#{2,6}\s+", "## ", b)
        b = b.replace("\\[", "[").replace("\\]", "]")
        out.append(b)
    text = "\n\n".join(out).strip() + "\n"
    spoken = [p for p in out if not p.startswith("## ") and not re.fullmatch(r"\*[^*][\s\S]*\*", p)]
    words = len(re.sub(r"[*#\[\]]", " ", " ".join(spoken)).split())
    return title, text, words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--title")
    ap.add_argument("--slug")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    md = open(a.source, encoding="utf-8").read()
    title, text, words = convert(md, a.all)
    title = (a.title or title or "Untitled script").strip()
    title = re.sub(r"^(.*?)\s+Script\s+[—–-]\s+", r"\1 — ", title)  # "Ep 1 Script — X" -> "Ep 1 — X"
    slug = a.slug or slugify(title)
    fname = slug + ".md"
    today = datetime.date.today().isoformat()
    os.makedirs(SCRIPTS, exist_ok=True)
    with open(os.path.join(SCRIPTS, fname), "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: {title}\nupdated: {today}\n---\n\n{text}")
    idx_path = os.path.join(SCRIPTS, "index.json")
    try:
        idx = json.load(open(idx_path, encoding="utf-8"))
    except Exception:
        idx = {"scripts": []}
    idx["scripts"] = [s for s in idx.get("scripts", []) if s.get("file") != fname]
    idx["scripts"].append({"file": fname, "title": title, "updated": today, "words": words})
    idx["scripts"].sort(key=lambda s: s.get("updated", ""), reverse=True)
    json.dump(idx, open(idx_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"Wrote scripts/{fname}: '{title}', {words} spoken words (~{max(1, round(words/150))} min)")


if __name__ == "__main__":
    sys.exit(main())
