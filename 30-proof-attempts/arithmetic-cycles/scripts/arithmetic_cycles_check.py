#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arithmetic-cycles 路线的可跑检查脚本。

全部数字由本脚本自己算出；凡与文献对照处，注释写明对照对象（本会话已读原文）。

运行：
    cd 30-proof-attempts/arithmetic-cycles
    /Users/luna/Documents/math\ IA/collatz-attack/20-experiments/.venv/bin/python scripts/arithmetic_cycles_check.py

分节：
  A  基础量：delta = log2 3、连分数、收敛项（与项目笔记和 Simons 与 de Weger 表对照）
  B  窗口判据的幸存集：最小幸存 K（正侧、负侧），复现 20-experiments 的实验表
  C  幸存集结构：最小幸存者与收敛项分母；对任意有限 X0 幸存集非空
  D  上界：chaining 型 U(m)（= J2）与 Rhein 型 K1（两个都算，与文献两张表对照）
  E  下界：L(m) = max{q_n : q_n + q_{n+1} <= X0 log2/m}（广义 Crandall 引理）
  F  双向夹逼的交叉点 m*(X0)
  G  穷举奇偶向量（k <= 18）找环，核对窗口判据从不排除真实存在的环
"""

import sys
import time

try:
    import numpy as np
except Exception as e:
    print("需要 numpy：", e)
    sys.exit(1)

try:
    from mpmath import mp, mpf, log, ceil, floor, fabs, exp
    mp.dps = 260
except Exception as e:
    print("需要 mpmath：", e)
    sys.exit(1)

OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)


DELTA = log(mpf(3)) / log(mpf(2))
LOG2 = log(mpf(2))
N_CF_MAX = 90

# ----------------------------------------------------------------------------
# A. 基础量
# ----------------------------------------------------------------------------
say("=" * 78)
say("A. delta = log2(3) 及其连分数")
say("=" * 78)
say("delta =", mp.nstr(DELTA, 30))


def cf_and_convergents(x, nmax):
    a, p, q = [], [], []
    cur = x
    for n in range(nmax + 1):
        an = int(floor(cur))
        a.append(an)
        if n == 0:
            p.append(an); q.append(1)
        elif n == 1:
            p.append(an * p[0] + 1); q.append(an * q[0])
        else:
            p.append(an * p[n - 1] + p[n - 2]); q.append(an * q[n - 1] + q[n - 2])
        fr = cur - an
        if fr == 0:
            break
        cur = 1 / fr
    return a, p, q


A_CF, P_CF, Q_CF = cf_and_convergents(DELTA, N_CF_MAX)
say("部分商 a_n（n = 0..40）：", A_CF[:41])
say("收敛项：")
for n in range(0, 41):
    d = mpf(P_CF[n]) - mpf(Q_CF[n]) * DELTA
    say("  n=%2d q_n=%-24s p_n=%-24s 符号=%s |p_n-q_n delta|=%s"
        % (n, Q_CF[n], P_CF[n], "+" if d > 0 else "-", mp.nstr(fabs(d), 8)))

# 精度自检：用更高精度重算连分数，比较前 N_CF_MAX+1 个部分商
_old_dps = mp.dps
mp.dps = 420
A2, P2, Q2 = cf_and_convergents(log(mpf(3)) / log(mpf(2)), N_CF_MAX)
mp.dps = _old_dps
same = A_CF[:len(A2)] == A2
say("精度自检（260 位 vs 420 位重算前 %d 个部分商）：%s" % (len(A2), "完全一致" if same else "不一致"))

check_pairs = {19: 397573379, 20: 6189245291, 21: 6586818670,
               22: 65470613321, 23: 137528045312, 24: 753110839881}
say("对照已知收敛项分母（本项目 10-literature/notes/cycles.md 第 16 条，源自 Simons 与 de Weger 编号）：")
allok = True
for n, v in check_pairs.items():
    ok = (n < len(Q_CF) and Q_CF[n] == v)
    allok = allok and ok
    say("  q_%d = %s  期望 %s  %s" % (n, Q_CF[n], v, "一致" if ok else "不一致"))
say("六个收敛项分母全部一致？ %s" % allok)

sw_q = {34: "2.6711e17", 33: "1.3044e17", 32: "6.2345e15", 31: "5.7509e15",
        30: "4.8361e14", 29: "4.3116e14", 28: "5.2449e13", 23: "1.3752e11",
        22: "6.5470e10", 21: "6.5868e9", 20: "6.1892e9"}
say("对照 Simons 与 de Weger（v1.43）Corollary 11 引用的 q_n：")
for n, v in sorted(sw_q.items()):
    if n < len(Q_CF):
        say("  q_%-3d = %-24s <-> 文献 %s" % (n, Q_CF[n], v))

say("champion 部分商（偶数下标的严格纪录，供 D 节 K2 说明用）：")
best, champs = -1, []
for n in range(0, len(A_CF)):
    if n % 2 == 0 and A_CF[n] > best:
        best = A_CF[n]
        champs.append((n, A_CF[n]))
say("  ", champs)


# ----------------------------------------------------------------------------
# 有限精度工具：delta 用整数 Δ / 2^N 表示，frac(K delta) 用整数运算
# ----------------------------------------------------------------------------
N_BITS = 150
DELTA_INT = int(floor(DELTA * mpf(2) ** N_BITS))
TWO_N = 1 << N_BITS


def frac_exact(K):
    return mpf((K * DELTA_INT) % TWO_N) / mpf(TWO_N)


def one_minus_frac_exact(K):
    return mpf(TWO_N - (K * DELTA_INT) % TWO_N) / mpf(TWO_N)


def survivor_value(K, w, side):
    """返回 True/False/None（None 表示判定裕度不足）。"""
    err = mpf(K) / mpf(2) ** N_BITS
    if side == "pos":
        d = one_minus_frac_exact(K) - mpf(K) * w
    else:
        d = frac_exact(K) - mpf(K) * w
    if d > err:
        return False
    if d < -err:
        return True
    return None


def first_survivor_side(w, Kmax, side):
    """numpy 预筛 + 高精度判定，返回最小幸存 K（无则 None）。"""
    Ks = np.arange(1, Kmax + 1, dtype=np.float64)
    frac = (Ks * float(DELTA)) % 1.0
    v = (1.0 - frac) if side == "pos" else frac
    thr = float(w) * Ks + 1e-6          # 预筛裕度远大于 double 误差（约 4e-9）
    cand = Ks[v <= thr].astype(np.int64)
    for K in cand:
        r = survivor_value(int(K), w, side)
        if r is True:
            return int(K)
        if r is None:
            raise RuntimeError("判定裕度不足 K=%d" % K)
    return None


# ----------------------------------------------------------------------------
# B. 窗口判据的幸存集
# ----------------------------------------------------------------------------
say("")
say("=" * 78)
say("B. 窗口判据的幸存集（w = 1/((3 X0 - 1) ln 2)）")
say("=" * 78)
say("判据（本项目 20-experiments/findings/cycles.md 第 2.5 节；本脚本独立重算）：")
say("  正环：若 1 - frac(K delta) > K w，则不存在奇数步数为 K 的非平凡正环；")
say("  负环：若     frac(K delta) > K w，则不存在奇数步数为 K 的非平凡负环；")
say("  前提：环上元素绝对值至少 X0；w = 1/((3 X0 - 1) ln 2)。")

X0_list = [10 ** 6, 10 ** 8, 3 * 10 ** 9, 10 ** 10, 3 * 10 ** 10, 10 ** 11, 10 ** 12]
exp_Mplus = {10 ** 6: 2965, 10 ** 8: 15600, 3 * 10 ** 9: 79334, 10 ** 10: 190536,
             3 * 10 ** 10: 190536, 10 ** 11: 190536, 10 ** 12: 10781273}
exp_Mminus = {10 ** 6: 664, 10 ** 8: 16265, 3 * 10 ** 9: 111201, 10 ** 10: 111201,
              3 * 10 ** 10: 492275, 10 ** 11: 1063886, 10 ** 12: 5446237}

say("")
say("X0            正侧最小幸存 K      M+ 实验值      负侧最小幸存 K      M- 实验值")
results_B = {}
t0 = time.time()
for X0 in X0_list:
    w = 1 / ((3 * mpf(X0) - 1) * LOG2)
    kp = first_survivor_side(w, exp_Mplus[X0] + 200, "pos")
    kn = first_survivor_side(w, exp_Mminus[X0] + 200, "neg")
    results_B[X0] = (kp, kn, w)
    say("%-13s %-19s %-15s %-19s %-10s" % (X0, kp, exp_Mplus[X0], kn, exp_Mminus[X0]))
ok_pos = all(results_B[X0][0] - 1 == exp_Mplus[X0] for X0 in X0_list)
ok_neg = all(results_B[X0][1] - 1 == exp_Mminus[X0] for X0 in X0_list)
say("正侧逐档一致：%s；负侧逐档一致：%s；（用时 %.1f s）" % (ok_pos, ok_neg, time.time() - t0))


# ----------------------------------------------------------------------------
# C. 幸存集结构
# ----------------------------------------------------------------------------
say("")
say("=" * 78)
say("C. 幸存集结构：最小幸存者与收敛项分母；对任意有限 X0 幸存集非空")
say("=" * 78)


def candidate_denominators():
    """全部收敛项分母与半收敛项分母 q_{n-1} + j q_n（1 <= j <= a_{n+1}）。"""
    out = []
    for n in range(0, len(Q_CF)):
        out.append((Q_CF[n], "收敛 q_%d" % n))
    for n in range(1, len(Q_CF) - 1):
        a_next = A_CF[n + 1] if n + 1 < len(A_CF) else 1
        for j in range(1, a_next + 1):
            q = Q_CF[n - 1] + j * Q_CF[n]
            out.append((q, "半收敛 q_%d+%dq_%d" % (n - 1, j, n)))
    return sorted(out)


CAND = candidate_denominators()


def min_survivor_in_candidates(w, side):
    """在（半）收敛项分母中找最小幸存者。"""
    best, tag = None, None
    for q, t in CAND:
        v = one_minus_frac_exact(q) if side == "pos" else frac_exact(q)
        if v <= mpf(q) * w:
            if best is None or q < best:
                best, tag = q, t
    return best, tag


say("比较「全体 K 的最小幸存者（全扫描）」与「（半）收敛项分母中的最小幸存者」：")
for X0 in X0_list:
    kp, kn, w = results_B[X0]
    cp, tp = min_survivor_in_candidates(w, "pos")
    cn, tn = min_survivor_in_candidates(w, "neg")
    say("  X0=%-13s 正侧：全体 %-10s 候选集 %-10s (%s) %s" % (
        X0, kp, cp, tp, "一致" if cp == kp else "不一致"))
    say("  %-17s 负侧：全体 %-10s 候选集 %-10s (%s) %s" % (
        "", kn, cn, tn, "一致" if cn == kn else "不一致"))

say("")
say("对很大的 X0（此时无法全扫描，只在候选集里找）：最小幸存者仍在（半）收敛项分母上")
for e in [20, 40, 60]:
    X0 = mpf(10) ** e
    w = 1 / ((3 * X0 - 1) * LOG2)
    cp, tp = min_survivor_in_candidates(w, "pos")
    cn, tn = min_survivor_in_candidates(w, "neg")
    say("  X0 = 1e%-3d 正侧最小幸存 K = %-24s (%s)" % (e, cp, tp))
    say("  %-10s 负侧最小幸存 K = %-24s (%s)" % ("", cn, tn))
say("含义：最小幸存者随 X0 无界增长，所以窗口判据对任何有限验证界都不能收尾。")


# ----------------------------------------------------------------------------
# D. 上界：chaining 型 U(m) 与 Rhein 型 K1(m)
# ----------------------------------------------------------------------------
say("")
say("=" * 78)
say("D. 上界（chaining + 连分数）")
say("=" * 78)
say("chaining 步（本文档第 5 步；与 Simons 与 de Weger Lemma 6/7 同型）：")
say("   |x_{i+1}| < B |x_i|^delta，B = (1+X0^-1)^delta / 2")
say("   => |x_i| < B^{1+delta+...+delta^{i-1}} |x_0|^{delta^i}")
say("   => |x_min| > C_m 2^{(delta-1)K/(delta^m-1)}，C_m = ((1+X0^-1)^m B^{T'})^{1/S}，")
say("      S = (delta^m-1)/(delta-1)，T' = sum_{i=1}^{m-1}(delta^i-1)/(delta-1)")
say("   => K 的上界 U(m) 由方程 m C_m^{-1} 2^{-(delta-1)x/(delta^m-1)} = log2/(2x) 定义（即文献的 J2）。")
say("      实现在 solve_U()：c_m = ((1+X0^-1)^m B^{T'})^{1/S}。")
say("Rhein 型（文献 Lemma 12 的模型）：Lambda > e^{-13.3(0.46057+log x)}")
say("   => K 的上界 K1(m) 由 e^{-13.3(0.46057+log x)} = m c_m 2^{-(delta-1)x/(delta^m-1)} 定义。")

X0_D = mpf("3.7469e18")     # Simons 与 de Weger v1.43：X0 = 3.25 * 2^60
say("X0 = 3.25 * 2^60 = %s" % mp.nstr(X0_D, 8))


def chain_T(m):
    """T' = sum_{i=1}^{m-1} (delta^i - 1)/(delta-1)，chaining 的指数和。"""
    if m == 1:
        return mpf(0)
    return ((DELTA ** m - DELTA) / (DELTA - 1) - (m - 1)) / (DELTA - 1)


