#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 第 2 轮：Psi 的补验、m = 92 链条的起点扫描、越界见证。

S1 项目 11 点网格逐点独立复算
S2 非降性网格检验（对数网格，236 点）
S3 不动点与台阶值集
S4 越界扫描：[L, U(92)] 内找一切让链越过 U 的起点，二分求最小越界起点
S5 越界见证的台阶稳健性（eps 乘因子后 Psi 不变）与两级精度一致
S6 Lemma 22 公式对暴力最小分母的对照（无理 alpha 情形）与 gamma 落在区间内的核验
"""
import sys
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
from fractions import Fraction
from mpmath import mp, mpf, power, pi, e as me, sqrt
import r4x_core as R

OUT = []
def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)

R.set_dps(120)
L = mpf("7.5311e11")
U92 = R.sdw_upper(92)
p("[S0] U(92) = 1.4784*92*delta^92 =", mp.nstr(U92, 25), "； L = 7.5311e11")
p()

# ---------------- S1 ----------------
GRID = [("7.5311e11", 5267319278509397), ("1e15", 130441933147714940),
        ("1e18", 4640282259296926456), ("1e20", 205632218873398596256),
        ("2.05632218873398596256e20", 205632218873398596256),
        ("2.5e20", 205632218873398596256), ("3.0e20", 205632218873398596256),
        ("3.0257e20", 205632218873398596256), ("3.1e20", 205632218873398596256),
        ("3.3e20", 7941964418702608664581),
        ("3.4302597024885020978e20", 15678296618531818732906)]
p("[S1] 项目 11 点网格逐点复算（右列为 rederivation-erratum.md:281 至 :291 记载值）")
allok = True
for (Ks, ref) in GRID:
    r = R.psi(92, mpf(Ks))
    ok = (r["psi"] == ref)
    allok &= ok
    p("     K_lo=%-24s m2=%-3s eps=%-14s Psi=%-22s 记载=%-22s 一致=%s" % (
        Ks, r["m2"], mp.nstr(r["eps"], 6), r["psi"], ref, ok))
p("     11 点全部逐位一致？", allok)
p()

# ---------------- S2 ----------------
p("[S2] 非降性网格：K_lo = 10^(11 + 0.004 k)，k = 0..235（覆盖 1e11 至 3.6e20）")
ks = []
for i in range(236):
    kk = power(10, 11 + 0.004 * i)
    r = R.psi(92, kk)
    ks.append((kk, r["psi"], r["m2"], r["eps"]))
bad = [(ks[i - 1], ks[i]) for i in range(1, len(ks)) if ks[i][1] < ks[i - 1][1]]
p("     点数 %d；相邻下降次数 %d" % (len(ks), len(bad)))
p("     首点 %s -> %s ；末点 %s -> %s" % (mp.nstr(ks[0][0], 8), ks[0][1], mp.nstr(ks[-1][0], 8), ks[-1][1]))
p("     值集（按 K 升序首次出现）：")
seen = []
for (kk, ps, m2, ee) in ks:
    if not seen or seen[-1][1] != ps:
        seen.append((kk, ps, m2, ee))
for s in seen:
    p("       自 K_lo=%s 起 Psi=%s (m2=%s, eps=%s)" % (mp.nstr(s[0], 8), s[1], s[2], mp.nstr(s[3], 6)))
p()

# ---------------- S3 ----------------
p("[S3] 不动点与台阶")
Kstar = 205632218873398596256
for Ks in [Kstar - 1, Kstar, Kstar + 1, 77692117359936589402, 77692117359936589403, 77692117359936589404]:
    r = R.psi(92, mpf(Ks))
    p("     K_lo=%-22s -> Psi=%-22s (m2=%s, eps=%s)" % (Ks, r["psi"], r["m2"], mp.nstr(r["eps"], 6)))
gridfixed = [(kk, ps) for (kk, ps, m2, ee) in ks if ps == kk]
p("     网格上 Psi(K_lo) == K_lo 的精确不动点数：%d" % len(gridfixed))
p("     Psi 在 K* 处是否恰为 K*？", R.psi(92, mpf(Kstar))["psi"] == Kstar)
p()

# ---------------- S4 ----------------
p("[S4] 越界扫描：链的某次迭代 > U(92) 即算越过")
def over_chain(K0):
    return R.chain(92, K0, cap=U92)

inrange = [(kk, ps, m2, ee) for (kk, ps, m2, ee) in ks if L <= kk <= U92]
res = []
for (kk, ps, m2, ee) in inrange:
    seq, term, over = over_chain(kk)
    res.append((kk, over, term, len(seq)))
n_over = sum(1 for r in res if r[1])
p("     [L, U] 内网格点数 %d；其中越界 %d" % (len(res), n_over))
fo = [r for r in res if r[1]]
if fo:
    p("     网格上首个越界起点 %s（终值 %s，步数 %d）" % (mp.nstr(fo[0][0], 12), fo[0][2], fo[0][3]))
    p("     越界起点的 Psi 值集合：", sorted(set(str(R.psi(92, r[0])["psi"]) for r in fo))[:5])
# 二分
lo = mpf("3.05e20")
hi = mpf("3.30e20")
for _ in range(120):
    mid = (lo + hi) / 2
    seq, term, over = over_chain(mid)
    if over:
        hi = mid
    else:
        lo = mid
p("     二分（起点 [3.05e20, 3.30e20]，120 轮）：最小越界起点 ∈ [%s, %s]" % (mp.nstr(lo, 30), mp.nstr(hi, 30)))
p("     该区间长度 = %s" % mp.nstr(hi - lo, 6))
r_lo = R.psi(92, lo); r_hi = R.psi(92, hi)
p("     Psi(lo)=%s (m2=%s, eps=%s)" % (r_lo["psi"], r_lo["m2"], mp.nstr(r_lo["eps"], 6)))
p("     Psi(hi)=%s (m2=%s, eps=%s)" % (r_hi["psi"], r_hi["m2"], mp.nstr(r_hi["eps"], 6)))
p("     阈值 U(92)/K_cross 附近：U(92)=%s, lo=%s, hi=%s" % (mp.nstr(U92, 22), mp.nstr(lo, 22), mp.nstr(hi, 22)))
p()

# ---------------- S5 ----------------
p("[S5] 越界见证 K_lo = 3.3e20 的稳健性")
for sc in ["1", "0.999", "1.001", "0.999999", "1.000001", "0.99", "1.01"]:
    r = R.psi(92, mpf("3.3e20"), eps_scale=sc)
    p("     eps*%-10s -> m2=%s Psi=%-22s >U(92)？%s" % (sc, r["m2"], r["psi"], r["psi"] > U92))
r120 = R.psi(92, mpf("3.3e20"))
R.set_dps(400)
r400 = R.psi(92, mpf("3.3e20"))
p("     自动精度(dps=%s) -> %s ；强制 dps=400 -> %s ；一致？%s" % (
    r120["dps"], r120["psi"], r400["psi"], r120["psi"] == r400["psi"]))
R.set_dps(120)
p()

# ---------------- S6 ----------------
p("[S6] Lemma 22 公式对暴力最小分母的对照")
def brute_min_den(a, b, QMAX):
    for q in range(1, QMAX + 1):
        lo_ = a * q
        if lo_.denominator != 1:
            pc = lo_.numerator // lo_.denominator + 1
        else:
            pc = lo_.numerator + 1
        if Fraction(pc, q) < b:
            return q
    return None

tests = [(me, "e"), (pi, "pi"), (sqrt(2), "sqrt2"), (R.DELTA, "delta")]
for (al, nm) in tests:
    for t in [4, 6, 8, 10]:
        eps = mpf(10) ** (-t)
        q_cf, k, A_, B_ = R.qmin_interval(al, al + eps)
        # 用高精度有理端点做暴力（alpha 真值未知，取 60 位小数近似为有理数，误差远小于 1e-40）
        a = Fraction(mp.nstr(al, 60))
        b = a + Fraction(1, 10 ** t)
        q_bf = brute_min_den(a, b, 4000000)
        p("     alpha=%-7s eps=1e-%-3d cf=%-12s k=%-3d brute=%-12s 一致=%s" % (
            nm, t, q_cf, k, q_bf, q_cf == q_bf))
p()
p("[S6b] 实际链条区间的 gamma 是否落在 (delta, delta+eps) 内")
for (mk, Ks) in [(91, mpf("7e11")), (91, mpf("7.5311e11")), (92, mpf("7.5311e11")),
                 (92, mpf("7.7692117359936589403e19")), (92, mpf("3.3e20"))]:
    r = R.psi(mk, Ks)
    e = r["eps"]
    gamma_num, gamma_den = None, r["psi"]
    # gamma 的小数值：用连分数前缀重建
    dg = r["digits"]
    from mpmath import mpf as _m
    # 直接检查：qmin 分母处存在一个分数落在区间内（用 Stern-Brocot 搜索的替代：检验 gamma 的具体数值）
    # gamma = [A[0];...;A[k-1], ck]，这里用 mpmath 重建
    A_ = R.cf_digits(R.DELTA, dg + 5)
    # 找出 k
    B_ = R.cf_digits(R.DELTA + e, dg + 5)
    k = 0
    while k < min(len(A_), len(B_)) and A_[k] == B_[k]:
        k += 1
    ck = min(A_[k], B_[k]) + 1
    pref = A_[:k] + [ck]
    val = mpf(0)
    for a_ in reversed(pref):
        val = a_ + (0 if val == 0 else 1 / val)
    inside = (R.DELTA < val < R.DELTA + e)
    p("     m=%d K_lo=%-24s k=%-3d ck=%-4s gamma=%-30s 在 (delta,delta+eps) 内？%s" % (
        mk, mp.nstr(Ks, 10), k, ck, mp.nstr(val, 12), inside))
p()

open("/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts/results/r4x_run2.out", "w").write("\n".join(OUT) + "\n")
