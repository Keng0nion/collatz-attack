#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
# -*- coding: utf-8 -*-
"""
奇偶向量与 2-adic 结构实验（主脚本，Python 精确整数与有理数）

覆盖四组内容：
  A 组：Terras 仿射公式、c 的递推与闭式、奇偶向量双射与精确计数、首降向量计数 A(k)
  B 组：环方程（Böhm 与 Sontacchi 形）在已知正负环上的复核与小型完备搜索
  C 组：Bernstein 与 Lagarias 共轭映射 Phi 的三种独立构造互校、精确函数方程、
        有理点、以及与原文 Theorem 3.1、表 2.1、表 2.2 的逐格对照
  D 组：引理杀手：把若干启发式中途断言取成精确命题，穷举搜反例并记录最小反例

本文件顶部声明：以下全部是有限范围内的精确枚举；全称命题不能由有限枚举确立。
所有数字由本脚本现场算出，输出为纯文本。
"""
import time
import math
import random
from fractions import Fraction

T0 = time.perf_counter()


def log(tag, msg):
    print(f"[{tag}] {msg}", flush=True)


# ---------------------------------------------------------------- 基础工具
def T(n):
    """加速 Collatz 映射 T(n) = n/2（偶），(3n+1)/2（奇）。整数精确。"""
    return (3 * n + 1) // 2 if (n & 1) else n // 2


def Tk(n, k):
    for _ in range(k):
        n = T(n)
    return n


def parity_vector(x, k):
    """长度 k 的奇偶向量（元组，0 = 偶步，1 = 奇步）。对负整数同样有效。"""
    v = []
    for _ in range(k):
        v.append(x & 1)
        x = T(x)
    return tuple(v)


def pv_int(x, k):
    """奇偶向量读成整数 sum b_i 2^i（等于 Phi^{-1}(x) mod 2^k，见 C 组）。"""
    y = 0
    for i in range(k):
        b = x & 1
        y |= b << i
        x = T(x)
    return y


def c_by_recurrence(v):
    """c 的递推：c_空 = 0；追加 0：c 不变；追加 1（原位序 j）：c <- 3c + 2^j。返回 (c, m)。"""
    c, m = 0, 0
    for j, b in enumerate(v):
        if b:
            c = 3 * c + (1 << j)
            m += 1
    return c, m


def c_by_closed_form(v):
    """闭式：c = sum_idx 3^{m-1-idx} 2^{i_idx}，i_idx 为 1 的位置（升序），m = 1 的个数。"""
    ones = [j for j, b in enumerate(v) if b]
    m = len(ones)
    c = 0
    for idx, j in enumerate(ones):
        c += (3 ** (m - 1 - idx)) * (1 << j)
    return c, m


def first_descent_prefix_len(v):
    """返回最小的 j 使 3^{m_j} < 2^j；若始终不出现返回 None。m_j 为前 j 位的 1 个数。"""
    m = 0
    for j, b in enumerate(v, start=1):
        m += b
        if 3 ** m < (1 << j):
            return j
    return None


# ================================================================ A 组
log("A0", "=" * 72)
log("A0", "A 组：仿射公式、c 的递推与闭式、奇偶向量双射、首降计数")

# A1：c 的递推与闭式对全部长度 <= 16 的向量逐一相符
KA1 = 16
bad = 0
nv = 0
for k in range(1, KA1 + 1):
    for w in range(1 << k):
        v = tuple((w >> i) & 1 for i in range(k))
        c1, m1 = c_by_recurrence(v)
        c2, m2 = c_by_closed_form(v)
        nv += 1
        if (c1, m1) != (c2, m2):
            bad += 1
            if bad <= 5:
                log("A1", f"不一致 v={v} 递推={(c1, m1)} 闭式={(c2, m2)}")
log("A1", f"c 递推 与 闭式 在长度 1..{KA1} 的全部 {nv} 个向量上一致；不一致数 = {bad}")

# A2：仿射公式 T^k(x) = (3^m x + c_v) / 2^k，对全部 k <= 14 与全部 x in [1, 2^k)
KA2 = 14
cnt = 0
bad2 = 0
for k in range(1, KA2 + 1):
    for x in range(1, 1 << k):
        v = parity_vector(x, k)
        c, m = c_by_recurrence(v)
        num = 3 ** m * x + c
        if num % (1 << k) != 0 or num >> k != Tk(x, k):
            bad2 += 1
            if bad2 <= 5:
                log("A2", f"失败 k={k} x={x} v={v} num={num}")
        cnt += 1
log("A2", f"仿射公式在 k<= {KA2}、共 {cnt} 个 (k,x) 组合上成立（含整除性检查），失败数 = {bad2}")

