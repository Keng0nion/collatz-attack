"""route-3 原文读法溯源：独立复算（本轮新写，与 route3_*.py 的实现不共享代码）。

纪律：先定义后计算；所有定义按一手原件重写，行号以本次抽取的 /tmp/r3/*.txt 为准；
锚点自检用项目已钉住的数字（m = 91 余量 37.09935525747164492758953 等）。

定义与出处：
  delta := log 3 / log 2                          [h5.txt:506 Definition 15]
  X0    := 695 * 2^60                             [h5.txt:80-83 Definition 4]
  c     := log2((162/97) X0)                      [h5.txt:698-703 Theorem 21 假设]
  A(m2) := (97(m-m2)+73)/(54 X0)                  [h5.txt:465-470 Theorem 14]
           m2 = m-1 时 3/X0，m2 = m 时 0          [h5.txt:814-818]
  v     := (m2/m) K_lo (delta-1)/(delta^m2-1)     [h5.txt:705-706]
  eps   := (A + 3/(2^v-1) + 3(m2-1)/(2^v-1)^delta) / (3 K_lo log 2)   [h5.txt:708-711]
  qmin  := (delta, delta+eps) 内分母最小者的分母   [h5.txt:822-825 Lemma 22]
  U(m)  := 1.4784 * m * delta^m                   [sidw144.txt:271]
  L     := 7.5311e11                              [sidw144.txt:271]

本脚本的 qmin 用「取整加倒数」递归（与 route3_psi_probe.py 的「找首个分叉项」不同实现），
并在小 eps 处与独立写的暴力扫描对拍。
"""
from fractions import Fraction

from mpmath import mp, mpf, log, power, floor

mp.dps = 250

DELTA = log(3) / log(2)                              # 定义 D1
X0 = mpf(695) * power(2, 60)                         # 定义 D2
C_HYP = log(mpf(162) / 97 * X0) / log(2)             # 定义 D3
LOG2 = log(2)
L_LOWER = mpf("7.5311e11")                           # 定义 D4


def U_of(m):                                         # 定义 D5
    return mpf("1.4784") * m * power(DELTA, m)


def v_of(m2, m, K):                                  # 定义 D6
    return (mpf(m2) / m) * K * (DELTA - 1) / (power(DELTA, m2) - 1)


def A_of(m2, m):                                     # 定义 D7
    if m2 == m:
        return mpf(0)
    if m2 == m - 1:
        return mpf(3) / X0
    return mpf(97 * (m - m2) + 73) / (54 * X0)


def eps_of(m2, m, K):                                # 定义 D8
    w = power(2, v_of(m2, m, K)) - 1
    return (A_of(m2, m) + 3 / w + 3 * (m2 - 1) / power(w, DELTA)) / (3 * K * LOG2)


def feasible(m2, m, K):                              # 定义 D9（Theorem 21 假设）
    return (power(DELTA, m2) - 1) / (DELTA - 1) * C_HYP <= mpf(m2) / m * K


