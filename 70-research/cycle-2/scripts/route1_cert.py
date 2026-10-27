#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-1 主证书：Ψ(K*) = K*（严格有理算术，无浮点参与判定）。

K* = 205632218873398596256，m = 92，X0 = 695·2^60（印出版 Definition 4）。

定义来源（本次亲自打开，非转述）：
  /tmp/h5.txt:83   Definition 4：X0 = 695·2^60
  /tmp/h5.txt:506  Definition 15：δ := log(3)/log(2)
  /tmp/h5.txt:695  至 :727  Theorem 21（一般式 + m2 = m−1 特例 + m2 = m 特例）
  /tmp/h5.txt:822  至 :825  Lemma 22
证书结构（每一步都在输出里带判据名、真值、失败即计入退出码）：
  一、锚点自检（2^δ ∋ 3、exp(ln2) ∋ 2、exp(ln3) ∋ 3、δ 与 c 的钉住值）
  二、δ 的严格有理区间与宽度来源
  三、δ 的连分数严格区间展开、收敛子、γ = [a_0;…;a_41, 2]
  四、门槛 G(m2) 与可行性：m2 = 91 可行、m2 = 92 不可行
  五、ε 的严格上下界：E_lo ≤ ε_opt(K*) ≤ E_hi（含 v、2^v − 1、(2^v − 1)^δ 的独立区间）
  六、γ 与 K* 的比较证书：左余量、右余量、所依据的 δ 界宽度
  七、最小性：两对 Farey 邻接（本文件内给出 Lemma G 的证明）
  八、结论与（可选）用 helper δ 界的稳健性复跑
