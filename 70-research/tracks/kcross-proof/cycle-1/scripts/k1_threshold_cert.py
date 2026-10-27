# -*- coding: utf-8 -*-
"""kcross-proof 第 1 轮路线 1：阈值 T 的两侧严格证书与端点事实复算。

只读地 import cycle-2 的区间库 c2r5_rig（不运行 c2r5_cert.py，不写任何旧目录）。
本脚本自己写一个独立的 Stern-Brocot 中项行走（与 R.simplest_fraction 的跳段版
互相独立），并用精确有理比较复算四条端点事实。

输出：
  1. 常数与端点事实（δ、C、92C、K*、γ、U(92)、simplest(δ_lo, γ)）
  2. 连续性前提：m₂ = 1..92 的门槛上界全部 ≤ 312e18
  3. 主导权：ε_opt = ε(92, ·) 在 [312e18, 315e18] 上
  4. 二分定位 ε_opt(K) = γ − δ 的根 R（N 步，精确有理中点）
  5. 终值复核与区间打印
"""
import sys, time, math
from fractions import Fraction as F

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts")
import c2r5_rig as R

M = 92
NSTEPS = 160
KA0, KB0 = F(312) * 10 ** 18, F(315) * 10 ** 18
GAM_N, GAM_D = 325919355854421968365, 205632218873398596256   # gamma, K*
GAM = F(GAM_N, GAM_D)

OUT = []
T0 = time.time()


def p(s=""):
    OUT.append(s)
    print(s, flush=True)


def sci(x, n=25):
    """精确有理数的科学计数法截断打印（n 位尾数）。"""
    x = F(x)
    if x == 0:
        return "0"
    sgn = "-" if x < 0 else ""
    x = abs(x)
    e = 0
    while x >= 10:
        x /= 10
        e += 1
    while x < 1:
        x *= 10
        e -= 1
    ip = x.numerator // x.denominator
    fr = x - ip
    digs = []
    for _ in range(n):
        fr *= 10
        d = fr.numerator // fr.denominator
        digs.append(str(d))
        fr -= d
    return "%s%d.%se%d" % (sgn, ip, "".join(digs), e)


def dec(x, ndig):
    """精确有理数的十进制截断打印（整数部分 + ndig 位小数）。"""
    x = F(x)
    sgn = "-" if x < 0 else ""
    x = abs(x)
    ip = x.numerator // x.denominator
    fr = x - ip
    digs = []
    for _ in range(ndig):
        fr *= 10
        d = fr.numerator // fr.denominator
        digs.append(str(d))
        fr -= d
    return "%s%d.%s" % (sgn, ip, "".join(digs))


# ---------- 独立实现一：简单中项行走（无跳段），带显式不变量断言 ----------
def simplest_mediant(A, B, cap=2000):
    """返回 (p, q)：区间 (A, B) 内分母最小的分数。A < B 为有理数。

    括号 x/y <= A < B <= z/w，维持 z*y - x*w = 1（unimodular）。
    若中项 (x+z)/(y+w) 严格落在 (A, B) 内则返回（最小性由单模区间引理保证：
    括号内任何分数 p/q 满足 q >= y + w，证明见正文引理 B）。
    """
    A, B = F(A), F(B)
    assert A < B
    x, y, z, w = 0, 1, 1, 0            # 0/1 与 1/0
    steps = 0
    while steps < cap:
        steps += 1
        assert z * y - x * w == 1, "unimodular 不变量破坏"
        assert F(x, y) <= A and (w == 0 or F(z, w) >= B), "括号包含 (A, B) 的不变量破坏"
        mn, md = x + z, y + w
        m = F(mn, md)
        if A < m < B:
            return m, steps, (x, y, z, w)
        if m <= A:
            x, y = mn, md
        else:
            z, w = mn, md
    raise RuntimeError("中项行走未收敛")


# ---------- 独立实现二：连分数前缀（区间包含判据） ----------
def cf_prefix(lo, hi, maxlen=200):
    """返回 [lo, hi] 内每一点的连分数展开的公共前缀（保证正确的前缀长度）。"""
    digs = []
    lo, hi = F(lo), F(hi)
    for _ in range(maxlen):
        n = lo.numerator // lo.denominator
        if hi.numerator // hi.denominator != n:
            break
        if lo == n:
            break
        digs.append(n)
        lo, hi = F(1, 1) / (hi - n), F(1, 1) / (lo - n)   # 高斯映射（区间保持）
        if lo > hi:
            lo, hi = hi, lo
    return digs


