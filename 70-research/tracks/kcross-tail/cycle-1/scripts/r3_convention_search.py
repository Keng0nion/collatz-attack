#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""路线 3 定向反例搜索 ②：(K*, c92) 上「两约定同值」的反例，即 argmin != 91 的点。

两部分：
  [A] A(90) 下界剪枝的均匀化引理及其单次精确判据：
      对一切 K >= K*、一切 m2 <= 90：eps(m2,K) >= A(90)/(3K ln2_hi)；
      对一切 K >= K*：eps(91,K) <= (A(91) + S(K*))/(3K ln2_lo)，其中
      S(K*) = [3/(2^v-1) + 3*90/(2^v-1)^delta 的上界，v = v(91,K*)]（v 关于 K 递增，
      故 S 关于 K 递减，K* 处最大）。于是剪枝失效边界不存在；最紧点在 K* 本身。
      判据（能取 False）：A(90)*ln2_lo > (A(91)+S(K*))*ln2_hi。
  [B] 定点搜索 (K*, c92)：均匀网格、K0（eps92 与 eps91 交点）邻域、c92 邻域、
      整数点与随机点；逐点算可行集、argmin（分离判据）、最小间隔、剪枝比值 r(K)。
只读 import；输出写本轨道 results 目录。
"""
import sys
import time
import random
import math
from fractions import Fraction as F

SCRIPTS = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
sys.path.insert(0, SCRIPTS)
import r4_common as C
import k3_rig as K3

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

p("#" * 74)
p("# 路线 3 定向反例搜索 ②：(K*, c92) 上 argmin != 91 的反例搜索")
p("# 脚本：tracks/kcross-tail/cycle-1/scripts/r3_convention_search.py")
p("#" * 74)
p("")

# ---------------- [A] 均匀化剪枝引理 ----------------
p("[A] A(90) 下界剪枝的均匀化（单次精确判据）")
A90 = K3.A_of(90, 92)
A91 = K3.A_of(91, 92)
p("    A(90) = %s" % A90)
p("    A(91) = %s" % A91)
v = K3.v_bounds(91, 92, KSTAR, DLO, DHI)
p("    v(91, K*) ∈ [%s, %s]" % (C.dec(v[0], 20), C.dec(v[1], 20)))
p2 = K3.pow2_bounds(v[0], v[1])
t_lo = K3.rd(p2[0] - 1)
t_hi = K3.ru(p2[1] - 1)
term2_hi = K3.ru(F(3) / t_lo)
pt = K3.t2vm1_delta_bounds(v[0], v[1], DLO, DHI)
term3_hi = K3.ru(F(3 * 90) / pt[0])
S = term2_hi + term3_hi
p("    term2_hi(91,K*) = %s" % C.dec(term2_hi, 30))
p("    term3_hi(91,K*) = %s" % C.dec(term3_hi, 30))
p("    S(K*) = term2_hi + term3_hi = %s" % C.dec(S, 30))
lhs = A90 * L2[0]
rhs = (A91 + S) * L2[1]
p("    判据：A(90)*ln2_lo > (A(91)+S)*ln2_hi ？ %s" % (lhs > rhs))
p("      A(90)*ln2_lo = %s" % C.dec(lhs, 30))
p("      (A(91)+S)*ln2_hi = %s" % C.dec(rhs, 30))
p("      比值 = %s ；绝对余量 = %s" % (
    C.dec(lhs / rhs, 20), C.dec(lhs - rhs, 30)))
p("    含义：对一切 K >= K*、一切 m2 <= 90：eps(m2,K) >= A(90)/(3K ln2_hi) > (A(91)+S)/(3K ln2_lo) >= eps(91,K)。")
p("    单调性依据：v(91,K) = (91/92)K(delta-1)/(delta^91-1) 关于 K 递增；3/(2^v-1) 与 3*90/(2^v-1)^delta 关于 v 递减。")
p("    机制检查（S 随 K 的读数，只验证单调下降方向）：")
for Kstr in ("205632218873398596256", "240000000000000000000",
             "280000000000000000000", "313195478959172262876",
             "299387967534477157441", "302578139046974169432"):
    Kx = F(Kstr)
    vx = K3.v_bounds(91, 92, Kx, DLO, DHI)
    px = K3.pow2_bounds(vx[0], vx[1])
    t2x = K3.ru(F(3) / K3.rd(px[0] - 1))
    ptx = K3.t2vm1_delta_bounds(vx[0], vx[1], DLO, DHI)
    t3x = K3.ru(F(3 * 90) / ptx[0])
    p("      K = %s ：S(K) = %s" % (Kstr, C.dec(t2x + t3x, 30)))
e91star = K3.eps_bounds(91, 92, KSTAR, DLO, DHI, L2)
p("    对照 k3_rig.eps_bounds(91,92,K*) = [%s, %s]" % (
    C.dec(e91star[0], 44), C.dec(e91star[1], 44)))
p("    与 A 路径一致性（eps_hi 应不小于 A(91)/(3K* ln2_hi)）：%s" % (
    e91star[1] >= A91 / (3 * KSTAR * L2[1])))

# ---------------- [B] 门槛与交点 ----------------
p("")
p("[B] 门槛 c92 与交点 K0")
g92 = K3.geom_bounds(92, DLO, DHI)
c92_lo = K3.rd(g92[0] * CIV[0] * F(92, 92))
c92_hi = K3.ru(g92[1] * CIV[1] * F(92, 92))
g91 = K3.geom_bounds(91, DLO, DHI)
c91_hi = K3.ru(g91[1] * CIV[1] * F(92, 91))
p("    c_91_hi = %s ；c_92 ∈ [%s, %s]" % (
    C.dec(c91_hi, 30), C.dec(c92_lo, 30), C.dec(c92_hi, 30)))
p("    c_91_hi < K* ？ %s ；K* < c_92_lo ？ %s" % (c91_hi < KSTAR, KSTAR < c92_lo))


def cmp92_91(K):
    a = K3.eps_bounds(92, 92, K, DLO, DHI, L2)
    b = K3.eps_bounds(91, 92, K, DLO, DHI, L2)
    if a[1] < b[0]:
        return "e92<e91"
    if b[1] < a[0]:
        return "e92>e91"
    return None


KA, KB = KSTAR + 1, c92_lo - 1
cA, cB = cmp92_91(KA), cmp92_91(KB)
p("    K*+1 处 %s ；c_92_lo-1 处 %s" % (cA, cB))
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
p("    交点 K0 ∈ [%s, %s]（宽度 %s）" % (C.dec(K0A, 30), C.dec(K0B, 30), C.fnum(K0B - K0A)))

# ---------------- [B2] 点集 ----------------
pts = []
for i in range(1, 9):
    pts.append(("int_nearKstar", KSTAR + i))
NA = 12
for i in range(NA):
    K = int(KSTAR) + 16 + (int(K0A) - int(KSTAR) - 20) * i // (NA - 1)
    pts.append(("grid_1", F(K)))
for u in ("1e-27", "1e-24", "1e-21", "1e-18", "1e-15", "1e-12", "1e-9", "1e-6"):
    d = F(u)
    pts.append(("K0_neigh", F(int(K0A * (1 - d)))))
    pts.append(("K0_neigh", F(int(K0A * (1 + d)))))
pts.append(("K0_neigh", K0A))
pts.append(("K0_neigh", K0B))
NB = 12
for i in range(NB):
    K = int(K0B) + 1 + (int(c92_lo) - int(K0B) - 2) * i // (NB - 1)
    pts.append(("grid_2", F(K)))
for u in ("1e-27", "1e-24", "1e-21", "1e-18", "1e-15", "1e-12", "1e-9", "1e-6"):
    d = F(u)
    pts.append(("c92_neigh", F(int(c92_lo * (1 - d)))))
pts.append(("c92_neigh", c92_lo - 1))
pts.append(("c92_neigh", c92_lo))
mid92 = (c92_lo + c92_hi) / 2
pts.append(("c92_neigh", F(int(mid92))))
pts.append(("c92_neigh", c92_hi))
for K in (KSTAR + 100, KSTAR + 10 ** 6, KSTAR + 10 ** 12, KSTAR + 10 ** 18,
          KSTAR * 3 // 2, 240000000000000000000, 260000000000000000000):
    pts.append(("spread", F(K)))
rng = random.Random(20261028)
lo_f, hi_f = float(KSTAR + 1), float(c92_lo)
for _ in range(10):
    x = math.exp(rng.uniform(math.log(lo_f), math.log(hi_f)))
    pts.append(("rand", F(int(x) + 1)))

seen = set()
allp = []
for g, K in pts:
    if K in seen:
        continue
    seen.add(K)
    allp.append((g, K))
p("")
p("[C] 点集（去重后 %d 个）：int_nearKstar 8、grid_1 %d、K0 邻域 18、grid_2 %d、c92 邻域 13、spread 7、随机 10" % (
    len(allp), NA, NB))

# ---------------- [C2] 逐点判定 ----------------
p("")
p("[D] 逐点判定（可行集、argmin、最小间隔、剪枝比值 r(K)）")
rows = []
hits = []
undec = []
noarg = []
t1 = time.time()
for g, K in allp:
    info = C.eps_opt(K, CIV, DLO, DHI, L2)
    feas = info["feas"]
    und = info["und"]
    f92 = 92 in feas
    arg = info["argmin"]
    if arg is None:
        noarg.append((g, K))
    # 与 91 的严格比较：有 m2 使 eps_hi(m2) < eps_lo(91) 记「91 被严格击败」
    beaten = []
    gap = None
    if 91 in info["vals"]:
        v91 = info["vals"][91]
        for t2, vv in info["vals"].items():
            if t2 == 91:
                continue
            if vv[1] < v91[0]:
                beaten.append((t2, vv))
            dgap = vv[0] - v91[1]
            if gap is None or dgap < gap:
                gap = dgap
    else:
        undec.append((g, K, "91 不可行"))
    if f92 and K < c92_lo:
        hits.append((g, K, "92 在 c92_lo 之下可行"))
    if 92 in und:
        undec.append((g, K, "92 未定"))
    if beaten:
        hits.append((g, K, "被严格击败：%s" % [(t2,) for (t2, _) in beaten]))
    if arg is not None and arg != 91 and K < c92_lo:
        hits.append((g, K, "argmin = %d" % arg))
    if not feas:
        hits.append((g, K, "可行集为空"))
    rK = None
    if 91 in info["vals"]:
        lb90 = K3.eps_lower_A_only(90, 92, K, L2)
        rK = lb90 / info["vals"][91][1]
    rows.append((g, K, len(feas), len(und), f92, arg, gap, rK))
p("    逐点用时 %.1f 秒" % (time.time() - t1))

p("")
p("[E] 结果汇总")
p("    点数 = %d（全部落在 (K*, c92) 内？ %s）" % (
    len(allp), all(KSTAR < K < c92_lo for (g, K) in allp)))
p("    命中数 = %d ：%s" % (len(hits), hits if hits else "无"))
p("    argmin 未分离点 = %d ：%s" % (len(noarg), [(g, str(K)) for (g, K) in noarg]))
p("    91 不可行或其他未定 = %d ：%s" % (len(undec), undec))
rmin = min((r for (g, K, nf, nu, f92, arg, gap, r) in rows if r is not None))
rmin_row = [row for row in rows if row[7] == rmin][0]
p("    剪枝比值 r(K) = A(90)/(3K ln2_hi) / eps_hi(91,K) 的最小值 = %s（在 K = %s，组 %s）" % (
    C.dec(rmin, 20), C.dec(rmin_row[1], 30), rmin_row[0]))
gmin = min((row[6] for row in rows if row[6] is not None))
gmin_row = [row for row in rows if row[6] == gmin][0]
p("    「91 与其余 m2 的最小间隔」 min_{m2!=91}(eps_lo(m2) - eps_hi(91)) = %s（在 K = %s）" % (
    C.dec(gmin, 30), C.dec(gmin_row[1], 30)))
argcnt = {}
for (g, K, nf, nu, f92, arg, gap, rK) in rows:
    argcnt[arg] = argcnt.get(arg, 0) + 1
p("    argmin 分布：%s" % sorted(argcnt.items(), key=lambda kv: -kv[1]))

p("")
p("[F] 逐点表（组、K 前 33 位、可行数、未定、92 可行、argmin、最小间隔、r(K)）")
for (g, K, nf, nu, f92, arg, gap, rK) in rows:
    p("    %-13s K=%s feas=%2d und=%d f92=%d arg=%s gap=%s r=%s" % (
        g, C.dec(K, 33), nf, nu, int(f92), arg,
        C.fnum(gap) if gap is not None else None,
        C.fnum(rK) if rK is not None else None))

p("")
p("[G] 覆盖度与盲区")
p("    覆盖 (K*, c92_lo)：int_nearKstar 8 点 + grid_1 12 点（步长 %s）+ K0 邻域 18 + grid_2 12 点（步长 %s）+ c92 邻域 13 + 随机 10" % (
    C.fnum((F(int(K0A)) - KSTAR) / (NA - 1)), C.fnum((c92_lo - F(int(K0B))) / (NB - 1))))
p("    盲区：采样点之间的连续统未覆盖（采样不能作全称证据）；全称结论由 [A] 的单次精确判据 + 可行集结构给出。")
p("    总用时 %.1f 秒。" % (time.time() - T0))

open(HERE + "/results/r3_convention_search.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/r3_convention_search.out")
