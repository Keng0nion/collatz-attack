"""route-3 原文读法溯源：Psi 的独立探针（核对 m = 92 那一句所依赖的四个记录值）。

本文件不复用项目脚本（不 import rederive-erratum.py 或任何其它项目模块），
全部定义按一手原件重写，行号以本次抽取的 /tmp/r3/*.txt 为准。

定义（先定义后计算）：
  delta := log 3 / log 2                    [h5.txt:506 Definition 15]
  X0    := 695 * 2^60                       [h5.txt:80-83 Definition 4]
  c     := log2((162/97) X0)                [h5.txt:698-703 Theorem 21 假设]
  A(m2) := (97(m-m2)+73)/(54 X0)            [h5.txt:465-470 Theorem 14；m2=m 时为 0、
                                             m2=m-1 时为 3/X0，见 h5.txt:813-818]
  v(m2) := (m2/m) K_lo (delta-1)/(delta^m2-1)   [h5.txt:705-706]
  eps(m2,K_lo) := (A + 3/(2^v - 1) + 3(m2-1)/(2^v-1)^delta) / (3 K_lo log 2)
                                            [h5.txt:708-711 Theorem 21 右端]
  qmin(eps) := (alpha,beta)=(delta, delta+eps) 的区间内分母最小者的分母
                                            [h5.txt:822-825 Lemma 22]
  Psi(K_lo) := qmin( min_{m2 可行} eps(m2,K_lo) )，可行 = Theorem 21 假设成立。
链的用法：delta < (K+L)/K < delta+eps，而 (K+L)/K 的既约分母整除 K（无需互素假设），
  故 K >= 该分母 >= qmin(eps)。[h5.txt:853-859 的七步自举]
"""
from mpmath import mp, mpf, log, power, floor

mp.dps = 200

DELTA = log(3) / log(2)
X0 = mpf(695) * power(2, 60)
C_HYP = log(mpf(162) / 97 * X0) / log(2)
LOG2 = log(2)


def v_of(m2, m, K):
    return (mpf(m2) / m) * K * (DELTA - 1) / (power(DELTA, m2) - 1)


def A_of(m2, m):
    if m2 == m:
        return mpf(0)
    if m2 == m - 1:
        return 3 / X0
    return (97 * (m - m2) + 73) / (54 * X0)


def eps_of(m2, m, K):
    v = v_of(m2, m, K)
    w = power(2, v) - 1
    return (A_of(m2, m) + 3 / w + 3 * (m2 - 1) / power(w, DELTA)) / (3 * K * LOG2)


def feasible(m2, m, K):
    return (power(DELTA, m2) - 1) / (DELTA - 1) * C_HYP <= mpf(m2) / m * K


def cf_terms(x, n):
    """x 的连分数部分商，取前 n 项。"""
    out = []
    for _ in range(n):
        ai = int(floor(x))
        out.append(ai)
        frac = x - ai
        if frac == 0:
            break
        x = 1 / frac
    return out


def qmin(eps, alpha=None, max_terms=400):
    """Lemma 22：区间 (alpha, alpha+eps) 内分母最小的分数的分母。"""
    a = DELTA if alpha is None else alpha
    b = a + eps
    A = cf_terms(a, max_terms)
    B = cf_terms(b, max_terms)
    k = None
    for i in range(min(len(A), len(B))):
        if A[i] != B[i]:
            k = i
            break
    assert k is not None, "两个连分数在给定的项数内未分叉，精度不足"
    terms = A[:k] + [min(A[k], B[k]) + 1]
    p_prev, q_prev = 1, 0        # p_{-1}, q_{-1}
    p_cur, q_cur = terms[0], 1   # p_0,  q_0
    for t in terms[1:]:
        p_prev, q_prev, p_cur, q_cur = p_cur, q_cur, t * p_cur + p_prev, t * q_cur + q_prev
    return q_cur, p_cur


def qmin_brute(eps, qmax, alpha=None):
    """暴力校验：扫 q = 1..qmax，返回最小可行 q（找不到返回 None）。"""
    a = DELTA if alpha is None else alpha
    b = a + eps
    for q in range(1, qmax + 1):
        p = int(floor(a * q)) + 1
        if p / mpf(q) < b:
            return q
    return None


print("=" * 78)
print("第 0 节：连分数机制自检 —— 与 SdW 印出的 delta 部分商对照")
print("=" * 78)
want_cf = [1, 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55]
got_cf = cf_terms(DELTA, len(want_cf))
print(f"sidw144.txt:133 印出：{want_cf}")
print(f"本脚本算出     ：{got_cf}")
print(f"前 {len(want_cf)} 项一致 ? {got_cf == want_cf}")

print()
print("=" * 78)
print("第 1 节：qmin 的暴力校验（小 eps，可穷举）")
print("=" * 78)
allok = True
for eps_s, qmax in (("1e-2", 100000), ("1e-3", 1000000), ("1e-4", 1000000), ("1e-5", 2000000),
                    ("1e-6", 5000000)):
    eps = mpf(eps_s)
    q_cf, p_cf = qmin(eps)
    q_bf = qmin_brute(eps, qmax)
    good = (q_bf is not None) and (q_cf == q_bf)
    allok &= bool(good)
    inint = DELTA < p_cf / mpf(q_cf) < DELTA + eps
    print(f"eps={eps_s:>6}: 连分数法 q={q_cf:>9}（p/q 在区间内 ? {inint}）；"
          f"暴力 q<={qmax} 得 {q_bf}；一致 ? {good}")
print(f"→ 小 eps 处两法一致：{allok}")

print()
print("=" * 78)
print("第 2 节：Psi(K_lo)（m = 92）与项目记录的四个值对照")
print("=" * 78)


