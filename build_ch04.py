# -*- coding: utf-8 -*-
"""第 4 章 基于物理的建模 —— 内容构建（WIP，逐节扩充）。
Produces parts/ch04.docx (content-only)."""
import os, re, fitz, hashlib
from hsbook_docx import DocBuilder, extract_equations, SRC_PDF, pidx

CH = 4
PAGES = range(53, 127)

# ---- equations (auto-cropped by label) ----
os.makedirs("ch4_eqs", exist_ok=True)
EQ = {}
for pp in PAGES:
    EQ.update(extract_equations(SRC_PDF, pidx(pp), CH, "ch4_eqs"))

# ---- equations whose labels OCR'd oddly (comma etc.) and were missed -> manual band crop
doc = fitz.open(SRC_PDF)
MANUAL_EQ = {  # label: (page, y0, y1)
    "4.26": (65, 316, 338),
}
def _man_eq(label, page_no, y0, y1, dpi=200):
    page = doc[pidx(page_no)]; words = page.get_text("words")
    left = min(w[0] for w in words); right = max(w[2] for w in words)
    box = fitz.Rect(left-7, y0, right+7, y1)
    path = f"ch4_eqs/eq_{label}.png"; page.get_pixmap(dpi=dpi, clip=box).save(path)
    EQ[label] = (path, box.width/72*2.54)
for lab, (pg, y0, y1) in MANUAL_EQ.items():
    _man_eq(lab, pg, y0, y1)

# ---- figures ----
os.makedirs("ch4_figs", exist_ok=True)
FIGPAGE = {"4.1": 54, "4.2": 54, "4.3": 56, "4.4": 57,
           "4.5": 59, "4.6": 62, "4.7": 63, "4.8": 63, "4.9": 68}
MANUAL  = {"4.3": (56, 92, 444, 408, 533), "4.5": (59, 95, 348, 372, 469),
           "4.6": (62, 78, 150, 375, 568), "4.7": (63, 70, 58, 365, 378),
           "4.8": (63, 65, 415, 405, 540), "4.9": (68, 88, 238, 365, 332)}
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
 "4.4": ("带变量定义的阀-缸组合示意图", "Schematic representation of valve-cylinder combination with variable definitions", 11),
 "4.5": ("零遮盖 4/3（四口/三位）滑阀", "Zero lapped 4/3 (four ports/three switching positions) spool valve", 9),
 "4.6": ("伺服阀的简化框图（临界中位，忽略流动力）", "A simplified block diagram of servo-valves (critical centre, neglected flow forces)", 9),
 "4.7": ("三级伺服阀的结构示意图", "Schematic representation of the three-stage servo-valve", 9.5),
 "4.8": ("三级伺服阀的模型结构", "Model structure of three-stage servo-valves", 13),
 "4.9": ("溢流阀的示意图", "Schematic representation of a pressure-relief valve", 9.5),
}

# ---- build ----
b = DocBuilder()
_lasteq = [None]
def eq(*labels):
    # stacked multi-line equations sometimes share one crop covering the whole
    # group (with all their numbers); skip consecutive identical-content crops.
    for L in labels:
        entry = EQ[L]
        hh = hashlib.md5(open(entry[0], "rb").read()).hexdigest()
        if hh == _lasteq[0]:
            continue
        b.eq_image(entry); _lasteq[0] = hh
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

b.h3("4.1.2　模型复杂度与适用性", "Model Complexity and Applications")
b.para("为深入理解在液压伺服系统行为中起作用的各种物理现象，建模方法从对整个系统进行"
       "广泛的理论建模开始。这些模型基于基本物理定律，如油液体积的质量平衡、运动部件的"
       "运动方程、流体湍流通过小节流孔的方程等（如第 3 章所述）。在理论建模中，所有预期"
       "会影响系统（动态）行为的效应都被纳入。本节内容基于液压伺服技术领域的早期工作"
       "（Merritt, 1967；Kockemann, 1989；Lausch, 1990；Lierschaft, 1993；Pawlik, 1994；"
       "Heintze, 1997；van Schothorst, 1997）。")
fig("4.4")
b.para("这类复杂非线性模型的一个问题是：难以选取模型中涉及的大量物理参数，使之产生"
       "定量有效的仿真结果。尽管许多参数值可以以合理精度先验已知，但大量参数只在某个"
       "范围内已知，有些甚至完全未知。这可能是由于制造公差，或由于制造商出于专有信息"
       "考虑而不提供参数值。")
