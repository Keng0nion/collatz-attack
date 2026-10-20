# 科拉茨猜想攻坚总报告

**本工作没有证明科拉茨猜想。科拉茨猜想仍然是开放问题。本报告给出的是边界、可复核的局部结果，以及六条候选证明路线各自的失败点。** 全文不出现任何「证明了猜想」或与之等价的说法；凡未证之处一律写明未证，凡仅预印本或自发布的宣称一律带标注，凡本工作未亲自打开原文的文献断言一律写「转引」。

---

## 一、摘要

本工作把科拉茨猜想（3x+1）的已知边界整理成清单，并沿六条路线做真实尝试，全部未成功。可复核积累有三类：计算地基（n ≤ 2^28 与 2^24 全量到达 1、自算验证界 10^12、周期 ≤ 34 无非平凡正环）；局部初等引理（筛饱和引理、二分定理、2 进等距刚性、代价定理等）；定量负结果（分离界对前沿贡献上限 7.3%，所需提升 1.19×10^18 倍；Tao 型逐层正上界不归零——与 Tao 定理相容的读法，非不可能性定理）。六条路线失败点已定位：终点上界一致性、逐层正上界、情形 II、m 无上界时夹逼失效、主目标等价于猜想无发散半边、受限版本真值与猜想相反。所有数字附复现命令。

---

## 二、主张台账

状态分三档：**甲** 已确证见诸来源；**乙** 本工作计算得到且经独立重算；**丙** 未证或存疑。文献类条目凡笔记标注「原文未打开」者一律按转引处理。

### 甲 已确证见诸来源

| # | 主张 | 证据指针 |
|---|---|---|
| 甲1 | Tao 定理（2022，同行评审 Forum of Mathematics Pi 10，文章 e12）：对任意 f(N) → ∞，Col_min(N) < f(N) 对下对数密度为 1 的 N 成立；固定常数 C_0 版「很可能与整个猜想一样难」 | `10-literature/frontier.md:15`；`10-literature/notes/tao-almost-all.md:16` 至 `:33`（关键结果一、二节）；`30-proof-attempts/tao-quantitative/attempt.md:9`（本项目下载 arXiv:1909.03562v7 逐句核对） |
| 甲2 | Korec 定理（1994，同行评审）：对每个 c > log_4 3 ≈ 0.79248125，{y : 存在 n，T^n(y) < y^c} 自然密度为 1 | `10-literature/frontier.md:17`；`10-literature/notes/stopping-times.md:37`（本项目读全文并读图核对） |
| 甲3 | Terras 与 Everett（1976、1977，同行评审）：有限停时的正整数集合自然密度为 1，即 {n : χ(n) = ∞} 密度为 0 | `10-literature/frontier.md:19`；`10-literature/notes/stopping-times.md:21` 至 `:31`（Terras 1976 与本项目复测记录见 frontier 第六节第 10 条） |
| 甲4 | Krasikov 与 Lagarias（2003，同行评审）：对 a 不被 3 整除，π_a(x) ≥ x^0.84 对充分大 x 成立；线性规划取 k = 11、λ = 1.7922310，指数 γ = log_2 λ ≈ 0.8417560 | `10-literature/frontier.md:20`；`10-literature/notes/stopping-times.md:60`（本项目读 arXiv 全文） |
| 甲5 | Barina（2025，同行评审 J. Supercomputing 81:810）：所有小于 2^71 ≈ 2.361×10^21 的正整数到达 1（有限计算记录，不是定理）；项目页自报前线 2075×2^60 ≈ 2^71.02 | `10-literature/frontier.md:28`；`10-literature/notes/verification.md:15` 至 `:17` |
| 甲6 | Hercher 2023（同行评审 JIS 26，文章 23.3.5）与 2026 勘误**主张**不存在 m ≤ 91 的非平凡 m 圈；若 X0 ≥ 1536×2^60 = 3×2^69 则任何非平凡环含 K > 1.375×10^11 个奇数项（精确门槛 q_23 = 137,528,045,312；2^71 已越过该门槛）。**该主张带未裁决争议**（与第三方的 82 之间，见甲7）：本项目笔记的判定是「在有专家审读之前，m ≤ 82、m ≤ 91、m ≤ 101 三个数字都不能当作既成记录；能当作记录的是 Hercher 论文与勘误本身」 | `10-literature/frontier.md:21`；`10-literature/notes/cycles.md:76` 至 `:79`（本项目通读全文）；`10-literature/notes/claims-2024-2026.md:73`（三家立场现状与该判定） |
| 甲7 | 与 甲6 并列的争议事实：zbMATH 评审 Zbl 1536.11052（评审人 Olivier Rozier）写 Theorem 21 的证明「靠近末尾有潜在缺陷」；第三方 Lean 仓库 PhilNorfleet 只承认 m ≤ 82 且未引用 2026 年勘误；另一第三方仓库 justinalick 接受含勘误的 m ≤ 91 并条件性宣称推进到 101 | `10-literature/notes/cycles.md:81` 至 `:82`；`10-literature/notes/claims-2024-2026.md:71` 至 `:75`；`30-proof-attempts/diophantine-transcendence/attempt.md:31` 至 `:35`（本项目 curl 三个来源的逐字引文） |
| 甲8 | Hercher 2026 勘误：作者承认 Theorem 21 第 14 页底部的推导「contains an error」，致谢指错者 Xinjun Wang，改用凸性取极值论证；勘误未撤回主结论 | `10-literature/notes/cycles.md:80`；`30-proof-attempts/diophantine-transcendence/rebuttal-2.md:62` 至 `:67`（逐字引文） |
| 甲9 | Böhm 与 Sontacchi（1978，同行评审）：环方程 x = c/(2^n − 3^m) 与充要条件；整数环满足绝对值小于 3^n | `10-literature/notes/cycles.md:24` 至 `:44`（本项目读页面图像核对） |
| 甲10 | 负整数上存在三个非平凡环 {−1}、{−5, −7, −10}、从 −17 起的 11 元环（周期分别为 1、3、11） | `10-literature/notes/cycles.md:44`；`20-experiments/findings/cycles.md:148` 至 `:156`；`40-formal/exact_check.py` 引理 3d（本报告实跑找回三个环） |
| 甲11 | Rozier 与 Terracol（arXiv:2502.00948v3；发表版 Discrete Mathematics 349（2026）115167）：悖论序列框架、定理 1.1（首项 [7, 4614] 内恰 593 条）、定理 2.2（c_j 双侧界）、定理 3.2（t(n) = ∞ 蕴涵无穷多条悖论序列）、推论 5.2（2 ≤ n ≤ 2.8×10^19 时 t(n) = τ(n)） | `30-proof-attempts/minimal-counterexample/attempt.md:237` 至 `:254`（本项目一手打开 v3 全文） |
| 甲12 | 族层面不可判定性：广义 Collatz 判定问题不可判定（Conway 1972）；{g : range(g) = ω} 是 Π⁰₂ 完备（Kurtz 与 Simon 2007）。只约束统一方法，不给原猜想任何结论 | `10-literature/frontier.md:30`；`10-literature/notes/barriers.md:24` 至 `:28` |
| 甲13 | 2 进侧的共轭定理（Bernstein 1994；Bernstein 与 Lagarias 1996，同行评审）：T 共轭于 2 进移位、共轭映射等距保测；「Φ 与其逆处处不可微」为**转引**（`30-proof-attempts/two-adic-control/attempt.md:164` 与 `:245` 均标「转引、本轮未用」）；「T 在 Z_2 上每个周期轨道皆有理」亦为**转引**（`10-literature/frontier.md:29` 自记「转引自 Rozier，其引 Lagarias 1990」；`10-literature/notes/two-adic.md:41` 自记「Lagarias 1990 原文我未能打开」） | `10-literature/frontier.md:29` 至 `:33`；`10-literature/notes/two-adic.md:23` 至 `:44`（关键结果第一、二节）；本项目自证版的**范围有限**的证明见 `30-proof-attempts/two-adic-control/attempt.md:330` 至 `:348`（附录只自证步骤 1、2：T_a 良定义、保测、共轭、等距与 Φ_a(Q∩Z_2) ⊆ Q∩Z_2；不含「处处不可微」与「周期轨道皆有理」） |
| 甲14 | 已被排除的路线（不可用）：纯测度或遍历论论证对整数无结论（Z 可数零测，且 T_3 与 T_5 在 Z_2 上完全同构）、参数不敏感论证、符号不敏感论证、固定深度的下降覆盖（n ≡ −1 mod 2^k 反例）、解析泛函方程路线（Opfer 自行撤回）、「有限验证通向全称命题」无桥梁 | `10-literature/frontier.md:43` 至 `:55`；`10-literature/notes/barriers.md:59` 至 `:73` |

### 乙 本工作计算得到且经独立重算

