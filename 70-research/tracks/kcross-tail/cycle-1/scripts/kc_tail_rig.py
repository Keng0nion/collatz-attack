#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kcross-tail 路线 2（精确解析抽验）自带的严格有理区间引擎。

与 kcross-proof/cycle-1/scripts/r2_rig.py 的独立性（逐条）：
  1. 网格 GRID = 10**230（r2_rig 为 10**200）；
  2. ln 走 atanh 级数：ln2 = 2 atanh(1/3)、ln3 = ln2 + 2 atanh(1/5)
     （r2_rig 走 -ln(1-u) 级数：u = 1/2 与 u = 1/3）；
  3. exp 走「缩到 <= 1/2 + Taylor(N = 150) + 尾界 + 逐次平方」，缩幅按 yhi <= 1/2 定
     （r2_rig 缩到 <= 1，N = 210）；
  4. 整数幂 delta^m 走带定向取整的二进制幂（与 r2_rig 同构，但网格不同）。
公式侧（eps、geom、v、A(m2)、C 的语义）与 r2_rig.py:258 至 :325 的定义一致，
本文件不重新推导公式本身；公式与定理 21 的一致性不在本文件的证据范围内。

严格性约定：每个函数返回 [lo, hi]，保证包含真值；一切取整用 rd（向下）与 ru（向上）
到 1/GRID 网格；级数一律附显式尾项界；判定由调用方用 Fraction 精确完成。
"""
from fractions import Fraction as F

GRID = 10 ** 230
X0_INT = 695 * 2 ** 60
V0_COARSE = 5000

_CACHE = {}


def fl(x):
    x = F(x)
    return x.numerator // x.denominator


def ce(x):
    x = F(x)
    return -((-x.numerator) // x.denominator)


def rd(x):
    x = F(x)
    return F(fl(x * GRID), GRID)


def ru(x):
    x = F(x)
    return F(ce(x * GRID), GRID)


# ---------- 区间四则（允许任意符号，除零区间除外） ----------
def iadd(a, b):
    return (rd(a[0] + b[0]), ru(a[1] + b[1]))


def isub(a, b):
    return (rd(a[0] - b[1]), ru(a[1] - b[0]))


def imul(a, b):
    ps = [a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]]
    return (rd(min(ps)), ru(max(ps)))


def idiv(a, b):
    assert not (b[0] <= 0 <= b[1]), "除零区间"
    ps = [a[0] / b[0], a[0] / b[1], a[1] / b[0], a[1] / b[1]]
    return (rd(min(ps)), ru(max(ps)))


# ---------- ln：atanh 级数 ----------
# 引理：对 0 <= t < 1，atanh(t) = sum_{j>=0} t^{2j+1}/(2j+1)，
# 且第 N 项后尾和 <= t^{2N+3}/((2N+3)(1-t^2))。


def atanh_bounds(t, N=260):
    t = F(t)
    assert 0 <= t <= F(1, 3)
    if t == 0:
        return (F(0), F(0))
    t2 = t * t
    lo = F(0)
    hi = F(0)
    pl, ph = rd(t), ru(t)
    for j in range(N + 1):
        lo = rd(lo + pl / (2 * j + 1))
        hi = ru(hi + ph / (2 * j + 1))
        if j < N:
            pl = rd(pl * t2)
            ph = ru(ph * t2)
    tail = ru(ph * t2 / ((2 * N + 3) * (1 - t2)))
    return lo, ru(hi + tail)


def ln2_bounds(N=260):
    key = ("ln2", N)
    if key not in _CACHE:
        a = atanh_bounds(F(1, 3), N)
        _CACHE[key] = (rd(2 * a[0]), ru(2 * a[1]))
    return _CACHE[key]


def ln3_bounds(N=260):
    key = ("ln3", N)
    if key not in _CACHE:
        a = ln2_bounds(N)
        b = atanh_bounds(F(1, 5), N)
        _CACHE[key] = (rd(a[0] + 2 * b[0]), ru(a[1] + 2 * b[1]))
    return _CACHE[key]


def ln_bounds(x, N=260):
    """ln(x) 的严格区间，x 为精确正有理数（端点用法：ln 单调，分开代入）。"""
    x = F(x)
    assert x > 0
    if x == 1:
        return (F(0), F(0))
    if x < 1:
        a = ln_bounds(1 / x, N)
        return (-a[1], -a[0])
    k = x.numerator.bit_length() - x.denominator.bit_length()
    while F(2) ** k > x:
        k -= 1
    while F(2) ** (k + 1) <= x:
        k += 1
    m = x / F(2) ** k            # m in [1, 2)
    t = (m - 1) / (m + 1)        # t in [0, 1/3)
    a = atanh_bounds(t, N)
    l2 = ln2_bounds(N)
    return (rd(k * l2[0] + 2 * a[0]), ru(k * l2[1] + 2 * a[1]))


def ln_iv(x_iv, N=260):
    """区间 [x_lo, x_hi] 上 ln 的严格区间（要求 x_lo > 0）。"""
    assert x_iv[0] > 0
    a = ln_bounds(x_iv[0], N)
    b = ln_bounds(x_iv[1], N)
    return (a[0], b[1])


# ---------- exp：缩小 + Taylor（N = 150，缩到 <= 1/2）+ 平方 ----------
def exp_bounds(ylo, yhi, N=150):
    ylo, yhi = F(ylo), F(yhi)
    assert 0 <= ylo <= yhi
    if yhi == 0:
        return (F(1), F(1))
    s = 0
    while F(2) ** s < 2 * yhi:      # yhi/2^s <= 1/2
        s += 1
    tl, th = ylo / F(2) ** s, yhi / F(2) ** s
    lo, hi = F(0), F(0)
    pl, ph = F(1), F(1)             # pl <= tl^i <= ph
    fact = F(1)
    for i in range(N + 1):
        if i:
            fact *= i
        lo = rd(lo + pl / fact)
        hi = ru(hi + ph / fact)
        pl = rd(pl * tl)
        ph = ru(ph * th)
    fact *= (N + 1)
    tail = ru(ph * th / fact / (1 - th / (N + 2)))
    hi = ru(hi + tail)
    for _ in range(s):
        lo, hi = rd(lo * lo), ru(hi * hi)
    return rd(lo), ru(hi)


# ---------- delta 与定理 21 的量 ----------
def delta_bounds(N=260):
    key = ("delta", N)
    if key not in _CACHE:
        a = ln2_bounds(N)
        b = ln3_bounds(N)
        _CACHE[key] = (rd(b[0] / a[1]), ru(b[1] / a[0]))
    return _CACHE[key]


def pow_int_bounds(dlo, dhi, n):
    """delta^n 的严格区间（n >= 0 整数），二进制幂 + 定向取整。"""
    assert dlo > 0 and n >= 0

    def step(d, mode):
        r = F(1)
        b = F(d)
        e = n
        while e:
            if e & 1:
                r = rd(r * b) if mode == 0 else ru(r * b)
            e >>= 1
            if e:
                b = rd(b * b) if mode == 0 else ru(b * b)
        return r
    return step(dlo, 0), step(dhi, 1)


def C_bounds():
    key = ("C",)
    if key not in _CACHE:
        arg = F(162, 97) * X0_INT
        a = ln_bounds(arg)
        l2 = ln2_bounds()
        _CACHE[key] = (rd(a[0] / l2[1]), ru(a[1] / l2[0]))
    return _CACHE[key]


def A_of(m2, m):
    """Theorem 21 与证明末段的 A(m2)（照 r2_rig.py:275 至 :281 的同一公式）。"""
    if m2 == m:
        return F(0)
    if m2 == m - 1:
        return F(3, X0_INT)
    return F(97 * (m - m2) + 73, 54 * X0_INT)


def geom_bounds(m2, dlo, dhi):
    pw = pow_int_bounds(dlo, dhi, m2)
    num = (rd(pw[0] - 1), ru(pw[1] - 1))
    den = (rd(dlo - 1), ru(dhi - 1))
    assert num[0] > 0 and den[0] > 0
    return (rd(num[0] / den[1]), ru(num[1] / den[0]))


def v_bounds(m2, m, K, dlo, dhi):
    pw = pow_int_bounds(dlo, dhi, m2)
    num = (rd(dlo - 1), ru(dhi - 1))
    den = (rd(pw[0] - 1), ru(pw[1] - 1))
    assert den[0] > 0
    c = F(m2, m) * F(K)
    return (rd(c * num[0] / den[1]), ru(c * num[1] / den[0]))


def feasible_decision(m2, m, K, dlo, dhi, Civ):
    g = geom_bounds(m2, dlo, dhi)
    lhs = imul(g, Civ)                     # geom(m2) * C
    rhs = ru(F(m2, m) * F(K))
    if lhs[1] < rhs:
        return True
    if lhs[0] > rhs:
        return False
    return None


def eps_bounds(m2, m, K, dlo, dhi, l2):
    """eps(m2, m, K) 的严格区间（公式见 r2_rig.py:303 至 :325）。"""
    A = A_of(m2, m)
    vl, vh = v_bounds(m2, m, K, dlo, dhi)
    if vl >= V0_COARSE:
        slack = F(3 + 3 * (m2 - 1), 2 ** V0_COARSE - 1)
        num = (rd(A), ru(A + slack))
    else:
        two_v = exp_bounds(rd(vl * l2[0]), ru(vh * l2[1]))
        t = (rd(two_v[0] - 1), ru(two_v[1] - 1))
        assert t[0] > 1, "2^v - 1 需 > 1 才取 ln"
        term1 = idiv((F(3), F(3)), t)
        ln_t = ln_iv(t)
        e = (rd(dlo * ln_t[0]), ru(dhi * ln_t[1]))
        pt = exp_bounds(e[0], e[1])
        term2 = idiv((F(3 * (m2 - 1)), F(3 * (m2 - 1))), pt)
        num = (rd(A + term1[0] + term2[0]), ru(A + term1[1] + term2[1]))
    den = imul((F(3 * K), F(3 * K)), l2)
    return idiv(num, den)
