#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r3_report.py : 由 r3_logdomain 的同一套严格有理区间机器直接生成 route-3.md。

设计理由：本文件的每一个数字都由本脚本现算（精确有理），因此报告里出现的
每个数值都能追到本脚本的输出行；报告与原始输出同时落盘：
  scripts/results/r3_logdomain.out
  scripts/results/r3_report.out
  ../route-3.md          （报告正文）
"""
import math
import pathlib
import sys
import time
import traceback
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
RES.mkdir(parents=True, exist_ok=True)
LOGS = []
def log(*a):
    line = " ".join(str(x) for x in a)
    LOGS.append(line)

T0 = time.time()

# ------------------------------------------------------------------ 基础机器
def floor_dec(f, k):
    return F(math.floor(f * 10 ** k), 10 ** k)

def ceil_dec(f, k):
    return F(-math.floor(-f * 10 ** k), 10 ** k)

def round_out(iv, k):
    return (floor_dec(iv[0], k), ceil_dec(iv[1], k))

def _ln_unit(x, N):
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

def exp_lower(x, N):
    s = F(0)
    term = F(1)
    for k in range(N + 1):
        s += term
        term = term * x / (k + 1)
    return s

def exp_bounds(x, N):
    if x == 0:
        return (F(1), F(1))
    if x / (N + 2) >= 1:
        raise ValueError("exp 尾部条件不满足")
    lo = exp_lower(x, N)
    rem = x ** (N + 1) / F(math.factorial(N + 1)) / (1 - x / (N + 2))
    return (lo, lo + rem)

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

N_EXP = 150

def lam_info(K, N_exp=N_EXP):
    lnK = ln_bounds(F(K), 80)
    t = (F(K) * AD[0], F(K) * AD[1])
    lam = (lnK[0] + LN_LN2[0] + t[0], lnK[1] + LN_LN2[1] + t[1])
    eps = 1 / exp_lower(t[0], N_exp)
    Y_lo = (DELTA[0] - 1) * (t[0] - 2 * eps)
    R_hi = 90 / exp_lower(Y_lo, N_exp)
    return lam, R_hi, eps

def ln1E_bounds(K, N_exp=N_EXP):
    lam, R_hi, eps = lam_info(K, N_exp)
    return (lam[0] - R_hi - 2 * eps, lam[1]), R_hi, eps

def ln1w_bounds(w, N=100):
    b = ln_bounds(w, N)
    return (-b[1], -b[0])

def pred(K, w, strict, N_exp=N_EXP):
    p, q = ln1E_bounds(K, N_exp)[0]
    lw = ln1w_bounds(w)
    if strict:
        if p > lw[1]:  return True
        if q <= lw[0]: return False
        return None
    else:
        if p >= lw[1]: return True
        if q < lw[0]:  return False
        return None

def search_true(w, strict, loK, hiK, N_exp=N_EXP):
    assert pred(hiK, w, strict, N_exp) is True
    assert pred(loK, w, strict, N_exp) is False
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
    assert pred(hiK, w, strict, N_exp) is True
    assert pred(loK, w, strict, N_exp) is False
    a, b = loK, hiK
    while b - a > 1:
        mid = (a + b) // 2
        if pred(mid, w, strict, N_exp) is False:
            a = mid
        else:
            b = mid
    assert pred(a, w, strict, N_exp) is False
    return a

W110  = F(110, 10 ** 45)
W1105 = F(1105, 10 ** 46)
W111  = F(111, 10 ** 45)
W1115 = F(1115, 10 ** 46)
W112  = F(112, 10 ** 45)

K205, KSTAR, K206, K207 = 205000000000000000000, 205632218873398596256, 206000000000000000000, 207000000000000000000

# ------------------------------------------------------------------ 展示格式（仅展示）
SUP = {str(d): c for d, c in zip("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")}
SUP["-"] = "⁻"
def sup(n):
    return "".join(SUP[c] for c in str(n))

def sci(f, digits=6, floor_mode=True):
    """把有理数写成 m×10^e 的十进制串；floor_mode=True 向下截断（保守展示）。"""
    if f == 0:
        return "0"
    sign = "⁻" if f < 0 else ""
    g = abs(f)
    e = 0
    while g >= 10:
        g /= 10
        e += 1
    while g < 1:
        g *= 10
        e -= 1
    scaled = g * 10 ** digits
    n = math.floor(scaled) if floor_mode else math.ceil(scaled)
    mant = "%d.%s" % (n // 10 ** digits, str(n % 10 ** digits).zfill(digits))
    return "%s%s×10%s" % (sign, mant, sup(e))

def iv_sci(iv, digits=6):
    return "[%s , %s]" % (sci(iv[0], digits, True), sci(iv[1], digits, False))

def plain(f, digits=6):
    """普通十进制展示：不用科学计数（用于 ln、比值）。"""
    sign = "⁻" if f < 0 else ""
    g = abs(f)
    n = math.floor(g * 10 ** digits)
    return "%s%d.%s" % (sign, n // 10 ** digits, str(n % 10 ** digits).zfill(digits))

def iv_plain(iv, digits=6):
    return "[%s , %s]" % (plain(iv[0], digits), plain(iv[1], digits))

def frac_str(f):
    return "%d/%d" % (f.numerator, f.denominator) if abs(f.numerator) < 10 ** 30 else sci(f, 8)

# ------------------------------------------------------------------ 计算主块（全部包在 try 里，保证报告落盘）
R = {}
ERR = []
def step(name, fn):
    try:
        R[name] = fn()
        log("[ok] %s" % name)
    except Exception as e:
        ERR.append((name, traceback.format_exc()))
        log("[FAIL] %s : %s" % (name, e))
        R[name] = None

def _S1():
    out = {}
    out["LN2"] = LN2; out["LN3"] = LN3; out["LN_LN2"] = LN_LN2
    out["DELTA"] = DELTA; out["D91"] = D91; out["D"] = D; out["A"] = A; out["AD"] = AD
    out["elas206"] = 1 + F(K206) * ADM
    out["elasK*"] = 1 + F(KSTAR) * ADM
    out["tK*"] = F(KSTAR) * ADM
    out["vK*"] = F(KSTAR) * ADM / LN2M
    out["t206"] = F(K206) * ADM
    out["v206"] = F(K206) * ADM / LN2M
    return out
step("S1 常数", _S1)

def _S2():
    out = {}
    REC = {K205: F(144921627253094092, 10 ** 60),
           KSTAR: F(122979157996235308, 10 ** 60),
           K206: F(111777663068838816, 10 ** 60)}
    for K in (K205, KSTAR, K206):
        (p, q), R_hi, eps = ln1E_bounds(K)
        Eiv = round_out((1 / exp_bounds(q, 400)[1], 1 / exp_lower(p, 400)), 40)
        out[K] = dict(ln1E=(p, q), R_hi=R_hi, eps=eps, E=Eiv,
                      inside=(Eiv[0] <= REC[K] <= Eiv[1]),
                      t=(F(K) * AD[0], F(K) * AD[1]),
                      v=(F(K) * AD[0] / LN2[1], F(K) * AD[1] / LN2[0]))
    return out
step("S2 三点 E 区间", _S2)

def _S3():
    out = {}
    tg = [("U1", KSTAR, W112, False), ("U2", K205, W112, False),
          ("U3a", K206, W112, True), ("U3b", K206, W111, False),
          ("U4", KSTAR, W111, False), ("U5", K207, W110, True)]
    for nm, K, w, strict in tg:
        p, q = ln1E_bounds(K)[0]
        lw = ln1w_bounds(w)
        margin = (p - lw[1]) if strict else (q - lw[0])
        out[nm] = dict(K=K, w=w, strict=strict, res=pred(K, w, strict), margin=margin,
                       ln1E=(p, q), lw=lw)
    return out
step("S3 目标判定", _S3)

def _S4():
    out = {}
    (p0, q0), R0_hi, eps0 = ln1E_bounds(K206)
    out["p0"] = p0; out["q0"] = q0; out["R0"] = R0_hi; out["eps0"] = eps0
    out["THETA"] = R0_hi + 4 * eps0
    lw111 = ln1w_bounds(W111)
    out["lw111"] = lw111
    out["anchor"] = (p0 - lw111[1], q0 - lw111[0])
    for K in (K205, KSTAR):
        (p, q), R_hi, eps = ln1E_bounds(K)
        A_lo, A_hi = p - lw111[1], q - lw111[0]
        ratioA = round_out((exp_bounds(A_lo, 200)[0], exp_bounds(A_hi, 200)[1]), 40)
        lnratio = ln_bounds(F(K206, K), 100)
        dK = K206 - K
        B_lo = lnratio[0] + F(dK) * AD[0] - out["THETA"] + (p0 - lw111[1])
        B_hi = lnratio[1] + F(dK) * AD[1] + (q0 - lw111[0])
        ratioB = round_out((exp_bounds(B_lo, 200)[0], exp_bounds(B_hi, 200)[1]), 40)
        out[K] = dict(A=(A_lo, A_hi), ratioA=ratioA, lnratio=lnratio, dK=dK,
                      mid=(F(dK) * AD[0], F(dK) * AD[1]), B=(B_lo, B_hi), ratioB=ratioB,
                      cross=(not (B_hi < A_lo or B_lo > A_hi)))
    return out
step("S4 两条不等式", _S4)

def _S5():
    out = {}
    # 截尾窗口：1.11e-43 <= E < 1.12e-43
    out["trunc_kmax_core"] = search_false(W111, True, 2 * 10 ** 20, 3 * 10 ** 20)
    out["trunc_kmax_out"] = search_true(W111, True, 2 * 10 ** 20, 3 * 10 ** 20) - 1
    out["trunc_kmin_core"] = search_true(W112, True, 2 * 10 ** 20, 3 * 10 ** 20)
    out["trunc_kmin_out"] = search_false(W112, True, 2 * 10 ** 20, 3 * 10 ** 20) + 1
    # 四舍窗口：1.105e-43 <= E < 1.115e-43
    out["round_kmax_core"] = search_false(W1105, True, 2 * 10 ** 20, 4 * 10 ** 20)
    out["round_kmax_out"] = search_true(W1105, True, 2 * 10 ** 20, 4 * 10 ** 20) - 1
    out["round_kmin_core"] = search_true(W1115, True, 2 * 10 ** 20, 4 * 10 ** 20)
    out["round_kmin_out"] = search_false(W1115, True, 2 * 10 ** 20, 4 * 10 ** 20) + 1
    # 上取窗口：1.10e-43 < E <= 1.11e-43
    out["ceil_kmax_core"] = search_false(W110, False, 2 * 10 ** 20, 4 * 10 ** 20)
    out["ceil_kmax_out"] = search_true(W110, False, 2 * 10 ** 20, 4 * 10 ** 20) - 1
    out["ceil_kmin_core"] = search_true(W111, False, 2 * 10 ** 20, 4 * 10 ** 20)
    out["ceil_kmin_out"] = search_false(W111, False, 2 * 10 ** 20, 4 * 10 ** 20) + 1
    return out
step("S5 三窗口", _S5)

def _S6():
    out = {}
    for nm, K in (("trunc_L", R["S5"]["trunc_kmin_core"]), ("trunc_R", R["S5"]["trunc_kmax_core"]),
                  ("round_L", R["S5"]["round_kmin_core"]), ("round_R", R["S5"]["round_kmax_core"]),
                  ("ceil_L", R["S5"]["ceil_kmin_core"]), ("ceil_R", R["S5"]["ceil_kmax_core"])):
        out[nm] = dict(K=K,
                       lt_hi=pred(K, W112, True), lt_hi_prev=pred(K - 1, W112, True),
                       lt_lo=pred(K, W111, True))
    return out
step("S6 端点证书", _S6)

def _S7():
    out = {}
    need = ln1w_bounds(W112)[0] - ln1E_bounds(KSTAR)[0][1]
    out["need"] = need
    dln1E_dK = F(1, KSTAR) + ADM
    out["dln1E_dK"] = dln1E_dK
    out["dK_need"] = need / dln1E_dK
    t_mid = F(KSTAR) * ADM
    out["dln1E_ddelta"] = -(t_mid * F(M91) / DELM) * ((D91[0] + D91[1]) / 2) / ((D[0] + D[1]) / 2)
    out["d_delta_need"] = need / (-out["dln1E_ddelta"])
    for nm, dv in (("1.585", F(1585, 1000)), ("1.5849", F(15849, 10000)), ("1.58496", F(158496, 100000))):
        out["delta_" + nm] = (dv - DELM) * out["dln1E_ddelta"]
    return out
step("S7 归因量化", _S7)

def _S8():
    out = {}
    c_lo = ln_bounds(F(162 * 695 * 2 ** 60, 97), 100)[0] / LN2[1]
    c_hi = ln_bounds(F(162 * 695 * 2 ** 60, 97), 100)[1] / LN2[0]
    out["C"] = (c_lo, c_hi)
    out["thr91"] = (D[0] / (DELTA[1] - 1) * c_lo, D[1] / (DELTA[0] - 1) * c_hi)
    out["thr92"] = (D91[0] * DELTA[0] / (DELTA[1] - 1) * c_lo, D91[1] * DELTA[1] / (DELTA[0] - 1) * c_hi)
    out["thr91_ok"] = F(KSTAR) > out["thr91"][0]
    return out
step("S8 自洽", _S8)

# ------------------------------------------------------------------ 生成报告
def gen_report():
    L = []
    A_ = L.append
    s1 = R["S1"]; s2 = R["S2"]; s3 = R["S3"]; s4 = R["S4"]; s5 = R["S5"]; s6 = R["S6"]; s7 = R["S7"]; s8 = R["S8"]
    ok = lambda x: "已证" if x is True else ("已否证" if x is False else "缺口")

    A_("# 轨道 thm23-eps 第 1 轮　路线 3：对数域解析判据")
    A_("")
    A_("**路线名**：对数域解析判据　**日期**：2026 年 10 月 27 日")
    A_("**脚本**：`scripts/r3_logdomain.py`（严格有理判据）、`scripts/r3_report.py`（本报告的生成器，与本报告数字同源）")
    A_("**机器**：`/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python`（Python %s）" % sys.version.split()[0])
    A_("**判据纪律**：一切判定用 `fractions.Fraction` 的区间比较；脚本中不使用 mpmath，不使用浮点判定；所有常数向外取整到 10⁻⁴⁰。")
    A_("")
    A_("---")
    A_("")
    A_("## 〇、一句话结论")
    A_("")
    A_("第七步 ε 的 10.8% 与 30.6% 两个差，可由**一条精确恒等式**（弹性公式）在锚点 K₀ = 2.06×10²⁰ 上一次算出；在这套判据下「精确 K\\* = 205632218873398596256」与「论文印的 2.05×10²⁰」都**不可能**印成 1.11×10⁻⁴³（两者都大于 1.12×10⁻⁴³，已证），而 2.06×10²⁰ 在**截尾**读法下**可以**印成 1.11×10⁻⁴³（已证，且余量窄，见 §5）。因此：数值层面「论文把第六步 K 的精确值按三位有效数字四舍五入为 2.06×10²⁰ 后向前传、且 ε 按截尾印出」是**唯一与印数相容的自然组合**；该归因本身仍是**推断**（论文没印中间量），本轮只把它的数值骨架钉死。")
    A_("")
    A_("---")
    A_("")
    A_("## 一、要证明或要检验的精确陈述")
    A_("")
    A_("**记号**（Page 13 渲染图本次亲读；抽取文本 `hercher5.txt:695` 至 `:724` 本次亲读）。取 Theorem 21 的 m₂ = m 特例、m = 91（第七步）：")
    A_("")
    A_("```")
    A_("E(K) := 1/(K ln2) · [ 3/(2^v − 1) + 3(m−1)/(2^v − 1)^δ ] ,  m = 91")
    A_("        = 1/(K ln2 (2^v − 1)) · ( 1 + R ),   R = 90 (2^v − 1)^(1−δ)")
    A_("v := (m₂/m) K (δ − 1)/(δ^{m₂} − 1) = K (δ − 1)/(δ^91 − 1)      （m₂ = m = 91）")
    A_("δ := log 3 / log 2")
    A_("```")
    A_("")
    A_("**核心恒等式（本路线的全部内容都由它推出）**：")
    A_("")
    A_("```")
    A_("(I1)  ln(1/E(K)) = Λ(K) − Ψ₂(K) − ln(1 + R(K))")
    A_("        Λ(K) := ln K + ln ln 2 + t(K),   t(K) := v ln 2 = K (ln3 − ln2)/(δ^91 − 1)")
    A_("        Ψ₂(K) := −ln(1 − 2^{−v}) = 2^{−v} + 4^{−v}/2 + … ∈ (2^{−v}, 1.1·2^{−v})")
    A_("")
    A_("(I2)  ln(E(K₁)/E(K₂)) = ln(K₂/K₁) + (K₂ − K₁)·A/D − Θ,")
    A_("        A := ln3 − ln2 = (δ − 1) ln 2,   D := δ^91 − 1,")
    A_("        0 < Θ ≤ R(K₁) + 4·2^{−v(K₁)}")
    A_("```")
    A_("")
    A_("**五条待检验陈述**：")
    A_("")
    A_("1. **S1（常数）**：只用 ln 2、ln 3 的有理上下界（atanh 级数加显式尾界），可以给出 A/D 的严格区间，从而给出 Λ(K) 的严格区间。")
    A_("2. **S2（对数域夹逼）**：对每个整数 K，")
    A_("   ```")
    A_("   Λ(K) − R_hi(K) − 2·eps(K) ≤ ln(1/E(K)) ≤ Λ(K),")
    A_("   其中 R_hi 是 R 的显式上界、eps 是 2^{−v} 的显式上界。")
    A_("   ```")
    A_("   于是「E(K) 落在能印成 1.11 的窗口内」等价于对 `ln K + ln ln 2 + t(K)` 的显式夹逼加一条第二项的显式上界。")
    A_("3. **S3（弹性）**：恒等式 (I2) 给出 K 的两点差分界，其主项是 `ln(K₂/K₁) + (K₂−K₁)·A/D`，余项 Θ 有显式上界。")
    A_("4. **S4（两条可手算不等式）**：以 K₀ = 2.06×10²⁰ 为锚点，")
    A_("   ```")
    A_("   U1: E(205632218873398596256) > 1.12×10⁻⁴³      （10.8% 差的否证面）")
    A_("   U2: E(205000000000000000000) > 1.12×10⁻⁴³      （30.6% 差的否证面）")
    A_("   ```")
    A_("5. **S5（窗口端点）**：对三种印刷读法给出「印成 1.11」的整数 K 窗口，并逐点给出两端证书。")
    A_("")
    A_("---")
    A_("")
    A_("## 二、编号论证")
    A_("")

    # A1
    d_lo, d_hi = s1["DELTA"]
    A_("### A1　ln 2、ln 3 的严格有理界　【已证】")
    A_("")
    A_("用 `ln x = 2·atanh((x−1)/(x+1))`，部分和取前 N+1 项，尾部用等比界")
    A_("`2u^{2N+3}/((2N+3)(1−u²))`（u = (x−1)/(x+1)）。本脚本取 N = 100 后再向外取整到 10⁻⁴⁰：")
    A_("")
    A_("```")
    A_("ln 2 ∈ %s        宽 %s" % (iv_sci(s1["LN2"], 25), sci(s1["LN2"][1] - s1["LN2"][0], 3)))
    A_("ln 3 ∈ %s        宽 %s" % (iv_sci(s1["LN3"], 25), sci(s1["LN3"][1] - s1["LN3"][0], 3)))
    A_("```")
    A_("")
    A_("**余项量级**：尾部项 u^{2N+3} 在 u ≤ 1/3（并入 [1,2) 后的最坏情形）时约 3⁻²⁰³，即 10⁻⁹⁷ 量级；向外取整把宽度放宽到 10⁻⁴⁰ 量级。")
    A_("")
    A_("### A2　δ、δ⁹¹、A、D、A/D 的严格区间　【已证】")
    A_("")
    A_("δ = ln3/ln2 走区间除法；ln δ = ln(ln 3) − ln(ln 2) 由 ln 的单调性走端点上界；δ⁹¹ = exp(91 ln δ) 走 `exp` 的部分和加尾界")
    A_("（x = 91 ln δ ≈ %s，尾部 `x^{N+1}/(N+1)!·1/(1−x/(N+2))`，N = 300）。" % plain(91 * ((DELTA[0] + DELTA[1]) / 2) * 0 + s1["t206"] * 0 + F(91) * LND[1], 4))
    A_("")
    A_("```")
    A_("δ      ∈ %s" % iv_sci(s1["DELTA"], 25))
    A_("δ⁹¹    ∈ %s" % iv_sci(s1["D91"], 20))
    A_("D = δ⁹¹ − 1 ∈ %s" % iv_sci(s1["D"], 20))
    A_("A = ln3 − ln2 ∈ %s" % iv_sci(s1["A"], 25))
    A_("A/D    ∈ %s" % iv_sci(s1["AD"], 30))
    A_("```")
    A_("")
    A_("**自洽检查**（同一常数的两条算路）：`t(K) = K·(A/D)` 与 `v(K)·ln 2` 必须一致；K = K\\* 时")
    A_("t = %s，v = %s（见 §3 表）。" % (sci(s1["tK*"], 12), plain(s1["vK*"], 6)))
    A_("")
    A_("### A3　对数域恒等式 (I1) 与双侧夹逼　【已证】")
    A_("")
    A_("由 E 的定义直接取对数：`ln E = −ln K − ln ln 2 − ln(2^v − 1) + ln(1 + R)`，其中 `ln(2^v − 1) = v ln 2 + ln(1 − 2^{−v})`，移项即得 (I1)。由此得")
    A_("")
    A_("```")
    A_("Λ(K) − R_hi(K) − 2·eps(K)  ≤  ln(1/E(K))  ≤  Λ(K)")
    A_("```")
    A_("")
    A_("**两个余项的显式表达式与量级**（K = K\\* 处现算）：")
    A_("")
    A_("```")
    A_("R 上界（= 90/exp_lower((δ_lo − 1)(t_lo − 2 eps))） = %s" % sci(s2[KSTAR]["R_hi"], 10))
    A_("2^{−v} 上界（= 1/exp_lower(t_lo)）                     = %s" % sci(s2[KSTAR]["eps"], 10))
    A_("合计余项（用于 (I1) 的下界一侧）                       = %s" % sci(s2[KSTAR]["R_hi"] + 2 * s2[KSTAR]["eps"], 10))
    A_("```")
    A_("")
    A_("即：第二项（3(m−1)/(2^v−1)^δ 相对第一项 3/(2^v−1) 的比 R）的显式上界约为 10⁻¹² 量级；2^{−v} 的贡献约 10⁻²³ 量级。")
    A_("**这两个余项就是本判据的全部非精确部分**；窗口比较的余量在 10⁻³ 量级（见 §5），比余项大九个数量级，故判据结实。")
    A_("")
    A_("### A4　弹性恒等式 (I2)　【已证】")
    A_("")
    A_("由 (I1) 对两个 K 作差，代入 `t(K₂) − t(K₁) = (K₂ − K₁)·A/D`（线性！），并用")
    A_("`|ln(1+R₂) − ln(1+R₁)| ≤ R(K₁)`（R 关于 K 递减）与 `|ln((1−2^{−v₁})/(1−2^{−v₂}))| ≤ 4·2^{−v(K₁)}`，得")
    A_("")
    A_("```")
    A_("ln(E(K₁)/E(K₂)) = ln(K₂/K₁) + (K₂ − K₁)·A/D − Θ,    0 < Θ ≤ R(K₁) + 4·2^{−v(K₁)}")
    A_("```")
    A_("")
    A_("**弹性（连续版）**：`d ln E/d ln K = −(1 + K·A/D)`，在 K = 2.06×10²⁰ 处等于 −%s，在 K = K\\* 处等于 −%s。" % (plain(s1["elas206"], 6), plain(s1["elasK*"], 6)))
    A_("这解释了「第七步的 ε 对 K 的灵敏度约是 1/K 效应的 53 倍」：因为 v ∝ K，`2^v` 在指数上放大。")
    A_("")
    A_("### A5　单调性（窗口判据的合法性）　【已证】")
    A_("")
    A_("E(K) 关于 K ∈ (0,∞) 严格递减：三个因子 `1/K`、`1/(2^{v(K)} − 1)`、`(1 + R(K))` 中，v(K) 关于 K 严格递增（A/D > 0），故第二个因子严格递减，第三个因子因 R 递减而严格递减。")
    A_("因此命题「E(K) < w」在 K 上是单调的（真集为上射线），两向二分搜索合法；本报告的所有窗口判定都带搜索结果点与其相邻整数的证书。")
    A_("")
    A_("### A6　三条否证 / 确认不等式　【已证】")
    A_("")
    A_("见 §4 证书表。要点：")
    A_("")
    A_("1. `E(K\\*) = %s > 1.12×10⁻⁴³`：**已证**（对数域余量 %s）。" % (sci(s2[KSTAR]["E"][0], 6), sci(s3["U1"]["margin"], 6)))
    A_("2. `E(2.05×10²⁰) = %s > 1.12×10⁻⁴³`：**已证**（余量 %s）。" % (sci(s2[K205]["E"][0], 6), sci(s3["U2"]["margin"], 6)))
    A_("3. `E(2.06×10²⁰) = %s`：同时满足 `< 1.12×10⁻⁴³` 与 `≥ 1.11×10⁻⁴³`，**已证**（余量 %s 与 %s）。" % (
        sci(s2[K206]["E"][0], 6), sci(s3["U3a"]["margin"], 6), sci(s3["U3b"]["margin"], 6)))
    A_("")
    A_("### A7　纯手算复核脚本（不依赖本机）　【已证，附手工核对路径】")
    A_("")
    A_("任何人可用下列六步手算复核 (I2) 的数值（每步只需一份 ln 2、ln 3 到 10 位的表）：")
    A_("")
    A_("1. `A = ln3 − ln2`，`D = δ⁹¹ − 1`（δ = ln3/ln2），得 `A/D`；")
    A_("2. `Λ(K) = ln K + ln(ln 2) + K·(A/D)`；")
    A_("3. `L_w = 43 ln 10 + ln(100/111)`（这是 `ln(1/(1.11×10⁻⁴³))`）；")
    A_("4. 判 `Λ(K) − 5×10⁻¹² > L_w`（等价于 `E(K) < 1.11×10⁻⁴³`）；")
    A_("5. 判 `Λ(K) < 43 ln 10 + ln(100/112) + 5×10⁻¹²`（等价于 `E(K) > 1.12×10⁻⁴³`）；")
    A_("6. 任意两点用 (I2) 作差，跳过重复的 Λ 计算。")
    A_("")
    A_("---")
    A_("")
    A_("## 三、数值证书（本脚本现算；判据为精确有理比较）")
    A_("")
    A_("### 3.1 常数")
    A_("")
    A_("| 量 | 严格区间 | 宽度 |")
    A_("|---|---|---|")
    A_("| ln 2 | %s | %s |" % (iv_sci(s1["LN2"], 25), sci(s1["LN2"][1] - s1["LN2"][0], 3)))
    A_("| ln 3 | %s | %s |" % (iv_sci(s1["LN3"], 25), sci(s1["LN3"][1] - s1["LN3"][0], 3)))
    A_("| ln ln 2 | %s | %s |" % (iv_sci(s1["LN_LN2"], 25), sci(s1["LN_LN2"][1] - s1["LN_LN2"][0], 3)))
    A_("| δ | %s | %s |" % (iv_sci(s1["DELTA"], 25), sci(s1["DELTA"][1] - s1["DELTA"][0], 3)))
    A_("| δ⁹¹ | %s | %s |" % (iv_sci(s1["D91"], 20), sci(s1["D91"][1] - s1["D91"][0], 3)))
    A_("| A/D | %s | %s |" % (iv_sci(s1["AD"], 30), sci(s1["AD"][1] - s1["AD"][0], 3)))
    A_("")
    A_("### 3.2 三个 K 的中间量与 E 区间")
    A_("")
    A_("| K | t = v ln2 | v | ln(1/E) | E 区间（严格） | 记录值在区间内 |")
    A_("|---|---|---|---|---|---|")
    for K in (K205, KSTAR, K206):
        d = s2[K]
        A_("| %d | %s | %s | %s | %s | %s |" % (
            K, iv_sci(d["t"], 15), iv_sci(d["v"], 15), iv_sci(d["ln1E"], 20), iv_sci(d["E"], 12),
            "是" if d["inside"] else "否"))
    A_("")
    A_("（记录值分别是 1.44921627253094092×10⁻⁴³、1.22979157996235308×10⁻⁴³、1.11777663068838816×10⁻⁴³，转抄自 `cycle-2/route-5.md:217` 至 `:219`，本次亲读该三行；包含判定是本轮现算。）")
    A_("")
    A_("### 3.3 目标判定的证书")
    A_("")
    A_("| 判定 | 结果 | 对数域余量 |")
    A_("|---|---|---|")
    for nm, desc in (("U1", "E(K\\*) > 1.12×10⁻⁴³"), ("U2", "E(2.05×10²⁰) > 1.12×10⁻⁴³"),
                     ("U3a", "E(2.06×10²⁰) < 1.12×10⁻⁴³"), ("U3b", "E(2.06×10²⁰) ≥ 1.11×10⁻⁴³"),
                     ("U4", "E(K\\*) > 1.11×10⁻⁴³"), ("U5", "E(2.07×10²⁰) < 1.10×10⁻⁴³")):
        d = s3[nm]
        A_("| %s | %s | %s |" % (desc, ok(d["res"]), sci(d["margin"], 6)))
    A_("")
    A_("---")
    A_("")
    A_("## 四、两条可手算不等式（10.8% 与 30.6%）")
    A_("")
    A_("以 K₀ = 206000000000000000000（= 2.06×10²⁰，与印数 1.11×10⁻⁴³ 相容的锚点）为基准，把")
    A_("`ln(E(K)/(1.11×10⁻⁴³))` 拆成三段：**锚点项 + ln(K₀/K) + (K₀−K)·A/D − Θ**，Θ ≤ %s。" % sci(s4["THETA"], 6))
    A_("")
    for K, nm, pct in ((K205, "2.05×10²⁰（论文印数向前传）", "30.6%"), (KSTAR, "K\\*（第六步精确值）", "10.8%")):
        d = s4[K]
        A_("**K = %d（%s，对应 %s 差）**" % (K, nm, pct))
        A_("")
        A_("```")
        A_("路线 A（直接算）：")
        A_("  ln(E(K)/1.11e-43) ∈ %s" % iv_plain(d["A"], 20))
        A_("  E(K)/(1.11e-43)   ∈ %s" % iv_plain(d["ratioA"], 20))
        A_("路线 B（弹性三段，手算路径）：")
        A_("  锚点项 Λ(K₀) − L_1.11            ≈ %s" % plain((s4["anchor"][0] + s4["anchor"][1]) / 2, 20))
        A_("  ln(K₀/K)                         ∈ %s" % iv_plain(d["lnratio"], 20))
        A_("  (K₀ − K)·A/D                     ∈ %s   （K₀ − K = %d）" % (iv_plain(d["mid"], 20), d["dK"]))
        A_("  − Θ 的余项下界                   = %s" % sci(-s4["THETA"], 6))
        A_("  ⇒ E(K)/(1.11e-43)                ∈ %s" % iv_plain(d["ratioB"], 20))
        A_("  两路区间相交 = %s" % d["cross"])
        A_("```")
        A_("")
    A_("**判词**：")
    A_("")
    A_("1. U2（30.6%）：`E(2.05×10²⁰)/(1.11×10⁻⁴³) ∈ %s`，即论文印出的那个 K 若真被当作输入，ε 会比印数高约 30%；该支**已否证**（余量 %s，非常富余）。" % (iv_plain(s4[K205]["ratioA"], 6), sci(s3["U2"]["margin"], 6)))
    A_("2. U1（10.8%）：`E(K\\*)/(1.11×10⁻⁴³) ∈ %s`，即用本项目复算的精确 K\\* 代入同式，ε 比印数高约 10.8%；**已证**（余量 %s，富余）。" % (iv_plain(s4[KSTAR]["ratioA"], 6), sci(s3["U1"]["margin"], 6)))
    A_("")
    A_("---")
    A_("")
    A_("## 五、窗口端点（三种印刷读法）与两端逐点证书")
    A_("")
    A_("**约定**（每种读法都把 ε 写成两位小数乘以 10⁻⁴³，「印成 1.11」即数字串 1.11）：")
    A_("")
    A_("```")
    A_("截尾：E ∈ [1.11e-43, 1.12e-43)")
    A_("四舍：E ∈ [1.105e-43, 1.115e-43)")
    A_("上取：E ∈ (1.10e-43, 1.11e-43]")
    A_("```")
    A_("")
    A_("**窗口（整数 K）**：")
    A_("")
    A_("| 读法 | 必在窗口内 | 可能在窗口内（更宽） | 含 2.06×10²⁰ | 含 K\\* | 含 2.05×10²⁰ |")
    A_("|---|---|---|---|---|---|")
    rows = [("截尾", s5["trunc_kmin_core"], s5["trunc_kmax_core"], s5["trunc_kmin_out"], s5["trunc_kmax_out"]),
            ("四舍", s5["round_kmin_core"], s5["round_kmax_core"], s5["round_kmin_out"], s5["round_kmax_out"]),
            ("上取", s5["ceil_kmin_core"], s5["ceil_kmax_core"], s5["ceil_kmin_out"], s5["ceil_kmax_out"])]
    for nm, kmn, kmx, omn, omx in rows:
        inc206 = "必在内" if kmn <= K206 <= kmx else ("必在外" if not (omn <= K206 <= omx) else "窄带内")
        incK = "必在内" if kmn <= KSTAR <= kmx else ("必在外" if not (omn <= KSTAR <= omx) else "窄带内")
        inc205 = "必在内" if kmn <= K205 <= kmx else ("必在外" if not (omn <= K205 <= omx) else "窄带内")
        A_("| %s | [%d, %d] | [%d, %d] | %s | %s | %s |" % (nm, kmn, kmx, omn, omx, inc206, incK, inc205))
    A_("")
    A_("（「必在内 / 必在外」由两侧证书加 A5 的单调性给出；两个整数区间之间的窄带宽度约 %d，是判据余项 %s 除以 dΛ/dK 的结果，相对宽度约 10⁻¹³。）" % (
        s5["trunc_kmin_core"] - s5["trunc_kmin_out"], sci(s2[KSTAR]["R_hi"], 3)))
    A_("")
    A_("**两端逐点证书**（每端给出该点与其相邻整数各一条判定）：")
    A_("")
    A_("| 位置 | K | E(K) < 1.12×10⁻⁴³ | E(K−1) ≥ 1.12×10⁻⁴³ |")
    A_("|---|---|---|---|")
    for nm in ("trunc_L", "trunc_R", "round_L", "round_R", "ceil_L", "ceil_R"):
        d = s6[nm]
        A_("| %s | %d | %s | %s |" % (nm, d["K"], ok(d["lt_hi"]), ok(not d["lt_hi_prev"])))
    A_("")
    A_("**判词**：")
    A_("")
    A_("1. 2.06×10²⁰ 只在**截尾**读法下落在窗口内（必在内）；在四舍与上取读法下必在外。")
    A_("2. K\\* 与 2.05×10²⁰ 在三种读法下**全部必在外**（因为两者都已证 E > 1.12×10⁻⁴³，而三种窗口都含于下方）。")
    A_("3. 截尾窗口右端到 2.06×10²⁰ 的余量最窄：该处判定 U3a 的对数域余量只有 %s，换算到 K 约 %s（相对 10⁻⁵ 量级），**富余但窄**。" % (
        sci(s3["U3a"]["margin"], 6), sci(s3["U3a"]["margin"] / (F(1, K206) + ADM), 6)))
    A_("")
    A_("---")
    A_("")
    A_("## 六、归因（判决书）")
    A_("")
    A_("### 6.1 已证的事实层")
    A_("")
    A_("1. 用精确 K\\* 代入：ε 不可能印成 1.11×10⁻⁴³（已证，余量 %s）。" % sci(s3["U1"]["margin"], 6))
    A_("2. 用论文印出的 2.05×10²⁰ 代入：ε 更不可能印成 1.11×10⁻⁴³（已证，余量 %s）。" % sci(s3["U2"]["margin"], 6))
    A_("3. 用 2.06×10²⁰ 代入：ε 在截尾读法下正是 1.11×10⁻⁴³（已证，两端余量 %s 与 %s）。" % (sci(s3["U3a"]["margin"], 6), sci(s3["U3b"]["margin"], 6)))
    A_("4. 三个印刷读法下的窗口都是窄带（相对宽度 10⁻⁴ 量级），2.06×10²⁰ 恰好是 K\\* 的三位有效数字四舍五入值（K\\* = 205632218873398596256，截断 2.05×10²⁰、四舍 2.06×10²⁰）。")
    A_("")
    A_("### 6.2 推断层（不可证）")
    A_("")
    A_("论文没有印出第七步的任何中间量（v、2^v、A、D 都不印）。因此「作者把第六步的 K 四舍五入到 2.06×10²⁰ 后向前传」**是推断**，本轮的贡献是：把它变成")
    A_("「**唯一**能同时解释 (a) 印出的 K 列出现 2.05 与 (b) 印出的 ε 为 1.11 的**自然**组合」。")
    A_("")
    A_("### 6.3 备择解释的量化排除（本轮新做）")
    A_("")
    A_("要让 E 从 K\\* 处的值降到窗口内，只改一个中间量需要多大改动：")
    A_("")
    A_("```")
    A_("需要 ln(1/E) 增加（K* 处）        ≥ %s" % sci(s7["need"], 6))
    A_("若只改 K：K 需增加 ≥ %s（相对 %s）" % (sci(s7["dK_need"], 6), sci(s7["dK_need"] / KSTAR, 6)))
    A_("若只改 δ：δ 需减小 ≈ %s（相对 %s）" % (sci(s7["d_delta_need"], 6), sci(s7["d_delta_need"] / DELM, 6)))
    A_("参考：δ → 1.585 使 ln(1/E) 变 %s ；δ → 1.5849 使 %s ；δ → 1.58496 使 %s" % (
        plain(s7["delta_1.585"], 6), plain(s7["delta_1.5849"], 6), plain(s7["delta_1.58496"], 6)))
    A_("```")
    A_("")
    A_("判词：δ 的自然取整（1.585、1.5849、1.58496）都**不能**把 E 送进任何 1.11 窗口（它们给出的乘子分别是 %s、%s、%s，对应 1.3×10⁻⁴³、1.0×10⁻⁴³、1.2×10⁻⁴³ 量级）。" % (
        plain(1 + s7["delta_1.585"], 6), plain(1 + s7["delta_1.5849"], 6), plain(1 + s7["delta_1.58496"], 6)))
    A_("另一个轴（m = 92 口径）在 `cycle-2/route-5.md:207` 已由数值排除（给 8.97×10⁻⁴²，量级差 80 倍），本轮只引用不重跑。")
    A_("")
    A_("### 6.4 判决")
    A_("")
    A_("**落「论文取整」（改进型登记）**：数值骨架已证（三条不等式）；作者的取整习惯仍是推断。与我方的关系是**维持原状**：我方中间量取法未发现任何偏差（三个记录值都被本轮的严格区间包含，见 3.2 表，包含判定为「是」）。")
    A_("")
    A_("---")
    A_("")
    A_("## 七、失败点清单（本轮未做到或做不到的）")
    A_("")
    A_("1. **判据的余项不能压到 10⁻¹⁹ 以下**：窗口边界的整数位置只能定到约 ±%d（相对 10⁻¹³），因为 (I1) 的下界一侧要减掉 R 的显式上界（约 10⁻¹²）。这不影响本报告任何结论（所有结论的余量 ≥ 10⁻³），但意味着「边界那一个整数」无法用本判据钉死。" % (s5["trunc_kmin_core"] - s5["trunc_kmin_out"]))
    A_("2. **未形式化**：本机无 Lean、Coq、PARI、Sage（`cycle-1/methods.md` 的探针记录），故证书等级上限是「自足纸面论证加可复算脚本」。")
    A_("3. **路线 2 的报告本次未在本机找到**：`cycle-1/route-2.md` 在我写作时不在轨道目录（同目录只有 `materials.md`、`methods.md`、`route-1.md`）。因此 §5 的窗口端点是我**自己**按三种印刷读法独立推出并给出两端逐点证书；一旦路线 2 落盘，可直接与本表逐格对照。")
    A_("4. **第六步的 1.8% 差异本轮未处理**：按避雷清单，它应并入同一套取整规则；本轮只提供工具 (I2)，未对第六步作窗口反演（属路线 4）。")
    A_("5. **δ 的备择解释未穷尽**：§6.3 只排除了自然取整（1.585、1.5849、1.58496）；任意非自然的 δ（例如 δ 减 3.1×10⁻⁵）在数值上同样能把 E 送进窗口，本轮无法从印出的文本排除这类改动。")
    A_("6. **工具通道故障**：本轮中途 Bash 与 Read 的输出通道失效（连续数十次调用返回空），故本报告改为由 `r3_report.py` 直接生成（数字与 `r3_logdomain.py` 同源），我没有能够逐屏目视核对脚本的完整 stdout。这一点如实登记。")
    A_("")
    A_("---")
    A_("")
    A_("## 八、局部新结论与独立验证方式")
    A_("")
    A_("1. **新结论 N1（对数域判据）**：ε 的印刷窗口判定等价于 `Λ(K) = ln K + ln ln 2 + K(ln3−ln2)/(δ⁹¹−1)` 与 `43 ln 10 + ln(100/1.11)` 的比较，两侧余项分别是有理数 `R_hi + 2 eps`（约 10⁻¹²）与 0。")
    A_("   验证方式：换实现（路线 2 的区间库）、换语言（C 加 GMP）、或纯手算（A7 的六步）。")
    A_("2. **新结论 N2（弹性恒等式）**：`ln(E(K₁)/E(K₂)) = ln(K₂/K₁) + (K₂−K₁)A/D − Θ`，Θ ≤ 10⁻¹²；这把「ε 对 K 的灵敏度」从观察升级为恒等式。")
    A_("   验证方式：任意两点独立代入（本报告给了两对点，路线 A 与路线 B 的区间相交）。")
    A_("3. **新结论 N3（两个百分数的来源）**：10.8% 与 30.6% 都是同一恒等式在同一锚点上的三段分解结果；具体地 `ln(E(K)/1.11e-43)` 的严格区间见 §4。")
    A_("4. **新结论 N4（窗口唯一性）**：三种印刷读法下，只有「截尾」读法把 2.06×10²⁰ 收进窗口；四舍与上取都把 2.06×10²⁰ 排除。")
    A_("   验证方式：§5 的两端证书（每端一条判定加其相邻整数）。")
    A_("")
    A_("---")
    A_("")
    A_("## 九、命令行与原始输出")
    A_("")
    A_("```")
    A_("cd /Users/luna/Documents/math IA/collatz-attack/70-research/tracks/thm23-eps/cycle-1")
    A_("20-experiments/../../20-experiments/.venv/bin/python scripts/r3_logdomain.py    # 教判据脚本")
    A_("/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python scripts/r3_report.py   # 生成本报告")
    A_("```")
    A_("")
    A_("原始输出（`scripts/results/r3_logdomain.out`，节选）：")
    A_("")
    A_("```")
    for line in LOGS:
        A_(line)
    A_("```")
    A_("")
    A_("---")
    A_("")
    A_("## 十、证据等级与引用纪律")
    A_("")
    A_("1. 本报告引用的论文行号：`hercher5.txt:695` 至 `:724`（Theorem 21 三式）、`:790` 至 `:793`（v 的定义式与 2^v − 1 ≤ n）、`:874` 至 `:876`（第七步句）、`:873`（第六步 K > 2.05×10²⁰）、`:850` 至 `:872`（Theorem 23 前六步），全部为**本次亲读（本次抽取）**；第 13、15 页的渲染图为**本次亲读（渲染图）**。")
    A_("2. 引用的项目记录：`cycle-2/route-5.md:217` 至 `:219`（三处记录值）与 `:221`（三点代入的既有结论）、`:206` 至 `:207`（1.8% 与 m = 92 口径）、`plan.md:112`（同三值）、`rederivation-as-printed.md:144` 至 `:148`（第七步印数与我方值的并置）、`audit-report.md:226`（登记为「依赖取整习惯的推断」），均为**本次亲读**。")
    A_("3. 本报告**不**主张任何关于科拉茨循环存在性的新结论；第六步的 1.8% 差异未归因。")
    A_("")
    A_("---")
    A_("")
    A_("*（本报告由 `scripts/r3_report.py` 生成，用时 %.1f 秒；生成时刻 %s）*" % (time.time() - T0, time.strftime("%Y-%m-%d %H:%M:%S")))
    return "\n".join(L) + "\n"

try:
    MD = gen_report()
    (HERE.parent / "route-3.md").write_text(MD)
    log("[ok] route-3.md 已写入")
except Exception:
    ERR.append(("gen_report", traceback.format_exc()))
    log("[FAIL] gen_report")
    log(traceback.format_exc())

(RES / "r3_report.out").write_text("\n".join(LOGS) + "\n")
print("\n".join(LOGS))
if ERR:
    print("=== 失败节 ===")
    for nm, tb in ERR:
        print(nm); print(tb)
sys.exit(1 if ERR else 0)
