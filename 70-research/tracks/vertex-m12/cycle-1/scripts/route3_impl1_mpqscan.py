#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route3_impl1_mpqscan.py —— route-3 实现一：精确有理（gmpy2.mpq）全活跃子集穷举。

与项目既有实现的分工（独立性说明）：
  既有实现 r2_j_independent_vertices.py 的 full_enumeration 用 fractions.Fraction 做
  高斯若尔当消元、单进程、itertools.combinations 顺序枚举、逐子集判「解不唯一就弃」。
  本实现：
    1. 算术栈：系数整行放大成整数后，消元与判定全程 gmpy2.mpq（GMP 有理数），不用
       fractions.Fraction；
    2. 枚举：自写的组合字典序编号与推进（route3_defs），按编号区间切成确定性分片，
       multiprocessing 多进程并行，每片给出 64 位可交换校验和（用于不一致定位）；
    3. 判定分类拆开统计：奇异 / 唯一解但不可行 / 可行（候选），避免把前两类混计；
    4. 本实现**不 import r2_common**，也不 import r2_j_independent_vertices；只依赖
       route3_defs.py（自写：约束表、可行性、解析族、组合编号、校验和）。

搜索本体不含任何结构剪枝与任何预筛：全部 C(2m2+1, m2) 个子集都过同一套精确消元与
可行性判定。允许枚举的完备性论证（初等线性代数，route3_defs.py 文件头）：任一顶点处
存在大小 m2、秩 m2 的活跃子集；反之满秩子集的唯一解若可行必是顶点。

输出约定：进度与摘要走 stderr，完整结果 JSON 走 stdout；落盘由命令行重定向完成
（这样每个数字都能在命令行与输出文件之间直接对上，且脚本本身不写任何文件）。

弃用方案登记（含一次自我更正）：初版尝试「Bareiss 无分数消元 + 精确回代」，在 m₂ = 3
冒烟里给出错解（子集 [3, 4, 6] 被 C3 判据拒绝，顶点少一个）。诊断脚本
route3_bareiss_probe.py 把缺陷定到一条实现细节：第一版在「该行当前列已为零（f == 0）」
时跳过整行更新，而在无分数消元里整行必须照乘主元；于是 4000 组随机方阵里 305 组出现
不整除，错解被 // 静默带过。修正该行更新后，允许行交换的版本零不整除（3994 组全过）——
**故弃用的真实原因是实现脆弱性，不是「Bareiss 与主元交换不相容」（这一早期说法已由同一
脚本更正）**。本文件改用 mpq 有理消元：无整除约定，正确性论证更短。

用法：
  python route3_impl1_mpqscan.py --m2 10 --workers 6 --chunk 100000 > 结果.json
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction
from math import comb
from multiprocessing import Pool

from gmpy2 import mpq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from route3_defs import (check_delta_anchor, constraint_rows, analytic_vertices,
                         v_vertex, canon_point, comb_unrank_lex, comb_next_lex,
                         point_code, agg_term, delta_lo, W_FROZEN)

MASK64 = (1 << 64) - 1


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# --------------------------------------------------------------- 精确消元

def solve_mpq(rows, rhs, n):
    """精确有理高斯若尔当（gmpy2.mpq，行主元）。返回唯一解（mpq 列表）或 None（奇异）。

    「某列在剩余行里全零 => 奇异」这一判据对求满秩解是正确的：此时行阶梯形剩余的
    子矩阵含零列，矩阵秩小于 n。
    """
    M = [[mpq(v) for v in row] + [mpq(rhs[i])] for i, row in enumerate(rows)]
    for col in range(n):
        piv = -1
        for i in range(col, n):
            if M[i][col] != 0:
                piv = i
                break
        if piv < 0:
            return None
        if piv != col:
            M[col], M[piv] = M[piv], M[col]
        Mc = M[col]
        pv = Mc[col]
        M[col] = [v / pv for v in Mc]
        Mc = M[col]
        for i in range(n):
            if i == col:
                continue
            f = M[i][col]
            if f == 0:
                continue
            Mi = M[i]
            M[i] = [Mi[j] - f * Mc[j] for j in range(n + 1)]
    return [M[i][n] for i in range(n)]


# ----------------------------------------------------------- 每子集判定

def judge_subset(S, cons, m2, pmq, qmq, wnum, wden):
    """对子集 S 做精确判定。

    返回 (kind, code, point_str, active_count)：
      kind = 'singular'（无唯一解）/ 'infeasible'（唯一解但不在 P 内）/ 'feasible'。
      code = 0（非候选）或 point_code(点串)（候选；与实现二同口径，用于分片对拍）。
    """
    rows = [cons[s][2] for s in S]
    rhs = [cons[s][3] for s in S]
    y = solve_mpq(rows, rhs, m2)
    if y is None:
        return "singular", 0, None, 0
    for j in range(m2):
        if y[j] < 1:                                   # C1
            return "infeasible", 0, None, 0
    for j in range(m2):
        if qmq * y[(j + 1) % m2] > pmq * y[j]:         # C2（含回绕）
            return "infeasible", 0, None, 0
    s = mpq(0)
    for j in range(m2):
        s += y[j]
    if wden * s < wnum:                                # C3
        return "infeasible", 0, None, 0
    act = 0
    for (kind, jj, row, brhs, label) in cons:
        val = mpq(0)
        for k in range(m2):
            rk = row[k]
            if rk:
                val += mpq(rk) * y[k]
        if val == brhs:
            act += 1
    ps = canon_point(y)
    return "feasible", point_code(ps), ps, act


