#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 2 轮第 5 路：定义审计表（子问题 1 与 4 的裁决用）。

对若干 K 打印：定理 21 前提的可行集、两种约定（min_eps 与 max_feasible）下的 m2、
两者的 eps、以及 Psi 的严格区间 [下界, 上界]（Stern-Brocot 两侧夹逼，无浮点判决）。

Psi 的严格夹逼依据：
  区间 (delta, delta+eps) 含于 (dlo, dhi + eps_hi) 且包含 (dhi, dlo + eps_lo)，
  故 min 分母满足  simplest(dlo, dhi+eps_hi) <= Psi <= simplest(dhi, dlo+eps_lo)。

运行：20-experiments/.venv/bin/python c2r5_defaudit.py
"""
import sys
from fractions import Fraction as F

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts"
C1 = "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts"
sys.path.insert(0, HERE)
sys.path.insert(0, C1)
import c2r5_rig as R
from mpmath import mp, mpf

mp.dps = 60
OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def m(x):
    x = F(x)
    return mpf(x.numerator) / mpf(x.denominator)


DLO, DHI = R.delta_bounds()
L2 = R.ln2_bounds()
CIV = R.C_bounds()
KSTAR = 205632218873398596256
M = 92

p("#" * 72)
p("# 第 2 轮第 5 路：定义审计表（K* 属哪一个 m2、哪一种约定）")
p("# delta 区间宽度 = %s ；C 区间宽度 = %s" % (float(DHI - DLO), float(CIV[1] - CIV[0])))
p("#" * 72)


def audit(K, tag):
    """对一个 K 输出可行集、两种约定的 m2 与 eps、Psi 的严格区间。"""
    feas = []
    undecided = []
    for m2 in range(1, M + 1):
        d = R.feasible_decision(m2, M, K, DLO, DHI, CIV)
        if d is True:
            feas.append(m2)
        elif d is None:
            undecided.append(m2)
    m2_max = max(feas)
    Kf = F(K)
    # 廉价剪枝：eps(m2) >= A(m2)/(3K ln2_hi)；只精算靠近 m2_max 的候选
    ev = [t for t in feas if t >= m2_max - 8]
    cand = {}
    for t in ev:
        cand[t] = R.eps_bounds(t, M, Kf, DLO, DHI, L2)
    m2_star = min(cand, key=lambda t: cand[t][1])
    e_star = cand[m2_star]
    # 剪枝合法性：被剪掉的 m2 的 A 下界必须大于 m2_star 的 eps 上界
    thresh = e_star[1]
    assert all(F(R.A_of(t, M)) / (F(3) * Kf * L2[1]) > thresh for t in feas if t < m2_max - 8), \
        "剪枝不成立"
    # 约定一：min_eps；约定二：max_feasible
    e_argmin = e_star
    e_maxfeas = cand[m2_max]
    betaM = (R.rd(DLO + e_argmin[0]), R.ru(DHI + e_argmin[1]))
    betaF = (R.rd(DLO + e_maxfeas[0]), R.ru(DHI + e_maxfeas[1]))
    psiM_lo = R.simplest_fraction(DLO, betaM[1]).denominator
    psiM_hi = R.simplest_fraction(DHI, betaM[0]).denominator
    psiF_lo = R.simplest_fraction(DLO, betaF[1]).denominator
    psiF_hi = R.simplest_fraction(DHI, betaF[0]).denominator
    p("")
    p("[K = %s]（%s）" % (K, tag))
    p("     可行集 = {1, ..., %d}（共 %d 个；未定 %d 个 = %s）；m2 = m = %d 可行？ %s" % (
        m2_max, len(feas), len(undecided), undecided, M, M in feas))
    p("     min_eps 约定：m2 = %d，eps ∈ [%s, %s]" % (
        m2_star, mp.nstr(m(e_argmin[0]), 20), mp.nstr(m(e_argmin[1]), 20)))
    p("     max_feasible 约定：m2 = %d，eps ∈ [%s, %s]" % (
        m2_max, mp.nstr(m(e_maxfeas[0]), 20), mp.nstr(m(e_maxfeas[1]), 20)))
    p("     Psi（min_eps 约定）∈ [%d, %d]  %s" % (
        psiM_lo, psiM_hi, "（两界相等）" if psiM_lo == psiM_hi else "（未定）"))
    p("     Psi（max_feasible 约定）∈ [%d, %d]  %s" % (
        psiF_lo, psiF_hi, "（两界相等）" if psiF_lo == psiF_hi else "（未定）"))
    p("     两种约定是否同值？ %s" % (psiM_lo == psiF_lo == psiM_hi == psiF_hi))
    return feas, m2_star, m2_max, (psiM_lo, psiM_hi, psiF_lo, psiF_hi)


# ---------- 1. 可行门槛（m2 何时变可行） ----------
p("")
p("[1] m = 92 时各 m2 的可行门槛 K_thresh(m2) = geom(m2)*C*(92/m2)（升序即为 m2 的可行顺序）")
for m2 in [87, 88, 89, 90, 91, 92]:
    g = R.geom_bounds(m2, DLO, DHI)
    lo = F(M, m2) * g[0] * CIV[0]
    hi = F(M, m2) * g[1] * CIV[1]
    p("     m2 = %2d ：K_thresh ≈ 10^%.6f（区间相对宽度 %.1e）" % (
        m2, float(mp.log10((m(lo) + m(hi)) / 2)), float((hi - lo) / lo)))

# ---------- 2. 定义表主体 ----------
p("")
p("[2] 定义表主体（K 升序）")
CASES = [
    (77692117359936589403, "m = 92 链从 L 出发的停滞值 7.7692117359936589403e19"),
    (81283051600000000000, "旧台阶表左端 8.12830516e19（K* 平台起点附近）"),
    (100000000000000000000, "10^20（route-3.md:137 的对照点）"),
    (KSTAR, "K* = 205632218873398596256"),
    (250000000000000000000, "2.5e20（K* 与 K_cross 之间）"),
    (313195478959172262850, "旧二分定位的 K_cross 中点附近 3.13195478959172262850e20"),
    (330000000000000000000, "3.3e20（旧越界见证起点）"),
]
rows = []
for (K, tag) in CASES:
    rows.append((K, tag) + audit(K, tag))

# ---------- 3. 与项目浮点实现的对照（本会话现跑，非引旧日志） ----------
p("")
p("[3] 与项目 cycle-1/scripts/r4x_core.py 的现跑对照（dps=200，仅作对照）")
import importlib
import r4x_core as RC
RC.set_dps(200)
for (K, tag) in CASES:
    r = RC.psi(M, mpf(K))
    p("     K = %-22s psi = %-24s m2(min_eps) = %-3s n_feasible = %-4s m2_max = %s" % (
        mp.nstr(mpf(K), 20), r["psi"], r["m2"], r["n_feasible"], r["m2_max_feasible"]))

open(HERE + "/results/c2r5_defaudit.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/c2r5_defaudit.out")
