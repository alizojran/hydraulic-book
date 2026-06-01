# -*- coding: utf-8 -*-
"""Build a Chinese translation of NASA TN D-5388 as a .docx file.
中文为主 + 关键术语中英对照。
"""
import os
import tempfile
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC_PDF = ("Analysis of dynamic performance limitations of fast response "
           "(150 to 200 Hz) electrohydraulic servos.pdf")
LATIN = "Times New Roman"
CJK = "宋体"
CJK_BOLD = "黑体"

# ---------- extract figures and Table I image from the source PDF ----------
# (figname, page_index, ytop, ybot, xleft, xright) as fractions of the page
_CROPS = [
 ("fig01", 4, 0.05, 0.35, 0.04, 0.97), ("fig02", 5, 0.39, 0.94, 0.08, 0.96),
 ("fig03", 7, 0.03, 0.41, 0.04, 0.97), ("fig04", 7, 0.42, 0.91, 0.08, 0.94),
 ("fig05", 9, 0.49, 0.94, 0.04, 0.98), ("fig06", 11, 0.52, 0.97, 0.08, 0.96),
 ("fig07", 12, 0.15, 0.57, 0.08, 0.96), ("fig08", 13, 0.51, 0.97, 0.04, 0.98),
 ("fig09", 15, 0.02, 0.44, 0.04, 0.98), ("fig10", 17, 0.51, 0.97, 0.04, 0.98),
 ("fig11", 19, 0.05, 0.48, 0.08, 0.98), ("fig12", 20, 0.07, 0.58, 0.04, 0.96),
 ("fig13", 22, 0.07, 0.53, 0.08, 0.96),
]
FIG = tempfile.mkdtemp(prefix="tn_d5388_figs_")
_doc = fitz.open(SRC_PDF)
for name, idx, yt, yb, xl, xr in _CROPS:
    pg = _doc[idx]; rc = pg.rect
    clip = fitz.Rect(rc.x0 + xl*rc.width, rc.y0 + yt*rc.height,
                     rc.x0 + xr*rc.width, rc.y0 + yb*rc.height)
    pg.get_pixmap(dpi=200, clip=clip).save(os.path.join(FIG, name + ".png"))
_doc.close()

doc = Document()

# ---------- page setup ----------
sec = doc.sections[0]
sec.page_height = Cm(29.7)
sec.page_width = Cm(21.0)
for m in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
    setattr(sec, m, Cm(2.54))
CONTENT_W = sec.page_width - sec.left_margin - sec.right_margin

# ---------- default style ----------
normal = doc.styles["Normal"]
normal.font.name = LATIN
normal.font.size = Pt(12)
normal._element.rPr.rFonts.set(qn("w:eastAsia"), CJK)
normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
normal.paragraph_format.space_after = Pt(0)

def style_heading(style_id, latin_size, cjk_font):
    st = doc.styles[style_id]
    st.font.name = LATIN
    st.font.size = Pt(latin_size)
    st.font.bold = True
    st.font.color.rgb = RGBColor(0, 0, 0)
    rpr = st.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), cjk_font)

style_heading("Heading 1", 15, CJK_BOLD)
style_heading("Heading 2", 13, CJK_BOLD)

def set_run(run, latin=LATIN, cjk=CJK, size=None, bold=None, italic=None, color=None):
    run.font.name = latin
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), latin)
    rfonts.set(qn("w:hAnsi"), latin)
    rfonts.set(qn("w:eastAsia"), cjk)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color

# ---------- math markup parser ----------
def add_math_runs(p, markup, size=12, color=None):
    """Render a string with _{...} subscripts and ^{...} superscripts."""
    i = 0
    n = len(markup)
    buf = ""
    def flush():
        nonlocal buf
        if buf:
            r = p.add_run(buf)
            set_run(r, size=size, color=color)
            buf = ""
    while i < n:
        ch = markup[i]
        if ch in "_^" and i + 1 < n and markup[i+1] == "{":
            flush()
            j = markup.index("}", i+2)
            content = markup[i+2:j]
            r = p.add_run(content)
            set_run(r, size=size, color=color)
            if ch == "_":
                r.font.subscript = True
            else:
                r.font.superscript = True
            i = j + 1
        else:
            buf += ch
            i += 1
    flush()

def add_equation(markup, number=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    pf.space_before = Pt(6)
    pf.space_after = Pt(6)
    pf.tab_stops.add_tab_stop(int(CONTENT_W / 2), WD_TAB_ALIGNMENT.CENTER)
    pf.tab_stops.add_tab_stop(int(CONTENT_W), WD_TAB_ALIGNMENT.RIGHT)
    set_run(p.add_run("\t"))
    add_math_runs(p, markup)
    if number:
        r = p.add_run("\t(" + number + ")")
        set_run(r)
    return p

# ---------- block helpers ----------
def h1(cn, en=None):
    p = doc.add_heading(level=1)
    r = p.add_run(cn)
    set_run(r, latin="Arial", cjk=CJK_BOLD, size=15, bold=True, color=RGBColor(0,0,0))
    if en:
        p.add_run("  ")
        r2 = p.add_run(en)
        set_run(r2, latin="Arial", cjk=CJK_BOLD, size=10.5, bold=False,
                color=RGBColor(0x55,0x55,0x55))

def h2(cn, en=None):
    p = doc.add_heading(level=2)
    r = p.add_run(cn)
    set_run(r, latin="Arial", cjk=CJK_BOLD, size=13, bold=True, color=RGBColor(0,0,0))
    if en:
        p.add_run("  ")
        r2 = p.add_run(en)
        set_run(r2, latin="Arial", cjk=CJK_BOLD, size=10, bold=False,
                color=RGBColor(0x55,0x55,0x55))

def para(cn, indent=True):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Pt(24)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(cn)
    set_run(r)
    return p

def label(cn):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(cn)
    set_run(r, bold=True)
    return p

def note(markup):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    add_math_runs(p, markup, size=11, color=RGBColor(0x33,0x33,0x33))

def figure(fname, num, cn, en, width_cm):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    run = p.add_run()
    run.add_picture(os.path.join(FIG, fname), width=Cm(width_cm))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(10)
    r1 = cap.add_run(f"图 {num}　{cn}")
    set_run(r1, size=10.5, bold=True)
    r2 = cap.add_run(f"\n(Figure {num}. {en})")
    set_run(r2, size=9, italic=True, color=RGBColor(0x66,0x66,0x66))

def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:fill"), hexcolor)
    tcPr.append(sh)

# =====================================================================
# TITLE PAGE
# =====================================================================
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
t.paragraph_format.space_before = Pt(24)
r = t.add_run("快速响应（150～200 Hz）电液伺服系统\n动态性能限制的分析")
set_run(r, latin="Arial", cjk=CJK_BOLD, size=20, bold=True)

st = doc.add_paragraph()
st.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = st.add_run("ANALYSIS OF DYNAMIC PERFORMANCE LIMITATIONS OF FAST RESPONSE "
               "(150 TO 200 Hz) ELECTROHYDRAULIC SERVOS")
set_run(r, size=11, italic=True, color=RGBColor(0x44,0x44,0x44))

for txt, sz in [("作者：John R. Zeller（约翰·R·泽勒）", 12),
                ("美国国家航空航天局　路易斯研究中心（Lewis Research Center），俄亥俄州克利夫兰", 11),
                ("NASA 技术报告　NASA Technical Note D-5388　·　1969 年 8 月", 11)]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    set_run(p.add_run(txt), size=sz)

# translator note box
doc.add_paragraph()
box = doc.add_paragraph()
box.paragraph_format.space_before = Pt(12)
pPr = box._p.get_or_add_pPr()
pbdr = OxmlElement("w:pBdr")
for edge in ("top", "left", "bottom", "right"):
    e = OxmlElement("w:" + edge)
    e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "6")
    e.set(qn("w:space"), "6"); e.set(qn("w:color"), "999999")
    pbdr.append(e)
