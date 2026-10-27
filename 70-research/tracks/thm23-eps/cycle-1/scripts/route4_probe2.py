#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-4 性能/宽度探针二：逐步打印中间量的位数、宽度与相对宽度。"""
import os
import sys
import time
from fractions import Fraction as F
from math import floor, ceil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.set_int_max_str_digits(2000000)
import route4_rig as Rig
import route4_chain as C


def sizes(x):
    if isinstance(x, tuple):
        return "(%d/%d, %d/%d)" % (
            len(str(abs(x[0].numerator))), len(str(x[0].denominator)),
            len(str(abs(x[1].numerator))), len(str(x[1].denominator)))
    return "%d/%d" % (len(str(abs(x.numerator))), len(str(x.denominator)))


def relw(a):
    if a[0] <= 0:
        return float(Rig.wid(a))
    return float(Rig.wid(a) / a[0])


def step_times(label, fn, *a, **kw):
    t0 = time.time()
    r = fn(*a, **kw)
    print("%-34s %7.3fs" % (label, time.time() - t0), flush=True)
    return r


K0 = C.K0
dl = Rig.delta_bounds()
print("DL 宽 %.2e 位数 %s" % (float(Rig.wid(dl)), sizes(dl)), flush=True)
print("GEOM[47] 宽 %.2e 位数 %s 相对宽 %.2e" %
      (float(Rig.wid(C.GEOM[47])), sizes(C.GEOM[47]), relw(C.GEOM[47])), flush=True)

v = Rig.idiv(Rig.imul((K0 * F(47, 91), K0 * F(47, 91)), (dl[0] - 1, dl[1] - 1)),
             (C.GEOM[47][0] - 1, C.GEOM[47][1] - 1))
print("v 宽 %.2e 位数 %s 相对宽 %.2e" % (float(Rig.wid(v)), sizes(v), relw(v)), flush=True)

n = floor(v[0])
r = (v[0] - n, v[1] - n)
print("r 位数 %s 宽 %.2e" % (sizes(r), float(Rig.wid(r))), flush=True)
l2 = Rig.ln2_bounds()
y = (r[0] * l2[0], r[1] * l2[1])
print("y = r*ln2 位数 %s 宽 %.2e" % (sizes(y), float(Rig.wid(y))), flush=True)

elo = step_times("exp_lb(r0*ln2_lo)", lambda: Rig.exp_bounds(y[0], Rig.SERX)[0])
print("  elo = %s" % str(elo)[:30], flush=True)
ehi = step_times("exp_ub(r1*ln2_hi)", lambda: Rig.exp_bounds(y[1], Rig.SERX)[1])
print("  ehi = %s" % str(ehi)[:30], flush=True)
p2 = (F(2) ** n * elo, F(2) ** n * ehi)
print("p2 = 2^v 位数 %s 宽 %.2e 相对宽 %.2e" %
      (sizes(p2), float(Rig.wid(p2)), relw(p2)), flush=True)

t1 = Rig.idiv((F(3), F(3)), (p2[0] - 1, p2[1] - 1))
print("t1 = 3/(2^v-1) 位数 %s 宽 %.2e 相对宽 %.2e" %
      (sizes(t1), float(Rig.wid(t1)), relw(t1)), flush=True)

t0 = time.time()
zhi = Rig.pow2_bounds(-v[0], Rig.SERX)[1]
zlo = Rig.pow2_bounds(-v[1], Rig.SERX)[0]
print("z = 2^-v 用时 %.3fs  宽 %.2e 相对宽 %.2e" %
      (time.time() - t0, float(zhi - zlo), float((zhi - zlo) / zlo)), flush=True)

l3 = Rig.ln3_bounds()
y_lo = r[0] * l3[0] - dl[1] * (zhi + 2 * zhi * zhi)
y_hi = r[1] * l3[1] - dl[0] * zlo
print("y^ 位数 %s 宽 %.2e" % (sizes((y_lo, y_hi)), float(y_hi - y_lo)), flush=True)
e_lo = step_times("exp(y_lo)", lambda: Rig.exp_bounds(y_lo, Rig.SERX)[0])
e_hi = step_times("exp(y_hi)", lambda: Rig.exp_bounds(y_hi, Rig.SERX)[1])
print("exp(.) 相对宽 %.2e" % float((e_hi - e_lo) / e_lo), flush=True)
p = (F(3) ** n * e_lo, F(3) ** n * e_hi)
print("p = (2^v-1)^delta 位数 %s 宽 %.2e 相对宽 %.2e" %
      (sizes(p), float(Rig.wid(p)), relw(p)), flush=True)

t2 = Rig.idiv((F(138), F(138)), p)
print("t2 宽 %.2e 相对宽 %.2e" % (float(Rig.wid(t2)), relw(t2)), flush=True)
A = (F(97 * 44 + 73, 54 * C.X0[695]),) * 2
br = Rig.iadd(Rig.iadd(A, t1), t2)
den = Rig.iscale(Rig.imul((K0, K0), l2), 3)
eps = Rig.idiv(br, den)
print("eps 宽 %.2e 相对宽 %.2e" % (float(Rig.wid(eps)), relw(eps)), flush=True)
print("A = %.6e ; t1 = %.6e ; t2 = %.6e ; t2/A = %.3e" %
      (float(A[0]), float(t1[0]), float(t2[0]), float(t2[0] / A[0])), flush=True)
print("t1 相对宽贡献到 eps: %.2e ; t2 相对宽贡献: %.2e" %
      (relw(t1), relw(t2) * float(t2[0] / A[0])), flush=True)
