#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-4 探针三：把第一步 ε 的每个分量的数值打出来（float 展示）。"""
import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.set_int_max_str_digits(2000000)
import route4_rig as Rig
import route4_chain as C


def pr(name, a):
    print("%-16s [%.12e, %.12e]  宽 %.2e" % (name, float(a[0]), float(a[1]),
                                            float(a[1] - a[0])), flush=True)


K = F(7) * 10 ** 11
print("DL = ", float(C.DL[0]), float(C.DL[1]), " 相对宽 %.2e" % float((C.DL[1] - C.DL[0]) / C.DL[0]), flush=True)
print("POW[47] =", float(C.POW[47][0]), float(C.POW[47][1]), flush=True)
print("POW[91] =", float(C.POW[91][0]), float(C.POW[91][1]), flush=True)
print("GEOM[47] =", float(C.GEOM[47][0]), float(C.GEOM[47][1]), flush=True)
import mpmath as mp
mp.mp.dps = 30
print("mpmath δ^47 =", mp.power(mp.log(3) / mp.log(2), 47), flush=True)
A = F(97 * 44 + 73, 54 * C.X0[695])
print("A = %.6e" % float(A), flush=True)
v = Rig.idiv(Rig.imul((K * F(47, 91), K * F(47, 91)), (C.DL[0] - 1, C.DL[1] - 1)),
             (C.POW[47][0] - 1, C.POW[47][1] - 1))
pr("v", v)
print("v 相对宽 %.2e" % float((v[1] - v[0]) / v[0]), flush=True)
p2 = Rig.pow2_interval(v); pr("2^v", p2)
t1 = Rig.idiv((F(3), F(3)), (p2[0] - 1, p2[1] - 1)); pr("t1", t1)
p = Rig.oneminus_pow2delta(v, C.DL); pr("(2^v-1)^δ", p)
t2 = Rig.idiv((F(138), F(138)), p); pr("t2", t2)
den = Rig.iscale(Rig.imul((K, K), Rig.ln2_bounds()), 3); pr("den=3Kln2", den)
br = Rig.iadd(Rig.iadd((A, A), t1), t2); pr("br", br)
eps = Rig.idiv(br, den); pr("eps", eps)
print("mpmath eps = %.20e" % float(C.mpmath_eps_general(47, K, 73, 695)), flush=True)
print("mpmath v = %.15f" % float(mp.mpf(47) / 91 * mp.mpf(7 * 10 ** 11) *
                                 (mp.log(3) / mp.log(2) - 1) /
                                 (mp.power(mp.log(3) / mp.log(2), 47) - 1)), flush=True)
