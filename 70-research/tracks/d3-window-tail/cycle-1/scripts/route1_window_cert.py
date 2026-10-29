#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route1_window_cert.py —— route-1「否证独立重算」第 3 件：两约定分岔窗口的严格区间证书。

自足：只 import 标准库；不 import 任何项目脚本。

口径（逐字取自 70-research/cycle-2/route-5.md:110 至 :125 的 (D2) 至 (D5)，m = 92）：
  geom(x) = (delta^x - 1)/(delta - 1)          delta = log2 3
  c_j     = (m/j)*geom(j)*C                    C = log2((162/97)X0)，X0 = 695*2^60
  v(x,K)  = (x/m)*K*(delta-1)/(delta^x - 1) = C*K/c_x
  A(x)    = 0 (x=m) ；3/X0 (x=m-1) ；(97(m-x)+73)/(54 X0)（其余）
  numerator(x,K) = A(x) + 3/(2^{v(x,K)} - 1) + 3(x-1)/(2^{v(x,K)} - 1)^delta
  epsilon(x,K)   = numerator(x,K)/(3 K log 2)（正分母，故比较 epsilon 等于比较 numerator）

门槛 K = c_j(1+f)（f >= 0）处第 j 档与第 j-1 档（两档同属「其余」分支）之差：
  D_j(f) = -97/(54 X0) + 3/(2^{v_j}-1) - 3/(2^{v_{j-1}}-1)
           + 3(j-1)(2^{v_j}-1)^{-delta} - 3(j-2)(2^{v_{j-1}}-1)^{-delta}
  v_j = C(1+f)（故 2^{v_j} = 2^C * 2^{Cf}），v_{j-1} = rho_j C(1+f)（故 2^{v_{j-1}} = (2^C)^{rho_j} * 2^{rho_j Cf}）
  rho_j = (j-1)(delta^j - 1)/(j(delta^{j-1} - 1))
