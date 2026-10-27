#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 侦察脚本 3：SB 双亲结构与收敛子（精确有理；mpmath 只用于打印与定向）。

运行：20-experiments/.venv/bin/python k3_probe3.py
"""
from fractions import Fraction as F
from mpmath import mp, mpf, nstr

mp.dps = 90

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
    while q and len(out) < n:
        a = p // q
        out.append(a)
        p, q = q, p - a * q
    return out


def show(label, v):
    print("%-28s = %s / %s  = %s" % (label, v.numerator, v.denominator,
                                     nstr(mpf(v.numerator) / v.denominator, 40)))


GAM = F(325919355854421968365, 205632218873398596256)
R = F(12587715785705330118969, 7941964418702608664581)
KSTAR = 205632218873398596256
dlo = F(158496250072115618145373894394781650875981440769248106045575,
        10 ** 50)   # 只作粗略定向（真 dlo 在正脚本里重新算）

print("R 的连分数 =", cf_frac(R.numerator, R.denominator, 60))
print("R 的连分数项数 =", len(cf_frac(R.numerator, R.denominator, 60)))
print()
show("gamma = [prefix;2]", GAM)
show("[prefix;1]", cf_value(PREFIX + [1]))
show("[prefix;1,1] ", cf_value(PREFIX + [1, 1]))
show("[prefix;1,1,37]", cf_value(PREFIX + [1, 1, 37]))
show("[prefix;1,1,38]", cf_value(PREFIX + [1, 1, 38]))
show("R", R)
print()
A = cf_value(PREFIX + [1])
B = cf_value(PREFIX + [1, 1, 37])
print("A = [prefix;1] 的分母 =", A.denominator)
print("B = [prefix;1,1,37] 的分母 =", B.denominator)
print("q_A + q_B =", A.denominator + B.denominator, " ; R 分母 =", R.denominator)
print("mediant(A,B) == R ?", F(A.numerator + B.numerator, A.denominator + B.denominator) == R)
print("unimodular: |pA qB - qA pB| =", abs(A.numerator * B.denominator - A.denominator * B.numerator))
print()
print("A < dlo ?", A < dlo, " ; dlo < gamma ?", dlo < GAM)
print("gamma <= B ?", GAM <= B)
print("A < R < B ?", A < R < B)
print()
# 收敛子表：用 R 的连分数展开（精确）
print("R 的收敛子（分母 q_i，i = 40 至 46）：")
p0, q0, p1, q1 = 1, 0, 0, 1
cf = cf_frac(R.numerator, R.denominator, 60)
for i, a in enumerate(cf):
    p0, q0, p1, q1 = a * p0 + p1, a * q0 + q1, p0, q0
    if i >= 40:
        print("   i=%2d a=%3d q_i=%d  侧=%s" % (i, a, q0, "?"))
print()
# 与 K* 和 route-4 记录的 7941964418702608664581 对照
print("K* =", KSTAR)
print("K* 是否等于某个 q_i（i<=45）？", [i for i, _ in enumerate([0]) if False])
