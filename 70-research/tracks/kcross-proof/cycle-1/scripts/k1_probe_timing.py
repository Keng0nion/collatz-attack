# -*- coding: utf-8 -*-
"""k1 探针：加载 cycle-2 的只读区间库，测单次 eps_bounds 的耗时与量级。
只读；不写任何旧目录。"""
import sys, time
from fractions import Fraction as F
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts")
import c2r5_rig as R

DLO, DHI = R.delta_bounds()
CIV = R.C_bounds()
L2 = R.ln2_bounds()
print("delta 区间宽度 = %.3g" % float(DHI - DLO))
print("C 区间宽度 = %.3g" % float(CIV[1] - CIV[0]))

for K in [F(312) * 10 ** 18, F(313195478959172262876), F(315) * 10 ** 18]:
    t0 = time.time()
    e = R.eps_bounds(92, 92, K, DLO, DHI, L2)
    dt = time.time() - t0
    print("K = %d  eps(92,K) ∈ [%.12e, %.12e]  宽度 %.3g  用时 %.2f s" % (
        K, float(e[0]), float(e[1]), float(e[1] - e[0]), dt))
