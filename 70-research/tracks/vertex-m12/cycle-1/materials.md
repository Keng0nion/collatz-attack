# vertex-m12 首轮一手材料（顶点识别的机器核对升一档）

收集人：材料收集员（本工作流子代理）
日期：2026 年 10 月 27 日
服务对象：本轨道首轮方案 `70-research/tracks/vertex-m12/plan.md`（177 行，md5 `6ad2e1e3ce6619bd9f31a7aab0f8d516`）与疑点原文的五条子问题
本文件性质：只做材料收集与逐字引用，**不作裁决、不含新数学结论**；凡我自己的推断处一律写明「我的推断」。

## 〇、怎么读这份文件

1. 每条材料给出：名称、路径或 URL、**我是否亲自打开**、与疑点相关的关键句（逐字）。
2. 证据分级（沿用本项目惯例）：**本次亲跑** = 本次执行命令所得；**原件逐字** = 本次亲自打开的原件（含渲染图核对）；**文件亲读** = 本次逐行读过的项目文件；**未核实** = 本次没做到或没找到。
3. 行号一律以本次自己下载或抽取的副本为准，并附 md5 与行数（纪律出处：`learnings.md:39`「用旧版本的行号作裁决前提」，行号漂移会让判定变成假判定）。
4. 逐字引文保留原文（含原文的连字符、上标压平等抽取痕迹，就地注明）；我自己的中文叙述遵项目排版纪律（正文不用半角连字符）。
5. 勘误与论文的公式若抽取乱码，一律用 `pdftoppm` 渲染成图再读（本次勘误两页、论文第 13、14 页都渲染并看图核对）。
6. 本文件的小节与我落的原始输出都在本目录 `materials/` 下；逐字引用的路径如果是相对路径，基准是 `collatz-attack/`。

---

## 一、一手原件（本次亲自下载、打开、渲染核对）

### 1.1 勘误：Corrigendum to Article 23.3.5（`There are no Collatz-m-Cycles with m ≤ 91`）

1. 出处：`https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf`
2. 本机副本：`70-research/tracks/vertex-m12/cycle-1/materials/corrigendum.pdf`（124287 字节，2 页），抽取文本 `corrigendum.txt`（`pdftotext -layout`，88 行）。
3. **我是否亲自打开**：是。本次 `curl -sL` 下载，退出码 0；字节数与 md5 实测 `124287`、`f23d5f969116cb1af6e9b981b4b3ba7a`，与 `70-research/cycle-1/plan.md:107`、`cycle-1/materials.md:71`、`audit-report.md:17` 的记录一致（即本次重下的与项目此前用的是同一份）。渲染图：第 1 页 `corr-p1-1.png`、第 2 页 `corr-p2-2.png`（150 dpi），**两页我都看过图**。
4. 抓取前的 host 校验（本次实测）：`dig +short cs.uwaterloo.ca` 得 `129.97.167.168`，`ipaddress` 判定 `is_private=False、is_loopback=False、is_reserved=False、is_global=True`。

**与疑点相关的逐字关键句**

1. **顶点句（疑点命题 R 的原文出处，第 2 页；抽取文本 `corrigendum.txt:43` 至 `:46`，已按第 2 页渲染图逐字核对）**：
   > `Since all xi are positive, the function S is convex and attains its maximum value at a vertex of the polytope determined by the constraints xi ≥ 1, xi+1 ≤ δxi , xm−m2 +1 < δxm , and xm−m2 +1 + · · · + xm ≥ mm2 · K. Thus, at least m2 of these constraints must be active, i.e., must hold with equality.`
   渲染图上的排版：`xi ≥ 1` 与 `xi+1 ≤ δxi` 是行内两条，`xm−m2+1 < δxm`（**严格不等号**）单列，和约束右端是分数 `(m2/m)·K`（抽取文本压平成 `mm2 · K`）。**这就是「可行顶点集恰为 m₂ 个循环旋转」这句话所在的原文段落的开头：原件只说「最大值在某顶点取到」与「至少 m₂ 条约束取等」，并没有写「顶点集是循环旋转」这个更强命题**——该更强命题见下面第 3 条（原文下一段）与项目里的 Step 8′。
2. **约束计数与把严格约束写成等式（第 2 页；`corrigendum.txt:54` 至 `:62` 逐字）**：
   > `    Thus, m2 of the remaining m2 + 1 constraints must be active. If all constraints xi+1 ≤ δxi , xm−m2 +1 < δxm were active simultaneously, this would lead to the contradiction xm = δ m2 xm , and hence δ = 1, contradicting δ = log 3/log 2. Therefore, the sum condition must be active, and we have xm−m2 +1 + · · · + xm = (m2/m)·K, together with all but one of the equations xi+1 = δxi , and xm−m2 +1 = δxm .`
   （抽取文本把该段拆成 `:54` 至 `:62` 若干行、分数压平为 `mm2 · K`；上面的引文按渲染图把分数还原写法。**注意：原件在这一句里把严格约束 `x_{m−m2+1} < δx_m` 升级写成等式 `x_{m−m2+1} = δx_m`。**）
3. **顶点坐标 = 循环置换（第 2 页；`corrigendum.txt:64` 至 `:65`）**：
   > `Consequently, S attains its maximum at a point whose coordinates are a cyclic permutation of xm−m2 +1 , δxm−m2 +1 , . . . , δ m2 −1 xm−m2 +1 , and`
   紧接 `:66` 起给出 `(m2/m)·K = … = x_{m−m2+1}·(δ^{m2} − 1)/(δ − 1)`，`:71` 行给出 `x_{m−m2+1} = v`（渲染图上逐字为 `x_{m−m2+1} = (m₂/m)·K·(δ−1)/(δ^{m₂}−1) = v`）。
4. **`x_i = 1` 不可行（第 2 页；`corrigendum.txt:47` 至 `:53`）**：
   > `    Suppose there is a value xi such that xi = 1. Then xi+1 ≤ δ, . . . , xi−1 ≤ δ m2 −1 . Hence, xm−m2 +1 + · · · + xm ≤ (δ m2 − 1)/(δ − 1) < (m2/m)·K, contradicting the sum constraint. The last inequality follows from the definition of m2 in the statement of Theorem 21.`
   （抽取文本把不等式拆行；上面按渲染图还原为一行。）
5. **首句（勘误要修的是哪一步；`corrigendum.txt:11` 至 `:14`，按第 1 页渲染图核对）**：
   > `The derivation of the inequalities T (nm−m2 +1+ℓ ) < 3/(2v −1)δ in the proof of Theorem 21 at the bottom of page 14 contains an error. To show the statement`
   渲染图上逐字：`T(n_{m−m2+1+ℓ}) < 3/(2^v−1)^δ`（δ 是整个分母括号的上标）。
6. 与「2m₂ + 1 条约束」口径的对照材料（**只登记，不裁决**）：勘误原文把约束写成 `x_i ≥ 1`（m₂ 条）、相邻链 `x_{i+1} ≤ δx_i`（窗口内）、**回绕单列一条 `x_{m−m2+1} < δx_m`**、和约束一条；代码侧 `r2_common.constraint_list` 把回绕并进 m₂ 条循环链约束（末条即回绕，见 2.1 第 3 条），两边都是 `2m₂ + 1` 条，差别只在回绕写严格号还是非严格号。项目对该差别的既有处理见 `60-audits/hercher-t21/rederivation-erratum.md:84`（逐字在 4.6 第 1 条之 3）。

### 1.2 论文：Hercher 2023（JIS 26，文章 23.3.5）

1. 出处：`https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf`
2. 本机副本：`70-research/tracks/vertex-m12/cycle-1/materials/hercher5.pdf`（250655 字节，22 页），抽取文本 `hercher5.txt`（`pdftotext -layout`，1256 行、76688 字节）。
3. **我是否亲自打开**：是。本次 `curl -sL` 下载，退出码 0；字节数与 md5 实测 `250655`、`3e2377bef0b1c0435dc455c9bbee43a1`，与 `70-research/cycle-1/plan.md:108`、`cycle-1/materials.md:24` 的记录一致。渲染图：第 13 页 `hercher-p13-13.png`、第 14 页 `hercher-p14-14.png`，**两页我都看过图**。
4. **一条与方法有关的重要事实（本次实测）**：两条 `grep` 在印刷版全文**零命中**（本次实跑，均无输出）——`grep -n "vertex\|vertices\|polytope" hercher5.txt` 与 `grep -n "convex" hercher5.txt`。即：**「凸性 + 多面体顶点」这一整套论证只存在于 2026 年勘误，印刷版第 14 页用的是另一条（后来被作者本人判为有错的）推导。** 疑点所说的「顶点识别」命题的原文出处只能是勘误。

