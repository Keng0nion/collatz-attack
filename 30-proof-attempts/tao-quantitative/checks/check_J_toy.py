#!/usr/bin/env python3
"""check_J_toy.py

本会话按反驳意见逐条复核其两个反例主张（我自己独立实现，不读反驳方的脚本）：

反例映射（反驳方给出）：
    f(N) = 1       若 N 为奇数
    f(N) = N/2     若 N ≡ 0 (mod 4)
    f(N) = 2       若 N ≡ 2 (mod 4)
记 S_min(N) = 轨道最小值，A_C = {N : S_min(N) > C}，B_m = {N : S_min(N) = m}。

要核对的三件事：
 (J1) 对每个 C >= 2，{N <= X : S_min(N) > C} 是空集（计数与对数权重都为 0）；
 (J2) 对数权重（我用等权求和 1/N，再用 log X 归一）在 {S_min > 1} 上趋于 1/2 > 0；
 (J3) 逐 x 恒等式  sum_{2 <= m <= x} logweight(B_m ∩ [1,x]) = logweight(A_1 ∩ [1,x])
      （后者是「下一步 #4 的目标不是更弱形式，而就是 T2」的证据）。

用法：python3 check_J_toy.py [X]
默认 X = 200000。
"""

import sys
from fractions import Fraction


def step(n):
    if n % 2 == 1:
        return 1
    if n % 4 == 0:
        return n // 2
    return 2


def orbit_min(n, cap=10000):
    seen = set()
    x = n
    m = x
    while True:
        if x in seen:
            return m
        seen.add(x)
        m = min(m, x)
        x = step(x)
        if x == 2 and n % 2 == 0:
            m = min(m, 2)
            return m
        if x == 1 and n % 2 == 1:
            return 1
        if len(seen) > cap:
            raise RuntimeError("cap exceeded")


def main():
    X = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
    print("check_J_toy: X = %d，映射 f(N) = 1（奇）、N/2（N≡0 mod 4）、2（N≡2 mod 4）" % X)

    mins = {}
    for n in range(1, X + 1):
        mins[n] = orbit_min(n)

    # (J1)
    print("")
    print("(J1) 各层 {S_min > C} 的计数（应当对 C >= 2 全为 0）：")
    for C in (1, 2, 3, 4):
        cnt = sum(1 for n in range(1, X + 1) if mins[n] > C)
        print("   C = %d : 计数 = %d" % (C, cnt))

    # (J2) 对数权重
    print("")
    print("(J2) 对数权重（1/N 求和，除以 log X）：")
    import math
    def logw(pred):
        return sum(Fraction(1, n) for n in range(1, X + 1) if pred(n))
    lw1 = logw(lambda n: mins[n] > 1)
    lw2 = logw(lambda n: mins[n] > 2)
    print("   logweight({S_min > 1}) / log X = %.6f" % (float(lw1) / math.log(X)))
    print("   logweight({S_min > 2}) / log X = %.6f" % (float(lw2) / math.log(X)))

    # (J3) 逐 x 恒等式：用 x = X 检验（对每个 x 都是集合恒等式）
    for x in (X, X // 2, X // 7):
        lhs = Fraction(0)
        for m in range(2, x + 1):
            for n in range(m, x + 1):
                if mins[n] == m:
                    lhs += Fraction(1, n)
        rhs = Fraction(0)
        for n in range(1, x + 1):
            if mins[n] > 1:
                rhs += Fraction(1, n)
        print("")
        print("(J3) x = %7d : sum_{2<=m<=x} logweight(B_m ∩ [1,x]) = %s"
              % (x, float(lhs)))
        print("            logweight(A_1 ∩ [1,x])                = %s   相等 = %s"
              % (float(rhs), lhs == rhs))

    print("")
    print("注：本脚本只复核「反驳方关于该玩具映射的两条主张」与一条恒等式，")
    print("     不涉及 3x+1 本身；映射是不可逆的分段仿射映射（f 非单射）。")


if __name__ == "__main__":
    main()