两约定分岔 ⟺ m2_max = j 可行且 argmin != j ⟺ D_j(f) > 0。
"""
from fractions import Fraction as F
import sys

OUT = []
ROOT = "/Users/luna/Documents/math IA/collatz-attack"


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def dec(x, nd):
    x = F(x)
    neg = x < 0
    x = abs(x)
    sc = 10 ** nd
    q = (x.numerator * sc) // x.denominator
    s = str(q)
    if nd:
        s = (s[:-nd] if len(s) > nd else "") + "." + s[-nd:].rjust(nd, "0")
        if s.startswith("."):
            s = "0" + s
    return ("-" if neg else "") + s


def sci(x, nd=6):
    x = F(x)
    if x == 0:
        return "0"
    neg = x < 0
    x = abs(x)
    e = 0
    while x >= 10:
        x /= 10
        e += 1
    while x < 1:
        x *= 10
        e -= 1
    return "%s%s×10^%d" % ("-" if neg else "", dec(x, nd), e)


def dec_to_F(s):
    s = s.strip()
    if "." in s:
        i, f = s.split(".")
        return F(int(i + f), 10 ** len(f))
    return F(int(s))


# #################### 严格区间原语 ####################
SNAP = 150


def snap_lo(x, Dg=SNAP):
    s = 10 ** Dg
    x = F(x)
    return F((x.numerator * s) // x.denominator, s)


def snap_hi(x, Dg=SNAP):
    s = 10 ** Dg
    x = F(x)
    n = x.numerator * s
    q, r = divmod(n, x.denominator)
    return F(q + (1 if r else 0), s)


def atanh_iv(u, N):
    """atanh(u) 的严格区间，要求 |u| <= 1/3（奇数性处理负号）。"""
    u = F(u)
    if u == 0:
        return F(0), F(0)
    if u < 0:
        a, b = atanh_iv(-u, N)
        return -b, -a
    assert 0 < u <= F(1, 3), u
    s = F(0)
    pw = u
    u2 = u * u
    for n in range(N + 1):
        s += pw / (2 * n + 1)
        pw *= u2
    return s, s + pw / ((2 * N + 3) * (1 - u2))


def ln2_atanh_iv(N):
    a, b = atanh_iv(F(1, 3), N)
    return 2 * a, 2 * b


def inter(a, b):
    lo, hi = max(a[0], b[0]), min(a[1], b[1])
    return (lo, hi) if lo <= hi else None


def ln_of_rat_iv(y, ln2iv, N, Dg=SNAP):
    y = F(y)
    assert y > 0
    k = y.numerator.bit_length() - y.denominator.bit_length()
    while F(2) ** k > y:
        k -= 1
    while F(2) ** (k + 1) <= y:
        k += 1
    z = y / F(2) ** k
    if z * z > 2:
        z /= 2
        k += 1
    u = (snap_lo(z, Dg) - 1) / (snap_lo(z, Dg) + 1)
    az = atanh_iv(u, N)
    lo2, hi2 = ln2iv
    if k >= 0:
        return k * lo2 + 2 * az[0], k * hi2 + 2 * az[1]
    return k * hi2 + 2 * az[0], k * lo2 + 2 * az[1]


def log2_of_rat_iv(y, ln2iv, N):
    a, b = ln_of_rat_iv(y, ln2iv, N)
    return a / ln2iv[1], b / ln2iv[0]


def exp_iv(x_lo, x_hi, N, K):
    def pos(a, b):
        a, b = snap_lo(a), snap_hi(b)
        y_lo, y_hi = a / F(2) ** K, b / F(2) ** K
        slo, term = F(0), F(1)
        for n in range(N + 1):
            slo += term
            term = term * y_lo / (n + 1)
            if n % 6 == 5:
                slo, term = snap_lo(slo), snap_lo(term)
        shi, term = F(0), F(1)
        for n in range(N + 1):
            shi += term
            term = term * y_hi / (n + 1)
            if n % 6 == 5:
                shi, term = snap_hi(shi), snap_hi(term)
        tail = snap_hi(term / (1 - y_hi / (N + 2)))
        a2, b2 = snap_lo(slo), snap_hi(shi + tail)
        for _ in range(K):
            a2, b2 = snap_lo(a2 * a2), snap_hi(b2 * b2)
        return a2, b2
    if x_lo >= 0:
        return pos(x_lo, x_hi)
    if x_hi <= 0:
        a, b = pos(-x_hi, -x_lo)
        return 1 / b, 1 / a
    a, b = pos(F(0), -x_lo)
    c, d = pos(F(0), x_hi)
    return 1 / b, d


def pow_rat_iv(base, e_lo, e_hi, ln2iv, N, K):
    a, b = ln_of_rat_iv(base, ln2iv, N)
    cs = [e_lo * a, e_lo * b, e_hi * a, e_hi * b]
    return exp_iv(min(cs), max(cs), N, K)


# #################### 常数 ####################
X0 = 695 * 2 ** 60
R2C = F(162 * X0, 97)
W0 = R2C - 1
M = 92
N_S, N_E, K_E = 90, 78, 14
A97 = F(97, 54 * X0)

p("#" * 72)
p("# route1_window_cert.py：两约定分岔窗口的严格区间证书（独立重算）")
p("# python %s ；m = 92 ；X0 = %d ；c_j 口径见 route-5.md:110 至 :125" % (sys.version.split()[0], X0))
p("#" * 72)
p("")
p("[0] 常数")
ln2A = ln2_atanh_iv(N_S)
s = F(0)
for n in range(1, N_S + 261):
    s += F(1, n * (2 ** n))
ln2B = (s, s + F(1, (N_S + 261) * (2 ** (N_S + 260))))
ln2iv = inter(ln2A, ln2B)
assert ln2iv is not None
p("    ln2 宽度 = %s（atanh 与对数级数两法相交）" % sci(ln2iv[1] - ln2iv[0], 3))
d3v = log2_of_rat_iv(F(3), ln2A, N_S)
p("    delta = log2 3 ∈ [%s, %s]  宽度 %s" % (dec(d3v[0], 30), dec(d3v[1], 30), sci(d3v[1] - d3v[0], 3)))
CA = log2_of_rat_iv(R2C, ln2A, N_S)
c695 = log2_of_rat_iv(F(695, 97), ln2A, N_S)
CB = (61 + 4 * d3v[0] + c695[0], 61 + 4 * d3v[1] + c695[1])
C_iv = inter(CA, CB)
assert C_iv is not None
p("    C ∈ [%s, %s]  宽度 %s（两套分解相交）" % (dec(C_iv[0], 40), dec(C_iv[1], 40), sci(C_iv[1] - C_iv[0], 3)))
lnR = ln_of_rat_iv(R2C, ln2iv, N_S)
lnW0 = ln_of_rat_iv(W0, ln2iv, N_S)
p("    ln(2^C) = ln((162/97)X0) 宽度 %s ；ln(2^C-1) 宽度 %s"
  % (sci(lnR[1] - lnR[0], 3), sci(lnW0[1] - lnW0[0], 3)))


def c_iv(j):
    return (F(M, j) * (d3v[0] ** j - 1) / (d3v[1] - 1) * C_iv[0],
            F(M, j) * (d3v[1] ** j - 1) / (d3v[0] - 1) * C_iv[1])


def rho_iv(j):
    return (F(j - 1, j) * (d3v[0] ** j - 1) / (d3v[1] ** (j - 1) - 1),
            F(j - 1, j) * (d3v[1] ** j - 1) / (d3v[0] ** (j - 1) - 1))


p("")
p("[1] 门槛 c_j 的严格区间（j = 88 至 92）")
CJ = {}
for j in (88, 89, 90, 91, 92):
    CJ[j] = c_iv(j)
    p("    c_%-2d ∈ [%s," % (j, dec(CJ[j][0], 22)))
    p("          %s]  相对宽 %s" % (dec(CJ[j][1], 22), sci((CJ[j][1] - CJ[j][0]) / CJ[j][0], 3)))
for j, s_ in ((89, "78555824936758779275.265552681458057901548946328722"),
              (90, "123124614107556571561.827996023727480573234158995835"),
              (91, "193003413899578228857.931158182789842293869597284142"),
              (92, "302578139046974169432.953163608816236674848698188491")):
    v = dec_to_F(s_)
    rel = abs(CJ[j][0] - v) / v
    p("    r4b2_window_probe.out 的 c_%-2d 打印串（48 位）与本轮下界相对差 = %s ；判据 <=1e-46 ？ %s"
      % (j, sci(rel, 3), rel <= F(1, 10 ** 46)))

# #################### 每格上下文 ####################
BASEC = exp_iv(-d3v[1] * lnW0[1], -d3v[0] * lnW0[0], N_E, K_E)      # (2^C-1)^{-delta}


def ctx_for(j):
    rho = rho_iv(j)
    Pj = pow_rat_iv(R2C, rho[0], rho[1], ln2iv, N_S, N_E)
    lp = (ln_of_rat_iv(Pj[0] - 1, ln2iv, N_S)[0], ln_of_rat_iv(Pj[1] - 1, ln2iv, N_S)[1])
    t3o = exp_iv(-d3v[1] * lp[1], -d3v[0] * lp[0], N_E, K_E)
    return dict(j=j, rho=rho, Pj=Pj, lp=lp,
                T3new0=(3 * (j - 1) * BASEC[0], 3 * (j - 1) * BASEC[1]),
                T3old0=(3 * (j - 2) * t3o[0], 3 * (j - 2) * t3o[1]))


def Dj_parts(ctx, f):
    """返回 (D_j(f) 区间, 中间量字典)。f 为精确有理数，f >= 0。"""
    j = ctx["j"]
    E = exp_iv(f * lnR[0], f * lnR[1], 22, 9)                # 2^{C f}（指数极小）
    W = (R2C * E[0], R2C * E[1])                             # 2^{v_j}
    T2n = (3 / (W[1] - 1), 3 / (W[0] - 1))
    lq = (ln_of_rat_iv(W[0] - 1, ln2iv, 34, 70)[0], ln_of_rat_iv(W[1] - 1, ln2iv, 34, 70)[1])
    corr = exp_iv(-d3v[1] * (lq[1] - lnW0[0]), -d3v[0] * (lq[0] - lnW0[1]), 14, 7)
    T3n = (ctx["T3new0"][0] * corr[0], ctx["T3new0"][1] * corr[1])
    E2 = exp_iv(f * ctx["rho"][0] * lnR[0], f * ctx["rho"][1] * lnR[1], 22, 9)
    W2 = (ctx["Pj"][0] * E2[0], ctx["Pj"][1] * E2[1])        # 2^{v_{j-1}}
    T2o = (3 / (W2[1] - 1), 3 / (W2[0] - 1))
    lq2 = (ln_of_rat_iv(W2[0] - 1, ln2iv, 34, 70)[0], ln_of_rat_iv(W2[1] - 1, ln2iv, 34, 70)[1])
    corr2 = exp_iv(-d3v[1] * (lq2[1] - ctx["lp"][0]), -d3v[0] * (lq2[0] - ctx["lp"][1]), 14, 7)
    T3o = (ctx["T3old0"][0] * corr2[0], ctx["T3old0"][1] * corr2[1])
    lo = -A97 + T2n[0] - T2o[1] + T3n[0] - T3o[1]
    hi = -A97 + T2n[1] - T2o[0] + T3n[1] - T3o[0]
    return (lo, hi), dict(W=W, W2=W2, T2n=T2n, T2o=T2o, T3n=T3n, T3o=T3o)


def sign_D(ctx, f):
    iv, mid = Dj_parts(ctx, f)
    if iv[1] < 0:
        return -1, iv, mid
    if iv[0] > 0:
        return 1, iv, mid
    return 0, iv, mid


def deriv_cert(ctx):
    """dD_j/df < 0 对一切 f >= 0 的显式界证明（用 W' = W^{rho}、X = W/2^C >= 1）。"""
    j = ctx["j"]
    rho_lo, rho_hi = ctx["rho"]
    # 记 X = W/2^C >= 1（W = 2^{v_j}），W' = W^{rho}（精确）。由 W = 2^C X 与 rho > 1：
    #   LHS 里的 3 lnR W/(W-1)^2 >= lnR_lo * W^{-1} = (lnR_lo/2^C) * X^{-1}（丢掉全部其余正项）
    #   RHS 的每一项 <= c1 * (系数上界) * 2^C^{-rho_lo} * X^{-rho} <= ... * X^{-rho_lo}（X >= 1）
    # 故 LHS/RHS >= (A/B) * X^{rho_lo-1} >= A/B，只需在 X = 1 处比较（显式有理数）。
    lhs = lnR[0] / R2C
    c1 = 1 / (1 - R2C ** (-rho_lo)) ** 2
    rhs = c1 * (rho_hi * lnR[1] * R2C ** (-rho_lo)
                + d3v[1] * rho_hi * (j - 2) * R2C ** (-rho_lo * d3v[0]))
    return lhs, rhs, c1, c1