pPr.insert(0, pbdr)  # pBdr must precede spacing/ind in pPr per OOXML schema
r = box.add_run("译者说明")
set_run(r, bold=True, size=10.5)
note_txt = (
    "\n本文为美国 NASA 技术报告 TN D-5388（公有领域文献）的中文译本，供学习与"
    "技术参考之用。译文以中文为主，关键专业术语在首次出现时附英文原词，文末另附"
    "“英汉术语对照表”。文中的方程、表格与插图均依据原文重制；图片直接取自原始扫描"
    "件。计量单位保留原文写法，即采用英制单位，并在括号内给出对应的国际单位制（SI）"
    "数值。如译文与原文有出入，应以英文原文为准。"
)
r = box.add_run(note_txt)
set_run(r, size=10.5, color=RGBColor(0x33,0x33,0x33))

doc.add_page_break()

# =====================================================================
# ABSTRACT
# =====================================================================
h1("摘要", "ABSTRACT")
para("快速响应（150～200 Hz）的电液阀控活塞伺服系统（electrohydraulic valve-controlled "
     "piston servo system）被用作实验动力学与控制研究中的研究工具。为实现如此高的响应"
     "速率，这些系统中的各个部件必须在其能力极限下工作。本文建立了这类系统的详细非线性"
     "解析模型，并通过将模型的动态性能与某一具体应用的实际实验数据进行对比，验证了该模型"
     "的准确性。该分析得出了一种新的广义设计准则（generalized design criterion），可在"
     "具体应用中帮助确定动态性能能力的最大区域。")

# =====================================================================
# SUMMARY
# =====================================================================
h1("概要", "SUMMARY")
para("先进推进系统（propulsion system）动力学与控制研究领域的工作，提出了对快速响应"
     "（150～200 Hz）伺服作动系统的需求。这类应用通常选用的设备是电液伺服阀"
     "（electrohydraulic servovalve）与缸内活塞作动器（piston-in-cylinder actuator，"
     "即活塞-缸）组合。在以有限振幅、并以如此高的速率（150～200 Hz）振荡各种推进系统部件"
     "时，系统各部件必须在其能力极限下工作。因此，在确定这些系统的动态性能能力时，必须"
     "考虑那些在较低响应应用中常被忽略的部件非线性。")
para("本文给出了这类系统的详细非线性解析模型，并通过将模型的动态性能与某一具体高频应用"
     "的实际实验数据进行对比，验证了该模型的准确性。借助这一非线性动态模型所实现的部件"
     "性能评估，得出了一种有助于系统部件选型的新设计准则。该新准则与已有的极限准则相结合，"
     "即可确定快速响应系统的动态性能能力最大区域。")

# =====================================================================
# INTRODUCTION
# =====================================================================
h1("引言", "INTRODUCTION")
para("先进推进系统领域的研究工作，对高性能、快速响应（150～200 Hz）的伺服系统提出了重大"
     "需求。这种需求体现在两个方面：其一，作为扰动装置，用于研究推进系统及其部件的高频"
     "动力学特性；其二，作为复杂系统中的控制回路环节。")
para("为提供这种快速响应控制能力，通常选用的设备是两级电液伺服阀（two-stage "
     "electrohydraulic servovalve）与缸内活塞作动器（活塞-缸）组合。其基本闭环结构如图1"
     "所示。该设备适合此类应用，原因有以下几点。第一，它本身就具备在所需高频速率下调制"
     "大量能量的能力。第二，大多数推进系统的被控变量都可以布置成能很好地适应活塞-缸作动器"
     "直线运动的形式。最后，该系统以电信号作为输入，便于接受定义明确的输入波形，从而大大"
     "简化了后续对研究性能数据的解释工作。")
figure("fig01.png", 1, "电液伺服系统的基本闭环结构",
       "Basic closed-loop configuration of electrohydraulic servo system.", 14)
para("在许多采用这种控制系统结构的应用中，作动器与负载组合的固有液压谐振频率"
     "（hydraulic resonant frequency）会限制动态性能的范围（参考文献1）。然而，本文中"
     "需要以如此高的响应速率（150～200 Hz）进行操纵的系统所涉及的负载质量相对较小。因此，"
     "通过将伺服阀与活塞作动器进行液压近耦合（close-coupling）以尽量减小被封闭液压油的"
     "容积，可使液压弹簧/负载质量的谐振频率出现在远高于所关注动态性能范围之处。")
