#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
checks_automata_v2.py ——「形式化与自动机路线」第二轮（2026 年 10 月 20 日）的独立验证脚本。

本脚本只验证本轮的结论，与同目录的 checks_formal_automata.py（第一轮）不共享代码。
运行：python3 -u checks_automata_v2.py        （约 1 至 2 分钟，主要在 B3 的停时数组）

记号（与 attempt.md 一致）：
  T 为加速科拉茨映射：T(n) = n/2（n 偶）、(3n+1)/2（n 奇）。
  v_k(n) = (n, T(n), ..., T^{k-1}(n)) 的奇偶，称为 n 的「长度 k 奇偶词」。
  T^k(n) = (3^{m(v)} n + c(v)) / 2^k，其中 v = v_k(n)，m(v) 为 v 中 1 的个数。
  σ(n) = min{d >= 1 : T^d(n) < n}（首降时间），σ(n) = ∞ 表示永不下降。
  「上升」条件：3^{m} >= 2^{len}（则整类的每个成员在对应步数都不下降）。
  定理 D（残类二分）：长度 a 的词 w 的类 mod 2^a 上 σ 有界，当且仅当 w 有某个真前缀是下降的
  （3^{m_i} < 2^i）；所有前缀都上升的类上 σ 无界，且有无界见证族。