b.para("这一问题的后果是：理论模型常常无法用于液压伺服系统行为的定量分析。尽管如此，"
       "仿真仍可提供大量定性认识，可用来对液压伺服系统模型进行简化，使之只考虑相关的"
       "动态。此外，仿真结果还提供了必要的洞见，以判断液压伺服系统的哪些非线性是相关的。"
       "于是可导出一个相对简单的液压伺服系统模型，它包含相关的非线性和动态，并为系统"
       "性质的实验参数估计提供良好基础。")
b.para("由于液压伺服系统的模型还要用于控制设计，模型不仅应在定性上正确，而且应在定量"
       "意义上具有预测价值。这意味着模型应准确表示真实系统的动态与非线性行为。若模型的"
       "输入-输出行为与模型参数之间存在清晰的关系，从而可选取或调整参数使模型拟合某个"
       "真实伺服系统的行为，这便是可能的。换言之，应能从实验输入-输出数据中辨识出模型"
       "参数。")
b.para("为此，至少要求模型与真实系统的相关动态同阶，且只把真实系统的主导非线性纳入模型；"
       "换言之，模型不应包含无关的动态和/或非线性。实际上，把“所有”可能在系统行为中起"
       "作用的物理现象都包含进去的理论模型并不满足这些要求——它过于复杂，无法直接用于"
       "辨识和控制设计。因此应当对其简化，如 4.4 节所讨论。")
b.para("然而，为不放弃理论模型的优点，简化应满足：")
b.bullet("保留理论模型所描述的（主导）动态行为；")
b.bullet("不改变模型的物理结构，使与某些物理现象相关的（主导）非线性效应仍可被考虑在内。")

b.h2("4.2　基本模型", "Elementary Models")
b.para("人们已为液压伺服系统或其子系统推导并阐明了若干基于物理的模型。然而，这些模型"
       "散见于不同的出版物中。本节的目的是通过统一、改进并完善该领域以往的研究，汇集"
       "液压伺服系统一些最基本的模型，包括阀、缸、管道和动力源。")

b.h3("4.2.1　阀", "Valves")
b.para("由于阀是一种复杂的器件，其理论建模同样相当复杂。与文献中关于该主题的其他研究"
       "一致（Merritt, 1967；Lin and Akers, 1989, 1991；Lausch, 1990；van Schothorst, 1997），"
       "这里纳入了许多动态与非线性效应，得到一个复杂的非线性模型。")
b.para("事实上，阀中存在的大多数非线性为：")
b.bullet("死区（dead band，对有遮盖的阀）。")
b.bullet("流量方程中的平方根函数。")
b.bullet("饱和（行程、速度、流量的饱和）。")
b.bullet("阀滞环（hysteresis），它源于阀芯与阀体之间的摩擦力没有在整个阀芯行程上均匀分布。")
b.bullet("响应灵敏度（response sensitivity），即为在停止时所沿的同一方向上获得可测量的阀流量"
         "变化所需的电输入信号变化量。")
b.bullet("反向误差（reversal error），即为在停止时所沿方向的相反方向上获得可测量的阀流量"
         "变化所需的电输入信号变化量。")
b.bullet("可重复性（repeatability），即当重复同一输入信号时阀产生相同流量的能力。")
b.bullet("复杂的流致力（flow-induced forces）与摩擦力。")
b.bullet("力矩马达（torque motor）模型中的各种非线性。")

b.label("4.2.1.1　滑阀的压力-流量方程（Pressure-Flow Equations for Spool Valves）")
b.para("流体通过阀口的流动由节流孔方程 3.77 描述，该式计入了压降方向（流动方向），即：")
eq("4.1")
b.para("考虑图 4.5 所示具有理想临界中位的四通滑阀。由该图，流量方程可写为：")
eq("4.2", "4.3")
fig("4.5")
b.para("函数 sg(x) 定义为：")
eq("4.4")
b.para("流动方向由 xv 的符号决定。cvi（i = 1, …, 4）是阀口的流量系数（也称阀常数）；若所有"
       "阀口相同，则它们相等。（再次注意：cv 的数值与量纲必须适配流量方程中所用的阀信号，"
       "见 3.3.3 节。）", indent=False)
b.para("欠遮盖（underlapped）阀对应的流量方程可写为：")
eq("4.5", "4.6")
b.para("式中 xui ≥ 0（i = 1, …, 4）是阀口的欠遮盖量；若所有阀口几何相同，则它们相等。对"
       "过遮盖（overlapped）阀，流量关系可表示为：", indent=False)
