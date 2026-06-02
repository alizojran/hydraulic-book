# -*- coding: utf-8 -*-
"""Chapter 2 — Tools for the analysis of hydraulic servo's (液压伺服系统的分析工具).
Book pages 15-31 (PDF indices 23-37).  Figures on the facing left pages:
  2.1 p22 (Discharge coefficient), 2.2 p24 (laminar/turbulent transition),
  2.3 p28 (oil-spring stiffness, rotated), 2.4/2.5 p31 (forces / friction),
  2.6 p33 (forces, flows, continuity), 2.7 p36 (servomotor survey, rotated).
"""
from viersma_docx import BookBuilder
from docx.shared import Pt

b = BookBuilder()


def P(*segs):
    return b.para_rich(list(segs))


def REF(n, text):
    p = b.doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    b._set_run(p.add_run(f"[{n}] "), bold=True, size=10.5)
    b._set_run(p.add_run(text), size=10.5)


b.h1("第 2 章　液压伺服系统的分析工具",
     "Tools for the analysis of hydraulic servo's", page_break_before=True)

b.para("要分析液压伺服系统，必须考虑以下三个方面：")
b.bullet("油液流经可变阀口（阀）的流动；")
b.bullet("油液的可压缩性；")
b.bullet("力与连续性。")

# ===================== 2.1 =====================
b.h2("2.1　湍流口流量", "Turbulent port flow")

P(("油液流经狭窄节流口的速度 ", ""), ("v", "m"), ("由下式决定：", ""))
b.equation_img(r"v = C_d\sqrt{\dfrac{2\Delta P}{\rho}}", "1")

P(("1917 年，Von Mises ", ""), ("[1]", ""), ("发现“流量（排放）系数” ", ""),
  ("C_d", "m"), ("为常数。理论上 ", ""), (r"C_d = \dfrac{\pi}{\pi+2} = 0.611", "m"),
  ("。这种流动之所以称为湍流，是因为开口两端的压降 ", ""), (r"\Delta P", "m"),
  ("与 ", ""), (r"\rho v^2", "m"), ("成正比。", ""))

P(("流量 ", ""), ("Q", "m"), ("即为阀口开度 ", ""), ("a", "m"), ("与速度 ", ""),
  ("v", "m"), ("之积：", ""))
b.equation_img(r"Q = av = bhC_d\sqrt{\dfrac{2\Delta P}{\rho}}", "2")

P(("式中 ", ""), ("h", "m"), ("（变量）为（矩形）节流口的最小尺寸（见图 2.1(a)），", ""),
  ("b", "m"), ("为恒定的宽度。只有当雷诺数“足够大”时才能保证湍流：", ""))
b.equation_img(r"Re = \dfrac{2vh}{\nu} = \dfrac{2\rho v h}{\mu}", "3")

b.scan_figure(22, "2.1", "流量系数 C_d", "Discharge coefficient Cd")

P(("式中 ", ""), (r"\nu", "m"), ("为运动黏度，", ""), (r"\mu", "m"),
  ("为动力黏度，", ""), (r"\rho", "m"), ("为密度。", ""))

P(("作者 ", ""), ("[2]", ""),
  ("的实验证明：在狭窄节流口非常锐利的棱边处，临界值 ", ""), ("Re_{cr}", "m"),
  ("低至 20；而棱边稍有圆角时，", ""), ("Re_{cr}", "m"),
  ("会升至 80 甚至更高！因此，在非常锐利的棱边处，可认为当 ", ""),
  ("Re > Re_{cr} \\approx 20", "m"), ("时 ", ""), ("C_d", "m"), ("为常数。", ""))

P(("在较小的 ", ""), ("Re", "m"), ("值下，会形成边界层。1954 年 Wuest ", ""),
  ("[3]", ""), ("针对极低的 ", ""), ("Re", "m"), ("值导出：", ""))
b.equation_img(r"C_d = \delta\sqrt{Re}", "4")

P(("式中 ", ""), (r"\delta", "m"), ("为依赖于几何形状的常数。联立式 (1)、(3)、(4) 得", ""))
b.equation_img(r"v = C_d\sqrt{\dfrac{2\Delta P}{\rho}} = \delta\sqrt{Re}\,"
               r"\sqrt{\dfrac{2\Delta P}{\rho}} = \delta\sqrt{\dfrac{2\rho v h}{\mu}}"
               r"\cdot\sqrt{\dfrac{2\Delta P}{\rho}}")
