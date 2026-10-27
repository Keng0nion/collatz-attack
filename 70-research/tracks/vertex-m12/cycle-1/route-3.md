# route-3 第二实现交叉核验（vertex-m12 首轮）

**路线名**：第二实现交叉核验
**日期**：2026 年 10 月 28 日
**执行者**：本工作流子代理（route-3 角色）
**本文件性质**：机器核对报告（附覆盖范围），不是证明。凡断言处逐条标注证据等级：**本次亲跑** = 本次执行命令所得；**文件亲读** = 本次逐行读过的文件（附路径与版本身份）；**未证/未跑** = 明写。

**一句话结论**：在冻结参数（δ = 126797/80000，W = 2000）下，m₂ ∈ {10, 12, 13, 14} 四档的全活跃子集穷举（本轨道两套互不共享代码的实现）都给出「可行顶点集恰为 m₂ 个循环旋转」；m₂ = 12 上两实现除顶点集、计数、证书全等外，5,200,300 个子集的分块校验和也逐块相等，且与另一实现（route-5）的检查点逐点精确相等；m₂ = 10、12 另在 δ 的严格上界 7924813/5000000 复跑，结论相同。**该范围之外（m₂ ≥ 15、其他参数取值、一般 m₂）仍属未证。**

---

## 一、要检验的精确陈述（先冻结，后开跑）

### 1.1 对象定义（本次亲跑独立复算，不 import 项目脚本）

窗口坐标 y = (y_1, …, y_{m₂}) ∈ R^{m₂}，多面体 P(m₂, δ, W) 由 2m₂ + 1 条约束给出（与 `tracks/vertex-m12/cycle-1/materials.md` 第 1.1 节的勘误原文、以及 `70-research/cycle-1/scripts/r2_common.py:162` 至 `:180` 的 `constraint_list` 同口径）：

1. (C1_j) y_j ≥ 1，j = 1..m₂（任意窗口坐标的下界）；
2. (C2_j) y_{j+1} ≤ δ·y_j，j = 1..m₂，指标模 m₂；j = m₂ 即回绕约束 x_{m−m₂+1} ≤ δ x_m；
3. (C3) Σ_j y_j ≥ W。

代码侧「回绕」并入 C2 链的末条（`r2_common.py:172` 至 `:177`），materials.md 第 1.1 节第 6 条已登记该写法差别（勘误原文把回绕单列且印严格号，项目按 `rederivation-erratum.md:83` 读成非严格号并闭化）。本报告一律按代码侧口径：25 条约束 = 12 条 C1 + 12 条 C2（含回绕）+ 1 条 C3。

### 1.2 参数锚点（本次亲跑，整数幂，无浮点）

1. δ 的严格下界：15849625/10^7 = **126797/80000**，由 2^15849625 < 3^10^7 保证。每次实现一实跑的 JSON 里都有锚点行，逐字：`δ 锚点复核（整数幂，无浮点）：2^15849625 < 3^10000000 < 2^15849626 全部为真 = True；δ 下界 = 126797/80000 = 1.5849625000（浮点仅作摘要）`（出处：`results/route3_impl1_m10.json` 的 `delta_anchor_line` 字段）。
2. δ 的严格上界：15849626/10^7 = **7924813/5000000**，由 3^10^7 < 2^15849626 保证（同上锚点行；另见 `scripts/route3_defs.py` 的 `delta_hi`）。
3. W = 2000（整数，精确）。
4. 顶点坐标的候选公式：v = W(δ−1)/(δ^{m₂}−1)，解析族 = { v·(δ^r, δ^{r+1}, …, δ^{r+m₂−1}) : r = 0..m₂−1 }。

### 1.3 待检验命题（本核对的对象）

对 m₂ ∈ {10, 12, 13, 14} 与上述 (δ, W)：**P 的顶点集恰为解析族的 m₂ 个循环旋转**；每个顶点的活跃约束法向量秩 = m₂，活跃约束条数给出证书。

### 1.4 与「顶点引理已证」的区别（禁止误读）

本报告检验的是**有限档位、有限参数上的机器核对**。它不证明一般 m₂ 的顶点识别命题，也不把勘误原文的顶点句升级为定理。一般命题的当前最高证据档是项目既有的纸面论证（`70-research/cycle-1/route-1.md` 的 Step 8′），本报告不改变这一点。

---

## 二、方法：两套实现与一条独立复核路径

### 2.1 三件产物（全部本次新写，全部不 import r2_common）

| 文件（`tracks/vertex-m12/cycle-1/scripts/`） | 角色 | 判定路径 | 算术栈 |
|---|---|---|---|
| `route3_impl1_mpqscan.py`（275 行） | 实现一：全活跃子集穷举 | 通用线性代数：高斯若尔当消元求唯一解 | 系数整行放大后 gmpy2.mpq（GMP 有理数） |
| `route3_impl2_struct.py`（318 行） | 实现二：全活跃子集穷举 | 图结构传播：链方程分量 + 自由度计数 + 和方程定值 | fractions.Fraction + 整数交叉相乘 |
| `route3_defs.py`（274 行） | 冻结定义与公共工具 | 约束表、解析族、组合编号、校验和 | Fraction + 整数幂（gmpy2） |

配套：`route3_xcheck.py`（逐子集与逐分块对拍器，142 行）、`route3_verify.py`（候选证书独立复核器，150 行，V1 至 V6 共 7 项检查）、`route3_vs_other_compare.py`（与 route-5 检查点逐点对拍，84 行）、`route3_bareiss_probe.py`（被弃方案的缺陷定位与自我更正，114 行）。

### 2.2 显式依赖清单（「不依赖任何引理」落到清单，不靠口头担保）

**搜索本体（决定哪些子集给候选）用到的全部东西**：

