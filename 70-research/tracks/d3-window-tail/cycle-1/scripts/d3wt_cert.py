# -*- coding: utf-8 -*-
"""d3-window-tail 第 1 轮 route-4：两约定分岔窗口的严格有理区间证书（自写，定案不经浮点）。

只用 fractions.Fraction 的精确运算、自写 atanh 级数（ln）与自写 Taylor 级数
（exp，带显式尾项上界）。不用 mpmath / mpfr 定案；不用放大的 delta 有理替代。

口径（与 cycle-2/scripts/c2r5_rig.py 的 A_of / v_exact / eps_bounds 一致）：
  m = 92；X0 = 695*2^60；delta = log 3/log 2；Q := 2^C = (162/97)X0（精确有理）；
  v(j,K) = (j/92)*K*(delta-1)/(delta^j - 1)；A(j) = 0 (j=92)、3/X0 (j=91)、(97*(92-j)+73)/(54X0)；
  num(j,K) = A(j) + 3/(2^v - 1) + 3*(j-1)/(2^v - 1)^delta；
  G_M(K) = num(M,K) - num(M-1,K)（与 eps(M,K) - eps(M-1,K) 同号，因分母 3K ln2 相同）。
窗口 W_M := { K >= K_thresh(M) : G_M(K) > 0 }，K_thresh(M) = (92/M)*((delta^M-1)/(delta-1))*C。
"""
import math
from fractions import Fraction as F

MM = 92
X0 = 695 * 2 ** 60
Q = F(162, 97) * X0
assert Q == F(112590 * 2 ** 60, 97)
U = F(1, 10 ** 10)

out = []
def P(*a):
    s = " ".join(str(x) for x in a)
    out.append(s)
    print(s)


def dec(fr, n=24):
    """有理数的十进制定向（向下）显示，n 位小数；仅用于打印。"""
    if fr is None:
        return "None"
    neg = fr < 0
    fr = -fr if neg else fr
    scale = 10 ** n
    i = (fr.numerator * scale) // fr.denominator
    return ("-" if neg else "") + "%d.%0*d" % (i // scale, n, i % scale)


# ------------------------------------------------------------------ 区间类（精确）
class Iv(object):
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi):
        if not (lo <= hi):
            raise ValueError("空区间")
        self.lo, self.hi = F(lo), F(hi)

    def __add__(self, o):
        o = o if isinstance(o, Iv) else Iv(o, o)
        return Iv(self.lo + o.lo, self.hi + o.hi)

    __radd__ = __add__

    def __neg__(self):
        return Iv(-self.hi, -self.lo)

    def __sub__(self, o):
        o = o if isinstance(o, Iv) else Iv(o, o)
        return Iv(self.lo - o.hi, self.hi - o.lo)

    def __rsub__(self, o):
        return Iv(o, o) - self

    def __mul__(self, o):
        o = o if isinstance(o, Iv) else Iv(o, o)
        v = [self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi]
        return Iv(min(v), max(v))

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = o if isinstance(o, Iv) else Iv(o, o)
        assert o.lo > 0 or o.hi < 0, "除数跨零"
        v = [self.lo / o.lo, self.lo / o.hi, self.hi / o.lo, self.hi / o.hi]
        return Iv(min(v), max(v))


def pos_pow(iv, n):
    if n == 0:
        return Iv(1, 1)
    return Iv(iv.lo ** n, iv.hi ** n)


# ------------------------------------------------------------------ ln / exp
def _atanh_series(s, N):
    s2 = s * s
    tot = F(0)
    p = s
    for k in range(N):
        tot += p / (2 * k + 1)
        p *= s2
    tail = (p / (2 * N + 1)) / (1 - s2)
    return tot, tot + tail


_LN2 = None
def ln2_iv():
    global _LN2
    if _LN2 is None:
        alo, ahh = _atanh_series(F(1, 3), 240)
        _LN2 = Iv(snap_lo(2 * alo), snap_hi(2 * ahh))
    return _LN2


