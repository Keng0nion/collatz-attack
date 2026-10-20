#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逆向树实验的分析与交叉校验：
  1. C 版与 Python 版逐层节点数的逐字段比对（两套独立实现）；
  2. 生长常数 c = N(d)/(4/3)^d 的收敛观察；
  3. 覆盖性：深度 D 的树覆盖了哪些奇数（用前向停时 sigma 独立判定）；
  4. 奇数 n 与「出现深度」的对照表，以及「建树到深度 D 能覆盖多少奇数」的量化。
用法：
  .venv/bin/python reverse_tree_analysis.py --py-json <...> --c-txt <...>
"""
import argparse
import json
import math
import re


def sigma_table(limit):
    memo = {1: 0}
    for n in range(2, limit + 1):
        if n in memo:
            continue
        stack = []
        m = n
        while m not in memo:
            stack.append(m)
            m = m // 2 if m % 2 == 0 else (3 * m + 1) // 2
        base = memo[m]
        for v in reversed(stack):
            base += 1
            memo[v] = base
    return memo


def parse_c_levels(path):
    lv = {}
    with open(path) as f:
        for line in f:
            if line.startswith("#LEVEL"):
                p = line.split()
                d = int(p[1])
                lv[d] = {
                    "size": int(p[2]), "odd": int(p[3]), "even": int(p[4]),
                    "res0": int(p[5]), "res1": int(p[6]), "res2": int(p[7]),
                    "min": int(p[8]), "max": int(p[9]),
                }
            elif line.startswith("#SUMMARY"):
                lv["summary"] = line.strip()
    return lv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--py-json", required=True)
    ap.add_argument("--c-txt", required=True)
    ap.add_argument("--coverage-limit", type=int, default=1_000_000)
    ap.add_argument("--odd-table-limit", type=int, default=200)
    args = ap.parse_args()

    out = []
    def emit(s=""):
        print(s, flush=True)
        out.append(s)

    pyj = json.load(open(args.py_json))
    clev = parse_c_levels(args.c_txt)
    csum = clev.pop("summary", "")

    py_depth = pyj["reached_depth"]
    c_depth = max(clev)
    emit("=" * 78)
    emit("一、两套独立实现的逐层比对（Python BFS 版 与 C 版）")
    emit("=" * 78)
    emit(f"Python 版到达深度 {py_depth}，C 版到达深度 {c_depth}")
    fields = ["size", "odd", "even", "res0", "res1", "res2", "min", "max"]
    bad = 0
    comp_depth = min(py_depth, c_depth)
    for d in range(comp_depth + 1):
        a = pyj["levels"][str(d)]
        b = clev[d]
        for f in fields:
            if a[f] != b[f]:
                emit(f"  不一致 d={d} 字段={f} python={a[f]} c={b[f]}")
                bad += 1
    emit(f"逐字段比对范围 d = 0 至 {comp_depth}，共 {len(fields)} 个字段：不一致 {bad} 处")

    # 奇数清单的逐层比对（Python JSON 里保存到 odd-list-depth，C 输出里到 20）
    odds_c = {}
    with open(args.c_txt) as f:
        for line in f:
            if line.startswith("#ODDS"):
                p = line.split()
                odds_c[int(p[1])] = [int(v) for v in p[2:]]
    list_depth = min(max(odds_c), max(int(k) for k in pyj["levels"]
                                     if "odd_values" in pyj["levels"][k]))
    bad_list = 0
    for d in range(list_depth + 1):
        a = pyj["levels"][str(d)].get("odd_values")
        b = odds_c.get(d)
        if a is None or b is None:
            continue
        if sorted(a) != sorted(b):
            emit(f"  奇数清单不一致 d={d}：python={a} c={b}")
            bad_list += 1
    emit(f"奇数清单逐层比对（d = 0 至 {list_depth}）：不一致 {bad_list} 处")
    emit(f"C 版自身校验：{csum if csum else '（未找到 #SUMMARY 行）'}")
    emit("")

    emit("=" * 78)
    emit("二、生长曲线：N(d) 与 (4/3)^d 的对照")
    emit("=" * 78)
    emit(f"{'d':>4} {'N(d)':>16} {'N(d)/N(d-1)':>13} {'N(d)/(4/3)^d':>15} {'奇数占比':>10} "
         f"{'≡2 占比':>10}")
    rows = []
    for d in sorted(clev):
        b = clev[d]
        pred = (4.0 / 3.0) ** d
        ratio = float("nan") if d == 0 else b["size"] / clev[d - 1]["size"]
        rows.append((d, b["size"], ratio, b["size"] / pred, b["odd"] / b["size"],
                     b["res2"] / b["size"]))
    for d, N, ratio, c, od, r2 in rows:
        if d % 4 == 0 or d >= c_depth - 6:
            emit(f"{d:>4} {N:>16} {ratio:>13.6f} {c:>15.6f} {od:>10.6f} {r2:>10.6f}")
    tail = [r for r in rows if r[0] >= c_depth - 9]
    cmean = sum(r[3] for r in tail) / len(tail)
    rmean = sum(r[2] for r in tail) / len(tail)
    emit("")
    emit(f"最后 10 层（d = {tail[0][0]} 至 {tail[-1][0]}）：")
    emit(f"  平均比值 N(d)/N(d-1) = {rmean:.6f}   （4/3 = {4/3:.6f}，相对差 "
         f"{(rmean - 4/3) / (4/3) * 100:+.4f}%）")
    emit(f"  平均常数 N(d)/(4/3)^d = {cmean:.6f}（逐层最大 {max(r[3] for r in tail):.6f}，"
         f"最小 {min(r[3] for r in tail):.6f}）")
    mid = [r for r in rows if 40 <= r[0] <= 48]
    if mid:
        c40 = sum(r[3] for r in mid) / len(mid)
        emit(f"  对照：d = 40 至 48 的平均常数 = {c40:.6f}（与最后 10 层的差 "
             f"{abs(cmean - c40):.6f}）")

    # 结构性恒等式：第 d+1 层的奇数个数 == 第 d 层里 ≡2 (mod 3) 的节点个数
    # 理由：第 d 层的孩子只有两类，2x（偶）与 (2x-1)/3（当 x ≡ 2 mod 3，必为奇）；
    # 两类按奇偶性不相交，x -> (2x-1)/3 单射，且层内无重复（本实验已校验）。
    ident_bad = [d for d in sorted(clev) if d + 1 in clev and clev[d + 1]["odd"] != clev[d]["res2"]]
    emit("")
    emit(f"结构性恒等式核对：第 d+1 层奇数个数 == 第 d 层中 x ≡ 2 (mod 3) 的个数；"
         f"逐层核对 d = 0 至 {c_depth - 1}，例外 {len(ident_bad)} 层：{ident_bad}")
    if ident_bad == [1]:
        emit("  唯一例外是 d = 1：第 1 层只有节点 2（2 ≡ 2 mod 3），它的第二个孩子是 1，"
             "即根节点，按去重规则被跳过，故第 2 层奇数个数为 0 而不是 1。")
        emit(f"  d = 2 至 {c_depth - 1} 全部成立，无例外。")
    emit(f"  例：第 64 层 x ≡ 2 (mod 3) 的个数 = {clev[64]['res2']}，第 65 层奇数个数 = "
         f"{clev[65]['odd']}")
    emit(f"  由此 odd/N 的极限为 (1/3)/(4/3) = 1/4，实测第 65 层为 "
         f"{clev[65]['odd'] / clev[65]['size']:.6f}")
    emit("")

    emit("=" * 78)
    emit("三、覆盖性：用前向停时 sigma 独立判定每个奇数的出现深度")
    emit("=" * 78)
    memo = sigma_table(args.coverage_limit)
    odd_ns = list(range(1, args.coverage_limit + 1, 2))
    pref = []
    m = -1
    for n in odd_ns:
        s = memo[n]
        if s > m:
            m = s
        pref.append(m)
    emit(f"已算出 n <= {args.coverage_limit} 的 sigma（前向迭代，偶除 2、奇取 (3n+1)/2）")
    emit(f"其中奇数 {len(odd_ns)} 个；sigma 最大值 = {max(memo[n] for n in odd_ns)}"
         f"（在 n = {max(odd_ns, key=lambda n: memo[n])}）")
    emit(f"sigma 平均值（奇数）= {sum(memo[n] for n in odd_ns) / len(odd_ns):.4f}")
    for D in (48, 64, c_depth):
        i = 0
        while i < len(pref) and pref[i] <= D:
            i += 1
        M = odd_ns[i - 1] if i > 0 else 0
        in_tree = sum(1 for n in odd_ns if memo[n] <= D)
        emit(f"  深度 D = {D:>3}：完整覆盖奇数到 M = {M:>5}；"
             f"在 n <= {args.coverage_limit} 的 {len(odd_ns)} 个奇数中，落入该深度的只有 {in_tree} 个"
             f"（{in_tree / len(odd_ns) * 100:.4f}%）")
    first_missing = None
    for n in odd_ns:
        if memo[n] > c_depth:
            first_missing = n
            break
    emit(f"  深度 {c_depth} 之外尚未出现的最小奇数 = {first_missing}（出现深度 {memo[first_missing]}）")
    emit("")
    emit("  完整覆盖奇数范围 n <= M 所需的最小深度（= 该范围内 sigma 的最大值）：")
    for M in (25, 100, 1000, 10 ** 4, 10 ** 5, 10 ** 6):
        if M > args.coverage_limit:
            continue
        sub = range(1, M + 1, 2)
        mx = max(sub, key=lambda n: memo[n])
        emit(f"    M = {M:>8}：需要深度 {memo[mx]:>4}（由 n = {mx} 达到；"
             f"该范围内奇数 {len(range(1, M + 1, 2))} 个）")
    emit("")
    emit("  建成到深度 D 所需的层规模（用实测常数外推，非实测）：")
    for D in (48, c_depth, 113):
        est = (4 / 3) ** D * cmean
        emit(f"    D = {D:>3}：N(D) 的线性外推 ≈ {est:.4g}"
             + ("（其中 D = 113 是覆盖全部奇数 n <= 1000 所需的最小深度，"
                "因为 sigma(871) = 113）" if D == 113 else "（本实验实测到这一层）"
                if D == c_depth else "（本实验实测到这一层）"))
    emit("")

    emit("=" * 78)
    emit(f"四、奇数与出现深度对照表（奇数 n <= {args.odd_table_limit}）")
    emit("=" * 78)
    emit(f"{'n':>6} {'出现深度 sigma(n)':>18} {'是否在深度 <= ' + str(c_depth) + ' 的树里':>22}")
    for n in range(1, args.odd_table_limit + 1, 2):
        emit(f"{n:>6} {memo[n]:>18} {'是' if memo[n] <= c_depth else '否':>22}")
    emit("")

    with open("results/revtree_analysis.txt", "w") as f:
        f.write("\n".join(out) + "\n")
    print("分析输出已写入 results/revtree_analysis.txt")


if __name__ == "__main__":
    main()