**与疑点相关的逐字关键句**

1. **Theorem 21 陈述（第 13 页；`hercher5.txt:695` 起，已按第 13 页渲染图逐字核对）**：
   > `Theorem 21. Let K be the number of odd numbers in a given m-cycle, and let L be the number of even numbers in it. Further, assume there exists a positive integer m2 with`
   > `m2 ≤ m and (δ^{m2} − 1)/(δ − 1) · log((162/97)·X0)/log(2) ≤ (m2/m)·K.`
   > `Let v = (m2/m)·K·(δ−1)/(δ^{m2}−1). Then we get`
   > `δ < (K+L)/K < δ + 1/(K·3·log(2))·( (97(m−m2)+73)/(54·X0) + 3/(2^v −1) + 3·(m2 −1)/((2^v −1)^δ) ).`
   （抽取文本 `:695` 至 `:706` 把分数压平；上面的写法按渲染图还原。**与 `+73` 有关的一处印刷出入，我按第 13、14 两页渲染图逐字确认，不是抽取误差**：陈述页（第 13 页，抽取文本 `:709`）印 `97(m−m₂)+73`，证明末行（第 14 页，抽取文本 `:810` 至 `:812`）印 `97(m−m₂)+1`。项目对此有既有登记，逐字如 `dispute.md:53`：`Theorem 21 的**陈述**用 `(97(m−m₂)+73)/(54·X₀)`，而**证明末行**印的是 `(97(m−m₂)+1)/(54·X₀)`。两者不等，但证明末行更弱（更小），且第三项 `3(m₂−1)/(2^v−1)^δ` 才是主项，故不影响结论。`；`rederivation-as-printed.md:269` 逐字：`论文 Theorem 21 的**陈述**页印 `(97(m−m₂)+73)/(54·X₀)`，**证明末行**印 `(97(m−m₂)+1)/(54·X₀)`（我在渲染图上确认了两处）。我按 `+73` 重建……并把 `+1` 也跑了一遍：`m = 91` 的两条链给出**相同**的七个 `m₂` 与七个 `q_min`。`。本条与顶点识别无关，只作引用纪律登记。）
2. **印刷版被修的那一步（第 14 页；`hercher5.txt:796` 至 `:801` 逐字，抽取原文照录）**：
   > `Now this gives T (nm−m2 +1 ) < 2v3−1 and, since`
   > `nm−m2 +1+ℓ < n(δℓ)m−m2 +1 ≤ nδm−m2 +1 ,`
   > `we get the inequality T (nm−m2 +1+ℓ ) < (2v −1) δ . Using this together with Theorem 14 and`
   （旁注：勘误首句指的就是这条不等式；上标在抽取里错位，读法与位置以第 14 页渲染图为准。）
3. **v 的定义句（第 14 页；`hercher5.txt:790`）**：
   > `   From the definition of v, we get v · δ δ−1  = mm2 · K. Thus, we have`
   （即 `v·(δ^{m2}−1)/(δ−1) = (m2/m)K`。）

### 1.3 与 (P1) 有关的读法登记（材料，不裁决）

1. 项目把 Theorem 21 的前提读作「存在 m₂ 使 `c·(δ^{m₂}−1)/(δ−1) ≤ W`」（`c := log₂((162/97)X₀)`），于是 `c > 1` 给出更强的一组判据 `(δ^{m₂}−1)/(δ−1) < W`，项目称 (P1)。出处：`cycle-1/route-1.md:306`（Step 3 逐字「`c := log₂((162/97)·X₀) = 60 + log₂(112590/97) > 61 > 1`，故 `(δ^{m₂} − 1)/(δ − 1) < W`，即 (P1) 成立」）。
2. 我本次用精确 `Fraction` 复算的 `c > 1` 派生量（四档阈值与 v）见 5.3；`X₀ = 695·2^60` 与 `c = 70.18080632830836682484879` 与 `r1_selfcheck` 的 `[0]` 锚点行一致（见 5.5）。

---

## 二、代码底座（本次逐行亲读；附 md5 与行数）

### 2.1 `70-research/cycle-1/scripts/r2_common.py`（244 行，md5 `cfee819667c0883e73732f03d2dc8bef`）

1. **我是否亲自打开**：是，全文读毕。
2. 多面体定义（docstring，`:11` 至 `:18`）逐字：
   > `多面体（勘误原文约束表的逐字转写，窗口 y_j := x_{m−m2+j}，j = 1..m2）：`
   > `  (C1) y_j >= 1                  （x_i = log2(n_i + 1) >= 1）`
   > `  (C2) y_{j+1} <= δ y_j          （j = 1..m2，指标循环，m2 条；末条即回绕约束`
   > `                                  x_{m−m2+1} <= δ x_m）`
   > `  (C3) Σ_j y_j >= W              （W = (m2/m)·K）`
3. 约束表实现（`:162` 至 `:180`）逐字：
   > `def constraint_list(m2, d, W):`
   > `    """把 2m2+1 条约束写成 (系数向量, 右端, 类型) 列表，类型 'ge'/'le'。`
   >
   > `    顺序：前 m2 条是 y_j >= 1；接着 m2 条是链约束 y_{j+1} <= δ y_j（j=0..m2−1`
   > `    循环，第 m2−1 条即回绕）；最后一条是 Σy >= W。`
   > `    """`
4. 精确求解与秩（`solve_exact`，`:183` 至 `:217`）逐字关键行：`:184` `"""精确高斯消元（Fraction）。返回 (解, 秩)；若不相容返回 (None, 秩)。"""`；`:212` 至 `:213` `if rank < m:` / `        return None, rank          # 解不唯一`。
5. 可行性（`feasible`，`:145` 至 `:159`）逐字关键行：`:153` `            bad.append(f"C1:y{j+1}<1")`；`:156` `            bad.append(f"C2:y{(j+1)%m2+1}>δ·y{j+1}")`；`:158` `            bad.append("C3:Σy<W")`。
6. 顶点与 v（`:134` 至 `:142`）逐字：`def v_vertex(m2, d, W): """v = W(δ−1)/(δ^{m2}−1)。"""`；`def vertex(m2, d, W, rot=0): """顶点向量：v·(δ^{rot}, δ^{rot+1}, ..., δ^{rot+m2−1})（指标 mod m2）。"""`。
7. δ 的严格括号（`delta_rigorous_bounds`，`:54` 至 `:70`）逐字：`:54` 至 `:57` `def delta_rigorous_bounds(q):` / `    """返回 (p/q, r/q) 使 2^p < 3^q < 2^r，即 p/q < log3/log2 < r/q。` / `    判据只用整数幂比较（2^p < 3^q 等价于 p/q < log3/log2），不用浮点。` / `    """`。
8. 独立性登记（`:5` 至 `:9`）逐字：本文件「只按勘误原文的约束表定义多面体与目标函数，不 import 任何项目脚本」，「一切判决只用 fractions.Fraction 与整数幂（gmpy2），浮点与 mpmath 只用于『探针』与『锚点自检』」。

### 2.2 `70-research/cycle-1/scripts/r2_j_independent_vertices.py`（272 行，md5 `4b8ce2a500d8ca9021fd0178deca637e`）

1. **我是否亲自打开**：是，全文读毕。
2. docstring 原理行（`:9` 至 `:12`）逐字：
   > `  A. 全活跃子集穷举（对 m2 = 10 与 m2 = 12）：枚举全部 C(2m2+1, m2) 个大小为 m2 的`
   > `     活跃子集，精确解线性方程组、查秩、查可行性。原理：任一顶点处存在一个大小为 m2`
   > `     且秩为 m2 的活跃子集，故此法不漏顶点，且完全不提 (L1)。代价：组合数爆炸，`
   > `     m2 = 10 为 352716，m2 = 12 为 5200300，m2 = 20 已是 2.7e11（不可能）。`
