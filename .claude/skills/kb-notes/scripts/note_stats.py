#!/usr/bin/env python3
"""Recompute an article's frontmatter statistics and run per-note sanity checks.

For each note it computes
    figures    number of figure callouts  (> [!figure] ...)
    equations  number of \\tag{n} in the body
    words      CJK characters + Latin words ([A-Za-z]+) in the body after the frontmatter
    sections   list of H2 headings (outside code fences)
    kinds      callout kinds used, in order of first appearance (the title word before
               the separator, e.g. "Definition" in "> [!definition] Definition — Title"
               or "定义" in "> [!definition] 定义　标题"; the callout type if no title word)
and compares them with the frontmatter. It also reports: equation tags not 1..N in order,
figure / table caption numbers not 1..N, TAB characters, unresolved in-note links
[[#Heading]] / [[#^id]], and embedded images missing from the vault.

Usage:
    python note_stats.py [--vault PATH] [--write] NOTE [NOTE ...]

    NOTE           a path to a .md file, or a note name (resolved inside the vault)
    --write        write figures / equations / words / sections / kinds into the frontmatter
                   (only keys that already exist are replaced; newline style is kept)

Exit code 1 when a frontmatter value differs (without --write) or a check fails.
Python 3 stdlib only; run with PYTHONIOENCODING=utf-8.
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


def load_config(vault_arg=None, start=None):
    """Return (vault_root, config_dict, config_path_or_None)."""
    if vault_arg:
        roots = [Path(vault_arg).resolve()]
    else:
        here = Path(start or Path.cwd()).resolve()
        roots = [here, *here.parents]
    for root in roots:
        hits = sorted(root.glob("*/kb.config.json"))
        if hits:
            with open(hits[0], encoding="utf-8-sig") as fh:
                return root, _merge(DEFAULT_CONFIG, json.load(fh)), hits[0]
    root = roots[0]
    print(f"warning: no */kb.config.json under {root}; using default config", file=sys.stderr)
    return root, DEFAULT_CONFIG, None


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for f in sorted(filenames):
            yield Path(dirpath) / f


def read_text(path):
    raw = Path(path).read_bytes().decode("utf-8-sig")
    nl = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), nl


# ---------------------------------------------------------------- stats
NON_CONTENT_CALLOUTS = {"figure", "series", "question", "reading", "quote", "cite"}
KIND_SEPARATORS = ("\u3000", " \u2014 ", " - ", ": ", "\uff1a", " \u00b7 ")


def split_frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return (m.group(1), text[m.end():]) if m else ("", text)


def kind_label(ctype, title):
    title = title.strip()
    for sep in KIND_SEPARATORS:
        if sep in title:
            return title.split(sep, 1)[0].strip()
    if title and " " not in title and len(title) <= 16:
        return title
    return ctype


def compute(body, labels):
    nocode = re.sub(r"```.*?```", "", body, flags=re.S)
    tags = [int(x) for x in re.findall(r"\\tag\{(\d+)\}", body)]
    fig_caps = [int(x) for x in re.findall(
        r"^> \[!figure\][^\n]*?\*\*" + re.escape(labels["figure"]) + r" ?(\d+)\*\*", body, re.M)]
    tab_caps = [int(x) for x in re.findall(
        r"^\*\*" + re.escape(labels["table"]) + r" ?(\d+)\*\*", body, re.M)]
    kinds = []
    for ctype, title in re.findall(r"^> \[!(\w+)\][+-]?[ \t]*(.*)$", nocode, re.M):
        if ctype.lower() in NON_CONTENT_CALLOUTS:
            continue
        k = kind_label(ctype, title)
        if k not in kinds:
            kinds.append(k)
    return {
        "figures": len(re.findall(r"^> \[!figure\]", body, re.M)),
        "equations": len(tags),
        "words": len(re.findall(r"[\u4e00-\u9fff]", body)) + len(re.findall(r"[A-Za-z]+", body)),
        "sections": [h.strip() for h in re.findall(r"^## (.+)$", nocode, re.M)],
        "kinds": kinds,
        "_tags": tags,
        "_figs": fig_caps,
        "_tabs": tab_caps,
    }


def fm_value(fm, key):
    m = re.search(rf"^{key}:[ \t]*(.*)$", fm, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    if key in ("figures", "equations", "words"):
        return int(v) if v.isdigit() else v
    if v.startswith("[") and v.endswith("]"):
        items = [x.strip() for x in re.findall(r'"[^"]*"|\'[^\']*\'|[^,]+', v[1:-1])]
        return [x[1:-1] if len(x) >= 2 and x[0] == x[-1] and x[0] in "'\"" else x for x in items if x]
    return v


def fm_format(key, value):
    if key == "sections":
        return "sections: [" + ", ".join('"' + h.replace('"', '\\"') + '"' for h in value) + "]"
    if key == "kinds":
        return "kinds: [" + ", ".join(value) + "]"
    return f"{key}: {value}"


def mask_code(text):
    """Blank out fenced code blocks and inline code spans (same length, newlines kept)."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"^[ ]*(```|~~~).*?^[ ]*\1[^\n]*$", blank, text, flags=re.S | re.M)
    return re.sub(r"`[^`\n]+`", blank, text)


def check_links(body, vault_files):
    issues = []
    body = mask_code(body)
    ids = set(re.findall(r"^\^([\w-]+)\s*$", body, re.M))
    heads = set(h.strip() for h in re.findall(r"^#{1,6}\s+(.+)$", body, re.M))
    for frag in re.findall(r"\[\[#([^\]|\\]+)", body):
        frag = frag.strip()
        if frag.startswith("^"):
            if frag[1:] not in ids:
                issues.append(f"in-note link to missing block id #{frag}")
        elif frag.split("#")[-1] not in heads:
            issues.append(f"in-note link to missing heading #{frag}")
    for img in re.findall(r"!\[\[([^\]|#\\]+)", body):
        base = img.strip().split("/")[-1]
        if os.path.splitext(base)[1].lower() in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp") \
                and base not in vault_files:
            issues.append(f"embedded image not found: {img}")
    return issues


def resolve_note(arg, root):
    p = Path(arg)
    if p.suffix != ".md":
        p = p.with_name(p.name + ".md")
    if p.exists():
        return p
    hits = [f for f in iter_files(root) if f.name == p.name]
    return hits[0] if hits else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("notes", nargs="+", help="note paths or names")
    ap.add_argument("--vault", help="vault root (default: discover from the first note / cwd)")
    ap.add_argument("--write", action="store_true", help="write the computed values to the frontmatter")
    args = ap.parse_args()

    first = Path(args.notes[0])
    root, cfg, _ = load_config(args.vault, first.parent if first.exists() else None)
    labels = cfg["labels"]
    vault_files = {f.name for f in iter_files(root)}
    status = 0

    for arg in args.notes:
        path = resolve_note(arg, root)
        if path is None:
            print(f"!! {arg}: not found")
            status = 1
            continue
        text, nl = read_text(path)
        fm, body = split_frontmatter(text)
        st = compute(body, labels)
        print(f"== {path.stem}")
        fm_new = fm
        for key in ("figures", "equations", "words", "sections", "kinds"):
            old = fm_value(fm, key)
            new = st[key]
            same = (set(old) == set(new)) if key == "kinds" and isinstance(old, list) else old == new
            mark = "ok  " if same else "DIFF"
            shown_old = "(missing)" if old is None else old
            print(f"  {mark} {key:9} frontmatter={shown_old}  computed={new}")
            if not same:
                if old is not None and args.write:
                    fm_new = re.sub(rf"^{key}:.*$", lambda _m, k=key, v=new: fm_format(k, v),
                                    fm_new, count=1, flags=re.M)
                elif not args.write:
                    status = 1
        problems = []
        if st["_tags"] != list(range(1, len(st["_tags"]) + 1)):
            problems.append(f"equation tags not 1..N in order: {st['_tags']}")
        if st["_figs"] != list(range(1, len(st["_figs"]) + 1)):
            problems.append(f"figure numbers not 1..N in order: {st['_figs']}")
        if st["_tabs"] != list(range(1, len(st["_tabs"]) + 1)):
            problems.append(f"table numbers not 1..N in order: {st['_tabs']}")
        if "\t" in text:
            problems.append(f"TAB characters: {text.count(chr(9))}")
        problems += check_links(body, vault_files)
        for p in problems:
            print("  CHECK", p)
        if problems:
            status = 1
        if args.write and fm_new != fm:
            new_text = text.replace(fm, fm_new, 1)
            path.write_bytes(new_text.replace("\n", nl).encode("utf-8"))
            print("  frontmatter written")
    sys.exit(status)


if __name__ == "__main__":
    main()
