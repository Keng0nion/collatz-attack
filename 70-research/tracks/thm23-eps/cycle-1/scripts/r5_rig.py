# -*- coding: utf-8 -*-
"""第 5 路（末值与结论稳健性）自足严格有理区间库。

只依赖标准库 fractions，不含任何浮点判定。
所有函数返回「有理上下界对」，判定一律用精确有理比较。
自检入口：python r5_rig.py
"""
import sys
from fractions import Fraction as F

sys.set_int_max_str_digits(1000000)   # 大有理数的十进制打印上限（展示与落盘用）

# 模块级参数：级数项数与 e 的有理界
N_ATANH = 140
N_EXP = 80
K0_E = 80


def floor_frac(x):
    """x > 0 有理数的下整。"""
    return x.numerator // x.denominator


def atanh_bounds(x, N=N_ATANH):
    """0 < x < 1 有理数；返回 (lo, hi)，lo < atanh(x) < hi。

    atanh(x) = sum_{k>=0} x^(2k+1)/(2k+1)，各项为正，部分和递增；
    尾界：sum_{k>=N} x^(2k+1)/(2k+1) < x^(2N+1)/((2N+1)(1-x^2))。
    """
    x = F(x)
    assert 0 < x < 1
    x2 = x * x
    xp = x          # x^(2k+1)
    s = F(0)
    for k in range(N):
        s += xp / (2 * k + 1)
        xp *= x2
    tail = xp / ((2 * N + 1) * (1 - x2))     # 此处 xp = x^(2N+1)
    return s, s + tail


def e_bounds(K0=K0_E):
    """e 的有理上下界：e = sum 1/k!；尾 sum_{k>K0} 1/k! <= (1/(K0+1)!)/(1-1/(K0+2))。

    推导：sum_{k>K0} 1/k! = sum_{j>=1} 1/(K0+j)!
      = (1/(K0+1)!) * sum_{j>=1} prod_{i=2}^{j} 1/(K0+i)
      <= (1/(K0+1)!) * sum_{j>=1} (1/(K0+2))^(j-1)
      = (1/(K0+1)!) / (1 - 1/(K0+2))。
    """
    s = F(0)
    t = F(1)
    for k in range(K0 + 1):
        s += t
        t = t / (k + 1)
    # 循环后 t = 1/(K0+1)!
    tail = t / (1 - F(1, K0 + 2))
    return s, s + tail


E_LO, E_HI = e_bounds()


def _ln2_bounds(N=N_ATANH):
    # ln 2 = 2 atanh(1/3)
    lo, hi = atanh_bounds(F(1, 3), N)
    return 2 * lo, 2 * hi


L2_LO, L2_HI = _ln2_bounds()


def ln_bounds(r, N=N_ATANH):
    """r > 1 有理数；返回 (lo, hi)，lo < ln r < hi。

    先按 2 的幂缩到 [1, 2)：ln r = j ln 2 + ln m，m = r/2^j；再走 atanh。
    """
    r = F(r)
    assert r > 1
    j = 0
    p = F(1)
    while p * 2 <= r:
        p *= 2
        j += 1
    m = r / p                      # m in [1, 2)
    lo, hi = atanh_bounds((m - 1) / (m + 1), N)
    return j * L2_LO + 2 * lo, j * L2_HI + 2 * hi


def _exp_pos_bounds(x, N=N_EXP):
    """x >= 0 有理数；返回 (lo, hi)，lo < e^x < hi。e^x = e^n * e^f，n = floor(x)，f in [0,1)。"""
    x = F(x)
    n = floor_frac(x)
    f = x - n
    s = F(0)
    term = F(1)
    for k in range(N + 1):
        s += term
        term = term * f / (k + 1)
    # 循环后 s = sum_{k=0}^{N} f^k/k!，term = f^(N+1)/(N+1)!
    rem = term / (1 - f / (N + 2))
    ef_lo, ef_hi = s, s + rem
    if n >= 0:
        return ef_lo * E_LO ** n, ef_hi * E_HI ** n
    return ef_lo / E_HI ** (-n), ef_hi / E_LO ** (-n)


def exp_bounds(x_lo, x_hi, N=N_EXP):
    """e^x 在 [x_lo, x_hi] 上的区间（e^x 单调增）。"""
    lo, _ = _exp_pos_bounds(F(x_lo), N)
    _, hi = _exp_pos_bounds(F(x_hi), N)
    return lo, hi


def pow2_bounds(v_lo, v_hi):
    """2^v 在 v in [v_lo, v_hi] 上的区间，v_lo > 0。"""
    assert F(v_lo) > 0
    return exp_bounds(F(v_lo) * L2_LO, F(v_hi) * L2_HI)


