#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 驱动（第一部分）：锚点自检、Psi 非降、不动点、起点扫描。

运行：
  cd "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts"
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" r4_run.py
"""

import sys
import time

from mpmath import mp, mpf, power, log

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
import r4_psi as R


def sec(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def nstr(x, n=30):
    if x is None:
        return "None"
    return mp.nstr(x, n, strip_zeros=False)


def chain_report(tag, bt):
    print(f"  {tag}")
    for d in bt["detail"]:
        if d["K_out"] is None:
            print(f"    第 {d['iter']} 步  K_in = {nstr(d['K_in'], 24)}"
                  f"  停止：{d['info'].get('reason')}")
            continue
        i = d["info"]
        print(f"    第 {d['iter']} 步  K_in = {nstr(d['K_in'], 24):>28}"
              f"  m2 = {i['m2']:>3}  v = {nstr(i['v'], 18):>24}"
              f"  eps = {mp.nstr(i['eps'], 6):>14}  K_out = {nstr(d['K_out'], 24)}")
    print("    终值 =", nstr(bt["K_final"], 30), " 状态 =", bt["status"])


def main():
    t0 = time.time()
    mp.dps = R.DPS_EPS
    X0, delta, c = R.consts(R.DPS_EPS)
    ctx = (X0, delta, c, R.dpow(delta, 400))

    sec("[0] 常量锚点")
    print("  X0（精确整数）       =", R.X0_INT)
    print("  X0                   =", nstr(X0, 30))
    print("  delta = log3/log2    =", nstr(delta, 40))
    print("  c = log2((162/97)X0) =", nstr(c, 30))
    print("  log2(X0 + 1)         =", nstr(log(X0 + 1) / log(mpf(2)), 30))
    print("  U(91) = 1.4784*91*d^91 =", nstr(R.sdw_upper(91, delta), 30))
    print("  U(92) = 1.4784*92*d^92 =", nstr(R.sdw_upper(92, delta), 30))

    sec("[1] q_min 的三种实现互校（验证 Lemma 22 的转写）")
    terms, complete = R._cf_greedy(delta, 60)
    print("  delta 的连分数前 24 项 =", terms[:24])
    print("  前 60 项全部算完（有理数终止）? ", complete)
    bad = []
    for eps_s in ["1e-3", "1e-5", "1e-7", "2e-9", "3e-11"]:
        epsv = mpf(eps_s)
        rec_a = R.qmin_divergence(epsv)
        qa = rec_a["q"]
        rec_b = R.qmin_semiconvergent(epsv, terms, 10 ** 12)
        qb = rec_b[0] if rec_b else None
        rec_c = R.qmin_bruteforce(epsv, 10 ** 7)
        qc = rec_c[0] if rec_c else None
        ok = (qa == qb and qa is not None)
        if not ok:
            bad.append((eps_s, qa, qb))
        print(f"  eps = {eps_s:>7}  分歧法 = {qa:>12}  半收敛子 = {str(qb):>12}"
              f"  穷举 = {str(qc):>12}  两法一致 ? {ok}")
    print("  两法不一致的 eps：", bad if bad else "无")

    sec("[2] m = 91 锚点（与 margin-table.txt 现行第 89 行对照）")
    bt91 = R.bootstrap(91, mpf(7) * mpf(10) ** 11, ctx)
    chain_report("m = 91，起点 7e11", bt91)
    Kf = int(bt91["K_final"])
    print("  终值（整数） =", Kf)
    print("  等于 7941964418702608664581 ?", Kf == 7941964418702608664581)
    U91, mg91 = R.margin(91, bt91["K_final"], delta)
    print("  U(91)  =", nstr(U91, 30))
    print("  余量   =", nstr(mg91, 30))
    print("  余量 25 位 =", mp.nstr(mg91, 25))
    print("  与钉住值 37.09935525747164492758953 一致 ?",
          mp.nstr(mg91, 25) == "37.09935525747164492758953")
    w = mpf(7941964418702608664581) / (mpf("1.4784") * 91 * power(delta, 91))
    print("  用整数终值重算余量 =", mp.nstr(w, 25), " 差 < 1e-20 ?",
          bool(abs(w - mg91) < mpf("1e-20")))

    sec("[3] m = 92 的链：起点 7e11 与 7.5311e11")
    for K0 in ["7e11", "7.5311e11"]:
        bt = R.bootstrap(92, mpf(K0), ctx)
        chain_report(f"m = 92，起点 {K0}", bt)
    U92, mg92 = R.margin(92, mpf(77692117359936589403), delta)
    print("  U(92)  =", nstr(U92, 30))
    print("  m = 92 链终值 77692117359936589403 / U(92) =", nstr(mg92, 20))

    sec("[4] Psi 非降（m = 92）：网格检验")
    exps = [11.8768, 12, 13, 14, 15, 16, 17, 18, 19, 19.5, 19.9, 20.0,
            20.1, 20.2, 20.3, 20.4, 20.45, 20.48, 20.5, 20.52, 20.53, 20.54]
    grid = [power(mpf(10), mpf(e)) for e in exps]
    prev = None
    nondec = True
    rows = []
    for K in grid:
        Q, info = R.psi(92, K, ctx)
        flag = ""
        if Q is not None and prev is not None and Q < prev:
            nondec = False
            flag = "   <== 下降"
        print(f"    K = {nstr(K, 12):>18}  m2 = {info['m2']:>3}  Psi = "
              f"{nstr(Q, 24):>28}{flag}")
        rows.append((K, Q))
        if Q is not None:
            prev = Q
    print("    网格上 Psi 非降 ?", nondec)
    print("    相邻差值符号：",
          "".join("+" if rows[i + 1][1] > rows[i][1] else
                  ("0" if rows[i + 1][1] == rows[i][1] else "-")
                  for i in range(len(rows) - 1)))

    sec("[5] 不动点：Psi(K) = K 的解（K 必落在 q_min 的塔里）")
    terms_long, _ = R._cf_greedy(delta, 300)
    tower = R.semiconvergents(terms_long, 10 ** 27)
    tower_qs = sorted(set(q for (q, p) in tower))
    print("  塔（分母 <= 1e27 的半收敛子）个数 =", len(tower_qs))
    fixes = []
    for Q in tower_qs:
        if Q < 10 ** 11:
            continue
        Qv = mpf(Q)
        got, info = R.psi(92, Qv, ctx)
        if got is not None and got == Q:
            fixes.append(Q)
    print("  区间 [1e11, 1e27] 内在塔元素上的不动点：")
    for f in fixes:
        print("    K* =", f, " =", nstr(mpf(f), 24),
              "  < U(92) ?", bool(mpf(f) < U92))

    sec("[6] 起点扫描：链的最大值是否越过 U(92)")
    probes = ["7.5311e11", "1e15", "1e18", "1e19", "7.7692117359937e19",
              "1e20", "1.5e20", "2.0e20", "2.05632218873398596256e20",
              "2.5e20", "3.0e20", "3.1e20", "3.2e20", "3.25e20", "3.3e20",
              "3.4e20", "3.4302597024885020978e20"]
    for s in probes:
        bt = R.bootstrap(92, mpf(s), ctx, max_iter=12)
        mx = max(bt["seq"])
        print(f"    K_lo = {s:>28}  T = {nstr(bt['K_final'], 22):>26}"
              f"  越过 U ? {str(bool(mx > U92)):>5}  状态 {bt['status']}")

    print("\n  时间 %.1f 秒" % (time.time() - t0))


if __name__ == "__main__":
    main()
