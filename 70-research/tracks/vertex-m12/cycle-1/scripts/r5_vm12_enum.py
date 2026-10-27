#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r5_vm12_enum.py —— vertex-m12 轨道路线五：八核全活跃子集穷举（可复跑、可断点续跑）。

语义（与 70-research/cycle-1/scripts/r2_j_independent_vertices.py 的 A 段逐字同义）：
  对给定 (m2, δ, W)，枚举全部 C(2m2+1, m2) 个大小 m2 的活跃约束子集；
  每个子集：精确解线性方程组（Fraction 或 gmpy2.mpq），秩亏/不相容则弃；
  满秩则查精确可行性（C1: y_j>=1；C2 循环链含回绕: y_{j+1}<=δy_j；C3: Σy>=W）；
  可行解按坐标元组去重收集；最后与解析族（v·δ^r 的 m2 个循环旋转）做集合相等判定。

依赖清单（"不依赖任何引理"落成显式清单；见 route-5.md 第 2 节）：
  数学侧：约束表逐字转写（r2_common.constraint_list）、精确有理算术（fractions/gmpy2）、
          组合枚举完备性、顶点当且仅当活跃约束法向量满秩（初等线性代数）。
  代码侧：r2_common.{delta_rigorous_bounds, constraint_list, solve_exact, feasible,
          v_vertex, vertex}（运行时断言 md5 = cfee819667c0883e73732f03d2dc8bef）。
  禁止侧：任何 (L1)、v 的数值信息、凸性论证、顶点引理的结论——搜索本体一概不用；
          v 只用于构造被检验的"解析族"对照集，不参与搜索判定。

分片：按组合字典序下标 [start, end) 切成 --chunks 个连续区间（deterministic，无重无漏）；
      父进程校验 Σ(end-start) = C(2m2+1, m2) 且各 worker 计数之和等于同一值。
