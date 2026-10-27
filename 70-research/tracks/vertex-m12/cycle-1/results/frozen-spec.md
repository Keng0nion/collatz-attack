# route-1 三向对照基线：冻结文书

冻结时刻：2026 年 10 月 27 日 22:28（JST；`date` 实测输出 `2026-10-27 22:28:38 JST`）。
性质：本文件在三组对照开跑**之前**写成并落盘。此后任何参数、期望值、判定规则的改动都必须在报告里显式登记为「冻结后修改」。本文件是 route-1 闸门的判据底本；报告 `route-1.md` 第一节与本文同文。
落盘路径：`70-research/tracks/vertex-m12/cycle-1/results/frozen-spec.md`。

## 一、要检验的精确陈述

**命题 R(m₂, δ, W)**：多面体 P(m₂, δ, W) 的全部可行顶点恰为解析的 m₂ 个循环旋转。

1. P 的约束表（勘误约束表的逐字转写；实现见冻结副本 `r2_common.constraint_list`，244 行版第 162 至 180 行，md5 `cfee819667c0883e73732f03d2dc8bef`）：
   (C1) y_j ≥ 1（j = 1 至 m₂）；
   (C2) y_{j+1} ≤ δ y_j（j = 1 至 m₂，指标循环，末条即回绕 y_1 ≤ δ y_{m₂}）；
   (C3) Σ_{j=1}^{m₂} y_j ≥ W。
2. 解析旋转集：{v·(δ^{r}, …, δ^{r+m₂−1})（指数按 mod m₂ 取）: r = 0 至 m₂ − 1}，其中 v = W(δ−1)/(δ^{m₂}−1)（`v_vertex`，同版第 134 至 136 行）。
3. 「顶点」的口径：点 y ∈ P 是顶点，当且仅当该点处活跃约束的法向量张成 R^{m₂}。本核对用等价的可执行形式：枚举全部 C(2m₂+1, m₂) 个大小为 m₂ 的活跃子集，精确解线性方程组、查秩 = m₂、查可行性（`full_enumeration`，`r2_j_independent_vertices.py`，272 行版第 92 至 114 行，md5 `4b8ce2a500d8ca9021fd0178deca637e`）。两方向的初等证明写在报告第三节第 2 条。
4. 本核对只在下列实例上做机器核对；**对一般 m₂ 与一般参数，R 仍属未证**（边界声明见报告第七节）。

## 二、参数锚点（三组对照）

1. 对照甲（阳性）：m₂ = 10、δ = D_LO7 = 126797/80000、W = 2000。
   1. δ 的身份：`r2_common.delta_rigorous_bounds(10^7)` 的下界，由整数幂判据给出，即把 126797/80000 通分为 15849625/10^7 后有 2^15849625 < 3^10000000（下界）与 2^15849626 > 3^10000000（上界 7924813/5000000）。严格性一律用这一**严格下界**做精确有理比较，方向不得写反。
   2. 阈值 (δ^10−1)/(δ−1) 的十进制摘要约 169.316390（浮点仅展示），W = 2000 > 阈值。
2. 对照乙（阴性）：m₂ = 2、δ = 3/2、W = 3/2。
   1. 该参数是**有意选的反例参数**（δ = 3/2 不是真实的 δ），用于检验冻结实现有没有判别力；阈值 (δ²−1)/(δ−1) = 5/2 > W，v = 3/5 < 1，预测族必含坐标 v < 1 的点。
3. 对照丙（边界 E10）：m₂ = 5、δ = D_LO7、W = (δ^5−1)/(δ−1)（阈值上的**等号**情形，v = 1）。
   1. W 的精确分数：`630347359154513105681/40960000000000000000`（逐字，对照 `r2_b_out.txt:93`）。

## 三、冻结期望值表（跑完后逐项核对；任一项不符 = 闸门失败）

对照甲（阳性；基线 = `r2_j_A.txt`，16 行，md5 `8f8d0112668a88d0811f30cefa396bd1`）：