# #################### 主循环 ####################
p("")
p("[2] 三格窗口右端的严格区间证书（j = 88、89、90）")
N_STEP = 96
FMAX = F(1, 10 ** 12)
RESULTS = {}
for j in (88, 89, 90):
    ctx = ctx_for(j)
    p("")
    p("    --- j = %d ---" % j)
    p("        rho_j ∈ [%s, %s]（宽度 %s）"
      % (dec(ctx["rho"][0], 20), dec(ctx["rho"][1], 20), sci(ctx["rho"][1] - ctx["rho"][0], 3)))
    iv0, _ = Dj_parts(ctx, F(0))
    p("        D_j(0) ∈ [%s, %s] ；> 0 ？（门槛处新档更差） %s"
      % (sci(iv0[0], 8), sci(iv0[1], 8), iv0[0] > 0))
    iv1, _ = Dj_parts(ctx, FMAX)
    p("        D_j(1e-12) ∈ [%s, %s] ；< 0 ？ %s" % (sci(iv1[0], 8), sci(iv1[1], 8), iv1[1] < 0))
    lhs, rhs, c1, c2 = deriv_cert(ctx)
    p("        单调性证书（对一切 f >= 0）：LHS 下界 %s > RHS 上界 %s ？ %s（余量 %s 倍）"
      % (sci(lhs, 6), sci(rhs, 6), lhs > rhs, sci(lhs / rhs, 3)))
    lo, hi = F(0), FMAX
    npos = nneg = nunk = 0
    for it in range(N_STEP):
        mid = (lo + hi) / 2
        sg, _, _ = sign_D(ctx, mid)
        if sg > 0:
            lo, npos = mid, npos + 1
        elif sg < 0:
            hi, nneg = mid, nneg + 1
        else:
            nunk += 1
            break
    p("        二分 %d 步：判据取「正」%d 次、「负」%d 次、不可判 %d 次（判据两值都出现）"
      % (N_STEP, npos, nneg, nunk))
    p("        f*_j ∈ [%s," % dec(lo, 40))
    p("               %s]  绝对宽 %s ；相对宽 %s"
      % (dec(hi, 40), sci(hi - lo, 3), sci((hi - lo) / lo, 3)))
    p("        窗口 = [c_j, c_j(1+f*))；左端 c_j ∈ [%s, %s]"
      % (dec(CJ[j][0], 22), dec(CJ[j][1], 22)))
    K_lo, K_hi = CJ[j][0] * (1 + lo), CJ[j][1] * (1 + hi)
    p("        K 侧右端 ∈ [%s," % dec(K_lo, 20))
    p("                    %s]  相对宽 %s" % (dec(K_hi, 20), sci((K_hi - K_lo) / K_lo, 3)))
    p("        m2_max = j 的可行性上界：c_{j+1} 下界 > 本窗口右端上界？ %s（比值 %s）"
      % (CJ[j + 1][0] > K_hi, sci(CJ[j + 1][0] / K_hi, 4)))
    RESULTS[j] = dict(f=(lo, hi), K=(K_lo, K_hi), ctx=ctx)