| # | 主张 | 证据指针（原输出与独立重算） |
|---|---|---|
| 乙1 | n ≤ 2^28 全部到达 1；范围内最大总停时 956，在 n = 226588897；63 个停时纪录与 OEIS A006877/A006878 零不一致 | 原输出 `20-experiments/results/sweep.txt:7`、`:75`、`:78`、`:209`；结论 `20-experiments/findings/sweep.md:78` 至 `:88`；独立重算：纯 Python 再模拟 63 个纪录点加 3000 随机点零不一致（`sweep_check.py`），OEIS b 文件逐条比对 0 不一致 |
| 乙2 | n ≤ 2^24 全部到达 1；最大总停时 704 在 15733191；Terras 停时（加速）最大 287 在 13421671；标准与加速停时均值比 1.499956 | 原输出 `20-experiments/results/stoptime_dist_summary.txt`；结论 `20-experiments/findings/stoptime-stats.md:118` 至 `:133`（C 程序汇总原文，287 在 `:127`、均值比 1.4999558440 在 `:128`）与 `:265`；独立重算：`scripts/verify_stoptime.py` 三项核对 0 不一致（`stoptime-stats.md:134` 至 `:142`）；与本项目另一条独立程序（`minimal-counterexample` 的 D9 段 χ 记录链）逐位一致 |
| 乙3 | 周期 ≤ 34 的非平凡**正环**不存在（无条件完备枚举，覆盖长度 1 至 34 的全部 2^k 个向量，叶子 3.44×10^10）；同一次枚举同时找回五个环：{0}、{1, 2} 与三个非平凡负环 {−1}（周期 1）、{−5, −7, −10}（周期 3）、{−17 族}（周期 11） | 原输出 `20-experiments/results/cycles_enum_exhaustive_k34_rerun.txt`；结论 `20-experiments/findings/cycles.md:243` 与环清单 `:148` 至 `:156`（注意：该行原文的「非平凡整数环一个也没有」措辞与紧随其后的负环清单自相矛盾，本报告按环清单读作「非平凡正环」）；独立重算：`scripts/cycles_solutions_verify.py` 重新算 c、迭代 T、核奇偶向量，168 条解行 0 失败 |
| 乙4 | 长度 ≤ 32 的奇偶向量完备搜索去重后只有四个环族（{1,2} 与 −1、−5、−17 三族）；伪命中 0；命中 116（含退化解 x = 0 则整除成立节点 148） | 原输出 `20-experiments/results/parity-vectors-cycle-search-K32.txt`；结论 `20-experiments/findings/parity-vectors.md:145`；独立重算：复核员用无剪枝穷举确认口径差异（`parity-vectors.md:185`） |
| 乙5 | 自算验证界 X0 = Y0 = 10^12：凡 1 ≤ n < 10^12 到达 1，凡 \|n\| < 10^12 的负整数到达三个已知负环之一；零未判定、零新环 | 原输出 `20-experiments/results/cycles_verify_free_runs.txt`；结论 `20-experiments/findings/cycles.md:246`；独立重算：位表法与无表法两种实现在 10^10 上给出同一结论，另有 10^6 项逐项完整迭代对照 |
| 乙6 | 环判据排除上界（前提：环上元素绝对值至少 X0）：X0 = 10^12 时 M+ = 10,781,273、M− = 5,446,237；七档 X0 的表与实验一致 | 原表 `20-experiments/findings/cycles.md:201` 至 `:209`；独立重算：`40-formal/independent-checks/criterion_exclusion_recheck.py`（本报告实跑，定点整数算法，七档全部一致，脚本 2.4 秒） |
| 乙7 | 由 M+ 升级到周期：δ×10,781,274 = 17,087,914.9999999824，故该类正环周期至少 17,087,915（与文献 Eliahou 的数值逐位相同） | `40-formal/independent-checks/criterion-recheck.md:38` 至 `:40`；本报告实跑复现 |
| 乙8 | q_23 = 137,528,045,312；q_23 + q_24 = 890,638,885,193；q_23×(1 + log_3 2) = 355,504,839,929；q_23×log_2 3 = 217,976,794,617 | `40-formal/independent-checks/README.md:16` 至 `:20`；本报告实跑 `q23_convergents.py` 并另用 mpmath 独立算连分数，逐位一致 |
| 乙9 | 逆向树：深度 65 累计 354,832,309 节点（补跑 66 层为 473,112,998）；层增长比 1.333347 对 4/3 差 +0.0010%；常数 N(d)/(4/3)^d 在 d = 40 至 66 稳定在 0.6713 附近；显式建树只完整覆盖奇数到 25，M(70) = 53、M(75) = 127 | 结论 `20-experiments/findings/reverse-tree.md:241` 至 `:250`；独立重算：`40-formal/independent-checks/reverse-tree-recheck.md`（另一套实现复现 M(D) 表与前 25 层，深跑未重跑）；本报告实跑 `reverse_tree_recheck.py` 一致 |
| 乙10 | SMT：线性形式与按位加权形式在截断上 UNSAT，核分别为 {x=1,x=2} 与 {x=3,x=4}；逐 k 冲突对 k ≤ 20 全 UNSAT；松弛变体 F 有 SAT 证书（负斐波那契尾），在 [3, 2^24] 的 8,388,607 个奇 x 上零违规，而 8,388,608 个偶 x 全部违反严格降 | 结论 `20-experiments/findings/smt-certificate.md:189` 至 `:199` 与 `:225` 至 `:231`；原输出 `20-experiments/results/verify_fib_certificate_2e24.txt`、`direct_reference_2e18_verify.txt`（第二条独立代码路径复验） |
| 乙11 | 1 圈：奇偶字 1^K 0^L 的四条等价归约成立；K = 1 至 20000 精确整数检验的唯一候选是 (1, 1, 2)（平凡环）；与 Rhin 型下界相撞的门槛 K0 = 108（该处下界 3.47048×10^(−33) 对 2^(−108) = 3.08149×10^(−33)，比值 1.12623） | `30-proof-attempts/arithmetic-cycles/attempt.md:141` 至 `:142`；本报告实跑 `scripts/arithmetic_cycles_round2.py`（约 3 分钟）逐项复现，包括 (K, m, T) = (1, 1, 2) 的三参数枚举与 K0 |
| 乙12 | 窗口判据的可达范围定理：(3X0 − 1)ln2 之外的 K 一律不被该判据排除（渐近 3 ln 2·X0 = 2.0794415 X0）；五档 X0 的幸存者阶梯上界全部成立 | `30-proof-attempts/arithmetic-cycles/attempt.md:35` 与 `:104` 至 `:108`；本报告实跑脚本 C 段复现（X0 = 10^4、10^5 两侧扫描被排除数为 0） |
| 乙13 | 倾斜恒等式 F(m+1) = exp(−mD)·Q(E_m)·E_tilt[e^(−cZ_m) 在可容许条件下的期望]（D = ln2 − H(log_3 2) = 0.034688185232…）；条件因子 E_tilt[e^(−cZ_m)]·m 在 15.2 至 16.8；边界因子 Q(E_m)·√m 落在 [0.6672, 0.6675]（`tao-quantitative/attempt.md:152`），与 C_S/√π = 0.6674426 相符到 4 位有效数字；精确计数给出 u_m·√m = 0.66744（同文件 `:145`），与 0.6674426 相符到 5 位有效数字 | `30-proof-attempts/tao-quantitative/attempt.md:218` 至 `:249`；原输出 `checks/out_D_tilt_30k.txt`、`checks/out_G_sa.txt`、`checks/out_I_sa_exact.txt`（恒等式逐阶检验 60 阶，最大相对差 7.7×10^(−51)） |
| 乙14 | 最小反例路线：筛饱和引理（χ(x) = ∞ ⟺ 对一切 k 有 x mod 2^k ∈ E_k）、二分定理（轨道无界 ⟺ 3^(S_j) > 2^j 对无穷多层成立）、首失败几何、c 的双侧界；数值 D1 至 D13 全过 | `30-proof-attempts/minimal-counterexample/attempt.md:80` 至 `:158`、`:296` 至 `:312`；原输出 `verify_dichotomy_output.txt`（D9 最大 χ 287 在 13421671；D11 的 (K) 违反 j ≤ 26 检查 502523 个向量，违反 0） |
| 乙15 | 2 进路线：等距刚性 T1（与 S 交换的 2 进等距恰为 id 与 σ）、整数不保持定理 T2（在覆盖范围内任何双射共轭都不保持整数）、搬运命题 O1；窗口 ≤ 4 的连续 S 交换双射恰为 {id, σ}（非满射 64954、满射非单射 580、未排除 2） | `30-proof-attempts/two-adic-control/attempt.md:19` 至 `:27`、`:74` 至 `:83`；本报告实跑 `scripts/round2_verify.py`，输出与存档逐字节相同（MD5 5da059c4f9b555357c11afe8fba7c664） |
| 乙16 | 自动机路线：(S1) 编码定理、(S2) 2 进闭包版本为假（反例 −1 与 4/5）、(S3) 残类二分、(S4) 非下降集结构、(S5) 显式下降判据、(S6) 势函数否决、(S7) 代价定理；脚本 26 条断言全过 | `30-proof-attempts/formal-automata/attempt.md:40` 至 `:76`；原输出 `results_checks_v2.txt`；本报告实跑 `checks_automata_v2.py`：26 条通过、失败断言数 0、退出码 0 |
| 乙17 | 顶路线关键数字：第一次使 M* ≥ 92 的验证界门槛 1.7233559×10^22（比 2^71 高 0.8632 个数量级）；第一道墙 eps/gap+ = 1.04317、第二道墙 1.33641；记录乘积 q·gap+ 沿上方逼近记录单调不增；改进分离界对前沿的贡献上限 7.3%（m = 91 处 K_surv 2.12308×10^20 对理想 1.97895×10^20） | 原输出 `30-proof-attempts/diophantine-transcendence/dt2_check2.out`、`dt2_struct.out`、`dt2_up.out`；本报告实跑三个脚本逐位复现（含 K_surv(92) = 3.3656783×10^20 对 K_low(92) = 7.7692117×10^19 的 4.332 倍） |
| 乙18 | 精确检查闸门：四条初等引理（仿射公式、c 的递推、环方程与 2^k > 3^m、停时与阈值判据）在有限范围全部 PASS | `40-formal/exact_check.py`；本报告实跑：退出码 0，输出 56 行，四条引理全 PASS，失败 0 |

### 丙 未证或存疑

