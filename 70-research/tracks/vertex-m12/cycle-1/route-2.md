# vertex-m12 轨道 第 2 路线报告：八核精确穷举主攻（m₂ = 12 升档核对）

**路线**：路线二「八核精确穷举主攻」
**轨道**：vertex-m12（顶点识别的机器核对升一档），cycle-1
**日期**：2026 年 10 月 28 日
**性质**：机器核对（附范围）。本文件内每个结论都标注级别；未跑、未证、未核实处逐条写明，不作口头担保。

---

## 〇 一句话结论

在参数冻结（δ = 126797/80000，即 log₂3 的严格下界；W = 2000）下，C 主实现以两条独立精确求解路径完成 m₂ = 12 的全部 C(25,12) = 5200300 个活跃子集穷举：**可行顶点数 = 12，且顶点集与解析的 12 个循环旋转精确相等（SETS_EQUAL True，逐坐标精确有理比较）**；同一实现下 m₂ = 10 校准与 Python 参考实现的判定串**逐字节一致**（352716 个判定全同，md5 `b269256bfff877a81fa5a81047a4c958`）；推档 m₂ = 13（20058300 个子集，第二路复核全部非 'S' 子集）与 m₂ = 14（77558760 个子集，第二路全量复核）同样给出「恰 m₂ 个循环旋转」，五档双路失配数全为 0。**上述范围之外的档位、一切其他参数取值、以及 δ 取真值的口径，仍属未证**（逐条见第九节）。

---

## 一 要检验的精确陈述与冻结口径

### 1.1 陈述 R(m₂, δ, W)（要检验的精确命题）

记窗口多面体 P(m₂, δ, W) ⊂ R^{m₂} 为下列 2m₂ + 1 条约束的交（逐字照 frozen/r2_common.py 的 `constraint_list`，md5 `cfee819667c0883e73732f03d2dc8bef`）：

1. (C1) y_j ≥ 1，j = 1..m₂（m₂ 条）；
2. (C2) y_{j+1} ≤ δ·y_j，j = 1..m₂，指标循环（m₂ 条；j = m₂ 即回绕约束 y_1 ≤ δ·y_{m₂}）；
3. (C3) Σ_{j=1}^{m₂} y_j ≥ W（1 条）。

**陈述 R(m₂, δ, W)**：P 的全部极点（顶点）恰为解析族

    V_r = v·(δ^{(0+r) mod m₂}, δ^{(1+r) mod m₂}, …, δ^{(m₂−1+r) mod m₂})，r = 0..m₂−1，
    v = W·(δ − 1)/(δ^{m₂} − 1)

这 m₂ 个循环旋转，且互不相同。

**本次检验的机器化判据**（与 frozen 语义逐字一致）：枚举全部 C(2m₂+1, m₂) 个大小为 m₂ 的约束子集 S；对每个 S，精确解线性方程组（S 的全部约束取等号），若解不唯一（含不相容）记 'S'；若唯一解在全部 2m₂+1 条约束下不可行记 'I'；可行记 'F'（即顶点候选）。判定集 {S 的解 | 判定 'F'} 就是机器核对口径下的顶点集。

### 1.2 参数冻结（先冻后跑）

1. δ = 126797/80000：沿袭项目 A1/E4 口径，为 log₂3 的严格**下界**（由 `delta_rigorous_bounds(10**7)` 给出，只用整数幂比较）。**口径注**：本次核对对象是「δ 取该有理数」的多面体 P(m₂, 126797/80000, 2000)，不是真 δ = log₂3 的无理多面体；二者之间的桥梁不属本次核对范围。
2. W = 2000（与 m₂ = 10 基线同参）；核对的档位 m₂ ∈ {5（边界校准档）、10（校准档）、12（主档）、13、14（推档）}。W = 2000 在 10 至 14 档均满足 (P1)（阈值 (δ^{m₂}−1)/(δ−1) 依次约 169.32、427.93、679.25、1077.58，均小于 2000）；v 依次约 11.81、4.67、2.94、1.86，均大于 1。
3. m₂ = 5 档取 W = (δ⁵ − 1)/(δ − 1) = 630347359154513105681/40960000000000000000（阈值上的边界情形 v = 1，即既有日志 E10 档；本次用它做与 `r2_b_out.txt:91` 至 `:99` 的对照，不属 R 的升档核对）。

### 1.3 依赖边界（写死在实现里）

允许：约束表逐字转写、初等线性代数（极点与活跃约束秩、唯一解判据）、精确有理算术（GMP mpq 与 Python Fraction）、组合枚举完备性。
禁止：(L1)（「y_j = 1 不可行」）、顶点引理的任何结论、凸性推导、v 的数值参与判定。
落实与审计：`grep -in "L1\|lemma\|convex\|polytope\|(P1)"` 在 `route2_vm_core.c`、`route2_vm_core.h`、`route2_vm_main.c`、`route2_ref_enum.py` 四文件中**零命中**（注释内亦无）；符号 `v`（`Vq`）在 C 实现里只出现于解析集比对与打印（`route2_vm_main.c` 第 22、361、374、375、577、578、589、613、617、619 行），判定路径完全不读它。

