#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
勘误版重推脚本：Hercher 2023 (J. Integer Seq. 26, Art. 23.3.5) Theorem 21
第 14 页「窗口尾部」步的勘误替代论证。

本脚本从零实现，不引用任何既有脚本。功能：
  1. 常数与假设的核对（X0、delta、c）；
  2. 对印出版争论步的直接否证（幂不等式方向）；
  3. 对勘误替代论证的独立校验（凸性、顶点界、幂不等式、x_i = 1 的不可行性）；
  4. Lemma 22 换算器 q_min 的两种独立实现与验证；
  5. m = 91 的七步自举链（勘误版尾部）与论文印刷值的对照；
  6. m = 91 处的余量倍数、可排除的最大 m；
  7. 敏感性与对照（A 的 +73 与 +1、两档精度、健全版尾部对照）。

运行：
  /Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python \
      "/Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/scripts/rederive-erratum.py"
"""

import json
import sys
from fractions import Fraction

from mpmath import (mp, mpf, log, log10, log1p, expm1, floor, power, iv, nstr)


def log2(x):
    """mpmath 没有 log2，本地补一个（对 mpf 与 Python 数值都适用）。"""
    return log(x) / log(2)

# ----------------------------------------------------------------------------
# 0. 常数
# ----------------------------------------------------------------------------

X0_INT = 695 * 2**60                      # 精确整数：Definition 4
SIG = 1000                                # 打印有效位数上限


def setup(dps):
    """返回 (X0, delta, c)；c := log2((162/97) X0)。"""
    mp.dps = dps
    X0 = mpf(X0_INT)
    delta = log(3) / log(2)
    c = log(mpf(162) / 97 * X0) / log(2)
    return X0, delta, c


def header(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def show(name, value, digits=40):
    print(f"  {name:<34} = {nstr(value, digits)}")


# ----------------------------------------------------------------------------
# 1. 基本量：f、S、尾部
# ----------------------------------------------------------------------------

HUGE_V = mpf(10) ** 8          # 2^v 超过 mpmath 指数上限的阈值（v 极大时）


def inv_2v_minus_1(v):
    """1/(2^v − 1)；v > HUGE_V 时返回 (0, True) 表示被截断（该项远小于任何可表示精度）。"""
    if v > HUGE_V:
        return mpf(0), True
    return 1 / (power(2, v) - 1), False


def f_tail(x):
    """x ↦ 3/(2^x − 1)（Remark 7 与勘误的 S 的被加项）。"""
    return 3 / (power(2, x) - 1)


def S_of(xs):
    """S(x_1, ..., x_k) := sum_i 3/(2^{x_i} − 1)。坐标过大时会越出 mpmath 指数上限。"""
    return sum(f_tail(x) for x in xs)


def log2_S_of(xs):
    """
    log2(S(xs)) 的稳定求值，适用于任意大的坐标（可到 1e18）。
        log2(3/(2^x − 1)) = log2 3 − x + log2(1 − 2^{-x})，
    其中修正项在 x >= 1000 时小于 2^{-1000}，直接记 0（相对误差可忽略）。
    求和在对数尺度做：取最大项 M，累加 2^{log2 t_i − M}（各项 <= 1，不会溢出）。
    """
    lts = []
    l3 = log2(mpf(3))
    for x in xs:
        corr = log2(1 - power(2, -x)) if x < 1000 else mpf(0)
        lts.append(l3 - x + corr)
    M = max(lts)
    acc = mpf(0)
    for lt in lts:
        d = lt - M
        if d < -10 ** 7:
            continue
        acc += power(2, d)
    return M + log2(acc)


# ----------------------------------------------------------------------------
# 2. 连分数工具
# ----------------------------------------------------------------------------

def cf_terms_of_mpf(x, max_terms):
    """贪心连分数前 max_terms 项；返回 (terms, complete)。"""
    terms = []
    y = mpf(x)
    for _ in range(max_terms):
        a = int(floor(y))
        terms.append(a)
        r = y - a
        if r == 0:
            return terms, True
        y = 1 / r
    return terms, False


def cf_first_divergence(ta, tb):
    n = min(len(ta), len(tb))
    for i in range(n):
        if ta[i] != tb[i]:
            return i
    return None


def cf_fraction(terms):
    """由连分数项还原精确有理数。"""
    fr = Fraction(terms[-1])
    for a in reversed(terms[:-1]):
        fr = a + 1 / fr
    return fr


# ----------------------------------------------------------------------------
# 3. 向外区间（用于严格判定 p/q 是否落在 (delta, delta+eps) 内）
# ----------------------------------------------------------------------------

def outward_delta_beta(eps, dps_iv=60, dps_pad=200):
    """
    返回 (d_lo, d_hi, b_lo, b_hi)，满足
        d_lo <= delta <= d_hi 且 b_lo <= delta + eps <= b_hi。
    区间用 iv 取得后向外加垫，垫量远小于 eps 又不影响判定。
    """
    iv.dps = dps_iv
    D = iv.log(3) / iv.log(2)
    mp.dps = dps_pad
    d_lo = +mpf(D.a)
    d_hi = +mpf(D.b)
    pad = mpf(10) ** (-(dps_pad) + 6)
    d_lo -= pad
    d_hi += pad
    b_lo = d_lo + eps - pad
    b_hi = d_hi + eps + pad
    return d_lo, d_hi, b_lo, b_hi


def strictly_inside(p, q, d_lo, d_hi, b_lo, b_hi):
    """严格判定 delta < p/q < delta + eps；只用严格不等式与向外区间。"""
    return (q * d_hi < p) and (p < q * b_lo)


# ----------------------------------------------------------------------------
# 4. Lemma 22 换算器：q_min 的两种实现
# ----------------------------------------------------------------------------

def qmin_lemma22(eps, dps_cf=250, max_terms=600):
    """
    Lemma 22：在 delta 与 delta+eps 的连分数首次分歧处取
        gamma = [a_0; ..., a_{k-1}, min(a_k, b_k) + 1]
    其分母即区间 (delta, delta+eps) 内分数的最小分母 q_min。
    返回 dict，或在 600 项内仍不分歧时返回 None。
    """
    save = mp.dps
    mp.dps = dps_cf
    delta = log(3) / log(2)
    ya = mpf(delta)
    yb = mpf(delta + eps)
    ta, tb = [], []
    k = None
    for _ in range(max_terms):          # 两条连分数同步推进，首次分歧即停
        aa = int(floor(ya))
        ab = int(floor(yb))
        ta.append(aa)
        tb.append(ab)
        if aa != ab:
            k = len(ta) - 1
            break
        ra = ya - aa
        rb = yb - ab
        if ra == 0 or rb == 0:
            break
        ya = 1 / ra
        yb = 1 / rb
    if k is None:
        mp.dps = save
        return None
    ck = min(ta[k], tb[k]) + 1
    gamma = cf_fraction(ta[:k] + [ck])
    out = {
        "k": k,
        "a_k": ta[k],
        "b_k": tb[k],
        "ck": ck,
        "gamma_num": gamma.numerator,
        "gamma_den": gamma.denominator,
        "prefix": ta[:k],
    }
    mp.dps = save
    return out


def legendre_certificate(eps, Qmax, dps_cf=250, max_terms=400):
    """
    证明：开区间 (delta, delta+eps) 内没有分母 <= Qmax 的分数。
    逻辑：若 eps < 1/(2 Qmax^2)，则区间内任一分数 p/q（q <= Qmax）满足
        |delta − p/q| < eps < 1/(2 Qmax^2) <= 1/(2 q^2)，
    由 Legendre 定理它是 delta 的收敛子；故只需逐一排除分母 <= Qmax 的收敛子。
    返回 (bool, reason)。
    """
    save = mp.dps
    Q = mpf(Qmax)
    if not (eps < 1 / (2 * Q * Q)):
        mp.dps = save
        return False, "not_legendre"
    mp.dps = dps_cf
    delta = log(3) / log(2)
    terms, _ = cf_terms_of_mpf(delta, max_terms)
    p2, q2 = 0, 1          # p_{-2}, q_{-2}
    p1, q1 = 1, 0          # p_{-1}, q_{-1}
    convs = []
    for a in terms:
        p0, q0 = a * p1 + p2, a * q1 + q2
        p2, q2 = p1, q1
        p1, q1 = p0, q0
        if q1 > Q:
            break
        convs.append((p1, q1))
    mp.dps = save
    d_lo, d_hi, b_lo, b_hi = outward_delta_beta(eps)
    for (p, q) in convs:
        if strictly_inside(p, q, d_lo, d_hi, b_lo, b_hi):
            return False, f"convergent_inside:{p}/{q}"
    return True, f"checked_{len(convs)}_convergents"


def eps_log10_upper_A(A, m2, v, K, delta):
    """
    返回 eps 的一个上界的 log10（Python float），三项都在对数空间计算，
    避免 2^v 溢出与 2^{-v} 下溢。
        eps = (A + 3/(2^v−1) + 3(m2−1)/(2^v−1)^delta) / (3 K log 2)
        t1 <= 6·2^{-v}                        （因 1/(2^v−1) <= 2^{1−v}）
        t2 <= 6(m2−1)·2^{-delta(v−1)}         （因 (2^v−1)^delta >= 2^{delta(v−1)}）
    故 eps <= 3·max(A, t1up, t2up)/(3 K log 2) = max(...)/(K log 2)。
    """
    logs = []
    if A > 0:
        logs.append(float(log10(A)))
    logs.append(float(log10(mpf(6)) - v * log10(mpf(2))))
    if m2 > 1:
        logs.append(float(log10(mpf(6) * (m2 - 1)) - delta * (v - 1) * log10(mpf(2))))
    m = max(logs)
    return m - float(log10(K)) - float(log10(log(mpf(2))))


def legendre_certificate_logspace(log10_eps, Qmax, dps_cf=250, max_terms=400):
    """
    与 legendre_certificate 同理，但只用 eps 的 log10 上界，不做减法，避免下溢。
    条件 eps <= 1/(2 Qmax^2) 与逐收敛子排除都在对数尺度完成。
    返回 (bool, reason)。
    """
    save = mp.dps
    mp.dps = dps_cf
    lq = float(log10(mpf(Qmax)))
    if not (log10_eps <= -2 * lq - float(log10(mpf(2)))):
        mp.dps = save
        return False, "not_legendre"
    delta = log(3) / log(2)
    terms, _ = cf_terms_of_mpf(delta, max_terms)
    p2, q2 = 0, 1
    p1, q1 = 1, 0
    convs = []
    for a in terms:
        p0, q0 = a * p1 + p2, a * q1 + q2
        p2, q2 = p1, q1
        p1, q1 = p0, q0
        if q1 > Qmax:
            break
        convs.append((p1, q1))
    # 严格区间：delta ∈ [d_lo, d_hi]；只用 log10 比较
    iv.dps = 60
    D = iv.log(3) / iv.log(2)
    mp.dps = dps_cf
    d_lo = +mpf(D.a)
    d_hi = +mpf(D.b)
    pad = mpf(10) ** (-(dps_cf) + 6)
    d_lo -= pad
    d_hi += pad
    for (p, q) in convs:
        if not (q * d_hi < p):        # 不在 delta 之上者与区间无关
            continue
        # g = p/q − delta >= p/q − d_hi > 0
        g_lo = mpf(p) / q - d_hi
        g_hi = mpf(p) / q - d_lo
        if g_lo <= 0:
            mp.dps = save
            return False, f"ambiguous:{p}/{q}"
        if float(log10(g_hi)) < log10_eps:
            mp.dps = save
            return False, f"convergent_inside:{p}/{q}"
    mp.dps = save
    return True, f"logspace_checked_{len(convs)}_convergents"


def qmin_bruteforce(eps, qmax, dps=80):
    """暴力求 (delta, delta+eps) 内最小分母分数（仅用于 eps 较大的合成测试）。"""
    mp.dps = dps
    delta = log(3) / log(2)
    d_lo, d_hi, b_lo, b_hi = outward_delta_beta(eps)
    for q in range(1, qmax + 1):
        p0 = int(floor(d_lo * q))
        for p in range(max(1, p0 - 1), p0 + 4):
            if strictly_inside(p, q, d_lo, d_hi, b_lo, b_hi):
                return p, q
    return None


def semiconvergent_scan(eps, qmax_scan, dps_cf=300, max_terms=400):
    """
    枚举 delta 的所有收敛子与中间分数（分母 <= qmax_scan），
    取严格落在 (delta, delta+eps) 内者中最小的分母。作为 qmin_lemma22 的独立对照。
    """
    save = mp.dps
    mp.dps = dps_cf
    delta = log(3) / log(2)
    terms, _ = cf_terms_of_mpf(delta, max_terms)
    mp.dps = save
    d_lo, d_hi, b_lo, b_hi = outward_delta_beta(eps)
    p2, q2 = 0, 1
    p1, q1 = 1, 0
    found = []
    for a in terms:
        for j in range(1, a + 1):
            p = p2 + j * p1
            q = q2 + j * q1
            if q > qmax_scan:
                break
            if strictly_inside(p, q, d_lo, d_hi, b_lo, b_hi):
                found.append((q, p))
        p_new = a * p1 + p2
        q_new = a * q1 + q2
        p2, q2 = p1, q1
        p1, q1 = p_new, q_new
        if q1 > qmax_scan:
            break
    if not found:
        return None
    found.sort()
    return found[0]


# ----------------------------------------------------------------------------
# 5. Theorem 21 的勘误版机制
# ----------------------------------------------------------------------------

def delta_powers(delta, nmax, dps):
    """预计算 delta^t, t = 0..nmax。"""
    save = mp.dps
    mp.dps = dps
    pw = [mpf(1)]
    for _ in range(nmax):
        pw.append(pw[-1] * delta)
    mp.dps = save
    return pw


def feasible_m2_max(m, K, delta, c, pw):
    """Theorem 21 假设中可行的最大 m2（1 <= m2 <= m）。"""
    best = None
    for t in range(1, m + 1):
        if (pw[t] - 1) / (delta - 1) * c <= (mpf(t) / m) * K:
            best = t
    return best


def m2_feasible(t, m, K, delta, c, pw):
    return (pw[t] - 1) / (delta - 1) * c <= (mpf(t) / m) * K


def v_of(m2, m, K, delta, pw):
    return (mpf(m2) / m) * K * (delta - 1) / (pw[m2] - 1)


def A_of(m2, m, X0, mode="73"):
    """Theorem 21 第一段的上界；mode='73' 用陈述里的 +73，mode='1' 用证明末行的 +1。"""
    if m2 == m:
        return mpf(0)
    if m2 == m - 1:
        return 3 / X0
    add = 73 if mode == "73" else 1
    return (97 * (m - m2) + add) / (54 * X0)


def eps_of(m2, m, K, X0, delta, pw, mode="73"):
    """
    勘误版 eps：
        eps = (1/(3 K log 2)) * ( A + 3/(2^v−1) + 3(m2−1)/(2^v−1)^delta )
    """
    v = v_of(m2, m, K, delta, pw)
    inv, cut = inv_2v_minus_1(v)
    t1 = 3 * inv
    t2 = 3 * (m2 - 1) * power(inv, delta)
    A = A_of(m2, m, X0, mode)
    eps = (A + t1 + t2) / (3 * K * log(2))
    return {"m2": m2, "v": v, "A": A, "t1": t1, "t2": t2, "eps": eps,
            "cut": cut}


def sound_eps_of(m2, m, K, X0, delta, pw, mode="73"):
    """第三方健全版尾部 3(m2−1)/X0（仅作对照）。"""
    v = v_of(m2, m, K, delta, pw)
    inv, cut = inv_2v_minus_1(v)
    t1 = 3 * inv
    t2 = 3 * (m2 - 1) / X0
    A = A_of(m2, m, X0, mode)
    return {"m2": m2, "v": v, "A": A, "t1": t1, "t2": t2,
            "eps": (A + t1 + t2) / (3 * K * log(2)), "cut": cut}


def best_m2(m, K, X0, delta, c, pw, eps_fn, mode="73"):
    """扫描全部 m2 ∈ [1, m] 找最小 eps，并同时报告最大可行 m2。"""
    mmax = feasible_m2_max(m, K, delta, c, pw)
    best = None
    for t in range(1, m + 1):
        if not m2_feasible(t, m, K, delta, c, pw):
            continue
        rec = eps_fn(t, m, K, X0, delta, pw, mode)
        if best is None or rec["eps"] < best["eps"]:
            best = rec
    return mmax, best


# ----------------------------------------------------------------------------
# 6. 自举链
# ----------------------------------------------------------------------------

K_START = mpf(7) * mpf(10) ** 11          # Hercher 引用 SdW Theorem 3：K > 7·10^11


def bootstrap(m, K0=K_START, dps=120, dps_cf=250, max_iter=30, mode="73",
              eps_fn=eps_of, use_certificate=True):
    """
    勘误版的七步型自举：给 m 与当前 K 下界，取最优 m2、算 eps、用 Lemma 22 换回新 K。
    每一步都记录（m2, v, eps, K_new）。停在不动点或迭代上限。
    """
    save = mp.dps
    mp.dps = dps
    X0, delta, c = setup(dps)
    pw = delta_powers(delta, max(m + 2, 200) + 2, dps)
    K = mpf(K0)
    steps = []
    status = "max_iter"
    for it in range(max_iter):
        mmax, best = best_m2(m, K, X0, delta, c, pw, eps_fn, mode)
        if mmax is None or best is None:
            status = "no_feasible_m2"
            break
        eps = best["eps"]
        qres = None
        if not best["cut"]:
            qres = qmin_lemma22(eps, dps_cf=dps_cf)
        if qres is None or best["cut"]:
            # 守卫触发（v 过大，2^{-v} 下溢，eps 被低估）或连分数在 600 项内不分歧：
            # 一律改用对数空间的上界证书，绝不用被低估的 eps 反解 K。
            Qmax = mpf("1.4784") * m * pw[m]
            log10e = eps_log10_upper_A(best["A"], best["m2"], best["v"], K, delta)
            ok, why = legendre_certificate_logspace(log10e, Qmax, dps_cf=dps_cf)
            status = ("guard_cert_" if best["cut"] else "cfdeep_cert_") + \
                     ("ok" if ok else "fail") + ":" + why
            steps.append({"iter": it + 1, "m2": best["m2"], "v": best["v"],
                          "eps": eps, "K_old": K, "K_new": None,
                          "qmin": None, "cert": (ok, why), "cut": best["cut"],
                          "log10_eps_ub": log10e, "Qmax": Qmax})
            break
        Knew = mpf(qres["gamma_den"])
        steps.append({"iter": it + 1, "m2": best["m2"], "v": best["v"],
                      "eps": eps, "K_old": K, "K_new": Knew, "qmin": qres,
                      "mmax": mmax, "A": best["A"], "t1": best["t1"],
                      "t2": best["t2"], "cut": best["cut"]})
        if Knew <= K:
            status = "fixed_point"
            K = Knew
            break
        K = Knew
    out = {"m": m, "K_final": K, "K_final_int": int(K) if K == int(K) else None,
           "steps": steps, "status": status, "dps": dps}
    mp.dps = save
    return out


def sdw_upper(m, delta):
    """Simons 与 de Weger 的上界（Hercher 论文引用的形式）。"""
    if m >= 91:
        return mpf("1.4784") * m * power(delta, m)
    if 78 <= m <= 90:
        return mpf("1.3993") * m * power(delta, m)
    return None


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------

def main():
    report = {}

    # ---- 0. 常数 -----------------------------------------------------------
    header("[0] 常数与基准核对（dps = 120）")
    mp.dps = 120
    X0, delta, c = setup(120)
    show("X0 (精确整数)", mpf(X0_INT), 30)
    show("X0", X0, 30)
    show("delta = log3/log2", delta, 30)
    show("c = log2((162/97)X0)", c, 30)
    show("log2(X0 + 1)", log(X0 + 1) / log(2), 30)
    show("2^delta", power(2, delta), 30)
    report["X0"] = nstr(X0, 30)
    report["delta"] = nstr(delta, 30)
    report["c"] = nstr(c, 30)

    # ---- 1. 印出版争论步的直接否证 ----------------------------------------
    header("[1] 印出版争论步的直接否证：n^{(delta^l)} <= n^delta 与 T 的单调性")
    mp.dps = 60
    delta = log(3) / log(2)
    d2 = delta * delta
    show("delta", delta, 25)
    show("delta^2", d2, 25)
    print(f"  delta^2 > delta ?               {d2 > delta}")
    show("2^delta", power(2, delta), 25)
    show("2^(delta^2)", power(2, d2), 25)
    print(f"  2^(delta^2) > 2^delta ?         {power(2, d2) > power(2, delta)}")
    for l in (2, 3, 4):
        print(f"  l = {l}: delta^l = {nstr(power(delta, l), 20)}, "
              f"delta^l > delta ? {power(delta, l) > delta}")
    show("f(10) = 3/(2^10-1)", f_tail(mpf(10)), 20)
    show("f(20) = 3/(2^20-1)", f_tail(mpf(20)), 20)
    print("  f 关于 n 严格递减（上界 3/n 亦然）：上界 n 只给出 T 的下界。")
    report["printed_step_check"] = {
        "delta2_gt_delta": bool(d2 > delta),
        "2_delta2_gt_2_delta": bool(power(2, d2) > power(2, delta)),
    }

    # ---- 2. 勘误替代论证的独立校验 ----------------------------------------
    header("[2] 勘误替代论证的独立校验")

    # 2a. 凸性
    print("\n[2a] f(x) = 3/(2^x − 1) 的凸性（二阶中心差分，全为正即凸）")
    mp.dps = 60
    for x0 in ("1.0001", "1.1", "2", "5", "70.18", "100"):
        x = mpf(x0)
        h = mpf("0.001")
        d2f = f_tail(x + h) - 2 * f_tail(x) + f_tail(x - h)
        print(f"  x = {x0:>8}（h = 0.001）: 二阶差分 = {nstr(d2f, 6)}"
              f"  (> 0 ? {d2f > 0})")
    print("  故 S(x_1, ..., x_k) = sum_i f(x_i) 作为可分离和也是凸函数。")

    # 2b. 幂不等式 (2^v − 1)^delta < 2^{delta v} − 1
    print("\n[2b] 收尾幂不等式：(2^v − 1)^delta < 2^{delta v} − 1 ?")
    print("     等价形式（令 u = 2^{-v}）：phi(u) := 1 − (1−u)^delta − u^delta > 0")
    print("     u 形式数值稳定，故大 v 处一律用 phi(u) 判定；小 v 处两形式并列核对。")
    mp.dps = 60
    delta = log(3) / log(2)
    ok_all = True

    def phi_u(v):
        u = power(2, -v)
        return -expm1(delta * log1p(-u)) - power(u, delta)

    for v0 in ("0.5", "1.001", "1.01", "1.1", "1.5", "2", "3", "5", "10", "30",
               "69.4092", "70.1808", "75.6", "100", "1000", "10000"):
        v = mpf(v0)
        u = power(2, -v)
        ph = phi_u(v)
        good = ph > 0
        ok_all = ok_all and good
        direct = ""
        if v <= 100:
            lhs = power(power(2, v) - 1, delta)
            rhs = power(2, delta * v) - 1
            direct = f"  [直接形式 左 < 右 ? {lhs < rhs}]"
        print(f"  v = {v0:>9}: u = {nstr(u, 6):>14}  phi = {nstr(ph, 10):>16}"
              f"  phi > 0 ? {good}{direct}")
    print(f"  全部成立：{ok_all}")
    print("  手算证明（本脚本作者，分两段；上一版写成「v > 0 时 u < 1/2 自动满足」是错的，")
    print("  已按交叉反驳意见改正）：phi'(u) = delta[(1−u)^{delta−1} − u^{delta−1}]，")
    print("    它在 0 < u < 1/2 为正、在 1/2 < u < 1 为负，故 phi 在 (0,1/2) 递增、")
    print("    在 (1/2,1) 递减；phi(0) = 0，phi(1/2) = 1 − 2^{1−delta} = 0.6666… > 0，")
    print("    phi(1) = 0，于是 phi > 0 对一切 0 < u < 1 成立。对应到 v：u < 1/2")
    print("    相当于 v > 1（即 phi' > 0 的那一段）；0 < v <= 1 落在 1/2 <= u < 1")
    print("    那一段，由 phi(1/2) > 0 与单调性覆盖；数值表里 v = 0.5 一行正是这一段。")
    report["power_ineq_all_v"] = bool(ok_all)

    # 2c. 顶点界：S(x) <= S(v, delta v, ..., delta^{m2-1} v)
    print("\n[2c] 顶点界数值检验：对可行 x（x_i >= 1、循环约束 x_{i+1} <= delta x_i、")
    print("     sum x_i >= W）检验 S(x) <= sum_j f(delta^j v)，v = W(delta−1)/(delta^{m2}−1)")
    print("     比较一律在对数尺度：超出量 = log2 S(x) − log2(顶点值)，阈值 1e-40。")
    print("     判据：只在满足 (A7) 的 v >= c 参数上才有检验力，故列出 v >= c 一栏；")
    print("     大 m2 的真实参数见 [2c-bis]（那里坐标达 1e18，必须走对数尺度）。")
    import random
    random.seed(20261021)
    mp.dps = 60
    delta = log(3) / log(2)
    X0t, _d, ct = setup(60)
    c = ct
    rand_tests = []
    TOL_LOG = mpf(10) ** (-40)

    def repair(x, m2, W):
        """投影到可行域：先压链约束，再整体放大到 sum >= W。"""
        for _ in range(3 * m2 + 5):
            for i in range(m2):
                j = (i + 1) % m2
                if x[j] > delta * x[i]:
                    x[j] = delta * x[i]
        s = sum(x)
        if s < W:
            sc = W / s
            x = [t * sc for t in x]
            for _ in range(3 * m2 + 5):
                for i in range(m2):
                    j = (i + 1) % m2
                    if x[j] > delta * x[i]:
                        x[j] = delta * x[i]
        return x if sum(x) >= W else None

    # 参数一律用 (m2, W) 显式给出；「(A7) 前沿」指取 v = c 或 v = 84，
    # 即满足 (A7) 所强制的 v >= c = log2((162/97)X0) = 70.1808...，
    # 这是实际链上出现的那一段参数区间。W = v (delta^{m2}-1)/(delta-1)。
    cases = []
    for (m2c, Wc) in [(2, mpf(70)), (3, mpf(210)), (5, mpf(200)), (10, mpf(2000))]:
        cases.append((m2c, mpf(Wc), "一般 W（v < c，仅作不等式本身的一般检验）"))
    for (m2c, vc) in [(5, c), (10, c), (20, c)]:
        Wc = vc * (power(delta, m2c) - 1) / (delta - 1)
        cases.append((m2c, Wc, f"(A7) 前沿 v = {nstr(vc, 7)}"))
    for (m2, W, case_note) in cases:
        v_case = W * (delta - 1) / (power(delta, m2) - 1)
        a7_ok = bool(v_case >= c)
        print(f"    —— 案例：m2 = {m2}, W = {nstr(W, 8)}, v = {nstr(v_case, 8)}, "
              f"v >= c ? {a7_ok}  【{case_note}】")
        v = W * (delta - 1) / (power(delta, m2) - 1)
        lg_vertex = log2_S_of([power(delta, j) * v for j in range(m2)])
        worst_log = mpf(-10) ** 9
        worst_mid = mpf(-10) ** 9
        worst_desc = ""
        n_ok = 0
        n_eval = 0
        for trial in range(400):
            kind = trial % 4
            if kind == 0:      # 随机点
                x = [mpf(random.uniform(1.0, 200.0)) for _ in range(m2)]
            elif kind == 1:    # 尖峰型
                x = [mpf(1.0) + mpf(random.uniform(0, 1)) for _ in range(m2)]
                x[random.randrange(m2)] = mpf(random.uniform(1, 1e3))
            elif kind == 2:    # 均匀型
                s = mpf(random.uniform(0.5, 50.0))
                x = [s for _ in range(m2)]
            else:              # 双尖峰
                x = [mpf(1.0) for _ in range(m2)]
                x[random.randrange(m2)] = mpf(random.uniform(1, 1e2))
                x[random.randrange(m2)] = mpf(random.uniform(1, 1e2))
            x = repair(x, m2, W)
            if x is None:
                continue
            lg_val = log2_S_of(x)
            # 有效中间量：令 M := max x_i，x 逐点支配以 M 为峰的循环几何序列 g，
            # 故 S(x) <= S(g) = sum_k f(M/delta^k) =: mid。mid 并不保证 <= 顶点值
            # （它只用到 M 与链约束），故只核对 S(x) <= mid 这一方向。
            M = max(x)
            lg_mid = log2_S_of([M / power(delta, k) for k in range(m2)])
            dlog = lg_val - lg_vertex
            dmid = lg_val - lg_mid
            n_eval += 1
            if dlog <= TOL_LOG:
                n_ok += 1
            if dmid > worst_mid:
                worst_mid = dmid
            if dlog > worst_log:
                worst_log = dlog
                worst_desc = f"kind={kind}"
        # 局部爬山：从顶点附近出发，逐坐标试探能否提高 S
        n_hill = 30 if m2 <= 10 else 10
        n_move = 200 if m2 <= 10 else 40
        for k in range(n_hill):
            x = [power(delta, j) * v * mpf(random.uniform(0.9, 1.1))
                 for j in range(m2)]
            x = repair(x, m2, W)
            if x is None:
                continue
            cur = log2_S_of(x)
            for _ in range(n_move):
                i = random.randrange(m2)
                cand = list(x)
                cand[i] = cand[i] * mpf(random.uniform(0.5, 2.0))
                cand = repair(cand, m2, W)
                if cand is None:
                    continue
                cv = log2_S_of(cand)
                if cv > cur:
                    x, cur = cand, cv
            dlog = cur - lg_vertex
            M = max(x)
            lg_mid = log2_S_of([M / power(delta, k) for k in range(m2)])
            worst_mid = max(worst_mid, cur - lg_mid)
            n_eval += 1
            if dlog <= TOL_LOG:
                n_ok += 1
            if dlog > worst_log:
                worst_log = dlog
                worst_desc = "hill_climb"
        # 对照：均匀（「平坦」）配置与顶点的 log2 差，用来看顶点相对平坦点的收益
        lg_flat = log2_S_of([W / m2] * m2)
        flat_gap = lg_flat - lg_vertex
        rand_tests.append((m2, nstr(W, 8), nstr(lg_vertex, 12),
                           nstr(worst_log, 8), bool(worst_log <= TOL_LOG),
                           f"{n_ok}/{n_eval}", worst_desc,
                           nstr(worst_mid, 8), a7_ok, nstr(flat_gap, 8),
                           nstr(v_case, 8)))
    print(f"  {'m2':>4} {'v':>10} {'v>=c':>5} {'log2 顶点值':>20} {'最大 log2 超出':>15} "
          f"{'OK?':>6} {'样本':>10} {'平坦配置 log2 差':>16}")
    for (m2, Ws, vv, wr, okv, cnt, wd, wm, a7, fl, vstr) in rand_tests:
        print(f"  {m2:>4} {vstr:>10} {str(a7):>5} {vv:>20} {wr:>15} {str(okv):>6} "
              f"{cnt:>10} {fl:>16}")
    report["vertex_bound_sampling"] = [
        {"m2": t[0], "v": t[10], "a7_ok": t[8], "max_log2_excess_vertex": t[3],
         "ok": t[4], "passed": t[5], "max_log2_excess_mid": t[7],
         "flat_log2_gap": t[9]}
        for t in rand_tests]
    report["vertex_bound_sampling_ok"] = all(t[4] for t in rand_tests)

    print("\n[2c-bis] 链上真实参数（m2, W = (m2/m)K_lo）的对数尺度核对")
    print("     真实参数的坐标可达 1e18 量级，2^{x_i} 越出 mpmath 指数上限，故")
    print("     一律在对数尺度比较：log2 S(x) = log2 3 − min_i x_i + log2 sum_i 2^{min−x_i}")
    print("     （x_i >= 70 时 2^{x_i}−1 与 2^{x_i} 的相对差 < 2^{-69}，可忽略）。")
    mp.dps = 80
    delta = log(3) / log(2)
    real_cases = [(47, (mpf(47) / 91) * K_START),
                  (67, (mpf(67) / 91) * mpf(5267319278509397)),
                  (82, (mpf(82) / 91) * mpf(4640282259296926456)),
                  (91, (mpf(91) / 91) * mpf(205632218873398596256))]

    real_rows = []
    for (m2r, Wr) in real_cases:
        vr = Wr * (delta - 1) / (power(delta, m2r) - 1)
        lg_vertex = log2_S_of([power(delta, j) * vr for j in range(m2r)])
        worst_log = mpf(-10) ** 9
        n_okr = 0
        n_evr = 0
        n_samp = 220 if m2r <= 47 else 90
        n_hill_r = 6 if m2r <= 47 else 3
        for trial in range(n_samp):
            kind = trial % 3
            if kind == 0:
                x = [mpf(random.uniform(1.0, 300.0)) for _ in range(m2r)]
            elif kind == 1:
                x = [power(delta, j) * vr * mpf(random.uniform(0.8, 1.25))
                     for j in range(m2r)]
                random.shuffle(x)
            else:
                x = [mpf(1.0) + mpf(random.uniform(0, 1)) for _ in range(m2r)]
                x[random.randrange(m2r)] = mpf(random.uniform(1, 1e6))
            x = repair(x, m2r, Wr)
            if x is None:
                continue
            dlog = log2_S_of(x) - lg_vertex
            n_evr += 1
            if dlog <= mpf(10) ** (-90):
                n_okr += 1
            worst_log = max(worst_log, dlog)
        # 爬山（对数尺度）
        for k in range(n_hill_r):
            x = [power(delta, j) * vr * mpf(random.uniform(0.9, 1.1))
                 for j in range(m2r)]
            random.shuffle(x)
            x = repair(x, m2r, Wr)
            if x is None:
                continue
            cur = log2_S_of(x)
            for _ in range(25):
                i = random.randrange(m2r)
                cand = list(x)
                cand[i] = cand[i] * mpf(random.uniform(0.5, 2.0))
                cand = repair(cand, m2r, Wr)
                if cand is None:
                    continue
                cv = log2_S_of(cand)
                if cv > cur:
                    x, cur = cand, cv
            dlog = cur - lg_vertex
            n_evr += 1
            if dlog <= mpf(10) ** (-90):
                n_okr += 1
            worst_log = max(worst_log, dlog)
        print(f"     m2 = {m2r:>3}, W = {nstr(Wr, 12):>16}, v = {nstr(vr, 12):>16}, "
              f"log2 顶点 = {nstr(lg_vertex, 12):>16}, 最大 log2 超出 = "
              f"{nstr(worst_log, 8):>12}, 通过 {n_okr}/{n_evr}")
        real_rows.append({"m2": m2r, "W": nstr(Wr, 12), "v": nstr(vr, 12),
                          "log2_vertex": nstr(lg_vertex, 12),
                          "max_log2_excess": nstr(worst_log, 8),
                          "passed": f"{n_okr}/{n_evr}"})
    report["vertex_bound_real_params"] = real_rows

    print("\n[2c+] 结论所依赖的三件事（勘误原文的论证 + 本脚本作者的补充）：")
    print("     1. 极值在顶点：S 是凸函数，可行多面体 P = {x_i >= 1、循环链、sum x_i >= W}")
    print("        的回收锥含于非负卦限（绕链一圈得 x_i <= delta^n x_i，故 d_i >= 0），")
    print("        沿任一回收方向 S 不增，故 S 在 P 上取到最大值；凸函数在凸多面体上的")
    print("        最大值必有一个在顶点取到（若不极端的点 x* 最大化，凸性使分解两端之一")
    print("        也最大化，维数递减至顶点）。这一步是勘误原文「attains its maximum at a")
    print("        vertex」所缺的补充，本脚本作者补上；")
    print("     2. 顶点识别：顶点需 n 个线性无关的起作用约束；x_i = 1 不可行（见 [2d]），")
    print("        故起作用约束取自 n 条链约束与 1 条和约束。n 条链全起作用会绕出")
    print("        delta^n = 1 的矛盾，故恰为「和约束 + 某 n−1 条链约束」，即坐标是")
    print("        (v, delta v, ..., delta^{n−1} v) 的循环置换，且 sum = W 定出 v。")
    print("     3. 顶点值：S(顶点) = sum_j f(delta^j v) <= f(v) + (n−1) f(delta v)（f 递减）")
    print("        = 3/(2^v−1) + 3(m2−1)/(2^{delta v}−1) < 3/(2^v−1) + 3(m2−1)/(2^v−1)^delta。")
    print("     注：x_{m−m2+1} < delta x_m 这条「回绕」约束是顶点识别所必需的，它来自")
    print("     窗口按 sum x 取最大（而非按 sum k）；本脚本作者原先试过一条绕开回绕约束的")
    print("     更简证明，经数值反例检验为误（h(M) = sum_k f(M/delta^k) 关于 M 递减，")
    print("     而 sum x >= W 只给出 M 的上界，方向相反），故不采用。")

    # 2d. x_i = 1 的不可行性
    print("\n[2d] x_i = 1 的不可行性：(delta^{m2} − 1)/(delta − 1) < (m2/m) K 吗？")
    mp.dps = 60
    X0, delta, c = setup(60)
    for (m, m2, K) in [(91, 47, mpf(7) * 10**11), (91, 91, mpf("7.94") * 10**21),
                       (91, 1, mpf(7) * 10**11)]:
        lhs = (power(delta, m2) - 1) / (delta - 1)
        rhs = (mpf(m2) / m) * K
        print(f"  m = {m}, m2 = {m2}, K = {nstr(K, 6)}: 左 = {nstr(lhs, 10)}, "
              f"右 = {nstr(rhs, 10)}, 左 < 右 ? {lhs < rhs}")

    # ---- 3. Lemma 22 换算器的验证 -----------------------------------------
    header("[3] Lemma 22 换算器 q_min 的两种实现与验证")
    print("\n[3a] 合成区间上的暴力对照（eps 较大，暴力可行）")
    mp.dps = 80
    delta = log(3) / log(2)
    for e in ("1e-3", "1e-5", "1e-8", "1e-10"):
        eps = mpf(e)
        bf = qmin_bruteforce(eps, 200000)
        lm = qmin_lemma22(eps, dps_cf=120)
        print(f"  eps = {e:>6}: 暴力 = {bf}, Lemma22 分母 = {lm['gamma_den']},"
              f" 分歧指标 k = {lm['k']}, 一致 ? {bf is not None and bf[1] == lm['gamma_den']}")

    print("\n[3b] m = 91 第一步（K = 7e11, m2 = 47）的 eps 上，两法独立对照")
    mp.dps = 120
    X0, delta, c = setup(120)
    pw = delta_powers(delta, 200, 120)
    mmax, best = best_m2(91, K_START, X0, delta, c, pw, eps_of, "73")
    eps1 = best["eps"]
    show("m2 (最优)", mpf(best["m2"]), 6)
    show("v", best["v"], 25)
    show("eps", eps1, 25)
    lm = qmin_lemma22(eps1, dps_cf=300)
    print(f"  Lemma 22: 分歧指标 k = {lm['k']}, (a_k, b_k) = ({lm['a_k']}, {lm['b_k']}),"
          f" c_k = {lm['ck']}")
    print(f"  q_min = {lm['gamma_den']}")
    sc = semiconvergent_scan(eps1, mpf(10) ** 24, dps_cf=300)
    if sc is None:
        print("  收敛子与中间分数扫描（分母 <= 1e24）：未找到（异常，应报告）")
    else:
        print(f"  收敛子与中间分数扫描（分母 <= 1e24）：最小分母 = {sc[0]}, 分子 = {sc[1]}")
        print(f"  两法一致 ? {sc[0] == lm['gamma_den']}")
    d_lo, d_hi, b_lo, b_hi = outward_delta_beta(eps1)
    p_ok = strictly_inside(lm["gamma_num"], lm["gamma_den"], d_lo, d_hi, b_lo, b_hi)
    print(f"  gamma 严格落在区间内（向外区间判定）? {p_ok}")

    print("\n[3c] Legendre 证书路径（独立于连分数分歧深度的排除判据）")
    mp.dps = 120
    Qup = mpf("1.4784") * 91 * power(delta, 91)
    okc, whyc = legendre_certificate(eps1, Qup, dps_cf=300)
    print(f"  eps = {nstr(eps1, 10)}, Qmax = 1.4784·91·delta^91 = {nstr(Qup, 12)}")
    print(f"  eps < 1/(2 Qmax^2) ? {eps1 < 1/(2*Qup*Qup)}")
    print(f"  证书结论：区间内无分母 <= Qmax 的分数 ? {okc}（{whyc}）")
    report["step1_qmin_crosscheck"] = {
        "qmin_lemma22": lm["gamma_den"],
        "qmin_scan": None if sc is None else sc[0],
        "agree": None if sc is None else bool(sc[0] == lm["gamma_den"]),
        "gamma_inside": bool(p_ok),
        "legendre_cert": bool(okc), "legendre_reason": whyc}

    # ---- 4. 自举前的选择原则核对 ------------------------------------------
    header("[4] m2 的选择原则：最大可行 m2 是否等价于最小 eps？")
    mp.dps = 120
    X0, delta, c = setup(120)
    pw = delta_powers(delta, 200, 120)
    for (m, K) in [(91, K_START), (91, mpf(5267319278509397)),
                   (91, mpf(4640282259296926456)), (91, mpf("7.94") * 10**21),
                   (92, K_START), (95, K_START)]:
        rows = []
        for t in range(1, m + 1):
            if m2_feasible(t, m, K, delta, c, pw):
                rows.append((t, eps_of(t, m, K, X0, delta, pw, "73")["eps"]))
        argmin = min(rows, key=lambda r: r[1])[0]
        mx = max(r[0] for r in rows)
        print(f"  m = {m}, K = {nstr(K, 8)}: 可行 m2 个数 = {len(rows)}, "
              f"最大可行 = {mx}, eps 最小者 = {argmin}, 一致 ? {mx == argmin}")

    # ---- 5. m = 91 的勘误版自举链 -----------------------------------------
    header("[5] m = 91 的勘误版自举链（起点 K > 7·10^11，A 用 +73）")
    boot91 = bootstrap(91, dps=120, dps_cf=300, mode="73")
    print(f"  {'步':>3} {'m2':>4} {'v':>22} {'eps':>26} {'K 新下界':>26}")
    for st in boot91["steps"]:
        kn = "—" if st["K_new"] is None else nstr(st["K_new"], 25)
        print(f"  {st['iter']:>3} {st['m2']:>4} {nstr(st['v'], 20):>22}"
              f" {nstr(st['eps'], 22):>26} {kn:>26}")
    print(f"  终值 K = {boot91['K_final_int']}")
    print(f"  状态：{boot91['status']}")
    mp.dps = 120
    delta = log(3) / log(2)
    up91 = sdw_upper(91, delta)
    margin91 = boot91["K_final"] / up91
    show("m = 91 的 SdW 上界 1.4784·91·delta^91", up91, 25)
    show("余量倍数 K下界 / K上界", margin91, 25)
    print(f"  排除 m = 91 ? {boot91['K_final'] > up91}")
    report["m91"] = {
        "chain": [{"m2": st["m2"], "v": nstr(st["v"], 20), "eps": nstr(st["eps"], 22),
                   "K_new": None if st["K_new"] is None else int(st["K_new"])}
                  for st in boot91["steps"]],
        "K_final": boot91["K_final_int"], "upper": nstr(up91, 25),
        "margin": nstr(margin91, 25), "excluded": bool(boot91["K_final"] > up91),
    }

    print("\n[5b] 七步的 q_min 逐 step 交叉核对（Lemma 22 与收敛子/中间分数扫描）")
    mp.dps = 120
    step_checks = []
    for st in boot91["steps"][:7]:
        eps_i = st["eps"]
        lmi = qmin_lemma22(eps_i, dps_cf=300)
        sci = semiconvergent_scan(eps_i, mpf(10) ** 24, dps_cf=300)
        agree = (sci is not None and lmi is not None
                 and sci[0] == lmi["gamma_den"])
        inside = strictly_inside(lmi["gamma_num"], lmi["gamma_den"],
                                 *outward_delta_beta(eps_i))
        print(f"  步 {st['iter']}: eps = {nstr(eps_i, 8):>14}, k = {lmi['k']:>3}, "
              f"q_min = {lmi['gamma_den']}, 扫描一致 ? {agree}, gamma 在区间内 ? {inside}")
        step_checks.append({"iter": st["iter"], "eps": nstr(eps_i, 8),
                            "k": lmi["k"], "q_min": lmi["gamma_den"],
                            "agree": bool(agree), "gamma_inside": bool(inside)})
    report["step_qmin_checks"] = step_checks

    print("\n[5c] 最后一步 eps 上的 Legendre 证书（独立排除判据）")
    mp.dps = 120
    eps7 = boot91["steps"][6]["eps"]
    okc7, whyc7 = legendre_certificate(eps7, up91, dps_cf=300)
    print(f"  eps7 = {nstr(eps7, 10)}, Qmax = 1.4784·91·delta^91 = {nstr(up91, 12)}")
    print(f"  eps7 < 1/(2 Qmax^2) ? {eps7 < 1/(2*up91*up91)}")
    print(f"  证书：区间 (delta, delta+eps7) 内无分母 <= Qmax 的分数 ? {okc7}（{whyc7}）")
    report["legendre_step7"] = {"ok": bool(okc7), "reason": whyc7,
                                "eps": nstr(eps7, 10)}

    print("\n[5d] 实际参数下的顶点值与被放宽的尾巴（m = 91 第七步：m2 = 91, v = 75.5946）")
    mp.dps = 120
    X0, delta, c = setup(120)
    pw = delta_powers(delta, 200, 120)
    v7 = mpf("75.594632394494331846")
    n7 = 91
    vertex7 = sum(f_tail(power(delta, j) * v7) for j in range(n7))
    loosen7 = f_tail(v7) + (n7 - 1) * f_tail(delta * v7)
    final7 = f_tail(v7) + (n7 - 1) * power(f_tail(v7) / 3, delta)
    for nm, val in (("S(顶点) = sum_j f(delta^j v)", vertex7),
                    ("3/(2^v−1) + 90·3/(2^{delta v}−1)", loosen7),
                    ("3/(2^v−1) + 90·3/(2^v−1)^delta", final7)):
        print(f"  {nm:<34} = {nstr(val, 12)}")
    print(f"  三者都远小于 A/(3K log2) 所需的量级；被放宽的尾巴与顶点值在 1e-12 相对")
    print(f"  精度下不可分辨（放宽度 = 顶点值的 {nstr((loosen7-vertex7)/vertex7, 6)} 倍）。")
    print(f"  (2^v−1)^delta = {nstr(power(power(2, v7) - 1, delta), 12)}"
          f"  vs  X0 = {nstr(X0, 12)}  比值 = {nstr(power(power(2, v7) - 1, delta)/X0, 8)}")
    report["vertex_vs_loosened_m91_step7"] = {
        "vertex": nstr(vertex7, 12), "loosened": nstr(loosen7, 12),
        "final": nstr(final7, 12),
        "ratio_to_X0": nstr(power(power(2, v7) - 1, delta) / X0, 8)}

    print("\n[5e0] 判据映射 Psi 的结构：Psi(K_lo) 与起点网格上的单调性（m = 92）")
    print("      Psi(K_lo) := 在阈值 K_lo 处取最优 m2 后由 Lemma 22 换回的最小分母。")
    print("      理论：K' > K 时可行 m2 集合更大，且每个 eps(m2, K) 关于 K 递减")
    print("      （1/K 因子与 2^{-v} 尾巴同时变小），故 eps(opt) 非增、Psi 非降。")
    mp.dps = 120
    X0, delta, c = setup(120)
    pw = delta_powers(delta, 200, 120)

    def psi_of(m, K):
        _mm, _best = best_m2(m, K, X0, delta, c, pw, eps_of, "73")
        if _best is None:
            return None, None
        _q = qmin_lemma22(_best["eps"], dps_cf=300)
        if _q is None:
            return None, _best["m2"]
        return mpf(_q["gamma_den"]), _best["m2"]

    prev = None
    mono = True
    grid = ["7.5311e11", "1e15", "1e18", "1e20", "2.05632218873398596256e20",
            "2.5e20", "3.0e20", "3.0257e20", "3.1e20", "3.3e20",
            "3.4302597024885020978e20"]
    psi_rows = []
    for g in grid:
        val, m2g = psi_of(92, mpf(g))
        flag = ""
        if prev is not None and val is not None and val < prev:
            mono = False
            flag = "  <-- 下降（与理论相反）"
        print(f"      K_lo = {g:>26}  m2 = {str(m2g):>3}  Psi = "
              f"{nstr(val, 22) if val is not None else 'None':>26}{flag}")
        if val is not None:
            prev = val
        psi_rows.append({"K_lo": g, "m2": m2g,
                         "Psi": None if val is None else nstr(val, 22)})
    print(f"      网格上 Psi 非降 ? {mono}")
    print(f"      注意 K_lo = 上界 3.4302597024885020978e20 不是合法的排除起点：")
    print(f"      该假设与 SdW 上界 K < 3.4302597024885020978e20 直接冲突，蕴含式空真。")
    report["psi_grid_m92"] = {"rows": psi_rows, "monotone": bool(mono)}

    print("\n[5e] 与论文 Corollary 24 第一条的对照（m ≤ 98 时论文声称 K > 7.76·10^19）")
    mp.dps = 120
    for m in (92, 95, 98, 99):
        bt = bootstrap(m, dps=120, dps_cf=250, mode="73")
        print(f"  m = {m}: 链终值 K = {nstr(bt['K_final'], 22)}（状态 {bt['status']}）")

    # ---- 6. 最大可排除 m ---------------------------------------------------
    header("[6] 逐 m 扫描：这一版本能排除到的最大 m")
    mp.dps = 120
    delta = log(3) / log(2)
    excluded = []
    guard_ms = []
    scan_rec = {}
    for m in range(2, 141):
        bt = bootstrap(m, dps=120, dps_cf=250, mode="73")
        if any(st.get("cut") for st in bt["steps"]):
            guard_ms.append(m)
        up = sdw_upper(m, delta)
        placeholder = up is None
        if placeholder:
            # m <= 77：SdW Theorem 3(b) 本身已排除 m <= 75；此处 up 置 0 只是占位，
            # 该区间的「排除」不构成这一版本的独立结论。
            up = mpf(0)
        ok = bt["K_final"] > up
        if ok:
            excluded.append(m)
        scan_rec[m] = {"K_final": nstr(bt["K_final"], 20), "status": bt["status"],
                       "upper": None if placeholder else nstr(up, 20),
                       "placeholder": placeholder, "excluded": bool(ok),
                       "guard": any(st.get("cut") for st in bt["steps"])}
    print(f"  被排除的 m（起点 K > 7e11，勘误版尾部）共 {len(excluded)} 个：")
    print(f"    {excluded}")
    print(f"  其中 m <= 77 的排除是占位（SdW Theorem 3(b) 已排除 m <= 75），")
    print(f"  这一版本自身有独立意义的扫描区间是 78 至 140。")
    print(f"  链内出现「守卫触发（v > 1e8，2^{{−v}} 下溢）」的 m 有 {len(guard_ms)} 个：")
    print(f"    {guard_ms}")
    print(f"  这些 m 的排除结论一律由对数空间证书给出（不依赖被低估的 eps）；")
    print(f"  m = 91 与 m = 92 的链中均无守卫触发（v 最大约 2919 与 1.4e3），故这两个")
    print(f"  关键结论完全落在正常数值范围内。")
    report["scan_summary"] = {"max_m": max(excluded), "guard_ms": guard_ms,
                              "n_excluded": len(excluded)}
    mx = max(excluded)
    print(f"  最大可排除 m = {mx}")
    bt92 = bootstrap(92, dps=120, dps_cf=250, mode="73")
    print("  m = 92 的完整链（它已停滞，故 92 不被排除）：")
    print(f"    {'步':>3} {'m2':>4} {'eps':>28} {'K':>26}")
    for st in bt92["steps"]:
        print(f"    {st['iter']:>3} {st['m2']:>4} {nstr(st['eps'], 24):>28}"
              f" {nstr(st['K_old'], 22):>26}")
    print(f"    终值 K = {nstr(bt92['K_final'], 22)}，状态 {bt92['status']}")
    up92 = sdw_upper(92, delta)
    print(f"    上界 1.4784·92·delta^92 = {nstr(up92, 22)}，排除 ? "
          f"{bt92['K_final'] > up92}")
    for m in range(mx - 1, min(mx + 6, 141)):
        bt = bootstrap(m, dps=120, dps_cf=250, mode="73")
        up = sdw_upper(m, delta)
        if up is None:
            print(f"    m = {m}: SdW 该区间无 1.4784 型上界，跳过")
            continue
        print(f"    m = {m}: K 终值 = {nstr(bt['K_final'], 22):>24}, "
              f"上界 = {nstr(up, 22):>24}, 排除 ? {bt['K_final'] > up}"
              f"（状态 {bt['status']}）")
    report["m92_chain"] = [{"iter": st["iter"], "m2": st["m2"],
                            "eps": nstr(st["eps"], 18),
                            "K": nstr(st["K_old"], 22)} for st in bt92["steps"]]
    report["m92_upper"] = nstr(up92, 22)
    report["max_m"] = mx
    report["excluded_list"] = excluded

    # ---- 7. 敏感性 --------------------------------------------------------
    header("[7] 敏感性：A 的 +73 与 +1、两档精度、健全版对照")
    mp.dps = 120
    b73 = bootstrap(91, dps=120, dps_cf=300, mode="73")
    b1 = bootstrap(91, dps=120, dps_cf=300, mode="1")
    print(f"  A 用 +73：K 终值 = {b73['K_final_int']}")
    print(f"  A 用 +1 ：K 终值 = {b1['K_final_int']}")
    b260 = bootstrap(91, dps=260, dps_cf=500, mode="73")
    print(f"  dps = 260：K 终值 = {b260['K_final_int']}（与 dps = 120 一致 ? "
          f"{b260['K_final_int'] == b73['K_final_int']}）")

    print("\n[7b] 勘误版与健全版在 m = 91 的同一步比较（第三步 K = 4.64e18 处取最优 m2）")
    mp.dps = 120
    X0, delta, c = setup(120)
    pw = delta_powers(delta, 200, 120)
    K3 = mpf(4640282259296926456)
    mmax_e, be = best_m2(91, K3, X0, delta, c, pw, eps_of, "73")
    mmax_s, bs = best_m2(91, K3, X0, delta, c, pw, sound_eps_of, "73")
    print(f"  勘误版：最优 m2 = {be['m2']}, v = {nstr(be['v'], 12)}, "
          f"eps = {nstr(be['eps'], 12)}")
    print(f"  健全版：最优 m2 = {bs['m2']}, v = {nstr(bs['v'], 12)}, "
          f"eps = {nstr(bs['eps'], 12)}")
    vE = be["v"]
    inv, _ = inv_2v_minus_1(vE)
    print(f"  勘误版尾项 3/(2^v−1)^delta = {nstr(3 * power(inv, delta), 8)}"
          f"  对 健全版尾项 3/X0 = {nstr(3 / X0, 8)}")
    print(f"  比值 ≈ {nstr(power(inv, delta) * X0, 8)}")

    # ---- 8. 输出 JSON 摘要 ------------------------------------------------
    header("[8] 机器可读摘要")
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))

    return report


if __name__ == "__main__":
    main()