# A2b：大 x 抽样（位宽 60/100/160，固定种子），k <= 40
random.seed(20261018)
K2B = 40
cnt2b = 0
bad2b = 0
for _ in range(200):
    k = random.randint(1, K2B)
    x = random.getrandbits(random.choice([60, 100, 160])) | 1
    v = parity_vector(x, k)
    c, m = c_by_recurrence(v)
    num = 3 ** m * x + c
    if num % (1 << k) != 0 or num >> k != Tk(x, k):
        bad2b += 1
    cnt2b += 1
log("A2b", f"仿射公式在 {cnt2b} 个随机大 x（位宽 60/100/160，k<= {K2B}）上成立，失败数 = {bad2b}")

# A3：奇偶向量映射 Z/2^k -> {0,1}^k 是双射
KA3 = 16
bad3 = 0
for k in range(1, KA3 + 1):
    seen = set()
    for x in range(1 << k):
        seen.add(pv_int(x, k))
    if len(seen) != (1 << k):
        bad3 += 1
        log("A3", f"k={k} 映射非满射：像大小 {len(seen)}")
log("A3", f"k=1..{KA3}：模 2^k 残数到长度 k 奇偶向量的映射是双射，异常数 = {bad3}")

# A3b：区间 [1,2^n] 上每个向量恰好出现 2^{n-k} 次
KA3B = 15
bad3b = 0
checks3b = 0
for k in range(1, KA3B + 1):
    for n in range(k, KA3B + 1):
        cntv = {}
        for x in range(1, (1 << n) + 1):
            v = pv_int(x, k)
            cntv[v] = cntv.get(v, 0) + 1
        for v, cc in cntv.items():
            checks3b += 1
            if cc != (1 << (n - k)):
                bad3b += 1
log("A3b", f"[1,2^n] 上每个长度 k 向量出现次数恒为 2^(n-k)：k<=n<= {KA3B}，"
           f"共 {checks3b} 个 (向量,区间) 格，异常数 = {bad3b}")

# A3c：(1.5) 实现与 pv_int 互逆，移到 C 组（那里定义了 psi_parity）

# A4：首降向量计数 A(k)：k <= 18 全枚举
KA4 = 18
A_count = {}
for k in range(1, KA4 + 1):
    cntk = 0
    for w in range(1 << k):
        v = tuple((w >> i) & 1 for i in range(k))
        if first_descent_prefix_len(v) == k:
            cntk += 1
    A_count[k] = cntk
log("A4", "首降向量计数 A(k)（k 为首次使 3^{m_k} < 2^k 的位置的向量个数）：")
log("A4", "k:  " + " ".join(f"{k:>2}" for k in range(1, KA4 + 1)))
log("A4", "A(k):" + " ".join(f"{A_count[k]:>2}" for k in range(1, KA4 + 1)))
log("A4", f"A(3) = {A_count[3]}：不存在任何长度 3 的奇偶向量满足「前两位比 >= 1、第三位比 < 1」，"
           f"故集合 {{chi = 3}} 为空（该结论对全部正整数 x 成立，不是范围结论）")
log("A4", f"累计密度 sum A(k)/2^k（k<= {KA4}）= {float(sum(Fraction(A_count[k], 1 << k) for k in range(1, KA4 + 1))):.6f}（随机模型下应收敛到 1）")

# ================================================================ B 组
log("B0", "=" * 72)
log("B0", "B 组：环方程 x = c/(2^k - 3^m) 在已知正负环上的复核与小型完备搜索")

for x, k in [(1, 2), (-1, 1), (-5, 3), (-17, 11)]:
    v = parity_vector(x, k)
    c, m = c_by_recurrence(v)
    delta = (1 << k) - 3 ** m
    x_solve = Fraction(c, delta)
    orb = [x]
    y = x
    for _ in range(k - 1):
        y = T(y)
        orb.append(y)
    log("B1", f"x={x} 周期 k={k} 奇步数 m={m} c={c} 2^k-3^m={delta} c/(2^k-3^m)={x_solve}"
              f" 相符={x_solve == x} T^k(x)={Tk(x, k)} 2^k>3^m={(1 << k) > 3 ** m}")
    log("B1", f"    环内 k 个元素：{orb}")

KPY = 20
found = {}
converse_hits = []
nodes = 0
for k in range(1, KPY + 1):
    for w in range(1 << k):
        v = tuple((w >> i) & 1 for i in range(k))
        c, m = c_by_recurrence(v)
        delta = (1 << k) - 3 ** m
        nodes += 1
        if delta == 0 or c % delta != 0:
            continue
        x = c // delta
        if x == 0:
            continue
        if parity_vector(x, k) != v:
            converse_hits.append((abs(x), k, x, v, c, delta))
            continue
        found.setdefault(x, (k, m, c, delta))
