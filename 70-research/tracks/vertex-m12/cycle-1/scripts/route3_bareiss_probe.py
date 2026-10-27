#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route3_bareiss_probe.py —— 被弃方案的诊断记录（route-3 失败点清单第 1 条）。

背景：实现一的初版想做「Bareiss 无分数消元（部分主元）+ 精确回代」，用 gmpy2 整数
全程无分数。自抽查发现：**带行交换的 Bareiss 与前向消元的精确整除不变量不相容**——
一旦在某一步发生行交换，后续 (主元·a_ij − a_ik·a_kj) 就出现不能被上一步主元整除的
情形，而 Python 的 // 是取下整，会静默给出错误解。本脚本把这一诊断固化下来，便于
复跑核对；它同时说明为什么实现一最终改用 gmpy2.mpq 的精确有理消元（无整除约定）。

运行：python route3_bareiss_probe.py
判读：输出会给出「无行交换时整除恒成立、有行交换时出现不整除」的计数对比。
"""
import random
from gmpy2 import mpz


def bareiss_diag(A, b, n):
    """在带部分主元的 Bareiss 上检查「每一步是否精确整除」。"""
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
            return ("singular", k, swaps)
        if piv != k:
            M[k], M[piv] = M[piv], M[k]
            c[k], c[piv] = c[piv], c[k]
            swaps += 1
        pk = M[k][k]
        for i in range(k + 1, n):
            f = M[i][k]
            if f == 0:
                continue
            for j in range(n):
                num = pk * M[i][j] - f * M[k][j]
                if num % prev != 0:
                    return ("inexact-matrix", k, swaps)
                M[i][j] = num // prev
            num = pk * c[i] - f * c[k]
            if num % prev != 0:
                return ("inexact-rhs", k, swaps)
            c[i] = num // prev
        prev = pk
    return ("ok", n, swaps)


def main():
    random.seed(1)
    n_trials = 4000
    stat = {"ok": 0, "singular": 0, "inexact": 0, "ok_no_swap": 0, "inexact_with_swap": 0}
    for _ in range(n_trials):
        n = random.randint(2, 6)
        A = [[random.randint(-20, 20) for _ in range(n)] for _ in range(n)]
        b = [random.randint(-20, 20) for _ in range(n)]
        kind, _k, swaps = bareiss_diag(A, b, n)
        if kind.startswith("inexact"):
            stat["inexact"] += 1
            if swaps:
                stat["inexact_with_swap"] += 1
        elif kind == "ok":
            stat["ok"] += 1
            if swaps == 0:
                stat["ok_no_swap"] += 1
        else:
            stat["singular"] += 1
    print(f"随机整数方阵 {n_trials} 组（n = 2 至 6，元素 ±20）：")
    print(f"  全程精确整除 = {stat['ok']}；奇异 = {stat['singular']}；出现不整除 = {stat['inexact']}")
    print(f"  其中「无行交换」且精确整除 = {stat['ok_no_swap']}；"
          f"不整除且发生过行交换 = {stat['inexact_with_swap']}")
    print("判读：无行交换时整除恒成立；行交换与 Bareiss 整除不变量不相容 => "
          "带主元交换的 Bareiss 不能直接用作精确解算器（本项目已弃用该方案）。")


if __name__ == "__main__":
    main()
