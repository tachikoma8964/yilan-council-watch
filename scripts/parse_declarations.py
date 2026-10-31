"""Turn the downloaded 財產申報 PDFs (監察院廉政專刊) into data/processed/assets-20.json.

One PDF per member: the latest 一般申報 listed on https://priso.cy.gov.tw/layout/baselist.
Counts are rows of the printed tables; money figures are the section totals the form itself prints.
"""
import glob
import json
import os
import re

import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDFS = os.path.join(ROOT, "data", "raw", "cy", "pdf")
OUT = os.path.join(ROOT, "data", "processed", "assets-20.json")
QUERY_PAGE = "https://priso.cy.gov.tw/layout/baselist"

TOTALS = {
    "cash": r"[（(]六[）)]現金.*?總金額[:：]新臺幣([\d,.]*)元",
    "deposit": r"[（(]七[）)]存款.*?總金額[:：]新臺幣([\d,.]*)元",
    "stock": r"1\.股票[（(]總價額[:：]新臺幣([\d,.]*)元",
    "bond": r"2\.債券[（(]總價額[:：]新臺幣([\d,.]*)元",
    "fund": r"3\.基金受益憑證[（(]總價額[:：]新臺幣([\d,.]*)元",
    "debt": r"[（十(]十一[）)]債務[（(]總金額[:：]新臺幣([\d,.]*)元",
    "business": r"[（(]十二[）)]事業投資[（(]總金額[:：]新臺幣([\d,.]*)元",
}


def squash(text):
    return re.sub(r"\s+", "", text or "")


def money(match):
    digits = match.group(1).replace(",", "") if match else ""
    return round(float(digits)) if digits else 0


def parse(path):
    doc = fitz.open(path)
    text = squash("".join(page.get_text() for page in doc))
    name = re.search(r"申報人姓名(\S+?)服務機關", text)
    period = re.search(r"廉政專刊第(\d+)期", text)
    date = re.search(r"申報日(\d+)年(\d+)月(\d+)日", text)
    kind = re.search(r"申報類別(.{2,6}?)(?:配偶|稱謂)", text)
    pages = [int(m.group(1)) for m in (re.search(r"廉政專刊第\d+期\s*(\d+)", p.get_text()) for p in doc) if m]
    if not pages:
        pages = [int(m.group(1)) for m in (re.search(r"\n(\d{1,4})\s*\n公\s*職", p.get_text()) for p in doc) if m]
    me = name.group(1)

    count = {"land": [0, 0], "building": [0, 0], "vehicle": [0, 0]}
    section = None
    for page in doc:
        for table in page.find_tables().tables:
            rows = table.extract()
            head = squash("".join(c or "" for c in rows[0])) if rows else ""
            if "坐落" in head:
                section = "land"
            elif "建物標示" in head:
                section = "building"
            elif "廠牌型號" in head:
                section = "vehicle"
            elif head and any(k in head for k in ("船舶", "種類總噸數", "型式製造廠", "幣別所有人", "存放機構", "名稱所有人", "投資人", "債權人", "財產種類", "保險公司", "虛擬")) or "稱謂" in head or "申報人姓名" in head:
                section = None
            if section is None:
                continue
            owner_col = {"land": 3, "building": 3, "vehicle": 2}[section]
            for row in rows:
                if len(row) <= owner_col:
                    continue
                owner = squash(row[owner_col])
                first = squash(row[0])
                if not owner or not first or "所有人" in owner or "坐落" in first or "建物標示" in first or "廠牌" in first:
                    continue
                count[section][0 if owner == me else 1] += 1

    result = {
        "name": me,
        "period": int(period.group(1)) if period else None,
        "pages": [min(pages), max(pages)] if pages else None,
        "declaredOn": f"{int(date.group(1)) + 1911}-{int(date.group(2)):02d}-{int(date.group(3)):02d}" if date else None,
        "kind": kind.group(1) if kind else None,
        "land": {"self": count["land"][0], "family": count["land"][1]},
        "building": {"self": count["building"][0], "family": count["building"][1]},
        "vehicle": {"self": count["vehicle"][0], "family": count["vehicle"][1]},
    }
    for key, pattern in TOTALS.items():
        result[key] = money(re.search(pattern, text))
    return result


def main():
    roster = {m["name"]: m["id"] for m in json.load(open(os.path.join(ROOT, "data/processed/councilors-20.json"), encoding="utf-8"))["members"]}
    out = {}
    for path in sorted(glob.glob(os.path.join(PDFS, "*.pdf"))):
        item = parse(path)
        if item["name"] in roster:
            out[roster[item["name"]]] = item
    json.dump({"source": QUERY_PAGE, "members": out}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    missing = [n for n in roster if roster[n] not in out]
    print(f"{len(out)} parsed; missing {missing}")
    for item in out.values():
        print(item["name"], item["period"], item["pages"], item["declaredOn"], item["kind"], "land", item["land"], "bld", item["building"],
              "cash", item["cash"], "dep", item["deposit"], "stock", item["stock"], "debt", item["debt"])


if __name__ == "__main__":
    main()