eq("4.7", "4.8")
b.para("其中过遮盖量 xoi ≥ 0（i = 1, …, 4）。", indent=False)
b.para("上面给出的所有流量关系也涵盖了任一腔室容积内压力超过系统压力的特殊情形，例如"
       "当带大负载的执行器突然快速换向时。此时执行器将充当泵。")
b.label("径向间隙与泄漏流（Radial Clearance and Leakage Flows）")
b.para("迄今为止我们讨论的是临界中位阀的压力-流量行为。然而，由于几乎不可能制造出精确的"
       "临界中位阀，“实际临界中位阀”具有径向间隙和少量欠遮盖。因此，阀-执行器系统中总是"
       "存在一些额外的泄漏流，它们影响这类阀的性能与行为以及小开度时相应的压力-流量曲线。"
       "因此，精确模型会计入欠遮盖或过遮盖情形下的泄漏流，以及倒圆的边和径向间隙在小阀口"
       "开度时导致层流这一事实（Merritt, 1967；McCloy and Martin, 1980；van Schothorst, 1997）。")
b.para("由于在这一小区域之外理论方程 4.2 和 4.3 拟合得很好，这里不考虑这些效应。然而从"
       "实用角度看，更好的做法是利用实测数据来辨识并补偿这些效应（另见 4.5.5 节和 6.4.3.1 "
       "节），而不是试图从理论上对这些现象建模、从而把更多不确定参数引入模型。")

b.label("4.2.1.2　伺服阀的动态特性（Dynamic Characteristics of Servo-valves）")
b.para("阀的动态行为涉及大量参数。其中许多参数可能只在某个（很宽的）范围内已知，甚至"
       "完全未知。从不同信息来源（制造商样本与图纸、文献、启发式/手动优化）获得的参数集"
       "并不能反映非常真实的（动态）行为（van Schothorst, 1997）。精确的解析描述既耗时又"
       "极难验证，详见 Merritt（1967）、Dahm（1978）以及较近期的 van Schothorst（1997）。"
       "只有当设计工程师关注阀的所有元素对暂态行为的影响时，这种描述才有用。")
b.para("如今，制造商的样本信息通常会针对各种规格和类型的阀提供众所周知的阶跃响应和/或"
       "频率响应。因此，利用这些信息来建立阀的简单近似模型是有用的。")
b.para("对阶跃响应和频率图的考察（见附录 B.2）提示，可用如下形式的二阶模型来近似伺服阀"
       "（Helduser, 1977；Lee, 1977；Kockemann, 1989；Lausch, 1990；Backe, 1992）：")
eq("4.9")
b.para("其中阀位置、速度、加速度以及阀输入信号均相对于最大行程和最大阀电压作了归一化：", indent=False)
eq("4.10", "4.11", "4.12")
b.para("式 4.9 中的参数——阀增益 Kv、固有频率 ωv 和阻尼系数 Dv——可由辨识获得，或通常从"
       "制造商的样本信息中提取（见 4.5.2 节）。参数 fhs 计入了阀滞环和响应灵敏度。", indent=False)
b.para("把式 4.2、4.3 和 4.9 组合起来，即可构成图 4.6 中伺服阀的框图。")
fig("4.6")

b.label("4.2.1.3　多级伺服阀的模型（Model of Multi-stage Servo-valves）")
b.para("参照图 2.4 以及图 4.7 中的示意表示，含主阀芯位置反馈的三级伺服阀模型结构示于"
       "图 4.8。两个阀芯都假设具有临界中位。下面给出的模型大量借鉴自 Hayase 等人"
       "（1993, 2000）和 van Schothorst（1997）。")
fig("4.7")
fig("4.8")
b.para("先导阀的模型（Model of the Pilot-valve）。　先导阀由力矩马达驱动的喷嘴挡板系统和"
       "一个滑阀组成。", indent=False)
b.para("力矩马达动态（Torque Motor Dynamics）。　驱动挡板的电磁力矩马达由电流 I 控制。"
       "该电流由电流放大器产生，它把阀控制输入 u（电压）转换为电流：", indent=False)
