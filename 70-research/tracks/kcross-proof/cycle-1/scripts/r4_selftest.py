#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 4 路自检：库路线互对照 + 复算 c2r5_cert 的两条已知输出 + 计时标定。

运行：/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python r4_selftest.py
"""
import sys
import time

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
sys.path.insert(0, HERE)
from fractions import Fraction as F
import r4_common as C

OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


t0 = time.time()
DLO, DHI, L2 = C.consts()
p("[0] delta ∈ [%s, %s]" % (C.dec(DLO, 45), C.dec(DHI, 45)))
p("    delta 区间宽度 = %s ；ln2 宽度 = %s" % (C.fnum(DHI - DLO), C.fnum(L2[1] - L2[0])))

# 1. C 的两条独立路线：695 专用 atanh 分解 vs 通用 ln 路线
Ca = C.R.C_bounds()
Cb = C.R.C_from_x0(C.X0_695)
p("[1] C(695) 专用路线 ∈ [%s, %s]" % (C.dec(Ca[0], 40), C.dec(Ca[1], 40)))
p("    C(695) 通用路线 ∈ [%s, %s]" % (C.dec(Cb[0], 40), C.dec(Cb[1], 40)))
p("    两区间相交 ？ %s ；宽度 %s 与 %s" % (
    not (Ca[1] < Cb[0] or Cb[1] < Ca[0]), C.fnum(Ca[1] - Ca[0]), C.fnum(Cb[1] - Cb[0])))
C704 = C.gauge_C(C.X0_704)
p("    C(704) ∈ [%s, %s]，宽度 %s" % (C.dec(C704[0], 40), C.dec(C704[1], 40),
                                    C.fnum(C704[1] - C704[0])))
p("    C(704) - C(695) ∈ [%s, %s]" % (
    C.dec(C704[0] - Ca[1], 12), C.dec(C704[1] - Ca[0], 12)))

# 2. 复算 c2r5_cert 第 5 节的 150 步根隔离（K1 = 下二分点）
t1 = time.time()
K1, K2 = C.root_interval(DLO, DHI, L2, steps=150)
p("[2] 150 步根隔离：K1 = %s" % C.dec(K1, 40))
p("    K2 = %s" % C.dec(K2, 40))
p("    对照 c2r5_cert.log:67 打印 313195478959172262876.6365306194907065260231016940260118526233")
p("    宽度 = %s ；相对宽度 = %s ；用时 %.1f 秒" % (
    C.fnum(K2 - K1), C.fnum((K2 - K1) / K1), time.time() - t1))

# 3. K* 处的 Psi 夹逼（对照证书：应为 K*）
t2 = time.time()
q_lo, q_hi, info = C.psi_two_sided(C.KSTAR, Ca, DLO, DHI, L2)
p("[3] Psi_92(K*) ∈ [%s, %s] ；等于 K* ？ %s ；argmin = %s（可行 %d 个，未定 %d 个）；用时 %.1f 秒" % (
    q_lo, q_hi, q_lo == q_hi == C.KSTAR, info["argmin"], len(info["feas"]), len(info["und"]),
    time.time() - t2))

# 4. 计时标定：一个 (a) 量级点与一个 (b) 量级点
for K in (F(753110000000), F(313195478959172262876)):
    t3 = time.time()
    q_lo, q_hi, info = C.psi_two_sided(K, Ca, DLO, DHI, L2)
    p("[4] K = %s ：Psi ∈ [%s, %s]，argmin = %s，可行 %d，未定 %d，用时 %.2f 秒" % (
        K, q_lo, q_hi, info["argmin"], len(info["feas"]), len(info["und"]), time.time() - t3))

p("[5] 总计用时 %.1f 秒" % (time.time() - t0))
open(HERE + "/results/r4_selftest.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/r4_selftest.out")
