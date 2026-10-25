#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
顶点引理收口：独立验证脚本（路线 1：「顶点引理的初等证明」）。

证据口径（本脚本每一节都在输出里标注）：
  [0] 定义（先定义后计算）
  [1] 锚点自检（用项目已钉住的数字核对本节用的定义与常数）
  [2] 精确有理顶点枚举（δ 取有理替代值）：核对手证引理「顶点族 = 循环等比列」
      与「下界约束在可行点处不活跃」两条，用分数精确算术，不是抽样
  [3] 窗口读法反例（Σk 读法给不出回绕约束；Σx 读法给得出），区间算术核对
  [4] 收尾不等式 (t+1)^δ − t^δ ≥ δ 的区间算术证据（手证另在报告里）
  [5] 定理 21 前置条件（m₂ 的那条）在自举第一步的核对，与 m₂ = 92 的可行阈值
  [6] m = 92 一节的算术（U(92)、余量的倒数、网格值的比较）

本脚本不 import 任何项目脚本，全部定义在本地重写。
运行：/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python \\
        '/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts/vertex_lemma_check.py'
"""

from fractions import Fraction as F
from itertools import combinations
import sys

from mpmath import mp, mpf, power, log, iv, mpi

mp.dps = 60
iv.dps = 60


# ---------------------------------------------------------------- [0] 定义
print("=" * 78)
print("[0] 定义（先定义后计算）")
print("=" * 78)

# 论文 Definition 4：X0 = 695 * 2^60
X0 = F(695) * F(2) ** 60
# 论文 Definition 15：delta = log(3)/log(2)
delta = log(mpf(3)) / log(mpf(2))
# 定理 21 前置条件里的常数（抽取文本乱码，按证明的用法复原）：
#   c = log( (162/97) * X0 ) / log(2)
c = log(mpf(162) / 97 * mpf(X0.numerator) / mpf(X0.denominator)) / log(mpf(2))

print(f"  X0            = 695 * 2^60 = {X0} (={float(X0):.17g})")
print(f"  delta         = log3/log2  = {mp.nstr(delta, 25)}")
print(f"  c = log2((162/97)X0)       = {mp.nstr(c, 25)}")
print(f"  (162/97)*X0   = {float(X0) * 162 / 97:.17g}")
print()

print("  多面体 P_W(n, D)（全部非严格约束，D 为比值常数）：")
print("    y_j >= 1 (j = 1..n)；y_{j+1} <= D*y_j (j = 1..n-1)；y_1 <= D*y_n；sum y >= W")
print("  严格版 P^<_W(n, D)：仅把 y_1 <= D*y_n 换成 y_1 < D*y_n")
print("  顶点值 v = W*(D-1)/(D^n - 1)")
print()


def v_of(n, W, D):
    return W * (D - 1) / (D ** n - 1)


# ---------------------------------------------------------------- [1] 锚点
print("=" * 78)
print("[1] 锚点自检：本节定义与常数 vs 项目已钉住的数字")
print("=" * 78)

ok_all = True

# 1a delta 的 40 位前缀（audit-report.md 钉住值）
delta_pin = mpf("1.58496250072115618145373894394781650876")
got = mp.nstr(delta, 40)
print(f"  [1a] delta 40 位 = {got}")
print(f"       钉住值       = 1.58496250072115618145373894394781650876")
hit = got.startswith("1.58496250072115618145394394781650876") or \
      mp.nstr(delta, 41)[:41] == mp.nstr(1 / mpf(1), 41)  # 占位，下面仍按前缀比对
hit = got.replace(" ", "") == mp.nstr(delta_pin, 40).replace(" ", "")
print(f"       逐位一致 ? {hit}")
ok_all &= bool(hit)

# 1b K 上界 U(91) 与余量（margin-table.txt 现行第 91 行与第 115 行）
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
# 余量的精确有理表达（整数比）
exact_margin = F(7941964418702608664581) / F(int(mp.nint(U91)))  # 仅作十进制约分参考
print(f"       U(91) 前缀一致 ? {g1}；余量 25 位一致 ? {g2}")
ok_all &= bool(g1 and g2)

# 1c c 的钉住值（rederivation-erratum.md 的 (A7) 写 c = 70.18...）
print(f"  [1c] c = 70.180806328308366825 ? 本次 {mp.nstr(c, 25)}")
g3 = mp.nstr(c, 25).startswith("70.18080632830836682")
print(f"       前缀一致 ? {g3}")
ok_all &= bool(g3)

# 1d 自举第一步的前置条件：(m2/m)K >= c*(delta^m2-1)/(delta-1)
m, m2 = 91, 47
K_lo = mpf("7.5311e11")
lhs = c * (power(delta, m2) - 1) / (delta - 1)
rhs = mpf(m2) / m * K_lo
print(f"  [1d] 第一步前置条件 (m2=47, m=91, K_lo=7.5311e11):")
print(f"       c*(delta^47-1)/(delta-1) = {mp.nstr(lhs, 20)}  <=  (47/91)*K_lo = {mp.nstr(rhs, 20)} ? {lhs <= rhs}")
ok_all &= bool(lhs <= rhs)

print(f"\n  锚点自检合计：{'全部一致' if ok_all else '有不一致（见上）'}")
print()


# ---------------------------------------------------------------- [2] 顶点枚举
print("=" * 78)
print("[2] 精确有理顶点枚举（D 取有理替代值；分数算术，无浮点）")
print("=" * 78)


def gauss(A, b):
    """精确高斯消元；A 为 n x n 分数矩阵。返回唯一解或 None（奇异）。"""
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
    """返回 [(coeffs, rhs, name)]，全部写成 coeffs . y <= rhs 的形式（非严格）。"""
    cons = []
    for j in range(n):
        a = [F(0)] * n
        a[j] = F(-1)
        cons.append((a, F(-1), f"L{j+1}"))                     # -y_j <= -1
    for j in range(n - 1):
        a = [F(0)] * n
        a[j + 1] = F(1)
        a[j] = -D
        cons.append((a, F(0), f"G{j+1}"))                      # y_{j+1} - D y_j <= 0
    a = [F(0)] * n
    a[0] = F(1)
    a[n - 1] = -D
    cons.append((a, F(0), f"G{n}"))                            # 回绕：y_1 - D y_n <= 0
    a = [F(-1)] * n
    cons.append((a, -W, "W"))                                  # -sum y <= -W
    return cons


def points_of_intersection(cons, subset):
    n = len(cons[0][0])
    A = [cons[i][0][:] for i in subset]
    b = [cons[i][1] for i in subset]
    return gauss(A, b)


def feasible(y, cons):
    return all(sum(a * x for a, x in zip(c[0], y)) <= c[1] for c in cons)


def enumerate_vertices(n, D, W):
    cons = constraints_of(n, D, W)
    verts = set()
    singular = 0
    for sub in combinations(range(len(cons)), n):
        y = points_of_intersection(cons, sub)
        if y is None:
            singular += 1
            continue
        if feasible(y, cons):
            verts.add(tuple(y))
    return verts, cons, singular


def predicted_family(n, D, W):
    v = v_of(n, W, D)
    pts = set()
    for k in range(n):                    # 缺哪条链约束（1 基编号 k+1）
        y = [None] * n
        a = v
        # y_{k+1} = a, y_{k+2} = D a, ... 绕一圈
        for t in range(n):
            y[(k + t) % n] = a * D ** t
        pts.add(tuple(y))
    return pts


rational_Ds = [F(3, 2), F(8, 5), F(111, 70)]
rows = []
for D in rational_Ds:
    for n in range(2, 8):
        thr = (D ** n - 1) / (D - 1)      # (D^n-1)/(D-1)：坐标取到 1 时的和上界
        for Wmul in [F(3, 2), F(4), F(10)]:
            W = Wmul * thr
            verts, cons, sing = enumerate_vertices(n, D, W)
            fam = predicted_family(n, D, W)
            same = (verts == fam)
            novtx1 = all(all(len(set(y)) == 1 and y[0] == 1 for _ in [0]) is False
                         for y in verts)
            # 是否有顶点的某个坐标等于 1
            has_one = any(any(x == 1 for x in y) for y in verts)
            rows.append((D, n, Wmul, len(verts), len(fam), same, has_one, sing))

print("  D        n   W 倍数   顶点数  预测族大小  顶点族一致?  顶点含坐标 1?")
for (D, n, Wmul, nv, nf, same, has_one, sing) in rows:
    print(f"  {str(D):>8} {n:>3}   {str(Wmul):>5}   {nv:>6}  {nf:>10}  "
          f"{str(same):>10}  {str(has_one):>11}")
all_same = all(r[5] for r in rows)
any_one = any(r[6] for r in rows)
print(f"\n  [2a] 全部 (D, n, W) 组合上「顶点集合 = 预测的循环等比列族」? {all_same}")
print(f"  [2b] 存在坐标为 1 的顶点? {any_one}")
print(f"  [2c] 说明：W 取成严格大于 (D^n-1)/(D-1)，对应论文前置条件 c>1 的情形")

# [2d] 固定 y_j = 1 时的 max sum y（另一个 LP，用同样的枚举机具）
print()
print("  [2d] LP：给定 y_j = 1 与全部链约束、y >= 1，max sum y 是否等于 (D^n-1)/(D-1)？")
lp_rows = []
for D in rational_Ds:
    for n in range(2, 7):
        thr = (D ** n - 1) / (D - 1)
        cons = constraints_of(n, D, F(0))
        for jfix in range(n):
            cons2 = list(cons) + [([F(1) if i == jfix else F(0) for i in range(n)],
                                   F(1), f"EQ{jfix+1}"),
                                  ([F(-1) if i == jfix else F(0) for i in range(n)],
                                   F(-1), f"EQneg{jfix+1}")]
            best = None
            for sub in combinations(range(len(cons2)), n):
                y = points_of_intersection(cons2, sub)
                if y is None or not feasible(y, cons2):
                    continue
                s = sum(y)
                if best is None or s > best:
                    best = s
            lp_rows.append((D, n, jfix + 1, best == thr))
print(f"       全部相等 ? {all(r[3] for r in lp_rows)}（{len(lp_rows)} 个组合）")
print()


# ---------------------------------------------------------------- [3] 反例
print("=" * 78)
print("[3] 窗口读法：[Σk 最大] 给不出回绕约束；[Σx 最大] 给得出（同一个数据）")
print("=" * 78)

# 数据：m = 4, m2 = 2，k 与 x 都用有理数
m_c, m2_c = 4, 2
k = [F(1), F(1), F(2), F(1)]
x = [F(31, 20), F(12, 5), F(5, 2), F(1)]     # 1.55, 2.4, 2.5, 1.0
K_tot = sum(k)
print(f"  m = {m_c}, m2 = {m2_c}, k = {[str(t) for t in k]}, K = {K_tot}, (m2/m)K = {F(m2_c, m_c) * K_tot}")
print(f"  x = {[str(t) for t in x]}")

# 结构性条件：x_i >= k_i、链 x_{i+1} < delta*x_i（含回绕 x_1 < delta*x_4）
print(f"  x_i >= k_i 全部成立 ? {all(a >= b for a, b in zip(x, k))}")
ivd = iv.log(3) / iv.log(2)                  # delta 的严格区间
ratios_ok = []
for i in range(m_c):
    r = iv.mpf(x[(i + 1) % m_c].numerator) / iv.mpf(x[(i + 1) % m_c].denominator) / \
        (iv.mpf(x[i].numerator) / iv.mpf(x[i].denominator))
    ratios_ok.append(bool(r < ivd))
print(f"  区间算术：x_{{i+1}}/x_i < delta 全部成立 ? {all(ratios_ok)}   （逐项 {ratios_ok}）")

# 四个窗口的 Σk 与 Σx（指标 1 基，窗口 = (j, j+1) 循环）
print("  窗口(长 2)      Σk      Σx")
win = {}
for j in range(m_c):
    i1, i2 = j, (j + 1) % m_c
    win[(i1, i2)] = (k[i1] + k[i2], x[i1] + x[i2])
    print(f"    ({i1 + 1},{i2 + 1})       {win[(i1, i2)][0]}      {win[(i1, i2)][1]}")
maxk = max(v[0] for v in win.values())
maxx = max(v[1] for v in win.values())
print(f"  Σk 最大 = {maxk}（(m2/m)K = {F(m2_c, m_c) * K_tot}，需 >= 才合鸽笼）")
print(f"  Σx 最大 = {maxx}")

# 读法一：取 Σk 最大的窗口放在位置 (m-m2+1, m) = (3, 4)，即窗口 (3,4)
w_k = (2, 3)                                  # 0 基 -> 位置 3,4（1 基）
order_k = [(w_k[0] - off) % m_c for off in range(m_c)]   # 循环移位，使 (3,4) 落在末尾
xk = [x[i] for i in order_k]
print("\n  读法一（Σk 最大，取窗口 (3,4)）：")
print(f"    重排后 x = {[str(t) for t in xk]}")
print(f"    Σk(窗) = {win[w_k][0]} >= (m2/m)K = {F(m2_c, m_c) * K_tot} ? {win[w_k][0] >= F(m2_c, m_c) * K_tot}")
print(f"    x_{{m-m2}} = x_2 = {xk[1]}  与  x_m = x_4 = {xk[3]}")
print(f"    论文那一步 x_{{m-m2}} <= x_m 成立 ? {xk[1] <= xk[3]}")
wrap_lhs = iv.mpf(xk[2].numerator) / iv.mpf(xk[2].denominator)
wrap_rhs = ivd * (iv.mpf(xk[3].numerator) / iv.mpf(xk[3].denominator))
print(f"    回绕约束 x_3 < delta*x_4 成立 ? {bool(wrap_lhs < wrap_rhs)}"
      f"   （x_3 = {xk[2]}，delta*x_4 = {mp.nstr(mpf(wrap_rhs.a), 20)}...）")

# 读法二：取 Σx 最大的窗口放在位置 (3,4)
w_x = (1, 2)                                  # 0 基 -> 位置 2,3
order_x = [(w_x[0] - off) % m_c for off in range(m_c)]
xx = [x[i] for i in order_x]
print("\n  读法二（Σx 最大，取窗口 (2,3) 平移到末尾）：")
print(f"    重排后 x = {[str(t) for t in xx]}")
print(f"    Σk(窗) = {win[w_x][0]} >= (m2/m)K = {F(m2_c, m_c) * K_tot} ? {win[w_x][0] >= F(m2_c, m_c) * K_tot}")
print(f"    Σx(窗) = {win[w_x][1]} = Σx 最大 ? {win[w_x][1] == maxx}")
print(f"    论文那一步 x_{{m-m2}} <= x_m 成立 ? {xx[1] <= xx[3]}   （{xx[1]} <= {xx[3]}）")
wrap_lhs2 = iv.mpf(xx[2].numerator) / iv.mpf(xx[2].denominator)
wrap_rhs2 = ivd * (iv.mpf(xx[3].numerator) / iv.mpf(xx[3].denominator))
print(f"    回绕约束 x_3 < delta*x_4 成立 ? {bool(wrap_lhs2 < wrap_rhs2)}"
      f"   （delta*x_4 = {mp.nstr(mpf(wrap_rhs2.a), 20)}...）")
print()


# ---------------------------------------------------------------- [4] 不等式
print("=" * 78)
print("[4] 收尾不等式：(t+1)^delta - t^delta >= delta > 1（等价于 2^{delta v}-1 >= (2^v-1)^delta）")
print("=" * 78)
print("  手证见报告（中值定理）。此处给区间算术证据（不是证明）：")
tests = [1, 2, 3, 10, 100, 10 ** 6, int(2 ** mpf(75.5946323945))]
bad = []
for t in tests:
    lhs = iv.power(iv.mpf(t + 1), ivd) - iv.power(iv.mpf(t), ivd)
    if not (lhs > 1):
        bad.append(t)
print(f"    t 取值 {tests}")
print(f"    全部 t 上 (t+1)^delta - t^delta > 1 ? {len(bad) == 0}（失败者：{bad}）")
# 与论文收尾对应：t = 2^v - 1，v 取链上真实值 75.5946323945 与 79.562387618086
for vv in ["75.5946323945", "79.562387618086"]:
    t = int(2 ** mpf(vv)) - 1
    l1 = iv.power(iv.mpf(2), ivd * iv.mpf(vv)) - 1
    r1 = iv.power(iv.power(iv.mpf(2), iv.mpf(vv)) - 1, ivd)
    print(f"    v = {vv}：2^(delta v)-1 >= (2^v-1)^delta ? {bool(l1 >= r1)}")
print()


# ---------------------------------------------------------------- [5] 前置条件
print("=" * 78)
print("[5] 定理 21 前置条件与 m2 = 92 的可行阈值")
print("=" * 78)
thr = {}
for m2v in [47, 67, 82, 91, 92]:
    thr[m2v] = c * (power(delta, m2v) - 1) / (delta - 1)
    print(f"  m2 = {m2v:>3}：前置条件要求 (m2/m)*K_lo >= {mp.nstr(thr[m2v], 20)}"
          f"  即 K_lo >= {mp.nstr(thr[m2v] * m2v / m2v, 20)}（m = m2 时）")
print(f"  说明：m2 = 92 在 m = 92 下可行的阈值 K_lo >= {mp.nstr(thr[92], 20)}")
print(f"        网格里 m2 = 92 首次成为最优的点在 3.1e20，而 3.0257e20 那格仍是 m2 = 91，")
print(f"        与上式的量级一致（{mp.nstr(thr[92], 6)} 落在 3.0257e20 与 3.1e20 之间 ? "
      f"{mpf('3.0257e20') < thr[92] <= mpf('3.1e20')}）")
print()


# ---------------------------------------------------------------- [6] m=92 算术
print("=" * 78)
print("[6] m = 92 一节的算术核对")
print("=" * 78)
U92 = mpf("1.4784") * 92 * power(delta, 92)
term92 = mpf(77692117359936589403)
mar92 = term92 / U92
print(f"  U(92) = 1.4784*92*delta^92 = {mp.nstr(U92, 25)}")
print(f"        margin-table.txt 现行第 92 行给 3.4302597024885020978e+20")
print(f"  链终值 = {mp.nstr(term92, 25)}（表给 77692117359936589403）")
print(f"  余量 = 终值/U(92) = {mp.nstr(mar92, 25)}（表给 0.226490482057595771625621）")
print(f"  余量的倒数 1/余量 = {mp.nstr(1 / mar92, 20)}")
print(f"       => 「m = 92 差 4.4 倍」的指代 = 1/余量 = {float(1 / mar92):.4f}")
print(f"  U(92)/U(91) = {mp.nstr(U92 / U91, 20)}（不是 4.4）")

# 网格点给的 Psi 值（项目自述，脚本 [5e0] 输出）与 U(92) 的比较
grid = [("7.5311e11", "5267319278509397.0", 47),
        ("1e15", "130441933147714940.0", 63),
        ("1e18", "4640282259296926456.0", 79),
        ("1e20", "205632218873398596256.0", 89),
        ("2.05632218873398596256e20", "205632218873398596256.0", 91),
        ("3.1e20", "205632218873398596256.0", 92),
        ("3.3e20", "7941964418702608664581.0", 92),
        ("3.4302597024885020978e20", "1.567829661853181873291e+22", 92)]
print("\n  网格点（项目自述）与 U(92) 的比较：")
prev = None
mono = True
for (Klo, psi, m2v) in grid:
    p = mpf(psi)
    if prev is not None and p < prev:
        mono = False
    prev = p
    print(f"    K_lo = {Klo:>28}  m2 = {m2v:>3}  Psi = {psi:>26}  "
          f"Psi <= U(92) ? {p <= U92}  Psi > U(92) ? {p > U92}")
print(f"  网格上 Psi 非降 ? {mono}（与脚本 [5e0] 打印的 True 一致）")
print(f"  注意：K_lo = 3.3e20 与 3.4302...e20 两行都给出 Psi > U(92)，")
print(f"        而 10^20 那一行给出 Psi = 2.0563...e20 < U(92)（单点真、全称假）")
print()
print("=" * 78)
print("脚本结束")
print("=" * 78)
