#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对 d3r3_mech 的关键单元做计时，定位慢点。只读不写。"""
import sys, time, importlib.util

spec = importlib.util.spec_from_file_location(
    "m", "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/d3-window-tail/cycle-1/scripts/d3r3_mech.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
F = m.F

t0 = time.time()
dlo_r, dhi_r, Clo_r, Chi_r = m.build_consts(32)
print("build_consts(32)", round(time.time() - t0, 2), "s")

t0 = time.time()
orc = m.Oracle(dlo_r, dhi_r, Clo_r, Chi_r)
print("Oracle init", round(time.time() - t0, 2), "s")

t0 = time.time()
cp = orc.cM(90)
print("cM(90)", round(time.time() - t0, 2), "s", m.sci(cp[0], 12))

# 给 pow2_bounds / pow_rat_bounds / ln_bounds 装计时器
acc = {"pow2": [0.0, 0], "pow_rat": [0.0, 0], "ln": [0.0, 0]}
_p2, _pr, _ln = m.pow2_bounds, m.pow_rat_bounds, m.ln_bounds


def w2(*a, **k):
    t = time.time()
    print("    pow2 起：分母位数", len(str(F(a[0]).denominator)), flush=True)
    r = _p2(*a, **k)
    print("    pow2 终", round(time.time() - t, 2), "s", flush=True)
    acc["pow2"][0] += time.time() - t
    acc["pow2"][1] += 1
    return r


def wr(*a, **k):
    t = time.time()
    print("    pow_rat 起", flush=True)
    r = _pr(*a, **k)
    print("    pow_rat 终", round(time.time() - t, 2), "s", flush=True)
    acc["pow_rat"][0] += time.time() - t
    acc["pow_rat"][1] += 1
    return r


def wl(*a, **k):
    t = time.time()
    print("    ln 起：分位", (F(a[0]).numerator.bit_length() - F(a[0]).denominator.bit_length()), flush=True)
    r = _ln(*a, **k)
    print("    ln 终", round(time.time() - t, 2), "s", flush=True)
    acc["ln"][0] += time.time() - t
    acc["ln"][1] += 1
    return r


m.pow2_bounds, m.pow_rat_bounds, m.ln_bounds = w2, wr, wl
K = F(123124614107556571561827996023727480573234158995835769416170731544288569211252109512728894368340633 // 10**50)
t0 = time.time()
lo, hi = orc.phi_bounds(90, K)
dt = time.time() - t0
print("phi_bounds(90, K)", round(dt, 2), "s ->", m.sci(lo, 12), m.sci(hi, 12))
print("  分项：pow2", round(acc["pow2"][0], 2), "s /", acc["pow2"][1], "次；pow_rat",
      round(acc["pow_rat"][0], 2), "s /", acc["pow_rat"][1], "次；ln", round(acc["ln"][0], 2), "s /", acc["ln"][1], "次")

t0 = time.time()
l2 = m.ln2_bounds(65)
print("ln2_bounds(65)", round(time.time() - t0, 2), "s")

t0 = time.time()
lo, hi, R_, tau = m.phi_at_threshold_bounds(90, dlo_r, dhi_r, l2=l2, cpair=cp)
print("phi_at_threshold(90) 缩精度", round(time.time() - t0, 2), "s", m.sci(lo, 16), m.sci(hi, 16))

t0 = time.time()
dlo, dhi, Clo, Chi = m.build_consts(70)
lo, hi, R_, tau = m.phi_at_threshold_bounds(90, dlo, dhi, l2=l2, cpair=cp)
print("phi_at_threshold(90) 全精度 exponent", round(time.time() - t0, 2), "s", m.sci(lo, 16), m.sci(hi, 16))
