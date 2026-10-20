"""独立验算 IV：逆向树实验三个核心主张的独立复核（主代理自写，不复用实验的任何代码）。

被复核的主张（来自 20-experiments/findings/reverse-tree.md）：
1. 层结构定义：第 d 层 = {n : σ(n) = d}（σ 为加速映射下的总停时），根节点 1 只在第 0 层出现一次。
2. 结构性恒等式：第 d+1 层的奇数个数 = 第 d 层中 x ≡ 2 (mod 3) 的节点个数，唯一例外是 d = 1。
3. 覆盖上界：M(70) = 53、M(71) = 71、M(73) = 95、M(75) = 127；
   以及 σ(27) = 70、σ(31) = 67、σ(41) = 69、σ(47) = 66、σ(55) = 71。

第一版实现的错误与修正（保留在这段注释里，免得后来者重蹈）：
第一版没有做根节点去重。根 1 的第二个孩子是 (2·2-1)/3 = 1，所以 {1, 2} 这对会在朴素 BFS 里
无限再生，于是每层多带一个奇节点、节点数被放大到约 2.3 倍（第 24 层 1534 对报告的 665），
结构性恒等式也因此「看似」处处成立（多出来的那个奇节点正好补上了 d = 1 的缺口）。
修正方式：加全局 seen 集合，跳过已出现过的节点，使各层恰好等于 σ 的纤维。

运行：
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
      40-formal/independent-checks/reverse_tree_recheck.py
"""


def sigma(n):
    """加速映射下的总停时：n 走到 1 的步数（σ(1) = 0）。"""
    assert n >= 1
    steps = 0
    x = n
    while x != 1:
        x = x // 2 if x % 2 == 0 else (3 * x + 1) // 2
        steps += 1
        if steps > 100000:
            raise RuntimeError(f"停时超过安全上限：n={n}")
    return steps


def build_levels(depth):
    """带根去重的 BFS（分支：2x；x ≡ 2 (mod 3) 时还有 (2x-1)/3）。"""
    levels = [{1}]
    seen = {1}
    for _ in range(depth):
        nxt = set()
        for x in levels[-1]:
            nxt.add(2 * x)
            if x % 3 == 2:
                nxt.add((2 * x - 1) // 3)
        nxt -= seen
        seen |= nxt
        levels.append(nxt)
    return levels


def main():
    depth = 24
    levels = build_levels(depth)

    print("== 0. 自我校验：各层是否等于 σ 的纤维（这是实验给出的层定义）==")
    bad = 0
    checked = 0
    for d in range(0, depth + 1):
        for n in levels[d]:
            if n <= 200000:
                checked += 1
                if sigma(n) != d:
                    bad += 1
                    if bad <= 5:
                        print(f"  不一致：n={n} 在第 {d} 层，但 σ(n) = {sigma(n)}")
    print(f"  核对 {checked} 个节点，不一致 {bad} 个")
    print()

    print("== 1. 结构性恒等式核对 ==")
    exceptions = []
    for d in range(0, depth):
        left = sum(1 for x in levels[d + 1] if x % 2 == 1)
        right = sum(1 for x in levels[d] if x % 3 == 2)
        if left != right:
            exceptions.append(d)
        if d <= 6 or d >= depth - 3:
            print(f"  d={d:2d}  第 {d+1} 层奇数 {left:6d}   第 {d} 层 ≡2 mod 3 {right:6d}"
                  + ("  <-- 例外" if left != right else ""))
    print(f"  例外出现在 d = {exceptions if exceptions else '无'}（实验报告：唯一例外是 d = 1）")
    print()

    print("== 2. 与实验报告表格逐格对照（d = 8、16、24 三行）==")
    report = {8: (6, 1, 2), 16: (68, 18, 23), 24: (665, 160, 220)}
    for d in (8, 16, 24):
        n_all = len(levels[d])
        n_odd = sum(1 for x in levels[d] if x % 2 == 1)
        n_two = sum(1 for x in levels[d] if x % 3 == 2)
        exp = report[d]
        ok = (n_all, n_odd, n_two) == exp
        print(f"  d={d:2d}  我算 N={n_all:6d} 奇数={n_odd:5d} ≡2mod3={n_two:6d}"
              f"   报告 N={exp[0]:6d} 奇数={exp[1]:5d} ≡2mod3={exp[2]:6d}   {'一致' if ok else '不一致'}")
    const24 = len(levels[24]) / ((4 / 3) ** 24)
    print(f"  d=24 常数 = {const24:.6f}（报告表格 d=24 行为 0.667255）")
    last = [len(levels[d]) / len(levels[d - 1]) for d in range(depth - 8, depth + 1)]
    avg = sum(last) / len(last)
    print(f"  最后 9 层平均比值 = {avg:.6f}（报告在 d = 56 至 65 为 1.333347，本处深度只到 {depth}）")
    print()

    print("== 3. 覆盖上界与停时值独立重算 ==")
    for n in (27, 31, 41, 47, 53, 55, 71, 73, 95, 97, 127, 129, 871):
        print(f"  σ({n}) = {sigma(n)}")
    print()
    for D in (25, 70, 71, 73, 75, 113):
        m = 1
        n = 1
        while sigma(n) <= D:
            m = n
            n += 2
        print(f"  M({D}) = {m}（第一个缺席的奇数是 {n}，其停时 {sigma(n)}）")
    print("  实验报告的值：M(70)=53、M(71)=71、M(73)=95、M(75)=127；缺席者 55、73、97、129；")
    print("  以及「覆盖奇数到 1000 需深度 113，由 n = 871 达到」。")


if __name__ == "__main__":
    main()