| # | 事项 | 状态与证据指针 |
|---|---|---|
| 丙1 | 科拉茨猜想本身（不存在发散轨道、无平凡环之外的环、逆向树含全部正整数） | 未证。本工作六条路线全部未成功（见第三节） |
| 丙2 | 「m ≤ 91」与「m ≤ 82」之间的裁决 | 存疑。作者勘误的凸性论证无第三方评审（`30-proof-attempts/diophantine-transcendence/attempt.md:180`）；分工：第三方 Lean 只到 82 且未引用勘误（`10-literature/notes/cycles.md:82`）；本项目第三轮核查主张 82 出自一个被 Hercher 自己的 Lemma 20 证伪的「最坏情形」前提、并称勘误论证经重构有效（`diophantine-transcendence/rebuttal-2.md:16`、`:81`），但该重构本身也「未形式化」（同文件 `:117`），且作者未采纳该主张（`diophantine-transcendence/attempt.md:287`）。**本报告不裁决，两个口径并列**；本项目笔记自己的判定见甲6（三个数字都不能当作既成记录） |
| 丙3 | 初等替代路线（不用 Rhin）证明 m ≤ M* 且 M* > 91 | 不成立。终点上界「圈蕴涵 K < K_up」对一切 K 一致有效这一步缺失；初等连分数分离界是逐区间的，把它当一致界用等价于额外假设 log_2 3 的部分商尾部不出现超过双重指数阈值的项（`diophantine-transcendence/attempt.md:133` 至 `:141`） |
| 丙4 | 前沿律 M*(X0) ≈ 5.0 log_10 X0 − 14 与 M*(X0) 表 | 本工作实现的结果，只有一种实现（`diophantine-transcendence/attempt.md:202`、`:235` 自述需要第二条独立实现）；几何尾部与「健全」尾部两个口径下截距不同 |
| 丙5 | 记录乘积 q·gap+ 单调不增 | 数值核验通过（320 条记录，本报告实跑复现为 True），但未证明；若可证，一致性缺口可退化为一个显式常数检查（`diophantine-transcendence/attempt.md:234`） |
| 丙6 | Tao 型逐层正上界不归零（T1 与 T2 的正面障碍） | 与 Tao 的 Theorem 3.1 相容的读法，**不是不可能性定理**；跨过它需要「某固定层对数密度为零」的零点型输入（`tao-quantitative/attempt.md:174`、`:178`） |
| 丙7 | 修补贴入的命题「凡 B 族逐层信息不足的映射必然违反 Tao 型结论」 | 假，且至今未改。第三轮核查用作者自己的玩具映射反证（该映射上 Λ(B_2) = 1/2 > 0 而 Λ(A_M) = 0 对一切 M ≥ 2 成立，`tao-quantitative/rebuttal-2.md:8`、`:15` 至 `:30`）；该命题仍留在正文三处：`tao-quantitative/attempt.md:95`、`:293`、`:349`（本报告实读确认） |
| 丙8 | 情形 II（χ = ∞、τ < ∞ 且轨道无界）的排除 | 未证。这是最小反例路线的主缺口；已知抓手（定理 3.2 的显式族、命题 9.2 双侧界、推论 5.2 的验证范围）都不足以排除它（`minimal-counterexample/attempt.md:268` 至 `:276`） |
| 丙9 | 「不存在非平凡正环」与「m 圈前沿推到一切 m」 | 未证。文献记录 m ≤ 91（带勘误争议）、K > 1.375×10^11、周期 ≥ 217,976,794,617（加速口径）；本工作实测 m 侧交叉点 68 与 77 是数值观察，U 侧排除判据未证（`arithmetic-cycles/attempt.md:185` 至 `:186`、`:190` 至 `:191`） |
| 丙10 | 周期猜想 PC_3（Φ 保持有理点） | 未证，且本路线原理上够不到：PC_3 等价于整族「3x + b 在 ℤ 上无发散轨道」，b = 1 那一档就是猜想的无发散半边（`two-adic-control/attempt.md:132`、`:148`） |
| 丙11 | 「∪_k D_k 不是 2 自动集」型不可能性定理 | 在猜想为真的前提下不可能存在（代价定理 S7：任何含余有限集的类上「L ∉ C」蕴涵 ¬猜想），`formal-automata/attempt.md:153` 至 `:155` |
| 丙12 | 窗口 ≥ 5 的连续 S 交换双射分类；「连续 S 交换双射必为等距」 | 未做、未核实。窗口 ≤ 4 已完成；反驳者宣称有一般定理但未给细节，本项目自己算出的周期层过滤显示该步需要的不是密度论证（`two-adic-control/attempt.md:155`） |
| 丙13 | 自动机路线 k = 65 的首降阈值 θ 数值 | 两个数分歧未决：本项目动态规划得 θ ≈ 867.1395（附显式见证），反驳者报 467.10，双方都给出算法口径（`formal-automata/attempt.md:241`、`:321`） |
| 丙14 | Lean 形式化 | 源码已写，但**未经 Lean 编译器检验**（本机无 Lean、lake、elan，`20-experiments/ENV.md:267` 至 `:293`）。条数两说并列：`40-formal/README.md:6` 记「50 条声明（含 7 条冒烟测试）」，本报告本轮自查（`grep -cE "^(theorem\|def\|example\|lemma\|abbrev\|noncomputable def\|private def) " 40-formal/lean/CollatzBasic.lean`）得 51 条（37 theorem、7 def、7 example），差 1 未对齐；代码中 `sorry` 与 `admit` 均为 0（`sorry` 一词仅出现在文件头注释第 20 行）。写作前的替代检查是 Python 有限枚举与引理名核对，不等于编译（`40-formal/README.md:12` 至 `:28`） |
| 丙15 | 本项目六份实测记录的内部不一致四处（已逐处登记） | 其一：边界地图把 Rozier 与 Terracol 摘要写成「长度 ≤ 60 的悖论序列恰好 593 条」，而独立复现的参量是首项 [7, 4614]、长度 [8, 92]（≤ 60 的为 288 条），由 `minimal-counterexample` 路线登记（`30-proof-attempts/minimal-counterexample/attempt.md:262`、`:324`）；其二：`30-proof-attempts/diophantine-transcendence/attempt.md:3` 指示「见 `rebuttal-2.md`」，而该目录的 `rebuttal-2.md` 已是第三轮备忘录，第一轮备忘录被备份为 `rebuttal-round1.md`（`30-proof-attempts/diophantine-transcendence/rebuttal-2.md:7`）；其三：`20-experiments/findings/cycles.md:243` 的「非平凡整数环一个也没有」与其后的负环清单自相矛盾（本报告按环清单读作非平凡正环）；其四：`40-formal/README.md:6` 的「50 条声明」与 Lean 文件实际 51 条不一致（见丙14） |
| 丙16 | 若干承重常数仍是转引 | Rhin 1987 界（经 Simons 与 de Weger v1.43 的 Lemma 12 转引，`arithmetic-cycles/attempt.md:203`）；Steiner 1977 原文未打开；Simons 与 de Weger 正式版（2005）只有 1.43 更新版被通读；Eliahou 1993 原文未打开、过渡点两说并列；加速映射周期下界 217,976,794,617 无一手出处（可由 q_23 复算）；「Φ 与逆处处不可微」与「T 在 Z_2 上周期轨道皆有理」两条均为转引（见甲13） |

---

## 三、六条路线逐条报告

排序按本工作路线裁决（依「剩余缺口是否被量化、是否只差可判定的单点、局部结论是否经得起独立复核」）：
1. `diophantine-transcendence`；2. `tao-quantitative`；3. `minimal-counterexample`；4. `arithmetic-cycles`；5. `two-adic-control`；6. `formal-automata`。

**计数规则与组成（本节与「红队抽查记录」共用）。** 规则：红队逐条指出、且作者的回应文件记录为「已接受并修补或修订」的条目才计入；红队指出而未修补、未采纳或属数值分歧者**不计入**，另列在各条「最终状态」与台账丙。按此规则，六条路线合计 **26 条**，逐条组成为：

1. `diophantine-transcendence` 7 条：漏引 Theorem 21 争议（`30-proof-attempts/diophantine-transcendence/attempt.md:250` 至 `:263`）；四处细节修正实为五处（gap⁺ 尺度、触发阈值口径、门槛精确化、4.3% 口径、`X0 = 2^85` 行 M* 修正，同文件 `:265` 至 `:271`）；第二道墙比值（部分成立、已改正文口径，同文件 `:273` 至 `:275`）。**未采纳**：第三轮关于「把 82 降格」与「把勘误论证做成可传播的证明」的建议（`30-proof-attempts/diophantine-transcendence/rebuttal-2.md:93`、`:95`；作者立场见 `attempt.md:287`）。
2. `tao-quantitative` 4 条：首轮三条指控（A 族必要性断言、层分离目标、Σ 形式，`30-proof-attempts/tao-quantitative/attempt.md:339` 至 `:355`）；Sparre Andersen 恒等式的状态标注（同文件 `:359`）。**未修补**：命题 (丙)（丙7）与「所需输入的形状描述」（`30-proof-attempts/tao-quantitative/rebuttal-2.md:94`）。
3. `minimal-counterexample` 5 条：第三轮的 G1 表述（`30-proof-attempts/minimal-counterexample/attempt.md:439` 至 `:458`）；第一轮的三条撤下与一条界订正（同文件 `:5` 与 `:291` 至 `:292`）。
4. `arithmetic-cycles` 7 条：第二轮四条（负侧下标、L 侧前提、常数印错、勘误口径，`30-proof-attempts/arithmetic-cycles/attempt.md:297` 至 `:344`）；第一轮三条（常数方向写反、U 侧判据降级、文本与脚本不一致，`30-proof-attempts/arithmetic-cycles/attempt-round1.md:335` 至 `:345`），其中第三条只部分落实（`30-proof-attempts/arithmetic-cycles/rebuttal-2.md:102`）。**未撤下**：「更强反例」宣称（见同文件 `:129`）。
5. `two-adic-control` 1 条：Φ_a 保低 p 位为假（`30-proof-attempts/two-adic-control/attempt.md:271` 至 `:312`）。
6. `formal-automata` 2 条：(S3) 第 3 条越界与 (S5) 漏同余条件（`30-proof-attempts/formal-automata/attempt.md:295` 至 `:317`）。

### 3.1 `diophantine-transcendence`（超越论与丢番图逼近）

**尝试了什么。** 目标 T1：只用初等工具（Simons 与 de Weger v1.43 的 Lemma 7、9、10 与 Hercher 2023 的 Theorem 14、16、21、Lemma 22 及其勘误）证明「不存在 m ≤ M* 的非平凡 m 圈」且 M* > 91，不使用 Rhin 1987。副目标 T2：改进 3^m 与 2^k 的分离界以推进 m 圈前沿。做法是把两台已发表的机具接起来：Lemma 10 给出与 m 无关的初等 K 起点（对 M = 91 取 q_35 = 397,560,349,370,386,783，比 Hercher 论文用的 7×10^11 好 5.7×10^5 倍），Hercher 的自举把 K 下界逐档抬到 7.94×10^21，与 SdW 的终点上界 1.4784·m·δ^m 相交。

**最致命的一击。** 分两轮。第二轮指出：主结论的唯一支柱是 Hercher 的 Theorem 21，而它的尾部条款恰好是 zbMATH 评审与第三方 Lean 仓库公开质疑的地方，初稿完全漏引——而项目自己的 `10-literature/frontier.md:21` 早已登记这场争议。第三轮（本项目自己的反驳备忘录）进一步主张：作者把「82」升格为与「91」并列的口径是「让步过度」，理由是该 82 出自第三方自己的「最坏情形」前提（一个晚窗口极小值吸收几乎全部 o 步），而该情形在 Hercher 自己的 Lemma 20（n_(i+1) < n_i^δ）下不可行：若尖峰承载窗口和 W = 2.0×10^20，其余窗口元素被增长约束逼到不小于 W/δ^90 = 199.2，远高于 log_2(X0+1) = 69.44（`rebuttal-2.md:16`、`:83` 至 `:87`）。**这一条是本项目内部的反驳主张，不是本报告的裁决**（见丙2）。

**作者如何回应。** 分两层。对**第二轮**的指控与细节：全部接受并修补（新增步骤 0 第 4 条与步骤 4b 的四口径前沿表；把 m ≤ 91 改写为条件结论；五处细节修正，含二分门槛精确为 1.7233559×10^22、第二道墙比值 1.33641、`X0 = 2^85` 一行的 M* 由 119 改为 120——那是程序提前返回的 bug；对勘误的凸性论证做了两条数值核查；保留结构性负结论 L1、L2、L3）。对**第三轮**的核心建议：**未采纳**，作者维持「m ≤ 91 与 m ≤ 82 两种口径并列」，并称要收敛最该做的事是把勘误的凸性论证逐步复核或形式化（`attempt.md:287`；第三轮备忘录则记「作者未做、而本应做的事」为把该论证做成可传播的证明与检验第三方的「最坏情形」前提，`rebuttal-2.md:93`、`:95`）。

**最终状态。** 主目标未证，且 (T1) 作为定理不成立（终点上界不一致）。立住的是三类：一、数值复现与数值表（七步自举逐位复现论文、K_1(m) 八档、q_20 至 q_34 连分数、四种口径的 M*(X0) 表）；二、负结果 L1（天花板引理：在本机具内改进分离界对前沿的贡献上限 7.3%，而 m = 92 的缺口是 4.332 倍；要桥接需把 ψ 提升 1.189×10^18 倍，Dirichlet 上限只允许约 100.2 倍）、L2（一致性引理：初等版「K < K_up」等价于部分商尾部条件，阈值随 q_N 双重指数增长）、L3（初等包络与 Rhin 包络同量级，比值 0.95 至 0.999）；三、前沿律 M*(X0) ≈ 5.0 log_10 X0 − 14。争议态：`m ≤ 91` 的成立条件只剩口径之争（甲6、甲7、丙2）。

**下一步最该做什么。** 1. 把 Theorem 21 的尾部定案：逐步复核或形式化勘误的凸性替代推导，并与两个 Lean 仓库做一次公开对照（本项目已给出四口径数值底稿，`attempt.md:233`）。2. 把 L2 的一致性问题做成正面结果——尝试证明记录乘积 q·gap⁺(q) 单调不增（本项目已数值核验 320 条，若可证则一致性问题退化为一个显式常数检查）。3. 用第二条独立实现复现两套口径的 M*(X0) 表。4. 把 K 门槛接成正式周期陈述（现为两步拼合）。

### 3.2 `tao-quantitative`（量化改进）

