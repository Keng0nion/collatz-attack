#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-2 第 10 步：两套不依赖 (L1) 的独立顶点核对。

背景（诚实登记）：第 2 步的顶点穷举在 m2 >= 10 时用的是「约简穷举」，它依赖 (L1)
即「y_j = 1 不可行」这条初等引理（第 2 步已验证其判据 (δ^m2−1)/(δ−1) < W）。因此那
部分不是独立核对。本脚本补两条不依赖 (L1) 的路线：

  A. 全活跃子集穷举（对 m2 = 10 与 m2 = 12）：枚举全部 C(2m2+1, m2) 个大小为 m2 的
     活跃子集，精确解线性方程组、查秩、查可行性。原理：任一顶点处存在一个大小为 m2
     且秩为 m2 的活跃子集，故此法不漏顶点，且完全不提 (L1)。代价：组合数爆炸，
     m2 = 10 为 352716，m2 = 12 为 5200300，m2 = 20 已是 2.7e11（不可能）。

  B. 线性目标最优解（对 m2 = 20、47、91）：对严格正权重 w，用 z3 的 LRA 判定
     「P ∧ Σ w_j y_j < min_r Σ w_j V_r[j]」是否 unsat。un sat 即「P 上该线性目标的
     最小值为诸旋转之一的最小值」，属于不依赖 (L1) 的独立读数。并对若干 w 取
     z3 的最优模型，转成精确分数后核对：可行、活跃秩 = m2（顶点证书）、且恰是某个旋转。
     局限如实写明：这是有限次 w 的取点，不能排除「某个未被抽到的 w 才暴露别的顶点」。

