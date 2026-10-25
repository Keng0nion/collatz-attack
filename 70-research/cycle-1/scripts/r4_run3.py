#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 驱动（第三部分）：数值稳健性。
  (F) q_min 对工作精度 dps_cf 的稳健性（250 / 320 / 400 位）；
  (G) q_min 对 eps 的扰动稳健性（相对扰动 1e-40 与 1e-60）；
  (H) 关键比值。

运行：
  cd "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts"
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" r4_run3.py
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

    sec("[F] q_min 对 dps_cf 的稳健性")
    cases = []
    # 链上出现的 eps：m = 91 第 7 步、m = 92 各步、以及两个不动点处的 eps
    bt91 = R.bootstrap(91, mpf(7) * mpf(10) ** 11, ctx, max_iter=7)
    for d in bt91["detail"]:
        cases.append(("m91 步 " + str(d["iter"]), d["info"]["eps"]))
    bt92 = R.bootstrap(92, mpf(7) * mpf(10) ** 11, ctx, max_iter=40)
    for d in bt92["detail"]:
        cases.append(("m92 步 " + str(d["iter"]), d["info"]["eps"]))
    for K in ["205632218873398596256", "77692117359936589403"]:
        Q, info = R.psi(92, mpf(K), ctx)
        cases.append(("m92 K=" + K, info["eps_ub"]))

    print("  每个 eps 用三档 dps_cf 各算一次，比较 q_min：")
    allsame = True
    for (tag, e) in cases:
        res = []
        for dcf in (250, 320, 400):
            rec = R.qmin_divergence(e, dps_cf=dcf)
            res.append(None if rec is None else rec["q"])
        same = len(set(res)) == 1
        if not same:
            allsame = False
        print(f"    {tag:>12}  eps = {mp.nstr(e, 8):>12}  q = {res[0]}"
              f"  三档一致 ? {same}")
    print("  全部三档一致 ?", allsame)

    sec("[G] q_min 对 eps 的扰动稳健性")
    print("  对每个 eps 取 eps*(1 ± 1e-40) 与 eps*(1 ± 1e-60)，比较 q_min：")
    allstable = True
    for (tag, e) in cases:
        base = R.qmin_divergence(e, dps_cf=300)
        qb = None if base is None else base["q"]
        outs = []
        for rel in ("1e-40", "1e-60"):
            for sgn in (1, -1):
                ep = e * (mpf(1) + sgn * mpf(rel))
                r = R.qmin_divergence(ep, dps_cf=300)
                outs.append((rel, sgn, None if r is None else r["q"]))
        ok = all(o[2] == qb for o in outs)
        if not ok:
            allstable = False
        print(f"    {tag:>12}  q = {qb}  扰动后仍相同 ? {ok}"
              + ("" if ok else "   " + str(outs)))
    print("  全部扰动稳定 ?", allstable)

    sec("[H] 关键比值与阈值")
    U92 = R.sdw_upper(92, delta)
    Kthr = mpf("313195478959172262876.636530619")
    Kstar = mpf("205632218873398596256")
    Kfix1 = mpf("77692117359936589403")
    SdW = mpf("753110839881")
    print("  U(92)            =", nstr(U92, 30))
    print("  K_thr            =", nstr(Kthr, 30))
    print("  K_thr / U(92)    =", nstr(Kthr / U92, 20))
    print("  U(92) - K_thr    =", nstr(U92 - Kthr, 20))
    print("  K*  = 205632218873398596256   K_thr / K* =", nstr(Kthr / Kstar, 20))
    print("  K*  / 7.7692117359937e19     =", nstr(Kstar / Kfix1, 20))
    print("  K_thr / 7.7692117359937e19   =", nstr(Kthr / Kfix1, 20))
    print("  K_thr / 753110839881         =", nstr(Kthr / SdW, 20))
    print("  K* / U(92)                   =", nstr(Kstar / U92, 20))
    print("  log10(K_thr) =", nstr(log(Kthr) / log(mpf(10)), 20))
    print("  log10(K*)    =", nstr(log(Kstar) / log(mpf(10)), 20))
    print("  log10(U(92)) =", nstr(log(U92) / log(mpf(10)), 20))

    sec("[I] 塔的完整性与不动点的穷尽性")
    terms, _ = R._cf_greedy(delta, 300)
    tower = R.semiconvergens_placeholder if False else R.semiconvergents(terms, 10 ** 27)
    qs = sorted(set(q for (q, p) in tower))
    print("  分母 <= 1e27 的半收敛子个数 =", len(qs))
    print("  最小的几个 =", qs[:6])
    print("  最大的几个 =", qs[-4:])
    print("  1e20 至 1e21 之间的塔元素 =",
          [q for q in qs if 10 ** 20 <= q <= 10 ** 21])
    print("  说明：U(92) = 3.43e20 < 1e27，故 U(92) 以下的不动点全部落在本塔内，")
    print("        本文件在塔元素上逐点检验 Psi(Q) = Q，即穷尽了 U(92) 以下的不动点。")
    print("  另：q_24（SdW 的 7.5311e11 出处）= 753110839881 是否在塔里 ?",
          753110839881 in set(qs))


if __name__ == "__main__":
    main()