**尝试了什么。** 目标 T1：证明存在绝对常数 C_0 使 {N : Col_min(N) > C_0} 的上对数密度为零；次目标 T2：Λ(A_1) = 0。做法是把 Tao 的论证拆到引理级（第 1 至 7 步），指出逐层估计的产物形状是正数 K(log C)^(−c) 且与 x 无关；然后尝试证明更强的边界估计 T3：F(k) ≤ C(k−1)^(−1/2)exp(−(k−1)D)。本轮新推进：倾斜恒等式（把 Chernoff 路线丢掉的因子精确写出来）、轮换恒等式（把生存概率变成一个计数量 R 的期望）、块结构与 K 的符号判据、劣质块不等式与条件性 m^(−1/4)、边界因子的经典常数。

**最致命的一击。** 首轮反驳三条指控全部成立：一、「A 族逐层级界无法相加」的必要性断言为假（{S_min > 1} 就是 A_1；给定 Tao 的逐层界，T2 等价于「对每个固定 m ≥ 2，Λ(B_m) = 0」这一纯逐层陈述）；二、层分离型反例要么字面自相矛盾、要么由玩具映射平凡实现且与 T1 无关；三、Σ_{2 ≤ m ≤ x} logweight(B_m) 就是 T2 而非更弱目标。第二轮核查又指出：修补时新写入的命题 (丙)「凡 B 族逐层信息不足的映射必然违反 Tao 型结论」为假（用作者自己的玩具映射反证：B_2 = 全体偶数，Λ(B_2) = 1/2 > 0，而 Λ(A_M) = 0 对一切 M ≥ 2 成立）。

**作者如何回应。** 首轮三条全部接受并修补：第 8 步新增 (v) 项（等价改写）、失败点 2 整段撤回、第 16 步与 G1 的状态从「缺口」改为「经典结论加两类数值验证」（并补上「恒等式左边必须是倾斜概率 Q(E_n) 而非 A(n)/2^n」这一必要修正）、下一步第 3、4 条整段重写、不建议做的事扩到五条。但 (丙) 的修正**没有落入正文**：`attempt.md:95`、`:293`、`:349` 至今仍是原样（本报告实读三行确认）；「所需输入的形状描述」（要求强于 (log C)^(−c) 的上界，而非零点型输入）也未被修改（`rebuttal-2.md:94`）。

**最终状态。** 主目标 T1 与 T2 未证。边界已被精确刻画：跨过 T1 需要「某固定层对数密度为零」的零点型输入（A 族或 B 族等价），且必须敏感于 r(1) = 1（陷阱引理：在 GGM 定理适用类里对每个阈值 B 都存在映射使 {S_min > B} 的对数密度至少 1/(B+2)）；陷阱存在升级为「该层对数密度为正」所需的前驱密度定理仍是未闭合纲领（本项目亲自核对了 Wirsching 预印本的「three unbridged gaps」与 arXiv:2608.27617 摘要的「Conjecture 2 … remains open」）。T3 只到条件性的 m^(−1/4)（前提 η(d) ≥ c/d，等价于 log_3 2 的部分商有界，未证），且第 15 步给出初等路线到不了 m^(−1/2) 的论证与两条数值否决（每串版 R ≤ C + K_+/q 被线性增长反例证伪，最大偏离 ⌊m/3⌋·0.7095112914，m = 2 至 22 全枚举）；T4 是数值猜想（F ≈ 10.8·exp(−(k−1)D)·(k−1)^(−3/2)）。局部新结论 D1、E1、E4、E5、F1、G1、H1 全部附独立验证方式。

**下一步最该做什么。** 1. 先修补 (丙)（已被证伪，仍在正文）。2. 把边界因子的严格化做在「局部化」上：测量倾斜测度下的截断矩 E_tilt[(R − K_+/q)_+; · > t] 是否指数衰减（`attempt.md:284` 给了可先跑的判定实验）。3. 补「夹道加端点」的联合公式，把 T4 从数值猜想升级为定理（即使成功也只改框架内部的幂次）。4. 形式化 D1、E1、E4（工程上最确定能完成的一步）。

### 3.3 `minimal-counterexample`（最小反例）

**尝试了什么。** 主定理：不存在 n ≥ 2 使 χ(n) = ∞（与原猜想等价）。工具是奇偶向量、阈值判据与模 2^k 筛。本工作立住的是：筛饱和引理（χ(x) = ∞ 等价于对一切 k 有 x mod 2^k ∈ E_k，并宣判「不存在更强的同余约束」「有限层永不矛盾」）；二分定理（奇数 n ≥ 3 时「轨道无界」「3^(S_j) > 2^j 对无穷多层成立」「轨道非最终周期」等价，且 liminf S_j/j ≥ log_3 2，附正性本质的 −1 反例）；归约定理（猜想 ⟸ (β) ∧ (CST)，而 (β) ∧ (α) 不足以沿本路线推出）；三情形分类（情形 II 是本路线此前没看清的漏洞）。

**最致命的一击。** 首轮把 G1 的缺口表述写成「情形 II 的每一项约束都已被本框架推尽」「现有数论工具对发散轨道无可用抓手」「没有可量化的距离」，遗漏了 Rozier 与 Terracol 的定理 3.2、定理 2.2 下界与推论 3.3。本项目一手打开并复现后确认反驳成立。

**作者如何回应。** G1 整段改写（三句主张撤下）、新增第 11 步（悖论序列框架，附本机复现：3 ≤ n < 2^24 内恰好 593 条、首项全在 [7, 4614]、长度 [8, 92]、其中 ≤ 60 的 288 条、没有一条的层等于 τ(n)）、命题 9.2 补全为双侧界、D11 从「推进验证范围」降级为「独立实现的一致性复核」（其范围被推论 5.2 与 Terras 的旧验证覆盖）、G3 引用串订正。更早的第一、二轮还撤下了四处失实陈述（含「χ ≤ τ 比 τ = χ 更弱」为错、「(K) 与 (α) 等价」未证、「最小反例必入环」的 φ 迭代推演无效）。

**最终状态。** 主定理未证；情形 I（τ = ∞）、II（τ < ∞ 且轨道无界）、III（τ < ∞ 且有界）的排除分别是缺口 G2、G1、G3。量化距离已给出：筛在 k = 286 档只给出 N ≥ 1.34×10^7，比暴力验证的 2^71 ≈ 2.36×10^21 弱约 10^14 倍，且每加一层只再砍约 3% 至 5% 的候选类。

**下一步最该做什么。** 攻情形 II（本路线最精确的中间问题）。首选抓手是把定理 3.2 的显式无穷族（首项形如 2^k N，参数由连分数对 (a, b) 控制）与最小反例的算术并排写出：N 满足 N ≡ r_k mod 2^k ∈ E_k、首失败几何、大小约束 N ≤ θ 与双侧界，逐条检查是否有一步需要 N 的额外下界才能成立。次选是 Garcia 与 Tal 型密度输入（先自行核对原文）。不要做的事：继续加深模 2^k 枚举（第 3 步已给出不可能性与定量收益）；把 (β) 当短期目标。

### 3.4 `arithmetic-cycles`（算术与连分数）

**尝试了什么。** 主目标 T1：不存在非平凡正环。把问题写成 U 侧（K 的上界，来自 chaining 与 Λ 的界）与 L 侧（K 的下界，来自验证界与连分数台阶）的夹逼。本轮立住五条：可达范围定理 T2（窗口判据能排除的 K 必满足 K < (3X0 − 1)ln2，渐近 2.0794415 X0；证明只用「长度不小于 1 的区间必含整数」与 δ 的无理性）；幸存者族与阶梯上界 T3（正侧用奇数下标收敛项、负侧用偶数下标）；有理候选定理 T4（对每个奇偶字 s 都存在有理候选 x(s) 使 T^k(x(s)) = x(s)，故任何对每个字都成立的必要条件都没有排除力——判据想有力量必须用整性）；1 圈的归约与封闭 T5；最大元定向前缀引理与 c_max T6。

**最致命的一击。** 第一轮反驳判 fatal：负侧的「同型事实」为假（负侧必须用偶数下标，奇数 n 的 K = q_n 恰被负侧判据排除；实测 X0 = 10^4 时 665 个 K = m·306 中有 61 个被负侧排除，而作者称 0 个）；归约的 L 侧漏写前提「环上所有元素绝对值至少 X0」（反例是已知正环 {1,2}）；常数 2.0814 印错（应为 3 ln 2 = 2.0794415）；勘误口径回退。随后的第二轮核查又指出：作者在修补时引入的「更强反例」宣称（印反版被 {−5,−7,−10} 在 X0 = 2 处证伪，阈值 6.0 > 5）是错的——6.0 来自把正环侧含 (1 + X0^(−1))^m 因子的常数套到负环上，按负侧常数该处要求只是 |x_min| > 4。

**作者如何回应。** 第二轮四条全部接受并修订（T3 拆成两条、负侧段重写、数值复核新增负侧全量与抽样；正文六处常数改为精确式；补上勘误标注；脚本重跑）。对第二轮核查所指的「更强反例」宣称：本轮（第二轮 attempt）正文已无该宣称，但它仍留在**未被改动的** `attempt-round1.md:222` 与 `:341`（本报告实读两行确认），主脚本的注释与输出也仍带两处旧错（`rebuttal-2.md:102`）。

**最终状态。** 主目标 T1 未完成。失败点清单：F1（主缺口）全称收尾——U(m) 随 m 以 δ^m 量级增长而 L(m) 只随验证界与连分数台阶增长（对 m 递减），故对每个固定 X0 都存在交叉点之后夹逼必然失效；F2 U 侧排除判据未证（继承第一轮 F7，`rebuttal-2` 逐行核对 SdW 原文后确认该步未证）；F3 chaining 天花板的定量刻画不完整；F4「初等判据类」的边界没有形式定义（一致性缺口）；F5 第 10 步的 Rhin 下界为转引；F6 验证界门槛不可复核。

**下一步最该做什么。** 1. 修 F2：把「Λ 上界加连分数事实」写成对全部 K ≤ q_(N_max) 可核的显式必要条件，并核对交叉点。2. 修 F3 的一半：把「U(m) 与 L(m) 的交叉点必存在」写成定理或带明确假设的条件性定理。3. 把 1 圈封闭做成端到端（一手核对 Steiner 1977 或形式化 Rhin 常数）。**不要**在窗口型框架内重复投入算力（T2 已给出硬上界）。

### 3.5 `two-adic-control`（2 进与遍历控制）

**尝试了什么。** 主目标：周期猜想 PC_3（Φ 保持有理 2 进整数）。本轮证成三条自足定理：T1（等距刚性：与移位 S 交换的 2 进等距恰为 id 与 σ(x) = −1 − x；推论 T1′：T_a 与 T_b 之间的等距共轭恰两条且被奇偶性唯一区分，等距中心化子是二阶群）；T2（整数不保持：若存在 p 使 |Fix(T_a^p) ∩ ℤ| > |Fix(T_b^p) ∩ ℤ|，则不存在任何双射 Ψ 满足 Ψ∘T_a = T_b∘Ψ 且 Ψ(ℤ ∩ Z_2) ⊆ ℤ ∩ Z_2——对 Ψ 不作任何正则性假设）；O1（搬运的同义反复：把「有理点都是最终周期点」沿共轭搬运，其真值条件正是猜想本身）。另有：块码刻画、窗口 ≤ 4 的连续 S 交换双射分类、周期点参数化 Fix(T_a^p) = {c_v/(2^p − a^m_v)} 与整数计数谱。

