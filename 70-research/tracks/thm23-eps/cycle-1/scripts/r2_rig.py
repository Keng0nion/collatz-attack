#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r2_rig.py：route-2「ε 的严格有理区间证书」自足严格区间库（判决路径）。

纪律（写死在本文件里，供复核）：
1. 只 import 标准库 fractions。不 import、不读 70-research/cycle-1 与
   70-research/cycle-2 下的任何脚本或输出（那些只在 r2_run3.py 的交叉验证里
   被调用，且只调用、不修改）。
2. 一切超越量的上下界都由「有理级数部分和 + 显式尾界」给出；
   中间结果按 10 的 -160 次幂网格做定向取整（下界向下、上界向上），
   取整本身不破坏包含性（floor(x) <= x <= ceil(x)）。
3. 判定一律走精确有理比较；本文件不含任何浮点运算（打印也走十进制截断）。

数学依据（每条都在报告里给出证明或出处）：
   ln 2 = 2 atanh(1/3)                                     （标准恒等式）
   ln 3 = 2 atanh(1/2)                                     （标准恒等式，与环内既有实现不同参数）
   atanh(x) = sum_{k>=0} x^{2k+1}/(2k+1)，尾界
       0 <= 余项 <= x^{2n+1}/((2n+1)(1-x^2))
   ln(x) 对有理 x > 0：x = 2^k m，m in [1,2)，ln m = 2 atanh((m-1)/(m+1))
   ln(1-u) = -sum_{i>=1} u^i/i，尾界 0 <= 余项 <= u^{n+1}/((n+1)(1-u))
   exp(y)（y in [ylo, yhi]）：移位 z = y/2^J in [0, 1/2]，
       部分和 + 尾界 z^{n+1}/((n+1)!(1-z/(n+2)))，再平方 J 次
   2^v - 1 = 2^v (1 - 2^{-v})， (2^v-1)^delta 的两条独立路线：
       (a) exp(delta * ln(2^v - 1))（直接，用大整数的 ln）
       (b) 2^{v delta} * (1 - 2^{-v})^delta（恒等式，避开取大数的对数）