3. 枚举主循环（`full_enumeration`，`:92` 至 `:114`）逐字关键行：`:102` `    for S in combinations(range(n), m2):`；`:108` 至 `:113`：
   > `        sol, rank = solve_exact(rows, b)`
   > `        if sol is None or rank < m2:`
   > `            continue`
   > `        ok, _ = feasible(sol, m2, d, W)`
   > `        if ok:`
   > `            verts[tuple(sol)] = S`
   进度行 `:104` 至 `:105` 每 200000 个子集打印一次（这就是基线日志里 `... 已枚举 200000/352716（33 s）` 的来源）。
4. **A 段实际只挂了一个档（`:121` 至 `:127` 逐字）**：
   > `    say("成本曲线（本机实测，用于说明为什么只做到 m2 = 10）：")`
   > `    say("    m2 = 10：C(21,10) = 352716 个子集，约 0.13 ms/个 → 约 50 s")`
   > `    say("    m2 = 12：C(25,12) = 5200300 个子集，实测 0.83 ms/个 → 投影约 72 min（本次未跑）")`
   > `    say("    m2 = 20：C(41,20) ≈ 2.7e11 个子集 → 不可达")`
   > `    cases = [`
   > `        ("A1 m2=10 δ_lo W=2000（即第 3 步的 E4）", 10, D_LO7, Fraction(2000)),`
   > `    ]`
   **我的推断（材料标注）：注释与打印文本里写「对 m2 = 10 与 m2 = 12」，但 `cases` 列表只有 A1；`grep -n "12" r2_j_independent_vertices.py` 命中的只有注释、打印文本与 B2 权重数（`:161`），没有任何 m₂ = 12 的实跑入口。即：m₂ = 12 档「代码写了、从未跑过」这一说法与源码一致（该说法出处：本轨道 `plan.md:40`）。**
5. A 段判定行与证书行（`:134` 至 `:138`）逐字：`say(f"    子集总数 C({2*m2+1},{m2}) = {total}，用时 {dt:.1f} s")`；`say(f"    可行顶点数 = {len(verts)}；与解析的 m2 = {m2} 个循环旋转相同 = {set(verts.keys()) == analytic}（解析集大小 {len(analytic)}）")`；`certs = sorted({active_rank(y, m2, d, W) for y in verts})`。
6. 独立性声明行（`:139` 至 `:141`）逐字：`    # 这一段的独立性说明：全程未调用任何与 (L1) 有关的判据`；输出对应行 `say(f"    独立性：本段只用 constraint_list / solve_exact / feasible，未使用 (L1) 或 v 的任何信息")`。
7. 模块守卫（`:264` 至 `:272`）：`if __name__ == "__main__":` 起按 `sys.argv[1]`（默认 `"AB"`）选跑 A、B 段——**import 本模块不会触发任何枚举**（我这几次实跑都依赖这一点）。

### 2.3 `70-research/cycle-1/scripts/r2_b_vertices.py`（187 行，md5 `4d19e2fc351cea7a3b21e487a3c02e97`）

1. **我是否亲自打开**：是，全文读毕（脚本无 `__main__` 守卫，import 即执行：`:142` 起模块级 `say(...)`，主循环 `for tag, m2, d, W in PARAMS:` 在 `:147`）。
2. 两条路线（docstring，`:7` 至 `:14`）逐字：
   > `  A. 约简穷举（对任意 m2）：先精确验证「y_j = 1 不可行」这一初等引理`
   > `     （判据 (δ^{m2}−1)/(δ−1) < W，纯有理比较），于是任一顶点必须有 m2 条活跃约束`
   > `     落在「m2 条循环链约束 + 1 条和约束」这 m2+1 条里。逐个枚举这 m2+1 个大小 m2 的`
   > `     子集，精确解线性方程组、查秩、查可行性。`
   > `  B. 全穷举（小 m2 用）：枚举全部 C(2m2+1, m2) 个活跃子集，不依赖引理 A，作交叉核对。`
3. 参数表（`:125` 至 `:138`）中与疑点直接相关的三行逐字：
   > `    ("E4  m2=10 δ_lo   W=2000",               10, D_LO7, Fraction(2000)),`
   > `    ("E10 m2=5  δ_lo   W=(δ^5−1)/(δ−1)（阈值上的边界情形 v=1）", 5, D_LO7, None),`
   > `    ("E12 m2=6  δ_lo   W=500",                6,  D_LO7, Fraction(500)),`
   以及全穷举档集合（`:140`）：`FULL_FOR = {2, 3, 4, 5, 6}`（E10 的 m₂ = 5 因此带全穷举交叉核对）。
4. W 为空时的边界口径（`:147` 至 `:152`）：`E5` 取 `W = 70·(δ^{m2}−1)/(δ−1)`（使 v = 70）；其余取 `W = (δ^{m2}−1)/(δ−1)`（阈值上的边界，v = 1）——**E10 的 v = 1 就是这么来的**。
5. **重要材料事实（对子问题 4）**：本脚本与 `r2_j_independent_vertices.py` **共用同一个 `r2_common` 底座**（三份文件都 `sys.path.insert(...cycle-1/scripts)` 后 `from r2_common import ...`）。所以两者只算「两条不同的枚举策略」，**不构成「不同语言与算术栈」的独立实现**；子问题 4 要求的交叉核验在既有材料里没有到位（本次核实的现有材料范围即此）。

---

## 三、既有基线日志（本次亲读；前轮产物，行号以本机现文件为准）

### 3.1 m₂ = 10 阳性基线

1. `70-research/cycle-1/scripts/results/verify-round2/r2_j_A.txt`（16 行，md5 `8f8d0112668a88d0811f30cefa396bd1`）。**我是否亲自打开**：是，逐行读毕。关键行逐字（`:4` 至 `:6`、`:11` 至 `:14`）：
   > `成本曲线（本机实测，用于说明为什么只做到 m2 = 10）：`
   > `    m2 = 10：C(21,10) = 352716 个子集，约 0.13 ms/个 → 约 50 s`
   > `    m2 = 12：C(25,12) = 5200300 个子集，实测 0.83 ms/个 → 投影约 72 min（本次未跑）`
   > `    子集总数 C(21,10) = 352716，用时 62.3 s`
   > `    可行顶点数 = 10；与解析的 m2 = 10 个循环旋转相同 = True（解析集大小 10）`
   > `    每个顶点的（活跃约束法向量秩，活跃约束条数）= [(10, 10)]`
   > `    独立性：本段只用 constraint_list / solve_exact / feasible，未使用 (L1) 或 v 的任何信息`
   同文件 `:10` 有跑中进度行 `      ... 已枚举 200000/352716（33 s）`，`:16` 有口径行 `口径：本脚本是独立核对，不是证明；A 段是穷举（在给定 m2 下完备），B 段是有限取点（不完备）。`
2. `…/verify-round2/r2_j_A.time`（3 行，md5 `440e8a872de8d71cacee663fab6536f3`）逐字：`real 62.49` / `user 61.78` / `sys 0.34`。
3. 成本曲线的出处登记（`cycle-1/route-2.md:205` 逐字）：
   > `3. 成本曲线（本机实测，用来交代为什么停在这里）：m2 = 10 每子集约 0.13 毫秒；m2 = 12 每子集 0.83 毫秒 × C(25,12) = 5200300 → 投影 72 分钟（**本次未跑**）；m2 = 20 需 C(41,20) = 269128937220 个子集（约 2.7e11），不可达。**[实测 + 未跑登记]**`
   以及 `cycle-1/route-2.md:271` 至 `:272`（N8 的命令行与原始输出摘要）逐字：
   > `2. 全活跃子集穷举（N8）：`$PY r2_j_independent_vertices.py A > results/verify-round2/r2_j_A.txt`；末几行原文：`子集总数 C(21,10) = 352716，用时 62.3 s`、`可行顶点数 = 10；与解析的 m2 = 10 个循环旋转相同 = True（解析集大小 10）`、`每个顶点的（活跃约束法向量秩，活跃约束条数）= [(10, 10)]`。`
   > `6. 成本曲线实测（N8 用）：内联脚本对 m2 = 10 测 3000 个子集得 0.39 秒（0.13 毫秒/个），对 m2 = 12 测 4000 个子集得 3.32 秒（0.83 毫秒/个）。`
   **注意（我的核对）**：`route-2.md` 的这两条只是文字登记，**内联测速脚本本身没落盘、不可复跑**（本次 `grep` 与文件清单都没有它）；0.83 毫秒/个这个数是「本次未跑」投影的唯一来源。

