#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
只读探针：加载项目脚本 60-audits/hercher-t21/scripts/rederive-erratum.py 为模块，
打印它的可行性判据与 v 的定义在链上参数处的取值。

目的：确认（或否证）审计关键词——链的第一步所用的 (m2, K) 是否满足
定理 21 陈述里的前提 (delta^{m2}-1)/(delta-1) * c <= (m2/m)K，以及脚本的
v_of 与报告里印的 v 是否同一个量。

不运行 main()，不写任何仓库文件。
运行：
  /Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python \
    "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts/probe_project_module.py"
"""

import importlib.util
import sys

from mpmath import mp, mpf, nstr

PROJ = "/Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/scripts/rederive-erratum.py"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)      # 模块尾部有 __main__ 保护，导入不会跑 main()
    return mod


p = load_module(PROJ, "rederive_erratum")

mp.dps = 120
X0, delta, c = p.setup(120)
pw = p.delta_powers(delta, 200, 120)

print("=== 脚本自带的常数 ===")
print("  c := log2((162/97)X0) =", nstr(c, 20))
print("  X0                    =", nstr(X0, 20))
print("  delta                 =", nstr(delta, 20))
print()

print("=== 可行性判据 (delta^t-1)/(delta-1)*c <= (t/m)K 在各 K 处对 (m=91, m2=47) ==")
for Ks in ["7e11", "7.5311e11", "1e15", "5.267319278509397e15",
           "1e18", "1e20", "2.05632218873398596256e20",
           "3.4302597024885020978e20", "6.18e24"]:
    K = mpf(Ks)
    mmax = p.feasible_m2_max(91, K, delta, c, pw)
    feas47 = p.m2_feasible(47, 91, K, delta, c, pw)
    v47 = p.v_of(47, 91, K, delta, pw)
    lhs = (pw[47] - 1) / (delta - 1) * c
    rhs = (mpf(47) / 91) * K
    print(f"  K = {Ks:>26}  mmax = {str(mmax):>4}  feasible(47) = {str(feas47):>5}"
          f"  v_of(47,91,K) = {nstr(v47, 10)}")
    print(f"        LHS(47) = {nstr(lhs, 14)}   RHS(47) = {nstr(rhs, 14)}")

print()
print("=== 用脚本自身的 best_m2 看链的第一步（m = 91, K = 7e11）===")
mmax, best = p.best_m2(91, mpf("7e11"), X0, delta, c, pw, p.eps_of, "73")
print("  feasible_m2_max =", mmax)
print("  best['m2'] =", best["m2"], " v =", nstr(best["v"], 12),
      " eps =", nstr(best["eps"], 12), " A =", nstr(best["A"], 12))
print("  t1 = 3/(2^v-1) =", nstr(best["t1"], 12), "  t2 =", nstr(best["t2"], 12))

print()
print("=== 对同一 K，逐个 m2 的 eps（仅列可行者前若干）===")
K = mpf("7e11")
rows = []
for t in range(1, 92):
    if p.m2_feasible(t, 91, K, delta, c, pw):
        rec = p.eps_of(t, 91, K, X0, delta, pw, "73")
        rows.append((t, rec["v"], rec["eps"]))
print("  可行 m2 的个数 =", len(rows), " 最小/最大 =",
      rows[0][0] if rows else None, rows[-1][0] if rows else None)
for (t, v, e) in rows[:6] + rows[-4:]:
    print(f"    m2 = {t:>3}  v = {nstr(v, 10):>14}  eps = {nstr(e, 10):>16}")

print()
print("=== 反查：什么 K 会让 m2=47 恰好可行（边界）===")
boundary = (pw[47] - 1) / (delta - 1) * c * 91 / 47
print("  K_boundary(47,91) =", nstr(boundary, 16))
b48 = (pw[48] - 1) / (delta - 1) * c * 91 / 48
print("  K_boundary(48,91) =", nstr(b48, 16))
print("  即 m2=47 可行要求 K >= 上式；47 是最大可行者的 K 区间上端另算。")

print()
print("=== 报告印的 v = 84.0214032616 与 v_of 的对照 ===")
print("  v_of(47, 91, 7e11)    =", nstr(p.v_of(47, 91, mpf("7e11"), delta, pw), 20))
print("  v_of(47, 92, 7.5311e11) =", nstr(p.v_of(47, 92, mpf("7.5311e11"), delta, pw), 20))
print("  84.0214032616... 与 v_of 不同，说明报告里印的 v 另有算法。")
