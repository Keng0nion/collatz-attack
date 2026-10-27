#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-4 审计脚本 3：仪表化全活跃子集枚举（分片、无重无漏、带捕获见证与证书）。

对指定 (m2, δ, W) 枚举全部 C(2m2+1, m2) 个子集（按字典序编号区间切分，
任一片内用 itertools.islice 取 [lo, hi)），对每个子集调用被审计的
r2_common.solve_exact 与 r2_common.feasible，统计：
  全秩子集数、命中（可行解，按子集计）、去重后的顶点集、每个顶点的全部见证子集。
另对每个顶点做两套证书：r2_j.active_rank（被审计实现）与 sympy（独立栈）。
输出含顶点集 sha256 指纹，供多核与单核对拍（运行两次比指纹）。

用法（在 cycle-1/scripts 下）：
  PY="/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python"
  "$PY" route4_enum_instrumented.py --m2 10 --jobs 1
  "$PY" route4_enum_instrumented.py --m2 10 --jobs 8
"""
import hashlib
import itertools
import math
import multiprocessing as mp
import sys
import time
from fractions import Fraction

import route4_util as U

RC, RJ = U.load()
D_LO7 = RJ.D_LO7


def shard(args):
    """枚举 [lo, hi) 区间；返回统计与局部顶点字典（坐标元组 → 见证子集列表）。"""
    lo, hi, m2, d, W = args
    cons = RC.constraint_list(m2, d, W)
    n = 2 * m2 + 1
    cnt = 0
    full_rank = 0
    hits = 0
    verts = {}
    t0 = time.time()
    it = itertools.combinations(range(n), m2)
    for S in itertools.islice(it, lo, hi):
        cnt += 1
        rows = [cons[i][0] for i in S]
        b = [cons[i][1] for i in S]
        sol, rank = RC.solve_exact(rows, b)
        if sol is None or rank < m2:
            continue
        full_rank += 1
        ok, _bad = RC.feasible(sol, m2, d, W)
        if ok:
            hits += 1
            verts.setdefault(tuple(sol), []).append(S)
    return {"lo": lo, "hi": hi, "cnt": cnt, "full_rank": full_rank,
            "hits": hits, "verts": verts, "secs": time.time() - t0}


def vertex_digest(verts):
    parts = []
    for y in sorted(verts):
        parts.append(";".join(str(t) for t in y))
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def main():
    m2, jobs = 10, 1
    for i, a in enumerate(sys.argv):
        if a == "--m2":
            m2 = int(sys.argv[i + 1])
        if a == "--jobs":
            jobs = int(sys.argv[i + 1])
    d, W = D_LO7, Fraction(2000)
    total = math.comb(2 * m2 + 1, m2)
    U.say("=" * 78)
    U.say(f"route-4 审计脚本 3：仪表化全活跃子集枚举（m2 = {m2}，jobs = {jobs}）")
    U.say(f"参数：δ = {d}（D_LO7），W = {W}；子集总数 = C({2*m2+1},{m2}) = {total}")
    U.say(f"命令行：{sys.argv}")
    U.say("=" * 78)
    t0 = time.time()
    chunk = math.ceil(total / jobs)
    ranges = [(k * chunk, min((k + 1) * chunk, total)) for k in range(jobs) if k * chunk < total]
    if jobs == 1:
        results = [shard((r[0], r[1], m2, d, W)) for r in ranges]
    else:
        ctx = mp.get_context("spawn")
        with ctx.Pool(len(ranges)) as pool:
            results = pool.map(shard, [(r[0], r[1], m2, d, W) for r in ranges])
    elapsed = time.time() - t0

    U.say("\n分片表（区间为子集字典序编号，区间两两不交、并集 = [0, 总数)）：")
    for res in sorted(results, key=lambda x: x["lo"]):
        U.say(f"    片 [{res['lo']}, {res['hi']})：迭代 {res['cnt']} 个子集，"
              f"全秩 {res['full_rank']}，命中 {res['hits']}，用时 {res['secs']:.1f} s")
    cnt_sum = sum(r["cnt"] for r in results)
    full_rank_sum = sum(r["full_rank"] for r in results)
    hits_sum = sum(r["hits"] for r in results)
    verts = {}
    for res in results:
        for y, Slist in res["verts"].items():
            verts.setdefault(y, []).extend(Slist)
    for y in verts:
        verts[y] = sorted(verts[y])

    U.say("\n漏斗统计：")
    U.say(f"    迭代子集总数 = {cnt_sum}（与 math.comb 相等 = {cnt_sum == total}）")
    U.say(f"    全秩子集数（rank = m2 且相容）= {full_rank_sum}")
    U.say(f"    命中（可行解，按子集计）= {hits_sum}")
    U.say(f"    去重后顶点数 = {len(verts)}")

    analytic = {tuple(RC.vertex(m2, d, W, rot)) for rot in range(m2)}
    same = set(verts) == analytic
    U.say(f"    与解析的 {m2} 个循环旋转相同 = {same}（解析集大小 {len(analytic)}；"
          f"集合差 = {len(set(verts) ^ analytic)}）")

    U.say("\n逐顶点证书（被审计实现 RJ.active_rank 与 sympy 独立栈两套；见证子集为命中该点的全部子集）：")
    cert_rc = set()
    n_cert_bad = 0
    for y in sorted(verts):
        rk_rc, nact_rc = RJ.active_rank(y, m2, d, W)
        rk_sy, nact_sy = U.active_rank_sympy(y, m2, d, W)
        cert_rc.add((rk_rc, nact_rc))
        okay = (rk_rc == m2 and rk_sy == m2 and nact_rc == nact_sy)
        if not okay:
            n_cert_bad += 1
        U.say(f"    顶点 {tuple(str(t) for t in y)}：RC 秩/条数 = {rk_rc}/{nact_rc}；"
              f"sympy 秩/条数 = {rk_sy}/{nact_sy}；见证子集数 = {len(verts[y])}"
              f"（首个 = {verts[y][0] if verts[y] else None}）；证书 {'PASS' if okay else 'FAIL'}")
    U.say(f"    证书集合（RC 口径）= {sorted(cert_rc)}")

    dig = vertex_digest(verts)
    U.say("\n结果指纹：")
    U.say(f"    顶点集 sha256 = {dig}")
    rate = elapsed / total * 1000
    U.say(f"    总用时 = {elapsed:.1f} s；每子集平均 = {rate:.3f} 毫秒/个")
    U.say("    审计注记：r2_j_independent_vertices.py:121 至 :124 打印的 0.13 与 0.83 毫秒/个、")
    U.say("    「投影约 72 min」是硬编码文本（非运行导出）；一切以本行实测数为准（learnings.md:36）。")

    U.say("\n核对项：")
    ok1 = cnt_sum == total
    ok2 = not n_cert_bad
    ok3 = same
    if m2 == 10 and d == D_LO7 and W == Fraction(2000):
        ok4 = (total == 352716 and len(verts) == 10 and cert_rc == {(10, 10)})
        U.say(f"    [{'PASS' if ok4 else 'FAIL'}] 与基线 r2_j_A.txt 记录对照：子集 352716、顶点 10、"
              f"证书 [(10, 10)]（实测：{total}、{len(verts)}、{sorted(cert_rc)}）")
    else:
        ok4 = True
    U.say(f"    [{'PASS' if ok1 else 'FAIL'}] 迭代计数 = C(2m2+1, m2)")
    U.say(f"    [{'PASS' if ok2 else 'FAIL'}] 全部顶点双证书通过（失败 {n_cert_bad}）")
    U.say(f"    [{'PASS' if ok3 else 'FAIL'}] 顶点集与解析旋转集相等")
    U.say("=" * 78)
    if not (ok1 and ok2 and ok3 and ok4):
        sys.exit(1)


if __name__ == "__main__":
    main()
