# -*- coding: utf-8 -*-
"""第 7 章 案例研究与实验结果 —— 内容构建（WIP，逐节扩充）。Produces parts/ch07.docx.
This chapter is figure-heavy (experimental plots); most figures use explicit boxes."""
import os, re, fitz, hashlib
from hsbook_docx import DocBuilder, extract_equations, SRC_PDF, pidx

CH = 7
PAGES = range(289, 315)
os.makedirs("ch7_eqs", exist_ok=True)
doc = fitz.open(SRC_PDF)
EQ = {}
for pp in PAGES:
    EQ.update(extract_equations(SRC_PDF, pidx(pp), CH, "ch7_eqs"))
# OCR-invisible equation labels -> explicit bands (page, y0, y1), full content width
def _band_eq(pg, y0, y1, label, dpi=200, pad=7):
    page = doc[pidx(pg)]; ws = page.get_text("words")
    L = min(w[0] for w in ws); R = max(w[2] for w in ws)
    box = fitz.Rect(L-pad, y0, R+pad, y1)
    path = os.path.join("ch7_eqs", f"eq_{label}.png"); page.get_pixmap(dpi=dpi, clip=box).save(path)
    return (path, box.width/72*2.54)
EXPLICIT_EQ = {"7.4": (303, 224, 256)}
for _lab, (_pg, _y0, _y1) in EXPLICIT_EQ.items():
    EQ[_lab] = _band_eq(_pg, _y0, _y1, _lab)

# ---- figures ----
os.makedirs("ch7_figs", exist_ok=True)
FIGPAGE = {}   # filled per section
MANUAL  = {}   # explicit boxes (page, x0, y0, x1, y1) for experimental plots
FIGCAP  = {}
def _figbox(page, fig):
    ws = page.get_text("words"); left = min(w[0] for w in ws); right = max(w[2] for w in ws)
    blocks = sorted(page.get_text("blocks"), key=lambda b: b[1]); caps = {}
    for b in blocks:
        m = re.match(r"\s*Figure\s*(\d+\.\d+)\.", b[4].replace("\n", " "))
        if m: caps.setdefault(m.group(1), b)
    cy0 = caps[fig][1]; top = page.rect.y0 + 40
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
    path = f"ch7_figs/fig_{fig}.png"; page.get_pixmap(dpi=200, clip=box).save(path); return path

b = DocBuilder()
_lasteq = [None]
def eq(*labels):
    for L in labels:
        entry = EQ[L]; hh = hashlib.md5(open(entry[0], "rb").read()).hexdigest()
        if hh == _lasteq[0]: continue
        b.eq_image(entry); _lasteq[0] = hh
def fig(num):
    cn, en, w = FIGCAP[num]; b.figure(_crop(num), num, cn, en, w)

# ===== section 7.1 assets =====
FIGPAGE.update({"7.1": 289, "7.3": 290, "7.6": 293, "7.10": 297})
MANUAL.update({"7.2": (290, 65, 93, 388, 255), "7.4": (291, 65, 378, 388, 545),
               "7.5": (292, 65, 93, 388, 322), "7.7": (295, 65, 93, 388, 255),
               "7.8": (295, 65, 328, 388, 545), "7.9": (296, 65, 273, 388, 435)})
