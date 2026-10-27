#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-4 审计脚本 2：用定义（中点）做极点判据，与活跃秩判据逐点对拍。

判据 A（定义，§3 的 Step 0）：y ∈ P 非极点 ⟺ 存在 d ≠ 0 使 y+d ∈ P 且 y−d ∈ P。
判据 B（审计对象的秩判据）：y ∈ P 是极点 ⟺ 活跃约束法向量秩 = m2。

对每个测试点向 z3（实数线性算术）问：
  ∃ d：d ≠ 0 ∧ (y+d ∈ P) ∧ (y−d ∈ P)？
sat 即判据 A 说「非极点」（并给模型 d 作精确见证，用独立转写逐条复核）；
unsat 即判据 A 说「极点」（另配 sympy 零核证书：活跃秩 = m2）。
两类证书都落成可 grep 的 PASS/FAIL 行。

用法（在 cycle-1/scripts 下）：
  PY="/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python"
  "$PY" route4_z3_extremality.py
"""
import sys
import time
from fractions import Fraction

import z3

import route4_util as U

RC, RJ = U.load()
D_LO7 = RC.delta_rigorous_bounds(10 ** 7)[0]

CHECKS = []


def check(name, ok, detail=""):
    ok = bool(ok)
    CHECKS.append((name, ok))
    line = f"  [{'PASS' if ok else 'FAIL'}] {name}"
    if detail:
        line += f" —— {detail}"
    U.say(line)


def rat(fr):
    return z3.RealVal(f"{fr.numerator}/{fr.denominator}")


def perturb_test(y, m2, d, W):
    """问 z3：∃d ≠ 0 使 y±d ∈ P。返回 (verdict, dvec or None, note)。"""
    cons = U.indep_constraints(m2, d, W)
    D = [z3.Real(f"d_{j}") for j in range(m2)]
    s = z3.Solver()
    s.set("timeout", 60000)
    for a, b, sense in cons:
        const = sum(a[j] * Fraction(y[j]) for j in range(m2))
        lin = rat(a[0]) * D[0]
        for j in range(1, m2):
            if a[j] != 0:
                lin = lin + rat(a[j]) * D[j]
        plus = rat(const) + lin
        minus = rat(const) - lin
        if sense == "ge":
            s.add(plus >= rat(b), minus >= rat(b))
        else:
            s.add(plus <= rat(b), minus <= rat(b))
    s.add(z3.Or([D[j] != 0 for j in range(m2)]))
    r = s.check()
    if r == z3.unsat:
        return "unsat", None, ""
    if r == z3.sat:
        md = s.model()
        dvec = []
        for j in range(m2):
            val = z3.simplify(md.eval(D[j], model_completion=True))
            if not z3.is_rational_value(val):
                return "sat", None, f"模型非有理数：{val.sexpr()[:60]}"
            fr = val.as_fraction()
            dvec.append(Fraction(fr.numerator, fr.denominator))
        return "sat", dvec, ""
    return str(r), None, ""


def witness_ok(y, dvec, m2, d, W):
    """sat 见证的独立复核：d ≠ 0，且 y±d 过独立转写的全部 2m2+1 条约束。"""
    if dvec is None or all(t == 0 for t in dvec):
        return False
    yp = [y[j] + dvec[j] for j in range(m2)]
    ym = [y[j] - dvec[j] for j in range(m2)]
    return U.indep_feasible(yp, m2, d, W) and U.indep_feasible(ym, m2, d, W)


def build_points(m2, d, W):
    """返回 (点列表, 备注列表)。每点为 (family, 标签, 坐标, 期望)。"""
    pts = []
    notes = []
    v = Fraction(W) * (d - 1) / (d ** m2 - 1)
    if v >= 1:
        Vs = [tuple(RC.vertex(m2, d, W, rot)) for rot in range(m2)]
        src = "旋转（解析顶点）"
    else:
        en, _cnt, _fr, _h = U.indep_enum_sympy(m2, d, W)
        Vs = sorted(en)
        src = "v < 1，改用独立枚举的顶点集"
        pred = [tuple(RC.vertex(m2, d, W, rot)) for rot in range(m2)]
        n_pred_out = sum(1 for y in pred if not U.indep_feasible(y, m2, d, W))
        notes.append(f"{src}；解析预测族中不在 P 内的点数 = {n_pred_out}")
    for i, y in enumerate(Vs):
        assert U.indep_feasible(y, m2, d, W), ("A 点不可行", y)
        pts.append(("A", f"顶点 {i}", y, "unsat"))
    for i in range(len(Vs)):
        for j in range(i + 1, len(Vs)):
            mid = tuple((Vs[i][k] + Vs[j][k]) / 2 for k in range(m2))
            if U.indep_feasible(mid, m2, d, W):
                pts.append(("B", f"两点中点 ({i},{j})", mid, "sat"))
            else:
                notes.append(f"中点 ({i},{j}) 不在 P 内，跳过")
    T = Fraction(W, m2)
    if T >= 1:
        pt = tuple([T] * m2)
        assert U.indep_feasible(pt, m2, d, W)
        pts.append(("C", "等坐标和紧点", pt, "sat"))
    t = 2 * Fraction(W)
    yD = [d ** j * t for j in range(m2 - 1)] + [d ** (m2 - 1) * t / 2]
    if U.indep_feasible(yD, m2, d, W):
        pts.append(("D", "单链活跃点", tuple(yD), "sat"))
    else:
        notes.append("D 点不在 P 内，跳过")
    return pts, notes


def main():
    t_start = time.time()
    U.say("=" * 78)
    U.say("route-4 审计脚本 2：定义（中点）判据 vs 活跃秩判据（z3 LRA 逐点对拍）")
    U.say("=" * 78)

    cases = [
        ("阴性对照 m2=2 δ=3/2 W=3/2", 2, Fraction(3, 2), Fraction(3, 2)),
        ("m2=2 δ_lo W=2000", 2, D_LO7, Fraction(2000)),
        ("m2=3 δ_lo W=2000", 3, D_LO7, Fraction(2000)),
        ("m2=4 δ_lo W=2000", 4, D_LO7, Fraction(2000)),
        ("m2=10 δ_lo W=2000", 10, D_LO7, Fraction(2000)),
    ]
    tot_pts = tot_unsat = tot_sat = tot_unknown = 0
    tot_cert_fail = 0
    tot_expect_mismatch = 0
    for label, m2, d, W in cases:
        U.say(f"\n[{label}]")
        pts, notes = build_points(m2, d, W)
        for nline in notes:
            U.say(f"    备注：{nline}")
        n_unsat = n_sat = n_unknown = 0
        n_cert_fail = 0
        n_mismatch = 0
        for fam, tag, y, expect in pts:
            verdict, dvec, note = perturb_test(y, m2, d, W)
            rk, nact = U.active_rank_sympy(y, m2, d, W)
            if verdict == "unsat":
                n_unsat += 1
                cert = (rk == m2)
                cert_txt = f"零核证书（活跃秩 = m2 = {m2}）：{'PASS' if cert else 'FAIL'}"
            elif verdict == "sat":
                n_sat += 1
                cert = witness_ok(y, dvec, m2, d, W) and (rk < m2)
                cert_txt = f"见证证书（d ≠ 0 且 y±d ∈ P，活跃秩 {rk} < m2）：{'PASS' if cert else 'FAIL'}"
                if note:
                    cert_txt += f"；{note}"
            else:
                n_unknown += 1
                cert = False
                cert_txt = f"判定异常：{verdict}；{note}"
            if not cert:
                n_cert_fail += 1
                tot_cert_fail += 1
            if not ((verdict == "unsat") == (expect == "unsat")):
                n_mismatch += 1
                tot_expect_mismatch += 1
            U.say(f"    [{fam}] {tag}：LRA 判定 = {verdict}（期望 {expect}）；"
                  f"活跃秩/条数 = {rk}/{nact}；{cert_txt}")
        U.say(f"    小组汇总：点数 {len(pts)}，unsat {n_unsat}，sat {n_sat}，异常 {n_unknown}，"
              f"证书失败 {n_cert_fail}，与期望不符 {n_mismatch}")
        tot_pts += len(pts)
        tot_unsat += n_unsat
        tot_sat += n_sat
        tot_unknown += n_unknown

    U.say("\n" + "=" * 78)
    check(f"逐点对拍：{tot_pts} 个点，unsat {tot_unsat}（极点），sat {tot_sat}（非极点）",
          tot_unknown == 0, f"异常 {tot_unknown}")
    check("全部点：证书（unsat 零核 / sat 见证）无失败", tot_cert_fail == 0,
          f"失败 {tot_cert_fail}")
    check("全部点：判定与期望无不符，且『活跃秩 = m2』与『LRA unsat』两个判据零分歧",
          tot_expect_mismatch == 0, f"不符 {tot_expect_mismatch}")
    U.say(f"总用时 {time.time() - t_start:.1f} s")
    U.say("=" * 78)
    if any(not ok for _n, ok in CHECKS):
        sys.exit(1)


if __name__ == "__main__":
    main()
