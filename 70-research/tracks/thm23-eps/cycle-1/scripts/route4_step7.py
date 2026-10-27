#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4：第七步 ε 的严格区间求值、印刷约定窗口反演、候选点精确判定。

事实层（本次亲读 200dpi 渲染图 scripts/route4-out/h5-p15-15.png，md5 2f6d307a...）：
  Hercher 2023 第 15 页第七步逐字：
    "Applying this lower bounnd a last time we get m2 >= 91, delta < (K+L)/K
     < delta + 1.11 · 10^-43 and K > 7.94 · 10^21."
  第七步是 m2 = m = 91 的特例（Theorem 21 的 m2 = m 式，无 X0 项）：
    delta < (K+L)/K < delta + ( 3/(2^v - 1) + 3*90/(2^v - 1)^delta ) / (3 K ln2),
    v = K (delta - 1)/(delta^91 - 1).
  本文件把右端的差值记作 eps_7(K)，用严格有理区间计算。

判定纪律：
  * 一切结论来自 Fraction 精确算术或区间包含；mpmath 只作展示与二分引导。
  * 印刷约定：ceil / round(四舍五入, half-up) / trunc(截尾)，各 1 位或 2 位小数。
  * 单调性引理（报告内给出证明）：K -> eps_7(K) 严格递减，故「印出给定字符串」
    的 K 集合是区间；窗口端点由区间二分严格包围。
