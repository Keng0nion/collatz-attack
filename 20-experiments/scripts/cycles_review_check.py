#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
"""复核意见核验：两处表述口径错误的独立复算（2026 年 10 月 19 日，按复核员意见）。

复核点一：判据的排除上界（M+、M−）带前提「环上元素绝对值至少 X0」。
    本脚本枚举已知五个环的 (k, m, |x_min|)，检查它们是否落在前提内；
    若不在前提内而写成「不存在奇数步数 <= M± 的环」，就会与已知环直接矛盾。
复核点二：百分比基准。比较本工作跨台阶所需验证界（9.84573e11）
    与文献门槛 2^40 = 1099511627776 时，「高」与「低」的分母不同。

用法：python cycles_review_check.py
"""
import mpmath as mp

def main():
    mp.mp.dps = 40
    print("=" * 74)
    print("复核点一：判据排除上界的前提")
    print("=" * 74)
    Mp, Mn = 10781273, 5446237          # X0 = Y0 = 10^12 下的精确值
    X0 = 10 ** 12
    known = [("{1,2}（平凡正环）", 2, 1, 1), ("{-1}", 1, 1, 1), ("{-5,-7,-10}", 3, 2, 5),
             ("{-17 族}", 11, 7, 17), ("{0}（不动点）", 1, 0, 0)]
    print(f"M+ = {Mp}，M- = {Mn}（X0 = Y0 = 10^12）")
    print(f"{'环':>18} {'k':>3} {'m':>3} {'|x_min|':>8} {'m<=M+':>7} {'m<=M-':>7} {'|x_min|>=10^12':>15}")
    for name, k, m, xm in known:
        print(f"{name:>18} {k:>3} {m:>3} {xm:>8} {str(m <= Mp):>7} {str(m <= Mn):>7} {str(xm >= X0):>15}")
    print()
    print("结论：已知五个环的 m 全部 <= M+ 与 M-，且它们的 |x_min| 全部远小于 10^12，")
    print("      因此「不存在奇数步数 <= M± 的环」若不加前提就是错的；")
    print("      正确写法是「在 |x| >= X0（即已知环之外）的前提下」。")
    print("      判据推导（§2.5 的 X* >= X0 一步）与判据脚本 [4] 节都带了这个前提，")
    print("      是 findings 正文的口径漏写，不是计算错误。")

    print()
    print("=" * 74)
    print("复核点二：百分比基准")
    print("=" * 74)
    mine = mp.mpf("9.84573e11")     # cycles_criterion_cost.py 输出的台阶门槛
    lit = mp.mpf(2) ** 40
    print(f"本工作门槛 = {mp.nstr(mine, 12)}")
    print(f"文献门槛   = {mp.nstr(lit, 12)}（2^40）")
    print(f"文献/本工作 = {mp.nstr(lit / mine, 8)}  => 文献门槛比本工作高 {mp.nstr((lit - mine) / mine * 100, 6)} %")
    print(f"本工作/文献 = {mp.nstr(mine / lit, 8)}  => 本工作比文献低 {mp.nstr((lit - mine) / lit * 100, 6)} %")
    print()
    print("结论：写「本工作比文献低约 12%」用了「高」的分母（11.674%），是错的；")
    print("      正确说法是「文献门槛比本工作高约 11.67%」或「本工作比文献低约 10.45%」。")

if __name__ == "__main__":
    main()
