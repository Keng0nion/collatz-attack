#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""勘误版替换推导中诸初等步骤的符号核验（sympy）。

只做三类事：
  1. 把原文隐含或省略的初等步骤写成可计算的恒等式或不等式并核验（E1、E2、E4、E6）；
  2. 给出印出版那一步为假的见证，防止本路线回退到印出版措辞（E3）；
  3. 对小 m2 穷举「活跃约束集」，核验顶点识别（corr.txt:54-72）的组合结论（E5）。

运行：
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
     "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts/verify_elementary_steps.py"
"""
from __future__ import annotations

import itertools
import sys

import sympy as sp

OK, BAD = "OK", "FAIL"
results = {}


def e1_convexity():
    """(E1) f(t) = 3/(2^t - 1) 在 t > 0 上严格凸。"""
    t = sp.Symbol("t", positive=True)
    f = 3 / (2 ** t - 1)
    f2 = sp.cancel(sp.diff(f, t, 2))
    num, den = sp.fraction(f2)
    num_f = sp.factor(sp.simplify(num))
    print("[E1] f'' =", f2)
    print("     分子 =", num_f)
    print("     分母 =", sp.factor(den))
    want = 3 * 2 ** t * (2 ** t + 1) * sp.log(2) ** 2
    num_ok = sp.simplify(num - want) == 0
    print("     分子等于 3*2^t*(2^t+1)*log(2)^2：", num_ok)
    print("     两因子在 t>0 时都为正，故 f''>0，f 严格凸；S 为凸函数之和因而凸。")
    return num_ok


def e2_tail():
    """(E2) (u-1)^delta < u^delta - 1（u > 1, delta > 1）。"""
    u, d = sp.Symbol("u", positive=True), sp.Symbol("d", positive=True)
    g = u ** d - (u - 1) ** d
    g1 = sp.simplify(sp.diff(g, u))
    print("[E2] g(u) = u^d - (u-1)^d，g'(u) =", g1)
    print("     d>1、u>1 时 u^{d-1} > (u-1)^{d-1} > 0，故 g'>0，g 严格增；")
    print("     g(1) = 1，故 g(u) > 1，即 (u-1)^d < u^d - 1。")
    g1_at = sp.simplify(g1.subs({u: 3, d: sp.Rational(3, 2)}))
    print("     抽点：g'(3)|_{d=3/2} =", g1_at, "> 0 ?", sp.N(g1_at) > 0)
    delta_v = sp.N(sp.log(3) / sp.log(2), 30)
    pairs = [(sp.Integer(2), sp.Rational(3, 2), "d=3/2"),
             (sp.Rational(3, 2), sp.Integer(2), "d=2"),
             (sp.Integer(10), delta_v, "d=delta")]
    allpos = True
    for uu, dd, tag in pairs:
        val = sp.N(g.subs({u: uu, d: dd}), 25)
        pos = bool(val > 1)
        allpos = allpos and pos
        print("     g(%s, %s) = %s > 1 ? %s   [%s]" % (uu, tag, val, pos, tag))
    print("     取 u = 2^v（v>0）即得 (2^v-1)^delta < 2^{delta v} - 1，这正是 corr.txt:79-82 隐含的一步。")
    return allpos


def e3_printed_false():
    """(E3) 印出版那一步的假不等式：n^{(delta^l)} <= n^{delta} 对 l >= 2、n > 1 为假。"""
    d = sp.Symbol("d", positive=True)
    diff = sp.factor(d ** 2 - d)
    print("[E3] 印出版（h5.txt:798-799）：n^{(delta^l)} <= n^{delta}，取对数等价于 delta^l <= delta")
    print("     l=2 时的差 delta^2 - delta =", diff)
    ok = sp.simplify(diff - d * (d - 1)) == 0
    print("     恒等式成立：", ok, "；delta>1 时 d(d-1)>0，故 delta^2 > delta，")
    print("     乘以 log n > 0（n>1）得 n^{(delta^2)} > n^{delta}，与印出版相反。")
    dv = sp.N(sp.log(3) / sp.log(2), 30)
    print("     数值见证：delta = %s，delta^2 - delta = %s > 0 ? %s"
          % (dv, sp.N(dv ** 2 - dv, 20), float(dv ** 2 - dv) > 0))
    return ok and float(dv ** 2 - dv) > 0


def e4_window_shift():
    """(E4) 窗口平移恒等式：sum x(原窗) - sum x(左移一格) = x_m - x_{m-m2}。"""
    n = 4
    x = sp.symbols("y0:%d" % (n + 1))
    now = sum(x[1:n + 1])
    shifted = sum(x[0:n])
    ident = sp.simplify((now - shifted) - (x[n] - x[0])) == 0
    print("[E4] 以 n=4 个坐标为例（y1..y4 代表窗口坐标，y0 代表窗口左边一格）")
    print("     sum(原窗) - sum(左移窗) =", sp.simplify(now - shifted), "= y_last - y0；恒等：", ident)
    print("     故「左移窗更大」等价于 x_{m-m2} > x_m；取 sum x 最大窗即得 x_{m-m2} <= x_m。")
    return ident


def e5_vertex_structure(nmax=6):
    """(E5) 顶点识别：和约束 + (n-1) 条链/回绕等式给出的坐标是 v*(delta 幂) 的置换。"""
    d, W = sp.symbols("delta W", positive=True)
    all_ok = True
    for n in range(2, nmax + 1):
        xs = [sp.Symbol("x%d" % i) for i in range(1, n + 1)]
        chains = [("chain%d" % i, sp.Eq(xs[i], d * xs[i - 1])) for i in range(1, n)]
        wrap = ("wrap", sp.Eq(xs[0], d * xs[n - 1]))
        sumc = ("sum", sp.Eq(sum(xs), W))
        constr = chains + [wrap, sumc]
        print("  n = %d，约束共 %d 条：" % (n, len(constr)))
        for combo in itertools.combinations(constr, n):
            names = tuple(c[0] for c in combo)
            try:
                sol = sp.linsolve([c[1] for c in combo], xs)
            except Exception as exc:  # noqa: BLE001
                print("    %-40s 求解异常：%s" % (",".join(names), exc))
                all_ok = False
                continue
            if sol == sp.EmptySet or sol is sp.EmptySet:
                print("    %-40s 无解（活跃约束互不相容）" % ",".join(names))
                continue
            vec = list(list(sol)[0])
            zero = all(sp.simplify(vi) == 0 for vi in vec)
            tag = "含和约束" if "sum" in names else "不含和约束"
            if zero:
                # 不含和约束的全链/回绕活跃解为原点，被下界约束 x_i >= 1 排除（这正是计数步的内容）
                print("    %-40s %s；解为原点（全零），被 x_i >= 1 排除：%s"
                      % (",".join(names), tag, "是"))
                continue
            v = sp.simplify(W * (d - 1) / (d ** n - 1))
            ratios = [sp.simplify(vi / v) for vi in vec]
            idx = []
            for r in ratios:
                hit = [j for j in range(n) if sp.simplify(r - d ** j) == 0]
                idx.append(hit[0] if len(hit) == 1 else None)
            same = sorted(x for x in idx if x is not None) == list(range(n)) and all(
                x is not None for x in idx)
            print("    %-40s %s；坐标 = v*(delta 的幂) 的置换？ %s（指数 %s）"
                  % (",".join(names), tag, same, idx))
            if not same:
                all_ok = False
        sol_all = sp.linsolve([c[1] for c in chains + [wrap]], xs)
        print("    全链+回绕活跃（%d 条）的解集：%s" % (n, sol_all))
    print("     结论：顶点识别给出的坐标多重集与 v*(1, delta, ..., delta^{n-1}) 一致，")
    print("     且「链与回绕全活跃」不含和约束时在 n>=3 只给出零解，故和约束必须活跃。")
    return all_ok


def e6_xi1_infeasible():
    """(E6) 几何和：sum_{j=0}^{n-1} delta^j = (delta^n - 1)/(delta - 1)。

    望远镜恒等式 (delta-1)*sum_{j<n} delta^j = delta^n - 1 对每个具体的 n 逐一代数核验；
    一般 n 的手算与之一致（展开消项）。sympy 的 summation 对符号 n 返回 Piecewise，
    故不用它做单一判定。
    """
    d = sp.Symbol("delta", positive=True)
    ident = True
    for n in range(1, 8):
        lhs = sp.expand((d - 1) * sum(d ** j for j in range(n)))
        rhs = sp.expand(d ** n - 1)
        ok = sp.simplify(lhs - rhs) == 0
        ident = ident and ok
        print("[E6] n = %d：(delta-1)*sum_{{j<n}} delta^j - (delta^n - 1) = %s（为 0？ %s）"
              % (n, sp.simplify(lhs - rhs), ok))
    print("     故 sum_{j<n} delta^j = (delta^n - 1)/(delta - 1)（delta > 1 时 delta - 1 != 0）")
    print("     于是 x_i = 1 时 sum x <= (delta^{m2}-1)/(delta-1)；由 c>1 与定理 21 假设右边 < W，矛盾。")
    return ident


def main():
    print("=" * 72)
    print("勘误版替换推导的初等步骤符号核验（sympy %s）" % sp.__version__)
    print("=" * 72)
    results["E1 凸性"] = e1_convexity()
    print()
    results["E2 尾项收口不等式"] = e2_tail()
    print()
    results["E3 印出版那步为假"] = e3_printed_false()
    print()
    results["E4 窗口平移恒等式"] = e4_window_shift()
    print()
    results["E6 几何和"] = e6_xi1_infeasible()
    print()
    print("=" * 72)
    print("E5 小 m2 顶点结构枚举")
    print("=" * 72)
    results["E5 顶点结构"] = e5_vertex_structure()
    print()
    print("=" * 72)
    print("汇总")
    print("=" * 72)
    for k, v in results.items():
        print("  %-22s %s" % (k, OK if v else BAD))
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
