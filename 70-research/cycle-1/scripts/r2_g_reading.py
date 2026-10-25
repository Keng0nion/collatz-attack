#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-2 第 7 步：读法的必要性（回应子问题 2「读法唯一性」）。

勘误原文（corr.txt:28 至 :34）：「let the cycle be entered in such a way that this sum is
maximal. Then x_{m−m2} ≤ x_m」。两种读法：
  读法 X（本路采用，勘误的顶点步需要它）：「this sum」= Σx。取 Σx 最大的窗 → x_{m−m2} ≤ x_m，
    与 Lemma 20 的 x_{m−m2+1} < δx_{m−m2} 合并得回绕约束 x_{m−m2+1} < δx_m。
  读法 K：「this sum」= Σk（上文鸽孔步里的和）。取 Σk 最大的窗只给 k_{m−m2} ≤ k_m，
    由 x_i ≥ k_i 推不出 x_{m−m2} ≤ x_m，故回绕约束不可用。
本脚本给出读法 K 下的显式反例（精确有理验证），说明读法 X 是承重的、不能替换。
"""
import sys
from fractions import Fraction

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
import mpmath
from r2_common import (delta_rigorous_bounds, v_vertex, vertex, feasible,
                       S_bounds, LEVEL_MID, delta_rigorous_bounds as _db)

D_LO7, D_HI7 = delta_rigorous_bounds(10 ** 7)


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def feasible_no_wrap(y, m2, d, W):
    """读法 K 的可行域 P'：y_j >= 1；仅内部链 y_{j+1} <= δ y_j（j = 1..m2−1）；Σy >= W。"""
    bad = []
    for j in range(m2):
        if y[j] < 1:
            bad.append(f"y{j+1}<1")
    for j in range(m2 - 1):
        if y[j + 1] > d * y[j]:
            bad.append(f"内部链 {j+2}")
    if sum(y) < W:
        bad.append("Σy<W")
    return len(bad) == 0, bad


SETS = [
    ("E3  m2=5   W=200",                      5,  D_LO7, Fraction(200)),
    ("E7  m2=91  W=205632218873398596256",    91, D_LO7, Fraction(205632218873398596256)),
    ("E2  m2=3   W=210",                      3,  D_LO7, Fraction(210)),
    ("E9  m2=5   δ=3/2  W=200",               5,  Fraction(3, 2), Fraction(200)),
]

say("=" * 78)
say("route-2 第 7 步：读法 K（Σk 读法）下顶点命题是否仍成立")
say("=" * 78)
say("显式候选：y* = (W − (m2−1), 1, 1, …, 1)（首个坐标为 W − m2 + 1，其余全为 1）")
say("")
for tag, m2, d, W in SETS:
    v = v_vertex(m2, d, W)
    V = list(vertex(m2, d, W, 0))
    ystar = [W - (m2 - 1)] + [Fraction(1)] * (m2 - 1)
    okP, badP = feasible(ystar, m2, d, W)          # 原（带回绕）多面体
    okK, badK = feasible_no_wrap(ystar, m2, d, W)  # 读法 K 的多面体
    lo, hi = S_bounds(ystar, *LEVEL_MID)
    rlo, rhi = S_bounds(V, *LEVEL_MID)
    ratio_lo = lo - rhi                             # > 0 即精确证书意义下的反例
    say(f"[{tag}]")
    say(f"    y* 在带回绕的 P 中可行 = {okP}（违反：{badP[:2]}）")
    say(f"    y* 在读法 K 的 P' 中可行 = {okK}（违反：{badK[:2]}）")
    say(f"    S(y*) 的严格界 = [{float(lo)} , {float(hi)}]（f(1) = 3 故下界 ≥ {3*(m2-1)}）")
    say(f"    S(V) 的严格界  = [{float(rlo):.6e} , {float(rhi):.6e}]")
    say(f"    反例判据 S_lo(y*) − S_hi(V) = {float(ratio_lo):.6e} → "
        f"{'反例成立' if ratio_lo > 0 else '不成立'}")
    if m2 <= 6:
        say(f"    精确差值下界 = 3·(m2−1) − S_hi(V) = {float(Fraction(3*(m2-1)) - rhi):.6e}"
            f"（用 f(1) = 3 精确值与 S_hi(V) 的精确差）")

say("")
say("交叉核对（读法 X 下同一构造为何不可行）：y* 违反的正是回绕约束 y_1 <= δ y_{m2}：")
tag, m2, d, W = SETS[2]
ystar = [W - (m2 - 1)] + [Fraction(1)] * (m2 - 1)
say(f"    m2={m2}, δ={d}, y_1 = {ystar[0]}, δ·y_{m2} = {d} → y_1 > δ·y_{m2} = "
    f"{ystar[0] > d * ystar[-1]}（故 y* 被回绕约束排除）")
say("")
say("结论口径：读法 K 下有显式可行反例（精确有理验证），故勘误的顶点论证不能按读法 K 读；")
say("这只是「读法 X 是承重的」这一事实陈述，不构成对勘误原文措辞的判定。")
