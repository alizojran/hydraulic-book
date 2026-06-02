# -*- coding: utf-8 -*-
"""第 3 章 液压物理基础 —— 内容构建（供 build_book.py 合并）。
Produces parts/ch03.docx (content-only)."""
import os, re, fitz, hashlib
from hsbook_docx import DocBuilder, extract_equations, SRC_PDF, pidx

# ----------------------------------------------------------------------------
# 1) auto-extract every numbered equation (3.1 .. 3.102) as cropped images
# ----------------------------------------------------------------------------
os.makedirs("ch3_eqs", exist_ok=True)
EQ = {}
for pp in range(29, 53):
    EQ.update(extract_equations(SRC_PDF, pidx(pp), 3, "ch3_eqs"))

# ----------------------------------------------------------------------------
# 2) crop the 14 figures (prose-paragraph-above heuristic + manual overrides)
# ----------------------------------------------------------------------------
os.makedirs("ch3_figs", exist_ok=True)
doc = fitz.open(SRC_PDF)
FIGPAGE = {"3.1":30,"3.2":33,"3.3":34,"3.4":36,"3.5":37,"3.6":41,"3.7":42,
           "3.8":43,"3.9":43,"3.10":45,"3.11":46,"3.12":47,"3.13":48,"3.14":51}
MANUAL = {"3.1":(30,95,84,366,162), "3.4":(36,48,44,408,236),
          "3.8":(43,68,52,376,192), "3.9":(43,88,298,348,403)}
def _figbox(page, fig):
    words = page.get_text("words")
    left = min(w[0] for w in words); right = max(w[2] for w in words)
    blocks = sorted(page.get_text("blocks"), key=lambda b: b[1])
    caps = {}
    for b in blocks:
        m = re.match(r"\s*Figure\s*(3\.\d+)\.", b[4].replace("\n", " "))
        if m: caps.setdefault(m.group(1), b)
    cy0 = caps[fig][1]; top = page.rect.y0 + 34
    for b in blocks:
        if b[3] <= cy0-2 and len(b[4].strip()) > 55 and not re.match(r"\s*Figure\s*3\.\d+\.", b[4].replace("\n"," ")):
            if b[1] < page.rect.y0+28: continue
            if b[3] > top: top = b[3]
    for f2, b2 in caps.items():
        if f2 != fig and b2[3] <= cy0-2 and b2[3] > top: top = b2[3]
    return fitz.Rect(left-4, top+3, right+4, cy0-1)
for fig, pp in FIGPAGE.items():
    if fig in MANUAL:
        p, x0, y0, x1, y1 = MANUAL[fig]; box = fitz.Rect(x0, y0, x1, y1); page = doc[pidx(p)]
    else:
        page = doc[pidx(pp)]; box = _figbox(page, fig)
    page.get_pixmap(dpi=200, clip=box).save(f"ch3_figs/fig_{fig}.png")

FIGCAP = {
 "3.1": ("库埃特流动；剪应力的定义", "Couette flow; definition of shear stress", 9.5),
 "3.2": ("夹带空气体积对等熵体积模量的影响", "Influence of entrained air volume on the isentropic bulk modulus", 11),
 "3.3": ("等熵体积模量的典型变化曲线（rv = 0.0001）", "Typical trace of isentropic bulk modulus (rv = 0.0001)", 13),
 "3.4": ("计算 E′ 的不同公式之比较", "Comparison of different formulae for the calculation of E'", 12),
 "3.5": ("控制管的定义", "Definition of control tube", 8.5),
 "3.6": ("圆柱形管道内流体微元的力平衡", "Force equilibrium of fluid elements in cylindrical pipelines", 10),
 "3.7": ("圆柱形管道内层流与湍流的速度分布", "Velocity profiles for laminar and turbulent flows in a cylindrical pipeline", 12.5),
 "3.8": ("圆形、缝隙型与短管型节流孔", "Round, slit-type and short tube orifices", 10.5),
 "3.9": ("流体流经节流孔：(a) 层流；(b) 湍流", "Flow through an orifice: (a) laminar flow; (b) turbulent flow", 9.5),
 "3.10": ("短管型节流孔的流量系数 αd（按式 3.64）", "Discharge coefficient αd for short tube orifices according to Equation 3.64", 11),
 "3.11": ("短管型节流孔的流量系数 αd（按式 3.65）", "Discharge coefficient αd for short tube orifices according to Equation 3.65", 11),
 "3.12": ("αd = f(√Re)（据 Viersma, 1980）", "αd = f(√Re) according to Viersma (1980)", 11),
 "3.13": ("因射流角不等而作用于阀芯的轴向流动力", "Axial flow force on spool due to unequal jet angles", 9.5),
 "3.14": ("(a) 电系统与 (b) 液压系统中各变量之间的关系（Beater, 1999）",
          "Relationships between variables in (a) electrical and (b) hydraulic systems (Beater, 1999)", 12.5),
}