def c_m(m, X0=X0_D):
    """本脚本自己的常数：B = (1+X0^-1)^delta / 2，S = (delta^m-1)/(delta-1)，
    c_m = ((1+X0^-1)^m B^{T'})^{1/S}（正侧；负侧没有 (1+X0^-1)^m 因子，见正文）。"""
    B = (1 + 1 / X0) ** DELTA / 2
    S = (DELTA ** m - 1) / (DELTA - 1)
    return ((1 + 1 / X0) ** m * B ** chain_T(m)) ** (1 / S)


def solve_U(m, X0=X0_D, neg_side=False):
    """解 m c_m 2^{-(delta-1)x/(delta^m-1)} = log2/(2x)（即文献的 J2 型方程）。"""
    B = (1 + 1 / X0) ** DELTA / 2
    S = (DELTA ** m - 1) / (DELTA - 1)
    if neg_side:
        cm = (B ** chain_T(m)) ** (1 / S)
    else:
        cm = ((1 + 1 / X0) ** m * B ** chain_T(m)) ** (1 / S)
    # 方程：log2(m cm) - (delta-1)x/(delta^m-1) = log2(log2/(2x))
    #  x = S [ log2(2 m cm / log 2) + log2 x ]
    x = mpf(10) ** (0.66445 * m)
    for _ in range(400):
        r = S * (log(2 * m * cm / LOG2) / LOG2 + log(x) / LOG2)
        if r <= 0:
            r = mpf(1)
        if fabs(r - x) < 1e-25 * max(mpf(1), x):
            break
        x = r
    return x


