#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-4（完备性与依赖审计）共用工具。

职责只有三件：
  1. 依赖守卫：import r2_common / r2_j 之前先比对 md5 与行数，不符即拒绝运行
     （引用纪律：learnings.md:39，行号与版本身份必须钉死）。
  2. 独立转写：按勘误约束表（corrigendum.txt:42 至 :72）自己重写一份约束表与
     可行性判据，供与 r2_common 的函数逐项对拍。
  3. 独立算术栈：用 sympy（精确有理）解方程、算秩、做小档全枚举，供与
     r2_common.solve_exact / r2_j.full_enumeration 对拍。

本文件不 import 任何项目脚本（除了守卫后加载的 r2_*），不含从项目脚本复制的函数体。
"""
import hashlib
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]           # collatz-attack/
DEPS = ROOT / "70-research" / "cycle-1" / "scripts"
EXPECT_MD5 = {
    "r2_common.py": "cfee819667c0883e73732f03d2dc8bef",
    "r2_j_independent_vertices.py": "4b8ce2a500d8ca9021fd0178deca637e",
    "r2_b_vertices.py": "4d19e2fc351cea7a3b21e487a3c02e97",
}


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def md5_of(p):
    """md5 在此仅用于与项目既有登记（materials.md 的 md5 清单）逐比特对身份，
    不承担任何安全用途；项目记录就是 md5，换算法会对不上。"""
    h = hashlib.md5()
    h.update(Path(p).read_bytes())
    return h.hexdigest()


def _in_child():
    try:
        import multiprocessing as mp
        return mp.parent_process() is not None
    except Exception:
        return False


def guard(quiet=None):
    """比对依赖文件的 md5 与行数；任何不符即退出码 2。

    子进程（spawn 出的 worker）重导入本模块时会再度执行守卫但不再打印，
    以免多核运行时刷屏；校验强度不变。"""
    if quiet is None:
        quiet = _in_child()
    bad = []
    for name, exp in EXPECT_MD5.items():
        p = DEPS / name
        cur = md5_of(p)
        n = len(Path(p).read_text(encoding="utf-8").splitlines())
        if not quiet:
            tag = "一致" if cur == exp else f"!! 与记录 {exp} 不符"
            say(f"依赖守卫：{name}  md5 {cur}  行数 {n}  {tag}")
        if cur != exp:
            bad.append(name)
    if bad:
        say("依赖守卫失败，脚本中止：", "、".join(bad))
        sys.exit(2)


def load():
    """守卫后加载依赖模块，返回 (r2_common, r2_j_independent_vertices)。"""
    guard()
    if str(DEPS) not in sys.path:
        sys.path.insert(0, str(DEPS))
    import r2_common as RC
    import r2_j_independent_vertices as RJ
    return RC, RJ


# --------------------------------------------------------------- 独立转写

def indep_constraints(m2, d, W):
    """按勘误原文独立转写 2m2+1 条约束。

    原文（corrigendum.txt:43 至 :46）：xi ≥ 1；xi+1 ≤ δxi；xm−m2+1 < δxm；
    xm−m2+1 + … + xm ≥ (m2/m)·K。窗口坐标 y_j := x_{m−m2+j}（j = 1..m2），
    记 0 基下标后：
      (C1) y_j ≥ 1                j = 0..m2−1
      (C2) y_{j+1} − δ y_j ≤ 0    j = 0..m2−2；回绕 y_0 − δ y_{m2−1} ≤ 0
      (C3) Σ y_j ≥ W
    回绕约束原文印严格号「<」，本转写与全线核对一律取「≤」（闭化读法，
    出处：rederivation-erratum.md:84 第 3 条、materials.md:45 第 6 条）。
    返回 [(系数元组, 右端, 'ge'/'le')]，顺序与 r2_common.constraint_list 的
    文档承诺一致：先 m2 条 C1，再 m2 条 C2（末条为回绕），最后 1 条 C3。
    """
    d = Fraction(d)
    W = Fraction(W)
    cons = []
    for j in range(m2):
        a = [Fraction(0)] * m2
        a[j] = Fraction(1)
        cons.append((tuple(a), Fraction(1), "ge"))
    for j in range(m2 - 1):
        a = [Fraction(0)] * m2
        a[j + 1] = Fraction(1)
        a[j] -= d
        cons.append((tuple(a), Fraction(0), "le"))
    a = [Fraction(0)] * m2
    a[0] = Fraction(1)
    a[m2 - 1] -= d
    cons.append((tuple(a), Fraction(0), "le"))
    cons.append((tuple([Fraction(1)] * m2), W, "ge"))
    return cons


def indep_feasible(y, m2, d, W):
    """独立复写的精确可行性判据（与转写同口径，非严格号只用于违反侧）。"""
    y = [Fraction(t) for t in y]
    if len(y) != m2:
        return False
    if any(t < 1 for t in y):
        return False
    if any(y[(j + 1) % m2] > d * y[j] for j in range(m2)):
        return False
    return sum(y) >= W


# --------------------------------------------------------------- sympy 对拍

def _as_fraction(v):
    import sympy as sp
    return Fraction(int(sp.numer(v)), int(sp.denom(v)))


def sympy_solve(rows, rhs, m):
    """sympy 精确解：返回 (解列表 or None, 系数秩, 增广秩)。

    解存在当且仅当 秩 = m 且增广秩 = 系数秩（列数 m）；否则返回 None。
    """
    import sympy as sp
    A = sp.Matrix([[sp.Rational(c.numerator, c.denominator) for c in r] for r in rows])
    b = sp.Matrix([sp.Rational(t.numerator, t.denominator) for t in rhs])
    rk = A.rank()
    rk_aug = A.row_join(b).rank()
    if rk == m and rk_aug == rk:
        if A.rows == A.cols:
            solv = A.solve(b)
        else:
            forest = sp.linsolve((A, b))
            assert len(forest) == 1, "预期唯一解"
            solv = list(forest)[0]
        return [_as_fraction(v) for v in solv], rk, rk_aug
    return None, rk, rk_aug


def indep_enum_sympy(m2, d, W):
    """独立全活跃子集枚举（sympy 算术栈 + 独立转写 + 独立可行性）。

    返回 (顶点字典：坐标元组 → [子集…], 迭代子集数, 全秩子集数, 命中数)。
    命中数按子集计（同一顶点被多个子集命中的会重复计数）。
    """
    cons = indep_constraints(m2, d, W)
    n = 2 * m2 + 1
    verts = {}
    cnt = 0
    full_rank = 0
    hits = 0
    for S in combinations(range(n), m2):
        cnt += 1
        rows = [cons[i][0] for i in S]
        rhs = [cons[i][1] for i in S]
        sol, _rk, _rkaug = sympy_solve(rows, rhs, m2)
        if sol is None:
            continue
        full_rank += 1
        if indep_feasible(sol, m2, d, W):
            hits += 1
            verts.setdefault(tuple(sol), []).append(S)
    return verts, cnt, full_rank, hits


def active_rank_sympy(y, m2, d, W):
    """活跃约束（a·y = b 全部计入，ge 与 le 同）法向量在 sympy 下的秩与条数。"""
    import sympy as sp
    cons = indep_constraints(m2, d, W)
    rows = []
    for a, b, _s in cons:
        if sum(a[j] * Fraction(y[j]) for j in range(m2)) == b:
            rows.append([sp.Rational(c.numerator, c.denominator) for c in a])
    if not rows:
        return 0, 0
    return sp.Matrix(rows).rank(), len(rows)
