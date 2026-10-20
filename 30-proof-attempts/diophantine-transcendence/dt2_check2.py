# dt2_check2.py -- (A) 记录表精度核查；(B) 「第一次 M* >= 92」的 X0 门槛（比 2^74 更精确）
import mpmath as mp

mp.mp.dps = 400
DELTA = mp.log(3) / mp.log(2)

def build_up(Qmax, dps):
    mp.mp.dps = dps
    d = DELTA
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

print("(A) 记录表在 dps=150 与 dps=400 下的比较（只列 q <= 1e45 的档）")
r150 = build_up(10 ** 45, 150)
r400 = build_up(10 ** 45, 400)
print("   记录数: dps150 = %d, dps400 = %d" % (len(r150), len(r400)))
bad = 0
for (q1, g1), (q2, g2) in zip(r150, r400):
    if q1 != q2 or abs(float(g1 / g2) - 1) > 1e-6:
        bad += 1
        if bad <= 5:
            print("   差异: q=%s  gap(150)=%s  gap(400)=%s" % (q1, mp.nstr(g1, 4), mp.nstr(g2, 4)))
print("   不一致条目数 = %d（比较 %d 条）" % (bad, min(len(r150), len(r400))))
print("   q <= 1e45 内最后一个记录: q=%s gap=%s" % (mp.nstr(r400[-1][0], 6), mp.nstr(r400[-1][1], 4)))

print("\n(B) 第一次使 M* >= 92 的 X0（对 X0 做二分，用 dt2_frontier 的同一算法）")
mp.mp.dps = 150
LOG2 = mp.log(2)
delta = DELTA
def dpow(k):
    return mp.exp(k * mp.log(delta))
Q = []
for line in open("dt2_q.txt"):
    i, pi, qi = map(int, line.split())
    while len(Q) <= i:
        Q.append(None)
    Q[i] = qi
UP = build_up(10 ** 200, 400)

def q_min(eff):
    for q, g in UP:
        if g < eff:
            return q
    return None

def best_step(M, K, X0):
    c = mp.log((mp.mpf(162) / 97) * X0) / LOG2
    beste = None; bestm = None
    for m2 in range(1, M + 1):
        v = (mp.mpf(m2) / M) * K * (delta - 1) / (dpow(m2) - 1)
        if v < c:
            continue
        t2 = 3 / (mp.mpf(2) ** v - 1); t3 = 3 * (m2 - 1) / (mp.mpf(2) ** v - 1) ** delta
        if m2 == M:
            br = t2 + t3
        elif m2 == M - 1:
            br = 3 / X0 + t2 + t3
        else:
            br = (97 * (M - m2) + 73) / (54 * X0) + t2 + t3
        e = br / (K * 3 * LOG2)
        if beste is None or e < beste:
            beste = e; bestm = m2
    return (bestm, beste) if beste is not None else None

def ladder(M, X0, K0, maxsteps=60):
    K = mp.mpf(K0)
    for st in range(maxsteps):
        bs = best_step(M, K, X0)
        if bs is None:
            return K
        m2, e = bs
        qn = q_min(e)
        if qn is None or mp.mpf(qn) <= K:
            return K
        K = mp.mpf(qn)
    return K

def start(M, X0):
    lim = LOG2 * mp.mpf(X0) / M
    best = None
    for n in range(1, len(Q) - 2):
        if Q[n] + Q[n + 1] <= lim:
            best = (n, Q[n])
    return best

def excluded92(X0):
    M = 92
    n0, K0 = start(M, X0)
    Kl = ladder(M, X0, K0)
    up = mp.mpf('1.4784') * M * dpow(M)
    return Kl > up

lo = mp.mpf(10) ** 21
hi = mp.mpf(10) ** 23
for _ in range(60):
    mid = (lo * hi) ** mp.mpf('0.5')
    if excluded92(mid):
        hi = mid
    else:
        lo = mid
print("   M* = 92 的最低 X0（二分 60 步，区间 [1e21,1e23]）: %s" % mp.nstr(hi, 8))
print("   与 2^74 = %s、2^73 = %s、10^22 = %s 对照" % (
    mp.nstr(mp.mpf(2) ** 74, 8), mp.nstr(mp.mpf(2) ** 73, 8), mp.nstr(mp.mpf(10) ** 22, 8)))
print("   log10(该值) = %s ；比 2^71 高 %s 个数量级"
      % (mp.nstr(mp.log10(hi), 6),
         mp.nstr(mp.log10(hi) - mp.log10(mp.mpf(2) ** 71), 4)))

print("\n(C) 两道墙的 eps/gap+（用于正文「4.3% 与 1.336」的口径）")
def best_eps(M, K, X0):
    c = mp.log((mp.mpf(162) / 97) * X0) / LOG2
    beste = None; bestm = None
    for m2 in range(1, M + 1):
        v = (mp.mpf(m2) / M) * K * (delta - 1) / (dpow(m2) - 1)
        if v < c:
            continue
        t2 = 3 / (mp.mpf(2) ** v - 1); t3 = 3 * (m2 - 1) / (mp.mpf(2) ** v - 1) ** delta
        if m2 == M:
            br = t2 + t3
        elif m2 == M - 1:
            br = 3 / X0 + t2 + t3
        else:
            br = (97 * (M - m2) + 73) / (54 * X0) + t2 + t3
        e = br / (K * 3 * LOG2)
        if beste is None or e < beste:
            beste = e; bestm = m2
    return bestm, beste

g41 = mp.mpf('6.32183e-41')      # gap+(q_41)，见 dt2_struct 与正文
m2a, ea = best_eps(92, mp.mpf('77692117359936589403'), mp.mpf(695) * mp.mpf(2) ** 60)
print("    第一道墙 X0=695*2^60, M=92, K=q_41: 最优 m2=%d eps=%s gap+=%s 比值=%s"
      % (m2a, mp.nstr(ea, 6), mp.nstr(g41, 6), mp.nstr(ea / g41, 6)))
g43 = mp.mpf('6.2446807e-43')    # gap+(q_43)
m2b, eb = best_eps(93, mp.mpf('205632218873398596256'), mp.mpf(2) ** 74)
print("    第二道墙 X0=2^74, M=93, K=q_43: 最优 m2=%d eps=%s gap+=%s 比值=%s"
      % (m2b, mp.nstr(eb, 6), mp.nstr(g43, 6), mp.nstr(eb / g43, 6)))