def solve_K1(m, X0=X0_D):
    """解 e^{-13.3(0.46057 + log x)} = m c_m 2^{-(delta-1) x/(delta^m-1)}（Rhein 型，取对数后迭代）。"""
    cm = c_m(m, X0)
    S = (DELTA ** m - 1) / (DELTA - 1)
    x = mpf(10) ** (0.66445 * m)
    for _ in range(400):
        # log2(m cm) - (delta-1)x/(delta^m-1) = -13.3(0.46057+ln x)/ln2
        # x = S * [ log2(m cm) + 13.3(0.46057+ln x)/ln 2 ]
        r = S * (log(m * cm) / LOG2 + mpf("13.3") * (mpf("0.46057") + log(x)) / LOG2)
        if r <= 0:
            r = mpf(1)
        if fabs(r - x) < 1e-25 * max(mpf(1), x):
            break
        x = r
    return x


say("")
say("m      U(m)=J2(m) 本脚本     文献 J2(m)          比值      K1(m) 本脚本      文献 K1(m)         比值")
sw_J2 = {64: "5.9379e14", 67: "2.4553e15", 68: "3.9396e15",
         90: "1.2542e20", 91: "2.0068e20", 100: "1.3737e22"}
sw_K1 = {2: "3.0877e2", 10: "3.5858e4", 63: "4.8181e15", 64: "7.7350e15",
         100: "1.7876e23"}
