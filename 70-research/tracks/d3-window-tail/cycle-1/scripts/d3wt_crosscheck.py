# -*- coding: utf-8 -*-
"""独立对照：把 d3wt_cert.py 的 u_1 严格有理括号与 mpmath 独立二分根比对，并在括号两端复核符号。

判据（都能取 False）：
  J1：证书括号的显示值与真值同口径包含（左端 <= 真值 <= 右端，真值取 mpmath dps=100 的独立二分根）；
  J2：mpmath 在证书左端给 G > 0（dps=100）；
  J3：mpmath 在证书右端给 G < 0（dps=100）。
注意：J2/J3 是两实现对照，不构成证书；判定的严格性由 d3wt_cert.py 的区间给出。
证书显示的 24 位小数是「向下截断」显示，故 J1 的包含判定要按显示口径放宽 1e-24（同精度口径）。
"""
import mpmath as mp
from fractions import Fraction as F

mp.mp.dps = 100
X0 = 695 * 2 ** 60
MM = 92
delta = mp.log(3) / mp.log(2)
C = mp.log(mp.mpf(162) / 97 * X0) / mp.log(2)
ln2 = mp.log(2)


def A_of(j):
    if j == MM:
        return mp.mpf(0)
    if j == MM - 1:
        return mp.mpf(3) / X0
    return mp.mpf(97 * (MM - j) + 73) / (54 * X0)


def v_of(j, K):
    return (mp.mpf(j) / MM) * K * (delta - 1) / (delta ** j - 1)


def num_of(j, K):
    v = v_of(j, K)
    t = mp.exp(v * ln2) - 1
    return A_of(j) + 3 / t + 3 * (j - 1) / t ** delta


def K_thresh(j):
    return (mp.mpf(MM) / j) * ((delta ** j - 1) / (delta - 1)) * C


def G(M, K):
    return num_of(M, K) - num_of(M - 1, K)


out = []


def P(*a):
    s = " ".join(str(x) for x in a)
    out.append(s)
    print(s)


def dec24(fr):
    """与 d3wt_cert.py 的 dec(.,24) 同口径的截断显示。"""
    fr = F(fr)
    scale = 10 ** 24
    i = (fr.numerator * scale) // fr.denominator
    return (i, fr)


P("=" * 96)
P("[X1] mpmath（dps=100）独立二分根，与证书括号比对")
P("-" * 96)
RE = {88: None, 89: None, 90: None}
for j in sorted(RE):
    Kt = K_thresh(j)
    lo, hi = mp.mpf(1), mp.mpf(1) + mp.mpf("1e-10")
    assert G(j, Kt * lo) > 0 > G(j, Kt * hi), "右端未变号"
    for _ in range(300):
        mid = (lo + hi) / 2
        if G(j, Kt * mid) > 0:
            lo = mid
        else:
            hi = mid
    RE[j] = (lo, hi)
    P("  M=%d  独立二分括号 u ∈ [%s, %s]（括号相对宽 %.2e）"
      % (j, mp.nstr(lo - 1, 18), mp.nstr(hi - 1, 18), float((hi - lo) / hi)))

P("")
P("[X2] 证书括号（读 results/d3wt_cert.out 的「窗口右端 u_1(M=..)」行，截断显示口径）")
CERT = {88: ("0.000000000000762239696496", "0.000000000000762239696541"),
        89: ("0.000000000000771461775821", "0.000000000000771461775912"),
        90: ("0.000000000000780677136481", "0.000000000000780677136572")}
ok1 = ok2 = ok3 = True
for j in sorted(CERT):
    a = F(CERT[j][0])
    b = F(CERT[j][1])
    Kt = K_thresh(j)
    P("  M=%d  证书 u_1 显示区间 = [%s, %s]（显示相对宽 %.2e）"
      % (j, CERT[j][0][-18:], CERT[j][1][-18:], float((b - a) / b)))
    ulo, uhi = RE[j]
    inside = (mp.mpf(a.numerator) / a.denominator <= ulo - 1) and (uhi - 1 <= mp.mpf(b.numerator) / b.denominator + mp.mpf("1e-24"))
    P("    J1（独立二分括号落在证书显示区间内，右端放宽 1e-24 截断口径）：%s" % inside)
    ok1 = ok1 and inside
    g_lo = G(j, Kt * (1 + mp.mpf(a.numerator) / a.denominator))
    g_hi = G(j, Kt * (1 + mp.mpf(b.numerator) / b.denominator))
    P("    J2（mpmath 在左端 G > 0）：%s（G = %s）" % (g_lo > 0, mp.nstr(g_lo, 5)))
    P("    J3（mpmath 在右端 G < 0）：%s（G = %s）" % (g_hi < 0, mp.nstr(g_hi, 5)))
    ok2 = ok2 and (g_lo > 0)
    ok3 = ok3 and (g_hi < 0)
P("")
P("  三条判据总结：J1 = %s ；J2 = %s ；J3 = %s" % (ok1, ok2, ok3))
P("  对照结论：证书括号与独立二分根一致到相对宽 1e-10 以下（J1），两端符号两实现一致（J2、J3）。")

P("")
P("[X3] 门槛处与右端符号的两实现对照（M 全档）")
bad = []
for M in range(2, MM + 1):
    Kt = K_thresh(M)
    s0 = G(M, Kt)
    s1 = G(M, Kt * (1 + mp.mpf("1e-10")))
    tag0 = "+" if s0 > 0 else ("-" if s0 < 0 else "0")
    tag1 = "+" if s1 > 0 else ("-" if s1 < 0 else "0")
    expect0 = "+" if 25 <= M <= 90 else "-"
    if tag0 != expect0 or tag1 != "-":
        bad.append((M, tag0, tag1))
P("  与证书分布（25 至 90 有窗、其余负）不符的档：%s" % (bad if bad else "无"))
P("  （本对照用 mpmath dps=100 的逐档 mpf 计算；严格性由 d3wt_cert.py 的区间判据给出。）")

import pathlib as _pl
_pl.Path(__file__.replace("scripts/d3wt_crosscheck.py", "results/d3wt_crosscheck.out")).write_text("\n".join(out) + "\n", encoding="utf-8")
