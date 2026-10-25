#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-2 第 8 步：m = 92 型参数的多面体层面覆盖（不涉及 Ψ 迭代，也不改 m = 92 的判定）。

说明：本路只做多面体层面的反例搜索。这里把 m = 92 相关的两组参数（m2 = 89 配 K = 1e20；
m2 = 92 配 K* = 205632218873398596256）放进同一套精确算术流程，看顶点机制是否变化。
参数来源：Ψ 网格的 K_lo = 1e20 → m2 = 89（materials.md §2.2 内第 7 条）；
K* 为链的不动点值（同处）。W = (m2/m)·K。
"""
import sys
from fractions import Fraction

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
import mpmath
import z3
from r2_common import (delta_rigorous_bounds, v_vertex, vertex, feasible, repair_normalize,
                       S_bounds, constraint_list, solve_exact,
                       LEVEL_MID, LEVEL_FINE, LEVEL_ULTRA, Det)

D_LO7, D_HI7 = delta_rigorous_bounds(10 ** 7)


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def rat(fr):
    return z3.RealVal(f"{fr.numerator}/{fr.denominator}")


def reduce_enum(m2, d, W):
    """链加和约简穷举（与第 2 步同一算法，见 r2_b_vertices.py）。"""
    cons = constraint_list(m2, d, W)
    chain = cons[m2:2 * m2]
    sumc = cons[2 * m2]
    found = {}
    for j in range(m2):
        rows = [chain[i][0] for i in range(m2) if i != j] + [sumc[0]]
        b = [chain[i][1] for i in range(m2) if i != j] + [sumc[1]]
        sol, rank = solve_exact(rows, b)
        if sol is None or rank < m2:
            continue
        ok, _ = feasible(sol, m2, d, W)
        if ok:
            found[tuple(sol)] = j
    return found


def S_probe(y, cut=10 ** 5):
    mpmath.mp.dps = 40
    tot = mpmath.mpf(0)
    for t in y:
        e = mpmath.mpf(t.numerator) / mpmath.mpf(t.denominator)
        if e > cut:
            continue
        tot += 3 / (mpmath.mpf(2) ** e - 1)
    return tot


SETS = [
    ("m = 92, m2 = 89, K = 1e20",        92, 89, D_LO7, Fraction(10) ** 20),
    ("m = 92, m2 = 92, K = K*（205632218873398596256）", 92, 92, D_LO7, Fraction(205632218873398596256)),
]

say("=" * 78)
say("route-2 第 8 步：m = 92 型参数的多面体层面覆盖")
say("=" * 78)
for tag, m, m2, d, K in SETS:
    W = Fraction(m2, m) * K
    v = v_vertex(m2, d, W)
    say(f"\n[{tag}]  W = (m2/m)K = {W if W.denominator == 1 else W.numerator / 1}（分数 {W}）")
    say(f"    v = {float(mpmath.mpf(v.numerator)/mpmath.mpf(v.denominator)):.9f}"
        f"  （真 δ 下同一 W 的 v 由 mpmath 另行核对，见下）")
    mpmath.mp.dps = 40
    delta = mpmath.log(3) / mpmath.log(2)
    Wm = mpmath.mpf(W.numerator) / mpmath.mpf(W.denominator)
    v_true = Wm * (delta - 1) / (delta ** m2 - 1)
    say(f"    真 δ 下 v = {mpmath.nstr(v_true, 18)}（与 δ_lo 下的 {float(mpmath.mpf(v.numerator)/mpmath.mpf(v.denominator)):.9f} 对照）")
    # 顶点穷举
    found = reduce_enum(m2, d, W)
    analytic = {tuple(vertex(m2, d, W, r)) for r in range(m2)}
    say(f"    约简穷举：可行顶点数 = {len(found)}；与 m2 个循环旋转相同 = {set(found) == analytic}")
    # z3：坐标下界与 y_j = 1 不可行（抽前 2 个 j）
    for j in range(min(2, m2)):
        ys = [z3.Real(f"y{j}_{i}") for i in range(m2)]
        s = z3.Solver(); s.set("timeout", 120000)
        for i in range(m2):
            s.add(ys[i] >= 1)
        for i in range(m2):
            s.add(ys[(i + 1) % m2] <= rat(d) * ys[i])
        s.add(sum(ys) >= rat(W))
        s.add(ys[j] < rat(v))
        r1 = s.check()
        s2 = z3.Solver(); s2.set("timeout", 120000)
        zs = [z3.Real(f"z{j}_{i}") for i in range(m2)]
        for i in range(m2):
            s2.add(zs[i] >= 1)
        for i in range(m2):
            s2.add(zs[(i + 1) % m2] <= rat(d) * zs[i])
        s2.add(sum(zs) >= rat(W))
        s2.add(zs[j] <= 1)
        r2 = s2.check()
        say(f"    z3（j={j+1}）：P ∧ y_j < v = {r1}（期望 unsat）；P ∧ y_j <= 1 = {r2}（期望 unsat）")
    # 搜索（顶点、均匀、平坦、两段、梳型、随机、扰动）
    V0 = list(vertex(m2, d, W, 0))
    ref_u = S_bounds(V0, *LEVEL_ULTRA)
    ref_m = S_bounds(V0, *LEVEL_MID)
    sV = S_probe(V0)
    det = Det(31337 + m2)
    samples = []
    for r in range(m2):
        samples.append(("顶点旋转", list(vertex(m2, d, W, r))))
    samples.append(("均匀", [W / m2] * m2))
    samples.append(("顶点加平坦", [v] + [d * v] * (m2 - 1)))
    for r in (Fraction(1, 2), Fraction(3, 4), Fraction(1, 1) / d, Fraction(1, 4)):
        for k in (1, m2 // 2, m2 - 1):
            u = [Fraction(1)] * (m2 - 1)
            for jj in range(k, m2 - 1):
                u[jj] = r
            y = [Fraction(1)]
            for jj in range(m2 - 1):
                y.append(y[-1] * d * u[jj])
            lam = max(W / sum(y), Fraction(1) / min(y))
            samples.append(("两段型", [t * lam for t in y]))
            u2 = [r] * (m2 - 1)
            for jj in range(k, m2 - 1):
                u2[jj] = Fraction(1)
            y = [Fraction(1)]
            for jj in range(m2 - 1):
                y.append(y[-1] * d * u2[jj])
            lam = max(W / sum(y), Fraction(1) / min(y))
            samples.append(("两段型", [t * lam for t in y]))
    for r in (Fraction(1, 2), Fraction(1, 4)):
        u = [r if j % 2 == 0 else Fraction(1) for j in range(m2 - 1)]
        y = [Fraction(1)]
        for jj in range(m2 - 1):
            y.append(y[-1] * d * u[jj])
        lam = max(W / sum(y), Fraction(1) / min(y))
        samples.append(("梳型", [t * lam for t in y]))
    for _ in range(120):
        y = [Fraction(det.between(1, 4096), det.pick([1, 2, 4, 8, 64])) for _ in range(m2)]
        y = repair_normalize(y, m2, d, W)
        samples.append(("随机修复", y))
        u = [min(Fraction(det.between(1, 1024), 1024), Fraction(1)) for _ in range(m2 - 1)]
        yy = [Fraction(1)]
        for jj in range(m2 - 1):
            yy.append(yy[-1] * d * u[jj])
        lam = max(W / sum(yy), Fraction(1) / min(yy))
        samples.append(("随机链型", [t * lam for t in yy]))
    for e in (Fraction(1, 1024), Fraction(1, 64), Fraction(1, 16)):
        y = list(V0)
        for j in range(0, m2, max(1, m2 // 6)):
            y[j] = y[j] * (1 - e)
        samples.append(("顶点乘性扰动", repair_normalize(y, m2, d, W)))
        y = list(V0)
        for j in range(0, m2, max(1, m2 // 6)):
            y[j] = y[j] * (1 + e)
        samples.append(("顶点乘性扰动", repair_normalize(y, m2, d, W)))
    n_feas = n_c1 = n_c2 = n_un = n_ce = 0
    best = None
    for fam, y in samples:
        if y is None:
            continue
        y = [Fraction(t) for t in y]
        ok, _ = feasible(y, m2, d, W)
        if not ok:
            continue
        n_feas += 1
        if all(a >= b for a, b in zip(sorted(y), sorted(V0))):
            n_c1 += 1
            continue
        loM, hiM = S_bounds(y, *LEVEL_MID)
        if hiM <= ref_m[0]:
            n_c2 += 1
            continue
        loU, hiU = S_bounds(y, *LEVEL_ULTRA)
        if loU > ref_u[1]:
            n_ce += 1
            say(f"    !! 反例：{fam}  y = {y}")
            continue
        if hiU <= ref_u[0]:
            n_c2 += 1
            continue
        n_un += 1
        r = float(S_probe(y) / sV)
        best = r if best is None else max(best, r)
    say(f"    样本：可行 {n_feas}；C1 {n_c1}；C2 {n_c2}；未决 {n_un}；反例 {n_ce}"
        f"（未决的最大探针比值 {best}）")
say("\n口径：以上只到多面体层面；不涉及 Ψ 迭代，也不改「m = 92（勘误口径）不被排除」的判定。")
