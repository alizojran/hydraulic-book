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
FIGPAGE = {"6.1": 214, "6.2": 216, "6.3": 217, "6.4": 219, "6.5": 221, "6.6": 223,
           "6.7": 225, "6.8": 225, "6.9": 227, "6.10": 229, "6.11": 230, "6.12": 230,
           "6.13": 231, "6.14": 232, "6.15": 233, "6.16": 234}
MANUAL  = {"6.1": (214, 65, 309, 388, 399), "6.6": (223, 65, 80, 388, 230),
           "6.9": (227, 65, 125, 388, 298), "6.12": (230, 65, 375, 388, 478),
           "6.13": (231, 65, 510, 388, 607), "6.16": (234, 65, 425, 388, 495)}
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
 "6.5": ("引入切换积分器", "Inclusion of a switching integrator", 8),
 "6.6": ("HSS 的线性观测器型状态反馈控制", "Linear observer-based state feedback control for HSSs", 12.5),
 "6.7": ("良好稳定域的定义", "Definition of nice stability region", 10),
 "6.8": ("HSS 状态反馈的典型极点配置", "Typical pole constellations for state feedback of HSSs", 12.5),
 "6.9": ("含增广积分作用的线性观测器型状态反馈控制（PI 状态控制器）", "Linear observer-based state feedback control with augmented integral action (PI state controller)", 13),
 "6.10": ("用于扰动补偿的前馈控制原理", "Principle of feedforward control for disturbance compensation", 11),
 "6.11": ("通用前馈控制方案", "Universal feedforward control scheme", 11),
 "6.12": ("位置反馈控制与负载压力前馈控制相结合", "Position feedback control combined with load pressure feedforward control", 11),
 "6.13": ("位置反馈控制与速度前馈控制相结合", "Position feedback control combined with velocity feedforward control", 11),
 "6.14": ("基于灰箱模型的自适应状态反馈控制方案", "Adaptive state feedback control scheme based on grey-box models", 12.5),
 "6.15": ("加入偏置校正", "Addition of an offset correction", 8.5),
 "6.16": ("阀曲线及其补偿曲线（Nissing, 2002）", "Valve curve and its compensation curve (Nissing, 2002)", 12),
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

b.h3("6.2.3　位置反馈", "Position Feedback")
b.para("接下来，为实现位置跟踪行为，施加对位置 xp 的反馈。该反馈主要把原点处的极点移入左半"
       "平面，并对共轭复极点对的位置有一定影响（其阻尼首先由压力反馈调整）。位置控制有许多"
       "选择，如简单的 P 控制。为同时提供稳定性和足够阻尼，位置反馈增益 Kp 应选得满足所谓的 "
       "M=1.3 准则（Viersma, 1980）：即闭环幅值（比）绝不超过 1.3（称为频率响应谐振峰）。遵守"
       "该准则，闭环阶跃响应通常显示约 23% 的超调（对二阶系统精确成立）。按良好工程实践，"
       "M=1.3 准则导致约为 2 的幅值裕度和约 45° 的相位裕度（PM）。注意，二阶系统的相位裕度与"
       "阻尼比的关系为 D ≈ PM/100（Franklin 等, 1990）。")
b.para("还要注意，若使用 PT1 控制器（一阶滞后），即")
eq("6.17")
b.para("或 PPT1 控制器，即", indent=False)
eq("6.18")
b.para("则可获得更快的闭环阶跃响应。常规线性控制器对位置控制、速度控制和力控制的适用性概览"
       "见表 6.2（另见 Anderson, 1988）。对某些液压伺服系统应用，可使用 PI 控制器以提高低频"
       "开环增益并减小稳态负载误差及“加速度”误差（Viersma, 1980）；然而须仔细考虑积分时间"
       "常数，因为此时闭环传递函数含双重积分器，会引起稳定性问题。", indent=False)
b.label("表 6.2　线性控制器在位置/速度/力控制上的性能概览（从 −− 最差 到 ++ 最佳）")
_t62 = doc[pidx(221)].get_pixmap(dpi=200, clip=fitz.Rect(65, 113, 388, 211))
_t62.save("ch6_figs/table_6.2.png")
b.image_block("ch6_figs/table_6.2.png", 15.5)
b.para("一种实用的折中是使用切换积分器（switching integrator），它只在控制器输入零点附近的区间 "
       "[eu, eo] 内被激活；见图 6.5。")
