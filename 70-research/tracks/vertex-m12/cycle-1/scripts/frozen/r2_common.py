#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-2 公共模块：窗口多面体的定义、精确有理界、可行性与顶点。

纪律（对应 70-research/learnings.md 第 28 条「先定死定义再用已知值做锚点自检」）：
  1. 本文件只按勘误原文的约束表定义多面体与目标函数，不 import 任何项目脚本，
     也不读任何既有脚本的输出。
  2. 一切判决只用 fractions.Fraction 与整数幂（gmpy2），浮点与 mpmath 只用于
     「探针」与「锚点自检」，绝不参与反例判定。

多面体（勘误原文约束表的逐字转写，窗口 y_j := x_{m−m2+j}，j = 1..m2）：
  (C1) y_j >= 1                  （x_i = log2(n_i + 1) >= 1）
  (C2) y_{j+1} <= δ y_j          （j = 1..m2，指标循环，m2 条；末条即回绕约束
                                  x_{m−m2+1} <= δ x_m）
  (C3) Σ_j y_j >= W              （W = (m2/m)·K）
目标：
  S(y) = Σ_{j=1}^{m2} 3 / (2^{y_j} − 1)
"""
from fractions import Fraction
import gmpy2

# ------------------------------------------------- 确定性抽样器（自带的整数发生器）

class Det:
    """splitmix64 型的确定性整数发生器：只用于可复现的抽样，不做任何安全用途。

    自带实现，避免依赖标准库随机数的行为差异；同一个种子在任何机器上给出同一串数。
    """

    def __init__(self, seed):
        self.s = (seed * 0x9E3779B97F4A7C15 + 0x2545F4914F6CDD1D) & ((1 << 64) - 1)

    def next(self):
        self.s = (self.s + 0x9E3779B97F4A7C15) & ((1 << 64) - 1)
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & ((1 << 64) - 1)
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & ((1 << 64) - 1)
        return z ^ (z >> 31)

    def below(self, n):
        """[0, n) 上的均匀整数（n 为正整数）。"""
        return self.next() % n

    def between(self, a, b):
        """[a, b] 上的均匀整数。"""
        return a + self.below(b - a + 1)

    def pick(self, seq):
        return seq[self.below(len(seq))]


# ---------------------------------------------------------------- δ 的严格括号

def delta_rigorous_bounds(q):
    """返回 (p/q, r/q) 使 2^p < 3^q < 2^r，即 p/q < log3/log2 < r/q。

    判据只用整数幂比较（2^p < 3^q 等价于 p/q < log3/log2），不用浮点。
    """
    import mpmath
    mpmath.mp.dps = 60
    d = mpmath.log(3) / mpmath.log(2)
    base = int(mpmath.floor(d * q))
    three_q = gmpy2.mpz(3) ** q
    p = base
    while not (gmpy2.mpz(2) ** p < three_q):
        p -= 1
    r = base + 1
    while not (gmpy2.mpz(2) ** r > three_q):
        r += 1
    return Fraction(p, q), Fraction(r, q)


# ------------------------------------------------- 2^e 与 3/(2^t − 1) 的严格界

def pow2_bounds(P, k, s):
    """e = P / 2^k（P 为整数，2^k 见下）；返回有理 (lo, hi) 使 lo <= 2^e <= hi。

    做法：令 q = 2^k，m = floor( (2^{P + s·q})^{1/q} )，则
        m / 2^s <= 2^e <= (m+1) / 2^s
    两个方向都只用整数根与整数幂，故严格。
    """
    q = 1 << k
    R = P + s * q
    if R < 0:
        raise ValueError("pow2_bounds 只支持 e >= −s")
    m, _exact = gmpy2.iroot(gmpy2.mpz(1) << R, q)
    m = int(m)
    return Fraction(m, 1 << s), Fraction(m + 1, 1 << s)


def f_bounds(t, k=10, s=20, Tmax=1000):
    """严格区间 [lo, hi] 含 3/(2^t − 1)，t 为正有理数（Fraction 或 int）。

    精度由 (k, s) 控制：把指数 t 向外舍入到 2^{-k} 的整数倍，再用 pow2_bounds 的
    2^{-s} 相对精度。t > Tmax 时用平凡界 (0, 3/(2^Tmax − 1))，仍是严格上界。
    """
    t = Fraction(t)
    if t > Tmax:
        return Fraction(0), Fraction(3, (1 << Tmax) - 1)
    if t <= 0:
        raise ValueError("t 必须为正")
    q = 1 << k
    Pa = (t * q).__floor__()            # floor(t·2^k)
    Pb = -((-t * q).__floor__())        # ceil(t·2^k)
    Alo, _Ahi = pow2_bounds(Pa, k, s)   # 2^{Pa/2^k} 的下界
    Blo, Bhi = pow2_bounds(Pb, k, s)    # 2^{Pb/2^k} 的界
    # f 关于 t 递减：Pa/2^k <= t <= Pb/2^k ⟹ f(Pb/2^k) <= f(t) <= f(Pa/2^k)
    hi = Fraction(3, 1) / (Alo - 1)
    lo = Fraction(3, 1) / (Bhi - 1)
    assert lo <= hi, (lo, hi)
    return lo, hi


def S_bounds(y, k=10, s=20, Tmax=1000):
    """严格区间 [lo, hi] 含 S(y) = Σ 3/(2^{y_j} − 1)。"""
    lo = Fraction(0)
    hi = Fraction(0)
    for t in y:
        a, b = f_bounds(t, k, s, Tmax)
        lo += a
        hi += b
    return lo, hi


# 精度档（k, s, Tmax）：带宽约为 0.7·(2^{-k} + 2^{-s}) 的相对量（实测值见运行日志）
LEVEL_COARSE = (0, 0, 10 ** 6)      # 指数按整数取整，带宽约 0.7 个相对量级，最便宜
LEVEL_MID = (10, 20, 1000)          # 实测带宽 6.8e-04
LEVEL_FINE = (14, 24, 300)          # 实测带宽 4.2e-05
LEVEL_ULTRA = (18, 28, 120)         # 实测约 2.6e-06（单项 iroot 约 0.12 s）


# ------------------------------------------------------------------ 多面体层

def v_vertex(m2, d, W):
    """v = W(δ−1)/(δ^{m2}−1)。"""
    return Fraction(W) * (d - 1) / (d ** m2 - 1)


def vertex(m2, d, W, rot=0):
    """顶点向量：v·(δ^{rot}, δ^{rot+1}, ..., δ^{rot+m2−1})（指标 mod m2）。"""
    v = v_vertex(m2, d, W)
    return tuple(v * d ** ((j + rot) % m2) for j in range(m2))


def feasible(y, m2, d, W):
    """精确可行性判定：返回 (bool, 违反的约束编号列表)。"""
    bad = []
    y = list(y)
    if len(y) != m2:
        return False, ["长度"]
    for j in range(m2):
        if y[j] < 1:
            bad.append(f"C1:y{j+1}<1")
    for j in range(m2):
        if y[(j + 1) % m2] > d * y[j]:
            bad.append(f"C2:y{(j+1)%m2+1}>δ·y{j+1}")
    if sum(y) < W:
        bad.append("C3:Σy<W")
    return (len(bad) == 0), bad


def constraint_list(m2, d, W):
    """把 2m2+1 条约束写成 (系数向量, 右端, 类型) 列表，类型 'ge'/'le'。

    顺序：前 m2 条是 y_j >= 1；接着 m2 条是链约束 y_{j+1} <= δ y_j（j=0..m2−1
    循环，第 m2−1 条即回绕）；最后一条是 Σy >= W。
    """
    cons = []
    for j in range(m2):
        a = [Fraction(0)] * m2
        a[j] = Fraction(1)
        cons.append((a, Fraction(1), "ge"))
    for j in range(m2):
        a = [Fraction(0)] * m2
        a[(j + 1) % m2] = Fraction(1)
        a[j] -= d
        cons.append((a, Fraction(0), "le"))
    a = [Fraction(1)] * m2
    cons.append((a, Fraction(W), "ge"))
    return cons


def solve_exact(A, b):
    """精确高斯消元（Fraction）。返回 (解, 秩)；若不相容返回 (None, 秩)。"""
    n = len(A)
    m = len(A[0])
    M = [[Fraction(A[i][j]) for j in range(m)] + [Fraction(b[i])] for i in range(n)]
    rank = 0
    pivots = []
    for col in range(m):
        piv = None
        for i in range(rank, n):
            if M[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        pv = M[rank][col]
        M[rank] = [v / pv for v in M[rank]]
        for i in range(n):
            if i != rank and M[i][col] != 0:
                f = M[i][col]
                M[i] = [M[i][j] - f * M[rank][j] for j in range(m + 1)]
        pivots.append(col)
        rank += 1
        if rank == n:
            break
    for i in range(rank, n):
        if all(M[i][j] == 0 for j in range(m)) and M[i][m] != 0:
            return None, rank
    if rank < m:
        return None, rank          # 解不唯一
    sol = [Fraction(0)] * m
    for i, col in enumerate(pivots):
        sol[col] = M[i][m]
    return sol, rank


def clean(y):
    """把近整数坐标压成整数（只用于构造，不改动数学内容；Fraction 精确）。"""
    return tuple(Fraction(t) for t in y)


def repair_normalize(y, m2, d, W):
    """把任意正坐标压成可行点：从最大坐标向后逐条压链，再放大到 Σ>=W 且 min>=1。

    压链用更新后的前驱坐标，故一趟扫描后全部 m2 条链约束成立；放大不改变比值，
    故链约束保持；放大系数取 max(1, W/Σy, 1/min y)，同时保证 Σ>=W 与 min>=1。
    """
    y = [Fraction(t) for t in y]
    if min(y) <= 0:
        return None
    a = max(range(m2), key=lambda i: y[i])
    for _sweep in range(2):
        # 两趟：第一趟可能把锚点 y_a 压小，从而破坏出口约束 y_{a+1} <= δ y_a；
        # 第二趟从 a+1 起重扫并修好它，且此时 y_a 已满足 y_a <= δ y_{a−1}，故不再变动。
        for k in range(1, m2 + 1):
            i = (a + k) % m2
            lim = d * y[(i - 1) % m2]
            if y[i] > lim:
                y[i] = lim
    lam = max(Fraction(1), W / sum(y), Fraction(1) / min(y))
    return [t * lam for t in y]
