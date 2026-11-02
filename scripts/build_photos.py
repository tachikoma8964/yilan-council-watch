"""Write site/photos/ and the two photo indexes.

Incumbents: the portrait on each member's page of the council site (data/raw/council-photos/<id>.jpg,
fetched from https://www.ilcc.gov.tw/pictures/people/<id>.JPG).
Other 2026 candidates: their portrait in the 111 年 election gazette when they ran then
(extract_gazette_photos finds it), otherwise a file placed by hand in data/raw/candidate-photos/<name>.jpg
with its source URL listed in data/raw/candidate-photos/sources.json.
"""
import json
import sys
import urllib.parse
from pathlib import Path

import fitz
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_gazette_photos as gazette
import ilcc

COUNCIL = ilcc.RAW / "council-photos"
HAND = ilcc.RAW / "candidate-photos"
OUT = ilcc.ROOT / "site" / "photos"


def main():
    members = json.loads((ilcc.PROCESSED / "councilors-20.json").read_text(encoding="utf-8"))["members"]
    candidates = json.loads((ilcc.PROCESSED / "candidates-21.json").read_text(encoding="utf-8"))["candidates"]
    OUT.mkdir(parents=True, exist_ok=True)

    member_index = {}
    for m in members:
        gazette.write(Image.open(COUNCIL / f"{m['id']}.jpg"), m["id"])
        member_index[m["id"]] = {"source": f"https://www.ilcc.gov.tw/pictures/people/{m['id']}.JPG", "from": "council"}
    (ilcc.PROCESSED / "member-photos.json").write_text(json.dumps(member_index, ensure_ascii=False, indent=1), encoding="utf-8")

    roster = {m["name"] for m in members}
    others = [c["name"] for c in candidates if c["name"] not in roster]
    in_gazette = {}
    for number in range(1, 14):
        doc = fitz.open(gazette.GAZETTE / f"d{number}.pdf")
        for name, xref, page_no in gazette.portraits(doc, number):
            if name in others and name not in in_gazette:
                in_gazette[name] = (doc, xref, gazette.source_url(number), page_no)
    # township mayor gazettes of 2022: several newcomers ran for mayor then
    mayor_dir = gazette.GAZETTE / "mayor"
    manifest = {Path(line).name: line for line in (mayor_dir / "manifest.txt").read_text(encoding="utf-8").split("\n") if line}
    for pdf in sorted(mayor_dir.glob("*.pdf")):
        doc = fitz.open(pdf)
        for name, xref, page_no in gazette.portraits(doc, 0, stem=pdf.stem, png_dir=mayor_dir / "png"):
            if name in others and name not in in_gazette:
                url = "https://eebulletin.cec.gov.tw/" + urllib.parse.quote(manifest.get(pdf.name, pdf.name))
                in_gazette[name] = (doc, xref, url, page_no)
    hand_sources = json.loads((HAND / "sources.json").read_text(encoding="utf-8")) if (HAND / "sources.json").exists() else {}

    candidate_index, missing = {}, []
    for i, c in enumerate(candidates, 1):
        name = c["name"]
        if name in roster:
            continue
        key = f"c21-{i:02d}"
        if name in in_gazette:
            doc, xref, url, page_no = in_gazette[name]
            gazette.save(doc, xref, key)
            candidate_index[name] = {"file": key, "source": url, "page": page_no, "from": "gazette"}
        elif (HAND / f"{name}.jpg").exists() and name in hand_sources:
            gazette.write(Image.open(HAND / f"{name}.jpg"), key)
            candidate_index[name] = {"file": key, "source": hand_sources[name]["url"], "from": hand_sources[name]["from"]}
        else:
            missing.append(name)
    (ilcc.PROCESSED / "candidate-photos.json").write_text(json.dumps(candidate_index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"members {len(member_index)}; candidates with photo {len(candidate_index)}; missing {missing}")


if __name__ == "__main__":
    main()
