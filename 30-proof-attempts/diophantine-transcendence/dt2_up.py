# dt2_up.py -- S6: 幸存者上界 K_surv、理想上界与「分离界天花板」
#
# 框架（SdW Lemma 7 + 分离界）对参数 m 的排除判据：
#   圈存在 =>  ln2*psi(K) <= Lambda < Phi_m(K)，其中 psi(K) = min_{1<=j<=K} ||j delta||
#   若 ln2*psi(K) >= Phi_m(K)，则 K 被排除。
# 幸存者证书（严格）：若 ln2*|q_N delta - p_N| < Phi_m(K)（q_N = 不超过 K 的最大收敛项分母），
#   则 psi(K) <= |q_N delta - p_N| < Phi_m(K)/ln2，故 K 不能被本框架排除。
#   => K_surv(m) := max{ K : ln2*|q_N(K) delta - p_N(K)| < Phi_m(K) } 是「必须超过」的下界。
# 理想口径：把 psi 换成 Dirichlet 上确界 1/K（即假设分离界完美），给出 K_up^ideal 的上界估计。
import mpmath as mp

mp.mp.dps = 150
LOG2 = mp.log(2)
delta = mp.log(3) / LOG2

def dpow(k):
    return mp.exp(k * mp.log(delta))

P, Q = [], []
for line in open("dt2_q.txt"):
    i, pi, qi = map(int, line.split())
    while len(Q) <= i:
        Q.append(None); P.append(None)
    Q[i] = qi; P[i] = pi

def c_m(m, X0):
    X0 = mp.mpf(X0)
    b = (1 + 1 / X0) ** (1 / delta) / mp.mpf(2) ** (1 / delta)
    E = mp.mpf(0); dk = mp.mpf(1)
    for i in range(1, m):
        dk *= delta
        E += (m - i) * dk
    expo = (delta - 1) / (dpow(m) - 1)
    return (1 + 1 / X0) ** (m * expo) * b ** (E * expo)

def Phi(m, K, X0, cm=None):
    if cm is None:
        cm = c_m(m, X0)
    return m * cm * mp.mpf(2) ** (-(delta - 1) * mp.mpf(K) / (dpow(m) - 1))

def absdev(n):
    """|q_n delta - p_n|"""
    return abs(mp.mpf(Q[n]) * delta - P[n])

def K_surv(m, X0=mp.mpf(695) * mp.mpf(2) ** 60):
    """幸存者上界：对每个收敛项区间 [q_N, q_{N+1})，取区间内满足幸存条件的最大 K"""
    cm = c_m(m, X0)
    best = mp.mpf(0); bestN = None
    for N in range(1, 60):
        if Q[N + 1] is None:
            break
        A = LOG2 * absdev(N)
        # 在 [q_N, q_{N+1}) 内求 Phi_m(K) > A 的最大 K
        if Phi(m, Q[N], X0, cm) <= A:
            continue
        # Phi 递减：解 Phi_m(t) = A
        lo, hi = mp.mpf(Q[N]), mp.mpf(Q[N + 1])
        for _ in range(200):
            mid = (lo + hi) / 2
            if Phi(m, mid, X0, cm) > A:
                lo = mid
            else:
                hi = mid
        t = lo
        cand = min(mp.mpf(Q[N + 1]) - 1, mp.floor(t) if t == mp.floor(t) else mp.floor(t))
        cand = min(mp.mpf(Q[N + 1]) - 1, mp.mpf(mp.floor(t)))
        if cand > best:
            best = cand; bestN = N
    return best, bestN

def K_surv_dirichlet(m, X0=mp.mpf(695) * mp.mpf(2) ** 60):
    """把 psi 换成 1/K（Dirichlet 允许的最好情形）时的对应尺度"""
    cm = c_m(m, X0)
    lo, hi = mp.mpf(10), mp.mpf('1e40')
    for _ in range(300):
        mid = (lo * hi) ** mp.mpf('0.5')
        if LOG2 / mid < Phi(m, mid, X0, cm):
            lo = mid
        else:
            hi = mid
    return lo

X0h = mp.mpf(695) * mp.mpf(2) ** 60
X071 = mp.mpf(2) ** 71

