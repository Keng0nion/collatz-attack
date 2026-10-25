#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 独立重算核心模块：Hercher 定理 21（勘误版口径）的自举映射 Psi。

独立声明：本文件不 import、不执行、不读 60-audits/hercher-t21/scripts/ 下的任何
项目脚本（包括 rederive-erratum.py 与 margin_table.py），也不读它们的输出。
一切定义直接取自两件一手原件：

  (P) Hercher 2023, JIS 26, Art. 23.3.5，本机 /tmp/h5.pdf（md5 3e2377be…），
      抽取文本 /tmp/h5.txt（md5 见报告）：
      - Definition 4  : X0 = 695 * 2^60                    (/tmp/h5.txt:80 至 :83)
      - Remark 7      : T(n_i) < 3/n_i < 3/X0              (/tmp/h5.txt:191 附近)
      - Theorem 14    : sum_{i<=m1} T(n_i) < (97 m1 + 73)/(54 X0)  (/tmp/h5.txt:465)
      - Theorem 21    : 前提、v、eps 三项                   (/tmp/h5.txt:695 至 :708)
      - Lemma 22      : 区间内最小分母的连分数公式          (/tmp/h5.txt:822 至 :831)
      - Theorem 23    : 七步自举                            (/tmp/h5.txt:850 至 :869)

  (C) 2026 年勘误，本机 /tmp/corr.pdf（md5 f23d5f96…），/tmp/corr.txt：
      - 被修正的是 T(n_{m-m2+1+l}) < 3/(2^v -1)^delta 的推导（:11 至 :22）；
      - 末句目标式 3/(2^v-1) + 3(m2-1)/((2^v-1)^delta) 与论文定理 21 陈述一致。

记号与公式（逐条对应上面出处，先定义后计算）：
  delta := log 3 / log 2                                  (P Definition 15)
  X0    := 695 * 2^60                                      (P Definition 4)
  前提    : (delta^m2 - 1)/(delta - 1) * log2((162/97) X0) <= (m2/m) K   (P Thm 21)
  v       := (m2/m) K (delta - 1)/(delta^m2 - 1)                          (P Thm 21)
  eps     := ( A(m2) + 3/(2^v - 1) + 3 (m2-1)/(2^v - 1)^delta ) / (3 K log 2)
  其中    A(m2) = 0 (m2 = m) / 3/X0 (m2 = m-1) / (97(m-m2)+73)/(54 X0) (其余)
  Psi(K)  := 在区间 (delta, delta + eps_opt) 内分母最小的分数之分母（P Lemma 22），
             eps_opt := min{ eps(m2) : m2 可行 }。
