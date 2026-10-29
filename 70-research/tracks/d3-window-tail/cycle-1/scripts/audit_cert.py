#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""d3-window-tail cycle-1 route-2（证书对抗审计）的独立复核脚本。

只做点值复核：不重跑任何既有脚本、不做大规模枚举、不重开二分。
  [A] C 的 float64 伪值判定（精确 float->Fraction，不经 float 中转高位数）
  [B] 第三项主导（10.7177 个数量级）与 log2(1+2^-C) 的独立复算
  [C] 窗口两端严格有理区间的点值复核（输入 route3_windows.json 的精确有理数）
  [D] 通用检查：K_thresh(M)(1+1e-11) < K_thresh(M+1)（M = 2..90）
  [E] j = 2、91、92 无窗的反向判据 / j = 88、89、90 的存在性判据（取点方向写成断言）
  [F] K*、T、R 的位置复核（R 区间取自 c2r5_cert.log，只读）

实现：decimal 定向区间（ROUND_FLOOR/ROUND_CEILING，prec=60，逐运算外扩 30 ulp）
      + mpmath(dps=60) 对照。判定全部为区间符号判定或精确有理数比较。
"""
from decimal import Decimal as D, localcontext, ROUND_FLOOR, ROUND_CEILING, getcontext
from fractions import Fraction as F
import json, math, re, hashlib, os

getcontext().prec = 260
PREC = 120
ULPS = 30
ROOT = "/Users/luna/Documents/math IA/collatz-attack"
U1 = os.path.join(ROOT, "70-research/tracks/undefined/cycle-1")
JSON_IN = os.path.join(U1, "scripts/results/route3_windows.json")
C1U2_OUT = os.path.join(U1, "scripts/results/c1u2_window_cert.out")
CERT_LOG = os.path.join(ROOT, "70-research/cycle-2/scripts/results/c2r5_cert.log")
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = []


def P(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s)


def rnd(x, mode, prec=PREC):
    with localcontext() as c:
        c.prec = prec
        c.rounding = mode
        return +x


def ulp(x, prec=PREC):
    if x == 0:
        return D(10) ** (-prec)
    return D(10) ** (x.adjusted() - prec + 1)


def dn(x, prec=PREC):
    t = rnd(x, ROUND_FLOOR, prec)
    return t - ULPS * ulp(t, prec)


def up(x, prec=PREC):
    t = rnd(x, ROUND_CEILING, prec)
    return t + ULPS * ulp(t, prec)


def dval(fr):
    return D(fr.numerator) / D(fr.denominator)


class IV:
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi

    @classmethod
    def ex(cls, x, prec=PREC):
        if isinstance(x, F):
            return cls(dn(dval(x), prec), up(dval(x), prec))
        return cls(dn(D(x), prec), up(D(x), prec))

    def __add__(self, o):
        o = o if isinstance(o, IV) else IV.ex(o)
        return IV(dn(self.lo + o.lo), up(self.hi + o.hi))

    def __sub__(self, o):
        o = o if isinstance(o, IV) else IV.ex(o)
        return IV(dn(self.lo - o.hi), up(self.hi - o.lo))

    def __mul__(self, o):
        o = o if isinstance(o, IV) else IV.ex(o)
        ps = [self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi]
        return IV(dn(min(ps)), up(max(ps)))

    def __truediv__(self, o):
        o = o if isinstance(o, IV) else IV.ex(o)
        assert o.lo > 0
        ps = [self.lo / o.lo, self.lo / o.hi, self.hi / o.lo, self.hi / o.hi]
        return IV(dn(min(ps)), up(max(ps)))

    def __neg__(self):
        return IV(-self.hi, -self.lo)

    def w(self):
        return self.hi - self.lo

    def sign(self):
        return 1 if self.lo > 0 else (-1 if self.hi < 0 else 0)


def iv_ln(a):
    assert a.lo > 0
    return IV(dn(a.lo.ln()), up(a.hi.ln()))


def iv_exp(a):
    return IV(dn(a.lo.exp()), up(a.hi.exp()))


def iv_pow(a, b):
    return iv_exp(b * iv_ln(a))


X0 = 695 * 2 ** 60
M_M = 92
LN2 = iv_ln(IV.ex(2))
DELTA = iv_ln(IV.ex(3)) / LN2
C_IV = IV.ex(60) + iv_ln(IV.ex(F(112590, 97))) / LN2


def A_of(m2):
    if m2 == M_M:
        return IV.ex(0)
    if m2 == M_M - 1:
        return IV.ex(F(3, X0))
    return IV.ex(F(97 * (M_M - m2) + 73, 54 * X0))


def v_of(m2, K):
    return IV.ex(F(m2, M_M)) * K * (DELTA - IV.ex(1)) / (ipow_iv(DELTA, m2) - IV.ex(1))


def N_of(m2, K):
    v = v_of(m2, K)
    t = iv_pow(IV.ex(2), v) - IV.ex(1)
    return A_of(m2) + IV.ex(3) / t + IV.ex(3 * (m2 - 1)) / iv_pow(t, DELTA)


def f_of(M, K):
    return N_of(M, K) - N_of(M - 1, K)


def ipow_iv(a, n):
    """整数幂（平方求幂，降向/升向各自定向）。"""
    lo = D(1)
    hi = D(1)
    base_lo, base_hi = a.lo, a.hi
    while n:
        if n & 1:
            lo, hi = dn(lo * base_lo), up(hi * base_hi)
        base_lo, base_hi = dn(base_lo * base_lo), up(base_hi * base_hi)
        n >>= 1
    return IV(lo, hi)


def kthresh(m2):
    geom = (ipow_iv(DELTA, m2) - IV.ex(1)) / (DELTA - IV.ex(1))
    return IV.ex(F(M_M, m2)) * geom * C_IV


def tau_of(t):
    pm = ipow_iv(DELTA, t)
    pm1 = ipow_iv(DELTA, t - 1)
    return IV.ex(F(t - 1, t)) * (pm - IV.ex(1)) / (pm1 - IV.ex(1))


def mono_ratio_ub(t):
    """L2 型比值上界：4 tau 2^{-(tau-1)v} + 2(t-2) delta 2^{(1-delta tau)v}，取 v = C_lo、tau = tau_lo。"""
    ta = tau_of(t)
    e1 = IV.ex(4) * ta.lo * iv_exp(-(ta.lo - D(1)) * C_IV.lo * LN2.lo)
    e2 = IV.ex(2 * (t - 2)) * DELTA.hi * iv_exp((D(1) - DELTA.lo * ta.lo) * C_IV.lo * LN2.lo)
    return e1 + e2


def decs(x, n=30):
    """Decimal/Fraction 的 n 位小数截断展示。"""
    y = D(x) if not isinstance(x, F) else dval(x)
    s = y.scaleb(n).to_integral_value(rounding=ROUND_FLOOR)
    neg = s < 0
    s = abs(s)
    out = "%d.%s" % (int(s) // 10 ** n, str(int(s) % 10 ** n).rjust(n, "0"))
    return ("-" if neg else "") + out


def sci(x, k=12):
    y = D(x) if not isinstance(x, F) else dval(x)
    if y == 0:
        return "0"
    s = "-" if y < 0 else ""
    y = abs(y)
    e = 0
    while y >= 10:
        y /= 10
        e += 1
    while y < 1:
        y *= 10
        e -= 1
    m = y.scaleb(k - 1).to_integral_value(rounding=ROUND_FLOOR)
    return "%s%d.%s e%+d" % (s, int(m) // 10 ** (k - 1), str(int(m) % 10 ** (k - 1)).rjust(k - 1, "0"), e)


def relw(x, y):
    return dval(x) / dval(y)


CHK = []


def C_(name, ok, det=""):
    CHK.append((name, bool(ok)))
    P("  [判据] %s -> %s   %s" % (name, bool(ok), det))


P("=" * 96)
P("audit_cert.py：d3-window-tail cycle-1 route-2 独立复核（定向 decimal 区间 + mpmath 对照）")
P("输入 md5（只读）：")
for pth in (JSON_IN, C1U2_OUT, CERT_LOG):
    P("  %s  %s" % (hashlib.md5(open(pth, "rb").read()).hexdigest(), pth))
P("常量（本脚本自算，定向区间 prec=%d 外扩 %d ulp）：" % (PREC, ULPS))
P("  C ∈ [%s, %s]；区间宽 %s" % (decs(C_IV.lo, 40), decs(C_IV.hi, 40), sci(C_IV.w())))
P("  delta ∈ [%s, %s]；区间宽 %s" % (decs(DELTA.lo, 40), decs(DELTA.hi, 40), sci(DELTA.w())))

# ---------------- [A] ----------------
P("")
P("-" * 96)
P("[A] C 的 float64 伪值判定（真值、double 精确值、route-5 (D1) 串）")
x64 = math.log2((162 / 97) * X0)
fx = F(x64)
d64 = D(fx.numerator) / D(fx.denominator)
P("  float64(C) 的精确值 = %s" % format(d64, "f"))
C_("A1 float64(C) 精确展开 = audit_c 记录的串", format(d64, "f") ==
  "70.180806328308364072654512710869312286376953125")
D1 = F(701808063283083640726545127109, 10 ** 28)
r28u = F(D(d64).quantize(D(1).scaleb(-28), rounding="ROUND_HALF_UP"))
r28d = F(D(d64).quantize(D(1).scaleb(-28), rounding="ROUND_DOWN"))
P("  (D1) 串 = %s；double 的 28 位截断 = %s" % (decs(D1, 28), decs(r28d, 28)))
C_("A2 (D1) = double 值在第 28 位小数四舍五入（半进位）", r28u == D1)
C_("A3 (D1) ≠ double 的 28 位截断（(D1) 只能是舍入写法）", r28d != D1)
gap = C_IV - IV.ex(D1)
P("  C 下界 − (D1) = %s（差值区间宽 %s）" % (sci(gap.lo, 6), sci(gap.w())))
C_("A4 严格：C 下界 − (D1) > 1e-28（连「28 位截断相容」都不成立）", gap.lo > D(10) ** -28)
C_("A5 真值 C 与 (D1) 之差 ≈ 2.7522e-15", D("2.75e-15") < gap.lo and gap.hi < D("2.76e-15"))
alt = ((60.0 + math.log2(695.0)) + math.log2(162.0)) - math.log2(97.0)
falt = F(alt)
P("  第二路 float64：60+log2 695+log2 162−log2 97 = %s" % format(D(falt.numerator) / D(falt.denominator), "f"))
C_("A6 第二路 float64 与第一路不同（(D1) 串只能来自第一路写法）", falt != fx)
import mpmath as mp
mp.mp.dps = 60
C_mp = 60 + mp.log(mp.mpf(112590) / 97) / mp.log(2)
P("  mpmath(dps=60) C = %s" % mp.nstr(C_mp, 34))
v_mp = D(mp.nstr(C_mp, 55))
diff_mp = abs(v_mp - C_IV.lo)
P("  与 C 区间下端的差 = %s（mpmath dps=60 自身误差 ~1e-58；nstr 55 位舍入 ~5e-55）" % sci(diff_mp, 4))
C_("A7 mpmath(dps=60) 与本脚本 C 区间一致到 1e-54（同精度口径：不要求 55 位串落在 1e-56 区间内）",
  diff_mp < D(10) ** -54)
C_("A8 C 区间不含 (D1) 值", not (C_IV.lo <= dval(D1) <= C_IV.hi))

# ---------------- [B] ----------------
P("")
P("-" * 96)
P("[B] 门槛处三项分解与第三项主导（10.7177 个数量级）")
twoC = iv_pow(IV.ex(2), C_IV)
T2 = IV.ex(3) / (twoC - IV.ex(1))
P("  3/(2^C−1) ∈ [%s, %s]" % (sci(T2.lo), sci(T2.hi)))
P("  97/(54X0) = 3·2^{−C} 精确 = %s" % sci(F(97, 54 * X0)))
P1 = T2 - IV.ex(F(97, 54 * X0))
P("  P1 := 3/(2^C−1) − 97/(54X0) ∈ [%s, %s]（route-5 只比了这两项）" % (sci(P1.lo), sci(P1.hi)))
C_("B1 P1 ∈ (1.675e-42, 1.676e-42)（与 audit_c 的 1.67519591503e-42 一致）",
  D("1.675e-42") < P1.lo and P1.hi < D("1.676e-42"))
T3 = {}
for j in (88, 89, 90):
    T3[j] = IV.ex(3 * (j - 1)) / iv_pow(twoC - IV.ex(1), DELTA)
    P("  第三项 3·%d/(2^C−1)^delta ∈ [%s, %s]" % (j - 1, sci(T3[j].lo), sci(T3[j].hi)))
C_("B2 第三项(90) ∈ (8.7449e-32, 8.7450e-32)（与 audit_c 一致）",
  D("8.7449e-32") < T3[90].lo and T3[90].hi < D("8.7450e-32"))
rat = T3[90].lo / P1.hi
lg = iv_ln(IV.ex(rat)) / iv_ln(IV.ex(10))
P("  第三项(90)/P1 ∈ [%s, %s]；log10 ∈ [%s, %s]" % (
    sci(rat), sci(T3[90].hi / P1.lo), decs(lg.lo, 6), decs(lg.hi, 6)))
C_("B3 5.22e10 < 第三项/P1 < 5.23e10（10.7177 个数量级）",
  rat > D("5.22e10") and T3[90].hi / P1.lo < D("5.23e10"))
C_("B3b log10(第三项/P1) ∈ (10.71, 10.72)", D("10.71") < lg.lo and lg.hi < D("10.72"))
u = IV.ex(1) / twoC
l2c = iv_ln(IV.ex(1) + u) / LN2
P("  log2(1+2^{−C}) ∈ [%s, %s]（route-5 写 1.5e-22）" % (sci(l2c.lo), sci(l2c.hi)))
C_("B4 log2(1+2^{−C}) ∈ (1.0780e-21, 1.0781e-21)", D("1.0780e-21") < l2c.lo and l2c.hi < D("1.0781e-21"))
C_("B5 1.5e-22 < log2(1+2^{−C}) 下界（route-5 值被排除，差约 7.19 倍）", D("1.5e-22") < l2c.lo)
q2c = IV.ex(F(97, 162)) / IV.ex(X0)
P("  2^{−C} = 97/(162X0) ∈ [%s, %s]（route-5 的「相对量 ≈7.4e-22」相容）" % (sci(q2c.lo), sci(q2c.hi)))
C_("B6 2^{−C} ∈ (7.47e-22, 7.48e-22)", D("7.47e-22") < q2c.lo and q2c.hi < D("7.48e-22"))

# ---------------- [C] ----------------
P("")
P("-" * 96)
P("[C] 窗口两端严格有理区间复核（route3_windows.json G=160；c1u2 印刷串做第二套外扩）")
js = json.load(open(JSON_IN, encoding="utf-8"))
G160 = js["160"]
c1u2_txt = open(C1U2_OUT, encoding="utf-8").read()
c1u2_br = {}
for mm in re.finditer(r"二分 \d+ 步：K1\((\d+)\) ∈ \[([0-9.]+), ([0-9.]+)\]", c1u2_txt):
    c1u2_br[int(mm.group(1))] = (F(D(mm.group(2))), F(D(mm.group(3))))
C_("C0 c1u2 印刷端点解析到 3 档（88、89、90）", set(c1u2_br) == {88, 89, 90})
cert = {}
for M in (88, 89, 90):
    Klo, Khi = F(G160[str(M)]["Klo"]), F(G160[str(M)]["Khi"])
    a, b = F(G160[str(M)]["a"]), F(G160[str(M)]["b"])
    fa, fb = f_of(M, IV.ex(a)), f_of(M, IV.ex(b))
    myK = kthresh(M)
    a2, b2 = c1u2_br[M]
    fa2 = f_of(M, IV.ex(a2))
    fb2 = f_of(M, IV.ex(b2 + F(1, 10 ** 20)))
    P("  --- M = %d ---" % M)
    P("    JSON 门槛 ∈ [%s, %s]（相对宽 %s）" % (decs(Klo, 20), decs(Khi, 20), sci(relw(Khi - Klo, Klo))))
    P("    本脚本门槛 ∈ [%s, %s]（相对宽 %s）" % (decs(myK.lo, 20), decs(myK.hi, 20),
                                                sci(myK.w() / myK.lo)))
    C_("C%d.a 本脚本门槛区间与 JSON 门槛区间相交且两端相对差 < 1e-40（两者皆为包含区间的一致性检查）" % M,
      max(Klo, F(myK.lo)) <= min(Khi, F(myK.hi)) and abs(myK.lo - dval(Klo)) < D(10) ** -40 * myK.lo)
    P("    f(%d,a) ∈ [%s, %s]；f(%d,b) ∈ [%s, %s]" % (M, sci(fa.lo), sci(fa.hi), M, sci(fb.lo), sci(fb.hi)))
    C_("C%d.b 严格 f(a) > 0 > f(b)（K1 ∈ (a,b) 的点值证书）" % M, fa.lo > 0 and fb.hi < 0)
    C_("C%d.c 窗口非空：门槛上端 Khi < a（a 处 f>0 且 K_thresh ≤ Khi）" % M, Khi < a)
    C_("C%d.d c1u2 印刷串 +1e-20 外扩后 f(a′)>0 且 f(b′+1e-20)<0" % M, fa2.lo > 0 and fb2.hi < 0)
    C_("C%d.e route3 的 [a,b] 落在 c1u2 印刷串外扩区间内" % M, a >= a2 + F(1, 10 ** 20) and b <= b2)
    rlo, rhi = (a - Khi) / Khi, (b - Klo) / Klo
    P("    rho ∈ [%s, %s]（区间相对宽 %s）" % (decs(rlo, 25), decs(rhi, 25), sci(relw(rhi - rlo, rlo))))
    P("    K1 区间相对宽 %s；门槛区间相对宽 %s" % (sci(relw(b - a, a)), sci(relw(Khi - Klo, Klo))))
    cert[str(M)] = dict(Klo=str(Klo), Khi=str(Khi), a=str(a), b=str(b),
                        rho_lo=str(rlo), rho_hi=str(rhi))
cert["note"] = "K1 区间 [a,b] 与门槛区间 [Klo,Khi] 均为精确有理数（route3_windows.json G=160 原串）；两端符号由本脚本独立判定"

# ---------------- [D] ----------------
P("")
P("-" * 96)
P("[D] 通用检查：K_thresh(M)·(1+1e-11) < K_thresh(M+1)（M = 2..90；把 L3 界升级为「一切窗口在相邻门槛之间」）")
worst = None
okD = True
for M in range(2, 91):
    lo_ = kthresh(M).hi * (D(1) + D(10) ** -11)
    hi_ = kthresh(M + 1).lo
    if not (lo_ < hi_):
        okD = False
        P("    反例：M = %d" % M)
    r = hi_ / lo_ - 1
    if worst is None or r < worst[1]:
        worst = (M, r)
P("    最小相对间隙 = %s（在 M = %d 处）" % (sci(worst[1]), worst[0]))
C_("D1 对一切 M = 2..90：K_thresh(M)(1+1e-11) < K_thresh(M+1)", okD)

# ---------------- [E] ----------------
P("")
P("-" * 96)
P("[E] 取点方向写成断言：j = 2、91、92 无窗（Klo 处 f<0）；j = 88、89、90 有窗（Khi 处 f>0）")
for j in (2, 91, 92, 88, 89, 90):
    kt = kthresh(j)
    g_lo = f_of(j, kt.lo)
    g_hi = f_of(j, kt.hi)
    rb = mono_ratio_ub(j)
    P("    j = %2d：f(Klo) 上界 = %s；f(Khi) 下界 = %s；单调比值上界 = %s" % (
        j, sci(g_lo.hi, 8), sci(g_hi.lo, 8), sci(rb.hi, 6)))
    if j in (2, 91, 92):
        C_("E%d 无窗：f(Klo) < 0（则 f(K_thresh) ≤ f(Klo) < 0）且比值上界 < 1" % j,
          g_lo.hi < 0 and rb.hi < 1)
    else:
        C_("E%d 有窗：f(Khi) > 0（则 f(K_thresh) ≥ f(Khi) > 0）且比值上界 < 1" % j,
          g_hi.lo > 0 and rb.hi < 1)

# ---------------- [F] ----------------
P("")
P("-" * 96)
P("[F] K*、T（3.131547906e20）、R（方程根 47 位区间）的位置复核")
Kstar = F(205632218873398596256)
T = F(3131547906, 10 ** 9) * 10 ** 20
kt91, kt92 = kthresh(91), kthresh(92)
P("  K_thresh(91) ∈ [%s, %s]；K_thresh(92) ∈ [%s, %s]" % (
    decs(kt91.lo, 16), decs(kt91.hi, 16), decs(kt92.lo, 16), decs(kt92.hi, 16)))
C_("F1 K_thresh(91) 上端 < K* < K_thresh(92) 下端", kt91.hi < D(Kstar) and D(Kstar) < kt92.lo)
C_("F2 T = 3.131547906e20 > K_thresh(92) 上端", dval(T) > kt92.hi)
logtxt = open(CERT_LOG, encoding="utf-8").read()
mR = re.search(r"K_cross ∈ \[([0-9.]+), ([0-9.]+)\]", logtxt)
gam = re.search(r"gamma = \[[^\]]*\] = (\d+)/(\d+)", logtxt)
Rlo, Rhi = F(D(mR.group(1))), F(D(mR.group(2)))
P("  R ∈ [%s, %s]（c2r5_cert.log 解析，只读）" % (decs(Rlo, 32), decs(Rhi, 32)))
C_("F3 R 区间下端 > K_thresh(92) 上端", dval(Rlo) > kt92.hi)
gamma = F(int(gam.group(1)), int(gam.group(2)))
P("  gamma = %s（分母 = K* ？%s；gcd = 1 ？%s）" % (gamma, gamma.denominator == Kstar,
                                                    math.gcd(gamma.numerator, gamma.denominator) == 1))
for K, tag in ((Rlo, "下端"), (Rhi, "上端")):
    e = N_of(92, IV.ex(K)) / (IV.ex(3) * IV.ex(K) * LN2) - (IV.ex(gamma) - DELTA)
    P("    eps(92,K)−(gamma−delta) 在 R %s ∈ [%s, %s]（符号 %d）" % (
        tag, sci(e.lo, 6), sci(e.hi, 6), e.sign()))
    C_("F4 R %s：eps(92,·)−(gamma−delta) %s 0" % (tag, ">" if tag == "下端" else "<"),
      (e.lo > 0) if tag == "下端" else (e.hi < 0))

P("")
P("[判据合计] %d/%d True" % (sum(1 for _, o in CHK if o), len(CHK)))
for n, o in CHK:
    if not o:
        P("  未过：%s" % n)
import pathlib as _pl
_pl.Path(os.path.join(HERE, "audit_cert.json")).write_text(
    json.dumps({"cert": cert, "checks": [[n, o] for n, o in CHK],
                "C_iv": [str(C_IV.lo), str(C_IV.hi)], "delta_iv": [str(DELTA.lo), str(DELTA.hi)]},
               ensure_ascii=False, indent=1), encoding="utf-8")
_pl.Path(os.path.join(HERE, "audit_cert.out")).write_text("\n".join(LOG) + "\n", encoding="utf-8")
print("[写出] audit_cert.out / audit_cert.json")
