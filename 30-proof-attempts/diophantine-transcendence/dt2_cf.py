# dt2_cf.py  --  S1: continued fraction of delta = log(3)/log(2)
# 核对目标：与 Simons-de Weger v1.43 Corollary 11 印出的 q_20..q_34 数值一致。
import mpmath as mp

mp.mp.dps = 250
delta = mp.log(3) / mp.log(2)
print("delta =", mp.nstr(delta, 60))

# 部分商（高精度递推）
cf = []
x = delta
for i in range(0, 160):
    ai = int(mp.floor(x))
    cf.append(ai)
    x = 1 / (x - ai)

print("a_0..a_40:", cf[:41])
big = [(i, a) for i, a in enumerate(cf) if a > 1000]
print("有大于 1000 的部分商（index, a）:", big)

# 收敛项
p = [cf[0], cf[0] * cf[1] + 1]
q = [1, cf[1]]
for i in range(2, 160):
    p.append(cf[i] * p[-1] + p[-2])
    q.append(cf[i] * q[-1] + q[-2])

sdw = {20: '6.1892e9', 21: '6.5868e9', 22: '6.5470e10', 23: '1.3752e11', 24: '7.5311e11',
       25: '5.4093e12', 26: '6.1624e12', 27: '1.1571e13', 28: '5.2449e13', 29: '4.3116e14',
       30: '4.8361e14', 31: '5.7509e15', 32: '6.2345e15', 33: '1.3044e17', 34: '2.6711e17'}
print("\n   n                 q_n        SdW 印出值      相对差     判定")
nbad = 0
for n, v in sdw.items():
    rel = float(mp.mpf(q[n]) / mp.mpf(v)) - 1
    ok = abs(rel) < 1e-4
    if not ok:
        nbad += 1
    print("%4d %20d   %12s   %10.2e   %s" % (n, q[n], v, rel, "OK" if ok else "MISMATCH"))
print("15 档核对：不一致数 =", nbad)

# 再核几个 frontier.md / 使用到的数
print("\nq_23 =", q[23], "(frontier.md 记 137528045312)")
print("q_24 =", q[24])
print("q_23+q_24 =", q[23] + q[24], "(frontier.md 记 890638885193)")
print("q_21+q_22 =", q[21] + q[22], "(旧 attempt 记 72057431991)")

# 存一个后续脚本可用的收敛项表
with open("dt2_q.txt", "w") as f:
    for i in range(len(q)):
        f.write("%d %d %d\n" % (i, p[i], q[i]))
print("\n已写 dt2_q.txt（index p_n q_n）")
