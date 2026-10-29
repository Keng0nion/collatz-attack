# vertex-tail 首轮一手材料（vertex-m12 四条终态路线成果的收尾）

**轨道**：`70-research/tracks/vertex-tail/`，第 1 轮（cycleNumber = 1）
**写作者**：材料收集员（本工作流子代理）。**日期**：2026 年 10 月 28 日
**本文件性质**：只收一手材料与本次亲读、亲跑记录，不做数学裁决、不写判决。(a) 对抗复核、(b) 闸门、(c) 账本条目的判定归各自报告；凡本文件与那三份产物冲突，以它们为准。
**标注约定**：「亲自打开」指我本次会话用工具读过该文件（读、grep 或渲染）；「本次实测」指我本次会话亲手运行命令所得（命令见第六节）；「未打开」「未跑」「未能核实」逐条明写。行号引用一律带该文件 md5 与行数（行号会随文件更新漂移，本文件已亲见两处漂移）。
**路径基准**：除注明外，路径相对 `collatz-attack/`。中文正文不用半角连字符（路径、文件名、md5、命令等标识除外）。

---

## 〇、速查总表

| 名称 | 路径 | md5（本次实测） | 亲自打开 | 与疑点的关系 |
|---|---|---|---|---|
| route-1 报告 | `70-research/tracks/vertex-m12/cycle-1/route-1.md` | `939cc627c887fd4064214b14accfa651`（293 行） | 是（逐行全文） | 三向对照基线；第 5 行自述「状态：进行中」 |
| route-2 报告 | 同上目录 `route-2.md` | `9db46ca0d456a7c463f63adf776aa40e`（380 行） | 是（逐行全文） | 「m₂ = 12 全量」与 C 双路的主记录 |
| route-3 报告 | 同上目录 `route-3.md` | `8b8fe031050f630565a1c58a5e53a560`（351 行） | 是（逐行全文） | 「双实现逐项对拍」的主记录 |
| route-4 报告 | 同上目录 `route-4.md` | `e5ff27b061020b6aa81e326bd54c0b70`（399 行） | 是（逐行全文） | 完备性初等论证与依赖审计；对 12、13、14 零执行 |
| route-5 报告 | 同上目录 `route-5.md` | `3e833e440ceb5cc74d3470b24ac8355e`（343 行） | 是（逐行全文） | 检查点与推档文书；m₂ = 14 判定更正 |
| 冻结文书 | 同上 `results/frozen-spec.md` | `f117144c2ea51ecb4a09387318369cfd`（94 行） | 是（逐行全文） | 先冻后跑的三组期望值表 |
| 检查点 | 同上 `results/ckpt/`（11 个目录） | 无单一 md5；逐片 JSON | 是（七目录全片 json.load 复算，见 2.2） | 计数关系与捕捉子集还原的底本 |
| r5 全量日志 | 同上 `results/logs/r5_full_m2_*.log` | 例如 `m2_12_mpq` 为 `eb16f9e78762849af99b195bd219db8d` | 是（读关键行；m2_12_mpq 全文） | 判定行与 SUMMARY_JSON 的唯一出处 |
| m₂ = 14 判定件 | 同上 `results/logs/r5_full_m2_14_mpq_verdict.txt`、`r5_m2_14_verdict_check.txt` | 报告登记 `1a1fbae0749f0f99584856b741ad3aea` | 是（全文） | 「判定已读取」的直接物证 |
| 判串 | 同上 `scripts/results/route2/*_decisions.txt`（7 份） | 逐份实测，见 3.8 | 是（md5、字节、直方图、F 位置） | 「全量判定为真」的字节层底本 |
| 实现一 | 同上 `scripts/route3_impl1_mpqscan.py` | `3f0035b17c0b601b37ec1c2e8502298a`（275 行） | 是（逐行全文） | mpq 消元实现；`code = 0` 约定 |
| 实现二 | 同上 `scripts/route3_impl2_struct.py` | `b641f2805dcf90379d954cb2dc9a1b9d`（318 行） | 是（逐行全文） | 结构传播实现；`nocand` 合并两类 |
| 对拍器 | 同上 `scripts/route3_xcheck.py` | `c63dd6db26951411d06a2649a9d1404b`（142 行） | 是（逐行全文） | 第 54 行判据是「零不一致」的可执行定义 |
| 复核器 | 同上 `scripts/route3_verify.py` | `dd73d5b742b5a40df439e35281651999`（150 行） | 部分（grep 读 V1 至 V6 定义） | 候选证书 V1 至 V6 |
| r5 枚举实现 | 同上 `scripts/r5_vm12_enum.py` | `4fd20e6737c51dda3e88e2f6c0ca2345`（485 行） | 是（逐行全文） | 检查点字段与判定行语义的机器底本 |
| C 主实现 | 同上 `scripts/route2_vm_main.c` 等四件 | 四件 md5 实测见 3.7 | 部分（头、模式行、对拍行、函数签名） | 双路求解与 CROSSCHECK 字段 |
| 共享账本 | `70-research/ledger.md` | `8e0b44e3ebbf795dc393e4fa559cbee3`（197 行） | 部分（读 1 至 140 行） | `:112` 与 `:123` 的既有措辞（含漂移） |
| 教训件 | `70-research/learnings.md` | `96f3d946b0fbae97e31b873090503fb9`（62 行） | 是（逐行全文） | `:44` 至 `:45`、`:52` 至 `:56` 纪律 |
| 上轮材料 | 同上目录 `materials.md`（vertex-m12 的） | `d0c98e6bdec0f21c32451381c4e832f4`（450 行） | 部分（读 1.1、3.3、4.1、4.6、4.8、5.7、六） | 勘误逐字抄录与「打不开的」清单 |
| 本轨方案 | `70-research/tracks/vertex-tail/plan.md` | `8b6c86f771a7700151cdc5c9a92b1429`（184 行） | 是（逐行全文） | 疑点原文与验收判据明细（第八节） |
| 本轨方法件 | `70-research/tracks/vertex-tail/cycle-1/methods.md` | `052a544aabe348235941e0864dfdbc3c`（88 行） | 是（逐行全文） | 同轨另一子代理的机具与边界清点 |
| 勘误原件 | 同上目录 `materials/corrigendum.pdf` + `corrigendum.txt` | `f23d5f969116cb1af6e9b981b4b3ba7a`、`993f3f5a93188076c60c7357ac552eeb`（88 行） | 是（全文 + pdftoppm 渲染两页读图） | 命题 R 的原文出处 |
| 复现件 | 同上 `materials/repro-*.txt`（3 份） | `0d1509629af57fa586edb666b2f19403`、`55eacc48888fe36adc1aaa2871c43bca`、`5d603d03a34ace5ad9107383d87fd0c1` | 是（全文） | 上轮材料收集员的亲跑记录 |

---

## 一、五份路线报告：点名两条声明的原文出处（全部逐字）

**总注**：任务书说「四份报告」（route-3、route-5 等），本轨 `plan.md:35` 按「已终态成果」读法取 route-2、route-3、route-4、route-5；route-1 一并收作对照。我五份全读。

### 1.1 「m₂ 等于 12 与 13 全量判定为真」的原文句

**route-2.md（C 主实现，md5 `9db46ca0…`）**

1. `:12`（一句话结论，逐字节选）：
   > 「C 主实现以两条独立精确求解路径完成 m₂ = 12 的全部 C(25,12) = 5200300 个活跃子集穷举：**可行顶点数 = 12，且顶点集与解析的 12 个循环旋转精确相等（SETS_EQUAL True，逐坐标精确有理比较）**；同一实现下 m₂ = 10 校准与 Python 参考实现的判定串**逐字节一致**（352716 个判定全同，md5 `b269256bfff877a81fa5a81047a4c958`）；推档 m₂ = 13（20058300 个子集，第二路复核全部非 'S' 子集）与 m₂ = 14（77558760 个子集，第二路全量复核）同样给出「恰 m₂ 个循环旋转」，五档双路失配数全为 0。」
2. `:33`（「全量判定为真」的可执行判据逐字）：
   > 「枚举全部 C(2m₂+1, m₂) 个大小为 m₂ 的约束子集 S；对每个 S，精确解线性方程组（S 的全部约束取等号），若解不唯一（含不相容）记 'S'；若唯一解在全部 2m₂+1 条约束下不可行记 'I'；可行记 'F'（即顶点候选）。判定集 {S 的解 | 判定 'F'} 就是机器核对口径下的顶点集。」
3. `:68`（m₂ = 12 第二路全量）：
   > 「第二路精确求解对**全部 5200300 个子集**逐一复核（其中解向量逐坐标比较 447565 次），mismatches = 0。」
4. `:69`（m₂ = 13 的覆盖缺口，逐字）：
   > 「第二路复核全部**非 'S'** 子集（compared = 1246767，'I' 与 'F' 全体），mismatches = 0。**覆盖缺口**：18811533 个 'S' 判定未过第二路。」
5. `:214`（模式差异自登记）：
   > 「**注意模式差异**：本档第二路只复核了非 'S' 的 1246767 个子集，与 10、12、14 档的全量复核不同（登记为覆盖缺口）。」
6. `:76`（结构性观察的边界）：
   > 「这与引理 A2 的纸面预测（恰 m₂ 条活跃、缺一条回绕链）一致，但本身只是观察，不作普遍断言。」
7. `:151`（Python 第二实现覆盖率，逐字）：
   > 「每档的**顶点判定（'F'）所在尾部区段全部被这七段覆盖**，即三档的顶点判定都经过 Python 独立实现的逐字节复核。**覆盖缺口**：Python 侧对 12、13、14 档均非全量（覆盖率 3.47%、0.59%、0.26%），未覆盖区段只由 C 实现给出。」

**route-5.md（八核检查点实现，md5 `3e833e44…`）**

1. `:108`（A 条 m₂ = 12）与随后引用块（`:109` 至 `:113` 逐字，我在 `r5_full_m2_12_mpq.log` 里逐行核到同文）：
   > `    子集总数 C(25,12) = 5200300；已处理 = 5200300（覆盖校验 = True）`
   > `    分检：秩亏/不相容 = 4752735，满秩不可行 = 447553，满秩可行子集 = 12`
   > `    可行顶点数 = 12；与解析的 m2 = 12 个循环旋转相同 = True（解析集大小 12）`
   > `    每个顶点的（活跃约束法向量秩，活跃约束条数）= [(12, 12)]`
   > `    每个可行解被活跃子集捕捉的个数（升序）= [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]`
2. `:114`（A 条独立验证口径）：
   > 「独立验证：按 5.1 命令行重跑（fraction 8 核约 9 分钟、mpq 约 2 分钟量级）；或对已完成分片用 `--resume` 复算汇总；对拍 `SUMMARY_JSON` 的 `equal`、`n_distinct_feasible`、`certs` 三个字段。」
3. `:115`（B 条 m₂ = 13）：
   > 「同上参数，C(27,13) = 20058300 个活跃子集的判定为「可行顶点集恰为 13 个循环旋转」，两引擎（mpq 与 fraction）各自全量跑完且判定行对称 `diff` 零差异。」
4. `:120`（B 条性能对照，节选）：
   > 「mpq 墙钟 516.4 s、CPU 2923.4 s、每子集 CPU 0.1457 ms；fraction 墙钟 3513.5 s…两者之比（fraction/mpq）4.80。」
5. `:126`（C 条收句）：
   > 「引擎为 mpq 单引擎（fraction 14 全量未跑，节三第 10 条）。」
6. `:343`（一句话状态，节选）：
   > 「m₂ = 10、12、13、14 四档在 (δ_lo = 126797/80000, W = 2000) 上的全活跃子集穷举判定均为「可行顶点集恰为 m₂ 个循环旋转」（10、12、13 双引擎全量、判定行对称 `diff` 零差异；14 为 mpq 单引擎全量，C(29,14) = 77558760 子集、32 分片、墙钟 2912.2 s）」

**route-3.md（双实现，md5 `8b8fe031…`）**

1. `:215`（结论 B）：
   > 「**结论 B（机器核对，附范围）**：m₂ = 12 上，两实现对**全部 5,200,300 个子集**给出的判定逐项相同（0 不一致），顶点集、计数、证书、分块校验和全等；并与 route-5 实现的分检计数（4752735 / 447553 / 12）与顶点坐标逐点一致。」

### 1.2 「双实现逐项对拍零不一致」的原文句与可执行定义

