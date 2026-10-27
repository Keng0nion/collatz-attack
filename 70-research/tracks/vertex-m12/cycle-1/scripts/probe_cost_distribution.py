#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成本分布探针：为什么「均匀随机子集」的每子集成本与「整场穷举」的平均不一致。

对照甲实测：整场穷举 352716 个子集共 70.4 s（平均 0.1996 ms/子集）。
成本抽样 S 实测：2000 个均匀随机子集平均 1.1691 ms/子集。
两者在对同一分布上应相等（穷举按定义遍历每个子集一次），故必有其一有问题。
本探针把同一判定函数（冻结副本）用在四种取样子集上，分别计时并统计秩命中的比例：
    1. 字典序最前 3000 个；2. 字典序最后 3000 个；3. 均匀随机 3000 个（Det）；
    4. 等距抽样：从整场 352716 个里等距取 3000 个（用 islice 跳过）。
另打印：每个子集的求解结果分类（秩 < m2 / 秩 = m2 且可行 / 秩 = m2 不可行）。

用法： "<venv>/python" probe_cost_distribution.py
"""
import os
import sys
import time
from fractions import Fraction
from itertools import combinations, islice

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "frozen"))
import r2_common as rc

m2, W = 10, Fraction(2000)
dlo = rc.delta_rigorous_bounds(10 ** 7)[0]
n = 2 * m2 + 1
total = 1
for i in range(m2):
    total = total * (n - i) // (i + 1)
cons = rc.constraint_list(m2, dlo, W)


def cost(S):
    """单个子集的判定成本（秒）与分类。"""
    rows = [cons[i][0] for i in S]
    b = [cons[i][1] for i in S]
    t0 = time.perf_counter()
    sol, rank = rc.solve_exact(rows, b)
    if sol is not None and rank >= m2:
        ok, _ = rc.feasible(sol, m2, dlo, W)
    else:
        ok = False
    dt = time.perf_counter() - t0
    if rank < m2:
        kind = "秩<m2"
    elif ok:
        kind = "秩=m2 可行"
    else:
        kind = "秩=m2 不可行"
    return dt, kind


def report(name, Ss):
    kinds = {"秩<m2": 0, "秩=m2 可行": 0, "秩=m2 不可行": 0}
    tt = 0.0
    t0 = time.perf_counter()
    for S in Ss:
        dt, kind = cost(S)
        tt += dt
        kinds[kind] += 1
    wall = time.perf_counter() - t0
    k = len(Ss)
    print(f"{name}：样本 {k} 个；判定用时合计 {tt:.4f} s，平均 {1000*tt/k:.4f} ms/子集；"
          f"含抽样总墙钟 {wall:.2f} s")
    print(f"    分类：秩<m2 = {kinds['秩<m2']}；秩=m2 不可行 = {kinds['秩=m2 不可行']}；"
          f"秩=m2 可行 = {kinds['秩=m2 可行']}")
    return tt / k


def main():
    print(f"探针参数：m2 = {m2}，δ = {dlo}，W = {W}，子集总数 = {total}（数学组合数 352716）")
    k = 3000
    first = list(islice(combinations(range(n), m2), k))
    last = list(islice(combinations(range(n), m2), total - k, total))
    det = rc.Det(20261027)

    def rand_subset():
        pool = list(range(n))
        for i in range(m2):
            j = i + det.below(n - i)
            pool[i], pool[j] = pool[j], pool[i]
        return tuple(sorted(pool[:m2]))

    rnd = [rand_subset() for _ in range(k)]
    stride = total // k
    it = iter(combinations(range(n), m2))
    strided = []
    idx = 0
    want = set(range(0, total, stride))
    for pos, S in enumerate(it):
        if pos in want:
            strided.append(S)
            if len(strided) >= len(want):
                break
    m_first = report("字典序最前 3000", first)
    m_last = report("字典序最后 3000", last)
    m_rand = report(f"均匀随机 3000（Det，步距 {stride} 无关）", rnd)
    m_str = report("等距抽样 3000（步距 %d）" % stride, strided)
    print(f"\n对照：整场穷举实测平均 = 0.1996 ms/子集（threeway-A-positive.txt：70.4 s / 352716）")
    print(f"四个采样均值：最前 {1000*m_first:.4f}；最后 {1000*m_last:.4f}；"
          f"随机 {1000*m_rand:.4f}；等距 {1000*m_str:.4f} ms/子集")
    print("判读：若等距与随机一致而最前/最后不同，则成本依子集内容而非枚举位置；"
          "若四者一致（皆约 0.2 ms），则 S 档测速必有实现偏差，待查。")


if __name__ == "__main__":
    main()
