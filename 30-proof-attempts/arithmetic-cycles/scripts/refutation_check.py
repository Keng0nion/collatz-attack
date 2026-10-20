#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反驳意见的现场复核（本文件由路线探索者·arithmetic-cycles 在收到反驳后新建）。

内容：
  1. C_m 与 C_m^{-1}：确认「|x_min| > C_m 2^{K/S}」把常数写反（正确版是 C_m^{-1}）。
  2. C_m > 1 的角落（X0 小、m 小的范围）。
  3. T2b 在已知环上的检验：先查前提（环上所有元素绝对值 >= X0），再查修正版与印出版；
     印出版在 {−5,−7,−10}（X0 = 2）上给出反例。
  4. T2a 构造复核：X0 = 1e6 与 1e12 各取一个收敛项，核对 P/K − δ <= w。

运行：
  cd 30-proof-attempts/arithmetic-cycles
  /Users/luna/Documents/math\\ IA/collatz-attack/20-experiments/.venv/bin/python scripts/refutation_check.py
"""
from mpmath import mp, mpf, log, floor, fabs

mp.dps = 120
DELTA = log(mpf(3)) / log(mpf(2))
LOG2 = log(mpf(2))


def chain_T(m):
    if m == 1:
        return mpf(0)
    return ((DELTA ** m - DELTA) / (DELTA - 1) - (m - 1)) / (DELTA - 1)


def Cm(m, X0):
    B = (1 + 1 / X0) ** DELTA / 2
    return ((1 + 1 / X0) ** m * B ** chain_T(m)) ** ((DELTA - 1) / (DELTA ** m - 1))


S_of = lambda m: (DELTA ** m - 1) / (DELTA - 1)

print("=" * 78)
print("1. C_m 与 C_m^{-1}（反驳意见一：常数写反）")
print("=" * 78)
for X0 in ["3.7469e18", "100", "5", "3", "2"]:
    print("   X0=%-11s" % X0,
          "  ".join("m=%d C=%.8f" % (m, Cm(m, mpf(X0))) for m in [1, 2, 3, 6, 7]))
c68 = Cm(68, mpf("3.7469e18"))
print("   m=68, X0=3.25*2^60:  C_68 =", mp.nstr(c68, 10), "  C_68^{-1} =", mp.nstr(1 / c68, 10))
print("   C_2(X0=3.25*2^60) =", mp.nstr(Cm(2, mpf("3.7469e18")), 8),
      "（Simons 与 de Weger v1.43 第 8 页给 c_2 = 0.76479 与 c_m -> 0.30576）")
print("   结论：C_m 就是 SW 的 c_m（Lambda 侧系数），故 x_min > c_m^{-1}2^{K/S}；")
print("        attempt.md 原第 6 步/第 11 步/T2b 印成 C_m 2^{K/S}，把常数写反。")

print()
print("=" * 78)
print("2. C_m > 1 的角落（印出版在该处强于可证结论）")
print("=" * 78)
for X0 in ["2", "3", "5", "10"]:
    bad = [m for m in range(1, 40) if Cm(m, mpf(X0)) > 1]
    print("   X0=%-4s 使 C_m > 1 的 m：%s" % (X0, bad))

print()
print("=" * 78)
print("3. T2b 在已知环上的检验（先查前提：环上所有元素绝对值 >= X0）")
print("=" * 78)
cycles = [("U 环 {1}（负环 {−1}）", 1, 1, 1),
          ("U 环 {5,7,10}（负环 {−5,−7,−10}）", 1, 2, 5),
          ("U 环 {17,…,34}（负环 {−17 族}）", 2, 7, 17)]
viol = []
for name, m, K, nmin in cycles:
    for X0 in ["2", "3", "5", "10", "17", "100"]:
        X0v = mpf(X0)
        if nmin < X0v:
            print("   %-34s X0=%-5s 前提不成立（|x_min|=%d < X0），跳过" % (name, X0, nmin))
            continue
        c = Cm(m, X0v)
        pw = 2 ** (K / S_of(m))
        corr, wrong = (1 / c) * pw, c * pw
        okc, okw = nmin > corr, nmin > wrong
        print("   %-34s X0=%-5s 修正版阈值 %-14s 满足=%-5s | 印出版阈值 %-14s 满足=%s"
              % (name, X0, mp.nstr(corr, 8), okc, mp.nstr(wrong, 8), okw))
        if not okw:
            viol.append((name, X0, nmin, mp.nstr(wrong, 8)))
        if not okc:
            viol.append(("修正版也应成立却失败", name, X0, mp.nstr(corr, 8)))
print("   印出版的反例：", [v for v in viol if v[0] != "修正版也应成立却失败"])
print("   修正版的反例：", [v for v in viol if v[0] == "修正版也应成立却失败"])

print()
print("=" * 78)
print("4. T2a 构造复核：取收敛项 K = q_n、P = p_n，核 P/K − delta <= w")
print("=" * 78)
from mpmath import exp


def cf(x, nmax):
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


A_CF, P_CF, Q_CF = cf(DELTA, 40)
for X0 in [10 ** 6, 10 ** 12]:
    X0v = mpf(X0)
    w = 1 / ((3 * X0v - 1) * LOG2)
    C = (3 * X0v - 1) * LOG2
    n = None
    for i in range(0, len(Q_CF) - 1):
        if i % 2 == 1 and mpf(Q_CF[i]) * mpf(Q_CF[i + 1]) >= C:
            n = i
            break
    K, P = Q_CF[n], P_CF[n]
    gap = mpf(P) / mpf(K) - DELTA
    print("   X0=%-12s 取 n=%-3d K=q_%d=%-12d  P/K − delta = %-14s <= w = %-12s  %s"
          % (X0, n, n, K, mp.nstr(gap, 8), mp.nstr(w, 8), gap <= w))
print("   即：这些 K 满足窗口必要条件而未被排除，且 K 随 X0 增大（收尾不可能性 T2a）。")