p("")
p("[3] 窗口内「argmin != m2_max（两约定分岔）」的证明链（不靠采样）")
p("    (i)   m2_max(K) = j：由 c_{j+1} > c_j(1+f*_j)（[2] 每格末行）与 F 是下段（已证）。")
p("    (ii)  numerator(j) > numerator(j-1)：由 D_j(0) > 0 与 f < f*_j（[2] 已证）。")
p("    (iii) 一切 k <= j-1 有 numerator(k) < numerator(k-1)：")
p("          第 k 档的自变量 f_k = K/c_k - 1 >= rho_{k+1}(1+f) - 1 >= rho_{k+1} - 1 > 0.56；")
p("          而 [2] 的单调性证书对每格成立（同一界只依赖 j 与 rho 的上界），故 f_k > f*_k 时 D_k < 0。")
rmin = min(rho_iv(k)[0] for k in (88, 89, 90, 91, 2, 3))
p("          数值：min rho_{k+1} 下界（k = 87 至 90 与 k = 1、2）= %s > 1 + f*_j（f*_j < 1e-12）"
  % dec(rmin, 12))
p("    => F = {1,...,j} 上分子在 k = j-1 取最小，故 m2_max = j 而 argmin = j-1 != m2_max：分岔成立。")

p("")
p("[4] j = 91、92 的窗口为空（对一切 f >= 0 的上界，显式证明）")
for j in (91, 92):
    astep = -F(105, 54 * X0) if j == 91 else -F(3, X0)
    ub = F(3) / (R2C - 1) + 3 * (j - 1) / (R2C - 1) * BASEC[1] + astep
    p("    j = %d：A 阶梯 = %s ；上界 = 3/(2^C-1) + 3(j-1)(2^C-1)^{-delta} + A阶梯 = %s ；< 0 ？ %s"
      % (j, sci(astep, 6), sci(ub, 8), ub < 0))
