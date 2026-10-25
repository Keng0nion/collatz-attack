# -*- coding: utf-8 -*-
"""路线 1（顶点引理的初等证明）本轮独立复核脚本。

运行：
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
      "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts/r1_selfcheck.py"

纪律：
  A. 先定义后计算：δ、S、P、P<、v 的定义按论文 Definition 15、Lemma 8、Lemma 20、
     Remark 7 与勘误第 1 至 2 页原文写出，再进入计算。
  B. 用已钉住的数字做锚点自检（见 [0]、[1] 两节）。
  C. 精确有理算术（Fraction）为主；mpmath 只用于真实的无理 δ。
  D. 不 import 任何项目脚本，全部独立实现。本脚本一切输出都是核对，不是证明。
"""
import random
from fractions import Fraction as F
from itertools import combinations
from mpmath import mp, mpf, log, power

mp.dps = 70
random.seed(20261025)
FAIL = []


def sec(t):
    print("\n==== " + t + " ====")


def chk(name, cond, extra=""):
    ok = bool(cond)
    if not ok:
        FAIL.append(name)
    print("   " + ("PASS" if ok else "FAIL") + " " + name + (("  " + extra) if extra else ""))
    return ok


def mf(x):
    """把 Fraction / int / str / mpf 统一成 mpf。"""
    if isinstance(x, F):
        return mpf(x.numerator) / x.denominator
    return mpf(x)


# ================= 定义（先定义后计算） =================
def delta():
    """Definition 15：δ = log 3 / log 2 > 1"""
    return log(3) / log(2)


def X0():
    """验证界，论文正文用 695·2^60"""
    return 695 * 2 ** 60


def c_premise():
    """Theorem 21 前置条件里的常数 c = log((162/97)·X0)/log 2"""
    return log(mpf(162) / 97 * X0()) / log(2)


def S(y):
    """S(y) := Σ_j 3/(2^{y_j} 减 1)（勘误第 1 页；底数恒为 2）"""
    return sum(3 / (power(2, mf(t)) - 1) for t in y)


def v_exact(W, D, n):
    """v := W·(δ 减 1)/(δ^{m2} 减 1)（Theorem 21 与勘误末段），精确有理版"""
    return W * (D - 1) / (D ** n - 1)


def v_mp(W, D, n):
    """同上，实数版"""
    return W * (D - 1) / (power(D, n) - 1)


def rows_of(n, D, W):
    """闭版 P 的约束行：列表 (coeffs, rhs)，含义 a·y <= rhs。共 2n 加 1 条。"""
    rows = []
    for j in range(n):
        a = [F(0)] * n
        a[j] = F(-1)
        rows.append((tuple(a), F(-1)))            # L_j：负 y_j <= 负 1
    for j in range(n):
        a = [F(0)] * n
        k = (j + 1) % n
        a[k] = a[k] + 1
        a[j] = a[j] - D
        rows.append((tuple(a), F(0)))             # G_j：y_{j+1} 减 D·y_j <= 0
    rows.append((tuple([F(-1)] * n), -W))         # 和约束：负 Σy <= 负 W
    return rows


def solve_exact(A, b, n):
    """精确高斯消元。返回唯一解元组；奇异返回 None；不相容返回 'inf'。"""
    M = [[A[i][j] for j in range(n)] + [b[i]] for i in range(n)]
    piv_col, r = [], 0
    for c in range(n):
        p = None
        for i in range(r, n):
            if M[i][c] != 0:
                p = i
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(n):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][k] - f * M[r][k] for k in range(n + 1)]
        piv_col.append(c)
        r += 1
        if r == n:
            break
    for i in range(r, n):
        if all(M[i][k] == 0 for k in range(n)) and M[i][n] != 0:
            return "inf"
    if len(piv_col) < n:
        return None
    x = [F(0)] * n
    for i, c in enumerate(piv_col):
        x[c] = M[i][n]
    return tuple(x)


def feasible(y, rows):
    for a, rhs in rows:
        if sum(a[j] * y[j] for j in range(len(y))) > rhs:
            return False
    return True


