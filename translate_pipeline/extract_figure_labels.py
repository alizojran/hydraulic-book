#!/usr/bin/env python3
"""Extract German text labels that lie INSIDE figure regions (axis labels,
component names in schematics, legends ...) so they can be compiled into a
German->Chinese reference table. These were deliberately excluded from the
translatable prose by extract.py and only appear baked into figure images."""
import fitz, json, re, os, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract import figure_regions, PDF, clean

WORD = re.compile(r'[A-Za-zÄÖÜäöüß]{3,}')

def center_inside(bbox, regions):
    cx = (bbox[0] + bbox[2]) / 2
    cy = (bbox[1] + bbox[3]) / 2
    for r in regions:
        if r.x0 <= cx <= r.x1 and r.y0 <= cy <= r.y1:
            return True
    return False

def good_label(s):
    s = s.strip(" .,:;-–—|()[]/")
    if len(s) < 3:
        return None
    words = WORD.findall(s)
    if not words:
        return None
    # drop lines that are mostly digits / symbols
    alpha = sum(c.isalpha() for c in s)
    if alpha < 0.5 * len(s.replace(' ', '')):
        return None
    # drop pure reference markers and equation-number fragments
    if re.fullmatch(r'[A-Za-z]{1,2}\d.*', s):
        pass
    return s

def main():
    doc = fitz.open(PDF)
    labels = collections.Counter()
    first_page = {}
    for pno in range(doc.page_count):
        page = doc[pno]
        regions = figure_regions(page)
        if not regions:
            continue
        for b in page.get_text("dict")["blocks"]:
            if b["type"] != 0:
                continue
            for l in b["lines"]:
                if not center_inside(l["bbox"], regions):
                    continue
                txt = clean("".join(sp["text"] for sp in l["spans"]))
                lab = good_label(txt)
                if lab:
                    key = lab
                    labels[key] += 1
                    first_page.setdefault(key, pno + 1)
    # rank by frequency then alphabetically
    items = sorted(labels.items(), key=lambda kv: (-kv[1], kv[0].lower()))
    out = [{"de": k, "n": n, "page": first_page[k]} for k, n in items]
    with open(os.path.join(os.path.dirname(__file__), "figure_labels.json"),
              "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"unique figure labels: {len(out)} (total occurrences {sum(labels.values())})")
    print("--- top 60 ---")
    for d in out[:60]:
        print(f"  {d['n']:3d}  p{d['page']:<3} {d['de']}")

if __name__ == "__main__":
    main()
