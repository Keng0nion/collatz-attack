#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速裁决 c_90：decimal 50 位 vs 判定器网格版 vs MPFR 版。"""
import importlib.util
from decimal import Decimal, getcontext

getcontext().prec = 60
spec = importlib.util.spec_from_file_location(
    "m", "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/d3-window-tail/cycle-1/scripts/d3r3_mech.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

dlo, dhi, Clo, Chi = m.build_consts(70)
dstr = m.sci(dlo, 50)
d = Decimal(dstr.replace("e+0", ""))
s = Decimal(0)
p = Decimal(1)
for i in range(90):
    s += p
    p *= d
c3 = Decimal(92) / Decimal(90) * s
print("delta 用值 =", dstr)
print("decimal 版 c_90 =", c3)

g2 = m.geom_interval_grid(90, dlo, dhi, 28)
c2 = m.F(92, 90) * g2[0], m.F(92, 90) * g2[1]
print("判定器网格版 c_90 ∈ [%s, %s]" % (m.sci(c2[0], 30), m.sci(c2[1], 30)))
c2n = Decimal(c2[0].numerator) / Decimal(c2[0].denominator)
print("网格版下端相对差（相对 decimal）= %s" % float((c2n - c3) / c3))

mp = Decimal("1754391557309500447.7158252352034381610805234981675601360621946804765299166224")
print("MPFR 版相对差 = %s" % float((mp - c3) / c3))
# 也裁决 c_89
g1 = m.geom_interval_grid(89, dlo, dhi, 28)
cb = m.F(92, 89) * g1[0]
s2 = Decimal(0)
p = Decimal(1)
for i in range(89):
    s2 += p
    p *= d
c3b = Decimal(92) / Decimal(89) * s2
print("c_89 decimal = %s ；网格版下端相对差 = %s"
      % (c3b, float((Decimal(cb.numerator) / Decimal(cb.denominator) - c3b) / c3b)))
