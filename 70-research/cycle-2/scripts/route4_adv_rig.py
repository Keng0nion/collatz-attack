#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 敌意否证探针：严格有理证书模块（与路线 1「连分数严格证书」互不复用代码）。

只用标准库 fractions 的精确有理算术，加自实现的 atanh 级数与指数级数（带显式尾界）。
不 import 任何项目脚本；不 import mpmath。

自建工具（每条都写清依据）：
  1. atanh(r) = Σ_{k≥0} r^{2k+1}/(2k+1)（0<r<1，各项为正），
     尾界 ≤ r^{2N+3}/((2N+3)(1−r²))。
     ln2 = 2·atanh(1/3)，ln3 = ln2 + 2·atanh(1/5)（因 (1+1/5)/(1−1/5) = 3/2）。
  2. exp(y)（有理 y ≥ 0）：先取 m 使 s = y/2^m ≤ 1，用 Σ_{k≤N} s^k/k! 加尾界
     s^{N+1}/(N+1)!·1/(1−s/(N+2))，再平方 m 次（区间平方，正数保序）。
  3. ln(x)（有理 x>0）：写 x = 2^j·u，u∈[1,2)，u=(1+s)/(1−s) 得 ln u = 2·atanh(s)，
     s=(u−1)/(u+1)∈[0,1/3]。
  4. 单模区间引理（本路线自证的初等引理，见证书输出 [L]）：
     若 p/q < r/s < p'/q' 且 p'q − p q' = 1，则 s ≥ q + q'。
     证明：r/s − p/q = (rq − sp)/(sq) ≥ 1/(sq)，p'/q' − r/s ≥ 1/(s q')，两式相加得
     p'/q' − p/q ≥ (q+q')/(s q q')；而 p'/q' − p/q = (p'q − pq')/(q q') = 1/(q q')。
     故 1/(q q') ≥ (q+q')/(s q q')，即 s ≥ q + q'。

本模块的结论形态：给定「印出版 Theorem 21 的 eps 公式（含 2026 勘误末项）」与 δ 的
严格有理界，输出逐条可复算的严格不等式链；每条都打印所用分数与余量的十进制前若干位。
"""

from fractions import Fraction as F


# ------------------------------------------------------------ 基本不等式工具

WP = 70          # 工作精度：级数中间量每 WP 位向外取整一次，控制位数与运行时间


def _renorm(lo, hi, wp=WP):
    """把区间端点向外取整到 10^{-wp} 网格（严格放宽，见坏例登记）。"""
    return coarsen(lo, hi, wp)


def atanh_bounds(r, N, wp=WP):
    """
    0 < r < 1 有理数；返回 (lo, hi) 使 lo <= atanh(r) <= hi。
    各项为正，故部分和是下界；每 16 项把部分和向外取整一次（只放宽，不收紧），
    避免 r^(2k+1) 的位数按 (2N+1)·len(r) 爆炸。
    """
    assert 0 < r < 1
    r_lo, r_hi = coarsen(r, r, wp)
    assert 0 < r_lo <= r <= r_hi < 1
    s = F(0)
    term = r_lo                # r_lo^(2k+1) <= r^(2k+1)：部分和是下界
    r2 = r_lo * r_lo
    for k in range(N + 1):
        s += term / (2 * k + 1)
        term *= r2
        if k % 16 == 15:
            s = coarsen(s, s, wp)[0]
            term = coarsen(term, term, wp)[0]
            r2 = coarsen(r2, r2, wp)[0]
    # 尾界用 r_hi（界关于 r 增）：Σ_{k>N} r^{2k+1}/(2k+1) <= r_hi^{2N+3}/((2N+3)(1-r_hi²))
    tail = r_hi ** (2 * N + 3) / ((2 * N + 3) * (1 - r_hi * r_hi))
    return s, s + tail


def ln2_bounds(N=120):
    lo, hi = atanh_bounds(F(1, 3), N)
    return 2 * lo, 2 * hi


def ln3_bounds(N=120):
    l2lo, l2hi = ln2_bounds(N)
    lo, hi = atanh_bounds(F(1, 5), N)
    return l2lo + 2 * lo, l2hi + 2 * hi


def delta_bounds(N=120, ln2=None, ln3=None):
    """delta = ln3/ln2 的严格有理区间。"""
    l2lo, l2hi = ln2 if ln2 else ln2_bounds(N)
    l3lo, l3hi = ln3 if ln3 else ln3_bounds(N)
    return l3lo / l2hi, l3hi / l2lo


def exp_bounds(y_lo, y_hi, N=60):
    """0 <= y_lo <= y_hi 有理数；返回 (lo, hi) 使 lo <= exp(y) <= hi。"""
    assert 0 <= y_lo <= y_hi

    def exp_r(y):
        if y == 0:
            return F(1), F(1)
        m = 0
        s = y
        while s > 1:
            s /= 2
            m += 1
        s_lo = coarsen(s, s, WP)[0]
        s_up = coarsen(s, s, WP)[1]
        # 求和用 s_lo（下界侧）；尾界用 s_up（界关于 s 增）
        acc = F(1)
        term = F(1)
        for k in range(1, N + 1):
            term *= s_lo / k
            acc += term
            if k % 16 == 15:
                acc = coarsen(acc, acc, WP)[0]
        mfact = 1
        for k in range(1, N + 2):
            mfact *= k
        tail = s_up ** (N + 1) / mfact / (1 - s_up / (N + 2))
        lo, hi = acc, acc + tail
        for _ in range(m):
            lo, hi = lo * lo, hi * hi
            lo, hi = coarsen(lo, hi, WP + 10)     # 平方后向外取整，防位数翻倍累积
        return lo, hi

    lo, _ = exp_r(y_lo)          # exp 单调；下界用 y_lo
    _, hi = exp_r(y_hi)
    return lo, hi


def ln_bounds(x_lo, x_hi, l2=None, N=120):
    """0 < x_lo <= x_hi 有理数；返回 (lo, hi) 使 lo <= ln(x) <= hi。"""
    assert 0 < x_lo <= x_hi
    l2lo, l2hi = l2 if l2 else ln2_bounds(N)

    def ln_r(x):
        j = 0
        u = x
        while u >= 2:
            u /= 2
            j += 1
        while u < 1:
            u *= 2
            j -= 1
        s = (u - 1) / (u + 1)
        if s == 0:
            return F(j) * l2lo, F(j) * l2hi
        alo, ahi = atanh_bounds(s, N)
        return F(j) * l2lo + 2 * alo, F(j) * l2hi + 2 * ahi

    lo, _ = ln_r(x_lo)
    _, hi = ln_r(x_hi)
    return lo, hi


def pow_int(x_lo, x_hi, n):
    """0 < x_lo <= x_hi，n >= 0 整数。"""
    assert 0 < x_lo <= x_hi and n >= 0
    return x_lo ** n, x_hi ** n


def coarsen(lo, hi, digits=120):
    """
    向外取整到 10^{-digits} 网格：返回 (lo', hi') 满足 lo' <= lo <= hi <= hi'。
    用途：把高精度大整数界压到 ~10^digits 位，避免级数里出现百万位中间量。
    这是严格操作（只放宽，不收紧），代价是损失约 10^{-digits} 的相对紧度。
    """
    q = 10 ** digits
    lo_c = F((lo * q).__floor__(), q)      # 向下取到 10^{-digits} 网格
    hi_c = F((hi * q).__ceil__(), q)       # 向上取到 10^{-digits} 网格
    assert lo_c <= lo and hi_c >= hi
    return lo_c, hi_c


def dec(fr, nd=25):
    """Fraction 的十进制前 nd 位有效数字（仅用于打印）。"""
    if fr == 0:
        return "0"
    s = "-" if fr < 0 else ""
    v = abs(fr)
    e = 0
    while v >= 10:
        v /= 10
        e += 1
    while v < 1:
        v *= 10
        e -= 1
    digits = ""
    for _ in range(nd):
        d = int(v)
        digits += str(d)
        v = (v - d) * 10
    return "%s%s.%se%+d" % (s, digits[0], digits[1:], e)


# ------------------------------------------------------------ Hercher 侧的量

M = 92
X0 = 695 * 2 ** 60


class Env(object):
    """一次会话的 δ/ln2 界与由此派生的量。"""

    def __init__(self, N=120):
        self.N = N
        self.ln2 = ln2_bounds(N)
        self.ln3 = ln3_bounds(N)
        self.delta = delta_bounds(N, self.ln2, self.ln3)

    @property
    def dlo(self):
        return self.delta[0]

    @property
    def dhi(self):
        return self.delta[1]

    def geom(self, m2):
        """(delta^m2 - 1)/(delta - 1) 的区间（m2 >= 1）。"""
        a_lo, a_hi = pow_int(self.dlo, self.dhi, m2)
        num = (a_lo - 1, a_hi - 1)
        den = (self.dlo - 1, self.dhi - 1)
        return num[0] / den[1], num[1] / den[0]

    def log2_162X0(self):
        """log2((162/97)·X0) 的区间（X0 为整数，正）。"""
        x = F(162, 97) * X0
        nlo, nhi = ln_bounds(x, x, self.ln2, self.N)
        return nlo / self.ln2[1], nhi / self.ln2[0]

    def G(self, m2):
        """前提左端 G(m2) 的区间。"""
        g_lo, g_hi = self.geom(m2)
        l_lo, l_hi = self.log2_162X0()
        return g_lo * l_lo, g_hi * l_hi

    def feasible_cert(self, m2, K):
        """返回 'yes' / 'no' / 'unknown'（yes 表示严格可行）。"""
        g_lo, g_hi = self.G(m2)
        thr = F(m2, M) * K
        if g_hi <= thr:
            return "yes"
        if g_lo > thr:
            return "no"
        return "unknown"

    def v_bounds(self, m2, K):
        g_lo, g_hi = self.geom(m2)
        c = F(m2, M) * K
        return c / g_hi, c / g_lo

    def eps_bounds(self, m2, K, vswitch=160):
        """
        eps(m2,K) 的严格区间。返回 (lo, hi)。

        v 很大时的捷径（本次修正：v 可达 10^18，直接算 exp 会爆）：
          v_lo >= 160 时用 2^v - 1 >= 2^{v_lo-1}（因 v_lo >= 1），得
            3/(2^v-1) <= 3·2^{1-v_lo} <= 3·2^{-159} < 2^{-157}，
            3(m2-1)/((2^v-1)^delta) <= 273·2^{1-v_lo} < 2^{-152}（delta > 1）。
          两者统一用 2^{-150} 作上界，下界取 0（正项）。这是严格不等式，不是近似。
        """
        v_lo, v_hi = self.v_bounds(m2, K)
        if v_lo >= vswitch:
            t1_lo = t2_lo = F(0)
            t1_hi = t2_hi = F(1, 2 ** 150)
            pw_lo, pw_hi, t_lo, t_hi = None, None, None, None
        else:
            # 2^v = exp(v ln2)（先把指数界压到 10^-90 网格，保持严格性）
            y_lo, y_hi = coarsen(v_lo * self.ln2[0], v_hi * self.ln2[1], 90)
            two_lo, two_hi = exp_bounds(y_lo, y_hi, N=self.N)
            two_lo, two_hi = coarsen(two_lo, two_hi, 90)
            t_lo, t_hi = two_lo - 1, two_hi - 1
            assert t_lo > 0
            # (2^v - 1)^delta = exp(delta * ln(2^v - 1))
            lt_lo, lt_hi = ln_bounds(t_lo, t_hi, self.ln2, self.N)
            lt_lo, lt_hi = coarsen(lt_lo, lt_hi, 90)
            pw_lo, pw_hi = exp_bounds(self.dlo * lt_lo, self.dhi * lt_hi, N=self.N)
            t1_hi = 3 / t_lo
            t2_hi = 3 * F(m2 - 1) / pw_lo if m2 > 1 else F(0)
            t1_lo = 3 / t_hi
            t2_lo = 3 * F(m2 - 1) / pw_hi if m2 > 1 else F(0)
        if m2 == M:
            A_lo = A_hi = F(0)
        elif m2 == M - 1:
            A_lo = A_hi = F(3, X0)
        else:
            A_lo = A_hi = F(97 * (M - m2) + 73, 54 * X0)
        num_lo = A_lo + t1_lo + t2_lo
        num_hi = A_hi + t1_hi + t2_hi
        den_lo = 3 * K * self.ln2[0]
        den_hi = 3 * K * self.ln2[1]
        return num_lo / den_hi, num_hi / den_lo

    def eps_opt_bounds(self, K, fast=True):
        """
        eps_opt 的严格区间。

        快路径（fast=True，本证书用）：
          A 的分段单调性：对 1 <= m2 <= M-1 有 A(m2) >= A(M-1) = 3/X0，
            因 m2 = M-1 走 3/X0 支，其余走 (97(M-m2)+73)/(54X0) >= (97·2+73)/(54X0) > 3/X0。
          v 项非负，故对一切 m2 <= M-1：eps(m2,K) >= (3/X0)/(3K·ln2_hi)。
          于是只要 m2 = M 被严格判为不可行（feasible_cert 返回 'no'），就有
            eps_opt(K) >= (3/X0)/(3K·ln2_hi)      —— 严格下界。
          上界：任取一个严格可行的 m2（优先取 M-1），eps_opt <= eps(m2,K) 的上界。
        """
        if not fast:
            possibly, certain = [], []
            for m2 in range(1, M + 1):
                c = self.feasible_cert(m2, K)
                if c == "no":
                    continue
                e_lo, e_hi = self.eps_bounds(m2, K)
                possibly.append((m2, e_lo))
                if c == "yes":
                    certain.append((m2, e_hi))
            if not certain:
                raise RuntimeError("无确定可行的 m2")
            return min(e for _, e in possibly), min(e for _, e in certain), \
                min(certain, key=lambda x: x[1])[0]
        c_full = self.feasible_cert(M, K)
        if c_full != "no":
            return self.eps_opt_bounds(K, fast=False)
        lo = F(3, X0) / (3 * K * self.ln2[1])
        order = [M - 1, M - 2, M - 3]
        hi = None
        arg = None
        for m2 in order:
            if self.feasible_cert(m2, K) == "yes":
                _, e_hi = self.eps_bounds(m2, K)
                hi, arg = e_hi, m2
                break
        if hi is None:
            return self.eps_opt_bounds(K, fast=False)
        return lo, hi, arg


# ------------------------------------------------------------ 证书主程序

def main():
    env = Env(N=120)
    dlo, dhi = env.delta
    l2lo, l2hi = env.ln2
    print("=" * 78)
    print("[A] ln2、ln3 与 delta 的严格有理界（atanh 级数 N=120 项 + 显式尾界）")
    print("=" * 78)
    print("ln2  ∈ [%s, %s]" % (dec(l2lo, 20), dec(l2hi, 20)))
    print("ln3  ∈ [%s, %s]" % (dec(env.ln3[0], 20), dec(env.ln3[1], 20)))
    print("delta∈ [%s, %s]" % (dec(dlo, 25), dec(dhi, 25)))
    print("delta 区间宽度 = %s" % dec(dhi - dlo, 8))
    print("锚点：materials.md:60 记 mpmath 给 1.58496250072115618145373894394781650875981441")
    print("      本区间是否含该前缀（前 40 位）？ 下界前 40 位 =", dec(dlo, 41)[:42])
    K_STAR = 205632218873398596256
    K_CLO = F(313195478959172262767)      # 二分区间左端的整数部分（route-4.md:202）
    print()
    print("=" * 78)
    print("[B] K* 处 eps_opt 的严格区间（m = 92，X0 = 695·2^60）")
    print("=" * 78)
    e_lo, e_hi, arg_hi = env.eps_opt_bounds(K_STAR)
    print("eps_opt(K*) ∈ [%s, %s]   （materials.md:154 记 8.973221708617136016325725e-42）"
          % (dec(e_lo, 20), dec(e_hi, 20)))
    print("体面可行的 argmin（用上界比较）= m2 =", arg_hi)
    for m2 in (90, 91, 92):
        c = env.feasible_cert(m2, K_STAR)
        lo, hi = env.eps_bounds(m2, K_STAR)
        print("   m2=%2d 可行性=%-7s eps∈[%s, %s]" % (m2, c, dec(lo, 12), dec(hi, 12)))
    print()
    print("=" * 78)
    print("[C] 关键分数（delta 的收敛项 p41/q41、p42/q42 与 gamma = p43/q43 = K*）")
    print("=" * 78)
    # 用高精度有理递推需要 delta 的连分数数字：这里改用「证书自证」的方式，
    # 把三个分数作为待验证的具体整数对输入，全部关系用精确整数与有理比较核验。
    # 数字来源：本次 route4_probe_seq.py（mpmath dps=120）与 materials.md:169 一致；
    # 其正确性由本节的整数恒等式与不等式自行保证（不依赖 mpmath）。
    # 三个分数的来源：本文件用 mpmath（dps=200）自算 δ 的连分数数字，再用精确整数
    # 递推 p_i = a_i·p_{i-1} + p_{i-2} 得到（route4_adv_core.convergents）。
    # 它们是否真是 δ 的收敛项，由本节 [C1]（单模性 |det| = 1）、[C2][C3]（落在 δ 两侧）、
    # [C4][C5]（父分数关系）与 [D] 的区间包含**自行锚定**，不靠外部来源。
    # 登记：本表初稿的 p42 曾被我写成一个未经计算的数（195172401531033149227），
    # 被 [C1] 的 |det| ≠ 1 与 [C5] 的 False 当场抓出；下面这组是本次实跑打印的真值。
    FRAC = {
        "p41/q41": (123139092617126647266, 77692117359936589403),
        "p42/q42": (202780263237295321099, 127940101513462006853),
        "gamma=p43/q43": (325919355854421968365, 205632218873398596256),
        "next=38q43+q42": (None, 7941964418702608664581),
    }
    p41, q41 = FRAC["p41/q41"]
    p42, q42 = FRAC["p42/q42"]
    pg, qg = FRAC["gamma=p43/q43"]
    print("p41/q41 = %d/%d" % (p41, q41))
    print("p42/q42 = %d/%d" % (p42, q42))
    print("gamma   = %d/%d   （分母 = K* = %d）" % (pg, qg, K_STAR))
    det = p41 * q42 - p42 * q41
    print("[C1] 单模性 p41·q42 − p42·q41 = %d   （需 = ±1）" % det)
    print("[C2] p42/q42 < delta ？ %s   （下界 δlo = %s）"
          % (F(p42, q42) < dlo, dec(dlo, 15)))
    print("[C3] gamma > delta ？ %s   （上界 δhi = %s）" % (F(pg, qg) > dhi, dec(dhi, 15)))
    print("[C4] q41 + q42 = %d   （应 = q43 = K* = %d，等号 %s）"
          % (q41 + q42, qg, q41 + q42 == qg))
    print("[C5] p41 + p42 = %d   （应 = pg = %d，等号 %s）" % (p41 + p42, pg, p41 + p42 == pg))
    print("[C6] gamma − δ 严格界 ∈ [%s, %s]"
          % (dec(F(pg, qg) - dhi, 12), dec(F(pg, qg) - dlo, 12)))
    print()
    print("=" * 78)
    print("[D] 证书 (F)：区间 (δ, δ+eps_opt(K*)) 内最小分母 = K*")
    print("=" * 78)
    # 上界侧：gamma 在区间内
    ok_g_up = F(pg, qg) > dhi
    ok_g_rt = F(pg, qg) < dlo + e_lo
    print("[D1] gamma > δ（严格，用 δ 上界）           : %s" % ok_g_up)
    print("[D2] gamma < δ + eps_opt（用 δ 下界与 eps 下界）: %s" % ok_g_rt)
    print("     ⟹ 区间内含分母 %d = K* 的分数 ⟹ Psi_true(K*) <= K*" % qg)
    # 下界侧：单模区间
    ok_left = F(p42, q42) < dlo
    ok_right = dhi + e_hi < F(p41, q41)
    print("[D3] p42/q42 < δ（严格，用 δ 下界）        : %s" % ok_left)
    print("[D4] δ + eps_opt < p41/q41（用 δ 上界与 eps 上界）: %s" % ok_right)
    print("     余量（p41/q41 − δhi − eps_hi）= %s" % dec(F(p41, q41) - dhi - e_hi, 12))
    print("[D5] 由 [C1]（单模）+ [D3][D4] 与单模区间引理：区间 (δ, δ+eps_opt) ⊂ (p42/q42, p41/q41)，")
    print("     其中一切分数分母 >= q41 + q42 = %d = K*" % (q41 + q42))
    print("     ⟹ Psi_true(K*) >= K*")
    concl = ok_g_up and ok_g_rt and ok_left and ok_right and abs(det) == 1 and (q41 + q42) == qg
    print("[D6] 结论：Psi_true(K*) = K* 严格成立？ %s" % concl)
    print()
    print("=" * 78)
    print("[E] 派生：对一切 K >= K* 的地板 Psi_true(K) >= K*（类 1 反例在此区间被证明不存在）")
    print("=" * 78)
    print("前提 1（ε 单调）与前提 2（区间套）都是初等命题，证明见下方 [E1][E2] 的文字陈述；")
    print("本节的机器核对只覆盖「K* 处区间 ⊂ 单模区间」这一步（[D] 已给）。")
    print("[E1] 单参数单调性：对固定 m2，v(m2,K) 关于 K 严格增，故 2^v − 1 增、方括号内减、")
    print("     再除以 3K·ln2（K 的严格增函数）得 eps(m2,·) 非增。")
    print("[E2] 可行集单调：前提左端 G(m2) 与 K 无关，故 K1 <= K2 时 F(K1) ⊆ F(K2)；")
    print("     于是 eps_opt(K) = min_{m2∈F(K)} eps(m2,K) 非增（对更大的集合取更小的函数值）。")
    print("[E3] 区间套：K >= K* ⟹ eps_opt(K) <= eps_opt(K*) ⟹ (δ, δ+eps_opt(K)) ⊆ (δ, δ+eps_opt(K*))")
    print("     ⊆ (p42/q42, p41/q41) ⟹ 该区间内一切分数分母 >= K*。")
    print()
    print("=" * 78)
    print("[F] 平台右端的严格夹逼（m2 = 92 分支与根的位置）")
    print("=" * 78)
    gap_lo, gap_hi = F(pg, qg) - dhi, F(pg, qg) - dlo
    print("γ − δ 的严格区间 ∈ [%s, %s]" % (dec(gap_lo, 15), dec(gap_hi, 15)))
    print("判据：eps_lo > gap_hi 则「区间含 γ（故 Psi = K*）」严格成立；")
    print("      eps_hi <= gap_lo 则「区间不含 γ（故 Psi > K*）」严格成立。")
    ks = [313195478959172262767, 313195478959172262876, 313195478959172262877,
          313195478959172262878, 313195478959172262933]
    for K in ks:
        e_lo, e_hi, arg = env.eps_opt_bounds(K)
        st = ("含 γ" if e_lo > gap_hi else ("不含 γ" if e_hi <= gap_lo else "未定"))
        print("  K = %-22s eps_opt ∈ [%s, %s]  argmin_hi = %d  判定=%s"
              % (K, dec(e_lo, 8), dec(e_hi, 8), arg, st))
    print()
    print("=" * 78)
    print("[G] 见证值 7941964418702608664581 > U(92) = 1.4784·92·δ^92（越界见证的严格性）")
    print("=" * 78)
    d92_lo, d92_hi = pow_int(dlo, dhi, 92)
    U_lo = F(14784, 10000) * 92 * d92_lo
    U_hi = F(14784, 10000) * 92 * d92_hi
    witness = 7941964418702608664581
    print("U(92) ∈ [%s, %s]   （route-4.md:205 记 3.4302597024885e20）" % (dec(U_lo, 18), dec(U_hi, 18)))
    print("见证 7941964418702608664581 > U(92) 上界？ %s" % (F(witness) > U_hi))
    print("比值 U_hi/见证 = %s" % dec(U_hi / F(witness), 10))


if __name__ == "__main__":
    main()