---

## 二 编号论证（每步标注级别）

### 2.1 完备性引理（把「枚举」与「顶点集」接起来的初等命题）

**引理 A1（已证；本轮自证；初等线性代数，无 (L1)、无凸性）**：点 y ∈ P 是 P 的极点（顶点）当且仅当 y 处活跃约束的法向量集之秩等于 m₂。

证明。(⟸) 反设 y = (y₁ + y₂)/2，y₁、y₂ ∈ P，y₁ ≠ y₂。每条活跃约束写成 n·x ≥ b（C1、C3 原样；C2 写成 δy_j − y_{j+1} ≥ 0）。则 n·y = b，且 n·y₁ ≥ b、n·y₂ ≥ b，相加得 n·y₁ = n·y₂ = b，故 d := y₁ − y₂ ≠ 0 与全部活跃法向量正交，秩至多 m₂ − 1，矛盾。(⟹) 若活跃法向量秩小于 m₂，取非零 d 正交于全部活跃法向量；活跃约束在 y ± εd 处仍取等，非活跃约束余量正，故 ε 充分小时 y ± εd ∈ P，y 是两端点的中点，不是极点。∎

**引理 A2（已证；构造性；纸面证明）**：解析族的每个 V_r 都可行，且其活跃约束恰为「除一条回绕链外的 m₂ − 1 条链约束 + 和约束」共 m₂ 条，其法向量秩 = m₂；特别地每个 V_r 是顶点。

证明要点。可行性：v 大于 1 使 C1 严格成立；链指数相邻差为 1（跨模处为 1 − m₂），除跨模那条外链约束全部取等，跨模那条为 v ≤ v·δ^{m₂}（因 δ 大于 1 严格成立）；Σ = v·(δ^{m₂}−1)/(δ−1) = W 取等。秩：这 m₂ 条法向量（m₂ − 1 条链行 + 全 1 行）线性无关（把变量按被移除的那条链切成一条路径后，链行诱导移位的线性无关结构成立，全 1 行不在链行张成里）。∎

**引理 A3（等价于原命题的翻译）**：机器判据的 'F' 点集恰为 P 的极点集。

证明。任取极点 y，由 A1 存在大小 m₂、秩 m₂ 的活跃子集 S；S 的方程组有唯一解且解就是 y，且 y 可行，故枚举到 S 时判 'F'。反过来，任何判据 'F' 的点 y 满足 rank(Act(y)) ≥ rank(S) = m₂，由 A1，y 是极点。∎

### 2.2 机器核对结果（级别：机器核对，附范围；五档原始输出可逐字 grep）

1. **m₂ = 10（校准档，阳性对照）**：子集总数 352716（乘法与 Pascal 两法互校 equal=True）；判定计数 S = 295780、I = 56926、F = 10；顶点数 10，与解析 10 个旋转 SETS_EQUAL True；证书（活跃约束法向量秩，活跃约束条数）= (10, 10)，与基线 `r2_j_A.txt:14` 的「[(10, 10)]」一致。
2. **m₂ = 12（主档）**：子集总数 5200300（两法互校 True，= C(25,12)）；判定计数 S = 4752735、I = 447553、F = 12；顶点数 12，与解析 12 个旋转 **SETS_EQUAL True**；证书 (12, 12)；第二路精确求解对**全部 5200300 个子集**逐一复核（其中解向量逐坐标比较 447565 次），mismatches = 0。
3. **m₂ = 13（推档）**：子集总数 20058300（两法互校 True，= C(27,13)）；判定计数 S = 18811533、I = 1246754、F = 13；顶点数 13，与解析 13 个旋转 SETS_EQUAL True；证书 (13, 13)；第二路复核全部**非 'S'** 子集（compared = 1246767，'I' 与 'F' 全体），mismatches = 0。**覆盖缺口**：18811533 个 'S' 判定未过第二路。
4. **m₂ = 14（推档）**：子集总数 77558760（两法互校 True，= C(29,14)）；判定计数 S = 74098262、I = 3460484、F = 14；顶点数 14，与解析 14 个旋转 SETS_EQUAL True；证书 (14, 14)；第二路对**全部 77558760 个子集**复核（解向量比较 3460498 次），mismatches = 0。
5. **m₂ = 5（边界校准，E10 档 v = 1）**：子集总数 462；判定计数 S = 170、I = 262、F = 30（每个顶点 6 个证书子集）；顶点数 5，与解析 5 个旋转 SETS_EQUAL True；证书 (5, 6)，与 `r2_b_out.txt:98` 的「[(5, 6)]」一致。五档的 `DECISIONS_COMPLETE PASS (undecided=0)`、`ENUM_CONTINUITY_CHECK PASS`、`MISMATCHES_TOTAL 0`、`EXIT_OK` 全部成立。

