# dt2_ladder.py -- S4: 自举链（Hercher Thm 21 + Lemma 22）与前沿 M*
#
# 链条（全部为已发表的初等步骤；终点上界可选两种）：
#  起点:  SdW Lemma 10（初等）：q_n + q_{n+1} <= log(2)*X0/M  =>  对一切 m<=M 的 m 圈，K > q_n
#  自举:  Hercher Thm 21：给定 K 下界，取满足假设的最大 m2<=M，得偏差上界 eps
#  换算:  Hercher Lemma 22：区间 (δ, δ+eps) 内最小分母 -> 新的 K 下界（用上方逼近记录表）
#  终点:  (i) SdW/Rhin 一致上界 K < 1.4784*M*δ^M（91<=M；78<=M<=90 用 1.3993）
#         (ii) 初等 CF 上界 K_up（见 dt2_up.py，逐区间、需尾条件）
import mpmath as mp

mp.mp.dps = 150
LOG2 = mp.log(2)
delta = mp.log(3) / LOG2

def dpow(k):
    return mp.exp(k * mp.log(delta))

# 收敛项
P, Q = [], []
for line in open("dt2_q.txt"):
    i, pi, qi = map(int, line.split())
    while len(Q) <= i:
        Q.append(None); P.append(None)
    Q[i] = qi; P[i] = pi

# ---------- 上方逼近记录表（Stern-Brocot 右降；gap+(q) = (⌈qδ⌉-qδ)/q） ----------
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

UP = build_up(10 ** 300)

def q_min(eff):
    """min{q : gap+(q) < eff}（依赖 UP 在 1e300 内完整）；找不到返回 None"""
    for q, g in UP:
        if g < eff:
            return q
    return None

print("上方逼近记录数 = %d，最大 q = %s" % (len(UP), mp.nstr(UP[-1][0], 8)))
print("最后 3 个记录 (q, gap+):", [(q, mp.nstr(g, 4)) for q, g in UP[-3:]])

# ---------- Theorem 21 ----------
def m2_max(M, K, X0):
    c = mp.log((mp.mpf(162) / 97) * X0) / LOG2
    best = 0
    for m2 in range(1, M + 1):
        if (dpow(m2) - 1) / (delta - 1) * c <= (mp.mpf(m2) / M) * K:
            best = m2
    return best

def eps21(M, m2, K, X0, special=True):
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

def K_start_lemm10(M, X0):
    lim = LOG2 * mp.mpf(X0) / M
    best = None
    for n in range(1, len(Q) - 2):
        if Q[n] + Q[n + 1] <= lim:
            best = (n, Q[n])
    return best

def ladder(M, X0, K0, verbose=False, maxsteps=200):
    K = mp.mpf(K0); hist = []
    for step in range(maxsteps):
        m2 = m2_max(M, K, X0)
        if m2 == 0:
            return K, hist, "m2=0"
        ep, v = eps21(M, m2, K, X0)
        if verbose:
            print("      step %2d: K=%-12s m2=%-3d v=%-10s eps=%-12s"
                  % (step, mp.nstr(K, 6), m2, mp.nstr(v, 5), mp.nstr(ep, 4)))
        if m2 == M:      # 假设已可达 m2=M：下一步必然爆掉
            qn = q_min(ep)
            hist.append((step, K, m2, ep, qn))
            return (mp.mpf(qn) if qn else mp.mpf('1e300')), hist, "m2=M(发散)"
        qn = q_min(ep)
        hist.append((step, K, m2, ep, qn))
        if qn is None or qn <= K:
            return K, hist, "停(无改进)"
        K = mp.mpf(qn)
    return K, hist, "步数上限"

def K_up_rhin(M):
    c = mp.mpf('1.4784') if M >= 91 else mp.mpf('1.3993')
    return c * M * dpow(M)

print()
print("=" * 92)
print("自举链：初等起点（Lemma 10）+ Theorem 21；终点用 Rhin 型一致上界")
print("X0 = 695*2^60 = %s ；log2((162/97)X0) = %s"
      % (mp.nstr(mp.mpf(695) * 2 ** 60, 10),
         mp.nstr(mp.log(mp.mpf(162) / 97 * mp.mpf(695) * 2 ** 60) / LOG2, 8)))
print("\n   M | 起点 q_n          |  终点 K_low        | 1.4784*M*δ^M      | 余量      | 判定")
for X0, tag in [(mp.mpf(695) * mp.mpf(2) ** 60, "695*2^60"),
                (mp.mpf(2) ** 71, "2^71")]:
    print("\n  --- X0 = %s ---" % tag)
    for M in range(88, 100):
        n0, K0 = K_start_lemm10(M, X0)
        Kl, hist, why = ladder(M, X0, K0)
        up = K_up_rhin(M)
        ok = Kl > up
        print("  %3d | q_%-3d = %-12s | %-18s | %-18s | %s | %s"
              % (M, n0, mp.nstr(K0, 5), mp.nstr(Kl, 5), mp.nstr(up, 6),
                 mp.nstr(Kl / up, 3), "矛盾(排除)" if ok else "未排除(" + why + ")"))

print()
print("=" * 92)
print("同一链条改用「牢靠起点」7e11（Hercher 论文用的起点）作为对照（M=91,92）")
for M in (91, 92, 93):
    Kl, hist, why = ladder(M, mp.mpf(695) * mp.mpf(2) ** 60, mp.mpf('7e11'))
    up = K_up_rhin(M)
    print("  M=%d  终点 K_low=%-18s  上界=%-18s  判定=%s (%s)"
          % (M, mp.nstr(Kl, 6), mp.nstr(up, 6), "矛盾" if Kl > up else "未排除", why))

print()
print("=" * 92)
print("链条细节（M = 92, X0 = 695*2^60，逐显示）")
n0, K0 = K_start_lemm10(92, mp.mpf(695) * mp.mpf(2) ** 60)
print("  起点 q_%d = %d" % (n0, K0))
Kl, hist, why = ladder(92, mp.mpf(695) * mp.mpf(2) ** 60, K0, verbose=True)
print("  终点 = %s (%s)" % (mp.nstr(Kl, 8), why))
