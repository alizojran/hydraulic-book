# -*- coding: utf-8 -*-
"""Generate all figures for 《小液滴质量测量方法讲解》.

All figures are self-produced (matplotlib drawings + numerical simulation of a
charged-droplet trajectory with air drag). Output -> drop_figs/*.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "dejavusans"
plt.rcParams["font.size"] = 10.5
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

OUT = "drop_figs"
os.makedirs(OUT, exist_ok=True)

C1, C2, C3, C4 = "#1f6fb4", "#d1495b", "#3a8f5f", "#8a6bbf"

# ---------------------------------------------------------------- physics ---
RHO = 1000.0        # droplet density [kg/m^3] (water-like)
RHO_AIR = 1.2       # air density [kg/m^3]
MU_AIR = 1.81e-5    # air viscosity [Pa*s]
GAMMA = 0.072       # surface tension [N/m]
EPS0 = 8.854e-12
G = 9.81

F_DROP = 450.0      # droplets per second (400~500)

# deflection geometry (jet fires vertically downward, E field horizontal)
V0 = 8.0            # initial axial speed [m/s]
E_FIELD = 3.0e5     # field between plates [V/m]
Z1 = 5e-3           # charge point -> plate entrance [m]
LP = 15e-3          # plate length [m]
Z_DET = 40e-3       # detection plane [m]
Q0, D0 = 0.3e-12, 100e-6   # induction charge 0.3 pC at d = 100 um, q ~ d


def drop_mass(d):
    return RHO * np.pi / 6 * d ** 3


def drag_acc(vx, vz, d, m):
    """Stokes drag with Schiller-Naumann correction, per velocity component."""
    v = np.hypot(vx, vz)
    if v < 1e-12:
        return 0.0, 0.0
    Re = RHO_AIR * v * d / MU_AIR
    f = 3 * np.pi * MU_AIR * d * v * (1 + 0.15 * Re ** 0.687)
    return -f * vx / v / m, -f * vz / v / m


def sim_trajectory(d, q=None, drag=True, dt=2e-5):
    """Integrate droplet flight; z axial (down, gravity), x transverse (E).
    Returns arrays z, x and impact velocity components."""
    m = drop_mass(d)
    if q is None:
        q = Q0 * d / D0
    x = z = 0.0
    vx, vz = 0.0, V0
    Z, X = [0.0], [0.0]

    def acc(x_, z_, vx_, vz_):
        ax = q * E_FIELD / m if (Z1 <= z_ <= Z1 + LP) else 0.0
        az = G
        if drag:
            dx_, dz_ = drag_acc(vx_, vz_, d, m)
            ax += dx_; az += dz_
        return ax, az

    while z < Z_DET:
        # RK4 on (x, z, vx, vz)
        a1x, a1z = acc(x, z, vx, vz)
        k1 = (vx, vz, a1x, a1z)
        a2x, a2z = acc(x + dt / 2 * k1[0], z + dt / 2 * k1[1],
                       vx + dt / 2 * k1[2], vz + dt / 2 * k1[3])
        k2 = (vx + dt / 2 * k1[2], vz + dt / 2 * k1[3], a2x, a2z)
        a3x, a3z = acc(x + dt / 2 * k2[0], z + dt / 2 * k2[1],
                       vx + dt / 2 * k2[2], vz + dt / 2 * k2[3])
        k3 = (vx + dt / 2 * k2[2], vz + dt / 2 * k2[3], a3x, a3z)
        a4x, a4z = acc(x + dt * k3[0], z + dt * k3[1],
                       vx + dt * k3[2], vz + dt * k3[3])
        k4 = (vx + dt * k3[2], vz + dt * k3[3], a4x, a4z)
        x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        z += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        vx += dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        vz += dt / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
        Z.append(z); X.append(x)
    return np.array(Z), np.array(X), vx, vz


def ballistic_deflection(d, q=None):
    """Text-book formula: constant axial speed V0, no drag, no gravity."""
    m = drop_mass(d)
    if q is None:
        q = Q0 * d / D0
    a = q * E_FIELD / m
    tL = LP / V0
    y_in = 0.5 * a * tL ** 2
    y_out = a * tL * (Z_DET - Z1 - LP) / V0
    return y_in + y_out


# ============================================================================
# Fig 1 -- method selection flowchart
# ============================================================================
def fig1():
    fig, ax = plt.subplots(figsize=(11.0, 5.6))
    ax.set_xlim(0, 16); ax.set_ylim(0, 10)
    ax.axis("off"); ax.grid(False)

    def box(x, y, w, h, text, fc="#eef3fa", ec=C1, fs=10.5):
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=1.5, zorder=3))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, zorder=4)

    def arrow(p0, p1, label=None, dx=0.15):
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", lw=1.6,
                                     color="#333333", mutation_scale=14,
                                     zorder=2))
        if label:
            ax.text((p0[0] + p1[0]) / 2 + dx, (p0[1] + p1[1]) / 2, label,
                    fontsize=10, color=C2, ha="left", va="center")

    box(6.0, 8.4, 4.0, 1.3, "需要逐滴数据？\n（散布、卫星滴、异常滴）",
        fc="#fdf3e3", ec="#c07b28")
    box(1.2, 5.6, 4.0, 1.3, "需要在线连续监测？", fc="#fdf3e3", ec="#c07b28")
    box(10.8, 5.6, 4.0, 1.3, "液体导电（水基）\n且允许带电？", fc="#fdf3e3",
        ec="#c07b28")

    box(0.4, 2.2, 3.4, 1.7, "称重平均法\n（标定/验收，<0.5%）", fc="#e8f2ea",
        ec=C3)
    box(4.2, 2.2, 3.4, 1.7, "科氏流量计法\n（在线平均，实时）", fc="#e8f2ea",
        ec=C3)
    box(8.6, 2.2, 3.4, 1.7, "频闪成像法\n（逐滴体积，~3%）", fc="#e8f2ea",
        ec=C3)
    box(12.4, 2.2, 3.4, 1.7, "电场偏转法\n（逐滴在线监测 q/m）", fc="#e8f2ea",
        ec=C3)

    arrow((6.0, 9.0), (3.2, 6.9), "否")
    arrow((10.0, 9.0), (12.8, 6.9), "是")
    arrow((2.4, 5.6), (2.1, 3.9), "否")
    arrow((4.0, 5.6), (5.9, 3.9), "是")
    arrow((11.6, 5.6), (10.3, 3.9), "否 →\n成像", dx=-1.9)
    arrow((13.9, 5.6), (14.1, 3.9), "是")

    ax.text(8.0, 0.9, "无论选哪条路：称重平均法都作为“基准尺”定期标定其他方案",
            ha="center", fontsize=11, color="#333333",
            bbox=dict(fc="#fffbe8", ec="#c9b458", lw=1))
    ax.set_title("小液滴质量测量方案选型（400~500 滴/秒）", fontsize=13, pad=10)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fd1_flow.png", dpi=190)
    plt.close(fig)


# ============================================================================
# Fig 2 -- gravimetric feasibility
# ============================================================================
def fig2():
    t = np.logspace(0, 3, 300)          # collection time [s]
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    cases = ((50e-6, C3), (100e-6, C1), (200e-6, C4))
    for d, c in cases:
        m = drop_mass(d)
        m_ng = m * 1e12
        m_lab = (f"{m_ng:.0f} ng" if m_ng < 1000 else f"{m_ng/1000:.1f} μg")
        for res, ls, lw in ((1e-8, "-", 2.0), (1e-7, "--", 1.5)):  # 0.01/0.1 mg
            rel = res / (m * F_DROP * t) * 100
            lab = (f"d = {d*1e6:.0f} μm（单滴 {m_lab}）"
                   if res == 1e-8 else None)
            ax.loglog(t, rel, color=c, ls=ls, lw=lw, label=lab)
    ax.axhline(0.1, color=C2, lw=1.5, ls=":")
    ax.text(1.2, 0.115, "目标 0.1%", color=C2, fontsize=10)
    ax.annotate("d = 100 μm、0.01 mg 天平：\n约 40 s 即达 0.1%",
                xy=(42, 0.1), xytext=(120, 1.2),
                arrowprops=dict(arrowstyle="->", color="#333333"),
                fontsize=10, bbox=dict(fc="#fffbe8", ec="#c9b458", lw=1))
    from matplotlib.ticker import FuncFormatter
    fmt = FuncFormatter(lambda v, _: f"{v:g}")
    ax.xaxis.set_major_formatter(fmt)
    ax.yaxis.set_major_formatter(fmt)
    ax.set_xlabel("采集时间 [s]（450 滴/秒）")
    ax.set_ylabel("平均单滴质量的分辨率 [%]")
    ax.set_ylim(1e-3, 50)
    ax.legend(fontsize=9.5, loc="lower left",
              title="实线：0.01 mg 天平；虚线：0.10 mg 天平")
    ax.set_title("称重平均法可行性：靠“攒滴数”把分辨率做上去", fontsize=12.5)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fd2_gravimetric.png", dpi=190)
    plt.close(fig)


# ============================================================================
# Fig 3 -- deflection rig schematic (with a real simulated trajectory)
# ============================================================================
def fig3():
    fig, ax = plt.subplots(figsize=(10.8, 7.0))
    ax.set_xlim(-7.5, 9.5); ax.set_ylim(-45, 6)
    ax.axis("off"); ax.grid(False)
    mm = 1e3

    # nozzle
    ax.add_patch(Rectangle((-1.1, 2.0), 2.2, 3.2, fc="#dddddd", ec="#222222",
                           lw=1.5, zorder=3))
    ax.plot([-1.1, -0.25], [2.0, 0.2], color="#222222", lw=1.5)
    ax.plot([1.1, 0.25], [2.0, 0.2], color="#222222", lw=1.5)
    ax.text(0, 3.6, "喷嘴 / 喷射阀", ha="center", fontsize=10.5, zorder=4)
    ax.annotate("驱动脉冲 400~500 Hz", xy=(1.1, 3.6), xytext=(3.4, 3.4),
                arrowprops=dict(arrowstyle="->", color="#555555"), fontsize=9.5)

    # charging electrode at breakoff
    for sx in (-1.9, 1.1):
        ax.add_patch(Rectangle((sx, -3.6), 0.8, 2.6, fc="#fdeaea", ec=C2,
                               lw=1.5, zorder=3))
    ax.text(-4.6, -2.3, "感应充电电极\n（断裂点处，充电电压 V$_c$）", color=C2,
            ha="center", fontsize=10)
    ax.text(3.2, -2.3, "断裂成滴点\n（z = 0，滴带电 q）", ha="left", fontsize=9.5)

    # deflection plates: z from Z1 to Z1+LP  (plot y = -z[mm])
    zp0, zp1 = Z1 * mm, (Z1 + LP) * mm
    ax.add_patch(Rectangle((-3.2, -zp1), 0.7, zp1 - zp0, fc="#eef3fa", ec=C1,
                           lw=1.6, zorder=3))
    ax.add_patch(Rectangle((2.5, -zp1), 0.7, zp1 - zp0, fc="#eef3fa", ec=C1,
                           lw=1.6, zorder=3))
    ax.text(-5.4, -(zp0 + zp1) / 2, "偏转电极\n-HV", color=C1, ha="center",
            fontsize=10.5)
    ax.text(4.6, -(zp0 + zp1) / 2 + 1.5, "偏转电极 +HV\n板长 L = 15 mm\n"
            "E = 300 kV/m", color=C1, ha="left", fontsize=10)
    for yE in np.linspace(-zp1 + 2, -zp0 - 2, 4):
        ax.add_patch(FancyArrowPatch((-2.4, yE), (2.4, yE), arrowstyle="-|>",
                                     lw=1.0, color="#8ab0d0",
                                     mutation_scale=10, zorder=2))

    # trajectories: charged (deflected, transverse magnified 3x) and uncharged
    MAG = 3.0
    Z, X, _, _ = sim_trajectory(100e-6)
    yfin_true = np.interp(Z_DET, Z, X) * mm
    ax.plot(X * mm * MAG, -Z * mm, color=C2, lw=2.2, zorder=4)
    ax.plot([0, 0], [0, -Z_DET * mm], color="#999999", lw=1.2, ls="--",
            zorder=2)
    for zz in np.linspace(0.002, Z_DET - 0.002, 9):
        xi = np.interp(zz, Z, X) * MAG
        ax.add_patch(Circle((xi * mm, -zz * mm), 0.28, fc=C2, ec="none",
                            zorder=5))
    ax.text(-1.3, -41.5, "未充电滴\n（直落）", color="#777777", fontsize=9.5,
            ha="center")

    # detection plane
    ax.plot([-2.5, 8.0], [-Z_DET * mm, -Z_DET * mm], color=C3, lw=2)
    yfin = yfin_true * MAG
    ax.add_patch(FancyArrowPatch((0, -Z_DET * mm + 1.2), (yfin, -Z_DET * mm + 1.2),
                                 arrowstyle="<->", lw=1.4, color=C3,
                                 mutation_scale=12, zorder=4))
    ax.text(yfin / 2 + 0.9, -Z_DET * mm + 3.1,
            f"偏移量 y ≈ {yfin_true:.1f} mm（图中横向放大 3×）",
            color=C3, ha="left", fontsize=10.5)
    ax.text(8.2, -Z_DET * mm, "检测面 z = D = 40 mm\n（相机 / 位置敏感探测器）",
            color=C3, fontsize=10, va="center")

    # Faraday cup
    ax.add_patch(Rectangle((yfin - 1.6, -Z_DET * mm - 3.4), 3.2, 2.2,
                           fc="#f5f5f5", ec="#222222", lw=1.5, zorder=3))
    ax.text(yfin, -Z_DET * mm - 5.6, "法拉第杯 + 皮安表：I = q·f\n"
            "（0.3 pC × 450 Hz ≈ 0.14 nA）", ha="center", fontsize=9.5)

    # velocity measurement
    ax.annotate("双脉冲频闪 + 相机\n→ 轴向速度 v", xy=(-0.35, -8),
                xytext=(-7.0, -11),
                arrowprops=dict(arrowstyle="->", color="#555555"),
                fontsize=10, ha="center")

    ax.set_title("电场偏转法测量装置示意（轨迹为 100 μm 水滴、q = 0.3 pC 的"
                 "含阻力仿真结果，横向放大 3×）", fontsize=12.5, pad=10)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fd3_rig.png", dpi=190)
    plt.close(fig)


# ============================================================================
# Fig 4 -- charging limits (Rayleigh) vs induction charge
# ============================================================================
def fig4():
    d = np.logspace(np.log10(20e-6), np.log10(300e-6), 200)
    qR = 8 * np.pi * np.sqrt(EPS0 * GAMMA * (d / 2) ** 3)
    q_ind = Q0 * d / D0

    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    ax.loglog(d * 1e6, qR * 1e12, color=C2, lw=2.2,
              label="Rayleigh 极限 q$_R$（超过即库仑分裂）")
    ax.loglog(d * 1e6, 0.1 * qR * 1e12, color=C2, lw=1.4, ls="--",
              label="工程安全线（10% q$_R$）")
    ax.loglog(d * 1e6, q_ind * 1e12, color=C1, lw=2.2,
              label="典型感应充电量（本文取 q ∝ d，100 μm 处 0.3 pC）")
    ax.fill_between(d * 1e6, q_ind * 1e12 * 0.5, q_ind * 1e12 * 2,
                    color=C1, alpha=0.15, label="感应充电常见范围（×0.5~×2）")
    ax.annotate("100 μm 水滴：q$_R$ ≈ 7 pC，\n0.3 pC 仅为其 4%，安全",
                xy=(100, 7.1), xytext=(30, 0.45),
                arrowprops=dict(arrowstyle="->", color="#333333"),
                fontsize=10, bbox=dict(fc="#fffbe8", ec="#c9b458", lw=1))
    from matplotlib.ticker import FuncFormatter
    fmt = FuncFormatter(lambda v, _: f"{v:g}")
    ax.set_xticks([20, 30, 50, 100, 200, 300])
    ax.xaxis.set_major_formatter(fmt); ax.xaxis.set_minor_formatter(FuncFormatter(lambda v, _: ""))
    ax.yaxis.set_major_formatter(fmt)
    ax.set_xlabel("液滴直径 d [μm]")
    ax.set_ylabel("电荷量 q [pC]")
    ax.legend(fontsize=9.5, loc="upper left")
    ax.set_title("充电量的物理边界：感应充电工作点远低于 Rayleigh 极限",
                 fontsize=12.5)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fd4_charge.png", dpi=190)
    plt.close(fig)


# ============================================================================
# Fig 5 -- trajectory simulation & deflection sensitivity
# ============================================================================
def fig5():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.8))
    mm = 1e3

    # (a) trajectories
    zp0, zp1 = Z1 * mm, (Z1 + LP) * mm
    for d, c in ((60e-6, C3), (100e-6, C1), (150e-6, C4)):
        Z, X, vx, vz = sim_trajectory(d)
        v_end = np.hypot(vx, vz)
        ax1.plot(X * mm, -Z * mm, color=c, lw=2,
                 label=f"d = {d*1e6:.0f} μm（到达时 v = {v_end:.1f} m/s）")
    for xs in (-3.0, 3.0):
        ax1.plot([xs, xs], [-zp1, -zp0], color=C1, lw=5, alpha=0.5)
    ax1.text(-4.7, -(zp0 + zp1) / 2, "偏转板", color=C1, rotation=90,
             va="center", fontsize=10)
    ax1.axhline(-Z_DET * mm, color=C3, lw=1.5, ls="--")
    ax1.text(-4.7, -Z_DET * mm + 0.8, "检测面", color=C3, fontsize=10)
    ax1.set_xlabel("横向偏移 x [mm]"); ax1.set_ylabel("轴向飞行距离 z [mm]")
    ax1.set_xlim(-5.2, 10); ax1.legend(fontsize=9, loc="upper right")
    ax1.set_title("(a) 含空气阻力的轨迹仿真（q ∝ d）", fontsize=12)

    # (b) deflection vs diameter: simulation vs ballistic formula
    ds = np.linspace(50e-6, 200e-6, 24)
    y_sim = np.array([np.interp(Z_DET, *sim_trajectory(d)[:2]) for d in ds])
    y_bal = np.array([ballistic_deflection(d) for d in ds])
    ax2.plot(ds * 1e6, y_bal * mm, "k--", lw=1.6,
             label="简化公式（恒速、无阻力）")
    ax2.plot(ds * 1e6, y_sim * mm, color=C2, lw=2.2, label="数值仿真（含阻力、重力）")
    ax2.annotate("小滴端阻力使轴向减速、驻留\n时间变长 → 偏移比简化公式大\n"
                 "（100 μm 处约 +40%，50 μm\n处约 3 倍）——必须数值修正",
                 xy=(ds[3] * 1e6, y_sim[3] * mm),
                 xytext=(95, y_sim[3] * mm * 0.55),
                 arrowprops=dict(arrowstyle="->", color="#333333"),
                 fontsize=9.5, bbox=dict(fc="#fffbe8", ec="#c9b458", lw=1))
    ax2.set_xlabel("液滴直径 d [μm]"); ax2.set_ylabel("检测面偏移量 y [mm]")
    ax2.legend(fontsize=9.5)
    ax2.set_title("(b) 偏移量-直径灵敏度：简化公式 vs 仿真", fontsize=12)

    fig.suptitle(f"电场偏转法数值仿真（E = 300 kV/m，L = 15 mm，D = 40 mm，"
                 f"v$_0$ = {V0:.0f} m/s，q ∝ d、100 μm 处 0.3 pC）",
                 fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(f"{OUT}/fd5_traj.png", dpi=190)
    plt.close(fig)


# ============================================================================
# Fig 6 -- error budget comparison
# ============================================================================
def fig6():
    comps = [("电荷量 δq/q（法拉第杯 + 滴间散布）", 3.0),
             ("速度项 2·δv/v（v² 进入公式）", 2.0),
             ("场强 δE/E（电压/间距）", 1.0),
             ("偏移量 δy/y（成像分辨率）", 1.0),
             ("阻力修正残差（依赖滴径，需迭代）", 2.0)]
    rss = np.sqrt(sum(v ** 2 for _, v in comps))

    fig, ax = plt.subplots(figsize=(10.8, 4.8))
    names = [n for n, _ in comps] + ["偏转法合计（RSS）", "频闪成像法（3·δd/d）",
                                     "称重平均法"]
    vals = [v for _, v in comps] + [rss, 3.0, 0.2]
    colors = ["#9db8d2"] * len(comps) + [C2, C4, C3]
    yy = np.arange(len(names))[::-1]
    ax.barh(yy, vals, color=colors, ec="#333333", lw=0.8, height=0.62)
    for y, v in zip(yy, vals):
        ax.text(v + 0.08, y, f"{v:.1f}%", va="center", fontsize=10.5)
    ax.set_yticks(yy); ax.set_yticklabels(names, fontsize=10.5)
    ax.set_xlabel("对单滴质量的不确定度贡献 [%]（1σ，典型乐观取值）")
    ax.set_xlim(0, 6.2)
    ax.set_title("误差预算：偏转法做“绝对测量”不如成像法与称重法——"
                 "它的价值在于在线监测", fontsize=12)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fd6_budget.png", dpi=190)
    plt.close(fig)


if __name__ == "__main__":
    for d in (60e-6, 100e-6, 150e-6):
        Z, X, vx, vz = sim_trajectory(d)
        y = np.interp(Z_DET, Z, X)
        print(f"d = {d*1e6:5.0f} um  m = {drop_mass(d)*1e12:7.1f} ng  "
              f"y = {y*1e3:5.2f} mm  v_end = {np.hypot(vx, vz):.2f} m/s  "
              f"(ballistic {ballistic_deflection(d)*1e3:5.2f} mm)")
    fig1(); print("fd1 ok")
    fig2(); print("fd2 ok")
    fig3(); print("fd3 ok")
    fig4(); print("fd4 ok")
    fig5(); print("fd5 ok")
    fig6(); print("fd6 ok")
    print("all figures ->", OUT)
