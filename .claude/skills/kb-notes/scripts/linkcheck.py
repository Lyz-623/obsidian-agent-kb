#!/usr/bin/env python3
"""Link checker for a kb-notes Obsidian vault.

Verifies that every heading link [[Note#Heading]] and block link [[Note#^id]]
(including in-note [[#Heading]] / [[#^id]] and links with an escaped table pipe
[[Note#^id\\|text]]) resolves to an existing heading or ^block-id line in the
target note.

Usage:
    python linkcheck.py [--vault PATH] [--strict]

    --vault PATH   vault root (default: search upward from the cwd for */kb.config.json)
    --strict       also report links to notes that do not exist and embedded
                   files (![[x.png]]) missing from the vault

Exit code 1 when anything is broken. Python 3 stdlib only; run with PYTHONIOENCODING=utf-8.
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


def iter_files(root):
    """Yield every file below root, skipping hidden folders."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for f in sorted(filenames):
            yield Path(dirpath) / f


def read_text(path):
    raw = Path(path).read_bytes().decode("utf-8-sig")
    return raw.replace("\r\n", "\n")


def mask_code(text):
    """Blank out fenced code blocks and inline code spans (same length, newlines kept),
    so that link-like text inside code is ignored, as Obsidian does."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"^[ ]*(```|~~~).*?^[ ]*\1[^\n]*$", blank, text, flags=re.S | re.M)
    return re.sub(r"`[^`\n]+`", blank, text)


def has_file_ext(name):
    """True for attachment links like 'fig.png' or 'paper.pdf' (not '.md')."""
    ext = os.path.splitext(name)[1].lower()
    return bool(ext) and ext != ".md" and re.fullmatch(r"\.[a-z0-9]{1,5}", ext) is not None


# ---------------------------------------------------------------- main logic
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--vault", help="vault root (default: discover from cwd)")
    ap.add_argument("--strict", action="store_true",
                    help="also report missing target notes and missing embedded files")
    args = ap.parse_args()

    root, cfg, _ = load_config(args.vault)
    notes, files = {}, set()
    for p in iter_files(root):
        files.add(p.name)
        if p.suffix == ".md":
            notes.setdefault(p.stem, p)

    tpl_dir = (root / cfg["folders"]["templates"]).resolve()
    template_notes = {n for n, p in notes.items() if tpl_dir in p.resolve().parents}
    heads, ids, texts = {}, {}, {}
    for n, p in notes.items():
        s = read_text(p)
        texts[n] = s
        heads[n] = set(h.strip() for h in re.findall(r"^#{1,6}\s+(.+)$", s, re.M))
        ids[n] = set(re.findall(r"^\^([\w-]+)\s*$", s, re.M))

    bad = 0
    for n, s in texts.items():
        s = mask_code(s)
        for m in re.finditer(r"\[\[([^\]#|]*)#([^\]|\\]+)", s):
            tgt = (m.group(1).split("/")[-1]) or n
            frag = m.group(2).strip()
            if tgt not in notes:
                # file links such as ![[paper.pdf#page=3]] are handled by --strict below
                if args.strict and n not in template_notes and not has_file_ext(tgt):
                    bad += 1
                    print("NO-NOTE", n, "->", tgt)
                continue
            if frag.startswith("^"):
                ok = frag[1:] in ids[tgt]
            else:
                ok = frag.split("#")[-1] in heads[tgt]
            if not ok:
                bad += 1
                print("BROKEN", n, "->", tgt, "#", frag)
        if args.strict and n not in template_notes:
            # whole-note and file links: [[Note]], [[Note|text]], ![[file.png|720]], [[paper.pdf]]
            for m in re.finditer(r"\[\[([^\]#|\\]*)[^\]]*\]\]", s):
                tgt = m.group(1).strip()
                if not tgt:
                    continue
                base = tgt.split("/")[-1]
                if has_file_ext(base):
                    if base not in files:
                        bad += 1
                        print("NO-FILE", n, "->", tgt)
                elif base.removesuffix(".md") not in notes:
                    bad += 1
                    print("NO-NOTE", n, "->", tgt)
    print("broken", bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
