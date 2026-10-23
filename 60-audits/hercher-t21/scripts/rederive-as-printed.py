#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重推：Hercher 2023 (JIS 26, Art. 23.3.5) Theorem 21 自举链，「印出版」。
本脚本从零编写，不复用任何既有脚本。

被重推的断言（Theorem 23 的证明，论文第 15 页）：
    设 m ≤ 91。若存在 m 圈，则 K > 7e11（Simons 与 de Weger 定理 3）。
    自举七步把 K 的下界推到 7.94e21，超过 SdW 上界 1.4784·m·δ^m < 2.2e20，
    故不存在这样的 m 圈。

所有假设都取自论文自身（行号指 /tmp/hercher-audit/hercher5.txt）：
  δ = log 3 / log 2                                    Definition 15，第 506 行
  X0 = 695 · 2^60                                      Definition 4，第 80 至 83 行
  T(n_i) < 3/n_i < 3/X0                                Remark 7，第 190 行
  k_i ≤ x_i = log2(n_i + 1)                            Lemma 8，第 207 行
  n_{i+1} < n_i^δ                                      Lemma 20，第 674 行
  δ < (K+L)/K < δ + (1/(3K log 2)) · Σ T(n_i)          Theorem 16，第 509 至 513 行
  m2 前提与 v 的定义                                    Theorem 21，第 696 至 705 行
  争议尾部 3(m2-1)/(2^v-1)^δ                           第 14 页底部（被质疑）
  K > 7e11                                             Theorem 23 证明首行，第 851 行
  K < 1.4784·m·δ^m                                     Theorem 23 证明末行，第 879 行
