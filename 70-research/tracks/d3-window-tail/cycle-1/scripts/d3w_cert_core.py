"""d3w_cert_core.py -- 严格有理区间核心（纯整数定向舍入，不依赖 mpmath / gmpy2 / decimal）

区间一律用 fractions.Fraction 的两个端点表示。四则运算由 Fraction 精确完成（无舍入）；
只有超越函数（atanh、ln、exp、2^x、x^y）走本文件的定点整数定向舍入：级数每一项分别
向下与向上取整，并显式加上尾项上界，因此每个返回值都是真包含区间。

对外接口：
  atanh_iv(p, q, D)        atanh(p/q)，要求 0 < p <= q/2
  ln2_iv(D)                ln 2
  ln_int_iv(n, D)          ln n（整数 n >= 1）
  ln_rat_iv(x_iv, D)       ln x（有理区间，x.lo > 0）
  exp_iv(y_iv, D)          exp(y)，要求 y_iv.lo >= 0
  two_pow_iv(x_iv, D)      2^x，要求 0 <= x_iv.lo，且区间不跨整数点
  pow_iv(base_iv, e_iv, D) base^e = exp(e ln base)，要求 base.lo > 1，e.lo >= 0
  ln_one_minus_iv(x_iv, D) ln(1-x)，要求 0 <= x.lo <= x.hi <= 1/2

自检见 scripts/d3w_core_selftest.py：用恒等式与 math 库对照，判据全部可翻 False。
"""

from fractions import Fraction as Fr


def _cdiv(a, b):
    """向上取整的整数除法（要求 b > 0）。"""
    return -((-a) // b)


class Iv(object):
    """有理区间 [lo, hi]。"""

    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi):
        lo, hi = Fr(lo), Fr(hi)
        if hi < lo:
            raise ValueError("empty interval")
        self.lo = lo
        self.hi = hi

    # ---- 精确四则（Fraction 无舍入）----
    def __add__(self, o):
        o = _as_iv(o)
        return Iv(self.lo + o.lo, self.hi + o.hi)

    def __sub__(self, o):
        o = _as_iv(o)
        return Iv(self.lo - o.hi, self.hi - o.lo)

    def __mul__(self, o):
        o = _as_iv(o)
        c = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return Iv(min(c), max(c))

    def __truediv__(self, o):
        o = _as_iv(o)
        if o.lo <= 0 <= o.hi:
            raise ZeroDivisionError("除数区间含 0")
        c = (self.lo / o.lo, self.lo / o.hi, self.hi / o.lo, self.hi / o.hi)
        return Iv(min(c), max(c))

    __rmul__ = __mul__
    __radd__ = __add__

    def __neg__(self):
        return Iv(-self.hi, -self.lo)

    def __pow__(self, k):
        k = int(k)
        if k == 0:
            return Iv(1, 1)
        if k < 0:
            return Iv(1, 1) / (self ** (-k))
        if k % 2 == 1:
            return Iv(self.lo ** k, self.hi ** k)
        a, b = self.lo ** k, self.hi ** k
        if self.lo >= 0:
            return Iv(a, b)
        if self.hi <= 0:
            return Iv(b, a)
        return Iv(Fr(0), max(a, b))

    # ---- 查询 ----
    def width(self):
        return self.hi - self.lo

    def relwidth(self):
        w = self.width()
        return float(w / max(abs(self.lo), abs(self.hi))) if self.hi != 0 else float(w)

    def contains(self, x):
        if isinstance(x, Iv):                  # 区间包含
            return self.lo <= x.lo and x.hi <= self.hi
        return self.lo <= Fr(x) <= self.hi

    def overlaps(self, x):
        x = _as_iv(x)
        return not (self.hi < x.lo or x.hi < self.lo)

    def sign(self):
        """-1 全负，+1 全正，0 含 0。"""
        if self.lo > 0:
            return 1
        if self.hi < 0:
            return -1
        return 0

    def __repr__(self):
        return "Iv[%s, %s]" % (self.lo, self.hi)


def _as_iv(o):
    if isinstance(o, Iv):
        return o
    return Iv(o, o)


def _frac_floor(x):
    """Fra（或 Fraction）向下取整为整数。"""
    x = Fr(x)
    return x.numerator // x.denominator


