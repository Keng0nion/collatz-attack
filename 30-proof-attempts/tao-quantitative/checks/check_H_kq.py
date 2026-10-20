#!/usr/bin/env python3
"""check_H_kq.py

测量一条「可能通往 m^{-1/2}」的初等路线是否成立：

  想法：若每个串都满足 R(s) <= C + K_+(s)/q（K_+ = max(K,0)），
  则由 E_tilt[K_+] <= sqrt(m p q)（Cauchy-Schwarz，K 为零均值 m 步随机游走）
  立即得到 E_tilt[R] <= C + sqrt(m p / q)，从而 Q(E_m) = E_tilt[R]/m = O(m^{-1/2})。

本程序（浮点实现，仅用于测量）：
 1. 全枚举 m <= 22：报告 max_s (R - K_+/q) 的增长（检验「每串」版本）；
 2. 倾斜测度抽样（每位取 1 概率 p）：报告 E[R]、E[K_+]/q、E[(R - K_+/q)_+]、max(R - K_+/q)
    （检验「平均」版本）。

注意：浮点比较在极接近的 P 值上理论上可能出错；本程序的 P_i 值间距
（同一起点的两个不同部分和之差至少为 eta(m) 量级，m <= 2000 时约 1e-5）
远大于 float64 的分辨率，故用于测量是安全的；但这不是一个严格的证明工具。

用法：python3 check_H_kq.py [MMAX_EXH] [NS] [MS...]
默认 MMAX_EXH = 22，NS = 20000，MS = 64 256 1024。
"""

import math
import random
import sys

P = math.log(2.0) / math.log(3.0)
Q = 1.0 - P


def R_and_K(eps):
    m = len(eps)
    xi = [Q if b else -P for b in eps]
    Pm = [0.0] * (2 * m + 1)
    for i in range(1, 2 * m + 1):
        Pm[i] = Pm[i - 1] + xi[(i - 1) % m]
    K = Pm[m]
    # 滑动窗口最小：窗口 [j+1, j+m]
    from collections import deque
    dq = deque()
    for i in range(1, m + 1):
        while dq and Pm[dq[-1]] >= Pm[i]:
            dq.pop()
        dq.append(i)
    R = 0
    for j in range(0, m):
        while dq and dq[0] <= j:
            dq.popleft()
        if Pm[j] < Pm[dq[0]]:
            R += 1
        if j + m + 1 <= 2 * m:
            i = j + m + 1
            while dq and Pm[dq[-1]] >= Pm[i]:
                dq.pop()
            dq.append(i)
    return R, K


def main():
    MMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 22
    NS = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    MS = [int(x) for x in sys.argv[3:]] or [64, 256, 1024]

    print("check_H_kq: 浮点测量，仅供定位路线，不是证明")
    print("p = %.15f  q = %.15f" % (P, Q))
    print("")
    print("=== 全枚举：max_s (R - K_+/q)（检验每串版本 R <= C + K_+/q） ===")
    print("   m     max(R - K_+/q)   增量/3     argmax 的 (R, K)")
    prev = None
    for m in range(2, MMAX + 1):
        best = None
        for mask in range(1 << m):
            eps = [(mask >> (m - 1 - i)) & 1 for i in range(m)]
            R, K = R_and_K(eps)
            gap = R - (K / Q if K > 0 else 0.0)
            if best is None or gap > best[0]:
                best = (gap, R, K)
        inc = "" if prev is None else "  %+.5f" % (best[0] - prev)
        print("%4d  %14.5f  %8s   R=%d K=%+.4f" % (m, best[0], inc, best[1], best[2]))
        prev = best[0]

    print("")
    print("=== 倾斜测度抽样（NS = %d）===" % NS)
    print("   m     E[R]        E[R]/sqrt(m)   E[K+]/q      E[(R-K+/q)+]  该量/sqrt(m)   max(R-K+/q)")
    rng = random.Random(20261020)   # 明文说明：刻意用带种子的 PRNG（数学蒙特卡洛，需可复现；非密码学用途）
    for m in MS:
        totR = 0.0
        totK = 0.0
        totPos = 0.0
        mx = None
        for _ in range(NS):
            eps = [1 if rng.random() < P else 0 for _ in range(m)]
            R, K = R_and_K(eps)
            Kp = K if K > 0 else 0.0
            totR += R
            totK += Kp / Q
            gap = R - Kp / Q
            if gap > 0:
                totPos += gap
            if mx is None or gap > mx:
                mx = gap
        ER = totR / NS
        EK = totK / NS
        EP = totPos / NS
        print("%5d  %10.4f  %12.6f  %12.4f  %12.4f  %12.6f  %12.4f"
              % (m, ER, ER / math.sqrt(m), EK, EP, EP / math.sqrt(m), mx))
    print("")
    print("对照：E[K_+]/q 的理论上界 sqrt(m p q)/q = %.6f * sqrt(m)" % math.sqrt(P / Q))
    print("对照：E[R] 的实测常数约 0.667（见 check_D_tilt），即 E[R] ≈ 0.667 sqrt(m)")


if __name__ == "__main__":
    main()