1. `route-3.md:191`（点名句，逐字）：
   > 「m₂ = 12：`route3_xcheck.py --mode allsubsets --m2 12` 对**全部 5,200,300 个子集**逐项比较两实现的判定（类别与候选点串），结果逐字：`"n_compare": 5200300, "n_mismatch": 0, "n_candidates_impl1": 12, "n_candidates_impl2": 12, "first_mismatches": []`（`results/route3_xcheck_m12_allsubsets.json`）」
2. `route-3.md:195`：
   > 「结论：在 m₂ ≤ 12 的这些档位上，「两实现的判定逐子集相同」不是抽样断言，而是逐项核对过的。」
3. 对拍器的实际判据（`scripts/route3_xcheck.py:54`，我逐行读过，逐字）：
   > `        ok = (p1 == p2) and (c1 == c2)`
   同文件 `:8` 的 docstring 却写「逐项比较实现一（mpq 消元）与实现二（结构传播）的判定：kind、候选点串、判定码。」——**代码只比较 `p`（候选点串）与 `c`（判定码），`kind`（类别）没有进入 `ok`**（`k1`、`k2` 只在 `:58` 的 mismatch 记录里被打印）。这是「类别与候选点串」这句话与代码对不上的第一手材料。
4. 判定码语义（`scripts/route3_impl1_mpqscan.py:97` 至 `:99` 逐字）：
   > 「kind = 'singular'（无唯一解）/ 'infeasible'（唯一解但不在 P 内）/ 'feasible'。code = 0（非候选）或 point_code(点串)（候选；与实现二同口径，用于分片对拍）。」
   `:104` `return "singular", 0, None, 0`；`:107` 至 `:116` 全部 `infeasible` 分支 `return "infeasible", 0, None, 0`。即**非候选判定码恒为 0**，「singular 与 infeasible 的类别差异在对拍下不可见」。
5. 实现二的对应口径（`scripts/route3_impl2_struct.py:78` 逐字）：
   > 「kind: 'nocand'（出局）/ 'feasible'。code 口径与实现一相同（候选给点码，否则 0）。」
   即实现二把 singular 与 infeasible 合并成 `nocand`，本来也无类别可分。
6. JSON 模式的比较字段（`route3_xcheck.py:70` 至 `:116` 实测字段清单）：`m2_equal`、`total_subsets_equal`、`scanned_subsets_equal`、`agg_equal`、`agg`、`n_candidate_subsets`、`candidate_point_sets_equal`、`candidate_ranks_equal`、`n_blocks_a`、`n_blocks_b`、`blocks_with_agg_mismatch`、`n_blocks_with_agg_mismatch`、`active_count_equal`、`active_count_table`。**没有分检计数（singular / infeasible）字段**。
7. 两实现结果 JSON 的键集差异（本次实测）：
   1. impl1 有而 impl2 没有：`n_infeasible_unique`、`n_singular`；
   2. impl2 有而 impl1 没有：`candidates_with_wrong_rank`；
   3. 两实现的候选编号列表（m₂ = 12）逐位相同：5200288 至 5200299。
8. 对拍落点与伴随日志：`results/route3_xcheck_m12_allsubsets.json` 与 `route3_xcheck_m10_allsubsets.json` 的伴随 `.log` 均为 **0 字节**（本次 `ls -la` 实测）；该模式无计时文件。

### 1.3 其余两份报告的边界句（route-1、route-4）

1. `route-1.md:5`：> 「**状态**：进行中（第 1 节冻结文书已落盘；第 2 节起在对照跑完后逐节追加）。」——报告头未改，正文已完稿（`:293` 有完整结论）。
2. `route-1.md:13`（节选）：> 「三组对照共 31 项检查全部 PASS（甲 8、乙 11、丙 12），附加八核分片复算 5 项 PASS；阳性档与基线 `r2_j_A.txt` 在归一化用时后**逐行一致（16 / 16 行，对拍脚本退出码 0）**。**闸门判定：三组全部一致，放行主攻。**」同一段落后半：> 「本条属机器核对（附范围）：只覆盖 m₂ ∈ {2, 5, 10} 的三组实例，**该范围之外仍属未证**」
3. `route-4.md:6`：> 「本路线**不执行** m₂ = 12、13、14 的任何穷举（那是路线二、三、五的职责）」
4. `route-4.md:399`：> 「**m₂ = 12、13、14 与一切其他参数本路线零执行**，「该范围之外仍属未证」的逐条声明在 §七 7.2。」
5. `route-4.md:43`（节选）：> 「m₂ = 12、13、14 与一切其他参数取值的判定归路线二、三、五；m₂ = 20、47、91 无独立穷举（组合规模不可达，`learnings.md:45`）。」

---

## 二、results/ 检查点与日志（路径、是否打开、逐字字段与关键行）

### 2.1 检查点目录与分片结构（亲自打开：全部七套全量目录逐片 + 四套 smoke 档）

1. `results/ckpt/` 下 11 个目录与分片数（本次 `ls` 实测）：`m2_10_fraction` 16 片、`m2_10_mpq` 16 片、`m2_12_fraction` 16 片、`m2_12_mpq` 16 片、`m2_13_fraction` 32 片、`m2_13_mpq` 16 片、`m2_14_mpq` 32 片；`smoke_m2_2`、`smoke_m2_2_mpq`、`smoke_m2_5`、`smoke_m2_5_mpq` 各 1 片。
2. 每片 JSON 的键（本次亲读，逐字）：`start`、`end`、`count`、`n_rank_def`、`n_infeasible`、`feasible`、`first`、`last`、`sec`、`chunk`。`feasible` 是「去重顶点坐标串（逗号连接）→ 记录」的字典，每条记录只有两个键：`count`（该点被捕捉的子集数）与 `examples`（最多 3 条捕捉子集编号）。**检查点本身不存活跃秩、活跃条数、顶点数汇总**——证书在日志的判定行与 `SUMMARY_JSON.certs`，或在实现二的候选记录里（见 3.2）。
3. 实例一（m₂ = 12 末片，`results/ckpt/m2_12_mpq/chunk_0015.json`）：`start = 4875281`、`end = 5200300`、`count = 325019`、`n_rank_def = 287585`、`n_infeasible = 37422`；`feasible` 12 条，首键对应 `count = 1`、`examples = [[12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24]]`；`first = [3, 7, 8, 9, 10, 11, 12, 16, 21, 22, 23, 24]`、`last = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]`。
4. 实例二（m₂ = 14 末片，`results/ckpt/m2_14_mpq/chunk_0031.json`）：`start = 75135048`、`end = 77558760`、`count = 2423712`、`n_rank_def = 2270302`、`n_infeasible = 153396`；`feasible` 14 条，首条 `examples = [[14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28]]`。
5. 阴性档（`results/ckpt/smoke_m2_2/chunk_0000.json`）：`count = 10`、`n_rank_def = 0`、`n_infeasible = 7`、`feasible` 3 条，键逐字为 `1,1`、`1,3/2`、`3/2,1`，各 `count = 1`，`examples` 分别 `[[0, 1]]`、`[[0, 2]]`、`[[1, 3]]`。
6. 边界档（`results/ckpt/smoke_m2_5/chunk_0000.json`）：`count = 462`、`n_rank_def = 170`、`n_infeasible = 262`、`feasible` 5 条，**每条 `count = 6`**；首键逐字为 `1,126797/80000,16077479209/6400000000,2038576131263573/512000000000000,258485337715827265681/40960000000000000000`（**含坐标 1，v = 1 的直接痕迹**），`examples` 例如 `[[0, 5, 6, 7, 8], [0, 5, 6, 7, 10], [0, 5, 6, 8, 10]]`。

### 2.2 检查点计数关系的本次亲跑复算（材料轮旁证；(b) 的 verify.py 会以新写实现重做这些判据）

复算内容（只读 JSON；命令见第六节第 1、2 条）：分片计数之和 = C(2m₂+1, m₂)；分片首尾相接（`start` 接前片 `end`，无重叠）；每片 `count = end − start`；每片 `n_rank_def + n_infeasible + Σfeasible.count = count`；去重可行点数与每顶点捕捉次数。

| 目录 | 文件数 | Σcount | C(2m₂+1,m₂) | 分片连续 | 逐片计数关系 | 去重顶点 | 捕捉次数（最小、最大） |
|---|---|---|---|---|---|---|---|
| m2_10_fraction | 16 | 352716 | 352716 | 是 | 全通过 | 10 | 1、1 |
| m2_10_mpq | 16 | 352716 | 352716 | 是 | 全通过 | 10 | 1、1 |
| m2_12_fraction | 16 | 5200300 | 5200300 | 是 | 全通过 | 12 | 1、1 |
| m2_12_mpq | 16 | 5200300 | 5200300 | 是 | 全通过 | 12 | 1、1 |
| m2_13_fraction | 32 | 20058300 | 20058300 | 是 | 全通过 | 13 | 1、1 |
| m2_13_mpq | 16 | 20058300 | 20058300 | 是 | 全通过 | 13 | 1、1 |
| m2_14_mpq | 32 | 77558760 | 77558760 | 是 | 全通过 | 14 | 1、1 |
| smoke_m2_2 | 1 | 10 | 10 | 单片 | 全通过 | 3 | 1、1 |
| smoke_m2_2_mpq | 1 | 10 | 10 | 单片 | 全通过 | 3 | 1、1 |
| smoke_m2_5 | 1 | 462 | 462 | 单片 | 全通过 | 5 | 6、6（Σ = 30） |
| smoke_m2_5_mpq | 1 | 462 | 462 | 单片 | 全通过 | 5 | 6、6（Σ = 30） |

（表注：「单片」指该档只有 1 片，连续性显然。）

### 2.3 捕捉子集还原为键坐标（本次亲跑，独立复算）

方法：取片内某可行条目的 `examples[0]`，用冻结件 `scripts/frozen/r2_common.py` 的 `constraint_list` 建方程组，Fraction 高斯消元求出唯一解，与键坐标逐位比较（**参数取被核对档自身的 δ、W**）。

1. m₂ = 12（δ = 126797/80000，W = 2000）：末片首键还原 = 键坐标 **True**。
2. m₂ = 14（同参数）：末片首键还原 = 键坐标 **True**。
3. m₂ = 2（δ = 3/2，W = 3/2）：三键 `1,1`、`1,3/2`、`3/2,1` 全部 **True**。
4. m₂ = 5（δ = 126797/80000，W = 阈值分数）：首键（含坐标 1 者）还原 = 键坐标 **True**。
5. 自查更正（如实登记）：我对 m₂ = 2 的第一次复算误用了 δ = 126797/80000 的约束表，三键中两键报 False；换回该档自身参数后三键全 True。**这是「复核器必须取被核对文件自带参数」纪律（`route-3.md:205` 第 5 节第 4 条的同类登记）的一次活例**。

### 2.4 r5 全量日志逐字关键行（亲自打开：是）

1. `results/logs/r5_full_m2_12_mpq.log`（全文读过；判定六行逐字）：
   > `    子集总数 C(25,12) = 5200300；已处理 = 5200300（覆盖校验 = True）`
   > `    用时 122.9 s（墙钟），CPU（含子进程 user+sys）690.1 s，每子集 0.0236 ms（墙钟/总）`
   > `    分检：秩亏/不相容 = 4752735，满秩不可行 = 447553，满秩可行子集 = 12`
   > `    可行顶点数 = 12；与解析的 m2 = 12 个循环旋转相同 = True（解析集大小 12）`
   > `    每个顶点的（活跃约束法向量秩，活跃约束条数）= [(12, 12)]`
   > `    每个可行解被活跃子集捕捉的个数（升序）= [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]`
   同文件 `SUMMARY_JSON` 逐字（节选关键字段）：`"total": 5200300, "processed": 5200300, "n_rank_def": 4752735, "n_infeasible": 447553, "n_feasible_subsets": 12, "n_distinct_feasible": 12, "n_analytic": 12, "equal": true, "certs": [[12, 12]], "wall_s": 122.89, "cpu_s": 690.07`；头部的身份行逐字：`脚本 md5 = a0511d9861e56764a7eeaa796385e359`、`r2_common.py md5 = cfee819667c0883e73732f03d2dc8bef（期望 cfee819667c0883e73732f03d2dc8bef；一致 = True）`。
