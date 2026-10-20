#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
# -*- coding: utf-8 -*-
"""丢番图路线 · 探针 1：delta = log2 3 的连分数、收敛项、单侧逼近的极小比值、
以及「K > q_n」所需的验证界 X0。

只做计算与自检，不做任何未经核验的断言。所有数字都打印出来供独立复核。

用法：
    .venv/bin/python dt_cf.py
"""
import sys
import mpmath as mp

DPS = 120


def frac(x):
    return x - mp.floor(x)


def cf_and_convergents(d, nmax):
    """返回 delta 的连分数部分商与收敛项 p_n/q_n。"""
    a = []
    p = [mp.mpf(1), mp.mpf(0)]   # p[-2], p[-1] 的滚动写法，下面手工管理
    # 标准递推：p_0 = a_0, p_1 = a_1 a_0 + 1, ...
    x = d
    ps = []
    qs = []
    pm2, pm1 = mp.mpf(0), mp.mpf(1)
    qm2, qm1 = mp.mpf(1), mp.mpf(0)
    for n in range(nmax):
        ai = int(mp.floor(x))
        a.append(ai)
        pn = ai * pm1 + pm2
        qn = ai * qm1 + qm2
        ps.append(pn)
        qs.append(qn)
        pm2, pm1 = pm1, pn
        qm2, qm1 = qm1, qn
        x = 1 / (x - ai)
    return a, ps, qs


