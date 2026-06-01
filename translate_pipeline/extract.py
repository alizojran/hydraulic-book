#!/usr/bin/env python3
"""Extract structured content (headings, paragraphs, captions, figures) from
Servohydraulik.pdf into extracted.json, rendering figure regions to PNG.

Element schema (per page, in reading order):
  {"k": <int id>, "t": "h1|h2|h3|p|cap", "de": "<german text>"}
  {"t": "fig", "img": "images/pNNN_fK.png", "w": <pt width>}
"""
import fitz, json, re, os, sys

OUTDIR = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(os.path.dirname(OUTDIR), "Servohydraulik.pdf")
IMGDIR = os.path.join(OUTDIR, "images")
os.makedirs(IMGDIR, exist_ok=True)

HEADER_Y = 50          # drop text whose top is above this (running header/page no)
ZOOM = 2.0             # figure render scale

NUM_HEAD = re.compile(r'^\d+(\.\d+)+\s+\S')      # 2.2 / 2.2.1 ...
CHAP_HEAD = re.compile(r'^\d+\s+[A-ZÄÖÜ]')        # 1 EINLEITUNG

def rect_union(a, b):
    return fitz.Rect(min(a.x0,b.x0), min(a.y0,b.y0), max(a.x1,b.x1), max(a.y1,b.y1))

def cluster(rects, gap=12.0):
    """Merge rects that overlap or lie within `gap` points of each other."""
    rects = [fitz.Rect(r) for r in rects]
    changed = True
    while changed:
        changed = False
        out = []
        for r in rects:
            hit = None
            for i, o in enumerate(out):
                if (r.x0 <= o.x1+gap and r.x1 >= o.x0-gap and
                    r.y0 <= o.y1+gap and r.y1 >= o.y0-gap):
                    hit = i; break
            if hit is None:
                out.append(fitz.Rect(r))
            else:
                out[hit] = rect_union(out[hit], r)
                changed = True
        rects = out
    return rects

def figure_regions(page):
    """Return list of fitz.Rect figure regions (raster images + vector clusters)."""
    graphics = []
    d = page.get_text("dict")
    for b in d["blocks"]:
        if b["type"] == 1:                      # raster image
            graphics.append(fitz.Rect(b["bbox"]))
    for dr in page.get_drawings():
        r = dr["rect"]
        if r.y1 < HEADER_Y + 2:                 # header rule zone
            continue
        if r.width <= 0 or r.height <= 0:
            continue
        graphics.append(r)
    clusters = cluster(graphics, gap=14.0)
    regions = []
    for c in clusters:
        if c.width >= 40 and c.height >= 24 and c.get_area() >= 2500:
            regions.append(c)
    return regions

def dehyphen(lines):
    """Join lines of a block into one string, removing soft hyphens."""
    out = ""
    for ln in lines:
        ln = ln.rstrip()
        if out and out[-1] == "-" and len(out) >= 2 and out[-2].isalpha() and ln[:1].islower():
            out = out[:-1] + ln.lstrip()
        elif out:
            out = out + " " + ln.lstrip()
        else:
            out = ln
    return out

BULLET = {"\x02": "• ", "\x03": "• ", "\x07": "• ", "\x08": "• ", "": "• ",
          "": "- ", "\x0b": "• "}

def clean(s):
    for k, v in BULLET.items():
        s = s.replace(k, v)
    s = re.sub(r'\.{4,}', ' ', s)     # TOC dot leaders
    s = re.sub(r'_{3,}', ' ', s)      # title-page rules
    s = re.sub(r'[\x00-\x1f\x7f]', ' ', s)  # stray control glyphs (unmapped math)
    return re.sub(r'[ \t]+', ' ', s).strip()

def block_text(b):
    lines = []
    sizes = []
    for l in b["lines"]:
        txt = "".join(sp["text"] for sp in l["spans"])
        if txt.strip():
            lines.append(txt)
            sizes.append(max(sp["size"] for sp in l["spans"]))
    if not lines:
        return None, 0.0
    return dehyphen(lines), (max(sizes) if sizes else 0.0)

def classify(text, size):
    t = text.strip()
    if t.startswith("Bild") or t.startswith("Tabelle"):
        return "cap"
    if size >= 13.5 and CHAP_HEAD.match(t):
        return "h1"
    if 10.8 <= size <= 11.6 and NUM_HEAD.match(t):
        return "h2" if t.count(".") <= 1 else "h3"
    return "p"

