# Agent workflow: building a knowledge base with Claude Code

This tutorial walks through growing the vault from a seed topic to a multi-series knowledge base, with Claude Code agents doing the writing and the `kb-notes` skill keeping everything consistent. The examples continue the sample topic (oscillations); replace it with yours.

Throughout, you talk to one Claude Code session in the vault folder. That session acts as the **coordinator**: it plans, writes briefs, spawns execution agents, integrates their work and runs the checks. Execution agents each own exactly one note.

## 0. Set up

1. Clone the repo and open it as an Obsidian vault (see the README). Keep Obsidian open while agents work: notes update live, and the dashboard refreshes when you return to Home.
2. Start Claude Code in the vault folder:
   ```
   cd obsidian-agent-kb
   claude
   ```
   `CLAUDE.md` tells the agent what the vault is, where the config and conventions are, and to use the `kb-notes` skill. If you installed the skill globally, it is available in every vault.
3. Optional: edit `90 System/kb.config.json` (title, lede, language) and `90 System/CONVENTIONS.md` (house rules) before writing anything. Agents follow these files, so a rule you put there applies to every future article.

## 1. Seed the topic

Give the agent the scope, the audience and the sources it may use. Put real literature notes in place first: agents cite only notes that exist, and they verify claims against them.

> I want this vault to explain coupled oscillators and normal modes to first-year graduate students. Start from the existing series on damped and driven oscillations. Create literature notes for French 1971 (already there), Goldstein, Poole and Safko 2002 *Classical Mechanics* (3rd ed.) and Taylor 2005 *Classical Mechanics*, using `Templates/Literature.md`. Bibliographic data only, no PDFs.

Rewrite the two front notes for your topic early. "Notation and conventions" is the single source of truth for symbols; every agent reads it, so settle sign conventions and units there before the first article.

## 2. Outline the series

Ask for a plan, not for text. A good outline is a list of series, each with one guiding question, and within each series a list of articles, each answering one question and owning a set of concepts.

> Propose a second series, "Coupled oscillators", of 3–4 articles. For each article give the title, the question it answers, the concepts it owns, the `seq` it gets, and which concepts it uses from earlier articles. No concept may be used before the article that introduces it. Do not write anything yet.

Review and edit the plan in chat. When you approve it, have the agent create the series map from `Templates/Series map.md` (question and intro paragraph only; entries are generated) and update the previous/next navigation of the neighbouring series maps.

## 3. Have agents write articles

Once the plan is fixed, ask for the articles. The skill's Workflow B fills `references/brief-new-article.md` for each article (neighbours to read, allowed citation keys, `seq`, figure count, word range, which term cards it owns) and spawns one writer per article in parallel.

> Write the three approved articles of series 2 in parallel, one agent per article, with their term cards. Each article gets 2–3 computed figures from a script in `90 System/figure-scripts/` using `figstyle.py`. Coordinate as the skill describes and run all checks at the end.

Each writer produces: the article, its term cards, one figure script, its PNGs (viewed and fixed for overlaps), and its line in the figure-scripts README. The coordinator then renumbers `seq`, fixes the `> [!series]` navigation blocks, adds cross-links the writers proposed, runs `outline-sync.py` and the checks, and reports.

Read the new articles in Obsidian. The best feedback is concrete: "the derivation of the normal-mode frequencies jumps from step 2 to the result", "Fig. 2 should show the beat envelope, not the two modes separately".

## 4. Optimise notes in parallel waves

Articles improve in waves. A wave is one request that applies the same goals to several notes at once (Workflow A, brief `references/brief-optimise-note.md`).

> Optimise all articles of series 1 in one parallel wave. Use "Free damped oscillations" as the reference style. Goals: merge thin subsections, replace text-only explanations with a formula plus a schematic figure, keep every key derivation step by step, captions one line per panel.

Rules that make parallel waves safe:

