"""Build docs/preview/data.js: the vault's notes in the shape the home dashboard reads from Dataview.

    python docs/preview/build_data.py

The preview harness (home.html, note.html) cannot run Obsidian or Dataview, so this script indexes
the vault the way Dataview would for the fields that 90 System/home/view.js actually uses:

- one page per Markdown note: frontmatter fields, plus `file` = {name, path, folder, mtime, size,
  outlinks, inlinks}; frontmatter strings that are a single wiki link ("[[Note]]") become link
  objects {path}, as Dataview turns them into Link values;
- the raw text of every content note (so note.html can render it without file:// fetches);
- kb.config.json, the vault's top-level folders and every file path (for image embeds).

Standard library only. data.js is a generated file (git-ignored); shoot.ps1 rebuilds it.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAULT = HERE.parent.parent
SKIP_DIRS = {".git", ".obsidian", ".claude", ".trash", "node_modules", "__pycache__"}

FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.S)
LINK_RE = re.compile(r"!?\[\[([^\]\n]+?)\]\]")
ITEM_RE = re.compile(r"""\s*('(?:[^']|'')*'|"(?:[^"\\]|\\.)*"|[^,\]]*)\s*(?:,|$)""")


def find_config():
    for d in sorted(p for p in VAULT.iterdir() if p.is_dir()):
        c = d / "kb.config.json"
        if c.is_file():
            return c
    sys.exit("kb.config.json not found one level below the vault root")


def scalar(v):
    """One YAML scalar of the subset used in the vault's frontmatter."""
    v = v.strip()
    if not v:
        return None
    if v[0] == "'" and v[-1] == "'" and len(v) >= 2:
        return v[1:-1].replace("''", "'")
    if v[0] == '"' and v[-1] == '"' and len(v) >= 2:
        try:
            return json.loads(v)
        except ValueError:
            return v[1:-1]
    if v in ("true", "false"):
        return v == "true"
    if v in ("null", "~"):
        return None
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d*", v):
        return float(v)
    return v


def parse_value(v):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        out, pos = [], 0
        while pos < len(inner):
            m = ITEM_RE.match(inner, pos)
            if not m or m.end() == pos:
                break
            item = m.group(1).strip()
            if item:
                out.append(scalar(item))
            pos = m.end()
        return out
    return scalar(v)


def parse_frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return {}, text
    fm, key = {}, None
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if km:
            key = km.group(1)
            fm[key] = parse_value(km.group(2))
        elif key and line.lstrip().startswith("- "):          # block list
            if not isinstance(fm.get(key), list):
                fm[key] = []
            fm[key].append(scalar(line.lstrip()[2:]))
    return fm, text[m.end():]


def link_target(inner):
    """'Note#Heading|Alias' -> 'Note'."""
    return inner.replace("\\|", "|").split("|")[0].split("#")[0].strip()


def main():
    cfg_path = find_config()
    config = json.loads(cfg_path.read_text(encoding="utf-8"))
    folders = config.get("folders", {})
    content_dirs = [folders.get(k) for k in ("series", "articles", "terms", "literature") if folders.get(k)]

    files, md = [], []
    for dirpath, dirnames, filenames in os.walk(VAULT):
        rel_dir = Path(dirpath).relative_to(VAULT).as_posix()
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not (rel_dir == "." and d == "docs"))
        for f in sorted(filenames):
            rel = (Path(rel_dir) / f).as_posix() if rel_dir != "." else f
            files.append(rel)
            if f.endswith(".md"):
                md.append(rel)

    by_name = {}
    for rel in md:
        by_name.setdefault(Path(rel).stem, rel)                 # Obsidian resolves by note name
    by_base = {}
    for rel in files:
        by_base.setdefault(Path(rel).name, rel)

    def resolve(target):
        if not target:
            return None
        if target in by_name:
            return by_name[target]
        if target.endswith(".md") and target[:-3] in by_name:
            return by_name[target[:-3]]
        return by_base.get(target) or by_base.get(Path(target).name)

    def linkify(v):
        if isinstance(v, str):
            m = re.fullmatch(r"\[\[([^\]]+)\]\]", v.strip())
            if m:
                return {"path": resolve(link_target(m.group(1))) or link_target(m.group(1)) + ".md"}
            return v
        if isinstance(v, list):
            return [linkify(x) for x in v]
        return v

    pages, notes = [], {}
    for rel in md:
        p = VAULT / rel
        text = p.read_text(encoding="utf-8").replace("\r\n", "\n")
        fm, body = parse_frontmatter(text)
        out = []
        for m in LINK_RE.finditer(text):                       # body and frontmatter, like Dataview
            target = resolve(link_target(m.group(1)))
            if target and target.endswith(".md") and target != rel and target not in out:
                out.append(target)
        st = p.stat()
        page = {k: linkify(v) for k, v in fm.items()}
        page["file"] = {
            "name": Path(rel).stem, "path": rel, "folder": Path(rel).parent.as_posix().replace(".", ""),
            "mtime": int(st.st_mtime * 1000), "size": st.st_size,
            "outlinks": [{"path": t} for t in out], "inlinks": [],
        }
        pages.append(page)
        if rel == config.get("home", "Home.md") or any(rel.startswith(d + "/") for d in content_dirs):
            notes[rel] = text

    idx = {pg["file"]["path"]: pg for pg in pages}
    for pg in pages:
        for l in pg["file"]["outlinks"]:
            if l["path"] in idx:
                idx[l["path"]]["file"]["inlinks"].append({"path": pg["file"]["path"]})

    data = {
        "configPath": cfg_path.relative_to(VAULT).as_posix(),
        "config": config,
        "topFolders": sorted({f.split("/")[0] for f in files if "/" in f}),
        "files": files,
        "pages": pages,
        "notes": notes,
    }
    js = "// Generated by docs/preview/build_data.py from the vault notes. Do not edit.\n"
    js += "window.KB_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n"
    (HERE / "data.js").write_text(js, encoding="utf-8", newline="\n")
    print(f"data.js: {len(pages)} pages, {len(notes)} note bodies, {len(files)} files")


if __name__ == "__main__":
    main()