log("B2", f"Python 完备搜索：k<= {KPY}，枚举向量 {nodes} 个；命中的环（按 x 去重，含负环）：")
for x in sorted(found, key=lambda t: (t > 0, abs(t))):
    k, m, c, delta = found[x]
    log("B2", f"    x={x} 首次命中 k={k} m={m} c={c} 2^k-3^m={delta}")
log("B2", f"    正环个数 = {sum(1 for x in found if x > 0)}，负环个数 = {sum(1 for x in found if x < 0)}")
log("B2", "「只看整除、不查奇偶向量一致性」的伪命中（最小 8 个，按 |x| 排序）：")
for t in sorted(converse_hits)[:8]:
    log("B2", f"    |x|={t[0]} k={t[1]} x={t[2]} v={t[3]} c={t[4]} delta={t[5]}")
log("B2", f"    伪命中总数（未去重，k<= {KPY}）= {len(converse_hits)}")

# ================================================================ C 组
log("C0", "=" * 72)
log("C0", "C 组：Bernstein 与 Lagarias 共轭映射 Phi 的数值检验（原文式 (1.3)-(1.6)）")


def q_minus1(x, N):
    """原文式 (1.5) 的实现：Phi^{-1}(x) mod 2^N = sum_{i<N} (T^i(x) mod 2) 2^i。
    注意：这是 Phi 的逆映射（也等于奇偶向量读成的整数 pv_int），不是 Phi 本身。"""
    x &= (1 << N) - 1
    y = 0
    for i in range(N):
        b = x & 1
        y |= b << i
        x = (3 * x + 1) >> 1 if b else x >> 1
    return y


def mod2(fr, N):
    """有理数 p/q（q 为奇数）在模 2^N 下的值。"""
    return (fr.numerator * pow(fr.denominator, -1, 1 << N)) % (1 << N)


def phi_formula(x):
    """原文式 (1.6) 的实现：x 为非负整数时 Phi(x) = -sum_{l>=1} 3^{-l} 2^{d_l}，精确 Fraction。"""
    if x == 0:
        return Fraction(0)
    bits = [i for i in range(x.bit_length()) if (x >> i) & 1]
    return -sum(Fraction(1, 3) ** (l + 1) * (1 << d) for l, d in enumerate(bits))


def phi_rec(x, N):
    """由低位到高位的递推实现 Phi：Phi(2z)=2Phi(z)，Phi(2z+1)=(2Phi(z)-1)/3，模 2^{2N} 计算。"""
    MOD = 1 << (2 * N)
    inv3 = pow(3, -1, MOD)
    y = 0
    for i in range(N - 1, -1, -1):
        if (x >> i) & 1:
            y = (2 * y - 1) * inv3 % MOD
        else:
            y = (2 * y) % MOD
    return y & ((1 << N) - 1)


# C1：(1.6) 与 递推 两种 Phi 实现一致；(1.5) 实现是它的逆
KC1 = 12
bad_c1 = 0
bad_c1b = 0
bad_c1c = 0
for N in range(1, KC1 + 1):
    for x in range(1 << N):
        a = mod2(phi_formula(x), N)
        c = phi_rec(x, N)
        if a != c:
            bad_c1 += 1
            if bad_c1 <= 5:
                log("C1", f"两种 Phi 实现不一致 N={N} x={x} (1.6)={a} 递推={c}")
        if q_minus1(c, N) != x:
            bad_c1b += 1
            if bad_c1b <= 3:
                log("C1", f"(1.5) o Phi != id：N={N} x={x} phi_rec={c} q(phi_rec)={q_minus1(c, N)}")
        if phi_rec(q_minus1(x, N), N) != x:
            bad_c1c += 1
            if bad_c1c <= 3:
                log("C1", f"Phi o (1.5) != id：N={N} x={x} q={q_minus1(x, N)} phi=({phi_rec(q_minus1(x, N), N)})")
log("C1", f"两种 Phi 实现（(1.6) 精确有理数 与 剥离递推）在 N<= {KC1}、全部 x<2^N 上一致，不一致数 = {bad_c1}")
log("C1", f"复合恒等式 (1.5) o Phi = id 失败数 = {bad_c1b}；Phi o (1.5) = id 失败数 = {bad_c1c}"
          f"（即 (1.5) 实现与两种 Phi 实现互为逆映射）")

# C2：整数上的精确函数方程与 (1.4)
KC2 = 12
bad_c2 = 0
cnt_c2 = 0
for x in range(1, (1 << KC2) + 1):
    a = phi_formula(x)
    if phi_formula(2 * x) != 2 * a:
        bad_c2 += 1
    if phi_formula(2 * x + 1) != (2 * a - 1) / 3:
        bad_c2 += 1
    if (x & 1) != mod2(a, 1):
        bad_c2 += 1
    cnt_c2 += 3
