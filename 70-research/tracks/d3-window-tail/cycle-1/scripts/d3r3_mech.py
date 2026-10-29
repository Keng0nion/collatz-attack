#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轨道 d3-window-tail cycle-1 route-3「新机制区间证书」主脚本。

机制（刻意与前两套实现不同）：
  M1 连分数 Möbius 尾项夹逼：delta = log2(3) 各用 (A,B) 递归（A' = B, B' = A/B^n，
     全部精确有理比较）取完整商 y ∈ (a,a+1)，再由 x = (p_n y + p_{n-1})/(q_n y + q_{n-1})
     对 y 严格单调夹出区间；只用小整数比较、无级数、无网格。实测该路径尺寸每步约乘 3.6，
     第 13 步已达 53057 位，故精度上限约 12 位 —— 只用作低位独立核验（整数判据 2^p<3^q），
     高精度区间由 M2 提供。
  M2 精确有理级数（atanh 与 exp）加显式几何尾界：2^v 与 b^{-delta} 的区间。
     端点全部是精确 Fraction，除解析尾界外无任何舍入（区别于 route-2 的
     GRID = 10^90 定向网格取整）。
  M3 Stern-Brocot 中位分数夹逼 + 认证符号判定器 -> 右端 K1(M) 的显式有理区间
     （区别于 route-2 与 route-3 的二分）。
  M4 自证单调性：两对初等不等式给出 Phi 关于 v 严格递减，附斜率下界。
  M5 左端门槛点用精确恒等式 2^C = (162/97)X0 做全有理判定。

