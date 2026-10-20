#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
"""独立复核 cycles_verify_bound 导出的 good 表（前 10^6 项）与 Python 完整迭代对照。

用法：python cycles_verify_dump_check.py [dump 文件] [上限]
默认读 results/verify_bound_dump_pos.txt，上限 10^6。
判定：n 到达 1 当且仅当完全迭代 T 能到 1（本范围 10^6 内必然终止）。
"""
import sys

def T(x):
    return x // 2 if x % 2 == 0 else (3 * x + 1) // 2

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "results/verify_bound_dump_pos.txt"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10**6
    good = {}
    for line in open(path, encoding="utf-8"):
        a, b = line.split()
        good[int(a)] = int(b)
    print(f"读入 {len(good)} 项（来自 {path}）")
    bad = 0
    for n in range(1, min(limit, max(good)) + 1):
        v = n
        while v != 1:
            v = T(v)
        if good.get(n) != 1:
            bad += 1
            if bad < 5:
                print("不一致：", n, good.get(n))
    print(f"完整迭代对照 {min(limit, max(good))} 项，不一致 {bad}")
    print(f"表中标为「到达 1」的项数：{sum(good.values())}")

if __name__ == "__main__":
    main()
