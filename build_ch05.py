# -*- coding: utf-8 -*-
"""第 5 章 实验建模（辨识）—— 内容构建（WIP，逐节扩充）。
Produces parts/ch05.docx (content-only)."""
import os, re, fitz, hashlib, numpy as np
from hsbook_docx import DocBuilder, extract_equations, SRC_PDF, pidx

CH = 5
PAGES = range(127, 212)

# ---- equations ----
os.makedirs("ch5_eqs", exist_ok=True)
doc = fitz.open(SRC_PDF)
EQ = {}
for pp in PAGES:
    EQ.update(extract_equations(SRC_PDF, pidx(pp), CH, "ch5_eqs"))

def _ink_crop(page, ycentre, label, out_dir="ch5_eqs", dpi=200, gap_mm=2.4, max_mm=80, pad=7):
    words = page.get_text("words")
    left = min(w[0] for w in words); right = max(w[2] for w in words)
    pm = page.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
    arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
    sc = dpi / 72.0
    col = arr[:, int(left*sc):int(right*sc)]
    ink = (col < 128).sum(axis=1); thr = 3
    cy = int(ycentre*sc); H = arr.shape[0]
    maxpx = int(max_mm/25.4*dpi); gap = int(gap_mm/25.4*dpi)
    top = cy; bl = 0
    for r in range(cy, max(0, cy-maxpx), -1):
        if ink[r] > thr: top = r; bl = 0
        else:
            bl += 1
            if bl >= gap: break
    bot = cy; bl = 0
    for r in range(cy, min(H, cy+maxpx)):
        if ink[r] > thr: bot = r; bl = 0
        else:
            bl += 1
            if bl >= gap: break
    box = fitz.Rect(left-pad, top/sc - 2, right+pad, bot/sc + 2)
    path = os.path.join(out_dir, f"eq_{label}.png")
    page.get_pixmap(dpi=dpi, clip=box).save(path)
    return (path, box.width/72*2.54)

# broadened right-margin recovery for labels OCR'd with comma / missing paren
_bpat = re.compile(r"\(?5[.,]\s?(\d+)[a-z]?\)?")
for pp in PAGES:
    page = doc[pidx(pp)]; words = page.get_text("words")
    if not words: continue
    left = min(w[0] for w in words); right = max(w[2] for w in words)
    rmargin = left + 0.78*(right-left)
    for w in words:
        m = _bpat.fullmatch(w[4])
        if m and w[0] > rmargin:
            lab = f"5.{m.group(1)}"
            if lab not in EQ:
                EQ[lab] = _ink_crop(page, (w[1]+w[3])/2, lab)

# equations whose labels did not OCR as tokens at all -> explicit (page, y-centre)
MANUAL_EQ = {"5.16": (139, 72)}   # labels that did not OCR as tokens (page, y-centre)
for lab, (pg, yc) in MANUAL_EQ.items():
    EQ[lab] = _ink_crop(doc[pidx(pg)], yc, lab)

# ---- figures ----
os.makedirs("ch5_figs", exist_ok=True)
FIGPAGE = {"5.1": 127, "5.2": 129, "5.3": 132, "5.4": 133, "5.5": 134, "5.6": 147}
MANUAL  = {"5.2": (129, 50, 72, 388, 583), "5.3": (132, 75, 172, 365, 335),
           "5.5": (134, 75, 56, 365, 233), "5.6": (147, 48, 56, 393, 207)}
TOPCUT  = {}
def _figbox(page, fig):
    words = page.get_text("words")
    left = min(w[0] for w in words); right = max(w[2] for w in words)
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
    path = f"ch5_figs/fig_{fig}.png"; page.get_pixmap(dpi=200, clip=box).save(path); return path

FIGCAP = {
 "5.1": ("辨识任务：确定模型使残差 ε 最小", "Identification task: determine model such that residual ε is minimised", 12),
 "5.2": ("系统辨识过程的示意流程图", "Schematic flowchart of system identification process", 11),
 "5.3": ("PRBS 示例", "An example of a PRBS", 11),
 "5.4": ("PRMS 示例", "An example of a PRMS", 11),
 "5.5": ("啁啾（chirp）信号", "A chirp signal", 11),
 "5.6": ("(a) 串-并联模型结构；(b) 并联模型结构", "(a) Serial-parallel model structures; (b) parallel model structures", 13),
}

# ---- build ----
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

b.h1("第 5 章　实验建模（辨识）", "CHAPTER 5  EXPERIMENTAL MODELLING (IDENTIFICATION)",
     page_break_before=True)
b.para("在第 4 章中，已给出并分析了液压伺服系统的理论模型。液压伺服系统的子系统模型已被"
       "化为适合控制器设计的表示形式。这最终得到了描述系统相关动态与非线性的简单模型，它们"
       "构成灰箱建模的基础。这另外还需要实验建模，即从输入-输出数据导出模型。这种建模方法也"
       "称为统计建模或经验建模，其导出过程称为辨识（identification）。")