2. `results/logs/r5_full_m2_13_fraction.log`（读尾部 25 行；判定六行逐字）：`分检：秩亏/不相容 = 18811533，满秩不可行 = 1246754，满秩可行子集 = 13`、`可行顶点数 = 13；与解析的 m2 = 13 个循环旋转相同 = True（解析集大小 13）`、`每个顶点的（活跃约束法向量秩，活跃约束条数）= [(13, 13)]`、捕捉次数 `[1, …, 1]`（13 个 1）；`SUMMARY_JSON` 中 `"equal": true, "certs": [[13, 13]], "wall_s": 3513.53, "cpu_s": 14040.65`。
3. `results/logs/r5_full_m2_14_mpq_verdict.txt`（全文）与 `results/logs/r5_m2_14_verdict_check.txt`（全文）：判定行为 `分检：秩亏/不相容 = 74098262，满秩不可行 = 3460484，满秩可行子集 = 14`、`可行顶点数 = 14；与解析的 m2 = 14 个循环旋转相同 = True（解析集大小 14）`、`每个顶点的（活跃约束法向量秩，活跃约束条数）= [(14, 14)]`；`SUMMARY_JSON` 中 `"equal": true, "certs": [[14, 14]], "wall_s": 2912.24, "cpu_s": 13477.7`。**这两份文件就是「m₂ = 14 判定已读取」的直接物证**（参见 `route-5.md:100` 的更正句）。
4. `results/logs/r5_full_m2_10_fraction.log` 与 `r5_full_m2_10_mpq.log`（只 grep 判定行，逐字）：两者都是 `分检：秩亏/不相容 = 295780，满秩不可行 = 56926，满秩可行子集 = 10`、`可行顶点数 = 10；…相同 = True（解析集大小 10）`、`每个顶点的（活跃约束法向量秩，活跃约束条数）= [(10, 10)]`。
5. 未做（如实登记）：m₂ = 12 的 fraction 与 mpq 两引擎判定六行「对称 diff 零差异」我只读了 mpq 全文与 fraction 的 m₂ = 13 尾部；**m₂ = 12 两引擎六行的对称 diff 本次未跑**（`route-5.md:108` 自述零差异，属其自证）。

### 2.5 r5_smoke 阴性、边界档（亲自打开：是）

1. `results/r5_smoke/smoke_m2_2_fraction.log`（全文），关键行逐字：
   > `    分检：秩亏/不相容 = 0，满秩不可行 = 7，满秩可行子集 = 3`
   > `    可行顶点数 = 3；与解析的 m2 = 2 个循环旋转相同 = False（解析集大小 2）`
   > `    每个顶点的（活跃约束法向量秩，活跃约束条数）= [(2, 2)]`
   > `      额外顶点 (1, 1)`（证书：捕捉它的活跃子集例 `[[0, 1]]`）；`额外顶点 (1, 3/2)`（`[[0, 2]]`）；`额外顶点 (3/2, 1)`（`[[1, 3]]`）；`缺失顶点 (3/5, 9/10)`；`缺失顶点 (9/10, 3/5)`
   `SUMMARY_JSON`：`"equal": false, "certs": [[2, 2]]`。**判别力（会输出 False、会列出额外与缺失顶点）在日志层直接可见**。
2. `results/r5_smoke/smoke_m2_5_fraction.log`（grep 判定行）：`分检：秩亏/不相容 = 170，满秩不可行 = 262，满秩可行子集 = 30`、`可行顶点数 = 5；与解析的 m2 = 5 个循环旋转相同 = True（解析集大小 5）`、`每个顶点的（活跃约束法向量秩，活跃约束条数）= [(5, 6)]`。
3. `results/r5_smoke/` 目录共 30 个文件：`probe_m10/12/13/14_fraction|mpq` 的 `.log` 与 `.time`（16）、`sample_m2_10_fraction|mpq` 与 `sample_m2_12_fraction|mpq` 的 `.log` 与 `.txt`（8）、`smoke_m2_2_fraction|mpq`、`smoke_m2_5_fraction|mpq` 的 `.log`（4）——本次 `ls` 实测。
4. 未做：四份 `sample_*.txt` 的内容与「两实现逐子集样本 diff 零差异」**本次未复跑**（文件在；diff 结论为 `route-5.md:81` 自述）。

### 2.6 md5-manifest.txt 与 route-4 仪表化日志（亲自打开：是）

1. `results/md5-manifest.txt`（`571fb2bb0a84d57418808108cdda4ce3`，本次实测；通读全文）：标题行逐字 `# route-1 md5 清单（生成时刻：2026-10-28 01:45:46 JST）`；第 32 行逐字 `939cc627c887fd4064214b14accfa651 |    34874 |   293 | 70-research/tracks/vertex-m12/cycle-1/route-1.md`（与 `plan.md:45` 所称「登记值」一致）；末行登记 `96f3d946b0fbae97e31b873090503fb9 |    14117 |    62 | 70-research/learnings.md`（与 learnings 现行身份一致）。**grep 五份报告文件名，只命中 route-1 两行（本轨与上游各一）**：route-2 至 route-5 报告不在该清单内（生成时刻早于它们定稿，且该清单是 route-1 路线自己的产物）。
2. `results/route4_enum_m10_jobs1.txt`（grep 关键行，逐字）：`    片 [0, 352716)：迭代 352716 个子集，全秩 56936，命中 10，用时 62.2 s`、`    迭代子集总数 = 352716（与 math.comb 相等 = True）`、`    全秩子集数（rank = m2 且相容）= 56936`、`    [PASS] 迭代计数 = C(2m2+1, m2)`。

---

## 三、scripts/ 双向实现与判串（名称、路径、是否打开、逐字关键句）

### 3.1 实现一 `route3_impl1_mpqscan.py`（275 行，md5 `3f0035b17c0b601b37ec1c2e8502298a`；亲自打开：逐行全文）

1. 独立性声明（docstring，`:5` 至 `:15` 节选逐字）：
   > 「本实现：1. 算术栈：系数整行放大成整数后，消元与判定全程 gmpy2.mpq（GMP 有理数），不用 fractions.Fraction；2. 枚举：自写的组合字典序编号与推进（route3_defs），按编号区间切成确定性分片，multiprocessing 多进程并行，每片给出 64 位可交换校验和（用于不一致定位）；3. 判定分类拆开统计：奇异 / 唯一解但不可行 / 可行（候选），避免把前两类混计；4. 本实现**不 import r2_common**，也不 import r2_j_independent_vertices；只依赖 route3_defs.py（自写：约束表、可行性、解析族、组合编号、校验和）。」
2. 弃用登记（`:24` 至 `:30` 节选逐字）：
   > 「初版尝试「Bareiss 无分数消元 + 精确回代」，在 m₂ = 3 冒烟里给出错解（子集 [3, 4, 6] 被 C3 判据拒绝，顶点少一个）。……**故弃用的真实原因是实现脆弱性，不是「Bareiss 与主元交换不相容」（这一早期说法已由同一脚本更正）**。」
3. 判定返回（`:97` 至 `:99` 已引于 1.2 第 4 条；`:104` `return "singular", 0, None, 0`；`:107` 至 `:116` 三个 `infeasible` 分支；`:127` `return "feasible", point_code(ps), ps, act`）。
4. 输出 JSON 顶层字段（`:237` 至 `:264` 亲读）：`impl`、`m2`、`delta`、`delta_anchor_line`、`W`、`v`、`total_subsets`、`scanned_subsets`、`workers`、`chunk`、`elapsed_sec`、`n_singular`、`n_infeasible_unique`、`n_candidate_subsets`、`agg`、`n_distinct_candidates`、`candidate_points_sorted`、`candidates`（含 rank、subset、point、active_count）、`analytic_count`、`analytic_equal_candidate_set`、`analytic_only`、`candidates_not_analytic`、`blocks`。
5. 实测日志字段（`results/route3_impl1_m12.log`，本次 grep，逐字）：`"elapsed_sec": 267.481`、`"n_singular": 4752735`、`"n_infeasible_unique": 447553`、`"n_candidate_subsets": 12`、`"analytic_equal_candidate_set": true`、`"agg": "a5eb2b93d333ca02"`。

### 3.2 实现二 `route3_impl2_struct.py`（318 行，md5 `b641f2805dcf90379d954cb2dc9a1b9d`；亲自打开：逐行全文）

1. 算法五条（docstring，`:5` 至 `:24` 节选；与 `route-3.md:154` 至 `:162` 的六条一一对应），其中 `:19` 至 `:21` 逐字：
   > 「(a) 不含 C3 行：唯一解 <=> f = 0；(b) 含 C3 行：和泛函在自由分量上的系数是 Σ δ^t > 0（δ > 0），故和方程必把维数降 1 => 唯一解 <=> f = 1；f = 0 时和方程是相容性条件，须精确验 Σ y = W。」
2. 判定口径（`:78` 已引于 1.2 第 5 条）；`:170` `return "feasible", point_code(ps), ps, act, True`。
3. 候选记录附加字段（`:296` 至 `:301`）：`"witness_rank": certs[c[0]]`、`"candidates_with_wrong_rank": bad_cert`。
4. 实测日志字段（`results/route3_impl2_m12.log`，本次 grep，逐字）：`"elapsed_sec": 51.832`、`"n_candidate_subsets": 12`、`"n_distinct_candidates": 12`、`"candidates_with_wrong_rank": []`、`"analytic_equal_candidate_set": true`、`"agg": "a5eb2b93d333ca02"`。

### 3.3 对拍器 `route3_xcheck.py`（142 行，md5 `c63dd6db26951411d06a2649a9d1404b`；亲自打开：逐行全文）

1. 三种模式（docstring，`:5` 至 `:15` 逐字节选）：
   > 「1. --mode allsubsets --m2 K：对 m2 = K 的全部 C(2K+1, K) 个子集，逐项比较实现一（mpq 消元）与实现二（结构传播）的判定：kind、候选点串、判定码。……2. --mode json --a 文件A --b 文件B：比较两份结果 JSON：总校验和、每分块校验和（不一致时报出分块区间）、候选子集编号列表与候选点集合（不一致时报出差集）。……3. --mode block…」
2. 实际判据 `:54` 与 `kind` 未入判的差额（已引于 1.2 第 3 条）；`:48` 至 `:49` 的调用返回含 `k1`、`k2`（类别），只在 `:58` mismatch 记录里打印。
3. JSON 模式比较字段清单（已列于 1.2 第 6 条）。
4. 落点实测（本次亲读内容）：
   1. `results/route3_xcheck_m12_allsubsets.json` 全文逐字：`"m2": 12, "lo": 0, "hi": 5200300, "n_compare": 5200300, "n_mismatch": 0, "n_candidates_impl1": 12, "n_candidates_impl2": 12, "first_mismatches": []`；
   2. `results/route3_xcheck_m10_allsubsets.json`：`"m2": 10, "n_compare": 352716, "n_mismatch": 0, "n_candidates_impl1": 10, "n_candidates_impl2": 10`；
   3. `results/route3_xcheck_m12_compare.json` 关键字段逐字：`"agg_equal": true`、`"candidate_point_sets_equal": true`、`"candidate_ranks_equal": true`、`"active_count_equal": true`、`"n_blocks_a": 21`、`"n_blocks_b": 21`、`"n_blocks_with_agg_mismatch": 0`；`active_count_table` 12 点全部 `[12, 12]`；
   4. `results/route3_vs_other_m12.json` / `…m13.json` / `…m14.json` 关键字段逐字：`"point_sets_equal": true`、`"n_only_in_mine": 0`、`"n_only_in_other": 0`（分片数 16 / 16 / 32）。
5. 伴随日志：`route3_xcheck_m10_allsubsets.log` 与 `route3_xcheck_m12_allsubsets.log` 均 0 字节（`ls -la` 实测）。

### 3.4 复核器 `route3_verify.py`（150 行，md5 `dd73d5b742b5a40df439e35281651999`；部分打开：grep 读 V1 至 V6 定义）

1. V1 至 V6 逐字（`:8` 至 `:13`）：
   > 「V1 编号自洽：按记录的 rank 用组合字典序反编号，结果必须逐位等于记录的 subset；V2 见证子集满秩：该子集系数矩阵的 Fraction 行阶梯秩必须 = m2；V3 见证方程成立：A_S · y = b_S 逐行精确成立（整数行 × 有理坐标）；V4 可行：y 满足全部 2m2+1 条约束（整数交叉相乘，无浮点）；V5 属于解析族：y 必须等于 v·δ^r 的某个循环旋转（给出 r）；V6 证书一致：活跃约束条数与秩由本文件独立重算，必须与结果 JSON 中记录值相同。」