### 3.2 E10 边界档（v = 1）

1. `70-research/cycle-1/scripts/results/r2_b_out.txt`（136 行，md5 `f3882451e5a45fc3cb5cce781f279e32`）。**我是否亲自打开**：是，E1 至 E12 全段读毕。E10 段逐字（`:91` 至 `:99`）：
   > `[E10 m2=5  δ_lo   W=(δ^5−1)/(δ−1)（阈值上的边界情形 v=1）]  δ = 126797/80000`
   > `    v = W(δ−1)/(δ^m2−1) 的分子位数 = 1，分母位数 = 1`
   > `    (L1) y_j = 1 不可行的初等引理判据 (δ^m2−1)/(δ−1) < W：70 位分子 / 66 位分母 vs W = 630347359154513105681/40960000000000000000  → False`
   > `    「5 条链约束全取等」（无和约束）：唯一解 = 零向量（秩 5）`
   > `    「5 条链约束全取等 + 和约束」（勘误 :63 的逐字等式读法）：不相容（无解）（增广秩 5）`
   > `    约简穷举：唯一可行顶点数 = 5；与解析的 m2 个循环旋转相同 = True（解析集大小 5）`
   > `    每个顶点的活跃约束法向量秩（应为 m2 = 5）：[(5, 6)]`
   > `    全穷举（C(2m2+1, m2) = 462 个子集，不依赖 L1）：可行顶点数 = 5；与约简一致 = True`
   > `    v ≈ 1.0（浮点仅作摘要）`
   各档汇总行（`:132`）逐字：`    E10 m2=5  δ_lo   W=(δ^5−1)/(δ−1)（阈值上的边界情形 v=1） | 5 | 5 | True | 0.0`。
2. `…/verify-round2/r2_b.time`（3 行）逐字：`real 44.08` / `user 43.94` / `sys 0.08`（整套 12 个参数集一次跑完的墙钟）。
3. E10 的证书含义（我的核对）：`[(5, 6)]` = 顶点处活跃约束法向量秩 5、活跃约束条数 6（比 m₂ = 5 多 1 条）——这与 `route-1.md` Step 8′ 第 2 条「恰当和约束活跃 + 恰 m₂ − 1 条链约束活跃」的计数口径互补：阈值上回绕约束也取等，于是活跃条数是 6 而秩仍是 5。

### 3.3 B 段（z3 LRA）与其两次读模型失败

1. 三份日志都在 `…/verify-round2/`：`r2_j_B.txt`（3801 字节）、`r2_j_B2.txt`（8303 字节）、`r2_j_B3.txt`（1673 字节）。**我是否亲自打开**：是，三份都通读。
2. 失败登记（`r2_j_B.txt` 与 `r2_j_B2.txt` 首段的逐字）：`（读模型异常：TypeError int() argument must be a string, a bytes-like object or a real number, not 'IntNumRef'）` 与 `    !! w#0：模型值不是有理数，未转成 Fraction`（B1 段 14/14、B2 段 12/12 全部失败）。
3. 修好后的结果（`r2_j_B3.txt` 逐字）：`取到最优模型并逐项精确核对的权重数 = 14；由这些模型**发现**的顶点数 = 10/20`（B1，2.3 秒）；B2 `12/12` 与 `12/47`（54.4 秒）；B3 `10/10` 与 `9/91`（526.3 秒）。三段的 `出现 sat = 0` 都成立。
4. 修复说明的出处（`cycle-1/route-2.md:248` 至 `:250`，§8.5 第 1 条）逐字要点：`Optimize` 的模型值是 `RatNumRef`，正确通道是 `RatNumRef.as_fraction()`；「**承重的判定（`unsat`）不受这个 bug 影响**，因为它不读模型」。本文件另注：`r2_j_B.txt`、`r2_j_B2.txt` 是保留的失败日志（项目明说不删）。

---

## 四、路线、账本、教训里的锚点（本次亲读）

### 4.1 账本（`70-research/ledger.md`，130 行，md5 `c238e1003f6cf3b1ee0fcf29ae82e58a`）

1. `:25`（节 0.2 第 4 条）逐字：
   > `4. **顶点识别的机器核对提升一档**：跑 m₂ = 12 的不依赖 (L1) 全活跃子集穷举（C(25,12) = 5200300 个子集，投影约 72 分钟），或把 det 与秩论证做成 Lean 引理（需先装 Lean）。`
2. `:109`（节 1.4 未决第 2 条）逐字：
   > `2. **全部证明未形式化**（本机无 Lean 与 Coq）：顶点引理、闭化零损失、Ψ 非降都只到「自足纸面论证」级；顶点识别的一般证明虽对任意 m₂ 写成，机器核对只到 m₂ = 10 的全活跃子集穷举（不依赖 (L1)）与 12 个参数集的约简穷举（依赖 (L1)），m₂ = 12 的全穷举未跑（投影约 72 分钟），m₂ = 20、47、91 的独立穷举不可达。`

### 4.2 教训（`70-research/learnings.md`，45 行，md5 `e88a8c5a37f0bf6d11cb795683f25638`）

1. `:45`（第 11 条）逐字：
   > `11. **对 m₂ = 20、47、91 硬做全活跃子集穷举**：`C(2m₂ + 1, m₂)` 的组合规模使这条路不可达（本轮到 m₂ = 10 已是 352716 个子集），更大 m₂ 只能做依赖 (L1) 的约简穷举。教训：升核对档位时选 m₂ = 12（C(25,12) = 5200300，投影约 72 分钟）这类「还跑得动」的档，而不是继续加参数集；不可达档要如实写成核对边界。`
2. `:36`（第 2 条，本题的直接教训）逐字要点：报告里的数字必须能 `grep` 到脚本或日志，「参数表与实跑日志对不上时以日志为准」——本轨道产物引 0.83 毫秒/个时只能引「登记文本」，因为测速内联脚本没落盘（见 3.1 第 3 条）。
3. `:38`（第 4 条）逐字：`教训：要卡边界必须用 δ 的**严格下界**（如 126797/80000）做精确有理比较。`
4. `:39`（第 5 条）逐字要点：引用 r2_j、r2_common 这类文件必须给路径、行号与版本身份（行数或 md5）——本文件第五节的 md5 清单即为此准备。
5. `:41`（第 7 条）逐字要点：「担保『无洞』要写出窗口的起算位置」；`:44`（第 10 条）逐字：`教训：网格只能作机制检查或反例搜索，永远不能当全称命题的证据。`

### 4.3 第 2 轮计划（`70-research/plan.md`，184 行，md5 `6e85bc8d155018719d3eb1a74310324f`）

1. `:132` 逐字（第 2 轮禁区）：`10. 「对 m₂ = 20、47、91 硬做全活跃子集穷举」（`learnings.md:45`）与「「m 圈排除」靠逐级抬高验证界走到终点」（`learnings.md:20`）：本轮不碰验证界，不做全活跃子集穷举。`
2. `:178` 逐字（留给后续轮次）：`3. 账本 0.2 第 4 条的顶点识别核对升一档（m₂ = 12 全活跃子集穷举约 72 分钟，或 Lean 引理）。`

### 4.4 第 1 轮小结与材料里的登记

1. `70-research/cycle-1/summary.md:106` 逐字：
   > `2. **全部证明未形式化**（本机无 Lean 与 Coq）：顶点引理、闭化零损失、Ψ 非降都只到「自足纸面论证」级。顶点识别的机器核对只到 m₂ = 10 的全活跃子集穷举与 12 个参数集的约简穷举，m₂ = 12 的全穷举未跑（投影约 72 分钟），m₂ = 20、47、91 的全穷举不可达。`
