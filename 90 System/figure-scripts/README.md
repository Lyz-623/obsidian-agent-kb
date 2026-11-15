# Figure scripts

Matplotlib sources of every figure embedded in the notes. Figures are computed, never drawn by hand, so they can be regenerated after any change of parameters or style.

```
python "90 System/figure-scripts/oscillator.py"
```

Requirements: Python 3 with numpy and matplotlib.

## Shared style: `figstyle.py`

Every script starts with `import figstyle; figstyle.use()` and saves with `figstyle.save(fig, "<subfolder>", "<stem>")`, which writes a 200-dpi PNG to `Assets/<subfolder>/<stem>.png` (the assets folder name comes from `kb.config.json`). The style gives closed frames with inward ticks, frameless legends, serif text with STIX maths and left-aligned panel labels "(a)", "(b)" via `figstyle.panel_label`. `figstyle.figure(rows, cols, width, height_mm)` creates a figure at the vault text width (140 mm), so fonts appear at their printed size.

Before writing, `save` prints two audits: `[legend-audit]` for data points under a legend and `[overlap-audit]` for text labels lying on a curve. Fix each warning (move the legend or label, widen an axis range) and re-run. Then look at the PNG itself: the audits catch the common problems, not all of them.

Embed a figure in a note with a figure callout:

```
> [!figure] **Fig. 1** Title clause. (a) …; (b) ….
> ![[damping-regimes.png|720]]

^fig-free-regimes
```

## Script → PNG (`Assets/…`)

- `oscillator.py` → oscillator/damping-regimes.png, oscillator/resonance.png, oscillator/transient.png