"""

from fractions import Fraction as F

GRID = 10 ** 160        # 绝对网格（PREC = None 时生效）
PREC = None             # 若为整数 n：改用相对网格，每量保留 n 位有效数字


def _step(x):
    """定向取整用的网格步长：PREC 为 None 时是 1/GRID，否则是 10^{-PREC} 乘量级。"""
    if PREC is None:
        return F(1, GRID)
    ax = abs(F(x))
    if ax == 0:
        return F(1, GRID)
    e = ax.numerator.bit_length() - ax.denominator.bit_length()
    t = F(10) ** e
    while t > ax:
        t /= 10
        e -= 1
    while t * 10 <= ax:
        t *= 10
        e += 1
    return t * F(10) ** (-PREC)


# ---------- 定向取整（网格） ----------

def rd(x):
    """向下取整到网格：结果 <= x。"""
    x = F(x)
    s = _step(x)
    q = x / s
    return F(q.numerator // q.denominator) * s


def ru(x):
    """向上取整到网格：结果 >= x。"""
    x = F(x)
    s = _step(x)
    q = x / s
    return F(-((-q.numerator) // q.denominator)) * s


def tighten(iv):
    return (rd(iv[0]), ru(iv[1]))


# ---------- 十进制打印（无浮点） ----------

def fmt_fixed(x, k):
    """向下截断到 k 位小数的十进制字符串（floor）。"""
    q = F(x) * 10 ** k
    q = q.numerator // q.denominator
    neg = q < 0
    q = abs(q)
    ip, fp = divmod(q, 10 ** k)
    return ("-" if neg else "") + str(ip) + ("." + str(fp).rjust(k, "0") if k else "")


def fmt_fixed_up(x, k):
    """向上截断到 k 位小数（ceil）。"""
    q = F(x) * 10 ** k
    q = -((-q.numerator) // q.denominator)
    neg = q < 0
    q = abs(q)
    ip, fp = divmod(q, 10 ** k)
    return ("-" if neg else "") + str(ip) + ("." + str(fp).rjust(k, "0") if k else "")


def dec_exp(x, k, up=False):
    """把正有理数 x 写成尾数加指数（s.ffff e±XX；k 位小数，up=True 时向上截断）。
    返回 (尾数字符串, 指数整数)。对 x > 0。"""
    x = F(x)
    assert x > 0
    t = F(1)
    e = 0
    if x >= 1:
        while x >= t * 10:
            t *= 10
            e += 1
    else:
        while x < t:
            t /= 10
            e -= 1
    m = x / t                     # 尾数在 [1, 10)
    s = fmt_fixed_up(m, k) if up else fmt_fixed(m, k)
    n = F(s)
    if n >= 10:                   # 向上截断进位到 10.000...
        s = fmt_fixed_up(n / 10, k)
        e += 1
    return s, e


def sci(x, k=25, up=False):
    s, e = dec_exp(x, k, up)
    return "%se%s%d" % (s, "+" if e >= 0 else "-", abs(e))


def show_iv(name, iv, k=25):
    return "%-22s [%s , %s]" % (name, sci(iv[0], k, up=False), sci(iv[1], k, up=True))


# ---------- 级数界：atanh、ln ----------

def atanh_bounds(x, n):
    """atanh(x) 的严格界，0 < x < 1 有理数，n 项部分和。
    尾项界：x^{2n+1}/((2n+1)(1-x^2))。"""
    x = F(x)
    assert 0 < x < 1
    x2 = x * x
    s = F(0)
    p = x
    for k in range(n):
        s += p / (2 * k + 1)
        p *= x2
    tail = p / ((2 * n + 1) * (1 - x2))
    return rd(s), ru(s + tail)


def ln2_bounds(n=90):
    """ln2 = 2 atanh(1/3)（x = 1/3，n 项：尾约 3^{-(2n+1)}）。"""
    lo, hi = atanh_bounds(F(1, 3), n)
    return rd(2 * lo), ru(2 * hi)


def ln3_bounds(n=230):
    """ln3 = 2 atanh(1/2)（(1+1/2)/(1-1/2) = 3）。n 项：尾约 2^{-(2n+1)}。"""
    lo, hi = atanh_bounds(F(1, 2), n)
    return rd(2 * lo), ru(2 * hi)


def delta_bounds(n2=90, n3=230):
    """delta = ln3/ln2 的严格区间（两个正的区间相除）。"""
    l2 = ln2_bounds(n2)
    l3 = ln3_bounds(n3)
    return rd(l3[0] / l2[1]), ru(l3[1] / l2[0])


def log2_int_pow(x):
    """floor(log2(x))，x 为正有理数：用整数比较，不用浮点。"""
    x = F(x)
    k = x.numerator.bit_length() - x.denominator.bit_length()
    while F(2) ** (k + 1) <= x:
        k += 1
    while F(2) ** k > x:
        k -= 1
    return k


def ln_bounds(x, n=90):
    """ln(x) 的严格界，x > 0 有理数。约化 x = 2^k m，m in [1,2)。"""
    x = F(x)
    assert x > 0
    if x == 1:
        return F(0), F(0)
    if x < 1:
        lo, hi = ln_bounds(1 / x, n)
        return -hi, -lo
    k = log2_int_pow(x)
    m = x / F(2) ** k                      # m in [1, 2)
    t = (m - 1) / (m + 1)                  # t in [0, 1/3)
    alo, ahi = atanh_bounds(t, n)
    l2 = ln2_bounds(n)
    if k >= 0:
        lo = k * l2[0] + 2 * alo
        hi = k * l2[1] + 2 * ahi
    else:
        lo = k * l2[1] + 2 * alo
        hi = k * l2[0] + 2 * ahi
    return rd(lo), ru(hi)


def ln_one_minus_bounds(ulo, uhi, n=80):
    """ln(1-u) 对 u in [ulo, uhi] ⊂ (0, 1) 的严格区间（递减函数）。"""
    ulo = F(ulo)
    uhi = F(uhi)
    assert 0 < ulo <= uhi < 1

    def part(u, m):
        s = F(0)
        p = u
        for i in range(1, m + 1):
            s += p / i
            p *= u
        return s, p                   # p = u^{m+1}

    shi, ph = part(uhi, n)
    tail = ph / ((n + 1) * (1 - uhi))
    lo = -(shi + tail)                # <= ln(1-uhi) <= ln(1-u)
    slo, _ = part(ulo, n)
    hi = -slo                         # >= ln(1-ulo) >= ln(1-u)
    return rd(lo), ru(hi)


# ---------- 级数界：exp 与 2^v ----------

def exp_pos_bounds(ylo, yhi, n=70):
    """exp(y) 对 0 <= ylo <= yhi 的严格界：返回 (lo, hi)，lo <= exp(ylo)，hi >= exp(yhi)。"""
    ylo = F(ylo)
    yhi = F(yhi)
    assert 0 <= ylo <= yhi
    J = 0
    while yhi / F(2) ** J > F(1, 2):
        J += 1
    zlo = ylo / F(2) ** J
    zhi = yhi / F(2) ** J

    def psum(z, m):
        s = F(0)
        term = F(1)
        for i in range(m + 1):
            s += term
            term = term * z / (i + 1)
        return s, term          # term = z^{m+1}/(m+1)!

    slo, _ = psum(zlo, n)
    shi, term_hi = psum(zhi, n)
    tail = term_hi * zhi / (n + 2) / (1 - zhi / (n + 2)) if zhi > 0 else F(0)
    # term_hi * zhi/(n+2) = zhi^{n+2}/(n+2)!；再乘 1/(1 - zhi/(n+2)) 得尾界
    upper = shi + tail

    lo = rd(slo)
    hi = ru(upper)
    for _ in range(J):
        lo = rd(lo * lo)
        hi = ru(hi * hi)
    return lo, hi


def exp_iv(ylo, yhi, n=70):
    """exp(y) 对 y in [ylo, yhi] 的严格区间（一般符号；要求 0 不在区间内或恰好为端点）。"""
    ylo = F(ylo)
    yhi = F(yhi)
    assert ylo <= yhi
    if ylo >= 0:
        return exp_pos_bounds(ylo, yhi, n)
    if yhi <= 0:
        lo, hi = exp_pos_bounds(-yhi, -ylo, n)
        return rd(1 / hi), ru(1 / lo)
    raise AssertionError("区间跨零，本库不支持")


# ---------- 定理 21 的各个量 ----------

X0_695 = 695 * 2 ** 60
X0_704 = 704 * 2 ** 60


def C_bounds(X0=X0_695, n=90):
    """C = log2((162/97) X0) 的严格区间。
    写法：(162/97) X0 = (162 X0/97)，取其对数 = ln(162 X0/97)/ln2。
    全走 ln_bounds（自我约化到 [1,2)），不用浮点。"""
    y = F(162, 97) * F(X0)
    ly = ln_bounds(y, n)
    l2 = ln2_bounds(n)
    return rd(ly[0] / l2[1]), ru(ly[1] / l2[0])


def pow_frac(lo, hi, k):
    """有理数区间 [lo, hi]（lo > 0）的整数幂 k >= 0：单调，取端点。"""
    assert F(lo) > 0
    return rd(F(lo) ** k), ru(F(hi) ** k)


def v_bounds(m2, m, K, dlo, dhi):
    """v = (m2/m) K (delta-1)/(delta^{m2}-1) 的严格区间。
    分子区间 [dlo-1, dhi-1] ⊂ (0, inf)，分母区间 [dlo^{m2}-1, dhi^{m2}-1] ⊂ (0, inf)，
    正除以正：商落在 [a1/b2, a2/b1]。"""
    num = (rd(F(dlo) - 1), ru(F(dhi) - 1))
    pw = pow_frac(dlo, dhi, m2)
    den = (rd(pw[0] - 1), ru(pw[1] - 1))
    assert num[0] > 0 and den[0] > 0
    c = F(m2, m) * F(K)
    return rd(c * num[0] / den[1]), ru(c * num[1] / den[0])


def two_v_bounds(vlo, vhi, l2):
    """2^v 对 v in [vlo, vhi]（正）的严格区间：2^v = exp(v ln2)。"""
    ylo = F(vlo) * F(l2[0])
    yhi = F(vhi) * F(l2[1])
    return exp_iv(ylo, yhi)


V_COARSE = 300       # v_lo 超过此值时 2^v 不可直接表示，走粗糙分支（见 eps_bounds）


def pow2vm1_delta_bounds(vlo, vhi, dlo, dhi, l2, route="a", n=90):
    """(2^v - 1)^delta 对 v in [vlo,vhi]、delta in [dlo,dhi] 的严格区间。

    route="a"：直接  exp(delta * ln(2^v - 1))，其中 ln(2^v-1) 用端点
               2^{vlo}-1、2^{vhi}-1 的对数区间（ln 单调）。
    route="b"：恒等式 2^v - 1 = 2^v (1 - 2^{-v})，
               (2^v-1)^delta = 2^{v delta} * (1 - 2^{-v})^delta。
    两条路线互补：报告里互为交叉验证。"""
    utter = two_v_bounds(vlo, vhi, l2)                 # 2^v ∈ [Elo, Ehi]
    if route == "a":
        # ln(2^v - 1) ∈ [ln(Elo - 1), ln(Ehi - 1)]（ln 单调；Elo - 1 > 0）
        assert utter[0] > 1
        q_lo = ln_bounds(utter[0] - 1, n)
        q_hi = ln_bounds(utter[1] - 1, n)
        # delta * ln(...)：两个正区间相乘，取四角
        prod_lo = rd(F(dlo) * q_lo[0])
        prod_hi = ru(F(dhi) * q_hi[1])
        return exp_iv(prod_lo, prod_hi)
    else:
        f1 = exp_iv(F(vlo) * F(dlo) * F(l2[0]), F(vhi) * F(dhi) * F(l2[1]))
        # u = 2^{-v} = 1/2^v ∈ [1/Ehi, 1/Elo]
        ulo = rd(1 / utter[1])
        uhi = ru(1 / utter[0])
        L = ln_one_minus_bounds(ulo, uhi)              # ⊂ (-1, 0]
        # delta * L：delta > 0，L < 0；min = dhi*Llo，max = dlo*Lhi
        zlo = rd(F(dhi) * L[0])
        zhi = ru(F(dlo) * L[1])
        assert zhi <= 0
        f2 = exp_iv(zlo, zhi)
        return rd(f1[0] * f2[0]), ru(f1[1] * f2[1])


def A_of(m2, m, X0=X0_695):
    """定理 21 与第 14 页证明末段的 A(m2)：精确有理值，不需要区间。"""
    if m2 == m:
        return F(0)
    if m2 == m - 1:
        return F(3, X0)
    return F(97 * (m - m2) + 73, 54 * X0)


def eps_bounds(m2, m, K, dlo, dhi, l2, X0=X0_695, route="a", k=1):
    """eps(m2, m, K) 的严格区间：
        eps = ( A(m2) + 3/(2^v - 1) + 3(m2-1)/(2^v - 1)^delta ) / (3 K ln 2)。
    返回 (iv, parts)，parts 里是各中间量的区间。"""
    A = A_of(m2, m, X0)
    v = v_bounds(m2, m, K, dlo, dhi)
    parts = {"A": A, "v": v}
    if v[0] >= V_COARSE:
        # 2^v 不可表示：用单调性给严格但粗糙的界
        # 3/(2^v-1) ∈ (0, 3/(2^{V_COARSE}-1)]，(2^v-1)^delta >= 2^v-1 => 第二项更小
        slack = F(3 + 3 * (m2 - 1), 2 ** V_COARSE - 1)
        num = (rd(A), ru(A + slack))
        parts["coarse"] = True
    else:
        t2v = two_v_bounds(v[0], v[1], l2)
        parts["2^v"] = t2v
        t = (rd(t2v[0] - 1), ru(t2v[1] - 1))
        assert t[0] > 0
        t1 = (rd(F(3) / t[1]), ru(F(3) / t[0]))
        parts["2^v-1"] = t
        parts["t1"] = t1
        T = pow2vm1_delta_bounds(v[0], v[1], dlo, dhi, l2, route=route)
        parts["(2^v-1)^delta"] = T
        t2 = (rd(F(3 * (m2 - 1)) / T[1]), ru(F(3 * (m2 - 1)) / T[0]))
        parts["t2"] = t2
        num = (rd(A + t1[0] + t2[0]), ru(A + t1[1] + t2[1]))
        parts["coarse"] = False
    den = (rd(F(3 * K) * F(l2[0])), ru(F(3 * K) * F(l2[1])))
    parts["den"] = den
    parts["num"] = num
    return (rd(num[0] / den[1]), ru(num[1] / den[0])), parts


def feasible_decision(m2, m, K, dlo, dhi, C, X0=X0_695):
    """定理 21 的前提 (delta^{m2}-1)/(delta-1) * C <= (m2/m) K：
    返回 True / False / "未定"。"""
    pw = pow_frac(dlo, dhi, m2)
    num = (rd(pw[0] - 1), ru(pw[1] - 1))
    den = (rd(F(dlo) - 1), ru(F(dhi) - 1))
    g = (rd(num[0] / den[1]), ru(num[1] / den[0]))
    lhs = (rd(g[0] * C[0]), ru(g[1] * C[1]))
    rhs = F(m2, m) * F(K)
    if lhs[1] <= rhs:
        return True
    if lhs[0] > rhs:
        return False
    return "未定"


def max_feasible_m2(m, K, dlo, dhi, C, X0=X0_695):
    """最大的可行 m2（论文链条读法），返回 (m2, 是否严格可行或未定判定同行)。"""
    for m2 in range(m, 0, -1):
        d = feasible_decision(m2, m, K, dlo, dhi, C, X0)
        if d is True:
            return m2
        if d == "未定":
            return ("未定", m2)
    return None


def min_eps_m2(m, K, dlo, dhi, l2, C, X0=X0_695, route="a"):
    """可行的 m2 中 eps 最小者（另一约定）。返回 (m2, eps_iv, n_feasible)。"""
    best = None
    nf = 0
    for m2 in range(1, m + 1):
        if feasible_decision(m2, m, K, dlo, dhi, C, X0) is not True:
            continue
        nf += 1
        iv, _ = eps_bounds(m2, m, K, dlo, dhi, l2, X0=X0, route=route)
        if best is None or iv[1] < best[1][0]:
            best = (m2, iv)
    return (best[0], best[1], nf) if best else (None, None, 0)


# ---------- 印刷规则判定 ----------

def decade(x):
    """floor(log10 x)，x > 0 有理数（整数比较）。"""
    x = F(x)
    assert x > 0
    e = 0
    if x >= 1:
        t = F(1)
        while x >= t * 10:
            t *= 10
            e += 1
    else:
        t = F(1)
        while x < t:
            t /= 10
            e -= 1
    return e


RULE_NAMES = {
    "up1": "向上取整到 1 位小数（= 2 位有效数字全进位）",
    "near1": "四舍五入到 1 位小数",
    "trunc1": "截尾到 1 位小数",
    "up2": "向上取整到 2 位小数",
    "near2": "四舍五入到 2 位小数",
    "trunc2": "截尾到 2 位小数",
}


def rule_predict(iv, k, rule):
    """对 eps 区间 [iv0, iv1] 预测「尾数保留 k 位小数」的规则值。

    返回 (尾数整数 v, 指数 e)：预测印数 = (v / 10^k) * 10^e；
    若区间跨越规则边界（同一区间内规则值不唯一）返回 None。
    rule ∈ {"up", "near", "trunc"}。
    """
    xlo, xhi = F(iv[0]), F(iv[1])
    if decade(xlo) != decade(xhi):
        return None
    e = decade(xlo)
    s = F(10) ** e
    a, b = xlo / s, xhi / s            # 尾数区间 ⊂ [1, 10)
    scale = 10 ** k

    def f(m):
        if rule == "up":
            return -((-m.numerator * scale) // m.denominator)          # ceil
        if rule == "near":
            return (2 * m.numerator * scale + m.denominator) // (2 * m.denominator)
        return (m.numerator * scale) // m.denominator                  # floor

    va, vb = f(a), f(b)
    if va != vb:
        return None
    return va, e


def mantissa_str(v, k):
    """尾数整数 v（尺度 10^k）转成字符串，如 v=69,k=1 -> '6.9'。"""
    scale = 10 ** k
    ip, fp = divmod(v, scale)
    return str(ip) + ("." + str(fp).rjust(k, "0") if k else "")
