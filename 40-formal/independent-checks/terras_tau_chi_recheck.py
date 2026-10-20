"""独立验算 V：Terras 系数停时猜想的独立检验，以及首降向量计数表的独立复算。

被复核的对象（来自 20-experiments/findings/parity-vectors.md）：
1. K3：Terras 系数停时猜想 τ(n) = χ(n)（n ≥ 2）在 x ≤ 2^30 上无例外。
2. L3：χ(n) ≥ τ(n) 对一切 n ≥ 1 成立（一行定理）。
3. A(k) 表（首降向量计数，k = 1 至 18）：1 1 0 1 2 0 3 7 0 12 0 30 85 0 173 476 0 961，
   其中 A(3) = 0 是对全部正整数成立的结构性事实（因此 χ 取不到 3）。

定义（本脚本自行实现，不复用实验代码；第一版曾把定义写错，见文末「实现史」）：
- 加速映射 T(n) = n/2（n 偶）、(3n+1)/2（n 奇），每步恰好消耗一个 2 的因子；
  此时仿射公式 T^k(n) = (3^m n + c)/2^k 成立（m 为 k 步中的奇数步数）。
- χ(n)：最小的 k 使 T^k(n) < n（加速映射下的首降步数；与 σ（总停时）不同，σ 是走到 1 的步数）。
- τ(n)：最小的 k 使 3^{m_k(n)} < 2^k，m_k 为前 k 步中的奇数步数。
- 首降向量：长度 k 的奇偶向量，满足对所有 j < k 有 3^{m_j} ≥ 2^j、且 3^{m_k} < 2^k。

运行：
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
      40-formal/independent-checks/terras_tau_chi_recheck.py
"""

POW3 = [3**i for i in range(100)]
POW2 = [2**i for i in range(100)]


def chi_and_tau(n):
    """加速映射下的 (χ, τ)。要求 n ≥ 2。"""
    x = n
    m = 0
    p3 = 1
    tau = -1
    k = 0
    while True:
        k += 1
        if x % 2 == 1:
            x = (3 * x + 1) // 2
            m += 1
            p3 *= 3
        else:
            x = x // 2
        if tau < 0 and p3 < (1 << k):
            tau = k
        if x < n:
            return (k, tau)
        if k > 20000:
            raise RuntimeError(f"χ 超过安全上限：n={n}")


def sigma_acc(n):
    """加速映射下走到 1 的步数（另一个脚本 reverse_tree_recheck.py 里的 σ）。"""
    steps = 0
    x = n
    while x != 1:
        x = x // 2 if x % 2 == 0 else (3 * x + 1) // 2
        steps += 1
    return steps


def count_first_descent_vectors(kmax):
    """独立枚举首降向量，返回 A(k)（下标 1 至 kmax）。"""
    res = [0] * (kmax + 1)
    for k in range(1, kmax + 1):
        cnt = 0
        for v in range(1 << k):
            m = 0
            ok = True
            for j in range(1, k + 1):
                if (v >> (k - j)) & 1:
                    m += 1
                if j < k:
                    if POW3[m] < POW2[j]:
                        ok = False
                        break
                else:
                    if not (POW3[m] < POW2[k]):
                        ok = False
            if ok:
                cnt += 1
        res[k] = cnt
    return res


def main():
    N = 1 << 22
    print("== 零、定义锚点自检 ==")
    for n, expect in ((27, 70), (837799, 329), (626331, 319)):
        print(f"  χ({n})（首降步数，加速映射）= {chi_and_tau(n)[0]}；"
              f"独立算的 σ({n})（走到 1 的步数）= {sigma_acc(n)}，报告 σ = {expect}")
    print("  （χ 与 σ 是两个不同的量：χ 是首次跌破自身的步数，σ 是走到 1 的步数。）")
    print()

    print(f"== 一、τ 与 χ 的独立检验（n = 2 至 {N}）==")
    viol_eq = []
    viol_ge = []
    hist = {}
    max_chi = 0
    argmax = 2
    for n in range(2, N + 1):
        c, t = chi_and_tau(n)
        if t < 0 or c < t:
            viol_ge.append((n, c, t))
        if c != t:
            viol_eq.append((n, c, t))
        hist[c] = hist.get(c, 0) + 1
        if c > max_chi:
            max_chi = c
            argmax = n
    print(f"  χ 的最大值 = {max_chi}（在 n = {argmax}）")
    print(f"  χ < τ 的数目（χ ≥ τ 是定理，应恒为 0）= {len(viol_ge)}")
    print(f"  χ ≠ τ 的数目（Terras 猜想的反例数）= {len(viol_eq)}")
    if viol_eq:
        print(f"  前几个反例：{viol_eq[:10]}")
    print()

    print("== 二、空层集核对 ==")
    empty = [k for k in range(1, max_chi + 1) if hist.get(k, 0) == 0]
    head = empty[:14]
    print(f"  本范围内取值为空的 χ 值（前 14 个）：{head}")
    print(f"  实验报告在 x ≤ 2^30 上观察到的前 14 个空值：3、6、9、11、14、17、19、22、25、28、30、33、36、38")
    print()

    print("== 三、A(k) 表的独立复算（k = 1 至 18）==")
    A = count_first_descent_vectors(18)
    mine = [A[k] for k in range(1, 19)]
    report = [1, 1, 0, 1, 2, 0, 3, 7, 0, 12, 0, 30, 85, 0, 173, 476, 0, 961]
    print(f"  我算：{mine}")
    print(f"  报告：{report}")
    print(f"  逐项一致：{mine == report}")
    print(f"  我算的零项 k：{[k for k in range(1, 19) if A[k] == 0]}")
    print(f"  与第二节空值集合的前几个（3、6、9、11、14、17）是否吻合："
          f"{[k for k in range(1, 19) if A[k] == 0] == [3, 6, 9, 11, 14, 17]}")
    print()

    print("== 实现史（保留，供后来者避坑）==")
    print("  第一版把 χ 与 τ 都写在标准映射下，且系数条件写成 3^m 对 2^k。")
    print("  标准映射的仿射公式分母是 2 的 (k 减 m) 次方，不是 2^k，所以那个写法")
    print("  既用了错的映射（首降），又用了错的系数指数，导致把一半的 n 报成「反例」。")


if __name__ == "__main__":
    main()
