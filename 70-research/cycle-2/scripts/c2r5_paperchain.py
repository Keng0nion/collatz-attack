#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 2 轮第 5 路：论文 Theorem 23 链条的两处读数复核（回答子问题 4，并试解登记在案的 10% 差异）。

逐字对照（第 15 页渲染图）：
  第一步：K > 7e11，「we get m2 >= 47」，ε < 6.9e-32
  第六步：K > 7.76e19，「we get m2 >= 88」，ε < 5.3e-41
  第七步：K > 2.05e20，「m2 >= 91」，ε < 1.11e-43
本项目（m = 92 口径）第六步记录 ε = 6.5947593e-41（route-4.md:141）。
本脚本按 m = 91 与 m = 92 两种口径分别复算，判定该差异是否为 m 取值不同所致。
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

CASES = [
    (91, 700000000000, "第一步：论文 m ≤ 91 口径，K = 7e11"),
    (92, 700000000000, "同上换 m = 92"),
    (91, 77692117359936589403, "第六步：论文口径 m = 91，K = 7.769e19"),
    (92, 77692117359936589403, "第六步：本项目口径 m = 92"),
    (91, 205632218873398596256, "第七步：论文口径 m = 91，K = K* = 2.0563e20"),
    (92, 205632218873398596256, "第七步换 m = 92（本项目 K* 格）"),
]
for (m_, K, tag) in CASES:
    feas = [t for t in range(1, m_ + 1) if R.feasible_decision(t, m_, K, DLO, DHI, CIV) is True]
    mx = max(feas)
    e = R.eps_bounds(mx, m_, F(K), DLO, DHI, L2)
    # 最小 eps 的候选（在最大可行附近 ±8 内精算）
    cand = {t: R.eps_bounds(t, m_, F(K), DLO, DHI, L2) for t in feas if t >= mx - 8}
    star = min(cand, key=lambda t: cand[t][1])
    p("%s" % tag)
    p("     m = %d, K = %s：可行集 {1..%d}；max_feasible m2 = %d，eps = %s" % (
        m_, K, mx, mx, mp.nstr(m(e[0]), 18)))
    p("     min_eps m2 = %d，eps = %s" % (star, mp.nstr(m(cand[star][0]), 18)))

open("/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts/results/c2r5_paperchain.out",
     "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/c2r5_paperchain.out")
