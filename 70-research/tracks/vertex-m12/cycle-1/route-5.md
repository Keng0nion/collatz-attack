# vertex-m12 轨道路线五：推档与未证边界文书（首轮报告）

撰写人：攻击轮路线五子代理（「推档与未证边界文书」路线）
日期：2026 年 10 月 27 日至 28 日（跨零点完成 m₂ = 14 档与 13 档 fraction 交叉核对）
路线：vertex-m12（顶点识别的机器核对升一档），cycleNumber = 1，依据 `70-research/tracks/vertex-m12/plan.md`（177 行）节五路线五与节八边界声明模板
本文件性质：**机器核对报告（附覆盖范围）**。参数与定义先冻结后开跑；每个数字都能 grep 到本报告引用的原始日志；凡本轮未跑、未证处逐处标明。本文件不是证明，也不把有限档位的核对写成全称结论（「该范围之外仍属未证」声明见节六）。

产物布局（本轨道目录 `70-research/tracks/vertex-m12/cycle-1/` 下）：

1. `scripts/r5_vm12_enum.py`：本报告的唯一枚举实现（Python multiprocessing 八核；Fraction 与 gmpy2.mpq 两套精确算术引擎；分片确定性切分；逐片断点续跑）。
2. `results/logs/`：本报告引用的全部原始日志与计时文件（`r5_*.log`、`r5_*.time`）。
3. `results/ckpt/`：逐分片校验点（JSON，每片含 [start, end)、计数、分检计数、可行解与捕捉子集例）。
4. `results/r5_smoke/`：冒烟与小档对照日志（含两实现的逐子集样本落盘）。

---

## 一、要证明或要检验的精确陈述（开跑前冻结）

### 1.1 命题 R(m₂, δ, W)

记 P(m₂, δ, W) ⊂ R^{m₂} 为满足下列约束的点集（逐字对应 `70-research/cycle-1/scripts/r2_common.py` 的 `constraint_list`，该文件版本身份见 1.4）：

1. (C1) y_j ≥ 1，j = 1 至 m₂（m₂ 条）；
2. (C2) y_{j+1} ≤ δ·y_j，指标按 m₂ 循环（m₂ 条；末条即回绕约束 x_{m−m₂+1} ≤ δ x_m）；
3. (C3) Σ_{j=1}^{m₂} y_j ≥ W（1 条）。

共 2m₂ + 1 条约束。记 v = W(δ−1)/(δ^{m₂}−1)；记 V_r（r = 0 至 m₂−1）为向量 (v·δ^r, v·δ^{r+1}, …, v·δ^{r+m₂−1})（指数按 m₂ 循环归约）。

**命题 R(m₂, δ, W)**：P(m₂, δ, W) 的可行顶点集（极点集）恰为 {V_0, …, V_{m₂−1}}。即「可行顶点集恰是 m₂ 个循环旋转」：既不多（每个顶点都是某个循环旋转）、也不少（每个循环旋转都是顶点）。

### 1.2 参数冻结（本轮首跑口径）

1. δ = 126797/80000，即 δ 的严格下界（由 `r2_common.delta_rigorous_bounds(10**7)` 给出；判据只用整数幂比较，2^p < 3^q 等价于 p/q < log₂3；上界为 7924813/5000000）。本轮全部档位同此 δ。首跑日志头部逐次打印该值（`results/logs/r5_full_m2_10_fraction.log` 第 3 行等）。
2. W = 2000（与既有 m₂ = 10 阳性对照同参，保证两档可比；W = 2000 在 m₂ = 10、12、13、14 四档上均满足 (P1) 阈值 (δ^{m₂}−1)/(δ−1)，四档阈值依次为 169.316390、427.925703、679.246192、1077.579742，六位小数；出处为材料 `materials.md` 第 5.3 节逐字输出与本轮日志的 `v` 行）。
3. 档位：m₂ = 10（阳性对照）、12（主档）、13、14（视实测成本推档）。
4. 读法冻结（非本轮新证，照项目既有登记）：勘误原文的回绕约束是严格号（x_{m−m₂+1} < δ x_m）；本核对照项目既有读法把多面体闭化（严格号读作 ≤）。依据的既有登记：`60-audits/hercher-t21/rederivation-erratum.md` 第 2 节第 3 条（材料 `materials.md` 第 4.6 节逐字转录：「由于最终只需要 S 的上界，把这条读成『≤』并把多面体闭化是合法的，也才能谈『顶点』」）。这也是 `r2_common.constraint_list` 的实现口径（回绕并入 m₂ 条循环链，用非严格号）。

### 1.3 本核对的方向（写死，防误读）

1. 本核对在 δ 的严格下界 δ_lo 上做（δ_lo < log₂3）。δ 只出现在 C2 右端，δ 增大使 P 单调变大；故本核对不对「δ = log₂3 的 P」直接作断语，也不对任何其他 δ 作断语（见节六）。
2. W = 2000 只是一个取值；应用档的 W = (m₂/m)·K（K 为圈中奇数个数，量级 1e11）不在本轮参数内（见节六）。
3. 本核对是机器核对：给出有限档位、有限参数上的穷举判定（条件完备：见节二第 2、3 步），不是全称证明。

### 1.4 依赖清单（「不依赖任何引理」落到显式清单）

数学侧（允许依赖）：

1. 约束表逐字转写（勘误的 C1、C2、C3；出处见上）；
2. 精确有理算术（fractions.Fraction 与 gmpy2.mpq 两套，互相对拍；无浮点参与任何判决）；
3. 组合枚举完备性（`itertools.combinations` 无重无漏，加本轮自带的覆盖计数校验）；
4. 初等线性代数：点 y ∈ P 是极点当且仅当 y 处活跃约束的法向量张满 R^{m₂}（证明见节二第 2 步）。

代码侧（逐函数；路径基准为 `collatz-attack/`）：

