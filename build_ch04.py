# -*- coding: utf-8 -*-
"""第 4 章 基于物理的建模 —— 内容构建（WIP，逐节扩充）。
Produces parts/ch04.docx (content-only)."""
import os, re, fitz
from hsbook_docx import DocBuilder, extract_equations, SRC_PDF, pidx

CH = 4
PAGES = range(53, 127)

# ---- equations (auto-cropped by label) ----
os.makedirs("ch4_eqs", exist_ok=True)
EQ = {}
for pp in PAGES:
    EQ.update(extract_equations(SRC_PDF, pidx(pp), CH, "ch4_eqs"))

# ---- figures ----
os.makedirs("ch4_figs", exist_ok=True)
doc = fitz.open(SRC_PDF)
FIGPAGE = {"4.1": 54, "4.2": 54, "4.3": 56, "4.4": 57}
MANUAL  = {"4.3": (56, 92, 444, 408, 533)}           # explicit box (page,x0,y0,x1,y1)
TOPCUT  = {"4.1": 62}                                 # force figure top (trim header)
def _figbox(page, fig):
    words = page.get_text("words")
    left = min(w[0] for w in words); right = max(w[2] for w in words)
    blocks = sorted(page.get_text("blocks"), key=lambda b: b[1])
    caps = {}
    for b in blocks:
        m = re.match(r"\s*Figure\s*(\d+\.\d+)\.", b[4].replace("\n", " "))
        if m: caps.setdefault(m.group(1), b)
    cy0 = caps[fig][1]; top = TOPCUT.get(fig, page.rect.y0 + 34)
    if fig not in TOPCUT:
        for b in blocks:
            if b[3] <= cy0-2 and len(b[4].strip()) > 55 and not re.match(r"\s*Figure\s*\d+\.\d+\.", b[4].replace("\n"," ")):
                if b[1] < page.rect.y0+28: continue
                if b[3] > top: top = b[3]
        for f2, b2 in caps.items():
            if f2 != fig and b2[3] <= cy0-2 and b2[3] > top: top = b2[3]
    return fitz.Rect(left-4, top+3, right+4, cy0-1)
def _crop(fig):
    if fig in MANUAL:
        p,x0,y0,x1,y1 = MANUAL[fig]; box = fitz.Rect(x0,y0,x1,y1); page = doc[pidx(p)]
    else:
        page = doc[pidx(FIGPAGE[fig])]; box = _figbox(page, fig)
    path = f"ch4_figs/fig_{fig}.png"; page.get_pixmap(dpi=200, clip=box).save(path); return path

FIGCAP = {
 "4.1": ("带动力源的阀-缸组合", "Valve-cylinder combination with power supply", 8.5),
 "4.2": ("带动力源的阀-马达组合", "Valve-motor combination with power supply", 8.5),
 "4.3": ("液压伺服系统的子系统及其相互连接", "Subsystems of hydraulic servo-systems with interconnections", 14.5),
 "4.4": ("简化为两个子系统（阀+缸）", "Reduced two-subsystem (valve + cylinder) representation", 8.5),
}

# ---- build ----
b = DocBuilder()
def eq(*labels):
    for L in labels: b.eq_image(EQ[L])
def fig(num):
    cn, en, w = FIGCAP[num]; b.figure(_crop(num), num, cn, en, w)

b.h1("第 4 章　基于物理的建模", "CHAPTER 4  PHYSICALLY BASED MODELLING",
     page_break_before=True)
b.para("本章致力于推导液压伺服系统的物理模型，涵盖液压伺服系统所涉及的最相关的动态与"
       "非线性效应。模型推导基于第 3 章所述的物理基础以及第一性原理（first principles）。"
       "为使模型复杂度尽可能低，必须作出许多假设和简化。")
b.para("首先，4.2 节介绍液压伺服系统的基本非线性模型。4.3 节总结一个典型的总体模型，并将其"
       "表述为状态空间模型。4.4 节提出模型简化并导出线性化模型。最后，4.5 节回顾确定主要"
       "物理模型参数的一些原则。")
b.para("本章的展开部分基于 Merritt（1967）、Saffe（1986）、Lierschaft（1993）、Pawlik（1994）、"
       "Ebner（1995）、Lemmen（1995）、Heintze（1997）、van Schothorst（1997）、Bernzen"
       "（1999a,b）的工作，以及正文中引用的大量论文。")

b.h2("4.1　引言", "Introduction")
b.para("在种类繁多的液压执行器与阀的组合中（见第 2 章），这里考虑图 4.1 所示的阀-缸"
       "（valve-cylinder）配置。它主要由一个比例阀或伺服阀和一个差动缸（differential "
       "cylinder，也称单出杆缸；图 4.1 中仅实线部分）组成，称为 A+αA 配置（Backe, 1992）；"
       "由于结构紧凑，它可能是应用最广泛的阀-执行器组合。")
b.para("作为 α = AB/AA = 1 的特例，同步缸（synchronising cylinder，多称双出杆缸）在图 4.1 中"
       "由虚线和实线共同表示。从建模角度看，几乎任何流量控制的液压伺服系统都可简化为这一"
       "基本的阀-缸配置。")
b.para("注意，阀-（旋转）马达配置的模型推导与阀-缸组合的推导非常相似；见表 4.1 和图 4.2。")
b.label("表 4.1　线性器件与旋转器件之间的类比")
b.table(["线性执行器（缸）", "旋转器件（马达、泵）"],
        [["活塞位置 xp", "角位置 φ"],
         ["活塞面积 A", "马达排量 V/(2π)"],
         ["质量 m", "转动惯量 J"],
         ["腔室容积 VA、VB", "被压缩容积 V0"],
         ["力 F", "转矩 T"]],
        [7.5, 8.5])