b.para("液压伺服系统的模型辨识与验证是本章的主题。除经典辨识方法外，还将论述用于统计建模"
       "（基于模糊和神经网络）的精选方法。")

b.h2("5.1　引言", "Introduction")
b.para("辨识的任务是确定模型参数 θ̂，使模型预测按指定准则尽可能少地偏离测量值；见图 5.1。")
fig("5.1")
b.para("通常采用均方误差作为准则（对 MISO 系统）：")
eq("5.1")
b.para("V(θ̂) 也称为“目标函数”“损失函数”或“性能准则”。式 5.1 中，k 表示离散时间采样"
       "（k = t/T0，T0 为采样周期），ŷ 是估计输出，N 是数据点数。真实系统输出 yu 通常被噪声 e "
       "扰动，得到可测输出 y。", indent=False)
b.para("辨识算法针对辨识数据降低代价 V。同时（或在模型验证期间）针对独立数据确定代价 V，"
       "以检验泛化性质并避免参数过拟合。模型评价方案（串-并联或并联）必须为明确定义的任务"
       "指定（详尽讨论见 5.8.5 节）。")
b.h3("5.1.1　通用辨识流程", "Generic Identification Procedure")
b.para("当试图辨识动态系统（这里是液压伺服系统）的模型时，通常遵循图 5.2 所示的流程，它包括"
       "以下主要步骤：")
b.para("1.　设计并执行实验，涉及激励信号的选择、采样周期的选择、辨识所需数据集的测量与记录，"
       "以及数据的预处理。见 5.2 节。", indent=False)
b.para("2.　选择合适的模型结构（或模型结构集），通常是某阶的微分或差分方程。在此阶段，用户应"
       "基于关于系统的先验知识作出合理选择；作此选择常需大量工程智慧。见 5.3 节和 5.4 节。", indent=False)
b.para("3.　使用某些数学方法（最小化模型输出与过程测量之间的误差）来辨识模型结构并估计模型的"
       "未知参数。见 5.5、5.6、5.8 和 5.9 节。有时可通过执行额外的参数优化来提升模型质量，但这"
       "并非默认的辨识步骤。", indent=False)
b.para("4.　验证（即测试）所得模型，看它就需求而言是否为系统的合适表示；见 5.10 节。若不是，"
       "则须重复步骤 1–3 中的某些步骤。", indent=False)
fig("5.2")
b.para("从验证框返回前面各阶段的路径表明，辨识过程以迭代方式执行：")
b.bullet("返回参数估计的路径。　一般而言，对非线性估计问题难以保证估计算法收敛到全局最优；"
         "这对常用的、数值上非常高效的基于导数的方法尤其如此，可能由局部极小引起。应以不同的"
         "（随机）参数初值重复参数辨识步骤，以降低陷入损失函数（坏的）局部极小的风险。除此"
         "之外，还可应用全局搜索策略，如模拟退火、进化策略和遗传算法；尽管这些方法有望找到"
         "全局最优，但需要巨大的计算量。")
b.bullet("返回模型结构选择的路径。　由于模型结构定义为一组候选模型（或模型族），而人们感兴趣"
         "的是参数数目最少的模型，因此可使用模型选择工具：通过就某些性能度量比较不同候选结构，"
         "可自动提取最优模型结构；见 5.5.5 节和 5.9.1 节。")
b.bullet("返回实验的路径。　若经多次尝试，无论如何选择模型结构似乎都无法得到可接受的模型，"
         "这可能意味着数据材料不足——可能由数据处理不充分或数据集信息不足造成。前一原因很"
         "常见，通常表明输入信号未充分激励系统、运行范围覆盖不够；因此须采集新数据。")
b.para("正如 Söderström 与 Stoica（1989）所指出的，没有万无一失、总能直接得到正确结果的辨识"
       "方法。相反，有许多从实用角度看有用的理论结果。即便如此，用户必须把这些理论的应用与"
       "常识和直觉结合起来，才能得到最合适的结果。下面讨论一些在实践中（尤其在液压中）处理"
       "系统辨识时可能有帮助的实际问题。")
b.h3("5.1.2　线性辨识与非线性辨识", "Linear vs. Non-linear Identification")
b.para("本章其余部分所采取的方法，与 Goodwin 与 Payne（1977）、Ljung 与 Söderström（1987）、"
       "Söderström 与 Stoica（1989）、Isermann（1992）和 Ljung（1999）等教材中关于线性系统"
       "辨识的权威论述非常一致。然而，这些书只略微涉及非线性模型的辨识。直到最近，Haber 与 "
       "Keviczky（1999）和 Nelles（2001）才出版了关于非线性系统辨识的专著。")
b.para("本书力图描述那些实际已成功应用于液压系统的（线性和非线性）方法，而不给出陈述的数学"
       "证明。除经典辨识技术外，模糊模型和人工神经网络也可用于描述液压伺服系统的非线性动态"
       "系统，故本节也予以论述。本书中关于模糊系统和神经网络的小节无意详尽，而是聚焦于所"
       "提出众多概念中精选的少数；除方法外，还论述实际应用方面。")
