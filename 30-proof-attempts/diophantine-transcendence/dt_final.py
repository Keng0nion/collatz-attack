#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
# -*- coding: utf-8 -*-
"""丢番图路线 · 探针 5：达到给定排除前沿 m 所需的验证界 X0。

【重要更正（2026 年 10 月 19 日，回应独立反驳）】本脚本的 X0min 取
    X0min(m) = min over q_n >= K_up(m) of min(c*m, cK*q_n) / (ln2*|q_n delta - p_n|)，
即收敛项分母取「不小于 K_up 的最小者」。这只是【充分条件】，不是最省的选择：
按同一份报告的结论 A（min_{K<=M} ||K delta|| = |q_N delta - p_N|，q_N 为不超过 M 的
最大收敛项分母），应当把结论 A 用在 M = K_up(m) 上，于是更省的门槛是
    X0min*(m) = min(c*m, cK*K_up(m)) / (ln2 * psi(K_up(m)))，psi(M) = |q_N delta - p_N|。
两者之比在 m = 70 至 120 上为 1.03 至 55.5 倍（m = 91 处 4.02 倍，m = 100 处 55.5 倍）。
本脚本保留旧口径仅供对照；【正确口径见 dt_fix2.py】，本报告第 6 步的表格已按它重算。
本脚本此前声称这两个量「充要」「等价」，那是错的：本文所有「所需 X0」都只是
「在『第 2 步的 K_up + 结论 A + 窗口上界』这条链内足以推出矛盾」的门槛，
链内它不能再降（见 dt_fix.py 第 (3) 节），但链外是否有别的机制，本报告不声称。

对参数 m，旧口径的推导如下：
    Q0 >= m/(ln2*|q_n delta - p_n|)  且  q_n >= K_up(m)  ==>  K > q_n >= K_up(m)，矛盾。
"""
import sys
import mpmath as mp

DPS = 160


def setup(nmax=130):
    mp.mp.dps = DPS
    d = mp.log(3) / mp.log(2)
    a, ps, qs = [], [], []
    x = d
    pm2, pm1, qm2, qm1 = mp.mpf(0), mp.mpf(1), mp.mpf(1), mp.mpf(0)
    for n in range(nmax):
        ai = int(mp.floor(x))
        a.append(ai)
        pn, qn = ai * pm1 + pm2, ai * qm1 + qm2
        ps.append(pn); qs.append(qn)
        pm2, pm1 = pm1, pn
        qm2, qm1 = qm1, qn
        x = 1 / (x - ai)
    return d, ps, qs


def c_m(m, delta, X0):
    b = (1 + 1 / X0) ** (1 / delta) / mp.mpf(2) ** (1 / delta)
    # E_m = sum_{i=1}^{m-1} (m-i) delta^i，用递推避免重复求和
    E = mp.mpf(0)
    for i in range(1, m):
        E += (m - i) * delta ** i
    ex = (delta - 1) / (delta ** m - 1)
    return (1 + 1 / X0) ** (m * ex) * b ** (E * ex)


def K1_rhin(m, delta, X0, cm):
    """Lemma 14 的 K1(m)：ln g(x) = 0 的较大根，
    g(x) = m c_m 2^{-(delta-1)x/(delta^m-1)} / e^{-13.3(0.46057+ln x)}。
    ln g 在 x* = 13.3(delta^m-1)/((delta-1)ln2) 处取极大，较大根 > x*。"""
    A = m * cm

    def f(x):
        return (mp.log(A) - (delta - 1) * x * mp.log(2) / (delta ** m - 1)
                + mp.mpf("13.3") * (mp.mpf("0.46057") + mp.log(x)))
    xstar = mp.mpf("13.3") * (delta ** m - 1) / ((delta - 1) * mp.log(2))
    if f(xstar) <= 0:
        return mp.mpf(0)          # 无根：该 m 无条件不可能（视为 K_up = 0，恒被排除）
    lo, hi = xstar, xstar
    while f(hi) > 0:
        hi *= 2
    for _ in range(500):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return hi


def K_up_cf(m, delta, X0, ps, qs, cm):
    """K 可行集 = ∪_N [q_N, min(q_N+1, R_N))，其中 R_N 由 Lemma 7 与连分数下界给出。
    返回该集合的上确界。"""
    best = mp.mpf(0)
    for N in range(0, len(qs) - 2):
        L = mp.log(2) * abs(qs[N] * delta - ps[N])
        R = (delta ** m - 1) * (mp.log(1 / L) + mp.log(m * cm)) / ((delta - 1) * mp.log(2))
        if qs[N] < R:
            best = max(best, min(qs[N + 1] - 1, mp.floor(R)))
    return best


def K_up_ideal(m, delta, X0, cm):
    return (delta ** m - 1) * mp.log(m * cm) / ((delta - 1) * mp.log(2))