para("消除这一固有性能限制后，近耦合、小质量的电液伺服系统便归入了某种较为特殊的类别。"
     "此时较高频率系统的动态性能能力，变得相当依赖于部件的某些物理极限。正弦输出性能的"
     "幅值与频率，将作为其中某些限制的函数而受到约束。该边界以内的区域即为动态性能能力的"
     "最大区域。")
para("本文评估了各部件限制在确定该边界时所起的作用。本文力求叙述足够详尽，以展示非线性"
     "分析在评估高性能要求系统时的价值。本文还将尝试，基于那些被发现具有显著影响的部件"
     "限制，建立通用的设计准则。")

# =====================================================================
# ANALYTICAL DESCRIPTION OF COMPONENTS
# =====================================================================
h1("部件的解析描述", "ANALYTICAL DESCRIPTION OF COMPONENTS")

h2("负载与活塞作动器的力平衡", "Load and Piston Actuator Force Balance")
para("对于所考虑的这类系统，假设由双出杆（双作用）油缸所驱动的负载，其摩擦载荷以及弹簧型"
     "（与位置相关）载荷均可忽略不计。采用图2的符号表示，可得如下方程：")
add_equation("P_{p}A_{p} = Mẍ_{o} + F_{o}", "1")
para("式中", indent=False)
add_equation("P_{p} = P_{1} − P_{2}", "2")
figure("fig02.png", 2, "伺服阀输出、活塞作动器与负载的示意图",
       "Schematic representation of servovalve output, piston actuator, and load.", 11)

h2("伺服阀输出与作动器的耦合", "Servovalve Output and Actuator Coupling")
para("还假设伺服阀与活塞作动器之间为液压近耦合。因此，所涉及的较短连接管路的传输线输运"
     "滞后（transport lag）可以忽略。但其中仍会存在一定量的被封闭液体，为使描述方程保持"
     "连续性，必须将其计入。对于所考虑的系统，等效输出质量 Mo 与这一小容积可压缩流体所"
     "构成的谐振频率，将出现在远超出所关注范围（150～200 Hz）之处。因此，该谐振不会成为"
     "系统动态性能的限制因素。描述伺服阀与作动器相互连接关系的方程如下：")
add_equation("A_{p}ẋ_{o} + (V_{t}/4β)Ṗ_{p} = q_{v}", "3")
para("方程(3)假设活塞处于中位，且负载情况使得流经阀芯各节流口的体积流量相等。")

h2("两级伺服阀", "Two-Stage Servovalve")
para("对于本文所讨论的这类高性能伺服系统，几乎在所有情况下都采用两级液压伺服阀。该装置"
     "的详细结构见图3。它采用由双喷嘴挡板阀（double jet flapper valve）液压前置放大级"
     "驱动的阀芯（滑阀，spool valve）输出级。这一灵敏的挡板由电磁力矩马达"
     "（torque motor）的衔铁（armature）驱动。此外，还设置了从阀芯到力矩马达衔铁的力反馈"
     "通路，以使其对不同工作模式不敏感。参考文献1推导了描述该控制部件工作的基本关系式。"
     "下面给出最终的描述方程及其所依据的假设。")
figure("fig03.png", 3, "两级电液伺服阀的结构示意图",
       "Schematic representation of two-stage electrohydraulic servovalve.", 13)
para("伺服阀的输出以压力和流量的形式，经由阀芯节流口（图2）并通过控制管路供给活塞作动器。"
     "将这一输出表示为阀芯位移 xs 的函数的方程定义为：")
add_equation("q_{v} = C_{s}x_{s}√P_{v}", "4")
para("式中", indent=False)
add_equation("P_{v} = P_{sp} − P_{p}", "5")
para("且回油压力为零。图4给出了由该关系式所得到的一族阀输出特性曲线。由该图可见，输出"
     "压力与流量之间的非线性关系，在物理上受到阀芯最大行程 xs(max) 的限制。")
figure("fig04.png", 4, "广义的伺服阀输出特性",
       "Generalized servovalve output characteristics.", 12)
para("阀芯位移由挡板阀前置放大级的作用决定。在设计良好的伺服阀中，使阀芯加速所需的压力"
     "作用力可以忽略。因此，阀芯运动将仅取决于挡板阀流向阀芯两端的体积流量。该作用定义"
     "如下：")
add_equation("x_{s} = (1/A_{s})∫q_{s} dt", "6")
para("完成液压前置放大的双喷嘴挡板阀，在解析上是一个相当复杂的装置。不过，参考文献1已对"
     "该装置作了透彻的研究。利用该工作的结果，由挡板流向阀芯的流量可以用下面的线性关系"
     "充分近似地表示：")
add_equation("q_{s} = K_{fn}x_{f}", "7")
para("尽管这一简单关系建立在许多假设之上，但该领域以往的工作（参考文献2）已表明，它在"
     "设计良好的高性能伺服阀中相当有效。")
para("挡板-衔铁的运动来自施加于力矩马达衔铁上的有效力矩。该力矩定义如下：")
add_equation("T_{diff} = K_{i}i_{c} − K_{w}x_{s}", "8")
para("衔铁由构成弹簧/质量/阻尼系统的若干元件组成。据此，可用如下二阶微分方程表示"
     "（参考文献2）：")
add_equation("T_{diff} = (K_{fs}/ω_{nf}^{2})ẍ_{f} + (2δK_{fs}/ω_{nf})ẋ_{f} + K_{fs}x_{f}", "9")
para("除了由阀芯最大位移所造成的伺服阀输出级能力的物理限制之外，由于挡板位移存在极限 "
     "±xf(max)，前置放大级的流量也存在限制。")

h2("力矩马达电流与伺服放大器输出", "Torque Motor Current and Servoamplifier Output")
para("对于驱动感性力矩马达线圈的常规电压源输出（低输出阻抗）放大器，其基本方程由式(10)"
     "定义。")
add_equation("v_{a} = L_{c}(di_{c}/dt) + R_{c}i_{c}", "10")
para("力矩马达线圈本身的感性时间常数 Lc/Rc 相当大。不过，目前有若干种改善响应的技术可供"
     "采用。为实现这一改善，已研制出一种具有高阻抗输出的精密伺服放大器（参考文献3）。该"
     "放大器已在本文所讨论的这类快速响应系统中进行了实验应用。该装置及其相关非线性限制的"
     "详细框图，作为图5完整非线性系统框图的一部分给出。")

