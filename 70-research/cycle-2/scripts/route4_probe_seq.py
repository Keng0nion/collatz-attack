#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探针：delta 的收敛项、半收敛项与「最佳上逼近」记录序列（gap 单调性检查）。"""
from mpmath import mp, mpf, log, power, floor

mp.dps = 120
d = mp.log(3) / mp.log(2)


def cf(x, n):
    out = []
    y = x
    for _ in range(n):
        fl = floor(y)
        out.append(int(fl))
        r = y - fl
        if r == 0:
            break
        y = 1 / r
    return out


A = cf(d, 60)
print("A[0:20] =", A[:20])
print("A[40:50] =", A[40:50])

# 收敛项：p_{-2}/q_{-2}=0/1, p_{-1}/q_{-1}=1/0
pm2, pm1 = 0, 1
qm2, qm1 = 1, 0
convs = [(0, 1), (1, 0)]
for a in A:
    p = a * pm1 + pm2
    q = a * qm1 + qm2
    convs.append((p, q))
    pm2, pm1 = pm1, p
    qm2, qm1 = qm1, q

for i in range(38, 50):
    p, q = convs[i + 2]
    g = mpf(p) / q - d
    print("conv idx=%2d q=%s gap=%s side=%s" % (i, q, mp.nstr(g, 12), "up" if g > 0 else "dn"))

# 全部半收敛项（介于相邻收敛项之间），denominator 上限
CAP = 10 ** 24
cands = set()
for n in range(0, 52):
    pn, qn = convs[n + 2]
    pn1, qn1 = convs[n + 3]
    tmax = A[n + 2] if n + 2 < len(A) else 0
    for t in range(1, tmax + 2):
        p = pn + t * pn1
        q = qn + t * qn1
        if q <= CAP:
            cands.add((p, q))
cands = sorted(cands, key=lambda pq: pq[1])
ups = [(p, q, mpf(p) / q - d) for (p, q) in cands if mpf(p) / q > d]
print("半收敛项中在上侧的条数 =", len(ups), "（分母上限 1e24）")
best = []
for (p, q, g) in ups:
    if not best or g < best[-1][2]:
        best.append((p, q, g))
print("记录序列条数 =", len(best))
for (p, q, g) in best:
    if q > 10 ** 19 and q < 10 ** 23:
        print("  q=%s gap=%s" % (q, mp.nstr(g, 12)))
