#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
# -*- coding: utf-8 -*-
"""丢番图路线 · 探针 8：修正后的「达到前沿 M 所需 X0」表。

只用有效的常数配对：
  上限（m 形态，随 1/X0 缩放）：Lambda < c * m / X0，
      c = 1     —— Simons 与 de Weger Corollary 5
      c = 97/162 —— Hercher Corollary 17（其有效常数）
  上限（K 形态，随 1/X0 缩放）：Lambda < cK * K / X0，
      cK = 1/3 —— Eliahou / Hercher Theorem 16 / 本项目判据（本项目写 3X0-1，更紧）
      cK = 1/4 —— Hercher Theorem 27
  下界：Lambda >= ln2 * psi(K_up)，psi(M) = |q_N delta - p_N|，q_N 为不超过 M 的最大收敛项分母
      （结论 A，已逐点核验：dt_fix.py 第 (1) 节）。
于是 X0min(m) = min( c*m, cK*K_up ) / (ln2 * psi(K_up))，K_up 取三种口径之最小者。

注意：Hercher Corollary 19 与 Corollary 29 的表述带硬写常数（695*2^60、1536*2^60），
是固定宽度窗口而非 1/X0 缩放形态；本脚本在第 (3) 节单独处理 Cor 19。

用法：.venv/bin/python dt_fix2.py
"""
import sys
import mpmath as mp

DPS = 170


def setup(nmax=150):
    mp.mp.dps = DPS
    d = mp.log(3) / mp.log(2)
    ps, qs = [], []
    x = d
    pm2, pm1, qm2, qm1 = mp.mpf(0), mp.mpf(1), mp.mpf(1), mp.mpf(0)
    for _ in range(nmax):
        a = int(mp.floor(x))
        pn, qn = a * pm1 + pm2, a * qm1 + qm2
        ps.append(pn); qs.append(qn)
        pm2, pm1 = pm1, pn
        qm2, qm1 = qm1, qn
        x = 1 / (x - mp.floor(x))
    return d, ps, qs


def psi(M, d, ps, qs):
    idx = max(i for i in range(len(qs)) if qs[i] <= M)
    return abs(qs[idx] * d - ps[idx]), idx


def c_m_fn(m, delta, X0):
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


def X0min(m, KU, d, ps, qs, c_mf, c_kf):
    """X0min(m) = min(c_mf*m, c_kf*K_up)/(ln2*psi(K_up))；返回 (值, 哪一项取到, K_up, psi)"""
    v, _ = psi(KU, d, ps, qs)
    cm_part, ck_part = c_mf * m, c_kf * KU
    if cm_part <= ck_part:
        return cm_part / (mp.log(2) * v), "m 形态", KU, v
    return ck_part / (mp.log(2) * v), "K 形态", KU, v


def main():
    d, ps, qs = setup()
    X0_pub = mp.mpf("3.7469e18")
    B = mp.mpf(2) ** 71

    KU = {"Rhin": lambda m: K1_rhin(m, d, X0_pub, c_m_fn(m, d, X0_pub)),
          "连分数": lambda m: K_up_cf(m, d, ps, qs, c_m_fn(m, d, X0_pub)),
          "理想": lambda m: K_up_ideal(m, d, c_m_fn(m, d, X0_pub))}

    print("=" * 78)
    print("(1) psi(K_up) 与最省形态（诊断用，m = 91 与 100）")
    print("=" * 78)
    for m in [91, 100]:
        for nm in ["Rhin", "连分数", "理想"]:
            KUv = KU[nm](m)
            v, idx = psi(KUv, d, ps, qs)
            print(f"  m = {m}, K_up({nm}) = {mp.nstr(KUv, 8):>16},"
                  f" 最大收敛项 q_{idx} = {mp.nstr(qs[idx], 8):>14}, psi = {mp.nstr(v, 10)}")

    print()
    print("=" * 78)
    print("(2) 修正后的「前沿 >= M 所需 X0」表（X0min = max_{m<=M}）")
    print("=" * 78)
    hdr = ["c=1, K_up=Rhin", "c=1, K_up=连分数", "c=97/162, K_up=连分数",
           "c=1, K_up=理想", "c=97/162, K_up=理想"]
    print(f"{'M':>5} " + " ".join(f"{h:>26}" for h in hdr))
    rows = {}
    for M in [75, 82, 91, 100, 150, 200]:
        row = []
        for c_mf, nm in [(mp.mpf(1), "Rhin"), (mp.mpf(1), "连分数"),
                         (mp.mpf(97) / 162, "连分数"), (mp.mpf(1), "理想"),
                         (mp.mpf(97) / 162, "理想")]:
            vals = [X0min(m, KU[nm](m), d, ps, qs, c_mf, mp.mpf(1) / 3)[0]
                    for m in range(2, M + 1)]
            X = max(vals)
            rows[(M, c_mf, nm)] = X
            row.append(f"{mp.nstr(X, 6)}/{mp.nstr(X / B, 4)}x")
        print(f"{M:>5} " + " ".join(f"{r:>26}" for r in row))
    print()
    print("  （分母 2^71 = " + mp.nstr(B, 8) + "；比值后缀 x 表示是 2^71 的倍数）")

    print()
    print("=" * 78)
    print("(3) Hercher Corollary 19 的忠实读法（固定宽度窗口，不随 1/X0 缩放）")
    print("=" * 78)
    w19 = mp.mpf(7) / 15 / (695 * mp.mpf(2) ** 60)
    print(f"  Cor 19: 若 X0 >= 695*2^60 则 Lambda < (7/15)*m/(695*2^60) = {mp.nstr(w19, 6)}*m")
    for m in [91, 100]:
        for nm in ["连分数", "理想"]:
            KUv = KU[nm](m)
            v, _ = psi(KUv, d, ps, qs)
            need = w19 * m
            got = mp.log(2) * v
            print(f"  m = {m}, K_up = {nm}: 需要 ln2*psi >= {mp.nstr(need, 6)},"
                  f" 实得 {mp.nstr(got, 6)}  →  {'够' if got >= need else '不够'}")

    print()
    print("=" * 78)
    print("(4) 主比较：连分数口径相对 Rhin 口径的余量（修正后）")
    print("=" * 78)
    for M in [75, 82, 91, 100]:
        a = rows[(M, mp.mpf(1), "Rhin")]
        b = rows[(M, mp.mpf(1), "连分数")]
        c = rows[(M, mp.mpf(97) / 162, "连分数")]
        e = rows[(M, mp.mpf(1), "理想")]
        print(f"  M = {M:>4}: Rhin(c=1) {mp.nstr(a / B, 5)}x | 连分数(c=1) {mp.nstr(b / B, 5)}x |"
              f" 连分数(c=97/162) {mp.nstr(c / B, 5)}x | 理想(c=1) {mp.nstr(e / B, 5)}x"
              f" || Rhin/连分数 = {mp.nstr(a / b, 4)}, 连分数/理想 = {mp.nstr(b / e, 4)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