# ----------------------------------------------------------------------------
# 3) build chapter content
# ----------------------------------------------------------------------------
b = DocBuilder()
_lasteq = [None]
def eq(*labels):
    for L in labels:
        entry = EQ[L]
        hh = hashlib.md5(open(entry[0], "rb").read()).hexdigest()
        if hh == _lasteq[0]:
            continue
        b.eq_image(entry); _lasteq[0] = hh
def fig(num):
    cn, en, w = FIGCAP[num]; b.figure(f"ch3_figs/fig_{num}.png", num, cn, en, w)

b.h1("第 3 章　液压物理基础", "CHAPTER 3  PHYSICAL FUNDAMENTALS OF HYDRAULICS",
     page_break_before=True)
b.para("本章的目的是定义液压油的某些物理性质，并讨论流体运动的基本定律与方程、流动的"
       "类型，以及流体通过节流孔和阀的流动。应当指出，本章无意给出液压（或流体力学）中"
       "流体运动的完整理论基础；它毋宁是总结后续各章将要用到的那些方程与概念。要了解更多"
       "细节与信息，读者可参阅贯穿全章给出的相应文献。")
b.para("本章的写作在很大程度上受到 Merritt（1967）标准教材中关于流体通过节流孔和阀的详尽"
       "讨论，以及较近期 Beater（1999）出色工作的影响。关于本章材料的分析与讨论，也可见于"
       "如 Findeisen 与 Findeisen（1994）以及 Will 等人（1999）的近期工作。")

b.h2("3.1　流体的物理性质", "Physical Properties of Fluids")
b.para("流体（液体和气体）是没有自身固定形状的物体；它们能够流动，即在力的作用下可以"
       "发生很大的形状变化；作用力越弱，形状变化越缓慢（Lencastre, 1987）。")
b.para("作用在流体表面微元上的法向应力称为压力（pressure）。在给定点处，它在各个方向上"
       "都相同。压力可按下式计算：")
eq("3.1")
b.para("因此其量纲为单位面积上的力（N/m²）。", indent=False)

b.h3("3.1.1　黏度及相关量", "Viscosity and Related Quantities")
b.para("动力黏度系数（dynamic viscosity）η 是表征运动液体中存在切向力的参数。设有相距 dy "
       "的两块平板（或两层流体）以相对速度 dvx 运动（见图 3.1），则会产生剪应力（shear "
       "stress）：")
eq("3.2")
b.para("其中 η 是比例系数，称为动力黏度。", indent=False)
fig("3.1")
b.para("运动黏度系数（kinematic viscosity）ν 是动力黏度与流体密度之比，即：")
eq("3.3")
b.para("液体的动力黏度随温度有相当大的变化：")
eq("3.4")
b.para("式中 η0 是参考温度 θ0 下的动力黏度。黏度-温度系数 λ1 应针对所考虑的流体由实验确定。"
       "对矿物油而言，它介于 0.036 与 0.057 K⁻¹ 之间（Ivantysyn and Ivantysynova, 1993）。", indent=False)
b.para("压力的影响由下式给出：")
eq("3.5")
b.para("式中 α 是依赖于温度的黏度-压力系数；矿物油 HLP 32 的取值见表 3.1。对 HFC 液与 HFD 液，"
       "可分别取 α = 0.35 Pa⁻¹ 和 α = 2.2 Pa⁻¹（Ivantysyn and Ivantysynova, 1993）。压力对黏度的"
       "影响在实践中并不那么重要。", indent=False)
b.label("表 3.1　矿物油 HLP 32 的黏度-压力系数（Ivantysyn and Ivantysynova, 1993）")
b.table(["θ [°C]", "α [10⁻² Pa⁻¹]", "θ [°C]", "α [10⁻² Pa⁻¹]"],
        [["0","3.268","60","1.770"],["10","2.900","70","1.626"],
         ["20","2.595","80","1.499"],["30","2.339","90","1.385"],
         ["40","2.121","100","1.283"],["50","1.933","",""]],
        [3,4,3,4])

b.h3("3.1.2　质量密度、体积模量及相关量", "Mass Density, Bulk Modulus and Related Quantities")
b.para("质量密度（mass density）ρ，或简称密度，是单位体积内所含的质量：")
eq("3.6")
b.para("液压油的密度通常介于 0.85 与 0.91 kg/dm³ 之间。实际上，液压油的密度是压力和温度的"
       "函数，即 ρ = ρ(p, θ)。可用二元泰勒级数的前三项作近似（Merritt, 1967）：", indent=False)
eq("3.7")
b.para("式中 ρ、p、θ 分别为流体在初始值 ρ0、p0、θ0 附近的质量密度、压力和温度。式 3.7 是流体的"
       "线性化状态方程。在液压现象中，通常假设温度恒定，从而把线性化状态方程 3.7 简化为简单"
       "形式（Merritt, 1967）：", indent=False)
