#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 2 轮第 5 路：两约定（min_eps 与 max_feasible）在可行门槛附近的分离检验。

判据：m2 = m2_max 可行但 eps(m2_max) > eps(m2_max - 1) 时两约定给出不同的 eps，
从而 Psi^F < Psi^M。理论上该窗口为 K ∈ [K_thresh(m2), K_thresh(m2)*(70.26/C))，
即相对宽度约 0.11%（m2 <= m-2；m2 = m 有 A = 0 的特殊优势，见报告第 4 节）。
"""
import sys
from fractions import Fraction as F

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts")
import c2r5_rig as R
from mpmath import mp, mpf

mp.dps = 40
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
M = 92

# 门槛中点（用严格区间的中点作为测试点，仅用于展示；判据比较仍是严格区间）
for t in (88, 89, 90):
    g = R.geom_bounds(t, DLO, DHI)
    lo = F(M, t) * g[0] * CIV[0]
    hi = F(M, t) * g[1] * CIV[1]
    p("=" * 70)
    p("m2 = %d 的门槛 K_thresh ∈ [%s, %s]" % (t, mp.nstr(m(lo), 20), mp.nstr(m(hi), 20)))
    for fac in [F(1), F(10001, 10000), F(10005, 10000), F(101, 100), F(105, 100)]:
        K = lo * fac
        fmax = max(x for x in range(1, M + 1)
                   if R.feasible_decision(x, M, K, DLO, DHI, CIV) is True)
        e_max = R.eps_bounds(fmax, M, K, DLO, DHI, L2)
        cand = {x: R.eps_bounds(x, M, K, DLO, DHI, L2) for x in range(max(1, fmax - 8), fmax + 1)
                if R.feasible_decision(x, M, K, DLO, DHI, CIV) is True}
        star = min(cand, key=lambda x: cand[x][1])
        beta_lo = R.rd(DLO + e_max[0])
        beta_hi = R.ru(DHI + e_max[1])
        psiF = R.simplest_fraction(DLO, beta_hi).denominator
        p("  K = K_thresh*%-7s ：m2_max = %d，eps(m2_max) = %s；argmin = %d，eps(argmin) = %s；分离？ %s" % (
            fac, fmax, mp.nstr(m(e_max[0]), 18), star, mp.nstr(m(cand[star][0]), 18),
            star != fmax))
        p("       Psi^F(K)（Stern-Brocot 下界）= %d" % psiF)

open("/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts/results/c2r5_convsplit.out",
     "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/c2r5_convsplit.out")
