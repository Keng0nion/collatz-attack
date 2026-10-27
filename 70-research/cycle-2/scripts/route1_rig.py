#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-1 自写严格有理算术库（唯一依赖：标准库 fractions）。

不复用 r4x_core.py 的任何浮点路径；不复用 scripts/route3_recheck.py（learnings.md:38）。
δ 的严格有理界本库自己重算一遍（并用 r4x_rig_helpers.py 的同款量作一致性对拍，
见 route1_cert.py 第七节），v、2^v − 1、(2^v − 1)^δ、ε(m₂, K) 的区间全部本库自实现。

每个函数返回 Fraction 端点构成的闭区间 [lo, hi]，lo <= 真值 <= hi，全部为精确有理运算。
不允许任何 float 参与判定。
"""
from fractions import Fraction as F

# ---------------------------------------------------------------- 基础

def floor_frac(q):
    """floor of a Fraction。"""
    return q.numerator // q.denominator


def ceil_frac(q):
    return -((-q.numerator) // q.denominator)


def iv_add(A, B):
    return (A[0] + B[0], A[1] + B[1])


def iv_sub(A, B):
    return (A[0] - B[1], A[1] - B[0])


def iv_mul(A, B):
    p = (A[0] * B[0], A[0] * B[1], A[1] * B[0], A[1] * B[1])
    return (min(p), max(p))


def iv_div(A, B):
    if B[0] <= 0 <= B[1]:
        raise ZeroDivisionError("除数区间含 0：%s" % (B,))
    p = (A[0] / B[0], A[0] / B[1], A[1] / B[0], A[1] / B[1])
    return (min(p), max(p))


def iv_pow_int(A, n):
    """A^n，n >= 0 整数；A 的端点为正数时用端点幂（两向单调）。"""
    if n == 0:
        return (F(1), F(1))
    if A[0] > 0:
        return (A[0] ** n, A[1] ** n)
    raise ValueError("只支持正区间")


IV_DIGITS = 200          # 区间端点的定向舍入位数（10^-200 量级，远小于一切判据余量）


def iv_round(A, digits=IV_DIGITS):
    """把区间端点向外舍入到 10^-digits 的整数倍（lo 向下、hi 向上），保证包含原区间。

    作用：把下游区间端点的十进制位数封顶，避免 δ^91 这种端点（分母上万位）在
    exp/ln 级数里把分母撑到百万位。舍入引入的绝对误差 < 10^-digits，
    而本证书全部判据的余量都在 10^-42 以上，故无损严格性。
    """
    s = 10 ** digits
    lo = A[0] * s
    hi = A[1] * s
    lo_f = floor_frac(lo)
    hi_f = -floor_frac(-hi)
    return (F(lo_f, s), F(hi_f, s))


def dec_str(fr, ndig):
    """分数的十进制截断串（含小数点），用于打印与锚点核对。"""
    n, d = fr.numerator, fr.denominator
    ip = n // d
    rem = n - ip * d
    out = [str(ip), "."]
    for _ in range(ndig):
        rem *= 10
        q = rem // d
        out.append(str(q))
        rem -= q * d
    return "".join(out)


def sci_str(fr, ndig=40):
    """科学计数法字符串（截断），仅在精确有理比较之外作展示。"""
    if fr == 0:
        return "0"
    neg = fr < 0
    x = -fr if neg else fr
    e = 0
    while x >= 10:
        x /= 10
        e += 1
    while x < 1:
        x *= 10
        e -= 1
    s = dec_str(x, ndig)
    return "%s%se%s" % ("-" if neg else "", s, ("+" if e >= 0 else "") + str(e))


# ---------------------------------------------------------------- ln

N_SER = 400          # ln2、ln3 的 atanh 级数项数
N_LN = 120           # 一般 ln 的 atanh 级数项数（u <= 1/3，尾部 ~5e-119，够用）


def _ln2_bounds(N=N_SER):
    """ln2 = 2*sum_{k>=0} 1/((2k+1) 3^(2k+1))。

    尾部：sum_{k>N} 1/((2k+1) 3^(2k+1))
        <= 1/(2N+3) * sum_{k>N} 3^(-(2k+1))
         = 1/(2N+3) * (3/8) * 9^(-(N+1))。
    ln2 - 2*partial  <=  2 * 上述。
    """
    s = F(0)
    for k in range(N + 1):
        s += F(1, (2 * k + 1) * 3 ** (2 * k + 1))
    lo = 2 * s
    tail_sum = F(3, 8) * F(1, 9 ** (N + 1)) / (2 * N + 3)
    return lo, lo + 2 * tail_sum


def _atanh_bounds(u, N, two=True):
    """ln((1+u)/(1-u)) 的严格区间；u = t/(2+t) in [0, 1)。

    ln = 2*sum_{k>=0} u^(2k+1)/(2k+1)（two=True）或 sum（two=False）。
    尾部 <= c * u^(2N+3)/((2N+3)(1-u^2))，c = 2 或 1。要求 u < 1。
    """
    if not (0 <= u < 1):
        raise ValueError("需要 0 <= u < 1")
    s = F(0)
    for k in range(N + 1):
        s += u ** (2 * k + 1) / (2 * k + 1)
    c = F(2) if two else F(1)
    part = c * s
    tail = c * u ** (2 * N + 3) / ((2 * N + 3) * (1 - u * u))
    return part, part + tail


_L2 = _ln2_bounds()

# ln3 = ln2 + ln(3/2)，ln(3/2) = 2 atanh(1/5)（比直接用 2 atanh(1/2) 快得多）
_L32 = _atanh_bounds(F(1, 5), N_SER)


def ln2_bounds():
    return _L2


def ln3_bounds():
    return (_L2[0] + _L32[0], _L2[1] + _L32[1])


_L3 = ln3_bounds()


def ln_bounds(x, N=N_LN):
    """ln(x) 的严格区间，x 为 Fraction > 0。

    归约：x = y * 2^n，y in [1,2)；y = 1 时精确；否则 ln y = 2 atanh(t/(2+t))，t = y-1。
    """
    if x <= 0:
        raise ValueError("ln 需要正数")
    n = 0
    y = F(x)
    while y >= 2:
        y /= 2
        n += 1
    while y < 1:
        y *= 2
        n -= 1
    if y == 1:
        ly = (F(0), F(0))
    else:
        t = y - 1
        ly = _atanh_bounds(t / (2 + t), N)
    if n >= 0:
        return (ly[0] + n * _L2[0], ly[1] + n * _L2[1])
    return (ly[0] + n * _L2[1], ly[1] + n * _L2[0])


# ---------------------------------------------------------------- exp

K_EXP = 60           # e^x 的 Taylor 项数（对 |x| <= 2 足够；余项显式控制）


def exp_series_bounds(x, K=K_EXP):
    """e^x 的严格区间，x 为 Fraction >= 0 的固定点值（端点分别调用）。

    lo = sum_{k=0}^{K} x^k/k!（正项级数部分和，必 <= e^x）
    hi = lo + x^(K+1)/(K+1)! * 1/(1 - x/(K+2))，要求 x < K+2。
    """
    if x < 0:
        raise ValueError("只支持 x >= 0")
    if x >= K + 2:
        raise ValueError("需要 x < K+2 才能控制余项")
    s = F(1)
    t = F(1)
    for k in range(1, K + 1):
        t = t * x / k
        s += t
    t_next = t * x / (K + 1)
    rem = t_next / (1 - x / (K + 2))
    return s, s + rem


def exp_bounds(xlo, xhi, K=K_EXP):
    """e^x 在 x in [xlo, xhi]（0 <= xlo <= xhi）上的严格区间。"""
    lo, _ = exp_series_bounds(xlo, K)
    _, hi = exp_series_bounds(xhi, K)
    return lo, hi


def pow2_bounds(xlo, xhi, K=K_EXP):
    """2^x 在 x in [xlo, xhi]（0 <= xlo <= xhi）上的严格区间。

    拆分整体数部分：x = n + a，n = floor(xlo)，a in [0, ~1]；2^n 精确整数幂。
    """
    if xlo < 0:
        raise ValueError("只支持 x >= 0")
    n = floor_frac(xlo)
    a_lo = xlo - n
    a_hi = xhi - n
    if a_hi >= 2:
        raise ValueError("小数部分过大：%s" % a_hi)
    elo = a_lo * _L2[0]
    ehi = a_hi * _L2[1]
    lo, _ = exp_series_bounds(elo, K)
    _, hi = exp_series_bounds(ehi, K)
    return 2 ** n * lo, 2 ** n * hi


# ---------------------------------------------------------------- δ 与区间上的复合

def delta_bounds():
    """δ = ln3/ln2 的严格有理区间。"""
    return _L3[0] / _L2[1], _L3[1] / _L2[0]


def geom_bounds(m2, dlo, dhi):
    """(δ^m2 - 1)/(δ - 1) 在 δ in [dlo,dhi] 上的严格区间（分子分母各自单调）。"""
    num = (dlo ** m2 - 1, dhi ** m2 - 1)
    den = (dlo - 1, dhi - 1)
    return iv_div(num, den)          # 分子分母都 > 0


# ---------------------------------------------------------------- 连分数（精确整数递推）

def cf_digits_iv(lo, hi, nsteps):
    """区间 [lo,hi] 内实数的连分数部分商，逐步用 floor 判定；判定失败抛错。

    不变式：第 i 步的 [lo,hi] 包含真值的第 i 个尾；真值在 (lo,hi) 内。
    """
    digs = []
    for i in range(nsteps):
        flo, fhi = floor_frac(lo), floor_frac(hi)
        if flo != fhi:
            raise RuntimeError("第 %d 项判定失败：floor 不一致" % i)
        if lo <= flo:
            raise RuntimeError("第 %d 项下端点恰为整数，区间退化" % i)
        a = flo
        digs.append(a)
        lo, hi = 1 / (hi - a), 1 / (lo - a)
    return digs


def contr(coef):
    """有限连分数 [c0; c1, …, cn] 的 (分子, 分母)，精确整数递推。"""
    pm2, pm1 = 0, 1
    qm2, qm1 = 1, 0
    for a in coef:
        p = a * pm1 + pm2
        q = a * qm1 + qm2
        pm2, pm1 = pm1, p
        qm2, qm1 = qm1, q
    return pm1, qm1


# ---------------------------------------------------------------- 证书常量与 ε 区间

X0 = 695 * 2 ** 60                    # 印出版 Definition 4
M_CYCLES = 92
KSTAR = 205632218873398596256


def ctx():
    """打包本证书共用的一致常量（δ 两种版本、ln2 界、c 的界）。"""
    l2lo, l2hi = ln2_bounds()
    l3lo, l3hi = ln3_bounds()
    dlo, dhi = delta_bounds()
    DL, DH = iv_round((dlo, dhi))
    lnY = ln_bounds(F(112590, 97))
    c_lo = 60 + lnY[0] / l2hi
    c_hi = 60 + lnY[1] / l2lo
    return {"l2lo": l2lo, "l2hi": l2hi, "l3lo": l3lo, "l3hi": l3hi,
            "dlo": dlo, "dhi": dhi, "DL": DL, "DH": DH, "c_lo": c_lo, "c_hi": c_hi}


def v_bounds(m2, K, DL, DH):
    """v = (m2/m)K(δ−1)/(δ^m2 − 1) 的严格区间。"""
    C = F(m2, M_CYCLES) * K
    num = (C * (DL - 1), C * (DH - 1))
    den = (DL ** m2 - 1, DH ** m2 - 1)
    return iv_round(iv_div(num, den))


def A_of(m2):
    """Theorem 21 的 A(m2)（印出版 /tmp/h5.txt:695 至 :727）。"""
    if m2 == M_CYCLES:
        return F(0)
    if m2 == M_CYCLES - 1:
        return F(3, X0)
    return F(97 * (M_CYCLES - m2) + 73, 54 * X0)


def eps_bounds(m2, K, C):
    """ε(m2, K) 的严格区间（A 项 + 3/(2^v−1) + 3(m2−1)/(2^v−1)^δ）。

    返回 (ε 区间, v 区间, (2^v−1) 区间, (2^v−1)^δ 区间)。
    v 过大（2^v 无法展开）时抛 ValueError，调用方自行退化到 A 项下界。
    """
    DL, DH = C["DL"], C["DH"]
    l2lo, l2hi = C["l2lo"], C["l2hi"]
    A = A_of(m2)
    vlo, vhi = v_bounds(m2, K, DL, DH)
    if vhi > 4000:
        raise ValueError("v 过大（%s），2^v 不适合直接展开" % sci_str(vhi, 6))
    two_v = iv_round(pow2_bounds(vlo, vhi))
    tlo, thi = two_v[0] - 1, two_v[1] - 1
    ln_t = iv_round((ln_bounds(tlo)[0], ln_bounds(thi)[1]))
    log2t = iv_round((ln_t[0] / l2hi, ln_t[1] / l2lo))
    z = iv_round(iv_mul((DL, DH), log2t))
    Tlo, Thi = iv_round(pow2_bounds(z[0], z[1]))
    num_lo = A + 3 / thi + 3 * F(m2 - 1) / Thi
    num_hi = A + 3 / tlo + 3 * F(m2 - 1) / Tlo
    return (iv_round((num_lo / (3 * K * l2hi), num_hi / (3 * K * l2lo))),
            (vlo, vhi), (tlo, thi), (Tlo, Thi))
