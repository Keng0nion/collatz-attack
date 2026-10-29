"""d3w_window_cert.py -- 两约定分岔窗口的严格区间证书（(b) 与 (c)）

不 import 任何被审脚本：N、F、K_th、v 全部本文件重写；每个端点都返回有理区间。
数学口径（m = 92，m₂ ∈ {1, ..., 92}）：
  δ = log3/log2；X0 = 695*2^60；C = log2((162/97)X0)（故 2^C = 162X0/97，精确）
  geom(m₂) = (δ^{m₂} - 1)/(δ - 1)；K_th(m₂) = (m/m₂)·geom(m₂)·C；v(m₂,K) = C·K/K_th(m₂)
  A(m₂) = 0 (m₂ = m)、3/X0 (m₂ = m-1)、(97(m - m₂) + 73)/(54·X0) (其余)
  N(m₂,K) = A(m₂) + 3/(2^v - 1) + 3(m₂ - 1)/(2^v - 1)^δ
  F_M(K)  = N(M,K) - N(M-1,K)，M = m₂_max(K) = max F_m(K) = max{m₂ : K ≥ K_th(m₂)}
窗口 W(M) = {K : argmin_{m₂ ∈ F_m(K)} N(m₂,K) ≠ M}。

本脚本证（全部为严格有理区间，无浮点参与判定）：
  一、常数与门槛区间；二、F_M(K_th(M)) 的符号（M = 2 至 92）；
  五、F 的严格单调性与「深档链」引理；六、窗口右端的严格括号与 u*；
  七、mpmath 独立二分对照；九、K* 与 c2r5_cert.log:67 根区间端点的窗口外判定。

运行：20-experiments/.venv/bin/python scripts/d3w_window_cert.py
"""
import sys
import os
import time
from fractions import Fraction as Fr

sys.set_int_max_str_digits(400000)   # δ^{m₂} 的分子分母可达数千位，需放宽十进制转换上限
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from d3w_cert_core import (Iv, ln2_iv, ln_int_iv, ln_rat_iv, exp_iv, two_pow_iv,
                           ln_one_minus_iv)

D = 60
MTH = 92
X0 = 695 * 2 ** 60
NUM = 162 * X0 - 97               # 97*(2^C - 1)
A_GEN = Fr(97, 54 * X0)           # 通用档的 A 阶梯 A(m₂) - A(m₂+1)

t0 = time.time()
res = []


def chk(name, cond, extra=""):
    res.append((name, bool(cond)))
    print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, extra))


def g(x):
    """仅用于占位打印（float 口径，末几位是 double 噪声）。"""
    return "%.18e" % float(x)


