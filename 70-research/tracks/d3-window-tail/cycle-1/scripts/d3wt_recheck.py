# -*- coding: utf-8 -*-
"""d3-window-tail 第 1 轮 route-4：对前版两条否证的独立复核（自写脚本，抽点重算）。

(A) C 的 float64 伪值判定：自写精确有理级数算 C，与 route-5.md:101 的十进制串、
    与 float64(log2((162/97)X0)) 的精确二进制值三方对照。
(B) 第三项与「两顶残差」之比（10.72 个数量级）的自写复算。
(C) 窗口：route-5 机制式（1.07806938779e-21 与 1.5e-22 两种输入）、真值（二分），
    以及二者之比与 T3new/P1 的一致性。

口径（与 cycle-2/scripts/c2r5_rig.py 的 A_of / v_exact 一致）：
  m = 92；X0 = 695*2^60；delta = log 3/log 2；C = log2((162/97)X0)；
  v(j,K) = (j/92)*K*(delta-1)/(delta^j - 1)；
  A(j) = 0 (j=92)、3/X0 (j=91)、(97*(92-j)+73)/(54*X0) (其余)；
  num(j,K) = A(j) + 3/(2^v - 1) + 3*(j-1)/(2^v - 1)^delta；G_M(K) = num(M,K) - num(M-1,K)。
不 import c2r5_rig.py，也不 import 本项目任何浮点路径；mpmath 只用于交叉对照。
"""
import math
from fractions import Fraction as F
from decimal import Decimal

import mpmath as mp

mp.mp.dps = 80
X0 = 695 * 2 ** 60
MM = 92
P = lambda *a: print(*a)


def dec(fr, n):
    """有理数的 n 位十进制显示（仅显示用）。"""
    return mp.nstr(mp.mpf(fr.numerator) / mp.mpf(fr.denominator), n)


# ---------------------------------------------------------------- 精确有理工具
def atanh_iv(s, N=70):
    """atanh(s) 的严格有理区间（0 <= s <= 1/3）。"""
    s2 = s * s
    tot = F(0)
    p = s
    for k in range(N):
        tot += p / (2 * k + 1)
        p *= s2
    tail = (p / (2 * N + 1)) / (1 - s2)
    return tot, tot + tail


def ln2_iv(N=70):
    lo, hi = atanh_iv(F(1, 3), N)
    return 2 * lo, 2 * hi


def ln_iv(y, N=70):
    """ln(y) 的严格有理区间，y > 0 有理。"""
    assert y > 0
    k = 0
    t = F(y)
    while t >= 2:
        t /= 2
        k += 1
    while t < 1:
        t *= 2
        k -= 1
    s = (t - 1) / (t + 1)
    assert 0 <= s <= F(1, 3)
    al, ah = atanh_iv(s, N)
    l2lo, l2hi = ln2_iv(N)
    if k >= 0:
        return 2 * al + k * l2lo, 2 * ah + k * l2hi
    return 2 * al + k * l2hi, 2 * ah + k * l2lo


def div_iv(a, b, c, d):
    """[a,b]/[c,d]，要求 0 < c <= d。"""
    v = [a / c, a / d, b / c, b / d]
    return min(v), max(v)


P("=" * 78)
P("[A] C 的真值与 route-5.md:101 的十进制串（本脚本自写精确有理级数）")
P("-" * 78)
Q = F(162, 97) * X0
assert Q == F(112590 * 2 ** 60, 97)
lnQlo, lnQhi = ln_iv(Q)
l2lo, l2hi = ln2_iv()
Clo, Chi = div_iv(lnQlo, lnQhi, l2lo, l2hi)
P("  自写 C 的严格有理区间宽度 = %s（对数量级 %s）"
  % (mp.nstr(mp.mpf(Chi.numerator) / Chi.denominator - mp.mpf(Clo.numerator) / Clo.denominator, 3),
     mp.nstr(mp.log10(mp.mpf(Chi.numerator) / Chi.denominator - mp.mpf(Clo.numerator) / Clo.denominator), 3)))
