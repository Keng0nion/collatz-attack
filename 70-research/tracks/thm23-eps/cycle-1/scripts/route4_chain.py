#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4：Theorem 23 七步链条的取整约定穷举（严格有理区间口径）。

链条建模（每个量都标出处；出处均为本轨道 materials/ 下本次重新下载的原件）：
  K_0 = 7 * 10^11                      （第 15 页 Theorem 23 证明首句，本次亲读渲染图）
  每步：m2 = 最大可行 m2（Theorem 21 前提，第 13 页；本脚本对每步验证「m2 可行、m2+1 不可行」）
        ε = (A + 3/(2^v-1) + 3(m2-1)/(2^v-1)^delta) / (3 K ln2)
            v = (m2/m) K (delta-1)/(delta^m2 - 1)          （第 13 页陈述）
            A = 0 (m2=m) | 3/X0 (m2=m-1) | (97(m-m2)+c)/(54 X0)（其余）
            c ∈ {73（陈述页印数）, 1（证明末行印数）}       （第 13、14 页印数出入）
        K' = q(gamma)：Lemma 22 的 gamma = [a0;..,a_{k-1}, min(ak,bk)+1] 的分母
                                            （第 15 页 Lemma 22 陈述，本次亲读）
  X0 ∈ {695*2^60（印出版）, 704*2^60（arXiv v3）}

穷举维度（与 ask 的 4*6*2*2 对应，并把 K 的「印刷规则」与「回代规则」分开）：
  K 回代 4 态：exact / trunc / round / ceil（按该步印数的有效位数取整后回代）
  K 印刷 3 态：trunc / round / ceil            （用于核对印出的 K 串）
  ε 印刷 6 态：{ceil, round, trunc} × {1 位, 2 位小数}
  A 2 态：c = 73 / c = 1
  X0 2 态：695 / 704
  → 4*3*6*2*2 = 288 组；再加「去掉尾随零」的必要变体 ×2 = 576 组。
  轨迹只由 (K 回代, A, X0) 决定（ε 印刷与 K 印刷是事后比对），共 4*2*2 = 16 条轨迹。

