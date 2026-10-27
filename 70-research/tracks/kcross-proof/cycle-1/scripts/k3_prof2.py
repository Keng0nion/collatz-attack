#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 性能探针 2：定位 K_cross 邻域格最后一步的耗时环节（只打印）。"""
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts")
import k3_rig as K

D = K.delta_bounds()
L2 = K.ln2_bounds()
KST = 205632218873398596256
KX = 313195478959172262876

t0 = time.time()
e92 = K.eps_bounds(92, 92, KX, D[0], D[1], L2)
t1 = time.time()
print("eps(92, KX): %.3f s  = %s" % (t1 - t0, K.sci(e92[0], 22)))
B2lo = K.rd(D[0] + e92[0])
B2hi = K.ru(D[1] + e92[1])
print("beta 区间宽 = %s" % float(B2hi - B2lo))

t0 = time.time()
prefB = K.certified_prefix(B2lo, B2hi, maxlen=250)
t1 = time.time()
print("certified_prefix(beta_KX): %.3f s，位数 = %d" % (t1 - t0, len(prefB)))
print("前 50 位 =", prefB[:50])
if len(prefB) > 46:
    print("42..49 位 =", prefB[42:50])
    print("各指数位上的部分商最大值 =", max(prefB), "（下标", prefB.index(max(prefB)), "）")

t0 = time.time()
prefA = K.certified_prefix(D[0], D[1], maxlen=250)
t1 = time.time()
print("certified_prefix(delta): %.3f s，位数 = %d" % (t1 - t0, len(prefA)))

kk = 0
while kk < min(len(prefA), len(prefB)) and prefA[kk] == prefB[kk]:
    kk += 1
print("首个相异下标 k =", kk)

t0 = time.time()
items = K.semiconv_list_frontier(prefA, prefB, kk)
t1 = time.time()
print("semiconv_list_frontier: %.3f s，条数 = %d" % (t1 - t0, len(items)))

t0 = time.time()
n_in = 0
for (val, src) in items:
    if val > D[1] and val < B2lo:
        n_in += 1
t1 = time.time()
print("比较循环: %.3f s，内点数 = %d" % (t1 - t0, n_in))
