#!/usr/bin/env python3
"""Figure-explanation audit for a kb-notes Obsidian vault.

Rules checked (see conventions, section "Figures"):

1. Every panel named in a figure caption, e.g. "(a) ... ; (b) ...", is discussed
   individually in the body text with its full label: "Fig. 3(a)", "图 3(b)",
   or a link "[[#^fig-id|Fig. 3]](b)". A range "Fig. 3(a)-(c)" counts only its
   endpoints, so the middle panel is still reported as missing.
2. No bare panel reference such as "(a)" or "in (b)" anywhere in the body:
   a panel letter must always be preceded by the figure label and number,
   otherwise the reader cannot tell which figure it belongs to.
3. Every figure is mentioned by number at least once in the body.

Captions themselves, math, code and links to other notes are ignored.

Usage:
    python figure_audit.py [--vault PATH] [NOTE ...]

Without NOTE arguments all articles are audited. Exit code 1 when problems remain.
Python 3 stdlib only; run with PYTHONIOENCODING=utf-8.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xref import load_config, iter_notes, read_text, mask_code, label_pattern  # noqa: E402

PANEL = r"[(（]([a-l])[)）]"
JOIN = r"[\s–—~\-、,，和与及&]*"


def blank(m):
    return re.sub(r"[^\n]", " ", m.group(0))


def strip_frontmatter(text):
    m = re.match(r"---\n.*?\n---\n", text, re.S)
    return (re.sub(r"[^\n]", " ", m.group(0)), text[m.end():]) if m else ("", text)


def mask_math(text):
    text = re.sub(r"\$\$.*?\$\$", blank, text, flags=re.S)
    return re.sub(r"(?<!\\)\$[^$\n]+?(?<!\\)\$", blank, text)


def normalise_links(text, note_name):
    """Replace wiki links by their display text; links to other notes become a
    neutral placeholder so that their figure numbers are not counted here."""
    def repl(m):
        target, disp = m.group(1), m.group(2)
        own = target.startswith("#") or target.split("#")[0] == note_name
        if not own:
            return "XREF"
        return disp if disp is not None else target
    return re.sub(r"\[\[([^\]|]*?)(?:\\?\|([^\]]*))?\]\]", repl, text)


def audit(path, name, labels):
    raw, _ = read_text(path)
    fm, body = strip_frontmatter(raw)
    lines_offset = fm.count("\n")
    body = mask_code(body)
    fig = labels["figure"]
    figlab = label_pattern(fig)
    if fig.rstrip(".").lower() == "fig":      # English prose also writes "Figure 3(b)"
        figlab = r"(?:" + figlab + r"|(?<![A-Za-z])Figure)"
    cap_re = re.compile(r"^>\s*\[!figure\][^\n]*?\*\*" + re.escape(fig) + r" ?(\d+)\*\*([^\n]*)$", re.M)

    figures = {}
    for m in cap_re.finditer(body):
        letters = list(dict.fromkeys(re.findall(PANEL, m.group(2))))
        figures[m.group(1)] = letters
    text = cap_re.sub(blank, body)          # captions are not body text
    text = mask_math(text)
    text = normalise_links(text, name)

    mentioned = {n: set() for n in figures}
    cited = set()
    ref_re = re.compile(figlab + r" ?(\d+)(?!\d)((?:" + JOIN + PANEL + r")*)")
    for m in ref_re.finditer(text):
        pre = text[max(0, m.start() - 4):m.start()]
        if pre.endswith("XREF"):
            continue
        n = m.group(1)
        cited.add(n)
        if n in mentioned:
            mentioned[n].update(re.findall(PANEL, m.group(2)))

    problems = []
    for n, letters in figures.items():
        if n not in cited:
            problems.append(f"  {fig} {n}: never mentioned in the text")
        miss = [x for x in letters if x not in mentioned[n]]
        if len(letters) > 1 and miss:
            problems.append(f"  {fig} {n}: panels not discussed individually: " + " ".join(f"({x})" for x in miss))

    chain = re.compile(figlab + r" ?\d+(?:" + JOIN + PANEL + r")*" + JOIN + r"$")
    for m in re.finditer(PANEL, text):
        pre = text[max(0, m.start() - 60):m.start()]
        if chain.search(pre):
            continue
        line_no = lines_offset + text.count("\n", 0, m.start()) + 1
        src_line = raw.split("\n")[line_no - 1].strip()
        snippet = src_line[:90] + ("…" if len(src_line) > 90 else "")
        problems.append(f"  bare panel ref {m.group(0)} at line {line_no}: {snippet}")
    return figures, problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--vault")
    ap.add_argument("notes", nargs="*")
    a = ap.parse_args()
    root, cfg, _ = load_config(a.vault)
    labels, folder, atype = cfg["labels"], cfg["folders"]["articles"], cfg["types"]["article"]
    notes = iter_notes(root)
    if a.notes:
        targets = []
        for n in a.notes:
            p = Path(n)
            name = p.stem if p.suffix == ".md" else n
            if name not in notes:
                print(f"no such note: {n}", file=sys.stderr)
                continue
            targets.append(name)
    else:
        targets = [n for n, p in notes.items()
                   if p.relative_to(root).parts[0] == folder
                   and re.search(r"^type:\s*['\"]?" + re.escape(atype) + r"['\"]?\s*$",
                                 read_text(p)[0][:2000], re.M)]
    total, nfig = 0, 0
    for name in sorted(targets):
        figures, problems = audit(notes[name], name, labels)
        nfig += len(figures)
        if problems:
            total += len(problems)
            print(f"== {name}  ({len(figures)} figures, {len(problems)} problems)")
            print("\n".join(problems))
    print(f"articles {len(targets)}  figures {nfig}  problems {total}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