log("C2", f"精确有理数上：Phi(2x)=2Phi(x)、Phi(2x+1)=(2Phi(x)-1)/3、Phi(x)==x (mod 2)，"
          f"x<= 2^{KC2}，共 {cnt_c2} 次检查，失败数 = {bad_c2}")

# C3：不动点、2 循环与两个已知值（用 Phi 实现 phi_rec 与其逆 q_minus1 各测一遍）
NC3 = 24
inv3_24 = pow(3, -1, 1 << NC3)
neg_inv3 = (-inv3_24) % (1 << NC3)
allones = (1 << NC3) - 1
chk = [
    ("Phi(-1) == -1", phi_rec(allones, NC3) == allones),
    ("Phi(1/3) == 1/3", phi_rec(inv3_24, NC3) == inv3_24),
    ("Phi(1) == -1/3", phi_rec(1, NC3) == neg_inv3),
    ("Phi(-1/3) == 1", phi_rec(neg_inv3, NC3) == 1),
    ("Phi(Phi(1)) == 1", phi_rec(phi_rec(1, NC3), NC3) == 1),
    ("Phi^{-1}(1) == -1/3（(1.5) 实现）", q_minus1(1, NC3) == neg_inv3),
    ("Phi^{-1}(-1/3) == 1（(1.5) 实现）", q_minus1(neg_inv3, NC3) == 1),
    ("Phi^{-1}(-1) == -1", q_minus1(allones, NC3) == allones),
]
for name, ok in chk:
    log("C3", f"{name}（模 2^{NC3}）：{ok}")

# C4：共轭方程 S o Phi^{-1} = Phi^{-1} o T（等价于 Phi o S = T o Phi，即 (1.3)）；S(y)=floor(y/2)
# 注意位数：S 会吃掉最低位，故左边取 N+1 位的 q 再右移
KC4 = 14
bad_c4 = 0
cnt_c4 = 0
for N in range(1, KC4 + 1):
    m = (1 << N) - 1
    for x in range(1 << N):
        y = q_minus1(x, N + 1)
        if q_minus1(T(x) & m, N) != (y >> 1):
            bad_c4 += 1
            if bad_c4 <= 5:
                log("C4", f"失败 N={N} x={x}")
        cnt_c4 += 1
log("C4", f"共轭方程 S o Phi^{{-1}} = Phi^{{-1}} o T 在 N<= {KC4}、共 {cnt_c4} 个 x 上成立，失败数 = {bad_c4}")

# C5：Phi_n 在奇数残数上的置换结构（对照原文 Theorem 3.1 与表 2.1、表 2.2）
def cycles_of_phi_odd(n):
    seen = set()
    cyc = []
    for x in range(1, 1 << n, 2):
        if x in seen:
            continue
        c = []
        y = x
        while y not in seen:
            seen.add(y)
            c.append(y)
            y = phi_rec(y, n)
        cyc.append(tuple(c))
    return cyc


TABLE21 = {
    2: [],
    3: [(1, 5)],
    4: [(1, 5), (9, 13)],
    5: [(1, 21), (5, 17), (7, 23), (9, 29, 25, 13)],
    6: [(1, 21), (3, 35), (5, 17, 37, 49), (7, 23), (9, 29, 25, 13),
        (19, 51), (27, 59), (33, 53), (39, 55), (41, 61, 57, 45)],
}
for n in range(2, 7):
    cyc = [c for c in cycles_of_phi_odd(n) if len(c) > 1]
    norm = sorted(tuple(sorted(c)) for c in cyc)
    want = sorted(tuple(sorted(c)) for c in TABLE21[n])
    log("C5", f"n={n}：长度 >= 2 的循环集合 算出 {norm}")
    log("C5", f"          原文表 2.1 给出 {want}  相符 = {norm == want}")

