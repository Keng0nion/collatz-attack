# dt2_frontier.py -- S5: 前沿 M*(X0) 与「距完整证明的数量级」
#
# 机制说明（本脚本的核心观察，验证见输出）：
#  自举每步把 K 跳到「上方逼近记录」的某个分母；只有在 eps < gap+(当前 K) 时才能前进，
#  而 eps ~ (97*(M-m2)+73)/(54*X0*3K*log2)，gap+(K) ~ 1/(c*K^2)，
#  于是存在停点 K <~ 70.9*X0/(97*(M-m2)+73)。前沿由「能否在停点前让 K >= 119.9*δ^M」决定。
import mpmath as mp

mp.mp.dps = 150
LOG2 = mp.log(2)
delta = mp.log(3) / LOG2

def dpow(k):
    return mp.exp(k * mp.log(delta))

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

UP = build_up(10 ** 400)

def q_min(eff):
    for q, g in UP:
        if g < eff:
            return q
    return None

def gap_of(K):
    """当前 K 处（K 是记录）的 gap+"""
    for q, g in UP:
        if q == K:
            return g
    return None

Q = []
for line in open("dt2_q.txt"):
    i, pi, qi = map(int, line.split())
    while len(Q) <= i:
        Q.append(None)
    Q[i] = qi

def K_start_lemm10(M, X0):
    lim = LOG2 * mp.mpf(X0) / M
    best = None
    for n in range(1, len(Q) - 2):
        if Q[n] + Q[n + 1] <= lim:
            best = (n, Q[n])
    return best

def m2_feasible(M, K, X0):
    c = mp.log((mp.mpf(162) / 97) * X0) / LOG2
    out = []
    for m2 in range(1, M + 1):
        v = (mp.mpf(m2) / M) * K * (delta - 1) / (dpow(m2) - 1)
        if v >= c:
            out.append((m2, v))
    return out

def eps_of(M, m2, K, X0, special=True):
    v = (mp.mpf(m2) / M) * K * (delta - 1) / (dpow(m2) - 1)
    t2 = 3 / (mp.mpf(2) ** v - 1)
    t3 = 3 * (m2 - 1) / (mp.mpf(2) ** v - 1) ** delta
    if special and m2 == M:
        br = t2 + t3
    elif special and m2 == M - 1:
        br = 3 / X0 + t2 + t3
    else:
        br = (97 * (M - m2) + 73) / (54 * X0) + t2 + t3
    return br / (K * 3 * LOG2), v

def best_step(M, K, X0):
    """在所有可行 m2 中取 eps 最小者"""
    cands = m2_feasible(M, K, X0)
    if not cands:
        return None
    beste = None; bestm = None
    for m2, v in cands:
        e, _ = eps_of(M, m2, K, X0)
        if beste is None or e < beste:
            beste = e; bestm = m2
    return bestm, beste

def ladder(M, X0, K0, trace=False, maxsteps=60):
    K = mp.mpf(K0); hist = []
    for st in range(maxsteps):
        bs = best_step(M, K, X0)
        if bs is None:
            return K, hist, "无可行 m2"
        m2, e = bs
        qn = q_min(e)
        if trace:
            g = gap_of(int(K)) if K == int(K) else None
            print("     step %2d K=%-14s m2=%-3d eps=%-13s gap(K)=%-13s q_min=%s"
                  % (st, mp.nstr(K, 6), m2, mp.nstr(e, 4),
                     mp.nstr(g, 4) if g else "-", mp.nstr(qn, 6) if qn else ">cap"))
        hist.append((st, K, m2, e, qn))
        # 修正（2026 年 10 月 20 日）：m2 = M 可达不等于发散，仍须按 q_min 迭代；
        # 旧版在此处提前返回，导致 X0 = 2^85 一档的 M* 被低估。
        if qn is None or mp.mpf(qn) <= K:
            return K, hist, ("m2=M 但无可增" if m2 == M else "停")
        K = mp.mpf(qn)
        if m2 == M and st + 1 < maxsteps:
            continue
    return K, hist, "步数上限"

def K_up_rhin(M):
    c = mp.mpf('1.4784') if M >= 91 else mp.mpf('1.3993')
    return c * M * dpow(M)

print("=" * 92)
print("M*(X0)：初等起点 + Hercher 自举 + Rhin 型一致终点上界 1.4784*M*δ^M")
print("\n   X0           2 的幂 |  M* |  M*+1 处停滞点 / 触发阈值        | 备注")
for X0, tag in [(mp.mpf(695) * mp.mpf(2) ** 60, "695*2^60"),
                (mp.mpf(2) ** 71, "2^71"),
                (mp.mpf(2) ** 73, "2^73"),
                (mp.mpf(2) ** 74, "2^74"),
                (mp.mpf(10) ** 22, "10^22"),
                (mp.mpf(2) ** 75, "2^75"),
                (mp.mpf(10) ** 23, "10^23"),
                (mp.mpf(10) ** 24, "10^24"),
                (mp.mpf(2) ** 80, "2^80"),
                (mp.mpf(2) ** 85, "2^85"),
                (mp.mpf(2) ** 90, "2^90"),
                (mp.mpf(2) ** 100, "2^100"),
                (mp.mpf(10) ** 30, "10^30"),
                (mp.mpf(10) ** 40, "10^40"),
                (mp.mpf(10) ** 60, "10^60")]:
    Mstar = None
    for M in range(85, 200):
        n0, K0 = K_start_lemm10(M, X0)
        Kl, hist, why = ladder(M, X0, K0)
        if Kl > K_up_rhin(M):
            Mstar = M
        else:
            print("  %-12s %6.1f | %3d | M=%d 停滞: K_low=%-12s 阈值(119.9δ^M)=%-12s 判定=%s"
                  % (tag, float(mp.log(X0) / LOG2), Mstar, M,
                     mp.nstr(Kl, 5), mp.nstr(mp.mpf('119.9') * dpow(M), 5), why))
            break

print()
print("=" * 92)
print("细节追踪：X0 = 695*2^60，M = 91 与 M = 92")
for M in (91, 92):
    n0, K0 = K_start_lemm10(M, mp.mpf(695) * mp.mpf(2) ** 60)
    print("  ---- M = %d，起点 q_%d = %d" % (M, n0, K0))
    Kl, hist, why = ladder(M, mp.mpf(695) * mp.mpf(2) ** 60, K0, trace=True)
    print("       终点 K_low = %s   (%s)；触发阈值 119.9*δ^M = %s；Rhin 上界 = %s"
          % (mp.nstr(Kl, 8), why, mp.nstr(mp.mpf('119.9') * dpow(M), 6),
             mp.nstr(K_up_rhin(M), 6)))