def pow_bounds(x_lo, x_hi, p_lo, p_hi):
    """1 < x_lo <= x_hi，0 < p_lo <= p_hi；返回 (lo, hi) 使 lo < x^p < hi 对一切 x in [x_lo, x_hi]、p in [p_lo, p_hi]。"""
    x_lo, x_hi, p_lo, p_hi = F(x_lo), F(x_hi), F(p_lo), F(p_hi)
    assert x_lo > 1 and p_lo > 0
    a1, b1 = ln_bounds(x_lo)
    a2, b2 = ln_bounds(x_hi)
    lo, _ = exp_bounds(p_lo * a1, p_lo * b1)      # 下界取 x_lo^p_lo
    _, hi = exp_bounds(p_hi * a2, p_hi * b2)      # 上界取 x_hi^p_hi
    return lo, hi


def delta_bounds(N=N_ATANH):
    """delta = ln3/ln2 的区间（ln3 走 atanh(1/2)）。"""
    l2lo, l2hi = _ln2_bounds(N)
    lo, hi = atanh_bounds(F(1, 2), N)
    l3lo, l3hi = 2 * lo, 2 * hi
    return l3lo / l2hi, l3hi / l2lo


def delta_bounds_alt(N=N_ATANH):
    """delta = ln3/ln2 的区间，独立走法：ln3 = ln2 + 2 atanh(1/5)。"""
    l2lo, l2hi = _ln2_bounds(N)
    lo, hi = atanh_bounds(F(1, 5), N)
    l3lo, l3hi = l2lo + 2 * lo, l2hi + 2 * hi
    return l3lo / l2hi, l3hi / l2lo


def sig_str(x, n=24):
    """展示用：把正有理数写成截断的科学计数法字符串（不用于判定）。"""
    x = F(x)
    assert x > 0
    # e 使 10^e <= x < 10^(e+1)；先用位长估一个初值（整数算术），再用精确比较校正
    e = ((x.numerator.bit_length() - x.denominator.bit_length()) * 30103) // 100000
    while F(10) ** e > x:
        e -= 1
    while F(10) ** (e + 1) <= x:
        e += 1
    # D = floor(x * 10^(n-1-e))，恰有 n 位十进制数字
    D = floor_frac(x * F(10) ** (n - 1 - e))
    s = str(D)
    assert len(s) == n, "位数异常"
    return s[0] + "." + s[1:] + "e" + ("%+d" % e)


def cf_prefix(L, U, maxlen=200):
    """区间连分数前缀证书。

    给定有理数 L < U（端点非整数），返回 (digits, lo, hi, done)：
    (L, U) 内每一点的连分数展开前 len(digits) 位等于 digits；
    digits 之末的残余区间为 (lo, hi)（尚未定出下一位）。
    """
    digits = []
    lo, hi = F(L), F(U)
    assert lo < hi
    for _ in range(maxlen):
        n = floor_frac(lo)
        if floor_frac(hi) != n:
            break
        if lo == n:
            break                        # 端点恰为整数，作停止处理
        digits.append(n)
        lo, hi = F(1) / (hi - n), F(1) / (lo - n)
    return digits, lo, hi


def convergents(digits):
    """连分数串 digits = [a0; a1, ...] 的收敛分数表 [(p_n, q_n)]。"""
    out = []
    p_m2, q_m2 = 0, 1
    p_m1, q_m1 = 1, 0
    for a in digits:
        p = a * p_m1 + p_m2
        q = a * q_m1 + q_m2
        out.append((p, q))
        p_m2, q_m2 = p_m1, q_m1
        p_m1, q_m1 = p, q
    return out


def simplest_open(A, B, cap=10 ** 7):
    """返回 (p, q, x, y, z, w)：区间 (A, B)（有理端点，A < B）内分母最小的分数 p/q，
    以及返回时刻的 Stern-Brocot 括号 x/y <= A < p/q < B <= z/w（unimodular：z*y - x*w = 1）。

    算法：从 0/1 与 1/0 出发，逐步取中项；中项 <= A 则下界取中项，中项 >= B 则上界取中项，
    中项严格落入区间即返回。步数为各连分数系数之和（本问题约三百步）。
    """
    An, Ad = F(A).numerator, F(A).denominator
    Bn, Bd = F(B).numerator, F(B).denominator
    assert F(A) < F(B)
    x, y = 0, 1
    z, w = 1, 0
    for _ in range(cap):
        mn, md = x + z, y + w
        if mn * Ad <= An * md:                 # 中项 <= A
            x, y = mn, md
        elif mn * Bd >= Bn * md:               # 中项 >= B
            z, w = mn, md
        else:
            assert z * y - x * w == 1, "unimodular 不变量被破坏"
            return mn, md, x, y, z, w
    raise RuntimeError("Stern-Brocot 未在 %d 步内收敛" % cap)


