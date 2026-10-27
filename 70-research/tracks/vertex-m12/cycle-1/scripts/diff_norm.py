#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""归一化用时数字后逐行对拍两份日志（用于 r2_j_A.txt 与冻结重跑的对拍）。

只归一化两类用时痕迹：
    「（数字 s）」→「（TS s）」；「用时 数字 s」→「用时 TS s」
其余逐字节比较。一致时退出码 0 并打印行数；不一致时打印统一 diff 并退出码 1。

用法：
    "<venv>/python" diff_norm.py <基线日志> <重跑日志>
"""
import difflib
import re
import sys


def norm(path):
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh.read().splitlines():
            line = re.sub(r"（\d+ s）", "（TS s）", line)
            line = re.sub(r"用时 \d+(?:\.\d+)? s", "用时 TS s", line)
            out.append(line)
    return out


def main():
    if len(sys.argv) != 3:
        print("用法：diff_norm.py <基线日志> <重跑日志>")
        return 2
    a, b = sys.argv[1], sys.argv[2]
    A, B = norm(a), norm(b)
    print(f"对拍：基线 = {a}")
    print(f"      重跑 = {b}")
    print("归一化规则：『（数字 s）』与『用时 数字 s』中的时间数字统一写为 TS；其余逐字节比较")
    if A == B:
        print(f"归一化后逐行一致：True；两文件行数 = {len(A)} / {len(B)}")
        return 0
    print(f"归一化后逐行一致：False；行数 = {len(A)} / {len(B)}")
    for line in difflib.unified_diff(A, B, fromfile=a, tofile=b, lineterm="", n=1):
        print(line)
    return 1


if __name__ == "__main__":
    sys.exit(main())
