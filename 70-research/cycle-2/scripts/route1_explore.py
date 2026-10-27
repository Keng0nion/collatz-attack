#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-1 探索脚本（仅供规划，不作证据）：用 mpmath 高精度看 K* 格的量级与余量，
决定严格有理证书需要多少位精度、哪些不等式是紧的。证书本身在 route1_cert.py。
"""
from mpmath import mp, mpf, power, log, floor

mp.dps = 400
DELTA = mp.log(3) / mp.log(2)
X0 = mpf(695) * power(2, 60)
KSTAR = 205632218873398596256
M = 92

def log2(x):
    return mp.log(x) / mp.log(2)

def geom(m2):
    return (power(DELTA, m2) - 1) / (DELTA - 1)

C_LOG = log2(mpf(162) / 97 * X0)      # log2((162/97) X0)

def premise_lhs(m2):
    return geom(m2) * C_LOG

def A_of(m2):
    if m2 == M:
        return mpf(0)
    if m2 == M - 1:
        return mpf(3) / X0
    return mpf(97 * (M - m2) + 73) / (54 * X0)

def eps_of(m2, K):
    v = (mpf(m2) / M) * K / geom(m2)
    t = power(2, v) - 1
    return (A_of(m2) + 3 / t + 3 * mpf(m2 - 1) / power(t, DELTA)) / (3 * K * mp.log(2))

print("[E1] 可行性（门槛 G(m2) <= (m2/92) K*）")
for m2 in (88, 89, 90, 91, 92):
    lhs = premise_lhs(m2)
    rhs = (mpf(m2) / M) * KSTAR
    print("   m2=%2d  G=%s  (m2/m)K*=%s  可行？%s  比值=%s" % (
        m2, mp.nstr(lhs, 22), mp.nstr(rhs, 22), lhs <= rhs, mp.nstr(rhs / lhs, 12)))

print()
print("[E2] eps(m2, K*) 全部（1..92），找 argmin 与不可行集")
feas, infeas = [], []
for m2 in range(1, M + 1):
    if premise_lhs(m2) <= (mpf(m2) / M) * KSTAR:
        feas.append(m2)
    else:
        infeas.append(m2)
print("   可行 m2 个数 =", len(feas), " 最小可行 =", min(feas) if feas else None,
      " 最大可行 =", max(feas) if feas else None)
emin, argmin = None, None
for m2 in feas:
    e = eps_of(m2, KSTAR)
    if emin is None or e < emin:
        emin, argmin = e, m2
print("   argmin =", argmin, " eps_opt =", mp.nstr(emin, 30))
print("   不可行 = 92 ？", 92 in infeas)
print("   eps(91) 三项：A 项 =", mp.nstr(A_of(91) / (3 * KSTAR * mp.log(2)), 30),
      " t1 项 =", mp.nstr((3 / (power(2, 1.0) - 1)) , 5))

v91 = (mpf(91) / M) * KSTAR / geom(91)
t91 = power(2, v91) - 1
print("   v(91) =", mp.nstr(v91, 25), " 2^v-1 =", mp.nstr(t91, 25))
print("   A(91) = 3/X0 ？", mp.nstr(A_of(91), 25), " 3/X0 =", mp.nstr(mpf(3) / X0, 25),
      " 170/(54X0) =", mp.nstr(mpf(170) / (54 * X0), 25))
e91 = eps_of(91, KSTAR)
print("   eps(91,K*) =", mp.nstr(e91, 30))
print("   A/(3K ln2) =", mp.nstr(A_of(91) / (3 * KSTAR * mp.log(2)), 30))
print("   t1/(3K ln2) =", mp.nstr((3 / t91) / (3 * KSTAR * mp.log(2)), 30))
print("   t2/(3K ln2) =", mp.nstr((3 * 90 / power(t91, DELTA)) / (3 * KSTAR * mp.log(2)), 30))

print()
print("[E3] delta 的连分数与收敛分母")
def cf_digits(x, nmax):
    out = []
    y = x
    for _ in range(nmax):
        fl = floor(y)
        out.append(int(fl))
        r = y - fl
        if r == 0:
            break
        y = 1 / r
    return out

def convergents(digs):
    pm2, pm1 = 0, 1
    qm2, qm1 = 1, 0
    out = []
    for a in digs:
        p = a * pm1 + pm2
        q = a * qm1 + qm2
        pm2, pm1 = pm1, p
        qm2, qm1 = qm1, q
        out.append((p, q))
    return out

A = cf_digits(DELTA, 60)
print("   a_0..a_45 =", A[:46])
conv = convergents(A[:50])
for j in (39, 40, 41, 42, 43, 44, 45):
    print("   q_%d = %d" % (j, conv[j][1]))
# gamma = [a_0;...;a_41, 2]
GAM = convergents(A[:42] + [2])[-1]
print("   [a0;...;a41,2] = %d / %d" % (GAM[0], GAM[1]))
print("   等于 325919355854421968365/205632218873398596256 ?",
      GAM == (325919355854421968365, 205632218873398596256))
# [P,3]
P3 = convergents(A[:42] + [3])[-1]
print("   [P,3] = %d / %d" % (P3[0], P3[1]), " 3q41+q40 =", 3 * conv[41][1] + conv[40][1])
gamma = mpf(GAM[0]) / GAM[1]
p3 = mpf(P3[0]) / P3[1]
print("   gamma - delta =", mp.nstr(gamma - DELTA, 30))
print("   [P,3] - gamma  =", mp.nstr(p3 - gamma, 30))
print("   [P,3] - (delta + eps_opt) =", mp.nstr(p3 - (DELTA + emin), 30))
print("   eps_opt - (gamma - delta) =", mp.nstr(emin - (gamma - DELTA), 30))
print("   (gamma-delta)/eps_opt =", mp.nstr((gamma - DELTA) / emin, 12))
print("   p42/q42 - delta =", mp.nstr(mpf(conv[42][0]) / conv[42][1] - DELTA, 30))
print("   行列式 |p43 q42 - p42 q43| =", abs(conv[43][0] * conv[42][1] - conv[42][0] * conv[43][1]))
print("   行列式 |p43 (3q41+q40) - (3p41+p40) q43| =",
      abs(conv[43][0] * (3 * conv[41][1] + conv[40][1]) - (3 * conv[41][0] + conv[40][0]) * conv[43][1]))
print("   q42+q43 =", conv[42][1] + conv[43][1], " 3q41+q40+q43 =", 3 * conv[41][1] + conv[40][1] + conv[43][1])

print()
print("[E4] A 项下界 E_lo = (3/X0)/(3 K* ln2) 与 gamma - delta 的比较")
E_lo = (mpf(3) / X0) / (3 * KSTAR * mp.log(2))
print("   E_lo =", mp.nstr(E_lo, 30), " E_lo/(gamma-delta) =", mp.nstr(E_lo / (gamma - DELTA), 12))

print()
print("[E5] K_cross 附近（登记用）：g(K) = eps(92,K) - (gamma-delta)")
def g(K):
    return eps_of(92, K) - (gamma - DELTA)
for Ks in ("3.13195478959172262767e20", "3.13195478959172262933e20", "3.1319547895917226287e20"):
    print("   K=%s  g=%s  可行m2=?" % (Ks, mp.nstr(g(mpf(Ks)), 12)),
          [m2 for m2 in range(1, M + 1) if premise_lhs(m2) <= (mpf(m2) / M) * mpf(Ks)][-1:])