b.para("推荐读者参阅一些教材以作更广或更深的学习：")
b.bullet("Babuška（1998）、Kroll（1997）用于模糊辨识与建模（本书推荐参考），Driankov 等"
         "（1993）用于模糊逻辑与控制入门。")
b.bullet("Hirota（1993）、Zimmermann 与 von Altrock（1994）用于模糊逻辑、建模与控制成功应用"
         "的汇集。")
b.bullet("Nørgaard 等（2000）用于基于神经网络的建模与控制（本书推荐参考），Hertz 等（1991）"
         "和 Haykin（1999）用于神经计算入门。")
b.bullet("Hunt 等（1995）用于关于神经网络方法与应用的有用文献汇集。")
b.h3("5.1.3　在线辨识与离线辨识", "Online vs. Offline Identification")
b.para("由于液压伺服系统中大多数参数在运行期间不变化，一种自然的做法是离线进行辨识，并在"
       "运行前相应地调整伺服控制。这种方法常被采用，其优点是可避免许多参数可辨识性问题：可"
       "精心设计一系列实验，使每个实验中单个性质清晰可观测，直到所有感兴趣的参数都能由累积"
       "信息准确推断。")
b.para("尽管这里建议在有其他足够解决方案时避免在线辨识算法，但有一些理由可能促使人们去处理"
       "在线辨识所隐含的问题，例如：")
b.bullet("液压伺服系统中某些动态参数实际上并非常数，如温度相关的体积模量。")
b.bullet("在线辨识的问题大体上是可解的。")
b.bullet("在线辨识方案最终给出一种更一般的方法，也可专门化为离线辨识任务。")
b.para("自适应控制就是这样一种应用的例子，其中在线辨识模型（与测量采集同时进行）是有用的。"
       "该主题由 Isermann 等（1992）、Åström 与 Wittenmark（1995）和 Landau 等（1998）广泛"
       "论述。此外，有许多教材论述在线（递推）辨识，如 Goodwin 与 Payne（1977）、Söderström "
       "与 Stoica（1989）、Johansson（1993）和 Ljung（1999）；Ljung 与 Söderström（1987）专门"
       "撰写了递推辨识的教材。")

b.h2("5.2　预辨识过程", "Pre-identification Process")
b.para("对（非线性）系统的辨识，恰当地定义待辨识系统的类型很重要。除一些预计算和所采用的"
       "系统结构外，输入-输出行为的刻画非常重要；其中，实验中所用信号的类型起重要作用，因此"
       "也讨论非线性系统动态的激励。显然，在预辨识阶段，没有合理而良好的数据记录就做不了"
       "什么。")
b.h3("5.2.1　输入信号的设计", "Design of Input Signals")
b.para("在线性系统辨识领域，只含两个幅值电平的伪随机二进制信号（PRBS）被广泛使用；见图 5.3。"
       "然而，Leontaritis 与 Billings（1987a）表明，对非线性系统，这类激励信号可能丧失可"
       "辨识性。")
fig("5.3")
b.para("对非线性系统，重要的是输入信号中要表现出所有（感兴趣的）幅值和频率及其所有组合"
       "（这被称为维数灾难，curse of dimensionality）。因此推荐其他类型的随机激励信号，如：")
b.bullet("具有高斯或均匀分布的独立序列。")
b.bullet("伪随机多电平信号（PRMS），其电平在每第 Nr 个采样时刻或随机时刻改变。")
b.bullet("啁啾（chirp，或多正弦）信号。")
b.label("5.2.1.1　伪随机多电平信号（Pseudo-random Multi-level Signals）")
b.para("设 v(k) 是方差为 σv² 的白噪声过程。PRMS（也称幅值调制的 PRBS）通过把同一（幅值）值"
       "保持 Nr 步（增大时钟周期）得到，即：")
eq("5.2")
b.para("其中 int(x) 是 x 的整数部分。引入一个额外的（随机）变量来决定何时改变电平，得到该信号"
       "的一种推广（Nørgaard 等, 2000）：", indent=False)
eq("5.3")
b.para("显然，若 a 取接近 1，输入将在长区间内保持恒定，因而具有低频特性。PRMS 的示例示于"
       "图 5.4。关于 PRMS 的生成与特性的详细信息，参阅 Haber 与 Keviczky（1999:639–710）。", indent=False)
fig("5.4")
b.para("实践经验表明，若把幅值变化的持续时间（或保持时间）选为两个事实之间的折中，则可获得"
       "最佳模型性能：一方面，持续时间必须足够长以对输出产生影响；另一方面，过长的时间不会"
       "给出关于系统的更多动态信息。因此，经验法则是：合适的保持时间应接近系统阶跃响应的"
       "整定时间。")
b.label("5.2.1.2　啁啾信号（Chirp Signals）")
b.para("啁啾信号是频率逐渐增加（从 ωstart 开始、到 ωend 结束）的正弦信号（Franklin 等, 1990）：")
eq("5.4")
b.para("其中", indent=False)
eq("5.5")
b.para("图 5.5 给出这样一个啁啾信号。把该信号应用于非线性系统时，应针对不同偏置值（u0）和"
       "幅值（a）的若干组合重复使用。", indent=False)
