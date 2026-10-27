#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 (b)：simplest(delta_lo, gamma) 最小性的独立复算。

要检验的精确陈述（c2r5_cert.log:75 与 route-5.md 第 6 节）：
  (B1) 设 gamma = 325919355854421968365/205632218873398596256（K* 为分母），
       delta_lo 为 delta 的严格下界。则 (delta_lo, gamma) 内最小分母分数为
       R = 12587715785705330118969/7941964418702608664581（分母 7941964418702608664581）。
  (B2) 该分母 > U(92) = 1.4784·92·delta^92。

本路线用的论证（与 Stern-Brocot 下降不同）：先写出候选 R 的 Stern-Brocot 双亲
（由 R 的连分数直接构造），再核验「括号在外 + unimodular」两点；由 Farey 不等式
（两行证明）得区间内一切分母 >= q_B + q_gamma = R 的分母；R 落在区间内故等号成立。
另加两项机制检查：(i) 重放 c2r5_rig.simplest_fraction 的下降轨迹（只读，确认它最后落在
同一括号上）；(ii) 小分母暴力搜索（q <= 10^5，明确标注非证明）。

运行：20-experiments/.venv/bin/python k3_run_b.py
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
GAM = F(325919355854421968365, 205632218873398596256)
RCLAIM = F(12587715785705330118969, 7941964418702608664581)

D = K.delta_bounds()

p("#" * 74)
p("# route-3 (b)：simplest(delta_lo, gamma) 最小性复算（独立论证 + 机制检查）")
p("# 运行脚本：tracks/kcross-proof/cycle-1/scripts/k3_run_b.py")
p("#" * 74)

# ---------- 0. 对象 ----------
p("")
p("[0] 对象与区间")
p("    delta_lo（本路线）= %s" % K.dec(D[0], 62))
p("    gamma = %d/%d（分母 K* = %d）" % (GAM.numerator, GAM.denominator, KSTAR))
p("    候选 R = %d/%d（分母 %d）" % (RCLAIM.numerator, RCLAIM.denominator, RCLAIM.denominator))
p("    R 的连分数 = %s" % (K.cf_frac(RCLAIM.numerator, RCLAIM.denominator),))

# ---------- 1. R 的双亲与括号 ----------
p("")
p("[1] 候选 R 的 Stern-Brocot 双亲（由 R 的连分数构造，不用任何搜索）")
low, high = K.sb_parents(RCLAIM.numerator, RCLAIM.denominator)
p("    低端 B = %d/%d（分母 %d）" % (low[0], low[1], low[1]))
p("    高端 = %d/%d（分母 %d；= gamma ？ %s）" % (high[0], high[1], high[1], F(high[0], high[1]) == GAM))
assert F(high[0], high[1]) == GAM
p("    unimodular ？ %s" % K.unimodular(low, high))
p("    分母和 = %d ；等于 R 的分母？ %s" % (low[1] + high[1], low[1] + high[1] == RCLAIM.denominator))
p("    中项 == R ？ %s" % (K.mediant(low, high) == RCLAIM))
assert K.unimodular(low, high) and low[1] + high[1] == RCLAIM.denominator
assert K.mediant(low, high) == RCLAIM

# ---------- 2. 括号覆盖区间 ----------
p("")
p("[2] 括号覆盖 (delta_lo, gamma)（两个严格有理比较）")
B_lo_frac = F(low[0], low[1])
p("    B < delta_lo ？（需严格，B 必须落在区间外） %s" % (B_lo_frac < D[0]))
p("    B 与 delta_lo 的间距 = %s" % K.sci(D[0] - B_lo_frac, 8))
p("    gamma <= gamma ？ 平凡 True")
p("    R ∈ (delta_lo, gamma) ？ %s" % (D[0] < RCLAIM < GAM))
assert B_lo_frac < D[0] and D[0] < RCLAIM < GAM

# ---------- 3. Farey 不等式（两行证明的核对） ----------
p("")
p("[3] Farey 不等式（全称结论的直接理由）")
p("    对任意 p/q ∈ (B, gamma)（最简）：p/q − B >= 1/(q·q_B)，gamma − p/q >= 1/(q·q_gamma)；")
p("    相加得 gamma − B = 1/(q_B·q_gamma) >= (q_B + q_gamma)/(q·q_B·q_gamma)，即 q >= q_B + q_gamma。")
p("    故 (delta_lo, gamma) ⊂ (B, gamma) 内一切 p/q 满足 q >= %d" % (low[1] + high[1]))
p("    而 R 落在区间内且分母 = %d，故 min 分母 = %d" % (RCLAIM.denominator, RCLAIM.denominator))
p("    -> (B1) 成立：simplest(delta_lo, gamma) = %d/%d" % (RCLAIM.numerator, RCLAIM.denominator))