2. `70-research/cycle-1/materials.md:274`（第 1 轮材料文件，394 行，md5 `c0b077e6b5d3f0d0bf671e721941d632`）逐字：
   > `   3. `:73` 至 `:81` 的精确核验（`m2 = 3..8` 穷举全部活跃约束子集；`m2 = 12、91、300` 的定向枚举与 200 个随机可行点）；`:75` 至 `:79` 给出逐字输出，含 `m2=3 v=70.18: 可行顶点等价类 1 个；最大 S=2.243035561e-21（活跃集 ['G1','G2','W']）`。**脚本在 `/tmp/dtatk3/`，本轮不存在，未重跑。**`
   （对应 `30-proof-attempts/diophantine-transcendence/rebuttal-2.md` 的 `:73` 至 `:81`；**该脚本已不存在、不可复跑，也不构成全活跃子集穷举**，只作历史参考。）
3. `70-research/cycle-1/route-5.md:146`（sympy 工具链的组合侧核验，材料 299 行，md5 `252d55081913c623e69db9d7610edce3`）逐字：
   > `**顶点计数的组合侧核验（本轮脚本 E5，已跑）**：对 m₂ = 2 至 6，把「m₂ − 1 条链或回绕等式 + 和约束」的全部子集用 `sympy.linsolve` 解出，坐标都是 v·(δ 的 0 至 m₂ − 1 次幂) 的一个循环置换（例如 m₂ = 6 时六个活跃集分别给出指数序列 [0,1,2,3,4,5]、[1,2,3,4,5,0]、…、[5,0,1,2,3,4]）；而「全部链与回绕同时活跃」的解恒为原点，被 x_i ≥ 1 排除——这正是 `corr.txt:54` 至 `:63` 计数步的内容。**该核验是对照性的（m₂ ≤ 6），链上真实用到的 m₂ = 47 至 91 未穷举；但计数论证本身对任意 m₂ 有效（脚本对每个 n 都验证了「全活跃 ⟹ 原点」）。**`

### 4.5 阴性对照与其证据边界（`70-research/cycle-1/route-1.md`，457 行，md5 `7be71b78cd4c582c67fa1b80c88d27e2`）

1. `:319`（Step 9′）逐字：
   > `10. **Step 9′（已证，本轮新增；(P1) 不可省）**：当 `W < (δ^{m₂} − 1)/(δ − 1)`（即 v < 1）时，预测族的点 `y_1 = v < 1` 违反下界，不再是顶点。m₂ = 2、δ = 3/2、W = 3/2 的反例里，P 的顶点集合恰为 `{(1,1), (1,3/2), (3/2,1)}`，与预测族 `{(3/5,9/10), (9/10,3/5)}` 不相交；最大值取在含坐标 1 的顶点 (1,1) 上（`S(1,1) = 6`，另两个顶点各给 4.640754482）。脚本 [3] 精确枚举给出以上全部数值。`
2. `:320`（证据边界，产物里引用阴性对照时必须照抄的口径）逐字：
   > `    **证据边界**：这否证的是「分类」，不是「不等式」。同一配置下 `S(v 型点) = 9.281088094` 仍大于 `max_P S = 6`，本轮没有找到使 `S(y) ≤ S(v 型点)` 失效的实例；故本节只主张 (P1) 是**该证明路线**的实质前提（在勘误的应用里由 `c > 1` 满足），不主张 (P1) 是命题成立的必要条件。`
3. Step 8′ 的顶点识别一般证明（`:312` 至 `:317`，子问题 1、3 的纸面论证来源）要点逐字摘录：第 1 条 `记链约束行 `G_j := y_{j+1} − δy_j`…全部 m₂ 条 G 行线性无关：它们组成的矩阵为 `C = S_m − δI`…故 `det C = ∏_ζ (ζ − δ) = (−1)^{m₂}(δ^{m₂} − 1) ≠ 0``；第 2 条 `故一个顶点至多有 `m₂ − 1` 条链约束活跃；秩判据要求至少 m₂ 条活跃约束，可用的只有 m₂ 条链约束加和约束这 m₂ + 1 条，于是恰为「和约束活跃 + 恰 m₂ − 1 条链约束活跃」`；第 4 条 `解「和约束取等 + 除 `G_{j₀}` 外全部取等」的方程组……得 y 是 `(a, δa, …, δ^{m₂−1}a)` 的循环排列；和约束给 `a(δ^{m₂} − 1)/(δ − 1) = W`，即 `a = v`……故顶点集合恰为该族的 m₂ 个循环排列，且每个都是顶点。`
4. 一般证明的核对档位（`route-1.md:340`，失败点清单第 6 条）逐字：`**本轮未跑**：`margin_table.py`、三份重推脚本、任何 Lean 编译、sympy 交互式复算。`

### 4.6 勘误版重推里对「顶点句」的三处补充（`60-audits/hercher-t21/rederivation-erratum.md`，460 行，md5 `867d5fc42989fd27fee89982c3eef7c9`）

1. `:82` 至 `:84` 三条补充逐字：
   > `1. **窗口选择必须按 Σx 读**（原件逐字是「let the cycle be entered in such a way that this sum is maximal」，上文那句「this sum」指代的是刚写下的 x 和而不是 Σk）。按 Σx 读，回绕约束 (A6) 才成立，顶点识别才成立；按 Σk 读则不成立。`
   > `2. **「凸函数在（无界）多面体上取最大值于顶点」未加论证**。P 的回收锥含于非负卦限（绕链一圈得 x_i ≤ δ^{m₂}x_i，故任一回收方向 d_i ≥ 0），沿回收方向 S 不增，故 S 在 P 上取到最大值；凸函数在凸多面体上的最大值必有一个在顶点取到（若最大点不极端，凸性使其分解两端之一也最大，维数递减至顶点）。这两句合起来补上这一处。`
   > `3. **严格不等号使可行集非闭**（勘误写 x_{m−m₂+1} < δx_m）。由于最终只需要 S 的上界，把这条读成「≤」并把多面体闭化是合法的，也才能谈「顶点」。这一处属表述，不影响结论。`
2. `:88` 的诚实说明（一条被自己数值反例否证的替代路线）逐字要点：`该尝试在我自己的数值反例下失败——h(M) 关于 M **递减**，而 Σx ≥ W 只给出 M 的**上界**，方向相反`。
3. `:160` 至 `:184` 的顶点界数值检验（**抽样，非穷举**）逐字要点：`[2c] 顶点界数值检验`，四行 `m2 = 47 … 通过 118/118`、`m2 = 67 … 通过 48/48`、`m2 = 82 … 通过 53/53`、`m2 = 91 … 通过 49/49`；`:182` `四例的「最大 log2 超出」都小于 -1e9（即最好样本也远低于顶点值），全部通过。`
4. `:347` 至 `:364` 的状态登记逐字要点：勘误作为「已严格成立的证明」需要补三处（`:347` 逐字 `3. 但它作为「已严格成立的证明」需要补三处（窗口按 Σx 读、无界多面体上最大值在顶点的取到性论证、严格不等号读作 ≤），见第二节。`）；`:363` 逐字 `2. **最大值在顶点取到的论证**（无界多面体的处理）。……这属于**需补的引理**，不长但原文没有。`
5. **这是我的推断（材料标注）**：以上第 1 至 4 条说明「顶点识别」这条线在项目里的既有最高证据档是「纸面论证 + m₂ ≤ 10 的穷举 + 高 m₂ 的数值抽样」，与账本 `:109` 的口径一致；子问题 3 要的 m₂ = 12 穷举在既有材料里没有任何痕迹。

### 4.7 formal 目录的现状（子问题 1 的「或做成 Lean 引理」那一半）

1. `40-formal/lean/CollatzBasic.lean`（631 行）。**我是否亲自打开**：是（读了头部声明与 `grep` 结果）。关键逐字（文件头注释）：
   > `本文件是在一台**没有 Lean 工具链的机器**上写成的：写就时 `which lean`、`which lake`、`
   > ``which elan` 均无输出，`~/.elan` 与 `~/.lake` 均不存在。因此：`
   > `1. **本文件从未经过 Lean 编译器检验。** 下文注释里凡出现「证明已写」字样，都只表示`
   > `「作者认为该证明在语法与策略层面应当成立」，**不等于编译通过**。`
