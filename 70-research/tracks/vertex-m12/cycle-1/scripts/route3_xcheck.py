#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route3_xcheck.py —— route-3 两实现对拍器（逐子集 + 逐分块 + 结果文件）。

三种模式：
  1. --mode allsubsets --m2 K
     对 m2 = K 的全部 C(2K+1, K) 个子集，逐项比较实现一（mpq 消元）与实现二（结构传播）
     的判定：kind、候选点串、判定码。不一致时打印编号、子集内容与两边判定（定位到编号）。
     用途：小 m2 的强对拍（证明两实现在该档完全一致）。
  2. --mode json --a 文件A --b 文件B
     比较两份结果 JSON：总校验和、每分块校验和（不一致时报出分块区间）、候选子集编号
     列表与候选点集合（不一致时报出差集）。用途：m2 = 12 及以上分块全扫的对拍。
  3. --mode block --m2 K --lo L --hi H
     只对编号区间 [L, H) 做模式 1 的逐子集对拍（大档定位用）。

本文件只读 JSON 与打印，不写任何文件。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction
from route3_defs import (constraint_rows, delta_lo, W_FROZEN, analytic_vertices,
                         canon_point, comb_unrank_lex, comb_next_lex, point_code)
import route3_impl1_mpqscan as I1
import route3_impl2_struct as I2


def compare_subsets(m2, lo, hi):
    delta = delta_lo(verify=False)
    W = W_FROZEN
    p, q = delta.numerator, delta.denominator
    wn, wd = W.numerator, W.denominator
    ncon = 2 * m2 + 1
    cons = constraint_rows(m2, delta, W)
    pmq = I1.mpq(p)
    qmq = I1.mpq(q)
    dpow = [delta ** k for k in range(-m2, m2 + 1)]
    S = comb_unrank_lex(ncon, m2, lo)
    n_mismatch = 0
    n_cand1 = 0
    n_cand2 = 0
    first = []
    for rank in range(lo, hi):
        St = tuple(S)
        k1, c1, p1, a1 = I1.judge_subset(St, cons, m2, pmq, qmq, I1.mpq(wn), I1.mpq(wd))
        k2, c2, p2, a2, _fr = I2.judge_struct(St, m2, dpow, p, q, wn, wd, None)
        if p1 is not None:
            n_cand1 += 1
        if p2 is not None:
            n_cand2 += 1
        ok = (p1 == p2) and (c1 == c2)
        if not ok:
            n_mismatch += 1
            if len(first) < 5:
                first.append((rank, list(St), (k1, p1), (k2, p2)))
        if rank + 1 < hi:
            S = comb_next_lex(S, ncon)
            if S is None:
                raise SystemExit("区间越界")
    return {
        "m2": m2, "lo": lo, "hi": hi, "n_compare": hi - lo,
        "n_mismatch": n_mismatch, "n_candidates_impl1": n_cand1,
        "n_candidates_impl2": n_cand2, "first_mismatches": first,
    }


def compare_json(a_path, b_path):
    with open(a_path) as fh:
        A = json.load(fh)
    with open(b_path) as fh:
        B = json.load(fh)
    rep = {"a_impl": A.get("impl"), "b_impl": B.get("impl")}
    rep["m2_equal"] = (A["m2"] == B["m2"])
    rep["total_subsets_equal"] = (A["total_subsets"] == B["total_subsets"])
    rep["scanned_subsets_equal"] = (A["scanned_subsets"] == B["scanned_subsets"])
    rep["agg_equal"] = (A["agg"] == B["agg"])
    rep["agg"] = {"a": A["agg"], "b": B["agg"]}
    rep["n_candidate_subsets"] = {"a": A["n_candidate_subsets"], "b": B["n_candidate_subsets"]}
    ca = {c["point"] for c in A["candidates"]}
    cb = {c["point"] for c in B["candidates"]}
    rep["candidate_point_sets_equal"] = (ca == cb)
    if ca != cb:
        rep["points_only_in_a"] = sorted(ca - cb)[:5]
        rep["points_only_in_b"] = sorted(cb - ca)[:5]
    ka = [c["rank"] for c in A["candidates"]]
    kb = [c["rank"] for c in B["candidates"]]
    rep["candidate_ranks_equal"] = (ka == kb)
    if ka != kb:
        rep["ranks_only_in_a"] = sorted(set(ka) - set(kb))[:10]
        rep["ranks_only_in_b"] = sorted(set(kb) - set(ka))[:10]
    bl = {}
    for r in A.get("blocks", []):
        bl[(r["start"], r["count"])] = r.get("agg")
    bad_blocks = []
    for r in B.get("blocks", []):
        key = (r["start"], r["count"])
        if key not in bl:
            bad_blocks.append((key, "missing_in_a", None, r.get("agg")))
        elif bl[key] != r.get("agg"):
            bad_blocks.append((key, "agg_mismatch", bl[key], r.get("agg")))
    for key in bl:
        if all(key != (r["start"], r["count"]) for r in B.get("blocks", [])):
            bad_blocks.append((key, "missing_in_b", bl[key], None))
    rep["n_blocks_a"] = len(A.get("blocks", []))
    rep["n_blocks_b"] = len(B.get("blocks", []))
    rep["blocks_with_agg_mismatch"] = bad_blocks[:10]
    rep["n_blocks_with_agg_mismatch"] = len(bad_blocks)
    # 逐候选活跃条数对照
    ma = {c["point"]: c.get("active_count") for c in A["candidates"]}
    mb = {c["point"]: c.get("active_count") for c in B["candidates"]}
    rep["active_count_equal"] = (ma == mb)
    rep["active_count_table"] = {k: [ma.get(k), mb.get(k)] for k in sorted(set(ma) | set(mb))}
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["allsubsets", "json", "block"], required=True)
    ap.add_argument("--m2", type=int, default=0)
    ap.add_argument("--lo", type=int, default=0)
    ap.add_argument("--hi", type=int, default=0)
    ap.add_argument("--a", type=str, default="")
    ap.add_argument("--b", type=str, default="")
    args = ap.parse_args()

    if args.mode == "json":
        rep = compare_json(args.a, args.b)
    else:
        m2 = args.m2
        ncon = 2 * m2 + 1
        from math import comb
        total = comb(ncon, m2)
        hi = args.hi if args.hi > 0 else total
        rep = compare_subsets(m2, args.lo, hi)
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