h2("反馈监测、信号比较与前置放大", "Feedback Monitoring, Signal Comparison, and Preamplification")
para("为给反馈提供作动器与负载输出位置的指示信号，采用了一个位置传感器"
     "（position transducer）。它可以用如下方程进行解析表示。")
add_equation("K_{fb}x_{o} = v_{fb}", "11")
para("期望位置 xd 与实际负载位置 xo 的比较（求和）在伺服放大器的前置放大输入端进行"
     "（图5）。其由以下方程定义：")
add_equation("K_{fb}x_{d} = v_{cd}", "12")
add_equation("v_{cd} − v_{fb} = v_{e}", "13")
para("上述信号比较结果 ve 在伺服放大器的前置放大级被放大。该运算由式(14)定义。")
add_equation("K_{pa}v_{e} = v_{pa}", "14")

h2("非线性框图", "Nonlinear Block Diagram")
para("上述各方程可以组合成图5的非线性框图。图中还包含了部件的物理限制。该非线性模型可用于"
     "对这些快速响应应用进行解析性的性能研究。")
figure("fig05.png", 5, "阀控活塞伺服系统的非线性框图表示",
       "Nonlinear block diagram representation of valve controlled piston servo system.", 15)

# =====================================================================
# DYNAMIC PERFORMANCE RESULTS
# =====================================================================
h1("动态性能结果", "DYNAMIC PERFORMANCE RESULTS")

h2("仿真模型性能", "Simulated Model Performance")
para("利用该非线性动态模型，确定了某一具体系统结构的动态性能。该系统的物理常数列于表I中。"
     "这些参数代表在路易斯研究中心研制的一台实际伺服作动器。该作动器通过操纵一个可变面积"
     "节流口来节流燃油流量，以高响应速率用于涡轮喷气发动机（turbojet engine）的动力学"
     "研究。评估是通过在模拟计算机（analog computer）上对模型进行仿真来完成的。对于不同"
     "水平的期望输出轴运动，其动态性能（频率响应，frequency response）示于图6。")

# ---- Table I ----
tbl_caption = doc.add_paragraph()
tbl_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = tbl_caption.add_run("表 I　燃油阀伺服系统物理常数")
set_run(r, size=10.5, bold=True)
r2 = tbl_caption.add_run("\n(TABLE I. — FUEL VALVE SERVO SYSTEM PHYSICAL CONSTANTS)")
set_run(r2, size=9, italic=True, color=RGBColor(0x66,0x66,0x66))

tableI_rows = [
 ("位置标度因数（反馈传感器与输入），V/in.（V/cm）", "K_{fb}", "80（31.5）"),
 ("伺服放大器前置放大增益，V/V", "K_{pa}", "0.46"),
 ("伺服放大器输出前向回路增益，V/V", "K_{a}", "50"),
 ("伺服放大器输出电流反馈增益，V/A", "K_{cf}", "188"),
 ("力矩马达线圈自感，H", "L_{c}", "0.57"),
 ("力矩马达线圈与伺服放大器等效电阻，Ω", "R_{c}", "600"),
 ("力矩马达增益，in.-lbf/A（cm-N/A）", "K_{i}", "10（114）"),
 ("力矩马达衔铁/挡板固有频率，rad/sec", "ω_{nf}", "730（2π）"),
 ("力矩马达衔铁/挡板阻尼比（无量纲）", "δ", "0.4"),
 ("衔铁挡板刚度，in.-lbf/in.（cm-N/cm）", "K_{fs}", "93（414）"),
 ("挡板阀线性流量系数，(in./sec)/in.（(cm/sec)/cm）", "K_{fn}", "150（968）"),
 ("反馈弹簧丝刚度，in.-lbf/in.（cm-N/cm）", "K_{w}", "13.5（60.0）"),
 ("阀芯端面面积，in.²（cm²）", "A_{s}", "0.026（0.1677）"),
 ("活塞面积，in.²（cm²）", "A_{p}", "0.25（1.612）"),
 ("阀芯节流口流量系数，(in.³/sec)/√lbf（(cm³/sec)/√N）", "C_{s}", "32.5（251.5）"),
 ("液压供油压力，lbf/in.²（N/cm²）", "P_{sp}", "3000（2070）"),
 ("等效作动器与输出负载质量，lbf-sec²/in.（N-sec²/cm）", "M_{o}", "0.00155（0.00271）"),
 ("伺服放大器最大输出电压，V", "v_{a(max)}", "±15"),
 ("挡板衔铁最大位移，in.（cm）", "x_{f(max)}", "±0.0012（±0.00305）"),
 ("阀芯最大位移，in.（cm）", "x_{s(max)}", "±0.015（±0.0381）"),
 ("伺服阀额定流量，in.³/sec（cm³/sec）", "Q_{r}", "15.4（252.5）"),
 ("最佳活塞面积，in.²（cm²）", "A_{p}^{*}", "0.0744（0.480）"),
 ("阀芯线性流量系数，(in./sec)/in.（(cm/sec)/cm）", "K_{s}", "1030（6640）"),
]
table = doc.add_table(rows=1, cols=3)
table.style = "Table Grid"
table.alignment = WD_TABLE_ALIGNMENT.CENTER
widths = [Cm(10.0), Cm(2.4), Cm(3.5)]
hdr = table.rows[0].cells
for c, txt in zip(hdr, ["参数（单位）", "符号", "数值　英制（SI）"]):
    c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(c.paragraphs[0].add_run(txt), size=10.5, bold=True)
    shade(c, "D9E2F3")
for name, sym, val in tableI_rows:
    cells = table.add_row().cells
    set_run(cells[0].paragraphs[0].add_run(name), size=10)
    cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_math_runs(cells[1].paragraphs[0], sym, size=10)
    cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(cells[2].paragraphs[0].add_run(val), size=10)
for row in table.rows:
    for i, c in enumerate(row.cells):
        c.width = widths[i]
doc.add_paragraph().paragraph_format.space_after = Pt(2)

