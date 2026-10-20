#!/usr/bin/env python3
"""check_E_rotation.py  （修订版：O(m) 计算 R，并加入关键比值测量）

本文件检验本路线的新引理 E1 至 E4，并测量一个决定性问题：
    R(s) 是否被 K(s) 控制（例如 R <= 1 + K_+/q）？

记号：串 eps ∈ {0,1}^m，增量 xi_j = +q（eps_j = 1，奇步）或 -p（eps_j = 0，偶步），
p = log_3 2，q = 1 - p。部分和 P_0 = 0，P_i = xi_1 + ... + xi_i = S_i - i p，K = P_m。
「好位置」j ∈ {0,...,m-1}：P_j < P_i 对一切 i ∈ (j, j+m]（下标按周期 m 读，
P_{i+m} = P_i + K）。R(s) = 好位置个数。

断言（逐点核对）：
 (E1) 好位置 ⟺ 该轮换是「可容许串」；于是 E[R] = m u_m，其中 u_m 为可容许概率，
      在等权（每串 1/2^m）与倾斜（每位 1 概率 p）两种测度下分别核对。
 (E2) K < 0 ⟹ R = 0；K > 0 ⟹ R >= 1。
 (E3) 好位置把环切成 R 个连续块，块长 d_t，块内 0 的个数 Z_t，块和 e_t = d_t q - Z_t > 0，
      且 sum_t e_t = K（精确）、sum_t d_t = m（精确）。
 (E4) e_t >= eta(d_t) >= eta(m)（eta 见 check_F_cf.py），故 (R-1)*eta(m) < K，更精细地
      K >= sum_t eta(d_t) >= c R^2 / m（若 eta(d) >= c/d），从而 R <= sqrt(K_+ m / c)。
 (关键测量) max over strings of (R - K_+ / q) 随 m 的增长行为；若它被常数控制，
      则 E[R] <= 常数 + E[K_+]/q <= 常数 + sqrt(m p / q)，直接给出 u_m = O(m^{-1/2})。

用法：python3 check_E_rotation.py [MMAX] [NS_TILT] [NS_UNIF]
默认 MMAX = 20，NS_TILT = 4000，NS_UNIF = 4000（用于 m = 64, 128, 256, 512, 1024）。
"""

import random
import sys
from collections import deque
from mpmath import mp, mpf, log, nstr

mp.dps = 30

p_mp = log(mpf(2)) / log(mpf(3))
q_mp = 1 - p_mp


def eta_upto(m):
    """eta(m) = min_{1<=d<=m}|dq - l|（高精度扫描）。"""
    best = None
    for d in range(1, m + 1):
        x = d * q_mp
        r = abs(x - round(x))
        if best is None or r < best:
            best = r
    return best


def R_of(eps):
    """O(m) 计算 R（滑动窗口最小值）。"""
    m = len(eps)
    xi = [q_mp if b else -p_mp for b in eps]
    P = [mpf(0)] * (2 * m + 1)
    for i in range(1, 2 * m + 1):
        P[i] = P[i - 1] + xi[(i - 1) % m]
    # 对每个 j ∈ [0, m)，需要 min P[j+1 .. j+m]
    R = 0
    dq = deque()
    # 先填窗口 j=0: 索引 1..m
    for i in range(1, m + 1):
        while dq and P[dq[-1]] >= P[i]:
            dq.pop()
        dq.append(i)
    for j in range(0, m):
        # 窗口 [j+1, j+m] 的最小值
        while dq and dq[0] <= j:
            dq.popleft()
        mn = P[dq[0]]
        if P[j] < mn:
            R += 1
        # 推进窗口到 j+1: 加入 j+m+1
        if j + m + 1 <= 2 * m:
            i = j + m + 1
            while dq and P[dq[-1]] >= P[i]:
                dq.pop()
            dq.append(i)
    return R


def blocks_of(eps, good):
    m = len(eps)
    xi = [q_mp if b else -p_mp for b in eps]
    P = [mpf(0)] * (2 * m + 1)
    for i in range(1, 2 * m + 1):
        P[i] = P[i - 1] + xi[(i - 1) % m]
    out = []
    R = len(good)
    for t in range(R):
        j = good[t]
        jn = good[(t + 1) % R] if R > 1 else j + m
        k = jn if jn > j else jn + m
        d = k - j
        Z = sum(1 for idx in range(j, k) if not eps[idx % m])
        e = P[k] - P[j]
        out.append((d, Z, e))
    return out


def admissible(eps):
    S = 0
    for i, b in enumerate(eps, start=1):
        S += b
        if 3 ** S < 2 ** i:
            return False
    return True


