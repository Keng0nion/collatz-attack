#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 4 路任务 (b) 的增补：两种约定分岔窗口的精确边界探针（对照 route-5 §4.4）。

背景：route-5.md:230 把分岔窗口宽度登记为「v 中 log2(1+2^-C) ≈ 1.5×10^-22、
K 中相对 ≈ 2×10^-24」；r4b_search_epsopt.py 第 [6] 节按同一判据式复算得
v 中 1.078069387×10^-21、相对 1.5361313×10^-23 —— 与登记不一致。

本脚本指出该判据式漏掉两项：新档 j 自身的 3(j-1)/(2^v - 1)^delta 项
（在门槛处 2^v - 1 最小，该项最大）与旧档 j-1 的 3/(2^{v'} - 1) 项
（v' ≈ 1.57 v，故该项极小）。正确判据是

    numerator(j) < numerator(j-1)
      ⟺ A(j) + 3/(2^v - 1) + 3(j-1)/(2^v - 1)^delta
         < A(j-1) + 3/(2^{v'} - 1) + 3(j-2)/(2^{v'} - 1)^delta，
      其中 v = v(j,K)，v' = v(j-1,K)。

本脚本对 j = 90、89、85 直接做数值边界定位：
  1. 在门槛 c_j 的邻域取相对偏移点，逐点用严格区间比较 numerator(j) 与
     numerator(j-1)，确定哪些 K 上 argmin = j-1（窗口内）或 j（窗口外）；
  2. 用二分把窗口右端 K*_j 夹到严格区间，换算相对宽度；
  3. 对 j = 91、92 验证「无窗口」（新档在其门槛处立即获胜）。

运行：/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python r4b2_window_probe.py
"""
import sys
import time

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
sys.path.insert(0, HERE)
from fractions import Fraction as F
import r4_common as C

OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


t_start = time.time()
DLO, DHI, L2 = C.consts()
CIV = C.R.C_bounds()
X0 = C.X0_695

p("#" * 74)
p("# 任务 (b) 增补：分岔窗口的精确边界（numerator 两两严格比较）")
p("# 脚本：tracks/kcross-proof/cycle-1/scripts/r4b2_window_probe.py")
p("#" * 74)
p("")


def thr(j):
    """c_j = (92/j) * geom(j) * C 的严格区间。"""
    g = C.R.geom_bounds(j, DLO, DHI)
    return (C.R.rd(g[0] * CIV[0] * F(92, j)), C.R.ru(g[1] * CIV[1] * F(92, j)))


def cmp_num(j, K):
    """比较 numerator(j, K) 与 numerator(j-1, K)，即
      numerator(j) = A(j) + 3/(2^v-1) + 3(j-1)/(2^v-1)^delta，v = v(j,K)。
    返回 'j_smaller' / 'jm1_smaller' / None（未分离）。
    实现：numerator(m2) = eps(m2,K) * (3K log2)（按定义式），故
      D := numer(j) - numer(j-1) 的严格区间 = iv_sub(iv_mul(eps_j, den), iv_mul(eps_m1, den))，
      den = 3K log2 的严格区间。A 项已含在 eps 内，无需单独处理。
    区间取值的符号判决是可靠的（D[1] < 0 或 D[0] > 0 即可下结论）。"""
    A_j = C.R.A_of(j, 92, X0)
    A_jm1 = C.R.A_of(j - 1, 92, X0) if j - 1 >= 1 else None
    if A_jm1 is None:
        return None
    # 用 (3K log2) * eps - A 的界来还原 R 的界：
    e_j = C.R.eps_bounds(j, 92, K, DLO, DHI, L2, X0=X0)
    e_m1 = C.R.eps_bounds(j - 1, 92, K, DLO, DHI, L2, X0=X0)
    den = C.R.iv_mul((F(3 * K), F(3 * K)), L2)      # 3K log2 的严格区间
    # numerator = eps * den；D = numer(j) - numer(j-1) 的严格区间
    nj = C.R.iv_mul(e_j, den)
    nm1 = C.R.iv_mul(e_m1, den)
    D = C.R.iv_sub(nj, nm1)
    if D[1] < 0:
        return "j_smaller"
    if D[0] > 0:
        return "jm1_smaller"
    return None


p("[0] 门槛 c_j（严格区间；只用中点作参考）")
mid = {}
for j in (85, 89, 90, 91, 92):
    clo, chi = thr(j)
    mid[j] = (clo + chi) / 2
    p("    c_%d ∈ [%s, %s]" % (j, C.dec(clo, 30), C.dec(chi, 30)))
p("    K* = %d ；c_90 与 K* 的关系：c_90_hi < K* ？ %s" % (C.KSTAR, thr(90)[1] < C.KSTAR))

p("")
p("[1] 邻域扫描：numerator(j) 与 numerator(j-1) 的严格比较（+ = j 更小，- = j-1 更小）")
for j in (85, 89, 90):
    c = mid[j]
    p("    --- j = %d，c_j 中点 = %s ---" % (j, C.dec(c, 30)))
    for t in (-1, 0, 1, 2, 5, 8, 12, 20, 50, 200):
        K = c * (1 + F(t, 10 ** 12)) if t >= 0 else c * (1 - F(1, 10 ** 12))
        r = cmp_num(j, K)
        feas_j = C.R.feasible_decision(j, 92, K, DLO, DHI, CIV)
        p("      相对偏移 %+ .0e ：j 可行？ %s ；比较 = %s" % (
            float(F(t, 10 ** 12)), feas_j, r))

p("")
p("[2] 窗口右端二分（j = 90 与 j = 89）：K 使 numerator(j) = numerator(j-1)")
for j in (90, 89):
    c = mid[j]
    Ka = c * (1 + F(1, 10 ** 13))       # 预期 -（窗口内）
    Kb = c * (1 + F(2, 10 ** 12))       # 预期 +（窗口外）
    ca, cb = cmp_num(j, Ka), cmp_num(j, Kb)
    p("    j = %d ：左端偏移 1e-13 -> %s ；右端偏移 2e-12 -> %s" % (j, ca, cb))
    if ca == "jm1_smaller" and cb == "j_smaller":
        for _ in range(50):
            Km = (Ka + Kb) / 2
            cm = cmp_num(j, Km)
            if cm == "jm1_smaller":
                Ka = Km
            elif cm == "j_smaller":
                Kb = Km
            else:
                break
        rel_lo = (Ka - c) / c
        rel_hi = (Kb - c) / c
        p("         窗口右端 K*_j ∈ [%s, %s]" % (C.dec(Ka, 24), C.dec(Kb, 24)))
        p("         相对窗口宽度 ∈ [%s, %s]" % (C.dec(rel_lo, 24), C.dec(rel_hi, 24)))
        p("         对照 route-5.md:230 的 2e-24 与 r4b [6] 的 1.5361313e-23：")
        p("           2e-24 落入？ %s ；1.5361313e-23 落入？ %s" % (
            rel_lo <= F(2, 10 ** 24) <= rel_hi, rel_lo <= F(15361313, 10 ** 31) <= rel_hi))
    else:
        p("         端点未分离（%s / %s），未二分。" % (ca, cb))

p("")
p("[3] j = 91 与 j = 92：验证其门槛处新档立即获胜（无窗口）")
for j in (91, 92):
    c = mid[j]
    for t in (0, 1, 10, 100):
        K = c * (1 + F(t, 10 ** 12))
        r = cmp_num(j, K)
        p("    j = %d 相对偏移 %+.0e ：比较 = %s" % (j, float(F(t, 10 ** 12)), r))

p("")
p("[4] 机制说明（供报告引用）")
p("    窗口的主导项是 3(j-1)/(2^v-1)^delta：在门槛处 2^v = 2^C ≈ 1.338×10^21，")
p("    该项约为 9×10^-32，比 3/(2^C-1) 与 97/(54X0) 之差（约 1.7×10^-42）大 10^10 倍。")
p("    它不是 route-5 引用的 log2(1+2^-C)（约 1.1×10^-21）：后者只在两边都")
p("    忽略 (2^v-1)^delta 项的近似判据下才是窗口尺度。本脚本的 [1]、[2] 两节")
p("    直接比较完整的 numerator（含全部三项），不依赖任何近似判据。")
p("    总用时 %.1f 秒。" % (time.time() - t_start))

open(HERE + "/results/r4b2_window_probe.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/r4b2_window_probe.out")