b.para("由此得到")
b.equation_img(r"v = \dfrac{4\delta^2}{\mu}\,h\Delta P")
b.para("以及")
b.equation_img(r"Q = av = bhv = \dfrac{4\delta^2}{\mu}\,bh^2\Delta P", "5")

P(("将层流外推到较大的 ", ""), ("Re", "m"),
  ("值，并假定从层流到湍流为突然过渡，可得", ""))
b.equation_img(r"\delta = \dfrac{C_{d,\mathrm{turb}}}{\sqrt{Re_{cr}}} \approx "
               r"\dfrac{0.611}{\sqrt{20}} = 0.136", "6")

P(("作者于 1961 年提出的这种层流—湍流流动模型 ", ""), ("[2]", ""),
  ("（见图 2.2(b)）可作为计算各类流量的基础。", ""))

b.scan_figure(24, "2.2", "从层流到湍流的过渡",
              "Transition from laminar to turbulent flow")

P(("将其应用于图 2.2(a) 的零开口（临界中位）阀：在很小的阀口开度下会出现层流，", ""),
  ("Q", "m"), ("与 ", ""), ("x", "m"), ("之间呈式 (5) 的抛物线关系。当 ", ""),
  ("x = h_T", "m"), ("时越过临界雷诺数 ", ""), ("Re_{cr}", "m"),
  ("，于是按式 (2) 转为恒定的流量增益。所幸 ", ""), ("x = 0", "m"),
  ("附近流量增益偏低的区域很小。由式 (2)–(6) 得", ""))
b.equation_img(r"h_T = \dfrac{\nu\,Re_{cr}}{2C_{d,\mathrm{turb}}\sqrt{2\Delta P/\rho}}", "7")

P(("例如取 ", ""),
  (r"\nu = 30\times10^{-6}\,\mathrm{m^2/s}", "m"), ("、", ""),
  ("Re_{cr} = 20", "m"), ("、", ""), ("C_d = 0.611", "m"), ("、", ""),
  (r"\Delta P = 50\times10^{5}\,\mathrm{N/m^2}", "m"), ("、", ""),
  (r"\rho = 900\,\mathrm{kg/m^3}", "m"), ("，可得 ", ""),
  (r"h_T = 4.66\times10^{-6}\,\mathrm{m} = 4.66\,\mu\mathrm{m}", "m"), ("。", ""))

P(("流量增益偏低的区域，可通过采用宽度 ", ""), ("b", "m"),
  ("更小的节流口而按比例缩小，如图 2.2(b) 所示。此时 ", ""), ("h_T", "m"),
  ("仍与前相同，但由于宽度 ", ""), (r"b < \pi d", "m"),
  ("，它发生在更小的流量处。因此，以最大流量或阀行程的百分比计，"
   "低增益区被大大缩小了！", ""))

P(("此外，还可在我们的“零开口”阀中引入一个非常小的搭接量 ", ""), ("U", "m"),
  ("。设进、出口开度 ", ""), ("a_1 = bh_1 = b(U+x)", "m"), ("、", ""),
  ("a_2 = bh_2 = b(U-x)", "m"), ("，压降 ", ""),
  (r"\Delta P_1 = \Delta P_2 = \Delta P", "m"), ("，则在搭接区内有", ""))
b.equation_img(r"Q_1 - Q_2 = \dfrac{4\delta^2}{\mu}\,b\,(h_1^2\Delta P_1 - "
               r"h_2^2\Delta P_2) = \dfrac{16\delta^2}{\mu}\,b\Delta P\,U x")
b.para("于是")
b.equation_img(r"\dfrac{\partial(Q_1 - Q_2)}{\partial x} = "
               r"16\dfrac{\delta^2}{\mu}\,b\Delta P\,U = \mathrm{constant}\,!!", "8")

P(("要求此流量增益等于 ", ""), ("x > h_T", "m"),
  ("处按式 (2) 的湍流流量增益，可得", ""))
b.equation_img(r"U = \dfrac{\nu\,Re_{cr}}{8C_{d,\mathrm{turb}}\sqrt{2\Delta P/\rho}} "
               r"= \dfrac{h_T}{4}", "9")

