#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 2 轮第 5 路：区间库自检与锚点核对（先定义后计算；锚点只作对照，不作证据）。

运行：20-experiments/.venv/bin/python c2r5_selftest.py
"""
import sys
from fractions import Fraction as F

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts"
C1 = "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts"
sys.path.insert(0, HERE)
sys.path.insert(0, C1)
import c2r5_rig as R

OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def dec(x, nd):
    """分数的十进制截断串（向下截断）。"""
    n, d = F(x).numerator, F(x).denominator
    sign = "-" if n < 0 else ""
    n = abs(n)
    ip = n // d
    rem = n - ip * d
    out = [sign + str(ip), "."]
    for _ in range(nd):
        rem *= 10
        out.append(str(rem // d))
        rem -= (rem // d) * d
    return "".join(out)


# ---------- 1. 常数锚点 ----------
p("[T1] 常数锚点（本轮自算，与已知十进制位对齐）")
l2 = R.ln2_bounds()
l3 = R.ln3_bounds()
d_lo, d_hi = R.delta_bounds()
p("     ln2 in [%s, %s]  宽度 %s" % (dec(l2[0], 60), dec(l2[1], 60), float(l2[1] - l2[0])))
p("     已知 ln2 = 0.693147180559945309417232121458176568075500134360255254120680")
p("     ln3 in [%s, %s]  宽度 %s" % (dec(l3[0], 60), dec(l3[1], 60), float(l3[1] - l3[0])))
p("     已知 ln3 = 1.098612288668109691395245236922525704647490557822749451734694")
PIN = "1.58496250072115618145373894394781650875981440769248106045575"
p("     delta_lo 50 位 = " + dec(d_lo, 50))
p("     delta_hi 50 位 = " + dec(d_hi, 50))
p("     r4x_rig.py:62 钉住的 59 位 delta = " + PIN)
p("     钉住值（59 位截断）落在区间内？ %s ；宽度 %s" % (F(PIN) > d_lo and F(PIN) < d_hi, float(d_hi - d_lo)))
p("     前 49 位与钉住值一致（截断口径）？ %s ；截断差 %s" % (
    dec(d_lo, 49) == PIN[:51] and dec(d_hi, 49) == PIN[:51], float(F(PIN) - d_lo)))
p("     delta 区间宽度（对数量级）= 1e%d" % round(__import__("math").log10(float(d_hi - d_lo))))

# 与项目 r4x_rig_helpers 独立对照（不同级数分解）
try:
    import r4x_rig_helpers as H
    h_lo, h_hi = H.delta_bounds()
    p("     项目 r4x_rig_helpers.delta_bounds() = [%s, %s]" % (dec(h_lo, 50), dec(h_hi, 50)))
    p("     两区间交集非空？ %s ；本库区间包含项目区间？ %s" % (
        max(d_lo, h_lo) < min(d_hi, h_hi), d_lo < h_lo and h_hi < d_hi))
except Exception as e:  # noqa
    p("     [跳过] r4x_rig_helpers 对照失败：%r" % (e,))

# ---------- 2. exp / pow ----------
p("")
p("[T2] exp 与幂函数锚点（对照 mpmath，仅作参照）")
from mpmath import mp, mpf, log as mlog, power as mpower
mp.dps = 60


def m(x):
    x = F(x)
    return mpf(x.numerator) / mpf(x.denominator)
for (x) in [F(1), F(7, 2), F(1234, 17), F(52), F(150)]:
    lo, hi = R.exp_bounds(x, x)
    ref = mpower(mp.e, m(x))
    p("     exp(%s) in [%s, %s] ｜mpmath %s ｜宽 %s" % (
        float(x), mp.nstr(m(lo), 25), mp.nstr(m(hi), 25), mp.nstr(ref, 25), float(hi - lo)))
vl = F(75)
t_lo, t_hi = R.exp_bounds(vl * R.ln2_bounds()[0], vl * R.ln2_bounds()[1])
p("     2^75 in [%s, %s] ；精确值 %d" % (mp.nstr(m(t_lo), 25), mp.nstr(m(t_hi), 25), 2 ** 75))
p("     (2^75 - 1)^delta in [%s, %s] ；mpmath %s" % tuple(
    [mp.nstr(m(x), 25) for x in R.pow_bounds(t_lo - 1, t_hi - 1, d_lo, d_hi)] +
    [mp.nstr(mpower(mpf(2) ** 75 - 1, m(PIN)), 25)]))

# ---------- 3. C = log2((162/97)X0) ----------
p("")
p("[T3] C = log2((162/97)X0)（X0 = 695*2^60 = %d）" % R.X0_INT)
C_lo, C_hi = R.C_bounds()
refC = mlog(mpf(162) / 97 * mpf(R.X0_INT)) / mlog(2)
p("     C in [%s, %s] ；mpmath %s ；宽 %s" % (
    mp.nstr(m(C_lo), 30), mp.nstr(m(C_hi), 30), mp.nstr(refC, 30), float(C_hi - C_lo)))

# ---------- 4. simplest_fraction 与 certified_prefix 的机制测试 ----------
p("")
p("[T4] Stern-Brocot 最小分母与连分数前缀证书的机制测试")
CASES = [(F(5, 3), F(12, 7), F(17, 10)), (F(3, 2), F(8, 5), F(11, 7)),
         (F(7, 5), F(10, 7), F(17, 12)), (F(11, 7), F(8, 5), F(19, 12)),
         (F(9, 4), F(14, 5), F(5, 2))]
for (A, B, want) in CASES:
    got = R.simplest_fraction(A, B)
    p("     (%s, %s) -> %s ；route-3.md:143 记录 %s ；一致？ %s" % (A, B, got, want, got == want))
# 暴力对照：小分母枚举
def brute(A, B, qmax=200):
    for q in range(1, qmax + 1):
        import math
        p0 = math.floor(A * q) + 1
        while F(p0, q) < B:
            if A < F(p0, q):
                return F(p0, q)
            p0 += 1
    return None
import random
random.seed(20261026)
bad = 0
for _ in range(60):
    q1 = random.randint(1, 60)
    q2 = random.randint(1, 60)
    A = F(random.randint(1, 200), q1)
    B = F(random.randint(1, 200), q2)
    if A >= B:
        A, B = B, A
    if B - A < F(1, 4000) or A <= 0:
        continue
    g = R.simplest_fraction(A, B)
    b = brute(A, B, 400)
    if b is not None and b.denominator < g.denominator:
        bad += 1
        p("     [反例] (%s, %s)：SB 给 %s，暴力给 %s" % (A, B, g, b))
p("     60 组随机区间与暴力枚举对照，矛盾条数 = %d" % bad)
p("     certified_prefix(415/93, 415/93) = %s ；真值 [4;2,6,7]" % (R.certified_prefix(F(415, 93), F(415, 93)),))
pref = R.certified_prefix(d_lo, d_hi, maxlen=120)
p("     delta 区间的连分数前缀长度 %d 位 = %s" % (len(pref), pref))
# 与 mpmath 抽取的连分数对照（仅参照）
mp.dps = 200
y = m(PIN)


def cf_m(x, n):
    out = []
    yy = x
    for _ in range(n):
        a = int(mp.floor(yy))
        out.append(a)
        r = yy - a
        if r == 0:
            break
        yy = 1 / r
    return out
p("     mpmath 抽取同精度连分数前 %d 位一致？ %s" % (
    len(pref), cf_m(y, len(pref)) == pref))

# ---------- 5. eps 的端到端锚点 ----------
p("")
p("[T5] eps(m2, m, K) 端到端锚点（项目记录只作对照）")
KSTAR = 205632218873398596256
e91 = R.eps_bounds(91, 92, KSTAR, d_lo, d_hi, l2)
p("     eps(91, 92, K*) in [%s, %s]" % (mp.nstr(m(e91[0]), 20), mp.nstr(m(e91[1]), 20)))
e88 = R.eps_bounds(88, 92, 77692117359936589403, d_lo, d_hi, l2)
p("     eps(88, 92, 77692117359936589403) in [%s, %s] ；route-4.md:141 记录 6.5947593e-41" % (
    mp.nstr(m(e88[0]), 20), mp.nstr(m(e88[1]), 20)))
e90 = R.eps_bounds(90, 92, KSTAR, d_lo, d_hi, l2)
p("     eps(90, 92, K*) in [%s, %s]（用于最小性对照）" % (
    mp.nstr(m(e90[0]), 20), mp.nstr(m(e90[1]), 20)))

open(HERE + "/results/c2r5_selftest.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] %s/results/c2r5_selftest.out" % HERE)