TABLE22 = {
    2:  [2],
    3:  [2, 1],
    4:  [4, 2],
    5:  [6, 3, 1],
    6:  [6, 7, 3],
    7:  [8, 10, 3, 3],
    8:  [14, 17, 8, 0, 3],
    9:  [14, 21, 18, 4, 0, 3],
    10: [10, 35, 24, 14, 2, 0, 3],
    11: [12, 40, 37, 18, 12, 2, 0, 3],
    12: [16, 48, 70, 23, 16, 10, 2, 0, 3],
    13: [26, 53, 79, 60, 24, 11, 10, 2, 0, 3],
    14: [22, 63, 111, 98, 50, 14, 11, 10, 2, 0, 3],
    15: [18, 81, 129, 153, 84, 40, 11, 11, 10, 2, 0, 3],
    16: [20, 96, 179, 186, 137, 78, 31, 11, 11, 10, 2, 0, 3],
    17: [18, 91, 242, 236, 207, 131, 61, 29, 11, 11, 10, 2, 0, 3],
    18: [12, 104, 305, 308, 312, 192, 105, 56, 29, 11, 11, 10, 2, 0, 3],
}
bad_c5 = 0
badpow = 0
badlong = 0
for n in range(2, 19):
    cyc = cycles_of_phi_odd(n)
    cnt = {}
    for c in cyc:
        L = len(c)
        j = L.bit_length() - 1
        if (1 << j) != L:
            badpow += 1
        cnt[j] = cnt.get(j, 0) + 1
    got = [cnt.get(j, 0) for j in range(0, len(TABLE22[n]))]
    tail = sum(cnt.get(j, 0) for j in range(len(TABLE22[n]), n + 1))
    want = TABLE22[n]
    ok = (got == want) and tail == 0
    if not ok:
        bad_c5 += 1
    if n >= 6 and cnt.get(n - 4, 0) != 3:
        badlong += 1
    log("C5b", f"n={n:>2}：|X_n,j| j=0..{len(want)-1} 算出 {got} 原文 {want} 相符 = {ok}"
               f"（j = n-4 处长度为 2^(n-4) 的循环个数 = {cnt.get(n - 4, 0)}）")
log("C5b", f"表 2.2 对照（n=2..18，逐格比较）：不符行数 = {bad_c5}；循环长度非 2 的幂的次数 = {badpow}；"
           f"n>=6 时「三条长度 2^(n-4) 的长循环」不符的次数 = {badlong}")
# 循环长度守恒
for n in (10, 14, 18):
    cyc = cycles_of_phi_odd(n)
    tot = sum(len(c) for c in cyc)
    log("C5c", f"n={n}：奇数残数总数（算出）= {tot}，应为 2^{n-1} = {1 << (n - 1)}，相符 = {tot == (1 << (n - 1))}")

# C6：有理点：Phi 把有理数映到有理数（对若干分母为奇数的有理 2 进数精确计算）
def binary_expansion(r):
    """返回 (1 位位置列表（到周期前）, 周期起点, 周期长度, 周期内的 1 位位置（相对起点）)。"""
    states = {}
    ones = []
    i = 0
    cur = r
    while True:
        if cur in states:
            j0 = states[cur]
            period = i - j0
            if period <= 0:
                raise RuntimeError("周期检测失败")
            return ones, j0, period, [d - j0 for d in ones if j0 <= d < i]
        states[cur] = i
        bit = cur.numerator & 1
        if bit:
            ones.append(i)
        cur = (cur - bit) / 2
        i += 1
        if i > 4000:
            raise RuntimeError("未检测到周期")


def phi_rational(r):
    """分母为奇数的有理数 r：用 2 进展开的周期与等比尾和精确求 Phi(r)。"""
    assert r.denominator % 2 == 1
    ones, j0, period, ones_per = binary_expansion(r)
    prefix = [d for d in ones if d < j0]
    L = len(prefix)
    A = sum(Fraction(1 << d, 3 ** (l + 1)) for l, d in enumerate(prefix))
    p = len(ones_per)
    if p == 0:
        return -A
    B = sum(Fraction(1 << (e + j0), 3 ** (L + i + 1)) for i, e in enumerate(ones_per))
    B = B / (1 - Fraction(1 << period, 3 ** p))
    return -(A + B)


NC6 = 20
for num, den in [(1, 1), (-1, 1), (1, 3), (-1, 3), (1, 5), (3, 5), (1, 7), (1, 9), (5, 7), (-1, 5)]:
    r = Fraction(num, den)
    val = phi_rational(r)
    rmod = mod2(r, NC6)
    okmod = mod2(val, NC6) == phi_rec(rmod, NC6)
    okinv = q_minus1(mod2(val, NC6), NC6) == rmod
    log("C6", f"r={r}：精确算出 Phi(r)={val}（分母 {val.denominator}，故为有理数）；"
              f"与递推实现模 2^{NC6} 相符 = {okmod}；与 (1.5) 实现的复合恒等式相符 = {okinv}")

# ================================================================ D 组
log("D0", "=" * 72)
log("D0", "D 组：引理杀手（把启发式断言取成精确命题后穷举搜反例）")

NDMAX = 18
XMAX = 1 << NDMAX
chi = [0] * (XMAX + 1)
n_inf = 0
for x in range(1, XMAX + 1):
    if x == 1:
        chi[x] = -1        # chi(1) = 无穷（1 在 1-2 循环上，永不降到自身以下）
        n_inf += 1
        continue
    y = x
    k = 0
    while k <= 20000:
        y = T(y)
        k += 1
        if y < x:
            break
    if k > 20000:
        chi[x] = -1
        n_inf += 1
    else:
        chi[x] = k
