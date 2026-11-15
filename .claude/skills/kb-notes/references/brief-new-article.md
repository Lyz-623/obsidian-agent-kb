# Brief: write one new article and its term cards (per-article execution agent)

Fill the `<…>` slots; one agent per new article; medium effort. The "Hard rules" and "Before finishing" sections of `brief-optimise-note.md` apply in full — include them or point the agent to that file.

---

You are writing ONE new article for series `<series_no> <Series map>` of an Obsidian knowledge-base vault.

- Vault root: `<VAULT>`; config `<VAULT>/<system>/kb.config.json`; conventions `<VAULT>/<conventions path>` (binding — read first).
- Skill scripts: `<SKILL>/scripts/`. Shared rules: `<SKILL>/references/brief-optimise-note.md` sections "Figures", "Hard rules", "Before finishing".

## Why this article exists

<The gap it fills, the question it answers, who reads it.>

New series order (use these `seq` values; do not change other articles' frontmatter):

- seq <a> **<New article>** (new, yours)
- seq <b> <Existing article> (existing)
- …

## Format

- File: `<folders.articles>/<Title>.md`. Copy the frontmatter shape of `<an existing article in the same series>` exactly (`type`, `series`, `series_no`, `seq`, `summary`, `sections`, `kinds`, `terms`, `sources`, `figures`, `equations`, `words`, `cssclasses`). End with the `> [!series]` navigation block (previous / next article, series map).
- Read first: `<existing neighbour articles>` and `<articles whose notation you must reuse>`. Use the same notation (time variables, sign and Fourier conventions, naming of signals) as those articles and the vault's notation note. Link to them instead of duplicating; your derivations must agree with their stated results, and any equation number you cite must match the current files.
- Depth: a good textbook chapter, about `<word range>` words of body. Every key result derived step by step in derivation cards; physical meaning before or after each formula; no jumps.
- Sources: cite only existing literature notes (`<CiteKey list>`; read the notes in `<folders.literature>` for keys). Do not invent citation keys. Verify claims against the sources; if unsure, say so in the report rather than guessing.
- Figures: `<n_min>`–`<n_max>` genuinely explanatory computed figures (principle schematics with simulated curves) from `<system>/figure-scripts/s<series>_<topic>.py`, stems `s<series>-<seq>-<slug>`, saved to `<folders.assets>/<subfolder>/`. View every PNG; add the README line.

## Term cards

- Create the new cards assigned to you, and only those: `<Term A>`, `<Term B>`, … in `<folders.terms>/`, with the exact shape of `<an existing term card>` (frontmatter `type`, `term`, `en`, `abbr`, `aliases`, `definition`, `series_no`, `defined_in: "[[<your article>]]"`; definition callout; "explained in" link to the defining heading; the dataview "appears in" block copied verbatim).
- In your `terms:` list, also link existing cards you use (`<existing term cards>`).

## Do not

Edit other articles, the series map, the home note, or run the outline-sync script — the coordinator does that.

## Final report

Outline (H2/H3), figures (stem → content), equation count, term cards created, any claim you were unsure about, and which existing notes would benefit from a link to yours (the coordinator adds them).
