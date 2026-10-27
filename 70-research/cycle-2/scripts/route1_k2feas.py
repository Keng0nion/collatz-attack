#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-1 单点补核（严格有理算术，快跑）：
route1_extra.py 跑通版里的 [J3] 是硬编码占位（当时写成 True 而未计算），
本脚本把该条的实质内容独立算一遍：
  (1) m2 = 92 在 Ka、Kb、K2 上可行：G(92) 的严格上界 ≤ Ka；
  (2) Ka < K2 < Kb 与 K* < K2 的整数比较；
  (3) K2 处的 ε(91, K2) 下界与 ε(92, K2) 下界的大小关系（决定 [四] 里取的 min 是否正确）。
输出即判据；任一失败退出码 1。
"""
import sys
import os
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from fractions import Fraction as F
from route1_rig import (ctx, geom_bounds, eps_bounds, A_of, iv_round, sci_str,
                        M_CYCLES, KSTAR)

T0 = time.time()
FAIL = []


def ck(tag, cond, note=""):
    ok = bool(cond)
    print("   %-58s %s%s" % (tag, "True" if ok else "False", ("   " + note) if note else ""))
    if not ok:
        FAIL.append(tag)
    return ok


C = ctx()
Ka = 313195478959172262767
Kb = 313195478959172262934
K2 = 313195478959172262876
l2hi = C["l2hi"]

print("=" * 78)
print("route-1 单点补核：G(92) 的可行性区间与 K2 处 ε 下界的取 min")
print("=" * 78)
print("时间：%s" % time.strftime("%Y-%m-%d %H:%M:%S"))
print()

# (1) G(92) 的严格区间（上界用 c 的上界乘 geom 的上界）
g92 = geom_bounds(M_CYCLES, C["DL"], C["DH"])
G92_lo = iv_round((g92[0] * C["c_lo"], g92[0] * C["c_lo"]))[0]
G92_hi = iv_round((g92[1] * C["c_hi"], g92[1] * C["c_hi"]))[1]
print("   G(92) ∈ [%s, %s]（与主证书 [四] 的区间一致）" % (sci_str(G92_lo, 25), sci_str(G92_hi, 25)))
ck("[M1] m2 = 92 在 Ka 可行：G(92) 上界 ≤ Ka", G92_hi <= F(Ka),
   "余量日历（Ka − G 上界）= %s" % sci_str(F(Ka) - G92_hi, 20))
ck("[M2] 同一条覆盖 Kb 与 K2（因 G 不依赖 K）", G92_hi <= F(Kb) and G92_hi <= F(K2))

# (2) 整数比较
ck("[M3] K* < K2 < Kb 且 Ka < K2", KSTAR < K2 < Kb and Ka < K2)
ck("[M4] Ka、Kb 同为正整数且 Kb − Ka = 167", Kb - Ka == 167)

# (3) K2 处两个 ε 下界的大小关系
E_lo_91 = A_of(91) / (3 * F(K2) * l2hi)
(elo92, ehi92), _, _, _ = eps_bounds(M_CYCLES, F(K2), C)
print("   ε(91, K2) 的 A 项下界 = %s" % sci_str(E_lo_91, 30))
print("   ε(92, K2) 的下界     = %s" % sci_str(elo92, 30))
ck("[M5] min 取自 m2 = 92 的那一支（即 ε(92,K2) 下界 < ε(91,K2) 下界）", elo92 < E_lo_91)
# 判据只取「余量为正」；余量量级 6.5e-62，与 route1_extra.py 的 [K1]/[L1] 逐位一致
_margin = elo92 - (F(325919355854421968365, 205632218873398596256) - C["dlo"])
ck("[M6] 该 min 仍 > 左余量 γ − δ 的严格界（余量为正）", _margin > 0,
   "余量 = %s（route1_extra 的 [K1] 给同一数字）" % sci_str(_margin, 45))
print()
print("=" * 78)
if FAIL:
    print("失败判据：%s" % FAIL)
    print("退出码 1")
    sys.exit(1)
print("全部判据通过；退出码 0；用时 %.1f 秒" % (time.time() - T0))
sys.exit(0)
