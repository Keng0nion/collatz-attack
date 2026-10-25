#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-2 第 4 步：z3 精确 LRA 独立核验（与第 2、3 步用不同机具重做同一批判定）。

四项检查（全部是线性有理算术，z3 在 LRA 上是精确的有理运算）：
  Z1  min_j y_j = v：对每个 j 断言「P ∧ y_j < v」应 unsat；配合第 2 步已精确验证的
      「顶点 (v, δv, …, δ^{m2−1}v) 可行」，即得 min over P of y_j = v。
  Z2  y_j = 1 不可行：断言「P ∧ y_j <= 1」应 unsat（这是第 2 步 (L1) 引理的 LP 形式）。
  Z3  回收锥含于非负卦限：断言「链约束（齐次）∧ d_1 < 0」应 unsat。
  Z4  严格回绕约束的开集含顶点：断言「y_j >= 1 ∧ 链 ≤ ∧ y_1 < δ y_{m2} ∧ y = V」应 sat。
z3 是可信但未形式化的求解器：以下结果记为「独立计算核验」，不是机器检验的证明。
"""
import sys
import time
from fractions import Fraction

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
import z3
from r2_common import delta_rigorous_bounds, v_vertex, vertex, feasible

D_LO7, D_HI7 = delta_rigorous_bounds(10 ** 7)
D_LO6, D_HI6 = delta_rigorous_bounds(10 ** 6)


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def rat(fr):
    return z3.RealVal(f"{fr.numerator}/{fr.denominator}")


def base_constraints(ys, m2, d, W, strict_wrap=False):
    cons = []
    for j in range(m2):
        cons.append(ys[j] >= 1)
    for j in range(m2):
        if strict_wrap and j == m2 - 1:
            cons.append(ys[(j + 1) % m2] < rat(d) * ys[j])
        else:
            cons.append(ys[(j + 1) % m2] <= rat(d) * ys[j])
    cons.append(sum(ys) >= rat(W))
    return cons


def check(m2, d, W, max_j=None, timeout_ms=60000):
    v = v_vertex(m2, d, W)
    V = list(vertex(m2, d, W, 0))
    ok, bad = feasible(V, m2, d, W)
    res = {"m2": m2, "v": v, "vertex_feasible": ok, "z1": [], "z2": [], "z3": None, "z4": None}
    js = range(m2) if max_j is None else range(min(m2, max_j))
    # Z1 / Z2
    for j in js:
        ys = [z3.Real(f"y{j}") for j in range(m2)]
        s = z3.Solver()
        s.set("timeout", timeout_ms)
        s.add(base_constraints(ys, m2, d, W))
        s.add(ys[j] < rat(v))
        r1 = s.check()
        s2 = z3.Solver()
        s2.set("timeout", timeout_ms)
        ys2 = [z3.Real(f"z{j}") for j in range(m2)]
        s2.add(base_constraints(ys2, m2, d, W))
        s2.add(ys2[j] <= 1)
        r2 = s2.check()
        res["z1"].append((j, str(r1)))
        res["z2"].append((j, str(r2)))
    # Z3 回收锥
    ds = [z3.Real(f"d{j}") for j in range(m2)]
    s3 = z3.Solver()
    s3.set("timeout", timeout_ms)
    for j in range(m2):
        s3.add(ds[(j + 1) % m2] <= rat(d) * ds[j])
    s3.add(ds[0] < 0)
    res["z3"] = str(s3.check())
    # Z4 严格回绕约束下的顶点
    ys = [z3.Real(f"w{j}") for j in range(m2)]
    s4 = z3.Solver()
    s4.set("timeout", timeout_ms)
    s4.add(base_constraints(ys, m2, d, W, strict_wrap=True))
    for j in range(m2):
        s4.add(ys[j] == rat(V[j]))
    res["z4"] = str(s4.check())
    return res


PARAMS = [
    ("E1  m2=2  δ_lo  W=70",                     2,  D_LO7, Fraction(70)),
    ("E2  m2=3  δ_lo  W=210",                    3,  D_LO7, Fraction(210)),
    ("E3  m2=5  δ_lo  W=200",                    5,  D_LO7, Fraction(200)),
    ("E4  m2=10 δ_lo  W=2000",                   10, D_LO7, Fraction(2000)),
    ("E5  m2=20 δ_lo  W 使 v=70",                20, D_LO7, None),
    ("E6  m2=47 δ_lo  W=(47/91)·7e11（只查前 3 个 j）", 47, D_LO7, Fraction(47, 91) * 10 ** 11 * 7),
    ("E7  m2=91 δ_lo  W=…（只查前 2 个 j）",       91, D_LO7, Fraction(205632218873398596256)),
    ("E8  m2=5  δ=317/200 W=200",                5,  Fraction(317, 200), Fraction(200)),
    ("E9  m2=5  δ=3/2  W=200",                   5,  Fraction(3, 2), Fraction(200)),
    ("E10 m2=5  δ_lo  v=1（阈值边界，预期 Z2 有 sat）", 5, D_LO7, None),
]

say("=" * 78)
say("route-2 第 4 步：z3 精确 LRA 独立核验")
say(f"z3 版本 = {z3.get_version_string()}")
say("=" * 78)
rows = []
for tag, m2, d, W in PARAMS:
    if W is None:
        W = (Fraction(70) * (d ** m2 - 1) / (d - 1)) if tag.startswith("E5") else (d ** m2 - 1) / (d - 1)
    maxj = 3 if m2 == 47 else (2 if m2 == 91 else None)
    t0 = time.time()
    res = check(m2, d, W, max_j=maxj)
    z1 = {r for _, r in res["z1"]}
    z2 = {r for _, r in res["z2"]}
    say(f"\n[{tag}]  v = 见下  顶点可行（精确有理） = {res['vertex_feasible']}  用时 {time.time()-t0:.1f} s")
    say(f"    Z1  P ∧ y_j < v 的全部判定集合 = {sorted(z1)}（期望 {{'unsat'}}，查了 "
        f"{len(res['z1'])} 个 j{'' if maxj is None else '（抽样）'}）")
    say(f"    Z2  P ∧ y_j <= 1 的全部判定集合 = {sorted(z2)}（期望 {{'unsat'}}，"
        f"边界情形 E10 预期含 sat）")
    say(f"    Z3  链约束 ∧ d_1 < 0 = {res['z3']}（期望 unsat）")
    say(f"    Z4  严格回绕下 y = V 可满足 = {res['z4']}（期望 sat）")
    rows.append((tag, sorted(z1), sorted(z2), res["z3"], res["z4"]))

say("\n" + "=" * 78)
say("汇总")
for r in rows:
    say("    " + r[0] + " | Z1 " + ",".join(r[1]) + " | Z2 " + ",".join(r[2]) +
        " | Z3 " + r[3] + " | Z4 " + r[4])
say("\n（z3 结果记为独立计算核验；第 2 步的精确有理穷举与它互为独立复算。）")