def enumerate_vertices(n, D, W):
    rows = rows_of(n, D, W)
    verts = set()
    for idx in combinations(range(len(rows)), n):
        A = [rows[i][0] for i in idx]
        b = [rows[i][1] for i in idx]
        sol = solve_exact(A, b, n)
        if sol is None or sol == "inf":
            continue
        if feasible(sol, rows):
            verts.add(sol)
    return verts, rows


def predicted(n, D, W):
    """预测的顶点族：v·(1, D, …, D^{n 减 1}) 的 n 个循环排列。"""
    v = v_exact(W, D, n)
    out = set()
    for s in range(n):
        out.add(tuple(v * D ** ((j - s) % n) for j in range(n)))
    return out, v


def slack_family(n, Dbound, W, u, t):
    """边界族：比值 r_t = D 的 负 (n 减 1)u 次幂，其余 n 减 1 个比值 = D 的 u 次幂。

    于是 Π r_j = 1，全部 r_j <= D；尺度 a 取最小可行值（贴着和约束或下界）。
    u = 1 且 t = n 时该点恰为顶点 v·(1, D, …, D^{n 减 1})，故本族含顶点且由其连续退化而来。
    """
    db = mf(Dbound)
    r = [power(db, mf(u)) for _ in range(n)]
    r[t % n] = power(db, -mf(n - 1) * mf(u))
    p = [mpf(1)] * n
    for j in range(1, n):
        p[j] = p[j - 1] * r[j - 1]
    a = max(1 / min(p), mf(W) / sum(p))
    return [a * x for x in p], a


def rand_feasible(n, Dbound, W, strict=True, spread=1.0, tries=400):
    """按比值参数化造随机可行点：r_j = y_{j+1}/y_j，要求 r_j <= Dbound 且 Π r_j = 1。"""
    db = float(Dbound)
    for _ in range(tries):
        g = [random.uniform(-1.0, 1.0) * spread for _ in range(n)]
        m = sum(g) / n
        g = [t - m for t in g]
        r = [pow(db, t) for t in g]
        if any(x > db * (1 + 1e-12) for x in r):
            continue
        if strict and r[-1] > db * (1 - 1e-9):
            continue
        p = [1.0] * n
        for j in range(1, n):
            p[j] = p[j - 1] * r[j - 1]
        amin = max(1.0 / min(p), float(W) / sum(p))
        a = amin * (1.0 + random.random() * 3.0)
        y = [a * x for x in p]
        if min(y) < 1.0 - 1e-12 or sum(y) < float(W) - 1e-9:
            continue
        return [mpf(x) for x in y]
    return None


# ================= [0] 锚点自检：定义层 =================
sec("[0] 锚点自检（定义层，已钉住数字）")
d = delta()
cval = c_premise()
print("   X0 = 695·2^60 = " + str(X0()))
print("   δ = log3/log2 = " + mp.nstr(d, 60))
print("   c = log((162/97)X0)/log2 = " + mp.nstr(cval, 25))
chk("c > 1（这是 v > 1 的来源）", cval > 1, "c = " + mp.nstr(cval, 20))
d_pin = "1.58496250072115618145373894394781650875981440769248106045575"
chk("δ 与钉住值 57 位小数一致（绝对差 < 1e-56）",
    abs(d - mpf(d_pin)) < mpf(10) ** -56,
    "绝对差 " + mp.nstr(abs(d - mpf(d_pin)), 5))

# ================= [1] 锚点自检：m = 91 的余量 =================
sec("[1] 锚点自检（m = 91 的定量行）")
U91 = mpf("1.4784") * 91 * power(d, 91)
K91 = mpf(7941964418702608664581)
print("   U(91) = 1.4784·91·δ^91 = " + mp.nstr(U91, 31))
chk("U(91) 的 25 位有效数字 = 214072842063828923281.3586（钉住值）",
    mp.nstr(U91, 25).replace(" ", "") == "214072842063828923281.3586",
    mp.nstr(U91, 25).replace(" ", ""))
ratio = K91 / U91
print("   K(91) 下界 / U(91) = " + mp.nstr(ratio, 25))
chk("余量前 25 位 = 37.09935525747164492758953（钉住值）",
    mp.nstr(ratio, 25).replace(" ", "") == "37.09935525747164492758953",
    mp.nstr(ratio, 26).replace(" ", ""))