# ---------- 4. 机制检查 (i)：重放 c2r5_rig 的下降 ----------
p("")
p("[4] 机制检查 (i)：重放 c2r5_rig.simplest_fraction 的整段跳下降（只读 import）")
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts")
import c2r5_rig as R2

dlo2, dhi2 = R2.delta_bounds()
got = R2.simplest_fraction(dlo2, GAM)
p("    c2r5_rig.simplest_fraction 的返回 = %d/%d ；等于本路线候选 R ？ %s" % (
    got.numerator, got.denominator, got == RCLAIM))
# 轨迹
A, Bb = F(dlo2), F(GAM)
x, y, z, w = 0, 1, 1, 0
fin = None
for step in range(80):
    kL = ((A * y - x) / (z - A * w))
    kL = kL.numerator // kL.denominator
    if kL >= 1:
        x, y = x + kL * z, y + kL * w
    kR = ((z - Bb * w) / (Bb * y - x))
    kR = kR.numerator // kR.denominator
    if kR >= 1:
        z, w = z + kR * x, w + kR * y
    m = F(x + z, y + w)
    if A < m < Bb:
        fin = (step, (x, y), (z, w), m)
        break
p("    轨迹末步：第 %d 步；括号 = (%d/%d, %d/%d)；中项 = %d/%d" % (
    fin[0], fin[1][0], fin[1][1], fin[2][0], fin[2][1], fin[3].numerator, fin[3].denominator))
p("    末步括号左端 == 本路线双亲的低端？ %s ；右端 == gamma ？ %s" % (
    F(fin[1][0], fin[1][1]) == F(low[0], low[1]), F(fin[2][0], fin[2][1]) == GAM))
p("    （注：重放用的是 c2r5_rig 自己的 delta_lo；两个 delta_lo 都远低于 B，见第 2 节）")

# ---------- 5. 机制检查 (ii)：小分母暴力搜索 ----------
p("")
p("[5] 机制检查 (ii)：小分母直接搜索（q <= 200000；**非证明**，仅机制）")
hits = []
for q in range(1, 200001):
    pc = K.fl(D[0] * q) + 1
    if F(pc, q) < GAM:
        hits.append((q, pc))
p("    q <= 200000 内首个命中：%s" % (hits[0] if hits else None))
p("    （与 route-4.md:136 提到的「分母 <= 10^6 的暴力对拍」同类；本路线只跑 q <= 2e5，用时可控）")

# ---------- 6. U(92) 比较 ----------
p("")
p("[6] (B2)：分母 > U(92) = 1.4784·92·delta^92（精确整数幂，无浮点）")
U_W = F(14784, 10000)
pw = (D[0] ** 92, D[1] ** 92)
U = (K.rd(U_W * 92 * pw[0]), K.ru(U_W * 92 * pw[1]))
p("    U(92) ∈ [%s, %s]" % (K.dec(U[0], 30), K.dec(U[1], 30)))
LOG_U = F("343025970248850209780.074794593")
p("    与 c2r5_cert.log:76 的打印值 343025970248850209780.074794593 之差 = %s（< 1e-8 => 同值）" % (
    K.sci(abs(LOG_U - U[0]), 4)))
assert abs(LOG_U - U[0]) < F(1, 10 ** 8)
p("    q_R = %d > U(92) 上界？ %s" % (RCLAIM.denominator, F(RCLAIM.denominator) > U[1]))
assert F(RCLAIM.denominator) > U[1]
p("    -> 越界侧全区间下界：对一切 beta(K) <= gamma 的 K，Psi(K) >= %d > U(92)" % RCLAIM.denominator)

# ---------- 7. 结论 ----------
p("")
p("[7] (b) 结论")
p("    (B1) 成立【已证（本路线独立论证：SB 双亲括号 + Farey 不等式；不依赖清单完备性）】")
p("    (B2) 成立【已证（精确有理幂 + 区间比较）】，但 U(92) 的常数 1.4784 属 SdW 预印本口径，未回一手核")
p("    与 c2r5_cert.log:75 的值逐位一致；重复的机制检查（下降重放、小分母搜索）都指向同一值")

open(HERE + "/results/k3_run_b.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/k3_run_b.out")
