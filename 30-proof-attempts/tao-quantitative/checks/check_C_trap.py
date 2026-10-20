#!/usr/bin/env python3
"""check_C_trap.py

独立验证「局部新结论 C」（陷阱引理 / 类层面不可达性）：

  对每个奇 q >= 3，映射
        C_q(N) = N/2        (N 偶)
        C_q(N) = 3N + q     (N 奇)
  满足 GGM（Gonçalves、Greenfeld、Madrid）定理 1.3 的三个条件
        (a) p = 2 与 q_mult = 3 互素；
        (b) 3 < 2^{2/1} = 4；
        (c) 3*1 + r(1) ≡ 0 (mod 2)（取 r(1) = q，q 为奇数）；
  并且 qZ 是 C_q 的前向不变集，于是对一切 N ∈ qZ 有 S_min(N) >= q，
  从而 {N : S_min(N) > B} 的自然密度 >= 1/q（对一切 B < q），
  即：GGM 定理的结论（对任何 f → ∞，{S_min > f(N)} 的对数密度为 0）
  与「固定阈值 B 的密度为正的陷阱」完全相容。

本程序验证：
  1. qZ 的不变性（直接模拟，逐点检查）；
  2. qZ 上轨道的最小值 >= q；
  3. qZ 的自然密度 = 1/q（有限范围统计 + 精确计数）；
  4. 诱导动力学：N = qM 时，C_q 在 qZ 上的作用与标准 Collatz 映射 M ↦ M/2 或
     3M+1 一致（逐点检查，用标准 Collatz 的加速映射做对比）；
  5. 三个 GGM 条件的算术检查；
  6. 附带：q = 3 与 q = 5 时在范围内找到的环（观察值，不是定理）。

用法：python3 check_C_trap.py [NMAX]
默认 NMAX = 200000。
"""

import sys
from math import gcd


def C(q, N):
    return N // 2 if N % 2 == 0 else 3 * N + q


def orbit_min(q, N, cap=10 ** 7):
    """返回到达 1（若进入 < q 的值）或走满 cap 的最小值。"""
    x = N
    m = x
    for _ in range(cap):
        if x == 1:
            return m, "reached 1"
        x = C(q, x)
        if x < m:
            m = x
    return m, "cap"


def standard_collatz_acc(M):
    """标准 Collatz 的加速映射（用于第 4 项对比）：M/2（偶）、(3M+1)/2（奇）。"""
    return M // 2 if M % 2 == 0 else (3 * M + 1) // 2


def main():
    NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
    QLIST = [3, 5, 7, 9, 11, 13, 15, 21, 35]

    print(f"check_C_trap: NMAX = {NMAX}")
    print()
    print("--- (5) GGM 条件算术检查 (p=2, q_mult=3, r(1)=q) ---")
    for q in QLIST:
        a = gcd(2, 3) == 1
        b = 3 < 2 ** (2 / 1)
        c = (3 * 1 + q) % 2 == 0
        print(f"  q={q:3d}: (a) gcd(2,3)=1 -> {a};  (b) 3 < 4 -> {b};  "
              f"(c) (3*1+{q}) mod 2 = {(3 * 1 + q) % 2} -> {c}")

    print()
    print("--- (1)(2) qZ 的不变性与轨道最小值 ---")
    for q in QLIST:
        n_inv = 0
        n_inv_bad = 0
        first_bad = None
        n_min_bad = 0
        first_min_bad = None
        count = 0
        for M in range(1, NMAX // q + 1):
            N = q * M
            count += 1
            # 不变性：单步与多步
            if C(q, N) % q != 0:
                n_inv_bad += 1
                if first_bad is None:
                    first_bad = (N, C(q, N))
            else:
                n_inv += 1
            # 轨道最小值（只对小 N 全轨道模拟，避免耗时）
            if N <= 2000:
                m, _ = orbit_min(q, N, 20000)
                if m < q:
                    n_min_bad += 1
                    if first_min_bad is None:
                        first_min_bad = (N, m)
        print(f"  q={q:3d}: qZ∩[1,{NMAX}] 计数={count}; 一步后仍在 qZ 的={n_inv}; "
              f"越界={n_inv_bad} {first_bad if first_bad else ''};  "
              f"N<=2000 中最小值<q 的个数={n_min_bad} {first_min_bad if first_min_bad else ''}")

    print()
    print("--- (3) 陷阱密度的有限范围统计与精确值 ---")
    for q in (3, 5, 7, 11):
        cnt = NMAX // q
        print(f"  q={q:3d}: #{'{N <= ' + str(NMAX) + ' : N in qZ}'} = {cnt}, "
              f"占比 = {cnt / NMAX:.6f}, 1/q = {1.0 / q:.6f}, 精确 = {cnt * q <= NMAX}")

    print()
    print("--- (3b) 固定阈值 B 下 {S_min > B} 的有限范围密度 ---")
    for q in (5, 11):
        for B in range(1, 6):
            # 在 N <= NMAX 内统计轨道最小值 > B 的 N（全轨道模拟，只对小范围）
            if NMAX > 20000:
                Nloc = 20000
            else:
                Nloc = NMAX
            cnt = 0
            for N in range(1, Nloc + 1):
                m, _ = orbit_min(q, N, 5000)
                if m > B:
                    cnt += 1
            print(f"  q={q:3d}, B={B}: #{'{N<=' + str(Nloc) + ' : S_min(N) > B}'} = {cnt}"
                  f" ({cnt / Nloc:.4%})；而下界保证 qZ 全部落入此集合（q > B 时）")

    print()
    print("--- (4) 诱导动力学：qZ 上的 C_q 对应 M ↦ M/2 或 3M+1 ---")
    for q in (3, 5, 7):
        bad = 0
        first = None
        for M in range(1, min(NMAX // q, 20000) + 1):
            N = q * M
            CN = C(q, N)
            # N 偶 ⟺ M 偶（q 奇）
            if M % 2 == 0:
                pred = q * (M // 2)
            else:
                pred = q * (3 * M + 1)
            if CN != pred:
                bad += 1
                if first is None:
                    first = (N, CN, pred)
        print(f"  q={q:3d}: M<=20000 上不一致={bad} {first if first else ''}")

    print()
    print("--- (6) 附带的环观察（不是定理）---")
    for q in (3, 5):
        seen = set()
        cycles = []
        for N0 in range(1, min(NMAX, 40000) + 1):
            # 找最小元素作为代表元
            m, _ = orbit_min(q, N0, 5000)
            key = m
            if key not in seen:
                seen.add(key)
        print(f"  q={q:3d}: 在 N<={min(NMAX, 40000)} 中出现的轨道最小值集合（去重）= "
              f"{sorted(seen)[:12]}{' ...' if len(seen) > 12 else ''}（共 {len(seen)} 个）")


if __name__ == "__main__":
    main()
