# -*- coding: utf-8 -*-
"""Toolkit for building the Chinese translation .docx of

    'Analysis, Synthesis and Design of Hydraulic Servosystems and Pipelines'
    Taco J. Viersma, Elsevier, 1980 (Studies in Mechanical Engineering 1)

The source PDF is a scan (no text layer), so equations are re-typeset from
LaTeX and rendered crisply with matplotlib mathtext (no external LaTeX needed);
figures are auto-cropped from the scanned left-hand pages and embedded with a
translated caption.  Visual style (fonts, headings, page) reuses the existing
DocBuilder from hsbook_docx.py for consistency with the other translated book.
"""
import os
import hashlib
import numpy as np
import fitz  # PyMuPDF
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from docx.shared import Pt, Cm
from docx.enum.text import WD_TAB_ALIGNMENT, WD_LINE_SPACING, WD_ALIGN_PARAGRAPH

from hsbook_docx import DocBuilder, crop_region, LATIN, CJK, CJK_BOLD  # noqa: F401

SRC_PDF = "（已压缩）Analysis,Synthesis and Design of Hydraulic Servosystems and Pipelines.pdf"

EQ_DIR = "v_eqs"
FIG_DIR = "v_figs"
EQ_DPI = 300
os.makedirs(EQ_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# matplotlib mathtext styling
matplotlib.rcParams["mathtext.fontset"] = "cm"   # Computer Modern – book-like
matplotlib.rcParams["mathtext.default"] = "it"


def _slug(s):
    keep = "".join(c if c.isalnum() else "_" for c in s)[:40]
    return keep + "_" + hashlib.md5(s.encode("utf-8")).hexdigest()[:6]


def render_eq(latex, out_path, fontsize=13, dpi=EQ_DPI, color="black"):
    """Render a LaTeX math string to a tight, transparent PNG."""
    fig = plt.figure(figsize=(0.1, 0.1))
    fig.text(0.0, 0.0, f"${latex}$", fontsize=fontsize, color=color)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight",
                pad_inches=0.02, transparent=True)
    plt.close(fig)
    return out_path


def autocrop_figure(page_index, out_path, dpi=200, pad_frac=0.012,
                    drop_caption=False):
    """Render a scanned page and crop to the non-white bounding box.

    Keeps the figure together with its original (English) caption unless
    drop_caption is set.  Returns (path, width_cm).
    """
    doc = fitz.open(SRC_PDF)
    page = doc[page_index]
    pm = page.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
    arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
    H, W = arr.shape
    ink = arr < 150
    rmass = ink.sum(axis=1); cmass = ink.sum(axis=0)
    # a "content" line carries real ink but is not a near-solid scanner edge
    rlo, rhi = max(10, 0.012 * W), 0.60 * W
    clo, chi = max(10, 0.012 * H), 0.60 * H
    good_r = np.where((rmass > rlo) & (rmass < rhi))[0]
    good_c = np.where((cmass > clo) & (cmass < chi))[0]
    if len(good_r) == 0 or len(good_c) == 0:
        doc.close()
        return None
    rows, cols = good_r, good_c
    pady = int(pad_frac * pm.height)
    padx = int(pad_frac * pm.width)
    y0 = max(0, rows[0] - pady); y1 = min(pm.height, rows[-1] + pady)
    x0 = max(0, cols[0] - padx); x1 = min(pm.width, cols[-1] + padx)
    sc = dpi / 72.0
    clip = fitz.Rect(x0 / sc, y0 / sc, x1 / sc, y1 / sc)
    page.get_pixmap(dpi=dpi, clip=clip).save(out_path)
    width_cm = (x1 - x0) / dpi * 2.54
    doc.close()
    return out_path, width_cm


class BookBuilder(DocBuilder):
    """DocBuilder + image-rendered equations and scanned-figure embedding."""

    def equation_img(self, latex, number=None, fontsize=13, max_cm=15.5):
        path = os.path.join(EQ_DIR, "eq_" + _slug(number or latex) + ".png")
        render_eq(latex, path, fontsize=fontsize)
        w, _h = Image.open(path).size
        width_cm = min(w / EQ_DPI * 2.54, max_cm)
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        pf.space_before = Pt(6); pf.space_after = Pt(6)
        pf.tab_stops.add_tab_stop(int(self.content_w / 2), WD_TAB_ALIGNMENT.CENTER)
        pf.tab_stops.add_tab_stop(int(self.content_w), WD_TAB_ALIGNMENT.RIGHT)
        self._set_run(p.add_run("\t"))
        p.add_run().add_picture(path, width=Cm(width_cm))
        if number:
            self._set_run(p.add_run("\t(" + number + ")"))
        return p

    def inline_eq(self, p, latex, fontsize=12):
        """Render a small inline equation image into an existing paragraph."""
        path = os.path.join(EQ_DIR, "in_" + _slug(latex) + ".png")
        render_eq(latex, path, fontsize=fontsize)
        w, _h = Image.open(path).size
        run = p.add_run()
        run.add_picture(path, width=Cm(min(w / EQ_DPI * 2.54, 15.0)))
        return run

    def scan_figure(self, page_index, num, cn, en, max_cm=14.5, drop_caption=False):
        """Auto-crop a scanned figure page and embed with bilingual caption."""
        out = os.path.join(FIG_DIR, f"fig_{num.replace('.', '_')}.png")
        res = autocrop_figure(page_index, out, drop_caption=drop_caption)
        if not res:
            return None
        _path, width_cm = res
        self.figure(out, num, cn, en, min(width_cm, max_cm))

    def scan_region(self, page_index, ytop, ybot, xleft, xright, width_cm=12,
                    caption_cn=None, tag=""):
        """Crop an arbitrary fractional region from the scan (matrices, tables)."""
        out = os.path.join(FIG_DIR, f"reg_p{page_index}_{tag}.png")
        crop_region(SRC_PDF, page_index, ytop, ybot, xleft, xright, out, dpi=220)
        self.image_block(out, width_cm, caption_cn)
        return out

    def scan_figure_crop(self, page_index, y0, y1, num, cn, en,
                         x0=0.05, x1=0.97, max_cm=14.5, dpi=220):
        """Crop a fractional sub-region of a scanned page and caption it as a
        numbered figure (use when several figures share one page)."""
        out = os.path.join(FIG_DIR, f"figc_{num.replace('.', '_')}.png")
        crop_region(SRC_PDF, page_index, y0, y1, x0, x1, out, dpi=dpi)
        w, _h = Image.open(out).size
        self.figure(out, num, cn, en, min(w / dpi * 2.54, max_cm))
