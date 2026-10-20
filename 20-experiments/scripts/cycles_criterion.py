#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
"""Eliahou 与 Crandall 型必要条件的实现与自算范围。

判据（本脚本自行推导，推导见下方 docstring 结尾；与文献里 Crandall 1978 的引理、
Eliahou 1993 的判别法同一机制，但常数由本工作独立给出并在已知环上核验）：

    设 T(n) = n/2（偶）、T(n) = (3n+1)/2（奇）。若整数上存在一个环：长度 k、奇数步 m 步、
    环上元素的绝对值最小者是 X*（并记 X0 为一个「已核验界」，即凡 |n| < X0 的整数都已被
    单独核验过到达 1（正侧）或到达三个已知负环之一（负侧）），则该环必满足

        X* >= X0,             （因为环上元素本身也必须被核验过）
        0 < |k*ln2 - m*ln3| = |sum_i ln(1 + 1/(3 x_i))| <= m / (3 X* - 1) <= m / (3 X0 - 1).

    其中第二式的推导：环方程乘积式 2^k = prod_i (3 + 1/x_i)，取对数得 k*ln2 - m*ln3
    = sum_i ln(1 + 1/(3 x_i))；再用 |ln(1+t)| <= |t|/(1-|t|)、|t| = 1/(3|x_i|) <= 1/(3 X*)
    得每项绝对值 <= 1/(3|x_i| - 1) <= 1/(3 X* - 1)，求和即得。

    于是对每个 m 有：若 min over 整数 n 的 |n*ln2 - m*ln3| = ln2 * ||m*delta||
    （delta = log2 3，||.|| 为到最近整数距离）大于 m/(3 X0 - 1)，则不存在奇数步数为 m 的环。
    记 M2(X0) = 使 m = 1, 2, ..., M2 全部被排除的最大 M2。
    因为任何环满足 k > m，故「不存在 m <= M2 的环」蕴含「不存在周期 <= M2 的环」。

本脚本做四件事：
1. 在四个已知环（1、-1、-5、-17 族）上核验上述不等式的常数（含边界情形）。
2. 对枚举搜索找到的全部解向量，核验每条解都满足该必要条件（必要条件被真实解违反即说明推导有错）。
3. 对若干 X0 值计算 M2(X0)，并给出对精度的稳定性检查（60 位与 200 位结果一致）与最小余量。
4. 给出连分数收敛项表，用于解释 M2 的台阶结构（台阶由 delta 的连分数决定）。

用法：python cycles_criterion.py <X0a> <X0b> ...
"""
import sys
import mpmath as mp

def delta_mp(dps):
    mp.mp.dps = dps
    return mp.log(3) / mp.log(2)

def dist_to_int(x):
    return abs(x - mp.nint(x))

def lambda_abs(k, m, dps):
    """|k*ln2 - m*ln3|，高精度。"""
    mp.mp.dps = dps
    return abs(k * mp.log(2) - m * mp.log(3))

def M2(X0, dps=60, mmax=300000, verbose=False):
    """返回 (M2, 第一个未被排除的 m, 最小余量, 余量最小处的 m)。
    排除判据：ln2 * ||m*delta|| > m / (3 X0 - 1)。"""
    mp.mp.dps = dps
    d = delta_mp(dps)
    ln2 = mp.log(2)
    mono = False
    first_open = None
    min_ratio = None
    argmin = None
    m = 1
    while m <= mmax:
        dmi = dist_to_int(d * m)
        if not mono:
            lhs = ln2 * dmi
            rhs = mp.mpf(m) / (3 * X0 - 1)
            ratio = lhs / rhs
            if ratio <= 1:
                first_open = m
                mono = True
            else:
                if min_ratio is None or ratio < min_ratio:
                    min_ratio = ratio; argmin = m
        m += 1
    if first_open is None:
        return None, None, min_ratio, argmin
    return first_open - 1, first_open, min_ratio, argmin

def convergents_of_delta(dp=60, count=20):
    """用高精度连分数展开求 delta = log2 3 的收敛项。"""
    mp.mp.dps = dp + 20
    x = mp.log(3) / mp.log(2)
    a = []
    for _ in range(count):
        ai = int(mp.floor(x))
        a.append(ai)
        x = 1 / (x - ai)
    p = [1, a[0]]
    q = [0, 1]
    for i in range(1, len(a)):
        p.append(a[i] * p[-1] + p[-2])
        q.append(a[i] * q[-1] + q[-2])
    return a, p[1:], q[1:]