2. 复核输出实测（三份 JSON 的 `per_candidate` 首条，逐字）：`route3_verify_impl1_m12.json` 首候选 `"rank": 5200288, "rotation_index": 0` 且 `V1 至 V6` 全 `true`；`route3_verify_impl2_m13.json` 首候选 `"rank": 20058287`；`route3_verify_impl2_m14.json` 首候选 `"rank": 77558746`。

### 3.5 定义件 `route3_defs.py`（274 行，md5 `088d08bff5065cb58a2b9decd48b2437`；部分打开：grep 关键行）

1. `:40` 逐字：`W_FROZEN = Fraction(2000)   # 本轨道 W = 2000`。
2. `:45` `def delta_lo(verify=True):`、`:56` `def delta_hi(verify=True):`；锚点断言行逐字：`:51` `assert left < right, "锚点复核失败：2^15849625 < 3^10^7 不成立"`、`:52` `assert right < gmpy2.mpz(2) ** (p + 1), "锚点复核失败：3^10^7 < 2^15849626 不成立"`。
3. `:71` 起 `check_delta_anchor`，`:78` 返回串格式逐字：`f"δ 锚点复核（整数幂，无浮点）：2^{p} < 3^{q} < 2^{p+1} 全部为真 = "`（其输出行被 route-3 各结果 JSON 的 `delta_anchor_line` 字段引用）。

### 3.6 r5 枚举实现 `r5_vm12_enum.py`（485 行，md5 `4fd20e6737c51dda3e88e2f6c0ca2345`；亲自打开：逐行全文）

1. 语义与依赖（docstring `:4` 至 `:8`、`:10` 至 `:16` 节选逐字）：
   > 「对给定 (m2, δ, W)，枚举全部 C(2m2+1, m2) 个大小 m2 的活跃约束子集；每个子集：精确解线性方程组（Fraction 或 gmpy2.mpq），秩亏/不相容则弃；满秩则查精确可行性（C1: y_j>=1；C2 循环链含回绕: y_{j+1}<=δy_j；C3: Σy>=W）；可行解按坐标元组去重收集；最后与解析族（v·δ^r 的 m2 个循环旋转）做集合相等判定。」「禁止侧：任何 (L1)、v 的数值信息、凸性论证、顶点引理的结论——搜索本体一概不用；v 只用于构造被检验的"解析族"对照集，不参与搜索判定。」
   分片与断点（`:18` 至 `:20`）：> 「按组合字典序下标 [start, end) 切成 --chunks 个连续区间（deterministic，无重无漏）；父进程校验 Σ(end-start) = C(2m2+1, m2) 且各 worker 计数之和等于同一值。断点续跑：每片结果落 results/ckpt/<tag>/chunk_%04d.json；--resume 时复用已有分片。」
2. 身份钉死（`:35` 至 `:36`、`:54` 至 `:58`）：期望 md5 常量 `MD5_R2_COMMON`、`MD5_R2_J`；不符即 `sys.exit(2)`（`:366` 至 `:368`）。
3. `active_rank`（`:84` 至 `:92`）逐字给出「点 y 处活跃约束的法向量集的秩（= m2 即为顶点的秩证书）」，返回 `(rank_exact(rows, m2), len(rows))`——**证书的「（活跃秩，活跃条数）」二元组就是这里算的**。
4. 检查点写入（`:289` 至 `:290`）与 `feasible` 记录构造（`:209` 至 `:216`，`examples` 上限 3 条）。
5. 判定行与 SUMMARY_JSON（`:437` 至 `:452`、`:464` 至 `:475`）：判定行模板、`certs = sorted({active_rank(y, m2, d, W) for y in found})`、`cap = sorted(v["count"] for v in feas.values())`、SUMMARY 字段（`n_rank_def / n_infeasible / n_feasible_subsets / n_distinct_feasible / n_analytic / equal / certs / wall_s / cpu_s / ms_per_subset_*`）。

### 3.7 C 主实现（四件源文件与编译产物；部分打开：头文件全文、模式行、对拍行、函数签名；未逐行读 .c 全文）

1. 身份实测（与 `route-2.md:91` 至 `:95` 的登记值逐位一致）：`scripts/route2_vm_main.c` md5 `25edc679aa8ca9ce0650e6eb666e8ec0`、637 行；`scripts/route2_vm_core.c` md5 `eb4b9978cd187c229788317660229cf3`、377 行；`scripts/route2_vm_core.h` md5 `8686adc13cb5bcd2040e547f9e47c521`、42 行；`scripts/route2_ref_enum.py` md5 `7cfa5b6c326476bf5cb0fc6ed8bdcf0d`、164 行；二进制 `scripts/route2_vm_enum` md5 `714ab3cbbf28e812180577731faa9c19`。
2. 双路求解的存在性（`route2_vm_core.c`）：`structure_solve` 在 `:135`、`generic_solve` 在 `:223`、证书计算 `active_cert` 在 `:313`（另 `feasible_q` 在 `:111`）；声明逐字在 `route2_vm_core.h`：`char structure_solve(...); char generic_solve(...); void active_cert(work_t *w, const mpq_t *y, int *nactive_out, int *rank_out);`。
3. 对拍模式（`route2_vm_main.c:25` 逐字）：`static int CrossMode = 2; /* 0=off, 1=alive, 2=full, 3=sample */`；`:472` 逐字：`printf("CROSSCHECK compared=%lld sol_cmp=%lld mismatches=%lld mode=%d\n", CROSS_COMPARED, CROSS_SOL_CMP, ...`。
4. C 日志关键行（`scripts/results/route2/` 下，本次 grep 实测，逐字）：
   1. m10（`c_m10_t8_log.txt`）：`DECISION_COUNTS S=295780 I=56926 F=10 total=352716`、`CROSSCHECK compared=352716 sol_cmp=56936 mismatches=0 mode=2`；
   2. m12：`DECISION_COUNTS S=4752735 I=447553 F=12 total=5200300`、`CROSSCHECK compared=5200300 sol_cmp=447565 mismatches=0 mode=2`、`THREAD_SETS_SUM 5200300 (== total : True)`、`ENUM_WALL_SEC 38.234`；
   3. m13：`DECISION_COUNTS S=18811533 I=1246754 F=13 total=20058300`、`CROSSCHECK compared=1246767 sol_cmp=1246767 mismatches=0 mode=1`；
   4. m14：`DECISION_COUNTS S=74098262 I=3460484 F=14 total=77558760`、`CROSSCHECK compared=77558760 sol_cmp=3460498 mismatches=0 mode=2`；
   5. m5（`m5_e10_log.txt`）：`DECISION_COUNTS S=170 I=262 F=30 total=462`、`CROSSCHECK compared=462 sol_cmp=292 mismatches=0 mode=2`；
   6. 各档均有 `ANALYTIC_COUNT … SETS_EQUAL True`、`MISMATCHES_TOTAL 0`、`EXIT_OK`。

### 3.8 判串七份（亲自打开：md5、字节数、直方图、F 位置全部本次实测）

路径均在 `scripts/results/route2/` 下。

| 文件 | md5 | 字节 | 直方图（S / I / F） | F 位置 |
|---|---|---|---|---|
| `c_m10_t8_decisions.txt` | `b269256bfff877a81fa5a81047a4c958` | 352716 | 295780 / 56926 / 10 | 352706 至 352715，连续 |
| `c_m10_t1_decisions.txt` | 同上（全同） | 352716 | 同上 | 同上 |
| `py_m10_decisions.txt` | 同上（全同） | 352716 | 同上 | 同上 |
| `c_m12_t8_decisions.txt` | `8fb4ba1aef28fdc293b52270985ec35e` | 5200300 | 4752735 / 447553 / 12 | 5200288 至 5200299，连续 |
| `c_m13_t8_decisions.txt` | `152514f874a144554d1dff2ec0570da9` | 20058300 | 18811533 / 1246754 / 13 | 20058287 至 20058299，连续 |
| `c_m14_t8_decisions.txt` | `37921d19726088fb8be115707a749356` | 77558760 | 74098262 / 3460484 / 14 | 77558746 至 77558759，连续 |
| `m5_e10_decisions.txt` | `18e23746174db60150198149b00cd869` | 462 | 170 / 262 / 30 | 首末 195、461，不连续 |

（以上与 `route-2.md` 第八节第 10 条、第四节第 3 条的登记值逐位一致；字节数 = 组合数可直接作计数校验。）

### 3.9 七段 Python 切片对拍（本次亲跑复算，逐段与 C 判串对应区间比对）

| m₂ | 段 | 区间 | 长度 | IDENTICAL | 段内 md5 |
|---|---|---|---|---|---|
| 12 | a | [0, 60000) | 60000 | True | `3fc7cb4298234a9a35157a67468cdabb` |
| 12 | b | [2570000, 2630000) | 60000 | True | `01d48b64c306fcda9abf601a1cee60da` |
| 12 | c | [5140000, 5200300) | 60300 | True | `6ed10684ab1144eed0718d983ebbac7b` |
| 13 | a | [0, 60000) | 60000 | True | `b3a1a41dab9edab79470d174440fdded` |
| 13 | b | [20000000, 20058300) | 58300 | True | `0df416d6afade99f69e439cae879c482` |
| 14 | a | [0, 40000) | 40000 | True | `aed2dfe579abcd7927c87672ecdf53fb` |
| 14 | b | [77400000, 77558760) | 158760 | True | `032e82bc5fca23d1804ff270e4e4b963` |

（七行全部与 `route-2.md` 第 4.3 节表逐位一致；切片长度之和 180300 / 118300 / 198760 与 `route-2.md:255` 的覆盖率 3.47% / 0.59% / 0.26% 的分子一致，分母加法我核过：5200300 − 5140000 = 60300、20058300 − 20000000 = 58300、77558760 − 77400000 = 158760。）

### 3.10 双实现顶点坐标相等的独立比对（本次亲跑）

1. `results/route3_impl1_m12.json` 的 `candidate_points_sorted`（12 点）与检查点 `m2_12_mpq` 全部片 `feasible` 键（12 点）**逐点集合相等**（本次以 Fraction 归一化后实测，两向差集皆空）。
2. 两实现候选编号列表（m₂ = 12）逐位相同：5200288 至 5200299（本次实测）。
3. 未重跑声明：`route3_xcheck.py --mode allsubsets --m2 12`（5200300 子集的逐子集对拍）**本次未重跑**——任务硬约束禁止全量重跑，且其记录值（`n_mismatch: 0`）我已逐字读过并在 3.3 第 4 条登记。

---

## 四、共享账本、教训件与姊妹件（是否打开、逐字关键句）

### 4.1 `70-research/ledger.md`（197 行，md5 `8e0b44e3ebbf795dc393e4fa559cbee3`；部分打开：读 1 至 140 行）

1. `:112`（节 1.4 未决第 2 条内，逐字节选）：
   > 「顶点识别的一般证明虽对任意 m₂ 写成，机器核对只到 m₂ = 10 的全活跃子集穷举（不依赖 (L1)）与 12 个参数集的约简穷举（依赖 (L1)），**m₂ = 12 的全穷举未跑**（投影约 72 分钟），m₂ = 20、47、91 的独立穷举不可达。」
2. `:123`（节 1.5 下一轮目标第 1 条，逐字节选）：
   > 「…第四优先：顶点识别的机器核对升一档；第五优先：Theorem 23 第 7 步 ε 差异定位。」
3. 行号漂移事实（本次亲读核实）：现行 §0.2（`:19` 至 `:25`）五条为「定义桥、平台右端、分岔窗口、证据卫生、较低优先（`K > U(92)` 解析论证）」，**不含「顶点识别的机器核对升一档」**；该措辞只在 `:123` 的对照句里。即 `vertex-m12/plan.md:20` 引「`ledger.md:25`（节 0.2 第 4 条）」承载该句已指向他处（本轨 `plan.md:25` 与 `:74` 也登记了这处漂移）。
4. 与 (c) 衔接相关：`:112` 的「m₂ = 12 的全穷举未跑」与「m₂ = 20、47、91 的独立穷举不可达」两句是账本待改写的对象——本轮 vertex-m12 已把前句跑成（四档、五引擎）、后句保持为边界。

