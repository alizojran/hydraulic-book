# -*- coding: utf-8 -*-
"""第 6 章 液压控制系统设计 —— 内容构建（WIP，逐节扩充）。Produces parts/ch06.docx."""
import os, re, fitz, hashlib, numpy as np
from hsbook_docx import DocBuilder, extract_equations, SRC_PDF, pidx

CH = 6
PAGES = range(212, 289)
os.makedirs("ch6_eqs", exist_ok=True)
doc = fitz.open(SRC_PDF)
EQ = {}
for pp in PAGES:
    EQ.update(extract_equations(SRC_PDF, pidx(pp), CH, "ch6_eqs"))

def _band(page, y0, y1, label, dpi=200, pad=7):
    ws = page.get_text("words"); L = min(w[0] for w in ws); R = max(w[2] for w in ws)
    box = fitz.Rect(L-pad, y0, R+pad, y1)
    path = os.path.join("ch6_eqs", f"eq_{label}.png"); page.get_pixmap(dpi=dpi, clip=box).save(path)
    return (path, box.width/72*2.54)
EXPLICIT_EQ = {"6.100": (250, 232, 256)}   # OCR-invisible label (provisional; refined when reached)
# (only applied if the page actually matches; refined in the 6.5 pass)

# ---- figures ----
os.makedirs("ch6_figs", exist_ok=True)
FIGPAGE = {"6.1": 214, "6.2": 216, "6.3": 217, "6.4": 219}
MANUAL  = {"6.1": (214, 65, 309, 388, 399)}
TOPCUT  = {}
def _figbox(page, fig):
    ws = page.get_text("words"); left = min(w[0] for w in ws); right = max(w[2] for w in ws)
    blocks = sorted(page.get_text("blocks"), key=lambda b: b[1]); caps = {}
    for b in blocks:
        m = re.match(r"\s*Figure\s*(\d+\.\d+)\.", b[4].replace("\n", " "))
        if m: caps.setdefault(m.group(1), b)
    cy0 = caps[fig][1]; top = TOPCUT.get(fig, page.rect.y0 + 40)
    if fig not in TOPCUT:
        for b in blocks:
            if b[3] <= cy0-2 and len(b[4].strip()) > 55 and not re.match(r"\s*Figure\s*\d+\.\d+\.", b[4].replace("\n"," ")):
                if b[1] < page.rect.y0+30: continue
                if b[3] > top: top = b[3]
        for f2, b2 in caps.items():
            if f2 != fig and b2[3] <= cy0-2 and b2[3] > top: top = b2[3]
    return fitz.Rect(left-4, top+3, right+4, cy0-1)
def _crop(fig):
    if fig in MANUAL:
        p, x0, y0, x1, y1 = MANUAL[fig]; box = fitz.Rect(x0, y0, x1, y1); page = doc[pidx(p)]
    else:
        page = doc[pidx(FIGPAGE[fig])]; box = _figbox(page, fig)
    path = f"ch6_figs/fig_{fig}.png"; page.get_pixmap(dpi=200, clip=box).save(path); return path

FIGCAP = {
 "6.1": ("HSS 的一般控制结构", "General control structure for HSSs", 13),
 "6.2": ("带输入扰动 z 的标准闭环框图", "Block diagram of a standard closed loop with input disturbance z", 12),
 "6.3": ("含负载压力反馈回路的位置反馈", "Position feedback including a load pressure feedback loop", 11),
 "6.4": ("含加速度反馈回路的位置反馈", "Position feedback including an acceleration feedback loop", 11),
}

b = DocBuilder()
_lasteq = [None]
def eq(*labels):
    for L in labels:
        entry = EQ[L]
        hh = hashlib.md5(open(entry[0], "rb").read()).hexdigest()
        if hh == _lasteq[0]: continue
        b.eq_image(entry); _lasteq[0] = hh
def fig(num):
    cn, en, w = FIGCAP[num]; b.figure(_crop(num), num, cn, en, w)

b.h1("第 6 章　液压控制系统设计", "CHAPTER 6  HYDRAULIC CONTROL SYSTEMS DESIGN",
     page_break_before=True)
b.para("本章的目的是综述 HSS 的基础与高级控制设计方法，包括理论背景以及对第 4、5 章所导出"
       "精选模型的应用。本章回顾标准控制设计方法的优点与局限，并利用控制理论领域的最新进展"
       "（涉及非线性控制、“经典”控制和智能控制技术，特别是模糊控制）应用于 HSS。每种设计"
       "方法——无论经典还是现代——都有优缺点和长短处。本章论述背后的理念是：设计者需理解"
       "所有这些，才能以最小代价开发出令人满意的设计。然而须指出，本章无法涵盖所有现有线性和"
       "非线性控制策略的每个细节。")

