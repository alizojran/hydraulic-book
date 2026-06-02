#!/usr/bin/env python3
"""Build the figure-label German->Chinese reference table as a .docx (sorted
two-column table) and a Markdown copy."""
import json, os, re
import docx
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DIR)

def sortkey(s):
    t = s.lower()
    for a, b in [("ä","a"),("ö","o"),("ü","u"),("ß","s"),("ω","z")]:
        t = t.replace(a, b)
    return (0 if re.match(r"[a-z]", t) else 1, t)

def set_cjk(doc):
    for sn in ("Normal", "Title", "Heading 1"):
        try:
            st = doc.styles[sn]
        except KeyError:
            continue
        rpr = st.element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts")
            rpr.append(rf)
        for a in ("w:eastAsia", "w:ascii", "w:hAnsi"):
            rf.set(qn(a), "Microsoft YaHei")

def main():
    data = json.load(open(os.path.join(DIR, "figure_labels_zh.json"), encoding="utf-8"))
    items = sorted(data.items(), key=lambda kv: sortkey(kv[0]))

    doc = docx.Document()
    set_cjk(doc)
    doc.styles["Normal"].font.size = Pt(10.5)

    h = doc.add_paragraph()
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = h.add_run("《伺服液压》图内德文标注 — 中文对照表")
    r.bold = True; r.font.size = Pt(15)

    note = doc.add_paragraph()
    rn = note.add_run("说明：原书图表（液压原理图、坐标轴、图例等）内部的德文标注随图保持原样、未在图中替换为中文。"
                      "下表按德文字母顺序汇总这些标注及其中文含义，供对照阅读；下标缩写（如 ist、soll、max 等）列于表末。")
    rn.font.size = Pt(9); rn.font.color.rgb = RGBColor(0x55,0x55,0x55)

    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for c, txt in zip(hdr, ("德文标注（Deutsch）", "中文含义")):
        p = c.paragraphs[0]; rr = p.add_run(txt); rr.bold = True
    for de, zh in items:
        cells = table.add_row().cells
        cells[0].paragraphs[0].add_run(de)
        cells[1].paragraphs[0].add_run(zh)

    out = os.path.join(ROOT, "Servohydraulik_图内标注对照表.docx")
    doc.save(out)
    print(f"saved {out}  ({len(items)} entries)")

    # markdown copy
    md = ["# 《伺服液压》图内德文标注 — 中文对照表", "",
          "> 原书图表内部的德文标注保持原样未替换；下表按德文字母顺序汇总其中文含义。", "",
          "| 德文标注 | 中文含义 |", "|---|---|"]
    for de, zh in items:
        md.append(f"| {de} | {zh} |")
    with open(os.path.join(DIR, "figure_labels_table.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("saved figure_labels_table.md")

if __name__ == "__main__":
    main()
