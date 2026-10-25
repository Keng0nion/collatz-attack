#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-2 第 5 步：把本路的独立实现与项目既有脚本的打印值对撞（交叉锚点）。

锚点取自 materials.md 与 rederivation-erratum.md 的既有打印值，全部用真 δ（mpmath）：
  (b1) [2c-bis] 的「log2 顶点值」四行（m2 = 47、67、82、91，W 取该表的链上真实值）
  (b2) [2c] 表后说明的三个「平坦配置低多少 log2 单位」：143.5、1114.8、59959.4
  (b3) 勘误末式的两个不等式：S(V) <= S(v, δv, …, δv) 与 (2^{δv}−1) > (2^v−1)^δ
  (b4) S 在 m2 个循环旋转上相同（区间互相重叠）
  (b5) sympy 复核 f(t) = 3/(2^t − 1) 的二阶导在 t > 0 上为正（凸性）
这些是「独立实现之间的一致性」，不是数学命题的证明。
"""
import sys
from fractions import Fraction

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
import mpmath
import sympy
from r2_common import v_vertex, vertex, S_bounds, LEVEL_ULTRA, LEVEL_FINE

mpmath.mp.dps = 60
delta = mpmath.log(3) / mpmath.log(2)
X0 = 695 * mpmath.mpf(2) ** 60
c = mpmath.log((mpmath.mpf(162) / 97) * X0) / mpmath.log(2)


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def to_mpf(t):
    if isinstance(t, mpmath.mpf):
        return t
    return mpmath.mpf(t.numerator) / mpmath.mpf(t.denominator)


def S_true(y):
    """真 δ 下的 S（mpmath 高精度；只作锚点，不参与判决）。"""
    tot = mpmath.mpf(0)
    for t in y:
        e = to_mpf(t)
        if e > 10 ** 5:
            continue          # 该项已低于 2^{-1e5}，对 30 位摘要无影响
        tot += 3 / (mpmath.mpf(2) ** e - 1)
    return tot


say("=" * 78)
say("route-2 第 5 步：与项目既有打印值的交叉锚点")
say(f"真 δ = {mpmath.nstr(delta, 20)}   c = {mpmath.nstr(c, 20)}")
say("=" * 78)

say("\n[b1] [2c-bis] 的 log2 顶点值四行（本路用 mpmath 真 δ 独立重算）")
bis = [
    (47, mpmath.mpf(47) / 91 * mpmath.mpf("7e11"),        "-82.4364407609"),
    (67, mpmath.mpf(67) / 91 * mpmath.mpf("5267319278509397"), "-88.4639865378"),
    (82, mpmath.mpf(82) / 91 * mpmath.mpf("4640282259296926456"), "-95.4409152027"),
    (91, mpmath.mpf(91) / 91 * mpmath.mpf("205632218873398596256"), "-74.0096698938"),
]
for m2, W, pin in bis:
    v = W * (delta - 1) / (delta ** m2 - 1)
    y = [v * delta ** j for j in range(m2)]
    lb = mpmath.log(S_true(y)) / mpmath.log(2)
    say(f"    m2={m2:>3}  W = {mpmath.nstr(W, 14):>18}  log2 S(V) = {mpmath.nstr(lb, 15):>18}"
        f"   既有打印 {pin}")

say("\n[b2] [2c] 表后说明的三个「平坦配置低多少 log2 单位」（v = c；本路独立重算）")
for m2, pin in [(5, 143.5), (10, 1114.8), (20, 59959.4)]:
    W = c * (delta ** m2 - 1) / (delta - 1)
    v = W * (delta - 1) / (delta ** m2 - 1)
    yv = [v * delta ** j for j in range(m2)]
    yu = [W / m2] * m2
    lbv = mpmath.log(S_true(yv)) / mpmath.log(2)
    lbu = mpmath.log(S_true(yu)) / mpmath.log(2)
    say(f"    m2={m2:>3}  log2 顶点 = {mpmath.nstr(lbv, 15):>18}  log2 平坦 = {mpmath.nstr(lbu, 15):>18}"
        f"  差 = {mpmath.nstr(lbv - lbu, 10):>14}   既有打印 {pin}")

say("\n[b3] 勘误末式两步（真 δ，mpmath）")
say("    解析：对 a = 2^v − 1 >= 1 与 δ > 1 有 (a+1)^δ − a^δ = ∫_a^{a+1} δ t^{δ−1} dt >= δ > 1，")
say("    故 (2^{δv} − 1) > (2^v − 1)^δ；数值核对如下（v 取 c 与几个链上真实值）：")
for v in [c, mpmath.mpf(84.0214032616477371876), mpmath.mpf(75.5946354312875996)]:
    a = mpmath.mpf(2) ** v - 1
    lhs = mpmath.mpf(2) ** (delta * v) - 1
    rhs = a ** delta
    say(f"      v = {mpmath.nstr(v, 18):>22}  2^{{δv}}−1 = {mpmath.nstr(lhs, 12):>16}  "
        f"(2^v−1)^δ = {mpmath.nstr(rhs, 12):>16}  比值−1 = {mpmath.nstr(lhs/rhs - 1, 6)}")

say("\n[b4] S 在 m2 个循环旋转上相同（精确区间互相重叠；δ 取 δ_lo，W = 70）")
from r2_common import delta_rigorous_bounds
d_lo, _ = delta_rigorous_bounds(10 ** 7)
for m2 in (3, 5):
    W = Fraction(70)
    ivs = [S_bounds(list(vertex(m2, d_lo, W, r)), *LEVEL_ULTRA) for r in range(m2)]
    lo_all = min(a for a, b in ivs)
    hi_all = max(b for a, b in ivs)
    say(f"    m2={m2}: 各旋转的 S 区间端点并集的相对跨度 = "
        f"{float((hi_all - lo_all) / lo_all):.3e}（{m2} 个区间全互相重叠 = "
        f"{all(not (ivs[i][1] < ivs[j][0] or ivs[j][1] < ivs[i][0]) for i in range(m2) for j in range(m2))}）")

say("\n[b5] sympy 复核凸性：f(t) = 3/(2^t − 1) 的二阶导")
t = sympy.Symbol("t", positive=True)
f = 3 / (2 ** t - 1)
d2 = sympy.simplify(sympy.diff(f, t, 2))
say(f"    f''(t) = {d2}")
num, den = sympy.fraction(sympy.together(d2))
say(f"    分母 = {den}；对 t > 0：2^t > 1 故分母 > 0；分子 = {num} > 0 → f'' > 0 → 凸。")

say("\n（以上是与既有打印值的一致性核对，不含新的数学判定。）")
