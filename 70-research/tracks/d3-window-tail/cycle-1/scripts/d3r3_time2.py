#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐步计时 phi_at_threshold_bounds（只读不写）。"""
import time, importlib.util
spec = importlib.util.spec_from_file_location(
    "m", "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/d3-window-tail/cycle-1/scripts/d3r3_mech.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
F = m.F

t0 = time.time()
dlo_r, dhi_r, Clo_r, Chi_r = m.build_consts(32)
print("build_consts(32)", round(time.time() - t0, 3), flush=True)
orc = m.Oracle(dlo_r, dhi_r, Clo_r, Chi_r)
t0 = time.time()
cp = orc.cM(88)
print("cM(88)", round(time.time() - t0, 3), flush=True)
l2 = m.ln2_bounds(65)
B_ = m.P2C - 1
t0 = time.time()
r = m.pow_rat_bounds(B_, B_, -dhi_r, -dhi_r, l2, 80)
print("pow_rat B^{-dhi}", round(time.time() - t0, 3), flush=True)
t0 = time.time()
p = m.pow_rat_bounds(m.P2C, m.P2C, F(cp[0], cp[2]), F(cp[0], cp[2]), l2, 80)
print("pow_rat P2C^{tl}", round(time.time() - t0, 3), flush=True)
t0 = time.time()
lo, hi, R_, tau = m.phi_at_threshold_bounds(88, dlo_r, dhi_r, l2=l2, cpair=cp)
print("phi_at_threshold(88)", round(time.time() - t0, 3), "s", m.sci(lo, 16), m.sci(hi, 16), flush=True)