### 4.2 `70-research/learnings.md`（62 行，md5 `96f3d946b0fbae97e31b873090503fb9`；亲自打开：逐行全文）

1. `:44`（三之 10）逐字：「**把网格检验当证明用**：……教训：网格只能作机制检查或反例搜索，永远不能当全称命题的证据。」
2. `:45`（三之 11）逐字（节选）：「**对 m₂ = 20、47、91 硬做全活跃子集穷举**：`C(2m₂ + 1, m₂)` 的组合规模使这条路不可达（本轮到 m₂ = 10 已是 352716 个子集），更大 m₂ 只能做依赖 (L1) 的约简穷举。教训：升核对档位时选 m₂ = 12（C(25,12) = 5200300，投影约 72 分钟）这类「还跑得动」的档……不可达档要如实写成核对边界。」
3. `:52` 至 `:56`（第 2 轮新增第 2 至 6 条）要点：`:52` 网格与「逐格核算」；`:53` 硬编码恒真判据（`ck(..., True, ...)`）；`:54` 改后脚本不重跑就沿用旧输出；`:55` 报告正文不经判据复核；`:56` **「等级声明按最弱一步计，不按最强一步计」（逐字）**。
4. 身份核对：现行 62 行 md5 与 `results/md5-manifest.txt` 末行登记一致（本次实测）。

### 4.3 上轮材料与方法件（vertex-m12 的 cycle-1 下）

1. `70-research/tracks/vertex-m12/cycle-1/materials.md`（450 行，md5 `d0c98e6bdec0f21c32451381c4e832f4`；部分打开：读 1.1、3.3、4.1、4.6、4.8、5.7、六等节）：`:31` 勘误顶点句逐字与渲染图核对说明；`:45` 第 6 条（回绕写法差别的两边口径）；`:358` 至 `:360` md5 清单；`:371` 至 `:372` 登记的 `ledger.md` 130 行（md5 `c238e1003f6cf3b1ee0fcf29ae82e58a`）与 `learnings.md` 45 行（md5 `e88a8c5a37f0bf6d11cb795683f25638`）**均为旧身份，与现行 197 行 / 62 行不同**——「行号引用必须带版本」的活例；`:381` 起「六、打不开的」（上轮结论：/tmp 旧副本全不存在、`/tmp/dtatk3` 不存在、Lean 工具链不可用、未跑清单五条）。
2. `70-research/tracks/vertex-m12/cycle-1/methods.md`（80 行，md5 `df2fdf05c7efb8dc57048c35887aae2d`；**未打开**，只测身份）。
3. 上轮 `materials/repro-*.txt` 三份（本次亲自打开全文）：
   1. `repro-r1_selfcheck.txt`（`0d1509629af57fa586edb666b2f19403`）关键行逐字：「PASS 预测族与顶点集合不相交（分类在 v < 1 时失效）」「失败项数 = 0」「全部通过 ? True」；
   2. `repro-r2_j_A-m2-10.txt`（`5d603d03a34ace5ad9107383d87fd0c1`）关键行逐字：「子集总数 C(21,10) = 352716，用时 65.4 s」「可行顶点数 = 10；与解析的 m2 = 10 个循环旋转相同 = True（解析集大小 10）」「每个顶点的（活跃约束法向量秩，活跃约束条数）= [(10, 10)]」；
   3. `repro-r2_b_vertices.txt`（`55eacc48888fe36adc1aaa2871c43bca`）E1 至 E6 段，含 E4 行「全穷举（C(2m2+1, m2) = 462 个子集，不依赖 L1）：可行顶点数 = 5；与约简一致 = True」（该文件本人只读了前 60 行——部分打开）。

### 4.4 本轨两件（plan.md 与 methods.md）

1. `70-research/tracks/vertex-tail/plan.md`（184 行，md5 `8b6c86f771a7700151cdc5c9a92b1429`；亲自打开：逐行全文）关键句：`:14` 疑点原文照抄；`:35` 「按「已终态成果」读法取 route-2、route-3、route-4、route-5 四条（route-1 是基线闸门报告……）」；`:64` 对拍靶点（`route3_xcheck.py:54` 只比点串与判定码，`kind` 未入判）；`:82` 至 `:85` 两条点名声明的冻结定义；`:109` 至 `:111` verify.py 判据明细（S1 至 S4 与 P1 至 P4）；`:129` 硬约束（不重跑 12、13 全量）；`:160` P3 的边界档口径逐字：「点名项『活跃秩等于活跃条数』在这些档位按字面不成立，闸门须按档区分并如实打印」。
2. `70-research/tracks/vertex-tail/cycle-1/methods.md`（88 行，md5 `052a544aabe348235941e0864dfdbc3c`；亲自打开：逐行全文）关键句：`:16` 本次实测「四档旋转点可行且证书 (m₂, m₂)（m₂ = 10、12、13、14），m₂ = 5 阈值档（v = 1）证书 (5, 6)，m₂ = 2 阴性档旋转点因 v = 3/5 < 1 被 C1 判不可行」；`:22` 检查点七目录逐片复算结论；`:24` 对拍字段与上限句「『零不一致』的强度上限即这两个字段，不能读成判定类别层面的全同」；`:84` 至 `:86` 两个切入点（闸门锚定、第三套实现抽点）。

---

## 五、勘误原件（corrigendum）与渲染核对

1. URL：`https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf`（上轮 `curl` 实测 200；**本次未重下，本次可达性未核实**）。本机副本 `70-research/tracks/vertex-m12/cycle-1/materials/corrigendum.pdf`（124287 字节，md5 `f23d5f969116cb1af6e9b981b4b3ba7a`，本次实测）。
2. 抽取文本 `corrigendum.txt`（88 行，md5 `993f3f5a93188076c60c7357ac552eeb`，本次实测）。**乱码点**（本次亲见）：分式被压平成行内——`mm2 · K` 实为 (m₂/m)·K；`δ m2 − 1` 实为 δ^{m₂} − 1；上标错位。故按要求用 `pdftoppm -png -r 150` 渲染两页读图：渲染件 `/tmp/vertex-tail-materials/corrpage-1.png`、`corrpage-2.png`（md5 `a7c7973e65a2b1ac6be465bd3170bb4c`、`5ec441677d201128d324b32f702f1492`——与上轮 `corr-p1-1.png`、`corr-p2-2.png` **逐字节相同**，本次实测）。
3. 逐字关键句（按渲染图核对）：
   1. 约束表与顶点句（第 2 页，抽取文本 `:43` 至 `:46`）：
     > 「Since all xi are positive, the function S is convex and attains its maximum value at a vertex of the polytope determined by the constraints xi ≥ 1, xi+1 ≤ δxi , xm−m2 +1 < δxm , and xm−m2 +1 + · · · + xm ≥ (m2/m)·K. Thus, at least m2 of these constraints must be active, i.e., must hold with equality.」
     （渲染图上回绕是**严格号**「<」，和约束右端是分数 (m₂/m)·K。）
   2. 顶点坐标句（`:64` 至 `:65`）：
     > 「Consequently, S attains its maximum at a point whose coordinates are a cyclic permutation of xm−m2 +1 , δxm−m2 +1 , . . . , δ m2 −1 xm−m2 +1 , and」
   3. v 的定义（`:70` 至 `:72`，按渲染图）：「xm−m2+1 = (m2/m)·K·(δ−1)/(δ^{m2}−1) = v」。
   4. 「sum condition must be active」（`:59`）；「x_i = 1」段（`:47` 至 `:53`）。
   5. 首句（`:12` 至 `:14`）：「The derivation of the inequalities T (nm−m2 +1+ℓ ) < …… in the proof of Theorem 21 at the bottom of page 14 contains an error.」
4. 与「2m₂ + 1 条」口径的关系（只登记，不裁决）：勘误把回绕约束单列且印严格号；代码侧 `r2_common.constraint_list` 把回绕并入循环链且用非严格号（闭化读法）；两边都是 2m₂ + 1 条。既有登记出处：`60-audits/hercher-t21/rederivation-erratum.md:83` 至 `:84`（上轮材料 4.6 有逐字抄录；**本次未重读该原件，未核实**）。
5. `hercher5.pdf`（论文本体，250655 字节，md5 `3e2377bef0b1c0435dc455c9bbee43a1`，本次实测；**本次未重渲染、未打开**；上轮渲染件 `hercher-p13-13.png`、`hercher-p14-14.png` 在 `materials/` 下）。

---

## 六、本次实跑命令一览（全部只读；可逐条复跑）

工作目录除注明外为 `70-research/tracks/vertex-m12/cycle-1`；`PY` = `/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python`。

1. **检查点结构复算**（两段，输出见 2.2 表）：`cd results/ckpt && python3 - <<'EOF' …`（逐目录 `json.load` 全部 `chunk_*.json`：分片数、`Σcount`、首尾相接、`count = end − start`、`n_rank_def + n_infeasible + Σfeasible.count = count`、去重与捕捉次数）；第二段同法（或修正版）跑 `smoke_m2_2`、`smoke_m2_5` 两档。
2. **捕捉子集还原**（输出见 2.3）：`"$PY" - <<'EOF' …`（`sys.path` 加 `scripts/frozen`，调 `r2_common.constraint_list`，Fraction 高斯消元，与键坐标比较）。
3. **判串身份与直方图**（输出见 3.8）：`cd scripts/results/route2 && for f in …; do md5 -q "$f"; wc -c < "$f"; done`，直方图用 `python3 -c` 的 `Counter`；F 位置用 `python3` 逐字节扫描。
4. **切片对拍**（输出见 3.9）：`"$PY" - <<'EOF' …`（读 `c_m*_t8_decisions.txt` 的对应区间与 `py_m*_slice_*.txt`，比较并算段内 md5）。
5. **集合比对**（输出见 3.10）：`"$PY" - <<'EOF' …`（`route3_impl1_m12.json` 的 `candidate_points_sorted` 与 `results/ckpt/m2_12_mpq` 全部键，Fraction 归一化后比集合）。
6. **C 侧身份与日志**（输出见 3.7）：`md5 -q`、`wc -l` 于 `scripts/route2_vm_main.c`、`route2_vm_core.c`、`route2_vm_core.h`、`route2_ref_enum.py`、`route2_vm_enum`；`grep -E "DECISION_COUNTS|CROSSCHECK|SETS_EQUAL|EXIT_OK"` 于 `scripts/results/route2/*_log*.txt`；`grep -n` 于 `route2_vm_core.c`、`route2_vm_main.c`、`route2_vm_core.h`。
7. **身份测量**（输出见〇表与各节）：`md5 -q`、`wc -l` 于五份报告、`frozen-spec.md`、账本、learnings、上轮 materials.md / methods.md、本轨 plan.md / methods.md、corrigendum 两件、hercher5.pdf、repro 三件、`md5-manifest.txt`。
8. **渲染与读图**（见 5.2）：`pdftoppm -png -r 150 corrigendum.pdf /tmp/vertex-tail-materials/corrpage`，然后 Read 两张 PNG。
9. **route3 产物关键字段**（见 1.2、3.3、3.4）：`cat` 于 `results/route3_xcheck_m12_allsubsets.json`、`route3_xcheck_m10_allsubsets.json`、`route3_xcheck_m12_compare.json`、`route3_vs_other_m12.json`、`…m13.json`、`…m14.json`；`python3` 列 `route3_impl1_m12.json` 与 `route3_impl2_m12.json` 的键集差；`grep` 于 `results/route3_impl1_m12.log`、`route3_impl2_m12.log`；`cat` 于三份 `route3_verify_*.json` 的头部。
10. **存在性与权限**：`ls -la` 于 0 字节日志（`route3_xcheck_m10/m12_allsubsets.log`）、`results/r5_smoke/`（30 文件）、`.mimosa/`（目录层次）、上轮登记的 `/tmp` 名单（全部 No such file）。
11. **本轨两件亲读**：Read 全文 `70-research/tracks/vertex-tail/plan.md` 与 `…/cycle-1/methods.md`；Read 相关节 `70-research/ledger.md`（1 至 140 行）与上轮 `materials.md` 的 1.1、3.3、4.1、4.6、4.8、5.7、六等节。

**未跑（逐条）**：m₂ = 12、13（以及 10、14）的任何全量枚举或抽点重算；`route3_xcheck.py --mode allsubsets` 的任何重跑；`r5_vm12_enum.py` 的任何重跑（含 `--resume` 汇总）；勘误 URL 的本次重下；`hercher5` 的本次渲染；`sample_*.txt` 的 diff；route-4 其余四份输出的细读；`70-research/cycle-1/verify.py`（另一轮的 964 行产物）。以上未跑项按任务边界（不重跑全量、材料收集员角色）如实登记，不计入任何「通过」。