### 2.3 结构性观察（机器核对级，附范围）

各档 'F' 判定在字典序中都恰位于最末区段：m₂ = 5 的 'F' 共 30 个（5 顶点 × 6 证书）；m₂ = 10 的 F 集 = {352706..352715}；m₂ = 12 的 F 集 = {5200288..5200299}；m₂ = 13 的 F 集 = {20058287..20058299}；m₂ = 14 的 F 集 = {77558746..77558759}。每个证书子集形如「m₂ − 1 条链 + 和约束」（如 m₂ = 12 的 `VERTEX 0 certs=1 cert_subset_idxs=5200292[12,13,14,15,16,17,18,20,21,22,23,24]`）。这与引理 A2 的纸面预测（恰 m₂ 条活跃、缺一条回绕链）一致，但本身只是观察，不作普遍断言。

### 2.4 与既有基线的对照与成本曲线

1. m₂ = 10：判定计数、顶点数 10、解析集相等、证书 (10, 10) 与 `r2_j_A.txt` 全中。
2. m₂ = 12：既有记录只到「投影约 72 分钟（未跑）」（`ledger.md:25`、`cycle-1/route-2.md:205`）；本次给出全量实跑。Python 单核口径为 0.83 毫秒/子集（乘以 5200300 约 71.9 分钟）；C 双路精确实现八线程墙钟 **38.27 秒**（第五节；运行期间机器负载很高，见第六节第 3 条）。
3. m₂ = 5：判定计数与证书 (5, 6) 与 `r2_b_out.txt:91` 至 `:99`（含「全穷举（C(2m2+1, m2) = 462 个子集，不依赖 L1）：可行顶点数 = 5；与约简一致 = True」）一致。

---

## 三 实现、依赖清单与「不依赖任何引理」的落实

### 3.1 文件与版本身份（md5 为本次实测）

| md5 | 行数 | 路径（相对本轨道 `cycle-1/`） |
|---|---|---|
| `25edc679aa8ca9ce0650e6eb666e8ec0` | 637 | `scripts/route2_vm_main.c` |
| `eb4b9978cd187c229788317660229cf3` | 377 | `scripts/route2_vm_core.c` |
| `8686adc13cb5bcd2040e547f9e47c521` | 42 | `scripts/route2_vm_core.h` |
| `714ab3cbbf28e812180577731faa9c19` | 可执行，70352 字节 | `scripts/route2_vm_enum`（二进制） |
| `7cfa5b6c326476bf5cb0fc6ed8bdcf0d` | 164 | `scripts/route2_ref_enum.py`（Python 参考实现） |
| `cfee819667c0883e73732f03d2dc8bef` | 244 | `scripts/frozen/r2_common.py`（冻结副本，与 `70-research/cycle-1/scripts/r2_common.py` 逐字节一致，`diff -q` 已验证） |
| `4b8ce2a500d8ca9021fd0178deca637e` | 272 | `scripts/frozen/r2_j_independent_vertices.py`（冻结副本，同上） |

编译命令（退出码 0、零警告）：

    cc -O2 -Wall -Wextra -I/opt/homebrew/include -L/opt/homebrew/lib -I. \
       route2_vm_main.c route2_vm_core.c -lgmp -lpthread -o route2_vm_enum

（Apple clang 不支持 `-fopenmp`，故多核用 **pthreads 加互斥量领取分片**，不依赖 libomp；精确算术用 **GMP mpq**，全程无浮点、无近似。）

### 3.2 双路精确求解器（互为独立校验）

1. **路径 A（结构分解，`structure_solve`）**：沿循环链按缺口把变量切成路径分量，分量头显式求解（链关系 y_v = δ^{dist} 乘以 h），再由签约束定头、和约束定唯一自由头。情形判别：唯一解等价于「无同分量双签，且 (s = 0 且签分量数 = 分量数) 或 (s = 1 且签分量数 = 分量数 − 1)」。该判别式是代码旁注里的推导，**其正确性由路径 B 的全量对拍承担**。
2. **路径 B（通用消元，`generic_solve`）**：mpq 精确 RREF，列扫描取首个非零枢轴、全行消元，与冻结 `r2_common.solve_exact` 同算法序；行只做正数缩放，不改解集。
3. **交叉核对**：逐子集比较两路判定字符；两路都判定有唯一解时解向量逐坐标精确比较；不一致会落 MISMATCH 行并非零退出。实测失配全为 0（第 2.2 节）。
4. **无预筛**：本实现没有任何近似或启发式预筛；两条路径都是全称精确判定，'F' 候选必须同时通过两路才入集。题面「预筛只允许判死、候选必须精确复验」在此被更强地满足。

### 3.3 枚举完备性的三重落实

1. 下标覆盖：分片按子集下标 [0, Total) 连续切分（块长 = (Total + 511) 整除 512），每子集恰处理一次（`THREAD_SETS_SUM == total : True` 五档全过）。
2. 组合双法互校：`unrank` 与 `next_comb` 在每个分片边界衔接核对（`ENUM_CONTINUITY_CHECK PASS`）；子集总数用乘法公式与 Pascal 表两法断言相等（五档全过）。
3. 判定完整性：处理完毕后判定缓冲无空缺（`DECISIONS_COMPLETE PASS (undecided=0)` 五档全过）。