2. 本次实测：`grep -n "det\|rank\|顶点\|vertex" 40-formal/lean/CollatzBasic.lean` **零命中**（即 det 与秩论证不在该 Lean 文件里）；`which lean`、`which lake`、`which elan` 本次未重测（**未核实**，沿用文件自述）。

### 4.8 引用对不上的一处（留给攻击轮处置）

1. 本轨道 `plan.md:32` 称「`cycle-2/route-1.md:295`…各自声明未做全活跃子集穷举」。本次核对：`grep -n "活跃子集\|穷举" cycle-2/route-1.md` 只命中 `:297` 与 `:305`，`cycle-2/route-1.md` 全文（344 行）**没有出现「全活跃子集穷举」字样**；`:297` 讲的是另一种穷举（`K*` 格的收敛与半收敛清单穷举）。即：`plan.md:32` 对该文件的引用**我未能核实**（其余三处 `cycle-2/route-2.md:223`、`route-4.md:323`、`route-5.md:354` 的「未做全活跃子集穷举」逐字均在，本次已读）。

---

## 五、本次亲跑的锚点复核（命令与原始输出；本节的每个数字都是本次实测）

### 5.1 机器与工具链（替路线二的 C 实现铺路的一手探测）

1. `sysctl -n hw.ncpu` → `8`；`sysctl -n hw.physicalcpu` → `8`；`which cc gcc clang` → `/usr/bin/cc`、`/usr/bin/gcc`、`/usr/bin/clang`（三者都在）。
2. OpenMP 探针（探针源码 `/tmp/omp_probe.c`，8 行；内容即 `#include <stdio.h>`、`#include <omp.h>`、`int main(void) { printf("max_threads=%d\n", omp_get_max_threads()); return 0; }`）：
   1. `cc -fopenmp omp_probe.c -o omp_probe1` → 失败，逐字报错 `clang: error: unsupported option '-fopenmp'`（两行重复）。
   2. `cc -Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib -lomp omp_probe.c -o omp_probe2` → 成功（33496 字节可执行文件），运行输出逐字 `max_threads=8`。
   3. `gcc -fopenmp …` → 同样失败，逐字 `clang: error: unsupported option '-fopenmp'`（即本机 `gcc` 实为 clang 前端）。
3. GMP：`/opt/homebrew/include/gmp.h -> ../Cellar/gmp/6.3.0/include/gmp.h`（软链在位）；`/opt/homebrew/lib/libgmp.a -> ../Cellar/gmp/6.3.0/lib/libgmp.a`（静态库在位）。
4. 解释器与依赖（`"20-experiments/.venv/bin/python" -c "import sys, gmpy2, mpmath, z3; …"`）逐字输出：`python 3.12.7`、`gmpy2 2.3.2`、`mpmath 1.3.0`、`z3 5.3.1`。
5. **我的推断**：以上与 `plan.md:75` 的探测结论一致（它记「`cc -fopenmp` 报 unsupported option；改用显式路径编译成功，运行输出 `max_threads=8`；GMP 可用」），可视为该条记录的独立复现。

### 5.2 组合数与 72 分钟投影（复算）

1. `"20-experiments/.venv/bin/python" -c "import math; …"` 逐字输出：`C(21,10) = 352716`、`C(25,12) = 5200300`、`C(27,13) = 20058300`、`C(29,14) = 77558760`；投影复算 `C(25,12)*0.83e-3/60 = 71.93748333333333 min`。
2. 与账本的「5200300 个子集，投影约 72 分钟」（`ledger.md:25`）一致；13、14 档相对 12 档的组合数比 = 20058300/5200300 ≈ 3.857、77558760/5200300 ≈ 14.914（我的复算，属算术）。

### 5.3 δ 严格括号与四档阈值、v（精确有理复算）

命令：`"20-experiments/.venv/bin/python" -c "… from r2_common import delta_rigorous_bounds, v_vertex …"`（`sys.path` 指向 `cycle-1/scripts`）。逐字输出：

```text
D_LO7 = 126797/80000  D_HI7 = 7924813/5000000
lo float = 1.584962500000000052
m2=10: threshold = 169.316390  (P1: W>thr = True)  v = 11.812206  v>1 = True
m2=12: threshold = 427.925703  (P1: W>thr = True)  v = 4.673709  v>1 = True
m2=13: threshold = 679.246192  (P1: W>thr = True)  v = 2.944441  v>1 = True
m2=14: threshold = 1077.579742  (P1: W>thr = True)  v = 1.856011  v>1 = True
```

与 `plan.md:66` 至 `:71` 的六位小数摘要逐项一致；W = 2000 在 12、13、14 三档上都满足 (P1)（故 W = 2000 可直接用于升档，与 `plan.md:71` 一致）。
另：E10 的 W 与 v 精确复算（`Fraction`）逐字输出 `W(E10) = 630347359154513105681/40960000000000000000`、`bits: 70 66`、`v = 1`，与基线日志 `r2_b_out.txt:93` 的「70 位分子 / 66 位分母」相符。

### 5.4 阳性对照：m₂ = 10 重跑（本次亲跑，未改脚本）

1. 命令逐字：
   ```bash
   cd "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts" && \
     { time "…/20-experiments/.venv/bin/python" r2_j_independent_vertices.py A ; } \
     > "…/tracks/vertex-m12/cycle-1/materials/repro-r2_j_A-m2-10.txt" 2>&1
   ```
   退出码 0。原始输出全文落盘：`materials/repro-r2_j_A-m2-10.txt`（1238 字节，md5 `5d603d03a34ace5ad9107383d87fd0c1`）。
2. 结果逐字（与基线同格式）：
   > `    子集总数 C(21,10) = 352716，用时 65.4 s`
   > `    可行顶点数 = 10；与解析的 m2 = 10 个循环旋转相同 = True（解析集大小 10）`
   > `    每个顶点的（活跃约束法向量秩，活跃约束条数）= [(10, 10)]`
   计时行逐字：`"…/20-experiments/.venv/bin/python  63.86s user 0.49s system 98% cpu 1:05.66 total`（墙钟 1 分 05.66 秒）。
3. **与基线 `r2_j_A.txt` 的对拍（本次实测）**：把两边的用时数字统一替换后 `diff`（命令：`diff <(sed -E 's/[0-9]+(\.[0-9]+)? s/TS s/g; …' 基线) <(…同上… 重跑)`），**除我追加的 `time` 行外零差异**。即：352716、10 个循环旋转、证书 (10, 10)、独立性声明行逐字复现；唯一差别是耗时 65.4 秒对基线 62.3 秒（本次机器负载下的正常波动，我的推断），墙钟 65.66 秒对基线 62.49 秒。
4. **口径声明**：这是「同机、同脚本、同解释器」的复跑，属阳性对照的**材料级证据**；本轨道攻击轮路线一的标准闸门（含三向对照的判定）不由本文件宣布。

### 5.5 阴性对照：m₂ = 2、δ = 3/2、W = 3/2（本次亲跑）

1. 命令逐字：
   ```bash
   cd "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts" && \
     { time "…/20-experiments/.venv/bin/python" r1_selfcheck.py ; } \
     > "…/materials/repro-r1_selfcheck.txt" 2>&1
   ```
   退出码 0；原始输出落盘 `materials/repro-r1_selfcheck.txt`（92 行、5585 字节，md5 `0d1509629af57fa586edb666b2f19403`）；墙钟 `3.85s user … 4.471 total`。
2. 与 `route-1.md:319` 直接对应的逐字输出（`repro-r1_selfcheck.txt:22` 至 `:28`）：
   > `==== [3] 假设 v > 1 的必要性：v < 1 时预测族不是顶点集合 ====`
   > `   v = 3/5（小于 1；预测族里 y_1 = v，违反 y_1 >= 1）`
   > `   实际顶点集合 = (Fraction(1, 1), Fraction(1, 1))；(Fraction(1, 1), Fraction(3, 2))；(Fraction(3, 2), Fraction(1, 1))`
   > `   预测族 = (Fraction(3, 5), Fraction(9, 10))；(Fraction(9, 10), Fraction(3, 5))`
   > `   PASS 预测族与顶点集合不相交（分类在 v < 1 时失效）`
   > `   顶点上 S 值（降序）= (Fraction(1, 1), Fraction(1, 1))->6.0；(Fraction(1, 1), Fraction(3, 2))->4.640754482；(Fraction(3, 2), Fraction(1, 1))->4.640754482`
   > `   PASS 最大值取在含坐标 1 的顶点上`
   汇总逐字：`   失败项数 = 0` / `   全部通过 ? True`。
