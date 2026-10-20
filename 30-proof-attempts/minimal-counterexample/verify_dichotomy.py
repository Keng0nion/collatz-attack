#!/usr/bin/env python3
"""最小反例路线第三轮新增内容的复核脚本。只用标准库，全部精确整数运算（对数只用于对称差检验）。

记号（加速映射 T(n) = n/2 若 n 偶，(3n+1)/2 若 n 奇）：
  S_j(n)   前 j 步的奇数个数（第 i 位 = x_{i-1} 的奇偶，i = 1..j）
  chi(n)   min{ j >= 1 : T^j(n) < n }（不存在取 None）
  tau(n)   min{ j >= 1 : 3^{S_j(n)} < 2^j }（不存在取 None）
  E_k      { n in [1, 2^k) : chi(n) >= k+1 }
  y_1..     轨道的奇数子序列：y_{t+1} = (3 y_t + 1) / 2^{b_t}，b_t = v_2(3 y_t + 1)，B_t = b_1+..+b_t

条目：
D1  亏损恒等式（精确整数形式与对数形式）
D2  亏损符号 == 系数侧（3^{S_{B_t}} 与 2^{B_t} 的比较），以及亏损 > 0 的精确整数判据
D3  互异正整数序列的倒数和上界（首次重复之前的前缀）
D4  有界轨道最终低于临界：最后临界层 J* 的分布（n <= N1）
D5  正性本质：n = -1 与 n = -5 的反例核对
D6  筛饱和方向 chi(x) >= k+1 ==> x mod 2^j in E_j（j <= k）
D7  首失败几何：第 j0 步为偶、3^{S_j0}/2^{j0} in [1/2, 1)、D <= 2^{j0-1}
D8  c 界 c_j <= 2^j ((3/2)^{S_j} - 1) 的精确整数形式
D9  最小幸存者序列 L_k = min{ n >= 2 : chi(n) >= k+1 }（= chi 记录链，n <= N3）
D10 |alpha_k| 与分支比例（动态规划，k <= 200）
D11 (K)-违反穷举（j <= K2）
D12 tau 有限性的范围检查与 max tau（n <= N4）
"""
import sys
from fractions import Fraction

CAP = 10 ** 6  # 单条轨道步数安全上限


def T(x):
    return x // 2 if x % 2 == 0 else (3 * x + 1) // 2


def chi(n, cap=CAP):
    y = n
    for j in range(1, cap + 1):
        y = T(y)
        if y < n:
            return j
    return None


def odd_suborbit(n, tmax):
    """返回 (ys, bs, Bs)：y_1 = n（要求 n 为奇数），至多 tmax 项。"""
    ys = [n]
    bs = []
    Bs = [0]
    y = n
    for _ in range(tmax):
        v = 3 * y + 1
        b = 0
        while v % 2 == 0:
            v //= 2
            b += 1
        bs.append(b)
        Bs.append(Bs[-1] + b)
        y = v
        ys.append(y)
    return ys, bs, Bs


# ---------------- D1 ----------------
def D1(N=2000, tmax=60):
    import math
    bad_int = []
    bad_log = []
    for n in range(3, N + 1, 2):
        ys, bs, Bs = odd_suborbit(n, tmax)
        num = 1  # prod_{s<=t} (3 y_s + 1)
        den = 1  # prod_{s<=t} y_s
        for t in range(1, tmax + 1):
            s = t - 1
            num *= 3 * ys[s] + 1
            den *= ys[s]
            # 精确恒等式：2^{B_t} y_{t+1} prod_{s<=t} y_s = y_1 prod_{s<=t} (3 y_s + 1)
            lhs = (1 << Bs[t]) * ys[t] * den
            rhs = n * num
            if lhs != rhs:
                if (n, t) not in bad_int:
                    bad_int.append((n, t))
            # 对数形式的亏损恒等式
            sig = sum(math.log1p(1.0 / (3.0 * ys[s2])) for s2 in range(t))
            lhs2 = t * math.log(3) - Bs[t] * math.log(2)
            rhs2 = math.log(ys[t] / n) - sig
            if abs(lhs2 - rhs2) > 1e-9 * (1 + abs(lhs2)):
                if (n, t) not in bad_log:
                    bad_log.append((n, t, lhs2, rhs2))
    return bad_int, bad_log


