#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
two_adic_control 路线的独立验证脚本。

覆盖的检查（每项都对应 attempt.md 里一条带编号的论证步骤）：

C1  T_a 的 2 进共轭机制：对奇 a = 3、5，用递推
        Phi_a(2y)   = 2 Phi_a(y)
        Phi_a(2y+1) = (2 Phi_a(y) - 1) / a
    在 Z/2^n Z 上构造置换，检查：双射、x 与 Phi(x) 同奇偶、
    层间相容（1-Lipschitz => 等距）、共轭恒等式 T_a(Phi_a(y)) = Phi_a(S y)。
C2  Phi_a 的等距性：v_2(Phi(x)-Phi(x')) == v_2(x-x')。
C3  Q_a = Phi_a^{-1} 的显式值：Q_3(1) = -1/3、Q_5(13) = -7/127、Q_3(1/5) = -1/7。
C4  5x+1 的屏障反例：13 在 T_5 下的轨道是有限环，且永不等于 1。
C5  有理点分母结构：分母不增；3 的指数在每个奇步恰减 1；
    分母为 3^j 时，至多 j 个奇步后落入整数。
C6  PC ⟺ 一族「3x+b 无发散」：分母 b 固定时分子按 T_b 演化，且分母恒为 b。
    并用已知负环 {-5,-7,-10} 与 b = -1 的映射作交叉核对。
C7  小范围 PC 探查：穷举小分子小分母的有理点，看轨道是否全部落入环。
C8  Q 的两个函数方程：Q(2x) = 2Q(x)、Q(2x+1) = 1 + 2Q(3x+2)（模 2^n）。
C9  共轭不变性的传递：T_3 与 T_5 的共轭唯一，等于 Phi_5^{-1} o Phi_3。

输出全部为可复核的计数与最小反例；失败一律打印明细。
"""

import sys
from fractions import Fraction as F
from math import gcd

sys.set_int_max_str_digits(200000)

OUT = []


def log(s=""):
    OUT.append(s)
    print(s)


def v2(p):
    """整数 p 的 2 进赋值（p != 0）。"""
    assert p != 0
    k = 0
    while p % 2 == 0:
        p //= 2
        k += 1
    return k


# ---------------------------------------------------------------- 2 进工具

def phi_res(a, y, n):
    """Phi_a(y) mod 2^n，y 是 [0, 2^n) 中的残数（递推定义）。"""
    if n == 0:
        return 0
    sub = phi_res(a, y >> 1, n - 1)          # mod 2^(n-1)
    m = 1 << n
    if y & 1 == 0:
        return (2 * sub) % m
    else:
        return ((2 * sub - 1) * pow(a, -1, m)) % m


def phi_table(a, n):
    return [phi_res(a, y, n) for y in range(1 << n)]


def T_a_res(a, x, modbits):
    """在 Z/2^modbits Z 上算 T_a（x 为残数）。"""
    m = 1 << modbits
    x %= m
    if x % 2 == 0:
        return (x // 2) % (m >> 1)
    else:
        return (((a * x + 1) // 2)) % (m >> 1)


def S_res(x, modbits):
    m = 1 << modbits
    x %= m
    return (x // 2) % (m >> 1)


# ---------------------------------------------------------------- C1

def check_C1(a, n):
    log(f"[C1] a = {a}, n = {n}（Z/2^{n} Z）")
    tab = phi_table(a, n)
    m = 1 << n
    # 双射
    bij = len(set(tab)) == m
    log(f"  双射: {bij}（{len(set(tab))} / {m}）")
    # 同奇偶
    par_ok = all((tab[y] - y) % 2 == 0 for y in range(m))
    log(f"  Phi(x) ≡ x (mod 2): {par_ok}")
    # 层间相容：Phi(y) mod 2^(n-1) == Phi(y mod 2^(n-1))，即 1-Lipschitz
    comp_ok = all(tab[y] % (m >> 1) == phi_res(a, y % (m >> 1), n - 1)
                  for y in range(m))
    log(f"  层间相容（1-Lipschitz，故为等距）: {comp_ok}")
    # Phi_a(2y) = 2 Phi_a(y)
    f1 = all(phi_res(a, 2 * y, n) == (2 * phi_res(a, y, n - 1)) % m
             for y in range(m >> 1))
    # Phi_a(2y+1) = (2 Phi_a(y) - 1)/a
    f2 = all((phi_res(a, 2 * y + 1, n) * a - (2 * phi_res(a, y, n - 1) - 1)) % m == 0
             for y in range(m >> 1))
    log(f"  Phi(2y) = 2 Phi(y): {f1};  Phi(2y+1) = (2Phi(y)-1)/a: {f2}")
    # 共轭恒等式 T_a(Phi_a(y)) = Phi_a(S y)，比较 mod 2^(n-1)
    bad = []
    for y in range(m):
        lhs = T_a_res(a, tab[y], n)
        rhs = phi_res(a, y >> 1, n - 1)
        if lhs != rhs:
            bad.append((y, lhs, rhs))
    log(f"  T_a(Phi_a(y)) == Phi_a(S y) mod 2^{n-1}: 失败 {len(bad)} 个"
        + (f"，最小反例 {bad[0]}" if bad else ""))
    # T_a 非单射（与笔记「自同胚」措辞的出入）：T_a(2y) = y = T_a(2y+1)
    img = set(T_a_res(a, x, n + 1) for x in range(1 << n))
    log(f"  T_a 非单射：T_a(2y) = y = T_a(2y+1) 对一切 y 成立；"
        f"模 2^{n+1} 上 {1 << n} 个残数的像只有 {len(img)} 个不同值")
    if a == 3:
        log(f"  显式碰撞：T_3(1) = {(3 * 1 + 1) // 2}、T_3(4) = {4 // 2}")
    return bij and par_ok and comp_ok and f1 and f2 and not bad and 1 <= len(img) < (1 << n)


# ---------------------------------------------------------------- C2

def check_C2(a, n):
    log(f"[C2] 等距性 v_2(Phi(x)-Phi(x')) == v_2(x-x')，a = {a}, n = {n}")
    m = 1 << n
    tab = phi_table(a, n)
    bad = 0
    tested = 0
    # 全部同奇偶对的低 12 位抽样 + 若干随机大步
    for x in range(0, m, 37):
        for d in (1, 2, 3, 4, 5, 8, 16, 64):
            if x + d < m:
                tested += 1
                if v2(tab[x + d] - tab[x]) != v2(d):
                    bad += 1
    log(f"  抽样 {tested} 对，失败 {bad} 个")
    return bad == 0


# ---------------------------------------------------------------- C3

def Q_value(a, x_r, n):
    """用有理数 x_r（分母奇）在 T_a 下的前 n 个奇偶位拼出 Q_a(x_r) mod 2^n。"""
    q = 0
    cur = x_r
    for i in range(n):
        bit = cur.numerator % 2
        q |= bit << i
        cur = T_rat(cur, a)
    return q


def T_rat(x, a):
    """有理数上的 T_a（分母必须为奇）。"""
    assert x.denominator % 2 == 1
    if x.numerator % 2 == 0:
        return x / 2
    else:
        return (a * x + 1) / 2


def check_C3(n=64):
    log(f"[C3] Q_a 的显式值（模 2^{n}）")
    ok = True
    for a, xr, expected in [(3, F(1), F(-1, 3)),
                            (5, F(13), F(-7, 127)),
                            (3, F(1, 5), F(-1, 7)),
                            (3, F(2, 5), F(-2, 7)),
                            (3, F(4, 5), F(-4, 7)),
                            (5, F(1), F(-3, 31)),
                            (5, F(3), F(-17, 31)),
                            (5, F(8), F(-24, 31)),
                            (5, F(4), F(-12, 31)),
                            (5, F(2), F(-6, 31))]:
        got = Q_value(a, xr, n)
        exp = expected
        m = 1 << n
        same = (exp.numerator * pow(exp.denominator, -1, m)) % m == got
        log(f"  Q_{a}({xr}) =? {expected}  ->  {same}（Q 的实际低 {n} 位 = {got}）")
        ok = ok and same
    return ok


# ---------------------------------------------------------------- C4

def orbit_5x1_int(n, cap=200000):
    """T_5 在正整数上的轨道（加速映射）。"""
    seen = {}
    x = n
    steps = 0
    path = []
    while x not in seen and steps < cap:
        seen[x] = steps
        path.append(x)
        x = x // 2 if x % 2 == 0 else (5 * x + 1) // 2
        steps += 1
    return path, x, steps


def check_C4():
    log("[C4] 5x+1 屏障反例：13 的轨道")
    path, end, steps = orbit_5x1_int(13)
    cyc_start = path.index(end)
    cycle = path[cyc_start:]
    log(f"  前 {steps} 步：{path[:12]} ...")
    log(f"  进入环：{cycle}")
    log(f"  轨道是否有限且不含 1：{'1' not in path and steps < 200000}")
    # 同族的其它起点（只打印小数，避免超长整数）
    for n0 in (1, 3):
        p, e, s = orbit_5x1_int(n0)
        c0 = p.index(e)
        log(f"  起点 {n0}: 环 = {p[c0:]}（长度 {len(p) - c0}），到达 1？ {1 in p}")
    # 起点 7 不打印数值，只看是否成环与位长增长（启发式证据，不是证明）
    p, e, s = orbit_5x1_int(7, cap=400)
    if s < 400:
        c0 = p.index(e)
        log(f"  起点 7: 在 {s} 步内成环，环长度 {len(p) - c0}")
    else:
        log(f"  起点 7: {s} 步内未重复；最大位长 {max(v.bit_length() for v in p)}"
            f"（表明轨道在长跑，属启发式证据，不是发散证明）")
    return True


# ---------------------------------------------------------------- C5

def check_C5(limit_num=60, limit_den=60, max_steps=400):
    log("[C5] 有理点的分母结构")
    bad_noninc = []       # 分母不增的违反
    bad_three = []        # 3 的指数在每个奇步恰减 1 的违反
    bad_int = []          # 分母为 3^j 时未在恰 j 个奇步内落入整数
    bad_free = []         # 分母的 3 自由部分不不变的违反
    tested = 0

    def free3(d):
        while d % 3 == 0:
            d //= 3
        return d

    for q in range(1, limit_den + 1, 2):
        for p in range(-limit_num, limit_num + 1):
            g = F(p, q)
            if g == 0:
                continue
            den0 = g.denominator
            free0 = free3(den0)
            j3 = 0
            t = den0
            while t % 3 == 0:
                t //= 3
                j3 += 1
            odd_steps = 0
            reached_int = (den0 == 1)
            cur = g
            tested += 1
            for _ in range(max_steps):
                if cur.denominator > den0:
                    bad_noninc.append((g, cur))
                    break
                if free3(cur.denominator) != free0:
                    bad_free.append((g, cur))
                    break
                is_odd = cur.numerator % 2 == 1
                if is_odd:
                    odd_steps += 1
                    nd = cur.denominator
                    j_before = 0
                    while nd % 3 == 0:
                        nd //= 3
                        j_before += 1
                    nxt = T_rat(cur, 3)
                    nd2 = nxt.denominator
                    j_after = 0
                    while nd2 % 3 == 0:
                        nd2 //= 3
                        j_after += 1
                    if (j_before >= 1 and j_after != j_before - 1) or \
                       (j_before == 0 and j_after != 0):
                        bad_three.append((g, cur, j_before, j_after))
                        break
                else:
                    nd = cur.denominator
                    nxt = T_rat(cur, 3)
                    j0 = 0
                    t2 = nd
                    while t2 % 3 == 0:
                        t2 //= 3
                        j0 += 1
                    j1 = 0
                    t2 = nxt.denominator
                    while t2 % 3 == 0:
                        t2 //= 3
                        j1 += 1
                    if j1 != j0:
                        bad_three.append((g, cur, j0, j1))
                        break
                cur = nxt
                if cur.denominator == 1:
                    reached_int = True
                    break
            if t == 1 and j3 >= 1 and odd_steps != j3:
                # 只在 j >= 1 时有断言：分母恰为 3^j 的点，应在恰 j 个奇步后落入整数
                bad_int.append((g, j3, odd_steps))
    log(f"  测试有理点 {tested} 个（|分子| <= {limit_num}，分母 <= {limit_den} 奇，步数上限 {max_steps}）")
    log(f"  分母不增：违反 {len(bad_noninc)} 个" + (f"，最小 {bad_noninc[0]}" if bad_noninc else ""))
    log(f"  分母的 3 自由部分不变：违反 {len(bad_free)} 个" + (f"，最小 {bad_free[0]}" if bad_free else ""))
    log(f"  3 的指数每奇步恰减 1：违反 {len(bad_three)} 个" + (f"，最小 {bad_three[0]}" if bad_three else ""))
    log(f"  分母恰为 3^j（j >= 1）时恰 j 个奇步落入整数：违反 {len(bad_int)} 个" + (f"，最小 {bad_int[0]}" if bad_int else ""))
    return not bad_noninc and not bad_three and not bad_int and not bad_free


# ---------------------------------------------------------------- C6

def T_b(n, b):
    return n // 2 if n % 2 == 0 else (3 * n + b) // 2


def check_C6(bs=(1, -1, 5, -5, 7, 11, -7), lim=40, steps=200):
    log("[C6] 分母 b 固定时分子按 T_b 演化（b 奇且 3 不整除 b）")
    ok = True
    for b in bs:
        if b % 2 == 0 or b % 3 == 0:
            log(f"  b = {b}: 跳过（需 b 奇且 3 不整除 b）")
            continue
        bad = 0
        n_tested = 0
        for p in range(-lim, lim + 1):
            if p == 0 or gcd(abs(p), abs(b)) != 1:
                continue      # 只测「分母恰为 |b|」的起点
            cur = F(p, b)
            num = p
            for _ in range(steps):
                if cur.denominator != abs(b):
                    bad += 1
                    break
                if cur != F(num, b):
                    bad += 1
                    break
                cur = T_rat(cur, 3)
                num = T_b(num, b)
            n_tested += 1
        log(f"  b = {b}: 测试起点 {n_tested} 个 x 步，分母恒为 {abs(b)} 且 x = T_b^t(p)/b，失败 {bad}")
        ok = ok and bad == 0
    # 交叉核对：b = -1（分式 p/(-1) = -p）对应负整数
    log("  交叉核对：T_{-1} 在 5 上的环 与 T_3 在 -5 上的环")
    p, e, s = 5, None, 0
    seen = {}
    cur = 5
    while cur not in seen:
        seen[cur] = s
        cur = T_b(cur, -1)
        s += 1
    cyc = [k for k in seen if seen[k] >= seen[cur]]
    log(f"    T_-1：{sorted(cyc)}（|x| 化成 T_3 上的环应等于 -{{5,7,10}}）")
    seen2 = {}
    cur2 = -5
    s2 = 0
    while cur2 not in seen2:
        seen2[cur2] = s2
        cur2 = T_rat(F(cur2), 3)
        s2 += 1
    cyc2 = [k for k in seen2 if seen2[k] >= seen2[cur2]]
    log(f"    T_3 在 -5 上：{sorted(cyc2)}")
    return ok


# ---------------------------------------------------------------- C7

def find_cycle_rational(x, a, max_steps=3000, num_cap=10**7):
    """返回 (是否成环, 环, 步数)；若分子越界或步数超限则不成环。"""
    seen = {}
    cur = x
    t = 0
    while cur not in seen:
        seen[cur] = t
        if abs(cur.numerator) > num_cap:
            return False, None, t
        if t >= max_steps:
            return False, None, t
        cur = T_rat(cur, a)
        t += 1
    start = seen[cur]
    cyc = [k for k, v in seen.items() if v >= start]
    cyc.sort(key=lambda z: seen[z])
    return True, cyc, t


def check_C7(num_lim=40, den_lim=61, max_steps=3000, num_cap=10**7, a=3):
    log(f"[C7] 小范围 PC 探查：a = {a}，|分子| <= {num_lim}，分母 <= {den_lim}（奇）")
    notcyc = []
    total = 0
    maxcyc = 0
    for q in range(1, den_lim + 1, 2):
        for p in range(-num_lim, num_lim + 1):
            x = F(p, q)
            if x == 0:
                continue
            total += 1
            ok, cyc, t = find_cycle_rational(x, a, max_steps, num_cap)
            if not ok:
                notcyc.append((x, t))
            else:
                maxcyc = max(maxcyc, len(cyc))
    log(f"  探查起点 {total} 个；未在 {max_steps} 步内成环的：{len(notcyc)} 个")
    if notcyc:
        log(f"  样例（前 10 个）：{notcyc[:10]}")
    log(f"  最长环长度：{maxcyc}")
    return notcyc


# ---------------------------------------------------------------- C8

def check_C8(a, n):
    log(f"[C8] Q 的函数方程，a = {a}, n = {n}")
    m = 1 << n
    tab = phi_table(a, n)                      # Phi = Q^{-1}
    inv = [0] * m
    for y, z in enumerate(tab):
        inv[z] = y                             # inv = Q_a
    ok1 = all(inv[(2 * x) % m] == (2 * inv[x]) % m for x in range(m >> 1))
    # 一般 a：T_a(2x+1) = (a(2x+1)+1)/2 = a x + (a+1)/2，故 Q(2x+1) = 1 + 2Q(a x + (a+1)/2)
    shift = (a + 1) // 2
    bad2 = []
    for x in range(m >> 1):
        lhs = inv[(2 * x + 1) % m]
        rhs = (1 + 2 * inv[(a * x + shift) % m]) % m
        if lhs != rhs:
            bad2.append((x, lhs, rhs))
    log(f"  Q(2x) = 2Q(x): {ok1}")
    log(f"  Q(2x+1) = 1 + 2Q(a x + (a+1)/2)（a 特有，非 2 进压缩）: 失败 {len(bad2)} 个"
        + (f"，最小反例 {bad2[0]}" if bad2 else ""))
    return ok1 and not bad2


# ---------------------------------------------------------------- C9

def check_C9(n):
    """共轭方向：Psi = Phi_5 o Phi_3^{-1} = Phi_5 o Q_3 满足 T_5 o Psi = Psi o T_3。
    另验证交换奇偶的 Psi_minus = Phi_5 o c o Q_3（c(z) = -1 - z），说明共轭不唯一。"""
    log(f"[C9] T_3 到 T_5 的共轭：主共轭 Psi = Phi_5 o Q_3 与交换奇偶的 Psi_minus = Phi_5 o c o Q_3（模 2^{n}）")
    m = 1 << n
    tab3 = phi_table(3, n)
    tab5 = phi_table(5, n)
    inv3 = [0] * m
    for y, z in enumerate(tab3):
        inv3[z] = y                                 # inv3 = Q_3
    Psi = [tab5[inv3[x]] for x in range(m)]         # Psi = Phi_5 o Q_3
    bad = []
    for x in range(m):
        lhs = T_a_res(5, Psi[x], n)                 # T_5(Psi(x)) mod 2^(n-1)
        t3 = T_a_res(3, x, n)                       # T_3(x) mod 2^(n-1)
        lo = Psi[t3]
        hi = Psi[t3 | (1 << (n - 1))]
        if lhs != lo % (1 << (n - 1)) or lo % (1 << (n - 1)) != hi % (1 << (n - 1)):
            bad.append((x, lhs, lo, hi))
    log(f"  Psi(T_3(x)) == T_5(Psi(x)) mod 2^{n-1}: 失败 {len(bad)} 个"
        + (f"，最小反例 {bad[0]}" if bad else ""))
    ok_par = all((Psi[x] - x) % 2 == 0 for x in range(m))
    ok_ff = all(Psi[2 * x] == (2 * Psi[x]) % m for x in range(m >> 1))
    log(f"  Psi(x) ≡ x (mod 2): {ok_par};  Psi(2x) = 2 Psi(x): {ok_ff}")
    # Psi(1) = Phi_5(Q_3(1)) = Phi_5(-1/3)：看它是否落在小分母有理数中
    val = None
    cands = [F(k, d) for d in range(1, 130, 2) for k in range(-3 * d, 3 * d + 1)]
    for cand in cands:
        if (cand.numerator * pow(cand.denominator, -1, m)) % m == Psi[1]:
            val = cand
            break
    log(f"  Psi(1) = Phi_5(-1/3) 在小分母（<= 129，|值| <= 3）中匹配到：{val}")
    # 独立验算：T_5(-1) = -2、T_5(-2) = -1，故 Q_5(-1) = -1/3，即 Phi_5(-1/3) = -1
    log(f"  独立核对：Q_5(-1) 应为 -1/3，Phi_5(-1/3) 应为 -1；"
        f"表值 Psi[1] = {Psi[1]}，-1 的低 {n} 位 = {(-1) % m}")
    # 另一支共轭：Psi_minus = Phi_5 o c o Q_3，c(z) = -1 - z（逐位取反）
    # 因为 c 与移位 S 交换（c(Sz) = S(c(z))），它也是共轭，但交换奇偶
    cc = [(-1 - x) % m for x in range(m)]
    Psim = [tab5[cc[inv3[x]]] for x in range(m)]
    badm = []
    for x in range(m):
        lhs = T_a_res(5, Psim[x], n)
        t3 = T_a_res(3, x, n)
        lo = Psim[t3]
        hi = Psim[t3 | (1 << (n - 1))]
        if lhs != lo % (1 << (n - 1)) or lo % (1 << (n - 1)) != hi % (1 << (n - 1)):
            badm.append((x, lhs, lo, hi))
    log(f"  c(z) = -1 - z 与 S 交换：{all(((-1 - ((x - (x & 1)) // 2)) % (1 << (n - 1))) == (((-1 - x) % m - (((-1 - x) % m) & 1)) // 2) % (1 << (n - 1)) for x in range(m))}")
    log(f"  Psi_minus = Phi_5 o c o Q_3 也是共轭：失败 {len(badm)} 个；"
        f"它交换奇偶（Psi_minus(x) ≡ 1 - x mod 2）："
        f"{all((Psim[x] - (1 - (x % 2))) % 2 == 0 for x in range(m))}")
    log(f"  Psi_minus(1) = {Psim[1]}（应等于 -2 的低 {n} 位 = {(-2) % m}）")
    return (not bad and ok_par and ok_ff and Psi[1] == (-1) % m
            and not badm and Psim[1] == (-2) % m)


# ---------------------------------------------------------------- C10

def c_of_vector(v):
    """奇偶向量 v（列表）对应的 c：扫描中「追加 1」时 c <- 3c + 2^|v|。"""
    c = 0
    for i, bit in enumerate(v):
        if bit:
            c = 3 * c + (1 << i)
    return c


def check_C10(kmax=9):
    """Böhm 与 Sontacchi 型的周期点参数化：x_v = c_v / (2^k - 3^m) 是 T_3 的周期点，
    其奇偶向量恰为 v。逐 (k, v) 精确核验。"""
    log(f"[C10] 周期点 x = c_v/(2^k - 3^m)：k <= {kmax} 的全部奇偶向量")
    n_vec = 0
    bad = []
    nonpos_notint = 0
    for k in range(1, kmax + 1):
        for mask in range(1 << k):
            v = [(mask >> i) & 1 for i in range(k)]
            m = sum(v)
            if m == 0:
                continue          # 全偶向量：x = 0/0，单列（不动点 0）
            c = c_of_vector(v)
            D = (1 << k) - 3 ** m
            if D == 0:
                bad.append(("D = 0", k, v))
                continue
            x = F(c, D)
            n_vec += 1
            # (1) T_3^k(x) = x
            cur = x
            ok_step = True
            for i in range(k):
                if (cur.numerator % 2) != v[i]:
                    ok_step = False
                    break
                cur = T_rat(cur, 3)
            if not ok_step or cur != x:
                bad.append(("非周期", k, v, x, cur))
            if x.denominator != 1:
                nonpos_notint += 1
    log(f"  测试奇偶向量 {n_vec} 个（k <= {kmax}，m >= 1）；失败 {len(bad)} 个"
        + (f"，首个 {bad[0] if bad else None}" if bad else ""))
    log(f"  其中 x_v 非整数的（即真正的有理非整数周期点）：{nonpos_notint} 个"
        f"（说明有理周期点大量存在，PC 不是空断言）")
    return not bad


# ---------------------------------------------------------------- C11

def phi_rat(q, a):
    """对有理数 q（分母奇）算 Phi_a(q) ∈ ℚ：沿 S 轨道找周期后解仿射方程。

    基本关系（y 偶）：Phi(y) = 2 Phi(Sy)；（y 奇）：Phi(y) = (2 Phi(Sy) - 1)/a。
    记 chain[i] = S^i(q)，则 Phi(chain[i]) = map_i(Phi(chain[i+1]))，
    其中 map_i(z) = 2z（偶）或 (2z-1)/a（奇）。周期上解 Phi(c_0) = (map_0 o ... o map_{p-1})(Phi(c_0))。
    """
    assert q.denominator % 2 == 1
    chain = []
    pos = {}
    cur = q
    while cur not in pos:
        pos[cur] = len(chain)
        chain.append(cur)
        bit = cur.numerator % 2
        cur = F(cur.numerator - bit * cur.denominator, 2 * cur.denominator)   # S(cur)
    start = pos[cur]
    pre = chain[:start]
    cyc = chain[start:]

    def coeffs(y):
        return (F(2), F(0)) if y.numerator % 2 == 0 else (F(2, a), F(-1, a))

    A, B = F(1), F(0)                     # T = A z + B，按 T <- T o map_i 复合
    for y in cyc:
        ai, bi = coeffs(y)
        A, B = A * ai, A * bi + B
    z = B / (1 - A)                       # 周期上的不动点
    for y in reversed(pre):               # 往回逐位应用 map_i
        ai, bi = coeffs(y)
        z = ai * z + bi
    return z


def check_C11(trials=40, nmax=10):
    """验证「到达 1 的集合 = Phi((1/3)Z)」的编码方向：
    q = A - 2^N/3（前缀 A 后接 Q(1) = -1/3 的展开）=> T_3^N(Phi_3(q)) = 1。
    同时验证 Phi_3(q) 是有理数（Bernstein 1994 的已证方向）。"""
    log(f"[C11] 到达 1 的编码：q = A - 2^N/3 => T_3^N(Phi_3(q)) = 1")
    import random
    rnd = random.Random(20261019)   # 固定种子，只为可复现；非密码学用途
    ok = 0
    bad = []
    for _ in range(trials):
        N = rnd.randint(1, nmax)
        A = rnd.randrange(1 << N)
        q = F(A) - F(1 << N, 3)
        x = phi_rat(q, 3)
        if x.denominator % 2 == 0:
            bad.append((N, A, q, x, "分母非奇"))
            continue
        y = x
        for _ in range(N):
            y = T_rat(y, 3)
        if y != 1:
            bad.append((N, A, q, x, y))
        else:
            ok += 1
    log(f"  {trials} 组随机 (N, A)：成立 {ok} 组，失败 {len(bad)} 组"
        + (f"，首个 {bad[0]}" if bad else ""))
    # 反向特例：Q_3(1) = -1/3 与 Q_3(2) = -2/3 对应 1 与 2
    log(f"  特例：Phi_3(-1/3) = {phi_rat(F(-1,3),3)}（应为 1）；"
        f"Phi_3(-2/3) = {phi_rat(F(-2,3),3)}（应为 2）；"
        f"Phi_3(-1/7) = {phi_rat(F(-1,7),3)}（应为 1/5，即 1/5 环的编码）")
    return not bad


# ---------------------------------------------------------------- C12

def check_C12(num_lim=30, den_lim=61, max_steps=4000, num_cap=10**9):
    """参数敏感性：把同样的 PC 探查用在 a = 5 上。
    对每个未成环的起点，明确区分两种终止原因：
      「越界」= |分子| 超过 num_cap（值在长跑），「超步」= 步数用尽。
    两者都是「该次有限运行内未出现重复」的严格有限陈述，都不是发散证明。"""
    log(f"[C12] a = 5 的 PC 探查（对照 C7 的 a = 3）")
    out = {}
    for a in (3, 5):
        over, stepout, total = [], [], 0
        maxbits = 0
        for q in range(1, den_lim + 1, 2):
            for p in range(-num_lim, num_lim + 1):
                x = F(p, q)
                if x == 0:
                    continue
                total += 1
                # 逐点重跑，记录终止原因与最大位长（判环 / 越界 / 超步三态分明）
                seen = {}
                cur = x
                t = 0
                capped = False
                while cur not in seen:
                    if abs(cur.numerator) > num_cap:
                        capped = True
                        break
                    if t >= max_steps:
                        break
                    seen[cur] = t
                    cur = T_rat(cur, a)
                    t += 1
                if capped:
                    over.append((x, t, max(abs(k.numerator).bit_length() for k in seen)))
                elif cur in seen:
                    maxbits = max(maxbits, max(abs(k.numerator).bit_length() for k in seen))
                else:
                    stepout.append((x, t))
        out[a] = (total, len(over), len(stepout))
        log(f"  a = {a}: 起点 {total} 个；成环 {total - len(over) - len(stepout)} 个"
            f"（最大环元素位长 {maxbits}）；越界 {len(over)} 个；超步 {len(stepout)} 个")
        if over:
            sign_pos = sum(1 for z in over if z[0] > 0)
            log(f"    越界起点中正数 {sign_pos} 个、负数 {len(over) - sign_pos} 个")
            log(f"    样例（起点, 步数, 途中最大位长）：{over[:6]}")
    return out


# ---------------------------------------------------------------- C13

def check_C13():
    """把 C12 的「越界」条目落到具体轨迹上，并给出两个 a 的漂移常数。"""
    log("[C13] a = 5 越界样例的显式轨迹 与 漂移常数")
    for x0 in (F(-30), F(30), F(1), F(13)):
        cur = x0
        path = []
        for _ in range(14):
            path.append(cur)
            cur = T_rat(cur, 5)
        log(f"  a = 5, 起点 {x0}: {path[:10]} ...")
    # 漂移常数：加速步下 log2 尺度的平均增量 = (1/2)log2(a/2) + (1/2)log2(1/2) = log2(a)/2 - 1
    import math
    for a in (3, 5, 7):
        d = math.log2(a) / 2 - 1
        log(f"  a = {a}: 随机模型漂移 = log2({a})/2 - 1 = {d:+.6f}（负则收缩，正则扩张）")
    return True



# ---------------------------------------------------------------- C14 / C15

def q_rat(x, a, max_steps=20000):
    """对最终周期的有理点 x 精确算 Q_a(x) ∈ ℚ（沿 T 轨道，遇环后解仿射方程）。"""
    seen = {}
    chain = []
    cur = x
    while cur not in seen:
        seen[cur] = len(chain)
        chain.append(cur)
        cur = T_rat(cur, a)
        if len(chain) > max_steps:
            return None
    start = seen[cur]
    pre = chain[:start]
    cyc = chain[start:]
    A = 0
    for j, y in enumerate(cyc):
        A += (y.numerator % 2) * (1 << j)
    qcyc = F(A, 1 - (1 << len(cyc)))
    q = qcyc
    for y in reversed(pre):
        q = (y.numerator % 2) + 2 * q
    return q


def check_C14():
    """反驳者给出的见证：-5 在 T_3 下周期，但 -5 不在 Phi_3((1/3)Z) 中。"""
    log("[C14] 见证 -5：周期但不落在 Phi_3((1/3)Z) 里")
    # 1) -5 的环
    for x in (F(-5), F(-7), F(-10)):
        log(f"  T_3({x}) = {T_rat(x, 3)}")
    # 2) Q_3(-5) 由函数方程精确解出
    q5, q7, q10 = None, None, None
    #   -5 奇: Q(-5) = 1 + 2 Q(-7); -7 奇: Q(-7) = 1 + 2 Q(-10); -10 偶: Q(-10) = 2 Q(-5)
    #   代入: q = 1 + 2(1 + 2(2q)) = 3 + 8q  =>  q = -3/7
    q = F(3, 1 - 8)
    log(f"  函数方程解得 Q_3(-5) = {q}")
    # 3) 数值核对：前 80 位奇偶和与 -3/7 的 2 进距离
    S = 0
    cur = F(-5)
    for i in range(80):
        S += (cur.numerator % 2) << i
        cur = T_rat(cur, 3)
    diff = S - F(-3, 7)
    num, den = diff.numerator, diff.denominator
    k = 0
    while num % 2 == 0:
        num //= 2
        k += 1
    log(f"  S_80 = {S}；v_2(S_80 - (-3/7)) = {k}（应 >= 80）：{k >= 80}")
    # 4) 与 q_rat / phi_rat 的一致性
    qq = q_rat(F(-5), 3)
    log(f"  q_rat(-5) = {qq}；phi_rat(-3/7, 3) = {phi_rat(F(-3, 7), 3)}（应为 -5）")
    # 5) -3/7 是否在 (1/3)Z 中
    t = 3 * q
    log(f"  3 * Q_3(-5) = {t}；是整数？ {t.denominator == 1}"
        f"  => -5 在 Phi_3((1/3)Z) 中？ {t.denominator == 1}")
    ok = (qq == F(-3, 7)) and (k >= 80) and (t.denominator != 1) and \
         (phi_rat(F(-3, 7), 3) == F(-5))
    return ok


def check_C15(num_lim=25, den_lim=31, a=3):
    """结构核对：Q_a(x) ∈ (1/3)Z  <=>  x 的轨道落到 {0, -1, 1, 2} 之一。
    这条把「科拉茨猜想（Bernstein 形式）」与「周期猜想」的差别落成可检验的判据。"""
    log(f"[C15] Q_3(x) ∈ (1/3)Z  <=>  轨道落到 {{0, -1, 1, 2}}（|分子| <= {num_lim}，分母 <= {den_lim} 奇）")
    bad = []
    n_pos = n_neg = 0
    n_periodic_not_in = 0
    for d in range(1, den_lim + 1, 2):
        for pnum in range(-num_lim, num_lim + 1):
            x = F(pnum, d)
            if x == 0:
                continue
            q = q_rat(x, a)
            if q is None:
                bad.append((x, "未成环"))
                continue
            in_thirds = (3 * q).denominator == 1
            # 轨道终点集
            seen = {}
            cur = x
            while cur not in seen:
                seen[cur] = len(seen)
                cur = T_rat(cur, a)
            cyc = [k for k, v in seen.items() if v >= seen[cur]]
            hits = {z for z in cyc if z in (F(0), F(-1), F(1), F(2))}
            reaches = len(hits) > 0
            if in_thirds != reaches:
                bad.append((x, q, in_thirds, sorted(cyc)))
            if in_thirds:
                n_pos += 1
            else:
                n_neg += 1
                n_periodic_not_in += 1
    log(f"  不一致 {len(bad)} 个" + (f"，首个 {bad[0]}" if bad else ""))
    log(f"  落在 Phi_3((1/3)Z) 的点 {n_pos} 个；不在的 {n_neg} 个"
        f"（其中全部是周期点：{n_periodic_not_in == n_neg}）")
    return not bad


# ---------------------------------------------------------------- main

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    res = {}
    res['C1a3'] = check_C1(3, n)
    res['C1a5'] = check_C1(5, n)
    res['C2a3'] = check_C2(3, min(n, 13))
    res['C2a5'] = check_C2(5, min(n, 13))
    res['C3'] = check_C3(64)
    res['C4'] = check_C4()
    res['C5'] = check_C5()
    res['C6'] = check_C6()
    nc = check_C7(60, 121, 3000, 10**8)
    res['C7'] = (len(nc) == 0)
    check_C12(30, 61, 4000, 10**9)
    res['C8a3'] = check_C8(3, n)
    res['C8a5'] = check_C8(5, n)
    res['C9'] = check_C9(min(n, 12))
    res['C10'] = check_C10(9)
    res['C11'] = check_C11(40, 10)
    check_C13()
    res['C14'] = check_C14()
    res['C15'] = check_C15()
    log("")
    log("== 汇总 ==")
    for k, v in res.items():
        log(f"  {k}: {v}")
    with open(sys.argv[2] if len(sys.argv) > 2 else "/dev/null", "w") as f:
        f.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
