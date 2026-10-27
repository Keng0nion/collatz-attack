#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-4 性能探针：把第一条轨迹第一步拆开计时，定位热点。"""
import os
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.set_int_max_str_digits(2000000)
import route4_rig as Rig
import route4_chain as C


def t(label, fn, *a, **kw):
    t0 = time.time()
    r = fn(*a, **kw)
    print("%-42s %8.3fs" % (label, time.time() - t0), flush=True)
    return r


K0 = C.K0
print("K0 =", K0, flush=True)
t("build_tables", C.build_tables)
mm = t("m2_max_feasible(K0,695)", C.m2_max_feasible, K0, 695)
print("  ->", mm, flush=True)
eps = t("eps_interval(47,K0,73,695)", C.eps_interval, 47, K0, 73, 695)
print("  eps 宽 %.2e" % float(Rig.wid(eps)), flush=True)
t("pow2_interval(v) 单测", lambda: None)
# 手动分步
dl = Rig.delta_bounds()
d91 = Rig.delta_pow_prod(91)
v = Rig.idiv(Rig.imul((K0 * F(47, 91), K0 * F(47, 91)), (dl[0] - 1, dl[1] - 1)),
             (C.GEOM[47][0] - 1, C.GEOM[47][1] - 1))
print("v =", str(v[0])[:40], "...", flush=True)
t("  pow2_interval(v)", Rig.pow2_interval, v)
t("  oneminus_pow2delta(v,DL)", Rig.oneminus_pow2delta, v, dl)
g = t("q_gamma(eps)", C.q_gamma, eps)
print("  ->", (g["q"], g["k"], g["ak"], g["bk"]) if g else None, flush=True)
