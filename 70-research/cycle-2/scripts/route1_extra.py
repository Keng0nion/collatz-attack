#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-1 附加证书（严格有理算术）：
  一、ε(m2 = 92, ·) 关于 K 的严格单调性（含初等证明文本）
  二、g(K) = ε(92, K) − (γ − δ) 的端点符号与严格二分（含唯一性）
  三、与 mpmath 记录值 K_root = 313195478959172262876.636530619490706526023102 的相容性
  四、区间延伸：Ψ(K) = K* 对一切 K ∈ [K*, K2]（K2 = 313195478959172262876），
      条件为「Ψ 关于 K 非降」（引 route-3.md:231 的 L7，项目内已有两条独立初等证明，
      未经第三方复核）——本条单独标为条件性结论。
  五、退出码：任一判据失败即 1。
"""
import sys
import os
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from fractions import Fraction as F
from route1_rig import (ctx, cf_digits_iv, contr, v_bounds, eps_bounds, A_of, sci_str,
                        dec_str, iv_round, M_CYCLES, X0, KSTAR)

T0 = time.time()
FAIL = []


def ck(tag, cond, note=""):
    ok = bool(cond)
    print("   %-56s %s%s" % (tag, "True" if ok else "False", ("   " + note) if note else ""))
    if not ok:
        FAIL.append(tag)
    return ok


C = ctx()
DL, DH = C["DL"], C["DH"]
l2lo, l2hi = C["l2lo"], C["l2hi"]
dlo, dhi = C["dlo"], C["dhi"]

print("=" * 78)
print("route-1 附加证书：K_cross 方程根的严格夹逼 与 [K*, K2] 区间延伸")
print("=" * 78)
print("时间：%s" % time.strftime("%Y-%m-%d %H:%M:%S"))
print()

# δ 的连分数与 γ（与主证书同一套机件）
digs = cf_digits_iv(dlo, dhi, 48)
GAM_NUM, GAM_DEN = contr(digs[:42] + [2])
gamma = F(GAM_NUM, GAM_DEN)
C3_NUM, C3_DEN = contr(digs[:42] + [3])
c3 = F(C3_NUM, C3_DEN)
Q_ = [contr(digs[:j + 1])[1] for j in range(len(digs))]

# ============================================================ 一、单调性
print("[一] 单调性引理（本文件给出初等证明）")
print("   Lemma M：固定 m2 ∈ [1,m]，K ↦ ε(m2, K) 在 K > 0 上严格递减。")
print("   证明：v = c·K，c = (m2/m)(δ−1)/(δ^m2 − 1) > 0，故 2^v − 1 关于 K 严格递增，")
print("         B(K) := A(m2) + 3/(2^v−1) + 3(m2−1)/(2^v−1)^δ 关于 K 严格递减且 > 0；")
print("         ε = B(K)/(3K·ln2)。取 K' > K：B(K') < B(K) 且 3K'ln2 > 3K·ln2 > 0，")
print("         两严格不等式相乘得 ε(K') < ε(K)。 □")
print("   推论：g(K) := ε(92, K) − (γ − δ) 在 K > 0 上严格递减、连续，故至多一个零点；")
print("         若区间两端符号相反，则零点存在且唯一（连续函数的介值定理 + 单调性）。")
print()

# ============================================================ 二、端点符号与二分
print("[二] g(K) = ε(92,K) − (γ − δ) 的端点符号与严格二分")


def g_bounds(K):
    """g(K) 的严格区间 [lo, hi]（用 92 可行域的 eps 区间与 δ 界）。"""
    (elo, ehi), _, _, _ = eps_bounds(M_CYCLES, K, C)
    return elo - (gamma - dlo), ehi - (gamma - dhi)


Ka = 313195478959172262767
Kb = 313195478959172262934
lo_a, hi_a = g_bounds(F(Ka))
lo_b, hi_b = g_bounds(F(Kb))
print("   g(%d) ∈ [%s, %s]" % (Ka, sci_str(lo_a, 25), sci_str(hi_a, 25)))
print("   g(%d) ∈ [%s, %s]" % (Kb, sci_str(lo_b, 25), sci_str(hi_b, 25)))
ck("[J1] g(Ka) > 0", lo_a > 0, "严格下界 = %s" % sci_str(lo_a, 45))
ck("[J2] g(Kb) < 0", hi_b < 0, "严格上界 = %s" % sci_str(hi_b, 45))
# [J3] m2 = 92 在 [Ka, Kb]（以及 K2）上可行：G(92) ≤ Ka 即覆盖全区间（G 与 K 无关）
from route1_rig import geom_bounds, iv_round as _ivr
_g92 = geom_bounds(M_CYCLES, C["DL"], C["DH"])
_G92_hi = _ivr((_g92[1] * C["c_hi"], _g92[1] * C["c_hi"]))[1]   # 只取上界
ck("[J3] m2 = 92 可行：G(92) ≤ Ka（同时覆盖 Kb 与 K2）", _G92_hi <= F(Ka),
   "G(92) 上界 = %s ≤ Ka = %d" % (sci_str(_G92_hi, 25), Ka))

# 严格二分（每步用精确有理中点；判据是 g 的区间不含 0）
a, b = F(Ka), F(Kb)
steps = 0
while steps < 60:
    m = (a + b) / 2
    lo_m, hi_m = g_bounds(m)
    if hi_m < 0:
        b = m
        steps += 1
    elif lo_m > 0:
        a = m
        steps += 1
    else:
        print("   第 %d 步中点判定失败（区间含 0），停在此处" % (steps + 1))
        break
print("   二分步数 = %d，最终区间 [%s, %s]" % (steps, a, b))
print("   区间宽度 = %s（精确有理：%s）" % (sci_str(b - a, 8), b - a if (b - a).denominator < 10 ** 40 else "分母过大"))
lo_a2, hi_a2 = g_bounds(a)
lo_b2, hi_b2 = g_bounds(b)
ck("[J4] 最终左端 g > 0", lo_a2 > 0)
ck("[J5] 最终右端 g < 0", hi_b2 < 0)
rel = (b - a) / a
print("   相对宽度 = %s" % sci_str(rel, 8))
ck("[J6] 相对宽度 < 10^-25", rel < F(1, 10 ** 25))

# ============================================================ 三、与 mpmath 记录值相容
print("[三] 与 mpmath 记录值的相容性（materials.md:216 的 findroot 值）")
MP_ROOT = F("313195478959172262876.636530619490706526023102")
ck("[J7] mpmath 的 K_root 落在本证书的严格区间内", a < MP_ROOT < b,
   "K_root ∈ (%s, %s)" % (dec_str(a, 20), dec_str(b, 20)))
print()

# ============================================================ 四、区间延伸
print("[四] 区间延伸：Ψ(K) = K* 对一切 K ∈ [K*, K2]（K2 = 313195478959172262876）")
K2 = F(313195478959172262876)
print("   K2 = %s < 根（J5：K2 = Ka 与 Kb 之间的整数，g(K2) > 0 见下）" % K2)

# K2 处：92 可行（G(92) 的上界 < K2），故 ε_opt(K2) ≤ ε(92, K2) ≤ E_hi(K2)
# 下界：m2 ∈ [1,91] 全部有 A(m2) ≥ 3/X0 ⟹ ε ≥ A(91)/(3 K2 ln2)；
#       m2 = 92 用完整 ε 下界（v ≈ 6.2，可展开）。取两者最小。
E_lo_91 = A_of(91) / (3 * K2 * l2hi)
(elo92, ehi92), v92, t92, T92 = eps_bounds(M_CYCLES, K2, C)
E_lo_K2 = min(E_lo_91, elo92)
E_hi_K2 = ehi92
print("   v(92, K2) ∈ [%s, %s]；2^v − 1 ∈ [%s, %s]" %
      (sci_str(v92[0], 20), sci_str(v92[1], 20), sci_str(t92[0], 20), sci_str(t92[1], 20)))
print("   ε(92, K2) ∈ [%s, %s]" % (sci_str(elo92, 30), sci_str(ehi92, 30)))
print("   A 项下界（m2 ≤ 91 通用）= A(91)/(3K2·ln2_hi) = %s" % sci_str(E_lo_91, 30))
print("   故 ε_opt(K2) ∈ [%s, %s]" % (sci_str(E_lo_K2, 30), sci_str(E_hi_K2, 30)))
ck("[K1] ε_opt(K2) > γ − δ（左余量为正）", E_lo_K2 - (gamma - dlo) > 0,
   "余量下界 = %s" % sci_str(E_lo_K2 - (gamma - dlo), 45))
ck("[K2] δ + ε_opt(K2) < [P,3]（最小性所需的右端比较）", c3 > dhi + E_hi_K2,
   "[P,3] − (δ+ε_opt) > %s" % sci_str(c3 - dhi - E_hi_K2, 8))
print("   于是：γ ∈ (δ, δ+ε_opt(K2))，且按主证书第七节同一分片论证（两对 Farey 邻接不变，")
print("   行列式 = 1 不依赖 K），(δ, δ+ε_opt(K2)) 内最小分母 = q_43 = K*，即 Ψ(K2) = K*。")
print("   结合主证书的 Ψ(K*) = K* 与「Ψ 关于 K 非降」（route-3.md:231 的 L7，项目内已证、")
print("   未经第三方复核），得：对一切 K ∈ [K*, K2]，Ψ(K) = K*。")
print("   【本条的证据类型：严格区间证书 + 一条引用的非降性引理；引理未经第三方复核】")
print()

# ============================================================ 五、K2 与 K_cross 的关系登记
print("[五] K2 与「K_cross」的关系（登记，不裁决）")
print("   本证书严格证明的是：方程 ε(92,K) = γ − δ 在 (Ka, Kb) 内有唯一实根；")
print("   K2 = 313195478959172262876 是该根下方的最大整数（g(K2) > 0）。")
print("   把该根等同于「K_cross」（链是否越过 U(92) 的阈值）是 materials.md:221 标为「推断、未证」")
print("   的读法，本轮未证，故本节只登记，不作为 K_cross 的定位证据。")
lo_K2, hi_K2 = g_bounds(K2)
ck("[L1] g(K2) > 0（K2 在根左侧）", lo_K2 > 0, "g(K2) 下界 = %s" % sci_str(lo_K2, 30))
print()

print("=" * 78)
if FAIL:
    print("失败判据：%s" % FAIL)
    print("退出码 1")
    sys.exit(1)
print("全部判据通过；退出码 0；用时 %.1f 秒" % (time.time() - T0))
sys.exit(0)