1. 约束表：勘误原文的约束表（materials.md 第 1.1 节逐字），在本轨道 `route3_defs.constraint_rows` 里独立转写；
2. 精确有理算术：gmpy2.mpq（实现一）、fractions.Fraction 与整数交叉相乘（实现二）；
3. 线性代数（实现一）：方阵「某列在剩余行里全零 ⟹ 奇异」。对求满秩解这是判据而非引理式假设：此时行阶梯形剩余子矩阵含零列，秩 < n；
4. 初等图论（实现二）：见 2.3 的五条，逐条给出证明要点；
5. 组合枚举完备性：顶点处存在大小 m₂、秩 m₂ 的活跃子集（证明见 4.2），故枚举全部 C(2m₂+1, m₂) 个子集不漏顶点；反之，满秩子集的唯一解若可行必是顶点。

**明确不用的东西**：不用 (L1)（「y_j = 1 不可行」这条初等引理）、不用 v 或解析族的任何数值信息参与搜索判定（解析族只在最后作对照集）、不用凸性论证、不用顶点引理的结论、不用模素数预筛或任何浮点筛选（没有任何「先粗筛后精验」通道）。

**实现二用到的五条初等事实（每条附证明要点；证明在 4.3 节）**：

1. 若 m₂ 条链约束全活跃，则链方程绕圈给出 y = 0，被 C1 排除；
2. 链方程边集去掉 k 条边后碎成 m₂ − k 条互不相交的有向路径（分量），每个分量由一个基点值决定全部坐标；
3. 分量内有 0 个 C1 钉 ⟹ 留一个自由度；恰 1 个 ⟹ 基点被钉死为 δ^{−d}；≥ 2 个 ⟹ 两式给出 δ 的不同整数幂相等，与 δ > 1 矛盾；
4. 记 f 为自由度个数（无 C1 钉的分量数），则链部分解空间维数 = f，系数秩 = m₂ − f；
5. 含 C3 行时和泛函在每个自由分量上的系数是 Σ δ^t > 0，故和方程必把维数降 1：唯一解 恰为 f = 1；f = 0 时和方程是相容性条件，须精确验 Σ y = W。

**这一条与本轨道纪律的对应**：`learnings.md:41` 要求「不依赖任何引理」落到显式依赖清单加代码审计（原文另见 `tracks/vertex-m12/plan.md` 第 127 行至第 137 行的避开清单第 6 条）。上面的清单即该要求的落点；实现二的第 1 至 5 条不是「引理式黑箱」，而是可以在本报告 4.3 节逐条读完的初等论证。

### 2.3 分片、编号与不一致定位

1. 子集用组合字典序编号（与 `itertools.combinations` 的输出次序逐项一致，本次亲跑核对 rank、unrank、next 三者，见 3.1）；
2. 全空间按编号切成确定性分片，各分片独立跑，父进程校验「各分片 count 之和 = C(2m₂+1, m₂)」；
3. 每个分片输出一个 64 位**可交换校验和**：agg = Σ_{子集} mix64((mix64(rank) ≪ 1) ⊕ code)，其中 code = 0（不出候选）或顶点坐标串的 FNV1a 码（出候选）。两实现共用同一口径，故可逐块对拍；不一致时分块校验和先定位到分片，再由 `route3_xcheck.py --mode block` 逐子集对拍定位到**子集编号**；
4. 候选顶点另行输出：捕捉它的子集编号与内容、精确坐标串、活跃约束条数、见证秩。

### 2.4 机器与工具链（本次亲跑）

1. `sysctl -n hw.ncpu` = 8，`sysctl -n hw.physicalcpu` = 8；
2. 解释器：`20-experiments/.venv/bin/python`，`sys.version` = 3.12.7；`gmpy2.version()` = 2.3.2，`gmpy2.mp_version()` = GMP 6.3.0；
3. 口径提醒：本机同时段有其它 actor 的重负载扫描（`uptime` 实测 load average 一度到 214.63），所有墙钟时间都在该背景下测得；本报告不把耗时当作干净环境下的性能结论。

---

## 三、实跑结果

### 3.1 自检（先于任何判定，本次亲跑）

1. **组合编号自检**：`route3_defs` 的 `comb_rank_lex`、`comb_unrank_lex`、`comb_next_lex` 三者与 `itertools.combinations(range(n), r)` 的次序逐项比对，n = 7、r = 3 全空间 35 个组合三项全一致（输出逐字：`rank 一致: True  unrank 一致: True  next 一致: True  总数: 35`）；全量扫描时父进程另校验分片计数之和等于 C(25, 12) = 5200300。
2. **求解器自检（这条挖出一个真缺陷，见第五节）**：随机整数方阵（n = 2 至 6，元素 ±20）上把「Bareiss 无分数消元 + 精确回代」与 Fraction 参考解对照，不一致立即被抓住（第 1 组就对不上）。诊断脚本扩到 4000 组并做三档开关实验，定量结论（`results/route3_bareiss_probe_out.txt` 逐字）：A 段（复现第一版）`不整除合计 = 305；其中「失败前一次行交换都没发生」的 = 229；发生过行交换的 = 76`；B 段（修正行更新，仍允许行交换）`结局分布 = {'ok': 3994, 'singular': 6}`，**零不整除**；C 段（修正且禁止交换）有 106 组需要交换。据此把缺陷定到「f == 0 跳过整行」这条实现细节，并据此弃用该方案、实现一改用 gmpy2.mpq（无整除约定，正确性论证更短）。
3. **两实现逐子集对拍（小档）**：m₂ = 2、3、4、5、6、7、8 的**全部**子集逐项比较判定与候选点串，合计 33094 个子集，**不一致 0**（逐字：`m2=2: … 不一致 0，候选 impl1=2 impl2=2`，…，`m2=8: … 不一致 0，候选 impl1=8 impl2=8`）。

### 3.2 阳性对照：m₂ = 10（全扫，两实现，与项目基线对拍）

