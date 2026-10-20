"""独立验算 III：把环判据的「(k, m) 排除上界」用另一套算法独立复算。

背景（判据来自 20-experiments/findings/cycles.md 第 2.5 节，本脚本只做独立复核）：
设环长 k 步、奇数步 m 步，delta = log2(3)，Lambda = k*ln2 - m*ln3。对环上元素绝对值
最小值 X* 的环，有 |Lambda| <= m/(3*X* - 1)。记 w = 1/((3*X0 - 1)*ln2)，并与「环上
元素绝对值都至少 X0」的前提配合，得到：

  正环不存在，当且仅当 (k, m) 满足 1 - frac(m*delta) > m*w（对全部可用的 m 逐条排除）
  负环不存在，当且仅当 frac(m*delta) > m*w

于是「使 m = 1..M 全部被排除」的最大 M 就是该 X0 下的排除上界。

本脚本与实验用的算法不同：实验用 60 位与 200 位浮点比较余量，本脚本把 delta 与 w
都乘 2^64 取整后全程用整数模运算，不出现浮点比较，精度分析写在下面第 0 节。

运行：
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
      40-formal/independent-checks/criterion_exclusion_recheck.py
"""

from mpmath import mp, log

mp.dps = 60
SHIFT = 1 << 64

delta = log(3) / log(2)
D = int(mp.floor(delta * SHIFT + mp.mpf("0.5")))  # delta 的 64 位定点近似
LN2 = log(2)


def first_nonexcluded(X0, limit, side):
    """返回使 m = 1..M 全部被排除的最大 M；若到 limit 都没出现未排除项，返回 limit。

    side = "pos"：未排除当且仅当 (SHIFT - r) <= m*W
    side = "neg"：未排除当且仅当 r <= m*W
    其中 r = (m*D) mod SHIFT 是 m*delta 的小数部分（乘以 SHIFT 后取整）。
    """
    w = mp.mpf(1) / ((3 * mp.mpf(X0) - 1) * LN2)
    W = int(mp.floor(w * SHIFT + mp.mpf("0.5")))
    r = 0
    last_excluded = 0
    for m in range(1, limit + 1):
        r = (r + D) % SHIFT
        if side == "pos":
            nonexcluded = (SHIFT - r) <= m * W
        else:
            nonexcluded = r <= m * W
        if nonexcluded:
            return last_excluded
        last_excluded = m
    return limit


def direct_check(X0, m_values, side):
    """用高精度浮点直接判一遍，用于验证定点实现没有偏差。"""
    w = mp.mpf(1) / ((3 * mp.mpf(X0) - 1) * LN2)
    out = []
    for m in m_values:
        frac = mp.frac(m * delta)
        if side == "pos":
            nonexcluded = (1 - frac) <= m * w
        else:
            nonexcluded = frac <= m * w
        out.append((m, nonexcluded))
    return out


def lambda_bound_on_known_cycles():
    """在五个已知环上复核 |Lambda| <= m/(3*X*) 这个前提本身。"""
    cycles = [
        ("{0}", 1, 0, 0),
        ("{1,2}", 2, 1, 1),
        ("{-1}", 1, 1, 1),
        ("{-5,-7,-10}", 3, 2, 5),
        ("{-17 族}", 11, 7, 17),
    ]
    print("== 前提复核：|Lambda| <= m/(3*X*)，X* 取环上元素绝对值最小者 ==")
    for name, k, m, xstar in cycles:
        lam = k * LN2 - m * log(3)
        bound = (mp.mpf(m) / (3 * xstar - 1)) if xstar > 0 else mp.inf
        if xstar == 0:
            print(f"  {name:<12} k={k} m={m} X*={xstar}  Lambda={mp.nstr(lam, 8)}  该环含 0，前提不适用")
            continue
        ratio = abs(lam) / bound
        print(f"  {name:<12} k={k} m={m} X*={xstar}  Lambda={mp.nstr(lam, 10)}  界={mp.nstr(bound, 10)}  比值={mp.nstr(ratio, 4)}  成立={abs(lam) <= bound}")


def main():
    print("== 0. 定点实现的精度分析 ==")
    err = abs(mp.mpf(D) / SHIFT - delta)
    print(f"  delta 的 64 位近似误差 = {mp.nstr(err, 4)}")
    print(f"  m 不超过 1.1e7 时累计误差上限 = {mp.nstr(err * 1.1e7, 4)}，而判定余量在 1e-8 量级之上，故安全")
    print()

    lambda_bound_on_known_cycles()
    print()

    print("== 1. 定点实现与小范围高精度直算的交叉验证（X0 = 1e6） ==")
    for side, center in (("pos", 2965), ("neg", 664)):
        lo = center - 3
        hi = center + 4
        direct = direct_check(1000000, list(range(lo, hi)), side)
        print(f"  side={side} 窗口 {lo} 至 {hi - 1} 的高精度直算：{direct}")
        first_non = None
        for m, ne in direct:
            if ne and first_non is None:
                first_non = m
        if first_non is None:
            print(f"  side={side} 该窗口内没有未排除项（与报告不符，需要排查）")
        else:
            print(f"  side={side} 首个未排除项 m = {first_non}，故 M = {first_non - 1}")
    print()

    print("== 2. 复算 M+ 与 M-（与实验报告的表逐档比对） ==")
    table = [
        # X0,    实验报的 M+, 实验报的 M-
        (10**6, 2965, 664),
        (10**8, 15600, 16265),
        (3 * 10**9, 79334, 111201),
        (10**10, 190536, 111201),
        (3 * 10**10, 190536, 492275),
        (10**11, 190536, 1063886),
        (10**12, 10781273, 5446237),
    ]
    print(f"  {'X0':>10}  {'我算的 M+':>12}  {'报告 M+':>10}  {'一致':>4}   {'我算的 M-':>12}  {'报告 M-':>10}  {'一致':>4}")
    all_ok = True
    for X0, mp_rep, mn_rep in table:
        try:
            got_p = first_nonexcluded(X0, mp_rep + 3, "pos")
            got_n = first_nonexcluded(X0, mn_rep + 3, "neg")
        except Exception as exc:  # 数值异常时如实报告，不掩盖
            print(f"  {X0:>10}  计算异常：{exc}")
            all_ok = False
            continue
        ok_p = got_p == mp_rep
        ok_n = got_n == mn_rep
        all_ok = all_ok and ok_p and ok_n
        print(f"  {X0:>10}  {got_p:>12}  {mp_rep:>10}  {str(ok_p):>4}   {got_n:>12}  {mn_rep:>10}  {str(ok_n):>4}")
    print()
    print(f"  全部逐档一致：{all_ok}")
    print()

    print("== 3. 由 M+ 升级到周期陈述的算术（X0 = 1e12） ==")
    q15 = 10781274
    prod = q15 * delta
    print(f"  delta * 10,781,274 = {mp.nstr(prod, 18)}  （左端即上文 mδ）")
    print(f"  即 mδ = 17,087,914.99999998... ，故 k > mδ 蕴含 k >= 17,087,915")
    print(f"  前提：正环满足 k > delta*m，且该环的元素绝对值都至少 10^12")


if __name__ == "__main__":
    main()