### 3.4 依赖清单（两级）

1. **数学依赖**：约束表逐字转写；初等线性代数（A1、A3）；唯一解判据与精确有理算术；组合枚举完备性。**零 (L1)、零顶点引理、零凸性推导、零 v 数值参与判定**（审计见 1.3 节与第八节第 9 条）。
2. **代码依赖**：C 主实现只依赖 GMP 与 pthread；Python 参考实现只 import `fractions` 与冻结的 `r2_common`，不 import 任何其它项目脚本。

---

## 四 校准与对拍

### 4.1 m₂ = 10 阳性对照：C 与 Python 逐比特一致

1. 判串（每子集一个字节，共 352716 字节）三方 md5 全同：C 八线程 = C 单线程 = Python 参考 = `b269256bfff877a81fa5a81047a4c958`；并逐字节 `cmp`：C 八线程 对 Python `IDENTICAL`、C 单线程 对 Python `IDENTICAL`（352716 个判定全部相等，不是抽样）。
2. 顶点清单对拍：C 日志中的 30 行 `VERTEX …` 行（10 顶点乘 3 行）与 Python 参考写出的顶点文件逐字节相同（`diff` 只报出 C 侧多出的摘要行）。
3. 判定计数：两实现都给出 S = 295780、I = 56926、F = 10；与基线口径（顶点数 10、10 个旋转、证书 (10, 10)）全中。
4. 线程数无关性：C 单线程墙钟 14.02 秒与八线程墙钟 2.84 秒判串 md5 相同，验证「八线程无重无漏」在本档成立。

### 4.2 m₂ = 5 边界档（E10，v = 1）对照

判定计数 S = 170、I = 262、F = 30；5 个顶点与解析集相同；证书 (active_count = 6, active_rank = 5)，与 `r2_b_out.txt:98` 的「[(5, 6)]」一致；判串 md5 `18e23746174db60150198149b00cd869`。

### 4.3 第二实现（Python）的分片对拍（每段都与 C 判串对应区间逐字节相同）

| 档与区间 | Python 判定计数 | md5（两实现同值） |
|---|---|---|
| m₂ = 12 [0, 60000) | S=57534 I=2466 F=0 | `3fc7cb4298234a9a35157a67468cdabb` |
| m₂ = 12 [2570000, 2630000) | S=57197 I=2803 F=0 | `01d48b64c306fcda9abf601a1cee60da` |
| m₂ = 12 [5140000, 5200300) | S=51158 I=9130 F=12 | `6ed10684ab1144eed0718d983ebbac7b` |
| m₂ = 13 [0, 60000) | S=58256 I=1744 F=0 | `b3a1a41dab9edab79470d174440fdded` |
| m₂ = 13 [20000000, 20058300) | S=50900 I=7387 F=13 | `0df416d6afade99f69e439cae879c482` |
| m₂ = 14 [0, 40000) | S=39110 I=890 F=0 | `aed2dfe579abcd7927c87672ecdf53fb` |
| m₂ = 14 [77400000, 77558760) | S=142825 I=15921 F=14 | `032e82bc5fca23d1804ff270e4e4b963` |

每档的**顶点判定（'F'）所在尾部区段全部被这七段覆盖**，即三档的顶点判定都经过 Python 独立实现的逐字节复核。**覆盖缺口**：Python 侧对 12、13、14 档均非全量（覆盖率 3.47%、0.59%、0.26%），未覆盖区段只由 C 实现给出。

### 4.4 阴性对照的口径诚实说明

本路线**未跑** m₂ = 2、δ = 3/2、W = 3/2 的阴性对照（该配置验证「v 小于 1 时预测族不是顶点集」；证据在路线一：`r1_selfcheck.py` 第 [3] 节，同轮材料收集员已亲跑并落盘 `materials/repro-r1_selfcheck.txt`，md5 `0d1509629af57fa586edb666b2f19403`）。本路线对负向判别的能力由另一路径部分覆盖：m₂ = 5 边界档（v = 1）报出含坐标 1 与回绕等式的顶点；m₂ = 10 至 14 档的 'S' 与 'I' 判定（合计百万量级）与 Python 参考在全部对拍区段一致，说明判据不会无条件输出旋转。

---

## 五 主档与推档细节（原始输出关键行）

### 5.1 m₂ = 12（主档）

命令：

    { time ./route2_vm_enum 12 126797 80000 2000 8 results/route2/c_m12_t8_decisions.txt \
        --expect-total 5200300 --expect-vertices 12 --tag m12-T8 --cross full \
        --chunkmap results/route2/c_m12_t8_chunkmap.txt > results/route2/c_m12_t8_log.txt 2>&1 ; } \
      2> results/route2/c_m12_t8_time.txt