| 项 | 实现一（mpq 消元） | 实现二（结构传播） | 项目基线 `r2_j_A.txt` | route-5 的独立实现 |
|---|---|---|---|---|
| 子集总数 | 352716 | 352716 | 352716 | 352716 |
| 墙钟 | 22.182 s（6 进程） | 5.692 s（4 进程） | 62.3 s（原基线，单进程）；65.4 s（材料重跑） | 3.34 s（8 进程） |
| 奇异 / 唯一解不可行 / 候选子集 | 295780 / 56926 / 10 | 只记候选：10 | 只记候选：10 | 295780 / 56926 / 10 |
| 可行顶点数（去重） | 10 | 10 | 10 | 10 |
| 与解析族相等 | True | True | True | True |
| 证书（活跃秩，活跃条数） | 全部 (10, 10) | 全部条数 10，见证秩 10 | `[(10, 10)]`（逐字） | `[[10, 10]]` |
| 分片校验和 agg | `2bde15694dbbcfa9` | `2bde15694dbbcfa9` | 无此字段 | 无此字段 |

判读（口径写清）：**与项目基线可比的三项逐字相符** —— 基线为 `70-research/cycle-1/scripts/results/verify-round2/r2_j_A.txt`（16 行、md5 `8f8d0112668a88d0811f30cefa396bd1`，本次逐行读过），其 `:11` 至 `:13` 逐字为 `子集总数 C(21,10) = 352716，用时 62.3 s`、`可行顶点数 = 10；与解析的 m2 = 10 个循环旋转相同 = True（解析集大小 10）`、`每个顶点的（活跃约束法向量秩，活跃约束条数）= [(10, 10)]`；本实现给出去重顶点 10、与解析族相等 True、每顶点活跃条数 10（证书的秩 10 由 `route3_verify.py` 独立重算确认）。**基线的「奇异 / 不可行」两类计数不可比**：基线的 `solve_exact` 把「解不唯一」与「不相容」都返回 None（`r2_common.py:212` 至 `:213`），不分离两类；本实现在这一点上比基线更细，其两类计数与 route-5 的独立实现三方一致（295780 / 56926）。

### 3.3 主结果：m₂ = 12（全扫 5200300 个子集）

1. **实现一**（`results/route3_impl1_m12.json`）：用时 267.481 s（5 进程）；分检：奇异 4752735、唯一解不可行 447553、候选子集 12；去重顶点 12 = 解析族 12（相等 True）；每个顶点活跃条数 12；agg = `a5eb2b93d333ca02`；分片 21 块。
2. **实现二**（`results/route3_impl2_m12.json`）：用时 51.832 s（5 进程）；候选子集 12、去重 12 = 解析族 12（相等 True）；每顶点活跃条数 12、见证秩 12（`candidates_with_wrong_rank` 为空）；agg = `a5eb2b93d333ca02`；分片 21 块。
3. **两实现逐项对拍**（`results/route3_xcheck_m12_compare.json`）：`agg_equal: True`、`candidate_point_sets_equal: True`、`candidate_ranks_equal: True`、`active_count_equal: True`、`n_blocks_with_agg_mismatch: 0`（21 块逐块相等）、候选子集编号列表逐位相同（rank 5200288 至 5200299）。
4. **候选证书独立复核**（`results/route3_verify_impl1_m12.json`、`…impl2_m12.json`）：12 个候选全部通过 V1 至 V6（编号自洽、见证子集满秩、见证方程 A_S·y = b_S 精确成立、全部 25 条约束精确可行、属于解析族、活跃条数与秩独立重算一致），旋转号恰为 0 至 11。
5. **与另一实现（route-5）对拍**：两侧顶点坐标串**逐点精确相等**（各 12 个点，差集为空，`results/route3_vs_other_m12.json` 与 `…_impl1.json`）；route-5 的日志（`results/logs/r5_full_m2_12_mpq.log`）逐字给出同一分检计数 `n_rank_def 4752735、n_infeasible 447553、n_feasible_subsets 12`，证书 `[[12, 12]]`，用时 122.89 s（8 进程）。
6. **捕捉次数**：每个顶点恰被 1 个活跃子集捕捉（两边一致），即 12 个顶点的活跃集大小都是 12，与证书 (12, 12) 自洽（活跃集大小 12 ⟹ 恰 1 个大小 12 的子集含于其中）。

### 3.4 推档：m₂ = 13、14（实现二全扫；与 route-5 逐点对拍）

| m₂ | 子集总数 | 本轨道实现二用时 | 候选子集 | 去重顶点 | 与解析族相等 | 证书 | agg | route-5 用时 / 分检 | 逐点对拍 |
|---|---|---|---|---|---|---|---|---|---|
| 13 | 20058300 | 38.643 s（5 进程） | 13 | 13 | True | 全部 (13, 13) | `5d4690cf6e0b1ff3` | 516.4 s（8 进程）/ 18811533、1246754、13 | 13 对 13，集合相等，差集空 |
| 14 | 77558760 | 592.974 s（5 进程） | 14 | 14 | True | 全部 (14, 14) | `91da64fcca9aa0a9` | 2912.24 s（8 进程）/ 74098262、3460484、14 | 14 对 14，集合相等，差集空 |

13、14 两档的候选证书也全部通过 `route3_verify.py` 的独立复核（`results/route3_verify_impl2_m13.json`、`…m14.json`，旋转号分别恰为 0 至 12 与 0 至 13）。

### 3.5 参数端点稳健性：δ 的严格上界（新增，本次亲跑）

1. m₂ = 10，δ = 7924813/5000000（严格上界），W = 2000：全扫 352716 个子集，4.213 s，候选 10 = 解析族 10（相等 True），候选证书独立复核全通过（旋转号 0 至 9）。
2. m₂ = 12，δ = 7924813/5000000，W = 2000：全扫 5200300 个子集，45.56 s，候选 12 = 解析族 12（相等 True），每顶点活跃条数 12，agg = `2c994b8a9308b2a0`（与下界跑的 `a5eb2b93d333ca02` 不同是应该的：δ 变了两边判定的判定码整体不同，本行只做端点对照，不与下界跑比校验和），候选证书独立复核全通过（旋转号 0 至 11）。
3. 口径：真实 δ = log₂3 落在 [λ, μ] = [126797/80000, 7924813/5000000] 内（两端分别由 2^15849625 < 3^10^7 与 3^10^7 < 2^15849626 保证）。本核对在**两个端点各做了一次全扫**；**区间内部的逐点检验未做**（见第七节边界声明第 2 条）。

