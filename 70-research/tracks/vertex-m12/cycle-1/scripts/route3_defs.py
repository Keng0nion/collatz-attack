#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route3_defs.py —— route-3（第二实现交叉核验）冻结定义与公共工具。

性质：本文件由 route-3 自写，**不 import 项目既有脚本**（不 import r2_common、不 import
r2_j_independent_vertices）。约束表、可行性、解析族、组合编号都在本文件里独立实现，
只用 fractions.Fraction、math.comb 与 gmpy2 整数幂。

冻结定义（与 tracks/vertex-m12/cycle-1/materials.md 第 1.1 节、cycle-1/route-1.md 的
Step 8′、r2_common.py 的 docstring 逐字同口径；本文件独立复算一次）：

  窗口坐标 y = (y_1, ..., y_m2) ∈ R^{m2}，多面体 P(m2, δ, W) 由 2*m2 + 1 条约束给出：
    (C1_j)  y_j >= 1                    j = 1..m2
    (C2_j)  y_{j+1} <= δ * y_j          j = 1..m2，指标模 m2；j = m2 即回绕约束
    (C3)    Σ_j y_j >= W

  参数（本轨道冻结）：δ := 15849625 / 10^7 = 126797 / 80000（log2(3) 的严格**下界**，
  由整数幂比较 2^15849625 < 3^10000000 现场复核），W := 2000。

  待检验命题（机器核对级，措辞见 tracks/vertex-m12/plan.md 节八）：
    对上述参数，P 的顶点集恰为 m2 个循环旋转
      { v * (δ^r, δ^{r+1}, ..., δ^{r+m2-1}) : r = 0..m2-1 },  v = W(δ-1)/(δ^{m2}-1)。

顶点判据（初等线性代数，不依赖 (L1)、不依赖顶点引理）：
  1. 若 y 是 P 的顶点，则 y 处活跃约束（取等的约束）的法向量张成 R^{m2}（秩 m2），
     故存在一个大小恰为 m2、法向量线性无关的活跃约束子集 S，y 是方程组 A_S y = b_S
     的唯一解。=> 枚举全部 C(2m2+1, m2) 个大小 m2 的子集不漏顶点。
  2. 反之，若某子集 S 的方程 A_S y = b_S 有唯一解 y 且 y ∈ P，则 y 处活跃集的秩
     >= rank(S) = m2，即 y 是顶点。=> 枚举结果都是顶点（附可行性）。
  （这两条在本脚本里只是允许枚举的完备性论证，搜索本体不做任何结构剪枝。）