# --------------------------------------------------------------- 分片工作

_G = {}


def worker_init(m2, p, q, wn, wd):
    _G["m2"] = m2
    _G["pmq"] = mpq(p)
    _G["qmq"] = mpq(q)
    _G["wnum"] = mpq(wn)
    _G["wden"] = mpq(wd)
    _G["cons"] = constraint_rows(m2, Fraction(p, q), Fraction(wn, wd))


def scan_block(task):
    """扫一个编号区间 [start, start+count)。返回分片统计字典。"""
    start, count = task
    m2 = _G["m2"]
    cons = _G["cons"]
    ncon = len(cons)
    t0 = time.time()
    S = comb_unrank_lex(ncon, m2, start)
    agg = 0
    n_sing = 0
    n_inf = 0
    cands = []
    for k in range(count):
        rank = start + k
        kind, code, ps, act = judge_subset(S, cons, m2, _G["pmq"], _G["qmq"],
                                           _G["wnum"], _G["wden"])
        if kind == "singular":
            n_sing += 1
        elif kind == "infeasible":
            n_inf += 1
        else:
            cands.append((rank, tuple(int(s) for s in S), ps, act))
        agg = (agg + agg_term(rank, code)) & MASK64
        if k + 1 < count:
            S = comb_next_lex(S, ncon)
            if S is None:
                raise RuntimeError("组合推进越界（分片区间超出总组合数）")
    return {
        "start": start,
        "count": count,
        "agg": f"{agg:016x}",
        "n_singular": n_sing,
        "n_infeasible_unique": n_inf,
        "n_candidates": len(cands),
        "candidates": cands,
        "sec": round(time.time() - t0, 3),
    }


# ------------------------------------------------------------------ 主流程

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m2", type=int, required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--chunk", type=int, default=100000)
    ap.add_argument("--no-anchor", action="store_true", help="跳过 δ 的整数幂锚点复核（快跑用）")
    ap.add_argument("--limit", type=int, default=0, help="只扫前 LIMIT 个子集（冒烟用）")
    args = ap.parse_args()

    m2 = args.m2
    delta = delta_lo(verify=not args.no_anchor)
    W = W_FROZEN
    p, q = delta.numerator, delta.denominator
    wn, wd = W.numerator, W.denominator
    ncon = 2 * m2 + 1
    total = comb(ncon, m2)
    todo = total if args.limit <= 0 else min(args.limit, total)

    tasks = []
    s = 0
    while s < todo:
        c = min(args.chunk, todo - s)
        tasks.append((s, c))
        s += c

    t_all = time.time()
    results = []
    with Pool(processes=args.workers, initializer=worker_init,
              initargs=(m2, p, q, wn, wd)) as pool:
        for r in pool.imap_unordered(scan_block, tasks, chunksize=1):
            results.append(r)
            log(f"  分片 [{r['start']}, {r['start']+r['count']}) 完成：奇异 {r['n_singular']}，"
                f"唯一解不可行 {r['n_infeasible_unique']}，候选 {r['n_candidates']}，"
                f"{r['sec']} s")
    elapsed = time.time() - t_all
    results.sort(key=lambda r: r["start"])

    agg = 0
    n_sing = 0
    n_inf = 0
    cands = []
    for r in results:
        agg = (agg + int(r["agg"], 16)) & MASK64
        n_sing += r["n_singular"]
        n_inf += r["n_infeasible_unique"]
        cands.extend(r["candidates"])

    ana = analytic_vertices(m2, delta, W)
    ana_str = {canon_point(y) for y in ana}
    cand_set = {c[2] for c in cands}
    v = v_vertex(m2, delta, W)

    out = {
        "impl": "route3-impl1-mpqscan",
        "m2": m2,
        "delta": f"{p}/{q}",
        "delta_anchor_line": check_delta_anchor() if not args.no_anchor else "（--no-anchor 跳过）",
        "W": f"{wn}/{wd}",
        "v": f"{v.numerator}/{v.denominator}",
        "total_subsets": total,
        "scanned_subsets": todo,
        "workers": args.workers,
        "chunk": args.chunk,
        "elapsed_sec": round(elapsed, 3),
        "n_singular": n_sing,
        "n_infeasible_unique": n_inf,
        "n_candidate_subsets": len(cands),
        "agg": f"{agg:016x}",
        "n_distinct_candidates": len(cand_set),
        "candidate_points_sorted": sorted(cand_set),
        "candidates": [
            {"rank": c[0], "subset": list(c[1]), "point": c[2], "active_count": c[3]}
            for c in sorted(cands, key=lambda z: z[0])
        ],
        "analytic_count": len(ana_str),
        "analytic_equal_candidate_set": (cand_set == ana_str),
        "analytic_only": sorted(ana_str - cand_set),
        "candidates_not_analytic": sorted(cand_set - ana_str),
        "blocks": results,
    }
    json.dump(out, sys.stdout, indent=1, ensure_ascii=False)
    sys.stdout.write("\n")
    log(json.dumps({k: out[k] for k in
                    ("m2", "total_subsets", "scanned_subsets", "elapsed_sec",
                     "n_singular", "n_infeasible_unique", "n_candidate_subsets",
                     "n_distinct_candidates", "analytic_count",
                     "analytic_equal_candidate_set", "agg")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
