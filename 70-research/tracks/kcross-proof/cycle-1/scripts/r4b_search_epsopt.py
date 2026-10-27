#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 4 路任务 (b)：K ∈ (K*, 3.15×10^20) 上找 eps_opt(K) ≠ eps(92, K) 的点。

目标：凡是「eps_opt 由 m2 = 92 支配」的断言，在哪些 K 上失效。分两类：
  B1：m2 = 92 不可行（K < c_92，c_92 为 m2 = 92 的可行门槛）——此时 eps_opt 由
      其他 m2 取到，与「公式值 eps(92,K)」是两个不同的数；
  B2：m2 = 92 可行但 argmin ≠ 92——即 route-5 §4.4 的两种约定分岔窗口，
      窗口相对宽度在项目里被登记为约 2×10^-24。

用严格有理区间逐点判定（eps_bounds + 分离判据）。门槛邻域覆盖：c_92 的严格区间
端点、相对偏移 10^-27 至 10^-6 共十余个尺度，以及 K*、3.15e20 附近的整数点。

附：分岔窗口的解析量化——窗口由
    3/(2^v - 1) 与 A(j-1) - A(j) = 97/(54 X0) 的交点决定（j <= m-2 时），
该交点的 v 满足 2^v = 2^C + 1；本脚本给出 log2(1 + 2^-C) 的严格区间与
K 中的相对窗口宽度的严格区间，并判定 route-5 登记的「约 2×10^-24」是否落在区间内。

