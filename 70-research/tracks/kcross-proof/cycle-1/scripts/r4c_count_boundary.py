#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 4 路任务 (c)：计数引理的边界压力。

目标命题（route-5 §6.2 第 1.3 步用到的计数事实）：
    「同一分母 K* 的两个分数不可能同时落入 (delta, beta(K*))」。
本脚本用的判据是精确比较
    beta - delta < 1/K*，
其中 beta = delta + eps_opt(K*)，故 beta - delta 的严格上界取 eps_opt(K*) 的上界。

同时给出一个更强的初等推论并做精确化：
    对每个整数 q <= K*，任意两个同分母分数相差至少 1/q >= 1/K*，
    故每个分母 q <= K* 至多一个分数落入 (delta, beta(K*)) —— 只要
    beta - delta < 1/K*（用严格上界验证）。

边界压力：把区间右端从 beta 的严格上界再向外放大一个网格宽度 GRID = 10^-100 的
任意倍数？不需要——本脚本一律用严格上界，并额外做两件事：
  1. 用 beta 的上界（而不是下界）做比较，余量量化打印；
  2. 反算使比较翻向所需的区间宽度阈值：beta - delta >= 1/K* 需要比实际宽度大多少倍。

运行：/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python r4c_count_boundary.py
"""
import sys

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
sys.path.insert(0, HERE)
from fractions import Fraction as F
import r4_common as C

OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


DLO, DHI, L2 = C.consts()
CIV = C.R.C_bounds()
KSTAR = C.KSTAR

p("#" * 74)
p("# 任务 (c)：beta - delta < 1/K* 的精确比较与「每个分母至多一个」推论")
p("# 脚本：tracks/kcross-proof/cycle-1/scripts/r4c_count_boundary.py")
p("#" * 74)
p("")
p("[0] 输入量与证据类型")
p("    delta ∈ [%s, %s]（严格区间，宽度 %s）" % (C.dec(DLO, 45), C.dec(DHI, 45), C.fnum(DHI - DLO)))
p("    来源：kc_rig.delta_bounds（ln2、ln3 的自足 atanh 级数界，网格 10^-100）")

info = C.eps_opt(KSTAR, CIV, DLO, DHI, L2)
EPS_LO, EPS_HI = info["lo"], info["hi"]
p("    K* = %d" % KSTAR)
p("    eps_opt(K*) ∈ [%s, %s]（约定 M；argmin = %s，唯一分离）" % (
    C.dec(EPS_LO, 44), C.dec(EPS_HI, 44), info["argmin"]))
p("    证据类型：eps_opt 区间来自 kc_rig.eps_bounds（精确有理区间，逐格最小），")
p("              delta 来自 kc_rig.delta_bounds；两者都未形式化、未经第三方复核。")

p("")
p("[1] 核心比较：beta - delta 的严格上界 vs 1/K*")
WD = C.R.ru(DHI + EPS_HI) - C.R.rd(DLO)     # beta 上界 - delta 下界（比真宽度大）
WD_STRICT = EPS_HI                          # eps_opt 上界即为 beta-delta 的严格上界
ONE_OVER = F(1, KSTAR)
p("    beta - delta 的严格上界（取 eps_opt(K*) 上界）= %s" % C.dec(WD_STRICT, 44))
p("    1/K* = %s" % C.dec(ONE_OVER, 44))
p("    比较 WD_STRICT < 1/K* ？ %s" % (WD_STRICT < ONE_OVER))
p("    余量（1/K* - eps_hi）= %s" % C.dec(ONE_OVER - WD_STRICT, 44))
p("    比值 (1/K*)/eps_hi ∈ [%s, %s]" % (
    C.dec(ONE_OVER / EPS_HI, 6), C.dec(ONE_OVER / EPS_LO, 6)))

p("")
p("[2] 更保守的形态：用 delta 的下界与 beta 的上界做成外扩区间后仍成立")
p("    外扩区间宽度 = beta_hi - delta_lo = %s" % C.dec(WD, 44))
p("    外扩后仍 < 1/K* ？ %s ；余量 = %s" % (WD < ONE_OVER, C.dec(ONE_OVER - WD, 44)))

p("")
p("[3] 加强推论：对一切 q <= K*，每个分母 q 至多一个分数落入 (delta, beta(K*))")
p("    理由：同分母 p1/q, p2/q 相差 >= 1/q >= 1/K* > beta - delta，")
p("          若两者都在区间内则相差 < beta - delta，矛盾。")
p("    该推论把所有 q <= K* 一并覆盖（不止 q = K*）。严格性来源同上：")
p("      beta - delta 的严格上界 < 1/K*（第 1 节精确比较）。")
# 验证对若干具体 q 的等价计数界（q 递减时 1/q 增大，仍 > WD_STRICT）
for q in (KSTAR, KSTAR - 1, KSTAR // 2, 10 ** 10, 77692117359936589403):
    p("      q = %d ：1/q > eps_hi ？ %s" % (q, F(1, q) > WD_STRICT))

p("")
p("[4] 边界反算：比较翻向所需的条件")
p("    需要 beta - delta >= 1/K* 才可能出现同分母两个分数；")
p("    即区间宽度至少要到 1/K* = %s。" % C.dec(ONE_OVER, 44))
p("    实际宽度上界只有 %s，两者相差倍率 %s。" % (
    C.dec(WD_STRICT, 44), C.dec(ONE_OVER / WD_STRICT, 6)))
p("    若把 eps_opt 相对放大 10^21 倍（超过上述倍率）才能触发反例形态；")
p("    learnings.md:38 的教训（放大 delta 不得当严格性检验）在本脚本不适用：")
p("    本脚本没有替换 delta，全部用 delta 与 eps 的严格界。")

p("")
p("[5] 结论（按证据类型）")
p("    C1【已证，精确有理比较】beta(K*) - delta < 1/K*，且余量为 1/K* - eps_hi = %s > 0。" % (
    C.dec(ONE_OVER - WD_STRICT, 30)))
p("    C2【已证，初等推论】对每个 q <= K*，至多一个分母为 q 的分数落入 (delta, beta(K*))；")
p("       特别地 q = K* 处至多一个（这正是 route-5 1.3 步所用）。")
p("    C3【未证，且本路不涉及】「至少一个」一侧（gamma 的落点）由 c2r5_cert 第 2 节给出，")
p("       不属本路计数引理的边界问题；本路只核「至多」一侧。")
p("    C4【登记】上述严格性等级受 kc_rig 未形式化约束，与项目其余证书同级。")

open(HERE + "/results/r4c_count_boundary.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/r4c_count_boundary.out")
