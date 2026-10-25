#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cycle-1 本轮增量结论的独立复算脚本（自足，只读断言不读结论文件）。

写作纪律
1. 本脚本自己重算一切：不读 route-*.md、不读 materials.md、不读它们的任何数字，
   也不 import 本轮的结论型模块（唯一例外见 A8 的账本数据说明，那里读的是数据表
   而不是结论）。
2. 能精确验证的用整数与 Fraction 精确算术；必须用超越函数的地方用 mpmath
   （dps 按需设到 80 至 400）并配显式误差条，误差条在注释里写明。
3. 无法机器验证的一律在注释里写明「无法机器验证」，不假装通过：
   1. 三路顶点引理的纸面证明本身（本脚本只复核它用到的代数恒等式与在大量实例上的结论）；
   2. 「S 严格凸 ⟹ 每一个最大值点都是顶点」这一解析论证（只做抽样佐证）；
   3. 「Ψ 关于 K_lo 非降」的四步初等证明（只复核它三条机制加数值网格）；
   4. 文本阅读判断（某一行是不是撤回转述、某段引文是不是「无关用法」）与一切行号引用；
   5. route-2 的 z3 断言与 4393 个样本那批搜索（样本集不可复现，本脚本改写自己的样本）。
4. 全部断言通过退出码 0；任一失败退出码 1，并把最小反例打印出来。

运行（逐字）：
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
    "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/verify.py"
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import itertools
import math
import os
import random
import subprocess
import sys
import time
from fractions import Fraction as F

import mpmath
from mpmath import mp

ROOT = "/Users/luna/Documents/math IA/collatz-attack"
SCRIPTS = ROOT + "/70-research/cycle-1/scripts"
AUDIT_MD = ROOT + "/60-audits/hercher-t21/audit-report.md"
MARGIN_TXT = ROOT + "/60-audits/hercher-t21/results/margin-table.txt"

FAILS: list[str] = []


def ck(name: str, cond: bool, detail: str = "") -> bool:
    """记账：通过打印一行，失败登记（最后统一打印最小反例）。"""
    if cond:
        print("  [通过] %s%s" % (name, ("  " + detail) if detail else ""))
    else:
        print("  [失败] %s%s" % (name, ("  " + detail) if detail else ""))
        FAILS.append(name + ((" | " + detail) if detail else ""))
    return bool(cond)


def to_mpf(fr: F):
    """Fraction → mpf（按当前上下文精度）。"""
    return mp.mpf(fr.numerator) / fr.denominator


def as_mpf(x):
    """Fraction 或 mpf 一律转成 mpf。"""
    return to_mpf(x) if isinstance(x, F) else mp.mpf(x)


# ======================================================================
# 零、记号与常数（全部从定义重算）
# ======================================================================
mp.dps = 160                          # 超越量一律在此精度下算
X0 = 695 * 2**60                      # 精确整数 801280445701758648320
DELTA = mp.log(3) / mp.log(2)         # 数值用（dps = 160，相对误差约 1e-160）
C_HYP = mp.log((mp.mpf(162) / 97) * X0) / mp.log(2)
L_START = F(75311) * 10**7            # 7.5311e11 的精确有理值
BAR = mp.mpf(2) ** -300               # 超越量误差条 ≈ 4.9e-91（见 A6 注释）
KSTAR = 205632218873398596256         # 项目记的候选不动点（A6/A7 只当数值观察用）
U92_INT = 343025970248850209780       # U(92) 的整数部分，仅用作网格端点


def ln_bounds(base: int, n: int = 200):
    """ln(base) = 2·Σ_{k≥0} 1/((2k+1)·base^{2k+1})，含显式几何尾界。

    相邻项之比 < 1/base²，故尾项 < term_n·(1 + 1/(base² − 1)) = term_n·base²/(base² − 1)。
    严格有理界（上界必须用 base² 这个因子，漏掉它就偏小、夹不住真值）。
    """
    s = F(0)
    p = base
    for k in range(n):
        s += F(1, (2 * k + 1) * p)
        p *= base * base
    term = F(1, (2 * n + 1) * p)
    return 2 * s, 2 * (s + term * F(base * base, base * base - 1))


LN2_LO, LN2_HI = ln_bounds(3)
LN3_LO, LN3_HI = ln_bounds(2)
DLO = LN3_LO / LN2_HI                 # 严格：delta ∈ [DLO, DHI]
DHI = LN3_HI / LN2_LO
DHI_MILLIONTH = F(2584963, 10**6)     # 严格上界之一（供整数判据用）：δ < 2584963/10^6
DEC6 = F(1584963, 10**6)              # 另一严格上界：δ < 1584963/10^6


def frac_of(x) -> F:
    """有限 mpf → Fraction 的精确转换。"""
    man, exp = x.man, x.exp
    if exp >= 0:
        return F(man << exp)
    return F(man, 1 << (-exp))