---

## 七、打不开的、未打开的、未能核实的（逐条写明尝试过什么）

1. **`/tmp` 旧副本一批**（上轮登记过的那批）：本次逐个 `ls -la`——`/tmp/corr.pdf`、`/tmp/corr.txt`、`/tmp/h5.pdf`、`/tmp/h5.txt`、`/tmp/sidw144.pdf`、`/tmp/corrpage-1.png`、`/tmp/corrpage-2.png`、`/tmp/p14-14.png`、`/tmp/dtatk3` **全部报 `No such file or directory`**（2026 年 10 月 28 日实测）。替代做法：勘误用本轨 `materials/` 下的副本重新渲染（与上轮渲染件逐字节相同，见 5.2）。
2. **`.mimosa` 内部目录**（本轨与 vertex-m12 各一处）：只 `ls` 到目录层次（`finding-ledger`、`history`、`hook-state`、`hook-status`、`reports`），**未打开其内部文件**——属安全钩子内部状态，与数学内容无关；登记在此仅为完整性。
3. **未打开全文（如实登记）**：`scripts/route2_vm_main.c`（637 行，只读头部、`CrossMode` 行、`CROSSCHECK` 行与参数解析段）；`scripts/route2_vm_core.c`（377 行，只 grep 函数签名与行号）；`scripts/route3_verify.py`（150 行，只读 V1 至 V6 定义与三份输出头部）；`scripts/route3_defs.py`（274 行，只 grep 关键行）；`materials/hercher5.pdf` 与 `hercher5.txt`（本次未打开）；`results/r5_smoke/sample_*.txt` 四份（未打开内容，也未复跑其 diff）；`results/route4_*.txt` 五份中只 grep 了 `route4_enum_m10_jobs1.txt` 的几行；`70-research/ledger.md` 只读了 1 至 140 行（余 57 行未读）；`70-research/tracks/vertex-m12/cycle-1/methods.md`（80 行）未打开；上轮 `repro-r2_b_vertices.txt` 只读了前 60 行。
4. **未能核实**：`route-2.md:271` 的内联测速脚本（0.83 毫秒/个的来源）未落盘，无法复跑测速本身（上轮已登记，本次沿袭）；`route-2.md` 第六节第 10 条（m₂ = 13、14 顶点独立复验输出未捕获落盘）为报告自述；`vertex-m12/plan.md:32` 对 `cycle-2/route-1.md:295` 的引用对不上（上轮 `materials.md:259` 至 `260` 已登记为「未能核实」，**本次未重查**）；`corrigendum.pdf` 的 URL 本次未重下（本次可达性未核实）；`rederivation-erratum.md:83` 至 `:84` 的原文本次未重读（只用上轮 materials 的逐字抄录）。
5. **本轮写作时点尚不存在的产物**：`70-research/tracks/vertex-tail/ledger-note.md`（(c) 的落点）与本轨 (a)、(b) 两份报告与 `cycle-1/verify.py`（(b) 的脚本）——它们由同轨其他子代理产出；本文件不预写其内容。

---

## 八、引用纪律与边界（材料轮的建议，不是判定）

1. 引本轨道任何结论时必须同时带：**实现名与引擎**、**覆盖范围（全量 / 分片 / 抽样）**、**比较字段清单**（对拍声明的字段上限见 1.2 第 6 条与 3.3 第 3 条）、以及「本轮未重跑全量」的事实。
2. 行号引用一律带 md5 与行数；本文件里已有三处活例：`route-1.md:5` 的「进行中」头、`ledger.md` §0.2 的漂移（`:19`至`:25` 对 `:123`）、上轮 `materials.md:371` 至 `:372` 登记的 ledger / learnings 旧身份。
3. 本文件全部「本次实测」都是只读复核、身份测量与渲染核对，**不构成对任何数学命题的证明**，也不替代 (b) 的闸门：(b) 的 `verify.py` 应以新写实现重做 2.2、2.3、3.9、3.10 的判据，并在分档口径（如 m₂ = 5 的证书 (5, 6)）上按其报告逐条打印通过与否。
4. 凡本文件与 (a)、(b)、(c) 三份产物冲突，以后三者为凭（它们带完整依赖清单与边界声明）。

**一句话状态**：五份报告、四档全量检查点（含两套引擎副本）、二至七份判串与切片、两套 Python 实现、C 双路实现与日志、共享账本与教训件、勘误原件（含渲染读图）均已亲自打开或实测身份；两条点名声明（「全量判定为真」「逐项对拍零不一致」）的原文逐字句、可执行判据、比较字段与已知盲区全部登记在案；未打开与未跑项逐条列于第七节与第六节末。


---

## 九、复采附录（同轮第二次材料收集；与首版并存）

**本附录性质**：同一任务书下重新做的材料复采，由材料收集员在本会话完成。首版 391 行（md5 `df9c0278acdafb7b06eb35719c05faef`）原本保留于本附录之前，逐字节未改；凡 `plan.md` 对 `materials.md` 的既有行号引用（如 `:112`、`:125`、`:267` 至 `:277`）仍然有效。本附录的「本次亲读」「本次实测」「本次亲跑」只指本次会话；首版已载而本次未重做的事项，按首版自身标注读取，不因本附录引用而升级。中文正文不用半角连字符（路径、文件名、md5、命令等标识除外）。

**身份登记（落盘后补录）**：前缀（行 1 至 391）与本附录（自第 392 行起）的 md5、整文件行数，见本附录末「复采登记」行。

### 9.1 身份表（本次会话亲测；只列与疑点直接相关者）

| 名称 | 路径（相对 `collatz-attack/`） | 行数 | md5（本次实测） | 本次是否亲开 |
|---|---|---|---|---|
| route-1 报告 | `70-research/tracks/vertex-m12/cycle-1/route-1.md` | 293 | `939cc627c887fd4064214b14accfa651` | 节选（`:1` 至 `:20`、`:86`、`:158`；首版逐行全读） |
| route-2 报告 | 同上 `route-2.md` | 380 | `9db46ca0d456a7c463f63adf776aa40e` | 节选（`:12`、`:68`、`:69`、`:80`、`:147`、`:192`、`:204`、`:214`、`:255`、`:371`） |
| route-3 报告 | 同上 `route-3.md` | 351 | `8b8fe031050f630565a1c58a5e53a560` | 节选（`:189` 至 `:195`、`:207`、`:215`、`:227`） |
| route-4 报告 | 同上 `route-4.md` | 399 | `e5ff27b061020b6aa81e326bd54c0b70` | 节选（`:6`、`:43`、`:334`、`:337`、`:399`） |
| route-5 报告 | 同上 `route-5.md` | 343 | `3e833e440ceb5cc74d3470b24ac8355e` | 节选（`:96` 至 `:100`、`:108`、`:115`、`:121`、`:330` 至 `:343`） |
| 冻结文书 | 同上 `results/frozen-spec.md` | 94 | `f117144c2ea51ecb4a09387318369cfd` | 亲读全文 |
| 首版材料 | `70-research/tracks/vertex-tail/cycle-1/materials.md` | 391 | `df9c0278acdafb7b06eb35719c05faef` | 亲读（含本次补读 `:81` 至 `:87`） |
| 本轨方案 | `70-research/tracks/vertex-tail/plan.md` | 201 | `06a5490fe0d4b58dad0e5e051fea1487` | 节选（疑点原文、`:51` 至 `:78`、`:103` 至 `:107`、`:115` 至 `:145`） |
| vertex-m12 方案 | `70-research/tracks/vertex-m12/plan.md` | 177 | `6ad2e1e3ce6619bd9f31a7aab0f8d516` | 节选（`:15` 至 `:32`） |
| 共享账本 | `70-research/ledger.md` | 197 | `8e0b44e3ebbf795dc393e4fa559cbee3` | 节选（`:17` 至 `:26`、`:108` 至 `:124`） |
| 教训件 | `70-research/learnings.md` | 62 | `96f3d946b0fbae97e31b873090503fb9` | 节选（`:41` 至 `:57`） |
| 对拍器一 | 同上 `scripts/route3_xcheck.py` | 142 | `c63dd6db26951411d06a2649a9d1404b` | 亲读（`:1` 至 `:60`、`:96` 至 `:142`） |
| 对拍器二 | 同上 `scripts/route3_vs_other_compare.py` | 84 | `43d70b1cc4e7382eff5833882b1cb6e7` | 逐行全读（首版未列此件） |
| 实现一 | 同上 `scripts/route3_impl1_mpqscan.py` | 275 | `3f0035b17c0b601b37ec1c2e8502298a` | 节选（`:96` 至 `:130`、`:237` 至 `:248` 及返回行） |
| 实现二 | 同上 `scripts/route3_impl2_struct.py` | 318 | `b641f2805dcf90379d954cb2dc9a1b9d` | 节选（`:74` 至 `:82` 及返回行） |
| 复核器 | 同上 `scripts/route3_verify.py` | 150 | `dd73d5b742b5a40df439e35281651999` | 节选（`:1` 至 `:30` 与 V 判据行） |
| r5 枚举实现 | 同上 `scripts/r5_vm12_enum.py` | 484 | `4fd20e6737c51dda3e88e2f6c0ca2345` | 节选（`:85`、`:299` 至 `:300`、`:437` 至 `:475`；首版记 485 行，差 1，如实登记） |
| C 主实现 | 同上 `scripts/route2_vm_main.c` | 637 | `25edc679aa8ca9ce0650e6eb666e8ec0` | 节选（`:25`、`:471` 至 `:473`、`:619`） |
| C 核心 | 同上 `scripts/route2_vm_core.c` | 377 | `eb4b9978cd187c229788317660229cf3` | 未打开内容（仅测身份） |
| Python 参考 | 同上 `scripts/route2_ref_enum.py` | 164 | `7cfa5b6c326476bf5cb0fc6ed8bdcf0d` | 节选（`:1` 至 `:24`） |
| 定义件 | 同上 `scripts/route3_defs.py` | 274 | `088d08bff5065cb58a2b9decd48b2437` | 未打开内容（仅测身份） |
| 三向基线驱动 | 同上 `scripts/three_way_baseline.py` | 485 | `ce5f86768282708d8feace976272659d` | 未打开内容（仅测身份） |
| 归一化对拍 | 同上 `scripts/diff_norm.py` | 46 | `9f8602bd0c4e8a6ceec79dafd97038de` | 未打开内容（仅测身份） |
| 冻结求解器 | 同上 `scripts/frozen/r2_common.py` | 244 | `cfee819667c0883e73732f03d2dc8bef` | 亲读（`:145` 至 `:195`） |
| 清单 | 同上 `results/md5-manifest.txt` | 未重数 | `571fb2bb0a84d57418808108cdda4ce3` | 未重读（首版通读；本次仅测身份） |
| 检查点 | 同上 `results/ckpt/`（11 目录）与 `det_run1`、`det_run2` | 逐片 | 无单一 md5 | 亲跑复算全部 `chunk_*.json`（见 9.4） |

**「五套实现」的口径说明（本附录读法）**：按产物线清点为 1. C 主实现（`route2_vm_main.c` 与 `core.c`，内含结构解与通用消元两条求解路径）；2. Python 参考（`route2_ref_enum.py`）；3. route3 实现一（mpq 消元）；4. route3 实现二（结构传播）；5. r5 八核枚举（`r5_vm12_enum.py`，引擎 fraction 与 mpq）。复核器与定义件不计入五套。若把 r5 的两引擎或 C 的两路各拆为独立套件，计数会变；本附录按「产物线」计。

### 9.2 两条点名声明的复采要点

