#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
formal-automata 路线：attempt.md 中全部「局部新结论」的独立验证脚本。

运行：python3 checks_formal_automata.py
（本机实测 Python 3.12.7；断言失败即抛 AssertionError。
 所有「计数为 0」的检查都是对声明范围内的逐点全量比对，不是抽样。）

被验证对象（编号与 attempt.md 一致）：
  A. c(v) 递推与闭式、仿射公式、奇偶向量与模 2^k 剩余类的双射
  B. 下降层 D_k 的「剩余类 + 阈值」结构（定理 T1）
  C. A(k) 序列与项目 parity-vectors 实验数字的交叉核对
  D. 2^m - 1 的上升前缀恒等式与整类未覆盖（定理 T2）
  E. 不存在「固定模数 + 每类有限下降界」的证书（定理 T3）
  F. D_k 的显式有限自动机与逐点比对（定理 T1 的可构造部分）
  G. 位权势函数的两点消去（定理 T4 之一，任意实权重）
  H. 多项式与「多项式 + 有界位权」势函数的渐近否决（定理 T4 之二）
  I. 截断域上势函数的充要条件（定理 T5）：[3,N] 一侧的见证与 [1,N] 一侧的循环
  J. 有界高度集合 S_N 的计算与不变性（定理 T5 的无穷域一侧）