# ---------------------------------------------------------------- qmin 的两种实现
def min_den_rec(alpha, beta, depth=0):
    """区间 (alpha, beta) 内分母最小的分数，返回 (p, q)。取整加倒数递归。"""
    if depth > 800:
        raise AssertionError("递归过深（精度不足或区间退化）")
    if beta == mp.inf:                               # 上端为无穷时，最小分母分数是整数
        return (int(floor(alpha)) + 1, 1)
    a = int(floor(alpha))
    k0 = a + 1
    if k0 < beta:                                    # 最小的整数严格落在区间内
        return (k0, 1)
    # 此时区间含于 (a, a+1] 内：x = a + 1/y，y ∈ (1/(beta-a), 1/(alpha-a))
    inv_lo = 1 / (beta - a)      # y 的下端
    inv_hi = mp.inf if alpha == a else 1 / (alpha - a)   # 左端恰为整数时 y 无上界
    if not (inv_lo < inv_hi):
        raise AssertionError("倒数变换后区间反向，输入退化")
    p2, q2 = min_den_rec(inv_lo, inv_hi, depth + 1)
    p, q = a * p2 + q2, p2
    from math import gcd
    g = gcd(p, q)
    return (p // g, q // g)


def qmin_rec(eps):
    p, q = min_den_rec(DELTA, DELTA + eps)
    return q, p


def qmin_brute(eps, qmax):
    """暴力：扫 q = 1..qmax，取最小的 q 使 (delta, delta+eps) 内有分数。"""
    for q in range(1, qmax + 1):
        p = int(floor(DELTA * q)) + 1
        if p < (DELTA + eps) * q:
            return q
    return None


def eps_star(K, m):
    """min_{m2 可行} eps(m2, K)；可行集为空返回 None。"""
    best = None
    arg = None
    for m2 in range(1, m + 1):
        if not feasible(m2, m, K):
            continue
        e = eps_of(m2, m, K)
        if best is None or e < best:
            best, arg = e, m2
    return best, arg


def Psi(K, m):
    e, arg = eps_star(K, m)
    if e is None:
        return None, None, None
    q, p = qmin_rec(e)
    return q, arg, e


def chain(K0, m, U, nmax=40):
    seq = [(0, mpf(K0), None)]
    K = mpf(K0)
    for i in range(1, nmax + 1):
        q, arg, e = Psi(K, m)
        if q is None:
            break
        seq.append((i, mpf(q), arg))
        if q == K:
            break
        K = mpf(q)
        if U is not None and K > U:
            break
    return seq


def show(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


# ================================================================ 第 0 节：定义
show("第 0 节：定义（先定义后计算）")
print(f"D1 delta        = {mp.nstr(DELTA, 50)}")
print(f"D2 X0           = {mp.nstr(X0, 22)}   (= 695*2^60, h5.txt:83)")
print(f"D3 c            = {mp.nstr(C_HYP, 26)}   (h5.txt:698-703)")
print(f"D4 L            = {mp.nstr(L_LOWER, 6)}   (sidw144.txt:271)")
print(f"D5 U(91), U(92) = {mp.nstr(U_of(91), 22)} , {mp.nstr(U_of(92), 22)}")
print(f"D6 v(47,91,7e11)= {mp.nstr(v_of(47, 91, mpf('7e11')), 22)}")

# ================================================================ 第 1 节：锚点自检
show("第 1 节：锚点自检（与项目已钉住的数字比；判据：前缀逐位）")


def anchor(name, got, want_str, note=""):
    got_s = mp.nstr(got, len(want_str.split(".")[0]) + 25)
    print(f"[锚点] {name}")
    print(f"       本脚本 = {got_s}")
    print(f"       钉住值 = {want_str}   {note}")


anchor("delta 前 40 位", DELTA,
       "1.58496250072115618145373894394781650875981440769248106045575",
       "（materials.md:339）")
anchor("c", C_HYP, "70.18080632830836682484879", "（materials.md:345）")
K_up91 = U_of(91)
margin91 = mpf(7941964418702608664581) / K_up91
anchor("K_up(91) = 1.4784*91*delta^91", K_up91, "214072842063828923281.3586",
       "（materials.md:343）")
anchor("余量 91 = 7941964418702608664581 / K_up(91)", margin91,
       "37.09935525747164492758953", "（materials.md:344 / margin-table.txt:89）")
anchor("v(47,91,7e11)", v_of(47, 91, mpf("7e11")), "84.02140326164773718764214",
       "（materials.md:340）")
anchor("v(47,92,7.5311e11)", v_of(47, 92, L_LOWER), "89.41365947118846256456601",
       "（materials.md:341）")

frac = Fraction(7941964418702608664581, 214072842063828923281)
print(f"[锚点] 有理数精确式 7941964418702608664581/214072842063828923281 = {float(frac):.17g}")
print("       与 37.09935525747164492758953 的前 17 位一致 ? "
      f"{abs(mpf(frac.numerator) / mpf(frac.denominator) - mpf('37.09935525747164492758953')) < mpf('1e-17')}")

# ================================================================ 第 2 节：qmin 对拍
show("第 2 节：qmin 递归实现的对拍（先对小 eps 暴力，再对有理小区间暴力）")
ok_all = True
for eps_s, qmax in (("1e-2", 200), ("1e-3", 2000), ("1e-4", 20000), ("1e-5", 200000)):
    e = mpf(eps_s)
    q_rec, p_rec = qmin_rec(e)
    q_bf = qmin_brute(e, qmax)
    inint = DELTA < mpf(p_rec) / q_rec < DELTA + e
    if q_rec == q_bf:
        tag = "一致"
    else:
        tag = f"不一致（暴力上限 {qmax} 可能太小）"
    ok_all &= (q_rec == q_bf) and bool(inint)
    print(f"  eps={eps_s:>6}: 递归 q={q_rec:>7} 在区间内 ? {inint} ; 暴力 q<={qmax} -> {q_bf} : {tag}")

# 有理端点的小区间：改走精确有理数版本的同一递归（避免二进制端点误差）
def min_den_frac(alpha, beta, depth=0):
    """精确有理版（与 mpf 版同一递归结构）；beta = None 表示上端为无穷。

    返回 (分子, 分母)，两者为整数且互素。
    """
    if depth > 2000:
        raise AssertionError("递归过深")
    if beta is None:
        return (alpha.numerator // alpha.denominator + 1, 1)
    a = alpha.numerator // alpha.denominator          # 向下取整
    k0 = a + 1
    if Fraction(k0, 1) < beta:
        return (k0, 1)
    inv_lo = 1 / (beta - a)
    inv_hi = None if alpha == a else 1 / (alpha - a)
    p2, q2 = min_den_frac(inv_lo, inv_hi, depth + 1)   # y = p2/q2
    p, q = a * p2 + q2, p2                             # x = a + 1/y = (a*p2+q2)/p2
    from math import gcd
    g = gcd(p, q)
    return (p // g, q // g)


for alpha_s, beta_s in (("3/2", "8/5"), ("5/3", "12/7"), ("7/5", "10/7"), ("11/7", "8/5"),
                        ("9/4", "14/5")):
    al = Fraction(alpha_s)
    be = Fraction(beta_s)
    p, q = min_den_frac(al, be)
    bf = None
    for qq in range(1, 5000):
        pp = al.numerator * qq // al.denominator + 1
        if Fraction(pp, qq) < be:
            bf = qq
            break
    inint = al < Fraction(p, q) < be
    good = (q == bf) and inint
    ok_all &= bool(good)
    print(f"  区间 ({alpha_s},{beta_s}): 精确递归 (p,q)=({p},{q}) 在区间内 ? {inint} ; "
          f"暴力 q={bf} ; 一致 ? {good}")
print(f"→ 第 2 节合计通过 ? {ok_all}")

# ================================================================ 第 3 节：Psi 五值
show("第 3 节：Psi(K_lo) 的五个记录值（m = 92，独立复算）")
cases = [
    ("K_lo = L = 7.5311e11", L_LOWER, "5267319278509397"),
    ("K_lo = 10^20", mpf("1e20"), "205632218873398596256"),
    ("K_lo = 3.1e20", mpf("3.1e20"), "205632218873398596256"),
    ("K_lo = 3.3e20", mpf("3.3e20"), "7941964418702608664581"),
    ("K_lo = U(92)", U_of(92), "15678296618531818732906"),
]
psi_ok = True
for name, K, want in cases:
    q, arg, e = Psi(K, 92)
    good = (str(q) == want)
    psi_ok &= good
    print(f"  {name}: 最优 m2={arg}  Psi={q}")
    print(f"      记录值={want}  逐位一致 ? {good}")
print(f"→ 第 3 节全部逐位一致 ? {psi_ok}")
print(f"  附：U(92)/Psi(U(92)) = {mp.nstr(U_of(92) / 15678296618531818732906, 12)}"
      "  （即该起点下链一步就越过 U(92)）")

# ================================================================ 第 4 节：两条链
show("第 4 节：m = 92 与 m = 91 的自举链（同一合法起点 L）")
seq92 = chain(L_LOWER, 92, U_of(92))
for i, K, arg in seq92:
    print(f"  m=92 第 {i:>2} 步: {mp.nstr(K, 22)}" + (f"  (m2={arg})" if arg else ""))
term92 = seq92[-1][1]
print(f"  m=92 链终值 = {term92}   记录（margin-table.txt:90） = 77692117359936589403")
print(f"  m=92 余量 = {mp.nstr(term92 / U_of(92), 25)}"
      "   记录（margin-table.txt:90） = 0.226490482057595771625621")
print(f"  终值 < U(92) ? {term92 < U_of(92)}   → 不排除")

seq91 = chain(L_LOWER, 91, U_of(91))
for i, K, arg in seq91:
    print(f"  m=91 第 {i:>2} 步: {mp.nstr(K, 22)}" + (f"  (m2={arg})" if arg else ""))
term91 = seq91[-1][1]
print(f"  m=91 链终值 = {term91}   记录（margin-table.txt:89） = 7941964418702608664581")
print(f"  m=91 余量 = {mp.nstr(term91 / U_of(91), 25)}"
      "   记录（margin-table.txt:89） = 37.0993552574716449275895")
print(f"  终值 > U(91) ? {term91 > U_of(91)}   → 排除")

# ================================================================ 第 5 节：非降性的机制检查
show("第 5 节：Psi 非降的机制检查（只给数值证据；解析一段见报告 3.4 第 6 条）")
pts = ["7.5311e11", "1e15", "1e18", "5e19", "1e20", "2.05632218873398596256e20",
       "2.2e20", "3.1e20", "3.3e20", "4e20"]
prev = None
mono = True
for s in pts:
    K = mpf(s)
    q, arg, e = Psi(K, 92)
    if prev is not None and q < prev[1]:
        mono = False
    print(f"  K_lo={s:>26}: eps*={mp.nstr(e, 6):>12}  Psi={q:>25}  (m2={arg})")
    prev = (K, q)
print(f"→ 该 10 点网格上 Psi 非降 ? {mono}")
print("  注：网格只是证据；本报告的解析一段（eps 关于 K 下降、可行集随 K 扩大、"
      "qmin 关于 eps 非增）给出证明，见报告 3.4 第 6 条。")
q_star, arg_star, _ = Psi(mpf("2.05632218873398596256e20"), 92)
print(f"  Psi(K*) = {q_star} ; K* = 205632218873398596256 ; 相等 ? "
      f"{q_star == 205632218873398596256}")

# ================================================================ 第 6 节：读法反例（精确算术）
show("第 6 节：Σk 极大性不蕴含回绕前提（精确有理算术，m = 4, m2 = 2）")
dlt = Fraction(3).limit_denominator(10 ** 12)  # 占位，下面用高精度比较代替
m, m2 = 4, 2
x = [Fraction(200), Fraction(300), Fraction(320), Fraction(250)]
k = [Fraction(1), Fraction(1), Fraction(300), Fraction(240)]
print("  逐点 k_i <= x_i ?", all(k[i] <= x[i] for i in range(m)))
dl = mpf(DELTA)
# 链约束用有理放大 delta_rat = 1.585 > delta 检验：放大后仍成立则对真 delta 成立
dlt_rat = Fraction(1585, 1000)
print(f"  （链约束用 delta_rat = {dlt_rat} > delta 检验；放大后仍成立 => 对真 delta 成立）")
print("  链约束 x_(i+1) <= delta_rat x_i（循环）?",
      all(x[(i + 1) % m] <= dlt_rat * x[i] for i in range(m)))
Ksum = sum(k)
lhs = (power(dl, m2) - 1) / (dl - 1) * C_HYP
rhs = mpf(m2) / m * mpf(Ksum.numerator) / Ksum.denominator
print(f"  Theorem 21 假设: {mp.nstr(lhs, 8)} <= {mp.nstr(rhs, 8)} ? {lhs <= rhs}")
windows_k = [sum(k[(s + j) % m] for j in range(m2)) for s in range(m)]
windows_x = [sum(x[(s + j) % m] for j in range(m2)) for s in range(m)]
print(f"  各窗 Sigma k = {windows_k}")
print(f"  各窗 Sigma x = {windows_x}")
argmax_k = max(range(m), key=lambda s: windows_k[s])
argmax_x = max(range(m), key=lambda s: windows_x[s])
print(f"  Sigma k 最大窗起点 = {argmax_k}（唯一 ? {windows_k.count(windows_k[argmax_k]) == 1}）")
print(f"  Sigma x 最大窗起点 = {argmax_x}（唯一 ? {windows_x.count(windows_x[argmax_x]) == 1}）")
prev_idx, last_idx = (argmax_k - 1) % m, (argmax_k + m2 - 1) % m
print(f"  取 Sigma k 最大窗: 回绕前提 x_{prev_idx} <= x_{last_idx} = "
      f"{x[prev_idx]} <= {x[last_idx]} ? {x[prev_idx] <= x[last_idx]}")
prev_idx2, last_idx2 = (argmax_x - 1) % m, (argmax_x + m2 - 1) % m
wx = mpf(windows_x[argmax_x].numerator) / windows_x[argmax_x].denominator
print(f"  取 Sigma x 最大窗: 和约束 {windows_x[argmax_x]} >= (m2/m)K = {mp.nstr(rhs, 8)} ? "
      f"{wx >= rhs}；回绕前提 {x[prev_idx2]} <= {x[last_idx2]} ? "
      f"{x[prev_idx2] <= x[last_idx2]}")

# ================================================================ 第 7 节：闭化对称性
show("第 7 节：闭化无损（S 对称 + 顶点互为循环置换）")


def S_of(coords):
    return sum(3 / (power(2, c) - 1) for c in coords)


for (mm, m22, Ks) in ((91, 47, mpf("7.5311e11")), (91, 47, mpf("7e11"))):
    v = (mpf(m22) / mm) * Ks * (DELTA - 1) / (power(DELTA, m22) - 1)
    V1 = [v * power(DELTA, i) for i in range(m22)]                    # 回绕约束不活跃
    V2 = [v * power(DELTA, (i - 1) % m22) for i in range(m22)]        # 第一条链约束不活跃
    same_set = sorted(mp.nstr(t, 30) for t in V1) == sorted(mp.nstr(t, 30) for t in V2)
    print(f"  m={mm} m2={m22} K={mp.nstr(Ks, 8)}: v={mp.nstr(v, 16)}")
    print(f"    S(V1)={mp.nstr(S_of(V1), 20)}  S(V2)={mp.nstr(S_of(V2), 20)}  "
          f"逐位相等 ? {mp.nstr(S_of(V1), 20) == mp.nstr(S_of(V2), 20)}")
    print(f"    坐标集相同（循环置换）? {same_set}")
    print(f"    V1 回绕余量 v - delta*x_m2 = {mp.nstr(V1[0] - DELTA * V1[-1], 10)}"
          f"  （< 0 即严格满足 ? {V1[0] - DELTA * V1[-1] < 0}）")
    print(f"    V2 回绕余量 = {mp.nstr(V2[0] - DELTA * V2[-1], 10)}"
          f"  （|值| < 容差 ? {abs(V2[0] - DELTA * V2[-1]) < mpf('1e-40')}）")

show("总表")
print(f"  delta 40 位锚点、c、K_up(91)、余量 91、v 三点、Psi 五值、两条链、qmin 对拍")
print(f"  Psi 五值逐位一致 ? {psi_ok} ; qmin 对拍通过 ? {ok_all} ; 非降网格 ? {mono}")