1. **「m₂ 等于 12 与 13 全量判定为真」**
   1. 首版已逐字引 `route-2.md:12`、`:68`、`:69`、`:214`、`:255` 与 `route-5.md:108`、`:115`；本次新增逐字两句：
      1. `route-2.md:80`（节选，逐字）：「m₂ = 12：既有记录只到「投影约 72 分钟（未跑）」（`ledger.md:25`、`cycle-1/route-2.md:205`）；本次给出全量实跑。Python 单核口径为 0.83 毫秒/子集（乘以 5200300 约 71.9 分钟）；C 双路精确实现八线程墙钟 **38.27 秒**……」
      2. `route-5.md:100`（节选，逐字）：「**更正**：工具恢复后重查日志，已读到 m₂ = 14 的全量判定为真（见节四 C 条与节五 5.4）；此前一次提交里「m₂ = 14 判定未读取」的表述作废，以本报告节四 C 条为准。」
   2. 本次亲测支撑值（只读复算，未重跑任何全量）：
      1. C 侧日志五档（`scripts/results/route2/`，本次 grep）逐字：m10 `DECISION_COUNTS S=295780 I=56926 F=10 total=352716`；m12 `S=4752735 I=447553 F=12 total=5200300`；m13 `S=18811533 I=1246754 F=13 total=20058300`；m14 `S=74098262 I=3460484 F=14 total=77558760`。各档另有 `CROSSCHECK … mismatches=0`、`THREAD_SETS_SUM … (== total : True)`、`ANALYTIC_COUNT … SETS_EQUAL True`、`EXIT_OK`。
      2. m12 的 `CROSSCHECK compared=5200300 sol_cmp=447565 mismatches=0 mode=2`；`sol_cmp = 447565` 与 `route-2.md:68` 的「解向量逐坐标比较 447565 次」逐位一致（指称同为 C 内部第二条求解路径）。m13 的对应行为 `compared=1246767 … mode=1`（alive 口径），即 `route-2.md:69` 的「非 'S' 全体复核」覆盖缺口在日志层可见。
      3. 判串七份的 md5、字节数与直方图见 9.4 表；m12 的 md5 `8fb4ba1aef28fdc293b52270985ec35e` 与 `route-2.md:192` 登记值一致。
      4. r5 日志「判定六行」（含「独立性」行、不含「用时」与分块行）的对称 `diff`，在 m10、m12、m13 三档全部零差异（退出码 0；命令见 9.7 第 5 条）。
      5. 检查点分片计数关系全部复算通过（9.4 第 1 条）。
   3. 随句边界（复采时一并登记）：`route-2.md:69`、`:214` 的「m₂ = 13 的 'S' 判定未过第二路（18811533 个）」与 `route-2.md:255` 的 Python 覆盖率 3.47%／0.59%／0.26%——「全量判定为真」在 13 档的机器口径是「非 'S' 全体逐子集复核」，引用时不可省。

2. **「双实现逐项对拍零不一致」**
   1. 首版已逐字引 `route-3.md:191`、`:195`、`:215` 与判据行 `route3_xcheck.py:54`；本次复测一致：`:54` 逐字为 `        ok = (p1 == p2) and (c1 == c2)`；docstring `:8` 逐字含「的判定：kind、候选点串、判定码。不一致时打印编号、子集内容与两边判定（定位到编号）。」；`kind` 的 `k1`、`k2` 只在 `:58` 的不一致记录里被打印。
   2. 第二对拍器（首版未单列）：`route3_vs_other_compare.py`（84 行，md5 `43d70b1cc4e7382eff5833882b1cb6e7`）docstring 逐字：「做三件事：1. 从两边取出**全部候选顶点的精确坐标串**（不做任何浮点近似），比较两个集合；2. 比较候选子集条数（捕捉每个顶点的活跃子集个数）；3. 不一致时打印差集（定位到具体坐标串），一致时给出「逐点精确相等」的结论行。」即第二个对拍器的比较字段是「顶点坐标串集合 + 捕捉条数」，不触及判定码与类别。
   3. 对拍落点本次重读：`results/route3_xcheck_m12_allsubsets.json` 逐字 `"m2": 12, "lo": 0, "hi": 5200300, "n_compare": 5200300, "n_mismatch": 0, "n_candidates_impl1": 12, "n_candidates_impl2": 12, "first_mismatches": []`；m10 同名件为 `"n_compare": 352716, "n_mismatch": 0`。`results/route3_vs_other_m12.json`、`…m12_impl1.json`、`…m13.json`、`…m14.json` 关键字段均为 `"point_sets_equal": true`、`"n_only_in_mine": 0`、`"n_only_in_other": 0`。
   4. 覆盖边界（本次清点 `results/route3_*.json`，共 25 份）：`--mode allsubsets` 落点只有 m10 与 m12（另有 m12 的 json 模式 `route3_xcheck_m12_compare.json`，21 块逐块校验和相等）；m13、m14 的 route-3 侧落点为 `route3_impl2_m13.json`、`route3_impl2_m14.json` 与 `route3_vs_other_m13/m14.json`（对 route-5 检查点），**没有** impl1 的 m13、m14 结果（`route3_impl1_*` 只有 m10、m12）。即「两实现逐子集对拍」的范围到 m2 = 12 为止；13、14 档的 route-3 侧是「实现二单实现 + 检查点对拍」。

### 9.3 口径五词：两个对拍器与五套实现的对照（本次亲读原句）

1. **类别**：实现一 `:97` 至 `:99` 逐字「kind = 'singular'（无唯一解）/ 'infeasible'（唯一解但不在 P 内）/ 'feasible'」；实现二 `:78` 逐字「kind: 'nocand'（出局）/ 'feasible'」（把前两类合并）；C 主实现与 Python 参考用判定字符：`route2_ref_enum.py:11` 逐字「'S' = 无唯一解（秩亏或不相容）；'I' = 有唯一解但不可行；'F' = 唯一解可行（顶点）」；r5 枚举无「类别」字段，直接给分检计数与证书。
2. **判定码**：实现一 `:98` 逐字「code = 0（非候选）或 point_code(点串)（候选；与实现二同口径，用于分片对拍）」；非候选分支全部返回 0（本次 rg 实测行号 `:105`（singular）、`:108`、`:111`、`:116`（infeasible）、`:127`（feasible）；首版记 `:104`、`:107` 至 `:116`，差 1，文件 md5 相同）；实现二 `:102` 至 `:156` 共 8 处 `return "nocand", 0, None, 0, False`、`:170` `return "feasible", point_code(ps), ps, act, True`。故「非候选判定码恒 0」在两实现成立，而 xcheck `:54` 只比点串与判定码——**singular 与 infeasible 的类别差异在该对拍下不可见**（首版 1.2 第 3 至 5 条已登记，本次复测代码与行号确认）。
3. **分检计数**：实现一 JSON 顶层有 `n_singular`、`n_infeasible_unique`；实现二**没有**这两个字段（本次实测键集差：实现一独有 `n_infeasible_unique`、`n_singular`，实现二独有 `candidates_with_wrong_rank`）；r5 为 `n_rank_def`、`n_infeasible`；C 为 `DECISION_COUNTS S/I/F`。xcheck 的 json 模式比较字段（首版 1.2 第 6 条清单：`m2_equal`、`total_subsets_equal`、`scanned_subsets_equal`、`agg_equal`、`n_candidate_subsets`、`candidate_point_sets_equal`、`candidate_ranks_equal`、`n_blocks_*`、`active_count_equal`、`active_count_table`）**不含分检计数**——「分检计数一致」没有两实现之间的直接对拍字段，只有三方（实现一、C、r5）在同值上互证。
4. **捕捉子集**：检查点 `feasible[键]` 的 `examples`（最多 3 条捕捉子集编号）与 `count`；r5 打印行「每个可行解被活跃子集捕捉的个数（升序）= […]」与 `cap = sorted(v["count"] …)`；C 侧 `VERTEX … certs=1 cert_subset_idxs=…` 行（如 `route-2.md:214` 的 `20058287[13,14,15,16,17,18,19,20,21,22,23,24,26]`）。
5. **活跃秩与活跃条数**：r5 `:449` 逐字 `certs = sorted({active_rank(y, m2, d, W) for y in found})`，`:85` 起 `def active_rank`（先给「点 y 处活跃约束的法向量集的秩」）；实现一 `active_count`（对约束全表逐条验等号计数）、`:127` 随候选返回；实现二候选附 `active_count` 与 `witness_rank = certs[c[0]]`；复核器 `route3_verify.py:13` 逐字「V6 证书一致：活跃约束条数与秩由本文件独立重算，必须与结果 JSON 中记录值相同。」

### 9.4 检查点与判串的本次亲跑结果

1. **检查点复算**（逐片 `json.load`；命令见 9.7 第 1 条）：

| 目录 | 片数 | Σcount | C(2m₂+1,m₂) | 首尾相接 | 逐片关系 | 去重点数 | 捕捉次数（min，max） |
|---|---|---|---|---|---|---|---|
| `results/ckpt/m2_10_fraction` | 16 | 352716 | 352716 | 是 | 全通过 | 10 | 1，1 |
| `results/ckpt/m2_10_mpq` | 16 | 352716 | 352716 | 是 | 全通过 | 10 | 1，1 |
| `results/ckpt/m2_12_fraction` | 16 | 5200300 | 5200300 | 是 | 全通过 | 12 | 1，1 |
| `results/ckpt/m2_12_mpq` | 16 | 5200300 | 5200300 | 是 | 全通过 | 12 | 1，1 |
| `results/ckpt/m2_13_fraction` | 32 | 20058300 | 20058300 | 是 | 全通过 | 13 | 1，1 |
| `results/ckpt/m2_13_mpq` | 16 | 20058300 | 20058300 | 是 | 全通过 | 13 | 1，1 |
| `results/ckpt/m2_14_mpq` | 32 | 77558760 | 77558760 | 是 | 全通过 | 14 | 1，1 |
| `results/ckpt/smoke_m2_2` | 1 | 10 | 10 | 单片 | 全通过 | 3 | 1，1 |
| `results/ckpt/smoke_m2_2_mpq` | 1 | 10 | 10 | 单片 | 全通过 | 3 | 1，1 |
| `results/ckpt/smoke_m2_5` | 1 | 462 | 462 | 单片 | 全通过 | 5 | 6，6 |
| `results/ckpt/smoke_m2_5_mpq` | 1 | 462 | 462 | 单片 | 全通过 | 5 | 6，6 |

「逐片关系」= 每片 `count = end − start` 且 `n_rank_def + n_infeasible + Σfeasible.count = count`。
2. **确定性两连跑检查点**：`det_run1/chunk_0000.json` 与 `det_run2/chunk_0000.json` 逐字节相同（本次 `diff` 退出码 0）；内容为 E10 档（m2 = 5：`count = 462`、`n_rank_def = 170`、`n_infeasible = 262`、5 键各 `count = 6`）。
3. **smoke 键逐字**：m₂ = 2 三键 `1,1`、`1,3/2`、`3/2,1`（各 count = 1）；m₂ = 5 五键（各 count = 6），首键逐字 `1,126797/80000,16077479209/6400000000,2038576131263573/512000000000000,258485337715827265681/40960000000000000000`（含坐标 1，v = 1 的直接痕迹）。
4. **判串七份**（本次重算 md5、字节、S／I／F 直方图、'F' 位置；路径 `scripts/results/route2/`）：

| 文件 | md5 | 字节 | S / I / F | 'F' 位置 |
|---|---|---|---|---|
| `c_m10_t8_decisions.txt` | `b269256bfff877a81fa5a81047a4c958` | 352716 | 295780 / 56926 / 10 | 352706 至 352715 |
| `c_m10_t1_decisions.txt` | 同上（与 t8、py 两份三份 md5 全同） | 352716 | 同上 | 同上 |
| `py_m10_decisions.txt` | 同上 | 352716 | 同上 | 同上 |
| `c_m12_t8_decisions.txt` | `8fb4ba1aef28fdc293b52270985ec35e` | 5200300 | 4752735 / 447553 / 12 | 5200288 至 5200299 |
| `c_m13_t8_decisions.txt` | `152514f874a144554d1dff2ec0570da9` | 20058300 | 18811533 / 1246754 / 13 | 20058287 至 20058299 |
| `c_m14_t8_decisions.txt` | `37921d19726088fb8be115707a749356` | 77558760 | 74098262 / 3460484 / 14 | 77558746 至 77558759 |
| `m5_e10_decisions.txt` | `18e23746174db60150198149b00cd869` | 462 | 170 / 262 / 30 | 首三个 195、197、199；末三个 459、460、461（共 30 个，不连续） |