原始输出关键行（`results/route2/c_m12_t8_log.txt` 可逐字 grep）：

    PARAMS M=12 N=25 delta=126797/80000 W=2000/1 threads=8 cross=full
    TOTAL_SUBSETS mult=5200300 pascal=5200300 equal=True
    EXPECT_TOTAL PASS (5200300)
    ENUM_CONTINUITY_CHECK PASS
    DECISIONS_COMPLETE PASS (undecided=0)
    DECISION_COUNTS S=4752735 I=447553 F=12 total=5200300
    CROSSCHECK compared=5200300 sol_cmp=447565 mismatches=0 mode=2
    THREAD_SETS_SUM 5200300 (== total : True)
    TIME_SAMPLE pathA n=18774 avg_ns=566.8
    TIME_SAMPLE pathB n=18774 avg_ns=59151.5
    ENUM_WALL_SEC 38.234
    FEASIBLE_SUBSETS 12
    VERTEX_COUNT 12
    EXPECT_VERTICES PASS (12)
    ANALYTIC_COUNT 12 VERTEX_COUNT 12 MATCH 12 SETS_EQUAL True
    MISMATCHES_TOTAL 0
    EXIT_OK

墙钟（`c_m12_t8_time.txt`）：`real 0m38.271s`、`user 1m51.020s`、`sys 0m0.581s`。

顶点集证据：12 个顶点每个都 `certs=1`、`active_count=12 active_rank=12`；证书下标恰为 {5200288..5200299}；坐标以精确分数打印（`VERTEX 0 coords=…` 至 `VERTEX 11 coords=…` 共 12 行），解析 v = 1717986918400000000000000000000000000000000000000000000000/367585379715027714724468362329970166286740140554559688053。判串 `c_m12_t8_decisions.txt`（5200300 字节）md5 `8fb4ba1aef28fdc293b52270985ec35e`。

### 5.2 m₂ = 13（推档，第二路覆盖「非 'S' 全体」）

命令：

    { time ./route2_vm_enum 13 126797 80000 2000 8 results/route2/c_m13_t8_decisions.txt \
        --expect-total 20058300 --expect-vertices 13 --tag m13-T8 --cross alive \
        > results/route2/c_m13_t8_log.txt 2>&1 ; } 2> results/route2/c_m13_t8_time.txt

关键行：

    TOTAL_SUBSETS mult=20058300 pascal=20058300 equal=True
    DECISION_COUNTS S=18811533 I=1246754 F=13 total=20058300
    CROSSCHECK compared=1246767 sol_cmp=1246767 mismatches=0 mode=1
    TIME_SAMPLE pathA n=72413 avg_ns=660.6
    TIME_SAMPLE pathB n=4573 avg_ns=99317.5
    ENUM_WALL_SEC 16.913
    VERTEX_COUNT 13 / EXPECT_VERTICES PASS (13)
    ANALYTIC_COUNT 13 VERTEX_COUNT 13 MATCH 13 SETS_EQUAL True
    MISMATCHES_TOTAL 0 / EXIT_OK

墙钟：`real 0m17.013s`、`user 0m51.773s`、`sys 0m0.356s`。证书下标 {20058287..20058299}，每顶点 `certs=1`、`active_count=13 active_rank=13`（如 `VERTEX 0 certs=1 cert_subset_idxs=20058287[13,14,15,16,17,18,19,20,21,22,23,24,26]`）；解析 v = 137438953472000000000000000000000000000000000000000000000000000/46677442868462369143918414938353227174659789601896504766056241。判串 md5 `152514f874a144554d1dff2ec0570da9`（20058300 字节）。**注意模式差异**：本档第二路只复核了非 'S' 的 1246767 个子集，与 10、12、14 档的全量复核不同（登记为覆盖缺口）。

### 5.3 m₂ = 14（推档，第二路全量复核）

命令：

    { time ./route2_vm_enum 14 126797 80000 2000 8 results/route2/c_m14_t8_decisions.txt \
        --expect-total 77558760 --expect-vertices 14 --tag m14-T8 --cross full \
        > results/route2/c_m14_t8_log.txt 2>&1 ; } 2> results/route2/c_m14_t8_time.txt

关键行：

    TOTAL_SUBSETS mult=77558760 pascal=77558760 equal=True
    DECISIONS_COMPLETE PASS (undecided=0)
    DECISION_COUNTS S=74098262 I=3460484 F=14 total=77558760
    CROSSCHECK compared=77558760 sol_cmp=3460498 mismatches=0 mode=2
    THREAD_SETS_SUM 77558760 (== total : True)
    TIME_SAMPLE pathA n=279996 avg_ns=738.3
    TIME_SAMPLE pathB n=279996 avg_ns=45518.6
    ENUM_WALL_SEC 458.351
    FEASIBLE_SUBSETS 14 / VERTEX_COUNT 14 / EXPECT_VERTICES PASS (14)
    ANALYTIC_COUNT 14 VERTEX_COUNT 14 MATCH 14 SETS_EQUAL True
    MISMATCHES_TOTAL 0 / EXIT_OK