def Psi(K_lo, m=92, verbose=False):
    best = None
    arg = None
    for m2 in range(1, m + 1):
        if not feasible(m2, m, K_lo):
            continue
        e = eps_of(m2, m, K_lo)
        if best is None or e < best:
            best, arg = e, m2
    q, p = qmin(best)
    if verbose:
        print(f"      K_lo={mp.nstr(K_lo, 22)}: 最优 m2={arg}, eps={mp.nstr(best, 8)}, "
              f"Psi={q}, 区间内 ? {DELTA < p / mpf(q) < DELTA + best}")
    return q, arg, best


U92 = mpf("1.4784") * 92 * power(DELTA, 92)      # sidw144.txt:271 的上界，m = 92
K_lo_L = mpf("7.5311e11")                        # sidw144.txt:271 的下界
print(f"U(92) = 1.4784*92*delta^92 = {mp.nstr(U92, 22)}"
      f"  （材料记 3.4302597024885020978e+20）")

cases = [
    ("K_lo = L = 7.5311e11", K_lo_L, "5267319278509397"),
    ("K_lo = 1e20", mpf("1e20"), "205632218873398596256"),
    ("K_lo = 3.1e20", mpf("3.1e20"), "205632218873398596256"),
    ("K_lo = 3.3e20", mpf("3.3e20"), "7941964418702608664581"),
    ("K_lo = U(92) = 3.4302597024885020978e20", mpf("3.4302597024885020978e20"),
     "1.5678296618531818732906e+22"),
]
for name, K_lo, want in cases:
    q, arg, e = Psi(K_lo, verbose=True)
    wq = mpf(want)
    rel = abs(mpf(q) - wq) / wq
    good = rel < mpf("1e-4") if wq > 1e6 else rel == 0
    print(f"   {name}: Psi = {q}")
    print(f"        记录值 = {want}   相对误差 = {mp.nstr(rel, 5)}   一致 ? {good}")

print()
print("=" * 78)
print("第 2b 节：m = 92 链从合法起点 L 出发的迭代（含终值与余量）")
print("=" * 78)


def iterate(K0, m=92, nmax=100, U=None):
    """从 K0 迭代 Ψ（固定 m），到不动点或越过 U 为止。

    越过 U 即排除达成；此后一步的 eps 小到连分数在 400 项内都不分叉，
    属于已无意义的步骤，故在此停表（不是精度不足导致的漏算）。
    """
    K = mpf(K0)
    seq = [(0, K, None)]
    for i in range(1, nmax + 1):
        q, arg, e = Psi(K, m=m)
        seq.append((i, mpf(q), arg))
        if mpf(q) == K:
            break
        K = mpf(q)
        if U is not None and K > U:
            break
    return seq


seq92 = iterate(K_lo_L, m=92, U=U92)
for i, K, arg in seq92:
    print(f"   第 {i:>2} 步: K = {mp.nstr(K, 22)}" + (f"   (最优 m2 = {arg})" if arg else ""))
stall92 = seq92[-1][1]
print(f"m = 92 的链终值 = {mp.nstr(stall92, 22)}")
print(f"   记录值（margin-table.txt:82 的 K 下界列）= 77692117359936589403")
print(f"   与记录值一致 ? {mp.nstr(stall92, 20) == '77692117359936589403.0'}")
print(f"m = 92 的余量 = 终值/U(92) = {mp.nstr(stall92 / U92, 25)}")
print(f"   记录值（margin-table.txt:82 余量列）= 0.226490482057595771625621")

print()
print("=" * 78)
print("第 2c 节：对照 —— m = 91 链从同一合法起点 L 出发的迭代")
print("=" * 78)
seq91 = iterate(K_lo_L, m=91, U=mpf("1.4784") * 91 * power(DELTA, 91))
for i, K, arg in seq91:
    print(f"   第 {i:>2} 步: K = {mp.nstr(K, 22)}" + (f"   (最优 m2 = {arg})" if arg else ""))
last91 = seq91[-1][1]
U91 = mpf("1.4784") * 91 * power(DELTA, 91)
print(f"m = 91 链末步 K = {mp.nstr(last91, 22)}")
print(f"   记录值（margin-table.txt:81 的 K 下界列）= 7941964418702608664581")
print(f"U(91) = {mp.nstr(U91, 22)}   K/U(91) = {mp.nstr(last91 / U91, 25)}")
print("   → 该比值 > 1 即 m = 91 被排除（与 margin-table.txt:81 的余量 37.099... 一致）。")

print()
print("=" * 78)
print("第 3 节：不动点核对与「合法起点」的上界")
print("=" * 78)
K_star_rec = mpf("2.05632218873398596256e20")
q_star, arg_star, e_star = Psi(K_star_rec, verbose=True)
print(f"Psi(K*) 与 K* 的相对差 = {mp.nstr(abs(mpf(q_star) - K_star_rec) / K_star_rec, 5)}")
print(f"K* < U(92) ? {K_star_rec < U92}   记录比值 K*/U = "
      f"{mp.nstr(K_star_rec / U92, 12)}")
q_L, arg_L, e_L = Psi(K_lo_L)
print(f"Psi(L) = {q_L}（L = 7.5311e11）;  Psi(L) < U(92) ? {mpf(q_L) < U92}")
print("→ 若 Psi 关于 K_lo 非降（该项目报告自述为「我的推理」，另有 11 点网格），")
print("  则一切 K_lo <= K* 的起点都给 Psi <= K* < U(92)，故 m = 92 在这些起点下不被排除；")
print("  而 K_lo = U(92) 这一起点本身与 SdW 的上界 K < U(92) 冲突，不是合法排除起点。")
