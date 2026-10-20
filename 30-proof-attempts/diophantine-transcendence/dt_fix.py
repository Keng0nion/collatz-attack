#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
# -*- coding: utf-8 -*-
"""丢番图路线 · 探针 7：对独立反驳的复核。

反驳的核心指控：dt_final.py 的 X0min 取「不小于 K_up 的最小收敛项分母」，
而按结论 A（不超过 M 的最大收敛项分母给 min_{K<=M} ||K delta||）应当取
「不超过 K_up 的最大收敛项分母」。后者给出更大的 |q delta - p|，故更省 X0。
本脚本三件事：
  (1) 逐点核验结论 A 在 M 取「收敛项分母」「下一个收敛项减一」「两者中点」三档时成立；
  (2) 用精确值证明 |q_n delta - p_n| 关于 n 单调递减（报告里的一个隐含前提）；
  (3) 同时按「旧口径（最小 q_n >= K_up）」与「反驳口径（最大 q_n <= K_up）」计算
      X0min 与 M 表，并给出各种文献常数的列。

用法：.venv/bin/python dt_fix.py
"""
import sys
import mpmath as mp

DPS = 160


def setup(nmax=140):
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


def psi(M, d, ps, qs):
    """min_{1<=K<=M} ||K delta|| = |q_N delta - p_N|，q_N 为不超过 M 的最大收敛项分母。"""
    idx = None
    for i in range(len(qs)):
        if qs[i] <= M:
            idx = i
        else:
            break
    return abs(qs[idx] * d - ps[idx]), idx


def c_m(m, delta, X0):
    b = (1 + 1 / X0) ** (1 / delta) / mp.mpf(2) ** (1 / delta)
    E = mp.mpf(0)
    for i in range(1, m):
        E += (m - i) * delta ** i
    ex = (delta - 1) / (delta ** m - 1)
    return (1 + 1 / X0) ** (m * ex) * b ** (E * ex)


def K1_rhin(m, delta, X0, cm):
    A = m * cm

    def f(x):
        return (mp.log(A) - (delta - 1) * x * mp.log(2) / (delta ** m - 1)
                + mp.mpf("13.3") * (mp.mpf("0.46057") + mp.log(x)))
    xstar = mp.mpf("13.3") * (delta ** m - 1) / ((delta - 1) * mp.log(2))
    if f(xstar) <= 0:
        return mp.mpf(0)
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


def K_up_cf(m, delta, ps, qs, cm):
    best = mp.mpf(0)
    for N in range(0, len(qs) - 2):
        L = mp.log(2) * abs(qs[N] * delta - ps[N])
        R = (delta ** m - 1) * (mp.log(1 / L) + mp.log(m * cm)) / ((delta - 1) * mp.log(2))
        if qs[N] < R:
            best = max(best, min(qs[N + 1] - 1, mp.floor(R)))
    return best


def K_up_ideal(m, delta, cm):
    return (delta ** m - 1) * mp.log(m * cm) / ((delta - 1) * mp.log(2))


C_MFORM = {"SdW Cor 5 (c=1)": mp.mpf(1),
           "H23 Cor 17 (c=97/162)": mp.mpf(97) / 162,
           "H23 Cor 19 (c=7/15)": mp.mpf(7) / 15}
C_KFORM = {"本项目 (cK=1/3)": mp.mpf(1) / 3, "H23 Thm 27 (cK=1/4)": mp.mpf(1) / 4}


def X0_old(m, K_up, d, ps, qs, c_mf=mp.mpf(1), c_kf=mp.mpf(1) / 3):
    """旧口径：q_n 取「不小于 K_up 的最小收敛项分母」。"""
    for i in range(len(qs) - 1):
        if qs[i] >= K_up:
            v = abs(qs[i] * d - ps[i])
            return min(c_mf * m / (mp.log(2) * v), c_kf * qs[i] / (mp.log(2) * v))
    return None


def X0_new(m, K_up, d, ps, qs, c_mf=mp.mpf(1), c_kf=mp.mpf(1) / 3):
    """反驳口径：用结论 A 于 M = K_up，取「不超过 K_up 的最大收敛项分母」。"""
    v, _ = psi(K_up, d, ps, qs)
    return min(c_mf * m / (mp.log(2) * v), c_kf * K_up / (mp.log(2) * v))


