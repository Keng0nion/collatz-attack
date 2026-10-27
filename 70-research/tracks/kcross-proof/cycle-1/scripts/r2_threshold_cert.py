#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kcross-proof 轨道第 1 轮第 2 路：阈值 T 的两侧严格区间证书（不经过「根」的命名）。

要交付的两个全称陈述（判据照抄 70-research/cycle-1/route-4.md:196：
「链从 K_lo 出发，若某次迭代 > U(92) 就算「越过」」）：

  (i)  对一切 K_lo ∈ 域 D_92 且 K_lo <= T_hi：链的全部迭代 <= K* < U(92)，永不越界；
  (ii) 对一切 K_lo >= T_lo：Psi_92(K_lo) >= 7941964418702608664581 > U(92)，首步越界。

其中 T := inf{ K_lo ∈ D_92 : 链从 K_lo 出发在某步 > U(92) }，(i)(ii) 合起来给 T ∈ [T_hi, T_lo]。
D_92 := {K > 0 : F_92(K) != 空} = [92·C, oo)（F_92 含 m2 = 1 当且仅当 K >= 92C）。

数值引擎：本目录 r2_rig.py（自足严格有理区间库，与 cycle-2/scripts/c2r5_rig.py
走不同的级数路线，见该文件头注）。除声明处外，一切判定都是 Fraction 精确比较；
c2r5_rig 只被只读 import（用于复现 route-5 的 150 步区间与对拍），
不运行 c2r5_cert.py，不写 cycle-1 与 cycle-2 的任何既有文件。

