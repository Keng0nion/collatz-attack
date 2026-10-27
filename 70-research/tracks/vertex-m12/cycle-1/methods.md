# vertex-m12 轨道第 1 轮方法侦察（第 1 与第 2 节）

写作者：方法侦察员。日期：2026 年 10 月 27 日。本文件只写本轮要求的第 1、2 节，不含新数学结论，不裁决任何命题。

标注约定：【本次亲核】＝本会话内实际下载、抽取或运行并给出定位；【项目记录】＝仓库内文件的自述，其自身的「未核实」「未跑」标注一律保留；【未核实】＝本次没有做到或只见二手片段。外链本次均实测可达（被拦截者注明）；可达不等于读过全文。行号以本会话亲核的现行版本为准。

本文件所写的「这类问题」：命题 R(m₂, δ, W)——多面体 P(m₂, δ, W) 的全部可行顶点是否恰为 m₂ 个循环旋转——以及为核对它所需的机器机具（全活跃子集穷举、精确有理算术、确定性并行、第二实现）。P 的约束表、顶点族与可行性判定见 `70-research/cycle-1/scripts/r2_common.py:134` 至 `:180`；命题与参数锚点、依赖边界见本轨道 `plan.md:80` 至 `:88`。

## 一、文献机具与可达范围

排列：先通用顶点枚举机具（1 至 2），再本轨道主方法及其算术、并行底座（3 至 5），再相邻对照物与替代通道（6 至 7）。每条写「做什么、到达哪里、卡在哪里」。

1. **反向搜索与现成多面体软件（lrs、mplrs、cddlib）**。【本次亲核】lrs 主页（https://cgm.cs.mcgill.ca/~avis/C/lrs.html ，本次抓取）：lrslib 是「a self-contained C implementation of the reverse search algorithm for vertex enumeration/convex hull problems」，「All computations are done exactly in either multiple precision or fixed integer arithmetic」，「Output is not stored in memory, so even problems with very large output sizes can sometimes be solved」；功能表含「converting an H-representation to a V-representation and vice versa」与「Estimating the number of vertices/rays or facets」；v7.3 的 lrs 用「limited multithreading」，mplrs 用「openMPI」。lrs 用户指南（https://cgm.cs.mcgill.ca/~avis/C/lrslib/USERGUIDE73.html ，本次抓取）：算法即 Avis 与 Fukuda 1992（Discrete & Computational Geometry 8 卷 295 至 313 页），「implemented in rational arithmetic」，算术从 64 位升到 128 位与高精度（GMP 或内置）；自述极限逐字：「Since it is a pivot based method, lrs can be very slow for degenerate inputs」。cddlib 主页（https://people.inf.ethz.ch/fukudak/cdd_home/index.html ，本次抓取）：双子描述法（double description method of Motzkin et al.）。到达范围：一般实例上可直接由 H 表示算出全部顶点与射线，全程精确算术，是可复用通道。卡点：依赖外部实现的正确性与「直接算顶点」这条路本身；本轨道方案用的是自写实现（C 主实现加 Python 第二实现，`plan.md:105` 至 `:115`），现成软件在此只作对照登记。

2. **顶点枚举的复杂性口径（什么算「多项式」）**。【本次亲核】Fukuda 的 Polyhedral Computation FAQ（2022 年 1 月 15 日版，https://cddlib.github.io/polyhedral_faq/ ，本次抓取）：2.15 节把「多项式」定义为对输入与输出联合规模的多项式（「We say an algorithm α is polynomial if it runs in time bounded by a polynomial in d, n, m」，此处 m 为输出规模），并写「Under the nondegeneracy assumption (see 2.12), there is a polynomial algorithm for the convex hull problem」「In the general case, there is no known polynomial algorithm. The paper [ABS97] is an excellet article presenting how various algorithms fail to be polynomial, through ingenious constructions of "nasty" polytopes」（原文如此）。出处链（FAQ 参考表，本次抓取）：[AF92] Discrete & Computational Geometry 8 卷 295 至 313 页（1992）、[AF96] Discrete Applied Mathematics 65 卷 21 至 46 页（1996）、[ABS97] Computational Geometry: Theory and Applications 7 卷 265 至 302 页（1997）。到达范围：这是「基枚举何时能是多项式」的通行语境。卡点：一般（退化）情形无已知多项式算法且有系统性反例构造。标注：FAQ 为作者本人维护的技术文档，非同行评审。

