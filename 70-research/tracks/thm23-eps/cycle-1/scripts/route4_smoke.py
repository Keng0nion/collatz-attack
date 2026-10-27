#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-4 冒烟测试：快/慢两条 ε 路径对照 + 计时。"""
import os
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route4_rig as Rig
import route4_step7 as S7

t0 = time.time()
print("delta 宽 %.2e" % float(Rig.wid(Rig.delta_bounds())))
t1 = time.time()
print("t delta %.2fs" % (t1 - t0))
e_fast = S7.step7_eps(206000000000000000000)
t2 = time.time()
print("fast eps(2.06e20) 宽 %.2e 用时 %.2fs" % (float(Rig.wid(e_fast)), t2 - t1))
print("  = [%s, %s]" % (S7._frac_dec(e_fast[0], 25), S7._frac_dec(e_fast[1], 25)))
e_slow = S7.step7_eps(206000000000000000000, slow=True)
t3 = time.time()
print("slow eps(2.06e20) 宽 %.2e 用时 %.2fs" % (float(Rig.wid(e_slow)), t3 - t2))
print("  慢路径区间包含快路径区间?", e_slow[0] <= e_fast[0] and e_fast[1] <= e_slow[1])
em = S7.mpmath_eps(206000000000000000000, 60)
print("  mpmath = %s" % em)
print("  mpmath in fast? %s ; in slow? %s" %
      (float(e_fast[0]) <= float(em) <= float(e_fast[1]),
       float(e_slow[0]) <= float(em) <= float(e_slow[1])))
t4 = time.time()
xi = S7.mantle_interval(F(2) * 10 ** 19)
print("x(2.0e20) 区间宽 %.2e 用时 %.2fs  lo=%s" %
      (float(Rig.wid(xi)), time.time() - t4, S7._frac_dec(xi[0], 12)))
t5 = time.time()
a, b = S7.solve_K(F(111, 100))
print("K@(x=1.11) in (%s, %s) 宽 %.1e 用时 %.1fs" %
      (S7._frac_dec(a, 6), S7._frac_dec(b, 6), float(b - a), time.time() - t5))
