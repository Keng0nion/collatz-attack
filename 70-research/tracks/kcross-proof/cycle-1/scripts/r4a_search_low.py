#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 4 路任务 (a)：K ∈ [L, R_lo) 上的反例搜索（Psi_92(K) > K* 或链越界）。

L = 7.5311×10^11（SdW 常数，项目口径）；R_lo = 方程 eps(92,K) = gamma - delta
的 150 步严格二分区间左端（本脚本复算，与 c2r5_cert.log:67 的 40 位打印对照）。

网格：对数等距 N_grid 点 + 对数均匀随机 N_rand 点（种子固定并打印）+
结构点（收敛分母、台阶值、K* 邻域、门槛邻域、整数邻点）。

每一个点都做（全部严格有理算术）：
  1. 可行集 F_92(K) 的三值判定（未定计数）；
  2. eps_opt(K) 的严格区间与唯一 argmin（分离判据）；
  3. Psi_92(K) 的两侧夹逼 [q_lo, q_hi]（Stern-Brocot 最小分母，含端点包络）；
  4. 自举链 K -> Psi(K) -> ... 到不动点，检查每一步 <= U(92) 且 <= K*。

命中目标（Psi > K* 或链越界）逐条按显式见证打印；命中 0 时打印点数、覆盖度、
对数步长与未定/未闭合计数（盲区）。

