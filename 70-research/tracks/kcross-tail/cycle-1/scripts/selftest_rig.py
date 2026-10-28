#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kc_tail_rig 的自检：与日志里的已知读数对照（不写仓库文件）。"""
import sys, time
from fractions import Fraction as F

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1/scripts"
sys.path.insert(0, HERE)
import kc_tail_rig as R
from mpmath import mp, mpf, log, exp

t0 = time.time()
mp.dps = 80

l2 = R.ln2_bounds()
l3 = R.ln3_bounds()
print("ln2 ∈ [%s, %s]" % (mp.nstr(mpf(l2[0].numerator) / mpf(l2[0].denominator), 45),
                           mp.nstr(mpf(l2[1].numerator) / mpf(l2[1].denominator), 45)))
print("ln2 区间宽 = %s" % mp.nstr(mpf((l2[1] - l2[0]).numerator) / mpf((l2[1] - l2[0]).denominator), 6))
d = R.delta_bounds()
dlo, dhi = d
print("delta ∈ [%s," % mp.nstr(mpf(dlo.numerator) / mpf(dlo.denominator), 55))
print("         %s]" % mp.nstr(mpf(dhi.numerator) / mpf(dhi.denominator), 55))
print("delta 区间宽 = %s" % mp.nstr((mpf(dhi.numerator) / mpf(dhi.denominator))
                                    - (mpf(dlo.numerator) / mpf(dlo.denominator)), 6))
# 对照 r2_threshold_cert.log:8 的 50 位 delta 打印
ref = "1.58496250072115618145373894394781650875981440769248"
print("delta 打印（50 位）与日志 :8 一致？", mp.nstr(mpf(dlo.numerator) / mpf(dlo.denominator), 50) == ref)

C = R.C_bounds()
print("C ∈ [%s, %s]" % (mp.nstr(mpf(C[0].numerator) / mpf(C[0].denominator), 30),
                         mp.nstr(mpf(C[1].numerator) / mpf(C[1].denominator), 30)))
print("日志 :12 记 C = 70.1808063283083668248487894995198792327435")

# 对照 r2_threshold_cert.log:50 至 :51 的 eps(92, 3.3e20) = 3.97640966729894126598e-44
K33 = F(33, 10) * 10 ** 19
e = R.eps_bounds(92, 92, K33, dlo, dhi, l2)
def dec(x, n):
    return mp.nstr(mpf(x.numerator) / mpf(x.denominator), n)
print("eps(92, 3.3e20) ∈ [%s, %s]" % (dec(e[0], 25), dec(e[1], 25)))
print("对照 c2r5_cert.log:24 的 3.976409667298941266e-44（本库应为同值或更窄）")

# 对照 r2 日志 [8.2]：v(92, T_hi) 下端 = 7.264342136866e+1
T_hi_num = 1542566275329005279840718039419280435916173943310179998952443721548967387604624457272573600391707651885171022391000442764034271240234375
T_hi_den = 4925250774549309901534880012517951725634967408808180833493536675530715221437151326426783281860614455100828498788352
T_hi = F(T_hi_num, T_hi_den)
v = R.v_bounds(92, 92, T_hi, dlo, dhi)
print("v(92, T_hi) ∈ [%s, %s]" % (dec(v[0], 20), dec(v[1], 20)))
print("T_hi = %s" % dec(T_hi, 62))
print("用时 %.1f 秒" % (time.time() - t0))
