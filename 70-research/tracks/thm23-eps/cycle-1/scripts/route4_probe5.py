#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-4 探针五：第一步 ε 的区间端点与 mpmath（dps 60/90）逐位对照到 45 位。"""
import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.set_int_max_str_digits(2000000)
import mpmath as mp
import route4_rig as Rig
import route4_chain as C
import route4_step7 as S7

K = F(7) * 10 ** 11
eps = C.eps_interval(47, K, 73, 695)
print("mine  lo = %s" % S7.sci(eps[0], 45), flush=True)
print("mine  hi = %s" % S7.sci(eps[1], 45), flush=True)
for dps in (60, 90, 140):
    em = C.mpmath_eps_general(47, K, 73, 695, dps=dps)
    print("mp dps=%3d = %s" % (dps, mp.nstr(em, 45)), flush=True)
    emq = F(mp.nstr(em, 45))
    print("   在区间内 = %s" % (eps[0] <= emq <= eps[1]), flush=True)
ep7 = C.eps_interval(90, F(77692117359936589403), 73, 695)
print()
print("步6（m2=90）mine lo = %s" % S7.sci(ep7[0], 30), flush=True)
em = C.mpmath_eps_general(90, F(77692117359936589403), 73, 695, dps=90)
print("步6 mp        = %s" % mp.nstr(em, 30), flush=True)
print("   在区间内 = %s" % (ep7[0] <= F(mp.nstr(em, 30)) <= ep7[1]), flush=True)