eq("3.8")
b.para("式中 ρi 是零压力下的质量密度。下述量", indent=False)
eq("3.9")
b.para("是压力变化除以恒温下体积的相对变化。它称为弹性模量（modulus of elasticity），也称为"
       "等温体积模量（isothermal bulk modulus）或简称液体的体积模量（bulk modulus）。它显著"
       "影响液压伺服系统的动态特性。对矿物油，在常见压力与温度下（θ ∈ [−40, 120] °C，"
       "p ≤ 450 bar），可取体积模量的平均值，典型地：", indent=False)
eq("3.10")
b.para("然而从实用角度看，这只是非常粗略的近似，因为体积模量随压力有相当大的变化，例如"
       "按下式：", indent=False)
eq("3.11")
b.para("典型值为 E = 16500 bar、Kp = 9.558。温度的影响可忽略。下述量", indent=False)
eq("3.12")
b.para("是恒压下因温度变化引起的体积相对变化。它称为液体的体膨胀系数（cubical expansion "
       "coefficient）。", indent=False)
b.para("文献中有许多计算液压油密度随温度和压力变化的公式。例如，在大气压（1 bar = 10⁵ N/m²）"
       "和可变温度 θ 下，密度由下式给出：")
eq("3.13")
b.para("式中 ρ0 是参考温度 θ0（如 15 °C）下的密度，β0 表示热膨胀因子，例如矿物油为 "
       "0.65×10⁻³ K⁻¹，HFC 液为 0.7×10⁻³ K⁻¹，HFD 液为 0.75×10⁻³ K⁻¹（Matthies, 1995）。"
       "压力变化后液压油的密度可表示为：", indent=False)
eq("3.14")
b.para("式中 Kp 是压缩因子（compressibility factor）：", indent=False)
eq("3.15")
b.para("对可变温度和可变压力，密度可按下式计算：")
eq("3.16")
b.para("κp 的典型值为：矿物油 0.7×10⁻⁴ bar⁻¹，HFC 液 0.3×10⁻⁴ bar⁻¹，HFD 液 0.35×10⁻⁴ bar⁻¹"
       "（Matthies, 1995）。由这些数值可知，压力对流体密度的影响很小，实践中可忽略。", indent=False)

b.h3("3.1.3　有效体积模量", "Effective Bulk Modulus")
b.para("液体的体积模量会因夹带气体（entrained gas）和机械柔度（mechanical compliance）而显著"
       "降低。据 Merritt（1967），液压系统中被夹带空气的估计量在流体处于大气压时高达 20%。"
       "随着压力升高，其中大部分空气溶入液体，不再影响体积模量。机械柔度的主要来源可能是"
       "连接阀、泵与执行器的液压管路。")
b.label("3.1.3.1　夹带空气的影响（Influence of Entrained Air）")
b.para("已有一些工作用于确定液-气混合物以及因机械柔度而产生的容器的体积模量。Backe 与 "
       "Murrenhoff（1994:103）提出了如下液-气混合物等熵体积模量的公式（另见 Beater, 1999:26）：")
eq("3.17")
b.para("式中 rv = VGO/VLO；E′isen 为液体（不含夹带空气）的等熵体积模量；VGO 为大气压下液体中"
       "夹带气体的体积；VLO 为大气压下液体的体积；p0 为大气压（p0 = 1 bar）；p 为液体压力；"
       "κ 为等熵指数（κ = 1.4）。", indent=False)
b.para("图 3.2 给出了对若干体积比 rv 值，比值 E′isen(p)/E′isen 的曲线。图 3.3 中绘出了体积模量"
       "随压力的具体依赖关系。")
fig("3.2")
fig("3.3")
b.para("尤其在低压区（如 p ≤ 100 bar），夹带气体对体积模量的影响相当大。在约 0.6 bar 的压力下，"
       "夹带空气可能发生爆燃（即所谓柴油效应，Diesel effect）。这种效应会造成极不希望的侵蚀"
       "缺陷、功率损失、压力峰值和噪声。这种现象更广为人知的名称是空化（cavitation，当流体"
       "压力降到蒸气压以下时气泡突然溃灭）（Lemmen, 2002）。")
b.para("注意，上面给出的表达式需要准确确定许多量（例如液体中夹带气体的体积），因此在实践中"
       "可能难以使用。")
b.label("3.1.3.2　机械柔度的影响（Influence of Mechanical Compliance）")
b.para("圆柱形管道的体积模量可按下式计算（Theißen, 1983）：")
eq("3.18")
b.para("式中 Ep 是（钢）管道的体积模量。对厚壁管道，系数 w 由下式给出：", indent=False)
eq("3.19")
b.para("其中 do 为外径，di 为内径，ν 为泊松数（Poisson's number），钢取 ν = 0.3。", indent=False)
b.para("对壁厚为 s 的薄壁管道（s/do < 0.1），式 3.19 近似为：")
eq("3.20")
b.para("表 3.2 给出了一些实验结果。可以看出，特别是对以交织金属丝增强的高压橡胶软管，弹性"
       "的影响相当可观。", indent=False)
