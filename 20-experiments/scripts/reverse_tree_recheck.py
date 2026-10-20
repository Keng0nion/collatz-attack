#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复核响应的核对脚本（针对评审员提出的四点）：
  1. §3.1 第 1 条：第 66 层的真实规模与「内存保护公式给出的估计」之差；
  2. §3.1 第 3 条：深度 70 的完整覆盖上界 M(70)；
  3. §5 第 3 条：最后 10 层常数的精确极差（用分数精确算术，不做二次取整）；
  4. 相关奇数的停时逐个列出，便于对账。
用法：
  .venv/bin/python reverse_tree_recheck.py --c-txt results/revtree_c_deep.txt
"""
import argparse
from fractions import Fraction


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


def parse_levels(path):
    lv = {}
    for line in open(path):
        if line.startswith("#LEVEL"):
            p = line.split()
            lv[int(p[1])] = dict(size=int(p[2]), odd=int(p[3]), even=int(p[4]),
                                 r0=int(p[5]), r1=int(p[6]), r2=int(p[7]))
    return lv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c-txt", default="results/revtree_c_deep.txt")
    ap.add_argument("--c-txt-66", default=None)
    ap.add_argument("--coverage-limit", type=int, default=1_000_000)
    args = ap.parse_args()

    out = []

    def emit(s=""):
        print(s, flush=True)
        out.append(s)

    emit("=" * 74)
    emit("核对一：第 66 层、第 67 层的真实规模 vs 内存保护公式的估计")
    emit("=" * 74)
    lv = parse_levels(args.c_txt)
    N65, r2_65 = lv[65]["size"], lv[65]["r2"]
    emit(f"实测：N(65) = {N65}，第 65 层中 x ≡ 2 (mod 3) 的个数 = {r2_65}")
    emit(f"实测恒等式 N(d+1) = N(d) + 第 d 层中 x ≡ 2 (mod 3) 的个数（本实验在 d = 2 至 64 逐层核对通过）")
    N66_pred = N65 + r2_65
    emit(f"由该恒等式得 N(66) = {N65} + {r2_65} = {N66_pred}")
    emit(f"  换算内存（每元素 16 字节）= {N66_pred * 16} 字节 = {N66_pred * 16 / 1e9:.3f} GB")
    need = int(N65 * 1.45) + 1024
    emit(f"程序里的内存保护用的是粗估 need = N(65) × 1.45 + 1024 = {need} 个元素"
         f"（scripts/reverse_tree_deep.c:155 附近）")
    emit(f"  该粗估换算内存 = {need * 16} 字节 = {need * 16 / 1e9:.3f} GB，比真实需求多 "
         f"{(need - N66_pred) / N66_pred * 100:.2f}%")
    if args.c_txt_66:
        lv66 = parse_levels(args.c_txt_66)
        if 66 in lv66:
            emit("")
            emit(f"实跑验证（另一次运行，--mem-guard-gb 2.1）：实测 N(66) = {lv66[66]['size']}，"
                 f"第 66 层 x ≡ 2 (mod 3) 的个数 = {lv66[66]['r2']}")
            emit(f"  与上文恒等式预测 {N66_pred} 相比：{'一致' if lv66[66]['size'] == N66_pred else '不一致'}")
            N67 = lv66[66]["size"] + lv66[66]["r2"]
            emit(f"  进而 N(67) = N(66) + 第 66 层中 x ≡ 2 (mod 3) 的个数 = {lv66[66]['size']} + {lv66[66]['r2']}"
                 f" = {N67}，换算内存 = {N67 * 16 / 1e9:.3f} GB")
            emit(f"  即：按真实规模，生成第 66 层需要 {lv66[66]['size'] * 16 / 1e9:.3f} GB（低于 2.0 GB 阈值），"
                 f"生成第 67 层需要 {N67 * 16 / 1e9:.3f} GB（超过 2.0 GB 阈值）")
    emit("")

    emit("=" * 74)
    emit("核对二：完整覆盖上界 M(D)（用前向停时独立计算）")
    emit("=" * 74)
    memo = sigma_table(args.coverage_limit)
    odd_ns = list(range(1, args.coverage_limit + 1, 2))
    pref = []
    m = -1
    for n in odd_ns:
        s = memo[n]
        if s > m:
            m = s
        pref.append(m)
    import bisect
    emit(f"{'D':>5} {'M(D)':>8} {'该深度之外最小的奇数':>22} {'它的停时':>10}")
    for D in list(range(25, 30)) + [48, 60, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]:
        i = bisect.bisect_right(pref, D) - 1
        M = odd_ns[i] if i >= 0 else 0
        first_missing = None
        for n in odd_ns:
            if memo[n] > D:
                first_missing = n
                break
        emit(f"{D:>5} {M:>8} {str(first_missing):>22} {str(memo[first_missing]):>10}")
    emit("")
    emit("相关奇数的停时：")
    for n in (25, 27, 31, 41, 47, 53, 55, 63, 73, 75, 97, 871, 6171, 77031, 837799):
        if n in memo:
            emit(f"  σ({n}) = {memo[n]}")
    emit("")

    emit("=" * 74)
    emit("核对三：最后 10 层常数 N(d)/(4/3)^d 的精确极差（分数算术）")
    emit("=" * 74)
    vals = {}
    for d in range(56, 66):
        c = Fraction(lv[d]["size"], 1) / Fraction(4, 3) ** d
        vals[d] = c
    for d in sorted(vals):
        emit(f"  d = {d:>2}  N = {lv[d]['size']:>9}  c = {float(vals[d]):.10f}"
             f"  精确分数小数前 20 位 = {vals[d].numerator / vals[d].denominator:.20f}")
    hi = max(vals.values())
    lo = min(vals.values())
    emit(f"  精确最大值 = {float(hi):.10f}（d = {[d for d in vals if vals[d] == hi][0]}）")
    emit(f"  精确最小值 = {float(lo):.10f}（d = {[d for d in vals if vals[d] == lo][0]}）")
    emit(f"  精确极差 = {float(hi - lo):.10f}；按 6 位小数取整 = {float(hi - lo):.6f}")
    emit(f"  两个已取整端点的差 = {float(f'{float(hi):.6f}') - float(f'{float(lo):.6f}'):.6f}"
         f"（这是二次取整的产物）")

    with open("results/revtree_recheck.txt", "w") as f:
        f.write("\n".join(out) + "\n")
    print("已写入 results/revtree_recheck.txt")


if __name__ == "__main__":
    main()
