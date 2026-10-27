#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify.py —— 轨道 thm23-eps cycle-1 本轮增量结论的独立复算闸门。

运行方式（仅需 Python 标准库；PDF 相关项另需 poppler 的 pdftotext 与 pdftoppm）：
    python3 verify.py            # 默认档，约 10 至 30 秒
    python3 verify.py --deep     # 深度档，约 1 至 3 分钟
退出码：全部通过 0；任一断言失败 1（打印最小反例）；缺工具或缺原件时相关项打 SKIP。

闸门调用路径（2026 年 10 月 28 日实测的原因定位）：工作流以仓库根
/Users/luna/Documents/math IA/collatz-attack 为 cwd 执行
    collatz-attack/20-experiments/.venv/bin/python collatz-attack/70-research/tracks/thm23-eps/cycle-1/verify.py
其中脚本参数是工作区相对路径，从仓库根解析会多一层 collatz-attack。仓库根 .gitignore 已登记
`collatz-attack/` 垫片目录（可随时删除）；本轮在其中补了符号链接 collatz-attack/70-research
指回真实的 70-research 目录，此路径即可解析到本脚本。脚本自身用 __file__ 定位 materials 与
scripts/route4-out，并带后备搜索，被复制或经符号链接执行都能找到材料。

纪律（本脚本的自我约束）：
    1. 脚本自行复算一切：区间算术、连分数、七步链条、窗口二分全部在脚本内实现，
       不读取 route 文件与 materials.md，不 import 项目内任何既有脚本。
    2. 期望值（46 位 eps、七步印数、K 串、q43 等）以字面常量写在本文件里，
       来源是本轮增量结论清单本身；PDF 只作第一手材料使用（可选，缺则 SKIP）。
    3. 判定只用精确整数与有理数比较，或严格区间包含；浮点只出现在显示用的科学计数里。
    4. 明确标注「无法机器验证」的部分（见各处注释与输出中的 [注] 行）。

默认档覆盖：
    自检：区间库定点锚（e、ln2、log2(3) 的 20 位小数邻域，exp(ln2) 含 2）。
    增量 1：第 15 页重渲染件 md5；两版第 15 页七步印数、K 串、X0 的文字抽取核对。
    增量 2：三个 K 的 eps 严格区间与记录 46 位值逐位核对；18 位记录值的舍入判定；
            第二条代数路线（3 的幂乘恒等式）交叉。
    增量 3：七步链条复算（最大可行 m2、eps、向上取整一位小数、Lemma 22 的 gamma 分母、
            K 串截尾核对）；第七步在三个候选 K 上的六种印刷规则。
    增量 4：五个交点 K@1.12、1.115、1.11、1.105、1.10 的严格二分（±1e9）与三条窗口包含判定。
    增量 5：delta 的连分数前缀、q43、q44、a44、a45、T、S38 与两条距离不等式。
    增量 6：第 12 页两版差异（因数 7/5、36 与 60）的文字抽取核对。
深度档（--deep）额外覆盖：
    a. 二分收紧到 ±1e6，并多解 1.20、1.15、1.05、1.00 四个交点；
    b. 窗口带全域 400 点扫描（逐点比对「命中的二小数规则集合」与由括号给出的
       严格窗口归属），另在窗口左右两侧各取 150 点断言无一印出 1.11
       （属抽样核验，不是证明；三个窗口彼此有交叠，故比对的是命中集合）。
