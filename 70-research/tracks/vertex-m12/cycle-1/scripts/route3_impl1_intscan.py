#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route3_impl1_intscan.py —— route-3 实现一：整数无分数消元（Bareiss）全活跃子集穷举。

与项目既有实现的分工（独立性说明）：
  既有实现 r2_j_independent_vertices.py 的 full_enumeration 用 fractions.Fraction 做
  高斯若尔当消元、单进程、itertools.combinations 顺序枚举。本实现：
    1. 算术栈：系数整行放大后全程 gmpy2 整数；消元用 Bareiss 无分数消元（精确整除），
       回代用 gmpy2.mpq；可行性判定用精确有理比较，不用 Fraction；
    2. 枚举：自写的组合字典序编号与推进（route3_defs），按编号区间切成确定性分片，
       multiprocessing 多进程并行，每片给出 64 位校验和（可交换），用于不一致定位；
    3. 本实现**不 import r2_common**，也不 import r2_j_independent_vertices；只依赖
       route3_defs.py（自写，含约束表、可行性、解析族、组合编号）。

搜索本体不含任何结构剪枝：全部 C(2m2+1, m2) 个子集都过同一套精确消元与可行性判定。
允许枚举的完备性论证（初等线性代数，写在 route3_defs.py 文件头）：任一顶点处存在
大小 m2、秩 m2 的活跃子集；反之满秩子集的唯一解若可行必是顶点。

用法：
  python route3_impl1_intscan.py --m2 10 --workers 6 --chunk 100000 --out 结果文件名
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction
from math import comb
from multiprocessing import Pool

import gmpy2
from gmpy2 import mpz, mpq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from route3_defs import (check_delta_anchor, constraint_rows, analytic_vertices,
                         v_vertex, canon_point, comb_unrank_lex, comb_next_lex,
                         point_code, agg_term, delta_lo, W_FROZEN)

MASK64 = (1 << 64) - 1

# 输出位置：写死为本轨道 results 目录；--out 只接受纯文件名（无分隔符、无父目录记号）
RESULTS_DIR = ("/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/"
               "vertex-m12/cycle-1/results")
SAFE_NAME_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.+")
PARENT_MARKER = chr(46) * 2


def safe_result_path(name):
    """把 --out 的值限制为纯文件名并落在写死的 results 目录内。"""
    if not name or len(name) > 120:
        raise SystemExit("拒绝写入：输出名不合法")
    if any(ch not in SAFE_NAME_CHARS for ch in name):
        raise SystemExit("拒绝写入：输出名只允许字母数字与下划线、点、加号")
    if not name.endswith(".json"):
        raise SystemExit("拒绝写入：输出名须以 .json 结尾")
    if PARENT_MARKER in name or name.startswith(chr(46)):
        raise SystemExit("拒绝写入：输出名不得含父目录记号或以前导点开头")
    return os.path.join(RESULTS_DIR, name)


# --------------------------------------------------------------- 精确消元

