#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""独立核对：

一、把 C 程序 stoptime_dist 的逐点转储（n <= dump 上限）与一个独立的纯 Python
    实现（不用记忆化，直接模拟）逐点比对。
二、把转储中 n <= 10000 的部分与本地 OEIS b 文件 b006577.txt 逐点比对。
三、把 stoptime_records.txt 与本地 OEIS b 文件 b006877.txt（纪录 n）与
    b006878.txt（纪录值）在 n <= 2^24 的范围内逐条比对。

用法：./.venv/bin/python scripts/verify_stoptime.py <dump.csv> <N上限>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))
OEIS = os.path.join(RES, "oeis")


def tot_brute(n):
    c = 0
    while n != 1:
        n = 3 * n + 1 if n & 1 else n >> 1
        c += 1
    return c


def chi_std_brute(n):
    """Terras 停时（标准步）。n = 1 时无定义（1 到 4 到 2 到 1 永不小于自身），
    调用方必须排除 n = 1。"""
    assert n > 1, "chi 对 n = 1 无定义"
    m, c = n, 0
    while m >= n:
        m = 3 * m + 1 if m & 1 else m >> 1
        c += 1
    return c


def chi_acc_brute(n):
    """Terras 停时（加速步）。同样要求 n > 1。"""
    assert n > 1, "chi 对 n = 1 无定义"
    m, c = n, 0
    while m >= n:
        m = (3 * m + 1) // 2 if m & 1 else m // 2
        c += 1
    return c


def main():
    dump = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, "stoptime_dump.csv")
    Nl = int(sys.argv[2]) if len(sys.argv) > 2 else 1 << 18

    bad = 0
    checked = 0
    maxn = 0
    with open(dump) as f:
        next(f)
        for line in f:
            n, t, cs, ca = (int(x) for x in line.strip().split(","))
            if n > Nl:
                break
            bt, bcs, bca = tot_brute(n), -1, -1
            if n > 1:
                bcs, bca = chi_std_brute(n), chi_acc_brute(n)
                ok = (t, cs, ca) == (bt, bcs, bca)
            else:
                ok = (t == bt and cs == 0 and ca == 0)   # n = 1 的 chi 按 0 记录，不参与比对
            checked += 1
            maxn = n
            if not ok:
                bad += 1
                if bad <= 5:
                    print("不一致：n=%d 转储=(%d,%d,%d) 独立=(%d,%d,%d)" % (n, t, cs, ca, bt, bcs, bca))
    print("核对一（与独立纯 Python 实现逐点比对）：比对 %d 个 n（1 至 %d），不一致 %d 个"
          % (checked, maxn, bad))

    # 与 OEIS b006577 比对
    path = os.path.join(OEIS, "b006577.txt")
    bad2 = 0
    cnt2 = 0
    if os.path.exists(path):
        ref = {}
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                a, b = line.split()
                ref[int(a)] = int(b)
        with open(dump) as f:
            next(f)
            for line in f:
                n, t, cs, ca = (int(x) for x in line.strip().split(","))
                if n in ref:
                    cnt2 += 1
                    if ref[n] != t:
                        bad2 += 1
                        if bad2 <= 5:
                            print("与 OEIS 不一致：n=%d 本地=%d OEIS=%d" % (n, t, ref[n]))
        print("核对二（与本地 OEIS b006577.txt 比对）：比对 %d 个 n，不一致 %d 个；"
              "b 文件覆盖范围 1 至 %d" % (cnt2, bad2, max(ref)))
    else:
        print("核对二：未找到 %s，跳过" % path)

    # 与 OEIS 纪录序列比对
    p877 = os.path.join(OEIS, "b006877.txt")
    p878 = os.path.join(OEIS, "b006878.txt")
    LIM = 1 << 24
    if os.path.exists(p877) and os.path.exists(p878):
        rec_n, rec_v = [], []
        for p, dst in ((p877, rec_n), (p878, rec_v)):
            with open(p) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    a, b = line.split()
                    dst.append(int(b))
        pairs = [(a, b) for a, b in zip(rec_n, rec_v) if a <= LIM]
        mine = []
        with open(os.path.join(RES, "stoptime_records.txt")) as f:
            next(f)
            for line in f:
                a, b = line.strip().split(",")
                mine.append((int(a), int(b)))
        bad3 = 0
        for pair in pairs:
            if pair not in mine:
                bad3 += 1
                if bad3 <= 5:
                    print("纪录不一致：OEIS 有 %s，我的表里没有" % (pair,))
        extra = [p for p in mine if p not in pairs]
        print("核对三（与本地 OEIS 纪录序列比对，限 n <= 2^24）：")
        print("  OEIS 侧纪录 %d 条（最后一条 %s），我的表 %d 条（最后一条 %s）"
              % (len(pairs), pairs[-1], len(mine), mine[-1]))
        print("  OEIS 有而我没有的 %d 条；我有而 OEIS 没有的 %d 条" % (bad3, len(extra)))
        if extra:
            print("  多出的条目（前 5 条）：%s" % extra[:5])
    else:
        print("核对三：未找到 OEIS 纪录 b 文件，跳过")


if __name__ == "__main__":
    main()
