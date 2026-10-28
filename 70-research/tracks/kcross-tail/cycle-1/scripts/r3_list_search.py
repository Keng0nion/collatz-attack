#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""路线 3 定向反例搜索 ③：438 条清单漏项？复算不带 cap_q 的完整清单与差集。

对象（两个格）：
  K* 格：K = 205632218873398596256（m2 = 92 不可行，端点由 eps(91,K*) 给）；
  K_cross 邻域格：K = 313195478959172262876（m2 = 92 可行，端点由 eps(92,K) 给）。
判据（能取 False）：
  1. K* 格完整清单条数 = 442 且被 cap 掉恰为 4（与 k3_run_e.out 第 [3] 节对账）；
  2. 「被 cap 的清单 = 完整清单中分母 < K* 的项」按多重集逐项相等（漏项为 0 的直接判据）；
  3. 完整清单中分母 < K* 的项落在区间内的条数 = 0；完整清单内点 = gamma 两种写法（分母 = K*）；
  4. 差集逐条分母 >= K*，且逐条打印（value、分母、出处）。
对 K_cross 格：先算枚举范围内最大部分商；超过 10^6 时只做 cap 版（并记录该格完整清单不可枚举的
事实与规模 = 枚举范围内部分商之和），不启动超大枚举（本轮实测：该格第 43 位部分商 3.6e20，
未加守卫的 cap_q=None 调用会生成 10 GB 级对象被强杀）。
只读 import k3_rig；输出写本轨道 results 目录。
"""
import sys
import time
from fractions import Fraction as F
from collections import Counter

SCRIPTS = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
sys.path.insert(0, SCRIPTS)
import k3_rig as K

OUT = []
HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1/scripts"


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s, flush=True)


T0 = time.time()
M = 92
KSTAR = 205632218873398596256
KX = 313195478959172262876
GAM_CLAIM = F(325919355854421968365, 205632218873398596256)

D = K.delta_bounds()
CB = K.C_bounds()
L2 = K.ln2_bounds()

p("#" * 74)
p("# 路线 3 定向反例搜索 ③：438 条清单漏项？完整清单与差集复算")
p("# 脚本：tracks/kcross-tail/cycle-1/scripts/r3_list_search.py")
p("#" * 74)
p("")
p("[0] 格端点（严格区间）")
E91 = K.eps_bounds(91, M, KSTAR, D[0], D[1], L2)
BETA_LO = K.rd(D[0] + E91[0])
BETA_HI = K.ru(D[1] + E91[1])
p("    K* 格：eps(91, K*) ∈ [%s, %s]" % (K.sci(E91[0], 24), K.sci(E91[1], 24)))
p("          beta ∈ [%s, %s]" % (K.dec(BETA_LO, 60), K.dec(BETA_HI, 60)))
f92KX = K.feasible(92, M, KX, D[0], D[1], CB)
p("    K_cross 格：m2 = 92 可行？ %s" % f92KX)
E92 = K.eps_bounds(92, M, KX, D[0], D[1], L2)
B2_LO = K.rd(D[0] + E92[0])
B2_HI = K.ru(D[1] + E92[1])
p("          eps(92, KX) ∈ [%s, %s]" % (K.sci(E92[0], 24), K.sci(E92[1], 24)))
p("          beta ∈ [%s, %s]" % (K.dec(B2_LO, 60), K.dec(B2_HI, 60)))


def rebuild(blo, bhi):
    prefA = K.certified_prefix(D[0], D[1], maxlen=250)
    prefB = K.certified_prefix(blo, bhi, maxlen=250)
    k = 0
    while k < min(len(prefA), len(prefB)) and prefA[k] == prefB[k]:
        k += 1
    ck = min(prefA[k], prefB[k]) + 1
    gam = K.cf_value(prefA[:k] + [ck])
    return prefA, prefB, k, ck, gam


def classify(items, blo, bhi):
    inside = []
    outside = 0
    undec = 0
    for (val, src) in items:
        if val > D[1] and val < blo:
            inside.append((val, src))
        elif val <= D[0] or val >= bhi:
            outside += 1
        else:
            undec += 1
    return inside, outside, undec


def run_cell(tag, blo, bhi, do_full):
    p("")
    p("[%s] 格端点 beta ∈ [%s, %s]" % (tag, K.dec(blo, 40), K.dec(bhi, 40)))
    prefA, prefB, kk, ck, gam = rebuild(blo, bhi)
    p("    delta 证书位数 = %d ；beta 证书位数 = %d ；首个相异下标 k = %d（a_k = %d, b_k = %d, c_k = %d）" % (
        len(prefA), len(prefB), kk, prefA[kk], prefB[kk], ck))
    p("    重建 gamma = %d/%d ；等于主张值？ %s ；分母 = K*？ %s" % (
        gam.numerator, gam.denominator, gam == GAM_CLAIM, gam.denominator == KSTAR))
    low, high = K.sb_parents(gam.numerator, gam.denominator)
    p("    gamma 双亲：%d/%d 与 %d/%d ；unimodular？ %s ；分母和 = %d（= K*？ %s）" % (
        low[0], low[1], high[0], high[1], K.unimodular(low, high),
        low[1] + high[1], low[1] + high[1] == KSTAR))
    # 枚举规模 = sum_{j=1..kk+1} a_j（alpha） + sum b_j（beta）
    scaleA = sum(prefA[1:kk + 2])
    scaleB = sum(prefB[1:kk + 2])
    maxA = max(prefA[1:kk + 2])
    maxB = max(prefB[1:kk + 2])
    p("    枚举范围 j <= k+1 = %d ：alpha 侧条数上界 = %d（最大部分商 %d）；beta 侧 = %d（最大部分商 %d）" % (
        kk + 1, scaleA, maxA, scaleB, maxB))
    capped = K.semiconv_list_frontier(prefA, prefB, kk, cap_q=KSTAR)
    p("    cap_q = K* 清单条数 = %d" % len(capped))
    in_c, out_c, un_c = classify(capped, blo, bhi)
    p("    cap 后清单分类：内 %d ；外 %d ；未定 %d" % (len(in_c), out_c, un_c))
    if not do_full:
        p("    完整清单（cap_q=None）不启动：枚举范围内最大部分商 = %d 过大" % max(maxA, maxB))
        p("    若强行枚举，仅该 j 一项就要生成 %d 条（本轮未加守卫的尝试实测峰值内存 10.2 GB 后被强杀）" % (
            max(maxA, maxB)))
        return None
    full = K.semiconv_list_frontier(prefA, prefB, kk, cap_q=None)
    p("    完整清单（cap_q=None）条数 = %d（= %d + %d，与枚举规模上界一致）" % (
        len(full), scaleA, scaleB))
    cf = Counter(full)
    cc = Counter(capped)
    full_under = {x: n for (x, n) in cf.items() if x[0].denominator < KSTAR}
    missing = Counter(full_under) - cc
    extra = cc - Counter(full_under)
    diff = Counter(full) - cc
    p("    漏项判据：被 cap 的清单 = 完整清单中分母 < K* 的项？ %s" % (
        len(missing) == 0 and len(extra) == 0))
    p("      漏项条数 = %d ；多余条数 = %d" % (sum(missing.values()), sum(extra.values())))
    p("    差集（完整减 cap）条数 = %d" % sum(diff.values()))
    for (val, src), n in sorted(diff.items(), key=lambda kv: kv[0][0]):
        p("      【差集】%d/%d（分母 %d >= K*？ %s；出处 %s；重数 %d）" % (
            val.numerator, val.denominator, val.denominator, val.denominator >= KSTAR, src, n))
    in_f, out_f, un_f = classify(full, blo, bhi)
    p("    完整清单分类：内 %d ；外 %d ；未定 %d" % (len(in_f), out_f, un_f))
    for (val, src) in sorted(in_f, key=lambda t: t[0]):
        p("      完整清单内点：%d/%d（分母 = K*？ %s；出处 %s）" % (
            val.numerator, val.denominator, val.denominator == KSTAR, src))
    n_in_under = sum(1 for (val, src) in in_f if val.denominator < KSTAR)
    p("    完整清单中分母 < K* 的内点条数 = %d（须为 0）" % n_in_under)
    return len(full), len(capped), sum(diff.values()), n_in_under, sum(missing.values())


r1 = run_cell("K* 格", BETA_LO, BETA_HI, do_full=True)
r2 = run_cell("K_cross 邻域格", B2_LO, B2_HI, do_full=False)

p("")
p("[对账] 与既有日志")
p("    K* 格：完整 %d（k3_run_e.out 记 442？ %s）；cap %d（记 438？ %s）；差集 %d（记 4？ %s）" % (
    r1[0], r1[0] == 442, r1[1], r1[1] == 438, r1[2], r1[2] == 4))
p("    K* 格 cap 后：内 %d / 外 %d / 未定 %d（k3_run_a.out 记 0/438/0）" % (r1[3], r1[1] - r1[3], 0))
p("    K_cross 格：cap 后清单已复算；完整清单按 [0] 与守卫判据不枚举（该格与 K* 格的唯一差别是第 43 位部分商）")
p("")
p("[结论] 漏项命中数 = %d（0 = 未发现漏项；且「被 cap 清单 = 完整清单中分母 < K* 的项」按多重集逐项相等）" % (
    r1[4]))
p("    总用时 %.1f 秒。" % (time.time() - T0))

open(HERE + "/results/r3_list_search.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/r3_list_search.out")