def _frac_ceil(x):
    x = Fr(x)
    return -((-x.numerator) // x.denominator)


# ---------------------------------------------------------------- atanh / ln

def atanh_iv(p, q, D):
    """atanh(p/q) 的严格区间；要求 0 < p <= q/2。"""
    p, q = int(p), int(q)
    if not (0 < p and 2 * p <= q):
        raise ValueError("要求 0 < p <= q/2")
    S = 10 ** D
    p2, q2 = p * p, q * q
    num, den = p, q
    lo_i = hi_i = 0
    j = 0
    while True:
        d = (2 * j + 1) * den
        lo_i += (S * num) // d
        hi_i += _cdiv(S * num, d)
        num *= p2
        den *= q2
        j += 1
        tail = _cdiv(S * num * q2, den * (2 * j + 1) * (q2 - p2))
        if tail <= 1 and j > 5:
            hi_i += tail
            break
        if j > 20000:
            raise ValueError("atanh 级数不收敛")
    return Iv(Fr(lo_i, S), Fr(hi_i, S))


def ln2_iv(D):
    """ln 2 = 2 atanh(1/3)。"""
    return Iv(2, 2) * atanh_iv(1, 3, D)


def ln_int_iv(n, D):
    """ln n 的严格区间（整数 n >= 1）。"""
    n = int(n)
    if n < 1:
        raise ValueError("要求 n >= 1")
    if n == 1:
        return Iv(0, 0)
    k = n.bit_length() - 1
    h = 1 << k
    ln2 = ln2_iv(D)
    if n == h:                             # n 为 2 的幂：ln n = k ln 2
        return Iv(k, k) * ln2
    a = atanh_iv(n - h, n + h, D)          # z ∈ (0, 1/3]
    return Iv(k, k) * ln2 + Iv(2, 2) * a


def ln_rat_iv(x_iv, D):
    """ln x 的严格区间（x_iv.lo > 0），用整数分子分母的对数差。"""
    x = _as_iv(x_iv)
    if x.lo <= 0:
        raise ValueError("要求 x > 0")
    a = ln_int_iv(x.lo.numerator, D) - ln_int_iv(x.lo.denominator, D)
    b = ln_int_iv(x.hi.numerator, D) - ln_int_iv(x.hi.denominator, D)
    return Iv(min(a.lo, b.lo), max(a.hi, b.hi))


# ------------------------------------------------------------------- exp

def _exp_small(y_iv, D):
    """exp(y) 的严格区间；要求 0 <= y_iv.lo <= y_iv.hi <= 1。"""
    S = 10 ** D
    Ylo = _frac_floor(y_iv.lo * S)
    Yhi = _frac_ceil(y_iv.hi * S)
    lo = S                      # k = 0 项（1.0 的定点表示就是 S）
    hi = S
    pw_lo, pw_hi = Ylo, Yhi     # Y^k
    div = 1                     # S^{k-1} * k!，k = 1 时为 1
    k = 1
    while True:
        lo += pw_lo // div
        hi += _cdiv(pw_hi, div)
        pw_lo *= Ylo
        pw_hi *= Yhi
        div = div * S * (k + 1)
        k += 1
        tail = _cdiv(2 * pw_hi, div)   # sum_{i>=k} y^i/i! <= 2 y^k/k!（y <= (k+1)/2）
        if tail <= 1 and k >= 6 and 2 * y_iv.hi <= k + 1:
            hi += tail
            break
        if k > 3000:
            raise ValueError("exp 级数不收敛")
    return Iv(Fr(lo, S), Fr(hi, S))


def exp_iv(y_iv, D):
    """exp(y) 的严格区间；要求 y_iv.lo >= 0。先降到 y <= 1 再反复平方。"""
    y = _as_iv(y_iv)
    if y.lo < 0:
        raise ValueError("要求 y_iv.lo >= 0")
    s = 0
    while y.hi > Fr(1):
        y = Iv(y.lo / 2, y.hi / 2)
        s += 1
        if s > 200:
            raise ValueError("降幅次数过多")
    r = _exp_small(y, D)
    for _ in range(s):
        r = r * r
    return r


def two_pow_iv(x_iv, D):
    """2^x 的严格区间；要求 0 <= x_iv.lo，且 x_iv 不跨整数点。"""
    x = _as_iv(x_iv)
    if x.lo < 0:
        raise ValueError("要求 x_iv.lo >= 0")
    n = int(x.lo)              # = floor(x.lo)，因 x.lo >= 0
    if int(x.hi) != n:
        raise ValueError("区间跨整数点")
    f = Iv(x.lo - n, x.hi - n)
    return Iv(2 ** n, 2 ** n) * exp_iv(f * ln2_iv(D), D)


def pow_iv(base_iv, e_iv, D):
    """base^e = exp(e ln base) 的严格区间；要求 base.lo > 1，e.lo >= 0。"""
    b, e = _as_iv(base_iv), _as_iv(e_iv)
    if b.lo <= 1 or e.lo < 0:
        raise ValueError("要求 base > 1 且 e >= 0")
    return exp_iv(e * ln_rat_iv(b, D), D)


def ln_one_minus_iv(x_iv, D):
    """ln(1-x) 的严格区间；要求 0 <= x_iv.lo <= x_iv.hi <= 1/2。
    ln(1-x) = -sum_{k>=1} x^k/k，尾项绝对值 <= x^k/(k(1-x)) <= 2 x^k/k。"""
    x = _as_iv(x_iv)
    if x.lo < 0 or x.hi > Fr(1, 2):
        raise ValueError("要求 0 <= lo <= hi <= 1/2")
    S = 10 ** D
    Xlo = _frac_floor(x.lo * S)
    Xhi = _frac_ceil(x.hi * S)
    lo_i = hi_i = 0
    pw_lo, pw_hi = Xlo, Xhi     # X^k
    Sp = 1                      # S^{k-1}
    k = 1
    while True:
        den = k * Sp
        lo_i += pw_lo // den
        hi_i += _cdiv(pw_hi, den)
        pw_lo *= Xlo
        pw_hi *= Xhi
        Sp *= S
        k += 1
        tail = _cdiv(2 * pw_hi, k * Sp)    # 2 x^k / k
        if tail <= 1 and k > 5:
            hi_i += tail
            break
        if k > 3000:
            raise ValueError("ln(1-x) 级数不收敛")
    # 取负：ln(1-x) ∈ [-hi_i/S, -lo_i/S]
    return Iv(Fr(-hi_i, S), Fr(-lo_i, S))
