#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route3_impl2_struct.py —— route-3 实现二：结构传播式全活跃子集穷举（算法上与实现一不同）。

算法（每条都附初等证明要点；搜索本体不做任何剪枝，全部 C(2m2+1, m2) 个子集都走这条路）：

  设子集 S 拆成三部分：C1 行集合 A1（y_j = 1）、C2 行集合 A2（y_{j+1} = δ y_j，指标模 m2）、
  是否含 C3 行（Σ y = W）。把「j ∈ A2」看成有向边 j -> j+1（每个节点出度至多 1），则

  1. 若 |A2| = m2（整圈都在），链方程绕一圈得 y_1 = δ^{m2} y_1，δ > 1 故 y = 0；
     0 违反 y_j >= 1（有 C1 行时还与 y_j = 1 冲突），故这种子集绝不产候选。
  2. 若 |A2| < m2，去掉 |A2| 条边后整圈碎成 m2 − |A2| 条互不相交的有向路径（称分量）。
     分量内 y 由「基点」一个自由参数决定：距基点 t 步的节点取 δ^t 倍。
  3. 分量含 0 个 C1 节点 => 该分量留一个自由度；含 1 个 => 基点被钉死（基点值 = δ^{−d}，
     d 为钉点到基点的距离）；含 >= 2 个 => 两式给出 δ^{d1} = δ^{d2}（d1 != d2），
     与 δ > 1 矛盾 => 方程组不相容。
  4. 记 f = 自由度个数（无 C1 钉的分量数）。则链部分解空间维数 = f，
     方程组系数秩 = m2 − f。
     (a) 不含 C3 行：唯一解 <=> f = 0；
     (b) 含 C3 行：和泛函在自由分量上的系数是 Σ δ^t > 0（δ > 0），故和方程必把维数降 1
         => 唯一解 <=> f = 1；f = 0 时和方程是相容性条件，须精确验 Σ y = W。
     f >= 2 时含 C3 也只有 >= 1 维解空间，弃。
  5. 唯一解算出后，用精确有理数验全部 2m2+1 条约束；全部满足即候选，并附（活跃条数，
     该子集系数矩阵秩 = m2）两张证书。

与实现一的差异（交叉核验的意义）：实现一走 gmpy2.mpq 线性方程组消元（通用线性代数），
本实现走图结构传播（每条约束只被读一次），两者的判定路径、运算符、早退点都不同；
分片方式、组合编号、判定码与校验和口径两者一致，故可按子集编号逐项对拍。
本文件不 import r2_common，也不 import r2_j_independent_vertices；只依赖 route3_defs.py。

输出约定：进度与摘要走 stderr，完整结果 JSON 走 stdout（落盘靠命令行重定向）。

用法：
  python route3_impl2_struct.py --m2 12 --workers 6 --chunk 100000 > 结果.json
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction
from math import comb
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from route3_defs import (check_delta_anchor, analytic_vertices, v_vertex, canon_point,
                         comb_unrank_lex, comb_next_lex, point_code, agg_term,
                         rank_fraction, constraint_rows, delta_lo, delta_hi, W_FROZEN)

MASK64 = (1 << 64) - 1


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ------------------------------------------------- 本实现自己的精确可行性判定

def feasible_own(y, m2, p, q, wn, wd):
    """用整数交叉相乘与 Fraction 求和做精确可行性判定（与实现一的判定写法不同）。"""
    for j in range(m2):
        if y[j] < 1:
            return False
    for j in range(m2):
        a = y[(j + 1) % m2]
        b = y[j]
        if q * a.numerator * b.denominator > p * b.numerator * a.denominator:
            return False
    tot = Fraction(0)
    for j in range(m2):
        tot += y[j]
    return tot >= Fraction(wn, wd)


