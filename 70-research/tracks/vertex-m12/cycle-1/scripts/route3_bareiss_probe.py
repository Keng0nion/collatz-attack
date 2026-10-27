#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route3_bareiss_probe.py —— 被弃方案（实现一第一版）的缺陷定位与更正（route-3 失败点清单第 1 条）。

背景：实现一的初版想把线性方程组解成整数（Bareiss 无分数消元 + 精确回代，gmpy2.mpz 全程）。
它在 m₂ = 3 的冒烟里给出错解（子集 [3, 4, 6] 把 C3 判成不满足），据此弃用、改用 gmpy2.mpq。

**本脚本的作用是把缺陷定到具体代码行，并更正一次早期误判**：
  第一版实现里有一条「若该行在当前列已为零（f == 0），跳过整行更新」的优化。
  在无分数消元里这是错的：Bareiss 的每一步要把整行乘上主元再除以上一步主元，
  f == 0 时该行仍须被缩放，跳过会破坏「第 k 步的条目 = 相应子式」这一不变量，
  后续除法随之出现不整除；而 Python 的 // 是取下整，会把不整除静默变成错解。

早期（错误）结论是「行交换与 Bareiss 的精确整除不变量不相容」。本脚本的 B 段把这条
更正掉：修正行更新后，允许行交换的版本在 4000 组随机方阵上**零不整除**。

运行：python route3_bareiss_probe.py
"""
import random
from gmpy2 import mpz


def bareiss(A, b, n, skip_zero_row, allow_swap):
    """Bareiss 前向消元，带三种开关，返回 (结局, 已发生行交换数)。

    skip_zero_row=True 复现第一版的缺陷（f == 0 时跳过整行）；
    False 为修正版：无论 f 是否为零，整行都按 (主元·行 − f·主元行)/上一步主元 更新。
    allow_swap=False 时遇到零主元直接报 'needs-swap'（用于统计有多少样本需要交换）。
    """
    M = [[mpz(v) for v in row] for row in A]
    c = [mpz(v) for v in b]
    prev = mpz(1)
    swaps = 0
    for k in range(n):
        piv = -1
        for i in range(k, n):
            if M[i][k] != 0:
                piv = i
                break
        if piv < 0:
            return "singular", swaps
        if piv != k:
            if not allow_swap:
                return "needs-swap", swaps
            M[k], M[piv] = M[piv], M[k]
            c[k], c[piv] = c[piv], c[k]
            swaps += 1
        pk = M[k][k]
        for i in range(k + 1, n):
            f = M[i][k]
            if skip_zero_row and f == 0:
                continue
            for j in range(n):
                num = pk * M[i][j] - f * M[k][j]
                if num % prev != 0:
                    return "inexact-matrix", swaps
                M[i][j] = num // prev
            num = pk * c[i] - f * c[k]
            if num % prev != 0:
                return "inexact-rhs", swaps
            c[i] = num // prev
        prev = pk
    return "ok", swaps


def make_cases(n_trials=4000, seed=1):
    random.seed(seed)
    cases = []
    for _ in range(n_trials):
        n = random.randint(2, 6)
        A = [[random.randint(-20, 20) for _ in range(n)] for _ in range(n)]
        b = [random.randint(-20, 20) for _ in range(n)]
        cases.append((n, A, b))
    return cases


def tally(cases, skip_zero_row, allow_swap):
    stat = {}
    swap_hist = {}
    for n, A, b in cases:
        kind, swaps = bareiss(A, b, n, skip_zero_row, allow_swap)
        stat[kind] = stat.get(kind, 0) + 1
        if kind.startswith("inexact"):
            swap_hist[swaps] = swap_hist.get(swaps, 0) + 1
    return stat, swap_hist


def main():
    cases = make_cases()
    n_trials = len(cases)
    print(f"随机整数方阵 {n_trials} 组（n = 2 至 6，元素 ±20，种子固定便于复跑）：")
    stat_a, hist_a = tally(cases, skip_zero_row=True, allow_swap=True)
    n_inexact = sum(v for k, v in stat_a.items() if k.startswith("inexact"))
    n_inexact_swap0 = hist_a.get(0, 0)
    print("A 段 复现第一版缺陷（f == 0 跳过整行，允许行交换）：")
    print(f"    结局分布 = {dict(sorted(stat_a.items()))}")
    print(f"    不整除合计 = {n_inexact}；其中「失败前一次行交换都没发生」的 = {n_inexact_swap0}"
          f"；发生过行交换的 = {n_inexact - n_inexact_swap0}")
    print("    => 不整除与行交换没有因果绑定（多数不整除样本根本没交换过），"
          "真正的成因是「f == 0 跳过整行」破坏不变量。")
    stat_b, _ = tally(cases, skip_zero_row=False, allow_swap=True)
    print("B 段 修正行更新（整行照乘主元），允许行交换：")
    print(f"    结局分布 = {dict(sorted(stat_b.items()))}")
    print("    => 零不整除；「Bareiss 与行主元不相容」这一早期结论在本实验上被否定。")
    stat_c, _ = tally(cases, skip_zero_row=False, allow_swap=False)
    print("C 段 修正行更新且禁止行交换（用于统计需要交换的样本量）：")
    print(f"    结局分布 = {dict(sorted(stat_c.items()))}")
    print("判读：第一版被弃用的真实原因是实现缺陷（一条想当然的行更新优化）加上"
          "「整除正确性要靠实现细节保证」这一脆弱性；换成 gmpy2.mpq 后正确性论证变短。"
          "本脚本不再主张 Bareiss 与主元交换本质不相容。")


if __name__ == "__main__":
    main()