P(("可见——在上例中——即使搭接量极小，", ""), (r"U = 1.16\,\mu\mathrm{m}", "m"),
  ("，也能在阀的整个工作范围内获得很好的恒定流量增益。这与制造商的实践相符："
   "通常采用几微米的搭接量来获得恒定的流量增益。尽管导出式 (8) 的假设"
   "并不会自动满足，结果却确实如此。", ""))

b.para("作为本节的结论，我们指出：在通常的工程实践中，可以不顾雷诺数（!!）"
       "直接采用湍流流量方程 (2)，只要记住在很小的阀口开度处，"
       "计算所得的流量增益可能出现相当大的偏差。")

# ===================== 2.2 =====================
b.h2("2.2　油液的可压缩性", "Compressibility of oil")

b.para("油液的可压缩性会显著影响液压伺服系统的动态特性，这一点常令外行人感到意外。"
       "油液这类液压流体虽远不如气体易于压缩，但当它在缸腔中被压缩时，其作用犹如"
       "一根弹簧，从而引入一个二阶质量—弹簧系统，其固有频率会陡然限制任何液压伺服"
       "系统的带宽。封闭在体积 V、压力 P 下的液压流体，其可压缩性定义为：")
b.equation_img(r"\dfrac{\Delta V}{V} = -\dfrac{\Delta P}{E}", "10")

P(("E", "m"), ("称为体积模量，常记作 ", ""), ("B", "m"), ("或 ", ""),
  (r"\beta", "m"), ("。体积模量与金属的杨氏弹性模量同量纲（", ""),
  (r"\mathrm{N/m^2}", "m"), ("）。出于类比，沿用同一符号 ", ""), ("E", "m"),
  ("。对矿物油，", ""), ("E", "m"), ("可高达 15 000 bar（", ""),
  (r"15\times10^{8}\,\mathrm{N/m^2}", "m"),
  ("）。但其实际有效值要低得多，主要是因为不可避免地混入了少量空气。此外，"
   "油箱使用不当（回油飞溅、液面面积过小、吸油滤器堵塞等）以及系统中的盲孔与气囊，"
   "都可能使 ", ""), ("E", "m"),
  ("降到理论值的 10% 以下！在良好的工程实践中，可期望 ", ""), ("E", "m"),
  ("介于 6 000～12 000 bar 之间。", ""))

P(("钢制缸体与管道的弹性对有效 ", ""), ("E", "m"),
  ("略有影响，但通常可以忽略。然而（高压）软管的弹性，则可能对有效体积模量 ", ""),
  ("E", "m"), ("造成灾难性的影响。", ""))

P(("图 2.3 中各种伺服系统的油弹簧刚度 ", ""), ("c_o", "m"),
  ("，都是基于某一确定的体积模量 ", ""), ("E", "m"),
  ("推导的。在图 2.3(a) 中，按式 (10)，", ""), (r"\Delta V = yA", "m"), ("、", ""),
  ("V = AL + V_L", "m"), ("，其中 ", ""), ("AL", "m"),
  ("为缸腔的有效容积，", ""), ("V_L", "m"), ("为无效容积。压力增量 ", ""),
  (r"\Delta P", "m"), ("由负载 ", ""), (r"F = A\Delta P", "m"),
  ("引起。于是", ""))
b.equation_img(r"\dfrac{yA}{AL + V_L} = -\dfrac{F}{AE} \,,\qquad "
               r"c_o = -\dfrac{F}{y} = \dfrac{A^2 E}{AL + V_L}", "11")

P(("负号源于 ", ""), ("y", "m"), ("与 ", ""), ("F", "m"),
  ("约定上（相反！）的正方向。在图 2.3(b) 和 (c) 中，", ""), ("c_o", "m"),
  ("由活塞两侧的油弹簧刚度相加得到。", ""))

b.scan_figure(28, "2.3", "油弹簧刚度与固有频率",
              "Oil spring stiffness and natural frequency", max_cm=16.2, rotate=270)

P(("线性马达 (a)、(b)、(c) 的刚度 ", ""), ("c_o", "m"),
  ("都强烈依赖于活塞位置。由于最低可能固有频率 ", ""),
  (r"\omega_o = \sqrt{c_o/M}", "m"),
  ("最为重要，已对图 2.3 中每一种马达算出了 ", ""), (r"c_{o,\min}", "m"),
  ("。", ""))