1. `70-research/cycle-1/scripts/r2_common.py`（244 行，md5 `cfee819667c0883e73732f03d2dc8bef`）的 `delta_rigorous_bounds`（`:54` 至 `:70`）、`constraint_list`（`:162` 至 `:180`）、`solve_exact`（`:183` 至 `:217`）、`feasible`（`:145` 至 `:159`）、`v_vertex`（`:134` 至 `:136`）、`vertex`（`:139` 至 `:142`）；
2. `70-research/cycle-1/scripts/r2_j_independent_vertices.py`（272 行，md5 `4b8ce2a500d8ca9021fd0178deca637e`）的 A 段语义（`full_enumeration`，`:92` 至 `:114`）作为对拍基准；本报告的 `rank_exact`、`active_rank` 与该文件的同名函数逐行同义；
3. 本轮脚本 `r5_vm12_enum.py` 的 `solve_exact_mpq`、`feasible_mpq` 是上述 `solve_exact`、`feasible` 的逐行同义镜像（差分抽验见节二第 4 步）。

禁止侧（搜索本体一律不碰；违者本核对降级为循环论证）：

1. (L1)「y_j = 1 不可行」及其判据 (δ^{m₂}−1)/(δ−1) < W；
2. v 的任何数值信息（v 只出现在两个地方：被判检验的解析族对照集构造、以及事后打印；均不参与搜索判定）；
3. 凸性论证、顶点引理的任何结论、勘误的顶点论证本身。

版本钉死（运行时断言，不符即中止）：上述两个 md5 逐次在日志头打印并断言一致；本轮全部日志均报「一致 = True」。本脚本自身的 md5 也逐次打印在日志头（各档日志的 `脚本 md5` 行；最终版本见节五）。

### 1.5 环境

python 3.12.7（`20-experiments/.venv/bin/python`）、gmpy2 2.3.2、mpmath 1.3.0；机器 hw.ncpu = 8、hw.physicalcpu = 8。并行用 Python multiprocessing（脚本落成文件并加 `__main__` 守卫，避免 spawn 找不到主模块的已知失败模式）。分片按组合字典序下标 [start, end) 连续切分（确定性子集编号区间，无重无漏），父进程断言 Σ(end−start) = C(2m₂+1, m₂)。

---

## 二、编号论证

1. **第 1 步（已证；代码语义）——语义冻结与钉死**：约束表、判定语义、参数、md5 钉死如节一；凡 md5 不符脚本即 `sys.exit(2)` 中止（本轮无触发）。日志头部逐次打印 δ、W、v 的精确分数、组合数与两依赖文件 md5。
2. **第 2 步（已证；初等引理，本轮纸面，未形式化）——枚举完备引理**：点 y ∈ P 是极点，当且仅当 y 处活跃约束的法向量张满 R^{m₂}。
   （⇒）若活跃法向量张不满，取非零 d 与全部活跃法向量正交。则对小 ε > 0，y ± εd 仍满足全部活跃约束（取等在两侧都保持）与全部非活跃约束（它们有严格裕量，ε 足够小时不破），故 y 是两可行点的中点，非极点。
   （⇐）若活跃法向量张满，取其中 m₂ 条线性无关者组成 S（满秩 m₂ 元组必存在）。设 y = (y′ + y″)/2 且 y′、y″ ∈ P。对 S 中每条约束（已转为统一的 ≥ 形式）：y′、y″ 在该约束都取 ≥ 等号右端，而 y 取等号，取平均迫使 y′、y″ 都取等号，于是 A_S(y′ − y) = 0，因 A_S 满秩得 y′ = y。故 y 是极点。
   推论：极点集 = {y : 存在 m₂ 元约束子集 S，A_S 满秩，y 是 A_S y = b_S 的唯一解，且 y ∈ P}。枚举全部 C(2m₂+1, m₂) 个 S 即不漏任何极点；同时任何被枚举命中的点（满秩、精确可行）必是极点，不会误报。注：S 允许不是极小活跃集（带冗余活跃集的极点会被其任意满秩 m₂ 元子集捕获，且可能被多个子集捕获；「捕捉个数」逐档记录在日志）。
3. **第 3 步（已证；组合计数与本轮断言）——覆盖无重无漏**：候选子集总数 C(2m₂+1, m₂)，本轮实算（脚本用 `math.comb` 打印在日志头）：m₂ = 10 为 352716、12 为 5200300、13 为 20058300、14 为 77558760。分片为连续下标区间，父进程断言区间长度之和等于组合总数，且各 worker 计数之和等于同一值（各档日志均报「覆盖校验 = True」与「已处理 = 总数」）。
4. **第 4 步（已证；差分抽验，本轮实跑）——两套算术引擎逐子集同义**：在 m₂ = 10 抽 3000 个子集、m₂ = 12 抽 1500 个子集（三段窗口：头部、中段、末段），两实现逐条输出（每条的秩亏秩值或不可行判定或可行坐标的精确分数）逐字相同，`diff` 零差异（`results/r5_smoke/sample_m2_10_*.txt`、`sample_m2_12_*.txt`）。另在 E10 配置与 m₂ = 2 阴性配置上两实现完全同输出（`results/r5_smoke/smoke_m2_5_*.log`、`smoke_m2_2_*.log`）。判定：mpq 镜像在抽验范围内与冻结实现无分歧。
5. **第 5 步（机器核对，附范围；本轮实跑）——各档全量判定**：见节五原始输出。判定口径：「可行顶点数」= 全量穷举收集的去重可行解个数；「与解析的 m₂ 个循环旋转相同」= 集合精确相等（两个方向都查：多出的顶点逐一列出并附证书，缺失的顶点也逐一列出）。
6. **第 6 步（等价于原命题）**：对固定 (m₂, δ, W)，「可行顶点集恰为 m₂ 个循环旋转」就是命题 R 在该参数点上的实例；机器核对给出该实例的真值，不给出 R 的全称真值。
7. **第 7 步（缺口；明确写出，不省略）**：δ 从 δ_lo 到 log₂3 的转移、W 从 2000 到应用值的转移、m₂ 从本轮最大档到 20、47、91 的转移，本轮都没有做，也不由本核对蕴含；一般 m₂ 的顶点识别仍只有项目内纸面论证（route-1 的 Step 8′ 等），未形式化（本机无 Lean 与 Coq）。逐条清单见节六。

