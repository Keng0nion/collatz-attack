#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-4 审计脚本 1：定义转写核对、可行性边界探针、求解器对拍、枚举空间、小档独立枚举。

路线：完备性与依赖审计（vertex-m12 首轮）。本脚本不产生任何新数学判定，
只把「枚举 = 顶点集」论证所依赖的每一处代码语义逐项对拍，并把每一处
发现落成带 PASS/FAIL 的行，方便 grep。

用法（在 cycle-1/scripts 下）：
  PY="/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python"
  "$PY" route4_audit_semantics.py
"""
import sys
import time
import math
from fractions import Fraction
from itertools import combinations

import route4_util as U

CHECKS = []


def check(name, ok, detail=""):
    ok = bool(ok)
    CHECKS.append((name, ok))
    line = f"  [{'PASS' if ok else 'FAIL'}] {name}"
    if detail:
        line += f" —— {detail}"
    U.say(line)
    return ok


def main():
    t_start = time.time()
    U.say("=" * 78)
    U.say("route-4 审计脚本 1：语义对拍（定义转写、可行性边界、求解器、枚举空间、小档枚举）")
    U.say("=" * 78)

    # ---------------- [0] 版本身份、工具链、δ 的独立复算与记录锚点 ----------------
    U.say("\n[0] 版本身份、工具链、δ 独立复算")
    RC, RJ = U.load()
    import gmpy2
    import sympy
    import z3
    U.say(f"  python {sys.version.split()[0]}；sympy {sympy.__version__}；gmpy2 {gmpy2.version()}；"
          f"z3 {z3.get_version_string()}")

    D_LO7, D_HI7 = RC.delta_rigorous_bounds(10 ** 7)
    q = 10 ** 7
    t3q = gmpy2.mpz(3) ** q
    p = int(t3q.bit_length()) - 1
    r = p + 1
    check("独立复算 δ 下界（用 bit_length 定 p，与 delta_rigorous_bounds 输出一致）",
          Fraction(p, q) == D_LO7, f"p/q = {p}/{q}")
    check("独立复算 δ 上界（r = p+1）", Fraction(r, q) == D_HI7, f"r/q = {r}/{q}")
    check("整数幂严格性（2^p < 3^q < 2^r，p、r 见上）",
          (gmpy2.mpz(2) ** p < t3q) and (t3q < gmpy2.mpz(2) ** r))
    thr5 = (D_LO7 ** 5 - 1) / (D_LO7 - 1)
    check("m2=5 阈值与既有日志记录一致（r2_b_out.txt:93）",
          thr5 == Fraction(630347359154513105681, 40960000000000000000), f"W(阈值) = {thr5}")
    U.say(f"  D_LO7 = {D_LO7}；D_HI7 = {D_HI7}")

    # ---------------- [1] 约束表转写核对 ----------------
    U.say("\n[1] 约束表转写核对（独立转写 vs r2_common.constraint_list）")
    cases_def = [
        (Fraction(126797, 80000), Fraction(2000)),
        (Fraction(3, 2), Fraction(3, 2)),
        (Fraction(126797, 80000), Fraction(10 ** 6, 7)),
    ]
    n_cmp = 0
    n_bad = 0
    n_count_bad = 0
    first_bad = None
    for m2 in range(2, 11):
        for d, W in cases_def:
            mine = U.indep_constraints(m2, d, W)
            theirs = [(tuple(a), b, s) for (a, b, s) in RC.constraint_list(m2, d, W)]
            n_cmp += 1
            same_order = len(theirs) == len(mine) and all(x == y for x, y in zip(theirs, mine))
            same_multiset = sorted(mine, key=repr) == sorted(theirs, key=repr)
            if not (len(theirs) == 2 * m2 + 1 and same_order and same_multiset):
                n_bad += 1
                if first_bad is None:
                    first_bad = (m2, d, W)
            ge_n = sum(1 for _a, _b, s in theirs if s == "ge")
            le_n = sum(1 for _a, _b, s in theirs if s == "le")
            if not (ge_n == m2 + 1 and le_n == m2):
                n_count_bad += 1
    check(f"逐项一致（{n_cmp} 组：m2=2 至 10 × 3 组参数；顺序与多重集都比）",
          n_bad == 0, f"不一致组数 = {n_bad}，首个 = {first_bad}")
    check("条数与类型计数（2m2+1；ge = m2+1，le = m2）", n_count_bad == 0)

    # ---------------- [2] 可行性判定边界探针 ----------------
    U.say("\n[2] 可行性边界探针（含 C1 下界、C2 链与回绕、C3 和约束的等号处理）")
    cases_probe = [
        ("阴性对照 m2=2 δ=3/2 W=3/2", 2, Fraction(3, 2), Fraction(3, 2)),
        ("m2=2 δ_lo W=2000", 2, D_LO7, Fraction(2000)),
        ("m2=3 δ_lo W=2000", 3, D_LO7, Fraction(2000)),
        ("边界 m2=5 δ_lo W=阈值（v=1）", 5, D_LO7, thr5),
        ("基线 m2=10 δ_lo W=2000", 10, D_LO7, Fraction(2000)),
    ]
    eps_small = Fraction(1, 10 ** 30)
    eps_big = Fraction(1, 10 ** 6)
    for label, m2, d, W in cases_probe:
        v = RC.v_vertex(m2, d, W)
        V = [RC.vertex(m2, d, W, rot) for rot in range(m2)]
        check(f"{label}：{m2} 个旋转互异", len(set(V)) == m2)
        if v >= 1:
            check(f"{label}：全部旋转可行（v ≥ 1）", all(RC.feasible(y, m2, d, W)[0] for y in V))
        else:
            check(f"{label}：全部旋转不可行（v < 1）",
                  all(not RC.feasible(y, m2, d, W)[0] for y in V), f"v = {v}")
        if v == 1:
            check(f"{label}：存在坐标恰为 1（阈值档）", any(t == 1 for y in V for t in y))
        elif v > 1:
            check(f"{label}：全部坐标严格大于 1", all(t > 1 for y in V for t in y))

        pts = []
        for rot, y in enumerate(V):
            pts.append((f"旋转 {rot}", y))
            for j in range(m2):
                for eps in (eps_small, eps_big):
                    for sgn in (1, -1):
                        z = list(y)
                        z[j] += sgn * eps
                        pts.append((f"旋转 {rot} 坐标 {j} {sgn:+d}{eps}", tuple(z)))
        T = Fraction(W, m2)
        pts.append(("等坐标和紧点（全坐标 = W/m2）", tuple([T] * m2)))
        pts.append(("等坐标和差一点", tuple([T - eps_small] * m2)))
        pts.append(("末坐标 1 差一点", tuple([T] * (m2 - 1) + [Fraction(1) - eps_small])))
        n_agree = 0
        bad = []
        for lab, y in pts:
            a = RC.feasible(y, m2, d, W)[0]
            b = U.indep_feasible(y, m2, d, W)
            if a == b:
                n_agree += 1
            else:
                bad.append((lab, a, b))
        check(f"{label}：{len(pts)} 个探针判定一致", n_agree == len(pts), f"分歧 = {bad[:3]}")

        # 结构性核对：每个旋转处，坐标加 ε 恰在一个位置可行（指数 0 的坐标），减 ε 全不可行
        if v >= 1:
            plus_ok = []
            minus_ok = []
            for rot, y in enumerate(V):
                nplus = 0
                nminus = 0
                for j in range(m2):
                    zp = list(y)
                    zp[j] += eps_small
                    zm = list(y)
                    zm[j] -= eps_small
                    if RC.feasible(tuple(zp), m2, d, W)[0]:
                        nplus += 1
                    if RC.feasible(tuple(zm), m2, d, W)[0]:
                        nminus += 1
                plus_ok.append(nplus)
                minus_ok.append(nminus)
            check(f"{label}：每个旋转处「加 ε」可行位置数恒为 1（极小坐标）",
                  all(x == 1 for x in plus_ok), f"实测 {plus_ok}")
            check(f"{label}：每个旋转处「减 ε」可行位置数恒为 0", all(x == 0 for x in minus_ok),
                  f"实测 {minus_ok}")
        # 和紧点的活跃秩（应远小于 m2，说明它不是顶点）
        if T >= 1:
            pt = tuple([T] * m2)
            okP = RC.feasible(pt, m2, d, W)[0]
            rkU, nactU = U.active_rank_sympy(pt, m2, d, W)
            check(f"{label}：等坐标和紧点可行且活跃秩 < m2（非顶点）",
                  okP and rkU < m2, f"活跃秩/条数 = {rkU}/{nactU}")
        # 顶点证书集合（被审计实现 RJ.active_rank）：一般档 [(m2, m2)]；阈值档 [(m2, m2+1)]
        if v >= 1:
            certs = sorted({RJ.active_rank(y, m2, d, W) for y in V})
            want = [(m2, m2 + 1)] if v == 1 else [(m2, m2)]
            check(f"{label}：顶点证书集合 = {want}（v = 1 时为 (m2, m2+1)，"
                  f"否则 (m2, m2)；阈值档对应 r2_b_out.txt:97 的 E10 记录 [(5, 6)]）",
                  certs == want, f"实测 {certs}")

    # ---------------- [3] solve_exact 与 sympy 对拍 ----------------
    U.say("\n[3] solve_exact 与 sympy 精确解对拍（含不相容与欠定的人造例）")
    n_sys = 0
    n_rank_bad = 0
    n_type_bad = 0
    n_sol_bad = 0
    for m2 in (3, 4, 5, 6, 10):
        trials = 150 if m2 != 10 else 60
        det = RC.Det(20261027)
        for _ in range(trials):
            S = set()
            while len(S) < m2:
                S.add(det.below(2 * m2 + 1))
            S = sorted(S)
            cons = RC.constraint_list(m2, Fraction(126797, 80000), Fraction(2000))
            rows = [cons[i][0] for i in S]
            rhs = [cons[i][1] for i in S]
            sol_rc, rank_rc = RC.solve_exact(rows, rhs)
            sol_sy, rk, rk_aug = U.sympy_solve(rows, rhs, m2)
            n_sys += 1
            if rank_rc != rk:
                n_rank_bad += 1
            if sol_rc is None:
                if not (rk < m2 or rk_aug > rk):
                    n_type_bad += 1
            else:
                if not (rk == m2 and rk_aug == rk):
                    n_type_bad += 1
                else:
                    vec = [Fraction(t) for t in sol_rc]
                    if vec != sol_sy:
                        n_sol_bad += 1
    check(f"随机子系统对拍（{n_sys} 个：m2 = 3、4、5、6 各 150 与 m2 = 10 的 60）",
          n_rank_bad == 0 and n_type_bad == 0 and n_sol_bad == 0,
          f"秩不符 {n_rank_bad}；解的结构不符 {n_type_bad}；解值不符 {n_sol_bad}")
    art = [
        ("人造不相容 3×2", [[1, 0], [1, 0], [0, 1]], [1, 2, 0], 2, "inconsistent"),
        ("人造相容 3×2", [[1, 0], [0, 1], [1, 1]], [1, 1, 2], 2, "unique"),
        ("人造欠定 2×3", [[1, 0, 0], [0, 1, 0]], [1, 1], 3, "underdetermined"),
    ]
    for name, Araw, braw, m, kind in art:
        rows = [[Fraction(c) for c in row] for row in Araw]
        rhs = [Fraction(t) for t in braw]
        sol_rc, rank_rc = RC.solve_exact(rows, rhs)
        sol_sy, rk, rk_aug = U.sympy_solve(rows, rhs, m)
        if kind == "inconsistent":
            ok = sol_rc is None and rank_rc == rk == 2 and rk_aug == 3
        elif kind == "unique":
            ok = sol_rc is not None and [Fraction(t) for t in sol_rc] == sol_sy == [Fraction(1), Fraction(1)]
        else:
            ok = sol_rc is None and rank_rc == rk == 2 and rk < m
        check(f"{name}：solve_exact 与 sympy 结论一致（{kind}）", ok,
              f"RC = ({sol_rc}, 秩 {rank_rc})；sympy = ({sol_sy}, 秩 {rk}, 增广 {rk_aug})")

    # ---------------- [4] 枚举空间核对 ----------------
    U.say("\n[4] 枚举空间核对（组合数、互异性、覆盖性）")
    n_bad = 0
    for m2 in range(2, 16):
        total_loop = 1
        for i in range(m2):
            total_loop = total_loop * ((2 * m2 + 1) - i) // (i + 1)
        if total_loop != math.comb(2 * m2 + 1, m2):
            n_bad += 1
    check("枚举计数公式（脚本同款循环）与 math.comb 一致（m2 = 2 至 15）", n_bad == 0)
    n_bad = 0
    for m2 in range(2, 9):
        it = list(combinations(range(2 * m2 + 1), m2))
        ok = (len(it) == math.comb(2 * m2 + 1, m2) == len(set(it))
              and all(list(s) == sorted(s) and len(s) == m2 for s in it))
        cover = set()
        for s in it:
            cover.update(s)
        ok = ok and cover == set(range(2 * m2 + 1))
        if not ok:
            n_bad += 1
    check("itertools.combinations 输出：逐个子集满足递增、互异、总数正确、覆盖全部约束（m2 = 2 至 8）",
          n_bad == 0)

    # ---------------- [5] 小档独立枚举与冻结实现对拍 ----------------
    U.say("\n[5] 小档全枚举对拍（sympy 独立实现 vs r2_j.full_enumeration vs 解析旋转集）")
    cases_enum = [
        ("m2=2 δ_lo W=2000", 2, D_LO7, Fraction(2000)),
        ("m2=3 δ_lo W=2000", 3, D_LO7, Fraction(2000)),
        ("m2=4 δ_lo W=2000", 4, D_LO7, Fraction(2000)),
        ("m2=5 δ_lo W=2000", 5, D_LO7, Fraction(2000)),
        ("m2=6 δ_lo W=2000", 6, D_LO7, Fraction(2000)),
        ("阴性对照 m2=2 δ=3/2 W=3/2", 2, Fraction(3, 2), Fraction(3, 2)),
    ]
    for label, m2, d, W in cases_enum:
        t0 = time.time()
        mine, cnt, full_rank, hits = U.indep_enum_sympy(m2, d, W)
        theirs, total, dt = RJ.full_enumeration(m2, d, W, progress=False)
        analytic = {tuple(RC.vertex(m2, d, W, rot)) for rot in range(m2)}
        same_impl = set(mine) == set(theirs)
        v = RC.v_vertex(m2, d, W)
        if v >= 1:
            same_analytic = set(mine) == analytic
            extra = ""
        else:
            same_analytic = (set(mine) != analytic)
            extra = f"（v < 1：解析集不在 P 内，二者不等是预期；解析集 = {sorted(analytic)}）"
        check(f"{label}：计数一致（独立 cnt = {cnt}，冻结 total = {total}，"
              f"math.comb = {math.comb(2 * m2 + 1, m2)}）",
              cnt == total == math.comb(2 * m2 + 1, m2))
        check(f"{label}：两实现顶点集逐坐标相等", same_impl,
              f"顶点数 = {len(mine)}（独立）与 {len(theirs)}（冻结）")
        check(f"{label}：与解析旋转集的关系符合预期（v ≥ 1 相等；v < 1 不等）",
              same_analytic, extra)
        U.say(f"    明细：迭代子集 {cnt}，全秩子集 {full_rank}，命中（含重）{hits}，"
              f"独立用时 {time.time() - t0:.1f} s，冻结用时 {dt:.1f} s")
    neg, cnt, full_rank, hits = U.indep_enum_sympy(2, Fraction(3, 2), Fraction(3, 2))
    check("阴性对照顶点集恰为 {(1,1),(1,3/2),(3/2,1)}（与 route-1.md:319 一致）",
          set(neg) == {(Fraction(1), Fraction(1)), (Fraction(1), Fraction(3, 2)),
                       (Fraction(3, 2), Fraction(1))}, f"实测 = {sorted(neg)}")

    # ---------------- 小结 ----------------
    n_pass = sum(1 for _n, ok in CHECKS if ok)
    n_fail = len(CHECKS) - n_pass
    U.say("\n" + "=" * 78)
    U.say(f"审计小结：检查 {len(CHECKS)} 项，通过 {n_pass} 项，失败 {n_fail} 项；"
          f"总用时 {time.time() - t_start:.1f} s")
    U.say("=" * 78)
    if n_fail:
        for n, ok in CHECKS:
            if not ok:
                U.say(f"  FAIL 未过项：{n}")
        sys.exit(1)


if __name__ == "__main__":
    main()