判定纪律：一切比较为精确有理比较或区间包含；未定即报「未定」，不猜。
"""
import json
import os
import sys
sys.set_int_max_str_digits(2000000)   # 慢路径区间端点可达数千位
from fractions import Fraction as F
from math import floor, ceil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import route4_rig as Rig
import route4_step7 as S7

OUT = HERE + "/route4-out"
X0 = {695: 695 * 2 ** 60, 704: 704 * 2 ** 60}

# 论文印数（本次亲读 200dpi 渲染图 h5-p15-15.png；mant 为尾数整数，sig 为有效位，exp 为十进指数）
PRINTED = [
    # m2, K_mant, K_sig, K_exp, eps_mant, eps_exp, eps_dec
    # eps_exp 为印刷指数的真值（负数）：6.9e-32 → -32；尾数 = eps / 10^eps_exp
    (47, 52, 2, 15, 69, -32, 1),
    (67, 397, 3, 17, 51, -36, 1),
    (77, 464, 3, 18, 41, -38, 1),
    (82, 274, 3, 19, 23, -39, 1),
    (86, 776, 3, 19, 23, -40, 1),
    (88, 205, 3, 20, 53, -41, 1),
    (91, 794, 3, 21, 111, -43, 2),
]
K0 = F(7) * 10 ** 11
LINES = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LINES.append(s)


def fd(fr, nd=18):
    n, d = fr.numerator, fr.denominator
    sign = "-" if n < 0 else ""
    n = abs(n)
    ip = n // d
    rem = n - ip * d
    out = [sign, str(ip), "."]
    for _ in range(nd):
        rem *= 10
        out.append(str(rem // d))
        rem -= (rem // d) * d
    return "".join(out)


# ---------------- 基础区间量（可缓存） ----------------
def build_tables(maxm=91):
    """返回 (DL, POW, GEOM, LOG2N)：POW[m2] = delta^m2 的区间（每步 snap，压住分母位数）；
    GEOM[m2] = (delta^m2-1)/(delta-1)（可行性判据用）。"""
    dl = Rig.delta_bounds()
    pw = [(F(1), F(1))]
    for _ in range(maxm):
        pw.append(Rig.snap(Rig.imul(pw[-1], dl)))
    geoms = {m2: Rig.snap(Rig.idiv((pw[m2][0] - 1, pw[m2][1] - 1),
                                   (dl[0] - 1, dl[1] - 1)))
             for m2 in range(1, maxm + 1)}
    log2n = {k: Rig.log2_num_bounds(v) for k, v in X0.items()}
    return dl, pw, geoms, log2n


DL, POW, GEOM, LOG2N = build_tables()


def feasible_flag(m2, K, x0key):
    """返回 +1 可行 / -1 不可行 / 0 未定。前提：(delta^m2-1)/(delta-1)*log2((162/97)X0) <= (m2/m)K"""
    lhs = Rig.imul(GEOM[m2], LOG2N[x0key])
    rhs = K * F(m2, 91)
    if lhs[1] <= rhs:
        return 1
    if lhs[0] > rhs:
        return -1
    return 0


def m2_max_feasible(K, x0key):
    """返回 (m2max, m2min, 说明)。m2 可行性关于 m2 单调（见报告第三节引理），
    故可行集 = {1..m2max}；本函数对边界做两次严格比较并验证单调区间的两翼。"""
    fl = {m2: feasible_flag(m2, K, x0key) for m2 in range(1, 92)}
    if any(v == 0 for v in fl.values()):
        raise RuntimeError("可行性比较未定：K=%s x0=%s" % (K, x0key))
    fea = [m2 for m2 in fl if fl[m2] == 1]
    if not fea:
        return None
    m2max = max(fea)
    m2min = min(fea)
    assert set(fea) == set(range(m2min, m2max + 1)), "可行集不是前缀"
    assert m2max == 91 or fl[m2max + 1] == -1
    return m2min, m2max


def eps_interval(m2, K, cK, x0key):
    """定理 21 的 ε 区间；cK = 证明末行常数（73 或 1）。"""
    if m2 == 91:
        A = (F(0), F(0))
    elif m2 == 90:
        A = (F(3, X0[x0key]), F(3, X0[x0key]))
    else:
        a = F(97 * (91 - m2) + cK, 54 * X0[x0key])
        A = (a, a)
    # v = (m2/m) K (delta-1)/(delta^m2 - 1)：分母是 (delta^m2 - 1)，用 POW[m2] 表
    v = Rig.idiv(Rig.imul((K * F(m2, 91), K * F(m2, 91)), (DL[0] - 1, DL[1] - 1)),
                 (POW[m2][0] - 1, POW[m2][1] - 1))
    p2 = Rig.pow2_interval(v)
    t = (p2[0] - 1, p2[1] - 1)
    t1 = Rig.idiv((F(3), F(3)), t)
    p = Rig.oneminus_pow2delta(v, DL)
    t2 = Rig.idiv((F(3 * (m2 - 1)), F(3 * (m2 - 1))), p)
    br = Rig.iadd(Rig.iadd(A, t1), t2)
    den = Rig.iscale(Rig.imul((K, K), Rig.ln2_bounds()), 3)
    return Rig.idiv(br, den)


def mpmath_eps_general(m2, K, cK, x0key, dps=60):
    """定理 21 的 ε 的 mpmath 独立实现（数值对照用；证书仍由区间给出）。"""
    import mpmath as mp
    mp.mp.dps = dps
    d = mp.log(3) / mp.log(2)
    Kk = mp.mpf(int(K))
    v = Kk * mp.mpf(m2) / 91 * (d - 1) / (mp.power(d, m2) - 1)
    t = mp.power(2, v) - 1
    if m2 == 91:
        A = mp.mpf(0)
    elif m2 == 90:
        A = 3 / mp.mpf(X0[x0key])
    else:
        A = mp.mpf(97 * (91 - m2) + cK) / (54 * mp.mpf(X0[x0key]))
    return (A + 3 / t + 3 * mp.mpf(m2 - 1) / mp.power(t, d)) / (3 * Kk * mp.log(2))


def q_gamma(eps_int):
    """beta = delta + eps 的区间与 delta 区间做 Lemma 22（区间已足够窄，直接算）。"""
    beta = (DL[0] + eps_int[0], DL[1] + eps_int[1])
    g = Rig.gamma_q(DL, beta)
    return g if "q" in g else None


# ---------------- 印刷规则 ----------------
def rule_int(x_lo, x_hi, rule, strip=False):
    if rule == "trunc":
        a, b = floor(x_lo), floor(x_hi)
    elif rule == "round":
        h = F(1, 2)
        a, b = floor(x_lo + h), floor(x_hi + h)
    elif rule == "ceil":
        a, b = ceil(x_lo), ceil(x_hi)
    else:
        raise ValueError(rule)
    if a != b:
        return None
    return a


def feed_value(q, K_mant, K_sig, K_exp, rule):
    """把 q 按「该步印数精度」（有效位 K_sig、指数 K_exp）用 rule 取整后回代。"""
    if rule == "exact":
        return F(q)
    scale = 10 ** (K_exp - K_sig + 1)
    m = rule_int(F(q, scale), F(q, scale), rule)
    if m is None:
        raise RuntimeError("回代取整未定")
    return F(m) * scale


def k_print_matches(q, K_mant, K_sig, K_exp, rule):
    scale = 10 ** (K_exp - K_sig + 1)
    m = rule_int(F(q, scale), F(q, scale), rule)
    return (m == K_mant), m


def eps_print_matches(eps_int, eps_mant, eps_exp, dec, rule, strip=False):
    """尾数 X = eps / 10^eps_exp * 10^dec，与印刷整数 eps_mant 比较。
    eps_exp 为印刷指数真值（如 6.9e-32 → eps_exp = -32，尾数整 69 = X*10 取整）。
    strip=True 时，允许尾数整数的末位零被抹掉后相等（必要变体）。"""
    s = F(10) ** (-eps_exp) * (10 ** dec)
    X = (eps_int[0] * s, eps_int[1] * s)
    m = rule_int(X[0], X[1], rule)
    if m is None:
        return None, None
    if m == eps_mant:
        return True, m
    if strip:
        mm = m
        while mm % 10 == 0 and mm != 0:
            mm //= 10
        if mm == eps_mant:
            return True, m
    return False, m


# ---------------- 轨迹 ----------------
TRAJ_CACHE = {}


def trajectory(kfeed, cK, x0key):
    key = (kfeed, cK, x0key)
    if key in TRAJ_CACHE:
        return TRAJ_CACHE[key]
    K = K0
    recs = []
    for i, (m2p, km, ks, kexp, em, eexp, edec) in enumerate(PRINTED):
        m2min, m2max = m2_max_feasible(K, x0key)
        m2 = m2max                              # 论文读法：最大可行 m2（印数序列 47..91 即此）
        eps = eps_interval(m2, K, cK, x0key)
        # 独立数值对照（硬校验：mpmath 值必须落在严格区间内，否则立刻报错）
        # 注意：nstr 的位数必须显著多于区间相对宽（本库 ~1e-54），否则十进制截断
        # 本身的误差就会把「在区间内」判成 False（本轮踩过，已修）。
        import mpmath as mp
        em = mpmath_eps_general(m2, K, cK, x0key, dps=90)
        emq = F(mp.nstr(em, 80))
        if not (eps[0] <= emq <= eps[1]):
            raise RuntimeError("ε 区间未含 mpmath 值：步%d K=%s m2=%d c=%d X0=%d\n"
                               " 区间 [%s, %s]\n mpmath %s" %
                               (i + 1, K, m2, cK, x0key, eps[0], eps[1], mp.nstr(em, 50)))
        g = q_gamma(eps)
        rec = {"i": i + 1, "K_in": K, "m2min": m2min, "m2max": m2max, "m2": m2,
               "eps": eps, "q": g["q"] if g else None,
               "gamma": g, "cK": cK, "X0": x0key, "kfeed": kfeed}
        recs.append(rec)
        if g is None:
            break
        K = feed_value(g["q"], km, ks, kexp, kfeed)
    TRAJ_CACHE[key] = recs
    return recs


def gas_windows():
    """从缓存文件读/建「1.11 的 K 窗口」边界。"""
    path = OUT + "/windows.json"
    targets = ["12/10", "111/100", "112/100", "1115/1000", "1105/1000",
               "11/10", "10/10", "115/100", "105/100"]
    if os.path.exists(path):
        d = json.load(open(path))
        return {F(k): (F(v[0]), F(v[1])) for k, v in d.items()}
    res = {}
    for t in targets:
        a, b = S7.solve_K(F(t))
        res[F(t)] = (a, b)
    json.dump({str(k): [str(v[0]), str(v[1])] for k, v in res.items()},
              open(path, "w"))
    return res


def main():
    say("=" * 78)
    say("route-4 七步取整约定穷举（严格有理区间；K 回代 × K 印刷 × ε 印刷 × A × X0）")
    say("=" * 78)
    say("")
    say("[A] 16 条轨迹：每步 m2（最大可行）、ε 区间宽度、q(gamma)")
    for kfeed in ("exact", "trunc", "round", "ceil"):
        for cK in (73, 1):
            for x0 in (695, 704):
                recs = trajectory(kfeed, cK, x0)
                say("")
                say("  轨迹 kfeed=%s c=%d X0=%d：" % (kfeed, cK, x0))
                for r in recs:
                    say("    步%d K_in=%s  m2max=%d（m2min=%d） ε 宽 %.1e  q=%s" %
                        (r["i"], fd(r["K_in"], 10) if r["K_in"] < 10 ** 25 else str(r["K_in"]),
                         r["m2max"], r["m2min"], float(Rig.wid(r["eps"])),
                         r["q"]))
    say("")
    say("[B] 每步 q(gamma) 的印刷核对（K 三态）与 ε 印刷核对（六态，含去零变体）")
    for kfeed in ("exact", "trunc", "round", "ceil"):
        for cK in (73, 1):
            for x0 in (695, 704):
                recs = trajectory(kfeed, cK, x0)
                say("")
                say("  轨迹 kfeed=%s c=%d X0=%d：" % (kfeed, cK, x0))
                for r in recs:
                    i = r["i"] - 1
                    m2p, km, ks, kexp, em, eexp, edec = PRINTED[i]
                    cells = []
                    for rule in ("trunc", "round", "ceil"):
                        ok, m = k_print_matches(r["q"], km, ks, kexp, rule)
                        cells.append("%s:%s(%s)" % (rule, "O" if ok else "x", m))
                    say("    步%d 印 K 核对 %s" % (r["i"], " ".join(cells)))
                    ecells = []
                    for rule in ("trunc", "round", "ceil"):
                        for dec in (1, 2):
                            ok, m = eps_print_matches(r["eps"], em, eexp, dec, rule, False)
                            oks, ms = eps_print_matches(r["eps"], em, eexp, dec, rule, True)
                            ecells.append("%s%d:%s%s" % (rule, dec,
                                                         "O" if ok else ("o" if oks else "x"),
                                                         "" if ok or oks else "(%s)" % m))
                    say("    步%d 印 ε 核对 %s" % (r["i"], " ".join(ecells)))
    say("")
    say("[C] 组合全集：能同时复现七步全部印数（m2、K 串、ε 串）的组合")
    full = []
    partial = []
    for kfeed in ("exact", "trunc", "round", "ceil"):
        for kprint in ("trunc", "round", "ceil"):
            for erule in ("trunc", "round", "ceil"):
                for dec in (1, 2):
                    for strip in (False, True):
                        for cK in (73, 1):
                            for x0 in (695, 704):
                                recs = trajectory(kfeed, cK, x0)
                                ok_all = len(recs) == 7
                                n_ok = 0
                                for r in recs:
                                    i = r["i"] - 1
                                    m2p, km, ks, kexp, em, eexp, edec = PRINTED[i]
                                    if r["m2"] != m2p:
                                        ok_all = False
                                        continue
                                    k_ok, _ = k_print_matches(r["q"], km, ks, kexp, kprint)
                                    e_ok, _ = eps_print_matches(r["eps"], em, eexp, dec, erule, strip)
                                    if k_ok and e_ok:
                                        n_ok += 1
                                    else:
                                        ok_all = False
                                if ok_all:
                                    full.append((kfeed, kprint, erule, dec, strip, cK, x0))
                                if n_ok >= 6:
                                    partial.append((kfeed, kprint, erule, dec, strip, cK, x0, n_ok))
    say("  同时复现七步的组合数 = %d" % len(full))
    for c in full:
        say("    %s" % (c,))
    say("  复现 >=6 步的组合（含具体步数）：")
    for c in partial:
        say("    %s" % (c,))

    say("")
    say("[D] 第七步输入的窗口归属（窗口边界由 route4_step7.solve_K 严格二分得到）")
    W = gas_windows()
    win3 = [
        ("trunc-2位（目标 1.11）", W[F("112/100")], W[F("111/100")]),
        ("round-2位（目标 1.11）", W[F("1115/1000")], W[F("1105/1000")]),
        ("ceil-2位（目标 1.11）", W[F("110/100")], W[F("111/100")]),
    ]
    for nm, se, be in win3:
        say("  %s：小端=[%s,%s] 大端=[%s,%s]" %
            (nm, fd(se[0], 6), fd(se[1], 6), fd(be[0], 6), fd(be[1], 6)))
    say("")
    seen = {}
    for kfeed in ("exact", "trunc", "round", "ceil"):
        for cK in (73, 1):
            for x0 in (695, 704):
                recs = trajectory(kfeed, cK, x0)
                if len(recs) < 7:
                    continue
                K7 = recs[6]["K_in"]           # 第七步的输入 = 第六步输出 q_6
                key = str(K7)
                if key in seen:
                    continue
                seen[key] = True
                verdicts = []
                for nm, se, be in win3:
                    v, m1_, m2_ = S7.rel_window(K7, se, be)
                    verdicts.append("%s→%s" % (nm.split("（")[0], v))
                say("  第七步输入 K_in = %s（轨迹 kfeed=%s c=%d X0=%d 首次出现）" %
                    (K7, kfeed, cK, x0))
                say("      %s" % "；".join(verdicts))
                # 该输入的 ε 在六种约定下印出的尾数（步 7 记录）
                eps7 = recs[6]["eps"]
                cells = []
                for rule in ("ceil", "round", "trunc"):
                    for dec in (1, 2):
                        ok, m = eps_print_matches(eps7, 111, -43, dec, rule, False)
                        oks, ms = eps_print_matches(eps7, 111, -43, dec, rule, True)
                        cells.append("%s%d=%s" % (rule, dec,
                                                  "1.11✓" if (ok or oks) else
                                                  ("%.2f" % (m / (10 ** dec)) if m else "?")))
                say("      ε₇ 印刷：%s" % " ".join(cells))

    with open(OUT + "/chain.txt", "w") as fh:
        fh.write("\n".join(LINES) + "\n")


if __name__ == "__main__":
    main()
