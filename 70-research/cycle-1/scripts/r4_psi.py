#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 独立重算：Hercher 定理 21（勘误版口径）的自举映射 Psi。

独立声明
========
本文件不 import、不执行、不读 60-audits/hercher-t21/scripts/ 下的任何项目脚本，
也不读它们的输出文件；只按 r4_run.py 的打印做锚点对照。一切定义直接取自两件
一手原件：

  (P) Hercher 2023, JIS 26, Article 23.3.5，本机 /tmp/h5.pdf（md5
      3e2377bef0b1c0435dc455c9bbee43a1），抽取文本 /tmp/h5.txt。
      - Definition 4  : X0 = 695 * 2^60             (/tmp/h5.txt:80 起)
      - Definition 15 : delta := log 3 / log 2       (/tmp/h5.txt:505 起)
      - Remark 7      : T(n_i) < 3/n_i < 3/X0        (/tmp/h5.txt:190)
      - Theorem 21    : 可行条件、v、eps 的三项       (/tmp/h5.txt:695 起)
      - Lemma 22      : 区间内最小分母的连分数公式    (/tmp/h5.txt:822 起)
      - Theorem 23    : 七步自举                      (/tmp/h5.txt:850 起)

  (C) 2026 勘误，本机 /tmp/corr.pdf（md5 f23d5f969116cb1af6e9b981b4b3ba7a），
      抽取文本 /tmp/corr.txt：替换尾部
        S(v, delta v, ..., delta v) = 3/(2^v - 1) + 3(m2-1)/(2^{delta v} - 1)
        < 3/(2^v - 1) + 3(m2-1)/((2^v - 1)^delta)     (/tmp/corr.txt:78 至 :83)

符号约定（按论文原意）
======================
  m      环长（奇步数 K 与偶步数 L 之和，m = K + L）
  K      环上奇数的个数（也是奇步总数）
  m2     窗口长度，1 <= m2 <= m
  X0     695 * 2^60
  delta  log 3 / log 2
  c      log((162/97) * X0) / log 2
  v      (m2/m) * K * (delta - 1) / (delta^{m2} - 1)
  A(m2)  (97(m - m2) + 73) / (54 X0)     （m2 <= m - 2）
         3 / X0                          （m2 = m - 1，Theorem 21 第二段）
         0                               （m2 = m，Theorem 21 第三段）
  eps    (1/(3 K log 2)) * ( A + 3/(2^v - 1) + 3(m2 - 1)/((2^v - 1)^delta) )
         于是 delta < m/K < delta + eps，而 m/K 的分母不超过 K。

  Psi(K_lo) := 在「K >= K_lo」这一前提下可推出的最强 K 下界，等于
               max over 可行 m2 of q_min(delta, delta + eps(m2, K_lo))
             = q_min(delta, delta + min over 可行 m2 of eps(m2, K_lo))
             （第二式用了 q_min 关于 eps 非增）

  q_min 由 Lemma 22 给出：若 delta 与 delta + eps 的连分数展开首次分歧在指标 k
  （前 k 项相同），则 gamma = [a_0; ..., a_{k-1}, min(a_k,b_k)+1]，q_min 即
  gamma 的分母。

数值方向纪律
============
  Theorem 21 的 eps 含 3/(2^v - 1) 与 3(m2-1)/(2^v-1)^delta 两项。v 很大时这两
  项极小。本文件对每一项都同时给「精确值」（v <= TAIL_EXACT_LOG2 时）与一个
  严格上界 1/(2^v-1) <= 2^{1-v}；最终用于反解 K 的量一律取上界（eps_ub），
  保证方向安全（eps 偏大 => q_min 偏小 => K 下界偏弱但合法）。