eq("4.13")
b.para("式中 Lim 是力矩马达的电感，Rim 是力矩马达的电阻，Kca 是电流放大器增益。", indent=False)
b.para("电枢上产生的总净力矩在理论上描述为：")
eq("4.14")
b.para("式中 μf 表示磁路某一部分的磁导率，Ag 是气隙的横截面积，la 是电枢长度，Mo 是永磁体"
       "的磁动势，N 是线圈匝数，G 是电枢中位时的气隙长度。", indent=False)
b.para("然而，更简单且常用的假设是：在电枢小转角下，电枢力矩与输入电流呈线性关系，即：")
eq("4.15")
b.para("式中 β 称为力矩马达的增益。", indent=False)
b.para("喷嘴挡板动态（Flapper-nozzle Dynamics）。　电枢转动引起的间隙距离变化由电枢端部"
       "位移 xg 表示；通过电枢转动和挡板长度 lf，它与挡板在两喷嘴间的偏转 xf 相关：", indent=False)
eq("4.16")
b.para("由于挡板只在很小的角度（≈0.01 rad）范围内转动，其运动方程可用挡板偏转表示：")
eq("4.17")
b.para("式中 Jf 是挡板-电枢的转动惯量，σf 是挡板的黏性摩擦系数，Kf 是连接挡板与壳体的"
       "挠性管的刚度，Tfl 是流动力引起的力矩，Tfb 表示反馈弹簧力矩（仅在使用机械式阀芯"
       "位置反馈时适用）。", indent=False)
b.para("挡板上流动力引起的合力矩可由如下理论表达式计算：")
eq("4.18")
b.para("喷嘴处的连续性（Continuity in the Nozzles）。　把连续性方程 3.35 应用于阀腔以及"
       "喷嘴与出口节流孔之间的容积，得到：", indent=False)
eq("4.19", "4.20", "4.21")
b.para("其中 Vni（i = 1, 2, 3）是阀腔容积，Ass,pi 和 ẋv,pi 分别是阀芯侧面积和阀芯速度。", indent=False)
b.para("通过进口节流的流量表示为：")
eq("4.22", "4.23")
b.para("式中 Ao 是进口节流孔的面积。喷嘴流量 Qn1 和 Qn2 可由节流孔方程 3.77（湍流）确定：", indent=False)
eq("4.24", "4.25")
b.para("式中 Pni（i = 1, 2, 3）是喷嘴压力，xf 是挡板位移，xf0 是中位时的挡板-喷嘴距离，"
       "dn 是喷嘴直径，αdn 是喷嘴在湍流下的流量系数。通过出口节流孔的喷嘴流量 Qn3（泄漏"
       "流）按下式计算：", indent=False)
eq("4.26")
b.para("式中 An3 是出口节流孔的面积。", indent=False)
b.para("先导阀芯动态（Pilot-spool Dynamics）。　对阀芯所受的力应用牛顿第二定律，得到：", indent=False)
eq("4.27")
b.para("式中 ms,pi 是先导阀芯的质量，Ffr(ẋv,pi) 是与速度相关的摩擦力（为简单起见，例如取 "
       "σf·ẋv,pi），lfb 是反馈弹簧的长度（若存在），Fax 是阀芯上的轴向流动力。后者可按下式"
       "计算：", indent=False)
eq("4.28")
b.para("式中 Asi（i = 1, 2, 3, 4）是阀芯阀口开度面积。射流角 θ 可假设为常数，即 θ ≈ 69°，"
       "由此 cosθ = 0.358。", indent=False)
b.para("位置反馈（Position Feedback）。　若存在阀芯到挡板位置的机械反馈，则作用在挡板上的"
       "相应反馈弹簧力矩可利用反馈弹簧常数 Kfb，与弹簧端部的虚拟变形相关联（van "
       "Schothorst, 1997）：", indent=False)
eq("4.29")
b.para("显然，当阀芯位置反馈不是机械式而是电气式时，反馈弹簧力矩须置零。同时，力矩马达"
       "输入的式 4.13 须修改为：")
eq("4.30")
b.para("式中 Ksp 是反馈增益，包含阀芯位置传感器增益。", indent=False)
b.para("伺服阀流量由下列方程确定（假设零遮盖，忽略泄漏流）：")
eq("4.31", "4.32")
b.para("主级的模型（Model of the Main Stage）。　与先导阀芯类似，主阀芯的动态为：", indent=False)
eq("4.33", "4.34", "4.35")
b.para("由于主阀芯的侧面积相对于阀芯两侧腔室容积较大，且加速度与摩擦力相对于阀芯上的"
       "最大驱动力（即 ps·Ass,pi）通常很小，因此在所关注的频率范围内，主级的压力动态可"
       "忽略。于是，式 4.33–4.35 可简化为两个静态关系：")
