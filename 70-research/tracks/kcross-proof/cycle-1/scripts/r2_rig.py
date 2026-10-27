#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kcross-proof 第 1 轮第 2 路：阈值侧证书专用的独立严格有理区间库。

与 70-research/cycle-2/scripts/c2r5_rig.py（下称原库）的差异，逐条：
  1. 网格 GRID = 10**200（原库 10**100）；
  2. ln2 走 -ln(1-1/2) = sum_{j>=1} (1/2)^j/j（原库走 2*atanh(1/3)）；
  3. ln3 走 ln2 + (-ln(1-1/3)) = ln2 + sum_{j>=1} (1/3)^j/j（原库走 ln2 + 2*atanh(1/5)）；
  4. C = log2((162/97)X0) 走 ln((162/97)X0)/ln2 的直接路线（原库走 60 + ln(112590/97)/ln2
     的定制 atanh 分解）；
  5. (2^v - 1)^delta 走「先给 2^v - 1 的区间，再取 ln 与 exp」的两步路线
     （原库走 2^{v delta}(1-2^{-v})^delta 的恒等分解）。
不变的部分：定理 21 各量的区间语义（四角法则对 v 与 geom、对 m2 的单调性、
可行性的三值判定）、Stern-Brocot 的连分数前缀证书。