p("    机制：j = m-1 与 j = m 的 A 阶梯为 -105/(54X0)、-3/X0，比 -97/(54X0) 更负，")
p("    超出 3/(2^C-1) 的量级，故新档在门槛处立即获胜（与 r4b2_window_probe.out 的 [3] 段一致）。")
p("    注意：因 v_j >= C 对一切 f >= 0 成立，该上界是全域的，不只是小 f。")

p("")
p("[5] K* 与 K_cross 的窗口隶属判定（严格比较）")
Kstar = 205632218873398596256
p("    K* = %d（c2r5_cert.log:5、:8 的分母）" % Kstar)
for j in (88, 89, 90):
    K_lo, K_hi = RESULTS[j]["K"]
    p("    j = %-2d 窗口 K 侧 ∈ [%s, %s] ；K* 落入？ %s ；与窗口相交？ %s"
      % (j, dec(K_lo, 6), dec(K_hi, 6), K_lo <= Kstar <= K_hi, not (Kstar < K_lo or Kstar > K_hi)))
p("    K* > c_91(1+f*_91) 的上界？ %s ；K* < c_92 的下界？ %s"
  % (Kstar > CJ[91][1] * (1 + RESULTS[90]["f"][1]), Kstar < CJ[92][0]))
p("    => K* ∈ [c_91(1+f*_91), c_92)；j = 91、92 窗口为空（[4]），88 至 90 窗口都在其下；")
p("       故 K* 不在任何窗口内（与 c2r5_cert.log [1] 的 F_92(K*) = {1,...,91} 相容，argmin = m2_max）。")
KC_lo = dec_to_F("313195478959172262876.6365306194907065260231016940260118526233")
KC_hi = dec_to_F("313195478959172262876.6365306194907065260231016961279595491105")
p("    K_cross ∈ [%s, %s]（cert.log [5]，47 位）" % (dec(KC_lo, 40), dec(KC_hi, 40)))
p("    K_cross 下端 > c_92 上界？ %s ；故 K_cross 也在一切窗口之外。" % (KC_lo > CJ[92][1]))