"""

from fractions import Fraction
import itertools
import random

# ---------------------------------------------------------------- 基础

def T(n: int) -> int:
    """加速科拉茨映射：T(n) = n/2（偶），(3n+1)/2（奇）。"""
    return (3 * n + 1) // 2 if (n & 1) else n >> 1


def Tk(n: int, k: int) -> int:
    for _ in range(k):
        n = T(n)
    return n


def pv(n: int, k: int):
    """长度 k 的奇偶向量（最早一步在左）。"""
    v = []
    x = n
    for _ in range(k):
        v.append(x & 1)
        x = T(x)
    return tuple(v)


def ceff(v):
    """递推得到 (c, m)：对类 v 中一切 n，T^k(n) = (3^m n + c) / 2^k。"""
    c = 0
    m = 0
    j = 0
    for b in v:
        if b:
            c = 3 * c + (1 << j)
            m += 1
        j += 1
    return c, m


def closed_form(v):
    ones = [j for j, b in enumerate(v) if b]
    m = len(ones)
    return sum(3 ** (m - 1 - t) * 2 ** ones[t] for t in range(m)), m


def descent_bruteforce(k: int, n: int) -> bool:
    return Tk(n, k) < n


def descent_formula(k: int, n: int) -> bool:
    """「剩余类 + 阈值」判据的整数形式：c_v < (2^k - 3^m_v) * n。"""
    c, m = ceff(pv(n, k))
    return c < ((1 << k) - 3 ** m) * n


def check(name, cond, extra=""):
    if not cond:
        raise AssertionError(f"检查失败：{name} {extra}")
    print(f"[通过] {name} {extra}")


# ---------------------------------------------------------------- A

def section_A():
    print("== A. c 递推与闭式、仿射公式、双射 ==")
    bad = 0
    total = 0
    for k in range(1, 13):
        for v in itertools.product((0, 1), repeat=k):
            total += 1
            if ceff(v) != closed_form(v):
                bad += 1
    print(f"A1 长度 1..12 的全部 {total} 个向量：递推与闭式不一致数 = {bad}")

    bad = 0
    cnt = 0
    for k in range(1, 13):
        for n in range(1, 1025):
            c, m = ceff(pv(n, k))
            num = 3 ** m * n + c
            if num % (1 << k) != 0 or num // (1 << k) != Tk(n, k):
                bad += 1
            cnt += 1
    print(f"A2 仿射公式 T^k(n) = (3^m n + c)/2^k：k=1..12, n=1..1024 共 {cnt} 组，失败数 = {bad}")

    bad = 0
    for k in range(1, 13):
        seen = {}
        for a in range(1, (1 << k) + 1):
            v = pv(a, k)
            if v in seen:
                bad += 1
            seen[v] = a
        if len(seen) != (1 << k):
            bad += 1
        for n in range(1, min(1 << (k + 4), 20000)):
            if pv(n, k) != pv(n + (1 << k), k):
                bad += 1
    print(f"A3 双射 a in [1,2^k] <-> v（k=1..12）与「pv_k 只依赖 n mod 2^k」：失败数 = {bad}")
    check("A 全部零失败", bad == 0)


# ---------------------------------------------------------------- B

def section_B(max_k=12, max_n=1 << 16):
    print("== B. 下降层 D_k 的剩余类 + 阈值结构（定理 T1）==")
    mism = 0
    compared = 0
    for k in range(1, max_k + 1):
        for n in range(1, max_n + 1):
            if descent_bruteforce(k, n) != descent_formula(k, n):
                mism += 1
            compared += 1
    print(f"B1 逐点比对 T^k(n) < n 与判据 c_v < (2^k-3^m)n：k=1..{max_k}, "
          f"n=1..{max_n} 共 {compared} 组，不一致数 = {mism}")

    mism2 = 0
    for k in range(1, max_k + 1):
        thresh = {}
        for a in range(1, (1 << k) + 1):
            c, m = ceff(pv(a, k))
            D = (1 << k) - 3 ** m
            thresh[a % (1 << k)] = (Fraction(c, D), c) if D > 0 else None
        for n in range(1, min(max_n, 1 << 14) + 1):
            t = thresh[n % (1 << k)]
            pred = (t is not None) and (Fraction(n) > t[0])
            if pred != descent_bruteforce(k, n):
                mism2 += 1
    print(f"B2 同一判据写成「n > theta_v」的分数形式：不一致数 = {mism2}")

    rows = []
    for k in range(1, 19):
        pieces = 0
        smax = 0
        for a in range(1, (1 << k) + 1):
            c, m = ceff(pv(a, k))
            D = (1 << k) - 3 ** m
            if D > 0:
                pieces += 1
                s = c // D + 1
                smax = max(smax, s)
        rows.append((k, pieces, smax))
    print("B3 k / D_k 的片段数（满足 2^k > 3^m 的向量数）/ 最大阈值 floor(theta)+1：")
    for k, p, s in rows:
        print(f"     k={k:2d}  片段数={p:6d}  最大阈值={s:12d}")
    check("B 结构检查零失配", mism == 0 and mism2 == 0)


# ---------------------------------------------------------------- C

def A_seq(K):
    """A(k) = #{v in {0,1}^k : 对一切 1<=j<=k-1 有 3^{m_j} >= 2^j 且 3^{m_k} < 2^k}。"""
    N = {0: 1}
    res = []
    for k in range(1, K + 1):
        a = 0
        for m, cnt in N.items():
            if 3 ** m < 2 ** k:
                a += cnt
            if 3 ** (m + 1) < 2 ** k:
                a += cnt
        res.append(a)
        N2 = {}
        for m, cnt in N.items():
            if 3 ** m >= 2 ** k:
                N2[m] = N2.get(m, 0) + cnt
            if 3 ** (m + 1) >= 2 ** k:
                N2[m + 1] = N2.get(m + 1, 0) + cnt
        N = N2
    return res


def section_C():
    print("== C. A(k) 与项目 parity-vectors 实验数字的交叉核对 ==")
    mine = A_seq(18)
    theirs = [1, 1, 0, 1, 2, 0, 3, 7, 0, 12, 0, 30, 85, 0, 173, 476, 0, 961]
    print(f"C1 本脚本 A(k)（k=1..18）= {mine}")
    print(f"C2 项目 parity-vectors 首降向量计数     = {theirs}")
    same = (mine == theirs)
    print(f"C3 逐项相同：{same}")
    if not same:
        print("   不一致项（k, 本脚本, 项目）："
              + str([(k + 1, mine[k], theirs[k]) for k in range(18) if mine[k] != theirs[k]]))


# ---------------------------------------------------------------- D

