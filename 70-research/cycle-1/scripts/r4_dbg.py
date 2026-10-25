#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""临时诊断：m = 91、K = 7e11 时 eps 的连分数分歧在哪一项。"""
import sys
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
import r4_psi as R
from mpmath import mp, mpf, power, log, floor

mp.dps = 120
X0, delta, c = R.consts(120)
pw = R.dpow(delta, 400)

K = mpf(7) * mpf(10) ** 11
feas, best, best_ub = R.best_m2(91, K, X0, delta, c, pw, 120)
print("可行 m2 个数 =", len(feas), " 最大 =", max(feas), " 最小 =", min(feas))
print("best m2 =", best["m2"], " v =", mp.nstr(best["v"], 20))
print("  A  =", mp.nstr(best["A"], 20))
print("  t1 =", mp.nstr(best["t1"], 20))
print("  t2 =", mp.nstr(best["t2"], 20))
print("  eps=", mp.nstr(best["eps"], 20))
print("  eps_ub=", mp.nstr(best["eps_ub"], 20))

eps = best["eps"]
print("\n分歧法细节（dps_cf = 250）:")
save = mp.dps
mp.dps = 250
d = log(mpf(3)) / log(mpf(2))
print("  d            =", mp.nstr(d, 40))
print("  mpf(eps)     =", mp.nstr(mpf(eps), 40))
b = d + mpf(eps)
print("  b            =", mp.nstr(b, 40))
print("  b - d        =", mp.nstr(b - d, 10))
print("  有效位数差 =", mp.nstr(log(d / (b - d)) / log(mpf(10)), 10))

ya, yb = d, b
print("  前 40 项连分数（两条同步）:")
for i in range(60):
    aa = int(floor(ya)); ab = int(floor(yb))
    mark = ""
    if aa != ab:
        mark = "   <== 首次分歧"
    if i < 40 or mark:
        print(f"    i={i:>3}  a={aa:>6}  b={ab:>6}{mark}")
    if aa != ab:
        break
    ra = ya - aa; rb = yb - ab
    if ra == 0 or rb == 0:
        print(f"    i={i:>3}  余项为零：ra={ra} rb={rb}")
        break
    ya = 1 / ra; yb = 1 / rb
mp.dps = save