def solve_bareiss(rows, rhs, n):
    """Bareiss 无分数消元 + 精确回代。返回唯一解（mpq 列表）或 None（奇异）。

    前向消元保持整数（Sylvester 恒等式保证整除），部分主元；右端同列一起变换。
    """
    M = [[mpz(v) for v in row] for row in rows]
    c = [mpz(v) for v in rhs]
    prev = mpz(1)
    for k in range(n):
        piv = -1
        for i in range(k, n):
            if M[i][k] != 0:
                piv = i
                break
        if piv < 0:
            return None                      # 该列以下全零 => 奇异
        if piv != k:
            M[k], M[piv] = M[piv], M[k]
            c[k], c[piv] = c[piv], c[k]
        pk = M[k][k]
        Mk = M[k]
        ck = c[k]
        for i in range(k + 1, n):
            f = M[i][k]
            if f == 0:
                continue
            Mi = M[i]
            M[i] = [(pk * Mi[j] - f * Mk[j]) // prev for j in range(n)]
            c[i] = (pk * c[i] - f * ck) // prev
        prev = pk
    x = [None] * n
    for i in range(n - 1, -1, -1):
        s = mpq(c[i])
        Ui = M[i]
        for j in range(i + 1, n):
            uij = Ui[j]
            if uij != 0:
                s -= mpq(uij) * x[j]
        x[i] = s / mpq(M[i][i])
    return x


def det_bareiss(rows, n):
    """整数行列式（Bareiss，部分主元，带符号）。返回 int。"""
    M = [[mpz(v) for v in row] for row in rows]
    prev = mpz(1)
    sign = 1
    for k in range(n):
        piv = -1
        for i in range(k, n):
            if M[i][k] != 0:
                piv = i
                break
        if piv < 0:
            return 0
        if piv != k:
            M[k], M[piv] = M[piv], M[k]
            sign = -sign
        pk = M[k][k]
        Mk = M[k]
        for i in range(k + 1, n):
            f = M[i][k]
            if f == 0:
                continue
            Mi = M[i]
            M[i] = [(pk * Mi[j] - f * Mk[j]) // prev for j in range(n)]
        prev = pk
    return int(sign * M[n - 1][n - 1])


# ----------------------------------------------------------- 每子集判定

def judge_subset(S, cons, m2, pq, wn, wd):
    """对子集 S 做精确判定。返回 (code, point_str 或 None, 活跃条数)。

    code = 0 表示该子集不给候选；否则 code = point_code(点串)（与实现二同口径）。
    """
    rows = [cons[s][2] for s in S]
    rhs = [cons[s][3] for s in S]
    y = solve_bareiss(rows, rhs, m2)
    if y is None:
        return 0, None, 0
    p, q = pq
    for j in range(m2):
        if y[j] < 1:                         # C1
            return 0, None, 0
    for j in range(m2):
        if mpq(q) * y[(j + 1) % m2] > mpq(p) * y[j]:    # C2（含回绕）
            return 0, None, 0
    s = mpq(0)
    for j in range(m2):
        s += y[j]
    if mpq(wd) * s < mpq(wn):                # C3
        return 0, None, 0
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
    return point_code(ps), ps, act


# --------------------------------------------------------------- 分片工作

_G = {}


def worker_init(m2, p, q, wn, wd):
    _G["m2"] = m2
    _G["pq"] = (p, q)
    _G["wn"] = wn
    _G["wd"] = wd
    _G["cons"] = constraint_rows(m2, Fraction(p, q), Fraction(wn, wd))


def scan_block(task):
    """扫一个编号区间 [start, start+count)。返回分片统计字典。"""
    start, count = task
    m2 = _G["m2"]
    pq = _G["pq"]
    wn, wd = _G["wn"], _G["wd"]
    cons = _G["cons"]
    ncon = len(cons)
    t0 = time.time()
    S = comb_unrank_lex(ncon, m2, start)
    agg = 0
    n_sing = 0
    n_non = 0
    cands = []
    for k in range(count):
        rank = start + k
        code, ps, act = judge_subset(S, cons, m2, pq, wn, wd)
        if ps is None:
            n_sing += 1
        else:
            n_non += 1
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
        "n_nonsingular": n_non,
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
    ap.add_argument("--out", type=str, required=True)
    ap.add_argument("--no-anchor", action="store_true", help="跳过 δ 的整数幂锚点复核（快跑用）")
    ap.add_argument("--limit", type=int, default=0, help="只扫前 LIMIT 个子集（冒烟用）")
    args = ap.parse_args()
    out_path = safe_result_path(args.out)

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
            print(f"  分片 [{r['start']}, {r['start']+r['count']}) 完成："
                  f"非奇异 {r['n_nonsingular']}，候选 {r['n_candidates']}，"
                  f"{r['sec']} s", flush=True)
    elapsed = time.time() - t_all
    results.sort(key=lambda r: r["start"])

    agg = 0
    n_sing = 0
    n_non = 0
    cands = []
    for r in results:
        agg = (agg + int(r["agg"], 16)) & MASK64
        n_sing += r["count"] - r["n_nonsingular"]
        n_non += r["n_nonsingular"]
        cands.extend(r["candidates"])

    ana = analytic_vertices(m2, delta, W)
    ana_str = {canon_point(y) for y in ana}
    cand_set = {c[2] for c in cands}
    v = v_vertex(m2, delta, W)

    out = {
        "impl": "route3-impl1-intscan-bareiss",
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
        "n_singular_or_infeasible": n_sing,
        "n_nonsingular": n_non,
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
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=False)
    print(json.dumps({k: out[k] for k in
                      ("m2", "total_subsets", "scanned_subsets", "elapsed_sec",
                       "n_singular_or_infeasible", "n_nonsingular", "n_candidate_subsets",
                       "n_distinct_candidates", "analytic_count",
                       "analytic_equal_candidate_set", "agg")}, ensure_ascii=False, indent=1))
    print(f"输出已写：{out_path}")


if __name__ == "__main__":
    main()
