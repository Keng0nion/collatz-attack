#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r3_logdomain.py : 路线 3（对数域解析判据）自足脚本。

只用 fractions.Fraction 与 int 做**判据**：不使用 mpmath，不使用浮点判定。
mpmath 只在 [S9] 段用于打印对照（标为展示）。

对象（Page 13 渲染图本次亲读；抽取 hercher5.txt:695 至 :724 本次亲读）：
  Theorem 21 的 m2 = m 特例，取 m = 91（第七步）：
    E(K) := (1/(K ln2)) * (1/(2^v - 1)) * (1 + 90/(2^v - 1)^(delta-1)),
    v = (m2/m) K (delta-1)/(delta^m2 - 1) = K (delta-1)/(delta^91 - 1)     (m2 = m = 91)
  关键恒等式（本脚本用到的全部）：
    (ln1) ln(1/E(K)) = Lambda(K) - Psi2(K) - ln(1+R(K)),
          Lambda(K) = ln K + ln ln 2 + t(K),  t(K) = v ln 2 = K (ln3 - ln2)/(delta^91 - 1),
          R(K) = 90 (2^v - 1)^{1-delta},  Psi2(K) = -ln(1 - 2^{-v}) = 2^{-v} + O(4^{-v}).
    (ln2) ln(E(K1)/E(K2)) = ln(K2/K1) + (K2-K1) A/D - Theta,  0 < Theta <= R(K1) + 4*2^{-v(K1)},
          A = ln3 - ln2, D = delta^91 - 1.
