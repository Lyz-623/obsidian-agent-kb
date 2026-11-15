"""Draw the link graph of the vault's content notes with matplotlib -> docs/images/graph.png.

    python docs/preview/graph.py

Nodes are the notes in the series, articles, terms and literature folders (from kb.config.json),
coloured by folder with the colours of the vault's graph-view groups (.obsidian/graph.json); edges are
the wiki links between them (frontmatter and body, undirected). This is a static drawing of the same
link data, not a screenshot of Obsidian's graph view. The layout is networkx's spring layout when
networkx is installed, otherwise a small Fruchterman-Reingold implementation below.
"""
import json
import math
import random
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_data as bd  # noqa: E402

VAULT = bd.VAULT
OUT = VAULT / "docs" / "images" / "graph.png"


def load():
    cfg = json.loads(bd.find_config().read_text(encoding="utf-8"))
    F = cfg["folders"]
    groups = [("articles", "Articles"), ("terms", "Term cards"), ("literature", "Literature"), ("series", "Series map / front notes")]
    colours = {"articles": "#3a64a8", "terms": "#1f7a6d", "literature": "#a0691c", "series": "#7a5aa6"}
    try:   # use the graph-view colour groups when they are plain path queries
        g = json.loads((VAULT / ".obsidian" / "graph.json").read_text(encoding="utf-8"))
        for cg in g.get("colorGroups", []):
            for key, _ in groups:
                if cg["query"] == f'path:"{F[key]}"':
                    colours[key] = "#%06x" % cg["color"]["rgb"]
    except (OSError, ValueError, KeyError):
        pass
    notes = {}
    for key, _ in groups:
        for p in sorted((VAULT / F[key]).glob("*.md")):
            notes[p.stem] = key
    edges = set()
    for name, key in notes.items():
        text = (VAULT / F[key] / f"{name}.md").read_text(encoding="utf-8")
        for m in bd.LINK_RE.finditer(text):
            t = bd.link_target(m.group(1))
            if t in notes and t != name:
                edges.add(tuple(sorted((name, t))))
    return notes, sorted(edges), groups, colours


def fr_layout(nodes, edges, iters=600, seed=7):
    """Fruchterman-Reingold force layout in the unit square (fallback when networkx is missing)."""
    rnd = random.Random(seed)
    pos = {n: [rnd.random(), rnd.random()] for n in nodes}
    k = 0.9 / math.sqrt(len(nodes))
    t = 0.1
    for _ in range(iters):
        disp = {n: [0.0, 0.0] for n in nodes}
        for i, a in enumerate(nodes):
            for b in nodes[i + 1:]:
                dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
                d = max(math.hypot(dx, dy), 1e-4)
                f = k * k / d
                disp[a][0] += dx / d * f; disp[a][1] += dy / d * f
                disp[b][0] -= dx / d * f; disp[b][1] -= dy / d * f
        for a, b in edges:
            dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
            d = max(math.hypot(dx, dy), 1e-4)
            f = d * d / k
            disp[a][0] -= dx / d * f; disp[a][1] -= dy / d * f
            disp[b][0] += dx / d * f; disp[b][1] += dy / d * f
        for n in nodes:   # weak pull to the centre keeps isolated notes in view
            disp[n][0] += (0.5 - pos[n][0]) * 0.05
            disp[n][1] += (0.5 - pos[n][1]) * 0.05
            d = max(math.hypot(*disp[n]), 1e-9)
            pos[n][0] += disp[n][0] / d * min(d, t)
            pos[n][1] += disp[n][1] / d * min(d, t)
        t *= 0.992
    return {n: tuple(v) for n, v in pos.items()}


def layout(nodes, edges, seed):
    try:
        import networkx as nx
    except ImportError:
        return fr_layout(nodes, edges, seed=seed)
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return nx.spring_layout(G, seed=seed, k=2.4 / math.sqrt(len(nodes)), iterations=800)


def draw(notes, edges, groups, colours, pos):
    """Draw one layout; return the figure and a clutter score (overlap of labels with labels/nodes/legend)."""
    nodes = list(notes)
    deg = {n: 0 for n in nodes}
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1
    fig, ax = plt.subplots(figsize=(12, 7.4), dpi=120)
    for a, b in edges:
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], color="#b9bec7", lw=0.9, zorder=1)
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    span = max(max(xs) - min(xs), max(ys) - min(ys))
    labels, dots = [], []
    for n in nodes:
        x, y = pos[n]
        s = 60 + 38 * deg[n]
        ax.scatter([x], [y], s=s, color=colours[notes[n]], edgecolor="white", linewidth=1.4, zorder=3)
        dots.append((x, y, math.sqrt(s) / 2 + 2))
        r = math.sqrt(s) / 2 + 3
        labels.append(ax.annotate(n, (x, y), xytext=(0, -r - 2), textcoords="offset points", ha="center", va="top",
                                  fontsize=9.5 if notes[n] != "articles" else 10.5,
                                  fontweight="bold" if notes[n] == "articles" else "normal", color="#333a44", zorder=4,
                                  path_effects=[pe.withStroke(linewidth=3.5, foreground="white")]))
    ax.set_xlim(min(xs) - 0.10 * span, max(xs) + 0.10 * span)
    ax.set_ylim(min(ys) - 0.10 * span, max(ys) + 0.06 * span)
    ax.set_axis_off()
    handles = [Line2D([], [], marker="o", ls="", markersize=9, markerfacecolor=colours[k], markeredgecolor="white", label=lbl)
               for k, lbl in groups]
    leg = ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=10)
    ax.set_title(f"Link graph of the sample vault: {len(nodes)} notes, {len(edges)} links (node size = number of links)",
                 loc="left", fontsize=11, color="#555c66")
    fig.tight_layout()
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    boxes = [t.get_window_extent(r).padded(3) for t in labels]
    from matplotlib.transforms import Bbox
    others = [leg.get_window_extent(r).padded(4)]
    for x, y, rad in dots:   # node discs in display pixels
        cx, cy = ax.transData.transform((x, y))
        rp = rad * fig.dpi / 72
        others.append(Bbox([[cx - rp, cy - rp], [cx + rp, cy + rp]]))

    def inter(a, b):
        w = min(a.x1, b.x1) - max(a.x0, b.x0)
        h = min(a.y1, b.y1) - max(a.y0, b.y0)
        return w * h if w > 0 and h > 0 else 0.0

    score = sum(inter(a, b) for i, a in enumerate(boxes) for b in boxes[i + 1:])
    score += sum(inter(a, b) for a in boxes for b in others)
    fw, fh = fig.canvas.get_width_height()
    score += sum(1e4 for a in boxes if a.x0 < 0 or a.x1 > fw or a.y0 < 0)
    return fig, score


def main():
    notes, edges, groups, colours = load()
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "Helvetica", "Arial", "DejaVu Sans"]})
    best = None
    for seed in range(1, 41):   # pick the least cluttered of a few deterministic layouts
        fig, score = draw(notes, edges, groups, colours, layout(list(notes), edges, seed))
        if best is None or score < best[1]:
            if best:
                plt.close(best[0])
            best = (fig, score, seed)
        else:
            plt.close(fig)
        if score == 0:
            break
    fig, score, seed = best
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor="white")
    print(f"graph.png: {len(notes)} nodes, {len(edges)} edges, layout seed {seed}, clutter {score:.0f} -> {OUT.relative_to(VAULT).as_posix()}")


if __name__ == "__main__":
    main()
