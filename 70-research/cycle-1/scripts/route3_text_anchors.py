"""route-3 原文读法溯源：锚点自检与文本侧数值核对。

纪律（本文件遵守）：先定死定义（每条注一手出处），再计算；用已钉住的数字自检；
不 import 任何项目脚本；不用印出版的被否证步骤。

一手原件（本次亲自 curl 下载并 md5 核对，副本在 /tmp/r3/）：
  corr.pdf    勘误，2 页，    md5 f23d5f969116cb1af6e9b981b4b3ba7a
  h5.pdf      JIS 26 (2023) 文章 23.3.5，22 页，md5 3e2377bef0b1c0435dc455c9bbee43a1
  sidw144.pdf SdW v1.44（2010），17 页，md5 696d4ff4b6f3f4036bac3892aa9cd968
行号一律以本次 pdftotext -layout 抽出的 /tmp/r3/*.txt 为准（corr 88 行、h5 1256 行、
sidw144 1067 行，与 materials.md 记录一致）。
"""
from mpmath import mp, mpf, log, power, floor

mp.dps = 80

print("=" * 78)
print("第 0 节：定义（先定义后计算）")
print("=" * 78)

# D1  delta := log 3 / log 2   [h5.txt:506 Definition 15；sidw144.txt:130-131]
delta = log(3) / log(2)

# D2  X0 := 695 * 2^60         [h5.txt:80-83 Definition 4]
X0 = mpf(695) * power(2, 60)

# D3  c := log((162/97) X0)/log 2   [h5.txt:698-703 Theorem 21 假设中的常数]
c = log(mpf(162) / 97 * X0) / log(2)


# D4  v(m2, m, K) := (m2/m) * K * (delta-1)/(delta^m2 - 1)
#     出处：corr.txt:69-72 与 h5.txt:705-706
def v_of(m2, m, K):
    return (mpf(m2) / m) * K * (delta - 1) / (power(delta, m2) - 1)


# D5  K_up 两段常数  [sidw144.txt:262-275 Theorem 3(d)]
def K_up(m):
    if 78 <= m <= 90:
        return mpf("1.3993") * m * power(delta, m)
    if 91 <= m <= 515619:
        return mpf("1.4784") * m * power(delta, m)
    return None


# D6  S(y) := sum_j 3/(2^{y_j} - 1)   [corr.txt:35-40]
def S(coords):
    return sum(3 / (power(2, y) - 1) for y in coords)


# D7  b^delta := (1/2) * (1 + 1/X0)^delta   [sidw144.txt:444-445, 454-455, 468]
bdelta = mpf(1) / 2 * power(1 + 1 / X0, delta)

print(f"D1 delta        = {mp.nstr(delta, 50)}")
print(f"D2 X0           = {mp.nstr(X0, 25)}   (= 695*2^60)")
print(f"D3 c            = {mp.nstr(c, 25)}")
print(f"D7 b^delta      = {mp.nstr(bdelta, 25)}")

print()
print("=" * 78)
print("第 1 节：锚点自检（与项目已钉住的数字比，按有效位数判）")
print("=" * 78)

ok = True


def anchor(name, got, want_str, digits):
    """判据：|got-want|/|want| < 10^{-(digits-1)}，即前 digits 位有效数字一致。"""
    global ok
    want = mpf(want_str)
    rel = abs(got - want) / abs(want)
    good = rel < power(10, -(digits - 1))
    ok &= bool(good)
    agree = "inf" if rel == 0 else str(int(floor(-mp.log10(rel))))
    print(f"[{'PASS' if good else 'FAIL'}] {name}")
    print(f"        got  = {mp.nstr(got, digits + 4)}")
    print(f"        want = {want_str}")
    print(f"        相对误差 = {mp.nstr(rel, 5)}（约一致 {agree} 位）")


anchor("delta 前 40 位（materials.md:339）", delta,
       "1.58496250072115618145373894394781650875981440769248106045575", 40)
anchor("c（materials.md:345）", c, "70.180806328308366825", 20)

Klo91 = mpf("7941964418702608664581")          # margin-table.txt:81 的 K 下界
KU91 = K_up(91)
anchor("K_up(91)（materials.md:343）", KU91, "214072842063828923281.3586", 25)
anchor("余量 91 = K_lo/K_up（materials.md:344）", Klo91 / KU91,
       "37.09935525747164492758953", 25)

anchor("v(47,91,7e11)（materials.md:340）", v_of(47, 91, mpf("7e11")),
       "84.02140326164773718764214", 22)
anchor("v(47,92,7.5311e11)（materials.md:341）", v_of(47, 92, mpf("7.5311e11")),
       "89.41365947118846256456601", 22)
