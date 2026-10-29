"""d3w_r5v_audit.py -- 独立复核否证一与否证二（C 的 float64 伪值；第三项主导的 10.72 个数量级）

不 import 任何被审脚本；不读被审脚本的输出；只读文本行做逐字对照。
运行：20-experiments/.venv/bin/python scripts/d3w_r5v_audit.py
"""
import sys
import os
import time
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from d3w_cert_core import Iv, ln2_iv, ln_int_iv, ln_rat_iv, pow_iv, two_pow_iv

D = 110
X0 = 695 * 2 ** 60
T162 = 162 * X0            # = 162 * 695 * 2^60
NUM = T162 - 97            # 162*X0 - 97，即 97*(2^C - 1) 的分子

res = []
t0 = time.time()


def chk(name, cond, extra=""):
    res.append((name, bool(cond)))
    print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, extra))


def dec(x, digits=40):
    """把 Fraction 精确打印到 digits 位小数（截断）。"""
    x = Fr(x)
    s = str(x.numerator * 10 ** digits // x.denominator)
    neg = s.startswith("-")
    if neg:
        s = s[1:]
    while len(s) <= digits:
        s = "0" + s
    out = s[:-digits] + "." + s[-digits:]
    return ("-" if neg else "") + out


print("== 一、常数与 C 的严格有理区间（自写定点定向舍入，D = %d）==" % D)
ln2 = ln2_iv(D)
ln3 = ln_int_iv(3, D)
delta = Iv(ln3.lo / ln2.hi, ln3.hi / ln2.lo)
LN112590_97 = ln_int_iv(112590, D) - ln_int_iv(97, D)     # ln(112590/97)，112590 = 162*695
C = Iv(60, 60) + Iv(LN112590_97.lo / ln2.hi, LN112590_97.hi / ln2.lo)
print("ln2  区间宽度 = %.3e" % float(ln2.width()))
print("delta = %s" % delta)
print("       宽度   = %.3e" % float(delta.width()))
print("C     = %s" % dec(C.lo, 34) + "  (下界)")
print("        %s" % dec(C.hi, 34) + "  (上界)")
print("       区间宽度 = %.3e" % float(C.width()))

# ---- 定义式自洽：2^C 必须精确等于 (162/97)X0 ----
twoC = two_pow_iv(C, D)
R = Fr(T162, 97)
chk("A1 2^C = (162/97)X0 成立（区间含精确有理值）", twoC.contains(R),
    "相对宽 %.2e" % float(twoC.width() / R))

print()
print("== 二、C 的真值与 route-5 的串（逐字）=")
S_R5_101 = "70.1808063283083640726545127109"     # cycle-2/route-5.md:101
S_CERT9 = "70.1808063283083668248487894995"      # c2r5_cert.log:9 与 route-5.md:427
s1 = Fr(S_R5_101)
s2 = Fr(S_CERT9)
print("route-5.md:101 的串         : %s" % S_R5_101)
print("c2r5_cert.log:9 的串        : %s" % S_CERT9)
print("真值下界（本脚本 34 位截断）: %s" % dec(C.lo, 34))
d1 = C.lo - s1          # 真值 − 串一（真值更大则 d1 > 0）
print("C_lo − 串一 = %s" % dec(d1, 40))
print("比值        = %s × 10^-15" % dec(d1 * 10 ** 15, 24))
chk("B1 串一严格小于 C 的下界（串一为假值）", d1 > 0)
chk("B2 串一与真值之差 = 2.7521942767886…×10^-15",
    Fr(2752194, 10 ** 21) < d1 < Fr(27522, 10 ** 19),
    "d1×1e15 = %s" % dec(d1 * 10 ** 15, 24))
d2 = C.lo - s2
chk("B3 串二与真值之差 < 1e-28（串二为真值 28 位截断）",
    abs(d2) < Fr(1, 10 ** 28), "C_lo − 串二 = %s" % dec(d2, 40))
chk("B4 两串前 16 位有效数字一致（含小数点共 17 字符）、第 17 位有效数字起分道",
    S_R5_101[:17] == S_CERT9[:17] and S_R5_101[:18] != S_CERT9[:18],
    "共同前缀 %s；其后 %s vs %s" % (S_CERT9[:17], S_R5_101[17], S_CERT9[17]))

print()
print("== 三、float64 伪值判定（与整数幂比较无关，直接由二进制值给出）==")
dbl = float(C.lo)                     # 区间宽 1e-100 远小于 double 间距，故为唯一邻近 double
chk("C1 区间内恰有一个 double（float(C_hi) 与 float(C_lo) 相等）",
    float(C.hi) == dbl, "float(lo)=%.20e float(hi)=%.20e" % (dbl, float(C.hi)))
dfr = Fr(dbl)                          # double 的精确二进制值（dyadic）
print("double 的精确值（40 位小数）: %s" % dec(dfr, 40))
print("double 相对 C_lo 的偏差     : %s" % dec(dfr - C.lo, 30))
print("串一与 double 的差          : %s" % dec(dfr - s1, 40))
chk("C2 串一 = double 舍入到 28 位小数（差 < 1e-28）", abs(dfr - s1) < Fr(1, 10 ** 28),
    "|double − 串一| = %s" % dec(abs(dfr - s1), 40))
_d30 = dec(Fr(dbl), 30)
_d28_round = dec(dfr + Fr(5, 10 ** 29), 28)      # 28 位小数的四舍五入（第 29 位起进位的判据）
print("double 的小数展开（30 位）: %s" % _d30)
print("double 舍入到 28 位小数    : %s" % _d28_round)
chk("C3 串一 = double 舍入到 28 位小数（逐字符）", _d28_round == S_R5_101,
    "double 28 位 = %s" % _d28_round)
chk("C4 真值区间不含任何串一的代表（串一 < C_lo）", s1 < C.lo)
chk("C5 double 与真值差 = 2.7521942767886198792…×10^-15",
    Fr(2752194, 10 ** 21) < C.lo - dfr < Fr(27522, 10 ** 19),
    "(C_lo − double)×1e15 = %s" % dec((C.lo - dfr) * 10 ** 15, 24))

print()
print("== 四、门槛处三项分解（M = 90；m = 92）==")
M = 90
# 2^C - 1 = (162 X0 - 97)/97 精确，故下式只含 δ 的超越性
base = Iv(Fr(NUM, 97), Fr(NUM, 97))          # 2^C - 1 的精确有理值
powC = pow_iv(base, delta, D)                # (2^C - 1)^delta
T3new = Iv(3 * (M - 1), 3 * (M - 1)) / powC  # 3(M-1)/(2^C-1)^delta
P1 = Fr(3 * 97, NUM) - Fr(97, 54 * X0)       # = 3/(2^C-1) - 97/(54 X0)，精确有理
print("(2^C-1)^delta ∈ [%s, %s]" % (dec(powC.lo, 18), dec(powC.hi, 18)))
print("T3new = 3*89/(2^C-1)^delta ∈ [%s, %s]" % (dec(T3new.lo, 50), dec(T3new.hi, 50)))
print("P1 = 3/(2^C-1) - 97/(54X0) = %s" % dec(P1, 56))
ratio = T3new / Iv(P1, P1)
print("比值 ∈ [%s, %s]" % (dec(ratio.lo, 8), dec(ratio.hi, 8)))
# 10^k 阶（整数比较，精确）
k_lo = len(str(int(ratio.lo))) - 1
k_hi = len(str(int(ratio.hi))) - 1
chk("D1 比值落在 5.2202×10^10 附近（10^k 阶为 10）", k_lo == 10 and k_hi == 10,
    "k_lo=%d k_hi=%d" % (k_lo, k_hi))
m_lo = ratio.lo / (10 ** 10)
m_hi = ratio.hi / (10 ** 10)
print("比值/10^10 ∈ [%s, %s] → 5.2202498×10^10" % (dec(m_lo, 8), dec(m_hi, 8)))
chk("D2 T3new > 5.22×10^10 × P1（第三项主导）", ratio.lo > Fr(52202, 10 ** 3))
chk("D3 T3new 与 8.74494110107×10^-32 一致到 12 位（区间宽 < 1e-44）",
    Fr("8.74494110107e-32") - Fr(1, 10 ** 43) < T3new.lo
    and T3new.hi < Fr("8.74494110107e-32") + Fr(1, 10 ** 43)
    and T3new.width() < Fr(1, 10 ** 44),
    "T3new 宽 = %.2e" % float(T3new.width()))
chk("D4 P1 = 1.67519591503459×10^-42 一致到 15 位",
    Fr("1.67519591503459e-42") - Fr(1, 10 ** 56) < P1 < Fr("1.67519591503459e-42") + Fr(1, 10 ** 56),
    "P1 = %s" % dec(P1, 46))
# log10 比值的小数部分（用整数比较给出两位小数区间）
from math import log10 as _lg
print("log10(比值) 约 %.4f" % _lg(float(ratio.lo)))
chk("D5 log10(比值) ∈ (10.71, 10.72)", 10.71 < _lg(float(ratio.lo)) < 10.72,
    "log10 = %.4f" % _lg(float(ratio.lo)))

print()
print("== 五、route-5 自相矛盾的旁证（两处 C 串并列）==")
chk("E1 :101 串与 :427 串不同（同文件内两值并存）", s1 != s2)
chk("E2 后者（:427）为本脚本真值的前 28 位", dec(C.lo, 28) == S_CERT9,
    "本脚本 28 位 = %s" % dec(C.lo, 28))

print()
print("耗时 %.1f 秒；通过 %d/%d" % (time.time() - t0,
                                   sum(1 for _, ok in res if ok), len(res)))
print("全部通过？", all(ok for _, ok in res))