log("Dpre", f"停时 chi(x)（最小 k 使 T^k(x) < x）在 x<= 2^{NDMAX} 上全部算出；chi 为「无穷」的 x 个数 = {n_inf}"
            f"（应为 1，即 x=1）；最大停时 = {max(chi[1:])} 在 x = {chi.index(max(chi[1:]))}")

# D1 命题 K1：对固定 k 与固定奇偶向量，T^k(x) < x 的取值恒定（即只依赖 x mod 2^k）
KD1 = 12
ND1 = 13
groups = {}
for k in range(1, KD1 + 1):
    g = {}
    for x in range(1, (1 << ND1) + 1):
        g.setdefault(parity_vector(x, k), []).append(x)
    groups[k] = g
ce1 = []
for k in range(1, KD1 + 1):
    for v, xs in groups[k].items():
        tv, fv = [], []
        for x in xs:
            (tv if Tk(x, k) < x else fv).append(x)
        if tv and fv:
            ce1.append((k, v, min(tv), min(fv)))
log("D1", f"命题 K1：同一奇偶向量内 T^k(x) < x 恒同。x<= 2^{ND1}，k<= {KD1}")
log("D1", f"    违反的 (k, 向量) 组数 = {len(ce1)}；按 k 分布 = "
          + ", ".join(f"{k}:{sum(1 for t in ce1 if t[0] == k)}" for k in range(1, KD1 + 1) if any(t[0] == k for t in ce1)))
m1 = min(ce1, key=lambda t: (max(t[2], t[3]), t[0]))
log("D1", f"    最小反例（按组内涉及的最大 x 最小）：k={m1[0]} v={m1[1]} 满足下降的最小 x={m1[2]}，不满足下降的最小 x={m1[3]}")
m1b = [t for t in ce1 if t[2] >= 2 and t[3] >= 2]
if m1b:
    m1c = min(m1b, key=lambda t: (max(t[2], t[3]), t[0]))
    log("D1", f"    限制两个 x 都 >= 2 后的最小反例：k={m1c[0]} v={m1c[1]} x={m1c[2]}（下降）与 x={m1c[3]}（不下降）")
list1 = sorted(ce1, key=lambda t: (max(t[2], t[3]), t[0]))[:10]
log("D1", f"    最小的 10 组反例（涉及的最大 x 排序）：{[(t[0], t[2], t[3]) for t in list1]}")

# D2 命题 K2：{chi = j} 是模 2^j 完整剩余类之并（朴素版）与精确版结构
# 精确版（本脚本推导并逐点验证）：对 x >= 1、j >= 1，记 v = pv_j(x)，m_i = v 前 i 位的 1 个数，
# c_i = 该前缀的仿射常数，则
#   chi(x) = j  <=>  3^{m_j} < 2^j  且  x > theta_j  且  对一切 i<j：3^{m_i} >= 2^i 或 x <= theta_i
# 其中 theta_i = c_i/(2^i - 3^{m_i})（此式仅在 3^{m_i} < 2^i 时出现）。
# 类代表元 r（使 pv_j(r) = v 的最小非负残数）= Phi(wv) 模 2^j（因为 pv_j = Phi^{-1} 模 2^j）。
JCHK = 12
bad_pred = 0
ce2_naive = []
first_bad = None
for j in range(1, JCHK + 1):
    for wv in range(1 << j):
        bits = [(wv >> i) & 1 for i in range(j)]
        ms, cs = [], []
        m = 0
        c = 0
        for i, b in enumerate(bits, start=1):
            if b:
                c = 3 * c + (1 << (i - 1))
                m += 1
            ms.append(m)
            cs.append(c)
        hi = None
        for i in range(1, j):
            if 3 ** ms[i - 1] < (1 << i):
                t = Fraction(cs[i - 1], (1 << i) - 3 ** ms[i - 1])
                hi = t if hi is None else min(hi, t)
        mu_ok = 3 ** ms[j - 1] < (1 << j)
        th_j = Fraction(cs[j - 1], (1 << j) - 3 ** ms[j - 1]) if mu_ok else None
        r = phi_rec(wv, j)
        assert pv_int(r, j) == wv, (j, wv, r)
        start = r if r >= 1 else (1 << j)
        cls = list(range(start, XMAX + 1, 1 << j))
        if not cls:
            continue
        txs, fxs = [], []
        for x in cls:
            pred = mu_ok and (th_j is not None and x > th_j) and (hi is None or x <= hi)
            truth = (chi[x] == j)
            if pred != truth:
                bad_pred += 1
                if first_bad is None:
                    first_bad = (j, wv, x, pred, truth)
            (txs if truth else fxs).append(x)
        if txs and fxs:
            ce2_naive.append((min(txs), j, wv, min(txs), min(fxs)))