3. **与 `route-1.md:319` 逐项对上**：顶点集合 `{(1,1), (1,3/2), (3/2,1)}`、预测族 `{(3/5,9/10), (9/10,3/5)}`、S 值 6.0 与 4.640754482 两项、不相交判定——全中。该脚本 `[3]` 节自带的诚实注（逐字）：`   注：S(v 型点) = 9.281088094，本次未找到使断言反向失效的实例，故只主张「分类失效」，不主张「不等式失效」`（与 `route-1.md:320` 的证据边界同口径）。

### 5.6 边界档：E10（v = 1、证书 (5, 6)）（本次亲跑）

1. 命令逐字：
   ```bash
   cd "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts" && \
     { time "…/20-experiments/.venv/bin/python" r2_b_vertices.py ; } \
     > "…/materials/repro-r2_b_vertices.txt" 2>&1
   ```
   退出码 0；原始输出落盘 `materials/repro-r2_b_vertices.txt`（10854 字节，md5 `55eacc48888fe36adc1aaa2871c43bca`）；墙钟 `47.00s user 0.46s system 96% cpu 48.933 total`。
2. E10 段本次逐字输出（与 `r2_b_out.txt:91` 至 `:99` 同版式）：
   > `[E10 m2=5  δ_lo   W=(δ^5−1)/(δ−1)（阈值上的边界情形 v=1）]  δ = 126797/80000`
   > `    v = W(δ−1)/(δ^m2−1) 的分子位数 = 1，分母位数 = 1`
   > `    (L1) y_j = 1 不可行的初等引理判据 (δ^m2−1)/(δ−1) < W：70 位分子 / 66 位分母 vs W = 630347359154513105681/40960000000000000000  → False`
   > `    约简穷举：唯一可行顶点数 = 5；与解析的 m2 个循环旋转相同 = True（解析集大小 5）`
   > `    每个顶点的活跃约束法向量秩（应为 m2 = 5）：[(5, 6)]`
   > `    全穷举（C(2m2+1, m2) = 462 个子集，不依赖 L1）：可行顶点数 = 5；与约简一致 = True`
   > `    v ≈ 1.0（浮点仅作摘要）`
3. **与基线 `r2_b_out.txt` 的对拍（本次实测）**：`diff`（同样先把用时数字归一化）只报两处差异——E6、E7 两个汇总行的每档耗时（`3.2 → 3.3`、`41.4 → 44.8`）与我追加的 `time` 行；**E10 段（含证书 `[(5, 6)]`）逐字相同**。基线 `r2_b.time` 记 `real 44.08`，本次 `48.933 total`。

### 5.7 md5 与行数清单（引用纪律用；本次实测）

| md5 | 行数 | 路径（相对 `collatz-attack/`） |
|---|---|---|
| `4b8ce2a500d8ca9021fd0178deca637e` | 272 | `70-research/cycle-1/scripts/r2_j_independent_vertices.py` |
| `cfee819667c0883e73732f03d2dc8bef` | 244 | `70-research/cycle-1/scripts/r2_common.py` |
| `4d19e2fc351cea7a3b21e487a3c02e97` | 187 | `70-research/cycle-1/scripts/r2_b_vertices.py` |
| `dff8206d0047119cf0b65214ddb7c808` | 461 | `70-research/cycle-1/scripts/r1_selfcheck.py` |
| `8f8d0112668a88d0811f30cefa396bd1` | 16 | `70-research/cycle-1/scripts/results/verify-round2/r2_j_A.txt` |
| `440e8a872de8d71cacee663fab6536f3` | 3 | `70-research/cycle-1/scripts/results/verify-round2/r2_j_A.time` |
| `f3882451e5a45fc3cb5cce781f279e32` | 136 | `70-research/cycle-1/scripts/results/r2_b_out.txt` |
| `7be71b78cd4c582c67fa1b80c88d27e2` | 457 | `70-research/cycle-1/route-1.md` |
| `8937ec141e0fb783c4943bb13db7f7be` | 279 | `70-research/cycle-1/route-2.md` |
| `252d55081913c623e69db9d7610edce3` | 299 | `70-research/cycle-1/route-5.md` |
| `3edf2901ca21e9d80f767cb5c41d7b4b` | 118 | `70-research/cycle-1/summary.md` |
| `c0b077e6b5d3f0d0bf671e721941d632` | 394 | `70-research/cycle-1/materials.md` |
| `d759149ee03223a454014223f549e75d` | 964 | `70-research/cycle-1/verify.py` |
| `c238e1003f6cf3b1ee0fcf29ae82e58a` | 130 | `70-research/ledger.md` |
| `e88a8c5a37f0bf6d11cb795683f25638` | 45 | `70-research/learnings.md` |
| `6e85bc8d155018719d3eb1a74310324f` | 184 | `70-research/plan.md` |
| `6ad2e1e3ce6619bd9f31a7aab0f8d516` | 177 | `70-research/tracks/vertex-m12/plan.md` |
| `867d5fc42989fd27fee89982c3eef7c9` | 460 | `60-audits/hercher-t21/rederivation-erratum.md` |

本目录 `materials/` 下的本次产物（md5 | 字节 | 文件）：`f23d5f969116cb1af6e9b981b4b3ba7a | 124287 | corrigendum.pdf`；`993f3f5a93188076c60c7357ac552eeb | 4953 | corrigendum.txt`；`3e2377bef0b1c0435dc455c9bbee43a1 | 250655 | hercher5.pdf`；`d134d5822733bb647affacbaebb3b2f5 | 76688 | hercher5.txt`；`a7c7973e65a2b1ac6be465bd3170bb4c | 208467 | corr-p1-1.png`；`5ec441677d201128d324b32f702f1492 | 225046 | corr-p2-2.png`；`6ef685fc10469f668de61afd7eeb61e6 | 278243 | hercher-p13-13.png`；`6d9d688d783ef792a9fd6f4751ebfcef | 203847 | hercher-p14-14.png`；`5d603d03a34ace5ad9107383d87fd0c1 | 1238 | repro-r2_j_A-m2-10.txt`；`0d1509629af57fa586edb666b2f19403 | 5585 | repro-r1_selfcheck.txt`；`55eacc48888fe36adc1aaa2871c43bca | 10854 | repro-r2_b_vertices.txt`。

---

## 六、打不开的、没打开的、本次未跑的（逐条写明尝试过什么）

1. **前轮 `/tmp` 下的原件副本已全部不存在**：`/tmp/corr.pdf`、`/tmp/corr.txt`、`/tmp/h5.pdf`、`/tmp/h5.txt`、`/tmp/sidw144.pdf`、`/tmp/corrpage-1.png`、`/tmp/corrpage-2.png`、`/tmp/p14-14.png` —— 本次逐个 `ls`，全部报 `No such file or directory`（`cycle-1/materials.md:303` 至 `:315` 记录的抽取产物、渲染图与 `/tmp/dtatk3/` 同此命运）。**替代做法**：本次重新 `curl` 勘误与论文并复测 md5（`f23d5f96…`、`3e2377be…` 与记录一致），重抽文本、重渲染三页图；即凡是本文件的逐字引文，其底本都是本次自己的副本。
2. **`/tmp/dtatk3/`**（`rebuttal-2.md:73` 至 `:81` 的 `m2 = 12、91、300` 定向枚举脚本）：本机不存在（上一条已证），**未重跑、无法重跑**；其输出只以 `cycle-1/materials.md:274` 的转述形式存在，且它**不是**全活跃子集穷举。
3. **Lean 工具链**：本机 `which lean/lake/elan` 本次未重测（**未核实**）；`40-formal/lean/CollatzBasic.lean` 自述「从未经过 Lean 编译器检验」，且不含 det 与秩论证（`grep` 零命中）。故「把 det 与秩论证做成 Lean 引理」（`ledger.md:25` 的备选路径）在本机**不可行**，除非先装工具链。
4. **本次未跑（属攻击轮的任务，或代价超出材料收集）**：
   1. m₂ = 12（C(25,12) = 5200300）、13、14 的**任何**穷举或抽样——本次零执行；
   2. C 实现、OpenMP 分片穷举——**未写一行**（只做了工具链探针，见 5.1）；
   3. 「第二实现交叉核验」——未写；且如 2.3 第 5 条所言，现成两脚本共用 `r2_common` 底座，不算独立算术栈；
   4. B 段（z3 LRA）三份日志**未重跑**（只读了现成日志）；
   5. `cycle-1/verify.py`（964 行）**未跑**（只读了头部写作纪律）；
   6. arXiv v3（`https://arxiv.org/pdf/2201.00406v3`）与 SdW v1.44 **本次未下载**（前者与本疑点关系较远，后者本次未用到）；`cycle-1/plan.md:107` 至 `:109` 记有它们的现行可达性（HTTP 200）。