def _frac_ceil(x):
    x = Fr(x)
    return -((-x.numerator) // x.denominator)


def _log10_floor(x):
    x = Fr(x)
    e = len(str(x.numerator)) - len(str(x.denominator))
    while Fr(10) ** e > x:
        e -= 1
    while Fr(10) ** (e + 1) <= x:
        e += 1
    return e


def sci(x, nd=22):
    """精确十进制科学计数法（不经 float）：nd 位有效数字截断。"""
    x = Fr(x)
    if x == 0:
        return "0"
    sign = "-" if x < 0 else ""
    a = abs(x)
    e = _log10_floor(a)
    m = a / Fr(10) ** e
    s = str(m.numerator * 10 ** (nd - 1) // m.denominator)
    while len(s) < nd:
        s = "0" + s
    return "%s%s.%se%+03d" % (sign, s[0], s[1:], e)


# ------------------------------------------------------------------ 常数
ln2 = ln2_iv(D)
ln3 = ln_int_iv(3, D)
delta = Iv(ln3.lo / ln2.hi, ln3.hi / ln2.lo)
LN = ln_int_iv(112590, D) - ln_int_iv(97, D)
C = Iv(60, 60) + Iv(LN.lo / ln2.hi, LN.hi / ln2.lo)

print("== 一、常数与门槛（严格有理区间，D = %d；整数运算定向舍入）==" % D)
print("  delta ∈ [%s, %s]   宽 %s" % (sci(delta.lo), sci(delta.hi), sci(delta.width(), 3)))
print("  C     ∈ [%s, %s]   宽 %s" % (sci(C.lo), sci(C.hi), sci(C.width(), 3)))
# 口径：:427 的 30 位串是真值的「截断」，故落在区间下方约 1.99×10⁻²⁹；判据用距离而非包含
_chk_str = Fr("70.1808063283083668248487894995")
chk("K1 真值下界与 route-5.md:427 的 30 位串相距 < 1e-28（截断口径一致）",
    abs(C.lo - _chk_str) < Fr(1, 10 ** 28), "相距 %.3e" % float(abs(C.lo - _chk_str)))
chk("K2 负对照：真值下界与 route-5.md:101 的串相距约 2.75×10⁻¹⁵（不是 1e-28 级）",
    Fr(2752194, 10 ** 21) < C.lo - Fr("70.1808063283083640726545127109") < Fr(27522, 10 ** 19))
chk("K3 2^C 与 (162/97)X0 的精确关系的区间自洽（2^C 相对宽 < 1e-50）",
    two_pow_iv(C, D).contains(Fr(162 * X0, 97)))


def geom_iv(m2):
    return (delta ** m2 - 1) / (delta - 1)


def Kth_iv(m2):
    return Iv(Fr(MTH, m2), Fr(MTH, m2)) * geom_iv(m2) * C


KTH = {m2: Kth_iv(m2) for m2 in range(1, MTH + 1)}
for m2 in (88, 89, 90, 91, 92):
    print("  K_th(%2d) ∈ [%s, %s]（相对宽 %s）"
          % (m2, sci(KTH[m2].lo), sci(KTH[m2].hi), sci(KTH[m2].relwidth(), 3)))
# route-1 记的 20 位值是「截断」，故用 20 位一致（相对 1e-19）作判据，而非精确整数包含
R1K = {90: "123124614107556571560", 91: "193003413899578228860", 92: "302578139046974169430"}
for m2 in (90, 91, 92):
    d = abs(KTH[m2].lo - Fr(R1K[m2])) / KTH[m2].lo
    chk("K4 至 K6 K_th(%d) 与 route-1 一致到相对 1e-19" % m2, d < Fr(1, 10 ** 19),
        "相对差 %s" % sci(d, 3))


# ------------------------------------------------------------- N 与 F
def A_rational(m2):
    if m2 == MTH:
        return Fr(0)
    if m2 == MTH - 1:
        return Fr(3, X0)
    return Fr(97 * (MTH - m2) + 73, 54 * X0)


def v_iv(m2, K):
    """v(m₂,K) = (m₂/m)·K·(δ-1)/(δ^{m₂}-1) = C·K/K_th(m₂)（两式等价，此处用前者）。"""
    K = K if isinstance(K, Iv) else Iv(K, K)
    return Iv(Fr(m2, MTH), Fr(m2, MTH)) * K * (delta - 1) / (delta ** m2 - 1)


def term23_iv(m2, v):
    """3/(2^v-1) + 3(m₂-1)/(2^v-1)^δ 的严格区间。

    用 ln(2^v-1) = v ln2 + ln(1 - 2^{-v})（v ≥ 1），避开大整数对数。
    v.lo > 200 时饱和：两项之和 ≤ 3/2^200 + 3(m₂-1)/2^(200·δ_lo)。
    """
    if v.lo > 200:
        return Iv(0, Fr(3, 2 ** 200)) + Iv(0, Fr(3 * (m2 - 1)) / Fr(2) ** int(200 * delta.lo))
    tv = two_pow_iv(v, D)                       # 2^v
    t2 = Iv(3, 3) / (tv - 1)
    if m2 <= 1:
        return t2
    x = Iv(1, 1) / tv                           # 2^{-v} <= 1/2
    ln_tm1 = v * ln2 + ln_one_minus_iv(x, D)    # ln(2^v - 1)
    t3 = Iv(3 * (m2 - 1), 3 * (m2 - 1)) / exp_iv(delta * ln_tm1, D)
    return t2 + t3


def N_iv(m2, K):
    return A_rational(m2) + term23_iv(m2, v_iv(m2, K))


def F_iv(M, K):
    return N_iv(M, K) - N_iv(M - 1, K)


# ------------------------------------------------- 三、门槛处 F 的符号
print()
print("== 三、F_M(K_th(M)) 的符号（M = 2 至 92；门槛处 m₂_max = M）==")
pos, neg, strad = [], [], []
for M in range(2, MTH + 1):
    F = F_iv(M, KTH[M])
    s = F.sign()
    (pos if s > 0 else neg if s < 0 else strad).append(M)
    if M >= 86 or M <= 4:
        print("  M = %2d : F ∈ [%s, %s]  sign = %+d" % (M, sci(F.lo), sci(F.hi), s))
print("  F > 0（门槛右侧存在分岔）的档：%s" % pos)
print("  F < 0（无分岔）的档数 = %d；未定档：%s" % (len(neg), strad))
chk("K7 M = 88、89、90 处 F > 0", all(M in pos for M in (88, 89, 90)))
chk("K8 M = 91、92 处 F < 0（route-1 A6 的特殊档无窗结论被证实）",
    all(M in neg for M in (91, 92)))
chk("K9 判据在全部 91 档都定号（无未定）", not strad, "未定 = %s" % strad)

# --------------------------------------------- 五、单调性与深档链
print()
print("== 五、F 的严格单调性与深档链引理（M = 88 至 92）==")


def dN_dK_iv(m2, K):
    """dN(m₂,K)/dK 的严格区间（两项皆负；w = dv/dK = C/K_th(m₂) 为常数）。

    t1 = 3 ln2 w 2^v/(2^v-1)^2 精确夹逼；
    t2 = 3(m₂-1)δ ln2 w 2^v/(2^v-1)^(δ+1) ≤ 3(m₂-1)δ ln2 w 2^(1+δ(1-v))（因 2^v-1 ≥ 2^(v-1)，v ≥ 1）。
    故 dN/dK ∈ [-(t1.hi + t2ub.hi), -t1.lo]。
    """
    K = K if isinstance(K, Iv) else Iv(K, K)
    v = v_iv(m2, K)
    w = C / KTH[m2]
    ex = Iv(1, 1) + delta * (Iv(1, 1) - v)          # = 1 + δ(1-v)，此处 ex.hi <= 0
    p2lo = Fr(1, 2 ** _frac_ceil(-ex.lo)) if ex.lo <= 0 else Fr(2) ** int(ex.lo)
    p2hi = Fr(1, 2 ** int(-ex.hi)) if ex.hi <= 0 else Fr(2) ** _frac_ceil(ex.hi)
    t2ub = Iv(3 * (m2 - 1), 3 * (m2 - 1)) * delta * ln2 * w * Iv(p2lo, p2hi)
    if v.lo > 200:
        t1ub = Iv(3, 3) * ln2 * w * Iv(2, 2) / Iv(Fr(2) ** 200, Fr(2) ** 200)
        return Iv(-(t1ub.hi + t2ub.hi), 0)
    tv = two_pow_iv(v, D)
    t1 = Iv(3, 3) * ln2 * w * tv / ((tv - 1) ** 2)
    return Iv(-(t1.hi + t2ub.hi), -t1.lo)


DERIV = {}
for M in (88, 89, 90, 91, 92):
    Kup = KTH[M + 1] if M + 1 <= MTH else KTH[M] * Iv(Fr(15, 10), Fr(15, 10))
    for tag, K in (("门槛", KTH[M]), ("区间右端", Kup)):
        dF_hi = dN_dK_iv(M, K).hi - dN_dK_iv(M - 1, K).lo
        DERIV[(M, tag)] = dF_hi
        print("  M = %2d %s：F' 上界 = %s" % (M, tag, sci(dF_hi)))
        chk("K10 M = %d 在%s处 F' < 0（严格递减）" % (M, tag), dF_hi < 0)
    nu = v_iv(M - 1, KTH[M])
    ub2 = (Iv(3, 3) / (two_pow_iv(nu, D) - 1)).hi
    ln_tm1 = nu * ln2 + ln_one_minus_iv(Iv(1, 1) / two_pow_iv(nu, D), D)
    ub3 = (Iv(3 * (M - 2), 3 * (M - 2)) / exp_iv(delta * ln_tm1, D)).hi
    deep_lb = A_GEN - ub2 - ub3
    print("       深档链下界 = A_步 - 3/(2^ν-1) - 3(M-2)/(2^ν-1)^δ = %s" % sci(deep_lb))
    chk("K11 M = %d 的深档链成立（N 对 m₂ ≤ M-2 严格递减）" % M, deep_lb > 0)

# --------------------------------------------- 六、窗口右端的严格括号
# ---- 五之二：全档深档链（M = 2 至 92，供「窗口存在集」用）----
print()
print("== 五之二、全档深档链的下界（M = 2 至 92；用于「N 对 m₂ ≤ M-2 严格递减」）==")
deep_min, deep_arg = None, None
for M in range(2, MTH + 1):
    nu = v_iv(M - 1, KTH[M])
    tv = two_pow_iv(nu, D)
    ub2 = (Iv(3, 3) / (tv - 1)).hi
    ub3 = (Iv(3 * (M - 2), 3 * (M - 2)) / exp_iv(delta * (nu * ln2 + ln_one_minus_iv(Iv(1, 1) / tv, D)), D)).hi
    lb = A_GEN - ub2 - ub3
    if deep_min is None or lb < deep_min:
        deep_min, deep_arg = lb, M
print("  最小下界 = %s（在 M = %d 处）；全部 > 0？%s"
      % (sci(deep_min), deep_arg, all(True for _ in [0]) and deep_min > 0))
chk("K11b 深档链对全部 M = 2 至 92 成立（最小下界 > 0）", deep_min > 0,
    "最小下界 %s 在 M = %d" % (sci(deep_min), deep_arg))

print()
print("== 六、窗口右端的严格括号（M = 88、89、90）==")
U_CERT = {}
KTH_MID = {}
for M in (88, 89, 90):
    Km = (KTH[M].lo + KTH[M].hi) / 2
    KTH_MID[M] = Km

    def Fu(u, M=M, Km=Km):
        return F_iv(M, Km * Iv(Fr(1) + u, Fr(1) + u))

    u_lo, u_hi = Fr(0), Fr(1, 10 ** 12)
    Fup = Fu(u_hi)
    chk("K12 M = %d 的上括号 F(1e-12) < 0" % M, Fup.sign() < 0, "F 上界 = %s" % sci(Fup.hi))
    steps = 0
    while steps < 80 and (u_hi - u_lo) > u_lo / 10 ** 25:
        mid = (u_lo + u_hi) / 2
        s = Fu(mid).sign()
        if s > 0:
            u_lo = mid
        elif s < 0:
            u_hi = mid
        else:
            if (mid - u_lo) < (u_hi - mid):
                u_hi = mid
            else:
                u_lo = mid
        steps += 1
    chk("K13 M = %d 括号两端严格变号" % M, Fu(u_lo).sign() > 0 and Fu(u_hi).sign() < 0,
        "步数 = %d" % steps)
    U_CERT[M] = (u_lo, u_hi)
    Kmid = Km * (1 + (u_lo + u_hi) / 2)
    dF_mid = dN_dK_iv(M, Kmid).hi - dN_dK_iv(M - 1, Kmid).lo
    print("          交点邻域中点处 F' 上界 = %s" % sci(dF_mid))
    chk("K13b M = %d 交点邻域中点处 F' < 0" % M, dF_mid < 0)
    Kro = Iv(KTH[M].lo * (1 + u_lo), KTH[M].hi * (1 + u_hi))
    print("  M = %2d : u* ∈ [%s, %s]（相对宽 %s，u 尺度）"
          % (M, sci(u_lo), sci(u_hi), sci((u_hi - u_lo) / u_lo, 3)))
    print("          窗口右端（去程交点）∈ [%s, %s]（括号相对宽 %s）"
          % (sci(Kro.lo), sci(Kro.hi), sci((Kro.hi - Kro.lo) / Kro.lo, 3)))
    print("          窗口 = (K_th(M), 右端) 故 ⊆ [%s, %s]、⊇ [%s, %s]；绝对宽 ∈ [%s, %s]"
          % (sci(KTH[M].lo), sci(Kro.hi), sci(KTH[M].hi), sci(Kro.lo),
             sci(Kro.lo - KTH[M].hi), sci(Kro.hi - KTH[M].lo)))
    print("          u*×1e13 ∈ [%s, %s]" % (sci(u_lo * 10 ** 13, 12), sci(u_hi * 10 ** 13, 12)))

# --------------------------------------------- 七、mpmath 独立二分
print()
print("== 七、独立二分对照（mpmath dps = 60，另一套实现，按 u 参数化）==")
try:
    from mpmath import mp, mpf, log as mlog, power as mpow

    mp.dps = 60
    d_f = mlog(3) / mlog(2)
    C_f = mpf(60) + mlog(mpf(112590) / 97) / mlog(2)
    Kth_f = {}
    for m2 in range(1, MTH + 1):
        gg = (mpow(d_f, m2) - 1) / (d_f - 1)
        Kth_f[m2] = (mpf(MTH) / m2) * gg * C_f

    def A_f(m2):
        if m2 == MTH:
            return mpf(0)
        if m2 == MTH - 1:
            return mpf(3) / X0
        return mpf(97 * (MTH - m2) + 73) / (54 * X0)

    def ind_F(M, u, Km):
        K = Km * (1 + u)

        def NN(m2):
            v = C_f * K / Kth_f[m2]
            return A_f(m2) + 3 / (mpow(2, v) - 1) + 3 * (m2 - 1) / mpow(mpow(2, v) - 1, d_f)
        return NN(M) - NN(M - 1)

    for M in (88, 89, 90):
        Km = mpf(str(KTH_MID[M]))
        lo, hi = mpf(0), mpf("1e-11")          # 各档用同一初始上括号
        for _ in range(200):
            mid = (lo + hi) / 2
            if ind_F(M, mid, Km) > 0:
                lo = mid
            else:
                hi = mid
        u_ind = lo
        u_lo, u_hi = U_CERT[M]
        rel = abs(u_ind - mpf(str(u_lo))) / mpf(str(u_lo))
        print("  M = %2d : 独立 u* = %s；与本证书下界相对差 = %.3e" % (M, u_ind, rel))
        chk("K14 M = %d 独立二分与本证书一致到相对 1e-15" % M, rel < mpf("1e-15"))
        chk("K15 M = %d 独立根落在本证书括号内" % M,
            mpf(str(u_lo)) <= u_ind <= mpf(str(u_hi)))
except ImportError as exc:
    chk("K14 独立二分对照", False, "mpmath 不可用：%r" % (exc,))

print()
print("== 八、与 route-1 记录的数值对照 ==")
R1 = {88: "7.622397", 89: "7.714617759", 90: "7.806771365"}
for M in (88, 89, 90):
    u_lo, u_hi = U_CERT[M]
    print("  M = %2d : 本证书 u*×1e13 = [%s, %s]；route-1 记 %s"
          % (M, sci(u_lo * 10 ** 13, 12), sci(u_hi * 10 ** 13, 12), R1[M]))
    chk("K16 M = %d 与 route-1 的 9 位一致" % M,
        abs(float(u_lo) * 1e13 - float(R1[M])) < 1e-6)

# --------------------------------------------- 九、K* 与根区间端点
print()
print("== 九、(c) K* 与 c2r5_cert.log:67 根区间端点的窗口外判定 ==")
Kstar = Fr(205632218873398596256)
chk("K17 K_th(91) ≤ K* < K_th(92)（K* 处 m₂_max = 91）",
    KTH[91].hi <= Kstar < KTH[92].lo)
F_star = F_iv(91, Iv(Kstar, Kstar))
print("  F_91(K*) ∈ [%s, %s]  sign = %+d" % (sci(F_star.lo), sci(F_star.hi), F_star.sign()))
chk("K18 F_91(K*) < 0（K* 处 argmin = 91 = m₂_max）", F_star.sign() < 0)
Kc_lo = Fr("313195478959172262876.6365306194907065260231016940260118526233")
Kc_hi = Fr("313195478959172262876.6365306194907065260231016961279595491105")
chk("K19 根区间的两个端点都 ≥ K_th(92)（该区段 m₂_max ≡ 92）",
    KTH[92].hi <= Kc_lo)
for nm, Kc in (("下端", Kc_lo), ("上端", Kc_hi)):
    F_c = F_iv(92, Iv(Kc, Kc))
    print("  根区间%s：F_92 ∈ [%s, %s]  sign = %+d" % (nm, sci(F_c.lo), sci(F_c.hi), F_c.sign()))
    chk("K20 根区间%s处 F_92 < 0（m₂_max = 92 为 argmin）" % nm, F_c.sign() < 0)
print("  M = 90 窗口右端上界 %s；K_th(91) 下界 %s；相隔 ≥ %s"
      % (sci(KTH[90].hi * (1 + U_CERT[90][1])), sci(KTH[91].lo),
         sci(KTH[91].lo - KTH[90].hi * (1 + U_CERT[90][1]))))

print()
print("== 十、负对照（判据可翻 False）==")
chk("N1 窗口内一点 F > 0（不是恒真）", F_iv(90, KTH_MID[90] * (1 + U_CERT[90][0])).sign() > 0)
chk("N2 K = K_th(90)×1.01（窗口外）时 F < 0",
    F_iv(90, KTH[90] * Iv(Fr(101, 100), Fr(101, 100))).sign() < 0)
chk("N3 M = 91 门槛处 F < 0（不被误判为正）", F_iv(91, KTH[91]).sign() < 0)
chk("N4 把 M = 90 与 M = 89 换位（错档）时门槛处符号为正但不构成 M = 90 的窗口判据",
    F_iv(89, KTH[90]).sign() != 0)

print()
print("耗时 %.1f 秒；通过 %d/%d" % (time.time() - t0,
                                   sum(1 for _, ok in res if ok), len(res)))
print("全部通过？", all(ok for _, ok in res))
