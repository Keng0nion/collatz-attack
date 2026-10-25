#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-2 第 9 步：分辨率的非退化演示（修正 r2_f_audit.py 第 [C] 段的退化构造）。

为什么原构造退化：顶点处全部链约束取等，把某个坐标乘性下调后再「压链」，扰动会沿链
传播成整体缩放，最后归一化把它抵消，于是又得到顶点本身（探针读数恰好 0.0）。这不是
分辨率问题，而是构造问题。

正确构造：在 u 表示 y_{j+1} = δ y_j u_j 上取 u_j = 1 − 2^{−e}（e = 10、20、40），
再按 Σ = W 归一。这样链约束按构造成立、形状确有改变，与顶点的相对偏差随 e 变小。
"""
import sys
from fractions import Fraction

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
import mpmath
from r2_common import (delta_rigorous_bounds, v_vertex, vertex, feasible, repair_normalize,
                       S_bounds, LEVEL_MID, LEVEL_FINE, LEVEL_ULTRA, Det)

D_LO7, _ = delta_rigorous_bounds(10 ** 7)
mpmath.mp.dps = 60


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def S_probe(y, cut=10 ** 5):
    tot = mpmath.mpf(0)
    for t in y:
        e = mpmath.mpf(t.numerator) / mpmath.mpf(t.denominator)
        if e > cut:
            continue
        tot += 3 / (mpmath.mpf(2) ** e - 1)
    return tot


def from_u(u, m2, d):
    y = [Fraction(1)]
    for j in range(m2 - 1):
        y.append(y[-1] * d * u[j])
    return y


SETS = [
    ("m2=3  W=210",   3,  Fraction(210)),
    ("m2=5  W=200",   5,  Fraction(200)),
    ("m2=10 W=2000",  10, Fraction(2000)),
    ("m2=20 v=70",    20, None),
    ("m2=91 W=205632218873398596256", 91, Fraction(205632218873398596256)),
]

say("=" * 78)
say("route-2 第 9 步：分辨率的非退化演示（u 表示下的微小松弛）")
say("=" * 78)
for tag, m2, W in SETS:
    if W is None:
        W = Fraction(70) * (D_LO7 ** m2 - 1) / (D_LO7 - 1)
    d = D_LO7
    V0 = list(vertex(m2, d, W, 0))
    ref_m = S_bounds(V0, *LEVEL_MID)
    ref_f = S_bounds(V0, *LEVEL_FINE)
    ref_u = S_bounds(V0, *LEVEL_ULTRA)
    sV = S_probe(V0)
    say(f"\n[{tag}]  v = {float(mpmath.mpf(v_vertex(m2, d, W).numerator)/mpmath.mpf(v_vertex(m2, d, W).denominator)):.9f}")
    for e in (10, 20, 40):
        eps = Fraction(1, 2 ** e)
        for mode in ("全部支", "唯一条"):
            u = [Fraction(1)] * (m2 - 1)
            if mode == "全部支":
                u = [1 - eps] * (m2 - 1)
            else:
                u[-1] = 1 - eps
            y = from_u(u, m2, d)
            lam = max(W / sum(y), Fraction(1) / min(y))
            y = [t * lam for t in y]
            ok, bad = feasible(y, m2, d, W)
            loM, hiM = S_bounds(y, *LEVEL_MID)
            loF, hiF = S_bounds(y, *LEVEL_FINE)
            loU, hiU = S_bounds(y, *LEVEL_ULTRA)
            c1 = all(a >= b for a, b in zip(sorted(y), sorted(V0)))
            r_m = "C1" if c1 else ("C2" if hiM <= ref_m[0] else "未决")
            r_f = "C1" if c1 else ("C2" if hiF <= ref_f[0] else "未决")
            r_u = "C1" if c1 else ("C2" if hiU <= ref_u[0] else ("反例" if loU > ref_u[1] else "未决"))
            ratio = (S_probe(y) / sV - 1) if S_probe(y) > 0 else None
            say(f"    2^-{e} {mode}：可行 {ok}  MID={r_m}  FINE={r_f}  ULTRA={r_u}"
                f"  探针 S(y)/S(V)−1 = {mpmath.nstr(ratio, 6)}")
            if not ok:
                say(f"      （违反：{bad[:3]}）")
say("")
say("读法：\n"
    "  探针差值为 0.0 且各档均未决 = 构造退化（扰动被归一化抵消），不是分辨率结论；\n"
    "  探针差值非零而各档未决 = 真正的分辨率边界（探针看得出、证书判不出）；\n"
    "  某档给出 C2 或 C1 = 该档已能判定。")
