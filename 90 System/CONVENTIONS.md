# Vault conventions

This vault's copy of the `kb-notes` conventions template (`.claude/skills/kb-notes/references/conventions-template.md`), localised for this English vault: labels `Eq.`, `Fig.`, `Table` (as in `90 System/kb.config.json`), straight or curly double quotes around article names in cross-references, folder names `10 Series`, `20 Articles`, `30 Terms`, `40 Literature`, `Assets`, `90 System`. Agents read this file, not the template. Edit it to change the house rules of this vault; `<Article>` is a note title and `<prefix>` the note's block-id prefix.

## 1. What the knowledge base is

- **Articles** (`types.article`, folder `folders.articles`): long-form explainers. One article answers one question; it explains *how and why* something works, at textbook depth (every key result derived, no knowledge jumps), not as a paper summary and not as a one-concept card.
- **Series maps** (`types.series`, folder `folders.series`): one per series; a guiding question, an intro paragraph, then auto-generated article entries. Never edit the generated entries by hand; run the vault's outline-sync script.
- **Term cards** (`types.term`, folder `folders.terms`): one atomic concept each, pointing to the article that defines it.
- **Literature notes** (`types.literature`, folder `folders.literature`): one per cited work; the citekey is the note name.
- **Front notes** (`front_notes`, type `types.front`): "about this collection" and "notation and conventions". The notation note is the single source of truth for symbols, sign conventions and units.
- **Home** (`home`): a dashboard generated from frontmatter. Scope: graph, articles, term cards, literature. No progress checklists, mastery levels, study schedules or export/import features.

Reading order is global: `series_no` then `seq`. A concept may be used only after the article that introduces it (lower `seq`); later articles link back instead of re-deriving, earlier articles never pre-teach later material. Each concept has one owner article.

## 2. Article structure

- Frontmatter keys: `type`, `series` (`"[[<Series map>]]"`), `series_no`, `seq`, `summary` (one sentence, no final full stop needed), `sections` (list of H2 titles, in order), `kinds` (callout kind words used), `terms` (`"[[Term]]"` list), `sources` (`"[[CiteKey]]"` list), `figures` (count of figure callouts), `equations` (count of `\tag`), `words` (CJK characters + Latin words in the body), `cssclasses`. Recompute the counts with `note_stats.py --write` after every edit.
- Opening: 2–4 sentences that pose the article's question and why it matters, then the first H2. No scope / notation / "this article will…" / reading-guide paragraph.
- **Every H2 is split into H3 subsections. Nothing sits directly under an H2.** No subsection holds just one card or one paragraph — merge thin subsections. Titles are short and precise.
- No meta transition paragraphs ("the previous section…, this section…"). Instead, connect cards with **question-driven bridges** of 1–2 sentences: say what problem the next card answers, give the intuition before a formula card. A section reads as question → card → next question, never as stacked boxes. Do not refer to "cards" or "boxes" in the text.
- No end-of-article summary / key-points card. A closing conclusion card inside the last subsection is fine; titled key-point blocks inside the text are content and stay.
- The article ends with a series navigation callout (`> [!series]`) linking the previous article, the next article and the series map.
- No worked numeric drills or unit-conversion examples; fold any important conclusion into the text or a card.
- Prefer figures and formulas over long prose. A long text-only passage or a text-only callout with several long bullets must become a formula plus a principle schematic.

## 3. Callout cards

Each card is a callout whose title starts with its kind word, a separator, then the card title:

```
> [!definition] Definition — Relative and common phase
> Body text …
>
> $$
> E = \dots \tag{1}
> $$

^def-<prefix>-relative-phase
```

| Callout type | Kind word | Use for |
|---|---|---|
| `definition` | Definition | every key concept |
| `proposition` | Proposition | every result: statement first, key formula, one bold takeaway sentence |
| `derivation` | Derivation | step-by-step proof of a result; bold step labels ("**Step 1: …**") with displayed equations |
| `explain` | Explanation | physical meaning, why a formula exists, how to read it |
| `warning` | Caution | conditions of validity, common mistakes (keep short; use a figure if it needs more than a few lines) |
| `conclusion` | Conclusion | what a subsection established |
| `intuition` | Concept | qualitative picture before the formalism |
| `keypoints` | Key points | titled in-text summary block (optional) |
| `figure` | — | figure card (section 5) |
| `series` | — | series navigation at the end |

- Conclusion before derivation: a proposition card states the result, the derivation card follows.
- Important formulas keep compact step-by-step derivations. "Conclusion only" is not acceptable for a key result; only genuinely peripheral derivations may be cut.
- Explain physical meaning before or right after each key formula; label formula parts with `\underbrace{…}_{\text{…}}` where it helps.
- Delete cards that only restate or add trivia.