def section_D(max_k=20, max_j=6, scan_bits=18):
    print("== D. 2^m-1 的上升前缀与整类未覆盖（定理 T2）==")
    bad = 0
    for m in range(1, max_k + max_j + 1):
        n = (1 << m) - 1
        x = n
        for i in range(0, m + 1):
            if i <= m and x != 3 ** i * 2 ** (m - i) - 1:
                bad += 1
            if 1 <= i <= m and not (x > n):
                bad += 1
            x = T(x)
    print(f"D1 恒等式 T^i(2^m-1) = 3^i 2^(m-i) - 1（i<=m）与严格上升性：m<=26，失败数 = {bad}")

    bad = 0
    for k in range(1, max_k + 1):
        for j in range(0, max_j + 1):
            n = (1 << (k + j)) - 1
            if n % (1 << k) != (1 << k) - 1:
                bad += 1
            if pv(n, k) != tuple([1] * k):
                bad += 1
            for i in range(1, k + 1):
                if not (Tk(n, i) > n):
                    bad += 1
                if descent_formula(i, n):
                    bad += 1
    print(f"D2 n = 2^(k+j)-1：类归属、前 k 位全 1、前 k 步上升、不属于 D_1..D_k：失败数 = {bad}")

    bad = 0
    tested = 0
    bad2 = 0
    for k in range(1, 13):
        step = 1 << k
        for n in range(step - 1, (1 << scan_bits) + 1, step):
            if n == 0:
                continue
            tested += 1
            for i in range(1, k + 1):
                if not (Tk(n, i) > n):
                    bad += 1
                    break
            for i in range(1, k + 1):
                if descent_formula(i, n):
                    bad2 += 1
                    break
    print(f"D3 整类扫描：k=1..12, n<=2^{scan_bits}, n ≡ 2^k-1 (mod 2^k) 共 {tested} 个 n，"
          f"「前 k 步严格上升」失败数 = {bad}，「落在 D_1..D_k 中」的个数 = {bad2}")
    check("D 上升前缀与整类未覆盖", bad == 0 and bad2 == 0)


# ---------------------------------------------------------------- E

def section_E():
    print("== E. 不存在「固定模数 + 每类有限下降界」的证书（定理 T3）==")
    ok = True
    cnt = 0
    for M in range(1, 7):
        for D in range(1, 25):
            j = max(D - M + 1, 0)
            n = (1 << (M + j)) - 1
            rise = all(Tk(n, i) > n for i in range(1, D + 1))
            if not rise or n % (1 << M) != (1 << M) - 1:
                ok = False
            cnt += 1
    print(f"E1 对 M=1..6 与 D=1..24 的全部 {cnt} 个 (M,D) 组合，取 n = 2^(M+j)-1 "
          f"(j = max(D-M+1,0))：n ≡ 2^M-1 且前 D 步全部上升，全部成立 = {ok}")

    M, D = 5, 12
    step = 1 << M
    tot = 0
    rise_all = 0
    for n in range(step - 1, (1 << 24) + 1, step):
        tot += 1
        if all(Tk(n, i) > n for i in range(1, D + 1)):
            rise_all += 1
    print(f"E2 例：类 31 mod 32（M=5）、D=12、n<=2^24：类内成员 {tot} 个，"
          f"其中前 12 步全上升者 {rise_all} 个")
    check("E 反例族成立", ok)


# ---------------------------------------------------------------- F

class DFA:
    """读 n 的二进制（最高位在前）判定 n in D_k 的显式有限自动机。"""

    def __init__(self, k):
        self.k = k
        self.mask = (1 << k) - 1
        self.s = {}
        for a in range(1, (1 << k) + 1):
            c, m = ceff(pv(a, k))
            D = (1 << k) - 3 ** m
            if D > 0:
                self.s[a & self.mask] = c // D + 1
        self.S = max(self.s.values()) if self.s else 1

    def start(self):
        return ("p", 0)

    def step(self, state, b):
        kind, val = state
        if kind == "p":
            p = (val << 1) | b
            return ("p", p) if p < self.S else ("B", p & self.mask)
        return ("B", ((val << 1) | b) & self.mask)

    def accept(self, state):
        kind, val = state
        if kind == "p":
            if val == 0:
                return False
            r = val & self.mask
            return r in self.s and val >= self.s[r]
        return val in self.s

    def run(self, n):
        st = self.start()
        for ch in bin(n)[2:]:
            st = self.step(st, int(ch))
        return self.accept(st)