运行：/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python r4b_search_epsopt.py
"""
import sys
import math
import random
import time

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
sys.path.insert(0, HERE)
from fractions import Fraction as F
import r4_common as C

OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


t_start = time.time()
DLO, DHI, L2 = C.consts()
CIV = C.R.C_bounds()
HI_END = F(315) * 10 ** 18          # 3.15×10^20

p("#" * 74)
p("# 任务 (b)：(K*, 3.15e20) 上 eps_opt(K) 与 eps(92, K) 的分离搜索")
p("# 脚本：tracks/kcross-proof/cycle-1/scripts/r4b_search_epsopt.py")
p("#" * 74)
p("")

# ---------- [0] 门槛表 ----------
p("[0] 可行门槛 c_j = (92/j) * geom(j) * C 的严格区间（j = 86 至 92）")
thr = {}
for j in range(86, 93):
    g = C.R.geom_bounds(j, DLO, DHI)
    c_lo = C.R.rd(g[0] * CIV[0] * F(92, j))
    c_hi = C.R.ru(g[1] * CIV[1] * F(92, j))
    thr[j] = (c_lo, c_hi)
    p("    c_%d ∈ [%s, %s]" % (j, C.dec(c_lo, 30), C.dec(c_hi, 30)))
p("    c_91_hi < K* ？ %s ；K* < c_92_lo ？ %s ；c_92_hi < 3.15e20 ？ %s" % (
    thr[91][1] < C.KSTAR, C.KSTAR < thr[92][0], thr[92][1] < HI_END))
p("    -> (K*, 3.15e20) 内唯一门槛是 c_92；c_91 及其以下都在 K* 之下。")

# ---------- [1] 采样点 ----------
pts = []
mid92 = (thr[92][0] + thr[92][1]) / 2
pts.append(C.KSTAR + 1)
pts.append(C.KSTAR + 2)
pts.append((C.KSTAR + mid92) / 2)
pts.append(mid92 - 1)
pts.append(mid92)
pts.append(mid92 + 1)
offs = ["-1e-27", "-1e-26", "-1e-25", "-5e-25", "-2e-24", "-4e-24", "-1e-23",
        "-1e-22", "-1e-21", "-1e-20", "-1e-18", "-1e-15", "-1e-12", "-1e-9", "-1e-6",
        "1e-27", "1e-26", "1e-25", "5e-25", "2e-24", "4e-24", "1e-23",
        "1e-22", "1e-21", "1e-20", "1e-18", "1e-15", "1e-12", "1e-9", "1e-6"]
for o in offs:
    d = F(o)
    K = mid92 * (1 + d)
    pts.append(F(int(K)))
# 对数网格 + 随机
rng = random.Random(20261028)
lo_f, hi_f = float(C.KSTAR + 1), float(HI_END)
for i in range(200):
    x = lo_f * (hi_f / lo_f) ** (i / 199)
    pts.append(F(int(x) + 1))
for _ in range(100):
    x = math.exp(rng.uniform(math.log(lo_f), math.log(hi_f)))
    pts.append(F(int(x) + 1))
pts.append(HI_END - 1)
pts.append(HI_END)
allp = []
seen = set()
for K in pts:
    if K in seen:
        continue
    if C.KSTAR < K <= HI_END:
        seen.add(K)
        allp.append(K)
allp.sort()
p("")
p("[1] 采样点：%d 个（含 c_92 邻域 30 个相对偏移点、对数网格 200、随机 100）" % len(allp))

# ---------- [2] 逐点判定 ----------
p("")
p("[2] 逐点判定（eps_opt 区间、argmin、与 eps(92,K) 的严格比较）")
rows = []
t1 = time.time()
n_b1 = n_b2 = n_eq = n_und = 0
for K in allp:
    info = C.eps_opt(K, CIV, DLO, DHI, L2)
    feas = info["feas"]
    f92 = 92 in feas
    arg = info["argmin"]
    e92 = info["e92"]
    lo_opt, hi_opt = info["lo"], info["hi"]
    # 与 eps(92,K) 的严格比较
    if lo_opt is None:
        rel = "no-feas"
    elif hi_opt < e92[0]:
        rel = "eps_opt < eps92"
    elif e92[1] < lo_opt:
        rel = "eps_opt > eps92"
    else:
        rel = "indistinguishable"
    if rel == "indistinguishable":
        n_eq += 1
    elif rel in ("eps_opt < eps92", "eps_opt > eps92"):
        if not f92:
            n_b1 += 1
        else:
            n_b2 += 1
    else:
        n_und += 1
    rows.append((K, f92, arg, len(feas), rel,
                 C.dec(lo_opt, 44) if lo_opt is not None else None,
                 C.dec(hi_opt, 44) if hi_opt is not None else None,
                 C.dec(e92[0], 44), C.dec(e92[1], 44)))
p("    逐点用时 %.1f 秒" % (time.time() - t1))

p("")
p("[3] 汇总")
p("    点数 = %d" % len(allp))
p("    类型 B1（92 不可行且 eps_opt 与 eps(92,K) 数值可分离）= %d" % n_b1)
p("    类型 B2（92 可行但 eps_opt 与 eps(92,K) 数值可分离）= %d" % n_b2)
p("    不可分离（= eps_opt 由 92 支配且区间相叠）= %d" % n_eq)
p("    其他/未定 = %d" % n_und)

# 细分：按 92 可行与否统计
n_feas92 = sum(1 for r in rows if r[1])
p("    其中 92 可行的点 = %d ；92 不可行的点 = %d" % (n_feas92, len(rows) - n_feas92))
argcnt = {}
for r in rows:
    argcnt[r[2]] = argcnt.get(r[2], 0) + 1
p("    argmin 分布（前 10）：%s" % sorted(argcnt.items(), key=lambda kv: -kv[1])[:10])

# 分岔窗口邻域细表（相对偏移点）
p("")
p("[4] c_92 邻域细表（相对 c_92 中点的偏移，判定 argmin 与 eps 比较）")
p("    c_92 中点 = %s" % C.dec(mid92, 30))
for K in allp:
    d = (F(K) - mid92) / mid92
    f = float(d)
    if abs(f) < 1e-5 and K != mid92:
        info = C.eps_opt(K, CIV, DLO, DHI, L2)
        arg = info["argmin"]
        e92 = info["e92"]
        rel = "-"
        if info["lo"] is not None:
            if info["hi"] < e92[0]:
                rel = "<"
            elif e92[1] < info["lo"]:
                rel = ">"
            else:
                rel = "="
        p("    K = %s 相对偏移 %+.3e 92可行=%s argmin=%s eps_opt vs eps92: %s" % (
            K, f, 92 in info["feas"], arg, rel))

# ---------- [5] eps(92,.) = eps(91,.) 交点 K0（在 (K*, c_92) 内） ----------
p("")
p("[5] eps(92,K) 与 eps(91,K) 的交点 K0（在 (K*, c_92) 内；边界标注用）")


def cmp92_91(K):
    """返回 'e92<e91'、'e92>e91' 或 None（区间重叠）。"""
    a = C.R.eps_bounds(92, 92, K, DLO, DHI, L2)
    b = C.R.eps_bounds(91, 92, K, DLO, DHI, L2)
    if a[1] < b[0]:
        return "e92<e91"
    if b[1] < a[0]:
        return "e92>e91"
    return None


KA, KB = C.KSTAR + 1, thr[92][0] - 1
cA, cB = cmp92_91(KA), cmp92_91(KB)
p("    左端 K = K*+1：%s ；右端 K = c_92_lo-1：%s" % (cA, cB))
K0A, K0B = KA, KB
if cA is not None and cB is not None and cA != cB:
    for _ in range(90):
        Km = (K0A + K0B) / 2
        cm = cmp92_91(Km)
        if cm is None:
            break
        if cm == cA:
            K0A = Km
        else:
            K0B = Km
    p("    交点 K0 ∈ [%s, %s]（90 步二分；宽度 %s）" % (
        C.dec(K0A, 30), C.dec(K0B, 30), C.fnum(K0B - K0A)))
    p("    含义：K < K0 时 eps(92,K) > eps(91,K)（92 格数值更差）；")
    p("          K0 < K < c_92 时 eps(92,K) < eps(91,K) 但 92 仍不可行，")
    p("          故 eps_opt 仍不是 eps(92,K)（这两段都属类型 B1）。")
else:
    p("    端点符号未分离，交点未定位。")

# ---------- [6] 分岔窗口宽度（解析） ----------
p("")
p("[6] 两种约定分岔窗口的解析量化（j <= m-2 的情形）")
p("    窗口由 3/(2^v - 1) 与 A(j-1)-A(j) = 97/(54 X0) 的交点决定；")
p("    该交点满足 2^v = 2^C + 1，即 v* = C + log2(1 + 2^-C)。")
twoC = C.R.exp_bounds(C.R.rd(CIV[0] * L2[0]), C.R.ru(CIV[1] * L2[1]))
one_plus = (C.R.rd(1 + 1 / twoC[1]), C.R.ru(1 + 1 / twoC[0]))
lb = C.R.ln_bounds(one_plus[0])[0], C.R.ln_bounds(one_plus[1])[1]
w_lo = C.R.rd(lb[0] / L2[1])
w_hi = C.R.ru(lb[1] / L2[0])
p("    2^C ∈ [%s, %s]" % (C.dec(twoC[0], 30), C.dec(twoC[1], 30)))
p("    log2(1 + 2^-C) ∈ [%s, %s]" % (C.dec(w_lo, 30), C.dec(w_hi, 30)))
p("    v 中的窗口宽度（= 上式）；K 中的相对窗口宽度 ∈ [%s, %s]" % (
    C.dec(w_lo / CIV[1], 30), C.dec(w_hi / CIV[0], 30)))
p("    对照 route-5.md:230 的登记「窗口宽度 ≈ 2×10^-24（相对）」：")
p("      它落在本脚本区间内？ %s" % (
    w_lo / CIV[1] <= F(2, 10 ** 24) <= w_hi / CIV[0]))
p("    注：该登记的两个数字（v 中 1.5e-22、相对 2e-24）与本脚本的严格区间")
p("        不一致；本脚本给出的是 [%s, %s]（v 中）与 [%s, %s]（相对）。" % (
        C.dec(w_lo, 12), C.dec(w_hi, 12), C.dec(w_lo / CIV[1], 12), C.dec(w_hi / CIV[0], 12)))

p("")
p("[7] 覆盖度与盲区")
p("    覆盖 (K*, 3.15e20)：对数网格步长 %.4f（每点覆盖对数窗 %.2e），随机 100 点。" % (
    (hi_f / lo_f) ** (1 / 199), math.log(hi_f / lo_f) / 199))
p("    c_92 邻域：30 个相对偏移点，最小 |偏移| = 1e-27，覆盖 [1e-27, 1e-6] 共 15 个尺度。")
p("    盲区：连续统未被覆盖；对「一切 K」的断言仍需全称论证（本路只做反例搜索）。")
p("    总用时 %.1f 秒。" % (time.time() - t_start))

open(HERE + "/results/r4b_search_epsopt.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/r4b_search_epsopt.out")
