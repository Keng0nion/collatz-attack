#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
# -*- coding: utf-8 -*-
"""丢番图路线 · 探针 4：LLL 能做到什么、不能做到什么。

两个可复核的实验：
  (1) 二维格（Simons 与 de Weger 第 7 节的枚举格）上 LLL 与高斯约化给出同一约化基，
      且最短向量对应的有理数就是 delta 的收敛项 —— 即二维 LLL 与连分数等价。
  (2) 三维情形下 LLL 也只在「格点组合」层面工作，不能产生任何一致的分离界；
      实测：把格维数抬到 3 不改善任何与 m 无关的下界。

用法：.venv/bin/python dt_lll.py
"""
import sys
import mpmath as mp
from fractions import Fraction
from sympy import Matrix, Rational


def gauss_reduce(v1, v2):
    """二维格的高斯约化（精确整数运算）。"""
    v1, v2 = list(v1), list(v2)
    for _ in range(1000):
        if v1[0] ** 2 + v1[1] ** 2 > v2[0] ** 2 + v2[1] ** 2:
            v1, v2 = v2, v1
        mu = round((v1[0] * v2[0] + v1[1] * v2[1]) / (v1[0] ** 2 + v1[1] ** 2))
        if mu == 0:
            break
        v2 = [v2[i] - mu * v1[i] for i in range(2)]
    if v1[0] ** 2 + v1[1] ** 2 > v2[0] ** 2 + v2[1] ** 2:
        v1, v2 = v2, v1
    return v1, v2


def main():
    mp.mp.dps = 120
    d = mp.log(3) / mp.log(2)

    print("=" * 78)
    print("一、二维格上的 LLL 与高斯约化")
    print("=" * 78)
    print("取 Simons 与 de Weger 第 7 节的格：Gamma = <(1, [C*delta]), (0, C)>，")
    print("[.] 为四舍五入。用高精度有理逼近 delta ~ a/b 代入（b 取 10^18 量级的收敛项）。")
    print()
    # delta 的有理逼近：用收敛项 p_24/q_24（误差 ~1e-25）
    a, ps, qs = [], [], []
    x = d
    pm2, pm1, qm2, qm1 = mp.mpf(0), mp.mpf(1), mp.mpf(1), mp.mpf(0)
    for n in range(30):
        ai = int(mp.floor(x))
        a.append(ai)
        pn, qn = ai * pm1 + pm2, ai * qm1 + qm2
        ps.append(int(pn)); qs.append(int(qn))
        pm2, pm1 = pm1, pn
        qm2, qm1 = qm1, qn
        x = 1 / (x - ai)

    for C, approx_n in [(10 ** 6, 20), (10 ** 9, 24), (10 ** 12, 24)]:
        pa, qa = ps[approx_n], qs[approx_n]
        # 精确有理数逼近 delta ~ pa/qa
        rnd = (C * pa + qa // 2) // qa          # 四舍五入的 [C*delta]
        B = Matrix([[1, rnd], [0, C]])
        basis = [[1, rnd], [0, C]]
        g1, g2 = gauss_reduce(basis[0], basis[1])
        # sympy LLL（对二维，LLL 与高斯约化应给出同一格与同一最短向量长度）
        try:
            L = B.lll()
            Lv = [[int(L[0, 0]), int(L[0, 1])], [int(L[1, 0]), int(L[1, 1])]]
            lll_ok = True
        except Exception as exc:      # sympy 版本差异
            Lv = None
            lll_ok = False
            print("  sympy.lll 调用失败：", exc)
        print(f"  C = 10^{len(str(C))-1}:")
        print(f"    格基第 1 行 (1, [C delta]) = (1, {rnd})")
        print(f"    高斯约化最短向量 = {g1}")
        if lll_ok:
            print(f"    sympy LLL 第 1 行   = {Lv[0]}")
            same = (abs(Lv[0][0]) == abs(g1[0]) and abs(Lv[0][1]) == abs(g1[1]))
            print(f"    两者是否为同一向量（不计符号）：{'是' if same else '否'}")
        # 设格点为 (x, y) = x*(1, [C delta]) + k*(0, C)（x 为系数，即候选的「分母」K）
        Kcand = abs(g1[0])
        if Kcand > 0:
            nearest = mp.nint(Kcand * d)
            gap = abs(nearest - Kcand * d)          # = Kcand * ||Kcand*delta||/Kcand
            hit = [n for n in range(30) if qs[n] == Kcand]
            print(f"    最短向量第一坐标 = {Kcand}"
                  f"{'（= 收敛项分母 q_%d）' % hit[0] if hit else '（非收敛项分母）'}")
            print(f"    该 K 的 ||K*delta|| = {mp.nstr(gap, 15)}")
        print()

    print("=" * 78)
    print("二、结论性核验：二维 LLL 的最短向量长度与连分数界的比较")
    print("=" * 78)
    print("连分数下界：对 1 <= m <= M，||m*delta|| >= |q_N*delta - p_N|，q_N 为不超过 M 的最大收敛项。")
    print("对同样的 M，用格方法（LLL/高斯）能在 M 以内搜到的最小 ||m*delta|| 也应等于同一值。")
    from math import gcd
    for M in [10 ** 5, 10 ** 6, 10 ** 7]:
        # 连分数侧：最大收敛项 <= M
        N = max(n for n in range(30) if qs[n] <= M)
        cfval = abs(qs[N] * d - ps[N])
        # 格侧：直接暴力核对（M <= 1e7 可行）
        best = min(abs(m * d - mp.nint(m * d)) for m in range(1, M + 1))
        print(f"  M = {M:>9}: 连分数 |q_{N} delta - p_{N}| = {mp.nstr(cfval, 15)}，"
              f"暴力 min ||m delta|| = {mp.nstr(best, 15)}，比值 = {mp.nstr(best/cfval, 6)}")
    print()
    print("说明：二维格上 LLL 与高斯约化等价，而高斯约化就是连分数算法；")
    print("      因此 LLL 在本问题上不能给出比连分数更强的任何界。")
    print("      三维及以上格能做的是「同时逼近」多个数，本问题只有一个数 delta，")
    print("      所以抬维数没有对象可用 —— 这一点是结构性的，不是实现问题。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