1. 子集总数 C(21,10) = 352716。
2. 可行顶点数 = 10，且顶点集与解析旋转集**精确相等**（Fraction 逐坐标比较），同一判定打印 True，解析集大小 10。
3. 每个顶点的（活跃约束法向量秩，活跃约束条数）= [(10, 10)]。
4. 逐行对拍：同路径冻结脚本的输出与 `r2_j_A.txt` 在归一化用时数字后逐行一致（归一化仅限「（数字 s）」与「用时 数字 s」两处）。基线用时 real 62.49 s、user 61.78 s、sys 0.34 s（仅登记，不作闸门项）。

对照乙（阴性；基线口径 = `route-1.md:319`，457 行版 md5 `7be71b78cd4c582c67fa1b80c88d27e2`，与 `r1_selfcheck.py` md5 `dff8206d0047119cf0b65214ddb7c808` 的 [3] 节）：

5. 子集总数 C(5,2) = 10。
6. 实际顶点集合恰为 {(1,1)、(1,3/2)、(3/2,1)}（三个点，精确分数）。
7. 预测族恰为 {(3/5,9/10)、(9/10,3/5)}；两集合不相交；「顶点集 = 预测族」为 False。
8. 每个顶点的活跃秩 = 2（= m₂）。顶点集上 S 的最大值在 (1,1)（S = 6 精确）；基线浮点 4.640754482 落在另两点的严格区间内。
9. 基线浮点 9.281088094 落在预测族点的严格区间内，且该严格区间下界 > 6（证据边界照 `route-1.md:320`：否证的是分类，不是不等式）。

对照丙（边界；基线 = `r2_b_out.txt` 第 91 至 99 行，136 行版 md5 `f3882451e5a45fc3cb5cce781f279e32`）：

10. 子集总数 C(11,5) = 462。
11. 可行顶点数 = 5，且与解析旋转集精确相等。
12. 证书 = [(5, 6)]。
13. v = 1（分子位数、分母位数都是 1）；阈值位数 = 70 位分子 / 66 位分母；判据 (δ^5−1)/(δ−1) < W 为 False（等号）。
14. 结构注两条与约简复算均与 `r2_b_out.txt` E10 段逐字对拍：零向量（秩 5）；不相容（无解）（增广秩 5）；约简复算 5 个顶点且与全穷举一致。此三条只作对拍，**不作 (L1) 无关证据**（E10 档 (L1) 判据为 False，约简的前提不成立；本档承重结论以全穷举为准）。

## 四、依赖边界与代码审计（「不依赖任何引理」的落地）

允许依赖（显式清单）：

1. 数学侧：
   1. 顶点 ⟺ 活跃约束法向量张成 R^{m₂}（有限维初等线性代数，完整证明见报告第三节第 2 条）；
   2. `itertools.combinations` 的枚举完备性（CPython 实现；本次另用「八核分片计数之和 = C(21,10)」做可执行的计数核对，其级别是机器核对，不是形式化保证）；
   3. 精确有理算术 `fractions.Fraction` 与整数幂 `gmpy2`；S 值的严格区间来自 `f_bounds` 与 `pow2_bounds`（只用整数根与整数幂）。
2. 代码侧（冻结副本，md5 见第六节）：`constraint_list`、`solve_exact`、`feasible`、`full_enumeration`、`active_rank`、`rank_exact`、`vertex`、`v_vertex`、`S_bounds`、`f_bounds`、`pow2_bounds`、`Det`。
3. 审计结论：以上函数体内不出现 (L1)（「y_j = 1 不可行」及其判据 (δ^{m₂}−1)/(δ−1) < W）、不出现顶点引理的结论（旋转分类）、不出现凸性论证；`vertex` 与 `v_vertex` 只用于**比较层**（构造解析期望集），不在**判定路径**（枚举、解方程、可行性）中调用。阴性对照乙即该审计的可执行旁证。

禁止依赖（违者本核对降级为循环论证）：

