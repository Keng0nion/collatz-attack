#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽验 2：A5 的 6456 项阶梯与 92C、eps_ub 的独立重算。

内容（全部用本路 kc_tail_rig 的精确有理区间，不用 kcross-proof 的任何库）：
  1. 以本路的 delta 区间给出 delta_lo、delta_hi；
  2. 对每个 q <= 6456 取 p = floor(q*delta_lo) + 1（「p/q > delta」一切候选 p 的下界），
     判 p/q >= delta_hi + eps_ub；同时判 floor(q*delta_lo) == floor(q*delta_hi)（保证 p 就是最小候选）；
  3. eps_ub = eps(1, 92C) 的上界（A(1) + 3/(2^C - 1)）/(3*92C*ln2)，用本路区间；
  4. 6457 > 92C。
命令行：/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python sc2_a5_ladder.py
"""
import hashlib
import sys
from fractions import Fraction as F

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1/scripts")
import kc_tail_rig as R

PROOF = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts/results"
R2LOG = PROOF + "/r2_threshold_cert.log"
OUTPATH = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1/scripts/results/sc2_out.txt"

out = []


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.append(s)


from decimal import Decimal, getcontext
getcontext().prec = 40


def dec(x, n=25):
    return format(Decimal(x.numerator) / Decimal(x.denominator), ".%de" % (n - 1))


p("#" * 78)
p("# kcross-tail 路线 2 抽验 2：A5 阶梯 6456 项与 92C、eps_ub 的独立重算")
p("#   r2_threshold_cert.log md5 %s" % hashlib.md5(open(R2LOG, "rb").read()).hexdigest())
p("#" * 78)
p("")

dlo, dhi = R.delta_bounds()
l2 = R.ln2_bounds()
Clo, Chi = R.C_bounds()
p("[1] 本路区间（kc_tail_rig，与 r2_rig 不同网格 10^230 与不同级数）")
p("    delta ∈ [%s, %s]；区间宽 = %.3e" % (dec(dlo, 30), dec(dhi, 30), float(dhi - dlo)))
p("    C     ∈ [%s, %s]" % (dec(Clo, 25), dec(Chi, 25)))
p("    日志 :8 的 50 位 delta = 1.58496250072115618145373894394781650875981440769248（截断一致）")
p("")

# eps_ub = eps(1, 92C) 的上界：A(1) = 8900/(54 X0)；v = C；分母 3*92C*ln2
X0 = 695 * 2 ** 60
A1 = F(97 * (92 - 1) + 73, 54 * X0)
twoC = R.exp_bounds(R.rd(Clo * l2[0]), R.ru(Chi * l2[1]))     # 2^C 的区间（C 只用区间）
tC = (R.rd(twoC[0] - 1), R.ru(twoC[1] - 1))
term = R.idiv((F(3), F(3)), tC)
num = (R.rd(A1 + term[0]), R.ru(A1 + term[1]))
denlo = F(3) * R.rd(92 * Clo) * l2[0]
eps_ub = R.ru(F(num[1].numerator, num[1].denominator) / denlo)
p("[2] eps_ub = eps(1, 92C) 的上界（本路算）")
p("    A(1) = 8900/(54X0) = %s" % dec(A1, 15))
p("    2^C 区间 = [%s, %s]（对照 (162/97)X0 = %s）" % (dec(twoC[0], 22), dec(twoC[1], 22), F(162, 97) * X0))
p("    eps_ub ∈ %s" % dec(eps_ub, 15))
p("    日志 :77 记 eps_ub = 1.548697222499e-23；本路与之相差 = %s" % dec(eps_ub - F("1.548697222499e-23"), 6))
p("")

p("[3] 阶梯：q = 1 至 6456（6456 项）")
cnt = 0
worst = None
worst_q = None
amb = []
for q in range(1, 6457):
    qlo = F(q) * dlo
    qhi = F(q) * dhi
    plo = qlo.numerator // qlo.denominator          # floor(q*delta_lo)
    phi = qhi.numerator // qhi.denominator
    if plo != phi:
        amb.append(q)
    pp = plo + 1
    margin = F(pp, q) - dhi - eps_ub
    assert margin > 0, ("阶梯失败", q, pp, float(margin))
    cnt += 1
    if worst is None or margin < worst:
        worst, worst_q = margin, (q, pp)
p("    通过项数 = %d" % cnt)
p("    floor(q·δ_lo) != floor(q·δ_hi) 的 q 个数 = %d（0 表示 p 就是最小候选 p）" % len(amb))
p("    最小余量 = %s，在 q = %d（p = %d）处" % (dec(worst, 8), worst_q[0], worst_q[1]))
p("    对照日志 :76 的『最小余量在 q = 6291（p = 9971），余量 = 1.443273e-7』")
p("    p/q 与 delta 之差 = %s" % dec(F(worst_q[1], worst_q[0]) - dlo, 8))
p("")

p("[4] 域闭合：6457 > 92C")
p("    92C ∈ [%s, %s] ；6457 > 92C ？ %s ；余量 = %s" % (
    dec(92 * Clo, 22), dec(92 * Chi, 22), 6457 > F(92) * Chi, dec(F(6457) - 92 * Chi, 8)))
p("    对照日志 :78 的余量 = 3.658177956302e-1")
open(OUTPATH, "w").write("\n".join(out) + "\n")
p("")
p("[写出] scripts/results/sc2_out.txt")