链：K_0 = 起点，K_{n+1} = Psi(K_n)；只要 Psi(K_n) > K_n 就可继续。
"""

from mpmath import mp, mpf, power, log, floor

DELTA = None

DEFS = {
    "delta": "log(3)/log(2)  (论文 Definition 15)",
    "X0": "695 * 2^60 = 801280445701758648320 (论文 Definition 4)",
    "premise": "(delta^m2-1)/(delta-1)*log2((162/97)X0) <= (m2/m)K  (定理 21 前提)",
    "v": "(m2/m)K(delta-1)/(delta^m2-1)  (定理 21)",
    "eps": "(A(m2)+3/(2^v-1)+3(m2-1)/(2^v-1)^delta)/(3K log2)  (定理 21 + 勘误)",
    "Psi": "Psi(K) = 区间 (delta, delta+eps_opt) 内最小分母（Lemma 22）",
}


def set_dps(dps):
    """设定精度并重算 delta。返回 delta。"""
    mp.dps = dps
    global DELTA
    DELTA = mp.log(3) / mp.log(2)
    return DELTA


def X0():
    return mpf(695) * power(2, 60)


def X0_exact():
    return 695 * 2 ** 60


def log2(x):
    return mp.log(x) / mp.log(2)


def geom(m2):
    """(delta^m2 - 1)/(delta - 1)"""
    return (power(DELTA, m2) - 1) / (DELTA - 1)


def premise_lhs(m2):
    """(delta^m2 - 1)/(delta - 1) * log2((162/97) X0)"""
    return geom(m2) * log2(mpf(162) / 97 * X0())


def premise_rhs(m2, m, K):
    """(m2/m) K"""
    return (mpf(m2) / m) * K


def feasible(m2, m, K):
    return premise_lhs(m2) <= premise_rhs(m2, m, K)


def v_of(m2, m, K):
    return premise_rhs(m2, m, K) / geom(m2)


def A_of(m2, m):
    if m2 == m:
        return mpf(0)
    if m2 == m - 1:
        return mpf(3) / X0()
    return mpf(97 * (m - m2) + 73) / (54 * X0())


def eps_of(m2, m, K):
    v = v_of(m2, m, K)
    t = power(2, v) - 1
    t1 = 3 / t
    t2 = 3 * mpf(m2 - 1) / power(t, DELTA)
    return (A_of(m2, m) + t1 + t2) / (3 * K * mp.log(2))


def cf_digits(x, nmax):
    """x 的连分数部分商（数值抽取，nmax 项或遇精确 0 结束）。"""
    out = []
    y = x
    for _ in range(nmax):
        fl = floor(y)
        out.append(int(fl))
        r = y - fl
        if r == 0:
            break
        y = 1 / r
    return out


def qmin_interval(alpha, beta, nmax=400, full=False):
    """
    Lemma 22：区间 (alpha, beta) 内分母最小的分数之分母。
    返回 (q, k, dig_alpha, dig_beta)，k 为两个连分数首个相异项的下标，
    dig_* 为各自的前 k+2 项（便于复核）。
    """
    A = cf_digits(alpha, nmax)
    B = cf_digits(beta, nmax)
    k = 0
    while k < min(len(A), len(B)) and A[k] == B[k]:
        k += 1
    if k >= min(len(A), len(B)):
        raise RuntimeError("两个连分数在前 %d 项内未分离，需提高精度" % nmax)
    # gamma = [A[0]; ...; A[k-1], ck]，其收敛分母 q_k
    pm2, pm1 = 0, 1
    qm2, qm1 = 1, 0
    for i in range(k):
        p = A[i] * pm1 + pm2
        q = A[i] * qm1 + qm2
        pm2, pm1 = pm1, p
        qm2, qm1 = qm1, q
    ck = min(A[k], B[k]) + 1
    qk = ck * qm1 + qm2
    if full:
        return qk, k, A[: k + 2], B[: k + 2], qm1, ck
    return qk, k, A[: k + 2], B[: k + 2]


def best_m2(m, K, convention="min_eps"):
    """
    在 1..m 中挑 m2。
      convention = "min_eps"      : 取 eps 最小的可行 m2（Psi 最大）
      convention = "max_feasible" : 取最大的可行 m2（论文链条的读法）
    返回 (m2, eps, m2_max_feasible, eps_at_max_feasible, n_feasible)
    """
    best = None
    rows = []
    for m2 in range(1, m + 1):
        if feasible(m2, m, K):
            e = eps_of(m2, m, K)
            rows.append((m2, e))
            if best is None or e < best[1]:
                best = (m2, e)
    if best is None:
        return None
    m2_max, e_max = rows[-1]
    if convention == "min_eps":
        return (best[0], best[1], m2_max, e_max, len(rows))
    return (m2_max, e_max, m2_max, e_max, len(rows))


def psi(m, K, convention="min_eps", eps_scale=None, auto=True):
    """
    Psi(K)。返回 dict。
    eps_scale: 若给定，则把 eps 乘以该因子后再做连分数步（用于台阶稳健性检验）。
    auto: 依 eps 的数量级自动抬精度（dps 与连分数项数），并在高精度下重算 eps。
    """
    set_dps(120)                      # 第一遍：低精度估 eps 的数量级
    b = best_m2(m, K, convention)
    if b is None:
        return {"K": K, "psi": None, "reason": "无可行 m2"}
    e0 = b[1] * (mpf(eps_scale) if eps_scale is not None else 1)
    if auto:
        # 注意：mpmath 的 log(x, b) 是「以 b 为底」；上一版误写成 log(10, e0)，
        # 导致 E 恒为约 1、nmax 恒为 81，这里改为以 10 为底正确取指数。
        E = max(0, -int(floor(log(e0, 10))))
        dps = max(120, int(0.65 * E) + 60)
        nmax = int(1.6 * E) + 120
    else:
        dps, nmax = 120, 400
    # 分离失败时自动加倍重试（最多 6 次），避免静默失准
    for _attempt in range(6):
        set_dps(dps)
        b = best_m2(m, K, convention)     # 高精度重算
        m2, e, m2_max, e_max, nf = b
        if eps_scale is not None:
            e = e * mpf(eps_scale)
        try:
            q, k, A, B = qmin_interval(DELTA, DELTA + e, nmax=nmax)
            break
        except RuntimeError:
            dps = int(dps * 1.6) + 20
            nmax = int(nmax * 1.6) + 20
    else:
        raise RuntimeError("连分数步在 6 次加倍后仍未分离：K=%s m=%s" % (K, m))
    return {
        "K": K, "psi": q, "m2": m2, "eps": e, "m2_max_feasible": m2_max,
        "eps_at_max": e_max, "n_feasible": nf, "cf_index": k,
        "digits": k + 2, "dps": dps, "nmax": nmax,
        "log10_q": mp.log10(mpf(q)),
    }


def chain(m, K0, convention="min_eps", max_steps=40, cap=None):
    """自举链。返回 (记录列表, 终值, 是否越过 cap)。"""
    seq = []
    K = K0
    for _ in range(max_steps):
        r = psi(m, K, convention=convention)
        r["K_in"] = K
        seq.append(r)
        if r["psi"] is None or r["psi"] <= K:
            return seq, K, False
        K = r["psi"]
        if cap is not None and K > cap:
            return seq, K, True
    return seq, K, False


def sdw_upper(m):
    """Simons 与 de Weger 定理 3(d)（论文引用形式）：K < 1.4784 m delta^m（m >= 91）。"""
    return mpf("1.4784") * m * power(DELTA, m)


def num(x, n=25):
    return mp.nstr(x, n)
