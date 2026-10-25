#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-4 辅助模块：ln2、ln3、(162/97)X0 的对数的严格有理上下界（供 r4x_run4 复用）。"""
from fractions import Fraction as F

N = 400

def ln2_bounds():
    s = F(0)
    for k in range(N + 1):
        s += F(1, (2 * k + 1) * 3 ** (2 * k + 1))
    lo = 2 * s
    tail = F(9, 4) / ((2 * N + 3) * 3 ** (2 * N + 3))
    return lo, lo + 2 * tail

def ln3_bounds():
    s = F(0)
    for k in range(N + 1):
        s += F(1, (2 * k + 1) * 2 ** (2 * k + 1))
    lo = 2 * s
    tail = F(8, 3) / ((2 * N + 3) * 2 ** (2 * N + 3))
    return lo, lo + 2 * tail

def delta_bounds():
    l2 = ln2_bounds()
    l3 = ln3_bounds()
    return l3[0] / l2[1], l3[1] / l2[0]

def dec_str(fr, ndig):
    """取分数的前 ndig 位十进制数字串（截断）。"""
    n, d = fr.numerator, fr.denominator
    ip = n // d
    rem = n - ip * d
    out = [str(ip), "."]
    for _ in range(ndig):
        rem *= 10
        out.append(str(rem // d))
        rem -= (rem // d) * d
    return "".join(out)