def cf_value(q):
    v = F(0)
    for a in reversed(q):
        v = F(a) + (F(0) if v == 0 else F(1, 1) / v)
    return v


p("=" * 74)
p("kcross-proof cycle-1 route-1：阈值证书（T = R 的两侧）")
p("脚本：tracks/kcross-proof/cycle-1/scripts/k1_threshold_cert.py")
p("只读依赖：70-research/cycle-2/scripts/c2r5_rig.py（未运行任何旧证书脚本）")
p("=" * 74)

# ================= 1. 常数 =================
p("")
p("[1] 常数（严格区间；δ、C 由 c2r5_rig 的 atanh 级数加显式尾界给出）")
DLO, DHI = R.delta_bounds()
CIV = R.C_bounds()
L2 = R.ln2_bounds()
p("     delta ∈ [%s, %s]" % (dec(DLO, 45), dec(DHI, 45)))
p("     delta 区间宽度 = %.3g" % float(DHI - DLO))
p("     C ∈ [%s, %s]  宽度 %.3g" % (dec(CIV[0], 30), dec(CIV[1], 30), float(CIV[1] - CIV[0])))
p("     X0 = 695*2^60 = %d" % R.X0_INT)
KSTAR = F(GAM_D)
p("     K* = %d ；等于分母 ？ %s" % (GAM_D, GAM_D == KSTAR))
p("     gamma = %d/%d ；gcd = %d" % (GAM_N, GAM_D, math.gcd(GAM_N, GAM_D)))
p("     gamma − delta ∈ [%s, %s]" % (sci(GAM - DHI), sci(GAM - DLO)))
p("     gamma > delta ？ %s（严格：gamma > delta_hi）" % (GAM > DHI))

# gamma 的连分数前缀复核（与 c2r5_cert 的 [2] 段对照）
pre = cf_prefix(DLO, R.delta_bounds()[1])
p("     delta 的连分数前缀（本次独立实现，前 %d 项）= %s" % (len(pre), pre))

# ================= 2. 四条端点事实 =================
p("")
p("[2] 四条端点事实（每条：精确有理比较 + 出处）")
# F1: gamma > delta —— 上面已判
p("     F1  gamma > delta              ：%s" % (GAM > DHI))
# F2: gamma − delta < eps_opt(K*)
E_KSTAR = R.eps_bounds(M, M, KSTAR, DLO, DHI, L2)   # 先看 m2=92（K* 处不可行，供对照）
worst_t, worst_lo = None, None
feas_list = []
for t in range(1, M + 1):
    fd = R.feasible_decision(t, M, KSTAR, DLO, DHI, CIV)
    feas_list.append((t, fd))
    if fd is True:
        e = R.eps_bounds(t, M, KSTAR, DLO, DHI, L2)
        if worst_lo is None or e[0] < worst_lo:
            worst_t, worst_lo, worst_hi = t, e[0], e[1]
p("     K* 处可行集判定：True 的个数 = %d ；False 的个数 = %d ；未定 = %d" % (
    sum(1 for _, f in feas_list if f is True),
    sum(1 for _, f in feas_list if f is False),
    sum(1 for _, f in feas_list if f is None)))
p("     不可行的 m2 = %s" % ([t for t, f in feas_list if f is False]))
p("     （对照记录：c2r5_cert.log:24 的 eps(91,92,K*) = 8.973221708617136016326e-42）")
p("     eps_opt(K*) ∈ [%s, %s]（argmin 下界在 m2 = %s 处）" % (
    sci(worst_lo), sci(worst_hi), worst_t))
p("     eps_opt(K*) 区间相对宽度 = %.1e" % float((worst_hi - worst_lo) / worst_lo))
p("     F2  gamma − delta < eps_opt(K*)：%s（比较 gamma − delta < eps_opt(K*) 的下界）" % (
    GAM - DLO < worst_lo))
p("     附：gamma 落在开区间 (delta, delta + eps_opt(K*)) 内？ %s（判据 delta_hi < gamma 且 gamma < delta_lo + eps_lo）" % (
    (GAM > DHI) and (GAM < DLO + worst_lo)))
