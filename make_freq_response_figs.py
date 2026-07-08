# -*- coding: utf-8 -*-
"""Generate all figures for 《液压缸频率响应测试讲解》.

All figures are self-produced (matplotlib drawings + numerical simulation of a
valve-controlled cylinder), no copyrighted material. Output -> frl_figs/*.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10.5
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

OUT = "frl_figs"
os.makedirs(OUT, exist_ok=True)

C1, C2, C3, C4 = "#1f6fb4", "#d1495b", "#3a8f5f", "#8a6bbf"

# ----------------------------------------------------------------------------
# Common plant parameters (symmetric cylinder, reduced-order model, Jelali&Kroll
# eq. 4.244-4.252 structure)
# ----------------------------------------------------------------------------
Ps = 210e5          # supply pressure [Pa]
Ap = 1.963e-3       # piston area (D=50 mm) [m^2]
mt = 500.0          # load mass [kg]
Lst = 0.4           # stroke [m]
V0 = 1.5e-4         # dead volume per chamber [m^3]
be = 7.0e8          # effective bulk modulus [Pa]
Cl = 6e-12          # leakage coeff [m^3/(s*Pa)]
Df = 5000.0         # viscous friction [N*s/m]
Fc = 250.0          # Coulomb friction [N]
vs = 1e-3           # Stribeck-ish smoothing velocity [m/s]
Qmax = 6.0e-4       # valve flow at u=1, full pressure drop [m^3/s]
Cv = Qmax / np.sqrt(Ps)
Kv0 = Qmax / Ap     # no-load max speed [m/s]
wv, Dv = 2 * np.pi * 70, 0.8   # valve dynamics
Kp = 40.0           # P position controller [1/m]
dz = 0.002          # spool deadzone (overlap) fraction

Vt_mid = 2 * (V0 + Ap * Lst / 2)
wh = np.sqrt(4 * be * Ap ** 2 / (Vt_mid * mt))
Dh = (Cl / Ap) * np.sqrt(be * mt / Vt_mid) + (Df / (4 * Ap)) * np.sqrt(
    Vt_mid / (be * mt))
fh = wh / 2 / np.pi
print(f"omega_h = {wh:.1f} rad/s ({fh:.1f} Hz),  D_h = {Dh:.3f}")


def pt2(w, wn, D):
    """second-order normalised frequency response"""
    r = w / wn
    return 1.0 / (1 - r ** 2 + 2j * D * r)


# ============================================================================
# Fig 1 -- test rig schematic
# ============================================================================
def fig1():
    fig, ax = plt.subplots(figsize=(11.5, 7.2))
    ax.set_xlim(0, 16.6); ax.set_ylim(0.8, 10.6)
    ax.axis("off"); ax.grid(False)

    def box(x, y, w, h, text, fc="#eef3fa", ec="#1f6fb4", fs=10.5, lw=1.4):
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=3))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, zorder=4)

    def arrow(p0, p1, color="#333333", lw=1.6, style="-|>", ls="-"):
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, lw=lw,
                                     color=color, linestyle=ls,
                                     mutation_scale=14, zorder=5))

    # --- electronics ---
    box(0.6, 8.9, 3.2, 1.3, "信号发生器\n正弦 / 扫频 / 多正弦", fc="#fdf3e3",
        ec="#c07b28")
    box(6.0, 8.9, 3.0, 1.3, "伺服放大器\nu → 阀电流 i", fc="#fdf3e3", ec="#c07b28")
    arrow((3.8, 9.55), (6.0, 9.55))
    ax.text(4.9, 9.75, "激励 u(t)", ha="center", fontsize=10)
    # reference tap to analyser (right side rail)
    ax.plot([4.9, 4.9, 16.1, 16.1, 15.4], [9.55, 10.35, 10.35, 3.6, 3.6],
            color="#777777", lw=1.2, ls="--", zorder=2)
    ax.text(10.4, 10.45, "参考通道 u(t)", fontsize=9.5, color="#555555",
            ha="center")

    # --- servo valve on cylinder ---
    box(5.8, 6.6, 4.8, 1.3, "电液伺服阀（直接安装在缸体上）", fc="#eef3fa")
    arrow((7.5, 8.9), (7.5, 7.9))
    ax.text(7.75, 8.35, "i", fontsize=10, style="italic")

    # supply / tank
    ax.add_patch(Circle((1.6, 7.25), 0.5, fc="#eef3fa", ec="#1f6fb4", lw=1.4,
                        zorder=3))
    ax.text(1.6, 7.25, "泵", ha="center", va="center", fontsize=10.5, zorder=4)
    ax.text(1.6, 6.45, "恒压泵站 p$_S$", ha="center", fontsize=9.5)
    ax.plot([2.1, 5.8], [7.25, 7.25], color="#333333", lw=1.6, zorder=2)
    # accumulator
    ax.add_patch(Circle((3.7, 8.25), 0.42, fc="#e8f2ea", ec="#3a8f5f", lw=1.4,
                        zorder=3))
    ax.plot([3.7, 3.7], [7.25, 7.83], color="#3a8f5f", lw=1.5, zorder=2)
    ax.text(3.7, 8.95, "蓄能器（就近稳压）", ha="center", fontsize=9.5)
    # tank line
    ax.plot([10.6, 11.7, 11.7], [7.0, 7.0, 6.1], color="#333333", lw=1.4,
            zorder=2)
    ax.plot([11.35, 12.05], [6.1, 6.1], color="#333333", lw=1.4)
    ax.plot([11.45, 11.95], [5.95, 5.95], color="#333333", lw=1.2)
    ax.plot([11.55, 11.85], [5.8, 5.8], color="#333333", lw=1.0)
    ax.text(12.25, 6.0, "回油箱 T", fontsize=9.5, va="center")

    # --- cylinder ---
    cyl_x, cyl_y, cyl_w, cyl_h = 5.0, 4.0, 6.6, 1.6
    ax.add_patch(Rectangle((cyl_x, cyl_y), cyl_w, cyl_h, fc="#f5f5f5",
                           ec="#222222", lw=1.8, zorder=3))
    # piston + rod
    ax.add_patch(Rectangle((7.15, cyl_y + 0.06), 0.35, cyl_h - 0.12,
                           fc="#9db8d2", ec="#222222", lw=1.2, zorder=4))
    ax.add_patch(Rectangle((3.2, 4.62), 3.95, 0.36, fc="#c9c9c9",
                           ec="#222222", lw=1.2, zorder=3))
    ax.text(6.1, 5.25, "A 腔", fontsize=10, ha="center", zorder=5)
    ax.text(9.6, 5.25, "B 腔", fontsize=10, ha="center", zorder=5)
    # ports to valve
    ax.plot([6.2, 6.2], [5.6, 6.6], color="#333333", lw=1.6, zorder=2)
    ax.plot([10.2, 10.2], [5.6, 6.6], color="#333333", lw=1.6, zorder=2)
    # pressure transducers
    for px, lab in ((6.2, "p$_A$"), (10.2, "p$_B$")):
        ax.add_patch(Circle((px + 0.45, 6.15), 0.18, fc="white", ec=C2,
                            lw=1.4, zorder=5))
        ax.plot([px, px + 0.28], [6.15, 6.15], color=C2, lw=1.2, zorder=4)
        ax.text(px + 0.45, 6.55, lab, color=C2, fontsize=10, ha="center")
    ax.text(8.35, 6.12, "压力传感器\n（辅助通道）", color=C2, fontsize=8.5,
            ha="center", va="center", zorder=6,
            bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
    ax.plot([10.83, 13.4, 13.4], [6.15, 6.15, 4.9], color=C2, lw=1.1, ls="--",
            zorder=2)

    # --- load mass on guideway ---
    box(1.0, 4.0, 2.2, 1.6, "负载质量\nm$_t$", fc="#eeeeee", ec="#222222")
    # guide hatch
    ax.plot([0.6, 12.0], [3.75, 3.75], color="#555555", lw=1.2)
    for gx in np.arange(0.7, 12.0, 0.55):
        ax.plot([gx, gx - 0.22], [3.75, 3.5], color="#888888", lw=0.9)
    ax.text(2.5, 3.28, "导轨（约束为直线运动）", fontsize=9, color="#555555")

    # displacement sensor
    box(0.9, 1.7, 3.4, 0.85, "位移传感器 x(t)\n（磁致伸缩 / 光栅）", fc="#fdeaea",
        ec=C2, fs=9.5)
    ax.plot([2.1, 2.1], [2.55, 4.0], color=C2, lw=1.3, zorder=2)

    # analyser
    box(11.6, 1.7, 3.8, 3.2,
        "频响分析仪 /\n数据采集系统\n（FFT・相关法）\n输出 Bode 图", fc="#e8f2ea",
        ec="#3a8f5f", fs=10)
    arrow((4.3, 2.12), (11.6, 2.12), color=C2)
    ax.text(7.9, 2.32, "响应通道 x(t)", fontsize=9.5, color=C2, ha="center")

    ax.set_title("液压缸（阀控缸系统）频率响应测试原理示意图", fontsize=13,
                 pad=12)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig1_rig.png", dpi=190)
    plt.close(fig)


# ============================================================================
# Fig 2 -- definition of amplitude ratio & phase
# ============================================================================
def fig2():
    f = 5.0
    T = 1 / f
    t = np.linspace(0, 2.4 * T, 1200)
    Au, Axm, phi = 1.0, 0.65, -40.0
    u = Au * np.sin(2 * np.pi * f * t)
    x = Axm * np.sin(2 * np.pi * f * t + np.radians(phi))

    fig, ax = plt.subplots(figsize=(10.5, 4.4))
    ax.plot(t * 1e3, u, color=C1, lw=2, label="输入指令 u(t)（幅值 A$_u$）")
    ax.plot(t * 1e3, x, color=C2, lw=2,
            label="活塞位移 x(t)（幅值 A$_x$，滞后 φ）")
    ax.axhline(0, color="#999999", lw=0.8)

    # amplitude arrows
    tp_u = (T / 4) * 1e3
    ax.annotate("", xy=(tp_u, Au), xytext=(tp_u, 0),
                arrowprops=dict(arrowstyle="<->", color=C1, lw=1.4))
    ax.text(tp_u + 4, 0.52, "A$_u$", color=C1, fontsize=12)
    tp_x = (T / 4 - phi / 360 * T) * 1e3
    ax.annotate("", xy=(tp_x, Axm), xytext=(tp_x, 0),
                arrowprops=dict(arrowstyle="<->", color=C2, lw=1.4))
    ax.text(tp_x + 4, 0.34, "A$_x$", color=C2, fontsize=12)

    # time delay between zero crossings
    t0u = T * 1e3            # u zero-cross (rising) at t=T
    t0x = (T - phi / 360 * T) * 1e3
    ax.annotate("", xy=(t0x, -0.88), xytext=(t0u, -0.88),
                arrowprops=dict(arrowstyle="<->", color="#333333", lw=1.4))
    ax.text((t0u + t0x) / 2, -0.8, "Δt", ha="center", fontsize=12)
    ax.plot([t0u, t0u], [-0.92, 0], color="#888888", lw=0.9, ls=":")
    ax.plot([t0x, t0x], [-0.92, 0], color="#888888", lw=0.9, ls=":")

    ax.text(0.985, 0.03,
            "幅值比  A(ω) = 20·lg(A$_x$/A$_{x,ref}$)  [dB]\n"
            "相位差  φ(ω) = -360°·Δt / T\n"
            "（本例：A$_x$/A$_u$ = 0.65 → -3.7 dB，φ = -40°）",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=10.5,
            bbox=dict(fc="#fffbe8", ec="#c9b458", lw=1))
    ax.set_xlabel("时间 [ms]")
    ax.set_ylabel("归一化幅值")
    ax.set_ylim(-1.35, 1.25)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_title(f"单一频率点（f = {f:.0f} Hz）的稳态正弦响应："
                 "幅值比与相位差的定义", fontsize=12.5)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fig2_def.png", dpi=190)
    plt.close(fig)


# ============================================================================
# Fig 3 -- Bode of velocity (PT2) and position (IT2) responses
# ============================================================================
def fig3():
    f = np.logspace(-0.5, 2.3, 700)
    w = 2 * np.pi * f
    Gv = pt2(w, wh, Dh)          # velocity / valve input, DC-normalised
    Gx = Gv / (1j * w / wh)      # position, normalised so |Gx|=0dB at w=wh asymptote

    fig, axs = plt.subplots(2, 2, figsize=(11.5, 7.0), sharex=True)

    # ---- velocity ----
    ax = axs[0, 0]
    ax.semilogx(f, 20 * np.log10(np.abs(Gv)), color=C1, lw=2)
    ax.axhline(-3, color="#888888", lw=1, ls="--")
    fr = fh * np.sqrt(1 - 2 * Dh ** 2)
    Mr = 1 / (2 * Dh * np.sqrt(1 - Dh ** 2))
    ax.annotate(f"谐振峰 M$_r$ = {20*np.log10(Mr):.1f} dB\n"
                f"f$_r$ ≈ f$_h$ = {fh:.1f} Hz",
                xy=(fr, 20 * np.log10(Mr)), xytext=(1.6, 12),
                arrowprops=dict(arrowstyle="->", color="#333333"),
                fontsize=10)
    i3 = np.argmin(np.abs(20 * np.log10(np.abs(Gv[f > fh])) - (-3)))
    f3 = f[f > fh][i3]
    ax.plot(f3, -3, "o", color=C2, ms=6)
    ax.annotate(f"-3 dB 带宽 ≈ {f3:.0f} Hz", xy=(f3, -3), xytext=(30, 5),
                arrowprops=dict(arrowstyle="->", color=C2), color=C2,
                fontsize=10)
    ax.text(1.0, -30, "低频渐近线 0 dB/dec\n（比例特性）", fontsize=9.5,
            color="#555555")
    ax.text(60, -38, "-40 dB/dec", fontsize=9.5, color="#555555")
    ax.set_ylabel("幅值 [dB]")
    ax.set_ylim(-60, 22)
    ax.set_title("速度响应 v/u（PT2 环节）", fontsize=12)

    ax = axs[1, 0]
    ax.semilogx(f, np.degrees(np.angle(Gv)), color=C1, lw=2)
    ax.axvline(fh, color="#888888", lw=1, ls="--")
    ax.axhline(-90, color="#888888", lw=1, ls="--")
    ax.plot(fh, -90, "s", color=C3, ms=6)
    ax.annotate("f = f$_h$ 处相位恰为 -90°", xy=(fh, -90), xytext=(1.2, -140),
                arrowprops=dict(arrowstyle="->", color=C3), color=C3,
                fontsize=10)
    ax.set_ylabel("相位 [°]")
    ax.set_xlabel("频率 [Hz]")
    ax.set_ylim(-190, 10)
    ax.set_yticks([0, -45, -90, -135, -180])

    # ---- position ----
    ax = axs[0, 1]
    ax.semilogx(f, 20 * np.log10(np.abs(Gx)), color=C2, lw=2)
    ax.axvline(fh, color="#888888", lw=1, ls="--")
    ax.text(0.55, 26, "-20 dB/dec\n（积分特性）", fontsize=9.5, color="#555555")
    ax.text(48, -46, "-60 dB/dec", fontsize=9.5, color="#555555")
    ax.annotate(f"液压固有频率\nf$_h$ = {fh:.1f} Hz", xy=(fh, 8),
                xytext=(2.3, -25),
                arrowprops=dict(arrowstyle="->", color="#333333"), fontsize=10)
    ax.set_ylim(-70, 45)
    ax.set_title("位置响应 x/u（IT2 环节，含积分）", fontsize=12)

    ax = axs[1, 1]
    ax.semilogx(f, np.degrees(np.angle(Gx)) - 360 *
                (np.degrees(np.angle(Gx)) > 0), color=C2, lw=2)
    ax.axhline(-90, color="#888888", lw=1, ls="--")
    ax.axhline(-270, color="#888888", lw=1, ls="--")
    ax.axvline(fh, color="#888888", lw=1, ls="--")
    ax.text(0.55, -82, "低频从 -90° 起步（积分环节）", fontsize=9.5,
            color="#555555")
    ax.text(30, -262, "高频趋向 -270°", fontsize=9.5, color="#555555")
    ax.set_xlabel("频率 [Hz]")
    ax.set_ylim(-290, -70)
    ax.set_yticks([-90, -135, -180, -225, -270])

    fig.suptitle("阀控缸降阶线性模型的典型频率响应"
                 f"（ω$_h$ = {wh:.0f} rad/s，D$_h$ = {Dh:.2f}，阀动态忽略）",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(f"{OUT}/fig3_bode.png", dpi=190)
    plt.close(fig)


# ============================================================================
# Fig 4 -- influence of damping ratio
# ============================================================================
def fig4():
    f = np.logspace(0.3, 2.2, 600)
    w = 2 * np.pi * f
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4))
    for D, c in zip((0.05, 0.1, 0.2, 0.4), (C2, C1, C3, C4)):
        G = pt2(w, wh, D)
        Mr = 1 / (2 * D * np.sqrt(1 - D ** 2)) if D < 0.707 else 1
        ax1.semilogx(f, 20 * np.log10(np.abs(G)), color=c, lw=2,
                     label=f"D$_h$ = {D:.2f}（M$_r$ = {Mr:.1f}）")
        ax2.semilogx(f, np.degrees(np.angle(G)), color=c, lw=2)
    ax1.axhline(20 * np.log10(1.3), color="#888888", ls="--", lw=1.2)
    ax1.text(2.4, 20 * np.log10(1.3) + 0.8,
             "M = 1.3 准则（+2.3 dB，Viersma 1980）", fontsize=9.5,
             color="#555555")
    ax1.set_xlabel("频率 [Hz]"); ax1.set_ylabel("幅值 [dB]")
    ax1.set_ylim(-40, 24); ax1.legend(fontsize=9.5, loc="lower left")
    ax1.set_title("阻尼比对谐振峰的影响（幅频）", fontsize=12)
    ax2.axhline(-90, color="#888888", ls="--", lw=1)
    ax2.axvline(fh, color="#888888", ls="--", lw=1)
    ax2.set_xlabel("频率 [Hz]"); ax2.set_ylabel("相位 [°]")
    ax2.set_yticks([0, -45, -90, -135, -180])
    ax2.set_title("阻尼比对相频特性的影响", fontsize=12)
    ax2.text(fh * 1.08, -30, "f$_h$", fontsize=11)
    fig.suptitle("液压缸阻尼比 D$_h$ 通常仅 0.05~0.2 —— 谐振峰尖锐，"
                 "测试时须限幅保护", fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(f"{OUT}/fig4_damping.png", dpi=190)
    plt.close(fig)


# ============================================================================
# Fig 5 -- piston-position dependence of omega_h
# ============================================================================
def fig5():
    xs = np.linspace(0.02, 0.98, 300) * Lst
    VA = V0 + Ap * xs
    VB = V0 + Ap * (Lst - xs)
    wh_x = np.sqrt(be * Ap ** 2 / mt * (1 / VA + 1 / VB))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4))
    ax1.plot(xs / Lst * 100, wh_x / 2 / np.pi, color=C1, lw=2.2)
    imin = np.argmin(wh_x)
    fmin = wh_x[imin] / 2 / np.pi
    ax1.plot(xs[imin] / Lst * 100, fmin, "o", color=C2, ms=7)
    ax1.annotate(f"中位刚度最低\nf$_h$,min = {fmin:.1f} Hz\n→ 规定的测试位置",
                 xy=(50, fmin), xytext=(30, fmin + 4.5),
                 arrowprops=dict(arrowstyle="->", color=C2), color=C2,
                 fontsize=10)
    ax1.set_ylim(fmin - 1.5, fmin + 11)
    ax1.set_xlabel("活塞位置 x / 行程 L [%]")
    ax1.set_ylabel("液压固有频率 f$_h$ [Hz]")
    ax1.set_title("f$_h$ 随活塞位置的变化（对称缸）", fontsize=12)

    f = np.logspace(0.5, 2.2, 500)
    w = 2 * np.pi * f
    for pos, c, ls in ((0.10, C3, "-"), (0.50, C1, "-"), (0.90, C4, "--")):
        VA_ = V0 + Ap * pos * Lst
        VB_ = V0 + Ap * (1 - pos) * Lst
        wh_ = np.sqrt(be * Ap ** 2 / mt * (1 / VA_ + 1 / VB_))
        G = pt2(w, wh_, Dh)
        ax2.semilogx(f, 20 * np.log10(np.abs(G)), color=c, ls=ls, lw=2,
                     label=f"x/L = {pos:.0%}（f$_h$ = {wh_/2/np.pi:.0f} Hz）")
    ax2.text(4.2, -31, "10% 与 90% 两条曲线重合（对称缸）", fontsize=9,
             color="#555555")
    ax2.set_xlabel("频率 [Hz]"); ax2.set_ylabel("幅值 [dB]")
    ax2.set_ylim(-35, 22); ax2.legend(fontsize=9.5, loc="upper left")
    ax2.set_title("不同活塞位置下的速度幅频特性", fontsize=12)
    fig.suptitle("测试必须规定活塞位置：中位最不利，行程两端 f$_h$ 升高",
                 fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(f"{OUT}/fig5_position.png", dpi=190)
    plt.close(fig)


# ============================================================================
# Fig 6 -- nonlinear simulation: amplitude dependence (closed-loop test)
# ============================================================================
def sim_closed_loop_frf(A_arr, freqs):
    """RK4 simulation of the nonlinear valve-cylinder model under a slow
    position P-loop, sinusoidal reference; returns complex FRF x/x_ref."""
    m = len(A_arr)
    G = np.zeros((len(freqs), m), dtype=complex)

    for k, fr in enumerate(freqs):
        w0 = 2 * np.pi * fr
        T = 1.0 / fr
        n_settle = max(3, int(np.ceil(1.2 / T)))
        n_meas = 5
        t_end = (n_settle + n_meas) * T
        dt = min(2e-4, T / 600)
        nst = int(round(t_end / dt))
        t_meas = n_settle * T

        x = np.zeros(m); v = np.zeros(m); pL = np.zeros(m)
        xv = np.zeros(m); xvd = np.zeros(m)
        Cx = np.zeros(m, dtype=complex)
        Cr = np.zeros(m, dtype=complex)

        def deriv(t, x, v, pL, xv, xvd):
            xref = A_arr * np.sin(w0 * t)
            u = np.clip(Kp * (xref - x), -1.0, 1.0)
            xvdd = wv * wv * (u - xv) - 2 * Dv * wv * xvd
            xve = np.sign(xv) * np.maximum(np.abs(xv) - dz, 0.0) / (1 - dz)
            QL = Cv * xve * np.sqrt(np.maximum(Ps - np.sign(xve) * pL, 1e3))
            pLd = (4 * be / Vt_mid) * (QL - Ap * v - Cl * pL)
            vd = (Ap * pL - Df * v - Fc * np.tanh(v / vs)) / mt
            return v, vd, pLd, xvd, xvdd

        t = 0.0
        for i in range(nst):
            k1 = deriv(t, x, v, pL, xv, xvd)
            k2 = deriv(t + dt / 2, x + dt / 2 * k1[0], v + dt / 2 * k1[1],
                       pL + dt / 2 * k1[2], xv + dt / 2 * k1[3],
                       xvd + dt / 2 * k1[4])
            k3 = deriv(t + dt / 2, x + dt / 2 * k2[0], v + dt / 2 * k2[1],
                       pL + dt / 2 * k2[2], xv + dt / 2 * k2[3],
                       xvd + dt / 2 * k2[4])
            k4 = deriv(t + dt, x + dt * k3[0], v + dt * k3[1],
                       pL + dt * k3[2], xv + dt * k3[3], xvd + dt * k3[4])
            x = x + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
            v = v + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
            pL = np.clip(pL + dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]),
                         -Ps, Ps)
            xv = xv + dt / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
            xvd = xvd + dt / 6 * (k1[4] + 2 * k2[4] + 2 * k3[4] + k4[4])
            t += dt
            if t >= t_meas:
                e = np.exp(-1j * w0 * t)
                Cx += x * e * dt
                Cr += A_arr * np.sin(w0 * t) * e * dt
        G[k] = Cx / Cr
        print(f"  f = {fr:6.2f} Hz done "
              + "  ".join(f"|G|={abs(g):.3f}" for g in G[k]))
    return G


def fig6():
    freqs = np.logspace(np.log10(0.3), np.log10(40), 14)
    A_arr = np.array([0.5e-3, 5e-3, 40e-3])
    print("fig6: nonlinear closed-loop FRF simulation ...")
    G = sim_closed_loop_frf(A_arr, freqs)

    # linear small-signal closed loop for reference
    f_lin = np.logspace(np.log10(0.3), np.log10(40), 400)
    w = 2 * np.pi * f_lin
    L = (Kp * Kv0 / (1j * w)) * pt2(w, wh, Dh) * pt2(w, wv, Dv)
    Gcl = L / (1 + L)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6))
    ax1.semilogx(f_lin, 20 * np.log10(np.abs(Gcl)), "k--", lw=1.6,
                 label="线性小信号模型")
    ax2.semilogx(f_lin, np.degrees(np.unwrap(np.angle(Gcl))), "k--", lw=1.6)
    labs = ("±0.5 mm（小幅值：摩擦/遮盖主导）",
            "±5 mm（中幅值：接近线性）",
            "±40 mm（大幅值：流量饱和限制）")
    for j, (lab, c) in enumerate(zip(labs, (C3, C1, C2))):
        ax1.semilogx(freqs, 20 * np.log10(np.abs(G[:, j])), "-o", color=c,
                     lw=1.8, ms=5, label=lab)
        ph = np.degrees(np.angle(G[:, j]))
        ph[ph > 30] -= 360
        ax2.semilogx(freqs, ph, "-o", color=c, lw=1.8, ms=5)
    ax1.axhline(-3, color="#888888", ls="--", lw=1)
    ax1.text(0.35, -2.6, "-3 dB", fontsize=9.5, color="#555555")
    ax1.set_xlabel("频率 [Hz]"); ax1.set_ylabel("幅值 20·lg|x/x$_{ref}$| [dB]")
    ax1.set_ylim(-32, 6); ax1.legend(fontsize=9, loc="lower left")
    ax1.set_title("闭环幅频特性随激励幅值的变化", fontsize=12)
    ax2.axhline(-90, color="#888888", ls="--", lw=1)
    ax2.set_xlabel("频率 [Hz]"); ax2.set_ylabel("相位 [°]")
    ax2.set_ylim(-230, 15)
    ax2.set_title("闭环相频特性随激励幅值的变化", fontsize=12)
    fig.suptitle("非线性模型仿真：同一系统在不同激励幅值下测得的频响并不相同"
                 "（位置闭环测试，P 控制器）", fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(f"{OUT}/fig6_amplitude.png", dpi=190)
    plt.close(fig)


# ============================================================================
# Fig 7 -- excitation signals
# ============================================================================
def fig7():
    fig, axs = plt.subplots(2, 2, figsize=(11.5, 6.2))

    # (a) stepped sine
    ax = axs[0, 0]
    t = np.linspace(0, 9, 4000)
    y = np.where(t < 3, np.sin(2 * np.pi * 0.8 * t),
                 np.where(t < 6, np.sin(2 * np.pi * 2 * (t - 3)),
                          np.sin(2 * np.pi * 4.5 * (t - 6))))
    ax.plot(t, y, color=C1, lw=1.4)
    for tx, lab in ((1.5, "f$_1$"), (4.5, "f$_2$"), (7.5, "f$_3$")):
        ax.text(tx, 1.18, lab, ha="center", fontsize=10.5)
    ax.axvline(3, color="#aaaaaa", ls="--", lw=1)
    ax.axvline(6, color="#aaaaaa", ls="--", lw=1)
    ax.set_title("(a) 逐点定频正弦（stepped sine）——精度最高、最慢",
                 fontsize=11)
    ax.set_ylim(-1.4, 1.5)

    # (b) chirp
    ax = axs[0, 1]
    t = np.linspace(0, 9, 6000)
    f0, f1 = 0.4, 5.0
    y = np.sin(2 * np.pi * f0 * (np.exp(t / 9 * np.log(f1 / f0)) - 1)
               * 9 / np.log(f1 / f0))
    ax.plot(t, y, color=C2, lw=1.2)
    ax.set_title("(b) 扫频信号（chirp）——频率连续上升，测试快", fontsize=11)
    ax.set_ylim(-1.4, 1.5)

    # (c) multisine
    ax = axs[1, 0]
    t = np.linspace(0, 9, 6000)
    rng = np.random.default_rng(7)
    y = sum(np.sin(2 * np.pi * fk * t + ph) for fk, ph in
            zip((0.5, 1.1, 2.3, 3.7, 5.3), rng.uniform(0, 2 * np.pi, 5)))
    ax.plot(t, y / np.max(np.abs(y)), color=C3, lw=1.2)
    ax.set_title("(c) 多正弦（multisine）——一次注入一组频率", fontsize=11)
    ax.set_xlabel("时间 [s]")
    ax.set_ylim(-1.4, 1.5)

    # (d) PRBS
    ax = axs[1, 1]
    rng = np.random.default_rng(3)
    bits = rng.integers(0, 2, 60) * 2 - 1
    t = np.linspace(0, 9, 6000)
    y = bits[np.minimum((t / 0.15).astype(int), 59)]
    ax.plot(t, y, color=C4, lw=1.2)
    ax.set_title("(d) PRBS ——宽频、简便；对强非线性对象激励不充分\n"
                 "（推荐改用 PRMS 或多正弦，Leontaritis & Billings 1987）",
                 fontsize=10.5)
    ax.set_xlabel("时间 [s]")
    ax.set_ylim(-1.6, 1.7)

    fig.suptitle("频响测试常用激励信号（另见《液压伺服系统》中译本第 5 章）",
                 fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(f"{OUT}/fig7_signals.png", dpi=190)
    plt.close(fig)


# ============================================================================
# Fig 8 -- entrained air / effective bulk modulus
# ============================================================================
def fig8():
    boil = 1.5e9
    kappa = 1.4
    alpha = np.linspace(0, 0.02, 300)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4))
    for p_bar, c in zip((35, 70, 140, 210), (C2, C4, C1, C3)):
        p = p_bar * 1e5
        beff = 1.0 / ((1 - alpha) / boil + alpha / (kappa * p))
        ax1.plot(alpha * 100, beff / 1e9, color=c, lw=2,
                 label=f"p = {p_bar} bar")
    ax1.set_xlabel("体积含气率 α [%]")
    ax1.set_ylabel("有效体积弹性模量 β$_{eff}$ [GPa]")
    ax1.legend(fontsize=10)
    ax1.set_title("混入空气使 β$_{eff}$ 急剧下降（压力越低越严重）",
                  fontsize=11.5)

    f = np.logspace(0.5, 2.2, 500)
    w = 2 * np.pi * f
    p = 100e5
    for a, c, ls in ((0.0, C1, "-"), (0.005, C3, "--"), (0.02, C2, "-.")):
        beff = 1.0 / ((1 - a) / boil + a / (kappa * p))
        wh_a = wh * np.sqrt(beff / boil)   # α=0 时取标称 f_h
        G = pt2(w, wh_a, Dh)
        ax2.semilogx(f, 20 * np.log10(np.abs(G)), color=c, ls=ls, lw=2,
                     label=f"α = {a:.1%} → f$_h$ = {wh_a/2/np.pi:.1f} Hz")
    ax2.set_xlabel("频率 [Hz]"); ax2.set_ylabel("幅值 [dB]")
    ax2.set_ylim(-35, 22); ax2.legend(fontsize=10, loc="lower left")
    ax2.set_title("含气量对测得谐振频率的影响（p = 100 bar）", fontsize=11.5)
    fig.suptitle("排气不彻底是频响测试最常见的误差源：实测 f$_h$ 明显低于估算值时"
                 "先查空气", fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(f"{OUT}/fig8_air.png", dpi=190)
    plt.close(fig)


if __name__ == "__main__":
    fig1(); print("fig1 ok")
    fig2(); print("fig2 ok")
    fig3(); print("fig3 ok")
    fig4(); print("fig4 ok")
    fig5(); print("fig5 ok")
    fig7(); print("fig7 ok")
    fig8(); print("fig8 ok")
    fig6(); print("fig6 ok")
    print("all figures ->", OUT)
