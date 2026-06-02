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

# ---- (more sections appended in subsequent passes: 7.2 ...) ----

os.makedirs("parts", exist_ok=True)
b.save("parts/ch07.docx")
print("Saved parts/ch07.docx (WIP through 7.1)")
