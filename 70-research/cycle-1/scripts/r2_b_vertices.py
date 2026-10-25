#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-2 第 2 步：精确有理算术下的顶点集穷举。

输入是多面体定义本身（2m2+1 条约束），不读任何既有脚本的输出。

两条路线：
  A. 约简穷举（对任意 m2）：先精确验证「y_j = 1 不可行」这一初等引理
     （判据 (δ^{m2}−1)/(δ−1) < W，纯有理比较），于是任一顶点必须有 m2 条活跃约束
     落在「m2 条循环链约束 + 1 条和约束」这 m2+1 条里。逐个枚举这 m2+1 个大小 m2 的
     子集，精确解线性方程组、查秩、查可行性。
  B. 全穷举（小 m2 用）：枚举全部 C(2m2+1, m2) 个活跃子集，不依赖引理 A，作交叉核对。
两者给出同一顶点集时，顶点集即被钉住（仍是有限穷举，不含未证步骤）。
本脚本不做目标函数 S 的比较（那在第 3 步）。
"""
import sys
import time
from fractions import Fraction
from itertools import combinations

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
from r2_common import (delta_rigorous_bounds, v_vertex, vertex, feasible,
                       constraint_list, solve_exact)

D_LO7, D_HI7 = delta_rigorous_bounds(10 ** 7)
D_LO6, D_HI6 = delta_rigorous_bounds(10 ** 6)


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def rank_exact(rows, ncols):
    """精确秩（Fraction 行阶梯）。"""
    M = [[Fraction(v) for v in r] for r in rows]
    rank = 0
    for col in range(ncols):
        piv = None
        for i in range(rank, len(M)):
            if M[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        pv = M[rank][col]
        M[rank] = [v / pv for v in M[rank]]
        for i in range(len(M)):
            if i != rank and M[i][col] != 0:
                f = M[i][col]
                M[i] = [M[i][j] - f * M[rank][j] for j in range(ncols)]
        rank += 1
    return rank


def active_rank(y, m2, d, W):
    """点 y 处活跃约束的法向量集的秩（=m2 即为顶点的秩证书）。"""
    cons = constraint_list(m2, d, W)
    rows = []
    for a, b, sense in cons:
        val = sum(a[j] * y[j] for j in range(m2))
        if val == b:
            rows.append(a)
    return rank_exact(rows, m2), len(rows)


def enumerate_vertices(m2, d, W, say_fn=print):
    """返回 (约简法顶点集, 说明列表)。"""
    found = {}
    notes = []
    threshold = (d ** m2 - 1) / (d - 1)
    cond = W > threshold
    notes.append(f"    (L1) y_j = 1 不可行的初等引理判据 (δ^m2−1)/(δ−1) < W："
                 f"{threshold.numerator.bit_length()} 位分子 / {threshold.denominator.bit_length()} 位分母 vs W = {W}  → {cond}")
    # 子集：m2 条链约束去掉第 j 条（j = 0..m2−1），再加和约束；另一种是「不要和约束」
    cons = constraint_list(m2, d, W)
    chain = cons[m2:2 * m2]           # m2 条链约束
    sumc = cons[2 * m2]
    for j in range(m2):
        rows = [chain[i][0] for i in range(m2) if i != j] + [sumc[0]]
        b = [chain[i][1] for i in range(m2) if i != j] + [sumc[1]]
        sol, rank = solve_exact(rows, b)
        if sol is None or rank < m2:
            notes.append(f"    子集 j={j}（去掉链 {j+1}）：无唯一解（秩 {rank}）")
            continue
        ok, bad = feasible(sol, m2, d, W)
        if ok:
            key = tuple(sol)
            found[key] = j
        else:
            notes.append(f"    子集 j={j}：解不可行 {bad[:2]}")
    # 「不要和约束」那一支：全部 m2 条链约束取等
    rows = [c[0] for c in chain]
    b = [c[1] for c in chain]
    sol, rank = solve_exact(rows, b)
    notes.append(f"    子集「全链、无和约束」：{'无解（秩 ' + str(rank) + '，与 δ^m2 = 1 矛盾一致）' if sol is None else '有解 ' + str(sol[:2])}")
    return found, notes


def full_enumeration(m2, d, W, cap=None):
    """全活跃子集穷举（不依赖 L1），返回顶点集。"""
    cons = constraint_list(m2, d, W)
    n = len(cons)
    verts = {}
    cnt = 0
    for S in combinations(range(n), m2):
        cnt += 1
        rows = [cons[i][0] for i in S]
        b = [cons[i][1] for i in S]
        sol, rank = solve_exact(rows, b)
        if sol is None or rank < m2:
            continue
        ok, _ = feasible(sol, m2, d, W)
        if ok:
            verts[tuple(sol)] = S
    return verts, cnt


PARAMS = [
    ("E1  m2=2  δ_lo   W=70",                 2,  D_LO7, Fraction(70)),
    ("E2  m2=3  δ_lo   W=210",                3,  D_LO7, Fraction(210)),
    ("E3  m2=5  δ_lo   W=200",                5,  D_LO7, Fraction(200)),
    ("E4  m2=10 δ_lo   W=2000",               10, D_LO7, Fraction(2000)),
    ("E5  m2=20 δ_lo   W 使 v=70",            20, D_LO7, None),
    ("E6  m2=47 δ_lo   W=(47/91)·7e11",       47, D_LO7, Fraction(47, 91) * 10 ** 11 * 7),
    ("E7  m2=91 δ_lo   W=205632218873398596256", 91, D_LO7, Fraction(205632218873398596256)),
    ("E8  m2=5  δ=317/200 W=200",             5,  Fraction(317, 200), Fraction(200)),
    ("E9  m2=5  δ=3/2  W=200",                5,  Fraction(3, 2), Fraction(200)),
    ("E10 m2=5  δ_lo   W=(δ^5−1)/(δ−1)（阈值上的边界情形 v=1）", 5, D_LO7, None),
    ("E11 m2=3  δ_hi   W=210",                3,  D_HI6, Fraction(210)),
    ("E12 m2=6  δ_lo   W=500",                6,  D_LO7, Fraction(500)),
]

FULL_FOR = {2, 3, 4, 5, 6}

say("=" * 78)
say("route-2 第 2 步：精确有理顶点集穷举")
say("=" * 78)

all_summary = []
for tag, m2, d, W in PARAMS:
    if W is None:
        if tag.startswith("E5"):
            W = Fraction(70) * (d ** m2 - 1) / (d - 1)      # 使 v = 70
        else:
            W = (d ** m2 - 1) / (d - 1)                     # 阈值上的边界（v = 1）
    t0 = time.time()
    say(f"\n[{tag}]  δ = {d.numerator}/{d.denominator}")
    v = v_vertex(m2, d, W)
    say(f"    v = W(δ−1)/(δ^m2−1) 的分子位数 = {v.numerator.bit_length()}，分母位数 = {v.denominator.bit_length()}")
    found, notes = enumerate_vertices(m2, d, W, say)
    for nline in notes:
        say(nline)
    # 与解析顶点比对
    analytic = {tuple(vertex(m2, d, W, rot)) for rot in range(m2)}
    same = set(found.keys()) == analytic
    say(f"    约简穷举：唯一可行顶点数 = {len(found)}；与解析的 m2 个循环旋转相同 = {same}"
        f"（解析集大小 {len(analytic)}）")
    # 秩证书
    cert = []
    for y in found:
        r, nact = active_rank(y, m2, d, W)
        cert.append((r, nact))
    say(f"    每个顶点的活跃约束法向量秩（应为 m2 = {m2}）：{sorted(set(cert))}")
    # 全穷举交叉核对
    if m2 in FULL_FOR:
        fv, cnt = full_enumeration(m2, d, W)
        say(f"    全穷举（C(2m2+1, m2) = {cnt} 个子集，不依赖 L1）：可行顶点数 = {len(fv)}；"
            f"与约简一致 = {set(fv.keys()) == set(found.keys())}")
    # 浮点摘要
    import mpmath
    mpmath.mp.dps = 30
    vf = mpmath.mpf(v.numerator) / mpmath.mpf(v.denominator)
    say(f"    v ≈ {mpmath.nstr(vf, 18)}（浮点仅作摘要）")
    all_summary.append((tag, m2, len(found), same, time.time() - t0))

say("\n" + "=" * 78)
say("汇总：参数集 / m2 / 顶点数 / 与解析一致 / 用时（秒）")
for row in all_summary:
    say("    " + " | ".join(str(x) if not isinstance(x, float) else f"{x:.1f}" for x in row))
say("\n（本步结论限于：在这些参数集上，顶点集被精确穷举钉住；不含 S 的比较。）")
