#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify.py —— 轨道 d3-window-tail 第 1 轮（cycle-1）六条增量结论的自足复算脚本。

运行方式与覆盖范围
------------------
1. 默认档：python3 verify.py
   覆盖：增量一（核心自检、三档 u* 的 130 步严格二分括号、37 位与 22 位前缀、
   c_j 区间相对宽、含于 route-3 与 r4b2 端点）；增量二（float64 精确值与 28 位小数
   两种舍入口径、C 真值与转述串之差、P1 精确有理恒等式、第三项与比值、convsplit
   只读审计）；增量三（j = 91、92 半直线上界、j = 2 至 90 的 D_j(10^-12) 全档定号、
   统一界与临界 j、c_90(1+1e-12) 对 K*、c_92 对 K_cross 下端、T 下界、K* 落段）；
   增量四（全部 j = 2 至 92 门槛处定号）；增量五（u* 前缀、K 侧绝对宽、两个相对余量）；
   增量六（route-3、r4b2、MPFR 端点的 Φ 符号、量级与区间包含）；
   深档链代表性子集 M ∈ {2, 3, 25, 45, 90, 91, 92}。
2. 深度档：python3 verify.py --deep
   在默认档之上，把深档链跑满全部 M = 2 至 92（默认档只跑代表性子集），并核最小步长。
3. 可选档：python3 verify.py --mpmath
   另做「δ、C、lnQ 与 mpmath dps = 80 的 50 位打印逐字对照」（mpmath 导入在本机约一分钟）。

自足性与禁止项
--------------
本脚本只用标准库（fractions、math、hashlib、re、os）。所有区间由本文件自带的
定点定向舍入核心给出（格距 10^-90，级数逐项向外取整并加显式尾界），不 import
项目任何模块。脚本运行时不读取 route-*.md 与 materials.md，也不读取任何本轮结论
文件；唯一读盘是对 70-research/cycle-2/scripts/results/c2r5_convsplit.out 的
只读审计（增量二(iii) 的核验对象本身）。

外部对照端点（嵌入为测试向量，运行时不读取这些文件）
----------------------------------------------------
A. route-3 独立二分的窗口右端精确有理端点 K1_88 至 K1_90，取自本轮 route-3 产物
   scripts/results/d3r3_windows.json（该文件是独立实现（整数定点二分）的输出，
   仅作对照向量引用）。
B. r4b2 的窗口右端 48 位括号与门槛 50 位打印串，取自兄弟轨道
   tracks/kcross-proof/cycle-1/scripts/results/r4b2_window_probe.out 的 [2] 节。
C. MPFR 下端串，取自同一兄弟轨道产物（r4b2_window_probe.out 与 route-3 的
   d3r3_conflict.out 均引用）。
D. K_cross 下端串，取自 cycle-2 产物 scripts/results/c2r5_cert.log 第 67 行（[5] 节）；
   T 下界 3.131547906e20 为本轮增量转述值（原出处为 cycle-2 侧，本脚本未回原件，
   只对「c_92 上界 < 该下界」做严格比较）。

等级声明（诚实边界）
--------------------
本脚本给出的区间是严格包含：一切取值向外取整并附显式尾界，前提是本文件的区间核心
实现正确。未形式化、未经第三方复核。凡增量中只能靠读文件核对的子结论（route-1、
route-2、route-4 的括号、账本文本、可引条目文本等），在对应位置以注释标明
「无法机器验证」并跳过。

判定口径
--------
实质断言（符号、包含关系、逐位一致到给定精度、精确有理恒等式、文件审计计数等）判
通过或失败；若失败，退出码 1 并打印最小反例。增量转述数字与重算值只相差 10 的整数
次幂（指数显示层滑落，尾数一致）一类情形记警告并打印对照，不计失败：本轮增量的
Φ 端点转述值中有四处此类滑落（增量一两处、增量六两处；详见运行输出末尾的警告清单）。

退出码：0 表示全部实质断言通过（警告另行打印）；
        1 表示有断言失败（打印最小反例）。
