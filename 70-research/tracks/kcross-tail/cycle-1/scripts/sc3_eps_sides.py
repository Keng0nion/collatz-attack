#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽验 3：A1 的 92 项（在精确 T_hi 上）与 B2 的符号（在精确 T_lo 上），并做第二引擎对拍。

引擎 1：本路 kc_tail_rig（精确有理区间，GRID = 10^230）
引擎 2：mpmath.iv（dps = 260，独立实现、独立舍入模型）
命令行：/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python sc3_eps_sides.py
"""
import hashlib
import re
import sys
from decimal import Decimal, getcontext
from fractions import Fraction as F

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1/scripts")
import kc_tail_rig as R
from mpmath import iv, mp, mpf, log, exp

PROOF = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts/results"
R2LOG = PROOF + "/r2_threshold_cert.log"
OUTPATH = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1/scripts/results/sc3_out.txt"
GAMMA = F(325919355854421968365, 205632218873398596256)
getcontext().prec = 400

out = []


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.append(s)


def dec(x, n=25):
    return format(Decimal(x.numerator) / Decimal(x.denominator), ".%de" % (n - 1))


txt = open(R2LOG, encoding="utf-8").read()
T_hi = F(*[int(g) for g in re.search(r"T_hi 的精确有理 = (\d+)/(\d+)", txt).groups()])
T_lo = F(*[int(g) for g in re.search(r"T_lo 的精确有理 = (\d+)/(\d+)", txt).groups()])

dlo, dhi = R.delta_bounds()
l2 = R.ln2_bounds()
gm = R.isub((R.rd(GAMMA), R.ru(GAMMA)), (dlo, dhi))       # gamma - delta 的区间

p("#" * 78)
p("# kcross-tail 路线 2 抽验 3：A1 的 92 项与 B2 的符号（双引擎）")
p("#   r2_threshold_cert.log md5 %s" % hashlib.md5(open(R2LOG, "rb").read()).hexdigest())
p("#" * 78)
p("")
p("[0] 输入与常数")
p("    T_hi = %s" % dec(T_hi, 40))
p("    T_lo = %s" % dec(T_lo, 40))
p("    gamma - delta ∈ [%s, %s]（本路区间）" % (dec(gm[0], 20), dec(gm[1], 20)))
p("")

p("[1] F_92(T_hi) 与 F_92(T_lo)（可行集，本路判据 geom(m2)*C <= (m2/92)K）")
Civ = R.C_bounds()
for name, K in (("T_hi", T_hi), ("T_lo", T_lo)):
    feas = [m for m in range(1, 93) if R.feasible_decision(m, 92, K, dlo, dhi, Civ) is True]
    und = [m for m in range(1, 93) if R.feasible_decision(m, 92, K, dlo, dhi, Civ) is None]
    p("    %s：可行 %d 个，未定 %d 个；最小可行 = %d，最大可行 = %d；= {1..92} ？ %s" % (
        name, len(feas), len(und), min(feas), max(feas), feas == list(range(1, 93))))
p("")

p("[2] 证书 A：A1 的 92 项（每项 eps(m2, T_hi)_下界 > (γ-δ)_上界）")
rows = []
for m2 in range(1, 93):
    e = R.eps_bounds(m2, 92, T_hi, dlo, dhi, l2)
    rows.append((e[0] - gm[1], m2))
rows.sort()
p("    全部 92 项通过？ %s ；最小余量 = %s，在 m2 = %d 处" % (
    all(r[0] > 0 for r in rows), dec(rows[0][0], 8), rows[0][1]))
p("    前三小：%s；%s；%s" % tuple("m2=%d 余量=%s" % (r[1], dec(r[0], 8)) for r in rows[:3]))
p("    对照 r2 日志 :64 至 :67：最小余量 m2 = 92 处 1.075910e-163；")
p("      eps(92,T_hi) = 6.2446806696927356e-43；m2 = 91 余量 5.124296e-42；m2 = 90 余量 8.850347e-42")
p("")

p("[3] 证书 B：B2 的符号（eps(92, T_lo)_上界 < (γ-δ)_下界）")
e_lo = R.eps_bounds(92, 92, T_lo, dlo, dhi, l2)
p("    eps(92, T_lo) ∈ [%s, %s]" % (dec(e_lo[0], 22), dec(e_lo[1], 22)))
p("    上界 - (γ-δ)_下界 = %s ；< 0 ？ %s" % (dec(e_lo[1] - gm[0], 8), e_lo[1] - gm[0] < 0))
p("    对照 r2 日志 :85 至 :87：eps ∈ [6.2446806696927356e-43, 同值]，负余量 -1.136322e-164")
p("")

p("[4] 第二引擎（mpmath.iv，独立实现）复核两个关键符号")
iv.dps = 260


def s_iv(K, m2):
    """mpmath.iv 下的 eps(m2, 92, K) - (gamma - delta)，K 为精确有理数。"""
    Kiv = iv.mpf(K.numerator) / iv.mpf(K.denominator)
    div = iv.mpf(3)
    Kiv = iv.mpf(K.numerator) / iv.mpf(K.denominator)
    d = iv.log(iv.mpf(3)) / iv.log(iv.mpf(2))
    gm_iv = iv.mpf(GAMMA.numerator) / iv.mpf(GAMMA.denominator) - d
    pw = iv.exp(iv.mpf(m2) * d * 0) if False else iv.exp(iv.mpf(92) * iv.log(d))  # δ^92
    v = iv.mpf(m2) / iv.mpf(92) * Kiv * (d - 1) / (pw - 1)
    tv = iv.exp(v * iv.log(iv.mpf(2)))
    num = iv.mpf(R.A_of(m2, 92).numerator) / iv.mpf(R.A_of(m2, 92).denominator) \
        + iv.mpf(3) / (tv - 1) + iv.mpf(3 * (m2 - 1)) / iv.exp(d * iv.log(tv - 1))
    den = iv.mpf(3) * Kiv * iv.log(iv.mpf(2))
    return num / den - gm_iv


for tag, K, m2 in (("A1 临界项 m2=92 @ T_hi", T_hi, 92), ("B2 临界项 m2=92 @ T_lo", T_lo, 92),
                   ("A1 次小项 m2=90 @ T_hi", T_hi, 90), ("A1 第三 m2=91 @ T_hi", T_hi, 91)):
    s = s_iv(K, m2)
    lo, hi = s.a, s.b
    p("    %s：S ∈ [%s, %s]" % (tag, mp.nstr(lo, 12), mp.nstr(hi, 12)))
    p("       符号确定？ %s（%s）" % (lo > 0 or hi < 0, "正" if lo > 0 else ("负" if hi < 0 else "未定")))
p("")

p("[5] 二分前提检查：S(3.12e20) > 0 > S(3.15e20)（本路引擎）")
for tag, K in (("3.12e20", F(312) * 10 ** 18), ("3.15e20", F(315) * 10 ** 18)):
    s1 = R.eps_bounds(92, 92, K, dlo, dhi, l2)
    v = s1[0] - gm[1], s1[1] - gm[0]
    p("    K = %s：S ∈ [%s, %s] ；符号 = %s" % (tag, dec(v[0], 8), dec(v[1], 8),
                                            "正" if v[0] > 0 else ("负" if v[1] < 0 else "未定")))
open(OUTPATH, "w").write("\n".join(out) + "\n")
p("")
p("[写出] scripts/results/sc3_out.txt")
