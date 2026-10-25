#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-2 第 1 步：先定死定义，再用项目里已钉住的数字做锚点自检。

锚点全部取自本轮材料（materials.md 第三节「本次亲跑的核对」与 methods.md 第 1 节）：
  链上锚点（m2 = 47 的三个组合，W = (m2/m)·K）：
     (m=91, K=7e11)        v = 84.02140326164773718764214
     (m=92, K=7.5311e11)   v = 89.41365947118846256456601
     (m=91, K=7.5311e11)   v = 90.39622715768503907626453
  定量锚点：K_up(91) = 214072842063828923281.3586、margin(91) = 37.09935525747164492758953、
            U(92) = 3.4302597024885020978e20、margin(92) = 0.226490482057595771625621
  c = log2((162/97)·X0) = 70.180806328308366825（(A7)）
  [2c] 一般 W 组：m2=2 W=70 → 27.0796965、m2=3 W=210 → 41.2001516、
                 m2=5 W=200 → 12.9960091、m2=10 W=2000 → 11.8122055
  [2c] 前沿组（v = c）：m2=5 W=1080.03627904、m2=10 W=11882.7608054、m2=20 W=1200678.58335
  δ 的 38 位小数钉住值 1.58496250072115618145373894394781650876（audit-report.md:312）
