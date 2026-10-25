#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试：先看 eps 的第一步取值，再单独检验连分数分离逻辑。"""
import sys
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
from mpmath import mp, mpf, power
import r4x_core as R

R.set_dps(120)
print("dps =", mp.dps)
K = mpf("7e11")
print("premise_lhs(47) =", mp.nstr(R.premise_lhs(47), 12), " rhs(47) =", mp.nstr(R.premise_rhs(47, 91, K), 12))
feas = [m2 for m2 in range(1, 92) if R.feasible(m2, 91, K)]
print("可行 m2 的最小与最大：", feas[0], feas[-1], " 个数", len(feas))
b = R.best_m2(91, K)
print("best_m2 =", b[0], " eps =", mp.nstr(b[1], 12))
e = b[1]
print("eps 的 mpf 表示 =", e)
print("delta        =", mp.nstr(R.DELTA, 45))
print("delta + eps  =", mp.nstr(R.DELTA + e, 45))
print("差值        =", mp.nstr((R.DELTA + e) - R.DELTA, 12))
print()
# 连分数分离逻辑的自检：对若干人工 eps 看分离下标与 q 值
for es in ["1e-10", "1e-15", "1e-20", "1e-25", "1e-32"]:
    ee = mpf(es)
    A = R.cf_digits(R.DELTA, 300)
    B = R.cf_digits(R.DELTA + ee, 300)
    k = 0
    while k < 300 and A[k] == B[k]:
        k += 1
    print("eps=%s -> 首个相异下标 k=%s, a_k=%s b_k=%s (前 12 项 %s)" % (
        es, k, A[k] if k < 300 else None, B[k] if k < 300 else None, A[:12]))
