# Brief: optimise one article (per-note execution agent)

Fill the `<…>` slots and save the brief to the session scratchpad; give each agent the brief path plus its one article. Run execution agents at medium effort.

---

You are optimising ONE article in an Obsidian knowledge-base vault.

- Vault root: `<VAULT>`. Config: `<VAULT>/<system>/kb.config.json` (folders, labels, types). Conventions: `<VAULT>/<conventions path>` — read it fully first; it is binding.
- Your article: `<folders.articles>/<Article>.md`. Figures: `<folders.assets>/<subfolder>/`. Figure scripts: `<system>/figure-scripts/` (read its README; use the shared style helper).
- Skill scripts: `<SKILL>/scripts/` (`note_stats.py`, `linkcheck.py`, `xref.py`). Run Python with `PYTHONIOENCODING=utf-8`.
- Reference example (already done; read it first and mirror its style): `<Reference article>`.
- Reading order: `<series list with seq ranges>`. Concepts from lower-`seq` articles may be used with a link; concepts from later articles must not be used.

## What the user asked

<Paste the user's request verbatim, plus any earlier feedback that still applies.>

Default goals when the request is "optimise / rewrite this note":

1. **Structure.** Re-plan H2 → H3. Merge thin subsections (one card or one paragraph); every H2 has H3s; nothing directly under an H2; concise, accurate titles.
2. **Cut redundancy.** Remove repeated explanations, cards that only restate, trivia, numeric drills, meta/scope paragraphs, an end-of-article summary.
3. **Figures and formulas instead of text walls.** Any long text-only passage or text-only callout (several long bullets, no figure) becomes a formula plus a principle schematic. Add genuinely explanatory, computed figures.
4. **Keep the derivations.** Important formulas keep compact step-by-step derivation cards with displayed equations; explain physical meaning and why each formula exists. Only truly peripheral derivations may be cut. No knowledge jumps.
5. **Renumber.** Number only key results, `\tag{1}`..`\tag{N}` in order; figures 1..N; tables 1..N. Update every in-note reference.
6. **Bridges.** Question-driven 1–2 sentence bridges between cards; no stacked boxes.
7. **Figure paragraphs.** Paper-style one-line captions (title clause + per-panel clauses); after each figure at most 1–2 interpretive sentences.

## Figures

- Extend the article's existing script if it has one; otherwise create `<system>/figure-scripts/s<series>_<topic>.py`, stems `s<series>-<seq>-<slug>`, saved to the assets subfolder the article already uses.
- Use the style helper; labels in the vault language; panel titles "(a) …" left-aligned; ticks inward. Numbers must be physically correct for the vault's standard example (`<standard example parameters>`).
- Look at every PNG you produce (Read tool) and fix overlaps or clipped labels by changing the script. Add the script → outputs line to the README.

## Hard rules

- **Never write text containing backslashes through shell heredocs or language string literals** (LaTeX `\tau`, `\left`, `\nu` get mangled into control characters). Write new content with the Write/Edit tools — e.g. write chunks to the scratchpad with Write, then splice them with a short script that only reads and moves text.
- No TAB characters in the final file.
- Keep existing block ids where the content survives; new ids use the note's prefix in kebab-case.
- Edit ONLY your article, your figure script(s), your new PNGs and your README line. Do not edit other articles, term cards or series maps, and do not run the outline-sync script — other agents are editing other notes concurrently; the coordinator integrates.
- Find inbound links to your article: `grep -rn "<Article>#" --include=*.md "<VAULT>"`. Every block id, heading or number they display that you change must appear in your report.

## Before finishing

1. `python <SKILL>/scripts/note_stats.py --vault "<VAULT>" --write "<path to article>"` — then re-run without `--write`; it must report no CHECK lines (tags 1..N, figure/table numbers 1..N, no TABs, in-note links resolve, images exist).
2. Confirm `sections` / `kinds` / counts in the frontmatter are updated (the script does this).

## Final report (your last message, concise)

1. New H2/H3 outline; what was merged or cut and why (brief).
2. New figures: stem → what it shows.
3. **Mapping for inbound fixes**: every inbound link target with its old displayed number → new number (e.g. `^eq-<prefix>-time-shift: {equation} (18) → {equation} (12)`, `^fig-…: {figure} 5 → {figure} 7`), and every removed or renamed heading or block id with its replacement. Write "none" if none.
4. Final counts (figures, equations, words) and anything unverified.
