"""独立验算 II：指数换算，以及「固定深度下降证书不存在」这一屏障的验证。

这一段屏障是死路清单里最有用的一条，因为很多人会不自觉地想用「有限个剩余类加
固定步数下降」去证明猜想。屏障的机理是：取 k 大于步数上限，则 n 同余 -1 模 2^k
的那一整类数，前 k 步全是奇数步且严格上升，所以任何固定步数的下降证书都盖不住它。

本脚本做两件事：
1. 用精确整数验证上面的机理（加速映射 T(x) = (3x+1)/2 对奇数，n = m*2^k - 1），
   对 k = 1..24 与若干乘数 m 逐一检查三条：每一步的输入都是奇数；序列严格递增；
   闭式 n_j = 3^j * m * 2^(k-j) - 1 与实际迭代完全一致。
2. 核对边界地图里三个由对数定义的门槛数字。

运行方式：
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
      40-formal/independent-checks/barrier_and_exponents.py
"""

from mpmath import mp, log

mp.dps = 50


def accelerated(x):
    """加速映射：x 为奇数时返回 (3x+1)/2；这里只用于奇数输入。"""
    assert x % 2 == 1, f"输入不是奇数：{x}"
    return (3 * x + 1) // 2


def check_barrier(k, m):
    """对 n = m*2^k - 1 验证前 k 步全为奇数步、严格递增、且与闭式一致。"""
    n = m * (2**k) - 1
    cur = n
    prev = None
    for j in range(k):
        if cur % 2 == 0:
            return f"k={k} m={m} 第 {j} 步输入为偶数，屏障命题不成立"
        closed = 3**j * m * 2 ** (k - j) - 1
        if cur != closed:
            return f"k={k} m={m} 第 {j} 步闭式不符：实际 {cur} 闭式 {closed}"
        if prev is not None and not cur > prev:
            return f"k={k} m={m} 第 {j} 步未严格递增：{prev} -> {cur}"
        prev = cur
        cur = accelerated(cur)
    return None


def main():
    print("== 一、屏障命题的精确验证 ==")
    bad = []
    total = 0
    for k in range(1, 25):
        for m in (1, 2, 3, 5, 7, 12345, 10**18 + 7):
            total += 1
            msg = check_barrier(k, m)
            if msg is not None:
                bad.append(msg)
    print(f"检查组合数：{total}；失败：{len(bad)}")
    for msg in bad[:5]:
        print("  ", msg)
    print("样例（k=20, m=1）：n = 2^20 - 1 =", 2**20 - 1)
    cur = 2**20 - 1
    seq = [cur]
    for _ in range(20):
        cur = accelerated(cur)
        seq.append(cur)
    print("  加速映射前 6 个值：", seq[:6])
    print("  第 20 步的值：", seq[20], "  闭式 3^20 - 1 =", 3**20 - 1, "  相符 ->", seq[20] == 3**20 - 1)
    print("  整段是否严格递增：", all(seq[i] < seq[i + 1] for i in range(len(seq) - 1)))
    print()

    print("== 二、指数与门槛换算 ==")
    gamma = log(mp.mpf("1.7922310")) / log(2)
    paper = mp.mpf("0.8417560")  # Krasikov 与 Lagarias 2003 表 2 的 k=11 值
    print("log_2(1.7922310) =", mp.nstr(gamma, 12))
    print("  论文表 2 的 k=11 值 = 0.8417560，与本次计算相差", mp.nstr(abs(gamma - paper), 3), "（落在第 7 位小数）")
    print("  边界地图写 ≈ 0.84175，属 5 位小数截断（四舍五入应写 0.84176）；实质无影响 ->", abs(gamma - mp.mpf("0.84175")) < mp.mpf("1e-4"))
    print("log_4(3) = log(3)/log(4) =", mp.nstr(log(3) / log(4), 10), " 边界地图写 0.7925 ->", abs(log(3) / log(4) - mp.mpf("0.7925")) < mp.mpf("5e-5"))
    allouche = mp.mpf(3) / 2 - log(2) / log(3)
    print("3/2 - log_3(2) =", mp.nstr(allouche, 10), " 边界地图写 0.8691 ->", abs(allouche - mp.mpf("0.8691")) < mp.mpf("5e-5"))
    print("log3/log2 =", mp.nstr(log(3) / log(2), 12), "（用于 q_23 的两个导出界）")
    print()
    print("== 三、结论 ==")
    if not bad:
        print("屏障命题在所检查的全部组合上成立；指数换算三处全部对上。")
    else:
        print("发现反例，需修订边界地图对应条目。")


if __name__ == "__main__":
    main()
