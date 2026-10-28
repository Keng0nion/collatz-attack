#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""账本条目数字复算（轨道 kcross-tail 第 1 轮，路线 5）。

只做「单点与小清单」量级的精确复算，不重跑任何证书脚本、不写任何既有日志：
  1. 从 r2_threshold_cert.log 的精确有理串重建 T_hi、T_lo，核分母结构、精确宽度、
     60 位截断打印与 28 位共同前缀（一律字符串解析，不经 float）。
  2. 从 k1_threshold_cert.log 的 KA、KB 核 [T_hi, T_lo] ⊆ [KA, KB] 与两侧余量。
  3. 从 r4b2_window_probe.out 的 c_j 与窗口右端复算相对窗口宽度（j = 89、90）。
  4. 用 mpmath（dps = 60，数值复算，非证书）重建 2×10⁻²⁴ 旧值的错因量级：
     3/(2^C − 1)、97/(54X₀)、两者之差、门槛处第三项、比值、log₂(1 + 2^−C)。
  5. 复算 C = log₂((162/97)·695·2⁶⁰) 与 c2r5_cert.log:9 的对照。

证据边界：第 1、2、3 组是精确有理算术（Fraction，无浮点中转）；第 4、5 组是
mpmath 高精度数值，只作量级与位数对照，不是严格区间证书。
"""

from __future__ import annotations

import re
from fractions import Fraction
from pathlib import Path

import mpmath as mp

REPO = Path(__file__).resolve().parents[5]
RES = REPO / "70-research/tracks/kcross-proof/cycle-1/scripts/results"


def dec_coeff(fr: Fraction, digits: int = 16) -> str:
    """给出 fr 的十进制科学计数系数（截断，不经 float）。"""
    if fr == 0:
        return "0"
    sign = "−" if fr < 0 else ""
    x = abs(fr)
    e = 0
    # 找到量级：10^e <= x < 10^(e+1)
    while x >= 10:
        x /= 10
        e += 1
    while x < 1:
        x *= 10
        e -= 1
    scaled = x * 10**digits
    head = scaled.numerator // scaled.denominator
    return f"{sign}{str(head)[0]}.{str(head)[1:]}×10^{e}"


def trunc_decimal(fr: Fraction, digits: int) -> str:
    """fr 的十进制截断打印：整数部分 + 小数部分（截断，不进位）。"""
    num, den = fr.numerator, fr.denominator
    ip = num // den
    rem = num - ip * den
    digs = []
    for _ in range(digits):
        rem *= 10
        digs.append(str(rem // den))
        rem -= (rem // den) * den
    return f"{ip}." + "".join(digs)


print("=" * 74)
print("[1] T 的两个端点（输入：r2_threshold_cert.log:57 与 :58 的精确有理串）")
print("=" * 74)

log = (RES / "r2_threshold_cert.log").read_text(encoding="utf-8").split("\n")
m = re.search(r"=\s*(\d+)/(\d+)\s*$", log[56])
T_hi = Fraction(int(m.group(1)), int(m.group(2)))
m = re.search(r"=\s*(\d+)/(\d+)\s*$", log[57])
T_lo = Fraction(int(m.group(1)), int(m.group(2)))

print(f"分母(T_hi) = 2**381 ？ {T_hi.denominator == 2**381}")
print(f"分母(T_lo) = 2**382 ？ {T_lo.denominator == 2**382}")
print(f"两分子均为奇数（即已既约）？ {T_hi.numerator % 2 == 1 and T_lo.numerator % 2 == 1}")
print(f"T_hi < T_lo（精确有理比较）？ {T_hi < T_lo}")

w = T_lo - T_hi
print(f"精确宽度 = {w.numerator}/{w.denominator}")
print(f"  分母 = 2**382 ？ {w.denominator == 2**382}")
print(f"  分子 = 3·5**18 ？ {w.numerator == 3 * 5**18}（3·5¹⁸ = {3 * 5**18}）")
print(f"宽度系数（截断 16 位）= {dec_coeff(w)}")
print(f"相对宽度 (T_lo − T_hi)/T_lo = {dec_coeff(w / T_lo)}")

t_hi_60 = trunc_decimal(T_hi, 60)
t_lo_60 = trunc_decimal(T_lo, 60)
print(f"T_hi 的 60 位截断打印 = {t_hi_60}")
print(f"T_lo 的 60 位截断打印 = {t_lo_60}")
print(f"与日志 :54 逐字符相同 ？ {'T_hi = ' + t_hi_60 in log[53]}")
print(f"与日志 :55 逐字符相同 ？ {'T_lo = ' + t_lo_60 in log[54]}")
common = 0
for a, b in zip(t_hi_60, t_lo_60):
    if a != b:
        break
    common += 1
print(f"两串共同前缀长度（含整数部分）= {common} 位，即小数点后 {common - 22} 位")
print(f"共同前缀串 = {t_hi_60[:common]}")

print()
print("=" * 74)
print("[2] [T_hi, T_lo] ⊆ [KA, KB]（输入：k1_threshold_cert.log:61 与 :62）")
print("=" * 74)
k1 = (RES / "k1_threshold_cert.log").read_text(encoding="utf-8").split("\n")
m = re.search(r"=\s*(\d+)/(\d+)\s*$", k1[60])
KA = Fraction(int(m.group(1)), int(m.group(2)))
m = re.search(r"=\s*(\d+)/(\d+)\s*$", k1[61])
KB = Fraction(int(m.group(1)), int(m.group(2)))
print(f"KA ≤ T_hi ？ {KA <= T_hi}；余量 T_hi − KA = {dec_coeff(T_hi - KA)}")
print(f"T_lo ≤ KB ？ {T_lo <= KB}；余量 KB − T_lo = {dec_coeff(KB - T_lo)}")
print(f"KA < KB ？ {KA < KB}；宽度 KB − KA = {dec_coeff(KB - KA)}（日志 :63 记 2.052683e-30）")

print()
print("=" * 74)
print("[3] 分岔窗口（输入：r4b2_window_probe.out 的 c_j 与窗口右端）")
print("=" * 74)
r4b2 = (RES / "r4b2_window_probe.out").read_text(encoding="utf-8").split("\n")
c_89 = Fraction(r4b2[7].split("∈ [")[1].split(",")[0].strip())
c_90 = Fraction(r4b2[8].split("∈ [")[1].split(",")[0].strip())
print(f"c_89 = {c_89}（取自 :8）；c_90 = {c_90}（取自 :9）")
for lineno, j in ((50, 90), (55, 89)):
    parts = r4b2[lineno].split("∈ [")[1].rstrip("]").split(",")
    lo = Fraction(parts[0].strip())
    hi = Fraction(parts[1].strip())
    cj = c_90 if j == 90 else c_89
    w_lo, w_hi = (lo - cj) / cj, (hi - cj) / cj
    print(f"j = {j}：窗口右端严格区间 = [{lo}, {hi}]")
    print(f"        相对窗口宽度 ∈ [{dec_coeff(w_lo, 15)}, {dec_coeff(w_hi, 15)}]")
    printed = r4b2[lineno + 1].split("∈ [")[1].split(",")[0].strip()
    log_digits = printed.split(".")[1].lstrip("0")   # 日志打印的有效数字串
    got_digits = dec_coeff(w_lo, 15).split("×")[0].replace(".", "")
    print(f"        日志 :{lineno + 2} 打印 = {printed}（有效数字串 {log_digits}，"
          f"{len(log_digits)} 位）")
    print(f"        档内复算有效数字串 = {got_digits}（前 {len(log_digits)} 位"
          f"{'一致' if got_digits[:len(log_digits)] == log_digits else '不一致'}）")

print()
print("=" * 74)
print("[4] 旧值 2×10⁻²⁴ 的错因量级（mpmath dps = 60，数值复算，非证书）")
print("=" * 74)
mp.mp.dps = 60
X0 = mp.mpf(695) * mp.mpf(2) ** 60
C = mp.log(mp.mpf(162) / 97 * X0) / mp.log(2)
delta = mp.log(3) / mp.log(2)
print(f"X₀ = 695·2⁶⁰ = {mp.nstr(X0, 25)}")
print(f"C = log₂((162/97)X₀) = {mp.nstr(C, 40)}")
C_str = mp.nstr(C, 45)
C_dec = C_str.split(".")[1]                      # C 的小数部分（高精度打印）
C_log9 = "70.1808063283083668248487894995"
C_log9_dec = C_log9.split(".")[1]
print(f"  与 c2r5_cert.log:9 的 {C_log9} 对照：前 28 位小数一致？ "
      f"{C_dec[:28] == C_log9_dec[:28]}（复算第 29 位起 = {C_dec[28:40]}）")
print(f"δ = log3/log2 = {mp.nstr(delta, 30)}")

t1 = 3 / (2**C - 1)
t2 = mp.mpf(97) / (54 * X0)
d = t1 - t2
print(f"3/(2^C − 1)      = {mp.nstr(t1, 40)}")
print(f"97/(54X₀)        = {mp.nstr(t2, 40)}")
print(f"两者之差         = {mp.nstr(d, 40)}")
third = 3 * 89 / (2**C - 1) ** delta
print(f"门槛处第三项（m₂ = 90）3·89/((2^C − 1)^δ) = {mp.nstr(third, 40)}")
print(f"第三项 / 差值    = {mp.nstr(third / d, 12)}（账本与 learnings 记 5.2×10¹⁰）")
lg = mp.log(1 + 2 ** (-C)) / mp.log(2)
print(f"log₂(1 + 2^−C)   = {mp.nstr(lg, 30)}")
print(f"旧判据式会给出的窗口（相对）≈ log₂(1+2^−C)/C = {mp.nstr(lg / C, 30)}"
      f"（route-5.md:230 写 2×10⁻²⁴）")
print("真窗口（第 [3] 组，j = 90）    ∈ [7.806771365412664, 7.806771365412681]×10⁻¹³")
print(f"旧值偏小约 {mp.nstr((mp.mpf('7.806771365412665e-13') / (lg / C)), 8)} 倍"
      f"，即 Q 缺少约 {mp.nstr(mp.log10(mp.mpf('7.806771365412665e-13') / (lg / C)), 6)} 个数量级")

print()
print("=" * 74)
print("[5] 对照 route-5.md:101（旧 (D1) 行）的错 C 值")
print("=" * 74)
C_wrong = mp.mpf("70.1808063283083640726545127109")
print(f"C 复算 − 旧 (D1) 值 = {mp.nstr(C - C_wrong, 8)}（量级 2.75×10⁻¹⁵）")
print(f"C 复算 − c2r5_cert.log:9 值 = {mp.nstr(C - mp.mpf('70.1808063283083668248487894995'), 8)}")
print()
print("证据边界：第 1、2、3 组为精确有理算术；第 4、5 组为 mpmath 数值，只作量级与位数对照。")