fig("6.5")
b.h3("6.2.4　小结", "Summary")
b.para("反馈增益 Kp 和 KpL 的选择分两步进行：")
b.para("1.　整定压差反馈增益 KpL，使所得闭环系统（位置反馈仍为零）的阻尼比 Dh 处于区间 "
       "0.5 < Dh < 0.7 内的某处，视实际应用和期望系统特性而定。", indent=False)
b.para("2.　此后增大位置反馈增益 Kp 以获得位置跟踪，例如直到满足所谓的 M=1.3 准则（Viersma, "
       "1980）。另一良好做法是选择比例增益，使受控系统的频率 ωh,cl 处于区间 1.3 ωh,open < ωh,cl < "
       "1.7 ωh,open 内。", indent=False)
b.para("这里强调，该控制策略的主要重点是位置控制（只有位置参考 xref 可用），压差反馈只用于"
       "修改闭环动态（阻尼）。压力反馈增益不应太大，否则会导致带宽受限的过阻尼系统。若可用，"
       "加速度反馈更可取，因为它在改善阻尼的同时不恶化对力扰动的刚度。注意，按上述洞见，对"
       "性能合理的 HSS 整定控制器是一项直截了当的任务，无需如实践中通常那样的特定参数化模型；"
       "然而，用该方法不可能任意配置极点以得到 HSS 某种所要求的受控行为。")
b.h2("6.3　基于估计器的状态反馈控制", "Estimator-based State Feedback Control")
b.para("控制理论中众所周知，通过全状态反馈可任意配置系统的所有极点以迫使系统呈现期望行为。"
       "因此，在前一小节的位置控制方案中加入速度反馈和压力（或压差）反馈，便可把液压伺服系统"
       "的闭环极点配置到期望位置。该方法已成功用于不同应用（von Wierschem, 1981；Feuser, "
       "1984；Kockemann 等, 1991）。状态空间设计方法的一个吸引人之处是其步骤如下：")
b.para("1.　在所有状态向量元素可用、且系统暂无参考信号（yref=0）的假设下设计控制律。", indent=False)
b.para("2.　设计一个估计器（也称观测器），当提供某些状态的测量时，它估计整个（或部分）状态"
       "向量。", indent=False)
b.para("3.　把控制律与估计器结合，其中控制律计算基于估计状态而非实际状态。", indent=False)
b.para("4.　加入预滤波器或积分器，以消除比例状态控制器情形下的稳态误差，或抑制作用于系统的"
       "未知扰动效应。", indent=False)
b.para("图 6.6 展示了对 HSS（考虑线性化模型式 4.234），控制律与估计器如何配合。")
fig("6.6")
b.h3("6.3.1　状态控制律的计算", "Computation of the State Control Law")
b.para("考虑如下形式的线性时不变（LTI）状态方程：")
eq("6.19")
b.para("确定这类系统状态反馈律有两种常见可能：极点配置法和最优控制法。后者也即著名的线性二次"
       "调节器（LQR）设计法。", indent=False)
b.label("6.3.1.1　极点配置（Pole Assignment）")
b.para("第一步是暂时假设 yref=0 并寻找如下形式的简单反馈律")
eq("6.20")
b.para("把控制律式 6.20 代入式 6.19，得", indent=False)
eq("6.21")
b.para("于是闭环系统的特征方程为", indent=False)
eq("6.22")
b.para("控制律设计就是选取增益向量 k，使式 6.22 的根处于期望位置，即 s = s1, s2, …, sn，使", indent=False)
eq("6.23")
b.para("因此，k 的所需元素通过匹配式 6.22 和 6.23 的系数确定。当且仅当系统（完全）可控（即"
       "可控性矩阵", indent=False)
eq("6.24")
b.para("满秩 n）时，用状态反馈把系统极点移到任何期望位置才是可能的。求解反馈增益的另一方法是"
       "使用 Ackermann 公式（Ackermann, 1972）", indent=False)
eq("6.25")
b.para("其中 C(F) 定义为", indent=False)
eq("6.26")
b.para("ai 是期望特征多项式（式 6.23）的系数。", indent=False)
b.label("6.3.1.2　最优控制（Optimal Control）")
b.para("时间连续 LTI 系统（式 6.19）的线性二次调节器设计（LQR）计算最优增益向量 k，使状态反馈"
       "律（式 6.20）最小化代价函数")
eq("6.27")
b.para("其中 Q 为适当选择的半定矩阵，R 为正定矩阵（因考虑 SISO 系统，R 在此为标量）。最优增益"
       "向量 k 由下式给出", indent=False)