---

## 三、失败点清单（本轮踩到或绕开的，逐条写具体）

1. **阳性对照的时间数字不复现（属预期波动，已登记）**：原脚本 `r2_j_independent_vertices.py A` 本轮单核实跑 71.8 s（`results/logs/r5_anchor_r2j_A_original.txt`，`time` 行 user 68.15 s），基线 `r2_j_A.time`（`results/verify-round2/r2_j_A.time`）是 `real 62.49 / user 61.78`。差异只在用时行；三条判定行（子集总数 352716、10 个循环旋转 True、证书 (10,10)）逐字相同。原因推断（我的推断）：本次机器上有其它 actor 的负载。本报告的时间数字一律标注是否含该影响。
2. **既有 0.83 毫秒/个 的成本登记与实测不符（以实测为准）**：route-2 登记的 `m2 = 12：实测 0.83 ms/个`（该测速脚本未落盘、不可复跑，材料 `materials.md` 第 3.1 节第 3 条已登记此缺陷）。本轮八核实跑测得 fraction 引擎每子集 CPU 0.5741 ms（`SUMMARY_JSON` 的 `ms_per_subset_cpu`，m₂ = 12），换算墙上时间每子集 0.1054 ms（8 核，含负载）。即旧登记高估约 1.45 倍；本报告的性能曲线以 5.1 的实测表为准，并把 0.83 降级为历史登记。
3. **每子集成本沿字典序强不均匀（对「倍率」口径的影响）**：m₂ = 12 fraction 档的 16 个分片各 325019 子集，首片 147.0 s、末片 348.3 s（分片行，`results/logs/r5_full_m2_12_fraction.log`）；m₂ = 13 mpq 档首片 266.7 s、末片 217.0 s（但后浪分片启动晚约 270 s，见分片行的「累计墙钟」列）。故本报告所有「每子集毫秒数」都是按子集总数平均的口径；分片耗时读数本身含抢占等待，只作趋势证据，不作 CPU 成本。
4. **机器负载对墙钟的挤压（口径已标注）**：由 CPU 与墙钟之比推得本轮各档实际核当量约 4.6 至 5.7（m₂ = 13 mpq：2923.4 / 516.4 = 5.66；m₂ = 14 mpq：13477.7 / 2912.2 = 4.63，为本轮最低），低于 8，原因推断（我的推断）为其它 actor 并发占核。故倍率与投影一律给 CPU 口径与墙钟口径两列。
5. **mpq 镜像的验证范围（未做全量的部分写明）**：逐子集差分抽验覆盖三段窗口各 1000（m₂ = 10）与各 500（m₂ = 12）个子集（零差异）；全量层面的双实现一致覆盖 m₂ = 10、12、13 三档（两引擎全量；判定行对称 `diff` 零差异）；m₂ = 14 档为 mpq 单引擎（fraction 14 全量未跑，见节四 C 条）。
6. **分片跳跃的额外枚举成本**：每个分片用 `itertools.islice` 从组合字典序头部跳过 start 个组合，跳过成本计入 CPU 与墙钟（未做组合 unrank 优化）。这不改变覆盖（父进程断言 Σ 区间长 = 组合总数，且各 worker 计数之和相等）。
7. **闭化读法与勘误严格号之差（既有登记，不是本轮新发现；引用照抄）**：勘误原文回绕约束是严格号（x_{m−m₂+1} < δ x_m），本核照项目既有读法闭化（≤）。这一步是「谈顶点」的前提之一（`rederivation-erratum.md` 第 2 节第 3 条，材料 `materials.md` 第 4.6 节）。凡引用本报告的判定时，此读法必须一并引用。
8. **脚本版本差异（一次，已用差分验证其无害）**：m₂ = 10、12、13 三档由同一版本（日志头的 `脚本 md5 = a0511d9861e56764a7eeaa796385e359`）跑出；m₂ = 14 档由当前版本（`脚本 md5 = 4fd20e6737c51dda3e88e2f6c0ca2345`）跑出，唯一改动是分片派发顺序（`--interleave`，按下标两端交替派发以降拖尾），不触及分片内容、判定语义与覆盖断言。该「无害」不是口头担保：当前版本在 m₂ = 12 的三段窗口样本（1500 子集）与旧版本样本逐字相同（`diff` 零差异，实测）。
9. **确定性检查的边界**：E10 配置（m₂ = 5、W 取阈值）两连跑（同版本）除日志头的 tag 行外零差异（实测）。代码中无随机性来源（`Det` 发生器未用于枚举；组合枚举与算术均确定），故重复运行应逐位一致；这一点在 m₂ = 12、13、14 档上未再两连跑（成本考虑，属未核实而非已证）。
10. **未跑清单（本轮明确不做）**：fraction 引擎的 14 档全量（13 档的 fraction 交叉核对已于 2026 年 10 月 28 日 02:46 完成，见节四 B 条）；C 主实现（plan 路线二的产物线，本轮未写一行 C 枚举）；B 段 z3 重跑；Lean 形式化（本机无工具链，沿用既有登记）；m₂ = 20、47、91 的任何穷举（组合规模不可达，见节六）。
11. **会话环境事故与更正（必须登记，防误读）**：2026 年 10 月 28 日 00:50 前后起约半小时，本会话的工具输出被环境重复注入的一条协调消息（内容含「再做 P3.1（若已完成）或 P3.2（p-adic 或分圆路径），完成后按 schema 返回」）阻断。该消息所指编号与本轨道不符（本轨道只有「路线一至五」；全库检索「P3.1」「P3.2」「p-adic」「分圆」零命中；本轮未据它虚构任何新数学路线；按其可执行解读——P3.1 对应 m₂ = 13、P3.2 对应 m₂ = 14——两者均已实跑完成）。**更正**：工具恢复后重查日志，已读到 m₂ = 14 的全量判定为真（见节四 C 条与节五 5.4）；此前一次提交里「m₂ = 14 判定未读取」的表述作废，以本报告节四 C 条为准。

