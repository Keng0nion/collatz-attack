#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""裁决 c_90 的第三条独立计算：decimal 模块 60 位 vs 精确有理（无网格）vs 判定器网格版。"""
import importlib.util
from fractions import Fraction as F
from decimal import Decimal, getcontext

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/d3-window-tail/cycle-1/scripts/"
spec = importlib.util.spec_from_file_location("m", HERE + "d3r3_mech.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
getcontext().prec = 60

dlo, dhi, Clo, Chi = m.build_consts(70)
print("delta 区间宽（相对）= %s" % m.sci((dhi - dlo) / dhi, 6))
print("C 区间宽（相对）= %s" % m.sci((Chi - Clo) / Chi, 6))

# (1) 精确有理，无网格（geom_interval 精确幂）
g1 = m.geom_interval(90, dlo, dhi)
c1 = F(92, 90) * g1[0], F(92, 90) * g1[1]
print("(1) 精确幂版 c_90 ∈ [%s, %s] 相对宽 %s" % (m.sci(c1[0], 30), m.sci(c1[1], 30), m.sci((c1[1] - c1[0]) / c1[1], 4)))

# (2) 判定器网格版（G=28）
g2 = m.geom_interval_grid(90, dlo, dhi, 28)
c2 = F(92, 90) * g2[0], F(92, 90) * g2[1]
print("(2) 网格版 c_90 ∈ [%s, %s] 相对宽 %s" % (m.sci(c2[0], 30), m.sci(c2[1], 30), m.sci((c2[1] - c2[0]) / c2[1], 4)))

# (3) decimal 60 位，用 delta 的高精度十进制值
dm = Decimal(str(m.sci(dlo, 55).replace("e+0", "")))
M = 90
s = Decimal(0)
p = Decimal(1)
for i in range(M):
    s += p
    p *= dm
c3 = Decimal(92) / Decimal(M) * s
print("(3) decimal 版 c_90 = %s" % c3)
print("    与 (1) 下端相对差 = %s" % (float((Decimal(c1[0].numerator) / Decimal(c1[0].denominator) - c3) / c3)))
print("    与 (2) 下端相对差 = %s" % (float((Decimal(c2[0].numerator) / Decimal(c2[0].denominator) - c3) / c3)))

# (4) 用 v 反推：v = K/c，看哪个 c 与 C·(1+rho) 的解析预测一致
K = F("123124614107652692133.007231919710646726095849")
print("(4) K/c 三种：")
for name, cc in (("精确幂", c1), ("网格", c2)):
    print("    %s: v = K/c ∈ [%s, %s]" % (name, m.sci(K / cc[1], 25), m.sci(K / cc[0], 25)))
print("    解析预测 v = C(1+rho)，rho = %.36s" % m.sci((K - F(92, 90) * g1[0] * Clo) / (F(92, 90) * g1[0] * Clo), 20))
