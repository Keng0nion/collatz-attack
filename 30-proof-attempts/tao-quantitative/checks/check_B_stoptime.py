#!/usr/bin/env python3
"""check_B_stoptime.py

独立验证「局部新结论 B」（Terras 停时密度的显式两侧界）及其精确值。

记号（与项目文献笔记 stopping-times.md 一致）：
  加速映射 T(n) = n/2（偶）、(3n+1)/2（奇）；
  S_k(n) = n, T(n), ..., T^{k-1}(n) 中奇数（奇步）的个数；
  lam_k(n) = 3^{S_k(n)} / 2^k；
  系数停时 tau(n) = min{ k >= 1 : lam_k(n) < 1 }；
  Terras 停时 chi(n) = min{ k >= 1 : T^k(n) < n }。
  密度 F(k) = 自然密度{ n : chi(n) >= k }（Terras 定理：= P[tau >= k]）。

本程序验证的三件事：
  (1) 字典恒等式：F(k) = A(k-1) / 2^{k-1}，其中 A(m) = #{长度 m 的 0/1 串：
      S_i >= t_i 对一切 i <= m}，t_i = min{ s : 3^s >= 2^i }。
      验证方式：在 n ∈ [1, 2^M] 上直接按 lam 判据算 tau(n)，数出 {tau >= k} 的
      计数，与 A(k-1) * 2^{M-k+1} 精确比对（对 k-1 <= M 应当逐个相等）。
  (2) 两侧显式界：2^{-(k-1)} <= F(k) <= exp(-(k-1) D)，
      D = ln 2 - H(log_3 2)（= 相对熵 D(log_3 2 || 1/2)，单位为 nat）。
  (3) 倾斜测度与边界因子：F(k) <= exp(-(k-1) D) * Q(E_{k-1})，
      Q(E_m) = sum_{good strings} p^{S}(1-p)^{m-S}（p = log_3 2），
      并数值观察 Q(E_m) 的幂律衰减阶（这是 Chernoff 之后唯一还缺的边界估计）。

用法：
  python3 check_B_stoptime.py [MMAX] [KMAX]
默认 MMAX = 20（枚举 n <= 2^20 做字典核对），KMAX = 1200（DP 到 k = 1200）。
"""

import sys
from math import log, log2, exp, ldexp

TWO = 2.0
LOG2 = log(2.0)


def thresholds(m: int):
    """t[i] = min{ s >= 0 : 3^s >= 2^i }，纯整数比较，i = 0..m。"""
    t = [0] * (m + 1)
    s = 0
    pw3 = 1
    for i in range(1, m + 1):
        pw2 = 1 << i
        while pw3 < pw2:
            s += 1
            pw3 *= 3
        t[i] = s
    return t


def A_exact(m: int):
    """A(i) 的精确值（大整数 DP），返回 list A[0..m]。"""
    t = thresholds(m)
    # f[s] = 满足约束且前缀和为 s 的前缀数
    f = [0] * (m + 2)
    f[0] = 1  # 空前缀，和 0
    A = [1]
    for i in range(1, m + 1):
        g = [0] * (m + 2)
        for s in range(0, i + 1):
            v = f[s]
            if v:
                g[s] += v        # 第 i 位取 0
                g[s + 1] += v    # 第 i 位取 1
        ti = t[i]
        for s in range(0, ti):   # 施加约束 S_i >= t_i
            g[s] = 0
        f = g
        A.append(sum(f))
    return A


def Q_tilted(m: int, p: float):
    """Q(E_i) 的浮点 DP，返回 list Q[0..m]（在倾斜测度下的生存概率）。"""
    t = thresholds(m)
    q = 1.0 - p
    f = [0.0] * (m + 2)
    f[0] = 1.0
    Q = [1.0]
    for i in range(1, m + 1):
        g = [0.0] * (m + 2)
        for s in range(0, i + 1):
            v = f[s]
            if v:
                g[s] += v * q
                g[s + 1] += v * p
        ti = t[i]
        for s in range(0, ti):
            g[s] = 0.0
        f = g
        Q.append(sum(f))
    return Q


def tau_of(n: int, cap: int, t=None):
    """按 lam 判据直接算 tau(n)：最小 k >= 1 使 3^{S_k} < 2^k，即 S_k < t_k。

    t[k] = min{ s : 3^s >= 2^k }，用精确整数比较，不依赖浮点。
    """
    if t is None:
        t = thresholds(cap)
    x = n
    s = 0
    for k in range(1, cap + 1):
        if x % 2 == 1:
            s += 1
        if s < t[k]:
            return k
        x = x // 2 if x % 2 == 0 else (3 * x + 1) // 2
    return None