figure("fig06.png", 6, "模型动态性能——仿真燃油阀伺服系统",
       "Model dynamic performance - simulated fuel valve servo.", 13)

h2("实验性能", "Experimental Performance")
para("由表I所描述的系统所表现出的实际实验动态性能示于图7。为便于比较，图中还一并给出了"
     "仿真模型的性能。两组曲线之间的相关性证明了该解析非线性模型的准确性。")
figure("fig07.png", 7, "实验动态性能——燃油阀伺服系统",
       "Experimental dynamic performance - fuel valve servo.", 13)

# =====================================================================
# DISCUSSION OF PERFORMANCE LIMITATIONS
# =====================================================================
h1("性能限制的讨论", "DISCUSSION OF PERFORMANCE LIMITATIONS")
para("由图6和图7的曲线可见，对于给定的期望输出轴运动，实际的正弦运动在较高频率处会被衰减。"
     "此外，随着期望输出运动幅值的增大，衰减出现的频率会降低。可见，作动系统中正在发生"
     "某种限制现象。在预测高性能电液伺服系统不衰减正弦输出运动的限制时，常规做法定义了"
     "两个极限准则，即由所选伺服阀输出能力所决定的速度（流量）极限和加速度（压力）极限。")
para("图4表明，最大输出能力出现在 xs(max) 特性线上。在该输出特性线上的不同点处传递给负载"
     "的功率，会在某一特定点处取得最大值。峰值功率传递点（peak power transfer point）的"
     "推导见参考文献1，因此这里只引用其结果。在峰值功率处，压力和流量由式(15)和式(16)"
     "定义。")
add_equation("P_{p(pp)} = (2/3)P_{sp}", "15")
add_equation("q_{v(pp)} = C_{s}x_{s(max)}√((1/3)P_{sp})", "16")
para("常规伺服阀术语选取这些压力和流量值，来定义作动器输出的加速度（压力）极限线和速度"
     "（流量）极限线。常规做法还将式(16)所定义的流量称为伺服阀的额定流量 Qr。选取式(15)"
     "和式(16)的压力与流量，便确定了图8中的剖面线（阴影）区域。因此，出于实用目的，正弦"
     "输出运动被保守地限制在不超过该区域的压力和流量范围内。利用这些极限压力与流量值，"
     "现在即可推导出常规所接受的加速度（压力）极限线和速度（流量）极限线方程。")
figure("fig08.png", 8, "采用峰值功率传递准则的无限制动态性能区域",
       "Region of unlimited dynamic performance using peak power transfer criteria.", 13)

h2("速度（流量）极限准则", "Velocity (Flow) Limit Criterion")
para("若输出活塞位置 xo 按正弦规律变化，则可写出下列方程：")
add_equation("x_{o} = X_{o} sin ωt", "17")
add_equation("ẋ_{o} = X_{o}ω cos ωt", "18")
para("为便于引用，重写定义伺服阀向负载输出流量的式(3)。")
add_equation("q_{v} = A_{p}ẋ_{o} + (V_{t}/4β)Ṗ_{p}", "3")
para("由于所考虑的封闭容积很小，式(3)右端第二项可以忽略，于是得到")
add_equation("q_{v} = A_{p}ẋ_{o}", "19")
para("将式(19)与式(18)合并可得")
add_equation("q_{v}/A_{p} = X_{o}ω cos ωt", "20")
para("仅取各参量的峰值，即得如下速度极限关系：")
add_equation("Q_{r}/A_{p} = X_{o}ω", "21")

h2("加速度（压力）极限准则", "Acceleration (Pressure) Limit Criterion")
para("正弦运动下的输出加速度定义为")
add_equation("ẍ_{o} = −X_{o}ω^{2} sin ωt", "22")
para("若假设作动器上仅有纯质量负载，则可得如下方程：")
add_equation("P_{p}A_{p} = M_{o}ẍ_{o}", "23")
para("于是，将式(22)和式(15)代入式(23)，并仅考虑峰值，即得如下加速度极限关系：")
add_equation("X_{o}ω^{2} = (2P_{sp}A_{p})/(3M_{o})", "24")
para("利用燃油阀伺服系统的参数（表I），可将速度极限和加速度极限曲线叠加到图6的数据上，"
     "所得合成结果示于图9。由于系统的衰减发生在远低于这些极限之处，显然还有其他某种因素"
     "限制了响应。")
figure("fig09.png", 9, "带速度极限与加速度极限的燃油阀解析模型性能",
       "Fuel valve analytical model performance with velocity and acceleration limits.", 14)

h2("挡板极限准则", "Flapper Limit Criterion")
para("无论是从对非线性模型的仿真所作的观察，还是通过解析推导，都发现这一限制是由伺服阀"
     "液压前置放大级内部的流量限制所造成的。换言之，流向伺服阀输出级（滑阀）的最大流量"
     "不足以使其在较高频率下足够快地换向滑移（以最大速度运动），从而无法提供额定流量 Qr。"
     "这种现象在较低响应的应用中通常不会出现。")
para("应当指出，两级伺服阀的高频（大流量）限制，是这类装置在设计良好时所固有的。为获得"
     "可靠的长期性能而设计的射流-挡板阀元件，其稳定性对节流口尺寸和间隙、进而对挡板流量"
     "施加了一定的限制。关于这些事实的详细讨论见参考文献1。")
para("基于上述观察，挡板级流量限制必须作为预测高性能电液伺服系统所能达到的最大动态性能的"
     "第三个准则。该准则的推导如下：当伺服阀输出被限制在由峰值功率传递处的压力和流量所"
     "界定的区域内（图8）时，式(4)的非线性关系")