fig("5.5")
b.para("液压系统辨识的经验表明，PRMS 是最合适的输入信号选择；它们就是比例如使用啁啾信号"
       "产生更好的模型；详见 Senger 与 Jelali（1996）。")
b.h3("5.2.2　预计算", "Pre-computations")
b.label("5.2.2.1　采样间隔的选择（Choice of Sampling Interval）")
b.para("为系统辨识选择最佳采样间隔是折中许多因素的结果：")
b.bullet("若辨识实验的总时间区间固定，宜选短采样间隔，因为这样可覆盖系统更多的工作点（即"
         "幅值-频率组合）。但采样间隔相对于所考虑系统的动态不应太短，以避免因相邻测量之间仅有"
         "微小变化而导致参数估计严重数值病态。")
b.bullet("若数据点总数固定，则采样间隔须通过折中选择：若很大，数据将含很少关于高频动态的信息；"
         "若很小，扰动可能有相对大的影响，且数据将含很少关于低频动态的信息。")
b.bullet("若辨识以控制系统设计为最终目的，会涉及某些其他方面。例如，低采样间隔允许快速跟踪和"
         "更平滑的控制输入；然而，快速采样的模型常为非最小相位（Åström and Wittenmark, 1997）。")
b.bullet("很短的采样间隔可能使极点过剩为二或更多的系统成为非最小相位；这种效应在设计调节器时"
         "导致特殊问题。")
b.para("作为粗略经验法则，可把采样间隔选为系统阶跃响应整定时间（或所关注时间常数）的 "
       "10–20%。而且，把采样间隔选得太大往往比太小糟糕得多（Söderström and Stoica, 1989）。")
b.para("对线性系统有一些经验法则；利用阶跃响应的特征值，建议从以下区间选择采样时间 T0：")
eq("5.6", "5.7", "5.8", "5.9")
b.para("其中 T63 和 T95 分别是阶跃响应达到稳态值 63% 和 95% 后的时间段。", indent=False)
b.para("Reuter（1995）通过熵分析为某液压伺服系统（见 7.1 节）提出 0.86 至 1.3 ms 之间的最优"
       "采样间隔。因此，对液压伺服系统，采样间隔应选在 1–2 ms 范围内，这是当今的常见做法。"
       "然而，采样时间的正确值取决于手头液压系统的规模和动态。")
b.label("5.2.2.2　数据的准备（Preparation of Data）")
b.para("当用所选输入序列从辨识实验采集到数据后，它们不大可能处于可立即用于辨识算法的状态。"
       "事实上，原始数据常含测量误差和其他不应纳入模型的信息。")
b.bullet("预滤波（prefiltering）常为必要，以避免混叠并从测量信号中去除噪声、周期性扰动、偏置和"
         "漂移。采样前应使用模拟抗混叠（低通）滤波器，其带宽应小于采样频率。")
b.bullet("从数据集中去除离群点（或坏数据）（或代之以插入输出信号的内插值）可能必要。若不去除，"
         "离群点会显著影响估计模型——它们往往在预测误差序列中表现为尖峰，因而对损失函数有大的"
         "贡献。然而，从数据集中去除某些点或时间区间只对静态数据可行，否则会引起暂态；因此，"
         "对动态系统，为得到更好的数据集，重新进行实验可能更可取。")
b.bullet("强烈推荐去除均值并把所有信号缩放到相同方差。事实上，缩放使估计算法数值稳健、收敛"
         "更快，并就是趋于给出更好的模型质量。通常，在辨识前把测量的输入 u(k) 和输出 y(k) 序列"
         "缩放为零均值和单位方差（Haber and Keviczky, 1999:399；Nørgaard, 2000a）：")
eq("5.10", "5.11")
b.para("（带上横线的 y、E{·}、(‾) 分别表示归一化值、期望值和均值；σ 是相应信号的标准差。）", indent=False)

b.h2("5.3　模型结构概览", "Overview of Model Structures")
b.para("辨识过程的关键步骤是决定一个模型结构，并在其中寻找一个好的模型。若给定了模型结构，"
       "系统辨识过程就化为参数估计问题，在大多数情况下这是个次要问题。实践中，通常会测试若干"
       "结构，辨识过程实际上变成在这些不同结构所得模型之间评价与选择的过程（Ljung, 1993）。"
       "另一方面，显然坏的模型结构无论可用数据的数量和质量如何、无论所选参数估计方法如何，"
       "都不可能产生好的模型。")
b.para("因此，第一个问题是判断系统是否容许标准线性模型描述（如 ARX 模型，见 5.3.2 节），还是"
       "必须构造量身定制的（非线性）模型集。这一判断可基于关于系统的先验知识，或基于非线性"
       "检验方法的应用；该主题的综述见 Billings 与 Fakhouri（1978）、Billings 与 Voon（1983）、"
       "Haber（1995）和 Haber 与 Keviczky（1999:399–483）。")