b.label("表 3.2　体积模量 E′ 的取值（Viersma, 1980）")
b.table(["公称压力 [MPa]", "钢管 E′ [MPa]（Ri=6.25, Ro=8 mm）", "高压软管 E′ [MPa]（Ri=6.25 mm）"],
        [["5","1460","500"],["9","1510","537"],["13","1570","568"],["22.5","1890","—"]],
        [4,6.5,6])
b.label("3.1.3.3　经验有效体积模量（Empirical Effective Bulk Modulus）")
b.para("其他研究者基于直接测量，导出了计算有效体积模量 E′（计入夹带空气和机械柔度的影响）的"
       "经验公式。德国文献中常用于计算液压缸 E′ 的公式是 Lee（1977）的公式：")
eq("3.21")
b.para("参数为 a1 = 0.5、a2 = 90、a3 = 3、Emax = 18000 bar、pmax = 280 bar。Hoffmann（1981）"
       "提出了公式：", indent=False)
eq("3.22")
b.para("式中压力 p 以帕斯卡（pascal）计。据 Eggerth（1980），有效体积模量可表示为：", indent=False)
eq("3.23")
b.para("参数 k1、k2 见表 3.3；p0 取为 10 bar。", indent=False)
b.label("表 3.3　Eggerth 公式的参数（Beater, 1999）")
b.table(["温度 [°C]", "k1 [10⁻¹⁰ m²/N]", "k2 [10⁻¹⁰ m²/N]", "λ"],
        [["20","4.943","1.9540","1.480"],["50","5.469","3.2785","1.258"],
         ["90","5.762","4.7750","1.100"]],
        [3.5,4.5,4.5,2.5])
b.para("有效体积模量 E′ 的各关系式绘于图 3.4。尽管这些公式是近似的，但对设计目的而言已足够。"
       "不过，实验数据总是更可取。")
fig("3.4")

b.h3("3.1.4　本节小结", "Section Summary")
b.para("本节已介绍并讨论了最重要的三个物理性质（黏度、密度和体积模量）。从实用角度看，以下"
       "结论性陈述很重要：")
b.bullet("密度可视为常数。")
b.bullet("流体黏度随温度有显著变化（式 3.4），随压力的变化则小得多。")
b.bullet("体积模量本质上取决于压力、夹带空气和机械柔度。推荐使用经验公式（如式 3.21、3.22 和 "
         "3.23）来计算有效体积模量。不过实践中可能需要对某些参数作调整。")

b.h2("3.2　流体运动的一般方程", "General Equations of Fluid Motion")
b.para("本节简要总结支配流体流动及相关现象的守恒基本原理和定律。更详细的推导可见若干流体"
       "力学标准教材（如 Slattery, 1972；White, 1986；Lencastre, 1987；Spurk, 1996；Oertel, "
       "1999）。关于流体力学守恒律的详细理论发展与讨论，以及关于管道液压学的精彩章节"
       "（4.3 节），可见 Truckenbrodt（1996）的优秀著作。")
b.para("守恒律可通过考察给定的物质量——控制质量（control mass）或控制体（control volume）——"
       "及其广延性质（如质量、动量和能量）来导出。在流体力学中，有几种表述守恒方程的方式，"
       "如控制质量法、控制体法和控制管（control tube）法。")

b.h3("3.2.1　连续性方程与压力瞬态", "Continuity Equation and Pressure Transients")
b.para("考虑如图 3.5 所示的控制管。质量守恒（连续性）方程的积分形式可写为（Truckenbrodt, "
       "1996）：")
eq("3.24")
b.para("式中密度 ρ = ρ(t, s) 一般而言并非常数。", indent=False)
fig("3.5")
b.para("对不可压缩流体，即 ρ = 常数（这是液压学中的标准假设），式 3.24 可简化为：")
eq("3.25")
b.para("或更一般地：", indent=False)
eq("3.26")
b.para("对定常流动（steady flow），连续性方程可表示为：")
eq("3.27")
b.para("或写成一般形式：", indent=False)
eq("3.28")
b.para("接下来，把质量守恒方程写成微分的、与坐标无关的形式（对长度为 ds 的控制管微元，"
       "见图 3.5）：")
eq("3.29")
b.para("同样可给出两个特例：", indent=False)
eq("3.30", "3.31")
b.para("给定坐标系（直角、柱面或球面），通过提供该坐标系中散度（div）算子的表达式，式 3.29 "
       "可取具体形式。柱坐标系 (r, φ, x) 中连续性方程的表达式由下式给出（Truckenbrodt, 1996）：", indent=False)
