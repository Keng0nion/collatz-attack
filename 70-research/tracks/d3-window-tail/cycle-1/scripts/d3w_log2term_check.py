"""d3w_log2term_check.py -- 复核 log₂(1 + 2^−C) 的数值（route-5.md:230 写 1.5×10⁻²²）

2^−C = 97/(162·X₀) 精确（因 2^C = 162X₀/97），故 log₂(1 + 2^−C) = ln(1 + t)/ln 2，t 为精确有理数。
本脚本用 d3w_cert_core 的定向舍入给严格区间，另用 mpmath 作独立对照。

运行：20-experiments/.venv/bin/python scripts/d3w_log2term_check.py
"""
import sys
import os
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from d3w_cert_core import Iv, ln2_iv, ln_one_minus_iv, ln_rat_iv

D = 80
X0 = 695 * 2 ** 60
t = Fr(97, 162 * X0)                       # 2^{-C}，精确有理
print("t = 2^-C = 97/(162X0) = %s" % ("%.6e" % float(t)))
# ln(1+t) = -ln(1 - u)，u = t/(1+t) <= 1/2
u = t / (1 + t)
ln1t = -ln_one_minus_iv(Iv(u, u), D)
lnval = ln1t / ln2_iv(D)
print("log2(1 + 2^-C) ∈ [%s, %s]" % (float(lnval.lo), float(lnval.hi)))
print("宽度 = %.2e" % float(lnval.width()))
try:
    from mpmath import mp, mpf, log as mlog
    mp.dps = 40
    v = mlog(1 + mpf(97) / (162 * X0)) / mlog(2)
    print("mpmath 独立值 = %s" % v)
    print("与区间中心之差 = %.2e" % float(abs(Fr(str(v)) - (lnval.lo + lnval.hi) / 2)))
except ImportError as exc:
    print("mpmath 不可用：%r" % (exc,))
print("对照 route-5.md:230 写的 1.5e-22：倍数 = %.4f"
      % float(lnval.lo / Fr("1.5e-22")))
print("对照 route-1/账本 记的 1.07806938779e-21：相对差 = %.2e"
      % float(abs(lnval.lo - Fr("1.07806938779e-21")) / lnval.lo))