b.para("在线性情形下，由于问题简单且有许多标准算法和软件包可用，快速成功的机会很大。在非"
       "线性情形下，必须先获得某些物理洞见才能估计模型，或寄望于非线性黑箱结构能捕捉非线性"
       "动态。这一问题显然与应用相关，因此文献中不常讨论。故本书主要聚焦于此，为解决这一难题"
       "作出贡献。然而，必须充分强调：系统辨识（尤其是非线性模型辨识）成功的关键在于思考、"
       "直觉和洞见，这永远不可能被自动化模型构造所取代。")
b.para("为简单起见，下面大多数方程针对 SISO 系统给出；然而推广到 MIMO 系统是直截了当的。")
b.h3("5.3.1　引言性说明与定义", "Introductory Remarks and Definitions")
b.para("在非线性系统辨识领域，可辨识出两种主要倾向（Stoica and Söderström, 1982）：第一种是用"
       "非常一般的描述来表示非线性系统，第二种是对某些类别的非线性系统使用某些特定的刻画。")
b.para("除一般描述与特定描述的区分外，构造给定过程数学模型的问题还有三种不同的处理方式"
       "（Sohlberg, 1998）。通常，系统模型或基于过程的完整知识——称为“白箱”模型，或主要基于"
       "实验数据——即“黑箱”模型。白箱模型通常用作仿真模型，一般是连续且非线性的。在黑箱"
       "建模与白箱建模之间有一个灰色地带，其中有一些物理洞见可用，但若干参数仍待从观测数据"
       "确定；这时使用“灰箱”模型方法。")
b.para("这些建模原理与“灰箱”建模的区别在于系统地使用过程的部分先验知识和实验数据。也就是说，"
       "黑箱建模只需辨识，白箱建模只需物理建模，而灰箱建模既需物理建模又需参数估计。实践中，"
       "是建模的实际目的和背景决定应选择哪种模型。")
b.label("5.3.1.1　白箱结构（White-box Structures）")
b.para("为给定过程构造数学模型的一种自然方式是白箱建模。它基于这样的预设：过程可完全由先验"
       "知识和物理洞见描述，即由数学方程（如微分方程、代数方程、逻辑关系及类似方程）描述。"
       "白箱模型在液压伺服系统领域广泛存在，如第 4 章所述。人们常被引向状态空间形式（一组一阶"
       "常微分方程）：")
eq("5.12")
b.para("其中 x 表示状态向量，u 输入向量，θ（未知）参数向量，y 输出向量。一般而言，参数向量由"
       "未知模型参数向量 p 和未知初始状态向量 x0 组成，即：", indent=False)
eq("5.13")
b.para("从化学和物理原理建模的优点是：它给出对系统行为的洞见，不同参数和变量有物理解释，"
       "系统变化可相对容易地测试，且由于不需要运行数据，甚至可在设计阶段进行。缺点是构造这种"
       "模型代价高（困难且耗时）。作为折中，数学建模常与实验结合以提高模型精度，并增强对随后"
       "用于控制设计的模型的信心。这直接引向灰箱建模。")
b.label("5.3.1.2　黑箱结构（Black-box Structures）")
b.para("为给定过程构造数学模型的另一种方式基于这样的思想：把过程视为完全未知，且不必使用任何"
       "反映过程物理结构的模型结构。相反，用一族标准模型中的一个模型来描述过程。已知这类模型"
       "族有良好的灵活性，过去已被成功使用。然后用过程实验数据估计（未知）模型参数，模型只"
       "给出过程的输入-输出关系。黑箱建模通常用于底层化学-物理描述复杂和/或不确定的过程，如"
       "液压伺服系统中的伺服阀。此外，黑箱模型常用于结合自适应控制和模型预测控制对工业过程"
       "建模。")
b.para("非线性系统黑箱建模的一些综述由 Haber 与 Keviczky（1976）、Mehra（1979）、Billings"
       "（1980）和 Sjöberg 等（1995）给出。")
b.para("与 Sjöberg 等（1995）、Ljung（1999）及许多其他研究者一致，任何（SISO）动态系统在离散"
       "时刻的输出都可在数学上描述为过去输入和输出的函数，即：")
eq("5.14")
b.para("其中 y(k) 是观测输出，φ 是过去量的向量（通常称为回归向量），θ 是未知参数向量。e(k) 是"
       "噪声项，它解释了下一个输出 y(k) 不会是过去数据的精确函数这一事实。辨识的目标是用一个"
       "预测器（模型）来逼近真实的输入-输出关系：", indent=False)
eq("5.15")
b.para("它使观测输出与预测输出之间的误差最小。利用式 5.15，基于截至时刻 k 可用的信息预测 "
       "(k+1) 之后的未来输出值（在确定性情形下假设扰动未来不影响系统）。为简化记号，"
       "ŷ(k+j|k) 将被记为 ŷ(k+j)。", indent=False)