eq("3.32")
b.para("再次考虑控制体 V 的质量守恒方程，设其内部累积或储存的流体质量为 m、质量密度为 ρ。"
       "由于介质假设为连续，所有流体都必须被计入，故质量储存的速率必须等于流入质量流量减去"
       "流出质量流量。因此可写出：")
eq("3.33")
b.para("计入式 3.8 并将式 3.33 除以 ρ，得：", indent=False)
eq("3.34")
b.para("若体积固定（V = V0），式 3.33 变为：", indent=False)
eq("3.35")
b.para("该方程是描述液压腔室内压力动态的基本方程。", indent=False)

b.h3("3.2.2　纳维-斯托克斯方程", "Navier-Stokes Equation")
b.para("动量守恒方程即纳维-斯托克斯方程（Navier-Stokes equation，微分形式）（Lencastre, 1987）：")
eq("3.36")
b.para("其中各项含义为：", indent=False)
b.bullet("ρg 表示体积力（body forces）。")
b.bullet("ρ dv/dt 表示惯性力。")
b.bullet("grad p 是分量为 ∂p/∂xi 的矢量，对应于压力沿流动方向的导数或斜率。")
b.bullet("项 η div(grad v) 表示矢量 v 在流动中的扩散，即由于黏性效应一个质点对其他质点的作用。")
b.bullet("项 (1/3)η grad(div v) 表示可压缩性的影响，对不可压缩液体则消失。")
b.para("设流体不可压缩并将式 3.36 通除以 ρ，得：")
eq("3.37")
b.para("在外力由势 ξ 导出的假设下，则 g = grad ξ。于是，对不可压缩液体，式 3.37 变为：", indent=False)
eq("3.38")
b.para("若该势为重力势，即 ξ = −gz，则通除以 g 给出：", indent=False)
eq("3.39")
b.para("其中 γ = ρg。在理想或完美液体（即 η = 0，现实中并不存在）的情形下，式 3.39 变为：", indent=False)
eq("3.40")
b.para("对沿迹线（path line）的流体微元，计入 η = ρν 和 γ = ρg，式 3.39 可重排为欧拉方程"
       "（Euler's equation）：", indent=False)
eq("3.41")
b.para("现在回到纳维-斯托克斯方程 3.37，并把该方程组写成柱坐标形式（Truckenbrodt, 1996）：")
eq("3.42")

b.h3("3.2.3　伯努利定理", "Bernoulli's Theorem")
b.para("考虑式 3.41，并记住（实质加速度，substantial acceleration）：")
eq("3.43", "3.44", "3.45")
b.para("于是可得：", indent=False)
eq("3.46")
b.para("方程的第一项本质上具有全局能量意义。它表示单位重量的质点沿其轨迹所排放的总能量的"
       "变化。", indent=False)
b.para("若从方程中去掉黏性项，即流动可类比为理想流体，则有：")
eq("3.47")
b.para("在定常流动的情形下，∂v/∂t = 0，能量守恒成立：", indent=False)
eq("3.48")
b.para("这就是表示一维定常流动伯努利定理（Bernoulli's theorem）的表达式。对定常流动中的"
       "不可压缩液体，若摩擦力（以及因而产生的能量损失）可以忽略，则质点的总能量沿其轨迹"
       "保持不变。", indent=False)

b.h3("3.2.4　本节小结", "Section Summary")
b.para("在本节给出的各式中，最重要、实践中最常用的是不可压缩流体的连续性方程（式 3.25–3.28）"
       "和伯努利方程 3.48（或其其他等价变体）。另一个常用的方程是描述液压腔室内压力动态的"
       "基本方程 3.35。")
b.para("一般连续性方程和纳维-斯托克斯方程仅对管道动态的分析有意义，见 4.2.5 节。")

b.h2("3.3　流体流经各种通道", "Flow Through Passages")
b.para("流体流经通道可能出现两种不同类型的流动：")
b.bullet("层流（laminar flow）或黏性流：每个流体质点描绘一条明确的轨迹，速度仅沿流动方向。")
b.bullet("湍流（turbulent flow）或水力流（这是液压现象中最常见的）：每个质点除沿流动方向的速度"
         "外，还被脉动的横向速度所扰动。")
b.para("由下式定义的雷诺数（Reynolds number）Re：")
eq("3.49")
b.para("是特征参数：Re 值较低时流动为层流；较高时为湍流。其中 v 是流动的平均速度，dh 表示"
       "水力直径（hydraulic diameter），其定义为：", indent=False)
eq("3.50")
b.para("式中 A 是流通截面积，S 是流通截面周长。对每一种流动情形，会约定其特征长度，并通过"
       "实验得到描述从黏性主导流向惯性主导流转变的雷诺数经验值。", indent=False)