---

## 四、编号论证（每一步标注：已证 / 机器核对（附范围）/ 缺口 / 未证）

### 4.1 定义与锚点冻结（已证，本次亲跑）

多面体定义如 1.1；δ 的两个端点由整数幂比较 2^15849625 < 3^10^7 < 2^15849626 现场复核（1.2）；W = 2000 为整数，无精度问题。**先冻结后开跑**：四次主实跑（实现一的 m₂ = 10、12 与实现二的四档）全部在冻结参数下进行，输出 JSON 自带 `delta` 与 `W` 字段，复核器一律以被核对文件自带的参数为准（自足复核，避免把核对对象的参数换成本文件的默认值）。

### 4.2 枚举的完备性（已证，初等线性代数）

**引理 A（不漏顶点）**：设 y 是 P 的顶点。则 y 处活跃约束的法向量张成 R^{m₂}（LP 基本定理：多面体的极点是基本可行解，即活跃约束中可取 m₂ 条线性无关者）。取其中线性无关的 m₂ 条，得大小恰为 m₂、秩恰为 m₂ 的子集 S。由于 y 满足所有这些约束取等，A_S y = b_S，且 A_S 可逆，故 y 是 A_S y = b_S 的唯一解。**故枚举全部 C(2m₂+1, m₂) 个大小 m₂ 的子集并解方程，必能见到 y。**

**引理 B（候选即顶点）**：若某子集 S 的 A_S 可逆、其唯一解 y 满足 P 的全部约束，则 y 处活跃约束 ⊇ S，秩 ≥ 秩(S) = m₂ = dim，仍由同一基本定理，y 是 P 的顶点。

**注**：A、B 只使用「极点 = 基本可行解」这一标准定理。两实现都不含任何结构剪枝（实现二的五条结构事实只是把「解方程并查秩」换一种算法来算同一个判定，见 4.3 与 4.4），故完备性对两实现都成立。

### 4.3 实现二的结构判定与被检验的数学定义的等价（已证，逐条）

设子集 S 分解为 C1 行集合 A1、C2 行集合 A2、是否含 C3 行 a3，|S| = m₂。

1. **|A2| = m₂ 时无候选（已证）**：链方程绕圈给出 y₁ = δ^{m₂} y₁，而 δ > 1 ⟹ δ^{m₂} − 1 ≠ 0 ⟹ y = 0，被 y_j ≥ 1 排除（若另有 C1 行则更直接矛盾）。
2. **分量结构（已证）**：把「j ∈ A2」看成边 j → j+1。每个节点出度、入度各至多 1，故 |A2| < m₂ 时整个有向图碎成 m₂ − |A2| 条互不相交的有向路径（每个缺边处「切断」一次）；路径 v₀ → v₁ → … 上 y_{v_t} = δ^t y_{v₀}，即每个分量由基点值一个参数决定。
3. **钉的三分类（已证）**：分量内 C1 行 0 个 ⟹ 留一个自由度；恰 1 个（距基点 t）⟹ 基点值 = δ^{−t}，全分量随之确定；≥ 2 个 ⟹ 两式给出 δ^{t₁} = δ^{t₂} 而 t₁ ≠ t₂，与 δ > 1（δ 的整数幂只有 k = 0 时为 1）矛盾 ⟹ 方程组不相容。
4. **秩与自由度（已证）**：链加钉的方程组解空间维数 = 自由度个数 f，故其系数秩 = m₂ − f。
5. **含 C3 行时的计数（已证）**：和泛函在任一自由分量上的系数是 Σ_{节点} δ^{距离} > 0（δ > 0），故它在解空间上非常值，加入和方程必使维数降 1。于是：a3 = 1 时唯一解 恰为 f = 1（此时基点值 = (W − 已钉分量之和) / 该分量系数，精确有理）；a3 = 0 时唯一解 恰为 f = 0。f ≥ 2（含 C3）或 f ≥ 1（不含 C3）一律非唯一，弃。
6. **f 与 |S| 的关系自洽（已证，附带检查）**：a3 = 1 时 |A1| + |A2| = m₂ − 1，故 f ≥ m₂ − (m₂ − 1) = 1 恒成立，这与第 5 条的「唯一解 恰为 f = 1」不冲突；a3 = 0 时 |A1| + |A2| = m₂，f = 0 可达。
7. **实现二的代码与上述六条一一对应**：`judge_struct` 里 `if not comps: return nocand`（第 1 条）、分量行走（第 2 条）、`len(pins) > 1 → nocand` 与 `dq(t − d)`（第 3 条）、`len(free)` 与 a3 的分支（第 4、5 条）；候选另查全部 25 条约束（精确）与活跃条数。

### 4.4 「判定程序 = 数学定义」的接口等价性（已证 + 机器核对）

1. **可行性**：两实现都用精确有理数比较 25 条约束（实现一用 mpq，实现二用整数交叉相乘与 Fraction 求和），与 1.1 的定义逐字对应（C2 含回绕）。**已证**（代码逐行读过）。
2. **唯一解判定**：实现一用消元（该列在剩余行全零 ⟹ 奇异），实现二用 4.3 的计数；两者的相等性是**机器核对**：m₂ = 2 至 8 的全部 33094 个子集逐项一致、m₂ = 10 的全部 352716 个子集逐项一致、m₂ = 12 的 5,200,300 个子集分块校验和逐块一致（另见 3.3 第 3 条）。
3. **顶点集的比较对象**：解析族由 v = W(δ−1)/(δ^{m₂}−1) 与 δ 的幂生成（`route3_defs.analytic_vertices`），它是**被检验的断言**，不参与搜索判定。

### 4.5 主判定（机器核对，附范围）