# F3: Psi_92(K*) = K* 的两侧夹逼（Stern-Brocot）
BETA_LO, BETA_HI = DLO + worst_lo, DHI + worst_hi
s_lo, st1, br1 = simplest_mediant(DLO, BETA_HI)
s_hi, st2, br2 = simplest_mediant(DHI, BETA_LO)
r_lo = R.simplest_fraction(DLO, BETA_HI)
r_hi = R.simplest_fraction(DHI, BETA_LO)
p("     F3  Psi_92(K*) 的两侧夹逼（(delta, delta+eps) ⊂ (delta_lo, beta_hi) 且 ⊃ (delta_hi, beta_lo)）")
p("         下界 simplest(delta_lo, beta_hi) = %s（分母 %d）[独立行走、%d 步；R 库给 %s]" % (
    s_lo, s_lo.denominator, st1, r_lo))
p("         上界 simplest(delta_hi, beta_lo) = %s（分母 %d）[独立行走、%d 步；R 库给 %s]" % (
    s_hi, s_hi.denominator, st2, r_hi))
p("         Psi_92(K*) ∈ [%d, %d] ；= K* ？ %s" % (
    s_lo.denominator, s_hi.denominator, s_lo.denominator == s_hi.denominator == GAM_D))
# F4: K* < U(92)，以及 simplest(delta_lo, gamma) > U(92)
U_LO = R.rd(F(14784, 10000) * M * DLO ** M)
U_HI = R.ru(F(14784, 10000) * M * DHI ** M)
p("     U(92) = 1.4784*92*delta^92 ∈ [%s, %s]" % (dec(U_LO, 9), dec(U_HI, 9)))
p("     F4  K* < U(92) ？ %s（比较 K* < U 下界 %s）" % (KSTAR < U_LO, dec(U_LO, 3)))
w, stw, brw = simplest_mediant(DLO, GAM)
rw = R.simplest_fraction(DLO, GAM)
p("     simplest(delta_lo, gamma) = %s" % w)
p("         （分母 %d；独立行走 %d 步；R 库同值？ %s）" % (
    w.denominator, stw, w == rw))
p("         分母 > U(92) 上界 ？ %s  （%d > %s）" % (
    F(w.denominator) > U_HI, w.denominator, dec(U_HI, 3)))
p("         可核对的最小性证书（单模括号）：x/y = %d/%d ≤ delta_lo ；z/w = %d/%d ≥ gamma ；" % (
    brw[0], brw[1], brw[2], brw[3]))
p("           z·y − x·w = %d（= 1）；中项分母 y + w = %d（= 最小分母）；" % (
    brw[2] * brw[1] - brw[0] * brw[3], brw[1] + brw[3]))
p("           中项严格落在 (delta_lo, gamma) 内？ %s" % (DLO < w < GAM))
p("           （引理 B：括号内任一分数 p/q 满足 q ≥ y + w，故最小分母恰为 y + w）")
SIMP = w.denominator

# ================= 3. 域底与连续性前提 =================
p("")
p("[3] 域与连续性前提")
G1 = R.geom_bounds(1, DLO, DHI)
DOM_LO = R.rd(F(M) * G1[0] * CIV[0])
DOM_HI = R.ru(F(M) * G1[1] * CIV[1])
p("     92*geom(1)*C ∈ [%s, %s]（域底：K > 0 且 F_92(K) != 空 等价于 K >= 该值）" % (
    dec(DOM_LO, 9), dec(DOM_HI, 9)))
worst_thr = None
for t in range(1, M + 1):
    g = R.geom_bounds(t, DLO, DHI)
    thr = R.ru(F(M, t) * g[1] * CIV[1])          # K_thresh(t) 的严格上界
    if worst_thr is None or thr > worst_thr[1]:
        worst_thr = (t, thr)
p("     m2 = 1..92 门槛 K_thresh(m2) = (92/m2)*geom(m2)*C 的上界最大值：m2 = %d 处 %s" % (
    worst_thr[0], dec(worst_thr[1], 3)))
p("     全部门槛 <= 312e18 ？ %s  ⟹ [312e18, 315e18] 上 F_92 恒为 {1, ..., 92}" % (
    worst_thr[1] <= KA0))
p("     域底 < K* < 门槛上界 < 312e18 ？ %s" % (DOM_HI < KSTAR < worst_thr[1] < KA0))

# ================= 4. 主导权（初值区间上） =================
p("")
p("[4] 主导权：ε_opt = ε(92, ·) 在 [312e18, 315e18] 上（两侧端点各用最不利方向）")
e92_lo = R.eps_bounds(M, M, KA0, DLO, DHI, L2)       # 左端、m2=92 的上界
mn, mt = None, None
for t in range(1, M):
    e = R.eps_bounds(t, M, KB0, DLO, DHI, L2)        # 右端、m2<=91 的下界
    if mn is None or e[0] < mn:
        mn, mt = e[0], t
