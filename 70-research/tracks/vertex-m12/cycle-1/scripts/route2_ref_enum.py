#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route2 参考实现（Python 侧）：逐子集判定串 + 顶点清单，供与 C 主实现逐比特对拍。

用法（均在 scripts/ 目录下执行）：
  PY=/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
  "$PY" route2_ref_enum.py --m2 10 --range 0:352716 --out results/route2/py_m10_decisions.txt --verts results/route2/py_m10_vertices.txt
  "$PY" route2_ref_enum.py --m2 12 --range 1000000:1050000 --out results/route2/py_m12_slice1.bin

语义锚：frozen/r2_common.py（md5 cfee819667c0883e73732f03d2dc8bef，与
70-research/cycle-1/scripts/r2_common.py 逐字节一致）。判定语义与 C 主实现相同：
  'S' = 无唯一解（秩亏或不相容）；'I' = 有唯一解但不可行；'F' = 唯一解可行（顶点）。
输出与 C 主实现同格式的 VERTEX 行（coords、certs、active_count、active_rank）与
ANALYTIC 行，供 diff 对拍；另打印判定串的 md5 供直接比较。
"""
import argparse
import hashlib
import sys
import time
from fractions import Fraction
from itertools import combinations

FROZEN = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/vertex-m12/cycle-1/scripts/frozen"
sys.path.insert(0, FROZEN)
from r2_common import constraint_list, solve_exact, feasible, vertex  # noqa: E402


def rank_exact(rows, ncols):
    """精确秩（Fraction 行阶梯；本脚本自带，不 import 其它项目脚本）。"""
    M = [[Fraction(v) for v in r] for r in rows]
    rank = 0
    for col in range(ncols):
        piv = None
        for i in range(rank, len(M)):
            if M[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        pv = M[rank][col]
        for j in range(col, ncols):
            M[rank][j] = M[rank][j] / pv
        for i in range(len(M)):
            if i == rank or M[i][col] == 0:
                continue
            f = M[i][col]
            for j in range(col, ncols):
                M[i][j] = M[i][j] - f * M[rank][j]
        rank += 1
        if rank == len(M):
            break
    return rank


def active_cert(y, m2, d, W):
    """活跃约束集（取等的约束）的（条数，秩）。"""
    cons = constraint_list(m2, d, W)
    rows = []
    for a, b, _sense in cons:
        val = sum(a[j] * y[j] for j in range(m2))
        if val == b:
            rows.append(a)
    return len(rows), rank_exact(rows, m2)


def coords_key(y):
    return ";".join(f"{t.numerator}/{t.denominator}" for t in y)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m2", type=int, required=True)
    ap.add_argument("--P", type=int, default=126797)
    ap.add_argument("--Q", type=int, default=80000)
    ap.add_argument("--W", default="2000")
    ap.add_argument("--range", dest="rng", default=None, help="a:b（子集字典序下标，半开区间）")
    ap.add_argument("--out", required=True)
    ap.add_argument("--verts", default=None)
    ap.add_argument("--progress", type=int, default=100000)
    args = ap.parse_args()

    m2 = args.m2
    d = Fraction(args.P, args.Q)
    W = Fraction(args.W)
    cons = constraint_list(m2, d, W)
    n = len(cons)
    total = 1
    for i in range(m2):
        total = total * (n - i) // (i + 1)
    if args.rng:
        a, b = (int(x) for x in args.rng.split(":"))
        a = max(0, a)
        b = min(total, b)
    else:
        a, b = 0, total

    print(f"[route2_ref_enum] m2={m2} delta={args.P}/{args.Q} W={W} "
          f"N={n} TOTAL={total} RANGE=[{a},{b})", flush=True)
    t0 = time.time()
    dec = bytearray()
    verts = {}  # key -> {"y": tuple, "certs": [ (idx, S) ]}
    cnt = {"S": 0, "I": 0, "F": 0}
    for idx, S in enumerate(combinations(range(n), m2)):
        if idx < a:
            continue
        if idx >= b:
            break
        rows = [cons[i][0] for i in S]
        bs = [cons[i][1] for i in S]
        sol, rank = solve_exact(rows, bs)
        if sol is None or rank < m2:
            ch = "S"
        else:
            ok, _bad = feasible(sol, m2, d, W)
            ch = "F" if ok else "I"
        cnt[ch] += 1
        dec.append(ord(ch))
        if ch == "F":
            y = tuple(sol)
            k = coords_key(y)
            rec = verts.setdefault(k, {"y": y, "certs": []})
            rec["certs"].append((idx, S))
        if args.progress and (idx - a) % args.progress == 0 and idx > a:
            print(f"    ... {idx}/{b}（{time.time()-t0:.0f} s）", flush=True)
    dt = time.time() - t0

    with open(args.out, "wb") as f:
        f.write(bytes(dec))
    md5 = hashlib.md5(bytes(dec)).hexdigest()
    print(f"DECISION_COUNTS S={cnt['S']} I={cnt['I']} F={cnt['F']} total={sum(cnt.values())}")
    print(f"DECISIONS_FILE {args.out} bytes={len(dec)}")
    print(f"DECISIONS_MD5 {md5}")
    print(f"ELAPSED_SEC {dt:.1f}")

    # 解析集
    analytic = {}
    for r in range(m2):
        vy = tuple(vertex(m2, d, W, r))
        analytic[coords_key(vy)] = vy
    print(f"ANALYTIC_COUNT {len(analytic)} VERTEX_COUNT {len(verts)} "
          f"SETS_EQUAL {set(analytic.keys()) == set(verts.keys())}")

    if args.verts:
        with open(args.verts, "w") as f:
            f.write(f"# route2 Python 参考顶点清单 m2={m2} delta={args.P}/{args.Q} W={W} "
                    f"range=[{a},{b})\n")
            for g, k in enumerate(sorted(verts.keys())):
                rec = verts[k]
                y = rec["y"]
                f.write(f"VERTEX {g} coords={k}\n")
                certs_sorted = sorted(rec["certs"], key=lambda t: t[0])
                f.write(f"VERTEX {g} certs={len(certs_sorted)} cert_subset_idxs=")
                f.write(",".join(f"{i}[" + ",".join(str(x) for x in S) + "]"
                                 for i, S in certs_sorted))
                f.write("\n")
                nact, rk = active_cert(y, m2, d, W)
                f.write(f"VERTEX {g} active_count={nact} active_rank={rk}\n")
        print(f"VERTS_FILE {args.verts}")
    print("EXIT_OK")


if __name__ == "__main__":
    main()
