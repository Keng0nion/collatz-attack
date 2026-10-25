#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 第 7 轮：非降性的正确尺度网格与台阶值集（修正上一轮网格尺度）。

网格一：K_lo = 10^(12 + 0.035 k)，k = 0..259（覆盖 1e12 至 ~2.2e21，含 U(92) 与 K_cross 邻域）
网格二：在 K_cross 两侧的密网格（相对步长 1e-6），检验台阶跳变与上集结构
"""
import sys
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
from mpmath import mp, mpf, power
import r4x_core as R

OUT = []
def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)

R.set_dps(120)
L = mpf("7.5311e11")
U92 = R.sdw_upper(92)
KSTAR = mpf(205632218873398596256)
KCROSS = mpf("313195478959172262850")

p("[I] 非降性网格一：K_lo = 10^(12 + 0.035 k)，k = 0..259")
vals = []
for k in range(260):
    kk = power(10, mpf(12) + mpf("0.035") * k)
    r = R.psi(92, kk)
    vals.append((kk, r["psi"], r["m2"]))
drops = [(vals[i - 1], vals[i]) for i in range(1, len(vals)) if vals[i][1] < vals[i - 1][1]]
p("     点数 %d，覆盖 [%s, %s]；相邻下降次数 %d" % (
    len(vals), mp.nstr(vals[0][0], 8), mp.nstr(vals[-1][0], 8), len(drops)))
p("     台阶值集（Psi 变化时才打印）：")
seen = []
for (kk, ps, m2) in vals:
    if not seen or seen[-1][1] != ps:
        seen.append((kk, ps, m2))
for s in seen:
    p("       自 K_lo=%-22s 起 Psi=%-24s (m2=%s)" % (mp.nstr(s[0], 9), s[1], s[2]))
p()

p("[I2] 非降性网格二：K_cross 两侧密网格（K_cross = %s）" % mp.nstr(KCROSS, 20))
for frac in ["0.999999", "0.9999999", "1", "1.0000001", "1.000001", "1.01"]:
    kk = KCROSS * mpf(frac)
    r = R.psi(92, kk)
    p("     K_lo = K_cross*%-10s = %-26s -> Psi=%-24s (m2=%s) 越界？%s" % (
        frac, mp.nstr(kk, 22), r["psi"], r["m2"], r["psi"] > U92))
p()

p("[I3] U(92) 邻域与 U 之上")
for frac in ["0.99999", "0.9999999999", "1", "1.0000000001", "1.00001"]:
    kk = U92 * mpf(frac)
    r = R.psi(92, kk)
    p("     K_lo = U(92)*%-12s -> Psi=%-24s (m2=%s) 越界？%s" % (
        frac, r["psi"], r["m2"], r["psi"] > U92))
p()

p("[I4] 台阶总表：Psi 的取值与对应的 K_lo 区间")
edges = []
for i, (kk, ps, m2) in enumerate(vals):
    if i == 0 or ps != vals[i - 1][1]:
        edges.append([kk, kk, ps, m2])
    else:
        edges[-1][1] = kk
for e in edges:
    p("     K_lo ∈ [%-22s, %-22s] -> Psi=%-24s (m2=%s)" % (
        mp.nstr(e[0], 9), mp.nstr(e[1], 9), e[2], e[3]))
p()

open("/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts/results/r4x_run6.out", "w").write("\n".join(OUT) + "\n")