p("     eps(92, 312e18) 上界 = %s ；min_{1<=m2<=91} eps(m2, 315e18) 下界 = %s（m2 = %s）" % (
    sci(e92_lo[1]), sci(mn), mt))
DOMIN = e92_lo[1] < mn
p("     支配不等式 eps(92,KA0)_hi < min eps(m2,KB0)_lo ？ %s" % DOMIN)
p("     ⟹ 对一切 K ∈ [312e18, 315e18]：eps_opt(K) = eps(92, K)（用 K<=KB0 时 eps ≥ 右端值、")
p("        K>=KA0 时 eps(92, ·) <= 左端值；m2=92 在 [KA0,KB0] 上可行，见第 3 节）")
assert DOMIN

# ================= 5. 二分定位 R =================
p("")
p("[5] 二分定位：S(K) = eps_opt(K) − (gamma − delta) 的根 R（%d 步，精确有理中点）" % NSTEPS)
GD_LO, GD_HI = GAM - DHI, GAM - DLO               # gamma − delta 的严格区间


def sign92(K):
    e = R.eps_bounds(M, M, K, DLO, DHI, L2)
    if e[0] > GD_HI:
        return "above"
    if e[1] < GD_LO:
        return "below"
    return None


KA, KB = KA0, KB0
sA, sB = sign92(KA), sign92(KB)
p("     起点 KA = %s 符号 %s ；KB = %s 符号 %s" % (KA, sA, KB, sB))
assert sA == "above" and sB == "below"
t1 = time.time()
for i in range(NSTEPS):
    KM = (KA + KB) / 2
    s = sign92(KM)
    if s == "above":
        KA = KM
    elif s == "below":
        KB = KM
    else:
        p("     ！第 %d 步中点未定，提前停止" % (i + 1))
        break
    if (i + 1) % 40 == 0:
        p("     已完成 %d 步，宽度 %.3g，用时 %.1f s" % (i + 1, float(KB - KA), time.time() - t1))
p("     二分完成：用时 %.1f s" % (time.time() - t1))
WID = KB - KA
p("     R ∈ [KA, KB]")
p("     KA = %s = %s" % (dec(KA, 60), KA))
p("     KB = %s = %s" % (dec(KB, 60), KB))
p("     绝对宽度 = %.6e ；相对宽度 = %.6e" % (float(WID), float(WID / KA)))
p("     一致十进制位（相对宽度对数量级倒数）≈ %d 位" % int(-math.log10(float(WID / KA))))

# ================= 6. 终值复核 =================
p("")
p("[6] 终值复核")
p("     端点符号：eps(92,KA)−(γ−δ) > 0 ？ %s ；eps(92,KB)−(γ−δ) < 0 ？ %s" % (
    sign92(KA) == "above", sign92(KB) == "below"))
e92A = R.eps_bounds(M, M, KA, DLO, DHI, L2)
mnA, mtA = None, None
for t in range(1, M):
    e = R.eps_bounds(t, M, KB, DLO, DHI, L2)
    if mnA is None or e[0] < mnA:
        mnA, mtA = e[0], t
p("     终值主导权：eps(92,KA) 上界 = %s < min_{1<=m2<=91} eps(m2,KB) 下界 = %s（m2 = %s）？ %s" % (
    sci(e92A[1]), sci(mnA), mtA, e92A[1] < mnA))
p("     注：终值端点的可行集仍为 {1,...,92}（门槛上界 < 312e18 < KA）", )
p("     K* < KA ？ %s（K* = %s < %s）" % (KSTAR < KA, KSTAR, dec(KA, 3)))
p("     KB < U(92) 下界 ？ %s（%s < %s）" % (KB < U_LO, dec(KB, 6), dec(U_LO, 6)))

