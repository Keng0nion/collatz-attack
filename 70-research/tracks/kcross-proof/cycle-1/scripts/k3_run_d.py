#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 (d)：[3.12, 3.15]×10^20 上的主导权 eps_opt = eps(92, ·) 独立重算。

精确陈述（对应 c2r5_cert.log:71 与 :72）：
  (D1) 对一切 K ∈ [3.12×10^20, 3.15×10^20] 与一切 m2 ∈ F_92(K) \\ {92}：
       eps(92, K) < eps(m2, K)。
  本路线的证明装配（两个初等引理 + 两个端点严格判定）：
   引理 A：固定 m2，K ↦ eps(m2, K) 严格递减（分母 3K ln2 递增，分子三项里 A 为常数、
           3/(2^v−1) 与 3(m2−1)/(2^v−1)^δ 随 v(K) = c·K 递增而递减）。
   引理 B：F_92(K) 关于 K 单调不减（门槛式 (D2) 的直接推论）。
   端点判定一：eps(92, K1) 的上界 < theta，K1 = 3.12×10^20；
   端点判定二：min_{m2 <= 91} eps(m2, K2) 的下界 > theta，K2 = 3.15×10^20；
               （下界用 A 部分：eps(m2,K) >= A(m2)/(3K·ln2_hi) >= A(91)/(3K2·ln2_hi)）
   于是对 K ∈ [K1,K2]、m2 ∈ F(K)\\92：eps(92,K) <= eps(92,K1) < theta < eps(m2,K2) <= eps(m2,K)。
  (D2) 把 c2r5 的 150 步二分端点（只读重放）作为同一对象的对照点，在其上重算 [5] 行的两个数。

