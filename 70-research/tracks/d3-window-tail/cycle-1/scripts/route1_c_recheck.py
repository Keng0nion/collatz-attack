#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route1_c_recheck.py —— 轨道 d3-window-tail cycle-1 route-1「否证独立重算」第 1 件。

自足脚本：只 import 标准库；不 import 任何项目脚本、不 import 被审代码。

(A) 用三套互相不同的分解（atanh 参数互不相同，其中一套的 ln2 走对数级数）给出
    C = log2((162/97)*X0) 的严格有理区间，并与三件对照物按「同精度口径」比较：
      R5_101 : 70-research/cycle-2/route-5.md:101 的 C 串与其自称严格区间（宽 7.9e-99）
      CERT9  : 70-research/cycle-2/scripts/results/c2r5_cert.log:9 的 C 串
      F64    : float64 精确二进制值（哪条表达式产生由本脚本自行判定）
(B) 复算门槛处相邻档差分解的第三加项 T3new、两顶残差 P1、比值与 log10 数量级。
(C) 每条判据配扰动实例（判据必须能取 False）。

精度口径（本次教训）：拿「截断打印串」当精确值做包含判定是错的（截断串必在真值一侧，
不与窄区间相交）。故本脚本一律用两套口径：
  1. 显示包络：k 位小数的串 s 对应 [s - 10^-k, s + 10^-k]，与严格区间求交；
  2. 吻合度：|严格区间端点 - 串| / 串 <= 10^-(有效位数-1)。
