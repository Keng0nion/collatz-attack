#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 K = r4b2 上端处逐项对照 MPFR 与精确有理路径的五个加项。"""
import importlib.util
from fractions import Fraction as F
from gmpy2 import mpfr, context, RoundDown, RoundUp, log, log2

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/d3-window-tail/cycle-1/scripts/"
spec = importlib.util.spec_from_file_location("m", HERE + "d3r3_mech.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

K = F("123124614107652692133.007231919710646726095849")
M = 90
PREC = 260


def ctx(r):
    return context(precision=PREC, round=r)


def dn(x):
    with ctx(RoundDown):
        return mpfr(x)


def up(x):
    with ctx(RoundUp):
        return mpfr(x)


# ---- 精确路径（Gv=34 判定器）----
dlo, dhi, Clo, Chi = m.build_consts(70)
orc = m.Oracle(dlo, dhi, Clo, Chi, Gv=34, K=50, Nln=55, Gser=50)
lo, hi = orc._phi_bounds(M, K)
print("精确 Phi_90 ∈ [%s, %s]" % (m.sci(lo, 14), m.sci(hi, 14)))
c_lo, c_hi, c1_lo, c1_hi = orc.cM(M)
print("精确 c_90 相对宽 %s；c_89 相对宽 %s" % (m.sci((c_hi - c_lo) / c_hi, 4), m.sci((c1_hi - c1_lo) / c1_hi, 4)))
v_lo, v_hi = m.g_out(K / c_hi, False, 34), m.g_out(K / c_lo, True, 34)
print("精确 v ∈ [%s, %s]" % (m.sci(v_lo, 25), m.sci(v_hi, 25)))
tl, th = c_lo / c1_hi, c_hi / c1_lo
print("精确 tau ∈ [%s, %s]（宽 %s）" % (m.sci(tl, 20), m.sci(th, 20), m.sci((th - tl) / tl, 4)))
l2 = orc.l2
b2_lo = m.g_out(m.pow2_bounds(v_lo, v_lo, l2, 50)[0] - 1, False, 30)
b2_hi = m.g_out(m.pow2_bounds(v_hi, v_hi, l2, 50)[1] - 1, True, 30)
print("精确 2^v - 1 ∈ [%s, %s]" % (m.sci(b2_lo, 22), m.sci(b2_hi, 22)))
t2lo, t2hi = 3 / b2_hi, 3 / b2_lo
print("精确 3/(2^v-1) ∈ [%s, %s]" % (m.sci(t2lo, 20), m.sci(t2hi, 20)))
Xlo, Xhi = m.pow_rat_bounds(b2_hi, b2_hi, -dhi, -dhi, l2, 50)
print("精确 (2^v-1)^(-delta) ∈ [%s, %s] → 3*89 倍 ∈ [%s, %s]"
      % (m.sci(Xlo, 18), m.sci(Xhi, 18), m.sci(267 * Xlo, 18), m.sci(267 * Xhi, 18)))
print("精确 A 差 = %s" % m.sci(m.Adiff(M), 22))

# ---- MPFR 路径 ----
ln2l, ln2h = dn(log(mpfr(2))), up(log(mpfr(2)))
ln3l, ln3h = dn(log(mpfr(3))), up(log(mpfr(3)))
dlo_m, dhi_m = (lambda: [None])()[0:0] or (dn(ln3l / ln2h), up(ln3h / ln2l))
X0 = 695 * 2**60
xl, xh = dn(mpfr(162 * X0) / mpfr(97)), up(mpfr(162 * X0) / mpfr(97))
Clo_m, Chi_m = dn(log2(xl)), up(log2(xh))


def geom_iv(M):
    sl, sh = mpfr(0), mpfr(0)
    pl, ph = mpfr(1), mpfr(1)
    for _ in range(M):
        with ctx(RoundDown):
            sl = sl + pl
        with ctx(RoundUp):
            sh = sh + ph
        with ctx(RoundDown):
            pl = pl * dlo_m
        with ctx(RoundUp):
            ph = ph * dhi_m
    return sl, sh


def cM_iv(M):
    gl, gh = geom_iv(M)
    with ctx(RoundDown):
        c1 = gl * mpfr(92) / mpfr(M)
    with ctx(RoundUp):
        c2 = gh * mpfr(92) / mpfr(M)
    return c1, c2


cm_lo, cm_hi = cM_iv(M)
c1m_lo, c1m_hi = cM_iv(M - 1)
print("MPFR c_90 ∈ [%s, %s]" % (cm_lo, cm_hi))
print("  相对宽 %s" % ((cm_hi - cm_lo) / cm_hi))
print("MPFR tau ∈ [%s, %s]" % (cm_lo / c1m_hi, cm_hi / c1m_lo))
with ctx(RoundDown):
    vlo_m = mpfr(K.numerator) / mpfr(K.denominator) / cm_hi
with ctx(RoundUp):
    vhi_m = mpfr(K.numerator) / mpfr(K.denominator) / cm_lo
print("MPFR v ∈ [%s, %s]" % (vlo_m, vhi_m))
with ctx(RoundDown):
    b2lo_m = mpfr(2) ** vlo_m - 1
print("MPFR 2^v-1（下端, 下界）= %s" % b2lo_m)
print("  与精确下端相对差 = %s" % ((mpfr(b2_lo.numerator) / mpfr(b2_lo.denominator) - b2lo_m) / b2lo_m))
