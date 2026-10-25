#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 驱动（第二部分）：
  (A) m = 91 锚点：论文的七步链（max_iter = 7）终值与余量；
  (B) 越界阈值的二分：K_thr := min{ K : Psi_92(K) > U(92) }；
  (C) 论文 Corollary 24 的 m <= 98 行给出的合法起点（与 m 的链终值对照）；
  (D) m = 92 至 120 的链终值与判定，检验「最大可排除 m = 91」。

运行：
  cd "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts"
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" r4_run2.py
"""

import sys

from mpmath import mp, mpf, power, log

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
import r4_psi as R


def sec(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def nstr(x, n=30):
    return "None" if x is None else mp.nstr(x, n, strip_zeros=False)


def main():
    mp.dps = R.DPS_EPS
    X0, delta, c = R.consts(R.DPS_EPS)
    ctx = (X0, delta, c, R.dpow(delta, 400))
    U92 = R.sdw_upper(92, delta)

    sec("[A] m = 91 锚点：论文的七步链（max_iter = 7）")
    bt = R.bootstrap(91, mpf(7) * mpf(10) ** 11, ctx, max_iter=7)
    for d in bt["detail"]:
        i = d["info"]
        print(f"  第 {d['iter']} 步  K_in = {nstr(d['K_in'], 24):>26}"
              f"  m2 = {i['m2']:>3}  v = {nstr(i['v'], 18):>24}"
              f"  eps = {mp.nstr(i['eps'], 6):>14}  K_out = {nstr(d['K_out'], 24)}")
    K7 = bt["K_final"]
    print("  七步终值 =", nstr(K7, 30))
    print("  等于 7941964418702608664581 ?", int(K7) == 7941964418702608664581)
    U91, mg = R.margin(91, K7, delta)
    print("  U(91) =", nstr(U91, 30))
    print("  余量 =", nstr(mg, 30))
    print("  余量 25 位 =", mp.nstr(mg, 25))
    print("  与钉住值 37.09935525747164492758953 逐位一致 ?",
          mp.nstr(mg, 25) == "37.09935525747164492758953")
    # 逐位比较：钉住值来自 margin-table.txt 现行第 89 行
    print("  margin-table 现行第 89 行的余量字段 = 37.0993552574716449275895")
    print("  本文件 25 位 = ", mp.nstr(mg, 25))
    print("  第 8 步（论文没有的续算）说明：K = 7.94e21 时最优 m2 = 91 = m，A = 0，")
    print("  v = 2919.6，尾项 3/(2^v - 1) 已不足 1e-120，eps 只剩被丢弃量级；")
    print("  故再迭代无意义——论文恰在此处停手并在下一步改用 Corollary 17 的分支。")

    sec("[B] 越界阈值 K_thr := min{ K : Psi_92(K) > U(92) } 的二分")
    print("  U(92) =", nstr(U92, 30))
    lo = mpf("3.0") * mpf(10) ** 20
    hi = mpf("3.2") * mpf(10) ** 20
    Qlo, _ = R.psi(92, lo, ctx)
    Qhi, _ = R.psi(92, hi, ctx)
    print("  Psi(3.0e20) =", nstr(Qlo, 24), " > U ?", bool(Qlo > U92))
    print("  Psi(3.2e20) =", nstr(Qhi, 24), " > U ?", bool(Qhi > U92))
    for _ in range(120):
        mid = (lo + hi) / 2
        Q, _i = R.psi(92, mid, ctx)
        if Q > U92:
            hi = mid
        else:
            lo = mid
    print("  二分 120 轮后：")
    print("    lo（Psi <= U）= ", nstr(lo, 30))
    print("    hi（Psi >  U）= ", nstr(hi, 30))
    print("    hi - lo =", nstr(hi - lo, 10))
    print("    hi / U(92) =", nstr(hi / U92, 20))
    print("    hi 与 U(92) 的间距 =", nstr(U92 - hi, 10))
    print("    Psi(lo) =", nstr(R.psi(92, lo, ctx)[0], 24))
    print("    Psi(hi) =", nstr(R.psi(92, hi, ctx)[0], 24))

    sec("[C] 论文 Corollary 24 的起点：m <= 98 那一行的真值")
    print("  逐 m 链终值（起点 7e11，七步型到不动点为止，max_iter = 40）：")
    for m in [92, 95, 98, 99, 100, 110, 117, 120, 130, 150, 200, 276]:
        bt = R.bootstrap(m, mpf(7) * mpf(10) ** 11, ctx, max_iter=40)
        Um = R.sdw_upper(m, delta)
        print(f"    m = {m:>4}  终值 = {nstr(bt['K_final'], 24):>30}"
              f"  状态 {bt['status']:>12}  终值 < U(m) ? "
              f"{'无 U' if Um is None else bool(bt['K_final'] < Um)}")

    sec("[D] m = 92 至 100 的判定（独立复现 margin-table 的 92 至 95 行）")
    for m in list(range(92, 101)):
        bt = R.bootstrap(m, mpf(7) * mpf(10) ** 11, ctx, max_iter=40)
        Um = R.sdw_upper(m, delta)
        mg = bt["K_final"] / Um
        print(f"    m = {m:>3}  K 下界 = {nstr(bt['K_final'], 24):>30}"
              f"  上界 = {nstr(Um, 24):>30}  余量 = {nstr(mg, 20)}"
              f"  判定 = {'排除' if bt['K_final'] > Um else '不排除'}")

    sec("[E] 合法起点的清单（m = 92 口径）")
    print("  1. Simons 与 de Weger v1.44 Corollary 11：345301 <= m <= 648401 时")
    print("     K > q_24 = 753110839881 = 7.5311e11（/tmp/sidw144.txt:622 至 :623）")
    print("  2. Hercher 2023 Corollary 24 第一行：m <= 98 时 K > 7.76e19（表 1，")
    print("     该行 7.76e19 是截断记法；本文件的 m = 98 链终值见 [C]）")
    print("  3. 链自身给出的更强起点（由 1 或 2 经 Psi 迭代得到）")
    print("  以上都在 K* = 205632218873398596256 与 K_thr 之下，见 [B]")


if __name__ == "__main__":
    main()
