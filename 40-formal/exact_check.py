#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exact_check.py —— 科拉茨初等引理（四条）在有限参数范围内的精确算术复核

运行方式（两种解释器都可以，脚本只用标准库）：
    python3 "40-formal/exact_check.py"
    "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" 40-formal/exact_check.py

必须先读的声明
一、本脚本只做**有限范围内的枚举与抽样验证，不是证明**。下面四条引理都是全称命题
    （对一切整数、或一切正整数、一切长度成立），全称命题无法靠有限枚举确立；即使本
    脚本全部 PASS，也只说明在被枚举的范围里没有反例。反过来，任何 FAIL 都会打印最小
    反例，那是真反例（在精确算术下算出的），不是估计误差。
二、全部算术精确：整数用 Python 任意精度 int；涉及阈值 θ = c_v / D_v 的比较用标准库
    fractions.Fraction（精确有理数）。全脚本不使用浮点数。
三、本脚本不读取、不导入 20-experiments/ 下的任何脚本或结果文件；所有被检验的量都在
    本文件内部按定义重新计算。随机样本用固定种子 SEED，结果可重复。
四、记号（与项目 30-proof-attempts/minimal-counterexample/attempt.md 的记号一致）：
    T(n) = n/2（n 偶）、(3n+1)/2（n 奇），定义域为全部整数（含负整数）；
    v_k(x) ∈ {0,1}^k：x 的前 k 步奇偶向量，第 i 位（i = 0 至 k 减 1）是 T^i(x) 的奇偶；
    S_k(x)：v_k(x) 中 1 的个数；
    c_k(x)：由递推 c_0 = 0、c_{j+1} = 3·c_j + b_j·2^j 定义（b_j 为第 j 位）；
    D_v = 2^{|v|} − 3^{m(v)}；θ_v = c_v / D_v（只在 D_v > 0 时用作阈值）；
    χ(x) = min{j ≥ 1 : T^j(x) < x}（停时，不存在时记 ∞）；
    τ(x) = min{j ≥ 1 : 3^{S_j(x)} < 2^j}（系数停时）；
    σ(x) = min{j ≥ 1 : T^j(x) = 1}（总停时，在 T 动力系统下）；
    E_k = {r : 1 ≤ r < 2^k，χ(r) ≥ k+1}。