---

## 四、局部新结论及其独立验证方式

本节的每条都是「机器核对（附范围）」级；独立验证方式写的是复跑路径，不是一次性观察。

1. **A 条（m₂ = 12 主档，判定为真）**：在 (δ, W) = (126797/80000, 2000) 上，C(25,12) = 5200300 个活跃子集全量穷举的判定是「可行顶点集恰为 12 个循环旋转」。原始行逐字（`results/logs/r5_full_m2_12_fraction.log` 与 `..._mpq.log`；两文件的判定六行与分检计数经对称 `diff` 逐字相同、零差异，仅分块与用时行不同）：
   > `    子集总数 C(25,12) = 5200300；已处理 = 5200300（覆盖校验 = True）`
   > `    分检：秩亏/不相容 = 4752735，满秩不可行 = 447553，满秩可行子集 = 12`
   > `    可行顶点数 = 12；与解析的 m2 = 12 个循环旋转相同 = True（解析集大小 12）`
   > `    每个顶点的（活跃约束法向量秩，活跃约束条数）= [(12, 12)]`
   > `    每个可行解被活跃子集捕捉的个数（升序）= [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]`
   独立验证：按 5.1 命令行重跑（fraction 8 核约 9 分钟、mpq 约 2 分钟量级）；或对已完成分片用 `--resume` 复算汇总；对拍 `SUMMARY_JSON` 的 `equal`、`n_distinct_feasible`、`certs` 三个字段。
2. **B 条（m₂ = 13，判定为真；双引擎全量）**：同上参数，C(27,13) = 20058300 个活跃子集的判定为「可行顶点集恰为 13 个循环旋转」，两引擎（mpq 与 fraction）各自全量跑完且判定行对称 `diff` 零差异。原始行逐字（`results/logs/r5_full_m2_13_mpq.log` 与 `results/logs/r5_full_m2_13_fraction.log`，两文件此六行逐字相同）：
   > `    子集总数 C(27,13) = 20058300；已处理 = 20058300（覆盖校验 = True）`
   > `    分检：秩亏/不相容 = 18811533，满秩不可行 = 1246754，满秩可行子集 = 13`
   > `    可行顶点数 = 13；与解析的 m2 = 13 个循环旋转相同 = True（解析集大小 13）`
   > `    每个顶点的（活跃约束法向量秩，活跃约束条数）= [(13, 13)]`
   性能对照（两引擎同一档）：mpq 墙钟 516.4 s、CPU 2923.4 s、每子集 CPU 0.1457 ms；fraction 墙钟 3513.5 s（`real 3513.86 / user 13956.00 / sys 84.86`）、CPU 14040.7 s、每子集 CPU 0.7000 ms；两者之比（fraction/mpq）4.80。独立验证：按 5.1 命令行重跑（任一引擎或两引擎）；或对任一档校验点 `results/ckpt/m2_13_mpq/`、`m2_13_fraction/` 加 `--resume` 复核汇总。
3. **C 条（m₂ = 14，判定为真）**：mpq 全量（32 分片、两端交替派发；2026 年 10 月 28 日 00:06 启动，00:55 完成；墙钟 2912.2 s）。原始行逐字（`results/logs/r5_full_m2_14_mpq.log`；摘录另存 `results/logs/r5_full_m2_14_mpq_verdict.txt`）：
   > `    子集总数 C(29,14) = 77558760；已处理 = 77558760（覆盖校验 = True）`
   > `    分检：秩亏/不相容 = 74098262，满秩不可行 = 3460484，满秩可行子集 = 14`
   > `    可行顶点数 = 14；与解析的 m2 = 14 个循环旋转相同 = True（解析集大小 14）`
   > `    每个顶点的（活跃约束法向量秩，活跃约束条数）= [(14, 14)]`
   一致性算术（本轮实算）：74098262 + 3460484 + 14 = 77558760；32 个分片行的 `count=` 之和亦等于 77558760。独立验证：按 5.1 命令行重跑，或对既有校验点 `results/ckpt/m2_14_mpq/` 加 `--resume` 复核汇总。引擎为 mpq 单引擎（fraction 14 全量未跑，节三第 10 条）。
4. **D 条（性能曲线与倍率实测，口径两列）**：

   | 档位 | 子集总数 | 引擎 | CPU 秒（user+sys 含子进程） | 每子集 CPU 毫秒 | 墙钟秒 | 墙钟每子集毫秒 |
   |---|---|---|---|---|---|---|
   | m₂ = 10 | 352716 | fraction | 91.6 | 0.2596 | 16.0 | 0.0455 |
   | m₂ = 10 | 352716 | mpq | 18.2 | 0.0515 | 3.3 | 0.0095 |
   | m₂ = 12 | 5200300 | fraction | 2985.3 | 0.5741 | 547.9 | 0.1054 |
   | m₂ = 12 | 5200300 | mpq | 690.1 | 0.1327 | 122.9 | 0.0236 |
   | m₂ = 13 | 20058300 | mpq | 2923.4 | 0.1457 | 516.4 | 0.0257 |
   | m₂ = 13 | 20058300 | fraction | 14040.7 | 0.7000 | 3513.5 | 0.1752 |
   | m₂ = 14 | 77558760 | mpq | 13477.7 | 0.1738 | 2912.2 | 0.0375 |
   倍率（组合数比）：13/12 = 3.857、14/12 = 14.914、14/13 = 3.867（`math.comb` 实算，日志头逐档打印）。成本比（每子集 CPU 毫秒）：fraction 12/10 = 2.211、13/12 = 1.219；mpq 12/10 = 2.577、13/12 = 1.098、14/13 = 1.193、14/12 = 1.310；两引擎比（fraction/mpq）：m₂ = 10 约 5.0、12 约 4.3、13 约 4.8。独立验证：逐格 grep 对应日志的 `SUMMARY_JSON`。
