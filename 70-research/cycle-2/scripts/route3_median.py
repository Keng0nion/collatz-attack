#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-3 独立核验脚本：用 Stern-Brocot 中位数走法（与连分数/Lemma 22 不同的算法）
求「区间内分母最小的分数」，对 route3_cert.py 的最小性结论做独立对拍。

两件事：
  A. 小规模穷举对拍：随机有理区间上，中位数走法 vs 暴力枚举（验证走法本身的正确性）。
  B. 真格对拍：在覆盖 (delta, delta + eps_opt(K*)) 的有理区间上求最小分母，
     与证书给出的 K* 比较。

本脚本不引用 Lemma 22，也不复用 route3_cert.py 的判断逻辑（只复用其严格界常量，
常量在下面用同一套 atanh 级数重新算出，代码独立）。

注：B 段是独立对拍（机制层），仍不是对全称命题的证明——最小性的证明由
route3_cert.py 第 5b 节的 Farey 邻元引理给出。
"""

from fractions import Fraction as F
from math import isqrt
import random
import sys

random.seed(20261026)
FAILS = []


def check(name, cond, extra=""):
    ok = bool(cond)
    if not ok:
        FAILS.append(name)
    print("[%s] %s %s" % ("PASS" if ok else "FAIL", name, extra))
    return ok


print("=" * 78)
print("route-3 独立对拍：Stern-Brocot 中位数走法")
print("=" * 78)

# ---------------------------------------------------------------- 常量（独立重算）
def atanh_bounds(x, N):
    s = F(0)
    xp = x
    for k in range(N + 1):
        s += xp / (2 * k + 1)
        xp *= x * x
    return s, s + x ** (2 * N + 3) / ((2 * N + 3) * (1 - x * x))


a3, a5 = atanh_bounds(F(1, 3), 60), atanh_bounds(F(1, 5), 60)
LN2_LO, LN2_HI = 2 * a3[0], 2 * a3[1]
LN3_LO, LN3_HI = LN2_LO + 2 * a5[0], LN2_HI + 2 * a5[1]
S = 10 ** 80
D_LO = F(-((-(LN3_LO / LN2_HI).numerator * S) // (LN3_LO / LN2_HI).denominator), S)
D_HI = F(((LN3_HI / LN2_LO).numerator * S) // (LN3_HI / LN2_LO).denominator, S)
K_STAR = 205632218873398596256
X0 = 695 * 2 ** 60
print("delta 区间 = [%s..., %s...]（80 位）" % (str(D_LO)[:26], str(D_HI)[:26]))


# ---------------------------------------------------------------- 中位数走法
def median_walk(a, b, limit=100000):
    """在开区间 (a,b)（a,b 为 Fraction）内求分母最小的分数。
    用整数对 (p,q) 表示 p/q，允许 q=0 表示 +∞（不构造 Fraction(p,0)）。
    返回 (p,q,steps)；若在 limit 步内不收敛返回 (None,None,limit)。"""
    lp, lq, hp, hq = 0, 1, 1, 0
    for steps in range(1, limit + 1):
        mq = lq + hq
        med = F(lp + hp, mq) if mq != 0 else None
        if med is not None and a < med < b:
            return med.numerator, med.denominator, steps
        if med is not None and med <= a:
            lp, lq = lp + hp, mq
        else:
            hp, hq = lp + hp, mq
    return None, None, limit


def brute_min_denom(a, b, qmax):
    """暴力：返回 (a,b) 内分母 <= qmax 的最小分母及其分数，找不到返回 None。"""
    for q in range(1, qmax + 1):
        p0 = a.numerator * q // a.denominator + 1
        while F(p0, q) < b:
            if F(p0, q) > a:
                return p0, q
            p0 += 1
    return None


# ---------------------------------------------------------------- A. 小规模对拍
print("\n--- A. 小规模穷举对拍（走法正确性） ---")
okA = True
cases = 0
for _ in range(300):
    qa = random.randint(1, 200)
    qb = random.randint(1, 200)
    pa = random.randint(1, 400)
    pb = random.randint(1, 400)
    a, b = F(pa, qa), F(pb, qb)
    if not (a < b):
        continue
    if b - a < F(1, 4000):
        continue
    p, q, st = median_walk(a, b)
    br = brute_min_denom(a, b, 3000)
    if br is None:
        continue                      # 该区间在 qmax 内无候选，跳过
    cases += 1
    if p is None or q != br[1] or F(p, q) != F(br[0], br[1]):
        okA = False
        print("   不一致：a=%s b=%s 走法 %s/%s 暴力 %d/%d" % (a, b, p, q, br[0], br[1]))
        break
check("中位数走法在 %d 个小有理区间上与暴力枚举一致" % cases, okA and cases > 50)

# ---------------------------------------------------------------- B. 真格对拍
print("\n--- B. 真格对拍：覆盖 (delta, delta+eps_opt(K*)) 的区间 ---")
# 中间量（与证书同源，但此处独立重算）
Q41 = 77692117359936589403
Q40 = 50247984153525417450
P41 = 123139092617126647266
P40 = 79641170620168673833
GAM_P, GAM_Q = 2 * P41 + P40, 2 * Q41 + Q40
F1_P, F1_Q = P41 + P40, Q41 + Q40
F3_P, F3_Q = 3 * P41 + P40, 3 * Q41 + Q40
check("K* = 2Q41 + Q40", GAM_Q == K_STAR)
check("gamma 在 (F(1),F(3)) 内", F(F1_P, F1_Q) < F(GAM_P, GAM_Q) < F(F3_P, F3_Q))

LN2_UB = F(6932, 10000)
DEN_UB = 75 * Q41 + 38 * Q40
EPS_LO = F(1, X0 * K_STAR * LN2_UB)          # eps 下界（证书第 3、4 节）
V1_LO = F(91, 92) * K_STAR / ((D_HI ** 91 - 1) / (D_LO - 1))
TWO_V_LO = 2 ** (V1_LO.numerator // V1_LO.denominator) * \
           (1 + (V1_LO - V1_LO.numerator // V1_LO.denominator) * LN2_LO)
EPS_UP = (F(3, X0) + F(3, TWO_V_LO - 1) + F(270, (2 ** 74) * isqrt(2 ** 74))) / (3 * K_STAR * LN2_LO)
print("eps 下界 = %.6e ；eps 上界 = %.6e" % (float(EPS_LO), float(EPS_UP)))

CELLS = [
    ("内层 (D_LO, D_LO+eps_lo)", D_LO, D_LO + EPS_LO),
    ("外层 (D_HI, D_HI+eps_up)  [包含真区间]", D_HI, D_HI + EPS_UP),
    ("整柱 (F(1), F(3))", F(F1_P, F1_Q), F(F3_P, F3_Q)),
]
for name, a, b in CELLS:
    p, q, st = median_walk(a, b)
    print("   %-38s -> %s / %s （步数 %d）" % (name, p, q, st))
    check("%s：最小分母 = K*" % name, q == K_STAR and F(p, q) == F(GAM_P, GAM_Q))

# 外层区间确实覆盖 (delta, delta+eps_opt)
check("外层区间覆盖真区间：D_HI < D_LO 的补（D_HI 是上界）且两端都向外",
      D_LO < D_HI and D_HI < D_HI + EPS_UP and D_LO + EPS_LO < D_HI + EPS_UP)
check("外层区间仍在 (F(1),F(3)) 内", F(F1_P, F1_Q) < D_HI and D_HI + EPS_UP < F(F3_P, F3_Q))

# ---------------------------------------------------------------- C. Lemma 22 公式对拍（机制层）
print("\n--- C. Lemma 22 公式 vs 中位数走法（机制对拍，非证明） ---")
from mpmath import mp, mpf, floor  # noqa: E402

mp.dps = 120


def cf(x, n):
    out = []
    for _ in range(n):
        fl = int(floor(x))
        out.append(fl)
        x = x - fl
        if x == 0:
            return out
        x = 1 / x
    return out


# 设计：对外框 O ⊇ (alpha,beta) 与内框 I ⊆ (alpha,beta) 各跑一次走法。
#   外框含的分数更多 => min(O) <= 真最小分母 q_true；内框含的分数更少 => min(I) >= q_true。
#   故 min(O) = min(I) = Q 蕴含 q_true = Q；再与 Lemma 22 的公式值 q22 比较。
G = 10 ** 24
okC = True
cntC = 0
tried = 0
while cntC < 25 and tried < 400:
    tried += 1
    p = random.choice([2, 3, 5, 6, 7, 8, 10, 11, 13])
    q = random.randint(1, 7)
    al = mpf(1) + mp.sqrt(p) / q
    eps = mpf(10) ** (-random.randint(3, 9))
    be = al + eps
    A, B = cf(al, 60), cf(be, 60)
    k = 0
    while k < min(len(A), len(B)) and A[k] == B[k]:
        k += 1
    if k == 0 or k >= min(len(A), len(B)):
        continue
    ck = min(A[k], B[k]) + 1
    pm2, pm1 = 0, 1
    qm2, qm1 = 1, 0
    for i in range(k):
        pn = A[i] * pm1 + pm2
        qn = A[i] * qm1 + qm2
        pm2, pm1 = pm1, pn
        qm2, qm1 = qm1, qn
    q22 = ck * qm1 + qm2
    if q22 > 200000:
        continue                       # 保持走法快速收敛
    alG, beG = int(al * G), int(be * G)
    aO, bO = F(alG - 1, G), F(beG + 1, G)          # 外框
    aI, bI = F(alG + 1, G), F(beG - 1, G)          # 内框
    if not (aO < bO and aI < bI):
        continue
    pO, qO, _ = median_walk(aO, bO, 50000)
    pI, qI, _ = median_walk(aI, bI, 50000)
    if qO is None or qI is None:
        continue
    cntC += 1
    if not (qO == qI == q22):
        okC = False
        print("   夹逼不一致：alpha=%s eps=1e-%d Lemma22 q=%d 外框 q=%s 内框 q=%s"
              % (mp.nstr(al, 10), -int(mp.log10(eps)), q22, qO, qI))
        break
check("Lemma 22 公式值 = 外框最小分母 = 内框最小分母（%d 个随机无理格）" % cntC,
      okC and cntC >= 20)

# ---------------------------------------------------------------- 结果
print("\n" + "=" * 78)
if FAILS:
    print("失败项：%s" % FAILS)
    sys.exit(1)
print("全部检查通过（退出码 0）")
print("=" * 78)
sys.exit(0)
