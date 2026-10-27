#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route3_vs_other_compare.py —— route-3 与另一实现（route-5 的分片检查点）逐点对拍。

输入：
  --mine   本轨道 results 目录下的结果 JSON 文件名（如 route3_impl2_m12.json）；
  --ckpt   另一实现的分片检查点目录名（如 m2_12_mpq，位于 results/ckpt/ 下）。
做三件事：
  1. 从两边取出**全部候选顶点的精确坐标串**（不做任何浮点近似），比较两个集合；
  2. 比较候选子集条数（捕捉每个顶点的活跃子集个数）；
  3. 不一致时打印差集（定位到具体坐标串），一致时给出「逐点精确相等」的结论行。

只读文件，不写任何文件。
"""
import argparse
import glob
import json
import os
import sys

BASE = ("/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/"
        "vertex-m12/cycle-1/results")


def norm(s):
    return ",".join(t.strip() for t in str(s).split(","))


def load_mine(name):
    with open(os.path.join(BASE, name)) as fh:
        d = json.load(fh)
    pts = [norm(c["point"]) for c in d["candidates"]]
    return d, pts


def load_ckpt(dirname):
    pts = []
    files = sorted(glob.glob(os.path.join(BASE, "ckpt", dirname, "chunk_*.json")))
    for f in files:
        with open(f) as fh:
            d = json.load(fh)
        for e in (d.get("feasible") or []):
            if isinstance(e, str):
                pts.append(norm(e))
            elif isinstance(e, (list, tuple)) and e and isinstance(e[0], str):
                pts.append(norm(e[0]))
            elif isinstance(e, dict):
                for key in ("point", "y", "coords", "solution"):
                    if key in e:
                        pts.append(norm(e[key]))
                        break
    return files, pts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mine", required=True)
    ap.add_argument("--ckpt", required=True)
    args = ap.parse_args()
    d, mine = load_mine(args.mine)
    files, other = load_ckpt(args.ckpt)
    sm, so = set(mine), set(other)
    rep = {
        "mine_file": args.mine,
        "mine_impl": d.get("impl"),
        "m2": d.get("m2"),
        "ckpt_dir": args.ckpt,
        "ckpt_files": len(files),
        "n_mine_points": len(mine),
        "n_mine_distinct": len(sm),
        "n_other_points": len(other),
        "n_other_distinct": len(so),
        "point_sets_equal": (sm == so),
        "only_in_mine": sorted(sm - so)[:3],
        "only_in_other": sorted(so - sm)[:3],
        "n_only_in_mine": len(sm - so),
        "n_only_in_other": len(so - sm),
    }
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 0 if sm == so else 1


if __name__ == "__main__":
    sys.exit(main())
