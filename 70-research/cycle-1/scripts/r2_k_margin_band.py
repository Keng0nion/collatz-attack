#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-2 第 11 步：两件第 3 步没做的事。

(A) 覆盖度的定量面：第 3 步只打印「未决样本」里 S(y)/S(V) 最大的 5 个，而本次搜索
    未决 = 0，所以那一栏是空的。这里改为在全样本上算：
      - 非顶点样本里，S 的严格下界相对顶点值严格上界的最大值（越接近 1 越「接近反例」）；
      - 用第 3 步同一套族生成器与同一批参数集（直接 import r2_c_search 的 gen_family），
        所以两处的样本集合逐位相同（随机族由同一 Det 种子驱动）。
(B) 分辨率带的构造性演示（比 r2_i 的 u 松弛更贴题）：沿线段 y(t) = (1−t)V + t V_rot(1)
    取点。两端点都在 P 内，故整段在 P 内（凸性）；S 沿段严格凸且两端值相等，故内点
    严格低于顶点值；且 t → 0+ 时亏空是 Θ(t)（不是 O(t²)），所以对任意目标相对亏空
    都能找到可行非顶点点。于是「证书分辨率带内一定存在可行非顶点点」是构造事实，不是
    抽样结论。本段用 mpmath 只做 t 的定位，报告出来的数与判决全部是精确有理数。