log("D2", f"命题 K2（朴素版）：{{chi = j}} 是模 2^j 完整剩余类之并。x<= 2^{NDMAX}，j<= {JCHK}")
log("D2", f"    违反的 (j, 类) 组数 = {len(ce2_naive)}")
for t in sorted(ce2_naive, key=lambda z: (z[0], z[1]))[:8]:
    log("D2", f"    j={t[1]} v={tuple((t[2] >> i) & 1 for i in range(t[1]))}：该类 chi=j 的最小 x={t[3]}，"
              f"但同类还有 chi!=j 的最小 x={t[4]}")
if ce2_naive:
    m2 = min(ce2_naive, key=lambda z: (z[0], z[1]))
    log("D2", f"    最小反例（按 chi=j 的最小 x 排序）：j={m2[1]} x={m2[3]}（与同类 x={m2[4]} 矛盾）")
log("D2", f"命题 K2（精确版，含阈值截断）：对 x<= 2^{NDMAX}、j<= {JCHK} 的全部 (x, j)，"
          f"判据与真实 chi 不符的次数 = {bad_pred}"
          + (f"，首个不符：j={first_bad[0]} v={tuple((first_bad[1] >> i) & 1 for i in range(first_bad[0]))} x={first_bad[2]} 判据={first_bad[3]} 真实={first_bad[4]}" if first_bad else ""))

# D3 命题 K3：Terras 系数停时猜想 tau(x) = chi(x)（x >= 2）
tau = [0] * (XMAX + 1)
for x in range(1, XMAX + 1):
    xx = x
    m = 0
    k = 0
    while True:
        b = xx & 1
        xx = T(xx)
        k += 1
        if b:
            m += 1
        if 3 ** m < (1 << k):
            tau[x] = k
            break
        if k > 200:
            tau[x] = -1
            break
neq = [x for x in range(2, XMAX + 1) if tau[x] != chi[x]]
log("D3", f"命题 K3（Terras 系数停时猜想）：tau(x) = chi(x) 对一切 x >= 2。x<= 2^{NDMAX}")
log("D3", f"    x=1 处 tau={tau[1]} chi={chi[1]}（x=1 被猜想排除，此项不符是已知的）")
log("D3", f"    2 <= x <= 2^{NDMAX} 中 tau != chi 的 x 个数 = {len(neq)}"
          + (f"，最小几个 = {neq[:5]}" if neq else "（全部相符）"))
log("D3", f"    2 <= x <= 2^{NDMAX} 中 tau 的最大值 = {max(tau[2:])}，chi 的最大值 = {max(chi[2:])}")

# D3b 精确边界分析：可能造成 tau < chi 的向量（阈值 theta_v >= 1 且类内最小正元素 x_min <= theta_v）
log("D3b", "边界条件：k = tau(x) 时 T^k(x) < x 等价于 x > theta_v = c_v/(2^k-3^m)。"
           "故反例只能是「theta_v >= 1 且该类最小正元素 x_min <= theta_v」的向量，且 x = x_min 即最小反例")
danger = []
for k in range(1, 21):
    for w in range(1 << k):
        v = tuple((w >> i) & 1 for i in range(k))
        if first_descent_prefix_len(v) != k:
            continue
        c, m = c_by_recurrence(v)
        delta = (1 << k) - 3 ** m
        if c >= delta:
            xmin = phi_rec(w, k)
            if xmin == 0:
                xmin = 1 << k
            danger.append((k, v, Fraction(c, delta), xmin))
viol = [t for t in danger if 2 <= t[3] <= t[2]]
log("D3b", f"    k<= 20 中 theta_v >= 1 的首降向量个数 = {len(danger)}")
log("D3b", f"    其中「x_min <= theta_v」（即真的会破坏 tau = chi 且 x >= 2）的向量个数 = {len(viol)}")
if viol:
    for t in sorted(viol, key=lambda z: z[3])[:8]:
        log("D3b", f"    反例：k={t[0]} v={t[1]} theta={float(t[2]):.6f} x_min={t[3]}")
log("D3b", f"    theta_v >= 1 的最小 k 分布（k: 个数）= "
          + ", ".join(f"{k}:{sum(1 for t in danger if t[0] == k)}" for k in range(1, 21) if any(t[0] == k for t in danger)))
log("D3b", f"    theta_v 的最大值 = {max(float(t[2]) for t in danger):.4f}（k={max(danger, key=lambda t: t[2])[0]}）")
for t in sorted(danger, key=lambda z: z[2])[:4]:
    log("D3b", f"    theta 最小的几个之一：k={t[0]} v={t[1]} theta={float(t[2]):.6f} x_min={t[3]}")
log("D3b", f"    x_min = 1 的向量（只可能造成 x=1 处不符）："
          + str([(t[0], tuple(t[1])) for t in danger if t[3] == 1][:6]))