def X0min(m, K_up, delta, ps, qs, c_m_form=False):
    """能达到「参数 m 被排除」的最小 X0（用 |q_n delta - p_n| 的精确值，而非粗下界 1/(q_n+q_n+1)）。

    设 K <= q_n。两条独立的 Lambda 上界都可与「Lambda >= ln2*|q_n delta - p_n|」矛盾：
      m 形态（SdW Corollary 5）：Lambda < m/X0            ==> X0 >= m/(ln2*|q_n d - p_n|)
      K 形态（Eliahou、Hercher、本项目）：Lambda <= K/(3X0-1) ==> 3X0-1 >= q_n/(ln2*|q_n d - p_n|)
    取两式中较小者，并对所有 q_n >= K_up(m) 取最小。"""
    best = None
    for i in range(0, len(qs) - 1):
        qn = qs[i]
        if qn >= K_up:
            v = abs(qn * delta - ps[i])
            cand_m = m / (mp.log(2) * v)
            cand_K = (qn / (mp.log(2) * v) + 1) / 3
            cand = min(cand_m, cand_K)
            if best is None or cand < best:
                best = cand
            break              # |q_n delta - p_n| 随 n 递减，最小者在最小的合格 n 处
    return best


def main():
    d, ps, qs = setup()
    X0_pub = mp.mpf("3.7469e18")
    MMAX = 300

    res = {"Rhin": {}, "CF": {}, "ideal": {}}
    for m in range(2, MMAX + 1):
        cm = c_m(m, d, X0_pub)
        res["Rhin"][m] = X0min(m, K1_rhin(m, d, X0_pub, cm), d, ps, qs)
        Ku = K_up_cf(m, d, X0_pub, ps, qs, cm)
        res["CF"][m] = X0min(m, Ku, d, ps, qs)
        res["ideal"][m] = X0min(m, K_up_ideal(m, d, X0_pub, cm), d, ps, qs)

    print("=" * 78)
    print("一、达到前沿 m 所需的验证界 X0（三种 K 上界口径）")
    print("=" * 78)
    print('X0 列写为「值（2 的幂次）」；"-" 表示收敛项表不足（该 m 需要的 K 上界超出表长）')
    print()
    print(f"{'前沿 m':>7} {'Rhin 口径 X0':>26} {'连分数口径 X0':>26} {'理想线性型 X0':>26}")
    for M in [20, 40, 60, 63, 68, 70, 74, 75, 80, 82, 90, 91, 100, 120, 150, 200, 300]:
        row = []
        for key in ["Rhin", "CF", "ideal"]:
            vals = [res[key][m] for m in range(2, M + 1)]
            if any(v is None for v in vals):
                row.append("-")
            else:
                X = max(vals)
                row.append(f"{mp.nstr(X, 6)} (2^{mp.nstr(mp.log(X, 2), 4)})")
        print(f"{M:>7} {row[0]:>26} {row[1]:>26} {row[2]:>26}")

    print()
    print("=" * 78)
    print("二、与两个文献门槛对照")
    print("=" * 78)
    B = mp.mpf(2) ** 71
    H = 1536 * mp.mpf(2) ** 60
    print(f"  Barina 2025 验证界 2^71 = {mp.nstr(B, 8)}")
    print(f"  Hercher 2023 Corollary 29 门槛 1536*2^60 = {mp.nstr(H, 8)}")
    for M in [75, 82, 91, 100, 150, 200]:
        parts = []
        for key in ["Rhin", "CF", "ideal"]:
            vals = [res[key][m] for m in range(2, M + 1)]
            if any(v is None for v in vals):
                parts.append("表长不足")
            else:
                X = max(vals)
                parts.append(f"{mp.nstr(X / B, 5)}x")
        print(f"  前沿 m >= {M:>4}: 所需 X0 相对 2^71 的倍数 —— "
              f"Rhin {parts[0]}, 连分数 {parts[1]}, 理想线性型 {parts[2]}")

    print()
    print("=" * 78)
    print("三、渐近斜率：X0 每乘 10 倍，前沿前进多少")
    print("=" * 78)
    print("（用连分数口径，取对数回归）")
    xs, ys = [], []
    for m in range(2, MMAX + 1):
        if res["CF"][m] is not None:
            xs.append(mp.log(res["CF"][m], 10))
            ys.append(m)
    # 取靠后的窗口做斜率
    for lo, hi in [(60, 100), (100, 200)]:
        idx = [i for i in range(len(xs)) if lo <= ys[i] <= hi]
        if len(idx) > 2:
            n = len(idx)
            sx = sum(xs[i] for i in idx) / n
            sy = sum(ys[i] for i in idx) / n
            sxx = sum((xs[i] - sx) ** 2 for i in idx)
            sxy = sum((xs[i] - sx) * (ys[i] - sy) for i in idx)
            slope = sxy / sxx
            print(f"  m 在 [{lo}, {hi}] 区间：拟合斜率 = {mp.nstr(slope, 5)}"
                  f"  （= log_10(delta) 的倒数 {mp.nstr(1/mp.log(d, 10), 5)}）")
    print()
    print("  含义：X0 每翻 10 倍，前沿只前进约 5 个 m。要排除全部 m 需要前沿无界，")
    print("        而任何有限 X0 只给出有限前沿 —— 这条路线任何有限验证界都走不到终点。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
