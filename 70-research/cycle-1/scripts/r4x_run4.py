#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 第 5 轮：两处修正与复验。

G1 delta 锚点：钉住的 40 位小数与严格有理区间 dlo/dhi 的前 40 位是否逐位一致
G2 区间内最小分母的独立穷举（修正上一轮的清单下标错位）：
   清单 = { [A_0;...;A_(j-1), m] : 1 <= j <= k+1, 1 <= m <= A_j }（alpha 侧）
        ∪ { [B_0;...;B_(j-1), m] : 1 <= j <= k+1, 1 <= m <= B_j }（beta 侧）
   标准结论：区间内最小分母的分数必为端点连分数的收敛或半收敛（best approximation
   of the second kind）。据此在清单内穷举并取最小分母，与 Lemma 22 的 gamma 对照。
"""
import sys
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
from fractions import Fraction as F
from mpmath import mp, mpf
import r4x_core as R
import r4x_rig_helpers as H

OUT = []
def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)

# ---------- G1 ----------
dlo, dhi = H.delta_bounds()
p("[G1] delta 严格有理区间（atanh 级数，N=%d）" % H.N)
p("     dlo 的 45 位小数 = " + H.dec_str(dlo, 45))
p("     dhi 的 45 位小数 = " + H.dec_str(dhi, 45))
PIN = "1.58496250072115618145373894394781650875981440769248106045575"
p("     materials.md:62 钉住的 40 位 = " + PIN)
p("     前 40 位逐位一致（对 dlo）？ " + str(H.dec_str(dlo, 40) == PIN[:42]))
p("     前 40 位逐位一致（对 dhi）？ " + str(H.dec_str(dhi, 40) == PIN[:42]))
p("     区间宽度 = " + str(float(dhi - dlo)))
p()

# ---------- G2 ----------
R.set_dps(200)

def cf_value_frac(quot):
    v = F(0)
    for a in reversed(quot):
        v = F(a) + (F(0) if v == 0 else 1 / v)
    return v

def min_den_exhaustive(alpha, beta, ndig=80, cap_q=None):
    A = R.cf_digits(alpha, ndig)
    B = R.cf_digits(beta, ndig)
    k = 0
    while k < min(len(A), len(B)) and A[k] == B[k]:
        k += 1
    best = None
    best_src = None
    inspected = 0
    for (src, S) in (("alpha", A), ("beta", B)):
        for j in range(1, min(k + 2, len(S))):
            pref = S[:j]
            for m_ in range(1, S[j] + 1):
                quot = pref + [m_]
                fr = cf_value_frac(quot)
                inspected += 1
                if cap_q is not None and fr.denominator >= cap_q:
                    break
                val = mpf(fr.numerator) / fr.denominator
                if alpha < val < beta:
                    if best is None or fr.denominator < best:
                        best = fr.denominator
                        best_src = (src, j, m_, fr)
                    break
    return best, best_src, k, inspected

p("[G2] 区间内最小分母穷举（修正清单）对 Lemma 22 的 gamma 值")
CASES = [(91, "7e11"), (91, "7.5311e11"), (92, "7.5311e11"),
         (92, "7.7692117359936589403e19"), (92, "3.3e20"), (92, "3.4302597024885020978e20")]
for (m, Ks) in CASES:
    r = R.psi(m, mpf(Ks))
    e = r["eps"]
    best, src, k, insp = min_den_exhaustive(R.DELTA, R.DELTA + e, ndig=80, cap_q=r["psi"] + 1)
    p("     m=%d K_lo=%-22s k=%-3d Lemma22 q=%-22s ；穷举最小分母=%-22s ；一致？%s ；清单（%s，下标 %s，m=%s）；检查条数 %s" % (
        m, Ks, k, r["psi"], best, best == r["psi"], src[0] if src else None,
        src[1] if src else None, src[2] if src else None, insp))
p()

# ---------- G3: 反向核验：区间内是否存在分母更小的分数（直接搜索小分母） ----------
p("[G3] 小分母直接搜索：对若干 q < q_gamma，检验是否存在 p 使 p/q 落在区间内")
for (m, Ks) in [(91, "7e11"), (92, "3.3e20")]:
    r = R.psi(m, mpf(Ks))
    e = r["eps"]
    qg = r["psi"]
    found = None
    for q in [1, 2, 3, 5, 10, 100, 1000, 10 ** 6, 10 ** 9, 10 ** 12, qg - 1]:
        lo_ = R.DELTA * q
        pc = int(mp.floor(lo_)) + 1
        if mpf(pc) / q < R.DELTA + e:
            found = (q, pc)
            break
    p("     m=%d K_lo=%-10s q_gamma=%-22s ；q<q_gamma 内首个命中：%s" % (m, Ks, qg, found))

open("/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts/results/r4x_run4.out", "w").write("\n".join(OUT) + "\n")