b.h3("3.3.1　管道中流动的形成", "Flow Establishment in Pipelines")
b.para("液压系统的一个基本元件是圆柱形管道，其中的流动可能是层流或湍流。雷诺数所用的特征"
       "长度是管道内径 d，即：")
eq("3.51")
b.para("实验观测表明，从层流到湍流的转变发生在 2000 < Recrit < 4000 范围内，典型值为 "
       "Recrit = 2300。Re < 2300 时流动总是层流；Re > 4000 时流动通常（但并非总是）为湍流。若"
       "极其小心地避免会导致湍流的扰动，则在远高于 4000 的雷诺数下也可能保持层流。然而这些"
       "情形是例外，4000 这一上限是一条很好的经验规则（Viersma, 1980）。", indent=False)
fig("3.6")
b.label("3.3.1.1　哈根-泊肃叶定律（Hagen-Poiseuille Law）")
b.para("考虑半径 r ≤ R 的圆柱形管道，设流动为定常且层流。出发点是轴向的力平衡（图 3.6）；即：")
eq("3.52")
b.para("式中 τw 是管壁处（即 r = R 处）的剪应力。另一方面，剪应力方程 3.2 可写为"
       "（v ≡ vx，dy ≡ −dr）：", indent=False)
eq("3.53")
b.para("于是可把式 3.52 与 3.53 联立，得到：", indent=False)
eq("3.54")
b.para("这是计算圆柱形管道内层流速度分布的关系式。事实上，对式 3.54 积分（dp/dx = 常数，"
       "v(R) = 0）给出速度分布（图 3.7）：", indent=False)
eq("3.55")
b.para("并分别导出最大速度与平均速度：", indent=False)
eq("3.56")
b.para("最后，把连续性方程 3.26 与式 3.56 联立，给出所谓的哈根-泊肃叶方程（Hagen-Poiseuille "
       "equation）：", indent=False)
eq("3.57")
fig("3.7")

b.h3("3.3.2　流体流经节流孔", "Flow Through Orifices")
b.para("节流孔（orifices）是流通通道中长度很短（对锐边节流孔理想情况下长度为零）的突然收缩，"
       "可以具有固定或可变的面积（见图 3.8）。节流孔通常用于控制流量，或产生压差（阀）。")
fig("3.8")
b.para("存在两种流动状态，取决于惯性力还是黏性力占主导。流体通过节流孔的速度必须增大到高于"
       "上游区域的速度，以满足连续性定律。在高雷诺数下，节流孔两端的压降是由流体质点从上游"
       "速度加速到更高的射流速度引起的。在低雷诺数下，压降是由流体黏性产生的内部剪切力引起"
       "的。")
b.label("3.3.2.1　湍流的节流孔方程（Orifice Equations for Turbulent Flow）")
b.para("由于大多数节流孔流动发生在高雷诺数下，该区域至关重要。这类流动常被称为“湍流”"
       "（图 3.9b），但该术语的含义与管道流动中的并不完全相同（Merritt, 1967）。参照图 3.9a，"
       "流体质点在截面 1 与 2 之间被加速到射流速度。这两个截面之间的流动是流线型或势流"
       "（potential flow），经验证明在该区域使用伯努利定理是合理的。")
fig("3.9")
b.para("根据伯努利定理（式 3.48），液压流的总能量损失来自质点之间的摩擦以及质点与管道壁之间"
       "的摩擦而退化为热的能量。截面 1 与 2 之间因摩擦耗散的能量等于：")
eq("3.58")
b.para("常用无量纲压力损失系数 ζ，其定义为：", indent=False)
eq("3.59")
b.para("系数 ζ 取决于管道的几何形状和雷诺数，可近似为：", indent=False)
eq("3.60")
b.para("考虑到在远离节流孔的某点处", indent=False)
eq("3.61")
b.para("且 A1 = A0 = A = (π/4)d² = 常数，可得流量为管道面积与速度之积，即：", indent=False)
eq("3.62")
b.para("在液压领域中，常用修正的节流孔方程代替式 3.62：", indent=False)
eq("3.63")
b.para("式中 αd 是流量系数（discharge coefficient）。理论上 αd = π/(π+2) = 0.611（von Mises, "
       "1917）。若流动为湍流且 A0 ≪ A，则不论具体几何形状如何，该值可用于所有锐边节流孔。", indent=False)
b.label("3.3.2.2　湍流的流量系数（Discharge Coefficient for Turbulent Flow）")
b.para("锐边节流孔（图 3.8）因其可预测的特性和对温度变化的不敏感性而受到青睐。然而成本往往"
       "限制了它们的使用，特别是作为固定节流器时，因此常改用带长度的节流孔（图 3.8c）。这种"
       "短管节流孔的平均流量系数可表示为（Merritt, 1967）；见图 3.10：")