5. **无法核实项**：`route-2.md:271` 第 6 条的内联测速脚本（0.83 毫秒/个的来源）没有落盘，**本次无法复跑该测速本身**；只能复核「5200300 × 0.83 毫秒 ≈ 71.94 分钟」这一步算术（5.2）。
6. **本文件的边界**：我不是攻击轮，以上三次实跑（5.4、5.5、5.6）都用**同一台机、同一批脚本、同一解释器**完成；它们能支持「基线可复现」这一材料结论，**不能**替代攻击轮路线一的三向闸门判定，也不能替代路线三的双实现对拍。凡本文件与攻击轮报告冲突，以攻击轮按 `plan.md` 节八模板产出的、带完整依赖清单与边界声明的产物为准（这是我作为材料收集员的建议，不是判定）。

---

## 七、五条子问题的材料索引

1. **定义与锚点冻结**：1.1（勘误顶点句与约束表逐字）、1.2（Theorem 21 陈述与 v 公式）、1.3（(P1) 读法）、2.1（`constraint_list` 逐字：代码侧 2m₂ + 1 条的口径与回绕写法）、5.3（δ 严格括号、四档阈值与 v 的精确复算）、5.7（md5 清单）；勘误与代码在回绕号上的差别见 1.1 第 6 条与 4.6 第 1 条之 3。
2. **三向对照复现**：阳性 3.1 + 5.4；阴性 4.5 + 5.5；边界 E10 3.2 + 5.6；三份原始输出都在本目录 `materials/repro-*.txt`。
3. **m₂ = 12 主攻**：2.2 第 4 条（cases 只有 A1，m₂ = 12 无入口）、3.1 第 3 条（0.83 毫秒/个与 72 分钟投影的登记与不可复跑说明）、5.2（组合数）、2.2 第 3 条（枚举循环与判定行，C 实现要对齐的语义）、2.1（精确算术底座语义）。
4. **第二实现交叉核验**：2.3 第 5 条（现成两脚本共用 `r2_common`，不构成独立实现）、4.4 第 3 条（sympy 侧核验只到 m₂ = 6）、5.1（可用的编译工具链与 GMP、libomp）、5.7（要对拍的日志清单）。
5. **推档与边界**：`ledger.md:25` 与 `:109`、`learnings.md:45`、`summary.md:106`（不可达档与未证的既有措辞，均在 4.1 至 4.4）、5.2（13、14 档组合数与倍率）、1.1 与 1.2（覆盖参数 δ、W 的原文根据）、本轨道 `plan.md` 节八的边界声明模板（模板本体在 plan.md，本文件只提供其中每条的事实出处）。

---

## 八、本次实跑命令一览（便于逐条复跑；均在 `collatz-attack/` 下执行）

```bash
# 0. 原件下载与复测（本次实测：md5 与项目记录一致）
cd "<cycle-1>/materials"   # 即 70-research/tracks/vertex-m12/cycle-1/materials
curl -sL --max-time 90 -o corrigendum.pdf https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf
curl -sL --max-time 90 -o hercher5.pdf    https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf
md5 -q corrigendum.pdf hercher5.pdf    # f23d5f96…、3e2377be…
pdftotext -layout corrigendum.pdf corrigendum.txt
pdftotext -layout hercher5.pdf    hercher5.txt
pdftoppm -png -r 150 -f 1 -l 2 corrigendum.pdf corr-p && pdftoppm -png -r 150 -f 13 -l 14 hercher5.pdf hercher-p

# 1. 工具链探针（OpenMP 两条命令、GMP 在位、解释器依赖）
cc -fopenmp /tmp/omp_probe.c -o /tmp/omp_probe1                      # 预期失败：unsupported option
cc -Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib -lomp \
   /tmp/omp_probe.c -o /tmp/omp_probe2 && /tmp/omp_probe2            # 预期输出 max_threads=8
ls -la /opt/homebrew/include/gmp.h /opt/homebrew/lib/libgmp.a
"20-experiments/.venv/bin/python" -c "import sys, gmpy2, mpmath, z3; print(sys.version.split()[0], gmpy2.version(), mpmath.__version__, z3.get_version_string())"

# 2. 组合数与 δ、阈值、v（复算）
"20-experiments/.venv/bin/python" -c "import math; print(math.comb(21,10), math.comb(25,12), math.comb(27,13), math.comb(29,14))"
"20-experiments/.venv/bin/python" -c "import sys; sys.path.insert(0,'70-research/cycle-1/scripts'); \
  from fractions import Fraction as F; from r2_common import delta_rigorous_bounds, v_vertex; \
  lo,hi=delta_rigorous_bounds(10**7); print(lo,hi); \
  [print(m, float((lo**m-1)/(lo-1)), float(v_vertex(m,lo,F(2000)))) for m in (10,12,13,14)]"

# 3. 三档对照（本次亲跑；输出分别重定向到 materials/repro-*.txt）
cd "70-research/cycle-1/scripts"
{ time "…/20-experiments/.venv/bin/python" r2_j_independent_vertices.py A ; } > "…/materials/repro-r2_j_A-m2-10.txt" 2>&1
{ time "…/20-experiments/.venv/bin/python" r1_selfcheck.py              ; } > "…/materials/repro-r1_selfcheck.txt"  2>&1
{ time "…/20-experiments/.venv/bin/python" r2_b_vertices.py             ; } > "…/materials/repro-r2_b_vertices.txt" 2>&1

# 4. 与基线的对拍（用时数字先归一化，再 diff）
diff <(sed -E 's/[0-9]+(\.[0-9]+)? s/TS s/g; s/（[0-9]+ s）/（TS s）/g' \
        "…/verify-round2/r2_j_A.txt") \
     <(sed -E 's/[0-9]+(\.[0-9]+)? s/TS s/g; s/（[0-9]+ s）/（TS s）/g' "…/materials/repro-r2_j_A-m2-10.txt")
```

（上表里 `…/` 的完整前缀：`/Users/luna/Documents/math IA/collatz-attack/`；`<cycle-1>` 即 `70-research/tracks/vertex-m12/cycle-1`。本次三档实跑（第 3 段）三次都退出码 0；第 4 段的 `diff` 因报出差异而返回非零（这正是对拍要它做的事，差异内容见 5.4 第 3 条与 5.6 第 3 条）；另有一次非零退出是 `grep` 在印刷版里无命中（见 1.2 第 4 条），不是失败。以上均如实登记，不作「全部通过」的笼统措辞。）

---

**一句话状态**：本文件把 m₂ = 12 升档所需的「原文口径、代码语义、基线数字、纪律出处、工具链实体」都落成了带 md5 的逐字材料，并当场复现了三档对照（阳性 65.4 秒全对、阴性含 (1,1) 全对、E10 证书 (5, 6) 全对）；**m₂ = 12、13、14 的任何穷举、C 实现与第二实现，本次一律未跑、未写，属攻击轮任务**；勘误与论文的现行 URL 与字节数本次实测可用，可复跑。
