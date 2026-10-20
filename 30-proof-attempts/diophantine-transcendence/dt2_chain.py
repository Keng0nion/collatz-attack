# dt2_chain.py -- S3: 主计算
#  (A) 复算 SdW v1.43 Lemma 14 的 K_1(m) 表（8 档）与极限常数 -> 验证 Lemma 7/12 实现
#  (B) 复算 Hercher 2023 Theorem 23 的 7 步自举（m <= 91，X0 = 695*2^60）
#  (C) 用初等起点（SdW Lemma 10）重跑自举，对目标 M 给出终点下界
#  (D) 与两种终点上界对照
# 记号：δ = log2(3)；Φ_m(K) = m c_m 2^{-(δ-1)K/(δ^m-1)}（SdW Lemma 7）
import mpmath as mp

mp.mp.dps = 120
log2 = mp.log(2)
ln3 = mp.log(3)
delta = ln3 / log2
LOG2 = mp.log(2)

# 工作精度下的 δ^k 与部分量
def dpow(k):
    return mp.exp(k * mp.log(delta))


def load_cf():
    q, p = [], []
    for line in open("dt2_q.txt"):
        i, pi, qi = map(int, line.split())
        while len(q) <= i:
            q.append(None); p.append(None)
        q[i] = qi; p[i] = pi
    return p, q


P, Q = load_cf()


def c_m(m, X0):
    X0 = mp.mpf(X0)
    b = (1 + 1 / X0) ** (1 / delta) / mp.mpf(2) ** (1 / delta)
    E = mp.mpf(0); dk = mp.mpf(1)
    for i in range(1, m):
        dk *= delta
        E += (m - i) * dk
    expo = (delta - 1) / (dpow(m) - 1)
    return (1 + 1 / X0) ** (m * expo) * b ** (E * expo), b


def Phi(m, K, X0, cm=None):
    if cm is None:
        cm, _ = c_m(m, X0)
    return m * cm * mp.mpf(2) ** (-(delta - 1) * mp.mpf(K) / (dpow(m) - 1))


def K1(m, X0, cm=None):
    if cm is None:
        cm, _ = c_m(m, X0)
    def f(x):
        x = mp.mpf(x)
        return (-13.3 * (0.46057 + mp.log(x))) - mp.log(m * cm) \
               + (delta - 1) * x * LOG2 / (dpow(m) - 1)
    lo = 13.3 * (dpow(m) - 1) / ((delta - 1) * LOG2) * mp.mpf('1.0000001')
    hi = lo
    while f(hi) < 0:
        hi *= 2
    a, b = lo, hi
    for _ in range(400):
        mid = (a + b) / 2
        if f(mid) > 0:
            b = mid
        else:
            a = mid
    return (a + b) / 2


print("=" * 78)
print("(A) 复算 SdW v1.43 Lemma 14 的 K_1(m) 表")
X0_sdw = mp.mpf('3.7469e18')
tab = {2: '3.0877e2', 10: '3.5858e4', 63: '4.8181e15', 64: '7.7350e15',
       100: '1.7876e23', 511: '1.3035e106', 512: '2.0698e106', 1000: '1.6144e204'}
nbad = 0
for m, v in tab.items():
    cm, _ = c_m(m, X0_sdw)
    k1 = K1(m, X0_sdw, cm)
    rel = float(k1 / mp.mpf(v)) - 1
    ok = abs(rel) < 5e-4
    nbad += (0 if ok else 1)
    print("  m=%4d  K_1(m)=%s   文献 %-12s 相对差 %8.2e  %s"
          % (m, mp.nstr(k1, 6), v, rel, "OK" if ok else "MISMATCH"))
print("  8 档不一致数 =", nbad)
cm30, b30 = c_m(30, X0_sdw)
print("  c_30 = %s（文献 < 0.30577）；b = %s（文献 0.64576）；"
      "k_1 极限 = %s（文献 15.107）；c_m 极限 = %s（文献 0.30576）"
      % (mp.nstr(cm30, 8), mp.nstr(b30, 6),
         mp.nstr(13.3 * mp.log(delta) / (LOG2 * (delta - 1)), 8),
         mp.nstr(mp.mpf(2) ** (-1 / (delta - 1)), 8)))

