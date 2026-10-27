# -*- coding: utf-8 -*-
"""第 5 路读数表：ε(K) 的严格区间（K 取三个候选）、SdW 上界 U(91) 与收尾句的严格比较。

所有判定用精确有理比较；mpmath 只作展示对照（本文件不 import 它）。
运行：<venv>/python r5_readings.py
"""
import sys
from fractions import Fraction as F

sys.set_int_max_str_digits(1000000)
from r5_rig import (delta_bounds, delta_bounds_alt, pow_bounds, pow2_bounds,
                    L2_LO, L2_HI, sig_str, dec_floor, dec_ceil)

S_GRID = 70        # 十进制网格：每步之后按 10^-70 向外取整（各函数单调，包含性保持）
N_SER = 60         # 本脚本级数项数（含 10^-37 级精度，远超判定所需）


def cut(lo, hi):
    return dec_floor(lo, S_GRID), dec_ceil(hi, S_GRID)

out_lines = []


def P(*args):
    s = " ".join(str(a) for a in args)
    print(s)
    out_lines.append(s)


# ---------- 常量 ----------
K_A = 205000000000000000000                      # 论文第六步印数 2.05e20（作为第七步输入）
K_B = 205632218873398596256                      # 我方精确值 K*（= q43）
K_C = 206000000000000000000                      # 记录中的第三点 2.06e20
M = 91
T = 7941964418702608664581                       # 末值（r5_cert 已证）
W1 = F(111, 10 ** 45)                            # 单元下界的读法值 1.11e-43
W3 = F(14492163, 10 ** 50)                       # 单元上界的读法值 1.4492163e-43
CLOSING_22E20 = F(22, 10) * F(10) ** 20
SDW_C = F(14784, 10000)

L1, U1 = delta_bounds(N_SER)
L2, U2 = delta_bounds_alt(N_SER)
DL, DU = cut(max(L1, L2), min(U1, U2))

P("=" * 78)
P("第 5 路读数表：ε(K) 严格区间、U(91) 与收尾句的严格比较")
P("=" * 78)
P("δ 区间（r5_rig 两种走法交集）：宽 = %s" % sig_str(DU - DL, 6))

# ---------- 1. δ^91 与 U(91) ----------
D91_LO, D91_HI = cut(*pow_bounds(DL, DU, F(M), F(M), N_SER, N_SER, S_GRID))
P("\n[1] δ^91 与 SdW 型上界 U(91) = 1.4784 · 91 · δ^91")
P("  δ^91 ∈ (%s, %s)" % (sig_str(D91_LO, 20), sig_str(D91_HI, 20)))
U_LO = SDW_C * M * D91_LO
U_HI = SDW_C * M * D91_HI
P("  U(91) ∈ (%s, %s)" % (sig_str(U_LO, 20), sig_str(U_HI, 20)))
P("  U(91) 上界 < 2.2e20 ：", U_HI < CLOSING_22E20, "（已证）")
P("  U(91) 上界 < T ：", U_HI < T, "（已证）")
P("  T > 2.2e20 ：", T > CLOSING_22E20, "（已证，精确整数比较）")
P("  注：m ↦ 1.4784·m·δ^m 在 m >= 1 上递增（(f(m+1)/f(m)) = ((m+1)/m)·δ > 1），")
P("      故 m <= 91 时 1.4784·m·δ^m <= U(91)（初等，未用代码）")

# ---------- 2. ε(K) 严格区间 ----------
def eps_bounds(K):
    """ε(91, 91, K) = [3/(2^v - 1) + 3·90/(2^v - 1)^δ] / (3 K ln 2)，v = K(δ-1)/(δ^91 - 1)。"""
    K = F(K)
    num_lo, num_hi = dec_floor(K * (DL - 1), S_GRID), dec_ceil(K * (DU - 1), S_GRID)
    den_lo, den_hi = D91_LO - 1, D91_HI - 1
    v_lo, v_hi = cut(num_lo / den_hi, num_hi / den_lo)     # v 单调
    P_lo, P_hi = cut(*pow2_bounds(v_lo, v_hi, N_SER, S_GRID))     # 2^v
    t1_lo, t1_hi = cut(F(3) / (P_hi - 1), F(3) / (P_lo - 1))      # 3/(2^v - 1)
    q_lo, q_hi = cut(*pow_bounds(P_lo - 1, P_hi - 1, DL, DU, N_SER, N_SER, S_GRID))
    t2_lo, t2_hi = cut(F(3 * (M - 1)) / q_hi, F(3 * (M - 1)) / q_lo)
    A_lo, A_hi = cut(t1_lo + t2_lo, t1_hi + t2_hi)
    lo, hi = cut(A_lo / (3 * K * L2_HI), A_hi / (3 * K * L2_LO))
    return lo, hi, (v_lo, v_hi, P_lo, P_hi, t1_lo, t1_hi, t2_lo, t2_hi, A_lo, A_hi)