anchor("v(47,91,7.5311e11)（materials.md:342）", v_of(47, 91, mpf("7.5311e11")),
       "90.39622715768503907626453", 22)

print()
print("=" * 78)
print("第 2 节：SdW 的对应引理是否提供「delta 链接」这一步")
print("=" * 78)
print("SdW Lemma 6（sidw144.txt:454-455，200 dpi 渲染图核对）：")
print("  For all i = 0,1,...,m-1 we have x_{i+1} < b^delta * x_i^delta.")
print("其证明末行（sidw144.txt:468）：x_{i+1} < (1/2)(x_i+1)^delta")
print("  <= (1/2)(1+X0^{-1})^delta x_i^delta = b^delta x_i^delta。")
print("Hercher Lemma 20（h5.txt:674-675）：n_{i+1} < n_i^delta。")
print(f"实测 b^delta = {mp.nstr(bdelta, 25)}")
print(f"b^delta < 1 ? {bdelta < 1}     （b^delta 略大于 1/2：{bdelta > mpf('0.5')}）")
print("→ 判定：x_{i+1} < b^delta x_i^delta 且 b^delta < 1 ⟹ x_{i+1} < x_i^delta，")
print("  即 SdW Lemma 6 蕴含 Hercher Lemma 20（常数处更强），且两文都注明循环成立")
print("  （sidw144.txt:471 'holds cyclically'；h5.txt:693 同注）。")

print()
print("=" * 78)
print("第 3 节：印出版假不等式（只作对照，不用于任何推导）")
print("=" * 78)
print("h5.txt:799 印出的式子：n_{m-m2+1+l} < n^{(delta^l)} <= n^{delta}")
print("第二式的方向：delta^l > delta（l >= 2）且 n > 1 → n^{delta^l} > n^delta，故印出者假。")
for n_exp in (70, 91):
    n = power(2, n_exp)
    ratio = power(n, power(delta, 2) - delta)
    print(f"  n = 2^{n_exp}: n^(delta^2)/n^delta = 2^{mp.nstr((power(delta,2)-delta)*n_exp, 8)}"
          f" = {mp.nstr(ratio, 8)}")
print("→ l = 2 处被违反的倍数如上（仅作对照，本轮不据此步做任何推断）。")

print()
print("=" * 78)
print("第 4 节：勘误替换式的方向核对 2^{delta v} - 1 > (2^v - 1)^delta")
print("=" * 78)
print("出处：corr.txt:79-82。令 w = 2^v - 1，要证 (w+1)^delta - 1 > w^delta。")
for vv in (c, v_of(47, 91, mpf("7e11")), v_of(47, 92, mpf("7.5311e11"))):
    w = power(2, vv) - 1
    lhs = power(2, delta * vv) - 1
    rhs = power(w, delta)
    print(f"  v = {mp.nstr(vv, 12):>16}")
    print(f"       (w+1)^delta - w^delta = {mp.nstr(lhs - rhs, 8)}  (> 1 ? {lhs - rhs > 1})")

print()
print("=" * 78)
print("第 5 节：Theorem 21 假设里被省略的桥（c > 1）")
print("=" * 78)
print("Theorem 21 假设（h5.txt:698-703）：(delta^{m2}-1)/(delta-1) * c <= (m2/m) K")
print("勘误 :50-53 用的是：(delta^{m2}-1)/(delta-1) < (m2/m) K")
print(f"桥 = c > 1；实测 c = {mp.nstr(c, 25)} > 1 ? {c > 1}")
print("→ 该步成立，其未写出的桥是 c = log2((162/97)X0) > 1。")

print()
print("=" * 78)
print("第 6 节：读法反例——Sigma k 极大性不蕴含回绕前提")
print("=" * 78)
# 形式约束系统（不是真实环：真实环不存在）：
#   x_i 实正数，链约束 x_{i+1} <= delta x_i（循环）；k_i 正整数且 k_i <= x_i；
#   Theorem 21 的假设在 m2 处成立。
m_t, m2_t = 4, 2
xs = [mpf(x) for x in (200, 300, 320, 250)]
ks = [1, 1, 300, 240]
print(f"m = {m_t}, m2 = {m2_t}, x = {[int(v) for v in xs]}, k = {ks}")
print(f"k_i <= x_i（逐点）? {all(k <= x for k, x in zip(ks, xs))}")
print(f"链约束 x_(i+1) <= delta x_i（循环）? "
      f"{all(xs[(i + 1) % m_t] <= delta * xs[i] for i in range(m_t))}")
K_t = sum(ks)
hyp_lhs = (power(delta, m2_t) - 1) / (delta - 1) * c
hyp_rhs = mpf(m2_t) / m_t * K_t
print(f"Theorem 21 假设：(delta^m2-1)/(delta-1)*c = {mp.nstr(hyp_lhs, 8)}"
      f" <= (m2/m)K = {hyp_rhs} ? {hyp_lhs <= hyp_rhs}")
