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
MANUAL_EQ = {}   # filled in as sections are translated
for lab, (pg, yc) in MANUAL_EQ.items():
    EQ[lab] = _ink_crop(doc[pidx(pg)], yc, lab)

# ---- figures ----
os.makedirs("ch5_figs", exist_ok=True)
FIGPAGE = {"5.1": 127, "5.2": 129, "5.3": 132, "5.4": 133, "5.5": 134}
MANUAL  = {"5.2": (129, 50, 72, 388, 583), "5.3": (132, 75, 172, 365, 335),
           "5.5": (134, 75, 56, 365, 233)}
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

# ---- (more sections appended in subsequent passes: 5.3 ...) ----

os.makedirs("parts", exist_ok=True)
b.save("parts/ch05.docx")
print("Saved parts/ch05.docx (WIP through 5.2)")