P(("图 2.3(d) 的旋转马达是一个特例。其旋转油弹簧刚度（单位 ", ""),
  (r"\mathrm{Nm/rad}", "m"),
  ("）可类比对称线性马达推导：用每弧度排量 ", ""), ("V_r", "m"),
  ("代替活塞面积 ", ""), ("A", "m"), ("，用 ", ""), (r"\pi", "m"),
  ("弧度（半圈）代替行程 ", ""), ("S", "m"), ("。当然，", ""), ("c_o", "m"),
  ("也可以直接通过下列代换得到：", ""))

P(("　　腔室容积：　", ""), (r"V_{1,2} = \dfrac{\pi}{2}V_r + \dfrac{V_L}{2}", "m"),
  ("，代替 ", ""), (r"V_{1,2} = \dfrac{S}{2}A + \dfrac{V_L}{2}", "m"), ("；", ""))
P(("　　流量：　　", ""), (r"Q_1 - Q_2 = \dot{\varphi}V_r", "m"), ("，代替 ", ""),
  (r"Q_1 - Q_2 = \dot{y}A", "m"), ("；", ""))
P(("　　负载：　　", ""), (r"T = V_r(P_1 - P_2)", "m"), ("，代替 ", ""),
  (r"F = A(P_1 - P_2)", "m"), ("。", ""))

P(("在许多应用中，一个重要的事实是：“无效”管路容积 ", ""), ("0.5V_L", "m"),
  ("相对于有效容积 ", ""), (r"0.5\pi V_r", "m"),
  ("不可忽略。因此在计算或估算旋转马达的 ", ""), ("c_o", "m"),
  ("时，必须格外小心。", ""))

P(("旋转马达及其常用传动装置的第二个复杂之处，是马达所“感受到”的惯量。"
   "折算到马达轴上的齿轮系等惯量，也汇总于图 2.3(d) 中。通常这一“附加惯量”"
   "比旋转马达自身的惯量 ", ""), ("J_M", "m"),
  ("大 5～10 倍。因此可以说：精心设计齿轮系等部件以获得可接受的固有频率 ", ""),
  (r"\omega_o = \sqrt{c_o/J_{\mathrm{tot}}}", "m"),
  ("，其重要性怎么强调都不为过。", ""))

# ===================== 2.3 =====================
b.h2("2.3　力与连续性", "Forces and continuity")

P(("这里将针对最一般的情形——非对称线性马达（", ""), (r"A_1 \neq A_2", "m"),
  ("）配非对称四通阀（", ""), (r"a_1 \neq a_3,\ a_2 \neq a_4", "m"),
  ("）——讨论复杂的力与连续性问题，见图 2.4。其他情形要简单得多，"
   "其结果可由这一般情形轻易导出。", ""))

b.para("下面按来源列出最重要的各种力，并简要讨论。")
b.bullet("油压 P₁ 与 P₂ 产生方向相反的作用力 P₁A₁ 与 P₂A₂（见图 2.4）。")
b.bullet("外力 Fₑ 来自液压马达外部，例如机床的切削力。")
b.bullet("摩擦力，与速度 ẏ 方向相反。须区分（线性的）黏性摩擦与高度非线性的"
         "库仑摩擦（干摩擦）。")
b.bullet("库仑摩擦是液压伺服系统中最“神奇”的非线性因素：一旦出现异常情况，"
         "它总是头号嫌疑！在通常实践中，库仑摩擦可达最大负载能力的 5～15%，"
         "因此绝不能像许多教科书和制造商样本那样忽略它，否则后果严重。本书作"
         "简化假设：运动中的马达，其库仑摩擦为常数，并随速度 ẏ 改变符号"
         "（见图 2.5）。尽管有一些误导性的文献，这里仍要强调（并将在后文证明）："
         "库仑摩擦本身无法在实践中提供足够的稳定性。")
b.bullet("黏性摩擦与速度 ẏ 成正比，在许多液压系统中有助于稳定性与阻尼。通常它无法"
         "被充分预测，其大小既难以精确设计，也几乎无法直接测量。然而其存在可被间接"
         "证明：大量实验都显示出某种程度的系统阻尼，而唯一的解释就是黏性摩擦的存在。"
         "因此在动态分析中绝不应将其忽略。")

P(("我们的实验还以间接的方式表明，黏性摩擦与库仑摩擦之间存在很强的相关性。"
   "例如，液压缸中的静压轴承不仅消除了库仑摩擦（这正是其目的！），同时也消除了"
   "黏性摩擦，从而使得必须另行采取阻尼措施！", ""))