断点续跑：每片结果落 results/ckpt/<tag>/chunk_%04d.json；--resume 时复用已有分片。
"""
import argparse
import hashlib
import itertools
import json
import math
import os
import platform
import resource
import sys
import time
from fractions import Fraction

REF_SCRIPTS = "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts"
MD5_R2_COMMON = "cfee819667c0883e73732f03d2dc8bef"
MD5_R2_J = "4b8ce2a500d8ca9021fd0178deca637e"
CKPT_ROOT = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/vertex-m12/cycle-1/results/ckpt"


def file_md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 16), b""):
            h.update(blk)
    return h.hexdigest()


sys.path.insert(0, REF_SCRIPTS)
import gmpy2  # noqa: E402
from r2_common import (delta_rigorous_bounds, constraint_list, solve_exact,  # noqa: E402
                       feasible, v_vertex, vertex)


def check_pins():
    m1 = file_md5(os.path.join(REF_SCRIPTS, "r2_common.py"))
    m2 = file_md5(os.path.join(REF_SCRIPTS, "r2_j_independent_vertices.py"))
    ok = (m1 == MD5_R2_COMMON and m2 == MD5_R2_J)
    return ok, m1, m2


def rank_exact(rows, ncols):
    """精确秩（Fraction 行阶梯）。与 r2_j_independent_vertices.py 的同名函数逐行同义。"""
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
        M[rank] = [v / pv for v in M[rank]]
        for i in range(len(M)):
            if i != rank and M[i][col] != 0:
                f = M[i][col]
                M[i] = [M[i][j] - f * M[rank][j] for j in range(ncols)]
        rank += 1
    return rank


def active_rank(y, m2, d, W):
    """点 y 处活跃约束的法向量集的秩（= m2 即为顶点的秩证书）。"""
    cons = constraint_list(m2, d, W)
    rows = []
    for a, b, sense in cons:
        val = sum(a[j] * y[j] for j in range(m2))
        if val == b:
            rows.append(a)
    return rank_exact(rows, m2), len(rows)


# ------------------------------------------------------------------ mpq 镜像实现

def solve_exact_mpq(A, b):
    """r2_common.solve_exact 的 gmpy2.mpq 镜像（逐行同义；A、b 为 mpq/int）。"""
    n = len(A)
    m = len(A[0])
    M = [list(A[i]) + [b[i]] for i in range(n)]
    rank = 0
    pivots = []
    for col in range(m):
        piv = None
        for i in range(rank, n):
            if M[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        pv = M[rank][col]
        M[rank] = [v / pv for v in M[rank]]
        for i in range(n):
            if i != rank and M[i][col] != 0:
                f = M[i][col]
                M[i] = [M[i][j] - f * M[rank][j] for j in range(m + 1)]
        pivots.append(col)
        rank += 1
        if rank == n:
            break
    for i in range(rank, n):
        if all(M[i][j] == 0 for j in range(m)) and M[i][m] != 0:
            return None, rank
    if rank < m:
        return None, rank
    sol = [gmpy2.mpq(0)] * m
    for i, col in enumerate(pivots):
        sol[col] = M[i][m]
    return sol, rank


def feasible_mpq(y, m2, d, W):
    """r2_common.feasible 的 mpq 镜像（返回 bool；判定方向同 frozen 版）。"""
    for j in range(m2):
        if y[j] < 1:
            return False
    for j in range(m2):
        if y[(j + 1) % m2] > d * y[j]:
            return False
    s = gmpy2.mpq(0)
    for t in y:
        s += t
    return not (s < W)


# ------------------------------------------------------------------ 单核/并行核心

_G = {}


def _init_worker(m2, d_str, W_str, impl, n, cons_rows, cons_b):
    d = Fraction(d_str)
    W = Fraction(W_str)
    _G["m2"] = m2
    _G["d"] = d
    _G["W"] = W
    _G["n"] = n
    _G["impl"] = impl
    _G["rows"] = cons_rows
    _G["b"] = cons_b
    if impl == "fraction":
        _G["rows"] = [list(A) for A in cons_rows]
        _G["b"] = [Fraction(x) for x in cons_b]
    else:
        _G["rows"] = [[gmpy2.mpq(fr.numerator, fr.denominator) for fr in A] for A in cons_rows]
        _G["b"] = [gmpy2.mpq(fr.numerator, fr.denominator) for fr in cons_b]


def process_range(start, end):
    """处理组合字典序下标区间 [start, end)；返回可 JSON 化的结果。"""
    m2 = _G["m2"]
    d = _G["d"]
    W = _G["W"]
    n = _G["n"]
    impl = _G["impl"]
    rows = _G["rows"]
    b = _G["b"]
    combs = itertools.combinations(range(n), m2)
    it = itertools.islice(combs, start, end)
    cnt = 0
    n_rd = 0
    n_infeas = 0
    feas = {}
    first = None
    last = None
    t0 = time.time()
    for S in it:
        cnt += 1
        if first is None:
            first = S
        last = S
        if impl == "fraction":
            sol, rank = solve_exact([rows[i] for i in S], [b[i] for i in S])
            if sol is None or rank < m2:
                n_rd += 1
                continue
            ok, _ = feasible(sol, m2, d, W)
        else:
            sol, rank = solve_exact_mpq([rows[i] for i in S], [b[i] for i in S])
            if sol is None or rank < m2:
                n_rd += 1
                continue
            ok = feasible_mpq(sol, m2, d, W)
        if not ok:
            n_infeas += 1
            continue
        key = ",".join(str(Fraction(t)) if impl == "fraction" else str(t) for t in sol)
        rec = feas.get(key)
        if rec is None:
            feas[key] = {"count": 1, "examples": [[int(i) for i in S]]}
        else:
            rec["count"] += 1
            if len(rec["examples"]) < 3:
                rec["examples"].append([int(i) for i in S])
    return {
        "start": start, "end": end, "count": cnt,
        "n_rank_def": n_rd, "n_infeasible": n_infeas,
        "feasible": feas,
        "first": list(first) if first else None,
        "last": list(last) if last else None,
        "sec": round(time.time() - t0, 3),
    }


def _pool_worker(args):
    cid, start, end = args
    res = process_range(start, end)
    res["chunk"] = cid
    return res


def _wcpu():
    ru = resource.getrusage(resource.RUSAGE_SELF)
    rc = resource.getrusage(resource.RUSAGE_CHILDREN)
    return ru.ru_utime + ru.ru_stime + rc.ru_utime + rc.ru_stime


def make_chunks(total, nchunks):
    bounds = [total * i // nchunks for i in range(nchunks + 1)]
    out = []
    for i in range(nchunks):
        if bounds[i] < bounds[i + 1]:
            out.append((i, bounds[i], bounds[i + 1]))
    return out


def run_full(args, d, W, total):
    m2 = args.m2
    chunks = make_chunks(total, args.chunks)
    ck = os.path.join(CKPT_ROOT, args.tag)
    os.makedirs(ck, exist_ok=True)
    results = [None] * len(chunks)
    todo = []
    for cid, start, end in chunks:
        path = os.path.join(ck, f"chunk_{cid:04d}.json")
        if args.resume and os.path.exists(path):
            with open(path) as fh:
                results[cid] = json.load(fh)
            print(f"      ... 复用分片 {cid} [{start},{end})", flush=True)
        else:
            todo.append((cid, start, end))
    assert sum(e - s for _c, s, e in chunks) == total, "分片覆盖必须等于组合总数"
    t0 = time.time()
    if todo:
        from multiprocessing import Pool
        if args.interleave:
            # 成本沿字典序单调上升，故按下标两端交替派发（cheap 分片与 expensive 分片配对），
            # 降低「后半程拖尾」的墙钟；只改派发顺序，不改分片内容与覆盖。
            reordered = []
            lo, hi = 0, len(todo) - 1
            while lo <= hi:
                reordered.append(todo[lo])
                if lo != hi:
                    reordered.append(todo[hi])
                lo += 1
                hi -= 1
            todo = reordered
        cons = constraint_list(m2, d, W)
        cons_rows = [c[0] for c in cons]
        cons_b = [c[1] for c in cons]
        with Pool(args.workers, initializer=_init_worker,
                  initargs=(m2, str(d), str(W), args.impl, 2 * m2 + 1, cons_rows, cons_b)) as pool:
            for res in pool.imap_unordered(_pool_worker, todo):
                cid = res["chunk"]
                results[cid] = res
                with open(os.path.join(ck, f"chunk_{cid:04d}.json"), "w") as fh:
                    json.dump(res, fh)
                print(f"      ... 分片 {cid} 完成 [{res['start']},{res['end']}) "
                      f"count={res['count']} {res['sec']} s（累计墙钟 {time.time()-t0:.0f} s）", flush=True)
    wall = time.time() - t0
    return results, wall


def aggregate(results, total):
    cnt = sum(r["count"] for r in results)
    n_rd = sum(r["n_rank_def"] for r in results)
    n_if = sum(r["n_infeasible"] for r in results)
    feas = {}
    for r in results:
        for k, rec in r["feasible"].items():
            cur = feas.get(k)
            if cur is None:
                feas[k] = {"count": rec["count"], "examples": list(rec["examples"])}
            else:
                cur["count"] += rec["count"]
                for ex in rec["examples"]:
                    if len(cur["examples"]) < 3:
                        cur["examples"].append(ex)
    return cnt, n_rd, n_if, feas


def fmt_frac(fr):
    return str(fr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m2", type=int, required=True)
    ap.add_argument("--delta", default=None, help="默认取 δ 的严格下界（该档 10^7 分数）")
    ap.add_argument("--W", default="2000", help="精确分数串，或 threshold（=(δ^m2−1)/(δ−1)）")
    ap.add_argument("--impl", default="fraction", choices=["fraction", "mpq"])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--chunks", type=int, default=None)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--interleave", action="store_true",
                    help="按下标两端交替派发分片（成本沿序上升时的墙钟均衡；不改覆盖）")
    ap.add_argument("--probe", type=int, default=0, help="只跑前 N 个子集做测速（单进程）")
    ap.add_argument("--dump-sample", type=int, default=0, help="输出 N 个子集逐条状态的样本（三段窗口）")
    ap.add_argument("--out-sample", default=None)
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    ok, m1, m2h = check_pins()
    m2 = args.m2
    n = 2 * m2 + 1
    if args.delta is None:
        d_lo, _d_hi = delta_rigorous_bounds(10 ** 7)
        d = d_lo
        delta_src = "δ 的严格下界（delta_rigorous_bounds(10**7)）"
    else:
        d = Fraction(args.delta)
        delta_src = "命令行给定"
    if args.W == "threshold":
        W = (d ** m2 - 1) / (d - 1)
        W_src = "阈值 (δ^m2−1)/(δ−1)"
    else:
        W = Fraction(args.W)
        W_src = "命令行给定"
    total = math.comb(n, m2)
    tag = args.tag or f"m2_{m2}_impl_{args.impl}"

    print("=" * 78)
    print(f"r5_vm12_enum.py  m2={m2}  impl={args.impl}  tag={tag}")
    print(f"δ = {fmt_frac(d)}（{delta_src}）  W = {fmt_frac(W)}（{W_src}）")
    print(f"组合数 C({n},{m2}) = {total}")
    print(f"v = W(δ−1)/(δ^{m2}−1) = {fmt_frac(v_vertex(m2, d, W))}")
    print(f"脚本 md5 = {file_md5(os.path.abspath(__file__))}")
    print(f"r2_common.py md5 = {m1}（期望 {MD5_R2_COMMON}；一致 = {m1 == MD5_R2_COMMON}）")
    print(f"r2_j_independent_vertices.py md5 = {m2h}（期望 {MD5_R2_J}；一致 = {m2h == MD5_R2_J}）")
    print(f"python {sys.version.split()[0]} / {platform.platform()}")
    print(f"note: {args.note}")
    if not ok:
        print("！！ md5 预钉不一致，按纪律中止（避免上游漂移）", flush=True)
        sys.exit(2)

    cons = constraint_list(m2, d, W)
    cons_rows = [c[0] for c in cons]
    cons_b = [c[1] for c in cons]

    if args.dump_sample:
        K = args.dump_sample
        third = max(1, K // 3)
        windows = [(0, min(third, total))]
        mid = max(0, total // 2 - third // 2)
        windows.append((mid, min(mid + third, total)))
        windows.append((max(0, total - third), total))
        _init_worker(m2, str(d), str(W), args.impl, n, cons_rows, cons_b)
        lines = []
        for (a, b) in windows:
            it = itertools.islice(itertools.combinations(range(n), m2), a, b)
            for offset, S in enumerate(it):
                i = a + offset
                if args.impl == "fraction":
                    sol, rank = solve_exact([_G["rows"][t] for t in S], [_G["b"][t] for t in S])
                    if sol is None or rank < m2:
                        status = f"rankdef rank={rank}"
                    else:
                        okf, _ = feasible(sol, m2, d, W)
                        status = ("feasible " + ",".join(str(x) for x in sol)) if okf else "infeasible"
                else:
                    sol, rank = solve_exact_mpq([_G["rows"][t] for t in S], [_G["b"][t] for t in S])
                    if sol is None or rank < m2:
                        status = f"rankdef rank={rank}"
                    else:
                        okf = feasible_mpq(sol, m2, d, W)
                        status = ("feasible " + ",".join(str(Fraction(t.numerator, t.denominator)) for t in sol)) if okf else "infeasible"
                lines.append(f"IDX {i} S={list(S)} {status}")
        if args.out_sample:
            with open(args.out_sample, "w") as fh:
                fh.write("\n".join(lines) + "\n")
        print(f"dump-sample {len(lines)} 条已写入 {args.out_sample}")
        return

    if args.probe:
        _init_worker(m2, str(d), str(W), args.impl, n, cons_rows, cons_b)
        K = args.probe
        third = max(1, K // 3)
        wins = [(0, min(third, total))]
        mid0 = max(0, total // 2 - third // 2)
        wins.append((mid0, min(mid0 + third, total)))
        wins.append((max(0, total - third), total))
        tots = [0, 0, 0]
        cnts = [0, 0, 0]
        for wi, (a, b) in enumerate(wins):
            r = process_range(a, b)
            cnts[wi] = r["count"]
            tots[wi] = r["sec"]
            ms = r["sec"] * 1000.0 / max(1, r["count"])
            print(f"[probe] 窗口{wi} [{a},{b})：{r['count']} 个子集 {r['sec']} s → {ms:.4f} ms/个（单进程）"
                  f" | 秩亏 {r['n_rank_def']} 满秩不可行 {r['n_infeasible']} "
                  f"可行解 {len(r['feasible'])}")
        tc, ts = sum(cnts), sum(tots)
        print(f"[probe] 三段合计：{tc} 个子集 {ts:.3f} s → {1000.0*ts/max(1,tc):.4f} ms/个（单进程，三段平均）")
        return

    nchunks = args.chunks or (args.workers * 2)
    print(f"分片：workers={args.workers} chunks={nchunks} impl={args.impl} resume={args.resume}")
    cpu0 = _wcpu()
    results, wall = run_full(args, d, W, total)
    cpu = _wcpu() - cpu0
    cnt, n_rd, n_if, feas = aggregate(results, total)
    print("-" * 78)
    print(f"    子集总数 C({n},{m2}) = {total}；已处理 = {cnt}（覆盖校验 = {cnt == total}）")
    print(f"    用时 {wall:.1f} s（墙钟），CPU（含子进程 user+sys）{cpu:.1f} s，"
          f"每子集 {1000.0*wall/total:.4f} ms（墙钟/总）")
    print(f"    分检：秩亏/不相容 = {n_rd}，满秩不可行 = {n_if}，"
          f"满秩可行子集 = {sum(v['count'] for v in feas.values())}")
    found = set()
    for k in feas:
        sol = tuple(Fraction(t) for t in k.split(","))
        found.add(sol)
    analytic = {tuple(vertex(m2, d, W, r)) for r in range(m2)}
    print(f"    可行顶点数 = {len(found)}；与解析的 m2 = {m2} 个循环旋转相同 = "
          f"{found == analytic}（解析集大小 {len(analytic)}）")
    certs = sorted({active_rank(y, m2, d, W) for y in found})
    print(f"    每个顶点的（活跃约束法向量秩，活跃约束条数）= {certs}")
    cap = sorted(v["count"] for v in feas.values())
    print(f"    每个可行解被活跃子集捕捉的个数（升序）= {cap}")
    print(f"    独立性：本段只用 constraint_list / solve_exact（或 mpq 镜像）/ feasible，"
          f"未使用 (L1) 或 v 的任何信息；v 仅用于构造对照解析集")
    if found != analytic:
        print("    ！！出现非解析可行顶点或解析顶点缺失，逐一列出：")
        for sol in sorted(found - analytic):
            print(f"      额外顶点 {fmt_frac_list(sol)}")
            for k, rec in feas.items():
                if tuple(Fraction(t) for t in k.split(",")) == sol:
                    print(f"        证书：捕捉它的活跃子集例 {rec['examples'][:3]}（共 {rec['count']} 个）")
        for sol in sorted(analytic - found):
            print(f"      缺失顶点 {fmt_frac_list(sol)}")
    summary = {
        "m2": m2, "delta": str(d), "W": str(W), "impl": args.impl,
        "workers": args.workers, "chunks": nchunks, "total": total, "processed": cnt,
        "n_rank_def": n_rd, "n_infeasible": n_if,
        "n_feasible_subsets": sum(v["count"] for v in feas.values()),
        "n_distinct_feasible": len(found), "n_analytic": len(analytic),
        "equal": found == analytic, "certs": certs,
        "wall_s": round(wall, 2), "cpu_s": round(cpu, 2),
        "ms_per_subset_wall": round(1000.0 * wall / total, 4),
        "ms_per_subset_cpu": round(1000.0 * cpu / total, 4),
    }
    print("SUMMARY_JSON " + json.dumps(summary, ensure_ascii=False))
    print("口径：本脚本是机器核对（附覆盖范围），不是证明；搜索无力（如秩亏）与可行性都只用精确有理算术判定。")


def fmt_frac_list(sol):
    return "(" + ", ".join(str(x) for x in sol) + ")"


if __name__ == "__main__":
    main()