"""
import os
import sys
sys.set_int_max_str_digits(2000000)   # 慢路径区间端点可达数千位
from fractions import Fraction as F
from math import floor, ceil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route4_rig as Rig

M = 91                     # m = m2 = 91
OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def _frac_dec(fr, nd):
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


def sci(fr, nd=30):
    """分数以科学计数法展示（截断到 nd 位）。"""
    if fr == 0:
        return "0"
    neg = fr < 0
    fr = abs(fr)
    e = len(str(fr.numerator)) - len(str(fr.denominator))
    s = F(10)
    while fr >= s ** (e + 1):
        e += 1
    while fr < s ** e:
        e -= 1
    return "%s%s·10^%d" % ("-" if neg else "", _frac_dec(fr / s ** e, nd), e)


# ---------------- 第七步 ε ----------------
def step7_eps(K, Nn=Rig.SERN, Nx=Rig.SERX, slow=False):
    """eps_7(K) 的严格区间。快路径用恒等式 (2^v-1)^delta = 3^n exp(r ln3 + delta ln(1-2^-v))；
    慢路径走 exp(delta*ln(2^v-1)) 原式；两条都是独立的严格路线。"""
    K = F(K)
    assert K > 0
    dl = Rig.delta_bounds(Nn)
    d91 = Rig.delta_pow_prod(M, Nn)
    v = Rig.idiv(Rig.imul((K, K), (dl[0] - 1, dl[1] - 1)),
                 (d91[0] - 1, d91[1] - 1))
    if slow:
        p2 = (Rig.pow2_bounds(v[0], Nx)[0], Rig.pow2_bounds(v[1], Nx)[1])
        t = (p2[0] - 1, p2[1] - 1)
        t1 = Rig.idiv((F(3), F(3)), t)
        lt = Rig.ln_interval(t, Nn)
        y = Rig.imul(dl, lt)
        p = (Rig.exp_bounds(y[0], Nx)[0], Rig.exp_bounds(y[1], Nx)[1])
    else:
        p2 = Rig.pow2_interval(v, Nx)
        t = (p2[0] - 1, p2[1] - 1)
        t1 = Rig.idiv((F(3), F(3)), t)
        p = Rig.oneminus_pow2delta(v, dl, Nx)
    t2 = Rig.idiv((F(3 * (M - 1)), F(3 * (M - 1))), p)
    br = Rig.iadd(t1, t2)
    den = Rig.iscale(Rig.imul((K, K), Rig.ln2_bounds(Nn)), 3)
    return Rig.idiv(br, den)


def mantle_interval(K, **kw):
    """x = eps_7(K) * 10^43 的严格区间。"""
    e = step7_eps(K, **kw)
    s = F(10) ** 43
    return (e[0] * s, e[1] * s)


# ---------------- 印刷规则（对区间严格判定） ----------------
def printed_scaled(xint, d, rule):
    """返回 (是否确定, 尾数*10^d 整数)。"""
    lo, hi = xint
    sc = 10 ** d
    if rule == "ceil":
        a, b = ceil(lo * sc), ceil(hi * sc)
    elif rule == "trunc":
        a, b = floor(lo * sc), floor(hi * sc)
    elif rule == "round":
        half = F(1, 2)
        a, b = floor(lo * sc + half), floor(hi * sc + half)
    else:
        raise ValueError(rule)
    return (a == b), (a if a == b else None)


def fmt_scaled(s, d):
    sc = 10 ** d
    s = int(s)
    ip = s // sc
    frac = str(s - ip * sc).rjust(d, "0")
    return ("%d.%s" % (ip, frac)) if d else str(ip)


# ---------------- 数值对照（仅展示） ----------------
def mpmath_eps(K, dps=60):
    import mpmath as mp
    mp.mp.dps = dps
    d = mp.log(3) / mp.log(2)
    v = mp.mpf(int(K)) * (d - 1) / (mp.power(d, M) - 1)
    t = mp.power(2, v) - 1
    return (3 / t + 3 * mp.mpf(M - 1) / mp.power(t, d)) / (3 * mp.mpf(int(K)) * mp.log(2))


def _x_mp(K_int, dps=40):
    import mpmath as mp
    mp.mp.dps = dps
    d = mp.log(3) / mp.log(2)
    K = mp.mpf(K_int)
    v = K * (d - 1) / (mp.power(d, M) - 1)
    t = mp.power(2, v) - 1
    eps = (3 / t + 3 * mp.mpf(M - 1) / mp.power(t, d)) / (3 * K * mp.log(2))
    return eps * mp.mpf(10) ** 43


def approx_root(target, iters=200):
    """mpmath 二分求 x(K)=target 的近似根（快、仅作二分引导）。"""
    import mpmath as mp
    t = mp.mpf(target.numerator) / target.denominator
    lo = mp.mpf(19) * 10 ** 19
    hi = mp.mpf(22) * 10 ** 19
    for _ in range(iters):
        mid = (lo + hi) / 2
        if _x_mp(mid) > t:
            lo = mid
        else:
            hi = mid
    mid = (lo + hi) / 2
    return F(int(mid * 10 ** 20), 10 ** 20)


def x_at(K, **kw):
    return mantle_interval(K, **kw)


def solve_K(target, rel=F(1, 10 ** 9)):
    """返回严格包围根 K*（x(K*)=target，x 严格递减）的区间 (a,b)：
    证书是区间比较 x(a) > target > x(b)。"""
    Ka = approx_root(target)
    for widen in (1, 10, 100, 1000, 10000, 100000):
        a = F(int(Ka * (1 - rel * widen)))
        b = F(int(Ka * (1 + rel * widen))) + 1
        xa = x_at(a)
        xb = x_at(b)
        if xa[0] > target and xb[1] < target:
            return a, b
    raise RuntimeError("solve_K 未找到严格括号：target=%s Ka=%s" % (target, Ka))


def rel_window(K, small_end, big_end):
    """窗口以小端 small_end、大端 big_end 为边界（都是包住真边界的区间）。
    余量一律以「正的区间」给出：距小端 = K 减小端边界；距大端 = 大端边界减 K。
    返回 (判定, 距小端余量区间或 None, 距大端余量区间或 None)。"""
    Llo, Lhi = small_end          # 真边界 ∈ [Llo, Lhi]
    Hlo, Hhi = big_end            # 真边界 ∈ [Hlo, Hhi]
    if K < Llo:
        return ("窗口外（偏小侧）", (Llo - K, Lhi - K), None)
    if K > Hhi:
        return ("窗口外（偏大侧）", None, (K - Hhi, K - Hlo))
    if Lhi <= K <= Hlo:
        return ("在窗口内", (K - Lhi, K - Llo), (Hlo - K, Hhi - K))
    return ("边界不确定带内", None, None)


def main():
    say("=" * 78)
    say("route-4 第七步 ε：严格区间求值、窗口反演、候选点判定")
    say("=" * 78)
    say("[0] 区间库：delta 宽 %.3e；ln2 宽 %.3e；ln3 宽 %.3e；网格 SNAP=1e-%d" %
        (float(Rig.wid(Rig.delta_bounds())), float(Rig.wid(Rig.ln2_bounds())),
         float(Rig.wid(Rig.ln3_bounds())), Rig.SNAP))

    K_STAR = 205632218873398596256
    CAND = [
        ("K* = 205632218873398596256（第六步精确 q_min，见 [7] 重算核对）", F(K_STAR)),
        ("2.05e20（印数截断读法）", F(205) * 10 ** 18),
        ("2.06e20（印数进位/四舍五入读法）", F(206) * 10 ** 18),
        ("2.059e20", F(2059) * 10 ** 17),
        ("2.0603e20", F(20603) * 10 ** 16),
        ("2.061e20", F(2061) * 10 ** 17),
        ("2.065e20", F(2065) * 10 ** 17),
    ]

    say("")
    say("[1] 候选点上的 eps_7*10^43（判定只用区间；mpmath 仅供展示）")
    rows = []
    for name, K in CAND:
        xi = mantle_interval(K)
        em = mpmath_eps(K)
        # 对照检查：mpmath 的 eps 乘 10^43，取 60 位十进制串转成有理数后与区间做精确比较
        # （展示级；区间宽度 1e-46 量级，60 位串的解析误差 ~1e-60 相对，不干扰结论）
        import mpmath as mp
        emx_str = mp.nstr(em * mp.mpf(10) ** 43, 60)
        emx = F(emx_str)
        inside = xi[0] <= emx <= xi[1]
        say("  %-44s x ∈ [%s, %s]（宽 %.1e） mpmath=%s 在区间内=%s" %
            (name, sci(xi[0], 26), sci(xi[1], 26), float(Rig.wid(xi)),
             emx_str, inside))
        rows.append((name, K, xi))

    say("")
    say("[2] 六种印刷约定（2 位与 1 位）在候选点印出的尾数；目标串为 1.11 时只有 2 位可能")
    for name, K, xi in rows:
        cell = []
        for rule in ("ceil", "round", "trunc"):
            for d in (2, 1):
                ok, s = printed_scaled(xi, d, rule)
                cell.append("%s%d=%s" % (rule, d, fmt_scaled(s, d) if ok else "不确定"))
        say("  %-44s %s" % (name, " ".join(cell)))

    say("")
    say("[3] 窗口反演：严格包围 x(K)=target 的 K 边界（x 严格递减；证书为区间比较）")
    targets = [F(12, 10), F(111, 100), F(112, 100), F(1115, 1000), F(1105, 1000),
               F(11, 10), F(10, 10), F(115, 100), F(105, 100)]
    bounds = {}
    for t in targets:
        a, b = solve_K(t)
        bounds[t] = (a, b)
        say("  K@(x=%s)：(%s, %s)  宽 %.2e  相对宽 %.1e" %
            (str(float(t)), str(a), str(b), float(b - a), float((b - a) / a)))

    say("")
    say("[4] 目标串「1.11」在 2 位小数各约定下的 K 窗口与候选点关系")
    windows = [
        # 小端（小 K 侧）在前：x 关于 K 严格递减，故较小的阈值对应较大的 K
        ("trunc 截尾", bounds[F(112, 100)], bounds[F(111, 100)], "(开, 闭]"),
        ("round 四舍五入", bounds[F(1115, 1000)], bounds[F(1105, 1000)], "(开, 闭]"),
        ("ceil 进位", bounds[F(111, 100)], bounds[F(110, 100)], "[闭, 开)"),
    ]
    for rname, se, be, oc in windows:
        say("")
        say("  约定 %s：窗口 %s，小端 K@小=[%s, %s]，大端 K@大=[%s, %s]" %
            (rname, oc, str(se[0]), str(se[1]), str(be[0]), str(be[1])))
        for cname, K, xi in rows:
            verdict, m1, m2 = rel_window(K, se, be)
            mm = ""
            if m1:
                mm += "  距小端(开) [%s, %s]" % (str(m1[0]), str(m1[1]))
            if m2:
                mm += "  距大端(闭) [%s, %s]" % (str(m2[0]), str(m2[1]))
            say("    %-44s %s%s" % (cname, verdict, mm))

    say("")
    say("[5] 附注：1 位小数各约定印出的是「1.1」而非「1.11」（目标串不同；列窗口备查）")
    aux = [
        ("trunc-1位", bounds[F(12, 10)], bounds[F(11, 10)]),
        ("round-1位", bounds[F(115, 100)], bounds[F(105, 100)]),
        ("ceil-1位", bounds[F(11, 10)], bounds[F(10, 10)]),
    ]
    for rname, se, be in aux:
        say("  %s：小端=[%s, %s] 大端=[%s, %s]" %
            (rname, str(se[0]), str(se[1]), str(be[0]), str(be[1])))
        for cname, K, xi in rows:
            verdict, _, _ = rel_window(K, se, be)
            say("    %-44s %s" % (cname, verdict))

    say("")
    say("[6] 单调性见证（该引理在报告第三节有完整证明；此处仅核实现）")
    tests = [(F(19, 10) * 10 ** 20, F(20, 10) * 10 ** 20),
             (F(205, 100) * 10 ** 20, F(206, 100) * 10 ** 20),
             (F(206, 100) * 10 ** 20, F(207, 100) * 10 ** 20),
             (F(20600, 10000) * 10 ** 20, F(20603, 10000) * 10 ** 20)]
    for K1, K2 in tests:
        x1 = mantle_interval(K1)
        x2 = mantle_interval(K2)
        say("    x(%s).lo > x(%s).hi ? %s" % (str(K1), str(K2), x1[0] > x2[1]))

    say("")
    say("[7] 第七步 Lemma 22 步：q(gamma) 与印数 K > 7.94e21 的核对")
    dl = Rig.delta_bounds()
    for name, K, xi in rows:
        eps = step7_eps(K)
        beta = (dl[0] + eps[0], dl[1] + eps[1])
        g = Rig.gamma_q(dl, beta)
        if "q" not in g:
            say("  %-44s gamma_q 需要收窄：%s" % (name, g))
            continue
        q = g["q"]
        # 印数核对：q 截尾/四舍五入到 3 位有效数字与 794（即 7.94e21）比较
        scale = 10 ** (21 - 3 + 1)
        cells = []
        for rule in ("trunc", "round", "ceil"):
            ok, s = printed_scaled((F(q, scale), F(q, scale)), 0, rule)
            cells.append("%s=%s" % (rule, s))
        say("  %-44s q=%s（%s）印 3 位有效数字核对：%s  连分数首异下标 k=%d, ak=%d, bk=%d" %
            (name, q, sci(F(q), 6), " ".join(cells), g["k"], g["ak"], g["bk"]))

    say("")
    say("[8] 快/慢两条 ε 路线交叉核对（K = 2.06e20）")
    ef = step7_eps(F(206) * 10 ** 18)
    say("  快路径：[%s, %s]" % (sci(ef[0], 26), sci(ef[1], 26)))
    es = step7_eps(F(206) * 10 ** 18, slow=True)
    say("  慢路径：[%s, %s]" % (sci(es[0], 26), sci(es[1], 26)))
    em = mpmath_eps(F(206) * 10 ** 18)
    say("  mpmath = %.40e" % float(em))
    say("  mpmath 在快区间内 = %s，在慢区间内 = %s" %
        (float(ef[0]) <= float(em) <= float(ef[1]),
         float(es[0]) <= float(em) <= float(es[1])))

    with open(os.path.dirname(os.path.abspath(__file__)) + "/route4-out/step7.txt", "w") as fh:
        fh.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
