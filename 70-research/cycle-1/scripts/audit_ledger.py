#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-5「假设账本与依赖审计」主脚本。

六节：
  [1] 出处逐行核对：账本每条断言的引文是否真在它声称的原件/报告行上；
  [2] 假设账本 + 依赖图：环路检测、三条结构查询（无循环、三处补丁不依赖待证结论、
      不含印出版已被否证的那一步）；
  [3] 勘误文本的 δ 清单与「无 δ^ℓ 迭代」核对（与印出版页面对照）；
  [4] 锚点自检：δ、X0、c、K 上界、余量与当前 margin-table.txt 逐位比对；
  [5] 印出版那一步的两条缺陷（假不等式、方向反）的独立复核；
  [6] 勘误版聚合尾界在自举链七个参数点的核对（前提是否满足、顶点值、两条不等式、ε）。

运行：
  /Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python \
    "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts/audit_ledger.py"
"""

import os
import re
import sys
from fractions import Fraction

from mpmath import mp, mpf, log, power, nstr

REPO = "/Users/luna/Documents/math IA/collatz-attack"
T21 = os.path.join(REPO, "60-audits/hercher-t21")
CORR = "/tmp/corr.txt"
H5 = "/tmp/h5.txt"
SIDW = "/tmp/sidw144.txt"
TABLE = os.path.join(T21, "results", "margin-table.txt")

MD5_EXPECT = {
    CORR: "f23d5f969116cb1af6e9b981b4b3ba7a",   # 勘误 PDF
    H5: "3e2377bef0b1c0435dc455c9bbee43a1",     # 论文 PDF
}
PDF_OF = {CORR: "/tmp/corr.pdf", H5: "/tmp/h5.pdf"}


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def read_lines(path):
    """按 '\\n' 切分（与 grep -n / wc -l 的行号口径一致）。

    注意：不能用 str.splitlines()——pdftotext 会在页间插入换页符 \\x0c，
    splitlines() 会把它当成换行，从而把行号整体推后（本轮实测 h5.txt：
    splitlines 口径 1278 行，\\n 口径 1256 行，差 22 个换页符）。
    """
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    return text.split("\n")


def sec(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


# ---------------------------------------------------------------------------
# [1] 出处逐行核对
# ---------------------------------------------------------------------------

PROV = [
    # (编号, 文件, 行, 引文片段, 归类)
    ("P01", H5, 80, "Definition 4", "论文定义：X0 = 695·2^60"),
    ("P02", H5, 170, "Definition 6", "论文定义：局部极小值 n_i 与 k_i、T(n_i)"),
    ("P03", H5, 190, "Remark 7", "论文引理：T(n_i) < 3/n_i < 3/X0"),
    ("P04", H5, 207, "Lemma 8. Let n and k be positive integers", "论文引理：k_i <= x_i"),
    ("P05", H5, 509, "Theorem 16", "论文定理：δ < (K+L)/K < δ + ΣT/(3K log2)"),
    ("P06", H5, 598, "Corollary 17", "论文推论：ΣT 用 97/54·m/X0 的界"),
    ("P07", H5, 673, "also can be found in [12]", "论文引理：Lemma 20 出处"),
    ("P08", H5, 674, "Lemma 20", "论文引理：n_{i+1} < n_i^δ"),
    ("P09", H5, 695, "Theorem 21. Let K be the number of odd numbers", "论文定理：定理 21 陈述开头"),
    ("P10", H5, 702, "m2 ≤ m and", "论文前提：(δ^{m2}-1)/(δ-1)·c ≤ (m2/m)K"),
    ("P11", H5, 740, "There are m2 consecutive local minima", "论文鸽笼：窗口 k 和 ≥ (m2/m)K"),
    ("P12", H5, 745, "From Lemma 8 we know that ki ≤", "论文印出版迭代步的第一步"),
    ("P13", H5, 753, "Subsequently, in an analogous way we get", "论文印出版被否证的 δ^ℓ 迭代"),
    ("P14", H5, 790, "From the definition of v, we get", "论文护栏：2^v - 1 <= n_{m-m2+1}"),
    ("P15", H5, 799, "nm−m2 +1+ℓ", "论文争议步：n^{(δ^ℓ)} ≤ n^δ"),
    ("P16", H5, 801, "Using this together with Theorem 14 and", "论文争议步的结论句"),
    ("P17", H5, 850, "Theorem 23 (Main Theorem)", "论文主定理：m ≤ 91 无环"),
    ("P18", H5, 851, "we get m2 ≥ 47", "论文链的第一步：m2 ≥ 47"),
    ("P19", H5, 822, "Lemma 22", "论文引理：区间内最小分母"),
    ("P20", H5, 1227, "[11] J. Simons", "参考文献 [11]"),
    ("P21", H5, 1231, "[12] J. Simons", "参考文献 [12]（v1.44）"),
    ("P22", SIDW, 262, "For m ≥ 78 the possible nontrivial m-cycles satisfy", "SdW 定理 3(d) 分段"),
    ("P23", SIDW, 265, "1.1173", "SdW：78 ≤ m ≤ 90 段下界（实测行 265）"),
    ("P24", SIDW, 270, "if 91 ≤ m ≤ 515 619 then", "SdW：91 段开头（实测行 270）"),
    ("P24b", SIDW, 271, "1.4784", "SdW：91 ≤ m ≤ 515619 段上界系数（实测行 271）"),
    ("P25", CORR, 12, "The derivation of the inequalities", "勘误：承认推导有误"),
    ("P26", CORR, 15, "To show the statement", "勘误：要重证的命题"),
    ("P27", CORR, 23, "For a local minimum ni in the hypothetically existing Collatz cycle, define", "勘误：x_i 的定义"),
    ("P28", CORR, 27, "Then, by Lemma 8, we know that", "勘误：Lemma 8 承接"),
    ("P29", CORR, 28, "which implies xi+1", "勘误：x_{i+1} < δx_i"),
    ("P30", CORR, 29, "Using the same argument as on page 13", "勘误：窗口（鸽笼）"),
    ("P31", CORR, 31, "Without loss of generality, let the cycle be entered in such", "勘误：this sum 与其后 x 和断言"),
    ("P32", CORR, 32, "Then xm−m2 ≤ xm", "勘误：回绕比较 x_{m-m2} ≤ x_m"),
    ("P33", CORR, 33, "this implies xm−m2 +1", "勘误：得 x_{m-m2+1} < δx_m"),
    ("P34", CORR, 35, "By Remark 7, we have", "勘误：S 的定义"),
    ("P35", CORR, 43, "Since all xi are positive, the function S is convex", "勘误：顶点断言"),
    ("P36", CORR, 44, "value at a vertex of the polytope determined by the constraints", "勘误：约束清单"),
    ("P37", CORR, 45, "and xm−m2 +1", "勘误：约束清单含严格不等号"),
    ("P38", CORR, 46, "least m2 of these constraints must be active", "勘误：活跃约束计数"),
    ("P39", CORR, 47, "Suppose there is a value xi such that xi = 1", "勘误：x_i = 1 不可行"),
    ("P40", CORR, 52, "The last inequality follows from the defi", "勘误：引 m2 的定义"),
    ("P41", CORR, 54, "of the remaining m2 + 1 constraints must be active", "勘误：剩余 m2+1 条"),
    ("P42", CORR, 56, "would lead to the contradiction xm", "勘误：链全活跃会矛盾"),
    ("P43", CORR, 59, "Therefore, the sum condition must be active", "勘误：和约束必活跃"),
    ("P44", CORR, 63, "together with all but one of the equations", "勘误：把回绕写成等式"),
    ("P45", CORR, 64, "Consequently, S attains its maximum at a point whose coordinates are a", "勘误：顶点坐标"),
    ("P46", CORR, 65, "cyclic permutation of", "勘误：循环置换"),
    ("P47", CORR, 71, "= v,", "勘误：x_{m-m2+1} = v"),
    ("P48", CORR, 78, "≤ S(v, δv, . . . , δ m2 −1 v) ≤ S(v, δv, . . . , δv)", "勘误：收尾链"),
    ("P49", CORR, 83, "which is exactly what we wanted to prove.", "勘误：末句"),
    # 项目内文件（对项目是一手）
    ("P50", TABLE, 89, "7941964418702608664581", "现行表：m = 91 行"),
    ("P51", TABLE, 90, "0.226490482057595771625621", "现行表：m = 92 行"),
    ("P51b", TABLE, 112, "37.09935525747164492758953", "现行表：m = 91 的 25 位自检行"),
    ("P52", os.path.join(T21, "audit-report.md"), 137, "已被勘误版重推者本人撤回", "核查报告：旧句已撤回"),
    ("P53", os.path.join(T21, "audit-report.md"), 193, "不得再引", "核查报告：旧句不得再引"),
    ("P54", os.path.join(T21, "audit-report.md"), 211, "未证", "核查报告：把 Ψ 非降标为未证"),
    ("P55", os.path.join(T21, "rederivation-erratum.md"), 334, "q_min 关于 ε 非增", "重推报告：q_min 单调性（非增）"),
    ("P56", os.path.join(T21, "rederivation-erratum.md"), 423, "q_min 关于 ε 非减", "重推报告：q_min 单调性（非减，方向写反）"),
    ("P57", os.path.join(T21, "rederivation-erratum.md"), 336, "把单点探针", "重推报告：撤回旧句"),
    ("P58", os.path.join(T21, "rederivation-erratum.md"), 403, "旧句（原文照录）", "重推报告：照录旧句"),
]


def check_provenance():
    sec("[1] 出处逐行核对（引文是否真在所称行上）")
    ok = 0
    bad = []
    for (pid, path, line, snippet, cls) in PROV:
        lines = read_lines(path)
        n = len(lines)
        lo, hi = max(0, line - 4), min(n, line + 3)
        window = norm(" ".join(lines[lo:hi]))
        hit = norm(snippet) in window
        actual = None
        if hit:
            for idx in range(lo, hi):
                if norm(snippet) in norm(lines[idx]):
                    actual = idx + 1
                    break
        if hit:
            ok += 1
            print(f"  {pid}  OK    {os.path.basename(path)}:{line}（命中行 {actual}）  {cls}")
        else:
            bad.append(pid)
            print(f"  {pid}  FAIL  {os.path.basename(path)}:{line}  片段未在 ±4 行内找到：{snippet}")
    print(f"\n  合计：{ok}/{len(PROV)} 条命中。未命中：{bad if bad else '无'}")
    return bad


# ---------------------------------------------------------------------------
# [2] 假设账本与依赖图
# ---------------------------------------------------------------------------

LEDGER = {
    # 记号与反证框架
    "H1": ("反证：假设存在 m 圈（m ≤ 91），n_i 为局部极小值",
           "Theorem 23 陈述（h5.txt:850）", "反证假设", []),
    "H2": ("k_i、K、L、T(n_i) 的定义", "Definition 6（h5.txt:170）", "论文定义", ["H1"]),
    "H3": ("X0 := 695·2^60 是圈元素的严格下界（n_i > X0）",
           "Definition 4（h5.txt:80）；Main Theorem 用 X0 = 695·2^60", "论文定义", ["H1"]),
    "H4": ("δ := log3/log2 > 1", "Definition 15（h5.txt:506）", "论文定义", []),
    # 论文引理
    "L-REM7": ("T(n_i) < 3/n_i < 3/X0 对一切 i", "Remark 7（h5.txt:190）", "论文引理", ["H2", "H3"]),
    "L-LEM8": ("k_i ≤ x_i := log2(n_i+1)；特别地 x_i ≥ 1", "Lemma 8（h5.txt:207）", "论文引理", ["H2"]),
    "L-LEM20": ("n_{i+1} < n_i^δ（含回绕 i = m）；等价 x_{i+1} < δx_i",
                "Lemma 20（h5.txt:674 与 :693 的注）", "论文引理", ["H2", "H4"]),
    "L-PIGEON": ("存在 m2 个连续极小值，其 k 和 ≥ (m2/m)K",
                 "第 13 页鸽笼（h5.txt:740）", "论文引理", ["H2"]),
    "L-THM14": ("Σ_{i≤m1} T(n_i) < (97m1+73)/(54X0)", "Theorem 14（h5.txt:465）", "论文引理", ["L-REM7"]),
    "L-THM16": ("δ < (K+L)/K < δ + ΣT/(3K log2)", "Theorem 16（h5.txt:509）", "论文引理", ["H2"]),
    "L-CF22": ("区间内分数的最小分母 = γ 的分母", "Lemma 22（h5.txt:822）", "论文引理", ["H4"]),
    # 定理 21 的前提与版本
    "PREM": ("(δ^{m2}-1)/(δ-1)·c ≤ (m2/m)K，1 ≤ m2 ≤ m，c := log2((162/97)X0)",
             "Theorem 21 陈述（h5.txt:695 至 :702，本轮按 200 dpi 渲染图核对）",
             "论文前提（= 报告 (A7)）", ["H2", "H3", "H4"]),
    "DEF-V": ("v := (m2/m)K(δ-1)/(δ^{m2}-1)", "Theorem 21 陈述同处", "论文定义", ["PREM"]),
    # 印出版被否证的步骤与被判定有效的部分
    "PRINT-IT": ("n_{m-m2+1+ℓ} < n^{(δ^ℓ)} ≤ n^δ 及其推论 T < 3/(2^v-1)^δ（ℓ ≥ 2 时幂不等式方向反）",
                 "h5.txt:799 至 :801（印出版）", "错误步骤（已否证）", ["L-LEM20", "H4"]),
    "PRINT-GUARD": ("由 v 的定义得 2^v - 1 ≤ n_{m-m2+1}（只覆盖窗口首个元素）",
                    "h5.txt:790 至 :794（印出版）", "论文引理（有效）", ["PREM", "L-LEM8"]),
    # 三处补丁
    "P1-WINDOW": ("窗口按 Σx 最大选取：则 (i) Σx ≥ (m2/m)K；(ii) x_{m-m2} ≤ x_m；(iii) x_{m-m2+1} < δx_m",
                  "勘误 corr.txt:28 至 :34；读法由本轮显式化（引理 W）", "原文读法 + 本轮新增初等引理", ["L-PIGEON", "L-LEM8", "L-LEM20"]),
    "P2-VERTEX": ("闭化多面体 P̄ 上 S 取到最大值，且最大值在顶点；顶点坐标多重集 = {v, δv, …, δ^{m2-1}v}",
                  "勘误 corr.txt:43 至 :46 与 :64 至 :72 的断言；本轮给出完整初等证明（引理 V、引理 S）",
                  "原文断言 + 本轮新增初等引理", ["P1-WINDOW", "PREM", "DEF-V", "H4"]),
    "P3-CLOSURE": ("把 x_{m-m2+1} < δx_m 放宽为 ≤（闭化）：P ⊆ P̄，故 sup_P S ≤ sup_{P̄} S",
                   "勘误 corr.txt:45 与 :63 自相出入（< 与 =）；本轮显式化（引理 C）",
                   "原文读法 + 本轮新增初等引理", ["P1-WINDOW"]),
    "L-SYM": ("S 关于坐标对称；f(x) = 3/(2^x-1) 在 x > 0 上凸且严格递减",
              "本轮新增初等引理（二阶导 3·2^x(2^x+1)(ln2)^2/(2^x-1)^3 > 0）", "本轮新增初等引理", ["H4"]),
    "L-MONO2": ("(2^v-1)^δ < 2^{δv}-1 对一切 v > 0",
                "本轮新增初等引理（g(y) = y^δ - (y-1)^δ 在 y > 1 上递增，g(1) = 1 > 0）",
                "本轮新增初等引理", ["H4"]),
    # 结论与链
    "C1": ("T(n_{m-m2+1}) + Σ_{i=m-m2+2}^{m} T(n_i) < 3/(2^v-1) + 3(m2-1)/((2^v-1)^δ)",
           "勘误 corr.txt:15 至 :22 与 :73 至 :83（勘误版聚合尾界）",
           "勘误版结论（附条件）", ["L-REM7", "P1-WINDOW", "P2-VERTEX", "P3-CLOSURE", "L-SYM", "L-MONO2"]),
    "CHAIN": ("七步自举：K > K_lo ⟹ K ≥ Ψ(K_lo)；m = 91 的终值 7941964418702608664581",
              "h5.txt:850 至 :876 的链 + 项目脚本 rederive-erratum.py 的 bootstrap", "项目脚本实现 + 论文数值",
              ["C1", "L-THM16", "L-CF22", "PREM", "DEF-V"]),
    "U-BOUND": ("K 上界：78 ≤ m ≤ 90 用 1.3993·m·δ^m，m ≥ 91 用 1.4784·m·δ^m",
                "SdW v1.44 定理 3(d)（sidw144.txt:262 至 :275）", "论文引理（外部）", ["H2"]),
    "PSI": ("Ψ(K_lo) := q_min(ε_opt(K_lo))，ε_opt 取可行 m2 中最小 ε",
            "项目脚本 rederive-erratum.py:435 至 :445 与 :997 至 :1000；判据见 rederivation-erratum.md:333",
            "项目脚本实现", ["C1", "L-CF22", "PREM", "DEF-V"]),
    "M1-EPSDEC": ("固定 m2 时 ε(m2, ·) 关于 K 严格递减（v 随 K 增，两个尾巴项同时变小，1/K 变小）",
                  "本轮新增初等引理（引理 M1）", "本轮新增初等引理", ["C1", "DEF-V"]),
    "M2-FEAS": ("可行 m2 集合随 K 单调不减", "本轮新增初等引理（引理 M2）", "本轮新增初等引理", ["PREM"]),
    "M3-EPSOPT": ("ε_opt 非增（可行集变大 + 逐点变小）", "本轮新增初等引理（引理 M3）", "本轮新增初等引理",
                  ["M1-EPSDEC", "M2-FEAS"]),
    "M4-QMIN": ("q_min 关于 ε 非增（区间变大，最小分母只能变小）", "本轮新增初等引理（引理 M4）", "本轮新增初等引理",
                ["L-CF22"]),
    "M5-PSIMONO": ("Ψ 非降（两个非增映射的复合）", "本轮新增初等引理（引理 M5）", "本轮新增初等引理",
                   ["M3-EPSOPT", "M4-QMIN", "PSI"]),
    "FIX": ("Ψ(K*) = K* = 2.05632218873398596256e20（单点数值等式）",
            "本轮独立复算 + 重推报告 :335、:410", "数值核对（单点）", ["PSI"]),
    "LEGAL": ("合法起点受已知输入约束：K_lo ≤ L = 7.5311e11（SdW v1.44 的 91 段下界）",
              "sidw144.txt:265 与 :622；重推报告 :333", "论文引理（外部）", ["U-BOUND"]),
    "M92-NEW": ("对一切合法起点 K_lo ≤ L（更一般地 K_lo ≤ K*），链迭代值 ≤ K* < U(92)，故 m = 92 不排除",
                "本轮统一表述（引理 M5 + 单点 FIX + LEGAL）", "本轮统一表述", ["M5-PSIMONO", "FIX", "LEGAL", "CHAIN"]),
    "M92-OLD": ("旧句：即使虚构起点 K > 10^20，链也只走到 2.0563e20（单点探针冒充全称断言）",
                "audit-report.md:208/:225 的初版旧句（现行文件已撤，见 :137、:193；旧句照录于 rederivation-erratum.md:403）",
                "已撤回（错误）", ["PSI"]),
}

QUERIES = [
    ("无循环（依赖图是 DAG）", None),
    ("三处补丁都不依赖待证结论 C1", ("P1-WINDOW", "P2-VERTEX", "P3-CLOSURE")),
    ("C1 的依赖闭包不含印出版被否证的步骤 PRINT-IT", ("C1",)),
    ("M92-NEW 的依赖闭包不含旧句 M92-OLD 与 PRINT-IT", ("M92-NEW",)),
    ("PSI/CHAIN 的依赖闭包不含 PRINT-IT", ("PSI", "CHAIN")),
]


def closure(node, seen=None):
    if seen is None:
        seen = set()
    for d in LEDGER[node][3]:
        if d not in seen:
            seen.add(d)
            closure(d, seen)
    return seen


def check_graph():
    sec("[2] 假设账本 + 依赖图：环路与结构查询")
    nodes = sorted(LEDGER)
    print(f"  账本规模：{len(nodes)} 个节点")
    print("  " + "、".join(f"{k}" for k in nodes))
    # 环路检测（DFS 着色）
    color = {k: 0 for k in nodes}
    cyc = []

    def dfs(u, stack):
        color[u] = 1
        stack.append(u)
        for v in LEDGER[u][3]:
            if color[v] == 1:
                cyc.append(stack[stack.index(v):] + [v])
            elif color[v] == 0:
                dfs(v, stack)
        stack.pop()
        color[u] = 2

    for k in nodes:
        if color[k] == 0:
            dfs(k, [])
    print(f"  环路检测：{'发现环路 ' + str(cyc) if cyc else '无环路（DAG）'}")

    print("\n  结构查询：")
    for (label, tgt) in QUERIES:
        if tgt is None:
            continue
        bad = []
        for t in tgt:
            cl = closure(t)
            for forbidden in ("PRINT-IT",):
                if forbidden in cl:
                    bad.append(f"{t} 经 {forbidden}")
            if t.startswith(("P1", "P2", "P3")) and "C1" in cl:
                bad.append(f"{t} 依赖 C1")
            if t == "M92-NEW" and "M92-OLD" in cl:
                bad.append("M92-NEW 依赖 M92-OLD")
        print(f"    {label}：{'通过' if not bad else '不通过 -> ' + str(bad)}")

    print("\n  结论 C1 的依赖闭包（拓扑序，含每条的出处与归类）：")
    cl = closure("C1") | {"C1"}
    order = []
    seen = set()

    def topo(u):
        for d in LEDGER[u][3]:
            if d not in seen:
                topo(d)
        seen.add(u)
        order.append(u)

    for k in sorted(cl):
        if k not in seen:
            topo(k)
    for k in order:
        stmt, src, cls, deps = LEDGER[k]
        print(f"    {k:<12} [{cls}] {stmt}")
        print(f"    {'':<12} 出处：{src}")
    print("\n  M92-NEW 的依赖闭包：")
    cl2 = closure("M92-NEW") | {"M92-NEW"}
    print("    " + "、".join(sorted(cl2)))


# ---------------------------------------------------------------------------
# [3] 勘误文本的 δ 清单与无 δ^ℓ 迭代核对
# ---------------------------------------------------------------------------

def check_delta_inventory():
    sec("[3] 勘误文本的 δ 清单：是否残留印出版的 δ^ℓ 迭代形式")
    lines = read_lines(CORR)
    pat_iter = re.compile(r"\(\s*δ\s*ℓ\s*\)|δ\s*ℓ\s*\)")
    hits = [(i + 1, ln) for i, ln in enumerate(lines) if "δ" in ln]
    for (i, ln) in hits:
        s = norm(ln)
        kind = "迭代形式（δ^ℓ）" if pat_iter.search(ln) else "单步比值或 δ 的幂和"
        print(f"    corr.txt:{i:<3} [{kind}] {s[:96]}")
    n_iter_corr = sum(1 for (_, ln) in hits if pat_iter.search(ln))
    h5 = read_lines(H5)
    n_iter_h5 = sum(1 for ln in h5 if pat_iter.search(ln))
    print(f"\n  勘误文本中「(δ ℓ)」形式命中数 = {n_iter_corr}")
    print(f"  论文文本中「(δ ℓ)」形式命中数 = {n_iter_h5}"
          f"（出现在印出版争议步，行 "
          + "、".join(str(i + 1) for i, ln in enumerate(h5) if pat_iter.search(ln)) + "）")
    print("  说明：本节只做文本清点，判定「勘误未使用该形式」是阅读结论，不是计算结论。")


# ---------------------------------------------------------------------------
# [4] 锚点自检
# ---------------------------------------------------------------------------

def seq_of_table(table_lines):
    rows = {}
    for ln in table_lines:
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", ln)
        if m:
            rows[int(m.group(2))] = {
                "K_lo": m.group(3), "K_up": m.group(4), "margin": m.group(5),
                "verdict": m.group(6), "lineno": None,
            }
    return rows


def check_anchors():
    sec("[4] 锚点自检（先定死定义，再与已钉住的数字比对）")
    mp.dps = 60
    X0 = mpf(695) * power(2, 60)
    delta = log(3) / log(2)
    c = log(mpf(162) / 97 * X0) / log(2)
    print(f"  δ（40 位） = {nstr(delta, 40)}")
    print(f"  X0         = {nstr(X0, 25)}（整数 {695 * 2**60}）")
    print(f"  c          = {nstr(c, 25)}")
    K_up91 = mpf("1.4784") * 91 * power(delta, 91)
    K_up92 = mpf("1.4784") * 92 * power(delta, 92)
    print(f"  K_up(91)   = {nstr(K_up91, 30)}")
    print(f"  K_up(92)   = {nstr(K_up92, 30)}")
    K_lo91 = mpf(7941964418702608664581)
    margin91 = K_up91 / K_lo91
    print(f"  margin(91) = {nstr(margin91, 25)}")
    Kstar = mpf("2.05632218873398596256e20")
    print(f"  K*         = {nstr(Kstar, 25)}   K* < K_up(92) ? {Kstar < K_up92}")

    tlines = read_lines(TABLE)
    rows = seq_of_table(tlines)
    print(f"\n  现行表 {os.path.basename(TABLE)}：{len(tlines)} 行")
    r91, r92 = rows.get(91), rows.get(92)
    print(f"    表 m = 91 行：K_lo={r91['K_lo']}  K_up={r91['K_up']}  margin={r91['margin']}")
    print(f"    表 m = 92 行：K_lo={r92['K_lo']}  K_up={r92['K_up']}  margin={r92['margin']}")
    checks = [
        ("m = 91 下界逐位", r91["K_lo"], "7941964418702608664581"),
        ("m = 91 上界 20 位", nstr(K_up91, 21)[:21], r91["K_up"][:21]),
        ("m = 91 余量 25 位", nstr(margin91, 25), r91["margin"][:25]),
        ("m = 92 上界 20 位", nstr(K_up92, 21)[:21], r92["K_up"][:21]),
    ]
    for (label, a, b) in checks:
        print(f"    {label}: 独立值 {a} vs 表值 {b} -> {'一致' if a == b else '不一致'}")
    print(f"    钉住值 25 位余量 37.09935525747164492758953 与表值一致 ? "
          f"{nstr(margin91, 25) == '37.09935525747164492758953'}")
    print("  注：本轮实测现行表 md5 与 materials.md 记录的旧版不同（旧版 112 行），"
          "行号口径随之改变，见 route-5.md 的出处漂移清单。")


# ---------------------------------------------------------------------------
# [5] 印出版那一步的两条缺陷
# ---------------------------------------------------------------------------

def check_printed_defects():
    sec("[5] 印出版争议步的两条缺陷（独立复核）")
    mp.dps = 50
    delta = log(3) / log(2)
    print(f"  δ² = {nstr(delta ** 2, 25)}  > δ ? {delta ** 2 > delta}")
    print("  幂不等式方向：对 n > 1 与 ℓ ≥ 2 有 δ^ℓ > δ，故 n^{δ^ℓ} > n^δ（与印出的 ≤ 相反）")
    for (n, ell) in [(2, 2), (3, 2), (10, 3), (mpf(10) ** 30 + 1, 2)]:
        lhs = power(n, power(delta, ell))
        rhs = power(n, delta)
        print(f"    n = {nstr(n, 12):>18}  ℓ = {ell}：n^(δ^ℓ) = {nstr(lhs, 12):>18}"
              f"   n^δ = {nstr(rhs, 12):>18}   n^(δ^ℓ) > n^δ ? {lhs > rhs}")
    print("\n  推理方向：f(x) = 3/x 严格递减，故「对晚窗口元素只有上界 n < U」只给出 T 的下界 3/U。")
    U = mpf("5.7049502556188977072e22")
    print(f"    例：U = 2^v - 1 = {nstr(U, 20)}，3/U = {nstr(3 / U, 10)}，"
          f"而印出的断言是 3/(2^v-1)^δ = {nstr(3 / power(U, delta), 10)}（更小）")
    print(f"    T(n) < 3/n 在 n 更小时更大：n = 10^30+1 处 3/n = {nstr(3 / (mpf(10) ** 30 + 1), 10)}"
          f" > 3/U ? {3 / (mpf(10) ** 30 + 1) > 3 / U}")


# ---------------------------------------------------------------------------
# [6] 勘误版尾界在自举链七个参数点的核对
# ---------------------------------------------------------------------------

def log2_S(xs):
    """log2(Σ 3/(2^{x_i}-1))，对数尺度求和（与项目脚本无关的独立实现）。"""
    l3 = log(mpf(3)) / log(mpf(2))
    lts = []
    for x in xs:
        corr = log(mpf(1) - power(2, -x)) / log(mpf(2)) if x < 1000 else mpf(0)
        lts.append(l3 - x + corr)
    M = max(lts)
    acc = mpf(0)
    for lt in lts:
        d = lt - M
        if d < mpf(10) ** (-50):
            continue
        acc += power(2, d)
    return M + log(mpf(acc)) / log(mpf(2))


def f_tail(x):
    return 3 / (power(2, x) - 1)


CHAIN_PARAMS = [  # (m2, K_lo, 论文该步印出的 eps)
    (47, "7e11", "6.9e-32"),
    (67, "5.267319278509397e15", "5.1e-36"),
    (77, "3.97e17", "4.1e-38"),
    (82, "4.640282259296926456e18", "2.3e-39"),
    (86, "2.74e19", "2.3e-40"),
    (88, "7.76e19", "5.3e-41"),
    (91, "2.05632218873398596256e20", "1.11e-43"),
]


def check_chain_params():
    sec("[6] 勘误版聚合尾界在链上七个参数点的核对（m = 91）")
    mp.dps = 60
    m = 91
    X0 = mpf(695) * power(2, 60)
    delta = log(3) / log(2)
    c = log(mpf(162) / 97 * X0) / log(2)
    print("  m2   K_lo            前提?   m2 是最大可行?   v              顶点值 log2"
          "        收尾不等式?   ε（本轮）     论文印 ε")
    for (m2, Ks, eps_paper) in CHAIN_PARAMS:
        K = mpf(Ks)
        lhs = (power(delta, m2) - 1) / (delta - 1) * c
        rhs = (mpf(m2) / m) * K
        prem = lhs <= rhs
        lhs2 = (power(delta, m2 + 1) - 1) / (delta - 1) * c
        rhs2 = (mpf(m2 + 1) / m) * K
        is_max = prem and not (lhs2 <= rhs2)
        v = (mpf(m2) / m) * K * (delta - 1) / (power(delta, m2) - 1)
        xs = [power(delta, j) * v for j in range(m2)]
        lgv = log2_S(xs)
        bound_loose = f_tail(v) + (m2 - 1) * f_tail(delta * v)
        bound_final = f_tail(v) + 3 * (m2 - 1) / power(power(2, v) - 1, delta)
        ok_final = lgv <= log(bound_final) / log(mpf(2))
        A = (97 * (m - m2) + 73) / (54 * X0) if m2 < m else mpf(0)
        eps = (A + f_tail(v) + 3 * (m2 - 1) / power(power(2, v) - 1, delta)) / (3 * K * log(mpf(2)))
        print(f"  {m2:>3}  {Ks:>16}  {str(prem):>5}   {str(is_max):>13}   {nstr(v, 12):>14}"
              f"   {nstr(lgv, 12):>16}   {str(ok_final):>10}   {nstr(eps, 8):>12}  {eps_paper}")
    print("\n  列含义：前提 = (δ^{m2}-1)/(δ-1)·c ≤ (m2/m)K（定理 21 陈述的前提 / 报告 (A7)）；")
    print("  「v」= (m2/m)K(δ-1)/(δ^{m2}-1)；「顶点值 log2」= log2 Σ_j 3/(2^{δ^j v}-1)；")
    print("  「收尾不等式」= 顶点值 ≤ 3/(2^v-1) + 3(m2-1)/((2^v-1)^δ)。")


def main():
    bad = check_provenance()
    check_graph()
    check_delta_inventory()
    check_anchors()
    check_printed_defects()
    check_chain_params()
    sec("汇总")
    print(f"  [1] 出处核对未命中条数 = {len(bad)}")
    print("  本脚本不宣称任何全称命题；[6] 是七点有限核对，属证据级。")


if __name__ == "__main__":
    main()
