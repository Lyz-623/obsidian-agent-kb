# CLAUDE.md

This repository is an **Obsidian vault**: an explainer-article knowledge base maintained by Claude Code agents. The vault root is the repository root. The sample content (one series on the damped, driven harmonic oscillator) shows the conventions in action; users replace it with their own topic.

## Where things are

- `90 System/kb.config.json` — folder names, frontmatter `type` values, front notes, reference labels (`Eq.`, `Fig.`, `Table`) and every dashboard string. Never hard-code these; read them from the config.
- `90 System/CONVENTIONS.md` — the writing and markup rules for this vault (article structure, callout cards, block ids, figures, equations, citations, term cards). Read it before editing any note.
- `10 Series/` series maps and the front notes "About this collection" and "Notation and conventions" (single source of truth for symbols); `20 Articles/` articles; `30 Terms/` term cards; `40 Literature/` literature notes; `Assets/` figures; `Templates/` note templates.
- `90 System/outline-sync.py` — regenerates the series maps from the articles.
- `90 System/figure-scripts/` — matplotlib scripts (`figstyle.py` shared style) that write the PNGs in `Assets/`; `README.md` lists script → outputs.
- `90 System/home/view.js` + `Home.md` — the dashboard (Dataview JS); `.obsidian/plugins/kb-open-home/` — local plugin that opens Home and records reading positions; `.obsidian/snippets/kb-article.css`, `kb-home.css` — styles.

## How to work here

- Use the **`kb-notes` skill** (`.claude/skills/kb-notes/`, or installed globally in `~/.claude/skills/kb-notes/`) for every knowledge-base task: optimising or rewriting a note, writing a new article with term cards, coordinating parallel agents, and checking cross-references. Follow its SKILL.md workflows and hard rules.
- Never write text containing backslashes (LaTeX) through shell heredocs, `echo` or string literals; use the file write/edit tools. No TAB characters in notes. Keep block ids (`^id`).
- Figures are computed by scripts in `90 System/figure-scripts/`; look at every PNG you produce and fix overlaps by changing the script.

## After every note edit

Run from the vault root, with `PYTHONIOENCODING=utf-8`:

```
python .claude/skills/kb-notes/scripts/note_stats.py --vault . --write "<Note>"   # frontmatter counts
python "90 System/outline-sync.py"                                               # regenerate series maps
python "90 System/outline-sync.py" --check                                       # must report "No differences."
python .claude/skills/kb-notes/scripts/xref.py --vault .                         # must report "problems 0"
python .claude/skills/kb-notes/scripts/linkcheck.py --vault . --strict           # must report "broken 0"
python .claude/skills/kb-notes/scripts/figure_audit.py --vault .                 # every panel explained as Fig. N(x): "problems 0"
```

(If the skill is installed globally instead, use `~/.claude/skills/kb-notes/scripts/…`.)

Do not commit, push or publish unless the user asks.
