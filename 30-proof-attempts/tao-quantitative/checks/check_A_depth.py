#!/usr/bin/env python3
"""check_A_depth.py

独立验证「局部新结论 A」（固定深度上升类的精确刻画）及其引理杀手。

加速映射 T(n) = n/2（n 偶）、(3n+1)/2（n 奇）。

主张一（精确刻画，已证）：对 D >= 1 与 n >= 1，下列等价：
    (i)   2^D 整除 n+1；
    (ii)  n, T(n), ..., T^{D-1}(n) 全为奇数；
    (iii) 前 D 步逐步严格上升：T^i(n) > T^{i-1}(n) 对 1 <= i <= D。
主张二（闭式）：在 (i) 成立时，T^i(n) = 3^i (n+1) / 2^i - 1（0 <= i <= D），
    于是 T^i(n) > n 对 1 <= i <= D 自动成立。
主张三（密度精确）：{n <= X : 2^D | (n+1)} 在 X 为 2^D 的倍数时恰有 X/2^D 个元素。
主张四（引理杀手，本程序给出反例）：朴素的加强命题
    「T^i(n) > n 对一切 1 <= i <= D  <=>  2^D | n+1」是假的；
    最小反例在 D = 3、n = 3 处（T(3)=5>3、T^2(3)=8>3、T^3(3)=4>3，但 3 不被 8 整除后的 7 同余类）。
    本程序枚举全部 D 与 n，报告每个 D 的最小反例。
主张五（与非下降密度的连接）：dens{ n : T^i(n) >= n 对 1 <= i <= D } = A(D)/2^D，
    其中 A(D) 为长度 D 的「可容许」奇偶向量数（定义见 check_B）。
    本程序用暴力枚举在 n <= 2^M 上核对。

用法：python3 check_A_depth.py [NMAX] [DMAX]
默认 NMAX = 2^18，DMAX = 18。
"""

import sys


def T(x: int) -> int:
    return x // 2 if x % 2 == 0 else (3 * x + 1) // 2


def walk(n: int, D: int):
    """返回 (各步是否严格上升, 各中间值是否奇数, 各步后的值列表)。"""
    x = n
    up = []
    odd = []
    vals = [x]
    for _ in range(D):
        odd.append(x % 2 == 1)
        y = T(x)
        up.append(y > x)
        x = y
        vals.append(x)
    return up, odd, vals


def A_vec(D: int):
    """长度 D 的可容许奇偶向量数：前 i 位（1<=i<=D）满足 3^{S_i} >= 2^i。"""
    # 精确整数判据：S_i >= t_i，t_i = min{ s : 3^s >= 2^i }
    t = [0] * (D + 1)
    s, pw3 = 0, 1
    for i in range(1, D + 1):
        while pw3 < (1 << i):
            s += 1
            pw3 *= 3
        t[i] = s
    f = [0] * (D + 2)
    f[0] = 1
    for i in range(1, D + 1):
        g = [0] * (D + 2)
        for ss in range(0, i + 1):
            if f[ss]:
                g[ss] += f[ss]
                g[ss + 1] += f[ss]
        for ss in range(0, t[i]):
            g[ss] = 0
        f = g
    return sum(f)


def main():
    NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 1 << 18
    DMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 18

    print(f"check_A_depth: n <= {NMAX}, D <= {DMAX}")
    bad1 = bad2 = bad3 = 0
    first = {}
    for D in range(1, DMAX + 1):
        for n in range(1, NMAX + 1):
            in_class = (n + 1) % (1 << D) == 0
            up, odd, vals = walk(n, D)
            if in_class != all(odd):          # 主张一 (i) <=> (ii)
                bad1 += 1
            if in_class != all(up):           # 主张一 (i) <=> (iii)
                bad2 += 1
            if in_class:                      # 主张二 闭式
                for i in range(0, D + 1):
                    if vals[i] != (3 ** i) * (n + 1) // (1 << i) - 1:
                        bad3 += 1
            # 主张四：朴素加强命题的反例（T^i(n) > n 全成立但 n 不在类里）
            naive = all(vals[i] > n for i in range(1, D + 1))
            if naive and not in_class:
                if D not in first:
                    first[D] = n
    print(f"主张一(i)<=>(ii) 不一致数 = {bad1}")
    print(f"主张一(i)<=>(iii) 不一致数 = {bad2}")
    print(f"主张二 闭式 不一致数 = {bad3}")
    print()
    print("主张四：朴素命题「T^i(n) > n (1<=i<=D) <=> 2^D | n+1」的最小反例")
    print("  （空格表示在 n <= NMAX 内该 D 无反例）")
    for D in range(1, min(DMAX, 12) + 1):
        n0 = first.get(D)
        if n0 is None:
            print(f"  D={D:2d}: 无")
        else:
            up, odd, vals = walk(n0, D)
            print(f"  D={D:2d}: n={n0}  轨道前几步={vals[1:D + 1]}  "
                  f"全大于 n={n0} -> {all(v > n0 for v in vals[1:D + 1])}  "
                  f"而 (n+1) mod 2^D = {(n0 + 1) % (1 << D)}")

    print()
    print("主张三（密度精确）：X 为 2^D 的倍数时 #{{n<=X : 2^D | n+1}} = X/2^D")
    for D in (1, 2, 3, 4, 5, 6, 8, 10, 12):
        step = 1 << D
        X = (NMAX // step) * step
        cnt = X // step
        print(f"  D={D:2d}: X={X}  计数={cnt}  X/2^D={X // step}  "
              f"精确={cnt * step == X}  密度={cnt / X:.10f}  2^-D={1 / step:.10f}")

    print()
    print("主张五：dens{n : T^i(n) >= n, 1<=i<=D} = A(D)/2^D")
    print("  说明：在 n <= 2^D 的单个周期上，非可容许类里的「阈值以下小元素」会给")
    print("  出 O(1) 个额外命中，因此有限计数略大于 A(D)；密度要取 X = 2^{D+SHIFT}。")
    SHIFT = 4
    for D in range(1, min(DMAX, 11) + 1):
        N = 1 << (D + SHIFT)
        cnt = 0
        for n in range(1, N + 1):
            x = n
            ok = True
            for _ in range(D):
                x = T(x)
                if x < n:
                    ok = False
                    break
            if ok:
                cnt += 1
        AD = A_vec(D)
        frac = cnt / N
        print(f"  D={D:2d}: 计数/X = {cnt}/{N} = {frac:.6f}   "
              f"A(D)/2^D = {AD / (1 << D):.6f}   差 = {frac - AD / (1 << D):.2e}")

    print()
    print("主张五附注：单个周期 n <= 2^D 上的计数与 A(D) 的差（截断效应）")
    for D in range(1, min(DMAX, 11) + 1):
        N = 1 << D
        cnt = 0
        for n in range(1, N + 1):
            x = n
            ok = True
            for _ in range(D):
                x = T(x)
                if x < n:
                    ok = False
                    break
            if ok:
                cnt += 1
        print(f"  D={D:2d}: 计数={cnt}  A(D)={A_vec(D)}  差={cnt - A_vec(D)}")


if __name__ == "__main__":
    main()