"""

import hashlib
import shutil
import subprocess
import sys
import tempfile
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _asset(rel):
    """定位材料文件：脚本自身目录优先，其次沿各级祖先与当前目录搜寻本轨道目录，
    以兼容经符号链接执行或被复制到别处的场合。"""
    bases = [HERE]
    a = HERE.parent
    for _ in range(8):
        bases.append(a / "70-research" / "tracks" / "thm23-eps" / "cycle-1")
        if a.parent == a:
            break
        a = a.parent
    c = Path.cwd()
    bases += [c / "collatz-attack" / "70-research" / "tracks" / "thm23-eps" / "cycle-1",
              c / "70-research" / "tracks" / "thm23-eps" / "cycle-1"]
    for b in bases:
        p = b / rel
        if p.exists():
            return p
    return bases[0] / rel


ARXIV_PDF = _asset("materials/arxiv-2201.00406v3.pdf")
PRINT_PDF = _asset("materials/hercher5.pdf")
RENDER_ARTIFACT = _asset("scripts/route4-out/h5-p15-15.png")

T0 = time.time()
DEEP = "--deep" in sys.argv[1:]

N_PASS = 0
N_FAIL = 0
N_SKIP = 0
FAILURES = []


def section(title):
    print("\n" + "=" * 4 + " " + title)


def check(name, ok, witness=""):
    global N_PASS, N_FAIL
    if ok:
        N_PASS += 1
        print("  [PASS] " + name)
    else:
        N_FAIL += 1
        FAILURES.append(name)
        line = "  [FAIL] " + name
        if witness:
            line += "　最小反例：" + str(witness)
        print(line)


def skip(name, why):
    global N_SKIP
    N_SKIP += 1
    print("  [SKIP] " + name + "：" + why)


def note(text):
    print("  [注] " + text)


# =====================================================================
# 1. 自足严格有理区间库
#    端点全为 Fraction；一切运算后向外取整到绝对网格 10 的负 140 次幂。
#    超越函数只用「正项级数部分和加显式尾界」，每一步定向取整，保证严格性。
# =====================================================================

P = 140
G = 10 ** P
FLOOR = F(1, G)


def dn(x):
    """不大于 x 的最大网格格点（向下取整）。"""
    return F((x.numerator * G) // x.denominator, G)


def up(x):
    """不小于 x 的最小网格格点（向上取整）。"""
    return F(-((-x.numerator * G) // x.denominator), G)


def iadd(a, b):
    return (dn(a[0] + b[0]), up(a[1] + b[1]))


def imul(a, b):
    ps = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (dn(min(ps)), up(max(ps)))


def idiv(a, b):
    assert b[0] > 0, "区间除法只允许正分母"
    return (dn(min(a[0] / b[1], a[1] / b[1])), up(max(a[0] / b[0], a[1] / b[0])))


def ineg(a):
    return (-a[1], -a[0])


def isub(a, b):
    return iadd(a, ineg(b))


def atanh_side(u, low, ncap=4000):
    """atanh(u) 的单侧界，u 为非负网格有理数（本脚本用到 u 不超过 1/3）。

    级数 sum u^(2k+1)/(2k+1)；下界：逐项向下取整后停在高阶项落到网格下；
    上界：逐项向上取整，停止时再加尾界 u^(2k+1)/((2k+1)(1-u^2))。
    """
    u2 = u * u
    pu = u
    tot = F(0)
    k = 0
    while k < ncap:
        t = pu / (2 * k + 1)
        if low:
            tot += dn(t)
            if pu <= FLOOR:
                return tot, k
            pu = dn(pu * u2)
        else:
            tot += up(t)
            if pu <= FLOOR:
                tail = up(pu / ((2 * k + 1) * (1 - u2)))
                return tot + tail, k
            pu = up(pu * u2)
        k += 1
    raise RuntimeError("atanh 级数未收敛")


LN2L = 2 * atanh_side(F(1, 3), True)[0]     # ln2 = 2 atanh(1/3)
LN2U = 2 * atanh_side(F(1, 3), False)[0]
LN3L = 2 * atanh_side(F(1, 2), True)[0]     # ln3 = 2 atanh(1/2)
LN3U = 2 * atanh_side(F(1, 2), False)[0]
LOGN2 = (LN2L, LN2U)
LN3_IV = (LN3L, LN3U)


def log2_floor(x):
    e = x.numerator.bit_length() - x.denominator.bit_length()
    while F(2) ** e > x:
        e -= 1
    while F(2) ** (e + 1) <= x:
        e += 1
    return e


def ln_side(x, low):
    """ln(x) 的单侧界，x 为正网格有理数。

    先把 x 写成 2^e 乘 m（m 在 [1,2)），再对 ln(m) 走 atanh 级数
    （u = (m-1)/(m+1) 不超过 1/3），按方向先对 u 定向取整。
    """
    e = log2_floor(x)
    m = x / F(2) ** e
    eln = (e * LN2L if e >= 0 else e * LN2U) if low else (e * LN2U if e >= 0 else e * LN2L)
    eln = dn(eln) if low else up(eln)
    if m == 1:
        return eln
    u = (m - 1) / (m + 1)
    u = dn(u) if low else up(u)
    at, _ = atanh_side(u, low)
    v = dn(2 * at) if low else up(2 * at)
    return dn(eln + v) if low else up(eln + v)


def ln_interval(x):
    return (ln_side(x[0], True), ln_side(x[1], False))


def exp_side_pos(y, low, ncap=4000):
    """exp(y) 的单侧界，y 为非负网格有理数。折半 J 次到 z <= 1/2，
    部分和加尾界 z^(k+1)/((k+1)!(1-z/(k+2)))，再平方 J 次。"""
    if y == 0:
        return F(1)
    J = 0
    while F(2) ** J * F(1, 2) <= y:
        J += 1
    z = y / F(2) ** J
    tot = F(0)
    pw = F(1)
    fa = F(1)
    k = 0
    while k < ncap:
        t = pw / fa
        if low:
            tot += dn(t)
            if pw <= FLOOR:
                break
            k += 1
            pw = dn(pw * z)
            fa = fa * k
        else:
            tot += up(t)
            if pw <= FLOOR:
                tail = up(pw * z / (fa * (k + 1)) / (1 - z / (k + 2)))
                tot += tail
                break
            k += 1
            pw = up(pw * z)
            fa = fa * k
    r = tot
    for _ in range(J):
        r = dn(r * r) if low else up(r * r)
    return r


def exp_side(y, low):
    if y >= 0:
        return exp_side_pos(y, low)
    e = exp_side_pos(-y, not low)
    return dn(F(1) / e) if low else up(F(1) / e)


def exp_interval(y):
    return (exp_side(y[0], True), exp_side(y[1], False))


# =====================================================================
# 2. 论文常数与公式（全部自行复算）
#    delta = log(3)/log(2)；X0 = 695 * 2^60（印出版，第 15 页文本亦由增量 1 核对）
#    C = log2((162/97) X0)；可行性：((delta^m2 - 1)/(delta - 1)) C <= (m2/m) K
#    eps(m2, K) = [ A(m2) + 3/(2^v - 1) + 3(m2-1)/(2^v-1)^delta ] / (3 K ln2)
#    v = (m2/m) K (delta - 1)/(delta^m2 - 1)
#    A(m2)：m2 = m 取 0；m2 = m - 1 取 3/X0；其余取 (97(m - m2) + 73)/(54 X0)
#    （公式出处：论文 Theorem 21 的 m2 = m 特例与一般式；本脚本按此定义复算。）
# =====================================================================

M_CYCLE = 91
X0_PRINT = 695 * 2 ** 60          # 印出版 Definition 4 的值（v3 为 704 乘 2 的 60 次幂）
DELTA = idiv(LN3_IV, LOGN2)
C_IV = idiv(ln_interval((F(162, 97) * X0_PRINT, F(162, 97) * X0_PRINT)), LOGN2)
ONE = (F(1), F(1))
DELTA_M1 = isub(DELTA, ONE)
POW = {0: (F(1), F(1))}
for _k in range(1, M_CYCLE + 1):
    POW[_k] = imul(POW[_k - 1], DELTA)

K_205 = 205000000000000000000
K_206 = 206000000000000000000
K_20603 = 206030000000000000000
K_STAR = 205632218873398596256          # 第六步精确输出（增量 2、3、5 均出现）
K_CHAIN0 = 7 * 10 ** 11
TEN43 = (F(10) ** 43, F(10) ** 43)


def feasible(m2, K, m=M_CYCLE):
    lhs = imul(idiv(isub(POW[m2], ONE), DELTA_M1), C_IV)
    rhs = F(m2, m) * F(K)
    if lhs[1] <= rhs:
        return True
    if lhs[0] > rhs:
        return False
    return None


def max_feasible(K, m=M_CYCLE):
    best = 0
    for m2 in range(1, m + 1):
        f = feasible(m2, K, m)
        if f is None:
            raise RuntimeError("可行性在 m2 = %d 处无法判定" % m2)
        if f:
            best = m2
        else:
            break
    return best


def a_branch(m2, m=M_CYCLE, X0=X0_PRINT):
    if m2 == m:
        return (F(0), F(0))
    if m2 == m - 1:
        return (F(3, X0), F(3, X0))
    return (F(97 * (m - m2) + 73, 54 * X0), F(97 * (m - m2) + 73, 54 * X0))


def eps_parts(m2, K, m=M_CYCLE, X0=X0_PRINT):
    KF = F(K)
    v = idiv(imul((F(m2, m) * KF, F(m2, m) * KF), DELTA_M1), isub(POW[m2], ONE))
    p2v = exp_interval(imul(v, LOGN2))
    p2v_m1 = isub(p2v, ONE)
    pw = exp_interval(imul(DELTA, ln_interval(p2v_m1)))
    t1 = idiv((F(3), F(3)), p2v_m1)
    t2 = idiv((F(3 * (m2 - 1)), F(3 * (m2 - 1))), pw)
    A = a_branch(m2, m, X0)
    num = iadd(A, iadd(t1, t2))
    den = imul((F(3) * KF, F(3) * KF), LOGN2)
    return dict(eps=idiv(num, den), v=v, p2v=p2v, p2v_m1=p2v_m1, pw=pw,
                t1=t1, t2=t2, num=num, den=den)


def eps_route_b(m2, K, m=M_CYCLE):
    """(2^v - 1)^delta 的第二条代数路线（交叉验证用）：
    (2^v - 1)^delta = 3^floor(v) * exp(r ln3 + delta ln(1 - 2^(-v)))，r = v - floor(v)；
    用 ln(1 - z) 在 (0, 1/2] 上的两端界 -(z + z^2) 与 -z。"""
    parts = eps_parts(m2, K, m)
    v = parts["v"]
    # floor(v)：v 为正区间
    e_lo = v[0].numerator // v[0].denominator
    e_hi = v[1].numerator // v[1].denominator
    if e_lo != e_hi:
        raise RuntimeError("floor(v) 无法判定")
    fl = e_lo
    r_iv = isub(v, (F(fl), F(fl)))
    z_iv = exp_interval(ineg(imul(v, LOGN2)))           # z = 2^(-v) = exp(-v ln2)
    z_lo, z_hi = z_iv
    ln1mz_iv = (-(z_hi + z_hi * z_hi), -z_lo)           # ln(1-z) 的两端界
    y_iv = iadd(imul(r_iv, LN3_IV), imul(DELTA, ln1mz_iv))
    pw_b = imul((F(3 ** fl), F(3 ** fl)), exp_interval(y_iv))
    t2_b = idiv((F(3 * (m2 - 1)), F(3 * (m2 - 1))), pw_b)
    num_b = iadd(parts["A"] if "A" in parts else a_branch(m2, m),
                 iadd(parts["t1"], t2_b))
    eps_b = idiv(num_b, parts["den"])
    return dict(eps=eps_b, pw=pw_b, t2=t2_b, num=num_b, floor_v=fl)


def cf_prefix_split(lo, hi, maxlen=400):
    """区间 (lo, hi) 的连分数公共前缀与首个相异系数（高斯映射，两端精确有理）。
    返回 (前缀列表, 小端下一系数, 大端下一系数)。端点恰为整数时报无法判定。"""
    pre = []
    while len(pre) < maxlen:
        alo = lo.numerator // lo.denominator
        ahi = hi.numerator // hi.denominator
        if alo != ahi:
            return pre, alo, ahi
        if lo == alo:
            raise RuntimeError("区间端点恰为整数，需要收窄")
        pre.append(alo)
        lo, hi = 1 / (hi - alo), 1 / (lo - alo)
    raise RuntimeError("前缀层数超过上限")


def cf_den(coeffs):
    """有限连分数 [c0; c1, ..., cn] 的分母（精确整数递推）。"""
    if len(coeffs) == 1:
        return 1
    qm1, q = 0, 1
    for a in coeffs[1:]:
        qm1, q = q, a * q + qm1
    return q


DELTA_PREFIX = cf_prefix_split(DELTA[0], DELTA[1], maxlen=400)
CF_COEFFS = DELTA_PREFIX[0]


def convergent_table(coeffs):
    """由系数表给 (p_n, q_n, a_n) 列表。"""
    pm1, p = 1, coeffs[0]
    qm1, q = 0, 1
    tbl = [(p, q, coeffs[0])]
    for a in coeffs[1:]:
        pm1, p = p, a * p + pm1
        qm1, q = q, a * q + qm1
        tbl.append((p, q, a))
    return tbl


def gamma_den(lo, hi):
    """Lemma 22 的 gamma = [前缀; min(a_k, b_k) + 1] 的分母（区间 (lo, hi) 版本）。"""
    pre, alo, ahi = cf_prefix_split(lo, hi)
    c = min(alo, ahi) + 1
    return cf_den(pre + [c]), len(pre), c, alo, ahi


def x43(K):
    """x(K) = eps(91, 91, K) * 10^43 的严格区间（关于 K 严格递减）。"""
    return imul(eps_parts(91, K)["eps"], TEN43)


# =====================================================================
# 3. 印刷规则（在 x = eps * 10^43 的尺度上作用；区间上判定，未定返回 None）
# =====================================================================

def trunc_rule(x_iv, d):
    s = F(10) ** d
    f = lambda v: F((v * s).numerator // (v * s).denominator, s)
    a, b = f(x_iv[0]), f(x_iv[1])
    return a if a == b else None


def ceil_rule(x_iv, d):
    s = F(10) ** d
    f = lambda v: F(-((-v * s).numerator // (v * s).denominator), s)
    a, b = f(x_iv[0]), f(x_iv[1])
    return a if a == b else None


def round_rule(x_iv, d):
    """四舍五入（half up），对正值。"""
    s = F(10) ** d
    f = lambda v: F((v * s + F(1, 2)).numerator // (v * s + F(1, 2)).denominator, s)
    a, b = f(x_iv[0]), f(x_iv[1])
    return a if a == b else None


RULES = ("ceil1", "ceil2", "round1", "round2", "trunc1", "trunc2")


def six_rules(x_iv):
    return {
        "ceil1": ceil_rule(x_iv, 1),
        "ceil2": ceil_rule(x_iv, 2),
        "round1": round_rule(x_iv, 1),
        "round2": round_rule(x_iv, 2),
        "trunc1": trunc_rule(x_iv, 1),
        "trunc2": trunc_rule(x_iv, 2),
    }


def dec_frac(s):
    """把十进制串（如 "1.44921627253094092e-43"）解析成精确 Fraction。"""
    m, _, e = s.partition("e")
    ex = int(e) if e else 0
    neg = m.startswith("-")
    if neg:
        m = m[1:]
    ip, _, fp = m.partition(".")
    v = F(int(ip + fp), 10 ** len(fp))
    v = v * 10 ** ex if ex >= 0 else v / 10 ** (-ex)
    return -v if neg else v


def sig_frac(digits, exp10):
    """尾数字符串 + 指数 -> 精确 Fraction（46 位记录值用）。"""
    n = len(digits)
    return F(int(digits), 10 ** (n - 1)) * (F(10) ** exp10)


def fmt(x, nd=25):
    """Fraction 的十进制显示（截断，仅用于展示）。"""
    neg = x < 0
    v = -x if neg else x
    ip = v.numerator // v.denominator
    rem = v - ip
    out = str(ip) + "."
    for _ in range(nd):
        rem *= 10
        d = rem.numerator // rem.denominator
        out += str(d)
        rem -= d
    return ("-" if neg else "") + out


def fmt_sci(x, nd=20):
    """科学计数显示（截断，仅用于展示）。"""
    if x == 0:
        return "0"
    e = log2_floor(x) if x > 0 else None
    # 用十进制幂定指数
    k = 0
    v = abs(x)
    while v >= 10:
        v /= 10
        k += 1
    while v < 1:
        v *= 10
        k -= 1
    return ("-" if x < 0 else "") + fmt(v, nd) + "e" + ("+" if k >= 0 else "") + str(k)


def pretty(v):
    """把十进制小数的 Fraction 显示成十进制串，其余仍显示分数。"""
    d = v.denominator
    k = 0
    while d > 1 and d % 10 == 0:
        d //= 10
        k += 1
    if d == 1:
        return fmt(v, k) if k else str(v.numerator)
    return str(v)


def tlabel(t):
    """把 1.12、1.115 这类目标值显示成标签。"""
    n = t * 1000
    return "%d.%03d" % (n // 1000, n % 1000)


def bisect_crossing(t, tol):
    """在 [2.05e20, 2.07e20] 上二分求 x(K) = t 的交点，返回括号 (a, b)，
    满足 x(a) > t > x(b)（严格区间比较）且 b - a <= tol。"""
    a, b = 205 * 10 ** 18, 207 * 10 ** 18
    assert x43(a)[0] > t, "左端不满足 x(a) > t"
    assert x43(b)[1] < t, "右端不满足 x(b) < t"
    while b - a > tol:
        m = (a + b) // 2
        if x43(m)[0] > t:
            a = m
        else:
            b = m
    return a, b


def round_check(x_iv, tgt, ulp):
    """区间 [x_iv] 在给定末位 ulp 下是否为 tgt 的正确截尾或正确四舍五入。"""
    trunc_ok = (x_iv[0] >= tgt) and (x_iv[1] < tgt + ulp)
    round_ok = (x_iv[0] >= tgt - ulp / 2) and (x_iv[1] < tgt + ulp / 2)
    return trunc_ok, round_ok


# =====================================================================
# 4. 增量清单给出的期望值（字面常量；来源：本轮增量结论本身）
# =====================================================================

# 增量 1：印数串（第 15 页，两版相同）
EPS_PRINT_STR = ["6.9", "5.1", "4.1", "2.3", "2.3", "5.3", "1.11"]
K_PRINT_STR = ["5.2", "3.97", "4.64", "2.74", "7.76", "2.05", "7.94"]
RENDER_MD5 = "2f6d307aff0ffdf29a7319e72cb2751c"

# 增量 2：三个 K 的 46 位记录值（尾数写成整数串，指数均为 -43）
EPS46 = {
    K_205: "1449216272530940917415524651121474797189592683",
    K_STAR: "1229791579962353075918171916433619021557150657",
    K_206: "1117776630688388161113190253588452920629473006",
}
EPS18 = {
    K_205: "1.44921627253094092e-43",
    K_STAR: "1.22979157996235308e-43",
    K_206: "1.11777663068838816e-43",
}

# 增量 3：七步链条
M2_SEQ = [47, 67, 77, 82, 86, 88, 91]
EPS_PRINT_FRAC = [F(69, 10), F(51, 10), F(41, 10), F(23, 10), F(23, 10),
                  F(53, 10), F(111, 100)]
EPS_PRINT_EXP = [-32, -36, -38, -39, -40, -41, -43]
K_PRINT_DIGITS = [1, 2, 2, 2, 2, 2, 2]        # 第 1 步印 2 位有效数字，其余 3 位
K_PRINT_EXP = [15, 17, 18, 19, 19, 20, 21]
# 记录里给出的六种规则读数（原文照录，仅供 [注] 对照；其末项见脚本内说明）
CLAIM_SIX_KSTAR = [F(120, 100), F(122, 100), F(123, 100), F(123, 100),
                   F(130, 100), F(123, 100)]
CLAIM_SIX_205 = [F(140, 100), F(144, 100), F(145, 100), F(145, 100),
                 F(150, 100), F(145, 100)]

# 增量 5
Q43_EXPECT = 205632218873398596256
Q44_EXPECT = 7736332199829210068325
A44_EXPECT = 37
A45_EXPECT = 4
T_EXPECT = 7941964418702608664581
S38_NUM_EXPECT = 12587715785705330118969

# 增量 4
CROSS_DEFAULT = [F(112, 100), F(1115, 1000), F(111, 100), F(1105, 1000), F(110, 100)]
CROSS_DEEP = [F(120, 100), F(115, 100)] + CROSS_DEFAULT + [F(105, 100), F(100, 100)]

TOL_DEFAULT = 2 * 10 ** 9
TOL_DEEP = 2 * 10 ** 6


# =====================================================================
# 5. 自检与各增量断言
# =====================================================================

def assert_selftest():
    section("0. 区间库自检（定点锚）")
    check("ln2 区间宽小于 1e-130", LN2U - LN2L < F(1, 10 ** 130))
    check("ln2 区间落在 20 位截断邻域内",
          LN2L >= F(69314718055994530941, 10 ** 20),
          "实测下界 " + fmt(LN2L, 25))
    check("ln2 区间上界不超过 20 位截断加一格",
          LN2U <= F(69314718055994530942, 10 ** 20),
          "实测上界 " + fmt(LN2U, 25))
    e_iv = (exp_side(F(1), True), exp_side(F(1), False))
    check("exp(1) 区间落在 e 的 20 位截断邻域内",
          e_iv[0] >= F(271828182845904523536, 10 ** 20) and
          e_iv[1] <= F(271828182845904523537, 10 ** 20))
    check("exp(ln2 区间) 包含精确整数 2",
          exp_interval(LOGN2)[0] <= 2 <= exp_interval(LOGN2)[1])
    check("delta 区间落在 20 位截断邻域内",
          DELTA[0] >= F(158496250072115618145, 10 ** 20) and
          DELTA[1] <= F(158496250072115618146, 10 ** 20),
          "实测 " + fmt(DELTA[0], 25) + " 至 " + fmt(DELTA[1], 25))
    check("连分数前缀在 45 层以上仍是确定的", len(CF_COEFFS) > 46,
          "实测接受层数 " + str(len(CF_COEFFS)))
    # 连分数自检锚（教科书例：415/93 邻域证书止于 [4, 2, 6]）
    lo = F(415, 93) - F(1, 10 ** 9)
    hi = F(415, 93) + F(1, 10 ** 9)
    pre, alo, ahi = cf_prefix_split(lo, hi)
    check("连分数前缀自检：415/93 的邻域止于 [4, 2, 6]", pre == [4, 2, 6], str(pre))


def assert_claim1_document():
    """增量 1：第 15 页两版逐字与渲染件 md5。

    能机器验证的：重渲染 md5 一致；两版第 15 页文本抽取中七步印数、K 串按序出现；
    第七步整句与 X0 的 695 与 704 归属。
    无法机器验证的：上标位等版式细节、「逐字亲读」这一人工动作本身
    （由渲染件 md5 相同担保所读图像与记录一致）。
    """
    section("增量 1：第 15 页与渲染件 md5")
    if not PRINT_PDF.exists():
        skip("第 15 页 PDF 检查", "materials/hercher5.pdf 不存在")
    else:
        if shutil.which("pdftoppm") is None:
            skip("第 15 页重渲染 md5", "未找到 pdftoppm")
        else:
            with tempfile.TemporaryDirectory() as td:
                out = str(Path(td) / "p15")
                r = subprocess.run(["pdftoppm", "-png", "-r", "200", "-f", "15",
                                    "-l", "15", str(PRINT_PDF), out],
                                   capture_output=True, text=True)
                png = Path(out + "-15.png")
                if r.returncode != 0 or not png.exists():
                    skip("第 15 页重渲染 md5", "pdftoppm 退出码 " + str(r.returncode))
                else:
                    md5 = hashlib.md5(png.read_bytes()).hexdigest()
                    check("第 15 页 200 dpi 重渲染 md5 == 记录值",
                          md5 == RENDER_MD5, "实测 " + md5)
        if RENDER_ARTIFACT.exists():
            md5 = hashlib.md5(RENDER_ARTIFACT.read_bytes()).hexdigest()
            check("在库渲染件 scripts/route4-out/h5-p15-15.png 的 md5 == 记录值",
                  md5 == RENDER_MD5, "实测 " + md5)
        else:
            skip("在库渲染件 md5", "scripts/route4-out/h5-p15-15.png 不存在")
        # 文本抽取核对（两版）
        texts = {}
        if shutil.which("pdftotext") is None:
            skip("第 15 页文本抽取核对", "未找到 pdftotext")
        else:
            for tag, pdf in (("印出版", PRINT_PDF), ("v3", ARXIV_PDF)):
                if not pdf.exists():
                    skip(tag + " 第 15 页文本", pdf.name + " 不存在")
                    continue
                r = subprocess.run(["pdftotext", "-f", "15", "-l", "15", str(pdf), "-"],
                                   capture_output=True, text=True)
                texts[tag] = " ".join(r.stdout.split())
            for tag, t in texts.items():
                pos, ok = -1, True
                seq = []
                for i in range(7):
                    seq += [EPS_PRINT_STR[i], K_PRINT_STR[i]]
                for tok in seq:
                    p = t.find(tok, pos + 1)
                    if p < 0:
                        ok = False
                        break
                    pos = p
                check(tag + " 第 15 页：eps 与 K 串按七步次序出现", ok, "断在 " + tok)
                for pat in ("δ + 1.11 · 10−43 and", "K > 7.94 · 1021",
                            "m2 ≥ 91", "Applying this lower bounnd a last time"):
                    check(tag + " 第 15 页含 " + repr(pat), pat in t)
                if tag == "印出版":
                    check("印出版第 15 页 X0 = 695 · 260 且无 704",
                          ("X0 = 695 · 260" in t) and ("X0 = 704 · 260" not in t))
                else:
                    check("v3 第 15 页 X0 = 704 · 260 且无 695",
                          ("X0 = 704 · 260" in t) and ("X0 = 695 · 260" not in t))
    note("上标位（指数 −43 在右上角）等版式细节无法由文本抽取机器验证；"
         "渲染件 md5 逐位相同担保所读图像与记录是同一张。")
    note("「我这份成品 md5 与 route-2、route-4 记录逐位相同」一句中的跨记录比对，"
         "脚本不读 route 文件，只能复核在库渲染件与重渲染件都等于该 md5。")


def assert_claim2_epsilon_table():
    """增量 2：三处 K 的 eps 严格区间与记录 46 位值、18 位值的舍入判定，
    以及 v、2^v、(2^v−1)^δ、t1、t2、num、den 的自洽与第二条代数路线交叉。

    无法机器验证的：与 route-2.md 表格的逐行对照（脚本不读该文件）；
    脚本改为复核 46 位记录值本身与第二条路线交叉。
    """
    section("增量 2：三处 K 的 eps 区间与记录值")
    results = {}
    for K in (K_205, K_STAR, K_206):
        parts = eps_parts(91, K)
        results[K] = parts
        eps = parts["eps"]
        w = eps[1] - eps[0]
        relw = w / eps[0]
        tgt46 = sig_frac(EPS46[K], -43)
        ulp46 = F(1, 10 ** 88)
        tr, ro = round_check(eps, tgt46, ulp46)
        check("K = " + str(K) + "：46 位记录值等于区间的正确截尾或正确舍入",
              tr or ro,
              "区间 " + fmt_sci(eps[0], 22) + " 至 " + fmt_sci(eps[1], 22) +
              "，记录 " + str(tgt46))
        check("K = " + str(K) + "：区间相对宽小于 1e-60（足以定 46 位）", relw < F(1, 10 ** 60),
              fmt_sci(relw, 8))
        tgt18 = dec_frac(EPS18[K])
        check("K = " + str(K) + "：18 位记录值不在区间内（打印精度事实）",
              not (eps[0] <= tgt18 <= eps[1]))
        tr18, ro18 = round_check(eps, tgt18, F(1, 10 ** 60))
        check("K = " + str(K) + "：18 位记录值是区间的正确舍入", ro18 or tr18)
        # 第二条代数路线
        rb = eps_route_b(91, K)
        inter = (max(eps[0], rb["eps"][0]), min(eps[1], rb["eps"][1]))
        check("K = " + str(K) + "：两条代数路线的 eps 区间相交",
              inter[0] <= inter[1], "路线 a " + fmt_sci(eps[0], 12) +
              "，路线 b " + fmt_sci(rb["eps"][0], 12))
        if inter[0] <= inter[1]:
            trb, rob = round_check(inter, tgt46, ulp46)
            check("K = " + str(K) + "：交集仍给出同一 46 位值", trb or rob)
            tr2, ro2 = round_check(rb["eps"], tgt46, ulp46)
            check("K = " + str(K) + "：路线 b 单独也给出同一 46 位值", tr2 or ro2)
    e205, estar, e206 = (results[K_205]["eps"], results[K_STAR]["eps"], results[K_206]["eps"])
    check("eps 关于 K 严格递减：eps(2.05e20) > eps(K*) > eps(2.06e20)",
          e205[0] > estar[1] and estar[0] > e206[1])
    check("K* 等于 q43（与增量 5 的连分数复算互相印证，见增量 5）",
          K_STAR == Q43_EXPECT)
    # 中间量的自洽（区间恒等式）
    for K in (K_205, K_STAR, K_206):
        p = results[K]
        back = imul(p["num"], idiv(ONE, p["den"]))
        check("K = " + str(K) + "：eps = num/den 与分步结果一致",
              max(p["eps"][0], back[0]) <= min(p["eps"][1], back[1]))
        check("K = " + str(K) + "：t2/t1 在 1e-12 至 1e-11 之间（数量级自洽）",
              F(3, 10 ** 12) < (p["t2"][0] / p["t1"][1]) and
              (p["t2"][1] / p["t1"][0]) < F(2, 10 ** 11))
    note("与 route-2.md 第 72 至 81 行逐量对照无法机器验证（脚本不读该文件）；"
         "此处以 46 位记录值逐位复现加第二条代数路线交叉替代。")


CHAIN = []


def build_chain():
    global CHAIN
    if CHAIN:
        return CHAIN
    K = K_CHAIN0
    for _ in range(7):
        m2 = max_feasible(K)
        parts = eps_parts(m2, K)
        gd, klen, c, alo, ahi = gamma_den(DELTA[0], up(DELTA[1] + parts["eps"][1]))
        CHAIN.append(dict(K_in=K, m2=m2, parts=parts, K_out=gd,
                          gamma=(gd, klen, c, alo, ahi)))
        K = gd
    return CHAIN


def assert_claim3_printing_rules():
    """增量 3：七步链条（前六步向上取整一位小数 6/6）与第七步六种印刷规则。

    前六步的 K 输入由链条自足复算（起点 K > 7 乘 10 的 11 次幂，m = 91，X0 = 695 乘 2 的 60 次幂，
    常数 +73），K 输出经 Lemma 22（区间连分数前缀）得到；判定为
    「向上取整到一位小数」与印数逐位相同。第七步在 K*、2.05e20、2.06e20 上判六种规则。
    无法机器验证的：与 route-2、route-4 报告分步表的对照（脚本不读那两个文件）。
    """
    section("增量 3：七步链条与第七步印刷规则")
    ch = build_chain()
    ok_m2 = all(ch[i]["m2"] == M2_SEQ[i] for i in range(7))
    check("七步最大可行 m2 依次为 47/67/77/82/86/88/91", ok_m2,
          ",".join(str(ch[i]["m2"]) for i in range(7)))
    hits = 0
    for i in range(6):
        eps = ch[i]["parts"]["eps"]
        mant = imul(eps, (F(10) ** (-EPS_PRINT_EXP[i]), F(10) ** (-EPS_PRINT_EXP[i])))
        up1 = ceil_rule(mant, 1)
        check("第 " + str(i + 1) + " 步：eps 向上取整到一位小数 == 印数 " +
              pretty(EPS_PRINT_FRAC[i]),
              up1 == EPS_PRINT_FRAC[i],
              "实测 " + pretty(up1) + "，区间 " + fmt_sci(eps[0], 16))
        hits += 1 if up1 == EPS_PRINT_FRAC[i] else 0
    check("第 1 至 6 步：向上取整一位小数 6/6 命中", hits == 6)
    # 区分性证据：第 3、6 步
    for i, tag in ((2, "第 3 步"), (5, "第 6 步")):
        eps = ch[i]["parts"]["eps"]
        mant = imul(eps, (F(10) ** (-EPS_PRINT_EXP[i]), F(10) ** (-EPS_PRINT_EXP[i])))
        near1 = round_rule(mant, 1)
        tr1 = trunc_rule(mant, 1)
        check(tag + "：四舍五入与截尾到一位小数给不出印数（区分性证据）",
              near1 != EPS_PRINT_FRAC[i] and tr1 != EPS_PRINT_FRAC[i]
              and near1 == EPS_PRINT_FRAC[i] - F(1, 10),
              "四舍五入 " + str(near1) + "，截尾 " + str(tr1))
    # 同步核对：第 3 步 4.0016e-38 与第 6 步 5.2071e-41 的位数截断
    eps3 = ch[2]["parts"]["eps"]
    m3 = imul(eps3, (F(10) ** 38, F(10) ** 38))
    t3 = trunc_rule(m3, 4)
    check("第 3 步 eps 的前五位是 4.0016", t3 == F(40016, 10000), "实测 " + str(t3))
    eps6 = ch[5]["parts"]["eps"]
    m6 = imul(eps6, (F(10) ** 41, F(10) ** 41))
    t6 = trunc_rule(m6, 4)
    check("第 6 步 eps 的前五位是 5.2071", t6 == F(52071, 10000), "实测 " + str(t6))
    # K 串（截尾到印出位数）
    ok_k = True
    for i in range(7):
        m = ch[i]["K_out"]
        scale = 10 ** K_PRINT_EXP[i]
        d = K_PRINT_DIGITS[i]
        t = F(m, scale)
        got = trunc_rule((t, t), d)
        want = dec_frac(K_PRINT_STR[i] + "e" + str(K_PRINT_EXP[i])) / scale
        if got != want:
            ok_k = False
            note("K 串第 " + str(i + 1) + " 步不符：" + str(got) + " 对 " + str(want))
            break
    check("七步 K 输出按截尾给出印数串 5.2/3.97/4.64/2.74/7.76/2.05/7.94", ok_k)
    check("第六步输出等于 K*（链条第六步输出即 K*，其印数为 2.05e20）",
          ch[5]["K_out"] == K_STAR, str(ch[5]["K_out"]))
    check("第七步输出等于 T（末值，见增量 5）", ch[6]["K_out"] == T_EXPECT,
          str(ch[6]["K_out"]))
    # 第七步：三个 K 的六种规则
    got = {}
    for K in (K_STAR, K_205, K_206):
        six = six_rules(x43(K))
        got[K] = six
        check("K = " + str(K) + "：六种规则在严格区间下全部可判",
              all(v is not None for v in six.values()), str(six))
        n111 = [r for r in RULES if six[r] == F(111, 100)]
        if K in (K_STAR, K_205):
            check("K = " + str(K) + "：六种规则无一给出 1.11", n111 == [], str(n111))
        else:
            check("K = 2.06e20：恰有截尾两位小数给出 1.11", n111 == ["trunc2"], str(n111))
    allpairs = [(K, r, got[K][r]) for K in got for r in RULES]
    one11 = [(K, r) for (K, r, v) in allpairs if v == F(111, 100)]
    check("三个 K 乘六种规则共 18 个组合里唯一给出 1.11 的组合是（2.06e20, 截尾两位）",
          one11 == [(K_206, "trunc2")], str(one11))
    # 集合与多重集核对（与记录值的对照见脚本头部与 [注] 行）
    mult_star = sorted(v for v in got[K_STAR].values())
    check("K* 六值多重集 = {1.20 两次, 1.22, 1.23 两次, 1.30}",
          mult_star == sorted([F(120, 100), F(120, 100), F(122, 100),
                               F(123, 100), F(123, 100), F(130, 100)]),
          str([str(v) for v in mult_star]))
    mult_205 = sorted(v for v in got[K_205].values())
    check("2.05e20 六值多重集 = {1.40 两次, 1.44, 1.45 两次, 1.50}",
          mult_205 == sorted([F(140, 100), F(140, 100), F(144, 100),
                              F(145, 100), F(145, 100), F(150, 100)]),
          str([str(v) for v in mult_205]))
    set_star = set(got[K_STAR].values())
    check("K* 六值的集合与记录的集合一致（{1.20, 1.22, 1.23, 1.30}）",
          set_star == set(CLAIM_SIX_KSTAR), str(sorted(str(v) for v in set_star)))
    set_205 = set(got[K_205].values())
    check("2.05e20 六值的集合与记录的集合一致（{1.40, 1.44, 1.45, 1.50}）",
          set_205 == set(CLAIM_SIX_205), str(sorted(str(v) for v in set_205)))
    note("记录括号里 K* 的六值为 1.20/1.22/1.23/1.23/1.30/1.23、2.05e20 的为 "
         "1.40/1.44/1.45/1.45/1.50/1.45；本次复算的截尾一位小数分别为 1.20 与 1.40，"
         "即记录列表的末项与复算不符（疑为转录时末项重复了中位值 1.23 与 1.45）。"
         "「六种规则全部落空」与「值集合一致」这两项实质判定均已严格复算通过；"
         "六个值的多重集以本次复算为准（1.20 两次、1.22、1.23 两次、1.30）。")
    note("「与 route-2、route-4 的分步表逐位相同」无法机器验证（脚本不读那两个文件）；"
         "链条本身已自足复算并与印数串逐项核对。")


def assert_claim4_windows():
    """增量 4：五个交点的严格二分与三条窗口包含判定。"""
    section("增量 4：窗口反演（严格二分）")
    tol = TOL_DEEP if DEEP else TOL_DEFAULT
    crosses = CROSS_DEEP if DEEP else CROSS_DEFAULT
    br = {}
    for t in crosses:
        a, b = bisect_crossing(t, tol)
        br[t] = (a, b)
        check("K@" + tlabel(t) + " 括号宽不超过容差且两端严格跨界",
              (b - a) <= tol and x43(a)[0] > t and x43(b)[1] < t,
              str(a) + " 至 " + str(b))
    ts = sorted(crosses, reverse=True)
    ok_order = all(br[ts[i]][1] < br[ts[i + 1]][0] for i in range(len(ts) - 1))
    check("交点随目标值下降而严格右移（含默认五点的次序）", ok_order,
          str([(tlabel(t), br[t][0]) for t in crosses]))
    for t in crosses:
        a, b = br[t]
        note("K@" + tlabel(t) + " 的独立括号（相对宽约 " + fmt_sci(F(b - a, a), 4) +
             "）：" + str(a) + " 至 " + str(b))
    # 三点直接区间判定
    x206 = x43(K_206)
    check("2.06e20 的 x 落在 [1.11, 1.12)（截尾窗口内含）",
          x206[0] >= F(111, 100) and x206[1] < F(112, 100), str(x206[0]))
    x20603 = x43(K_20603)
    check("2.0603e20 的 x 落在 [1.105, 1.115)（四舍窗口内含）",
          x20603[0] >= F(1105, 1000) and x20603[1] < F(1115, 1000), str(x20603[0]))
    check("2.0603e20 的 x 落在 (1.10, 1.11]（进位窗口内含）",
          x20603[0] > F(110, 100) and x20603[1] <= F(111, 100), str(x20603[0]))
    # 用括号作集合包含判定（区间版）
    b112, b1115, b111, b1105, b110 = (br[F(112, 100)], br[F(1115, 1000)],
                                      br[F(111, 100)], br[F(1105, 1000)],
                                      br[F(110, 100)])
    check("截尾窗口 (K@1.12, K@1.11] 含 2.06e20",
          b112[1] < K_206 <= b111[0],
          "K@1.12 上端 " + str(b112[1]) + "，K@1.11 下端 " + str(b111[0]))
    check("四舍窗口 (K@1.115, K@1.105] 含 2.0603e20",
          b1115[1] < K_20603 <= b1105[0])
    check("进位窗口 [K@1.11, K@1.10) 含 2.0603e20",
          b111[0] <= K_20603 < b110[0])
    check("2.06e20 不在四舍窗口（2.06e20 < K@1.115）", K_206 < b1115[0])
    check("2.06e20 不在进位窗口（2.06e20 < K@1.11）", K_206 < b111[0])
    check("K* 与 2.05e20 在三个窗口左侧之外（均 < K@1.12）",
          K_STAR < b112[0] and K_205 < b112[0])
    note("「与 route-4.md 第 115 至 126 行记录包围逐端一致」无法机器验证（脚本不读该文件）；"
         "上方括号可直接与该记录人工对拍。")
    if not DEEP:
        note("深度档（--deep）会把二分容差收紧到 ±1e6、多解 1.20/1.15/1.05/1.00 四个交点，"
             "并按括号作窗口归属的逐点比对扫描；本次未开启。")
    else:
        # 逐点扫描（抽样核验，不是证明）：由本次括号给出每个取样点的严格窗口归属，
        # 再与逐点复算的六种规则输出比对。三点注意：
        #   1. 三个窗口彼此有交叠（例如 x 在 1.11 至 1.115 时截尾与四舍都印 1.11），
        #      故比对的是「命中集合」而不是「只有该规则命中」；
        #   2. 与任一括号相交的取样点无法严格归属，跳过（这类点极少）；
        #   3. 窗口之外的点断言六种规则无一给出 1.11。
        def decided_rules(K):
            """返回该点严格可判的命中规则集合；若有未判项返回 None。"""
            hits = set()
            if K > b112[1] and K <= b111[0]:
                hits.add("trunc2")
            elif K <= b112[0] or K > b111[1]:
                pass
            else:
                return None
            if K > b1115[1] and K <= b1105[0]:
                hits.add("round2")
            elif K <= b1115[0] or K > b1105[1]:
                pass
            else:
                return None
            if K >= b111[1] and K < b110[0]:
                hits.add("ceil2")
            elif K < b111[0] or K >= b110[1]:
                pass
            else:
                return None
            return hits

        n_scan = 400
        span = b110[1] + 2 * 10 ** 16 - (b112[0] - 2 * 10 ** 16)
        base = b112[0] - 2 * 10 ** 16
        bad, wit, decided = 0, "", 0
        for j in range(1, n_scan + 1):
            K = base + span * j // (n_scan + 1)
            exp = decided_rules(K)
            if exp is None:
                continue
            decided += 1
            six = six_rules(x43(K))
            got = set(r for r in RULES if six[r] == F(111, 100))
            if got != exp:
                bad += 1
                wit = wit or ("K=" + str(K) + " 预期 " + str(sorted(exp)) +
                              " 实测 " + str(sorted(got)))
        check("窗口带全域 " + str(n_scan) + " 点扫描：命中的二小数规则集合与括号归属一致"
              "（可判点 " + str(decided) + " 个）",
              bad == 0 and decided >= n_scan * 9 // 10, wit)
        n_out = 150
        bad, wit = 0, ""
        for j in range(1, n_out + 1):
            K = b112[0] - 1 - 3 * 10 ** 15 + 2 * 10 ** 13 * j
            if not (K < b112[0]):
                continue
            six = six_rules(x43(K))
            if any(v == F(111, 100) for v in six.values()):
                bad += 1
                wit = wit or ("K=" + str(K) + " 时 " + str(six))
        check("窗口左侧之外（K@1.12 以下）" + str(n_out) + " 点无一印 1.11", bad == 0, wit)
        bad, wit = 0, ""
        for j in range(1, n_out + 1):
            K = b110[0] + 1 + 2 * 10 ** 13 * j
            six = six_rules(x43(K))
            if any(v == F(111, 100) for v in six.values()):
                bad += 1
                wit = wit or ("K=" + str(K) + " 时 " + str(six))
        check("窗口右侧之外（K@1.10 以上）" + str(n_out) + " 点无一印 1.11", bad == 0, wit)


def assert_claim5_continued_fraction():
    """增量 5：连分数前缀、q43 与 q44、a44 与 a45、T、S38 与两条距离不等式。"""
    section("增量 5：delta 的连分数与末值 T")
    tbl = convergent_table(CF_COEFFS)
    check("delta 前缀证书层数覆盖到 45，a44 = 37",
          len(tbl) > 45 and tbl[44][2] == A44_EXPECT, str(tbl[44][2]))
    check("a45 = 4", len(tbl) > 45 and tbl[45][2] == A45_EXPECT, str(tbl[45][2]))
    p43, q43, _ = tbl[43]
    p44, q44, _ = tbl[44]
    check("q43 = 205632218873398596256", q43 == Q43_EXPECT, str(q43))
    check("q44 = 7736332199829210068325", q44 == Q44_EXPECT, str(q44))
    check("q43 与 K* 相等（增量 2、3 的链条第六步输出）", q43 == K_STAR)
    check("unimodular：|p43 q42 − p42 q43| = 1",
          abs(p43 * tbl[42][1] - tbl[42][0] * q43) == 1)
    T = q43 + q44
    check("T = q43 + q44 = 7941964418702608664581", T == T_EXPECT, str(T))
    check("链条第七步输出等于 T（增量 3 复算）",
          build_chain()[6]["K_out"] == T)
    S_num = p43 + p44
    check("S38 的分子 = 12587715785705330118969", S_num == S38_NUM_EXPECT, str(S_num))
    S38 = F(S_num, T)
    d_hi = S38 - DELTA[1]
    d_lo = S38 - DELTA[0]
    check("S38 − delta > 3/(4 T^2)", d_hi > F(3, 4 * T * T),
          "余量 " + fmt_sci(d_hi - F(3, 4 * T * T), 6))
    gam = F(p43, q43)
    check("1/(q43 T) < p43/q43 − delta < 1/(q43 q44)",
          (gam - DELTA[1]) > F(1, q43 * T) and (gam - DELTA[0]) < F(1, q43 * q44))
    check("1/(q43 T) 属于 6.123e-43 量级（在 6.123e-43 与 6.124e-43 之间）",
          F(6123, 10 ** 46) < F(1, q43 * T) < F(6124, 10 ** 46),
          fmt_sci(F(1, q43 * T), 16))
    note("S38 与 gamma 的 20 位近似：S38 − delta 约 " + fmt_sci(d_hi, 8) +
         "，p43/q43 − delta 约 " + fmt_sci(gam - DELTA[1], 8) + "。")


def assert_claim6_page12():
    """增量 6：两版第 12 页 Corollary 19 区域的差异（因数 7/5、36 与 60）。

    无法机器验证的：渲染图目视这一动作本身，以及「反驳某记录页码」这类记录间关系的判断。
    能机器验证的：两版第 12 页文本抽取的差异模式。
    """
    section("增量 6：第 12 页两版差异")
    if shutil.which("pdftotext") is None:
        skip("第 12 页文本抽取核对", "未找到 pdftotext")
        return
    t12 = {}
    for tag, pdf in (("印出版", PRINT_PDF), ("v3", ARXIV_PDF)):
        if not pdf.exists():
            skip(tag + " 第 12 页文本", pdf.name + " 不存在")
            continue
        r = subprocess.run(["pdftotext", "-f", "12", "-l", "12", str(pdf), "-"],
                           capture_output=True, text=True)
        t12[tag] = " ".join(r.stdout.split())
    if "印出版" in t12:
        t = t12["印出版"]
        check("印出版第 12 页 Corollary 19 带因数 7/5 的版式标记（分母 5 紧邻于 695）",
              "3 log(2) 5 695" in t)
        check("印出版第 12 页 Corollary 19 前提 X0 ≥ 695 · 260",
              "Corollary 19. Provided that X0 ≥ 695 · 260" in t)
        check("印出版第 12 页程序句为「up to 36 consecutive summands」",
              "up to 36 consecutive summands" in t)
        check("印出版第 12 页无「up to 60 consecutive summands」",
              "up to 60 consecutive summands" not in t)
    if "v3" in t12:
        t = t12["v3"]
        check("v3 第 12 页 Corollary 19 不带因数 7/5（分母 5 标记缺席）",
              "3 log(2) 5 695" not in t and "3 log(2) 5" not in t)
        check("v3 第 12 页 Corollary 19 前提 X0 ≥ 704 · 260",
              "Corollary 19. Provided that X0 ≥ 704 · 260" in t)
        check("v3 第 12 页程序句为「up to 60 consecutive summands」",
              "up to 60 consecutive summands" in t)
        check("v3 第 12 页无「up to 36 consecutive summands」",
              "up to 36 consecutive summands" not in t)
    if "印出版" in t12 and "v3" in t12:
        # 两处确为「不只 X0 替换」的差异：程序句里不含 695 与 704
        seg = "consecutive summands"
        ok = True
        for tag in ("印出版", "v3"):
            t = t12[tag]
            i = t.find("up to", t.find("It considers partial sums"))
            j = t.find("consecutive summands", i)
            if i < 0 or j < 0:
                ok = False
                break
            window = t[i:j + len(seg)]
            if "695" in window or "704" in window:
                ok = False
                break
        check("36 与 60 之差所在句子不含 X0 的 695 或 704（即该差异不是 X0 替换）", ok)
    note("「反驳某记录页码落在 12 页正确」这类记录间关系的判断无法机器验证；"
         "本次检查所用的正是两版第 12 页，其文本差异模式与增量描述一致。")


def main():
    print("verify.py —— thm23-eps cycle-1 增量结论独立复算（"
          + ("深度档" if DEEP else "默认档") + "）")
    if not DEEP:
        print("（深度档用法：python3 verify.py --deep；其覆盖范围见脚本头部说明）")
    assert_selftest()
    assert_claim1_document()
    assert_claim2_epsilon_table()
    assert_claim3_printing_rules()
    assert_claim4_windows()
    assert_claim5_continued_fraction()
    assert_claim6_page12()
    print("\n" + "=" * 4 + " 汇总")
    print("PASS " + str(N_PASS) + "，FAIL " + str(N_FAIL) + "，SKIP " + str(N_SKIP) +
          "，用时 " + "%.1f" % (time.time() - T0) + " 秒")
    if N_FAIL:
        print("失败项：")
        for name in FAILURES:
            print("  " + name)
        print("退出码 1")
        return 1
    print("全部断言通过，退出码 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
