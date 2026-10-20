#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
"""Böhm 与 Sontacchi 环判据的形式核验（纯 Python，大整数精确）。

本脚本做三件事，全部用精确算术：
1. 用两套独立写法的 c 公式互相对表（求和公式与逐步递推公式）。
2. 对四个已知环（正整数上的 1、负整数上的 -1、-5、-17）用环判据
   x = c 除以 (2^k - 3^m) 反解出 x，并用加速映射 T 直接迭代核验。
3. 抽检：对随机奇偶向量，比较 c 两种算法，并核验 x 与向量的一致性。

加速映射取 T(n) = n/2（偶）、T(n) = (3n+1)/2（奇）。
约定：奇偶向量 eps[0..k-1]，eps[i] = 1 表示第 i 步是奇数步；
奇数步位置记作 0 = j_1 < j_2 < ... < j_m <= k-1（环从奇数项起，故 j_1 = 0）。
c = sum_{t=1..m} 3^(m-t) * 2^(j_t)。
"""
import random

def T(n):
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2

def c_sum(ones, k):
    """求和公式：ones 为奇数步位置（升序）列表。"""
    m = len(ones)
    return sum(3 ** (m - t) * 2 ** j for t, j in enumerate(ones, start=1))

def c_rec(ones, k):
    """逐步递推公式（Halbeisen 与 Hungerbühler 的 phi 递推）：
    从左到右扫向量，遇到 0 不变，遇到 1 做 c <- 3c + 2^p。"""
    c = 0
    oneset = set(ones)
    for p in range(k):
        if p in oneset:
            c = 3 * c + 2 ** p
    return c

def trajectory(n, steps):
    x = n
    out = [x]
    for _ in range(steps):
        x = T(x)
        out.append(x)
    return out

def main():
    print("=" * 72)
    print("Böhm 与 Sontacchi 环判据形式核验")
    print("=" * 72)

    # --- 1. 已知环 --------------------------------------------------------
    known = [
        ("正整数环 {1}",        [0, 1],        2, 1),
        ("负整数环 {-1}",       [0],           1, 1),
        ("负整数环 {-5,-7,-10}", [0, 1],        3, 2),
        ("负整数环 {-17 那一族}", None,         None, None),  # 下面自动求
    ]

    print("\n[1] 四个已知环：用判据反解 x = c / (2^k - 3^m) 并核验")
    # 手工给定的几个短环。
    # 注意：ones 是「奇数步位置」，对 1 -> 2 -> 1 向量为 (1,0)，奇数步只有位置 0。
    cases = []
    cases.append(("正整数环 1 -> 2 -> 1", [0], 2, 1))
    cases.append(("负整数环 -1 -> -1", [0], 1, 1))
    cases.append(("负整数环 -5 -> -7 -> -10 -> -5", [0, 1], 3, 2))
    cases.append(("不动点 0 -> 0", [], 1, 0))

    # -17 那一族：从 -17 出发，走加速映射直到回到 -17，记录奇数步位置
    start = -17
    traj = [start]
    x = start
    for _ in range(200):
        x = T(x)
        traj.append(x)
        if x == start:
            break
    k = len(traj) - 1
    ones = [i for i in range(k) if traj[i] % 2 != 0]
    m = len(ones)
    cases.append(("负整数环 从 -17 起的加速环", ones, k, m))
    print(f"    从 -17 起加速环长 k = {k}，奇数步数 m = {m}")
    print(f"    环元素（加速）：{traj[:k]}")
    print(f"    奇数步位置：{ones}")

    ok_all = True
    for name, ones, k, m in cases:
        c1 = c_sum(ones, k)
        c2 = c_rec(ones, k)
        D = 2 ** k - 3 ** m
        assert c1 == c2, (name, c1, c2)
        assert D != 0, (name, "2^k = 3^m 不可能，但被触发了")
        q, r = divmod(c1, D)
        integral = (r == 0)
        xval = q if integral else None
        # 直接迭代核验
        ver = None
        if integral:
            t = trajectory(xval, k)
            ver = (t[-1] == xval)
        sign = "2^k > 3^m（正解条件）" if D > 0 else "2^k < 3^m（负解）"
        print(f"  {name}:")
        print(f"    k = {k}, m = {m}, 2^k - 3^m = {D}  [{sign}]")
        print(f"    c（求和）= {c1}")
        print(f"    c（递推）= {c2}  （两法一致：{c1 == c2}）")
        print(f"    x = c/(2^k-3^m) = {q} 余 {r}  整数解：{integral}")
        if ver is not None:
            print(f"    判据给出的 x = {xval}，直接迭代 T^{k} 后回到自身：{ver}")
            if not ver:
                ok_all = False
        else:
            ok_all = False
        if integral and ver is None:
            ok_all = False

    print(f"\n    四个已知环全部由同一判据复现：{ok_all}")

    # --- 2. 随机向量抽检（两套 c 公式） -----------------------------------
    print("\n[2] 随机奇偶向量抽检：两套 c 公式是否逐位一致（k <= 60）")
    rnd = random.Random(20261018)
    bad = 0
    for _ in range(20000):
        k = rnd.randint(1, 60)
        vec = [rnd.randint(0, 1) for _ in range(k)]
        vec[0] = 1
        ones = [i for i in range(k) if vec[i] == 1]
        if c_sum(ones, k) != c_rec(ones, k):
            bad += 1
    print(f"    20000 个随机向量中两法不一致的个数：{bad}")

    # --- 3. 判据的充分性抽检（按向量构造 x，核验 T^k(x) = x） -------------
    print("\n[3] 充分性抽检：对随机向量，若 (2^k - 3^m) 整除 c 则 x 必是 k 步环点")
    tested = 0
    found = 0
    for _ in range(400000):
        k = rnd.randint(1, 24)
        vec = [0] * k
        vec[0] = 1
        for i in range(1, k):
            vec[i] = rnd.randint(0, 1)
        ones = [i for i in range(k) if vec[i] == 1]
        m = len(ones)
        D = 2 ** k - 3 ** m
        c = c_sum(ones, k)
        tested += 1
        if c % D == 0:
            x = c // D
            found += 1
            t = trajectory(x, k)
            assert t[-1] == x, ("充分性失败", vec, x)
            # 顺带核验奇偶向量确实一致
            par = [1 if t[i] % 2 != 0 else 0 for i in range(k)]
            assert par == vec, ("奇偶向量不一致", vec, par, x)
    print(f"    抽检向量数：{tested}，其中整除命中 {found} 个，全部通过 T^k(x)=x 与奇偶一致性核验")

    # --- 4. 已知环在 (k, m) 平面上落在哪一侧 -----------------------------
    print("\n[4] 正负两侧的分界（2^k 与 3^m 的大小）")
    for name, ones, k, m in cases:
        D = 2 ** k - 3 ** m
        print(f"    {name}: k = {k}, m = {m}, 2^k = {2**k}, 3^m = {3**m}, "
              f"{'2^k > 3^m' if D > 0 else '2^k < 3^m'}")
    print("\n结论：负数环恰好落在 2^k < 3^m 一侧；判据 x = c/(2^k-3^m) 对两侧同一形式，")
    print("      因此「阳性对照」只需去掉 2^k > 3^m 这一条对正解的限制。")

if __name__ == "__main__":
    main()