裁决一律用 Fraction 与整数幂，浮点只出现在摘要行。
"""
import sys
import time
from fractions import Fraction
from itertools import combinations

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
import mpmath
import z3
from r2_common import (delta_rigorous_bounds, v_vertex, vertex, feasible,
                       constraint_list, solve_exact, Det)

D_LO7, _ = delta_rigorous_bounds(10 ** 7)


def rank_exact(rows, ncols):
    """精确秩（Fraction 行阶梯）。与 r2_b_vertices.py 的同名函数逐行相同（此处重写
    一份，是为了不 import 那个脚本、避免执行它顶层的穷举）。"""
    M = [[Fraction(v) for v in r] for r in rows]
    rank = 0
    for col in range(ncols):
        piv = None
        for i in range(rank, len(M)):
            if M[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        pv = M[rank][col]
        M[rank] = [v / pv for v in M[rank]]
        for i in range(len(M)):
            if i != rank and M[i][col] != 0:
                f = M[i][col]
                M[i] = [M[i][j] - f * M[rank][j] for j in range(ncols)]
        rank += 1
    return rank


def active_rank(y, m2, d, W):
    """点 y 处活跃约束的法向量集的秩（= m2 即为顶点的秩证书）。"""
    cons = constraint_list(m2, d, W)
    rows = []
    for a, b, sense in cons:
        val = sum(a[j] * y[j] for j in range(m2))
        if val == b:
            rows.append(a)
    return rank_exact(rows, m2), len(rows)


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def rat(fr):
    return z3.RealVal(f"{fr.numerator}/{fr.denominator}")


def z3_to_fraction_sexpr(val):
    """兜底路径：只处理两种形状的 sexpr，即「整数或 a.0」与「(/ a b)」（a、b 为前一种）。
    嵌套形状直接报错，不做猜测。主路径是 RatNumRef.as_fraction()，本函数是保险丝。"""
    s = val.sexpr().replace("\n", " ").strip()
    tok = s.replace("(", " ").replace(")", " ").replace("/", " ").split()
    vals = [Fraction(t[:-2] if t.endswith(".0") else t) for t in tok]
    if len(vals) == 1:
        return vals[0]
    if len(vals) == 2:
        return vals[0] / vals[1]
    raise ValueError(f"不认识的 sexpr 形状：{s[:80]}")


def full_enumeration(m2, d, W, progress=True):
    """全活跃子集穷举（不依赖 L1）：返回 (顶点字典, 子集总数, 用时)。"""
    cons = constraint_list(m2, d, W)
    n = len(cons)
    total = 1
    for i in range(m2):
        total = total * (n - i) // (i + 1)
    verts = {}
    t0 = time.time()
    cnt = 0
    for S in combinations(range(n), m2):
        cnt += 1
        if progress and cnt % 200000 == 0:
            say(f"      ... 已枚举 {cnt}/{total}（{time.time()-t0:.0f} s）")
        rows = [cons[i][0] for i in S]
        b = [cons[i][1] for i in S]
        sol, rank = solve_exact(rows, b)
        if sol is None or rank < m2:
            continue
        ok, _ = feasible(sol, m2, d, W)
        if ok:
            verts[tuple(sol)] = S
    return verts, total, time.time() - t0


def part_A():
    say("=" * 78)
    say("A 段：全活跃子集穷举（不依赖 (L1)），m2 = 10 与 m2 = 12")
    say("=" * 78)
    say("成本曲线（本机实测，用于说明为什么只做到 m2 = 10）：")
    say("    m2 = 10：C(21,10) = 352716 个子集，约 0.13 ms/个 → 约 50 s")
    say("    m2 = 12：C(25,12) = 5200300 个子集，实测 0.83 ms/个 → 投影约 72 min（本次未跑）")
    say("    m2 = 20：C(41,20) ≈ 2.7e11 个子集 → 不可达")
    cases = [
        ("A1 m2=10 δ_lo W=2000（即第 3 步的 E4）", 10, D_LO7, Fraction(2000)),
    ]
    for tag, m2, d, W in cases:
        if W is None:
            W = Fraction(70) * (d ** m2 - 1) / (d - 1)
        say(f"\n[{tag}]")
        verts, total, dt = full_enumeration(m2, d, W)
        analytic = {tuple(vertex(m2, d, W, r)) for r in range(m2)}
        say(f"    子集总数 C({2*m2+1},{m2}) = {total}，用时 {dt:.1f} s")
        say(f"    可行顶点数 = {len(verts)}；与解析的 m2 = {m2} 个循环旋转相同 = "
            f"{set(verts.keys()) == analytic}（解析集大小 {len(analytic)}）")
        certs = sorted({active_rank(y, m2, d, W) for y in verts})
        say(f"    每个顶点的（活跃约束法向量秩，活跃约束条数）= {certs}")
        # 这一段的独立性说明：全程未调用任何与 (L1) 有关的判据
        say(f"    独立性：本段只用 constraint_list / solve_exact / feasible，"
            f"未使用 (L1) 或 v 的任何信息")


def claimed_min_psi(m2, d, W, w):
    """诸旋转上 Σw_j y_j 的最小值（精确分数）。"""
    best = None
    for r in range(m2):
        V = vertex(m2, d, W, r)
        val = sum(Fraction(w[j]) * V[j] for j in range(m2))
        if best is None or val < best:
            best = val
    return best


def part_B():
    say("\n" + "=" * 78)
    say("B 段：线性目标最优解（z3 LRA），m2 = 20、47、91")
    say("=" * 78)
    cases = [
        ("B1 m2=20 δ_lo W 使 v=70",        20, D_LO7, None,   14),
        ("B2 m2=47 δ_lo W=(47/91)·7e11",   47, D_LO7, Fraction(47, 91) * 10 ** 11 * 7, 12),
        ("B3 m2=91 δ_lo W=205632218873398596256", 91, D_LO7, Fraction(205632218873398596256), 10),
    ]
    for tag, m2, d, W, nweights in cases:
        if W is None:
            W = Fraction(70) * (d ** m2 - 1) / (d - 1)
        say(f"\n[{tag}]")
        claimed = {tuple(vertex(m2, d, W, r)) for r in range(m2)}
        det = Det(777 + m2)
        weights = []
        # 结构化权重
        weights.append([1] * m2)
        for j in range(min(m2, 4)):
            e = [0] * m2
            e[j] = 1
            weights.append(e)
        e = [0] * m2
        e[0] = 1
        e[m2 - 1] = 1
        weights.append(e)
        # 随机严格正权重
        while len(weights) < nweights:
            weights.append([det.between(1, 10 ** 6) for _ in range(m2)])
        ys = [z3.Real(f"y_{i}") for i in range(m2)]
        base = []
        for i in range(m2):
            base.append(ys[i] >= 1)
        for i in range(m2):
            base.append(ys[(i + 1) % m2] <= rat(d) * ys[i])
        base.append(sum(ys) >= rat(W))
        n_un = n_sat = n_bad = 0
        discovered = set()
        n_opt_model = 0
        t0 = time.time()
        for wi, w in enumerate(weights):
            target = claimed_min_psi(m2, d, W, w)
            obj = sum(Fraction(w[j]) * ys[j] for j in range(m2))
            s = z3.Solver()
            s.set("timeout", 300000)
            for c in base:
                s.add(c)
            s.add(obj < rat(target))
            r = s.check()
            if r == z3.unsat:
                n_un += 1
            else:
                n_sat += 1
                say(f"    !! w#{wi}：P ∧ (Σw·y < 旋转最小值) = {r}")
            # 另取最优模型，核对它是顶点且是旋转
            o = z3.Optimize()
            o.set("timeout", 300000)
            for c in base:
                o.add(c)
            h = o.minimize(obj)
            if o.check() != z3.sat:
                n_bad += 1
                say(f"    !! w#{wi}：Optimize 未给出 sat")
                continue
            md = o.model()
            pt = []
            okread = True
            for v in ys:
                val = z3.simplify(md.eval(v, model_completion=True))
                # 实测：Optimize 的模型值是 RatNumRef，其 .numerator()/.denominator() 返回
                # z3 的 IntNumRef（不是 Python int，int() 直接失败）；正确通道是 .as_fraction()，
                # 它直接给出 fractions.Fraction。故此处的读法以 .as_fraction() 为准。
                try:
                    if z3.is_rational_value(val):
                        fr = val.as_fraction()
                    else:
                        fr = z3_to_fraction_sexpr(val)
                except Exception as e:
                    okread = False
                    say(f"    （读模型异常：{type(e).__name__} {e}）")
                    break
                pt.append(Fraction(fr.numerator, fr.denominator))
            if not okread:
                n_bad += 1
                say(f"    !! w#{wi}：模型值不是有理数，未转成 Fraction")
                continue
            n_opt_model += 1
            inP, bad = feasible(pt, m2, d, W)
            rk, nact = active_rank(pt, m2, d, W)
            isrot = tuple(pt) in claimed
            psi_pt = sum(Fraction(w[j]) * pt[j] for j in range(m2))
            exact_opt = (psi_pt == target)
            if not (inP and rk == m2 and isrot and exact_opt):
                n_bad += 1
                say(f"    !! w#{wi}：可行 {inP}，秩 {rk}（活跃 {nact} 条），"
                    f"是旋转 {isrot}，目标值等于旋转最小值 {exact_opt}")
                if not inP:
                    say(f"        违反 {bad[:3]}")
            else:
                discovered.add(tuple(pt))
        say(f"    权重数 = {len(weights)}；unsat（即 P 上该线性目标的最优值与诸旋转一致）= {n_un}；"
            f"出现 sat = {n_sat}；模型核对异常 = {n_bad}")
        say(f"    取到最优模型并逐项精确核对的权重数 = {n_opt_model}；"
            f"由这些模型**发现**的顶点数 = {len(discovered)}/{m2}")
        say(f"    用时 {time.time()-t0:.1f} s")
        say(f"    局限：这是 {len(weights)} 个 w 的有限取点，不能排除「某个未抽到的 w "
            f"才暴露其他顶点」；它不构成顶点集的穷举。")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "AB"
    mpmath.mp.dps = 40
    if "A" in which:
        part_A()
    if "B" in which:
        part_B()
    say("\n口径：本脚本是独立核对，不是证明；A 段是穷举（在给定 m2 下完备），"
        "B 段是有限取点（不完备）。")