1. (L1) 及其判据；2. 顶点引理与 Step 8′ 的任何结论；3. 「S 在顶点取最大」的凸性论证；4. v 的数值信息参与判定；5. 对 m₂ = 20、47、91 的不可达穷举（`learnings.md:45`，45 行版 md5 `e88a8c5a37f0bf6d11cb795683f25638`）。

## 五、闸门规则

三组对照全部逐项一致 → 放行主攻（m₂ = 12 等）；任何一项不符 → 先定位（定义、参数、实现三方向），修好前不得开跑大档。对拍口径：日志里的每个数字必须能 grep 到原始输出；参数表与实跑日志不一致时以日志为准（`learnings.md:36`）。本路线全部产出标注为「机器核对（附范围）」级证据（`learnings.md:30`）。

## 六、身份表（冻结时刻实测 md5 与行数）

| md5 | 行数 | 路径（相对 `collatz-attack/`） | 角色 |
|---|---|---|---|
| `cfee819667c0883e73732f03d2dc8bef` | 244 | `70-research/tracks/vertex-m12/cycle-1/scripts/frozen/r2_common.py` | 冻结副本（与上游逐字节相同） |
| `4b8ce2a500d8ca9021fd0178deca637e` | 272 | `70-research/tracks/vertex-m12/cycle-1/scripts/frozen/r2_j_independent_vertices.py` | 冻结副本（与上游逐字节相同） |
| `cfee819667c0883e73732f03d2dc8bef` | 244 | `70-research/cycle-1/scripts/r2_common.py` | 上游原件 |
| `4b8ce2a500d8ca9021fd0178deca637e` | 272 | `70-research/cycle-1/scripts/r2_j_independent_vertices.py` | 上游原件 |
| `8f8d0112668a88d0811f30cefa396bd1` | 16 | `70-research/cycle-1/scripts/results/verify-round2/r2_j_A.txt` | 对照甲基线日志 |
| `440e8a872de8d71cacee663fab6536f3` | 3 | `70-research/cycle-1/scripts/results/verify-round2/r2_j_A.time` | 对照甲基线计时 |
| `f3882451e5a45fc3cb5cce781f279e32` | 136 | `70-research/cycle-1/scripts/results/r2_b_out.txt` | 对照丙基线日志 |
| `7be71b78cd4c582c67fa1b80c88d27e2` | 457 | `70-research/cycle-1/route-1.md` | 对照乙基线口径来源（Step 9′） |
| `dff8206d0047119cf0b65214ddb7c808` | 461 | `70-research/cycle-1/scripts/r1_selfcheck.py` | 对照乙期望值来源（[3] 节） |
| `4d19e2fc351cea7a3b21e487a3c02e97` | 187 | `70-research/cycle-1/scripts/r2_b_vertices.py` | 对照丙约简口径来源 |
| `e88a8c5a37f0bf6d11cb795683f25638` | 45 | `70-research/learnings.md` | 纪律出处 |
| `6ad2e1e3ce6619bd9f31a7aab0f8d516` | 177 | `70-research/tracks/vertex-m12/plan.md` | 本轨道方案 |

## 七、本路线将落盘的产物（跑前登记）

1. 脚本（`70-research/tracks/vertex-m12/cycle-1/scripts/`）：`three_way_baseline.py`（三组对照驱动，模式 A、B、C 与附加模式 P、S）、`frozen/run_frozen_A.py`（冻结脚本同路径重跑）、`diff_norm.py`（归一化对拍）；冻结副本两份（第六节）。
2. 日志（`results/`）：`threeway-A-frozen-run.txt`（stdout）、`threeway-A-frozen-run.stderr.txt`（身份行与计时）、`threeway-A-diff.txt`（对拍）、`threeway-A-positive.txt`（对照甲逐项）、`threeway-B-negative.txt`、`threeway-C-boundary.txt`、`threeway-P-partition.txt`、`threeway-S-cost-sample.txt`，各附 `.time` 计时文件。
3. `md5-manifest.txt`（run 后生成，覆盖脚本、冻结副本、日志与被引基线）。