5. **E 条（成本模型修正）**：把「m₂ = 12 需 0.83 毫秒/个、单核投影 72 分钟」的旧登记修正为「fraction 每子集 CPU 0.5741 毫秒，mpq 0.1327 毫秒；八核墙钟 fraction 547.9 秒、mpq 122.9 秒（本机本轮负载下）」。独立验证：节五命令行复跑 + `SUMMARY_JSON` 字段。
6. **F 条（枚举的结构观察，四档实测）**：全部「捕捉到可行顶点的活跃子集」在字典序里恰为最后 m₂ 个，形状为「和约束（指标 2m₂）+ 链约束（指标 m₂ 至 2m₂−1）中去掉一个」，每个顶点被且仅被一个子集捕捉（捕捉个数向量全为 1）。证据：四档校验点 JSON 逐条取出（`results/ckpt/m2_10_fraction/`、`m2_12_fraction/`、`m2_13_mpq/`、`m2_14_mpq/`），如 m₂ = 14 档的 14 个捕捉子集即：{14,…,27}∪{28} 逐一去掉一个链指标（形状检查：每个元组都含指标 28 且其余元素在 14 至 27，实测通过）。**性质上这是观察，不是定理**；它给出的独立验证是：从任一档校验点 JSON 用两行 Python 重新抽取（节五 5.1 第 6 条的命令）。
7. **G 条（判别力证据，阴性档）**：同一枚举在 (m₂, δ, W) = (2, 3/2, 3/2) 上正确报「不相同 = False」，并逐条列出 3 个非解析顶点（(1,1)、(1,3/2)、(3/2,1)）与 2 个缺失解析点（(3/5,9/10)、(9/10,3/5)），与 `route-1.md:319` 逐项一致。说明这套机器核对不是「无条件输出 True」。证据：`results/r5_smoke/smoke_m2_2_fraction.log` 与 `..._mpq.log`（两引擎同输出）。

---

## 五、完整命令行与原始输出摘要

### 5.1 命令行（全部可在本机逐条复跑）

公共变量：

```bash
PY="/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python"
TRACK="/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/vertex-m12/cycle-1"
REF="/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts"
```

一键复跑脚本：`scripts/r5_run_all.sh`（子命令 `anchors`、`full10`、`full12`、`full13`、`full13fraction`、`full14`、`probes`，与本节的命令一一对应，输出路径相同）。

1. 阳性对照（原脚本、单核，复现基线）：

```bash
cd "$REF"
{ time "$PY" r2_j_independent_vertices.py A ; } > "$TRACK/results/logs/r5_anchor_r2j_A_original.txt" 2>&1
```

关键原始行（逐字）：`    子集总数 C(21,10) = 352716，用时 71.8 s`；`    可行顶点数 = 10；与解析的 m2 = 10 个循环旋转相同 = True（解析集大小 10）`；`    每个顶点的（活跃约束法向量秩，活跃约束条数）= [(10, 10)]`；`time` 行 `68.15s user 0.29s system 94% cpu 1:12.09 total`。与基线 `r2_j_A.txt`（62.3 s）的差异只在用时行。

2. 阴性对照（原脚本）：

```bash
cd "$REF"
{ time "$PY" r1_selfcheck.py ; } > "$TRACK/results/logs/r5_anchor_r1_selfcheck_original.txt" 2>&1
```

关键原始行（逐字，`[3]` 段）：`   实际顶点集合 = (Fraction(1, 1), Fraction(1, 1))；(Fraction(1, 1), Fraction(3, 2))；(Fraction(3, 2), Fraction(1, 1))`；`   PASS 预测族与顶点集合不相交（分类在 v < 1 时失效）`；`   失败项数 = 0`。

3. 八核主脚本（本报告全部判定行与性能数字的出处）：

```bash
cd "$TRACK/scripts"
/usr/bin/time -p "$PY" r5_vm12_enum.py --m2 10 --W 2000 --impl fraction --workers 8 --chunks 16 --tag m2_10_fraction \
    > "$TRACK/results/logs/r5_full_m2_10_fraction.log" 2> "$TRACK/results/logs/r5_full_m2_10_fraction.time"
/usr/bin/time -p "$PY" r5_vm12_enum.py --m2 10 --W 2000 --impl mpq      --workers 8 --chunks 16 --tag m2_10_mpq \
    > "$TRACK/results/logs/r5_full_m2_10_mpq.log" 2> "$TRACK/results/logs/r5_full_m2_10_mpq.time"
/usr/bin/time -p "$PY" r5_vm12_enum.py --m2 12 --W 2000 --impl fraction --workers 8 --chunks 16 --tag m2_12_fraction \
    > "$TRACK/results/logs/r5_full_m2_12_fraction.log" 2> "$TRACK/results/logs/r5_full_m2_12_fraction.time"
/usr/bin/time -p "$PY" r5_vm12_enum.py --m2 12 --W 2000 --impl mpq      --workers 8 --chunks 16 --tag m2_12_mpq \
    > "$TRACK/results/logs/r5_full_m2_12_mpq.log" 2> "$TRACK/results/logs/r5_full_m2_12_mpq.time"
/usr/bin/time -p "$PY" r5_vm12_enum.py --m2 13 --W 2000 --impl mpq      --workers 8 --chunks 16 --tag m2_13_mpq \
    > "$TRACK/results/logs/r5_full_m2_13_mpq.log" 2> "$TRACK/results/logs/r5_full_m2_13_mpq.time"
/usr/bin/time -p "$PY" r5_vm12_enum.py --m2 14 --W 2000 --impl mpq      --workers 8 --chunks 32 --interleave --tag m2_14_mpq \
    > "$TRACK/results/logs/r5_full_m2_14_mpq.log" 2> "$TRACK/results/logs/r5_full_m2_14_mpq.time"
# 追加（2026 年 10 月 28 日 01:25 启动、02:46 完成）：m₂ = 13 的 fraction 引擎交叉核对（判定行与 mpq 档逐字相同，见节四 B 条）
/usr/bin/time -p "$PY" r5_vm12_enum.py --m2 13 --W 2000 --impl fraction --workers 8 --chunks 32 --interleave --tag m2_13_fraction \
    > "$TRACK/results/logs/r5_full_m2_13_fraction.log" 2> "$TRACK/results/logs/r5_full_m2_13_fraction.time"
```