def judge_struct(S, m2, dpow, p, q, wn, wd, cons=None):
    """结构传播判定。返回 (kind, code, point_str, active_count, subset_full_rank)。

    kind: 'nocand'（出局）/ 'feasible'。code 口径与实现一相同（候选给点码，否则 0）。
    """
    A1 = 0
    A2 = 0
    a3 = False
    for s in S:
        if s < m2:
            A1 |= 1 << s
        elif s < 2 * m2:
            A2 |= 1 << (s - m2)
        else:
            a3 = True

    # 分量划分（起点 = 入边缺失的节点）
    comps = []
    for j in range(m2):
        if not (A2 >> ((j - 1) % m2)) & 1:
            nodes = [j]
            cur = j
            while (A2 >> cur) & 1:
                cur = (cur + 1) % m2
                nodes.append(cur)
            comps.append(nodes)
    if not comps:
        return "nocand", 0, None, 0, False       # |A2| = m2：链方程强推 y = 0

    # dpow 表的下标约定：dpow[k + m2] 表示 δ^k，k 取 −m2..m2
    def dq(k):
        return dpow[k + m2]

    sum_const = Fraction(0)
    free = []
    for nodes in comps:
        pins = [t for t in range(len(nodes)) if (A1 >> nodes[t]) & 1]
        if len(pins) > 1:
            return "nocand", 0, None, 0, False   # 同分量两个钉：δ 幂相等而指数不同
        if len(pins) == 1:
            d = pins[0]
            for t in range(len(nodes)):
                sum_const += dq(t - d)
        else:
            free.append(nodes)

    y = [None] * m2
    if a3:
        if len(free) == 1:
            nodes = free[0]
            c = Fraction(0)
            for t in range(len(nodes)):
                c += dq(t)
            base = (Fraction(wn, wd) - sum_const) / c      # 自由基点取值
            for t in range(len(nodes)):
                y[nodes[t]] = dq(t) * base
        elif len(free) != 0:
            return "nocand", 0, None, 0, False
    elif len(free) != 0:
        return "nocand", 0, None, 0, False

    # 钉住分量的坐标
    for nodes in comps:
        pins = [t for t in range(len(nodes)) if (A1 >> nodes[t]) & 1]
        if len(pins) == 1:
            d = pins[0]
            for t in range(len(nodes)):
                if y[nodes[t]] is None:
                    y[nodes[t]] = dq(t - d)

    if any(v is None for v in y):
        return "nocand", 0, None, 0, False

    if a3:
        tot = Fraction(0)
        for v in y:
            tot += v
        if tot != Fraction(wn, wd):
            return "nocand", 0, None, 0, False              # 相容性条件不满足

    if not feasible_own(y, m2, p, q, wn, wd):
        return "nocand", 0, None, 0, False

    act = 0
    if cons is None:
        cons = constraint_rows(m2, Fraction(p, q), Fraction(wn, wd))
    for (kind, jj, row, brhs, label) in cons:
        val = Fraction(0)
        for k in range(m2):
            rk = row[k]
            if rk:
                val += Fraction(rk) * y[k]
        if val == brhs:
            act += 1
    ps = canon_point(y)
    return "feasible", point_code(ps), ps, act, True


# --------------------------------------------------------------- 分片工作

_G = {}


def worker_init(m2, p, q, wn, wd):
    _G["m2"] = m2
    _G["p"] = p
    _G["q"] = q
    _G["wn"] = wn
    _G["wd"] = wd
    d = Fraction(p, q)
    _G["dpow"] = [d ** k for k in range(-m2, m2 + 1)]     # 下标 k + m2
    _G["cons"] = constraint_rows(m2, d, Fraction(wn, wd))


def scan_block(task):
    start, count = task
    m2 = _G["m2"]
    dpow = _G["dpow"]
    ncon = 2 * m2 + 1
    t0 = time.time()
    S = comb_unrank_lex(ncon, m2, start)
    agg = 0
    cands = []
    for k in range(count):
        rank = start + k
        S_t = tuple(S)
        kind, code, ps, act, _fr = judge_struct(
            S_t, m2, dpow, _G["p"], _G["q"], _G["wn"], _G["wd"], None)
        agg = (agg + agg_term(rank, code)) & MASK64
        if kind == "feasible":
            cands.append((rank, tuple(int(s) for s in S_t), ps, act))
        if k + 1 < count:
            S = comb_next_lex(S, ncon)
            if S is None:
                raise RuntimeError("组合推进越界（分片区间超出总组合数）")
    return {
        "start": start,
        "count": count,
        "agg": f"{agg:016x}",
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
    ap.add_argument("--delta", choices=["lo", "hi"], default="lo",
                    help="δ 取严格下界（默认，126797/80000）或严格上界（7924813/5000000）")
    args = ap.parse_args()

    m2 = args.m2
    delta = (delta_lo if args.delta == "lo" else delta_hi)(verify=not args.no_anchor)
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
            log(f"  分片 [{r['start']}, {r['start']+r['count']}) 完成："
                f"候选 {r['n_candidates']}，{r['sec']} s")
    elapsed = time.time() - t_all
    results.sort(key=lambda r: r["start"])

    agg = 0
    cands = []
    for r in results:
        agg = (agg + int(r["agg"], 16)) & MASK64
        cands.extend(r["candidates"])

    # 候选证书独立复核（本实现内）：该子集系数矩阵秩应 = m2（列满秩）
    cons = constraint_rows(m2, delta, W)
    certs = {}
    for (rk, sub, ps, act) in cands:
        rows = [cons[s][2] for s in sub]
        rr = rank_fraction(rows, m2)
        certs[rk] = rr
    bad_cert = [rk for rk, rr in certs.items() if rr != m2]

    ana = analytic_vertices(m2, delta, W)
    ana_str = {canon_point(y) for y in ana}
    cand_set = {c[2] for c in cands}
    v = v_vertex(m2, delta, W)

    out = {
        "impl": "route3-impl2-structural",
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
        "n_candidate_subsets": len(cands),
        "agg": f"{agg:016x}",
        "n_distinct_candidates": len(cand_set),
        "candidate_points_sorted": sorted(cand_set),
        "candidates": [
            {"rank": c[0], "subset": list(c[1]), "point": c[2], "active_count": c[3],
             "witness_rank": certs[c[0]]}
            for c in sorted(cands, key=lambda z: z[0])
        ],
        "candidates_with_wrong_rank": bad_cert,
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
                     "n_candidate_subsets", "n_distinct_candidates", "analytic_count",
                     "analytic_equal_candidate_set", "candidates_with_wrong_rank", "agg")},
                   ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