运行：20-experiments/.venv/bin/python r2_threshold_cert.py
"""
import sys
import time
from fractions import Fraction as F

sys.dont_write_bytecode = True
HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
sys.path.insert(0, HERE)
import r2_rig as R2

M = 92
KSTAR = 205632218873398596256
GAM_N, GAM_D = 325919355854421968365, 205632218873398596256
GAM = F(GAM_N, GAM_D)
U92_W = F(14784, 10000)
NSTEPS = 400
KA0, KB0 = F(312) * 10 ** 18, F(315) * 10 ** 18
OUT = []
T_START = time.time()


def p(s=""):
    OUT.append(s)
    print(s, flush=True)


def chk(name, cond, extra=""):
    tag = "True" if cond else "False"
    p("     [%s] %s %s" % ("PASS" if cond else "FAIL", name, extra))
    return cond


def sci(x, nd=12):
    return R2.sci(x, nd)


p("#" * 78)
p("# kcross-proof cycle-1 route-2：阈值 T 的两侧严格区间证书（不经过根命名）")
p("# 脚本：tracks/kcross-proof/cycle-1/scripts/r2_threshold_cert.py（数值引擎 r2_rig.py）")
p("# 解释器：%s" % sys.version.split()[0])
p("#" * 78)

# ================= [0] 常数与自检 =================
p("")
p("[0] 常数（严格区间）与引擎自检")
t0 = time.time()
DLO, DHI = R2.delta_bounds()
L2 = R2.ln2_bounds()
L3 = R2.ln3_bounds()
CIV = R2.C_bounds()
p("     delta ∈ [%s, %s]" % (R2.dec_str(DLO, 50), R2.dec_str(DHI, 50)))
p("     delta 区间宽度 = %s（网格 GRID = 10^200）" % sci(DHI - DLO))
p("     ln2 ∈ [%s, %s]（宽度 %s）" % (R2.dec_str(L2[0], 45), R2.dec_str(L2[1], 45), sci(L2[1] - L2[0])))
p("     ln3 ∈ [%s, %s]（宽度 %s）" % (R2.dec_str(L3[0], 45), R2.dec_str(L3[1], 45), sci(L3[1] - L3[0])))
p("     C = log2((162/97)X0) ∈ [%s, %s]（宽度 %s）" % (
    R2.dec_str(CIV[0], 40), R2.dec_str(CIV[1], 40), sci(CIV[1] - CIV[0])))
p("     X0 = 695*2^60 = %d（印出版口径；arXiv v3 的 704*2^60 不在本路范围）" % R2.X0_INT)
KNOWN_DELTA = "1.58496250072115618145373894394781650875981441"   # cycle-2/methods.md:61 登记的 45 位
p("     对拍（45 位已知值，出处 cycle-2/methods.md:61）：delta 前 45 位 = %s" % R2.dec_str(DLO, 44))
chk("delta 与登记值逐位一致", R2.dec_str(DLO, 44).startswith(KNOWN_DELTA[:44]))
GD_LO, GD_HI = GAM - DHI, GAM - DLO
p("     gamma = %d/%d = %s" % (GAM_N, GAM_D, R2.dec_str(GAM, 45)))
p("     gamma - delta ∈ [%s, %s]（宽度 %s）" % (sci(GD_LO, 14), sci(GD_HI, 14), sci(GD_HI - GD_LO)))
chk("gamma > delta_hi（即 gamma > delta，严格）", GAM > DHI)
p("     92·C ∈ [%s, %s]" % (R2.dec_str(92 * CIV[0], 12), R2.dec_str(92 * CIV[1], 12)))
p("     用时 %.2fs" % (time.time() - t0))

# ================= [1] gamma 的连分数身份证书与 unimodular bracket =================
p("")
p("[1] gamma 的连分数身份证书（本库独立实现的前缀证书）与最小分母 bracket")
t0 = time.time()
PREF = R2.certified_prefix(DLO, DHI)
p("     delta 的连分数前缀证书长度 = %d 位" % len(PREF))
CONV = R2.convergents(PREF)
C43 = [c for c in CONV if c[0] == 43][0]
C44 = [c for c in CONV if c[0] == 44][0]
p("     第 43 个收敛分数 p43/q43 = %d/%d" % (C43[1], C43[2]))
chk("它恰等于 gamma（p43 = 分子、q43 = K*）", C43[1] == GAM_N and C43[2] == KSTAR)
chk("gamma 的分子分母互素（gcd = 1）", __import__("math").gcd(GAM_N, GAM_D) == 1)
p("     第 44 个收敛分数 p44/q44 = %d/%d" % (C44[1], C44[2]))
X_Y, Z_W = F(C44[1], C44[2]), GAM
p("     bracket 取 x/y = p44/q44、z/w = gamma")
chk("x/y < delta_lo（严格）", X_Y < DLO, "余量 = %s" % sci(DLO - X_Y))
chk("z/w = gamma > delta_lo（严格）", Z_W > DLO)
chk("z·y - x·w = 1（unimodular）", Z_W.numerator * X_Y.denominator - X_Y.numerator * Z_W.denominator == 1)
D0 = X_Y.denominator + Z_W.denominator
p("     分母之和 y + w = %d + %d = %d" % (X_Y.denominator, Z_W.denominator, D0))
MED = F(X_Y.numerator + Z_W.numerator, X_Y.denominator + Z_W.denominator)
p("     中项 (x+z)/(y+w)（注意不是两分数之和） = %d/%d" % (MED.numerator, MED.denominator))
chk("中项的分母 = D0（说明下界可达，最小分母恰为 D0）", MED.denominator == D0)
chk("中项 ∈ (delta_lo, gamma)", DLO < MED < GAM, "左余量 = %s，右余量 = %s" % (sci(MED - DLO), sci(GAM - MED)))
p("     与 (D5) 记法的一致性核对：[a0;...;a41, 2] 是否等于 gamma ？ %s" % (
    R2.cf_value(PREF[:42] + [2]) == GAM))
p("     用时 %.2fs" % (time.time() - t0))

# ================= [2] 端点事实 =================
p("")
p("[2] 端点事实（全部精确有理比较）")
U92_IV = (R2.rd(U92_W * M * R2.pow_int_grid(DLO, DHI, 92)[0]),
          R2.ru(U92_W * M * R2.pow_int_grid(DLO, DHI, 92)[1]))
p("     U(92) = 1.4784·92·delta^92 ∈ [%s, %s]" % (R2.dec_str(U92_IV[0], 12), R2.dec_str(U92_IV[1], 12)))
chk("K* < U(92)_下界", F(KSTAR) < U92_IV[0],
    "余量 = %s（比值 %.4f）" % (sci(U92_IV[0] - KSTAR), float(U92_IV[0] / KSTAR)))
chk("D0 > U(92)_上界", F(D0) > U92_IV[1],
    "余量 = %s（比值 %.4f）" % (sci(F(D0) - U92_IV[1]), float(F(D0) / U92_IV[1])))
G92C = R2.geom_bounds(92, DLO, DHI)
p("     geom(92)·C ∈ [%s, %s]（m2 = 92 的可行门槛）" % (sci(G92C[0] * CIV[0]), sci(G92C[1] * CIV[1])))
p("     域底 92C = %s" % R2.dec_str(92 * CIV[0], 10))

# ================= [3] 二分定位 T（端点选择用；证书在 [4] 与 [5]） =================
p("")
p("[3] 二分定位：S(K) = eps(92, K) - (gamma - delta) 的符号（精确有理中点）")
p("     说明：二分只用于「挑选端点 T_hi、T_lo」；[4] 与 [5] 的证书是独立的有限精确检查，")
p("     不引用「根」这个对象，也不依赖二分的任何数值结论。")
K1, K2 = KA0, KB0
t0 = time.time()
done = 0
stall = None
for step in range(NSTEPS):
    Km = (K1 + K2) / 2
    e = R2.eps_bounds(92, 92, Km, DLO, DHI, L2)
    if e[0] > GD_HI:
        K1 = Km
        done += 1
    elif e[1] < GD_LO:
        K2 = Km
        done += 1
    else:
        stall = (step, e)
        break
    if (step + 1) % 100 == 0:
        p("     已完成 %d 步，宽度 %s，用时 %.1fs" % (step + 1, sci(K2 - K1), time.time() - t0))
T_HI, T_LO = K1, K2
p("     完成 %d 步%s；用时 %.1fs" % (done, "（提前停在未定处）" if stall else "", time.time() - t0))
if stall:
    p("     未定步 = %d，eps 区间 = [%s, %s]" % (stall[0], sci(stall[1][0], 16), sci(stall[1][1], 16)))
p("     T_hi = %s" % R2.dec_str(T_HI, 60))
p("     T_lo = %s" % R2.dec_str(T_LO, 60))
p("     绝对宽度 = %s；相对宽度 = %s；一致十进制位 ≈ %d" % (
    sci(T_LO - T_HI), sci((T_LO - T_HI) / T_HI),
    int(-__import__("math").log10(float((T_LO - T_HI) / T_HI)))))
p("     T_hi 的精确有理 = %s" % R2.frac_str(T_HI))
p("     T_lo 的精确有理 = %s" % R2.frac_str(T_LO))

# ================= [4] 证书 A：下侧 =================
p("")
p("[4] 证书 A（下侧）：对一切 K_lo ∈ D_92 且 K_lo <= T_hi，链的全部迭代 <= K* < U(92)")
t0 = time.time()
p("     A1 有限检查：对一切 m2 ∈ F_92(T_hi)，比较 eps(m2, T_hi) 与 gamma - delta")
FEAS = []
MARGS = []
NONE = []
for t in range(1, M + 1):
    d = R2.feasible_decision(t, M, T_HI, DLO, DHI, CIV)
    if d is True:
        FEAS.append(t)
        e = R2.eps_bounds(t, M, T_HI, DLO, DHI, L2)
        marg = e[0] - GD_HI
        MARGS.append((marg, t, e))
    else:
        if d is None:
            NONE.append(t)
        p("       m2 = %d 可行判定 = %s（不参与 A1 的取最小）" % (t, d))
chk("A1a 92 个 m2 的可行判定全部确定（无未定）", not NONE, "未定 = %s" % (NONE,))
p("     F_92(T_hi) = {1, ..., %d}（%d 个元素，全部判定 True）" % (max(FEAS), len(FEAS)))
MARGS.sort()
for marg, t, e in MARGS[:3]:
    p("       最小余量前三：m2 = %d，eps ∈ [%s, %s]，eps_lo - (gamma-delta)_hi = %s" % (
        t, sci(e[0], 16), sci(e[1], 16), sci(marg, 6)))
chk("A1：全部 eps(m2, T_hi)_下界 > (gamma - delta)_上界（92 项逐项精确比较）",
    MARGS[0][0] > 0, "最小值在 m2 = %d 处，余量 = %s" % (MARGS[0][1], sci(MARGS[0][0], 6)))
p("     A2 化归（ε_opt 严格递减，初等）：对一切 K ∈ [92C, T_hi]，eps_opt(K) >= eps_opt(T_hi)，")
p("        而 eps_opt(T_hi) = min_{m2 ∈ F_92(T_hi)} eps(m2, T_hi) > gamma - delta（A1）。")
p("        （递减证明：K1 < K2、m* 为 K1 处 argmin ⟹ m* ∈ F(K1) ⊆ F(K2) 且 eps(m*, K2) < eps(m*, K1)，")
p("          故 eps_opt(K2) <= eps(m*, K2) < eps(m*, K1) = eps_opt(K1)。ε(m2, ·) 的严格递减见 [6] 引理。）")
p("     A3 gamma ∈ (delta, delta + eps_opt(K))：gamma > delta 由 [0]，gamma < delta + eps_opt(K) 由 A2。")
p("        故 gamma 是落在开区间 (delta, delta + eps_opt(K)) 内、分母为 K* 的分数 ⟹ Ψ_92(K) <= K*。")
chk("A4 K* < U(92)（见 [2]）", F(KSTAR) < U92_IV[0])
p("     A5 域闭合（化归引理，避免「链在域外未定义」的洞）：")
eps_ub = R2.eps_bounds(1, M, F(92) * CIV[0], DLO, DHI, L2)[1]   # eps(1, ·) 递减，K >= 92C
QLIM = 6456
worst = None
for q in range(1, QLIM + 1):
    pmin = R2.fl(F(q) * DLO) + 1
    marg = F(pmin, q) - (DHI + eps_ub)
    if worst is None or marg < worst[0]:
        worst = (marg, q, pmin)
chk("A5：对一切 q <= %d，最小的 p/q > delta 已 >= delta_hi + eps_ub（故 Ψ(K) >= %d）" % (QLIM, QLIM + 1),
    worst[0] >= 0, "最小余量在 q = %d（p = %d），余量 = %s" % (worst[1], worst[2], sci(worst[0], 6)))
p("        其中 eps_ub = eps(1, 92C) 的上界 = %s（用 1 ∈ F_92(K) 对一切 K >= 92C 与 eps(1,·) 递减）" % sci(eps_ub, 12))
chk("A5b 6457 > 92C（链一旦进入就永不离开域 D_92）", F(QLIM + 1) > 92 * CIV[1],
    "余量 = %s" % sci(F(QLIM + 1) - 92 * CIV[1]))
p("     A6 结论 A：对一切 K_lo ∈ D_92 且 K_lo <= T_hi，K_{n+1} = Ψ_92(K_n) <= K*，")
p("        且 K_{n+1} >= 6457 > 92C（A5），故链在域内永不中断，全部迭代 <= K* < U(92)：永不越界。")
p("        用时 %.2fs" % (time.time() - t0))

# ================= [5] 证书 B：上侧 =================
p("")
p("[5] 证书 B（上侧）：对一切 K_lo >= T_lo，Ψ_92(K_lo) >= 7941964418702608664581 > U(92)")
t0 = time.time()
d92 = R2.feasible_decision(M, M, T_LO, DLO, DHI, CIV)
chk("B1 92 ∈ F_92(T_lo)", d92 is True)
e92 = R2.eps_bounds(M, M, T_LO, DLO, DHI, L2)
p("     B2 eps(92, T_lo) ∈ [%s, %s]；上界 - (gamma-delta)_下界 = %s" % (
    sci(e92[0], 16), sci(e92[1], 16), sci(GD_LO - e92[1], 6)))
chk("B2 eps(92, T_lo)_上界 < (gamma - delta)_下界", e92[1] < GD_LO,
    "负余量 = %s" % sci(e92[1] - GD_LO, 6))
p("     B3 单调性：对一切 K >= T_lo，eps_opt(K) <= eps_opt(T_lo) <= eps(92, T_lo) < gamma - delta。")
p("        故 delta + eps_opt(K) < gamma，开区间 (delta, delta + eps_opt(K)) ⊆ (delta, gamma)。")
p("     B4 bracket 证书（最小分母）：由 [1] 的 unimodular bracket (x/y, z/w) = (p44/q44, gamma)，")
p("        x/y < delta_lo、zy - xw = 1、y + w = D0；对区间 (delta_lo, gamma) 内任何分数 p/q：")
p("        p/q - x/y >= 1/(qy)、z/w - p/q >= 1/(qw)（分子为非零整数），相加得")
p("        1/(yw) = z/w - x/y >= (y+w)/(qyw) ⟹ q >= y + w = D0 = %d。" % D0)
chk("B5 于是 Ψ_92(K) >= D0（对一切 K >= T_lo）", True, "（用 B3 的包含 + B4 的 q >= D0）")
chk("B6 D0 > U(92)_上界（见 [2]）", F(D0) > U92_IV[1], "比值 %.4f" % float(F(D0) / U92_IV[1]))
p("     B7 非空性（保证 min 存在、陈述不空转）：任给 L > 0，开区间 (delta, delta+L) 内必有分数：")
p("        取整数 q > 1/L，则 (q·delta, q·delta + qL) 是长度 > 1 的开区间，必含整数 p，")
p("        即 p/q ∈ (delta, delta+L)，且分母 q <= 1/L + 1。故 (D5) 的最小值非空。")
p("     B8 结论 B：对一切 K_lo >= T_lo，链的第一步 Ψ_92(K_lo) >= D0 > U(92)，即首步越界。")
p("        用时 %.2fs" % (time.time() - t0))

# ================= [6] 单调性引理（本路自证的初等引理） =================
p("")
p("[6] 两条初等引理（本路自写，供 A2 与 B3 使用）")
p("     L1（ε(m2, ·) 严格递减）：v = (m2/m)K(delta-1)/(delta^{m2}-1) 关于 K 严格增，故")
p("        2^v - 1 严格增、(2^v-1)^delta 严格增、B(K) := A(m2) + 3/(2^v-1) + 3(m2-1)/(2^v-1)^delta")
p("        严格减且为正，而 1/(3K ln2) 也严格减，两个严格不等式相乘得 ε(m2, K') < ε(m2, K)。")
p("     L2（ε_opt 严格递减）：见 A2 的两行。两条都只用 v 关于 K 的单调性与正性，初等。")
p("     说明：本路的 A、B 两侧都只用 L1、L2，不使用第 1 轮的 Ψ 非降性"
  "（非降性是否仍为别处识别所需，不在本路范围）。")

# ================= [7] 三套区间的相交与相含 =================
p("")
p("[7] 三套区间的相交与相含（全部精确有理比较）")
t0 = time.time()
LO1 = F(45136225354708871151757558816616152091, 2 ** 57)
HI1 = F(361089802837670969214060470532929216895, 2 ** 60)
p("     I1（route-1 的 60 步区间，端点照抄 cycle-2/route-1.md §5.2 第 3 条）")
p("        = [%s, %s]；宽度 %s；相对宽度 %s" % (R2.dec_str(LO1, 40), R2.dec_str(HI1, 40),
                                                sci(HI1 - LO1), sci((HI1 - LO1) / LO1)))
# route-5 的 150 步区间：只读 import c2r5_rig 原位复现（确定性算法，逐位可复算）
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts")
import c2r5_rig as R5
DLO5, DHI5 = R5.delta_bounds()
L25 = R5.ln2_bounds()
CIV5 = R5.C_bounds()
G5LO, G5HI = GAM - DHI5, GAM - DLO5


def sign5(K):
    e = R5.eps_bounds(M, M, K, DLO5, DHI5, L25)
    if e[0] > G5HI:
        return "above"
    if e[1] < G5LO:
        return "below"
    return None


k1, k2 = F(312) * 10 ** 18, F(315) * 10 ** 18
p("     I5（route-5 的 150 步区间，用其 rig 原位复现；algorithm 与起点均照 c2r5_cert.py 第 5 节）")
for _ in range(150):
    km = (k1 + k2) / 2
    s = sign5(km)
    if s == "above":
        k1 = km
    elif s == "below":
        k2 = km
    else:
        break
LO5, HI5 = k1, k2
p("        = [%s, %s]；宽度 %s" % (R2.dec_str(LO5, 40), R2.dec_str(HI5, 40), sci(HI5 - LO5)))
p("        与 c2r5_cert.log:67 打印的截断十进制逐位一致？ 左端 %s，右端 %s" % (
    R2.dec_str(LO5, 40).startswith("313195478959172262876.6365306194907065260231016940260118526233"),
    R2.dec_str(HI5, 40).startswith("313195478959172262876.6365306194907065260231016961279595491105")))
p("     I2（本路阈值区间）= [T_hi, T_lo]；宽度 %s" % sci(T_LO - T_HI))
TAB = [("I1(route-1,60步)", LO1, HI1), ("I5(route-5,150步)", LO5, HI5), ("I2(本路,T侧)", T_HI, T_LO)]
for i in range(3):
    for j in range(i + 1, 3):
        a, b = TAB[i], TAB[j]
        inter = min(a[2], b[2]) - max(a[1], b[1])
        p("     %s ∩ %s ：相交 ？ %s（重叠长度 %s）" % (a[0], b[0], inter > 0, sci(inter) if inter > 0 else "0"))
chk("I5 ⊆ I1（复现 plan.md 第零节第 3 条的嵌套结果）", LO1 <= LO5 and HI5 <= HI1,
    "余量 = %s 与 %s" % (sci(LO5 - LO1), sci(HI1 - HI5)))
chk("I2 ⊆ I5（本路区间严格落在 route-5 区间内）", LO5 <= T_HI and T_LO <= HI5,
    "余量 = %s 与 %s" % (sci(T_HI - LO5), sci(HI5 - T_LO)))
chk("I2 ⊆ I1", LO1 <= T_HI and T_LO <= HI1,
    "余量 = %s 与 %s" % (sci(T_HI - LO1), sci(HI1 - T_LO)))
chk("三个区间两两相交", max(LO1, LO5, T_HI) < min(HI1, HI5, T_LO))
p("     用时 %.2fs" % (time.time() - t0))

# ================= [8] 三引擎对拍 =================
p("")
p("[8] 引擎对拍（本库 r2_rig 对 c2r5_rig、mpmath.iv、MPFR/gmpy2）")
t0 = time.time()
p("     [8.1] c2r5_rig（cycle-2 原库）")
p("        delta：本库 [%s, %s]，原库 [%s, %s]" % (R2.dec_str(DLO, 45), R2.dec_str(DHI, 45),
                                                    R2.dec_str(DLO5, 45), R2.dec_str(DHI5, 45)))
chk("两库的 delta 区间相交", not (DHI < DLO5 or DHI5 < DLO), "重叠 = %s" % sci(min(DHI, DHI5) - max(DLO, DLO5)))
chk("两库的 C 区间相交", not (CIV[1] < CIV5[0] or CIV5[1] < CIV[0]))
eA = R2.eps_bounds(M, M, F(33) * 10 ** 19, DLO, DHI, L2)
eB = R5.eps_bounds(M, M, F(33) * 10 ** 19, DLO5, DHI5, L25)
p("        eps(92, 3.3e20)：本库 [%s, %s]；原库 [%s, %s]" % (sci(eA[0], 14), sci(eA[1], 14), sci(eB[0], 14), sci(eB[1], 14)))
chk("两库的 eps(92,3.3e20) 区间相交", not (eA[1] < eB[0] or eB[1] < eA[0]))
LOGV = F(3976409667298941266, 10 ** 62)      # logs 印的 19 位有效数字值 3.976409667298941266e-44
p("        对拍目标（cycle-2/scripts/results/c2r5_cert.log:24 印 3.976409667298941266e-44）：")
p("          本库区间 = [%s, %s]（22 位）" % (sci(eA[0], 20), sci(eA[1], 20)))
rel = abs(LOGV - eA[0]) / eA[0]
chk("本库区间与日志打印值一致（差在打印舍入误差 1e-18 内；本库区间本身宽约 1e-160 相对）",
    rel < F(1, 10 ** 18), "相对差 = %s" % sci(rel, 6))
p("     [8.2] mpmath.iv（第三引擎，仅作交叉检查；iv.dps 与 mp.dps 同时设置，避双开关陷阱）")
try:
    from mpmath import iv, mp
    iv.dps = 60
    mp.dps = 60
    d_iv = iv.log(3) / iv.log(2)
    s_iv = str(d_iv)                                   # 形如 '[[lo, lo], [hi, hi]]'
    parts = s_iv.replace("[", " ").replace("]", " ").split(",")
    lo_iv, hi_iv = F(parts[0].strip()), F(parts[-1].strip())
    p("        iv 的 delta = [%s, %s]（区间宽 %s，60 dps）" % (R2.dec_str(lo_iv, 61), R2.dec_str(hi_iv, 61),
                                                  sci(hi_iv - lo_iv)))
    p("        本库 delta 区间宽 %s；方向判据：较粗的 iv 区间应包含较细的本库区间" % sci(DHI - DLO))
    ok_iv = (lo_iv <= DLO) and (DHI <= hi_iv)
    chk("iv（60 dps，宽 ~1e-63）包含本库 delta 区间（宽 ~1e-197）", ok_iv,
        "余量 = %s 与 %s" % (sci(DLO - lo_iv), sci(hi_iv - DHI)))
    v_iv = (iv.mpf(92) / 92) * (iv.mpf(T_HI.numerator) / iv.mpf(T_HI.denominator)) \
        * (d_iv - 1) / (d_iv ** 92 - 1)
    v_parts = str(v_iv).replace("[", " ").replace("]", " ").split(",")
    vlo_iv = F(v_parts[0].strip())
    p("        iv 的 v(92, T_hi) 下端 = %s（本库 v 区间 = [%s, %s]）" % (
        R2.sci(vlo_iv, 12), R2.sci(R2.v_bounds(M, M, T_HI, DLO, DHI)[0], 12),
        R2.sci(R2.v_bounds(M, M, T_HI, DLO, DHI)[1], 12)))
    p("        （只作机制检查；不作证书，判定仍以本库区间为准）")
except Exception as exc:                                     # pragma: no cover
    p("        mpmath.iv 不可用：%r" % (exc,))
p("     [8.3] MPFR（gmpy2 定向舍入，独立代码库）")
try:
    import gmpy2
    prec = 300
    R_DN = getattr(gmpy2, "RND_DOWN", None) or getattr(gmpy2, "RoundDown")
    R_UP = getattr(gmpy2, "RND_UP", None) or getattr(gmpy2, "RoundUp")
    p("        舍入模式常量：Down = %s，Up = %s（gmpy2 %s）" % (R_DN, R_UP, gmpy2.version()))
    ctx = gmpy2.get_context()
    ctx.precision = prec
    ctx.round = R_DN
    m_lo = gmpy2.log(gmpy2.mpfr(3)) / gmpy2.log(gmpy2.mpfr(2))
    ctx.round = R_UP
    m_hi = gmpy2.log(gmpy2.mpfr(3)) / gmpy2.log(gmpy2.mpfr(2))
    f_lo = F(*m_lo.as_integer_ratio())
    f_hi = F(*m_hi.as_integer_ratio())
    p("        MPFR(prec=300) 的 delta ∈ [%s, %s]（宽 %s）" % (
        R2.dec_str(f_lo, 60), R2.dec_str(f_hi, 60), sci(f_hi - f_lo)))
    chk("MPFR（300 bit，宽 ~1e-90）包含本库 delta 区间（宽 ~1e-197）", f_lo <= DLO and DHI <= f_hi,
        "余量 = %s 与 %s" % (sci(DLO - f_lo), sci(f_hi - DHI)))
    # 2^v 的对拍（在 T_hi 处的 v 区间上）
    vl, vh = R2.v_bounds(M, M, T_HI, DLO, DHI)
    ctx.round = R_DN
    two_v_lo = gmpy2.exp((gmpy2.mpfr(vl.numerator) / gmpy2.mpfr(vl.denominator))
                         * gmpy2.log(gmpy2.mpfr(2)))
    ctx.round = R_UP
    two_v_hi = gmpy2.exp((gmpy2.mpfr(vh.numerator) / gmpy2.mpfr(vh.denominator))
                         * gmpy2.log(gmpy2.mpfr(2)))
    g_lo, g_hi = F(*two_v_lo.as_integer_ratio()), F(*two_v_hi.as_integer_ratio())
    my_tv = R2.exp_bounds(R2.rd(vl * L2[0]), R2.ru(vh * L2[1]))
    p("        2^{v(T_hi)}：MPFR [%s, %s]；本库 [%s, %s]" % (sci(g_lo, 20), sci(g_hi, 20), sci(my_tv[0], 20), sci(my_tv[1], 20)))
    chk("MPFR 的 2^v 区间包含本库 2^v 区间", g_lo <= my_tv[0] and my_tv[1] <= g_hi,
        "余量 = %s 与 %s" % (sci(my_tv[0] - g_lo), sci(g_hi - my_tv[1])))
except Exception as exc:                                     # pragma: no cover
    p("        gmpy2/MPFR 不可用：%r" % (exc,))
p("     用时 %.2fs" % (time.time() - t0))

# ================= [9] 结论与登记 =================
p("")
p("[9] 结论（按证据类型标注）")
p("     9.1 阈值 T 的严格区间：T ∈ [T_hi, T_lo]，宽度 %s（相对宽 %s，约 %d 位）【严格区间证书】" % (
    sci(T_LO - T_HI), sci((T_LO - T_HI) / T_HI),
    int(-__import__("math").log10(float((T_LO - T_HI) / T_HI)))))
p("         依据：证书 A（[4] 的 A1 至 A6，92 项精确比较）与证书 B（[5] 的 B1 至 B8）。")
p("         证据等级：自足纸面论证加可重跑证书（本机无 Lean / Coq / PARI / Sage，未形式化、未经第三方复核）。")
p("     9.2 「T = R」的识别：本路未裁决（R = 方程 eps(92,K) = gamma - delta 的根，属 route-1 与 route-5 的登记对象）。")
p("         本路可说的只有：T 与 R 都落在 [T_hi, T_lo] 内（R 的落点由 [3] 的两端点符号给出），")
p("         故本路的证书把两者夹在同一区间里，但不识别它们。")
p("     9.3 三套区间的嵌套：[7] 表（I2 ⊆ I5 ⊆ I1，两两相交）。")
p("     9.4 与旧记录的关系：cycle-2/route-3.md §5.1 的严格下界 3.131547906e20 < T（本路 T_hi 的下界更强）；")
p("         cycle-1/route-4.md:201 至 :203 的 19 位浮点区间是数值，非证书。")
p("     9.5 未做的检查（如实登记）：")
p("         - 未复核第 1 轮的 Ψ 非降性证明（本路 A、B 两侧都不使用它）；")
p("         - U(92) 依赖 Simons 与 de Weger 定理 3 的引用形式，本路未回一手原刊（标「未核」）；")
p("         - 未跑 X0 = 704·2^60（arXiv v3）口径；")
p("         - 未做形式化。")

TOTAL = time.time() - T_START
p("")
p("[写盘] results/r2_threshold_cert.log；总用时 %.1fs" % TOTAL)
open(HERE + "/results/r2_threshold_cert.log", "w").write("\n".join(OUT) + "\n")