墙钟：`real 7m38.640s`、`user 33m42.177s`、`sys 0m11.475s`。证书下标 {77558746..77558759}，每顶点 `certs=1`、`active_count=14 active_rank=14`。判串 md5 `37921d19726088fb8be115707a749356`（77558760 字节）。

### 5.4 成本曲线实测汇总（高负载下测得，作上界读）

| 档 | 子集总数 | 第二路模式 | 墙钟 | 抽样每子集（路径 A / 路径 B） |
|---|---|---|---|---|
| m₂ = 10 | 352716 | full | 2.84 s（八线程）；14.02 s（单线程） | 59.7 µs / 84.6 µs（八线程，n=1274）；单线程 0.76 µs / 46.9 µs（n=1274） |
| m₂ = 12 | 5200300 | full | 38.27 s | 0.57 µs / 59.2 µs（n=18774） |
| m₂ = 13 | 20058300 | alive | 17.01 s | 0.66 µs / 99.3 µs（n=72413 与 n=4573） |
| m₂ = 14 | 77558760 | full | 458.4 s（7 分 38 秒） | 0.74 µs / 45.5 µs（n=279996） |

单核外推（仅算术）：m₂ = 12 单核约 5200300 乘以 59.8 µs 约 5.2 分钟，对比 Python 单核口径（0.83 毫秒/子集，约 71.9 分钟）约快 13.9 倍。所有耗时含高负载影响（第六节第 3 条）。

---

## 六 失败点清单（诚实登记；未做的一律写明）

1. **Python 第二实现对 12、13、14 档非全量**：对拍覆盖率 3.47%（180300/5200300）、0.59%（118300/20058300）、0.26%（198760/77558760）；各档 'F' 尾部区段全被覆盖，但未覆盖区段的 'S'、'I' 判定只由 C 实现给出。不足以排除「两实现在未对拍区段同错」的风险。
2. **m₂ = 13 的第二路覆盖缺口**：18811533 个 'S' 判定只由路径 A 给出；10、12、14 档无此缺口。
3. **机器负载**：运行期间 load average 约 72 至 268（并行 actor 占用），全部墙钟为受扰值；八线程并行度实测约 2.9 至 4.4。耗时不作为算法效率的干净度量。
4. **δ 取有理下界的口径**：全部结果针对 P(m₂, 126797/80000, 2000)；从「下界多面体的顶点集」到「真值多面体的顶点集」的推理不属本轮，未做。
5. **纸面推导未形式化**：引理 A2 与路径 A 的情形判别属纸面推导（A2 有完整证明，路径 A 的判别式靠对拍）；本机无 Lean 与 Coq，全部核对未形式化。
6. **语义对拍非形式化**：C 与 Python 的判定语义一致性由「同一约束表、同一不等式方向、同一唯一解口径」逐行核对加 m₂ = 10 全量对拍支撑，但不是形式化证明。
7. **阴性对照未由本路线重跑**：m₂ = 2、δ = 3/2、W = 3/2 的证据沿用路线一与材料收集员的 `r1_selfcheck.py` 复跑（第 4.4 节）。
8. **未重跑**：`r2_b_vertices.py` 的其余 11 个参数集（只跑了 E10 边界档对照）、B 段 z3 日志、`cycle-1/verify.py`。
9. **小档多核失效**：m₂ = 5 冒烟只有 1 个分片（THREAD 1 至 7 空闲）；不构成缺陷，仅说明小档八线程不生效。
10. **顶点集独立复验脚本的输出捕获**：m₂ = 12 的输出已捕获（见第八节第 8 条）；m₂ = 13、14 的同法脚本已执行但输出未在本会话捕获落盘，如实登记；这两档的顶点判定可信度由第 4.3 节的 'F' 尾部段逐字节一致与 C 侧 `SETS_EQUAL True` 行共同承担。
11. **「预筛」条款无对象**：本实现不存在预筛（双路全精确），题面「预筛只允许判死」在此无对象；若未来加入预筛，必须仍满足「候选顶点过精确复验」。

---

## 七 局部新结论及其独立验证方式

（级别一律为「机器核对（附范围）」。）

