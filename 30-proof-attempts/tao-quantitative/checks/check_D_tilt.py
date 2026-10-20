#!/usr/bin/env python3
"""check_D_tilt.py

检验本路线新引理 D1（倾斜恒等式）与它对「损耗因子」的定量刻画。

记号（与 attempt.md 一致）：
  p = log_3 2，q = 1 - p，D = ln2 - H(p)（H 为二元熵，nat）。
  长度 m 的 0/1 串 eps，「可容许」= 对一切 1 <= i <= m 有 3^{S_i} >= 2^i，
  其中 S_i 为前 i 位的 1 的个数（1 = 奇步）。
  A(m) = 可容许串数；N(m, S) = 其中恰有 S 个 1 的串数。
  F(k) = A(k-1) / 2^{k-1}（Terras 停时密度）。
  倾斜测度 P_tilt：每一位取 1 的概率 p，取 0 的概率 q；Q(E_m) = P_tilt(可容许)。
  Z_m = S_m - m p。

断言（本程序逐点核对）：
 (D1a) F(k) = A(m)/2^m 与 A(m) = sum_S N(m,S) 的定义一致性；
 (D1b) 倾斜恒等式（精确）：
         A(m)/2^m = exp(-m D) * sum_S N(m,S) p^S q^{m-S} exp(- (S - m p) ln(p/q) )
      且右侧的 sum_S N(m,S) p^S q^{m-S} exp(-(S-mp)ln(p/q)) = exp(-m H(p)) * A(m)
      （与 S 无关的因子——这是恒等式的全部内容）；
 (D1c) 分解 F(k) = exp(-(k-1) D) * Q(E_m) * E_tilt[e^{-c Z_m} | 可容许]，c = ln(p/q)；
      据此报告损耗因子 E_tilt[e^{-cZ}|adm] 的衰减（启发式预测 ~ Const/m）；
 (D1d) 报告 E_tilt[Z_m | 可容许]（「夹道」启发式预测 ~ Const*sqrt(m)）；
 (D1e) 报告 F(k) 的有效幂指数 alpha（拟合 log F + D m 对 log m 的斜率）。

用法：python3 check_D_tilt.py [MMAX] [STEP]
默认 MMAX = 3000，STEP = 100。
"""

import sys
from mpmath import mp, mpf, log, exp

mp.dps = 60

p = log(mpf(2)) / log(mpf(3))
q = 1 - p
Hp = -(p * log(p) + q * log(q))
D = log(mpf(2)) - Hp
c = log(p / q)


def s_min(i):
    """最小的 S 使 3^S >= 2^i（精确整数比较）。"""
    S = 0
    # 起点用浮点估计，再用精确整数比较修正
    est = int(i * float(log(mpf(2)) / log(mpf(3))))
    S = max(0, est - 2)
    while 3 ** S < 2 ** i:
        S += 1
    return S


def main():
    MMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    STEP = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    print("check_D_tilt: MMAX = %d, STEP = %d" % (MMAX, STEP))
    print("p = %s" % mp.nstr(p, 30))
    print("q = %s" % mp.nstr(q, 30))
    print("H(p) = %s" % mp.nstr(Hp, 30))
    print("D = ln2 - H(p) = %s   exp(-D) = %s" % (mp.nstr(D, 30), mp.nstr(exp(-D), 30)))
    print("c = ln(p/q) = %s" % mp.nstr(c, 30))
    print("")

    # dp[S] = 长度 i 的可容许串中恰有 S 个 1 的个数（精确整数）
    dp = [1]  # i = 0, S = 0
    rows = {}
    # 预计算 p^S q^{m-S} 需要按 m 计算，这里逐 m 处理
    header = ("     m   log2A(m)  resid=lnF+mD  F(k)         "
              "Q(E_m)     Q*sqrt(m)  E[e^-cZ|adm]  *m       E[Z|adm]/sqrt(m)  alpha_eff")
    print(header)
    prev = None
    for i in range(1, MMAX + 1):
        smin = s_min(i)
        newdp = [0] * (i + 1)
        # 末位取 1：S -> S+1，要求 S+1 >= smin
        for S in range(0, i):
            v = dp[S]
            if v:
                if S + 1 >= smin:
                    newdp[S + 1] += v
                if S >= smin:
                    newdp[S] += v
        dp = newdp
        if i % STEP == 0 or i == MMAX:
            A = sum(dp)
            m = i
            # F = A/2^m，用 mpmath 高精度
            lnA = log(mpf(A))
            lnF = lnA - m * log(mpf(2))
            F = exp(lnF)
            resid = lnF + m * D          # 残差：F ~ exp(-mD) * m^(-alpha) 时 resid ~ -alpha log m
            # 倾斜量
            Q = mpf(0)
            Zbar = mpf(0)
            W = mpf(0)  # sum N p^S q^{m-S} exp(-c(S-mp))
            for S in range(0, m + 1):
                v = dp[S]
                if not v:
                    continue
                w = mpf(v) * p ** S * q ** (m - S)
                Q += w
                Zbar += w * (S - m * p)
                W += w * exp(-c * (S - m * p))
            Zbar = Zbar / Q
            Rm = W / Q          # = E_tilt[e^{-cZ} | adm]
            rows[m] = (F, Q, Rm, Zbar)
            # 恒等式核对：W 应当等于 exp(-m H(p)) * A(m)
            Wpred = exp(-m * Hp) * mpf(A)
            rel = abs(W - Wpred) / Wpred
            # 分解式核对：F = exp(-mD) Q Rm
            Fpred = exp(-m * D) * Q * Rm
            relF = abs(F - Fpred) / F
            alpha = "        --"
            if prev is not None:
                r0, m0 = prev
                a = -(resid - r0) / (log(mpf(m)) - log(mpf(m0)))
                alpha = "%10.4f" % float(a)
            prev = (resid, m)
            print("%6d  %8.3f  %12.6f  %12.6e  %10.5e  %8.6f  %12.6e  %9.4f  %14.4f  %s"
                  % (m, float(lnA) / float(log(mpf(2))), float(resid),
                     float(F), float(Q), float(Q) * (m ** 0.5),
                     float(Rm), float(Rm) * m, float(Zbar) / (m ** 0.5), alpha))
            # g(m) := ln F + m D + 1.5 ln m；若 F = C exp(-mD) m^{-3/2} 则 g = ln C 为常数
            g = resid + mpf(1.5) * log(mpf(m))
            print("        [猜想的锐形式] g(m) = lnF + mD + 1.5 ln m = %s   （常数则为 C = %s）"
                  % (mp.nstr(g, 10), mp.nstr(exp(g), 10)))
            print("        [恒等式核对] |W - exp(-mH)A| / 值 = %.3e   |F - exp(-mD)Q R| / F = %.3e"
                  % (float(rel), float(relF)))

    print("")
    print("说明：alpha 为相邻两档之间 -(Delta log F)/(Delta log m) 的读数，")
    print("它不含 m D 项（因为 log F 已含 -mD），故 alpha 直接给出幂次指数。")
    print("m=            F 的有效形式近似 exp(-mD) * C * m^(-alpha)。")


if __name__ == "__main__":
    main()