def main():
    d, ps, qs = setup()
    X0_pub = mp.mpf("3.7469e18")

    print("=" * 78)
    print("(1) 核验结论 A：min_{1<=K<=M} ||K delta|| == |q_N delta - p_N|，q_N 为不超过 M 的最大收敛项")
    print("=" * 78)
    for n in [8, 11, 13]:
        Q, Qn = int(qs[n]), int(qs[n + 1])
        for M in [Q, Qn - 1, (Q + Qn - 1) // 2]:
            best = None
            for K in range(1, M + 1):
                v = abs(K * d - mp.nint(K * d))
                if best is None or v < best:
                    best = v
            pred, idx = psi(mp.mpf(M), d, ps, qs)
            print(f"  M = {M:>10}（q_{n} = {Q}, q_{n+1} = {Qn}）: 暴力 = {mp.nstr(best, 16)}, "
                  f"预测(q_{idx}) = {mp.nstr(pred, 16)}, 比 = {mp.nstr(best / pred, 8)}")

    print()
    print("=" * 78)
    print("(2) |q_n delta - p_n| 单调递减的核验（报告里隐含用到）")
    print("=" * 78)
    mono = True
    for n in range(0, 40):
        a = abs(qs[n] * d - ps[n])
        b = abs(qs[n + 1] * d - ps[n + 1])
        if not (b < a):
            mono = False
            print(f"  *** n = {n} 处不降：{mp.nstr(a, 12)} -> {mp.nstr(b, 12)}")
    print("  n = 0 至 40 全部严格递减" if mono else "  *** 存在非递减处 ***")
    print("  证明要点：|q_(n+1)a - p_(n+1)| < 1/q_(n+2) <= 1/(q_n+q_(n+1)) < |q_n a - p_n|")
    print("  （用 q_(n+2) >= q_(n+1) + q_n 与 Lemma 9(b) 的下界）")

    print()
    print("=" * 78)
    print("(3) 旧口径与反驳口径的对比（K_up 用连分数版）")
    print("=" * 78)
    print(f"{'m':>4} {'K_up^CF':>22} {'旧 X0 (c=1)':>22} {'新 X0 (c=1)':>22} {'比值':>8}")
    ratio_min, ratio_max = None, None
    for m in [70, 80, 90, 91, 100, 120]:
        cm = c_m(m, d, X0_pub)
        Ku = K_up_cf(m, d, ps, qs, cm)
        xo = X0_old(m, Ku, d, ps, qs)
        xn = X0_new(m, Ku, d, ps, qs)
        r = xo / xn
        ratio_min = r if ratio_min is None else min(ratio_min, r)
        ratio_max = r if ratio_max is None else max(ratio_max, r)
        print(f"{m:>4} {mp.nstr(Ku, 8):>22} {mp.nstr(xo, 8):>22} {mp.nstr(xn, 8):>22} "
              f"{mp.nstr(r, 6):>8}")
    print(f"  比值区间：[{mp.nstr(ratio_min, 6)}, {mp.nstr(ratio_max, 6)}]")

    print()
    print("=" * 78)
    print("(4) 修正后的 M 表：新口径（最省）+ 各种文献常数")
    print("=" * 78)
    B = mp.mpf(2) ** 71
    hdr = ["连分数口径 (c=1)", "连分数口径 (97/162)", "连分数口径 (7/15)",
           "理想线性型 (c=1)", "理想线性型 (7/15)"]
    print(f"{'M':>5} " + " ".join(f"{h:>24}" for h in hdr))
    out = {}
    for M in [75, 82, 91, 100, 150, 200]:
        row = []
        for key, cval, kind in [("cf1", C_MFORM["SdW Cor 5 (c=1)"], "cf"),
                                ("cf97", C_MFORM["H23 Cor 17 (c=97/162)"], "cf"),
                                ("cf7", C_MFORM["H23 Cor 19 (c=7/15)"], "cf"),
                                ("id1", C_MFORM["SdW Cor 5 (c=1)"], "id"),
                                ("id7", C_MFORM["H23 Cor 19 (c=7/15)"], "id")]:
            vals = []
            for m in range(2, M + 1):
                cm = c_m(m, d, X0_pub)
                Ku = K_up_cf(m, d, ps, qs, cm) if kind == "cf" else K_up_ideal(m, d, cm)
                x = X0_new(m, Ku, d, ps, qs, c_mf=cval)
                vals.append(x)
            X = max(vals)
            out[(M, key)] = X
            row.append(f"{mp.nstr(X, 6)}/{mp.nstr(X / B, 4)}x")
        print(f"{M:>5} " + " ".join(f"{r:>24}" for r in row))

    print()
    print("  同样的表但用 K 形态常数（cK = 1/4，H23 Theorem 27）：")
    for M in [75, 91, 100]:
        for kind in ["cf", "id"]:
            vals = []
            for m in range(2, M + 1):
                cm = c_m(m, d, X0_pub)
                Ku = K_up_cf(m, d, ps, qs, cm) if kind == "cf" else K_up_ideal(m, d, cm)
                vals.append(X0_new(m, Ku, d, ps, qs, c_mf=mp.mpf(1) / 3, c_kf=mp.mpf(1) / 4))
            X = max(vals)
            print(f"    M = {M:>4}, K_up = {kind}: X0 = {mp.nstr(X, 6)} "
                  f"= {mp.nstr(X / B, 5)} x 2^71")

    print()
    print("=" * 78)
    print("(5) 两套 K_low 下的前沿对比（反驳者称前沿不变）")
    print("=" * 78)

    def K_low_crude(m, X0):
        best = mp.mpf(0)
        for n in range(len(qs) - 1):
            if qs[n] + qs[n + 1] <= mp.log(2) * X0 / m:
                best = max(best, qs[n])
        return best

    def K_low_fine(m, X0):
        best = mp.mpf(0)
        for n in range(len(qs) - 1):
            v = abs(qs[n] * d - ps[n])
            if X0 >= m / (mp.log(2) * v):
                best = max(best, qs[n])
        return best

    for X0 in [X0_pub, mp.mpf(2) ** 71]:
        line = []
        for klname, kl in [("粗", K_low_crude), ("精", K_low_fine)]:
            for kname, kf in [("Rhin", lambda m: K1_rhin(m, d, X0, c_m(m, d, X0))),
                              ("CF", lambda m: K_up_cf(m, d, ps, qs, c_m(m, d, X0)))]:
                f = None
                for m in range(2, 300):
                    if kf(m) <= kl(m, X0):
                        f = m
                line.append(f"{klname}/{kname}={f}")
        print(f"  X0 = {mp.nstr(X0, 8)}: " + ", ".join(line))

    return 0


if __name__ == "__main__":
    sys.exit(main())
