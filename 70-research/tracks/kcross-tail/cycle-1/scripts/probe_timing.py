#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""路线 4 的计时探针（只读；不进 verify.py 的正式产物）。

目的：在写 verify.py 之前，量出四组断言各自的实际耗时，确保闸门总用时在 2 分钟以内。
本脚本不写任何仓库文件，不重跑任何证书脚本，只做只读 import 与单点复算。
"""
import sys, time
from fractions import Fraction as F

KP = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
if KP not in sys.path:
    sys.path.insert(0, KP)


def clock(tag, t0):
    print("  [计时] %-46s %8.2f s" % (tag, time.time() - t0))
    return time.time()


KSTAR = 205632218873398596256
Q41 = 77692117359936589403
THI = F("1542566275329005279840718039419280435916173943310179998952443721548967387604624457272573600391707651885171022391000442764034271240234375/4925250774549309901534880012517951725634967408808180833493536675530715221437151326426783281860614455100828498788352")

t0 = time.time()
print("[A] 导入四库")
import k3_rig as K3
t0 = clock("import k3_rig", t0)
import r2_rig as R2
t0 = clock("import r2_rig", t0)
import r4_common as R4
import kc_rig as KC
t0 = clock("import r4_common(含 kc_rig)", t0)

print("[B] 组 2 与组 3 的前置：k3_rig 常数与 eps 梯子")
D = K3.delta_bounds()
t0 = clock("k3_rig.delta_bounds", t0)
C = K3.C_bounds()
L2 = K3.ln2_bounds()
t0 = clock("k3_rig.C_bounds + ln2_bounds", t0)
E = {}
for t in range(83, 93):
    E[t] = K3.eps_bounds(t, 92, KSTAR, D[0], D[1], L2)
t0 = clock("k3_rig.eps_bounds × 10（m2 = 83..92）", t0)
print("      样例 eps(91,92,K*) =", K3.sci(E[91][0], 22))

print("[C] 组 3：连分数前缀与清单")
prefA = K3.certified_prefix(D[0], D[1], maxlen=250)
t0 = clock("certified_prefix(delta) 长度 = %d" % len(prefA), t0)
BETA_LO = K3.rd(D[0] + E[91][0] if 92 not in E else E[91][0])
BETA_LO = K3.rd(D[0] + E[91][0])
BETA_HI = K3.ru(D[1] + E[91][1])
prefB = K3.certified_prefix(BETA_LO, BETA_HI, maxlen=250)
t0 = clock("certified_prefix(beta) 长度 = %d" % len(prefB), t0)
k = 0
while k < min(len(prefA), len(prefB)) and prefA[k] == prefB[k]:
    k += 1
items_cap = K3.semiconv_list_frontier(prefA, prefB, k, cap_q=KSTAR)
t0 = clock("semiconv_list_frontier(cap_q = K*) 条数 = %d" % len(items_cap), t0)
items_full = K3.semiconv_list_frontier(prefA, prefB, k, cap_q=None)
t0 = clock("semiconv_list_frontier(无 cap) 条数 = %d" % len(items_full), t0)

print("[D] 组 1：r2_rig 单点")
R2D = R2.delta_bounds()
t0 = clock("r2_rig.delta_bounds", t0)
R2L2 = R2.ln2_bounds()
e_hi = R2.eps_bounds(92, 92, THI, R2D[0], R2D[1], R2L2)
t0 = clock("r2_rig.eps_bounds(92,92,T_hi)", t0)

print("[E] 组 4：r4_common 不动点（kc_rig 引擎）")
CIV = R4.gauge_C(R4.X0_695)
DLO, DHI, RL2 = R4.consts()
t0 = clock("r4_common.consts + gauge_C", t0)
q_lo, q_hi, info = R4.psi_two_sided(KSTAR, CIV, DLO, DHI, RL2)
t0 = clock("psi_two_sided(K*) → [%s, %s]" % (q_lo, q_hi), t0)
q_lo2, q_hi2, info2 = R4.psi_two_sided(Q41, CIV, DLO, DHI, RL2)
t0 = clock("psi_two_sided(q41) → [%s, %s]" % (q_lo2, q_hi2), t0)

print("[F] 跨库小 v 探针（kc_rig 的 v < 3 补丁路径）")
for t in (3, 5):
    a = KC.eps_bounds(t, 92, 100, KC.delta_bounds()[0], KC.delta_bounds()[1], KC.ln2_bounds())
    b = K3.eps_bounds(t, 92, 100, D[0], D[1], L2)
    print("      m2 = %d, K = 100：kc_rig %s ；k3_rig %s ；相交 %s"
          % (t, KC.sci(a[0], 12), K3.sci(b[0], 12), max(a[0], b[0]) <= min(a[1], b[1])))
t0 = clock("跨库小 v 探针 × 2", t0)
print("总用时 %.2f s" % (time.time() - t0))
