#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本轮路线 2 的探索脚本（非证书）：用 mpmath 高精度点值确认量级与公式读法。

用途：在写严格脚本之前，先确认
  1. v(92, T_hi) 与 2^v 的量级（对照我在纸上估算的 72.9 与 7e21）；
  2. A(92) = 0、A(91) = 3/X0 的读数（对照 c2r5_cert.log:27）；
  3. numerator(92) 与 (gamma - delta)*3K ln2 的大小（对照日志 6.24468066969273e-43）；
  4. 5.55e-21 与 3/X0、240/(54X0) 的关系；
  5. j = 90、89 窗口两格。
只读，不写仓库其它文件。
"""
from fractions import Fraction as F
from mpmath import mp, mpf, log, exp

mp.dps = 120

X0 = 695 * 2 ** 60
T_hi_str = ("313195478959172262876.636530619490706526023101695229245285067058019209183949160046")
K_hi = F(T_hi_str)
# 用字符串转 mpf，禁止 float 中转
KN = mpf("313195478959172262876.636530619490706526023101695229245285067058019209183949160046")

# delta = ln3/ln2 的高精度点值
delta = log(3) / log(2)
print("delta =", delta)
print("delta^92 =", exp(92 * log(delta)))
print("(delta-1)/(delta^92-1) =", (delta - 1) / (exp(92 * log(delta)) - 1))

v92 = KN * (delta - 1) / (exp(92 * log(delta)) - 1)
print("v(92, T_hi) =", v92)
print("2^v =", exp(v92 * log(2)))
print("3/(2^v-1) =", 3 / (exp(v92 * log(2)) - 1))
print("(2^v-1)^delta =", exp(delta * log(exp(v92 * log(2)) - 1)))
print("3*91/(2^v-1)^delta =", 273 / exp(delta * log(exp(v92 * log(2)) - 1)))

num92 = 3 / (exp(v92 * log(2)) - 1) + 273 / exp(delta * log(exp(v92 * log(2)) - 1))
print("numerator(92, T_hi) =", num92)

gamma = F(325919355854421968365, 205632218873398596256)
gam = mpf(325919355854421968365) / mpf(205632218873398596256)
print("gamma - delta =", gam - delta)

den = 3 * KN * log(2)
print("3K ln2 =", den)
print("(gamma-delta)*3K ln2 =", (gam - delta) * den)
print("eps(92,T_hi) =", num92 / den)
print("S(T_hi) = eps - (gamma-delta) =", num92 / den - (gam - delta))

print()
print("3/X0 =", mpf(3) / mpf(X0))
print("240/(54X0) =", mpf(240) / (54 * mpf(X0)))
print("105/(54X0) =", mpf(105) / (54 * mpf(X0)))
print("267/(54X0) =", mpf(267) / (54 * mpf(X0)))
print("170/(54X0) =", mpf(170) / (54 * mpf(X0)))
print("3/(2^C-1), 2^C=(162/97)X0 :", mpf(291) / (162 * mpf(X0) - 97))
print("97/(54X0) =", mpf(97) / (54 * mpf(X0)))
print("diff =", mpf(291) / (162 * mpf(X0) - 97) - mpf(97) / (54 * mpf(X0)))

# 窗口两格（用日志打印的区间端点，字符串解析）
c90lo = F("123124614107556571561.827996023727480573234158995835")
c90hi = c90lo
k90lo = F("123124614107652692133.007231711933058876044901")
k90hi = F("123124614107652692133.007231919710646726095849")
print()
print("j=90 rel_lo =", (k90lo - c90hi) / c90hi)
print("j=90 rel_hi =", (k90hi - c90lo) / c90lo)
print("j=90 打印 24 位：", "%.24e" % float(((k90lo - c90hi) / c90hi)))

c89lo = F("78555824936758779275.265552681458057901548946328722")
k89lo = F("78555824936819382091.475309577063948109807001")
k89hi = F("78555824936819382091.475309709629966165890197")
print("j=89 rel_lo =", (k89lo - c89lo) / c89lo)
print("j=89 rel_hi =", (k89hi - c89lo) / c89lo)