**最致命的一击。** 「Φ_a 保低 p 位」为假：Φ_3(1) = −1/3 ≡ 5 (mod 8) ≠ 1、Φ_5(1) = −1/5 ≡ 3 (mod 4) ≠ 1。该断言被两处当作事实使用（步骤 8 细节与步骤 12），属「结论真而理由假」。

**作者如何回应。** 接受、删去该断言、换以等距性为核心的论证（Fix(S^p) 是模 2^p 的完整剩余系，等距把它映成完整剩余系，故 Fix(T_a^p) 亦然），并借修补把窗口分类从 ≤ 3 推到 ≤ 4（两类严格证书：非满射用子集构造、非单射用碰撞对证书，证书验证失败 0 例），补上步骤 1、2 的自足化证明。对反驳者宣称的「连续 S 交换双射必为等距」一般定理：记录为未核实、不采纳（本项目自己的过滤实验显示周期层条件严格弱于双射）。

**最终状态。** 主目标未证且本路线原理上够不到：由第一轮的还原定理，PC_3 等价于整族「3x + b 在 ℤ 上无发散轨道」（b = 1 就是猜想的无发散半边）。本轮的全部收获是否定性侧——共轭在算术上不透明，三层屏障（测度与拓扑层、共轭刚度层、算术搬运层）合起来把 frontier 第三节第 10 条的一部分从描述性判断提升为定理。

**下一步最该做什么。** 1. 不要在这条路线上继续找「共轭把有理点信息搬过来」的桥；若继续，应把目标定为「把屏障做成定理」。2. 窗口 ≥ 5 的分类，或那条一般定理（若成立，T1 立刻给出全部窗口的分类）。3. 把 T2 的覆盖推到所有 a ≠ b（需要整数周期点计数谱的一般规律）。4. 形式化「只使用保测同构型不变量」这一论证类。

### 3.6 `formal-automata`（形式化与自动机）

**尝试了什么。** 把受限版本编码为自动机与线性递推并尝试判定，用证书搜索证明受限证书形式下的不可能性定理。产物是 (S1) 至 (S8)：编码定理与 D_k 的自动机结构；2 进闭包版本的完全解；残类二分定理；非下降集结构与「永不下降」判据；显式下降判据；势函数与证书形式的否决；代价定理；残余缺口。

**最致命的一击。** 两条。一、(S3) 第 3 条把「σ 在类上取任意大的有限值」与「类词全前缀上升」的等价外推到含 σ = ∞ 的情形——那需要额外输入 (∗)（有限例外集内不含永不下降者），而把「有限例外」当成「有界」是无效推理；该等价完整形式恰是 Terras 系数停时猜想。二、(S5) 末句漏写同余条件，按字面为假（反例 k = 3、m = 1、n = 7：2·3 ≤ 8 且 7 > 3 而 T^3(7) = 26 ≥ 7）。

**作者如何回应。** 两条都接受并修补：(S3) 重写为五条并显式列出 (∗)；补证新引理 θ_w < 3^(len(w))，由此把例外集压进 [2, 3^a]，得 a ≤ 44 时 (∗) 可由 2^71 验证兑现（3^44 < 2^71 < 3^45 实跑核验）；(S5) 补全同余条件并说明 m = 0 情形平凡。另新增首降阈值的动态规划与 k = 65 的显式见证（θ = 364625035073295549935/420491770248316829 ≈ 867.1395，词为 65 位、类代表元 n = 30913060423816076283），并如实登记与反驳者报值 467.10 的分歧。

**最终状态。** 受限版本（2 进闭包）已被完全解决，而答案与猜想相反：该层上「几乎一切点都不到达 1」（反例 −1 与 4/5），失败集测度为 1。不可能性方向被代价定理封死：任何形如「∪_k D_k 不是 2 自动集」「不可定义于 ⟨N,+,V_2⟩」「非半线性」的定理都会顺手证否猜想，故在猜想为真的前提下这类定理不可能存在。**本路线没有第三条出口**：对原猜想本身零进展。

**下一步最该做什么。** 1. 把「全上升词情形」写成独立的可攻击判定问题（诚实提示：它落在发散轨道一侧，不知道是否比猜想容易，不要当捷径）。2. 给「测度型证书」写精确语法并重做循环性论证。3. 把四条初等引理（编码双射与周期点、二分、非下降集结构、显式判据）写成可机检命题——这是本路线唯一能稳赚的产出。

---

## 四、计算实验逐条

### 4.1 全量验证地基（`sweep`）

**范围。** n 从 1 到 2^28 = 268,435,456 的全部整数，一个不漏。计数约定与 OEIS A006577 一致。算法是记忆化加「只走到跌破自身」的加速，每条轨迹都显式下降，归纳即得结论（不使用猜想为真这一假设）。

**关键数字。** 有限总停时 268,435,456 / 268,435,456；最大总停时 956，唯一取到于 n = 226588897；63 个纪录保持者；校验 A 至 E 全过；OEIS A006577 逐条 10000 项零不一致，A006877 与 A006878 在范围内的 63 项零不一致；Terras 停时 χ 在 [3, 250000] 上最大值 135、唯一取到于 35655（与文献笔记一致）。

**独立重算是否一致。** 一致。纯 Python 任意精度再模拟（63 个纪录点加 3000 个随机点）零不一致；200000 个 xorshift64 随机点直接模拟零不一致；134,217,728 个偶数逐条满足递推。A006877 的 148 项中有 85 项超过 2^28，**未核对**（范围之外）。

**不能证明什么。** 不能证明猜想（范围只到 2^28）；不能排除非平凡环与发散轨道（只有「轨迹全部元素大于 2^28」的环才可能完全避开扫描）；不给任何密度或渐近结论；结论依赖实现正确性（一个只在未被抽样路径上生效的系统性缺陷不会被上述检查发现）。

### 4.2 停时分布（`stoptime-stats`）

**范围。** n 从 1 到 2^24 = 16,777,216 全部精确计算，无抽样。

**关键数字。** 全部到达 1；总停时均值 160.633636、标准差 62.853604、偏度 0.639281、峰度 3.432158（口径 n = 2 至 2^24）；最大 704 在 n = 15,733,191；Terras 停时（加速）最大 287 在 13,421,671；标准与加速停时均值比 1.499956（与 1.5 差 0.003%）；分带均值斜率 7.19191 对模型 7.22826（差 −0.503%）；正态性被拒（卡方 784231，自由度 27，p 值约 1.2×10^(−170233)）；右尾 t = 500 时实测 1537 对同矩正态预测 0.8（约 1900 倍）；范围最大值 704 只有重尾极值模型（Gumbel 矩拟合预测 690.50）接近；Krasikov 与 Lagarias 下界在 2^24 处折合覆盖率 7.19%。

**独立重算是否一致。** 一致。独立纯 Python 逐点比对 262,144 个 n 零不一致；与 OEIS b006577 逐点 10000 项零不一致；与 OEIS 纪录序列 57 条零不一致。

**不能证明什么。** 不能证明分布的正态性或非正态性（有限样本经验陈述）；不能证明 Krasikov 与 Lagarias 下界的任何改进或不可能性（7.19% 只是把文献表述按指数形式外推的示意，文献定理写「对充分大 x」且未给显式 x_0）；γ_k 外推无预测价值（纯曲线拟合）；漂移模型的吻合不能外推。

### 4.3 逆向树（`reverse-tree`）

**范围。** Python 版建树到 48 层；C 版主运行到 65 层（另有一次把内存阈值放宽到 2.1 GB 的补跑到达 66 层）；前向停时表覆盖 n ≤ 10^6 的 500,000 个奇数。

**关键数字。** C 版 65 层累计 354,832,309 节点（三次运行逐层一致），补跑 66 层为 473,112,998 节点、峰值内存 3.31 GB；末 10 层平均比值 1.333347（对 4/3 差 +0.0010%）；常数 N(d)/(4/3)^d 在 d = 40 至 66 稳定于 0.6713 附近（精确最大 0.6713615458、最小 0.6713032319、精确极差 0.0000583139）；显式建树只完整覆盖奇数到 n = 25；第一个缺席的奇数是 27（出现深度 70）；M(70) = 53、M(71) = 71、M(73) = 95、M(75) = 127；覆盖奇数到 1000 需深度 113（由 871 达到）；层结构恒等式「第 d+1 层奇数个数 = 第 d 层中 x ≡ 2 (mod 3) 的节点数」在 d = 2 至 64 全成立（d = 1 是根去重造成的唯一例外）。

**独立重算是否一致。** 部分一致。独立复现记录（`40-formal/independent-checks/reverse-tree-recheck.md`，另一套完全独立的实现）复现了 M(D) 全表、层结构恒等式、第 8、16、24 层表格与 d = 113 的覆盖结论；**深跑本身（第 65、66 层）未重跑**，其可信度依赖报告自己的双向校验（层内严格递增、每个孩子的父节点在上一层二分可查）与三次运行逐字一致。本报告实跑该复核脚本，输出一致。

**不能证明什么。** 「增长率是 4/3」只是 66 层内的经验事实；常数 0.6713 没有被证明收敛；显式建树在覆盖性上极不划算（推到 75 层才覆盖到 127，而单层内存已近 6 GB 量级外推值）；本实验对无限情形零结论。

### 4.4 奇偶向量与 2 进结构（`parity-vectors`）

**范围。** 仿射公式与 c 递推在长度 ≤ 16 的全部 131,070 个向量上；环搜索在长度 ≤ 32 的全部 8,589,934,590 个向量上（剪枝跳过 2,545,358,193 个）；共轭映射置换结构到 n ≤ 30；τ = χ 检验到 x ≤ 2^30（1,073,741,824）与「τ ≤ 40 的全体 x」（1,228,671,536 个首降向量、15,263,013,070 个节点）；Terras 密度对照在 X = 2^28（k 到 240）。

**关键数字。** c 递推与闭式在 131,070 个向量上零不一致；仿射公式在 32,752 个组合加 200 个随机大整数上零失败；长度 ≤ 32 搜索的整除命中 116 次全部通过奇偶向量一致性（含退化解 x = 0 则节点 148），去重后恰四个环族（{1, 2} 与 −1、−5、−17），伪命中 0；A(3) = 0（结构性）；K3 的 τ = χ 在两套范围内零反例，最接近反例的三种口径分别为 2.000000、2.285714、0.495069；密度定理实测比值与 1 的偏离上确界：k ≤ 155 时 2.5502%（在 k = 135）、k ≤ 200 时 10.4540%、k ≤ 240 时 15.4630%。

**独立重算是否一致。** 一致（含口径订正）。复核员用无剪枝穷举确认了「命中 116 与 148」的口径差异，并用精确有理数独立复现 P[τ ≥ 135]；K2 朴素版的最小反例是 j = 2、x = 5 与 x = 1 同类（精确版判据在 x ≤ 2^18、j ≤ 12 逐点 0 不符）。Bernstein 与 Lagarias 的表 2.1 与 2.2 是逐格复核（原文表格以渲染图像读出，存在人工转录风险）。

**不能证明什么。** 不能证明不存在非平凡正环（周期大于 32 的环完全未触及，与文献记录的 10^11 量级差 10 个数量级）；不能把 τ = χ 的有限检验说成全称结论（范围落在 Terras 旧验证之内，是独立复核不是新范围）；不能证明 Bernstein 与 Lagarias 的定理本身；不能给出密度定理的误差项。

### 4.5 环搜索（`cycles`）

