#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-2 严格区间算术工具。

纪律：本文件只用标准库 fractions.Fraction 做精确有理算术；不 import 任何项目脚本，
不读任何项目输出。所有下界与上界都是 Fraction，所有比较都是精确有理比较。
浮点数只用于打印与「报告用量级」，不参与任何判定。

提供：
  atanh_iv(z, N)            : atanh(z) 的严格有理区间（0 <= z <= 1/2）
  ln2_iv(N), ln3_iv(N)      : ln2、ln3 的严格有理区间
  delta_iv(N)               : delta = ln3/ln2 = log2(3) 的严格有理区间
  ln_rat_iv(x, ...)         : 任意正有理数 x 的 ln 的严格有理区间（二次幂归约 + atanh 级数）
  log2_162X0_iv(...)        : log2((162/97)*X0) 的严格有理区间
  dec_round(fr, digs, up)   : 向指定方向舍入到 digs 位十进制小数的有理数
  poly_iv(lo, hi, k)        : [lo^k, hi^k]（0 < lo <= hi，k >= 1）
  cf_digits_iv(u, v, nmax)  : 由有理区间 [u, v] 严格确定 delta 型常数的连分数部分商
"""

from fractions import Fraction as F


# ---------------------------------------------------------------- 双曲反正切

def atanh_iv(z, N):
    """0 <= z <= 1/2：返回 (lo, hi) 使 lo <= atanh(z) <= hi。
    级数 atanh(z) = sum_{k>=0} z^(2k+1)/(2k+1)；尾界为
      sum_{k>N} z^(2k+1)/(2k+1) <= z^(2N+3)/((2N+3)(1-z^2))。
    注意：这里只对上界用尾界，下界是部分和本身（部分和 <= atanh）。
    """
    if not (0 <= z <= F(1, 2)):
        raise ValueError("atanh_iv 只支持 0 <= z <= 1/2")
    z = F(z)
    z2 = z * z
    s = F(0)
    term = z
    for k in range(N + 1):
        s += term / (2 * k + 1)
        term *= z2
    # 循环结束时 term = z^(2N+3)
    tail = term / ((2 * N + 3) * (1 - z2))
    return s, s + tail


def ln2_iv(N):
    lo, hi = atanh_iv(F(1, 3), N)
    return 2 * lo, 2 * hi


def ln3_iv(N):
    lo, hi = atanh_iv(F(1, 2), N)
    return 2 * lo, 2 * hi


def delta_iv(N):
    """delta = ln3/ln2 的严格有理区间。"""
    l2lo, l2hi = ln2_iv(N)
    l3lo, l3hi = ln3_iv(N)
    return l3lo / l2hi, l3hi / l2lo


# ---------------------------------------------------------------- 一般 ln

def _floor_log2(x):
    """返回唯一的整数 k 使 2^k <= x < 2^(k+1)（x 为正有理数）。"""
    n, d = x.numerator, x.denominator
    k = n.bit_length() - d.bit_length()
    while F(2) ** k > x:
        k -= 1
    while F(2) ** (k + 1) <= x:
        k += 1
    return k


def ln_rat_iv(x, ln2lo, ln2hi, N):
    """正有理数 x 的 ln 的严格有理区间。
    归约：x = 2^k * y，y 在 [1, 2)；ln x = 2*atanh((y-1)/(y+1)) + k*ln2。
    """
    x = F(x)
    if x <= 0:
        raise ValueError("ln_rat_iv 只支持 x > 0")
    k = _floor_log2(x)
    y = x / F(2) ** k                      # y in [1, 2)
    z = (y - 1) / (y + 1)                  # z in [0, 1/3]
    alo, ahi = atanh_iv(z, N)
    if k >= 0:
        return 2 * alo + k * ln2lo, 2 * ahi + k * ln2hi
    return 2 * alo + k * ln2hi, 2 * ahi + k * ln2lo


def log2_162X0_iv(ln2lo, ln2hi, N):
    """log2((162/97)*X0)，其中 X0 = 695*2^60，故 (162/97)*X0 = 112590*2^60/97。
    值 = 60 + ln(112590/97)/ln2。
    """
    x = F(112590, 97)
    xlo, xhi = ln_rat_iv(x, ln2lo, ln2hi, N)
    num_lo = 60 * ln2lo + xlo
    num_hi = 60 * ln2hi + xhi
    return num_lo / ln2hi, num_hi / ln2lo


# ---------------------------------------------------------------- 舍入与幂

def dec_round(fr, digs, up):
    """把有理数 fr 向 dig 位十进制小数的方向舍入：up=True 向上，False 向下。"""
    fr = F(fr)
    scale = 10 ** digs
    num = fr * scale
    q = num.numerator // num.denominator
    if up and F(q, scale) < fr:
        q += 1
    return F(q, scale)


def poly_iv(lo, hi, k):
    """0 < lo <= hi，k >= 1：返回 [lo^k, hi^k]（精确有理）。"""
    if lo <= 0 or lo > hi or k < 1:
        raise ValueError("poly_iv 参数非法")
    return F(lo) ** k, F(hi) ** k


# ---------------------------------------------------------------- 区间连分数

def cf_digits_iv(u, v, nmax):
    """对满足 u <= x <= v 的 x，逐项严格确定其连分数部分商。
    返回 (digits, status)：status 为
      "ok"                 前 nmax 项全部严格确定；
      "ambiguous"          在第 len(digits) 项处区间跨越整数点，无法确定；
      "endpoint"           某端点在整数点上，该项已确定但后续不能确定；
    算法：若 floor(u) == floor(v) 则该项确定为该整数；再做 u,v := 1/(v-fi), 1/(u-fi)。
    """
    u, v = F(u), F(v)
    if u > v:
        raise ValueError("区间端点顺序颠倒")
    digs = []
    for _ in range(nmax):
        au = u.numerator // u.denominator
        av = v.numerator // v.denominator
        if au != av:
            return digs, "ambiguous"
        digs.append(au)
        u2, v2 = u - au, v - au
        if u2 == 0 or v2 == 0:
            return digs, "endpoint"
        u, v = 1 / v2, 1 / u2
    return digs, "ok"


# ---------------------------------------------------------------- 显示

def sci(fr, sig=20):
    """把有理数写成科学记号（前 sig 位有效数字）；只用于显示，不参与判定。"""
    fr = F(fr)
    if fr == 0:
        return "0"
    neg = fr < 0
    fr = -fr if neg else fr
    e = 0
    ten = F(10)
    while fr >= 10:
        fr /= ten
        e += 1
    while fr < 1:
        fr *= ten
        e -= 1
    return "%s%s e%+d" % ("-" if neg else "", dec_str(fr, sig), e)


def dec_str(fr, ndig, truncate=True):
    """取有理数的十进制数字串（截断到 ndig 位小数）。"""
    fr = F(fr)
    neg = fr < 0
    fr = -fr if neg else fr
    ip = fr.numerator // fr.denominator
    rem = fr.numerator - ip * fr.denominator
    out = [("-" if neg else ""), str(ip), "."]
    for _ in range(ndig):
        rem *= 10
        d = rem // fr.denominator
        out.append(str(d))
        rem -= d * fr.denominator
    return "".join(out)


def rel_gap(a, b):
    """(|a-b| / |b|) 的浮点近似，只用于报告量级。"""
    a, b = F(a), F(b)
    if b == 0:
        return float("inf")
    return float(abs(a - b) / abs(b))
