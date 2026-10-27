#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4「敌意否证探针」搜索核心（与路线 1「连分数严格证书」互不复用代码）。

本文件不 import 也不读任何项目脚本（r4x_core.py / r4x_run*.py / r4x_rig*.py /
route3_recheck.py），全部定义按一手出处的转引重建；转引文本逐字读自
`70-research/cycle-2/materials.md`（416 行，md5 257de8b9aa99e67134bc85f4f4d512be）：

  [P] Hercher 2023, JIS 26 Art. 23.3.5 Theorem 21 与 Lemma 22，见 materials.md:28 至 :38
      （eps 三项、前提、v 的定义）、:46 至 :53（Lemma 22 陈述与证明两种 parity）。
  [C] 2026 勘误末句 3/(2^v-1) + 3(m2-1)/((2^v-1)^delta)，见 materials.md:76 至 :81。
      X0 = 695 * 2^60（印出版口径，materials.md:99 与 :102）。

定义基准（先写死，再用已知值锚点自检；learnings.md:28）：
  delta := log_2 3 ；m := 92 ；m2 取 1..92
  geom(m2) := (delta^m2 - 1)/(delta - 1)
  G(m2)    := geom(m2) * log2((162/97) * X0)          「前提左端」
  m2 可行  <=>  G(m2) <= (m2/m) * K
  v(m2,K)  := (m2/m) * K / geom(m2)                   （= (m2/m)K(delta-1)/(delta^m2-1)）
  A(m2)    := 0 (m2=m) | 3/X0 (m2=m-1) | (97(m-m2)+73)/(54*X0) (其余)
  eps(m2,K):= (A(m2) + 3/(2^v-1) + 3*(m2-1)/(2^v-1)^delta) / (3*K*ln2)
  eps_opt(K) := min{ eps(m2,K) : m2 可行 }             【约定 min_eps】
  Psi_lem(K) := Lemma 22 的 q：取区间 (delta, delta+eps_opt(K)) 两端连分数的首个相异
                下标 k，ck := min(A_k,B_k)+1，q := 分母([A_0;...;A_{k-1}, ck])
  Psi_true(K):= 区间 (delta, delta+eps_opt(K)) 内分母最小的分数之分母（真值）

Psi_true 的独立算法（不走 Lemma 22 的公式）：
  1. 取 delta 的连分数收敛项 p_n/q_n 与全部半收敛项 (p_n + t p_{n+1})/(q_n + t q_{n+1})；
  2. 只留上侧（值 > delta）者，按分母升序扫描并做「记录筛选」（gap 比此前一切更小者
     才入列），得到「最佳上逼近」序列：分母严格增、gap 严格减；
  3. Psi_true(K) := 序列中第一个 gap < eps_opt(K) 的分母。
  完备性依据是「δ 的一切最佳逼近都是收敛项或半收敛项」这一标准事实；本文件用
  `brute_min_den` 在小区间上对它做穷举对拍（见 route4_adv_search.py 的单元测试）。
