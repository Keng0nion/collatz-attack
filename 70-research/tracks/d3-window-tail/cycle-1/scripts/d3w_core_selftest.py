"""d3w_core_selftest.py -- d3w_cert_core 的自检（判据全部可翻 False，含一条负对照）

运行：20-experiments/.venv/bin/python scripts/d3w_core_selftest.py
"""
import sys
import os
import time
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from d3w_cert_core import (Iv, atanh_iv, ln2_iv, ln_int_iv, ln_rat_iv, exp_iv,
                           two_pow_iv, pow_iv, ln_one_minus_iv)

D = 110
X0 = 695 * 2 ** 60
R = Fr(162 * X0, 97)          # 2^C 的精确值（C 的定义式）
N24 = 129807432203684900427743  # 162*X0 - 97

t0 = time.time()
res = []


def chk(name, cond, extra=""):
    res.append((name, bool(cond), extra))
    print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, extra))


ln2 = ln2_iv(D)
print("ln2  =", ln2)
print("      width = %.3e" % float(ln2.width()))
chk("S1 ln2 区间不平凡（宽度 < 1e-100）", ln2.width() < Fr(1, 10 ** 100),
    "width=%.2e" % float(ln2.width()))

# S2 恒等式：ln 6 = ln2 + ln3，ln 10 = ln2 + ln5，ln 12 = 2 ln2 + ln3
ln3, ln5, ln6, ln10, ln12 = (ln_int_iv(n, D) for n in (3, 5, 6, 10, 12))
for (nm, a, b) in (("ln6=ln2+ln3", ln6, ln2 + ln3), ("ln10=ln2+ln5", ln10, ln2 + ln5),
                   ("ln12=2ln2+ln3", ln12, Iv(2, 2) * ln2 + ln3)):
    chk("S2 %s（区间相交）" % nm, a.lo <= b.hi and b.lo <= a.hi)

# S3 exp(ln 2) 必须含 2；exp(ln 3) 必须含 3
chk("S3 exp(ln2) 含 2", exp_iv(ln2, D).contains(2), repr(exp_iv(ln2, D)))
e3 = exp_iv(ln3, D)
chk("S3 exp(ln3) 含 3", e3.contains(3), "宽=%.2e" % float(e3.width()))

# S4 核心恒等式：2^C = (162/97) X0 精确成立，区间必须含它
C_lo = 60 + ln_rat_iv(Iv(Fr(112590, 97), Fr(112590, 97)), D).lo / ln2.hi
C_hi = 60 + ln_rat_iv(Iv(Fr(112590, 97), Fr(112590, 97)), D).hi / ln2.lo
Civ = Iv(C_lo, C_hi)
print("C    =", Civ)
print("      width = %.3e" % float(Civ.width()))
twoC = two_pow_iv(Civ, D)
chk("S4 2^C 区间含 (162/97)X0 精确值", twoC.contains(R),
    "2^C=[%s, %s]" % (float(twoC.lo), float(twoC.hi)))
chk("S4 区间宽度不平凡", twoC.width() / R < Fr(1, 10 ** 95),
    "相对宽 %.2e" % float(twoC.width() / R))

# S5 负对照：2^C 区间不得含 2^(C+1e-8) 的值（判据有分辨力）
chk("S5 负对照：2^C 区间不含 (162/97)X0*(1+1e-8)",
    not twoC.contains(R * Fr(100000001, 100000000)))

# S6 ln(1-x)：x=1/2 给 -ln2，须与 -ln2 区间相交
lom = ln_one_minus_iv(Iv(Fr(1, 2), Fr(1, 2)), D)
chk("S6 ln(1/2) = -ln2（区间相交）", lom.lo <= -ln2.hi and -ln2.lo <= lom.hi,
    repr(lom))
# x = 1/3（z 边界）也要成立
lom2 = ln_one_minus_iv(Iv(Fr(1, 3), Fr(1, 3)), D)
chk("S6 ln(2/3) = ln2 - ln3（区间相交）",
    lom2.lo <= (ln2 - ln3).hi and (ln2 - ln3).lo <= lom2.hi)

# S7 pow_iv：2 = 2^1，用 pow_iv(Iv(2), Iv(1)) 须含 2
chk("S7 pow_iv(2,1) 含 2", pow_iv(Iv(2, 2), Iv(1, 1), D).contains(2))
# 3^2 = 9（用 δ 型调用：pow_iv(Iv(3), Iv(2))）
chk("S7 pow_iv(3,2) 含 9", pow_iv(Iv(3, 3), Iv(2, 2), D).contains(9))

# S8 atanh 边界：atanh(1/3) 与 math 对照，且 atanh 不越界
a13 = atanh_iv(1, 3, D)
chk("S8 atanh(1/3) 宽 < 1e-100", a13.width() < Fr(1, 10 ** 100))
chk("S8 atanh(1/2) 与 (1/2)ln3 相交", atanh_iv(1, 2, D).overlaps(Fr(1, 2) * ln3))

# S9 δ = ln3/ln2 区间与 mpmath 对照（若可用）
delta = Iv(ln3.lo / ln2.hi, ln3.hi / ln2.lo)
print("delta =", delta)
print("       width = %.3e" % float(delta.width()))
try:
    from mpmath import mp, log as mlog
    mp.dps = 60
    # 口径说明：mpmath dps=60 的值本身只精确到约 1e-59，不能要求它落进 1e-106 宽的区间；
    # 因此这里比的是「与本区间中心的距离 < 1e-55」，即检验两实现一致到 mpmath 自身的精度。
    dm = Fr(str(mlog(3) / mlog(2)))
    chk("S9 δ 与 mpmath 60 位值之差 < 1e-55", abs(dm - delta.lo) < Fr(1, 10 ** 55),
        "差 = %.2e" % float(abs(dm - delta.lo)))
    Cm = Fr(str(mlog(Fr(R)) / mlog(2)))
    chk("S9 C 与 mpmath 60 位值之差 < 1e-55", abs(Cm - Civ.lo) < Fr(1, 10 ** 55),
        "差 = %.2e" % float(abs(Cm - Civ.lo)))
    # 负对照：δ 区间不得含 δ + 1e-9
    chk("S9 负对照：δ 区间不含 δ+1e-9", not delta.contains(dm + Fr(1, 10 ** 9)))
except ImportError as exc:    # mpmath 不可用时不得当通过
    chk("S9 mpmath 对照", False, "mpmath 不可用：%r" % (exc,))

print()
print("耗时 %.1f 秒；通过 %d/%d" % (time.time() - t0,
                                   sum(1 for _, ok, _ in res if ok), len(res)))
print("全部通过？", all(ok for _, ok, _ in res))
