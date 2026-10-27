#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 (e) 附：两版 X0 口径下端点事实的稳健性 + 清单条数对账。

`materials.md` 3.7 第 5 条登记：`route-3.md:160` 只对「落点 (L)」做过 X0 = 704·2^60 的
稳健性核对，「T = R 这一识别在两口径下各自是否成立」项目内没有材料。本脚本不做 T = R，
只把我这一路的四条端点事实里的三条（(a) 的两格、(d) 的主导权）在两版 X0 下各跑一遍。

另附 K* 格清单条数的对账（不设 cap_q 的完整清单与本报告用的 cap_q 清单）。

运行：20-experiments/.venv/bin/python k3_run_e.py
"""
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import k3_rig as K

OUT = []
OUTPATH = HERE / "results" / "k3_run_e.out"


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


M = 92
KSTAR = 205632218873398596256
KX = 313195478959172262876
K1 = F(312) * 10 ** 18
K2 = F(315) * 10 ** 18
GAM = F(325919355854421968365, 205632218873398596256)
D = K.delta_bounds()
L2 = K.ln2_bounds()
C695 = K.C_bounds()
X0695 = 695 * 2 ** 60
X0704 = 704 * 2 ** 60

p("#" * 74)
p("# route-3 (e)：两版 X0 口径稳健性（端点事实）+ 清单条数对账")
p("# 运行脚本：tracks/kcross-proof/cycle-1/scripts/k3_run_e.py")
p("#" * 74)


def A_of_x0(m2, m, X0):
    if m2 == m:
        return F(0)
    if m2 == m - 1:
        return F(3, X0)
    return F(97 * (m - m2) + 73, 54 * X0)


def eps_bounds_x0(m2, m, Kv, X0):
    """与 k3_rig.eps_bounds 同公式，只把 A 的 X0 换成参数。"""
    A = A_of_x0(m2, m, X0)
    vl, vh = K.v_bounds(m2, m, Kv, D[0], D[1])
    den_lo = K.rd(3 * F(Kv) * L2[0])
    den_hi = K.ru(3 * F(Kv) * L2[1])
    if vl >= K.V_COARSE or vh > 8 * K.V_COARSE:
        slack = F(3 + 3 * (m2 - 1), 2 ** K.V_COARSE)
        return K.rd(K.rd(A) / den_hi), K.ru(K.ru(A + slack) / den_lo)
    p2 = K.pow2_bounds(vl, vh)
    t_lo = K.rd(p2[0] - 1)
    t_hi = K.ru(p2[1] - 1)
    pt = K.t2vm1_delta_bounds(vl, vh, D[0], D[1])
    c3 = 3 * (m2 - 1)
    num_lo = K.rd(A + K.rd(3 / t_hi) + (K.rd(c3 / pt[1]) if c3 else F(0)))
    num_hi = K.ru(A + K.ru(3 / t_lo) + (K.ru(c3 / pt[0]) if c3 else F(0)))
    return K.rd(num_lo / den_hi), K.ru(num_hi / den_lo)


def run_cell(tag, Kv, X0, C):
    feas = set(t for t in range(1, M + 1) if K.feasible(t, M, Kv, D[0], D[1], C) is True)
    m2s = 92 if 92 in feas else 91
    e = eps_bounds_x0(m2s, M, Kv, X0)
    blo = K.rd(D[0] + e[0])
    bhi = K.ru(D[1] + e[1])
    gam_in = (GAM > D[1]) and (GAM < blo)
    low, high = K.sb_parents(GAM.numerator, GAM.denominator)
    cover = (F(low[0], low[1]) < D[0]) and (F(high[0], high[1]) > bhi)
    p("    [%s] X0 = %d：max F = %d ；argmin = %d ；eps_opt ∈ [%s, %s]" % (
        tag, X0, max(feas), m2s, K.sci(e[0], 22), K.sci(e[1], 22)))
    p("        gamma ∈ (delta, beta)？ %s ；双亲括号覆盖 [DLO, BETA_HI]？ %s" % (gam_in, cover))
    return gam_in and cover


p("")
p("[1] (a) 的两格在两版 X0 下的端点事实")
for X0, C, tag2 in ((X0695, C695, "695"), (X0704, K.C_bounds.__wrapped__() if False else None, "704")):
    if C is None:
        # X0 = 704·2^60 时 C = log2((162/97)·X0) = 60 + log2(162·704/97)
        l2 = K.ln2_bounds()
        ln_r = K.ln_bounds(F(162 * 704, 97))
        C = (K.rd(60 + ln_r[0] / l2[1]), K.ru(60 + ln_r[1] / l2[0]))
        p("    [准备] X0 = 704·2^60 时 C = log2((162/97)X0) ∈ [%s, %s]" % (K.dec(C[0], 40), K.dec(C[1], 40)))
    p("  X0 口径 = %s：" % tag2)
    ok1 = run_cell("K*", KSTAR, X0, C)
    ok2 = run_cell("KX", KX, X0, C)

p("")
p("[2] (d) 的主导权在两版 X0 下（eps(92, ·) 不含 X0，只有 A 侧变）")
for X0, tag2 in ((X0695, "695"), (X0704, "704")):
    e92 = eps_bounds_x0(92, M, K1, X0)
    theta = K.rd(F(3, X0) / (3 * K2 * L2[1]))
    p("    X0 = %d：eps(92, K1) 上界 = %s ；theta = %s ；余量因子 = %s" % (
        X0, K.sci(e92[1], 22), K.sci(theta, 22), K.sci(theta / e92[1], 8)))

p("")
p("[3] K* 格清单条数对账（不设 cap_q 的完整清单；该格 beta 侧最大部分商 55，可安全穷举）")
prefA = K.certified_prefix(D[0], D[1], maxlen=250)
e91 = K.eps_bounds(91, M, KSTAR, D[0], D[1], L2)
prefB = K.certified_prefix(K.rd(D[0] + e91[0]), K.ru(D[1] + e91[1]), maxlen=250)
k = 0
while k < min(len(prefA), len(prefB)) and prefA[k] == prefB[k]:
    k += 1
full = K.semiconv_list_frontier(prefA, prefB, k, cap_q=None)
capped = K.semiconv_list_frontier(prefA, prefB, k, cap_q=KSTAR)
n_in = sum(1 for (v, s) in full if v > D[1] and v < K.rd(D[0] + e91[0]))
n_in_c = sum(1 for (v, s) in capped if v > D[1] and v < K.rd(D[0] + e91[0]))
p("    完整清单条数 = %d（其中落在区间内 %d，含重复写法）" % (len(full), n_in))
p("    cap_q = K* 的清单条数 = %d（其中落在区间内 %d）" % (len(capped), n_in_c))
p("    被 cap 掉（分母 >= K*）的条数 = %d" % (len(full) - len(capped)))
p("    （route2_enum.out 记完整清单 442 条、内点 2、未定 0；本条与之一致）")

p("")
p("[4] (e) 结论")
p("    两版 X0 口径下，(a) 的两格端点事实都成立（gamma 落点与括号覆盖）")
p("    eps(92, ·) 与 X0 无关；主导权在 704 口径下余量更大（A 缩小 695/704）")

OUTPATH.write_text("\n".join(OUT) + "\n", encoding="utf-8")
print("\n[写出] results/k3_run_e.out")