# ================= [2] 顶点枚举（精确有理，D > 1 任意） =================
sec("[2] 闭版 P 的顶点集合：精确有理枚举（D 为有理替代，W 取使 v > 1）")
tot_cfg, bad, coord1 = 0, [], 0
for D in [F(3, 2), F(8, 5), F(111, 70)]:
    for n in range(1, 7):
        base = (D ** n - 1) / (D - 1)
        for k in [F(3, 2), F(4), F(10)]:
            W = k * base
            verts, rows = enumerate_vertices(n, D, W)
            pred, v = predicted(n, D, W)
            tot_cfg += 1
            if verts != pred:
                bad.append((str(D), n, str(k), len(verts), len(pred)))
            coord1 += sum(1 for y in verts if F(1) in y)
print("   配置数 = " + str(tot_cfg) + "；与预测族不等的配置数 = " + str(len(bad)))
chk("全部配置上顶点集合 = 预测的循环等比列族", len(bad) == 0, str(bad[:4]))
chk("无任何顶点的坐标等于 1（对应 Step 9）", coord1 == 0)
print("   v 的范围（本节点）：最小 " + str(min(v_exact(F(3, 2) * (F(3, 2) ** n - 1) / (F(3, 2) - 1), F(3, 2), n)
                                              for n in range(1, 7))) +
      "，最大 " + str(max(v_exact(F(10) * (F(111, 70) ** n - 1) / (F(111, 70) - 1), F(111, 70), n)
                            for n in range(1, 7))))

D, n, k = F(3, 2), 5, F(4)
W = k * (D ** n - 1) / (D - 1)
verts, rows = enumerate_vertices(n, D, W)
vals = [S(y) for y in verts]
chk("顶点族上 S 取同一值（S 关于坐标对称的核对）",
    max(vals) - min(vals) < mpf(10) ** -60, "跨度 " + mp.nstr(max(vals) - min(vals), 5))

# ================= [3] 假设 v > 1 的必要性 =================
sec("[3] 假设 v > 1 的必要性：v < 1 时预测族不是顶点集合")
D, n = F(3, 2), 2
W = F(3, 2)                                     # 小于 (D^n 减 1)/(D 减 1) = 5/2
verts, rows = enumerate_vertices(n, D, W)
pred, v = predicted(n, D, W)
print("   v = " + str(v) + "（小于 1；预测族里 y_1 = v，违反 y_1 >= 1）")
print("   实际顶点集合 = " + "；".join(str(y) for y in sorted(verts)))
print("   预测族 = " + "；".join(str(y) for y in sorted(pred)))
chk("预测族与顶点集合不相交（分类在 v < 1 时失效）", len(pred & verts) == 0)
vlist = sorted(verts, key=lambda y: -S(y))
print("   顶点上 S 值（降序）= " + "；".join(str(y) + "->" + mp.nstr(S(y), 10) for y in vlist))
chk("最大值取在含坐标 1 的顶点上", F(1) in vlist[0])
print("   注：S(v 型点) = " + mp.nstr(S(tuple(v * D ** ((j - 0) % n) for j in range(n))), 10) +
      "，本次未找到使断言反向失效的实例，故只主张「分类失效」，不主张「不等式失效」")

# ================= [4] Step 9 用的上界：max Σy 在 y_j = 1 时 =================
sec("[4] 固定 y_j = 1 时 Σy 的最大值（Step 9 那条上界）")
bad4, cnt4 = [], 0
for D in [F(3, 2), F(8, 5), F(111, 70)]:
    for n in range(2, 6):
        for j in range(n):
            allrows = rows_of(n, D, F(1)) + [([F(0)] * j + [F(1)] + [F(0)] * (n - j - 1), F(1))]
            best = None
            for sub in combinations(range(len(allrows)), n):
                A = [allrows[i][0] for i in sub]
                b = [allrows[i][1] for i in sub]
                sol = solve_exact(A, b, n)
                if sol is None or sol == "inf" or not feasible(sol, allrows):
                    continue
                s = sum(sol)
                if best is None or s > best:
                    best = s
            cnt4 += 1
            if best != (D ** n - 1) / (D - 1):
                bad4.append((str(D), n, j, str(best)))