eq("4.36", "4.37")
b.para("最后，描述执行器流量的静态关系为：")
eq("4.38", "4.39")
b.para("为使积分器稳定，主阀芯位置 xvm 通过如下形式的电气反馈回路反馈到先导级：")
eq("4.40")
b.para("式中 Kpm 是比例增益，Kdm 是微分增益，uv 是参考信号。模拟式主阀芯位置反馈回路由"
       "制造商在电子线路中实现，并由其设定 Kpm 和 Kdm 的值。事实上，式 4.36 和 4.37 连同"
       "流量方程 4.31 和 4.32 使主阀芯具有非线性积分器的特性。取决于先导阀芯的阀口几何，"
       "主阀芯速度 ẋvm 与先导阀芯位置 xv,pi 呈非线性关系。", indent=False)
b.para("注意，用式 4.36 和 4.37 对主阀芯建模会在非线性仿真模型中引入代数环（algebraic "
       "loops），这可能在仿真时引起问题。读者可参阅 van Schothorst（1997）了解更多细节。")
b.para("简化经验模型（Simplified Empirical Model）。　无论伺服阀多么复杂，通常都可以使用"
       "式 4.9 的简单动态模型，其五个参数（连同流量方程 4.38 和 4.39）由制造商样本和/或"
       "辨识确定（以制造商参数作初值）。然而，简化模型的参数不再具有直接的物理含义，即"
       "不能用来重建伺服阀的任何物理参数。这里可指出：即便对上述复杂得多的伺服阀模型，"
       "物理参数的先验知识也不足以从辨识参数唯一地确定理论模型中的物理参数，如 van "
       "Schothorst（1997）所述。这意味着伺服阀模型与辨识模型之间可能始终存在某种差距。", indent=False)
b.para("然而，由于上述原因这两种模型是分开使用的，所以这一事实并不严重。就控制设计而言，"
       "需要对动态作准确的（且常常可实时的）刻画，这使得简化模型一经验证便很有用。另一"
       "方面，复杂模型提供的洞见可用于系统设计，即在元件设计阶段，此时并不需要精确知道"
       "模型参数。")

b.label("4.2.1.4　压力阀的建模（Modelling of Pressure Valves）")
b.para("迄今为止，我们把伺服阀作为控制液压伺服系统中流量和/或压力的主要元件来讨论"
       "（该分析在很大程度上也适用于比例阀）。然而，在液压动力的产生与利用中，还需要其他"
       "阀来实现辅助功能。例如，压力阀在液压系统中很常用，并具有多种功能（见第 2 章）。"
       "几乎所有液压系统都共有的是溢流阀（pressure-relief valve）。这种阀的示意图示于图 4.9。")
fig("4.9")
b.para("描述阀芯运动的方程为：")
eq("4.41")
b.para("式中 mc 是阀芯质量加上弹簧质量的三分之一，Fc 是摩擦力，x 是阀芯位移，Ks 是弹簧"
       "刚度，Fax 是轴向流动力，Ass 是阀芯侧面积，pc 是被感测压力（在左侧控制腔内），F0 是"
       "弹簧预紧力。", indent=False)
b.para("流入被感测压力腔的流量按如下方式把供油压力 ps 与控制腔压力 pc 及阀芯运动联系起来：")
eq("4.42")
b.para("式中 Vc 是左侧控制腔的容积，αd 是流量系数，Arc 是（通常为固定的）节流器的面积。", indent=False)
b.para("把连续性方程应用于（被控制的）供油压力腔，得到：")
eq("4.43")
b.para("式中 Vt 是被控压力腔的总容积，Qpu 是理想泵流量，QL 是任意负载流量，QLe 是泄漏流"
       "（包含负载泄漏和泵泄漏），Qmo 是通过主节流孔的流量，CL 是泄漏系数，Amo 是主节流孔"
       "的面积。", indent=False)
b.para("式 4.41、4.42 和 4.43 定义了完整的溢流阀系统，可联立求解以分析其动态。由于液压"
       "系统中常使用两级溢流阀，其模型可以类似地推导。")

# ---- (more sections appended in subsequent passes: 4.2.2 ...) ----

os.makedirs("parts", exist_ok=True)
b.save("parts/ch04.docx")
print("Saved parts/ch04.docx (WIP through 4.2.1)")