"""
from fractions import Fraction
from math import comb
import gmpy2

# ------------------------------------------------------------------ 冻结参数

DELTA_P = 15849625          # 下界分子：2^p < 3^q
DELTA_Q = 10 ** 7           # 下界分母
W_FROZEN = Fraction(2000)   # 本轨道 W = 2000

_MASK64 = (1 << 64) - 1


def delta_lo(verify=True):
    """返回 δ 的严格下界 Fraction(p, q)，verify=True 时用整数幂现场复核 2^p < 3^q < 2^{p+1}。"""
    p, q = DELTA_P, DELTA_Q
    if verify:
        left = gmpy2.mpz(2) ** p
        right = gmpy2.mpz(3) ** q
        assert left < right, "锚点复核失败：2^15849625 < 3^10^7 不成立"
        assert right < gmpy2.mpz(2) ** (p + 1), "锚点复核失败：3^10^7 < 2^15849626 不成立"
    return Fraction(p, q)


def check_delta_anchor():
    """返回复核行的字符串摘要（供日志落盘）。"""
    p, q = DELTA_P, DELTA_Q
    left = gmpy2.mpz(2) ** p
    right = gmpy2.mpz(3) ** q
    hi = gmpy2.mpz(2) ** (p + 1)
    d = Fraction(p, q)
    return (f"δ 锚点复核（整数幂，无浮点）：2^{p} < 3^{q} < 2^{p+1} 全部为真 = "
            f"{bool(left < right < hi)}；δ 下界 = {d.numerator}/{d.denominator}"
            f" = {float(d):.10f}（浮点仅作摘要）")


# ------------------------------------------------------- 约束表的整数放大形式

def constraint_rows(m2, delta, W):
    """2m2+1 条约束的整数系数行。

    每行独立乘一个**正**比例因子化成整数（行放大不改变等式解集、不改变不等号方向、
    不改变取等与否、不改变法向量张成的空间）：
      C1_j: q * y_j                 = q          （乘 q）
      C2_j: q * y_{j+1} - p * y_j   = 0          （乘 q；δ = p/q）
      C3  : q * wd * Σ y_j          = q * wn     （乘 q*wd；W = wn/wd）

    返回：列表，元素 (kind, j, row(int 列表), rhs(int), label)。
    顺序与 r2_common.constraint_list 一致：前 m2 条 C1，接着 m2 条 C2（末条即回绕），
    最后 C3。
    """
    p, q = delta.numerator, delta.denominator
    wn, wd = W.numerator, W.denominator
    cons = []
    for j in range(m2):
        row = [0] * m2
        row[j] = q
        cons.append(("C1", j, row, q, f"C1_{j+1}"))
    for j in range(m2):
        row = [0] * m2
        row[(j + 1) % m2] = q
        row[j] -= p
        cons.append(("C2", j, row, 0, f"C2_{j+1}"))
    row = [q * wd] * m2
    cons.append(("C3", -1, row, q * wn, "C3"))
    return cons


# ------------------------------------------------------------ 解析族与可行性

def v_vertex(m2, delta, W):
    """v = W(δ-1)/(δ^{m2}-1)（精确有理）。"""
    return Fraction(W) * (delta - 1) / (delta ** m2 - 1)


def analytic_vertices(m2, delta, W):
    """解析族的 m2 个循环旋转（精确有理坐标集合）。"""
    v = v_vertex(m2, delta, W)
    return {tuple(v * delta ** ((j + r) % m2) for j in range(m2)) for r in range(m2)}


def feasible(y, m2, delta, W):
    """精确可行性判定（独立于搜索本体重写一份）：返回 (bool, 违反约束标签列表)。"""
    bad = []
    if len(y) != m2:
        return False, ["长度"]
    for j in range(m2):
        if y[j] < 1:
            bad.append(f"C1_{j+1}")
    for j in range(m2):
        if y[(j + 1) % m2] > delta * y[j]:
            bad.append(f"C2_{j+1}")
    if sum(y) < W:
        bad.append("C3")
    return (len(bad) == 0), bad


def active_labels(y, m2, delta, W, cons=None):
    """y 处取等的约束标签列表（精确有理判定）。"""
    if cons is None:
        cons = constraint_rows(m2, delta, W)
    act = []
    for idx, (kind, j, row, rhs, label) in enumerate(cons):
        val = sum(Fraction(row[k]) * y[k] for k in range(m2))
        if val == rhs:
            act.append(label)
    return act


def rank_fraction(rows, ncols):
    """Fraction 行阶梯秩（本文件自写，route-3 的第三条独立算术路径）。"""
    M = [[Fraction(x) for x in r] for r in rows]
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
        M[rank] = [x / pv for x in M[rank]]
        for i in range(len(M)):
            if i != rank and M[i][col] != 0:
                f = M[i][col]
                M[i] = [M[i][j] - f * M[rank][j] for j in range(ncols)]
        rank += 1
        if rank == len(M):
            break
    return rank


def active_certificate(y, m2, delta, W, cons=None):
    """顶点证书：(活跃约束法向量秩, 活跃约束条数)，用 Fraction 秩路径。"""
    if cons is None:
        cons = constraint_rows(m2, delta, W)
    act = []
    for idx, (kind, j, row, rhs, label) in enumerate(cons):
        val = sum(Fraction(row[k]) * y[k] for k in range(m2))
        if val == rhs:
            act.append(row)
    return rank_fraction(act, m2), len(act)


# ------------------------------------------------------------ 坐标规范化

def canon_point(y):
    """把精确有理坐标元组写成规范字符串（约分、整数写 n/1）。"""
    out = []
    for x in y:
        f = Fraction(x)
        out.append(f"{f.numerator}/{f.denominator}")
    return ",".join(out)


def parse_point(s):
    return tuple(Fraction(t) for t in s.split(","))


# -------------------------------------------------- 组合枚举：字典序编号与推进

def comb_rank_lex(c, n, r):
    """字典序编号：rank = Σ_i （把第 i 位从 c_{i-1}+1 增大到 c_i 所越过的组合数）。"""
    rank = 0
    prev = -1
    for i, e in enumerate(c):
        for j in range(prev + 1, e):
            rank += comb(n - 1 - j, r - 1 - i)
        prev = e
    return rank


def comb_unrank_lex(n, r, rank):
    """字典序编号 rank 对应的组合（严格递增列表）。"""
    res = []
    start = 0
    rem = rank
    for i in range(r):
        for j in range(start, n):
            cnt = comb(n - 1 - j, r - 1 - i)
            if rem < cnt:
                res.append(j)
                start = j + 1
                break
            rem -= cnt
    if len(res) != r:
        raise ValueError("编号越界")
    return res


def comb_next_lex(c, n):
    """把组合按字典序推进一步（返回新列表；已到末位返回 None）。"""
    r = len(c)
    out = list(c)
    i = r - 1
    while i >= 0 and out[i] == n - r + i:
        i -= 1
    if i < 0:
        return None
    out[i] += 1
    for k in range(i + 1, r):
        out[k] = out[k - 1] + 1
    return out


# -------------------------------------------------- 64 位混合（分块校验和用）

def mix64(x):
    """splitmix64 终混（确定性、跨实现一致）。"""
    z = (int(x) + 0x9E3779B97F4A7C15) & _MASK64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK64
    return (z ^ (z >> 31)) & _MASK64


def point_code(point_str):
    """坐标字符串 -> 64 位码（FNV1a）。"""
    h = 0xCBF29CE484222325
    for ch in point_str.encode("utf-8"):
        h = ((h ^ ch) * 0x100000001B3) & _MASK64
    return h


def agg_term(rank, code):
    """子集编号与判定码的混合项；Σ 该项即分块校验和（可交换，便于分块对拍）。"""
    return mix64((mix64(rank) << 1) ^ code)