eq("6.28")
b.para("其中 S 是代数 Riccati 矩阵方程的解", indent=False)
eq("6.29")
b.para("设计参数是矩阵 Q 和 R。Q 通常取为对角，常设为单位矩阵；R 用于惩罚控制作用。改变加权"
       "矩阵元素间的相对大小意味着恢复速度与控制信号幅值之间的权衡。寻找相对权重的过程很难，"
       "通常通过试错完成。", indent=False)
b.h3("6.3.2　极点位置的选择", "Selection of Pole Locations")
b.para("状态反馈增益的设计通常用标准设计方法（如上述极点配置）进行，由此可把极点配置成任意"
       "模式以塑造 HSS 的闭环动态，其主要重点是快速跟踪位置参考信号。一般推荐把极点配置在"
       "“良好稳定”区域内，该区域由以下边界包围（见图 6.7）：")
b.bullet("稳定边界（虚轴）减去安全裕度 ε > 0。")
b.bullet("两条恒定最小阻尼 Dmin = cos φmin 的直线。")
b.bullet("距稳定边界的最大距离 E > 0，以限制控制作用并抑制测量噪声。")
fig("6.7")
b.para("通常，闭环极点选为一对期望的主导二阶极点，其余极点选得其实部对应于足够阻尼的模态，"
       "使闭环系统以合理的控制代价模拟二阶系统（Franklin 等, 1986）。液压系统推荐的极点配置"
       "（这里针对式 4.250 或 4.252 中 n=3 的降阶线性模型）为：")
b.para("(a) 所有极点配置在实轴上同一位置（二项式形式）；见图 6.8a。闭环系统将显示最大阻尼 "
       "D=1，即无超调（所谓非周期情形）。", indent=False)
b.para("(b) 所有极点有相同实部，其中两个构成夹角 45° 的复极点对；见图 6.8b。二阶极点选得阻尼比 "
       "D=cos(45°)≈0.7，第三个极点有相同实部。", indent=False)
b.para("(c) 极点位于一个圆上；见图 6.8c。二阶极点如 (b) 选取，带实部的极点稍向左移，使闭环动态"
       "相应更快。", indent=False)
fig("6.8")
b.h3("6.3.3　稳态误差的消除", "Elimination of Steady-state Errors")
b.para("若系统是 1 型（积分型）或更高型（如位置控制的 HSS）且 yref 是阶跃，则无稳态误差，即 "
       "y(∞) = yss = yref,ss。对 0 型（比例型）系统（如速度、压力或力控制的 HSS），会有误差，因为"
       "维持系统于期望状态需要一定控制。为解决该问题，有两种常见方案：为参考信号设计预滤波器，"
       "或引入积分作用。")
b.label("6.3.3.1　预滤波器的设计（Design of Pre-filter）")
b.para("可设计预滤波器")
eq("6.30")
b.para("以消除稳态误差，即确保稳态值 y∞ 与 yref,∞ 相等。总控制律则为", indent=False)
eq("6.31")
b.para("于是得到闭环系统的状态空间描述（以 yref 为输入）", indent=False)
eq("6.32")
b.label("6.3.3.2　状态扩展的积分控制（“PI 状态反馈控制”）")
b.para("该方法的原理是用一个“人工”积分器扩展模型式 6.19，从而给现有输出添加一个积分输出。"
       "即用 xI 增广状态向量 x，xI 满足微分方程")
eq("6.33")
b.para("因此得到扩展系统模型", indent=False)
eq("6.34")
b.para("PI 状态控制律为", indent=False)
eq("6.35")
b.para("这将得到图 6.9 所示的控制结构。有了系统的这一扩展定义，6.3.1 节已给出的设计技术（极点"
       "配置和最优控制）可以类似方式用于确定 k（从而确定 kI 和 k1）。由于 kp 应选为（Föllinger, "
       "1990）", indent=False)
eq("6.36")
b.para("k 的计算便直截了当", indent=False)
eq("6.37")
b.para("PI 状态控制器能抑制作用于系统的未知扰动效应（如通过参数变化）。注意，观测器（或估计器）"
       "设计必须基于扩展模型式 6.34。", indent=False)
fig("6.9")
b.h3("6.3.4　对液压伺服系统线性模型的应用", "Application to HSS Linear Models")
b.para("形式上，状态反馈控制器可基于线性模型式 4.234 设计。然而这会比基于简化模型式 4.250"
       "（忽略阀动态）的控制器设计复杂得多。此时反馈律取如下形式")