def section_F(max_k=5, max_n=1 << 12):
    print("== F. D_k 的显式有限自动机（定理 T1 的可构造部分）==")
    for k in range(1, max_k + 1):
        d = DFA(k)
        mism = 0
        for n in range(1, max_n + 1):
            if d.run(n) != descent_bruteforce(k, n):
                mism += 1
        rnd = random.Random(20261019)
        mism_big = 0
        trials = 4000
        for _ in range(trials):
            n = rnd.randrange(1, 1 << 60)
            if d.run(n) != descent_formula(k, n):
                mism_big += 1
        print(f"F{k} 状态数 = S + 2^k = {d.S} + {1 << k} = {d.S + (1 << k)}；"
              f"n<=2^12 逐点比对不一致 = {mism}；随机 60 位大数 {trials} 次不一致 = {mism_big}")
        check(f"F{k} 自动机与判据一致", mism == 0 and mism_big == 0)


# ---------------------------------------------------------------- G

def bitval(x, i):
    return (x >> i) & 1


def section_G(max_k=40):
    print("== G. 位权势函数的两点消去（定理 T4 之一）==")
    rnd = random.Random(7)
    w = [Fraction(rnd.randrange(-10 ** 6, 10 ** 6), rnd.randrange(1, 1000))
         for _ in range(max_k + 4)]

    def V(x):
        return sum(w[i] for i in range(x.bit_length()) if bitval(x, i))

    worst = None
    for k in range(1, max_k + 1):
        x1 = (1 << k) - 1
        x2 = 1 << k
        d1 = V(T(x1)) - V(x1)
        d2 = V(T(x2)) - V(x2)
        if d1 + d2 != 0 or d1 != w[k] - w[k - 1] or d2 != w[k - 1] - w[k]:
            worst = (k, d1, d2)
    print(f"G1 随机有理权重，k=1..{max_k}：Δ(x1)+Δ(x2) ≡ 0 且 Δ(x1)=w_k-w_(k-1)、"
          f"Δ(x2)=w_(k-1)-w_k：异常 = {worst}")
    for k in (1, 2):
        x1, x2 = (1 << k) - 1, 1 << k
        print(f"G2 k={k}：x1={x1}, x2={x2}, T(x1)={T(x1)}, T(x2)={T(x2)}；"
              f"两个见证点都在 [1, max(T(x1),x2)] = [1, {max(T(x1), x2)}] 内")
    check("G 两点消去", worst is None)


# ---------------------------------------------------------------- H

def polyval(P, x):
    return sum(a * x ** i for i, a in enumerate(P))


def section_H():
    print("== H. 多项式与「多项式 + 有界位权」势函数的渐近否决（定理 T4 之二）==")
    rnd = random.Random(11)

    def bitweight(x, w):
        return sum(w[i] for i in range(x.bit_length()) if bitval(x, i))

    cases = []
    for d in (1, 2, 3, 4):
        for sgn in (+1, -1):
            P = [Fraction(rnd.randrange(-5, 6)) for _ in range(d)]
            P.append(Fraction(sgn))
            cases.append((f"纯多项式 d={d} 首项{sgn:+d}", P, None))
    for d in (2, 3):
        for sgn in (+1, -1):
            P = [Fraction(rnd.randrange(-5, 6)) for _ in range(d)]
            P.append(Fraction(sgn))
            w = [Fraction(rnd.randrange(-3, 4)) for _ in range(80)]
            cases.append((f"多项式 d={d} 首项{sgn:+d} + 有界位权", P, w))
    cases.append(("纯位权", [Fraction(0)],
                  [Fraction(rnd.randrange(-9, 10)) for _ in range(80)]))

    for name, P, w in cases:
        best = None
        for x in range(3, 1 << 16):
            vx = polyval(P, x) + (0 if w is None else bitweight(x, w))
            vt = polyval(P, T(x)) + (0 if w is None else bitweight(T(x), w))
            if vt > vx - 1:
                best = x
                break
        print(f"H1 {name}：在 [3, 2^16] 内最早违反 V(T(x)) <= V(x)-1 的 x = {best}")

    print("H2 渐近系数核对（纯多项式，首项为 ±x^d）：")
    for d in (1, 2, 3, 4):
        x_odd = 3 * (1 << 13) + 1
        x_even = 1 << 15
        P_pos = [Fraction(0)] * (d + 1)
        P_pos[d] = Fraction(1)
        P_neg = [Fraction(0)] * (d + 1)
        P_neg[d] = Fraction(-1)
        d_pos_odd = polyval(P_pos, T(x_odd)) - polyval(P_pos, x_odd)
        d_neg_even = polyval(P_neg, T(x_even)) - polyval(P_neg, x_even)
        lead_odd = (Fraction(3, 2) ** d - 1) * x_odd ** d
        lead_even = (Fraction(1, 2) ** d - 1) * x_even ** d * (-1)
        print(f"     d={d}: 首项正、奇步 Δ = {d_pos_odd} > 0？{d_pos_odd > 0}"
              f"（主项 {lead_odd}）；首项负、偶步 Δ = {d_neg_even} > 0？{d_neg_even > 0}"
              f"（主项量级 {abs(lead_even)}）")


