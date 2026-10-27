#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 性能探针：定位 eps_bounds 的耗时环节（只打印，不作证据）。"""
import sys
import time

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts")
import k3_rig as K

D = K.delta_bounds()
L2 = K.ln2_bounds()
KST = 205632218873398596256

t0 = time.time()
vl, vh = K.v_bounds(91, 92, KST, D[0], D[1])
t1 = time.time()
print("v_bounds: %.3f s  v ∈ [%s, %s]" % (t1 - t0, float(vl), float(vh)))

t0 = time.time()
p2 = K.pow2_bounds(vl, vh)
t1 = time.time()
print("pow2_bounds: %.3f s" % (t1 - t0))

t0 = time.time()
pt = K.t2vm1_delta_bounds(vl, vh, D[0], D[1])
t1 = time.time()
print("t2vm1: %.3f s" % (t1 - t0))

t0 = time.time()
e = K.eps_bounds(91, 92, KST, D[0], D[1], L2)
t1 = time.time()
print("eps_bounds(91): %.3f s  eps ∈ [%s, %s]" % (t1 - t0, K.sci(e[0], 22), K.sci(e[1], 22)))

t0 = time.time()
e = K.eps_bounds(83, 92, KST, D[0], D[1], L2)
t1 = time.time()
print("eps_bounds(83): %.3f s  eps ∈ [%s, %s]" % (t1 - t0, K.sci(e[0], 22), K.sci(e[1], 22)))

t0 = time.time()
for t in (83, 84, 85, 86, 87, 88, 89, 90, 91):
    K.eps_bounds(t, 92, KST, D[0], D[1], L2)
t1 = time.time()
print("整条梯子(83..91): %.3f s" % (t1 - t0))
