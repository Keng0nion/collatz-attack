#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
# -*- coding: utf-8 -*-
"""丢番图路线 · 探针 3：K 的上界与下界、以及「排除 m 圈」的前沿 m*(X0)。

记号（与 Simons 与 de Weger v1.43 一致）：
  m   = 局部极小值个数（m 圈参数）
  K   = 环上奇数个数；L = 偶数个数；周期 = K + L
  delta = log2 3，Lambda = (K+L)ln2 - K ln3 = sum_{奇数 n 在环上} ln(1 + 1/(3n))

三条不等式：
  (S1) Corollary 5（SdW）：  0 < Lambda < m/x_min <= m/X0
  (S2) Lemma 7（SdW）：      Lambda < m*c_m*2^{-(delta-1)K/(delta^m-1)}
  (S3) Lemma 12（SdW，Rhin）：Lambda > e^{-13.3(0.46057+ln K)}
  (S3') 本工作（初等，连分数）：Lambda >= ln2 * ||K delta|| >= ln2 * |q_N delta - p_N|
        其中 q_N 是不超过 K 的最大收敛项分母。

K 的上界：由 (S2) 与 (S3) 或 (S3') 联立。
K 的下界：由 (S1) 与「K <= q_n 时 Lambda > ln2/(q_n+q_n+1)」联立，得 Lemma 10 形态：
        q_n + q_n+1 <= ln2 * X0 / m   ==>   K > q_n。

用法：.venv/bin/python dt_cycle.py
"""
import sys
import mpmath as mp

DPS = 150


def delta_and_convergents(nmax):
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
    return d, a, ps, qs


def c_m(m, delta, X0):
    """Lemma 7 证明中给出的 c_m（由 (1+X0^-1)^m 与 b^{E_m} 的几何级数算出）。
    b = (1+1/X0)^{1/delta} / 2^{1/delta}
    E_m = sum_{i=1}^{m-1} (m-i) delta^i
    c_m = (1+1/X0)^{m(delta-1)/(delta^m-1)} * b^{E_m (delta-1)/(delta^m-1)}
    """
    b = (1 + 1 / X0) ** (1 / delta) / mp.mpf(2) ** (1 / delta)
    E = sum((m - i) * delta ** i for i in range(1, m))
    ex = (delta - 1) / (delta ** m - 1)
    return (1 + 1 / X0) ** (m * ex) * b ** (E * ex)


def K1_rhin(m, delta, X0, lo=1, hi=None):
    """Lemma 14：K < K1(m)，K1(m) 是 e^{-13.3(0.46057+ln x)} = m c_m 2^{-(delta-1)x/(delta^m-1)} 的最大解。"""
    cm = c_m(m, delta, X0)
    A = m * cm

    def f(x):
        lhs = -mp.mpf("13.3") * (mp.mpf("0.46057") + mp.log(x))
        rhs = mp.log(A) - (delta - 1) * x * mp.log(2) / (delta ** m - 1)
        return lhs - rhs
    if hi is None:
        hi = mp.mpf(10) ** (3 * m + 10)
    # f 在 x 小时为负、大时为正？先扫出变号区间
    x = lo
    while f(x) <= 0 and x < hi:
        x *= 2
    hi = x
    for _ in range(400):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return hi, cm


def R_cf(m, delta, X0, qN, pN, cm):
    """由 Lemma 7 与连分数下界 Lambda > ln2*|q_N delta - p_N| 得到的 K 上界（该 N 段内常数）。"""
    L = mp.log(2) * abs(qN * delta - pN)
    return (delta ** m - 1) * (mp.log(1 / L) + mp.log(m * cm)) / ((delta - 1) * mp.log(2))


def K_up_cf(m, delta, X0, ps, qs, cm):
    """在所有「K 落在 [q_N, q_N+1)」的分段上取满足 K < R_N 的最大 K。
    注意 R_N 随 N 递减，故只需检查前若干段。"""
    best = mp.mpf(0)
    for N in range(0, len(qs) - 1):
        R = R_cf(m, delta, X0, qs[N], ps[N], cm)
        if qs[N] >= R:
            # 该段里没有可行 K；R 随 N 增大而减小，后面的段也不会有
            break
        cand = min(qs[N + 1] - 1, mp.floor(R))
        if cand > best:
            best = cand
    return best


def K_low_lemm10(m, delta, X0, qs):
    """Lemma 10：若 q_n + q_n+1 <= ln2*X0/m 则 K > q_n。返回可保证的最大 q_n。"""
    best = mp.mpf(0)
    for n in range(0, len(qs) - 1):
        if qs[n] + qs[n + 1] <= mp.log(2) * X0 / m:
            best = max(best, qs[n])
        else:
            break
    return best


