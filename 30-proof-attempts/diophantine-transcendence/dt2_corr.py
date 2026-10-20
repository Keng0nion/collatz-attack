# dt2_corr.py -- 对 2026 勘误（Theorem 21 尾部替代推导）的数值核查
#
# 勘误论点（原文抄录后逐条对应）：
#   设 x_i = log2(n_i + 1)（i 遍历 m2 个连续局部极小值），W := (m2/m)K。
#   约束：x_i >= 1；x_{i+1} <= δ x_i；x_1 <= δ x_{m2}（循环选取）；Σ x_i >= W。
#   目标：S(x) = Σ_i 3/(2^{x_i} - 1)（由 T(n_i) < 3/n_i = 3/(2^{x_i}-1)）。
#   结论：S 在可行多面体上的最大值 <= S(v, δv, ..., δv) = 3/(2^v-1) + 3(m2-1)/(2^{δv}-1)，
#         v = W(δ-1)/(δ^{m2}-1)。
# 核查：(1) 凸性；(2)「某个 x_i = 1 时 Σx 不达 W」；(3) 顶点枚举（S 为凸函数，最大值在顶点）。
import mpmath as mp
from itertools import combinations

mp.mp.dps = 60
delta = mp.log(3) / mp.log(2)

f = lambda x: 3 / (mp.mpf(2) ** mp.mpf(x) - 1)
S = lambda xs: sum(f(x) for x in xs)

print("(1) 凸性：f(x) = 3/(2^x - 1) 的二阶差分为正（应为正）")
for x in (1, 2, 5, 20, 50, 100):
    h = mp.mpf('0.01')
    print("    x=%-5s  f''≈ %s" % (x, mp.nstr((f(x + h) - 2 * f(x) + f(x - h)) / h ** 2, 6)))

print("\n(2)「某个 x_i = 1」时 Σx 的上界（几何级数 (δ^{m2}-1)/(δ-1)）vs W")
for m2, m, K in ((8, 92, mp.mpf('3.0e20')), (60, 92, mp.mpf('3.0e20'))):
    W = (mp.mpf(m2) / m) * K
    cap = (delta ** m2 - 1) / (delta - 1)
    print("    m2=%2d: W = %-10s ；上界 = %-12s ；W 更大？ %s"
          % (m2, mp.nstr(W, 4), mp.nstr(cap, 6), W > cap))

print("\n(3) 顶点枚举：S 为凸函数，逐坐标递减，故最大值在顶点；逐顶点算 S 并与勘误界比")
def vertices(m2, W):
    """约束（全部写成 A x <= b 或 = 形式）：
       C_i: x_i >= 1        (i=1..m2)
       G_i: x_{i+1} - δ x_i <= 0 (i=1..m2-1)
       G_0: x_1 - δ x_{m2} <= 0
       Wc:  Σ x_i >= W
       顶点：取 m2 个独立约束为等式。"""
    cons = []
    for i in range(m2):                       # C_i: x_i = 1
        A = [mp.mpf(0)] * m2; A[i] = mp.mpf(1); cons.append((A, mp.mpf(1), "C%d" % (i + 1)))
    for i in range(m2 - 1):                   # G_i: x_{i+1} = δ x_i
        A = [mp.mpf(0)] * m2; A[i + 1] = mp.mpf(1); A[i] = -delta
        cons.append((A, mp.mpf(0), "G%d" % (i + 1)))
    A = [mp.mpf(0)] * m2; A[0] = mp.mpf(1); A[-1] = -delta
    cons.append((A, mp.mpf(0), "G0"))         # G_0: x_1 = δ x_{m2}
    A = [mp.mpf(1)] * m2
    cons.append((A, W, "W"))                  # 和约束 Σx = W
    for idx in combinations(range(len(cons)), m2):
        M = mp.matrix([cons[i][0] for i in idx])
        b = mp.matrix([cons[i][1] for i in idx])
        try:
            sol = mp.lu_solve(M, b)
        except Exception:
            continue
        if sol is None:
            continue
        try:
            x = [sol[i, 0] for i in range(m2)]
        except Exception:
            try:
                x = list(sol)
            except Exception:
                continue
        if any(v != v for v in x):          # NaN 检查
            continue
        ok = True
        for i in range(m2):
            if x[i] < 1 - mp.mpf('1e-30'):
                ok = False; break
        if ok:
            for i in range(m2 - 1):
                if x[i + 1] > delta * x[i] + mp.mpf('1e-25') * abs(x[i]):
                    ok = False; break
        if ok and x[0] > delta * x[-1] + mp.mpf('1e-25') * abs(x[-1]):
            ok = False
        if ok and sum(x) < W - mp.mpf('1e-25') * abs(W):
            ok = False
        if ok:
            yield [x[i] for i in range(m2)], [cons[i][2] for i in idx]

for m2, m, K in ((3, 91, mp.mpf('1e19')), (4, 91, mp.mpf('1e20')),
                 (5, 92, mp.mpf('3e20')), (6, 90, mp.mpf('1e20'))):
    W = (mp.mpf(m2) / m) * K
    v = W * (delta - 1) / (delta ** m2 - 1)
    bound = 3 / (mp.mpf(2) ** v - 1) + 3 * (m2 - 1) / (mp.mpf(2) ** (delta * v) - 1)
    best = mp.mpf(0); bestact = None; cnt = 0
    for xs, act in vertices(m2, W):
        cnt += 1
        val = S(xs)
        if val > best:
            best = val; bestact = act
    print("    m2=%d: 可行顶点 %3d ；最大 S = %-12s ；勘误界 = %-12s ；比值 = %s ；活跃约束 %s"
          % (m2, cnt, mp.nstr(best, 6), mp.nstr(bound, 6),
             mp.nstr(best / bound, 6), bestact))