# 逐点核对 x_min 的奇偶向量
badx = 0
for k, v, th, xmin in danger:
    if parity_vector(xmin, k) != v:
        badx += 1
log("D3b", f"    核对：全部 {len(danger)} 个危险向量的 x_min 确实以该向量为奇偶向量（不符数 = {badx}）")
log("D3b", f"    最小的「x_min 与 theta 的差距」（theta - x_min 的最大值，取遍全部危险向量）= "
          f"{max(float(t[2]) - t[3] for t in danger):.3f}（该值为负表示无向量造成反例）")
close = sorted(danger, key=lambda t: t[3] - t[2])[:6]
for t in close:
    log("D3b", f"    最接近反例的 6 个（按 x_min - theta 升序）：k={t[0]} x_min={t[3]} theta={float(t[2]):.4f} "
              f"x_min - theta = {t[3] - float(t[2]):.1f}")

# D4 命题 K4：停时在同余类上均匀（精确计数版；只统计有限停时 j >= 1，排除 chi = 无穷的 x=1）
ce4 = []
seen_nk = {}
maxrel_j_eq_k = {}
maxrel_all = {}
maxrel_pairs = {}
PAIRS = [(2, 2), (3, 2), (4, 2), (4, 4), (5, 5), (6, 3), (6, 4), (6, 6)]
for k in range(1, 8):
    M = 1 << k
    total = {}
    percls = {}
    for n in range(k, NDMAX + 1):
        X = 1 << n
        start = 1 if n == k else (1 << (n - 1)) + 1
        for x in range(start, X + 1):
            cj = chi[x]
            total[cj] = total.get(cj, 0) + 1
            d = percls.setdefault(x & (M - 1), {})
            d[cj] = d.get(cj, 0) + 1
        mx_all = 0.0
        mx_eqk = 0.0
        for j in sorted(total):
            if j < 1:
                continue
            want = Fraction(total[j], M)
            for a in range(M):
                got = percls.get(a, {}).get(j, 0)
                if got != want:
                    t = (n, k, a, j, got, want, total[j])
                    if (n, k, j) not in seen_nk:
                        seen_nk[(n, k, j)] = t
                    ce4.append(t)
            wantf = total[j] / M
            mx = 0.0
            for a in range(M):
                got = percls.get(a, {}).get(j, 0)
                mx = max(mx, abs(got - wantf) / wantf) if wantf > 0 else mx
            mx_all = max(mx_all, mx)
            if j == k:
                mx_eqk = mx
            if (k, j) in PAIRS:
                maxrel_pairs[(k, j, n)] = mx
        maxrel_all[(k, n)] = mx_all
        maxrel_j_eq_k[(k, n)] = mx_eqk
log("D4", f"命题 K4（同余类均匀性）：#{{x<=2^n, x mod 2^k = a, chi = j}} == 2^-k * #{{x<=2^n, chi = j}}"
          f"（k<= 7，n<= {NDMAX}，j >= 1 有限停时）")
log("D4", f"    违反的 (n,k,a,j) 组合数 = {len(ce4)}（该精确等式几乎处处不成立）")
for nk in sorted(seen_nk)[:6]:
    t = seen_nk[nk]
    log("D4", f"    n={t[0]} k={t[1]} j={t[3]} 首次失败于 a={t[2]}：该类计数={t[4]}，均匀性要求={t[5]}"
              f"（= {float(t[5]):.4f}），全局计数={t[6]}")
nmin = min(t[0] for t in ce4)
kmin = min(t[1] for t in ce4 if t[0] == nmin)
amin = min(t[2] for t in ce4 if t[0] == nmin and t[1] == kmin)
jmin = [t[3] for t in ce4 if t[0] == nmin and t[1] == kmin and t[2] == amin][0]
log("D4", f"    最小反例：(n, k, a, j) = ({nmin}, {kmin}, {amin}, {jmin})"
          f"（即 x <= {1 << nmin} 上，chi = {jmin} 在类 {amin} mod {1 << kmin} 内的计数与均匀值不符）")
log("D4", "    相对偏差 sup_a |count_a - total/2^k| / (total/2^k)：")
log("D4", "      （甲）j = k（自然模数）时：")
for k in range(2, 7):
    row = [f"n={n}:{maxrel_j_eq_k.get((k, n), float('nan')):.4f}" for n in (12, 14, 16, 18)]
    log("D4", f"        k={k}  " + "  ".join(row))
log("D4", "      （乙）指定 (k, j) 对：")
for (k, j) in PAIRS:
    row = [f"n={n}:{maxrel_pairs.get((k, j, n), float('nan')):.4f}" for n in (12, 14, 16, 18)]
    log("D4", f"        k={k} j={j}  " + "  ".join(row))


log("X", f"总耗时 {time.perf_counter() - T0:.2f} 秒")