**范围。** 无条件完备枚举 k ≤ 34 的全部奇偶向量；完备剪枝与穷举对照到 k ≤ 30；自算验证界做到 X0 = Y0 = 10^12（两种实现）；判据排除上界算到 X0 = 10^12 并给出代价表。

**关键数字。** k ≤ 34 全枚举（叶子 3.44×10^10、节点 6.87×10^10）用时 70.2 秒，解行 168 条全部经 Python 独立复核，去重后恰五个环（{0}、{1, 2} 与三个非平凡负环 {−1}、{−5,−7,−10}、{−17 族}），即**无非平凡正环、非平凡负环有三族**；阳性对照完整；剪枝把节点砍 1.8 至 3.1 倍但单节点成本升高约 11 倍，净效果更慢（如实报告的负面结果）；验证界 10^12：正侧 4815.8 秒、负侧 5473.6 秒，两侧零未判定、零新环，最大步数 550 与 539；判据表见 乙6、乙7；推到 m ≥ 10^8 需要 X0 > 2.46×10^15（折算约 140 至 190 天，或位表法约 300 TB 内存）。

**独立重算是否一致。** 一致。`40-formal/independent-checks/criterion_exclusion_recheck.py` 用定点整数模运算（不做浮点比较）独立复算七档 M± 表，全部一致；`criterion-recheck.md` 另复核了前提不等式在四个已知环上的成立性。

**不能证明什么。** 不能证明「没有非平凡正环」；判据那两条带前提（环上元素绝对值至少 10^12、已知五个环除外），漏写前提就会与已知环矛盾（本项目自己被复核员点过一次）；验证界本身未被形式化验证（60 位与 200 位浮点比较，无非区间算术证书）；负环穷尽性是文献里的猜想而非本工作结论。

### 4.6 截断势函数与反例搜索（`smt-certificate`）

**范围。** 证书搜索在截断 [1, N] 上，线性形式到 N = 2^20，按位加权形式到 N = 2^18（补充试跑到 2^20），逐 k 冲突对到 k = 20；轨道反例搜索在 x ≤ 2^20；F 变体证书延展验证到 2^24。

**关键数字。** 形式无关的命题 1：截断上不存在任何满足 V(T(x)) ≤ V(x) − 1 的势函数（因为 1 → 2 → 1），UNSAT 核恰为 {x = 1, x = 2}；命题 2：对每个 k ≥ 2，x = 2^k − 1 与 x = 2^k 一对方程已经矛盾（差分 w_k − w_(k−1) 与 w_(k−1) − w_k 相加为 0），故整个按位加权类被否证，去环后的最小核恰为 {x = 3, x = 4}；松弛变体 F（只要求奇步严格降）SAT，权重尾部为负斐波那契，在 [3, 2^24] 的 8,388,607 个奇 x 上零违规，而 8,388,608 个偶 x 全部违反严格降；轨道反例搜索给出多个可复核长轨道（K = 200 时 SAT，x = 867203，精确停时 218）。

**独立重算是否一致。** 一致。证书另用 `direct_reference.py --verify-json` 第二条独立代码路径复验；停时计算用第二条独立实现交叉核对（「标准步数 = 加速步数加奇值步数」在抽样点全部成立）；直接计算与 z3 真值对照一致。

**不能证明什么。** 不否证猜想；不否证「存在某种势函数型证明」（被否证的只有按位加权类与两个松弛族；形式不受限时同一问题在 [3, 4096] 上 SAT）；不构成「无环」的证据（UNSAT 的核心恰是环附近的状态）；z3 的 unknown 不构成任何存在性或不存在性（K = 300 与 328 限时 unknown，而真值可由直接计算确定为存在）。

### 4.7 精确检查闸门（`40-formal`）

**范围与结果。** `40-formal/exact_check.py` 用精确整数与 Fraction 复核四条初等引理：仿射公式与双射（k ≤ 16 的全部 131,071 个剩余类与字）、c 的递推（递推、闭式、拼接恒等式）、环方程与 2^k > 3^m 的必要性（含负环阳性对照，找回三个负环）、停时与阈值判据（含反向不成立的最小见证）。全部算术精确、无浮点、不读取其他实验的输出。

**本报告的实测。** 命令 `"$PY" 40-formal/exact_check.py`，**退出码 0**，输出 56 行，四条引理全部 PASS，失败 0。闸门通过。

**不能证明什么。** 四条引理都是全称命题，有限枚举不能确立它们；PASS 只说明所枚举范围内无反例（脚本自己的声明写在文件抬头）。

---

## 五、机器可复核清单（完整命令）

以下命令一律使用项目自带解释器：

```bash
PY='/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python'
cd "/Users/luna/Documents/math IA/collatz-attack"
```

**1. 精确检查闸门（本报告实跑：退出码 0，四条引理全 PASS）**

```bash
"$PY" 40-formal/exact_check.py; echo "exit=$?"
```

**2. 独立验算记录（本报告全部实跑）**

```bash
"$PY" 40-formal/independent-checks/q23_convergents.py              # q_23、q_23+q_24、两个周期下界
"$PY" 40-formal/independent-checks/criterion_exclusion_recheck.py  # M± 七档（约 2.4 秒）
"$PY" 40-formal/independent-checks/barrier_and_exponents.py        # 屏障与指数换算
"$PY" 40-formal/independent-checks/reverse_tree_recheck.py        # M(D) 表与层结构
```

**3. 顶路线的三个关键数字（本报告实跑，逐位复现存档）**

```bash
cd 30-proof-attempts/diophantine-transcendence
"$PY" dt2_check2.py    # 门槛 1.7233559e+22、log10 = 22.2364、两道墙 1.04317 与 1.33641
"$PY" dt2_struct.py    # 记录乘积 q*gap+ 单调不增 = True（约 95 秒）
"$PY" dt2_up.py        # 分离界贡献上限 7.3%（m = 91）、K_surv(92) 对 K_low(92) 的 4.332 倍
"$PY" dt2_cf.py        # 连分数 q_20 至 q_34 与 SdW Corollary 11 对照（会改写 dt2_q.txt）
"$PY" dt2_ladder.py    # Hercher 自举七步
"$PY" dt2_soundtail.py # 四种尾部口径的前沿表
"$PY" dt2_corr.py      # 勘误凸性论证的两条要点
"$PY" dt2_l2.py        # 一致性阈值
```

**4. 算术路线的 1 圈封闭（本报告实跑，约 3 分钟）**

```bash
cd ../arithmetic-cycles
"$PY" scripts/arithmetic_cycles_round2.py       # K ≤ 20000 唯一候选 (1,1,2)；门槛 K0 = 108
```

**5. 2 进路线（本报告实跑：与存档逐字节相同）**

```bash
cd ../two-adic-control
"$PY" scripts/round2_verify.py /tmp/twoadic_mine.txt && md5 /tmp/twoadic_mine.txt
# 期待 MD5 = 5da059c4f9b555357c11afe8fba7c664
diff /tmp/twoadic_mine.txt results/round2_run1.txt   # 应无输出
```

**6. 自动机路线（本报告实跑：26 条通过、失败 0、退出码 0）**

```bash
cd ../formal-automata
python3 -u checks_automata_v2.py                 # 约 47 秒
python3 -u checks_formal_automata.py             # 第一轮脚本，17 条通过（本报告未重跑）
```

**7. 红队意见的核对命令（本报告实跑）**

```bash
cd "/Users/luna/Documents/math IA/collatz-attack"
grep -cE "^(theorem|def|example|lemma|abbrev|noncomputable def|private def) " 40-formal/lean/CollatzBasic.lean   # 51
grep -n "max=287\|1.4999558440" 20-experiments/findings/stoptime-stats.md                                      # :127、:128
grep -n "^39\." 10-literature/notes/claims-2024-2026.md                                                       # 第 39 条在 :73
grep -n "^7\. " 10-literature/notes/two-adic.md                                                               # 第 7 条在 :41
sed -n '287p' 30-proof-attempts/diophantine-transcendence/attempt.md    # 两种口径并列
sed -n '91,95p' 30-proof-attempts/diophantine-transcendence/rebuttal-2.md  # 作者未采纳
sed -n '95p;293p;349p' 30-proof-attempts/tao-quantitative/attempt.md    # (丙) 仍在正文
sed -n '222p;341p' 30-proof-attempts/arithmetic-cycles/attempt-round1.md   # 更强反例宣称仍在
```

**8. 六组实验（本报告未重跑；命令照录自各 findings 的「完整命令行」节）**

```bash
cd "../../20-experiments"
# 8.1 全量验证地基（findings/sweep.md 第 49 至 57 行）
mkdir -p results/oeis
curl -s -o results/oeis/b006577.txt https://oeis.org/A006577/b006577.txt
curl -s -o results/oeis/b006877.txt https://oeis.org/A006877/b006877.txt
curl -s -o results/oeis/b006878.txt https://oeis.org/A006878/b006878.txt
cc -O3 -Wall -Wextra -o scripts/sweep scripts/sweep.c
/usr/bin/time -p ./scripts/sweep 268435456 results/sweep_records.tsv results/sweep_lens.tsv > results/sweep.txt 2> results/sweep.stderr
./.venv/bin/python scripts/sweep_check.py results/sweep.txt

# 8.2 停时分布（findings/stoptime-stats.md 第 88 至 107 行）
cc -O3 -o stoptime_dist stoptime_dist.c
time ./stoptime_dist 16777216 "/Users/luna/Documents/math IA/collatz-attack/20-experiments/results" \
     262144 "/Users/luna/Documents/math IA/collatz-attack/20-experiments/results/stoptime_dump.csv"
time ./.venv/bin/python scripts/stoptime_stats.py
time ./.venv/bin/python scripts/verify_stoptime.py results/stoptime_dump.csv 262144

# 8.3 逆向树（findings/reverse-tree.md 第 68 至 93 行）
"$PY" scripts/reverse_tree_bfs.py --depth 48 --coverage-limit 1000000 \
     --json results/revtree_py_d48.json --txt results/revtree_py_d48.txt
cd scripts && cc -O3 -o reverse_tree_deep reverse_tree_deep.c && cd ..
/usr/bin/time -l ./scripts/reverse_tree_deep --depth 66 --odd-list-depth 20 --mem-guard-gb 2.0 \
     > results/revtree_c_deep.txt 2> results/revtree_c_deep_time.txt
"$PY" scripts/reverse_tree_analysis.py --py-json results/revtree_py_d48.json \
     --c-txt results/revtree_c_deep.txt --coverage-limit 1000000 --odd-table-limit 200
"$PY" scripts/reverse_tree_recheck.py

# 8.4 奇偶向量与 2 进结构（findings/parity-vectors.md 第 44 至 64 行）
./.venv/bin/python scripts/parity_vectors.py > results/parity-vectors-python.txt
cc -O3 -o scripts/cycle_search scripts/cycle_search.c
./scripts/cycle_search 32 > results/parity-vectors-cycle-search-K32.txt
cc -O3 -o scripts/bl_permutation scripts/bl_permutation.c
./scripts/bl_permutation 30 > results/parity-vectors-bl-permutation.txt
cc -O3 -o scripts/stopping_conjecture scripts/stopping_conjecture.c
./scripts/stopping_conjecture 1073741824 > results/parity-vectors-stopping-conjecture.txt
cc -O3 -o scripts/theta_analysis scripts/theta_analysis.c
./scripts/theta_analysis 40 > results/parity-vectors-theta-analysis.txt
cc -O3 -o scripts/terras_density scripts/terras_density.c
./scripts/terras_density 268435456 > results/parity-vectors-terras-density.txt

# 8.5 环搜索（findings/cycles.md 第 93 至 134 行）
cc -O3 -march=native -pthread -o scripts/cycles_bs_enum        scripts/cycles_bs_enum.c
cc -O3 -march=native -pthread -o scripts/cycles_verify_bound   scripts/cycles_verify_bound.c
cc -O3 -march=native -pthread -o scripts/cycles_verify_free    scripts/cycles_verify_free.c
cc -O3 -march=native -pthread -o scripts/cycles_stopping_stats scripts/cycles_stopping_stats.c
./scripts/cycles_bs_enum 0 34 1 > results/cycles_enum_exhaustive_k34_rerun.txt   # 70.2 秒
./scripts/cycles_verify_free 1000000000000 1000000000000 8   # 两侧共约 2.9 小时
.venv/bin/python scripts/cycles_criterion.py 1000000 100000000
.venv/bin/python scripts/cycles_criterion_sides.py 100000000 3000000000 10000000000 30000000000 100000000000
.venv/bin/python scripts/cycles_criterion_exact_M.py 1000000 30000000000 100000000000 1000000000000

# 8.6 截断势函数（findings/smt-certificate.md 第 55 至 73 行）
"$PY" -u scripts/smt_certificate_search.py --N 1048576 --N-small 4096 --timeout-ms 900000 \
       --json-out results/certificates_2e20.json > results/smt_certificate_search_2e20.txt 2>&1
"$PY" -u scripts/smt_certificate_search.py --N 262144 --N-small 4096 --timeout-ms 600000 \
       --json-out results/certificates_2e18.json > results/smt_certificate_search_2e18.txt 2>&1
"$PY" -u scripts/smt_orbit_counterexample.py --N 1048576 --timeout-ms 120000 --extra-k 328 \
       --json-out results/smt_orbit_2e20.json > results/smt_orbit_counterexample_2e20.txt 2>&1
"$PY" -u scripts/direct_reference.py --N 1048576 > results/direct_reference_2e20.txt 2>&1
"$PY" -u scripts/verify_fib_certificate.py --limit 16777216 --domain-N 262144 \
       | tee results/verify_fib_certificate_2e24.txt
```

