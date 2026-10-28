#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""路线 3 定向反例搜索：定向探针 1（只读）。

目的：核清 eps 公式各分项的量级与 v 的取值，标定三个搜索的靶区：
  1. delta、C、K*、U(92)、gamma - delta 的实际读数；
  2. eps_bounds(91, 92, K*) 与日志 8.9732217086171360163257247e-42 的对照；
  3. v(91, K*)、v(92, K*) 与三项分解（A、3/(2^v-1)、3(m2-1)/(2^v-1)^delta）；
  4. A(90) 下界剪枝 A(90)/(3K ln2_hi) 与 eps(91, K) 的比值随 K 的变化（找剪枝失效边界）。
"""
import sys

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
sys.path.insert(0, HERE)
from fractions import Fraction as F
import r4_common as C
import kc_rig as KC
import k3_rig as K3

OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


DLO, DHI, L2 = C.consts()
CIV = C.R.C_bounds()
KSTAR = F(C.KSTAR)
X0 = F(C.X0_695)

p("[1] 常量读数")
p("    delta ∈ [%s, %s]" % (C.dec(DLO, 60), C.dec(DHI, 60)))
p("    ln2 ∈ [%s, %s]" % (C.dec(L2[0], 60), C.dec(L2[1], 60)))
p("    delta - 1 ∈ [%s, %s]" % (C.dec(DLO - 1, 30), C.dec(DHI - 1, 30)))
p("    C ∈ [%s, %s]" % (C.dec(CIV[0], 45), C.dec(CIV[1], 45)))
p("    X0 = 695*2^60 = %d" % X0)
p("    gamma - delta ∈ [%s, %s]" % (C.dec(C.GAMMA - DHI, 32), C.dec(C.GAMMA - DLO, 32)))
U92 = (C.R.rd(C.U92_W * C.M * C.R.iv_pow((DLO, DHI), 92)[0]),
       C.R.ru(C.U92_W * C.M * C.R.iv_pow((DLO, DHI), 92)[1]))
p("    U(92) ∈ [%s, %s]" % (C.dec(U92[0], 32), C.dec(U92[1], 32)))
p("    K* = %d" % C.KSTAR)

p("")
p("[2] eps 与 v 的分项（K = K*）")
for m2 in (90, 91, 92):
    e = K3.eps_bounds(m2, 92, KSTAR, DLO, DHI, L2)
    eK = KC.eps_bounds(m2, 92, KSTAR, DLO, DHI, L2)
    v = K3.v_bounds(m2, 92, KSTAR, DLO, DHI)
    A = K3.A_of(m2, 92)
    p("    m2 = %d ：A = %s" % (m2, A))
    p("           v ∈ [%s, %s]" % (C.dec(v[0], 20), C.dec(v[1], 20)))
    p("           eps(k3) ∈ [%s, %s]" % (C.dec(e[0], 44), C.dec(e[1], 44)))
    p("           eps(kc) ∈ [%s, %s]" % (C.dec(eK[0], 44), C.dec(eK[1], 44)))
    p("           A/(3K ln2_hi) = %s （eps_lower_A_only）" % C.dec(K3.eps_lower_A_only(m2, 92, KSTAR, L2), 44))

p("")
p("[3] A(90) 下界剪枝随 K 的比值 r(K) = (A(90)/(3K ln2_hi)) / eps_hi(91,K)")
p("    目标：r(K) > 1 的 K 段上，m2 <= 90 一律劣于 91（argmin = 91 的充分条件之一）")
for Kstr in ("205632218873398596256", "220000000000000000000",
             "240000000000000000000", "260000000000000000000",
             "280000000000000000000", "300000000000000000000",
             "302578139046974169432", "313195478959172262876"):
    K = F(Kstr)
    elo = K3.eps_lower_A_only(90, 92, K, L2)
    ehi = K3.eps_bounds(91, 92, K, DLO, DHI, L2)[1]
    r = elo / ehi
    p("    K = %s ：r = %s" % (Kstr, C.dec(r, 20)))

open(HERE.replace("kcross-proof/cycle-1", "kcross-tail/cycle-1") + "/results/r3_probe1.out", "w").write("\n".join(OUT) + "\n")
print("\n[done]")