fig("4.1")
fig("4.2")

b.h3("4.1.1　子系统的描述", "Characterisation of Subsystems")
b.para("尽管第 2 章已经给出了液压伺服系统的一般性描述，但为了对该系统进行数学建模，这里要"
       "给出更精确的描述，包括系统边界（system boundary）。")
b.para("阀（执行元件）提供的控制输入 u 通常是电压或电流，可视为理想输入信号，即电信号的"
       "输入阻抗无限大。（伺服）阀的控制输入 u 用于控制油液流过阀口。油由动力源单元在假定"
       "恒定的供油压力 pS 下供给，而回油在（较低的）回油压力 pT 下流入油箱。")
b.para("执行器（缸）由活塞分隔的两个油腔组成。流入和流出油腔的油流 QA 和 QB 驱动活塞，从而"
       "分别产生推动执行器负载所需的压力 pA 和 pB。这样，活塞运动（以活塞速度表示）取决于"
       "执行器的负载。实际上，对于具有自由运动体的运动系统，该负载可看作惯性质量 mp 加上"
       "某个外力 Fext（例如可能包含重力）。")
b.para("恒定的阀开度和恒定的阀压降会产生恒定的油流，进而产生恒速的线性运动（平移）。这"
       "解释了液压执行器在输入 u 与输出 y（活塞位置）之间的基本积分行为。由于两腔中的油是"
       "可压缩的，两段油柱相当于两个弹簧。负载通过活塞被夹在这两个“弹簧”之间。这导致了"
       "二阶行为，它总是与液压执行器的积分特性串联出现。")
b.para("为降低所定义系统边界内系统建模的复杂度，区分若干子系统是有益的（图 4.3）：")
b.para("1.　（伺服）阀（4.2.1 节），它根据执行器压力把控制输入转换为油流。尽管该器件被"
       "设计得快速且呈线性输入-输出行为，但其实际行为通常并不理想。由于阀流驱动执行器，"
       "阀的任何非理想行为都会传播到整个伺服系统，因此建模中把阀明确视为一个独立子系统。",
       indent=False)
b.para("2.　包含负载质量的液压执行器（4.2.2 节），以驱动油流 QA、QB 和外力 Fext 为输入，"
       "相应地以执行器压力 pA、pB 和位置 xp 或速度 ẋp 为输出。作为子系统的液压执行器构成"
       "整个液压伺服系统的核心。执行器基座应始终设计得尽可能刚硬，其阻抗（如惯性）应足够"
       "大以避免寄生能量交换；换言之，不应出现基座的寄生运动。一旦在应用中出现寄生运动，"
       "就应意识到系统动态会受到基座阻抗的影响，此时不能假设执行器刚性连接到具有无限阻抗"
       "的基座（见 4.2.3.5 节）。", indent=False)
b.para("3.　阀与执行器之间的一组管道作为第三个子系统（4.2.5 节），它尤其重要，例如当执行器"
       "行程很长时。由于油的可压缩性和惯性，相对较长的管道不能视为静态器件；压力波以有限"
       "速度沿管道传播，并几乎理想地在管道末端反射。由于管道动态，缸侧的压力和流量必须与"
       "阀侧的区分开来。如图 4.3 所示，压力和流量被加了下标：下标 Av 表示管道 A 的阀侧，"
       "Ac 表示缸侧；Bv 和 Bc 分别表示管道 B 的阀侧和缸侧。", indent=False)
b.para("4.　其次，动力源系统与阀之间、以及油箱与阀之间的一组管道作为第四个子系统。当主"
       "管路与蓄能器/阀之间的距离较大时，这尤其重要（4.2.5 节）。在许多把阀放置得非常靠近"
       "缸的液压伺服控制应用中，回油管路（或马达的壳体泄油管路）的动态对液压系统的功能、"
       "尤其是耐久性可能至关重要。", indent=False)
b.para("5.　在大多数液压伺服应用中，动力源单元的设计使系统在一定的运行范围（即油流需求）"
       "内维持恒定的供油压力。一种有效的做法是把液压蓄能器与压力控制的流量泵结合使用"
       "（Viersma, 1980）。特别是对活塞速度有高性能要求的液压伺服系统，应意识到可能达到"
       "运行范围的极限，从而导致压力下降。另一个例子是使用负载敏感（load-sensing）系统，"
       "其中流量和压力水平被同时调节。由此产生的波动可通过把供油压力 pS 和回油压力 pT 建模"
       "为依赖于所输送流量来加以考虑（4.2.4 节）。若假设理想供油（这在实践中并不现实），"
       "则压力 pS 和 pT 是恒定的。", indent=False)
b.para("因此，计入管道动态后，整个液压伺服系统可由其五个子系统表示，其相互连接如图 4.3 "
       "所示。然而，对于管道效应在输入-输出行为中不起作用的低频行为，以及理想供油的情形，"
       "液压伺服系统的模型简化为仅含两个子系统（阀+缸）的模型；见图 4.4。")
fig("4.3")
fig("4.4")

# ---- (more sections appended in subsequent passes: 4.1.2, 4.2 ...) ----

os.makedirs("parts", exist_ok=True)
b.save("parts/ch04.docx")
print("Saved parts/ch04.docx (WIP through 4.1.1)")
