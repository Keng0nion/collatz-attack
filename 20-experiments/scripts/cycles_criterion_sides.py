#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
"""单侧窗口版判据：把正、负两侧分开，各自用单侧逼近窗口，得到 M+ 与 M-。

推导（本工作自推，常数在已知环上核验过）：

  设环长度 k、奇数步 m 步、环上元素绝对值最小者是 X*，并设 X0 是「已核验界」：
  正侧 = 凡 1 <= n < X0 都到达 1；负侧 = 凡 |n| < Y0 的负整数都到达三个已知负环之一。

  环方程乘积式 2^k = prod_i (3 + 1/x_i) 取对数：
        Lambda := k*ln2 - m*ln3 = sum_i ln(1 + 1/(3 x_i)).
  正环（x_i > 0）时 Lambda > 0（因为 2^k = prod(3+1/x_i) > 3^m），且
        Lambda <= sum_i 1/(3 x_i - 1) <= m/(3 X0 - 1).
  负环（x_i < 0）时 Lambda < 0（prod(3+1/x_i) < 3^m），且
        |Lambda| <= sum_i 1/(3|x_i| - 1) <= m/(3 Y0 - 1).

  记 delta = log2 3、w = 1/((3 X0 - 1) ln2)。则 Lambda = m ln2 (k/m - delta)，于是

    正环：k/m 属于单侧窗口 (delta, delta + w]；等价于 1 - frac(m*delta) <= m*w
          （frac(m*delta) = m*delta - floor(m*delta)；m*delta 恒非整数，因 delta 无理）。
    负环：k/m 属于 [delta - w, delta)；等价于 frac(m*delta) <= m*w。

  于是排除判据分裂为两条（比用双侧距离 ||m*delta|| 更强）：
    排除「奇数步数为 m 的正环」 <=> 1 - frac(m*delta) > m*w
    排除「奇数步数为 m 的负环」 <=>     frac(m*delta) > m*w
  记 M+ = 使 m = 1..M+ 全部被正侧排除的最大 M+（同理 M-）。

用法：python cycles_criterion_sides.py <X0> [<X0> ...]
"""
import sys
import mpmath as mp

def frac(x):
    return x - mp.floor(x)

def run(X0, dps=60, mmax=2000000):
    mp.mp.dps = dps
    d = mp.log(3) / mp.log(2)
    w = 1 / ((mp.mpf(3) * X0 - 1) * mp.log(2))
    Mp = None      # 正侧第一个未被排除的 m
    Mn = None
    mp_min = None; mn_min = None
    for m in range(1, mmax + 1):
        fr = frac(m * d)
        rhs = m * w
        if Mp is None:
            ratio = (1 - fr) / rhs
            if ratio <= 1:
                Mp = m
            elif mp_min is None or ratio < mp_min[0]:
                mp_min = (ratio, m)
        if Mn is None:
            ratio = fr / rhs
            if ratio <= 1:
                Mn = m
            elif mn_min is None or ratio < mn_min[0]:
                mn_min = (ratio, m)
        if Mp is not None and Mn is not None:
            break
    return Mp, Mn, mp_min, mn_min

def main():
    xs = [int(a) for a in sys.argv[1:]] or [10**10]
    print("单侧窗口版判据：不存在奇数步数 <= M 的环（正侧用 M+，负侧用 M-）")
    print(f"{'X0':>18} {'M+ (正环)':>14} {'首个未排除 m':>12} {'M- (负环)':>14} "
          f"{'首个未排除 m':>12} {'最小余量(正)':>12} {'最小余量(负)':>12}")
    for X0 in xs:
        Mp, Mn, mp_min, mn_min = run(X0)
        print(f"{X0:>18} {('>'+str(Mp-1)) if Mp else '?':>14} {str(Mp):>12} "
              f"{('>'+str(Mn-1)) if Mn else '?':>14} {str(Mn):>12} "
              f"{mp.nstr(mp_min[0], 6) if mp_min else '-':>12} "
              f"{mp.nstr(mn_min[0], 6) if mn_min else '-':>12}")
        # 精度稳定性：200 位复算，只看两个首个未排除的 m 是否相同
        Mp2, Mn2, _, _ = run(X0, dps=200)
        if (Mp, Mn) != (Mp2, Mn2):
            print(f"    ！！精度不一致：60 位 ({Mp},{Mn}) vs 200 位 ({Mp2},{Mn2})")

if __name__ == "__main__":
    main()
