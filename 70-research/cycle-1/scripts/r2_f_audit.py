#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-2 第 6 步：判决机制的独立审计（抓自己代码的错）。

  A  界机制的无探针精确审计：对随机 (t, k, s) 逐条用整数比较验证
       (i) 指数向外舍入：Pa <= t·2^k <= Pb（精确整数比较）
       (ii) 整数根的定义式：m^{2^k} <= 2^{P + s·2^k} < (m+1)^{2^k}（精确整数比较）
     这两条加 f 的单调性即给出 lo <= f(t) <= hi，全程不涉及浮点。
  A' 含容性的有容差检查：mpmath(dps=80) 探针的相对精度约 1e-80，故只在区间相对带宽
     大于 1e-60 时要求探针落在区间内；带宽更窄时只比较两者的一致位数。
  B  判决与探针的一致性：凡判定为「不超过顶点值」的样本，探针应给 S(y)/S(V) <= 1+1e-9。
  C  分辨率边界：顶点坐标的部分乘性微扰（修好后一链 + 放大到可行），如实报告
     哪些能判定、哪些只能未决，以及探针读数。
  D  从顶点出发的定向爬山：尝试沿可行扰动提高 S，报告严格界确认的改进次数。
"""
import sys
from fractions import Fraction

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
import gmpy2
import mpmath
from r2_common import (delta_rigorous_bounds, v_vertex, vertex, feasible, S_bounds,
                       f_bounds, pow2_bounds, repair_normalize,
                       LEVEL_MID, LEVEL_FINE, LEVEL_ULTRA, Det)

D_LO7, D_HI7 = delta_rigorous_bounds(10 ** 7)
mpmath.mp.dps = 80


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def S_probe(y, cut=10 ** 5):
    tot = mpmath.mpf(0)
    for t in y:
        e = mpmath.mpf(t.numerator) / mpmath.mpf(t.denominator)
        if e > cut:
            continue
        tot += 3 / (mpmath.mpf(2) ** e - 1)
    return tot


say("=" * 78)
say("route-2 第 6 步：判决机制独立审计")
say("=" * 78)

# ---------------------------------------------------------------- A
say("\n[A] 界机制的无探针精确审计（整数比较；200 组随机 (t, k, s)）")
det = Det(99991)
bad_round = bad_root = 0
for trial in range(200):
    k = det.pick([8, 10, 12, 14, 18])
    s = det.pick([0, 8, 20, 28, 32])
    num = det.between(1, 5000)
    den = det.pick([1, 2, 4, 8, 3, 7, 1024, 1000000])
    t = Fraction(num, den)
    q = 1 << k
    Pa = (t * q).__floor__()
    Pb = -((-t * q).__floor__())
    if not (Pa <= t * q <= Pb):
        bad_round += 1
    for P in (Pa, Pb):
        R = P + s * q
        if R < 0:
            continue
        m, _ = gmpy2.iroot(gmpy2.mpz(1) << R, q)
        m = int(m)
        if not (gmpy2.mpz(m) ** q <= gmpy2.mpz(1) << R < gmpy2.mpz(m + 1) ** q):
            bad_root += 1
say(f"    指数向外舍入违规次数 = {bad_round}；整数根定义式违规次数 = {bad_root}")
say("    这两条成立 ⟹ A_lo <= 2^{Pa/2^k} <= A_hi 与 B_lo <= 2^{Pb/2^k} <= B_hi，")
say("    再由 f 递减得 3/(B_hi−1) <= f(t) <= 3/(A_lo−1)，即 lo <= f(t) <= hi。")

# ---------------------------------------------------------------- A'
say("\n[A'] 含容性检查（探针相对精度约 1e-80；带宽 < 1e-60 时只比一致位数）")
SETS = [
    ("m2=3  δ_lo  W=210",  3,  D_LO7, Fraction(210)),
    ("m2=5  δ_lo  W=200",  5,  D_LO7, Fraction(200)),
    ("m2=10 δ_lo  W=2000", 10, D_LO7, Fraction(2000)),
    ("m2=20 δ_lo  v=70",   20, D_LO7, None),
    ("m2=91 δ_lo  W=205632218873398596256", 91, D_LO7, Fraction(205632218873398596256)),
]


def rand_feasible(m2, d, W, det):
    y = [Fraction(det.between(1, 4096), det.pick([1, 2, 4, 8, 64])) for _ in range(m2)]
    return repair_normalize(y, m2, d, W)


tot_pts = 0
bad_wide = 0
bad_narrow = 0
min_margin = None
for tag, m2, d, W in SETS:
    if W is None:
        W = Fraction(70) * (d ** m2 - 1) / (d - 1)
    ll = Det(777 + m2)
    n_cert = n_un = 0
    V0 = list(vertex(m2, d, W, 0))
    ref_m = S_bounds(V0, *LEVEL_MID)
    ref_u = S_bounds(V0, *LEVEL_ULTRA)
    sV = S_probe(V0)
    for _ in range(60):
        y = rand_feasible(m2, d, W, ll)
        ok, bad = feasible(y, m2, d, W)
        if not ok:
            continue
        tot_pts += 1
        p = S_probe(y)
        for lvl, name in ((LEVEL_MID, "MID"), (LEVEL_ULTRA, "ULTRA")):
            lo, hi = S_bounds(y, *lvl)
            lof = mpmath.mpf(lo.numerator) / mpmath.mpf(lo.denominator)
            hif = mpmath.mpf(hi.numerator) / mpmath.mpf(hi.denominator)
            relband = float((hi - lo) / lo) if lo > 0 else float("inf")
            if relband > 1e-60:
                if not (lof <= p <= hif):
                    bad_wide += 1
                    say(f"    !! 宽区间未包住探针：{tag} {name} 带宽 {relband:.3e}")
                if p > 0:            # p = 0 时探针的全部项都超过截断阈值，无法算余量
                    m = min(float((p - lof) / p), float((hif - p) / p))
                    min_margin = m if min_margin is None else min(min_margin, m)
            else:
                if not (abs(float(p / lof - 1)) < 1e-60 or abs(float(lof / p - 1)) < 1e-60):
                    bad_narrow += 1
        cert = (S_bounds(y, *LEVEL_MID)[1] <= ref_m[0]) or (S_bounds(y, *LEVEL_ULTRA)[1] <= ref_u[0])
        ratio = p / sV
        if cert:
            n_cert += 1
            if ratio > 1 + mpmath.mpf("1e-9"):
                say(f"    !! 判定为「不超过」但探针给 {mpmath.nstr(ratio, 12)}：{tag}")
        else:
            n_un += 1
    say(f"    {tag}: 60 点中已判定 {n_cert}，证书未决 {n_un}")
say(f"    {tot_pts} 个点：宽区间未包住探针的次数 = {bad_wide}；"
    f"窄区间（带宽 < 1e-60）与探针不一致的次数 = {bad_narrow}；最小探针余量 = {min_margin:.3e}")

# ---------------------------------------------------------------- C
say("\n[C] 分辨率边界：顶点坐标的部分乘性微扰（先压链再放大，保证可行）")
for tag, m2, d, W in SETS[:4]:
    if W is None:
        W = Fraction(70) * (d ** m2 - 1) / (d - 1)
    V0 = list(vertex(m2, d, W, 0))
    ref_m = S_bounds(V0, *LEVEL_MID)
    ref_u = S_bounds(V0, *LEVEL_ULTRA)
    sV = S_probe(V0)
    for e in (20, 40):
        eps = Fraction(1, 2 ** e)
        y = list(V0)
        for j in range(max(1, m2 // 6)):
            y[j] = y[j] * (1 - eps)
        y = repair_normalize(y, m2, d, W)
        ok, _ = feasible(y, m2, d, W)
        loU, hiU = S_bounds(y, *LEVEL_ULTRA)
        loM, hiM = S_bounds(y, *LEVEL_MID)
        c_m = hiM <= ref_m[0]
        c_u = hiU <= ref_u[0]
        ce = loU > ref_u[1]
        say(f"    {tag}  2^-{e} 微扰：可行 {ok}  MID {'≤' if c_m else '未决'}"
            f"  ULTRA {'≤' if c_u else ('反例' if ce else '未决')}"
            f"  探针 S(y)/S(V)−1 = {mpmath.nstr(S_probe(y)/sV - 1, 8)}")

# ---------------------------------------------------------------- D
say("\n[D] 从顶点出发的定向爬山（每套 200 次可行扰动试探）")
for tag, m2, d, W in SETS[:4]:
    if W is None:
        W = Fraction(70) * (d ** m2 - 1) / (d - 1)
    ll = Det(4242 + m2)
    V0 = list(vertex(m2, d, W, 0))
    ref_u = S_bounds(V0, *LEVEL_ULTRA)
    sV = S_probe(V0)
    n_better = n_feas = 0
    best = None
    for _ in range(200):
        y = list(V0)
        idx = ll.below(m2)
        y[idx] = y[idx] * (1 + (Fraction(ll.between(1, 1023), 1024) - Fraction(1, 2)))
        y = repair_normalize(y, m2, d, W)
        ok, _ = feasible(y, m2, d, W)
        if not ok:
            continue
        n_feas += 1
        p = S_probe(y)
        if p > sV:
            loU, hiU = S_bounds(y, *LEVEL_ULTRA)
            if loU > ref_u[1]:
                n_better += 1
        if best is None or p / sV > best:
            best = p / sV
    say(f"    {tag}: 可行试探 {n_feas}/200；经严格界确认为反例的 {n_better}；"
        f"探针最好比值 = {mpmath.nstr(best, 12)}")

say("\n（审计的结论只关于本路代码的自洽性；不含新的数学判定。）")
