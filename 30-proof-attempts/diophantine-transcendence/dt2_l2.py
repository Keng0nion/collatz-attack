# dt2_l2.py -- L2 与失败点 1(b) 的数值
#  (1) 一致性引理的显式阈值：C_N 失败 <=> a_{N+1} > ln2/(q_N * Phi_m(q_N))   [m=92, q_N=10^30]
#  (2) 若只有无理测度型一致界 Lambda >= c*K^(1-mu)，要压过 Phi_92(K_low) 需要多大的 c
import mpmath as mp

mp.mp.dps = 60
delta = mp.log(3) / mp.log(2)
LOG2 = mp.log(2)

def dpow(k):
    return mp.exp(k * mp.log(delta))

m = 92
cm_inf = mp.mpf(2) ** (-1 / (delta - 1))          # X0 -> 无穷 的极限常数（X0 依赖可忽略）

print("(1) 一致性阈值")
qN = mp.mpf(10) ** 30
Phi = m * cm_inf * mp.mpf(2) ** (-(delta - 1) * qN / (dpow(m) - 1))
thr = LOG2 / (qN * Phi)
print("  delta^92 =", mp.nstr(dpow(92), 8))
print("  (delta-1)/(delta^92-1) =", mp.nstr((delta - 1) / (dpow(92) - 1), 6))
print("  Phi_92(1e30) =", mp.nstr(Phi, 6))
print("  阈值 = ln2/(q_N*Phi) =", mp.nstr(thr, 6))
print("  log10(阈值) =", mp.nstr(mp.log10(thr), 8))

print("\n(2) 无理测度型一致界的常数要求（最紧点在 K = K_low(92) = 7.7692117e19）")
K = mp.mpf('7.7692117e19')
PhiK = m * cm_inf * mp.mpf(2) ** (-(delta - 1) * K / (dpow(m) - 1))
print("  Phi_92(K_low) =", mp.nstr(PhiK, 6))
for mu in (2.5, 3.0, 3.6, 5.0, 13.3):
    c = PhiK * K ** (mu - 1)
    print("    mu=%-6s 需要 c >= %s" % (mu, mp.nstr(c, 4)))