print("   组合数 = " + str(cnt4) + "；不等于 (D^n 减 1)/(D 减 1) 的个数 = " + str(len(bad4)))
chk("固定任一坐标为 1 后 Σy 的最大值恒等于 (D^n 减 1)/(D 减 1)", len(bad4) == 0, str(bad4[:3]))

# ================= [5] 随机采样：S(y) <= S(顶点) =================
sec("[5] 随机可行点采样：S(y) 是否始终不超过 S(顶点)（核对，非证明）")
worst, tot, maxratio = [], 0, mpf(0)
for D in [F(3, 2), F(8, 5), F(111, 70)]:
    for n in range(2, 6):
        base = (D ** n - 1) / (D - 1)
        for k in [F(3, 2), F(4), F(10)]:
            W = k * base
            v = v_exact(W, D, n)
            Sv = S([v * D ** j for j in range(n)])
            for _ in range(120):
                y = rand_feasible(n, float(D), W, strict=True, spread=1.4)
                if y is None:
                    continue
                tot += 1
                Sy = S(y)
                maxratio = max(maxratio, Sy / Sv)
                if Sy > Sv + mpf(10) ** -40:
                    worst.append((str(D), n, str(k), mp.nstr(Sy, 12), mp.nstr(Sv, 12)))
            for t in range(n):
                for iu in range(1, 21):
                    y, a = slack_family(n, D, W, F(iu, 20), t)
                    if min(y) < 1 or sum(y) < mf(W) or not all(y[(j + 1) % n] <= mf(D) * y[j]
                                                               for j in range(n)):
                        continue
                    tot += 1
                    Sy = S(y)
                    maxratio = max(maxratio, Sy / Sv)
                    if Sy > Sv + mpf(10) ** -40:
                        worst.append((str(D), n, str(k), "族 " + mp.nstr(Sy, 12), mp.nstr(Sv, 12)))
print("   采样点数 = " + str(tot) + "；超过顶点值的点数 = " + str(len(worst)))
print("   采样最大值 / 顶点值 = " + mp.nstr(maxratio, 20))
chk("全部采样点满足 S(y) <= S(顶点)", len(worst) == 0, str(worst[:3]))

# ================= [6] 平均化不等式（Jensen 方向） =================
sec("[6] 循环平均点：ȳ 可行且 S(y) >= S(ȳ)（凸性方向核对）")
bad6, cnt6 = [], 0
for D in [F(3, 2), F(8, 5)]:
    for n in range(2, 5):
        W = F(4) * (D ** n - 1) / (D - 1)
        for _ in range(60):
            y = rand_feasible(n, float(D), W, strict=True, spread=1.2)
            if y is None:
                continue
            cnt6 += 1
            bar = [sum(y) / n] * n
            if not (min(bar) >= 1 and sum(bar) >= mf(W) and
                    all(bar[(j + 1) % n] <= mf(D) * bar[j] for j in range(n))):
                bad6.append(("ȳ 不可行", str(D), n))
                continue
            if S(y) + mpf(10) ** -40 < S(bar):
                bad6.append(("Jensen 方向反", str(D), n))
print("   样本数 = " + str(cnt6) + "；异常数 = " + str(len(bad6)))
chk("ȳ 可行且 S(y) >= S(ȳ)", len(bad6) == 0, str(bad6[:3]))