3. **活跃集基枚举（本轨道主方法）**：任一顶点处存在恰 m₂ 条线性无关的活跃约束，故枚举全部 C(2m₂+1, m₂) 个子集不漏顶点（初等事实；项目自述 `r2_j_independent_vertices.py:9` 至 `:12`，两方向证明见 `route-1.md:310` 至 `:318` 的 Step 7 与 Step 8′）。实现：约束表 `r2_common.py:162` 至 `:180`，精确求解与秩 `:183` 至 `:217`，可行性 `:145` 至 `:159`，驱动 `r2_j_independent_vertices.py:92` 至 `:114`。到达范围【实测记录】：m₂ = 10、δ = 126797/80000、W = 2000 时 C(21,10) = 352716 个子集、62.3 秒、可行顶点数 10、与解析的 10 个循环旋转相同、证书 (10, 10)（`70-research/cycle-1/scripts/results/verify-round2/r2_j_A.txt:11` 至 `:13`；计时 `r2_j_A.time`：real 62.49、user 61.78、sys 0.34）。成本曲线【实测】：m₂ = 10 约 0.13 毫秒/个、m₂ = 12 约 0.83 毫秒/个（4000 个子集 3.32 秒），按 C(25,12) = 5200300 推得约 72 分钟（`route-2.md:271` 与 `:205`；`r2_j_A.txt:6` 同载「本次未跑」）。卡点：组合数按 m₂ 指数增长（m₂ = 20 为 C(41,20) ≈ 2.7×10^11，`r2_j_independent_vertices.py:12`、`learnings.md:45`），且每子集消元成本随 m₂ 上升（0.13 至 0.83 毫秒即两档实测）；12 档之后的可达性只能实测。另：现有主脚本仍是单进程 Python（`r2_j_independent_vertices.py:102` 的 `for S in combinations(...)`）。

4. **精确有理算术底座**：项目用 `fractions.Fraction` 分数消元（`r2_common.py:183` 至 `:217`）；δ 的严格括号只用整数幂比较（`r2_common.py:54` 至 `:70`）。【本次亲核】实跑 `delta_rigorous_bounds(10**7)` 输出 `D_LO7 = 126797/80000`、上界 `7924813/5000000`（命令与输出见文末）。C 侧两件经典工具：Bareiss 整数保持消元（只做整数运算、除法保证整除；摘要本次抓取自 https://en.wikipedia.org/wiki/Bareiss_algorithm ，百科级来源，非一手文献核对）与 GMP 大整数库（本机在位：`plan.md:75` 记 `/opt/homebrew/include/gmp.h` 与 `libgmp.a`）。到达范围：全部判决（秩、可行性、坐标相等）都在精确算术内完成，无舍入通道。卡点：速度（Python 单核 0.83 毫秒/个即第 3 条口径）；提速需编译语言与新算术栈（本轨道计划 C 加 GMP 或定长大整数 Bareiss，`plan.md:107`）。

5. **确定性并行分片**：组合可按字典序编号（combinadic，https://en.wikipedia.org/wiki/Combinatorial_number_system ，本次抓取摘录：「Distinct numbers correspond to distinct k-combinations, and produce them in lexicographic order」，百科级来源），把 C(2m₂+1, m₂) 切成互不重叠的编号区间分发，无重无漏。本机工具链【项目记录，本轨道先期实测】：Apple clang 报 `unsupported option '-fopenmp'`，改用 libomp 显式路径编译成功、输出 `max_threads=8`（`plan.md:75` 与 `:157`）；八核（`plan.md:74`：hw.ncpu = 8、Apple M2）。到达范围：八核化属本轨道待做项。卡点：分片正确性须自证（子集总数校验与每线程首末编号，`plan.md:107` 至 `:108`）；并行只压常数，不改变组合总数。

6. **同构对照物：项目自建的奇偶向量枚举**：`20-experiments/scripts/cycles_bs_enum.c` 按 Böhm 与 Sontacchi 判据枚举（实现要点 `20-experiments/findings/cycles.md:19` 至 `:28`；编译与命令 `:95`、`:104`）。到达范围：k ≤ 34 全枚举 3.44×10^10 个叶子、70.2 秒，结论「周期不超过 34 的非平凡整数环一个也没有」（`cycles.md:243`）。卡点（同文实测外推，`cycles.md:264`）：路径是 2^k，k = 40 约 37 分钟、k = 50 约 26 天；完备剪枝只砍多项式比例（实测 3 倍）。教训与本轨道同构：穷举类核对的覆盖档位由组合总数与逐项成本共同锁死。