"""
import math
import pathlib
import sys
import time
from fractions import Fraction as F

T0 = time.time()
OUT = []
def say(*a):
    line = " ".join(str(x) for x in a)
    OUT.append(line)
    print(line, flush=True)

# ---------------------------------------------------------------- 十进制取整（精确）
def floor_dec(f, k):
    return F(math.floor(f * 10 ** k), 10 ** k)

def ceil_dec(f, k):
    return F(-math.floor(-f * 10 ** k), 10 ** k)

def round_out(iv, k):
    return (floor_dec(iv[0], k), ceil_dec(iv[1], k))

def dec(f, digits=25):
    """展示用十进制（向下取整到 digits 位有效数字），非判据。"""
    if f == 0:
        return "0"
    s = "-" if f < 0 else ""
    g = abs(f)
    e = 0
    while g >= 10:
        g /= 10
        e += 1
    while g < 1:
        g *= 10
        e -= 1
    n = math.floor(g * 10 ** digits)
    return "%s%d.%s e%d" % (s, n // 10 ** digits, str(n % 10 ** digits).zfill(digits), e)

def iv_dec(iv, digits=25):
    return "[%s , %s]" % (dec(iv[0], digits), dec(iv[1], digits))

# ---------------------------------------------------------------- ln：atanh 级数 + 显式尾界
def _ln_unit(x, N):
    """1 <= x < 2：返回 ln x 的有理上下界（尾界 2u^{2N+3}/((2N+3)(1-u^2))）。"""
    u = (x - 1) / (x + 1)
    u2 = u * u
    s = F(0)
    p = u
    for k in range(N + 1):
        s += p / (2 * k + 1)
        p *= u2
    lo = 2 * s
    tail = 2 * u ** (2 * N + 3) / ((2 * N + 3) * (1 - u2))
    return (lo, lo + tail)

LN2 = _ln_unit(F(2), 100)

def ln_bounds(x, N=80):
    """x: Fraction > 0。先并入 [1,2) 再展级数：ln x = ln m + s ln 2。"""
    m = F(x)
    s = 0
    while m >= 2:
        m /= 2
        s += 1
    while m < 1:
        m *= 2
        s -= 1
    lo, hi = _ln_unit(m, N)
    if s >= 0:
        return (lo + s * LN2[0], hi + s * LN2[1])
    return (lo + s * LN2[1], hi + s * LN2[0])

# ---------------------------------------------------------------- exp：部分和 + 显式尾界
def exp_lower(x, N):
    """x >= 0：e^x 的下界（部分和，全正项）。"""
    s = F(0)
    term = F(1)
    for k in range(N + 1):
        s += term
        term = term * x / (k + 1)
    return s

def exp_bounds(x, N):
    """x >= 0：e^x 的有理上下界；要求 x/(N+2) < 1。"""
    if x == 0:
        return (F(1), F(1))
    if x / (N + 2) >= 1:
        raise ValueError("exp 尾部条件不满足")
    lo = exp_lower(x, N)
    rem = x ** (N + 1) / F(math.factorial(N + 1)) / (1 - x / (N + 2))
    return (lo, lo + rem)

# ---------------------------------------------------------------- 常数（全部向外取整到 40 位小数）
P = 40
LN2 = round_out(LN2, P)
LN3 = round_out(ln_bounds(F(3), 100), P)
LN5 = round_out(ln_bounds(F(5), 100), P)
LN10 = (LN2[0] + LN5[0], LN2[1] + LN5[1])
LN_LN2 = round_out((ln_bounds(LN2[0], 80)[0], ln_bounds(LN2[1], 80)[0]), P)
DELTA = round_out((LN3[0] / LN2[1], LN3[1] / LN2[0]), P)
LND = round_out((ln_bounds(LN3[0], 80)[0] - ln_bounds(LN2[1], 80)[1],
                 ln_bounds(LN3[1], 80)[0] - ln_bounds(LN2[0], 80)[1]), P)
M91 = 91
D91 = round_out((exp_bounds(M91 * LND[0], 300)[0], exp_bounds(M91 * LND[1], 300)[1]), P)
D = (D91[0] - 1, D91[1] - 1)
A = (LN3[0] - LN2[1], LN3[1] - LN2[0])
AD = (A[0] / D[1], A[1] / D[0])
ADM = (AD[0] + AD[1]) / 2
DELM = (DELTA[0] + DELTA[1]) / 2
LN2M = (LN2[0] + LN2[1]) / 2

N_EXP = 200          # 判据用的 exp 级数长度（严格，仅影响余项松紧）

# ---------------------------------------------------------------- 核心：Lambda、余项、判定
def lam_info(K, N_exp=N_EXP):
    """返回 (Lambda 区间, R 上界, 2^{-v} 上界)。K 为 int。"""
    lnK = ln_bounds(F(K), 80)
    t = (F(K) * AD[0], F(K) * AD[1])
    lam = (lnK[0] + LN_LN2[0] + t[0], lnK[1] + LN_LN2[1] + t[1])
    eps = 1 / exp_lower(t[0], N_exp)                 # 2^{-v} <= eps
    Y_lo = (DELTA[0] - 1) * (t[0] - 2 * eps)         # Y = (delta-1) ln(2^v-1) >= Y_lo
    R_hi = 90 / exp_lower(Y_lo, N_exp)               # R <= R_hi
    return lam, R_hi, eps

def ln1E_bounds(K, N_exp=N_EXP):
    """ln(1/E(K)) 的严格区间 [Lambda_lo - R_hi - 2 eps , Lambda_hi]。"""
    lam, R_hi, eps = lam_info(K, N_exp)
    return (lam[0] - R_hi - 2 * eps, lam[1]), R_hi, eps

def ln1w_bounds(w, N=100):
    """w 为 Fraction：ln(1/w) 的严格区间。"""
    b = ln_bounds(w, N)
    return (-b[1], -b[0])

def pred(K, w, strict, N_exp=N_EXP):
    """判定 E(K) < w（strict=True）或 E(K) <= w（strict=False）。
    返回 True / False / None（None = 本判据的余项不足以判定）。"""
    p, q = ln1E_bounds(K, N_exp)[0]
    lw = ln1w_bounds(w)
    if strict:
        if p > lw[1]:  return True      # ln(1/E) > ln(1/w) => E < w
        if q <= lw[0]: return False
        return None
    else:
        if p >= lw[1]: return True      # E <= w
        if q < lw[0]:  return False
        return None

def search_true(w, strict, loK, hiK, N_exp=N_EXP):
    """min{K in [loK,hiK] : pred(K) is True}（把 None 当 False），结果点带证书。"""
    assert pred(hiK, w, strict, N_exp) is True, "上端不是 True"
    assert pred(loK, w, strict, N_exp) is False, "下端不是 False"
    a, b = loK, hiK
    while b - a > 1:
        mid = (a + b) // 2
        if pred(mid, w, strict, N_exp) is True:
            b = mid
        else:
            a = mid
    assert pred(b, w, strict, N_exp) is True
    return b

def search_false(w, strict, loK, hiK, N_exp=N_EXP):
    """max{K in [loK,hiK] : pred(K) is False}（把 None 当 True），结果点带证书。"""
    assert pred(hiK, w, strict, N_exp) is True, "上端不是 True"
    assert pred(loK, w, strict, N_exp) is False, "下端不是 False"
    a, b = loK, hiK
    while b - a > 1:
        mid = (a + b) // 2
        if pred(mid, w, strict, N_exp) is False:
            a = mid
        else:
            b = mid
    assert pred(a, w, strict, N_exp) is False
    return a

# 阈值（精确有理）
W110  = F(110, 10 ** 45)
W1105 = F(1105, 10 ** 46)
W111  = F(111, 10 ** 45)
W1115 = F(1115, 10 ** 46)
W112  = F(112, 10 ** 45)

K205 = 205000000000000000000
KSTAR = 205632218873398596256
K206 = 206000000000000000000
K207 = 207000000000000000000

# ================================================================ 输出
say("=" * 80)
say("r3_logdomain.py  路线 3：对数域解析判据    Python %s" % sys.version.split()[0])
say("判据只用 fractions.Fraction 与 int；无 mpmath、无浮点判定；常数一律向外取整到 1e-%d" % P)
say("=" * 80)

say("\n[S1] 常数（严格有理区间）")
say("  ln 2        = %s   宽 %.1e" % (iv_dec(LN2), float(LN2[1] - LN2[0])))
say("  ln 3        = %s   宽 %.1e" % (iv_dec(LN3), float(LN3[1] - LN3[0])))
say("  ln ln 2     = %s" % iv_dec(LN_LN2))
say("  delta       = %s   宽 %.1e" % (iv_dec(DELTA), float(DELTA[1] - DELTA[0])))
say("  delta^91    = %s" % iv_dec(D91, 20))
say("  D=delta^91-1= %s" % iv_dec(D, 20))
say("  A=ln3-ln2   = %s" % iv_dec(A))
say("  A/D         = %s   宽 %.1e" % (iv_dec(AD, 25), float(AD[1] - AD[0])))
say("  A/D 检验：K*(A/D) = t(K*) = v ln2 = %s" % dec(F(KSTAR) * ADM, 20))
say("  弹性 1+K(A/D)（K=2.06e20）= %s" % dec(1 + F(K206) * ADM, 20))
say("  弹性 1+K(A/D)（K=K*）    = %s" % dec(1 + F(KSTAR) * ADM, 20))

say("\n[S2] 三处记录值（转抄自 cycle-2/route-5.md:217 至 :219）与 E 区间的包含判定")
REC = {
    K205:  ("1.44921627253094092e-43",  F(144921627253094092, 10 ** 60)),
    KSTAR: ("1.22979157996235308e-43",  F(122979157996235308, 10 ** 60)),
    K206:  ("1.11777663068838816e-43",  F(111777663068838816, 10 ** 60)),
}
for K in (K205, KSTAR, K206):
    (p, q), R_hi, eps = ln1E_bounds(K)
    say("  K = %d" % K)
    say("     ln(1/E) in %s" % iv_dec((p, q), 20))
    say("     R 上界 = %s   2^{-v} 上界 = %s   合计余项 = %s" % (
        dec(R_hi, 12), dec(eps, 12), dec(R_hi + 2 * eps, 12)))
    say("     t = v ln2 in %s   v in %s" % (
        iv_dec((F(K) * AD[0], F(K) * AD[1]), 15),
        iv_dec((F(K) * AD[0] / LN2[1], F(K) * AD[1] / LN2[0]), 15)))
    Eiv = round_out((1 / exp_bounds(q, 400)[1], 1 / exp_lower(p, 400)), 40)
    nm, rec = REC[K]
    say("     E in %s" % iv_dec(Eiv, 20))
    say("     记录值 %s 落在区间内 = %s" % (nm, Eiv[0] <= rec <= Eiv[1]))

say("\n[S3] 三条目标判定的严格证书（对数域区间比较；True/False 均为已证）")
targets = [
    ("U1  E(K*) > 1.12e-43      （10.8% 差的否证面）", KSTAR, W112, False),
    ("U2  E(2.05e20) > 1.12e-43 （30.6% 差的否证面）", K205, W112, False),
    ("U3a E(2.06e20) < 1.12e-43 （窗口右端）", K206, W112, True),
    ("U3b E(2.06e20) >= 1.11e-43（窗口左端）", K206, W111, False),
    ("U4  E(K*) > 1.11e-43", KSTAR, W111, False),
    ("U5  E(2.07e20) < 1.10e-43 （窗口外右侧）", K207, W110, True),
]
for label, K, w, strict in targets:
    r = pred(K, w, strict)
    p, q = ln1E_bounds(K)[0]
    lw = ln1w_bounds(w)
    margin = (p - lw[1]) if strict else (q - lw[0])
    say("  %-44s -> %s  对数域余量 %s" % (label, r, dec(margin, 12)))
say("  注：对数域余量 = 离阈值最近的区间端点之差（正=留有余量，负=方向相反）")

say("\n[S4] 两条可手算不等式：三段分解（锚点 K0 = 2.06e20）")
(p0, q0), R0_hi, eps0 = ln1E_bounds(K206)
lw111 = ln1w_bounds(W111)
THETA_HI = R0_hi + 4 * eps0
say("  余项界 Theta <= R(K0) + 4*2^{-v(K0)} = %s" % dec(THETA_HI, 12))
say("  锚点项 ln(1/E(K0)) - ln(10^43/1.11) in %s" % iv_dec((p0 - lw111[1], q0 - lw111[0]), 20))
for K in (K205, KSTAR):
    say("  --- K = %d  ---" % K)
    (p, q), R_hi, eps = ln1E_bounds(K)
    A_lo, A_hi = p - lw111[1], q - lw111[0]
    say("     路线 A（直接）：ln(E(K)/1.11e-43) in %s" % iv_dec((A_lo, A_hi), 20))
    say("                    比值 E(K)/(1.11e-43) in %s" % iv_dec(
        round_out((exp_bounds(A_lo, 200)[0], exp_bounds(A_hi, 200)[1]), 40), 20))
    lnratio = ln_bounds(F(K206, K), 100)
    dK = K206 - K
    B_lo = lnratio[0] + F(dK) * AD[0] - THETA_HI + (p0 - lw111[1])
    B_hi = lnratio[1] + F(dK) * AD[1] + (q0 - lw111[0])
    say("     路线 B（弹性三段）：ln(K0/K) in %s" % iv_dec(lnratio, 20))
    say("                        (K0-K)*A/D in %s   (K0-K = %d)" % (
        iv_dec((F(dK) * AD[0], F(dK) * AD[1]), 20), dK))
    say("                        比值 in %s" % iv_dec(
        round_out((exp_bounds(B_lo, 200)[0], exp_bounds(B_hi, 200)[1]), 40), 20))
    say("     两路区间相交 = %s" % (not (B_hi < A_lo or B_lo > A_hi)))

say("\n[S5] 三种印刷读法下「印成 1.11」的整数 K 窗口（两向搜索，皆带证书）")
say("  约定：截尾 [1.11,1.12)*1e-43；四舍 [1.105,1.115)*1e-43；上取 (1.10,1.11]*1e-43")
def window(name, w_lo, w_hi, strict_lo, loK=2 * 10 ** 20, hiK=3 * 10 ** 20):
    if strict_lo:
        kmax_core = search_false(w_lo, False, loK, hiK)
        kmax_out  = search_true(w_lo, False, loK, hiK) - 1
    else:
        kmax_core = search_false(w_lo, True, loK, hiK)
        kmax_out  = search_true(w_lo, True, loK, hiK) - 1
    kmin_core = search_true(w_hi, True, loK, hiK)
    kmin_out  = search_false(w_hi, True, loK, hiK) + 1
    say("  %s" % name)
    say("     必在窗口内的整数区间 [%d , %d]   宽 %d" % (kmin_core, kmax_core, kmax_core - kmin_core + 1))
    say("     可能在窗口内的整数区间 [%d , %d]（补集必在窗口外）" % (kmin_out, kmax_out))
    wmode = False if strict_lo else True      # 窗口下界一侧的判定式：上取用 E<=w_lo
    say("     证书：pred(%d, E<w_hi)=%s ; pred(%d, E<w_hi)=%s" % (
        kmin_core, pred(kmin_core, w_hi, True), kmin_core - 1, pred(kmin_core - 1, w_hi, True)))
    say("           pred(%d, E%s w_lo)=%s ; pred(%d, E%s w_lo)=%s" % (
        kmax_core + 1, "<=" if not wmode else "<", pred(kmax_core + 1, w_lo, wmode),
        kmax_core, "<=" if not wmode else "<", pred(kmax_core, w_lo, wmode)))
    return (kmin_core, kmax_core), (kmin_out, kmax_out)

T1 = window("截尾到两位小数（须 1.11e-43 <= E < 1.12e-43）", W111, W112, False)
T2 = window("四舍五入到两位小数（须 1.105e-43 <= E < 1.115e-43）", W1105, W1115, False)
T3 = window("向上取整到两位小数（须 1.10e-43 < E <= 1.11e-43）", W110, W111, True)

say("\n  成员判定（用「必在窗口内」与「必在窗口外」两栏合判）")
for K, nm in ((KSTAR, "K*=第六步精确值"), (K205, "2.05e20（论文印数）"), (K206, "2.06e20（三位四舍五入）"), (K207, "2.07e20")):
    st = []
    for (core, outer), wn in ((T1[0], "截尾"), (T2[0], "四舍"), (T3[0], "上取")):
        inside = core[0] <= K <= core[1]
        outside = not (outer[0] <= K <= outer[1])
        st.append("%s:%s" % (wn, "必在内" if inside else ("必在外" if outside else "未决(窄带内)")))
    say("     %-24s %s" % (nm, "  ".join(st)))

say("\n[S6] 端点逐点证书（两端各给一个点，含其相邻整数）")
def endpoint_cert(name, K, w_lo, w_hi, strict_lo):
    wmode = False if strict_lo else True
    say("  %s：K = %d" % (name, K))
    say("     E(K) <  w_hi : %s" % pred(K, w_hi, True))
    say("     E(K-1)>= w_hi : %s" % (not pred(K - 1, w_hi, True)))
    say("     E(K) %s w_lo : %s" % (">" if strict_lo else ">=", not pred(K, w_lo, wmode)))
    say("     E(K+1)%s w_lo : %s" % ("<=" if strict_lo else "<", pred(K + 1, w_lo, wmode)))
endpoint_cert("截尾窗口左端（最小可印成 1.11 者）", T1[0][0], W111, W112, False)
endpoint_cert("截尾窗口右端（最大可印成 1.11 者）", T1[0][1], W111, W112, False)
endpoint_cert("四舍窗口左端", T2[0][0], W1105, W1115, False)
endpoint_cert("四舍窗口右端", T2[0][1], W1105, W1115, False)
endpoint_cert("上取窗口左端", T3[0][0], W110, W111, True)
endpoint_cert("上取窗口右端", T3[0][1], W110, W111, True)

say("\n[S7] 归因量化：把 E 移入窗口需要多大的中间量改动（区间比较）")
need = ln1w_bounds(W112)[0] - ln1E_bounds(KSTAR)[0][1]
say("  K* 处 ln(1/E) 距 1.12e-43 门槛还差（需增加）%s" % dec(need, 12))
dln1E_dK = F(1, KSTAR) + ADM
dK_need = need / dln1E_dK
say("  d ln(1/E)/dK = 1/K + A/D = %s ；因此 K 需增加 >= %s（相对 %s）" % (
    dec(dln1E_dK, 12), dec(dK_need, 12), dec(dK_need / KSTAR, 12)))
say("     即 K 需 >= %s" % dec(F(KSTAR) + dK_need, 20))
t_mid = F(KSTAR) * ADM
dln1E_ddelta = -(t_mid * F(M91) / DELM) * ((D91[0] + D91[1]) / 2) / ((D[0] + D[1]) / 2)
say("  d ln(1/E)/ddelta 主项 = -t*m2/delta*(delta^m2/(delta^m2-1)) ~ %s" % dec(dln1E_ddelta, 12))
say("     若只改 delta：需 delta 减小 ~ %s（相对 %s）" % (
    dec(need / (-dln1E_ddelta), 12), dec(need / (-dln1E_ddelta) / DELM, 12)))
say("     参考：delta 中值 = %s" % dec(DELM, 20))
for dname, dv in (("1.585", F(1585, 1000)), ("1.5849", F(15849, 10000)), ("1.58496", F(158496, 100000))):
    dln = (dv - DELM) * dln1E_ddelta
    say("       delta -> %s：ln(1/E) 变动 %s ；E 的乘子 ~ %s" % (
        dname, dec(dln, 12), dec(1 + dln, 12)))

say("\n[S8] 自洽检查")
say("  v(K*)   = %s" % dec(F(KSTAR) * ADM / LN2M, 20))
say("  v(2.06e20) = %s" % dec(F(K206) * ADM / LN2M, 20))
say("  K* = %d ；三位有效数字之截断 = %d e18 ；四舍五入 = %d e18" % (
    KSTAR, KSTAR // 10 ** 18, (KSTAR + 5 * 10 ** 17) // 10 ** 18))
say("  可行性：m2=91 需 K >= (delta^91-1)/(delta-1) * log2((162/97)*X0), X0 = 695*2^60")
c_lo = ln_bounds(F(162 * 695 * 2 ** 60, 97), 100)[0] / LN2[1]
c_hi = ln_bounds(F(162 * 695 * 2 ** 60, 97), 100)[1] / LN2[0]
say("     log2((162/97)X0) in [%s , %s]" % (dec(c_lo, 20), dec(c_hi, 20)))
say("     m2=91 门槛 in [%s , %s]" % (
    dec(D[0] / (DELTA[1] - 1) * c_lo, 20), dec(D[1] / (DELTA[0] - 1) * c_hi, 20)))
say("     K* > 门槛下界 = %s" % (F(KSTAR) > D[0] / (DELTA[1] - 1) * c_lo))
say("     m2=92 门槛 in [%s , %s]（应 > K*）" % (
    dec(D91[0] * DELTA[0] / (DELTA[1] - 1) * c_lo, 20), dec(D91[1] * DELTA[1] / (DELTA[0] - 1) * c_hi, 20)))

say("\n[S9] 展示对照（mpmath，仅展示，不参与任何判定）")
try:
    from mpmath import mp, mpf, log as mlog, power as mpower
    mp.dps = 60
    d_mp = mlog(3) / mlog(2)
    for K in (K205, KSTAR, K206):
        v_mp = mpf(K) * (d_mp - 1) / (mpower(d_mp, 91) - 1)
        E_mp = (1 / (mpf(K) * mlog(2) * (mpower(2, v_mp) - 1))) * (1 + 90 / mpower(mpower(2, v_mp) - 1, d_mp - 1))
        say("     K = %d : v = %s ; E = %s" % (K, mp.nstr(v_mp, 25), mp.nstr(E_mp, 25)))
except Exception as e:
    say("     mpmath 不可用：%s" % e)

say("\n[T] 用时 %.1f 秒；全部判据为精确有理比较" % (time.time() - T0))
resdir = pathlib.Path(__file__).resolve().parent / "results"
resdir.mkdir(parents=True, exist_ok=True)
(resdir / "r3_logdomain.out").write_text("\n".join(OUT) + "\n")