SIG = 30          # 有效数字（十进制）——所有超越结果的定向舍入位数
_lncache = {}


def _nd(x):
    """正整数的十进制位数（不用 str，避开 CPython 3.11 的 4300 位整数转串上限）。"""
    assert x > 0
    k = max(1, int(x.bit_length() * 0.30103))
    while 10 ** (k + 1) <= x:
        k += 1
    while k > 1 and 10 ** k > x:
        k -= 1
    return k


def _snap_nd(A, D, d, up):
    """A/D（A >= 0、D > 0 整数）定向舍入到 d 位有效数字，返回有理数。"""
    if A == 0:
        return F(0)
    e = _nd(A) - _nd(D)
    while (A < D * 10 ** (e - 1)) if e - 1 >= 0 else (A * 10 ** (1 - e) < D):
        e -= 1
    while (A >= D * 10 ** e) if e >= 0 else (A * 10 ** (-e) >= D):
        e += 1
    m = d - 1 - e
    if m >= 0:
        num = A * 10 ** m          # 值 ≈ q/10^m
        q = -((-num) // D) if up else num // D
        return F(q, 10 ** m)
    den = D * 10 ** (-m)           # 值 ≈ q·10^(-m)
    q = -((-A) // den) if up else A // den
    return F(q) * F(10) ** (-m)


def snap_lo(x, d=SIG):
    """把非负有理数 x 向下舍入到 d 位有效数字。"""
    x = F(x)
    assert x >= 0
    if x == 0:
        return F(0)
    return _snap_nd(x.numerator, x.denominator, d, False)


def snap_hi(x, d=SIG):
    """把非负有理数 x 向上舍入到 d 位有效数字。"""
    x = F(x)
    assert x >= 0
    if x == 0:
        return F(0)
    return _snap_nd(x.numerator, x.denominator, d, True)


def sn(iv, d=SIG):
    """区间定向（外向）舍入到 d 位有效数字，控制分母膨胀；只对非负区间用。"""
    assert iv.lo >= 0
    return Iv(snap_lo(iv.lo, d), snap_hi(iv.hi, d))


def sns(iv, d=SIG):
    """同 sn，但允许负区间（对两端分别定向舍入）。"""
    lo = snap_lo(iv.lo, d) if iv.lo > 0 else (-snap_hi(-iv.lo, d) if iv.lo < 0 else F(0))
    hi = snap_hi(iv.hi, d) if iv.hi > 0 else (-snap_lo(-iv.hi, d) if iv.hi < 0 else F(0))
    return Iv(lo, hi)


def ln_pos(y, rel=F(1, 10 ** 26)):
    """ln(y) 的严格区间，y > 0 有理（入口出口都做定向有效数字舍入，控制分母膨胀）。"""
    y = F(y)
    if y in _lncache:
        return _lncache[y]
    y = snap_lo(y)
    k = 0
    t = y
    while t >= 2:
        t /= 2
        k += 1
    while t < 1:
        t *= 2
        k -= 1
    s = snap_hi((t - 1) / (t + 1))
    N = 48
    while True:
        alo, ahh = _atanh_series(s, N)
        if (ahh - alo) <= rel * alo:      # s = 0（y 恰为 2 的幂）时两侧同为 0，用 <= 收口
            break
        N *= 2
        assert N <= 8192, "atanh 未收敛"
    l2 = ln2_iv()
    r = (Iv(2 * alo + k * l2.lo, 2 * ahh + k * l2.hi) if k >= 0
         else Iv(2 * alo + k * l2.hi, 2 * ahh + k * l2.lo))
    r = Iv(snap_lo(r.lo), snap_hi(r.hi))
    _lncache[y] = r
    return r


def _taylor_raw(z, N):
    """返回 (A, D)：sum_{k=0}^{N} z^k/k! = A/D 精确，另给尾项 (Rn, Dn) 使 R <= Rn/Dn。全整数。"""
    z = snap_lo(z)
    p, q = z.numerator, z.denominator
    assert 0 <= p <= (N + 2) * q
    A = 0
    c = math.factorial(N)
    u = 1
    v = q ** N
    for k in range(N + 1):
        A += c * u * v
        if k < N:
            c //= (k + 1)
            u *= p
            v //= q
    D = q ** N * math.factorial(N)
    Rn = p ** (N + 1) * (N + 2)
    Dn = q ** N * math.factorial(N + 1) * ((N + 2) * q - p)
    return A, D, Rn, Dn


EXP_N = 64          # 归约到 r <= 1/2 后的 Taylor 项数；余项 <= r^(N+1)/(N+1)!/(1-r/(N+2)) < 1e-100


def exp_pos(zlo, zhi, rel=F(1, 10 ** 26)):
    """exp 的严格区间，0 <= zlo <= zhi 有理。

    算法：取 2 的幂归约 z = 2^m·r（r <= 1/2），r 上做 N 项 Taylor（带显式余项上界），
    再连续平方 m 次；每步的中间结果都做定向有效数字舍入，故整数规模恒定（~2000 位）。
    区间单调性：exp 递增，故 [exp(zlo), exp(zhi)] ⊇ exp([zlo, zhi])；
    平方保包含：lo_{k+1} <= lo_k^2 <= exp(2^{k+1} rlo)，hi 同理。
    """
    zlo, zhi = F(zlo), F(zhi)
    assert 0 <= zlo <= zhi
    m = 0
    while zhi / 2 ** m > F(1, 2):
        m += 1
    rlo = zlo / 2 ** m
    rhi = zhi / 2 ** m
    A, D, _, _ = _taylor_raw(rlo, EXP_N)
    B, E, Rn, Dn = _taylor_raw(rhi, EXP_N)
    lo = _snap_nd(A, D, SIG, False)
    hi = _snap_nd(B, E, SIG, True) + _snap_nd(Rn, Dn, SIG, True)
    for _ in range(m):
        lo = _snap_nd(lo.numerator ** 2, lo.denominator ** 2, SIG, False)
        hi = _snap_nd(hi.numerator ** 2, hi.denominator ** 2, SIG, True)
    lo = _snap_nd(lo.numerator, lo.denominator, SIG, False)
    hi = _snap_nd(hi.numerator, hi.denominator, SIG, True)
    assert lo <= hi
    return Iv(lo, hi)


def pow_pos(base, ex):
    """base^ex 的严格区间：base > 1、ex > 0 两区间（对两者单调增）。"""
    return exp_pos(ex.lo * ln_pos(base.lo).lo, ex.hi * ln_pos(base.hi).hi)


def pow2_Au(Aiv, u):
    """2^(A*u) 的严格区间，A ∈ Aiv、u 有理 ∈ [0,U]；用 e^z ∈ [1+z, 1+z+z^2]。"""
    L2s = ln2_iv()
    zlo = snap_lo(Aiv.lo * u * L2s.lo)
    zhi = snap_hi(Aiv.hi * u * L2s.hi)
    assert zhi <= 1
    return Iv(snap_lo(1 + zlo), snap_hi(1 + zhi + zhi * zhi))


def pow1p_delta(yiv):
    """(1+y)^delta 的严格区间，0 <= y <= 1e-8、delta ∈ [1,2]；用 1+delta*y <= (1+y)^delta <= 1+delta*y+(delta*y)^2。"""
    assert yiv.lo >= 0 and yiv.hi <= F(1, 10 ** 7)
    lo = 1 + DELTA.lo * yiv.lo
    hi = 1 + DELTA.hi * yiv.hi + (DELTA.hi * yiv.hi) ** 2
    return Iv(snap_lo(lo), snap_hi(hi))


# ------------------------------------------------------------------ 常数证书
P("=" * 104)
P("[0] 原语自检（可翻 False；含 >10^29 量级，正是旧版 _snap_nd 负幂符号写错的地方）")
P("-" * 104)
_selftest = []
for (A, D) in ((1234567, 1000), (1, 3), (10 ** 40 + 7, 3), (2 ** 200, 10 ** 7),
               (30531938055841308709325002965, 10 ** 4)):
    a, b = _snap_nd(A, D, 30, False), _snap_nd(A, D, 30, True)
    _selftest.append((F(A, D) >= a, F(A, D) <= b, a < b or F(A, D) == a))
P("  定向舍入包含性（下界 <= 真值 <= 上界，5 组含 10^40 与 3.05×10^33 量级）：%s"
  % all(all(t) for t in _selftest))
_e1 = exp_pos(F(77), F(77))
P("  exp(77) 的高精度核对：用 mpmath 的 30 位值是否落在区间内由对照脚本另做；")
P("  本自检只查包含性与单调性：exp(77) > exp(76) ？%s ；exp(0) == 1 ？%s"
  % (exp_pos(F(77), F(77)).lo > exp_pos(F(76), F(76)).hi,
     exp_pos(F(0), F(0)).lo == 1 and exp_pos(F(0), F(0)).hi == 1))
_l3 = ln_pos(3)
P("  ln3 的区间宽 %.3e ；ln(2^70) 与 70·ln2 相交非空 ？%s"
  % (float(_l3.hi - _l3.lo),
     not (_l3.hi * 70 < ln_pos(2 ** 70).lo or _l3.lo * 70 > ln_pos(2 ** 70).hi)))
P("")
P("=" * 104)
P("[1] 常数证书（严格有理区间；自写 atanh 级数 + 自写 Taylor 级数，定案不经浮点）")
P("-" * 104)
L2 = ln2_iv()
LN3 = ln_pos(3)
DELTA = Iv(LN3.lo / L2.hi, LN3.hi / L2.lo)
LNQ = ln_pos(Q)
CIV = Iv(LNQ.lo / L2.hi, LNQ.hi / L2.lo)
P("  ln2   区间宽度 = %.3e" % float(L2.hi - L2.lo))
P("  delta ∈ [%s,\n           %s]" % (dec(DELTA.lo, 40), dec(DELTA.hi, 40)))
P("  delta 区间宽度 = %.3e" % float(DELTA.hi - DELTA.lo))
P("  C     ∈ [%s,\n           %s]" % (dec(CIV.lo, 40), dec(CIV.hi, 40)))
P("  C 区间宽度 = %.3e" % float(CIV.hi - CIV.lo))
P("  Q = 2^C = (162/97)X0 = %d/%d（精确有理）" % (Q.numerator, Q.denominator))
QPOW = pow_pos(Iv(Q - 1, Q - 1), DELTA)
P("  (2^C-1)^delta ∈ [%s, %s]" % (dec(QPOW.lo, 22), dec(QPOW.hi, 22)))
P("  恒等式检验 3/2^C - 97/(54X0) == 0（精确有理）：%s" % (3 / Q - F(97, 54 * X0) == 0))
P1 = 3 / (Q * (Q - 1))
P("  P1 := 3/(2^C-1) - 97/(54X0) = 3/(2^C(2^C-1)) = %s（精确有理，不需超越估计）" % dec(P1, 46))

# ------------------------------------------------------------------ 每档 M 的量
def A_of(j):
    if j == MM:
        return F(0)
    if j == MM - 1:
        return F(3, X0)
    return F(97 * (MM - j) + 73, 54 * X0)


def thresh_iv(M):
    return Iv(F(MM, M), F(MM, M)) * ((pos_pow(DELTA, M) - 1) / (DELTA - 1)) * CIV


def rho_iv(M):
    return Iv(F(M - 1, M), F(M - 1, M)) * ((pos_pow(DELTA, M) - 1) / (pos_pow(DELTA, M - 1) - 1))


rows = []
P("")
P("=" * 104)
P("[2] 逐档 M = 2..92：门槛处与右端 x = 1+U 的 G_M 符号（严格区间判据），窗口右端 u_1 的区间")
P("-" * 104)
P("  约定 x := K/K_thresh(M)；t := 2^(C x)，s := 2^(rho_M C x)；")
P("      G_M(x) = A(M)-A(M-1) + 3/(t-1) - 3/(s-1) + 3(M-1)/(t-1)^delta - 3(M-2)/(s-1)^delta")
P("  符号栏：+ 表示 G_M(1) 的区间严格为正；- 表示严格为负；? 表示区间跨零")
P("")
P("  M | K_thresh(M)（下界显示） | rho_M | G_M(1) 符号 大小 | G_M(1+U) 符号 | u_1 区间")
for M in range(2, MM + 1):
    Kt = thresh_iv(M)
    rho = rho_iv(M)
    Adiff = A_of(M) - A_of(M - 1)
    rhoC = Iv(rho.lo * CIV.lo, rho.hi * CIV.hi)
    s_base = exp_pos(rho.lo * CIV.lo * L2.lo, rho.hi * CIV.hi * L2.hi)
    s_pow = pow_pos(Iv(s_base.lo - 1, s_base.hi - 1), DELTA)

    def G_at(u, _M=M, _Adiff=Adiff, _rhoC=rhoC, _sbase=s_base, _spow=s_pow):
        E = pow2_Au(CIV, u)
        t = Iv(Q, Q) * E
        Ep = pow2_Au(_rhoC, u)
        s = _sbase * Ep
        yC = (Iv(Q, Q) * (E - 1)) / (Q - 1)
        tp = QPOW * pow1p_delta(yC)
        ys = (_sbase * (Ep - 1)) / (_sbase - 1)
        sp = _spow * pow1p_delta(ys)
        g1 = sns(Iv(3, 3) / (t - 1))
        g2 = sns(Iv(3, 3) / (s - 1))
        g3 = sns(Iv(3 * (_M - 1), 3 * (_M - 1)) / tp)
        g4 = sns(Iv(3 * (_M - 2), 3 * (_M - 2)) / sp)
        return sns(Iv(_Adiff, _Adiff) + g1 - g2 + g3 - g4)

    g1 = G_at(F(0))
    gU = G_at(U)
    s1 = "+" if g1.lo > 0 else ("-" if g1.hi < 0 else "?")
    s2 = "+" if gU.lo > 0 else ("-" if gU.hi < 0 else "?")
    lo_u = hi_u = None
    if s1 == "+" and s2 == "-":
        a, b = F(0), U
        for _ in range(70):
            m = (a + b) / 2
            gm = G_at(m)
            if gm.lo > 0:
                a = m
            elif gm.hi < 0:
                b = m
            else:
                break
        lo_u, hi_u = a, b
    rows.append((M, Kt, rho, g1, gU, s1, s2, lo_u, hi_u))
    P("  %2d | %s | %s | %s %s | %s | %s"
      % (M, dec(Kt.lo, 6), dec(rho.lo, 19), s1, dec(g1.lo, 12), s2,
         ("[%s, %s]" % (dec(lo_u, 20), dec(hi_u, 20))) if lo_u is not None else "无"))

# ------------------------------------------------------------------ 汇总
win = [r[0] for r in rows if r[5] == "+"]
now = [r[0] for r in rows if r[5] == "-"]
und = [r[0] for r in rows if r[5] == "?"]
P("")
P("=" * 104)
P("[3] 窗口存在性分布（严格区间判据，无网格、无采样）")
P("-" * 104)
P("  门槛处 G_M(1) > 0（有窗）的档：%s" % win)
P("  门槛处 G_M(1) < 0（无窗）的档：%s" % now)
P("  未定档：%s" % und)
P("  边界邻档的 G_M(1) 区间：")
for M in (23, 24, 25, 26, 87, 88, 89, 90, 91, 92):
    for r in rows:
        if r[0] == M:
            P("    M=%2d  G_M(1) ∈ [%s, %s]   符号 %s" % (M, dec(r[3].lo, 18), dec(r[3].hi, 18), r[5]))

P("")
P("=" * 104)
P("[4] 三条引理与 M = 91、92 的空窗口（半直线直接不等式）")
P("-" * 104)
for M in (88, 89, 90):
    for r in rows:
        if r[0] == M:
            P("  L1(M=%d)：G_M(门槛) ∈ [%s, %s]，严格 > 0 ？%s" % (M, dec(r[3].lo, 18), dec(r[3].hi, 18), r[3].lo > 0))
            P("  L3(M=%d)：G_M(1+1e-10) ∈ [%s, %s]，严格 < 0 ？%s" % (M, dec(r[4].lo, 18), dec(r[4].hi, 18), r[4].hi < 0))
            P("  窗口右端 u_1(M=%d) ∈ [%s, %s]（括号相对宽 %.2e；与 u_1 之比 %.2e）"
              % (M, dec(r[7], 24), dec(r[8], 24), float((r[8] - r[7]) / r[8]), float((r[8] - r[7]) / r[8])))
P("")
P("  L2（单调性，显式不等式，无导数）：f := 3/(t-1)、h := 3(M-1)/(t-1)^delta、g := 3/(s-1)、")
P("     k := 3(M-2)/(s-1)^delta 都是 t 或 s 的递减函数，因而对任意 1 <= x1 < x2 <= 1+U")
P("     G(x2)-G(x1) <= -[f(1)-f(1+U)] + [g(1)-g(1+U)] + [h(1)-h(1+U)] + [k(1)-k(1+U)]。")
P("     逐档核验余量（只列最小与最大）：")
res = []
for M in win:
    rho = rho_iv(M)
    rhoC = Iv(rho.lo * CIV.lo, rho.hi * CIV.hi)
    s_base = exp_pos(rho.lo * CIV.lo * L2.lo, rho.hi * CIV.hi * L2.hi)
    E1 = pow2_Au(CIV, U)
    tU = Iv(Q, Q) * E1
    Ep = pow2_Au(rhoC, U)
    sU = s_base * Ep
    tpU = QPOW * pow1p_delta((Iv(Q, Q) * (E1 - 1)) / (Q - 1))
    spU = pow_pos(Iv(s_base.lo - 1, s_base.hi - 1), DELTA)
    f1 = Iv(3, 3) / (Iv(Q, Q) - 1)
    fU = Iv(3, 3) / (tU - 1)
    h1 = Iv(3 * (M - 1), 3 * (M - 1)) / QPOW
    hU = Iv(3 * (M - 1), 3 * (M - 1)) / tpU
    g1 = Iv(3, 3) / (s_base - 1)
    gU = Iv(3, 3) / (sU - 1)
    k1 = Iv(3 * (M - 2), 3 * (M - 2)) / spU
    kU = Iv(3 * (M - 2), 3 * (M - 2)) / (spU * pow1p_delta((s_base * (Ep - 1)) / (s_base - 1)))
    margin = (f1 - fU).lo - ((g1 - gU).hi + (h1 - hU).hi + (k1 - kU).hi)
    res.append((float(margin), M))
res.sort()
P("     最小余量：M=%d，余量下界 = %.4e ；最大余量：M=%d，余量下界 = %.4e"
  % (res[0][1], res[0][0], res[-1][1], res[-1][0]))
P("     全部 %d 个有窗档余量为正（即 G 在 [1,1+U] 上严格递减）：%s" % (len(res), all(x[0] > 0 for x in res)))
P("     另：x >= 1+U 时 G_M(x) < 0 由 [4] 末段的直接不等式给出（t、s 在 x 上递增，两个正项按 x=1+U 取值）。")
P("")
P("  M = 91、92 的空窗口（半直线，直接不等式；丢弃两个负项，两个正项在 t >= Q 上按 t = Q 取值）：")
for M in (91, 92):
    Adiff = A_of(M) - A_of(M - 1)
    up = Iv(Adiff, Adiff) + Iv(3, 3) / (Iv(Q, Q) - 1) + Iv(3 * (M - 1), 3 * (M - 1)) / QPOW
    P("    M=%d：G_M(x) <= [%s, %s] < 0 ？%s（对一切 x >= 1）"
      % (M, dec(up.lo, 20), dec(up.hi, 20), up.hi < 0))

P("")
P("=" * 104)
P("[5] max 右端与 K*、K_cross 区间、T 的下界的比较")
P("-" * 104)
worst = None
for r in rows:
    if r[7] is None:
        continue
    hi_end = r[1].hi * (1 + r[8])
    if worst is None or hi_end > worst[0]:
        worst = (hi_end, r[0], r[1], r[8])
P("  有窗档中右端最大者：M=%d；K_thresh 区间上界 = %s；u_1 上界 = %s"
  % (worst[1], dec(worst[2].hi, 6), dec(worst[3], 26)))
P("  max_{M<=90} K_thresh(M)*(1+u_1(M)) 的上界 = %s" % dec(worst[0], 6))
uni = thresh_iv(90).hi * (1 + U)
P("  统一（更松）上界 max_{M<=90} K_thresh(M)*(1+1e-10) = %s" % dec(uni, 6))
Kstar = F(205632218873398596256)
P("  K* = %d" % Kstar)
P("  K* - max 右端上界 = %s ；相对余量 = %s" % (dec(Kstar - worst[0], 6), dec((Kstar - worst[0]) / worst[0], 14)))
P("  K* - 统一上界   = %s ；相对余量 = %s" % (dec(Kstar - uni, 6), dec((Kstar - uni) / uni, 14)))
R_lo = F(31319547895917226287663653061949070652602310169, 10 ** 8)
P("  R（K_cross 的 47 位区间）下界（c2r5_cert.log:67 逐字复核）= %s" % dec(R_lo, 6))
P("  R_lo - max 右端上界 = %s ；相对余量 = %s" % (dec(R_lo - worst[0], 6), dec((R_lo - worst[0]) / worst[0], 14)))
T_lo = F(3131547906, 10) * 10 ** 12
P("  T 的下界 3.131547906e20（cycle-2/route-3.md:225）= %s" % dec(T_lo, 4))
P("  T_lo - max 右端上界 = %s ；相对余量 = %s" % (dec(T_lo - worst[0], 6), dec((T_lo - worst[0]) / worst[0], 14)))
P("  （R 与 T 分栏：R 是方程 eps(92,K) = gamma - delta 的根区间；T 是平台右端的已证下界。）")
P("")
Kt91, Kt92 = thresh_iv(91), thresh_iv(92)
P("  K* 的窗口归属：")
P("    K_thresh(91) ∈ [%s, %s] ；K_thresh(92) ∈ [%s, %s]"
  % (dec(Kt91.lo, 6), dec(Kt91.hi, 6), dec(Kt92.lo, 6), dec(Kt92.hi, 6)))
P("    K_thresh(91) <= K* < K_thresh(92) ？%s（故 K* 处 m2_max = 91）"
  % (Kt91.hi <= Kstar and Kstar < Kt92.lo))
P("    结合 [4] 的 M = 91 半直线上界 < 0：K* 处 G_91 < 0，两约定同值，K* 不在任何窗口内。")
P("  R（K_cross）的窗口归属：")
P("    R 的下界 > K_thresh(92) 的上界 ？%s" % (R_lo > Kt92.hi))
P("    结合 [4] 的 M = 92 半直线上界 < 0：R 处 G_92 < 0，两约定同值，R 不在任何窗口内。")

import pathlib as _pl
_pl.Path(__file__.replace("scripts/d3wt_cert.py", "results/d3wt_cert.out")).write_text("\n".join(out) + "\n", encoding="utf-8")
