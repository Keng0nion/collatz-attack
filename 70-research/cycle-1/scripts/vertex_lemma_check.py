#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
顶点引理收口：独立验证脚本（路线 1「顶点引理的初等证明」）。

证据口径（每一节在输出里标注）：
  [0] 定义（先定义后计算）
  [1] 锚点自检：本节定义与常数 vs 项目已钉住的数字
  [2] 精确有理顶点枚举（D 取有理替代值）：核对「顶点族 = 循环等比列」与
      「可行点处下界约束不活跃」，用分数精确算术，不是抽样
  [3] 窗口读法：[Σk 最大] 给不出回绕约束，[Σx 最大] 给得出（同一个数据）
  [4] 收尾不等式 (t+1)^D - t^D >= D 的区间算术证据（手证在报告里）
  [5] 定理 21 前置条件（m2 那条）与 m2 = 92 的可行阈值
  [6] m = 92 一节的算术（U(92)、余量的倒数、网格值比较）

本脚本不 import 任何项目脚本，定义全部在本地重写。

运行：
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
    "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts/vertex_lemma_check.py"
"""

from fractions import Fraction as F
from itertools import combinations

from mpmath import mp, mpf, power, log, iv

mp.dps = 60
iv.dps = 60


# ---------------------------------------------------------------- [0] 定义
print("=" * 78)
print("[0] 定义（先定义后计算）")
print("=" * 78)

X0 = F(695) * F(2) ** 60                      # 论文 Definition 4
delta = log(mpf(3)) / log(mpf(2))              # 论文 Definition 15
c = log(mpf(162) / 97 * mpf(X0.numerator) / mpf(X0.denominator)) / log(mpf(2))

print(f"  X0            = 695 * 2^60 = {X0}")
print(f"  delta         = log3/log2  = {mp.nstr(delta, 25)}")
print(f"  c = log2((162/97)X0)       = {mp.nstr(c, 25)}")
print()
print("  多面体 P_W(n, D)（全部非严格约束）：")
print("    y_j >= 1 (j = 1..n)；y_{j+1} <= D*y_j (j = 1..n-1)；y_1 <= D*y_n；sum y >= W")
print("  严格版 P^<_W(n, D)：仅把 y_1 <= D*y_n 换成 y_1 < D*y_n")
print("  顶点候选参数 a = W*(D-1)/(D^n - 1)（本脚本记作 a_of）")
print()


def a_of(n, W, D):
    return W * (D - 1) / (D ** n - 1)


# ---------------------------------------------------------------- [1] 锚点
print("=" * 78)
print("[1] 锚点自检：本节定义与常数 vs 项目已钉住的数字")
print("=" * 78)

ok_all = True

got40 = mp.nstr(delta, 40)
print(f"  [1a] delta 40 位 = {got40}")
print(f"       钉住值       = 1.58496250072115618145373894394781650876")
hit = got40 == "1.58496250072115618145373894394781650876"
print(f"       逐位一致 ? {hit}")
ok_all &= bool(hit)

U91 = mpf("1.4784") * 91 * power(delta, 91)
K91 = mpf(7941964418702608664581)
margin91 = K91 / U91
print(f"  [1b] U(91) = 1.4784*91*delta^91 = {mp.nstr(U91, 31)}")
print(f"       钉住值 214072842063828923281.358576944")
print(f"       K(91) 下界 = {mp.nstr(K91, 25)}（钉住 7941964418702608664581）")
print(f"       余量 25 位 = {mp.nstr(margin91, 25)}")
print(f"       钉住值       37.09935525747164492758953")
g1 = mp.nstr(U91, 31).startswith("214072842063828923281.35857694")
g2 = mp.nstr(margin91, 25) == "37.09935525747164492758953"
print(f"       U(91) 前缀一致 ? {g1}；余量 25 位一致 ? {g2}")
ok_all &= bool(g1 and g2)

print(f"  [1c] c 的钉住值 70.180806328308366825；本次 {mp.nstr(c, 25)}")
g3 = mp.nstr(c, 25).startswith("70.18080632830836682")
print(f"       前缀一致 ? {g3}")
ok_all &= bool(g3)

m, m2 = 91, 47
K_lo = mpf("7.5311e11")
lhs = c * (power(delta, m2) - 1) / (delta - 1)
rhs = mpf(m2) / m * K_lo
print(f"  [1d] 自举第一步的前置条件 (m2=47, m=91, K_lo=7.5311e11)：")
print(f"       c*(delta^47-1)/(delta-1) = {mp.nstr(lhs, 20)}")
print(f"       (47/91)*K_lo             = {mp.nstr(rhs, 20)}")
print(f"       前置条件成立（左边 <= 右边）? {lhs <= rhs}")
ok_all &= bool(lhs <= rhs)

print(f"\n  锚点自检合计：{'全部一致' if ok_all else '有不一致（见上）'}")
print()


# ---------------------------------------------------------------- [2] 顶点枚举
print("=" * 78)
print("[2] 精确有理顶点枚举（D 有理；分数算术，无浮点）")
print("=" * 78)


def gauss(A, b):
    """精确高斯消元；A 为 n x n 分数矩阵；返回唯一解或 None（奇异）。"""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if M[r][col] != 0:
                piv = r
                break
        if piv is None:
            return None
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [a - f * bb for a, bb in zip(M[r], M[col])]
    return [M[i][n] for i in range(n)]


def constraints_of(n, D, W):
    """[(coeffs, rhs, name)]，全部写成 coeffs . y <= rhs。"""
    cons = []
    for j in range(n):
        a = [F(0)] * n
        a[j] = F(-1)
        cons.append((a, F(-1), f"L{j + 1}"))
    for j in range(n - 1):
        a = [F(0)] * n
        a[j + 1] = F(1)
        a[j] = -D
        cons.append((a, F(0), f"G{j + 1}"))
    a = [F(0)] * n
    a[0] = F(1)
    a[n - 1] = -D
    cons.append((a, F(0), f"G{n}"))
    a = [F(-1)] * n
    cons.append((a, -W, "W"))
    return cons


def feasible(y, cons):
    return all(sum(a * x for a, x in zip(c[0], y)) <= c[1] for c in cons)


def enumerate_vertices(cons, n):
    verts = set()
    for sub in combinations(range(len(cons)), n):
        A = [cons[i][0][:] for i in sub]
        b = [cons[i][1] for i in sub]
        y = gauss(A, b)
        if y is None:
            continue
        if feasible(y, cons):
            verts.add(tuple(y))
    return verts


def predicted_family(n, D, W):
    """缺第 k 条链约束时，坐标是 (a, D a, ..., D^{n-1} a) 的循环排列。"""
    a = a_of(n, W, D)
    pts = set()
    for k in range(n):
        y = [None] * n
        for t in range(n):
            y[(k + t) % n] = a * D ** t
        pts.add(tuple(y))
    return pts


rational_Ds = [F(3, 2), F(8, 5), F(111, 70)]
print("  D         n   W 倍数   顶点数  预测族  顶点族一致?  顶点含坐标 1?")
rows = []
for D in rational_Ds:
    for n in range(2, 8):
        thr = (D ** n - 1) / (D - 1)
        for Wmul in [F(3, 2), F(4), F(10)]:
            W = Wmul * thr
            cons = constraints_of(n, D, W)
            verts = enumerate_vertices(cons, n)
            fam = predicted_family(n, D, W)
            same = (verts == fam)
            has_one = any(any(x == 1 for x in y) for y in verts)
            rows.append((D, n, Wmul, len(verts), len(fam), same, has_one))
            print(f"  {str(D):>8} {n:>3}   {str(Wmul):>5}   {len(verts):>6}  "
                  f"{len(fam):>6}  {str(same):>11}  {str(has_one):>11}")
print(f"\n  [2a] 全部 {len(rows)} 个组合上「顶点集合 = 预测的循环等比列族」? "
      f"{all(r[5] for r in rows)}")
print(f"  [2b] 存在坐标为 1 的顶点? {any(r[6] for r in rows)}")
print("  [2c] W 一律取成严格大于 (D^n-1)/(D-1)，对应论文前置条件 c > 1 的情形")
print()

print("  [2d] LP（用同一枚举机具）：给定 y_j = 1、链约束、y >= 1，max sum y 是否")
print("       恰好等于 (D^n-1)/(D-1)（即「某坐标等于 1 时和的上界」）？")
lp_ok = []
for D in rational_Ds:
    for n in range(2, 7):
        thr = (D ** n - 1) / (D - 1)
        cons = constraints_of(n, D, F(0))
        for jfix in range(n):
            cons2 = list(cons)
            cons2.append(([F(1) if i == jfix else F(0) for i in range(n)], F(1),
                          f"EQ{jfix + 1}"))
            cons2.append(([F(-1) if i == jfix else F(0) for i in range(n)], F(-1),
                          f"EQneg{jfix + 1}"))
            best = None
            for sub in combinations(range(len(cons2)), n):
                y = gauss([cons2[i][0][:] for i in sub], [cons2[i][1] for i in sub])
                if y is None or not feasible(y, cons2):
                    continue
                s = sum(y)
                if best is None or s > best:
                    best = s
            lp_ok.append(best == thr)
print(f"       全部相等 ? {all(lp_ok)}（{len(lp_ok)} 个组合）")
print()


# ---------------------------------------------------------------- [3] 反例
print("=" * 78)
print("[3] 窗口读法：[Σk 最大] 给不出回绕约束，[Σx 最大] 给得出（同一个数据）")
print("=" * 78)


def place_window(xs, a, m):
    """循环移位：使 0 基的窗口 (a, a+1) 落在 0 基位置 (m-2, m-1) 即 1 基 (m-1, m)。"""
    return [xs[(a + j - 2) % m] for j in range(m)]


m_c, m2_c = 4, 2
k = [F(1), F(1), F(2), F(1)]
x = [F(31, 20), F(12, 5), F(5, 2), F(1)]
K_tot = sum(k)
print(f"  m = {m_c}, m2 = {m2_c}, k = {[str(t) for t in k]}, K = {K_tot}, "
      f"(m2/m)K = {F(m2_c, m_c) * K_tot}")
print(f"  x = {[str(t) for t in x]}")
print(f"  x_i >= k_i 全部成立 ? {all(a >= b for a, b in zip(x, k))}")

ivd = iv.log(3) / iv.log(2)
ratios = []
for i in range(m_c):
    num = iv.mpf(x[(i + 1) % m_c].numerator) / iv.mpf(x[(i + 1) % m_c].denominator)
    den = iv.mpf(x[i].numerator) / iv.mpf(x[i].denominator)
    ratios.append(bool(num / den < ivd))
print(f"  区间算术 x_(i+1)/x_i < delta：{ratios}；全成立 ? {all(ratios)}")

win = {}
print("  窗口(1 基)    Σk     Σx")
for j in range(m_c):
    i1, i2 = j, (j + 1) % m_c
    win[(i1, i2)] = (k[i1] + k[i2], x[i1] + x[i2])
    print(f"    ({i1 + 1},{i2 + 1})        {win[(i1, i2)][0]}      {win[(i1, i2)][1]}")
maxk = max(v[0] for v in win.values())
maxx = max(v[1] for v in win.values())
print(f"  Σk 最大 = {maxk}；Σx 最大 = {maxx}；门槛 (m2/m)K = {F(m2_c, m_c) * K_tot}")

print("\n  读法一（按 Σk 最大取窗口 (3,4)，放在位置 (3,4)）：")
w_k = (2, 3)
xk = place_window(x, w_k[0], m_c)
print(f"    重排后 x(位置 1..4) = {[str(t) for t in xk]}")
print(f"    Σk(窗) = {win[w_k][0]} >= (m2/m)K ? {win[w_k][0] >= F(m2_c, m_c) * K_tot}")
print(f"    x_(m-m2) = 位置 2 的 {xk[1]}；x_m = 位置 4 的 {xk[3]}")
print(f"    论文那一步 x_(m-m2) <= x_m 成立 ? {xk[1] <= xk[3]}")
lhs_w = iv.mpf(xk[2].numerator) / iv.mpf(xk[2].denominator)
rhs_w = ivd * (iv.mpf(xk[3].numerator) / iv.mpf(xk[3].denominator))
print(f"    回绕约束 x_(m-m2+1) < delta*x_m 成立 ? {bool(lhs_w < rhs_w)}"
      f"   （x_(m-m2+1) = {xk[2]}，delta*x_m = {mp.nstr(mpf(rhs_w.a), 20)}...）")

print("\n  读法二（按 Σx 最大取窗口 (2,3)，平移放到位置 (3,4)）：")
w_x = (1, 2)
xx = place_window(x, w_x[0], m_c)
print(f"    重排后 x(位置 1..4) = {[str(t) for t in xx]}")
print(f"    Σk(窗) = {win[w_x][0]} >= (m2/m)K ? {win[w_x][0] >= F(m2_c, m_c) * K_tot}")
print(f"    Σx(窗) = {win[w_x][1]} = Σx 最大 ? {win[w_x][1] == maxx}")
print(f"    论文那一步 x_(m-m2) <= x_m 成立 ? {xx[1] <= xx[3]}   （{xx[1]} <= {xx[3]}）")
lhs_w2 = iv.mpf(xx[2].numerator) / iv.mpf(xx[2].denominator)
rhs_w2 = ivd * (iv.mpf(xx[3].numerator) / iv.mpf(xx[3].denominator))
print(f"    回绕约束 x_(m-m2+1) < delta*x_m 成立 ? {bool(lhs_w2 < rhs_w2)}"
      f"   （delta*x_m = {mp.nstr(mpf(rhs_w2.a), 20)}...）")
print()


# ---------------------------------------------------------------- [4] 不等式
print("=" * 78)
print("[4] 收尾不等式：(t+1)^delta - t^delta >= delta > 1")
print("=" * 78)
print("  手证见报告（中值定理）。此处给 60 位区间算术证据（不是证明）：")
tests = [1, 2, 3, 10, 100, 10 ** 6, int(2 ** mpf("75.5946323945")),
         int(2 ** mpf("79.562387618086"))]
bad = []
for t in tests:
    lhs_i = iv.power(iv.mpf(t + 1), ivd) - iv.power(iv.mpf(t), ivd)
    if not (lhs_i > 1):
        bad.append(t)
print(f"    t 取值 {tests}")
print(f"    全部 t 上 (t+1)^delta - t^delta > 1 ? {len(bad) == 0}（失败者：{bad}）")
for vv in ["75.5946323945", "79.562387618086"]:
    l1 = iv.power(iv.mpf(2), ivd * iv.mpf(vv)) - 1
    r1 = iv.power(iv.power(iv.mpf(2), iv.mpf(vv)) - 1, ivd)
    print(f"    v = {vv}：2^(delta v) - 1 >= (2^v - 1)^delta ? {bool(l1 >= r1)}")
print()


# ---------------------------------------------------------------- [5] 前置条件
print("=" * 78)
print("[5] 定理 21 前置条件与 m2 = 92 的可行阈值")
print("=" * 78)
thr = {}
for m2v in [47, 67, 82, 91, 92]:
    thr[m2v] = c * (power(delta, m2v) - 1) / (delta - 1)
    print(f"  m2 = {m2v:>3}：前置条件要求 (m2/m)*K_lo >= {mp.nstr(thr[m2v], 20)}")
print(f"  说明：m2 = 92（m = 92、乘子 92/92 = 1）的可行阈值 K_lo >= "
      f"{mp.nstr(thr[92], 20)}")
print(f"        它落在网格的 3.0257e20 与 3.1e20 之间 ? "
      f"{mpf('3.0257e20') < thr[92] <= mpf('3.1e20')}"
      f"（网格里 3.0257e20 那格最优 m2 = 91、3.1e20 那格是 92）")
print()


# ---------------------------------------------------------------- [6] m=92
print("=" * 78)
print("[6] m = 92 一节的算术核对")
print("=" * 78)
U92 = mpf("1.4784") * 92 * power(delta, 92)
term92 = mpf(77692117359936589403)
mar92 = term92 / U92
print(f"  U(92) = 1.4784*92*delta^92 = {mp.nstr(U92, 25)}")
print(f"       表（margin-table.txt 现行第 92 行）给 3.4302597024885020978e+20")
print(f"  链终值 = {mp.nstr(term92, 25)}（表给 77692117359936589403）")
print(f"  余量 = 终值/U(92) = {mp.nstr(mar92, 25)}（表给 0.226490482057595771625621）")
print(f"  余量的倒数 1/余量 = {mp.nstr(1 / mar92, 20)}")
print(f"       => 「m = 92 差 4.4 倍」的指代 = 1/余量 = {float(1 / mar92):.4f}")
print(f"  U(92)/U(91) = {mp.nstr(U92 / U91, 20)}（不是 4.4）")

grid = [("7.5311e11", "5267319278509397.0", 47),
        ("1e15", "130441933147714940.0", 63),
        ("1e18", "4640282259296926456.0", 79),
        ("1e20", "205632218873398596256.0", 89),
        ("2.05632218873398596256e20", "205632218873398596256.0", 91),
        ("3.1e20", "205632218873398596256.0", 92),
        ("3.3e20", "7941964418702608664581.0", 92),
        ("3.4302597024885020978e20", "1.567829661853181873291e+22", 92)]
print("\n  网格点（项目自述，脚本 [5e0] 输出）与 U(92) 的比较：")
prev = None
mono = True
for (Klo, psi, m2v) in grid:
    p = mpf(psi)
    if prev is not None and p < prev:
        mono = False
    prev = p
    print(f"    K_lo = {Klo:>28}  m2 = {m2v:>3}  Psi = {psi:>26}  "
          f"Psi <= U(92) ? {p <= U92}")
print(f"  网格上 Psi 非降 ? {mono}（与脚本 [5e0] 打印的 True 一致）")
print("  注意：3.3e20 与 U(92) 两行的 Psi 都大于 U(92)，而 1e20 那行小于 U(92)。")
print()
print("=" * 78)
print("脚本结束")
print("=" * 78)