4. 边界档与阴性档（八核脚本，两引擎）：

```bash
cd "$TRACK/scripts"
"$PY" r5_vm12_enum.py --m2 5 --W threshold --impl fraction --workers 1 --chunks 1 --tag smoke_m2_5 \
    > "$TRACK/results/r5_smoke/smoke_m2_5_fraction.log" 2>&1
"$PY" r5_vm12_enum.py --m2 5 --W threshold --impl mpq      --workers 1 --chunks 1 --tag smoke_m2_5_mpq \
    > "$TRACK/results/r5_smoke/smoke_m2_5_mpq.log" 2>&1
"$PY" r5_vm12_enum.py --m2 2 --delta 3/2 --W 3/2 --impl fraction --workers 1 --chunks 1 --tag smoke_m2_2 \
    > "$TRACK/results/r5_smoke/smoke_m2_2_fraction.log" 2>&1
"$PY" r5_vm12_enum.py --m2 2 --delta 3/2 --W 3/2 --impl mpq      --workers 1 --chunks 1 --tag smoke_m2_2_mpq \
    > "$TRACK/results/r5_smoke/smoke_m2_2_mpq.log" 2>&1
```

E10 档原始行（逐字，两引擎相同）：`    可行顶点数 = 5；与解析的 m2 = 5 个循环旋转相同 = True（解析集大小 5）`；`    每个顶点的（活跃约束法向量秩，活跃约束条数）= [(5, 6)]`；分检行为 `    分检：秩亏/不相容 = 170，满秩不可行 = 262，满秩可行子集 = 30`（即 5 个顶点 × 每顶点 6 个捕捉子集）。与 `r2_b_out.txt:91` 至 `:99` 的 E10 段逐字同口径（该段证书 `[(5, 6)]`、全穷举 462 子集、`与约简一致 = True`）。

5. 测速探针（三段窗口取样，单进程）与逐子集样本：

```bash
cd "$TRACK/scripts"
for m in 10 12 13 14; do
  K=3000; if [ "$m" -ge 13 ]; then K=1500; fi
  for impl in fraction mpq; do
    /usr/bin/time -p "$PY" r5_vm12_enum.py --m2 $m --impl $impl --probe $K --tag probe_m${m}_${impl} \
        > "$TRACK/results/r5_smoke/probe_m${m}_${impl}.log" 2> "$TRACK/results/r5_smoke/probe_m${m}_${impl}.time"
  done
done
"$PY" r5_vm12_enum.py --m2 10 --impl fraction --dump-sample 3000 --out-sample "$TRACK/results/r5_smoke/sample_m2_10_fraction.txt" > "$TRACK/results/r5_smoke/sample_m2_10_fraction.log" 2>&1
"$PY" r5_vm12_enum.py --m2 10 --impl mpq      --dump-sample 3000 --out-sample "$TRACK/results/r5_smoke/sample_m2_10_mpq.txt"      > "$TRACK/results/r5_smoke/sample_m2_10_mpq.log" 2>&1
"$PY" r5_vm12_enum.py --m2 12 --impl fraction --dump-sample 1500 --out-sample "$TRACK/results/r5_smoke/sample_m2_12_fraction.txt" > "$TRACK/results/r5_smoke/sample_m2_12_fraction.log" 2>&1
"$PY" r5_vm12_enum.py --m2 12 --impl mpq      --dump-sample 1500 --out-sample "$TRACK/results/r5_smoke/sample_m2_12_mpq.txt"      > "$TRACK/results/r5_smoke/sample_m2_12_mpq.log" 2>&1
diff "$TRACK/results/r5_smoke/sample_m2_10_fraction.txt" "$TRACK/results/r5_smoke/sample_m2_10_mpq.txt"   # 零差异
diff "$TRACK/results/r5_smoke/sample_m2_12_fraction.txt" "$TRACK/results/r5_smoke/sample_m2_12_mpq.txt"   # 零差异
```

三段窗口探针实测（每子集毫秒，单进程；fraction 与 mpq 两列）：

| 档位 | fraction | mpq |
|---|---|---|
| m₂ = 10 | 0.2003 | 0.0367 |
| m₂ = 12 | 0.3317 | 0.0757 |
| m₂ = 13 | 0.4993 | 0.1933 |
| m₂ = 14 | 0.9280 | 0.5820 |

（窗口为「字典序头部 1/3、中段 1/3、末段 1/3」各 K/3 个；末段窗口显著更贵——m₂ = 12 fraction 三段依次 0.162、0.239、0.594 毫秒/个——故此法给的是单进程偏乐观的近似，仅用于投影。）

6. 校验点抽取（F 条观察的复跑命令）：

```bash
cd "$TRACK/results/ckpt" && "$PY" -c "
import json, glob
for tag in ['m2_10_fraction','m2_12_fraction','m2_13_mpq','m2_14_mpq']:
    exs = []
    for f in sorted(glob.glob(tag + '/chunk_*.json')):
        d = json.load(open(f))
        for k, rec in d['feasible'].items():
            exs += [tuple(e) for e in rec['examples']]
    print(tag, len(set(exs)), sorted(set(exs))[-2:])
"
```

### 5.2 原始输出摘要（每档判定与性能；数字可直接 grep 对应日志）

