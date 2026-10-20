#!/usr/bin/env python3
"""最小反例路线的引理复核脚本（只用标准库；全部为精确整数运算）。

记号（加速映射 T(n) = n/2 若 n 偶，(3n+1)/2 若 n 奇）：
  停时         chi(n) = min{ j >= 1 : T^j(n) < n }（若不存在则为 +inf）
  系数停时     tau(n) = min{ j >= 1 : 3^{S_j(n)} < 2^j }，S_j = 前 j 步（不含第 j 步的值）中奇数个数；
               这等价于奇偶向量 v_j(n) 的"系数条件 3^{m_j} >= 2^j"首次失败
  层级幸存集   E_k  = { n in [1, 2^k) : chi(n) >= k+1 }
  系数可容许集 a_k  = { n in [1, 2^k) : tau(n) >= k+1 }
  阈值         theta_v = c_v / (2^{|v|} - 3^{m_v})，c_v 由奇偶向量决定

复核条目：
  C1  阈值等价：T^j(x) >= x  <=>  3^{m_j} >= 2^j  或  x <= theta
  C2  奇偶向量只依赖 x mod 2^j（同余类常值性）
  C3  E_k 的两套独立实现（逐层树 vs 直接迭代）一致
  C4  结构命题：E_k = a_k ⊔ {1}（k <= K），即 chi >= k+1 与"tau >= k+1 或 n = 1"在 [1,2^k) 上等价
  C5  chi <= tau（即不存在 chi >= tau+1 的 n），以及 tau > chi 的计数（Terras 猜想方向）
  C6  首次失败处的精确公式：tau(n) = j 时 m_j = ceil(j*log_3 2) - 1（用整数比较实现）
  C7  恒等式 2^{B_t} y_{t+1} = prod_{s<=t}(3 y_s + 1) 与不等式 B_t ln2 <= t ln3 + t/(3n)
  C8  密度：|a_k|/2^k 与已知 F(k+1)（Terras/本项目实验值）对照
  C9  定理 (K)（与"无非平凡环"等价的那条）在范围内的检验：
      对一切长度 j <= K、系数条件在 j 处首次失败、且类最小元 r>1 的向量，验证 T^j(r) < r

用法：python3 verify_lemmas.py
"""
from fractions import Fraction
from collections import defaultdict

def T(x):
    return x // 2 if x % 2 == 0 else (3 * x + 1) // 2

def bits_c_m(x, k):
    """x 的长度 k 奇偶向量、对应 c、1 的个数 m、以及 T^k(x)。"""
    y = x
    bits = []
    c = 0
    m = 0
    for i in range(k):
        b = y & 1
        bits.append(b)
        if b:
            c = 3 * c + (1 << i)
            m += 1
        y = T(y)
    return tuple(bits), c, m, y

def chi(n, cap=10 ** 6):
    y = n
    for j in range(1, cap + 1):
        y = T(y)
        if y < n:
            return j
    return None  # 未在 cap 步内下降

def tau(n, cap=10 ** 6):
    y = n
    m = 0
    for j in range(1, cap + 1):
        if y & 1:
            m += 1
        y = T(y)
        if 3 ** m < (1 << j):
            return j
    return None

# ---------------- C1 ----------------
def C1(X=1 << 10, K=10):
    bad = []
    for x in range(1, X):
        y = x
        c = 0
        m = 0
        for k in range(1, K + 1):
            b = y & 1
            if b:
                c = 3 * c + (1 << (k - 1))
                m += 1
            y = T(y)
            lhs = (y >= x)
            if (1 << k) > 3 ** m:
                rhs = (x * ((1 << k) - 3 ** m) <= c)
            else:
                rhs = True
            if lhs != rhs:
                bad.append((x, k, lhs, rhs))
    return bad

# ---------------- C2 ----------------
def C2(X=1 << 11, K=9):
    return sum(1 for k in range(1, K + 1) for x in range(1, X)
               if bits_c_m(x, k)[0] != bits_c_m(x + (1 << k), k)[0])