# ---------- Stern-Brocot 上方逼近记录 ----------
_UP = None
def up_records(Qmax):
    global _UP
    if _UP is not None and _UP[-1][0] >= Qmax:
        return _UP
    mp.mp.dps = 400
    dhi = mp.log(3) / mp.log(2)
    mp.mp.dps = 120
    rec = []; best = None
    lo_n, lo_d, hi_n, hi_d = 0, 1, 1, 0
    steps = 0
    while steps < 20000:
        mn, md = lo_n + hi_n, lo_d + hi_d
        if md > Qmax:
            break
        steps += 1
        val = mp.mpf(mn) / md
        if val > dhi:
            hi_n, hi_d = mn, md
            g = (mp.mpf(mn) - md * dhi) / md
            if best is None or g < best:
                best = g
                rec.append((md, g))
        else:
            lo_n, lo_d = mn, md
    _UP = rec
    return rec


def q_min_upto(eff, Qmax):
    """min{q <= Qmax : gap+(q) < eff}，依赖记录表在 Qmax 内完整；找不到返回 None"""
    for q, g in up_records(Qmax):
        if g < eff:
            return q
    return None


print()
print("=" * 78)
print("(B) 复算 Hercher Theorem 23 的 7 步自举（m <= 91，X0 = 695*2^60）")
X0h = mp.mpf(695) * mp.mpf(2) ** 60
print("  X0 = 695*2^60 = %s ；log2((162/97)X0) = %s"
      % (mp.nstr(X0h, 10), mp.nstr(mp.log((mp.mpf(162) / 97) * X0h) / LOG2, 8)))

T21C = None
def m2_max(M, K, X0):
    global T21C
    if T21C is None:
        T21C = (delta, mp.log((mp.mpf(162) / 97) * X0) / LOG2)
    best = 0
    for m2 in range(1, M + 1):
        lhs = (dpow(m2) - 1) / (delta - 1) * T21C[1]
        if lhs <= (mp.mpf(m2) / M) * K:
            best = m2
    return best


def eps21(M, m2, K, X0, special=True):
    """Theorem 21 偏差上界: 一般式，或 m2=M-1 / m2=M 的特例式"""
    v = (mp.mpf(m2) / M) * K * (delta - 1) / (dpow(m2) - 1)
    if special and m2 == M:
        br = 3 / (mp.mpf(2) ** v - 1) + 3 * (m2 - 1) / (mp.mpf(2) ** v - 1) ** delta
    elif special and m2 == M - 1:
        br = 3 / X0 + 3 / (mp.mpf(2) ** v - 1) + 3 * (m2 - 1) / (mp.mpf(2) ** v - 1) ** delta
    else:
        br = (97 * (M - m2) + 73) / (54 * X0) + 3 / (mp.mpf(2) ** v - 1) \
             + 3 * (m2 - 1) / (mp.mpf(2) ** v - 1) ** delta
    return br / (K * 3 * LOG2), v


print("\n  步 |    输入 K      | m2 |        eps        |      新 K 下界      |  论文印出")
paper_K = ['5.2e15', '3.97e17', '4.64e18', '2.74e19', '7.76e19', '2.05e20', '7.94e21']
paper_eps = ['6.9e-32', '5.1e-36', '4.1e-38', '2.3e-39', '2.3e-40', '5.3e-41', '1.11e-43']
K = mp.mpf('7e11')
M = 91
for i in range(8):
    m2 = m2_max(M, K, X0h)
    ep, v = eps21(M, m2, K, X0h)
    qn = q_min_upto(ep, 10 ** 40)
    tag = mp.nstr(qn, 6) if qn else ">1e40"
    print("  %2d | %12s | %2d | %14s | %18s | %s" % (i + 1, mp.nstr(K, 4), m2,
          mp.nstr(ep, 5), tag, paper_K[i] + " / " + paper_eps[i] if i < 7 else ""))
    if qn is None or K > 10 ** 40:
        break
    K = mp.mpf(qn)

# ---------- (C) 已移出 ----------
# 说明：本文件早期版本在这里放了一份「初等起点 + 自举求前沿」的实现，但它与
# dt2_ladder.py / dt2_frontier.py 里的实现不一致（对 M <= 91 误报「未达」）。
# 前沿计算以 dt2_ladder.py（用 7e11 起点复现论文七步，并在 M=91 处给出发散）
# 与 dt2_frontier.py（八档 X0 的 M* 表）为准；本文件只保留 (A)(B) 两节。
print()
print("=" * 78)
print("(C) 见 dt2_ladder.py 与 dt2_frontier.py（本文件不再重复前沿计算）")
