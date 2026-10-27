#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 侦察脚本 1：用 mpmath 仅作定向（非严格），确认对象与常数。

只打印，不落任何证据级结论。运行：
  20-experiments/.venv/bin/python k3_probe1.py
"""
from mpmath import mp, mpf, floor, nstr
from fractions import Fraction as F

mp.dps = 80

C1 = 60 + mp.log(mpf(112590) / 97) / mp.log(2)
print("C = 60 + log2(112590/97) =", nstr(C1, 45))
X0 = 695 * 2 ** 60
C2 = mp.log((mpf(162) / 97) * X0) / mp.log(2)
print("C = log2((162/97)X0)    =", nstr(C2, 45))

d = mp.log(3) / mp.log(2)
print("delta =", nstr(d, 60))

gam = F(325919355854421968365, 205632218873398596256)
gm = mpf(gam.numerator) / gam.denominator
print("gamma =", nstr(gm, 60))
print("gamma - delta =", nstr(gm - d, 50))

r = F(12587715785705330118969, 7941964418702608664581)
rm = mpf(r.numerator) / r.denominator
print("r =", nstr(rm, 60))
print("delta < r ?", d < rm, " ; r < gamma ?", rm < gm)

dlo45 = F(1584962500721156181453738943947816508759814407, 10 ** 45)
print("dlo45 < r ?", mpf(dlo45.numerator) / dlo45.denominator < rm)


def cf_frac(p, q, n):
    out = []
    for _ in range(n):
        a = p // q
        out.append(a)
        p, q = q, p - a * q
        if q == 0:
            break
    return out


print("cf(gamma) =", cf_frac(gam.numerator, gam.denominator, 60))
print("cf(r)     =", cf_frac(r.numerator, r.denominator, 60))


def cf(x, n):
    out = []
    for _ in range(n):
        a = int(floor(x))
        out.append(a)
        x = 1 / (x - a)
    return out


print("cf(delta,50) =", cf(d, 50))