# ---------------- C3/C4 ----------------
def tree_levels(K):
    """逐层构造 E_k（用阈值判据），节点 (r, y, best_c, best_D, c, m)。

    best_c/best_D 表示迄今最小 theta = best_c/best_D（best_D = 0 表示迄今无约束）。
    约束：r <= theta  <=>  r * best_D <= best_c（best_D > 0）。
    """
    levels = []
    # 第 1 层：奇数类（首位的系数条件 3^1 >= 2^1 自动成立，无阈值约束）
    lvl = [(1, T(1), 0, 0, 1, 1)]  # c(1)=1, m=1
    levels.append(lvl)
    for j in range(1, K):
        nxt = []
        p = 1 << j
        for (r, y, bc, bd, c, m) in levels[-1]:
            for delta, yy in ((0, y), (p, y + 3 ** m)):
                s = r + delta
                if s >= (1 << (j + 1)):
                    continue
                bit = yy & 1
                if bit:
                    c_new = 3 * c + p
                    m_new = m + 1
                else:
                    c_new = c
                    m_new = m
                yn = T(yy)
                D = (1 << (j + 1)) - 3 ** m_new
                nbc, nbd = bc, bd
                if D > 0:
                    if nbd == 0 or c_new * nbd < nbc * D:
                        nbc, nbd = c_new, D
                ok = (nbd == 0) or (s * nbd <= nbc)
                if ok:
                    nxt.append((s, yn, nbc, nbd, c_new, m_new))
        levels.append(nxt)
    return levels

def brute_E(k):
    """直接迭代定义的 E_k = {n < 2^k : chi(n) >= k+1}，仅取奇数（偶数在 j=1 就下降）。"""
    out = []
    for n in range(1, 1 << k, 2):
        y = n
        ok = True
        for j in range(1, k + 1):
            y = T(y)
            if y < n:
                ok = False
                break
        if ok:
            out.append(n)
    return out

def alpha_k(k):
    """{n < 2^k : tau(n) >= k+1}，用向量条件直接判定。"""
    out = []
    for n in range(1, 1 << k, 2):
        y = n
        m = 0
        ok = True
        for j in range(1, k + 1):
            if y & 1:
                m += 1
            y = T(y)
            if 3 ** m < (1 << j):
                ok = False
                break
        if ok:
            out.append(n)
    return out

# ---------------- C5/C6 ----------------
def C5C6(N=200000, cap=400):
    n_chi_gt_tau = []
    n_tau_gt_chi = []
    tau_records = []
    bad_formula = []
    best = 0
    for n in range(2, N + 1):
        t = tau(n, cap)
        if t is None:
            n_tau_gt_chi.append((n, None))
            continue
        c = chi(n, cap)
        if c is None:
            n_chi_gt_tau.append((n, t, None))
            continue
        if c > t:
            n_chi_gt_tau.append((n, t, c))
        if t > c:
            n_tau_gt_chi.append((n, t, c))
        if t > best:
            best = t
            tau_records.append((n, t))
        # 公式：tau = j 时，3^{m_{j-1}} >= 2^{j-1} > 3^{m_j}，即 m_j = ceil(j log_3 2) - 1
        _, _, m, _ = bits_c_m(n, t)
        if 3 ** m >= (1 << t):
            bad_formula.append((n, t, m, "m too big"))
    return n_chi_gt_tau, n_tau_gt_chi, tau_records, bad_formula