b.para("于是，模型选择问题一般可视为由两个设计任务组成：")
b.bullet("从过去信息中选择回归向量 φ；")
b.bullet("选择非线性函数 g。")
b.para("回归量选择的可能性将在 5.3.2 节和 5.3.3 节讨论。关于非线性函数 g 的性质，有若干流行的"
       "选择（如经典多项式、Volterra 展开、核估计器、小波网络、径向基网络、B 样条、多层网络、"
       "模糊模型）。所有这些都属于参数化函数族 g(φ,θ)，可写成函数展开（function expansions）"
       "（Volterra 级数模型只适合小规模问题，因为参数/回归量数目通常过于庞大）：")
eq("5.16")
b.para("其中基函数 fi(φ, βi, γi) 可用不同方式构造。事实上，式 5.16 的展开起着统一框架的作用，"
       "用于研究大多数非线性黑箱模型结构（Ljung, 1999）。", indent=False)
b.label("5.3.1.3　灰箱结构（Grey-box Structures）")
b.para("对许多工业过程（如第 4 章提到的液压伺服系统），只有关于过程结构和/或参数的不完整知识"
       "可用。因此灰箱模型适合这类过程。由于灰箱模型设计既需物理建模又需参数估计，其开发可能"
       "比黑箱模型更昂贵，即构造灰箱模型可能比黑箱模型耗时更长（灰箱构造步骤的更多细节见 "
       "Sohlberg, 1998）。另一方面，灰箱建模产生过程的更好模型，它们比黑箱模型更透明/物理上"
       "更可解释、泛化性质更好；于是过程可被更高效地控制，所产产品的质量可被改善。该主题的"
       "进一步讨论见 Kroll（2000）。")
b.para("实际上，液压伺服系统中提出的非线性辨识问题是灰箱建模的典型例子，因为有物理洞见可用，"
       "但若干参数仍待从观测数据确定。这里应区分两个子情形：")
b.bullet("补充物理建模。　灰箱建模方法的第一个有趣之处是从所辨识参数重建底层物理量，因为所"
         "辨识参数有物理解释。")
b.bullet("半物理建模。　利用物理洞见来提示测量数据信号（即回归量）的某些（非线性）组合和/或"
         "变换；然后把这些新信号交给黑箱性质的模型结构。")
b.label("5.3.1.4　混合模型（Hybrid Models）")
b.para("表示非线性系统最流行的方法之一是混合模型（Ljung, 1993），即把线性动态块与一个或多个"
       "静态非线性块组合的模型，如 Hammerstein 模型（静态非线性元件后接线性系统）和 Wiener "
       "模型（线性系统后接静态非线性元件）。注意，“混合模型”一词定义不严，文献中用于差异"
       "很大的概念。")
b.para("从系统辨识角度看，Hammerstein 模型最具吸引力。相反，Wiener 模型的辨识更困难，因为"
       "非线性的输入不可测因而未知，且线性动态仍待辨识。")
b.para("暂且把注意力限于主导静态非线性，可容易看出：伺服阀模型（见图 4.6）是 Wiener 型，执行器"
       "模型（见图 4.11）是 Hammerstein 型，而三级伺服阀模型（见图 4.8）是更一般模型结构的典型"
       "例子，可用描述函数（Describing Function）理论刻画（Atherton, 1975；Föllinger, 1993）。"
       "描述函数方法及其在频域非线性液压系统辨识中的应用的深入论述见 van Schothorst（1997）。")
b.para("尽管该方法已成功应用于液压伺服系统部件（伺服阀、执行器、管道）的辨识，但我们不认为它"
       "会在实际实现中有用——它是一种非常特殊且相对复杂的辨识例程，故不再进一步考虑。")
b.para("近来系统辨识中特别受关注的是构思能处理动态效应（由微分/差分方程描述）和逻辑约束（系统"
       "的“如果与但是”）的混合模型结构，即模糊系统或人工神经网络。近年来该领域已有相当深入"
       "的工作，现已有许多关于这类混合模型结构的具体结果，其中一些将在 5.4.2 节和 5.4.3 节"
       "给出。")
b.label("5.3.1.5　参数线性可参数化性（Linear Parameterisability）")
b.para("无论模型结构应当如何，若它对参数是线性的，则非常有利。模型对其参数的线性性意味着："
       "可通过求解线性方程组一步找到参数，而不必使用非线性迭代优化算法。这类问题非常有吸引力："
       "估计问题大为简化，解唯一（即不存在局部极小问题），且可用经典最小二乘求解器求得"
       "（见 5.5.2 节）。这种参数线性的模型结构可写为：")
eq("5.17")
b.para("通常，液压伺服系统基于物理的模型实际上对参数是非线性的，但某些简化可导致参数线性的"
       "子模型，如 5.7 节所述。", indent=False)
b.h3("5.3.2　线性模型结构回顾", "Review of Linear Model Structures")
b.para("为对模型结构（尤其是回归量）的选择获得一些指导，下面遵循 Sjöberg 等（1995）和 Ljung"
       "（1999）回顾线性情形。")
b.label("5.3.2.1　输入-输出模型（Input-Output Models）")
b.para("实践中常用的线性黑箱结构都是如下一般族的变体：")
eq("5.18")
b.para("它们用不同方式选取系统的“极点”、用不同方式描述噪声特性。式 5.18 中，q 表示后移"
       "（或延迟）算子，它对信号 x(k) 的作用为：", indent=False)
