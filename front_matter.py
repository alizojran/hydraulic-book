# -*- coding: utf-8 -*-
"""前置材料：书名页 + 译者说明 + 全书目录（中文）。Produces parts/front.docx."""
import os
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from hsbook_docx import DocBuilder

b = DocBuilder()

# ---- title page ----
b.title("液压伺服系统：建模、辨识与控制",
        "Hydraulic Servo-systems: Modelling, Identification and Control",
        ["作者：Mohieddine Jelali（穆希丁·杰拉利）　·　Andreas Kroll（安德烈亚斯·克罗尔）",
         "Springer-Verlag London Limited, 2003",
         "（Advances in Industrial Control 工业控制进展丛书）",
         "—— 中文译本（中文为主，关键术语中英对照）——"])
b.note_box("译者说明",
    "本文件是 Jelali 与 Kroll 所著《液压伺服系统：建模、辨识与控制》（Springer, 2003）的"
    "中文译本，供学习与技术参考之用。"
    "译文以中文为主，关键专业术语首次出现时附英文原词，便于核对。原书为扫描+OCR 版，"
    "其中的公式与插图直接取自原书并以图片形式嵌入，正文按原书编号引用图、表、公式；"
    "表格则重新录入并翻译。计量单位保留原文写法。文献引用（作者与年份）保留原文。"
    "如译文与原文有出入，应以英文原著为准。")

# ---- table of contents ----
b.doc.add_page_break()
h = b.doc.add_paragraph(); h.alignment = WD_ALIGN_PARAGRAPH.CENTER
b._set_run(h.add_run("目　录"), latin="Arial", cjk="黑体", size=16, bold=True)
b._set_run(h.add_run("　CONTENTS"), latin="Arial", cjk="黑体", size=11,
           color=RGBColor(0x66,0x66,0x66))

def chap(num, cn, en):
    p = b.doc.add_paragraph(); p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(1)
    b._set_run(p.add_run(f"{num}　{cn}"), bold=True, size=12)
    b._set_run(p.add_run(f"  {en}"), size=9, italic=True, color=RGBColor(0x70,0x70,0x70))

def sec(num, cn):
    p = b.doc.add_paragraph(); p.paragraph_format.left_indent = Pt(22)
    p.paragraph_format.space_after = Pt(0)
    b._set_run(p.add_run(f"{num}　{cn}"), size=10.5, color=RGBColor(0x22,0x22,0x22))

TOC = [
 ("符号表", "Notation", []),
 ("第 1 章", "Introduction（引言）", [
    ("1.1", "液压系统的历史回顾与研究动因"), ("1.2", "本书的目标与重点"),
    ("1.3", "各章概要"), ("1.4", "工作背景与文献注记")]),
 ("第 2 章", "General Description of Hydraulic Servo-systems（液压伺服系统总述）", [
    ("2.1", "液压伺服系统的基本结构"), ("2.2", "部件描述"),
    ("2.3", "液压伺服系统的分类"), ("2.4", "测量与控制装置"), ("2.5", "应用示例")]),
 ("第 3 章", "Physical Fundamentals of Hydraulics（液压的物理基础）", [
    ("3.1", "流体的物理性质"), ("3.2", "流体运动的一般方程"),
    ("3.3", "流体流经各种通道"), ("3.4", "阀口（阀芯）作用力"), ("3.5", "电液类比")]),
 ("第 4 章", "Physically Based Modelling（基于物理的建模）", [
    ("4.1", "引言"), ("4.2", "基本模型"), ("4.3", "典型非线性状态空间模型"),
    ("4.4", "阀控系统的结构化与简化模型"), ("4.5", "特定模型参数的确定"),
    ("4.6", "实现与软件工具"), ("4.7", "本章小结")]),
 ("第 5 章", "Experimental Modelling (Identification)（实验建模/辨识）", [
    ("5.1", "引言"), ("5.2", "预辨识过程"), ("5.3", "模型结构概览"),
    ("5.4", "若干非线性模型结构的描述"), ("5.5", "参数估计方法"),
    ("5.6", "优化算法"), ("5.7", "非线性液压系统的灰箱辨识"),
    ("5.8", "模糊辨识"), ("5.9", "基于人工神经网络的辨识"),
    ("5.10", "模型验证与模型结构比较"), ("5.11", "实现与软件工具"), ("5.12", "本章小结")]),
 ("第 6 章", "Hydraulic Control Systems Design（液压控制系统设计）", [
    ("6.1", "引言"), ("6.2", "经典反馈控制设计"), ("6.3", "基于估计器的状态反馈控制"),
    ("6.4", "线性反馈控制的扩展"), ("6.5", "反馈线性化控制"),
    ("6.6", "类似反馈线性化的方法"), ("6.7", "模糊控制"),
    ("6.8", "基于神经网络的控制"), ("6.9", "振动阻尼控制"), ("6.10", "状态估计"),
    ("6.11", "实现与软件工具"), ("6.12", "控制的快速原型工具"), ("6.13", "本章小结")]),
 ("第 7 章", "Case Studies and Experimental Results（案例研究与实验结果）", [
    ("7.1", "同步缸的辨识与控制"), ("7.2", "小型差动缸的建模与控制"),
    ("7.3", "大型差动缸的控制"), ("7.4", "柔性机器人的振动阻尼控制"),
    ("7.5", "混凝土泵的振动阻尼控制")]),
 ("附录 A", "Fluid Power Symbols（流体动力符号）", []),
 ("附录 B", "Data and Catalogue Sheets（数据与产品样本表）", []),
 ("附录 C", "Non-linear Control Background（非线性控制基础）", []),
 ("参考文献", "References", []),
 ("索引", "Index", []),
]
for num, en_or_cn, secs in TOC:
    # for chapters en_or_cn holds "EN（CN）"; for non-chapter rows it's the EN label
    if num.startswith("第"):
        chap(num, en_or_cn.split("（")[1].rstrip("）"), en_or_cn.split("（")[0].strip())
    else:
        chap(num, en_or_cn.split("（")[1].rstrip("）") if "（" in en_or_cn else en_or_cn,
             en_or_cn.split("（")[0].strip() if "（" in en_or_cn else "")
    for sn, scn in secs:
        sec(sn, scn)

os.makedirs("parts", exist_ok=True)
b.save("parts/front.docx")
print("Saved parts/front.docx")