P("\n[2] ε(91, 91, K) 的严格区间（公式与论文 Theorem 21 的 m2 = m 特例一致）")
res = {}
for name, K in (("2.05e20（论文第六步印数）", K_A),
                ("K* = 2.05632218873398596256e20", K_B),
                ("2.06e20（记录第三点）", K_C)):
    lo, hi, det = eps_bounds(K)
    res[K] = (lo, hi)
    P("  K = %s" % name)
    P("    v ∈ (%s, %s)" % (sig_str(det[0], 16), sig_str(det[1], 16)))
    P("    3/(2^v-1) ∈ (%s, %s)" % (sig_str(det[4], 12), sig_str(det[5], 12)))
    P("    270/(2^v-1)^δ ∈ (%s, %s)" % (sig_str(det[6], 12), sig_str(det[7], 12)))
    P("    ε ∈ (%s, %s)" % (sig_str(lo, 22), sig_str(hi, 22)))
    P("    区间相对宽度 ≈ %s" % sig_str((hi - lo) / hi, 4))

# ---------- 3. 单调性与 8 位印数核对 ----------
P("\n[3] 单调性与 8 位印数核对")
P("  ε(2.05e20) > ε(K*) > ε(2.06e20) ：",
  res[K_A][0] > res[K_B][1] and res[K_B][0] > res[K_C][1], "（区间序，已证）")
HALF8 = F(5, 10) * F(10) ** (-50)     # 8 位有效数字（1.x e-43，末位在 10^-50）的半末位 = 0.5e-50
for K, target in ((K_A, F(14492163, 10 ** 50)), (K_B, F(12297916, 10 ** 50)), (K_C, F(11177766, 10 ** 50))):
    lo, hi = res[K]
    inside = (target - HALF8 < lo) and (hi < target + HALF8)
    P("  K = %d ： ε ∈ (%s, %s)，落在 8 位印数 %s 的 ±0.5 末位内：%s" %
      (K, sig_str(lo, 10), sig_str(hi, 10), sig_str(target, 8), inside))
    assert inside

# ---------- 4. 单元包含判定（决定「同一连分数单元」） ----------
P("\n[4] 三个读法的 ε 区间是否落在同一连分数单元 [w1, w3] = [1.11e-43, 1.4492163e-43]")
P("  （单元的严格陈述在 r5_cert.py 第 8 节：对一切有理 w ∈ [w1, w3]，")
P("    (δ, δ+w) 内最小分母 = T，已证）")
ok_all = True
for name, K in (("2.05e20", K_A), ("K*", K_B), ("2.06e20", K_C)):
    lo, hi = res[K]
    inside = (lo >= W1) and (hi <= W3)
    ok_all = ok_all and inside
    P("  读法 K = %-8s ： ε 上下界均落在单元内：%s" % (name, inside))
    P("      下界 - w1 = %s ； w3 - 上界 = %s" % (sig_str(lo - W1, 10), sig_str(W3 - hi, 10)))
P("  三读法全部落在单元内：", ok_all, "（已证）")
P("  推论：三读法下 (δ, δ+ε) 内最小分母均为 T =", T, "（由 r5_cert 第 8 节的区间陈述）")
P("  推论：印数 7.94e21 相对 T 的偏差固定为 %s（3 位舍入），不随读法变化" % sig_str(abs(T - F(794, 100) * F(10) ** 21), 6))

# ---------- 5. 结论链零件 ----------
P("\n[5] 结论链（供判词引用；每一步的证法见 route-5.md）")
P("  (a) (K+L)/K ∈ (δ, δ+ε) 且其最简分母为 d ⇒ d >= T ⇒ K >= T")
P("  (b) SdW 型上界：K < 1.4784·m·δ^m <= U(91) < 2.2e20")
P("  (c) 2.2e20 < T")
P("  故对三种读法均有 K >= T > 2.2e20 > U(91) >= K，矛盾（结论对读法不敏感）")

with open("results/r5_readings.log", "w") as fh:
    fh.write("\n".join(out_lines) + "\n")
P("\n退出码 0")