FIGCAP.update({
 "7.1": ("“长缸试验台”：实际构造与原理图", "'Long cylinder test bed': actual construction and schematic diagram", 12),
 "7.2": ("开环速度阶跃响应", "Open-loop velocity step responses", 12),
 "7.3": ("辨识数据集：输入信号（上）与所得活塞速度（下）", "An identification data set: input signal (top) and resulting piston velocity (bottom)", 12),
 "7.4": ("NOBCF(5,2) 模型在验证数据上的评估", "Evaluation of the NOBCF(5,2) model on the validation data", 12),
 "7.5": ("NOBCF(4,2) 模型的阶跃响应（仿真）", "Step responses of the NOBCF(4,2) model (simulation)", 12),
 "7.6": ("不同输入的阶跃响应（并联评价）：测量（含噪曲线）、模糊模型预测、物理模型预测", "Step responses for different inputs (parallel evaluation)", 12),
 "7.7": ("参考阶跃下模糊状态控制器与模糊 NMPC 的比较（仿真）", "Fuzzy state controller vs. fuzzy NMPC for reference steps (simulation)", 12),
 "7.8": ("带时不变设定点滤波器的线性状态反馈控制器的阶跃响应", "Step responses with a linear state feedback controller with time-invariant set-point filter", 12),
 "7.9": ("PID 控制器的阶跃响应", "Step responses with a PID controller", 11.5),
 "7.10": ("NNOE(4,1,4) 神经网络模型的并联评价与测量输出比较", "Parallel evaluation of the NNOE(4,1,4) neural network model vs. measured output", 12),
})

b.h1("第 7 章　案例研究与实验结果", "CHAPTER 7  CASE STUDIES AND EXPERIMENTAL RESULTS",
     page_break_before=True)
b.para("本章描述若干使用本书所述精选建模与控制方法的案例研究，以展示这些方法的性能和不同"
       "方面。重点放在就开发时间、闭环性能和计算量，比较广泛使用的经典（多为线性）方法与"
       "高级（通常为非线性）策略。")
b.h2("7.1　同步缸的辨识与控制", "Identification and Control of a Synchronising Cylinder")
b.para("第一个案例研究处理图 7.1 所示电液驱动的建模与控制。将应用不同技术（经典、模糊逻辑、"
       "神经网络）来辨识系统的黑箱模型并对其控制。")
fig("7.1")
b.h3("7.1.1　系统描述", "System Description")
b.para("该系统主要由一个同步缸（带长活塞杆）和一个伺服阀组成（驱动参数概览见附录 B.1）。"
       "图 7.2 阐明了系统对输入信号 u（伺服阀电压）阶跃变化的典型开环速度响应。阶跃响应清楚"
       "显示输入信号相关的阻尼：小输入信号时呈振荡行为，大输入信号时呈阻尼行为。因此，线性"
       "模型显然不能在整个运行范围上近似这种行为。")
fig("7.2")
b.para("由于系统关于活塞位置的积分行为，用简单有限差分法（即欧拉近似）计算的活塞速度将用作"
       "辨识的输出信号 y。输入信号被缩放为 u′ = u/10 [V]（10 V 是最大伺服阀电压）。用伪随机"
       "多电平信号激励液压伺服系统，以 1 kHz 采样率采集 5000 对输入-输出数据记录用于系统参数"
       "辨识，如图 7.3 所示。类似地，为验证过程生成了若干数据集（PRMS 和阶跃响应族）。")
fig("7.3")
b.h3("7.1.2　标准形连续时间模型", "Continuous-time Model in Canonical Form")
b.para("本案例研究从基于 5.4.1 节引入的模型结构、结合 5.5.3 节所述延迟状态变量滤波器用 OLS 法"
       "导出连续时间模型开始。选择一个用两个二阶全通滤波器均衡、截止频率 400 rad/s 的六阶"
       "巴特沃思滤波器作为延迟状态变量滤波器，以产生用于系统辨识的延迟滤波输入、输出及相关"
       "高阶导数。为参数估计指定了一个二次非线性度（l=2）的五阶（n=5）非线性能观性标准形"
       "模型（见式 5.64 和 5.67），即 NOBCF(5,2)。该指定含 21 个候选项，ERR 之和（式 5.138）"
       "达到 99.95，表明所选项充分表示了系统。图 7.4 和 7.5 给出用（PRMS）测试数据集的交叉"
       "验证结果以及阀输入幅值 u′=0.1, 0.2, …, 1 的十个阶跃响应。显然，所辨识的（NOBCF）描述"
       "就小的稳态偏差和良好捕捉的可变阻尼而言，提供了该驱动的高质量模型。")