1. **R(12, 126797/80000, 2000) = 真**：P 的全部极点为 12 个循环旋转（全量 5200300 子集）。独立验证：(a) 双路逐子集对拍 mismatches = 0；(b) Python 参考在三段确定性分片（含全部 'F' 尾部段）判串逐字节一致；(c) 顶点坐标经 Python 脚本用冻结 `r2_common` 重解复核（可行、活跃秩 12、与解析集精确相等）。
2. **R(13, …, 2000) = 真**（非 'S' 全复核口径）与 **R(14, …, 2000) = 真**（双路全量口径）：顶点数为 13 与 14，均与解析旋转集精确相等（各档 `ANALYTIC_COUNT … SETS_EQUAL True` 行）。独立验证：m₂ = 14 的双路全量对拍（compared = 77558760，mismatches = 0）加两档的 Python 分片对拍（含 'F' 尾部段）。
3. **五档判串与判定计数成为可复跑的固定指称**（md5 与字节数见第八节第 10 条）。
4. **成本曲线**：C 双路精确实现八核墙钟 m₂ = 12 为 38.3 秒、m₂ = 13（alive 口径）17.0 秒、m₂ = 14 为 7 分 38 秒；这给出了「更大档位（15 至 19）在八核上仍属可达、m₂ 不小于 20 全活跃穷举不可达」的下一步界（投影级，未跑）。
5. **结构性事实**：五档的 'F' 都密集出现在字典序最末区段，证书模式「m₂ − 1 条链 + 和约束」，与 A2 的纸面预测一致。

---

## 八 完整命令行与原始输出摘要（可复跑）

均在 `…/vertex-m12/cycle-1/scripts/` 下执行；`PY` 指 `/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python`。

1. 编译（退出码 0、零警告）：见 3.1 节命令；二进制 md5 `714ab3cbbf28e812180577731faa9c19`。

2. 冒烟（m₂ = 5，E10）：

       ./route2_vm_enum 5 126797 80000 630347359154513105681/40960000000000000000 8 \
          results/route2/m5_e10_decisions.txt --expect-total 462 --expect-vertices 5 \
          --tag m5-E10 --cross full > results/route2/m5_e10_log.txt 2>&1

   输出关键行：`DECISION_COUNTS S=170 I=262 F=30 total=462`、`VERTEX 0..4 active_count=6 active_rank=5`、`ANALYTIC_COUNT 5 VERTEX_COUNT 5 MATCH 5 SETS_EQUAL True`、`EXIT_OK`；判串 md5 `18e23746174db60150198149b00cd869`。

3. m₂ = 10 校准：

       { time ./route2_vm_enum 10 126797 80000 2000 8 results/route2/c_m10_t8_decisions.txt \
           --expect-total 352716 --expect-vertices 10 --tag m10-T8 --cross full \
           --chunkmap results/route2/c_m10_t8_chunkmap.txt > results/route2/c_m10_t8_log.txt 2>&1 ; }
       { time ./route2_vm_enum 10 126797 80000 2000 1 results/route2/c_m10_t1_decisions.txt \
           --expect-total 352716 --expect-vertices 10 --tag m10-T1 --cross full \
           > results/route2/c_m10_t1_log.txt 2>&1 ; }

   输出：三方判串 md5 同为 `b269256bfff877a81fa5a81047a4c958`（含 Python 参考 `route2_ref_enum.py --m2 10 --range 0:352716`），逐字节 `cmp` 双 `IDENTICAL`；八线程墙钟 2.840 秒、单线程 14.022 秒；Python 参考 `ELAPSED_SEC 318.3`。

4. m₂ = 12 主档：见 5.1 节命令；判串 md5 `8fb4ba1aef28fdc293b52270985ec35e`；墙钟 38.271 秒。

5. 推档（命令见 5.2、5.3 节；`--cross alive` 与 `--cross full` 之差已在第 2.2 节登记）：

       m₂ = 13：判串 md5 152514f874a144554d1dff2ec0570da9；墙钟 17.013 秒
       m₂ = 14：判串 md5 37921d19726088fb8be115707a749356；墙钟 7m38.640s

6. Python 分片（每段一条命令）：

       "$PY" route2_ref_enum.py --m2 12 --range 0:60000          --out results/route2/py_m12_slice_a.txt --progress 0
       "$PY" route2_ref_enum.py --m2 12 --range 2570000:2630000  --out results/route2/py_m12_slice_b.txt --progress 0
       "$PY" route2_ref_enum.py --m2 12 --range 5140000:5200300  --out results/route2/py_m12_slice_c.txt --progress 0
       "$PY" route2_ref_enum.py --m2 13 --range 0:60000          --out results/route2/py_m13_slice_a.txt --progress 0
       "$PY" route2_ref_enum.py --m2 13 --range 20000000:20058300 --out results/route2/py_m13_slice_b.txt --progress 0
       "$PY" route2_ref_enum.py --m2 14 --range 0:40000          --out results/route2/py_m14_slice_a.txt --progress 0
       "$PY" route2_ref_enum.py --m2 14 --range 77400000:77558760 --out results/route2/py_m14_slice_b.txt --progress 0

7. 逐字节对拍脚本（内联 heredoc；读 C 判串对应子串比较）：

       "$PY" - <<'EOF'
       import hashlib
       spans = {12: [(0,60000),(2570000,2630000),(5140000,5200300)],
                13: [(0,60000),(20000000,20058300)],
                14: [(0,40000),(77400000,77558760)]}
       names = {12: "abc", 13: "ab", 14: "ab"}
       for m, sp in spans.items():
           c = open(f'results/route2/c_m{m}_t8_decisions.txt','rb').read()
           for nm, (a, b) in zip(names[m], sp):
               p = open(f'results/route2/py_m{m}_slice_{nm}.txt','rb').read()
               seg = c[a:b]
               print(f'm2={m} slice_{nm} [{a},{b}) IDENTICAL={seg==p} md5={hashlib.md5(seg).hexdigest()}')
       EOF

   实测输出：七行全 `IDENTICAL=True`，md5 与第 4.3 节表一致。

