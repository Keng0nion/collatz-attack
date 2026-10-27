#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 独立复算库（换算法）：严格有理区间库。

与 70-research/cycle-2/scripts/c2r5_rig.py 的原语对照（本库一律用不同的原语）：

| 量 | 本库 | c2r5_rig |
|---|---|---|
| ln2 | 4·atanh(1/6) + 2·atanh(1/99)（Machin 式分解） | 2·atanh(1/3) |
| ln3 | 2·atanh(1/2)（单级数） | ln2 + 2·atanh(1/5) |
| 2^x（x 有理） | 二进制展开 + 嵌套平方根（只用 isqrt 与有理数乘法） | exp 的 Taylor 加尾界 |
| (1−u)^δ | 二项级数前两项 + 显式余项 | ln(1−u) 级数 + exp |
| 区间取整 | 一律乘 GRID 后 floor/ceil（Fraction 精确） | 同型（GRID = 10^100） |

本库不含任何浮点判决；mpmath 只在对照脚本里出现，并明确标注「非严格」。

一切上下界都写成 (lo, hi) 的 Fraction 对，lo 为下界、hi 为上界。
"""
from fractions import Fraction as F
from math import gcd, isqrt

GRID = 10 ** 160            # 全局取整网格
POW2_D = 90                 # 嵌套平方根每层的十进制位数
POW2_L = 256                # 二进制展开位数
V_COARSE = 4000             # v >= 此值时 2^v 走「解析压掉」分支


def fl(x):
    x = F(x)
    return x.numerator // x.denominator


def ce(x):
    x = F(x)
    return -((-x.numerator) // x.denominator)


def rd(x):
    """向下取整到 1/GRID 网格。"""
    return F(fl(F(x) * GRID), GRID)


def ru(x):
    """向上取整到 1/GRID 网格。"""
    return F(ce(F(x) * GRID), GRID)


def dec(x, nd):
    """精确十进制截断打印（与 c2r5_cert.py 的 dec 同型，便于逐位对拍）。"""
    x = F(x)
    sign = "-" if x < 0 else ""
    x = abs(x)
    ip = x.numerator // x.denominator
    rem = x.numerator - ip * x.denominator
    out = [sign + str(ip), "."]
    for _ in range(nd):
        rem *= 10
        out.append(str(rem // x.denominator))
        rem -= (rem // x.denominator) * x.denominator
    return "".join(out)


def sci(x, nd=22):
    """科学计数法（nd 位有效数字），供人读；不用于判定。"""
    x = F(x)
    if x == 0:
        return "0"
    sign = "-" if x < 0 else ""
    ax = abs(x)
    e = 0
    while ax >= 10:
        ax /= 10
        e += 1
    while ax < 1:
        ax *= 10
        e -= 1
    s = dec(ax, nd)
    return "%s%se%s%d" % (sign, s, "+" if e >= 0 else "-", abs(e))


# ---------------- 1. atanh 级数与 ln2、ln3 ----------------

def atanh_bounds(x, N):
    """atanh(x) 的严格区间，0 < x < 1，取前 N 项。

    余项 R_N = sum_{k>=N} x^{2k+1}/(2k+1) ∈ (0, x^{2N+1}/((2N+1)(1-x^2))]。
    """
    x = F(x)
    assert 0 < x < 1 and N >= 1
    x2 = x * x
    s = F(0)
    p = x                      # p = x^(2k+1)
    for k in range(N):
        s += p / (2 * k + 1)
        p *= x2
    tail = p / ((2 * N + 1) * (1 - x2))
    return s, s + tail


def ln2_bounds(N=140):
    """ln2 = 4·atanh(1/6) + 2·atanh(1/99)（Machin 式；两个级数都跑得快）。"""
    a = atanh_bounds(F(1, 6), N)
    b = atanh_bounds(F(1, 99), N)
    return rd(4 * a[0] + 2 * b[0]), ru(4 * a[1] + 2 * b[1])


def ln3_bounds(N=300):
    """ln3 = 2·atanh(1/2)。"""
    a = atanh_bounds(F(1, 2), N)
    return rd(2 * a[0]), ru(2 * a[1])


def ln2_bounds_alt(N=140):
    """对照路径 A：ln2 = 2·atanh(1/7) + 2·atanh(1/5)（= ln(4/3) + ln(3/2)）。"""
    a = atanh_bounds(F(1, 7), N)
    b = atanh_bounds(F(1, 5), N)
    return rd(2 * a[0] + 2 * b[0]), ru(2 * a[1] + 2 * b[1])


def ln3_bounds_alt(N=300):
    """对照路径 A：ln3 = ln2 + 2·atanh(1/5)（= ln2 + ln(3/2)）。"""
    a = ln2_bounds(N)
    b = atanh_bounds(F(1, 5), N)
    return rd(a[0] + 2 * b[0]), ru(a[1] + 2 * b[1])


def ln_bounds(x, N=200):
    """ln(x) 的严格区间，x > 0 有理数：x = 2^k·m, m ∈ [1,2)，ln m = 2·atanh((m-1)/(m+1))。"""
    x = F(x)
    assert x > 0
    if x == 1:
        return F(0), F(0)
    if x < 1:
        lo, hi = ln_bounds(1 / x, N)
        return -hi, -lo
    k = x.numerator.bit_length() - x.denominator.bit_length()
    while F(2) ** k > x:
        k -= 1
    while F(2) ** (k + 1) <= x:
        k += 1
    m = x / F(2) ** k
    t = (m - 1) / (m + 1)
    a = atanh_bounds(t, N) if t > 0 else (F(0), F(0))
    l2 = ln2_bounds(N)
    return rd(k * l2[0] + 2 * a[0]), ru(k * l2[1] + 2 * a[1])


def delta_bounds(Nl2=140, Nl3=300):
    """delta = ln3/ln2 的严格区间。"""
    a = ln2_bounds(Nl2)
    b = ln3_bounds(Nl3)
    return rd(b[0] / a[1]), ru(b[1] / a[0])


# ---------------- 2. 定理 21 的常数 ----------------

X0_INT = 695 * 2 ** 60


def C_bounds():
    """C = log2((162/97)·X0) = 60 + ln(112590/97)/ln2 的严格区间。"""
    l2 = ln2_bounds()
    ln_r = ln_bounds(F(112590, 97))
    return rd(60 + ln_r[0] / l2[1]), ru(60 + ln_r[1] / l2[0])


# ---------------- 3. 2^x：二进制展开 + 嵌套平方根 ----------------

def _sqrt_lo(y, D=POW2_D):
    """√y 的严格下界：s/10^D，s = isqrt(floor(y·10^(2D)))。"""
    y = F(y)
    q = (y.numerator * 10 ** (2 * D)) // y.denominator
    return F(isqrt(q), 10 ** D)


def _sqrt_hi(y, D=POW2_D):
    """√y 的严格上界：(isqrt(floor(y·10^(2D)))+1)/10^D。"""
    y = F(y)
    q = (y.numerator * 10 ** (2 * D)) // y.denominator
    return F(isqrt(q) + 1, 10 ** D)


_ROOT_TABLE = {}


def root_table(L=POW2_L, D=POW2_D):
    """r_i = 2^(2^{-i}) 的区间表，i = 1..L（r_{i} = √r_{i-1}，逐层用定向平方根）。"""
    key = (L, D)
    if key in _ROOT_TABLE:
        return _ROOT_TABLE[key]
    lo = F(2)
    hi = F(2)
    tbl = []
    for _ in range(L):
        lo = _sqrt_lo(lo, D)
        hi = _sqrt_hi(hi, D)
        tbl.append((lo, hi))
    _ROOT_TABLE[key] = tbl
    return tbl


def _bits_of(f, L):
    """f ∈ [0,1) 的二进制前 L 位：返回下标列表 S（b_i = 1），i 从 1 起。"""
    f = F(f)
    n, d = f.numerator, f.denominator
    S = []
    for i in range(1, L + 1):
        if ((n << i) // d) & 1:
            S.append(i)
    return S


def _prod_lo(f, L):
    tbl = root_table(L)
    p = F(1)
    for i in _bits_of(f, L):
        p *= tbl[i - 1][0]
    return p


def _prod_hi(f, L):
    tbl = root_table(L)
    p = F(1)
    for i in _bits_of(f, L):
        p *= tbl[i - 1][1]
    return p


def pow2_bounds(x_lo, x_hi, L=POW2_L):
    """2^x 的严格区间，x ∈ [x_lo, x_hi]。

    下界：x >= x_lo ⟹ 2^x >= 2^{floor(x_lo)}·(二进制截断的乘积下界)。
    上界：f − p(f) < 2^{-L}，2^{f-p} <= 1 + 2^{-L}·ln2·… <= 1 + 4·2^{-L}（用 e^u <= 1+2u, u<=1）。
    """
    x_lo, x_hi = F(x_lo), F(x_hi)
    assert x_lo <= x_hi
    if x_lo < 0 < x_hi:
        a = pow2_bounds(-x_lo, -x_lo, L)          # 点值 2^{-x_lo}
        b = pow2_bounds(x_hi, x_hi, L)            # 点值 2^{x_hi}
        return rd(F(1) / a[1]), ru(b[1])
    if x_hi <= 0:
        if x_lo == 0:
            return rd(F(1)), ru(F(1))
        a = pow2_bounds(-x_lo, -x_lo, L)          # 点值 2^{-x_lo}
        lo = F(1) / a[1]
        if x_hi == 0:
            hi = F(1)
        else:
            b = pow2_bounds(-x_hi, -x_hi, L)      # 点值 2^{-x_hi}
            hi = F(1) / b[0]
        return rd(lo), ru(hi)
    assert x_hi < 10 ** 7, "指数过大，pow2 原语不适用"
    n_lo = fl(x_lo)
    n_hi = fl(x_hi)
    f_lo = x_lo - n_lo
    f_hi = x_hi - n_hi
    lo = F(2) ** n_lo * _prod_lo(f_lo, L)
    hi = F(2) ** n_hi * _prod_hi(f_hi, L) * (1 + 4 * F(1, 2 ** L))
    return rd(lo), ru(hi)


# ---------------- 4. (2^v − 1)^delta ----------------

def one_minus_u_pow_delta_bounds(u_lo, u_hi, d_lo, d_hi):
    """(1−u)^δ 的严格区间，0 < u_lo <= u_hi < 1/4，δ ∈ (1, 2)。

    用二项级数前两项： (1−u)^δ = 1 − δu + W(δ)u² + R，W(δ) = δ(δ−1)/2，
    余项 |R| <= sum_{k>=3} u^k = u³/(1−u)（因 |C(δ,k)| = δ(δ−1)Π|δ−j|/k! <= 2/(k(k−1)) <= 1 于 k>=3）。
    """
    u_lo, u_hi = F(u_lo), F(u_hi)
    d_lo, d_hi = F(d_lo), F(d_hi)
    assert 0 <= u_lo <= u_hi < 1
    if u_hi >= F(1, 4):
        # 兜底：Bernoulli 不等式 (1-u)^δ >= 1 - δu（δ >= 1, u ∈ [0,1]），上界取 1
        lo = 1 - d_hi * u_hi
        return rd(lo if lo > 0 else F(0)), F(1)
    W_lo = d_lo * (d_lo - 1) / 2
    W_hi = d_hi * (d_hi - 1) / 2
    tail = u_hi ** 3 / (1 - u_hi)
    # u_lo 可能因网格向下取整变 0：此时二次项取 0 仍是合法下界/上界（见 docstring 的单调性）
    lo = 1 - d_hi * u_hi + W_lo * u_lo * u_lo - tail
    hi = 1 - d_lo * u_lo + W_hi * u_hi * u_hi + tail
    return rd(lo), ru(hi)


def t2vm1_delta_bounds(v_lo, v_hi, d_lo, d_hi):
    """(2^v − 1)^δ 的严格区间，v ∈ [v_lo, v_hi]（正）、δ ∈ [d_lo, d_hi] ⊂ (1,2)。

    恒等式 2^v − 1 = 2^v(1 − 2^{-v})：(2^v−1)^δ = 2^{vδ}·(1−2^{-v})^δ。
    """
    v_lo, v_hi = F(v_lo), F(v_hi)
    d_lo, d_hi = F(d_lo), F(d_hi)
    p2 = pow2_bounds(v_lo, v_hi)
    f1 = pow2_bounds(rd(v_lo * d_lo), ru(v_hi * d_hi))
    u_lo = rd(F(1) / p2[1])
    u_hi = ru(F(1) / p2[0])
    f2 = one_minus_u_pow_delta_bounds(u_lo, u_hi, d_lo, d_hi)
    return rd(f1[0] * f2[0]), ru(f1[1] * f2[1])


# ---------------- 5. 定理 21 的 v、A、eps、可行性 ----------------

def A_of(m2, m, X0=X0_INT):
    if m2 == m:
        return F(0)
    if m2 == m - 1:
        return F(3, X0)
    return F(97 * (m - m2) + 73, 54 * X0)


def v_bounds(m2, m, K, d_lo, d_hi):
    """v = (m2/m)K(δ−1)/(δ^{m2}−1) 的严格区间（δ 精确整数幂，四角法则）。"""
    d_lo, d_hi = F(d_lo), F(d_hi)
    K = F(K)
    pw_lo = d_lo ** m2
    pw_hi = d_hi ** m2
    c = F(m2, m) * K
    assert pw_lo > 1
    v_lo = c * (d_lo - 1) / (pw_hi - 1)
    v_hi = c * (d_hi - 1) / (pw_lo - 1)
    return rd(v_lo), ru(v_hi)


def eps_bounds(m2, m, K, d_lo, d_hi, l2):
    """eps(m2, m, K) 的严格区间：(A + 3/(2^v−1) + 3(m2−1)/(2^v−1)^δ) / (3K ln2)。"""
    K = F(K)
    A = A_of(m2, m)
    vl, vh = v_bounds(m2, m, K, d_lo, d_hi)
    den_lo = rd(3 * K * l2[0])
    den_hi = ru(3 * K * l2[1])
    if vl >= V_COARSE or vh > 8 * V_COARSE:
        # v 很大：只保留 A 与一个解析上界（对下界无害，因为三项都非负）
        slack = F(3 + 3 * (m2 - 1), 2 ** V_COARSE)
        num_lo = rd(A)
        num_hi = ru(A + slack)
        return rd(num_lo / den_hi), ru(num_hi / den_lo)
    p2 = pow2_bounds(vl, vh)
    t_lo = rd(p2[0] - 1)
    t_hi = ru(p2[1] - 1)
    assert t_lo > 0
    term2_lo = rd(3 / t_hi)
    term2_hi = ru(3 / t_lo)
    pt = t2vm1_delta_bounds(vl, vh, d_lo, d_hi)
    c3 = 3 * (m2 - 1)
    term3_lo = rd(c3 / pt[1]) if c3 else F(0)
    term3_hi = ru(c3 / pt[0]) if c3 else F(0)
    num_lo = rd(A + term2_lo + term3_lo)
    num_hi = ru(A + term2_hi + term3_hi)
    return rd(num_lo / den_hi), ru(num_hi / den_lo)


def eps_lower_A_only(m2, m, K, l2):
    """eps 的 A 部分下界：A(m2)/(3K·ln2_hi)（其余两项非负，对一切 v 有效）。"""
    K = F(K)
    return rd(A_of(m2, m) / (3 * K * l2[1]))


def geom_bounds(m2, d_lo, d_hi):
    """geom(m2) = (δ^{m2} − 1)/(δ − 1) 的严格区间（精确整数幂）。"""
    d_lo, d_hi = F(d_lo), F(d_hi)
    num_lo = d_lo ** m2 - 1
    num_hi = d_hi ** m2 - 1
    den_lo = d_lo - 1
    den_hi = d_hi - 1
    return rd(num_lo / den_hi), ru(num_hi / den_lo)


def feasible(m2, m, K, d_lo, d_hi, C):
    """geom(m2)·C <= (m2/m)K 的严格判定，返回 True / False / None。"""
    g = geom_bounds(m2, d_lo, d_hi)
    lhs_lo = rd(g[0] * C[0])
    lhs_hi = ru(g[1] * C[1])
    rhs = F(m2, m) * F(K)
    if lhs_hi <= rhs:
        return True
    if lhs_lo > rhs:
        return False
    return None


# ---------------- 6. 连分数：证书、收敛子、SB 双亲、清单 ----------------

def certified_prefix(lo, hi, maxlen=200):
    """区间 [lo, hi] 内每一点连分数展开的公共前 maxlen 位（外向取整保包含）。

    每步要求 floor(lo) = floor(hi) = n 且 lo > n（严格），Gauss 映射 1/(x−n) 递减，
    故像区间为 [1/(hi−n), 1/(lo−n)]；为控制分母规模，向外取整到 1/GRID 网格。
    """
    lo, hi = F(lo), F(hi)
    assert lo < hi
    digits = []
    for _ in range(maxlen):
        n = fl(lo)
        if fl(hi) != n or lo == n:
            break
        digits.append(n)
        nlo = F(1) / (hi - n)
        nhi = F(1) / (lo - n)
        lo = rd(nlo)          # 向下取整 => 区间扩大（仍是超集）
        hi = ru(nhi)
    return digits


def cf_frac(p, q):
    """p/q 的规范连分数（末项 >= 2，除非是整数）。"""
    p, q = int(p), int(q)
    out = []
    while q:
        a = p // q
        out.append(a)
        p, q = q, p - a * q
    return out


def cf_value(quot):
    v = F(0)
    for a in reversed(quot):
        v = F(a) + (F(0) if v == 0 else 1 / v)
    return v


def sb_parents(p, q):
    """p/q（最简、非整数）的 Stern-Brocot 双亲 (lower, upper)。

    双亲 = {p_{n-1}/q_{n-1}, (p_n − p_{n-1})/(q_n − q_{n-1})}，满足 unimodular 与
    分母和 = q；n 为奇数时前者在下，n 为偶数时后者在下。
    """
    cf = cf_frac(p, q)
    assert len(cf) >= 2
    n = len(cf) - 1
    p0, q0, p1, q1 = 1, 0, 0, 1
    conv = []
    for a in cf:
        p0, q0, p1, q1 = a * p0 + p1, a * q0 + q1, p0, q0
        conv.append((p0, q0))
    pn1, qn1 = conv[n - 1]
    other = (p - pn1, q - qn1)
    assert other[1] > 0
    if n % 2 == 1:
        return (pn1, qn1), other
    return other, (pn1, qn1)


def mediant(a, b):
    return F(a[0] + b[0], a[1] + b[1])


def unimodular(a, b):
    return abs(a[0] * b[1] - a[1] * b[0]) == 1


def farey_lower_bound(u, s):
    """由 unimodular 括号 (u, s)（u、s 为 (分子, 分母)）给出的分母下界：q >= q_u + q_s。

    证明：对任意 p/q ∈ (u, s)：p/q − u >= 1/(q·q_u)，s − p/q >= 1/(q·q_s)，
    相加得 s − u = 1/(q_u·q_s) >= (q_u + q_s)/(q·q_u·q_s)，即 q >= q_u + q_s。
    """
    assert unimodular(u, s)
    return u[1] + s[1]


def semiconv_list_frontier(A_digits, B_digits, k, cap_q=None):
    """G2 式清单：{[A_0;...;A_{j-1}, m] : 1 <= j <= k+1, 1 <= m <= A_j}
    ∪ 对 B 同型。返回 (值, 出处) 列表。

    项 [S_0;...;S_{j-1}, m] = (m p_{j-1} + p_{j-2})/(m q_{j-1} + q_{j-2})（标准收敛子递推），
    其分母关于 m 严格递增；cap_q 给定时只保留分母 < cap_q 的项（对「最小分母 < cap_q 的项
    必在清单内」这一完备性用法无损：目标项的分母 < cap_q，故其 m 落在被列出的前缀内）。
    """
    out = []
    for tag, S in (("alpha", A_digits), ("beta", B_digits)):
        conv = [(0, 1), (1, 0)]          # p_{-2}/q_{-2}, p_{-1}/q_{-1}
        for a in S:
            conv.append((a * conv[-1][0] + conv[-2][0], a * conv[-1][1] + conv[-2][1]))
        for j in range(1, min(k + 2, len(S))):
            aj = S[j]
            pj1, qj1 = conv[j + 1]       # p_{j-1}/q_{j-1}
            pj2, qj2 = conv[j]           # p_{j-2}/q_{j-2}
            for m in range(1, aj + 1):
                num = m * pj1 + pj2
                den = m * qj1 + qj2
                if cap_q is not None and den >= cap_q:
                    break
                out.append((F(num, den), (tag, j, m)))
    return out
