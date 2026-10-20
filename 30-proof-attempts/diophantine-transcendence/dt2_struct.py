# dt2_struct.py -- S2: 区间最小值结构 + 记录乘积（一致性问题的量化）
#  (Q1) min_{1<=j<=q_N}||j delta|| == |q_N delta - p_N|?          [SdW Lemma 9(c)]
#  (Q2) min_{q_N<=j<q_{N+1}}||j delta|| 与 |q_N delta - p_N| 的关系  [旧 attempt 用法的检验]
#  (Q3) 上方逼近记录上乘积 q*gap+(q) 的行为（决定「一致性」是否可能）
import mpmath as mp

mp.mp.dps = 400
delta = mp.log(3) / mp.log(2)
DIG = 300
B = 10 ** DIG
A = int(mp.floor(delta * B + mp.mpf('0.5')))
print("有理截断误差 =", float(abs(mp.mpf(A) / B - delta)))

def nf(j):
    t = (j * A) % B
    return min(t, B - t)

q, p = [], []
for line in open("dt2_q.txt"):
    i, pi, qi = map(int, line.split())
    while len(q) <= i:
        q.append(None); p.append(None)
    q[i] = qi; p[i] = pi

print("\n(Q1) min_{1<=j<=q_N} ||j delta|| vs |q_N delta - p_N|（穷举）")
bad = []
for N in range(2, 18):
    target = abs(q[N] * A - p[N] * B)
    m = min(nf(j) for j in range(1, q[N] + 1))
    if m != target:
        bad.append((N, m, target))
print("  N=2..17：违反数 =", len(bad), bad, " => SdW Lemma 9(c) 成立")

print("\n(Q2) 区间 [q_N, q_{N+1}) 上真实最小值 / |q_N delta - p_N|（穷举，小 N）")
for N in range(2, 15):
    lo, hi = q[N], q[N + 1]
    if hi - lo > 10 ** 7:
        print("  N=%2d 区间长 %d 过大，跳过" % (N, hi - lo)); continue
    target = abs(q[N] * A - p[N] * B)
    vals = [nf(j) for j in range(lo, hi)]
    m = min(vals)
    print("  N=%2d a_{N+1}=%2d 区间长=%-9d 真实min/|q_Nd-p_N| = %.6f   最小点 j-q_N = %d"
          % (N, q[N + 1] // q[N], hi - lo, m / target, vals.index(m)))

print("\n(Q2') 结构候选（中间分数）：cand = min_t |(q_N+t q_{N-1})d - (p_N+t p_{N-1})|，t=1..a_{N+1}-1")
print("      cand/|q_N d-p_N| < 1 表示区间最小值比 |q_N d-p_N| 更小（旧用法的 psi 不保守）")
worst = 1.0; rows = []
for N in range(2, 45):
    AN = abs(q[N] * A - p[N] * B)
    AN1 = abs(q[N - 1] * A - p[N - 1] * B)
    a_next = q[N + 1] // q[N]
    cand = AN
    for t in range(1, a_next):
        cand = min(cand, abs(AN - t * AN1))
    r = cand / AN
    worst = min(worst, r)
    if r < 0.999:
        rows.append((N, a_next, r))
for N, a, r in rows:
    print("      N=%2d a_{N+1}=%2d  cand/AN = %.6f" % (N, a, r))
print("      最小 cand/AN = %.6f（出现在 a_{N+1} 较小处）" % worst)

print("\n(Q3) 上方逼近记录上乘积 q*gap+ 的行为（前 20 条与后 10 条）")
def recs(Qmax):
    mp.mp.dps = 400
    d = mp.log(3) / mp.log(2)
    mp.mp.dps = 400
    out = []; best = None
    lo_n, lo_d, hi_n, hi_d = 0, 1, 1, 0
    while True:
        mn, md = lo_n + hi_n, lo_d + hi_d
        if md > Qmax:
            break
        if mp.mpf(mn) / md > d:
            hi_n, hi_d = mn, md
            g = (mp.mpf(mn) - md * d) / md
            if best is None or g < best:
                best = g; out.append((md, g, md * g))
        else:
            lo_n, lo_d = mn, md
    return out

R = recs(10 ** 60)
print("  记录数 =", len(R))
for i, (qq, g, prod) in enumerate(R[:20] + R[-10:]):
    print("      q=%-24d gap+=%-12s q*gap+=%s" % (qq, mp.nstr(g, 4), mp.nstr(prod, 4)))
mono = all(R[i + 1][2] <= R[i][2] for i in range(len(R) - 1))
print("  q*gap+ 沿记录单调不增？", mono)
