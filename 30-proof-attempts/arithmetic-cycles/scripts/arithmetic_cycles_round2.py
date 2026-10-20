#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arithmetic-cycles 第二轮（路线探索者续作）数值复核。

本脚本独立于上一轮的 arithmetic_cycles_check.py（不 import 它，重新实现）。

复核的五条新命题：
  A  收敛项表（80 位与 260 位互校；q_19..q_24 与项目记录对照）
  B  1 圈的精确判别（区间条件 + 整除条件），K <= KMAX 的完全检验；
     以及 (K, L, m) 三参数方程的独立核对
  C  窗口判据：可达上界（新引理 N2）、幸存者丰度（新引理 N3）、M± 表复核
  D  有理环候选（新引理 N1）：所有长度 <= KWORD 的字，T^k(x) = x 与奇偶向量逐位核对
  E  最大元定向前缀引理与 c_max 公式（已知环核对）
  F  与既有记录值的交叉核对（q_23 桥接）

运行（本目录下）：
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
      scripts/arithmetic_cycles_round2.py
"""
import sys
from fractions import Fraction

from mpmath import mp, mpf, log, floor, nstr

OUT = []


def say(*args):
    s = " ".join(str(a) for a in args)
    OUT.append(s)
    print(s)


KWORD = 14          # D 段最大字长
KMAX_ONE = 20000    # B 段 1 圈直接检验的最大 K

# ----------------------------------------------------------------------
# A. delta = log2 3 的连分数与收敛项
# ----------------------------------------------------------------------
say("=" * 72)
say("A. delta = log2(3) 的连分数与收敛项（两种精度互校）")
say("=" * 72)


def cf_and_convergents(dps, nmax):
    mp.dps = dps
    delta = log(mpf(3), 2)
    a, p, q = [], [0, 1], [1, 0]
    x = delta
    res = []
    for j in range(nmax):
        aj = int(floor(x))
        a.append(aj)
        pn = aj * p[-1] + p[-2]
        qn = aj * q[-1] + q[-2]
        p.append(pn)
        q.append(qn)
        res.append((aj, pn, qn))
        frac = x - aj
        if frac == 0:
            break
        x = 1 / frac
    return delta, res


NCF = 30
delta80, CF80 = cf_and_convergents(80, NCF)
delta260, CF260 = cf_and_convergents(260, NCF)
A80 = [t[0] for t in CF80]
A260 = [t[0] for t in CF260]
say("部分商（80 位） ：", A80)
say("部分商（260 位）：", A260)
say("两种精度下前 %d 个部分商完全一致？ %s" % (len(A80), A80 == A260))

A_CF = A80
P_CF = [t[1] for t in CF80]
Q_CF = [t[2] for t in CF80]
say("")
say("  n   a_n        q_n                     p_n                     p_n - q_n delta")
mp.dps = 80
for n in range(0, 26):
    e = P_CF[n] - Q_CF[n] * delta80
    say("  %2d  %2d   %-22d  %-22d  %s" % (n, A_CF[n], Q_CF[n], P_CF[n], nstr(e, 12)))
say("")
rec = {19: 397573379, 20: 6189245291, 21: 6586818670,
       22: 65470613321, 23: 137528045312, 24: 753110839881}
ok = all(Q_CF[n] == v for n, v in rec.items())
say("q_19..q_24 与本项目记录值（397573379, 6189245291, 6586818670, 65470613321,")
say("  137528045312, 753110839881）逐位一致？ %s" % ok)

# |p_n - q_n delta| < 1/q_{n+1} 与符号规律
bad = [n for n in range(0, NCF - 2) if abs(P_CF[n] - Q_CF[n] * delta80) >= 1 / Q_CF[n + 1]]
say("|p_n - q_n delta| < 1/q_{n+1} 对 n = 0..%d 全部成立？ %s" % (NCF - 3, not bad))
signok = all((P_CF[n] - Q_CF[n] * delta80 > 0) == (n % 2 == 1) for n in range(0, 26))
say("奇数 n 时 p_n - q_n delta > 0、偶数 n 时 < 0？ %s" % signok)

# ----------------------------------------------------------------------
# B. 1 圈的精确判别
# ----------------------------------------------------------------------
say("")
say("=" * 72)
say("B. 1 圈（奇偶字 1^K 0^L）的精确判别与 K <= %d 的完全检验" % KMAX_ONE)
say("=" * 72)
say("")
say("推导（本脚本用的必要充分条件，详见 attempt.md 第 9 步）：")
say("  设字为 1^K 0^L，则 c = 3^K - 2^K，D = 2^(K+L) - 3^K，x = c/D；")
say("  1 圈存在 <=> x 是正整数 <=> D | c；")
say("  又由 x + 1 = 2^K m（m >= 1）得 D | 2^L - 1 且 m = (2^L - 1)/D >= 1，")
say("  故 2^L (2^K - 1) <= 3^K - 1 且 2^(K+L) > 3^K；")
say("  后一式给出 L >= L0 := bit_length(3^K) - K，前一式给出 L <= L0（因为 2^(L0+1) > 2(3/2)^K >")
say("  (3^K-1)/(2^K-1) 对 K >= 1 成立），故 L = L0 是唯一候选。")
say("")

say("K = 1 的候选（应给出平凡环）：")
for K in (1,):
    three = 3 ** K
    N = three.bit_length()
    L = N - K
    D = (1 << N) - three
    cpu = (1 << L) * ((1 << K) - 1) <= three - 1
    div = ((1 << L) - 1) % D == 0
    x = Fraction(three - (1 << K), D)
    say("  K=%d: N=%d L=%d  D=%d  区间条件=%s  整除条件=%s  x=%s" %
        (K, N, L, D, cpu, div, x))

say("")
survivors = []
three = 1
two = 1
for K in range(1, KMAX_ONE + 1):
    three *= 3
    two *= 2
    N = three.bit_length()          # = ceil(K log2 3)，精确
    L = N - K
    if L < 1:
        continue
    if (1 << L) * (two - 1) <= three - 1:
        D = (1 << N) - three
        if ((1 << L) - 1) % D == 0:
            survivors.append((K, L, N))

say("对 K = 1..%d 逐个检验（全部用精确整数算术，无浮点）：" % KMAX_ONE)
say("  通过区间条件且通过整除条件的 (K, L, N)（即 1 圈候选）：%s" % (survivors,))
interval_pass = []
three = 1
two = 1
for K in range(1, KMAX_ONE + 1):
    three *= 3
    two *= 2
    N = three.bit_length()
    L = N - K
    if L >= 1 and (1 << L) * (two - 1) <= three - 1:
        interval_pass.append(K)
say("  只通过区间条件的 K：%s" % (interval_pass,))
say("  结论：K = 2..%d 内没有非平凡 1 圈（这是本脚本的直接检验范围）。" % KMAX_ONE)

say("")
say("归约恒等式的精确核对（用 Fraction 验算，不看整性）：对 (K, L) 令 D = 2^(K+L) - 3^K，")
say("  c = 3^K - 2^K，x = c/D，m = (x+1)/2^K；应恒有 2^L x + 1 = 3^K m 且")
say("  (m >= 1) <=> (D <= 2^L - 1) <=> (2^L (2^K - 1) <= 3^K - 1)。")
badA = badB = 0
for K in range(1, 26):
    for L in range(1, 40):
        D = (1 << (K + L)) - 3 ** K
        if D <= 0:
            continue
        c = 3 ** K - 2 ** K
        x = Fraction(c, D)
        m = (x + 1) / (1 << K)
        if 2 ** L * x + 1 != 3 ** K * m:
            badA += 1
        if (m >= 1) != ((1 << L) * ((1 << K) - 1) <= 3 ** K - 1):
            badB += 1
say("  K = 1..25, L = 1..39, D > 0 的全部组合：2^L x + 1 = 3^K m 失败数 = %d（应为 0）" % badA)
say("  (m >= 1) 与区间条件不等价的个数 = %d（应为 0）" % badB)
say("")
say("独立核对（三参数方程 m 3^K - 1 = 2^L (m 2^K - 1)，只对小的 K、m 枚举）：")
say("  即 T := (m 3^K - 1)/(m 2^K - 1) 必须是 2 的幂。")
found_m = []
three = 3
two = 2
for K in range(1, 41):
    three = 3 ** K
    two = 2 ** K
    for m in range(1, 20001):
        num = m * three - 1
        den = m * two - 1
        if num % den:
            continue
        T = num // den
        if T >= 2 and (T & (T - 1)) == 0:
            found_m.append((K, m, T))
say("  K <= 40, m <= 20000 的解 (K, m, T=2^L)：%s" % (found_m,))
say("  （T = 2 对应 K=1, m=1 的平凡环，x = 2^K m - 1 = 1。）")

say("")
say("B2. 与超越论输入的衔接（为什么 m = 1 这一档是「可封闭」的）")
say("  由本文件第 9 步，非平凡 1 圈的必要条件是：存在整数 N 使 0 < N ln2 - K ln3 < 2^(-K)。")
say("  Rhin 1987 型显式下界（数值按本项目文献笔记转引 Simons 与 de Weger v1.43 的 Lemma 12，")
say("  我未打开 Rhin 原文）：|N ln2 - K ln3| > exp(-13.3 (0.46057 + ln H))，H = max(N, K)。")
say("  比较要点：2^(-K) 随 K 指数衰减，而下界只按 H^(-13.3) 多项式衰减，故 K 一大，下界就大于")
say("  2^(-K)，于是必要条件与下界相撞。求门槛 K0（K >= K0 时下界 > 2^(-K)）：")
mp.dps = 40
K0 = None
for K in range(2, 2000):
    H = max(K, int(K * 1.6) + 2)
    lower = mp.e ** (-13.3 * (0.46057 + mp.log(H)))
    if lower > mp.mpf(2) ** (-K):
        K0 = K
        break
say("    K0 = %s（即 K >= %s 时，Rhin 型下界 > 2^(-K)）" % (K0, K0))
if K0:
    H = max(K0, int(K0 * 1.6) + 2)
    low = mp.e ** (-13.3 * (0.46057 + mp.log(H)))
    say("    在 K = %d 处：下界 = %s，2^(-K) = %s，比值 = %s"
        % (K0, nstr(low, 6), nstr(mp.mpf(2) ** (-K0), 6), nstr(low / mp.mpf(2) ** (-K0), 6)))
    Hn = max(20000, int(20000 * 1.6) + 2)
    lown = mp.e ** (-13.3 * (0.46057 + mp.log(Hn)))
    say("    在 K = 20000 处：下界 = %s，2^(-K) = %s，下界/2^(-K) = %s（远超 1）"
        % (nstr(lown, 6), nstr(mp.mpf(2) ** (-20000), 6),
           nstr(lown / mp.mpf(2) ** (-20000), 6)))
say("  结论（本文件第 10 步）：m = 1 档由「K <= 20000 的精确检验（本脚本 B 段，已实跑）」")
say("  加「K >= %s 的 Rhin 型下界（转引，未一手核对）」共同封闭，相容于文献把该档归于" % K0)
say("  Steiner 1977 的记载（Wikipedia 与项目笔记均为二手）。")

# ----------------------------------------------------------------------
# C. 窗口判据：可达上界、幸存者丰度、M± 表
# ----------------------------------------------------------------------
say("")
say("=" * 72)
say("C. 窗口判据：可达上界（N2）、幸存者丰度（N3）、M± 表复核")
say("=" * 72)
mp.dps = 50
D50 = log(mpf(3), 2)


def window_criterion(X0, kmax, side="pos"):
    """返回首个未被排除的 K（1 <= K <= kmax），找不到返回 None。"""
    C = (3 * mpf(X0) - 1) * log(mpf(2))
    w = 1 / C
    for K in range(1, kmax + 1):
        fr = mpf(K) * D50 - floor(mpf(K) * D50)
        if side == "pos":
            if 1 - fr <= K * w:
                return K, C, w
        else:
            if fr <= K * w:
                return K, C, w
    return None, C, w


say("")
say("M± 表复核（M = 首个未被排除的 K 减 1；项目实验记录：2966/665、15601/16266、")
say("  79335/111202、190537/111202、190537/492276、190537/1063887、10781274/5446238）：")
for X0, km in ((10 ** 4, 10 ** 5), (10 ** 6, 10 ** 5), (10 ** 8, 10 ** 6),
               (3 * 10 ** 9, 10 ** 6), (10 ** 10, 10 ** 6),
               (3 * 10 ** 10, 10 ** 6), (10 ** 11, 2 * 10 ** 6)):
    kp, C, w = window_criterion(X0, km, "pos")
    kn, _, _ = window_criterion(X0, km, "neg")
    say("  X0=%-12d  C=(3X0-1)ln2=%-16s 首个正侧未排除 K=%-10s 首个负侧未排除 K=%s"
        % (X0, nstr(C, 8), kp, kn))
kp, C, w = window_criterion(10 ** 12, 2 * 10 ** 7, "pos")
kn, _, _ = window_criterion(10 ** 12, 2 * 10 ** 7, "neg")
say("  X0=%-12d  C=(3X0-1)ln2=%-16s 首个正侧未排除 K=%-10s 首个负侧未排除 K=%s"
    % (10 ** 12, nstr(C, 8), kp, kn))

say("")
say("幸存者计数与「阶梯上界」的直接检验（X0 = 10^4，C = (3X0-1)ln2 = %s）：" % nstr((3 * mpf(10 ** 4) - 1) * log(mpf(2)), 10))
C4 = (3 * mpf(10 ** 4) - 1) * log(mpf(2))
N4 = 10 ** 6
cnt = 0
first = None
for K in range(1, N4 + 1):
    fr = mpf(K) * D50 - floor(mpf(K) * D50)
    if 1 - fr <= K / C4:
        cnt += 1
        if first is None:
            first = K
say("  K <= %d 的幸存者个数 = %d，首个幸存者 = %d，sqrt(N) = %d" % (N4, cnt, first, int(N4 ** 0.5)))
n0 = None
for n in range(1, 26, 2):
    if Q_CF[n] * Q_CF[n + 1] >= C4:
        n0 = n
        break
say("  首个满足 q_n q_{n+1} >= C 的奇数 n = %d（q_n = %d），故阶梯上界给 M+ < q_n = %d，"
    % (n0, Q_CF[n0], Q_CF[n0]))
say("  实测首个幸存者 %d <= q_n = %d？ %s（上界成立）" % (first, Q_CF[n0], first <= Q_CF[n0]))
say("")
say("恒等式抽查：正侧 1 - frac(m q_n delta) = m(p_n - q_n delta)（n 奇）；")
say("            负侧     frac(m q_n delta) = m(q_n delta - p_n)（n 偶，m e_n < 1）：")
for n in (9, 13, 15):
    qn, pn = Q_CF[n], P_CF[n]
    eps = pn - qn * delta80
    for m in (1, 7, 1000):
        if m * eps >= 1:
            continue
        K = m * qn
        fr = mpf(K) * D50 - floor(mpf(K) * D50)
        lhs = 1 - fr
        rhs = m * eps
        say("  正 n=%-3d m=%-6d  1-frac = %-22s  m eps = %-22s  相对差 = %s"
            % (n, m, nstr(lhs, 18), nstr(rhs, 18), nstr(abs(lhs - rhs) / rhs, 3)))
for n in (8, 10, 12, 14):
    qn, pn = Q_CF[n], P_CF[n]
    eps = qn * delta80 - pn
    for m in (1, 7, 1000):
        if m * eps >= 1:
            continue
        K = m * qn
        fr = mpf(K) * D50 - floor(mpf(K) * D50)
        say("  负 n=%-3d m=%-6d     frac = %-22s  m eps = %-22s  相对差 = %s"
            % (n, m, nstr(fr, 18), nstr(m * eps, 18), nstr(abs(fr - m * eps) / (m * eps), 3)))

say("")
say("N2（可达上界）：引理说 Kw >= 1（即 K >= C）时两侧都必不排除；直接扫描检验（两侧同时）：")
for X0 in (10 ** 4, 10 ** 5):
    C = (3 * mpf(X0) - 1) * log(mpf(2))
    Cint = int(floor(C)) + 1
    badp = badn = 0
    for K in range(Cint, Cint + 20000):
        fr = mpf(K) * D50 - floor(mpf(K) * D50)
        if 1 - fr > K / C:
            badp += 1
        if fr > K / C:
            badn += 1
    say("  X0=%-8d C=%-14s 对 K = C..C+20000 扫描，正侧被排除=%d 负侧被排除=%d（都应为 0）"
        % (X0, nstr(C, 10), badp, badn))
say("  另有精确逻辑证明：区间 (K(delta-1), K(delta-1)+Kw] 长度 Kw >= 1 时必含整数，")
say("  故 K >= (3X0-1)ln2 的 K 一律不被排除；这说明该判据的可达范围被常数 (3X0-1)ln2 卡住。")

say("")
say("N3（幸存者族）——第一版把负侧写成「奇数 n 的同型事实」，该说法为假，本轮已改正：")
say("  正侧引理：对奇数 n 与 1 <= m < 1/(p_n - q_n delta)，K = m q_n 是正侧幸存者；")
say("    q_n q_{n+1} >= C 时 m = 1..q_{n+1} 全部可行。")
say("  负侧引理（需要偶数 n）：对偶数 n 有 p_n - q_n delta < 0，令 e_n = |p_n - q_n delta|，")
say("    则 m e_n < 1 时 frac(m q_n delta) = m e_n，故负侧判据 frac(K delta) <= K/C 在 e_n <= q_n/C")
say("    时成立（同一条 q_n q_{n+1} >= C 前提）。奇数 n 在负侧恰好相反：frac(q_n delta) 接近 1。")
say("")
say("（0）反例与修正的直接核对：")
for X0, n in ((10 ** 4, 7), (10 ** 6, 9), (10 ** 8, 11)):
    C = (3 * mpf(X0) - 1) * log(mpf(2))
    K = Q_CF[n]
    fr = mpf(K) * D50 - floor(mpf(K) * D50)
    say("     反例：X0=%-10d 奇数 n=%-3d K=q_n=%-8d frac(K delta)=%-14s K/C=%-14s 负侧被排除=%s"
        % (X0, n, K, nstr(fr, 10), nstr(mpf(K) / C, 10), fr > K / C))
X0s = 10 ** 4
Cs = (3 * mpf(X0s) - 1) * log(mpf(2))
q7, q8, q9 = Q_CF[7], Q_CF[8], Q_CF[9]
bad = 0
for m in range(1, q8 + 1):
    K = m * q7
    fr = mpf(K) * D50 - floor(mpf(K) * D50)
    if fr > K / Cs:
        bad += 1
say("     反例计数：X0=10^4 时声称的 665 个 K = m*306 中，负侧被排除的个数 = %d（第一版声称 0）" % bad)
kntest, _, _ = window_criterion(X0s, 5000, "neg")
say("     矛盾位置：X0=10^4 实测首个负侧幸存者 = %s，故 M- = %d，而奇数 n 公式会预测 M- < q_7 = 306"
    % (kntest, kntest - 1))
say("     修正版（偶数 n=8，q_8 = %d）在 X0 = 10^4 上 m = 1..q_9 = %d 的负侧被排除数 = %d（应为 0）"
    % (q8, q9, sum(1 for m in range(1, q9 + 1)
                   if (mpf(m * q8) * D50 - floor(mpf(m * q8) * D50)) > mpf(m * q8) / Cs)))
for X0 in (10 ** 6, 10 ** 8):
    C = (3 * mpf(X0) - 1) * log(mpf(2))
    for n in (6, 8, 10, 12, 14, 16):
        if Q_CF[n] * Q_CF[n + 1] >= C:
            n0 = n
            break
    qn, qn1 = Q_CF[n0], Q_CF[n0 + 1]
    cnt = 0
    step = max(1, qn1 // 20000)
    for m in range(1, qn1 + 1, step):
        K = m * qn
        if (mpf(K) * D50 - floor(mpf(K) * D50)) > mpf(K) / C:
            cnt += 1
    kn2, _, _ = window_criterion(X0, 2 * 10 ** 6, "neg")
    say("     修正版：X0=%-12d 最小合格偶数 n=%d（q_n=%d）抽样 m 步长 %d 共 %d 个，负侧被排除=%d；"
        % (X0, n0, qn, step, (qn1 + step - 1) // step, cnt))
    say("             实测首个负侧幸存者 = %s <= q_n = %d？ %s（上界成立）" % (kn2, qn, kn2 <= qn))

say("")
say("（i）正侧全量核对（X0 = 10^4，首个合格奇数 n = 7，q_7 = 306，q_8 = 665）：")
bad = []
for m in range(1, q8 + 1):
    K = m * q7
    fr = mpf(K) * D50 - floor(mpf(K) * D50)
    if 1 - fr > K / Cs:
        bad.append((m, K))
say("     m = 1..%d 共 %d 个 K = m*306 中正侧被排除的个数 = %d（应为 0）" % (q8, q8, len(bad)))
cnt2 = 0
for K in range(1, q7 * q8 + 1):
    fr = mpf(K) * D50 - floor(mpf(K) * D50)
    if 1 - fr <= K / Cs:
        cnt2 += 1
say("     K <= q_7 q_8 = %d 内的正侧幸存者总数 = %d >= q_8 = %d >= sqrt(N) = %d"
    % (q7 * q8, cnt2, q8, int((q7 * q8) ** 0.5)))
say("（ii）正侧大档全量核对（反驳者做过、本轮复跑）：")
for X0, n in ((10 ** 6, 9), (10 ** 8, 11)):
    C = (3 * mpf(X0) - 1) * log(mpf(2))
    qn, qn1 = Q_CF[n], Q_CF[n + 1]
    cnt = 0
    for m in range(1, qn1 + 1):
        K = m * qn
        if (1 - (mpf(K) * D50 - floor(mpf(K) * D50))) > mpf(K) / C:
            cnt += 1
    say("     X0=%-12d n=%d（q_n=%d）: m = 1..%d 全量，正侧被排除 = %d（应为 0）"
        % (X0, n, qn, qn1, cnt))

say("")
say("「阶梯」预测的直接检验（两侧都做）：")
say("  正侧预测 = min{q_n : n 奇数且 (p_n - q_n delta) <= q_n/C}；")
say("  负侧预测 = min{q_n : n 偶数且 |p_n - q_n delta| <= q_n/C}；")
say("  两者都保证「不超过」（实测可以更小，因为半收敛项分母也能成为幸存者）。")
for X0, km, kmn in ((10 ** 4, 10 ** 5, 5000), (10 ** 6, 10 ** 5, 5000),
                    (10 ** 8, 10 ** 6, 5 * 10 ** 5), (10 ** 11, 2 * 10 ** 6, 2 * 10 ** 6),
                    (10 ** 12, 2 * 10 ** 7, 10 ** 7)):
    C = (3 * mpf(X0) - 1) * log(mpf(2))
    kp, _, _ = window_criterion(X0, km, "pos")
    kn, _, _ = window_criterion(X0, kmn, "neg")
    pred, predn = None, None
    for n in range(1, 26, 2):
        eps = P_CF[n] - Q_CF[n] * delta80
        if eps <= Q_CF[n] / C:
            pred = Q_CF[n]
            break
    for n in range(2, 26, 2):
        eps = Q_CF[n] * delta80 - P_CF[n]
        if eps <= Q_CF[n] / C:
            predn = Q_CF[n]
            break
    say("  X0=%-14d 正侧：实测 %-12s 预测 %-12s 上界成立=%s" % (X0, kp, pred, kp <= pred))
    say("                 负侧：实测 %-12s 预测 %-12s 上界成立=%s" % (kn, predn, kn <= predn))
say("  说明：小档实测更小是因为首个幸存者是半收敛项分母，例如：")
for K0 in (200, 2966):
    hit = []
    for j in range(2, 26):
        for a in range(1, A_CF[j + 1] + 1):
            if Q_CF[j - 1] + a * Q_CF[j] == K0:
                hit.append((j, a, A_CF[j + 1]))
    say("    K0=%-6d 表示为 q_{j-1} + a q_j 的方式（需 1 <= a <= a_{j+1}）：%s" % (K0, hit))
neb = []
for j in range(2, 26):
    for a in range(1, A_CF[j + 1] + 1):
        if Q_CF[j - 1] + a * Q_CF[j] == 16266:
            neb.append((j, a, A_CF[j + 1]))
say("    K0=%-6d（X0 = 10^8 的负侧首个幸存者）同样表示为 q_{j-1} + a q_j：%s" % (16266, neb))

# ----------------------------------------------------------------------
# D. 有理环候选
# ----------------------------------------------------------------------
say("")
say("=" * 72)
say("D. 有理环候选（N1）：所有长度 <= %d 的字" % KWORD)
say("=" * 72)


def word_candidate(bits):
    """bits: 0/1 列表（按步序）。返回 (c, K, k)。"""
    c = 0
    p = 0
    K = 0
    for b in bits:
        if b:
            c = 3 * c + (1 << p)
            K += 1
        p += 1
    return c, K, len(bits)


def parity(x):
    return x.numerator & 1


def Tmap(x):
    if x.numerator % 2 == 0:
        return x / 2
    return (3 * x + 1) / 2


bad_total = 0
bad_cycle = 0
tested = 0
worst = None
for k in range(1, KWORD + 1):
    for mask in range(1 << k):
        bits = [(mask >> i) & 1 for i in range(k)]
        c, K, kk = word_candidate(bits)
        D = (1 << k) - 3 ** K
        x = Fraction(c, D)
        y = x
        okv = True
        for i in range(k):
            if parity(y) != bits[i]:
                okv = False
                break
            y = Tmap(y)
        if not okv:
            bad_total += 1
        if y != x:
            bad_cycle += 1
        if not okv and worst is None:
            worst = (k, bits, c, K, D)
        tested += 1
say("检验了 %d 个字（长度 1 至 %d）：" % (tested, KWORD))
say("  奇偶向量与字不符的个数 = %d（应为 0）" % bad_total)
say("  T^k(x) != x 的个数 = %d（应为 0）" % bad_cycle)
say("  注：x 的分母为奇数，迭代保持在 Q_(2) = {a/b : b 为奇数} 内，奇偶性 = 分子奇偶。")
say("  另注：x 的整性即 (2^k - 3^K) | c，这是唯一未自动满足的条件。")

say("")
say("对固定族的整性检验（本族为非平凡 1 圈候选 K 与收敛项分母的对应）：")
for n in (3, 5, 7, 9, 11):
    K = Q_CF[n]
    N = P_CF[n]
    if K > 5000:
        say("  n=%d: q_n=%d 过大，跳过整数检验" % (n, K))
        continue
    three = 3 ** K
    L = N - K
    D = (1 << N) - three
    x = Fraction(three - (1 << K), D)
    say("  n=%d: K=q_n=%d, N=p_n=%d, L=%d, x=%s 是整数？ %s"
        % (n, K, N, L, nstr(mp.mpf(x.numerator) / x.denominator, 10), x.denominator == 1))

# ----------------------------------------------------------------------
# E. 最大元定向前缀引理与 c_max
# ----------------------------------------------------------------------
say("")
say("=" * 72)
say("E. 最大元定向前缀引理与 c_max 公式（已知环核对）")
say("=" * 72)


def accelerate_orbit(x0):
    """返回加速映射下从 x0 出发的环（元素列表），x0 必须在环上。"""
    seq = [x0]
    y = Tmap(Fraction(x0))
    while y != x0:
        seq.append(y)
        y = Tmap(y)
    return seq


known = [
    ("{1,2}", [1, 2]),
    ("{-1}", [-1]),
    ("{-5,-7,-10}", [-5, -7, -10]),
    ("{-17 族}", [-17, -25, -37, -55, -82, -41, -61, -91, -136, -68, -34]),
]
say("")
say("引理（统一陈述）：把环旋到最大元（通常序下最大的元素）后，每个前缀 (p, q_p) 满足")
say("  2^p > 3^(q_p)（正环）或 2^p < 3^(q_p)（负环）；证明见 attempt.md 第 12 步")
say("  （x_p <= x_0 给 c_p <= (2^p - 3^(q_p)) x_0，c_p > 0 定出括号的正负）。")
for name, elems in known:
    x0 = max(elems)
    want = "gt" if all(e > 0 for e in elems) else "lt"
    seq = accelerate_orbit(x0)
    if seq[0] != x0:
        continue
    bad = []
    p = 0
    q = 0
    y = Fraction(x0)
    for _ in range(len(seq)):
        if parity(y):
            q += 1
        p += 1
        if want == "gt" and not ((1 << p) > 3 ** q):
            bad.append((p, q))
        if want == "lt" and not ((1 << p) < 3 ** q):
            bad.append((p, q))
        y = Tmap(y)
    say("  %-14s 起点 x0=%-5d 周期 k=%-3d K=%-2d  违反前缀条件的个数=%d"
        % (name, x0, len(seq), q, len(bad)))

say("")
say("c_max 公式核对（对字的旋转起点为奇数步）：c_max = 3^(K-1)(2^(k-K+1)+1) - 2^k。")


def c_max_formula(k, K):
    return 3 ** (K - 1) * ((1 << (k - K + 1)) + 1) - (1 << k)


check = [("{1,2}", "10", 1), ("{-1}", "1", 1), ("{-5,-7,-10}", "110", 5),
         ("{-17 族}", "11110111000", 2363)]
for name, word, cval in check:
    k = len(word)
    K = word.count("1")
    cm = c_max_formula(k, K)
    # 穷举所有同 (k, K) 的字，验证 c <= c_max
    mx = 0
    for mask in range(1 << k):
        bits = [(mask >> i) & 1 for i in range(k)]
        if bits[0] != 1 or sum(bits) != K:
            continue
        c, _, _ = word_candidate(bits)
        mx = max(mx, c)
    say("  %-14s 字=%s c=%-8d c_max(公式)=%-10d 同 (k,K) 全部字的最大 c=%-10d 一致=%s"
        % (name, word, cval, cm, mx, cm == mx))

# ----------------------------------------------------------------------
# F. 桥接交叉核对
# ----------------------------------------------------------------------
say("")
say("=" * 72)
say("F. 与既有记录值的交叉核对（K 门槛到周期下界）")
say("=" * 72)
mp.dps = 80
q23 = 137528045312
say("  ceil(delta * q_23)        = %d（记录值 217976794617）"
    % int(floor(delta80 * q23) + 1))
say("  ceil((1 + delta) * q_23)  = %d（记录值 355504839929）"
    % int(floor((1 + delta80) * q23) + 1))
say("  恒等式 ceil(K delta) = bit_length(3^K) 的精确检验（对 K = 1..2000）：")
ok_bl = True
for K in range(1, 2001):
    N = (3 ** K).bit_length()
    if not ((1 << (N - 1)) <= 3 ** K < (1 << N)):
        ok_bl = False
say("    2^(N-1) <= 3^K < 2^N 全部成立？ %s（由 log2 单调，这等价于 N = ceil(K delta)）" % ok_bl)

with open("results/arithmetic_cycles_round2.txt", "w") as f:
    f.write("\n".join(OUT) + "\n")
say("")
say("输出已写入 results/arithmetic_cycles_round2.txt（%d 行）" % len(OUT))
