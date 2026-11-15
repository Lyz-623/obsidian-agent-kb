"""Shared matplotlib style for knowledge-base figures.

Import and call `use()` before plotting, then save every figure with `save()`:

    import figstyle
    figstyle.use()
    fig, ax = plt.subplots(...)
    ...
    figstyle.save(fig, "oscillator", "damping-regimes")   # -> Assets/oscillator/damping-regimes.png

House style
- one serif text font for labels and STIX maths, 9-10 pt at the final printed width;
- closed frames (all four spines) with inward ticks on every quantitative panel;
- legends never carry a frame or fill (`save` turns them off whatever a script asks for);
- panel labels "(a)", "(b)" ... as left-aligned titles, placed with `panel_label`;
- PNG at 200 dpi on a white background, laid out at the vault text width (`TEXT_WIDTH_MM`).

Before writing, `save` runs two audits that print warnings for visual review:
- `[legend-audit]`: data points that lie under a (frameless) legend;
- `[overlap-audit]`: direct text labels that sit on top of a plotted curve.
Fix every warning (move the legend / label, widen the axis range) and re-run the script.

The assets folder comes from kb.config.json (`folders.assets`), so this file works unchanged in
any vault that follows the same layout.
"""
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent            # <system>/figure-scripts
SYSTEM = HERE.parent                              # <system>
VAULT = SYSTEM.parent                             # vault root
try:
    _CONFIG = json.loads((SYSTEM / "kb.config.json").read_text(encoding="utf-8"))
except (OSError, ValueError):
    _CONFIG = {}
ASSETS = VAULT / _CONFIG.get("folders", {}).get("assets", "Assets")
PNG_DPI = 200
TEXT_WIDTH_MM = 140                               # full text width; 140 mm at 200 dpi = 1102 px

PALETTE = {
    "blue": "#3a64a8", "orange": "#d0702a", "teal": "#1f7a6d", "violet": "#7a5aa6",
    "rose": "#a8506a", "amber": "#a06a1c", "green": "#3d7f4f", "grey": "#626e7c",
}
CYCLE = [PALETTE[k] for k in ("blue", "orange", "teal", "violet", "rose", "green", "grey")]


def use(**overrides):
    """Apply the house rcParams (call once, before creating figures)."""
    rc = {
        "font.family": "serif",
        "font.serif": ["Source Serif 4", "Source Serif Pro", "Charter", "Georgia", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 9.5,
        "axes.labelsize": 10,
        "axes.titlesize": 10,
        "axes.titlelocation": "left",
        "legend.fontsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "axes.linewidth": 0.6,
        "axes.prop_cycle": matplotlib.cycler(color=CYCLE),
        "lines.linewidth": 1.4,
        "legend.frameon": False,
        "legend.handlelength": 1.8,
        "axes.unicode_minus": True,
        "figure.dpi": 100,
        "savefig.dpi": PNG_DPI,
        "savefig.facecolor": "white",
    }
    rc.update(overrides)
    plt.rcParams.update(rc)


def figure(rows=1, cols=1, width=1.0, height_mm=None, **kwargs):
    """Create a figure at `width` x text width (mm-exact) with a constrained layout."""
    w_in = TEXT_WIDTH_MM * width / 25.4
    h_in = (height_mm / 25.4) if height_mm else w_in * (0.42 if rows == 1 else 0.36 * rows)
    return plt.subplots(rows, cols, figsize=(w_in, h_in), layout="constrained", **kwargs)


def panel_label(ax, label):
    """Panel label such as '(a)' as a left-aligned bold title."""
    ax.set_title(label, loc="left", fontweight="bold", pad=4)


def _frames(fig):
    """Closed frames with inward ticks on every axis that is switched on."""
    for ax in fig.axes:
        if not ax.axison:
            continue
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(0.6)
        ax.tick_params(direction="in", length=3, width=0.6, top=True, right=True)
        leg = ax.get_legend()
        if leg is not None:
            leg.set_frame_on(False)
    for leg in fig.legends:
        leg.set_frame_on(False)


def _points(art):
    import numpy as np
    from matplotlib.lines import Line2D
    from matplotlib.collections import PathCollection
    if isinstance(art, Line2D):
        xy = np.c_[art.get_xdata(), art.get_ydata()].astype(float)
        return art.get_transform().transform(xy)
    if isinstance(art, PathCollection):
        return art.get_offset_transform().transform(art.get_offsets())
    return np.empty((0, 2))


def _audit(fig, name):
    """Print legends with data underneath and text labels lying on curves."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    issues = 0
    for i, ax in enumerate(fig.axes):
        arts = [a for a in list(ax.lines) + list(ax.collections) if a.get_visible()]
        leg = ax.get_legend()
        if leg is not None:
            box = leg.get_window_extent(r).padded(-1)
            hits = sum(int(((xy[:, 0] > box.x0) & (xy[:, 0] < box.x1) & (xy[:, 1] > box.y0) & (xy[:, 1] < box.y1)).sum())
                       for xy in map(_points, arts) if len(xy))
            if hits:
                issues += 1
                print(f"[legend-audit] {name} panel {i}: {hits} data points under the legend")
        for text in ax.texts:
            if not text.get_visible() or not text.get_text().strip():
                continue
            box = text.get_window_extent(r).padded(1)
            for line in ax.lines:
                xy = _points(line)
                if len(xy) < 8:
                    continue
                if (((xy[:, 0] > box.x0) & (xy[:, 0] < box.x1) & (xy[:, 1] > box.y0) & (xy[:, 1] < box.y1))).any():
                    issues += 1
                    print(f"[overlap-audit] {name} panel {i}: label {text.get_text()!r} lies on curve {line.get_label()!r}")
                    break
    return issues


def save(fig, subfolder, stem):
    """Write `fig` as <assets>/<subfolder>/<stem>.png (200 dpi, white) after style fixes and audits."""
    _frames(fig)
    target = ASSETS / subfolder / f"{stem}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    _audit(fig, target.name)
    fig.savefig(target, dpi=PNG_DPI, facecolor="white", bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    try:
        shown = target.relative_to(VAULT).as_posix()
    except ValueError:
        shown = str(target)
    print(f"[figstyle] wrote {shown}")
    return target


if os.environ.get("FIGSTYLE_SELFTEST"):
    use()
    f, a = figure()
    a.plot([0, 1], [0, 1], label="line")
    a.legend()
    save(f, "_selftest", "selftest")