U_vals, K1_vals = {}, {}
for m in [2, 10, 63, 64, 67, 68, 90, 91, 100]:
    U = solve_U(m, X0_D); U_vals[m] = U
    K1 = solve_K1(m, X0_D); K1_vals[m] = K1
    rj = sw_J2.get(m)
    rk = sw_K1.get(m)
    say("%-6d %-24s %-20s %-8s %-18s %-19s %s" % (
        m, mp.nstr(U, 8), rj if rj else "-",
        mp.nstr(U / mpf(rj), 4) if rj else "-",
        mp.nstr(K1, 6), rk if rk else "-",
        mp.nstr(K1 / mpf(rk), 4) if rk else "-"))
say("注：文献 J2 与 K1 各自来自 Simons 与 de Weger v1.43 第 12 页与第 11 页的两张表；")
say("    K1 是 Rhein 型（超越论）上界，J2 是 chaining + 连分数（初等）上界，两者同阶 m delta^m。")
say("渐近：U(m)/(m delta^m) -> log(delta)/((delta-1) log 2) = %s"
    % mp.nstr(log(DELTA) / ((DELTA - 1) * LOG2), 8))
for m in [10, 63, 91, 100]:
    say("   m=%-4d U(m)/(m delta^m) = %-10s K1(m)/(m delta^m) = %s" % (
        m, mp.nstr(U_vals[m] / (m * DELTA ** m), 8),
        mp.nstr(K1_vals[m] / (m * DELTA ** m), 8)))
