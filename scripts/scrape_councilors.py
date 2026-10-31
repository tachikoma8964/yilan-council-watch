"""Scrape the current-term councilor list from the council site into data/processed/."""
import json
import re
import sys
from datetime import date

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import ilcc

LIST_PATH = "Html/H_05/H_05.asp"
MEMBER_LINK = re.compile(r'href="[^"]*Sys_id=PMZ([^,"]+),(\d*),([A-Z]*),(A\d+),"')

# An empty code on the council's list is not confirmed to mean "no party", so it is left unlabeled.
PARTY_NAMES = {
    "DDP": "民主進步黨",
    "KMT": "中國國民黨",
}


def main():
    html = ilcc.fetch(LIST_PATH)
    ilcc.save_raw("councilors-current.html", html)

    members = []
    seen = set()
    for name, district, party_code, member_id in MEMBER_LINK.findall(html):
        if member_id in seen:
            continue
        seen.add(member_id)
        members.append({
            "id": member_id,
            "name": name.replace("　", ""),
            "district": int(district) if district else None,
            "partyCode": party_code,
            "party": PARTY_NAMES.get(party_code),
            "source": ilcc.BASE + "Incfiles/PBrowse.aspx?Sys_id=PMZ" + name,
        })

    members.sort(key=lambda m: (m["district"] or 99, m["id"]))
    out = {
        "term": 20,
        "retrieved": date.today().isoformat(),
        "sourcePage": ilcc.BASE + LIST_PATH,
        "members": members,
    }
    ilcc.PROCESSED.mkdir(parents=True, exist_ok=True)
    path = ilcc.PROCESSED / "councilors-20.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{len(members)} members -> {path}")
    by_district = {}
    for m in members:
        by_district.setdefault(m["district"], []).append(m["name"])
    for d in sorted(by_district, key=lambda k: (k is None, k)):
        print(d, len(by_district[d]), "、".join(by_district[d]))
    print("parties:", sorted({m["partyCode"] for m in members}))


if __name__ == "__main__":
    main()
