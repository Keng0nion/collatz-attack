#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐项对照：MPFR 路径与精确有理路径在 K = r4b2 下端处算 Phi_90 的各项。"""
import importlib.util
from fractions import Fraction as F
import gmpy2
from gmpy2 import mpfr, context, RoundDown, RoundUp, log, log2

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/d3-window-tail/cycle-1/scripts/"
spec = importlib.util.spec_from_file_location("m", HERE + "d3r3_mech.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

K = F("123124614107652692133.007231711933058876044901")
M = 90

# 精确路径
dlo, dhi, Clo, Chi = m.build_consts(70)
orc = m.Oracle(dlo, dhi, Clo, Chi, Gv=34, K=50, Nln=55, Gser=50)
lo, hi = orc._phi_bounds(M, K)
print("精确路径 Phi_90(K) ∈ [%s, %s]" % (m.sci(lo, 12), m.sci(hi, 12)))
c = orc.cM(M)
print("精确 c_90 ∈ [%s, %s]（相对宽 %s）" % (m.sci(c[0], 12), m.sci(c[1], 12), m.sci((c[1]-c[0])/c[1], 4)))
print("精确 A 差 = %s" % m.sci(m.Adiff(M), 20))
vlo, vhi = m.g_out(K / c[1], False, 34), m.g_out(K / c[0], True, 34)
print("精确 v = K/c_90 ∈ [%s, %s]" % (m.sci(vlo, 12), m.sci(vhi, 12)))

# MPFR 路径（与 d3r3_indbisect 相同写法）
PREC = 260


def ctx(r):
    return context(precision=PREC, round=r)


def f_lo(f, *a):
    with ctx(RoundDown):
        return f(*a)


def f_hi(f, *a):
    with ctx(RoundUp):
        return f(*a)


ln2l, ln2h = f_lo(log, mpfr(2)), f_hi(log, mpfr(2))
ln3l, ln3h = f_lo(log, mpfr(3)), f_hi(log, mpfr(3))
dlo_m, dhi_m = f_lo(lambda a, b: a / b, ln3l, ln2h), f_hi(lambda a, b: a / b, ln3h, ln2l)
X0 = 695 * 2**60
with ctx(RoundDown):
    xl = mpfr(162 * X0) / mpfr(97)
with ctx(RoundUp):
    xh = mpfr(162 * X0) / mpfr(97)
Clo_m, Chi_m = f_lo(log2, xl), f_hi(log2, xh)
print("MPFR delta ∈ [%s, %s]" % (dlo_m, dhi_m))
print("精确 delta ∈ [%s, %s]" % (m.sci(dlo, 20), m.sci(dhi, 20)))
print("MPFR C ∈ [%s, %s]" % (Clo_m, Chi_m))
print("精确 C ∈ [%s, %s]" % (m.sci(Clo, 20), m.sci(Chi, 20)))


def geom_iv(M):
    sl, sh = mpfr(0), mpfr(0)
    pl, ph = mpfr(1), mpfr(1)
    for _ in range(M):
        with ctx(RoundDown):
            sl = sl + pl
        with ctx(RoundUp):
            sh = sh + ph
        pl = f_lo(lambda a, b: a * b, pl, dlo_m)
        ph = f_hi(lambda a, b: a * b, ph, dhi_m)
    return sl, sh


def cM_iv(M):
    gl, gh = geom_iv(M)
    with ctx(RoundDown):
        c1 = gl * mpfr(92) / mpfr(M)
    with ctx(RoundUp):
        c2 = gh * mpfr(92) / mpfr(M)
    return c1, c2


c_lo_m, c_hi_m = cM_iv(M)
print("MPFR c_90 ∈ [%s, %s]" % (c_lo_m, c_hi_m))
c1_lo_m, c1_hi_m = cM_iv(M - 1)
with ctx(RoundDown):
    v_lo_m = mpfr(K.numerator) / mpfr(K.denominator) / c_hi_m
with ctx(RoundUp):
    v_hi_m = mpfr(K.numerator) / mpfr(K.denominator) / c_lo_m
with ctx(RoundDown):
    tl_m = c_lo_m / c1_hi_m
with ctx(RoundUp):
    th_m = c_hi_m / c1_lo_m
print("MPFR v ∈ [%s, %s]；tau ∈ [%s, %s]" % (v_lo_m, v_hi_m, tl_m, th_m))
c1 = orc.cM(M - 1)
print("精确 c_89 ∈ [%s, %s]；tau ∈ [%s, %s]" % (m.sci(c1[0], 12), m.sci(c1[1], 12),
      m.sci(c[0] / c1[1], 12), m.sci(c[1] / c1[0], 12)))
