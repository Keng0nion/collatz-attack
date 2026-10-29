#!/usr/bin/env python3
"""spot_recheck2：第二轮抽点，直接验证「捕捉子集 = 字典序末 m2 个」的结构观察。

只读输入：检查点 chunk_*.json（feasible 的 examples）；不重跑任何全量枚举、
不 import 既有实现（只用标准库），也不 invoke 第一轮 spot_recheck.py 的判定路径。
本脚本只做两件事：
  1. 把每个可行顶点的 examples 子集编号 unrank 成组合，打印（自算 unrank，来自 spot_recheck_lib）；
  2. 打印按字典序排序后的顶点坐标键与「最大编号捕捉子集」的关系。
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spot_recheck import unrank  # 仅复用本轮自写的 unrank（同一作者、同一轮）

CKPT = ("/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/vertex-m12/cycle-1/results/ckpt")


def run(dd, m2):
    d = os.path.join(CKPT, dd)
    fs = sorted(f for f in os.listdir(d) if f.startswith("chunk_"))
    recs = {}
    for f in fs:
        c = json.load(open(os.path.join(d, f)))
        for k, v in c["feasible"].items():
            recs.setdefault(k, []).append((c["start"], v["examples"]))
    rows = []
    for k, lst in recs.items():
        exs = [e for _, es in lst for e in es]
        for e in exs:
            rows.append((tuple(e), k))
    rows.sort(key=lambda t: t[0])
    print("目录 %s（m2 = %d）：顶点 %d 个，捕捉子集 %d 个" % (dd, m2, len(recs), len(rows)))
    total = 1
    for i in range(m2):
        total = total * (2 * m2 + 1 - i) // (i + 1)
    print("  组合总数 C(%d,%d) = %d；末 %d 个编号 = %d 至 %d" % (2 * m2 + 1, m2, total, m2, total - m2, total - 1))
    for r, sub in rows[-1 * m2:]:
        print("    编号 %d → %s" % (r, list(sub)))
    print("  末 m2 个捕捉子集互不相同 = %s；并集大小 = %d"
          % (len(set(s for _, s in rows[-m2:])) == m2, len(set(s for _, s in rows[-m2:]))))
    return rows


if __name__ == "__main__":
    for dd, m2 in (("m2_12_mpq", 12), ("m2_13_mpq", 13)):
        run(dd, m2)
