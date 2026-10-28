#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽验 1（探索，非证书）：S(K) = eps(92,K) - (gamma - delta) 在两个打印端点上的符号与量级。

目的：确认 r2_threshold_cert.log 第 [3]/[4]/[5] 节自述的
  A1（m2 = 92）正余量 1.075910e-163 与 B2 负余量 1.136322e-164 是否可复现（换库 mpmath）。
全部字符串解析，禁 float 中转。
"""
from fractions import Fraction as F
from mpmath import mp, mpf, log, exp

mp.dps = 260

T_hi = "313195478959172262876.636530619490706526023101695229245285067058019209183949160046"
T_lo = "313195478959172262876.636530619490706526023101695229245285067058019209183949160046"
gamma_str = "325919355854421968365/205632218873398596256"

delta = log(3) / log(2)
gam = mpf(325919355854421968365) / mpf(205632218873398596256)
gd = gam - delta
print("gamma - delta =", gd)
print("1/(q43 q44)   =", 1 / (mpf(205632218873398596256) * mpf(7736332199829210068325)))
print()

d92 = exp(92 * log(delta)) - 1
c = (delta - 1) / d92
print("c = (delta-1)/(delta^92-1) =", c)
print()


def S_at(Ks):
    K = mpf(Ks)
    v = K * c            # = v(92, 92, K)
    tv = exp(v * log(2))
    num = 3 / (tv - 1) + 273 / exp(delta * log(tv - 1))
    den = 3 * K * log(2)
    return num, den, num / den - gd


for name, Ks in (("T_hi", T_hi), ("T_lo", T_lo)):
    num, den, s = S_at(Ks)
    print("==", name, "==")
    print("  K      =", mpf(Ks))
    print("  num    =", num)
    print("  3Kln2  =", den)
    print("  S      =", s)
    print("  |S|    = %s" % mp.nstr(abs(s), 12))
    print()

# 根：二分（仅用 S 的符号；用 mpmath，非严格，但精度 260 位远超所需）
lo, hi = mpf("313195478959172262876.6"), mpf("313195478959172262877.0")
slo = S_at(lo)[2]
shi = S_at(hi)[2]
print("S(lo = ...876.6) 符号 =", slo > 0, mp.nstr(slo, 8))
print("S(hi = ...877.0) 符号 =", shi > 0, mp.nstr(shi, 8))
# 找括住 R 的更窄区间：先在 T_hi 附近扫描
for off in ("0", "-1e-60", "1e-60", "-1e-100", "1e-100"):
    K = mpf(T_hi) + mpf(off)
    s = S_at(K)[2]
    print("  K = T_hi + %s -> S 符号 %s, S = %s" % (off, s > 0, mp.nstr(s, 10)))