P(("综上所述，我们采用图 2.5 所示的简单（但已足够复杂）的摩擦模型：", ""))
b.equation_img(r"F_{\mathrm{friction}} = F_c + w\dot{y} = "
               r"\dfrac{\dot{y}}{|\dot{y}|}\,|F_c|_{\max} + w\dot{y}")

b.scan_figure_crop(31, 0.04, 0.40, "2.4", "作用力", "Forces")
b.scan_figure_crop(31, 0.40, 0.97, "2.5", "库仑摩擦与黏性摩擦",
                   "Coulomb friction and viscous friction")

P(("将图 2.4 中的各力与牛顿定律联立，得", ""))
b.equation_img(r"P_1 A_1 - P_2 A_2 - F_e - F_c - w\dot{y} = M\ddot{y}")
b.para("或")
b.equation_img(r"P_1 A_1 - P_2 A_2 = F_e + F_c + w\dot{y} + M\ddot{y}")
P(("现定义总负载 ", ""), (r"\Sigma F", "m"), ("为", ""))
b.equation_img(r"\Sigma F = F_e + F_c + w\dot{y} + M\ddot{y}")
b.para("最终得到")
b.equation_img(r"P_1 A_1 - P_2 A_2 = \Sigma F = F_e + F_c + w\dot{y} + M\ddot{y}")

P(("可见，油压 ", ""), ("P_1", "m"), ("与 ", ""), ("P_2", "m"),
  ("之间的关系取决于总负载 ", ""), (r"\Sigma F", "m"), ("。而 ", ""), ("P_1", "m"),
  ("、", ""), ("P_2", "m"), ("又决定阀中各阀口两端的压降。利用", ""))
b.equation_img(r"Q = av = aC_d\sqrt{\dfrac{2\Delta P}{\rho}}")
P(("图 2.6 中流经阀口 ", ""), ("a_1", "m"), ("、", ""), ("a_2", "m"), ("、", ""),
  ("a_3", "m"), ("、", ""), ("a_4", "m"), ("的流量为", ""))
b.equation_img(r"Q_1 = a_1 C_d\sqrt{\dfrac{2(P_s - P_1)}{\rho}},\quad "
               r"Q_2 = a_2 C_d\sqrt{\dfrac{2P_1}{\rho}},")
b.equation_img(r"Q_3 = a_3 C_d\sqrt{\dfrac{2P_2}{\rho}},\quad "
               r"Q_4 = a_4 C_d\sqrt{\dfrac{2(P_s - P_2)}{\rho}}.")

b.scan_figure(33, "2.6", "力、流量与连续性", "Forces, flows and continuity")

P(("考虑油液的可压缩性（按图 2.3）以及连续性，可得到关于马达速度 ", ""),
  (r"\dot{y}", "m"), ("的两个（!）方程：", ""))
b.equation_img(r"\dot{y} = \dfrac{Q_1 - Q_2}{A_1} - "
               r"\dfrac{A_1 L_1 + V_{L1}}{A_1 E}\,\dot{P}_1")
b.equation_img(r"\dot{y} = \dfrac{Q_3 - Q_4}{A_2} + "
               r"\dfrac{A_2 L_2 + V_{L2}}{A_2 E}\,\dot{P}_2")

P(("联立前述各式并忽略 ", ""), ("V_{L1}", "m"), ("与 ", ""), ("V_{L2}", "m"),
  ("，最终得到", ""))
b.equation_img(r"\dot{y} = C_d\sqrt{\dfrac{P_s}{\rho}}\left[\dfrac{a_1}{A_1}"
               r"\sqrt{2\!\left(1 - \dfrac{P_1}{P_s}\right)} - \dfrac{a_2}{A_1}"
               r"\sqrt{\dfrac{2P_1}{P_s}}\right] - \dfrac{L_1}{E}\dot{P}_1", "12")
b.equation_img(r"\dot{y} = C_d\sqrt{\dfrac{P_s}{\rho}}\left[\dfrac{a_3}{A_2}"
               r"\sqrt{\dfrac{2P_2}{P_s}} - \dfrac{a_4}{A_2}"
               r"\sqrt{2\!\left(1 - \dfrac{P_2}{P_s}\right)}\right] "
               r"+ \dfrac{L_2}{E}\dot{P}_2", "13")
b.para("式中")
b.equation_img(r"P_1 A_1 - P_2 A_2 = \Sigma F = F_e + F_c + w\dot{y} + M\ddot{y}", "14")

