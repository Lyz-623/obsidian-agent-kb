---
name: kb-notes
description: Maintain an Obsidian explainer-article knowledge base (a vault with a `*/kb.config.json`, e.g. `90 System/kb.config.json`) whose notes are long-form articles, series maps, term cards and literature notes. Use when the user asks to optimise, rewrite, restructure or deepen a note/article; write a new article for a series; add or fix term cards; check or fix cross-references, equation/figure/table numbers or broken heading/block links; sync the outline or series maps; renumber the reading order; or reorganise series in such a vault (including requests in other languages, e.g. 优化笔记, 新写一篇文章, 术语卡片, 检查交叉引用, 同步大纲). Not for general Markdown editing outside such a vault.
---

# kb-notes

Workflows and checkers for an Obsidian knowledge base built from long-form explainer **articles** (one question each, H2 → H3, callout cards, numbered key equations, computed figures), **series maps** (generated outline per series), **term cards** and **literature notes**, with a frontmatter-driven home dashboard.

Skill files (paths relative to this SKILL.md):

- `references/conventions-template.md` — generic writing and markup conventions.
- `references/brief-optimise-note.md` — brief for a per-note rewrite agent.
- `references/brief-new-article.md` — brief for a new-article agent (+ term cards).
- `references/coordinator-checklist.md` — integration steps after a wave of agents.
- `scripts/xref.py` — cross-note displayed-number checker / fixer.
- `scripts/linkcheck.py` — heading / block-id link checker (`--strict`: also missing notes and files).
- `scripts/note_stats.py` — recompute and write frontmatter counts; per-note sanity checks.

Run every script with `PYTHONIOENCODING=utf-8 python <script> --vault "<VAULT>" …`. They are Python 3 stdlib only and read the vault config.

## 1. Orient first (every task)

1. **Find the vault and config.** Use the path the user gives, else search upward from the cwd for a directory that has `*/kb.config.json` one level below it (normally `90 System/kb.config.json`; any language). The scripts do the same discovery when `--vault` is omitted.
2. **Read `kb.config.json`.** Note `folders` (series, articles, terms, literature, assets, system, templates), `types` (frontmatter `type` values), `front_notes`, `labels` (equation / figure / table words), `home`, `conventions`. Never hard-code folder names, type values or labels; take them from the config.
3. **Read the conventions file** at `conventions` (e.g. `90 System/CONVENTIONS.md`). It is the vault's localised copy of `references/conventions-template.md` and overrides it. If the vault has none, use the template and offer to create a localised copy.
4. **Read the user's memory/feedback** for the vault if present; explicit user instructions override conventions.
5. **Read one exemplary article** in full (ask the user or pick the most recently optimised one) plus the notation front note. Mirror the exemplar.
6. Derived reference formats (from `labels`): equation ref `{equation} ({n})`; figure caption `**{figure} {n}**`, ref `{figure} {n}`; table caption `**{table} {n}**`, ref `{table} {n}`. Cross-note: `[[Article#^id|"Article" {equation} (n)]]`.

## 2. Workflow A — optimise / rewrite existing notes

1. Clarify scope only if unclear (which notes; what the user disliked). Otherwise proceed with the default goals in `references/brief-optimise-note.md`.
2. Baseline: run `xref.py` and `linkcheck.py`; record pre-existing problems.
3. Back up each target note to the session scratchpad (never inside the vault).
4. **One note:** do it yourself following the brief, or delegate to one agent.
   **Several notes:** write the brief once to the scratchpad (fill every `<…>` slot: vault, exemplar, user request verbatim, reading order, standard example parameters), then spawn one agent per note **in parallel**. Each agent edits only its own note, figure script(s), PNGs and README line.
5. Integrate with `references/coordinator-checklist.md` (inbound number fixes, headings, stats, outline sync, final checks).
6. Report per note: new outline, what was cut/merged, new figures, fixes applied, anything unverified.

## 3. Workflow B — write a new article (and term cards)

1. Agree the plan with the user: title(s), the question each answers, position in the reading order (`series_no`, `seq`), and which concepts it owns. Check that no later article's concept is needed and that no existing article already owns it.
2. Decide the new global `seq` order; list the term cards to create and assign each to exactly one writer.
3. Fill `references/brief-new-article.md` (neighbour articles to read for notation, allowed citation keys from the literature folder, figure count, word range) and spawn one writer per article in parallel.
4. Coordinator: renumber `seq` of existing articles, fix previous/next `> [!series]` blocks, update the series map intro and the "about" note by hand, run outline sync, add the cross-links writers proposed, verify term cards (`defined_in`, "explained in" heading exists, listed in `terms:`).
5. For new term cards only (no article): copy the shape of an existing card exactly (see conventions, "Term cards"); `defined_in` must point to the article that actually explains the term and the linked heading must exist.

