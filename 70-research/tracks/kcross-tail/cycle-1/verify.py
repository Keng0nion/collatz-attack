#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kcross-tail cycle-1 复算闸门 verify.py（2026 年 10 月 28 日）。

落点：70-research/tracks/kcross-tail/cycle-1/verify.py
用法：
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" verify.py
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" verify.py --deep

对本轮四条增量结论各写一个断言函数，一切判定用精确整数、有理数与自写区间引擎完成：

  结论 1（T 的两侧严格区间与证书数值核心）见 assert_conclusion_1()：
    复算 δ、C；默认档从 r2、k1 日志解析 T_hi、T_lo、KA、KB（本轮结论所引出处）并用本引擎
    在端点独立判号（S(T_hi) > 0、S(T_lo) < 0），深度档另跑 400 步二分复现端点并与日志比对；
    核分母结构、精确宽度、13 位截断、60 位截断相同、[T_hi, T_lo] ⊆ [KA, KB] 两侧余量；
    核 A1 全部 92 项余量（最小三项位置与读数）、B2 负余量；核 K* 格 ε 梯子（83 至 91）
    与 k3_run_a.out 打印串的 20 位有效数字比对；门禁元事实（文件 md5、行数、SUMMARY）。
  结论 2（T = R 的纸面论证）见 assert_conclusion_2()：
    「完整纸面论证、逻辑层未见缺口」「非降性对本命题不必要」等属阅读与逻辑判断，
    无法机器验证（函数内明示并跳过）；只复算其数值前提：γ 的连分数身份（由本引擎的
    δ、β 证书前缀独立重建）、γ ∈ (δ, δ + ε_opt(K*))、γ 分母恰为 K*，以及单模括号加
    Farey 引理的实例（区间 (δ_lo, γ) 的最小分母 = 双亲分母和）。
  结论 3（分岔窗口修正）见 assert_conclusion_3()：
    复算门槛 c_90、c_89（30 位打印与日志串一致）与两格相对窗口宽——本引擎直接比较
    numerator(j) 与 numerator(j−1) 的严格区间并二分变号点；核 12 位与 15 位截断、
    旧值 2e-24 与 1.5361313e-23 的排除、log2(1 + 2^{-C})/C 的读数；结论所引 15 位串
    的出处（日志左括号端二次截断）单独核对，并与真窗口宽的 15 位截断并列打印。
  结论 4（K* 格清单记账、两个不动点、账本引用卫生）见 assert_conclusion_4()：
    复算可行集与 argmin、ε_opt(K*) 的 30 位读数、q41 格与 γ 落点；用自写 Stern-Brocot
    复算 Ψ(K*) = K* 与 Ψ(q41) = q41；复算清单 442 = 220 + 222、cap 后 438、差集 4 条
    分母 ≥ K*（最小恰为 K*）与「内 0、外 438、未定 0」分类；核账本四件 md5。

自足与阅读纪律：
  * 主判据（第 0 至 4 组）全部自算：自写区间引擎，不 import 项目任何区间库
    （kc_rig、r2_rig、k3_rig、r4_common 等在主判据里一律不用）；
    不读取任何 route-*.md 或 materials.md 里的数字。
  * 第 5 组「跨库对拍」是对照段（对应本轨道 plan.md 验收标准的「至少两库同值」），
    读 kc_rig 与 r2_rig 作同值比对，已在输出中单独标注。
  * 只对下列结果文件做对照（每处的用途在行内注明）：
      k3_run_a.out（结论 1 的 20 位比对对象）、r2_threshold_cert.log 与
      k1_threshold_cert.log（T、KA、KB 精确有理的出处核对）、r4b2_window_probe.out
      （c_j 与窗口右端打印串、15 位串出处核对）、k3_run_e.out 与 r3_list_search.out
      （清单计数原样串）、kcross-proof 闸门 verify.py 与其 results/verify.out（元事实）、
      kcross-tail 账本四件（md5；深度档另重跑 cite_check.py 与 ledger_numbers.py）。
  * 默认档与深度档覆盖范围（本文件末尾 main() 也会打印）：
      默认档（轻量，数秒级）：结论 1 的全部结构读数与证书数值核心（A1 92 项、B1、B2、
              梯子 9 格、端点独立判号；端点解析自本轮结论所引日志）；结论 2 的全部数值前提；
              结论 3 的 c_j 复算、在日志 bracket 两端独立判号（由此夹住变号点，12 位截断与
              旧值排除成立）、15 位串出处核对、log2 恒等读数；结论 4 的可行集、argmin、
              两个不动点、清单记账、四件 md5。A5 域闭合只抽检 q ≤ 64。
      深度档（--deep，重算量较大项，约一分至两分）：另跑 400 步二分复现 T_hi、T_lo、
              KA、KB 并与日志逐字符比对；两格窗口各 240 步二分（真窗口宽的 15 位与 30 位
              截断）；A5 完整 6456 项扫描（复核最坏位置 q = 6291、p = 9971）；重跑
              cite_check.py 与 ledger_numbers.py；在临时镜像目录里重跑 kcross-proof 闸门
              （复现其历史 EXIT=0 并核输出与登记文件逐字节相同），并原地重跑一次以登记其
              「7.2b 自指伪影」的非幂等性（详见 1.15a 与 1.15b 的说明）。
              三个子进程各自读取自己的核对对象，本脚本只取退出码、总结行与输出哈希。

退出码：全部判据通过 = 0；任一失败 = 1，逐条打印计算值与声称值（最小反例）。