WORD = re.compile(r'[A-Za-zÄÖÜäöüß]{3,}')

def is_prose(text):
    """Real German prose vs. scrambled equation/math fragments."""
    t = text.strip()
    if len(t) < 3:
        return False
    # figure/table captions and headings are always prose-like
    if t.startswith(("Bild", "Tabelle")):
        return True
    # only count tokens that carry alphanumeric content (ignore "•", "-", "(" ...)
    tokens = [tok for tok in t.split() if re.search(r'[A-Za-z0-9ÄÖÜäöüß]', tok)]
    if not tokens:
        return False
    wordish = sum(1 for tok in tokens if WORD.search(tok))
    score = wordish / len(tokens)
    # require enough word-like tokens AND a real multi-letter word present
    return wordish >= 1 and (score >= 0.6 or (score >= 0.5 and len(tokens) >= 6))

def inside(bbox, regions, frac=0.6):
    r = fitz.Rect(bbox)
    a = r.get_area()
    if a <= 0:
        return False
    for reg in regions:
        inter = r & reg
        if inter.get_area() >= frac * a:
            return True
    return False

def process(debug_pages=None):
    doc = fitz.open(PDF)
    pages_out = []
    kid = 0
    for pno in range(doc.page_count):
        page = doc[pno]
        regions = figure_regions(page)
        d = page.get_text("dict")
        items = []        # (y0, kind, payload)
        math_rects = []   # bboxes of scrambled equation/math blocks -> render as image
        # text blocks: classify into prose (translate) vs math (render)
        for b in d["blocks"]:
            if b["type"] != 0:
                continue
            if b["bbox"][1] < HEADER_Y:
                continue
            if inside(b["bbox"], regions):
                continue   # text inside a figure -> part of rendered image
            text, size = block_text(b)
            if not text:
                continue
            text = clean(text)
            if not text:
                continue
            if is_prose(text):
                items.append((b["bbox"][1], "txt", (classify(text, size), text)))
            else:
                math_rects.append(fitz.Rect(b["bbox"]))
        # cluster math fragments into renderable equation regions
        for reg in cluster(math_rects, gap=8.0):
            if reg.width >= 28 and reg.height >= 10 and reg.get_area() >= 500:
                regions.append(reg)
        # figures + equation regions, ordered by vertical position
        for fi, reg in enumerate(regions):
            items.append((reg.y0, "fig", (reg, fi)))
        items.sort(key=lambda x: x[0])

        elements = []
        for y0, typ, payload in items:
            if typ == "fig":
                reg, fi = payload
                fname = f"images/p{pno+1:03d}_f{fi}.png"
                if debug_pages is None:
                    pix = page.get_pixmap(clip=reg, matrix=fitz.Matrix(ZOOM, ZOOM))
                    pix.save(os.path.join(OUTDIR, fname))
                elements.append({"t": "fig", "img": fname, "w": round(reg.width, 1)})
            else:
                kind, text = payload
                kid += 1
                elements.append({"k": kid, "t": kind, "de": text})
        pages_out.append({"page": pno + 1, "elements": elements})

        if debug_pages and (pno + 1) in debug_pages:
            print(f"===== PAGE {pno+1}: {len(regions)} figure region(s) =====")
            for e in elements:
                if e["t"] == "fig":
                    print(f"   [FIG {e['img']}  w={e['w']}]")
                else:
                    print(f"   <{e['t']}> {e['de'][:90]!r}")

    if debug_pages is None:
        with open(os.path.join(OUTDIR, "extracted.json"), "w", encoding="utf-8") as f:
            json.dump({"pages": pages_out}, f, ensure_ascii=False, indent=1)
        tot = sum(len(e.get("de","")) for p in pages_out for e in p["elements"])
        ntext = sum(1 for p in pages_out for e in p["elements"] if "de" in e)
        nfig = sum(1 for p in pages_out for e in p["elements"] if e["t"]=="fig")
        print(f"Wrote extracted.json: {len(pages_out)} pages, {ntext} text elements, "
              f"{nfig} figures, {tot} german chars")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        pgs = set(int(x) for x in sys.argv[2:])
        process(debug_pages=pgs)
    else:
        process()