对 δ = 126797/80000、W = 2000、m₂ ∈ {10, 12, 13, 14}：P 的顶点集**恰为** m₂ 个循环旋转，逐档的候选子集数、去重顶点数、与解析族的集合相等判定、每顶点证书（活跃秩 = m₂、活跃条数 = m₂）见第三节表格；每个候选另经 `route3_verify.py` 的 V1 至 V6 独立复核（见证子集满秩、A_S·y = b_S 精确成立、25 条约束精确可行、属于解析族、编号自洽、证书一致）。**范围外的推论一律无效**（见第七节）。

### 4.6 参数端点（机器核对，附范围）

δ 取严格上界 7924813/5000000 时，m₂ = 10、12 两档结论相同（3.5 节）。区间 [λ, μ] 内部未逐点检验；「顶点集在区间上恒定」这一命题本轮**未证**（它需要对全部子集的判定条件在区间上做符号分析，远超本轮工作量）。

### 4.7 一般 m₂ 与应用档（未证）

1. 一般 m₂ 的顶点识别仍是纸面论证（`70-research/cycle-1/route-1.md` 的 Step 8′），**未形式化、未证**；
2. m₂ = 15 及以上未跑；m₂ = 20、47、91 的全活跃子集穷举组合规模不可达（C(41,20) ≈ 2.7e11 等，见 `learnings.md:45`），本报告只把它们写成核对边界；
3. 「顶点引理已证」这一说法在本轮产物中**不成立**：本轮成果是四档（加两个 δ 上界档）机器核对，不是定理。

### 4.8 与原命题的关系（标注「等价」与「不等价」）

1. 本轮检验的是**冻结参数下的有理性命题**「P(m₂, δ₀, 2000) 的顶点集 = 解析族」，与勘误原文的一般命题（任意 m₂、δ = log₂3 真实值）**不等价**：前者是后者的有限实例。
2. 4.2 的两条引理是**关于枚举完备性的初等事实**（已证），但它们不构成「顶点识别命题」的证明：它们只说明「枚举能看到顶点」，真正的结论（顶点集恰为解析族）由有限档位的穷举给出。

### 4.9 逐子集全量对拍（本次亲跑；本路线最强的「两实现相等」证据）

1. m₂ = 12：`route3_xcheck.py --mode allsubsets --m2 12` 对**全部 5,200,300 个子集**逐项比较两实现的判定（类别与候选点串），结果逐字：`"n_compare": 5200300, "n_mismatch": 0, "n_candidates_impl1": 12, "n_candidates_impl2": 12, "first_mismatches": []`（`results/route3_xcheck_m12_allsubsets.json`）；
2. m₂ = 10：同样方式对全部 352716 个子集，`"n_mismatch": 0`（`results/route3_xcheck_m10_allsubsets.json`）；
3. m₂ = 2 至 8：33094 个子集，全零不一致（3.1 第 3 条）。

结论：在 m₂ ≤ 12 的这些档位上，「两实现的判定逐子集相同」不是抽样断言，而是逐项核对过的。

---

## 五、失败点清单（把失败定到具体步骤与具体不等式）

1. **已弃方案：Bareiss 无分数消元配部分主元（实现一初版）。** 缺陷定到一条具体实现细节：第一版在「该行在当前列已为零（f == 0）」时**跳过整行更新**，而 Bareiss 每一步要把整行乘上主元再除以上一步主元，f == 0 时也必须缩放；跳过就破坏了「第 k 步条目 = 相应子式」的不变量，`//` 的取下整把不整除静默变成错解。定量诊断（`route3_bareiss_probe.py`，本次亲跑，输出落盘 `results/route3_bareiss_probe_out.txt`）：A 段（复现第一版）`结局分布 = {'inexact-matrix': 295, 'inexact-rhs': 10, 'ok': 3689, 'singular': 6}`，`不整除合计 = 305；其中「失败前一次行交换都没发生」的 = 229；发生过行交换的 = 76`；B 段（修正行更新）`{'ok': 3994, 'singular': 6}`，**零不整除**；C 段（修正且禁止交换）`{'needs-swap': 106, 'ok': 3889, 'singular': 5}`。
   **并更正一条早期错误结论**：我一开始把成因记成「行交换与 Bareiss 的精确整除不变量不相容」，B 段实验（修正行更新后允许行交换仍零不整除）**否证了这个说法**；弃用的真实原因是实现脆弱性（一条想当然的行更新优化就能让结果静默错掉）加上 mpq 版本的正确性论证更短。这条更正同时写进了 `route3_impl1_mpqscan.py` 的弃用登记。
2. **由第 1 条连带出的判定错误（已被阳性对照抓住）。** 现象：m₂ = 3 的第一版冒烟只找到 2 个顶点而解析族有 3 个；直接检查子集 `[3, 4, 6]`（= 链 C2₁、C2₂ 加和约束）给出错解并把 C3 判成不满足（逐字：`[3, 4, 6] 解= ['40960000000000000/104387965470349', …] 可行= (False, ['C3'])`），而真解是 (v, vδ, vδ²)（v = 12800000000000/32621239209）。修好后的同一冒烟：`候选 3、解析 3、相等 True`。**这条是「先跑小档阳性对照」这一纪律的直接收益。**
3. **实现二的 δ 幂表下标偏移（编码期自查发现，未进入实跑）。** 表 `dpow[k + m₂] = δ^k` 而初版直接以距离 d 取 `dpow[d]`，等价于整体乘 δ^{m₂}；改为统一的 `dq(k)` 取法后，m₂ = 3 起与实现一逐子集一致。
4. **复核器最初把 δ 写死为下界（自查发现，属工具缺陷不是数学缺陷）。** 首次复核 δ 上界跑的结果时报「12 个候选全部不通过、旋转号全 None」；定位为复核器用了自己的默认 δ 而不是被核对文件的 δ。改为「一律取被核对文件自带的 `delta` 与 `W`」后，同一文件的复核全通过。**登记理由**：这类工具缺陷最容易伪装成数学反例。
5. **工程记录（非数学问题）**：本机安全钩子（Mimosa）两次拦截「脚本内直接写结果文件」的写法（路径穿越规则），最终把两实现改成「结果 JSON 走 stdout、由命令行重定向落盘」，反而让每个数字与命令行一一对应。
6. **耗时数字的背景声明**：本机同时段有其它 actor 的重负载扫描（load average 峰值 214.63），第三节所有墙钟都在该背景下测得；同一档不同时间的耗时不可直接横比（例如 m₂ = 13 的 38.6 s 与 m₂ = 14 的 593.0 s，子集数之比是 3.87 倍而耗时之比是 15.3 倍，差值来自负载与分片粒度不同，不能当作算法复杂度结论）。

