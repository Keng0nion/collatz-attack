#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4（取整约定穷举与窗口反演）严格有理区间库。

纪律：
  1. 一切算术用 fractions.Fraction 精确进行；超越函数一律用「正项级数部分和 = 下界，
     显式余项界 = 上界」的写法，所有余项界在注释里给出推导。
  2. 本文件不 import、不执行任何旧 cycle-1 / cycle-2 脚本，也不读它们的结果文件。
  3. 本文件只提供工具；判定逻辑在 route4_step7.py 与 route4_chain.py。

级数与余项界（全部为本次自行推导，可逐行复核）：
  ln2 = 2*sum_{k>=0} (1/3)^{2k+1}/(2k+1)；
        余项 sum_{k>N} <= (1/(2N+3))*(1/3)^{2N+3}*9/8   （等比 1/9 求和）
  ln3 = 2*sum_{k>=0} (1/2)^{2k+1}/(2k+1)；
        余项 <= (1/(2N+3))*(1/2)^{2N+3}*4/3           （等比 1/4 求和）
  ln t （1<=t<2）= 2*atanh(u), u=(t-1)/(t+1) in [0,1/3)；
        余项 <= 2*u^{2N+3}/((2N+3)*(1-u^2))
  exp y （0<=y<=1）= sum y^n/n!；截项后余项 <= (y^{N+1}/(N+1)!)/(1-y/(N+2))
  exp y （y 任意 >=0）：先折半至 z=y/2^s<=1 再逐次平方（单调，区间端点平方即可）
  2^v （v>=0）：n=floor(v), r=v-n，2^v = 2^n * exp(r*ln2)
  2^v （v<0）：2^v = 1/2^{-v}