def main():
    MMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    NS_T = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
    NS_U = int(sys.argv[3]) if len(sys.argv) > 3 else 4000

    print("check_E_rotation（修订版）")
    print("p = %s   q = %s" % (nstr(p_mp, 20), nstr(q_mp, 20)))
    print("")
    print("=== 全枚举 m <= %d ===" % MMAX)
    print("  m   E[R]（等权）  m*u_m（等权）  E_tilt[R]    m*Q(E_m)（倾斜）  违例"
          "(K<0&R>0)  违例(E3 sum e=K)  违例(E4 (R-1)eta<K)  max(R - K_+/q)")
    for m in range(2, MMAX + 1):
        totR = 0
        totRt = mpf(0)
        ws = mpf(0)
        Qu = mpf(0)
        Qt = mpf(0)
        vK = vE3 = vE4 = 0
        eta = eta_upto(m)
        maxgap = None
        for mask in range(1 << m):
            eps = [(mask >> (m - 1 - i)) & 1 for i in range(m)]
            R = R_of(eps)
            K = mpf(m * 0)  # placeholder
            S = sum(eps)
            K = q_mp * S - p_mp * (m - S)
            totR += R
            wt = (p_mp ** S) * (q_mp ** (m - S))
            totRt += wt * R
            ws += wt
            if K < 0 and R > 0:
                vK += 1
            # 好位置列表（暴力，小 m 可用）
            P = [mpf(0)] * (2 * m + 1)
            xi = [q_mp if b else -p_mp for b in eps]
            for i in range(1, 2 * m + 1):
                P[i] = P[i - 1] + xi[(i - 1) % m]
            good = [j for j in range(m) if all(P[j] < P[i] for i in range(j + 1, j + m + 1))]
            if len(good) != R:
                print("      [R 计算不一致]")
            if R > 0:
                bl = blocks_of(eps, good)
                se = sum(e for (_, _, e) in bl)
                sd = sum(d for (d, _, _) in bl)
                if abs(se - K) > mpf('1e-20') or sd != m:
                    vE3 += 1
                if R >= 2 and (R - 1) * eta >= K:
                    vE4 += 1
            if admissible(eps):
                Qu += mpf(1) / (1 << m)
                Qt += wt
            gap = R - (K / q_mp if K > 0 else mpf(0))
            if maxgap is None or gap > maxgap:
                maxgap = gap
                argmax = eps
        Eu = mpf(totR) / (1 << m)
        Et = totRt / ws
        print("%4d  %11.6f  %11.6f  %11.6f  %12.6f  %8d  %8d  %8d  %14.5f"
              % (m, float(Eu), float(m * Qu), float(Et), float(m * Qt), vK, vE3, vE4,
                 float(maxgap)))
        if abs(float(Eu) - float(m * Qu)) > 1e-12:
            print("      [E1 等权核对失败] E[R] = %s, m*u_m = %s" % (nstr(Eu, 12), nstr(m * Qu, 12)))
        if abs(float(Et) - float(m * Qt)) > 1e-12:
            print("      [E1 倾斜核对失败] E_tilt[R] = %s, m*Q = %s" % (nstr(Et, 12), nstr(m * Qt, 12)))

    print("")
    print("=== 随机抽样（倾斜测度与等权测度各 %d 个样本） ===" % NS_T)
    print("   m   NS   E_tilt[R]/sqrt(m)  max R   max(R-K_+/q)   [等权] E[R]/sqrt(m)  max R")
    rng = random.Random(20261020)   # 明文说明：此处刻意用带种子的 PRNG（数学蒙特卡洛实验，需可复现；非密码学用途）
    for m in (64, 128, 256, 512, 1024):
        totR = 0
        maxR = 0
        maxgap = None
        for _ in range(NS_T):
            eps = [1 if rng.random() < float(p_mp) else 0 for _ in range(m)]
            R = R_of(eps)
            S = sum(eps)
            K = q_mp * S - p_mp * (m - S)
            totR += R
            if R > maxR:
                maxR = R
            gap = R - (K / q_mp if K > 0 else mpf(0))
            if maxgap is None or gap > maxgap:
                maxgap = gap
        Eu = mpf(totR) / NS_T
        totR2 = 0
        maxR2 = 0
        for _ in range(NS_U):
            eps = [rng.randint(0, 1) for _ in range(m)]
            R = R_of(eps)
            totR2 += R
            if R > maxR2:
                maxR2 = R
        Eu2 = mpf(totR2) / NS_U
        print("%5d  %5d  %16.6f  %6d  %14.5f   %16.6f  %6d"
              % (m, NS_T, float(Eu) / (m ** 0.5), maxR, float(maxgap),
                 float(Eu2) / (m ** 0.5), maxR2))

    print("")
    print("=== 结构性串（全 1 串、以及按「最小超额块」拼接的候选极值串） ===")
    print("   m    全1串 R    全1串 K/q    候选串 R   候选串 K   候选块长 d  块超额 e=dq-Z")
    for m in (64, 256, 1024):
        eps = [1] * m
        R1 = R_of(eps)
        K1 = q_mp * m
        # 候选：找出使 eta(d) 最小的 d <= m，用「Z=round(dq) 个 0 与其余 1」的块拼接
        bestd, besteta = None, None
        for d in range(2, min(m, 200) + 1):
            x = d * q_mp
            r = abs(x - round(x))
            if besteta is None or r < besteta:
                besteta, bestd = r, d
        d = bestd
        Z = int(round(d * q_mp))
        # 排列：先放 0 再放 1（使块内先降后升，尝试让块边界成为环极小）
        blk = [0] * Z + [1] * (d - Z)
        t = m // d
        cand = (blk * t)[: t * d]
        Rc = R_of(cand)
        Sc = sum(cand)
        Kc = q_mp * Sc - p_mp * (len(cand) - Sc)
        print("%5d  %8d  %10.4f  %10d  %9.4f  %10d   %s"
              % (m, R1, float(K1 / q_mp), Rc, float(Kc), d, nstr((d * q_mp - Z), 8)))


if __name__ == "__main__":
    main()
