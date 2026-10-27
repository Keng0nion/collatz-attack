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
  * 一切结论来自 Fraction 精确算术或区间包含；mpmath 只作展示对照（明确标注）。
  * 印刷约定：ceil / round(四舍五入, half-up) / trunc(截尾)，各 1 位或 2 位小数，
    作用在尾数上（尾数 = eps * 10^43，或 1 位小数时按 eps * 10^E 的 E 取整）。
  * 单调性引理（本文件第四节论证并数值见证）：K -> eps_7(K) 严格递减，
    故「印出给定字符串」的 K 集合是区间。
"""
from fractions import Fraction as F
from math import floor, ceil
import sys

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import route4_rig as Rig

M = 91                     # m = m2 = 91
N_LAST = 90                # m2 - 1
OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)


def dec(x, nd=30):
    """分数的十进制截断展示。"""
    if isinstance(x, F):
        return Rig and _frac_dec(x, nd)
    return str(x)


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


# ---------------- 第七步 ε ----------------
def step7_eps(K, Nn=Rig.SERN, Nx=Rig.SERX):
    """返回 eps_7(K) 的严格区间 (lo,hi)（K 为 Fraction 或 int）。"""
    K = F(K)
    assert K > 0
    dl = Rig.delta_bounds(Nn)
    d91 = Rig.delta_pow_bounds(M, Nn)
    v = Rig.idiv(Rig.imul((K, K), (dl[0] - 1, dl[1] - 1)),
                 (d91[0] - 1, d91[1] - 1))
    p2 = (Rig.pow2_bounds(v[0], Nx)[0], Rig.pow2_bounds(v[1], Nx)[1])
    t = (p2[0] - 1, p2[1] - 1)
    t1 = Rig.idiv((F(3), F(3)), t)
    lt = Rig.ln_interval(t, Nn)
    y = Rig.imul(dl, lt)
    p = (Rig.exp_bounds(y[0], Nx)[0], Rig.exp_bounds(y[1], Nx)[1])
    t2 = Rig.idiv((F(M - 1) * 3, F(M - 1) * 3), p)
    br = Rig.iadd(t1, t2)
    l2 = Rig.ln2_bounds(Nn)
    den = Rig.iscale(Rig.imul((K, K), l2), 3)
    return Rig.idiv(br, den)


def mantle_interval(K, Nn=Rig.SERN, Nx=Rig.SERX):
    """x = eps_7(K) * 10^43 的严格区间。"""
    e = step7_eps(K, Nn, Nx)
    s = F(10) ** 43
    return (e[0] * s, e[1] * s)


# ---------------- 印刷规则（对区间严格判定） ----------------
def printed_scaled(xint, d, rule):
    """
    xint = (lo,hi) 含真值 x>0；d = 小数位数；rule in {'ceil','round','trunc'}。
    返回 (确定与否, 打印出的尾数*10^d 整数值 或 None)。
    """
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
    if a == b:
        return True, a
    return False, None


def fmt_scaled(s, d):
    """把「尾数*10^d」整数还原成打印串。"""
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
    return (3 / t + 3 * mp.mpf(N_LAST) / mp.power(t, d)) / (3 * mp.mpf(int(K)) * mp.log(2))


# ---------------- 二分求边界 ----------------
def x_at(K, Nn=Rig.SERN, Nx=Rig.SERX):
    return mantle_interval(K, Nn, Nx)


def solve_K(target, K_lo=F(20, 10) * 10 ** 20, K_hi=F(21, 10) * 10 ** 20,
            tol=F(1, 10 ** 5)):
    """在 [K_lo,K_hi] 内二分求 x(K) = target（x 单调递减）。返回 (a,b)：
    a < b, x(a) > target > x(b), b - a <= tol。区间端点均把结论包住。"""
    xa = x_at(K_lo)
    xb = x_at(K_hi)
    assert xa[1] < target, "左端 x 上界应低于 target"
    assert xb[0] > target, "右端 x 下界应高于 target"
    a, b = F(K_lo), F(K_hi)
    while b - a > tol:
        mid = (a + b) / 2
        xm = x_at(mid)
        if xm[0] > target:
            b = mid
        elif xm[1] < target:
            a = mid
        else:
            raise RuntimeError("二分点落在不确定区：K=%s x=%s" % (mid, xm))
    return a, b


def main():
    say("=" * 78)
    say("route-4 第七步 ε：严格区间求值、窗口反演、候选点判定")
    say("=" * 78)
    dl = Rig.delta_bounds()
    say("[0] delta 区间宽度 = %.3e；ln2 宽度 %.3e；ln3 宽度 %.3e" %
        (float(Rig.wid(dl)), float(Rig.wid(Rig.ln2_bounds())),
         float(Rig.wid(Rig.ln3_bounds()))))

    # 候选 K（全部为精确整数）
    K_STAR = 205632218873398596256           # 我方链条第六步的精确输出（本脚本将重算核对）
    CAND = [
        ("K*（第六步精确 q_min，待本脚本链条节重算核对）", F(K_STAR)),
        ("印数截断 2.05*10^20", F(205) * 10 ** 18),
        ("印数进位/四舍五入 2.06*10^20", F(206) * 10 ** 18),
        ("2.059*10^20", F(2059) * 10 ** 17),
        ("2.0603*10^20", F(20603) * 10 ** 16),
        ("2.061*10^20", F(2061) * 10 ** 17),
        ("2.065*10^20", F(2065) * 10 ** 17),
    ]

    say("")
    say("[1] 候选点上的 eps_7 与 mpmath 对照（判定只用区间；mpmath 仅供展示）")
    rows = []
    for name, K in CAND:
        xi = mantle_interval(K)
        em = mpmath_eps(K)
        inside = float(xi[0]) <= float(em) <= float(xi[1])
        say("  %-42s eps*1e43 区间 = [%s, %s]（宽 %.1e）mpmath=%s 区间内=%s"
            % (name, _frac_dec(xi[0], 20), _frac_dec(xi[1], 20),
               float(Rig.wid(xi)), "%s" % (("+%.12e" % 0) if False else em), inside))
        rows.append((name, K, xi))

    # 各印刷约定下的判定
    say("")
    say("[2] 六种印刷约定在候选点印出的尾数（步 7：目标串 1.11，2 位小数）")
    conv2 = [("ceil", 2), ("round", 2), ("trunc", 2)]
    for name, K, xi in rows:
        cell = []
        for rule, d in conv2:
            ok, s = printed_scaled(xi, d, rule)
            cell.append("%s%d=%s" % (rule, d, fmt_scaled(s, d) if ok else "不确定"))
        say("  %-42s %s" % (name, "  ".join(cell)))
    say("")
    say("  （1 位小数三种约定：目标串只能是 1.1 或 1.2 等，不可能是 1.11，见 [4] 附注）")

    # 窗口反演
    say("")
    say("[3] 窗口反演：解 x(K) = target 的 K 边界（x = eps_7(K)*10^43，严格递减）")
    targets = [F(110, 100), F(105, 100), F(111, 100), F(112, 100),
               F(1115, 1000), F(1105, 1000), F(12, 10), F(115, 100), F(10, 10)]
    bounds = {}
    for t in targets:
        a, b = solve_K(t)
        bounds[t] = (a, b)
        say("  K@(x=%s) in (%s, %s)  宽度 %.1e" %
            (str(float(t)), _frac_dec(a, 12), _frac_dec(b, 12), float(b - a)))

    def win_to_str(w):
        lo, hi = w
        return "(K@%s, K@%s]" % (lo, hi)

    say("")
    say("[4] 目标串「1.11」在各 2 位小数约定下的 K 窗口与候选点关系")
    windows = {
        "trunc 截尾": (bounds[F(112, 100)], bounds[F(111, 100)]),   # (K@1.12, K@1.11]
        "round 四舍五入": (bounds[F(1115, 1000)], bounds[F(1105, 1000)]),
        "ceil 进位": (bounds[F(111, 100)], bounds[F(110, 100)]),     # [K@1.11, K@1.10)
    }
    for rname, (wl, wh) in windows.items():
        # wl, wh 都是 (a,b) 边界区间；窗口 = (lo_end, hi_end] 形式，两侧各有一个小区间
        say("")
        say("  约定 %s：" % rname)
        for cname, K, xi in rows:
            # 判定：把窗口端点视为区间 [wl[0],wl[1]] 与 [wh[0],wh[1]]
            Llo, Lhi = wl[0], wl[1]
            Hlo, Hhi = wh[0], wh[1]
            if rname.startswith("ceil"):
                # 窗口 = [K@1.11, K@1.10)：下闭上开；wl=bounds[1.11], wh=bounds[1.10]
                inwin = (K >= Hhi) and (K < Llo)
                inwin2 = (K >= Hlo) and (K <= Lhi)
                if inwin:
                    verdict = "在窗口内"
                    marg_lo = (K - Hhi, K - Hlo)     # 距下界（含闭端）
                    marg_hi = (Llo - K, Lhi - K)     # 距上界（开端）
                elif inwin2:
                    verdict = "在边界不确定带内"
                    marg_lo = marg_hi = None
                else:
                    verdict = "在窗口外"
                    marg_lo = (K - Hhi, K - Hlo) if K < Hlo else None
                    marg_hi = (Llo - K, Lhi - K) if K > Lhi else None
            else:
                # 窗口 = (边界L, 边界H]：L = wl（截尾用 K@1.12；round 用 K@1.115），H = wh
                # 判定：Lhi <= K <= Hlo → 确定在窗口内； K <= Llo 或 K >= Hhi → 确定在窗口外
                if K <= Llo:
                    verdict = "窗口外（偏小侧）"
                    marg_lo = None
                    marg_hi = (Llo - K, Lhi - K)
                elif K >= Hhi:
                    verdict = "窗口外（偏大侧）"
                    marg_lo = (K - Hhi, K - Hlo)
                    marg_hi = None
                elif Lhi <= K <= Hlo:
                    verdict = "在窗口内"
                    marg_lo = (K - Hhi, K - Hlo)
                    marg_hi = (Llo - K, Lhi - K)
                else:
                    verdict = "在边界不确定带内"
                    marg_lo = marg_hi = None
            mm = ""
            if marg_lo:
                mm += " 距下界(开) [%s, %s]" % (_frac_dec(marg_lo[0], 6), _frac_dec(marg_lo[1], 6))
            if marg_hi:
                mm += " 距上界(闭) [%s, %s]" % (_frac_dec(marg_hi[0], 6), _frac_dec(marg_hi[1], 6))
            say("    %-42s %s%s" % (cname, verdict, mm))

    say("")
    say("[5] 附注：1 位小数各约定下印出的是「1.1」而非「1.11」（目标串不同，故不构成候选读法）")
    for rule in ("trunc", "round", "ceil"):
        # 目标串 1.1 的窗口：trunc: (K@1.2, K@1.1]; round: (K@1.15, K@1.05]; ceil: [K@1.1, K@1.0)
        if rule == "trunc":
            L, H = bounds[F(12, 10)], bounds[F(11, 10)]
        elif rule == "round":
            L, H = bounds[F(115, 100)], bounds[F(105, 100)]
        else:
            L, H = bounds[F(11, 10)], bounds[F(10, 10)]
        say("    %s-1位：窗口端点为 (%s,%s) 与 (%s,%s)" %
            (rule, _frac_dec(L[0], 10), _frac_dec(L[1], 10),
             _frac_dec(H[0], 10), _frac_dec(H[1], 10)))

    say("")
    say("[6] 单调性见证（区间比较，非网格）：对若干 K1<K2 检查 x(K1) 的区间下界 > x(K2) 的区间上界")
    tests = [(F(19, 10) * 10 ** 20, F(20, 10) * 10 ** 20),
             (F(205, 100) * 10 ** 20, F(206, 100) * 10 ** 20),
             (F(206, 100) * 10 ** 20, F(207, 100) * 10 ** 20),
             (F(20600, 10000) * 10 ** 20, F(20603, 10000) * 10 ** 20)]
    for K1, K2 in tests:
        x1 = mantle_interval(K1)
        x2 = mantle_interval(K2)
        say("    x(%s) lo = %s > x(%s) hi = %s ? %s" %
            (_frac_dec(K1, 4), _frac_dec(x1[0], 12),
             _frac_dec(K2, 4), _frac_dec(x2[1], 12), x1[0] > x2[1]))

    # 写文件
    with open(__file__.rsplit("/", 1)[0] + "/route4-out/step7.txt", "w") as fh:
        fh.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