def main():
    print("=" * 78)
    print("Eliahou 与 Crandall 型必要条件：实现、核验、自算范围")
    print("=" * 78)

    # ---- 1. 在已知环上核验不等式 ----
    print("\n[1] 已知环上核验必要条件 0 < |k ln2 - m ln3| <= m/(3|x_min| - 1)")
    known = [
        ("正整数环 {1,2}", 2, 1, 1),
        ("负整数环 {-1}", 1, 1, 1),
        ("负整数环 {-5,-7,-10}", 3, 2, 5),
        ("负整数环 -17 族", 11, 7, 17),
    ]
    ok = True
    for name, k, m, xmin in known:
        L = lambda_abs(k, m, 60)
        rhs = mp.mpf(m) / (3 * xmin - 1)
        good = (L <= rhs)
        ok = ok and good
        print(f"    {name:<22} k={k:>2} m={m:>2} |x_min|={xmin:>2}  "
              f"|Lambda|={mp.nstr(L, 12):>16}  m/(3|x_min|-1)={mp.nstr(rhs, 12):>16}  满足：{good}")
    print(f"    四个环全部满足：{ok}")

    # ---- 2. 枚举搜索的每条解向量也核验 ----
    print("\n[2] 对枚举搜索输出的每条解向量核验必要条件")
    import re
    sol_re = re.compile(r"^SOL k=(\d+) m=(\d+) x=(-?\d+) c=(\d+) D=(-?\d+) ones=")
    n_checked = 0
    n_bad = 0
    n_skip = 0
    worst = None
    path = "results/cycles_enum_exhaustive_k34.txt"
    try:
        for line in open(path, encoding="utf-8"):
            mm = sol_re.match(line)
            if not mm:
                continue
            k, m, x = int(mm.group(1)), int(mm.group(2)), int(mm.group(3))
            # 该环的 |x_min|：这里直接用 |x|（x 只是环上某元素，须用环的最小绝对值；
            # 由独立复核脚本已知每个解所属环，这里保守地用 |x| 作为上界不做此检验，
            # 改为用该环的真实最小绝对值：重算整条环）
            traj = [x]
            for _ in range(k):
                traj.append(traj[-1] // 2 if traj[-1] % 2 == 0 else (3 * traj[-1] + 1) // 2)
            d = next(i for i in range(1, k + 1) if traj[i] == x)
            elems = traj[:d]
            xmin = min(abs(v) for v in elems)
            m_ = sum(1 for v in elems if v % 2 != 0)
            if m_ == 0 or xmin == 0:
                n_skip += 1
                continue          # 不动点 0（m = 0）：判据的推导要求 x_i != 0，不适用
            L = lambda_abs(d, m_, 60)
            rhs = mp.mpf(m_) / (3 * xmin - 1)
            n_checked += 1
            ratio = L / rhs
            if worst is None or ratio > worst[0]:
                worst = (ratio, k, m, xmin, mp.nstr(L, 10), mp.nstr(rhs, 10))
            if L > rhs:
                n_bad += 1
                print(f"    违反：k={k} m={m} x={x} |Lambda|={mp.nstr(L,12)} rhs={mp.nstr(rhs,12)}")
    except FileNotFoundError:
        print(f"    （找不到 {path}，跳过）")
    print(f"    核验 {n_checked} 条环解，违反 {n_bad} 条（另有 {n_skip} 条为不动点 0，判据不适用）")
    if worst:
        print(f"    最紧的一条（比值 |Lambda| / 上界，越接近 1 越紧）：{float(worst[0]):.4f}  "
              f"k={worst[1]} m={worst[2]} |x_min|={worst[3]}  |Lambda|={worst[4]}  上界={worst[5]}")

    # ---- 3. M2(X0) ----
    print("\n[3] 各 X0 下的排除上界 M2（即：不存在奇数步数 m <= M2 的环）")
    xs = [int(a) for a in sys.argv[1:]] or [10**6, 10**8, 10**9]
    print(f"    {'X0':>22} {'M2':>14} {'首个未排除 m':>14} {'最小余量':>14} {'精度复核':>10}  （M2 上限扫描到 300000）")
    results = {}
    for X0 in xs:
        M, first_open, min_ratio, argmin = M2(X0, dps=60)
        M200, fo200, mr200, am200 = M2(X0, dps=200)
        stable = (M == M200)
        results[X0] = (M, first_open, min_ratio, argmin, stable)
        print(f"    {X0:>22} {str(M):>14} {str(first_open):>14} "
              f"{mp.nstr(min_ratio, 6):>14} {'一致' if stable else '不一致！':>10}")
    # 台阶解释：未排除的 m 必然落在收敛项分母附近
    print("\n    M2 的台阶由 delta = log2 3 的连分数决定。收敛项分母 q_n：")
    a, p, q = convergents_of_delta(80, 24)
    print("    部分商 a_n：", a[:20])
    for i in range(min(22, len(q))):
        print(f"      n={i:>2} a={a[i]:>3} p={p[i]:>25} q={q[i]:>25}")

    # ---- 4. 与已知环的对照：M2 必须不小于已知环的 m ----
    print("\n[4] 一致性检查：已知环的 m 必须不在被排除集合里（否则判据自相矛盾）")
    for X0 in xs:
        M = results[X0][0]
        # 只有 |x_min| >= X0 的环才受该验证界的约束
        constrained = [(name, m, xmin) for (name, _, m, xmin) in known if xmin >= X0]
        bad = [x for x in constrained if M is not None and x[1] <= M]
        print(f"    X0={X0}: M2={M}；受该验证界约束（|x_min| >= X0）的已知环："
              f"{[(n, m) for (n, m, _) in constrained]}")
        print(f"        其中奇与数步数 m <= M2 因而会与判据冲突的：{bad}（应为空）")

if __name__ == "__main__":
    main()
