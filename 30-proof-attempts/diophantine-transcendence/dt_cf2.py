#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
# -*- coding: utf-8 -*-
"""丢番图路线 · 探针 2：单侧窗口判据的精确结构（Stern 与 Brocot 记录序列）。

核心事实（本脚本先验证再使用）：
  正侧判据「排除奇数步数 m 的正环」等价于  1 - frac(m*delta) > m*w，
  而 (1 - frac(m*delta))/m = ceil(m*delta)/m - delta 恰是「分母 m 的最佳上方逼近」的偏差。
  记 gap+(M) = min_{1<=m<=M} (1-frac(m*delta))/m = min{p/q - delta : p/q > delta, 1<=q<=M}。
  于是 M+(X0) = （第一个使 gap 降到 <= w 的最佳上方逼近的分母）- 1。
  负侧同理，换成「最佳下方逼近」。

用法：.venv/bin/python dt_cf2.py
"""
import sys
import mpmath as mp

DPS = 140


def records(delta, side, max_den):
    """Stern 与 Brocot 下降：返回 side='up' 时的最佳上方逼近序列，
    side='down' 时的最佳下方逼近序列。元素为 (p, q)。分母严格递增。"""
    lb, lq = 0, 1      # 左父（在 delta 下方）
    rb, rq = 1, 0      # 右父（在 delta 上方，1/0 = 无穷）
    out = []
    while True:
        mb, mq = lb + rb, lq + rq
        if mq > max_den:
            break
        above = (mb > mq * delta)
        if above:
            rb, rq = mb, mq
            if side == "up":
                out.append((mb, mq))
        else:
            lb, lq = mb, mq
            if side == "down":
                out.append((mb, mq))
    return out