7. **三条替代通道（交叉核验用）**：（一）z3 的 LRA 线性最优读数【项目记录】：对严格正权重 w 验证「P ∧ Σw·y < 诸旋转最小值」为 unsat，并取最优模型核对四项；m₂ = 20、47、91 三集，权重 14、12、10 个全部 unsat，发现顶点 10/20、12/47、9/91，用时 2.3、54.4、526.3 秒（`r2_j_independent_vertices.py:155` 至 `:261`；`route-2.md:217` 至 `:219`）。卡点（脚本自注 `:260` 至 `:261`）：有限权重取点不是法锥穷举，不能排除漏取的 w 暴露别的顶点。（二）形式化：把 det 与秩论证做成 Lean 引理是本轨道备选（`ledger.md:25`）；文献侧第三方 Lean 只到 m ≤ 82 且未覆盖勘误（`barriers.md:38`，项目笔记的转述记录）。卡点：本机无 Lean 与 Coq（`ledger.md:18`、`:109`），工作量未评估【未核实】。（三）第二实现：不同语言与算术栈的独立实现对拍是项目既定纪律（`plan.md:111` 至 `:115`）。

## 二、已知的不可能性结果

分三组：有出处的不可能性或硬度结论（1 至 3）、普适的算术与验证边界（4 至 5）、项目内已登记为失败、无效或不足的具体做法（6 至 10）。凡非定理者逐条标明。

1. **一般情形下「无界多面体的顶点生成」不可在多项式输出时间内完成（Khachiyan、Boros、Borys、Elbassioni 与 Gurvich，Discrete & Computational Geometry 39 卷 174 至 190 页，2008）**。【本次亲核】论文摘要逐字（大学著录页与 DIMACS 技术报告 2005-21 摘要页本次抓取；卷页与作者经 Crossref 本次核对）：「Given a feasible system of linear inequalities, generating all vertices of the corresponding polyhedron is hard. Yet, in the case of bounded polyhedra the complexity remains open. Equivalently, the complexity of generating vertices and extreme rays of polyhedra remains open.」同摘要另写「implying that (directed) negative cycles cannot be generated in polynomial output time, unless P=NP」。界线三条：其一，此结论约束一般实例的高效通道，不否定任何具体小实例的穷举（本轨道主攻恰是具体实例）；其二，本命题的 P 无界——本次实跑确认射线 (1, δ, …, δ^{m₂−1}) 满足全部齐次约束（m₂ = 10、12；命令与输出见文末），故该族实例原则上落在「unbounded」这一被指为难的类别；其三，有界情形与「顶点加极射线」情形的复杂性在该文标注为未决。用法：写进边界声明，不作为本轨道核对的反例。另须写明：本次只读摘要与著录，未读证明。

2. **一般（非退化之外）情形没有已知的多项式顶点枚举算法，且有系统性反例构造**。【本次亲核】Fukuda FAQ 2.15 与 [ABS97]（本次抓取）：非退化假设下有多项式算法（反向搜索），一般情形「no known polynomial algorithm」，[ABS97] 用「nasty polytopes」展示各算法为何失败。界线：一般算法侧的天花板；对本族的直接含义有限（已验证档的顶点证书恰为 (10, 10)，即活跃约束数等于秩等于维数），只提示「换现成软件也会撞经典陷阱」。

3. **「给定顶点列表已完备」这类核对在一般情形是 coNP 完全的**。【本次亲核】Fukuda FAQ 2.18（本次抓取）：多面体验证问题中「is P_H ⊆ P_V?」一侧「is known to be coNP-complete, due to [FO85]」（[FO85] = R. Freund 与 J. Orlin，Mathematical Programming 33 卷 133 至 145 页，1985；FAQ 参考表本次抓取），另一侧「is P_V ⊆ P_H?」容易（逐个检查顶点满足 H 表示即可）。界线：① FAQ 把讨论放在有界多面体口径，P 无界时该文未覆盖；② 本轨道不走一般判定器，而是「不漏顶点的组合枚举再对表」，不受该完备性难度约束；③ 它正面解释核对纪律：抽查与有限权重（第一节第 7 条）不能替代不漏顶点的枚举。