b.h2("6.1　引言", "Introduction")
b.para("与其他工业控制系统类似，液压控制系统的完整设计过程通常包含以下步骤：")
b.para("1.　建模。　由物理方程（白箱建模，见第 4 章）、或用辨识技术由实验数据（黑箱建模，见"
       "第 5 章）、或两种方法的结合（灰箱建模，见第 5 章）确定 HSS 的数学模型。", indent=False)
b.para("2.　输入-输出可控性分析。　考察可期望的（最大）闭环性能，有助于决定初始控制结构。", indent=False)
b.para("3.　控制结构选择。　在此阶段选择待操纵和待测量的变量，以及它们之间应建立的联系。", indent=False)
b.para("4.　控制器设计。　包括把工程设计问题转化为数学设计问题的表述，以及相应控制器的综合。", indent=False)
b.para("5.　控制系统分析。　通过分析和仿真，对照性能指标或设计者经验评估控制系统。", indent=False)
b.para("6.　控制器实现。　在此阶段把控制器算法编码（计算机控制时用软件），注意处理抗积分饱和"
       "（anti-windup）、无扰切换（bump-less transfer）和物理约束等重要问题。", indent=False)
b.para("7.　控制系统调试与整定。　最后使控制器上线，进行现场测试并实施任何所需修改（即控制器"
       "参数的整定与优化），然后认证受控 HSS 完全可运行并满足性能指标。", indent=False)
b.para("本章主要聚焦于步骤 4、5 和 6。对其他步骤感兴趣的读者可参阅 Skogestad 与 Postlethwaite"
       "（1996）和 Åström 与 Wittenmark（1997）的教材。")
b.para("就 HSS 而言，其控制受到相当大的关注，因为它们在运行中以高功率水平提供高性能运动"
       "控制，以及闭环位置、速度和力控制系统。因此 HSS 在许多工业领域有广泛应用，如机床、"
       "机器人、运动模拟器、疲劳试验系统、轧机等。然而，HSS 的动态特性复杂且高度非线性，主要"
       "非线性包括液压油的可压缩性、伺服阀复杂的流动性质以及液压执行器中的摩擦。此外，液压"
       "系统的工况及作用其上的扰动以复杂方式变化（如阀、油和负载参数可能显著变化），且这些"
       "参数因种种原因（如温度相关行为）常常并不精确已知或时变。所有这些性质和事实使控制设计"
       "和整定变得困难。")
b.para("液压伺服系统闭环控制的主要目标是：")
b.bullet("线性化的输入-输出行为，且在整个运行范围内保持一致。")
b.bullet("足够的阻尼，以获得更好的阶跃响应。")
b.bullet("尽可能（在液压系统动态和由未建模动态、参数变化与扰动所施加的鲁棒稳定性要求允许的"
         "范围内）改善控制带宽。")
b.bullet("机械部件的尺寸和流量至少应保持不变。")
b.para("因此，理想控制器应对参数和扰动变化鲁棒，并同时带来最佳性能。然而实践中须视手头应用"
       "权衡取舍。许多工业 HSS 控制器通过增大缸径以提高缸中流体的有效刚度，从而以固定增益"
       "控制律实现高带宽；这需要更大、更昂贵的部件和更高的流量才能以给定速度移动负载。获得"
       "快速响应的更好方法是对系统的主导动态建模，然后在控制器设计中利用这一动态知识——其"
       "优点是：要达到给定带宽，机械部件更小、所需流量更少，因此整个系统便宜得多（Bobrow "
       "and Lum, 1996）。")
b.h3("6.1.1　一般方法", "General Approaches")
b.para("尽管在大多数应用中 HSS 的控制问题可描述为控制活塞运动的问题（液压执行器应施加该运动"
       "所需的力），但可考虑图 6.1 所示的广义控制结构，其中可识别出三个部分（van Schothorst, "
       "1997）：")
b.bullet("轨迹生成。　这一部分（可能由某外部驱动信号 r 馈入）为运动系统生成期望轨迹。在许多"
         "（工业）应用中，轨迹生成器（或预滤波器）只生成系统须跟随的期望位置轨迹 xref；更高级的"
         "轨迹生成器（如机器人操作臂中）还提供可用于前馈部分的期望速度 ẋref 和加速度 ẍref。")
