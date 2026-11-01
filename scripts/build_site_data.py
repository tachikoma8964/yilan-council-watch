"""Merge scraped councilors and bills into the single JSON file the static site reads."""
import json
from datetime import date
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ilcc

TERM = 20
SITE_DATA = ilcc.ROOT / "site" / "data" / "data.json"

# Constituencies of the 20th term. Source: Wikipedia 宜蘭縣議會; seat counts match the council's list.
# To be checked against the Central Election Commission announcement.
DISTRICTS = [
    (1, "宜蘭市", 7), (2, "頭城鎮", 2), (3, "礁溪鄉", 2), (4, "員山鄉", 2), (5, "壯圍鄉", 2),
    (6, "羅東鎮", 5), (7, "五結鄉", 3), (8, "冬山鄉", 4), (9, "三星鄉、大同鄉", 1),
    (10, "蘇澳鎮、南澳鄉", 3), (11, "全縣（平地原住民）", 1),
    (12, "宜蘭市、頭城鎮、礁溪鄉、壯圍鄉、員山鄉、三星鄉、大同鄉（山地原住民）", 1),
    (13, "羅東鎮、蘇澳鎮、冬山鄉、五結鄉、南澳鄉（山地原住民）", 1),
]
# Names in the proposer field that are not members: kept as the source wrote them, counted for nobody.
SOURCE_ISSUES = {
    "林佩穎": "提案人欄的「林佩穎」疑為「林佩螢」筆誤，未計入任何議員",
    "交通": "提案人欄位異常，未計入任何議員",
    "建設": "提案人欄位異常，未計入任何議員",
}


def proposed_on(instance):
    match = re.search(r"(\d{3})(\d{2})(\d{2})\d{3}$", instance)
    return f"{int(match.group(1)) + 1911}-{match.group(2)}-{match.group(3)}" if match else None


def short_resolution(text):
    if not text:
        return "無紀錄"
    if "審查意見" in text:
        return "照審查意見通過"
    if "照案" in text:
        return "照案通過"
    return text.strip("。 ")


def main():
    councilors = json.loads((ilcc.PROCESSED / "councilors-20.json").read_text(encoding="utf-8"))
    motions = json.loads((ilcc.PROCESSED / "bills-motions.json").read_text(encoding="utf-8"))
    roster = {m["name"]: m for m in councilors["members"]}
    photos = json.loads((ilcc.PROCESSED / "member-photos.json").read_text(encoding="utf-8"))
    declared = json.loads((ilcc.PROCESSED / "assets-20.json").read_text(encoding="utf-8"))
    bills = [b for b in motions["bills"] if b["term"] == TERM]

    proposed, cosigned, categories = Counter(), Counter(), {}
    out_bills, outsiders = [], Counter()
    for b in sorted(bills, key=lambda x: (proposed_on(x["id"]) or "", x["id"]), reverse=True):
        issue = next((SOURCE_ISSUES[n] for n in b["proposers"] if n in SOURCE_ISSUES), None)
        for name in b["proposers"]:
            if name in roster:
                proposed[name] += 1
                categories.setdefault(name, Counter())[re.sub(r"\s+", "", b["category"] or "")] += 1
            elif name not in SOURCE_ISSUES:
                outsiders[name] += 1
        for name in set(b["cosigners"]):
            if name in roster:
                cosigned[name] += 1
        out_bills.append({
            "id": b["id"], "no": b["caseNo"], "on": proposed_on(b["id"]), "title": b["title"],
            "by": b["proposers"], "with": b["cosigners"], "cat": re.sub(r"\s+", "", b["category"] or ""), "team": b["committee"],
            "session": f'第 {b["session"]} 次{b["sessionType"]}', "reviewed": b["reviewDate"] or None,
            "result": short_resolution(b["resolution"]), "url": b["source"], "issue": issue,
        })

    by_session = {}
    for item in out_bills:
        by_session.setdefault(item["session"], []).append(item)
    def span(items):
        """First and last registration date of a session, ignoring stray entries months away from the rest."""
        days = sorted(date.fromisoformat(i["on"]) for i in items)
        middle = days[len(days) // 2]
        near = [d for d in days if abs((d - middle).days) <= 120]
        return near[0].isoformat(), near[-1].isoformat()

    sessions = [{
        "label": label, "n": len(items), "from": span(items)[0], "to": span(items)[1],
        "members": len({p for i in items for p in i["by"] if p in roster}),
    } for label, items in by_session.items()]
    sessions.sort(key=lambda s: s["from"], reverse=True)

    members = [{
        "id": m["id"], "name": m["name"], "district": m["district"], "party": m["party"],
        "proposed": proposed[m["name"]], "cosigned": cosigned[m["name"]],
        "categories": dict(categories.get(m["name"], {})),
        "photo": photos.get(m["id"]),
        "assets": {k: v for k, v in declared["members"][m["id"]].items() if k != "name"} if m["id"] in declared["members"] else None,
    } for m in councilors["members"]]

    data = {
        "term": TERM, "termYears": "2022–2026",
        "retrieved": motions["retrieved"],
        "sources": {"members": councilors["sourcePage"], "bills": "https://www.ilcc.gov.tw/Html/H_08/H_08.aspx"},
        "assetSource": declared["source"],
        "sessions": sessions,
        "photoCredit": "中央選舉委員會選舉公報（111 年，宜蘭縣選舉委員會編印）",
        "districts": [{"n": n, "area": area, "seats": seats} for n, area, seats in DISTRICTS],
        "members": members,
        "outsiders": [{"name": n, "proposed": c} for n, c in outsiders.most_common()],
        "bills": out_bills,
    }
    SITE_DATA.parent.mkdir(parents=True, exist_ok=True)
    SITE_DATA.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(members)} members, {len(out_bills)} bills, outsiders {dict(outsiders)} -> {SITE_DATA.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