"""

import sys
import time
from fractions import Fraction

from mpmath import mp, mpf, power, log, floor

X0_INT = 695 * 2 ** 60                      # Hercher Definition 4
DPS_EPS = 120                               # eps 与 v 的工作精度
DPS_CF = 250                                # 连分数工作精度
TAIL_EXACT_LOG2 = 400                       # v 超过此值改用解析上界 1e-120


# ---------------------------------------------------------------------------
# 1. 常量
# ---------------------------------------------------------------------------

def consts(dps=DPS_EPS):
    """返回 (X0, delta, c)。c = log((162/97)X0)/log 2，见 Theorem 21 前提。"""
    mp.dps = dps
    X0 = mpf(X0_INT)
    delta = log(mpf(3)) / log(mpf(2))
    c = log(mpf(162) / mpf(97) * X0) / log(mpf(2))
    return X0, delta, c


def dpow(delta, n):
    """[1, delta, delta^2, ..., delta^n]。"""
    out = [mpf(1)] * (n + 1)
    acc = mpf(1)
    for j in range(1, n + 1):
        acc = acc * delta
        out[j] = acc
    return out


# ---------------------------------------------------------------------------
# 2. Theorem 21 的各分量
# ---------------------------------------------------------------------------

def m2_feasible(t, m, K, delta, c, pw):
    """Theorem 21 前提：(delta^t - 1)/(delta - 1) * c <= (t/m) * K。

    c 即前提里的 log((162/97)X0)/log(2)；论文原句在 /tmp/h5.txt:695 起。
    """
    return (pw[t] - 1) / (delta - 1) * c <= (mpf(t) / m) * K


def feasible_list(m, K, delta, c, pw):
    return [t for t in range(1, m + 1) if m2_feasible(t, m, K, delta, c, pw)]


def v_of(m2, m, K, delta, pw):
    """v = (m2/m) K (delta - 1)/(delta^{m2} - 1)。"""
    return (mpf(m2) / m) * K * (delta - 1) / (pw[m2] - 1)


def A_of(m2, m, X0):
    """Theorem 21 三段分别给的第一项。"""
    if m2 == m:
        return mpf(0)
    if m2 == m - 1:
        return 3 / X0
    return (97 * (m - m2) + 73) / (54 * X0)


def eps_of(m2, m, K, X0, delta, pw, dps=DPS_EPS):
    """Theorem 21 的 eps（勘误版尾部）。

    返回 eps（v 精确时的值或略小的值）与 eps_ub（严格上界）。
    """
    mp.dps = dps
    v = v_of(m2, m, K, delta, pw)
    if v <= TAIL_EXACT_LOG2:
        inv = 1 / (power(mpf(2), v) - 1)
        inv_ub = inv
        exact = True
    else:
        inv = mpf(0)
        # 1/(2^v - 1) <= 2^{1-v}；v > 400 时 2^{1-v} < 2^-399 < 1e-120，
        # 这里取 1e-120 作安全上界（仍严格成立）。
        inv_ub = mpf("1e-120")
        exact = False
    A = A_of(m2, m, X0)
    eps = (A + 3 * inv + 3 * mpf(m2 - 1) * power(inv, delta)) / (3 * K * log(mpf(2)))
    eps_ub = (A + 3 * inv_ub + 3 * mpf(m2 - 1) * power(inv_ub, delta)) \
        / (3 * K * log(mpf(2)))
    return {"m2": m2, "v": v, "A": A, "eps": eps, "eps_ub": eps_ub,
            "tail_exact": exact}


def best_m2(m, K, X0, delta, c, pw, dps=DPS_EPS):
    """扫全部可行 m2，返回 (可行集, 按 eps 最小者, 按 eps_ub 最小者)。

    判决一律用 eps_ub：对任一可行 m2 都给出合法下界，取其最大者即取 eps_ub
    最小者对应的 q_min。
    """
    mp.dps = dps
    feas = feasible_list(m, K, delta, c, pw)
    if not feas:
        return None, None, None
    best = None
    best_ub = None
    for t in feas:
        rec = eps_of(t, m, K, X0, delta, pw, dps)
        if best is None or rec["eps"] < best["eps"]:
            best = rec
        if best_ub is None or rec["eps_ub"] < best_ub["eps_ub"]:
            best_ub = rec
    return feas, best, best_ub


# ---------------------------------------------------------------------------
# 3. q_min：Lemma 22 的三种实现
# ---------------------------------------------------------------------------

def _cf_greedy(x, max_terms):
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


def _frac_of_cf(terms):
    fr = Fraction(int(terms[-1]))
    for a in reversed(terms[:-1]):
        fr = Fraction(int(a)) + 1 / fr
    return fr


def qmin_divergence(eps, dps_cf=DPS_CF, max_terms=4000):
    """实现一：Lemma 22 的首次分歧法。返回 dict 或 None。"""
    save = mp.dps
    mp.dps = dps_cf
    d = log(mpf(3)) / log(mpf(2))
    b = d + mpf(eps)
    ya, yb = d, b
    ta, tb = [], []
    k = None
    for i in range(max_terms):
        aa = int(floor(ya))
        ab = int(floor(yb))
        ta.append(aa)
        tb.append(ab)
        if aa != ab:
            k = i
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
    fr = _frac_of_cf(ta[:k] + [ck])
    out = {"k": k, "ak": ta[k], "bk": tb[k], "ck": ck,
           "p": fr.numerator, "q": fr.denominator, "prefix": ta[:k]}
    mp.dps = save
    return out


def semiconvergents(delta_terms, qmax):
    """枚举 delta 的分母 <= qmax 的全部半收敛子（含收敛子），按分母升序。

    半收敛子 = [a_0; a_1, ..., a_{i-1}, j]，1 <= j <= a_i。
    """
    p2, q2 = 0, 1        # p_{-2}, q_{-2}
    p1, q1 = 1, 0        # p_{-1}, q_{-1}
    out = []
    for i, a in enumerate(delta_terms):
        a = int(a)
        for j in range(1, a + 1):
            p = j * p1 + p2
            q = j * q1 + q2
            if q <= qmax:
                out.append((q, p))
        p0 = a * p1 + p2
        q0 = a * q1 + q2
        p2, q2 = p1, q1
        p1, q1 = p0, q0
        if q1 > qmax * (a + 2):
            break
    out = sorted(set(out))
    return out


def qmin_semiconvergent(eps, delta_terms, qmax, dps=DPS_EPS):
    """实现二：上方半收敛子的记录扫描。"""
    mp.dps = dps
    d = log(mpf(3)) / log(mpf(2))
    hit = []
    for (q, p) in semiconvergents(delta_terms, qmax):
        gap = mpf(p) / q - d
        if gap <= 0:
            continue
        if gap < eps:
            hit.append((q, p, gap))
    if not hit:
        return None
    return min(hit, key=lambda t: t[0])


def qmin_bruteforce(eps, qmax, dps=DPS_EPS):
    """实现三（验证用）：对 q = 1..qmax 直接判断区间内是否有整数分子。

    存在 p 使 q*delta < p < q*(delta+eps) 等价于
        floor(q*delta) + 1 < q*(delta+eps)。
    """
    mp.dps = dps
    d = log(mpf(3)) / log(mpf(2))
    for q in range(1, qmax + 1):
        qd = mpf(q) * d
        lo = int(floor(qd)) + 1
        if mpf(lo) < qd + q * eps:
            return q, lo
    return None


# ---------------------------------------------------------------------------
# 4. Psi 与自举链
# ---------------------------------------------------------------------------

def psi(m, K_lo, ctx, dps=DPS_EPS):
    """Psi_m(K_lo)：在「K >= K_lo」下由 Theorem 21 加 Lemma 22 推出的 K 下界。

    返回 (Q, 记录字典)；Q 为 None 表示无可行 m2 或连分数不收敛。
    """
    mp.dps = dps
    X0, delta, c, pw = ctx
    feas, best, best_ub = best_m2(m, K_lo, X0, delta, c, pw, dps)
    if best is None:
        return None, {"reason": "no_feasible_m2"}
    rec = qmin_divergence(best_ub["eps_ub"], dps_cf=DPS_CF)
    if rec is None:
        return None, {"reason": "cf_no_divergence", "eps_ub": best_ub["eps_ub"],
                      "m2": best_ub["m2"]}
    return rec["q"], {"m2": best_ub["m2"], "v": best_ub["v"],
                      "A": best_ub["A"], "eps": best_ub["eps"],
                      "eps_ub": best_ub["eps_ub"], "tail_exact": best_ub["tail_exact"],
                      "cf": rec, "n_feasible": len(feas), "max_feasible": max(feas)}


def bootstrap(m, K0, ctx, dps=DPS_EPS, max_iter=40):
    """自举链：K_{n+1} = Psi_m(K_n)，停在不动点（K_{n+1} <= K_n）或迭代上限。"""
    mp.dps = dps
    K = mpf(K0)
    seq = [K]
    detail = []
    status = "max_iter"
    for it in range(max_iter):
        Q, info = psi(m, K, ctx, dps)
        detail.append({"iter": it + 1, "K_in": K, "K_out": Q, "info": info})
        if Q is None:
            status = "stuck:" + str(info.get("reason"))
            break
        seq.append(Q)
        if Q <= K:
            status = "fixed_point"
            K = Q
            break
        K = Q
    return {"m": m, "K0": mpf(K0), "K_final": K, "status": status, "seq": seq,
            "detail": detail}


# ---------------------------------------------------------------------------
# 5. 上界与余量
# ---------------------------------------------------------------------------

def sdw_upper(m, delta):
    """Simons 与 de Weger v1.44 Theorem 3(d) 的分段上界。

    出处：/tmp/sidw144.txt:262 至 :275（本机抽取文本）
        78 <= m <= 90      : 1.3993 * m * delta^m
        91 <= m <= 515619  : 1.4784 * m * delta^m
    """
    if 78 <= m <= 90:
        return mpf("1.3993") * m * power(delta, m)
    if 91 <= m:
        return mpf("1.4784") * m * power(delta, m)
    return None


def margin(m, K_low, delta, dps=DPS_EPS):
    mp.dps = dps
    U = sdw_upper(m, delta)
    if U is None:
        return None, None
    return U, K_low / U
