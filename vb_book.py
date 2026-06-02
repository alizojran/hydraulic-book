# -*- coding: utf-8 -*-
"""Compose the combined Chinese-translation Word file for
'Analysis, Synthesis and Design of Hydraulic Servosystems and Pipelines'.

Runs each completed per-part builder, then merges parts/*.docx into one master.
Work-in-progress chapters are intentionally excluded until finished.
"""
import os
import subprocess
import sys
from docx import Document
from docxcompose.composer import Composer

os.makedirs("parts", exist_ok=True)

# (builder script, output part) — extend as chapters are completed
PARTS = [
    ("vb_front.py", "parts/front.docx"),
    ("vb_ch1.py", "parts/ch01.docx"),
]

for script, out in PARTS:
    print("Running", script)
    subprocess.run([sys.executable, script], check=True)

master = Document(PARTS[0][1])
comp = Composer(master)
for _script, part in PARTS[1:]:
    comp.append(Document(part))

OUT = "液压伺服系统与管路的分析、综合与设计_中文译本.docx"
comp.save(OUT)
print("Saved combined:", OUT, os.path.getsize(OUT), "bytes")