fig("7.4"); fig("7.5")
b.h3("7.1.3　模糊模型辨识", "Fuzzy Model Identification")
b.para("应用 5.8.2.1 节所述 Kortmann（1989）的结构搜索算法，辨识出回归向量和特征向量由 "
       "y(k−1)、y(k−2)、y(k−3)、y(k−4) 和 u(k−4) 组成（用于预测 y(k)）。Reuter（1995）确定合适"
       "采样时间在 0.86 至 1.3 ms 之间；然而选择采样时间 T0=2 ms，因为测试表明这能使模糊状态"
       "反馈控制算法在实现时的标准个人计算机（PC 486-66DX）上实时执行（1 ms 周期不允许实时"
       "执行非线性控制律）。辨识并优化了一个以这些为输入、c=4 条规则、∞-范数、v=1.5 的模糊"
       "模型。图 7.6 给出与不同阶跃响应的交叉验证，并描绘了物理模型的仿真结果。模糊模型比"
       "简化的基于第一性原理的模型表现更好，但开发时间少几个数量级。")
fig("7.6")
b.h3("7.1.4　模糊模型预测控制器与模糊状态反馈控制器", "Fuzzy Model Predictive and Fuzzy State Feedback Controllers")
b.para("下面研究该线性电液驱动的伺服控制。控制目标定义为：在控制信号及其变化率受约束下，应"
       "尽快跟随速度参考的任意阶跃响应；闭环特性应与控制信号幅值无关；超调应可容忍（如约 "
       "15%）。所有信号归一化：y*=y/1 [m/s]、yref*=yref/1 [m/s]、u*=u/10 [V]。本节结果均由仿真"
       "研究获得。")
b.label("7.1.4.1　模糊模型预测控制器的实现细节")
b.para("所用模糊 MPC 已在 6.7.2 节描述，它用 7.1.3 节辨识的 Sugeno 型模糊模型作内部预测模型。"
       "由于辨识的死区时间 τ=3，最小代价时域选为 N1=1+τ=4。最大代价时域按过程主导时间常数"
       "设为 N2=8（约对应幅值 yref=0.4 阶跃响应的整定时间）。Nu=2（相比 Nu=1 有明显改善，"
       "Nu>2 改善可忽略）。须满足若干约束：缩放控制信号 |u*|≤1（来自伺服阀控制范围），"
       "|Δu*|≤0.8（任意选取），|y*|≤0.8（物理给定的最大可达速度，但从未违反）。为避免计算任意"
       "稳态控制的额外模块，代价函数中不考虑 u² 项（γ=0）；β 设为 1；α=5（在控制性能与控制"
       "信号活跃度之间提供合理折中）；Δu0=0 为优化初值。过程用第 4 章所述基于物理的连续时间"
       "模型的简化版本仿真。")
b.label("7.1.4.2　模糊状态反馈控制器的实现细节")
b.para("模糊状态反馈控制器按 6.7.1 节设计。第一阶段，选择每个局部模型的主导极点，使相应的"
       "连续时间二阶时滞系统具有阻尼 D=0.7 和特征频率 ωh=500 s⁻¹。该控制算法可望在标准工业"
       "控制平台上实时执行：在 PC 486-66DX 上计算一个控制作用耗时不到 2 ms。过程用 5.4.2.3 节"
       "描述、7.1.3 节辨识的 Sugeno 型模糊模型仿真。")
b.label("7.1.4.3　仿真结果")
b.para("图 7.7 给出模糊 MPC 和模糊状态空间控制器对参考速度阶跃变化（yref=0.1, …, 0.6 m/s，"
       "0.1 m/s 增量）的阶跃响应。仿真从初始速度 y0=−0.0112 m/s（u=0 时的数值平衡）开始。对"
       "模糊 MPC，阶跃响应的动态与参考值变化幅值无关，且整定时间显著短于非线性模糊状态反馈"
       "控制器：20 ms（小参考幅值）到 40 ms（大参考幅值）后被控变量保持在参考处，无稳态误差"
       "残留（尽管物理模型与模糊模型的稳态增益不同）。然而，如前所述，若在最先进工业自动化"
       "系统上执行，模糊 MPC 对该应用不具备实时能力。")