严格性约定：每个函数返回的区间 [lo, hi] 满足「对区间内一切真值，真值 ∈ [lo, hi]」；
一切取整用 rd（向下）与 ru（向上）到 GRID 网格；级数一律附显式尾项界。
所有判定在调用方用 Fraction 精确完成。
"""
from fractions import Fraction as F

GRID = 10 ** 200

# ---------- 网格取整 ----------


def fl(x):
    x = F(x)
    return x.numerator // x.denominator


def ce(x):
    x = F(x)
    return -((-x.numerator) // x.denominator)


def rd(x):
    """向下取整到 1/GRID 网格（保持下界性质）。"""
    return F(fl(F(x) * GRID), GRID)


def ru(x):
    """向上取整到 1/GRID 网格（保持上界性质）。"""
    return F(ce(F(x) * GRID), GRID)


# ---------- 区间四则 ----------


def iv_add(a, b):
    return (rd(a[0] + b[0]), ru(a[1] + b[1]))


def iv_sub(a, b):
    return (rd(a[0] - b[1]), ru(a[1] - b[0]))


def iv_mul(a, b):
    ps = [a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]]
    return (rd(min(ps)), ru(max(ps)))


def iv_div(a, b):
    assert not (b[0] <= 0 <= b[1]), "除零区间"
    ps = [a[0] / b[0], a[0] / b[1], a[1] / b[0], a[1] / b[1]]
    return (rd(min(ps)), ru(max(ps)))


# ---------- 对数：两条与 c2r5_rig 不同的级数路线 ----------
# 引理（初等）：对 0 < u < 1，-ln(1-u) = sum_{j>=1} u^j/j，
# 且第 N 项之后的尾和 <= u^{N+1}/((N+1)(1-u))（几何级数逐项放大）。


def _neg_ln1mu(u, N):
    """返回 (-ln(1-u)) 的严格界，0 < u < 1（u 为精确有理数）。

    逐项累加时把幂保持在网格上（下路每步 rd、上路每步 ru），避免
    分数规模随项数线性膨胀。"""
    u = F(u)
    assert 0 < u < 1
    lo = F(0)
    hi = F(0)
    pl, ph = rd(u), ru(u)          # pl <= u^j <= ph
    for j in range(1, N + 1):
        lo = rd(lo + pl / j)
        hi = ru(hi + ph / j)
        pl = rd(pl * u)
        ph = ru(ph * u)
    tail = ru(ph * u / ((N + 1) * (1 - u)))
    return lo, ru(hi + tail)


_CACHE = {}


def ln2_bounds(N=800):
    """ln2 = -ln(1-1/2)。u = 1/2 的尾界在 N = 800 时约 2^{-801}/800。"""
    key = ("ln2", N)
    if key not in _CACHE:
        _CACHE[key] = _neg_ln1mu(F(1, 2), N)
    return _CACHE[key]


def ln3_bounds(N=520):
    """ln3 = ln2 + (-ln(1-1/3))。"""
    key = ("ln3", N)
    if key not in _CACHE:
        a = ln2_bounds(900)
        b = _neg_ln1mu(F(1, 3), N)
        _CACHE[key] = (rd(a[0] + b[0]), ru(a[1] + b[1]))
    return _CACHE[key]


def delta_bounds(N=520):
    """delta = ln3/ln2（ln2 > 0，区间除法保持包含）。"""
    key = ("delta", N)
    if key not in _CACHE:
        a = ln2_bounds(900)
        b = ln3_bounds(N)
        _CACHE[key] = (rd(b[0] / a[1]), ru(b[1] / a[0]))
    return _CACHE[key]


# ---------- 一般对数（atanh 路线）与指数 ----------


def _atanh_bounds(t, N):
    """atanh(t) = sum_{j>=0} t^{2j+1}/(2j+1)，0 <= t <= 1/3；
    尾界 <= t^{2N+3}/((2N+3)(1-t^2))。"""
    t = F(t)
    assert 0 <= t < 1
    if t == 0:
        return F(0), F(0)
    t2 = t * t
    lo = F(0)
    hi = F(0)
    pl, ph = rd(t), ru(t)          # pl <= t^{2j+1} <= ph
    for j in range(N + 1):
        lo = rd(lo + pl / (2 * j + 1))
        hi = ru(hi + ph / (2 * j + 1))
        pl = rd(pl * t2)
        ph = ru(ph * t2)
    tail = ru(ph * t2 / ((2 * N + 3) * (1 - t2)))
    return lo, ru(hi + tail)


def ln_bounds(x, N=280):
    """ln(x) 的严格界，x > 0 有理数。

    x = 2^k m，m ∈ [1,2)，t = (m-1)/(m+1) ∈ [0,1/3]，
    ln x = k ln2 + 2 atanh(t)。x < 1 时用 ln(1/x) 取负（区间反向）。"""
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
    m = x / F(2) ** k
    t = (m - 1) / (m + 1)
    a = _atanh_bounds(t, N)
    l2 = ln2_bounds(900)
    return (rd(k * l2[0] + 2 * a[0]), ru(k * l2[1] + 2 * a[1]))


def exp_bounds(y_lo, y_hi, N=210):
    """exp 的严格界，0 <= y_lo <= y_hi。

    先把 y 除以 2^s 缩到 [0,1]，Taylor 部分和加尾界，
    再平方 s 次（下界一路 rd、上界一路 ru）。
    尾界：sum_{i>N} t^i/i! <= t^{N+1}/(N+1)! / (1 - t/(N+2))，t <= 1。"""
    y_lo, y_hi = F(y_lo), F(y_hi)
    assert 0 <= y_lo <= y_hi
    if y_hi == 0:
        return (F(1), F(1))
    s = 0
    while F(2) ** s < y_hi:
        s += 1
    tl, th = y_lo / F(2) ** s, y_hi / F(2) ** s
    lo = F(0)
    hi = F(0)
    pl = F(1)                      # pl <= t^i <= ph（幂保持在网格上）
    ph = F(1)
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


def exp_any(y_lo, y_hi):
    """exp 的严格界，允许负参数（负支走 1/exp(-y)）。"""
    y_lo, y_hi = F(y_lo), F(y_hi)
    assert y_lo <= y_hi
    if y_lo >= 0:
        return exp_bounds(y_lo, y_hi) if y_hi > 0 else (F(1), F(1))
    if y_hi <= 0:
        return iv_div((F(1), F(1)), exp_bounds(-y_hi, -y_lo))
    lo = iv_div((F(1), F(1)), exp_bounds(-y_lo, -y_lo))[0]
    hi = exp_bounds(y_hi, y_hi)[1]
    return (rd(min(lo, F(1))), ru(max(hi, F(1))))


def pow_real(b_iv, e_iv):
    """b^e 的严格界，b 区间端点均 > 1，e 区间端点均 > 0。
    b^e = exp(e ln b) 关于 b、e 都递增，故取下端对下端、上端对上端。"""
    assert b_iv[0] > 1 and e_iv[0] > 0
    lb = ln_bounds(b_iv[0])
    hb = ln_bounds(b_iv[1])
    return exp_bounds(rd(e_iv[0] * lb[0]), ru(e_iv[1] * hb[1]))


def pow_int_grid(dlo, dhi, n):
    """delta^n 的严格区间（n >= 0 整数，0 < dlo <= dhi）：定向取整的二进制幂。"""
    assert dlo > 0 and n >= 0

    def low(d):
        r = F(1)
        b = F(d)
        e = n
        while e:
            if e & 1:
                r = rd(r * b)
            e >>= 1
            if e:
                b = rd(b * b)
        return r

    def high(d):
        r = F(1)
        b = F(d)
        e = n
        while e:
            if e & 1:
                r = ru(r * b)
            e >>= 1
            if e:
                b = ru(b * b)
        return r

    return low(dlo), high(dhi)


# ---------- 定理 21 的量（区间语义与 (D2)(D3) 一致） ----------

X0_INT = 695 * 2 ** 60
V0_COARSE = 5000


def C_bounds():
    """C = log2((162/97) X0) 的严格区间：ln 路线，不写定制分解。"""
    key = ("C",)
    if key not in _CACHE:
        arg = F(162, 97) * X0_INT
        a = ln_bounds(arg)
        l2 = ln2_bounds(900)
        _CACHE[key] = (rd(a[0] / l2[1]), ru(a[1] / l2[0]))
    return _CACHE[key]


def A_of(m2, m):
    """Theorem 21 与第 14 页证明末段的 A(m2)。"""
    if m2 == m:
        return F(0)
    if m2 == m - 1:
        return F(3, X0_INT)
    return F(97 * (m - m2) + 73, 54 * X0_INT)


def geom_bounds(m2, dlo, dhi):
    """geom(m2) = (delta^m2 - 1)/(delta - 1)，四角法则。"""
    pw = pow_int_grid(dlo, dhi, m2)
    num = (rd(pw[0] - 1), ru(pw[1] - 1))
    den = (rd(dlo - 1), ru(dhi - 1))
    assert num[0] > 0 and den[0] > 0
    return (rd(num[0] / den[1]), ru(num[1] / den[0]))


def v_bounds(m2, m, K, dlo, dhi):
    """v = (m2/m) K (delta-1)/(delta^m2 - 1)，四角法则（分子、分母都为正）。"""
    pw = pow_int_grid(dlo, dhi, m2)
    num = (rd(dlo - 1), ru(dhi - 1))
    den = (rd(pw[0] - 1), ru(pw[1] - 1))
    assert den[0] > 0
    c = F(m2, m) * F(K)
    return (rd(c * num[0] / den[1]), ru(c * num[1] / den[0]))


def eps_bounds(m2, m, K, dlo, dhi, l2):
    """eps(m2, m, K) 的严格区间。

    eps = [ A(m2) + 3/(2^v - 1) + 3(m2-1)/(2^v - 1)^delta ] / (3 K ln2)。

    v >= V0_COARSE 时 2^v 不可直接表示，用单调性给粗界：
      3/(2^v-1) <= 3/(2^V0-1)，且 delta > 1 故 (2^v-1)^delta >= 2^v-1 >= 2^V0-1，
      于是 3(m2-1)/(2^v-1)^delta <= 3(m2-1)/(2^V0-1)。"""
    A = A_of(m2, m)
    vl, vh = v_bounds(m2, m, K, dlo, dhi)
    if vl >= V0_COARSE:
        slack = F(3 + 3 * (m2 - 1), 2 ** V0_COARSE - 1)
        num = (rd(A), ru(A + slack))
    else:
        two_v = exp_bounds(rd(vl * l2[0]), ru(vh * l2[1]))
        t = (rd(two_v[0] - 1), ru(two_v[1] - 1))
        assert t[0] > 1
        term1 = iv_div((F(3), F(3)), t)
        pt = pow_real(t, (dlo, dhi))
        term2 = iv_div((F(3 * (m2 - 1)), F(3 * (m2 - 1))), pt)
        num = (rd(A + term1[0] + term2[0]), ru(A + term1[1] + term2[1]))
    den = iv_mul((F(3 * K), F(3 * K)), l2)
    return iv_div(num, den)


def feasible_decision(m2, m, K, dlo, dhi, Civ):
    """Theorem 21 可行性 geom(m2) C <= (m2/m) K。返回 True / False / None。"""
    g = geom_bounds(m2, dlo, dhi)
    lhs = iv_mul(g, Civ)
    rhs = F(m2, m) * F(K)
    if lhs[1] <= rhs:
        return True
    if lhs[0] > rhs:
        return False
    return None


# ---------- 连分数：前缀证书与收敛分数 ----------


def certified_prefix(x_lo, x_hi, maxlen=400):
    """返回 digits：保证 [x_lo, x_hi] 内每一点的连分数展开前 len(digits) 位等于 digits。

    依据：每步要求 floor(lo) = floor(hi) = n 且 lo > n（严格），
    高斯映射 x -> 1/(x-n) 在 (n, n+1) 上连续递减，故新区间取
    [1/(hi-n) 向下取整, 1/(lo-n) 向上取整] 仍包含一切象。"""
    digits = []
    lo, hi = F(x_lo), F(x_hi)
    for _ in range(maxlen):
        n = fl(lo)
        if fl(hi) != n:
            break
        if lo == n:
            break
        digits.append(n)
        lo, hi = rd(1 / (hi - n)), ru(1 / (lo - n))
    return digits


def convergents(digits):
    """连分数串的收敛分数表 [(i, p, q)]（q 为分母）。"""
    p_m2, p_m1 = 0, 1
    q_m2, q_m1 = 1, 0
    out = []
    for i, a in enumerate(digits):
        p = a * p_m1 + p_m2
        q = a * q_m1 + q_m2
        out.append((i, p, q))
        p_m2, p_m1 = p_m1, p
        q_m2, q_m1 = q_m1, q
    return out


def cf_value(quot):
    """连分数串 [q0; q1, ...] 的精确值。"""
    v = F(0)
    for a in reversed(list(quot)):
        v = F(a) + (F(0) if v == 0 else 1 / v)
    return v


# ---------- 打印工具 ----------


def dec_str(x, ndig):
    """精确有理数的十进制截断（截断，不是四舍五入）。"""
    x = F(x)
    sgn = "-" if x < 0 else ""
    x = abs(x)
    ip = x.numerator // x.denominator
    rem = x.numerator - ip * x.denominator
    out = [sgn + str(ip), "."]
    for _ in range(ndig):
        rem *= 10
        d = rem // x.denominator
        out.append(str(d))
        rem -= d * x.denominator
    return "".join(out)


def frac_str(x):
    x = F(x)
    return "%d/%d" % (x.numerator, x.denominator)


def sci(x, nd=12):
    """对数量级的科学记数打印（截断到 nd 位有效数字，仅用于显示）。"""
    x = F(x)
    if x == 0:
        return "0"
    sgn = "-" if x < 0 else ""
    x = abs(x)
    e = 0
    while x >= 10:
        x /= 10
        e += 1
    while x < 1:
        x *= 10
        e -= 1
    return "%s%s e%+d" % (sgn, dec_str(x, nd), e)
