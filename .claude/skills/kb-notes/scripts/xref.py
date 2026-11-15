#!/usr/bin/env python3
"""Cross-note number checker / fixer for a kb-notes Obsidian vault.

Checks every block-id link whose display text shows a number, e.g.

    [[Some article#^eq-energy|"Some article" Eq. (3)]]
    [[Some article#^fig-setup\\|Fig. 2]]        (escaped pipe inside a table)

against the target block: the equation's \\tag{n}, the figure card's
**Fig. n** caption, or the table's **Table n** caption line. Labels come from
the vault config (labels.equation / labels.figure / labels.table).

Usage:
    python xref.py [--vault PATH] [--fix] [--local] [--skip NOTE ...]

    --vault PATH   vault root (default: search upward from the cwd for */kb.config.json)
    --fix          rewrite wrong displayed numbers when the target has exactly one number
    --local        also check in-note links [[#^id|Eq. (n)]]
    --skip NOTE    note name(s) to ignore as source and target (notes being edited by others)

Exit code 1 when problems remain. Python 3 stdlib only; run with PYTHONIOENCODING=utf-8.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- config
DEFAULT_CONFIG = {
    "title": "My Knowledge Base",
    "home": "Home.md",
    "folders": {"series": "10 Series", "articles": "20 Articles", "terms": "30 Terms",
                "literature": "40 Literature", "assets": "Assets", "system": "90 System",
                "templates": "Templates"},
    "types": {"article": "article", "series": "series-map", "term": "term",
              "literature": "literature", "home": "home", "front": "series-front"},
    "front_notes": ["About this collection", "Notation and conventions"],
    "labels": {"equation": "Eq.", "figure": "Fig.", "table": "Table"},
    "conventions": "90 System/CONVENTIONS.md",
}


def _merge(base, extra):
    out = dict(base)
    for k, v in extra.items():
        out[k] = _merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def load_config(vault_arg=None):
    """Return (vault_root, config_dict, config_path_or_None)."""
    if vault_arg:
        roots = [Path(vault_arg).resolve()]
    else:
        here = Path.cwd().resolve()
        roots = [here, *here.parents]
    for root in roots:
        hits = sorted(root.glob("*/kb.config.json"))
        if hits:
            with open(hits[0], encoding="utf-8-sig") as fh:
                return root, _merge(DEFAULT_CONFIG, json.load(fh)), hits[0]
    root = roots[0]
    print(f"warning: no */kb.config.json under {root}; using default config", file=sys.stderr)
    return root, DEFAULT_CONFIG, None


def iter_notes(root):
    """Map note name (basename without .md) -> path, skipping hidden folders."""
    notes = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for f in sorted(filenames):
            if f.endswith(".md"):
                name = f[:-3]
                if name in notes:
                    print(f"warning: duplicate note name {name!r}; using {notes[name]}", file=sys.stderr)
                    continue
                notes[name] = Path(dirpath) / f
    return notes


def read_text(path):
    """Read UTF-8 text with LF newlines; return (text, newline_used)."""
    raw = Path(path).read_bytes().decode("utf-8-sig")
    nl = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), nl


def write_text(path, text, nl):
    Path(path).write_bytes(text.replace("\n", nl).encode("utf-8"))


def mask_code(text):
    """Blank out fenced code blocks and inline code spans (same length, newlines kept),
    so that link-like text inside code is ignored, as Obsidian does."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"^[ ]*(```|~~~).*?^[ ]*\1[^\n]*$", blank, text, flags=re.S | re.M)
    return re.sub(r"`[^`\n]+`", blank, text)


def label_pattern(label):
    """Regex for a label; Latin labels must not be glued to a preceding letter."""
    pre = r"(?<![A-Za-z])" if label[:1].isascii() and label[:1].isalpha() else ""
    return pre + re.escape(label)


# ---------------------------------------------------------------- main logic
def build_patterns(labels):
    eq, fig, tab = labels["equation"], labels["figure"], labels["table"]
    return {
        # displayed references inside link text
        "ref": {
            "equation": re.compile(label_pattern(eq) + r" ?\((\d+)\)"),
            "figure": re.compile(label_pattern(fig) + r" ?(\d+)"),
            "table": re.compile(label_pattern(tab) + r" ?(\d+)"),
        },
        # numbers carried by the target block
        "tag": re.compile(r"\\tag\{(\d+)\}"),
        "fig_cap": re.compile(r"\*\*" + re.escape(fig) + r" ?(\d+)\*\*"),
        "tab_cap": re.compile(r"\*\*" + re.escape(tab) + r" ?(\d+)\*\*"),
        "tab_block": re.compile(r"\*\*" + re.escape(tab) + r" ?(\d+)\*\*[^\n]*\n\n(\|[^\n]*\n)+\n\^([\w-]+)"),
    }


def block_numbers(text, P):
    """Map block id -> {'equation': [...], 'figure': [...], 'table': [...]}."""
    out = {}
    prev = ""
    for b in re.split(r"\n\s*\n", text):
        m = re.fullmatch(r"\s*\^([\w-]+)\s*", b)
        if m:
            fig = P["fig_cap"].search(prev)
            tab = P["tab_cap"].search(prev)
            out[m.group(1)] = {
                "equation": P["tag"].findall(prev),
                "figure": [fig.group(1)] if fig else [],
                "table": [tab.group(1)] if tab else [],
            }
        else:
            prev = b
    # tables: caption line, blank line, table rows, blank line, ^id
    for m in P["tab_block"].finditer(text):
        out.setdefault(m.group(3), {"equation": [], "figure": [], "table": []})["table"] = [m.group(1)]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--vault", help="vault root (default: discover from cwd)")
    ap.add_argument("--fix", action="store_true", help="rewrite wrong displayed numbers")
    ap.add_argument("--local", action="store_true", help="also check in-note [[#^id|...]] links")
    ap.add_argument("--skip", nargs="*", default=[], help="note names to ignore")
    args = ap.parse_args()

    root, cfg, _ = load_config(args.vault)
    P = build_patterns(cfg["labels"])
    notes = iter_notes(root)
    skip = set(args.skip)
    link_re = re.compile(r"\[\[([^\]#|]*)#\^([\w-]+)(\\?)\|([^\]]*)\]\]")
    cache = {}
    problems = 0
    unfixed = 0

    for name, path in notes.items():
        if name in skip:
            continue
        text, nl = read_text(path)

        def repl(m):
            nonlocal problems, unfixed
            tgt_raw, bid, esc, disp = m.groups()
            if not tgt_raw and not args.local:
                return m.group(0)
            tgt = tgt_raw.split("/")[-1] if tgt_raw else name
            if tgt not in notes or tgt in skip:
                return m.group(0)
            if tgt not in cache:
                cache[tgt] = block_numbers(read_text(notes[tgt])[0], P)
            info = cache[tgt].get(bid)
            if info is None:
                print(f"MISSING id  {name}: {tgt}#^{bid}")
                problems += 1
                unfixed += 1
                return m.group(0)
            for kind, pat in P["ref"].items():
                shown = pat.findall(disp)
                if not shown:
                    continue
                actual = info[kind]
                if len(shown) == 1 and actual and shown[0] not in actual:
                    print(f"MISMATCH   {name}: {tgt}#^{bid} shows {kind} {shown[0]} actual {actual}")
                    problems += 1
                    if len(actual) == 1:
                        disp = pat.sub(lambda mm: mm.group(0)[: mm.start(1) - mm.start(0)] + actual[0]
                                       + mm.group(0)[mm.end(1) - mm.start(0):], disp)
                    else:
                        unfixed += 1
                elif not actual:
                    print(f"NO-NUMBER  {name}: {tgt}#^{bid} shows {kind} {shown} but target has none")
                    problems += 1
                    unfixed += 1
            return f"[[{tgt_raw}#^{bid}{esc}|{disp}]]"

        # find links on the code-masked text (same offsets), rewrite them in the original
        pieces, last = [], 0
        for mm in link_re.finditer(mask_code(text)):
            orig = link_re.fullmatch(text, mm.start(), mm.end())
            pieces.append(text[last:mm.start()])
            pieces.append(repl(orig) if orig else text[mm.start():mm.end()])
            last = mm.end()
        new = "".join(pieces) + text[last:]
        if new != text and args.fix:
            write_text(path, new, nl)
            print("fixed", name)
    remaining = unfixed if args.fix else problems
    print("problems", problems)
    if args.fix:
        print("unfixed", remaining)
    sys.exit(1 if remaining else 0)


if __name__ == "__main__":
    main()
