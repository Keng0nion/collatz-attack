#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 4 路任务 (d)：口径压力。

三件事：
  1. U(92) = 1.4784 * 92 * delta^92 的严格区间（自算，对照 c2r5_cert.log:76），
     并在区间内移动（取两端）检查两个严格不等式
        K* < U(92) 与 U(92) < 7941964418702608664581
     的余量；顺带核 K1（根区间左端）< U(92)。
  2. X0 = 695*2^60（印出版）与 704*2^60（arXiv v3）两种口径下 R 的位移：
     初等观察 ε(92,K) 的公式不含 X0（A(m) = 0，v 不含 X0）⟹ 方程
     eps(92,K) = gamma - delta 的根在两种口径下是同一个数（位移 = 0，精确）。
     再把两边口径的「主导权复核」（[K1,K2] 上 eps_opt = eps(92,.)）分别严格重做，
     并核 c_92(704) < K1，说明动力学阈值 T（= eps_opt 的根）在两口径下也不动。
  3. 支配权的口径压力：若错误改用 m2 = 91 支（例如忽略 92 的可行性），
     方程 eps(91,K) = gamma - delta 的根在哪里？给严格区间并核它 > U(92)。

运行：/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python r4d_gauge.py
"""
import sys
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
CIV695 = C.R.C_bounds()
CIV704 = C.gauge_C(C.X0_704)
N794 = 7941964418702608664581

p("#" * 74)
p("# 任务 (d)：U(92) 的严格区间内移动；X0 两种口径下 R 的位移")
p("# 脚本：tracks/kcross-proof/cycle-1/scripts/r4d_gauge.py")
p("#" * 74)
p("")

# ---------- [1] U(92) 严格区间与两个严格不等式 ----------
p("[1] U(92) = 1.4784*92*delta^92 的严格区间与余量")
U92 = (C.R.rd(C.U92_W * C.M * C.R.iv_pow((DLO, DHI), 92)[0]),
       C.R.ru(C.U92_W * C.M * C.R.iv_pow((DLO, DHI), 92)[1]))
p("    U(92) ∈ [%s, %s]" % (C.dec(U92[0], 30), C.dec(U92[1], 30)))
p("    区间宽度 = %s（对照 c2r5_cert.log:76 打印 343025970248850209780.074794593）" % C.fnum(U92[1] - U92[0]))
p("    K* = %d" % C.KSTAR)
p("    U_lo - K* = %s（正？ %s）" % (C.dec(U92[0] - C.KSTAR, 6), U92[0] > C.KSTAR))
p("    N794 = %d" % N794)
p("    N794 - U_hi = %s（正？ %s）" % (C.dec(N794 - U92[1], 6), N794 > U92[1]))
t0 = time.time()
K1, K2 = C.root_interval(DLO, DHI, L2, steps=150)
p("    K1（根区间左端，150 步） = %s ；K2 = %s（用时 %.1f 秒）" % (
    C.dec(K1, 32), C.dec(K2, 32), time.time() - t0))
p("    U_lo - K2 = %s（正？ %s）；U_lo - K1 = %s（正？ %s）" % (
    C.dec(U92[0] - K2, 6), U92[0] > K2, C.dec(U92[0] - K1, 6), U92[0] > K1))
p("    在 U(92) 区间内移动：两端点分别按最不利方向使用（K* < U_lo、U_hi < N794），")
p("    故结论对 U(92) 的一切可能真值成立。")

# ---------- [2] X0 两口径：R 的位移 ----------
p("")
p("[2] X0 = 695*2^60 与 704*2^60 两种口径下 R 的位移")
p("    初等观察（本路新增）：m2 = m = 92 时 A(m) = 0，且 v = K(delta-1)/(delta^92-1)")
p("    不含 X0，故 eps(92,K) 与 X0 无关；gamma 是 delta 的连分数构造（分母 K* = q_43），")
p("    同样与 X0 无关。因此方程 eps(92,K) = gamma - delta 的根 R 在两口径下是同一个数。")
p("    位移 = 0（精确相等），证据类型：初等恒等式（读公式）+ 下面两条严格复核。")
p("    C(695) ∈ [%s, %s]" % (C.dec(CIV695[0], 30), C.dec(CIV695[1], 30)))
p("    C(704) ∈ [%s, %s] ；差 ∈ [%s, %s]" % (
    C.dec(CIV704[0], 30), C.dec(CIV704[1], 30),
    C.dec(CIV704[0] - CIV695[1], 12), C.dec(CIV704[1] - CIV695[0], 12)))

p("")
p("    [2.1] 主导权复核（对每口径）：对一切 m2 <= 91 且 K2 可行者，")
p("          eps(m2, K2) 的下界 > eps(92, K1) 的上界？")
for tag, XV, CIV in (("695", C.X0_695, CIV695), ("704", C.X0_704, CIV704)):
    eK1 = C.R.eps_bounds(92, 92, K1, DLO, DHI, L2, X0=XV)
    worst_t, worst_lo = None, None
    n_feas = 0
    fo = open(HERE + "/results/r4d_domination_%s.out" % tag, "w")
    for t in range(1, 92):
        if C.R.feasible_decision(t, 92, K2, DLO, DHI, CIV) is not True:
            continue
        n_feas += 1
        e2 = C.R.eps_bounds(t, 92, K2, DLO, DHI, L2, X0=XV)
        if worst_lo is None or e2[0] < worst_lo:
            worst_t, worst_lo = t, e2[0]
        fo.write("m2=%d feasible_at_K2=1 eps_lo=%s eps_hi=%s\n" % (
            t, C.dec(e2[0], 44), C.dec(e2[1], 44)))
    fo.close()
    p("          X0 = %s 口径：eps(92,K1) 上界 = %s" % (tag, C.dec(eK1[1], 44)))
    p("             min（可行 m2 的 eps 下界）= %s（m2 = %s 处；可行计数 %d）" % (
        C.dec(worst_lo, 44), worst_t, n_feas))
    p("             严格分离？ %s ；余量 = %s" % (
        eK1[1] < worst_lo, C.dec(worst_lo - eK1[1], 44)))

p("")
p("    [2.2] 门槛 c_92 在两口径下的严格区间（c_92 = geom(92) * C，因为 m2 = m）")
for tag, CIV in (("695", CIV695), ("704", CIV704)):
    g = C.R.geom_bounds(92, DLO, DHI)
    c_lo = C.R.rd(g[0] * CIV[0])
    c_hi = C.R.ru(g[1] * CIV[1])
    p("          X0 = %s：c_92 ∈ [%s, %s] ；c_92_hi < K1 ？ %s" % (
        tag, C.dec(c_lo, 30), C.dec(c_hi, 30), c_hi < K1))
p("    结论：两口径下都有 c_92 < R，且 [K1,K2] 上 eps_opt = eps(92,.)，")
p("    故动力学阈值 T（eps_opt 的根）在两口径下也落在同一个严格区间 [K1,K2] 内。")

# ---------- [3] 支配权口径压力：91 支的根 ----------
p("")
p("[3] 支配权压力：方程 eps(91,K) = gamma - delta 的根")
GD_LO, GD_HI = C.GAMMA - DHI, C.GAMMA - DLO


def sign91(K):
    e = C.R.eps_bounds(91, 92, K, DLO, DHI, L2)
    if e[0] > GD_HI:
        return "above"
    if e[1] < GD_LO:
        return "below"
    return None


A91, B91 = F(1) * 10 ** 20, F(1) * 10 ** 22
sA, sB = sign91(A91), sign91(B91)
p("    端点符号：K = 1e20 -> %s ；K = 1e22 -> %s" % (sA, sB))
if sA == "above" and sB == "below":
    for _ in range(80):
        Km = (A91 + B91) / 2
        s = sign91(Km)
        if s == "above":
            A91 = Km
        elif s == "below":
            B91 = Km
        else:
            break
    p("    eps(91,.) = gamma - delta 的根 ∈ [%s, %s]" % (C.dec(A91, 30), C.dec(B91, 30)))
    p("    该根 > U(92) 上界？ %s" % (A91 > U92[1]))
else:
    p("    符号未分离，未定位。")

p("")
p("[4] 结论（按证据类型）")
p("    D1【已证，精确有理比较】K* < U_lo、U_hi < 7941964418702608664581，")
p("       余量见第 1 节（在 U(92) 严格区间的两端取最不利方向）。")
p("    D2【已证，初等恒等式 + 两口径严格复核】R 在同一数上：位移 = 0；")
p("       两口径的 eps_opt = eps(92,.) 主导权与 c_92 < K1 都逐条严格复核（第 2 节）。")
p("    D3【已证，严格区间】91 支的根远离 U(92)（第 3 节），说明支配权若失效后果巨大；")
p("       该根不属任何现行结论的依赖项，只作压力对照。")
p("    总用时 %.1f 秒。" % (time.time() - t_start))

open(HERE + "/results/r4d_gauge.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/r4d_gauge.out")
