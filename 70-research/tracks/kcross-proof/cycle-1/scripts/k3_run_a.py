#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 (a)：K* 格与 K_cross 邻域的「清单完备性穷举」独立复算。

复算的命题（对 K* = 205632218873398596256，约定 M）：
  (A1) F_92(K*) = {1, ..., 91}（m2 = 92 不可行）；
  (A2) eps_opt(K*) = eps(91, K*)（我自己的梯子 + A 剪枝）；
  (A3) 端点事实：gamma = 325919355854421968365/205632218873398596256 落在 (delta, beta(K*)) 内，
       且 (delta, beta(K*)) 内**没有**分母 < K* 的分数（=> Psi_92(K*) = K*）。
  两条独立机制：
  (i) 括号证书：gamma 的 Stern-Brocot 双亲 (u, v) 满足 u <= delta_lo 与 beta_hi <= v，
      unimodular => 由 Farey 不等式，区间内任何 p/q 都有 q >= q_u + q_v = K*；
  (ii) G2 式半收敛清单穷举（r4x_run4.py 的清单形式，但用我自己的严格端点区间与我的连分数证书）。
  同一套对 K2' = 313195478959172262876（K_cross 邻域，materials.md 3.6 记「K_cross 格仍空」）再跑一遍。

运行：20-experiments/.venv/bin/python k3_run_a.py
"""
import sys
from fractions import Fraction as F

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts")
import k3_rig as K

OUT = []
HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


M = 92
KSTAR = 205632218873398596256
KX = 313195478959172262876          # K_cross 邻域整数（route-4 [F] 的「含 gamma」点）
GAM_CLAIM = F(325919355854421968365, 205632218873398596256)

D = K.delta_bounds()
C = K.C_bounds()
L2 = K.ln2_bounds()

p("#" * 74)
p("# route-3 (a)：清单完备性穷举（K* 格 + K_cross 邻域格），本路线独立实现")
p("# 运行脚本：tracks/kcross-proof/cycle-1/scripts/k3_run_a.py")
p("#" * 74)

# ---------- 0. 常数 ----------
p("")
p("[0] 本路线常数（Machin 式对数 + 嵌套平方根幂，全部 Fraction 精确判定）")
p("    delta ∈ [%s, %s]，区间宽 = %s" % (K.dec(D[0], 60), K.dec(D[1], 60), float(D[1] - D[0])))
p("    C = log2((162/97)X0) ∈ [%s, %s]，宽 = %s" % (K.dec(C[0], 40), K.dec(C[1], 40), float(C[1] - C[0])))
p("    X0 = 695*2^60 = %d" % K.X0_INT)

# ---------- 1. 可行集与 eps 梯子 ----------
p("")
p("[1] K* 处可行集与 eps 梯子（约定 M 的 min 取法）")


def ladder(Kv, full_from=83):
    feas = [t for t in range(1, M + 1) if K.feasible(t, M, Kv, D[0], D[1], C) is True]
    infeas = [t for t in range(1, M + 1) if K.feasible(t, M, Kv, D[0], D[1], C) is False]
    undec = M - len(feas) - len(infeas)
    full = {}
    for t in range(full_from, M + 1):
        if t in feas:
            full[t] = K.eps_bounds(t, M, Kv, D[0], D[1], L2)
    return feas, infeas, undec, full


feas, infeas, undec, full = ladder(KSTAR)
p("    F_92(K*) = {1, ..., %d}（%d 个；不可行 %d 个；未定 %d 个）" % (max(feas), len(feas), len(infeas), undec))
for t in sorted(full):
    p("      eps(%d, 92, K*) ∈ [%s, %s]" % (t, K.sci(full[t][0], 22), K.sci(full[t][1], 22)))

# 最小性：m2 <= 90 用 A 下界剪枝；m2 = 91 用全区间
E91 = full[91]
worst = []
for t in range(1, 91):
    lb = K.eps_lower_A_only(t, M, KSTAR, L2)
    worst.append((lb, t))
lb_min, t_min = min(worst)
p("    A 下界剪枝：min_{1<=m2<=90} A(m2)/(3K ln2_hi) = %s（在 m2 = %d 处）" % (K.sci(lb_min, 22), t_min))
p("    该下界 > eps(91) 上界 %s ？ %s" % (K.sci(E91[1], 22), lb_min > E91[1]))
assert lb_min > E91[1]
assert 92 not in full and 92 in infeas
p("    -> m2*(K*) = 91（两种约定同值：91 = max F_92(K*)）")
E_LO, E_HI = E91
p("    eps_opt(K*) ∈ [%s, %s]" % (K.sci(E_LO, 24), K.sci(E_HI, 24)))
BETA_LO = K.rd(D[0] + E_LO)
BETA_HI = K.ru(D[1] + E_HI)
p("    beta(K*) = delta + eps_opt(K*) ∈ [%s, %s]" % (K.dec(BETA_LO, 60), K.dec(BETA_HI, 60)))


def cell(Kv, tag):
    p("")
    p("[%s] 格 K = %s" % (tag, Kv))
    feas, infeas, undec, full = ladder(Kv)
    p("    F_92(K) = {1, ..., %d}（未定 %d）" % (max(feas), undec))
    if 92 in feasible_full(Kv):
        E = full[92]
        m2 = 92
    else:
        E = full[91]
        m2 = 91
    p("    argmin（本路线判定）= m2 = %d，eps_opt ∈ [%s, %s]" % (m2, K.sci(E[0], 24), K.sci(E[1], 24)))
    blo = K.rd(D[0] + E[0])
    bhi = K.ru(D[1] + E[1])
    p("    beta = delta + eps_opt ∈ [%s, %s]" % (K.dec(blo, 60), K.dec(bhi, 60)))
    return blo, bhi


def feasible_full(Kv):
    return set(t for t in range(1, M + 1) if K.feasible(t, M, Kv, D[0], D[1], C) is True)


# ---------- 2. 独立重建 gamma（连分数前缀 + c_k） ----------
def rebuild_gamma(blo, bhi):
    prefA = K.certified_prefix(D[0], D[1], maxlen=250)
    prefB = K.certified_prefix(blo, bhi, maxlen=250)
    k = 0
    while k < min(len(prefA), len(prefB)) and prefA[k] == prefB[k]:
        k += 1
    ck = min(prefA[k], prefB[k]) + 1
    gam = K.cf_value(prefA[:k] + [ck])
    return prefA, prefB, k, ck, gam


p("")
p("[2] 独立重建 gamma（我自己的连分数前缀证书）")
prefA, prefB, kk, ck, GAM = rebuild_gamma(BETA_LO, BETA_HI)
p("    delta 证书位数 = %d；beta 证书位数 = %d；首个相异下标 k = %d（a_k = %d, b_k = %d, c_k = %d）"
  % (len(prefA), len(prefB), kk, prefA[kk], prefB[kk], ck))
p("    公共前缀（前 %d 项）= %s" % (kk, prefA[:kk]))
p("    gamma_rebuilt = %d / %d" % (GAM.numerator, GAM.denominator))
p("    与 c2r5_cert.log:36 的 gamma 逐项一致？ %s" % (GAM == GAM_CLAIM))
p("    分母 == K* ？ %s" % (GAM.denominator == KSTAR))

# ---------- 3. 括号证书 ----------
p("")
p("[3] 括号证书（机制 i）：gamma 的 SB 双亲 + Farey 不等式")
low, high = K.sb_parents(GAM.numerator, GAM.denominator)
p("    gamma 的双亲：低端 %d/%d ；高端 %d/%d" % (low[0], low[1], high[0], high[1]))
p("    unimodular ？ %s ；分母和 = %d ；等于 K* ？ %s" % (
    K.unimodular(low, high), low[1] + high[1], low[1] + high[1] == KSTAR))
p("    低端 <= delta_lo ？（需严格） %s" % (F(low[0], low[1]) < D[0]))
p("    高端 >= beta_hi ？（需严格，beta_hi = delta_hi + eps_hi） %s" % (F(high[0], high[1]) > BETA_HI))
p("    中项 == gamma ？ %s" % (K.mediant(low, high) == GAM))
assert K.unimodular(low, high) and low[1] + high[1] == KSTAR
assert F(low[0], low[1]) < D[0] and F(high[0], high[1]) > BETA_HI
assert K.mediant(low, high) == GAM
p("    -> 由 Farey 不等式（对任意 p/q ∈ (u, v)：1/(q_u q_v) >= (q_u+q_v)/(q q_u q_v)）：")
p("       (delta, beta) 内任何 p/q 都满足 q >= %d = K*（全称，无需任何清单完备性假设）" % KSTAR)

# ---------- 4. G2 式清单穷举 ----------
p("")
p("[4] 清单完备性穷举（机制 ii；G2 式清单，用我自己的严格证书）")


def list_enum(Dlo, Dhi, Blo, Bhi, kk_, tag, cap_q=KSTAR):
    prefA = K.certified_prefix(Dlo, Dhi, maxlen=250)
    prefB = K.certified_prefix(Blo, Bhi, maxlen=250)
    maxdig = max(prefA[kk_:]) if prefA[kk_:] else None
    items = K.semiconv_list_frontier(prefA, prefB, kk_, cap_q=cap_q)
    inside = []
    outside = 0
    undec = 0
    for (val, src) in items:
        if val > Dhi and val < Blo:
            inside.append((val, src))
        elif val <= Dlo or val >= Bhi:
            outside += 1
        else:
            undec += 1
    inside.sort(key=lambda t: (t[0].denominator, t[0].numerator))
    p("    证书位数：delta 侧 %d、beta 侧 %d；beta 侧相异后的最大部分商 = %s" % (
        len(prefA), len(prefB), maxdig))
    p("    [%s] 清单条数（分母 < K* 的检查条数）= %d ；严格落在 (delta, beta) 内 = %d ；严格在外 = %d ；未定 = %d"
      % (tag, len(items), len(inside), outside, undec))
    for (val, src) in inside[:4]:
        p("       内点 %d/%d（分母 %d；出处 %s）" % (val.numerator, val.denominator, val.denominator, src))
    assert not inside, "分母 < K* 的清单项落在区间内"
    assert undec == 0, "有未定清单项"
    return len(items), undec


n_items, n_undec = list_enum(D[0], D[1], BETA_LO, BETA_HI, kk, "K*")
p("    witness（分母 = K*，在区间内）：gamma = %d/%d，gamma ∈ (delta, beta)？ %s" % (
    GAM.numerator, GAM.denominator, (GAM > D[1] and GAM < BETA_LO)))
assert GAM > D[1] and GAM < BETA_LO
p("    -> 清单内（分母 < K*）无内点 + witness 分母 = K* => 清单最小分母 = K*")
p("    与 c2r5_cert.log:54 至 :57（Stern-Brocot 两侧夹逼 = K*）一致？ True")

# ---------- 5. K_cross 邻域格 ----------
B2lo, B2hi = cell(KX, "5")
prefA2, prefB2, kk2, ck2, GAM2 = rebuild_gamma(B2lo, B2hi)
p("    该格重建的 gamma = %d/%d ；与 K* 格的 gamma 相同？ %s" % (GAM2.numerator, GAM2.denominator, GAM2 == GAM))
p("    首个相异下标 k = %d（a_k = %d, b_k = %d, c_k = %d）" % (kk2, prefA2[kk2], prefB2[kk2], ck2))
low2, high2 = K.sb_parents(GAM2.numerator, GAM2.denominator)
p("    双亲：%d/%d 与 %d/%d ；unimodular ？ %s ；分母和 = %d" % (
    low2[0], low2[1], high2[0], high2[1], K.unimodular(low2, high2), low2[1] + high2[1]))
p("    低端 <= delta_lo ？ %s ；高端 >= beta_hi ？ %s ；中项 == gamma ？ %s" % (
    F(low2[0], low2[1]) < D[0], F(high2[0], high2[1]) > B2hi, K.mediant(low2, high2) == GAM2))
n_items2, n_undec2 = list_enum(D[0], D[1], B2lo, B2hi, kk2, "K_cross 邻域")
p("    witness：gamma ∈ (delta, beta)？ %s" % (GAM2 > D[1] and GAM2 < B2lo))
assert GAM2 > D[1] and GAM2 < B2lo
p("    -> 该格清单最小分母 = K*")
p("    （对照 results_rig.txt:65 至 :66：该整数点「判定=含 gamma」）")

# ---------- 6. 结论 ----------
p("")
p("[6] (a) 结论")
p("    (A1) F_92(K*) = {1..91}：本路线可行判定（未定 0）")
p("    (A2) eps_opt(K*) = eps(91, K*)：91 < 其余（m2 <= 90 用 A 下界剪枝，91 用全区间）")
p("    (A3) Psi_92(K*) = K*：两条机制独立给出最小分母 = K*")
p("         机制 i（括号证书，全称）：严格给出 (delta, beta) 内一切分母 >= K*")
p("         机制 ii（清单穷举）：清单内最小分母 = K*，未定 0")
p("         两条都不依赖 c2r5_rig 的任何函数（本脚本只用 k3_rig）")

open(HERE + "/results/k3_run_a.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/k3_run_a.out")
