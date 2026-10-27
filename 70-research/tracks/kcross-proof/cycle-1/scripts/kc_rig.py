#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kcross-proof 轨道第 1 轮第 4 路：严格有理区间库（自足实现）。

来源与改动声明：本文件是 70-research/cycle-2/scripts/c2r5_rig.py 的复制件
（复制时原件 md5 = 350fc6b97222ba4fa0cff05377eba505，439 行）。改动只有两处，
都是为了口径压力测试（本轨道第 4 路任务 d）：

  1. A_of 与 eps_bounds 增加可选参数 X0（默认 None 时退回模块级 X0_INT，
     与原件行为逐位一致）；这样同一套区间算术可以跑 695*2^60 与 704*2^60 两种口径。
  2. 新增 C_from_x0(x0int, N)：任意整数 X0 的 C = log2((162/97)X0) 严格区间，
     走 ln_bounds 路线（原件 C_bounds 是把 695 情形写成专门的 atanh 分解）。
  3. pow_2vm1_delta 增加 v_lo < 3 的小 v 直路分支（2026 年 10 月 28 日，补丁）：
     原件在 u = 2^{-v} 接近 1 时级数界失效，会在外层触发「除零区间」断言。
     对所有 v >= 3 的调用（既有一切日志涉及的路径）逐行不变。

原有的 delta_bounds / exp_bounds / pow_bounds / geom_bounds / v_bounds /
feasible_decision / simplest_fraction / certified_prefix 一律未改。