五、四条引理（每条一个断言函数，精确陈述见各自的 statement 字符串）：
    引理 1（奇偶向量与仿射公式）：3^{S_k(x)}·x + c_k(x) = 2^k·T^k(x)；v_k 只由
        x mod 2^k 决定，r ↦ v_k(r)（r ∈ [0, 2^k)）是到 {0,1}^k 的双射。
    引理 2（c 的递推）：沿轨迹的递推、字级递推 c(v0) = c(v)、c(v1) = 3c(v) + 2^{|v|}、
        闭式 c(v) = Σ_{i: v_i = 1} 2^i·3^{#(v 中位于 i 之后的 1)} 三者一致，且满足拼接
        恒等式 c_{j+l}(x) = 3^{S_l(T^j x)}·c_j(x) + 2^j·c_l(T^j x)。
    引理 3（环方程与 2^k > 3^m 的必要性）：x > 0 且 T^k(x) = x ⟹ x·(2^k − 3^{S_k(x)})
        = c_k(x) 且 2^k > 3^{S_k(x)}；并以负整数上已知的环（含 −1 与 −5 所在的两个）做
        阳性对照，检验该必要性的假设「x > 0」确实是本质的。
    引理 4（停时与奇偶向量长度的对应关系）：χ(x) = min{j : x > θ_{v_j(x)}}（等价地逐点
        判据 T^j(x) < x ⟺ D_j > 0 且 x·D_j > c_j）；τ(x) ≤ χ(x)；χ(x) ≥ k+1 ⟹
        x mod 2^k ∈ E_k；σ(x) = min{j : 3^{S_j(x)}·x + c_j(x) = 2^j}。
六、关于 gmpy2 与 sympy：本项目环境里装有 gmpy2 与 sympy（允许使用），但本脚本的精确性
    由 Python 内置任意精度 int 与 fractions.Fraction 保证，不需要它们，故未导入；这样
    系统自带的 python3 也能直接运行本脚本（该解释器没有 gmpy2）。
"""

from __future__ import annotations

import random
import sys
from fractions import Fraction

SEED = 20261020

K_VEC = 16          # 引理 1 与 2：奇偶向量长度上限（全部 2^k 个向量）
K_SPLIT = 10        # 引理 2c：全枚举拼接恒等式的长度上限（更长用抽样）
K_SPLIT_MAX = 20    # 引理 2c：抽样拼接恒等式的长度上限
N_SPLIT_SAMPLE = 300
K_CYCLE = 32        # 引理 3a 与 3b：k 的枚举上限
X_CYCLE = 40000     # 引理 3a 与 3b：正整数 x 的枚举上限
X_NEG = 30000       # 引理 3d：负整数扫描范围（|x| 上限）
K_NEG = 40          # 引理 3d：负环周期上限
X_STOP = 20000      # 引理 4：正整数 x 的枚举上限
K_E = 14            # 引理 4c：E_k 的层数上限
X_FRAC = 5000       # 引理 4e：用 Fraction 比较阈值的样本上限
CAP = 2000          # 引理 4：单条轨道的迭代上限（安全阀）

POW3 = [3 ** i for i in range(48)]      # 供 S ≤ 47 的情形索引


#================================================================= 基本定义

def T(n):
    """加速科拉茨映射：n 偶 取 n/2；n 奇 取 (3n+1)/2。负整数同样适用（Python 的 % 对负数给非负余数）。"""
    return (3 * n + 1) // 2 if n % 2 else n // 2


def iter_T(x, k):
    for _ in range(k):
        x = T(x)
    return x


def word_of(x, k):
    """x 的前 k 步奇偶向量（由直接迭代算出，不依赖任何公式）。"""
    w = []
    for _ in range(k):
        w.append(x % 2)
        x = T(x)
    return tuple(w)


def word_from_bits(r, k):
    """把 r 的低 k 位直接当作长度 k 的字（枚举全部 2^k 个字用的独立路径）。"""
    return tuple((r >> i) & 1 for i in range(k))


def traj(x, n):
    """返回 j = 0 至 n 的 (S_j, c_j, T^j(x)) 三个列表，由轨迹递推算出。"""
    S = [0] * (n + 1)
    C = [0] * (n + 1)
    V = [x] * (n + 1)
    v = x
    s = 0
    cc = 0
    for j in range(1, n + 1):
        bit = v % 2
        if bit:
            s += 1
            cc = 3 * cc + (1 << (j - 1))
        v = T(v)
        S[j] = s
        C[j] = cc
        V[j] = v
    return S, C, V


def S_c_of_word(w):
    """字级递推：c(空) = 0、c(v0) = c(v)、c(v1) = 3·c(v) + 2^{|v|}。"""
    s = 0
    cc = 0
    for j, b in enumerate(w):
        if b:
            s += 1
            cc = 3 * cc + (1 << j)
    return s, cc


def c_closed_form(w):
    """闭式 c = Σ_{i: w_i = 1} 2^i · 3^{#(w 中位于 i 之后的 1)}。"""
    suf = 0
    cc = 0
    for i in range(len(w) - 1, -1, -1):
        if w[i]:
            cc += (1 << i) * POW3[suf]
            suf += 1
    return cc


def chi_direct(x, cap=10 ** 6):
    """χ(x) = min{j ≥ 1 : T^j(x) < x}，由直接迭代算出；x ≤ 1 时不存在（返回 None）。"""
    if x <= 1:
        return None
    v = x
    for j in range(1, cap + 1):
        v = T(v)
        if v < x:
            return j
    return None


def big_samples():
    """大整数样本：随机（固定种子）与结构化各若干，含负整数。"""
    rnd = random.Random(SEED)
    out = []
    for bits, k, cnt in ((256, 96, 3), (1024, 128, 3), (4096, 200, 3)):
        for _ in range(cnt):
            x = rnd.getrandbits(bits) | (1 << (bits - 1))
            out.append((x, k))
            out.append((-x, k))
    out += [
        (2 ** 1000 - 1, 120),
        (2 ** 1000 + 1, 120),
        (3 ** 999, 120),
        (-(2 ** 1000 - 1), 120),
        (-(10 ** 300 + 7), 120),
    ]
    return out


#================================================================= 报告框架

class Sub:
    """一条子断言：累计失败数，并保留「最小」反例（按 key 的字典序最小）。"""

    def __init__(self, code, statement, scale=""):
        self.code = code
        self.statement = statement
        self.scale = scale
        self.failures = 0
        self.worst_key = None
        self.worst = ""

    def ok(self, cond, key, detail):
        if cond:
            return True
        self.failures += 1
        if self.worst_key is None or key < self.worst_key:
            self.worst_key = key
            self.worst = detail
        return False


class Lemma:
    def __init__(self, no, title, statement):
        self.no = no
        self.title = title
        self.statement = statement
        self.subs = []

    def sub(self, code, statement, scale=""):
        s = Sub(code, statement, scale)
        self.subs.append(s)
        return s

    @property
    def failed(self):
        return any(s.failures for s in self.subs)


def report(lem):
    status = "FAIL" if lem.failed else "PASS"
    print("=" * 100)
    print(f"【{status}】引理 {lem.no}：{lem.title}")
    print(f"    陈述：{lem.statement}")
    for s in lem.subs:
        st = "FAIL" if s.failures else "PASS"
        print(f"    [{st}] {s.code} {s.statement}")
        print(f"           规模：{s.scale}；失败：{s.failures}")
        if s.failures:
            print(f"           最小反例（本次扫描检出的 {s.failures} 个失败里按键值字典序最小者）：{s.worst}")


#================================================================= 引理 1

def check_lemma1():
    lem = Lemma(
        1,
        "奇偶向量与仿射公式",
        "对一切整数 x 与 j ≥ 0：3^{S_j(x)}·x + c_j(x) = 2^j·T^j(x)；且 v_j 只由 x mod 2^j "
        "决定，r ↦ v_j(r)（r ∈ [0, 2^j)）是到 {0,1}^j 的双射。",
    )
    a = lem.sub(
        "1a",
        "仿射恒等式：对每个 k 与每个 r ∈ [0, 2^k)，3^{S_k(r)}·r + c_k(r) = 2^k·T^k(r)"
        "（S、c 由轨迹逐步递推，等式右侧用同一次迭代得到的 T^k(r)）",
    )
    b = lem.sub(
        "1b",
        "双射：r ↦ v_k(r) 给出 2^k 个互不相同的奇偶向量，即每个长度 k 的字恰好被一个剩余类实现",
    )
    c1 = lem.sub(
        "1c",
        "每个字都被实现（构造性路径）：r_v = c_v·(2^k − 3^{m_v}) 的模 2^k 逆元，验证 v_k(r_v) = v",
    )
    d = lem.sub(
        "1d",
        "随机大整数与结构化大整数（含负整数）：仿射恒等式成立，且 v_k(x) = v_k(x mod 2^k)",
    )

    n_res = 0
    n_words = 0
    for k in range(0, K_VEC + 1):
        seen = {}
        for r in range(1 << k):
            v = r
            s = 0
            cc = 0
            w = []
            for j in range(k):
                bit = v % 2
                w.append(bit)
                if bit:
                    s += 1
                    cc = 3 * cc + (1 << j)
                v = T(v)
            w = tuple(w)
            a.ok(
                POW3[s] * r + cc == (1 << k) * v,
                (k, r),
                f"k = {k}，r = {r}：3^({s})·r + c = {POW3[s] * r + cc}，"
                f"而 2^k·T^k(r) = {(1 << k) * v}（c = {cc}，S = {s}）",
            )
            seen[w] = seen.get(w, 0) + 1
            n_res += 1
        dup = [w for w, cnt in seen.items() if cnt != 1]
        b.ok(
            len(seen) == (1 << k) and not dup,
            (k, 0),
            f"k = {k}：不同向量 {len(seen)} 个（期望 {1 << k}），重复向量示例 {dup[:3]}",
        )
        for w0 in seen:
            n_words += 1
            s, cc = S_c_of_word(w0)
            if k == 0:
                rv = 0
            else:
                dvec = (1 << k) - POW3[s]
                rv = (cc * pow(dvec, -1, 1 << k)) % (1 << k)
            got = word_of(rv, k)
            c1.ok(
                got == w0,
                (k, rv),
                f"k = {k}，字 {w0}：构造出 r_v = {rv}，其奇偶向量为 {got}",
            )
    a.scale = f"k = 0 至 {K_VEC} 的全部剩余类，共 {n_res} 个"
    b.scale = f"k = 0 至 {K_VEC} 的每一层"
    c1.scale = f"k = 0 至 {K_VEC} 的全部字，共 {n_words} 个"

    for x, k in big_samples():
        S, C, V = traj(x, k)
        d.ok(
            (3 ** S[k]) * x + C[k] == (1 << k) * V[k],
            (k, abs(x)),
            f"x = {x}，k = {k}：3^S·x + c = {(3 ** S[k]) * x + C[k]} ≠ 2^k·T^k(x) = {(1 << k) * V[k]}",
        )
        d.ok(
            word_of(x, k) == word_of(x % (1 << k), k),
            (k, abs(x)),
            f"x = {x}，k = {k}：v_k(x) ≠ v_k(x mod 2^k)",
        )
    d.scale = f"固定种子 {SEED} 的随机样本（256 / 1024 / 4096 位，正负各半）加 5 个结构化样本，共 {len(big_samples())} 个"
    return lem


#================================================================= 引理 2

def check_lemma2():
    lem = Lemma(
        2,
        "c 的递推",
        "沿轨迹的递推 c_{j+1} = 3·c_j + b_j·2^j、字级递推 c(v0) = c(v)、c(v1) = 3c(v) + 2^{|v|}、"
        "闭式 c(v) = Σ_{i: v_i = 1} 2^i·3^{#(v 中位于 i 之后的 1)} 三者给出同一个 c，"
        "且 c 满足拼接恒等式 c_{j+l}(x) = 3^{S_l(T^j x)}·c_j(x) + 2^j·c_l(T^j x)。",
    )
    a = lem.sub(
        "2a",
        "轨迹递推与字级递推一致（字由直接迭代独立算出）",
    )
    b = lem.sub(
        "2b",
        "闭式与字级递推一致（字由二进制枚举独立给出，不经轨迹）",
    )
    c2 = lem.sub(
        "2c",
        "拼接恒等式 c_{j+l}(x) = 3^{S_l(T^j x)}·c_j(x) + 2^j·c_l(T^j x)",
    )

    n_a = 0
    for k in range(0, K_VEC + 1):
        for r in range(1 << k):
            w = word_of(r, k)
            S, C, _ = traj(r, k)
            s2, c2v = S_c_of_word(w)
            a.ok(
                S[k] == s2 and C[k] == c2v,
                (k, r),
                f"k = {k}，r = {r}：轨迹递推 (S, c) = ({S[k]}, {C[k]})，"
                f"字级递推 (S, c) = ({s2}, {c2v})（字 {w}）",
            )
            n_a += 1
    a.scale = f"k = 0 至 {K_VEC} 的全部 {n_a} 个剩余类"

    n_b = 0
    for k in range(0, K_VEC + 1):
        for r in range(1 << k):
            w = word_from_bits(r, k)
            _, c_rec = S_c_of_word(w)
            c_cl = c_closed_form(w)
            b.ok(
                c_rec == c_cl,
                (k, r),
                f"k = {k}，字 {w}：递推 c = {c_rec}，闭式 c = {c_cl}",
            )
            n_b += 1
    b.scale = f"k = 0 至 {K_VEC} 的全部 {n_b} 个字"

    def split_check(k, x, key):
        S, C, V = traj(x, k)
        for j in range(0, k + 1):
            l = k - j
            S2, C2, _ = traj(V[j], l)
            lhs = C[k]
            rhs = (3 ** S2[l]) * C[j] + (1 << j) * C2[l]
            c2.ok(
                lhs == rhs,
                key + (j,),
                f"k = {k}，x = {x}，拼接点 j = {j}：c_k(x) = {lhs} ≠ "
                f"3^({S2[l]})·c_j(x) + 2^j·c_({l})(T^j x) = {rhs}",
            )

    n_c = 0
    for k in range(0, K_SPLIT + 1):
        for r in range(1 << k):
            split_check(k, r, (k, r))
            n_c += k + 1
    rnd = random.Random(SEED + 1)
    for k in range(K_SPLIT + 1, K_SPLIT_MAX + 1):
        for _ in range(N_SPLIT_SAMPLE):
            r = rnd.getrandbits(k)
            split_check(k, r, (k, r))
            n_c += k + 1
    for x, k in big_samples():
        kk = min(k, 64)
        split_check(kk, x, (kk, abs(x)))
        n_c += kk + 1
    c2.scale = (
        f"k = 0 至 {K_SPLIT} 全枚举、k = {K_SPLIT + 1} 至 {K_SPLIT_MAX} 每层 {N_SPLIT_SAMPLE} 个随机样本、"
        f"加大整数样本，共 {n_c} 个 (k, x, j) 组合"
    )
    return lem


#================================================================= 引理 3

def check_lemma3():
    lem = Lemma(
        3,
        "环方程与 2^k > 3^m 的必要性",
        "若 x > 0 且 T^k(x) = x，则 x·(2^k − 3^{S_k(x)}) = c_k(x) 且 2^k > 3^{S_k(x)}；"
        "该必要性的假设「x > 0」是本质的——负整数上已知的环（含 −1 与 −5 所在的两个）"
        "全部满足反向不等式 2^k < 3^m，而环方程本身仍成立。",
    )
    a = lem.sub(
        "3a",
        "必要性：对 1 ≤ x ≤ 40000、1 ≤ k ≤ 32，若 T^k(x) = x 则 2^k > 3^{S_k(x)} "
        "且 x·(2^k − 3^{S_k(x)}) = c_k(x)",
    )
    b = lem.sub(
        "3b",
        "(k, m) 网格（k ≤ 32、0 ≤ m ≤ k）：满足 2^k > 3^m 的对上逐点核对双向等价 "
        "T^k(x) = x ⟺ x·(2^k − 3^m) = c_k(x)；不满足 2^k > 3^m 的对上范围内没有正不动点",
    )
    c3 = lem.sub(
        "3c",
        "全部长度 k ≤ 16 的 2^k 个字上的环判据：D = 2^k − 3^{m} 恒非零；m ≥ 1 时 "
        "c/D > 0 ⟺ 2^k > 3^m；D | c 时 x* = c/D 必为整数且 T^k(x*) = x*、v_k(x*) 与字一致",
    )
    dd = lem.sub(
        "3d",
        "阳性对照（负整数环）：穷举 |x| ≤ 30000、周期 ≤ 40 的负整数环，必须找回 −1 与 "
        "−5 所在的环；每个环的每个元素满足环方程与 2^k < 3^{S_k}",
    )

    # 网格的静态统计
    grid_total = 0
    grid_sat = 0
    for k in range(1, K_CYCLE + 1):
        for m in range(0, k + 1):
            grid_total += 1
            if (1 << k) > POW3[m]:
                grid_sat += 1

    fixed = {}
    first_mismatch = {}
    for x in range(1, X_CYCLE + 1):
        v = x
        s = 0
        cc = 0
        for k in range(1, K_CYCLE + 1):
            bit = v % 2
            if bit:
                s += 1
                cc = 3 * cc + (1 << (k - 1))
            v = T(v)
            dvec = (1 << k) - POW3[s]
            is_fixed = (v == x)
            eq = (x * dvec == cc)
            if is_fixed:
                fixed[(k, s)] = fixed.get((k, s), 0) + 1
                a.ok(
                    dvec > 0 and eq,
                    (k, x),
                    f"k = {k}，x = {x}：T^k(x) = x 而 2^k = {1 << k}、3^m = {POW3[s]}、"
                    f"c = {cc}、x·D = {x * dvec}（需要 D > 0 且 x·D = c）",
                )
            if dvec > 0 and is_fixed != eq:
                if (k, s) not in first_mismatch:
                    first_mismatch[(k, s)] = (
                        f"k = {k}，m = {s}，x = {x}：T^k(x) = x 为 {is_fixed}，"
                        f"而 x·(2^k − 3^m) = c 为 {eq}（c = {cc}，D = {dvec}）"
                    )

    n_grid_sat = 0
    n_grid_unsat = 0
    for k in range(1, K_CYCLE + 1):
        for m in range(0, k + 1):
            if (1 << k) > POW3[m]:
                n_grid_sat += 1
                b.ok(
                    (k, m) not in first_mismatch,
                    (k, m),
                    first_mismatch.get((k, m), ""),
                )
            else:
                n_grid_unsat += 1
                b.ok(
                    fixed.get((k, m), 0) == 0,
                    (k, m),
                    f"k = {k}，m = {m}：2^k = {1 << k} ≤ 3^m = {POW3[m]}，"
                    f"但范围内有 {fixed.get((k, m), 0)} 个正不动点",
                )
    a.scale = f"1 ≤ x ≤ {X_CYCLE}、1 ≤ k ≤ {K_CYCLE}，共 {X_CYCLE * K_CYCLE} 个 (x, k) 点"
    b.scale = (
        f"{grid_total} 个 (k, m) 对，其中满足 2^k > 3^m 的 {n_grid_sat} 个（双向逐点核对）、"
        f"不满足的 {n_grid_unsat} 个（要求范围内无正不动点）"
    )

    hits = 0
    pos_hits = 0
    neg_hits = 0
    for k in range(1, K_VEC + 1):
        for r in range(1 << k):
            w = word_from_bits(r, k)
            m, cc = S_c_of_word(w)
            dvec = (1 << k) - POW3[m]
            c3.ok(dvec != 0, (k, r), f"k = {k}，字 {w}：2^k = 3^m（2^k 偶、3^m 奇，不应发生）")
            if cc % dvec == 0:
                hits += 1
                xstar = cc // dvec
                if m >= 1:
                    c3.ok(
                        (xstar > 0) == (dvec > 0),
                        (k, xstar),
                        f"k = {k}，字 {w}：x* = {xstar} 与 D = 2^k − 3^m = {dvec} 符号不一致",
                    )
                    if xstar > 0:
                        pos_hits += 1
                    else:
                        neg_hits += 1
                c3.ok(
                    iter_T(xstar, k) == xstar,
                    (k, xstar),
                    f"k = {k}，字 {w}：x* = {xstar} 而 T^k(x*) = {iter_T(xstar, k)} ≠ x*",
                )
                c3.ok(
                    word_of(xstar, k) == w,
                    (k, xstar),
                    f"k = {k}，字 {w}：x* = {xstar} 的奇偶向量为 {word_of(xstar, k)}",
                )
    c3.scale = (
        f"k = 1 至 {K_VEC} 的全部 131070 个字中，D 整除 c 的 {hits} 个"
        f"（正候选 {pos_hits} 个、负候选 {neg_hits} 个、零候选 {hits - pos_hits - neg_hits} 个）"
    )

    found = {}
    for x in range(-1, -X_NEG - 1, -1):
        vals = [x]
        for _ in range(K_NEG):
            vals.append(T(vals[-1]))
        for k in range(1, K_NEG + 1):
            if vals[k] == x:
                cyc = frozenset(vals[:k])
                if cyc not in found:
                    found[cyc] = (x, k)
                break

    for cyc, (rep, k) in found.items():
        for e in cyc:
            S, C, V = traj(e, k)
            dd.ok(V[k] == e, (k, e), f"环 {sorted(cyc)}：T^({k})({e}) = {V[k]} ≠ {e}")
            dd.ok(
                e * ((1 << k) - POW3[S[k]]) == C[k],
                (k, e),
                f"环 {sorted(cyc)}：x = {e}，k = {k}，m = {S[k]}："
                f"x·(2^k − 3^m) = {e * ((1 << k) - POW3[S[k]])} ≠ c = {C[k]}",
            )
            dd.ok(
                (1 << k) < POW3[S[k]],
                (k, e),
                f"环 {sorted(cyc)}：x = {e} < 0，但 2^k = {1 << k} ≥ 3^m = {POW3[S[k]]}",
            )

    def cycle_of(x):
        seen = []
        v = x
        for _ in range(K_NEG + 1):
            seen.append(v)
            v = T(v)
            if v == x:
                return frozenset(seen)
        return None

    cyc_m1 = cycle_of(-1)
    cyc_m5 = cycle_of(-5)
    dd.ok(
        len(found) >= 3,
        (0, 0),
        f"只找到 {len(found)} 个负整数环：{[sorted(c) for c in found]}",
    )
    dd.ok(cyc_m1 in found, (0, 0), f"−1 所在的环 {sorted(cyc_m1)} 未被找回")
    dd.ok(cyc_m5 in found, (0, 0), f"−5 所在的环 {sorted(cyc_m5)} 未被找回")
    dd.scale = (
        f"|x| ≤ {X_NEG}、周期 ≤ {K_NEG}；找到 {len(found)} 个环："
        + "、".join(str(sorted(c)) for c in sorted(found, key=lambda c: min(c)))
    )
    return lem


#================================================================= 引理 4

def check_lemma4():
    lem = Lemma(
        4,
        "停时与奇偶向量长度的对应关系",
        "χ(x) = min{j ≥ 1 : T^j(x) < x} 等于 min{j : x > θ_{v_j(x)}}（θ 只在 D_j > 0 时定义），"
        "等价地逐点判据 T^j(x) < x ⟺ D_j > 0 且 x·D_j > c_j；τ(x) ≤ χ(x)；"
        "χ(x) ≥ k+1 ⟹ x mod 2^k ∈ E_k；σ(x) = min{j ≥ 1 : T^j(x) = 1} 等于"
        "使 3^{S_j(x)}·x + c_j(x) = 2^j 的最短长度（全部结论仅在所枚举的范围内核对）。",
    )
    a = lem.sub(
        "4a",
        "下降判据（逐点等价）：T^j(x) < x ⟺ 2^j > 3^{S_j(x)} 且 x·(2^j − 3^{S_j(x)}) > c_j(x)",
    )
    b = lem.sub(
        "4b",
        "停时公式：独立迭代算出的 χ(x) 等于 min{j : x > θ_{v_j(x)}}；且 τ(x) = min{j : D_j > 0} ≤ χ(x)",
    )
    c4 = lem.sub(
        "4c",
        f"相容性：χ(x) ≥ k+1 ⟹ (x mod 2^k) ∈ E_k（E_k 由 χ 的暴力定义独立算出，k ≤ {K_E}）（单向断言，反向见 4f）",
    )
    dd = lem.sub(
        "4d",
        "总停时：σ(x) = min{j : T^j(x) = 1} 等于 min{j : 3^{S_j(x)}·x + c_j(x) = 2^j}；并逐点核对仿射恒等式",
    )
    e = lem.sub(
        "4e",
        f"阈值的有理数形式：用 Fraction 精确比较「x > θ（θ = c_j / D_j）」与整数形式「x·D_j > c_j」等价（x ≤ {X_FRAC}）",
    )
    f = lem.sub(
        "4f",
        "反向不成立的具体见证：范围内存在 x mod 2^k ∈ E_k 而 χ(x) < k+1（这正是本脚本只断言单向的原因）",
    )

    chi_map = {}
    n4a = 0
    n4e = 0
    for x in range(1, X_STOP + 1):
        v = x
        s = 0
        cc = 0
        p2 = 1
        p3 = 1
        chi = None
        tau = None
        sigma = None
        chi_formula = None
        sigma_formula = None
        j = 0
        while j < CAP:
            j += 1
            bit = v % 2
            p2 <<= 1
            if bit:
                s += 1
                cc = 3 * cc + (p2 >> 1)
                p3 *= 3
            v = T(v)
            dvec = p2 - p3
            desc = v < x
            crit = (dvec > 0 and x * dvec > cc)
            a.ok(
                desc == crit,
                (j, x),
                f"j = {j}，x = {x}：T^j(x) = {v}，下降为 {desc}；"
                f"判据（D = {dvec} > 0 且 x·D = {x * dvec} > c = {cc}）为 {crit}",
            )
            n4a += 1
            if dvec > 0 and tau is None:
                tau = j
            if desc and chi is None:
                chi = j
            if crit and chi_formula is None:
                chi_formula = j
            if v == 1 and sigma is None:
                sigma = j
            if p3 * x + cc == p2 and sigma_formula is None:
                sigma_formula = j
            dd.ok(
                p3 * x + cc == p2 * v,
                (j, x),
                f"j = {j}，x = {x}：3^S·x + c = {p3 * x + cc} ≠ 2^j·T^j(x) = {p2 * v}",
            )
            if x <= X_FRAC:
                th = Fraction(cc, dvec) if dvec > 0 else None
                e.ok(
                    desc == (th is not None and Fraction(x) > th),
                    (j, x),
                    f"j = {j}，x = {x}：θ = {th}，x > θ 为 {th is not None and Fraction(x) > th}，"
                    f"而实际下降为 {desc}",
                )
                n4e += 1
            if v == 1:
                break
        chi_map[x] = chi
        ch2 = chi_direct(x)
        b.ok(
            ch2 == chi,
            (0, x),
            f"x = {x}：独立迭代 χ = {ch2}，本次扫描 χ = {chi}",
        )
        if x >= 2:
            b.ok(
                chi is not None and chi == chi_formula,
                (0, x),
                f"x = {x}：χ = {chi}，由阈值给出的最小值 = {chi_formula}",
            )
            b.ok(
                tau is not None and tau <= chi,
                (0, x),
                f"x = {x}：τ = {tau}，χ = {chi}（应有 τ ≤ χ）",
            )
            dd.ok(
                sigma is not None and sigma == sigma_formula,
                (0, x),
                f"x = {x}：σ = {sigma}，由仿射恒等式给出的最小值 = {sigma_formula}",
            )
        else:
            b.ok(
                chi is None and chi_formula is None,
                (0, x),
                f"x = 1：χ 应为 ∞（永不下降），得到 χ = {chi}、公式值 = {chi_formula}",
            )
            dd.ok(sigma == 2, (0, x), f"x = 1：σ = {sigma}，期望 2（轨道 1 到 2 再到 1）")
    a.scale = f"1 ≤ x ≤ {X_STOP}，1 ≤ j ≤ σ(x)，共 {n4a} 个 (x, j) 点"
    b.scale = f"1 ≤ x ≤ {X_STOP}（含 x = 1 的 χ = ∞ 边界情形）"
    dd.scale = f"1 ≤ x ≤ {X_STOP}"
    e.scale = f"1 ≤ x ≤ {X_FRAC}，共 {n4e} 个 (x, j) 点，逐个用 Fraction 比较"

    # E_k 由暴力定义独立算出
    chi_small = {}
    for r in range(1, 1 << K_E):
        chi_small[r] = chi_direct(r)
    E = {}
    for k in range(1, K_E + 1):
        E[k] = {r for r in range(1, 1 << k) if chi_small[r] is None or chi_small[r] >= k + 1}

    n4c = 0
    reverse_min = None
    for x in range(1, X_STOP + 1):
        chx = chi_map[x]
        for k in range(1, K_E + 1):
            n4c += 1
            ge = chx is None or chx >= k + 1
            r = x % (1 << k)
            memb = r in E[k]
            if ge:
                c4.ok(
                    memb,
                    (k, x),
                    f"k = {k}，x = {x}：χ = {chx} ≥ k+1，但 x mod 2^k = {r} 不在 E_k 中",
                )
            elif memb and (reverse_min is None or (k, x) < reverse_min):
                reverse_min = (k, x, chx, r)
    c4.scale = f"1 ≤ x ≤ {X_STOP}、1 ≤ k ≤ {K_E}，共 {n4c} 个 (x, k) 点"

    if reverse_min is None:
        f.ok(False, (0, 0), "范围内找不到「x mod 2^k ∈ E_k 而 χ(x) < k+1」的例子")
        f.scale = f"1 ≤ x ≤ {X_STOP}、1 ≤ k ≤ {K_E}：未找到反例（与预期不符）"
    else:
        k0, x0, ch0, r0 = reverse_min
        v = x0
        non_desc = True
        for j in range(1, k0 + 1):
            v = T(v)
            if v < x0:
                non_desc = False
        f.ok(
            (r0 in E[k0]) and (ch0 < k0 + 1) and non_desc is False,
            (0, 0),
            f"k = {k0}，x = {x0} 的见证核对失败",
        )
        f.scale = (
            f"最小反例 (k, x) = ({k0}, {x0})：x mod 2^k = {r0} 属于第 {k0} 层的 E_k（E_k 独立暴力算出），"
            f"而 χ(x) = {ch0} < k+1；直接迭代在 j = {ch0} 处首次下降"
        )
    return lem


#================================================================= 主流程

BANNER = f"""exact_check.py —— 科拉茨初等引理（四条）的有限范围精确算术复核
声明：以下全部是有限范围的枚举与抽样验证，不是证明。四条引理都是全称命题，
      全称命题无法靠有限枚举确立；全部 PASS 只说明所枚举范围内无反例。
      全部算术精确：int 与 fractions.Fraction，无浮点数。
      本脚本不读取 20-experiments/ 下的任何结果文件；所有量在此按定义重新计算。
      规模常量：K_VEC = {K_VEC}，K_CYCLE = {K_CYCLE}，X_CYCLE = {X_CYCLE}，X_NEG = {X_NEG}，
      K_NEG = {K_NEG}，X_STOP = {X_STOP}，K_E = {K_E}，随机种子 SEED = {SEED}。"""


def main():
    print(BANNER)
    lemmas = []
    for fn in (check_lemma1, check_lemma2, check_lemma3, check_lemma4):
        lem = fn()
        report(lem)
        lemmas.append(lem)
        sys.stdout.flush()

    failed = [lem.no for lem in lemmas if lem.failed]
    print("=" * 100)
    if failed:
        print(f"总计：{len(lemmas)} 条引理，失败于引理 {failed}（反例见上，均为精确算术下的真反例）")
        print("退出码 1")
        return 1
    print(f"总计：{len(lemmas)} 条引理全部 PASS（有限范围，不是证明）")
    print("退出码 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
