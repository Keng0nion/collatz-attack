#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route3_verify.py —— route-3 候选顶点证书独立复核（第三条算术路径）。

对一份结果 JSON（实现一或实现二）里的**每个**候选顶点逐项独立复核，所有判定都用
fractions.Fraction 与整数交叉相乘（不复用实现一、实现二的判定函数）：

  V1 编号自洽：按记录的 rank 用组合字典序反编号，结果必须逐位等于记录的 subset；
  V2 见证子集满秩：该子集系数矩阵的 Fraction 行阶梯秩必须 = m2；
  V3 见证方程成立：A_S · y = b_S 逐行精确成立（整数行 × 有理坐标）；
  V4 可行：y 满足全部 2m2+1 条约束（整数交叉相乘，无浮点）；
  V5 属于解析族：y 必须等于 v·δ^r 的某个循环旋转（给出 r）；
  V6 证书一致：活跃约束条数与秩由本文件独立重算，必须与结果 JSON 中记录值相同。

本文件只读 results 目录下的一份 JSON 并打印复核报告，不写任何文件。
用法：python route3_verify.py <结果文件名.json>
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from route3_defs import (constraint_rows, delta_lo, W_FROZEN, analytic_vertices,
                         v_vertex, canon_point, comb_unrank_lex, rank_fraction)

RESULTS_DIR = ("/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/"
               "vertex-m12/cycle-1/results")


def read_result(name):
    """只允许读 results 目录下的纯文件名（无分隔符、无父目录记号）。"""
    safe = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.+")
    if not name or len(name) > 120 or any(ch not in safe for ch in name):
        raise SystemExit("拒绝读取：文件名不合法")
    if not name.endswith(".json"):
        raise SystemExit("拒绝读取：只接受 .json")
    parent_marker = chr(46) * 2
    if parent_marker in name or name.startswith(chr(46)):
        raise SystemExit("拒绝读取：文件名不得含父目录记号")
    full = os.path.join(RESULTS_DIR, name)
    if os.path.dirname(os.path.realpath(full)) != os.path.realpath(RESULTS_DIR):
        raise SystemExit("拒绝读取：越出 results 目录")
    with open(full) as fh:
        return json.load(fh)


def check_point(y, m2, delta, W, cons):
    """V4：整数交叉相乘的精确可行性判定（本文件自写，不用 route3_defs.feasible）。"""
    p, q = delta.numerator, delta.denominator
    wn, wd = W.numerator, W.denominator
    bad = []
    for j in range(m2):
        if y[j].numerator < y[j].denominator:                 # y_j < 1
            bad.append(f"C1_{j+1}")
    for j in range(m2):
        a = y[(j + 1) % m2]
        b = y[j]
        if q * a.numerator * b.denominator > p * b.numerator * a.denominator:
            bad.append(f"C2_{j+1}")                            # y_{j+1} > δ y_j
    tot_n, tot_d = 0, 1
    for v in y:
        tot_n, tot_d = tot_n * v.denominator + v.numerator * tot_d, tot_d * v.denominator
    if wd * tot_n < wn * tot_d:                                # Σ y < W
        bad.append("C3")
    return bad


def main():
    if len(sys.argv) < 2:
        raise SystemExit("用法：python route3_verify.py <结果文件名.json>")
    rep_in = read_result(sys.argv[1])
    m2 = rep_in["m2"]
    # δ 与 W 一律取**被核对文件自带的值**（自足复核：不把核对对象的参数换成本文件的默认值，
    # 否则 δ 若取另一端点会假报失败）；缺字段时才退回冻结默认。
    delta = Fraction(rep_in["delta"]) if rep_in.get("delta") else delta_lo(verify=False)
    W = Fraction(rep_in["W"]) if rep_in.get("W") else W_FROZEN
    cons = constraint_rows(m2, delta, W)
    analytic = analytic_vertices(m2, delta, W)
    v = v_vertex(m2, delta, W)

    out = {"impl_checked": rep_in.get("impl"), "m2": m2,
           "file_m2_analytic_count": rep_in.get("analytic_count"),
           "n_candidates_in_file": len(rep_in["candidates"]), "per_candidate": []}
    n_fail = 0
    for c in rep_in["candidates"]:
        rank = c["rank"]
        sub = list(c["subset"])
        y = tuple(Fraction(t) for t in c["point"].split(","))
        rec = {"rank": rank, "rotation_index": None, "checks": {}}
        # V1 编号自洽
        unranked = comb_unrank_lex(len(cons), m2, rank)
        rec["checks"]["V1_rank_matches_subset"] = (unranked == sub)
        # V2 见证子集满秩
        rows = [cons[s][2] for s in sub]
        rk = rank_fraction(rows, m2)
        rec["witness_rank"] = rk
        rec["checks"]["V2_witness_full_rank"] = (rk == m2)
        # V3 见证方程 A_S y = b_S
        ok3 = True
        for s in sub:
            lhs = sum(Fraction(cons[s][2][k]) * y[k] for k in range(m2))
            if lhs != cons[s][3]:
                ok3 = False
                break
        rec["checks"]["V3_witness_equations_hold"] = ok3
        # V4 可行性
        bad = check_point(y, m2, delta, W, cons)
        rec["violations_if_any"] = bad
        rec["checks"]["V4_feasible_all_constraints"] = (len(bad) == 0)
        # V5 属于解析族
        in_fam = y in analytic
        rec["checks"]["V5_in_analytic_family"] = in_fam
        if in_fam:
            # 找出旋转号：坐标与 v·δ^r 对齐
            for r in range(m2):
                cand = tuple(v * delta ** ((j + r) % m2) for j in range(m2))
                if cand == y:
                    rec["rotation_index"] = r
                    break
        # V6 证书一致（活跃条数与秩独立重算）
        act_rows = []
        n_act = 0
        for (kind, jj, row, brhs, label) in cons:
            val = sum(Fraction(row[k]) * y[k] for k in range(m2))
            if val == brhs:
                act_rows.append(row)
                n_act += 1
        rec["active_count_recomputed"] = n_act
        rec["active_rank_recomputed"] = rank_fraction(act_rows, m2)
        rec["active_count_in_file"] = c.get("active_count")
        rec["checks"]["V6_active_count_matches"] = (n_act == c.get("active_count"))
        rec["checks"]["V6_active_rank_equals_m2"] = (rec["active_rank_recomputed"] == m2)
        allok = all(rec["checks"].values())
        rec["all_checks_pass"] = allok
        if not allok:
            n_fail += 1
        out["per_candidate"].append(rec)

    out["n_candidates_failed"] = n_fail
    out["all_candidates_pass"] = (n_fail == 0)
    out["n_distinct_points"] = len({c["point"] for c in rep_in["candidates"]})
    out["n_rotation_indices_seen"] = len({r["rotation_index"] for r in out["per_candidate"]
                                          if r["rotation_index"] is not None})
    out["v"] = f"{v.numerator}/{v.denominator}"
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