fig("7.7")
b.para("模糊状态反馈控制器把强烈变化的开环动态补偿到最小。自适应设定点滤波器完全消除了稳态"
       "误差——这种误差在无设定点滤波器或带恒定设定点滤波器的（线性/模糊）比例状态反馈控制器"
       "情形下会出现（图 7.8）。整定时间（略）短于线性状态反馈控制器情形。如上所述，模糊状态"
       "反馈控制器可望在标准工业硬件上实时执行。")
fig("7.8")
b.para("带自适应设定点滤波器的线性状态反馈控制器产生与模糊状态反馈控制器几乎相同的结果，"
       "尽管所得局部闭环系统结果不稳定。此外还测试了保证稳定性的基于 LMI 的控制器设计，但由于"
       "设计的保守性，闭环性能明显差于上面所给出的。图 7.9 给出线性 PID 控制器的阶跃响应作"
       "比较。为公平比较，用数值优化设计 PID 控制器（以足够长每段阶跃的 PRMS 为参考序列、"
       "最小化被控变量与参考偏差的平方和选取三个控制器参数）。如预期，积分部分消除了稳态误差，"
       "但闭环系统的动态明显随参考信号阶跃幅值变化，整定时间也显著更长。用时不变 PID 控制器"
       "不可能补偿液压驱动的可变阻尼以使闭环系统对所有参考信号有相似动态。")
fig("7.9")
b.h3("7.1.5　神经网络（多层感知器）辨识", "Neural Network (Multi-layer Perceptron) Identification")
b.para("为比较训练了一个（全连接）神经网络（MLP）模型。模型结构选为单隐层含六个神经元的 "
       "NNOE(4,1,4)。训练前把数据集缩放为零均值和单位方差（式 5.10 和 5.11）；训练后把网络中的"
       "权重新缩放，以使模型可应用于未缩放数据。图 7.10 中，把观测输出与若干输入阶跃的并联"
       "模型评价（即模型的纯仿真）比较。仿真表明 ANN 模型的预测质量良好。")
fig("7.10")

b.h3("7.1.6　本节小结", "Section Summary")
b.para("从本节给出的辨识结果看，所考虑的液压驱动可用所考虑的所有模型（即多项式模型、模糊"
       "模型和 ANN 模型）恰当地建模。控制器仿真研究证明，带自适应设定点滤波器的模糊状态反馈"
       "控制器产生比线性 PID 控制器、甚至比线性状态反馈控制器更优的结果；最佳控制性能由模糊"
       "模型预测控制器实现，但后者在标准自动化平台的工业应用上仍远未可实现。")

# ===== section 7.2 assets =====
FIGPAGE.update({"7.11": 298, "7.12": 298, "7.13": 299, "7.15": 300, "7.16": 300,
                "7.17": 301, "7.18": 302, "7.22": 305})
MANUAL.update({"7.14": (299, 65, 398, 388, 553), "7.19": (303, 65, 443, 388, 573),
               "7.20": (304, 65, 148, 388, 333), "7.21": (304, 65, 390, 388, 560)})
FIGCAP.update({
 "7.11": ("实验室试验台“柔性机器人”", "Laboratory test-bed 'flexible robot'", 9),
 "7.12": ("驱动机器人的液压回路（Nissing, 2002）", "Hydraulic circuit actuating the robot (Nissing, 2002)", 12),
 "7.13": ("液压差动缸", "Hydraulic differential cylinder", 9),
 "7.14": ("测量与仿真的活塞位置阶跃响应之比较（比例位置控制器）", "Measured vs. simulated piston position step responses (proportional position controller)", 12),
 "7.15": ("测量与仿真的速度阶跃响应之比较（位置 P 控制器下）", "Measured vs. simulated velocity step responses (under position P-controller)", 11),
 "7.16": ("测量与仿真的活塞速度阶跃响应之比较（开环系统）", "Measured vs. simulated piston velocity step responses (open-loop system)", 12),
 "7.17": ("仿真：活塞位置阶跃响应（线性比例 vs. 非线性控制器）", "Simulation: piston position step response (linear proportional vs. non-linear controller)", 12),
 "7.18": ("仿真：活塞速度阶跃响应（非线性位置控制器）", "Simulation: piston velocity step response (non-linear position controller)", 11),
 "7.19": ("小缸 HSS 基于输入-输出线性化的级联负载力控制简化算法", "Simplified algorithm of cascade load force control for HSSs with small cylinder", 12.5),
 "7.20": ("活塞位置阶跃响应（比例线性 vs. 非线性控制器）", "Piston position step response (proportional linear vs. non-linear controller)", 12),
 "7.21": ("活塞位置阶跃响应（图 7.20 的放大）", "Piston position step response (zoomed)", 12),
 "7.22": ("非线性控制器的负载压力-力跟踪", "Load-pressure-force tracking for the non-linear controller", 12),
})