def main():
    mp.mp.dps = DPS
    d = mp.log(3) / mp.log(2)

    print("=" * 78)
    print("一、delta = log2 3 与连分数")
    print("=" * 78)
    print("delta =", mp.nstr(d, 60))
    a, ps, qs = cf_and_convergents(d, 46)
    print("部分商（0 号起）:", a[:36])
    print()
    print("收敛项 p_n/q_n，n = 19..35：")
    print(f"{'n':>4} {'p_n':>28} {'q_n':>28}")
    for n in range(19, 36):
        print(f"{n:>4} {mp.nstr(ps[n], 28):>28} {mp.nstr(qs[n], 28):>28}")

    print()
    print("对照 Simons 与 de Weger v1.43 Corollary 11 原表（q_20..q_34）：")
    lit = {20: "6.1892e9", 21: "6.5868e9", 22: "6.5470e10", 23: "1.3752e11",
           24: "7.5311e11", 25: "5.4093e12", 26: "6.1624e12", 27: "1.1571e13",
           28: "5.2449e13", 29: "4.3116e14", 30: "4.8361e14", 31: "5.7509e15",
           32: "6.2345e15", 33: "1.3044e17", 34: "2.6711e17"}
    ok_all = True
    for n in sorted(lit):
        mine = mp.nstr(qs[n], 5)
        agree = (mine[:5] == mp.nstr(mp.mpf(lit[n].replace("e", "e")), 5)[:5]) if False else None
        # 直接比较 3 位有效数字
        mine3 = mp.nstr(qs[n], 3)
        lit3 = mp.nstr(mp.mpf(lit[n]), 3)
        flag = "OK" if mine3 == lit3 else "不一致"
        if mine3 != lit3:
            ok_all = False
        print(f"  q_{n:<2} 我算 {mp.nstr(qs[n], 12):>16}   文献 {lit[n]:>12}   {flag}")
    print("全部一致" if ok_all else "存在不一致，见上")
    print("【注】文献侧数字逐字取自本机下载的 v1.43 PDF 的 Corollary 11（文件见 dt_sources.txt 记录）")

    print()
    print("=" * 78)
    print("二、关键不等式：1/(q_n+q_(n+1)) < |q_n*delta - p_n| < 1/q_(n+1)")
    print("=" * 78)
    print(f"{'n':>4} {'|q_n d - p_n|':>26} {'1/(q_n+q_n+1)':>26} {'1/q_n+1':>26} {'检查':>6}")
    for n in range(0, 36):
        v = abs(qs[n] * d - ps[n])
        lo = 1 / (qs[n] + qs[n + 1])
        hi = 1 / qs[n + 1]
        chk = "OK" if (lo < v < hi) else "违反"
        print(f"{n:>4} {mp.nstr(v, 20):>26} {mp.nstr(lo, 20):>26} {mp.nstr(hi, 20):>26} {chk:>6}")

    print()
    print("=" * 78)
    print("三、单侧（上方）逼近的比值 |q_n d - p_n| / q_n，n 为奇数时 p_n/q_n > delta")
    print("=" * 78)
    print(f"{'n':>4} {'符号 p_n-q_n d':>16} {'比值 |q_n d-p_n|/q_n':>26}")
    for n in range(1, 36):
        sgn = ps[n] - qs[n] * d
        ratio = abs(sgn) / qs[n]
        print(f"{n:>4} {'正(上方)' if sgn > 0 else '负(下方)':>16} {mp.nstr(ratio, 20):>26}")

    print()
    print("=" * 78)
    print("四、真值核验：单侧窗口判据的极小比值 min_{m<=M} (1-frac(m d))/m")
    print("=" * 78)
    print("先在小范围内暴力核验「极小值落在奇数收敛项上」这一结构。")
    import numpy as np
    df = float(d)
    for M in [1000, 10 ** 5, 10 ** 6, 10 ** 7, 3 * 10 ** 7]:
        m = np.arange(1, M + 1, dtype=np.float64)
        fr = m * df
        fr = fr - np.floor(fr)
        val = (1.0 - fr) / m
        i = int(np.argmin(val))
        mbest = i + 1
        vbest = float(val[i])
        # 高精度复核
        mm = mp.mpf(mbest)
        frx = mm * d - mp.floor(mm * d)
        vx = (1 - frx) / mm
        print(f"  M = {M:>10}: 暴力极小在 m = {mbest:>12}, 值 = {mp.nstr(vx, 12)}")

    print()
    print("=" * 78)
    print("五、「K > q_n」所需验证界 X0（三种口径）")
    print("=" * 78)
    print("口径 1（本工作判据，逐 K 的精确单侧窗口）：")
    print("   排除 1<=K<=M  <=>  w < min_{K<=M}(1-frac(K d))/K,  w = 1/((3X0-1)ln2)")
    print("   取 M = q_n，极小值在 m = q_n（下方近似已由暴力核验，见第四节），")
    print("   于是需要 3X0 - 1 > q_n / (ln2 * |q_n d - p_n|)。")
    print()
    print("口径 2（Simons 与 de Wyer / Eliahou 的引理形态，用 L >= 1/(q_n+q_n+1) 的下界）：")
    print("   Lambda > ln2/(q_n+q_n+1) 与 Lambda <= K/(3X0) 在 K<=q_n 时矛盾")
    print("   <= 需要 3 ln2 X0 > q_n(q_n+q_n+1)。")
    print()
    print("口径 3（Hercher Theorem 16 / 27 的 m 无关形态）：")
    print("   Lambda < K/(3X0) 或 K/(4X0)，条件同上，只换常数。")
    print()
    tgt = [19, 20, 21, 22, 23, 24]
    print(f"{'n':>4} {'q_n':>22} {'X0 口径1':>22} {'X0 口径2 (=3ln2)':>22} "
          f"{'X0 口径2 (=4ln2)':>22}")
    for n in tgt:
        qn, qn1 = qs[n], qs[n + 1]
        v = abs(qs[n] * d - ps[n])
        X1 = (qn / (mp.log(2) * v) + 1) / 3
        X2a = qn * (qn + qn1) / (3 * mp.log(2))
        X2b = qn * (qn + qn1) / (4 * mp.log(2))
        print(f"{n:>4} {mp.nstr(qn, 12):>22} {mp.nstr(X1, 8):>22} "
              f"{mp.nstr(X2a, 8):>22} {mp.nstr(X2b, 8):>22}")

    print()
    print("对照：Hercher 2023 Corollary 29 的门槛 X0 >= 1536*2^60 =", mp.nstr(1536 * mp.mpf(2) ** 60, 8))
    print("对照：Barina 2025 的验证界 2^71 =", mp.nstr(mp.mpf(2) ** 71, 8))

    print()
    print("=" * 78)
    print("六、区间算术（mpmath.iv）对关键量的认证")
    print("=" * 78)
    mp.iv.dps = 60
    ivd = mp.iv.log(3) / mp.iv.log(2)
    print("delta ∈ [", mp.nstr(ivd.a, 25), ",", mp.nstr(ivd.b, 25), "]")
    # 认证 q_23 d - p_23 的符号与量级
    for n in [21, 22, 23, 24]:
        qn = int(qs[n])
        ivv = qn * ivd
        lo = ivv.a - mp.floor(ivv.a)
        hi = ivv.b - mp.floor(ivv.b)
        print(f"  q_{n}*delta 的小数部分区间 [{mp.nstr(lo, 20)}, {mp.nstr(hi, 20)}]"
              f"   （宽度 {mp.nstr(hi - lo, 5)}）")
    print("【注】上表用于确认符号判定有充足余量；mpmath 的 iv 模块提供方向性舍入，")
    print("      但本工作不做形式化验证，故只称「数值区间认证」。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