eq("5.19")
b.para("其中 τ 是采样周期的整数倍（即动态含 τ 个采样的延迟；本书中无延迟系统定义为 τ = 0）。"
       "A(q)、B(q)、C(q)、D(q) 和 F(q) 是 q⁻¹ 的多项式，阶数分别为 n、m、p、t、r：", indent=False)
eq("5.20")
b.para("式 5.18 可改写为")
eq("5.21")
b.para("与式 5.21 相关的最优预测器由下式给出：")
eq("5.22")
b.para("它可表示为“伪线性”回归形式（推导见 Ljung, 1999:88–90）：", indent=False)
eq("5.23")
b.para("其参数向量为", indent=False)
eq("5.24")
b.para("回归向量为", indent=False)
eq("5.25")
b.para("其中 w(k) 和 v(k) 定义为", indent=False)
eq("5.26", "5.27")
b.para("式 5.23 在数学上等价于（下文将常用此式）：", indent=False)
b.para("式 5.22 描述的特例称为：")
b.bullet("带外部输入的自回归（ARX）模型（C=D=F=1）。从黑箱视角看这是“完整的”线性模型，即当"
         "多项式阶数趋于无穷时，它能描述所有线性系统（包括其噪声特性）。唯一缺点是为容纳噪声"
         "描述，多项式阶数可能须取得比动态所需的更大。")
b.bullet("带外部输入的自回归滑动平均（ARMAX）模型（D=F=1）。这是 ARX 模型最知名的改型，其中"
         "噪声模型被赋予“自己的参数”。")
b.bullet("有限脉冲响应（FIR）模型（A=C=D=F=1）。这是最简单的动态模型，是对延迟输入信号的线性"
         "回归；但注意 m 可能相当大，且不直接与系统的阶数相关。")
b.bullet("输出误差（OE）模型（A=C=D=1）。OE 模型能描述所有线性系统（当多项式阶数趋于无穷），"
         "但不能描述加性噪声的特性。主要优点是通常需要较少的回归量即可得到好的逼近；然而关于 "
         "θ 的最小化变得更复杂，必须迭代求解。")
b.bullet("Box-Jenkins（BJ）模型（A=1）由 Box 与 Jenkins（1970）提出并论述。它是带噪声模型额外"
         "自由度的 OE 模型，即加性扰动可以是任何有色扰动（而不只是白噪声）。BJ 模型非常灵活，"
         "但需要估计大量参数，故实践中很少使用。")
b.bullet("当 A(q) 含因子 1−q⁻¹ 时，模型称为带外部输入的自回归求和滑动平均（ARIMA(X)）。这类"
         "模型适合描述漂移和非平稳扰动（或动态中甚至含积分器的过程）（Söderström and Stoica, "
         "1989）。")
b.para("在这一般情形下，回归量（即回归向量 φ 的元素）由下列给出：")
b.bullet("u(k−i)：过去输入（与 B 多项式相关）。")
b.bullet("y(k−i)：过去测量输出（与 A 多项式相关）。")
b.bullet("ŷu(k−i|θ)：仅由过去 u 仿真的输出（与 F 多项式相关）。")
b.bullet("ε(k−i|θ) = y(k−i)−ŷ(k−i|θ)：过去预测误差（与 C 多项式相关）。")
b.bullet("εu(k−i|θ) = y(k−i)−ŷu(k−i|θ)：过去仿真误差（与 D 多项式相关）。当回归向量中不以任何"
         "形式涉及观测输出时，ŷu(k) 为模型输出。注意，当 A≠1 时，“仿真输出”指量 A(q)y(k)。")
b.para("例 5.1。　流行的 ARX 模型的预测器取如下形式：")
eq("5.28")
b.para("记住式 5.20 中的多项式，ARX 模型可等价地写成一步超前预测器的形式", indent=False)
eq("5.29")
b.para("其中", indent=False)
eq("5.30")
b.label("5.3.2.2　状态空间模型（State-space Models）")
b.para("在状态空间形式中，输入、噪声和输出之间的关系用借助辅助状态向量 x 的一阶微分或差分"
       "方程组来表示。在 Kalman（1960）关于预测和线性二次控制的开创性工作之后，线性系统的"
       "状态空间描述成为日益占主导的方法。如下形式的（一般）线性状态空间描述（随机模型）")
eq("5.31")
b.para("是迄今讨论的输入-输出模型结构的一种广泛使用的替代。v(k) 和 w(k) 假设为零均值的独立"
       "随机变量序列（通常分别称为“过程噪声”和“测量噪声”），其协方差为", indent=False)