b.h2("7.2　小型差动缸的建模与控制", "Modelling and Control of a Small Differential Cylinder")
b.para("第二个案例研究关于用于控制机器人臂的小型差动缸伺服系统（系统参数概览见附录 B.1）的"
       "建模与控制。")
b.h3("7.2.1　系统描述", "System Description")
b.para("下面给出图 7.11 和 7.12 所示实验室试验台的实验结果。该试验台为现实的实验室规模实验"
       "设计，配有用弹簧钢制造的连杆以实现显著的柔性。两/三个旋转关节在闭运动链内由小型静液"
       "差动缸驱动，把驱动的平移变换为关节的转动。对下面的研究，缸被单独安装在一块板上，如"
       "图 7.13 所示。")
fig("7.11"); fig("7.12"); fig("7.13")
b.h3("7.2.2　基于物理的模型", "Physically Based Model")
b.para("为获得仿真和控制设计的模型，已在 MATLAB 中实现微分方程 4.181。为简单起见，忽略泄漏"
       "流、流体质量和阀摩擦；并假设体积模量（初值用式 3.21 的参数）和腔容积在缸两侧相等。"
       "使用了初始摩擦模型参数 σ=175 N·s/m、Fc0=120 N、Fs0=185 N、cs=0.0174 m/s。为使该模型"
       "拟合真实系统，比较计算的与测量的位置阶跃响应。为避免误差积分，系统和模型由增益 "
       "K=30 V/m 的简单比例控制器控制。图 7.14 给出参考位置从 0.05 到 0.15 m 变化的阶跃响应，"
       "这里只见小偏差。图 7.15 给出对应于图 7.14 位置信号的活塞速度。")
fig("7.14"); fig("7.15")
b.para("这些曲线表明，在 0.25 s 后速度降到 0.05 m/s 以下之前，测量与估计信号良好对应。为获得"
       "额外整定信息，使用开环系统对伺服阀输入从 0 到 100% 变化的活塞速度阶跃响应。由于压力"
       "管路是软管，须调整体积模量函数（式 3.21）；一些摩擦力（见图 4.32）参数也须整定（即"
       "适配测量）。结果示于图 7.16。")
fig("7.16")
b.h3("7.2.3　线性控制与非线性控制", "Linear vs. Non-linear Control")
b.para("把基于输入-输出线性化的级联压差-力控制概念（见 6.5 和 6.6 节、图 6.25 和 6.26）应用于"
       "差动缸。下面给出仿真和实验结果。")
b.label("7.2.3.1　仿真结果")
b.para("参考力发生器")
eq("7.1")
b.para("由位置偏差的比例反馈和两个前馈项（补偿（测量的）外力和摩擦力）组成。只考虑静摩擦和"
       "库仑摩擦，忽略黏性摩擦。图 7.17 给出应用 P 控制器和级联非线性控制器所得闭环系统的位置"
       "阶跃响应（参考从 0 到 0.15 m 阶跃）。由该图似乎用非线性控制器无法获得显著改善；然而，"
       "看速度阶跃响应（从 0 到 0.65 m/s 再回到零，图 7.15 和 7.18），可清楚看出两控制器结果的"
       "巨大差别——非线性控制器表现远好于线性控制器。", indent=False)
