#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
"""独立复核 cycles_bs_enum 输出的每一条解，并去重成「不同的环」。

复核内容（全部用 Python 大整数，与 C 程序完全独立的实现）：
1. 由 ones 重算 c = sum_t 3^(m-t) * 2^(j_t)，与 C 打印的 c 对表。
2. 检查 D = 2^k - 3^m 与 x = c / D（整除）。
3. 从 x 出发迭代加速映射 T，核验：k 步内回到 x；记实际周期 d；核对轨迹的奇偶向量
   与 ones 的前 d 位一致；核对 d 整除 k（x 是 k 周期点）。
4. 去重：同一族环的旋转与重复全部归并，输出「不同的环」清单。

用法：
  python cycles_solutions_verify.py <enum输出文件> [--json 输出摘要]
"""
import sys
import re
from collections import defaultdict

def T(n):
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2

def c_sum(ones):
    m = len(ones)
    return sum(3 ** (m - t) * 2 ** j for t, j in enumerate(ones, start=1))

SOL_RE = re.compile(r"^SOL k=(\d+) m=(\d+) x=(-?\d+) c=(\d+) D=(-?\d+) ones=(.*)$")

def main():
    path = sys.argv[1]
    lines = [l.rstrip("\n") for l in open(path, encoding="utf-8") if l.startswith("SOL")]
    # 每个 k 的统计行
    stat = {}
    for l in open(path, encoding="utf-8"):
        mm = re.match(r"^# k=(\d+) nodes=(\d+) leaves=(\d+) hits=(\d+) sec=([\d.]+)", l)
        if mm:
            stat[int(mm.group(1))] = (int(mm.group(2)), int(mm.group(3)), int(mm.group(4)), float(mm.group(5)))

    print(f"读入解行数：{len(lines)}")
    print(f"覆盖 k：{min(stat)} .. {max(stat)}")

    errs = []
    per_k = defaultdict(int)
    cycles = {}      # key = (min_element, period) -> 信息
    for l in lines:
        mm = SOL_RE.match(l)
        if not mm:
            errs.append(("解析失败", l)); continue
        k, m, x, c, D, ones_s = mm.groups()
        k, m, x, c, D = int(k), int(m), int(x), int(c), int(D)
        ones = [int(t) for t in ones_s.split(",")] if ones_s else []
        per_k[k] += 1
        # 1. c 重算
        if c_sum(ones) != c:
            errs.append(("c 不一致", l, c_sum(ones))); continue
        # 2. D 与整除
        if D != 2 ** k - 3 ** m:
            errs.append(("D 不一致", l)); continue
        if len(ones) != m:
            errs.append(("m 与 ones 长度不一致", l)); continue
        if c % D != 0 or x != c // D:
            errs.append(("x 与 c/D 不一致", l)); continue
        # 3. 迭代核验
        traj = [x]
        for _ in range(k):
            traj.append(T(traj[-1]))
        if traj[k] != x:
            errs.append(("T^k(x) != x", l)); continue
        # 实际周期
        d = None
        for i in range(1, k + 1):
            if traj[i] == x:
                d = i; break
        if d is None:
            errs.append(("找不到周期", l)); continue
        if k % d != 0:
            errs.append(("d 不整除 k", l)); continue
        # 奇偶向量一致：ones 是「奇数步位置」列表，与轨迹的奇偶位向量对表
        par = [1 if traj[i] % 2 != 0 else 0 for i in range(d)]
        oneset = set(ones)
        par_exp = [1 if i in oneset else 0 for i in range(d)]
        if par != par_exp:
            errs.append(("奇偶向量不一致", l, par, par_exp)); continue
        # 去重
        elems = tuple(sorted(traj[:d]))
        key = (min(traj[:d]), d)
        if key not in cycles:
            cycles[key] = {"elems": elems, "period": d, "minabs": min(abs(v) for v in elems),
                           "maxabs": max(abs(v) for v in elems), "count": 0, "ks": set()}
        cycles[key]["count"] += 1
        cycles[key]["ks"].add(k)

    print(f"\n复核失败条目数：{len(errs)}")
    for e in errs[:10]:
        print("  ", e)

    print(f"\n不同环的个数：{len(cycles)}")
    print(f"{'最小元':>12} {'周期':>5} {'最小|元素|':>10} {'最大|元素|':>12} {'出现次数':>8}  元素")
    for key in sorted(cycles, key=lambda t: (t[1], t[0])):
        info = cycles[key]
        el = info["elems"]
        el_s = ",".join(str(v) for v in el) if len(el) <= 40 else f"{el[0]},...,{el[-1]}（{len(el)} 个）"
        print(f"{key[0]:>12} {info['period']:>5} {info['minabs']:>10} {info['maxabs']:>12} "
              f"{info['count']:>8}  {el_s}")

    print("\n按 k 统计（节点数、叶子数、整除命中数、用时）")
    for k in sorted(stat):
        n, lf, h, sec = stat[k]
        print(f"  k={k:>2} 节点={n:>12} 叶子={lf:>12} 命中={h:>4} 用时={sec:>8.3f}s")

    # 关键断言
    print("\n[断言] 在 k <= 34 的完整枚举里，非平凡环只应出现负整数上的三个：")
    nontrivial = [key for key in cycles if not (key[1] == 1 and key[0] == 0)]
    for key in sorted(nontrivial, key=lambda t: t[1]):
        info = cycles[key]
        print(f"  最小元 {key[0]:>8}, 周期 {info['period']:>3}, 元素 {info['elems']}")

if __name__ == "__main__":
    main()
