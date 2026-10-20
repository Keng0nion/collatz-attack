# dt2_soundtail.py -- 「几何尾部不可用」时的自举链（第三方 Lean 项目的健全变体）
#
# 背景：Hercher Theorem 21 的尾部项 3(m2-1)/(2^v-1)^delta 来自 2026 勘误的凸性论证；
# 第三方 Lean 项目（PhilNorfleet/Hercher2023_lean）不采信该步，改用平凡界 T(n_i) < 3/X0，
# 于是 eps 的尾巴变成 3(m2-1)/X0。本脚本在同一台机具（同一个起点、同一个 Lemma 22 换算、
# 同一个 SdW 终点上界）下重算前沿，验证「上限从 91 掉到 82」这一说法。
import mpmath as mp

mp.mp.dps = 150
LOG2 = mp.log(2)
delta = mp.log(3) / LOG2

def dpow(k):
    return mp.exp(k * mp.log(delta))

Q = []
for line in open("dt2_q.txt"):
    i, pi, qi = map(int, line.split())
    while len(Q) <= i:
        Q.append(None)
    Q[i] = qi

def build_up(Qmax):
    mp.mp.dps = 400
    d = mp.log(3) / mp.log(2)
    mp.mp.dps = 150
    rec = []; best = None
    lo_n, lo_d, hi_n, hi_d = 0, 1, 1, 0
    while True:
        mn, md = lo_n + hi_n, lo_d + hi_d
        if md > Qmax:
            break
        if mp.mpf(mn) / md > d:
            hi_n, hi_d = mn, md
            g = (mp.mpf(mn) - md * d) / md
            if best is None or g < best:
                best = g; rec.append((md, g))
        else:
            lo_n, lo_d = mn, md
    return rec

UP = build_up(10 ** 200)

def q_min(eff):
    for q, g in UP:
        if g < eff:
            return q
    return None

def feas(M, K, X0):
    c = mp.log((mp.mpf(162) / 97) * X0) / LOG2
    out = []
    for m2 in range(1, M + 1):
        v = (mp.mpf(m2) / M) * K * (delta - 1) / (dpow(m2) - 1)
        if v >= c:
            out.append((m2, v))
    return out

def eps_geo(M, m2, K, X0):
    """2026 勘误后的几何尾部（与 dt2_ladder.py 一致，含论文的两个特例式）"""
    v = (mp.mpf(m2) / M) * K * (delta - 1) / (dpow(m2) - 1)
    t2 = 3 / (mp.mpf(2) ** v - 1)
    t3 = 3 * (m2 - 1) / (mp.mpf(2) ** v - 1) ** delta
    if m2 == M:
        br = t2 + t3
    elif m2 == M - 1:
        br = 3 / X0 + t2 + t3
    else:
        br = (97 * (M - m2) + 73) / (54 * X0) + t2 + t3
    return br / (K * 3 * LOG2)

def eps_geo_general(M, m2, K, X0):
    """同上，但一律用一般式（不用特例式），用于分离「特例式是否关键」"""
    v = (mp.mpf(m2) / M) * K * (delta - 1) / (dpow(m2) - 1)
    br = (97 * (M - m2) + 73) / (54 * X0) + 3 / (mp.mpf(2) ** v - 1) \
         + 3 * (m2 - 1) / (mp.mpf(2) ** v - 1) ** delta
    return br / (K * 3 * LOG2)

def eps_sound(M, m2, K, X0):
    """第三方「健全」尾部（含特例式）：其他窗口极小值只用平凡界 3/X0"""
    v = (mp.mpf(m2) / M) * K * (delta - 1) / (dpow(m2) - 1)
    t2 = 3 / (mp.mpf(2) ** v - 1)
    if m2 == M:
        br = t2 + 3 * (m2 - 1) / X0
    elif m2 == M - 1:
        br = 3 / X0 + t2 + 3 * (m2 - 1) / X0
    else:
        br = (97 * (M - m2) + 73) / (54 * X0) + t2 + 3 * (m2 - 1) / X0
    return br / (K * 3 * LOG2)

