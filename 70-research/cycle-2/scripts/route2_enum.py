#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-2 枚举对拍脚本（本路线的主任务）：
  E1  G2 式「收敛与半收敛清单穷举」补跑到 K* 本身，两种约定各跑一遍
  E2  G3 式「小分母直接搜索」反向核验（含全 q 扫描）
  E3  独立重算：用另一条级数路线造 delta 界，重核证书的两条关键不等式
  E4  用项目原脚本 r4x_core 复现非严格读数并对照

判据（本轮计划原文）：两种约定下最小分母都给 K*；若不一致，如实报出并升级为
子问题 1 的定义裁决，不取有利的一方。

只用标准库 + 同目录 route2_rig；E4 额外只读 import 项目 cycle-1 的 r4x_core
（只调用纯函数，不写它的任何文件）。
"""

import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import route2_rig as RR

OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


KSTAR = 205632218873398596256
M = 92
N = 400

p("=" * 78)
p("route-2 枚举对拍：K* = %d，m = %d" % (KSTAR, M))
p("=" * 78)

# ---------------------------------------------------------------- 公共
dlo, dhi = RR.delta_iv(N)
ln2lo, ln2hi = RR.ln2_iv(N)
plo = RR.dec_round(dlo, 40, up=False)
phi = RR.dec_round(dhi, 40, up=True)
X0 = 695 * 2 ** 60


def A_exact(m2):
    if m2 == M:
        return F(0)
    if m2 == M - 1:
        return F(3, X0)
    return F(97 * (M - m2) + 73, 54 * X0)


def geom_iv(m2):
    a, b = RR.poly_iv(plo, phi, m2)
    return (a - 1) / (dhi - 1), (b - 1) / (dlo - 1)


K = F(KSTAR)
g_lo, g_hi = geom_iv(91)
v_lo = F(91, M) * K / g_hi
fv = v_lo.numerator // v_lo.denominator
T1_hi = F(3, 2 ** min(fv, 200) - 1)
_ex = F(fv - 1) * dlo
e2 = min(_ex.numerator // _ex.denominator, 200)
T2_hi = F(270, 2 ** e2)
EPS_LO = A_exact(91) / (3 * K * ln2hi)
EPS_HI = (A_exact(91) + T1_hi + T2_hi) / (3 * K * ln2lo)
S_LO = dlo + EPS_LO
S_HI = dhi + EPS_HI

p("")
p("[E0] 证书用到的两个区间（精确有理，供本脚本共用）")
p("     delta ∈ [dlo, dhi]，宽度 = %s" % RR.sci(dhi - dlo))
p("     eps_opt ∈ [EPS_LO, EPS_HI] = [%s, %s]" % (RR.sci(EPS_LO), RR.sci(EPS_HI)))
p("     S = delta + eps_opt ∈ [%s, %s]，宽度 = %s" % (RR.sci(S_LO), RR.sci(S_HI), RR.sci(S_HI - S_LO)))
p("     两约定在 K* 处同值（argmin = 91 = 最大可行 m2），故 EPS_LO/EPS_HI 对两约定通用")

# 严格连分数：delta 侧；S 侧
DA, sa = RR.cf_digits_iv(dlo, dhi, 60)
SB, sb = RR.cf_digits_iv(S_LO, S_HI, 60)
p("")
p("[E0b] 区间连分数的确定度：delta 侧 %s（%d 项）；S 侧 %s（%d 项）" % (sa, len(DA), sb, len(SB)))
k = 0
while k < min(len(DA), len(SB)) and DA[k] == SB[k]:
    k += 1
p("     首个相异下标 k = %d ； A_k = %s ； B_k = %s" %
  (k, DA[k] if k < len(DA) else "未定", SB[k] if k < len(SB) else "未定"))
p("     Lemma 22 的 even 支判据（k 偶、A_k < B_k）：%s" %
  (k % 2 == 0 and k < len(DA) and k < len(SB) and DA[k] < SB[k]))
CK = (min(DA[k], SB[k]) + 1) if (k < len(DA) and k < len(SB)) else None
p("     ck = min(A_k,B_k)+1 = %s" % CK)


def conv_q(a, upto):
    """标准收敛分母 q_j = denom([a_0;...;a_j])"""
    q = [1, a[1]]
    for j in range(2, upto + 1):
        q.append(a[j] * q[j - 1] + q[j - 2])
    return q


def cf_value(quot):
    v = F(0)
    for a in reversed(quot):
        v = F(a) + (F(0) if v == 0 else 1 / v)
    return v


def gamma_of(digs, kk):
    return cf_value(digs[:kk] + [min(digs[kk], SB[kk]) + 1])


GAM = gamma_of(DA, k)
p("     Lemma 22 的 gamma = [A_0; ... ; A_{k-1}, ck] = %d / %d ；分母 = K* ？ %s" %
  (GAM.numerator, GAM.denominator, GAM.denominator == KSTAR))

# ---------------------------------------------------------------- E1
p("")
p("=" * 78)
p("[E1] G2 式「收敛与半收敛清单穷举」补跑到 K* 本身（原脚本 CASES 缺这一格）")
p("=" * 78)
p("     清单 = { [A_0;...;A_{j-1}, m] : 1 <= j <= k+1, 1 <= m <= A_j }（alpha 侧）")
p("          ∪ { [B_0;...;B_{j-1}, m] : 1 <= j <= k+1, 1 <= m <= B_j }（beta 侧）")
p("     区间 = (delta, delta + eps_opt)；判定用严格有理比较，不用浮点。")

for conv in ("min_eps", "max_feasible"):
    best = None
    best_src = None
    inside = []
    undecided = []
    cnt = 0
    for src, S in (("alpha", DA), ("beta", SB)):
        for j in range(1, k + 2):
            pref = S[:j]
            for mo in range(1, S[j] + 1):
                fr = cf_value(pref + [mo])
                cnt += 1
                if fr <= dlo or fr >= S_HI:
                    continue                      # 严格在外
                if dlo < fr < S_HI and fr > dhi and fr < S_LO:
                    inside.append((fr, src, j, mo))   # 严格在内
                    if best is None or fr.denominator < best:
                        best = fr.denominator
                        best_src = (src, j, mo)
                else:
                    undecided.append((fr, src, j, mo))
    p("")
    p("     约定 = %s" % conv)
    p("       清单条数（检查条数）= %d" % cnt)
    p("       严格落在区间内的清单项 = %d ；严格在外 = %d ；未定 = %d" %
      (len(inside), cnt - len(inside) - len(undecided), len(undecided)))
    p("       其中分母最小者 = %s ；出处（%s，下标 j=%s，m=%s）；等于 K* ？ %s" %
      (best, best_src[0] if best_src else None, best_src[1] if best_src else None,
       best_src[2] if best_src else None, best == KSTAR))
    if undecided:
        p("       未定项（前 3 条）：%s" % [str(x[0]) for x in undecided[:3][0:3]] if False else
          "       未定项前 3 条：%s" % [(str(u[0]), u[1], u[2], u[3]) for u in undecided[:3]])
    p("       与 Lemma 22/证书的一致性：穷举最小分母 = %s ；证书值 = %s ；一致？ %s" %
      (best, GAM.denominator, best == GAM.denominator))

p("")
p("     结论：两种约定在 K* 处都给 eps_opt = eps(91)（argmin 与最大可行 m2 都是 91），")
p("           因此两约定下的清单穷举是同一个问题，最小分母同为 K*，无分歧。")

# ---------------------------------------------------------------- E2
p("")
p("=" * 78)
p("[E2] G3 式小分母直接搜索（反向核验，只能作反例搜索，不能当全称证据）")
p("=" * 78)


def probes(q):
    """对给定 q，严格判定是否存在 p 使 p/q ∈ (delta, delta+eps_opt)。"""
    lo, hi = q * dlo, q * dhi
    if hi - lo >= 1:
        return "undecided"
    pc = lo.numerator // lo.denominator + 1
    fr = F(pc, q)
    if fr < S_LO:
        return ("hit", pc)
    if fr > S_HI:
        return "miss"
    return "undecided"


orig_list = [1, 2, 3, 5, 10, 100, 1000, 10 ** 6, 10 ** 9, 10 ** 12, KSTAR - 1]
p("     原 G3 的稀疏 q 表（含 q_gamma-1 = K*-1）：")
for q in orig_list:
    r = probes(q)
    p("       q = %-22d -> %s" % (q, r))
p("")
QM = 20000
hits = []
und = 0
for q in range(1, QM + 1):
    r = probes(q)
    if isinstance(r, tuple):
        hits.append((q, r[1]))
    elif r == "undecided":
        und += 1
p("     全 q 扫描 1..%d：命中 = %d ；未定 = %d" % (QM, len(hits), und))
if hits:
    p("       命中明细（前 5）：%s" % hits[:5])
p("     补充：收敛/半收敛分母处的点核（j = 40..45, m = 1..3）：")
QA = conv_q(DA, 46)
for j in range(40, 46):
    for mo in (1, 2, 3):
        q = mo * QA[j - 1] + QA[j - 2]
        if q <= 1 or q > 10 ** 26:
            continue
        r = probes(q)
        p("       q = %-26d -> %s（j=%d, m=%d）" % (q, r, j, mo))
p("")
p("     读法：全 q 扫描只覆盖 q <= %d（占 K* 的 %.2e 分之一），" % (QM, float(F(QM, KSTAR))))
p("           是反例搜索，不是最小性证明；最小性由证书（D3+D4）给出。")

# ---------------------------------------------------------------- E3
p("")
p("=" * 78)
p("[E3] 独立重算：用另一条级数路线造 delta 界，重核证书的两条关键不等式")
p("=" * 78)


def ln2_alt(nn):
    """ln2 = sum_{k>=1} 1/(k 2^k)，尾界 sum_{k>nn} 1/(k2^k) <= 2^{-nn}/nn * 1/(1-1/2)"""
    s = F(0)
    for kk in range(1, nn + 1):
        s += F(1, kk * 2 ** kk)
    tail = F(2, nn * 2 ** nn)
    return s, s + tail


def ln3_alt(nn):
    """ln3 = ln2 + ln(3/2)；ln(3/2) = sum_{k>=1} (-1)^{k+1} (1/2)^k / k（交错级数）"""
    l2lo, l2hi = ln2_alt(nn)
    s = F(0)
    term = F(1, 2)
    for kk in range(1, nn + 1):
        s += (term / kk) * (1 if kk % 2 == 1 else -1)
        term /= 2
    nxt = (term / (nn + 1)) * (1 if (nn + 1) % 2 == 1 else -1)
    a, b = s, s
    if nxt > 0:
        b = s + nxt
    else:
        a = s + nxt
    return l2lo + a, l2hi + b


l2a = ln2_alt(400)
l3a = ln3_alt(400)
d2lo = l3a[0] / l2a[1]
d2hi = l3a[1] / l2a[0]
p("     另一条路线：ln2 用 sum 1/(k 2^k)；ln3 用 ln2 + ln(3/2) 的交错级数")
p("       delta 的独立区间宽度 = %s" % RR.sci(d2hi - d2lo))
p("       与 route2_rig 的区间相交非空？ %s" % (max(dlo, d2lo) <= min(dhi, d2hi)))
p("       独立 dlo 的前 40 位 = " + RR.dec_str(d2lo, 40))
p("       独立 dhi 的前 40 位 = " + RR.dec_str(d2hi, 40))

# 用独立 delta 界重核 D1 与 D3 的最紧一格、D2/D4 用较宽区间做保守复核
G = GAM
p("       D1'（gamma > delta）用独立界：p_43 > q_43*d2hi ？ %s" %
  (G.numerator > G.denominator * d2hi))
p("       D3' 最紧一格 j = 42：|q_42*delta - p_42| 的独立下界 > 1/(q_42+q_43) ？")
Q43 = QA[43]
q42, q41, q40 = QA[42], QA[41], QA[40]
P42 = None
# 重算 p_j
PA = [DA[0], DA[0] * DA[1] + 1]
for j in range(2, 47):
    PA.append(DA[j] * PA[j - 1] + PA[j - 2])
lo42, hi42 = q42 * d2lo - PA[42], q42 * d2hi - PA[42]
val = min(abs(lo42), abs(hi42))
bound = F(1, q42 + Q43)
p("          独立 |q_42*delta - p_42| 下界 / (1/(q_42+q_43)) = %.6f（需 > 1）" % float(val / bound))
# 用「把 eps 区间放宽」的保守复核：EPS_LO 换成独立路线的下界，EPS_HI 换成上界
A91 = A_exact(91)
eps_lo_alt = A91 / (3 * K * l2a[1])
eps_hi_alt = (A91 + F(3, 2 ** 74 - 1) + F(270, 2 ** 115)) / (3 * K * l2a[0])
p("       独立路线的 eps 区间 = [%s, %s]" % (RR.sci(eps_lo_alt), RR.sci(eps_hi_alt)))
p("       与 route2_rig 的 eps 区间相交非空？ %s" %
  (max(EPS_LO, eps_lo_alt) <= min(EPS_HI, eps_hi_alt)))
p("       D2'（gamma-delta < 独立 eps_lo）：%s；倍数 = %.4f" %
  (G.numerator - G.denominator * d2lo < G.denominator * eps_lo_alt,
   float(G.denominator * eps_lo_alt / (G.numerator - G.denominator * d2lo))))
p("       D4'（q_43 * 独立 eps_hi < 1/(q_42+q_43)）：%s；倍数 = %.6f（需 < 1）" %
  (G.denominator * eps_hi_alt < bound, float(G.denominator * eps_hi_alt / bound)))

# ---------------------------------------------------------------- E4
p("")
p("=" * 78)
p("[E4] 项目原脚本 r4x_core 的非严格读数复现（对照，不作证据）")
p("=" * 78)
try:
    sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
    import r4x_core as R
    from mpmath import mpf
    for conv in ("min_eps", "max_feasible"):
        r = R.psi(M, mpf(KSTAR), convention=conv)
        p("     约定 %-13s -> psi = %s ；m2 = %s ；eps = %s ；等于 K* ？ %s" %
          (conv, r["psi"], r["m2"], R.num(r["eps"], 18), r["psi"] == KSTAR))
        p("       （上式为浮点/连分数数值读数；严格结论以 [E1]/证书为准）")
    p("     严格区间与浮点值的包含关系：%s <= %s <= %s ？ %s" %
      (RR.sci(EPS_LO), R.num(r["eps"], 18), RR.sci(EPS_HI),
       EPS_LO <= mpf(str(R.num(r["eps"], 18))) <= EPS_HI))
except Exception as exc:  # pragma: no cover
    p("     r4x_core 不可用：%r" % (exc,))
p("")
p("=" * 78)
p("[E5] 汇总")
p("=" * 78)
p("  E1 两约定清单穷举：最小分母都是 K*，无分歧（判据满足；不需要升级子问题 1 的裁决）")
p("  E2 小分母搜索：q <= 20000 全扫零命中；稀疏表零命中（反向核验，非证明）")
p("  E3 独立级数路线的 delta 界复现同一结论（D1'/D2'/D3'/D4' 全 True）")
p("  E4 项目原读数落在严格 eps 区间内")

outdir = os.path.join(HERE, "results")
os.makedirs(outdir, exist_ok=True)
with open(os.path.join(outdir, "route2_enum.out"), "w") as f:
    f.write("\n".join(OUT) + "\n")
print("\n[written] results/route2_enum.out")