4. **浮点算术不能承担这类判定（普适结论加项目实测）**。【本次亲核】Kettner、Mehlhorn、Pion、Schirra 与 Yap，Computational Geometry 40 卷 61 至 78 页（2008，DOI 10.1016/j.comgeo.2007.06.003，Crossref 本次核对；预印本 PDF 本次下载并抽读摘要）：摘要逐字「The algorithms of computational geometry are designed for a machine model with exact real arithmetic. Substituting floating-point arithmetic for the assumed real arithmetic may cause implementations to fail.」【项目记录】numpy float64 在 2^53 以上整数不可分辨（`70-research/cycle-1/methods.md:114`，实测 `np.float64(2**53 + 1) == 2**53` 为 True）；z3 5.3.1 无 `Pow`、含 2^x 的编码返回 unknown（`70-research/cycle-2/methods.md:65`）。界线：浮点可作探针，进判决链不可以；本轨道全部判定走精确有理数。

5. **有限取点与网格不能升级为全称（项目纪律，不是定理；配一条反向实测）**：`learnings.md:44` 记「网格只能作机制检查或反例搜索，永远不能当全称命题的证据」。配套实测：在证书分辨率带内可以显式构造可行非顶点——沿两旋转连线取点，ρ = 1e−6 起各档未决（`route-2.md` 第 8.4 节 N11，`:246`：E2 在 ρ = 1e−6 处贴近度区间 [0.999997355857, 1.00000264415]）。故「搜索未决为 0」或「有限权重全 unsat」都不得读成几何结论；适用范围含第一节第 7 条的两条替代读数与一切抽样方案。

6. **依赖 (L1) 的约简穷举不构成独立核对（项目判定）**：m₂ ≥ 10 的约简穷举依赖 (L1)（y_j = 1 不可行这条初等引理），它「与解析一致」对顶点识别是循环性证据；本轨道要补的恰是不依赖 (L1) 的全活跃子集穷举（`r2_j_independent_vertices.py:5` 至 `:12`；`ledger.md:109` 的边界登记）。【项目记录】

7. **已登记为方向写反的具体做法：「用放大 δ 的有理替代做严格性检验」**：放大 δ 只让链约束更容易满足，通过它不蕴含真 δ 情形通过；要卡边界必须用 δ 的严格下界（如 126797/80000）做精确有理比较（`learnings.md:38`；其提到的 `route3_recheck.py` 第 6 节仍打印该错误方向，本次未打开该脚本、未重跑）。【项目记录】

8. **采样或随机化代替穷举不可接受（本轨道纪律）**：分片必须确定性、无重无漏，须以子集总数校验；任何快速通道预筛只允许判死（本轨道 `plan.md:165` 至 `:166` 第 4、5 条）。【项目记录】

9. **族层面的不可判定性只约束统一方法，不给 3x+1 本身任何结论**：Conway 1972（广义 Collatz 的判定问题不可判定）与 Kurtz 与 Simon 2007（{g : range(g) = ω} 为 Π⁰₂ 完备）——出处与界线见 `10-literature/notes/barriers.md` 第一节第 1、2 条与 `10-literature/notes/undecidability.md`（项目笔记的转述与核对记录，原文本次未开）。用法：只决定边界声明措辞——不得写成「机器核对证明了一般 m₂ 的顶点识别」。

10. **记录级天花板（原文自述，不是定理）**：Simons 与 de Weger 自述「要覆盖本质更大的 m 范围需要全新的想法」「no new ideas emerge」（转引 `barriers.md:36`；原文本次未打开）。界线：它约束循环排除主链的前沿，不约束本轨道的顶点核对；列此项是为边界声明提供定位——升一档核对是复核局部论证，不是推进前沿。

文末（本次实跑与来源可达性，供复核）：