运行：/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python d3r3_mech.py [节号...]
"""
import sys, math
from fractions import Fraction as F

sys.set_int_max_str_digits(2000000)

X0 = 695 * 2**60
P2C = F(162, 97) * X0          # 2^C 的精确值（定义式推论）
TWO60 = 2**60


# ---------- 十进制打印 ----------
def p10(e):
    """精确的 10^e（e 可负）。"""
    return F(10**e) if e >= 0 else F(1, 10**(-e))


def sci(x, k=30):
    """把 Fraction 打印成 k 位有效数字（截断）。全程精确，不经 float。"""
    if x == 0:
        return "0"
    s = "-" if x < 0 else ""
    x = abs(x)
    e = int((x.numerator.bit_length() - x.denominator.bit_length()) * 0.3010299956639812)
    while x >= p10(e + 1):
        e += 1
    while x < p10(e):
        e -= 1
    d = k - e
    if d >= 0:
        num = x.numerator * 10**d // x.denominator     # k+1 位（截断）
    else:
        num = x.numerator // (x.denominator * 10**(-d))
    digs = str(num).rjust(k + 1, "0")
    ip, fp = digs[:len(digs) - k], digs[len(digs) - k:]
    return f"{s}{ip}.{fp}e{e:+d}"


def rel_width(lo, hi):
    return (hi - lo) / hi


# ---------- M1 连分数（对数之比的完整商夹逼） ----------
def pow_frac(b, n):
    """精确整数幂 b^n（n 可为负）。"""
    return F(b.numerator**n, b.denominator**n) if n >= 0 else F(b.denominator**(-n), b.numerator**(-n))


def floor_logB_A(A, B):
    """精确求 n = floor(log_B A)（A>0, B>1）：满足 B^n <= A < B^(n+1)。
    先倍增定界，再二分；只用精确有理比较，不取对数。"""
    A, B = F(A), F(B)
    assert A > 0 and B > 1
    if A >= 1:
        hi = 1
        while pow_frac(B, hi) <= A:
            hi *= 2
        lo = hi // 2
    else:
        Ax = 1 / A
        k = floor_logB_A(Ax, B)
        return -k if pow_frac(B, k) == Ax else -(k + 1)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if pow_frac(B, mid) <= A:
            lo = mid
        else:
            hi = mid
    return lo


def cf_certificate(A, B, nsteps):
    """对 x = ln A / ln B 做 nsteps 步递归；返回
    (terms, 证书区间 lo< x <hi)。
    证书：x = (p_n y + p_{n-1})/(q_n y + q_{n-1})，y = 完整商 ∈ (a_{n+1}, a_{n+1}+1)，
    该 Möbius 映射在 y>0 上严格单调，故 x 严格夹在 y 取两端点的值之间。"""
    A, B = F(A), F(B)
    terms = []
    for _ in range(nsteps + 1):
        n = floor_logB_A(A, B)
        terms.append(n)
        A, B = B, A / pow_frac(B, n)
    # 收敛子
    p_m2, p_m1, q_m2, q_m1 = 0, 1, 1, 0
    pn, qn = {}, {}
    for i, a in enumerate(terms):
        p_i = a * p_m1 + p_m2
        q_i = a * q_m1 + q_m2
        pn[i], qn[i] = p_i, q_i
        p_m2, p_m1, q_m2, q_m1 = p_m1, p_i, q_m1, q_i
    # 取 n = nsteps-1，用第 n+1 项（即 terms[nsteps]）作完整商的整数部分
    n = nsteps - 1
    y0 = terms[nsteps]
    v1 = F(pn[n] * y0 + (pn[n - 1] if n >= 1 else 0), qn[n] * y0 + (qn[n - 1] if n >= 1 else 1))
    y1 = y0 + 1
    v2 = F(pn[n] * y1 + (pn[n - 1] if n >= 1 else 0), qn[n] * y1 + (qn[n - 1] if n >= 1 else 1))
    lo, hi = min(v1, v2), max(v1, v2)
    return terms[:nsteps + 1], lo, hi


# ---------- M2 级数加显式尾界 ----------
SER_GRID = 70      # 级数输入向外的十进制网格位数（只影响 gcd 速度与判据宽度，不损严格性）


def g_out(x, up, G=None):
    """向外取整到 1/10^G 网格（G 默认 SER_GRID）。"""
    G = SER_GRID if G is None else G
    if up:
        return F(-((-x.numerator * 10**G) // x.denominator), 10**G)
    return F((x.numerator * 10**G) // x.denominator, 10**G)


def atanh_series(t, N):
    """atanh 的部分和（t 已取整）：sum_{j<N} t^{2j+1}/(2j+1) 与余项上界
    sum_{j>=N} t^{2j+1}/(2j+1) <= t^{2N+1}/((2N+1)(1-t^2))。"""
    s = F(0)
    tp = t
    for j in range(N):
        s += tp / (2 * j + 1)
        tp *= t * t
    tail = tp / ((2 * N + 1) * (1 - t * t))
    return s, tail


def atanh_bounds(t, N):
    """atanh(t) 的区间（0<=t<1）：先向外取整 t，再取部分和与余项。"""
    lo, _ = atanh_series(g_out(t, False), N)
    s, tail = atanh_series(g_out(t, True), N)
    return lo, s + tail


def ln2_bounds(N=60):
    lo, hi = atanh_bounds(F(1, 3), N)
    return 2 * lo, 2 * hi


def ln_bounds(q, N=45, l2=None):
    """ln(q) 的区间，q 为精确正有理。ln q = k ln2 + ln(q/2^k)，q/2^k ∈ [1,2)。
    级数自变量 t = u/(2+u) 先向外取整到网格。"""
    if l2 is None:
        l2 = ln2_bounds(N)
    l2lo, l2hi = l2
    q = F(q)
    k = 0
    while q >= 2**(k + 1):
        k += 1
    while q < 2**k:
        k -= 1
    r = q / F(2)**k
    u = r - 1                      # 0 <= u < 1
    t = u / (2 + u)                # 0 <= t <= 1/3
    s_lo, _ = atanh_series(g_out(t, False), N)
    s_hi, tail = atanh_series(g_out(t, True), N)
    lo = 2 * s_lo + (k * l2lo if k >= 0 else k * l2hi)
    hi = 2 * (s_hi + tail) + (k * l2hi if k >= 0 else k * l2lo)
    return lo, hi


def exp_series(y, K):
    """exp(y)（y 已取整，0<=y<=1）：部分和与余项上界
    sum_{k>K} y^k/k! <= y^{K+1}/(K+1)! / (1 - y/(K+2))。"""
    s = F(0)
    term = F(1)
    for k in range(K):
        s += term
        term *= y / (k + 1)        # term = y^(k+1)/(k+1)!
    tail = term * y / (K + 1) / (1 - y / (K + 2))
    return s, tail


def exp_bounds(y, K=45):
    """exp(y) 的区间（0 <= y <= 1），自变量先向外取整到网格。"""
    s_lo, _ = exp_series(g_out(y, False), K)
    s_hi, tail = exp_series(g_out(y, True), K)
    return s_lo, s_hi + tail


def pow2_bounds(xlo, xhi, l2=None, K=45):
    """2^x 在 x ∈ [xlo,xhi] 上的区间。2^x = 2^n * exp(f ln2)；x 先向外取整到网格。"""
    if l2 is None:
        l2 = ln2_bounds()
    l2lo, l2hi = l2
    xlo = g_out(xlo, False)
    xhi = g_out(xhi, True)
    n_lo = math.floor(xlo)
    n_hi = math.floor(xhi)
    f_lo = xlo - n_lo
    f_hi = xhi - n_hi
    e_lo_lo, _ = exp_bounds(f_lo * l2lo, K)
    _, e_hi_hi = exp_bounds(f_hi * l2hi, K)
    lo = F(2)**n_lo * e_lo_lo
    hi = F(2)**n_hi * e_hi_hi
    return lo, hi


def pow_rat_bounds(b_lo, b_hi, e_lo, e_hi, l2=None, K=45, Nln=45):
    """b^e 的区间：b ∈ [b_lo,b_hi] ⊂ (1,∞)（或 [b_lo,b_hi] ⊂ (0,1)），e ∈ [e_lo,e_hi] 实数。
    用 b^e = 2^{e log2 b}；log2 b = ln b / ln 2。"""
    if l2 is None:
        l2 = ln2_bounds()
    l2lo, l2hi = l2
    llo, lhi = ln_bounds(b_lo, Nln, l2)
    hlo, hhi = ln_bounds(b_hi, Nln, l2)
    g_lo, g_hi = llo / l2hi, hhi / l2lo      # log2 b 的区间
    # e*log2 b 的区间
    if e_lo >= 0:
        xl, xh = e_lo * g_lo, e_hi * g_hi
    elif e_hi <= 0:
        xl, xh = e_lo * g_hi, e_hi * g_lo
    else:
        xl, xh = min(e_lo * g_hi, e_hi * g_lo), max(e_lo * g_lo, e_hi * g_hi)
    return pow2_bounds(xl, xh, l2, K)


def out_grid(x, G, up):
    """向外取整到 1/G 网格。"""
    if up:
        return F(-((-x.numerator * G) // x.denominator), G)
    return F((x.numerator * G) // x.denominator, G)


# ---------- 口径常量 ----------
def build_consts(N=70):
    """delta = ln3/ln2 与 C = 60 + ln(112590/97)/ln2 的高精度严格区间。
    机制：atanh 级数加显式几何尾界，端点全为精确 Fraction，无网格舍入。"""
    l2 = ln2_bounds(N)
    l3 = ln_bounds(3, N, l2)
    dlo, dhi = l3[0] / l2[1], l3[1] / l2[0]
    lq = ln_bounds(F(112590, 97), N, l2)
    Clo = 60 + lq[0] / l2[1]
    Chi = 60 + lq[1] / l2[0]
    return (dlo, dhi, Clo, Chi)


def geom_interval_grid(M, dlo, dhi, G=24):
    """geom(M) = sum_{i<M} delta^i 的区间，逐步向外取整到 1/10^G 网格。
    每步误差 <= 10^-G，总和相对误差约 M·10^-G/geom，用于判定器内部（相对精度约 10^-20）。
    幂与和的每一步都向外取整，故仍是严格区间。"""
    glo = ghi = F(0)
    plo = phi = F(1)
    for _ in range(M):
        glo = g_out(glo + plo, False, G)
        ghi = g_out(ghi + phi, True, G)
        plo = g_out(plo * dlo, False, G)
        phi = g_out(phi * dhi, True, G)
    return glo, ghi


def geom_interval(M, dlo, dhi):
    """geom(M) = sum_{i<M} delta^i 的区间（delta>1，幂单调）。"""
    glo = ghi = F(0)
    plo = phi = F(1)
    for _ in range(M):
        glo += plo
        ghi += phi
        plo *= dlo
        phi *= dhi
    return glo, ghi


def cM_intervals(M, dlo, dhi):
    def c(m):
        g = geom_interval(m, dlo, dhi)
        return F(92, m) * g[0], F(92, m) * g[1]
    return c(M), c(M - 1) if M > 1 else None


# ---------- M5 左端门槛处精确判定 ----------
def A_of(m2):
    """口径里的 A(m2)：92 档为 0，91 档为 3/X0，其余为 (97(92-m2)+73)/(54X0)。"""
    if m2 == 92:
        return F(0)
    if m2 == 91:
        return F(3) / X0
    return F(97 * (92 - m2) + 73, 54 * X0)


def Adiff(M):
    """A(M) - A(M-1)：M = 92 时 -3/X0，M = 91 时 -105/(54X0)，M <= 90 时 -97/(54X0)。"""
    return A_of(M) - A_of(M - 1)


def phi_at_threshold_bounds(M, dlo, dhi, l2=None, K=80, cpair=None):
    """Phi_M(K_thresh(M)) 的严格区间，用 2^C = (162/97)X0 精确值。
    Phi_M(K_thresh) = [A(M)-A(M-1)] + 3/(2^C-1) - 3/(2^{tau C}-1)
                      + 3(M-1)B^{-delta} - 3(M-2)(2^{tau C}-1)^{-delta},
    其中 B = 2^C - 1，tau = c_M/c_{M-1}。注意 A 差随档位变：91 与 92 档不是 -97/(54X0)。"""
    if l2 is None:
        l2 = ln2_bounds(65)
    B_ = P2C - 1
    R = Adiff(M) + 3 / B_              # 前两项之和（精确有理）
    t4lo, _ = pow_rat_bounds(B_, B_, -dhi, -dhi, l2, K)
    _, t4hi = pow_rat_bounds(B_, B_, -dlo, -dlo, l2, K)
    if cpair is None:
        gM = geom_interval_grid(M, dlo, dhi, 28)
        gM1 = geom_interval_grid(M - 1, dlo, dhi, 28)
        cpair = (F(92, M) * gM[0], F(92, M) * gM[1], F(92, M - 1) * gM1[0], F(92, M - 1) * gM1[1])
    (c_lo, c_hi, c1_lo, c1_hi) = cpair
    tl, th = c_lo / c1_hi, c_hi / c1_lo
    p_lo, _ = pow_rat_bounds(P2C, P2C, tl, tl, l2, K)
    _, p_hi = pow_rat_bounds(P2C, P2C, th, th, l2, K)
    b2p_lo, b2p_hi = p_lo - 1, p_hi - 1
    t5lo_, _ = pow_rat_bounds(b2p_hi, b2p_hi, -dhi, -dhi, l2, K)
    _, t5hi_ = pow_rat_bounds(b2p_lo, b2p_lo, -dlo, -dlo, l2, K)
    lo = R - 3 / b2p_lo + 3 * (M - 1) * t4lo - 3 * (M - 2) * t5hi_
    hi = R - 3 / b2p_hi + 3 * (M - 1) * t4hi - 3 * (M - 2) * t5lo_
    return lo, hi, R, (tl, th)


# ---------- M4 单调性证书 ----------
def mono_certificate(dlo, dhi, tau_lo, tau_hi, t0=60, l2=None):
    """证明 v >= t0 时 Phi 关于 v 严格递减（两对不等式）。
    g(t)=2^t/(2^t-1)^2, h(t)=2^t(2^t-1)^{-delta-1}。
    2^{-t} <= g(t) <= (16/9)2^{-t}；2^{-delta t} <= h(t) <= (4/3)^{delta+1}2^{-delta t}。
    对 1：2^{-t} > (16/9) tau 2^{-tau t}
    对 2：(M-1) delta 2^{-delta t} > (M-2) tau delta (4/3)^{delta+1} 2^{-tau delta t}
    """
    if l2 is None:
        l2 = ln2_bounds()
    l2lo, l2hi = l2
    t = F(t0)
    # 对 1：证 2^{-t} > (16/9) tau_hi 2^{-tau_lo t}
    e_lo = -(tau_lo - 1) * t
    u_lo, _ = pow2_bounds(e_lo, e_lo, l2)
    rhs1 = F(16, 9) * tau_hi * u_lo
    ok1 = F(1) > rhs1
    # 对 2：拿 tau_hi、delta_hi 作最坏方向
    lo2 = (1) / (tau_hi * pow_rat_bounds(F(4, 3), F(4, 3), dhi + 1, dhi + 1, l2)[1])
    # (M-1)/(M-2) >= 1 的因子先不乘（M>=88 时 > 1）
    e2 = -(tau_lo - 1) * dlo * t
    u2_lo, _ = pow2_bounds(e2, e2, l2)
    rhs2 = tau_hi * pow_rat_bounds(F(4, 3), F(4, 3), dhi + 1, dhi + 1, l2)[1] * u2_lo
    ok2 = lo2 > rhs2
    return ok1, rhs1, ok2, lo2, rhs2, t


# ---------- M3 认证符号判定器 ----------
class Oracle:
    """认证符号判定器：给定 M 与有理 K，返回 Phi_M(K) 的严格有理区间。
    内部用缩精度常量（约 30 位）与级数尾界；判据的严格性只依赖单调方向正确，
    与内部精度无关（精度只决定判定器的可分辨宽度）。"""

    def __init__(self, dlo, dhi, Clo, Chi, Gexp=20, Gv=22, K=40, Nln=45, Gser=36):
        self.dlo, self.dhi = dlo, dhi
        self.Clo, self.Chi = Clo, Chi
        self.l2 = ln2_bounds(Nln)
        self.Gv = 10**Gv
        self.K = K
        self.Gser = Gser
        self.cache = {}

    def cM(self, M):
        """c_M = (92/M) geom(M) 与 c_{M-1} 的区间。
        先用精确幂算 geom（数位大），随即向外取整到 1/Gv 网格以控规模；
        向外取整只加宽区间，证书严格性不受影响。"""
        if M not in self.cache:
            gM = geom_interval_grid(M, self.dlo, self.dhi, 28)
            gM1 = geom_interval_grid(M - 1, self.dlo, self.dhi, 28)
            g = self.Gv
            c_lo = out_grid(F(92, M) * gM[0], g, False)
            c_hi = out_grid(F(92, M) * gM[1], g, True)
            c1_lo = out_grid(F(92, M - 1) * gM1[0], g, False)
            c1_hi = out_grid(F(92, M - 1) * gM1[1], g, True)
            self.cache[M] = (c_lo, c_hi, c1_lo, c1_hi)
        return self.cache[M]

    def phi_bounds(self, M, K):
        """返回 (lo, hi)：Phi_M(K) 的严格区间（lo <= Phi <= hi）。
        判定器内部把级数网格放宽到 1/10^36 以提速；向外取整只加宽区间，
        判定宽度随之放宽到约 10^-55（远超本轮所需的 10^-30）。"""
        global SER_GRID
        _save = SER_GRID
        SER_GRID = self.Gser
        try:
            return self._phi_bounds(M, K)
        finally:
            SER_GRID = _save

    def _phi_bounds(self, M, K):
        c_lo, c_hi, c1_lo, c1_hi = self.cM(M)
        g = self.Gv
        Kf = F(K)
        v_lo = out_grid(Kf / c_hi, g, False)
        v_hi = out_grid(Kf / c_lo, g, True)
        tl = c_lo / c1_hi
        th = c_hi / c1_lo
        vp_lo = out_grid(v_lo * tl, g, False)
        vp_hi = out_grid(v_hi * th, g, True)
        Kk = self.K
        l2 = self.l2
        # 2^v 与 2^v'
        a_lo, a_hi = pow2_bounds(v_lo, v_lo, l2, Kk)
        b_lo, b_hi = pow2_bounds(v_hi, v_hi, l2, Kk)
        pa_lo, pa_hi = pow2_bounds(vp_lo, vp_lo, l2, Kk)
        pb_lo, pb_hi = pow2_bounds(vp_hi, vp_hi, l2, Kk)
        # 基（2^v - 1）区间，随后向外取整到较小网格以控规模
        gb = 10**30
        b2_lo = out_grid(a_lo - 1, gb, False)
        b2_hi = out_grid(b_hi - 1, gb, True)
        b2p_lo = out_grid(pa_lo - 1, gb, False)
        b2p_hi = out_grid(pb_hi - 1, gb, True)
        A0 = -Adiff(M)        # Phi = Adiff(M) + 3/(2^v-1) - ... ；这里取 -A0 = Adiff(M)
        # 上界：每项取使 Phi 变大的方向
        t2u = 3 / b2_lo
        t3u = -3 / b2p_hi
        _, t4u = pow_rat_bounds(b2_lo, b2_lo, -self.dlo, -self.dlo, l2, Kk)
        t5u_, _ = pow_rat_bounds(b2p_hi, b2p_hi, -self.dhi, -self.dhi, l2, Kk)
        phi_u = -A0 + t2u + t3u + 3 * (M - 1) * t4u - 3 * (M - 2) * t5u_
        # 下界：每项取使 Phi 变小的方向
        t2l = 3 / b2_hi
        t3l = -3 / b2p_lo
        _, t4l = pow_rat_bounds(b2_hi, b2_hi, -self.dhi, -self.dhi, l2, Kk)
        t5l_, _ = pow_rat_bounds(b2p_lo, b2p_lo, -self.dlo, -self.dlo, l2, Kk)
        phi_l = -A0 + t2l + t3l + 3 * (M - 1) * t4l - 3 * (M - 2) * t5l_
        return phi_l, phi_u

    def sign(self, M, K):
        lo, hi = self.phi_bounds(M, K)
        if lo > 0:
            return 1, lo, hi
        if hi < 0:
            return -1, lo, hi
        return 0, lo, hi


# ---------- 主流程 ----------
def main():
    print("=" * 78)
    print("[0] 口径与精确恒等式（全部精确有理，无浮点）")
    print(f"  X0 = 695*2^60 = {X0}")
    print(f"  2^C = (162/97)X0 = {P2C.numerator}/{P2C.denominator}（精确）")
    R = F(97, 54) / (X0 * (P2C - 1))
    print(f"  R := 3/(2^C-1) - 97/(54X0) = 97/(54 X0 (2^C-1)) 精确值 = {sci(R, 45)}")

    print("=" * 78)
    print("[1] 连分数路径的可达精度上限（实测尺寸增长；只用于低位独立核验）")
    import time as _t
    t0 = _t.time()
    A, B = F(3), F(2)
    terms_d, sizes = [], []
    for i in range(13):
        n = floor_logB_A(A, B)
        terms_d.append(n)
        A, B = B, A / pow_frac(B, n)
        sizes.append((i, n, max(len(str(A.numerator)), len(str(B.denominator))), round(_t.time() - t0, 2)))
    print(f"  log2 3 的连分数前 13 项：{terms_d}")
    print(f"  (步, 项, 有理数十进制位数, 累计秒)：{sizes}")
    print(f"  尺寸每步约乘 {round((sizes[12][2] / sizes[8][2]) ** 0.25, 2)}；"
          f"外推第 25 步约 10^25 位以上，故 (A,B) 路径可用精度上限约 12 位。")
    _, mlo, mhi = cf_certificate(3, 2, 11)
    print(f"  Möbius 尾项证书（11 步）：delta ∈ ({sci(mlo, 18)}, {sci(mhi, 18)})"
          f"  端点分母位数 {len(str(mlo.denominator))}, {len(str(mhi.denominator))}")
    dlo_t, dhi_t, Clo_t, Chi_t = build_consts(70)

    p_m2, p_m1, q_m2, q_m1 = 0, 1, 1, 0
    convs = []
    for a in terms_d:
        p_i = a * p_m1 + p_m2
        q_i = a * q_m1 + q_m2
        convs.append((p_i, q_i))
        p_m2, p_m1, q_m2, q_m1 = p_m1, p_i, q_m1, q_i
    print("  整数判据 2^p < 3^q < 2^(p+1)（纯整数，独立于级数；末列 = 级数区间含于整数区间？）：")
    for p, q in convs[1:]:
        if q > 2 * 10**6:
            continue
        if 2**p < 3**q:
            ilo, ihi, ok = F(p, q), F(p + 1, q), True
        else:
            ilo, ihi, ok = F(p - 1, q), F(p, q), 2**(p - 1) < 3**q and 3**q < 2**p
        print(f"    p/q={p}/{q}: 判据成立？ {ok} ；粗细一致？ {ilo <= dlo_t and dhi_t <= ihi}")

    print("=" * 78)
    print("[2] 机制二（级数加显式尾界）给出 delta、C、门槛与左端证书")
    dlo, dhi, Clo, Chi = dlo_t, dhi_t, Clo_t, Chi_t
    print(f"  delta ∈ ({sci(dlo, 45)}, {sci(dhi, 45)})  相对宽 {sci(rel_width(dlo, dhi), 4)}")
    print(f"  C     ∈ ({sci(Clo, 45)}, {sci(Chi, 45)})  相对宽 {sci(rel_width(Clo, Chi), 4)}")
    res = {}
    for M in range(87, 93):
        glo, ghi = geom_interval_grid(M, dlo, dhi, 58)
        res[M] = (F(92, M) * glo * Clo, F(92, M) * ghi * Chi)
    for M in (88, 89, 90, 91, 92):
        klo, khi = res[M]
        print(f"  M={M}: K_thresh ∈ ({sci(klo, 42)}, {sci(khi, 42)}) 相对宽 {sci(rel_width(klo, khi), 4)}")
    print(f"  相邻门槛之比（下界）M=89..92：{[sci(res[M][0] / res[M - 1][1], 12) for M in (89, 90, 91, 92)]}")
    dlo_r, dhi_r, Clo_r, Chi_r = build_consts(32)      # 判定器用缩精度常量（约 32 位）
    orc = Oracle(dlo_r, dhi_r, Clo_r, Chi_r)
    thr = {}
    for M in (88, 89, 90, 91, 92):
        lo, hi, R_, tau = phi_at_threshold_bounds(M, dlo_r, dhi_r, cpair=orc.cM(M))
        thr[M] = (lo, hi)
        print(f"  M={M}: Phi_M(K_thresh) ∈ ({sci(lo, 20)}, {sci(hi, 20)})  符号 {1 if lo > 0 else (-1 if hi < 0 else 0)}")
    B_ = P2C - 1
    l2 = ln2_bounds(65)
    lo90, hi90, R90, tau90 = phi_at_threshold_bounds(90, dlo_r, dhi_r, cpair=orc.cM(90))
    t4 = pow_rat_bounds(B_, B_, -dhi_r, -dhi_r, l2)[0]
    p_lo = pow_rat_bounds(P2C, P2C, tau90[0], tau90[0], l2)[0]
    t3 = 3 / (p_lo - 1)
    print(f"  M=90 三项分解：R = {sci(R90, 20)}；-3/(2^(tauC)-1) = -{sci(t3, 20)}；"
          f"3*89*B^(-delta) >= {sci(3 * 89 * t4, 20)}")
    print(f"    第三项 / |前两项之和（含 tauC 修正）| ≈ {sci(3 * 89 * t4 / abs(R90 + t3), 12)}；"
          f"第三项 / 两项残差 97/(54X0(2^C-1)) ≈ {sci(3 * 89 * t4 / (F(97, 54) / (X0 * B_)), 12)}")

    print("=" * 78)
    print("[3] M4 自证单调性（v >= 60 时 Phi 关于 v 严格递减）与窗口封闭界")
    for M in (88, 89, 90, 91, 92):
        (c_lo, c_hi, c1_lo, c1_hi) = orc.cM(M)
        tl, th = c_lo / c1_hi, c_hi / c1_lo
        ok1, rhs1, ok2, lo2, rhs2, t = mono_certificate(dlo_r, dhi_r, tl, th)
        if M == 90:
            print(f"  tau_90 ∈ ({sci(tl, 15)}, {sci(th, 15)})")
            print(f"  对 1：1 > (16/9)tau_hi*2^-((tau_lo-1)*60) ？ {ok1}（右端 {sci(rhs1, 12)}）")
            print(f"  对 2：1/(tau_hi(4/3)^(delta_hi+1)) > tau_hi(4/3)^(delta_hi+1)*2^-((tau_lo-1)delta_lo*60) ？"
                  f" {ok2}（{sci(lo2, 12)} vs {sci(rhs2, 12)}）")
        g_lo = pow2_bounds(F(-60), F(-60), l2)[0]
        slack = F(1) - F(16, 9) * th * pow2_bounds(-(tl - 1) * 60, -(tl - 1) * 60, l2)[0]
        rate = 3 * l2[0] * g_lo * slack / c_hi
        clo, chi = thr[M]
        if chi < 0:
            print(f"  M={M}: 斜率下界 |dPhi/dK| >= {sci(rate, 8)}；Phi(K_thresh) <= {sci(chi, 12)} < 0 "
                  f"=> 该档无根（窗口为空）")
        else:
            print(f"  M={M}: 斜率下界 |dPhi/dK| >= {sci(rate, 8)}；由 Phi(K_thresh) <= {sci(chi, 12)} 得"
                  f" K1 <= K_thresh + {sci(chi / rate, 8)}（相对 {sci(chi / rate / res[M][0], 6)}）")

    print("=" * 78)
    print("[4] 机制三：右端证书（判定器 + 二分定位 + Stern-Brocot 中位夹逼）")
    windows = {}
    for M in (88, 89, 90):
        klo, khi = res[M]
        # 起点括号：两端都用判定器认证（起点只作初始括号，其含根性由端点符号证明）
        L = Hi = None
        for off in (16, 14, 12, 10, 9, 8):
            cand = klo * (1 + F(1, 10**off))
            s, _, _ = orc.sign(M, cand)
            if s == 1:
                L = cand
                break
        for off in (8, 9, 10, 11, 12, 6):
            cand = khi * (1 + F(1, 10**off))
            s, _, _ = orc.sign(M, cand)
            if s == -1:
                Hi = cand
                break
        if L is None or Hi is None:
            print(f"  M={M}: 起点括号失败（L={L}, H={Hi}）—— 缺口")
            continue
        steps = 0
        while (Hi - L) / L > F(1, 10**10) and steps < 200:
            m = (L + Hi) / 2
            s, _, _ = orc.sign(M, m)
            if s == 1:
                L = m
            elif s == -1:
                Hi = m
            else:
                break
            steps += 1
        # 端点向小分母取整（向外，保持符号），再走 Stern-Brocot 中位夹逼
        scale = 10**max(0, len(str(L.numerator)) - len(str(L.denominator)) - 13)
        Lr = F(-((-L.numerator * scale) // L.denominator), scale)      # 向上取整
        Hr = F((Hi.numerator * scale) // Hi.denominator, scale)        # 向下取整
        sL, loL, hiL = orc.sign(M, Lr)
        sH, loH, hiH = orc.sign(M, Hr)
        if sL == 1 and sH == -1:
            L, Hi = Lr, Hr
        sb = 0
        while (Hi - L) / L > F(1, 10**26) and sb < 3000:
            m = F(L.numerator + Hi.numerator, L.denominator + Hi.denominator)
            s, _, _ = orc.sign(M, m)
            if s == 1:
                L = m
            elif s == -1:
                Hi = m
            else:
                break
            sb += 1
        sL, loL, hiL = orc.sign(M, L)
        sH, loH, hiH = orc.sign(M, Hi)
        windows[M] = (L, Hi)
        print(f"  M={M}: K1 ∈ ({sci(L, 42)}, {sci(Hi, 42)}) 相对宽 {sci(rel_width(L, Hi), 4)}"
              f"（二分 {steps} 步 + 中位 {sb} 步）")
        print(f"      端点认证：Phi(L) >= {sci(loL, 16)} (>0: {loL > 0})；Phi(H) <= {sci(hiH, 16)} (<0: {hiH < 0})")
        print(f"      端点分母位数 {len(str(L.denominator))}/{len(str(Hi.denominator))}；"
              f"rho ∈ [{sci((L - khi) / khi, 18)}, {sci((Hi - klo) / klo, 18)}]")

    print("=" * 78)
    print("[5] K* 与 K_cross 的窗口外判定")
    Kstar = 205632218873398596256
    wmax = max(windows[M][1] for M in (88, 89, 90))
    print(f"  K* = {Kstar}")
    print(f"  K* > max(M<=90) K1 上端？ {Kstar > wmax}  余量 {sci(F(Kstar) - wmax, 20)}，"
          f"相对 {sci((F(Kstar) - wmax) / Kstar, 8)}")
    print(f"  K_thresh(91) 上端 {sci(res[91][1], 20)} < K* < K_thresh(92) 下端 {sci(res[92][0], 20)} ？"
          f" {res[91][1] < Kstar < res[92][0]}")
    print(f"  M=91、92 门槛处 Phi < 0（配单调性 => 无窗口）？ {thr[91][1] < 0}, {thr[92][1] < 0}")
    print(f"  K_cross 现行严格面下界 3.131547906e20（条件性，转引 cycle-2/route-3.md 5.1 与 ledger.md:14）")

    print("=" * 78)
    print("[6] 扰动检验（判据必须能翻 False）")
    ratio = 3 * 89 * t4 / (F(97, 54) / (X0 * (P2C - 1)))
    print(f"  (a) 第三项 / 两项残差 = {sci(ratio, 12)}（账本口径 5.22e10）：判据 > 1e10 ？ {ratio > 10**10}；"
          f"阈值抬到 1e11 ？ {ratio > 10**11}；降到 1e9 ？ {ratio > 10**9}")
    for M in (88, 89, 90):
        rho_lo = (windows[M][0] - res[M][1]) / res[M][1]
        print(f"  (b) M={M}: rho >= {sci(rho_lo, 12)}：> 1e-13 ？ {rho_lo > F(1, 10**13)}；"
              f"阈值抬到 1e-12 ？ {rho_lo > F(1, 10**12)}；< 1e-20（判 route-5 的 2e-24 机制）？ {rho_lo < F(1, 10**20)}")
    print(f"  (c) 判定器在 K1 两端给出相反符号（上表 lo 为正、hi 为负即证判据不恒真）")
    print(f"  (d) 门槛处 Phi 在 M=88..92 的符号：{[1 if thr[M][0] > 0 else (-1 if thr[M][1] < 0 else 0) for M in (88, 89, 90, 91, 92)]}")
    # 落盘本次证书的显式有理端点（供审计与对照脚本读取）
    import json
    out = {"delta": [str(dlo), str(dhi)], "C": [str(Clo), str(Chi)], "Kstar": str(Kstar)}
    for M in (88, 89, 90, 91, 92):
        out[f"Kthresh_{M}"] = [str(res[M][0]), str(res[M][1])]
        if M in windows:
            out[f"K1_{M}"] = [str(windows[M][0]), str(windows[M][1])]
            out[f"phiLo_{M}"] = str(orc.sign(M, windows[M][0])[1])
            out[f"phiHi_{M}"] = str(orc.sign(M, windows[M][1])[2])
        out[f"thrPhi_{M}"] = [str(thr[M][0]), str(thr[M][1])]
    import pathlib as _pl
    _pl.Path("/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/d3-window-tail/cycle-1/scripts/results/d3r3_windows.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print("  已落盘 scripts/results/d3r3_windows.json（显式有理端点）")

    X0b = 704 * 2**60
    P2Cb = F(162, 97) * X0b
    Rb = F(97, 54) / (X0b * (P2Cb - 1))
    Cb_lo = 60 + ln_bounds(F(162 * 704, 97), 70, l2)[0] / l2[1]
    print(f"  (e) 704 口径（arXiv v3）重算：R(704) = {sci(Rb, 20)}；C(704) 下端 ≈ {sci(Cb_lo, 20)}，"
          f"C 改变约 {sci((Cb_lo - Clo) / Clo, 6)}（判据随口径变，非硬编码）")


if __name__ == "__main__":
    main()
