#!/usr/bin/env python3
"""check_I_sa_exact.py

对「Sparre Andersen 型恒等式」在我们这条游走上做**逐阶精确检验**，
以判定 attempt.md 第 16 步与局部结论 G1 的状态标注是否恰当。

待检验的恒等式（候选形式）：
    sum_{n>=0} u_n s^n  =  exp( sum_{k>=1} (s^k / k) * P(Z_k > 0) ),
其中 Z_k = S_k - k p（S_k ~ Bin(k,p)，p = log_3 2），u_n = P(Z_i > 0, 1 <= i <= n) = A(n)/2^n。

做法：左边用精确整数 DP 算 A(n)（故 u_n 精确）；右边用幂级数指数算到 N 阶（dps = 50）；
逐阶比较。若逐阶相符，则该恒等式对本游走（在数值精度内）成立；若不符，
则 G1 的「恒等式」用法只能作为渐近启发，必须改标注。

另附：对三种有理步长游走用 Fraction 精确算术检验同一恒等式（作为对照组，
用于说明该恒等式的成立与否依赖于步长分布的格结构与零点结构）。

用法：python3 check_I_sa_exact.py [N]
默认 N = 40。
"""

import sys
from fractions import Fraction
from mpmath import mp, mpf, log, exp, binomial

mp.dps = 50

P = log(mpf(2)) / log(mpf(3))
Q = 1 - P


def A_list(N):
    """A(n) = 长度 n 的可容许串数（精确整数）；A(0) = 1。"""
    out = [1]
    dp = [1]
    for i in range(1, N + 1):
        # 最小 S 使 3^S >= 2^i
        smin = 0
        while 3 ** smin < 2 ** i:
            smin += 1
        new = [0] * (i + 1)
        for S, v in enumerate(dp):
            if not v:
                continue
            if S + 1 >= smin:
                new[S + 1] += v
            if S >= smin:
                new[S] += v
        dp = new
        out.append(sum(dp))
    return out