P(("由这些方程，须解出 ", ""), ("P_1", "m"), ("、", ""), ("P_2", "m"),
  ("以及 ", ""), (r"\dot{y}", "m"),
  ("。一般而言，无法求得解析解；只有在非常特殊的条件下才能找到特解。", ""))

P(("任何解都必须满足这样的要求：由式 (12) 与 (13) 给出的速度 ", ""),
  (r"\dot{y}", "m"),
  ("必须相同。令式 (12) 与 (13) 中所有对应项分别相等，即可方便地求得一个特解。"
   "这些“条件”为：", ""))
b.equation_img(r"\dfrac{a_1}{A_1} = \dfrac{a_3}{A_2} \,,\qquad "
               r"\dfrac{a_2}{A_1} = \dfrac{a_4}{A_2}", "15")
b.equation_img(r"L_1 = L_2 = \dfrac{S}{2}", "16")
b.equation_img(r"P_1 + P_2 = P_s", "17")

P(("条件 (15) 涉及阀与马达的尺寸，理论上可以满足。条件 (16) 把解限制在活塞的"
   "某一个位置。条件 (17) 与式 (14) 联立，得", ""))
b.equation_img(r"\dfrac{P_1}{P_s} = \dfrac{A_2 + \Sigma F/P_s}{A_1 + A_2} "
               r"\,,\qquad "
               r"\dfrac{P_2}{P_s} = \dfrac{A_1 - \Sigma F/P_s}{A_1 + A_2}", "18")

b.para("将式 (15)、(16)、(18) 代入式 (12)，得")
b.equation_img(r"\dot{y} = C_d\sqrt{\dfrac{2P_s}{\rho}}\left[\dfrac{a_1}{A_1}"
               r"\sqrt{\dfrac{A_1 - \Sigma F/P_s}{A_1 + A_2}} - \dfrac{a_2}{A_1}"
               r"\sqrt{\dfrac{A_2 + \Sigma F/P_s}{A_1 + A_2}}\right] "
               r"- \dfrac{1}{c_o}\dfrac{\mathrm{d}\,\Sigma F}{\mathrm{d}t}", "19")
P(("式中 ", ""), (r"c_o = \dfrac{2E(A_1 + A_2)}{S}", "m"), ("。", ""))

P(("如上所述，式 (19) 只是一个特解，仅在条件 (15) 与 (16) 满足时才成立。"
   "问题在于：若条件不满足，该解是否仍为良好的近似？文献中对此问题一向系统性地"
   "回避，默认条件是否满足无关紧要。", ""))

P(("第 3 章将证明：若条件 (15) 不满足，式 (18) 与 (19) 与物理实际毫无相似之处，"
   "这暗示非对称马达需要配用非对称阀。我们将证明这一暗示是正确的，但其用处不大，"
   "因为非对称阀通常无商品供应……因此需要专门设法解决这一问题。", ""))

P(("对称马达配对称阀则不会带来这类麻烦。把阀口开度 ", ""), ("a_1", "m"),
  ("、", ""), ("a_2", "m"), ("与阀芯位移 ", ""), ("x", "m"),
  ("联系起来，经线性化与近似处理后，可得到一个便于处理的微分方程，"
   "从而允许进行动态分析、综合与设计。后续各章将针对几种液压伺服马达完成此项工作。"
   "图 2.7 作为一份“预先的总结”，给出了液压伺服马达的基本综览——其中已应用上述"
   "分析工具并完成了线性化。", ""))

b.scan_figure(36, "2.7", "液压伺服马达综览", "Survey of hydraulic servomotors",
              max_cm=16.2, rotate=270)

# ---- references ----
b.h2("参考文献", "References")
REF(1, "R. von Mises, Berechnung von Ausfluß- und Überfallzahlen, "
       "Z. Ver. Deutsch. Ing., 61 (1917) 447.")
REF(2, "T. J. Viersma, Investigations into the accuracy of hydraulic servomotors, "
       "Thesis, Delft University of Technology (1961); "
       "Philips Res. Rep. 16 (1961) 507; 17 (1962) 20.")
REF(3, "W. Wuest, Strömung durch Schlitz- und Lochblenden bei kleinen "
       "Reynolds-Zahlen, Ing.-Arch., 22 (1934) 357.")

b.save("parts/ch02.docx")
print("saved parts/ch02.docx")
