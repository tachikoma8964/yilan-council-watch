"""Cut member portraits out of the CEC election gazette (111年 縣市議員, 宜蘭縣).

The gazette PDFs are scanned pages with no text layer, so names are read with macOS Vision
(scripts/ocr_lines.swift) and paired with the portrait printed directly below each name.
Needs: .venv with pymupdf and pillow, and `swiftc` for the OCR helper.
"""
import hashlib
import io
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

import fitz
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ilcc

GAZETTE = ilcc.RAW / "gazette"
OCR_BIN = GAZETTE / "ocr_lines"
OUT = ilcc.ROOT / "site" / "photos"
SOURCE_DIR = "01選舉公報/06縣市議員/111年/14宜蘭縣"
CJK_NAME = re.compile(r"^[一-鿿·‧]{2,4}$")
FULL, THUMB = 320, 128
# Members who took office after the 2022 election are not in that gazette (黃雯如: 2024 by-election).
# Their portrait is the one on their own page of the council's site.
COUNCIL_PHOTOS = {"黃雯如": "https://www.ilcc.gov.tw/pictures/people/A2035.JPG"}
# Names the OCR misreads, checked by eye against the printed page.
OCR_ALIASES = {}


def source_url(district):
    return "https://bulletin.cec.gov.tw/" + urllib.parse.quote(f"{SOURCE_DIR}/宜蘭縣第{district}選舉區.pdf")


def ocr_lines(png):
    cache = png.with_suffix(".tsv")
    if not cache.exists():
        if not OCR_BIN.exists():
            subprocess.run(["swiftc", "-O", str(Path(__file__).with_name("ocr_lines.swift")), "-o", str(OCR_BIN)], check=True)
        cache.write_text(subprocess.run([str(OCR_BIN), str(png)], capture_output=True, text=True, check=True).stdout, encoding="utf-8")
    rows = []
    for line in cache.read_text(encoding="utf-8").splitlines():
        x, y, w, h, text = line.split("\t", 4)
        rows.append((float(x), float(y), float(w), float(h), text.replace(" ", "").replace("　", "")))
    return rows


def portraits(doc, number):
    """Yield (name, xref, page_no) for each portrait whose printed name could be read."""
    for page_no, page in enumerate(doc, 1):
        png = GAZETTE / "png" / f"d{number}-p{page_no}.png"
        if not png.exists():
            png.parent.mkdir(exist_ok=True)
            page.get_pixmap(dpi=80).save(png)
        lines = [r for r in ocr_lines(png) if CJK_NAME.match(r[4])]
        pw, ph = page.rect.width, page.rect.height
        for info in page.get_image_info(xrefs=True):
            if not (0.65 < info["width"] / info["height"] < 0.9 and info["width"] > 300):
                continue
            x0, y0, x1, _ = info["bbox"]
            left, right, top = x0 / pw - 0.02, x1 / pw + 0.02, y0 / ph
            near = [r for r in lines if left <= r[0] + r[2] / 2 <= right and top - 0.06 <= r[1] + r[3] <= top + 0.005]
            name = min(near, key=lambda r: top - (r[1] + r[3]))[4] if near else None
            name = OCR_ALIASES.get(name, name)
            yield name, info["xref"], page_no


def save(doc, xref, member_id):
    write(Image.open(io.BytesIO(doc.extract_image(xref)["image"])), member_id)


def write(raw, member_id):
    raw = raw.convert("RGB")
    for width, suffix in ((FULL, ""), (THUMB, "-s")):
        copy = raw.resize((width, round(raw.height * width / raw.width)), Image.LANCZOS)
        copy.save(OUT / f"{member_id}{suffix}.jpg", quality=82, optimize=True, progressive=True)


def main():
    roster = {m["name"]: m for m in json.loads((ilcc.PROCESSED / "councilors-20.json").read_text(encoding="utf-8"))["members"]}
    OUT.mkdir(parents=True, exist_ok=True)
    found, unread = {}, []
    for number in range(1, 14):
        doc = fitz.open(GAZETTE / f"d{number}.pdf")
        for name, xref, page_no in portraits(doc, number):
            if name is None:
                unread.append((number, page_no, xref))
            elif name in roster and name not in found:
                found[name] = (number, page_no, xref, doc)
    index = {}
    for name, (number, page_no, xref, doc) in found.items():
        member = roster[name]
        save(doc, xref, member["id"])
        index[member["id"]] = {"source": source_url(number), "page": page_no, "gazetteDistrict": number}
    for name, url in COUNCIL_PHOTOS.items():
        member_id = roster[name]["id"]
        write(Image.open(GAZETTE / f"{member_id}.jpg"), member_id)
        index[member_id] = {"source": url, "from": "council"}
        found[name] = None
    (ilcc.PROCESSED / "member-photos.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    missing = [n for n in roster if n not in found]
    print(f"{len(found)}/{len(roster)} photos; missing {missing}; portraits with unreadable name {unread}")


if __name__ == "__main__":
    main()
