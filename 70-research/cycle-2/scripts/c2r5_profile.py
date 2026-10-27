#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 2 轮第 5 路：单步耗时探针（决定证书脚本的精度与步数）。"""
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts")
t00 = time.time()
import c2r5_rig as R

print("import %.2fs" % (time.time() - t00))
t0 = time.time()
d = R.delta_bounds()
print("delta_bounds %.2fs" % (time.time() - t0))
t0 = time.time()
c = R.C_bounds()
print("C_bounds %.2fs  C=%.20f" % (time.time() - t0, float(c[0])))
dl, dh = d
t0 = time.time()
e = R.eps_bounds(91, 92, 205632218873398596256, dl, dh, R.ln2_bounds())
print("eps91 %.2fs  %.16e  相对宽度 %.2e" % (time.time() - t0, float(e[0]), float((e[1] - e[0]) / e[0])))
t0 = time.time()
e2 = R.eps_bounds(88, 92, 77692117359936589403, dl, dh, R.ln2_bounds())
print("eps88 %.2fs  %.16e" % (time.time() - t0, float(e2[0])))
t0 = time.time()
e3 = R.eps_bounds(92, 92, 313195478959172262900, dl, dh, R.ln2_bounds())
print("eps92(Kcross) %.2fs  %.16e" % (time.time() - t0, float(e3[0])))
t0 = time.time()
s = R.simplest_fraction(dl, F(1.585))
print("simplest_small %.2fs  %s" % (time.time() - t0, s))
t0 = time.time()
s2 = R.simplest_fraction(dl, R.ru(dh + e[1]))
print("simplest_cert %.2fs  分母 %d" % (time.time() - t0, s2.denominator))
t0 = time.time()
pre = R.certified_prefix(dl, dh)
print("certified_prefix(delta) 长度 %d  %.2fs" % (len(pre), time.time() - t0))
print("总耗时 %.2fs" % (time.time() - t00))