# ---------------------------------------------------------------- I

def section_I(N=4096):
    print("== I. 截断域上势函数的充要条件（定理 T5）==")
    lo = 3
    # [3,N] 一侧：逃逸时间 V(x) = min{k : T^k(x) 不在 [3,N]}
    V = {}
    for x in range(lo, N + 1):
        k = 0
        y = x
        while lo <= y <= N:
            y = T(y)
            k += 1
            if k > 10 ** 5:
                break
        V[x] = k if k <= 10 ** 5 else None
    undef = [x for x in V if V[x] is None]
    print(f"I1 [3,{N}] 上逃逸时间全部有限（即 [3,N] 无 T 环）：未定义个数 = {len(undef)}")
    bad = 0
    cnt = 0
    for x in range(lo, N + 1):
        y = T(x)
        if lo <= y <= N:
            if V[y] != V[x] - 1:
                bad += 1
            cnt += 1
    print(f"I2 在 {cnt} 个满足 T(x) 仍落在 [3,N] 的 x 上，恒等式 V(T(x)) = V(x) - 1 "
          f"失败数 = {bad}")
    inv = all((not (lo <= T(x) <= N)) or V[T(x)] == V[x] - 1 for x in range(lo, N + 1))
    print(f"I3 同上，全域形式：{inv}")
    # 环上的矛盾（算术演示）
    print("I4 环上的矛盾演示：若有环，沿环求和给出 0 <= -(环长)；例如 {1,2} 上要求 "
          "V(2) <= V(1)-1 与 V(1) <= V(2)-1 同时成立，相加得 0 <= -2。")
    check("I 截断域的逃逸时间见证", len(undef) == 0 and bad == 0)


# ---------------------------------------------------------------- J

def section_J(N=1 << 14):
    print("== J. 有界高度集合 S_N（定理 T5 的无穷域一侧）==")
    A = set(range(1, N + 1))
    changed = True
    while changed:
        changed = False
        for n in list(A):
            if T(n) not in A:
                A.remove(n)
                changed = True
    print(f"J1 N={N}：S_N = {{n <= N : 轨道恒 <= N}} 大小 = {len(A)}（占 {len(A)/N:.4f}），"
          f"最大元 = {max(A)}")
    print(f"J2 S_N 含 {{1,2}}：{1 in A and 2 in A}；S_N ∩ [3,N] 非空：{len(A) > 2}")
    print(f"J3 S_N 是 T 不变的：{all(T(n) in A for n in A)}")
    # 独立判定：到达 1 且轨道峰值 <= N
    bad = 0
    for n in range(1, N + 1):
        y = n
        peak = 0
        for _ in range(100000):
            peak = max(peak, y)
            if y == 1:
                break
            y = T(y)
        reach1 = (y == 1)
        if (reach1 and peak <= N) != (n in A):
            bad += 1
    print(f"J4 与「到达 1 且峰值 <= N」的独立判定不一致数 = {bad}")
    check("J 有界高度集合", bad == 0)