"""
import sys
from fractions import Fraction
from collections import defaultdict

FAIL = 0


def check(cond, name, extra=""):
    global FAIL
    tag = "[通过]" if cond else "[失败]"
    if not cond:
        FAIL += 1
    print(f"{tag} {name}" + (f" —— {extra}" if extra else ""))
    sys.stdout.flush()


def T_int(n):
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def word_int(n, k):
    """n 的长度 k 奇偶词（n 取整数代表元）"""
    w = []
    v = n
    for _ in range(k):
        w.append(v & 1)
        v = T_int(v)
    return tuple(w)


def c_of_word(w):
    """由递推 c(空)=0；追加 0：c 不变；追加 1（当前长度 j）：c <- 3c + 2^j。返回 (c, m)。"""
    c = 0
    m = 0
    for j, b in enumerate(w):
        if b:
            c = 3 * c + (1 << j)
            m += 1
    return c, m


# ------------------------------------------------------------------ A 段
print("=" * 78)
print("A 段：编码与周期点")
print("=" * 78)

# A1：长度 k 的词与模 2^k 残数的双射（代表元 1..2^k）
ok = True
detail = []
for k in range(1, 13):
    seen = {}
    for a in range(1, (1 << k) + 1):
        w = word_int(a, k)
        if w in seen:
            ok = False
            detail.append((k, a, seen[w]))
        seen[w] = a
    ok = ok and (len(seen) == (1 << k))
check(ok, "A1 长度 k 奇偶词与 1..2^k 残数一一对应",
      f"k = 1..12，重复或缺口 = {len(detail)}")

# A2：后缀刻画。对 x mod 2^N，T^j(x) ≡ 1 (mod 2^{N-j}) 当且仅当长度 N 词的后 N-j 位是 1,0,1,0,...
bad = 0
checked = 0
for N in range(4, 14):
    for x in range(1 << N):
        w = word_int(x if x else (1 << N), N)
        y = x
        for j in range(0, N + 1):
            # 检查这一刻：y ≡ T^j(x) (mod 2^{N-j})，词的后 N-j 位 = (1,0,1,0,...)
            tail = w[j:]
            alt = tuple(1 if (i % 2 == 0) else 0 for i in range(len(tail)))
            lhs = (y % (1 << (N - j)) == 1 % (1 << (N - j)))
            rhs = (tail == alt)
            checked += 1
            if lhs != rhs:
                bad += 1
                if bad <= 3:
                    print("    反例：", N, x, j, y, tail)
            if j == N:
                break
            y = T_int(y)
check(bad == 0, "A2 后缀刻画 T^j(x) ≡ 1 (mod 2^{N-j}) ⟺ 词的后缀为 (1,0) 交替",
      f"检查 {checked} 组，不符 {bad} 组（N = 4..13）")

# A3：周期点公式 x_v = c(v)/(2^k - 3^{m(v)})
def word_of_frac_k(x, k):
    """有理数（分母为奇数）的长度 k 奇偶词"""
    w = []
    for _ in range(k):
        num = x.numerator
        if num % 2 == 0:
            w.append(0)
            x = x / 2
        else:
            w.append(1)
            x = (3 * x + 1) / 2
    return tuple(w)


bad_word = 0
bad_fix = 0
bad_period = 0
sign_ok = True
tested = 0
for k in range(1, 8):
    for w in range(1 << k):
        word = tuple((w >> i) & 1 for i in range(k))
        c, m = c_of_word(word)
        D = (1 << k) - 3 ** m
        x = Fraction(c, D)
        tested += 1
        if word_of_frac_k(x, k) != word:
            bad_word += 1
            if bad_word <= 3:
                print("    词失败：", k, word, x)
        # T^k(x) = x 验证（分数精确）
        y = x
        for _ in range(k):
            y = y / 2 if (y.numerator % 2 == 0) else (3 * y + 1) / 2
        if y != x:
            bad_fix += 1
            if bad_fix <= 3:
                print("    不动失败：", k, word, x, y)
        # 符号：D > 0（即 2^k > 3^m）时 x >= 0，D < 0 时 x <= 0
        if D > 0 and x < 0:
            sign_ok = False
        if D < 0 and x > 0:
            sign_ok = False
check(bad_word == 0, "A3a 对每个长度 k ≤ 7 的词，x_v = c/(2^k−3^m) 的奇偶词恰为 v",
      f"{tested} 个词，不符 {bad_word}")
check(bad_fix == 0, "A3b T^k(x_v) = x_v（分数精确）", f"不符 {bad_fix}")
check(sign_ok, "A3c 符号：2^k > 3^m ⟺ x_v >= 0（且 v ≠ 0^k 时 > 0）")

# A3d：精确周期 = 词的原始根长
def prim_root_len(w):
    n = len(w)
    for d in range(1, n + 1):
        if n % d == 0 and all(w[i] == w[i % d] for i in range(n)):
            return d
    return n


bad_per = 0
for k in range(1, 8):
    for w in range(1 << k):
        word = tuple((w >> i) & 1 for i in range(k))
        c, m = c_of_word(word)
        x = Fraction(c, (1 << k) - 3 ** m)
        d0 = prim_root_len(word)
        # T^{d0}(x) = x 且对 d < 2k 的其他 d 不成立（除 d0 的倍数）
        y = x
        for d in range(1, 2 * k + 1):
            y = y / 2 if (y.numerator % 2 == 0) else (3 * y + 1) / 2
            if y == x and d % d0 != 0:
                bad_per += 1
                if bad_per <= 3:
                    print("    周期失败：", k, word, d0, d)
check(bad_per == 0, "A3d x_v 的 T 精确周期 = 词的原始根长（d < 2k 内无杂散周期）")

# A3e：模算术第二个见证（复现性）：X = c·D^{-1} mod 2^N，则 T^k(X) ≡ X mod 2^{N-k}
N = 24
bad_mod = 0
for k in range(1, 9):
    for w in range(1 << k):
        word = tuple((w >> i) & 1 for i in range(k))
        c, m = c_of_word(word)
        D = ((1 << k) - 3 ** m) % (1 << N)
        X = (c * pow(D, -1, 1 << N)) % (1 << N)
        Y = (3 ** m * X + c) // (1 << k) if (3 ** m * X + c) % (1 << k) == 0 else None
        if Y is None or (Y - X) % (1 << (N - k)) != 0:
            bad_mod += 1
check(bad_mod == 0, "A3e 模 2^24 见证：3^m X + c ≡ 0 (mod 2^k) 且商 ≡ X (mod 2^{24-k})",
      f"不符 {bad_mod}（k ≤ 8）")

# A4：原词计数（莫比乌斯）
def mobius(n):
    if n == 1:
        return 1
    f = 0
    p = 2
    t = n
    while p * p <= t:
        if t % p == 0:
            t //= p
            if t % p == 0:
                return 0
            f += 1
        p += 1
    if t > 1:
        f += 1
    return -1 if f % 2 else 1


bad_mob = 0
for k in range(1, 19):
    brute = sum(1 for w in range(1 << k)
                if prim_root_len(tuple((w >> i) & 1 for i in range(k))) == k)
    form = sum(mobius(k // d) * (1 << d) for d in range(1, k + 1) if k % d == 0)
    if brute != form:
        bad_mob += 1
        print("    不符：", k, brute, form)
check(bad_mob == 0, "A4 原词计数 = Σ_{d|k} μ(k/d) 2^d（暴力一致，k ≤ 18）")

# A5：整数周期点表
known = {0: "0", -1: "-1", 1: "1", 2: "2", -5: "-5", -7: "-7", -10: "-10",
         -17: "-17", -25: "-25", -37: "-37", -55: "-55", -82: "-82",
         -41: "-41", -61: "-61", -91: "-91", -136: "-136", -68: "-68", -34: "-34"}
period_pts = defaultdict(set)
for k in range(1, 13):
    for w in range(1 << k):
        word = tuple((w >> i) & 1 for i in range(k))
        c, m = c_of_word(word)
        D = (1 << k) - 3 ** m
        if c % D == 0:
            period_pts[prim_root_len(word)].add(c // D)
unexpected = {}
for p, s in period_pts.items():
    extra = s - set(known.keys())
    if extra:
        unexpected[p] = extra
print("    各精确周期的整数周期点：")
for p in sorted(period_pts):
    print(f"      周期 {p}: {sorted(period_pts[p])}")
check(not unexpected and 0 in period_pts[1] and -1 in period_pts[1]
      and {1, 2} <= period_pts[2] and {-5, -7, -10} <= period_pts[3],
      "A5 整数周期点（周期 ≤ 12）恰为已知环：0、-1、{1,2}、{-5,-7,-10}、-17 环",
      f"意外点 {unexpected}")

# A6：有理周期点与非整数例子（定理 B 的例证）
def step_frac(x):
    return x / 2 if x.numerator % 2 == 0 else (3 * x + 1) / 2


examples = {}
x = Fraction(4, 5)
orb = []
for _ in range(3):
    orb.append(x)
    x = step_frac(x)
examples["4/5 的 3 圈"] = (orb, x == Fraction(4, 5))
x = Fraction(1, 3)
examples["1/3 一步到 1"] = ([x], step_frac(x) == 1)
x = Fraction(-1)
examples["-1 不动"] = ([x], step_frac(x) == x)
ok_frac = all(v[1] for v in examples.values())
for kk, (orb2, ok2) in examples.items():
    print(f"    {kk}: {orb2} 验证 {ok2}")
check(ok_frac, "A6 有理点：4/5 构成正有理 3 圈、1/3 一步到 1、-1 为不动点")
# 4/5 的奇偶词是 (0,0,1) 周期，故不是 (1,0) 交替 ⟹ 永不达 1（定理 B）
w45 = []
x = Fraction(4, 5)
for _ in range(3):
    w45.append(x.numerator % 2)
    x = step_frac(x)
check(tuple(w45) == (0, 0, 1), "A6b 4/5 的奇偶词周期为 (0,0,1)（非 (1,0) 交替）")

# ------------------------------------------------------------------ F 段
print()
print("=" * 78)
print("F 段：有限商上的截断（不存在自映射）")
print("=" * 78)
bad_q = 0
for s in range(1, 9):
    for a in range(0, 1 << (s + 1)):
        b = a + (1 << (s + 1))
        if (T_int(a) - T_int(b)) % (1 << s) != 0:
            bad_q += 1
check(bad_q == 0, "F1 T 诱导良定义的 Z/2^{s+1} → Z/2^s（s ≤ 8）", f"失败 {bad_q}")
# 不是 Z/2^s → Z/2^s：最小反例对
first_bad = None
for s in range(1, 9):
    for a in range(1 << s):
        b = a + (1 << s)
        if (T_int(a) - T_int(b)) % (1 << s) != 0:
            first_bad = (s, a, b, T_int(a), T_int(b))
            break
    if first_bad:
        break
print(f"    Z/2^s → Z/2^s 失败的最小反例：s={first_bad[0]}，{first_bad[1]} 与 {first_bad[2]} 同类"
      f"，但像 {first_bad[3]} 与 {first_bad[4]} 不同类")
check(first_bad is not None, "F2 T 不诱导 Z/2^s 上的自映射（存在同类不同像）")

# ------------------------------------------------------------------ B 段
print()
print("=" * 78)
print("B 段：残类二分定理（定理 D）")
print("=" * 78)


def prefix_ascending_flags(word):
    """返回列表 flags[i] = (3^{m_i} >= 2^i)，i = 1..len(word)"""
    flags = []
    c = 0
    m = 0
    for j, b in enumerate(word):
        if b:
            c = 3 * c + (1 << j)
            m += 1
        flags.append(3 ** m >= (1 << (j + 1)))
    return flags


# B1：全上升词计数 N_a
def count_ascending_dp(a):
    dp = {(0, 0): 1}
    for L in range(1, a + 1):
        nd = defaultdict(int)
        for (l, m), cnt in dp.items():
            for b in (0, 1):
                if 3 ** (m + b) >= (1 << L):
                    nd[(L, m + b)] += cnt
        dp = nd
    return sum(dp.values())


bad_cnt = 0
Na = {}
for a in range(1, 25):
    d = count_ascending_dp(a)
    Na[a] = d
    if a <= 16:
        brute = sum(1 for w in range(1 << a)
                    if all(prefix_ascending_flags(tuple((w >> i) & 1 for i in range(a)))))
        if brute != d:
            bad_cnt += 1
check(bad_cnt == 0, "B1 全上升词计数 N_a：DP 与暴力一致（a ≤ 16）")
print("    N_a（a = 1..24）：", [Na[a] for a in range(1, 25)])
print(f"    对照：全词数 2^a，比例 N_a/2^a（a = 4,8,12,16,20,24）："
      f"{[round(Na[a] / (1 << a), 5) for a in (4, 8, 12, 16, 20, 24)]}")

# 词 <-> 类代表元（1..2^k）的对照表
def word_rep_map(k):
    """返回 {word: rep}，rep ∈ [1, 2^k]，rep 的类 mod 2^k 的奇偶词就是 word"""
    d = {}
    for x in range(1, (1 << k) + 1):
        d[word_int(x, k)] = x
    return d


# B2：坏类的见证族：整类成员 σ > k（见证取类内最小 ≥ 2 的成员；n = 1 单独排除）
kmaps = {k: word_rep_map(k) for k in range(1, 15)}
bad_witness = 0
witness_tested = 0
degenerate = []
for a in range(1, 7):
    for r in range(1 << a):
        word = word_int(r if r else (1 << a), a)
        flags = prefix_ascending_flags(word)
        if not all(flags):
            continue
        for k in range(a, a + 9):
            wk = word + (1,) * (k - a)
            rep = kmaps[k][wk]
            n = rep if rep >= 2 else rep + (1 << k)
            if rep < 2:
                degenerate.append((a, r, k, rep))
            witness_tested += 1
            if n % (1 << a) != (r % (1 << a)):
                bad_witness += 1
                continue
            y = n
            okk = True
            for _ in range(k):
                y = T_int(y)
                if y < n:
                    okk = False
                    break
            if not okk:
                bad_witness += 1
check(bad_witness == 0, "B2 全上升类的见证族：整类成员在 k 步内都不下降",
      f"检查 {witness_tested} 个（a ≤ 6，k ≤ a+8），失败 {bad_witness}")
print(f"    其中类内最小成员为 1 的退化情形（改用类内次小成员 {2}^k + 1）：{degenerate}")

# B3：σ 数组与逐类最大值
LIM = 1 << 20
print("    正在计算 n ≤ 2^20 的首降时间数组……")
sigma = [0] * (LIM + 1)
for n in range(2, LIM + 1):
    v = n
    d = 0
    while v >= n:
        v = (v >> 1) if (v & 1) == 0 else ((3 * v + 1) >> 1)
        d += 1
    sigma[n] = d
print("    完成。")

LIMITS = (1 << 16, 1 << 18, 1 << 20)
bad_class = 0
rows = []
for a in range(1, 7):
    Amod = 1 << a
    mx = {lim: [0] * Amod for lim in LIMITS}
    for lim in LIMITS:
        arr = mx[lim]
        for n in range(2, min(lim, LIM) + 1):
            c = n & (Amod - 1)
            if sigma[n] > arr[c]:
                arr[c] = sigma[n]
    for r in range(Amod):
        word = word_int(r if r else Amod, a)
        flags = prefix_ascending_flags(word)
        pred_bad = all(flags)
        m16, m18, m20 = (mx[LIMITS[0]][r], mx[LIMITS[1]][r], mx[LIMITS[2]][r])
        rows.append((a, r, pred_bad, m16, m18, m20))
        if not pred_bad:
            if not (m16 == m18 == m20):
                bad_class += 1
                if bad_class <= 5:
                    print("    有界类不稳：", a, r, m16, m18, m20)
        else:
            if not (mx[LIMITS[1]][r] > mx[LIMITS[0]][r] or mx[LIMITS[2]][r] > mx[LIMITS[1]][r]):
                bad_class += 1
                if bad_class <= 5:
                    print("    无界类未见增长：", a, r, m16, m18, m20)
check(bad_class == 0, "B3 残类二分（数值）：有界类截断稳定，无界类随截断增长")
print("    无界类（全上升词）的逐类最大 σ（a, r, 词, 2^16, 2^18, 2^20）：")
for (a, r, pb, m16, m18, m20) in rows:
    if pb:
        print(f"      a={a} r={r} 词={word_int(r if r else (1 << a), a)} {m16} {m18} {m20}")
mxb = max((row[5] for row in rows if not row[2]), default=0)
print(f"    有界类的最大 σ（2^20 截断）的上确界 = {mxb}")
print(f"    无界类个数 / 总类数（a = 1..6）："
      f"{[(sum(1 for x in rows if x[0] == a and x[2]), 1 << a) for a in range(1, 7)]}")

# B4：非下降集的精确结构 {n : σ(n) > k} = ⊔_w {n ≡ a_w (mod 2^k), n ≤ Θ_w}
bad_struct = 0
checked_struct = 0
for k in range(1, 9):
    kmap = word_rep_map(k)
    theta_by_rep = {}
    for word, rep in kmap.items():
        best = None
        cc = 0
        mm = 0
        for j, b in enumerate(word):
            if b:
                cc = 3 * cc + (1 << j)
                mm += 1
            i = j + 1
            if 3 ** mm < (1 << i):
                num, den = cc, (1 << i) - 3 ** mm
                if best is None or num * best[1] < best[0] * den:
                    best = (num, den)
        theta_by_rep[rep] = best
    Amod = 1 << k
    for n in range(2, (1 << 16) + 1):
        rep = n & (Amod - 1)
        if rep == 0:
            rep = Amod
        best = theta_by_rep[rep]
        # 无下降前缀 ⟹ Θ_w = ∞ ⟹ 非下降（pred = True）
        pred = True if best is None else (n * best[1] <= best[0])
        actual = sigma[n] > k
        checked_struct += 1
        if pred != actual:
            bad_struct += 1
            if bad_struct <= 3:
                print("    结构反例：", n, k, pred, actual)
check(bad_struct == 0, "B4 非下降集精确结构（词 + 阈值）",
      f"检查 {checked_struct} 组，不符 {bad_struct}（k ≤ 8，n ≤ 2^16）")

# B4b：同一结构的更深检查（k ≤ 14）
bad_struct2 = 0
checked2 = 0
for k in range(9, 15):
    kmap = word_rep_map(k)
    theta_by_rep = {}
    for word, rep in kmap.items():
        best = None
        cc = 0
        mm = 0
        for j, b in enumerate(word):
            if b:
                cc = 3 * cc + (1 << j)
                mm += 1
            i = j + 1
            if 3 ** mm < (1 << i):
                num, den = cc, (1 << i) - 3 ** mm
                if best is None or num * best[1] < best[0] * den:
                    best = (num, den)
        theta_by_rep[rep] = best
    Amod = 1 << k
    for n in range(2, (1 << 16) + 1):
        rep = n & (Amod - 1)
        if rep == 0:
            rep = Amod
        best = theta_by_rep[rep]
        pred = True if best is None else (n * best[1] <= best[0])
        actual = sigma[n] > k
        checked2 += 1
        if pred != actual:
            bad_struct2 += 1
check(bad_struct2 == 0, "B4b 同一结构（k = 9..14）", f"检查 {checked2} 组，不符 {bad_struct2}")

# B5b：D_k 的密度与 ⋃_{k≤K} D_k 的覆盖（n ∈ D_k ⟺ σ(n) ≤ k）
print("    D_k 的字面密度 #{w : 3^{m(w)} < 2^k}/2^k（k ≤ 24）：")
dens = []
for k in range(1, 25):
    cnt = sum(1 for w in range(1 << k)
              if 3 ** sum((w >> i) & 1 for i in range(k)) < (1 << k))
    dens.append(cnt / (1 << k))
print("    ", [round(x, 6) for x in dens])
print("    ⋃_{k≤K} D_k 在 [2, 2^20] 上的覆盖（K = 1,2,3,5,10,15,20,25）：")
cov = []
for K in (1, 2, 3, 5, 10, 15, 20, 25):
    c = sum(1 for n in range(2, LIM + 1) if sigma[n] <= K)
    cov.append((K, c, round(c / (LIM - 1), 6)))
print("    ", cov)
print(f"    未被 ⋃_{{k≤25}} D_k 覆盖的 n ≤ 2^20 个数："
      f"{sum(1 for n in range(2, LIM + 1) if sigma[n] > 25)}")

# B5：阈值最大值与 2^k - 3^m 的丢番图联系
print("    θ 最大值表（k, 取得最大的词中 1 的个数 m, 2^k−3^m, θ）：")
theta_rows = []
for k in range(1, 19):
    best = None
    bestinfo = None
    for w in range(1 << k):
        c, m = c_of_word(tuple((w >> i) & 1 for i in range(k)))
        D = (1 << k) - 3 ** m
        if D <= 0:
            continue
        if best is None or c * best[1] > best[0] * D:
            best = (c, D)
            bestinfo = (m, D)
    if best:
        theta_rows.append((k, bestinfo[0], bestinfo[1], best[0], best[1]))
        print(f"      k={k:2d} m={bestinfo[0]:2d} 2^k−3^m={bestinfo[1]:<8d} θ={best[0]}/{best[1]}"
              f" ≈ {best[0] / best[1]:.4f}")
# 最小正差 2^k - 3^m（精确整数）
print("    最小正差 2^k − 3^m（精确整数，k ≤ 40）：")
gaps = []
for k in range(2, 41):
    bestm = None
    for m in range(0, k):
        D = (1 << k) - 3 ** m
        if D > 0 and (bestm is None or D < bestm[1]):
            bestm = (m, D)
    gaps.append((k, bestm[0], bestm[1]))
for (k, m, D) in gaps:
    if D <= 1000 or k in (8, 19, 20, 30, 40):
        print(f"      k={k:2d} m={m:2d} 2^k−3^m={D}")

# 「首次下降类」的阈值最大表（对照 parity-vectors 实验报告的最大阈值）
print("    首次下降类（所有真前缀上升、整词下降）的阈值最大值：")
first_desc_rows = []
for k in range(2, 19):
    best = None
    bestinfo = None
    for w in range(1 << k):
        word = tuple((w >> i) & 1 for i in range(k))
        flags = prefix_ascending_flags(word)
        if not all(flags[:-1]) or flags[-1]:
            continue
        c, m = c_of_word(word)
        D = (1 << k) - 3 ** m
        if D <= 0:
            continue
        if best is None or c * best[1] > best[0] * D:
            best = (c, D)
            bestinfo = (m, D, word)
    if best:
        first_desc_rows.append((k, bestinfo[0], bestinfo[1], best[0] / best[1], bestinfo[2]))
        print(f"      k={k:2d} m={bestinfo[0]:2d} 2^k−3^m={bestinfo[1]:<6d} θ={best[0]}/{best[1]}"
              f" ≈ {best[0] / best[1]:.4f} 词={bestinfo[2]}")
fd_best = max(first_desc_rows, key=lambda t: t[3])
print(f"    首次下降类阈值的全局最大：k={fd_best[0]}，θ ≈ {fd_best[3]:.4f}"
      f"（对照 parity-vectors 实验报告的 k = 8、24.5385）")

# 连分数（精确整数、中项法）求 log_2 3 的收敛分数
lo = (1, 1)   # 2^1 = 2 < 3 = 3^1
hi = (2, 1)   # 2^2 = 4 > 3 = 3^1
convs = []
for _ in range(14):
    k = lo[0] + hi[0]
    m = lo[1] + hi[1]
    if (1 << k) > 3 ** m:
        hi = (k, m)
    else:
        lo = (k, m)
    convs.append((k, m, (1 << k) - 3 ** m))
print("    log_2 3 的中项法收敛分数 (k, m, 2^k − 3^m)（k ≤ 60 才列出）：")
for (k, m, D) in convs:
    if k <= 60:
        print(f"      ({k}, {m}, {D})")

# ------------------------------------------------------------------ E 段
print()
print("=" * 78)
print("E 段：显式下降判据（证书引理）")
print("=" * 78)

# E1：c 的上界 c_w ≤ 2^{k-m}(3^m - 2^m)
bad_bound = 0
for k in range(1, 17):
    for w in range(1 << k):
        c, m = c_of_word(tuple((w >> i) & 1 for i in range(k)))
        if m == 0:
            continue
        if c > (1 << (k - m)) * (3 ** m - 2 ** m):
            bad_bound += 1
check(bad_bound == 0, "E1 c_w ≤ 2^{k−m}(3^m − 2^m)", f"k ≤ 16 全部词，越界 {bad_bound}")

# E2：判据「2^k > 3^m 且 n ≥ ⌈2^{k-m}(3^m-2^m)/(2^k-3^m)⌉ ⟹ T^k(n) < n」
bad_crit = 0
tested_crit = 0
for k in range(1, 15):
    kmap = word_rep_map(k)
    for word, rep in kmap.items():
        c, m = c_of_word(word)
        D = (1 << k) - 3 ** m
        if D <= 0 or m == 0:
            continue
        num = (1 << (k - m)) * (3 ** m - 2 ** m)
        thr = num // D + 1  # 最小的 > num/D 的整数（判据是严格不等式 n > θ）
        n = rep if rep >= thr else rep + (1 << k) * ((thr - rep) // (1 << k) + 1)
        if n > LIM:
            continue
        tested_crit += 1
        y = n
        for _ in range(k):
            y = T_int(y)
        if y >= n:
            bad_crit += 1
            if bad_crit <= 3:
                print("    判据反例：", k, word, n, y)
check(bad_crit == 0, "E2 显式下降判据（词阈值上界，严格不等式）",
      f"检查 {tested_crit} 组（k ≤ 14，n ≤ 2^20），失败 {bad_crit}")

# E3：特例 3^m·2 ≤ 2^k ⟹ n ≥ 2(3/2)^m 时 T^k(n) < n
bad_e3 = 0
tested_e3 = 0
for k in range(1, 15):
    kmap = word_rep_map(k)
    for word, rep in kmap.items():
        c, m = c_of_word(word)
        if 3 ** m * 2 > (1 << k) or m == 0:
            continue
        # 阈值：最小的 > 2(3/2)^m 的整数
        thr = (2 * 3 ** m + (1 << m) - 1) >> m
        if (2 * 3 ** m) % (1 << m) == 0:
            thr += 1
        n = rep if rep >= thr else rep + (1 << k) * ((thr - rep) // (1 << k) + 1)
        if n > LIM:
            continue
        tested_e3 += 1
        y = n
        for _ in range(k):
            y = T_int(y)
        if y >= n:
            bad_e3 += 1
check(bad_e3 == 0, "E3 特例：3^m·2 ≤ 2^k 与 n > 2(3/2)^m ⟹ T^k(n) < n",
      f"检查 {tested_e3} 组，失败 {bad_e3}")

# E4：θ_w < 3^{len(w)}（用于把 (S3)3 的例外集压进已验证范围）
bad_e4 = 0
tested_e4 = 0
for k in range(1, 17):
    for w in range(1 << k):
        word = tuple((w >> i) & 1 for i in range(k))
        c, m = c_of_word(word)
        D = (1 << k) - 3 ** m
        if D <= 0:
            continue
        tested_e4 += 1
        if not (c < 3 ** k):
            bad_e4 += 1
check(bad_e4 == 0, "E4 θ_w = c/(2^k−3^m) < 3^k（k ≤ 16 全部下降词）",
      f"检查 {tested_e4} 个，失败 {bad_e4}")
print("    3^44 < 2^71 < 3^45：", 3 ** 44 < 2 ** 71 < 3 ** 45,
      f"（3^44 = {3**44}，2^71 = {2**71}）")


# ------------------------------------------------------------------ G 段
print()
print("=" * 78)
print("G 段：首次下降类阈值的动态规划与显式见证（本轮修订新增）")
print("=" * 78)


def fd_best_dp(k):
    """首次下降词（所有真前缀上升、整词下降）中 θ = c/D 的最大者。
    DP 状态 (长度, 1 的个数) -> 最大 c；约束 3^{m_j} >= 2^j 只依赖 (j, m_j)，故 DP 有效。"""
    dp = {0: (0, [])}
    for i in range(0, k - 1):
        nd = {}
        for m, (c, w) in dp.items():
            if 3 ** m >= (1 << (i + 1)) and (m not in nd or nd[m][0] < c):
                nd[m] = (c, w + [0])
            if 3 ** (m + 1) >= (1 << (i + 1)) and (m + 1 not in nd or nd[m + 1][0] < 3 * c + (1 << i)):
                nd[m + 1] = (3 * c + (1 << i), w + [1])
        dp = nd
    best = None
    for m, (c, w) in dp.items():
        for b in (0, 1):
            m2 = m + b
            D = (1 << k) - 3 ** m2
            if D <= 0:
                continue
            c2 = c if b == 0 else 3 * c + (1 << (k - 1))
            if best is None or c2 * best[1] > best[0] * D:
                best = (c2, D, w + [b], m2)
    return best


def fd_brute(k):
    best = None
    for w in range(1 << k):
        word = tuple((w >> i) & 1 for i in range(k))
        flags = prefix_ascending_flags(word)
        if not all(flags[:-1]) or flags[-1]:
            continue
        c, m = c_of_word(word)
        D = (1 << k) - 3 ** m
        if D <= 0:
            continue
        if best is None or c * best[1] > best[0] * D:
            best = (c, D, list(word), m)
    return best


bad_dp = 0
for k in range(2, 15):
    a1 = fd_best_dp(k)
    a2 = fd_brute(k)
    if (a1 is None) != (a2 is None):
        bad_dp += 1
        continue
    if a1 is not None and a1[0] * a2[1] != a2[0] * a1[1]:
        bad_dp += 1
        print("    DP 与暴力不符：", k)
check(bad_dp == 0, "G1 首次下降阈值的 DP 与暴力一致（k ≤ 14）")
b8 = fd_best_dp(8)
b16 = fd_best_dp(16)
check(b8[0] * 13 == 319 * b8[1] and b16[0] * 6487 == 148813 * b16[1],
      "G1b DP 复现 k = 8 的 319/13 与 k = 16 的 148813/6487")


def rep_of_word(word):
    """逐位构造类代表元 a ∈ [1, 2^k]：第 j 步两个提升的 T^j 奇偶相反，故唯一确定。"""
    k = len(word)
    a = 1 if word[0] == 1 else 2
    for j in range(1, k):
        x, y = a, a + (1 << j)
        for _ in range(j - 1):
            x = T_int(x)
            y = T_int(y)
        px = T_int(x) & 1
        py = T_int(y) & 1
        if px != word[j] and py == word[j]:
            a = a + (1 << j)
    return a


# G2：k = 65 的显式见证（本轮修订新增，用于回应反驳方给出的 k = 65 数据点）
K65 = 65
c65, D65, w65, m65 = fd_best_dp(K65)
rep65 = rep_of_word(w65)
cc = 0
mm = 0
okpre = True
for j, b in enumerate(w65):
    if b:
        cc = 3 * cc + (1 << j)
        mm += 1
    if j + 1 <= K65 - 1 and 3 ** mm < (1 << (j + 1)):
        okpre = False
x = rep65
ww = []
for _ in range(K65):
    ww.append(x & 1)
    x = T_int(x)
n65 = rep65
while n65 * D65 <= c65:
    n65 += (1 << K65)
y = n65
first = None
for i in range(1, K65 + 1):
    y = T_int(y)
    if y < n65 and first is None:
        first = i
check(cc == c65 and mm == m65 and tuple(ww) == tuple(w65) and okpre
      and 3 ** m65 < (1 << K65) and first == K65 and y < n65,
      "G2 k = 65 的显式见证：词、类代表元、真前缀全上升、整词下降、首次下降恰在 65 步",
      f"c={c65} m={m65} D={D65} θ≈{c65 / D65:.4f} 类代表元={rep65} 见证 n={n65}")
print(f"    k = 65 的词（65 位）：{''.join(map(str, w65))}")
print(f"    θ = {c65}/{D65} ≈ {c65 / D65:.4f}"
      f"（反驳方报 k = 65 为 467.10，与此不符；本值附显式见证，见上行）")

# ------------------------------------------------------------------ C 段
print()
print("=" * 78)
print("C 段：n 一致证书的不存在（显式见证）")
print("=" * 78)

bad_c = 0
tested_c = 0
for k in range(1, 9):
    for d in range(1, 25):
        # 见证：n ≡ 2^k − 1 (mod 2^k)，取 n = 2^{k+j} − 1，j 使 k+j >= d
        j = max(0, d - k)
        n = (1 << (k + j)) - 1
        tested_c += 1
        if n % (1 << k) != ((1 << k) - 1) % (1 << k):
            bad_c += 1
            continue
        y = n
        for _ in range(d):
            y = T_int(y)
        if y < n:
            bad_c += 1
check(bad_c == 0, "C1 对每个 (k, d)，类 2^k−1 中存在 n 使 T^d(n) ≥ n",
      f"检查 {tested_c} 组，失败 {bad_c}（k ≤ 8，d ≤ 24）")

# ------------------------------------------------------------------ D 段
print()
print("=" * 78)
print("D 段：对照与记录")
print("=" * 78)

# D1：5x+1 的同一计数（说明 N_a 的数值依赖常数 3）
def count_ascending_general(a, base):
    dp = {(0, 0): 1}
    for L in range(1, a + 1):
        nd = defaultdict(int)
        for (l, m), cnt in dp.items():
            for b in (0, 1):
                if base ** (m + b) >= (1 << L):
                    nd[(L, m + b)] += cnt
        dp = nd
    return sum(dp.values())


print("    N_a(3x+1) 与 N_a(5x+1) 对照（a = 1..16）：")
print("     3x+1:", [count_ascending_general(a, 3) for a in range(1, 17)])
print("     5x+1:", [count_ascending_general(a, 5) for a in range(1, 17)])

# D2：首降时间记录
mx = 0
arg = 0
for n in range(2, LIM + 1):
    if sigma[n] > mx:
        mx = sigma[n]
        arg = n
print(f"    n ≤ 2^20 内最大首降时间 σ = {mx}，最小见证 n = {arg}")
blocks = []
for j in range(1, 21):
    m = 0
    for n in range(1 << j, min(1 << (j + 1), LIM + 1)):
        if sigma[n] > m:
            m = sigma[n]
    blocks.append(m)
print("    逐二进块 [2^j, 2^{j+1}) 的最大 σ：")
print("     ", blocks)
print("    最大总停时 τ（到 1 的加速步数）对照：记忆化计算")
cache_tau = {}
tau_max = 0
tau_arg = 0
for n0 in range(2, LIM + 1):
    stack = []
    v = n0
    while v != 1 and v not in cache_tau:
        stack.append(v)
        v = T_int(v)
    base = 0 if v == 1 else cache_tau[v]
    for x in reversed(stack):
        base += 1
        cache_tau[x] = base
    d = cache_tau[n0]
    if d > tau_max:
        tau_max = d
        tau_arg = n0
print(f"    n ≤ 2^20 内最大总停时 τ = {tau_max}，最小见证 n = {tau_arg}"
      f"（对照第一轮实验的直接计算：329，见证 837799）")

print()
print("=" * 78)
print(f"全部检查完成；失败断言数 = {FAIL}")
print("=" * 78)
sys.exit(1 if FAIL else 0)
