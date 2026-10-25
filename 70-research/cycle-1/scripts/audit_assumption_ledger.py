#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""假设账本与依赖审计（第 1 轮路线 5）。

纪律：先定义后计算。本文件按顺序做四件事：
  1. 钉死记号（NOTATION），全部按一手原件；
  2. 写出假设账本（LEDGER）：每条含 id、一句话陈述、出处、类别、依赖；
  3. 结构检查：无环性、印出版回退、目标自指、版本冲突、缺口闭合状态、已撤回断言隔离；
  4. 锚点自检：c、delta、K_up(91)、余量 与项目已钉住的数字比对。

本文件不做数学证明的机器验证（那是 verify_elementary_steps.py 的职责），
只检查账本自身的结构性质。运行：
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
     "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts/audit_assumption_ledger.py"
"""
from __future__ import annotations

import sys
from collections import defaultdict

# ------------------------------------------------------------------
# 一、记号（先定义；全部按一手原件，行号以本次副本为准）
# ------------------------------------------------------------------
NOTATION = {
    "X0": "X0 = 695*2^60，Definition 4（h5.txt:80-83）：已知所有 n <= X0 的轨迹归 1",
    "delta": "delta = log(3)/log(2) > 1，Definition 15（h5.txt:505-506，渲染页 9）",
    "m": "m 圈上局部极小值的个数；n_1..n_m 按出现顺序，n_{m+1} := n_1（Definition 6，h5.txt:170-174）",
    "k_i": "n_i 之后连续 o 步的准确条数（k_i >= 1），h5.txt:175-177",
    "K": "圈上奇数的个数，K = sum_i k_i；L 为偶数个数（h5.txt:695-696）",
    "T": "T(n_i) := sum_{t=0}^{k_i-1} 1/C^t(n_i)（h5.txt:182-188）",
    "x_i": "x_i := log(n_i+1)/log 2，故 n_i = 2^{x_i} - 1（corr.txt:23-26，渲染页 1）",
    "S": "S(x_{m-m2+1},...,x_m) := sum_i 3/(2^{x_i} - 1)（corr.txt:35-40）",
    "m2": "整数 1 <= m2 <= m，满足定理 21 陈述里的存在性条件（渲染页 13）",
    "c": "c := log((162/97) X0)/log 2 = log2((162/97) X0)",
    "W": "W := (m2/m) K",
    "v": "v := (m2/m) K (delta-1)/(delta^{m2} - 1) = W (delta-1)/(delta^{m2} - 1)（渲染页 13）",
}

# ------------------------------------------------------------------
# 二、假设账本
# kind 取值：
#   论文定义 / 定理假设 / 论文引理 / 论文论证 / 原文读法 / 原文断言待补
#   表述修正 / 本轮新增 / 标准引理 / 目标命题 / 印出版已否证 / 已撤回断言
# 每条 deps 列出它用到的前提（会计审计的边）；gaps 为空表示无缺口。
# ------------------------------------------------------------------
LEDGER = [
    dict(id="N.def.X0", kind="论文定义", deps=[],
         stmt="X0 = 695*2^60；X0 是已知「所有 n <= X0 归 1」的最大值",
         src="h5.txt:80-83（本次亲读）+ 渲染页 12 佐证"),
    dict(id="N.def.delta", kind="论文定义", deps=[],
         stmt="delta = log(3)/log(2) > 1",
         src="h5.txt:505-506（抽取把分式压平为 log(3) 与 log(2) 两行）"),
    dict(id="N.def.x", kind="论文定义", deps=[],
         stmt="x_i := log(n_i+1)/log 2，故 n_i = 2^{x_i} - 1",
         src="corr.txt:23-26；勘误新增"),
    dict(id="N.def.S", kind="论文定义", deps=[],
         stmt="S := sum_{i=m-m2+1}^{m} 3/(2^{x_i} - 1)",
         src="corr.txt:35-40"),
    dict(id="N.def.W", kind="论文定义", deps=[],
         stmt="W := (m2/m) K",
         src="定理 21 陈述与 corr.txt:31（sum x >= (m2/m)K）"),
    dict(id="N.def.v", kind="论文定义", deps=["N.def.W"],
         stmt="v = W (delta-1)/(delta^{m2}-1)",
         src="渲染页 13（定理 21 陈述页，逐字核对）"),

    dict(id="A0.cycle", kind="定理假设", deps=[],
         stmt="存在一个非平凡 m 圈（反证法的假设）",
         src="定理 21 与定理 23 的设定（h5.txt:695, :850）"),
    dict(id="A1.elem_gt_X0", kind="论文引理", deps=["N.def.X0", "A0.cycle"],
         stmt="圈上每个元素 > X0（否则该元素 <= X0 归 1，与非平凡矛盾）",
         src="Definition 4 的用法；Remark 7 证明末句 h5.txt:206「The last inequality follows from n_i > X0」"),
    dict(id="A3.k_le_x", kind="论文引理", deps=["N.def.x"],
         stmt="1 <= k_i <= x_i",
         src="Lemma 8（h5.txt:207-208）n ≡ -1 mod 2^k 故 n >= 2^k - 1"),
    dict(id="A4.n_delta", kind="论文引理", deps=["A1.elem_gt_X0", "N.def.delta"],
         stmt="n_{i+1} < n_i^delta，且对回绕 i = m 亦成立",
         src="Lemma 20（h5.txt:674-675）+ 回绕注（h5.txt:693）；其证明末句用 n_i > X0 > 3（渲染页 12 逐字）"),
    dict(id="A5.x_chain", kind="论文引理", deps=["A4.n_delta"],
         stmt="x_{i+1} < delta x_i",
         src="由 n_{i+1}+1 < n_i^delta + 1 < (n_i+1)^delta 展开（h5.txt:747-749 逐字）；corr.txt:27-28"),
    dict(id="A6.window_k", kind="论文论证", deps=["A0.cycle"],
         stmt="存在 m2 个连续局部极小值，其后紧跟的 o 步总数 >= (m2/m) K",
         src="论文第 13 页鸽笼论证（h5.txt:740-744 逐字；materials.md 同处逐字）。此步未被勘误否证"),
    dict(id="A7.window_x", kind="原文读法", deps=["A3.k_le_x", "A6.window_k"],
         stmt="把窗口取成使 sum x 最大的那一组（等价地：取其循环移位使 sum x 最大）",
         src="corr.txt:31-32 的 w.l.o.g. 句；审计判据：按 sum k 读时回绕约束 A8 的推导不成立"),
    dict(id="A8.wrap", kind="论文引理", deps=["A5.x_chain", "A7.window_x"],
         stmt="x_{m-m2+1} < delta x_{m-m2} <= delta x_m",
         src="corr.txt:32-34 逐字（严格号）"),
    dict(id="A9.sum", kind="论文引理", deps=["A7.window_x", "A3.k_le_x"],
         stmt="x_{m-m2+1} + ... + x_m >= (m2/m) K",
         src="corr.txt:29-31 逐字（sum x >= sum k >= (m2/m)K）"),
    dict(id="A10.T_lt_3n", kind="论文引理", deps=["A1.elem_gt_X0", "N.def.x"],
         stmt="T(n_i) < 3/n_i = 3/(2^{x_i} - 1)",
         src="Remark 7（h5.txt:190 逐字），其证明末句用 n_i > X0（h5.txt:206）"),
    dict(id="A11.S_convex", kind="本轮新增", deps=[],
         stmt="f(t) = 3/(2^t - 1) 在 t > 0 上严格凸，故 S 凸",
         src="原文只写一句「Since all x_i are positive, the function S is convex」（corr.txt:43）；本轮以 sympy 符号核验 f'' > 0，见 verify_elementary_steps.py"),
    dict(id="A12.x_ge_1", kind="论文引理", deps=["A3.k_le_x"],
         stmt="x_i >= 1",
         src="由 1 <= k_i <= x_i（corr.txt:44 的约束 x_i >= 1）"),
    dict(id="A14.H21", kind="定理假设", deps=["N.def.X0"],
         stmt="(delta^{m2}-1)/(delta-1) * c <= (m2/m) K 且 m2 <= m，其中 c = log((162/97)X0)/log 2",
         src="定理 21 陈述（渲染页 13 逐字，本次亲读）"),
    dict(id="A14b.c_gt_1", kind="本轮新增", deps=["A14.H21"],
         stmt="c = log2((162/97) X0) = 70.180806328308366825 > 1，故 (delta^{m2}-1)/(delta-1) < W 且 v >= c > 1",
         src="本轮锚点自检（数值部分），与 materials.md:345 钉住的 c 逐位一致"),
    dict(id="C1.closure", kind="表述修正", deps=["A8.wrap"],
         stmt="把 x_{m-m2+1} < delta x_m 读成 <= 并取闭包：P_open 含于 Pbar",
         src="审计结论：只用 S 的上界，P_open 含于 Pbar 故 sup_{P_open} S <= max_{Pbar} S，闭化无损"),
    dict(id="C2.attain", kind="本轮新增", deps=["A12.x_ge_1", "C1.closure", "N.def.S"],
         stmt="max_{Pbar} S 存在（Pbar 非空，且任一满足 S >= M/2 的点坐标一致有上界）",
         src="本轮给出的初等论证：某坐标经 S >= M/2 有上界，再由闭化的循环链 x_{i+1} <= delta x_i 得全体坐标 <= delta^{m2-1} B"),
    dict(id="C3.polytope", kind="标准引理", deps=[],
         stmt="有界多面体是其顶点集之凸包；凸函数在凸包上的值不超过顶点值中的最大者",
         src="标准引理（Minkowski 表示的有界多面体特例）；本轮给出维数递降证明纲要"),
    dict(id="C4.no_xi1", kind="论文引理", deps=["A9.sum", "A14.H21", "A14b.c_gt_1", "A12.x_ge_1", "C1.closure"],
         stmt="可行点没有坐标等于 1：若 x_i = 1 则 sum x <= (delta^{m2}-1)/(delta-1) < W",
         src="corr.txt:47-53 逐字；末句「The last inequality follows from the definition of m2 in the statement of Theorem 21」"),
    dict(id="C5.count", kind="论文引理", deps=["C1.closure", "C3.polytope", "C4.no_xi1", "A9.sum", "A12.x_ge_1"],
         stmt="顶点处至少 m2 条约束活跃；链与回绕全活跃会给出 x_m = delta^{m2} x_m；故和约束活跃，另 m2-1 条为链/回绕等式，顶点坐标为 v 的循环几何序列",
         src="corr.txt:54-72 逐字"),
    dict(id="A15.tail", kind="本轮新增", deps=[],
         stmt="(u-1)^delta < u^delta - 1（u > 1, delta > 1），故 3/(2^{delta v}-1) < 3/(2^v-1)^delta",
         src="原文该步未写；本轮以 sympy 符号核验，见 verify_elementary_steps.py"),
    dict(id="A16.mono", kind="论文引理", deps=["N.def.S", "N.def.v", "N.def.delta"],
         stmt="S(v, delta v, ..., delta^{m2-1} v) <= S(v, delta v, ..., delta v)",
         src="corr.txt:78 逐字；由 f 递减与 delta^j v >= delta v"),

    dict(id="TARGET.tail", kind="目标命题", deps=["A10.T_lt_3n", "C2.attain", "C3.polytope", "C5.count", "A15.tail", "A16.mono"],
         stmt="T(n_{m-m2+1}) + sum_{i=m-m2+2}^{m} T(n_i) < 3/(2^v - 1) + 3(m2-1)/((2^v-1)^delta)",
         src="corr.txt:15-22 逐字（勘误自称要重证的命题，与定理 21 陈述的被用形式一致）"),

    dict(id="G2.decompose", kind="表述修正", deps=["C1.closure", "C2.attain", "C3.polytope"],
         stmt="缺口 2（顶点取到性）分解为闭化、取到性、多面体顶点表示三条，各有出处",
         src="audit-report.md:188 与 rederivation-erratum.md:82、:363 的补法；本次逐条归位"),

    dict(id="P1.printed_false", kind="印出版已否证", deps=[],
         stmt="印出版第 14 页：n_{m-m2+1+l} < n_{m-m2+1}^{(delta^l)} <= n_{m-m2+1}^{delta}，其中第二个不等号对 l >= 2 为假",
         src="h5.txt:798-799（渲染页 14 已重渲染为 /tmp/r5-p14-14.png，本次未成功读出图像）"),
    dict(id="P2.printed_concl", kind="印出版已否证", deps=["P1.printed_false"],
         stmt="印出版据上一步得 T(n_{m-m2+1+l}) < 3/(2^v-1)^delta",
         src="h5.txt:801"),
    dict(id="P3.plus73", kind="论文论证", deps=[],
         stmt="定理 21 陈述页印 +73，证明末行印 +1（本轮登记，不改动）",
         src="渲染页 13（陈述）对 h5.txt:810（证明末行），两处本次亲读"),

    dict(id="M1.chain", kind="定理假设", deps=[],
         stmt="链是一个蕴含式：K > K_lo 蕴含 K >= Psi(K_lo)",
         src="rederivation-erratum.md:331-334（materials.md §2.2 第 6 条第 1 项逐字）+ 脚本 [5e0]"),
    dict(id="M2.psi_monotone", kind="本轮新增", deps=["M1.chain"],
         stmt="Psi 关于 K_lo 非降（每个 eps(m2, .) 关于 K 递减，可行 m2 集随 K 只增，q_min 关于 eps 非增）",
         src="rederivation-erratum.md:418-426 的作者自述「我自己的推理」+ 十一格网格；本轮审计其方向，见 CONFLICTS/方向条目"),
    dict(id="M3.fixed_point", kind="定理假设", deps=["M1.chain"],
         stmt="Psi(K*) = K*，K* = 2.05632218873398596256e20",
         src="rederivation-erratum.md:334 + 脚本 [5e0] 网格输出"),
    dict(id="M4.m92_verdict", kind="目标命题", deps=["M1.chain", "M2.psi_monotone", "M3.fixed_point"],
         stmt="可用起点类 = {K_lo <= L = 7.5311e11}；在 M2 下其最大输出为 K* = 2.0563e20 < U = 3.4302597024885020978e20，故 m = 92 不被排除",
         src="rederivation-erratum.md:331-339（materials.md §2.2 第 6 条第 3 项逐字）；本轮改写「任何不超过 K* 的起点」为「可用起点类」以消歧"),
    dict(id="M5.old_robust", kind="已撤回断言", deps=[],
         stmt="旧句：即使虚构起点 K > 1e20，链也只走到 2.0563e20（「对起点稳健」）",
         src="audit-report.md:208 与 :225 逐字；被 rederivation-erratum.md:336 撤回（materials.md §2.2 第 6 条第 4 项）"),
    dict(id="M6.probe_U", kind="定理假设", deps=[],
         stmt="K_lo = U 时第一步给出 K_new = 1.5678296618531818732906e22 > U；但该起点与 SdW 上界 K < U 冲突，不是可用起点",
         src="rederivation-erratum.md:337 逐字（materials.md §2.2 第 6 条第 4 项）"),
]

# ------------------------------------------------------------------
# 三、版本冲突登记（同一约束在同一处同时出现不同形式）
# ------------------------------------------------------------------
CONFLICTS = [
    dict(id="V1.wrap_symbol",
         entries=["corr.txt:33 与 :44 写严格 x_{m-m2+1} < delta x_m",
                  "corr.txt:63 写等式 x_{m-m2+1} = delta x_m",
                  "rederivation-erratum.md:82 写 <（严格）",
                  "rederivation-erratum.md:362 写 <=（非严格）"],
         effect="活跃约束计数与「顶点」两处需要等式或非严格形式",
         verdict="以 C1 的闭化读法裁决：论证只产出 S 的上界，P_open 含于 Pbar，故闭化无损；严格形式下结论不变（只降为上确界）",
         status="已裁决（不改变数值后果，改变的是「严格性」一栏的措辞）"),
    dict(id="V2.A_value",
         entries=["渲染页 13 陈述：97(m-m2)+73",
                  "h5.txt:810 证明末行：97(m-m2)+1"],
         effect="定理 21 的 A 项常数两处不同",
         verdict="+73 更大，是更弱的上界，故陈述页取值保守；勘误只替换尾项推导，不涉及 A 项",
         status="登记，本轮不改（materials.md §六 第 5 条同此）"),
    dict(id="V3.qmin_direction",
         entries=["rederivation-erratum.md:334 写「q_min 关于 eps 非增」",
                  "rederivation-erratum.md:423 写「q_min 关于 eps 非减」，同句结论是「Psi 非降」",
                  "rederive-erratum.py:172-176（qmin_lemma22 的 docstring）与 :320-336（qmin_bruteforce）都写「区间 (delta, delta+eps) 内分数的最小分母」"],
         effect="若按 :423 的两条单调性复合（非增 ∘ 非减）得到 Psi 非增，与结论矛盾；:334 的两条复合（非增 ∘ 非增）才得到 Psi 非降",
         verdict="以代码实现为准裁决：q_min 是区间 (delta, delta+eps) 内分数分母的最小值，区间随 eps 增大而变大，故 q_min 关于 eps 非增；:334 对、:423 错",
         status="已裁决（:423 的方向表述错误；结论方向不变）；实现侧已由两处 docstring 核实"),
]

# ------------------------------------------------------------------
# 四、三处缺口与 m = 92 的收口状态
# ------------------------------------------------------------------
GAPS = [
    dict(id="gap1.window_reading", name="窗口读法（子问题 2）",
         before="原文「this sum」指代不明：按 sum x 读才有回绕约束与 sum x >= sum k >= W",
         resolution="用构造替代读法：直接取 sum x 最大的 m2 窗（A7）。由 A3 与 A6，该窗满足 sum x >= sum x(第 13 页窗) >= sum k(第 13 页窗) >= W",
         closes_with=["A7.window_x", "A3.k_le_x", "A6.window_k"],
         status="收口：给出不依赖读者解释的显式构造（论证见报告第二节 R2）"),
    dict(id="gap2.vertex_attainment", name="无界多面体上最大值在顶点取到（子问题 1）",
         before="原文一句断言，无论证",
         resolution="分解为 C1（闭化无损）、C2（取到性，本轮给初等论证）、C3（有界多面体等于顶点凸包，标准引理加维数递降纲要）",
         closes_with=["C1.closure", "C2.attain", "C3.polytope", "G2.decompose"],
         status="收口为三条显式陈述；其中 C2 与 C3 的纲要为本轮所给，未形式化、未经第三方复核"),
    dict(id="gap3.strict_closure", name="严格不等号闭化（子问题 4）",
         before="P 非闭，「顶点」无从谈起",
         resolution="C1：论证只产出上界，P_open 含于 Pbar，故 max_{Pbar} S 可作为 sup_{P_open} S 的上界；顶点识别用的是同一个闭集，不循环",
         closes_with=["C1.closure"],
         status="收口：闭化无损（对「上界」用途），且与顶点识别自洽"),
    dict(id="m92.verdict", name="m = 92「对起点稳健」（子问题 3）",
         before="audit-report.md:208/:225 的旧句（对一切更强起点稳健）对 rederivation-erratum.md:336 的撤回",
         resolution="旧句字面为假（M6 给出越界探针）；正确表述按可用起点类：K_lo <= L，在 M2（未证、仅有纲与网格）下最大输出 K* < U，故不排除 m = 92",
         closes_with=["M1.chain", "M2.psi_monotone", "M3.fixed_point", "M4.m92_verdict", "M6.probe_U"],
         status="重判：旧句撤下；统一表述见报告第四节。注意「对一切可用起点」是全称断言，其依据 M2 是纲而非已证命题"),
]

# ------------------------------------------------------------------
# 五、结构性检查
# ------------------------------------------------------------------
def build_graph(ledger):
    nodes = {e["id"]: e for e in ledger}
    used_by = defaultdict(list)
    for e in ledger:
        for d in e["deps"]:
            used_by[d].append(e["id"])
    return nodes, used_by


def find_cycles(nodes):
    WHITE, GREY, BLACK = 0, 1, 2
    color = {k: WHITE for k in nodes}
    cycles = []

    def dfs(u, stack):
        color[u] = GREY
        stack.append(u)
        for v in nodes[u]["deps"]:
            if v not in nodes:
                continue
            if color[v] == GREY:
                i = stack.index(v)
                cycles.append(stack[i:] + [v])
            elif color[v] == WHITE:
                dfs(v, stack)
        stack.pop()
        color[u] = BLACK

    for k in nodes:
        if color[k] == WHITE:
            dfs(k, [])
    return cycles


def closure(nodes, root):
    seen, order = set(), []

    def rec(u):
        if u in seen or u not in nodes:
            return
        seen.add(u)
        order.append(u)
        for v in nodes[u]["deps"]:
            rec(v)

    rec(root)
    return seen, order


def topo_order(nodes):
    indeg = {k: 0 for k in nodes}
    for e in nodes.values():
        for d in e["deps"]:
            if d in nodes:
                indeg[e["id"]] += 1
    ready = [k for k, v in indeg.items() if v == 0]
    out = []
    while ready:
        u = ready.pop(0)
        out.append(u)
        for w in [x for x in nodes if u in nodes[x]["deps"]]:
            indeg[w] -= 1
            if indeg[w] == 0:
                ready.append(w)
    return out


def main():
    nodes, used_by = build_graph(LEDGER)
    failures = []

    print("=" * 72)
    print("一、账本规模")
    print("=" * 72)
    print("记号条目 %d 条；假设账本 %d 条" % (len(NOTATION), len(LEDGER)))
    kinds = defaultdict(int)
    for e in LEDGER:
        kinds[e["kind"]] += 1
    for k in sorted(kinds):
        print("  %-14s %d" % (k, kinds[k]))
    missing = sorted({d for e in LEDGER for d in e["deps"] if d not in nodes})
    print("悬空依赖（引用了不存在的节点）：", missing if missing else "无")
    if missing:
        failures.append("存在悬空依赖：" + repr(missing))

    print()
    print("=" * 72)
    print("二、无环性（循环检测）")
    print("=" * 72)
    cyc = find_cycles(nodes)
    print("检测到环的个数：", len(cyc))
    for c in cyc:
        print("  环：", " -> ".join(c))
    if cyc:
        failures.append("依赖图有环")
    order = topo_order(nodes)
    print("拓扑序长度 %d（应等于节点数 %d）：%s" % (len(order), len(nodes), "OK" if len(order) == len(nodes) else "不一致"))
    if len(order) != len(nodes):
        failures.append("拓扑序不完整（存在环或依赖悬空）")

    print()
    print("=" * 72)
    print("三、目标命题的证明闭包：自指与印出版回退")
    print("=" * 72)
    for target in ["TARGET.tail", "M4.m92_verdict"]:
        seen, _ = closure(nodes, target)
        in_closure = sorted(seen)
        print("目标 %s 的闭包 %d 个节点" % (target, len(seen)))
        bad_self = target in nodes[target]["deps"] or any(target in nodes[x]["deps"] for x in seen if x != target)
        print("  自指（目标出现在自己的闭包边里）：", bad_self)
        if bad_self:
            failures.append(target + " 自指")
        printed = sorted(x for x in seen if nodes[x]["kind"] == "印出版已否证")
        print("  闭包内的印出版已否证节点：", printed if printed else "无")
        if printed:
            failures.append(target + " 闭包含印出版已否证节点：" + repr(printed))
        retired = sorted(x for x in seen if nodes[x]["kind"] == "已撤回断言")
        print("  闭包内的已撤回断言：", retired if retired else "无")
        if retired:
            failures.append(target + " 闭包含已撤回断言：" + repr(retired))
        unprovenish = sorted(x for x in seen if nodes[x]["kind"] in ("本轮新增", "标准引理", "原文读法"))
        print("  闭包内需要逐条标证据类型的节点：", unprovenish)

    print()
    print("=" * 72)
    print("四、顶点句是否暗中用到待证的界（子问题 1 的核心检查）")
    print("=" * 72)
    seen_t, _ = closure(nodes, "TARGET.tail")
    print("TARGET.tail 闭包内的节点：")
    for x in sorted(seen_t):
        print("  %-18s [%s]" % (x, nodes[x]["kind"]))
    other_goals = [x for x in seen_t if nodes[x]["kind"] == "目标命题" and x != "TARGET.tail"]
    print("检查：闭包内是否含其它目标命题节点（排除自身）？",
          other_goals or "无")
    print("检查：是否有节点把 TARGET.tail 列为依赖（自指边）？",
          [x for x in seen_t if x != "TARGET.tail" and "TARGET.tail" in nodes[x]["deps"]] or "无")
    if other_goals or [x for x in seen_t if x != "TARGET.tail" and "TARGET.tail" in nodes[x]["deps"]]:
        failures.append("TARGET.tail 闭包含其它目标命题或存在自指边")
    print("检查：C4/C5 用到的 A14.H21 是定理假设还是目标？",
          "定理假设" if nodes["A14.H21"]["kind"] == "定理假设" else "非假设")
    print("检查：A14.H21 是否出现在 A14.H21 自己的闭包内（是否被用来证自身）？",
          "A14.H21" in closure(nodes, "A14.H21")[0])
    print("说明：定理 21 的假设 A14.H21 是对 m2 存在性的假设，不是待证的尾项不等式 TARGET.tail；")
    print("      故 C4.no_xi1 用 A14.H21 不构成循环。尾项不等式的证明用到 A14 以外的前提已逐条列出。")

    print()
    print("=" * 72)
    print("五、版本冲突与收口状态")
    print("=" * 72)
    for c in CONFLICTS:
        print("[%s] %s" % (c["id"], c["status"]))
        for e in c["entries"]:
            print("    - " + e)
        print("    影响：" + c["effect"])
        print("    裁决：" + c["verdict"])
        print()
    for g in GAPS:
        print("[%s] %s -> %s" % (g["id"], g["name"], g["status"]))
        print("    收口所依节点：" + "、".join(g["closes_with"]))
        print()

    print("=" * 72)
    print("六、锚点自检（先定义后计算的落地）")
    print("=" * 72)
    from mpmath import mp, mpf, log as mlog, power
    mp.dps = 60
    X0 = mpf(695) * power(2, 60)
    delta = mlog(3) / mlog(2)
    c = mlog(mpf(162) / 97 * X0) / mlog(2)
    print("X0   = %s" % mp.nstr(X0, 25))
    print("delta= %s" % mp.nstr(delta, 40))
    print("c    = %s" % mp.nstr(c, 25))
    pinned_c = "70.180806328308366825"
    print("钉住值 c = %s；前 20 位一致？ %s" % (pinned_c, mp.nstr(c, 21).startswith("70.1808063283083668")))
    K_up_91 = mpf("1.4784") * 91 * power(delta, 91)
    K_lo_91 = mpf(7941964418702608664581)
    marg = K_lo_91 / K_up_91
    print("K_up(91) = %s（钉住 214072842063828923281.3586）" % mp.nstr(K_up_91, 27))
    print("余量     = %s（钉住 37.09935525747164492758953）" % mp.nstr(marg, 25))
    print("余量前 25 位一致？", mp.nstr(marg, 25) == "37.09935525747164492758953")
    U92 = mpf("1.4784") * 92 * power(delta, 92)
    print("U(92)    = %s（钉住 3.4302597024885020978e+20）" % mp.nstr(U92, 20))
    Kstar = mpf("2.05632218873398596256") * mpf(10) ** 20
    print("K* < U(92)？", Kstar < U92, " 比值 U/K* =", mp.nstr(U92 / Kstar, 12))
    print("L = 7.5311e11 <= K* ？", mpf("7.5311") * mpf(10) ** 11 <= Kstar)

    print()
    print("=" * 72)
    print("七、失败点清单（本文件的检查结论）")
    print("=" * 72)
    if failures:
        for f in failures:
            print("  未通过：" + f)
    else:
        print("  结构性检查全部通过：无环、无悬空依赖、目标闭包不含印出版已否证节点与已撤回断言。")
        print("  仍未证（不是本文件能解决的）：M2 的全称形式、C2 与 C3 的形式化、以及所有证据类型的标注义务。")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
