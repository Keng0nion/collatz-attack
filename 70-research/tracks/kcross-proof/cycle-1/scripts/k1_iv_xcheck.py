# -*- coding: utf-8 -*-
"""kcross-proof 第 1 轮路线 1：用 mpmath 区间算术（iv 后端，MPFI 风格）独立复核
ε(92, K) − (γ − δ) 的符号与 ε_opt(K*) 的数值。

与 k1_threshold_cert.py 的区别（独立性声明）：
  1. 数值后端不同：证书用 Fraction（自足有理区间库），本脚本用 mpmath.iv；
  2. 端点来源不同：K 的取值从 k1_threshold_cert.log 的 R_LO_FRAC / R_HI_FRAC 读入，
     不由本脚本重算；
  3. 本脚本不是证书（mpmath.iv 的实现正确性未在本轮核验），只作跨后端一致性检查。

预置：先跑 k1_threshold_cert.py 生成 results/k1_threshold_cert.log。
"""
import re, sys
from fractions import Fraction as F
from mpmath import iv, mp

iv.dps = 160      # 细端点处 ε−(γ−δ) 的残余约 1e-93，dps=90 时被 iv 自身误差淹没（首跑实测）

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
LOG = HERE + "/results/k1_threshold_cert.log"

# ---------- 从日志读回端点（精确有理） ----------
txt = open(LOG).read()
def grab(name):
    m = re.search(r"%s = (-?\d+)/(\d+)" % name, txt)
    assert m, name
    return F(int(m.group(1)), int(m.group(2)))

R_LO = grab("R_LO_FRAC")
R_HI = grab("R_HI_FRAC")
U_LO = grab("U92_LO_FRAC")
DLO = grab("DLO_FRAC")
DHI = grab("DHI_FRAC")
KSTAR = 205632218873398596256
GAM_N, GAM_D = 325919355854421968365, 205632218873398596256
print("从日志读入：R_LO = %s..." % str(R_LO)[:30])
print("             R_HI = %s..." % str(R_HI)[:30])
print("             U_LO = %s ；delta 区间宽 %.2e" % (str(U_LO)[:30], float(DHI - DLO)))

# ---------- 构造区间量 ----------
def iv_of(x):
    """精确有理数 -> iv 值（两端分开构造，避免任何浮点中转）。"""
    x = F(x)
    return iv.mpf(x.numerator) / iv.mpf(x.denominator)

DELTA = iv.log(3) / iv.log(2)
GAM = iv_of(GAM_N) / iv_of(GAM_D)
X0 = iv_of(695 * 2 ** 60)
LN2 = iv.log(2)
print("delta(iv) = [%s, %s]" % (iv.nstr(DELTA.a, 30), iv.nstr(DELTA.b, 30)))
print("delta(iv) 宽度 = %.2e" % float(DELTA.b - DELTA.a))


def eps_iv(m2, m, K, A):
    """ε(m2, m, K) 的 iv 区间（(D3) 公式：与证书同式，独立实现）。"""
    K = iv_of(K)
    v = iv_of(F(m2, m)) * K * (DELTA - 1) / (DELTA ** m2 - 1)
    two_v = iv.exp(v * LN2)
    t = two_v - 1
    term1 = iv.mpf(3) / t
    term2 = iv.mpf(3 * (m2 - 1)) / iv.exp(DELTA * iv.log(t))
    return (A + term1 + term2) / (iv.mpf(3) * K * LN2)


def report(tag, m2, m, K, A):
    e = eps_iv(m2, m, K, A)
    d = GAM - DELTA
    diff = e - d
    lo, hi = float(diff.a), float(diff.b)
    sgn = "above" if lo > 0 else ("below" if hi < 0 else "未定")
    print("  %-28s eps ∈ [%s, %s]" % (tag, iv.nstr(e.a, 25), iv.nstr(e.b, 25)))
    print("  %-28s eps−(γ−δ) 符号 = %s（区间 [%.3e, %.3e]）" % ("", sgn, lo, hi))
    return sgn


print("")
print("[A] X₀ 口径自检：iv 下的 X0 = %s" % iv.nstr(X0, 25))
print("[B] K* 处 eps(91,92,K*)（A = 3/X0，m2 = 91）与 eps(92,92,K*)（A = 0，m2 = 92 不可行，仅对照）")
report("eps(91,92,K*) iv", 91, 92, KSTAR, iv.mpf(3) / X0)
print("  证书值（k1_threshold_cert.log 第 2 节）= 8.9732217086171360163257247e-42")
report("eps(92,92,K*) iv", 92, 92, KSTAR, iv.mpf(0))

print("")
print("[C] 本轮根区间两端点的符号（这是关键独立性检查）")
sA = report("eps(92,92,R_LO) iv", 92, 92, R_LO, iv.mpf(0))
sB = report("eps(92,92,R_HI) iv", 92, 92, R_HI, iv.mpf(0))

print("")
print("[D] 粗端点（312e18 与 315e18）的符号与证书对照")
report("eps(92,92,312e18) iv", 92, 92, F(312) * 10 ** 18, iv.mpf(0))
report("eps(92,92,315e18) iv", 92, 92, F(315) * 10 ** 18, iv.mpf(0))

print("")
print("[E] U(92) 的 iv 值（对照：证书 U 的下界 = %s...）" % str(U_LO)[:30])
u = iv_of(F(14784, 10000)) * iv_of(92) * DELTA ** 92
print("    U(92)(iv) = [%s, %s]" % (iv.nstr(u.a, 25), iv.nstr(u.b, 25)))

print("")
print("[F] 结论对照（本脚本只作跨后端检查，不是证书）")
print("    两端符号 iv 后端：R_LO 处 %s ；R_HI 处 %s" % (sA, sB))
print("    与证书（Fraction 后端）一致 ？ %s" % (sA == "above" and sB == "below"))