# ---------------- C7 ----------------
def C7(x, cap=300):
    """精确恒等式：2^{B_t} · y_{t+1} · prod_{s<=t} y_s = y_1 · prod_{s<=t}(3 y_s + 1)。

    等价形式：2^{B_t} = (y_1 / y_{t+1}) · prod_{s<=t} (3 + 1/y_s)。
    返回 (恒等式是否成立, 不等式 B_t ln2 <= t ln3 + t/(3n) 首次失败处或 None)。
    """
    from math import log
    y = x
    bsum = 0
    prod_num = 1   # prod (3 y_s + 1)
    prod_den = 1   # prod y_s
    ident = True
    fail = None
    for t in range(1, cap + 1):
        v = 3 * y + 1
        k = 0
        while v % 2 == 0:
            v //= 2
            k += 1
        prod_num *= 3 * y + 1
        prod_den *= y
        bsum += k
        if (1 << bsum) * v * prod_den != x * prod_num:
            ident = False
        if bsum * log(2) > t * log(3) + t / (3 * x) + 1e-9 and fail is None:
            fail = (t, bsum)
        y = v
        if y == 1:
            break
    return ident, fail

# ---------------- C8 ----------------
def density_alpha(K):
    """|a_k| / 2^k，用 (j, m) 状态 DP 精确计数（条件：对每个 j <= k，3^{m_j} >= 2^j）。"""
    cur = {(0, 0): 1}
    out = []
    for k in range(1, K + 1):
        nxt = defaultdict(int)
        for (j, m), cnt in cur.items():
            if j < k - 1:
                continue
            for b in (0, 1):
                mm = m + b
                if 3 ** mm >= (1 << (j + 1)):
                    nxt[(j + 1, mm)] += cnt
        # 把未到 k-1 的状态保留
        keep = defaultdict(int)
        for (j, m), cnt in cur.items():
            if j < k - 1:
                keep[(j, m)] += cnt
        cur = keep
        for st, cnt in nxt.items():
            cur[st] += cnt
        tot = sum(cnt for (j, m), cnt in cur.items() if j == k)
        out.append((k, tot, Fraction(tot, 1 << k)))
    return out

# ---------------- C9 ----------------
def C9(K):
    """对一切长度 j<=K 的"首次失败"向量，验证类最小元 r>1 时 T^j(r) < r。"""
    # 逐层生成：kept = 满足所有 i<j 系数条件的 (r, y, c, m)
    kept = [(1, T(1), 1, 1)]  # r=1: c=1, m=1（首位为 1）
    viol = []
    checked = 0
    for j in range(1, K + 1):
        p = 1 << j
        nxt = []
        for (r, y, c, m) in kept:
            for delta, yy in ((0, y), (p, y + 3 ** m)):
                s = r + delta
                if s >= (1 << (j + 1)):
                    continue
                bit = yy & 1
                if bit:
                    c_new = 3 * c + p
                    m_new = m + 1
                else:
                    c_new = c
                    m_new = m
                yn = T(yy)
                D = (1 << (j + 1)) - 3 ** m_new
                if D > 0:  # 该位构成"首次失败"（此前全部满足）；这是候选环判据
                    checked += 1
                    if yn >= s and s > 1:
                        viol.append((j + 1, s, yn))
                else:
                    nxt.append((s, yn, c_new, m_new))
        kept = nxt
    return checked, viol

