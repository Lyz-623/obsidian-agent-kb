"""Outline sync: keep every series map in step with the current structure of its articles.

Run after every article edit (from anywhere; the vault is this file's parent folder):
    python "90 System/outline-sync.py"           # write changes
    python "90 System/outline-sync.py" --check   # report differences only (exit 1 if any)

All folder names, note types and formatting strings come from kb.config.json next to this file.

Rules (the articles are the source of truth):
- an article's frontmatter `sections` is taken from the `## ` headings of its body;
- each article entry in a series map is `## [[Title]]` + blank line + summary + outline.summary_end
  + sections joined by outline.section_sep;
- entries are sorted by `seq`; the series map's frontmatter `articles` holds the actual count;
- the "{articles} articles in {series} series" count in the first front note is kept in sync
  (pattern from outline.about_count).
The intro paragraph, the question callout and the navigation callout of a series map are left
untouched; entries are written between the intro and the navigation callout. The file's own line
endings (CRLF/LF) are preserved.
"""
import json
import re
import sys
from pathlib import Path

SYSTEM = Path(__file__).resolve().parent
ROOT = SYSTEM.parent
CONFIG = json.loads((SYSTEM / "kb.config.json").read_text(encoding="utf-8"))
FOLDERS = CONFIG["folders"]
TYPES = CONFIG["types"]
OUT = {"summary_end": ". ", "section_sep": " · ", "nav_callout": "series",
       "about_count": "{articles} articles in {series} series"}
OUT.update(CONFIG.get("outline", {}))
ART = ROOT / FOLDERS["articles"]
MAP = ROOT / FOLDERS["series"]
CHECK = "--check" in sys.argv
CRLF, LF = chr(13) + chr(10), chr(10)
NEWLINE = {}
changes = []


def read(path):
    raw = path.read_bytes().decode("utf-8")
    NEWLINE[path] = CRLF if CRLF in raw else LF
    return raw.replace(CRLF, LF)


def split_fm(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return (m.group(1), text[m.end():]) if m else ("", text)


def fm_get(fm, key):
    m = re.search(rf"^{key}:[ \t]*(.*)$", fm, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        v = v[1:-1]
        if m.group(1).strip()[0] == "'":
            v = v.replace("''", "'")
    return v


def write(path, old, new):
    if old != new:
        changes.append(path.relative_to(ROOT).as_posix())
        if not CHECK:
            path.write_bytes(new.replace(LF, NEWLINE[path]).encode("utf-8"))


def quote(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# 1. articles: sections <- H2 headings
articles = []
for p in sorted(ART.glob("*.md")):
    text = read(p)
    fm, body = split_fm(text)
    if fm_get(fm, "type") != TYPES["article"]:
        continue
    body_nocode = re.sub(r"```.*?```", "", body, flags=re.S)
    heads = [h.strip() for h in re.findall(r"^## (.+)$", body_nocode, re.M)]
    new_line = "sections: [" + ", ".join(quote(h) for h in heads) + "]"
    if re.search(r"^sections:.*$", fm, re.M):
        fm2 = re.sub(r"^sections:.*$", lambda _: new_line, fm, count=1, flags=re.M)
    else:
        fm2 = fm + "\n" + new_line
    write(p, text, text.replace(fm, fm2, 1))
    try:
        series_no, seq = int(fm_get(fm, "series_no")), int(fm_get(fm, "seq"))
    except (TypeError, ValueError):
        print(f"!! {p.name}: series_no / seq missing or not an integer, skipped")
        continue
    articles.append({
        "title": p.stem,
        "series_no": series_no,
        "seq": seq,
        "summary": (fm_get(fm, "summary") or "").rstrip().rstrip(OUT["summary_end"].strip() or "."),
        "sections": heads,
    })

# 2. series maps: rebuild the article entries
nav = re.compile(rf"^> \[!{re.escape(OUT['nav_callout'])}\]", re.M)
for p in sorted(MAP.glob("[0-9]*.md")):
    text = read(p)
    fm, body = split_fm(text)
    if fm_get(fm, "type") != TYPES["series"]:
        continue
    n = int(fm_get(fm, "series_no"))
    arts = sorted((a for a in articles if a["series_no"] == n), key=lambda a: a["seq"])
    entries = "\n\n".join(
        f"## [[{a['title']}]]\n\n{a['summary']}{OUT['summary_end']}" + OUT["section_sep"].join(a["sections"])
        for a in arts
    )
    m_nav = nav.search(body)
    end = m_nav.start() if m_nav else len(body)
    m_first = re.search(r"^## \[\[", body[:end], re.M)
    if m_first:
        start = m_first.start()
    else:   # no entries yet: insert right before the navigation callout
        start = end
    tail = body[end:]
    head = body[:start].rstrip("\n") + "\n\n"
    body2 = head + (entries + "\n\n" if entries else "") + tail
    if not m_nav:
        body2 = body2.rstrip("\n") + "\n"
    fm2 = re.sub(r"^articles:.*$", f"articles: {len(arts)}", fm, flags=re.M)
    write(p, text, text.replace(fm, fm2, 1).replace(body, body2, 1))

# 3. first front note ("About this collection"): article / series counts
fronts = CONFIG.get("front_notes") or []
about = MAP / f"{fronts[0]}.md" if fronts else None
if about and about.exists():
    t = read(about)
    nseries = len({a["series_no"] for a in articles})
    tpl = OUT["about_count"]
    pat = re.escape(tpl).replace(r"\{articles\}", r"\d+").replace(r"\{series\}", r"\d+")
    t2 = re.sub(pat, tpl.format(articles=len(articles), series=nseries), t)
    write(about, t, t2)

if CHECK:
    print("Out of sync: " + ", ".join(changes) if changes else "No differences.")
else:
    print("Synced: " + ", ".join(changes) if changes else "Already in sync.")
sys.exit(1 if CHECK and changes else 0)