def _selftest():
    print("=== r5_rig 自检 ===")
    # 1. atanh 尾界：与 20 位十进制锚点比较（仅展示与包含检查）
    lo, hi = atanh_bounds(F(1, 3), 60)
    # 锚点按截尾语义：真值落在 [anchor, anchor + 尾位) 内；与区间 [lo, hi] 相交才算通过
    A1 = F(34657359027997265470, 10 ** 20)
    print("atanh(1/3) in (%s, %s)" % (sig_str(lo), sig_str(hi)))
    print("  与截尾锚点区间 [0.34657359027997265470, +1e-20) 相交（精确比较）:",
          lo < A1 + F(1, 10 ** 20) and hi > A1)
    # 2. ln/e 界与小数点锚点
    l2lo, l2hi = _ln2_bounds()
    print("ln2 in (%s, %s)" % (sig_str(l2lo), sig_str(l2hi)))
    A2 = F(693147180559945309417, 10 ** 21)
    print("  ln2 与截尾锚点区间 [0.693147180559945309417, +1e-21) 相交:",
          l2lo < A2 + F(1, 10 ** 21) and l2hi > A2)
    elo, ehi = E_LO, E_HI
    print("e in (%s, %s)" % (sig_str(elo), sig_str(ehi)))
    A3 = F(2718281828459045235360, 10 ** 21)
    print("  e 与截尾锚点区间 [2.718281828459045235360, +1e-21) 相交:",
          elo < A3 + F(1, 10 ** 21) and ehi > A3)
    # 2.5 尾界必要条件测试（专抓「尾界小于被截去的窗口和」这类错）
    x = F(1, 3)
    sN, sNh = atanh_bounds(x, 40)
    win = F(0)
    xp = x ** (2 * 40 + 1)
    for k in range(40, 60):
        win += xp / (2 * k + 1)
        xp *= x * x
    print("atanh 尾界 (%.6e) 不小于窗口和(40..59):%s  且不大于两倍窗口和:%s" %
          (float(sNh - sN), (sNh - sN) >= win, (sNh - sN) <= 2 * win))
    f = F(93, 100)
    s0 = F(0)
    term = F(1)
    for k in range(81):
        s0 += term
        term = term * f / (k + 1)
    rem = term / (1 - f / 82)
    win2 = F(0)
    t2 = term
    for k in range(81, 101):
        win2 += t2
        t2 = t2 * f / (k + 1)
    print("exp 尾界 (%.6e) 不小于窗口和(81..100):%s  且不大于两倍窗口和:%s" %
          (float(rem), rem >= win2, rem <= 2 * win2))
    import math
    t3 = F(1, math.factorial(81))
    tail3 = t3 / (1 - F(1, 82))
    win3 = F(0)
    t4 = t3
    for k in range(81, 101):
        win3 += t4
        t4 = t4 / (k + 1)
    print("e 尾界 (%.6e) 不小于窗口和(81..100):%s  且不大于两倍窗口和:%s" %
          (float(tail3), tail3 >= win3, tail3 <= 2 * win3))
    assert (sNh - sN) >= win and rem >= win2 and tail3 >= win3
    # 3. delta 两种走法一致（区间相交）
    a1, b1 = delta_bounds()
    a2, b2 = delta_bounds_alt()
    print("delta (走法 1) in (%s, %s)" % (sig_str(a1), sig_str(b1)))
    print("delta (走法 2) in (%s, %s)" % (sig_str(a2), sig_str(b2)))
    print("  两区间相交且合区间宽 < 1e-80:", max(a1, a2) < min(b1, b2) and (min(b1, b2) - max(a1, a2)) < F(1, 10 ** 80))
    # 4. 连分数前缀：已知有理数 415/93 = [4;2,6,7]
    L = F(415, 93) - F(1, 10 ** 9)
    U = F(415, 93) + F(1, 10 ** 9)
    d, rlo, rhi = cf_prefix(L, U)
    print("415/93 邻域前缀 =", d, "（区间跨过 415/93 的终止点，第 4 位两侧分别是 7 与 6，故证书正确地止于第 3 位）")
    # 5. simplest_open 小样例
    p, q, x, y, z, w = simplest_open(F(2, 5), F(9, 20))
    print("simplest(0.4, 0.45) = %d/%d（手算最小分母 7，值 3/7）" % (p, q))
    assert (p, q) == (3, 7)
    p, q, x, y, z, w = simplest_open(F(9, 8), F(827, 728))
    print("simplest(9/8, 827/728) = %d/%d（项目记录的真最小分母 15，见于 cycle-1/route-4.md:88）" % (p, q))
    assert (p, q) == (17, 15)
    # 6. pow_bounds 与 pow2_bounds 的锚点（仅展示）
    lo, hi = pow2_bounds(F(10), F(10))
    print("2^10 in (%s, %s)：" % (sig_str(lo), sig_str(hi)), lo < 1024 < hi)
    lo, hi = pow_bounds(F(3), F(3), F(2), F(2))
    print("3^2 的区间含 9：", lo < 9 < hi)
    print("=== 自检结束 ===")


if __name__ == "__main__":
    _selftest()
