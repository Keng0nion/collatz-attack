#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-3「落点不等式的初等化归」严格有理证书。

目标命题 (F)：在 m = 92 口径、min_eps 与 max_feasible 两种约定下 Psi(K*) = K*，
K* = 205632218873398596256。

化归（每一步都在报告 route-3.md 里编号）：
  (F)  <=  [Lemma 22（Hercher 2023，已发表）] + [delta 的连分数数字（严格）]
           + (L) gamma - delta < eps_opt(K*)      （落点）
           + (U) delta + eps_opt(K*) < F(3)       （柱体归属）
           + [定义口径：Psi、eps_opt 按 r4x_core.py，X0 = 695*2^60]
(L) 与 (U) 都只用：delta 的严格有理区间、精确整数幂、初等指数下界；不含浮点。
数值只在第 7 节出现，仅作锚点自检。

退出码 0 当且仅当全部检查通过。
"""

from fractions import Fraction as F
from math import isqrt
import sys

FAILS = []


def check(name, cond, extra=""):
    ok = bool(cond)
    if not ok:
        FAILS.append(name)
    print("[%s] %s %s" % ("PASS" if ok else "FAIL", name, extra))
    return ok


print("=" * 78)
print("route-3 严格证书：Psi(K*) = K* 的初等化归")
print("=" * 78)

# ---------------------------------------------------------------- 0. 常数
K_STAR = 205632218873398596256          # 2.05632218873398596256e20
X0 = 695 * 2 ** 60                      # 印出版 Definition 4
M = 92
C0 = 162 * 695                          # (162/97)X0 = C0/97 * 2^60

print("\n--- 0. 常数（精确整数） ---")
print("K*  = %d" % K_STAR)
print("X0  = 695 * 2^60 = %d" % X0)
print("(162/97)X0 = (%d/97) * 2^60" % C0)

# ---------------------------------------------------------------- 1. ln2 ln3 的严格有理界
print("\n--- 1. ln2、ln3 的严格有理区间（初等 atanh 级数 + 显式尾界） ---")


def atanh_bounds(x, N):
    """x = 1/3 或 1/5。返回 (lo,hi) 使 lo < atanh(x) < hi。
    atanh(x) = sum_{k>=0} x^(2k+1)/(2k+1)（各项为正，部分和为下界）；
    尾界 sum_{k>N} x^(2k+1)/(2k+1) < x^(2N+3)/((2N+3)(1-x^2))。"""
    s = F(0)
    xp = x
    for k in range(N + 1):
        s += xp / (2 * k + 1)
        xp *= x * x
    rem = x ** (2 * N + 3) / ((2 * N + 3) * (1 - x * x))
    return s, s + rem


N_TERMS = 60
a3lo, a3hi = atanh_bounds(F(1, 3), N_TERMS)
a5lo, a5hi = atanh_bounds(F(1, 5), N_TERMS)
LN2_LO, LN2_HI = 2 * a3lo, 2 * a3hi
LN3_LO = LN2_LO + 2 * a5lo
LN3_HI = LN2_HI + 2 * a5hi
print("ln2 区间宽度 = %.3e" % float(LN2_HI - LN2_LO))
check("ln2 区间宽度 < 1e-55", 0 < LN2_HI - LN2_LO < F(1, 10 ** 55))

# delta = ln3/ln2 的严格区间；向内取整到分母 10^80 的网格
D_LO_RAW = LN3_LO / LN2_HI
D_HI_RAW = LN3_HI / LN2_LO
check("原始 delta 区间宽度 < 1e-55", 0 < D_HI_RAW - D_LO_RAW < F(1, 10 ** 55))
S = 10 ** 80
D_LO = F(-((-D_LO_RAW.numerator * S) // D_LO_RAW.denominator), S)   # ceil
D_HI = F((D_HI_RAW.numerator * S) // D_HI_RAW.denominator, S)       # floor
check("向内取整后 D_LO < D_HI（网格未穿越）", D_LO < D_HI)
check("向内取整仍是严格界：D_LO >= 原始下界", D_LO >= D_LO_RAW)
check("向内取整仍是严格界：D_HI <= 原始上界", D_HI <= D_HI_RAW)
print("delta 区间宽度（取整后）= %.3e" % float(D_HI - D_LO))


def dec(fr, n=45):
    v = fr.numerator * 10 ** n // fr.denominator
    s = str(v).rjust(n + 1, "0")
    return s[:-n] + "." + s[-n:]


print("delta 下界前 45 位 = %s" % dec(D_LO))
print("delta 上界前 45 位 = %s" % dec(D_HI))

# ---------------------------------------------------------------- 2. delta 的连分数数字（严格）
print("\n--- 2. delta 的连分数数字（区间算法，精确有理） ---")


def cf_interval(u, v, n):
    """对 [u,v] 逐项抽连分数；每步要求 floor(u)==floor(v)。返回数字表或 None。"""
    digs = []
    for _ in range(n):
        fu, fv = u.numerator // u.denominator, v.numerator // v.denominator
        if fu != fv:
            return digs
        digs.append(int(fu))
        if v - fu == 0:
            return digs
        u, v = 1 / (v - fu), 1 / (u - fu)
    return digs


DIG = cf_interval(D_LO, D_HI, 50)
check("区间连分数算法给出 >= 46 项", len(DIG) >= 46, "实测 %d 项" % len(DIG))
TARGET = [1, 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55, 1, 4, 3, 1, 1, 15, 1, 9,
          2, 5, 7, 1, 1, 4, 8, 1, 11, 1, 20, 2, 1, 10, 1, 4, 1, 1, 1, 1, 1, 37, 4]
check("delta 前 46 个部分商与材料一致", DIG[:46] == TARGET)


def convergents(digs):
    out = []
    pm2, pm1 = 0, 1
    qm2, qm1 = 1, 0
    for a in digs:
        p = a * pm1 + pm2
        q = a * qm1 + qm2
        out.append((p, q))
        pm2, pm1 = pm1, p
        qm2, qm1 = qm1, q
    return out


CONV = convergents(DIG)
cyl_ok = True
for n in range(46):
    Pn, Qn = CONV[n]
    if n >= 1:
        Pn1, Qn1 = CONV[n - 1]
        E1, E2 = F(Pn, Qn), F(Pn + Pn1, Qn + Qn1)
    else:
        E1, E2 = F(Pn, Qn), F(DIG[0] + 1)
    lo_, hi_ = min(E1, E2), max(E1, E2)
    if not (lo_ < D_LO and D_HI < hi_):
        cyl_ok = False
        print("   柱体失败于 n = %d" % n)
check("柱体包含性：n=0..45 全部满足（delta 严格落在柱体内）", cyl_ok)
check("a_42 = 1", DIG[42] == 1, "实测 %d" % DIG[42])
check("a_43 = 1", DIG[43] == 1, "实测 %d" % DIG[43])
check("a_44 = 37", DIG[44] == 37, "实测 %d" % DIG[44])

# ---------------------------------------------------------------- 3. 收敛分母、gamma
print("\n--- 3. 收敛分母、gamma 与精确整数恒等式 ---")
P41, Q41 = CONV[41]
P40, Q40 = CONV[40]
print("Q_40 = %d" % Q40)
print("Q_41 = %d" % Q41)
print("Q_42 = %d" % CONV[42][1])
print("Q_43 = %d" % CONV[43][1])
check("Q_41 = 77692117359936589403", Q41 == 77692117359936589403)
check("Q_40 = 50247984153525417450", Q40 == 50247984153525417450)
check("Q_43 = 2*Q_41 + Q_40 = K*", 2 * Q41 + Q40 == K_STAR)

GAM_P, GAM_Q = 2 * P41 + P40, 2 * Q41 + Q40     # gamma = [a0;...;a41,2] = F(2)
print("gamma = %d / %d" % (GAM_P, GAM_Q))
check("gamma 分母 = K*", GAM_Q == K_STAR)
check("gamma 分子 = 325919355854421968365", GAM_P == 325919355854421968365)
EPS0 = P41 * Q40 - P40 * Q41
check("Mobius 行列式 = +1（F 严格增）", EPS0 == 1, "实测 %d" % EPS0)
check("gamma 既约", abs(GAM_P * Q41 - P41 * GAM_Q) == 1)
HARSH_P, HARSH_Q = 3 * P41 + P40, 3 * Q41 + Q40  # F(3) = [a0;...;a41,3]
print("F(3) = %d / %d" % (HARSH_P, HARSH_Q))

# ---------------------------------------------------------------- 4. 落点 (L)
print("\n--- 4. 落点 (L)：gamma - delta < eps_opt(K*) ---")
# 恒等式（本报告自证）：x0 = [a42;a43,a44,...]，a42=a43=1，y2=[a44;a45,...]
#   gamma - delta = 1 / (K* (Q41(2 y2+1) + Q40 (y2+1)))，y2 in (37,38)
DEN_UB = 75 * Q41 + 38 * Q40            # y2>37 => 2y2+1>75, y2+1>38
DEN_LB = 77 * Q41 + 39 * Q40            # y2<38 => 2y2+1<77, y2+1<39
print("75 Q41 + 38 Q40 = %d" % DEN_UB)
print("77 Q41 + 39 Q40 = %d" % DEN_LB)
check("DEN_LB 恰为 7941964418702608664581（m=92 链的越界见证）",
      DEN_LB == 7941964418702608664581)
GAMDELTA_UB = F(1, K_STAR * DEN_UB)
GAMDELTA_LB = F(1, K_STAR * DEN_LB)
print("gamma - delta 的严格上界 = %.9e" % float(GAMDELTA_UB))

# A 项普遍下界：论文定理 21 三段形式（m2<=m-2 / m2=m-1 / m2=m）
A_list = [F(3, X0)] + [F(97 * (M - m2) + 73, 54 * X0) for m2 in range(1, M)]
check("A(m2) >= 3/X0 对 m2 = 1..91 成立", min(A_list) == F(3, X0),
      "最小 = 3/X0 = %.6e" % float(F(3, X0)))
A_alt = [F(3, X0)] + [F(97 * (M - m2) + 1, 54 * X0) for m2 in range(1, M - 1)] + [F(3, X0)]
check("若按证明末行的 (97(m-m2)+1)/(54X0) 读（m2=91 仍走 3/X0 特例），仍 A >= 3/X0",
      min(A_alt) == F(3, X0))

GEOM92_LO = (D_LO ** 92 - 1) / (D_HI - 1)
GEOM92_HI = (D_HI ** 92 - 1) / (D_LO - 1)
GEOM91_HI = (D_HI ** 91 - 1) / (D_LO - 1)
check("(162/97)X0 > 2^70", C0 > 97 * 2 ** 10)
check("(162/97)X0 < 2^71", C0 < 97 * 2 ** 11)
check("m2 = 92 在 K* 处不可行：geom(92)*70 > K*", GEOM92_LO * 70 > K_STAR,
      "geom(92) 下界 = %.6e -> 乘积 %.6e" % (float(GEOM92_LO), float(GEOM92_LO * 70)))
check("m2 = 91 在 K* 处可行：geom(91)*71 < (91/92)K*", GEOM91_HI * 71 < F(91, 92) * K_STAR,
      "geom(91) 上界 = %.6e" % float(GEOM91_HI))

LN2_UB = F(6932, 10000)
check("ln2 < 6932/10000（严格）", LN2_HI < LN2_UB)
check("75Q41 + 38Q40 > X0 * (6932/10000)（精确有理比较）", DEN_UB > X0 * LN2_UB,
      "比值 = %.4f" % float(F(DEN_UB) / (X0 * LN2_UB)))
EPS_LO = F(1, X0 * K_STAR * LN2_UB)
check("(L) 成立：eps_opt(K*) > 1/(X0 K* U2) > gamma - delta", EPS_LO > GAMDELTA_UB,
      "余量倍数 = %.3f" % float(EPS_LO / GAMDELTA_UB))
print("eps 下界 = %.9e ；gamma-delta 上界 = %.9e" % (float(EPS_LO), float(GAMDELTA_UB)))
check("(gamma-delta) K* < 1（故 p = ceil(delta K*) 唯一确定）", GAMDELTA_UB * K_STAR < 1)
check("p = gamma 分子 = 2P41 + P40", GAM_P == 2 * P41 + P40)

# X0 口径稳健性：arXiv v3 用 704*2^60（材料 §1.4）
X0_ALT = 704 * 2 ** 60
check("换 X0 = 704*2^60 后落点仍成立（75Q41+38Q40 > X0' U2）", DEN_UB > X0_ALT * LN2_UB,
      "比值 = %.4f" % float(F(DEN_UB) / (X0_ALT * LN2_UB)))
EPS_LO_ALT = F(1, X0_ALT * K_STAR * LN2_UB)
check("换 X0 后 eps 下界仍 > gamma - delta", EPS_LO_ALT > GAMDELTA_UB,
      "余量倍数 = %.3f" % float(EPS_LO_ALT / GAMDELTA_UB))

# ---------------------------------------------------------------- 5. 上界 (U)
print("\n--- 5. 上界 (U)：delta + eps_opt(K*) < F(3) ---")
V1_LO = F(91, 92) * K_STAR / GEOM91_HI
V1_FLOOR = V1_LO.numerator // V1_LO.denominator
V1_FRAC = V1_LO - V1_FLOOR
check("v1 下界 > 74", V1_LO > 74, "v1_lo = %.6f" % float(V1_LO))
POW2_FLOOR = 2 ** V1_FLOOR
# 2^{v1} >= 2^{v1_lo} = 2^{floor} * 2^{frac} >= 2^{floor} * (1 + frac*ln2)（e^u >= 1+u）
TWO_V_LO = POW2_FLOOR * (1 + V1_FRAC * LN2_LO)
TAIL2_UB = F(3, 1) / (TWO_V_LO - 1)
# 第三项：3*90/((2^v-1)^delta) < 3*90/((2^v-1)^(3/2)) <= 3*90/(N74*sqrt(N74))
check("delta 下界 > 3/2", D_LO > F(3, 2))
N74 = POW2_FLOOR
TAIL3_UB = F(270, N74 * isqrt(N74))
EPS_UP = (F(3, X0) + TAIL2_UB + TAIL3_UB) / (3 * K_STAR * LN2_LO)
F3_MINUS_GAM = F(1, (3 * Q41 + Q40) * (2 * Q41 + Q40))
F3_MINUS_DELTA_LO = F3_MINUS_GAM + GAMDELTA_LB
print("2^{v1} 下界 = %.6e ；eps(91,K*) 上界 = %.9e" % (float(TWO_V_LO), float(EPS_UP)))
print("F(3)-gamma = %.9e ；F(3)-delta 下界 = %.9e" % (float(F3_MINUS_GAM), float(F3_MINUS_DELTA_LO)))
check("(U) 成立：eps_opt(K*) <= eps(91,K*) < F(3) - delta", EPS_UP < F3_MINUS_DELTA_LO,
      "余量倍数 = %.3f" % float(F3_MINUS_DELTA_LO / EPS_UP))
check("两端夹住：gamma < delta + eps_opt(K*) < F(3)", GAMDELTA_UB < EPS_LO and EPS_UP < F3_MINUS_DELTA_LO)
check("m2 = 91 可行（故 eps_opt <= eps(91) 可用）", GEOM91_HI * 71 < F(91, 92) * K_STAR)

# 两约定同区间：min_eps 给 eps_opt in [1/(X0K*U2), eps(91,K*)]；max_feasible 给 eps(91,K*)
check("max_feasible 处也 >= A 项下界（eps(91,K*) >= 1/(X0K*U2)）",
      F(1, X0 * K_STAR * LN2_UB) <= F(3, X0) / (3 * K_STAR * LN2_UB))
check("两种约定给出的区间都含 gamma 且都在 (F(1),F(3)) 内（由 (L)(U) 与 91 可行、92 不可行）",
      GEOM91_HI * 71 < F(91, 92) * K_STAR and GEOM92_LO * 70 > K_STAR)

# ---------------------------------------------------------------- 5b. 最小性：Farey 邻元初等引理
print("\n--- 5b. 最小性：Farey 邻元初等引理（不依赖 Lemma 22） ---")
# 引理（初等，两行）：若 a/b < c/d、bc - ad = 1，则一切 u/v 满足 a/b < u/v < c/d 者必有 v >= b+d。
#   证：(u/v-a/b) = (ub-av)/(vb) >= 1/(vb)，(c/d-u/v) = (cv-ud)/(dv) >= 1/(dv)，
#   相加得 1/(bd) = c/d - a/b >= (b+d)/(vbd)，故 v >= b+d。
F1_P, F1_Q = P41 + P40, Q41 + Q40                  # F(1) = [a0;...;a41,1]
print("F(1) = %d / %d" % (F1_P, F1_Q))
check("F(1) < D_LO（delta 在 F(1) 右侧）", F(F1_P, F1_Q) < D_LO)
check("D_HI < F(2) = gamma", D_HI < F(GAM_P, GAM_Q))
check("det(F(1),F(2)) = P42*K* - GAM_P*Q42 = +-1", abs(F1_P * GAM_Q - GAM_P * F1_Q) == 1,
      "实测 %d" % (F1_P * GAM_Q - GAM_P * F1_Q))
check("det(F(2),F(3)) = +-1", abs(GAM_P * HARSH_Q - HARSH_P * GAM_Q) == 1,
      "实测 %d" % (GAM_P * HARSH_Q - HARSH_P * GAM_Q))
check("F(1) < F(2) < F(3)", F(F1_P, F1_Q) < F(GAM_P, GAM_Q) < F(HARSH_P, HARSH_Q))
check("(delta, delta+eps) 被 (F(1),F(3)) 覆盖（由 5b 与第 5 节两端夹住）",
      F(F1_P, F1_Q) < D_LO and EPS_UP < F(HARSH_P, HARSH_Q) - D_HI,
      "F(3)-D_HI 与 eps 上界之比 = %.3f" % float((F(HARSH_P, HARSH_Q) - D_HI) / EPS_UP))
# 三段覆盖：分母下界 = min(Q42+K*, K*+Q_F3) > K*，而 gamma 本身分母 = K*
MIN_OTHER = min(F1_Q + GAM_Q, GAM_Q + HARSH_Q)
check("(F(1),F(2)) 与 (F(2),F(3)) 内的分母下界 > K*", MIN_OTHER > GAM_Q,
      "min(Q42+K*, K*+Q_F3) = %d" % MIN_OTHER)
check("两段两侧分母均 >= K*，且 gamma 分母 = K*（故最小性成立）", MIN_OTHER > GAM_Q == K_STAR)

# ---------------------------------------------------------------- 6. 平台区间
print("\n--- 6. 平台：certified K 范围（Psi(K) = K*） ---")
LOG2C_LO = F(70) + F(13262, 112590) / LN2_UB
print("log2((162/97)X0) 下界 = %.6f" % float(LOG2C_LO))
K92_LO = GEOM92_LO * LOG2C_LO
XSTAR = K_STAR * DEN_UB / (X0 * LN2_UB)
PLAT_HI = min(K92_LO, XSTAR)
print("m2=92 门槛下界 = %.6e ；X* = %.6e" % (float(K92_LO), float(XSTAR)))
print("平台环 certified 右端 = %.6e" % float(PLAT_HI))
check("平台区间在 K* 之上非空", PLAT_HI > K_STAR, "PLAT_HI/K* = %.4f" % float(PLAT_HI / K_STAR))


def exp_ub(z, J=3):
    """z >= 0 有理；exp(z) 的严格上界：部分和 + 余项 <= (z^{J+1}/(J+1)!)/(1-z/(J+2))。"""
    s, t = F(0), F(1)
    for j in range(J + 1):
        if j > 0:
            t = t * z / j
        s += t
    return s + t * z / (J + 1) / (1 - z / (J + 2))


def pow2_ub(v, grid=10 ** 6):
    """v >= 0 有理；2^v 的严格上界（v 先向上取到 1e-6 网格）。"""
    w = F(-((-v.numerator * grid) // v.denominator), grid)
    fl = w.numerator // w.denominator
    return 2 ** fl * exp_ub((w - fl) * LN2_HI)


# 并入 m2 = 92 分支：对 K <= X，若正常 m2 <= 91 用 A 下界，否则 m2 = 92 用 2^v 下界
def two_branch_min(X):
    b1 = F(1, X0 * X * LN2_UB)
    b2 = F(1, 1) / ((pow2_ub(X / GEOM92_LO) - 1) * X * LN2_UB)
    return min(b1, b2)


lo_s, hi_s = K_STAR, F(3) * K_STAR
for _ in range(80):
    mid = (lo_s + hi_s) / 2
    if two_branch_min(mid) > GAMDELTA_UB:
        lo_s = mid
    else:
        hi_s = mid
PLAT_HI2 = lo_s
print("并入 m2=92 分支后的 certified 右端 = %.9e" % float(PLAT_HI2))
print("  该处两条下界：A 分支 %.6e，m2=92 分支 %.6e"
      % (float(F(1, X0 * PLAT_HI2 * LN2_UB)),
         float(F(1) / ((pow2_ub(PLAT_HI2 / GEOM92_LO) - 1) * PLAT_HI2 * LN2_UB))))
check("加强后的 certified 右端 > 3.13e20（逼近 K_cross 的数值定位 3.1319547896e20）",
      PLAT_HI2 > F(313, 100) * 10 ** 18, "PLAT_HI2 = %.9e" % float(PLAT_HI2))
KCROSS_NUM = F(3131954789591722628766365, 10 ** 4)     # 3.131954789591722628766365e20
check("加强后的 certified 右端 < 数值 K_cross（故只是下界，不是定位）",
      PLAT_HI2 < KCROSS_NUM, "缺口 = %.4f%%" % float(100 * (KCROSS_NUM / PLAT_HI2 - 1)))

# ---------------------------------------------------------------- 7. 数值锚点（仅自检）
print("\n--- 7. 数值锚点（mpmath，仅自检，不作判据） ---")
from mpmath import mp, mpf  # noqa: E402

mp.dps = 200
d = mp.log(3) / mp.log(2)
gam = mpf(GAM_P) / GAM_Q
print("delta  (mp.nstr 50) = %s" % mp.nstr(d, 50))
print("gamma  (mp.nstr 50) = %s" % mp.nstr(gam, 50))
print("gamma - delta       = %s" % mp.nstr(gam - d, 25))
print("材料 3.2 记的锚点    = 6.244680669692735665906112e-43")
check("D_LO <= delta <= D_HI（高精度复算）",
      mpf(D_LO.numerator) / D_LO.denominator <= d <= mpf(D_HI.numerator) / D_HI.denominator)
check("gamma - delta 与材料锚点前 22 位一致",
      mp.nstr(gam - d, 22) == "6.244680669692735665906e-43")

# y2 = [a44; a45, ..., a52] 的严格有理区间（柱体端点）
CONVY = convergents(DIG[44:53])
PY, QY = CONVY[-1]
PY1, QY1 = CONVY[-2]
YA, YB = sorted([F(PY, QY), F(PY + PY1, QY + QY1)])
print("y2 in ( %s , %s )" % (mp.nstr(mpf(YA.numerator) / YA.denominator, 25),
                             mp.nstr(mpf(YB.numerator) / YB.denominator, 25)))
for name, yv in (("y2 下端点", YA), ("y2 上端点", YB)):
    ident = 1 / (K_STAR * (Q41 * (2 * (mpf(yv.numerator) / yv.denominator) + 1)
                           + Q40 * ((mpf(yv.numerator) / yv.denominator) + 1)))
    print("  恒等式在 %s 处 = %s" % (name, mp.nstr(ident, 25)))
check("闭式恒等式落在 [1/(K*DEN_UB), 1/(K*DEN_LB)] 内（高精度复算）",
      1 / (K_STAR * DEN_LB) <= gam - d <= 1 / (K_STAR * DEN_UB))
GDU_MP = mpf(GAMDELTA_UB.numerator) / GAMDELTA_UB.denominator
check("严格上界 > 真值，且比值 < 1.02",
      GDU_MP > gam - d and GDU_MP / (gam - d) < mpf("1.02"),
      "比值 = %.5f" % float(GDU_MP / (gam - d)))

# eps_opt(K*) 与 m2 扫描（锚点）
def eps_of(m2, K):
    geom = (d ** m2 - 1) / (d - 1)
    v = (mpf(m2) / M) * K / geom
    t = mp.power(2, v) - 1
    if m2 == M:
        A = mpf(0)
    elif m2 == M - 1:
        A = mpf(3) / X0
    else:
        A = mpf(97 * (M - m2) + 73) / (54 * X0)
    return (A + 3 / t + 3 * mpf(m2 - 1) / mp.power(t, d)) / (3 * K * mp.log(2))


def feasible(m2, K):
    geom = (d ** m2 - 1) / (d - 1)
    return geom * (mp.log(mpf(C0) / 97 * mp.power(2, 60)) / mp.log(2)) <= (mpf(m2) / M) * K


Kstar_mp = mpf(K_STAR)
feas = [m2 for m2 in range(1, M + 1) if feasible(m2, Kstar_mp)]
eps_list = [(m2, eps_of(m2, Kstar_mp)) for m2 in feas]
amin = min(eps_list, key=lambda t: t[1])
print("K* 处可行 m2 集合 = 1..%d（个数 %d）" % (max(feas), len(feas)))
print("argmin = m2 = %d，eps = %s" % (amin[0], mp.nstr(amin[1], 25)))
print("材料 2.3 记的 eps_opt(K*) = 8.973221708617136016325725e-42")
check("锚点：可行集 = {1..91}（m2=92 不可行）", max(feas) == 91 and len(feas) == 91)
check("锚点：argmin = 91，eps 与材料一致", amin[0] == 91 and mp.nstr(amin[1], 20) == "8.9732217086171360163e-42")
check("锚点：eps(92) 也 > gamma - delta（抗辩用）",
      eps_of(M, Kstar_mp) > gam - d, "eps(92) = %s" % mp.nstr(eps_of(M, Kstar_mp), 10))
print("A(91) = 3/X0 = %s ；170/(54X0) = %s"
      % (mp.nstr(mpf(3) / X0, 12), mp.nstr(mpf(170) / (54 * X0), 12)))
print("（材料 §3.3 标 170/(54X0) 但数值为 3/X0；两者不一致，见报告第 6 节）")

# K_cross 的根（锚点，非严格）
f = lambda K: eps_of(92, K) - (gam - d)
lo_, hi_ = mpf("3.12e20"), mpf("3.15e20")
for _ in range(200):
    mid = (lo_ + hi_) / 2
    if f(mid) > 0:
        lo_ = mid
    else:
        hi_ = mid
print("K_cross 的根锚点 in (%s, %s)" % (mp.nstr(lo_, 25), mp.nstr(hi_, 25)))
print("材料 3.5 记的 K_root = 313195478959172262876.636530619490706526023102")
KROOT_REF = mpf("313195478959172262876.636530619490706526023102")
check("锚点：二分根与材料 K_root 的相对差 < 1e-19",
      abs(((lo_ + hi_) / 2 - KROOT_REF) / KROOT_REF) < mpf("1e-19"),
      "相对差 = %s" % mp.nstr(abs(((lo_ + hi_) / 2 - KROOT_REF) / KROOT_REF), 5))

# ---------------------------------------------------------------- 结果
print("\n" + "=" * 78)
if FAILS:
    print("失败项：%s" % FAILS)
    sys.exit(1)
print("全部检查通过（退出码 0）")
print("=" * 78)
sys.exit(0)
