#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 侦察脚本 5：复现 c2r5_rig.simplest_fraction 的返回并逐步追踪。

运行：20-experiments/.venv/bin/python k3_probe5.py
"""
import sys
from fractions import Fraction as F

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts")
import c2r5_rig as R2


def dec(x, nd):
    x = F(x)
    sign = "-" if x < 0 else ""
    x = abs(x)
    ip = x.numerator // x.denominator
    rem = x.numerator - ip * x.denominator
    out = [sign + str(ip), "."]
    for _ in range(nd):
        rem *= 10
        out.append(str(rem // x.denominator))
        rem -= (rem // x.denominator) * x.denominator
    return "".join(out)


PREFIX = [1, 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55, 1, 4, 3, 1, 1, 15, 1, 9, 2, 5, 7,
          1, 1, 4, 8, 1, 11, 1, 20, 2, 1, 10, 1, 4, 1, 1, 1]


def cf_value(quot):
    v = F(0)
    for a in reversed(quot):
        v = F(a) + (F(0) if v == 0 else 1 / v)
    return v


GAM = F(325919355854421968365, 205632218873398596256)
RCLAIM = F(12587715785705330118969, 7941964418702608664581)
B = cf_value(PREFIX + [1, 1, 37])
BLOW = cf_value(PREFIX + [1, 1, 36])
DLO, DHI = R2.delta_bounds()
print("c2r5_rig delta_bounds: dlo =", dec(DLO, 55))
print("                       dhi =", dec(DHI, 55))
print("  B < dlo ?", B < DLO, "  ；BLOW < dlo ?", BLOW < DLO, "  ；dhi < GAM ?", DHI < GAM)
print()
got = R2.simplest_fraction(DLO, GAM)
print("simplest_fraction(dlo, GAM) 返回 =", got.numerator, "/", got.denominator)
print("  等于 RCLAIM ?", got == RCLAIM, " ；等于 B ?", got == B)
print()
# 逐步追踪（复制 c2r5_rig.simplest_fraction 的逐步逻辑）
A, Bb = F(DLO), F(GAM)
x, y, z, w = 0, 1, 1, 0
print("逐步追踪（步数上限 60）：")
for step in range(60):
    kL = (A * y - x).numerator // (z - A * w).numerator if False else None
    kL = ((A * y - x) / (z - A * w))
    kL = kL.numerator // kL.denominator
    if kL >= 1:
        x, y = x + kL * z, y + kL * w
    kR = ((z - Bb * w) / (Bb * y - x))
    kR = kR.numerator // kR.denominator
    if kR >= 1:
        z, w = z + kR * x, w + kR * y
    mn, md = x + z, y + w
    m = F(mn, md)
    inside = A < m < Bb
    print("  step %2d: kL=%s kR=%s 括号 = %d/%d 与 %d/%d ；中项 = %d/%d ；在区间内？ %s" % (
        step, kL, kR, x, y, z, w, mn, md, inside))
    if inside:
        print("  -> 返回", mn, "/", md)
        break
print()
print("参照：BLOW = %d/%d ；B = %d/%d ；RCLAIM = %d/%d" % (
    BLOW.numerator, BLOW.denominator, B.numerator, B.denominator,
    RCLAIM.numerator, RCLAIM.denominator))
