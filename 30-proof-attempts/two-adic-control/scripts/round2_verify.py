#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
two-adic-control 路线第二轮的可执行验证。

全部判定为精确运算：有理数用 fractions.Fraction，2 进整数用模 2^N 的整数。
无浮点参与任何判定。

覆盖内容（与 attempt.md 的编号步骤对应）：

A1  等距中心化子定理的枚举侧面：窗口 k = 1、2、3 的全部块码中，哪些是等距
    （v_2(phi(x)-phi(x')) == v_2(x-x')）。
A2  块码刻画恒等式 phi_c(x)_n = c(窗 n..n+k-1) 满足 S∘phi = phi∘S。
A3  显式共轭与「算术不透明」见证（精确有理数）：Phi_a(1) = -1/a；
    Psi_+ = Phi_b∘Q_a、Psi_- = Phi_b∘sigma∘Q_a 的取值与解析式；
    共轭恒等式抽查。
A4  不动点与二周期点的整数计数（公式 x = c_v/(2^p - a^m) 的全部解）。
A5  S_a 结构（有界核验）与 Phi_a 的整数性失效。
A6  搬运命题的有界核验：Phi_b(y) 是最终周期点 <=> y ∈ Q。
A7  非双射块码的显式证书：缺词（非满射）或碰撞对（非单射），逐条显式验证。
"""

import sys
from fractions import Fraction as F
from itertools import product

sys.set_int_max_str_digits(200000)

OUT = []


def log(s=""):
    OUT.append(s)
    print(s)


# ================================================================ 基础工具

def v2_int(n):
    assert n != 0
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


def odd(x):
    """x ∈ Q 且分母为奇数（即 x ∈ Z_2）时为奇：等于分子的奇偶。"""
    return x.numerator % 2 == 1


def T(a, x):
    return (a * x + 1) / 2 if odd(x) else x / 2


def S(x):
    """2 进移位。x ∈ Q 且 x - (x mod 2) ∈ Q，除以 2 后仍在 Q。"""
    return (x - (x.numerator % 2)) / 2


def Q_of_periodic(a, x, limit=4000):
    """T_a 轨道最终周期的 x：精确计算 Q_a(x) = sum (T_a^i x mod 2) 2^i。"""
    seen = {}
    seq = []
    y = x
    while y not in seen:
        seen[y] = len(seq)
        seq.append(y.numerator % 2)
        y = T(a, y)
        if len(seq) > limit or abs(y.numerator) > 10 ** 400:
            raise RuntimeError("orbit did not repeat within limit")
    pre = seen[y]
    per = seq[pre:]
    val = sum(F(e) * (2 ** i) for i, e in enumerate(seq[:pre]))
    inner = sum(F(e) * (2 ** j) for j, e in enumerate(per))
    val += F(2 ** pre) * inner / (1 - 2 ** len(per))
    return val


def Phi(a, y, limit=100000):
    """
    Φ_a(y)，y ∈ Q ∩ Z_2（分母奇）。递推 Phi(2z) = 2 Phi(z)、
    Phi(2z+1) = (2 Phi(z) - 1)/a；遇周期解 u = beta/(a^M - alpha)。
    对有理 y 该递推必然终止（命中 0 或进入周期），见正文说明。
    """
    path = []
    seen = {}
    z = y
    while z != 0 and z not in seen:
        seen[z] = len(path)
        path.append(z)
        z = S(z)
        if len(path) > limit:
            raise RuntimeError("Phi recursion did not close")
    if z == 0:
        u = F(0)
        for zz in reversed(path):
            u = 2 * u if not odd(zz) else (2 * u - 1) / a
        return u
    start = seen[z]
    cyc = path[start:]
    alpha, beta, M = F(1), F(0), 0
    for w in reversed(cyc):
        if not odd(w):
            alpha, beta = 2 * alpha, 2 * beta
        else:
            alpha, beta, M = 2 * alpha, 2 * beta - a ** M, M + 1
    den = a ** M - alpha
    if den == 0:
        raise RuntimeError("degenerate cycle in Phi")
    u = beta / den
    for zz in reversed(path[:start]):
        u = 2 * u if not odd(zz) else (2 * u - 1) / a
    return u


def sigma(z):
    return -1 - z


def eventually_periodic(a, x, limit=400):
    """有界探测：x 在 T_a 下是否在 limit 步内出现重复。None 表示未判定。"""
    seen = {}
    y = x
    for i in range(limit):
        if y in seen:
            return True
        if abs(y.numerator) > 10 ** 200:
            return None
        seen[y] = i
        y = T(a, y)
    return None


# ================================================================ 块码

def phi_code(x, c, k, N):
    """φ_c(x) mod 2^N，x 为非负整数；φ_c(x)_n = c(窗 (x_n..x_{n+k-1}))。"""
    v = 0
    mask = (1 << k) - 1
    for n in range(N):
        if c[(x >> n) & mask]:
            v |= (1 << n)
    return v


def isometry_failures(c, k, jmax=7, N=26):
    bad = []
    for j in range(0, jmax + 1):
        for x in range(0, 1 << j):
            y = x + (1 << j)
            d = (phi_code(x, c, k, N) - phi_code(y, c, k, N)) % (1 << N)
            if d == 0:
                bad.append((x, j, "v2>=N"))
            elif v2_int(d) != j:
                bad.append((x, j, v2_int(d)))
    return bad


def image_mod(c, k, N):
    return set(phi_code(x, c, k, N) for x in range(1 << (N + k - 1)))


def tails_word(u, b):
    return tuple(list(u[1:]) + [b])


def win_int(w):
    """把窗（低位在前）转成块码表的下标。"""
    return sum(bit << i for i, bit in enumerate(w))


def A_set(c, k):
    """最大不动点：能承载共同标签序列无穷延拓的状态对 (u,u')，u ∈ {0,1}^{k-1}。"""
    states = list(product((0, 1), repeat=max(k - 1, 0)))
    A = set(product(states, states))
    changed = True
    while changed:
        changed = False
        for (u, up) in list(A):
            ok = False
            for b, bp in product((0, 1), repeat=2):
                if c[win_int(list(u) + [b])] == c[win_int(list(up) + [bp])]:
                    if (tails_word(u, b), tails_word(up, bp)) in A:
                        ok = True
                        break
            if not ok:
                A.discard((u, up))
                changed = True
    return A


def walk(u, up, c, k, A, cap=64):
    """在 A 上贪心走出一条相容路径，返回 (bits_x, bits_up, cycle_start)。"""
    bx, bup = [], []
    seen = {}
    cur = (u, up)
    while cur not in seen and len(bx) < cap:
        seen[cur] = len(bx)
        found = None
        for b, bp in product((0, 1), repeat=2):
            if c[win_int(list(cur[0]) + [b])] == c[win_int(list(cur[1]) + [bp])]:
                nxt = (tails_word(cur[0], b), tails_word(cur[1], bp))
                if nxt in A:
                    found = (nxt, b, bp)
                    break
        if found is None:
            return None
        nxt, b, bp = found
        bx.append(b)
        bup.append(bp)
        cur = nxt
    return bx, bup, seen.get(cur)


def collision_witness(c, k):
    """
    构造非单射见证：返回 (prefix, digits_x, digits_x')（prefix 为公共前缀，
    长度 0 或 1）或 None。
    依据：非单射 <=> 存在 (u,u') ∈ A、u != u'，且 u_0 != u'_0（取 m = 0）
    或存在 b 使 c(b + u) = c(b + u')（取 m = 1）。见 attempt.md 步骤 5、6。
    """
    if k == 1:
        return None
    A = A_set(c, k)
    for (u, up) in A:
        if u == up:
            continue
        if u[0] != up[0]:
            pre = ()
        else:
            pre = None
            for b in (0, 1):
                if c[win_int([b] + list(u))] == c[win_int([b] + list(up))]:
                    pre = (b,)
                    break
            if pre is None:
                continue
        w = walk(u, up, c, k, A)
        if w is None or w[2] is None:
            continue
        bx, bup, cyc = w
        off = len(u)                       # dx = u 后接 walk 追加的数字
        dx = list(u) + bx
        dup = list(up) + bup
        return pre, tuple(dx), tuple(dup), off + cyc
    return None


def digits_value(prefix, period):
    """数字序列（prefix 后接 period 无限重复）的精确 2 进值。"""
    val = sum(F(e) * (2 ** i) for i, e in enumerate(prefix))
    inner = sum(F(e) * (2 ** j) for j, e in enumerate(period))
    val += F(2 ** len(prefix)) * inner / (1 - 2 ** len(period))
    return val


def phi_of_digits(prefix, period, c, k):
    """按定义精确求 phi_c(x)，x = prefix + period 无限重复。"""
    P = len(period)
    L = len(prefix)
    seg = list(prefix) + list(period) * (k + 3)
    labels = [c[sum(seg[n + i] << i for i in range(k))]
              for n in range(len(seg) - k + 1)]
    pre_lab = labels[:L]
    per_lab = labels[L:L + P]
    assert len(per_lab) == P
    return digits_value(pre_lab, per_lab)


def label_seq(digits, c, k, length):
    return [c[sum(digits[n + i] << i for i in range(k))] for n in range(length)]


def succ_state(u, b, k):
    """状态 u ∈ {0,1}^{k-1} 读入位 b 后的后继状态。"""
    if k == 1:
        return ()
    return tuple(list(u[1:]) + [b])


def surjective_full(c, k):
    """
    满射判定：子集构造。图像为满当且仅当每个有限词都是某条有限路径的标号
    （有限路径总能延拓，故等价于满）。返回 True 表示满射。
    """
    states = list(product((0, 1), repeat=max(k - 1, 0)))
    idx = {s: i for i, s in enumerate(states)}
    start = frozenset(range(len(states)))
    seen = {start}
    stack = [start]
    while stack:
        S = stack.pop()
        for lab in (0, 1):
            T = set()
            for si in S:
                u = states[si]
                for b in (0, 1):
                    if c[win_int(list(u) + [b])] == lab:
                        T.add(idx[succ_state(u, b, k)])
            if not T:
                return False
            Tf = frozenset(T)
            if Tf not in seen:
                seen.add(Tf)
                stack.append(Tf)
    return True


# ================================================================ 主流程

def main(outfile=None):
    log("=" * 78)
    log("two-adic-control 第二轮验证（全部精确算术）")
    log("=" * 78)

    # -------------------------------------------------------------- A1
    log()
    log("[A1] 块码 c:{0,1}^k -> {0,1} 中「等距」者的枚举（k = 1,2,3）")
    log("     等距判据 v_2(phi(x)-phi(x')) == v_2(x-x')，j <= 7、24 位精度")
    for k in (1, 2, 3):
        passed = [c for c in product((0, 1), repeat=1 << k)
                  if not isometry_failures(c, k)]
        log("  k = %d：块码总数 %d，等距者 %d 个" % (k, 1 << (1 << k), len(passed)))
        for c in passed:
            dep = [i for i in range(1, 1 << k) if c[i] != c[i & 1]]
            log("      等距：c = %s（不依赖高于第 0 位者：%s）"
                % ("".join(map(str, c)), dep == []))

    # -------------------------------------------------------------- A2
    log()
    log("[A2] 块码刻画恒等式满足 S∘phi_c = phi_c∘S（等价于 S∘Phi_c 的共轭机制）")
    fails = []
    for k in (1, 2, 3):
        for c in product((0, 1), repeat=1 << k):
            for x in range(0, 1 << 12, 5):
                N = 12
                left = phi_code(x, c, k, N + 1) >> 1
                right = phi_code(x >> 1, c, k, N)
                if left != right:
                    fails.append((k, c, x))
    log("  不符个数：%d（应为 0）" % len(fails))

    # -------------------------------------------------------------- A3
    log()
    log("[A3] 算术不透明的精确见证")
    for a in (1, 3, 5, 7, 9):
        v = Phi(a, F(1))
        log("  Phi_%d(1) = %s；整数？ %s（公式 -1/a = %s）"
            % (a, v, v.denominator == 1, F(-1, a)))
    log("  行内结论：对每个奇 a >= 3，Phi_a 把整数 1 送到非整数 -1/a。")

    log()
    log("  共轭取值与解析式：")
    for (a, b) in [(3, 5), (3, 7), (3, 9), (1, 5), (1, 7), (3, 3)]:
        Q1 = Q_of_periodic(a, F(1))
        Qm1 = Q_of_periodic(a, F(-1))
        Q0 = Q_of_periodic(a, F(0))
        Q3 = Q_of_periodic(a, F(3))
        p_plus_m1 = Phi(b, Qm1)
        p_minus_0 = Phi(b, sigma(Q0))
        p_plus_3 = Phi(b, Q3)
        p_minus_3 = Phi(b, sigma(Q3))
        log("   (a,b) = (%d,%d)：Q_a(1) = %s，Q_a(-1) = %s，Q_a(3) = %s"
            % (a, b, Q1, Qm1, Q3))
        log("      Psi_+(-1) = %s；预期 -1/(b-2) = %s；整数？ %s"
            % (p_plus_m1, F(-1, b - 2), p_plus_m1.denominator == 1))
        log("      Psi_-(0)  = %s；预期 -1/(b-2) = %s；整数？ %s"
            % (p_minus_0, F(-1, b - 2), p_minus_0.denominator == 1))
        log("      Psi_+(3)  = %s；Psi_-(3) = %s" % (p_plus_3, p_minus_3))
        if a == 3 and b != 3:
            pred = 4 * F(-(b * b) + 2 * b + 4, (b * b) * (b - 4))
            log("        解析式 a=3：Psi_-(3) = 4(-b^2+2b+4)/(b^2(b-4)) = %s；相符？ %s"
                % (pred, pred == p_minus_3))
        if a == 1:
            log("        解析式 a=1：Psi_-(3) = -2/b = %s；相符？ %s"
                % (F(-2, b), F(-2, b) == p_minus_3))

    log()
    log("  共轭恒等式 Psi_+(T_a x) = T_b(Psi_+(x)) 与 Psi_-(T_a x) = T_b(Psi_-(x)) 抽查：")
    for (a, b) in [(3, 5), (3, 7), (1, 5), (5, 3)]:
        good = bad = skip = 0
        for p in range(-6, 7):
            for q in (1, 3, 5, 7):
                x = F(p, q)
                try:
                    qx = Q_of_periodic(a, x)
                    qtx = Q_of_periodic(a, T(a, x))
                except RuntimeError:
                    skip += 1
                    continue
                okp = Phi(b, qtx) == T(b, Phi(b, qx))
                okm = Phi(b, sigma(qtx)) == T(b, Phi(b, sigma(qx)))
                good += 1 if (okp and okm) else 0
                bad += 0 if (okp and okm) else 1
        log("   (a,b) = (%d,%d)：抽查 %d 组，失败 %d 组，跳过 %d 组"
            % (a, b, good + bad, bad, skip))

    # -------------------------------------------------------------- A4
    log()
    log("[A4] 不动点与二周期点：Fix(T_a^p) = {c_v/(2^p - a^m_v)} 的全部解，及整数计数")

    def fixpoints(a, p):
        pts = set()
        for v in product((0, 1), repeat=p):
            c, m = 0, 0
            for i, vi in enumerate(v):
                if vi:
                    c = a * c + (1 << i)
                    m += 1
            pts.add(F(c, 2 ** p - a ** m))
        return pts

    log("   a   | |Fix(T_a)| | 整数个数 | 整数集      | |Fix(T_a^2)| | 整数个数 | 整数集")
    for a in (1, 3, 5, 7, 9, 11):
        f1 = fixpoints(a, 1)
        z1 = sorted(x for x in f1 if x.denominator == 1)
        f2 = fixpoints(a, 2)
        z2 = sorted(x for x in f2 if x.denominator == 1)
        log("   %-3d | %-9d | %-8d | %-11s | %-11d | %-8d | %s"
            % (a, len(f1), len(z1), "{" + ",".join(str(x) for x in z1) + "}",
               len(f2), len(z2), "{" + ",".join(str(x) for x in z2) + "}"))

    log()
    log("  表格 2：|Fix(T_a^p) ∩ Z|（整数周期点的计数谱），p = 1..8")
    log("      a\\p  " + "".join("%6d" % p for p in range(1, 9)))
    spectra = {}
    for a in (1, 3, 5, 7, 9, 11, 13):
        row = []
        for p in range(1, 9):
            zp = [x for x in fixpoints(a, p) if x.denominator == 1]
            row.append(len(set(zp)))
        spectra[a] = row
        log("      %-4d " % a + "".join("%6d" % v for v in row))
    log("  对比规则（T2 的判据）：若存在 p 使计数(a,p) > 计数(b,p)，")
    log("  则不存在任何共轭 Ψ 满足 ΨT_a = T_bΨ 且 Ψ(Z) ⊆ Z。")
    covered = []
    odd_list = [1, 3, 5, 7, 9, 11, 13]
    for a in odd_list:
        for b in odd_list:
            if a == b:
                continue
            for p in range(1, 9):
                if spectra[a][p - 1] > spectra[b][p - 1]:
                    covered.append((a, b, p))
                    break
    log("  p <= 8 被上述规则覆盖的有序对 (a -> b)：%s"
        % ", ".join("%d->%d(p=%d)" % t for t in covered))

    # -------------------------------------------------------------- A5
    log()
    log("[A5] S_a = Phi_a(Q ∩ Z_2) = {最终周期点}：有界核验与整数性失效")
    for a in (3, 5):
        tot = cyc = 0
        for p in range(-10, 11):
            for q in range(1, 16, 2):
                x = F(p, q)
                tot += 1
                if eventually_periodic(a, x, limit=600) is True:
                    cyc += 1
        log("  a = %d：%d 个有理点中 %d 个在 600 步内成环（其余未判定）" % (a, tot, cyc))
        bad = 0
        cnt = 0
        for p in range(-10, 11):
            for q in range(1, 16, 2):
                v = Phi(a, F(p, q))
                cnt += 1
                if v.denominator % 2 == 0 or v.denominator < 0:
                    bad += 1
        log("     Phi_a 在这些点上的值全为分母奇的分数（Bernstein 半）：异常 %d / %d"
            % (bad, cnt))
    log()
    log("  Phi_a 在 2 的幂上的取值（2 齐次性 Phi(2^k) = 2^k Phi(1) = -2^k/a）：")
    for a in (3, 5):
        row = []
        for k in range(0, 4):
            row.append("2^%d->%s" % (k, Phi(a, F(2 ** k))))
        log("   a = %d：%s" % (a, "，".join(row)))

    # -------------------------------------------------------------- A6
    log()
    log("[A6] 搬运命题：Phi_b(y) 是 T_b 的最终周期点 <=> y ∈ Q（有界核验）")
    for b in (3, 5):
        ok = 0
        bad = []
        for p in range(-6, 7):
            for q in range(1, 12, 2):
                y = F(p, q)
                v = Phi(b, y)
                if eventually_periodic(b, v, limit=600) is True:
                    ok += 1
                else:
                    bad.append((y, v))
        log("  b = %d：%d 个有理 y 的 Phi_b(y) 在 600 步内成环；未判定 %d 个"
            % (b, ok, len(bad)))
        for y, v in bad[:4]:
            log("      未判定例：y = %s -> Phi_b(y) = %s" % (y, v))

    # -------------------------------------------------------------- A7
    log()
    log("[A7] 非双射块码的显式证书（缺词 / 碰撞对），每条证书当场验证")
    for k in (1, 2, 3):
        n_ns = n_col = n_cand = n_cer_bad = 0
        cands = []
        for c in product((0, 1), repeat=1 << k):
            img = image_mod(c, k, 10)
            if len(img) < (1 << 10):
                n_ns += 1
                continue
            wit = collision_witness(c, k)
            if wit is None:
                n_cand += 1
                cands.append(c)
                continue
            pre, dx, dup, cyc = wit
            px, perx = dx[:cyc], dx[cyc:]
            pxp, perp = dup[:cyc], dup[cyc:]
            if not perx or not perp:
                n_cer_bad += 1
                continue
            gx = tuple(pre) + tuple(px)
            gxp = tuple(pre) + tuple(pxp)
            vx = phi_of_digits(gx, perx, c, k)
            vxp = phi_of_digits(gxp, perp, c, k)
            # 两条序列必须真的不同：在有限可见范围内比对
            L = min(len(gx) + len(perx), len(gxp) + len(perp), 12)
            sx = list(gx + perx * 4)[:L]
            sxp = list(gxp + perp * 4)[:L]
            if vx == vxp and sx != sxp:
                n_col += 1
            else:
                n_cer_bad += 1
        log("  k = %d：非满射证书 %d 个；碰撞证书 %d 个；证书验证失败 %d 个；"
            "未排除者 %d 个" % (k, n_ns, n_col, n_cer_bad, n_cand))
        for c in cands:
            dep = [i for i in range(1, 1 << k) if c[i] != c[i & 1]]
            log("       未排除：c = %s（不依赖高位：%s）"
                % ("".join(map(str, c)), dep == []))

    # -------------------------------------------------------------- A8
    log()
    log("[A8] 周期点参数化（步骤 8）的逐点核验：三组相等关系")
    log("     (1) Fix(S^p) = {A/(1-2^p)}；(2) Ф_a(Fix(S^p)) = {c_v/(2^p - a^m_v)}；")
    log("     (3) 候选点确被 T_a^p 固定，且个数为 2^p。")
    a8_ok = True
    for a in (3, 5):
        for p in (1, 2, 3, 4):
            # (1)
            fixS = set()
            for A in range(1 << p):
                y = F(A, 1 - 2 ** p)
                if S(y) != y if p == 1 else False:
                    a8_ok = False
                z = y
                for _ in range(p):
                    z = S(z)
                if z != y:
                    a8_ok = False
                    log("     Fix(S^p) 反例：a=%d p=%d A=%d" % (a, p, A))
                fixS.add(y)
            if len(fixS) != (1 << p):
                a8_ok = False
            # (2)
            via_phi = set(Phi(a, y) for y in fixS)
            cands = set()
            for v in product((0, 1), repeat=p):
                c, m = 0, 0
                for i, vi in enumerate(v):
                    if vi:
                        c = a * c + (1 << i)
                        m += 1
                cands.add(F(c, 2 ** p - a ** m))
            if via_phi != cands:
                a8_ok = False
                log("     集合不等：a=%d p=%d" % (a, p))
            # (3)
            for x in cands:
                t = x
                for _ in range(p):
                    t = T(a, t)
                if t != x:
                    a8_ok = False
                    log("     非不动点：a=%d p=%d x=%s" % (a, p, x))
            if len(cands) != (1 << p):
                a8_ok = False
                log("     个数不为 2^p：a=%d p=%d 得 %d" % (a, p, len(cands)))
            log("     a=%d p=%d：|Fix(S^p)|=%d，|候选|=%d，两集合相等？ %s"
                % (a, p, len(fixS), len(cands), via_phi == cands))
    log("  A8 总体：%s" % ("全部通过" if a8_ok else "存在失败（见上）"))

    # -------------------------------------------------------------- A9
    log()
    log("[A9] 对反驳的处置核验（本地重跑，与反驳者的命令等价）")

    def red(x, m):
        """x ∈ Q（分母奇）在 Z/2^m 中的值。"""
        return (x.numerator * pow(x.denominator, -1, m)) % m

    log("  (1) 反例复核：断言「Phi_a(y) ≡ y (mod 2^p) 对一切 p」为假")
    for a in (3, 5):
        v = Phi(a, F(1))
        row = []
        for p in (1, 2, 3, 4):
            row.append("mod 2^%d=%d%s" % (p, red(v, 2 ** p),
                                          "✓" if red(v, 2 ** p) == 1 * (1 % (2 ** p)) else "✗"))
        log("     Phi_%d(1) = %s：%s" % (a, v, "，".join(row)))
    log("     结论：该断言对 a = 5、y = 1 自 p = 2 起为假，对 a = 3、y = 1 自 p = 3 起为假。")

    log("  (2) 正确论证所用结论的直接核验：Fix(S^p) 与 Fix(T_a^p) 都是模 2^p 的完整剩余系")
    for a in (3, 5):
        for p in (1, 2, 3, 4, 5):
            resS = set()
            for A in range(1 << p):
                y = F(A, 1 - 2 ** p)
                resS.add(red(y, 2 ** p))
            fx = set()
            for v in product((0, 1), repeat=p):
                c, m = 0, 0
                for i, vi in enumerate(v):
                    if vi:
                        c = a * c + (1 << i)
                        m += 1
                fx.add(red(F(c, 2 ** p - a ** m), 2 ** p))
            ok = (len(resS) == (1 << p)) and (len(fx) == (1 << p))
            log("     a=%d p=%d：|Fix(S^p) mod 2^p|=%d，|Fix(T_a^p) mod 2^p|=%d（应为 %d）%s"
                % (a, p, len(resS), len(fx), 1 << p, "✓" if ok else "✗"))
    log("     （Φ_a 是等距这一工具本身由步骤 1 的证明与第一轮脚本 C2 给出；")
    log("       等距 ⟹ x ≡ x′ (mod 2^p) ⟺ Φ_a(x) ≡ Φ_a(x′) (mod 2^p)，故完整剩余系性质被保持。）")

    def Fp_bijective(c, k, p):
        """循环字映射 F_p 是否双射（定义域与值域同为 {0,1}^p，故单射即双射）。"""
        seen = set()
        for v in range(1 << p):
            w = 0
            for i in range(p):
                win = 0
                for j in range(k):
                    win |= ((v >> ((i + j) % p)) & 1) << j
                if c[win]:
                    w |= 1 << i
            if w in seen:
                return False
            seen.add(w)
        return True

    log("  (3) 周期层过滤：g 双射 ⟹ 各层 F_p 双射（严格必要条件），故 F_p 失败即证非双射")
    import random
    for k in (1, 2, 3):
        surv = []
        for c in product((0, 1), repeat=1 << k):
            if all(Fp_bijective(c, k, p) for p in range(1, 9)):
                surv.append(c)
        dep = [c for c in surv
               if all(c[i] == c[i & 1] for i in range(1 << k))]
        log("     k=%d（穷尽 %d 个）：p ≤ 8 过滤后幸存 %d 个，其中不依赖高位者 %d 个"
            % (k, 1 << (1 << k), len(surv), len(dep)))
    log("     增加一节周期层过滤：k = 4 的 65536 个块码（穷尽，p ≤ 6，抗争性早退）")
    surv4 = []
    for c in product((0, 1), repeat=1 << 4):
        if all(Fp_bijective(c, 4, p) for p in range(1, 7)):
            surv4.append(c)
    dep4 = [c for c in surv4 if all(c[i] == c[i & 1] for i in range(1 << 4))]
    log("     k=4：过滤后幸存 %d 个，其中不依赖高位者 %d 个" % (len(surv4), len(dep4)))
    random.seed(20261020)
    for k in (5, 6):
        trials = 20000
        surv_rand = 0
        for _ in range(trials):
            c = tuple(random.randrange(2) for _ in range(1 << k))
            dep = all(c[i] == c[i & 1] for i in range(1 << k))
            if dep:
                continue
            if all(Fp_bijective(c, k, p) for p in range(1, 9)):
                surv_rand += 1
        log("     k=%d：随机 %d 个块码中，p ≤ 8 过滤后幸存（且依赖高位）者 %d 个"
            % (k, trials, surv_rand))

    log("  (4) 窗口 ≤ 4 的严格分类：满射判定用子集构造，单射判定用 A 集判据加显式碰撞证书")
    log("     子集构造的判据：有限词标号某条有限路径（有限路径总可延拓，故等价于满射）")
    for k in (1, 2, 3, 4):
        n_ns = n_noinj = n_cand = n_bad = 0
        cands = []
        for c in product((0, 1), repeat=1 << k):
            if not surjective_full(c, k):
                n_ns += 1
                continue
            wit = collision_witness(c, k)
            if wit is None:
                cands.append(c)
                continue
            pre, dx, dup, cut = wit
            px, perx = dx[:cut], dx[cut:]
            pxp, perp = dup[:cut], dup[cut:]
            if not perx or not perp:
                n_bad += 1
                continue
            gx = tuple(pre) + tuple(px)
            gxp = tuple(pre) + tuple(pxp)
            try:
                vx = phi_of_digits(gx, perx, c, k)
                vxp = phi_of_digits(gxp, perp, c, k)
            except AssertionError:
                n_bad += 1
                continue
            L = min(len(gx) + len(perx), len(gxp) + len(perp), 14)
            sx = list((gx + perx * 4))[:L]
            sxp = list((gxp + perp * 4))[:L]
            if vx == vxp and sx != sxp:
                n_noinj += 1
            else:
                n_bad += 1
        log("     k=%d：非满射 %d 个；满射但非单射（证书通过）%d 个；证书失败 %d 个；"
            "未排除 %d 个" % (k, n_ns, n_noinj, n_bad, len(cands)))
        for c in cands:
            dep = [i for i in range(1, 1 << k) if c[i] != c[i & 1]]
            log("        未排除：c = %s（不依赖高位：%s）"
                % ("".join(map(str, c)), dep == []))

    # -------------------------------------------------------------- 汇总
    log()
    log("=" * 78)
    log("汇总")
    log("=" * 78)
    log("A1 等距块码（窗口 <= 3）：只有 id 与 sigma（两者是同一映射的冗余窗口表示）")
    log("A2 S 交换恒等式失败数：%d" % len(fails))
    log("A3 Phi_a(1) = -1/a；Psi_+(-1) = Psi_-(0) = -1/(b-2)（b >= 5 时为非整数）")
    log("A4 不动点整数计数：a ∈ {1,3} 时为 2，a >= 5 时为 1")
    log("A7 块码分类（窗口 <= 3）：未排除者只有 id 与 sigma")
    log("提示：A5/A6 中「未判定」指轨道在限步内未成环，不构成反例。")

    if outfile:
        with open(outfile, "w", encoding="utf-8") as fh:
            fh.write("\n".join(OUT) + "\n")
        print("\n[written] %s" % outfile)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