记法与出处见 70-research/cycle-2/route-5.md 第 2 节（定义表）。
"""
from fractions import Fraction as F

GRID = 10 ** 100


def fl(x):
    return F(x).numerator // F(x).denominator


def ce(x):
    x = F(x)
    return -((-x.numerator) // x.denominator)


def rd(x):
    """向下取整到 1/GRID 的网格（保持下界性质）。"""
    return F(fl(F(x) * GRID), GRID)


def ru(x):
    """向上取整到 1/GRID 的网格（保持上界性质）。"""
    return F(ce(F(x) * GRID), GRID)


# ---------- 基本区间运算（端点均为 GRID 网格倍数） ----------

def iv_add(a, b):
    return (rd(a[0] + b[0]), ru(a[1] + b[1]))


def iv_sub(a, b):
    return (rd(a[0] - b[0]), ru(a[1] - b[1]))


def iv_mul(a, b):
    ps = [a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]]
    return (rd(min(ps)), ru(max(ps)))


def iv_div(a, b):
    assert not (b[0] <= 0 <= b[1]), "除零区间"
    ps = [a[0] / b[0], a[0] / b[1], a[1] / b[0], a[1] / b[1]]
    return (rd(min(ps)), ru(max(ps)))


def iv_pow(a, n):
    """非负整数幂。"""
    assert n >= 0
    lo = F(a[0]) ** n
    hi = F(a[1]) ** n
    return (rd(lo), ru(hi))


# ---------- 级数界 ----------

def atanh_bounds(x, N=None, tol=F(1, 10 ** 95), Nmax=800):
    """atanh(x) 的严格界，0 < x < 1（x 为有理数）。
    atanh(x) = sum_{k>=0} x^{2k+1}/(2k+1)；第 k 项之后的尾界
    x^{2k+3}/((2k+3)(1-x^2))。N 为 None 时按 tol 自适应取项数。"""
    x = F(x)
    assert 0 < x < 1
    x2 = x * x
    s = F(0)
    p = x                      # p = x^(2k+1)
    k = 0
    while True:
        s += p / (2 * k + 1)
        tail = p * x2 / ((2 * k + 3) * (1 - x2))
        if N is not None:
            if k >= N:
                break
        else:
            if tail <= tol or k >= Nmax:
                break
        p *= x2
        k += 1
    return rd(s), ru(s + tail)


_CACHE = {}


def ln2_bounds(N=400):
    """ln2 = 2 atanh(1/3)。"""
    if N in _CACHE:
        return _CACHE[N]
    lo, hi = atanh_bounds(F(1, 3), N)
    _CACHE[N] = (rd(2 * lo), ru(2 * hi))
    return _CACHE[N]


def ln3_bounds(N=400):
    """ln3 = ln2 + ln(3/2) = ln2 + 2 atanh(1/5)（与项目 r4x_rig_helpers 的
    atanh(1/2) 路线不同，可作独立对照）。"""
    if ("l3", N) in _CACHE:
        return _CACHE[("l3", N)]
    a = ln2_bounds(N)
    b = atanh_bounds(F(1, 5), N)
    _CACHE[("l3", N)] = (rd(a[0] + 2 * b[0]), ru(a[1] + 2 * b[1]))
    return _CACHE[("l3", N)]


def delta_bounds(N=400):
    """delta = ln3/ln2 的严格区间。"""
    if ("d", N) in _CACHE:
        return _CACHE[("d", N)]
    a = ln2_bounds(N)
    b = ln3_bounds(N)
    _CACHE[("d", N)] = (rd(b[0] / a[1]), ru(b[1] / a[0]))
    return _CACHE[("d", N)]


def ln_bounds(x, N=None):
    """ln(x) 的严格界（x > 0 有理数）：x = 2^k m, m in [1,2)，
    ln m = 2 atanh((m-1)/(m+1))，(m-1)/(m+1) in [0, 1/3]。"""
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


def exp_bounds(y_lo, y_hi, terms=70):
    """exp 的严格界，要求 0 < y_lo <= y_hi。
    先按 2 的幂缩至 [0,1]，Taylor 加尾界，再平方回代。"""
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
    plo = phi = F(1)
    fact = F(1)
    for i in range(terms + 1):
        if i > 0:
            fact *= i
            plo *= tl
            phi *= th
        lo += rd(plo / fact)
        hi += ru(phi / fact)
    # 尾界：sum_{i>terms} t^i/i! <= t^{terms+1}/(terms+1)! /(1 - t/(terms+2))
    fact *= (terms + 1)
    tail = th ** (terms + 1) / fact / (1 - th / (terms + 2))
    hi += tail
    for _ in range(s):
        lo, hi = rd(lo * lo), ru(hi * hi)
    return rd(lo), ru(hi)


def pow_bounds(b_lo, b_hi, e_lo, e_hi, N=None):
    """b^e 的严格界，b > 1，e > 0（对 b、e 单调增）。"""
    lb = ln_bounds(b_lo, N)
    hb = ln_bounds(b_hi, N)
    return exp_bounds(rd(F(e_lo) * lb[0]), ru(F(e_hi) * hb[1]))


def exp_any(y_lo, y_hi):
    """exp 的严格界，允许负参数（用 1/exp(-y) 走正值分支）。"""
    y_lo, y_hi = F(y_lo), F(y_hi)
    assert y_lo <= y_hi
    if y_lo >= 0:
        return exp_bounds(y_lo, y_hi) if y_hi > 0 else (F(1), F(1))
    if y_hi <= 0:
        a = exp_bounds(-y_hi, -y_lo)
        return iv_div((F(1), F(1)), a)
    lo = iv_div((F(1), F(1)), exp_bounds(-y_lo, -y_lo))[0]
    hi = exp_bounds(y_hi, y_hi)[1]
    return (rd(min(lo, F(1))), ru(max(hi, F(1))))


def _ln_one_minus_single(u, upper, tol, Jmax):
    """-ln(1-u) = sum_{j>=1} u^j/j 的单侧界（upper=True 取上界）。"""
    s = F(0)
    p = F(1)
    j = 1
    while True:
        p *= u
        s += p / j
        tail = p * u / ((j + 1) * (1 - u))
        if tail <= tol or j >= Jmax:
            break
        j += 1
    return ru(s + tail) if upper else rd(s)


def ln_one_minus_bounds(u_lo, u_hi, tol=F(1, 10 ** 110), Jmax=400):
    """ln(1-u) 的严格界，0 <= u_lo <= u_hi < 1（u_lo = 0 表示 2^{-v} 已在网格下溢出为 0，
    此时上界取 ln(1) = 0）。ln(1-u) 关于 u 递减：上界取 u_lo，下界取 u_hi。"""
    u_lo, u_hi = F(u_lo), F(u_hi)
    assert 0 <= u_lo <= u_hi < 1
    if u_lo == 0:
        return (-_ln_one_minus_single(u_hi, True, tol, Jmax), F(0))
    hi = -_ln_one_minus_single(u_lo, False, tol, Jmax)   # -(下界)
    lo = -_ln_one_minus_single(u_hi, True, tol, Jmax)    # -(上界)
    return (rd(lo), ru(hi))


def pow_2vm1_delta(v_lo, v_hi, d_lo, d_hi, l2):
    """(2^v - 1)^delta 的严格区间，v in [v_lo, v_hi] ⊂ (0, ∞)，delta in [d_lo, d_hi]。

    恒等式：2^v - 1 = 2^v (1 - 2^{-v})，故 (2^v-1)^delta = 2^{v delta} (1 - 2^{-v})^delta。
    两个因子都关于 v 与 delta 单调增，故取端点值即为区间。
    本式避免对 ~1e22 量级的底数取对数（那会强迫 atanh 级数取上百项）。

    小 v 分支（kcross-proof 第 1 轮第 4 路新增，2026 年 10 月 28 日）：
    恒等式路线的第二因子 (1 - 2^{-v})^delta 在 u = 2^{-v} 接近 1（即 v 小）时，
    ln_one_minus_bounds 按 u 展开的级数收敛极慢，Jmax = 400 截断后区间极宽，
    经 exp 后下端在 10^-100 网格下舍入为 0，使外层 iv_div 的除零断言触发。
    v_lo < 3 时改走直路：先严格夹 2^v - 1，再对底数与指数取四角。
    该分支只在调用者把 eps 用在「不可行」m2 上时才会被激活；对所有 v >= C（可行）
    的调用，下面的恒等式路线逐行与原件相同。"""
    l2lo, l2hi = l2
    if v_lo < 3:
        tv = exp_bounds(rd(F(v_lo) * l2lo), ru(F(v_hi) * l2hi))
        t = (rd(tv[0] - 1), ru(tv[1] - 1))
        assert t[0] > 0, "pow_2vm1_delta：v_lo 过小，2^v - 1 在 10^-100 网格下退化"
        lb = ln_bounds(t[0])
        hb = ln_bounds(t[1])
        cand = [F(d_lo) * lb[0], F(d_lo) * hb[1],
                F(d_hi) * lb[0], F(d_hi) * hb[1]]
        return exp_any(rd(min(cand)), ru(max(cand)))
    # 因子一：2^{v delta}
    f1 = exp_bounds(rd(F(v_lo) * F(d_lo) * l2lo), ru(F(v_hi) * F(d_hi) * l2hi))
    # 因子二：(1 - u)^delta, u = 2^{-v} ∈ [u_lo, u_hi]
    u = exp_any(ru(-F(v_hi) * l2hi), ru(-F(v_lo) * l2lo))
    L = ln_one_minus_bounds(u[0], u[1])          # [Llo, Lhi] ⊂ (-1, 0]
    assert L[1] <= 0
    z_lo = rd(F(d_hi) * L[0])                    # δ 取上端、L 取下端时取最小
    z_hi = ru(F(d_lo) * L[1])                    # δ 取下端、L 取上端时取最大
    f2 = exp_any(z_lo, z_hi)
    return iv_mul(f1, f2)


# ---------- 定理 21 的量 ----------

X0_INT = 695 * 2 ** 60
V0_COARSE = 5000          # v >= 5000 时走粗糙分支（2^v 不可直接表示）


def C_bounds(N=400):
    """C = log2((162/97) X0) = 60 + ln(112590/97)/ln2 的严格区间（X0 = 695*2^60）。

    ln(112590/97) = -2 ln2 + 6 ln3 + 2 atanh(1/9) + 2 atanh(56/83) - 2 atanh(1/193)，
    由 112590 = 2*3^4*5*139、139 = 27*(139/27)、97 = 96*(97/96)、5 = 4*(5/4) 分解而得。
    """
    l2 = ln2_bounds(N)
    l3 = ln3_bounds(N)
    a9 = atanh_bounds(F(1, 9), N)
    a83 = atanh_bounds(F(56, 83), N)
    a193 = atanh_bounds(F(1, 193), N)
    lo = -2 * l2[1] + 6 * l3[0] + 2 * a9[0] + 2 * a83[0] - 2 * a193[1]
    hi = -2 * l2[0] + 6 * l3[1] + 2 * a9[1] + 2 * a83[1] - 2 * a193[0]
    return rd(60 + lo / l2[1]), ru(60 + hi / l2[0])


def C_from_x0(x0int, N=400):
    """C = log2((162/97) X0) 的严格区间，任意正整数 X0（走 ln_bounds 路线）。

    与 C_bounds（695 专用 atanh 分解）互为独立对照。"""
    if ("Cx", x0int, N) in _CACHE:
        return _CACHE[("Cx", x0int, N)]
    l2 = ln2_bounds(N)
    num = ln_bounds(F(162 * x0int), N)
    den = ln_bounds(F(97), N)
    val = (rd((num[0] - den[1]) / l2[1]), ru((num[1] - den[0]) / l2[0]))
    _CACHE[("Cx", x0int, N)] = val
    return val


def pow_monotone(dlo, dhi, n):
    """delta^n 的严格区间，delta in [dlo, dhi] ⊂ (0, ∞)（n >= 0 整数）。
    单调性 + 每步定向取整的二进制幂：低路每步向下取整，高路每步向上取整。"""
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


def geom_bounds(m2, dlo, dhi):
    """((delta^m2 - 1)/(delta - 1)) 的区间，delta in [dlo, dhi]。"""
    pw = pow_monotone(dlo, dhi, m2)
    num = (rd(pw[0] - 1), ru(pw[1] - 1))
    den = (rd(dlo - 1), ru(dhi - 1))
    return iv_div(num, den)


def v_exact(m2, m, K, d):
    """v = (m2/m) K (delta-1)/(delta^m2 - 1) 在 delta = d 处的精确有理值。"""
    return F(m2, m) * F(K) * (F(d) - 1) / (F(d) ** m2 - 1)


def v_bounds(m2, m, K, dlo, dhi):
    """v 的严格区间。四角法则：分子 (delta-1) ∈ [dlo-1, dhi-1]，
    分母 (delta^m2 - 1) ∈ [plo-1, phi-1]（由 pow_monotone 定向估计），系数 (m2/m)K > 0。
    另注（报告引理）：v 关于 delta 严格递减（m2 >= 2）；
    证明：d/dd[(d-1)/(d^n-1)] 的分子 h(d) = d^n(1-n) + n d^{n-1} - 1，
    h(1) = 0 且 h'(d) = n(n-1)d^{n-2}(1-d) < 0（d > 1），故 h < 0。"""
    pw = pow_monotone(dlo, dhi, m2)
    num = (rd(dlo - 1), ru(dhi - 1))
    den = (rd(pw[0] - 1), ru(pw[1] - 1))
    assert den[0] > 0
    ps = [num[0] / den[0], num[0] / den[1], num[1] / den[0], num[1] / den[1]]
    c = F(m2, m) * F(K)
    return (rd(c * min(ps)), ru(c * max(ps)))