win_k = [(sum(ks[(s + j) % m_t] for j in range(m2_t)), s) for s in range(m_t)]
win_x = [(sum(xs[(s + j) % m_t] for j in range(m2_t)), s) for s in range(m_t)]
print(f"各窗 Sigma k（窗起点 s）：{[(t, s) for t, s in win_k]}")
print(f"各窗 Sigma x（窗起点 s）：{[(mp.nstr(t, 8), s) for t, s in win_x]}")
sk_max = [s for t, s in win_k if t == max(t for t, _ in win_k)]
sx_max = [s for t, s in win_x if t == max(t for t, _ in win_x)]
print(f"Sigma k 唯一最大的窗起点：{sk_max}；Sigma x 唯一最大的窗起点：{sx_max}")
s_k = sk_max[0]
win_idx = [(s_k + j) % m_t for j in range(m2_t)]
prev_idx = (s_k - 1) % m_t
print(f"取 Sigma k 最大窗（起点 {s_k}，指标 {win_idx}）：")
print(f"  回绕前提 x_(前一指标) <= x_(窗末指标)："
      f"{mp.nstr(xs[prev_idx], 8)} <= {mp.nstr(xs[win_idx[-1]], 8)} ? "
      f"{xs[prev_idx] <= xs[win_idx[-1]]}")
s_x = sx_max[0]
win_idx_x = [(s_x + j) % m_t for j in range(m2_t)]
prev_idx_x = (s_x - 1) % m_t
print(f"取 Sigma x 最大窗（起点 {s_x}，指标 {win_idx_x}）：")
print(f"  该窗 Sigma x >= (m2/m)K ? {sum(xs[i] for i in win_idx_x) >= hyp_rhs}")
print(f"  回绕前提：{mp.nstr(xs[prev_idx_x], 8)} <= {mp.nstr(xs[win_idx_x[-1]], 8)} ? "
      f"{xs[prev_idx_x] <= xs[win_idx_x[-1]]}")
print("→ 判定：在这个形式约束系统内，Sigma k 极大性不蕴含回绕前提；Sigma x 极大性蕴含它。")
print("  限定：本反例是关于「蕴含式是否成立」的，不是关于真实环的（真实环不存在）；")
print("  构造落入自举实际参数区间（m <= 91、m2 >= 47）的同型反例属路线 2 的范围，本文件不主张。")

print()
print("=" * 78)
print("第 7 节：闭化无损的对称性核对（S 对称 + 两顶点互为循环置换）")
print("=" * 78)
print("V1：回绕约束为不活跃那条的顶点 → x_i = v*delta^{i-1}（i = 1..m2）")
print("V2：第一条链约束为不活跃的顶点   → x_i = v*delta^{(i-2) mod m2}（i = 1..m2）")
for (mm, mm2, KK) in ((91, 47, mpf("7.5311e11")), (91, 47, mpf("7e11"))):
    vv = v_of(mm2, mm, KK)
    V1 = [vv * power(delta, j) for j in range(mm2)]
    V2 = [vv * power(delta, (i - 1) % mm2) for i in range(mm2)]
    s1, s2 = S(V1), S(V2)
    w1 = V1[0] - delta * V1[-1]
    w2 = V2[0] - delta * V2[-1]
    tol = power(10, -60) * delta * V1[-1]
    print(f"m={mm} m2={mm2} K={KK}: v={mp.nstr(vv, 14)}")
    print(f"  S(V1) = {mp.nstr(s1, 20)}    S(V2) = {mp.nstr(s2, 20)}   相等 ? {s1 == s2}")
    print(f"  坐标集合相同（循环置换）? "
          f"{sorted(mp.nstr(y, 30) for y in V1) == sorted(mp.nstr(y, 30) for y in V2)}")
    print(f"  V1 回绕余量 v - delta*x_m2 = {mp.nstr(w1, 8)}（<0 即严格满足）? {w1 < 0}")
    print(f"  V2 回绕余量 v - delta*x_m2 = {mp.nstr(w2, 8)}"
          f"（精确为 0；此处 |值| < 容差 {mp.nstr(tol, 3)}）? {abs(w2) < tol}")
print("→ 判定：S 对称，两顶点的坐标互为循环置换，故 S 取值相同（数值上逐位相等）；")
print("  「回绕约束为不活跃那条」的顶点严格可行，故这个最大值取值在严格可行集内取到。")

print()
print("=" * 78)
print(f"总体锚点自检：{'全部通过' if ok else '有未通过项'}")
print("=" * 78)