## 4. Workflow C — check and repair (cross-references, links, counts, outline)

Run in this order and fix until clean:

1. `xref.py --vault V` — every `[[Note#^id|… {label} n …]]` shows the target's real number. `--fix` rewrites mismatches when the target has exactly one number; `MISSING id` and `NO-NUMBER` need a manual fix. `--local` also checks in-note `[[#^id|…]]`. `--skip NOTE…` ignores notes other agents are editing.
2. `linkcheck.py --vault V` — every `[[Note#Heading]]` / `[[Note#^id]]` resolves → `broken 0`. Add `--strict` to catch links to missing notes and missing embedded files.
3. `note_stats.py --vault V NOTE…` — compares `figures`, `equations`, `words`, `sections`, `kinds` with the body and checks tags 1..N, figure/table numbers 1..N, TABs, in-note links, images. `--write` updates the frontmatter (keeps newline style).
4. Outline sync: run the vault's own script in the system folder (`outline-sync.py` or `outline_sync.py`) with `--check`; only run it in write mode when the user's task involves editing notes or the user asks. It is vault-specific and not part of this skill.
5. Report the counts before and after.

## 5. Workflow D — restructure the knowledge base

Moving, splitting, merging or renaming articles or series:

1. Propose the new structure (series list, article list with `seq`, owners of each concept) and get the user's approval before moving content.
2. Rename notes with a method that updates links (Obsidian rename, or a vault-wide replace of `[[Old` → `[[New` including `[[Old#` and `[[Old|`); never leave both names.
3. When content moves between articles, carry its block ids with it and update inbound links to point at the new note; renumber equations/figures/tables in both notes; run `xref.py --fix`.
4. Update `series`, `series_no`, `seq` in frontmatter; series maps (create one per new series from the template; intro paragraph and guiding question by hand); previous/next navigation; the "about" note.
5. Run Workflow C to clean, then outline sync.
6. Respect the home scope: graph, articles, term cards, literature — no progress checklists, mastery levels or export features.

## 6. Coordinator rules for parallel agents

- **One note per agent.** Execution agents edit only their own note, own figure script(s), own new PNGs and their own README line. They never edit other notes, term cards they were not assigned, series maps, the home note, and never run outline sync.
- **The coordinator alone** applies inbound link fixes from the agents' mapping reports, renumbers `seq`, updates series maps and navigation, runs outline sync and all checks.
- Every agent's final report must include the inbound mapping (old → new numbers, removed/renamed ids and headings) or "none".
- **Model allocation:** planning, brief writing and independent review on a strong model at high effort; execution agents (writing, rewriting, fixing, figure scripts) at medium effort; purely mechanical work (applying listed fixes, link/stat checks) at low effort. Do not use high effort for execution.
- Briefs live in the session scratchpad, not in the vault. Give each agent the brief path and its single note.
- Before reporting done, the coordinator runs: `xref.py` → `problems 0`, `linkcheck.py` → `broken 0`, outline sync `--check` → no differences, `note_stats.py` on each edited note → no DIFF/CHECK.

## 7. Hard rules

- **Never write text containing backslashes through shell heredocs, `echo`, or programming-language string literals** — LaTeX such as `\tau`, `\nu`, `\left`, `\frac`, `\beta` turns into TAB, newline, form-feed or backspace characters. Write content with the file-write/edit tools (into the note directly, or into scratchpad chunks spliced by a script that only reads and moves text). Scripts that must contain regexes go in files written by the Write tool, using raw strings.
- **No TAB characters** in notes.
- **Keep block ids** (`^id`) when the content survives; other notes link to them. Report every removed or renamed id.
- **Number key equations 1..N in order** (`\tag{n}`), figures 1..N, tables 1..N, per article; update in-note references; report changed numbers that other notes display.
- **Update frontmatter counts** (`figures`, `equations`, `words`, `sections`, `kinds`) after every edit — `note_stats.py --write`.
- **Concept order:** never use a concept before the article (by `seq`) that introduces it; link back rather than re-derive.
- **Figures are computed** by scripts in the system folder, viewed after rendering, redrawn (not patched) when flawed; no backup copies in the vault.
- **Verify claims** against the cited literature; do not assume the user or an earlier note is right. Citations stay bare `[[CiteKey|Author Year]]`.
- Preserve each file's newline style (CRLF/LF) and UTF-8 encoding. The scripts already do.
- Do not delete user content the user did not point at without asking; do not commit, push or publish unless asked.