say("即：只用 chaining + 连分数的上界比 Rhein 型上界好一个常数因子（同阶 m delta^m）。")


# ----------------------------------------------------------------------------
# E. 下界 L(m)
# ----------------------------------------------------------------------------
say("")
say("=" * 78)
say("E. 下界 L(m) = max{ q_n : q_n + q_{n+1} <= X0 log2 / m }")
say("=" * 78)


def L_of_m(m, X0):
    thr = X0 * LOG2 / m
    best, bestn = None, None
    for n in range(0, len(Q_CF) - 1):
        if mpf(Q_CF[n]) + mpf(Q_CF[n + 1]) <= thr:
            best, bestn = Q_CF[n], n
    return best, bestn


for X0v, name in [(mpf("3.7469e18"), "Simons 与 de Weger v1.43 的 X0 = 3.25 * 2^60"),
                  (mpf(695) * mpf(2) ** 60, "Hercher 2023 的 X0 = 695 * 2^60")]:
    say("X0 = %s（%s）" % (mp.nstr(X0v, 8), name))
    say("  m           L(m)                      q 下标")
    for m in [1, 3, 7, 19, 20, 68, 91, 100, 216, 217]:
        L, n = L_of_m(m, X0v)
        say("  %-11d %-25s q_%s" % (m, mp.nstr(L, 8) if L else "无", n))