eq("3.64")
fig("3.10")
b.para("据 Lichtarowicz 等人（1965），平均流量系数可用下式估计（见图 3.11）：")
eq("3.65")
b.para("其中", indent=False)
eq("3.66", "3.67")
fig("3.11")
b.label("3.3.2.3　湍流-层流的流量系数（Discharge Coefficient for Turbulent-Laminar Flow）")
b.para("上面提出的公式仅在出现湍流时有效。只有在“足够大”的雷诺数下才能确保湍流：")
eq("3.68")
b.para("式中 h 是（矩形）节流孔的最小尺寸。在低温、低节流孔压降和/或小节流孔开度时，雷诺数"
       "可能变得足够低而允许层流。", indent=False)
b.para("Viersma（1980）进行的实验证明，在窄节流孔的极锐边处临界值 Recrit 低至 20，而略微倒圆"
       "的边会使 Recrit 增至 80 或更高。因此，在极锐边处，可假设 αd 在 Re > Recrit ≈ 20 时为常数。")
b.para("尽管导出式 3.63 的分析在低雷诺数下不成立，但许多人尝试通过把流量系数绘制为雷诺数的"
       "函数把该方程推广到层流区，即：")
eq("3.69")
b.para("正如许多研究者所指出的（Wuest, 1954；Viersma, 1980）。量 δ 取决于几何形状，称为层流"
       "流量系数。Viersma（1980）发现：", indent=False)
eq("3.70", "3.71", "3.72")
b.para("于是流量系数可由图 3.12 所示的层流区渐近线以及湍流区的 αd = 0.611 来表示。", indent=False)
fig("3.12")
b.label("3.3.2.4　层流的节流孔方程（Orifice Equations for Laminar Flow）")
b.para("把雷诺数表示为：")
eq("3.73")
b.para("并将式 3.73 和 3.69 代入式 3.63，对低雷诺数得到：", indent=False)
eq("3.74")
b.para("Wuest（1954）从理论上确定了流体通过锐边圆形节流孔（在无限平面内，即图 3.8a 中 "
       "do ≪ d）的层流表达式：")
eq("3.75")
b.para("以及通过锐边矩形缝隙（在无限平面内高 bo、宽 w，即图 3.8b 中 bo ≪ B，且 w ≫ bo）的"
       "表达式：", indent=False)
eq("3.76")
b.para("令式 3.74 等于式 3.75 和 3.76，得到锐边圆形节流孔 δ = 0.2，锐边缝隙节流孔 δ = 0.157。", indent=False)

b.h3("3.3.3　流体流经阀", "Flow Through Valves")
b.para("流体通过阀的节流孔（图 3.13）通常用节流孔方程 3.63 描述，并在阀芯位置 xv 与流通面积"
       "之间假设线性关系（临界中位，critical centre），即：")
eq("3.77")
b.para("其流量系数为", indent=False)
eq("3.78")
b.para("适用于伺服阀（dv：阀芯直径），以及", indent=False)
eq("3.79")
b.para("适用于具有沟槽角 α 的三角形阀座的特种比例阀（见 Kockemann 等，1991）。", indent=False)
fig("3.13")
b.para("注意 cv 通常以下式给出：")
eq("3.80")
b.para("还要注意，式 3.77 可用阀电压 uv 写为：", indent=False)
eq("3.81")
b.para("这意味着 cv 的数值和量纲必须适配所用的信号（可以是阀行程 xv、阀电压 uv 或阀电流 Iv）。"
       "在本书其余部分，将只使用符号 cv，而不考虑阀信号的性质（归一化与否）。", indent=False)
b.para("实践中，流量系数最好通过实验确定，或用阀制造商的样本数据（QN、ΔpN 和 xv,max）计算：")
eq("3.82")
b.para("式中 QN 是额定流量，ΔpN 是额定压降，xv,max 是阀的最大行程。相应的流量系数为：", indent=False)
eq("3.83")
b.para("由于式 3.77 在低雷诺数下不成立，Feigel（1987a）导出了以下用于层流-湍流阀流动情形的"
       "流量方程：")
eq("3.84")
b.para("假设 A = πdxv，所引入的层流-湍流流量系数 clt 按下式计算：", indent=False)
eq("3.85")
b.para("式中 δ 是曲线 αd = f(√Re) 按式 3.69 的斜率。当 xv → ∞ 时式 3.84 变为式 3.77，因此也可用于"
       "湍流阀流动。clt 的典型值为 0.6（Saffe, 1986）。", indent=False)
b.para("另一个被许多研究者使用（如 Klein, 1993）、并考虑了对阀芯位置 xv 依赖关系的流量系数"
       "近似公式为：")
eq("3.86")
b.para("式中 αd0 是基本流量系数，Kd,corr 是修正因子，xv,max 是最大阀芯位移。典型值为 "
       "αd0 = 0.65、Kd,corr = 0.32。", indent=False)