5. **捕捉子集还原五例（本次亲跑，全部 True）**：用冻结 `r2_common.constraint_list` 与 `solve_exact` 对每档首键的 `examples[0]` 建方程求解，解与键坐标逐位相等且可行（violations 空）：m2_12_mpq（examples `[[12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24]]`）、m2_13_mpq（`[[13, …, 24, 26]]`）、m2_14_mpq、smoke_m2_2（`[[0, 1]]`）、smoke_m2_5（`[[0, 5, 6, 7, 8]]`）。
6. **引擎样本 diff（本次亲跑）**：`results/r5_smoke/sample_m2_10_fraction.txt` 与 `sample_m2_10_mpq.txt`（各 3000 行）、`sample_m2_12_fraction.txt` 与 `sample_m2_12_mpq.txt`（各 1500 行）两组 `diff` 均退出码 0（零差异）。
7. **route-1 门输出复采（本次亲读）**：`threeway-A-positive.txt` 行「本进程检查汇总：PASS = 8，FAIL = 0；总用时 71.1 s」；`threeway-B-negative.txt` 行「[PASS] 预测集与顶点集不相交（分类在 v < 1 时失效）」与「[PASS] 顶点集与预测集相等 = False（实现有判别力，不会无条件输出旋转）」；`threeway-C-boundary.txt` 行「[PASS] 证书 = [(5, 6)]（对照 r2_b_out.txt:97）；实测 [(5, 6)]」；`threeway-A-diff.txt` 行「归一化后逐行一致：True；两文件行数 = 16 / 16」。
8. **r5 判定行与证书复采（本次亲读）**：m12 与 m14 的「每个顶点的（活跃约束法向量秩，活跃约束条数）= [(12, 12)] / [(14, 14)]」、m10 为 `[(10, 10)]`、`smoke_m2_5` 为 `[(5, 6)]`、`smoke_m2_2` 为 `[(2, 2)]` 且 `equal: false` 并列「额外顶点 (1, 1)、(1, 3/2)、(3/2, 1)」与「缺失顶点 (3/5, 9/10)、(9/10, 3/5)」。

### 9.5 账本衔接两处与 learnings 的现行措辞（逐字，供 (c) 对接）

1. `ledger.md:24`（现行 §0.2 第 4 条，md5 `8e0b44e3ebbf795dc393e4fa559cbee3`）逐字：「4. **证据卫生与复现包**：重跑改动后的 `route1_extra.py`（约 42 分钟）与 `route4_adv_rig.py` 的 [F] 第 4、5 点及 [G] 段；对 K*、K* ± 1、2K* 做扰动检验，排查判据恒真；修 `route2_enum.py` 的 E4 TypeError。」
2. `ledger.md:112`（现行 §1.4 第 2 条）逐字（节选）：「……顶点识别的一般证明虽对任意 m₂ 写成，机器核对只到 m₂ = 10 的全活跃子集穷举（不依赖 (L1)）与 12 个参数集的约简穷举（依赖 (L1)），m₂ = 12 的全穷举未跑（投影约 72 分钟），m₂ = 20、47、91 的独立穷举不可达。」
3. `ledger.md:123`（§1.5 内，该语义的现存唯一处）逐字（节选）：「……第四优先：顶点识别的机器核对升一档；第五优先：Theorem 23 第 7 步 ε 差异定位。」
4. **旧句与漂移（本次亲读）**：`tracks/vertex-m12/plan.md:25` 逐字引当时账本「`ledger.md:25`（节 0.2 第 4 条）：「顶点识别的机器核对提升一档：跑 m₂ = 12 的不依赖 (L1) 全活跃子集穷举（C(25,12) = 5200300 个子集，投影约 72 分钟），或把 det 与秩论证做成 Lean 引理（需先装 Lean）」——列为第 1 轮后的第 4 优先」。现行账本 `:25` 已是 §0.2 第 5 条（较低优先），旧句不在现行文本中；「升一档」语义仅存于 `:123` 与 `plan.md:25` 的引文。
5. `learnings.md:45`（三之 11）逐字（节选）：「……教训：升核对档位时选 m₂ = 12（C(25,12) = 5200300，投影约 72 分钟）这类「还跑得动」的档，而不是继续加参数集；不可达档要如实写成核对边界。」

### 9.6 边界句复采（清点，不裁决）

1. **范围声明落点（行号本次实测）**：`route-3.md:227`（四档 {10, 12, 13, 14}；含「m₂ ≥ 15 未跑」与「δ 严格区间内部逐点检验未做，只做了两个端点」）与 `route-2.md:371`（五档 {5, 10, 12, 13, 14}；含两条缺口：Python 分片覆盖、13 档 'S' 未过第二路）。
2. **m₂ = 14 更正**：`route-5.md:100`（见 9.2 第 1.1 条）；`route-5.md:121`（C 条「判定为真」，mpq 单引擎、32 分片、墙钟 2912.2 s）。
3. **引擎与覆盖不对称**：`route-5.md:330` 逐字（节选）「引擎覆盖：10、12、13 为双引擎全量、判定行对称 `diff` 零差异，14 为 mpq 单引擎全量、fraction 14 未跑」；`route-2.md:255` Python 覆盖率 3.47%／0.59%／0.26%；本附录 9.2 第 2.4 条的 impl1 覆盖止于 m12。
4. **确定性边界**：`route-5.md:98` 逐字（节选）「……这一点在 m₂ = 12、13、14 档上未再两连跑（成本考虑，属未核实而非已证）。」；`route-5.md:97` 的脚本版本差异（m10、m12、m13 用 `a0511d9861e56764a7eeaa796385e359` 版，m14 用 `4fd20e6737c51dda3e88e2f6c0ca2345` 版；「无害」由 1500 子集样本 `diff` 零差异支撑——本附录另测 fraction 与 mpq 的 1500 行样本亦零差异，见 9.4 第 6 条）。
5. **读法边界（闭化）**：`route-5.md:96`（第七条：勘误回绕约束严格号，本核按既有读法闭化）；`frozen-spec.md` 约束表逐字「（C2）y_{j+1} ≤ δ y_j（j = 1 至 m₂，指标循环，末条即回绕 y_1 ≤ δ y_{m₂}）」。
6. **δ 为严格下界**：`route-2.md:12` 逐字（节选）「δ = 126797/80000，即 log₂3 的严格下界」；`route-5.md:340` 逐字（节选）「参数（δ = 126797/80000，即 δ 的严格下界；W = 2000）」；`frozen-spec.md` 二之 1 的整数幂判据（2^15849625 < 3^10000000 < 2^15849626）。
7. **负载背景**：`route-3.md:207` 逐字（节选）「本机同时段有其它 actor 的重负载扫描（load average 峰值 214.63），第三节所有墙钟都在该背景下测得……」

### 9.7 本次亲跑命令一览（全部只读；可逐条复跑）

工作目录除注明外为 `collatz-attack/70-research/tracks/vertex-m12/cycle-1`；`PY` = `collatz-attack/20-experiments/.venv/bin/python`（本次实测 gmpy2 版本 2.3.2）。

1. **检查点全量复算**：`cd results/ckpt && python3 - <<'EOF' …`（逐目录 `json.load` 全部 `chunk_*.json`：片数、`Σcount`、首尾相接、`count = end − start`、`n_rank_def + n_infeasible + Σfeasible.count = count`、去重与捕捉次数；含 `det_run1`、`det_run2`）。
2. **判串身份与直方图**：`cd scripts/results/route2 && python3 - <<'EOF' …`（流式 md5、逐字节 S／I／F 计数与 'F' 位置，七份）。
3. **捕捉子集还原五例**：`"$PY" - <<'EOF' …`（`sys.path` 加 `scripts/frozen`，调 `r2_common.constraint_list` 与 `r2_common.solve_exact`，Fraction 与键坐标逐位比较；参数取被核对档自身 δ、W）。
4. **C 日志 grep**：`grep -E "DECISION_COUNTS|CROSSCHECK|THREAD_SETS_SUM|SETS_EQUAL|MISMATCHES_TOTAL|EXIT_OK" scripts/results/route2/c_m1*_t8_log.txt py_m10_log.txt`。
5. **r5 判定行对称 diff**：`cd results/logs && grep -E "子集总数|分检|可行顶点数|每个顶点的|每个可行解|独立性" r5_full_m2_12_mpq.log > /tmp/a && … _fraction.log > /tmp/b && diff /tmp/a /tmp/b`（m10、m12、m13 三档，退出码均 0）。
6. **样本 diff**：`cd results/r5_smoke && diff sample_m2_10_fraction.txt sample_m2_10_mpq.txt && diff sample_m2_12_fraction.txt sample_m2_12_mpq.txt`（退出码均 0）。
7. **对拍落点逐字**：`cat results/route3_xcheck_m12_allsubsets.json results/route3_xcheck_m10_allsubsets.json results/route3_vs_other_m12.json …`；`python3 -c` 读 `route3_xcheck_m12_compare.json` 的关键字段。
8. **两实现 JSON 键差与候选**：`python3 -c`（impl1 与 impl2 顶层键集差、`agg`、候选编号列表、首候选）。
9. **身份测量**：`md5 -q` 与 `wc -l` 于 9.1 表内全部文件与七份判串、检查点逐片。
10. **账本与教训件**：`awk` 打印 `ledger.md:17` 至 `:26`、`:108` 至 `:124` 与 `learnings.md:41` 至 `:57`。

**未跑（逐条）**：m₂ = 10、12、13、14 的任何全量枚举或抽点重跑；`route3_xcheck.py` 任何模式；`r5_vm12_enum.py`（含 `--resume`）；C 二进制与 Python 参考；勘误与 `hercher5` 的 PDF 重开或重渲染；`three_way_baseline.py` 重跑。以上未跑项按任务硬约束与角色边界如实登记，不计入任何「通过」。

### 9.8 未打开、未跑、未能核实（逐条）

1. **未打开内容**：`scripts/route2_vm_core.c`、`scripts/route3_defs.py`、`scripts/three_way_baseline.py`、`scripts/diff_norm.py`（本次只测了身份）；`materials/hercher5.pdf` 与 `materials/corrigendum.pdf`（本次未重开、未渲染；本附录的 δ 与闭化读法引用自 `frozen-spec.md`、`route-2.md:12`、`route-5.md:96`、`:340`，未回 PDF）；`.mimosa/` 内部文件（同首版第七节）。
2. **未重读**：`results/md5-manifest.txt`（首版通读；本次仅测 md5）；`results/r5_smoke/` 的 `probe_*` 日志（未打开内容）。
3. **未核实**：`r5_smoke/sample_*.txt` 与 `det_run1/2` 的生成命令未定位（本次只对既有文件做了字节级比对）；`route-2.md:271` 的内联测速脚本仍未落盘（首版登记沿用）。
4. **行号差异如实登记**：`route3_impl1_mpqscan.py` 的返回行本次 rg 实测为 `:105`、`:108`、`:111`、`:116`、`:127`；首版记 `:104`、`:107` 至 `:116`（文件 md5 相同，属计数口径差 1，非文件差异）。

### 9.9 复采者备注（只报事实，不裁决）

1. 若 (a) 要写「对拍只比点串与判定码」的可执行定义：判据行与两实现的非候选返回行都在 9.3；「singular 与 infeasible 的类别差异不可见」的直接机制 = 两实现非候选判定码恒 0 加 xcheck 不比 `kind`。
2. 若 (b) 的 P3 要按档打印「活跃秩与活跃条数」：主档四档为 `(m₂, m₂)`（r5 四档日志行逐档可见），边界档 m₂ = 5 为 `(5, 6)`（`r5_smoke` 与 `threeway-C-boundary.txt` 两处），阴性档 m₂ = 2 为 `(2, 2)` 且 `equal: false` 并列额外与缺失顶点（`results/r5_smoke/smoke_m2_2_fraction.log`）。
3. 若 (c) 要对接账本：现行 §0.2 第 4 条已不含顶点句（9.5 第 1 条），§1.4 第 2 条的「未跑」句仍是现行文本（9.5 第 2 条），「升一档」句只在 `:123`（9.5 第 3 条）；三处行号、md5 与漂移事实均在 9.5。

**复采登记（2026 年 10 月 28 日，落盘后补录）**：前缀（行 1 至 391，首版全文）md5 = `df9c0278acdafb7b06eb35719c05faef`（落盘后用 `head -n 391 materials.md | md5` 复测相等）；本附录正文（行 392 至 546）共 155 行、md5 = `1f5e736a0f5940795018b201a134e56a`；整文件截至第 546 行（不含本登记行）md5 = `293d2285129f1d9bf77cb822202601b8`、行数 546。本登记行之后如有增改，均不计入上述身份。