def A_of(m2, m, X0=None):
    """定理 21 与第 14 页证明末段的 A(m2)：m2 = m 取 0，m2 = m-1 取 3/X0，
    其余取 (97(m-m2)+73)/(54 X0)。X0 默认模块级 X0_INT（695*2^60）。"""
    X = X0_INT if X0 is None else F(X0)
    if m2 == m:
        return F(0)
    if m2 == m - 1:
        return F(3, X)
    return F(97 * (m - m2) + 73, 54 * X)


def eps_bounds(m2, m, K, dlo, dhi, l2, N=None, X0=None):
    """eps(m2, m, K) 的严格区间（定理 21 的界，含 (2^v - 1)^delta 的指数位置）。"""
    A = A_of(m2, m, X0)
    vl, vh = v_bounds(m2, m, K, dlo, dhi)
    if vl >= V0_COARSE:
        # v 极大时 2^v 不可表示；用单调性给出严格而粗糙的区间：
        # num = A + 3/(2^v-1) + 3(m2-1)/(2^v-1)^delta ∈ [A, A + (3 + 3(m2-1))/(2^V0-1)]
        # （2^v - 1 >= 2^V0 - 1，且 (2^v-1)^delta >= 2^v - 1，因为 delta > 1）
        slack = F(3 + 3 * (m2 - 1), 2 ** V0_COARSE - 1)
        num = (rd(A), ru(A + slack))
        den = iv_mul((F(3 * K), F(3 * K)), l2)
        return iv_div(num, den)
    two_v = exp_bounds(rd(vl * l2[0]), ru(vh * l2[1]))
    t = (rd(two_v[0] - 1), ru(two_v[1] - 1))
    assert t[0] > 0
    term1 = iv_div((F(3), F(3)), t)
    pt = pow_2vm1_delta(vl, vh, dlo, dhi, l2)
    term2 = iv_div((F(3 * (m2 - 1)), F(3 * (m2 - 1))), pt)
    num = (rd(A + term1[0] + term2[0]), ru(A + term1[1] + term2[1]))
    den = iv_mul((F(3 * K), F(3 * K)), l2)
    return iv_div(num, den)