| 档位 | 引擎 | 组合数（覆盖校验） | 秩亏 | 满秩不可行 | 可行子集 | 顶点数 | 判定（与解析族相同） | 证书 | 每子集 CPU 毫秒 | CPU 秒 | 墙钟秒 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| m₂ = 10 | fraction | 352716（True） | 295780 | 56926 | 10 | 10 | True | [(10,10)] | 0.2596 | 91.6 | 16.0 |
| m₂ = 10 | mpq | 352716（True） | 295780 | 56926 | 10 | 10 | True | [(10,10)] | 0.0515 | 18.2 | 3.3 |
| m₂ = 12 | fraction | 5200300（True） | 4752735 | 447553 | 12 | 12 | True | [(12,12)] | 0.5741 | 2985.3 | 547.9 |
| m₂ = 12 | mpq | 5200300（True） | 4752735 | 447553 | 12 | 12 | True | [(12,12)] | 0.1327 | 690.1 | 122.9 |
| m₂ = 13 | mpq | 20058300（True） | 18811533 | 1246754 | 13 | 13 | True | [(13,13)] | 0.1457 | 2923.4 | 516.4 |
| m₂ = 13 | fraction | 20058300（True） | 18811533 | 1246754 | 13 | 13 | True | [(13,13)] | 0.7000 | 14040.7 | 3513.5 |
| m₂ = 14 | mpq | 77558760（True） | 74098262 | 3460484 | 14 | 14 | True | [(14,14)] | 0.1738 | 13477.7 | 2912.2 |

m₂ = 14 档的补充：三项分检之和 74098262 + 3460484 + 14 = 77558760（等于组合总数）；有效核当量 13477.7 / 2912.2 = 4.63（本轮最低，负载最重时段的记录）。

对照结论一（与基线）：m₂ = 10 两引擎的「子集总数、可行顶点数、与解析相同、证书」四行与 `r2_j_A.txt` 归一化后逐字相同（`diff` 零差异，两引擎各自成立）。

对照结论二（与 E10 边界档）：m₂ = 5 阈值档两引擎报 5 个顶点、证书 (5, 6)、相等 True，与 `r2_b_out.txt` E10 段一致。

对照结论三（与阴性档）：m₂ = 2、δ = 3/2、W = 3/2 两引擎报「不相同 = False」，非解析顶点与缺失解析点与 `route-1.md:319` 逐项一致。

### 5.3 文件清单与 md5（本轮 `results/` 下产物）

| 文件 | md5 |
|---|---|
| `scripts/r5_vm12_enum.py`（当前版本，含 `--interleave`） | `4fd20e6737c51dda3e88e2f6c0ca2345` |
| `results/logs/r5_full_m2_10_fraction.log` | `f91223df69d325438fa00751f7d0a61b` |
| `results/logs/r5_full_m2_10_mpq.log` | `ed4807b53a6834dc2143ccc8335e01d4` |
| `results/logs/r5_full_m2_12_fraction.log` | `0b286172e8385be71c5573c5f7d1a2b9` |
| `results/logs/r5_full_m2_12_mpq.log` | `eb16f9e78762849af99b195bd219db8d` |
| `results/logs/r5_full_m2_13_mpq.log` | `b29117e845961ba98c54563a33221b8c` |
| `results/logs/r5_full_m2_13_fraction.log` | `a0c5f7fbf687adc232d9c1e5885a7d89` |
| `results/logs/r5_full_m2_14_mpq.log` | `5b13b01b441209cc4a7f6f664f96779a` |
| `results/logs/r5_full_m2_14_mpq_verdict.txt` | `1a1fbae0749f0f99584856b741ad3aea` |
| `results/logs/r5_anchor_r2j_A_original.txt` | `001c387eeaa62a2ebb5cd5f4d4517213` |
| `results/logs/r5_anchor_r1_selfcheck_original.txt` | `85872750ff4fea5ea0fc73998d221a0e` |
| `results/r5_smoke/sample_m2_10_fraction.txt` | `aeb7b12269bd3b400c3cb7bb79f9cc75` |
| `results/r5_smoke/sample_m2_12_fraction.txt` | `8beba7c8be8f4aa1e16adcb7ae68cee7` |

版本身份（引用纪律）：`70-research/cycle-1/scripts/r2_common.py`（244 行，md5 `cfee819667c0883e73732f03d2dc8bef`）与 `r2_j_independent_vertices.py`（272 行，md5 `4b8ce2a500d8ca9021fd0178deca637e`）在每个日志头部逐次打印并断言一致（本轮全部日志均 `一致 = True`）。`r2_j_A.txt` 基线（16 行，md5 `8f8d0112668a88d0811f30cefa396bd1`）、`r2_b_out.txt`（136 行，md5 `f3882451e5a45fc3cb5cce781f279e32`）按材料 `materials.md` 第 5.7 节登记核对；本轮引自它们的每一行都注明文件与段落。

### 5.4 m₂ = 14 档（判定：True；mpq 全量完成）

命令行见 5.1 第 3 条末行（32 分片、两端交替派发、mpq 引擎）；2026 年 10 月 28 日 00:06 启动、00:55 完成。原始输出 `results/logs/r5_full_m2_14_mpq.log`（md5 `5b13b01b441209cc4a7f6f664f96779a`）、时间文件 `results/logs/r5_full_m2_14_mpq.time`（`real 2912.61 / user 13328.89 / sys 148.99`）、逐分片校验点 `results/ckpt/m2_14_mpq/`、判定行摘录 `results/logs/r5_full_m2_14_mpq_verdict.txt`（md5 `1a1fbae0749f0f99584856b741ad3aea`）。

判定行逐字（`results/logs/r5_full_m2_14_mpq.log`）：

