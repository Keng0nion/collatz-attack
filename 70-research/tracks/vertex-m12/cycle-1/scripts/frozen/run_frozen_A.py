#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""以冻结副本运行 r2_j_independent_vertices.py 的 A 段（与基线同路径）。

做法：先把本目录（frozen/）置于 sys.path[0] 并抢先导入 r2_common（冻结副本），
再用 runpy 以 __main__ 身份执行冻结脚本；脚本内部对 r2_common 的导入因
sys.modules 已缓存而命中冻结副本，不会被其自身 line 27 的 sys.path.insert
拉到上游目录。核对信息打印到 stderr，stdout 保持与基线同格式，便于逐行对拍。

用法：
    "<venv>/python" run_frozen_A.py > <日志> 2> <stderr 记录>
"""
import hashlib
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2_common

if os.path.abspath(r2_common.__file__) != os.path.join(HERE, "r2_common.py"):
    raise SystemExit(f"r2_common 未命中冻结副本：{r2_common.__file__}")

SCRIPT = os.path.join(HERE, "r2_j_independent_vertices.py")


def md5f(path):
    # md5 在此只作「版本身份指纹」，用于与本项目既有记录的 md5 清单对读，
    # 不用于任何安全用途（安全用途须换 SHA-256 及以上）。
    h = hashlib.md5()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 16), b""):
            h.update(blk)
    return h.hexdigest()


print(f"[run_frozen_A] python = {sys.version.split()[0]}", file=sys.stderr, flush=True)
print(f"[run_frozen_A] r2_common 加载自 {r2_common.__file__}（md5 {md5f(r2_common.__file__)}）",
      file=sys.stderr, flush=True)
print(f"[run_frozen_A] 冻结脚本 = {SCRIPT}（md5 {md5f(SCRIPT)}）", file=sys.stderr, flush=True)
sys.argv = [SCRIPT, "A"]
runpy.run_path(SCRIPT, run_name="__main__")