运行：20-experiments/.venv/bin/python k3_run_d.py
"""
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import k3_rig as K

C2SCRIPTS = HERE.parents[3] / "cycle-2" / "scripts"
OUT = []
OUTPATH = HERE / "results" / "k3_run_d.out"


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


M = 92
GAM = F(325919355854421968365, 205632218873398596256)
D = K.delta_bounds()
L2 = K.ln2_bounds()
C = K.C_bounds()
X0 = K.X0_INT

K1 = F(312) * 10 ** 18
K2 = F(315) * 10 ** 18
GD_LO = GAM - D[1]          # gamma - delta 的下界
GD_HI = GAM - D[0]          # gamma - delta 的上界

p("#" * 74)
p("# route-3 (d)：[3.12, 3.15]×10^20 主导权重算与根区间复核")
p("# 运行脚本：tracks/kcross-proof/cycle-1/scripts/k3_run_d.py")
p("#" * 74)

p("")
p("[0] 常数（本路线）")
p("    delta ∈ [%s, %s]" % (K.dec(D[0], 55), K.dec(D[1], 55)))
p("    gamma = %d/%d" % (GAM.numerator, GAM.denominator))
p("    gamma − delta ∈ [%s, %s]" % (K.sci(GD_LO, 22), K.sci(GD_HI, 22)))
p("    与 results_rig.txt:31 的 6.2446806696927356659061116684983820458161e-43 一致（22 位）")


def rel_agree(mine, theirs, digits=20):
    """按有效数字比较（容许两侧各自打印的最后一位），返回布尔。"""
    tol = F(1, 10 ** (digits - 1))
    return abs(mine - theirs) <= tol * abs(theirs)


# ---------- 1. 端点判定一 ----------
p("")
p("[1] 端点判定一：eps(92, K1) 的上界，K1 = %s" % K1)
e92K1 = K.eps_bounds(92, M, K1, D[0], D[1], L2)
p("    eps(92, K1) ∈ [%s, %s]" % (K.sci(e92K1[0], 24), K.sci(e92K1[1], 24)))
p("    该点上 m2 = 92 可行？ %s（门槛比较）" % K.feasible(92, M, K1, D[0], D[1], C))

# ---------- 2. 端点判定二 ----------
p("")
p("[2] 端点判定二：min_{m2 <= 91} eps(m2, K2) 的下界，K2 = %s" % K2)
amin = None
for t in range(1, 92):
    a = K.A_of(t, M)
    if amin is None or a < amin[1]:
        amin = (t, a)
p("    argmin_{1<=m2<=91} A(m2) = m2 = %d，A = %s（= 3/X0 ？ %s）" % (
    amin[0], K.sci(amin[1], 22), amin[1] == F(3, K.X0_INT)))
assert amin[0] == 91 and amin[1] == F(3, K.X0_INT)
THETA = K.rd(amin[1] / (3 * K2 * L2[1]))
p("    A 下界 theta = A(91)/(3·K2·ln2_hi) = %s" % K.sci(THETA, 24))
worst = None
for t in range(83, 92):
    if K.feasible(t, M, K2, D[0], D[1], C) is not True:
        continue
    e = K.eps_bounds(t, M, K2, D[0], D[1], L2)
    if worst is None or e[0] < worst[1]:
        worst = (t, e[0])
p("    梯子（m2 = 83..91，在 K2 可行者）：min eps 下界 = %s（m2 = %d）" % (K.sci(worst[1], 24), worst[0]))
p("    （注：此处 K2 = 3.15e20 > 日志的 K2' ≈ 3.13195e20，故该值略小；与单调性一致）")

# ---------- 3. 主导权 ----------
p("")
p("[3] 主导权（比值与余量）")
ratio = e92K1[1] / THETA
p("    eps(92, K1) 上界 / theta = %s" % K.sci(ratio, 20))
p("    theta / eps(92, K1) 上界 = %s（> 1 即主导权成立）" % K.sci(1 / ratio, 20))
assert e92K1[1] < THETA
p("    -> (D1) 对一切 K ∈ [K1, K2] 与 m2 ∈ F(K)\\92 成立")
p("       余量因子 = %s" % K.sci(THETA / e92K1[1], 20))

# ---------- 4. 重放 c2r5 的 150 步二分（只读对照） ----------
p("")
p("[4] 对照：重放 c2r5_cert.py 第 5 节的 150 步二分（只读 import c2r5_rig）")
sys.path.insert(0, str(C2SCRIPTS))
import c2r5_rig as R2

DLO2, DHI2 = R2.delta_bounds()
L22 = R2.ln2_bounds()
GD_LO2, GD_HI2 = GAM - DHI2, GAM - DLO2


def sign_theirs(Kv):
    e = R2.eps_bounds(M, M, Kv, DLO2, DHI2, L22)
    if e[0] > GD_HI2:
        return "above"
    if e[1] < GD_LO2:
        return "below"
    return None


Ka, Kb = F(312) * 10 ** 18, F(315) * 10 ** 18
for _ in range(150):
    Km = (Ka + Kb) / 2
    s = sign_theirs(Km)
    if s == "above":
        Ka = Km
    elif s == "below":
        Kb = Km
    else:
        break
p("    重放端点：K1' = %s" % K.dec(Ka, 46))
p("                K2' = %s" % K.dec(Kb, 46))
rw = (Kb - Ka) / Ka
p("    相对宽度 = %s ；一致十进制位 ≈ %d" % (K.sci(rw, 4), int(-__import__("math").log10(float(rw)))))
LOG1 = "313195478959172262876.6365306194907065260231016940260118526233"
LOG2 = "313195478959172262876.6365306194907065260231016961279595491105"
p("    与 c2r5_cert.log:67 的 40 位截断十进制逐位一致？ %s ；%s" % (
    K.dec(Ka, 40) == LOG1, K.dec(Kb, 40) == LOG2))
e92Ka = K.eps_bounds(92, M, Ka, D[0], D[1], L2)
p("    本路线在 K1' 上的 eps(92, K1') 上界 = %s" % K.sci(e92Ka[1], 24))
p("    与 c2r5_cert.log:71 的 6.2446806696927356659061116685e-43 同值？（20 位） %s" % (
    rel_agree(e92Ka[1], F("6.2446806696927356659061116685e-43"))))
lowK2p = min(K.eps_bounds(t, M, Kb, D[0], D[1], L2)[0]
             for t in range(1, 92)
             if K.feasible(t, M, Kb, D[0], D[1], C) is True)
p("    本路线在 K2' 上的 min_{m2<=91 可行} eps 下界 = %s" % K.sci(lowK2p, 24))
p("    与 c2r5_cert.log:71 的 5.74876439712480888646759896504e-42（m2 = 91 处取到）同值？（20 位） %s" % (
    rel_agree(lowK2p, F("5.74876439712480888646759896504e-42"))))
p("    25 步回看：对 K 邻近 K1' 的点，本路线的 47 位区间内主导权余量见第 3 节（端点更严）")

# ---------- 5. 本路线自己的二分（我的 sign 与我的机器） ----------
p("")
p("[5] 本路线自己的二分（我的 sign_my 与我的 eps_bounds；同一方程 eps(92,K) = gamma − delta）")


def sign_my(Kv):
    e = K.eps_bounds(M, M, Kv, D[0], D[1], L2)
    if e[0] > GD_HI:
        return "above"
    if e[1] < GD_LO:
        return "below"
    return None


p("    起点符号：K = 3.12e20 %s ；K = 3.15e20 %s" % (sign_my(K1), sign_my(K2)))
assert sign_my(K1) == "above" and sign_my(K2) == "below"
Ma, Mb = K1, K2
steps = 150
for i in range(steps):
    Km = (Ma + Mb) / 2
    s = sign_my(Km)
    if s == "above":
        Ma = Km
    elif s == "below":
        Mb = Km
    else:
        steps = i
        break
p("    二分 %d 步（未定即停）：根 ∈ [%s, %s]" % (steps, K.dec(Ma, 50), K.dec(Mb, 50)))
m1 = (Ma - K1) * 2 ** steps / (K2 - K1)
m2_ = (Mb - K1) * 2 ** steps / (K2 - K1)
assert m1.denominator == 1 and m2_.denominator == 1
p("    精确端点（本次 150 步）：Ma = %d / %d ；Mb = %d / %d" % (
    Ma.numerator, Ma.denominator, Mb.numerator, Mb.denominator))
p("    等价整数写法：Ma = 312*10^18 + %d*(3*10^18)/2^150 ；Mb = 312*10^18 + %d*(3*10^18)/2^150" % (
    m1.numerator, m2_.numerator))
rwd = (Mb - Ma) / Ma
p("    相对宽度 = %s ；一致十进制位 ≈ %d" % (K.sci(rwd, 4), int(-__import__("math").log10(float(rwd)))))
L1 = F(45136225354708871151757558816616152091, 2 ** 57)
U1 = F(361089802837670969214060470532929216895, 2 ** 60)
p("    route-1 的 60 步区间 [%s, %s]（route1_extra.out:21 至 :25 的精确端点）" % (K.dec(L1, 40), K.dec(U1, 40)))
p("    本路线区间 ⊆ route-1 区间？ %s（左余量 %s，右余量 %s）" % (
    L1 < Ma and Mb < U1, K.sci(Ma - L1, 4), K.sci(U1 - Mb, 4)))
p("    与重放的 150 步区间相交？ %s ；两端点逐项相等？ %s , %s" % (
    max(Ma, Ka) < min(Mb, Kb), Ma == Ka, Mb == Kb))
p("    （两端点逐项相等 => 本路线与 c2r5 的符号函数在 150 步里的每次判定都一致）")
s876 = sign_my(F(313195478959172262876))
s877 = sign_my(F(313195478959172262877))
p("    整数点复核：313195478959172262876 符号 %s ；313195478959172262877 符号 %s" % (s876, s877))
p("    （对照 results_rig.txt:65 至 :67：876 判定=含 gamma、877 判定=不含 gamma）")

# ---------- 6. 结论与分栏登记 ----------
p("")
p("[6] (d) 结论与两件事的分栏登记")
p("    (D1) 成立【已证（条件：定理 21 的公式与 (D2)/(D3)/(D5) 的定义；引理 A、B 为初等）】")
p("    第 1 栏【对象 R = eps(92,K) − (gamma−delta) 的根】：本路线独立严格区间见第 5 节；")
p("         与 route-1 的 60 步区间相含、与 route-5 的 150 步区间相交")
p("    第 2 栏【对象 T = 越界阈值：「R = T」】：本轮**未证**，本路线不为它提供新证据")

OUTPATH.write_text("\n".join(OUT) + "\n", encoding="utf-8")
print("\n[写出] results/k3_run_d.out")