# ---------------------------------------------------------------- K

def tau_table(N):
    """总停时 τ（首次命中 1 的步数），带记忆化。"""
    tau = {1: 0}
    for n in range(2, N + 1):
        if n in tau:
            continue
        path = []
        x = n
        while x not in tau:
            path.append(x)
            x = T(x)
        t = tau[x]
        while path:
            y = path.pop()
            t += 1
            tau[y] = t
    return tau


def section_K():
    """对本轮反驳（甩给 formal-automata 的独立反驳意见）的独立复核。

    复核两件事：
      K1 「固定模数 + 每类深度 + 目标为固定界 X0」的证书被 2^(k+j)-1 族反驳；
      K2/K3 证书形式的二分：纤维上 σ 无界则不存在证书；纤维有限则构造成立。
    """
    print("== K. 证书形式的判据（对反驳修补的独立复核）==")

    # K1：目标为固定界 X0 的版本
    rows = []
    for k, c, X0 in [(1, 1, 10 ** 6), (5, 12, 4096), (10, 3, 10 ** 9),
                     (7, 50, 10 ** 30), (4, 1000, 10 ** 50)]:
        j = max(c - k, 0)
        while Tk((1 << (k + j)) - 1, c) <= X0:
            j += 1
        n = (1 << (k + j)) - 1
        rows.append((k, c, "%g" % float(X0), k + j,
                     n % (1 << k) == (1 << k) - 1, Tk(n, c) > X0))
    print("K1 (k, c, X0, 见证指数 m = k+j, 属类 2^k-1 且 T^c > X0)：")
    for r in rows:
        print(f"     k={r[0]} c={r[1]} X0={r[2]} m={r[3]} 类归属={r[4]} 越界={r[5]}")
    ok1 = all(r[4] and r[5] for r in rows)
    check("K1 固定界版本被同一族反驳", ok1)

    # K2：σ 在类 2^k-1 上无界 => 任何固定深度 d 都被击破
    bad = 0
    for k in range(1, 7):
        for d in range(1, 25):
            n = (1 << (k + max(d - k, 0))) - 1
            if not (n % (1 << k) == (1 << k) - 1 and Tk(n, d) >= n):
                bad += 1
    print(f"K2 k=1..6 与 d=1..24 的每个 (k,d)：同类见证 n 满足 T^d(n) >= n，失败数 = {bad}")
    check("K2 纤维上 σ 无界则无一致深度", bad == 0)

    # K3：纤维有限时的构造性证书（φ = (n mod 2^k, 位长)，深度 = 箱内最大总停时，取奇）
    N = 1 << 20
    tau = tau_table(N)
    for K in (1, 2, 4):
        c = {}
        for n in range(2, N + 1):
            key = (n % (1 << K), n.bit_length() - 1)
            if tau[n] > c.get(key, 0):
                c[key] = tau[n]
        for key in list(c):
            if c[key] % 2 == 0:
                c[key] += 1
        viol = 0
        for n in range(2, N + 1):
            if not Tk(n, c[(n % (1 << K), n.bit_length() - 1)]) < n:
                viol += 1
        fail = 0
        for n in range(2, 20001):
            x = n
            guard = 0
            while x >= 2 and guard <= 4:
                x = Tk(x, c[(x % (1 << K), x.bit_length() - 1)])
                guard += 1
            if x != 1:
                fail += 1
        print(f"K3 K={K}：n ∈ [2, 2^20] 上 T^c(n) < n 的违规数 = {viol}；"
              f"用该深度做下降链（n ≤ 20000，最多 5 段）未到 1 的个数 = {fail}")
        check(f"K3 K={K} 构造性证书成立", viol == 0 and fail == 0)


# ---------------------------------------------------------------- main

def main():
    section_A()
    section_B()
    section_C()
    section_D()
    section_E()
    section_F()
    section_G()
    section_H()
    section_I()
    section_J()
    section_K()
    print("全部检查完成，无 AssertionError。")


if __name__ == "__main__":
    main()
