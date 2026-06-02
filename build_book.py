# -*- coding: utf-8 -*-
"""Compose the single combined Word file from front matter + chapter parts.

Run the per-part builders first (build_ch01.py, build_ch02.py, ... and
front_matter.py), then merge parts/*.docx into one master document.
"""
import os, glob, subprocess, sys
from docx import Document
from docxcompose.composer import Composer

# (script, output part) — extend as chapters are translated
PARTS = [
    ("front_matter.py", "parts/front.docx"),
    ("build_ch01.py", "parts/ch01.docx"),
    ("build_ch02.py", "parts/ch02.docx"),
]
# auto-include any further chapters that have been built (ch03.docx, ...)
EXTRA = ["build_ch03.py", "build_ch04.py", "build_ch05.py", "build_ch06.py",
         "build_ch07.py", "build_appendix.py", "build_references.py"]
for s in EXTRA:
    if os.path.exists(s):
        out = "parts/" + s.replace("build_", "").replace(".py", ".docx")
        PARTS.append((s, out))

for script, out in PARTS:
    print("Running", script)
    subprocess.run([sys.executable, script], check=True)

master = Document(PARTS[0][1])
comp = Composer(master)
for _, part in PARTS[1:]:
    comp.append(Document(part))

OUT = "液压伺服系统-建模、辨识与控制_中文译本.docx"
comp.save(OUT)
print("Saved combined:", OUT, os.path.getsize(OUT), "bytes")