# ================= 7. 一致性对照与上限检查 =================
p("")
p("[7] 与旧记录的对照（只作对照，不作证据）")
p("     cycle-2/c2r5_cert.log:67 的 47 位区间左端 = 313195478959172262876.6365306194907065260231016940260118526233")
p("     cycle-2/c2r5_cert.log:67 的 47 位区间右端 = 313195478959172262876.6365306194907065260231016961279595491105")
OLDL = F(3131954789591722628766365306194907065260231016940260118526233, 10 ** 40)
OLDH = F(3131954789591722628766365306194907065260231016961279595491105, 10 ** 40)
# 旧端点十进制是 dec(K, 40) 的截断打印（c2r5_cert.py:43 至 :54 的实现），
# 故真端点 K1 ∈ [OLDL, OLDL+1e-40)、K2 ∈ [OLDH, OLDH+1e-40)。
p("     本轮区间 ⊆ 旧区间（用截断误差 +1e-40 的最坏情形）？ %s" % (
    OLDL + F(1, 10 ** 40) <= KA and KB + F(1, 10 ** 40) <= OLDH))
p("     余量：KA − 旧左端 = %s ；旧右端 − KB = %s" % (
    dec(KA - OLDL, 30), dec(OLDH - KB, 30)))
p("     cycle-1/route-4.md:201 的 19 位浮点区间 [313195478959172262767.2965..., 313195478959172262933.8299...] 包含本轮区间 ？ %s" % (
    F(313195478959172262767) < KA and KB < F(313195478959172262934)))
p("     route-3 的严格下界 3.131547906e20 < R ？ %s" % (F(3131547906, 10 ** 10) < KA))

p("")
p("[8] 汇总（供报告引用的关键数字）")
p("     SIMPLEST_DEN = %d" % SIMP)
p("     U92 ∈ [%s, %s]" % (dec(U_LO, 9), dec(U_HI, 9)))
p("     KSTAR = %d" % GAM_D)
p("     R_LO = %s" % KA)
p("     R_HI = %s" % KB)
p("     REL_WIDTH = %.6e ；DIGITS = %d" % (float(WID / KA), int(-math.log10(float(WID / KA)))))
p("     总用时 %.1f s" % (time.time() - T0))

p("     R_LO_FRAC = %d/%d" % (KA.numerator, KA.denominator))
p("     R_HI_FRAC = %d/%d" % (KB.numerator, KB.denominator))
p("     U92_LO_FRAC = %d/%d" % (U_LO.numerator, U_LO.denominator))
p("     U92_HI_FRAC = %d/%d" % (U_HI.numerator, U_HI.denominator))
p("     DLO_FRAC = %d/%d" % (DLO.numerator, DLO.denominator))
p("     DHI_FRAC = %d/%d" % (DHI.numerator, DHI.denominator))

with open("results/k1_threshold_cert.log", "w") as f:
    f.write("\n".join(OUT) + "\n")

import json
summary = {
    "delta_lo": str(DLO), "delta_hi": str(DHI),
    "C_lo": str(CIV[0]), "C_hi": str(CIV[1]),
    "domain_floor_lo": str(DOM_LO), "domain_floor_hi": str(DOM_HI),
    "Kstar": str(GAM_D), "gamma": "%d/%d" % (GAM_N, GAM_D),
    "U92_lo": str(U_LO), "U92_hi": str(U_HI),
    "simplest_delta_lo_gamma": "%d/%d" % (w.numerator, w.denominator),
    "simplest_den": w.denominator,
    "R_lo": str(KA), "R_hi": str(KB),
    "abs_width": str(WID), "rel_width": str(WID / KA),
    "digits": int(-math.log10(float(WID / KA))),
    "checks": {
        "F1_gamma_gt_delta": bool(GAM > DHI),
        "F2_gamma_minus_delta_lt_epsstar": bool(GAM - DLO < worst_lo),
        "gamma_in_interval_at_Kstar": bool((GAM > DHI) and (GAM < DLO + worst_lo)),
        "F3_Psi_Kstar_is_Kstar": bool(s_lo.denominator == s_hi.denominator == GAM_D),
        "F4_Kstar_lt_U92": bool(KSTAR < U_LO),
        "simplest_den_gt_U92_hi": bool(F(w.denominator) > U_HI),
        "all_thresholds_le_312e18": bool(worst_thr[1] <= KA0),
        "dominance_on_[312e18,315e18]": bool(DOMIN),
        "final_endpoint_signs": bool((sign92(KA) == "above") and (sign92(KB) == "below")),
        "final_dominance": bool(e92A[1] < mnA),
        "Kstar_lt_R_lo": bool(KSTAR < KA),
        "R_hi_lt_U92_lo": bool(KB < U_LO),
    },
}
with open("results/k1_threshold_cert.json", "w") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print("\n[写出] results/k1_threshold_cert.log 与 results/k1_threshold_cert.json")