"""

import sys
import os
import re
import math
import time
import hashlib
from fractions import Fraction as F

# ============================================================ 常量与口径
X0 = 695 * 2 ** 60                      # 印出版口径 695·2^60
NUMQ = 162 * X0                         # Q = 2^C = 162X0/97（精确有理）
KSTAR = 205632218873398596256           # K*（精确整数）
F0 = F(1, 10 ** 12)                     # 窗口右端的相对宽包络基准
SC = 10 ** 90                           # 定点格距

# ============================================================ 定点区间核心
# 区间 (lo, hi) 表示 [lo/SC, hi/SC]，lo、hi 为整数。所有运算向外取整。


def fl(n, d):
    """n/d 的下取整（floor），d != 0。"""
    if d < 0:
        n, d = -n, -d
    return n // d


def cl(n, d):
    """n/d 的上取整（ceil），d != 0。"""
    if d < 0:
        n, d = -n, -d
    return -((-n) // d)


def iv_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def iv_sub(a, b):
    return (a[0] - b[1], a[1] - b[0])


def iv_neg(a):
    return (-a[1], -a[0])


def iv_mul(a, b):
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (fl(min(p), SC), cl(max(p), SC))


def iv_div(a, b):
    assert b[0] > 0, ("除数必须严格为正", b)
    return (fl(a[0] * SC, b[1]), cl(a[1] * SC, b[0]))


def iv_int(k):
    return (k * SC, k * SC)


def iv_mul_int(a, k):
    if k >= 0:
        return (a[0] * k, a[1] * k)
    return (a[1] * k, a[0] * k)


def iv_div_int(a, k):
    assert k > 0
    return (fl(a[0], k), cl(a[1], k))


def iv_from_frac(q):
    return (fl(q.numerator * SC, q.denominator), cl(q.numerator * SC, q.denominator))


def iv_span_frac(qlo, qhi):
    """区间 [qlo, qhi]（精确有理端点）的向外取整表示。"""
    return (fl(qlo.numerator * SC, qlo.denominator), cl(qhi.numerator * SC, qhi.denominator))


def iv_pow_int(a, n):
    """a 的 n 次幂（n >= 0，a > 0），逐次向外取整。"""
    r = iv_int(1)
    b = a
    while n:
        if n & 1:
            r = iv_mul(r, b)
        b = iv_mul(b, b)
        n >>= 1
    return r


_LN_TERMS = 120


def _atanh_iv(z):
    """z ∈ [0, 1/3] 为精确有理数；返回 atanh(z) 的严格区间（按 SC 缩放）。"""
    zlo = fl(z.numerator * SC, z.denominator)
    zhi = cl(z.numerator * SC, z.denominator)
    z2lo = fl(zlo * zlo, SC)
    z2hi = cl(zhi * zhi, SC)
    lo = 0
    hi = 0
    plo, phi = zlo, zhi
    for i in range(_LN_TERMS):
        lo += fl(plo, 2 * i + 1)
        hi += cl(phi, 2 * i + 1)
        plo = fl(plo * z2lo, SC)
        phi = cl(phi * z2hi, SC)
    # 尾界：sum_{i>=n} z^(2i+1)/(2i+1) <= z^(2n+1)/((2n+1)(1-z^2))
    n = _LN_TERMS
    rem = cl(phi * SC * SC, (2 * n + 1) * (SC * SC - z2hi))
    return (lo, hi + rem)


# ln2 = 2 atanh(1/3)
LN2 = iv_mul_int(_atanh_iv(F(1, 3)), 2)


def ln_frac(num, den):
    """精确有理数 num/den > 0 的 ln 严格区间。"""
    assert num > 0 and den > 0
    k = num.bit_length() - den.bit_length()
    while True:
        if k >= 0:
            ok_lo = num >= (den << k)
            ok_hi = num < (den << (k + 1))
        else:
            ok_lo = (num << (-k)) >= den
            ok_hi = (num << (-k - 1)) < den
        if ok_lo and ok_hi:
            break
        k += -1 if not ok_lo else 1
    m = F(num, den << k) if k >= 0 else F(num << (-k), den)
    assert F(1) <= m < 2
    z = (m - 1) / (m + 1)
    at = _atanh_iv(z)
    return iv_add(iv_mul_int(at, 2), iv_mul_int(LN2, k))


def ln_iv(a):
    """区间 a（各端点为格上整数）上的 ln 的严格区间：对两端分别取 ln 再取单调包络。"""
    assert a[0] > 0
    return (ln_frac(a[0], SC)[0], ln_frac(a[1], SC)[1])


_EXP_TERMS = 90


def _exp_small(rlo, rhi):
    """exp 在 [rlo/SC, rhi/SC]（0 <= r <= 1）上的严格区间。"""
    lo = SC
    hi = SC
    plo = phi = SC
    for i in range(1, _EXP_TERMS):
        plo = fl(plo * rlo, SC * i)
        phi = cl(phi * rhi, SC * i)
        lo += plo
        hi += phi
    n = _EXP_TERMS
    # 尾界：sum_{i>=n} r^i/i! <= (r^n/n!)·(n+1)/(n+1-r)
    rem = cl(phi * rhi * (n + 1), n * ((n + 1) * SC - rhi))
    return (lo, hi + rem)


def exp_iv(x):
    """区间 x 上 exp 的严格区间（x 为按 SC 缩放的区间）。"""
    k = fl(x[0], LN2[1])
    while k * LN2[1] > x[0]:
        k -= 1
    while x[1] - k * LN2[0] > SC:
        k += 1
    while k * LN2[1] > x[0]:
        k -= 1
    rlo = x[0] - k * LN2[1]
    rhi = x[1] - k * LN2[0]
    assert rlo >= 0 and rhi <= SC, ("exp 归约区间超出 [0,1]", rlo, rhi)
    e = _exp_small(rlo, rhi)
    if k >= 0:
        s = 1 << k
        return (e[0] * s, e[1] * s)
    s = 1 << (-k)
    return (fl(e[0], s), cl(e[1], s))


def pow_neg_delta_ub(xlo_int):
    """(x)^(-delta) 的上界，x = xlo_int/SC（x 区间只用下端点取上界）。"""
    L = ln_frac(xlo_int, SC)
    return exp_iv(iv_neg(iv_mul(DELTA, L)))[1]


# ============================================================ 十进制打印与字串
def digs(q, sig):
    """正有理数 q 的 sig 位有效数字（向零截断），返回纯数字串。"""
    assert q > 0
    num, den = q.numerator, q.denominator
    e = len(str(num)) - len(str(den))
    while num >= den * 10 ** e:
        e += 1
    while num < den * 10 ** (e - 1):
        e -= 1
    if sig - e >= 0:
        d = (num * 10 ** (sig - e)) // den
    else:
        d = num // (den * 10 ** (e - sig))
    s = str(d)
    if len(s) < sig:
        s = s + '0' * (sig - len(s))
    return s


def dec(q, sig=24):
    """有理数 q 的十进制科学记数法串（sig 位有效数字，向零截断，标准指数口径）。"""
    if q == 0:
        return "0"
    neg = q < 0
    qa = -q if neg else q
    num, den = qa.numerator, qa.denominator
    e = len(str(num)) - len(str(den))
    while num >= den * 10 ** e:
        e += 1
    while num < den * 10 ** (e - 1):
        e -= 1
    if sig - e >= 0:
        d = (num * 10 ** (sig - e)) // den
    else:
        d = num // (den * 10 ** (e - sig))
    s = str(d)
    if len(s) < sig:
        s = s + '0' * (sig - len(s))
    return ('-' if neg else '') + s[0] + '.' + s[1:] + 'e' + str(e - 1)


def iv_str(a, sig=24):
    return "[" + dec(F(a[0], SC), sig) + ", " + dec(F(a[1], SC), sig) + "]"


def sci(s):
    """十进制科学记数法串 -> 精确 Fraction。"""
    s = s.strip()
    if 'e' in s or 'E' in s:
        mant, ex = re.split('[eE]', s)
    else:
        mant, ex = s, '0'
    ip, _, fp = mant.partition('.')
    digits = (ip + fp) or '0'
    q = F(int(digits), 10 ** len(fp))
    e = int(ex)
    return q * (10 ** e) if e >= 0 else q / (10 ** (-e))


# ============================================================ 断言框架
FAILS = []
WARNS = []
NCHECK = 0


def check(name, ok, detail=""):
    global NCHECK
    NCHECK += 1
    print(("[PASS] " if ok else "[FAIL] ") + name + (("　——　" + detail) if detail else ""))
    if not ok:
        FAILS.append((name, detail))


def warn(msg):
    WARNS.append(msg)
    print("[WARN] " + msg)


def section(tag, title):
    print("\n" + "=" * 10 + " [" + tag + "] " + title + " " + "=" * 10)


def exp_slip_check(name, mine, quoted, tag=""):
    """把「重算值 / 转述值」按数量级分类：同位数量级记通过；只差 10 的整数次幂记警告。"""
    if mine == 0 or quoted == 0:
        check(name, False, "零值无法比较")
        return
    r = abs(float(mine) / float(quoted))
    lg = math.log10(r)
    if abs(lg) < 0.02:
        check(name, True, "重算与转述同数量级（比值 %.6f）" % r)
    else:
        k = round(lg)
        if abs(lg - k) < 0.02 and k != 0:
            warn(name + "：转述值的指数与重算相差 10 的 %d 次幂（显示层滑落；转述 %s，重算 %s）%s"
                 % (k, dec(F(quoted), 12), dec(F(mine), 12), tag))
            check(name + "（尾数一致，指数记警告）", True,
                  "尾数一致、指数滑落 10 的 %d 次幂" % k)
        else:
            check(name, False, "重算 %s 与转述 %s 比值 %.6g" % (dec(F(mine), 12), dec(F(quoted), 12), r))


def fix(q, nd):
    """有理数 q 的定点十进制串（nd 位小数，向零截断）。"""
    neg = q < 0
    qa = -q if neg else q
    scaled = (qa.numerator * 10 ** nd) // qa.denominator
    ip, fp = divmod(scaled, 10 ** nd)
    return ("-" if neg else "") + str(ip) + "." + str(fp).rjust(nd, "0")


# ============================================================ 数学层
LNQ = ln_frac(NUMQ, 97)
DELTA = iv_div(ln_frac(3, 1), LN2)
C_IV = iv_div(LNQ, LN2)
ONE = iv_int(1)
QM1 = F(NUMQ - 97, 97)                  # 2^C - 1 的精确有理值

_DPOW = {}


def delta_pow(j):
    if j not in _DPOW:
        _DPOW[j] = iv_pow_int(DELTA, j)
    return _DPOW[j]


def v_iv(m2, K):
    """v(m2,K) = (m2/92)·K·(delta-1)/(delta^m2 - 1) 的严格区间。"""
    dm2 = iv_sub(delta_pow(m2), ONE)
    v = iv_mul(iv_mul(iv_mul_int(K, m2), iv_sub(DELTA, ONE)), iv_div(ONE, dm2))
    return iv_div_int(v, 92)


def N_iv(m2, K):
    """分子 N(m2,K) = A(m2) + 3/(2^v-1) + 3(m2-1)/(2^v-1)^delta 的严格区间。"""
    v = v_iv(m2, K)
    two_v = exp_iv(iv_mul(v, LN2))
    tm1 = iv_sub(two_v, ONE)
    assert tm1[0] > 0, ("2^v - 1 必须严格为正", tm1)
    t2 = iv_div((3 * SC, 3 * SC), tm1)
    lnt = ln_iv(tm1)
    t3 = iv_mul_int(exp_iv(iv_neg(iv_mul(DELTA, lnt))), 3 * (m2 - 1))
    if m2 == 92:
        A = (0, 0)
    elif m2 == 91:
        A = iv_from_frac(F(3, X0))
    else:
        A = iv_from_frac(F(97 * (92 - m2) + 73, 54 * X0))
    return iv_add(A, iv_add(t2, t3))


def Phi_iv(M, K):
    """Phi_M(K) = N(M,K) - N(M-1,K)。"""
    return iv_sub(N_iv(M, K), N_iv(M - 1, K))


def c_j_iv(j):
    """门槛 K_th(j) = (92/j)·geom(j)·C 的严格区间。"""
    g = iv_div(iv_sub(delta_pow(j), ONE), iv_sub(DELTA, ONE))
    return iv_mul(iv_mul_int(g, 92), iv_div(C_IV, (j * SC, j * SC)))


def D_j(j, f):
    """D_j(f) = Phi_j(c_j·(1+f))（f 为 Fraction），用闭形式避免重算 c_j。"""
    x = iv_from_frac(1 + f)
    u = iv_mul(LNQ, x)
    t = exp_iv(u)
    tm1 = iv_sub(t, ONE)
    T2j = iv_div((3 * SC, 3 * SC), tm1)
    lnt = ln_iv(tm1)
    T3j = iv_mul_int(exp_iv(iv_neg(iv_mul(DELTA, lnt))), 3 * (j - 1))
    rho = iv_mul(iv_div(iv_sub(delta_pow(j), ONE), iv_sub(delta_pow(j - 1), ONE)),
                 iv_from_frac(F(j - 1, j)))
    u2 = iv_mul(iv_mul(rho, x), LNQ)
    s = exp_iv(u2)
    sm1 = iv_sub(s, ONE)
    T2p = iv_div((3 * SC, 3 * SC), sm1)
    lns = ln_iv(sm1)
    T3p = iv_mul_int(exp_iv(iv_neg(iv_mul(DELTA, lns))), 3 * (j - 2))
    Ast = iv_from_frac(F(-97, 54 * X0))
    return iv_add(Ast, iv_sub(iv_add(T2j, T3j), iv_add(T2p, T3p)))


def bisect_u(j, steps=130):
    """在 [0, 1e-12] 上做 steps 步严格二分，返回 (lo, hi, 未定步数)。"""
    lo, hi = F(0), F0
    d0 = D_j(j, lo)
    d1 = D_j(j, hi)
    assert d0[0] > 0 and d1[1] < 0, ("端点符号反例", j, d0, d1)
    und = 0
    for _ in range(steps):
        mid = (lo + hi) / 2
        dm = D_j(j, mid)
        if dm[0] > 0:
            lo = mid
        elif dm[1] < 0:
            hi = mid
        else:
            und += 1
    return lo, hi, und


# ============================================================ 外部对照向量
# A. route-3 独立二分（本轨 scripts/results/d3r3_windows.json 的 K1_88 至 K1_90）
K1R3 = {
    88: (F("39374113918870180240978705656/785496143"), F("17862900969637302849771785195/356356967")),
    89: (F("721541186073145926909503781517/9185075539"), F("456339170142841923249741721234/5809106715")),
    90: (F("31069780769808963182310536489/252344188"), F("253404555694983006473081192673/2058114517")),
}
# B. r4b2（兄弟轨道 kcross-proof 产物 r4b2_window_probe.out 的 [2] 节）
R4B2 = {
    89: (F("78555824936819382091.475309577063948109807001"),
         F("78555824936819382091.475309709629966165890197")),
    90: (F("123124614107652692133.007231711933058876044901"),
         F("123124614107652692133.007231919710646726095849")),
}
R4B2_C = {
    89: "78555824936758779275.265552681458057901548946328722",
    90: "123124614107556571561.827996023727480573234158995835",
}
# C. MPFR 下端串
MPFR_LO = F("123124614107652692133.0072322914378057066853155987473655841313302516937255859375")
# D. K_cross 下端串（cycle-2 产物 c2r5_cert.log 第 67 行 [5] 节）
KCROSS_LO = F("313195478959172262876.6365306194907065260231016940260118526233")
# 增量转述的窗口值（37 位）与 T 下界
USTAR37 = {
    88: "7622396965265262225804740254338679074",
    89: "7714617758586982140404811955329781889",
    90: "7806771365412671715788394707855134401",
}
T_LO = sci("3.131547906e20")
CONVSPLIT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "..", "..", "cycle-2", "scripts", "results", "c2r5_convsplit.out")


# ============================================================ 增量一
def inc1():
    section("一", "增量一：三档窗口两端严格有理区间证书（含 j = 88）")

    # 核心自检：两条强判据（exp(ln2) 含 2；exp(lnQ) 含精确有理 Q）
    e2 = exp_iv(LN2)
    ok2 = F(e2[0], SC) <= F(2) <= F(e2[1], SC)
    check("[1.1] 核心：exp(ln2) 含精确整数 2（严格）", ok2, "exp(ln2) ∈ " + iv_str(e2, 22))
    eQ = exp_iv(LNQ)
    Q = F(NUMQ, 97)
    okQ = F(eQ[0], SC) <= Q <= F(eQ[1], SC)
    check("[1.2] 核心：exp(lnQ) 含精确有理 Q = 162X0/97（严格）", okQ,
          "exp(lnQ) ∈ " + iv_str(eQ, 22))
    # C 双路径互交与转述 53 位串
    C2 = iv_add(iv_int(60), iv_div(ln_frac(112590, 97), LN2))
    inter = (max(C_IV[0], C2[0]), min(C_IV[1], C2[1]))
    check("[1.3] 核心：C 的两条独立路径区间相交非空", inter[0] <= inter[1],
          "交集 " + iv_str(inter, 24))
    c53 = F("70.18080632830836682484878949951987923274357748761288488")
    d53 = abs(c53 - F(C_IV[0] + C_IV[1], 2 * SC))
    check("[1.4] C 区间中点与增量转述的 53 位真值串一致到绝对 1e-52", d53 < F(1, 10 ** 52),
          "|中点 - 串| = " + dec(d53, 3) + "；C ∈ " + iv_str(C_IV, 30))

    # 左端 c_j 区间相对宽与 r4b2 打印串对照
    for j in (88, 89, 90):
        cj = c_j_iv(j)
        w = F(cj[1] - cj[0], cj[0])
        check("[1.5] c_%d 严格区间相对宽 < 1e-84（增量称约 6e-86）" % j, w < F(1, 10 ** 84),
              "相对宽 " + dec(w, 6) + "；c_%d ∈ " % j + iv_str(cj, 24))
    c90 = c_j_iv(90)
    s90 = sci(R4B2_C[90])
    check("[1.6] c_90 中点与 r4b2 的 50 位串一致到绝对 1e-28", abs(F(c90[0] + c90[1], 2 * SC) - s90) < F(1, 10 ** 28),
          "|中点 - 串| = " + dec(abs(F(c90[0] + c90[1], 2 * SC) - s90), 3))
    c89 = c_j_iv(89)
    s89 = sci(R4B2_C[89])
    check("[1.7] c_89 中点与 r4b2 的 51 位串一致到绝对 1e-28", abs(F(c89[0] + c89[1], 2 * SC) - s89) < F(1, 10 ** 28),
          "|中点 - 串| = " + dec(abs(F(c89[0] + c89[1], 2 * SC) - s89), 3))

    # 三档 130 步严格二分
    mine = {}
    for j in (88, 89, 90):
        lo, hi, und = bisect_u(j, 130)
        mine[j] = (lo, hi)
        check("[1.8] j=%d：130 步二分全部严格判定（未定步数为 0）" % j, und == 0,
              "未定步数 %d" % und)
        d37lo, d37hi = digs(lo, 37), digs(hi, 37)
        ok37 = (d37lo == USTAR37[j] and d37hi == USTAR37[j])
        check("[1.9] j=%d：括号两端 37 位截断与增量转述串逐字相同" % j, ok37,
              "lo37=%s hi37=%s" % (d37lo, d37hi) + ("" if ok37 else " 期望 " + USTAR37[j]))
        d22 = USTAR37[j][:22]
        ok22 = (digs(lo, 22) == d22 and digs(hi, 22) == d22)
        check("[1.10] j=%d：22 位截断与增量五转述的 22 位值逐字相同" % j, ok22,
              "22 位 " + digs(lo, 22))
        wid = F(hi - lo, 1) / lo
        okw = F(92, 10 ** 41) <= wid <= F(98, 10 ** 41)
        check("[1.11] j=%d：括号相对宽落在 9.2e-40 至 9.8e-40" % j, okw,
              "相对宽 " + dec(wid, 6))
        # 含于 route-3 端点（映射为 f 区间）
        cj = c_j_iv(j)
        r3lo, r3hi = K1R3[j]
        flo = r3lo / F(cj[1], SC) - 1
        fhi = r3hi / F(cj[0], SC) - 1
        ok_in = flo <= lo and hi <= fhi
        check("[1.12] j=%d：我的括号含于 route-3 精确有理端点" % j, ok_in,
              "route-3 对应 f 区间 [" + dec(flo, 24) + ", " + dec(fhi, 24) + "]")
        # 含于 r4b2 括号（仅 j = 89、90 有）
        if j in R4B2:
            r4lo, r4hi = R4B2[j]
            flo4 = r4lo / F(cj[1], SC) - 1
            fhi4 = r4hi / F(cj[0], SC) - 1
            ok_in4 = flo4 <= lo and hi <= fhi4
            check("[1.13] j=%d：我的括号含于 r4b2 的 48 位括号" % j, ok_in4,
                  "r4b2 对应 f 区间 [" + dec(flo4, 24) + ", " + dec(fhi4, 24) + "]")
        print("       j=%d 终端打印：f*_lo = %s，f*_hi = %s" % (j, dec(lo, 40), dec(hi, 40)))

    # 端点处 Φ 的符号与量级；转述指数滑落记警告
    quoted = {(88, 0): "+4.08150657e-43", (88, 1): "-7.19135555e-43",
              (89, 0): "+1.12641311e-42", (89, 1): "-4.19606554e-43",
              (90, 0): "+2.51361056e-41", (90, 1): "-3.14760815e-41"}
    for j in (88, 89, 90):
        for side, K in enumerate(K1R3[j]):
            Piv = Phi_iv(j, iv_from_frac(K))
            sign_ok = (Piv[0] > 0) if side == 0 else (Piv[1] < 0)
            check("[1.14] j=%d %s端：Φ 符号为 %s（严格）" % (j, "左" if side == 0 else "右",
                                                        "+" if side == 0 else "-"), sign_ok,
                  "Φ ∈ " + iv_str(Piv, 12))
            mid = F(Piv[0] + Piv[1], 2 * SC)
            exp_slip_check("[1.15] j=%d %s端：Φ 量级与转述值对照" % (j, "左" if side == 0 else "右"),
                           mid, sci(quoted[(j, side)]))
    # 无法机器验证项（注释登记，跳过）：
    # ・「含于 route-2、route-4 的括号」「比 route-1 的相对宽 1.6e-29 窄若干数量级」：
    #   这些数字在 route-*.md 中，本脚本不读取本轮结论文件，故跳过。
    return mine


# ============================================================ 增量二
def inc2():
    section("二", "增量二：三条否证经逐位复现（C 伪值、第三项主导、convsplit 事实）")

    # (i) C 的 float64 伪值
    f64 = float(math.log2((162 / 97) * X0))
    fq = F(f64)
    fstr = "70.180806328308364072654512710869312286376953125"
    check("[2.1] 重算的 float64 值等于增量转述的精确二进制值",
          fq == F(fstr), "重算 " + dec(fq, 52))
    from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_DOWN
    getcontext().prec = 120
    dv = Decimal(fq.numerator) / Decimal(fq.denominator)
    q28 = Decimal(1).scaleb(-28)
    up = str(dv.quantize(q28, rounding=ROUND_HALF_UP))
    dn = str(dv.quantize(q28, rounding=ROUND_DOWN))
    s101 = "70.1808063283083640726545127109"
    check("[2.2] float64 值四舍五入到 28 位小数与 route-5 串逐字符相等",
          up == s101 and dn != s101, "HALF_UP=%s DOWN=%s" % (up, dn))
    diff = F(C_IV[0] + C_IV[1], 2 * SC) - sci(s101)
    qdiff = sci("2.75219427678861987923274357749e-15")
    check("[2.3] C 真值与 route-5 串之差等于转述的 2.75219427678861987923274357749e-15",
          abs(diff - qdiff) < F(1, 10 ** 44),
          "差 = " + dec(diff, 32) + "；|差 - 转述| = " + dec(abs(diff - qdiff), 3))
    fake = sci("7.9e-99")
    lo_f, hi_f = sci(s101) - fake, sci(s101) + fake
    disjoint = (F(C_IV[1], SC) < lo_f) or (F(C_IV[0], SC) > hi_f)
    check("[2.4] 自称宽 7.9e-99 的闭区间与 C 严格区间不相交（伪区间）", disjoint,
          "C ∈ " + iv_str(C_IV, 24))

    # (ii) 两项残差、第三项、比值
    P1 = F(9409, 54 * X0 * (162 * X0 - 97))
    idn = 3 * F(1, 1) / (F(NUMQ, 97) - 1) - F(97, 54 * X0)
    check("[2.5] P1 的精确有理恒等式 3/(2^C-1) - 97/(54X0) = 9409/(54X0(162X0-97))",
          P1 == idn, "两式相等 = " + str(P1 == idn))
    check("[2.6] P1 与转述的 1.67519591503458701469794551289e-42 一致到 1e-70",
          abs(P1 - sci("1.67519591503458701469794551289e-42")) < F(1, 10 ** 70),
          "P1 = " + dec(P1, 31))
    t3iv = iv_mul_int(exp_iv(iv_neg(iv_mul(DELTA, ln_frac(QM1.numerator, QM1.denominator)))), 267)
    t3mid = F(t3iv[0] + t3iv[1], 2 * SC)
    rel = abs(t3mid / sci("8.74494110107491520289380765652e-32") - 1)
    check("[2.7] 第三项 3·89·(2^C-1)^(-delta) 与转述的 8.74494110107491520289380765652e-32 一致到相对 1e-28",
          rel < F(1, 10 ** 28), "重算 " + dec(t3mid, 31) + "，相对差 " + dec(rel, 3))
    ratio = F(t3iv[0], SC) / P1
    quot_v = sci("5.2202497765130727096e10")
    check("[2.8] 比值与转述的 5.2202497765130727096e10 一致到相对 1e-19",
          abs(ratio / quot_v - 1) < F(1, 10 ** 19), "下界比值 " + dec(ratio, 24))
    lg = (ln_frac(t3iv[0], SC)[0] - ln_frac(P1.numerator, P1.denominator)[1])  # 保守
    lg_v = F(lg, SC) / F(ln_frac(10, 1)[1], SC)
    check("[2.8b] 比值的 log10 与转述的 10.7176912835 一致到 1e-10",
          abs(lg_v - sci("10.7176912835")) < F(1, 10 ** 10), "log10 下界 " + dec(lg_v, 14))

    # (iii) convsplit 只读审计
    path = os.path.normpath(CONVSPLIT)
    if not os.path.exists(path):
        print("[SKIP] convsplit 审计：文件不存在 " + path + "（无法机器验证，跳过）")
        return
    data = open(path, "rb").read()
    text = data.decode("utf-8")
    lines = text.splitlines()
    md5 = hashlib.md5(data).hexdigest()
    check("[2.9] convsplit.out 的 md5 与转述的 39f60fa65a6859f1bd084b5b8beaf38e 相同",
          md5 == "39f60fa65a6859f1bd084b5b8beaf38e", "md5 = " + md5)
    check("[2.10] convsplit.out 行数为 36", len(lines) == 36, "行数 %d" % len(lines))
    nF = sum(1 for s in lines if "分离？ False" in s)
    nT = sum(1 for s in lines if "分离？ True" in s)
    nZ = sum(1 for s in lines if "逐格" in s)
    check("[2.11] 「分离？ False」= 15 且「分离？ True」= 0 且无「逐格」字样",
          nF == 15 and nT == 0 and nZ == 0, "False=%d True=%d 逐格=%d" % (nF, nT, nZ))
    facs = set()
    for s in lines:
        m = re.search(r"K = K_thresh\*([0-9/]+)", s)
        if m:
            facs.add(m.group(1))
    check("[2.12] 采样倍率为 {1, 10001/10000, 2001/2000, 101/100, 21/20}（步长 0、1e-4、5e-4、1e-2、5e-2）",
          facs == {"1", "10001/10000", "2001/2000", "101/100", "21/20"}, "倍率集合 " + str(sorted(facs)))
    blocks = {}
    cur = None
    for s in lines:
        m = re.match(r"m2 = (\d+) 的门槛", s)
        if m:
            cur = int(m.group(1))
            blocks[cur] = None
        if cur is not None and blocks[cur] is None and "K = K_thresh*1 " in s:
            mm = re.search(r"m2_max = (\d+)", s)
            if mm:
                blocks[cur] = int(mm.group(1))
    ok_b = all(blocks.get(M) == M - 1 for M in (88, 89, 90))
    check("[2.13] 门槛行给 m2_max = M - 1（采样点在门槛之下）", ok_b, "门槛行 m2_max = " + str(blocks))
    for s in lines:
        m = re.match(r"m2 = (\d+) 的门槛 K_thresh ∈ \[([0-9.]+)", s)
        if m and int(m.group(1)) == 88:
            check("[2.14] convsplit 的 K_thresh(88) 前 20 位与我的 c_88 区间整数部分一致",
                  m.group(2).split(".")[0] == digs(F(c_j_iv(88)[0], SC), 20)[:20],
                  "文件 " + m.group(2) + "；我的 " + dec(F(c_j_iv(88)[0] + c_j_iv(88)[1], 2 * SC), 24))


# ============================================================ 增量三
def inc3(mine):
    section("三", "增量三：(c) 窗口外判定与「K >= K_th(91) 两约定同值」")

    # j = 91、92 半直线上界
    uQ = iv_from_frac(QM1)
    b91 = iv_add(iv_from_frac(F(-105, 54 * X0)),
                 iv_add(iv_div((3 * SC, 3 * SC), uQ), iv_mul_int(
                     exp_iv(iv_neg(iv_mul(DELTA, ln_frac(QM1.numerator, QM1.denominator)))), 270)))
    b92 = iv_add(iv_from_frac(F(-3, X0)),
                 iv_add(iv_div((3 * SC, 3 * SC), uQ), iv_mul_int(
                     exp_iv(iv_neg(iv_mul(DELTA, ln_frac(QM1.numerator, QM1.denominator)))), 273)))
    check("[3.1] j=91：对一切 f >= 0 的上界 < 0（严格）", b91[1] < 0, "上界 ∈ " + iv_str(b91, 12))
    exp_slip_check("[3.2] j=91 上界与转述 -1.84889259e-22 对照", F(b91[0] + b91[1], 2 * SC),
                   sci("-1.84889259e-22"))
    check("[3.3] j=92：对一切 f >= 0 的上界 < 0（严格）", b92[1] < 0, "上界 ∈ " + iv_str(b92, 12))
    exp_slip_check("[3.4] j=92 上界与转述 -1.50222523e-21 对照", F(b92[0] + b92[1], 2 * SC),
                   sci("-1.50222523e-21"))

    # j = 2..90 在 f = 1e-12 处的直接定号
    bad = []
    for j in range(2, 91):
        d = D_j(j, F0)
        if not d[1] < 0:
            bad.append((j, iv_str(d, 12)))
    check("[3.5] j = 2 至 90 共 89 档：D_j(1e-12) < 0 且 0 例外", len(bad) == 0,
          (("非负档（最小反例）" + str(bad[:3])) if bad else "89 档全部严格为负"))

    # 统一界：对一切 f >= 1e-12 与一切 j <= 90，D_j(f) < 0
    Xf = iv_from_frac(1 + F0)
    two = exp_iv(iv_mul(LNQ, Xf))           # 2^(C(1+f0)) = exp(lnQ·(1+f0))
    u0 = iv_sub(two, ONE)
    B = iv_add(iv_from_frac(F(-97, 54 * X0)), iv_div((3 * SC, 3 * SC), u0))
    Uub = pow_neg_delta_ub(u0[0])           # (u0)^(-delta) 的上界（取下端点）
    ub_hi = F(B[1], SC) + 267 * F(Uub, SC)
    check("[3.6] 统一界 B(f0) + 3·89·u0^(-delta) < 0（覆盖一切 j <= 90 的半直线）",
          ub_hi < 0, "B 上界 = " + dec(F(B[1], SC), 12) + "，总上界 = " + dec(ub_hi, 12))
    crit = F(-B[1], SC) / (3 * F(Uub, SC))
    check("[3.7] 临界 (j-1) 上界 >= 89（界覆盖到 j = 90 及以上）", crit >= 89,
          "(j-1) 临界 = " + dec(crit, 8))

    # c_90(1+1e-12) 上界 < K*
    c90 = c_j_iv(90)
    c90u = iv_mul(c90, iv_from_frac(1 + F0))
    KS = KSTAR * SC
    check("[3.8] c_90·(1+1e-12) 上界 < K*（严格有理比较）", c90u[1] < KS,
          "上界 = " + dec(F(c90u[1], SC), 26) + "；K* = " + str(KSTAR))
    exp_slip_check("[3.9] c_90·(1+1e-12) 上界与转述 1.23124614107679696176e20 对照",
                   F(c90u[1], SC), sci("1.23124614107679696176e20"))

    # c_92 上界 < K_cross 下端串；T 下界同侧
    c92 = c_j_iv(92)
    check("[3.10] c_92 上界 < K_cross 下端串", F(c92[1], SC) < KCROSS_LO,
          "c_92 上界 = " + dec(F(c92[1], SC), 26))
    check("[3.11] T 下界 3.131547906e20 > c_92 上界", T_LO > F(c92[1], SC),
          "T 下界 = " + dec(T_LO, 10))

    # K* 落段 [c_91, c_92)
    c91 = c_j_iv(91)
    check("[3.12] c_91 <= K* < c_92（严格）", c91[1] <= KS < c92[0],
          "c_91 上界 = " + dec(F(c91[1], SC), 22))


# ============================================================ 增量四
def inc4():
    section("四", "增量四：阈值符号全档定号（j = 2 至 92）")
    pos, neg, zer = [], [], []
    for j in range(2, 93):
        # 注意：此处必须用一般式 Phi_iv（含 m2 = 91、92 的 A 段），
        # 不能用 D_j（D_j 的常数段只对 j <= 90 成立）。
        d = Phi_iv(j, c_j_iv(j))
        if d[0] > 0:
            pos.append(j)
        elif d[1] < 0:
            neg.append(j)
        else:
            zer.append(j)
    check("[4.1] 正档恰为 25 至 90（66 档）", pos == list(range(25, 91)),
          "正档首尾 %s；共 %d 档" % ((pos[:1] + pos[-1:]) if pos else [], len(pos)))
    check("[4.2] 负档恰为 2 至 24 与 91、92（25 档）",
          neg == list(range(2, 25)) + [91, 92], "负档 %s；共 %d 档" % (neg, len(neg)))
    check("[4.3] 未定档为 0", len(zer) == 0, "未定 %s" % zer)
    # 无法机器验证项（注释登记，跳过）：
    # ・「正负档位与各路报告逐档相同」：需要各路报告的逐档表原文，本脚本不读取，跳过。


# ============================================================ 增量五
def inc5(mine):
    section("五", "增量五：(d) 更正条目的可复算数字")
    for j in (88, 89, 90):
        lo, hi = mine[j]
        d22 = USTAR37[j][:22]
        check("[5.1] j=%d：22 位窗口值与我的独立证书逐位相同" % j,
              digs(lo, 22) == d22 and digs(hi, 22) == d22, "22 位 " + digs(lo, 22))
    for j, quoted in ((88, "38208351387"), (89, "60602816210"), (90, "96120571179")):
        cj = c_j_iv(j)
        lo, hi = mine[j]
        wlo = F(cj[0], SC) * lo
        whi = F(cj[1], SC) * hi
        q = sci(quoted[0] + "." + quoted[1:] + "e7")
        check("[5.2] j=%d：窗口绝对宽（K 侧）与转述 11 位值一致到相对 1e-9" % j,
              abs(wlo / q - 1) < F(1, 10 ** 9) and abs(whi / q - 1) < F(1, 10 ** 9),
              "重算 [" + dec(wlo, 12) + ", " + dec(whi, 12) + "]")
    c90 = c_j_iv(90)
    r12 = iv_div((KSTAR * SC, KSTAR * SC), iv_mul(c90, iv_from_frac(1 + F0)))
    v12 = F(r12[0] + r12[1], 2 * SC)
    check("[5.3] K*/c_90(1+1e-12) 与转述 1.6701146262562994 一致到 1e-15",
          abs(v12 - sci("1.6701146262562994")) < F(1, 10 ** 15), "重算 " + dec(v12, 20))
    lo, hi = mine[90]
    ru = iv_div((KSTAR * SC, KSTAR * SC),
                iv_mul(c90, iv_span_frac(1 + lo, 1 + hi)))
    mu_lo, mu_hi = F(ru[0], SC) - 1, F(ru[1], SC) - 1
    check("[5.4] 相对余量 K*/c_90(1+u*) - 1 截断到 14 位小数与转述 0.67011462625666 逐字相同",
          fix(mu_lo, 14) == "0.67011462625666" and fix(mu_hi, 14) == "0.67011462625666",
          "重算 [" + fix(mu_lo, 20) + ", " + fix(mu_hi, 20) + "]")
    print("       说明：[5.3] 的 1.6701146262562994 与重算精确值 1.6701146262562996601 在末两位相差"
          "约 2.6e-16（float64 级显示值）；余量 0.67011462625666 对应分母含 u* 的口径"
          "（两者是不同的式子，不是同一值）。")
    # 无法机器验证项（注释登记，跳过）：
    # ・ledger-note.md 的「更正后的窗口值（22 位）」原文串、route-1.md 第 110 至 125 行的
    #   四个可引条目文本：需要读取本轮结论文件才能核对，本脚本自足运行，不读取，故跳过。


# ============================================================ 增量六
def inc6():
    section("六", "增量六：数字锚点与多实现互证（可复算部分）")
    # d3r3_conflict.out 的 M = 90 下端区间包含我的值
    P = Phi_iv(90, iv_from_frac(K1R3[90][0]))
    qlo, qhi = sci("2.513609590448e-41"), sci("2.513611603624e-41")
    check("[6.1] Φ_90(K1_90 下端) 落在 d3r3_conflict.out 的区间内",
          qlo <= F(P[0], SC) and F(P[1], SC) <= qhi, "Φ ∈ " + iv_str(P, 12))
    # r4b2 两端与 diag5 值对照
    Pr = Phi_iv(90, iv_from_frac(R4B2[90][0]))
    check("[6.2] Φ_90(r4b2 下端) 为正，且与 d3r3_diag5.out 的 +7.410663e-47 尾数一致",
          Pr[0] > 0 and abs(F(Pr[0] + Pr[1], 2 * SC) / sci("7.410663e-47") - 1) < F(1, 10 ** 6),
          "Φ ∈ " + iv_str(Pr, 12))
    exp_slip_check("[6.2b] Φ_90(r4b2 下端) 与增量六「我判」组的 +7.41066282e-46 对照",
                   F(Pr[0] + Pr[1], 2 * SC), sci("+7.41066282e-46"))
    Ph = Phi_iv(90, iv_from_frac(R4B2[90][1]))
    check("[6.3] Φ_90(r4b2 上端) 为负，且与 d3r3_diag5.out 的 -1.099244e-46 尾数一致",
          Ph[1] < 0 and abs(F(Ph[0] + Ph[1], 2 * SC) / sci("-1.099244e-46") - 1) < F(1, 10 ** 6),
          "Φ ∈ " + iv_str(Ph, 12))
    exp_slip_check("[6.3b] Φ_90(r4b2 上端) 与增量六「我判」组的 -1.09924404e-45 对照",
                   F(Ph[0] + Ph[1], 2 * SC), sci("-1.09924404e-45"))
    Pm = Phi_iv(90, iv_from_frac(MPFR_LO))
    check("[6.4] Φ_90(MPFR 下端) 为负，且与 d3r3_diag5.out 的 -4.391675e-46 尾数一致",
          Pm[1] < 0 and abs(F(Pm[0] + Pm[1], 2 * SC) / sci("-4.391675e-46") - 1) < F(1, 10 ** 6),
          "Φ ∈ " + iv_str(Pm, 12))
    # 无法机器验证项（注释登记，跳过）：
    # ・「五套互不复用的实现相互一致到约 1e-23 相对」：需要各实现的原产物逐位对照，
    #   超出本脚本可复算范围，跳过。


# ============================================================ 深档链
def deep_chain(Ms, label):
    section("链", "深档链：K = c_M 处 N(m2) 对 m2 <= M 减 2 严格递减（%s）" % label)
    total = 0
    n_direct = 0
    n_bound = 0
    mind = None
    mindM = None
    bad = []
    for M in Ms:
        K = c_j_iv(M)
        steps = M - 2
        if steps <= 0:
            print("       M=%d：空链（无步长）" % M)
            continue
        vs = {m2: v_iv(m2, K) for m2 in range(1, M)}
        for m2 in range(1, M - 1):
            total += 1
            v2 = vs[m2]
            if v2[1] <= 1000 * SC:
                n_direct += 1
                a = N_iv(m2, K)
                b = N_iv(m2 + 1, K)
                d = F(a[0] - b[1], SC)
            else:
                n_bound += 1
                vm = vs[m2 + 1]
                assert v2[0] >= 110 * SC and vm[0] >= 110 * SC, (
                    "界分支要求 v >= 110", M, m2, dec(F(v2[0], SC), 8), dec(F(vm[0], SC), 8))
                U = pow_neg_delta_ub((2 ** 110 - 1) * SC)
                eps = F(3, 2 ** 110 - 1) + F(3 * ((m2 + 1) - 1) * U, SC)
                if m2 + 1 <= 90:
                    dA = F(97, 54 * X0)
                elif m2 + 1 == 91:
                    dA = F(105, 54 * X0)
                else:
                    dA = F(3, X0)
                d = dA - eps
            if d <= 0:
                bad.append((M, m2, dec(d, 8)))
            if mind is None or d < mind:
                mind, mindM = d, (M, m2)
    print("       直接求值 %d 步、界论证 %d 步（界论证用 v >= 110 的单调上界）" % (n_direct, n_bound))
    check("[链.1] 全部步长严格为正且共 %d 步" % total, not bad,
          ("最小反例 " + str(bad[:3])) if bad else "无反例")
    check("[链.2] 最小步长落在 2.24177e-21 至 2.24179e-21（与 97/(54X0) 同量级，M=%s）" % str(mindM),
          F(224177, 10 ** 5) * F(1, 10 ** 21) <= mind <= F(224179, 10 ** 5) * F(1, 10 ** 21),
          "最小步长下界 = " + dec(mind, 12))


# ============================================================ main
def main():
    argv = sys.argv[1:]
    deep = "--deep" in argv
    want_mp = "--mpmath" in argv

    print("verify.py —— d3-window-tail cycle-1 六条增量自足复算")
    print("模式：" + ("默认档 + --deep" if deep else "默认档") + (" + --mpmath" if want_mp else ""))
    print("格距 SC = 10^90；一切区间为严格包含（向外取整 + 显式尾界）。")

    t0 = time.time()

    n0 = len(FAILS)
    mine = inc1()
    print("[小结] 增量一：%s" % ("通过" if len(FAILS) == n0 else "未通过（见上）"))
    n0 = len(FAILS)
    inc2()
    print("[小结] 增量二：%s" % ("通过" if len(FAILS) == n0 else "未通过（见上）"))
    n0 = len(FAILS)
    inc3(mine)
    print("[小结] 增量三：%s" % ("通过" if len(FAILS) == n0 else "未通过（见上）"))
    n0 = len(FAILS)
    inc4()
    print("[小结] 增量四：%s" % ("通过" if len(FAILS) == n0 else "未通过（见上）"))
    n0 = len(FAILS)
    inc5(mine)
    print("[小结] 增量五：%s" % ("通过" if len(FAILS) == n0 else "未通过（见上）"))
    n0 = len(FAILS)
    inc6()
    print("[小结] 增量六：%s" % ("通过" if len(FAILS) == n0 else "未通过（见上）"))

    n0 = len(FAILS)
    if deep:
        deep_chain(list(range(2, 93)), "全部 M = 2 至 92")
    else:
        deep_chain([2, 3, 25, 45, 90, 91, 92],
                   "默认子集 M ∈ {2, 3, 25, 45, 90, 91, 92}；加 --deep 跑满")
    print("[小结] 深档链：%s" % ("通过" if len(FAILS) == n0 else "未通过（见上）"))

    if want_mp:
        section("附", "与 mpmath dps = 80 的 50 位打印对照")
        from mpmath import mp, mpf, nstr, log as mlog
        mp.dps = 80
        refs = [("delta", DELTA, mlog(3) / mlog(2)),
                ("C", C_IV, mpf(60) + mlog(mpf(112590) / mpf(97)) / mlog(2)),
                ("lnQ", LNQ, mlog(mpf(162) * mpf(X0) / 97))]
        for name, iv, ref in refs:
            lo50 = nstr(mpf(iv[0]) / mpf(SC), 50)
            hi50 = nstr(mpf(iv[1]) / mpf(SC), 50)
            r50 = nstr(ref, 50)
            check("[附.1] %s：与 mpmath 50 位打印至少一端逐字相同" % name,
                  lo50 == r50 or hi50 == r50, "我的 [%s, %s]；mpmath %s" % (lo50, hi50, r50))
    else:
        print("[SKIP] --mpmath 未开启：与 mpmath 的 50 位打印对照跳过（核心自检已含 exp 强判据）")

    print("\n" + "=" * 40)
    print("检查总数 %d；失败 %d；警告 %d；耗时 %.1f 秒" % (NCHECK, len(FAILS), len(WARNS), time.time() - t0))
    for name, detail in FAILS:
        print("  失败最小反例：%s　——　%s" % (name, detail))
    for w in WARNS:
        print("  警告：%s" % w)
    if FAILS:
        print("结论：未全部通过（退出码 1）。")
        return 1
    print("结论：全部实质断言通过（退出码 0）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