"""
from fractions import Fraction as F
from math import floor, ceil

SERN = 80       # ln 级数项数（ln3 的 2 进制级数收敛最慢，N=80 给 delta 宽 ~1.4e-50）
SERX = 30       # exp 级数项数（y<=1 时余项 <= 1/30! ~ 4.4e-33，展宽后仍 << 1e-32 相对）


# ---------------- 区间基本运算（端点 F，lo <= hi） ----------------
def iadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def isub(a, b):
    return (a[0] - b[1], a[1] - b[0])


def imul(a, b):
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (min(p), max(p))


def idiv(a, b):
    assert not (b[0] <= 0 <= b[1]), "除零区间"
    return imul(a, (1 / b[1], 1 / b[0]))


def iscale(a, k):
    """整数 k 乘区间。"""
    return (a[0] * k, a[1] * k) if k >= 0 else (a[1] * k, a[0] * k)


def wid(a):
    return a[1] - a[0]


SNAP = 130      # 向外取整到的十进制网格位数


def snap(a, nd=SNAP):
    """把区间向外取整到 10^-nd 网格：仍严格包含真值，但压住分母位数。

    用途：区间乘积会把分母位数累加（delta^91 走乘积到 4500 位），传给 exp 级数后
    更会放大 30 倍；对外给 1e-130 的绝对精度对本轮全部判定都绰绰有余。"""
    s = F(10) ** nd
    return (floor(a[0] * s) / s, ceil(a[1] * s) / s)


# ---------------- ln2 / ln3 ----------------
def ln2_bounds(N=SERN):
    s = F(0)
    for k in range(N + 1):
        s += F(1, (2 * k + 1) * 3 ** (2 * k + 1))
    tail = F(9, 8) * F(1, 3 ** (2 * N + 3)) / (2 * N + 3)
    return (2 * s, 2 * (s + tail))


def ln3_bounds(N=SERN):
    s = F(0)
    for k in range(N + 1):
        s += F(1, (2 * k + 1) * 2 ** (2 * k + 1))
    tail = F(4, 3) * F(1, 2 ** (2 * N + 3)) / (2 * N + 3)
    return (2 * s, 2 * (s + tail))


def ln_t_bounds(t, N=SERN):
    """1 <= t < 2 的 Fraction；返回 ln t 的 [lo,hi]。"""
    assert 1 <= t < 2
    u = (t - 1) / (t + 1)
    s = F(0)
    for k in range(N + 1):
        s += u ** (2 * k + 1) / (2 * k + 1)
    lo = 2 * s
    if u == 0:
        return (F(0), F(0))
    tail = 2 * u ** (2 * N + 3) / ((2 * N + 3) * (1 - u * u))
    return snap((lo, lo + tail))


def _cmp_pow2(num, den, e):
    """比较 2^e 与 num/den：返回 -1/0/1（精确整数比较）。"""
    if e >= 0:
        a, b = den << e, num
    else:
        a, b = den, num << (-e)
    return (a > b) - (a < b)


def ln_rat_bounds(x, N=SERN):
    """x > 0 的 Fraction；返回 ln x 的严格 [lo,hi]。"""
    assert x > 0
    num, den = x.numerator, x.denominator
    e = num.bit_length() - den.bit_length()
    while _cmp_pow2(num, den, e) > 0:        # 2^e > x：e 太大
        e -= 1
    while _cmp_pow2(num, den, e + 1) <= 0:   # 2^(e+1) <= x：e 太小
        e += 1
    t = x / F(2) ** e
    assert 1 <= t < 2
    l2 = ln2_bounds(N)
    lt = ln_t_bounds(t, N)
    return snap(iadd(iscale(l2, e), lt))


def ln_interval(a, N=SERN):
    """a = (lo,hi) 全正；返回 ln 的区间（ln 单调增）。"""
    return (ln_rat_bounds(a[0], N)[0], ln_rat_bounds(a[1], N)[1])


# ---------------- exp / 2^v ----------------
def exp_unit_bounds(y, N=SERX):
    """0 <= y <= 1；exp y 的 [lo,hi]。"""
    assert 0 <= y <= 1
    s = F(1)
    term = F(1)
    for n in range(1, N + 1):
        term = term * y / n
        s += term
    # term = y^N/N!；余项从 y^{N+1}/(N+1)! 起
    tail = term * y / (N + 1) / (1 - y / (N + 2))
    return (s, s + tail)


def exp_bounds(y, N=SERX):
    """y 任意 Fraction；exp y 的 [lo,hi]（y<0 时用 1/exp(-y)）。"""
    if y < 0:
        lo, hi = exp_bounds(-y, N)
        return (1 / hi, 1 / lo)
    if y <= 1:
        return exp_unit_bounds(y, N)
    s = 0
    z = y
    while z > 1:
        z = z / 2
        s += 1
    lo, hi = exp_unit_bounds(z, N)
    for _ in range(s):
        lo, hi = lo * lo, hi * hi
    return (lo, hi)


def pow2_bounds(v, N=SERX):
    """v 任意 Fraction；2^v 的 [lo,hi]。"""
    if v == 0:
        return (F(1), F(1))
    if v < 0:
        lo, hi = pow2_bounds(-v, N)
        return (1 / hi, 1 / lo)
    n = int(v)
    r = v - n
    l2 = ln2_bounds()
    elo = exp_bounds(r * l2[0], N)[0]
    ehi = exp_bounds(r * l2[1], N)[1]
    p = F(2) ** n
    return snap((p * elo, p * ehi))


def pow2_interval(vint, N=SERX):
    """2^v 的区间（v 为区间，要求 floor 恒定；r=v-n in [0,1) 避免大指数级数）。"""
    vlo, vhi = vint
    n = floor(vlo)
    assert floor(vhi) == n, "2^v 的整数部分不恒定，需收窄"
    l2 = ln2_bounds()
    r = (vlo - n, vhi - n)
    elo = exp_bounds(r[0] * l2[0], N)[0]
    ehi = exp_bounds(r[1] * l2[1], N)[1]
    p = F(2) ** n
    return snap((p * elo, p * ehi))


def oneminus_pow2delta(vint, dint, N=SERX):
    """(2^v - 1)^delta 的区间。恒等式（避免平方放大）：
       (2^v-1)^delta = exp(delta*(v ln2 + ln(1-2^-v))) = 3^n * exp(r ln3 + delta ln(1-2^-v)),
       v = n + r, n=floor(v), r in [0,1)；z = 2^-v 很小时
       -（z+2z^2) <= ln(1-z) <= -z  （0<z<=1/2 时成立：ln(1-z) = -sum z^k/k）。
       要求 z_hi <= 1/2。
    """
    vlo, vhi = vint
    n = floor(vlo)
    assert floor(vhi) == n, "floor(v) 不恒定"
    r = (vlo - n, vhi - n)
    l3 = ln3_bounds()
    zhi = pow2_bounds(-vlo, N)[1]
    zlo = pow2_bounds(-vhi, N)[0]
    assert zhi <= F(1, 2), "z 不够小"
    dlo, dhi = dint
    y_lo = r[0] * l3[0] - dhi * (zhi + 2 * zhi * zhi)
    y_hi = r[1] * l3[1] - dlo * zlo
    e_lo = exp_bounds(y_lo, N)[0]
    e_hi = exp_bounds(y_hi, N)[1]
    p = F(3) ** n
    return snap((p * e_lo, p * e_hi))


def delta_pow_prod(m, N=SERN):
    """delta^m 的区间（区间乘积，避免 exp 的大指数平方放大；相对宽 ~ m*delta^{m-1}*w(delta)/delta^m）。"""
    dl = delta_bounds(N)
    p = (F(1), F(1))
    for _ in range(m):
        p = snap(imul(p, dl))
    return p


# ---------------- delta 与定理 21 的量 ----------------
def delta_bounds(N=SERN):
    l2 = ln2_bounds(N)
    l3 = ln3_bounds(N)
    return snap((l3[0] / l2[1], l3[1] / l2[0]))


def delta_pow_bounds(m, N=SERN):
    """delta^m 的区间（m>=1），delta in (1,2)。"""
    l2 = ln2_bounds(N)
    l3 = ln3_bounds(N)
    ld = (l3[0] - l2[1], l3[1] - l2[0])      # ln delta 区间
    return exp_bounds(iscale(ld, m)[0], SERX)[0], exp_bounds(iscale(ld, m)[1], SERX)[1]


def geom_bounds(m, N=SERN):
    """(delta^m - 1)/(delta - 1) 的区间。"""
    dm = delta_pow_bounds(m, N)
    dl = delta_bounds(N)
    return snap(idiv((dm[0] - 1, dm[1] - 1), (dl[0] - 1, dl[1] - 1)))


def log2_num_bounds(X0int, N=SERN):
    """log2((162/97)*X0int) 的区间，X0int 为整数。"""
    r = F(162, 97) * X0int
    lnr = ln_rat_bounds(r, N)
    l2 = ln2_bounds(N)
    return idiv(lnr, l2)


# ---------------- 连分数：区间信息的严格抽取 ----------------
def cf_stream(lo, hi, max_terms=2000):
    """
    由严格区间 [lo,hi]（0 < lo <= hi）抽取连分数部分商。
    返回 dict:
      terms  : 已确定的项列表
      idx    : 首个不能确定的项下标（None 表示 max_terms 内全确定）
      floors : 在 idx 处区间对应的 floor 范围 (fl, fh)
      yint   : idx 处的剩余区间
      why    : 退化标记
    """
    terms = []
    ylo, yhi = lo, hi
    for i in range(max_terms):
        fl, fh = floor(ylo), floor(yhi)
        if fl == fh:
            a = fl
            terms.append(a)
            if ylo == a:
                # 区间下端恰为整数：倒数无上界，无法继续（视为需收窄）
                return {"terms": terms, "idx": i + 1, "floors": (fl, fh),
                        "yint": (ylo, yhi), "why": "lower-end-integer"}
            ylo, yhi = 1 / (yhi - a), 1 / (ylo - a)
        else:
            return {"terms": terms, "idx": i, "floors": (fl, fh),
                    "yint": (ylo, yhi), "why": "ambiguous"}
    return {"terms": terms, "idx": None, "floors": None, "yint": (ylo, yhi),
            "why": "max-terms"}


def gamma_q(alpha_int, beta_int, max_terms=2000):
    """
    Lemma 22 的 q(gamma)：alpha in alpha_int, beta in beta_int（alpha<beta），
    找到两个区间的连分数首个相异下标 k，返回 ck=min(ak,bk)+1 的分母。
    返回 dict（'q','k','ak','bk','ck'）或 {'need_refine':True,...}。
    """
    xa, xb = alpha_int, beta_int
    common = []
    for i in range(max_terms):
        fa_l, fa_h = floor(xa[0]), floor(xa[1])
        fb_l, fb_h = floor(xb[0]), floor(xb[1])
        if fa_l == fa_h == fb_l == fb_h:
            a = fa_l
            common.append(a)
            if xa[0] == a or xb[0] == a:
                return {"need_refine": True, "why": "lower-end-integer", "k": i}
            xa = (1 / (xa[1] - a), 1 / (xa[0] - a))
            xb = (1 / (xb[1] - a), 1 / (xb[0] - a))
            continue
        if fa_l != fa_h or fb_l != fb_h:
            return {"need_refine": True, "why": "ambiguous", "k": i,
                    "floors": ((fa_l, fa_h), (fb_l, fb_h))}
        ck = min(fa_l, fb_l) + 1
        p_m2, p_m1 = F(0), F(1)
        q_m2, q_m1 = F(1), F(0)
        for a in common:
            p = a * p_m1 + p_m2
            q = a * q_m1 + q_m2
            p_m2, p_m1 = p_m1, p
            q_m2, q_m1 = q_m1, q
        qk = ck * q_m1 + q_m2
        return {"q": qk, "k": i, "ak": fa_l, "bk": fb_l, "ck": ck,
                "n_common": len(common)}
    return {"need_refine": True, "why": "max-terms"}


# ---------------- 自测 ----------------
def _selftest():
    import mpmath as mp
    mp.mp.dps = 50
    ok = True
    l2 = ln2_bounds()
    l3 = ln3_bounds()
    ld = delta_bounds()
    print("[selftest] ln2 宽度 = %.3e" % float(l2[1] - l2[0]))
    print("[selftest] ln3 宽度 = %.3e" % float(l3[1] - l3[0]))
    print("[selftest] delta 宽度 = %.3e" % float(ld[1] - ld[0]))
    print("[selftest] mpmath ln2 在区间内 litmus: 前 40 位 =",
          mp.nstr(mp.log(2), 40))
    # 用小整数分数反查 ln 区间
    for x in (F(2), F(3), F(112590, 97), F(162 * 695 // 97)):
        b = ln_rat_bounds(x)
        v = mp.log(mp.mpf(x.numerator) / x.denominator)
        inside = float(b[0]) <= float(v) <= float(b[1])
        print("[selftest] ln(%s): 宽度 %.2e，mpmath 值在区间内 = %s" %
              (x, float(b[1] - b[0]), inside))
        ok = ok and inside
    # exp 自测：exp(1) 与 e，exp(0.5) 与 sqrt(e)
    e_lo, e_hi = exp_bounds(F(1))
    print("[selftest] exp(1) 区间宽 %.2e，含 mpmath e = %s" %
          (float(e_hi - e_lo),
           float(e_lo) <= float(mp.e) <= float(e_hi)))
    p_lo, p_hi = pow2_bounds(F(1, 2))
    print("[selftest] 2^(1/2) 区间宽 %.2e，含 mpmath 值 = %s" %
          (float(p_hi - p_lo),
           float(p_lo) <= float(mp.sqrt(2)) <= float(p_hi)))
    p_lo, p_hi = pow2_bounds(F(80))
    print("[selftest] 2^80 区间宽 %.2e（应为 0，整数幂）" % float(p_hi - p_lo))
    # 连分数自测（教科书例）：alpha=100/201=[0;2,100], beta=101/203=[0;2,101]
    # 首个相异下标 k=2，min(100,101)+1=101 → gamma=[0;2,101]=101/203，q=203。
    tiny = F(1, 10 ** 12)
    g = gamma_q((F(100, 201), F(100, 201) + tiny),
                (F(101, 203), F(101, 203) + tiny))
    print("[selftest] gamma_q(100/201, 101/203) =", g, "（期望 q=203,k=2,ck=101）")
    ok = ok and g.get("q") == 203 and g.get("k") == 2 and g.get("ck") == 101
    # 随机核对：用 gamma_q 的下界性质——区间 (a+tiny, b) 内不得存在分母 < q 的分数
    import random
    random.seed(4)
    bad = 0
    n_ref = 0
    for _ in range(300):
        d1 = random.randint(3, 60)
        d2 = random.randint(3, 60)
        a = F(random.randint(1, d1 - 1), d1)
        b = F(random.randint(1, d2 - 1), d2)
        if a >= b:
            a, b = b, a
        if a == b:
            continue
        gq = gamma_q((a, a + tiny), (b, b + tiny))
        if "q" not in gq:
            n_ref += 1
            continue
        q = gq["q"]
        alo, bhi = a + tiny, b      # (alo,bhi) 含于真实区间
        best = None
        for qq in range(1, 401):
            n = floor(alo * qq) + 1
            while n < bhi * qq:
                if alo < F(n, qq) < bhi:
                    best = qq
                    break
                n += 1
            if best:
                break
        if best is not None and best < q:
            bad += 1
            print("[selftest] 违反下界性质：区间 (%s,%s) gamma_q=%s 但存在分母 %s" %
                  (a, b, q, best))
    print("[selftest] gamma_q 随机核对：违反数 = %d，需收窄数 = %d（400 内穷举）"
          % (bad, n_ref))
    ok = ok and bad == 0
    print("[selftest] 总体 =", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    _selftest()
