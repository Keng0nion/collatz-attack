#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 第 3 轮：精确有理数对照。

用 atanh 级数给出 ln2、ln3 的严格有理上下界（尾项显式控制），由此得
delta = ln3/ln2 的严格有理区间 [dlo, dhi]，全部用 Fraction 精确算术。
然后把三个关键比较做成有理数比较（无浮点）：

  C1 余量(91) > 1   : 1.4784*91*dhi^91 < 7941964418702608664581
  C2 余量(92) < 1   : 77692117359936589403 < 1.4784*92*dlo^92
  C3 越界见证 > U   : 1.4784*92*dhi^92 < 7941964418702608664581
  C4 见证落在区间内 : 7.5311e11 < 3.3e20 且 3.3e20 < 1.4784*92*dlo^92
  C5 m2 = 92 的可行门槛 c92 < 见证起点与 K_cross 附近值
  C6 L < U(92) 且 L < K*（整数比较）

级数与尾界：
  ln2 = 2*sum_{k>=0} 1/((2k+1)3^(2k+1))，余项 < (9/2)*(1/3)^(2N+3)/(2N+3)
  ln3 = 2*sum_{k>=0} 1/((2k+1)2^(2k+1))，余项 < (8/3)*(1/2)^(2N+3)/(2N+3)
  ln(112590/97) = ln(t) + 10*ln2, t = 112590/99328, x = (t-1)/(t+1) = 13262/211918
  ln(t) = 2*sum_{k>=0} x^(2k+1)/(2k+1)，余项 < 2*x^(2N+3)/((2N+3)(1-x^2))
"""
from fractions import Fraction as F

N = 400

def ln2_bounds():
    s = F(0)
    for k in range(N + 1):
        s += F(1, (2 * k + 1) * 3 ** (2 * k + 1))
    lo = 2 * s
    tail = F(2 * 9, 2) * F(1, 3 ** (2 * N + 3)) / (2 * N + 3)
    tail = F(9, 2) * F(1, 3 ** (2 * N + 3)) / (2 * N + 3)
    return lo, lo + 2 * tail

def ln3_bounds():
    s = F(0)
    for k in range(N + 1):
        s += F(1, (2 * k + 1) * 2 ** (2 * k + 1))
    lo = 2 * s
    tail = F(8, 3) * F(1, 2 ** (2 * N + 3)) / (2 * N + 3)
    return lo, lo + 2 * tail

def ln_t_bounds():
    t = F(112590, 99328)
    x = (t - 1) / (t + 1)
    s = F(0)
    for k in range(N + 1):
        s += x ** (2 * k + 1) / (2 * k + 1)
    lo = 2 * s
    tail = 2 * x ** (2 * N + 3) / ((2 * N + 3) * (1 - x * x))
    return lo, lo + tail, x

L2 = ln2_bounds()
L3 = ln3_bounds()
Lt = ln_t_bounds()
dlo = L3[0] / L2[1]
dhi = L3[1] / L2[0]
print("ln2 in [%s, %s]" % (float(L2[0]), float(L2[1])))
print("ln3 in [%s, %s]" % (float(L3[0]), float(L3[1])))
print("delta 区间宽度 =", float(dhi - dlo))
PINNED = F("1.58496250072115618145373894394781650875981440769248106045575")
print("钉住的 40 位 delta 在区间内？", dlo < PINNED < dhi)
print("delta_lo =", float(dlo), " delta_hi =", float(dhi))

C14784_91 = F(14784, 10000) * 91
C14784_92 = F(14784, 10000) * 92
K91 = 7941964418702608664581
K92 = 77692117359936589403
W = 7941964418702608664581          # 见证处的 Psi 值
Witness = F(33, 10) * 10 ** 20      # 3.3e20
L = F(75311, 100000) * 10 ** 11     # 7.5311e11
Kstar = 205632218873398596256

print()
print("[C1] U(91) < K 下界(91)：", C14784_91 * dhi ** 91 < K91)
print("[C2] K 下界(92) < U(92)：", K92 < C14784_92 * dlo ** 92)
print("[C3] U(92) < 见证 Psi 值 7.94e21：", C14784_92 * dhi ** 92 < W)
print("[C4] L < 3.3e20 < U(92)：", L < Witness, Witness < C14784_92 * dlo ** 92)
print("[C6] L < U(92) 与 L < K*：", L < C14784_92 * dlo ** 92, L < Kstar)

# C5：m2 = m 的可行门槛 c_m = ((d^m-1)/(d-1)) * log2((162/97)X0)
log2_num_lo = 60 + (Lt[0] + 10 * L2[0]) / L2[1]
log2_num_hi = 60 + (Lt[1] + 10 * L2[1]) / L2[0]
print()
print("log2((162/97)X0) 严格区间 = [%s, %s]" % (float(log2_num_lo), float(log2_num_hi)))
for m in (91, 92):
    g_lo = (dlo ** m - 1) / (dhi - 1)
    g_hi = (dhi ** m - 1) / (dlo - 1)
    if m == 91:
        c_lo = g_lo * log2_num_lo
        c_hi = g_hi * log2_num_hi
    else:
        c_lo = g_lo * log2_num_lo
        c_hi = g_hi * log2_num_hi
    print("c_%d = ((delta^%d-1)/(delta-1))*log2((162/97)X0) 在 [%s, %s]" % (
        m, m, float(c_lo), float(c_hi)))
    if m == 92:
        c92_lo, c92_hi = c_lo, c_hi
print("[C5] c92 < 3.3e20 ？", c92_hi < Witness)
print("[C5b] c92 < L ？（用于说明起点 L 处 m2 = 92 不可行）", c92_lo > L)

# 余量的有理数上下界（把 d^91 夹出区间再取比值）
m91_lo = F(K91) / (C14784_91 * dhi ** 91)
m91_hi = F(K91) / (C14784_91 * dlo ** 91)
m92_lo = F(K92) / (C14784_92 * dhi ** 92)
m92_hi = F(K92) / (C14784_92 * dlo ** 92)
print()
print("余量(91) 严格区间 = [%s, %s]" % (float(m91_lo), float(m91_hi)))
print("余量(92) 严格区间 = [%s, %s]" % (float(m92_lo), float(m92_hi)))
print("见证处 U(92)/Psi 的比值上界 =", float(C14784_92 * dhi ** 92 / W))