# ----------------------------------------------------------------------------
# F. 双向夹逼
# ----------------------------------------------------------------------------
say("")
say("=" * 78)
say("F. 双向夹逼：比较 U(m) 与 L(m)，找夹逼失效处 m*(X0)")
say("=" * 78)
for X0v, name in [(mpf("3.7469e18"), "SW v1.43 的 X0（= 3.25 * 2^60）"),
                  (mpf(695) * mpf(2) ** 60, "Hercher 2023 的 X0（= 695 * 2^60）")]:
    say("X0 = %s（%s）" % (mp.nstr(X0v, 8), name))
    say("  m      U(m)                L(m)                判定")
    cross = None
    for m in list(range(2, 121)):
        U = solve_U(m, X0v)
        L, n = L_of_m(m, X0v)
        if L is None:
            continue
        good = U < L
        if not good and cross is None:
            cross = m
        if m in (60, 63, 64, 65, 66, 67, 68, 69, 70, 75, 80, 90, 91, 100, 110):
            say("  %-6d %-20s %-20s %s" % (m, mp.nstr(U, 8), mp.nstr(L, 8),
                                           "U<L（矛盾，排除）" if good else "U>=L（夹逼失效）"))
    say("  首个 U(m) >= L(m) 的 m = %s" % cross)
    say("")


# ----------------------------------------------------------------------------
# G. 穷举奇偶向量 + 判据一致性
# ----------------------------------------------------------------------------
say("=" * 78)
say("G. 穷举奇偶向量（k <= 18）找环，核对窗口判据从不排除真实存在的环")
say("=" * 78)


