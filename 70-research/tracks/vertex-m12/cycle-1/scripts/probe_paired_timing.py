#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配对计时探针：同一进程内交替测量两条代码路径对同一批子集的判定成本。

背景：S 档（three_way_baseline.py S）与成本分布探针（probe_cost_distribution.py）
用同一冻结函数、同一 Det 抽样流（前 2000 个 m2 = 10 随机子集完全相同），
但实测均值相差约 4 倍。本探针把两条路径放在同一进程内交替各跑 6 轮：
    路径 A（S 档式）：外层 time.time() 包住整段循环；
    路径 B（探针式）：逐子集 time.perf_counter() 包住 cost(S) 的判定。
每轮都记录墙钟与进程 CPU 时间（time.process_time）。若两路径在同一轮内一致，
则先前差异来自机器状态（负载、核心迁移、频率），不是代码路径；若某路径系统性
偏慢，则是代码差异，必须在报告里点名。

用法： "<venv>/python" probe_paired_timing.py
"""
import os
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "frozen"))
import r2_common as rc

m2, W = 10, Fraction(2000)
dlo = rc.delta_rigorous_bounds(10 ** 7)[0]
n = 2 * m2 + 1
cons = rc.constraint_list(m2, dlo, W)

det = rc.Det(20261027)
SUBS = []
for _ in range(2000):
    pool = list(range(n))
    for i in range(m2):
        j = i + det.below(n - i)
        pool[i], pool[j] = pool[j], pool[i]
    SUBS.append(tuple(sorted(pool[:m2])))


def path_A():
    """S 档式：外层计时，循环内联判定。"""
    t0 = time.time()
    p0 = time.process_time()
    hits = 0
    for S in SUBS:
        rows = [cons[i][0] for i in S]
        b = [cons[i][1] for i in S]
        sol, rank = rc.solve_exact(rows, b)
        if sol is None or rank < m2:
            continue
        ok, _ = rc.feasible(sol, m2, dlo, W)
        if ok:
            hits += 1
    return time.time() - t0, time.process_time() - p0, hits


def path_B():
    """探针式：逐子集计时 + 函数调用包装。"""
    t0 = time.time()
    p0 = time.process_time()
    tt = 0.0
    hits = 0
    for S in SUBS:
        rows = [cons[i][0] for i in S]
        b = [cons[i][1] for i in S]
        q0 = time.perf_counter()
        sol, rank = rc.solve_exact(rows, b)
        if sol is not None and rank >= m2:
            ok, _ = rc.feasible(sol, m2, dlo, W)
        else:
            ok = False
        tt += time.perf_counter() - q0
        if ok:
            hits += 1
    return time.time() - t0, tt, time.process_time() - p0, hits


def main():
    print(f"配对探针：m2 = {m2}，δ = {dlo}，W = {W}；同一批 {len(SUBS)} 个子集（Det(20261027) 前 2000）")
    print("轮次 | 路径 A 墙钟 | 路径 A CPU | 路径 B 墙钟 | 路径 B 判定累计 | 路径 B CPU | 命中")
    for r in range(6):
        if r % 2 == 0:
            a_wall, a_cpu, a_hits = path_A()
            b_wall, b_judge, b_cpu, b_hits = path_B()
        else:
            b_wall, b_judge, b_cpu, b_hits = path_B()
            a_wall, a_cpu, a_hits = path_A()
        print(f"  {r}  | {a_wall:.3f} s | {a_cpu:.3f} s | {b_wall:.3f} s | {b_judge:.3f} s | "
              f"{b_cpu:.3f} s | A={a_hits} B={b_hits}")
    print("判读：同一轮内 A 与 B 的墙钟应接近（B 略多计时开销）；若逐轮整体漂移，")
    print("      则成本随时间变（机器状态），与代码路径无关。")


if __name__ == "__main__":
    main()
