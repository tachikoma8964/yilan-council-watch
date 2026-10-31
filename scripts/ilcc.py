"""Shared helpers for reading the Yilan County Council site (Big5, classic ASP)."""
import re
import time
import urllib.request
from pathlib import Path

BASE = "https://www.ilcc.gov.tw/"
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
USER_AGENT = "Mozilla/5.0 (compatible; yilan-council-watch/0.1; public-record reader)"


def fetch(path, data=None, delay=1.0):
    """GET (or POST) a page from the council site and return it decoded from Big5."""
    request = urllib.request.Request(BASE + path, data=data, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read()
    time.sleep(delay)
    return body.decode("big5", errors="replace")


def save_raw(name, text):
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / name).write_text(text, encoding="utf-8")


def strip_tags(html):
    html = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html)
    return re.sub(r"[ \t　]+", " ", re.sub(r"(?s)<[^>]+>", " ", html))