# ================= [7] Σk 读法的显式反例（精确整数比较） =================
sec("[7] 「this sum」按 Σk 读的反例：精确整数比较")
kvec = [F(1), F(1), F(2), F(1)]
xvec = [F(31, 20), F(12, 5), F(5, 2), F(1)]
m2, m = 2, 4
K = sum(kvec)
print("   m = 4, m2 = 2, k = " + str(kvec) + ", K = " + str(K) + ", (m2/m)K = " + str(F(m2, m) * K))
print("   x = " + str(xvec))
ksums = [sum(kvec[(s + t) % m] for t in range(m2)) for s in range(m)]
xsums = [sum(xvec[(s + t) % m] for t in range(m2)) for s in range(m)]
print("   四个窗口（起点 1 到 4）：Σk = " + str([str(t) for t in ksums]) + "；Σx = " + str([str(t) for t in xsums]))
chk("k_i <= x_i 全成立", all(kvec[i] <= xvec[i] for i in range(m)))
chk("Σk 最大 = 3，且门槛 (m2/m)K = 5/2 可达", max(ksums) == 3 and max(ksums) >= F(m2, m) * K)
chk("Σx 最大 = 49/10 且唯一位于窗口 (2,3)", max(xsums) == F(49, 10) and xsums.index(max(xsums)) == 1)
for nm, cc in [
    ("x2/x1 < δ 等价于 2^48 < 3^31", 2 ** 48 < 3 ** 31),
    ("x3/x2 < δ 等价于 2^25 < 3^24", 2 ** 25 < 3 ** 24),
    ("x4/x3 < δ 等价于 2^2 < 3^5", 2 ** 2 < 3 ** 5),
    ("x1/x4 < δ 等价于 2^31 < 3^20", 2 ** 31 < 3 ** 20),
    ("Σx 读法重排后回绕 24/25 < δ 等价于 2^24 < 3^25", 2 ** 24 < 3 ** 25),
]:
    chk(nm, cc)
y_sk = xvec[:]
chk("Σk 读法取窗口 (3,4) 后：x_{m 减 m2} <= x_m 失败（12/5 对 1）", not (y_sk[m - m2 - 1] <= y_sk[m - 1]))
chk("Σk 读法取窗口 (3,4) 后：回绕 x_{m 减 m2 + 1} < δ·x_m 失败（等价于 2^5 >= 3^2）", 2 ** 5 >= 3 ** 2)
y_sx = [xvec[3], xvec[0], xvec[1], xvec[2]]
chk("Σx 读法把窗口 (2,3) 平移到末尾后：x_{m 减 m2} <= x_m 成立", y_sx[m - m2 - 1] <= y_sx[m - 1])
chk("Σx 读法同上：回绕 x_{m 减 m2 + 1} < δ·x_m 成立（24/25 < δ）",
    mf(y_sx[m - m2]) < d * mf(y_sx[m - 1]))

# ================= [8] Step 8 线性代数：符号验证 =================
sec("[8] Step 8 的线性代数：δ 作符号变量的验证（n = 2 至 6）")
import sympy as sp
x = sp.symbols("x")
detbad, perpbad = [], []
for n in range(2, 7):
    C = sp.Matrix([[-x if i == j else (1 if j == (i + 1) % n else 0) for j in range(n)]
                   for i in range(n)])
    if sp.simplify(C.det() - (-1) ** n * (x ** n - 1)) != 0:
        detbad.append(n)
    for j0 in range(n):
        keep = [i for i in range(n) if i != j0]
        sub = C[keep, :]
        if sub.rank() != n - 1:
            perpbad.append((n, j0, "链约束子阵秩"))
        w = sp.Matrix([x ** ((t - j0 - 1) % n) for t in range(n)])
        for i in keep:
            if sp.simplify((C[i, :] * w)[0]) != 0:
                perpbad.append((n, j0, "w 不正交于保留行"))
        if sp.simplify(-sum(w)) == 0:
            perpbad.append((n, j0, "和行与 w 内积为 0"))
print("   行列式恒等式失败的 n = " + str(detbad))
chk("δ 符号下 det(G_1 至 G_n) = (负 1)^n·(δ^n 减 1)", len(detbad) == 0)
chk("删去任一条链约束后：子阵秩 n 减 1，垂直向量 w 只差和行一条", len(perpbad) == 0, str(perpbad[:3]))

