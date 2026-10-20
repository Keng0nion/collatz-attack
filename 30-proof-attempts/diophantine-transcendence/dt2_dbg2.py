# dt2_dbg2.py -- 定位 dt2_chain.py 第 (C) 节与 dt2_ladder.py 结果不一致的原因
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

X0 = mp.mpf(695) * mp.mpf(2) ** 60

def up_records(Qmax):
    mp.mp.dps = 400
    d = mp.log(3) / mp.log(2)
    mp.mp.dps = 150
    rec = []; best = None
    lo_n, lo_d, hi_n, hi_d = 0, 1, 1, 0
    steps = 0
    while steps < 20000:
        mn, md = lo_n + hi_n, lo_d + hi_d
        if md > Qmax:
            break
        steps += 1
        if mp.mpf(mn) / md > d:
            hi_n, hi_d = mn, md
            g = (mp.mpf(mn) - md * d) / md
            if best is None or g < best:
                best = g; rec.append((md, g))
        else:
            lo_n, lo_d = mn, md
    return rec

R = up_records(10 ** 40 + 10)
print("记录数 =", len(R), " 最大 q =", mp.nstr(R[-1][0], 6))
print("前 6 条:", [(q, mp.nstr(g, 3)) for q, g in R[:6]])
print("q 在 1e18 至 1e21 的记录:")
for q, g in R:
    if 10 ** 18 <= q <= 10 ** 21:
        print("   q=%-22d gap+=%s" % (q, mp.nstr(g, 6)))
print("q=1 的 gap+ =", mp.nstr(R[0][1], 4))
print("→ q_min(4.002e-38) 应为:", [q for q, g in R if g < mp.mpf('4.002e-38')][:1])
print("→ q_min(4.274e-38) 应为:", [q for q, g in R if g < mp.mpf('4.274e-38')][:1])
