#!/usr/bin/env python3
"""check_F_cf.py

测量「劣质块」分析（引理 E4）所需的丢番图量：

    eta(m) := min_{1 <= d <= m, l 整数} |d q - l|,   q = 1 - p = log_2(3/2)

并给出连分数侧的可核算下界：对 q 的连分数分式分母 q_n 有严格事实
    min_{1 <= d < q_{n+1}} |d q - l| >= |q_n q - p_n| >= 1/(q_n + q_{n+1}),
（第一式是「最佳逼近」性质，第二式是连分数的标准不等式；两者都是初等等式，
但 q_n 本身是由数值展开得到的，故本文件是数值测量而非证明。）

报告：
 1. q 与 p = log_3 2 的连分数部分商（dps = 80）；
 2. 分式收敛子的 q_n 与 |q_n q - p_n|，以及乘积 q_n * |q_n q - p_n|（应当趋近 1/ 某常数）；
 3. 由严格不等式给出的 eta 下界在 d = q_n 处的形状：d * (1/(q_n + q_{n+1}))；
 4. 直接扫描 eta(m) 的小 m 表与 m * eta(m)，用以展示「eta(m) ~ c/m」的量级。

用法：python3 check_F_cf.py [NDEPTH]
默认 NDEPTH = 45。
"""

import sys
from mpmath import mp, mpf, log, nstr, floor

mp.dps = 80


def cf(x, n):
    a = []
    for _ in range(n):
        ai = int(floor(x))
        a.append(ai)
        x = x - ai
        if x == 0:
            break
        x = 1 / x
    return a


def convergents(a):
    pn1, pn2 = 1, 0   # p_{-1} = 1, p_{-2} = 0
    qn1, qn2 = 0, 1
    out = []
    for ai in a:
        pn = ai * pn1 + pn2
        qn = ai * qn1 + qn2
        out.append((pn, qn))
        pn1, pn2 = pn, pn1
        qn1, qn2 = qn, qn1
    return out


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 45
    p = log(mpf(2)) / log(mpf(3))
    q = 1 - p
    print("check_F_cf: 深度 %d，dps = %d" % (N, mp.dps))
    print("p = log_3 2 = %s" % nstr(p, 40))
    print("q = log_2(3/2) = %s" % nstr(q, 40))
    for name, x in (("p = log_3 2", p), ("q = log_2(3/2)", q)):
        a = cf(x, N)
        cvg = convergents(a)
        print("")
        print("--- %s 的连分数 ---" % name)
        print("部分商 a_1..a_%d: %s" % (len(a), a))
        print("部分商最大值 = %d   （数值展开，非证明）" % max(a))
        print("   n        q_n            |q_n*x - p_n|        严格下界 1/(q_n+q_{n+1})   q_n*|q_n*x-p_n|")
        for i in range(min(len(cvg) - 1, N - 1)):
            pn, qn = cvg[i]
            pn1, qn1 = cvg[i + 1]
            e = abs(qn * x - pn)
            l = 1 / mpf(qn + qn1)
            print("  %3d  %14d  %s   %s   %s"
                  % (i, qn, nstr(e, 12), nstr(l, 12), nstr(qn * e, 12)))
    print("")
    print("--- 直接扫描 eta(m) = min_{d<=m}|dq - l|（q = log_2(3/2)）---")
    print("      m         eta(m)          m*eta(m)")
    best = None
    hist = []
    for m in range(1, 4001):
        x = m * q
        r = abs(x - round(x))
        if best is None or r < best:
            best = r
            hist.append((m, r))
    for m in (2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 3999):
        x = m * q
        r = abs(x - round(x))
        # 只算「到 m 为止」的最小值
        bm = min(abs(t * q - round(t * q)) for t in range(1, m + 1))
        print("  %6d   %s   %s" % (m, nstr(bm, 12), nstr(m * bm, 12)))
    print("")
    print("--- 逐段最小值的「记录」序列（m 处新低的 (m, eta(m))） ---")
    print("  m        eta(m)         m*eta(m)")
    for (m, r) in hist[:25]:
        print("  %6d  %s   %s" % (m, nstr(r, 12), nstr(m * r, 12)))


if __name__ == "__main__":
    main()