# ---------------- D2 ----------------
def D2(N=2000, tmax=60):
    bad_sign = []
    bad_crit = []
    for n in range(3, N + 1, 2):
        ys, bs, Bs = odd_suborbit(n, tmax)
        # 逐位重建 S_j 与 B 的对应：S_{B_t} == t
        y = n
        m = 0
        j = 0
        levels = {}
        for _ in range(Bs[tmax] ):
            if y % 2:
                m += 1
            j += 1
            y = T(y)
            levels[j] = m
        for t in range(1, tmax + 1):
            if levels.get(Bs[t]) != t:
                bad_crit.append((n, t, Bs[t], levels.get(Bs[t])))
            # 符号对应：3^t >= 2^{B_t}  <==>  3^{S_{B_t}} >= 2^{B_t}
            a = (3 ** t >= (1 << Bs[t]))
            b = (3 ** levels.get(Bs[t], t) >= (1 << Bs[t]))
            if a != b:
                bad_sign.append((n, t))
    return bad_sign, bad_crit


# ---------------- D3 ----------------
def D3(N=2000, tmax=80):
    """互异阶段（首次重复/到达 1 之前）逐前缀验证两个倒数和上界：
    (H) 任何 t 个互异正整数，Σ1/v <= H_t（本证明对一般发散轨道使用的形式）；
    (n) 若前缀内所有值 >= n，则 Σ1/v <= Σ_{i=0}^{t-1}1/(n+i)（对 chi = inf 轨道使用的形式）。"""
    badH = []
    badn = []
    checked = 0
    checkedn = 0
    for n in range(3, N + 1, 2):
        y = n
        seen = {n}
        acc = Fraction(0)
        H = Fraction(0)
        boundn = Fraction(0)
        minv = n
        for t in range(1, tmax + 1):
            v = 3 * y + 1
            while v % 2 == 0:
                v //= 2
            if v in seen:
                break  # 出现重复，互异性结束
            seen.add(v)
            acc += Fraction(1, v)
            H += Fraction(1, t)
            minv = min(minv, v)
            if minv >= n:
                boundn += Fraction(1, n + t - 1)
            checked += 1
            if acc > H:
                badH.append((n, t))
                break
            if minv >= n:
                checkedn += 1
                if acc > boundn:
                    badn.append((n, t))
                    break
            y = v
            if y == 1:
                break
    return checked, badH, checkedn, badn


# ---------------- D4 ----------------
def D4(N1=20000, Jmax=400):
    """对每个 n 求最后临界层 J*(n) = max{ j <= Jmax : 3^{S_j(n)} >= 2^j }（在到达 1 之前），
    并解析核对到达 1 之后（1-2 循环）的临界层有限。"""
    from collections import Counter
    hist = Counter()
    maxJ = 0
    argmax = None
    for n in range(3, N1 + 1, 2):
        y = n
        m = 0
        Jstar = 0
        for j in range(1, Jmax + 1):
            if y % 2:
                m += 1
            y = T(y)
            if 3 ** m >= (1 << j):
                Jstar = j
            if y == 1:
                break
        if Jstar > maxJ:
            maxJ = Jstar
            argmax = n
        hist[Jstar] += 1
    # 1-2 循环（n = 1）自身的最后临界层
    y = 1
    m = 0
    Jstar1 = 0
    for j in range(1, 2000):
        if y % 2:
            m += 1
        y = T(y)
        if 3 ** m >= (1 << j):
            Jstar1 = j
    return hist, maxJ, argmax, Jstar1


# ---------------- D5 ----------------
def D5(J=200):
    # n = -1：chi = inf（T(-1) = -1 >= -1），轨道有界；检查 3^{S_j} > 2^j 对所有 j
    y = -1
    m = 0
    all_crit = True
    for j in range(1, J + 1):
        if y % 2:
            m += 1
        y = T(y)
        if not (3 ** m > (1 << j)):
            all_crit = False
    # n = -5 的环：-5 -> -7 -> -10 -> -5
    orbit = []
    y = -5
    for _ in range(10):
        orbit.append(y)
        y = T(y)
    # 环 -5 -> -7 -> -10 -> -5：周期 p = 3、奇数步 m = 2
    p, m2 = 3, 2
    neg_cycle_ok = (2 ** p < 3 ** m2)
    return all_crit, orbit, p, m2, neg_cycle_ok