b.para("此类系统的最优一步超前预测器是卡尔曼滤波器（Kalman filter）")
eq("5.32")
b.para("其滤波增益矩阵为", indent=False)
eq("5.33")
b.para("其中 S 表示 Riccati 方程的半正定解", indent=False)
eq("5.34")
b.para("式 5.33 的预测滤波器可改写为所谓的状态空间新息形式（SSIF）：")
eq("5.35")
b.para("由于预测滤波器可写为（Söderström and Stoica, 1989；Ljung, 1999）", indent=False)
eq("5.36")
b.para("SSIF 与一般输入-输出形式（ARMAX，式 5.22）之间的关系成立：", indent=False)
eq("5.37")
b.para("与 5.3.2.1 节引入的输入-输出模型相比，对系统物理机理的洞见更易纳入状态空间模型。此外，"
       "状态空间回归量在其内部结构上受限更少。这再次意味着，用状态空间模型可能以更少的回归量"
       "得到更高效的模型（Sjöberg 等, 1995）。换言之，状态空间模型能表示比输入-输出模型更广"
       "范围的动态系统。", indent=False)
eq("5.38")
b.para("此外，状态空间模型还有以下优点（Chou and Maciejowski, 1997）：(i) 因果性内建于模型"
       "结构；(ii) 一般而言，只要系统模型为状态空间形式，就有用于系统变换、简化和分析以及在"
       "观测器/滤波器和控制器综合中利用模型的最佳、最可靠的数值算法。", indent=False)
b.h3("5.3.3　非线性输入-输出模型", "Non-linear Input-output Models")
b.para("遵循（非线性）系统辨识文献中的命名（Chen 等, 1990a,b；Chen and Billings, 1992；Sjöberg "
       "等, 1995），下面给出最广为人知的（输入-输出）结构。")
b.para("NARMAX 模型表示 ARMAX 模型的非线性版本，是输入-输出模型的一般形式（Chen and "
       "Billings, 1992），可在数学上描述为：")
eq("5.39")
b.para("NARX 模型与 NARMAX 模型不同，不含随机输入。NARX 模型可在数学上表示为：")
eq("5.40")
b.para("NFIR 模型是 NARMAX 模型的简化版本，只含观测输入：")
eq("5.41")
b.para("NOE 模型使用模型的输出（而非观测输出）作为回归量。NOE 模型由下式支配：")
eq("5.42")
b.para("NBJ 模型可在数学上描述为：")
eq("5.43")
b.para("由于 NOE、NBJ 和 NARMAX 模型的回归量含来自模型自身的过去信息，它们也被归类为"
       "（外部）递归网络。", indent=False)
b.para("例 5.2。　广泛使用的多项式 NARX 模型（也称 Kolmogorov-Gabor 多项式模型）可表示为")
eq("5.44")
b.para("以多项式系数作为未知（待估计）参数。由于这类模型复杂度高，只应与结构选择算法（如 "
       "Kortmann, 1989 所提出的）结合使用。", indent=False)
b.label("5.3.3.1　串-并联模型与并联模型（Serial-parallel vs. Parallel Model）")
b.para("模型的动态行为本质上受输出反馈回网络方式的影响。文献中常讨论的两种方法是串-并联模型"
       "（NARX 型）和并联模型（NOE 型）；见图 5.6。在并联模型中，模型与系统之间（对输入和"
       "输出）完全并行，而串-并联模型只对输入并行。")
fig("5.6")
b.para("若专门关注仿真模型（或长时域预测模型），原则上最好考虑 NOE 模型，因为它们被辨识为"
       "提供最优仿真器。然而，这类模型的辨识比辨识 NARX 模型更困难、更耗时。（在某些文献中，"
       "模型按串-并联模型辨识，却按并联模型仿真；另见 5.4.2.3 节和 5.8.5.1 节的讨论。）")
b.label("5.3.3.2　滞后空间的确定（Determination of Lag Space）")
b.para("正确滞后空间的选择（即用作回归量的延迟信号的动态阶数 n 和 m）对模型质量起决定性作用，"
       "同时也是个难题。除试错和关于系统的先验知识外，可靠地自动确定滞后空间的策略很少。最"
       "著名的方法是使用所谓的 Lipschitz 商（He and Asada, 1993 提出）：")
eq("5.45")
b.para("对 i = 1,…,N，j = 1,…,N 且 i≠j，下标“(n)”表示回归量的数目。Lipschitz 阶指标定义为 c 个"
       "（c ∈ [0.01N, 0.02N]）最大 Lipschitz 商的几何平均：", indent=False)
eq("5.46")
b.para("对不同的滞后选择（n 或 m）评估该阶指标并把它绘为各参数的函数，便可把回归量的最优数目"
       "选为曲线的“拐点”。", indent=False)
b.h3("5.3.4　非线性状态空间模型", "Non-linear State-space Models")
b.para("与式 5.12 的连续时间描述类似，MIMO 非线性动态系统的状态空间模型可表示为")
eq("5.47")
b.para("其中 v(k) 和 w(k) 是适当维数的零均值扰动和噪声向量。此情形下模型由函数 f 和 h 定义。", indent=False)

# ---- (more sections appended in subsequent passes: 5.4 ...) ----

os.makedirs("parts", exist_ok=True)
b.save("parts/ch05.docx")
print("Saved parts/ch05.docx (WIP through 5.3)")
