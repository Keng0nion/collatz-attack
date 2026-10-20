#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
# -*- coding: utf-8 -*-
"""丢番图路线 · 探针 6：本报告依赖的两条外部工具的核验。

(C1) 最佳逼近（第二类）：对 K <= q_n 有 ||K*delta|| >= |q_n*delta - p_n|。
     逐点暴力核验若干档（q_n = 665, 15601, 79335, 190537, 10781274）。
(C2) 区间算术：对 q_19..q_24 认证 |q_n*delta - p_n| > 1/(q_n+q_(n+1))。
     说明：mpmath 的 iv 模块用方向性舍入，但不是形式化验证工具，故只称「数值区间认证」。

用法：.venv/bin/python dt_check.py
"""
import sys
import mpmath as mp


def main():
    mp.mp.dps = 200
    d = mp.log(3) / mp.log(2)
    a, ps, qs = [], [], []
    x = d
    pm2, pm1, qm2, qm1 = mp.mpf(0), mp.mpf(1), mp.mpf(1), mp.mpf(0)
    for n in range(40):
        ai = int(mp.floor(x))
        a.append(ai)
        pn, qn = ai * pm1 + pm2, ai * qm1 + qm2
        ps.append(pn); qs.append(qn)
        pm2, pm1 = pm1, pn
        qm2, qm1 = qm1, qn
        x = 1 / (x - ai)

    print("=" * 78)
    print("(C1) 最佳逼近性质：对 1 <= K <= q_n 逐点核验 ||K delta|| >= |q_n delta - p_n|")
    print("=" * 78)
    print("（|q_n delta - p_n| 本身用 200 位精度直接算；逐点核验用同样精度比较）")
    for n in [8, 9, 11, 13, 15]:
        Q = int(qs[n])
        target = abs(qs[n] * d - ps[n])
        worst = None
        worst_k = None
        for K in range(1, Q + 1):
            v = abs(K * d - mp.nint(K * d))
            if worst is None or v < worst:
                worst = v
                worst_k = K
            if v < target:
                print(f"  *** 反例：K = {K}, ||K delta|| = {mp.nstr(v, 20)} < "
                      f"|q_{n} delta - p_{n}| = {mp.nstr(target, 20)}")
                break
        else:
            print(f"  q_{n} = {Q:>10}: 逐点核验通过；最小 ||K delta|| = {mp.nstr(worst, 20)} "
                  f"在 K = {worst_k}（{'= q_%d' % n if worst_k == Q else '其他'}），"
                  f"比值 = {mp.nstr(worst / target, 8)}")

    print()
    print("=" * 78)
    print("(C2) 区间算术认证：1/(q_n+q_(n+1)) < |q_n delta - p_n| < 1/q_(n+1)")
    print("=" * 78)
    mp.iv.dps = 80
    ivd = mp.iv.log(3) / mp.iv.log(2)
    print(f"  delta 的区间宽度 = {mp.nstr(mp.mpf(ivd.b) - mp.mpf(ivd.a), 5)}")
    ok = True
    for n in range(1, 30):
        qn = int(qs[n])
        pn = int(ps[n])
        ivv = qn * ivd                       # 区间 [lo, hi]
        lo = abs(mp.mpf(ivv.a) - pn)
        hi = abs(mp.mpf(ivv.b) - pn)
        # |q_n delta - p_n| 落在 [min(lo,hi), max(lo,hi)]（因 p_n 精确）
        vmin, vmax = min(lo, hi), max(lo, hi)
        lowbound = mp.mpf(1) / (qn + int(qs[n + 1]))
        upbound = mp.mpf(1) / int(qs[n + 1])
        good = (vmin > lowbound) and (vmax < upbound)
        ok = ok and good
        if n >= 19 or not good:
            print(f"  n = {n:>2}: |q_n d - p_n| ∈ [{mp.nstr(vmin, 18)}, {mp.nstr(vmax, 18)}]"
                  f"  下界 {mp.nstr(lowbound, 10)}  上界 {mp.nstr(upbound, 10)}"
                  f"  {'通过' if good else '*** 未通过'}")
    print("  全部 n = 1..29 通过" if ok else "  *** 有未通过项 ***")

    print()
    print("=" * 78)
    print("(C3) 已知环不触犯判据前提（阳性对照）")
    print("=" * 78)
    X0 = 10 ** 12
    known = [0, 1, -1, 5, 7, 10, 17, 136]
    print(f"  已知环的元素绝对值最大者 = {max(abs(v) for v in known)}，"
          f"判据前提要求 >= X0 = {X0}")
    print(f"  {max(abs(v) for v in known)} < {X0} 成立，故已知环不受 M+、M- 约束，无矛盾。")
    print("  （已知环清单取自本项目的 findings/cycles.md 第四节表：{0}、{1,2}、{-1}、"
          "{-10,-7,-5}、{-17,...,-136}）")

    return 0


if __name__ == "__main__":
    sys.exit(main())
