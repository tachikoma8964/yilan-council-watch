"""Draw site/og.png (1200x630), the preview image shown when the site is shared."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
INK, RED, RED_DEEP = (26, 26, 26), (193, 39, 45), (110, 21, 25)
TINTS = {"n": (249, 222, 196), "c": (243, 230, 188), "s": (236, 208, 196), "w": (230, 224, 208), "i": (240, 208, 214)}
# (number, group, col, row, colspan, rowspan) on a 4 x 4 grid, same arrangement as the site's map
TILES = [(9, "w", 0, 0, 1, 2), (4, "c", 1, 0, 1, 1), (3, "n", 2, 0, 1, 1), (2, "n", 3, 0, 1, 1),
         (1, "c", 1, 1, 2, 1), (5, "c", 3, 1, 1, 1), (8, "s", 0, 2, 1, 1), (6, "s", 1, 2, 2, 1),
         (7, "s", 3, 2, 1, 1), (10, "s", 0, 3, 4, 1)]

img = Image.new("RGB", (1200, 630), "white")
d = ImageDraw.Draw(img)
big, mid, small = (ImageFont.truetype(FONT, s) for s in (96, 40, 30))
d.text((70, 150), "宜蘭縣", font=big, fill=INK)
d.text((70, 260), "議會觀測", font=big, fill=INK)
d.text((70, 410), "第 20 屆議員、議案與財產申報", font=mid, fill=INK)
d.text((70, 475), "每個數字都連到官網原文，不評價、不排名", font=small, fill=(90, 90, 90))
x0, y0, cell, row = 700, 60, 105, 125
for no, group, c, r, cs, rs in TILES:
    box = (x0 + c * cell * 1.1, y0 + r * row, x0 + (c + cs) * cell * 1.1, y0 + (r + rs) * row)
    d.rectangle(box, fill=TINTS[group], outline=INK, width=4)
    d.text((box[0] + 12, box[1] + 8), f"{no:02d}", font=small, fill=RED_DEEP)
img.save(ROOT / "site" / "og.png", optimize=True)