add_equation("q_{v} = C_{s}x_{s}√P_{v}", "4")
para("可以用下式充分近似地表示")
add_equation("q_{v} = K_{s}x_{s}", "25")
note("其中　K_{s} = ∂q_{v}/∂x_{s} ，在 P_{v} = (1/3)P_{sp} 处取值")
para("将阀输出流量 qv 的这一线性化关系代入式(19)，得到")
add_equation("K_{s}x_{s} = A_{p}ẋ_{o}", "26")
para("将式(18)代入式(26)并整理，得到")
add_equation("x_{s} = (A_{p}X_{o}/K_{s})ω cos ωt", "27")
para("求导得")
add_equation("ẋ_{s} = −(A_{p}/K_{s})ω^{2}X_{o} sin ωt", "28")
para("对式(6)求导并整理，得到")
add_equation("q_{s} = A_{s}ẋ_{s}", "29")
para("为便于引用，重写式(7)。")
add_equation("q_{s} = K_{fn}x_{f}", "7")
para("将式(28)、(29)和(7)合并，并仅考虑正弦运动的峰值，得到如下方程：")
add_equation("(A_{s}A_{p}ω^{2}X_{o})/K_{s} = K_{fn}x_{f(max)}", "30")
para("整理式(30)，即得如下挡板流量极限关系")
add_equation("X_{o}ω^{2} = (K_{fn}K_{s}x_{f(max)})/(A_{p}A_{s})", "31")
para("利用前例的参数（表I），可将这一极限准则与图9的合成曲线相结合，生成图10。这一新极限"
     "与实际系统最大动态性能之间的密切吻合，证明了该准则的有效性，并强调了它在快速响应"
     "（150～200 Hz）应用中进行性能预测的必要性。")
figure("fig10.png", 10, "带速度、加速度与挡板流量极限的燃油阀性能",
       "Fuel valve performance with velocity, acceleration, and flapper flow limits.", 14)

# =====================================================================
# GENERALIZED DESIGN CRITERIA
# =====================================================================
h1("最大动态性能能力区域的广义设计准则",
   "GENERALIZED DESIGN CRITERIA FOR REGION OF MAXIMUM DYNAMIC PERFORMANCE CAPABILITY")
para("为清晰起见，将式(21)、(24)和(31)所定义的三个极限关系重列于此。")
label("速度极限")
add_equation("X_{o}ω = Q_{r}/A_{p}", "21")
label("加速度极限")
add_equation("X_{o}ω^{2} = (2P_{sp}A_{p})/(3M_{o})", "24")
label("挡板流量极限")
add_equation("X_{o}ω^{2} = (K_{fn}K_{s}x_{f(max)})/(A_{p}A_{s})", "31")
para("对于负载质量和可用供油压力均已确定的具体应用，这些准则都是活塞作动器面积以及具体"
     "伺服阀容量的函数。对于某一特定伺服阀，这些曲线将仅取决于活塞面积。图11给出了各极限"
     "线随活塞面积变化而产生的广义位移（移动）。")
figure("fig11.png", 11, "通用极限线——对活塞面积的依赖关系",
       "General limit lines - dependence on piston area.", 13)
para("由该图可见，对于某一特定的活塞面积 Ap，可使相互平行的挡板流量线与输出加速度线重合。"
     "出现这种重合时的活塞面积可按如下方法确定：令式(24)与式(31)相等，得到")
add_equation("(K_{fn}K_{s}x_{f(max)})/(A_{s}A_{p}) = (2P_{sp}A_{p})/(3M_{o})", "32")
para("解出重合时的活塞面积，得到")
add_equation("A_{p}^{*} = √[(x_{f(max)}M_{o}K_{fn}K_{s})/((2/3)A_{s}P_{sp})]", "33")
para("对表I所规定的燃油阀系统采用“最佳”活塞面积 Ap*，将使动态性能能力的高频区域最大化。"
     "该区域在图12中以剖面线（阴影）表示。该图中的虚线为实验燃油阀系统动态性能能力的边界，"
     "该系统所用面积大于 Ap*。该图表明，选择“非最佳”面积会导致性能能力达不到最大。")
figure("fig12.png", 12, "优化后的动态性能能力区域",
       "Optimized dynamic performance capability region.", 13)
para("应当指出，由式(33)得到的活塞面积（Ap* = 0.0744 in.²，即 0.480 cm²）相对较小。如果"
     "存在纯质量以外的对抗性负载，则必须仔细审查该面积是否足够。不过，在许多作动应用中，"
     "由式(33)所选取的面积能够在整个动态性能能力区域内实现成功运行。")

# =====================================================================
# FURTHER EXTENSIONS
# =====================================================================
h1("广义极限准则的进一步推广", "FURTHER EXTENSIONS OF THE GENERALIZED LIMIT CRITERIA")
para("图12表明，动态性能能力的边界由两条相交于同一点的直线组成。对于最佳活塞面积的情形，"
     "它们是活塞速度极限线，以及重合在一起的挡板流量极限线和活塞加速度极限线。应当注意，"
     "在对数坐标图上，活塞速度极限线的斜率为 −1，而挡板流量极限线或活塞加速度极限线的"
     "斜率为 −2。")
para("这些直线由之发出的交点或“拐点”（corner point），具有与之相对应的位移坐标和频率"
     "坐标，分别定义为 xo** 和 ω**。")
para("再次注意图11中所示挡板流量极限线随活塞面积减小（向右）的移动方向可见，对于所有大于"
     "或等于 Ap* 的活塞面积，拐点 (xo**, ω**) 将由活塞速度极限线与挡板流量极限线的交点"
     "确定。这些坐标的关系可按如下方法确定：将式(21)代入式(31)，解出 ω**，即得式(34)。")
add_equation("ω^{**} = (K_{fn}K_{s}x_{f(max)})/(A_{s}Q_{r})　　（当 A_{p} ≥ A_{p}^{*} 时）", "34")
para("将 ω** 的这一表达式代入式(21)，解出 xo**，得到如下关系：")
add_equation("x_{o}^{**} = (Q_{r}^{2}A_{s})/(K_{fn}K_{s}x_{f(max)}A_{p})　　（当 A_{p} ≥ A_{p}^{*} 时）", "35")
para("对于小于 Ap* 的活塞面积，查看图11可知，活塞加速度极限线将位于挡板流量极限线的左侧。"
     "因此，对于 Ap < Ap* 的情形，动态性能能力边界的交点 (xo**, ω**) 将由常规的活塞加速度"
     "极限线与速度极限线确定。坐标 xo** 和 ω** 的关系可按如下方法确定：将式(21)代入式(24)，"
     "解出 ω**，得到如下关系：")