- **One note per agent.** An execution agent edits only its own note, its own figure script, its own PNGs and its own README line. It never touches other notes, series maps or Home, and never runs outline-sync.
- **Mapping reports.** Every agent ends with the inbound mapping: old → new equation, figure and table numbers, and removed or renamed block ids and headings (or "none"). Other notes link to those numbers.
- **Backups outside the vault.** The coordinator copies each target note to its scratchpad before the wave, so a bad rewrite can be compared or restored.
- **Effort split.** Planning, briefs and independent review run on a strong model at high effort; writing and fixing agents at medium effort; mechanical fixes at low effort.

## 5. The coordinator loop

After each wave the coordinator works through `references/coordinator-checklist.md`. In short:

1. Collect the agents' reports and mappings.
2. Fix inbound references: `xref.py` reports links whose displayed number no longer matches the target (`[[Article#^id|“Article” Eq. (3)]]` where the block now holds `\tag{4}`); `--fix` rewrites them; missing ids are re-pointed by hand from the mapping.
3. Update renamed headings vault-wide; `linkcheck.py` must report `broken 0`.
4. Recompute frontmatter counts with `note_stats.py --write`.
5. Renumber `seq` and fix previous/next navigation if articles moved.
6. Run `outline-sync.py` (check, then write) so the series maps match the articles.
7. Verify new term cards (`defined_in`, the "Explained in" heading exists, listed in `terms:`).
8. For substantive rewrites, run an independent read-only review agent and apply its fixes.
9. Run the final checks and report what changed, per note.

You stay in the loop at two points: approving plans before writing starts, and reading the result after each wave. Feedback you give once ("no worked numeric examples", "captions in one line") belongs in `90 System/CONVENTIONS.md` so every later agent follows it.

## 6. Checks

All scripts are Python 3 standard library only. Run them from the vault root with `PYTHONIOENCODING=utf-8` (paths shown for the project-local skill; use `~/.claude/skills/kb-notes/scripts/` for a global install).

| Command | Checks | Clean result |
|---|---|---|
| `python .claude/skills/kb-notes/scripts/xref.py --vault .` | cross-note displayed numbers match the target's `\tag{}` or caption (`--fix`, `--local`, `--skip`) | `problems 0` |
| `python .claude/skills/kb-notes/scripts/linkcheck.py --vault . --strict` | every `[[Note#Heading]]` / `[[Note#^id]]` resolves; with `--strict` also missing notes and embedded files | `broken 0` |
| `python .claude/skills/kb-notes/scripts/note_stats.py --vault . "<Note>"` | `figures`, `equations`, `words`, `sections`, `kinds` vs body; tags 1..N; TABs; in-note links; images (`--write` updates) | no `DIFF` / `CHECK` |
| `python "90 System/outline-sync.py" --check` | series maps match the articles | `No differences.` |

## 7. Example prompts

Copy, adapt and paste into Claude Code.

- **Seed:** "Read CLAUDE.md and the conventions. Summarise what this vault expects from an article in ten bullet points, then wait."
- **Plan:** "Propose a series on <topic> for <audience>: 3–5 articles, one question each, concepts owned per article, `seq` values. Do not write yet."
- **Write:** "Write the approved articles in parallel, one agent per article, each with its term cards and 2–3 computed figures. Coordinate and run all checks."
- **Optimise one note:** "Optimise the article <Title>: it reads like a list of facts. Restructure it around the question in its first paragraph and add a schematic figure for the mechanism."
- **Optimise a wave:** "Optimise every article of series <n> in one parallel wave with <reference article> as the style reference. Report per article what was merged, cut and added."
- **Terms:** "Find concepts used in two or more articles that have no term card, and create the cards; each `defined_in` must point to the article that actually explains the concept."
- **Check and repair:** "Run xref, linkcheck, note_stats on all articles and outline-sync --check. Fix everything that is mechanical; list anything that needs my decision."
- **Restructure:** "Series 2 has grown to 7 articles. Propose a split into two series with new guiding questions and `seq` values. Wait for approval, then move content, keep block ids, fix all inbound links and regenerate the series maps."
- **Figures:** "Re-run every figure script, look at each PNG, and fix overlapping labels or legends in the scripts."
- **Literature:** "For each claim in <article> that cites <CiteKey>, check it against the source and tell me which claims you could not verify."