def feasible_decision(m2, m, K, dlo, dhi, Civ):
    """定理 21 的可行性：geom(m2)*C <= (m2/m)K。返回 True / False / None（未定）。"""
    g = geom_bounds(m2, dlo, dhi)
    lhs = iv_mul(g, Civ)
    rhs = F(m2, m) * F(K)
    if lhs[1] <= rhs:
        return True
    if lhs[0] > rhs:
        return False
    return None


def A_bounds_int():
    """atanh 形参表（供脚本直接打印）。"""
    return None


# ---------- Stern-Brocot：区间内最小分母 ----------

def simplest_fraction(A, B, cap=400):
    """返回 (p, q)：区间 (A, B) 内分母最小的分数（A, B 为有理数，A < B）。

    算法：Stern-Brocot 下降，但从 0/1 与 1/0 出发时对每一侧做「整段跳」：
    左端保持 x/y、右端 z/w，先取最大的 k 使 (x + k z)/(y + k w) <= A 并整段跳过去
    （k = floor((A y - x)/(z - A w))，由 z/w > B > A 知分母为正），
    再对称地对右端跳；当某一步的中项严格落在 (A, B) 内即返回。

    最小性证明（本报告引理的算法版本）：
    每一步的括号端点满足 unimodular（z y - x w = 1，初值 1*1 - 0*0 = 1，
    跳段与单步都保号）。对括号内任意分数 p/q，由
    p/q - x/y >= 1/(q y) 与 z/w - p/q >= 1/(q w) 相加得
    1/(y w) = z/w - x/y >= (y + w)/(q y w)，即 q >= y + w；
    而返回时中项的分母恰为 y + w 且中项在区间内，故它就是最小分母。"""
    A, B = F(A), F(B)
    assert A < B
    x, y, z, w = 0, 1, 1, 0
    for _ in range(cap):
        # 左跳：最大 k >= 1 使 (x + kz)/(y + kw) <= A
        kL = fl((A * y - x) / (z - A * w))
        if kL >= 1:
            x, y = x + kL * z, y + kL * w
        # 右跳：最大 k >= 1 使 (z + kx)/(w + ky) >= B
        kR = fl((z - B * w) / (B * y - x))
        if kR >= 1:
            z, w = z + kR * x, w + kR * y
        mn, md = x + z, y + w
        m = F(mn, md)
        if A < m < B:
            return m
    raise RuntimeError("Stern-Brocot 未在 %d 段内收敛" % cap)


def cf_value(quot):
    """连分数串 [q0; q1, ...] 的精确值。"""
    v = F(0)
    for a in reversed(quot):
        v = F(a) + (F(0) if v == 0 else 1 / v)
    return v


def certified_prefix(x_lo, x_hi, maxlen=300):
    """返回 digits：保证 [x_lo, x_hi] 内每一点的连分数展开前 len(digits) 位等于 digits。

    依据：每步要求 floor(lo) = floor(hi) = n 且 lo > n（严格），
    高斯映射 x -> 1/(x - n) 在 (n, n+1) 上连续递减。"""
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
