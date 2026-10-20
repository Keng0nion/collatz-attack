#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
"""对照检查：把本项目文献笔记转述的 Crandall 引理形式与自推判据放在同一 X0 下比较。

Crandall 引理的形式取自本项目 10-literature/notes/cycles.md 第 2 条（转述自 Simons 与 de Weger
对 Crandall 1978 的引用，原文我未打开）：若 p_n/q_n 是 delta = log 3 除以 log 2 的收敛项
且 n >= 4，则非平凡 m 圈的奇数步数 K > min(q_n, 2*x_min/(q_n + q_(n+1)))。

最大化右边的 n 给出该引理在同一验证界下的 K 下界。本脚本把它与自推的单侧窗口判据
（cycles_criterion_exact_M.py 给出的 M+）并列，用于判断两者的量级关系是否合理。

用法：python cycles_crandall_crosscheck.py <X0> [<X0> ...]
"""
import sys
import mpmath as mp

def convergents(dp=80, count=30):
    mp.mp.dps = dp
    x = mp.log(3) / mp.log(2)
    a = []
    for _ in range(count):
        ai = int(mp.floor(x)); a.append(ai); x = 1 / (x - ai)
    p = [1, a[0]]; q = [0, 1]
    for i in range(1, len(a)):
        p.append(a[i] * p[-1] + p[-2]); q.append(a[i] * q[-1] + q[-2])
    return a, p[1:], q[1:]

def crandall_K(X0):
    a, p, q = convergents()
    best = (0, None)
    for n in range(4, len(q) - 1):
        v = min(q[n], 2 * mp.mpf(X0) / (q[n] + q[n + 1]))
        if v > best[0]:
            best = (v, n)
    return best

def main():
    xs = [int(t) for t in sys.argv[1:]] or [10**10]
    a, p, q = convergents()
    print("delta = log2 3 的收敛项（供对照）：")
    for n in range(6, 16):
        print(f"  n={n:>2} a={a[n]:>3} p_n={p[n]:>14} q_n={q[n]:>14}")
    print()
    for X0 in xs:
        v, n = crandall_K(X0)
        print(f"X0 = {X0}: 按 Crandall 引理形式得 K > {mp.nstr(v, 8)}（在 n = {n} 处取得）；"
              f"本工作判据在同一 X0 下给 M+ 与 M−（见 cycles_criterion_exact_M.py）")

if __name__ == "__main__":
    main()