fig("7.17"); fig("7.18")
b.label("7.2.3.2　实验结果")
b.para("与非线性控制器在仿真中的轻松应用相反，在真实系统上的实现更困难。由于缸小，其动态相对"
       "快，时间常数与被忽略子系统（即阀和管道动态）的相差不远。事实上，由图 7.16 可推断空载缸"
       "的固有频率约 100 Hz，处于应考虑伺服阀和管道动态的区域。计入式 3.82 和数值 E′≈"
       "15×10⁶ N/m²、cv′≈10⁻⁷ m³/(s·√N)、V≈10⁻⁴ m³、ps，对所考虑的缸导出时间常数 Tp 的近似 "
       "Tp < 10 ms（对 0 ≤ pL* ≤ 0.85），与实验结果（见 4.4.2.1 节的图）良好吻合。另一问题源于"
       "该试验台所用 PC 的限制：无法实现小于 1 ms 的采样时间（需要 10–50 μs 区域的采样时间）。")
b.para("为解决这些问题并把概念应用于试验台，把式 6.99（假设 KLi=0，E′A=E′B=:E′，VA=VB=V）和"
       "式 6.129–6.130 的控制律写成如下形式（Bernzen and Riege, 1996）：")
eq("7.2")
b.para("压力动态补偿项 KFL 只含快速的压力相关部分，故假设为常数，即", indent=False)
eq("7.3")
b.para("速度补偿项 Kx2 可近似为", indent=False)
eq("7.4")
b.para("有了这些近似，得到大为简化、易于实现的控制律（对 u ≥ 0）", indent=False)
eq("7.5")
b.para("u < 0 情形的控制律由组合式 6.99、6.129 和 6.130 类似得到（小结见图 7.19）。最后，把"
       "图 7.19 的控制律应用于现已重装回机器人的小型差动缸。图 7.20 和 7.21 给出用（线性）"
       "P 控制器和级联（非线性）控制器所得的典型结果。非线性控制器实现了更好的控制性能"
       "（更小的上升时间和更小的稳态位置误差）。", indent=False)
fig("7.19"); fig("7.20"); fig("7.21")
b.para("用线性概念的受控系统对柔性臂引起的扰动的反应非常敏感；见图 7.21。P 控制器应用可见"
       "大于 1.2 mm 的位置误差，而非线性控制器实现小于 0.25 mm 的偏差。此外，图 7.22 表明非"
       "线性控制器的负载压力-力跟踪工作良好，只在快速阶跃变化区附近见一些偏差。")
fig("7.22")

# ===== sections 7.3-7.5 assets =====
FIGPAGE.update({"7.23": 306, "7.24": 307, "7.25": 307, "7.30": 310, "7.31": 310,
                "7.32": 311, "7.33": 311, "7.34": 312, "7.35": 312, "7.37": 313,
                "7.38": 314, "7.39": 314})
MANUAL.update({"7.26": (308, 65, 53, 388, 266), "7.27": (308, 65, 298, 388, 490),
               "7.28": (309, 65, 53, 388, 258), "7.29": (309, 65, 278, 388, 477),
               "7.36": (313, 65, 53, 388, 239)})
