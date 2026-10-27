#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 侦察脚本 4：检验 c2r5 的 simplest(delta_lo, gamma) 是否真的最小。

只用精确有理 + 临时用「钉住的 50 位十进制」当 delta 的宽区间（正式脚本里会换成自己的证书）。
运行：20-experiments/.venv/bin/python k3_probe4.py
"""
import sys
from fractions import Fraction as F
from mpmath import mp, mpf, nstr

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts")
import c2r5_rig as R2

mp.dps = 90

PREFIX = [1, 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55, 1, 4, 3, 1, 1, 15, 1, 9, 2, 5, 7,
          1, 1, 4, 8, 1, 11, 1, 20, 2, 1, 10, 1, 4, 1, 1, 1]


def cf_value(quot):
    v = F(0)
    for a in reversed(quot):
        v = F(a) + (F(0) if v == 0 else 1 / v)
    return v


GAM = F(325919355854421968365, 205632218873398596256)
RCLAIM = F(12587715785705330118969, 7941964418702608664581)
B = cf_value(PREFIX + [1, 1, 37])
BLOW = cf_value(PREFIX + [1, 1, 36])
print("B      = %d / %d" % (B.numerator, B.denominator))
print("B_low  = %d / %d" % (BLOW.numerator, BLOW.denominator))
print("R(claim) = %d / %d" % (RCLAIM.numerator, RCLAIM.denominator))
print("gcd(B) =", __import__("math").gcd(B.numerator, B.denominator))
print()
print("q_B + q_gamma == q_Rclaim ?", B.denominator + GAM.denominator == RCLAIM.denominator)
print("p_B + p_gamma == p_Rclaim ?", B.numerator + GAM.numerator == RCLAIM.numerator)
print("unimodular |pB qG - qB pG| =",
      abs(B.numerator * GAM.denominator - B.denominator * GAM.numerator))
print("unimodular |pBL qG - qBL pG| =",
      abs(BLOW.numerator * GAM.denominator - BLOW.denominator * GAM.numerator))
print("q_BL + q_gamma == q_B ?", BLOW.denominator + GAM.denominator == B.denominator)
print("p_BL + p_gamma == p_B ?", BLOW.numerator + GAM.numerator == B.numerator)
print()
print("B < B_low ?", B < BLOW, " ; B < gamma ?", B < GAM, " ; Rclaim < gamma ?", RCLAIM < GAM)
print("B < Rclaim ?", B < RCLAIM)
print("B 的小数（60 位）:", nstr(mpf(B.numerator) / B.denominator, 62))
print("B_low 的小数      :", nstr(mpf(BLOW.numerator) / BLOW.denominator, 62))
print("Rclaim 小数       :", nstr(mpf(RCLAIM.numerator) / RCLAIM.denominator, 62))
print("gamma 小数        :", nstr(mpf(GAM.numerator) / GAM.denominator, 62))
print()
PIN50 = "1.58496250072115618145373894394781650875981440769248106045575"


def dec_to_frac(s):
    ip, fp = s.split(".")
    return F(int(ip + fp), 10 ** len(fp))


DLO_PIN = dec_to_frac(PIN50)
DHI_PIN = DLO_PIN + F(1, 10 ** 50)
print("按钉住 50 位取 delta ∈ [P, P+1e-50]：")
print("  B < DLO_PIN ?", B < DLO_PIN, "   （若 True，B 落在 (delta_lo, gamma) 内）")
print("  B_low < DLO_PIN ?", BLOW < DLO_PIN)
print("  DHI_PIN < gamma ?", DHI_PIN < GAM)
print()
print("c2r5_rig.delta_bounds() 的 dlo/dhi（只读对照）：")
dlo2, dhi2 = R2.delta_bounds()
print("  dlo2 =", R2.dec(dlo2, 50))
print("  dhi2 =", R2.dec(dhi2, 50))
print("  B < dlo2 ?", B < dlo2)
print("  BLOW < dlo2 ?", BLOW < dlo2)
print("  dhi2 < GAM ?", dhi2 < GAM)
print()
print("直接调用 c2r5_rig.simplest_fraction(dlo2, GAM)：")
try:
    got = R2.simplest_fraction(dlo2, GAM)
    print("  返回 = %d / %d" % (got.numerator, got.denominator))
    print("  等于 Rclaim ?", got == RCLAIM, " ；等于 B ?", got == B)
except Exception as e:
    print("  异常：", repr(e))
print()
print("直接调用 c2r5_rig.simplest_fraction(B_low + tiny, GAM)：")
try:
    got2 = R2.simplest_fraction(BLOW + F(1, 10 ** 30), GAM)
    print("  返回 = %d / %d" % (got2.numerator, got2.denominator))
except Exception as e:
    print("  异常：", repr(e))