运行：/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python r4a_search_low.py
"""
import sys
import time
import random
import math

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
L_CONST = F(753110000000)                 # 7.5311×10^11
U92 = (C.R.rd(C.U92_W * C.M * C.R.iv_pow((DLO, DHI), 92)[0]),
       C.R.ru(C.U92_W * C.M * C.R.iv_pow((DLO, DHI), 92)[1]))

p("#" * 74)
p("# 任务 (a)：[L, R_lo) 上 Psi_92(K) > K* 与链越界的反例搜索")
p("# 脚本：tracks/kcross-proof/cycle-1/scripts/r4a_search_low.py")
p("#" * 74)
p("")
p("[0] 基本量与标定")
p("    delta ∈ [%s, %s]，宽度 %s" % (C.dec(DLO, 45), C.dec(DHI, 45), C.fnum(DHI - DLO)))
p("    C = log2((162/97)X0) ∈ [%s, %s]" % (C.dec(CIV[0], 40), C.dec(CIV[1], 40)))
p("    K* = %d ；L = 753110000000 ；U(92) ∈ [%s, %s]" % (
    C.KSTAR, C.dec(U92[0], 32), C.dec(U92[1], 32)))
t0 = time.time()
R_lo, R_hi = C.root_interval(DLO, DHI, L2, steps=150)
p("    R_lo（150 步二分左端）= %s" % C.dec(R_lo, 40))
p("    R_hi（150 步二分右端）= %s" % C.dec(R_hi, 40))
p("    宽度 %s ，相对宽度 %s ；二分用时 %.1f 秒" % (
    C.fnum(R_hi - R_lo), C.fnum((R_hi - R_lo) / R_lo), time.time() - t0))
p("    对照 c2r5_cert.log:67 打印：313195478959172262876.6365306194907065260231016940260118526233（40 位）")

# ---------------- 采样点集 ----------------
N_grid = 300
N_rand = 200
SEED = 20261028
lo_f = float(L_CONST)
hi_f = float(R_lo)
grid = []
for i in range(N_grid):
    x = lo_f * (hi_f / lo_f) ** (i / (N_grid - 1))
    grid.append(F(int(x) + 1))
rng = random.Random(SEED)
rand_pts = []
for _ in range(N_rand):
    x = math.exp(rng.uniform(math.log(lo_f), math.log(hi_f)))
    rand_pts.append(F(int(x) + 1))

struct = []
struct.append(L_CONST)
struct.append(L_CONST + 1)
for q in (77692117359936589403, 127940101513462006853, 397560349370386783,
          4640282259296926456, 27444133206411171953, 50247984153525417450):
    if L_CONST < q < R_lo:
        struct.append(F(q))
for d in (-2, -1, 1, 2):
    struct.append(F(C.KSTAR + d))
struct.append(F(C.KSTAR) * 2)
struct.append(F(313195478959172262876))
struct.append(F(313195478959172262876) + F(1, 2))
struct.append(F(302580000000000000000))
struct.append(F(302580000000000000000) + F(1, 2))
struct.append(F(193000000000000000000))

all_pts = []
seen = set()
for K in grid + rand_pts + struct:
    if K in seen:
        continue
    if not (L_CONST <= K < R_lo):
        continue
    seen.add(K)
    all_pts.append(K)
all_pts.sort()

p("")
p("[1] 采样点集")
p("    对数网格：%d 点，从 L 到 R_lo；相邻比值 = (R_lo/L)^(1/%d) = %.6f（对数步长 %.6f）" % (
    N_grid, N_grid - 1, (hi_f / lo_f) ** (1.0 / (N_grid - 1)),
    math.log(hi_f / lo_f) / (N_grid - 1)))
p("    随机点：%d 点，对数均匀，种子 = %d" % (N_rand, SEED))
p("    结构点：%d 点（L、收敛分母、K* 邻域、门槛邻域、整数邻点）" % len(struct))
p("    合并去重并在 [L, R_lo) 内截取后：%d 点" % len(all_pts))
p("    最小点 = %s ；最大点 = %s" % (all_pts[0], all_pts[-1]))

# ---------------- 逐点计算 ----------------
p("")
p("[2] 逐点判定（严格有理算术；Psi 两侧夹逼）")

# 同一 K 只算一次（链的迭代值在采样点之间大量重复；只用精确 K 作键，语义不变）
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


hits = []          # (K, 类型, 详情)
undecided = 0
unclosed = 0
ambiguous_vs_U = 0
chain_records = []
psi_min, psi_max = None, None
chain_fixed_values = {}
first_plateau = None

t1 = time.time()
for idx, K in enumerate(all_pts):
    q_lo, q_hi, info = psi_cached(K)
    if q_lo is None:
        undecided += 1
        continue
    if psi_min is None or q_lo < psi_min:
        psi_min = q_lo
    if psi_max is None or q_hi > psi_max:
        psi_max = q_hi
    # 目标 1：Psi > K*
    if q_lo > C.KSTAR:
        hits.append((K, "Psi>K*", "Psi ∈ [%d, %d]" % (q_lo, q_hi)))
    # 链
    steps, status = chain_cached(K, max_steps=64)
    chain_records.append((K, steps, status))
    if status not in ("fixed", "cycle"):
        unclosed += 1
    # 目标 2：链越界（任何一步 > U(92)）
    for (Kin, a, b, arg, nf) in steps:
        if a is not None and F(a) > U92[1]:
            hits.append((K, "chain>U92", "K_in=%s Psi_lower=%d" % (Kin, a)))
            break
        if a is not None and b is not None and F(a) <= U92[1] < F(b):
            ambiguous_vs_U += 1
    # 记录到达的不动点
    if status == "fixed":
        fv = steps[-1][1]
        chain_fixed_values[fv] = chain_fixed_values.get(fv, 0) + 1
    if first_plateau is None and q_lo == q_hi == C.KSTAR and K > C.KSTAR:
        first_plateau = K
p("    Psi 缓存命中后共算了 %d 个不同的 K（采样点 %d 个）" % (len(PSI_CACHE), len(all_pts)))
p("    链中「Psi 夹逼跨过 U(92) 上界但未判为越界」的步数 = %d" % ambiguous_vs_U)
p("    逐点用时 %.1f 秒（平均每点 %.3f 秒）" % (time.time() - t1, (time.time() - t1) / len(all_pts)))

p("")
p("[3] 结果汇总")
p("    点数 = %d ；未定（Psi 未夹住）= %d ；链未到不动点（fixed_interval/undecided/cap）= %d" % (
    len(all_pts), undecided, unclosed))
p("    反例类 A1（Psi(K) > K*）命中数 = %d" % sum(1 for h in hits if h[1] == "Psi>K*"))
p("    反例类 A2（链某步 > U(92)）命中数 = %d" % sum(1 for h in hits if h[1] == "chain>U92"))
p("    Psi 夹逼全区间：q_lo 最小 = %d ；q_hi 最大 = %d" % (psi_min, psi_max))
p("    链的不动点分布（前 12 个）：")
for fv, cnt in sorted(chain_fixed_values.items(), key=lambda kv: -kv[1])[:12]:
    p("      不动点 %d ：%d 次" % (fv, cnt))
if first_plateau is not None:
    p("    最早出现 Psi = K*（K > K*）的采样点 = %s" % first_plateau)
p("    K* 在不动点分布中？ %s（次数 %d）" % (
    C.KSTAR in chain_fixed_values, chain_fixed_values.get(C.KSTAR, 0)))

# 逐点全表（压缩为每点一行）
p("")
p("[4] 逐点全表（K, F 大小, argmin, Psi 夹逼, 链长, 终点）")
for (K, steps, status) in chain_records:
    Kin, a, b, arg, nf = steps[0]
    nsteps = len(steps)
    endv = steps[-1][1]
    p("    K=%s feas=%d argmin=%s Psi∈[%s,%s] steps=%d end=%s status=%s" % (
        K, nf, arg, a, b, nsteps, endv, status))

# 逐条见证（若有）
p("")
p("[5] 反例见证")
if not hits:
    p("    命中 0。")
else:
    for (K, typ, det) in hits:
        p("    【见证】类型=%s K=%s %s" % (typ, K, det))

p("")
p("[6] 覆盖度与盲区")
p("    覆盖区间：[L, R_lo) = [%s, %s)" % (L_CONST, C.dec(R_lo, 40)))
p("    对数步长：网格相邻比值 %.6f（即每点覆盖对数窗 %.2e）；随机点平均间距约 %.3e（对数）" % (
    (hi_f / lo_f) ** (1.0 / (N_grid - 1)), math.log(hi_f / lo_f) / (N_grid - 1),
    math.log(hi_f / lo_f) / N_rand))
p("    盲区：网格与随机点之间的连续统没有被覆盖（网格只能作机制检查或反例搜索，")
p("         不能构成全称命题的证据——learnings.md:44）；未定点 %d 个、链未闭合 %d 个。" % (
        undecided, unclosed))
p("    总用时 %.1f 秒。" % (time.time() - t_start))

open(HERE + "/results/r4a_search_low.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/r4a_search_low.out")