FIGCAP.update({
 "7.23": ("“大缸试验台”", "'Big cylinder test-bed'", 11),
 "7.24": ("摩擦力补偿曲线（Bernzen, 1999）", "Friction force compensation curve (Bernzen, 1999)", 10),
 "7.25": ("非线性控制器的位置控制性能（Bernzen, 1999）", "Position control performance of the non-linear controller (Bernzen, 1999)", 12),
 "7.26": ("不同增益的比例（线性）控制器的位置性能（Bernzen, 1999）", "Position performance of a proportional (linear) controller with different gains (Bernzen, 1999)", 12),
 "7.27": ("对应图 7.25 和 7.26 的位置偏差（放大）（Bernzen, 1999）", "Position deviation (zoomed) corresponding to Figures 7.25 and 7.26 (Bernzen, 1999)", 12),
 "7.28": ("K=200 V/m 线性控制的速度（Bernzen, 1999）", "Velocity for linear control with K=200 V/m (Bernzen, 1999)", 12),
 "7.29": ("非线性控制的速度（Bernzen, 1999）", "Velocity for non-linear control (Bernzen, 1999)", 12),
 "7.30": ("活塞位置（Bernzen, 1999）", "Piston position (Bernzen, 1999)", 12),
 "7.31": ("活塞速度（Bernzen, 1999）", "Piston velocity (Bernzen, 1999)", 12),
 "7.32": ("测量的负载力（Bernzen, 1999）", "Measured load force (Bernzen, 1999)", 12),
 "7.33": ("拆下的混凝土泵静液差动缸", "Dismounted hydrostatic differential cylinder of the concrete pump", 11),
 "7.34": ("实际与参考活塞速度（Nissing, 2002）", "Actual and reference piston velocity (Nissing, 2002)", 12),
 "7.35": ("负载力（Nissing, 2002）", "Load force (Nissing, 2002)", 12),
 "7.36": ("活塞速度及其参考（Nissing, 2002）", "Piston velocity and its reference (Nissing, 2002)", 12),
 "7.37": ("无振动控制的负载力（Bernzen et al., 1999a）", "Load force without vibration control (Bernzen et al., 1999a)", 12),
 "7.38": ("带振动控制的负载力（Bernzen et al., 1999a）", "Load force with vibration control (Bernzen et al., 1999a)", 12),
 "7.39": ("实际与参考活塞速度（Bernzen et al., 1999a）", "Actual and reference piston velocity (Bernzen et al., 1999a)", 12),
})

b.h2("7.3　大型差动缸的控制", "Control of a Big Differential Cylinder")
b.para("本案例研究取自 Bernzen（1999:36-39），处理大型差动缸伺服系统（驱动参数概览见附录 B.1）"
       "的位置控制。再次实验考察 6.6.2.1 节（图 6.25 和 6.26）所给级联压差-力控制的性能，并与用"
       "比例位置控制器所得性能比较。")
b.h3("7.3.1　系统描述", "System Description")
b.para("此应用考虑一个由（大型）差动缸与负载质量耦合组成的试验台。图 7.23 给出试验台的实际"
       "构造和简化原理图。由于压力动态已如 6.6.2.1 节所述被精确线性化，控制设计的主要手段是"
       "选择压差力的参考生成器，故只需选择控制器增益 K。")
fig("7.23")
b.h3("7.3.2　线性控制与非线性控制", "Linear vs. Non-linear Control")
b.para("使用了图 6.26 的状态反馈线性化控制律。用 K=110 s⁻¹ 取得良好结果。系统压力 pS 和油箱"
       "压力 pT 被测量并用于控制律。对参考生成器，采用如下关系")
eq("7.6")
b.para("其中 Kp=200 kN·s/m，Kv=120 kN·s/m。外力由负载质量的加速度力给出", indent=False)
eq("7.7")
b.para("加速度由位置信号的有限差分估计。", indent=False)
b.para("若主要重点是位置跟踪，则静摩擦力是重要因素。为补偿该力，使用了图 7.24 所示的简化"
       "曲线（位置偏差的函数）；函数参数由实验确定，零点周围 1 mm 的位置偏差区域旨在避免极限"
       "环。主要目标是以高位置控制性能产生液压驱动的良好动态行为。")
fig("7.24")
b.para("参考位置由下式给出")
eq("7.8")
b.para("即在 2 s 内把系统从 0.1 定位到 0.4 m。位置参考信号经微分得到参考速度 ẋp,ref(t) 和参考"
       "加速度 ẍp,ref(t)。图 7.25 展示非线性控制器的高性能，即无超调的快速响应。用（线性）"
       "P 控制器所得控制结果示于图 7.26。", indent=False)
