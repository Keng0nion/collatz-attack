#!/usr/bin/env python3
"""debug_sa.py：定位 check_I_sa_exact.py 的对照组为何报告「0 阶不符」。

对最简单的情形（对称 ±1 游走）手算前三阶，与脚本的中间量逐项对照。
"""

from fractions import Fraction

a, b = Fraction(1), Fraction(-1)
p = Fraction(1, 2)

NN = 4
states = {0: Fraction(1)}
left = {0: Fraction(1)}
for n in range(1, NN + 1):
    ns = {}
    for x, w in states.items():
        for val, pr in ((a, p), (b, 1 - p)):
            y = x + val
            if y > 0:
                ns[y] = ns.get(y, Fraction(0)) + w * pr
    states = ns
    left[n] = sum(states.values())
print("left (P(S_i>0, i<=n)) =", {k: str(v) for k, v in left.items()})

Pk = {}
for k in range(1, NN + 1):
    dist = {0: Fraction(1)}
    for _ in range(k):
        nd = {}
        for x, w in dist.items():
            nd[x + a] = nd.get(x + a, Fraction(0)) + w * p
            nd[x + b] = nd.get(x + b, Fraction(0)) + w * (1 - p)
        dist = nd
    Pk[k] = sum(w for x, w in dist.items() if x > 0)
print("P(S_k>0) =", {k: str(v) for k, v in Pk.items()})

F = [Fraction(0)] * (NN + 1)
for k in range(1, NN + 1):
    F[k] = Pk[k] / k
cc = [Fraction(0)] * (NN + 1)
cc[0] = Fraction(1)
for n in range(1, NN + 1):
    s = Fraction(0)
    for k in range(1, n + 1):
        s += k * F[k] * cc[n - k]
    cc[n] = s / n
print("cc (exp 级数系数) =", {k: str(v) for k, v in enumerate(cc)})
print("逐阶比较：")
for n in range(1, NN + 1):
    print("   n=%d  left=%s  cc=%s  相等=%s" % (n, left[n], cc[n], left[n] == cc[n]))