1. 【本次亲核】实跑（命令照录）：在 `70-research/cycle-1/scripts` 下用 `20-experiments/.venv/bin/python` 执行内联脚本（heredoc），导入 `r2_common` 的 `delta_rigorous_bounds` 与 `constraint_list`。输出三行照录：`D_LO7 = 126797/80000  D_HI7 = 7924813/5000000`；`m2=10: 射线 (1,δ,...,δ^(m2−1)) 满足全部齐次约束 = True; 非零 = True`；`m2=12: 射线 (1,δ,...,δ^(m2−1)) 满足全部齐次约束 = True; 非零 = True`。
2. 外链可达性（本次）：lrs 主页、lrs 用户指南、Fukuda FAQ（cddlib.github.io）、cddlib 主页、DIMACS 2005-21 摘要页、Rutgers 著录页（Khachiyan 2008 摘要）、Kettner 等预印本 PDF、Wikipedia 的 Bareiss 与 combinadic 两条均抓取成功；Springer 的 Khachiyan 正文页与 INFORMS 的 Dyer 1983 页被反爬拦截（本次未打开，正文未用；Dyer 1983 只出现在 FAQ 参考表）。arXiv 的「An Automated Approach to the Collatz Conjecture」（Yolcu、Aaronson 与 Heule，2021）本次经 arXiv API 核到摘要（其可达范围是「nontrivial weakenings」，不给猜想本身），因与本轨道机具关系较远，未列入正文。
3. 范围声明：本文件只做机具与边界的清点；本轮未跑任何枚举或对照（属攻击轮）；所有「到达范围」数字均可按所给出处复跑；凡本次未亲跑者以【项目记录】【未核实】标注。

## 三、本机工具：能做什么、不能做什么

（本节为同一文件的追加轮，条目一律以 2026 年 10 月 27 日追加会话的实跑为准，命令与输出见本节末尾；第 1、2 节文末的「本轮未跑任何枚举」指上一次会话，追加轮另跑了下列探针，其中含一次 2000 子集的微型校准。解释器一律为 `20-experiments/.venv/bin/python`。）

1. **解释器与包版本**【本次亲核】：python 3.12.7；mpmath 1.3.0、gmpy2 2.3.2、sympy 1.14.0、z3 5.3.1、numpy 2.5.4。能：项目既有脚本都在这个解释器下运行（本节探针同此）。不能：本机没有 Lean 与 Coq（第 1 节第 7 条已登记）。
2. **mpmath（高精度实数）**：能：δ = log2 3 的 45 位复算（输出 `1.58496250072115618145373894394781650875981441`）；`mpmath.iv` 区间算术（设过 `mp.dps = 60` 后 iv 仍按自身精度给出宽度 8.881784197001252e-16，再设 `iv.dps = 60` 得宽度 4.667261458395856e-61）。不能：只在数值意义下成立，不是机器检验；`mp.dps` 与 `iv.dps` 是两套开关（同类陷阱项目笔记已记，见 `70-research/cycle-2/methods.md:61`）。对本轨道：可做余量与落点探针，不参与顶点判决。
3. **gmpy2（精确整数与有理数）**：能：精确分数（本次印 `7941964418702608664581/214072842063828923281`）；MPFR 定向舍入（本次对 2^74.772951607598 取 RoundDown 与 RoundUp，得 3.227760467642759e+22 与 3.227760467642791e+22，`hi>lo` 为 True）。不能：定向舍入给出的是浮点包络；要把某不等式写成「已证」，仍须自写单调化归（如 2^t 递增、3/(2^t−1) 递减），库不代替这一步。对本轨道：全部判决可用 fractions 或 gmpy2 精确完成。
4. **sympy（符号代数）**：能：写出引理代数骨架（本次把 3/(2^x−1) 的二阶导化简为 `3*2**x*(2**x + 1)*log(2)**2/(2**x - 1)**3`）。不能：判定含超越常数的命题——本次 `solve_univariate_inequality(2^x > 3)` 输出 `log(3)/log(2) < x`、`log(3)/log(2) > 3/2` 输出 `True`，这两条由数值求值驱动（本轮未核其内部依据），不得当证明。对本轨道：只用于骨架核对与措辞检查。
5. **z3（SMT）**：能：线性有理片段精确（本次 unsat）、多项式实数片段精确（本次 unsat）、可做 LRA 最优值与顶点读数（项目 N9，见第 1 节第 7 条）。不能：无 `Pow`（`hasattr(z3, "Pow")` 为 False，`2**c == 3` 编码返回 unknown），含 2^{x_i} 的目标函数不能直接交给它；读模型必须走 `RatNumRef.as_fraction()`（`route-2.md` 第 8.5 节）。对本轨道：可作线性可行性与最优值通道，不可作超越量通道。
6. **numpy（批量浮点）**：能：采样与反例探针（项目搜索脚本在用）。不能：本次 `np.float64(2**53 + 1) == np.float64(2**53)` 为 True——2^53 以上整数不可分辨，任何判决链不得经过它。
7. **cc 与 GMP、libomp（编译侧）**：能：Apple clang 21.0.0（`cc --version` 首行）编译通过（本次小程序输出 `cc ok 210`）；GMP 6.3.0 在位（`/opt/homebrew/include/gmp.h`、`/opt/homebrew/lib/libgmp.a`，Homebrew 符号链接），本次 `cc -O2 -I/opt/homebrew/include vm12_t2.c -L/opt/homebrew/lib -lgmp` 编译运行成功，输出 3^100+1（`515377520732011331036461129765621272702107522002`）与精确分数；libomp 在位（`libomp.a`、`libomp.dylib`），显式路径 `-Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib -lomp` 编译成功、运行输出 `max_threads=8`（八核）。不能：裸 `cc` 编译带 `#include <omp.h>` 报 `fatal error: 'omp.h' file not found`；C 侧无现成区间算术库，严格界要自写向外舍入或经 gmpy2 的 MPFR 包装。对本轨道：C 主实现（GMP 精确算术加 libomp 八核）的整条工具链本次实测在位。
8. **multiprocessing（Python 并行）**：能：写成文件并在 `if __name__ == "__main__"` 守卫下运行时 `Pool(4)` 冒烟通过（本次输出 `pool4: [0, 1, 4, 9, 16, 25, 36, 49] | cpu_count: 8`）。不能：从 stdin 管道运行的脚本里用 spawn 会失败——本次首跑实测 `FileNotFoundError`（找不到 `<stdin>` 对应的主模块路径），且 `Pool` 反复重启 worker 刷出 16 MB 以上重复回溯（终止时仍在增长；重跑改为文件加守卫后正常）。对本轨道：第二实现若用 multiprocessing，必须落成文件；分片正确性仍靠编号校验（第 1 节第 5 条）。
9. **一句总括**：本轨道需要的三种能力——精确有理判决、八核确定性穷举、第二套算术栈（C 加 GMP）——本机全部在位（本次探针；另有一次 2000 子集微型校准，实测 0.257 秒、0.129 毫秒/个，与 `route-2.md:271` 的 0.13 毫秒/个相符）；不够用的是形式化（无 Lean 与 Coq），以及把含 2^{x_i} 的判定交给数值或 SMT 通道的幻想。

