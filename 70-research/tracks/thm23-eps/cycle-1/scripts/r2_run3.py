#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r2_run3.py：三方交叉验证（本路线严格区间 / cycle-2 的 c2r5_rig / cycle-1 的 r4x_core）。

纪律：
- 只调用、不修改 70-research/cycle-2/scripts/c2r5_rig.py 与
  70-research/cycle-1/scripts/r4x_core.py；不写它们的任何输出文件。
- 判定以本路线（r2_rig）的严格区间为准；不一致处单列登记。
- mpmath（dps 200 与 400）只作对照展示，不作判据（见 learnings.md:29 的纪律）。
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r2_rig as R
from fractions import Fraction as F

ROOT = "/Users/luna/Documents/math IA/collatz-attack/70-research"
sys.path.insert(0, os.path.join(ROOT, "cycle-2", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "cycle-1", "scripts"))

OUT = []


def p(s=""):
    OUT.append(s)
    print(s)


R.PREC = 100
N_AT, N_L3, N_LN = 70, 120, 70

M = 91
KSTAR = 205632218873398596256
ROWS = [
    ("步 1（K=7e11）", 47, 7 * 10 ** 11),
    ("步 2（K=5267319278509397）", 67, 5267319278509397),
    ("步 3（K=397560349370386783）", 77, 397560349370386783),
    ("步 4（K=4640282259296926456）", 82, 4640252259296926456 if False else 4640282259296926456),
    ("步 5（K=27444133206411171953）", 86, 27444133206411171953),
    ("步 6（K=77692117359936589463）", 88, 77692117359936589403),
    ("步 7（K=K*）", 91, KSTAR),
    ("步 7 候选 K=2.05e20", 91, 205000000000000000000),
    ("步 7 候选 K=2.06e20", 91, 206000000000000000000),
]


def frac_to_mpf(mp, f):
    return mp.mpf(f.numerator) / mp.mpf(f.denominator)


def main():
    t0 = time.time()
    p("=" * 100)
    p("r2_run3：三方交叉验证（r2_rig 严格区间 / c2r5_rig.eps_bounds / r4x_core（mpmath 200 与 400））")
    p("=" * 100)
    d = R.delta_bounds(N_AT, N_L3)
    l2 = R.ln2_bounds(N_AT)
    p("")
    p("[1] 本路线常数：delta 宽度 %s；ln2 宽度 %s" % (R.sci(d[1] - d[0], 4), R.sci(l2[1] - l2[0], 4)))

    import c2r5_rig as G
    p("    c2r5_rig 载入成功（cycle-2/scripts，只读调用）")
    gd = G.delta_bounds(400)
    gl2 = G.ln2_bounds(400)
    p("    c2r5_rig.delta 宽度 %s" % R.sci(gd[1] - gd[0], 4))

    import r4x_core as C
    p("    r4x_core 载入成功（cycle-1/scripts，只读调用）")

    import mpmath as mp

    mismatches = []
    p("")
    p("[2] 逐行对照（每行：本路线区间；c2r5_rig 区间；mpmath dps 200 与 400 值；判定）")
    p("    「包含」= 对照值/区间与本路线区间一致；mpmath 值打印到 30 位（只作展示）")
    for name, m2, K in ROWS:
        iv, parts = R.eps_bounds(m2, M, K, d[0], d[1], l2, X0=R.X0_695, route="a")
        giv = G.eps_bounds(m2, M, K, gd[0], gd[1], gl2)
        C.set_dps(200)
        v200 = C.eps_of(m2, M, K)
        C.set_dps(400)
        v400 = C.eps_of(m2, M, K)
        s200 = mp.nstr(v200, 30)
        s400 = mp.nstr(v400, 30)
        # 判定
        inter_rc = not (iv[1] < giv[0] or giv[1] < iv[0])
        in_my_400 = iv[0] <= frac_to_mpf(mp, iv[0]) * 0 + mp.mpf(0) or True  # 占位，下面用精确方式
        # 精确方式：把 mpmath 值转成有理数（mpmath 的 mpf 有限二进制 -> 精确 Fraction）
        v400f = F(v400)
        v200f = F(v200)
        in400 = iv[0] <= v400f <= iv[1]
        in200 = iv[0] <= v200f <= iv[1]
        in400_g = giv[0] <= v400f <= giv[1]
        p("")
        p("  ---- %s，m2 = %d，K = %d ----" % (name, m2, K))
        p("    本路线 : [%s ," % R.sci(iv[0], 30))
        p("              %s]   相对宽度 %s" % (R.sci(iv[1], 30), R.sci((iv[1] - iv[0]) / iv[1], 4)))
        p("    c2r5_rig: [%s ," % R.sci(giv[0], 30))
        p("              %s]   相对宽度 %s" % (R.sci(giv[1], 30), R.sci((giv[1] - giv[0]) / giv[1], 4)))
        p("    mpmath200 = %s" % s200)
        p("    mpmath400 = %s" % s400)
        p("    判定：两严格区间相交？%s ；mpmath400 落在本路线区间内？%s ；落在 c2r5_rig 区间内？%s ；mpmath200 落在本路线区间内？%s"
          % (inter_rc, in400, in400_g, in200))
        if not (inter_rc and in400 and in400_g and in200):
            mismatches.append(name)

    p("")
    p("[3] 不一致登记")
    if not mismatches:
        p("    无：九行的两严格区间两两相交，且 mpmath dps 200 与 400 的值都落在两个严格区间内。")
    else:
        for m in mismatches:
            p("    不一致：%s" % m)

    p("")
    p("[4] 说明（证据等级）")
    p("  1. mpmath 无证书：dps 200 与 400 的一致只能作对照，不能作判据（本表用它做「不在证书区间之外」的粗检）。")
    p("     本表把 mpmath 的 mpf 转成精确 Fraction 后比较，故「落在区间内」这一判定本身是精确有理比较。")
    p("  2. c2r5_rig 与本路线不共享代码、参数化也不同（c2r5_rig：ln3 = ln2 + 2 atanh(1/5)；")
    p("     本路线：ln3 = 2 atanh(1/2)，ln2 = 2 atanh(1/3)）；二者的区间相交是本轮最强交叉验证。")
    p("  3. 以本路线（r2_rig）的严格区间为准；两严格区间若不相交，必须单列登记（本表第 3 节）。")
    p("")
    p("用时 %.2f 秒" % (time.time() - t0))
    p("=" * 100)
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "r2_run3.out"), "w") as f:
        f.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