**9. 其余路线的核验脚本**

```bash
# 最小反例路线（约 14 秒）
cd "/Users/luna/Documents/math IA/collatz-attack/30-proof-attempts/minimal-counterexample"
python3 verify_lemmas.py > verify_output_rerun.txt 2>&1
python3 verify_rebuttal.py > verify_rebuttal_output_rerun.txt 2>&1
python3 verify_dichotomy.py > verify_dichotomy_output.txt 2>&1

# 量化路线（各脚本的输出已存档于 checks/ 下）
cd "../tao-quantitative/checks"
"$PY" check_D_tilt.py ; "$PY" check_E_rotation.py 20 2000 2000 ; "$PY" check_G_sa.py
"$PY" check_H_kq.py 22 20000 64 256 1024 ; "$PY" check_I_sa_exact.py 60 ; "$PY" check_J_toy.py 20000
```

**10. Lean（本报告未运行：本机无工具链）**

```bash
bash "40-formal/setup-lean.sh"    # 需联网装 elan 与 Mathlib，数 GB 磁盘
cd "$HOME/lean-collatz-formal" && lake env lean "/Users/luna/Documents/math IA/collatz-attack/40-formal/lean/CollatzBasic.lean"
```

---

## 六、未做的事与做不到的事

**本报告的实测边界（读与跑分开记账）。**

1. **本报告亲自实跑的命令**：`40-formal/exact_check.py`（退出码 0）；四个独立验算脚本（q_23、判据七档、屏障与指数、逆向树 M(D)）；`dt2_check2.py`、`dt2_struct.py`、`dt2_up.py`（顶路线三个数字）；`arithmetic_cycles_round2.py`；`round2_verify.py`（与存档逐字节相同）；`checks_automata_v2.py`（26 条通过）；一次自写的 mpmath 连分数复算（q_23 = 137,528,045,312 等逐位一致）；以及第五节第 7 组的红队核对命令。此外逐行读取了列在证据指针里的原始输出文件。
2. **本报告未重跑、只读存档的**：六组实验的 C 程序与主脚本（sweep、stoptime_dist、reverse_tree_deep 深跑、cycle_search、cycles_bs_enum、cycles_verify_free 的 10^12 档、smt 的 z3 求解、全部 tao 的 check 脚本、`minimal-counterexample` 的三个 verify 脚本、第一轮的 `checks_formal_automata.py`）。这些数字的证据是各自的原始输出文件，本报告未对它们做机器复算。
3. **文献层的读法**：`10-literature/frontier.md`、`notes/stopping-times.md`、`notes/cycles.md` 通读；`notes/barriers.md` 的第一至第三节、`notes/claims-2024-2026.md` 第五节与技术极限节、`notes/verification.md` 的关键结果节精读；`notes/tao-almost-all.md`、`notes/two-adic.md`、`notes/undecidability.md` 只读结构与 frontier 的压缩判断与条目定位，未逐页通读。凡本报告引用这三份笔记涉及的文献断言，一律走 frontier 或各路线 attempt 的一手核对记录，并保留其「原文未打开」标注。
4. **本机做不到的事**（`20-experiments/ENV.md` 实测）：没有 Lean、lake、elan、Coq、Isabelle、PARI、Sage，因此任何形式化结论都无法在本机复核（Lean 源码只能写、不能编译）；只有 8 GiB 内存，大 SAT 与 10^15 级验证界都不可行；GPU 不可用（Metal 编译器缺失）；系统 python3 三个候选都缺关键库。
5. **本工作明确未做的计算**：2^71 级全量验证（引用 Barina 2025）；10^15 级验证界（折算约 140 至 190 天）；Hercher 五周 C++ 计算的重构（验证界门槛 1536×2^60 不可复核）；Simons 与 de Weger 第 7 节的格枚举段；两个 Lean 仓库的源码重建与编译（只读文本）；Rhin 1987、Barina 2025、SdW 期刊版、Eliahou 1993、Steiner 1977、Terras 1976 等原文的亲手核对（多处为转引，逐条见台账丙16）。
6. **做不到的事（数学上）**：把任何「几乎所有」结论升级为全称结论（无已知桥梁）；排除发散轨道（文献侧无技术，本项目六条路线全部在此或等价处止步）；把分离界的改进变成前沿的实质推进（被天花板引理封在 7.3% 内）；由有限验证推出全称命题；由自动机路线得到任何不可能性定理（代价定理说明那会自毁）。

---

## 七、攻坚地图：六条路线的失败点合并

### 7.1 六条路线的失败点对照

| 路线 | 主目标 | 最致命的一击 | 最终状态 | 离完整证明还差什么（一句话） |
|---|---|---|---|---|
| `diophantine-transcendence` | 初等（不用 Rhin）证明 m ≤ M* 且 M* > 91 | 终点上界的一致性缺失：逐区间分离界被当一致界用；且主结论的唯一支柱（Hercher Theorem 21 尾部）有公开争议 | 未证；M* > 91 只在几何尾部口径下成立（健全口径 82 或 86），第一次超过 91 需把验证界抬到 1.7233559×10^22 | 需要与 K 无关的一致机制：log_2 3 部分商的显式上界（或等价的无理测度）并去掉对验证界 X0 的依赖 |
| `tao-quantitative` | T1（固定阈值对数密度为零）与 T2（Λ(A_1) = 0） | 逐层正上界 K(log C)^(−c) 对每个固定 C 都不归零；任何常数级改进都不行 | 未证；T3 只到条件性 m^(−1/4)；T4 是数值猜想 | 需要零点型输入：某固定层对数密度为零（等价：对每个固定 m，Λ(B_m) = 0），且必须敏感于 3N+1 的「加 1」 |
| `minimal-counterexample` | 不存在 n ≥ 2 使 χ(n) = ∞ | 情形 II（χ = ∞、τ < ∞、轨道无界）的全部约束（模筛、大小约束、临界游走、悖论序列）都与它相容，不产生矛盾 | 未证；三情形分类已证，I 与 III 接文献机具，II 无工具 | 需要把悖论序列的显式无穷族与最小反例的算术联合成矛盾的种子——或一条能察觉「常数级对数权重」的估计形式 |
| `arithmetic-cycles` | 不存在非平凡正环 | 全称收尾失败：U(m) 随 m 以 δ^m 增长而 L(m) 对 m 递减，对每个固定 X0 都有交叉点之后失效 | 未证；1 圈档已封闭（精确检验加转引下界）；窗口型判据被硬卡在 (3X0 − 1)ln2 | 需要 U 侧排除判据本身（现为数值观察）与「交叉点必存在」的定理，或与 m 无关的新上界形状 |
| `two-adic-control` | 周期猜想 PC_3 | 主目标等价于整族「3x + b 无发散轨道」，b = 1 就是猜想的无发散半边；共轭在算术上不透明 | 未证且原理上够不到；否定性侧立住（T1、T2、O1） | 需要轨道显式伪随机性质（不属于 2 进动力学），或把「跨零测集的桥梁」造出来 |
| `formal-automata` | 用自动机与证书形式推进猜想 | 受限版本（2 进闭包）真值与猜想相反（−1、4/5）；等价于猜想的那一层（Z = ∅）只被改写成无穷多条阈值不等式 | 未证；不可能性方向被代价定理封死，本路线没有第三条出口 | 需要判定「全上升词是否有整数实现」（τ 有限性）与 (∗)（Z 的完整刻画）——两者都不比猜想显然容易 |

### 7.2 合起来的攻坚地图

把六条线并排看，只剩三类互不相同的技术屏障，每一条路线都至少撞上其中一个：

**屏障一、从「几乎所有」到「所有」没有技术（拦住 `tao-quantitative` 与 `minimal-counterexample`）。** 全部密度型结果碰不到零密度例外集；单条坏轨道加它的加倍链对 [1, X] 的对数权重至少 1/N_0，是常数，与一切 o(log X) 型估计相容。跨过它需要「某固定层为零」的零点型输入或能察觉常数级权重的估计形式——本工作给出的是这一障碍的精确形状（B 族逐层等价、陷阱引理、筛饱和引理），没有跨过它。

**屏障二、发散轨道没有工具（拦住 `minimal-counterexample` 的情形 II、`tao-quantitative` 的 (β)、`two-adic-control` 的主目标、`formal-automata` 的 Z 层）。** 四条路线从四个不同的角度走到同一个对象：不下降到起点以下的轨道。 Lagarias 2010 的判断（排除发散轨道须先证明迭代的显式伪随机性质）在本工作中被四次独立复现为「每条路线自己的语言里的同一个缺口」。

**屏障三、丢番图分离性的「一致性」而非「精度」（拦住 `diophantine-transcendence` 与 `arithmetic-cycles`）。** 两条路线的终点都要求关于 \|x log 2 + y log 3\| 的显式下界对全部参数一致有效，而现有输入（Rhin 1987 的逐点常数、连分数逐区间台阶）都不是一致机制；连分数方法的可达范围被硬卡在 (3X0 − 1)ln2 或被部分商尾部条件拦死，且前沿对验证界只有对数依赖（M* ≈ 5.0 log_10 X0 − 14，即每 10 倍验证界换约 5 个 m；推到 m ≤ 10^8 需约 2.0×10^7 个数量级的验证界）。本工作同时给出这条屏障上的两条定量负结果：分离界对 m 圈前沿的贡献上限 7.3%（改进它需要 1.19×10^18 倍，而 Dirichlet 只允许约 100 倍）；周期 ≤ 34 的无条件枚举（无非平凡正环）与 10^12 验证界下的必要条件排除（周期至少 17,087,915，且带前提）。