def main():
    mp.mp.dps = DPS
    d = mp.log(3) / mp.log(2)

    print("=" * 78)
    print("零、用暴力法核验「记录序列」结构（numpy 双精度，仅作结构核验）")
    print("=" * 78)
    import numpy as np
    df = float(d)
    recs_up = records(d, "up", 10 ** 40)
    recs_dn = records(d, "down", 10 ** 40)
    print(f"  记录序列长度：上方 {len(recs_up)} 条，下方 {len(recs_dn)} 条"
          f"（最大分母 {recs_up[-1][1]:.3e}）")

    # 高精度暴力核验（mpmath，仅到 M = 200000，双精度在更大范围不可信）
    print("  高精度暴力核验（mpmath 140 位）：")
    for M in [20000, 200000]:
        bu = None
        for m in range(1, M + 1):
            fr = m * d - mp.floor(m * d)
            v = (1 - fr) / m
            if bu is None or v < bu:
                bu = v
        pu = [r for r in recs_up if r[1] <= M][-1]
        vu = mp.mpf(pu[0]) / pu[1] - d
        print(f"    M = {M:>7}: 上方暴力 = {mp.nstr(bu, 15)}, 记录预测 = {mp.nstr(vu, 15)},"
              f" 相对差 = {mp.nstr(abs(bu - vu) / vu, 3)}")
    for M in [1000, 10 ** 5, 10 ** 6, 10 ** 7, 10 ** 8]:
        m = np.arange(1, M + 1, dtype=np.float64)
        fr = m * df
        fr = fr - np.floor(fr)
        up = (1.0 - fr) / m
        dn = fr / m
        # 记录序列给出的预测值：分母 <= M 的最后一条记录
        pu = [r for r in recs_up if r[1] <= M][-1]
        pd = [r for r in recs_dn if r[1] <= M][-1]
        vu = mp.mpf(pu[0]) / pu[1] - d
        vd = d - mp.mpf(pd[0]) / pd[1]
        bu = float(np.min(up))
        bd = float(np.min(dn))
        ru = abs(bu - float(vu)) / float(vu)
        rd = abs(bd - float(vd)) / float(vd)
        print(f"  M = {M:>10}:  上方 min(暴力)={bu:.6e} 记录预测={float(vu):.6e} "
              f"相对差={ru:.2e} | 下方 min={bd:.6e} 记录预测={float(vd):.6e} 相对差={rd:.2e}")

    print()
    print("=" * 78)
    print("一、记录序列中的关键项（高精度）")
    print("=" * 78)
    print(f"{'序号':>4} {'q':>26} {'p/q - delta':>26}")
    for i, (p, q) in enumerate(recs_up):
        g = mp.mpf(p) / q - d
        if q in (1, 3, 5, 17, 41, 306, 971, 111202, 190537, 31867, 79335,
                 10590737, 10781274) or g < mp.mpf(10) ** -20:
            print(f"{i:>4} {q:>26} {mp.nstr(g, 12):>26}")
    print("  （q 加粗项以外的记录此处略去；下方逼近序列首几项：）")
    for i, (p, q) in enumerate(recs_dn[:12]):
        print(f"    {i:>3} {q:>12}   delta - p/q = {mp.nstr(d - mp.mpf(p)/q, 12)}")

    print()
    print("=" * 78)
    print("二、复算 cycles.md 4.5 节的 M+ 与 M-（判据 w = 1/((3X0-1)ln2)）")
    print("=" * 78)
    lit = {10 ** 6: (2965, 664), 10 ** 8: (15600, 16265), 3 * 10 ** 9: (79334, 111201),
           10 ** 10: (190536, 111201), 3 * 10 ** 10: (190536, 492275),
           10 ** 11: (190536, 1063886), 10 ** 12: (10781273, 5446237)}
    print(f"{'X0':>14} {'M+(我算)':>14} {'M+(cycles.md)':>14} {'一致':>5} "
          f"{'M-(我算)':>14} {'M-(cycles.md)':>14} {'一致':>5}")
    allok = True
    for X0 in sorted(lit):
        w = 1 / ((3 * mp.mpf(X0) - 1) * mp.log(2))
        first_up = None
        for p, q in recs_up:
            if mp.mpf(p) / q - d <= w:
                first_up = q
                break
        first_dn = None
        for p, q in recs_dn:
            if d - mp.mpf(p) / q <= w:
                first_dn = q
                break
        Mp = first_up - 1
        Mn = first_dn - 1
        lMp, lMn = lit[X0]
        okp = (Mp == lMp)
        okn = (Mn == lMn)
        allok = allok and okp and okn
        print(f"{X0:>14} {Mp:>14} {lMp:>14} {'是' if okp else '否':>5} "
              f"{Mn:>14} {lMn:>14} {'是' if okn else '否':>5}")
    print("全部一致" if allok else "*** 存在不一致 ***")
    print("  （cycles.md 的数字见 20-experiments/findings/cycles.md 第 4.5 节表）")

    print()
    print("=" * 78)
    print("三、「K > q_n」所需验证界 X0")
    print("=" * 78)
    print("判据：排除全部 K <= q_n 需要 w < gap+(q_n)，gap+(q_n) = 分母 <= q_n 的最佳上方偏差。")
    print("注意 gap+(q_n) 未必在 m = q_n 取到（见第零节：上方最佳逼近含 Stern 与 Brocot 中间分数）。")
    print()
    # 连分数收敛项
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

    print(f"{'n':>3} {'q_n':>22} {'gap+(q_n)':>22} {'在 q_n 取到?':>12} "
          f"{'X0(1/(3ln2))':>18} {'X0(1/(4ln2))':>18}")
    rows = {}
    for n in range(19, 25):
        Q = int(qs[n])
        cand = [r for r in recs_up if r[1] <= Q][-1]
        g = mp.mpf(cand[0]) / cand[1] - d
        X0_3 = 1 / (3 * mp.log(2) * g) + mp.mpf(1) / 3
        X0_4 = 1 / (4 * mp.log(2) * g)
        at_qn = "是" if cand[1] == Q else f"否(在 {cand[1]})"
        rows[n] = (Q, g, X0_3, X0_4)
        print(f"{n:>3} {Q:>22} {mp.nstr(g, 12):>22} {at_qn:>12} "
              f"{mp.nstr(X0_3, 8):>18} {mp.nstr(X0_4, 8):>18}")
    print()
    print("对照 1：Hercher 2023 Corollary 29 门槛 X0 >= 1536*2^60 =",
          mp.nstr(1536 * mp.mpf(2) ** 60, 10))
    print("对照 2：Barina 2025 验证界 2^71 =", mp.nstr(mp.mpf(2) ** 71, 10))
    for n in [21, 22, 23]:
        Q, g, X3, X4 = rows[n]
        print(f"  以 K > q_{n} = {Q} 为目标：本工作 w 口径需 X0 > {mp.nstr(X3, 6)}"
              f"（= 2^{mp.nstr(mp.log(X3, 2), 5)}）")
        print(f"      与 1536*2^60 之比 {mp.nstr(X3 / (1536 * mp.mpf(2) ** 60), 5)}，"
              f"与 2^71 之比 {mp.nstr(X3 / mp.mpf(2) ** 71, 5)}")

    print()
    print("=" * 78)
    print("四、按 X0 反查能达到的 M+（含更细的 X0 台阶）")
    print("=" * 78)
    print(f"{'X0':>16} {'M+':>22} {'= 哪个记录分母':>16} {'相应 gap':>24}")
    for e in range(12, 25):
        X0 = mp.mpf(10) ** e
        w = 1 / ((3 * X0 - 1) * mp.log(2))
        for i, (p, q) in enumerate(recs_up):
            if mp.mpf(p) / q - d <= w:
                print(f"{'10^%d' % e:>16} {q - 1:>22} {q:>16} "
                      f"{mp.nstr(mp.mpf(p) / q - d, 12):>24}")
                break

    return 0


if __name__ == "__main__":
    sys.exit(main())