add_equation("ω^{**} = (2P_{sp}A_{p}^{2})/(3Q_{r}M_{o})　　（当 A_{p} < A_{p}^{*} 时）", "36")
para("将式(36)代入式(21)，解出 xo**，得到")
add_equation("x_{o}^{**} = (Q_{r}^{2}M_{o})/((2/3)P_{sp}A_{p}^{3})　　（当 A_{p} < A_{p}^{*} 时）", "37")
para("图13给出了不同活塞面积下交点 (xo**, ω**) 的轨迹。各坐标已对最佳面积 Ap* 处的交点"
     "进行了归一化。")
figure("fig13.png", 13, "动态性能能力区域归一化拐点的轨迹",
       "Locus of normalized corner points for region of dynamic performance capabilities.", 12)
para("活塞面积大于 Ap* 时的轨迹由式(34)和式(35)确定。由于式(34)所定义的频率 ω** 不是活塞"
     "面积 Ap 的函数，因此 Ap > Ap* 时的轨迹即为图13中所示的竖直线。")
para("若活塞面积 Ap 小于最佳面积 Ap*，则轨迹可由式(36)和式(37)确定。这两式意味着")
add_equation("x_{o}^{**} ∝ (ω^{**})^{−3/2}　　（当 A_{p} < A_{p}^{*} 时）")
para("因此，图13的轨迹在 Ap < Ap* 时斜率为 −3/2。由此可知，只要知道 Ap = Ap* 处的坐标，"
     "就足以完全确定拐点轨迹。正因如此，图13的轨迹已对该点处的坐标进行了归一化。"
     "Ap = Ap* 处的坐标 (xo*, ω*) 定义为")
add_equation("x_{o}^{*} = (Q_{r}^{2}A_{s})/(K_{fn}K_{s}x_{f(max)}A_{p}^{*})", "38")
add_equation("ω^{*} = (K_{fn}K_{s}x_{f(max)})/(A_{s}Q_{r})", "39")
para("活塞面积之比 (Ap/Ap*) 决定了拐点在图13归一化轨迹上的位置。由式(36)、(37)和(38)可"
     "推导出如下关系：")
label("当 Ap > Ap* 时：")
add_equation("x_{o}^{**}/x_{o}^{*} = A_{p}^{*}/A_{p} < 1", "40")
label("当 Ap < Ap* 时：")
add_equation("x_{o}^{**}/x_{o}^{*} = (A_{p}^{*}/A_{p})^{3} > 1", "41")
label("以及")
add_equation("ω^{**}/ω^{*} = (A_{p}/A_{p}^{*})^{2} < 1", "42")
para("因此，式(33)以及式(38)至(42)完全描述了拐点的位置。图13的归一化图中还包含若干由各"
     "拐点发出的边界线。速度极限线向左斜率为 −1，挡板流量极限线或加速度极限线向右斜率为 "
     "−2。")
para("有了这样一幅关于可能的动态性能能力区域的较为完整的图景后，可作如下几点观察。对于"
     "大于最佳值 Ap* 的活塞面积，边界线向左移动，实际上缩小了动态性能能力区域。因此，除非"
     "对抗性力负载的要求需要更大的活塞面积，否则采用 Ap* 将获得最高的频率-幅值性能。")
para("对于小于 Ap* 的活塞面积，图13表明，高频性能被牺牲，以换取在更大的 xo 幅值下的较低"
     "频率运行。")

# =====================================================================
# CONCLUDING REMARKS
# =====================================================================
h1("结论", "CONCLUDING REMARKS")
para("本文对用于高响应（150～200 Hz）研究应用的电液阀控活塞伺服作动系统的非线性方面进行了"
     "详细分析。分析中将主要负载视为惯性（质量）负载，并假设作动器与阀为近耦合。分析表明，"
     "在这些条件下，一个此前被认为无足轻重的伺服阀内部限制（挡板流量限制），会极大地影响"
     "快速响应系统的动态性能能力。本文对这一限制进行了研究，并将其归纳为通用的设计准则。"
     "这些准则可为特定系统确定动态性能能力的最大区域。随后即可采用经典控制技术，以确保在"
     "整个该能力区域内获得稳定的动态性能。")
para("美国国家航空航天局，路易斯研究中心，俄亥俄州克利夫兰，1969 年 6 月 17 日。", indent=False)

# =====================================================================
# APPENDIX - SYMBOLS
# =====================================================================
h1("附录 A　符号表", "APPENDIX — SYMBOLS")

def symbol_table(rows, header=("符号", "含义（单位）")):
    t = doc.add_table(rows=1, cols=2)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hc = t.rows[0].cells
    for c, txt in zip(hc, header):
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run(c.paragraphs[0].add_run(txt), size=10.5, bold=True)
        shade(c, "EAEAEA")
    for sym, mean in rows:
        cells = t.add_row().cells
        cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_math_runs(cells[0].paragraphs[0], sym, size=10.5)
        set_run(cells[1].paragraphs[0].add_run(mean), size=10.5)
    for row in t.rows:
        row.cells[0].width = Cm(3.0)
        row.cells[1].width = Cm(12.9)
    return t

main_symbols = [
 ("A", "面积，in.²（cm²）"),
 ("C", "系数（非线性）"),
 ("F", "力，lbf（N）"),
 ("i", "电流（瞬时值），A"),
 ("K", "标度因数或线性化系数"),
 ("L", "自感，H"),
 ("M", "质量，lbf-sec²/in.（N-sec²/cm）"),
 ("P", "压力（稳态），lbf/in.²（N/cm²）"),
 ("p", "压力（瞬时值），lbf/in.²（N/cm²）"),
 ("Q", "体积流量（稳态），in.³/sec（cm³/sec）"),
 ("q", "体积流量（瞬时值），in.³/sec（cm³/sec）"),
 ("R", "电阻，Ω"),
 ("T", "力矩，in.-lbf（cm-N）"),
 ("t", "时间，sec"),
 ("V", "容积，in.³（cm³）"),
 ("v", "电压（瞬时值），V"),
 ("X", "直线位移（正弦波峰值），in.（cm）"),
 ("x", "直线位移（瞬时值），in.（cm）"),
 ("β", "体积弹性模量，lbf/in.²（N/cm²）"),
 ("δ", "阻尼比（无量纲）"),
 ("π", "数值常数，3.1416"),
 ("ρ", "质量密度，lbf-sec²/in.⁴（N-sec²/cm⁴）"),
 ("ω", "频率（角频率），rad/sec"),
]
symbol_table(main_symbols)