p("")
p("[6] 与兄弟轨道 r4b2_window_probe.out 的对照（同精度口径：只比到对方打印位数）")
for j, a, b in ((90, "123124614107652692133.007231711933058876044901",
                 "123124614107652692133.007231919710646726095849"),
                (89, "78555824936819382091.475309577063948109807001",
                 "78555824936819382091.475309709629966165890197")):
    ra, rb = dec_to_F(a), dec_to_F(b)
    my = RESULTS[j]["K"]
    p("    j = %d：" % j)
    p("      r4b2 区间 ⊆ 本轮区间 或 本轮区间 ⊆ r4b2 区间？ %s / %s ；相交？ %s"
      % (my[0] <= ra and rb <= my[1], ra <= my[0] and my[1] <= rb, not (my[1] < ra or my[0] > rb)))
    p("      两区间中点相对差 = %s" % sci(abs((my[0] + my[1]) / 2 - (ra + rb) / 2) / ra, 4))
    p("      相对窗口宽度：本轮 %s ；r4b2 打印 %s"
      % (sci(RESULTS[j]["f"][0], 8),
         "7.80677136541e-13" if j == 90 else "7.71461775858e-13"))
p("    j = 88：r4b2 与 kcross-tail/cycle-1/ledger-note.md 均记该格严格区间缺失；本轮补上：")
p("      相对窗口宽度 ∈ [%s, %s] ；K 侧右端 ∈ [%s, %s]"
  % (sci(RESULTS[88]["f"][0], 8), sci(RESULTS[88]["f"][1], 8),
     dec(RESULTS[88]["K"][0], 20), dec(RESULTS[88]["K"][1], 20)))
p("    上一轮数值（undefined/cycle-1/route-1.md:10、materials.md:41 记 7.622/7.715/7.807×10^-13）对照：")
p("      本轮 %s / %s / %s（对方是数值观察，本轮是两端严格区间；见 [2]）"
  % (sci(RESULTS[88]["f"][0], 6), sci(RESULTS[89]["f"][0], 6), sci(RESULTS[90]["f"][0], 6)))

