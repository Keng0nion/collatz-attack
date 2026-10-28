#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""路线 3 定向反例搜索 ③ 的定位探针：找出完整清单枚举的真实代价。

逐阶段打时间戳（flush），先给连分数尾部的部分商上界，再分别计时
cap_q = 10**9 与 cap_q = None 的 semiconv_list_frontier 调用。
"""
import sys
import time
from fractions import Fraction as F

SCRIPTS = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
sys.path.insert(0, SCRIPTS)
import k3_rig as K


def p(*a):
    print(("[t=%.1fs] " % (time.time() - T0)) + " ".join(str(x) for x in a), flush=True)


T0 = time.time()
M = 92
KSTAR = 205632218873398596256
D = K.delta_bounds()
CB = K.C_bounds()
L2 = K.ln2_bounds()
p("常数就绪：delta 宽 = %s ；C 宽 = %s" % (float(D[1] - D[0]), float(CB[1] - CB[0])))

E91 = K.eps_bounds(91, M, KSTAR, D[0], D[1], L2)
BETA_LO = K.rd(D[0] + E91[0])
BETA_HI = K.ru(D[1] + E91[1])
p("E91 与 beta 就绪")

prefA = K.certified_prefix(D[0], D[1], maxlen=250)
p("prefA 就绪，长度 = %d" % len(prefA))
prefB = K.certified_prefix(BETA_LO, BETA_HI, maxlen=250)
p("prefB 就绪，长度 = %d" % len(prefB))
k = 0
while k < min(len(prefA), len(prefB)) and prefA[k] == prefB[k]:
    k += 1
p("首个相异下标 k = %d ；a_k = %d ；b_k = %d" % (k, prefA[k], prefB[k]))
tailA = prefA[k:]
tailB = prefB[k:]
p("prefA 尾部长度 = %d ；最大部分商 = %d" % (len(tailA), max(tailA) if tailA else None))
p("prefB 尾部长度 = %d ；最大部分商 = %d" % (len(tailB), max(tailB) if tailB else None))
p("prefA 尾部前 30 项 = %s" % tailA[:30])
p("prefA 尾部最大项的下标（相对 k）= %d" % (tailA.index(max(tailA)) if tailA else -1))
p("prefB 尾部前 30 项 = %s" % tailB[:30])
p("prefB 尾部最大项的下标（相对 k）= %d" % (tailB.index(max(tailB)) if tailB else -1))

# 枚举规模预估：sum_{j=1..k+1} a_j (alpha 侧) + b_j (beta 侧)
sA = sum(prefA[1:k + 2])
sB = sum(prefB[1:k + 2])
p("枚举规模预估（sum a_j, j=1..k+1）= %d（alpha）；%d（beta）" % (sA, sB))

t = time.time()
capped = K.semiconv_list_frontier(prefA, prefB, k, cap_q=KSTAR)
p("cap_q = K* 清单条数 = %d ；用时 %.2f 秒" % (len(capped), time.time() - t))

t = time.time()
capped9 = K.semiconv_list_frontier(prefA, prefB, k, cap_q=10 ** 9)
p("cap_q = 1e9 清单条数 = %d ；用时 %.2f 秒" % (len(capped9), time.time() - t))

t = time.time()
full = K.semiconv_list_frontier(prefA, prefB, k, cap_q=None)
p("cap_q = None 清单条数 = %d ；用时 %.2f 秒" % (len(full), time.time() - t))