运行与环境：主判据只用 Python 标准库（任意 Python 3.7 及以上；已用 20-experiments 的
venv 解释器与系统 python3 各实跑通过）；默认档数秒级，深度档约一到两分钟。
输出：打印到 stdout，并同时写入 <脚本目录>/results/verify.out（本轨道 plan.md 列出的
产物；目录会自动创建；若 stdout 已经指向该文件则不重复写）。--help / -h 打印用法。
脚本从不改写仓库文件（深度档的镜像实验只在系统临时目录进行并当场清理）。
"""

import hashlib
import os
import re
import subprocess
import sys
import time
from fractions import Fraction as F
from functools import lru_cache
from math import gcd

T_START = time.time()
REPO = "/Users/luna/Documents/math IA/collatz-attack"
KPROOF = REPO + "/70-research/tracks/kcross-proof/cycle-1"
KPROOF_SCR = KPROOF + "/scripts"
KPROOF_RES = KPROOF_SCR + "/results"
KTAIL = REPO + "/70-research/tracks/kcross-tail/cycle-1"
KTAIL_SCR = KTAIL + "/scripts"
KTAIL_RES = KTAIL_SCR + "/results"
VENV_PY = REPO + "/20-experiments/.venv/bin/python"

DEEP = "--deep" in sys.argv[1:]

if ("--help" in sys.argv[1:]) or ("-h" in sys.argv[1:]):
    print("用法：verify.py [--deep]")
    print("  默认档（秒级）：四条增量结论的轻量复算（端点与结构读数、证书数值核心、端点判号、")
    print("                  清单记账、两个不动点、账本 md5、跨库对拍对照）。")
    print("  --deep（约两三分钟）：另跑 400 步二分复现端点、两格 240 步窗口二分、A5 全量")
    print("                  6456 项扫描，并重跑 cite_check.py、ledger_numbers.py 与 kcross-proof")
    print("                  闸门（镜像与原地两种方式）。")
    print("输出：stdout，并同时写入 <脚本目录>/results/verify.out（若 stdout 未指向该文件）。")
    sys.exit(0)


class _Tee:
    """把输出同时写到第二个流（用于产出 results/verify.out；逐行刷新保中途可见）。"""

    def __init__(self, first, second):
        self._first = first
        self._second = second

    def write(self, s):
        self._first.write(s)
        self._second.write(s)
        if "\n" in s:
            self.flush()
        return len(s)

    def flush(self):
        for st in (self._first, self._second):
            try:
                st.flush()
            except Exception:
                pass


_TEE_FILE = None


def install_output_tee():
    """把 stdout 再接一份到 <脚本目录>/results/verify.out（计划书列出的产物）。

    若 stdout 已经指向该文件（外层重定向），则不重复写；写入失败时只提示、不影响判定。
    """
    global _TEE_FILE
    target = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "verify.out")
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        same = False
        try:
            a, b = os.fstat(1), os.stat(target)
            same = (a.st_dev == b.st_dev and a.st_ino == b.st_ino)
        except OSError:
            same = False
        if same:
            return target, None
        _TEE_FILE = open(target, "w", encoding="utf-8")
        base = sys.__stdout__ if sys.__stdout__ is not None else sys.stdout
        sys.stdout = _Tee(base, _TEE_FILE)
        return target, _TEE_FILE
    except OSError as exc:
        print("  [注意] 无法写入 %s（%s）；只输出到 stdout" % (target, exc))
        return target, None

FAILS = []
NCHK = 0


def check(cid, ok, msg):
    global NCHK
    NCHK += 1
    ok = bool(ok)
    if not ok:
        FAILS.append((cid, msg))
    print("  [%s] %-7s %s" % ("PASS" if ok else "FAIL", cid, msg))
    return ok


def note(msg):
    print("         · %s" % msg)


def section(title):
    print()
    print("=" * 84)
    print(title)
    print("=" * 84)


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError as exc:
        print("  [FAIL] 输入文件缺失或不可读：%s（%s）" % (path, exc))
        sys.exit(1)


def md5_of(path):
    try:
        h = hashlib.md5()
        with open(path, "rb") as fh:
            h.update(fh.read())
        return h.hexdigest()
    except OSError as exc:
        print("  [FAIL] 输入文件缺失或不可读：%s（%s）" % (path, exc))
        sys.exit(1)


# =====================================================================
# [引擎] 自写精确有理区间引擎（与项目区间库无关；一切判定用 Fraction）
# =====================================================================
GRID = 10 ** 190          # 绝对取整网格 1e-190：判据所需的区间宽度约 1e-171，仍留足余量
TOL = F(1, 10 ** 240)     # 级数截断目标


def fl(x):
    x = F(x)
    return x.numerator // x.denominator


def rd(x):
    """向下取整到 1/GRID 网格（保持下界性质；直接整数运算，不经中间 Fraction）。"""
    return F(x.numerator * GRID // x.denominator, GRID)


def ru(x):
    """向上取整到 1/GRID 网格（保持上界性质）。"""
    return F(-((-x.numerator * GRID) // x.denominator), GRID)


def atanh_iv(x):
    """atanh(x) 的严格区间（0 < x < 1）：前若干项加显式尾界。

    atanh(x) = sum_{k>=0} x^{2k+1}/(2k+1)；第 k 项之后的尾界为
    x^{2k+3}/((2k+3)(1−x^2))（各项单调递减的正级数）。
    下界与上界各用一条定向取整的部分和（若共用一条向下取整的和，
    多次加法的累积舍入可达 项数×网格 ≈ 3e-238，会把上界压到真值之下）。
    """
    x = F(x)
    assert 0 < x < 1
    x2 = x * x
    slo = F(0)
    shi = F(0)
    p = x
    k = 0
    while True:
        term = p / (2 * k + 1)
        slo = rd(slo + term)
        shi = ru(shi + term)
        tail = p * x2 / ((2 * k + 3) * (1 - x2))
        if tail <= TOL:
            return slo, ru(shi + tail)
        p *= x2
        k += 1


def ln2_iv():
    """ln2 = 2·atanh(1/3)。"""
    a = atanh_iv(F(1, 3))
    return rd(2 * a[0]), ru(2 * a[1])


def ln3_iv():
    """ln3 = ln2 + 2·atanh(1/5)（atanh(1/5) = (1/2)·ln(3/2)）。"""
    a = atanh_iv(F(1, 5))
    l2 = ln2_iv()
    return rd(l2[0] + 2 * a[0]), ru(l2[1] + 2 * a[1])


def ln_pos(x):
    """ln(x) 的严格区间（x > 0 有理数）：2 的幂分解 + atanh 级数。"""
    x = F(x)
    assert x > 0
    if x == 1:
        return F(0), F(0)
    if x < 1:
        lo, hi = ln_pos(1 / x)
        return -hi, -lo
    k = x.numerator.bit_length() - x.denominator.bit_length()
    while F(2) ** k > x:
        k -= 1
    while F(2) ** (k + 1) <= x:
        k += 1
    m = x / F(2) ** k
    t = (m - 1) / (m + 1)
    a = atanh_iv(t) if t > 0 else (F(0), F(0))
    l2 = ln2_iv()
    return rd(k * l2[0] + 2 * a[0]), ru(k * l2[1] + 2 * a[1])


def exp_pos(y_lo, y_hi):
    """exp 的严格区间，0 <= y_lo <= y_hi：按 2 的幂缩至 [0,1]，Taylor 加尾界，再平方回代。"""
    y_lo, y_hi = F(y_lo), F(y_hi)
    assert 0 <= y_lo <= y_hi
    if y_hi == 0:
        return F(1), F(1)
    # 缩放因子取「y / 2^s <= 1/64」：Taylor 项数压到约 75 项，代价是少量额外平方
    s = 0
    lim = 64 * y_hi
    while F(2) ** s < lim:
        s += 1
    tl, th = y_lo / F(2) ** s, y_hi / F(2) ** s
    lo = rd(F(1))
    hi = ru(F(1))
    tlo = thi = F(1)
    i = 1
    while True:
        tlo = rd(tlo * tl / i)
        thi = ru(thi * th / i)
        lo = rd(lo + tlo)
        hi = ru(hi + thi)
        if i >= 8 and thi <= TOL:
            break
        i += 1
        if i > 400:
            break
    tail = ru(thi / (1 - th / (i + 2)))
    hi = ru(hi + tail)
    for _ in range(s):
        lo, hi = rd(lo * lo), ru(hi * hi)
    return lo, hi


def exp_any(y_lo, y_hi):
    """exp 的严格区间，允许负参数（用 1/exp(−y) 走正值分支）。"""
    y_lo, y_hi = F(y_lo), F(y_hi)
    assert y_lo <= y_hi
    if y_lo >= 0:
        return exp_pos(y_lo, y_hi)
    if y_hi <= 0:
        a = exp_pos(-y_hi, -y_lo)
        return rd(F(1) / a[1]), ru(F(1) / a[0])
    assert y_lo > -1
    lo = rd(F(1) + y_lo)
    hi = ru(exp_pos(y_hi, y_hi)[1])
    return lo, hi


def ln1m_iv(u_lo, u_hi):
    """ln(1 − u) 在 u ∈ [u_lo, u_hi] ⊂ [0, 1/2) 上的严格区间。

    S(u) = −ln(1 − u) = sum_{j>=1} u^j/j 关于 u 严格增，故
    ln(1−u) ∈ [−S(u_hi), −S(u_lo)]；两端各用定向取整的部分和加尾界。
    """
    u_lo, u_hi = F(u_lo), F(u_hi)
    assert 0 <= u_lo <= u_hi < F(1, 2)
    slo = F(0)
    p = F(1)
    j = 0
    while True:
        j += 1
        p = p * u_lo
        slo = rd(slo + p / j)
        if p <= TOL or j >= 120:
            break
    shi = F(0)
    p = F(1)
    j = 0
    while True:
        j += 1
        p = p * u_hi
        shi = ru(shi + p / j)
        if p * u_hi / ((j + 1) * (1 - u_hi)) <= TOL or j >= 120:
            break
    tail = ru(p * u_hi / ((j + 1) * (1 - u_hi)))
    return -(shi + tail), -slo


# ---- 模块级常数：ln2、δ、C、X0 ----
LN2 = ln2_iv()
L3 = ln3_iv()
DLO, DHI = rd(L3[0] / LN2[1]), ru(L3[1] / LN2[0])       # delta = ln3/ln2 的严格区间


def C_iv():
    """C = log2((162/97)·X0) = 60 + ln(112590/97)/ln2 的严格区间。"""
    lnr = ln_pos(F(112590, 97))
    return rd(60 + lnr[0] / LN2[1]), ru(60 + lnr[1] / LN2[0])


CLO, CHI = C_iv()
X0 = 695 * 2 ** 60

# ---- 定理 21 的量 ----
V_COARSE = 2048            # v_lo >= 此值时走解析压掉分支（2^2048 有 617 位，安全可表示）


def dpow(d, n, up):
    """d^n 的定向幂（n 整数 >= 1），每步向指定方向取整。"""
    r = F(1)
    b = F(d)
    e = n
    while e:
        if e & 1:
            r = ru(r * b) if up else rd(r * b)
        e >>= 1
        if e:
            b = ru(b * b) if up else rd(b * b)
    return r


@lru_cache(maxsize=None)
def delta_pow_iv(n):
    return dpow(DLO, n, False), dpow(DHI, n, True)


@lru_cache(maxsize=None)
def geom_iv(n):
    """geom(n) = (δ^n − 1)/(δ − 1) 的严格区间（关于 δ 严格增）。"""
    plo, phi = delta_pow_iv(n)
    return rd((plo - 1) / (DLO - 1)), ru((phi - 1) / (DHI - 1))


def v_iv(m2, K):
    """v = (m2/92)·K·(δ − 1)/(δ^{m2} − 1) 的严格区间（正四角法则）。"""
    c = F(m2, 92) * F(K)
    plo, phi = delta_pow_iv(m2)
    return rd(c * (DLO - 1) / (phi - 1)), ru(c * (DHI - 1) / (plo - 1))


def pow2_iv(v_lo, v_hi):
    """2^v 的严格区间（0 <= v_lo <= v_hi）。"""
    return exp_pos(rd(F(v_lo) * LN2[0]), ru(F(v_hi) * LN2[1]))


def tpow_delta_iv(v_lo, v_hi, P):
    """(2^v − 1)^δ 的严格区间，复用 P = 2^v 的区间。

    恒等式 (2^v − 1)^δ = 2^{vδ}·(1 − 2^{−v})^δ；两个因子都单调，取端点。
    """
    f1 = exp_pos(rd(F(v_lo) * DLO * LN2[0]), ru(F(v_hi) * DHI * LN2[1]))
    u_lo = rd(F(1) / P[1])
    u_hi = ru(F(1) / P[0])
    L_lo, L_hi = ln1m_iv(u_lo, u_hi)
    z_lo = rd(DHI * L_lo)
    z_hi = ru(DLO * L_hi)
    f2 = exp_any(z_lo, z_hi)
    return rd(f1[0] * f2[0]), ru(f1[1] * f2[1])


def A_of(m2):
    """Theorem 21 与证明末段的 A(m2)：m2 = 92 取 0；m2 = 91 取 3/X0；其余 (97(92−m2)+73)/(54X0)。"""
    if m2 == 92:
        return F(0)
    if m2 == 91:
        return F(3, X0)
    return F(97 * (92 - m2) + 73, 54 * X0)


def num_iv(m2, K):
    """numerator(m2) = A + 3/(2^v − 1) + 3(m2 − 1)/(2^v − 1)^δ 的严格区间。"""
    A = A_of(m2)
    vlo, vhi = v_iv(m2, K)
    if vlo >= V_COARSE:
        slack = F(3 + 3 * (m2 - 1), 2 ** V_COARSE - 1)
        return rd(A), ru(A + slack)
    P = pow2_iv(vlo, vhi)
    t_lo = rd(P[0] - 1)
    t_hi = ru(P[1] - 1)
    assert t_lo > 0, "2^v − 1 在网格下退化"
    term1 = (rd(F(3) / t_hi), ru(F(3) / t_lo))
    if m2 > 1:
        pt = tpow_delta_iv(vlo, vhi, P)
        term2 = (rd(F(3 * (m2 - 1)) / pt[1]), ru(F(3 * (m2 - 1)) / pt[0]))
    else:
        term2 = (F(0), F(0))
    return rd(A + term1[0] + term2[0]), ru(A + term1[1] + term2[1])


def eps_iv(m2, K):
    """eps(m2, K) = numerator(m2)/(3·K·ln2) 的严格区间。"""
    nlo, nhi = num_iv(m2, K)
    K = F(K)
    den_lo = rd(3 * K * LN2[0])
    den_hi = ru(3 * K * LN2[1])
    return rd(nlo / den_hi), ru(nhi / den_lo)


def feasible_dec(m2, K):
    """geom(m2)·C <= (m2/92)·K 的三值判定（True / False / None）。"""
    g = geom_iv(m2)
    lhs_lo = rd(g[0] * CLO)
    lhs_hi = ru(g[1] * CHI)
    rhs = F(m2, 92) * F(K)
    if lhs_hi <= rhs:
        return True
    if lhs_lo > rhs:
        return False
    return None


# ---- Stern-Brocot：区间内最小分母（自写；Farey 引理的算法版） ----
def simplest_fraction(A, B, cap=20000):
    """区间 (A, B) 内分母最小的分数（精确有理算法）。

    Stern-Brocot 下降加整段跳：括号端点 (x/y, z/w) 保持 z·y − x·w = 1；
    对括号内任意分数 p/q，由 p/q − x/y >= 1/(qy) 与 z/w − p/q >= 1/(qw) 相加得
    q >= y + w，而返回时中项的分母恰为 y + w，故它是最小分母。
    """
    A, B = F(A), F(B)
    assert A < B
    x, y, z, w = 0, 1, 1, 0
    for _ in range(cap):
        kL = fl((A * y - x) / (z - A * w))
        if kL >= 1:
            x, y = x + kL * z, y + kL * w
        kR = fl((z - B * w) / (B * y - x))
        if kR >= 1:
            z, w = z + kR * x, w + kR * y
        mn, md = x + z, y + w
        m = F(mn, md)
        if A < m < B:
            return m
    raise RuntimeError("Stern-Brocot 未收敛")


# ---- 连分数：证书前缀、收敛子 ----
def cf_prefix(lo, hi, maxlen=260):
    """区间 [lo, hi] 内一切点的公共连分数前缀（每步外向取整保包含）。"""
    lo, hi = F(lo), F(hi)
    assert lo < hi
    digits = []
    for _ in range(maxlen):
        n = fl(lo)
        if fl(hi) != n or lo == n:
            break
        digits.append(n)
        lo, hi = rd(F(1) / (hi - n)), ru(F(1) / (lo - n))
    return digits


def cf_convergents(digits):
    p0, q0, p1, q1 = 1, 0, 0, 1
    out = []
    for a in digits:
        p0, q0, p1, q1 = a * p0 + p1, a * q0 + q1, p0, q0
        out.append((p0, q0))
    return out


def cf_value(digits):
    v = F(0)
    for a in reversed(digits):
        v = F(a) + (F(0) if v == 0 else F(1) / v)
    return v


def semiconv_list(digits, k, cap=None, tag="?"):
    """G2 式清单：{[S_0;…;S_{j-1}, m] : 1 <= j <= k+1, 1 <= m <= S_j}。

    项 = (m·p_{j-1} + p_{j-2})/(m·q_{j-1} + q_{j-2})（标准收敛子递推）；
    分母关于 m 严格递增，cap 给定时一旦分母 >= cap 即停（前缀内完备性不受损）。
    """
    conv = [(0, 1), (1, 0)]
    for a in digits:
        conv.append((a * conv[-1][0] + conv[-2][0], a * conv[-1][1] + conv[-2][1]))
    out = []
    for j in range(1, k + 2):
        aj = digits[j]
        pj1, qj1 = conv[j + 1]
        pj2, qj2 = conv[j]
        for m in range(1, aj + 1):
            n = m * pj1 + pj2
            d = m * qj1 + qj2
            if cap is not None and d >= cap:
                break
            out.append((F(n, d), (tag, j, m)))
    return out


# ---- 打印与判定辅助 ----
def trunc_sig(x, n):
    """正有理数的 n 位有效数字十进制截断：返回 (尾数串, 指数)。"""
    x = F(x)
    assert x > 0
    e = 0
    while x >= 10:
        x /= 10
        e += 1
    while x < 1:
        x *= 10
        e -= 1
    m = fl(x * 10 ** (n - 1))
    s = str(m)
    return s[0] + "." + s[1:], e


def sig_str(x, n):
    m, e = trunc_sig(x, n)
    return "%se%+d" % (m, e)


def dec_str(x, nd):
    """正有理数的小数截断：整数部分加 nd 位小数（与项目 dec 同型）。"""
    x = F(x)
    ip = x.numerator // x.denominator
    rem = x.numerator - ip * x.denominator
    out = [str(ip), "."]
    for _ in range(nd):
        rem *= 10
        d = rem // x.denominator
        out.append(str(d))
        rem -= d * x.denominator
    return "".join(out)


def bucket_of(claim, mode="trunc"):
    """把声称串（如 '1.0759105e-163'）化为 [lo, hi) 判定桶。

    mode='trunc'：第 n 位有效数字截断恰等于该串；
    mode='round'：四舍五入到第 n 位有效数字恰等于该串（±半个末位）。
    """
    s = claim.strip()
    neg = s.startswith("-") or s.startswith("−")
    if neg:
        s = s[1:]
    mant, _, ex = s.partition("e")
    e = int(ex)
    digs = mant.replace(".", "")
    n = len(digs)
    val = F(int(digs), 10 ** (n - 1)) * F(10) ** e
    half = F(10) ** (e - n + 1) / 2
    if mode == "trunc":
        lo, hi = val, val + 2 * half
    elif mode == "round":
        lo, hi = val - half, val + half
    else:
        raise ValueError(mode)
    if neg:
        return -hi, -lo
    return lo, hi


def in_bucket(iv, claim, mode="trunc"):
    lo, hi = bucket_of(claim, mode)
    return lo <= iv[0] and iv[1] <= hi


def strip_sig(s):
    t = s.strip().replace(" ", "").split("e")[0].replace(".", "").lstrip("+-")
    return t[:20]


# =====================================================================
# [共享计算] 缓存
# =====================================================================
CACHE = {}


def run_bisection():
    """400 步二分 S(K) = eps(92, K) − (γ − δ)（精确有理中点；第 160 步记 KA、KB）。

    这是重算量最大的单项（约 400 次严格区间求值），只在 --deep 档运行。
    """
    out = {"steps": 0, "stall": None, "KA": None, "KB": None}
    K1, K2 = F(312) * 10 ** 18, F(315) * 10 ** 18
    gd_lo, gd_hi = GAM - DHI, GAM - DLO
    for step in range(400):
        Km = (K1 + K2) / 2
        elo, ehi = eps_iv(92, Km)
        if elo > gd_hi:
            K1 = Km
        elif ehi < gd_lo:
            K2 = Km
        else:
            out["stall"] = (step + 1, Km, (elo, ehi), (gd_lo, gd_hi))
            break
        out["steps"] = step + 1
        if step == 159:
            out["KA"], out["KB"] = K1, K2
    out["T_hi"], out["T_lo"] = K1, K2
    return out


def get_endpoints():
    """端点来源：默认档从 r2、k1 日志解析（本轮结论所引出处）；深度档另跑 400 步二分复现。

    返回 dict：T_hi、T_lo、KA、KB（精确有理，字符串精确解析）、lines_ok（行号与内容核对）、
    repro（深度档的二分结果；默认档为 None）。
    """
    if "end" in CACHE:
        return CACHE["end"]
    lines = read_text(KPROOF_RES + "/r2_threshold_cert.log").splitlines()
    lok2 = len(lines) > 58 and ("T_hi 的精确有理" in lines[56]) and ("T_lo 的精确有理" in lines[57])
    T_hi = parse_frac_last(lines[56]) if lok2 else None
    T_lo = parse_frac_last(lines[57]) if lok2 else None
    kl = read_text(KPROOF_RES + "/k1_threshold_cert.log").splitlines()
    lok1 = len(kl) > 62 and ("KA " in kl[60]) and ("KB " in kl[61])
    KA = parse_frac_last(kl[60]) if lok1 else None
    KB = parse_frac_last(kl[61]) if lok1 else None
    d = {"T_hi": T_hi, "T_lo": T_lo, "KA": KA, "KB": KB,
         "lines_ok": bool(lok2 and lok1), "repro": None}
    if DEEP:
        d["repro"] = run_bisection()
    CACHE["end"] = d
    return d


def get_endpoint_signs():
    """在本引擎里独立判定 S(T_hi) > 0 与 S(T_lo) < 0（证书端点的性质；两种档都跑）。"""
    if "signs" in CACHE:
        return CACHE["signs"]
    end = get_endpoints()
    gd_lo, gd_hi = GAM - DHI, GAM - DLO
    ehi = eps_iv(92, end["T_hi"])
    elo = eps_iv(92, end["T_lo"])
    CACHE["signs"] = {"T_hi": (ehi[0] - gd_hi, ehi[1] - gd_lo),
                      "T_lo": (elo[0] - gd_hi, elo[1] - gd_lo)}
    return CACHE["signs"]


GAM_N, GAM_D = 325919355854421968365, 205632218873398596256
GAM = F(GAM_N, GAM_D)
KSTAR = 205632218873398596256
Q41 = 77692117359936589403


def get_feasible(K):
    key = ("feas", K)
    if key not in CACHE:
        feas, und = [], []
        for m2 in range(1, 93):
            d = feasible_dec(m2, K)
            if d is True:
                feas.append(m2)
            elif d is None:
                und.append(m2)
        CACHE[key] = (feas, und)
    return CACHE[key]


def get_epsopt(K):
    """eps_opt(K) 的区间、argmin 与可行集（缓存）。"""
    key = ("eo", K)
    if key not in CACHE:
        feas, und = get_feasible(K)
        vals = {m2: eps_iv(m2, K) for m2 in feas}
        lo = min(v[0] for v in vals.values())
        hi = min(v[1] for v in vals.values())
        arg = None
        for m2 in feas:
            if all(vals[m2][1] < vals[u][0] for u in feas if u != m2):
                arg = m2
        CACHE[key] = {"lo": lo, "hi": hi, "arg": arg, "feas": feas, "und": und, "vals": vals}
    return CACHE[key]


def get_prefixes():
    """δ 与 β = δ + ε_opt(K*) 的证书前缀、首个相异下标（缓存）。"""
    if "pref" in CACHE:
        return CACHE["pref"]
    eo = get_epsopt(KSTAR)
    blo = rd(DHI + eo["lo"])
    bhi = ru(DHI + eo["hi"])
    pa = cf_prefix(DLO, DHI)
    pb = cf_prefix(blo, bhi)
    k = 0
    while k < min(len(pa), len(pb)) and pa[k] == pb[k]:
        k += 1
    CACHE["pref"] = (pa, pb, k)
    return CACHE["pref"]


# =====================================================================
# [0] 引擎自检
# =====================================================================
def engine_selftest():
    section("[0] 自写区间引擎自检（全部用 Fraction 精确判定）")
    xs = [F(1, 3), F(22, 7), F(10 ** 5, 3), F(1, 10 ** 50)]
    check("E.1", all(rd(x) <= x <= ru(x) for x in xs), "rd/ru 保下界与保上界")
    e2 = exp_pos(rd(LN2[0]), ru(LN2[1]))
    e3 = exp_pos(rd(L3[0]), ru(L3[1]))
    check("E.2", e2[0] <= 2 <= e2[1] and e3[0] <= 3 <= e3[1], "exp(ln2) ∋ 2、exp(ln3) ∋ 3（级数往返）")
    ed = exp_pos(rd(DLO * LN2[0]), ru(DHI * LN2[1]))
    check("E.3", ed[0] <= 3 <= ed[1], "exp(δ·ln2) ∋ 3（δ = ln3/ln2 的区间往返）")
    p = pow2_iv(70, 70)
    check("E.4", p[0] <= 2 ** 70 <= p[1], "2^70 的区间包含精确整数 1180591620717411303424")
    a = exp_pos(F(1), F(1))
    b = exp_any(F(-1), F(-1))
    check("E.5", a[0] * b[0] <= 1 <= a[1] * b[1], "exp(1)·exp(−1) ∋ 1")
    u = F(1, 1000)
    L = ln1m_iv(u, u)
    eb = exp_any(L[0], L[1])
    check("E.6", eb[0] <= F(999, 1000) <= eb[1], "exp(ln(1 − 1/1000)) ∋ 999/1000")
    check("E.7", simplest_fraction(F(2, 5), F(3, 5)) == F(1, 2)
          and simplest_fraction(F(1, 3), F(1, 2)) == F(2, 5),
          "Stern-Brocot 最小分母两例：(0.4, 0.6) → 1/2、(1/3, 1/2) → 2/5")
    check("E.8", cf_value([1, 1, 1, 2]) == F(8, 5) and cf_value([1, 1, 1, 1, 1]) == F(8, 5),
          "连分数往返：[1;1,1,2] = [1;1,1,1,1] = 8/5")
    check("E.9", F(158, 100) < DLO < DHI < F(159, 100) and DHI - DLO < F(1, 10 ** 150),
          "δ 区间落在 (1.58, 1.59) 且宽 < 1e-150（实测宽 %s）" % sig_str(DHI - DLO, 3))
    check("E.10", F(70) < CLO < CHI < F(71) and CHI - CLO < F(1, 10 ** 150),
          "C 区间落在 (70, 71) 且宽 < 1e-150（实测宽 %s）" % sig_str(CHI - CLO, 3))


# =====================================================================
# [1] 结论 1
# =====================================================================
def assert_conclusion_1():
    section("结论 1：T 的两侧严格区间与证书数值核心")
    end = get_endpoints()
    if not check("1.1", end["lines_ok"] and end["T_hi"] is not None and end["T_lo"] is not None
                 and end["KA"] is not None and end["KB"] is not None,
                 "从 r2_threshold_cert.log:57、:58 解析 T_hi、T_lo，从 k1_threshold_cert.log:61、:62 "
                 "解析 KA、KB（本轮结论所引出处；字符串精确解析）"):
        return
    T_hi, T_lo, KA, KB = end["T_hi"], end["T_lo"], end["KA"], end["KB"]
    if DEEP:
        rep = end["repro"]
        ok = (rep["steps"] == 400 and rep["stall"] is None
              and (rep["T_hi"], rep["T_lo"], rep["KA"], rep["KB"]) == (T_hi, T_lo, KA, KB))
        check("1.1d", ok, "深度档：本引擎 400 步二分复现的 T_hi、T_lo、KA、KB 与日志逐字符一致"
                          "（完成 %d 步）" % rep["steps"])
        if rep["stall"]:
            st = rep["stall"]
            note("最小反例：第 %d 步未定，K_mid = %s；eps 区间 = [%s, %s]"
                 % (st[0], sig_str(st[1], 20), sig_str(st[2][0], 20), sig_str(st[2][1], 20)))
    else:
        note("默认档不重跑 400 步二分（重算量较大项；端点的独立复现见 --deep 档的判据 1.1d）；"
             "本档改为在端点处用本引擎独立判号（判据 1.2b）并核全部结构读数。")
    check("1.2", T_hi < T_lo, "T_hi < T_lo（精确有理比较）")
    sg = get_endpoint_signs()
    check("1.2b", sg["T_hi"][0] > 0 and sg["T_lo"][1] < 0,
          "本引擎在端点独立判号：S(T_hi) > 0（余量 %s）、S(T_lo) < 0（负余量 %s）"
          % (sig_str(sg["T_hi"][0], 8), sig_str(-sg["T_lo"][1], 8)))
    check("1.3a", T_hi.denominator == 2 ** 381 and T_hi.numerator % 2 == 1,
          "分母(T_hi) = 2^381 且分子为奇数")
    check("1.3b", T_lo.denominator == 2 ** 382 and T_lo.numerator % 2 == 1,
          "分母(T_lo) = 2^382 且分子为奇数")
    W = T_lo - T_hi
    check("1.4a", W == F(3 * 5 ** 18, 2 ** 382), "精确宽度 = 3·5^18/2^382")
    check("1.4b", W == F(3 * 10 ** 18, 2 ** 400), "精确宽度 = 3·10^18/2^400（与 3e18 起点、400 步自洽）")
    check("1.5a", sig_str(W, 13) == "1.161777574454e-102", "宽度 13 位截断 = %s" % sig_str(W, 13))
    check("1.5b", sig_str(W / T_hi, 13) == "3.709432774431e-123",
          "相对宽 13 位截断 = %s" % sig_str(W / T_hi, 13))
    check("1.6", dec_str(T_hi, 60) == dec_str(T_lo, 60), "两端 60 位小数截断逐字符相同")
    note("该串 = %s" % dec_str(T_hi, 60))
    blob = read_text(KPROOF_RES + "/r2_threshold_cert.log")
    check("1.7", (dec_str(T_hi, 60) in blob) and (dec_str(T_lo, 60) in blob),
          "r2 日志的 60 位小数打印与解析出的精确有理逐字符一致（文中命中）")
    check("1.8a", KA is not None and KA <= T_hi and T_lo <= KB, "第 160 步快照 [KA, KB] ⊇ [T_hi, T_lo]")
    if KA is not None:
        check("1.8b", sig_str(T_hi - KA, 13) == "3.610201961371e-31",
              "T_hi − KA 13 位截断 = %s" % sig_str(T_hi - KA, 13))
        check("1.8c", sig_str(KB - T_lo, 13) == "1.691663101213e-30",
              "KB − T_lo 13 位截断 = %s" % sig_str(KB - T_lo, 13))
        check("1.8d", sig_str(KB - KA, 7) == "2.052683e-30",
              "KB − KA 7 位截断 = %s" % sig_str(KB - KA, 7))
    b1 = read_text(KPROOF_RES + "/k1_threshold_cert.log")
    check("1.9", (dec_str(KA, 40) in b1) and (dec_str(KB, 40) in b1),
          "k1 日志的 KA、KB 小数打印与解析出的精确有理逐字符一致（文中命中）")
    # ---- A1：92 项余量 ----
    gd_lo, gd_hi = GAM - DHI, GAM - DLO
    feas_all = all(feasible_dec(m2, T_hi) is True for m2 in range(1, 93))
    check("1.10a", feas_all, "T_hi 处 92 个 m2 的可行判定全部为 True（F_92(T_hi) = {1, …, 92}）")
    rows = []
    for m2 in range(1, 93):
        e = eps_iv(m2, T_hi)
        rows.append((e[0] - gd_hi, e[1] - gd_lo, m2))
    check("1.10b", all(r[0] > 0 for r in rows),
          "A1：92 项 eps(m2, T_hi)_下界 > (γ−δ)_上界（本引擎严格区间逐项判定）")
    rows.sort(key=lambda r: (r[0], r[1]))
    check("1.10c", [r[2] for r in rows[:3]] == [92, 91, 90], "最小余量前三分别落在 m2 = 92、91、90")
    check("1.10d", rows[2][1] < rows[3][0], "第三小与第四小严格分离（排序无并列）")
    note("前三读数：m2 = 92 余量 ≈ %s；91 ≈ %s；90 ≈ %s（区间宽约 %s）"
         % (sig_str(rows[0][0], 8), sig_str(rows[1][0], 8), sig_str(rows[2][0], 8),
            sig_str(rows[0][1] - rows[0][0], 3)))
    for r, c8, c7 in ((rows[0], "1.0759105e-163", "1.075910e-163"),
                      (rows[1], "5.1242963e-42", "5.124296e-42"),
                      (rows[2], "8.8503473e-42", "8.850347e-42")):
        ok = in_bucket((r[0], r[1]), c8, "round") and in_bucket((r[0], r[1]), c7, "trunc")
        check("1.10e.%d" % r[2], ok,
              "m2 = %d 余量 ∈ [%s, %s]：8 位舍入读 %s、7 位截断读 %s" % (r[2], sig_str(r[0], 10), sig_str(r[1], 10), c8, c7))
    blob = read_text(KPROOF_RES + "/r2_threshold_cert.log")
    need = ("1.075910 e-163", "5.124296 e-42", "8.850347 e-42", "1.136322 e-164")
    check("1.10f", all(s in blob for s in need),
          "r2 日志含四处读数原样串（1.075910e-163、5.124296e-42、8.850347e-42、1.136322e-164）")
    # ---- B1、B2 ----
    e92 = eps_iv(92, T_lo)
    check("1.11a", feasible_dec(92, T_lo) is True, "B1：92 ∈ F_92(T_lo)（可行判定 True）")
    check("1.11b", e92[1] < gd_lo, "B2：eps(92, T_lo)_上界 < (γ−δ)_下界（负余量）")
    marg = (e92[0] - gd_hi, e92[1] - gd_lo)
    check("1.11c", in_bucket(marg, "-1.1363222e-164", "round") and in_bucket(marg, "-1.136322e-164", "trunc"),
          "负余量 ∈ [%s, %s]：8 位舍入读 −1.1363222e-164、7 位截断读 −1.136322e-164"
          % (sig_str(-marg[1], 10) + "（负）", sig_str(-marg[0], 10) + "（负）"))
    # ---- K* 格 ε 梯子与 k3_run_a.out 的 20 位比对 ----
    la = read_text(KPROOF_RES + "/k3_run_a.out").splitlines()
    got = {}
    for s in la:
        m = re.search(r"eps\((\d+), 92, K\*\)", s)
        if m:
            nums = re.findall(r"(\d\.\d+e[-+]\d+)", s)
            if nums:
                got[int(m.group(1))] = nums[0]
    hit20 = 0
    for m2 in range(83, 92):
        mine = sig_str(eps_iv(m2, KSTAR)[0], 20)
        theirs = got.get(m2)
        ok = theirs is not None and strip_sig(theirs) == strip_sig(mine)
        hit20 += ok
        if not ok:
            note("m2 = %d：本引擎 %s；日志 %s" % (m2, mine, theirs))
    check("1.12", hit20 == 9, "K* 格 ε 梯子 83 至 91 的 20 位有效数字与 k3_run_a.out 一致：%d/9" % hit20)
    # ---- A5 域闭合（默认档抽检小规模；深度档全量） ----
    e1 = eps_iv(1, rd(F(92) * CLO))
    eps_ub = e1[1]

    def a5_scan(qmax):
        worst = None
        okall = True
        for q in range(1, qmax + 1):
            pmin = fl(F(q) * DLO) + 1
            margq = F(pmin, q) - (DHI + eps_ub)
            if margq < 0:
                okall = False
            if worst is None or margq < worst[0]:
                worst = (margq, q, pmin)
        return worst, okall

    check("1.13a", F(6457) > F(92) * CHI, "6457 > 92·C_hi（链一进入就永不离开域 D_92）")
    if DEEP:
        worst, okall = a5_scan(6456)
        check("1.13b", okall, "A5 深度档：q ≤ 6456 的最小 p/q > δ 全部 ≥ δ_hi + eps_ub")
        check("1.13c", worst[1] == 6291 and worst[2] == 9971,
              "A5 最坏位置 q = %d、p = %d（与日志一致；余量 ≈ %s）" % (worst[1], worst[2], sig_str(worst[0], 7)))
    else:
        worst, okall = a5_scan(64)
        check("1.13b", okall, "A5 默认档抽检：q ≤ 64 的最小 p/q > δ 全部 ≥ δ_hi + eps_ub（全量 6456 项见 --deep）")
        note("深度档将复算全部 6456 项并复核最坏位置 q = 6291、p = 9971（日志 :76）")
    check("1.13d", ("q <= 6456" in blob) and ("q = 6291" in blob) and ("p = 9971" in blob),
          "r2 日志含 A5 的门槛数 6456 与最坏位置原样串")
    # ---- 门禁元事实（文件核对；深度档另重跑） ----
    gp = KPROOF_SCR + "/verify.py"
    check("1.14a", md5_of(gp) == "d7db4e5b9c88abf4b9e5bff2c8c266cb" and len(read_text(gp).splitlines()) == 450,
          "闸门文件 md5 = d7db4e5b…、450 行（与本轮结论 1 一致）")
    gt = read_text(KPROOF_RES + "/verify.out")
    check("1.14b", len(gt.splitlines()) == 127 and "判据 57 条，FAIL 0 条" in gt,
          "results/verify.out 127 行且含 SUMMARY「判据 57 条，FAIL 0 条」（读输出文件核对，非重跑）")
    if DEEP:
        # (a) 镜像重跑：复现历史命令（> results/verify.out 先清空输出文件）的 EXIT=0，
        #     并核输出与登记文件逐字节相同。只在临时镜像里动文件，不改仓库。
        gate_mirror_check(gp)
        # (b) 原地重跑：如实登记「自指伪影」（7.2b 扫描结果目录找针串，而它自己的输出文件含该针串）
        py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
        r2 = subprocess.run([py, gp], cwd=KPROOF_SCR, capture_output=True)
        out2 = r2.stdout.decode("utf-8", "replace")
        needle = "5.254869241218064"
        selfref = (needle in gt) and ("[PASS] 7.2b" in gt)
        if r2.returncode == 0:
            check("1.15b", True, "原地重跑退出码 0（本次未触发自指伪影）")
        else:
            ok = ("判据 57 条，FAIL 1 条；清单：7.2b" in out2) and ("['verify.out']" in out2)
            check("1.15b", ok and selfref,
                  "原地重跑退出码 %d：唯一失败为 7.2b 且命中恰为 verify.out（自指伪影成立：登记 verify.out 的 "
                  "7.2b 行本身含针串）" % r2.returncode)
        note("非幂等性登记：闸门 7.2b 扫描 results 目录找针串 5.254869241218064，而它自己的输出文件"
             "（由「> results/verify.out」写入）在 7.2b 消息里含该针串，故原地重跑必失败于 7.2b；"
             "历史 EXIT=0 的可复现条件（先清空输出文件）已由 1.15a 的镜像重跑复现。")


def gate_mirror_check(gp):
    """把两轨脚本与结果树复制到临时镜像，改写 ROOT 常量后重跑闸门（不动仓库任何文件）。"""
    import shutil
    import tempfile
    try:
        mir = tempfile.mkdtemp(prefix="kcross_gate_mirror_")
    except OSError as exc:
        check("1.15a", False, "无法创建临时镜像目录：%s" % exc)
        return
    try:
        base = os.path.join(mir, "70-research/tracks")
        os.makedirs(os.path.join(base, "kcross-proof/cycle-1"))
        os.makedirs(os.path.join(base, "kcross-tail/cycle-1"))
        os.makedirs(os.path.join(mir, "70-research/cycle-2"))
        shutil.copytree(KPROOF_SCR, os.path.join(base, "kcross-proof/cycle-1/scripts"))
        shutil.copytree(KTAIL_SCR, os.path.join(base, "kcross-tail/cycle-1/scripts"))
        shutil.copy(KTAIL + "/ledger-note.md", os.path.join(base, "kcross-tail/cycle-1/"))
        shutil.copy(REPO + "/70-research/cycle-2/route-4.md", os.path.join(mir, "70-research/cycle-2/"))
        shutil.copy(KPROOF + "/route-4.md", os.path.join(base, "kcross-proof/cycle-1/"))
        mgate = os.path.join(base, "kcross-proof/cycle-1/scripts/verify.py")
        with open(mgate, "r", encoding="utf-8") as fh:
            txt = fh.read()
        old_root = 'ROOT = "%s"' % REPO
        if old_root not in txt:
            check("1.15a", False, "镜像闸门里找不到 ROOT 常量行，无法改写")
            return
        txt = txt.replace(old_root, 'ROOT = "%s"' % mir, 1)
        with open(mgate, "w", encoding="utf-8") as fh:
            fh.write(txt)
        vout_mir = os.path.join(base, "kcross-proof/cycle-1/scripts/results/verify.out")
        open(vout_mir, "w").close()          # 复现「> results/verify.out」的先清空语义
        py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
        r = subprocess.run([py, mgate], cwd=os.path.dirname(mgate), capture_output=True)
        got = hashlib.md5(r.stdout).hexdigest()
        want = md5_of(KPROOF_RES + "/verify.out")
        ok = (r.returncode == 0) and ("判据 57 条，FAIL 0 条" in r.stdout.decode("utf-8", "replace")) \
            and got == want
        check("1.15a", ok, "镜像重跑闸门（先清空输出）：退出码 %d、SUMMARY 命中、输出与登记 verify.out "
                           "逐字节相同（md5 %s）" % (r.returncode, got))
    except OSError as exc:
        check("1.15a", False, "镜像重跑失败：%s" % exc)
    finally:
        shutil.rmtree(mir, ignore_errors=True)


def parse_frac_last(line):
    hit = re.findall(r"(\d+/\d+)", line)
    return F(hit[-1]) if hit else None


# =====================================================================
# [2] 结论 2
# =====================================================================
def assert_conclusion_2():
    section("结论 2：T = R 的纸面论证（逻辑层无法机器验证；只复算数值前提）")
    note("无法机器验证（阅读与逻辑判断，跳过机器断言）：")
    note("  · 定理 A 的 A2、A4 与定理 B 的 B3 是否构成「完整纸面论证、逻辑层未见缺口」；")
    note("  · 「非降性对本命题不必要」与「无一步等价于原命题」的推理判断；")
    note("  · 条件压缩成一项的口径问题（属 route 文档层面的表述）；以及 A5 中")
    note("    「单模括号加 Farey 引理 L4 的两步不等式相加」的一般引理本身（下面只核它的实例）。")
    sg = get_endpoint_signs()
    check("2.1", sg["T_hi"][0] > 0 and sg["T_lo"][1] < 0,
          "R 的定位：S(T_hi) > 0、S(T_lo) < 0（S(K) = eps(92, K) − (γ−δ)，本引擎端点判号）")
    eo = get_epsopt(KSTAR)
    check("2.2a", eo["arg"] == 91, "argmin(K*) = 91（ε_opt(K*) = ε(91, K*)，严格分离判定）")
    check("2.2b", DHI < GAM and GAM < DLO + eo["lo"],
          "γ ∈ (δ, δ + ε_opt(K*))（区间判定；即「γ 落在开区间内」）")
    check("2.2c", GAM.denominator == KSTAR and gcd(GAM_N, GAM_D) == 1,
          "γ 的分母恰为 K* 且既约（gcd = 1）（即 B3 的「分母恰为 K*」）")
    prefA, prefB, k = get_prefixes()
    gm = cf_value(prefA[:k] + [min(prefA[k], prefB[k]) + 1])
    conv = cf_convergents(prefA)
    check("2.3a", gm == GAM and gm.denominator == KSTAR and conv[43] == (GAM_N, GAM_D),
          "由本引擎 δ、β 证书前缀独立重建 γ = [a0;…;a41, c_k]：等于登记值且分母 = K*")
    P, Q = conv[44]
    D0r = Q + KSTAR
    check("2.3b", F(P, Q) < DLO and GAM_N * Q - P * GAM_D == 1,
          "单模括号实例：p44/q44 = %d/%d < δ_lo 且 z·y − x·w = 1" % (P, Q))
    check("2.3c", D0r == 7941964418702608664581 and simplest_fraction(DLO, GAM) == F(P + GAM_N, D0r),
          "Farey 实例：区间 (δ_lo, γ) 的最小分母 = y + w = %d，且恰为中项 (p44 + γ 分子)/(q44 + K*)" % D0r)
    note("提示：以上是「数值前提已核」；纸面论证本身仍需人工复核，本脚本不为其背书。")


# =====================================================================
# [3] 结论 3
# =====================================================================
def assert_conclusion_3():
    section("结论 3：分岔窗口修正（门槛与窗口宽的独立复算；旧值排除）")
    src = read_text(KPROOF_RES + "/r4b2_window_probe.out")
    LOG_C = {90: F("123124614107556571561.827996023727480573234158995835"),
             89: F("78555824936758779275.265552681458057901548946328722")}
    LOG_R = {90: (F("123124614107652692133.007231711933058876044901"),
                  F("123124614107652692133.007231919710646726095849")),
             89: (F("78555824936819382091.475309577063948109807001"),
                  F("78555824936819382091.475309709629966165890197"))}
    CLAIM12 = {90: "7.80677136541", 89: "7.71461775858"}

    def c_iv(j):
        g = geom_iv(j)
        return rd(F(92, j) * g[0] * CLO), ru(F(92, j) * g[1] * CHI)

    def dsign(j, K):
        """numerator(j) − numerator(j−1) 的严格符号：'jm1'（>0）、'j'（<0）或 None。"""
        nj = num_iv(j, K)
        nm = num_iv(j - 1, K)
        dlo_ = nj[0] - nm[1]
        dhi_ = nj[1] - nm[0]
        if dlo_ > 0:
            return "jm1"
        if dhi_ < 0:
            return "j"
        return None

    win = {}
    pad = F(2, 10 ** 30)      # 允许 c_j 打印串的 30 位截断落差
    for j in (90, 89):
        civ = c_iv(j)
        okc = (dec_str(civ[0], 30) == dec_str(LOG_C[j], 30) == dec_str(civ[1], 30))
        oktol = abs(LOG_C[j] - (civ[0] + civ[1]) / 2) <= pad
        check("3.1.%d" % j, okc and oktol,
              "c_%d：本引擎 30 位打印 [%s, %s]，与日志自印串一致（差 ≤ 1e-30 的截断落差）"
              % (j, dec_str(civ[0], 30), dec_str(civ[1], 30)))
        note("c_%d = %s（本引擎复算）" % (j, dec_str(civ[0], 30)))
        rlo, rhi = LOG_R[j]
        s_lo, s_hi = dsign(j, rlo), dsign(j, rhi)
        check("3.2.%d" % j, s_lo == "jm1" and s_hi == "j",
              "j = %d：本引擎在日志 bracket 两端独立判号（左端旧档胜、右端新档胜，故变号点被夹在其中）" % j)
        wrlo = (rlo - LOG_C[j]) / LOG_C[j]
        wrhi = (rhi - LOG_C[j]) / LOG_C[j]
        check("3.3.%d" % j, sig_str(wrlo - pad, 12) == sig_str(wrhi + pad, 12) == CLAIM12[j] + "e-13",
              "j = %d：真窗口宽（已被夹在日志 bracket 内）的 12 位截断 = %se-13" % (j, CLAIM12[j]))
        old1 = F(2, 10 ** 24)
        old2 = F(15361313, 10 ** 30)
        old2f = F(15361313786354857241362112574, 10 ** 51)   # = 1.5361313786354857241362112574e-23
        check("3.4.%d" % j, not (wrlo - pad <= old1 <= wrhi + pad) and not (wrlo - pad <= old2 <= wrhi + pad)
              and not (wrlo - pad <= old2f <= wrhi + pad),
              "j = %d：2e-24、1.5361313e-23（含 29 位全串 15361313786354857241362112574/10^51）都不落在括号内" % j)
        if DEEP:
            c = (civ[0] + civ[1]) / 2
            Ka = c * (1 + F(1, 10 ** 13))
            Kb = c * (1 + F(2, 10 ** 12))
            s_in, s_out = dsign(j, Ka), dsign(j, Kb)
            ok0 = s_in == "jm1" and s_out == "j"
            check("3.5.%d" % j, ok0, "深度档：偏移 1e-13 与 2e-12 处的两向判号成立")
            if ok0:
                for _ in range(240):
                    Km = (Ka + Kb) / 2
                    s = dsign(j, Km)
                    if s == "jm1":
                        Ka = Km
                    elif s == "j":
                        Kb = Km
                    else:
                        break
                wlo = (Ka - c) / c
                whi = (Kb - c) / c
                win[j] = {"c": c, "Ka": Ka, "Kb": Kb, "wlo": wlo, "whi": whi}
                check("3.6.%d" % j, sig_str(wlo, 12) == sig_str(whi, 12) == CLAIM12[j] + "e-13",
                      "深度档：j = %d 在 240 步二分后窗口宽 ∈ [%s, %s]，12 位截断 = %se-13"
                      % (j, sig_str(wlo, 20), sig_str(whi, 20), CLAIM12[j]))
                check("3.6b.%d" % j, Kb < KSTAR,
                      "j = %d：窗口右端上界 %s < K*（窗口全部在 K* 之下，不进目标区间）" % (j, sig_str(Kb, 16)))
    # ---- 15 位串的出处核对与真窗口宽并列 ----
    wrlo90 = (LOG_R[90][0] - LOG_C[90]) / LOG_C[90]
    wrhi90 = (LOG_R[90][1] - LOG_C[90]) / LOG_C[90]
    check("3.7", sig_str(wrlo90, 15) == "7.80677136541266e-13",
          "结论所引 15 位串 = 日志左括号端二次截断读数：dec_trunc15 = %s" % sig_str(wrlo90, 15))
    note("对照：同一日志右括号端读数 dec_trunc15 = %s（故该 15 位串是括号左端的读数）" % sig_str(wrhi90, 15))
    if DEEP and 90 in win:
        wlo90, whi90 = win[90]["wlo"], win[90]["whi"]
        t15 = sig_str(wlo90, 15)
        check("3.8", t15 == sig_str(whi90, 15) and t15 == "7.80677136541267e-13",
              "深度档：真窗口宽（本引擎 240 步二分）15 位截断 = %s" % t15)
        note("差异说明：结论 3 的 15 位串 …266 是日志左端读数（3.7），真窗口宽的 15 位截断为 …267，")
        note("两者只在第 15 位差 1（打印粒度效应）；12 位读数与旧值排除不受影响。")
        if 89 in win:
            note("j = 89 真窗口宽 15 位截断 = %s（结论未给 15 位，仅列 12 位）"
                 % sig_str(win[89]["wlo"], 15))
        tail89 = ("；j = 89 ∈ [%s, %s]" % (sig_str(win[89]["wlo"], 30), sig_str(win[89]["whi"], 30))
                  if 89 in win else "")
        note("深度档读数（240 步）：j = 90 窗口宽 ∈ [%s, %s]%s"
             % (sig_str(wlo90, 30), sig_str(whi90, 30), tail89))
    else:
        note("真窗口宽的 15 位与 30 位截断依赖不少于 60 步的独立二分，安排在 --deep 档；默认档已用两端"
             "判号（3.2.90）把变号点夹在日志 bracket 内，故 12 位读数与旧值排除在默认档即为独立判定。")
    # ---- log2(1 + 2^{−C})/C 的恒等读数 ----
    u = exp_any(rd(-CHI * LN2[1]), ru(-CLO * LN2[0]))
    vlo_, vhi_ = F(1) + u[0], F(1) + u[1]
    lv_lo = ln_pos(vlo_)[0]
    lv_hi = ln_pos(vhi_)[1]
    val = (rd(lv_lo / (LN2[1] * CHI)), ru(lv_hi / (LN2[0] * CLO)))
    check("3.9", in_bucket(val, "1.5361313786354857241362112574e-23", "trunc"),
          "log2(1 + 2^−C)/C 的 29 位截断 = %s（第二版旧值的算式读数）" % sig_str(val[0], 29))
    check("3.10", in_bucket(val, "1.5361313e-23", "trunc")
          and F(15361313786354857241362112574, 10 ** 51) == bucket_of("1.5361313786354857241362112574e-23")[0],
          "8 位截断 1.5361313e-23 与 29 位全串同为该式读数；旧值排除判据用的有理数正是该 29 位截断")
    note("边界（随结论 3 引用）：证的是「存在一个变号点落在该括号内」，不是「窗口本身宽该值」；")
    note("「两版旧值同源」属解释性判断，本脚本只核数值。")


# =====================================================================
# [4] 结论 4
# =====================================================================
def assert_conclusion_4():
    section("结论 4：K* 格清单记账、两个不动点、账本引用卫生")
    eo = get_epsopt(KSTAR)
    check("4.1a", eo["feas"] == list(range(1, 92)) and eo["und"] == [],
          "K* 格可行集 F_92(K*) = {1, …, 91}（不可行 {92}、未定 0）")
    check("4.1b", eo["arg"] == 91, "argmin(K*) = 91（严格分离）")
    check("4.1c", in_bucket((eo["lo"], eo["hi"]), "8.97322170861713601632572478554e-42", "trunc"),
          "ε_opt(K*) 的 30 位截断 = %s" % sig_str(eo["lo"], 30))
    eo41 = get_epsopt(Q41)
    check("4.2a", eo41["arg"] == 88, "q41 格 argmin = 88（可行集上界 %d、未定 %d）"
          % (max(eo41["feas"]), len(eo41["und"])))
    check("4.2b", DHI < GAM < DLO + eo41["lo"], "γ ∈ (δ, δ + ε_opt(q41))（区间判定）")
    for tag, Kv in (("K*", KSTAR), ("q41", Q41)):
        eoK = get_epsopt(Kv)
        q_out = simplest_fraction(DLO, DHI + eoK["hi"]).denominator
        q_in = simplest_fraction(DHI, DLO + eoK["lo"]).denominator
        check("4.3.%s" % tag, q_out == Kv and q_in == Kv,
              "Ψ(%s) ∈ [%d, %d]，两端都等于自身（自写 Stern-Brocot 最小分母，内外括号均判）"
              % (tag, q_out, q_in))
    prefA, prefB, k = get_prefixes()
    check("4.4a", (k, prefA[k], prefB[k]) == (42, 1, 2),
          "首个相异下标 k = %d（a_k = %d、b_k = %d、c_k = %d）" % (k, prefA[k], prefB[k], min(prefA[k], prefB[k]) + 1))
    na = sum(prefA[1:k + 2])
    nb = sum(prefB[1:k + 2])
    check("4.4b", na == 220 and nb == 222, "枚举规模上界：alpha 侧 %d、beta 侧 %d（合 %d）" % (na, nb, na + nb))
    full = semiconv_list(prefA, k, None, "alpha") + semiconv_list(prefB, k, None, "beta")
    capped = semiconv_list(prefA, k, KSTAR, "alpha") + semiconv_list(prefB, k, KSTAR, "beta")
    check("4.4c", len(full) == 442 and len(capped) == 438,
          "完整清单 %d 条、cap_q = K* 清单 %d 条" % (len(full), len(capped)))
    cs = set(capped)
    dropped = [it for it in full if it not in cs]
    check("4.4d", len(dropped) == 4 and min(v.denominator for v, s in dropped) == KSTAR
          and all(v.denominator >= KSTAR for v, s in dropped),
          "差集 %d 条、分母全部 ≥ K*、最小恰为 K*" % len(dropped))
    check("4.4e", sum(1 for v, s in dropped if v == GAM) == 2
          and sorted(s for v, s in dropped if v == GAM) == [("alpha", 43, 1), ("beta", 42, 2)],
          "差集含 γ 的两种写法（alpha,43,1）与（beta,42,2）")
    note("差集四条：%s" % "；".join("%s %s（分母 %d）" % (s, v, v.denominator) for v, s in dropped))
    eoK = get_epsopt(KSTAR)
    beta_lo = rd(DHI + eoK["lo"])
    beta_hi = ru(DHI + eoK["hi"])
    ins = [v for v, s in capped if DHI < v < beta_lo]
    outs = [v for v, s in capped if v <= DLO or v >= beta_hi]
    check("4.5", len(ins) == 0 and len(outs) == 438 and len(capped) - len(ins) - len(outs) == 0,
          "cap 后清单分类：内 %d、外 %d、未定 %d" % (len(ins), len(outs), len(capped) - len(ins) - len(outs)))
    e3 = read_text(KPROOF_RES + "/k3_run_e.out")
    r3 = read_text(KTAIL_RES + "/r3_list_search.out")
    ok = (("完整清单条数 = 442" in e3) and ("cap_q = K* 的清单条数 = 438" in e3)
          and ("被 cap 掉（分母 >= K*）的条数 = 4" in e3)
          and (re.search(r"内\s*0\s*；\s*外\s*438\s*；\s*未定\s*0", r3) is not None)
          and ("442（= 220 + 222" in r3))
    check("4.6", ok, "k3_run_e.out 与 r3_list_search.out 含计数原样串（442、438、4、内 0；外 438；未定 0）")
    led = ((KTAIL + "/ledger-note.md", "f2057af61f2c0ad977045c23c3fd56c3"),
           (KTAIL_SCR + "/cite_check.py", "d8a165fafea3b895ce64179dd061dc79"),
           (KTAIL_SCR + "/ledger_numbers.py", "8cbe4f50454d8c10d4affba37e892d63"),
           (KTAIL_RES + "/cite_check.out", "f46be6150aebd8508cd523afccdffd02"))
    n_ok = 0
    for path, want in led:
        got = md5_of(path)
        n_ok += (got == want)
        if got != want:
            note("md5 不符：%s 实测 %s（登记 %s）" % (path, got, want))
    check("4.7", n_ok == 4, "账本四件的 md5 与登记值逐件一致（%d/4）" % n_ok)
    if DEEP:
        py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
        r1 = subprocess.run([py, KTAIL_SCR + "/cite_check.py"], cwd=KTAIL_SCR, capture_output=True, text=True)
        check("4.8a", r1.returncode == 0 and "共 179 条机器断言；FAIL 0 条" in r1.stdout,
              "重跑 cite_check.py：退出码 %d、末段命中「共 179 条机器断言；FAIL 0 条」" % r1.returncode)
        r2 = subprocess.run([py, KTAIL_SCR + "/ledger_numbers.py"], cwd=KTAIL_SCR, capture_output=True, text=True)
        check("4.8b", r2.returncode == 0, "重跑 ledger_numbers.py：退出码 %d" % r2.returncode)
    else:
        note("账本侧重跑（cite_check.py、ledger_numbers.py）在 --deep 档；默认档只做 md5 与文件存在核对。")


# =====================================================================
def cross_library_check():
    """跨库对拍（对照用，读项目区间库 kc_rig 与 r2_rig；本脚本主判据仍是 1 至 4 组自算）。"""
    section("[5] 跨库对拍（对照用：同一量在至少两库下同值，且与本引擎一致）")
    try:
        if KPROOF_SCR not in sys.path:
            sys.path.insert(0, KPROOF_SCR)
        import kc_rig as KC
        import r2_rig as R2
    except Exception as exc:
        check("5.0", False, "项目区间库不可导入：%r" % (exc,))
        return

    def inter(a, b):
        return not (a[1] < b[0] or b[1] < a[0])

    try:
        dk = KC.delta_bounds()
        dr = R2.delta_bounds()
        check("5.1", inter(dk, dr) and inter(dk, (DLO, DHI)) and inter(dr, (DLO, DHI)),
              "δ 区间三库两两相交（kc_rig 宽 %s、r2_rig 宽 %s、本引擎宽 %s）"
              % (sig_str(dk[1] - dk[0], 3), sig_str(dr[1] - dr[0], 3), sig_str(DHI - DLO, 3)))
        ek = KC.eps_bounds(91, 92, KSTAR, dk[0], dk[1], KC.ln2_bounds())
        er = R2.eps_bounds(91, 92, KSTAR, dr[0], dr[1], R2.ln2_bounds())
        em = eps_iv(91, KSTAR)
        check("5.2", inter(ek, er) and inter(ek, em) and inter(er, em)
              and sig_str(ek[0], 20) == sig_str(er[0], 20) == sig_str(em[0], 20),
              "eps(91, 92, K*) 三库区间两两相交且 20 位打印一致（%s）" % sig_str(em[0], 20))
        e2k = KC.eps_bounds(92, 92, KSTAR, dk[0], dk[1], KC.ln2_bounds())
        e2r = R2.eps_bounds(92, 92, KSTAR, dr[0], dr[1], R2.ln2_bounds())
        e2m = eps_iv(92, KSTAR)
        check("5.3", inter(e2k, e2r) and inter(e2k, e2m) and inter(e2r, e2m),
              "eps(92, 92, K*) 三库区间两两相交（m2 = 92 在 K* 处不可行，作形式值对拍）")
    except Exception as exc:
        check("5.9", False, "跨库对拍执行失败：%r" % (exc,))
    note("本段只作同值对拍；主判据（1 至 4 组）全部由本脚本自算，未依赖上述两库。")


def main():
    target, fh = install_output_tee()
    try:
        print("=" * 84)
        print("kcross-tail cycle-1 复算闸门 verify.py")
        print("档位：%s" % ("深度档 --deep（含 400 步二分复现端点、窗口 240 步二分、A5 全量 6456 项、镜像重跑与原地重跑闸门、账本两个子进程重跑）"
                         if DEEP else "默认档（端点取自所引日志并独立判号；A5 抽检 q ≤ 64；窗口用日志 bracket 两端判号）"))
        print("解释器：%s" % sys.executable)
        print("输出：stdout%s" % ("（stdout 已指向 %s）" % target if fh is None else "，并同时写入 %s" % target))
        print("纪律：主判据全部自算（自写区间引擎）；不读取 route-*.md 或 materials.md 的数字；")
        print("      第 5 组「跨库对拍」读项目区间库作对照，已单独标注。")
        print("退出码 0 = 全部判据通过；任一失败 = 1 并打印最小反例。")
        engine_selftest()
        assert_conclusion_1()
        assert_conclusion_2()
        assert_conclusion_3()
        assert_conclusion_4()
        cross_library_check()
        print()
        print("-" * 84)
        if FAILS:
            print("汇总：判据 %d 条，FAIL %d 条（用时 %.1f 秒）；最小反例：" % (NCHK, len(FAILS), time.time() - T_START))
            for cid, msg in FAILS:
                print("  FAIL %s：%s" % (cid, msg))
            print("退出码 1")
        else:
            print("汇总：判据 %d 条，FAIL 0 条（全部通过；用时 %.1f 秒）" % (NCHK, time.time() - T_START))
            print("退出码 0")
    finally:
        try:
            sys.stdout = sys.__stdout__ if sys.__stdout__ is not None else sys.stdout
            if fh is not None:
                fh.flush()
                fh.close()
        except Exception:
            pass
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
