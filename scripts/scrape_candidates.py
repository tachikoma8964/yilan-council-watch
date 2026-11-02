"""Read the CEC roster of registered candidates for the 2026 (115年) county councilor election
and keep the Yilan rows: data/processed/candidates-21.json.

Source: 中央選舉委員會「115年地方公職人員選舉候選人登記名冊」, table 4-1.
This is the registration roster, not the final candidate list, which the county commission
announces later with ballot numbers.
"""
import json
import re
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ilcc

PDF = ilcc.RAW / "cec" / "115-council-candidates.pdf"
OUT = ilcc.PROCESSED / "candidates-21.json"
PAGE = "https://web.cec.gov.tw/central/article/64709"
FILE = "https://web.cec.gov.tw/api/file/9ccb6224-20be-479e-931f-81aa6155f28a.pdf"
DISTRICT = re.compile(r"宜蘭縣第(\d+)選舉區")
DATE = re.compile(r"(\d{3})/(\d{2})/(\d{2})")
HEADER = {"選舉區", "登記日期", "姓名", "推薦之政黨", "備註"}


def main():
    text = "".join(page.get_text() for page in fitz.open(PDF))
    made = re.search(r"製表日期：(\d{3})年(\d{2})月(\d{2})日", text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    rows, i = [], 0
    while i < len(lines):
        district = DISTRICT.fullmatch(lines[i])
        date = DATE.fullmatch(lines[i + 1]) if district and i + 1 < len(lines) else None
        if not date:
            i += 1
            continue
        # name lines, then the party, up to the next row or a page header
        j = i + 2
        parts = []
        while j < len(lines) and not DISTRICT.fullmatch(lines[j]) and lines[j] not in HEADER and not lines[j].startswith(("115年縣市議員", "製表日期")):
            parts.append(lines[j])
            j += 1
        party = parts.pop()
        name = " ".join(parts)
        han = re.match(r"[\u4e00-\u9fff·‧]+", name).group(0)
        rows.append({
            "district": int(district.group(1)),
            "registeredOn": f"{int(date.group(1)) + 1911}-{date.group(2)}-{date.group(3)}",
            "name": han, "fullName": name if name != han else None,
            "party": None if party == "無" else party,
        })
        i = j
    rows.sort(key=lambda r: (r["district"], r["registeredOn"], r["name"]))
    data = {
        "term": 21, "election": "115年地方公職人員選舉",
        "tableDate": f"{int(made.group(1)) + 1911}-{made.group(2)}-{made.group(3)}" if made else None,
        "sourcePage": PAGE, "sourceFile": FILE, "candidates": rows,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(rows), "candidates;", sorted({r["party"] for r in rows if r["party"]}))


if __name__ == "__main__":
    main()