# ---------------- D6 ----------------
def brute_E(k):
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
    return set(out)


def D6(X=1 << 12, K=12):
    Es = {k: brute_E(k) for k in range(1, K + 1)}
    bad = []
    for x in range(3, X + 1, 2):
        # 该 x 的实际 chi 上限 k_max
        y = x
        kmax = 0
        for j in range(1, K + 1):
            y = T(y)
            if y < x:
                break
            kmax = j
        for k in range(1, kmax + 1):
            # 断言 chi(x) >= k+1 ==> x mod 2^j in E_j（j <= k）
            for j in range(1, k + 1):
                r = x % (1 << j)
                if r not in Es[j]:
                    bad.append((x, k, j, r))
                    break
    return bad


# ---------------- D7 ----------------
def D7(N=100000):
    bad = []
    checked = 0
    for n in range(3, N + 1, 2):
        y = n
        m = 0
        j0 = None
        for j in range(1, 400):
            if y % 2:
                m += 1
            last_y = y
            y = T(y)
            if 3 ** m < (1 << j):
                j0 = j
                break
        if j0 is None:
            continue
        checked += 1
        # (i) 第 j0 步的起点 T^{j0-1}(n) = last_y 为偶
        if last_y % 2 != 0:
            bad.append((n, j0, "bit", last_y))
            continue
        # (ii) 1/2 <= 3^{S}/2^{j0} < 1
        if not (2 * 3 ** m >= (1 << j0) and 3 ** m < (1 << j0)):
            bad.append((n, j0, "ratio", m))
            continue
        # (iii) D = 2^{j0} - 3^{m} <= 2^{j0-1}
        D = (1 << j0) - 3 ** m
        if D > (1 << (j0 - 1)):
            bad.append((n, j0, "D", D))
    return checked, bad


# ---------------- D8 ----------------
def D8(N=1 << 16, cap=40):
    bad = []
    worst = None
    checked = 0
    for n in range(3, N + 1, 2):
        y = n
        c = 0
        m = 0
        for j in range(1, cap + 1):
            if y % 2:
                c = 3 * c + (1 << (j - 1))
                m += 1
            y = T(y)
            # 精确整数形式：c_j <= 2^j ((3/2)^m - 1) = 2^{j-m}(3^m - 2^m)（m>=1 时）
            if m >= 1:
                rhs = (1 << (j - m)) * (3 ** m - 2 ** m)
                checked += 1
                if c > rhs:
                    bad.append((n, j, c, rhs))
            if c > 0:
                ratio = Fraction(c, (1 << (j - m)) * (3 ** m - 2 ** m)) if m >= 1 else Fraction(0)
                if m >= 1 and (worst is None or ratio > worst[0]):
                    worst = (ratio, n, j)
    return checked, bad, worst


# ---------------- D9 ----------------
def D9(N3=1 << 24):
    """扫描全部奇数 n < N3 的 chi(n)，输出记录链（chi 严格创新高）与 L_k。"""
    records = []
    best = 0
    nmax_chi = 0
    for n in range(3, N3, 2):
        y = n
        j = 0
        while True:
            y = T(y)
            j += 1
            if y < n:
                break
            if j > CAP:
                raise RuntimeError("cap")
        if j > best:
            best = j
            records.append((n, j))
        nmax_chi = max(nmax_chi, j)
    return records, nmax_chi


# ---------------- D10 ----------------
def D10(K=200):
    """|alpha_k| = #{长度 k 的奇偶向量：对每个 j<=k 有 3^{m_j} >= 2^j}（逐层精确计数）。"""
    states = {(0, 0): 1}
    out = []
    for k in range(1, K + 1):
        new = {}
        for (j, m), cnt in states.items():
            if j != k - 1:
                continue
            for b in (0, 1):
                mm = m + b
                if 3 ** mm >= (1 << k):
                    new[(k, mm)] = new.get((k, mm), 0) + cnt
        states = new
        tot = sum(states.values())
        out.append((k, tot))
    return out


