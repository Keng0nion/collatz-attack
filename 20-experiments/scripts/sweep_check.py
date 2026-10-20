#!/usr/bin/env python
"""sweep_check.py —— 把 sweep 的结果与 OEIS 数据逐条核对

读取（均由本脚本同目录的仓库文件提供，OEIS b 文件抓取自 oeis.org，抓取命令见输出）：
  results/oeis/b006577.txt   A006577：总停时 a(n) = 到达 1 的步数（n = 1..10000）
  results/oeis/b006877.txt   A006877：总停时纪录保持者（148 项，来自 Eric Roosendaal 表）
  results/oeis/b006878.txt   A006878：对应的纪录值（步数，148 项）
  results/sweep_lens.tsv     本次 sweep 导出的 (n, len[n])，n = 1..1000000
  results/sweep_records.tsv  本次 sweep 的全部（严格）纪录保持者

用法： .venv/bin/python scripts/sweep_check.py [append_to_file]
       给出第二个参数时，报告同时追加写入该文件（用于 results/sweep.txt）。
"""

import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
N_LIMIT = 268435456


class Tee(object):
    """把写入同时送到两个流（stdout 与日志文件）。"""

    def __init__(self, first, second):
        self.first = first
        self.second = second

    def write(self, s):
        self.first.write(s)
        self.second.write(s)

    def flush(self):
        self.first.flush()
        self.second.flush()