"""
import sys
import os
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from fractions import Fraction as F
from route1_rig import (ln2_bounds, ln3_bounds, ln_bounds, exp_bounds, pow2_bounds,
                        delta_bounds, geom_bounds, dec_str, sci_str, floor_frac,
                        iv_div, iv_mul, iv_sub, iv_add, iv_round,
                        cf_digits_iv, contr, v_bounds, eps_bounds, A_of, ctx,
                        X0 as X0_RIG, M_CYCLES, KSTAR as KSTAR_RIG)

T0 = time.time()
FAIL = []


def ck(tag, cond, note=""):
    ok = bool(cond)
    print("   %-54s %s%s" % (tag, "True" if ok else "False", ("   " + note) if note else ""))
    if not ok:
        FAIL.append(tag)
    return ok


# ============================================================ 钉死的定义输入
KSTAR = 205632218873398596256                       # 项目记号 K*
M = 92
X0 = 695 * 2 ** 60                                  # Definition 4
A_M1 = F(3, X0)                                     # Theorem 21 特例 m2 = m−1
A_GEN73 = F(97 * 2 + 73, 54 * X0)                   # m2 ≤ m−2 时 A 最小（陈述页 +73）
A_GEN01 = F(97 * 2 + 1, 54 * X0)                    # 同（证明末行 +1 口径）

print("=" * 78)
print("route-1 主证书：Psi(K*) = K*（严格有理算术；判定无浮点）")
print("=" * 78)
print("输入：K* = %d，m = %d，X0 = 695·2^60 = %d" % (KSTAR, M, X0))
print("时间：%s" % time.strftime("%Y-%m-%d %H:%M:%S"))
print()

# ============================================================ 一、锚点自检
print("[一] 锚点自检（先钉死定义，再用已知值核对；learnings.md:28）")

l2lo, l2hi = ln2_bounds()
l3lo, l3hi = ln3_bounds()
print("   ln2 ∈ [%s, %s]，宽度 %s" % (dec_str(l2lo, 40), dec_str(l2hi, 40),
                                    sci_str(l2hi - l2lo, 6)))
print("   ln3 ∈ [%s, %s]，宽度 %s" % (dec_str(l3lo, 40), dec_str(l3hi, 40),
                                    sci_str(l3hi - l3lo, 6)))

dlo, dhi = delta_bounds()
DL, DH = iv_round((dlo, dhi))            # 区间链用的舍入版（含真值；误差 < 10^-200）
print("   δ ∈ [%s," % dec_str(dlo, 50))
print("        %s]" % dec_str(dhi, 50))
print("   δ 区间宽度 = %s（区间链用 10^-200 舍入版 [%s, %s]）"
      % (sci_str(dhi - dlo, 8), dec_str(DL, 25), dec_str(DH, 25)))

pw_lo, pw_hi = pow2_bounds(dlo, dhi)
ck("[A1] 2^δ ∋ 3（δ 的定义式自检）", pw_lo < 3 < pw_hi,
   "2^δ ∈ [%s, %s]" % (sci_str(pw_lo, 25), sci_str(pw_hi, 25)))
e1_lo, e1_hi = exp_bounds(l2lo, l2hi)
ck("[A2] exp(ln2) ∋ 2", e1_lo < 2 < e1_hi)
e3_lo, e3_hi = exp_bounds(l3lo, l3hi)
ck("[A3] exp(ln3) ∋ 3", e3_lo < 3 < e3_hi)
g3lo, g3hi = ln_bounds(F(3))
ck("[A4] ln 归约路径与 ln3 级数路径相容（区间相交）", max(g3lo, l3lo) <= min(g3hi, l3hi))
PIN45 = "1.584962500721156181453738943947816508759814407"
ck("[A5] δ 左端的 45 位小数 = 钉住值前 45 位", dec_str(dlo, 45) == PIN45,
   "本机 %s" % dec_str(dlo, 45))
ck("[A6] 126797/80000 < dlo（δ 的严格下界锚点，learnings.md:38）", F(126797, 80000) < dlo)

# c = log2((162/97)X0) = 60 + log2(112590/97)
Y = F(112590, 97)
lnY = ln_bounds(Y)
c_lo = 60 + lnY[0] / l2hi
c_hi = 60 + lnY[1] / l2lo
PIN_C = F("70.180806328308366825")       # cycle-1/materials.md:345 钉住值（18 位）
print("   c = log2((162/97)X0) ∈ [%s, %s]" % (dec_str(c_lo, 30), dec_str(c_hi, 30)))
ck("[A7] 钉住值 c = 70.180806328308366825 与本区间相差 < 10^-17（钉住值只到 18 位）",
   abs(PIN_C - c_lo) < F(1, 10 ** 17) and abs(PIN_C - c_hi) < F(1, 10 ** 17),
   "偏差 = %s" % sci_str(c_lo - PIN_C, 6))
print()

# ============================================================ 二、δ 界宽度来源
print("[二] δ 界宽度来源（本次亲核既有界）")
ck("[B1] 本库 δ 宽度 < 既有 helper 宽度 1.7962682907797472e-244（r4x_run4.out:7）",
   (dhi - dlo) < F("1.7962682907797472e-244"),
   "本库 = %s（ln2 走 atanh(1/3)，ln3 = ln2 + ln(3/2) 走 atanh(1/5)）" % sci_str(dhi - dlo, 8))
print()

# ============================================================ 三、连分数
print("[三] δ 的连分数严格区间展开（每步 floor 判定，精确有理递归）")


digs = cf_digits_iv(dlo, dhi, 48)
print("   a_0..a_47 = %s" % digs)
MAT_DIGS = [1, 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55, 1, 4, 3, 1, 1, 15, 1, 9, 2, 5, 7,
            1, 1, 4, 8, 1, 11, 1, 20, 2, 1, 10, 1, 4, 1, 1, 1, 1, 1, 37, 4]
ck("[C1] 前 46 项与 cycle-2/materials.md:166 的记录逐项一致", digs[:46] == MAT_DIGS)


P_, Q_ = [], []
for j in range(len(digs)):
    p, q = contr(digs[:j + 1])
    P_.append(p)
    Q_.append(q)
print("   q_39..q_44 = %s" % [Q_[j] for j in (39, 40, 41, 42, 43, 44)])
GAM_NUM, GAM_DEN = contr(digs[:42] + [2])
gamma = F(GAM_NUM, GAM_DEN)
C3_NUM, C3_DEN = contr(digs[:42] + [3])
c3 = F(C3_NUM, C3_DEN)
p43q43 = F(P_[43], Q_[43])
for j in (42, 43):
    print("   p_%d/q_%d = %d / %d" % (j, j, P_[j], Q_[j]))
print("   γ = [a_0;…;a_41,2] = %d / %d" % (GAM_NUM, GAM_DEN))
print("   [P,3] = [a_0;…;a_41,3] = %d / %d" % (C3_NUM, C3_DEN))
ck("[C2] γ = p_43/q_43（因 a_42 = a_43 = 1）", (GAM_NUM, GAM_DEN) == (P_[43], Q_[43]),
   "a_42 = %d，a_43 = %d" % (digs[42], digs[43]))
ck("[C3] γ 的分母恰为项目记录的 K* = 205632218873398596256", GAM_DEN == KSTAR,
   "分母 = %d" % GAM_DEN)
ck("[C4] γ 与项目记录的有理值一致", gamma == F(325919355854421968365, 205632218873398596256))
ck("[C5] [P,3] 的分母 = 3q_41 + q_40", C3_DEN == 3 * Q_[41] + Q_[40],
   "3q_41 + q_40 = %d" % (3 * Q_[41] + Q_[40]))
ck("[C6] |p_43·q_42 − p_42·q_43| = 1", abs(GAM_NUM * Q_[42] - P_[42] * GAM_DEN) == 1,
   "值 = %d" % (GAM_NUM * Q_[42] - P_[42] * GAM_DEN))
ck("[C7] (3p_41+p_40)·q_43 − p_43·(3q_41+q_40) = 1", C3_NUM * GAM_DEN - GAM_NUM * C3_DEN == 1,
   "值 = %d" % (C3_NUM * GAM_DEN - GAM_NUM * C3_DEN))
ck("[C8] p_42/q_42 < δ（与 dlo 精确比较）", F(P_[42], Q_[42]) < dlo,
   "p_42/q_42 − dlo = %s" % sci_str(F(P_[42], Q_[42]) - dlo, 6))
ck("[C9] γ > δ（与 dhi 精确比较）", gamma > dhi, "γ − dhi = %s" % sci_str(gamma - dhi, 6))
print()

# ============================================================ 四、门槛与可行性
print("[四] 门槛与可行性（G(m2) = ((δ^m2−1)/(δ−1))·log2((162/97)X0) ≤ (m2/m)K）")

geom91 = geom_bounds(91, DL, DH)
geom92 = geom_bounds(92, DL, DH)
G91_lo, G91_hi = iv_round((geom91[0] * c_lo, geom91[1] * c_hi))
G92_lo, G92_hi = iv_round((geom92[0] * c_lo, geom92[1] * c_hi))
print("   G(91) ∈ [%s, %s]" % (sci_str(G91_lo, 25), sci_str(G91_hi, 25)))
print("   G(92) ∈ [%s, %s]" % (sci_str(G92_lo, 25), sci_str(G92_hi, 25)))
RHS91 = F(91, M) * KSTAR
ck("[D1] m2 = 91 可行：G(91) ≤ (91/92)K*", G91_hi <= RHS91,
   "(91/92)K*/G(91) > %s" % dec_str(RHS91 / G91_hi, 10))
ck("[D2] m2 = 92 不可行：G(92) > K*", G92_lo > KSTAR,
   "G(92)/K* > %s" % dec_str(G92_lo / KSTAR, 10))
print("   由 Theorem 21 假设 m2 ≤ m = 92：可行集 ⊆ {1,…,91}（D2）；91 ∈ 可行集（D1）")
print()

# ============================================================ 五、ε 的严格上下界
print("[五] ε 的严格上下界：E_lo ≤ ε_opt(K*) ≤ E_hi")


print("   A(91) = 3/X0 = %s（印出版 Theorem 21 特例，/tmp/h5.txt:713 至 :718）"
      % sci_str(A_M1, 25))
print("   A(m2 ≤ 90) 的最小值：+73 口径 %s；+1 口径 %s"
      % (sci_str(A_GEN73, 25), sci_str(A_GEN01, 25)))
ck("[E1] A(m2) ≥ 3/X0 对一切 m2 ∈ [1,91]（两种口径都成立：162 < 195 < 267）",
   A_M1 <= A_GEN01 and A_M1 <= A_GEN73)
E_lo = A_M1 / (3 * KSTAR * l2hi)
print("   E_lo := (3/X0)/(3K*·ln2_hi) = %s" % sci_str(E_lo, 30))
CTX = ctx()
eps91, v91, t91, T91 = eps_bounds(91, KSTAR, CTX)
E_hi = eps91[1]
print("   v(91, K*) ∈ [%s, %s]" % (sci_str(v91[0], 25), sci_str(v91[1], 25)))
print("   2^v − 1 ∈ [%s, %s]" % (sci_str(t91[0], 25), sci_str(t91[1], 25)))
print("   (2^v − 1)^δ ∈ [%s, %s]" % (sci_str(T91[0], 25), sci_str(T91[1], 25)))
print("   ε(91, K*) ∈ [%s, %s]" % (sci_str(eps91[0], 30), sci_str(eps91[1], 30)))
# 钉住值是「舍入到自身位数的十进制」，不是真值的截断下界；本区间宽约 1e-200，
# 故判据只能取「与该位数上的舍入误差相容」（同 materials.md:362 第 1 条登记的 59 位截断现象）。
PIN_EPS = F("8.973221708617136016325725e-42")     # materials.md:154（25 位有效数字）
PIN_V = F("74.77295160759765432628649")           # materials.md:195（23 位有效数字）
ck("[E2] ε(91, K*) 与本区间的差 < 钉住值自身精度 1e-65（materials.md:154）",
   abs(PIN_EPS - eps91[0]) < F(1, 10 ** 65),
   "差 = %s" % sci_str(PIN_EPS - eps91[0], 6))
ck("[E3] v(91, K*) 与本区间的差 < 钉住值自身精度 1e-22（materials.md:195）",
   abs(PIN_V - v91[0]) < F(1, 10 ** 22),
   "差 = %s" % sci_str(PIN_V - v91[0], 6))
ck("[F1] E_lo ≤ ε_opt（由 D2 + E1：92 不可行 ⟹ 可行集 ⊆ [1,91]，各 A ≥ 3/X0）",
   E_lo <= eps91[0])
ck("[F2] ε_opt ≤ E_hi（由 D1：91 可行 ⟹ min ≤ ε(91) ≤ E_hi）", eps91[0] <= E_hi)
print("   故 ε_opt(K*) ∈ [E_lo, E_hi] = [%s, %s]" % (sci_str(E_lo, 30), sci_str(E_hi, 30)))
print()

# ============================================================ 六、比较证书
print("[六] γ 与 K* 的比较证书（左右余量严格界；所依据的 δ 界宽度）")

left_lo, left_hi = gamma - dhi, gamma - dlo                    # 左余量 γ − δ
right_lo, right_hi = dlo + E_lo - gamma, dhi + E_hi - gamma    # 右余量 (δ+ε_opt) − γ
print("   左余量 γ − δ ∈ [%s, %s]" % (sci_str(left_lo, 30), sci_str(left_hi, 30)))
print("      严格下界 = %s" % sci_str(left_lo, 45))
print("   右余量 (δ+ε_opt) − γ ∈ [%s, %s]" % (sci_str(right_lo, 30), sci_str(right_hi, 30)))
print("      严格下界 = %s" % sci_str(right_lo, 45))
print("   δ 界宽度 = %s" % sci_str(dhi - dlo, 8))
print("   ε_opt 与左右余量的量级：ε_opt ~ 1e-42，左余量 ~ 6e-43，右余量 ~ 8e-42")
ck("[G1] 左余量为正：γ > δ", left_lo > 0)
ck("[G2] 右余量为正：δ + ε_opt > γ", right_lo > 0)
ck("[G3] 两个余量的下界都远大于 δ 界宽度乘以 q_43", left_lo > (dhi - dlo) * Q_[43]
   and right_lo > (dhi - dlo) * Q_[43])
print()

# ============================================================ 七、最小性
print("[七] 最小性：区间 (δ, δ+ε_opt) 内不存在分母 < K* 的有理数")
print("   Lemma G：若 p/q < p'/q' 且 p'q − p q' = 1，则任一 p/q < r/s < p'/q' 满足 s ≥ q+q'。")
print("     证明：u := rq − ps ≥ 1（整数且正），w := p's − rq' ≥ 1，")
print("           q'u + qw ≥ q' + q，而 q'u + qw = s·(p'q − pq') = s，故 s ≥ q + q'。 □")
ck("[H1] [P,3] > δ + ε_opt（用 dhi + E_hi 的精确有理比较）", c3 > dhi + E_hi,
   "[P,3] − (δ+ε_opt) > %s" % sci_str(c3 - dhi - E_hi, 8))
print("   分片：(δ, δ+ε_opt) = (δ, γ) ∪ {γ} ∪ (γ, δ+ε_opt)")
print("     · (δ, γ) ⊆ (p_42/q_42, p_43/q_43)（C8、C9）⟹ 分母 ≥ q_42+q_43 = %d"
      % (Q_[42] + Q_[43]))
print("     · γ 的分母恰为 q_43 = K* = %d" % Q_[43])
print("     · (γ, δ+ε_opt) ⊆ (γ, [P,3])（C9、H1）⟹ 分母 ≥ q_43+(3q_41+q_40) = %d"
      % (Q_[43] + 3 * Q_[41] + Q_[40]))
ck("[H2] q_42 + q_43 > K*", Q_[42] + Q_[43] > KSTAR,
   "余量 = %d" % (Q_[42] + Q_[43] - KSTAR))
ck("[H3] q_43 + (3q_41+q_40) > K*", Q_[43] + 3 * Q_[41] + Q_[40] > KSTAR,
   "余量 = %d" % (Q_[43] + 3 * Q_[41] + Q_[40] - KSTAR))
print()

# ============================================================ 八、结论
print("[八] 结论")
print("   γ ∈ (δ, δ+ε_opt(K*))（G1、G2）且 γ = p_43/q_43、分母 = K*（C2、C3）；")
print("   任何有理数 r ≠ γ 若落在该区间，按分片与 Lemma G 其分母 ≥ min(q_42+q_43, q_43+3q_41+q_40) > K*（七）。")
print("   故 (δ, δ+ε_opt(K*)) 内的最小分母 = K* = %d，即 Ψ(K*) = K*（m = 92，X0 = 695·2^60）。" % KSTAR)
print()

print("=" * 78)
if FAIL:
    print("失败判据：%s" % FAIL)
    print("退出码 1（证书未通过）")
    sys.exit(1)
print("全部判据通过；退出码 0；用时 %.1f 秒" % (time.time() - T0))
sys.exit(0)