**共同还要背着的三条硬约束**（任何完整证明必须满足，`10-literature/frontier.md:105` 至 `:117`）：用只对 a = 3 成立的事实（5x+1 有环且与 3x+1 在 Z_2 上同构）；用正性（负整数有三个非平凡环）；证书形式的步数必须无界（n ≡ −1 mod 2^k 反例）且不能假定轨道高度被初始值固定倍数控制（sup T_m/m 无界）。

### 7.3 离完整证明「最近的三个可操作增量」（都不是证明；以下是本报告的排序判断，不是文献结论）

1. **把 Hercher Theorem 21 的尾部定案**：逐步复核或形式化勘误的凸性替代推导，并与两个 Lean 仓库做公开对照。这是本项目已两次触到、也是唯一一处「只差一次可判定复核」就会同时影响前沿记录（91 与 82）与一条方向禁令（分离界无助于前沿）的环节。
2. **把记录乘积 q·gap⁺(q) 单调不增证明出来**（本工作已数值核验 320 条记录全过）：若成立，初等版终点上界的一致性问题会从「无穷合取」退化为「一个显式常数检查」。
3. **把 Tao 定理全有效化并与 2^71 验证合并**（frontier 活口第 3 条，Tao 自己在 Remark 1.4 脚注里列为「原则上可能」）：产物是「Col_min(N) = 1 对正对数密度的 N 成立」——它不产出猜想，更不产出固定阈值版本，但它是现行体系里最接近可达的中间门槛。

### 7.4 结语

本工作能做实的，是把边界钉死、把局部结果做到可独立复核、把每条路线的失败点写成可攻击的具体命题（哪一步、为什么是缺口、跨过它需要什么）。它做不到的，是把任何一条路线补完。就本工作掌握的全部证据看：猜想两侧的现状是——**无环一侧机械最完整（m ≤ 91 带勘误争议、K > 1.375×10^11、周期 ≥ 3.55×10^11 的标准口径）但全面临一致性与验证界依赖两道墙；无发散一侧没有任何机械，且本工作沿六条路线的四次独立尝试都止步于同一个缺口。** 科拉茨猜想仍然是开放问题。

---

## 八、对红队意见的回应

红队对本报告提出 12 条意见（引用行号见 `50-report/final-report.md` 本节的逐条；红队的原始列表由本次任务的提示给出）。逐条处理如下：11 条完全成立并已修改，1 条（第 8 条计数）部分成立、已按更严口径重写计数规则与组成。另对红队的两处行号引用偏差作了订正（见本节末与第九节）。

1. **甲6 的无条件口径（成立，已修改）。** 甲6 改写为：Hercher 论文与勘误**主张**不存在 m ≤ 91 的 m 圈，并明确写出该主张带未裁决争议（甲7）与本项目笔记自己的判定（`10-literature/notes/claims-2024-2026.md:73`：「m ≤ 82、m ≤ 91、m ≤ 101 三个数字都不能当作既成记录；能当作记录的是 Hercher 论文与勘误本身」）。附带说明：7.1 表中的 M* 是本工作机具算出的前沿（另一个对象），与 Hercher 的发表值并非同一量；但红队指出的「甲6 读起来像既成记录」成立，已改。
2. **乙3 与摘要的「非平凡整数环」（成立，已修改）。** 改为「非平凡**正环**」，并在乙3 补注同一次枚举找回的三个非平凡负环及其周期。同时如实登记：来源 `20-experiments/findings/cycles.md:243` 的措辞「周期不超过 34 的非平凡整数环一个也没有」与紧随其后的负环清单自相矛盾，本报告此前沿用了该措辞；现已按同一节的环清单读作「非平凡正环」（该内部不一致已登记进丙15）。
3. **甲13 的「转引」标注（成立，已修改，并订正行号）。** 「T 在 Z_2 上每个周期轨道皆有理」已从 Bernstein 与 Lagarias 条目中拆出并标「转引」，指针为 `10-literature/frontier.md:29`（自记转引自 Rozier，其引 Lagarias 1990）、`10-literature/notes/two-adic.md:41`（自记「Lagarias 1990 原文我未能打开」）、`30-proof-attempts/two-adic-control/attempt.md:245`（列为「转引、本轮未用」）。**红队引用的 `two-adic.md:7` 是笔记的条目编号而不是行号；正确行号是 41**（本报告实跑 `grep -n "^7\. " 10-literature/notes/two-adic.md` 确认）。
4. **甲13 的附录范围（成立，已修改）。** 已写明：`two-adic-control/attempt.md:330` 至 `:348` 的附录只自证步骤 1、2（T_a 良定义、保测、共轭、等距与 Φ_a(Q∩Z_2) ⊆ Q∩Z_2），不含「处处不可微」，后者属转引（`attempt.md:164`、`:245`）。
5. **丙2 与 3.1 的口径冲突（成立，已修改）。** 3.1 现在把第三轮的判断明确记为「本项目自己的反驳备忘录的主张」并给出其证据指针，同时写明作者未采纳；丙2 保持「不裁决，两个口径并列」。
6. **3.1 的「全部接受并修补」（成立，已修改）。** 已改为分层叙述：第二轮指控与五处细节 = 作者接受并修补（7 条）；第三轮的核心建议（把 82 降格、把勘误论证做成可传播的证明、检验第三方的「最坏情形」前提）= **未采纳**，作者维持两个口径并列（`30-proof-attempts/diophantine-transcendence/attempt.md:287`），第三轮备忘录对此记为「作者未做、而本应做的事」（`rebuttal-2.md:93`、`:95`）。
7. **`tao-quantitative` 计数含未修补项（成立，已修改）。** 计数规则重写为「只要作者的回应文件记录为已接受并修补或修订才计入」；该栏的 4 条组成已写明为「首轮三条 + Sparre Andersen 状态标注一处」，(丙) 与「所需输入的形状描述」移入「未修补」单列（见 3.2 与丙7）。
8. **`arithmetic-cycles` 与 `minimal-counterexample` 的计数不可复现（部分成立：数目本身可复现，但此前未给组成，已补）。** 现已在第三节开头逐条列出组成与文件行号：`arithmetic-cycles` 7 条 = 第二轮四条（`attempt.md:297` 至 `:344`）＋第一轮三条（`attempt-round1.md:335` 至 `:345`），其中「文本与脚本不一致」只部分落实（`rebuttal-2.md:102`）；`minimal-counterexample` 5 条 = 第三轮 G1 一条 ＋ 第一轮三项撤下与一项界订正（`attempt.md:5`）。若按红队更严的读法（只计本报告叙述里逐条列出的条目），两栏分别是 5 与 4；本报告采用「凡作者回应文件中有编号且可指认行号者即计入」的更宽口径，并把该口径写明。计数保持 26（逐条组成见第三节开头）。
9. **丙14 的 Lean 条数（成立，已修改）。** 本报告本轮自查（命令见第五节第 7 组）：`40-formal/lean/CollatzBasic.lean` 行首关键字计 **51 条**（37 theorem、7 def、7 example）；`40-formal/README.md:6` 记「50 条」，两数差 1 未对齐，现并列写入丙14。另自查：`sorry` 与 `admit` 在代码中均为 0（`sorry` 一词仅出现在文件头注释第 20 行）。原报告的「50 条」是转述 README 而非自查，现两数并列。
10. **乙2 的证据指针（成立，已修改）。** 指针改为 `20-experiments/findings/stoptime-stats.md:118` 至 `:133`（C 程序汇总原文，其中 287 在 `:127`、均值比 1.4999558440 在 `:128`）与 `:265`（关键数字第 6 条的 1.499956）。
11. **乙13 的「5 位」（成立，已修改）。** 已拆开表述：区间 [0.6672, 0.6675] 与 0.6674426 相符到 **4 位**有效数字（区间出处 `tao-quantitative/attempt.md:152`）；「相符到 5 位」只对精确计数值 0.66744（同文件 `:145`）与 0.6674426 成立。
12. **摘要的 Tao 条（成立，已修改）。** 摘要改为「Tao 型逐层正上界不归零——这是与 Tao 定理相容的读法，不是不可能性定理」，与丙6 的限定一致。

**红队意见中本报告不接受的部分：无实质条目；仅两处行号引用需订正。** 除第 3 条里已订正的 `two-adic.md`（条目编号 7、实际行号 41）之外，第 1 条引的 `claims-2024-2026.md:39` 同样是**条目编号**而非行号：该判定文字在文件的第 73 行（本报告实跑 `grep -n "^39\." 10-literature/notes/claims-2024-2026.md` 得到 73）。两处内容（而非行号）都被本报告采纳。

**红队指出而本次仍未处理的争议（进入本报告 unresolved 清单）**：「m ≤ 91」与「m ≤ 82」的裁决；`tao-quantitative` 的 (丙) 与形状描述；`arithmetic-cycles` 的「更强反例」宣称与脚本残留；`formal-automata` 的 k = 65 数值分歧；`two-adic-control` 的一般定理未核实；「K 门槛到周期下界」未形式化；Lean 未编译；M*(X0) 表单实现与 q·gap⁺ 单调性未证明；加速映射周期下界无一手出处与两处内部记录不一致。逐条见台账丙1 至丙16。

---

## 九、红队抽查记录

**红队抽查的条数：12 条。** 本报告处理的条数：**12 条**（全部处理），其中：

1. **完全采纳并已修改：11 条**（第 1、2、3、4、5、6、7、9、10、11、12 条）。
2. **部分采纳并已按更严口径重写：1 条**（第 8 条计数规则；计数器保持 26，但补上逐条组成、文件行号与「更严读法会更低」的对照）。
3. **订正红队的引用偏差：2 处**（`claims-2024-2026.md` 的判定在第 73 行而非第 39 行；`two-adic.md` 的「Lagarias 1990 原文我未能打开」在第 41 行而非第 7 行；两处都是把条目编号当成了行号，内容均已被本报告采纳）。
4. **本报告本轮为验证红队意见实跑的命令**（全部照录于第五节第 7 组）：Lean 声明计数（51）、`stoptime-stats.md` 的 `:127` 与 `:128`、`claims` 第 39 条的实际行号、`two-adic.md` 第 7 条的实际行号、`attempt.md:287` 与 `rebuttal-2.md:91` 至 `:95` 的原文、`tao-quantitative/attempt.md:95`、`:293`、`:349` 三行原文、`attempt-round1.md:222` 与 `:341` 两行原文。
5. **未解决事项**：见第八节末段与台账丙1 至丙16；红队本身指出的争议（如 91 与 82 的裁决）不因本次修改而解决。

---

*本报告的每一条数字都在正文里给出文件路径或命令；凡本报告亲手实跑的，均已在本会话内执行并记录退出码与输出（第五节与第六节逐条对应）。凡未跑的，均标注为未跑。本报告不产生任何关于科拉茨猜想的新结论，也不对「m ≤ 91」与「m ≤ 82」之争作裁决。*