P("  C_lo = %s" % dec(Clo, 45))
P("  C_hi = %s" % dec(Chi, 45))
r5_101 = F(701808063283083640726545127109, 10 ** 28)
r5_427 = F(701808063283083668248487894995, 10 ** 28)
f64 = math.log2((162 / 97) * X0)
A_float = F(f64)
P("  route-5.md:101 串 = %s" % dec(r5_101, 30))
P("  route-5.md:427 串 = %s" % dec(r5_427, 30))
P("  float64(log2((162/97)X0)) 的精确二进制值 = %s" % Decimal(f64))
P("  该 float64 值 == route-5.md:101 串（精确有理比较）？%s" % (A_float == r5_101))
_n28 = F(f64) * 10 ** 28
P("  route-5.md:101 串 == float64 值四舍五入到 28 位小数？%s"
  % (r5_101 == F(round(_n28), 10 ** 28)))
P("  （该四舍五入的精确值 = %s）" % dec(F(round(_n28), 10 ** 28), 32))
d101 = abs(A_float - Clo) if A_float < Clo else abs(A_float - Chi)
P("  float64 值到 C 区间的精确距离 = %s" % dec(d101, 22))
P("  float64 值落在 C 区间内（严格有理比较）？%s" % (Clo <= A_float <= Chi))
P("  route-5.md:427 串落在 C 区间内？%s ；它与区间的精确距离 = %s"
  % (Clo <= r5_427 <= Chi, dec(abs(r5_427 - Clo) if r5_427 < Clo else abs(r5_427 - Chi), 22)))
P("  A_float - C_hi 的符号 = %s（说明 float64 落在 C 的下方）"
  % ("负" if A_float < Chi else "非负"))

P("")
P("=" * 78)
P("[B] 第三项与两顶残差之比（mpmath dps=60 交叉对照）")
P("-" * 78)
mp.mp.dps = 60
delta = mp.log(3) / mp.log(2)
Cm = 60 + mp.log(mp.mpf(112590) / 97) / mp.log(2)
twoC = mp.exp(Cm * mp.log(2))
P("  mpmath 的 C（45 位）= %s" % mp.nstr(Cm, 45))
_Clo_m = mp.mpf(Clo.numerator) / mp.mpf(Clo.denominator)
_Chi_m = mp.mpf(Chi.numerator) / mp.mpf(Chi.denominator)
P("  自写 C 区间含 mpmath 的 60 位 C ？（数值交叉对照）%s" % (_Clo_m <= Cm <= _Chi_m))
P("  mpmath C - 自写 C_lo = %s ；C_hi - 自写 C_hi = %s"
  % (mp.nstr(Cm - _Clo_m, 6), mp.nstr(Cm - _Chi_m, 6)))
D1 = 3 / (twoC - 1) - mp.mpf(97) / (54 * X0)
P("  3/(2^C-1) = %s" % mp.nstr(3 / (twoC - 1), 26))
P("  97/(54X0)  = %s" % mp.nstr(mp.mpf(97) / (54 * X0), 26))
P("  两顶残差 P1 = 3/(2^C-1) - 97/(54X0) = %s" % mp.nstr(D1, 22))
geomC = (twoC - 1) ** delta
P("  (2^C-1)^delta = %s" % mp.nstr(geomC, 22))
for j in (88, 89, 90):
    t3 = 3 * (j - 1) / geomC
    P("  T3new(j=%d) = %s   T3new/P1 = %s   log10 = %s"
      % (j, mp.nstr(t3, 22), mp.nstr(t3 / D1, 9), mp.nstr(mp.log10(t3 / D1), 9)))

P("")
P("=" * 78)
P("[C] 窗口：真值（二分）与 route-5 机制式")
P("-" * 78)


def A_of(j):
    if j == MM:
        return mp.mpf(0)
    if j == MM - 1:
        return mp.mpf(3) / X0
    return mp.mpf(97 * (MM - j) + 73) / (54 * X0)


def v_of(j, K):
    return (mp.mpf(j) / MM) * K * (delta - 1) / (delta ** j - 1)


def num_of(j, K):
    v = v_of(j, K)
    t = mp.exp(v * mp.log(2)) - 1
    return A_of(j) + 3 / t + 3 * (j - 1) / t ** delta


