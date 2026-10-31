"""Scrape councilor-sponsored bills (議員提案) from the council's bill database.

One search POST returns every bill; each bill's detail page then gives proposer,
co-signers, category, committee, session and the reading resolution. Raw detail
pages are cached under data/raw/ so a rerun only fetches what is missing.
"""
import html
import http.cookiejar
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ilcc

SEARCH_URL = ilcc.BASE + "Html/H_08/H_08.aspx"
DETAIL_URL = ilcc.BASE + "CSource/C06/C0601M01.aspx?Fmotion_instanceOS="
DELAY = 0.6
HIDDEN = ["__EVENTTARGET", "__EVENTARGUMENT", "__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION"]
LABELS = {
    "來源別": "source", "建檔日期": "filed", "議案程序": "procedure", "系統編號": "systemNo",
    "提案人": "proposers", "案號": "caseNo", "連署人": "cosigners", "類別": "category",
    "小組": "committee", "案由": "title", "法規名稱": "lawName", "辦法": "measure",
    "理由": "reason", "附件": "attachment", "審議日期": "reviewDate", "二讀決議": "resolution",
}

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
opener.addheaders = [("User-Agent", ilcc.USER_AGENT)]


def decode(raw):
    return raw.decode("big5", errors="replace")


def hidden(page, name):
    match = re.search(r'name="%s"[^>]*value="([^"]*)"' % name, page)
    return html.unescape(match.group(1)) if match else ""


def search_all(category):
    page = decode(opener.open(SEARCH_URL, timeout=60).read())
    form = {name: hidden(page, name) for name in HIDDEN}
    form.update({"ddlFmotion_category": category, "ddlFmotion_property": "", "txtKeyword": "", "btSearch": " -搜尋-"})
    body = urllib.parse.urlencode(form, encoding="big5").encode("ascii")
    request = urllib.request.Request(SEARCH_URL, data=body, headers={"Content-Type": "application/x-www-form-urlencoded", "Referer": SEARCH_URL})
    return decode(opener.open(request, timeout=180).read())


def parse_list(page):
    items = {}
    for row in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", page):
        link = re.search(r'Fmotion_instanceOS=([^&"]+)&amp;[^"]*"[^>]*>\s*([^<]+?)\s*</a>', row)
        if not link:
            continue
        cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip() for c in re.findall(r"(?is)<td[^>]*>(.*?)</td>", row)]
        items[link.group(1)] = {"instance": link.group(1), "caseLabel": link.group(2).strip(), "title": cells[-1] if cells else ""}
    return items


def fetch_detail(instance):
    cache = ilcc.RAW / "bills" / (instance + ".html")
    if cache.exists():
        return cache.read_text(encoding="utf-8")
    url = DETAIL_URL + urllib.parse.quote(instance, encoding="big5")
    for attempt in range(3):
        try:
            text = decode(opener.open(url, timeout=60).read())
            break
        except urllib.error.URLError:
            if attempt == 2:
                raise
            time.sleep(3)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(text, encoding="utf-8")
    time.sleep(DELAY)
    return text


def clean_cells(page):
    page = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<!--.*?-->", "", page)
    cells = [re.sub(r"[ \t\r\n\xa0]+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip(" \t\r\n\xa0") for c in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", page)]
    return [c for c in cells if c and c != "\xa0"]


def names(text):
    # Split on commas and ASCII spaces only: a full-width space sits inside names such as 林　麗.
    tokens = [n.replace("　", "") for n in re.split(r"[、，,]|[ \t\r\n\xa0]+", text) if n]
    merged = []
    for token in tokens:
        # The site writes two-character names with a space inside (林  麗); join adjacent single characters.
        if merged and len(token) == 1 and len(merged[-1]) == 1:
            merged[-1] += token
        else:
            merged.append(token)
    return merged


def parse_detail(instance, page):
    cells = clean_cells(page)
    fields, tail, key = {}, [], None
    for cell in cells:
        label = LABELS.get(re.sub(r"\s+", "", cell))
        if label and label not in fields:
            key = label
            fields[key] = ""
            continue
        if key == "attachment":
            tail.append(cell)
        elif key and not fields[key]:
            fields[key] = cell
    heading = next((c for c in cells if "議案資料" in c), "")
    term = re.search(r"第\s*(\d+)\s*屆\s*第\s*(\d+)\s*次\s*(\S+)", heading)
    meeting = next((c for c in tail if re.search(r"第\s*\d+\s*屆", c)), "")
    filed = fields.get("filed", "")
    return {
        "id": instance,
        "caseNo": fields.get("caseNo"),
        "term": int(term.group(1)) if term else None,
        "session": int(term.group(2)) if term else None,
        "sessionType": term.group(3) if term else None,
        "filed": filed.replace("/", "-"),
        "procedure": fields.get("procedure"),
        "proposers": names(fields.get("proposers", "")),
        "cosigners": names(fields.get("cosigners", "")),
        "category": fields.get("category"),
        "committee": fields.get("committee"),
        "title": fields.get("title"),
        "meeting": meeting,
        "reviewDate": fields.get("reviewDate", "").replace("/", "-"),
        "resolution": fields.get("resolution"),
        "source": DETAIL_URL + urllib.parse.quote(instance, encoding="utf-8"),
    }


def main(category="議員提案", slug="motions"):
    listing = parse_list(search_all(category))
    print(f"{len(listing)} {category} found", flush=True)
    bills, failed = [], []
    for index, instance in enumerate(sorted(listing), 1):
        try:
            bill = parse_detail(instance, fetch_detail(instance))
            bill["listTitle"] = listing[instance]["title"]
            bills.append(bill)
        except Exception as error:
            failed.append({"id": instance, "error": str(error)})
        if index % 25 == 0:
            print(f"  {index}/{len(listing)}", flush=True)
    out = {"category": category, "retrieved": date.today().isoformat(), "count": len(bills), "failed": failed, "bills": bills}
    ilcc.PROCESSED.mkdir(parents=True, exist_ok=True)
    path = ilcc.PROCESSED / f"bills-{slug}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"done: {len(bills)} parsed, {len(failed)} failed -> {path}", flush=True)


if __name__ == "__main__":
    main()