def eps_sound_general(M, m2, K, X0):
    """第三方「健全」尾部的一般式（不含特例式）——反驳者的口径"""
    v = (mp.mpf(m2) / M) * K * (delta - 1) / (dpow(m2) - 1)
    br = (97 * (M - m2) + 73) / (54 * X0) + 3 / (mp.mpf(2) ** v - 1) + 3 * (m2 - 1) / X0
    return br / (K * 3 * LOG2)

def ladder(M, X0, K0, epsf, maxsteps=80):
    K = mp.mpf(K0)
    for st in range(maxsteps):
        F = feas(M, K, X0)
        if not F:
            return K, "无可行 m2"
        m2 = min(F, key=lambda t: epsf(M, t[0], K, X0))[0]
        e = epsf(M, m2, K, X0)
        qn = q_min(e)
        if qn is None or mp.mpf(qn) <= K:
            return K, "停"
        K = mp.mpf(qn)
    return K, "步数上限"

def start(M, X0):
    lim = LOG2 * mp.mpf(X0) / M
    best = None
    for n in range(1, len(Q) - 2):
        if Q[n] + Q[n + 1] <= lim:
            best = (n, Q[n])
    return best

print("=" * 92)
print("同一台机具、四种尾部处理下的前沿（X0 = 695*2^60）")
print("  列：几何尾部+特例式（Hercher 发表形态）/ 几何尾部一般式 / 健全尾部+特例式 / 健全尾部一般式（反驳者口径）")
print("\n   M | 几何+特例        | 几何一般式       | 健全+特例        | 健全一般式（反驳者）")
res = {}
for M in range(78, 96):
    X0 = mp.mpf(695) * mp.mpf(2) ** 60
    n0, K0 = start(M, X0)
    up = (mp.mpf('1.4784') if M >= 91 else mp.mpf('1.3993')) * M * dpow(M)
    out = []
    for f in (eps_geo, eps_geo_general, eps_sound, eps_sound_general):
        Kl, why = ladder(M, X0, K0, f)
        out.append((Kl, why, Kl > up))
    res[M] = out
    print("  %3d | %-13s %-6s | %-13s %-6s | %-13s %-6s | %-13s %-6s"
          % (M, mp.nstr(out[0][0], 6), "排除" if out[0][2] else "未排除",
             mp.nstr(out[1][0], 6), "排除" if out[1][2] else "未排除",
             mp.nstr(out[2][0], 6), "排除" if out[2][2] else "未排除",
             mp.nstr(out[3][0], 6), "排除" if out[3][2] else "未排除"))
for i, nm in enumerate(("几何+特例式", "几何一般式", "健全+特例式", "健全一般式（反驳者）")):
    mx = max(M for M in res if res[M][i][2])
    print("  最大被排除的 M（%s）= %d" % (nm, mx))

print()
print("X0 = 2^71（Barina 档位）下的同一对照（几何+特例式 与 健全+特例式）：")
for M in range(80, 96):
    X0 = mp.mpf(2) ** 71
    n0, K0 = start(M, X0)
    up = (mp.mpf('1.4784') if M >= 91 else mp.mpf('1.3993')) * M * dpow(M)
    Kg, wg = ladder(M, X0, K0, eps_geo)
    Ks, ws = ladder(M, X0, K0, eps_sound)
    print("  %3d | 几何 K_low=%-14s %-8s | 健全 K_low=%-14s %-8s"
          % (M, mp.nstr(Kg, 6), "排除" if Kg > up else "未排除",
             mp.nstr(Ks, 6), "排除" if Ks > up else "未排除"))

print()
print("健全尾部口径下的前沿 M*（用于说明「前沿律斜率约 5/十年」在两个口径下都成立）：")
for X0, tag in [(mp.mpf(2) ** 71, "2^71"), (mp.mpf(2) ** 80, "2^80"), (mp.mpf(2) ** 90, "2^90"),
                (mp.mpf(2) ** 100, "2^100"), (mp.mpf(10) ** 40, "10^40")]:
    Mstar = None
    for M in range(78, 220):
        n0, K0 = start(M, X0)
        Kl, _ = ladder(M, X0, K0, eps_sound)
        up = (mp.mpf('1.4784') if M >= 91 else mp.mpf('1.3993')) * M * dpow(M)
        if Kl > up:
            Mstar = M
        else:
            break
    print("  %-6s log10 X0 = %-8s M* = %s" % (tag, mp.nstr(mp.log10(X0), 6), Mstar))