"""

from fractions import Fraction

from mpmath import mp, mpf, log, power, floor

X0_INT = 695 * 2 ** 60
X0 = mpf(X0_INT)
M = 92                      # 本路线只打 m = 92 这一格（materials.md:146）
DPS = 100                   # 搜索精度；锚点另在 dps=250 复核

K_STAR = 205632218873398596256


def K_cross_lo():
    """route-4.md:202 二分区间左端（按当前 mp.dps 重建，避免模块导入期的精度截断）。"""
    return mpf("313195478959172262767.2965018064132891595")


def K_cross_hi():
    """route-4.md:202 二分区间右端。"""
    return mpf("313195478959172262933.8299555001867702231")


def setdps(d):
    mp.dps = d


def delta():
    return mp.log(3) / mp.log(2)


def geom(m2):
    d = delta()
    return (power(d, m2) - 1) / (d - 1)


def log2(x):
    return mp.log(x) / mp.log(2)


def G(m2):
    d = delta()
    return (power(d, m2) - 1) / (d - 1) * log2(mpf(162) / 97 * X0)


def feasible(m2, K):
    return G(m2) <= (mpf(m2) / M) * K


def A_of(m2):
    if m2 == M:
        return mpf(0)
    if m2 == M - 1:
        return mpf(3) / X0
    return mpf(97 * (M - m2) + 73) / (54 * X0)


def v_of(m2, K):
    return (mpf(m2) / M) * K / geom(m2)


def eps_of(m2, K):
    v = v_of(m2, K)
    t = power(2, v) - 1
    return (A_of(m2) + 3 / t + 3 * mpf(m2 - 1) / power(t, delta())) / (3 * K * mp.log(2))


def feasible_set(K):
    return [m2 for m2 in range(1, M + 1) if feasible(m2, K)]


def eps_opt_min_eps(K):
    """min_eps 约定：取 eps 最小的可行 m2。返回 (m2, eps) 或 None。"""
    best = None
    for m2 in feasible_set(K):
        e = eps_of(m2, K)
        if best is None or e < best[1]:
            best = (m2, e)
    return best


def eps_opt_max_feasible(K):
    fs = feasible_set(K)
    if not fs:
        return None
    m2 = fs[-1]
    return (m2, eps_of(m2, K))


# ---------------------------------------------------------------- 连分数工具

def cf_digits(x, nmax):
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


_DELTA_DIGITS = {}


def delta_digits(nmax):
    key = (mp.dps, nmax)
    if key not in _DELTA_DIGITS:
        _DELTA_DIGITS[key] = cf_digits(delta(), nmax)
    return _DELTA_DIGITS[key]


def convergents(nmax):
    A = delta_digits(nmax)
    pm2, pm1 = 0, 1
    qm2, qm1 = 1, 0
    out = []
    for a in A:
        p = a * pm1 + pm2
        q = a * qm1 + qm2
        out.append((p, q))
        pm2, pm1 = pm1, p
        qm2, qm1 = qm1, q
    return out, A


_UPPER_RECORDS = {}


def upper_approx_records(cap, nmax=None):
    """
    最佳上逼近记录序列（分母升序、gap 严格降）。返回 [(p, q, gap), ...]。
    候选族：收敛项本身 + 相邻收敛项之间的全部半收敛项（分母 <= cap）。
    """
    key = (mp.dps, cap)
    if key in _UPPER_RECORDS:
        return _UPPER_RECORDS[key]
    if nmax is None:
        nmax = max(80, int(3.3 * len(str(cap))) + 40)
    convs, A = convergents(nmax)
    d = delta()
    cands = set()
    for (p, q) in convs:
        if q <= cap:
            cands.add((p, q))
    for n in range(len(convs) - 1):
        pn, qn = convs[n]
        pn1, qn1 = convs[n + 1]
        # convergents() 返回 out[i] = p_i/q_i（无哨兵项），故
        # (convs[n], convs[n+1]) = (p_n, p_{n+1})，其间半收敛项为
        #   (p_n + t·p_{n+1})/(q_n + t·q_{n+1})，t = 1..a_{n+2}（t = a_{n+2} 给 p_{n+2}）。
        # 旧版误用 A[n]（差两个下标），漏掉 a_{n+2} 较大的族（如 t = 12 那一档），
        # 已由 [S0.2] 的暴力对拍抓出；现改用 A[n+2] 并留 3 项余量。
        tmax = (A[n + 2] if n + 2 < len(A) else (A[-1] if A else 0)) + 3
        for t in range(1, tmax + 1):
            p = pn + t * pn1
            q = qn + t * qn1
            if 0 < q <= cap:
                cands.add((p, q))
    ups = []
    for (p, q) in cands:
        g = mpf(p) / q - d
        if g > 0:
            ups.append((p, q, g))
    ups.sort(key=lambda x: x[1])
    recs = []
    for (p, q, g) in ups:
        if not recs or g < recs[-1][2]:
            recs.append((p, q, g))
    _UPPER_RECORDS[key] = recs
    return recs


def psi_true(K, cap=None, records=None):
    """区间 (delta, delta+eps_opt(K)) 内分母最小的分数之分母；返回 dict。"""
    b = eps_opt_min_eps(K)
    if b is None:
        return {"K": K, "psi": None, "reason": "无可行 m2"}
    m2, e = b
    if records is None:
        if cap is None:
            cap = int(max(10 ** 26, 60 * (1 / mpf(e)) ** mpf("0.55")))
        records = upper_approx_records(cap)
    hit = None
    for (p, q, g) in records:
        if g < e:
            hit = (p, q, g)
            break
    if hit is None:
        return {"K": K, "psi": None, "reason": "记录序列截断", "m2": m2, "eps": e}
    p, q, g = hit
    return {"K": K, "psi": q, "m2": m2, "eps": e, "gap": g, "num": p,
            "right_margin": e - g, "records_n": len(records)}


def brute_min_den(a, b, qmax):
    """暴力：返回 (q, p) 使 a < p/q < b 的最小 q；无则 None。a,b 为 mpf。"""
    for q in range(1, qmax + 1):
        p0 = floor(a * q) + 1
        if p0 < b * q:
            return (q, int(p0))
    return None


def first_diff_index(A, B):
    k = 0
    while k < min(len(A), len(B)) and A[k] == B[k]:
        k += 1
    return k


def prefix_conv(A, k):
    """连分数前缀 A_0..A_{k-1} 的 (p_{k-1}, p_{k-2}, q_{k-1}, q_{k-2})。"""
    pm2, pm1 = 0, 1
    qm2, qm1 = 1, 0
    for i in range(k):
        p = A[i] * pm1 + pm2
        q = A[i] * qm1 + qm2
        pm2, pm1 = pm1, p
        qm2, qm1 = qm1, q
    return pm1, pm2, qm1, qm2


def cf_value_tail(tail):
    v = Fraction(tail[-1])
    for c in reversed(tail[:-1]):
        v = Fraction(c) + Fraction(1) / v
    return v


def cf_value_parts(c0, tail):
    if not tail:
        return Fraction(c0)
    return Fraction(c0) + Fraction(1) / cf_value_tail(tail)


def psi_lem(K, nmax=500):
    """Lemma 22 的 q（项目口径的 Psi，用于对拍）。返回 dict。"""
    b = eps_opt_min_eps(K)
    if b is None:
        return {"K": K, "psi": None, "reason": "无可行 m2"}
    m2, e = b
    A = delta_digits(nmax)
    B = cf_digits(delta() + e, nmax)
    k = first_diff_index(A, B)
    if k >= min(len(A), len(B)):
        return {"K": K, "psi": None, "reason": "连分数未分离", "m2": m2, "eps": e}
    pm1, pm2, qm1, qm2 = prefix_conv(A, k)
    ck = min(A[k], B[k]) + 1
    q = ck * qm1 + qm2
    gamma = cf_value_parts(A[0], A[1:k] + [ck])
    d = delta()
    gm = mpf(gamma.numerator) / gamma.denominator
    return {"K": K, "psi": q, "m2": m2, "eps": e, "k": k, "ck": ck,
            "A_k": A[k], "B_k": B[k], "q_km1": qm1, "q_km2": qm2,
            "gamma_num": gamma.numerator, "gamma_den": gamma.denominator,
            "left_margin": gm - d, "right_margin": (d + e) - gm,
            "in_interval": (gm > d and gm < d + e)}


def chain(K0, max_steps=80, cap=None, psi_fn=None):
    if psi_fn is None:
        psi_fn = psi_true
    seq = []
    K = K0
    for _ in range(max_steps):
        r = psi_fn(K)
        r["K_in"] = K
        seq.append(r)
        if r["psi"] is None or r["psi"] <= K:
            return seq, K, False
        K = r["psi"]
        if cap is not None and K > cap:
            return seq, K, True
    return seq, K, False


def U(m):
    """Simons 与 de Weger 上界（materials.md:90 逐字转引）：K < 1.4784 m delta^m。"""
    return mpf("1.4784") * m * power(delta(), m)


def nstr(x, n=25):
    return mp.nstr(x, n)
