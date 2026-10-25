#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 第 4 轮：修正扫描网格、高精度核验 gamma、最小分母独立穷举、越界集合的结构。

F1 gamma 是否落在 (delta, delta+eps) 内（高精度，修正上一轮用 float 重建的错）
F2 区间内最小分母：在端点连分数的收敛与半收敛清单上穷举，与 Lemma 22 的 gamma 对照
F3 正确的 [L, U(92)] 扫描（对数网格 0.04 步长）与越界集合的上集结构
F4 越界门槛 K_cross 的精细二分与两侧台阶值
F5 安全集合的结构：对 K_lo < K_cross，链的每次迭代是否 ≤ K*
"""
import sys
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
from mpmath import mp, mpf, power
import r4x_core as R

OUT = []
def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)

R.set_dps(200)
L = mpf("7.5311e11")
U92 = R.sdw_upper(92)
KSTAR = 205632218873398596256
p("[F3.0] U(92) =", mp.nstr(U92, 25), "；L = 7.5311e11；K* =", KSTAR)
p()

# ---------- F1: gamma 高精度落在区间内的核验 ----------
def cf_value(quot):
    """把连分数部分商列表求值为 mpf（全 mpf 运算）。"""
    v = mpf(0)
    for a in reversed(quot):
        v = mpf(a) + (mpf(0) if v == 0 else 1 / v)
    return v

def gamma_of(alpha, beta, ndig=60):
    A = R.cf_digits(alpha, ndig)
    B = R.cf_digits(beta, ndig)
    k = 0
    while k < min(len(A), len(B)) and A[k] == B[k]:
        k += 1
    ck = min(A[k], B[k]) + 1
    quot = A[:k] + [ck]
    return cf_value(quot), k, ck, quot, A, B

p("[F1] gamma 落在 (delta, delta+eps) 内的高精度核验（dps=200）")
CASES = [(91, "7e11"), (91, "7.5311e11"), (92, "7.5311e11"), (92, "7.7692117359936589403e19"),
         (92, "2.05632218873398596256e20"), (92, "3.12e20"), (92, "3.3e20"), (92, "3.4302597024885020978e20")]
for (m, Ks) in CASES:
    r = R.psi(m, mpf(Ks))
    e = r["eps"]
    gam, k, ck, quot, A, B = gamma_of(R.DELTA, R.DELTA + e, ndig=90)
    left = (R.DELTA < gam)
    right = (gam < R.DELTA + e)
    gap_l = mp.nstr(gam - R.DELTA, 6)
    gap_r = mp.nstr(R.DELTA + e - gam, 6)
    p("     m=%d K_lo=%-22s k=%-3d ck=%-4s gamma分母=%-22s 在区间内？%s（左余 %s，右余 %s）" % (
        m, Ks, k, ck, r["psi"], left and right, gap_l, gap_r))
p()

# ---------- F2: 最小分母的独立穷举（收敛与半收敛清单） ----------
p("[F2] 区间内最小分母的独立穷举（清单 = 端点连分数的收敛与半收敛）")
def min_den_by_semiconv(alpha, beta, ndig=90):
    A = R.cf_digits(alpha, ndig)
    best = None
    # 收敛与半收敛：[A_0;...;A_{i-1}, m]，1 <= m <= A_i（i 从 1 起）
    for i in range(1, len(A)):
        pref = A[:i - 1]
        for m_ in range(1, A[i] + 1):
            q = cf_value(pref + [m_])
            if alpha < q < beta:
                # 分母
                den = None
                # 用 Fraction 求分母
                from fractions import Fraction as F
                fr = F(m_)
                for aa in reversed(pref):
                    fr = F(aa) + 1 / fr
                den = fr.denominator
                if best is None or den < best[0]:
                    best = (den, fr)
    return best

import time
for (m, Ks) in [(91, "7e11"), (91, "7.5311e11"), (92, "3.3e20")]:
    r = R.psi(m, mpf(Ks))
    e = r["eps"]
    t0 = time.time()
    b = min_den_by_semiconv(R.DELTA, R.DELTA + e, ndig=70)
    p("     m=%d K_lo=%-14s Lemma22 的 q=%-22s ；穷举清单最小分母=%-22s ；一致？%s （%.1f 秒）" % (
        m, Ks, r["psi"], b[0] if b else None, (b[0] == r["psi"]) if b else None, time.time() - t0))
p()

# ---------- F3: 正确的 [L, U] 扫描 ----------
p("[F3] [L, U(92)] 越界扫描（对数网格 0.04 步长，含 K_cross 与 U 端点）")
grid = []
for i in range(0, 260):
    grid.append(power(10, mpf(11) + mpf("0.04") * i))
grid = [g for g in grid if L <= g <= U92]
grid += [L, U92, mpf("3.0257e20"), mpf("3.1e20"), mpf("3.3e20"), mpf("3.12e20"), mpf("3.13e20"), mpf("3.15e20")]
grid = sorted(set(grid))
p("     网格点数 %d，范围 [%s, %s]" % (len(grid), mp.nstr(grid[0], 8), mp.nstr(grid[-1], 8)))
overs = []
for g in grid:
    seq, term, over = R.chain(92, g, cap=U92)
    if over:
        overs.append((g, term, len(seq)))
p("     其中链越过 U 的点数 %d / %d" % (len(overs), len(grid)))
if overs:
    p("     最小越界网格点 = %s（终值 %s）" % (mp.nstr(overs[0][0], 20), overs[0][1]))
    p("     最大不越界网格点 = %s" % mp.nstr([g for g in grid if g < overs[0][0]][-1], 20))
    p("     越界点里的 Psi 首步值集合（前 5）：", sorted(set(str(R.psi(92, g)["psi"]) for g, t, n in overs))[:5])
p("     上集结构：越界点是否连续位于网格尾部？", [i for i, g in enumerate(grid) if g in [o[0] for o in overs]] == list(range(len(grid) - len(overs), len(grid))))
p()

# ---------- F4: K_cross 精细二分 ----------
p("[F4] 最小越界起点 K_cross 的精细二分（起点 [3.12e20, 3.15e20]）")
lo, hi = mpf("3.12e20"), mpf("3.15e20")
for _ in range(200):
    mid = (lo + hi) / 2
    seq, term, over = R.chain(92, mid, cap=U92)
    if over:
        hi = mid
    else:
        lo = mid
    if hi - lo < mpf(10) ** (-18) * lo:
        break
p("     K_cross ∈ [%s, %s]" % (mp.nstr(lo, 40), mp.nstr(hi, 40)))
p("     相对宽度 = %s" % mp.nstr((hi - lo) / hi, 6))
for (nm, kv) in [("K_cross_lo", lo), ("K_cross_hi", hi)]:
    r = R.psi(92, kv)
    p("     Psi(%s) = %s (m2=%s, eps=%s)" % (nm, r["psi"], r["m2"], mp.nstr(r["eps"], 8)))
p("     与 K* = %s 比较：K_cross_lo > K* ？ %s" % (KSTAR, lo > KSTAR))
p("     与 U(92) 比较：K_cross_hi < U(92) ？ %s" % (hi < U92))
p()

# ---------- F5: 安全集合的结构 ----------
p("[F5] 对 K_lo < K_cross 的起点，链的最大迭代值是否 ≤ K*")
tests = [L, mpf("1e15"), mpf("1e18"), mpf("1e20"), mpf(KSTAR), mpf("2.5e20"), mpf("3.0e20"),
         mpf("3.1e20"), lo * mpf("0.999999"), lo * mpf("0.999999999")]
ok = True
for t in tests:
    seq, term, over = R.chain(92, t, cap=U92)
    mx = max([r["psi"] for r in seq if r["psi"] is not None] + [0])
    ok &= (not over) and (mx <= KSTAR)
    p("     K_lo=%-24s 终值=%-22s 最大迭代值=%-22s ≤K*？%s 越界？%s" % (
        mp.nstr(t, 10), term, mx, mx <= KSTAR, over))
p("     全部满足？", ok)
# 也检查 K* 本身与其右邻（K*+1 起）
for t in [mpf(KSTAR + 1), mpf("2.1e20"), mpf("2.5e20")]:
    r = R.psi(92, t)
    p("     单步核验 Psi(%s) = %s （≤K*？%s）" % (mp.nstr(t, 8), r["psi"], r["psi"] <= KSTAR))
p()

open("/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts/results/r4x_run3.out", "w").write("\n".join(OUT) + "\n")
