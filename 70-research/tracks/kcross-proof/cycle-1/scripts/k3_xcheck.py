#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 库自检与对拍（本文件的结论只作机制检查；证书由 k3_run_*.py 出）。

对照对象：
  1. 本库 ln2/ln3 的 Machin 式路径 vs 对照路径 vs mpmath（非严格，仅显示）；
  2. 幂原语：对 2^{a/b}（小分母 b）做**精确整数校验** lo^b <= 2^a <= hi^b；
  3. 幂原语 vs c2r5_rig.pow_bounds / pow_2vm1_delta（只读 import，作数值对拍）；
  4. delta 区间 vs c2r5_rig.delta_bounds 与钉住 50 位；
  5. 连分数前缀证书 vs c2r5_rig.certified_prefix。

运行：20-experiments/.venv/bin/python k3_xcheck.py
"""
import sys
from fractions import Fraction as F

import k3_rig as K
from mpmath import mp, mpf, nstr

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts")
import c2r5_rig as R2

mp.dps = 90
OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


p("=" * 74)
p("route-3 库自检：k3_rig.py")
p("=" * 74)

# ---------- 1. 对数 ----------
p("")
p("[1] ln2、ln3 的三条路径（本库 Machin 式为主；另两条只作对照）")
l2 = K.ln2_bounds()
l2a = K.ln2_bounds_alt()
p("    ln2 主路径 [4atanh(1/6)+2atanh(1/99)] 区间宽 = %s" % float(l2[1] - l2[0]))
p("    ln2 对照 A [2atanh(1/7)+2atanh(1/5)]   区间宽 = %s" % float(l2a[1] - l2a[0]))
p("    两路径区间相交（严格）？ %s" % (max(l2[0], l2a[0]) < min(l2[1], l2a[1])))
p("    ln2 主路径 60 位 = %s" % K.dec(l2[0], 60))
p("    mpmath ln2      = %s" % nstr(mp.log(2), 60))
_t = mpf(l2[0].numerator) / l2[0].denominator
_t2 = mpf(l2[1].numerator) / l2[1].denominator
p("    mpmath ln2 落在主路径区间内（非严格对照）？ %s" % (_t <= mp.log(2) <= _t2))
l3 = K.ln3_bounds()
l3a = K.ln3_bounds_alt()
p("    ln3 主路径 [2atanh(1/2)]    宽度 = %s" % float(l3[1] - l3[0]))
p("    ln3 对照 A [ln2+2atanh(1/5)] 宽度 = %s" % float(l3a[1] - l3a[0]))
p("    两路径区间相交（严格）？ %s" % (max(l3[0], l3a[0]) < min(l3[1], l3a[1])))
p("    ln3 主路径 60 位 = %s" % K.dec(l3[0], 60))
p("    mpmath ln3      = %s" % nstr(mp.log(3), 60))
p("    [非严格对照] |本库下界 − mpmath| < 1e-100 ？ %s ; |本库上界 − mpmath| < 1e-100 ？ %s" % (
    abs(mpf(l3[0].numerator) / l3[0].denominator - mp.log(3)) < mpf("1e-100"),
    abs(mpf(l3[1].numerator) / l3[1].denominator - mp.log(3)) < mpf("1e-100")))

# ---------- 2. delta 与 C ----------
p("")
p("[2] delta = ln3/ln2 与 C")
d = K.delta_bounds()
p("    本库 delta 区间宽 = %s ；45 位打印 = %s" % (float(d[1] - d[0]), K.dec(d[0], 62)))
p("    c2r5_rig delta 区间宽 = %s" % float(R2.delta_bounds()[1] - R2.delta_bounds()[0]))
p("    本库区间与 c2r5 区间相交？ %s" % (max(d[0], R2.delta_bounds()[0]) < min(d[1], R2.delta_bounds()[1])))
PIN = "1.58496250072115618145373894394781650875981440769248106045575"
PIN_F = F(int(PIN.replace(".", "")), 10 ** (len(PIN) - 2))
p("    钉住串（截断）与本库下界前 59 位小数逐位一致？ %s" % (K.dec(d[0], 59) == PIN))
C = K.C_bounds()
p("    本库 C = log2((162/97)X0) ∈ [%s, %s] 宽 %s" % (K.dec(C[0], 40), K.dec(C[1], 40), float(C[1] - C[0])))
p("    c2r5_rig C ∈ [%s, %s]" % (K.dec(R2.C_bounds()[0], 40), K.dec(R2.C_bounds()[1], 40)))
p("    两区间相交？ %s" % (max(C[0], R2.C_bounds()[0]) < min(C[1], R2.C_bounds()[1])))

# ---------- 3. 幂原语的精确整数校验 ----------
p("")
p("[3] 幂原语的精确校验：对 x = a/b（b <= 256），检验 lo^b <= 2^a <= hi^b")
CASES = [(3, 5), (7, 3), (1, 1024), (72, 1), (73, 1), (161, 256), (2, 1), (0, 1), (1, 256)]
ok_all = True
for (a, b) in CASES:
    x = F(a, b)
    lo, hi = K.pow2_bounds(x, x)
    if b == 1:
        okL = lo ** b <= 2 ** a
        okH = 2 ** a <= hi ** b
    else:
        okL = lo ** b <= 2 ** a
        okH = 2 ** a <= hi ** b
    ok_all &= bool(okL and okH)
    p("    %s/%s: lo^b <= 2^a <= hi^b ？ %s , %s  （区间相对宽 %s）" % (
        a, b, okL, okH, float((hi - lo) / lo)))
p("    全部通过？ %s" % ok_all)

# ---------- 4. 幂原语 vs c2r5_rig（数值对拍） ----------
p("")
p("[4] 幂原语 vs c2r5_rig.pow_bounds / pow_2vm1_delta（只读对照）")
l2r = R2.ln2_bounds()
for xs in ["72", "74.772951607598", "113.2", "1850.7"]:
    x = F(xs) if "." not in xs else F(int(xs.replace(".", "")), 10 ** (len(xs) - len(xs.split(".")[0]) - 1))
    mine = K.pow2_bounds(x, x)
    theirs = R2.pow_bounds(F(2), F(2), x, x)
    good = max(mine[0], theirs[0]) <= min(mine[1], theirs[1])
    p("    2^%s：本库 [%s, %s]；c2r5 [%s, %s]；相交？ %s" % (
        xs, K.sci(mine[0]), K.sci(mine[1]), K.sci(theirs[0]), K.sci(theirs[1]), good))
x = F(-73) + F(1, 3)
mine = K.pow2_bounds(x, x)
p("    2^(-73+1/3)：本库 [%s, %s]" % (K.sci(mine[0]), K.sci(mine[1])))

vv = (F(72000, 1000), F(72123, 1000))
mine2 = K.t2vm1_delta_bounds(vv[0], vv[1], d[0], d[1])
their2 = R2.pow_2vm1_delta(vv[0], vv[1], d[0], d[1], l2r)
p("    (2^v−1)^δ, v∈[72, 72.123]：本库 [%s, %s]" % (K.sci(mine2[0], 24), K.sci(mine2[1], 24)))
p("                                c2r5 [%s, %s]" % (K.sci(their2[0], 24), K.sci(their2[1], 24)))
p("    相交？ %s" % (max(mine2[0], their2[0]) <= min(mine2[1], their2[1])))

# ---------- 5. 连分数前缀证书 ----------
p("")
p("[5] certified_prefix：本库 vs c2r5_rig")
BETA_LO = d[0] + F(8973221708617136016326, 10 ** 55) * F(1, 10 ** 1)
prefA = K.certified_prefix(d[0], d[1], maxlen=200)
p("    本库 delta 前缀位数 = %d" % len(prefA))
p("    c2r5 delta 前缀位数 = %d" % len(R2.certified_prefix(R2.delta_bounds()[0], R2.delta_bounds()[1], maxlen=300)))
pref70 = prefA[:40]
p("    前 40 位 = %s" % (pref70,))
p("    与 c2r5_cert.log:35 的公共前缀前 40 位一致？ %s" % (
    pref70 == [1, 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55, 1, 4, 3, 1, 1, 15, 1, 9, 2, 5, 7, 1, 1, 4, 8, 1, 11, 1, 20, 2, 1, 10, 1, 4, 1]))

open("/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts/results/k3_xcheck.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/k3_xcheck.out")
