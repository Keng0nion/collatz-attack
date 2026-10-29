#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-3 独立二分（另一机制：MPFR 定向舍入 + 中值二分）。
本脚本不 import d3r3_mech，用 gmpy2 的 MPFR（文档声明正确舍入）独立重算同一式子，
给出 K1(M) 的二分括号，再与 d3r3_windows.json 里的证书端点对照到明写相对宽。

注意（诚实标注）：MPFR 的正确舍入是第三方库的文档声明，本脚本只把它当独立数值对照，
不作证明；证明侧是本目录 d3r3_mech.py 的精确有理区间。
"""
import sys, json, time
import gmpy2
from gmpy2 import mpfr, mpz, context, RoundDown, RoundUp, log, log2

import sys as _sys
PREC = int(_sys.argv[1]) if len(_sys.argv) > 1 else 260
X0 = 695 * 2**60
CNUM = 162 * X0
CDEN = 97


def ctx(r):
    return context(precision=PREC, round=r)


def f_lo(f, *a):
    with ctx(RoundDown):
        return f(*a)


def f_hi(f, *a):
    with ctx(RoundUp):
        return f(*a)


def rat_iv(num, den):
    """num/den（整数）的可靠区间。"""
    return f_lo(lambda x, y: x / y, mpfr(num), mpfr(den)), f_hi(lambda x, y: x / y, mpfr(num), mpfr(den))


# delta = ln3/ln2
ln2l, ln2h = f_lo(log, mpfr(2)), f_hi(log, mpfr(2))
ln3l, ln3h = f_lo(log, mpfr(3)), f_hi(log, mpfr(3))
dlo, dhi = f_lo(lambda a, b: a / b, ln3l, ln2h), f_hi(lambda a, b: a / b, ln3h, ln2l)
# C = log2((162/97) X0)
xl, xh = rat_iv(CNUM, CDEN)
Clo, Chi = f_lo(log2, xl), f_hi(log2, xh)


def geom_iv(M):
    """sum_{i<M} delta^i 的区间。"""
    sl, sh = mpfr(0), mpfr(0)
    pl, ph = mpfr(1), mpfr(1)
    for _ in range(M):
        with ctx(RoundDown):
            sl = sl + pl
        with ctx(RoundUp):
            sh = sh + ph
        pl = f_lo(lambda a, b: a * b, pl, dlo)
        ph = f_hi(lambda a, b: a * b, ph, dhi)
    return sl, sh


def cM_iv(M):
    gl, gh = geom_iv(M)
    cl = f_lo(lambda a, m: a * m, gl, mpfr(92) / mpfr(M)) if False else None
    with ctx(RoundDown):
        c1 = gl * mpfr(92) / mpfr(M)
    with ctx(RoundUp):
        c2 = gh * mpfr(92) / mpfr(M)
    return c1, c2


def phi_iv(M, K):
    """Phi_M(K) 的 MPFR 区间（下界向下、上界向上；每项按单调方向取端点）。"""
    c_lo, c_hi = cM_iv(M)
    c1_lo, c1_hi = cM_iv(M - 1)
    with ctx(RoundDown):
        v_lo = mpfr(K) / c_hi
    with ctx(RoundUp):
        v_hi = mpfr(K) / c_lo
    with ctx(RoundDown):
        tl = c_lo / c1_hi
    with ctx(RoundUp):
        th = c_hi / c1_lo
    with ctx(RoundDown):
        vp_lo = v_lo * tl
    with ctx(RoundUp):
        vp_hi = v_hi * th

    def pow2(v, r):
        with ctx(r):
            return gmpy2.exp2(v)

    def pwr(b, e, r):
        # b^e = 2^(e log2 b)
        with ctx(r):
            return gmpy2.exp2(e * log2(b))

    A0l = f_hi(lambda: mpfr(97) / (mpfr(54) * mpfr(X0)))   # 用于上界要取下界方向：这里另算
    with ctx(RoundDown):
        A0_lo = mpfr(97) / (mpfr(54) * mpfr(X0))
    with ctx(RoundUp):
        A0_hi = mpfr(97) / (mpfr(54) * mpfr(X0))
    # 各端点值
    b2vlo, b2vhi = pow2(v_lo, RoundDown), pow2(v_lo, RoundUp)
    b2vhi_lo, b2vhi_hi = pow2(v_hi, RoundDown), pow2(v_hi, RoundUp)
    bp_lo_lo, bp_lo_hi = pow2(vp_lo, RoundDown), pow2(vp_lo, RoundUp)
    bp_hi_lo, bp_hi_hi = pow2(vp_hi, RoundDown), pow2(vp_hi, RoundUp)
    # 上界：+3/(2^v-1) 用最小基；-3/(2^vp-1) 用最大基；正的 delta 次幂用最小基与最小 delta
    with ctx(RoundUp):
        up2 = mpfr(3) / (b2vlo - 1)
    with ctx(RoundDown):
        lo2 = mpfr(3) / (b2vhi_hi - 1)
    with ctx(RoundDown):
        up3 = mpfr(-3) / (bp_hi_hi - 1)
    with ctx(RoundUp):
        lo3 = mpfr(-3) / (bp_lo_lo - 1)
    up4 = pwr(b2vlo - 1, -dlo, RoundUp)          # 上界：正项取最小基、最小 delta
    lo4 = pwr(b2vhi_hi - 1, -dhi, RoundDown)     # 下界：正项取最大基、最大 delta
    # 第五项为负：-3(M-2) * X，X = (2^v'-1)^(-delta)
    #   下界要用 X 的最大值（最小基、最小 delta）的上界；
    #   上界要用 X 的最小值（最大基、最大 delta）的下界。
    Xmax_up = pwr(bp_lo_lo - 1, -dlo, RoundUp)
    Xmin_lo = pwr(bp_hi_hi - 1, -dhi, RoundDown)
    with ctx(RoundDown):
        phi_lo = -A0_hi + lo2 + lo3 + mpfr(3) * (M - 1) * lo4 - mpfr(3) * (M - 2) * Xmax_up
    with ctx(RoundUp):
        phi_hi = -A0_lo + up2 + up3 + mpfr(3) * (M - 1) * up4 - mpfr(3) * (M - 2) * Xmin_lo
    return phi_lo, phi_hi


def sign(M, K):
    lo, hi = phi_iv(M, K)
    if lo > 0:
        return 1
    if hi < 0:
        return -1
    return 0


def bisect(M, Klo, Khi, target=F(1, 10**30) if False else None):
    tgt = float(10) ** -30
    L, H = mpfr(Klo), mpfr(Khi)
    steps = 0
    while steps < 200:
        with ctx(RoundUp):
            rel = (H - L) / L
        if rel < mpfr(tgt):
            break
        with ctx(RoundDown):
            mid = (L + H) / 2
        s = sign(M, mid)
        if s == 1:
            L = mid
        elif s == -1:
            H = mid
        else:
            break
        steps += 1
    return L, H, steps


from fractions import Fraction as F


def main():
    print("=" * 78)
    print("[1] 独立二分（MPFR 定向舍入机制）：K1(M) 的括号")
    t0 = time.time()
    res = {}
    for M in (88, 89, 90):
        # 起点括号：门槛乘 (1+1e-16) 与 (1+1e-8)
        c_lo, c_hi = cM_iv(M)
        g_lo, g_hi = geom_iv(M)
        with ctx(RoundDown):
            kth_lo = g_lo * mpfr(92) / mpfr(M) * Clo
        with ctx(RoundUp):
            kth_hi = g_hi * mpfr(92) / mpfr(M) * Chi
        with ctx(RoundUp):
            L = kth_lo * (1 + mpfr(1) / mpfr(10)**16)
        with ctx(RoundDown):
            H = kth_hi * (1 + mpfr(1) / mpfr(10)**8)
        sL, sH = sign(M, L), sign(M, H)
        L, H, steps = bisect(M, L, H)
        res[M] = (L, H, steps)
        with ctx(RoundUp):
            relw = (H - L) / L
        print(f"  M={M}: K1 ∈ [{L}, {H}]")
        print(f"      相对宽 {relw}（{steps} 步）；起点符号 ({sL},{sH})；终点符号 "
              f"({sign(M, L)},{sign(M, H)})")
    print(f"  用时 {round(time.time() - t0, 2)} s")

    print("=" * 78)
    print("[2] 与证书端点（d3r3_windows.json）对照：同精度口径、明写相对宽")
    try:
        mine = json.load(open("/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/d3-window-tail/cycle-1/scripts/results/d3r3_windows.json"))
    except FileNotFoundError:
        print("  d3r3_windows.json 不存在：主脚本未跑完，缺该对照")
        return
    for M in (88, 89, 90):
        a, b = F(mine[f"K1_{M}"][0]), F(mine[f"K1_{M}"][1])
        L, H, steps = res[M]
        La, Ha = mpfr(a.numerator) / mpfr(a.denominator), mpfr(b.numerator) / mpfr(b.denominator)
        with ctx(RoundDown):
            inter = (min(H, Ha) - max(L, La))
        with ctx(RoundUp):
            union = (max(H, Ha) - min(L, La)) / La
        print(f"  M={M}: 两括号相交？ {inter > 0}；并集相对宽 ≤ {union}"
              f"（证书相对宽 {float((b - a) / b):.3e}）")
        # 用独立 MPFR 路径验证证书端点符号
        sa, sb = sign(M, La), sign(M, Ha)
        print(f"      独立路径对证书端点的判定：Phi(下端) 正？ {sa == 1}；Phi(上端) 负？ {sb == -1}")


if __name__ == "__main__":
    main()