---

## 六、局部新结论及其独立验证方式

1. **结论 A（机器核对，附范围）**：δ = 126797/80000、W = 2000 时，m₂ = 10、12、13、14 四档的可行顶点集恰为 m₂ 个循环旋转；每顶点活跃约束条数与秩均为 m₂。
   独立验证方式：另一套算法（结构传播）同档全扫、与 route-5 实现的检查点逐点精确对拍、以及 `route3_verify.py` 的 V1 至 V6 见证复核（含 A_S·y = b_S 的直接代入与 25 条约束的精确可行性）。
2. **结论 B（机器核对，附范围）**：m₂ = 12 上，两实现对**全部 5,200,300 个子集**给出的判定逐项相同（0 不一致），顶点集、计数、证书、分块校验和全等；并与 route-5 实现的分检计数（4752735 / 447553 / 12）与顶点坐标逐点一致。
   独立验证方式：`route3_xcheck.py` 两种模式（json 对拍与逐子集对拍）的可复跑输出。
3. **结论 C（机器核对，附范围）**：把 δ 换成严格上界 7924813/5000000（m₂ = 10、12）后结论不变，即结论 A 在包含真实 δ 的严格有理区间的两个端点都成立。
   独立验证方式：`--delta hi` 的全扫输出与复核器输出。
4. **结论 D（已证，初等）**：4.2 的两条引理（枚举不漏顶点、满秩可行解必是顶点）与 4.3 的六条结构事实。
   独立验证方式：本报告 4.2、4.3 的证明要点逐条可读；机器侧另有两实现逐子集一致性作为交叉佐证（若结构事实有误，两实现会在同一批子集上分歧）。
5. **未取得结论的部分（明写）**：一般 m₂ 的顶点识别（未证）、δ 区间内部的稳定性（未证）、m₂ ≥ 15 的任何档位（未跑）、其它 (δ, W) 取值（未跑）、以及「本轮核对能否升级为定理」（不能，本轮不产出定理）。

---

## 七、核对边界声明（按 `tracks/vertex-m12/plan.md` 节八模板逐字出现并填实）

「本核对覆盖：m₂ 属于实际档位集合 {10, 12, 13, 14}（另在 m₂ = 10、12 用 δ 的严格上界复跑一遍）；参数（δ = 126797/80000，W = 2000；上界档 δ = 7924813/5000000）；方法为不依赖 (L1) 与顶点引理的全活跃子集穷举（两套互不共享代码的实现，加逐候选证书独立复核）。范围内的判定：可行顶点集恰为 m₂ 个循环旋转〔四档全部成立；每个顶点活跃约束条数与秩均为 m₂；m₂ = 12 上两实现对全部 5,200,300 个子集判定逐项一致，并与 route-5 实现的检查点逐点精确相等〕。该范围之外仍属未证：1. m₂ 超出实际档位的全部情形（m₂ ≥ 15 未跑）；2. 一切其他参数取值（含 (P1) 边缘与不满足 (P1) 的区域；δ 严格区间 [126797/80000, 7924813/5000000] 内部的逐点检验未做，只做了两个端点）；3. 一般 m₂ 的顶点识别仍只有纸面证明（route-1、route-2、route-5），未经形式化；4. 应用档 m₂ = 20、47、91 无独立穷举（组合规模不可达，`learnings.md:45`）；5. 本核对是机器核对，不构成对顶点引理的证明。」

---

## 八、完整命令行与原始输出摘要（全部本次亲跑，可复跑）

工作目录一律为 `70-research/tracks/vertex-m12/cycle-1`；`PY` = `20-experiments/.venv/bin/python`。

### 8.1 小档自检与逐子集对拍

```bash
$PY scripts/route3_xcheck.py --mode allsubsets --m2 2      # 同式逐个跑到 --m2 8
$PY scripts/route3_xcheck.py --mode allsubsets --m2 10 > results/route3_xcheck_m10_allsubsets.json
$PY scripts/route3_xcheck.py --mode allsubsets --m2 12 > results/route3_xcheck_m12_allsubsets.json
$PY scripts/route3_bareiss_probe.py
```

逐字摘要：`m2=2: … 不一致 0，候选 impl1=2 impl2=2` … `m2=8: … 不一致 0，候选 impl1=8 impl2=8`；`"m2": 10, "n_compare": 352716, "n_mismatch": 0`；`"m2": 12, "n_compare": 5200300, "n_mismatch": 0, "n_candidates_impl1": 12, "n_candidates_impl2": 12`；Bareiss 诊断（`results/route3_bareiss_probe_out.txt`）逐字：`A 段 … 结局分布 = {'inexact-matrix': 295, 'inexact-rhs': 10, 'ok': 3689, 'singular': 6}`、`不整除合计 = 305；其中「失败前一次行交换都没发生」的 = 229；发生过行交换的 = 76`、`B 段 … 结局分布 = {'ok': 3994, 'singular': 6}`、`C 段 … 结局分布 = {'needs-swap': 106, 'ok': 3889, 'singular': 5}`。

### 8.2 阳性对照 m₂ = 10