本脚本不做任何反例判定，只做定义核对与界机制自检。日志由外部重定向保存。
"""
import sys
import time
from fractions import Fraction

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
import mpmath
from r2_common import (delta_rigorous_bounds, v_vertex, vertex, feasible,
                       S_bounds, LEVEL_MID, Det)

OUT = []
def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)

def close(got, pinned, decimals):
    """把 got 四舍五入到 pinned 的小数位数后逐字符比较。"""
    from decimal import Decimal, getcontext, ROUND_HALF_EVEN
    getcontext().prec = 80
    q = Decimal(1).scaleb(-decimals)
    return str(Decimal(got).quantize(q, rounding=ROUND_HALF_EVEN)) == pinned

say("=" * 78)
say("route-2 第 1 步：定义与锚点自检")
say("=" * 78)

# ---------------------------------------------------------------- 1. δ 的括号
say("\n[1] δ = log3/log2 的严格有理括号（判据是整数幂 2^p < 3^q < 2^r，不用浮点）")
brackets = {}
t0 = time.time()
for q in (10 ** 5, 10 ** 6, 10 ** 7):
    lo, hi = delta_rigorous_bounds(q)
    brackets[q] = (lo, hi)
    say(f"    q = 10^{len(str(q))-1}: δ_lo = {float(lo):.12f} δ_hi = {float(hi):.12f} "
        f"宽度 = {float(hi-lo):.2e}  [2^{lo.numerator} < 3^{q} < 2^{hi.numerator}]")
say(f"    耗时 {time.time()-t0:.2f} s；q = 10^7 一侧的整数 3^(10^7) 约 {int(10**7*1.585)+1} 位")
D_LO, D_HI = brackets[10 ** 7]        # 宽度 1e-7 的严格括号，本次搜索用的多面体参数
D_LO6, D_HI6 = brackets[10 ** 6]      # 宽度 1e-6

# ------------------------------------------------------------ 2. δ 的 60 位复算
mpmath.mp.dps = 60
d_true = mpmath.log(3) / mpmath.log(2)
say("\n[2] δ 的 mpmath(dps=60) 复算，与 38 位小数钉住值比对")
say(f"    δ = {mpmath.nstr(d_true, 60)}")
pin = "1.58496250072115618145373894394781650876"
say(f"    四舍五入到 38 位小数 = {mpmath.nstr(d_true, 39)}")
say(f"    与钉住值 {pin} 逐字符比对 → {'一致' if mpmath.nstr(d_true, 39) == pin else '不一致'}")
say(f"    （钉住值是四舍五入到第 38 位小数；直接截断会得 ...50875，这不是分歧：第 39 位是 9。）")
say(f"    严格括号检查 δ_lo < δ < δ_hi → "
    f"{mpmath.mpf(D_LO.numerator)/D_LO.denominator < d_true} 与 {d_true < mpmath.mpf(D_HI.numerator)/D_HI.denominator}")

# --------------------------------------------------- 3. v 公式与锚点（真 δ）
say("\n[3] v = W(δ−1)/(δ^{m2}−1) 与既有脚本锚点比对（真 δ，mpmath dps=60；W = (m2/m)·K）")
chain_anchors = [
    (47, 91, mpmath.mpf("7e11"),      "84.02140326164773718764214", 23),
    (47, 92, mpmath.mpf("7.5311e11"), "89.41365947118846256456601", 23),
    (47, 91, mpmath.mpf("7.5311e11"), "90.39622715768503907626453", 23),
]
general_anchors = [
    (2,  mpmath.mpf(70),   "27.0796965", 7),
    (3,  mpmath.mpf(210),  "41.2001516", 7),
    (5,  mpmath.mpf(200),  "12.9960091", 7),
    (10, mpmath.mpf(2000), "11.8122055", 7),
]
allok = True
for m2, m, K, pinv, dec in chain_anchors:
    W = mpmath.mpf(m2) / m * K
    v = W * (d_true - 1) / (d_true ** m2 - 1)
    got = mpmath.nstr(v, dec + 2)
    same = close(got, pinv, dec)
    allok &= same
    say(f"    (m2={m2}, m={m}, K={mpmath.nstr(K,6)})  v = {got}  锚点 {pinv}  {'一致' if same else '不一致'}")
for m2, W, pinv, dec in general_anchors:
    v = W * (d_true - 1) / (d_true ** m2 - 1)
    got = mpmath.nstr(v, dec + 2)
    same = close(got, pinv, dec)
    allok &= same
    say(f"    (m2={m2:>2}, W={mpmath.nstr(W,6)})  v = {got}  锚点 {pinv}  {'一致' if same else '不一致'}")

say("\n[4] 自举定量锚点（K 上界、余量、m = 92）")
delta = d_true
K_lo_91 = mpmath.mpf(7941964418702608664581)
U91 = mpmath.mpf("1.4784") * 91 * delta ** 91
U92 = mpmath.mpf("1.4784") * 92 * delta ** 92
say(f"    K_up(91) = 1.4784·91·δ^91 = {mpmath.nstr(U91, 25)}   锚点 214072842063828923281.3586  "
    f"{'一致' if close(mpmath.nstr(U91,25), '214072842063828923281.3586', 4) else '不一致'}")
say(f"    margin(91) = 7941964418702608664581/K_up = {mpmath.nstr(K_lo_91/U91, 26)}   锚点 37.09935525747164492758953")
say(f"    U(92) = 1.4784·92·δ^92 = {mpmath.nstr(U92/10**20, 20)}e20   锚点 3.4302597024885020978e20")
say(f"    margin(92) = 77692117359936589403/U(92) = {mpmath.nstr(mpmath.mpf('77692117359936589403')/U92, 24)}"
    f"   锚点 0.226490482057595771625621")

say("\n[5] c = log2((162/97)·X0)（(A7) 里的常数）")
X0 = 695 * mpmath.mpf(2) ** 60
c = mpmath.log((mpmath.mpf(162) / 97) * X0) / mpmath.log(2)
say(f"    log2(X0) = {mpmath.nstr(mpmath.log(X0)/mpmath.log(2), 18)}（材料另记 log2(X0+1) = 69.44）")
say(f"    c = log2(162/97·X0) = {mpmath.nstr(c, 19)}   锚点 70.180806328308366825  "
    f"{'一致' if close(mpmath.nstr(c,20), '70.180806328308366825', 18) else '不一致'}")

say("\n[6] 前沿组 W 锚点：v = c 时 W = c(δ^{m2}−1)/(δ−1)")
for m2, pinw, dec in [(5, "1080.03627904", 8), (10, "11882.7608054", 7), (20, "1200678.58335", 5)]:
    W = c * (delta ** m2 - 1) / (delta - 1)
    got = mpmath.nstr(W, 25)
    say(f"    m2={m2:>3}  W = {got:>18}   锚点 {pinw:>15}  {'一致' if close(got, pinw, dec) else '不一致'}")

# --------------------------------------------- 7. 严格界机制自检（与高精度对比）
say("\n[7] 界机制自检：S_bounds 的区间必须含高精度值（多面体参数取 δ 括号下界）")
rng = Det(20261024)
bad = 0
n_ok = 0
for trial in range(40):
    m2 = rng.pick([2, 3, 5, 10])
    W = Fraction(rng.between(50, 5000), rng.pick([1, 2, 4]))
    d = D_LO6
    y = []
    s = Fraction(rng.between(1, 40), rng.pick([1, 2, 4, 8]))
    for _ in range(m2):
        y.append(s)
        s = s * d * Fraction(rng.between(1, 8), 8)
    lam = max(Fraction(1), W / sum(y))
    y = [t * lam for t in y]
    ok, _ = feasible(y, m2, d, W)
    if not ok:
        continue
    n_ok += 1
    lo, hi = S_bounds(y, *LEVEL_MID)
    ref = mpmath.mpf(0)
    for t in y:
        e = mpmath.mpf(t.numerator) / mpmath.mpf(t.denominator)   # 先算指数，再取 2^e
        ref += 3 / (mpmath.mpf(2) ** e - 1)
    lof = mpmath.mpf(lo.numerator) / mpmath.mpf(lo.denominator)
    hif = mpmath.mpf(hi.numerator) / mpmath.mpf(hi.denominator)
    if not (lof <= ref <= hif):
        bad += 1
        say(f"    !! 未包住：m2={m2} W={W}")
say(f"    {n_ok} 个可行样本：区间未包住高精度值的次数 = {bad}")
say(f"      y1..y2 = {[mpmath.nstr(mpmath.mpf(t.numerator)/t.denominator, 12) for t in y[:2]]}")
lo, hi = S_bounds(y, *LEVEL_MID)
say(f"      LEVEL_MID (k=10, s=20) 带宽相对量 = {float((hi - lo) / lo):.3e}")

say("\n[8] 顶点可行性（精确有理检查，δ 取严格括号两端与 1.585）")
for (m2, W, d, tag) in [(3, Fraction(210), D_LO, "δ_lo"), (3, Fraction(210), D_HI, "δ_hi"),
                        (3, Fraction(210), Fraction(317, 200), "1.585"), (2, Fraction(70), D_LO, "δ_lo")]:
    V = vertex(m2, d, W, 0)
    ok, badl = feasible(V, m2, d, W)
    say(f"    m2={m2} W={W} {tag:>4}  顶点可行 = {ok}  违反 = {badl}  "
        f"v = {float(V[0]):.9f}  Σy = W 精确成立 = {sum(V) == W}")

say("\n（本脚本无判定性结论，只核对定义与界机制。）")
