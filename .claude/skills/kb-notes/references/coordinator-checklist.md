# Coordinator checklist (after a wave of per-note agents)

The coordinator is the only agent that edits more than one note. Work through this list after every wave; run scripts with `PYTHONIOENCODING=utf-8`.

## Before the wave

- [ ] Read `kb.config.json` and the vault's CONVENTIONS file; note labels, folders, types.
- [ ] Baseline: `xref.py --vault <VAULT>` and `linkcheck.py --vault <VAULT>` both report 0 (fix or record pre-existing problems first, so the wave's problems are distinguishable).
- [ ] Back up each target article to the scratchpad (not the vault).
- [ ] Write the brief(s) to the scratchpad; assign each agent exactly one note (plus its script and assets). Assign new term cards to exactly one agent each. Fix `seq` values for new articles in the brief.
- [ ] Spawn agents in parallel at medium effort; keep planning and review on a strong model at high effort.

## After the wave

1. [ ] **Collect reports.** For each agent: outline, new figures, inbound mapping (old number → new number, removed/renamed ids and headings), unverified points.
2. [ ] **Apply inbound fixes.** Run `xref.py --vault <VAULT>` (report), then `xref.py --vault <VAULT> --fix` for number mismatches. Fix `MISSING id` and `NO-NUMBER` lines by hand using the agents' mappings (point the link at the replacement id or heading).
3. [ ] **Headings.** For every renamed heading, update inbound `[[Note#Heading]]` links vault-wide; then `linkcheck.py --vault <VAULT>` must report `broken 0`.
4. [ ] **Per-note stats.** `note_stats.py --vault <VAULT> <each edited article>`: no DIFF and no CHECK lines (re-run with `--write` if counts drifted after your link fixes).
5. [ ] **Reading order.** If articles were added, removed or moved, renumber `seq` globally (series_no, then reading order) and update `series_no` / `series` where needed; check previous/next links in every affected `> [!series]` navigation block.
6. [ ] **Outline sync.** Run the vault's outline-sync script in check mode, then in write mode; it updates `sections`, series-map entries and counts. Update series-map intro paragraphs and the "about" note's series list by hand when scope changed.
7. [ ] **New term cards.** Shape matches an existing card; `defined_in` points to the defining article; the defining heading in the "explained in" link exists; articles that use the term list it in `terms:`.
8. [ ] **Links suggested by agents.** Add the cross-links agents proposed (one sentence + link at the point of use; do not re-teach).
9. [ ] **Figures.** Every embedded image exists (`linkcheck.py --strict`); each new script is in the figure-scripts README; no draft/backup PNGs left in assets.
10. [ ] **Hygiene.** No TAB characters; no LaTeX mangled into control characters (search edited files for `\x09`, `\x0c`, `\x08`, `\x0b`, `\x0d` not part of CRLF); no inline HTML for emphasis.
11. [ ] **Review.** For substantive rewrites, run an independent read-only review agent (strong model, high effort) on the changed articles: conventions, correctness of derivations against sources, concept order. Apply its fixes via medium/low-effort agents.
12. [ ] **Final checks.** `xref.py` → `problems 0`; `linkcheck.py` → `broken 0`; outline-sync check → no differences.
13. [ ] **Report to the user**: what changed per article, new figures/cards, fixes applied, anything unverified. Do not commit or push unless asked.