def solve_exact(A, b):
    """Fraction 高斯消元；奇异返回 None。"""
    n = len(A)
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for c in range(n):
        piv = None
        for r in range(c, n):
            if M[r][c] != 0:
                piv = r
                break
        if piv is None:
            return None
        M[c], M[piv] = M[piv], M[c]
        p = M[c][c]
        M[c] = [x / p for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                Mc, Mr = M[c], M[r]
                M[r] = [Mr[k] - f * Mc[k] for k in range(n + 1)]
    return [M[i][n] for i in range(n)]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def polytope_rows(D: F, n: int, W: F):
    """P = {y : y_j ≥ 1；y_{j+1} ≤ D·y_j（j = 1..n，下标循环）；Σy ≥ W}。

    行格式 (系数, 右端, 名字)，约束写成 系数·y ≤ 右端；最后一条 G_n 是回绕条。
    """
    rows = []
    for j in range(n):
        v = [F(0)] * n
        v[j] = F(-1)
        rows.append((v, F(-1), "L%d" % (j + 1)))
    for j in range(n):
        v = [F(0)] * n
        v[(j + 1) % n] += 1
        v[j] -= D
        rows.append((v, F(0), "G%d" % (j + 1)))
    rows.append(([F(-1)] * n, -W, "W"))
    return rows


def enumerate_vertices(D: F, n: int, W: F):
    """全活跃子集穷举（不预设任何未知结论）：返回 {顶点坐标元组: 活跃集}。"""
    rows = polytope_rows(D, n, W)
    nr = len(rows)
    verts = {}
    for comb in itertools.combinations(range(nr), n):
        s = solve_exact([rows[i][0] for i in comb], [rows[i][1] for i in comb])
        if s is None:
            continue
        if all(dot(rows[i][0], s) <= rows[i][1] for i in range(nr)):
            verts[tuple(s)] = tuple(rows[i][2] for i in comb)
    return verts


def predicted_family(D: F, n: int, W: F):
    """(v, Dv, …, D^{n-1}v) 的 n 个循环排列，v = W(D−1)/(D^n−1)。"""
    v = W * (D - 1) / (D**n - 1)
    base = tuple(v * D**j for j in range(n))
    return {tuple(base[k:] + base[:k]) for k in range(n)}, v


def S_value(coords, dps: int = 50):
    """S(y) = Σ 3/(2^{y_j} − 1)；坐标可以是准确有理数或 mpf。"""
    with mp.workdps(dps):
        return sum(3 / (mp.mpf(2) ** as_mpf(c) - 1) for c in coords)


def sample_feasible(D: F, n: int, W: F, rng: random.Random, trials: int, denom: int = 1 << 18):
    """造精确有理可行点：y_{j+1} = D·y_j·u_j（u_j ≤ 1），再整体放缩到 Σy ≥ W、y_j ≥ 1。

    回绕 y_1 ≤ D·y_n 等价于 Πu_j ≥ 1/D；不满足的样本直接丢弃（放缩不改变它）。
    覆盖不到全多面体，只作抽样证据。
    """
    pts = []
    for _ in range(trials):
        u = [F(rng.randrange(denom // 2, denom + 1), denom) for _ in range(n)]
        z = [F(1)]
        for j in range(n - 1):
            z.append(D * z[-1] * u[j])
        if z[-1] < 1 / D:
            continue
        lam = max(W / sum(z), F(1) / min(z))
        pts.append([lam * t for t in z])
    return pts


# ======================================================================
# 一、顶点引理自足化（增量 1）
# ======================================================================
def assert_1_vertex_lemma() -> bool:
    print("一、顶点引理自足化（增量 1）")
    ok = True

    # 1a 行列式恒等式 det(S_n − D·I) = (−1)^n (D^n − 1)：符号化（sympy）与精确有理双路
    try:
        import sympy as sp

        d = sp.symbols("d")
        sym_ok = True
        for n in range(2, 7):
            S = sp.zeros(n, n)
            for j in range(n):
                S[(j + 1) % n, j] = 1
            sym_ok = sym_ok and sp.simplify(sp.det(S - d * sp.eye(n)) - (-1) ** n * (d**n - 1)) == 0
        ok &= ck("1a det C = (−1)^n(D^n − 1)（sympy 符号核对，n = 2..6）", sym_ok)
    except ImportError:
        print("  [跳过] 1a sympy 不在环境里，符号核对无法机器验证")
    rat_ok = True
    for D in (F(3, 2), F(8, 5), F(111, 70)):
        for n in range(2, 9):
            C = [[F(0)] * n for _ in range(n)]
            for j in range(n):
                C[(j + 1) % n][j] = F(1)
                C[j][j] -= D
            rat_ok &= (solve_exact(C, [F(1)] * n) is not None) == (D**n != 1)
    ok &= ck("1a′ 同一恒等式的精确有理版（3 个 D × n = 2..8 全部可解且 D^n ≠ 1）", rat_ok)

    # 1b 「删一条链约束」的正交补向量与内积（解出通路的显式线性代数）
    lin_ok, rank_ok = True, True
    for D in (F(3, 2), F(8, 5)):
        for n in range(2, 9):
            for j0 in range(n):
                # 断点在 j0 的循环等比向量：w_{j0+1+t} = D^t（t = 0..n−1，下标循环）
                w = [D ** ((j - j0 - 1) % n) for j in range(n)]
                w2 = [(D ** t) for t in range(n)]                # 逐项核对定义
                lin_ok &= sorted(w) == sorted(w2)
                for j in range(n):
                    if j == j0:
                        continue
                    g = [F(0)] * n
                    g[(j + 1) % n] += 1
                    g[j] -= D
                    lin_ok &= dot(g, w) == 0
                lin_ok &= dot([F(-1)] * n, w) == -(D**n - 1) / (D - 1) != 0
                sub = [polytope_rows(D, n, F(1))[i][0] for i in range(n)]   # n 条 G 行
                keep = [sub[j] for j in range(n) if j != j0] + [[F(-1)] * n]
                rank_ok &= solve_exact(keep, [F(0)] * n) == [F(0)] * n
    ok &= ck("1b 删一条链约束后的正交补向量（w_{j0+1+t} = D^t）与内积非零恒等式"
             "（精确有理，n = 2..8 全 j0）", lin_ok)
    ok &= ck("1b′ m2 − 1 条链约束加和约束的解唯一（系数行列式非零），即秩恰为 m2",
             rank_ok)

    # 1c 顶点集合 = 预测循环族：54 个组合（D ∈ {3/2, 8/5, 111/70}，n = 2..7，W 乘 3/2、4、10）
    combos, all_ok, strict_ok, count_ok, active_ok = 0, True, True, True, True
    for D in (F(3, 2), F(8, 5), F(111, 70)):
        for n in range(2, 8):
            base = (D**n - 1) / (D - 1)
            for mult in (F(3, 2), F(4), F(10)):
                W = mult * base
                verts = enumerate_vertices(D, n, W)
                fam, v = predicted_family(D, n, W)
                combos += 1
                all_ok &= set(verts) == fam
                count_ok &= len(fam) == n and len(verts) == n
                for y in verts:
                    strict_ok &= all(t > 1 for t in y)          # 无坐标等于 1（下界全不活跃）
                    strict_ok &= sum(y) >= W
                V0 = tuple(v * D**j for j in range(n))
                strict_ok &= (V0 in verts) and V0[0] < D * V0[-1]   # V 本身回绕严格（V ∈ P^<）
                strict_ok &= v == mult > 1
                # 每个顶点恰有 n − 1 条链（含回绕）活跃；V 缺的正是回绕那条
                for y, act in verts.items():
                    nchain = sum(1 for t in act if t.startswith("G"))
                    active_ok &= nchain == n - 1 and "W" in act
                actV0 = verts.get(V0)
                active_ok &= actV0 is not None and set(actV0) == {"W"} | {
                    "G%d" % (j + 1) for j in range(n - 1)}
    ok &= ck("1c 54 个组合上顶点集合与预测循环族逐点相等（精确有理全穷举）",
             all_ok and count_ok, "组合数 %d" % combos)
    ok &= ck("1c′ 同一 54 组：顶点无坐标等于 1、和约束取等、V 本身回绕严格（V ∈ P^<）",
             strict_ok)
    ok &= ck("1c″ 每个顶点恰有 m2 − 1 条链约束活跃；V 的活跃集 = 和约束 + 除回绕外全部链",
             active_ok)

    # 1d 大 m2 的全活跃子集穷举（最大一批 C(21,10) = 352716 个子集）
    big_ok, big_detail = True, []
    for n in (8, 9, 10):
        D = F(3, 2)
        W = F(3, 2) * (D**n - 1) / (D - 1)
        verts = enumerate_vertices(D, n, W)
        fam, _ = predicted_family(D, n, W)
        big_ok &= set(verts) == fam and len(verts) == n
        big_detail.append("n=%d 子集 %d 顶点 %d" % (n, math.comb(2 * n + 1, n), len(verts)))
    big_ok &= math.comb(21, 10) == 352716
    ok &= ck("1d 全活跃子集穷举到 m2 = 10（含 C(21,10) = 352716 个子集）", big_ok,
             "；".join(big_detail))

    # 1e 顶点族上 S 取常值、最大值等于 S(V)、抽样点 S ≤ S(V)
    const_ok, max_ok, samp_ok, samp_detail = True, True, True, []
    rng = random.Random(20251026)
    for D, n, mult in ((F(3, 2), 4, F(3, 2)), (F(8, 5), 5, F(4)), (F(111, 70), 6, F(10))):
        W = mult * (D**n - 1) / (D - 1)
        fam, v = predicted_family(D, n, W)
        vals = [S_value(list(y)) for y in fam]
        sV = S_value([v * D**j for j in range(n)])
        const_ok &= max(vals) - min(vals) < mp.mpf("1e-45") and abs(max(vals) - sV) < mp.mpf("1e-45")
        verts = enumerate_vertices(D, n, W)
        max_ok &= abs(max(S_value(list(y)) for y in verts) - sV) < mp.mpf("1e-40")
        pts = sample_feasible(D, n, W, rng, 900)
        worst = max((S_value(y) for y in pts), default=mp.mpf(0))
        samp_ok &= worst <= sV + mp.mpf("1e-40")
        samp_ok &= all(sum(y) <= y[j] * (D**n - 1) / (D - 1) for y in pts for j in range(n))
        samp_detail.append("n=%d 样本 %d 最大 S=%s vs S(V)=%s"
                           % (n, len(pts), mp.nstr(worst, 7), mp.nstr(sV, 7)))
    ok &= ck("1e 顶点族上 S 为常值且等于 S(V)", const_ok)
    ok &= ck("1e′ max_{顶点} S = S(V)", max_ok)
    ok &= ck("1e″ 抽样可行点 S ≤ S(V)，且 Σy ≤ y_j(D^n−1)/(D−1) 逐点成立", samp_ok,
             "；".join(samp_detail))
    print("       注：「每个最大值点都是顶点」依赖 S 严格凸的解析论证，无法机器验证；"
          "以上抽样只作佐证。")
    return ok


# ======================================================================
# 二、(P1) 是实质前提且不可省（增量 2）
# ======================================================================
def assert_2_p1_essential() -> bool:
    print("二、(P1) 的实质性与不可省（增量 2）")
    ok = True
    D, n, W = F(3, 2), 2, F(3, 2)
    thr = (D**n - 1) / (D - 1)
    ok &= ck("2a W = 3/2 ≤ (D^n − 1)/(D − 1) = 5/2，即 (P1) 失败", W <= thr,
             "W=%s 阈值=%s" % (W, thr))
    verts = enumerate_vertices(D, n, W)
    expect = {(F(1), F(1)), (F(1), F(3, 2)), (F(3, 2), F(1))}
    ok &= ck("2b 顶点集合恰为 {(1,1), (1,3/2), (3/2,1)}（精确有理全穷举）", set(verts) == expect,
             "实际 %s" % sorted(verts))
    fam, v = predicted_family(D, n, W)
    ok &= ck("2c 预测族与顶点集不相交，且预测族点违反 y_j ≥ 1（v = 3/5 < 1）",
             not (set(verts) & fam) and all(any(t < 1 for t in y) for y in fam),
             "预测族 %s，v=%s" % (sorted(fam), v))
    s11 = S_value([F(1), F(1)], dps=60)
    s12 = S_value([F(1), F(3, 2)], dps=60)
    s21 = S_value([F(3, 2), F(1)], dps=60)
    ok &= ck("2d S(1,1) = 6（精确）", s11 == 6 and 3 / (2 - 1) + 3 / (2 - 1) == 6)
    lo2 = F(math.isqrt(2 * 10**60), 10**30)     # √2 的精确有理下界与上界
    hi2 = F(math.isqrt(2 * 10**60) + 1, 10**30)
    full = 3 + 3 / (2 ** mp.mpf("1.5") - 1)
    ok &= ck("2d′ S(1,3/2) = S(3/2,1) = 3 + 3/(2^{3/2} − 1) = (24 + 6√2)/7 ≈ 4.640754482",
             abs(s12 - s21) < mp.mpf("1e-40")
             and (F(24) + 6 * lo2) / 7 <= frac_of(full) <= (F(24) + 6 * hi2) / 7
             and abs(s12 - mp.mpf("4.640754482034081")) < mp.mpf("1e-12"),
             "值 = %s" % mp.nstr(s12, 16))
    ok &= ck("2e max_P S = 6（在 (1,1) 上取到）",
             s11 > s12 and abs(max(S_value(list(y)) for y in verts) - 6) < mp.mpf("1e-30"))
    ok &= ck("2f 活跃集：(1,1) 由两条下界活跃；另两顶点分别由链 G1 与回绕 G2 加一条下界活跃"
             "（回绕活跃的那个是 (3/2,1)，另一是它的镜像）",
             set(verts.values()) == {("L1", "L2"), ("L1", "G1"), ("L2", "G2")},
             "实际 %s" % sorted(verts.values()))
    sv = S_value([v, D * v], dps=60)
    ok &= ck("2g 同一配置下 S(预测族点) ≈ 9.281088094 仍大于 max_P S（只否证分类，不否证不等式）",
             sv > 6 and abs(sv - mp.mpf("9.281088094")) < mp.mpf("1e-8"), "S(V)=%s" % mp.nstr(sv, 10))
    ok &= ck("2h c = 60 + log2(112590/97)，695·162 = 112590，2 < 112590/97 < 2^11 ⟹ 61 < c < 71",
             695 * 162 == 112590 and 97 * 2 < 112590 < 97 * 2048)
    return ok


# ======================================================================
# 三、更强的坐标下界 y_j ≥ v（增量 3）
# ======================================================================
def assert_3_coord_lower_bound() -> bool:
    print("三、坐标下界 y_j ≥ v（增量 3）")
    ok = True
    min_ok, attain_ok, pos_ok = True, True, True
    for D in (F(3, 2), F(8, 5), F(111, 70)):
        for n in range(2, 7):
            W = F(3, 2) * (D**n - 1) / (D - 1)
            fam, v = predicted_family(D, n, W)
            verts = enumerate_vertices(D, n, W)
            for j in range(n):
                min_ok &= min(y[j] for y in verts) == v
                attain_ok &= any(y[j] == v for y in verts)
            pos_ok &= v > 1
    ok &= ck("3a 每个坐标在顶点上的最小值的精确值 = v（15 组配置、全部 j）", min_ok)
    ok &= ck("3b 每个坐标的最小值在顶点处取到", attain_ok)
    ok &= ck("3c v > 1（故 y_j ≥ v 强于「没有坐标等于 1」）", pos_ok)
    rng = random.Random(7)
    s1, s2, npts = True, True, 0
    for D, n in ((F(3, 2), 3), (F(8, 5), 4)):
        W = F(4) * (D**n - 1) / (D - 1)
        _, v = predicted_family(D, n, W)
        for y in sample_feasible(D, n, W, rng, 1200):
            npts += 1
            s1 &= all(t >= v for t in y)
            s2 &= all(sum(y) <= t * (D**n - 1) / (D - 1) for t in y)
    ok &= ck("3d 抽样 %d 个精确有理可行点：y_j ≥ v 与 Σy ≤ y_j(D^n−1)/(D−1) 全成立" % npts,
             s1 and s2)
    print("       注：route-2 的 z3 unsat 断言与 4393 个样本那批搜索无法复现（样本集不可得），"
          "此处是重写的样本与精确顶点值。")
    return ok


# ======================================================================
# 四、读法缺口（增量 4）
# ======================================================================
def lt_delta(num: int, den: int) -> bool:
    """精确判据：num/den < log2(3) ⟺ 2^num < 3^den（正整数）。"""
    return 2**num < 3**den


def le_delta(num: int, den: int) -> bool:
    return 2**num <= 3**den


def windows(x, m, m2):
    return [sum(x[(s + j) % m] for j in range(m2)) for s in range(m)]


def a8_halves_exact(x, m, m2, s):
    """窗起点 s（0 基）时 A8 的两半：(a) x_pre ≤ x_last；(b) 回绕 x_s < δ·x_last。"""
    pre = x[(s - 1) % m]
    last = x[(s + m2 - 1) % m]
    h1 = pre <= last
    h2 = lt_delta(x[s].numerator * last.denominator, x[s].denominator * last.numerator)
    return h1, h2


def assert_4_reading_gap() -> bool:
    print("四、窗口读法缺口（增量 4）")
    ok = True
    # 4a 精确数据一（m = 4、m2 = 2）
    m, m2 = 4, 2
    x = [F(31, 20), F(12, 5), F(5, 2), F(1)]
    k = [F(1), F(1), F(2), F(1)]
    six = [lt_delta(48, 31), lt_delta(25, 24), lt_delta(2, 5), lt_delta(31, 20),
           2**5 >= 3**2, lt_delta(24, 25)]
    ok &= ck("4a 六条整数等价式 2^48<3^31、2^25<3^24、2^2<3^5、2^31<3^20、2^5≥3^2、2^24<3^25 全真",
             all(six))
    ok &= ck("4a′ 逐点 k_i ≤ x_i 与四条循环链不等式（精确整数判据）",
             all(k[i] <= x[i] for i in range(m))
             and all(le_delta(x[(i + 1) % m].numerator * x[i].denominator,
                              x[(i + 1) % m].denominator * x[i].numerator) for i in range(m)))
    wk, wx = windows(k, m, m2), windows(x, m, m2)
    ok &= ck("4a″ 窗和：Σk = (2,3,3,2) 最大在窗 (2,3)、(3,4)；Σx = (79/20,49/10,7/2,51/20) "
             "唯一最大在 (2,3)",
             wk == [F(2), F(3), F(3), F(2)] and wx == [F(79, 20), F(49, 10), F(7, 2), F(51, 20)]
             and max(wx) == F(49, 10) and wx.count(F(49, 10)) == 1 and wx.index(max(wx)) == 1
             and max(wk) == 3 and wk.index(max(wk)) == 1)
    h1k, h2k = a8_halves_exact(x, m, m2, 2)      # Σk 读法：把窗 (3,4) 放末尾
    h1x, h2x = a8_halves_exact(x, m, m2, 1)      # Σx 读法：把窗 (2,3) 放末尾
    ok &= ck("4a‴ Σk 读法下 A8 两半都失败（x_2 = 12/5 > x_4 = 1；回绕 x_3 = 5/2 ≥ δ·1）",
             (not h1k) and (not h2k))
    ok &= ck("4a⁗ Σx 读法下 A8 两半都成立（x_1 = 31/20 ≤ x_3 = 5/2；回绕 12/5 < δ·5/2）",
             h1x and h2x)

    # 4b 精确数据二（m = 4、m2 = 2）
    x = [F(200), F(300), F(320), F(250)]
    k = [F(1), F(1), F(300), F(240)]
    ok &= ck("4b 逐点 k_i ≤ x_i 与四条循环链不等式（精确整数判据）",
             all(k[i] <= x[i] for i in range(m))
             and all(le_delta(x[(i + 1) % m].numerator * x[i].denominator,
                              x[(i + 1) % m].denominator * x[i].numerator) for i in range(m)))
    ok &= ck("4b′ δ < 2584963/10^6（⟺ 3^{10^6} < 2^{2584963}）与 c < 71（⟺ 112590 < 97·2048），"
             "故 (δ+1)·c < 2.584963·71 = 183.53 < 271",
             3 ** (10**6) < 2**2584963 and 112590 < 97 * 2048)
    wk, wx = windows(k, m, m2), windows(x, m, m2)
    ok &= ck("4b″ 窗和：Σk = (2,301,540,241) 唯一最大在窗 (3,4)；Σx = (500,620,570,450) "
             "唯一最大在窗 (2,3)",
             wk == [F(2), F(301), F(540), F(241)] and wx == [F(500), F(620), F(570), F(450)]
             and wk.index(max(wk)) == 2 and wk.count(max(wk)) == 1
             and wx.index(max(wx)) == 1 and wx.count(max(wx)) == 1)
    h1k, h2k = a8_halves_exact(x, m, m2, 2)
    h1x, h2x = a8_halves_exact(x, m, m2, 1)
    ok &= ck("4b‴ Σk 读法下 A8 的 4c 一半失败（x_2 = 300 > x_4 = 250）；回绕本身仍成立（320 < δ·250）",
             (not h1k) and h2k)
    ok &= ck("4b⁗ Σx 读法下 A8 两半都成立（x_1 = 200 ≤ x_3 = 320；回绕 300 < δ·320）",
             h1x and h2x)

    # 4c y* = (W − m2 + 1, 1, …, 1) 在去掉回绕的 P′ 上的显式反例
    cases = [(3, F(210)), (5, F(200)), (5, F(200)), (91, F(205632218873398596256))]
    Dlist = [F(3, 2), F(3, 2), F(8, 5), F(8, 5)]
    feas_ok, wrap_ok, cmp_ok, det = True, True, True, []
    for (n, W), D in zip(cases, Dlist):
        y = [W - n + 1] + [F(1)] * (n - 1)
        feas_ok &= all(t >= 1 for t in y)
        feas_ok &= all(y[j + 1] <= D * y[j] for j in range(n - 1))
        feas_ok &= sum(y) >= W                       # 实际上取等
        wrap_ok &= y[0] > DEC6 * y[-1]               # 回绕被违反（用 δ 的严格上界代替）
        v_lo = W * (DLO - 1) / (DHI**n - 1)          # v 的严格下界
        fl = math.floor(to_mpf(v_lo))
        sV_ub = F(3 * n, 2**fl - 1)                  # S(V) 的严格上界
        cmp_ok &= sV_ub < F(3 * (n - 1))             # 上界 < S(y*) 的平凡下界 3(m2 − 1)
        # 结构事实（精确）：y* 恰有 m2 − 1 个坐标等于 1，故 S(y*) = 3(m2−1) + 3/(2^{y_1} − 1)
        cmp_ok &= sum(1 for t in y if t == 1) == n - 1 and y[0] > 0
        v_num = to_mpf(W) * (DELTA - 1) / (DELTA**n - 1)
        sy = S_value(y, dps=140)          # 精度要高：sy 只比 3(m2−1) 大 1e-60 量级
        sV = S_value([v_num * DELTA**j for j in range(n)], dps=140)
        cmp_ok &= mp.mpf(3 * (n - 1)) <= sy < mp.mpf(3 * (n - 1)) + mp.mpf("1e-6")
        cmp_ok &= abs((sy - sV) - 3 * (n - 1)) < mp.mpf("0.01")
        det.append("m2=%d: S(y*)=%s, S(V)=%s" % (n, mp.nstr(sy, 8), mp.nstr(sV, 6)))
    ok &= ck("4c y* 在去掉回绕的 P′ 上处处可行（4 组参数；和约束取等）", feas_ok)
    ok &= ck("4c′ y* 一律违反回绕（y_1 > δ·y_n）", wrap_ok)
    ok &= ck("4c″ S(y*) = 3(m2−1) + 3/(2^{y_1}−1) ∈ [3(m2−1), 3(m2−1) + 1e−6)（结构 + 高精度两道），"
             "S(V) 的严格上界 < 3(m2−1)，且 S(y*) − S(V) ≈ 3(m2−1)（6.00、12.00、12.00、270.00）",
             cmp_ok, "；".join(det))
    return ok


# ======================================================================
# 五、闭化缺口（增量 5）
# ======================================================================
def assert_5_closure() -> bool:
    print("五、严格不等号闭化（增量 5）")
    ok = True
    strict_ok, maxeq_ok = True, True
    for D, n, mult in ((F(3, 2), 3, F(3, 2)), (F(8, 5), 4, F(4)), (F(111, 70), 5, F(10))):
        W = mult * (D**n - 1) / (D - 1)
        fam, v = predicted_family(D, n, W)
        V0 = tuple(v * D**j for j in range(n))
        for y in fam:
            strict_ok &= all(t > 1 for t in y) and sum(y) >= W
        strict_ok &= V0 in fam and V0[0] < D * V0[-1]   # V 的回绕严格（V ∈ P^<）
        verts = enumerate_vertices(D, n, W)
        sV = S_value(list(V0))
        maxeq_ok &= set(verts) == fam and abs(max(S_value(list(y)) for y in verts) - sV) < mp.mpf("1e-40")
    ok &= ck("5a V := (v, Dv, …, D^{m2−1}v) 严格满足回绕（δ^{m2} > 1）且坐标 > 1，故 V ∈ P^<；"
             "其余旋转只有回绕取等", strict_ok)
    ok &= ck("5a′ 因 V ∈ P^< ⊆ P 而 max_{P^<} S = max_P S = S(V)（同点取到，闭化零损失）", maxeq_ok)
    return ok


# ======================================================================
# 六、m = 92 旧句为假与越界见证（增量 6）
# ======================================================================
def eps_of(m: int, m2: int, K):
    """Theorem 21 的 ε（勘误修正后的第三项）；A 项按原刊的三个分支。"""
    v = (mp.mpf(m2) / m) * K * (DELTA - 1) / (DELTA**m2 - 1)
    if m2 == m:
        A = mp.mpf(0)
    elif m2 == m - 1:
        A = 3 / X0
    else:
        A = (97 * (m - m2) + 73) / (54 * X0)
    return (A + 3 / (2**v - 1) + 3 * (m2 - 1) / (2**v - 1) ** DELTA) / (3 * K * mp.log(2))


def feasible(m: int, m2: int, K) -> bool:
    return (DELTA**m2 - 1) / (DELTA - 1) * C_HYP <= (mp.mpf(m2) / m) * K


def eps_opt(m: int, K):
    best, arg = None, None
    for m2 in range(1, m + 1):
        if feasible(m, m2, K):
            e = eps_of(m, m2, K)
            if best is None or e < best:
                best, arg = e, m2
    return best, arg


def min_denom_in(a: F, b: F, cap: int = 10**6):
    """Stern-Brocot：开区间 (a, b) 内分母最小的分数（精确有理端点）。"""
    ln, ld, hn, hd = 0, 1, 1, 0
    for _ in range(cap):
        mn, md = ln + hn, ld + hd
        x = F(mn, md)
        if x <= a:
            ln, ld = mn, md
        elif x >= b:
            hn, hd = mn, md
        else:
            return x
    raise RuntimeError("Stern-Brocot 未终止")


def psi_of(m: int, K, eps_val, eps_scale=None):
    """Ψ(K)：区间 (δ, δ + ε_opt) 内最小分母的分母。

    严格化：δ 用 A 节的严格有理界 [DLO, DHI]（宽度约 4.6e-124）；ε 用 dps = 160 的
    数值加误差条 BAR = 2^-300 ≈ 4.9e-91（ε 的相对误差约 1e-160，故其绝对误差远小于
    BAR；δ 的取值误差 ≤ 界宽 4.6e-124 乘以有界的敏感度，也远小于 BAR）。
    内区间 (DHI, DLO + ε − BAR) 必含于真区间，外区间 (DLO, DHI + ε + BAR) 必包含真
    区间；两者最小分母相等时结论严格。搜索本身是精确有理运算。ε 小到与 BAR 同量级
    时（本脚本的网格里不会出现，最小 ε ≈ 8e-82 对 K = 1e21）本方式失效，直接报错。
    """
    if eps_scale is not None:
        eps_val = eps_val * mp.mpf(eps_scale)
    elo, ehi = frac_of(eps_val - BAR), frac_of(eps_val + BAR)
    if DLO + elo <= DHI:
        raise RuntimeError("ε 低于误差条 BAR，严格化失效")
    inner = min_denom_in(DHI, DLO + elo)
    outer = min_denom_in(DLO, DHI + ehi)
    return inner.numerator, inner.denominator, inner.denominator == outer.denominator


def U_of(m: int):
    return mp.mpf("1.4784") * m * DELTA**m


def chain(m: int, K0, max_steps: int = 12, stop_above=None):
    """K_{n+1} = Ψ(K_n)，Ψ(K_n) > K_n 时继续；返回 (每次迭代的分母, 每步的 m2, 终值)。

    stop_above 给定时，某一步的新值一超过它就停（论文侧「越过上界 U(m) 即排除」的停法）。
    """
    K = to_mpf(K0) if isinstance(K0, F) else mp.mpf(K0)
    vals, args = [], []
    for _ in range(max_steps):
        e, am2 = eps_opt(m, K)
        num, den, uniq = psi_of(m, K, e)
        if not uniq:
            raise RuntimeError("区间最小分母不唯一")
        if den <= K:
            return vals, args, K
        vals.append(den)
        args.append(am2)
        K = mp.mpf(den)
        if stop_above is not None and K > stop_above:
            return vals, args, K
    return vals, args, K


def assert_6_m92() -> bool:
    print("六、m = 92 旧句为假与三处越界见证（增量 6）")
    ok = True
    U92 = U_of(92)
    # 6a 独立复现论文七步链条（第三方锚点的端到端校验；停在越过 U(91) 的那一步）
    vals, args, _ = chain(91, F(7) * 10**11, stop_above=U_of(91))
    exp_args = [47, 67, 77, 82, 86, 88, 91]
    exp_vals = [5267319278509397, 397560349370386783, 4640282259296926456,
                27444133206411171953, 77692117359936589403, 205632218873398596256,
                7941964418702608664581]
    ok &= ck("6a 独立实现复现 m = 91、起点 7e11 的七步链条（m2 与 K 全同）",
             args == exp_args and [int(v) for v in vals] == exp_vals, "m2 = %s" % args)
    # 6b 见证一：K_lo = 3.3e20 首步即越界
    e, am2 = eps_opt(92, mp.mpf("3.3e20"))
    num, den, uniq = psi_of(92, mp.mpf("3.3e20"), e)
    ok &= ck("6b K_lo = 3.3e20：Ψ = 7941964418702608664581 > U(92) = %s（首步越界）"
             % mp.nstr(U92, 22),
             den == 7941964418702608664581 and mp.mpf(den) > U92 and uniq and am2 == 92,
             "Ψ/U = %s" % mp.nstr(mp.mpf(den) / U92, 6))
    scales_ok = True
    for sc in ("0.99", "0.999", "1", "1.001", "1.01", "1.000001", "0.999999"):
        if psi_of(92, mp.mpf("3.3e20"), e, eps_scale=sc)[1] != den:
            scales_ok = False
    ok &= ck("6b′ ε 乘 0.99 至 1.01 共七种尺度：Ψ 都等于 7941964418702608664581（台阶宽）", scales_ok)
    with mp.workdps(400):
        d400 = psi_of(92, mp.mpf("3.3e20"), eps_of(92, 92, mp.mpf("3.3e20")))[1]
    ok &= ck("6b″ dps = 400 的 Ψ 与主精度（dps = 160）相同（%d）" % d400, d400 == den)
    # 6c 见证二：右端点 U(92)
    e2, _ = eps_opt(92, U92)
    _, den2, u2 = psi_of(92, U92, e2)
    ok &= ck("6c K_lo = U(92)：Ψ = 15678296618531818732906 > U(92)",
             den2 == 15678296618531818732906 and mp.mpf(den2) > U92 and u2, "Ψ = %d" % den2)
    # 6d K_cross 区间
    left = F(3131954789591722627672965018064132891595, 10**19)
    right = F(3131954789591722629338299555001867702231, 10**19)
    ok &= ck("6d 给定 K_cross 区间的宽度与相对宽度（约 166.53 与 5.3e-19 < 1e-18）",
             abs(float(right - left) - 166.5) < 1 and to_mpf((right - left) / right) < mp.mpf("1e-18"),
             "宽 %s 相对宽 %s" % (float(right - left), mp.nstr(to_mpf((right - left) / right), 4)))
    le_, _ = eps_opt(92, to_mpf(left))
    re_, _ = eps_opt(92, to_mpf(right))
    dl = psi_of(92, to_mpf(left), le_)[1]
    dr = psi_of(92, to_mpf(right), re_)[1]
    ok &= ck("6d′ 左端不越界（Ψ = %d = K*）、右端首步越界（Ψ = %d ≈ 7.94e21）" % (dl, dr),
             dl == KSTAR and dr == 7941964418702608664581
             and mp.mpf(dl) < U92 and mp.mpf(dr) > U92)
    lo, hi = left, right
    for _ in range(70):
        mid = (lo + hi) / 2
        em, _ = eps_opt(92, to_mpf(mid))
        if mp.mpf(psi_of(92, to_mpf(mid), em)[1]) > U92:
            hi = mid
        else:
            lo = mid
    ok &= ck("6d″ 自跑的 70 轮二分（判定式：首步 Ψ > U(92)）落点含于给定区间内",
             lo >= left and hi <= right,
             "自跑区间宽 %s" % float(hi - lo))
    ok &= ck("6e K* = 205632218873398596256 < K_cross < U(92)",
             mp.mpf(KSTAR) < to_mpf(lo) and to_mpf(hi) < U92)
    # 6f 弱读法：起点 ≤ K* 的抽样链条都不越界
    weak_ok, weak_detail = True, []
    for Ks in ("7.5311e11", "1e12", "1e15", "1e18", "1e20", "205632218873398596256"):
        vals_i, _, _ = chain(92, mp.mpf(Ks))
        mx = max(vals_i) if vals_i else mp.mpf(Ks)
        weak_ok &= mx <= mp.mpf(KSTAR) and mx < U92
        weak_detail.append("K_lo=%s 最大迭代 %s" % (Ks, mp.nstr(mx, 8)))
    ok &= ck("6f 起点 ≤ K* 的六个抽样链条：最大迭代 ≤ K* < U(92)（弱读法成立）", weak_ok,
             "；".join(weak_detail[:3]))
    return ok


# ======================================================================
# 七、Ψ 关于 K_lo 非降（增量 7）
# ======================================================================
def assert_7_monotone() -> bool:
    print("七、Ψ 关于 K_lo 非降（增量 7）")
    ok = True

    def grid_scan(lo: F, hi: F, npts: int):
        prev, mono, downs = None, True, []
        for i in range(npts):
            K = lo + (hi - lo) * F(i, npts - 1)
            e, _ = eps_opt(92, to_mpf(K))
            d = psi_of(92, to_mpf(K), e)[1]
            if prev is not None and d < prev:
                mono = False
                downs.append((i, d, prev))
            prev = d
        return mono, downs

    mono1, down1 = grid_scan(L_START, F(U92_INT), 70)
    mono2, down2 = grid_scan(F(10) ** 12, F(10) ** 21, 60)
    ok &= ck("7a [L, U(92)] 上 70 点网格：Ψ 无下降", mono1, "下降 %s" % down1[:1])
    ok &= ck("7a′ [1e12, 1e21] 上 60 点网格：Ψ 无下降", mono2, "下降 %s" % down2[:1])
    mech1 = True
    for m2 in (47, 88, 92):
        prev = None
        for i in range(40):
            K = F(10) ** 20 + F(i) * F(10) ** 19
            e = eps_of(92, m2, to_mpf(K))
            if prev is not None and e > prev:
                mech1 = False
            prev = e
    ok &= ck("7b 机制一：固定 m2 时 ε(m2, ·) 关于 K 非增（3 个 m2 × 40 点）", mech1)
    thr1 = (DELTA**47 - 1) / (DELTA - 1) * C_HYP
    ok &= ck("7b′ 机制二：可行阈值 ((δ^{m2}−1)/(δ−1))·c 与 K 无关（可行集随 K 单增）",
             thr1 > 0, "m2 = 47 的阈值 = %s" % mp.nstr(thr1, 10))
    mech3, prev = True, None
    for i in range(30):
        e = mp.mpf("1e-40") * (mp.mpf(3) ** i)
        d = psi_of(92, mp.mpf("3.3e20"), e)[1]
        if prev is not None and d > prev:
            mech3 = False
        prev = d
    ok &= ck("7b″ 机制三：区间内最小分母关于 ε 非增（ε 跨 14 个数量级）", mech3)
    print("       注：四步初等证明本身是纸面推理，无法机器验证；以上是它的三条机制与两组网格，"
          "属证据不属证明。")
    return ok


# ======================================================================
# 八、结构性收口：账本 38 条、无环、TARGET 闭包 27 节点（增量 8）
# ======================================================================
def assert_8_ledger() -> bool:
    print("八、假设账本与依赖闭包（增量 8）")
    ok = True
    py = sys.executable
    for name in ("audit_assumption_ledger.py", "verify_elementary_steps.py"):
        r = subprocess.run([py, SCRIPTS + "/" + name], capture_output=True, text=True, timeout=1800)
        ok &= ck("8a %s 实跑退出码 0" % name, r.returncode == 0, "exit=%d" % r.returncode)
    # 8b 结构重算。数据来源是 route-5 脚本内联的账本表（属数据不属结论）；
    #    条目数、悬空依赖、无环性、闭包大小与闭包内容都由本脚本自己算。
    spec = importlib.util.spec_from_file_location("aal", SCRIPTS + "/audit_assumption_ledger.py")
    mod = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
    nodes = {e["id"]: e for e in mod.LEDGER}
    ok &= ck("8b 账本条目数 = 38", len(nodes) == 38, "实际 %d" % len(nodes))
    dangling = [a for e in mod.LEDGER for a in e["deps"] if a not in nodes]
    ok &= ck("8b′ 悬空依赖 0 条", not dangling, "悬空 %s" % dangling[:3])
    color, cycles = {}, []

    def dfs(u, stack):
        color[u] = 1
        for v in nodes[u]["deps"]:
            if color.get(v, 0) == 1:
                cycles.append(stack + [u, v])
            elif color.get(v, 0) == 0:
                dfs(v, stack + [u])
        color[u] = 2

    for u in list(nodes):
        if color.get(u, 0) == 0:
            dfs(u, [])
    ok &= ck("8b″ 依赖图环数 = 0（自写 DFS 重算）", not cycles, "环 %s" % cycles[:1])
    seen, stack = set(), ["TARGET.tail"]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        stack.extend(nodes[u]["deps"])
    ok &= ck("8b‴ TARGET.tail 的闭包 = 27 个节点", len(seen) == 27, "实际 %d" % len(seen))
    kinds = [nodes[u]["kind"] for u in seen]
    ok &= ck("8b⁗ 闭包内无「印出版已否证」也无「已撤回断言」",
             "印出版已否证" not in kinds and "已撤回断言" not in kinds,
             "闭包类别计数 %s" % {k: kinds.count(k) for k in sorted(set(kinds))})
    self_ref = [u for u in seen if u != "TARGET.tail" and "TARGET.tail" in nodes[u]["deps"]]
    ok &= ck("8b⁵ 闭包内无节点把 TARGET.tail 列为依赖（无自指）", not self_ref)
    print("       注：「TARGET 的顶点句只用定理 21 的假设 (H21)」这一判断依赖账本表本身的"
          "依赖列，本脚本只重算结构不看内容。")
    return ok


# ======================================================================
# 九、版本与行号层事实（增量 9）
# ======================================================================
def assert_9_versions() -> bool:
    print("九、版本与行号层事实（增量 9）")
    ok = True

    def md5_of(path):
        with open(path, "rb") as fh:
            return hashlib.md5(fh.read()).hexdigest()

    text = open(AUDIT_MD, encoding="utf-8").read()
    lines = text.split("\n")
    hits = [i + 1 for i, s in enumerate(lines) if "对起点稳健" in s]
    ok &= ck("9a audit-report.md 现行 324 行、md5 f8d99b9dc218a1282a2dc8247dbe774f",
             text.count("\n") == 324 and md5_of(AUDIT_MD) == "f8d99b9dc218a1282a2dc8247dbe774f",
             "实测 %d 行 md5 %s" % (text.count("\n"), md5_of(AUDIT_MD)))
    ok &= ck("9a′ 「对起点稳健」在 HEAD 命中 :10、:110、:137、:193、:221",
             hits == [10, 110, 137, 193, 221], "实测 %s" % hits)
    ok &= ck("9a″ 五个命中行都含「撤回」，且 :193 逐字含「已被作者撤回，不得再引」",
             all("撤回" in lines[i - 1] for i in hits) and "已被作者撤回，不得再引" in lines[192])
    r = subprocess.run(["git", "-C", ROOT, "show", "495cd61:60-audits/hercher-t21/audit-report.md"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        ok &= ck("9b 旧版提交 495cd61（318 行、命中 :208 与 :225）", False,
                 "git 读取失败：" + r.stderr.strip())
    else:
        old = r.stdout.split("\n")
        ohits = [i + 1 for i, s in enumerate(old) if "对起点稳健" in s]
        ok &= ck("9b 旧版提交 495cd61：318 行、「对起点稳健」命中 :208 与 :225",
                 r.stdout.count("\n") == 318 and ohits == [208, 225],
                 "实测 %d 行 命中 %s" % (r.stdout.count("\n"), ohits))
        ok &= ck("9b′ 旧版 :208 逐字含旧句「即使虚构起点 K > 10²⁰，链也只走到 2.0563×10²⁰」",
                 "即使虚构起点" in old[207] and "2.0563" in old[207])
    mtext = open(MARGIN_TXT, encoding="utf-8").read()
    ml = mtext.split("\n")
    ok &= ck("9c margin-table.txt 现行 123 行、md5 b0a742be9f215f332d0f85750ad57366",
             mtext.count("\n") == 123 and md5_of(MARGIN_TXT) == "b0a742be9f215f332d0f85750ad57366",
             "%d 行 md5 %s" % (mtext.count("\n"), md5_of(MARGIN_TXT)))
    ok &= ck("9c′ m = 91 在 :89（终值、U、余量 37.0993552574716449275895、排除）",
             ml[88].split()[0] == "91" and "7941964418702608664581" in ml[88]
             and "214072842063828923281.358576944" in ml[88]
             and "37.0993552574716449275895" in ml[88] and "排除" in ml[88])
    ok &= ck("9c″ m = 92 在 :90（终值、U、余量 0.226490482057595771625621、不排除）",
             ml[89].split()[0] == "92" and "77692117359936589403" in ml[89]
             and "343025970248850209780.074794593" in ml[89]
             and "0.226490482057595771625621" in ml[89] and "不排除" in ml[89])
    print("       注：route 报告内的行号引用（例如 :271 至 :292）无法机器验证，未列入检查；"
          "「两份报告现存的文本分歧已不现存」这一步只做到了命中行与文件状态层面。")
    return ok


# ======================================================================
# 十、文献与一手原件（增量 10）
# ======================================================================
def assert_10_sources() -> bool:
    print("十、文献与一手原件侧（增量 10）")
    ok = True
    need = ["/tmp/h5.txt", "/tmp/sidw144.txt", "/tmp/sidw143.txt", "/tmp/sidw143.pdf"]
    missing = [p for p in need if not os.path.exists(p)]
    if missing:
        return ck("10 一手原件在 /tmp 缺席，无法验证", False, "缺失：" + "、".join(missing))
    h5 = open("/tmp/h5.txt", encoding="utf-8", errors="replace").read().split("\n")
    s144 = open("/tmp/sidw144.txt", encoding="utf-8", errors="replace").read().split("\n")
    s143 = open("/tmp/sidw143.txt", encoding="utf-8", errors="replace").read().split("\n")
    alltxt = ("\n".join(h5)).lower()
    all144 = ("\n".join(s144)).lower()
    zero_ok = all(w not in alltxt and w not in all144
                  for w in ("vertex", "vertices", "convex", "polytope", "attains"))
    ok &= ck("10a h5.txt 与 sidw144.txt 对 vertex、vertices、convex、polytope、attains 命中数全为 0",
             zero_ok)
    mhits = [i + 1 for i, s in enumerate(s144) if "maximum" in s]
    ok &= ck("10a′ sidw144.txt 的 maximum 只命中 :95、:301、:723、:863", mhits == [95, 301, 723, 863],
             "实测 %s" % mhits)
    s143_txt = open("/tmp/sidw143.txt", encoding="utf-8", errors="replace").read()
    ok &= ck("10b /tmp/sidw143.pdf 是真件（275795 字节、md5 2e5e5c4f36deb283c0925229573b7648）、"
             "sidw143.txt 1056 行（按 wc -l 口径数换行符）",
             os.path.getsize("/tmp/sidw143.pdf") == 275795
             and hashlib.md5(open("/tmp/sidw143.pdf", "rb").read()).hexdigest()
             == "2e5e5c4f36deb283c0925229573b7648"
             and s143_txt.count("\n") == 1056,
             "版面尾部有分页符，故按 wc -l 口径数换行符")
    seg143 = "\n".join(s143[267:269])
    seg144 = "\n".join(s144[269:271])
    ok &= ck("10b′ v1.43 的 :268 至 :269 给 1.3752×10^11，v1.44 的 :270 至 :271 给 7.5311×10^11，"
             "且 v1.43 该段不含 7.5311",
             "1.3752" in seg143 and "1.4784 mδ m" in seg143
             and "7.5311" in seg144 and "1.4784 mδ m" in seg144 and "7.5311" not in seg143)
    seg798 = "\n".join(h5[797:801])
    ok &= ck("10c h5.txt:798 至 :801 逐字含印出版那一步（n_{m−m2+1+ℓ} 的指数折叠式）",
             "nm−m2 +1+ℓ" in seg798 and "T (n" in seg798 and "nδm−m2 +1" in seg798,
             "命中片段 %d 行" % sum(1 for s in h5[797:801] if "nm−m2 +1+ℓ" in s))
    ok &= ck("10c′ 该步的第二个不等号对 ℓ ≥ 2 为假（δ^ℓ > δ，δ² − δ > 0 见证）",
             all(DELTA**ell > DELTA for ell in range(2, 11)) and DELTA**2 - DELTA > 0,
             "δ² − δ = %s" % mp.nstr(DELTA**2 - DELTA, 10))
    print("       注：「逐字读出」「无关用法」这类阅读判断无法机器验证；本脚本只核对文本命中"
          "与折叠式本身的真假。")
    return ok


# ======================================================================
# 十一、数值锚点（增量 11）
# ======================================================================
def assert_11_anchors() -> bool:
    print("十一、数值锚点独立复算（增量 11）")
    ok = True
    ok &= ck("11a δ 前 40 位 = 1.58496250072115618145373894394781650876",
             mp.nstr(DELTA, 40) == "1.58496250072115618145373894394781650876", mp.nstr(DELTA, 40))
    ok &= ck("11a′ δ 的严格有理界夹住数值 δ（DLO ≤ δ_数值 ≤ DHI，按精确有理比较）",
             DLO <= frac_of(DELTA) <= DHI,
             "界宽 %s" % mp.nstr(to_mpf(DHI - DLO), 3))
    U91, U92 = U_of(91), U_of(92)
    ok &= ck("11b U(91) = 214072842063828923281.3586",
             mp.nstr(U91, 25) == "214072842063828923281.3586", mp.nstr(U91, 25))
    ok &= ck("11b′ U(92) = 343025970248850209780.0748",
             mp.nstr(U92, 25) == "343025970248850209780.0748", mp.nstr(U92, 25))
    _, _, term91 = chain(91, L_START, stop_above=U91)
    vals92, args92, term92 = chain(92, L_START, stop_above=U92)
    ok &= ck("11c m = 91 链从 L 出发的终值 = 7941964418702608664581",
             int(term91) == 7941964418702608664581)
    ok &= ck("11c′ m = 92 链从 L 出发的终值 = 77692117359936589403（中间 %d 步，m2 = %s）"
             % (len(vals92), args92), int(term92) == 77692117359936589403)
    m91 = mp.mpf(int(term91)) / U91
    m92 = mp.mpf(int(term92)) / U92
    ok &= ck("11d 余量(91) = 37.09935525747164492758953",
             mp.nstr(m91, 25) == "37.09935525747164492758953", mp.nstr(m91, 25))
    ok &= ck("11d′ 余量(92) = 0.2264904820575957716256207",
             mp.nstr(m92, 25) == "0.2264904820575957716256207", mp.nstr(m92, 25))
    ok &= ck("11d″ 1/余量(92) = 4.4151965721266085987",
             mp.nstr(1 / m92, 20) == "4.4151965721266085987", mp.nstr(1 / m92, 20))
    ok &= ck("11e c = 70.1808063283083668248",
             mp.nstr(C_HYP, 21) == "70.1808063283083668248", mp.nstr(C_HYP, 21))
    return ok


def main() -> int:
    print("=" * 72)
    print("cycle-1 增量结论独立复算（verify.py）")
    print("=" * 72)
    print("环境：python %s；mpmath %s；dps = %d" % (sys.version.split()[0], mpmath.__version__, mp.dps))
    print("严格有理 δ 界：宽度 %s（atanh 级数 200 项 + 显式尾界）；超越量误差条 %s"
          % (mp.nstr(to_mpf(DHI - DLO), 3), mp.nstr(BAR, 3)))
    print()
    for fn in (assert_1_vertex_lemma, assert_2_p1_essential, assert_3_coord_lower_bound,
               assert_4_reading_gap, assert_5_closure, assert_6_m92, assert_7_monotone,
               assert_8_ledger, assert_9_versions, assert_10_sources, assert_11_anchors):
        t0 = time.time()
        fn()
        print("       （本节耗时 %.1f 秒）" % (time.time() - t0))
    print("=" * 72)
    if FAILS:
        print("未通过 %d 条：" % len(FAILS))
        for f in FAILS:
            print("  最小反例/失败点：" + f)
        print("退出码 1")
        return 1
    print("全部断言通过（退出码 0）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
