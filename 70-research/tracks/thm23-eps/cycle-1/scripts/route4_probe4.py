#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-4 探针四：第一步 ε 的每个分量与 mpmath 逐位对照（找系统性偏置）。"""
import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.set_int_max_str_digits(2000000)
import mpmath as mp
import route4_rig as Rig
import route4_chain as C
import route4_step7 as S7

mp.mp.dps = 80
d = mp.log(3) / mp.log(2)
K = F(7) * 10 ** 11
m2 = 47
A = F(97 * 44 + 73, 54 * C.X0[695])

v = Rig.idiv(Rig.imul((K * F(m2, 91), K * F(m2, 91)), (C.DL[0] - 1, C.DL[1] - 1)),
             (C.POW[m2][0] - 1, C.POW[m2][1] - 1))
p2 = Rig.pow2_interval(v)
t1 = Rig.idiv((F(3), F(3)), (p2[0] - 1, p2[1] - 1))
p = Rig.oneminus_pow2delta(v, C.DL)
t2 = Rig.idiv((F(138), F(138)), p)
den = Rig.iscale(Rig.imul((K, K), Rig.ln2_bounds()), 3)
br = Rig.iadd(Rig.iadd((A, A), t1), t2)
eps = Rig.idiv(br, den)

mpv = mp.mpf(int(K)) * mp.mpf(m2) / 91 * (d - 1) / (mp.power(d, m2) - 1)
mp2v = mp.power(2, mpv)
mt1 = 3 / (mp2v - 1)
mpp = mp.power(mp2v - 1, d)
mt2 = 138 / mpp
mden = 3 * mp.mpf(int(K)) * mp.log(2)
mbr = mp.mpf(A.numerator) / A.denominator + mt1 + mt2
meps = mbr / mden
md47 = mp.power(d, m2)

rows = [
    ("delta^47", C.POW[m2], md47),
    ("v", v, mpv),
    ("2^v", p2, mp2v),
    ("t1", t1, mt1),
    ("(2^v-1)^delta", p, mpp),
    ("t2", t2, mt2),
    ("3Kln2", den, mden),
    ("br=A+t1+t2", br, mbr),
    ("eps", eps, meps),
]
for name, iv, mv in rows:
    lo, hi = float(iv[0]), float(iv[1])
    mvf = float(mv)
    inside = lo <= mvf <= hi
    print("%-14s 区间[%s, %s]  mpmath=%s  含=%s  相对差=%.2e" %
          (name, S7.sci(iv[0], 22), S7.sci(iv[1], 22), mp.nstr(mv, 22),
           inside, abs(lo - mvf) / max(abs(lo), 1e-300)), flush=True)