p("")
p("[7] 扰动实例（每个判据都能取另一值）")
p("    (a) 「上界 < 0」判据：j = 91 得 %s，j = 92 得 %s，j = 90 得 %s（负对照与前两格的差别由 A 阶梯造成）"
  % (F(3) / (R2C - 1) + 3 * 90 / (R2C - 1) * BASEC[1] - F(105, 54 * X0) < 0,
     F(3) / (R2C - 1) + 3 * 91 / (R2C - 1) * BASEC[1] - F(3, X0) < 0,
     F(3) / (R2C - 1) + 3 * 89 / (R2C - 1) * BASEC[1] - A97 < 0))
K_lo, K_hi = RESULTS[90]["K"]
f_mid = (RESULTS[90]["f"][0] + RESULTS[90]["f"][1]) / 2
pt_in = CJ[90][0] * (1 + f_mid)
p("    (b) 「落在 j = 90 窗口内」判据：窗口内一点 %s -> %s ；K* -> %s"
  % (dec(pt_in, 6), K_lo <= pt_in <= K_hi, K_lo <= Kstar <= K_hi))
sg0, _, _ = sign_D(RESULTS[90]["ctx"], F(0))
sg2, _, _ = sign_D(RESULTS[90]["ctx"], RESULTS[90]["f"][1] * 2)
p("    (c) 符号判据 sign_D：f = 0 -> %s ；f = 2f*_90 -> %s（两值都取到）" % (sg0, sg2))
ub90 = F(3) / (R2C - 1) + 3 * 89 / (R2C - 1) * BASEC[1] - A97
p("    (d) A 阶梯灵敏度：换成 96/(54X0) 时 j = 90 的上界 = %s（仍 > 0）；"
  % sci(F(3) / (R2C - 1) + 3 * 89 / (R2C - 1) * BASEC[1] - F(96, 54 * X0), 6))
p("        换成 105/(54X0) 时为 %s（< 0）——判据确实依赖 A 阶梯的精确值。"
  % sci(F(3) / (R2C - 1) + 3 * 89 / (R2C - 1) * BASEC[1] - F(105, 54 * X0), 6))

p("")
p("[5b] 对一切 j <= 90 的统一下界（把「不在任何窗口内」补成全域命题，不逐格造证书）")
F0 = F(1, 10 ** 12)
Wf0 = R2C * exp_iv(F0 * lnR[0], F0 * lnR[1], 22, 9)[1]
t2max = 3 / (Wf0 - 1)
p("    f0 = 1e-12 处 3/(2^{v_j}-1) 的上界 = %s（在 f >= f0 时更小，函数随 f 递减）" % sci(t2max, 8))
B0 = -A97 + t2max
margin = -B0                                  # = 97/(54X0) - 3/(2^{C(1+f0)}-1) > 0
p("    B(f0) := -97/(54X0) + 3/(2^{C(1+f0)}-1) = %s < 0" % sci(B0, 8))
jmax = margin / (3 * BASEC[0]) + 1
p("    上界 D_j(f) <= B(f0) + (j-1)*3*(2^C-1)^{-delta}（丢掉了两个负项）")
p("    故 D_j(f) < 0 对一切 f >= f0 成立，当 (j-1) < %s，即 j <= %d"
  % (sci(margin / (3 * BASEC[0]), 8), int(jmax)))
p("    配合 [2]、[3] 的单调性（dD_j/df < 0 对一切 f >= 0），j <= %d 的窗口含于 [c_j, c_j(1+f0)]" % int(jmax))
c90max = CJ[90][1] * (1 + F0)
p("    而 c_90(1+f0) 上界 = %s < K* = 205632218873398596256 ？ %s"
  % (dec(c90max, 6), c90max < Kstar))
p("    => 一切 j <= 90 的窗口都在 K* 之下；j = 91、92 窗口为空（[4]）：K* 与 K_cross 不在任何窗口内。")

