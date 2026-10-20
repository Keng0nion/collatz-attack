#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
"""台阶代价表：把「判据能排除到多大的奇数步数 m」与「需要多大的验证界 X0」对表。

规则（单侧窗口版，推导见 cycles_criterion_sides.py 的 docstring）：
  排除奇数步数 m 的正环   <=>  1 - frac(m*delta) > m / ((3 X0 - 1) ln2)
  排除奇数步数 m 的负环   <=>      frac(m*delta) > m / ((3 X0 - 1) ln2)

给定 X0，正侧上界 M+(X0) = min{m : 1 - frac(m*delta) <= m*w} - 1，其中 w = 1/((3X0-1)ln2)。
反解：要让 m 被排除，需要 X0 > (m/((1-frac(m*delta))*ln2) + 1)/3（正侧）。
于是「M+ >= m」所需的 X0 是所有 m' <= m 里最难排除者的代价。

本脚本用双精度先筛出 frac 靠近 0 或 1 的候选 m（只有这些会当台阶），
再用 mpmath 高精度算出精确门槛，输出台阶表与若干量级的代价。

前置条件：m 若已 ≥ 某个收敛项/半收敛项分母，其 frac(m*delta) 可能极小。
用法：python cycles_criterion_cost.py <Mmax>
"""
import sys
import mpmath as mp

def candidates(Mmax, thresh=1e-4):
    """用双精度筛：||m*delta|| < 1/2 - 接近 1 或 0 的 m。返回候选 m 列表。"""
    # delta 的双精度近似足够筛分数（筛完再用高精度复核）
    d = 1.5849625007211561814537389439478165087598144076924811
    cands = []
    for m in range(2, Mmax + 1):
        fr = m * d
        fr = fr - int(fr)
        if fr < thresh or 1 - fr < thresh:
            cands.append(m)
    return cands

def mdelta_frac(m, dps=60):
    mp.mp.dps = dps + 20
    d = mp.log(3) / mp.log(2)
    x = m * d
    return x - mp.floor(x)

def main():
    Mmax = int(sys.argv[1]) if len(sys.argv) > 1 else 2000000
    print(f"台阶代价表（单侧窗口版判据），扫描 m 到 {Mmax}")
    cands = candidates(Mmax)
    print(f"双精度初筛出的候选台阶 m 个数：{len(cands)}（这些 m 的 frac(m*delta) 贴近 0 或 1）")

    # 对每个候选算正侧与负侧门槛
    rows = []
    for m in cands:
        fr = mdelta_frac(m, 60)
        ln2 = mp.log(2)
        # 正侧：需 1 - fr > m/((3X0-1) ln2)  =>  X0 > (m/((1-fr)ln2) + 1)/3
        need_p = (mp.mpf(m) / ((1 - fr) * ln2) + 1) / 3
        need_n = (mp.mpf(m) / (fr * ln2) + 1) / 3
        rows.append((m, fr, need_p, need_n))

    # 累计台阶：要让 M+ >= m，需 X0 超过所有 m' <= m 的正侧门槛
    best_p = mp.mpf(0); best_n = mp.mpf(0)
    print(f"\n{'m':>14} {'frac(m*delta)':>16} {'X0_min(正侧)':>20} {'X0_min(负侧)':>20}")
    for (m, fr, need_p, need_n) in rows:
        best_p = max(best_p, need_p)
        best_n = max(best_n, need_n)
        print(f"{m:>14} {mp.nstr(fr, 8):>16} {mp.nstr(need_p, 8):>20} {mp.nstr(need_n, 8):>20}")

    print("\n累计代价（要把正/负两侧的排除范围推到某个 m，需要多大的 X0）：")
    cum_p = []; cum_n = []
    bp = mp.mpf(0); bn = mp.mpf(0)
    for (m, fr, need_p, need_n) in rows:
        bp = max(bp, need_p); bn = max(bn, need_n)
        cum_p.append((m, bp)); cum_n.append((m, bn))
    for scale in [10**4, 10**5, 10**6, 10**7, 10**8]:
        for (m, v) in cum_p:
            if m >= scale:
                print(f"  正侧达到 m >= {scale:.0e}：需要 X0 > {mp.nstr(v, 6)}（台阶在 m = {m}）")
                break
        for (m, v) in cum_n:
            if m >= scale:
                print(f"  负侧达到 m >= {scale:.0e}：需要 X0 > {mp.nstr(v, 6)}（台阶在 m = {m}）")
                break

if __name__ == "__main__":
    main()