## 4. Block ids

- A block-id line `^id` follows every card, figure, displayed key equation and table, separated by one blank line.
- Ids are short kebab-case with the note's prefix: `def-`, `eq-`, `der-`, `fig-`, `tab-` + `<prefix>-` + slug.
- **Keep existing ids** when the content survives (other notes link to them). When an id must go, report it so inbound links can be fixed.

## 5. Figures

```
> [!figure] **Fig. 3** Title clause. (a) what is plotted vs what, conditions, what colours/lines mean; (b) …
> ![[<stem>.png|720]]

^fig-<prefix>-<slug>
```

- Caption in **one line, paper style**: a title clause, then one clause per panel, plus the model / parameters used. No interpretation in the caption, no "generated by script X" text, no licence lines. Figures reproduced from literature end the caption with `(from [[CiteKey|Author Year]])` (localised).
- After the figure, **at most 1–2 sentences that interpret it** (what to notice, why, link to the equation, panel comparison). Never restate axes, legend or parameters. No "Reading Figure N:" bullet lists.
- Figures are numbered 1..N per article in order of appearance.
- Figures are computed: a matplotlib script in `<system>/figure-scripts/` named after the series and topic, writing `<stem>.png` into the article's assets subfolder via the shared style helper. Numbers must be physically correct for the vault's standard example. Look at every PNG produced and fix overlaps. A flawed figure is redrawn from its script, never pixel-patched or explained away in the caption. Keep no backup or draft copies. Add each script → outputs line to the figure-scripts README.
- Prefer genuinely explanatory schematics (principle diagrams, annotated mechanisms with simulated curves) over decorative plots.

## 6. Equations

- Displayed: `$$ … \tag{n} $$`, its own lines (inside a callout every line starts with `> `). Formulas are never mixed into prose when they are results.
- **Number only key results**, 1..N in order of appearance per article. Intermediate steps inside derivations stay unnumbered.
- In-note reference: `Eq. (n)` or `[[#^eq-id|Eq. (n)]]`.
- After renumbering, update every in-note reference and report inbound references from other notes.

## 7. Tables

```
**Table 2**  Caption sentence.

| … | … |
|---|---|

^tab-<prefix>-<slug>
```

Numbered 1..N per article. Inside a table, a wiki link's pipe is escaped: `[[Note#^id\|text]]`.

## 8. Links and citations

- Citations: bare `[[CiteKey|Author Year]]`. No page, figure, equation or section locators in the citation (verify claims against the exact place in the source, but keep the locator out of the text).
- Cross-note references show the article name and the target's number in the target's numbering:
  - block: `[[<Article>#^id|"<Article>" Eq. (n)]]`, `… Fig. n`, `… Table n`
  - heading: `[[<Article>#Heading|"<Article> · Heading"]]`
  Use the vault's quotation marks (e.g. corner brackets in a CJK vault).
- Key terms link their term card on first use in a section: `**[[Term]]**`.
- When a heading is renamed, update every inbound `[[Note#Heading]]` link vault-wide.

## 9. Emphasis and punctuation

- Native Markdown only: `**term**` (key concept), `==result==` (key conclusion), `***condition***` (critical assumption or distinction). No inline HTML (`<u>`, `<span>`): it breaks Live Preview.
- Delimiters must satisfy CommonMark flanking rules: sentence punctuation goes outside the closing delimiter; where a delimiter must touch a bracket or a `$…$` formula, insert a hair space (U+200A).
- No TAB characters anywhere.

## 10. Term cards

Frontmatter: `type` (`types.term`), `term`, `en`, `abbr`, `aliases`, `definition` (one or two sentences, may contain inline math), `series_no`, `defined_in: "[[<Article>]]"`, `cssclasses`. Body: a definition callout repeating the definition, one line `Explained in [[<Article>#Heading|<Article> · Heading]].`, and an "Appears in" heading with a dataview block listing articles that link to the card (copy it verbatim from an existing card).

## 11. Literature notes

Frontmatter: `type` (`types.literature`), `citekey`, `title`, `authors`, `year`, `venue` or `journal`, `doi`, `pdf`. Body: an info callout, a reading-notes section, a dataview list of citing articles, and optionally the embedded PDF.

## 12. Series maps and outline sync

A series map's article entries are `## [[<Article>]]`, blank line, the article's `summary` + full stop + its H2 titles joined by ` · `, sorted by `seq`. After any article edit, run the vault's outline-sync script (check mode first). It does not rewrite intro paragraphs or the series list in the "about" note: update those by hand when an article's scope changes or an article/series is added, removed or renamed.