def chi_of(n: int, cap: int):
    """直接模拟算 chi(n)（首次 T^k(n) < n）。"""
    x = n
    for k in range(1, cap + 1):
        x = x // 2 if x % 2 == 0 else (3 * x + 1) // 2
        if x < n:
            return k
    return None


def main():
    MMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    KMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 1200

    p = 1.0 / log2(3.0)           # log_3 2
    H = -(p * log(p) + (1 - p) * log(1 - p))
    D = LOG2 - H                  # 相对熵 D(p || 1/2)，单位 nat
    print(f"p = log_3 2 = {p:.12f}")
    print(f"H(p) = {H:.12f}  nat;  D = ln2 - H(p) = {D:.12f} nat ="
          f" {D / LOG2:.12f} bit")
    print(f"exp(-D) = {exp(-D):.12f}   （每步衰减因子）")
    print()

    # ---------- (1) 字典恒等式：枚举 n <= 2^MMAX ----------
    print(f"--- (1) 字典恒等式核对：枚举 n ∈ [1, 2^{MMAX}] ---")
    cap = max(MMAX + 400, 600)
    tt = thresholds(cap)
    cnt_tau_ge = [0] * (MMAX + 3)
    cnt_chi_ge = [0] * (MMAX + 3)
    diff_chi_tau = 0
    first_diff = []
    N = 1 << MMAX
    max_tau = 0
    max_chi = 0
    for n in range(2, N + 1):
        a = tau_of(n, cap, tt)
        b = chi_of(n, cap)
        if a is None or b is None:
            raise RuntimeError(f"cap 太小: n={n}")
        max_tau = max(max_tau, a)
        max_chi = max(max_chi, b)
        if a != b:
            diff_chi_tau += 1
            if len(first_diff) < 5:
                first_diff.append((n, a, b))
        for k in range(1, min(a, MMAX + 2) + 1):
            cnt_tau_ge[k] += 1
        for k in range(1, min(b, MMAX + 2) + 1):
            cnt_chi_ge[k] += 1
    A = A_exact(MMAX + 2)
    print(f"  范围 n ∈ [2, {N}]；tau 最大 {max_tau}，chi 最大 {max_chi}")
    print(f"  tau 与 chi 不一致个数（n>=2）= {diff_chi_tau}  最小几例：{first_diff}")
    bad = 0
    print("   k   实测#{tau>=k}  精确 A(k-1)*2^(M-k+1)-1   实测#{chi>=k}   F(k)=A/2^(k-1)")
    for k in range(1, MMAX + 2):
        # 枚举起点为 n ∈ [2, 2^M]，故预测值 = 全量 [1,2^M] 的预测减 1（n=1 计入全部 k）
        # 枚举区间是 [2, 2^M]；与 [1, 2^M] 的差别只在 n = 1，而 tau(1) = 2、chi(1) = 无穷。
        # 因 tau(1) = 2，n = 1 只计入 k <= 2，故预测值减去 1 当且仅当 k <= 2。
        pred = A[k - 1] * (1 << (MMAX - (k - 1))) - (1 if k <= 2 else 0) if k - 1 <= MMAX else None
        ok = (pred == cnt_tau_ge[k])
        if not ok:
            bad += 1
        if k <= 12 or k in (16, 20, 21, MMAX + 1):
            F = exp(log(A[k - 1]) - (k - 1) * LOG2)
            print(f"  {k:3d}   {cnt_tau_ge[k]:10d}      {pred}        "
                  f"{cnt_chi_ge[k]:10d}      {F:.12e}  {'OK' if ok else 'MISMATCH'}")
    print(f"  字典恒等式不一致个数 = {bad}")

    # ---------- (2)(3) 大范围 DP ----------
    print()
    print(f"--- (2)(3) DP 到 k = {KMAX} ---")
    m = KMAX
    A = A_exact(m)
    Q = Q_tilted(m, p)
    print("   k        F(k)              Chernoff上界 exp(-(k-1)D)"
          "        下界 2^-(k-1)      Q(E_{k-1})    Q*sqrt(k)")
    rows = []
    for k in range(2, m + 1):
        mm = k - 1
        F = exp(log(A[mm]) - mm * LOG2)
        ub = exp(-mm * D)
        lb = ldexp(1.0, -mm)
        q = Q[mm]
        rows.append((k, F, ub, q))
        if k in (2, 5, 10, 20, 50, 100, 135, 200, 400, 800, 1200) or (k <= 6):
            print(f"  {k:4d}  {F:.6e}     {ub:.6e}          {lb:.6e}    "
                  f"{q:.6e}   {q * (k - 1) ** 0.5:.6f}")
    # 界检查
    viol_ub = [r for r in rows if r[1] > r[2] * (1 + 1e-12)]
    viol_lb = [r for r in rows if r[1] < 2.0 ** (-(r[0] - 1)) * (1 - 1e-12)]
    viol_tilt = [r for r in rows if r[1] > exp(-(r[0] - 1) * D) * r[3] * (1 + 1e-12)]
    print(f"  违反上界 F<=exp(-(k-1)D) 的 k 个数 = {len(viol_ub)}")
    print(f"  违反下界 F>=2^-(k-1) 的 k 个数 = {len(viol_lb)}")
    print(f"  违反 F<=exp(-(k-1)D)*Q 的 k 个数 = {len(viol_tilt)}")

    # 与文献记录值对比
    print()
    print("--- 与项目文献笔记记录的数值对比（stopping-times.md 第 82 行 /"
          " parity-vectors.md）---")
    lit = {50: 3.54e-3, 100: 2.64e-4, 135: 5.3312e-5, 200: 3.32e-6}
    for k, v in sorted(lit.items()):
        if k <= m:
            F = exp(log(A[k - 1]) - (k - 1) * LOG2)
            print(f"  k={k:4d}: 本程序 {F:.6e}   文献 {v:.6e}   "
                  f"相对差 {abs(F - v) / v:.4%}")

    # 幂律拟合：Q(E_m) ~ c m^{-gamma}
    print()
    print("--- 边界因子 Q(E_m) 的幂律拟合（Chernoff 之后唯一缺的一步）---")
    pts = [(k - 1, q) for (k, F, ub, q) in rows if 200 <= k - 1 <= m]
    if len(pts) > 10:
        x1, y1 = log(pts[0][0]), log(pts[0][1])
        x2, y2 = log(pts[-1][0]), log(pts[-1][1])
        gamma = -(y2 - y1) / (x2 - x1)
        c = exp(y1 + gamma * x1)
        print(f"  在 m ∈ [{pts[0][0]}, {pts[-1][0]}] 上拟合 Q(E_m) ≈ c m^(-gamma):")
        print(f"    gamma = {gamma:.6f}   c = {c:.6f}")
        for mm in (200, 400, 800, 1200):
            qt = [q for (kk, F, ub, q) in rows if kk - 1 == mm]
            if qt:
                print(f"    m={mm:5d}: Q={qt[0]:.6e}  Q*m^0.5={qt[0] * mm ** 0.5:.6f}"
                      f"  Q*m^1.5={qt[0] * mm ** 1.5:.4f}")
    # 有效衰减率
    print()
    print("--- 有效指数衰减率 -d ln F / dk（窗口）---")
    for lo, hi in ((50, 100), (100, 200), (200, 400), (400, 800), (800, 1200)):
        if hi > m:
            continue
        Fa = exp(log(A[lo - 1]) - (lo - 1) * LOG2)
        Fb = exp(log(A[hi - 1]) - (hi - 1) * LOG2)
        print(f"  k ∈ [{lo},{hi}]: rate = {(log(Fa) - log(Fb)) / (hi - lo):.6f}"
              f"   （相对熵 D = {D:.6f}）")

    # 亏损因子：F 相对 e^{-Dm} 与 Q(E_m) 的关系
    print()
    print("--- 亏损因子 loss(m) = F(m+1) / (e^{-D m} Q(E_m)) 与 F 自身的幂律 ---")
    print("     m      F(m+1)        e^{-Dm}Q(E_m)     loss(m)    loss*m^-0.5"
          "   F*e^{Dm}*m")
    for mm in (50, 100, 200, 400, 800, 1200, 1600, 2000):
        if mm > m:
            continue
        F = exp(log(A[mm]) - mm * LOG2)
        base = exp(-mm * D) * Q[mm]
        loss = F / base
        print(f"  {mm:5d}  {F:.6e}    {base:.6e}    {loss:.6f}     "
              f"{loss * mm ** -0.5:.6f}    {F * exp(mm * D) * mm:.6f}")

    # F 自身的幂律：F(m+1) ≈ c e^{-Dm} m^{-gamma}，用相邻两点估计 gamma
    print()
    print("--- F 自身幂指数的相邻估计 gamma(m) = ln[F(m)/F(2m)]/ln2 - D*m/ln2"
          " (以 e^{-Dm}m^{-gamma} 为模型) ---")
    for mm in (50, 100, 200, 400, 800, 1600):
        if 2 * mm > m:
            continue
        F1 = exp(log(A[mm]) - mm * LOG2)
        F2 = exp(log(A[2 * mm]) - 2 * mm * LOG2)
        g = (log(F1) - log(F2) - mm * D) / LOG2
        print(f"  m ∈ [{mm},{2 * mm}]: gamma ≈ {g:.4f}")


if __name__ == "__main__":
    main()
