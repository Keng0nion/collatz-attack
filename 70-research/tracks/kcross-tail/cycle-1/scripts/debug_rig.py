#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试 kc_tail_rig 的 eps 分支（临时，不写仓库）。"""
import sys
from fractions import Fraction as F

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1/scripts"
sys.path.insert(0, HERE)
import kc_tail_rig as R
from mpmath import mp, mpf, log, exp

mp.dps = 60


def dec(x, n=25):
    if isinstance(x, tuple):
        return "[%s, %s]" % (dec(x[0], n), dec(x[1], n))
    return mp.nstr(mpf(F(x).numerator) / mpf(F(x).denominator), n)


dlo, dhi = R.delta_bounds()
l2 = R.ln2_bounds()
K = F(33, 10) * 10 ** 19
print("K =", dec(K, 25))
vl, vh = R.v_bounds(92, 92, K, dlo, dhi)
print("v =", dec((vl, vh)))
print(" 参考 v 点值 =", mpf(33) / 10 * mpf(10) ** 19 * (log(3) / log(2) - 1) / (exp(92 * log(log(3) / log(2))) - 1))
two_v = R.exp_bounds(R.rd(vl * l2[0]), R.ru(vh * l2[1]))
print("2^v =", dec(two_v))
print(" 参考 2^v =", exp(mpf(33) / 10 * mpf(10) ** 19 * (log(3) / log(2) - 1) / (exp(92 * log(log(3) / log(2))) - 1) * log(2)))
t = (R.rd(two_v[0] - 1), R.ru(two_v[1] - 1))
print("t = 2^v - 1 =", dec(t))
term1 = R.idiv((F(3), F(3)), t)
print("term1 = 3/(2^v-1) =", dec(term1))
lt = R.ln_iv(t)
print("ln(t) =", dec(lt))
e = (R.rd(dlo * lt[0]), R.ru(dhi * lt[1]))
print("delta*ln(t) =", dec(e))
pt = R.exp_bounds(e[0], e[1])
print("t^delta =", dec(pt))
term2 = R.idiv((F(3 * 91), F(3 * 91)), pt)
print("term2 = 273/t^delta =", dec(term2))
num = (R.rd(term1[0] + term2[0]), R.ru(term1[1] + term2[1]))
print("num =", dec(num))
den = R.imul((F(3 * K), F(3 * K)), l2)
print("den = 3K ln2 =", dec(den))
print("eps =", dec(R.idiv(num, den)))
print("日志对照 r2_threshold_cert.log:50 / c2r5_cert.log:24 : 3.976409667298941266e-44")
print("A_of(92,92) =", R.A_of(92, 92), " A_of(91,92) =", dec(R.A_of(91, 92), 22))
print("A_of(90,92) =", dec(R.A_of(90, 92), 22))