## 四、本轮最可能产生增量的两个切入点

1. **八核 C 主实现先在 m₂ = 10 校准（与 `r2_j_A.txt` 逐项比对），再跑 m₂ = 12**。一句理由：12 档的瓶颈是每子集成本乘组合数（Python 单核 0.83 毫秒/个 × C(25,12) ≈ 72 分钟投影），而 GMP、libomp 与八核本次实测全部在位、按编号确定性分片可直接落地——这是把主攻压进本轮预算、并给 13、14 档真实倍率的唯一杠杆。
2. **第二实现对拍加编号化落盘（Python multiprocessing 加 Fraction 或 gmpy2，分块跑；任何分歧按子集编号定位）**。一句理由：单实现即使跑通也区分不了「实现错」与「定义错」，而编号化对拍能把分歧缩微到具体子集，是反例证书与「零 (L1)」口径的可信度支点。

（追加轮实跑记录，供复核。）

1. Python 探针：`"20-experiments/.venv/bin/python" /tmp/vm12_probe2.py`（文件加 `__main__` 守卫；含上列全部探针与 2000 子集校准），退出码 0，输出全文见上列引用；日志副本 `/tmp/vm12_probe2_out.txt`（tee 落盘）。首跑为 stdin 版，在 multiprocessing 处失败并刷屏，已终止并改为文件版。
2. C 侧探针：`cc --version | head -1`；`cc -O2 vm12_t1.c -o vm12_t1 && ./vm12_t1`；`cc -O2 -I/opt/homebrew/include vm12_t2.c -L/opt/homebrew/lib -lgmp -o vm12_t2 && ./vm12_t2`；`cc -Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib -lomp vm12_t3.c -o vm12_t3 && ./vm12_t3`。三个源文件：`/tmp/vm12_t1.c`、`/tmp/vm12_t2.c`、`/tmp/vm12_t3.c`。
3. 边界：本节结论只对本次命令与版本成立；未跑的写「本次未跑」；两套并行的端到端确定性分片（含中断续跑）属攻击轮，本节未测。
