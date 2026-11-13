# HWO Autocue

A phone teleprompter for Hobby with Oli scripts. Live at https://hobbywitholi.github.io/autocue/ (add it to your home screen).

- **Scripts** live in `scripts/` as Markdown, listed in `scripts/index.json`. The app shows every script in the index.
- **Format:** `## Section — 0:00 to 0:15` headings, plain paragraphs are read aloud, paragraphs wholly in `*italics*` are notes (hide them with the Notes button), `[square brackets]` are highlighted as things to fill in.
- **Adding a script:** `python3 tools/doc2cue.py source.md` writes `scripts/<slug>.md` and updates the index, then commit and push. `tools/grab_export.py` saves a Claude Docs markdown export from the session to a file first.
- **Controls:** tap the text to play or pause, drag to scroll, WPM −/+ for speed, A−/A+ for text size, Sections to jump, Mirror for teleprompter glass, 3-2-1 countdown. Bluetooth remotes and keyboards: Space/Enter play, ↑/↓ speed, ←/→ or Page Up/Down jump sections. The screen stays awake while prompting, and it remembers where you stopped.
