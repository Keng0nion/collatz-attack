#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 侦察脚本 2：把半收敛清单与 SB 双亲结构算清楚（非严格，只用精确有理）。

运行：20-experiments/.venv/bin/python k3_probe2.py
"""
from fractions import Fraction as F
from mpmath import mp, mpf, nstr

mp.dps = 80

PREFIX = [1, 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55, 1, 4, 3, 1, 1, 15, 1, 9, 2, 5, 7,
          1, 1, 4, 8, 1, 11, 1, 20, 2, 1, 10, 1, 4, 1, 1, 1]
assert len(PREFIX) == 42


def cf_value(quot):
    v = F(0)
    for a in reversed(quot):
        v = F(a) + (F(0) if v == 0 else 1 / v)
    return v


def cf_frac(p, q, n):
    out = []
    for _ in range(n):
        a = p // q
        out.append(a)
        p, q = q, p - a * q
        if q == 0:
            break
    return out


def rebuild(cf):
    p0, q0, p1, q1 = 1, 0, 0, 1
    for a in cf:
        p0, q0, p1, q1 = a * p0 + p1, a * q0 + q1, p0, q0
    return F(p0, q0)


GAM = F(325919355854421968365, 205632218873398596256)
R = F(12587715785705330118969, 7941964418702608664581)
print("cf(R) =", cf_frac(R.numerator, R.denominator, 60))
print("rebuild(cf(R)) == R ?", rebuild(cf_frac(R.numerator, R.denominator, 60)) == R)

# 收敛子分母表（对 PREFIX 及其后续项）
for tail, label in [([2], "gamma=[prefix;2]"),
                    ([1, 1], "gamma=[prefix;1,1]"),
                    ([1, 1, 1], "[prefix;1,1,1]"),
                    ([1, 1, 1, 1], "[prefix;1,1,1,1]"),
                    ([1, 1, 2], "[prefix;1,1,2]"),
                    ([1, 1, 1, 37], "[prefix;1,1,1,37]"),
                    ([1, 1, 1, 38], "R=[prefix;1,1,1,38]")]:
    v = cf_value(PREFIX + tail)
    print("%-24s = %s / %s   = %.20f" % (label, v.numerator, v.denominator,
                                         mpf(v.numerator) / v.denominator))

# 收敛子序列（对真 delta 的连分数，用 mpmath 定向）
d = mp.log(3) / mp.log(2)
qprev, qcur = 1, 0
pprev, pcur = 0, 1
x = d
print("\n收敛子表（mpmath 定向，非严格）：")
for i in range(50):
    a = int(mp.floor(x))
    pprev, pcur = a * pcur + pprev, pcur
    qprev, qcur = a * qcur + qprev, qcur
    if i >= 39:
        val = mpf(pcur) / qcur
        print("  i=%2d a=%3d p/q(%d/%d) 符号 %s" % (
            i, a, pcur, qcur, ">" if val > d else "<"))
    x = 1 / (x - a)
    if x > 1e60:
        break
