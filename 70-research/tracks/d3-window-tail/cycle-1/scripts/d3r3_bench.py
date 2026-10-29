#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""基准：Fraction 级数与定点区间算术的速度对比（只读不写）。"""
import time, importlib.util
from fractions import Fraction as F
spec = importlib.util.spec_from_file_location(
    "m", "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/d3-window-tail/cycle-1/scripts/d3r3_mech.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

for dg in (10, 20, 40, 77):
    y = F(1234567890, 10**dg)
    t0 = time.time()
    m.exp_bounds(y, 60)
    print(f"exp_bounds(den 10^{dg}), K=60: {round(time.time() - t0, 4)} s")

for dg in (20, 40):
    q = F(10**dg + 7, 10**dg)
    t0 = time.time()
    m.ln_bounds(q, 45, m.ln2_bounds(45))
    print(f"ln_bounds(1+10^-{dg}), N=45: {round(time.time() - t0, 4)} s")

# 定点区间算术基准
GRID = 10**32


def fmul(a, b):
    return (a[0] * b[0]) // GRID, (a[1] * b[1] + GRID - 1) // GRID


def fexp(y, K=60):
    """exp(y)，y 为 [0,1) 的缩放整数区间。"""
    s = (GRID, GRID)
    term = (GRID, GRID)
    for k in range(K):
        s = (s[0] + term[0], s[1] + term[1])
        term = fmul(term, y)
        term = (term[0] // (k + 1), (term[1] + k) // (k + 1))
    return s


t0 = time.time()
for _ in range(200):
    fmul((GRID + 12345, GRID + 12346), (GRID + 999, GRID + 1000))
print("200 次定点乘法:", round(time.time() - t0, 4), "s")
t0 = time.time()
for _ in range(200):
    fexp((GRID // 2, GRID // 2 + 1), 60)
print("200 次定点 exp（K=60）:", round(time.time() - t0, 4), "s")