label("下标（Subscripts）")
subs = [
 ("a", "放大器（amplifier）"), ("c", "线圈（coil）"), ("cd", "指令（command）"),
 ("cf", "电流反馈（current feedback）"), ("d", "给定/需求（demand）"),
 ("diff", "差值（difference）"), ("e", "误差（error）"), ("f", "挡板（flapper）"),
 ("fb", "反馈（feedback）"), ("fn", "挡板喷嘴（flapper nozzle）"),
 ("fs", "挡板弹簧（flapper spring）"), ("i", "电流（current）"),
 ("max", "最大值（maximum）"), ("nf", "固有频率（natural frequency）"),
 ("o", "输出（output）"), ("p", "活塞（piston）"),
 ("pa", "前置放大器（preamplifier）"), ("pp", "峰值功率（peak power）"),
 ("r", "额定（rated）"), ("s", "阀芯（spool）"),
 ("sp", "供油压力（supply pressure）"), ("t", "总/合计（total）"),
 ("v", "阀（valve）"), ("w", "（反馈）弹簧丝（wire）"),
]
symbol_table(subs, header=("下标", "含义"))

label("上标（Superscripts）")
sups = [
 ("*", "最佳值（optimum）"),
 ("**", "拐点标记（corner point designation）"),
 ("· （上点）", "对时间的一阶导数（first derivative w.r.t. time）"),
 (".. （上双点）", "对时间的二阶导数（second derivative w.r.t. time）"),
]
symbol_table(sups, header=("上标", "含义"))

# =====================================================================
# REFERENCES
# =====================================================================
h1("参考文献", "REFERENCES")
refs = [
 "Merritt, Herbert E.: Hydraulic Control Systems. John Wiley & Sons, Inc., 1967.",
 "Thayer, W. J.: Transfer Functions for Moog Servovalves. Tech. Bull. #103, "
 "Moog Servocontrols, Inc.",
 "Zeller, John R.: Design and Analysis of a Modular Servoamplifier for "
 "Fast-Response Electrohydraulic Control Systems. NASA TN D-4898, 1968.",
]
for i, ref in enumerate(refs, 1):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Pt(24)
    p.paragraph_format.first_line_indent = Pt(-24)
    p.paragraph_format.space_after = Pt(4)
    set_run(p.add_run(f"{i}.　{ref}"), size=11)

# =====================================================================
# TRANSLATOR APPENDIX - GLOSSARY
# =====================================================================
h1("附录 B　英汉术语对照表", "GLOSSARY (Translator's note)")
para("下表汇总本文出现的主要专业术语，供阅读与查证之用。", indent=False)
glossary = [
 ("electrohydraulic servo", "电液伺服（系统）"),
 ("electrohydraulic servovalve", "电液伺服阀"),
 ("two-stage servovalve", "两级伺服阀"),
 ("spool / spool valve", "阀芯 / 滑阀"),
 ("flapper; double jet flapper valve", "挡板；双喷嘴挡板阀"),
 ("nozzle", "喷嘴"),
 ("torque motor", "力矩马达"),
 ("armature", "衔铁"),
 ("piston actuator; piston-in-cylinder", "活塞作动器；缸内活塞（活塞-缸）"),
 ("double-ended cylinder", "双出杆（双作用）油缸"),
 ("close-coupled / close-coupling", "近耦合（紧耦合）"),
 ("entrapped fluid / volume", "被封闭流体 / 封闭容积"),
 ("bulk modulus", "体积弹性模量"),
 ("hydraulic resonant frequency", "液压谐振频率"),
 ("natural frequency", "固有频率"),
 ("damping ratio", "阻尼比"),
 ("frequency response", "频率响应"),
 ("dynamic performance", "动态性能"),
 ("mass load / inertial load", "质量负载 / 惯性负载"),
 ("force balance", "力平衡"),
 ("servoamplifier", "伺服放大器"),
 ("preamplifier", "前置放大（级/器）"),
 ("position transducer", "位置传感器"),
 ("(force) feedback", "（力）反馈"),
 ("self-inductance", "自感"),
 ("rated flow", "额定流量"),
 ("supply pressure", "供油压力"),
 ("velocity (flow) limit", "速度（流量）极限"),
 ("acceleration (pressure) limit", "加速度（压力）极限"),
 ("flapper flow limit", "挡板流量极限"),
 ("peak power transfer", "峰值功率传递"),
 ("corner point", "拐点（转折点）"),
 ("optimum piston area", "最佳活塞面积"),
 ("nonlinear analytical model", "非线性解析模型"),
 ("design criterion / criteria", "设计准则"),
 ("propulsion system", "推进系统"),
 ("turbojet engine", "涡轮喷气发动机"),
 ("analog computer", "模拟计算机"),
 ("transport lag", "输运滞后（传输滞后）"),
]
gt = doc.add_table(rows=1, cols=2)
gt.style = "Table Grid"
gt.alignment = WD_TABLE_ALIGNMENT.CENTER
hc = gt.rows[0].cells
for c, txt in zip(hc, ["English", "中文"]):
    c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(c.paragraphs[0].add_run(txt), size=10.5, bold=True)
    shade(c, "EAEAEA")
for en, cn in glossary:
    cells = gt.add_row().cells
    set_run(cells[0].paragraphs[0].add_run(en), size=10.5)
    set_run(cells[1].paragraphs[0].add_run(cn), size=10.5)
for row in gt.rows:
    row.cells[0].width = Cm(8.0)
    row.cells[1].width = Cm(7.9)

# =====================================================================
# Ensure settings.xml zoom has required percent attribute (schema fix)
_settings = doc.settings.element
_zoom = _settings.find(qn("w:zoom"))
if _zoom is not None and _zoom.get(qn("w:percent")) is None:
    _zoom.set(qn("w:percent"), "100")

out = "快速响应电液伺服系统动态性能限制分析_NASA-TN-D-5388_中文译本.docx"
doc.save(out)
print("Saved:", out, os.path.getsize(out), "bytes")