# ---------------- D11 ----------------
def D11(K):
    kept = [(1, T(1), 1, 1)]
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
                if D > 0:
                    checked += 1
                    if yn >= s and s > 1:
                        viol.append((j + 1, s, yn))
                else:
                    nxt.append((s, yn, c_new, m_new))
        kept = nxt
    return checked, viol


# ---------------- D12 ----------------
def D12(N=1 << 20):
    maxt = 0
    arg = None
    inf_count = 0
    for n in range(2, N + 1):
        y = n
        m = 0
        t = None
        for j in range(1, 400):
            if y % 2:
                m += 1
            y = T(y)
            if 3 ** m < (1 << j):
                t = j
                break
        if t is None:
            inf_count += 1
        elif t > maxt:
            maxt = t
            arg = n
    return maxt, arg, inf_count


# ---------------- D13 ----------------
def D13(N=2000, tmax=60):
    """定理 5.1 的计数内核，与正文使用的形式逐字对应：
    (a) 充分条件：y_{t+1} >= y_1 e^{1/3} t^{1/3}  ==> 3^{S_{B_t}} >= 2^{B_t}（逐点整数核对）；
    (b) 矛盾界：若一切 t >= t1 都有 t - t1 <= y_1 e^{1/3} t^{1/3}，则 t 有上界
        （s = t^{1/3} 时 s^3 - y_1 e^{1/3} s - t1 <= 0 的解集有界；给出最大整数解 s 与 t <= s^3）。"""
    import math
    # (a)
    bad_a = []
    checked_a = 0
    for n in range(3, N + 1, 2):
        ys, bs, Bs = odd_suborbit(n, tmax)
        y = n
        m = 0
        levels = {}
        for j in range(1, Bs[tmax] + 1):
            if y % 2:
                m += 1
            y = T(y)
            levels[j] = m
        for t in range(1, tmax + 1):
            # 全程整数核对：前提 y_{t+1}^3 >= 3 y_1^3 t（因 3 >= e，这是充分条件的强化形式）
            if ys[t] ** 3 >= 3 * (n ** 3) * t:
                checked_a += 1
                if not (3 ** levels[Bs[t]] >= (1 << Bs[t])):
                    bad_a.append((n, t))
    # (b) 用整数判据 (t - t1)^3 <= 3 y_1^3 t（3 >= e，解集包含真实解集，仍是有限界）
    out = []
    for n in (3, 27, 1000, 1 << 20, 1 << 71):
        for t1 in (0, 10, 1000):
            def g(t):
                return (t - t1) ** 3 - 3 * (n ** 3) * t
            # 二分找最大整数 t 使 g(t) <= 0
            lo, hi = max(t1, 1), max(t1, 1) + 1
            while g(hi) <= 0:
                hi *= 2
            while lo + 1 < hi:
                mid = (lo + hi) // 2
                if g(mid) <= 0:
                    lo = mid
                else:
                    hi = mid
            t_bound = lo
            ok_at = g(t_bound) <= 0
            ok_above = all(g(t_bound + k) > 0 for k in (1, 2, 10, 10 ** 4))
            out.append((n, t1, t_bound, ok_at, ok_above))
    return checked_a, bad_a, out