> `    子集总数 C(29,14) = 77558760；已处理 = 77558760（覆盖校验 = True）`
> `    用时 2912.2 s（墙钟），CPU（含子进程 user+sys）13477.7 s，每子集 0.0375 ms（墙钟/总）`
> `    分检：秩亏/不相容 = 74098262，满秩不可行 = 3460484，满秩可行子集 = 14`
> `    可行顶点数 = 14；与解析的 m2 = 14 个循环旋转相同 = True（解析集大小 14）`
> `    每个顶点的（活跃约束法向量秩，活跃约束条数）= [(14, 14)]`
> `    每个可行解被活跃子集捕捉的个数（升序）= [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]`

覆盖校验与算术核对（本轮实跑）：32 个分片行的 `count=` 之和 = 77558760 = C(29,14)；分检三项之和 74098262 + 3460484 + 14 = 77558760；`SUMMARY_JSON` 的 `equal` 为 true、`certs` 为 [[14,14]]、`ms_per_subset_cpu` 为 0.1738、有效核当量 13477.7 / 2912.2 = 4.63。

版本身份：该档脚本为当前版本（日志头 `脚本 md5 = 4fd20e6737c51dda3e88e2f6c0ca2345`，含 `--interleave` 派发顺序改动；见节三第 8 条）；两个依赖文件 md5 断言一致。

复核方式：`zsh scripts/r5_run_all.sh full14` 复跑；或对既有校验点加 `--resume` 复核汇总；覆盖校验由脚本内置断言（Σ(end−start) = C(29,14)，各 worker 计数之和相等）。

---

## 六、核对边界声明（照 plan.md 节八模板逐条填实）

### 6.1 模板逐字填实

> 本核对覆盖：m₂ 属于实际档位集合 {10, 12, 13, 14}；参数（δ = 126797/80000，W = 2000）；方法为不依赖 (L1) 与顶点引理的全活跃子集穷举。范围内的判定：可行顶点集恰为 m₂ 个循环旋转（四档判定均为 True，未出现反例）。该范围之外仍属未证：1. m₂ 超出实际档位的全部情形；2. 一切其他参数取值（含 (P1) 边缘与不满足 (P1) 的区域）；3. 一般 m₂ 的顶点识别仍只有纸面证明（route-1、route-2、route-5），未经形式化；4. 应用档 m₂ = 20、47、91 无独立穷举（组合规模不可达，`learnings.md:45`）；5. 本核对是机器核对，不构成对顶点引理的证明。

（上段的「实际档位集合」处即模板的填空位；模板本体逐字见 `plan.md:149`。）

### 6.2 逐条展开与补充登记

**本核对覆盖**：m₂ 属于实际档位集合（10、12、13、14；引擎覆盖：10、12、13 为双引擎全量、判定行对称 `diff` 零差异，14 为 mpq 单引擎全量、fraction 14 未跑）；参数（δ = 126797/80000，即 δ 的严格下界；W = 2000）；方法为不依赖 (L1) 与顶点引理的全活跃子集穷举（依赖清单见节一 1.4；「枚举不漏顶点」的初等论证见节二第 2 步；覆盖校验见节二第 3 步）。**范围内的判定：可行顶点集恰为 m₂ 个循环旋转**（四档全为 True；逐条证据见节四 A、B、C 条与节五 5.2、5.4；每档的判定行都能在同档日志里 grep 到）。

**该范围之外仍属未证**（逐条，不省略）：

1. m₂ 超出实际档位的全部情形：m₂ ≥ 15、以及任何大于 14 的 m₂ 都没有核对结论（14 档已在范围内，见节四 C 条）。
2. 一切其他参数取值：其他 δ（含 δ = log₂3 真值本身，以及 δ_lo < δ < log₂3 的每一取值）；其他 W（含 (P1) 边缘 W = (δ^{m₂}−1)/(δ−1) 与不满足 (P1) 的区域）；应用档的 W = (m₂/m)·K（K 的量级 1e11，对应 m = 20、47、91 等）。δ 只以 C2 右端出现、δ 增大使 P 单调变大这一方向性事实（节一 1.3）只说明「为什么本核对选 δ_lo」，**不构成任何转移定理**。
3. 一般 m₂ 的顶点识别仍只有纸面证明（项目内：`cycle-1/route-1.md` Step 8′、`route-2.md`、`route-5.md`；原件：勘误第 2 页顶点段），未经形式化（本机无 Lean 与 Coq，Lean 文件自述从未经编译器检验）。本核对不改变这一点，也不构成对顶点引理的证明。
4. 应用档 m₂ = 20、47、91 无独立穷举（组合规模不可达，`learnings.md:45`；C(41,20) = 269128937220 与 2.7e11 的登记见 `route-2.md:205`，本报告未重跑该组合数的独立性）。
5. 本核对是**机器核对（附范围）**，不是证明：它是有限档位、有限参数上的穷举判定；阴性档（m₂ = 2）证明这套机具有判别力，但不使任何 True 判定升级为定理。
6. 补充登记一（结构观察的边界）：「全部捕捉子集恰为字典序末 m₂ 个、且每顶点恰被 1 个子集捕捉」只是 10、12、13、14 四档的实测观察（节四 F），不是对更大 m₂ 的断言。
7. 补充登记二（性能数字的边界）：每子集毫秒与墙钟都是本机、本轮负载下的实测（CPU 含子进程 user+sys；墙钟受其它 actor 挤压，核当量约 4.6 至 5.7，见节三第 4 条）；由它做的任何外推是投影，不是复杂度定理。
8. 补充登记三（读法边界）：本核对按项目既有读法把回绕约束闭化（严格号读作 ≤，`rederivation-erratum.md` 第 2 节第 3 条）；凡引用本报告判定时须一并引用该读法。

**一句话状态**：m₂ = 10、12、13、14 四档在 (δ_lo = 126797/80000, W = 2000) 上的全活跃子集穷举判定均为「可行顶点集恰为 m₂ 个循环旋转」（10、12、13 双引擎全量、判定行对称 `diff` 零差异；14 为 mpq 单引擎全量，C(29,14) = 77558760 子集、32 分片、墙钟 2912.2 s）；该结论只覆盖上述档位与这两参数，凡超出者一律未证，逐条见上。