```bash
{ time $PY scripts/route3_impl1_mpqscan.py --m2 10 --workers 6 --chunk 100000 > results/route3_impl1_m10.json ; } 2>results/route3_impl1_m10.log
{ time $PY scripts/route3_impl2_struct.py --m2 10 --workers 4 --chunk 100000 > results/route3_impl2_m10.json ; } 2>results/route3_impl2_m10.log
$PY scripts/route3_xcheck.py --mode json --a results/route3_impl1_m10.json --b results/route3_impl2_m10.json > results/route3_xcheck_m10_compare.json
```

逐字摘要（取自 `results/route3_impl1_m10.log` 与 `results/route3_impl2_m10.log` 原文）：

1. 实现一 stderr 末段逐字：`"elapsed_sec": 22.182`、`"n_singular": 295780`、`"n_infeasible_unique": 56926`、`"n_candidate_subsets": 10`、`"n_distinct_candidates": 10`、`"analytic_equal_candidate_set": true`、`"agg": "2bde15694dbbcfa9"`；计时行逐字 `… --workers 6 --chunk 100000 >   30.06s user 0.78s system 136% cpu 22.577 total`；
2. 实现二 stderr 末段逐字：`"elapsed_sec": 5.692`、`"n_candidate_subsets": 10`、`"n_distinct_candidates": 10`、`"candidates_with_wrong_rank": []`、`"agg": "2bde15694dbbcfa9"`；计时行逐字 `… --workers 4 --chunk 100000 >   7.70s user 0.34s system 129% cpu 6.190 total`；
3. 对拍（`results/route3_xcheck_m10_compare.json`）逐字字段：`"agg_equal": true`、`"candidate_point_sets_equal": true`、`"n_blocks_with_agg_mismatch": 0`。
基线 `r2_j_A.txt` 与 route-5 的对应行见 3.2 表。

### 8.3 主结果 m₂ = 12

```bash
$PY scripts/route3_impl2_struct.py --m2 12 --workers 5 --chunk 250000 > results/route3_impl2_m12.json 2>results/route3_impl2_m12.log
$PY scripts/route3_impl1_mpqscan.py --m2 12 --workers 5 --chunk 250000 > results/route3_impl1_m12.json 2>results/route3_impl1_m12.log
$PY scripts/route3_xcheck.py --mode json --a results/route3_impl1_m12.json --b results/route3_impl2_m12.json > results/route3_xcheck_m12_compare.json
$PY scripts/route3_verify.py route3_impl1_m12.json > results/route3_verify_impl1_m12.json
$PY scripts/route3_verify.py route3_impl2_m12.json > results/route3_verify_impl2_m12.json
$PY scripts/route3_vs_other_compare.py --mine route3_impl1_m12.json --ckpt m2_12_mpq > results/route3_vs_other_m12_impl1.json
$PY scripts/route3_vs_other_compare.py --mine route3_impl2_m12.json --ckpt m2_12_mpq > results/route3_vs_other_m12.json
```

逐字摘要：实现一 `elapsed_sec 267.481、n_singular 4752735、n_infeasible_unique 447553、n_candidate_subsets 12、n_distinct_candidates 12、analytic_equal_candidate_set true、agg a5eb2b93d333ca02`；实现二 `elapsed_sec 51.832、候选 12、agg a5eb2b93d333ca02、candidates_with_wrong_rank []`；对拍 `agg_equal True、candidate_point_sets_equal True、candidate_ranks_equal True、active_count_equal True、n_blocks_with_agg_mismatch 0`；两实现对 route-5 检查点 `n_mine_points 12、n_other_points 12、point_sets_equal true、n_only_in_mine 0、n_only_in_other 0`；route-5 日志行 `n_rank_def 4752735、n_infeasible 447553、n_feasible_subsets 12、certs [[12, 12]]、wall_s 122.89`。

### 8.4 推档 m₂ = 13、14

```bash
$PY scripts/route3_impl2_struct.py --m2 13 --workers 5 --chunk 500000 > results/route3_impl2_m13.json 2>results/route3_impl2_m13.log
$PY scripts/route3_impl2_struct.py --m2 14 --workers 5 --chunk 1000000 > results/route3_impl2_m14.json 2>results/route3_impl2_m14.log
$PY scripts/route3_vs_other_compare.py --mine route3_impl2_m13.json --ckpt m2_13_mpq > results/route3_vs_other_m13.json
$PY scripts/route3_vs_other_compare.py --mine route3_impl2_m14.json --ckpt m2_14_mpq > results/route3_vs_other_m14.json
$PY scripts/route3_verify.py route3_impl2_m13.json > results/route3_verify_impl2_m13.json
$PY scripts/route3_verify.py route3_impl2_m14.json > results/route3_verify_impl2_m14.json
```

逐字摘要：13 档 `total_subsets 20058300、elapsed_sec 38.643、候选 13、相等 True、agg 5d4690cf6e0b1ff3`，对拍 `13 对 13、point_sets_equal true`；14 档 `total_subsets 77558760、elapsed_sec 592.974、候选 14、相等 True、agg 91da64fcca9aa0a9`，对拍 `14 对 14、point_sets_equal true`；两档复核 `候选 13 / 14 全通过 True`。

### 8.5 δ 严格上界变体

```bash
$PY scripts/route3_impl2_struct.py --m2 10 --workers 5 --delta hi --chunk 100000 > results/route3_impl2_m10_deltahi.json 2>results/route3_impl2_m10_deltahi.log
$PY scripts/route3_impl2_struct.py --m2 12 --workers 5 --delta hi --chunk 250000 > results/route3_impl2_m12_deltahi.json 2>results/route3_impl2_m12_deltahi.log
$PY scripts/route3_verify.py route3_impl2_m12_deltahi.json > results/route3_verify_impl2_m12_deltahi.json
```

逐字摘要：m₂ = 10 档 `delta 7924813/5000000、候选 10、相等 True、elapsed_sec 4.213`；m₂ = 12 档 `delta 7924813/5000000、候选 12、相等 True、elapsed_sec 45.56、agg 2c994b8a9308b2a0`；复核 `12 个候选全通过，旋转号 0 至 11`。

---

## 九、文件身份（md5）与复跑指引