fig("7.25"); fig("7.26")
b.para("乍看图 7.25 和 7.26 可能得出非线性控制器不优于线性控制器的结论。然而，考虑图 7.27 给出"
       "的定位误差，可见用非线性概念有显著性能改善。线性控制器的应用产生残留的位置偏差，它可"
       "用更高增益减小，但代价是位置信号有更多超调。振动在速度信号中也可清楚看到（图 7.28）。"
       "与线性控制器相反，非线性控制器的应用导致非常小的位置偏差（<1 mm）和无振动的速度信号"
       "（见图 7.29）。")
fig("7.27"); fig("7.28"); fig("7.29")
b.h2("7.4　柔性机器人的振动阻尼控制", "Vibration Damping Control for a Flexible Robot")
b.para("本案例研究改编自 Nissing 等（1999a），再次考虑图 7.11 的实验室试验台（重装执行器）。"
       "图 7.30–7.32 给出简单 P 控制器与 6.9 节引入的新振动阻尼控制器之间的比较。执行器跟随"
       "参考位置从 0.03 到 0.11 m（约为运行范围的 50%）的阶跃，但对位置（图 7.30）甚至速度"
       "（图 7.31）只见小差别，而图 7.32 的执行器力清楚显示新控制概念的出色性能：振动阻尼控制器"
       "只需约 1 s 即可抑制振动而不恶化位置控制性能。与此相反，比例位置控制器引起强烈振动，"
       "30 s 后才消退。公平地说，线性概念本质上未采取任何避免振动的直接努力。")
fig("7.30"); fig("7.31"); fig("7.32")
b.h2("7.5　混凝土泵的振动阻尼控制", "Vibration Damping Control for a Concrete Pump")
b.para("最后一个案例研究处理真实混凝土泵机器人（见图 2.13）的主动振动控制，改编自 Nissing 等"
       "（1999a,b）。作为对该系统实现控制概念的第一步，拆下一个静液差动缸并在实验室搭建"
       "（见图 7.33）用于实验速度控制器设计，安装了若干测量装置（含压力和位置/速度传感器）。")
fig("7.33")
b.para("按 6.9.3 节设计并实现了一个简化的非线性速度控制器。图 7.34–7.36 给出实验结果。第一个"
       "实验假设幅值 60 kN 的正弦扰动力（真实情况下典型发生），由该扰动力用弹簧-阻尼元件"
       "（式 6.148）计算参考活塞速度，图 7.34 表明速度控制器的跟踪质量足够。第二个实验同样用"
       "弹簧-阻尼元件（式 6.148）计算参考活塞速度，图 7.35 给出所生成的力信号，图 7.36 给出相应"
       "的活塞速度及其参考。")
fig("7.34"); fig("7.35"); fig("7.36")
b.para("最后，把静液差动缸重装回混凝土泵，在真实系统上验证控制概念。最优参数弹簧刚度 c 和"
       "阻尼常数 d 由实验确定（Nissing, 2000, 2002）。图 7.37 给出在 t=0 手动激励末端执行器、"
       "所有连杆水平对齐时无振动控制的缸标准化执行器力变化，可清楚看到弹性连杆振动在 30 s 多"
       "才消退。")
fig("7.37")
b.para("相比之下，图 7.38 给出带主动振动阻尼概念的执行器力，可清楚看到振动在 5 s 内消退；此外，"
       "无振动控制概念时的绝对力变化是用控制概念时活塞力的两倍多。图 7.39 阐明速度控制器的"
       "良好质量：活塞速度令人满意地跟随式 6.148 计算的参考速度，还可看出当力作用于活塞杆时"
       "执行器会顺从（差动缸伸出和缩回一次）。当臂在其固有频率被手动激励时，无振动阻尼情形下"
       "力幅值（以及末端执行器位置）很大；而振动阻尼控制（6.9 节、图 6.40）激活时则不出现："
       "力幅值在每次脉冲时都保持在同一低水平。")
fig("7.38"); fig("7.39")

os.makedirs("parts", exist_ok=True)
b.save("parts/ch07.docx")
print("Saved parts/ch07.docx (COMPLETE: 7.1-7.5)")