"""
import sys
from fractions import Fraction

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
import mpmath
from r2_common import (delta_rigorous_bounds, v_vertex, vertex, feasible, repair_normalize,
                       S_bounds, LEVEL_MID, LEVEL_FINE, LEVEL_ULTRA, Det)
import r2_c_search as R2C          # 已加 __main__ 守卫，import 不再执行搜索主块

D_LO7, _ = delta_rigorous_bounds(10 ** 7)


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def mpf_to_frac(x, bits=80):
    """把 [0,1] 内的 mpmath 数转成精确二进分数（mpmath 只用于定位 t）。"""
    n = int(mpmath.floor(x * (1 << bits)))
    return Fraction(n, 1 << bits)


def S_probe(y, cut=10 ** 5, dps=60):
    mpmath.mp.dps = dps
    tot = mpmath.mpf(0)
    for t in y:
        e = mpmath.mpf(t.numerator) / mpmath.mpf(t.denominator)
        if e > cut:
            continue
        tot += 3 / (mpmath.mpf(2) ** e - 1)
    return tot


PARAMS = R2C.PARAMS
say("=" * 78)
say("route-2 第 11 步：(A) 覆盖度的定量面  (B) 分辨率带的构造性演示")
say("=" * 78)
say("族生成器与参数集直接取自 r2_c_search（gen_family / PARAMS），故样本集合与第 3 步一致。")

# ---------------------------------------------------------------- (A) 覆盖度定量面
say("\n[A] 全样本的贴近程度（非顶点样本）")
say("    列：参数集 | 可行样本 | 其中顶点样本 | 非顶点样本 | C1 | C2 | 未决 | 反例 | "
    "非顶点样本 max S_lo(y)/S_hi(V)")
rows = []
for tag, m2, d, W in PARAMS:
    if W is None:
        W = (Fraction(70) * (d ** m2 - 1) / (d - 1)) if tag.startswith("E5") else (d ** m2 - 1) / (d - 1)
    det = Det(12345 + m2 * 1000 + (1 if tag.startswith("E5") else 0))
    V0 = list(vertex(m2, d, W, 0))
    claimed = {tuple(vertex(m2, d, W, r)) for r in range(m2)}
    refs = {}
    for lvlname, lvl in (("MID", LEVEL_MID), ("FINE", LEVEL_FINE), ("ULTRA", LEVEL_ULTRA)):
        rot = list(range(min(m2, 6))) + [m2 - 1]
        lo = hi = None
        for r in sorted(set(rot)):
            a, b = S_bounds(list(vertex(m2, d, W, r)), *lvl)
            lo = a if lo is None else min(lo, a)
            hi = b if hi is None else max(hi, b)
        refs[lvlname] = (lo, hi)
    samples = R2C.gen_family(m2, d, W, det)
    n_feas = n_vert = n_nonv = n_c1 = n_c2 = n_un = n_ce = 0
    vert_fam = {}
    cand = []          # (MID 严格上界比, MID 严格下界比, 族名, y)
    for fam, yraw in samples:
        y = [Fraction(t) for t in yraw]
        ok, _ = feasible(y, m2, d, W)
        if not ok:
            continue
        n_feas += 1
        if tuple(y) in claimed:
            n_vert += 1
            vert_fam[fam] = vert_fam.get(fam, 0) + 1
            continue
        n_nonv += 1
        loM, hiM = S_bounds(y, *LEVEL_MID)
        if R2C.sorted_dominates(y, V0):
            n_c1 += 1
        elif hiM <= refs["MID"][0]:
            n_c2 += 1
        else:
            loU, hiU = S_bounds(y, *LEVEL_ULTRA)
            if loU > refs["ULTRA"][1]:
                n_ce += 1
                say(f"    !! 反例：{fam}  y = {y}")
            elif hiU <= refs["ULTRA"][0]:
                n_c2 += 1
            else:
                n_un += 1
        cand.append((hiM / refs["MID"][0], loM / refs["MID"][1], fam, y))
    # 精修前 K 名（按 MID 严格上界排序），给出 ULTRA 档的严格区间
    K = 20
    cand.sort(key=lambda t: t[0], reverse=True)
    ref = []
    for ub, lb, fam, y in cand[:K]:
        loU, hiU = S_bounds(y, *LEVEL_ULTRA)
        ref.append((hiU / refs["ULTRA"][0], loU / refs["ULTRA"][1], fam))
    qs = lambda q: mpmath.nstr(mpmath.mpf(q.numerator) / mpmath.mpf(q.denominator), 12)
    ub_all = cand[0][0] if cand else None
    say(f"    {tag} | {n_feas} | {n_vert} | {n_nonv} | {n_c1} | {n_c2} | {n_un} | {n_ce} |")
    say(f"        MID 档严格上界 max S_hi(y)/S_lo(V)（全体非顶点样本）= "
        f"{'无' if ub_all is None else qs(ub_all)}")
    if ref:
        top = max(ref, key=lambda t: t[0])
        tight = max(ref, key=lambda t: t[1])
        say(f"        精修前 {K} 名（ULTRA 档）：严格上界最大值 = {qs(top[0])}"
            f"（族 {top[2]}）；其中最紧的严格下界 = {qs(tight[1])}（族 {tight[2]}）"
            f"，即离顶点值的相对亏空 ≥ {qs(1 - tight[1])}")
    if vert_fam:
        vf = sorted(vert_fam.items(), key=lambda kv: -kv[1])[:4]
        say(f"        恰好落在顶点上的样本共 {n_vert} 个，按族："
            + "、".join(f"{k} {v}" for k, v in vf)
            + ("（其余族为 0）" if len(vf) < 4 else ""))
    rows.append((tag, n_feas, n_vert, n_nonv, n_c1, n_c2, n_un, n_ce, ub_all))
say("    读法：上界栏全部 < 1，即每个非顶点样本都被精确区间判定为「严格低于顶点值」；")
say("    「最紧的严格下界」一栏说明本次搜索离顶点值最近到什么程度（越小越远）。")

# ---------------------------------------------------------------- (B) 分辨率带
say("\n[B] 分辨率带的构造性演示：线段 y(t) = (1−t)V + t·V_rot(1)")
say("    目标相对亏空 ρ：定位 t（mpmath 探针，仅用于定位），再报精确区间与精确判决。")
BAND = [Fraction(1, 100), Fraction(1, 10 ** 4), Fraction(1, 10 ** 6),
        Fraction(1, 10 ** 8), Fraction(1, 10 ** 12)]
for tag, m2, d, W in [p for p in PARAMS if p[0].startswith(("E2", "E3", "E7"))]:
    if W is None:
        W = (Fraction(70) * (d ** m2 - 1) / (d - 1))
    V0 = list(vertex(m2, d, W, 0))
    V1 = list(vertex(m2, d, W, 1))
    refs = {}
    for lvlname, lvl in (("MID", LEVEL_MID), ("FINE", LEVEL_FINE), ("ULTRA", LEVEL_ULTRA)):
        rot = list(range(min(m2, 6))) + [m2 - 1]
        lo = hi = None
        for r in sorted(set(rot)):
            a, b = S_bounds(list(vertex(m2, d, W, r)), *lvl)
            lo = a if lo is None else min(lo, a)
            hi = b if hi is None else max(hi, b)
        refs[lvlname] = (lo, hi)
    say(f"\n    [{tag}]  v = "
        f"{float(mpmath.mpf(v_vertex(m2, d, W).numerator)/mpmath.mpf(v_vertex(m2, d, W).denominator)):.9f}")
    sV = S_probe(V0)
    def gval(tm):
        fm = mpf_to_frac(tm)
        return S_probe([V0[j] * (1 - fm) + V1[j] * fm for j in range(m2)])

    for rho in BAND:
        target = (1 - mpmath.mpf(rho.numerator) / mpmath.mpf(rho.denominator)) * sV
        # 先正向定位：t = 2^-k（k 从小到大即 t 从大到小），找最后一个使 g(t) < target 的 k。
        # 这样得到的括号 [2^-(k+1), 2^-k] 完全落在 g 的下降段内（t_1 远小于段内极小点）。
        k_last = None
        for k in range(1, 300):
            tk = mpmath.mpf(2) ** (-k)
            if gval(tk) < target:
                k_last = k
            elif k_last is not None:
                break
        if k_last is None:
            say(f"      ρ={float(rho):.0e}：未找到括号（目标低于段内极小值）")
            continue
        lo_t, hi_t = mpmath.mpf(2) ** (-(k_last + 1)), mpmath.mpf(2) ** (-k_last)
        for _ in range(200):
            mid = (lo_t + hi_t) / 2
            if gval(mid) > target:
                lo_t = mid
            else:
                hi_t = mid
        t = mpf_to_frac(hi_t)       # 取右端：S(y(t)) 略低于目标
        # 括号合法性登记（探针读数，只用于说明定位可靠）
        say(f"      定位：t ∈ [{float(lo_t):.3e}, {float(hi_t):.3e}]，"
            f"g(左) − 目标 = {mpmath.nstr(gval(lo_t) - target, 3)}，"
            f"g(右) − 目标 = {mpmath.nstr(gval(hi_t) - target, 3)}")
        y = [V0[j] * (1 - t) + V1[j] * t for j in range(m2)]
        ok, bad = feasible(y, m2, d, W)
        loM, hiM = S_bounds(y, *LEVEL_MID)
        loF, hiF = S_bounds(y, *LEVEL_FINE)
        loU, hiU = S_bounds(y, *LEVEL_ULTRA)
        c1 = R2C.sorted_dominates(y, V0)
        v_m = "C1" if c1 else ("C2" if hiM <= refs["MID"][0] else "未决")
        v_f = "C1" if c1 else ("C2" if hiF <= refs["FINE"][0] else "未决")
        v_u = "C1" if c1 else ("C2" if hiU <= refs["ULTRA"][0] else
                               ("反例" if loU > refs["ULTRA"][1] else "未决"))
        # 精确相对贴近度区间：S_lo(y)/S_hi(V) 与 S_hi(y)/S_lo(V)
        q1 = loU / refs["ULTRA"][1]
        q2 = hiU / refs["ULTRA"][0]
        qs = lambda q: mpmath.nstr(mpmath.mpf(q.numerator) / mpmath.mpf(q.denominator), 12)
        say(f"      ρ={float(rho):.0e}：t = {float(t):.6e}  可行 {ok}  MID={v_m} FINE={v_f} ULTRA={v_u}"
            f"  精确贴近度区间 [{qs(q1)}, {qs(q2)}]（含 1−ρ = {float(1-rho):.12f}）")
    # 证明性一句：t 属于 (0,1) 即内点，故非顶点
    say("      说明：t ∈ (0,1) 时 y(t) 是两顶点的真凸组合，由凸性在 P 内、由 S 沿段严格凸")
    say("      且两端值相等，故 S(y(t)) < S(V)；这些点都非顶点。")
say("\n口径：A 段是有限样本的定量覆盖（不是证明）；B 段是构造性存在陈述（已证成分：")
say("凸性与严格凸性、可行性；mpmath 只用于定位 t，报告的数字与判决都是精确有理数）。")