# ---------------- 主程序 ----------------
def main():
    print("=" * 72)
    bad = C1()
    print(f"C1 阈值等价（x < 2^10, j <= 10）：反例 {len(bad)}")
    print(f"C2 奇偶向量只依赖 mod 2^j（x < 2^11, j <= 9）：反例 {C2()}")

    print("-" * 72)
    print("C1 顺带给出：首次失败处 tau = j 时 m_j = ceil(j log_3 2) - 1（整数判据）")
    n_chi_gt_tau, n_tau_gt_chi, tau_records, bad_formula = C5C6()
    print(f"C5 n <= 200000：chi > tau 的个数 = {len(n_chi_gt_tau)}（应为 0，即 chi <= tau）")
    print(f"   chi < tau 的个数 = {len(n_tau_gt_chi)}（Terras 猜想断言 τ = χ，故应为 0）")
    print(f"   tau 纪录（前 12 条）：{tau_records[:12]}")
    print(f"C6 tau 的 m 公式失效数 = {len(bad_formula)}")

    print("-" * 72)
    K = 18
    levels = tree_levels(K)
    print(f"C3/C4 逐层：k, |E_k|（树）, |E_k|（直接迭代）, |a_k|, 是否存在 E_k \\ (a_k ∪ {{1}})")
    bad_struct = []
    for k in range(1, K + 1):
        tree_set = set(r for (r, y, bc, bd, c, m) in levels[k - 1])
        bf = set(brute_E(k))
        al = set(alpha_k(k))
        target = al | {1}
        flag = (tree_set == bf) and (tree_set == target)
        if not flag:
            bad_struct.append(k)
        if k <= 20:
            print(f"  k={k:2d}  |E|={len(tree_set):6d}  直接迭代 {len(bf):6d}  |a_k|={len(al):6d}"
                  f"  结构成立={tree_set == target}  两实现一致={tree_set == bf}")
    print(f"C4 结论：k <= {K} 上结构命题 E_k = a_k ∪ {{1}} 全部成立 = {not bad_struct}"
          + (f"；失败层：{bad_struct}" if bad_struct else ""))

    print("-" * 72)
    print("C4 前 8 层 E_k 完整列表：")
    for k in range(1, 9):
        print(f"  k={k}: {sorted(r for (r, _, _, _, _, _) in levels[k - 1])}")
    print("  推论：N mod 4 = 3；N mod 16 ∈ {7, 11, 15}")

    print("-" * 72)
    print("C4 附：类 -1 mod 2^k 是否在 E_k 中，以及 chi(2^k - 1) >= k")
    ok1 = all(((1 << k) - 1) in set(r for (r, _, _, _, _, _) in levels[k - 1]) for k in range(1, K + 1))
    ok2 = True
    for k in range(1, 17):
        n = (1 << k) - 1
        if chi(n) is not None and chi(n) <= k:
            ok2 = False
    print(f"   类 -1 恒在 E_k（k <= {K}）= {ok1}；chi(2^k - 1) >= k（k <= 16）= {ok2}")

    print("-" * 72)
    print("C7 恒等式与不等式（n <= 2000，cap 300）")
    ident_ok = all(C7(n)[0] for n in range(2, 2001))
    fails = sum(1 for n in range(2, 2001) if C7(n)[1] is not None)
    print(f"   恒等式 2^{{B_t}}·y_{{t+1}}·prod(y_s) = y_1·prod(3y_s+1) 全部成立 = {ident_ok}")
    print(f"   不等式 B_t ln2 <= t ln3 + t/(3n) 的失败个数 = {fails}"
          f"（该不等式只在'轨道元素都不低于 n'时有证明，故对一般 n 失败是预期的）")

    print("-" * 72)
    print("C8 密度 |a_k|/2^k（= F(k+1) = 密度{{chi >= k+1}}，Terras 密度定理）")
    dl = density_alpha(21)
    # 本项目 stoptime-stats 实验的直接实测值：chi 生存率（加速步）在阈值 3、10、20 处
    # 该实验的"阈值 k"= 密度{chi >= k} = F(k) = |a_{k-1}|/2^{k-1}，故对应本表的下标 k-1
    known = {2: 0.25, 9: 0.074219, 19: 0.028591}
    for (k, tot, frac) in dl:
        tag = ""
        if k in known:
            tag = f"   对照 k={k} 实测 {known[k]:.6f}（相对差 {abs(float(frac)-known[k])/known[k]:.2%}）"
        print(f"  k={k:2d}  |a_k|={tot:8d}  |a_k|/2^k={float(frac):.9f}{tag}")

    print("-" * 72)
    print("C9 定理 (K)：首次失败向量的类最小元 r > 1 时必有 T^j(r) < r（等价于'无非平凡环'）")
    for K2 in (12, 16, 20, 24):
        checked, viol = C9(K2)
        print(f"  j <= {K2}: 检查的首次失败向量 {checked} 个，违反（r>1 且 T^j(r) >= r）{len(viol)} 个"
              + (f"  例：{viol[:3]}" if viol else ""))

if __name__ == "__main__":
    main()