b.bullet("前馈控制。　有了期望轨迹，前馈控制可用于生成供给（反馈）控制系统的信号，使受控运动"
         "系统尽可能好地实现期望轨迹。实际上，最优前馈控制使用系统的理想逆模型，恰好生成实现"
         "期望轨迹的那些控制信号。反馈部分是必不可少的，因为不可能实现运动系统的精确逆模型、"
         "也不可能知道所有扰动。")
b.bullet("反馈控制。　反馈控制可看作校正控制，用以应对前馈通路中的（建模）误差和未知扰动。它"
         "把前馈信号与系统测量输出信号的反馈结合起来。")
fig("6.1")
b.para("轨迹生成器通常只是一个二阶低通滤波器，如由外部参考信号 r(t)（通常是位置参考）驱动、"
       "具有可调截止频率 ωe 的巴特沃思滤波器（见 5.5.3.1 节）：")
eq("6.1")
b.para("借助 ωe，可调整期望位置-速度-加速度轨迹的频率内容。在高频范围，期望加速度与 ωe² 成"
       "正比；因此从物理上看，高截止频率 ωe 意味着对系统的高要求。", indent=False)
b.h3("6.1.2　文献概览与分类", "Literature Scan and Classification")
b.para("在液压执行器控制领域，可找到种类繁多的控制设计技术和应用。要对文献中的控制问题和控制"
       "设计技术作出完整的概览和分类并非易事。一般而言，液压伺服控制问题被处理为：")
b.bullet("位置控制问题（Merritt, 1967；Viersma, 1980；……；Nissing, 2002）。这是液压伺服控制的"
         "标准应用。")
b.bullet("速度控制问题（Anderson, 1988；Backe, 1992；……）。速度控制一般用于旋转驱动应用，但也"
         "常作为速度补偿隐含包含在位置控制方案中。")
b.bullet("力控制问题（Sepehri 等, 1990；Backe, 1992；Boes, 1995；Heintze and van der Weiden, "
         "1995）。这通常见于金属成形机和试验机。")
b.para("尽管不同类型控制问题有这种清晰区分，但很难就用于解决所提控制问题的控制设计技术给出"
       "刻画。实际上，可用计算能力、控制设计者的经验与偏好、可用传感器等实际原因似乎在选择"
       "某种控制设计策略时起重要作用（van Schothorst, 1997）。尽管如此，表 6.1 给出液压伺服控制"
       "文献的一个适度分类和简要综述。")
b.label("表 6.1　HSS 控制技术文献概览")
b.table(["控制技术", "精选文献"],
        [["经典反馈控制", "Merritt (1967), Viersma (1980), Anderson (1988), Backe (1992)"],
         ["状态反馈控制", "von Wierschem (1981), Feuser (1984), Kockemann 等 (1991), Neumann 等 (1991a,b)"],
         ["反馈控制的扩展（前馈控制、非线性补偿）", "McClamroch (1985), de Boer (1992), Lierschaft (1993), Heintze and van der Weiden (1995), Bobrow and Lum (1996), Polzer and Nissing (2000b), van Schothorst (1997)"],
         ["预测控制", "Kotzev 等 (1994), Stahl and Irle (1999)"],
         ["自适应控制（自校正/学习控制）", "Porter and Tatnall (1970), Yun and Cho (1985, 1988, 1991), Saffe (1986), Kockemann 等 (1991), Boes (1992, 1995), Huang and Wang (1995), Bobrow and Lum (1996) 等"],
         ["变结构控制（滑模控制）", "Lee and Lee (1990), Chern and Wu (1992), Hwang and Lan (1994), Behmenburg (1995)"],
         ["反馈线性化（输入-输出线性化）", "Hahn 等 (1994), Del Re and Isidori (1995), Alleyne (1996), Bernzen (1999a), Sohl and Bobrow (1999), Lemmen 等 (2000), Tunay 等 (2001)"],
         ["模糊控制", "Klein (1993), Behmenburg (1995), Boes (1995), Zhao and Virvalo (1995), Berger (1997)"],
         ["神经控制", "Burton 等 (1992), Plummer and Vaughan (1996)"],
         ["双线性控制", "Naujoks and Wurmthaler (1988), Guo and Schwarz (1989), Guo (1991), Yin (1992, 1994), Schwarz 等 (1996)"]],
        [5.5, 10.5])

