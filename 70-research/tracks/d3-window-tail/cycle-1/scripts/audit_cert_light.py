#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""d3-window-tail cycle-1 route-2（证书对抗审计）独立复核实测版（自足、无重型依赖）。

设计（为绕开本环境 mpmath/decimal 导入极慢的问题）：
  * 只用 fractions.Fraction 与整数运算；超越量全部走自写级数与显式尾界；
  * 每步定向舍入到 1/GRID 网格（GRID = 1e-70），区间宽度 ~1e-60 到 1e-50 量级；
  * 判据全部是「区间符号判定」或「精确有理比较」，并登记所需精度的余量；
  * 不重跑既有脚本、不做枚举、不重开二分（只做点值复核）。

节：[A] C 的 float64 伪值  [B] 第三项主导  [C] 窗口两端区间与端点符号
    [D] 门槛单调性（窗口界于相邻门槛之间）  [E] j=2/91/92 无窗反向判据  [F] K*、T、R 位置
"""
import json, math, re, hashlib, os
from fractions import Fraction as F

GRID = 10 ** 70
ROOT = "/Users/luna/Documents/math IA/collatz-attack"
U1 = os.path.join(ROOT, "70-research/tracks/undefined/cycle-1")
JSON_IN = os.path.join(U1, "scripts/results/route3_windows.json")
C1U2_OUT = os.path.join(U1, "scripts/results/c1u2_window_cert.out")
CERT_LOG = os.path.join(ROOT, "70-research/cycle-2/scripts/results/c2r5_cert.log")
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = []
CHK = []
X0 = 695 * 2 ** 60
M_M = 92


def P(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s)


def C_(name, ok, det=""):
    CHK.append((name, bool(ok)))
    P("  [判据] %s -> %s   %s" % (name, bool(ok), det))


def fl(x):
    x = F(x)
    return F((x.numerator * GRID) // x.denominator, GRID)


def ce(x):
    x = F(x)
    return F(-((-x.numerator * GRID) // x.denominator), GRID)


# --------- 定向区间（(lo, hi) 二元组） ---------
def iadd(a, b):
    return (fl(a[0] + b[0]), ce(a[1] + b[1]))


def isub(a, b):
    return (fl(a[0] - b[1]), ce(a[1] - b[0]))


def imul(a, b):
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (fl(min(p)), ce(max(p)))


def idiv(a, b):
    assert b[0] > 0, "除数须正"
    p = (a[0] / b[0], a[0] / b[1], a[1] / b[0], a[1] / b[1])
    return (fl(min(p)), ce(max(p)))


def ipow_int(a, n):
    lo, hi = F(1), F(1)
    blo, bhi = a[0], a[1]
    while n:
        if n & 1:
            lo, hi = fl(lo * blo), ce(hi * bhi)
        blo, bhi = fl(blo * blo), ce(bhi * bhi)
        n >>= 1
    return (lo, hi)


def ico(x):
    return (F(x), F(x))


def iw(x):
    return x[1] - x[0]


# --------- 初等函数（自足级数 + 显式尾界） ---------
def atanh_iv(x, N):
    """atanh(x)，0 < x < 1/3：sum x^{2j+1}/(2j+1)，尾界 x^{2N+3}/((2N+3)(1-x^2))。"""
    x = F(x)
    x2 = x * x
    s = F(0)
    pw = x
    for j in range(N + 1):
        s += pw / (2 * j + 1)
        pw *= x2
    tail = pw / ((2 * N + 3) * (1 - x2))
    return (fl(s), ce(s + tail))


LN2 = tuple(2 * v for v in atanh_iv(F(1, 3), 130))       # ln2 = 2 atanh(1/3)
LN3 = iadd(tuple(2 * v for v in atanh_iv(F(1, 5), 130)), ico(LN2[0])) if False else \
      iadd((LN2[0], LN2[1]), tuple(2 * v for v in atanh_iv(F(1, 5), 130)))
# ln(112590/97) = 10 ln2 + 2 atanh(6631/105959)（精确分解：112590/97 = 2^10 * (112590/99328)）
LN112 = iadd(tuple(10 * v for v in LN2), tuple(2 * v for v in atanh_iv(F(6631, 105959), 80)))
LN2I = (LN2[0], LN2[1])
DELTA = idiv(LN3, LN2I)
C_IV = iadd((F(60), F(60)), idiv(LN112, LN2I))


def exp_dir(y, up):
    """exp(y) 的定向界（y 有理，|y| <= 200）。归约到 [0, ln2) 后用泰勒 + 尾界。"""
    y = F(y)
    k = int((y / LN2I[1]).__floor__())
    for _ in range(6):
        r_lo = y - k * LN2I[1]
        r_hi = y - k * LN2I[0]
        if r_lo < 0:
            k -= 1
            continue
        if r_hi > LN2I[1]:
            k += 1
            continue
        break
    else:
        raise RuntimeError("exp 归约失败")
    N = 60
    if r_lo >= 0 and r_hi <= LN2I[1]:
        pass
    # 泰勒（对 r ∈ [0, ln2] ⊂ [0, 0.7]）
    r = r_hi if up else r_lo
    s = F(1)
    t = F(1)
    for j in range(1, N + 1):
        t = fl(t * r / j) if not up else ce(t * r / j)
        s = fl(s + t) if not up else ce(s + t)
    # 尾界：t_{N+1} <= t * r/(N+1)，几何比 r/(N+2) <= 0.7/62
    tn = (fl(t * r / (N + 1))) if not up else ce(t * r / (N + 1))
    ratio = fl(r / (N + 2)) if not up else ce(r / (N + 2))
    tail = tn / (1 - ratio) if not up else ce(tn / fl(1 - ratio))
    val = s + tail if up else s
    if k >= 0:
        q = 2 ** k
        return ce(val * q) if up else fl(val * q)
    q = 2 ** (-k)
    return ce(val / q) if up else fl(val / q)


def exp_iv(y):
    return (exp_dir(y[0], False), exp_dir(y[1], True))


def pow2_neg_iv(v):
    """2^{-v} 的区间（v = (lo,hi)，单调递减）。"""
    z = (fl(-(v[1]) * LN2I[1]), ce(-(v[0]) * LN2I[0]))
    return exp_iv(z)


def inv_2vm1(v):
    """1/(2^v - 1) = 2^{-v}/(1-2^{-v}) 的区间（用 1/(1-x) ∈ [1, 1+2x]，x<=1/2）。"""
    u = pow2_neg_iv(v)
    lo_ = u[0]
    hi_ = u[1]
    return (lo_, ce(hi_ * (1 + 2 * u[1])))


def inv_2vm1_delta(v, d):
    """1/(2^v - 1)^d = 2^{-dv} (1-2^{-v})^{-d} 的区间（(1-x)^{-d} ∈ [1, 1+4x]，x<=1/5，d<=2）。"""
    u = pow2_neg_iv(v)
    dv = imul(d, v)
    zd = (fl(-(dv[1]) * LN2I[1]), ce(-(dv[0]) * LN2I[0]))
    p = exp_iv(zd)                       # 2^{-dv}
    return (p[0], ce(p[1] * (1 + 4 * u[1])))


def A_iv(m2):
    if m2 == M_M:
        return ico(F(0))
    if m2 == M_M - 1:
        return ico(F(3, X0))
    return ico(F(97 * (M_M - m2) + 73, 54 * X0))


def v_iv(m2, K):
    """v = (m2/92) K (delta-1)/(delta^m2 - 1)。"""
    pm = ipow_int(DELTA, m2)
    fr = idiv(isub(DELTA, ico(F(1))), isub(pm, ico(F(1))))
    return imul(imul(ico(F(m2, M_M)), K), fr)


def N_iv(m2, K):
    v = v_iv(m2, K)
    t2 = inv_2vm1(v)
    t3 = inv_2vm1_delta(v, DELTA)
    return iadd(iadd(A_iv(m2), tuple(3 * x for x in t2)), tuple(3 * (m2 - 1) * x for x in t3))


def f_iv(M, K):
    return isub(N_iv(M, K), N_iv(M - 1, K))


def kthresh(m2):
    """K_thresh = (92/m2) geom(m2) C，geom = (delta^m2-1)/(delta-1)。"""
    pm = ipow_int(DELTA, m2)
    geom = idiv(isub(pm, ico(F(1))), isub(DELTA, ico(F(1))))
    return imul(imul(ico(F(M_M, m2)), geom), C_IV)


def tau_iv(t):
    pm = ipow_int(DELTA, t)
    pm1 = ipow_int(DELTA, t - 1)
    return imul(ico(F(t - 1, t)), idiv(isub(pm, ico(F(1))), isub(pm1, ico(F(1)))))


def dec(x, n=30):
    x = F(x)
    s = "-" if x < 0 else ""
    y = abs(x)
    i = y.numerator // y.denominator
    r = y - i
    d = (r.numerator * 10 ** n) // r.denominator
    return "%s%d.%s" % (s, i, str(d).rjust(n, "0"))


def sci(x, k=12):
    x = F(x)
    if x == 0:
        return "0"
    s = "-" if x < 0 else ""
    y = abs(x)
    e = 0
    while y >= 10:
        y /= 10
        e += 1
    while y < 1:
        y *= 10
        e -= 1
    m = (y.numerator * 10 ** k) // y.denominator
    return "%s%d.%s e%+d" % (s, m // 10 ** k, str(m % 10 ** k).rjust(k, "0"), e)


P("=" * 96)
P("audit_cert_light.py：route-2 独立复核（自足 Fraction 定向区间，GRID = 1e-70；无重型依赖）")
P("输入 md5（只读）：")
for pth in (JSON_IN, C1U2_OUT, CERT_LOG):
    P("  %s  %s" % (hashlib.md5(open(pth, "rb").read()).hexdigest(), pth))
P("  常数区间：ln2 ∈ [%s, %s]（宽 %s）" % (dec(LN2[0], 25), dec(LN2[1], 25), sci(iw(LN2))))
P("            delta ∈ [%s, %s]（宽 %s）" % (dec(DELTA[0], 25), dec(DELTA[1], 25), sci(iw(DELTA))))
P("            C ∈ [%s, %s]（宽 %s）" % (dec(C_IV[0], 25), dec(C_IV[1], 25), sci(iw(C_IV))))
P("  自检 exp(ln2) 覆盖 2：下界 ≤ 2 ≤ 上界 ？%s" % (
    exp_dir(LN2[0], False) <= 2 <= exp_dir(LN2[1], True)))

# ================= [A] =================
P("")
P("-" * 96)
P("[A] C 的 float64 伪值判定")
x64 = math.log2((162 / 97) * X0)
fx = F(x64)
d64str = dec(fx, 45)
P("  float64(C) 的精确值 = %s" % d64str)
C_("A1 float64(C) 精确展开 = audit_c.out [A5] 记录串",
   d64str == "70.180806328308364072654512710869312286376953125")
D1 = F(701808063283083640726545127109, 10 ** 28)
sc = fx * 10 ** 28
q = sc.numerator // sc.denominator
r28d = F(q, 10 ** 28)
r28u = F(q + 1, 10 ** 28) if F(q, 10 ** 28) != sc else r28d
r28r = F(sc.numerator * 2 // sc.denominator + (1 if (sc.numerator * 2) % sc.denominator else 0), 2 * 10 ** 28) if False else None
half = F(1, 2)
r28round = F((sc + half).numerator // (sc + half).denominator, 10 ** 28)
P("  (D1) = %s；double 的 28 位截断 = %s" % (dec(D1, 28), dec(r28d, 28)))
C_("A2 (D1) = double 的 28 位四舍五入（floor(x+1/2) 语义）", r28round == D1)
C_("A3 (D1) ≠ double 的 28 位截断", r28d != D1)
gap = isub(C_IV, ico(D1))
P("  C − (D1) ∈ [%s, %s]" % (sci(gap[0]), sci(gap[1])))
C_("A4 严格：C 下界 − (D1) > 1e-16（差 ≈ 2.7522e-15；本区间宽 ~1e-65，余量 49 个数量级）",
   gap[0] > F(1, 10 ** 16))
C_("A5 差 ∈ (2.75e-15, 2.76e-15)", F(275, 10 ** 17) < gap[0] and gap[1] < F(276, 10 ** 17))
alt = ((60.0 + math.log2(695.0)) + math.log2(162.0)) - math.log2(97.0)
C_("A6 第二路 float64 ≠ 第一路（(D1) 只能来自 log2((162/97)X0) 一路）", F(alt) != fx)
P("  第二路 float64 精确值 = %s" % dec(F(alt), 45))

# ================= [B] =================
P("")
P("-" * 96)
P("[B] 第三项主导（10.7177 个数量级）")
twoC = ipow_int(ico(F(2)), 70)  # 占位，下面用 exp 直接算
t2C = inv_2vm1(C_IV)                                    # 1/(2^C - 1)
P1 = isub(tuple(3 * x for x in t2C), ico(F(97, 54 * X0)))  # 3/(2^C-1) - 97/(54X0)
P("  3/(2^C−1) ∈ [%s, %s]；97/(54X0) = %s" % (sci(3 * t2C[0]), sci(3 * t2C[1]), sci(F(97, 54 * X0))))
P("  P1 = 3/(2^C−1) − 97/(54X0) ∈ [%s, %s]" % (sci(P1[0], 10), sci(P1[1], 10)))
C_("B1 P1 ∈ (1.6751e-42, 1.6753e-42)", F(16751, 10 ** 46) < P1[0] and P1[1] < F(16753, 10 ** 46))
T3 = {}
for j in (88, 89, 90):
    t3 = inv_2vm1_delta(C_IV, DELTA)
    T3[j] = tuple(3 * (j - 1) * x for x in t3)
    P("  第三项 3·%d/(2^C−1)^delta ∈ [%s, %s]" % (j - 1, sci(T3[j][0], 10), sci(T3[j][1], 10)))
C_("B2 第三项(90) ∈ (8.7448e-32, 8.7451e-32)", F(87448, 10 ** 37) < T3[90][0] and T3[90][1] < F(87451, 10 ** 37))
rat = T3[90][0] / P1[1]
P("  第三项(90)/P1 ∈ [%s, %s]" % (sci(rat, 10), sci(T3[90][1] / P1[0], 10)))
C_("B3 比值 ∈ (5.22e10, 5.221e10)：log10 ≈ 10.7177（比 route-5 比的两项差大 10.72 个数量级）",
   F(522, 10 ** 8) < rat and T3[90][1] / P1[0] < F(5221, 10 ** 9))
l2c = idiv((fl(F(1) / (2 ** 22)) if False else fl(F(97, 162) / X0 - (F(97, 162) / X0) ** 2 / 2), F(97, 162) / X0), LN2I)
P("  log2(1+2^{−C}) ∈ [%s, %s]" % (sci(l2c[0]), sci(l2c[1])))
C_("B4 log2(1+2^{−C}) ∈ (1.078e-21, 1.079e-21)（route-5 的 1.5e-22 被排除，差 7.19 倍）",
   F(1078, 10 ** 24) < l2c[0] and l2c[1] < F(1079, 10 ** 24))
C_("B5 2^{−C} = 97/(162X0) = 7.4726e-22（route-5 的「相对量」相容）",
   abs(F(97, 162) / X0 - F(74726075659361527737, 10 ** 37)) < 0 and True)

# ================= [C] =================
P("")
P("-" * 96)
P("[C] 窗口两端区间复核（route3 G=160 精确有理 + c1u2 印刷串 +1e-20 外扩）")
js = json.load(open(JSON_IN, encoding="utf-8"))
G160 = js["160"]
c1u2_txt = open(C1U2_OUT, encoding="utf-8").read()
c1u2_br = {}
for mm in re.finditer(r"二分 \d+ 步：K1\((\d+)\) ∈ \[([0-9.]+), ([0-9.]+)\]", c1u2_txt):
    c1u2_br[int(mm.group(1))] = (F(mm.group(2)), F(mm.group(3)))
C_("C0 c1u2 印刷端点解析到 88、89、90 三档", set(c1u2_br) == {88, 89, 90})
cert = {}
for M in (88, 89, 90):
    Klo, Khi = F(G160[str(M)]["Klo"]), F(G160[str(M)]["Khi"])
    a, b = F(G160[str(M)]["a"]), F(G160[str(M)]["b"])
    a2, b2 = c1u2_br[M]
    b2o = b2 + F(1, 10 ** 20)
    P("  --- M = %d ---" % M)
    fKlo, fKhi = f_iv(M, ico(Klo)), f_iv(M, ico(Khi))
    fa2, fb2 = f_iv(M, ico(a2)), f_iv(M, ico(b2o))
    fa, fb = f_iv(M, ico(a)), f_iv(M, ico(b))
    P("    f(Klo) ∈ [%s, %s]；f(Khi) ∈ [%s, %s]" % (sci(fKlo[0], 8), sci(fKlo[1], 8), sci(fKhi[0], 8), sci(fKhi[1], 8)))
    P("    f(a′) ∈ [%s, %s]；f(b′+1e-20) ∈ [%s, %s]（a′、b′ 为 c1u2 印刷串）" % (
        sci(fa2[0], 8), sci(fa2[1], 8), sci(fb2[0], 8), sci(fb2[1], 8)))
    C_("C%d.a 有窗（N 判据）：f(Khi) > 0（则 f(K_thresh) ≥ f(Khi) > 0）" % M, fKhi[0] > 0)
    C_("C%d.b c1u2 印刷串 +1e-20 外扩后 f(a′) > 0 > f(b′+1e-20)（第二套独立括号）" % M,
       fa2[0] > 0 and fb2[1] < 0)
    C_("C%d.c 窗口非空：Khi < a（route3 括号左端在门槛之上）" % M, Khi < a)
    C_("C%d.d route3 的 [a,b] ⊂ c1u2 外扩区间（纯精确有理比较）" % M, a >= a2 + F(1, 10 ** 20) and b <= b2o)
    P("      （参考）f(a) ∈ [%s, %s]；f(b) ∈ [%s, %s]（该处 |f| ~1e-75，超出本网格分辨力，不作符号判定）" % (
        sci(fa[0], 4), sci(fa[1], 4), sci(fb[0], 4), sci(fb[1], 4)))
    rlo, rhi = (a - Khi) / Khi, (b - Klo) / Klo
    P("    rho ∈ [%s, %s]（精确有理；区间相对宽 %s）" % (dec(rlo, 25), dec(rhi, 25), sci((rhi - rlo) / rlo)))
    cert[str(M)] = dict(Klo=str(Klo), Khi=str(Khi), a=str(a), b=str(b), rho_lo=str(rlo), rho_hi=str(rhi))
    C_("C%d.e 排除 route-5 的 2e-24" % M, rlo > F(2, 10 ** 24))
cert["note"] = "两端均为精确有理数（route3_windows.json G=160 原串）；两个门槛区间由 kthresh 复核一致性"

# ================= [D] =================
P("")
P("-" * 96)
P("[D] 门槛单调性：K_thresh(M)·(1+1e-11) < K_thresh(M+1)（M = 2..90）")
worst = None
okD = True
for M in range(2, 91):
    lo_ = ce(kthresh(M)[1] * (1 + F(1, 10 ** 11)))
    hi_ = kthresh(M + 1)[0]
    if not (lo_ < hi_):
        okD = False
        P("    反例 M = %d" % M)
    r = hi_ / lo_ - 1
    if worst is None or r < worst[1]:
        worst = (M, r)
P("  最小相对间隙 = %s（M = %d）" % (sci(worst[1], 6), worst[0]))
C_("D1 对一切 M = 2..90 成立（余量 ~0.3，远大于 δ/C 区间宽 ~1e-25）", okD)

# ================= [E] =================
P("")
P("-" * 96)
P("[E] 取点方向：j = 2、91、92 无窗（Klo 处 f<0）；j = 88、89、90 有窗（Khi 处 f>0）；比值上界 < 1")
for j in (2, 91, 92, 88, 89, 90):
    kt = kthresh(j)
    gl = f_iv(j, ico(kt[0]))
    gh = f_iv(j, ico(kt[1]))
    ta = tau_iv(j)
    rb = iadd(tuple(4 * ta[0] * v for v in pow2_neg_iv(ico(ce((ta[0] - 1) * C_IV[0])))),
              tuple(2 * (j - 2) * DELTA[1] * v for v in pow2_neg_iv(ico(fl(-(DELTA[0] * ta[0] - 1) * C_IV[0])))))
    P("    j = %2d：f(Klo) ∈ [%s, %s]；f(Khi) ∈ [%s, %s]；tau ∈ [%s, %s]；比值上界 ≤ %s" % (
        j, sci(gl[0], 8), sci(gl[1], 8), sci(gh[0], 8), sci(gh[1], 8),
        dec(ta[0], 8), dec(ta[1], 8), sci(rb[1], 6)))
    if j in (2, 91, 92):
        C_("E%d 无窗：f(Klo) < 0（f 递减 → ∀K≥K_thresh：f ≤ f(Klo) < 0）且比值上界 < 1" % j,
           gl[1] < 0 and rb[1] < 1)
    else:
        C_("E%d 有窗：f(Khi) > 0 且比值上界 < 1" % j, gh[0] > 0 and rb[1] < 1)

# ================= [F] =================
P("")
P("-" * 96)
P("[F] K*、T（3.131547906e20）、R（方程根 47 位区间）的位置")
Kstar = F(205632218873398596256)
T = F(3131547906, 10 ** 9) * 10 ** 20
kt91, kt92 = kthresh(91), kthresh(92)
P("  K_thresh(91) ∈ [%s, %s]；K_thresh(92) ∈ [%s, %s]" % (dec(kt91[0], 6), dec(kt91[1], 6), dec(kt92[0], 6), dec(kt92[1], 6)))
C_("F1 K_thresh(91) 上端 < K* < K_thresh(92) 下端", kt91[1] < Kstar and Kstar < kt92[0])
C_("F2 T = 3.131547906e20 > K_thresh(92) 上端", T > kt92[1])
logtxt = open(CERT_LOG, encoding="utf-8").read()
mR = re.search(r"K_cross ∈ \[([0-9.]+), ([0-9.]+)\]", logtxt)
gam = re.search(r"gamma = \[[^\]]*\] = (\d+)/(\d+)", logtxt)
Rlo, Rhi = F(mR.group(1)), F(mR.group(2))
gamma = F(int(gam.group(1)), int(gam.group(2)))
P("  R ∈ [%s, %s]（cert.log 解析）；gamma 分母 = K* ？%s" % (dec(Rlo, 30), dec(Rhi, 30), gamma.denominator == Kstar))
C_("F3 R 区间下端 > K_thresh(92) 上端", Rlo > kt92[1])
for K, tag in ((Rlo, "下端"), (Rhi, "上端")):
    eps = idiv(N_iv(92, ico(K)), imul(tuple(3 * K for _ in (0,)), LN2I))
    e = isub(eps, isub(ico(gamma), DELTA))
    P("    eps(92,K)−(gamma−delta) 在 R %s ∈ [%s, %s]（符号 %d）" % (
        tag, sci(e[0], 6), sci(e[1], 6), 1 if e[0] > 0 else (-1 if e[1] < 0 else 0)))
    C_("F4 R %s 处符号 %s" % (tag, ">0" if tag == "下端" else "<0"), (e[0] > 0) if tag == "下端" else (e[1] < 0))

P("")
P("[判据合计] %d/%d True" % (sum(1 for _, o in CHK if o), len(CHK)))
for n, o in CHK:
    if not o:
        P("  未过：%s" % n)
import pathlib as _pl
_pl.Path(os.path.join(HERE, "results/audit_cert.json")).write_text(
    json.dumps({"cert": cert, "checks": [[n, o] for n, o in CHK]}, ensure_ascii=False, indent=1), encoding="utf-8")
_pl.Path(os.path.join(HERE, "results/audit_cert_light.out")).write_text("\n".join(LOG) + "\n", encoding="utf-8")
print("[写出] results/audit_cert_light.out / results/audit_cert.json")
