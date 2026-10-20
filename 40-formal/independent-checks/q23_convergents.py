"""独立验算：log2(3) 的连分数门槛 q_23 与由它导出的两个周期下界。

本脚本由主代理（非工作流子代理）编写并运行，目的只有一个：把边界地图里几个
载荷数字用精确/高精度算术重算一遍，确认它们不是抄错的。

运行方式：
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
      40-formal/independent-checks/q23_convergents.py

验算结论（2026 年 10 月 18 日运行）：
  q_23 = 137528045312 确实出现在 log2(3) 的连分数收敛分母序列中；
  q_23 + q_24 = 890638885193 与文献给出的下一档门槛逐位一致；
  q_23 * (1 + log3/log2) = 355504839929.0 与标准映射的周期下界逐位一致；
  q_23 * log2(3) = 217976794617.0 与加速映射的周期下界逐位一致
  （该数字在文献里只有二手来源，本次由 q_23 独立复算得到）。
  附带发现：Eliahou 周期形式里的三个常数 301994、17087915、85137581
  恰好是 log2(3) 连分数第 13、15、16 个收敛分数的分子。
"""

from mpmath import mp, log

mp.dps = 90
x = log(3) / log(2)  # log2(3)


def cf_convergents(value, n):
    """log2(3) 的连分数部分商与前 n 个收敛分数 (p, q)。"""
    a = []
    v = mp.mpf(value)
    for _ in range(n):
        ai = int(mp.floor(v))
        a.append(ai)
        frac = v - ai
        if frac < mp.mpf("1e-80"):
            break
        v = 1 / frac
    p_prev, p_cur = 0, 1
    q_prev, q_cur = 1, 0
    out = []
    for ai in a:
        p = ai * p_cur + p_prev
        q = ai * q_cur + q_prev
        out.append((p, q))
        p_prev, p_cur = p_cur, p
        q_prev, q_cur = q_cur, q
    return a, out


def main():
    a, conv = cf_convergents(x, 30)
    print("log2(3) 的连分数部分商:", a[:24])
    print()

    q23 = 137528045312
    q24 = 753110839881
    idx23 = idx24 = None
    for i, (p, q) in enumerate(conv):
        if q == q23:
            idx23 = i
        if q == q24:
            idx24 = i
        if i <= 26:
            print(f"n={i:2d}  p={p:<24} q={q}")

    print()
    print("q_23 在收敛分数序列中的下标（从 0 计）:", idx23)
    print("q_24 在收敛分数序列中的下标（从 0 计）:", idx24)
    print("q_23 + q_24 =", q23 + q24, " 文献给出的下一档门槛 890638885193 ->", q23 + q24 == 890638885193)
    print()

    delta = log(3) / log(2)
    std_bound = mp.mpf(q23) * (1 + delta)
    acc_bound = mp.mpf(q23) * delta
    print("q_23 * (1 + log3/log2) =", mp.nstr(std_bound, 15), " 文献标准映射下界 355504839929 ->", abs(std_bound - 355504839929) < 0.5)
    print("q_23 * log2(3)         =", mp.nstr(acc_bound, 15), " 文献加速映射下界 217976794617 ->", abs(acc_bound - 217976794617) < 0.5)
    print()

    print("1536 * 2^60 =", 1536 * 2**60, " 3 * 2^69 =", 3 * 2**69, " 相等 ->", 1536 * 2**60 == 3 * 2**69)
    print("2^71 =", 2**71, " 2048 * 2^60 =", 2048 * 2**60, " 相等 ->", 2**71 == 2048 * 2**60)
    print("2075 * 2^60 =", 2075 * 2**60, " log2 =", mp.nstr(log(2075 * 2**60) / log(2), 8))
    print()

    print("Eliahou 周期形式的三个常数是否落在收敛分数分子里：")
    for target in (301994, 17087915, 85137581):
        hit = "未出现"
        for i, (p, q) in enumerate(conv):
            if p == target:
                hit = f"第 {i} 个收敛分数的分子（分母 {q}）"
        print(f"  {target}: {hit}")


if __name__ == "__main__":
    main()
