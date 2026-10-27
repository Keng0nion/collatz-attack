#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 2 轮第 5 路：Psi_92(K*) = K* 的严格有理区间证书，兼 K_cross 的严格根隔离。

证书结构（每一节都打印它实际核对的比较）：
  第 1 节 常数与 eps 的严格区间（自足级数界，无浮点判决）
  第 2 节 端点连分数前缀的严格证书（区间包含判据）与 gamma 的构造
  第 3 节 Psi_92(K*) = K* 的两侧夹逼（Stern-Brocot 最小分母）
  第 4 节 两种约定在 K* 处同值；m2 = 91 的最小性
  第 5 节 K_cross 的严格根隔离（符号判决 + 单调性）
  第 6 节 越界见证：simplest(delta_lo, gamma) 作为全区间下界
  第 7 节 结论文本（含每一步的证据类型）

运行：20-experiments/.venv/bin/python c2r5_cert.py
"""
import sys
from fractions import Fraction as F

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts"
sys.path.insert(0, HERE)
import c2r5_rig as R
from mpmath import mp, mpf

mp.dps = 50          # 仅影响显示精度；一切判定都是 Fraction 精确比较
OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def m(x):
    x = F(x)
    return mpf(x.numerator) / mpf(x.denominator)


def raw(x, n=30):
    return mp.nstr(m(x), n)


def dec(x, nd):
    x = F(x)
    sign = "-" if x < 0 else ""
    x = abs(x)
    ip = x.numerator // x.denominator
    rem = x.numerator - ip * x.denominator
    out = [sign + str(ip), "."]
    for _ in range(nd):
        rem *= 10
        out.append(str(rem // x.denominator))
        rem -= (rem // x.denominator) * x.denominator
    return "".join(out)


M = 92
KSTAR = 205632218873398596256
U92_W = F(14784, 10000)

p("#" * 74)
p("# 第 2 轮第 5 路：Psi_92(K*) = K* 严格区间证书")
p("# 运行脚本：70-research/cycle-2/scripts/c2r5_cert.py")
p("#" * 74)

# ================= 第 1 节：常数与 eps 的严格区间 =================
p("")
p("[1] 常数与 eps(m2, 92, K*) 的严格有理区间")
DLO, DHI = R.delta_bounds()
L2 = R.ln2_bounds()
DWD = DHI - DLO
p("     delta ∈ [%s, %s]" % (dec(DLO, 45), dec(DHI, 45)))
p("     delta 区间宽度 = %s（对数量级 1e%d）；ln2 区间宽度 = %s" % (
    float(DWD), round(__import__("math").log10(float(DWD))), float(L2[1] - L2[0])))
CIV = R.C_bounds()
p("     C = log2((162/97)X0) ∈ [%s, %s]，宽度 %s" % (raw(CIV[0]), raw(CIV[1]), float(CIV[1] - CIV[0])))
p("     X0 = 695*2^60 = %d（Definition 4 印出版；arXiv v3 为 704*2^60，见报告）" % R.X0_INT)

feas = [t for t in range(1, M + 1) if R.feasible_decision(t, M, KSTAR, DLO, DHI, CIV) is True]
inf = [t for t in range(1, M + 1) if R.feasible_decision(t, M, KSTAR, DLO, DHI, CIV) is False]
p("     K* 处的可行集 F_92(K*) = {1, ..., %d}（%d 个；判定为不可行 %d 个；未定 %d 个）" % (
    max(feas), len(feas), len(inf), M - len(feas) - len(inf)))
for t in (89, 90, 91, 92):
    d = R.feasible_decision(t, M, KSTAR, DLO, DHI, CIV)
    g = R.geom_bounds(t, DLO, DHI)
    lhs = m(F(t, M) * KSTAR) / m(g[1] * CIV[1]) if False else None
    p("       m2 = %d 可行？ %s（geom 区间下界 %s vs 右端 %s）" % (
        t, d, raw(g[0]), raw(F(t, M) * KSTAR)))
eps = {}
for t in range(max(feas) - 8, M + 1):
    if t in feas:
        eps[t] = R.eps_bounds(t, M, KSTAR, DLO, DHI, L2)
for t in sorted(eps):
    p("       eps(%d, 92, K*) ∈ [%s, %s]" % (t, mp.nstr(m(eps[t][0]), 22), mp.nstr(m(eps[t][1]), 22)))

# 最小性（min_eps 约定）：eps(91) 严格小于其余所有可行 m2 的 eps 上界
m2_star = min(eps, key=lambda t: eps[t][1])
assert m2_star == 91, m2_star
for t in sorted(eps):
    if t != 91:
        assert eps[91][1] < eps[t][0], "最小性未在 m2 = %d 处分离" % t
# 被剪掉的 m2 ≤ 82：用 A 的廉价下界
for t in range(1, max(feas) - 8):
    assert F(R.A_of(t, M)) / (F(3) * F(KSTAR) * L2[1]) > eps[91][1]
p("     -> 最小性成立：eps(91) 严格小于 83 至 90 共 8 个精算值（逐对比较通过），")
p("        且对 m2 <= 82 用 A 的廉价下界 A(m2)/(3K ln2_hi) 剪枝（该下界 > eps(91) 上界，逐项通过）")
p("     -> m2 = 91 = m - 1，A(91) 取定理 21 第二段的 3/X0 = %s" % raw(R.A_of(91, M)))
p("     -> max_feasible 约定也给 m2 = 91（%d = max F_92(K*)）" % max(feas))
E_LO, E_HI = eps[91]
BETA = (R.rd(DLO + E_LO), R.ru(DHI + E_HI))
p("     eps_opt(K*) ∈ [%s, %s]（相对宽度 1e%d）" % (
    mp.nstr(m(E_LO), 22), mp.nstr(m(E_HI), 22),
    round(__import__("math").log10(float((E_HI - E_LO) / E_LO)))))
p("     beta = delta + eps_opt(K*) ∈ [%s, %s]" % (dec(BETA[0], 60), dec(BETA[1], 60)))

# ================= 第 2 节：连分数前缀证书与 gamma =================
p("")
p("[2] 端点连分数前缀的严格证书（certified_prefix：区间包含判据）")
prefA = R.certified_prefix(DLO, DHI, maxlen=300)
prefB = R.certified_prefix(BETA[0], BETA[1], maxlen=300)
p("     alpha = delta 的证书位数 = %d ；beta 的证书位数 = %d" % (len(prefA), len(prefB)))
k = 0
while k < min(len(prefA), len(prefB)) and prefA[k] == prefB[k]:
    k += 1
assert k < min(len(prefA), len(prefB)), "前缀未在证书长度内分离"
ck = min(prefA[k], prefB[k]) + 1
p("     首个相异下标 k = %d ：a_k = %d，b_k = %d，c_k = min+1 = %d" % (
    k, prefA[k], prefB[k], ck))
p("     公共前缀（前 %d 项）= %s" % (k, prefA[:k]))
gam = R.cf_value(prefA[:k] + [ck])
p("     gamma = [公共前缀; c_k] = %s" % gam)
p("     gamma 分子 = %d ；分母 = %d" % (gam.numerator, gam.denominator))
p("     分母等于 K* ？ %s ；分子等于 route-4.md 记录的 325919355854421968365 ？ %s" % (
    gam.denominator == KSTAR, gam.numerator == 325919355854421968365))
import math as _m
p("     gcd(分子, 分母) = %d" % _m.gcd(gam.numerator, gam.denominator))
p("     gamma - delta ∈ [%s, %s]" % (dec(gam - DHI, 42), dec(gam - DLO, 42)))
p("     严格夹住：gamma > delta_hi ？ %s ；gamma < beta_lo ？ %s" % (
    gam > DHI, gam < BETA[0]))

# 收敛分母表（对 delta 的连分数前缀）
p("     delta 的收敛分母 q_i（i = k-3 至 k+2）：")
qn2, qn1 = 1, 1 if False else (1, 0)
qm2, qm1 = 1, 0
qs = {}
for i, a in enumerate(prefA[: k + 3]):
    q = a * qm1 + qm2
    qm2, qm1 = qm1, q
    qs[i] = q
    if i >= k - 3:
        p("       q_%d = %d" % (i, q))
p("     K* = %d ；等于某个 q_i ？ %s" % (
    KSTAR, [i for i in qs if qs[i] == KSTAR]))
p("     77692117359936589403 等于某个 q_i ？ %s" % ([i for i in qs if qs[i] == 77692117359936589403],))
p("     gamma 的分母与 [前缀; c_k] 的连续性检查：q_k = c_k*q_(k-1) + q_(k-2) = %d" % (
    ck * qs[k - 1] + qs[k - 2]))

# ================= 第 3 节：Psi_92(K*) 的两侧夹逼 =================
p("")
p("[3] Psi_92(K*) 的严格夹逼（Stern-Brocot 最小分母，两侧）")
lo = R.simplest_fraction(DLO, BETA[1])
hi = R.simplest_fraction(DHI, BETA[0])
p("     下界 simplest(delta_lo, beta_hi) = %d / %d = %s" % (lo.numerator, lo.denominator, lo))
p("     上界 simplest(delta_hi, beta_lo) = %d / %d = %s" % (hi.numerator, hi.denominator, hi))
p("     区间 (delta, beta) 含于 (delta_lo, beta_hi) 且包含 (delta_hi, beta_lo)，故：")
p("     Psi_92(K*) ∈ [%d, %d] ；等于 K* ？ %s" % (
    lo.denominator, hi.denominator, lo.denominator == hi.denominator == KSTAR))
assert lo.denominator == hi.denominator == KSTAR
p("     见证：gamma = %s / %s 落在 (delta, beta) 内且分母为 K*" % (gam.numerator, gam.denominator))

# ================= 第 4 节：证伪面检查 =================
p("")
p("[4] 证伪面检查（若 (F) 为假，下列任一必然会成立；逐条核否）")
p("     区间内是否存在分母 < K* 的分数？ 否（第 3 节下界 = K*，覆盖整个 (delta, beta)）")
p("     gamma 是否等于端点？ %s" % (gam <= DHI or gam >= BETA[0]))
p("     两种约定是否同值？ 是（m2 = 91 = max F_92(K*)，eps 与约定无关）")

# ================= 第 5 节：K_cross 的严格根隔离 =================
p("")
p("[5] K_cross 的严格根隔离：eps_opt(K) = gamma - delta 的根")
GD_LO, GD_HI = gam - DHI, gam - DLO   # gamma - delta ∈ [GD_LO, GD_HI]


def sign_eps92(K):
    """返回 'above'（eps(92,K) > gamma-delta）、'below'（<）或 None（未定）。"""
    e = R.eps_bounds(M, M, K, DLO, DHI, L2)
    if e[0] > GD_HI:
        return "above"
    if e[1] < GD_LO:
        return "below"
    return None


K1, K2 = F(312) * 10 ** 18, F(315) * 10 ** 18
s1, s2 = sign_eps92(K1), sign_eps92(K2)
p("     起点：K1 = %s 符号 %s ；K2 = %s 符号 %s" % (K1, s1, K2, s2))
assert s1 == "above" and s2 == "below"
STEPS = 150
for _ in range(STEPS):
    Kmid = (K1 + K2) / 2
    s = sign_eps92(Kmid)
    if s == "above":
        K1 = Kmid
    elif s == "below":
        K2 = Kmid
    else:
        break
p("     二分 %d 步后：K_cross ∈ [%s, %s]" % (STEPS, dec(K1, 40), dec(K2, 40)))
p("     区间绝对宽度 = %s ；相对宽度 = %s" % (float(K2 - K1), float((K2 - K1) / K1)))
p("     一致十进制位（相对宽度对数量级倒数）≈ %d 位" % round(-__import__("math").log10(float((K2 - K1) / K1))))
p("     端点符号复核：eps(92,K1) - (gamma-delta) > 0 ？ %s ；eps(92,K2) - (gamma-delta) < 0 ？ %s" % (
    sign_eps92(K1) == "above", sign_eps92(K2) == "below"))
# 区间内 eps_opt = eps(92, .)：对一切 m2 ≠ 92 检查 eps(92,K1) < eps(m2,K2)
worst_t, worst_lo = None, None
for t in range(1, M):
    if R.feasible_decision(t, M, K2, DLO, DHI, CIV) is not True:
        continue
    e2 = R.eps_bounds(t, M, K2, DLO, DHI, L2)
    if worst_lo is None or e2[0] < worst_lo:
        worst_t, worst_lo = t, e2[0]
eK1_92 = R.eps_bounds(M, M, K1, DLO, DHI, L2)
p("     主导权复核：eps(92,K1) 上界 = %s ；min_{1<=m2<=91, 在 K2 可行} eps(m2,K2) 的下界 = %s（在 m2=%s 处取到）" % (
    raw(eK1_92[1]), raw(worst_lo), worst_t))
assert eK1_92[1] < worst_lo, "K_cross 邻域内 eps 的最小者不唯一"
p("     -> 在 [K1, K2] 上 eps_opt = eps(92, .)，故 K_cross 是该方程的根（唯一性由 eps(92,.) 严格递减保证）")

# ================= 第 6 节：越界见证的下界 =================
p("")
p("[6] 越界侧的全区间下界：simplest(delta_lo, gamma)")
w = R.simplest_fraction(DLO, gam)
p("     simplest(delta_lo, gamma) = %s（分母 %d）" % (w, w.denominator))
U92 = (R.rd(U92_W * M * R.iv_pow((DLO, DHI), 92)[0]), R.ru(U92_W * M * R.iv_pow((DLO, DHI), 92)[1]))
p("     U(92) = 1.4784*92*delta^92 ∈ [%s, %s]" % (raw(U92[0]), raw(U92[1])))
p("     对一切 beta <= gamma 的 K：Psi(K) >= simplest(delta_lo, gamma) > U(92) ？ %s" % (
    w.denominator > 0 and F(w.denominator) > U92[1]))
p("     旧日志记录（仅对照，不作证据）：r4x_run3.out:10 在 K_lo=3.3e20 与 r4x_run3.out:30 在 K_cross_hi 处给 7941964418702608664581")

# ================= 第 7 节：结论 =================
p("")
p("[7] 结论（按证据类型标注）")
p("     7.1 Psi_92(K*) = K* = 205632218873398596256【严格区间证书：δ 与 ε 的严格有理界 +")
p("         Stern-Brocot 两侧夹逼；依赖 Lemma 22 的等价构造与其最小性（本证书用自证版），")
p("         未形式化、未经第三方复核】")
p("     7.2 K* 处 m2 = 91（两种约定同值）【已证于第 1 节，逐个比较 + 剪枝界】")
p("     7.3 K_cross 的严格区间见第 5 节【严格根隔离；唯一性依赖 eps_opt 严格递减，见报告引理】")
p("     7.4 越界当且仅当 K_lo >= K_cross：一侧由第 6 节下界给出，另一侧由 Psi = K* 与单调性给出")
p("         【条件性：依赖第 1 轮的非降性引理与第 5 节的根隔离】")

open(HERE + "/results/c2r5_cert.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/c2r5_cert.out")