eq("6.38")
b.para("给出闭环的系统矩阵（式 6.21）", indent=False)
eq("6.39")
b.para("应用式 6.22 和 6.23 导出控制器增益", indent=False)
eq("6.40", "6.41", "6.42")
b.para("如前，系数 αi 与具体应用中期望的极点位置相关。", indent=False)
b.h2("6.4　线性反馈控制的扩展", "Extensions to Linear Feedback Control")
b.para("迄今论述的控制器都基于线性反馈原理。一方面，使用反馈的主要目的是镇定不稳定系统并减小"
       "可能的扰动和模型不准确性的影响；然而，用反馈快速跟踪参考通常有一个副作用：控制器对"
       "噪声（实践中不可避免）变得高度敏感。另一方面，线性控制设计无法确保闭环系统在整个运行"
       "范围内有相同的动态行为。因此，线性反馈控制应与其他技术结合以在实践中取得满意结果。"
       "对迄今给出的（线性）反馈控制方法有若干（非线性）扩展，如应用前馈控制、增益调度或自适应"
       "方法，以及对特定非线性的补偿。")
b.h3("6.4.1　反馈与前馈相结合的控制", "Combined Feedback and Feedforward Control")
b.para("前馈控制是一种消除可测量扰动的控制方法。其基本思想是利用测得的扰动来预测扰动对过程"
       "变量的影响并提供合适的补偿作用。该方法的通用原理示于图 6.10。与反馈控制相比，前馈控制"
       "的优点是可在扰动影响变量之前施加校正作用，因此前馈控制允许在不影响系统稳定性的情况下"
       "快速跟踪参考。")
fig("6.10")
b.para("考虑分别把输出 y 与扰动 z 和控制 u 联系起来的传递函数 Gz(s) 和 Gu(s)（见 4.4.4.4 节）。"
       "扰动的“完美”抵消通过下式获得")
eq("6.43")
b.para("前提是能获得并物理实现逆 Gu⁻¹(s)。这当然可能不成立，如由于测量扰动先于其出现于过程而"
       "产生的时延；此时须改用合适的近似。假设对象和控制器稳定且所有扰动已知，前馈控制方案可"
       "扩展以产生“完美”控制：", indent=False)
eq("6.44")
b.para("由此给出", indent=False)
eq("6.45")
b.para("遗憾的是，Gu(s) 和 Gz(s) 绝非精确模型，扰动也绝非精确已知。此外常遇到高幅值的非常活跃"
       "的控制信号（若不滤波）。因此，尽管前馈控制能对扰动采取某些预见性作用，但它本身不能"
       "保证良好的控制质量，须与反馈控制结合以减小模型和（扰动）信号不确定性的影响，如图 6.11 "
       "所示。", indent=False)
fig("6.11")
b.label("6.4.1.1　压差前馈控制（Pressure-difference Feedforward Control）")
b.para("若压差参考可用，可把它前馈到压差反馈回路，如图 6.12 所示。压差前馈增益可计算为式 4.258 "
       "传递函数静态增益的倒数：")
eq("6.46")
fig("6.12")
b.para("由于同时提供位置参考 xref 和压差参考 PL,ref，反馈控制设计具有位置控制与压力控制之间权衡"
       "的性质。尤其当用于生成 PL 参考的模型知识相当准确时，可在此权衡中强调压力控制，从而增大"
       "压力反馈增益、代价是较小的位置反馈增益。PL 参考前馈的一个额外优点是：只要 Fext 的估计"
       "可用，它就允许补偿外力（见 6.10.1.3 节）。")
b.label("6.4.1.2　速度前馈控制（Velocity Feedforward Control）")
b.para("从位置伺服控制的角度考虑液压执行器的模型结构（图 4.26）可见，在单位反馈下，恒速的位置"
       "参考只能以恒定跟踪误差被跟踪（所谓 1 型系统）。从物理上看，恒速运动需要恒定的阀流量，"
       "这意味着反馈控制情形下的恒定跟踪误差（van Schothorst, 1997）。避免该跟踪误差的一个显然"
       "方法是应用速度前馈（当然只在速度参考 ẋref 可用时才可能）；见图 6.13。速度前馈增益 Kx,ff "
       "的设计直截了当，应选为式 4.255 传递函数静态增益的倒数：")