### 9.1 本路线脚本（全部本次新写）

| 文件 | md5 | 行数 |
|---|---|---|
| `scripts/route3_defs.py` | `088d08bff5065cb58a2b9decd48b2437` | 274 |
| `scripts/route3_impl1_mpqscan.py` | `3f0035b17c0b601b37ec1c2e8502298a` | 275 |
| `scripts/route3_impl2_struct.py` | `b641f2805dcf90379d954cb2dc9a1b9d` | 318 |
| `scripts/route3_xcheck.py` | `c63dd6db26951411d06a2649a9d1404b` | 142 |
| `scripts/route3_verify.py` | `dd73d5b742b5a40df439e35281651999` | 150 |
| `scripts/route3_vs_other_compare.py` | `43d70b1cc4e7382eff5833882b1cb6e7` | 84 |
| `scripts/route3_bareiss_probe.py` | `fc73afa8d6a1967bfeb95a9c369bda73` | 114 |
| `scripts/route3_impl1_intscan.py` | `f7e5603bd634267ff22b9db0395c339e` | 316 |
| `results/route3_bareiss_probe_out.txt` | `a9e90407f02fff8052e51b3cd5071251` | 11 |

末行说明：`route3_impl1_intscan.py` 是**已弃用的第一版**（docstring 首行自述「整数无分数消元（Bareiss）」），它的 m₂ = 3 冒烟输出 `results/route3_smoke_m3.json` 就是第五节第 2 条那个失败标本（逐字：`候选 2、去重 2、解析 3、集合相等 False`）；任何后续引用都不得把它当作有效实现，有效实现是 `route3_impl1_mpqscan.py`。

### 9.2 原始结果（`results/`）

| 文件 | md5 | 内容 |
|---|---|---|
| `route3_impl1_m10.json` | `c9c77768e5eda8006db969299187ad02` | 实现一 m₂ = 10 全扫 |
| `route3_impl2_m10.json` | `c711aeac30d711c90e11b085992f2146` | 实现二 m₂ = 10 全扫 |
| `route3_impl2_m10_deltahi.json` | `2ecc539057d68efc9647f19693688da7` | δ 上界变体 m₂ = 10 |
| `route3_impl1_m12.json` | `ae707bd3ff64907a29873421f6dc423b` | 实现一 m₂ = 12 全扫 |
| `route3_impl2_m12.json` | `658a5bcaae56eafd4ffd30f451aa857f` | 实现二 m₂ = 12 全扫 |
| `route3_impl2_m12_deltahi.json` | `eebc3d9b17f5c5739b8d7b1d47e83189` | δ 上界变体 m₂ = 12 |
| `route3_impl2_m13.json` | `edf1593c32b08cadea1dcdb449179a9e` | 实现二 m₂ = 13 全扫 |
| `route3_impl2_m14.json` | `91fb541d8769f905dfac63f70048886d` | 实现二 m₂ = 14 全扫 |
| `route3_xcheck_m10_compare.json` | `c3a46ab09d5cb00552709bf9b6c52853` | m₂ = 10 两实现对拍 |
| `route3_xcheck_m10_allsubsets.json` | `2b6211cf5ad8195f7e8831470c56fa76` | m₂ = 10 逐子集对拍 |
| `route3_xcheck_m12_compare.json` | `7cd74fe6650fc13d43a7e7f7a0ebe266` | m₂ = 12 两实现对拍 |
| `route3_xcheck_m12_allsubsets.json` | `19f78a95f64a3b06a6444647acbb86e8` | m₂ = 12 逐子集对拍（5200300 个） |
| `route3_vs_other_m12.json`（实现二） / `route3_vs_other_m12_impl1.json`（实现一） | `47d3defdc75af9587f8e7f9604d1b022` / `a807588f45abd109a646c98c073c01f2` | 与 route-5 检查点逐点对拍 |
| `route3_verify_impl2_m12_deltahi.json` | `4ab7137d503d064bbe1d7b38c66feee5` | δ 上界变体 m₂ = 12 的候选复核 |
| `route3_smoke_m3.json` | （第一版冒烟，失败标本） | 第五节第 2 条的现场 |
| `route3_vs_other_m13.json` | `4e851bc7a40c873bf3e1ca6e14317bf9` | 同上（13 档） |
| `route3_vs_other_m14.json` | `adb1d0a97a4542ea80d55db1666a2a88` | 同上（14 档） |
| `route3_verify_impl1_m10.json` 等 8 份 | `54ead2ff…`、`bdf056c4…`、`cc9ff66f…`、`a6e1c0a3…`、`1b0fed08…` 等 | 候选证书独立复核（V1 至 V6） |

说明：上表 md5 是本次会话内实测值；`route3_defs.py`、`route3_impl2_struct.py`、`route3_verify.py` 在会话内有修订（加 δ 上界选项、复核器改为取文件参数），**以本节数值为最终版**；`results/md5-manifest.txt` 是另一 actor 的清单，与本表不混用（引用时各按各的路径）。

### 9.3 复跑指引（三步）

1. 自检：`$PY scripts/route3_xcheck.py --mode allsubsets --m2 6`（应得 1716 个、0 不一致）；
2. 复现 m₂ = 12 的两实现与对拍：按 8.3 的前三条命令（实现二约 1 分钟，实现一约 5 分钟，视负载）；
3. 与 route-5 检查点对拍：按 8.3 的最后两条命令（要求 `results/ckpt/m2_12_mpq/` 存在；若该目录被清理，则退化为「与解析族比较」这一档证据）。

---

**报告状态一句话**：本路线把 m₂ = 12 的顶点识别核对做成了两套独立实现的全量逐子集互证（5200300 子集、0 不一致），并把 13、14 两档与 δ 上界端点纳入覆盖；所有候选顶点都带可独立复核的证书；四档范围内「顶点集恰为 m₂ 个循环旋转」成立，**范围之外（m₂ ≥ 15、其它参数、一般 m₂）一律未证**，且本轮不产出任何定理。
