"""List which member each downloaded 財產申報 PDF belongs to and which members still lack one."""
import glob, json, os, re, sys
import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDFS = os.path.join(ROOT, "data", "raw", "cy", "pdf")


def header(path):
    text = fitz.open(path)[0].get_text()
    name = re.search(r"申報人姓名\s*(\S+)", text)
    date = re.search(r"申\s*報\s*日\s*(\d+)\s*年\s*(\d+)\s*月\s*(\d+)\s*日", text)
    return (name.group(1) if name else None), (tuple(map(int, date.groups())) if date else None)


if __name__ == "__main__":
    roster = [m["name"] for m in json.load(open(os.path.join(ROOT, "data/processed/councilors-20.json"), encoding="utf-8"))["members"]]
    got = {}
    for f in sorted(glob.glob(os.path.join(PDFS, "*.pdf"))):
        name, date = header(f)
        got[name] = os.path.basename(f)
        print(os.path.basename(f), name, date)
    print("missing:", [n for n in roster if n not in got])