"""

import sys
from mpmath import mp, mpf, log, floor

X0_INT = 695 * 2 ** 60                    # 精确整数 801280445701758648320
SDW_START = mpf(7) * mpf(10) ** 11        # 论文用的统一下界起点
SDW_COEF = mpf("1.4784")                  # 论文用的 SdW 上界系数
LN2 = None                                # 在 setup 内赋值


# ----------------------------------------------------------------------
# 基本量的定义（全部由论文的式子直接给出）
# ----------------------------------------------------------------------
def setup(dps):
    mp.dps = dps
    globals()["LN2"] = log(mpf(2))


def delta():
    return log(mpf(3)) / log(mpf(2))


def c_const():
    """c = log2((162/97)·X0)，Theorem 21 前提里除以 log(2) 的那一项。"""
    return log(mpf(162) / mpf(97) * mpf(X0_INT)) / log(mpf(2))


def A_term(m, m2, plus=73):
    """Theorem 21 的 A。陈述页印 +73，证明末行印 +1；默认按陈述页 +73。"""
    if m2 == m:
        return mpf(0)
    if m2 == m - 1:
        return mpf(3) / mpf(X0_INT)
    return mpf(97 * (m - m2) + plus) / (mpf(54) * mpf(X0_INT))


def v_of(m, m2, K, d):
    """v = (m2/m)·K·(δ-1)/(δ^{m2}-1)。"""
    return (mpf(m2) / m) * K * (d - 1) / (d ** m2 - 1)


def eps_printed(m, m2, K, d, plus=73):
    """印出版的 ε（尾部 3(m2-1)/(2^v-1)^δ，即被质疑那一步的产物）。"""
    v = v_of(m, m2, K, d)
    A = A_term(m, m2, plus)
    tv = mpf(2) ** v - 1
    tail = mpf(3) * (m2 - 1) / (tv ** d)
    return (A + mpf(3) / tv + tail) / (mpf(3) * K * log(mpf(2)))


def eps_sound(m, m2, K, d, plus=73):
    """第三方健全版的 ε（尾部退回 Remark 7 的 3/X0），仅作对照。"""
    v = v_of(m, m2, K, d)
    A = A_term(m, m2, plus)
    tv = mpf(2) ** v - 1
    tail = mpf(3) * (m2 - 1) / mpf(X0_INT)
    return (A + mpf(3) / tv + tail) / (mpf(3) * K * log(mpf(2)))


# ----------------------------------------------------------------------
# m2 前提：(δ^{m2}-1)/(δ-1)·c ≤ (m2/m)·K
# ----------------------------------------------------------------------
def max_feasible_m2(m, K, d, c):
    for m2 in range(m, 0, -1):
        lhs = (d ** m2 - 1) / (d - 1) * c
        if lhs <= mpf(m2) / m * K:
            return m2
    return 0


# ----------------------------------------------------------------------
# K 的下界算子：Lemma 22 的连分数换算（第 822 至 845 行）
# ----------------------------------------------------------------------
def cf_terms(x, nmax):
    a = []
    y = mpf(x)
    for _ in range(nmax):
        ai = int(floor(y))
        a.append(ai)
        r = y - ai
        if r == 0:
            break
        y = 1 / r
    return a


def convergent(a):
    p0, p1 = 0, 1
    q0, q1 = 1, 0
    for ai in a:
        p0, p1 = p1, ai * p1 + p0
        q0, q1 = q1, ai * q1 + q0
    return p1, q1


def qmin_lemma22(a_val, b_val, nmax=400):
    """Lemma 22 的字面换算：γ = [a0;…;a_{k-1}, min(a_k,b_k)+1]，返回其分子分母。"""
    A = cf_terms(a_val, nmax)
    B = cf_terms(b_val, nmax)
    lim = min(len(A), len(B))
    k = 0
    while k < lim and A[k] == B[k]:
        k += 1
    if k == lim:
        return None, None
    ck = min(A[k], B[k]) + 1
    gam = A[:k] + [ck]
    p, q = convergent(gam)
    return (p, q), (k, A[k], B[k], ck)


def brute_min_denom(a_val, b_val, Q):
    """独立朴素检验：在 q ≤ Q 内穷举，看是否有 p/q 落在开区间内。"""
    hits = []
    for q in range(1, Q + 1):
        lo = a_val * q
        hi = b_val * q
        p = int(floor(lo)) + 1
        if p < hi:
            hits.append((p, q))
            if len(hits) > 3:
                break
    return hits


def qmin_walk(a_val, b_val, q_cap, step_cap=10 ** 7):
    """
    独立于 Lemma 22 公式的最小分母搜索（Stern 与 Brocot 中位分数下降）。
    维护两个 Farey 邻元 L < a_val < b_val < R；中位分数的分母为 qL+qR，
    而区间内任何分数的分母都不小于 qL+qR，故一旦中位分数落入区间即为最小分母。
    返回 (p, q)；若 qL+qR 超过 q_cap 仍未命中，返回 (None, None)（表示下界 > q_cap）。
    """
    k = int(floor(a_val))
    if int(floor(b_val)) > k:
        return k + 1, 1
    pL, qL, pR, qR = k, 1, k + 1, 1
    steps = 0
    while qL + qR <= q_cap:
        steps += 1
        if steps > step_cap:
            return None, None
        p, q = pL + pR, qL + qR
        if p <= a_val * q:
            pL, qL = p, q
        elif p >= b_val * q:
            pR, qR = p, q
        else:
            return p, q
    return None, None


# ----------------------------------------------------------------------
# 自举
# ----------------------------------------------------------------------
def one_round(m, K, d, c, eps_fn, mode):
    """
    给定下界 K，返回这一轮选出的 (m2, ε)。
    mode = 'max'  取前提允许的最大 m2（论文印出的取值方式）
    mode = 'minE' 在全部可行 m2 上取 ε 最小者
    """
    m2max = max_feasible_m2(m, K, d, c)
    if m2max == 0:
        return None
    if mode == 'max':
        return m2max, eps_fn(m, m2max, K, d)
    best = None
    for m2 in range(1, m2max + 1):
        e = eps_fn(m, m2, K, d)
        if best is None or e < best[1]:
            best = (m2, e)
    return best


def bootstrap(m, K_start, d, c, eps_fn, mode='max', kmax=200, stop_above=None):
    """逐轮：ε → 最小分母 → 新的 K 下界，直到不动点或越过 stop_above。"""
    K = mpf(K_start)
    hist = []
    for _ in range(kmax):
        if stop_above is not None and K > stop_above:
            break
        r = one_round(m, K, d, c, eps_fn, mode)
        if r is None:
            break
        m2, eps = r
        # q_min：先用 Lemma 22 公式（ε 可表示时），再用 Stern 与 Brocot 走查交叉验证
        frac_cf, info = (None, None)
        try:
            frac_cf, info = qmin_lemma22(d, d + eps)
        except Exception:
            frac_cf, info = None, None
        q_cap = max(10 ** 30, 10 * int(mpf(SDW_COEF) * m * d ** m))
        p_w, q_w = qmin_walk(d, d + eps, q_cap)
        # 两法一致？
        agree = (frac_cf is not None and q_w is not None
                 and frac_cf == (p_w, q_w))
        q_use = q_w if q_w is not None else (frac_cf[1] if frac_cf else None)
        if q_use is None:
            # 连分母都已超过 SdW 上界：该 m 直接排除
            hist.append(dict(m2=m2, eps=eps, qmin=None, q_cf=None, agree=None,
                             beyond=True, q_cap=q_cap))
            return mpf(q_cap), hist
        rec = dict(m2=m2, eps=eps, qmin=q_use, q_cf=frac_cf, agree=agree,
                   beyond=False, q_cap=q_cap, stall=False, info=info,
                   walk=(p_w, q_w))
        if q_use <= K:
            rec["stall"] = True
            hist.append(rec)
            break
        hist.append(rec)
        K = mpf(q_use)
    return K, hist


def fmt(x, sig=6):
    if x is None:
        return "None"
    x = mpf(x)
    if x == 0:
        return "0"
    from mpmath import mpf as _m
    e = int(floor(log(abs(x)) / log(mpf(10))))
    mant = x / mpf(10) ** e
    return "%.*f×10^%d" % (sig, mant, e)


# ----------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------
def main():
    out = []
    def p(s=""):
        out.append(s)
        print(s)

    for dps in (120, 200):
        setup(dps)
        d = delta()
        c = c_const()
        X0 = mpf(X0_INT)

        p("=" * 78)
        p("精度 mp.dps = %d" % dps)
        p("=" * 78)
        p("δ                       = %s" % mp.nstr(d, 40))
        p("X0 = 695·2^60           = %d" % X0_INT)
        p("log2(X0+1)              = %s" % mp.nstr(log(X0 + 1) / log(mpf(2)), 20))
        p("c = log2((162/97)·X0)   = %s" % mp.nstr(c, 20))
        p("1.4784·91·δ^91          = %s" % fmt(SDW_COEF * 91 * d ** 91))
        p()

        # ---------------- 争议步的两个缺陷：数值核验 ----------------
        p("---- 争议步的数值核验 ----")
        p("δ^2 = %s > δ = %s  → 第二个不等号对 ℓ ≥ 2 为假"
          % (mp.nstr(d ** 2, 20), mp.nstr(d, 20)))
        for l in (1, 2, 3, 5):
            p("    n = 2: 2^(δ^%d) = %s   vs   2^δ = %s" %
              (l, mp.nstr(mpf(2) ** (d ** l), 20), mp.nstr(mpf(2) ** d, 20)))
        p()

        # 第一步：印出版自举（m = 91）
        K_up91 = SDW_COEF * 91 * d ** 91
        p("---- 印出版自举，m = 91，模式 = 最大可行 m2 ----")
        K91, h91 = bootstrap(91, SDW_START, d, c, eps_printed, mode='max',
                             stop_above=K_up91)
        # 论文第 852 至 874 行印出的整数 m2（原文写作「>=」，实为最大可行值）
        paper_m2 = [47, 67, 77, 82, 86, 88, 91]
        # 论文印出的新 K 是 2 至 3 位有效数字的取整值，只能比到印刷精度
        paper_K_str = ["5.2e15", "3.97e17", "4.64e18", "2.74e19", "7.76e19",
                       "2.05e20", "7.94e21"]
        # 下面七个整数不是论文印出的（论文没有印全整数），而是争点简报第 4.1 节
        # 另一场会话独立算出的 q_min；用作跨会话交叉核对，不是「论文值」。
        brief_K = [5267319278509397, 397560349370386783, 4640282259296926456,
                   27444133206411171953, 77692117359936589403,
                   205632218873398596256, 7941964418702608664581]
        for i, h in enumerate(h91):
            pm = paper_m2[i] if i < len(paper_m2) else "无"
            bs = paper_K_str[i] if i < len(paper_K_str) else "无"
            qs = "超过该 m 的上界（walk 在 q_cap 处退出）" if h["qmin"] is None \
                else str(h["qmin"])
            ok_brief = (i < len(brief_K) and h["qmin"] == brief_K[i])
            p("  步 %d: m2 = %3d (论文印 %s)  ε = %s"
              % (i + 1, h["m2"], pm, fmt(h["eps"])))
            p("        q_min = %s   [论文印出的新 K = %s，只可比到印刷精度]"
              % (qs, bs))
            p("        与简报第 4.1 节另一场会话的 q_min 整数相符 = %s"
              % (ok_brief if i < len(brief_K) else "论文无此步"))
            p("        Lemma22 连分数公式给出 γ = %s / %s"
              % (h["q_cf"][0] if h["q_cf"] else "不可用",
                 h["q_cf"][1] if h["q_cf"] else "不可用"))
            if h["info"]:
                k_, ak, bk, ck = h["info"]
                p("          首次分歧指标 k = %d，a_k = %d，b_k = %d，c_k = %d"
                  % (k_, ak, bk, ck))
            p("        Stern 与 Brocot 走查给出 p/q = %s  两法逐位一致 = %s"
              % (("%d/%d" % h["walk"]) if h["walk"][0] is not None else "（超出上界）",
                 h["agree"]))
            if bs != "无":
                # 印刷值只有 2 至 3 位有效数字：把 q_min 也四舍五入到同样的有效位数再比
                mant_s = bs.split("e")[0].replace(".", "")
                nsig = len(mant_s)
                q_ = h["qmin"]
                e_ = int(floor(log(mpf(q_)) / log(mpf(10))))
                scale_ = mpf(10) ** (e_ - nsig + 1)
                rounded_ = int(mpf(q_) / scale_ + mpf("0.5")) * scale_
                same = (rounded_ == mpf(bs.split("e")[0]) * mpf(10) ** int(bs.split("e")[1]))
                p("        q_min 四舍五入到 %d 位有效数字 = %s  论文印 %s  → %s"
                  % (nsig, mp.nstr(rounded_, nsig + 2), bs,
                     "相符" if same else "论文是截断（非四舍五入）"))
        p("  终点：K 下界 = %d" % K91)
        p("        K 上界 = 1.4784·91·δ^91 = %s" % fmt(K_up91))
        p("        余量倍数 = K 下界 / K 上界 = %s" % mp.nstr(mpf(K91) / K_up91, 12))
        p()

        # 变体：ε 最小化的 m2
        p("---- 印出版自举，m = 91，模式 = ε 最小化 ----")
        K91b, h91b = bootstrap(91, SDW_START, d, c, eps_printed, mode='minE',
                               stop_above=K_up91)
        p("  步数 %d，终点 K = %d，m2 序列 = %s"
          % (len(h91b), K91b, [h["m2"] for h in h91b]))
        p("  余量倍数 = %s" % mp.nstr(mpf(K91b) / K_up91, 12))
        p()

        # 变体：证明末行的 +1
        p("---- 印出版自举，m = 91，A 用证明末行的 +1 ----")
        eps_plus1 = lambda m, m2, K, dd: eps_printed(m, m2, K, dd, plus=1)
        K91c, h91c = bootstrap(91, SDW_START, d, c, eps_plus1, mode='max',
                               stop_above=K_up91)
        p("  步数 %d，终点 K = %d，m2 序列 = %s，余量倍数 = %s"
          % (len(h91c), K91c, [h["m2"] for h in h91c],
             mp.nstr(mpf(K91c) / K_up91, 12)))
        p()

        # 对照：健全版尾部
        p("---- 对照：第三方健全版尾部 3(m2-1)/X0，m = 91 ----")
        K91s, h91s = bootstrap(91, SDW_START, d, c, eps_sound, mode='max',
                               stop_above=K_up91)
        p("  步数 %d，终点 K = %s，m2 序列 = %s"
          % (len(h91s), fmt(K91s), [h["m2"] for h in h91s]))
        p("  （对照脚本自身的健全口径：这是桩校验，不是本版结论）")
        p("  余量与上界之比 = %s" % mp.nstr(K91s / K_up91, 12))
        K91s2, h91s2 = bootstrap(91, SDW_START, d, c, eps_sound, mode='minE',
                                 stop_above=K_up91)
        p("  ε 最小化模式下：步数 %d，终点 K = %s，m2 序列 = %s"
          % (len(h91s2), fmt(K91s2), [h["m2"] for h in h91s2]))
        p("  健全口径逐 m 扫描（起点 7e11，上界 1.4784·m·δ^m）：")
        last_s, stall_s = None, None
        for m in range(2, 105):
            Kup = SDW_COEF * m * d ** m
            Km, hm = bootstrap(m, SDW_START, d, c, eps_sound, mode='max',
                               stop_above=Kup)
            if Km > Kup:
                last_s = m
            else:
                if stall_s is None:
                    stall_s = (m, Km)
                if 95 <= m <= 100:
                    p("    m = %3d 未排除：K 下界 = %s，上界 = %s，步数 = %d"
                      % (m, fmt(Km), fmt(Kup), len(hm)))
        p("    最大被排除 m = %s；首个停滞 m = %s，停滞点 K = %s"
          % (last_s, stall_s[0] if stall_s else "无",
             fmt(stall_s[1]) if stall_s else "无"))
        p()

        # 逐 m 扫描
        p("---- 逐 m 扫描（论文常数：起点 7e11，上界 1.4784·m·δ^m）----")
        first_excluded, last_excluded, allrows = None, None, []
        for m in range(2, 121):
            Kup = SDW_COEF * m * d ** m
            Km, hm = bootstrap(m, SDW_START, d, c, eps_printed, mode='max',
                               stop_above=Kup)
            ok = Km > Kup
            allrows.append((m, Km, Kup, ok, len(hm)))
            if ok:
                if first_excluded is None:
                    first_excluded = m
                last_excluded = m
        p("  首个小 m 被排除 = %s，最大的 m 被排除 = %s"
          % (first_excluded, last_excluded))
        p("  m = 80 至 96 的明细：")
        for (m, Km, Kup, ok, nh) in allrows:
            if 80 <= m <= 96:
                p("    m = %3d  步数 = %2d  K 下界 = %-22s 上界 = %-22s %s"
                  % (m, nh, fmt(Km), fmt(Kup), "排除" if ok else "未排除"))
        p()

        # 逐 m 扫描：m 相关的 SdW 常数
        p("---- 逐 m 扫描（m 相关 SdW 常数）----")
        p("  78 ≤ m ≤ 90:  K > 1.1173e17,  K < 1.3993·m·δ^m   (sidw144.txt 第 261 至 270 行)")
        p("  91 ≤ m ≤ 515619:  K > 7.5311e11,  K < 1.4784·m·δ^m (sidw144.txt 第 271 行)")
        last2 = None
        for m in range(78, 121):
            if m <= 90:
                Kstart, coef = mpf("1.1173") * mpf(10) ** 17, mpf("1.3993")
            else:
                Kstart, coef = mpf("7.5311") * mpf(10) ** 11, mpf("1.4784")
            Kup = coef * m * d ** m
            Km, hm = bootstrap(m, Kstart, d, c, eps_printed, mode='max',
                               stop_above=Kup)
            if Km > Kup:
                last2 = m
            else:
                p("    m = %d 未排除（K 下界 = %s，上界 = %s）" % (m, fmt(Km), fmt(Kup)))
        p("  这一口径下最大的 m 被排除 = %s" % last2)
        p()

        # 额外假设的量化：争议步要成立，需要 n_{i0+ℓ} 有多大
        p("---- 争议步若要成立所需的额外下界 n_{i0+ℓ} ≥ (2^v-1)^δ ----")
        p("  以下按 m = 91 自举各轮的 K 下界（该轮进入时的 K）计算阈值：")
        Krun = mpf(SDW_START)
        for i in range(len(h91)):
            r = one_round(91, Krun, d, c, eps_printed, 'max')
            m2, eps = r
            v = v_of(91, m2, Krun, d)
            thr = (mpf(2) ** v - 1) ** d
            p("    轮 %d: m2 = %3d, K = %-22s v = %-18s (2^v-1)^δ = %s"
              % (i + 1, m2, fmt(Krun), mp.nstr(v, 10), fmt(thr)))
            p("           对照 X0 = %s，log2(阈值) = %s"
              % (fmt(X0), mp.nstr(log(thr) / log(mpf(2)), 10)))
            Krun = mpf(h91[i]["qmin"])
        p()

        # 朴素穷举校验（只对第一步的 ε，规模受限）
        p("---- 朴素穷举校验 q_min（m = 91，第一步，ε = %s）----"
          % fmt(h91[0]["eps"]))
        hits = brute_min_denom(d, d + h91[0]["eps"], 300000)
        p("  在 q ≤ 300000 内落在 (δ, δ+ε) 内的分数：%s"
          % ("无" if not hits else hits))
        p("  第一步 q_min = %d >> 300000，与穷举不冲突" % h91[0]["qmin"])
        p()

    # ---------------- 具体反例（缺陷 2） ----------------
    setup(200)
    d = delta()
    c = c_const()
    p("=" * 78)
    p("缺陷 2 的具体反例（每一步只用论文自己列出的约束）")
    p("=" * 78)
    Krun = mpf(SDW_START)
    for i in range(7):
        r = one_round(91, Krun, d, c, eps_printed, 'max')
        m2, eps = r
        v = v_of(91, m2, Krun, d)
        ni0_low = mpf(2) ** v - 1                 # 2^v - 1 ≤ n_{i0}
        claimed = mpf(3) / ((mpf(2) ** v - 1) ** d)
        n_cand = mpf(10) ** 30
        ok_upper = n_cand < ni0_low ** d           # 满足印出的上界链
        T_lb = mpf(1) / n_cand                     # k = 1 时 T(n) = 1/n
        p("  轮 %d: m2 = %3d, 2^v-1 = %-20s" % (i + 1, m2, fmt(ni0_low)))
        p("         取 n = 10^30：n < n_{i0}^δ ? %s" % ok_upper)
        p("         印出断言 T < %s ；实际 k=1 时 T = 1/n = %s ；反例成立 ? %s"
          % (fmt(claimed), fmt(T_lb), T_lb > claimed))
        # 推进 K：用本轮的 ε 换出新的 K 下界
        q_cap = max(int(SDW_COEF * 91 * d ** 91) + 10, 10 ** 25)
        pw, qw = qmin_walk(d, d + eps, q_cap)
        if qw is None or qw <= Krun:
            break
        Krun = mpf(qw)

    # ================= 交叉反驳后的补充核验（2026 年 10 月 21 日） =================
    setup(200)
    d = delta()
    X0 = mpf(X0_INT)
    p("=" * 78)
    p("补充核验（应交叉反驳而加；mp.dps = 200）")
    p("=" * 78)

    # --- A：循环绕回给出的逐元素下界（我原报告说「往后走得不到下界」，此句被判错 ---
    m_w, m2_w = 91, 91
    K_w = mpf(205632218873398596256)          # 第七轮进入时的 K 下界
    v_w = v_of(m_w, m2_w, K_w, d)
    thr_w = d * log(mpf(2) ** v_w - 1) / log(mpf(2))   # 所需阈值 delta*log2(2^v-1)
    p("---- A. 循环绕回得到的逐元素下界（m = 91，m2 = 91，K = 2.056322×10^20）----")
    p("  v                          = %s" % mp.nstr(v_w, 12))
    p("  向后一步（第 m2−1 个尾部元素）= v/δ = %s" % mp.nstr(v_w / d, 12))
    p("  处处成立的通界 min x > K/(m·δ^{m−1}) = %s"
      % mp.nstr(K_w / (m_w * d ** (m_w - 1)), 12))
    p("  所需阈值 δ·log2(2^v−1)      = %s" % mp.nstr(thr_w, 12))
    p("  最好的尾部元素缺口 = 阈值/(v/δ) = %s  （δ² = %s）"
      % (mp.nstr(thr_w / (v_w / d), 10), mp.nstr(d ** 2, 10)))
    p("  最差元素的缺口 = 阈值/(K/(m δ^{m−1})) = %s"
      % mp.nstr(thr_w / (K_w / (m_w * d ** (m_w - 1))), 8))
    p("  向后 j 步到达的下标（核验指数与 m 还是与 m2 有关）：")
    for (mm, mm2, ell) in [(91, 91, 1), (91, 86, 1), (91, 86, 85), (91, 47, 46)]:
        i0 = mm - mm2 + 1
        tgt = i0 + ell
        j = 0
        while True:
            j += 1
            idx = i0 - j
            while idx < 1:
                idx += mm
            if idx == tgt or j > mm + 2:
                break
        p("    m=%d m2=%d ℓ=%d → i0=%d 目标=%d 向后 j=%d（m−ℓ=%d；m2−ℓ=%d）"
          % (mm, mm2, ell, i0, tgt, j, mm - ell, mm2 - ell))
    p()

    # --- B：A 用 +1 与 +73 时各轮的 ε ---
    p("---- B. A 的 +1 与 +73：各轮 ε 对照 ----")
    def eps_v(m_, m2_, K_, plus_):
        if m2_ == m_:
            A_ = mpf(0)
        elif m2_ == m_ - 1:
            A_ = mpf(3) / X0
        else:
            A_ = mpf(97 * (m_ - m2_) + plus_) / (54 * X0)
        v_ = v_of(m_, m2_, K_, d)
        tv_ = mpf(2) ** v_ - 1
        return (A_ + 3 / tv_ + mpf(3) * (m2_ - 1) / tv_ ** d) / (3 * K_ * log(mpf(2)))
    Ks_B = [mpf(SDW_START), mpf(5267319278509397), mpf(397560349370386783),
            mpf(4640282259296926456), mpf(27444133206411171953),
            mpf(77692117359936589403), mpf(205632218873398596256)]
    m2s_B = [47, 67, 77, 82, 86, 88, 91]
    for i, (Kb, m2b) in enumerate(zip(Ks_B, m2s_B), 1):
        e73 = eps_v(91, m2b, Kb, 73)
        e1 = eps_v(91, m2b, Kb, 1)
        p("  轮 %d m2=%2d  ε(+73)=%-18s ε(+1)=%-18s 相对差=%s"
          % (i, m2b, mp.nstr(e73, 8), mp.nstr(e1, 8),
             mp.nstr(abs(e73 - e1) / e73, 6)))
    p("  第七轮 ε 对 K 的敏感度（论文印 1.11×10^-43）：")
    for Ktry in [mpf(205632218873398596256), mpf("2.06") * 10 ** 20,
                 mpf("2.05") * 10 ** 20]:
        p("    K = %-24s → ε = %s" % (mp.nstr(Ktry, 10),
                                       mp.nstr(eps_v(91, 91, Ktry, 73), 8)))
    p()

    # --- C：证人的奇偶性修正与可容性 ---
    p("---- C. 反例证人：n = 10^30 为偶数，改为 n = 10^30 + 1 ----")
    n_even = 10 ** 30
    n_odd = 10 ** 30 + 1
    p("  10^30 mod 4 = %d（偶数，不是局部极小值）" % (n_even % 4))
    p("  10^30+1 mod 4 = %d（奇数且 ≡ 1 mod 4，可与 k_i = 1 相容）" % (n_odd % 4))
    x_w = log(mpf(n_odd) + 1) / log(mpf(2))
    p("  证人 x = log2(n+1) = %s" % mp.nstr(x_w, 12))
    p("  可容性（第七轮）：")
    p("    上界 x_{i0+1} < δ·v        = %-18s 满足 ? %s"
      % (mp.nstr(d * v_w, 12), x_w < d * v_w))
    p("    下界 x_{i0+1} > v/δ^{m−1}  = %-18s 满足 ? %s"
      % (mp.nstr(v_w / d ** (m_w - 1), 8), x_w > v_w / d ** (m_w - 1)))
    p("    下界 x > K/(m·δ^{m−1})    = %-18s 满足 ? %s"
      % (mp.nstr(K_w / (m_w * d ** (m_w - 1)), 12),
         x_w > K_w / (m_w * d ** (m_w - 1))))
    claimed_w = 3 / (mpf(2) ** v_w - 1) ** d
    p("    印出断言 3/(2^v−1)^δ      = %s" % mp.nstr(claimed_w, 8))
    p("    实际 k=1 时 T = 1/n       = %s" % mp.nstr(1 / mpf(n_odd), 8))
    p("    反例仍成立 ? %s（倍数 %s）"
      % (1 / mpf(n_odd) > claimed_w,
         mp.nstr((1 / mpf(n_odd)) / claimed_w, 8)))
    p()

    # --- D：勘误收尾不等式抽查（大 v 的相对差小到需要更高精度，见下）---
    p("---- D. 勘误收尾不等式 (2^v−1)^δ < 2^{δv}−1 抽查 ----")
    p("  注：两端相对差约 δ/2^v，v 大时低于 mp.dps = 200 的分辨率，")
    p("  故本段单独把精度提到 mp.dps = 400，并同时打印相对差。")
    setup(400)
    d4 = delta()
    for vv in ["0.001", "1", "2", "10", "75.594632", "100", "1000", "5000"]:
        vv = mpf(vv)
        x_ = mpf(2) ** vv
        lhs = (x_ - 1) ** d4
        rhs = mpf(2) ** (d4 * vv) - 1
        rel = (rhs - lhs) / rhs
        p("  v=%-12s LHS<RHS ? %-6s 相对差 = %s"
          % (mp.nstr(vv, 8), lhs < rhs, mp.nstr(rel, 6)))
    p("  二阶导数的解析核验：f(x) = x^δ − 1 − (x−1)^δ 在 x > 1 上严格增、f(1) = 0，")
    p("  故 (2^v−1)^δ < 2^{δv}−1 对一切 v > 0 成立（此证明与数值抽查两法独立）。")
    p()

    p()
    p("(本脚本的 stdout 与 /tmp/rederive-as-printed.out 逐字节相同)")
    with open("/tmp/rederive-as-printed.out", "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
