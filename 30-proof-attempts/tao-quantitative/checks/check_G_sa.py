#!/usr/bin/env python3
"""check_G_sa.py

对「边界因子」的经典预言做数值检验（Sparre Andersen 型恒等式）。

设 Z_k = S_k - k p（S_k 为前 k 位 1 的个数，p = log_3 2），倾斜测度下 Z 是零均值随机游走
（步长 +q 概率 p、-p 概率 q），且 Z_k 永不取 0（因 0 ∉ Z - kp）。记
    u_n = P_tilt(Z_i > 0, 1 <= i <= n)  = Q(E_n)（可容许概率）。

经典（Sparre Andersen）恒等式的形式为
    sum_{n>=0} u_n s^n = exp( sum_{k>=1} (s^k / k) P(Z_k > 0) )，
其推论是 u_n ~ C_S * C(2n,2n/…) 型系数，即 u_n ~ C_S / sqrt(pi n)，
    C_S := exp( sum_{k>=1} (1/k) (P(Z_k > 0) - 1/2) )。

本程序：
 1. 用带状动态规划计算 P(Z_k > 0) = P(Bin(k,p) >= ceil(kp))，k <= K；
 2. 累加得 C_S（尾部用拟合外推），并与 0.66744 * sqrt(pi) 比较；
 3. 打印若干 P(Z_k > 0) 的抽样值。
这是数值检验，不是证明；恒等式本身本会话未核对原始文献。

用法：python3 check_G_sa.py [K]
默认 K = 200000。
"""

import math
import sys

P = math.log(2.0) / math.log(3.0)
Q = 1.0 - P


def survival_series(K):
    """返回 S_k = P(Bin(k,p) >= ceil(k p))，k = 1..K（浮点，带状 DP）。

    递推：P(Bin(k,p) >= j) = q * P(Bin(k-1,p) >= j) + p * P(Bin(k-1,p) >= j-1)。
    带宽度取 30*sqrt(k)+60；带外的值按 1（阈值下方）或 0（阈值上方）处理，
    误差量级为亚高斯尾部，远小于本程序的报告精度。
    """
    out = [0.0] * (K + 1)
    V = [1.0]          # 第 k-1 行的带内值：V[j - lo_prev]
    lo_prev, hi_prev = 0, 0
    for k in range(1, K + 1):
        thr = math.ceil(k * P)
        B = int(30 * math.sqrt(k)) + 60
        lo = max(0, thr - B)
        hi = min(k + 1, thr + B)
        nV = [0.0] * (hi - lo + 1)
        for j in range(lo, hi + 1):
            tot = 0.0
            for jj, wgt in ((j, Q), (j - 1, P)):
                if jj <= 0:
                    a = 1.0
                elif jj > k - 1:
                    a = 0.0
                elif lo_prev <= jj <= hi_prev:
                    a = V[jj - lo_prev]
                elif jj < lo_prev:
                    a = 1.0
                else:
                    a = 0.0
                tot += wgt * a
            nV[j - lo] = tot
        V, lo_prev, hi_prev = nV, lo, hi
        if 1 <= thr <= k:
            out[k] = V[thr - lo]
        else:
            out[k] = 1.0 if thr <= 0 else 0.0
    return out


def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
    print("check_G_sa: K = %d, p = %.15f, q = %.15f" % (K, P, Q))
    S = survival_series(K)
    print("抽样 P(Z_k > 0)：")
    for k in (1, 2, 5, 10, 100, 1000, 10000, 100000):
        if k <= K:
            print("   k = %6d   P = %.12f   P - 1/2 = %+.3e" % (k, S[k], S[k] - 0.5))
    # 拟合尾部形态：P - 1/2 ~ A k^{-1/2} + B k^{-3/2}
    tot = 0.0
    for k in range(1, K + 1):
        tot += (S[k] - 0.5) / k
    # 尾部估计：把 (S_k - 1/2) * sqrt(k) 视作缓慢变化，用最后一段的平均值外推
    tail_est = 0.0
    w = 2000
    if K > w:
        avg = 0.0
        cnt = 0
        for k in range(K - w + 1, K + 1):
            if k >= 1:
                avg += (S[k] - 0.5) * math.sqrt(k)
                cnt += 1
        avg /= cnt
        # sum_{k>K} A k^{-3/2} ≈ 2 A / sqrt(K)
        tail_est = 2.0 * avg / math.sqrt(K)
    CS = math.exp(tot + tail_est)
    print("")
    print("累加至 K 的部分和 = %.12f" % tot)
    print("尾部估计（2A/sqrt(K)，A = 尾段平均 (P-1/2)sqrt(k)）= %.3e" % tail_est)
    print("C_S = exp(部分和 + 尾部) = %.10f" % CS)
    print("预言 u_n ~ C_S / sqrt(pi n)，即 u_n * sqrt(n) -> C_S/sqrt(pi) = %.10f"
          % (CS / math.sqrt(math.pi)))
    print("check_D_tilt 实测 u_m*sqrt(m) ≈ 0.66744（m 从 250 到 30000，波动 ±0.0002）")
    print("差值 = %+.5f （相对 %.3f%%）"
          % (CS / math.sqrt(math.pi) - 0.66744, 100 * (CS / math.sqrt(math.pi) / 0.66744 - 1)))


if __name__ == "__main__":
    main()