eq("6.47")
b.para("忽略摩擦项（即 σ=0），可简化为", indent=False)
eq("6.48")
fig("6.13")
b.para("速度前馈的一个重要副产品是：补偿活塞速度对质量平衡的影响，使压力动态与负载动态解耦；"
       "另见 6.6.2 节。")
b.h3("6.4.2　自适应控制", "Adaptive Control")
b.para("如前节所述，控制 HSS 的标准方法依赖于在工作点附近对动态作局部（雅可比）线性化，随后"
       "进行线性控制设计。然而，液压系统的工况和（负载）扰动以未知方式变化（如阀、油和负载"
       "参数可能显著变化，参数还可能因老化而改变）。因此，任何具有恒定反馈增益的常规控制器"
       "设计方法、或不考虑工况和负载扰动变化的现代控制设计方法，都无法获得最优性能，甚至可能"
       "发生不稳定的系统运行。为确保满意性能，当过程在不同工况和不同负载扰动下运行时，必须"
       "反复重新设计控制器参数。这直接引向自适应控制技术的应用，许多作者已为 HSS 提出并明确"
       "应用了它。5.7 节（图 5.22）的在线辨识方案现在可扩展用于自适应控制方案，如图 6.14 所示"
       "（另见 Boes, 1992, 1995）。当然，可用参数化黑箱模型（如 ARX 模型）代替灰箱（线性）"
       "模型（如 Yu and Kuo, 1997）。")
fig("6.14")
b.h3("6.4.3　特殊（静态）非线性的补偿", "Compensation of Special (Static) Non-linearities")
b.para("迄今给出的所有设计方法都未考虑液压驱动中存在的非线性效应，如库仑摩擦、间隙和非线性"
       "阀流特性。下面讨论如何给线性控制器添加某些非线性补偿以改善闭环系统的性能。非线性特性 "
       "αd,c2(x) 可通过在控制信号进入系统之前、在控制回路中植入该非线性的估计逆 αd,c2⁻¹(x) 来补偿。"
       "这假设非线性可由实验确定，或由任何模型或观测器估计。")
b.label("6.4.3.1　非理想阀几何的补偿（Compensation for Non-ideal Valve Geometry）")
b.para("可给控制量添加一个偏置校正项，以补偿死区行为（如因伺服阀的滞环、过遮盖或径向间隙，见 "
       "4.2.1.1 节）并减小稳态误差（图 6.15）。这种校正项的正确值可由反转流量-信号函数 Q(u)"
       "（4.5.1.1 节）通过实验确定；否则可从制造商样本中提取估计。")
fig("6.15")
b.para("特别地，大多数伺服阀有欠遮盖（闭式中位）或过遮盖（开式中位），尽管零遮盖是高度可取的。"
       "为在控制器设计中规避该问题，可使用 Polzer 与 Nissing（2000b）的阀补偿。为此，对静态"
       "情形（xp=0、ṗA=ṗB=0）测量输入电压 u 对应的活塞速度。借助测得的压力，可计算依赖于输入"
       "电压 u 的理论活塞速度。所需关系可由把 pA 和 pB 的压力动态方程 4.198 和 4.199 相减导出：")
eq("6.49")
b.para("它取决于运动方向，因为活塞表面积对正负速度不同。带过遮盖或欠遮盖的阀的典型输入-速度"
       "曲线见图 6.16（左）。为补偿过遮盖（从而确保式 4.198、4.199 和控制器设计有效），建立两"
       "曲线与零遮盖曲线 ẋp,th(u) 之差并用作阀补偿 uc。对给定输入电压 uunc（来自控制器），须添加"
       "额外补偿电压 uc，使理论活塞速度可由总输出达到：", indent=False)
eq("6.50")
fig("6.16")
b.label("6.4.3.2　非线性流特性的补偿（Compensation for Non-linear Flow Characteristic）")
b.para("文献中有这种补偿技术的例子，其中平方根表达式被反转并用于控制。Neumann 等（1991a,b）"
       "给出非线性仿真结果并得出结论：性能有相当大的改善。他们用观测的压差进行补偿，因为实际"
       "压差未被测量。Lierschaft（1993）以及后来的 Heintze 与 van der Weiden（1995）给出了实验"
       "结果，其中非线性补偿……（详见原文）。")

# ---- (more sections appended in subsequent passes: 6.5 ...) ----

os.makedirs("parts", exist_ok=True)
b.save("parts/ch06.docx")
print("Saved parts/ch06.docx (WIP through 6.4)")