8. 顶点集独立复验（解析各档 C 日志的 `VERTEX … coords=` 行，用冻结 `r2_common.feasible` 与精确秩复核，并与解析旋转集比较）。m₂ = 12 的实测输出：

       C 侧顶点数 = 12 (应为 12)
       C 顶点集 == 解析旋转集 : True
         V0..V11: 可行=True 活跃条数=12 活跃秩=12（逐点）
       全部顶点可行且活跃秩 = m2 : True

   （m₂ = 13、14 的同法脚本已执行，输出未在本会话捕获落盘，见第六节第 10 条。）

9. 依赖审计：

       grep -in "L1\|lemma\|convex\|polytope\|(P1)" route2_vm_core.c route2_vm_core.h route2_vm_main.c route2_ref_enum.py
       # 输出为空（零命中）

10. 判串 md5 一览（文件均在 `scripts/results/route2/`）：

        m5_e10_decisions.txt       18e23746174db60150198149b00cd869       462 字节
        c_m10_t8_decisions.txt     b269256bfff877a81fa5a81047a4c958       352716 字节
        c_m10_t1_decisions.txt     b269256bfff877a81fa5a81047a4c958       352716 字节
        py_m10_decisions.txt       b269256bfff877a81fa5a81047a4c958       352716 字节
        c_m12_t8_decisions.txt     8fb4ba1aef28fdc293b52270985ec35e       5200300 字节
        c_m13_t8_decisions.txt     152514f874a144554d1dff2ec0570da9       20058300 字节
        c_m14_t8_decisions.txt     37921d19726088fb8be115707a749356       77558760 字节

11. 日志与计时文件：`c_m10_t8_log.txt`、`c_m10_t1_log.txt`、`c_m12_t8_log.txt`、`c_m13_t8_log.txt`、`c_m14_t8_log.txt` 与各自 `*_time.txt`，分片映射 `c_m10_t8_chunkmap.txt`、`c_m12_t8_chunkmap.txt`，以及 `py_m12_slice_*_log.txt` 等 Python 侧日志。

---

## 九 核对边界声明（照 plan.md 节八模板填实）

> 「本核对覆盖：m₂ 属于档位集合 {5（边界校准档，W 取阈值使 v = 1）、10（校准档）、12（主档）、13（第二路覆盖非 'S' 全体）、14（第二路全量）}；参数（δ = 126797/80000，即 log₂3 的严格下界而非真值；W = 2000）；方法为不依赖 (L1) 与顶点引理的全活跃子集穷举，双路精确求解逐子集交叉核对。范围内的判定：可行顶点集恰为 m₂ 个循环旋转（五档全为真，且与解析集逐坐标精确相等）。该范围之外仍属未证：1. m₂ 超出 {5, 10, 12, 13, 14} 的全部情形；2. 一切其他参数取值（含 (P1) 边缘与不满足 (P1) 的区域，以及 δ 取真值 log₂3 的口径）；3. 一般 m₂ 的顶点识别仍只有纸面证明（route-1、route-2、route-5 的既有一手材料），未经形式化；4. 应用档 m₂ = 20、47、91 无独立穷举（组合规模不可达，`learnings.md:45`）；5. 本核对是机器核对，不构成对顶点引理的证明。另登记两条本轮缺口：Python 第二实现对 12、13、14 档仅分片覆盖（3.47%、0.59%、0.26%）；m₂ = 13 档的 'S' 判定未过第二路。」

---

## 十 复跑指引

1. 依赖：macOS（Apple clang）、GMP（`/opt/homebrew`）、pthread；Python 侧为 `20-experiments/.venv/bin/python`（Python 3.12.7、gmpy2、mpmath）。
2. 复跑顺序：编译（3.1 节命令）→ 冒烟（第八节第 2 条，秒级）→ 任一档全量（第八节第 4、5 条；m₂ = 12 约 40 秒起，m₂ = 14 约 8 分钟，视负载）→ `md5 -q` 对照判串 md5 表（第八节第 10 条）→ Python 分片与对拍（第八节第 6、7 条）。
3. 断点说明：本实现不做中途落盘，长跑中断需整档重跑；判定文件与日志在结束时一次性写出。
4. 目录产物清单（`scripts/results/route2/`）：七份判串文件、五份 C 日志、三份计时文件、两份分片映射、七段 Python 切片与日志、`m5_e10_*`、`py_m10_*`；脚本在 `scripts/` 下（`route2_vm_main.c`、`route2_vm_core.c`、`route2_vm_core.h`、`route2_ref_enum.py`、编译产物 `route2_vm_enum`）。