# ================= [9] 真实 δ 下的实例（m = 91, m2 = 47） =================
sec("[9] 真实 δ 下的实例：m2 = 47, m = 91, K_lo = 7.5311e11")
W9 = mpf(47) / 91 * mpf("7.5311") * mpf(10) ** 11
v9 = v_mp(W9, d, 47)
y9 = [v9 * power(d, j) for j in range(47)]
Sv9 = S(y9)
bound9 = 3 / (power(2, v9) - 1) + 3 * 46 / power(power(2, v9) - 1, d)
print("   W = (47/91)·K_lo = " + mp.nstr(W9, 20))
print("   v = W·(δ 减 1)/(δ^47 减 1) = " + mp.nstr(v9, 20))
print("   S(v, δv, …, δ^46 v) = " + mp.nstr(Sv9, 20))
print("   收尾上界 3/(2^v 减 1) + 3·46/(2^v 减 1)^δ = " + mp.nstr(bound9, 20))
chk("v > 1（Step 9 前提）", v9 > 1)
chk("S(顶点) <= 收尾上界（Step 11）", Sv9 <= bound9)
chk("2^(δv) 减 1 > (2^v 减 1)^δ（Step 4b(ii) 在真实 v 上）",
    power(2, d * v9) - 1 > power(power(2, v9) - 1, d))
worst9, cnt9, maxr9 = 0, 0, mpf(0)
for t in range(47):
    for iu in range(1, 41):
        u = mpf(iu) / 40
        y, a = slack_family(47, d, W9, u, t)
        if min(y) < 1 or sum(y) < W9 or not all(y[(j + 1) % 47] <= d * y[j] for j in range(47)):
            continue
        cnt9 += 1
        Sy = S(y)
        maxr9 = max(maxr9, Sy / Sv9)
        if Sy > Sv9 + Sv9 * mpf(10) ** -30:
            worst9 += 1
    if t == 46:
        yv, av = slack_family(47, d, W9, mpf(1), 46)
        chk("边界族在 u = 1、t = 47 处恰还原顶点（生成器的自洽核对）",
            max(abs(yv[j] - y9[j]) for j in range(47)) < Sv9 * mpf(10) ** -20,
            "a = " + mp.nstr(av, 20) + "；v = " + mp.nstr(v9, 20))
print("   边界族采样点数 = " + str(cnt9) + "；超过顶点值的点数 = " + str(worst9))
print("   采样最大值 / 顶点值 = " + mp.nstr(maxr9, 20))
chk("真实 δ 与 m2 = 47 下边界族采样不超顶点值", worst9 == 0)
for u in [mpf(1), mpf(39) / 40, mpf(19) / 20, mpf(1) / 2]:
    y, a = slack_family(47, d, W9, u, 46)
    print("   u = " + mp.nstr(u, 6) + "：a = " + mp.nstr(a, 12) + "，S = " + mp.nstr(S(y), 12))

# ================= [10] Step 4b 与一阶、二阶导 =================
sec("[10] Step 4b 与导数核对")
tl = []
for t in [mpf(1), mpf(2), mpf("2.5"), mpf(10), v9 - 1, power(2, v9) - 1]:
    if t >= 1:
        tl.append(mp.nstr(power(t + 1, d) - power(t, d), 8) + (">1" if power(t + 1, d) - power(t, d) > 1 else "<=1"))
print("   (t+1)^δ 减 t^δ 在 t 取 " + str(len(tl)) + " 个值上 = " + "；".join(tl))
chk("(t+1)^δ 减 t^δ > 1 在全部取样 t >= 1 上成立", all(">1" == s.split(">")[-1] or s.endswith(">1") for s in tl))
h = mpf(10) ** -25
f1 = lambda t: 3 / (power(2, t) - 1)
d2a = 3 * power(2, mpf(3)) * (power(2, mpf(3)) + 1) * log(2) ** 2 / (power(2, mpf(3)) - 1) ** 3
d2n = (f1(mpf(3) + h) - 2 * f1(mpf(3)) + f1(mpf(3) - h)) / h ** 2
chk("f'' 的解析式与差分一致（相对差 < 1e-20）", abs(d2n - d2a) / d2a < mpf(10) ** -20,
    "解析 " + mp.nstr(d2a, 15) + "；差分 " + mp.nstr(d2n, 15))
chk("f 在 t = 3 处一阶导为负", (f1(mpf(3) + h) - f1(mpf(3) - h)) / (2 * h) < 0)

# ================= [11] 汇总 =================
print("\n==== 汇总 ====")
print("   失败项数 = " + str(len(FAIL)))
for f in FAIL:
    print("   FAIL: " + f)
print("   全部通过 ? " + str(len(FAIL) == 0))
