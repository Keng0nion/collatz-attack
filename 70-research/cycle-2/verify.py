#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cycle-2 verify.py —— 第 2 轮增量结论的独立复算脚本

本脚本自己遵守的纪律：
1. 不读取 route-1..5.md、materials.md，也不读取本轮任何脚本的产物文件
   （results/*.out、*.log、*.txt、results_rig.txt 等）；一切数值都从定义重算：
   δ = ln 3 / ln 2、X0 = 695·2^60、m = 92、K* = 205632218873398596256、
   Theorem 21 的可行性判据与 ε 公式、Ψ = 区间内最小分母。只用精确有理数
   （fractions.Fraction）与外向取整的区间算术，判定一律用严格不等式。
2. 每条断言对应本轮增量结论的一条。能机器判定的用严格区间或精确整数判据；
   只能查证或属产物层的（其他脚本的行数、md5、退出码，渲染图逐字核对等）
   在注释里写明「无法机器验证」并跳过，不写入判据。
3. 全部通过退出码 0；任何失败退出码非零，并打印首条（最小）反例。

覆盖的增量结论与对应节号：
  结论 1：Ψ(K*) = K*（五路证书的数学内容：连分数加 Farey 邻接、清单穷举、
          落点不等式组、记录序列加单模区间、Stern-Brocot 两侧夹逼）  → 第 1 节
  结论 2：结构性恒等式与闭式（K* = q43、γ = p43/q43、F(1)/F(2)/F(3)、
          p41/q41 与 p42/q42 的 10^-41 余量）                        → 第 2 节
  结论 3：(i) 对一切 K ≥ K*，Ψ(K) ≥ K*；(ii) 平台右端与两支下界       → 第 3 节
  结论 4：方程 ε(92,K) = γ − δ 的根的三套严格区间与唯一性口径          → 第 4 节
  结论 5：一手原件（重下、字节数、md5、文本层子串、K* 处 m2 = 91）      → 第 5 节
  结论 6：清单穷举计数与 k = 42、A42 = 1、B42 = 2、c42 = 2            → 第 6 节
  结论 7：论文链条读数（m = 91、第一步与第七步印数、A 项 3/X0）         → 第 7 节

口径说明（随结论一起写）：
  1. 本脚本证明的与核验的都是「项目重建物」口径下的命题（Ψ、ε_opt 是项目定义，
     论文本身没有 Ψ 符号）；K_cross = 该方程根这一读法仍是未证读法，本脚本不裁决。
  2. 「复现某十进制串」一般指：本脚本用严格区间算出的量，其前若干有效位与
     该串相同（两侧端点截断到同位数字后一致）；引用串最末一位若系原文按
     有效数字舍入印出（截断比较差末位 1），则另以「两端点与串之差小于
     1 ulp」同时成立为准（第 7 节五处引用串都加这一条）。
  3. 本脚本不做形式化核验；结论的等级上限仍是「自足纸面论证加可复算证书」。
"""

import hashlib
import os
import re
import subprocess
import sys
import tempfile
from fractions import Fraction as F

X0 = 695 * 2 ** 60
KSTAR = 205632218873398596256
M = 92
GRID = 150
G10 = 10 ** GRID

# ============================================================ 严格有理区间机件
# 所有区间一律外向取整到 10^-150 网格（只放宽不收紧），保证包含真值。

def rnd_dn(x):
    return F((x.numerator * G10) // x.denominator, G10)


def rnd_up(x):
    return F(-((-x.numerator * G10) // x.denominator), G10)


def iv_mul(a, b):
    return rnd_dn(a[0] * b[0]), rnd_up(a[1] * b[1])


def iv_div(a, b):
    assert b[0] > 0
    return rnd_dn(a[0] / b[1]), rnd_up(a[1] / b[0])


def iv_scale(a, c):
    assert c > 0
    return rnd_dn(a[0] * c), rnd_up(a[1] * c)


def iv_sub(a, b):
    return rnd_dn(a[0] - b[1]), rnd_up(a[1] - b[0])


def iv_add(a, b):
    return rnd_dn(a[0] + b[0]), rnd_up(a[1] + b[1])


def ln2_iv(N=300):
    """ln 2 = 2·atanh(1/3) = 2·sum_{k>=0} (1/3)^(2k+1)/(2k+1)，尾界为几何级数比较。"""
    x = F(1, 3)
    p = x
    s = F(0)
    for k in range(N + 1):
        s += p / (2 * k + 1)
        p *= x * x
    tail = p / ((2 * N + 3) * (1 - x * x))
    return 2 * s, 2 * (s + tail)


def ln3_iv(N=300):
    """ln 3 = ln 2 + 2·atanh(1/5)（因 (1+1/5)/(1-1/5) = 3/2）。"""
    lo2, hi2 = ln2_iv(N)
    x = F(1, 5)
    p = x
    s = F(0)
    for k in range(N + 1):
        s += p / (2 * k + 1)
        p *= x * x
    tail = p / ((2 * N + 3) * (1 - x * x))
    return lo2 + 2 * s, hi2 + 2 * (s + tail)


L2LO, L2HI = ln2_iv(300)
L3LO, L3HI = ln3_iv(300)
D_LO_F = L3LO / L2HI            # δ 的精细严格下界
D_HI_F = L3HI / L2LO            # δ 的精细严格上界
D_LO = rnd_dn(D_LO_F)           # 粗化（供幂、ε 用；仍是严格下界）
D_HI = rnd_up(D_HI_F)           # 粗化上界


def l10(x, n):
    """x > 0 的十进制阶（floor(log10 x)）；非正输入直接报错，
    否则下界比较「F(10)**e > x」对负 x 恒真，会陷入死循环。"""
    if x <= 0:
        raise ValueError("l10 只接受正数")
    e = len(str(x.numerator)) - len(str(x.denominator))
    while F(10) ** e > x:
        e -= 1
    while F(10) ** (e + 1) <= x:
        e += 1
    return e


def sig_digits(x, n):
    """x > 0 的前 n 个有效数字（截断），返回 (十进制阶, n 位整数)。"""
    e = l10(x, n)
    d = x / F(10) ** e * 10 ** (n - 1)
    di = d.numerator // d.denominator
    if di >= 10 ** n:
        di //= 10
        e += 1
    return e, di


def sci_str(x, n=6):
    """有效数字串。支持零与负数：第 4 节的余量明细里有按其定义就为负的值
    （如「右端 g < 0」的余量），不先取符号会让 l10 死循环。"""
    if x == 0:
        return "0.0e+0"
    if x < 0:
        return "-" + sci_str(-x, n)
    e, di = sig_digits(x, n)
    s = str(di)
    return "%s.%se%+d" % (s[0], s[1:], e)


def same_lead(x, y, n):
    """x、y 的前 n 个有效数字相同"""
    return sig_digits(x, n) == sig_digits(y, n)


def near_iv(iv, claimed, n):
    """区间 iv 的两个端点与十进制串 claimed 的前 n 位一致"""
    c = F(claimed)
    return same_lead(iv[0], c, n) and same_lead(iv[1], c, n)


def ulp_consistent(iv, claimed, ulp):
    """区间两端与十进制引用串之差都小于 ulp。

    用于引用串末位系按有效数字舍入印出的情形（此时截断比较会差末位 1）。"""
    c = F(claimed)
    return abs(iv[0] - c) < ulp and abs(iv[1] - c) < ulp


def ln_pos(x, N=200):
    """有理数 x >= 1 的 ln 的严格区间：ln x = k·ln2 + 2·atanh(u)。

    级数每步定向取整（下界全向下、上界全向上），否则端点分母会随项数指数
    膨胀（实测把一次调用拖到十几分钟）。取整引入的绝对误差每步 <= 10^-150。"""
    k = 0
    t = F(1)
    while 2 * t <= x:
        t *= 2
        k += 1
    s = x / t
    u = (s - 1) / (s + 1)
    u2_dn = rnd_dn(u * u)
    u2_up = rnd_up(u * u)
    p = rnd_dn(u)
    acc_lo = F(0)
    for j in range(N + 1):
        acc_lo = rnd_dn(acc_lo + rnd_dn(p / (2 * j + 1)))
        p = rnd_dn(p * u2_dn)
    p = rnd_up(u)
    acc_hi = F(0)
    for j in range(N + 1):
        acc_hi = rnd_up(acc_hi + rnd_up(p / (2 * j + 1)))
        p = rnd_up(p * u2_up)
    tail_hi = rnd_up(p / ((2 * N + 3) * rnd_dn(1 - u * u)))
    lo = rnd_dn(k * L2LO + rnd_dn(2 * acc_lo))
    hi = rnd_up(k * L2HI + rnd_up(2 * (acc_hi + tail_hi)))
    return lo, hi


EXP_MM = 160


def _exp_lo(x):
    """exp(x) 的严格下界（x >= 0）：exp(x) = 2^n·exp(x − n·ln2)，级数逐项向下。"""
    n = (x / L2HI).__floor__()
    r = x - n * L2HI          # 0 <= r <= ln2
    assert r >= 0
    t = F(1)
    s = F(1)
    for j in range(1, EXP_MM + 1):
        t = rnd_dn(rnd_dn(t * r) / j)
        s = rnd_dn(s + t)
    return rnd_dn(s * F(2) ** n)


def _exp_hi(x):
    """exp(x) 的严格上界（x >= 0）：级数逐项向上再加显式尾界。"""
    n = (x / L2HI).__floor__()
    r = x - n * L2LO          # 0 <= r < 1
    assert 0 <= r < F(11, 10)
    t = F(1)
    s = F(1)
    for j in range(1, EXP_MM + 1):
        t = rnd_up(rnd_up(t * r) / j)
        s = rnd_up(s + t)
    tail = rnd_up(t * r / (EXP_MM + 1) / rnd_dn(1 - r / (EXP_MM + 2)))
    return rnd_up((s + tail) * F(2) ** n)


def exp_iv(xlo, xhi):
    """exp 的严格区间，要求 0 <= xlo <= xhi；两端点各自拆 2^n，级数每步定向取整
    以控制分母尺寸（见 ln_pos 的说明）。"""
    assert 0 <= xlo <= xhi
    return _exp_lo(xlo), _exp_hi(xhi)


def pow2_iv(vlo, vhi):
    """2^v 的严格区间（v >= 0 有理区间）。"""
    return exp_iv(rnd_dn(vlo * L2LO), rnd_up(vhi * L2HI))


def log1m_iv(tlo, thi, MM=16):
    """ln(1-t) 的严格区间，t ∈ [tlo, thi] ⊂ (0, 1)；ln(1-t) 关于 t 递减。"""
    def lo_at(t):
        # ln(1-t) = -(sum t^j/j)；下界 = 负的（sum 的上界）
        p = t
        s = F(0)
        for j in range(1, MM + 1):
            s = rnd_up(s + rnd_up(p / j))
            p = rnd_up(p * t)
        tail = rnd_up(p / ((MM + 1) * rnd_dn(1 - t)))
        return rnd_dn(-(s + tail))

    def hi_at(t):
        # 上界 = 负的（sum 的下界，尾项为正可丢）
        p = t
        s = F(0)
        for j in range(1, MM + 1):
            s = rnd_dn(s + rnd_dn(p / j))
            p = rnd_dn(p * t)
        return rnd_up(-s)

    return lo_at(thi), hi_at(tlo)


def lnpow2m1_iv(vlo, vhi):
    """ln(2^v - 1) 的严格区间（v >= 2）：= v·ln2 + ln(1 - 2^-v)。"""
    Bl, Bh = pow2_iv(vlo, vhi)
    l1lo, l1hi = log1m_iv(1 / Bh, 1 / Bl)
    return rnd_dn(vlo * L2LO + l1lo), rnd_up(vhi * L2HI + l1hi)


def delta_pow_iv(n):
    """δ^n 的严格区间。"""
    a = (D_LO, D_HI)
    r = (F(1), F(1))
    k = n
    while k:
        if k & 1:
            r = iv_mul(r, a)
        k >>= 1
        if k:
            a = iv_mul(a, a)
    return r


def geom_iv(m2):
    """geom(m2) = (δ^m2 - 1)/(δ - 1) 的严格区间。"""
    plo, phi = delta_pow_iv(m2)
    return iv_div((plo - 1, phi - 1), (D_LO - 1, D_HI - 1))


C_GIV = ln_pos(F(112590, 97))      # ln((162/97)·X0) = 60·ln2 + ln(112590/97)
C_LO = rnd_dn(60 + C_GIV[0] / L2HI)
C_HI = rnd_up(60 + C_GIV[1] / L2LO)


def A_exact(m2, m, plus73=True):
    if m2 == m:
        return F(0)
    if m2 == m - 1:
        return F(3, X0)
    extra = 73 if plus73 else 1
    return F(97 * (m - m2) + extra, 54 * X0)


def feas(m2, m, K):
    """m2 是否可行（严格判定；返回 None 表示未定）。"""
    g = geom_iv(m2)
    G = iv_mul(g, (C_LO, C_HI))
    rhs = F(m2, m) * K
    if G[1] <= rhs:
        return True
    if G[0] > rhs:
        return False
    return None


VMAX = 2000     # 指数上限：v 超出它时 2^v 不可精确表示，改用可计算的严格压缩界


def eps_iv(m2, m, K, A=None):
    """ε(m2, m, K) 的严格区间，K 为精确有理数。

    v 很大（K 远高于 m2 的可行门槛，如 m2 = 47 在 K = K* 处 v ≈ 2.4e10）时，
    2^v - 1 以 2^vcap - 1（vcap <= v）为下界压掉：T 项给上界，下界直接把 T 项
    丢掉（T 项此时小于 2^-vcap，可忽略但方向严格）。"""
    if A is None:
        A = A_exact(m2, m)
    g = geom_iv(m2)
    vlo, vhi = iv_scale((1 / g[1], 1 / g[0]), F(m2, m) * K)
    if vhi <= VMAX:
        Bl, Bh = pow2_iv(vlo, vhi)
        T1 = iv_div((F(3), F(3)), (Bl - 1, Bh - 1))
        if m2 <= 1:
            T2 = (F(0), F(0))
        else:
            lt = lnpow2m1_iv(vlo, vhi)
            Dl, Dh = exp_iv(rnd_dn(D_LO * lt[0]), rnd_up(D_HI * lt[1]))
            c = F(3 * (m2 - 1))
            T2 = iv_div((c, c), (Dl, Dh))
    else:
        vcap = min(VMAX, max(1, vlo.__floor__()))
        Bcap = F(2) ** vcap - 1              # <= 2^v - 1（因 v >= vlo >= vcap）
        T1 = (F(0), F(3) / Bcap)
        if m2 <= 1:
            T2 = (F(0), F(0))
        else:
            lb, ub = ln_pos(Bcap)
            Dl, Dh = exp_iv(rnd_dn(D_LO * lb), rnd_up(D_HI * ub))
            T2 = (F(0), F(3 * (m2 - 1)) / Dl)
    num = iv_add(iv_add((A, A), T1), T2)
    den = (F(3) * K * L2LO, F(3) * K * L2HI)
    return iv_div(num, den)


def cf_digits(lo, hi, maxn):
    """区间连分数：逐项取整；两端取整相同才确定该项。"""
    digs = []
    for _ in range(maxn):
        nlo = lo.numerator // lo.denominator
        nhi = hi.numerator // hi.denominator
        if nlo != nhi:
            return digs, False
        d_lo = lo - nlo
        d_hi = hi - nlo
        if d_lo <= 0 or d_hi <= 0:
            return digs, False
        digs.append(nlo)
        lo, hi = 1 / d_hi, 1 / d_lo
    return digs, True


def convergents(digs):
    p = [digs[0], digs[0] * digs[1] + 1]
    q = [1, digs[1]]
    for a in digs[2:]:
        p.append(a * p[-1] + p[-2])
        q.append(a * q[-1] + q[-2])
    return p, q


def cf_value(digs):
    """连分数的精确有理值。"""
    v = F(0)
    for a in reversed(digs):
        v = F(a) + (F(0) if v == 0 else 1 / v)
    return v


def simplest(a, b):
    """区间 (a, b) 内分母最小的分数（Stern-Brocot 中位数走法，整段跳）。
    理由（自足）：括号保持单模（z·y 减 x·w 恒等于 1），括号内任意 p/q 给出
    p/q − x/y >= 1/(q·y) 与 z/w − p/q >= 1/(q·w)，相加得 q >= y + w；
    而返回的中项分母恰为 y + w，故它最小。"""
    p1, q1 = F(0), F(1)
    p2, q2 = F(1), F(0)
    while True:
        pm, qm = p1 + p2, q1 + q2
        val = pm / qm
        if a < val < b:
            return val
        if val <= a:
            k = int((a * q1 - p1) / (p2 - a * q2))
            k = max(k, 1)
            p1, q1 = p1 + k * p2, q1 + k * q2
        else:
            k = int((p2 - b * q2) / (b * q1 - p1))
            k = max(k, 1)
            p2, q2 = k * p1 + p2, k * q1 + q2


def brute_min_den(a, b, qmax=300):
    for q in range(1, qmax + 1):
        p = a.numerator * q // a.denominator + 1
        if a < F(p, q) < b:
            return F(p, q)
    return None


# ============================================================ 断言收集

FAILS = []


def ck(tag, cond, detail=""):
    cond = bool(cond)
    line = "[%s] %s" % ("OK  " if cond else "FAIL", tag)
    if detail:
        line += "   " + detail
    print(line)
    if not cond:
        FAILS.append((tag, detail))
    return cond


def int_clip(x):
    return x.numerator // x.denominator


# ============================================================ 第 1 节：Ψ(K*) = K*

def sec1(st):
    print("")
    print("== 第 1 节：Ψ(K*) = K*（五路证书的数学内容，独立重算）==")
    # 工具箱锚点（同时校验 ln/exp/δ 全链）
    e2 = exp_iv(L2LO, L2HI)
    ck("[1.0a] exp(ln2) ∋ 2（互逆自检）", e2[0] <= 2 <= e2[1],
       "区间宽 %s" % sci_str(e2[1] - e2[0], 3))
    e3 = exp_iv(L3LO, L3HI)
    ck("[1.0b] exp(ln3) ∋ 3", e3[0] <= 3 <= e3[1])
    p2d = exp_iv(rnd_dn(D_LO_F * L2LO), rnd_up(D_HI_F * L2HI))
    ck("[1.0c] 2^δ ∋ 3（δ 定义式自检，检查整条 δ 链）", p2d[0] <= 3 <= p2d[1],
       "区间宽 %s" % sci_str(p2d[1] - p2d[0], 3))
    st["simplest_unit"] = (simplest(F(9, 8), F(827, 728)) == F(17, 15))

    # 连分数（精细区间）
    digs, ok = cf_digits(D_LO_F, D_HI_F, 60)
    st["digs_d"] = digs
    ck("[1.1] δ 的连分数前 48 项严格确定", ok and len(digs) >= 48,
       "实得 %d 项；a42 = %s、a43 = %s、a44 = %s" %
       (len(digs), digs[42] if len(digs) > 42 else "?",
        digs[43] if len(digs) > 43 else "?", digs[44] if len(digs) > 44 else "?"))
    p, q = convergents(digs)
    st["pq"] = (p, q)

    # 收敛子符号交替（结构自检）
    alt = True
    for j in range(20, 45):
        v = F(p[j], q[j])
        if v > D_HI:
            sgn = 1
        elif v < D_LO:
            sgn = -1
        else:
            sgn = 0
        if sgn == 0 or (j > 20 and sgn == prev):
            alt = False
        prev = sgn
    ck("[1.2] 收敛子与 δ 的上下交替（j = 20 至 44，结构自检）", alt)

    # 可行性：F(K*) = {1..91}，92 不可行
    fs = [m2 for m2 in range(1, M + 1) if feas(m2, M, F(KSTAR)) is True]
    b92 = feas(M, M, F(KSTAR))
    G91 = iv_mul(geom_iv(91), (C_LO, C_HI))
    G92 = iv_mul(geom_iv(92), (C_LO, C_HI))
    ck("[1.3] 可行集 = {1, …, 91}，m2 = 92 不可行（K = K*）",
       fs == list(range(1, M)) and b92 is False,
       "G(91) ≤ %s（阈 (91/92)K* = %s）；G(92) > %s" %
       (sci_str(G91[1], 8), sci_str(F(91, 92) * KSTAR, 8), sci_str(G92[0], 8)))

    # ε_opt(K*) 的严格区间（下界用 A 项普遍界，上界用 ε(91)）
    E_lo = A_exact(91, M) / (3 * KSTAR * L2HI)
    E_hiI = eps_iv(91, M, F(KSTAR))
    E_hi = E_hiI[1]
    st["E"] = (E_lo, E_hi)
    ck("[1.4a] E_lo = (3/X0)/(3K*·ln2 上界) 复现 8.755860480644673357335956527977e-42",
       near_iv((E_lo, E_lo), "8.755860480644673357335956527977e-42", 16),
       "E_lo = %s" % sci_str(E_lo, 16))
    ck("[1.4b] ε(91, K*) 复现 8.973221708617136016325724785544e-42",
       near_iv(E_hiI, "8.973221708617136016325724785544e-42", 16),
       "区间 = [%s, %s]" % (sci_str(E_hiI[0], 16), sci_str(E_hiI[1], 16)))
    # 两种约定同值：argmin = 91、最大可行 = 91
    amin_ok = True
    for m2 in range(1, 91):
        if A_exact(m2, M) / (3 * KSTAR * L2HI) <= E_hi:
            amin_ok = False
    ck("[1.4c] min_eps 与 max_feasible 在 K* 处同值（argmin = 91 = 最大可行）",
       amin_ok and 91 in fs and 92 not in fs)

    # γ 的落点与 Farey 双侧夹逼（引理：p/q < r/s < p'/q' 且 p'q − p q' = 1 ⇒ s >= q + q'）
    gam = F(p[43], q[43])
    st["gam"] = gam
    ck("[1.5a] γ = p43/q43 在 δ 上方（γ > δ 上界）", gam > D_HI,
       "γ − δ 下界 = %s" % sci_str(gam - D_HI, 20))
    ck("[1.5b] γ 落在区间内（γ < δ + ε_opt 下界）", gam < D_LO + E_lo,
       "余量下界 = %s" % sci_str(D_LO + E_lo - gam, 8))
    det1 = p[41] * q[42] - p[42] * q[41]
    ck("[1.5c] 单模邻接对 (p42/q42, p41/q41)：行列式绝对值 = 1", abs(det1) == 1,
       "值 = %d" % det1)
    ck("[1.5d] p42/q42 < δ 且 δ + ε_opt < p41/q41（区间被单模对夹住）",
       F(p[42], q[42]) < D_LO and D_HI + E_hi < F(p[41], q[41]),
       "p41/q41 − (δ+ε_opt) > %s" % sci_str(F(p[41], q[41]) - D_HI - E_hi, 10))
    ck("[1.5e] 结论（引理 G）：Ψ(K*) = K*", int_clip(gam.denominator) == KSTAR,
       "最小分母 = %d" % gam.denominator)

    # Stern-Brocot 两侧夹逼（第 5 路）
    S_LO = D_LO + E_lo
    S_HI = D_HI + E_hi
    st["S"] = (S_LO, S_HI)
    s1 = simplest(D_LO, S_HI)
    s2 = simplest(D_HI, S_LO)
    ck("[1.6a] simplest 单元测试（9/8 与 827/728 的最小分母 = 17/15）并随机暴力对拍",
       st["simplest_unit"] and simplest(F(3, 10), F(45, 100)) == F(1, 3),
       "暴力对拍见 [1.6b]")
    import random
    rng = random.Random(20261027)
    bf_ok = True
    for _ in range(20):
        a1 = F(rng.randint(1, 40), rng.randint(2, 60))
        b1 = a1 + F(1, rng.randint(2, 30))
        if simplest(a1, b1) != brute_min_den(a1, b1):
            bf_ok = False
    ck("[1.6b] simplest 与暴力枚举在小有理区间上一致（20 个随机区间）", bf_ok)
    ck("[1.6c] 两侧夹逼同为 γ（c2r5 第 [3] 节口径）", s1 == gam and s2 == gam,
       "simplest(δ_lo, β_hi) = %s/%s" % (s1.numerator, s1.denominator))

    # 第 2 路风格（收敛数为第二类最佳逼近）：D1 至 D5 的严格不等式
    bound = F(1, q[42] + q[43])
    worst = None
    worst_j = None
    d3_ok = True
    for j in range(0, 43):
        vlo = q[j] * D_LO - p[j]
        vhi = q[j] * D_HI - p[j]
        if vlo <= 0 <= vhi:
            d3_ok = False
            break
        m_ = min(abs(vlo), abs(vhi))
        r_ = m_ / bound
        if worst is None or r_ < worst:
            worst = r_
            worst_j = j
    ck("[1.7a] D3' 对一切 j ≤ 42：|q_j·δ − p_j| > 1/(q42+q43)（43 格全过）",
       d3_ok and worst > 1, "最紧一格 j = %d，比 %.6f" % (worst_j, float(worst)))
    ck("[1.7b] D4' q43·ε_hi < 1/(q42+q43)",
       F(q[43]) * E_hi < bound,
       "比 %.6f（本脚本用紧 ε_hi，第 2 路的 0.626069 用其较松的 ε_hi）" %
       float(F(q[43]) * E_hi / bound))
    ck("[1.7c] D5' q43·ε_lo > 1/q44（交叉核对）",
       F(q[43]) * E_lo > F(1, q[44]),
       "倍数 %.6f" % float(F(q[43]) * E_lo * q[44]))

    # 第 1 路细判据与关键数字
    ck("[1.8a] [P,3] = F(3) > δ + ε_opt（右邻接对可用）",
       F(3 * p[41] + p[40], 3 * q[41] + q[40]) > D_HI + E_hi,
       "余量 > %s" % sci_str(F(3 * p[41] + p[40], 3 * q[41] + q[40]) - D_HI - E_hi, 8))
    det2 = (3 * p[41] + p[40]) * q[43] - p[43] * (3 * q[41] + q[40])
    ck("[1.8b] (F(2), F(3)) 也是单模邻接对（行列式 = 1）", abs(det2) == 1,
       "值 = %d" % det2)
    ck("[1.8c] q42+q43 > K* 且 q43+(3q41+q40) > K*",
       q[42] + q[43] > KSTAR and q[43] + 3 * q[41] + q[40] > KSTAR,
       "q42+q43 = %d；q43+Q_F3 = %d" % (q[42] + q[43], q[43] + 3 * q[41] + q[40]))
    # 产物层断言（无法机器验证，按纪律跳过）：
    #   route1_cert.out 93 行 / 30 条判据全 True / 退出码 0 / md5 fee908…；
    #   route2_cert.py 复跑退出码 0、产物 md5 ffa188…；route3_cert.py 两跑
    #   58 PASS / 0 FAIL 且两次输出逐字节相同；results_rig.txt 的 [D1] 至 [D6]
    #   标记行；c2r5_cert.log 的 [3] 节行。以上都是本轮其他脚本的产物与运行记录，
    #   其数学内容已由本脚本第 1、4、6 节重算，此处不重复核验。


# ============================================================ 第 2 节：结构恒等式

def sec2(st):
    print("")
    print("== 第 2 节：结构性恒等式与闭式（独立重算）==")
    p, q = st["pq"]
    gam = st["gam"]
    ck("[2.1a] q41 = 77692117359936589403、q42 = 127940101513462006853",
       q[41] == 77692117359936589403 and q[42] == 127940101513462006853,
       "q41 = %d；q42 = %d" % (q[41], q[42]))
    ck("[2.1b] K* = q43 = q41 + q42", q[43] == KSTAR and q[43] == q[41] + q[42],
       "q43 = %d" % q[43])
    ck("[2.1c] q43 = 2·q41 + q40（因 a42 = a43 = 1）",
       q[43] == 2 * q[41] + q[40])
    ck("[2.1d] p43 = p41 + p42 且 γ = p43/q43 = 325919355854421968365/205632218873398596256",
       p[43] == p[41] + p[42] and gam == F(325919355854421968365, KSTAR))
    ck("[2.1e] |p41·q42 − p42·q41| = 1", abs(p[41] * q[42] - p[42] * q[41]) == 1)
    digs = st["digs_d"]
    f1 = cf_value(digs[:42] + [1])
    f2 = cf_value(digs[:42] + [2])
    f3 = cf_value(digs[:42] + [3])
    ck("[2.2a] F(1) = p42/q42、F(2) = γ、F(3) = 449058448471548615631/283324336233335185659",
       f1 == F(p[42], q[42]) and f2 == gam
       and f3 == F(449058448471548615631, 283324336233335185659),
       "F(3) = %d/%d" % (f3.numerator, f3.denominator))
    ck("[2.2b] F(3) − γ = 1.7164255009e-41（引用值 1.716425501e-41 为 10 位四舍五入）",
       near_iv((f3 - gam, f3 - gam), "1.716425501e-41", 9)
       and abs(F(f3 - gam) - F("1.716425501e-41")) < F(1, 10 ** 51),
       "值 = %s" % sci_str(f3 - gam, 12))
    hi41 = F(p[41], q[41]) - D_LO
    lo41 = F(p[41], q[41]) - D_HI
    ck("[2.2c] p41/q41 在 δ 上方 6.32e-41",
       F(632, 100) * 10 ** -41 < lo41 and hi41 < F(633, 100) * 10 ** -41
       and lo41 > 0,
       "值 ∈ [%s, %s]" % (sci_str(lo41, 10), sci_str(hi41, 10)))
    lo42 = D_LO - F(p[42], q[42])
    hi42 = D_HI - F(p[42], q[42])
    ck("[2.2d] p42/q42 在 δ 下方 3.74e-41",
       F(373, 100) * 10 ** -41 < lo42 and hi42 < F(375, 100) * 10 ** -41,
       "值 ∈ [%s, %s]" % (sci_str(lo42, 10), sci_str(hi42, 10)))


# ============================================================ 第 3 节：地板与平台

def sec3(st):
    print("")
    print("== 第 3 节：全部 K ≥ K* 的地板；平台至 3.131547906e20 ==")
    p, q = st["pq"]
    E_lo, E_hi = st["E"]
    # (i) 对一切 K ≥ K*：[D3][D4] 两条（在 K* 处）加初等单调性引理
    ck("[3.1a] [D3]/[D4] 两条在 K* 处成立（已由第 1、2 节判据覆盖）",
       F(p[42], q[42]) < D_LO and D_HI + E_hi < F(p[41], q[41]) and
       abs(p[41] * q[42] - p[42] * q[41]) == 1)
    mlo = F(p[41], q[41]) - D_HI - E_hi
    mhi = F(p[41], q[41]) - D_LO - E_lo
    ck("[3.1b] [D4] 余量复现 5.42451274713e-41（取下端：δ 与 ε 都取上界）",
       near_iv((mlo, mlo), "5.42451274713e-41", 10) and mlo > 0 and mhi > mlo,
       "余量 ∈ [%s, %s]" % (sci_str(mlo, 12), sci_str(mhi, 12)))
    # 抽样：ε(m2, ·) 随 K 严格递减（全称单调性是初等引理：v 与 K 成正比，
    # 2^v − 1 与 (2^v−1)^δ 递增，A 项与 K 无关，再除以 3K·ln2。）
    mono_ok = True
    Ks = [F(KSTAR), F(12, 10) * KSTAR, F(15, 10) * KSTAR]
    for m2 in (47, 88, 91, 92):
        prev = eps_iv(m2, M, Ks[0])
        for K in Ks[1:]:
            cur = eps_iv(m2, M, K)
            if not (prev[0] > cur[1]):
                mono_ok = False
            prev = cur
    ck("[3.1c] 抽样：ε(m2, ·) 随 K 严格递减（m2 = 47、88、91、92；三个 K 点）",
       mono_ok, "全称部分为初等引理（注释内），本项只作抽样，不代替证明")
    # (ii) 平台：两支下界（K ≤ X）
    X = 313154790600000000000
    U2 = F(6932, 10000)
    gap_up = F(1, KSTAR * (75 * q[41] + 38 * q[40]))
    ck("[3.2a] γ − δ 的严格上界 = 1/(K*(75q41 + 38q40)) 复现 6.285990611e-43",
       near_iv((gap_up, gap_up), "6.285990611e-43", 10) and gam_gt(st, gap_up),
       "上界 = %s；且 > γ − δ 区间上端" % sci_str(gap_up, 10))
    b1 = F(1, X0 * X * L2HI)
    b1u = F(1, X0 * X * U2)
    ck("[3.2b] 第一支下界（m2 ≤ 91，K = X）复现 5.749073e-42（U2 口径）",
       near_iv((b1u, b1u), "5.749073e-42", 7) and b1 > gap_up,
       "紧界 = %s；U2 口径 = %s" % (sci_str(b1, 10), sci_str(b1u, 10)))
    g92 = geom_iv(92)
    vmax = rnd_up(F(X) / g92[0])
    p2v = exp_iv(rnd_dn(vmax * L2LO), rnd_up(vmax * L2HI))
    b2 = F(1, (p2v[1] - 1) * X * L2HI)
    b2u = F(1, (p2v[1] - 1) * X * U2)
    ck("[3.2c] 第二支下界（m2 = 92 支，绑定义）> γ − δ 的上界（余量为正）",
       b2 > gap_up and b2u > gap_up,
       "紧界 = %s、U2 口径 = %s；阈 = %s；与引用值 6.285992e-43 相对差 %.1e" %
       (sci_str(b2, 10), sci_str(b2u, 10), sci_str(gap_up, 10),
        abs(float(b2u / F("6.285992e-43") - 1))))
    d1 = A_exact(90, M) / (3 * X * L2HI)
    d1p = A_exact(90, M, plus73=False) / (3 * X * L2HI)
    ck("[3.2d] 对一切 m2 ≤ 91：A(m2) ≥ 3/X0（+73 与 +1 两种读法都成立）",
       d1 > gap_up and d1p > gap_up,
       "m2 = 90 的最紧下界：+73 口径 %s、+1 口径 %s" % (sci_str(d1, 8), sci_str(d1p, 8)))
    # 本脚本自己的紧界二分：平台右端 ≥ X
    lo, hi = F(31, 10) * 10 ** 20, F(32, 10) * 10 ** 20
    for _ in range(70):
        mid = (lo + hi) / 2
        vv = rnd_up(mid / g92[0])
        pp = exp_iv(rnd_dn(vv * L2LO), rnd_up(vv * L2HI))
        if F(1, (pp[1] - 1) * mid * L2HI) > gap_up:
            lo = mid
        else:
            hi = mid
    ck("[3.2e] 用本脚本的紧界二分：平台右端 ≥ 3.131547906e20（引用右端是保守有效值）",
       lo >= F(X), "紧界右端 ≈ %s（引用值 %s）" % (sci_str(lo, 10), sci_str(F(X), 10)))
    # 平台结论的装配（注释写明依赖）：
    #   对 K ∈ (K*, X]：任何可行 m2 落在两支之一，两支下界在 K = X 处最小，
    #   故 ε_opt(K) ≥ min(b1, b2) > γ − δ；于是 γ ∈ (δ, δ + ε_opt(K))，Ψ(K) ≤ K*；
    #   再由第 3.1 节得 Ψ(K) ≥ K*，故 Ψ(K) = K*。
    #   由此 K_cross > 3.131547906e20 依赖「K_cross = 该方程根」这一未证读法（不裁决）。


def gam_gt(st, gap_up):
    """gap_up 是 γ − δ 的严格上界"""
    return st["gam"] - D_LO < gap_up


# ============================================================ 第 4 节：根的严格区间

def sec4(st):
    print("")
    print("== 第 4 节：方程 ε(92,K) = γ − δ 的根的严格区间（独立重算）==")
    p, q = st["pq"]
    gam = st["gam"]
    giv = (gam - D_HI, gam - D_LO)     # γ − δ 的严格区间
    st["gap"] = giv

    def g_iv(K):
        return eps_iv(92, M, K)

    ck("[4.1a] 相邻整数反号（第 4 路 [F]）：K = …876 含 γ、…877 不含",
       g_iv(F(313195478959172262876))[0] > giv[1]
       and g_iv(F(313195478959172262877))[1] < giv[0],
       "g(…876) > %s；g(…877) < %s" %
       (sci_str(g_iv(F(313195478959172262876))[0] - giv[1], 8),
        sci_str(g_iv(F(313195478959172262877))[1] - giv[0], 8)))
    # 第 1 路的两端有理数（相对宽 4.62488828e-37）
    R1a = F(45136225354708871151757558816616152091, 2 ** 57)
    R1b = F(361089802837670969214060470532929216895, 2 ** 60)
    wa = g_iv(R1a)
    wb = g_iv(R1b)
    width1 = R1b - R1a
    rel1 = width1 / R1a
    ck("[4.2a] 第 1 路端点：g > 0 在左、g < 0 在右（[J1] 至 [J5] 口径）",
       wa[0] > giv[1] and wb[1] < giv[0],
       "g 左 > %s；g 右 < %s" % (sci_str(wa[0] - giv[1], 8), sci_str(wb[1] - giv[0], 8)))
    ck("[4.2b] 该区间宽恰为 167/2^60 = 1.44849410e-16，相对宽 4.62488828e-37",
       width1 == F(167, 2 ** 60) and near_iv((width1, width1), "1.44849410e-16", 9)
       and near_iv((rel1, rel1), "4.62488828e-37", 9),
       "宽 = %s；相对宽 = %s" % (sci_str(width1, 10), sci_str(rel1, 10)))
    # 第 5 路的 47 位区间（打印串为 40 位小数，按字面解析）
    L5a = F("313195478959172262876.6365306194907065260231016940260118526233")
    L5b = F("313195478959172262876.6365306194907065260231016961279595491105")
    ga = g_iv(L5a)
    gb = g_iv(L5b)
    wid5 = L5b - L5a
    rel5 = wid5 / L5a
    ck("[4.3a] 第 5 路端点：g > 0 在左、g < 0 在右（[5] 节口径）",
       ga[0] > giv[1] and gb[1] < giv[0],
       "g 左 > %s；g 右 < %s" % (sci_str(ga[0] - giv[1], 8), sci_str(gb[1] - giv[0], 8)))
    ck("[4.3b] 该区间绝对宽 ≈ 2.1019476964872e-27、相对宽 ≈ 6.71e-48",
       near_iv((wid5, wid5), "2.1019476964872e-27", 14)
       and near_iv((rel5, rel5), "6.71e-48", 3),
       "宽 = %s（引用 2.1019476964872256e-27，打印端点为 40 位舍入）" % sci_str(wid5, 14))
    ck("[4.3c] 两套区间相容：第 5 路区间含于第 1 路区间",
       R1a < L5a and L5b < R1b)
    # 第 5 路的「主导权复核」：在该区间上 ε_opt = ε(92, ·)
    min91 = A_exact(91, M) / (3 * L5b * L2HI)
    e92_lo = ga[0]
    ck("[4.4] 主导权：min_{m2≤91} ε(m2, K2) 的下界 > ε(92, K1) 的上界",
       min91 > ga[1],
       "min 下界 = %s（本脚本；引用值 5.74876439712480888646759896504e-42 在其 13 位"
       "之外有约 4e-14 相对偏差，量级与结论不受影响）；ε(92,K1) 上界 = %s" %
       (sci_str(min91, 16), sci_str(ga[1], 16)))
    # 唯一性：ε(92, ·) 严格递减（初等引理，同上）＋ 抽样；全称部分不机器可证。
    mono = True
    prev = g_iv(F(KSTAR))
    for K in (F(2 * KSTAR), F(3 * KSTAR)):
        cur = g_iv(K)
        if not (prev[0] > cur[1]):
            mono = False
        prev = cur
    ck("[4.5] 抽样：ε(92, ·) 随 K 严格递减（唯一性口径）", mono,
       "全称部分是初等引理（注释内），本项只作抽样")
    # 登记（不裁决）：这是「方程 ε(92,K) = γ − δ 的根」的区间；
    # 「该根 = K_cross（越界阈值）」是未证读法，本脚本不核验。


# ============================================================ 第 5 节：一手原件

def normalize_text(t):
    t = re.sub(r"-\s*\n\s*", "", t)
    t = re.sub(r"\s+", " ", t)
    return t


def sec5(st):
    print("")
    print("== 第 5 节：一手原件（重下、md5 与文本层核验）==")
    url = "https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf"
    tmp = os.path.join(tempfile.gettempdir(), "c2verify_hercher5.pdf")
    got = False
    try:
        if os.path.exists(tmp):
            os.remove(tmp)
        r = subprocess.run(["curl", "-sLf", "--max-time", "90", "-o", tmp, url],
                           capture_output=True, timeout=150)
        got = (r.returncode == 0 and os.path.exists(tmp))
    except Exception:
        got = False
    if not got:
        print("[SKIP] [5.1] 印出版 PDF 重下核验：网络不可用，本项未运行（不计通过）")
        print("[SKIP] [5.2] 文本层子串核验：无下载件，本项未运行（不计通过）")
        return
    with open(tmp, "rb") as f:
        data = f.read()
    size = len(data)
    md5 = hashlib.md5(data).hexdigest()
    ck("[5.1] 印出版 hercher5.pdf 重下：250655 字节、md5 3e2377bef0b1c0435dc455c9bbee43a1",
       size == 250655 and md5 == "3e2377bef0b1c0435dc455c9bbee43a1",
       "实测 %d 字节、md5 %s" % (size, md5))
    txt = os.path.join(tempfile.gettempdir(), "c2verify_hercher5.txt")
    try:
        subprocess.run(["pdftotext", "-layout", tmp, txt], capture_output=True,
                       timeout=120, check=True)
        with open(txt, encoding="utf-8", errors="replace") as f:
            body = normalize_text(f.read())
    except Exception:
        print("[SKIP] [5.2] 文本层子串核验：pdftotext 不可用，本项未运行（不计通过）")
        return
    lem22 = [
        "Lemma 22. Let 0 < α < β be two real numbers with continued fraction expansions",
        "Then every fraction in the open interval (α, β) has a denominator which is not smaller than the one of",
        "If k is even, increasing the partial denominator increases the fraction.",
        "If k is odd, decreasing the partial denominator increases the fraction.",
    ]
    miss = [s for s in lem22 if s not in body]
    ck("[5.2a] Lemma 22 文本层：开区间、两种 parity 全印", not miss,
       "缺 %d 条" % len(miss) if miss else "4 条子串全部命中")
    th21 = [
        "Theorem 21. Let K be the number of odd numbers in a given m-cycle",
        "Further, assume there exists a positive integer m2 with",
        "97(m − m2 ) + 73",
        "97(m − m2 ) + 1",
        "There are m2 consecutive local minima which are directly followed by at least",
        "X0 = 695 · 260 .",
    ]
    miss = [s for s in th21 if s not in body]
    ck("[5.2b] Theorem 21 文本层：A 三段（陈述 +73 与证明末行 +1 并存）、m2 为正整数、循环窗、X0 = 695·2^60",
       not miss, "缺 %d 条" % len(miss) if miss else "6 条子串全部命中")
    ck("[5.2c] 渲染图逐字核对与勘误窗口论证：无法机器验证（需人工读图），跳过", True,
       "本脚本只做文本层子串核验")
    # K* 处 m2 = 91、两种约定同值：数学内容已在第 1.3、1.4c 节重算。


# ============================================================ 第 6 节：清单穷举

def sec6(st):
    print("")
    print("== 第 6 节：K* 格清单穷举（442 / 2 / 440 / 0）与 k = 42 数据 ==")
    p, q = st["pq"]
    gam = st["gam"]
    digs_d = st["digs_d"]
    S_LO, S_HI = st["S"]
    digs_s, ok_s = cf_digits(S_LO, S_HI, 60)
    ck("[6.1a] S = δ + ε_opt 侧的区间连分数至少确定到下标 42",
       len(digs_s) >= 43 and digs_s[:42] == digs_d[:42] and digs_s[42] == 2,
       "实得 %d 项；首异下标 k = %s，A_k = %s，B_k = %s" %
       (len(digs_s), next((i for i in range(min(len(digs_s), len(digs_d)))
                           if digs_s[i] != digs_d[i]), None),
        digs_d[42] if len(digs_d) > 42 else "?",
        digs_s[42] if len(digs_s) > 42 else "?"))
    ck("[6.1b] k = 42、A42 = 1、B42 = 2、c42 = min+1 = 2（区间确定，非网格）",
       digs_d[42] == 1 and digs_s[42] == 2)
    f25 = cf_value(digs_d[:42] + [2, 2])
    ck("[6.1c] S < F(2.5) 且 S > F(2) = γ，故尾 b43 = 2（清单条数 442 的依据）",
       S_HI < f25 and gam < S_LO,
       "F(2.5) = %d/%d；S_HI 与 F(2.5) 差 = %s" %
       (f25.numerator, f25.denominator, sci_str(f25 - S_HI, 8)))
    b43 = 2
    Bdig = digs_d[:42] + [2] + [b43]
    cnt = 0
    inside = []
    outside = 0
    undec = []
    per_side = {"alpha": 0, "beta": 0}
    for src, S in (("alpha", digs_d), ("beta", Bdig)):
        for j in range(1, 44):
            pref = S[:j]
            for mo in range(1, S[j] + 1):
                fr = cf_value(pref + [mo])
                cnt += 1
                per_side[src] += 1
                if fr <= D_LO or fr >= S_HI:
                    outside += 1
                elif fr > D_HI and fr < S_LO:
                    inside.append((fr, src, j, mo))
                else:
                    undec.append((fr, src, j, mo))
    ck("[6.2a] 清单条数 = 442（alpha 侧 220 与 beta 侧 222）",
       cnt == 442 and per_side["alpha"] == 220 and per_side["beta"] == 222,
       "实得 %d（alpha %d、beta %d）" % (cnt, per_side["alpha"], per_side["beta"]))
    ck("[6.2b] 严格在内 = 2、严格在外 = 440、未定 = 0",
       len(inside) == 2 and outside == 440 and len(undec) == 0,
       "实得 内 %d、外 %d、未定 %d" % (len(inside), outside, len(undec)))
    if inside:
        ck("[6.2c] 在内两项都是 γ（alpha 侧 j = 43 与 beta 侧 j = 42）",
           all(x[0] == gam for x in inside)
           and sorted((x[1], x[2]) for x in inside) == [("alpha", 43), ("beta", 42)],
           "; ".join("%s j=%d m=%d" % (x[1], x[2], x[3]) for x in inside))
        ck("[6.2d] 最小分母 = K*（两约定同值）",
           min(x[0].denominator for x in inside) == KSTAR)


# ============================================================ 第 7 节：论文链条

def sec7(st):
    print("")
    print("== 第 7 节：论文 Theorem 23 链条读数（独立重算）==")
    Kf = F(7) * 10 ** 11
    e47 = eps_iv(47, 91, Kf)
    ck("[7.1a] 第一步：K = 7e11、m = 91 下 m2 = 47 可行、48 不可行",
       feas(47, 91, Kf) is True and feas(48, 91, Kf) is False)
    ck("[7.1b] 第一步 ε(47; m = 91; 7e11) 复现 6.89235101715965838e-32 且 < 6.9e-32",
       near_iv(e47, "6.89235101715965838e-32", 15)
       and ulp_consistent(e47, "6.89235101715965838e-32", F(1, 10 ** 49))
       and e47[1] < F(69, 10) * 10 ** -32,
       "区间 = [%s, %s]；与引用串差 %s（< 1 ulp = 1e-49；引用串末位为舍入）" %
       (sci_str(e47[0], 18), sci_str(e47[1], 18),
        sci_str(abs(e47[1] - F("6.89235101715965838e-32")), 3)))
    e47m92 = eps_iv(47, 92, Kf)
    ck("[7.1c] 同格若取 m = 92 则给 7.0463702029216624e-32（与印数 6.9e-32 不合）",
       near_iv(e47m92, "7.0463702029216624e-32", 15)
       and ulp_consistent(e47m92, "7.0463702029216624e-32", F(1, 10 ** 48)),
       "区间 = [%s, %s]" % (sci_str(e47m92[0], 18), sci_str(e47m92[1], 18)))
    e206 = eps_iv(91, 91, F(206) * 10 ** 18)
    e205 = eps_iv(91, 91, F(205) * 10 ** 18)
    eK = eps_iv(91, 91, F(KSTAR))
    ck("[7.2a] 第七步：K = 2.06e20 代入同式复现 1.11777663068838816e-43",
       near_iv(e206, "1.11777663068838816e-43", 15)
       and ulp_consistent(e206, "1.11777663068838816e-43", F(1, 10 ** 60)),
       "区间 = [%s, %s]" % (sci_str(e206[0], 18), sci_str(e206[1], 18)))
    ck("[7.2b] 同式在 K = 2.05e20 给 1.44921627253094092e-43",
       near_iv(e205, "1.44921627253094092e-43", 15)
       and ulp_consistent(e205, "1.44921627253094092e-43", F(1, 10 ** 60)),
       "区间 = [%s, %s]" % (sci_str(e205[0], 18), sci_str(e205[1], 18)))
    ck("[7.2c] 同式在 K = K* 给 1.22979157996235308e-43",
       near_iv(eK, "1.22979157996235308e-43", 15)
       and ulp_consistent(eK, "1.22979157996235308e-43", F(1, 10 ** 60)),
       "区间 = [%s, %s]" % (sci_str(eK[0], 18), sci_str(eK[1], 18)))
    a3 = A_exact(91, M)
    a170 = F(170, 54 * X0)
    general91 = F(97 * (M - 91) + 73, 54 * X0)
    ck("[7.3a] 印出版 A(91) = 3/X0 = 3.744008e-21，与 170/(54·X0) = 3.928897e-21 不同",
       a3 == F(3, X0) and a170 == general91 and a3 != a170 and a3 < a170,
       "3/X0 = %s；170/(54X0) = %s" % (sci_str(a3, 10), sci_str(a170, 10)))
    ck("[7.3b] 若按证明末行的 (97(m−m2)+1)/(54X0) 读，m2 ≤ 90 的 A 仍 > 3/X0",
       A_exact(90, M, plus73=False) > F(3, X0))
    # 印数侧（6.9e-32 与 1.11e-43）的文本层核验在第 5.2b 节（需下载件）；
    # 「作者有意把 K 取整到 2.06e20」仍是推断（本轮原文即如此标注）。


# ============================================================ 主流程

def main():
    print("cycle-2 verify.py（独立复算；不读本轮结论文件）")
    print("δ 区间宽 = %s；K* = %d；X0 = %d" %
          (sci_str(D_HI - D_LO, 3), KSTAR, X0))
    st = {}
    sec1(st)
    sec2(st)
    sec3(st)
    sec4(st)
    sec5(st)
    sec6(st)
    sec7(st)
    print("")
    if FAILS:
        print("失败 %d 条；最小反例（首条）：%s   %s" %
              (len(FAILS), FAILS[0][0], FAILS[0][1]))
        return 1
    print("全部判据通过；退出码 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
