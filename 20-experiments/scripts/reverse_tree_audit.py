#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""审计 findings/reverse-tree.md：
   1. 找出「含中文且含半角连字符」的行（正文纪律检查，代码块与行内代码除外）；
   2. 把文中引用的关键数字与 results/ 下的原始输出逐一对账。
"""
import re
import sys

MD = "findings/reverse-tree.md"
C_TXT = "results/revtree_c_deep.txt"
ANALYSIS = "results/revtree_analysis.txt"
PY_JSON = "results/revtree_py_d48.json"

CJK = re.compile(r"[\u4e00-\u9fff]")


def strip_code(text):
    """去掉围栏代码块与行内代码，剩下的算「正文」。"""
    out = []
    in_fence = False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        out.append(re.sub(r"`[^`]*`", "", line))
    return "\n".join(out)


def main():
    text = open(MD, encoding="utf-8").read()
    prose = strip_code(text)
    print("=" * 70)
    print("一、正文纪律检查：含中文且含半角连字符的行")
    print("=" * 70)
    hits = 0
    for i, line in enumerate(prose.split("\n"), 1):
        if CJK.search(line) and "-" in line:
            print(f"  行 {i}: {line.strip()[:160]}")
            hits += 1
    print(f"  命中 {hits} 行")

    print()
    print("=" * 70)
    print("二、数字对账（文中数字 与 原始输出）")
    print("=" * 70)

    ctxt = open(C_TXT, encoding="utf-8").read()
    anal = open(ANALYSIS, encoding="utf-8").read()
    levels = {}
    for line in ctxt.split("\n"):
        if line.startswith("#LEVEL"):
            p = line.split()
            levels[int(p[1])] = dict(size=int(p[2]), odd=int(p[3]), even=int(p[4]),
                                     r0=int(p[5]), r1=int(p[6]), r2=int(p[7]),
                                     mn=p[8], mx=p[9])
    # 人读表里最后两列是「最小奇数 / 最大奇数」，单独解析
    odd_span = {}
    for line in ctxt.split("\n"):
        p = line.split()
        if len(p) == 12 and p[0].isdigit():
            odd_span[int(p[0])] = (p[10], p[11])
    checks = []
    # 表 4.1 的格子
    want_rows = {
        0: (1, 1, 0), 8: (6, 1, 2), 16: (68, 18, 23), 24: (665, 160, 220),
        32: (6682, 1668, 2220), 40: (66763, 16696, 22246), 48: (666725, 166619, 222222),
        56: (6660211, 1665133, 2220477), 60: (21050985, 5263009, 7016955),
        64: (66531372, 16633395, 22178988), 65: (88710360, 22178988, 29570329),
    }
    for d, (n, odd, r2) in want_rows.items():
        lv = levels[d]
        ok = (lv["size"], lv["odd"], lv["r2"]) == (n, odd, r2)
        checks.append((f"层 {d} 的 N/奇数/≡2 = ({n}, {odd}, {r2})", ok,
                       f"原始 ({lv['size']}, {lv['odd']}, {lv['r2']})"))
    # 表 4.2 的格子
    want_odd = {20: (52, 43, 349525), 30: (936, 185, 357913941),
                48: (166619, 297, 93824992236885),
                64: (16633395, 107, 6148914691236517205),
                65: (22178988, 71, 4099276460824344803)}
    for d, (cnt, mn, mx) in want_odd.items():
        lv = levels[d]
        got = odd_span.get(d)
        if got is None:
            continue
        ok = (lv["odd"], got[0], got[1]) == (cnt, str(mn), str(mx))
        checks.append((f"层 {d} 奇数计数/最小奇数/最大奇数 = ({cnt}, {mn}, {mx})", ok,
                       f"原始 ({lv['odd']}, {got[0]}, {got[1]})"))
    # 关键数字
    pairs = [
        ("累计节点 354832309", "total_nodes=354832309" in ctxt),
        ("最后 10 层平均常数 0.671338", "0.671338" in anal),
        ("平均比值 1.333347", "1.333347" in anal),
        ("深度 65 覆盖到 n = 25", "深度 D =  65：完整覆盖奇数到 M =    25" in anal),
        ("最小未出现奇数 27 与深度 70", "尚未出现的最小奇数 = 27（出现深度 70）" in anal),
        ("sigma 最大 329 在 837799", "sigma 最大值 = 329（在 n = 837799）" in anal),
        ("sigma 平均 91.6065", "sigma 平均值（奇数）= 91.6065" in anal),
        ("深度 65 收纳占比 27.2538%", "27.2538%" in anal),
        ("深度 48 收纳占比 9.6320%", "9.6320%" in anal),
        ("n <= 1000 需深度 113", "M =     1000：需要深度  113（由 n = 871 达到" in anal),
        ("D=113 外推 8.811e+13", "8.811e+13" in anal),
        ("D=65 最大节点 2^65", "36893488147419103232" in ctxt),
        ("第 64 层 ≡2 个数 = 22178988", levels[64]["r2"] == 22178988),
        ("第 65 层奇数 22178988", levels[65]["odd"] == 22178988),
        ("C 版校验 verify_fail=0", "verify_fail=0" in ctxt),
        ("跳过根节点 1 次", "skipped_root_child=1" in ctxt),
    ]

    # 复核轮新增的对账（2026 年 10 月 19 日）
    md = text
    c66 = ""
    try:
        c66 = open("results/revtree_c_d66.txt", encoding="utf-8").read()
    except FileNotFoundError:
        pass
    rch = ""
    try:
        rch = open("results/revtree_recheck.txt", encoding="utf-8").read()
    except FileNotFoundError:
        pass
    lv66 = {}
    for line in c66.split("\n"):
        if line.startswith("#LEVEL"):
            p = line.split()
            lv66[int(p[1])] = dict(size=int(p[2]), odd=int(p[3]), r2=int(p[7]))
    pairs += [
        ("补跑到达第 66 层", "reached_depth=66" in c66),
        ("实测 N(66) = 118280689", lv66.get(66, {}).get("size") == 118280689),
        ("实测第 66 层 ≡2 = 39424846", lv66.get(66, {}).get("r2") == 39424846),
        ("findings 写出 N(66) 实测值", "118,280,689" in md),
        ("findings 写出 N(67) = 157705535", "157,705,535" in md),
        ("findings 写出 M(70) = 53", "M(70) = 53" in md),
        ("recheck 里 M(70) 行 = 53", "\n   70       53" in rch),
        ("findings 写出精确极差 0.0000583139", "0.0000583139" in md),
        ("recheck 里精确极差 = 0.0000583139", "精确极差 = 0.0000583139" in rch),
        ("recheck 里 6 位取整 = 0.000058", "按 6 位小数取整 = 0.000058" in rch),
        ("旧值 0.000059 只剩一处（7.3 修订说明里）", md.count("0.000059") == 1),
        ("findings 有 7.3 复核与修订记录", "### 7.3 复核与修订记录" in md),
        ("补跑峰值 3.31 GB 已记录", "3,314,944,736" in md),
    ]

    for name, ok in pairs:
        checks.append((name, bool(ok), ""))

    bad = 0
    for name, ok, extra in checks:
        mark = "通过" if ok else "不一致"
        if not ok:
            bad += 1
        print(f"  [{mark}] {name} {extra}")
    print(f"  合计 {len(checks)} 项，不一致 {bad} 项")
    return 1 if (hits or bad) else 0


if __name__ == "__main__":
    sys.exit(main())