def main():
    mp.mp.dps = DPS
    d, a, ps, qs = delta_and_convergents(60)
    X0_pub = mp.mpf("3.7469e18")   # v1.43 用的验证界

    print("=" * 78)
    print("一、复算 Simons 与 de Weger v1.43 Lemma 14 的 K1(m) 表")
    print("=" * 78)
    print("（文献值逐字取自本机下载的 v1.43 PDF；k1(m) = K1(m)/(m delta^m)）")
    lit = {2: "3.0877e2", 10: "3.5858e4", 63: "4.8181e15", 64: "7.7350e15",
           100: "1.7876e23", 511: "1.3035e106", 512: "2.0698e106", 1000: "1.6144e204"}
    print(f"{'m':>5} {'我算 K1(m)':>22} {'文献 K1(m)':>16} {'我算 k1(m)':>12} "
          f"{'文献 k1(m)':>12} {'c_m':>12}")
    for m in sorted(lit):
        K1, cm = K1_rhin(m, d, X0_pub)
        k1 = K1 / (m * d ** m)
        print(f"{m:>5} {mp.nstr(K1, 6):>22} {lit[m]:>16} {mp.nstr(k1, 6):>12} "
              f"{'-':>12} {mp.nstr(cm, 6):>12}")
    print()
    print("c_m 的极限核对：m=30 时 c_m =", mp.nstr(c_m(30, d, X0_pub), 7),
          "（文献：m >= 30 时 c_m < 0.30577）")
    print("m -> 大 时 b^{delta/(delta-1)} =",
          mp.nstr(mp.mpf(2) ** (-1 / (d - 1)), 7), "（文献：0.30576）")
    print("极限比值 13.3*ln(delta)/(ln2*(delta-1)) =",
          mp.nstr(mp.mpf("13.3") * mp.log(d) / (mp.log(2) * (d - 1)), 7),
          "（文献：15.107）")

    print()
    print("=" * 78)
    print("二、K 的上界：Rhin（Lemma 12）与连分数（本工作）的对比")
    print("=" * 78)
    print(f"{'m':>5} {'K1 Rhin':>24} {'K_up CF':>24} {'比值 Rhin/CF':>14}")
    rows = {}
    for m in [20, 40, 60, 63, 70, 71, 72, 75, 80, 90, 91, 100]:
        K1, cm = K1_rhin(m, d, X0_pub)
        Kc = K_up_cf(m, d, X0_pub, ps, qs, cm)
        rows[m] = (K1, Kc)
        print(f"{m:>5} {mp.nstr(K1, 8):>24} {mp.nstr(Kc, 8):>24} "
              f"{mp.nstr(K1 / Kc, 6) if Kc > 0 else 'n/a':>14}")

    print()
    print("=" * 78)
    print("三、排除前沿 m*(X0)：K_low(m) 与 K_up(m) 的交叉")
    print("=" * 78)
    print("判据：对参数 m，若 K_low(m) >= K_up(m) 则不存在该 m 的环。")
    print("K_low(m) 用 Lemma 10（下界侧，SdW Corollary 5 + 连分数）；")
    print("K_up(m) 分别用 Rhin 与连分数。")
    print()
    for X0 in [X0_pub, mp.mpf("1e19"), mp.mpf("1e20"), 1536 * mp.mpf(2) ** 60,
               mp.mpf(2) ** 71, mp.mpf("1e22"), mp.mpf("1e23")]:
        fR = None
        fC = None
        Klow_used = {}
        for m in range(2, 400):
            K1, cm = K1_rhin(m, d, X0)
            Klow = K_low_lemm10(m, d, X0, qs)
            Klow_used[m] = Klow
            if K1 <= Klow:
                fR = m
            Kc = K_up_cf(m, d, X0, ps, qs, cm)
            if Kc <= Klow:
                fC = m
        print(f"  X0 = {mp.nstr(X0, 8):>14}  （= 2^{mp.nstr(mp.log(X0, 2), 5)}）"
              f"  前沿：Rhin 口径 m* = {fR}，连分数口径 m* = {fC}")

    print()
    print("=" * 78)
    print("四、灵敏度：线性型下界的「完美化」（L -> 1，即 ln(1/L) = 0）能买到多少 m")
    print("=" * 78)
    print("K_up ~ (delta^m-1)(ln(1/L) + ln(m c_m))/((delta-1)ln2)，故 K_up 大致正比于 ln(1/L)。")
    print("线性型越强 => ln(1/L) 越小 => K_up 越小 => 前沿越大。极限 L -> 1：")
    for X0 in [X0_pub, mp.mpf("1e20"), mp.mpf("1e21"), mp.mpf("1e22"), mp.mpf("1e23")]:
        fC_perfect = None
        fC = None
        for m in range(2, 400):
            Klow = K_low_lemm10(m, d, X0, qs)
            cm = c_m(m, d, X0)
            Kc = K_up_cf(m, d, X0, ps, qs, cm)
            if Kc <= Klow:
                fC = m
            Kperf = (d ** m - 1) * (mp.log(m * cm)) / ((d - 1) * mp.log(2))
            if Kperf <= Klow:
                fC_perfect = m
        print(f"  X0 = {mp.nstr(X0, 6):>10}（2^{mp.nstr(mp.log(X0, 2), 4)}）: "
              f"连分数口径前沿 {fC}，理想线性型（L=1）前沿 {fC_perfect}")

    print()
    print("五、把 K_up 压低一个因子 r 对应前沿前进多少（数值，X0 = 3.7469e18）")
    print("=" * 78)
    for r in [1.0, 1.67, 13.0, 100.0, 1000.0, 10 ** 6, 10 ** 12, 10 ** 100]:
        f = None
        for m in range(2, 400):
            cm = c_m(m, d, X0_pub)
            Kc = K_up_cf(m, d, X0_pub, ps, qs, cm) / r
            if Kc <= K_low_lemm10(m, d, X0_pub, qs):
                f = m
        print(f"  K_up 缩小 {r:>10.3g} 倍 -> 前沿 m* = {f}"
              f"   （log_delta(r) = {mp.nstr(mp.log(r, d), 4) if r > 1 else '0'}）")

    return 0


if __name__ == "__main__":
    sys.exit(main())
