#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 第 1 轮：独立实现的锚点自检。
先定义后计算，逐条对照外部已钉住的数字：
  A1 delta 的 40 位前缀（materials.md:62 记录值）
  A2 论文 Theorem 23 自己对 m = 91、起点 7e11 的七步链条（第三方原始数据）
  A3 项目钉住值（materials.md:137）：m=91、起点 7.5311e11 终值 7941964418702608664581
  A4 项目钉住值（materials.md:82 至 :85）：m=92 终值 77692117359936589403、余量 0.226490482058
  A5 qmin 连分数步与暴力最小分母搜索一致（自证）
"""
import sys
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
from fractions import Fraction
from mpmath import mp, mpf, power
import r4x_core as R

OUT = []
def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)

# ---------- A1: delta ----------
d = R.set_dps(120)
p("[A1] delta (dps=120) 50 位：")
p("     ", mp.nstr(R.DELTA, 50))
PINNED40 = "1.58496250072115618145373894394781650875981440769248106045575"
p("     materials.md:62 钉住值：", PINNED40)
p("     前 40 位一致？", mp.nstr(R.DELTA, 60)[:42] == PINNED40[:42])
p("     X0 = 695*2^60 精确 =", R.X0_exact())
p("     X0 数值 =", mp.nstr(R.X0(), 25))
p("     log2((162/97)X0) =", mp.nstr(R.log2(mpf(162)/97*R.X0()), 20))
p()

# ---------- A2: 论文七步链条（m=91, 起点 7e11, 两种 m2 选取约定） ----------
p("[A2] 论文 Theorem 23 链条（m=91, K0=7e11）；论文公布值：")
p("     m2 >= 47,67,77,82,86,88,91；K > 5.2e15,3.97e17,4.64e18,2.74e19,7.76e19,2.05e20,7.94e21")
p("     eps ~= 6.9e-32,5.1e-36,4.1e-38,2.3e-39,2.3e-40,5.3e-41,1.11e-43")
for conv in ("min_eps", "max_feasible"):
    R.set_dps(120)
    seq, term, over = R.chain(91, mpf("7e11"), convention=conv, cap=R.sdw_upper(91))
    p("  == 约定 %s ==" % conv)
    for r in seq:
        p("     K_in=%-22s m2=%-3s eps=%-14s Psi=%s" % (
            mp.nstr(r["K_in"], 8), r.get("m2"), mp.nstr(r["eps"], 6), r.get("psi")))
    p("     终值 =", term)
p()

# ---------- A3/A4: 项目钉住值 ----------
R.set_dps(120)
for (m, Lstr) in [(91, "7.5311e11"), (92, "7.5311e11")]:
    seq, term, over = R.chain(m, mpf(Lstr), cap=R.sdw_upper(m))
    U = R.sdw_upper(m)
    p("[A%d] m=%d 起点 %s" % (3 if m == 91 else 4, m, Lstr))
    for r in seq:
        p("     K_in=%-22s m2=%-3s eps=%-14s Psi=%s" % (
            mp.nstr(r["K_in"], 8), r.get("m2"), mp.nstr(r["eps"], 6), r.get("psi")))
    p("     终值 K 下界 =", term)
    p("     U(%d) = 1.4784*%d*delta^%d =" % (m, m, m), mp.nstr(U, 25))
    if term > 0:
        p("     余量 K下界/U =", mp.nstr(mpf(term)/U, 30))
    p()

# ---------- A5: qmin 与暴力搜索一致 ----------
def brute_min_den(alpha, beta, QMAX):
    """暴力：q=1,2,... 找最小 q 使存在整数 p 满足 alpha < p/q < beta（alpha,beta 为 Fraction）。"""
    for q in range(1, QMAX + 1):
        lo = alpha * q
        hi = beta * q
        p_cand = lo.__floor__() + 1
        if p_cand < hi:
            return q
    return None

p("[A5] qmin（连分数公式）对暴力搜索的自证（区间为有理端点，暴力上限 200000）")
import random
random.seed(20261025)
bad = 0
tests = 0
for _ in range(40):
    a = Fraction(random.randint(1, 500), random.randint(1, 500))
    b = a + Fraction(1, random.randint(2, 1500))
    if not (0 < a < b):
        continue
    q_cf, k, A_, B_ = R.qmin_interval(mpf(a.numerator)/a.denominator, mpf(b.numerator)/b.denominator)
    q_bf = brute_min_den(a, b, 200000)
    tests += 1
    ok = (q_bf is not None) and (q_cf == q_bf)
    if not ok:
        bad += 1
        p("     不一致：", a, b, "cf=", q_cf, "bf=", q_bf)
p("     随机有理区间 %d 例，全部一致？%s" % (tests, bad == 0))
# 再在含 delta 的真实区间上测：有理端点、暴力可行
for (alo, den, num_eps, den_eps) in [(15849, 10000, 1, 1000), (15849, 10000, 1, 100000)]:
    a = Fraction(alo, den)
    b = a + Fraction(num_eps, den_eps)
    q_cf, k, A_, B_ = R.qmin_interval(mpf(a.numerator)/a.denominator, mpf(b.numerator)/b.denominator)
    q_bf = brute_min_den(a, b, 2000000)
    p("     区间 (%s, %s)（含 delta=%s）：连分数 q=%s，暴力 q=%s，一致？%s" % (
        a, b, mp.nstr(R.DELTA, 12), q_cf, q_bf, q_cf == q_bf))
p()

open("/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts/results/r4x_run1.out", "w").write("\n".join(OUT) + "\n")
