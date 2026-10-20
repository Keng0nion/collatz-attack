#!/usr/bin/env python3
"""对反驳意见的独立复核（只用标准库；精确整数运算）。

复核项：
 A. chi >= tau 是否恒成立（反驳者称这是平凡事实），以及范围内 CST（chi = tau）是否成立
 B. 反驳者给出的「证明步骤反例」：a=3, n=3（tau(3)=4）时 phi(3)=2 是否仍与 n 同类
 C. 反驳者称我第 9 步的界 c_v <= 2^{j-m-1} 3^m 为假（例：v=(1,0,1,1)，c=29 > 27）
 D. 反驳者的 a=5 类比反例：n=5 时 tau_5(5)、x*=c/D 的整性、轨道所入环的周期与 274 的整除关系
"""
from fractions import Fraction

def mk(a):
    def T(x):
        return x // 2 if x % 2 == 0 else (a * x + 1) // 2
    return T

def tau_chi(T, a, n, cap=5000):
    """返回 (tau, chi, m_at_tau, c_at_tau, T^{tau}(n))；chi = min{j: T^j(n)<n} 或 None。"""
    y = n
    m = 0
    c = 0
    chi = None
    for j in range(1, cap + 1):
        if y & 1:
            c = a * c + (1 << (j - 1))
            m += 1
        y = T(y)
        if chi is None and y < n:
            chi = j
        if a ** m < (1 << j):
            return j, chi, m, c, y
    return None, chi, None, None, None

T3 = mk(3)
T5 = mk(5)

print("=" * 72)
print("A. chi >= tau 是否恒成立（n <= 200000，a = 3）")
bad_ge = 0      # chi < tau 的个数（若为 0，则 chi >= tau 在范围内成立）
bad_cst = 0     # chi > tau 的个数（CST 的反例数）
for n in range(2, 200001):
    t, ch, _, _, _ = tau_chi(T3, 3, n, cap=500)
    if t is None:
        bad_cst += 1
        continue
    if ch is None:
        bad_cst += 1
    elif ch < t:
        bad_ge += 1
    elif ch > t:
        bad_cst += 1
print(f"   chi < tau 个数 = {bad_ge}   （0 表示 chi >= tau 在范围内成立）")
print(f"   chi > tau 个数 = {bad_cst}   （0 表示本范围内 CST chi = tau 成立）")
print("   一行证明（chi >= tau）：若 T^j(n) < n，由 T^j(n) = (3^{S_j}n + c_j)/2^j 且 c_j >= 0 得")
print("   3^{S_j} n <= 3^{S_j} n + c_j < 2^j n，故 3^{S_j} < 2^j，即 tau(n) <= j。")

print("=" * 72)
print("B. 反驳者的 a = 3、n = 3 反例（针对我第 6 步 x_l 的「同余归纳」）")
j, ch, m, c, y = tau_chi(T3, 3, 3, cap=500)
D = (1 << j) - 3 ** m
print(f"   tau(3) = {j}, m = {m}, c = {c}, D = {D}, theta = c/D = {Fraction(c, D)}, T^{j}(3) = {y}")
print(f"   x_1 = phi(3) = (3^{m}*3 + c)/2^{j} = {(3**m*3+c) >> j}")
x1 = (3 ** m * 3 + c) >> j
print(f"   x_1 是否仍满足类条件 3^{m} x + c ≡ 0 (mod 2^{j})： {(3**m*x1+c) % (1<<j) == 0}"
      f"（3^{m}x_1+c = {3**m*x1+c}，2^{j} = {1<<j}）")
print(f"   x_2 = phi(x_1) = {Fraction(3**m*x1+c, 1<<j)}  是整数？ {(3**m*x1+c) % (1<<j) == 0}")

print("=" * 72)
print("C. 我第 9 步的界 c_v <= 2^{j-m-1} 3^m 是否成立（全部 j <= 20 的向量）")
viol_old = 0
viol_new = 0
worst = None
for j in range(1, 21):
    for v in range(1 << j):
        c = 0
        m = 0
        for i in range(j):
            if (v >> i) & 1:
                c = 3 * c + (1 << i)
                m += 1
        if c == 0:
            continue
        if c > 2 ** (j - m - 1) * 3 ** m:
            viol_old += 1
            if worst is None:
                worst = (j, v, m, c, 2 ** (j - m - 1) * 3 ** m)
        if c >= (1 << j) * Fraction(3, 2) ** m:
            viol_new += 1
print(f"   旧界违反数 = {viol_old}（反驳者称 2506 个；此处只统计 c > 0 的向量）")
if worst:
    j, v, m, c, bd = worst
    print(f"   首个反例：j = {j}, 位串（低位在前）= {format(v, 'b')}, m = {m}, c = {c}, 旧界 = {bd}")
print(f"   修正界 c_v < 2^j·(3/2)^m 的违反数 = {viol_new}")

print("=" * 72)
print("D. 反驳者的 a = 5 类比反例（n = 5）")
j, ch, m, c, y = tau_chi(T5, 5, 5, cap=5000)
D = (1 << j) - 5 ** m
xs = Fraction(c, D)
print(f"   tau_5(5) = {j}, m = {m}, chi_5(5) = {ch}（None 表示 5000 步内未下降）")
print(f"   D = 2^{j} - 5^{m} = {D}（> 0：{D>0}），T_5^{j}(5) = {y}，5 <= x* = c/D：{5 <= xs}")
print(f"   x* = c/D 是整数？ {xs.denominator == 1}（分子位数 {len(str(xs.numerator))}，分母位数 {len(str(xs.denominator))}）")
# 5 的轨道进入的环
orb = []
z = 5
for _ in range(40):
    orb.append(z)
    z = T5(z)
    if z in orb:
        cyc = orb[orb.index(z):]
        break
print(f"   轨道（到首次重复）：{orb}")
print(f"   所入环：{cyc}，周期 = {len(cyc)}；环上最小元 = {min(cyc)} >= 5：{min(cyc) >= 5}（故 chi_5(5) = ∞）")
print(f"   周期 {len(cyc)} 整除 j = {j} ？ {j % len(cyc) == 0}")
print(f"   说明：a=5 的轨道确实进入环（定理 B 的结论在此类比下成立），但「x* 为整数」与")
print(f"   「周期整除 j0」两条证明内部断言在此类比下为假。")