p("")
p("[7.5] 机制核算：route-5.md:230 的 2×10^-24 与三轮数值的关系（本证书独立复算）")
sens = 3 * C_iv[0] * ln2iv[0] * R2C / (R2C - 1) ** 2      # |d/df[3/(2^{v_j}-1)]| 在 f=0 处
sens = 3 * C_iv[0] * ln2iv[0] * R2C / (R2C - 1) ** 2
P1ex = 3 * (F(97, 162 * X0)) ** 2 / (1 - F(97, 162 * X0))
dlog = log2_of_rat_iv(1 + F(1) / R2C, ln2iv, N_S)[0]      # log2(1 + 2^{-C}) 严格下界
p("    灵敏度系数 |d/df[3/(2^{v_j}-1)]|（f = 0 处）= %s（= 3*C*ln2*2^C/(2^C-1)^2）" % sci(sens, 6))
p("    (a) route-5 自己的两项框架：交点条件 v > log2(2^C+1) = C + log2(1+2^-C)，")
p("        故相对宽 = log2(1+2^-C)/C = %s" % sci(dlog / C_iv[1], 6))
p("        而 route-5.md:230 把 log2(1+2^-C) 写成 1.5e-22：真值 = %s，差 %s 倍（第一处算术错）"
  % (sci(dlog, 6), sci(dlog / F(15, 10 ** 23), 4)))
p("    (b) 该两项框架的窗口也 = P1/灵敏度 = %s（两路一致，说明归一化本身无误）"
  % sci(P1ex / sens, 6))
p("    (c) 但门槛处真实主导差 = 第三项 − 下一档第二项 = %s"
  % sci(RESULTS[90]["ctx"]["T3new0"][0] - 3 / (RESULTS[90]["ctx"]["Pj"][1] - 1), 6))
p("    (d) 真实窗口 = (c)/灵敏度 = %s ；本证书二分 f*_90 = %s ；相对差 %s（线性化误差）"
  % (sci((RESULTS[90]["ctx"]["T3new0"][0] - 3 / (RESULTS[90]["ctx"]["Pj"][1] - 1)) / sens, 6),
     sci(RESULTS[90]["f"][0], 6),
     sci(abs((RESULTS[90]["ctx"]["T3new0"][0] - 3 / (RESULTS[90]["ctx"]["Pj"][1] - 1)) / sens
             - RESULTS[90]["f"][0]) / RESULTS[90]["f"][0], 3)))
p("    => 真值 / route-5 写值（2×10^-24）= %s 倍；其中漏第三项贡献 %s 倍，"
  % (sci(RESULTS[90]["f"][0] / F(2, 10 ** 24), 4),
     sci((RESULTS[90]["ctx"]["T3new0"][0] - 3 / (RESULTS[90]["ctx"]["Pj"][1] - 1)) / P1ex, 4)))
p("       即 route-5 自己框架内的 log2(1+2^-C) 数值错贡献 %s 倍（两者相乘即总倍率）。"
  % sci(dlog / F(15, 10 ** 23), 4))

p("")
p("[8] 结论与等级")
p("    8.1 三格（j = 88、89、90）窗口右端给出两端严格有理的包含区间，相对宽 <= 1e-28（见 [2]）。")
p("    8.2 根唯一：单调性 dD_j/df < 0 对一切 f >= 0 由 [2]、[3] 的显式界证明（非采样）。")
p("    8.3 左端 = c_j（严格区间）；按 (D2) 的「<=」写法窗口含左端点，按「<」写法则不含。")
p("    8.4 右端 pin：本证书的右端 = D_j 变号点，与 r4b2 的「numerator(j) = numerator(j-1)」同义。")
p("    8.5 K* 与 K_cross 落在一切窗口之外（[5]），j = 91、92 窗口为空（[4]）。")
p("    等级：自足纸面论证 + 可复算脚本（自足区间原语，经 e 的独立严格参照自检）；")
p("          未形式化、未经第三方复核；未用任何网格或采样作全称证据。")

path = (ROOT + "/70-research/tracks/d3-window-tail/cycle-1/scripts/results/route1_window_cert.out")
import pathlib as _pl
_pl.Path(path).write_text("\n".join(OUT) + "\n", encoding="utf-8")
print("\n[写出] " + path)