print("=" * 96)
print("幸存者上界 K_surv(m)（严格：这些 K 不能被本框架排除）与自举终点 K_low(m) 的对照")
print("K_low(m) 取自 dt2_frontier.py（初等起点 + 自举 + 停点）；K_up_Rhin = 1.4784*m*δ^m")
Klow = {88: mp.mpf('1.3929e27'), 89: mp.mpf('2.0563e20'), 90: mp.mpf('1.1322e28'),
        91: mp.mpf('7.9419644e21'), 92: mp.mpf('7.7692117e19'),
        93: mp.mpf('7.7692117e19'), 94: mp.mpf('7.7692117e19')}
print("\n   m | K_surv(m)          | K_low(m)           | K_low/K_surv | Rhin 上界 1.4784mδ^m | 差值倍数")
for m in range(88, 96):
    ks, N = K_surv(m, X0h)
    up = mp.mpf('1.4784') * m * dpow(m) if m >= 91 else mp.mpf('1.3993') * m * dpow(m)
    kl = Klow.get(m)
    print("  %2d | %-18s | %-18s | %-12s | %-20s | K_surv/Rhin = %.4f"
          % (m, mp.nstr(ks, 6), mp.nstr(kl, 6) if kl else "-",
             mp.nstr(kl / ks, 4) if kl else "-", mp.nstr(up, 6), ks / up))

print()
print("=" * 96)
print("理想口径：若分离界完美（psi 取 Dirichlet 允许的最大尺度 1/K），门槛降到多少？")
print("\n   m | K_surv(实际收敛项)  | K^ideal（psi=1/K） | 两者之比 | 说明")
for m in (88, 90, 91, 92, 93, 95, 100):
    ks, N = K_surv(m, X0h)
    ki = K_surv_dirichlet(m, X0h)
    print("  %2d | %-18s | %-18s | %-10s | 分离界全部潜力只值这个比"
          % (m, mp.nstr(ks, 6), mp.nstr(ki, 6), mp.nstr(ks / ki, 4)))

print()
print("=" * 96)
print("M = 92 失败点的定量：")
ks92, N92 = K_surv(92, X0h)
kl92 = mp.mpf('7.7692117e19')
print("  自举给 K_low(92) = %s" % mp.nstr(kl92, 8))
print("  框架要求 K > K_surv(92) = %s  （差 %s 倍）" % (mp.nstr(ks92, 8), mp.nstr(ks92 / kl92, 4)))
print("  触发 m2=M 发散所需 K > 119.9*δ^92 = %s （差 %s 倍）"
      % (mp.nstr(mp.mpf('119.9') * dpow(92), 6),
         mp.nstr(mp.mpf('119.9') * dpow(92) / kl92, 4)))
print("  Rhin 一致上界 1.4784*92*δ^92 = %s" % mp.nstr(mp.mpf('1.4784') * 92 * dpow(92), 6))
print("  K_surv(92) 与 Rhin 上界之比 = %.4f （说明两条上界同量级：换分离界买不到东西）"
      % (ks92 / (mp.mpf('1.4784') * 92 * dpow(92))))
print()
print("  为把 K_surv(92) 压到 K_low 之下，需要 psi 提升多少倍？")
# Phi_m(K) = A 中 A = ln2*psi；要把门槛 K 降到 7.77e19，需要 A' = Phi_92(7.77e19)
A_needed = Phi(92, kl92, X0h)
A_now = LOG2 * absdev(N92)
print("   当前(区间 %d 的收敛项处) ln2*psi = %s" % (N92, mp.nstr(A_now, 6)))
print("   需要 ln2*psi >= Phi_92(K_low) = %s" % mp.nstr(A_needed, 6))
print("   即 psi 需要提升 %s 倍" % mp.nstr(A_needed / A_now, 4))
print("   而 Dirichlet 上限给 psi <= 1/K_low = %s，最多提升 %s 倍"
      % (mp.nstr(1 / kl92, 6), mp.nstr((1 / kl92) / (A_now / LOG2), 4)))
print("   => 分离界无论多强都不足以跨过（缺口远超 Dirichlet 允许的最大提升）")
