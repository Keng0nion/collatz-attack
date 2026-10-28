#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""路线 3 定向反例搜索 ①：T = R 为假？在 [K*, R] 段与 R 邻域找 K_lo < R 的越界点。

判据（三值，全部严格有理）：
  越界认证：链某一步 Psi 的下界 > U(92) 上界；
  无越界认证：链全部步 Psi 的上界 <= U(92) 下界（且每步夹逼闭合）；
  其余：模棱（逐条记录）。
链规则：K_{n+1} = Psi_92(K_n)，至不动点/循环/未夹住/64 步（r4_common 口径）。
点集五组：A 均匀整数网格 (K*, R_lo]；B R 邻域相对偏移与 R 区间内部点；
          C 整数结构点与 R 以上对照点；D K* 以下衔接点；E 域底中止点。
只读 import kcross-proof 的 r4_common；输出写本轨道 results 目录，不碰旧证据。
"""
import sys
import time
from fractions import Fraction as F

SCRIPTS = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
sys.path.insert(0, SCRIPTS)
import r4_common as C

OUT = []
HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1/scripts"


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


T0 = time.time()
DLO, DHI, L2 = C.consts()
CIV = C.R.C_bounds()
KSTAR = F(C.KSTAR)
Q41 = F(77692117359936589403)
U92_W, M = C.U92_W, C.M
U92 = (C.R.rd(U92_W * M * C.R.iv_pow((DLO, DHI), 92)[0]),
       C.R.ru(U92_W * M * C.R.iv_pow((DLO, DHI), 92)[1]))

p("#" * 74)
p("# 路线 3 定向反例搜索 ①：T = R 为假？K_lo < R 的越界点搜索")
p("# 脚本：tracks/kcross-tail/cycle-1/scripts/r3_cross_search.py")
p("#" * 74)
p("")
p("[0] 常量与 R 的严格区间")
p("    U(92) ∈ [%s, %s]" % (C.dec(U92[0], 32), C.dec(U92[1], 32)))
p("    K* = %d ；q41 = %d" % (C.KSTAR, Q41))
t0 = time.time()
R_lo, R_hi = C.root_interval(DLO, DHI, L2, steps=150)
t_root = time.time() - t0
p("    R_lo（150 步二分左端）= %s" % C.dec(R_lo, 40))
p("    R_hi（150 步二分右端）= %s" % C.dec(R_hi, 40))
p("    宽度 = %s ；相对宽度 = %s ；二分用时 %.1f 秒" % (
    C.fnum(R_hi - R_lo), C.fnum((R_hi - R_lo) / R_lo), t_root))
p("    对照 r4a_search_low.out:10 的 R_lo 打印（同一二分口径）：%s" % (
    "313195478959172262876.6365306194907065260231016940260118526233（40 位）"))

# ---------------- 点集 ----------------
pts = []
Rf = int(R_lo)                       # floor(R_lo)
K0i = int(KSTAR) + 1
NA = 30
for i in range(NA):
    K = K0i + (Rf - K0i) * i // (NA - 1)
    pts.append(("A_grid", F(K)))
for u in ("1e-30", "1e-28", "1e-26", "1e-24", "1e-22", "1e-20", "1e-18",
          "1e-15", "1e-12", "1e-9", "1e-6", "1e-3"):
    d = F(u)
    pts.append(("B_nearR", F(int(R_lo * (1 - d)))))
pts.append(("B_nearR", R_lo))
mid = (R_lo + R_hi) / 2
pts.append(("B_insideR", (R_lo + mid) / 2))
pts.append(("B_insideR", mid))
pts.append(("B_insideR", (mid + R_hi) / 2))
pts.append(("C_above", R_hi))
for u in ("1e-30", "1e-24", "1e-18", "1e-12", "1e-6"):
    d = F(u)
    pts.append(("C_above", R_hi * (1 + d)))
for K in (313195478959172262876, 313195478959172262877, 313195478959172262878,
          313195478959172262880, 313195478959172262900,
          302578139046974169432, 302578139046974169433,
          299387967534477157441, 299387967534477157442,
          int(KSTAR) + 2, int(KSTAR) + 3):
    pts.append(("C_int", F(K)))
for K in (int(KSTAR) - 1, int(KSTAR) - 2, int(KSTAR) - 10, int(KSTAR) - 10 ** 6,
          int(KSTAR) - 10 ** 12, 2 * 77692117359936589403, 77692117359936589403,
          77692117359936589403 - 1, 77692117359936589403 + 1,
          193000000000000000000):
    pts.append(("D_below", F(K)))
for K in (6456, 6457, 7000, 10 ** 4, 10 ** 6, 10 ** 8, 10 ** 12):
    pts.append(("E_low", F(K)))

seen = set()
allp = []
for g, K in pts:
    if K in seen:
        continue
    seen.add(K)
    allp.append((g, K))

stepA = (F(Rf) - F(K0i)) / (NA - 1)
p("")
p("[1] 点集（去重后 %d 个）" % len(allp))
p("    A 网格：%d 个整数点，从 K*+1 = %d 到 %d，步长 = %s（约 %s）" % (
    NA, K0i, Rf, stepA, C.fnum(stepA)))
p("    B 邻域：12 个 R_lo 以下相对偏移点（1e-30 至 1e-3）、R_lo 本身、R 区间内部 3 点")
p("    C 对照：R_hi 与 5 个 R 以上相对偏移点；11 个整数结构点（876/877 等在 C_int）")
p("    D 衔接：K* 以下 10 点（含 q41 邻域）")
p("    E 中止：域底附近 7 点（6456、6457、7000、1e4、1e6、1e8、1e12）")

# ---------------- 逐点判定 ----------------
PSI_CACHE = {}


def psi_cached(K):
    if K not in PSI_CACHE:
        PSI_CACHE[K] = C.psi_two_sided(K, CIV, DLO, DHI, L2)
    return PSI_CACHE[K]


def chain_cached(K0, max_steps=64):
    seen = set()
    steps = []
    K = F(K0)
    for _ in range(max_steps):
        q_lo, q_hi, info = psi_cached(K)
        steps.append((K, q_lo, q_hi, info.get("argmin"), len(info.get("feas", []))))
        if q_lo is None:
            return steps, "undecided"
        if q_lo == q_hi:
            if F(q_lo) == K:
                return steps, "fixed"
            if F(q_lo) in seen:
                return steps, "cycle"
            seen.add(F(q_lo))
            K = F(q_lo)
        else:
            return steps, "fixed_interval"
    return steps, "cap"


p("")
p("[2] 逐点判定（严格有理；越界判据 = 某步 Psi 下界 > U(92) 上界）")
hits_cross = []
hits_amb = []
und = []
unclosed = []
recs = []
t1 = time.time()
for g, K in allp:
    steps, status = chain_cached(K, max_steps=64)
    recs.append((g, K, steps, status))
    for (Kin, a, b, arg, nf) in steps:
        if a is not None and F(a) > U92[1]:
            hits_cross.append((g, K, Kin, a))
            break
        if a is not None and b is not None and F(a) <= U92[1] < F(b):
            hits_amb.append((g, K, Kin, a, b))
    if status == "undecided":
        und.append((g, K))
    if status == "fixed_interval":
        unclosed.append((g, K))
p("    逐点用时 %.1f 秒（%d 个不同 K 进了 Psi 缓存，含链迭代）" % (
    time.time() - t1, len(PSI_CACHE)))

p("")
p("[3] 结果汇总")
p("    点数 = %d" % len(allp))
p("    越界认证命中数 = %d（其中 K < R_lo 的 = %d；K >= R_hi 的 = %d）" % (
    len(hits_cross),
    sum(1 for h in hits_cross if h[1] < R_lo),
    sum(1 for h in hits_cross if h[1] >= R_hi)))
p("    模棱点（夹逼跨 U(92) 上界但未判越界）= %d" % len(hits_amb))
p("    未夹住点（Psi 无下界，链中止）= %d ：%s" % (
    len(und), [str(K) for (g, K) in und]))
p("    未闭合点（两步夹逼不相等，链止于 fixed_interval）= %d ：%s" % (
    len(unclosed), [str(K) for (g, K) in unclosed]))
mn, mx = None, None
for g, K in allp:
    ql, qh, info = PSI_CACHE[K]
    if ql is None:
        continue
    mn = ql if mn is None or ql < mn else mn
    mx = qh if mx is None or qh > mx else mx
p("    全体首步 Psi 夹逼范围：最小下界 = %s ；最大上界 = %s" % (mn, mx))

p("")
p("[4] 逐点细读（全部组；B 与 C 组标出相对偏移）")
for g, K, steps, status in recs:
    if g not in ("B_nearR", "B_insideR", "C_above"):
        Kin0, a0, b0, arg0, nf0 = steps[0]
        p("    %s K = %s 首步 Psi %s 步数 %d 终点 %s 状态 %s" % (
            g, C.dec(F(K), 30),
            ("= %d" % a0) if (a0 is not None and a0 == b0) else ("∈ [%s, %s]" % (a0, b0)),
            len(steps), steps[-1][1], status))
        continue
    Kin, a, b, arg, nf = steps[0]
    rel = (F(K) - R_lo) / R_lo if g != "C_above" else (F(K) - R_hi) / R_hi
    p("    %s K = %s（相对 %s 偏移 %s）首步 Psi %s 步数 %d 终点 %s 状态 %s" % (
        g, C.dec(F(K), 30), "R_lo" if g != "C_above" else "R_hi",
        C.fnum(rel),
        ("= %d" % a) if (a is not None and a == b) else ("∈ [%s, %s]" % (a, b)),
        len(steps), steps[-1][1], status))

p("")
p("[5] 越界认证见证（若有）与无越界清单摘要")
if not hits_cross:
    p("    命中 0（含 R 以上对照组也未认证越界？这不该发生）")
else:
    for (g, K, Kin, a) in hits_cross:
        p("    【越界认证】起点组 = %s ；K_lo = %s ；首次越界步 K_in = %s ；Psi 下界 = %d ；U(92) 上界 = %s" % (
            g, C.dec(F(K), 30), C.dec(F(Kin), 30), a, C.dec(U92[1], 32)))
    p("    其中 K_lo < R_lo 的认证越界点 = %d（若 > 0 即为「T = R 为假」的直接见证）" % (
        sum(1 for h in hits_cross if h[1] < R_lo)))

p("")
p("[6] 覆盖度与盲区")
p("    A 网格覆盖 [K*+1, %d]，步长约 %s（相对步长 %s）" % (
    Rf, C.fnum(stepA), C.fnum(stepA / KSTAR)))
p("    B 组覆盖 R_lo 以下 12 个相对尺度（1e-30 至 1e-3）；R 区间内部 3 点")
p("    C 组覆盖 R_hi 与以上 5 个相对尺度；整数点 %d 个" % sum(1 for g, K in allp if g == "C_int"))
p("    D 组覆盖 K* 以下 10 点；E 组覆盖域底 7 点")
p("    盲区 1：网格与邻域点在连续统上未覆盖（采样不能作全称证据）。")
p("    盲区 2：R 的严格区间 [R_lo, R_hi] 宽 %s（相对 %s）；在其内部符号不可判（见 B_insideR 读数）。" % (
    C.fnum(R_hi - R_lo), C.fnum((R_hi - R_lo) / R_lo)))
p("    盲区 3：E 组点处 F_92 为空（域外），链在定义域底即中止，不代表越界。")
p("    总用时 %.1f 秒。" % (time.time() - T0))

open(HERE + "/results/r3_cross_search.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/r3_cross_search.out")