b.para("最后，流体通过阀节流孔的广义表达式为：")
eq("3.87")
b.para("式中 A(xv) 是阀节流孔的面积。A(xv) 取决于节流孔几何形状（即节流孔的几何形式和中位"
       "类型），不同制造商各异，特别是对比例阀。", indent=False)

b.h3("3.3.4　本节小结", "Section Summary")
b.para("对 Re < Recrit，节流孔流动为层流，流量与压降直接相关，由式 3.74 给出。在 Recrit 附近，"
       "惯性和黏性都很重要。对 Re > Recrit，流动可按湍流处理，由节流孔方程 3.63 描述。通常，"
       "节流孔方程 3.63 被用于所有情形，而完全不考虑可能遇到的流动类型。这在大多数情况下是"
       "合理的，但在某些情形下可能导致严重误差。αd 的典型且实际的值介于 0.65 与 0.75 之间。")
b.para("更实用的方法是应用节流孔方程 3.77，并按式 3.82（或等价的式 3.83）计算流量系数。")

b.h2("3.4　阀口（阀芯）作用力", "Spool Port Forces")
b.para("与流体通过阀口的流动密切相关的是作用在阀芯上的轴向力。这种流动力（flow force）由流动"
       "的动量变化引起，原因是进口流和出口流的射流角不同，如图 3.13 所示。")
b.para("作用在阀芯上的稳态轴向流动力可按下式计算（Merritt, 1967；Lausch, 1990）：")
eq("3.88")
b.para("射流角 θ 可假设为常数，即 θ ≈ 69°，由此 cosθ = 0.358，这与 von Mises（1917）导出的"
       "理论值相符（当阀芯与阀套之间没有径向间隙时）。", indent=False)
b.para("Feigel（1992）提出了以下计算未补偿滑阀稳态流动力的公式：")
eq("3.89")
b.para("其中单边阀 Kf = 0.077 [N·min/(dm³·bar)]，双边阀 Kf = 0.054，四边阀 Kf = 0.109。"
       "式 3.89 与式 3.77 联立给出：", indent=False)
eq("3.90")
b.para("迄今为止讨论的仅是稳态流动力。如果阀腔中的流体团被加速，则会产生一个作用在阀芯凸肩"
       "端面上的力。动态流动力的大小由牛顿第二定律给出：")
eq("3.91")
b.para("利用式 3.77，动态流动力变为：", indent=False)
eq("3.92")
b.para("因此，动态流动力与阀芯速度和压力变化成正比。速度项更为重要，因为它表示一个阻尼力；"
       "压力变化率项通常被忽略。", indent=False)
b.para("实践中，轴向阀芯力对阀制造商似乎并不起任何重要作用。尽管已研究了若干减小或消除这些"
       "力的补偿技术（见 Merritt, 1967 和 Feigel, 1992），但没有一种被实践者广泛接受。该问题的"
       "实际解决方案是使用两级伺服阀，其中先导级（通常是喷嘴挡板阀，flapper-nozzle valve）"
       "提供适当的力来推动主级滑阀。")

b.h2("3.5　电液类比", "Electro-hydraulic Analogy")
b.para("电液类比的原理总结于图 3.14。")
fig("3.14")
b.h3("3.5.1　液压电容", "Hydraulic Capacitance")
b.para("式 3.35 可写为：")
eq("3.93")
b.para("比例因子", indent=False)
eq("3.94")
b.para("称为液压电容（hydraulic capacitance），类比于电路中电容器的电容。", indent=False)
b.h3("3.5.2　液压电阻", "Hydraulic Resistance")
b.para("层流的液压电阻 Rh,L 例如可由哈根-泊肃叶方程 3.57 确定：")
eq("3.95")
b.para("对半径 R、长度 l 的圆柱形管道，式 3.95 给出：", indent=False)
eq("3.96")
b.para("由于在此情形下压降与流量直接成正比，由该方程给出的电阻称为对运动的线性电阻"
       "（linear resistance）。", indent=False)
b.para("然而一般而言，液压电阻对运动是非线性的，例如由于式 3.63 中的平方根函数，该式可重排"
       "为：")
eq("3.97")
b.para("或由式 3.77：", indent=False)
eq("3.98")
b.para("实践中，更可取的是使用对所讨论实际阀测量得到的 Δp–Q 特性（或流量-压力函数）。标准化"
       "阀的制造商通常在其样本中给出该特性。", indent=False)
b.h3("3.5.3　液压电感", "Hydraulic Inductance")
b.para("把牛顿定律")
eq("3.99")
b.para("连续性方程", indent=False)
eq("3.100")
b.para("与", indent=False)
eq("3.101")
b.para("联立，导出液压电感（hydraulic inductance）：", indent=False)
eq("3.102")

os.makedirs("parts", exist_ok=True)
b.save("parts/ch03.docx")
print("Saved parts/ch03.docx")