def Pk(k):
    """P(Z_k > 0) = P(Bin(k,p) >= ceil(k p))（高精度）。"""
    thr = 0
    while thr < k * 0:  # 占位
        pass
    # ceil(k p)：用高精度判断
    x = mpf(k) * P
    thr = int(mp.ceil(x))
    s = mpf(0)
    for j in range(thr, k + 1):
        s += mpf(binomial(k, j)) * P ** j * Q ** (k - j)
    return s


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    print("check_I_sa_exact: N = %d, dps = %d" % (N, mp.dps))
    A = A_list(N)
    u_unif = [exp(log(mpf(A[n])) - n * log(mpf(2))) for n in range(N + 1)]
    # 倾斜概率 Q(E_n) = sum_S N(n,S) p^S q^{n-S}（用整数 DP 的分布）
    dist = [1]
    QE = [mpf(1)]
    for i in range(1, N + 1):
        smin = 0
        while 3 ** smin < 2 ** i:
            smin += 1
        new = [0] * (i + 1)
        for S, v in enumerate(dist):
            if not v:
                continue
            if S + 1 >= smin:
                new[S + 1] += v
            if S >= smin:
                new[S] += v
        dist = new
        QE.append(sum(mpf(v) * P ** S * Q ** (i - S) for S, v in enumerate(dist) if v))
    print("左边两个候选（等权 u_n = A(n)/2^n 与倾斜 Q(E_n)）前几项：")
    for n in range(0, 7):
        print("   n=%2d  A/2^n = %s   Q(E_n) = %s" % (n, mp.nstr(u_unif[n], 12), mp.nstr(QE[n], 12)))
    # 右边：F(s) = sum_{k>=1} (s^k/k) P_k，取 exp 的幂级数
    F = [mpf(0)] * (N + 1)          # F[k] 为 s^k 的系数
    for k in range(1, N + 1):
        F[k] = Pk(k) / k
    # exp(F)：c_0 = 1，n c_n = sum_{k=1}^{n} k F[k] c_{n-k}
    c = [mpf(0)] * (N + 1)
    c[0] = mpf(1)
    for n in range(1, N + 1):
        s = mpf(0)
        for k in range(1, n + 1):
            s += k * F[k] * c[n - k]
        c[n] = s / n
    print("")
    print("逐阶比较（相对差）：")
    print("   n     |c_n - Q(E_n)|/Q(E_n)      |c_n - A(n)/2^n| / (A(n)/2^n)")
    worst_t = worst_u = 0
    for n in range(1, N + 1):
        rt = abs(c[n] - QE[n]) / QE[n]
        ru = abs(c[n] - u_unif[n]) / u_unif[n]
        worst_t = max(worst_t, float(rt))
        worst_u = max(worst_u, float(ru))
        if n <= 10:
            print("  %3d    %s            %s" % (n, mp.nstr(rt, 3), mp.nstr(ru, 3)))
    print("")
    print("对 Q(E_n) 的逐阶最大相对差 = %.3e" % worst_t)
    print("对 A(n)/2^n 的逐阶最大相对差 = %.3e" % worst_u)
    print("结论：恒等式的左边是**倾斜**概率 Q(E_n)（而非等权 A(n)/2^n）；")
    print("若前者在 1e-35 量级以下，则该恒等式在本游走上逐阶成立（数值证据）。")

    # 对照组：三种有理步长游走，用 Fraction 精确检验
    print("")
    print("对照组（有理步长，Fraction 精确算术，检验同一形式的恒等式）：")
    walks = {
        "对称 ±1（p=1/2, 步长 +1/-1）": (Fraction(1, 2), Fraction(1), Fraction(-1)),
        "零均值非对称（p=1/3, 步长 +2/-1）": (Fraction(1, 3), Fraction(2), Fraction(-1)),
        "有偏（p=7/10, 步长 +1/-1）": (Fraction(7, 10), Fraction(1), Fraction(-1)),
    }
    for name, (p, a, b) in walks.items():
        # u_n 用精确 DP 在整数格上算：状态 = 部分和（整数）
        # 步长取值：a（概率 p）或 b（概率 1-p）
        NN = 12
        uu = {0: Fraction(1)}
        states = {0: Fraction(1)}
        left = {0: Fraction(1)}
        for n in range(1, NN + 1):
            ns = {}
            for x, w in states.items():
                for val, pr in ((a, p), (b, 1 - p)):
                    y = x + val
                    if y > 0:
                        ns[y] = ns.get(y, Fraction(0)) + w * pr
            states = ns
            left[n] = sum(states.values())
        # 右边：P(Z_k > 0) 精确
        Pk_exact = {}
        for k in range(1, NN + 1):
            # 随机游走的部分和分布（整数）
            dist = {0: Fraction(1)}
            for _ in range(k):
                nd = {}
                for x, w in dist.items():
                    nd[x + a] = nd.get(x + a, Fraction(0)) + w * p
                    nd[x + b] = nd.get(x + b, Fraction(0)) + w * (1 - p)
                dist = nd
            Pk_exact[k] = sum(w for x, w in dist.items() if x > 0)
        # exp 级数
        FF = [Fraction(0)] * (NN + 1)
        for k in range(1, NN + 1):
            FF[k] = Pk_exact[k] / k
        cc = [Fraction(0)] * (NN + 1)
        cc[0] = Fraction(1)
        for n in range(1, NN + 1):
            s = Fraction(0)
            for k in range(1, n + 1):
                s += k * FF[k] * cc[n - k]
            cc[n] = s / n
        diffs = [1 for n in range(1, NN + 1) if cc[n] != left[n]]
        print("   %s：1 至 %d 阶不符的阶数 = %d%s" %
              (name, NN, len(diffs),
               "" if not diffs else "（首次不符在 n=%d，左 %s 右 %s）"
               % (diffs[0], left[diffs[0]], cc[diffs[0]])))


if __name__ == "__main__":
    main()
