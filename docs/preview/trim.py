"""Trim the empty page background below the content of a screenshot and report its size.

    python docs/preview/trim.py <png> [<png> ...]

The bottom rows that have the same colour as the bottom-left pixel are cut, leaving a margin of
MARGIN px. Needs Pillow; without it the files are left as they are.
"""
import sys
from pathlib import Path

MARGIN = 28

try:
    from PIL import Image, ImageChops
except ImportError:  # pragma: no cover
    Image = None

for arg in sys.argv[1:]:
    p = Path(arg)
    if Image is None:
        print(f"{p.name}: Pillow not installed, not trimmed")
        continue
    im = Image.open(p).convert("RGB")
    w, h = im.size
    bg = Image.new("RGB", (w, h), im.getpixel((0, h - 1)))
    box = ImageChops.difference(im, bg).getbbox()
    if box:
        bottom = min(h, box[3] + MARGIN)
        if bottom < h:
            im = im.crop((0, 0, w, bottom))
    im.save(p, optimize=True)
    print(f"{p.name}: {im.size[0]}x{im.size[1]}, {p.stat().st_size // 1024} KB")