def K_thresh(j):
    return (mp.mpf(MM) / j) * ((delta ** j - 1) / (delta - 1)) * Cm


P("  log2(1 + 2^-C) = %s   ← route-5.md:230 写 1.5e-22"
  % mp.nstr(mp.log(1 + mp.exp(-Cm * mp.log(2))) / mp.log(2), 22))
P("  97/(162*X0)    = %s   ← route-5.md:229 写 ~7.4e-22"
  % mp.nstr(mp.mpf(97) / (162 * X0), 22))
P("")
P("  M | rho_M | K_thresh(M) | u_true | G_M(K_thresh) | u_true/u_mech | u_true/(1.5e-22/C)")
for j in (88, 89, 90):
    Kt = K_thresh(j)
    rho = v_of(j - 1, Kt) / Cm
    g = lambda K: num_of(j, K) - num_of(j - 1, K)
    lo, hi = Kt, Kt * (1 + mp.mpf("1e-9"))
    assert g(lo) > 0 > g(hi), "门槛处或右端符号未按预期"
    for _ in range(120):
        mid = (lo + hi) / 2
        if g(mid) > 0:
            lo = mid
        else:
            hi = mid
    Kr = (lo + hi) / 2
    u_true = (Kr - Kt) / Kt
    dv0 = mp.log(1 + mp.exp(-Cm * mp.log(2))) / mp.log(2)
    u_mech = dv0 / Cm
    u_r5 = mp.mpf("1.5e-22") / Cm
    P("  %d | %s | %s | %s | %s | %s | %s"
      % (j, mp.nstr(rho, 20), mp.nstr(Kt, 22), mp.nstr(u_true, 13), mp.nstr(g(Kt), 23),
         mp.nstr(u_true / u_mech, 9), mp.nstr(u_true / u_r5, 9)))
    if j == 90:
        P("     |G_90(K_thresh)|/P1 = %s  ；log10 = %s"
          % (mp.nstr(g(Kt) / D1, 9), mp.nstr(mp.log10(g(Kt) / D1), 9)))
        P("     T3new/P1 = %s ；（真值窗口）/（route-5 机制式修正后窗口）= %s"
          % (mp.nstr((3 * 89 / geomC) / D1, 9), mp.nstr(u_true / u_mech, 9)))

P("")
P("  门槛表（M = 86 至 92）与 K*、K_cross、T 下界的比较：")
Kstar = mp.mpf(205632218873398596256)
Kcross_lo = mp.mpf("313195478959172262876.636530619490706526023101")
T_lo = mp.mpf("3.131547906e20")
for j in range(86, 93):
    Kt = K_thresh(j)
    P("    M=%d  K_thresh = %s   (K* - Kt)/Kt = %s   (Kcross - Kt)/Kt = %s"
      % (j, mp.nstr(Kt, 22), mp.nstr((Kstar - Kt) / Kt, 7), mp.nstr((Kcross_lo - Kt) / Kt, 7)))
Kt90 = K_thresh(90)
P("  K_thresh(90) = %s ；K*/K_thresh(90) = %s ；T_lo/K_thresh(90) = %s"
  % (mp.nstr(Kt90, 24), mp.nstr(Kstar / Kt90, 9), mp.nstr(T_lo / Kt90, 9)))
P("  M=91、92 门槛处 G 符号：G_91 = %s ；G_92 = %s"
  % (mp.nstr(num_of(91, K_thresh(91)) - num_of(90, K_thresh(91)), 18),
     mp.nstr(num_of(92, K_thresh(92)) - num_of(91, K_thresh(92)), 18)))
P("  门槛处 G 逐档符号（M = 2 至 92，数值观察，证书见 d3wt_cert.py）：")
pos, neg = [], []
for j in range(2, 93):
    Kt = K_thresh(j)
    s = num_of(j, Kt) - num_of(j - 1, Kt)
    (pos if s > 0 else neg).append(j)
P("    目录一（G_M(门槛) > 0，即有窗）：%s" % pos)
P("    目录二（G_M(门槛) < 0，即无窗）：%s" % neg)