def read_bfile(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                rows.append((int(parts[0]), int(parts[1])))
    return rows


def read_tsv(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            rows.append(tuple(int(x) for x in line.split()))
    return rows


def collatz_steps(n):
    """独立实现：标准 3x+1 映射，Python 任意精度整数，逐步数到 1。"""
    c = 0
    while n != 1:
        if n % 2:
            n = 3 * n + 1
        else:
            n = n // 2
        c += 1
    return c


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else None
    fp = None
    orig_stdout = sys.stdout
    if out_path is not None:
        fp = open(out_path, "a")
        fp.write("\n\n# ==================================================================\n")
        fp.write("# OEIS cross-check report (appended by scripts/sweep_check.py)\n")
        fp.write("# ==================================================================\n")
        sys.stdout = Tee(orig_stdout, fp)

    base = os.path.join(EXP, "results")
    a577 = dict(read_bfile(os.path.join(base, "oeis", "b006577.txt")))
    a877 = [v for _, v in read_bfile(os.path.join(base, "oeis", "b006877.txt"))]
    a878 = dict(read_bfile(os.path.join(base, "oeis", "b006878.txt")))
    lens = dict(read_tsv(os.path.join(base, "sweep_lens.tsv")))
    recs = read_tsv(os.path.join(base, "sweep_records.tsv"))

    print("== OEIS cross-check (scripts/sweep_check.py) ==")
    print("sweep limit N = %d" % N_LIMIT)
    print("reproduction commands (run from collatz-attack/20-experiments):")
    print("  curl -s -o results/oeis/b006577.txt https://oeis.org/A006577/b006577.txt")
    print("  curl -s -o results/oeis/b006877.txt https://oeis.org/A006877/b006877.txt")
    print("  curl -s -o results/oeis/b006878.txt https://oeis.org/A006878/b006878.txt")
    print("  cc -O3 -Wall -Wextra -o scripts/sweep scripts/sweep.c")
    print("  /usr/bin/time -p ./scripts/sweep 268435456 results/sweep_records.tsv results/sweep_lens.tsv > results/sweep.txt 2> results/sweep.stderr")
    print("  ./.venv/bin/python scripts/sweep_check.py results/sweep.txt")
    stderr_path = os.path.join(base, "sweep.stderr")
    if os.path.exists(stderr_path):
        print("wall clock of the sweep run (read from results/sweep.stderr, produced by /usr/bin/time -p):")
        with open(stderr_path) as f:
            for line in f:
                line = line.rstrip("\n")
                if line:
                    print("  " + line)

    print("")
    print("-- 1. A006577 (total stopping time) item by item --")
    print("b-file terms: %d (n = 1..%d), sweep dump covers n = 1..%d" % (len(a577), max(a577), max(lens)))
    missing = 0
    mismatch = []
    for n in sorted(a577):
        if n not in lens:
            missing += 1
            if missing <= 5:
                print("  MISSING in sweep dump: n = %d" % n)
            continue
        if lens[n] != a577[n]:
            mismatch.append((n, lens[n], a577[n]))
    print("compared: %d   mismatch: %d   missing: %d" % (len(a577) - missing, len(mismatch), missing))
    for row in mismatch[:20]:
        print("  MISMATCH n=%d sweep=%d oeis=%d" % row)
    print("first 24 terms side by side (n: oeis / sweep):")
    head = []
    for n in range(1, 25):
        head.append("%d:%d/%d" % (n, a577.get(n, -1), lens.get(n, -1)))
    print("  " + " ".join(head))

    print("")
    print("-- 2. A006877 (record holders) vs sweep record list --")
    in_range = [v for v in a877 if v <= N_LIMIT]
    out_range = [v for v in a877 if v > N_LIMIT]
    print("A006877 terms: %d, within N: %d, beyond N: %d" % (len(a877), len(in_range), len(out_range)))
    print("sweep record list length: %d" % len(recs))
    print("")
    print("idx  A006877_n        sweep_n         A006878_steps  sweep_steps   match")
    nbad = 0
    for i in range(max(len(in_range), len(recs))):
        idx = i + 1
        on = in_range[i] if i < len(in_range) else None
        sn = recs[i][1] if i < len(recs) else None
        ostep = a878.get(idx) if on is not None else None
        sstep = recs[i][2] if i < len(recs) else None
        ok = (on == sn) and (ostep == sstep)
        if not ok:
            nbad += 1
        print("%-4d %-15s %-15s %-14s %-13s %s" % (
            idx, on, sn, ostep, sstep, "OK" if ok else "MISMATCH"))
    print("")
    print("record rows compared: %d   mismatch: %d" % (max(len(in_range), len(recs)), nbad))
    if out_range:
        print("beyond N (not checked, sweep cannot reach them): first 10 = %s" % out_range[:10])

    print("")
    print("-- 3. self-consistency of the sweep record list --")
    inc_n = all(recs[i][1] < recs[i + 1][1] for i in range(len(recs) - 1))
    inc_s = all(recs[i][2] < recs[i + 1][2] for i in range(len(recs) - 1))
    print("n strictly increasing: %s" % inc_n)
    print("steps strictly increasing: %s" % inc_s)
    print("last record (max total stopping time in range): n = %d steps = %d" % (recs[-1][1], recs[-1][2]))
    print("first record: n = %d steps = %d" % (recs[0][1], recs[0][2]))

    print("")
    print("-- 4. independent re-simulation in Python (arbitrary precision) --")
    pybad = 0
    for row in recs:
        n = row[1]
        s = row[2]
        if collatz_steps(n) != s:
            pybad += 1
            print("  MISMATCH record n=%d python=%d sweep=%d" % (n, collatz_steps(n), s))
    print("record holders re-simulated with Python big ints: %d   mismatch: %d" % (len(recs), pybad))
    import random
    rnd = random.Random(20261018)
    pybad2 = 0
    nsamp = 3000
    for _ in range(nsamp):
        n = rnd.randint(1, 1000000)
        if collatz_steps(n) != lens[n]:
            pybad2 += 1
            if pybad2 <= 5:
                print("  MISMATCH sample n=%d python=%d sweep=%d" % (n, collatz_steps(n), lens[n]))
    print("random n in [1, 1000000] re-simulated in Python: %d   mismatch: %d" % (nsamp, pybad2))
    print("note: every Python step is done on arbitrary precision integers, no 64 bit truncation possible")

    verdict = "ALL CONSISTENT"
    if missing or mismatch or nbad or not inc_n or not inc_s or pybad or pybad2:
        verdict = "DISCREPANCIES FOUND (listed above)"
    print("")
    print("verdict: %s" % verdict)

    if fp is not None:
        sys.stdout = orig_stdout
        fp.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