b.h2("6.2　经典反馈控制设计", "Classical Feedback Control Design")
b.para("控制液压伺服系统的标准方法是应用线性反馈控制设计方法。这些方法的理论背景可见若干"
       "入门控制书籍，如 Franklin 等（1986）、Föllinger（1990）、Unbehauen（1993, 1994）和 Lunze"
       "（2001）；高级主题另参阅 Franklin 等（1990）、Skogestad 与 Postlethwaite（1996）、Åström 与 "
       "Wittenmark（1997）等。本节仅以紧凑方式给出一些精选设计技术。")
b.para("我们从回顾闭环控制原理（已在 2.4.1 节、图 2.12 引入）开始，设 Gp(s) 为待控系统的（线性）"
       "传递函数，Gc(s) 为控制器的传递函数（图 6.2）。则对输入 yref 的闭环传递函数为：")
fig("6.2")
eq("6.2")
b.para("对扰动 z 的传递函数可写为", indent=False)
eq("6.3")
b.para("线性系统允许叠加，即输出 y 是参考和扰动两个输入的共同贡献。包含两个输入的结果为", indent=False)
eq("6.4")
b.para("在大多数液压伺服控制的标准应用中，只有位置参考可用。这类应用的常规控制策略是对执行器"
       "位置进行比例反馈以获得伺服行为，同时多数情况下为阻尼目的引入比例压力反馈回路（Merritt, "
       "1967；Viersma, 1980）；见图 6.3。其目的是在存在扰动 z（负载或外力变化、供油压力变化等）"
       "时，使位置 x(t) 保持接近位置参考 xref(t)。")
fig("6.3")
b.para("为更深入了解这种经典控制器的有效性，考虑 4.4.4.3 和 4.4.4.4 节导出的液压系统线性化模型"
       "（为简单起见忽略阀动态）。由于图 4.26 的模型结构通常表现为一个（阻尼很差，即典型 "
       "Dh = 0.05–0.25 的）二阶系统与一个积分器串联，显然比例位置反馈导致跟踪行为。")
b.h3("6.2.1　压力反馈", "Pressure Feedback")
b.para("首先分析压力反馈回路的效果。应用压力反馈")
eq("6.5")
b.para("导出如下闭环传递函数：", indent=False)
eq("6.6")
b.para("它被化为一个 PT2 与积分器串联的标准形式（见式 4.244）。简单计算给出受控系统的固有频率 "
       "ωh,cl 和阻尼 Dh,cl", indent=False)
eq("6.7", "6.8")
b.para("只要黏性摩擦系数 σ 小（液压系统通常如此），式 6.7 和 6.8 表明压力反馈对固有频率 ωh,cl 仅"
       "有微弱影响。另一方面，压力反馈对阻尼 Dh,cl 有与泄漏项等效的作用。因此，压力控制系统的 "
       "Dh,cl 可用压力反馈轻易调整，而 ωh,cl 变化很小。", indent=False)
b.para("然而，液压执行器对扰动力表现出有限的刚度。由于压力反馈可视为人为引入的泄漏，它会增大"
       "如库仑摩擦或静摩擦对定位精度的扰动效应（Heintze, 1997）。为此，考虑扰动传递函数")
eq("6.9")
b.para("于是负载刚度可确定为", indent=False)
eq("6.10")
b.para("或等价地", indent=False)
eq("6.11")
b.para("由于此式右端第二项小于 1，负载刚度因压力反馈而降低。为避免该问题，应使用如下形式的"
       "压力反馈来代替式 6.5 的控制律：", indent=False)
eq("6.12")
b.para("若再次计算特征参数，可看出这种压力反馈的有效性：", indent=False)
eq("6.13", "6.14", "6.15")
b.para("因此，只有液压系统的阻尼受压力反馈增益 KpL 影响。", indent=False)
b.h3("6.2.2　加速度反馈", "Acceleration Feedback")
b.para("由于加速度与压差密切相关（见式 4.257），液压阻尼 Dh,cl 也可经加速度反馈调整；见图 6.4。"
       "此时可导出")
fig("6.4")
eq("6.16")
b.para("ωh,cl 和 Ch,cl 分别同式 6.13 和 6.15。因此，加速度反馈也不会恶化液压驱动系统的刚度。然而，"
       "测量加速度一般被认为比测量 pL 更复杂、因而更昂贵；故实际应用中常无传感器测量加速度。"
       "尽管如此，加速度可由位置或速度信号微分估计（见 6.10.1.3 节），但由于位置信号有噪声以及"
       "微分引入的相位延迟，所构造的加速度信号质量不会很理想。", indent=False)

# ---- (more sections appended in subsequent passes: 6.3 ...) ----

os.makedirs("parts", exist_ok=True)
b.save("parts/ch06.docx")
print("Saved parts/ch06.docx (WIP through 6.2)")