def main():
    print("=" * 72)
    bad_int, bad_log = D1()
    print(f"D1 恒等式 2^B_t y_(t+1) prod y_s = y_1 prod (3y_s+1)（n<=2000 奇，t<=60）：违反 {len(bad_int)}")
    print(f"D1 亏损恒等式对数形式（相对误差 1e-9）：违反 {len(bad_log)}")
    bad_sign, bad_crit = D2()
    print(f"D2 S_(B_t) == t 违反 {len(bad_crit)}；亏损符号 <-> 系数侧 违反 {len(bad_sign)}")

    checked, badH, checkedn, badn = D3()
    print(f"D3 倒数和上界 (H)：检查 {checked} 个互异前缀，违反 {len(badH)}")
    print(f"D3 倒数和上界 (n)：满足'前缀全部 >= n'的 {checkedn} 个前缀中违反 {len(badn)}")

    hist, maxJ, argmax, Jstar1 = D4()
    print(f"D4 最后临界层 J*（n<=20000 奇，到达 1 之前）：最大 {maxJ}（n={argmax}）")
    print(f"   J* 分布（前 12 档）：{sorted(hist.items())[:12]}")
    print(f"   n=1 的 1-2 循环的最后临界层 J*(1) = {Jstar1}（此后 3^(j/2) < 2^j 恒成立，m 每 2 步加 1）")

    all_crit, orbit, p, m2, neg_ok = D5()
    print(f"D5 n=-1：3^(S_j) > 2^j 对 j<=200 全成立 = {all_crit}（轨道有界，故正性必要）")
    print(f"D5 n=-5 轨道前 10 项 {orbit}；环 (p={p}, m={m2}) 满足 2^p < 3^m = {neg_ok}")

    bad6 = D6()
    print(f"D6 筛饱和（chi(x)>=k+1 ==> x mod 2^j in E_j，x<=2^12，j<=k<=12）：违反 {len(bad6)}")

    checked7, bad7 = D7()
    print(f"D7 首失败几何（n<=10^5 奇，检查 {checked7} 个）：违反 {len(bad7)}")

    checked8, bad8, worst8 = D8()
    print(f"D8 c 界 c_j <= 2^j((3/2)^m - 1)（精确整数）：检查 {checked8} 点，违反 {len(bad8)}")
    if worst8:
        print(f"   最紧的一处比值 c/界 = {float(worst8[0]):.6f}（n={worst8[1]}, j={worst8[2]}）")

    print("-" * 72)
    print("D9 扫描 chi 记录（n < 2^24 的奇数）：")
    records, nmax_chi = D9()
    print(f"   记录链条数 {len(records)}；范围最大 chi = {nmax_chi}，最后一条记录 {records[-1]}")
    print(f"   记录链（前 20 条）：{records[:20]}")
    print("   L_k 分段（L_k = min{{n>=2: chi(n)>=k+1}}，n < 2^24 内可见的部分）：")
    lo = 1
    for (n, c) in records:
        hi = c - 1
        if hi >= lo:
            print(f"     k = {lo} .. {hi}: L_k = {n}")
        lo = max(lo, c)

    print("-" * 72)
    dl = D10()
    print("D10 |alpha_k| 与分支比（k 抽样）：")
    for (k, tot) in dl:
        if k in (1, 2, 5, 10, 15, 20, 30, 50, 100, 150, 200):
            print(f"   k={k:3d}  |alpha_k|={tot:12d}  比例 |a_k|/2^k={float(Fraction(tot,1<<k)):.6e}")

    print("-" * 72)
    for K2 in (20, 24, 26):
        ck, viol = D11(K2)
        print(f"D11 (K)-违反穷举 j <= {K2}：检查 {ck} 个首次失败向量，违反 {len(viol)}")

    print("-" * 72)
    maxt, arg, infc = D12()
    print(f"D12 n <= 2^20：max tau = {maxt}（n={arg}），tau = inf 的个数 = {infc}")

    print("-" * 72)
    checked_a, bad_a, out13 = D13()
    print(f"D13(a) 充分条件 y_(t+1) >= y_1 e^(1/3) t^(1/3) ==> 3^S_(B_t) >= 2^(B_t)："
          f"命中该前提的 {checked_a} 个点中违反 {len(bad_a)}")
    print("D13(b) 计数矛盾界：整数判据 (t - t1)^3 <= 3 y_1^3 t 的最大解 t（此后 g(t) > 0）")
    for (n, t1, t_bound, ok_at, ok_above) in out13:
        tag = {3: "3", 27: "27", 1000: "1000", 1 << 20: "2^20", 1 << 71: "2^71"}.get(n, str(n))
        print(f"   y_1={tag}, t1={t1}: 最大解 t = {t_bound}，该点成立={ok_at}，"
              f"其后 1、2、10、10^4 步处均不成立={ok_above}")


if __name__ == "__main__":
    main()