严格区间原语先用独立严格参照（e 的阶乘级数区间）自检。
"""
from fractions import Fraction as F
import math
import sys

OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def dec(x, nd):
    x = F(x)
    neg = x < 0
    x = abs(x)
    sc = 10 ** nd
    q = (x.numerator * sc) // x.denominator
    s = str(q)
    if nd:
        s = (s[:-nd] if len(s) > nd else "") + "." + s[-nd:].rjust(nd, "0")
        if s.startswith("."):
            s = "0" + s
    return ("-" if neg else "") + s


def round_dec(x, nd):
    """Fraction 精确四舍五入到 nd 位小数。"""
    x = F(x)
    sc = 10 ** nd
    t = x * sc
    fl = t.numerator // t.denominator
    if t - fl >= F(1, 2):
        fl += 1
    return F(fl, sc)


def sci(x, nd=6):
    x = F(x)
    if x == 0:
        return "0"
    neg = x < 0
    x = abs(x)
    e = 0
    while x >= 10:
        x /= 10
        e += 1
    while x < 1:
        x *= 10
        e -= 1
    return "%s%s×10^%d" % ("-" if neg else "", dec(x, nd), e)


def dec_to_F(s):
    s = s.strip()
    if "." in s:
        i, f = s.split(".")
        return F(int(i + f), 10 ** len(f))
    return F(int(s))


# #################### 严格区间原语 ####################
SNAP = 150


def snap_lo(x, Dg=SNAP):
    s = 10 ** Dg
    x = F(x)
    return F((x.numerator * s) // x.denominator, s)


def snap_hi(x, Dg=SNAP):
    s = 10 ** Dg
    x = F(x)
    n = x.numerator * s
    q, r = divmod(n, x.denominator)
    return F(q + (1 if r else 0), s)


def atanh_iv(u, N):
    """atanh(u) 的严格区间，要求 |u| <= 1/3（奇数性处理负号）。"""
    u = F(u)
    if u == 0:
        return F(0), F(0)
    if u < 0:
        a, b = atanh_iv(-u, N)
        return -b, -a
    assert 0 < u <= F(1, 3), u
    s = F(0)
    pw = u
    u2 = u * u
    for n in range(N + 1):
        s += pw / (2 * n + 1)
        pw *= u2
    return s, s + pw / ((2 * N + 3) * (1 - u2))


def ln2_atanh_iv(N):
    a, b = atanh_iv(F(1, 3), N)
    return 2 * a, 2 * b


def ln2_series_iv(N):
    s = F(0)
    for n in range(1, N + 1):
        s += F(1, n * (2 ** n))
    return s, s + F(1, (N + 1) * (2 ** N))


def inter(a, b):
    lo, hi = max(a[0], b[0]), min(a[1], b[1])
    return (lo, hi) if lo <= hi else None


def ln_of_rat_iv(y, ln2iv, N, Dg=SNAP):
    y = F(y)
    assert y > 0
    k = y.numerator.bit_length() - y.denominator.bit_length()
    while F(2) ** k > y:
        k -= 1
    while F(2) ** (k + 1) <= y:
        k += 1
    z = y / F(2) ** k
    if z * z > 2:
        z /= 2
        k += 1
    z = snap_lo(z, Dg)
    u = (z - 1) / (z + 1)
    az = atanh_iv(u, N)
    lo2, hi2 = ln2iv
    if k >= 0:
        return k * lo2 + 2 * az[0], k * hi2 + 2 * az[1]
    return k * hi2 + 2 * az[0], k * lo2 + 2 * az[1]


def log2_of_rat_iv(y, ln2iv, N):
    a, b = ln_of_rat_iv(y, ln2iv, N)
    return a / ln2iv[1], b / ln2iv[0]


def exp_iv(x_lo, x_hi, N, K):
    def pos(a, b):
        a, b = snap_lo(a), snap_hi(b)
        y_lo, y_hi = a / F(2) ** K, b / F(2) ** K
        slo, term = F(0), F(1)
        for n in range(N + 1):
            slo += term
            term = term * y_lo / (n + 1)
            if n % 6 == 5:
                slo, term = snap_lo(slo), snap_lo(term)
        shi, term = F(0), F(1)
        for n in range(N + 1):
            shi += term
            term = term * y_hi / (n + 1)
            if n % 6 == 5:
                shi, term = snap_hi(shi), snap_hi(term)
        tail = snap_hi(term / (1 - y_hi / (N + 2)))
        a2, b2 = snap_lo(slo), snap_hi(shi + tail)
        for _ in range(K):
            a2, b2 = snap_lo(a2 * a2), snap_hi(b2 * b2)
        return a2, b2
    if x_lo >= 0:
        return pos(x_lo, x_hi)
    if x_hi <= 0:
        a, b = pos(-x_hi, -x_lo)
        return 1 / b, 1 / a
    a, b = pos(F(0), -x_lo)
    c, d = pos(F(0), x_hi)
    return 1 / b, d


def pow_rat_iv(base, e_lo, e_hi, ln2iv, N, K):
    a, b = ln_of_rat_iv(base, ln2iv, N)
    cs = [e_lo * a, e_lo * b, e_hi * a, e_hi * b]
    return exp_iv(min(cs), max(cs), N, K)


# #################### 常数 ####################
X0 = 695 * 2 ** 60
R2C = F(162 * X0, 97)
N_S, N_E, K_E = 90, 78, 14

p("#" * 72)
p("# route1_c_recheck.py：C 值伪值判定与第三项量级的独立重算")
p("# python %s ；X0 = 695*2^60 = %d" % (sys.version.split()[0], X0))
p("#" * 72)
p("")
p("[0] 严格区间原语自检（用独立严格参照，不用截断打印串）")
e_s, e_t = F(0), F(1)
for n in range(0, 201):
    e_s += e_t
    e_t = e_t / (n + 1)
e_ref = (e_s, e_s + e_t / (1 - F(1, 202)))
p("    e 的独立严格区间（阶乘级数）宽度 = %s" % sci(e_ref[1] - e_ref[0], 3))
ee = exp_iv(F(1), F(1), N_E, K_E)
p("    exp_iv([1,1]) 含该严格区间？ %s（exp_iv 区间宽度 %s）"
  % (ee[0] <= e_ref[0] and e_ref[1] <= ee[1], sci(ee[1] - ee[0], 3)))
ln2A = ln2_atanh_iv(N_S)
ln2B = ln2_series_iv(N_S + 260)
ab = inter(ln2A, ln2B)
p("    ln2 两法（atanh 与对数级数）相交非空？ %s ；宽度 %s" % (ab is not None, sci(ab[1] - ab[0], 3)))
ln2iv = ab
p("    2^C = (162/97)*X0 = %d/%d（C 定义式，精确有理）" % (R2C.numerator, R2C.denominator))

p("")
p("[1] C = log2((162/97)*X0) 的三套互相不同的分解")
CA = log2_of_rat_iv(R2C, ln2A, N_S)
d3 = log2_of_rat_iv(F(3), ln2A, N_S)
c695 = log2_of_rat_iv(F(695, 97), ln2A, N_S)
CB = (61 + 4 * d3[0] + c695[0], 61 + 4 * d3[1] + c695[1])
CCr = log2_of_rat_iv(F(56295, 97), ln2B, N_S)
CC = (61 + CCr[0], 61 + CCr[1])
for tag, iv in (("A 直接 log2((162/97)X0)", CA),
                ("B 61+4log2(3)+log2(695/97)", CB),
                ("C 61+log2(56295/97)（ln2 走对数级数）", CC)):
    p("    %-34s 宽度 %s ；C ∈ [%s," % (tag, sci(iv[1] - iv[0], 3), dec(iv[0], 55)))
    p("    %-34s            %s]" % ("", dec(iv[1], 55)))
tri = inter(inter(CA, CB), CC)
assert tri is not None
C_lo, C_hi = tri
Cmid = (C_lo + C_hi) / 2
p("    三套交集 C ∈ [%s," % dec(C_lo, 55))
p("                  %s]  宽度 %s" % (dec(C_hi, 55), sci(C_hi - C_lo, 3)))

p("")
p("[2] 与三件对照物的比较（显示包络 + 吻合度两套口径）")
R5_101 = "70.1808063283083640726545127109"
x101 = dec_to_F(R5_101)
env101 = (x101 - F(1, 10 ** 28), x101 + F(1, 10 ** 28))
p("    (2a) route-5.md:101 串 = %s ；自称严格区间宽 7.9e-99" % R5_101)
p("         判据 P_a：显示包络（±1e-28）与本轮 C 区间相交？ %s" % (inter(tri, env101) is not None))
p("         真值中点与该串之差 = %s" % sci(abs(Cmid - x101), 8))
p("           = 显示分辨率 1e-28 的 %s 倍 ；= 自称宽度的 %s 倍"
  % (sci(abs(Cmid - x101) * F(10) ** 28, 3), sci(abs(Cmid - x101) / F(79, 10 ** 100), 3)))
p("         本轮 C 的前 32 位小数 = %s" % dec(C_lo, 32))
p("         :101 串补零后的前 32 位小数 = %s0000" % R5_101)
p("         扰动实例 A1：换成 cert.log:9 串的包络后 P_a = %s"
  % (inter(tri, (dec_to_F("70.1808063283083668248487894995") - F(1, 10 ** 28),
                 dec_to_F("70.1808063283083668248487894995") + F(1, 10 ** 28))) is not None))
p("         扰动实例 A2：把 :101 串加 3e-15 后 P_a = %s"
  % (inter(tri, (x101 + F(3, 10 ** 15) - F(1, 10 ** 28), x101 + F(3, 10 ** 15) + F(1, 10 ** 28))) is not None))

CERT9 = "70.1808063283083668248487894995"
x9 = dec_to_F(CERT9)
env9 = (x9 - F(1, 10 ** 28), x9 + F(1, 10 ** 28))
p("    (2b) c2r5_cert.log:9 串 = %s" % CERT9)
p("         判据 P_b1：显示包络与本轮 C 区间相交？ %s" % (inter(tri, env9) is not None))
p("         判据 P_b2：本轮 C 下界的 28 位小数截断 == 该串？ %s" % (dec(C_lo, 28) == CERT9))
p("         真值中点与该串之差 = %s（< 1e-28，即该串是本轮值的 28 位小数截断）" % sci(abs(Cmid - x9), 8))
p("         诚实边界：cert.log 只显示 31 位数字，其自称的 7.9e-99 宽度本脚本无法用显示串核验；")
p("         本判据只能核到显示分辨率（结论是「与该日志一致，不构成反例」）。")
p("         扰动实例 B1：该串末位减 1 后 P_b1 = %s ；P_b2 = %s"
  % (inter(tri, (x9 - F(1, 10 ** 28) - F(1, 10 ** 28), x9 - F(1, 10 ** 28) + F(1, 10 ** 28))) is not None,
     dec(C_lo, 28) == CERT9[:-1] + "4"))

p("    (2c) float64 侧")
CLAIM_F64 = dec_to_F("70.180806328308364072654512710869312286376953125")
cands = [
    ("log2(162/97*695*2**60)", lambda: math.log2(162 / 97 * 695 * 2 ** 60)),
    ("log2((162/97)*(695*2**60))", lambda: math.log2((162 / 97) * (695 * 2 ** 60))),
    ("log2(162*695*2**60/97)", lambda: math.log2(162 * 695 * 2 ** 60 / 97)),
    ("log(162/97*695*2**60)/log(2)", lambda: math.log(162 / 97 * 695 * 2 ** 60) / math.log(2)),
    ("log2(162/97)+60+log2(695)", lambda: math.log2(162 / 97) + 60 + math.log2(695)),
    ("log2(162/97)+log2(695*2**60)", lambda: math.log2(162 / 97) + math.log2(695 * 2 ** 60)),
    ("log2(112590/97)+60", lambda: math.log2(112590 / 97) + 60),
    ("log2(112590*2**60/97)", lambda: math.log2(112590 * 2 ** 60 / 97)),
    ("log2(162*695*2**60)-log2(97)", lambda: math.log2(162 * 695 * 2 ** 60) - math.log2(97)),
]
hits = []
for name, fn in cands:
    v = fn()
    if F(*v.as_integer_ratio()) == CLAIM_F64:
        hits.append(name)
p("         与 route-4.md:82 至 :86 的精确二进制值相等的候选表达式数 = %d / %d"
  % (len(hits), len(cands)))
p("         对照值本身是 float64 可表示值？ %s" % (float(CLAIM_F64) == CLAIM_F64))
f64 = float(math.log2(162 / 97 * 695 * 2 ** 60))
r28 = round_dec(CLAIM_F64, 28)
p("         判据 P_c：该 double 精确值四舍五入到 28 位小数 == :101 串 ？ %s" % (r28 == x101))
p("         四舍五入结果 = %s ；%s" % (dec(r28, 28), hits[0] if hits else ""))
p("         扰动实例 C1：把 :101 串末位 9 改 8 后 P_c = %s" % (r28 == dec_to_F(R5_101[:-1] + "8")))
p("         真值中点与该 double 之差 = %s ；:101 与该 double 之差 = %s ulp（1 ulp = 2^-46）"
  % (sci(abs(Cmid - CLAIM_F64), 8), sci(abs(x101 - CLAIM_F64) * F(2 ** 46), 3)))

p("")
p("[3] 门槛处相邻档差分解：第三加项与两顶残差（M = 88、89、90）")
t = F(97, 162 * X0)
p("    3t == 97/(54X0)（精确恒等式）？ %s" % (3 * t == F(97, 54 * X0)))
P1 = 3 * t * t / (1 - t)
p("    P1 := 3t^2/(1-t) = %s（精确有理，与 M 无关）" % sci(P1, 25))
p("    3/(2^C-1) - 97/(54X0) == P1（精确）？ %s" % (3 / (R2C - 1) - F(97, 54 * X0) == P1))
W0 = R2C - 1
lnW0 = ln_of_rat_iv(W0, ln2iv, N_S)
lnR = ln_of_rat_iv(R2C, ln2iv, N_S)
BASEC = exp_iv(-d3[1] * lnW0[1], -d3[0] * lnW0[0], N_E, K_E)
p("    (2^C-1)^{-delta} = %s（区间宽 %s）" % (sci(BASEC[0], 25), sci(BASEC[1] - BASEC[0], 3)))
rows = []
lg10 = log2_of_rat_iv(F(10), ln2iv, N_S)
for M in (88, 89, 90):
    rho = (F(M - 1, M) * (d3[0] ** M - 1) / (d3[1] ** (M - 1) - 1),
           F(M - 1, M) * (d3[1] ** M - 1) / (d3[0] ** (M - 1) - 1))
    T3new = (3 * (M - 1) * BASEC[0], 3 * (M - 1) * BASEC[1])
    p2 = pow_rat_iv(R2C, rho[0], rho[1], ln2iv, N_S, N_E)
    T2old = (3 / (p2[1] - 1), 3 / (p2[0] - 1))
    lnV = (ln_of_rat_iv(p2[0] - 1, ln2iv, N_S)[0], ln_of_rat_iv(p2[1] - 1, ln2iv, N_S)[1])
    ex2 = exp_iv(-d3[1] * lnV[1], -d3[0] * lnV[0], N_E, K_E)
    T3old = (3 * (M - 2) * ex2[0], 3 * (M - 2) * ex2[1])
    G0 = (P1 + T3new[0] - T2old[1] - T3old[1], P1 + T3new[1] - T2old[0] - T3old[0])
    ratio = (T3new[0] / P1, T3new[1] / P1)
    l10 = (log2_of_rat_iv(ratio[0], ln2iv, N_S)[0] / lg10[1],
           log2_of_rat_iv(ratio[1], ln2iv, N_S)[1] / lg10[0])
    rows.append(dict(M=M, rho=rho, T3new=T3new, T2old=T2old, T3old=T3old, G0=G0,
                     ratio=ratio, l10=l10))
    p("    M = %d：rho = %s" % (M, dec(rho[0], 20)))
    p("        T3new ∈ [%s," % sci(T3new[0], 25))
    p("                  %s]" % sci(T3new[1], 25))
    p("        T2old ∈ [%s, %s]" % (sci(T2old[0], 25), sci(T2old[1], 25)))
    p("        T3old ∈ [%s, %s]" % (sci(T3old[0], 25), sci(T3old[1], 25)))
    p("        G0    ∈ [%s, %s] ；T3new > T2old+P1+T3old ？ %s"
      % (sci(G0[0], 25), sci(G0[1], 25), T3new[0] > T2old[1] + P1 + T3old[1]))
    p("        T3new/P1 ∈ [%s, %s] ；log10 = %s（8 位小数）"
      % (sci(ratio[0], 20), sci(ratio[1], 20), dec(l10[0], 8)))
M90 = rows[2]

p("")
p("[4] 记账串的吻合度（判据：相对差 <= 10^-(有效位数-1)）")


def agree(iv, s, sig, exp10):
    v = dec_to_F(s) * F(10) ** exp10
    rel = abs(iv[0] - v) / v
    return rel, rel <= F(1, 10 ** (sig - 1))


checks = [
    ("route-1.md:10 的 8.74494110107e-32（M=90）", M90["T3new"], "8.74494110107", 12, -32),
    ("audit_c.out 的 8.7449411010749152029e-32", M90["T3new"], "8.7449411010749152029", 20, -32),
    ("route-1.md 的 P1 = 1.67519591503459e-42", (P1, P1), "1.67519591503459", 15, -42),
    ("route-1.md 的 T2old = 2.31430028313e-33（M=90）", M90["T2old"], "2.31430028313", 12, -33),
    ("route-1.md 的 G0 = 8.51351107293e-32（M=90）", M90["G0"], "8.51351107293", 12, -32),
    ("route-1.md 的比值 5.2202498e10", M90["ratio"], "5.2202498", 8, 10),
]
for tag, iv, s, sig, ex in checks:
    rel, ok = agree(iv, s, sig, ex)
    p("    %-52s 相对差 = %-11s 判据 = %s" % (tag, sci(rel, 3), ok))
p("    route-1.md:10 的 10.7177（4 位小数）：|log10 - 10.7177| = %s <= 5e-5 ？ %s"
  % (dec(abs(M90["l10"][0] - F(107177, 10000)), 10),
     abs(M90["l10"][0] - F(107177, 10000)) <= F(5, 10 ** 5)))
p("    扰动实例 D1：把 10.7177 改 10.7176 后同一判据 = %s"
  % (abs(M90["l10"][0] - F(107176, 10000)) <= F(5, 10 ** 5)))
p("    扰动实例 D2：把 audit 串末位加 1（…152030）后 20 位判据 = %s"
  % agree(M90["T3new"], "8.7449411010749152030", 20, -32)[1])
p("")
p("[5] 本脚本结论")
p("    (5.1) :101 的 C 串与真值差 %s" % sci(abs(Cmid - x101), 8))
p("          = 显示分辨率 1e-28 的 %s 倍 ；= 其自称宽度 7.9e-99 的 %s 倍"
  % (sci(abs(Cmid - x101) * F(10) ** 28, 3), sci(abs(Cmid - x101) / F(79, 10 ** 100), 3)))
p("          故任何宽度 7.9e-99、端点显示为该串的区间都不可能含 C：:101 的「严格区间」是伪区间。")
p("    (5.2) :101 串 == 该 double 精确值的 28 位小数四舍五入 ？ %s（%d / %d 条候选表达式同值）"
  % (r28 == x101, len(hits), len(cands)))
p("    (5.3) v = C、m2 = 90 处第三加项 = %s，" % sci(M90["T3new"][0], 25))
p("          是 P1 = %s 的 %s 倍，log10 = %s（4 位小数口径 10.7177 判据 = %s）"
  % (sci(P1, 25), sci(M90["ratio"][0], 20), dec(M90["l10"][0], 8),
     abs(M90["l10"][0] - F(107177, 10000)) <= F(5, 10 ** 5)))

path = ("/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/d3-window-tail/"
        "cycle-1/scripts/results/route1_c_recheck.out")
import pathlib as _pl
_pl.Path(path).write_text("\n".join(OUT) + "\n", encoding="utf-8")
print("\n[写出] " + path)
