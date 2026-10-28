#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽验 1：T 端点精确算术、分母 2 的幂结构、窗口两格、route-4 §5.2 的 5.55e-21 出处。

只读 kcross-proof 的既有日志（不重跑任何证书脚本）；所有十进制一律字符串精确解析，
禁 float 中转（本会话已知 Fraction(float) 会破坏第 20 位以上数字）。
命令行：/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python sc1_endpoints_windows.py
"""
import hashlib
import re
import sys
from decimal import Decimal, getcontext, ROUND_DOWN, ROUND_UP
from fractions import Fraction as F

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1/scripts")
import kc_tail_rig as R

PROOF = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts/results"
R2LOG = PROOF + "/r2_threshold_cert.log"
K1LOG = PROOF + "/k1_threshold_cert.log"
R4B2 = PROOF + "/r4b2_window_probe.out"
R4B = PROOF + "/r4b_search_epsopt.out"
OUTPATH = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1/scripts/results/sc1_out.txt"

out = []


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.append(s)


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def dfr(s):
    """十进制串（可含 e 记法）精确转 Fraction。"""
    getcontext().prec = 400
    return F(Decimal(s))


def dec(x, n=25):
    """有理数的十进制显示（四舍五入到 n 位有效数字，仅供人读）。"""
    getcontext().prec = n + 5
    return format(Decimal(x.numerator) / Decimal(x.denominator), ".%de" % (n - 1))


getcontext().prec = 400


def trunc_dec(x, nd):
    s = str((x * 10 ** nd).numerator // (x * 10 ** nd).denominator)
    return s if nd == 0 else s[:-nd] + "." + s[-nd:]


p("#" * 78)
p("# kcross-tail 路线 2 抽验 1：T 端点、2 的幂结构、窗口两格、5.55e-21 出处")
for path in (R2LOG, K1LOG, R4B2, R4B):
    p("#   %s  %s" % (path.split("/")[-1], md5(path)))
p("#" * 78)
p("")

txt = open(R2LOG, encoding="utf-8").read()
lines = txt.splitlines()


def grab(pat, s, label):
    m = re.search(pat, s)
    assert m, "未匹配：" + label
    return m.group(1), m.group(2)


T_hi = F(*[int(g) for g in grab(r"T_hi 的精确有理 = (\d+)/(\d+)", txt, "T_hi")])
T_lo = F(*[int(g) for g in grab(r"T_lo 的精确有理 = (\d+)/(\d+)", txt, "T_lo")])
p("[1] 端点有理数（%s 第 57 至 58 行）" % R2LOG.split("/")[-1])
p("    T_hi 分母 == 2**381 ？ %s ；2 的指数 = %s" % (
    T_hi.denominator == 2 ** 381, (T_hi.denominator.bit_length() - 1)
    if T_hi.denominator & (T_hi.denominator - 1) == 0 else "非 2 幂"))
p("    T_lo 分母 == 2**382 ？ %s ；2 的指数 = %s" % (
    T_lo.denominator == 2 ** 382, (T_lo.denominator.bit_length() - 1)
    if T_lo.denominator & (T_lo.denominator - 1) == 0 else "非 2 幂"))
p("    两分子为奇数（既约）？ T_hi %s / T_lo %s ；T_hi < T_lo ？ %s" % (
    T_hi.numerator % 2 == 1, T_lo.numerator % 2 == 1, T_hi < T_lo))
p("")

w = T_lo - T_hi
rel = w / T_hi
p("[2] 精确宽度与相对宽度")
p("    宽度 == 3*5**18/2**382 ？ %s ；== 3*10**18/2**400 ？ %s" % (
    w == F(3 * 5 ** 18, 2 ** 382), w == F(3 * 10 ** 18, 2 ** 400)))
p("    宽度系数（20 位）= %s" % dec(w, 20))
p("    相对宽度（20 位）= %s" % dec(rel, 20))
p("    宽度 ∈ [1.161777574454e-102, 1.161777574455e-102) ？ %s" % (
    dfr("1.161777574454e-102") <= w < dfr("1.161777574455e-102")))
p("    相对宽 ∈ [3.709432774431e-123, 3.709432774432e-123) ？ %s" % (
    dfr("3.709432774431e-123") <= rel < dfr("3.709432774432e-123")))
p("    一致位数 ≈ %.2f（route-2.md:12 记『约 122 位一致』）" % (
    -(rel.numerator.bit_length() - rel.denominator.bit_length()) * 0.30102999566398120))
p("")

p("[3] 60 位打印与公共前缀")
p("    T_hi 截断 60 位 == 日志 :54 ？ %s ；T_lo 截断 60 位 == 日志 :55 ？ %s ；两行相同？ %s" % (
    trunc_dec(T_hi, 60) == lines[53].strip().split("= ")[1],
    trunc_dec(T_lo, 60) == lines[54].strip().split("= ")[1],
    lines[53].strip().split("= ")[1] == lines[54].strip().split("= ")[1]))
pref = "313195478959172262876.6365306194907065260231016952"
p("    49 位有效数字共同前缀 %s 是两端的公共截断？ %s" % (
    pref, trunc_dec(T_hi, 28) == pref and trunc_dec(T_lo, 28) == pref))
p("")

k1 = open(K1LOG, encoding="utf-8").read()
KA = F(*[int(g) for g in re.findall(r"KA = [\d.]+ = (\d+)/(\d+)", k1)[0]])
KB = F(*[int(g) for g in re.findall(r"KB = [\d.]+ = (\d+)/(\d+)", k1)[0]])
p("[4] 相含检查")
p("    KA（%s 第 61 行的精确有理）≤ T_hi ？ %s ；余量 = %s" % (
    K1LOG.split("/")[-1], KA <= T_hi, dec(T_hi - KA, 8)))
p("    T_lo ≤ KB ？ %s ；余量 = %s" % (T_lo <= KB, dec(KB - T_lo, 8)))
p("    对照 route-1.md:119 的 3.61×10⁻³¹ 与 1.69×10⁻³⁰（同一对数）")
i5 = re.search(r"I5（route-5.*?\n.*?= \[([\d.]+), ([\d.]+)\]；", txt)
if i5:
    i5lo, i5hi = dfr(i5.group(1)), dfr(i5.group(2))
    p("    I2 ⊆ I5（I5 端点取自 %s [7] 节 60 位打印，按截断方向保守）？ %s" % (
        R2LOG.split("/")[-1], i5lo <= T_hi and T_lo <= i5hi))
    p("      余量 = %s 与 %s（对照日志 :119 至 :121 的 1.203233432443e-27 与 8.987142640435e-28）" % (
        dec(T_hi - i5lo, 8), dec(i5hi - T_lo, 8)))
p("")

r4 = open(R4B2, encoding="utf-8").read().splitlines()
c = {}
for j in (85, 89, 90, 91, 92):
    ln = [l for l in r4 if l.strip().startswith("c_%d ∈" % j)][0]
    v = re.findall(r"([\d.]+)", ln.split("∈")[1])
    c[j] = (dfr(v[0]), dfr(v[1]))
p("[5] 窗口两格 (K*_j - c_j)/c_j（逐字取自 %s）" % R4B2.split("/")[-1])
for j in (90, 89):
    idx = [i for i, l in enumerate(r4) if ("j = %d ：左端偏移" % j) in l][0]
    kl = [l for l in r4[idx:idx + 4] if "窗口右端" in l][0]
    v = re.findall(r"([\d.]+)", kl.split("∈")[1])
    klo, khi = dfr(v[0]), dfr(v[1])
    rlo, rhi = (klo - c[j][1]) / c[j][1], (khi - c[j][0]) / c[j][0]
    p("    j = %d：相对窗口宽度 ∈ [%s, %s]" % (j, dec(rlo, 25), dec(rhi, 25)))
    p("       两端 12 位打印同为 %s ？ %s（日志第 %d、%d 行）" % (
        "7.80677136541e-13" if j == 90 else "7.71461775858e-13",
        trunc_dec(rlo, 12) == trunc_dec(rhi, 12), idx + 3, idx + 4))
    p("       含 2e-24 ？ %s ；含 1.5361313e-23 ？ %s ；含 1.5361313e-24（脚本实判常量）？ %s" % (
        rlo <= dfr("2e-24") <= rhi, rlo <= dfr("1.5361313e-23") <= rhi,
        rlo <= dfr("1.5361313e-24") <= rhi))
p("    缺陷见证：r4b2_window_probe.py:132 写作 F(15361313, 10**31) = 1.5361313e-24，")
p("      与所贴标签 1.5361313e-23（=%s :62 的实值 1.5361313e-23）差 10 倍；" % R4B.split("/")[-1])
p("      两个量都在窗口外，故结论不变，但该行判据与标签不一致。")
p("")

X0 = 695 * 2 ** 60
p("[6] route-4 §5.2 第 2 条的 5.55×10⁻²¹：真值与出处")
p("    X0 = 695*2^60 = %s" % X0)
p("    A(91) = 3/X0 = %s" % dec(F(3, X0), 12))
p("    A(90)-A(91) = 105/(54X0) = %s（与 §5.2 第 2 条第二项一致）" % dec(F(105, 54 * X0), 12))
p("    240/(54X0) = %s ← 同族表达式里最接近 5.55e-21 者" % dec(F(240, 54 * X0), 12))
p("    97/(54X0) = %s ；3/(2^C-1)（2^C=(162/97)X0，精确有理）= %s" % (
    dec(F(97, 54 * X0), 12), dec(F(291, 162 * X0 - 97), 12)))
p("    恒等式 3/(2^C-1) - 97/(54X0) == 97/(54X0(2^C-1)) ？ %s ；差 = %s" % (
    F(291, 162 * X0 - 97) - F(97, 54 * X0) == F(97 * 97, 54 * X0 * (162 * X0 - 97)),
    dec(F(291, 162 * X0 - 97) - F(97, 54 * X0), 12)))
hit = [l for l in r4 if "5.55" in l or "5.546" in l]
p("    %s 全文检索 '5.55'/'5.546'：%d 行（说明 5.55e-21 在 r4b2 日志里没有印出过）" % (
    R4B2.split("/")[-1], len(hit)))
p("    3/X0 > 3/(2^C-1) ？ %s ；比值 = %s" % (
    F(3, X0) > F(291, 162 * X0 - 97), dec(F(3, X0) / F(291, 162 * X0 - 97), 8)))
p("")

p("[7] j = 92 无窗口的一个可判形式（本路自写，见报告第 2 节）")
dlo, dhi = R.delta_bounds()
l2 = R.ln2_bounds()
Clo, Chi = R.C_bounds()
ylo = R.rd((Clo - 1) * dlo * l2[0])
ex = R.exp_bounds(ylo, R.ru((Chi - 1) * dhi * l2[1]))
ub = R.ru(F(1) / ex[0])
term = R.ru(273 * ub)
lhs = F(291, 162 * X0 - 97) + term
p("    δ 区间宽 = %s ；C 区间 = [%s, %s]" % (float(dhi - dlo), dec(Clo, 22), dec(Chi, 22)))
p("    273*2^{-(C-1)δ} 的上界 = %s" % dec(term, 8))
p("    291/(162X0-97) + 该上界 < 3/X0 ？ %s ；余量 = %s" % (lhs < F(3, X0), dec(F(3, X0) - lhs, 8)))
p("")
open(OUTPATH, "w").write("\n".join(out) + "\n")
p("[写出] scripts/results/sc1_out.txt")
