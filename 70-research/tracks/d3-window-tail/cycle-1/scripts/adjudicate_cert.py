#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""裁决员独立严格有理区间证书（自写，不 import 项目脚本；scratch 落在轨道 scripts/ 下以便实跑）。
机制：Fraction 精确四则 + atanh 级数（显式几何尾界）+ exp 阶乘级数（显式尾界，含 k=N 首项），
每步向外取整到 40 位有效数字（有界分母）。
目标：(b) 三格窗口两端的严格有理区间 + 独立 mpmath 二分对照；
(c) K* 与 K_cross 窗口外判定；(a) 门槛处全 91 档符号扫描。
"""
from fractions import Fraction as F
from decimal import Decimal, getcontext
import math, time, sys
import mpmath as mp
sys.set_int_max_str_digits(1000000)
getcontext().prec = 45
mp.mp.dps = 120

t0 = time.time()
X0 = 695 * 2**60
Q = F(162 * X0, 97)               # 2^C 精确
SIG = 60
N_AT = 55
N_EX = 50

def snap(x, up):
    """向外取整到 40 位有效数字（有界分母）。"""
    if x == 0:
        return x
    ax = x if x > 0 else -x
    e = math.floor(math.log10(ax.numerator) - math.log10(ax.denominator)) - 1
    while ax >= 10**(e+1): e += 1
    while ax < 10**e: e -= 1
    sh = SIG - 1 - e
    q = F(1, 10**sh) if sh >= 0 else F(10**(-sh), 1)
    n = x / q
    k = -((-n.numerator) // n.denominator) if up else (n.numerator // n.denominator)
    return k * q

def iv_add(a, b): return (a[0] + b[0], a[1] + b[1])
def iv_sub(a, b): return (a[0] - b[1], a[1] - b[0])
def iv_mul(a, b):
    p = [a[0]*b[0], a[0]*b[1], a[1]*b[0], a[1]*b[1]]
    return (snap(min(p), False), snap(max(p), True))
def iv_div(a, b):
    assert b[0] > 0
    return (snap(a[0]/b[1], False), snap(a[1]/b[0], True))

def atanh_iv(x):
    slo = F(0); shi = F(0); plo = x; phi = x
    for k in range(N_AT):
        slo += plo / (2*k + 1)
        shi += phi / (2*k + 1)
        plo = snap(plo * x * x, False)
        phi = snap(phi * x * x, True)
    # 余项 sum_{k>=N} x^{2k+1}/(2k+1) <= x^{2N+1}/((2N+1)(1-x^2))
    tail = snap(snap(phi / (2*N_AT + 1), True) / (1 - x*x), True)
    return (slo, shi + tail)

ln2h = atanh_iv(F(1, 3)); LN2 = (2*ln2h[0], 2*ln2h[1])
ln3h = atanh_iv(F(1, 5)); LN3 = (LN2[0] + 2*ln3h[0], LN2[1] + 2*ln3h[1])
DELTA = iv_div(LN3, LN2)
lnwh = atanh_iv(F(6631, 105959))
CIV = (60 + snap(snap(10*LN2[0] + 2*lnwh[0], False) / LN2[1], False),
       60 + snap(snap(10*LN2[1] + 2*lnwh[1], True) / LN2[0], True))

def fm(x, n=30):
    if isinstance(x, F):
        return mp.nstr(mp.mpf(x.numerator) / mp.mpf(x.denominator), n)
    return str(x)

print("[0] C ∈ [%s,\n        %s]" % (fm(CIV[0]), fm(CIV[1])))
print("    δ ∈ [%s, %s]" % (fm(DELTA[0]), fm(DELTA[1])))
print("    C 相对宽 = %.3e；δ 相对宽 = %.3e" % (float((CIV[1]-CIV[0])/CIV[0]), float((DELTA[1]-DELTA[0])/DELTA[0])))
mp.mp.dps = 120
C_mp = mp.log(mp.mpf(162*X0)/97)/mp.log(2)
print("    C_mp 在区间内？", mp.mpf(CIV[0].numerator)/CIV[0].denominator <= C_mp <= mp.mpf(CIV[1].numerator)/CIV[1].denominator)

def exp_pos_iv(z):
    """e^z，z ∈ [0, 0.9]。"""
    slo = F(0); shi = F(0); tlo = F(1); thi = F(1)
    for k in range(N_EX):
        slo += tlo; shi += thi
        tlo = snap(tlo * z[0] / (k+1), False)
        thi = snap(thi * z[1] / (k+1), True)
    tail = snap(thi / (1 - z[1]/(N_EX+1)), True)   # 含 k=N 项的正确余项界
    return (slo, shi + tail)

def exp_iv(zlo, zhi):
    if zlo >= 0:
        return exp_pos_iv((zlo, zhi))
    if zhi <= 0:
        E = exp_pos_iv((-zhi, -zlo))
        return (snap(1/E[1], False), snap(1/E[0], True))
    raise AssertionError("混合符号未用")

def iv_2pow(vlo, vhi):
    def one(v):
        n = v.numerator // v.denominator
        t = v - n
        z = iv_mul((t, t), LN2)
        E = exp_iv(z[0], z[1])
        return (snap(F(2)**n * E[0], False), snap(F(2)**n * E[1], True))
    return (one(vlo)[0], one(vhi)[1])

def ln_iv_one(w):
    k = 0
    while F(2)**k > w: k -= 1
    while F(2)**(k+1) <= w: k += 1
    r = w / F(2)**k
    u = (r - 1) / (r + 1)
    a = atanh_iv(u)
    if k >= 0:
        return (snap(k*LN2[0] + 2*a[0], False), snap(k*LN2[1] + 2*a[1], True))
    return (snap(k*LN2[1] + 2*a[0], False), snap(k*LN2[0] + 2*a[1], True))

def iv_neg_pow2(slo, shi):
    def one(s):
        n = s.numerator // s.denominator
        w = s - n
        z = iv_sub((F(0), F(0)), iv_mul((w, w), LN2))
        E = exp_iv(z[0], z[1])
        return (snap(E[0] / F(2)**n, False), snap(E[1] / F(2)**n, True))
    return (one(shi)[0], one(slo)[1])

def iv_pow_neg_delta(X):
    """X^{-δ} = 2^{-δ·log2 X} = 2^{-δ·ln X / ln 2}。"""
    l = ln_iv_one(X[0]); h = ln_iv_one(X[1])
    slo = snap(snap(DELTA[0]*l[0], False) / LN2[1], False)
    shi = snap(snap(DELTA[1]*h[1], True) / LN2[0], True)
    return iv_neg_pow2(slo, shi)

POWDELTA = [(F(1), F(1))]
for i in range(1, 93):
    POWDELTA.append(iv_mul(POWDELTA[-1], DELTA))
DELTA1 = iv_sub(DELTA, (F(1), F(1)))

def geom_iv(M):
    return iv_div(iv_sub(POWDELTA[M], (F(1), F(1))), DELTA1)

def c_iv(M):
    return iv_mul(iv_mul((F(92, M), F(92, M)), geom_iv(M)), CIV)

def A_exact(M):
    if M == 92: return F(0)
    if M == 91: return F(3, X0)
    return F(97*(92 - M) + 73, 54*X0)

def phi_iv(M, K):
    dM = iv_sub(POWDELTA[M], (F(1), F(1)))
    dM1 = iv_sub(POWDELTA[M-1], (F(1), F(1)))
    vM = iv_div(iv_mul(iv_mul((F(M, 92), F(M, 92)), (K, K)), DELTA1), dM)
    vM1 = iv_div(iv_mul(iv_mul((F(M-1, 92), F(M-1, 92)), (K, K)), DELTA1), dM1)
    XM = iv_sub(iv_2pow(vM[0], vM[1]), (F(1), F(1)))
    XM1 = iv_sub(iv_2pow(vM1[0], vM1[1]), (F(1), F(1)))
    t2M = iv_div((F(3), F(3)), XM); t2M1 = iv_div((F(3), F(3)), XM1)
    t3M = iv_mul((F(3*(M-1)), F(3*(M-1))), iv_pow_neg_delta(XM))
    t3M1 = iv_mul((F(3*(M-2)), F(3*(M-2))), iv_pow_neg_delta(XM1))
    Ad = A_exact(M) - A_exact(M-1)
    return iv_add((Ad, Ad), iv_add(iv_sub(t2M, t2M1), iv_sub(t3M, t3M1)))

def sign_of(iv):
    if iv[0] > 0: return +1
    if iv[1] < 0: return -1
    return 0

# 原语自检（参照 route-1 A7/A4 的公开值）
t2selft = iv_div((F(3), F(3)), (Q-1, Q-1))
qselft = iv_pow_neg_delta((Q-1, Q-1))
print("    自检 3/(2^C−1) ∈ [%s, %s]（参照 2.2417822697808458321087452e-21）" % (fm(t2selft[0], 30), fm(t2selft[1], 30)))
print("    自检 (2^C−1)^(−δ) ∈ [%s, %s]（参照 3.2752588393539008250538605e-34）" % (fm(qselft[0], 30), fm(qselft[1], 30)))

print("\n[1] 左端 K_th(M)（M = 88..92）")
for M in (88, 89, 90, 91, 92):
    c = c_iv(M)
    print("  K_th(%d) ∈ [%s, %s]  相对宽 %.3e" % (M, fm(c[0]), fm(c[1]), float((c[1]-c[0])/c[0])))
print("  时间 %.1f 秒" % (time.time()-t0))

delta_mp = mp.log(3)/mp.log(2)
def geom_mp(M):
    s = mp.mpf(0); p = mp.mpf(1)
    for _ in range(M):
        s += p; p *= delta_mp
    return s
def phi_mp(M, K):
    v = K * M / (92 * geom_mp(M)); vp = K * (M-1) / (92 * geom_mp(M-1))
    b2 = mp.power(2, v) - 1; b2p = mp.power(2, vp) - 1
    if M == 92: Ad = -3/mp.mpf(X0)
    elif M == 91: Ad = 3/mp.mpf(X0) - (97*2+73)/(54*mp.mpf(X0))
    else: Ad = -97/(54*mp.mpf(X0))
    return Ad + 3/b2 - 3/b2p + 3*(M-1)*mp.power(b2, -delta_mp) - 3*(M-2)*mp.power(b2p, -delta_mp)

print("\n[2] 三格窗口：两端严格有理区间 + 独立二分")
for M in (88, 89, 90):
    c = c_iv(M)
    lo = c[0]
    hi = snap(c[1] * (1 + F(1, 10**10)), True)
    s_lo = sign_of(phi_iv(M, lo)); s_hi = sign_of(phi_iv(M, hi))
    steps = 0
    while (hi - lo)/lo > F(1, 10**45) and steps < 200:
        mid = (lo + hi)/2
        s = sign_of(phi_iv(M, mid))
        assert s != 0, "不可判"
        if s > 0: lo = mid
        else: hi = mid
        steps += 1
    mlo = mp.mpf(lo.numerator)/lo.denominator; mhi = mp.mpf(hi.numerator)/hi.denominator
    for _ in range(400):
        mm = (mlo + mhi)/2
        if phi_mp(M, mm) > 0: mlo = mm
        else: mhi = mm
    mroot = (mlo+mhi)/2
    fl_ = lo/c[1] - 1; fh = hi/c[0] - 1
    print("  M = %d：门槛处 Φ>0 %s；hi 处 Φ<0 %s；二分 %d 步；相对宽 %.3e" %
          (M, s_lo > 0, s_hi < 0, steps, float((hi-lo)/lo)))
    print("     K₁ ∈ [%s,\n           %s]" % (fm(lo, 45), fm(hi, 45)))
    print("     f* ∈ [%s,\n           %s]" % (fm(fl_, 30), fm(fh, 30)))
    print("     f* 括号相对宽 = %.3e" % float((fh - fl_)/fl_))
    print("     独立 mpmath 根 = %s；在括号内？ %s" %
          (mp.nstr(mroot, 30), mp.mpf(lo.numerator)/lo.denominator <= mroot <= mp.mpf(hi.numerator)/hi.denominator))
print("  时间 %.1f 秒" % (time.time()-t0))

print("\n[2b] 与各路报告值的机器比对（包含性）")
claims = {
 88: {"f": "7.622396965265262225804740254e-13",
      "K1": "50126425533409882371.60427791037362289396",
      "ext": []},
 89: {"f": "7.714617758586982140404811955e-13",
      "K1": "78555824936819382091.47530961864025893883",
      "ext": []},
 90: {"f": "7.806771365412671715788394707e-13",
      "K1": "123124614107652692133.00723179560208072177",
      "ext": [("r4b2（转引 d3r3_audit.out:46）",
               "123124614107652692133.007231711933058876044901",
               "123124614107652692133.007231919710646726095849"),
              ("证书A（转引 d3r3_audit.out:43）",
               "123124614107652692133.00719033138608916063",
               "123124614107652692133.00726031962620707253")]},
}
for M in (88, 89, 90):
    c = c_iv(M)
    lo = c[0]; hi = snap(c[1] * (1 + F(1, 10**10)), True)
    st = 0
    while (hi - lo)/lo > F(1, 10**45) and st < 200:
        mid = (lo + hi)/2
        s = sign_of(phi_iv(M, mid)); assert s != 0
        if s > 0: lo = mid
        else: hi = mid
        st += 1
    fclaim = F(Decimal(claims[M]["f"]))
    kclaim = F(Decimal(claims[M]["K1"]))
    fl_ = lo/c[1] - 1; fh = hi/c[0] - 1
    def off(x, a, b):
        return F(0) if a <= x <= b else (x - a if x < a else x - b)
    of_ = off(fclaim, fl_, fh); ok_ = off(kclaim, lo, hi)
    print("  M = %d：报告 f* 相对本括号偏移 %.3e（本括号 f* 相对宽 %.3e）；报告 K₁ 相对偏移 %.3e" %
          (M, float(of_/fclaim), float((fh-fl_)/fl_), float(ok_/kclaim)))
    print("        报告 f* 在括号内？ %s；报告 K₁ 在括号内？ %s" % (fl_ <= fclaim <= fh, lo <= kclaim <= hi))
    for name, a, b in claims[M]["ext"]:
        A_ = F(Decimal(a)); B_ = F(Decimal(b))
        print("        %s：与本括号相交？ %s；本括号含于其内？ %s" %
              (name, lo <= B_ and A_ <= hi, A_ <= lo and hi <= B_))
print("  时间 %.1f 秒" % (time.time()-t0))

print("\n[3] 门槛处全 91 档符号扫描")
pos = []; neg = []; und = []
for M in range(2, 93):
    c = c_iv(M)
    s = sign_of(phi_iv(M, (c[0]+c[1])/2))
    (pos if s > 0 else neg if s < 0 else und).append(M)
print("  正号档 = %s 至 %s（%d 档）" % (pos[0], pos[-1], len(pos)))
print("  负号档 =", neg)
print("  未定档 =", und)
print("  时间 %.1f 秒" % (time.time()-t0))

print("\n[4] 半直线上界与 f0 统一界")
lnQ1 = ln_iv_one(Q - 1)
q1nd = iv_neg_pow2(snap(snap(DELTA[0]*lnQ1[0], False) / LN2[1], False),
                   snap(snap(DELTA[1]*lnQ1[1], True) / LN2[0], True))
t2Q = iv_div((F(3), F(3)), (Q-1, Q-1))
b91 = iv_add((A_exact(91)-A_exact(90),)*2, iv_add(t2Q, iv_mul((F(270), F(270)), q1nd)))
b92 = iv_add((A_exact(92)-A_exact(91),)*2, iv_add(t2Q, iv_mul((F(273), F(273)), q1nd)))
print("  一切 x≥1：G_91 ≤ %s < 0 ？ %s" % (fm(b91[1]), b91[1] < 0))
print("  一切 x≥1：G_92 ≤ %s < 0 ？ %s" % (fm(b92[1]), b92[1] < 0))
f0 = F(1, 10**12)
v0 = iv_mul(CIV, (f0, f0))
q2v = iv_2pow(v0[0], v0[1])
bterm = iv_div((F(3), F(3)), iv_sub(iv_mul((Q, Q), q2v), (F(1), F(1))))
for Mt in (90, 111, 112):
    bM = iv_add((F(-97, 54*X0),)*2, iv_add(bterm, iv_mul((F(3*(Mt-1)), F(3*(Mt-1))), q1nd)))
    print("  f ≥ f0 时 G_%d ≤ %s（<0 ？ %s）" % (Mt, fm(bM[1]), bM[1] < 0))
c90u = snap(c_iv(90)[1] * (1 + f0), True)
print("  c_90(1+f0) 上界 = %s" % fm(c90u))
print("  c_90(1+f0) < K* ？ %s" % (c90u < 205632218873398596256))
mono_ok = all(c_iv(M)[1] < c_iv(M+1)[0] for M in range(2, 92))
print("  门槛严格递增（两两区间分离）？", mono_ok)
print("  c_91 上界 < K* < c_92 下界 ？ %s / %s" %
      (c_iv(91)[1] < 205632218873398596256, 205632218873398596256 < c_iv(92)[0]))
Kcross_lo = F(Decimal("313195478959172262876.6365306194907065260231016940260118526233"))
print("  K_cross 下端 > c_92 上界 ？ %s" % (Kcross_lo > c_iv(92)[1]))
print("  时间 %.1f 秒" % (time.time()-t0))
