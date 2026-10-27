#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-2 主证书脚本：把 Psi(K*) = K* 做成精确有理证书。

不含任何浮点判定：所有判别式都是 Fraction 的精确比较。
只 import 标准库与同目录的 route2_rig（后者也只用标准库）。

结构
  A  delta 的严格有理区间 + 严格连分数部分商（区间连分数法）
  B  delta 的收敛数 p_j / q_j（精确整数递归），验证 q_43 = K*
  C  eps_opt(K*) 的严格上下界（含 m2 可行性 与 argmin 的有限核对）
  D  四条判别不等式（精确有理）
  E  结论

用法：
  /Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python route2_cert.py
输出同时写 results/route2_certificate.out 并打印。
"""

import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import route2_rig as RR

OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def sci(fr, sig=22):
    """把有理数写成科学记号（前 sig 位有效数字），只用于显示。"""
    fr = F(fr)
    if fr == 0:
        return "0"
    neg = fr < 0
    fr = -fr if neg else fr
    e = 0
    ten = F(10)
    while fr >= 10:
        fr /= ten
        e += 1
    while fr < 1:
        fr *= ten
        e -= 1
    return "%s%s...e%+d" % ("-" if neg else "", RR.dec_str(fr, sig), e)


N_SERIES = 400          # atanh 级数项数
DIGS_POW = 40           # 幂运算前把 delta 舍入到的小数位数
CAP = 200               # 2^v 的指数上限（超过则用 3/2^CAP 作上界）
KSTAR = 205632218873398596256
M = 92
X0 = 695 * 2 ** 60

p("=" * 78)
p("route-2 严格证书：Psi(K*) = K*，K* = %d，m = %d" % (KSTAR, M))
p("=" * 78)
p("")

# ---------------------------------------------------------------- A
p("[A] delta = log2(3) 的严格有理区间与严格连分数")
dlo, dhi = RR.delta_iv(N_SERIES)
p("    atanh 级数 N = %d；区间宽度（浮点示意） = %.4e" % (N_SERIES, float(dhi - dlo)))
p("    dlo（前 50 位） = " + RR.dec_str(dlo, 50))
p("    dhi（前 50 位） = " + RR.dec_str(dhi, 50))
p("    区间宽度的分母位数 = %d bit" % (dhi - dlo).denominator.bit_length())
p("    锚点自检 126797/80000 < dlo ？ %s" % (F(126797, 80000) < dlo))
p("    锚点自检 dhi < 1584963/1000000 ？ %s" % (dhi < F(1584963, 1000000)))

DIG, STATUS = RR.cf_digits_iv(dlo, dhi, 130)
p("    区间连分数：状态 = %s，严格确定项数 = %d" % (STATUS, len(DIG)))
p("    前 46 项 = %s" % (DIG[:46],))
if len(DIG) < 48:
    p("    !! 严格确定项数不足 48，本证书不可用")
    raise SystemExit(1)
p("")

# ---------------------------------------------------------------- B
p("[B] delta 的收敛数（精确整数递归）与 K* 的收敛身份")

A = DIG[:50]


def conv(a, n):
    """返回 (P, Q)，P[j]/Q[j] = [a_0; ... ; a_j]"""
    P = [a[0], a[0] * a[1] + 1]
    Q = [1, a[1]]
    for j in range(2, n + 1):
        P.append(a[j] * P[j - 1] + P[j - 2])
        Q.append(a[j] * Q[j - 1] + Q[j - 2])
    return P, Q


P, Q = conv(A, 48)
for j in range(38, 49):
    p("    q_%-2d = %d" % (j, Q[j]))
p("")
p("    q_41 = %d" % Q[41])
p("    q_42 = %d" % Q[42])
p("    q_43 = %d%s" % (Q[43], "   <== 等于 K*" if Q[43] == KSTAR else "   <== 不等于 K*，证书不可用"))
p("    q_44 = %d" % Q[44])
p("    q_45 = %d" % Q[45])
if Q[43] != KSTAR:
    p("    !! q_43 不等于 K*，本证书不可用")
    raise SystemExit(1)

GAM_NUM, GAM_DEN = P[43], Q[43]
p("    gamma = p_43/q_43 = %d / %d" % (GAM_NUM, GAM_DEN))
p("    行列式自检 p_43*q_42 - p_42*q_43 = %d（应为 +1 或 -1）" %
  (P[43] * Q[42] - P[42] * Q[43]))
p("    合法性：q_43 = 2*q_41 + q_40 ？ %s（因 a_42 = a_43 = 1）" %
  (Q[43] == 2 * Q[41] + Q[40]))
p("    半收敛刻划：gamma = [A_0; ... ; A_41, 2] ⟺ p_43 = 2*p_41 + p_40 且 q_43 = 2*q_41 + q_40 ：%s" %
  ((P[43] == 2 * P[41] + P[40]) and (Q[43] == 2 * Q[41] + Q[40])))
p("")
p("    关键量：1/(q_42+q_43) 的十进制（前 30 位） = " +
  RR.dec_str(F(1, Q[42] + Q[43]), 30))
p("    关键量：1/q_44       的十进制（前 30 位） = " +
  RR.dec_str(F(1, Q[44]), 30))
p("")

# ---------------------------------------------------------------- C
p("[C] eps 的严格上下界（m = %d，K = K*）" % M)
ln2lo, ln2hi = RR.ln2_iv(N_SERIES)
p("    ln2 区间宽度 = 2^-%d" % (ln2hi - ln2lo).denominator.bit_length())

plo = RR.dec_round(dlo, DIGS_POW, up=False)
phi = RR.dec_round(dhi, DIGS_POW, up=True)
p("    delta 的幂用边界（%d 位十进制，两端向外舍入）：[%s, %s]" %
  (DIGS_POW, float(plo), float(phi)))
p("    自检 plo <= dlo ？ %s ； dhi <= phi ？ %s" % (plo <= dlo, dhi <= phi))

log2lo, log2hi = RR.log2_162X0_iv(ln2lo, ln2hi, N_SERIES)
p("    log2((162/97)*X0) 的区间（前 30 位）：lo = %s" % RR.dec_str(log2lo, 30))
p("                                          hi = %s" % RR.dec_str(log2hi, 30))


def geom_iv(m2):
    """(delta^m2 - 1)/(delta - 1) 的严格区间（delta 递增）"""
    num_lo, num_hi = RR.poly_iv(plo, phi, m2)
    return (num_lo - 1) / (dhi - 1), (num_hi - 1) / (dlo - 1)


def A_exact(m2):
    if m2 == M:
        return F(0)
    if m2 == M - 1:
        return F(3, X0)
    return F(97 * (M - m2) + 73, 54 * X0)


def feasible(m2):
    """返回 (是否可行_下界判定, 是否不可行_上界判定)；True/None 表示未定"""
    g_lo, g_hi = geom_iv(m2)
    lhs_lo = g_lo * log2lo
    lhs_hi = g_hi * log2hi
    rhs = F(m2, M) * KSTAR
    ok = lhs_hi <= rhs
    no = lhs_lo > rhs
    return (ok, no, lhs_lo, lhs_hi, rhs)


p("")
p("    --- m2 的可行性与 argmin 的有限核对（全部精确有理）---")
p("    m2 = 92 与 91 的可行性：")
for m2 in (92, 91, 90):
    ok, no, lo, hi, rhs = feasible(m2)
    p("      m2 = %-3d  LHS 区间 = [%s, %s]" % (m2, sci(lo), sci(hi)))
    p("               RHS = (m2/m)K* = %s" % sci(rhs))
    p("               可行？ %s（下界判定 <= RHS：%s ；上界判定 > RHS：%s）" %
      ("是" if ok else ("否" if no else "未定"), ok, no))

FEAS91 = feasible(91)
INFEAS92 = feasible(92)
if not (FEAS91[0] and INFEAS92[1]):
    p("    !! 91 可行与 92 不可行的严格判定未通过，证书不可用")
    raise SystemExit(1)
p("      结论（精确）：91 可行、92 不可行 → 可行集 = {1, ..., 91}（单调性由下面逐点核对一并覆盖）")
p("")

# 逐点核对：1..91 全可行（用 m2 的 LHS 区间递增性与 RHS 递增性）
p("    逐点核对 m2 = 1..91 的可行性（91 点，全部精确）：")
bad = []
for m2 in range(1, 92):
    ok, no, lo, hi, rhs = feasible(m2)
    if not ok:
        bad.append(m2)
p("      不可行的 m2 个数 = %d（应为 0）" % len(bad))
if bad:
    p("      !! 有不可行点：%s" % bad)
    raise SystemExit(1)

# m2 = 91 的 eps 上下界
K = F(KSTAR)
T1_lo = F(0)                                   # 3/(2^v-1) > 0 恒成立
g_lo, g_hi = geom_iv(91)
v_lo = F(91, M) * K / g_hi
v_hi = F(91, M) * K / g_lo
fv = v_lo.numerator // v_lo.denominator        # floor(v_lo)
p("")
p("    m2 = 91：v 的区间（前 25 位） = [%s, %s]" % (RR.dec_str(v_lo, 25), RR.dec_str(v_hi, 25)))
p("    floor(v_lo) = %d" % fv)
e1 = fv if fv <= CAP else CAP
T1_hi = F(3, 2 ** e1 - 1)
p("    T1 = 3/(2^v - 1) 的严格上界 = 3/(2^%d - 1) = %s" % (e1, sci(T1_hi)))
# T2 = 3*90/(2^v - 1)^delta <= 3*90/2^E，E 取 (floor(v_lo)-1)*dlo 的整数下界
e2 = 0
tmp = fv - 1
if tmp >= 2:
    ex = F(tmp) * dlo          # 指数的严格下界
    e2 = ex.numerator // ex.denominator
    e2 = min(e2, CAP)
T2_hi = F(3 * 90, 2 ** e2) if e2 > 0 else F(3 * 90)
p("    T2 = 3*90/(2^v - 1)^delta 的严格上界 = 3*90/2^%d = %s" % (e2, sci(T2_hi)))

A91 = A_exact(91)
p("    A(91) = 3/X0 = %s（精确有理数）" % sci(A91))
eps_lo = A91 / (3 * K * ln2hi)
eps_hi = (A91 + T1_hi + T2_hi) / (3 * K * ln2lo)
p("    eps(91) 的严格区间：")
p("      eps_lo = %s" % sci(eps_lo))
p("      eps_hi = %s" % sci(eps_hi))
p("      （对照：非严格 mpmath 值 8.973221708617136016325725e-42）")
p("")

# argmin 核对：eps(91)_hi < A(m2)/(3K ln2_hi) 对一切 m2 = 1..90
p("    argmin 核对：对一切 m2 = 1..90，核 eps(91)_hi < A(m2)/(3K ln2_hi)：")
worst = None
nbad = 0
for m2 in range(1, 91):
    low = A_exact(m2) / (3 * K * ln2hi)
    if not (eps_hi < low):
        nbad += 1
        p("      !! m2 = %d 未通过：eps(91)_hi = %s vs A(m2)/(3Kln2_hi) = %s" %
          (m2, RR.dec_str(eps_hi, 20), RR.dec_str(low, 20)))
    if worst is None or low < worst[1]:
        worst = (m2, low)
p("      未通过个数 = %d（应为 0）" % nbad)
if worst:
    p("      最紧的一格：m2 = %d，下界 = %s，比值 eps(91)_hi/下界 = %.6f（需 < 1）" %
      (worst[0], sci(worst[1]), float(eps_hi / worst[1])))
if nbad:
    p("    !! argmin 核对未通过，证书不可用")
    raise SystemExit(1)
p("      结论（精确）：argmin = 91（min_eps 约定），且最大可行 m2 = 91（max_feasible 约定）")

# 特殊：m2 = 92 的 A = 0 会不会更小？它不可行，不进可行集
p("      附注：m2 = 92 的 A = 0（eps 会更小），但它不可行（上面已精确判定），不入可行集")
p("")

# ---------------------------------------------------------------- D
p("[D] 四条判别不等式（全部精确有理比较）")
p("")
p("  D1  gamma > delta ：判据 p_43 > q_43 * dhi")
lhs1 = GAM_NUM
rhs1 = GAM_DEN * dhi
p("      p_43        = %d" % lhs1)
p("      q_43 * dhi  = %s" % RR.dec_str(rhs1, 30))
p("      成立？ %s   余量 = %s" % (lhs1 > rhs1, sci(F(lhs1) - rhs1)))
D1 = lhs1 > rhs1
p("")
p("  D2  gamma - delta < eps_lo ：判据 p_43 - q_43*dlo < q_43*eps_lo")
lhs2 = F(GAM_NUM) - GAM_DEN * dlo
rhs2 = GAM_DEN * eps_lo
p("      p_43 - q_43*dlo = %s" % sci(lhs2))
p("      q_43 * eps_lo   = %s" % sci(rhs2))
p("      成立？ %s   倍数 = %.6f（需 > 1）" % (lhs2 < rhs2, float(rhs2 / lhs2)))
D2 = lhs2 < rhs2
p("")
p("  D3  对一切 j <= 42：|q_j*delta - p_j| > 1/(q_42+q_43)")
bound = F(1, Q[42] + Q[43])
p("      1/(q_42+q_43) = %s" % RR.dec_str(bound, 30))
D3 = True
ratio_min = None
for j in range(0, 43):
    lo = Q[j] * dlo - P[j]
    hi = Q[j] * dhi - P[j]
    if lo <= hi:
        a, b = lo, hi
    else:
        a, b = hi, lo
    okj = (a > bound) or (b < -bound)
    absmin = min(abs(a), abs(b))
    r = float(absmin / bound) if bound != 0 else float("inf")
    if ratio_min is None or r < ratio_min[0]:
        ratio_min = (r, j)
    if not okj:
        D3 = False
        p("      !! j = %d 未通过：区间 [%s, %s]" % (j, RR.dec_str(a, 25), RR.dec_str(b, 25)))
p("      全部 43 个 j 通过？ %s" % D3)
p("      最紧的一格：j = %d，|q_j*delta - p_j| / (1/(q_42+q_43)) = %.6f（需 > 1）" %
  (ratio_min[1], ratio_min[0]))
p("      最紧一格的区间宽度 q_42*(dhi-dlo) = %s（远小于余量）" %
  sci(F(Q[42]) * (dhi - dlo)))
p("")
p("  D4  q_43 * eps_hi < 1/(q_42+q_43)")
lhs4 = GAM_DEN * eps_hi
p("      q_43 * eps_hi  = %s" % sci(lhs4))
p("      1/(q_42+q_43)  = %s" % sci(bound))
p("      成立？ %s   倍数 = %.6f（需 < 1）" % (lhs4 < bound, float(lhs4 / bound)))
D4 = lhs4 < bound
p("")
p("  D5  q_43 * eps_lo > 1/q_44（gamma 落入区间的更弱形式，作交叉核对）")
lhs5 = GAM_DEN * eps_lo
rhs5 = F(1, Q[44])
p("      q_43 * eps_lo = %s" % sci(lhs5))
p("      1/q_44        = %s" % sci(rhs5))
p("      成立？ %s   倍数 = %.6f（需 > 1）" % (lhs5 > rhs5, float(lhs5 / rhs5)))
D5 = lhs5 > rhs5
p("")

# ---------------------------------------------------------------- E
p("[E] 结论")
allok = D1 and D2 and D3 and D4 and D5
p("  D1 %s ； D2 %s ； D3 %s ； D4 %s ； D5 %s" % (D1, D2, D3, D4, D5))
if allok:
    p("")
    p("  *** 证书成立（依赖：收敛数为第二类最佳逼近这一经典引理；见 route-2.md 引理 2）***")
    p("  1) gamma = p_43/q_43 落在开区间 (delta, delta + eps_opt(K*)) 内（D1 与 D2）；")
    p("  2) 分母小于 q_43 的分数都不在该区间内（D3 与 D4 的合取）；")
    p("  3) 故该区间内分母最小的分数之分母 = q_43 = K* = %d；" % KSTAR)
    p("  4) 两种约定（min_eps 与 max_feasible）在 K* 处都给 eps_opt = eps(91)，")
    p("     故两种约定下 Psi(K*) = K* 同时成立。")
    p("  注意：本证书不依赖 Lemma 22 的『收敛或半收敛清单』，只依赖引理 2；")
    p("        清单穷举（route2_enum.py）是独立交叉核对。")
else:
    p("  *** 证书不成立：见上面未通过项 ***")

p("")
p("附：K* 处的 eps 三项分解（严格区间口径）")
p("      A 项  下界 = %s  ；上界 = %s" % (sci(A91 / (3 * K * ln2hi)), sci(A91 / (3 * K * ln2lo))))
p("      T1 项 下界 = 0 ；上界 = %s" % sci(T1_hi / (3 * K * ln2lo)))
p("      T2 项 下界 = 0 ；上界 = %s" % sci(T2_hi / (3 * K * ln2lo)))
p("      A 项占 eps_lo 的比例 = %.6f" % float((A91 / (3 * K * ln2hi)) / eps_lo))

outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(outdir, exist_ok=True)
with open(os.path.join(outdir, "route2_certificate.out"), "w") as f:
    f.write("\n".join(OUT) + "\n")
print("\n[written] results/route2_certificate.out")