def enumerate_and_filter(kmax):
    hits, real = 0, {}
    for k in range(1, kmax + 1):
        for bits in range(1 << k):
            m = bin(bits).count("1")
            if m == 0:
                continue
            c, pw = 0, 1
            for t in range(k - 1, -1, -1):
                if (bits >> t) & 1:
                    c += (1 << t) * pw
                    pw *= 3
            D = (1 << k) - 3 ** m
            if D == 0 or c % D != 0:
                continue
            x = c // D
            if x == 0:
                continue
            hits += 1
            v, ok = x, True
            for t in range(k):
                b = (bits >> t) & 1
                if v % 2 == 0:
                    if b != 0:
                        ok = False; break
                    v //= 2
                else:
                    if b != 1:
                        ok = False; break
                    v = (3 * v + 1) // 2
            if ok and v == x:
                # 记录环上全部元素（沿加速映射走 k 步）
                elems, w2 = [], x
                for _ in range(k):
                    elems.append(w2)
                    w2 = (w2 // 2) if w2 % 2 == 0 else ((3 * w2 + 1) // 2)
                real[(x, k, m)] = (bits, elems)
    return hits, real


t0 = time.time()
hits, real = enumerate_and_filter(18)
say("k <= 18 穷举完成（用时 %.1f s）：整除命中 %d 条（含旋转重复），真环 %d 条" % (
    time.time() - t0, hits, len(real)))
prims = {}
for (x, k, m), (bits, elems) in real.items():
    prims.setdefault(abs(x), set()).add(tuple(sorted(set(elems), key=abs)))
say("去重后（按起点绝对值）的不同环轨道数：%d" % len(prims))
say("各轨道的元素绝对值：")
for a in sorted(prims):
    for t in prims[a]:
        say("   |x|=%s -> %s" % (a, sorted(set(abs(e) for e in t))))

say("")
say("一致性检查：判据说「排除」的 K，在 k <= 18 的穷举里不得出现该奇数步数的、")
say("            元素绝对值 >= X0 的环。")
for X0 in [2, 5, 10, 100, 10 ** 6]:
    w = 1 / ((3 * mpf(X0) - 1) * LOG2)
    bad = []
    for K in range(1, 19):
        pos = survivor_value(K, w, "pos")
        neg = survivor_value(K, w, "neg")
        hp = [x for (x, k, m), (bits, elems) in real.items()
              if m == K and x > 0 and min(abs(e) for e in elems) >= X0]
        hn = [x for (x, k, m), (bits, elems) in real.items()
              if m == K and x < 0 and min(abs(e) for e in elems) >= X0]
        if pos is False and hp:
            bad.append(("正", K, hp))
        if neg is False and hn:
            bad.append(("负", K, hn))
    say("  X0 = %-10s 违反 %d 条 %s" % (X0, len(bad), bad[:4]))


# ----------------------------------------------------------------------------
# H. 两个新引理的核对：连分数上界 |p_n - q_n delta| < 1/q_{n+1}；周期下界的桥接
# ----------------------------------------------------------------------------
say("")
say("=" * 78)
say("H. 核对：连分数标准不等式与「K 门槛导出周期下界」的桥接引理")
say("=" * 78)
bad = []
for n in range(0, len(Q_CF) - 1):
    d = fabs(mpf(P_CF[n]) - mpf(Q_CF[n]) * DELTA)
    if not (d < mpf(1) / mpf(Q_CF[n + 1])):
        bad.append(n)
say("|p_n - q_n delta| < 1/q_{n+1} 对 n = 0..%d 全部成立？ %s" % (len(Q_CF) - 2, not bad))
signok = all(((mpf(P_CF[n]) - mpf(Q_CF[n]) * DELTA) > 0) == (n % 2 == 1)
             for n in range(0, len(Q_CF) - 1))
say("奇数 n 时 p_n - q_n delta > 0、偶数 n 时 < 0（SW Lemma 9(d)）？ %s" % signok)

say("")
say("桥接引理（周期下界的正式形式）：K > q_n 且 n 为奇数时，")
say("  加速映射周期 k = K + L > delta K > delta q_n，标准映射周期 = k + K > (1 + delta) q_n。")
for n in [23, 24]:
    qn = mpf(Q_CF[n])
    acc = ceil(DELTA * qn)
    std = ceil((1 + DELTA) * qn)
    say("  n=%d: q_n = %s  加速下界 = %s  标准下界 = %s" % (
        n, Q_CF[n], acc, std))
say("文献记录值（本项目 notes/cycles.md 第 16 条）：加速 217976794617，标准 355504839929。")
qn23 = mpf(Q_CF[23])
say("  复算 n=23：delta q_23 = %s ；(1+delta) q_23 = %s" % (
    mp.nstr(DELTA * qn23, 20), mp.nstr((1 + DELTA) * qn23, 20)))


# ----------------------------------------------------------------------------
# I. m 无关的双侧下界（本文档第 8 步的 m 无关形式）
# ----------------------------------------------------------------------------
say("")
say("=" * 78)
say("I. m 无关下界：K > q_{n*}，n* = max{ n : q_n (q_n + q_{n+1}) < (3X0-1) ln 2 }")
say("=" * 78)
say("（对正环与负环同时成立；证明见文档第 8 步，用到 |Lambda| <= K/(3X0-1) 与 Lemma 9(b)(c)。）")
for X0 in [mpf(10) ** 12, mpf("3.7469e18"), mpf(1536) * mpf(2) ** 60, mpf(2) ** 71]:
    C = (3 * X0 - 1) * LOG2
    nstar = None
    for n in range(0, len(Q_CF) - 1):
        if mpf(Q_CF[n]) * (mpf(Q_CF[n]) + mpf(Q_CF[n + 1])) < C:
            nstar = n
    say("  X0 = %-14s C = %-12s n* = %-4s K > q_%s = %s" % (
        mp.nstr(X0, 8), mp.nstr(C, 6), nstar, nstar, Q_CF[nstar] if nstar is not None else "-"))
say("对照：Hercher 2023 Corollary 29（X0 >= 1536 * 2^60 时 K > 1.375e11 = q_23）比本式强。")

say("")
say("=" * 78)
say("脚本结束")
say("=" * 78)

with open("results/arithmetic_cycles_check.txt", "w") as f:
    f.write("\n".join(OUT) + "\n")
print("\n[已写入 results/arithmetic_cycles_check.txt]")
