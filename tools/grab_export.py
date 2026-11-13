#!/usr/bin/env python3
"""Save the most recent Claude Docs markdown export from this session to a file.

The Docs export tool returns the file as base64 inside its result. This finds the newest
export in the session transcripts (~/.claude/projects/**/*.jsonl) and decodes it.

Usage: python3 tools/grab_export.py OUT.md ["text that must appear in the export"]
"""
import base64, glob, os, re, sys

out = sys.argv[1]
must = sys.argv[2] if len(sys.argv) > 2 else ""
files = sorted(glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True), key=os.path.getmtime, reverse=True)
for f in files:
    found = None
    for line in open(f, encoding="utf-8", errors="ignore"):
        if "bytes_b64" not in line or "text/markdown" not in line:
            continue
        for m in re.finditer(r'bytes_b64[^A-Za-z0-9]{1,12}([A-Za-z0-9+/=]{200,})', line):
            try:
                txt = base64.b64decode(m.group(1)).decode("utf-8")
            except Exception:
                continue
            if must in txt:
                found = txt
    if found:
        open(out, "w", encoding="utf-8").write(found)
        print(f"Saved {len(found)} chars to {out}")
        sys.exit(0)
sys.exit("No markdown export found. Run the Docs export (format markdown) first, or write the file by hand.")
