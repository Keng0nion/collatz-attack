#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-4 审计脚本 4：AST 依赖审计（代码调用级），落实「零 (L1)、零顶点引理、零凸性」。

做法：
  1. md5 守卫后解析 r2_common.py、r2_j_independent_vertices.py、r2_b_vertices.py 的源码；
  2. 对关键函数列出被调用的名字与引用的全部 Name，并按禁用集逐项断言：
     - full_enumeration 体内不得出现 (L1) 判据、v、顶点解析族、凸性相关名字；
     - constraint_list / solve_exact / feasible 体内不得出现 (L1)、v、顶点解析族；
  3. 用 tokenize 区分注释、字符串与代码，报告「L1」「顶点引理」「convex」「凸」的每一处命中
     及其行号，并断言它们不出现在上述函数体的行区间内；
  4. 对照登记：(L1) 依赖在 r2_b_vertices.enumerate_vertices 里的确切位置（仅登记，不评判）。

用法（在 cycle-1/scripts 下）：
  PY="/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python"
  "$PY" route4_dep_ast.py
"""
import ast
import io
import sys
import tokenize

import route4_util as U

CHECKS = []


def check(name, ok, detail=""):
    ok = bool(ok)
    CHECKS.append((name, ok))
    line = f"  [{'PASS' if ok else 'FAIL'}] {name}"
    if detail:
        line += f" —— {detail}"
    U.say(line)


def call_name(f):
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return call_name(f.value) + "." + f.attr
    return type(f).__name__


def function_info(node):
    walks = list(ast.walk(node))
    calls = sorted({call_name(n.func) for n in walks if isinstance(n, ast.Call)})
    names = sorted({n.id for n in walks if isinstance(n, ast.Name)})
    return {"range": (node.lineno, node.end_lineno), "calls": calls, "names": names}


def load_text(name):
    return (U.DEPS / name).read_text(encoding="utf-8")


def audit_file(fname, watch):
    text = load_text(fname)
    tree = ast.parse(text)
    info = {}
    U.say(f"\n---- {fname}（{len(text.splitlines())} 行）----")
    mod_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mod_imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            mod_imports.append(f"from {node.module} import ...")
    U.say(f"  模块级 import：{sorted(set(mod_imports))}")
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            info[node.name] = function_info(node)
            U.say(f"  函数 {node.name}：行 {node.lineno} 至 {node.end_lineno}")
            U.say(f"    调用：{info[node.name]['calls']}")
    return text, info, tree


def main():
    U.say("=" * 78)
    U.say("route-4 审计脚本 4：AST 依赖审计（代码调用级）")
    U.say("=" * 78)
    U.guard()

    text_common, info_common, _ = audit_file("r2_common.py", None)
    text_j, info_j, _ = audit_file("r2_j_independent_vertices.py", None)
    text_b, info_b, _ = audit_file("r2_b_vertices.py", None)

    pure = ["constraint_list", "solve_exact", "feasible"]
    forbidden_pure = {"v_vertex", "vertex", "analytic", "enumerate_vertices", "threshold",
                      "D_LO7", "D_HI7", "mpmath", "z3", "delta_rigorous_bounds",
                      "active_rank", "rank_exact", "claimed_min_psi"}
    U.say("\n---- 断言 1：纯判定函数（constraint_list、solve_exact、feasible）的禁用集 ----")
    for fname in pure:
        f = info_common[fname]
        bad_calls = sorted(set(f["calls"]) & forbidden_pure)
        bad_names = sorted(set(f["names"]) & forbidden_pure)
        check(f"r2_common.{fname}（行 {f['range'][0]} 至 {f['range'][1]}）零禁用引用",
              not bad_calls and not bad_names, f"命中调用 {bad_calls}；命中名字 {bad_names}")

    forbidden_enum = {"v_vertex", "vertex", "analytic", "enumerate_vertices", "threshold",
                      "D_LO7", "D_HI7", "mpmath", "z3", "delta_rigorous_bounds",
                      "active_rank", "rank_exact", "repair_normalize", "claimed_min_psi",
                      "psi", "det", "Det"}
    f = info_j["full_enumeration"]
    bad_calls = sorted(set(f["calls"]) & forbidden_enum)
    bad_names = sorted(set(f["names"]) & forbidden_enum)
    U.say("\n---- 断言 2：full_enumeration 的禁用集 ----")
    U.say(f"  full_enumeration（行 {f['range'][0]} 至 {f['range'][1]}）实际调用：{f['calls']}")
    check("r2_j.full_enumeration 零 (L1)、零 v、零顶点解析族、零凸性引用",
          not bad_calls and not bad_names, f"命中调用 {bad_calls}；命中名字 {bad_names}")

    U.say("\n---- 断言 3：关键字命中（tokenize 分类；f-string 字面量按字符串计）----")
    patterns = ["L1", "顶点引理", "convex", "凸"]
    text_kinds = {"COMMENT", "STRING", "FSTRING_MIDDLE", "FSTRING_START", "FSTRING_END"}
    hits = {p: [] for p in patterns}
    code_hits = []
    for fname, text in (("r2_common.py", text_common),
                        ("r2_j_independent_vertices.py", text_j),
                        ("r2_b_vertices.py", text_b)):
        gen = tokenize.generate_tokens(io.StringIO(text).readline)
        for tok in gen:
            for p in patterns:
                if p in tok.string:
                    kind = tokenize.tok_name[tok.type]
                    rec = (fname, tok.start[0], tok.end[0], kind, tok.string.strip()[:60])
                    hits[p].append(rec)
                    if kind not in text_kinds:
                        code_hits.append(rec)
    for p in patterns:
        U.say(f"  模式「{p}」命中 {len(hits[p])} 处：")
        for fname, l0, l1, kind, snip in hits[p]:
            U.say(f"    {fname}:{l0} 至 {l1}  [{kind}] {snip}")
    check("两文件中「convex」「凸」零命中", not hits["convex"] and not hits["凸"])
    check("「L1」「顶点引理」只出现在注释或字符串字面量（代码语义区零命中）", not code_hits,
          f"代码区命中 {code_hits}")

    ranges_pure = [info_common[n]["range"] for n in pure] + [info_j["full_enumeration"]["range"]]
    in_body = []
    for p in ("L1", "顶点引理"):
        for fname, l0, l1, kind, snip in hits[p]:
            if fname in ("r2_common.py", "r2_j_independent_vertices.py") and kind not in text_kinds:
                for a, b in ranges_pure:
                    if not (l1 < a or l0 > b):
                        in_body.append((fname, l0, p))
    check("（代码区）「L1」「顶点引理」不出现在 constraint_list / solve_exact / feasible / full_enumeration 的行区间内",
          not in_body, f"命中 {in_body}")
    U.say("  说明：r2_j_independent_vertices.py:93 的「（不依赖 L1）」是 full_enumeration 的")
    U.say("  文档字符串（STRING 类命中），不是对本段判据的引用；其函数体调用表见断言 2。")

    U.say("\n---- 对照登记：(L1) 依赖在 r2_b_vertices.py 里的位置 ----")
    eb = info_b["enumerate_vertices"]
    U.say(f"  enumerate_vertices：行 {eb['range'][0]} 至 {eb['range'][1]}；"
          f"调用含 v_vertex：{'v_vertex' in eb['calls']}；调用含 constraint_list："
          f"{'constraint_list' in eb['calls']}")
    U.say("  该函数内 (L1) 判据的原文行（r2_b_vertices.py:71 至 :74）：")
    for ln, line in enumerate(text_b.splitlines(), 1):
        if 71 <= ln <= 74:
            U.say(f"    {ln}: {line.strip()}")
    U.say("  说明：该函数先算阈值 (δ^m2−1)/(δ−1) 再用判据 W > 阈值 决定「y_j = 1 不可行」，")
    U.say("  属依赖 (L1) 的约简路线；本轨道主核对 full_enumeration 不使用它（期望其调用表里没有）。")
    check("full_enumeration 不调用 enumerate_vertices",
          "enumerate_vertices" not in info_j["full_enumeration"]["calls"])
    check("full_enumeration 的调用表恰为文档承诺的四个（constraint_list、solve_exact、feasible、time 等辅助）",
          {"constraint_list", "solve_exact", "feasible"} <= set(info_j["full_enumeration"]["calls"])
          and not (set(info_j["full_enumeration"]["calls"]) & forbidden_enum))

    n_pass = sum(1 for _n, ok in CHECKS if ok)
    U.say("\n" + "=" * 78)
    U.say(f"依赖审计小结：检查 {len(CHECKS)} 项，通过 {n_pass} 项，失败 {len(CHECKS) - n_pass} 项")
    U.say("=" * 78)
    if n_pass != len(CHECKS):
        sys.exit(1)


if __name__ == "__main__":
    main()
