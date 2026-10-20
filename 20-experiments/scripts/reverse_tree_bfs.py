#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逆向树实验：从 1 出发，用分支
    x -> 2x
    x -> (2x-1)/3     仅当 2x-1 是 3 的倍数、且 (2x-1)/3 为正奇数
做广度优先生长，测量：
  1. 节点数随层数的增长曲线（与 (4/3)^层数 对照）
  2. 每层覆盖了哪些奇数
  3. 在可达到的深度内，哪些奇数 n <= M 已全部出现在树里
另附独立交叉校验（用前向迭代算停时 sigma，与 BFS 深度比对）。

用法：
  .venv/bin/python reverse_tree_bfs.py --depth 45
"""
import argparse
import bisect
import json
import resource
import time


def children(x):
    """按任务规定的两条分支，返回 x 的孩子列表。"""
    out = [2 * x]
    num = 2 * x - 1
    if num % 3 == 0:
        y = num // 3
        if y > 0 and y % 2 == 1:
            out.append(y)
    return out


def parent(n):
    """树的父映射：偶 n -> n/2；奇 n -> (3n+1)/2（即短路 Collatz 映射，n != 1）。"""
    if n % 2 == 0:
        return n // 2
    return (3 * n + 1) // 2


# ---------------------------------------------------------------- 独立方法：前向停时
def sigma_table(limit, memo=None):
    """sigma[n] = 前向迭代（偶除以 2，奇取 (3n+1)/2）到 1 的步数；1 <= n <= limit。"""
    if memo is None:
        memo = {}
    memo[1] = 0
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, default=45, help="BFS 最大深度")
    ap.add_argument("--odd-list-depth", type=int, default=14, help="完整打印每层奇数表的深度上限")
    ap.add_argument("--coverage-limit", type=int, default=1_000_000, help="前向停时计算的上界")
    ap.add_argument("--node-guard", type=int, default=60_000_000, help="节点总数保护阈值")
    ap.add_argument("--json", default=None)
    ap.add_argument("--txt", default=None)
    args = ap.parse_args()

    log_lines = []

    def emit(s=""):
        print(s, flush=True)
        log_lines.append(s)

    t_start = time.perf_counter()
    emit("=" * 78)
    emit("逆向树 BFS 实验")
    emit(f"分支：x -> 2x；x -> (2x-1)/3（当且仅当 3 | 2x-1 且结果为正奇数）")
    emit(f"最大深度 = {args.depth}；节点保护阈值 = {args.node_guard}")
    emit("=" * 78)

    # ---------------------------------------------------------- BFS 生长
    depth_of = {1: 0}
    seen = {1}
    cur = [1]
    levels_total_children = []      # 每层孩子总数（未去重）
    collisions = []                 # (parent, child) 已被访问过的孩子
    level_info = {}
    reached_depth = 0
    total_nodes = 1
    t_bfs0 = time.perf_counter()
    for d in range(args.depth + 1):
        odds = [v for v in cur if v % 2 == 1]
        n_odd = len(odds)
        n_even = len(cur) - n_odd
        res = [0, 0, 0]
        for v in cur:
            res[v % 3] += 1
        two_child = 0
        kid_count = 0
        for x in cur:
            k = children(x)
            kid_count += len(k)
            if len(k) == 2:
                two_child += 1
        info = {
            "depth": d,
            "size": len(cur),
            "odd": n_odd,
            "even": n_even,
            "min": min(cur),
            "max": max(cur),
            "odd_min": min(odds) if odds else None,
            "odd_max": max(odds) if odds else None,
            "res0": res[0],
            "res1": res[1],
            "res2": res[2],
            "nodes_with_two_children": two_child,
            "children_total": kid_count,
        }
        if d <= args.odd_list_depth:
            info["odd_values"] = sorted(odds)
            info["even_values"] = sorted(v for v in cur if v % 2 == 0)
        level_info[d] = info
        levels_total_children.append(kid_count)
        reached_depth = d
        if d == args.depth:
            break
        if total_nodes + kid_count > args.node_guard:
            emit(f"[保护] 展开第 {d} 层会使总节点数超过阈值 {args.node_guard}，停在深度 {d}。")
            break
        nxt = []
        for x in cur:
            for c in children(x):
                if c in seen:
                    collisions.append((x, c))
                    continue
                seen.add(c)
                depth_of[c] = d + 1
                nxt.append(c)
        total_nodes += len(nxt)
        cur = nxt
    t_bfs = time.perf_counter() - t_bfs0
    emit(f"BFS 实际到达深度 = {reached_depth}；总节点数 = {total_nodes}；耗时 = {t_bfs:.2f} s")
    emit(f"最大常驻内存 = {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.1f} MB")
    emit("")

    # ---------------------------------------------------------- 增长曲线
    emit("表 1  逐层节点数 N(d)，与 (4/3)^d 及比值对照")
    emit(f"{'d':>4} {'N(d)':>14} {'N(d)/N(d-1)':>13} {'(4/3)^d':>13} {'N(d)/(4/3)^d':>15} "
         f"{'奇数':>8} {'偶数':>8} {'≡2 (mod 3)':>11} {'min':>10} {'max':>12}")
    growth_rows = []
    prev = None
    for d in sorted(level_info):
        inf = level_info[d]
        pred = (4.0 / 3.0) ** d
        ratio = (inf["size"] / prev) if prev else float("nan")
        row = {
            "d": d,
            "N": inf["size"],
            "ratio_prev": ratio,
            "pred_4_3_d": pred,
            "N_over_pred": inf["size"] / pred,
            "odd": inf["odd"],
            "even": inf["even"],
            "res2": inf["res2"],
        }
        growth_rows.append(row)
        if d % 5 == 0 or d <= 12:
            emit(f"{d:>4} {inf['size']:>14} {ratio:>13.5f} {pred:>13.3e} "
                 f"{inf['size'] / pred:>15.6f} {inf['odd']:>8} {inf['even']:>8} "
                 f"{inf['res2']:>11} {inf['min']:>10} {inf['max']:>12}")
        prev = inf["size"]
    emit("")

    # ---------------------------------------------------------- 每层奇数
    emit(f"表 2  每层覆盖的奇数（深度 0 至 {min(args.odd_list_depth, reached_depth)} 完整列出）")
    for d in sorted(level_info):
        inf = level_info[d]
        if d <= min(args.odd_list_depth, reached_depth):
            emit(f"  深度 {d:>2}  奇数 {inf['odd']:>3} 个：{inf['odd_values']}")
    emit("")
    emit("表 3  较大深度处每层奇数的计数与最大最小奇数")
    emit(f"{'d':>4} {'奇数个数':>10} {'最小奇数':>12} {'最大奇数':>16}")
    for d in sorted(level_info):
        inf = level_info[d]
        if d > min(args.odd_list_depth, reached_depth):
            emit(f"{d:>4} {inf['odd']:>10} {str(inf['odd_min']):>12} {str(inf['odd_max']):>16}")
    emit("")

    # ---------------------------------------------------------- 结构校验
    emit("表 4  结构校验")
    checks = {}

    # 4.1 父映射一致性：每个非根节点的父节点应在上一层，且等于 parent(n)
    bad_parent = 0
    for n, d in depth_of.items():
        if n == 1:
            continue
        p = parent(n)
        if p not in depth_of or depth_of[p] != d - 1:
            bad_parent += 1
    checks["bad_parent_count"] = bad_parent
    emit(f"  4.1 父映射一致（parent(n) 恰在上一层）：违规 {bad_parent} 个")

    # 4.2 孩子数只能是 1 或 2，且第 2 个孩子存在的充要条件是 x ≡ 2 (mod 3)
    bad_children = 0
    branch_residue_ok = True
    for n in depth_of:
        k = len(children(n))
        if k not in (1, 2):
            bad_children += 1
        if (k == 2) != (n % 3 == 2):
            branch_residue_ok = False
    checks["bad_children_count"] = bad_children
    checks["second_child_iff_x_eq_2_mod_3"] = branch_residue_ok
    emit(f"  4.2 孩子数 ∈ {{1,2}}：违规 {bad_children} 个；"
         f"「第二分支存在 ⟺ x ≡ 2 (mod 3)」：{'成立' if branch_residue_ok else '不成立'}")

    # 4.3 第二条分支的结果必为奇数（任务给定条件中的「正奇数」是否由「3 | 2x-1」自动保证）
    auto_odd = all(((2 * n - 1) // 3) % 2 == 1 for n in depth_of if (2 * n - 1) % 3 == 0)
    checks["second_branch_auto_odd"] = auto_odd
    emit(f"  4.3 凡 3 | 2x-1，(2x-1)/3 自动为奇数：{'成立' if auto_odd else '不成立'}")

    # 4.4 重复孩子（回到已见节点）只应来自 1 -> 2 -> 1 这个二元环
    checks["collisions"] = [list(c) for c in collisions]
    emit(f"  4.4 重复孩子事件共 {len(collisions)} 次：{collisions}")

    # ---------------------------------------------------------- 与 (4/3)^d 的对照
    emit("")
    emit("表 5  增长率的收敛观察（取最后若干层的比值）")
    tail = growth_rows[-12:]
    for r in tail:
        emit(f"  d={r['d']:>3}  N(d)/N(d-1) = {r['ratio_prev']:.6f}   N(d)/(4/3)^d = {r['N_over_pred']:.6f}")

    # ---------------------------------------------------------- 覆盖性（独立方法）
    emit("")
    emit("独立交叉校验：前向停时 sigma（偶除 2，奇取 (3n+1)/2）")
    t_sig0 = time.perf_counter()
    memo = sigma_table(args.coverage_limit)
    t_sig = time.perf_counter() - t_sig0
    emit(f"  已算出 n <= {args.coverage_limit} 的 sigma，耗时 {t_sig:.2f} s")

    # 与 BFS 深度比对：树中每个 n <= limit 的深度应等于 sigma(n)
    mismatch = 0
    for n, d in depth_of.items():
        if n <= args.coverage_limit and memo.get(n) != d:
            mismatch += 1
    checks["sigma_depth_mismatch"] = mismatch
    emit(f"  与 BFS 深度比对（n <= {args.coverage_limit} 的树节点）：不一致 {mismatch} 个")

    # 集合层面：树 ∩ [1, limit] 应恰为 {n <= limit : sigma(n) <= reached_depth}
    tree_small = {n for n in depth_of if n <= args.coverage_limit}
    sigma_small = {n for n in range(1, args.coverage_limit + 1)
                   if memo[n] <= reached_depth}
    only_tree = len(tree_small - sigma_small)
    only_sigma = len(sigma_small - tree_small)
    checks["set_only_tree"] = only_tree
    checks["set_only_sigma"] = only_sigma
    emit(f"  集合层面（n <= {args.coverage_limit}）：树中有而 sigma 判无 {only_tree} 个；"
         f"sigma 判有而树中无 {only_sigma} 个")

    # 覆盖深度：深度 D 的树覆盖了哪些奇数
    emit("")
    emit("覆盖性：深度 D 的树包含了哪些奇数")
    odd_ns = list(range(1, args.coverage_limit + 1, 2))
    pref = []
    m = -1
    for n in odd_ns:
        s = memo[n]
        if s > m:
            m = s
        pref.append(m)          # pref[i] = max(sigma) over odd n <= odd_ns[i]
    M_of_D = {}
    for D in range(0, reached_depth + 1):
        i = bisect.bisect_right(pref, D) - 1
        M_of_D[D] = odd_ns[i] if i >= 0 else 0
    emit(f"  深度 {reached_depth} 的树覆盖了全部奇数 n <= {M_of_D[reached_depth]}")
    probe = [0, 5, 10, 20, 30, 40, 50, 60, 80, 100, 120, 150, 180, 200]
    emit("  各深度对应的完整覆盖上界 M(D)（M(D) = 使所有奇数 n <= M 均已出现的最大 M）：")
    for D in probe:
        if D <= reached_depth:
            emit(f"    D = {D:>4}  ->  M(D) = {M_of_D[D]}")
    # 未被覆盖的最小奇数
    first_missing = None
    for n in range(1, args.coverage_limit + 1, 2):
        if memo[n] > reached_depth:
            first_missing = (n, memo[n])
            break
    emit(f"  深度 {reached_depth} 内尚未出现的最小奇数：{first_missing}")
    # 全部奇数 n <= limit 是否都出现在（无限深的）树里
    not_reaching = [n for n in range(1, args.coverage_limit + 1, 2) if n not in memo]
    emit(f"  前向迭代意义下，奇数 n <= {args.coverage_limit} 中轨道未回到 1 的：{len(not_reaching)} 个")

    # ---------------------------------------------------------- 分支密度
    emit("")
    emit("表 6  逐层「≡2 (mod 3)」密度与平均孩子数")
    emit(f"{'d':>4} {'N(d)':>14} {'N(≡2)':>14} {'密度':>10} {'平均孩子数':>12}")
    dens_rows = []
    for d in sorted(level_info):
        inf = level_info[d]
        dens = inf["res2"] / inf["size"]
        avgk = inf["children_total"] / inf["size"]
        dens_rows.append({"d": d, "N": inf["size"], "res2": inf["res2"],
                          "density_res2": dens, "avg_children": avgk})
        if d % 5 == 0 or d <= 12:
            emit(f"{d:>4} {inf['size']:>14} {inf['res2']:>14} {dens:>10.6f} {avgk:>12.6f}")
    # 密度收敛：最后 10 层平均
    last = dens_rows[-10:]
    emit(f"  最后 {len(last)} 层的 ≡2 密度均值 = {sum(r['density_res2'] for r in last) / len(last):.6f}"
         f"；平均孩子数均值 = {sum(r['avg_children'] for r in last) / len(last):.6f}")

    t_total = time.perf_counter() - t_start
    emit("")
    emit(f"总耗时 = {t_total:.2f} s；峰值内存 = "
         f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.1f} MB")

    out = {
        "params": vars(args),
        "reached_depth": reached_depth,
        "total_nodes": total_nodes,
        "seconds_bfs": t_bfs,
        "seconds_sigma": t_sig,
        "seconds_total": t_total,
        "maxrss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6,
        "levels": {str(k): v for k, v in level_info.items()},
        "growth": growth_rows,
        "density": dens_rows,
        "checks": checks,
        "coverage": {
            "limit": args.coverage_limit,
            "M_of_D": {str(D): M_of_D[D] for D in range(0, reached_depth + 1)},
            "first_missing": first_missing,
            "odd_not_reaching_1": len(not_reaching),
        },
    }
    if args.json:
        with open(args.json, "w") as f:
            json.dump(out, f, indent=1)
        emit(f"JSON 已写入 {args.json}")
    if args.txt:
        with open(args.txt, "w") as f:
            f.write("\n".join(log_lines) + "\n")
        print(f"日志已写入 {args.txt}")


if __name__ == "__main__":
    main()
