# collatz-attack：科拉茨猜想（3x+1）攻坚

**English:** An AI-produced, machine-verified attack on the Collatz conjecture (3x+1). **No proof is claimed** — the conjecture remains open. This repository delivers (1) a literature frontier map with every claim traced back to primary sources, (2) six computational experiments whose key numbers were each recomputed by an independent re-implementation, (3) six genuine proof attempts, each reduced to a precise failure point after adversarial review, and (4) a machine-checked set of elementary lemmas plus quantitative negative results. Everything runs on a laptop.

> **本仓库没有证明科拉茨猜想。** 它是 1937 年至今的开放问题，且有广义版本不可判定等结构性障碍。这里交付的是：已知边界的清单、可复核的局部结果、以及六条候选证明路线逐条的精确失败点。

---

## 一、这是什么

一次把「尝试证明科拉茨猜想」当作工程项目来做的结果。它不宣称任何突破，它宣称的是另一件事：**这里的每个数字都至少有两套独立实现，每条文献主张都回到了原始来源，每条路线的失败都被定位到了具体的不等式或具体的步骤。**

全部文档与代码由 AI 代理生成（署名与过程详见 [PROVENANCE.md](PROVENANCE.md)），未经同行评审。

## 二、硬数字（全部经换实现独立重算）

1. **n 不超过 2^28（268,435,456）全部归于 1**，耗时 5.2 秒；纪录保持者 63 条与 OEIS A006877 逐条零不符，总停时前 10000 项与 A006577 零不符。最大总停时 956，在 n 等于 226,588,897。
2. **周期不超过 34 不存在非平凡正环**（完备枚举长度 1 至 34 的全部 2^k 个奇偶向量，叶子 3.44×10^10 个，70.2 秒；负整数上三个已知环被同一套判据精确回收作阳性对照）。
3. **自算验证界 10^12**（正负两侧各约 1.5 小时，两种独立实现互证）。在此前提下、且环上元素绝对值至少 10^12 时，**正环周期至少 17,087,915**，与 Eliahou 1993 同一台阶，而所需验证界低约 10.45%。所有排除上界七档经第二套算法（整数定点）复核全对。
4. **按位加权势函数类不存在**（含 a·x + b·popcount(x) 与其一般按位形式）：对任意 N ≥ 4 在 [3, N] 上都不存在满足每步至少降 1 的函数，附初等证明，并在每个二进位尺度上重现。更进一步：**任何非空不变域上都不存在良基严格下降势函数**。
5. **Terras 系数停时猜想（1976，至今未解）在 n 不超过 2^30 无例外**；本项目用另一套实现独立复核到 2^22，零反例，且空层集与首降向量计数表 A(k) 的零项互相吻合。
6. **逆向树路线被定量判死**：显式建树到深度 66（4.73 亿节点）只能完整覆盖奇数到 **n 等于 25**；覆盖到 1000 需深度 113（约 8.8×10^13 节点）。增长常数 0.6713 在深度 40 至 66 稳定到万分之一。
7. **若干定量负结果**：Krasikov 与 Lagarias 的 x^0.84 型下界在 x 等于 2^24 处只覆盖 7.19%，推到 99% 需指数不小于 0.9994；Tao 型逐层正上界既不归零也不可相加；「有限覆盖 + 固定步数下降」这一类证书形式被 n 同余 −1 模 2^k 的一整类数排除。

## 三、六条路线各自的落点

| 路线 | 结局 | 最致命的一击 |
|---|---|---|
| arithmetic-cycles 算术路线 | 未证明，四条局部引理 | 负侧「同型事实」为假（实跑反例），且 U(m) 随 m 指数增长而 L(m) 只由验证界决定，固定 X0 必有交叉点之后夹逼失效 |
| tao-quantitative 量化改进 | 未证明，五条局部结论 | 逐层正上界 Λ(A_C) ≤ K(log C)^(−c) 对每个固定阈值都是正常数，框架内任何常数级改进都不使它归零 |
| two-adic-control 2 进控制 | 未证明，六条局部引理 | 主定理等价于「3x+b 在 Z 上无发散轨道」整族命题，换坐标不降难度；共轭在算术上不透明 |
| minimal-counterexample 最小反例 | 未证明，五条局部引理 | 它自称缺失的「新结构定理」已存在（Rozier 与 Terracol 2026，同行评审），该文献整覆盖并超越其缺口 |
| formal-automata 形式化 | 未证明，三条结构/不可能性结果 | 受限版本这一层与猜想真值相反（反例 −1 与 4/5）；任何「并集非自动」型不可能性定理都会顺手证否猜想 |
| diophantine-transcendence 丢番图 | 未证明，五条局部结论 | 头号数字 m ≤ 91 全部压在 Hercher 定理 21 的「几何尾部」一步上，而该步公开有争议（zbMATH 审稿人指出潜在缺陷、第三方 Lean 只接受 m ≤ 82） |

六条路线全部经过独立反驳者的攻击（只接受两种证据：可运行的反例，或打开的原始来源），两条另加第二轮首席反驳，全部由作者逐条回应。

## 四、机器可复核的部分

1. **精确算术闸门**：`40-formal/exact_check.py`，用 Fraction 与 gmpy2 逐条验证初等引理，**退出码 0 表示全部通过**；18 处 PASS 与 4 条顶层引理。它自己打印「有限范围，不是证明」。
2. **Lean 4 源码**：`40-formal/lean/CollatzBasic.lean`（51 条声明）。**未经编译器检验**——本机没有 Lean 工具链，这一点写在文件头部的「未编译声明（必读）」里，安装脚本在 `40-formal/setup-lean.sh`。
3. **主代理的五轮独立验算**：`40-formal/independent-checks/`。对象分别是连分数载荷常数与两个周期下界、屏障机制与指数换算、环判据排除上界（七档）、逆向树的层结构与覆盖上界、Terras 系数停时猜想与 A(k) 表。每一轮都留了脚本与记录，含**我自己一次把定义写错、凭空造出 209 万个「反例」**的完整复盘。

## 五、复现

```bash
# 1. 重建环境（仓库不含 venv）
python3 -m venv 20-experiments/.venv
20-experiments/.venv/bin/pip install numpy sympy z3-solver gmpy2 python-flint

# 2. 确定性闸门（退出码 0 = 全部通过）
20-experiments/.venv/bin/python 40-formal/exact_check.py; echo "exit=$?"

# 3. 最小检查清单（环实验）
cd 20-experiments
.venv/bin/python scripts/cycles_bs_formula_check.py
.venv/bin/python scripts/cycles_solutions_verify.py results/cycles_enum_exhaustive_k34.txt
./.venv/bin/python scripts/cycles_criterion.py 1000000 100000000

# 4. 我自己的独立验算
.venv/bin/python ../40-formal/independent-checks/q23_convergents.py
.venv/bin/python ../40-formal/independent-checks/criterion_exclusion_recheck.py
.venv/bin/python ../40-formal/independent-checks/reverse_tree_recheck.py
.venv/bin/python ../40-formal/independent-checks/terras_tau_chi_recheck.py
```

C 程序用 `cc -O3` 编译（源码在同目录，编译产物未入库）。总报告 `50-report/final-report.md` 里每条关键数字都附了完整命令行。交互式边界图 `50-report/frontier-map.html` 是单文件、无外部依赖，直接双击可开。

## 六、目录结构

1. `00-scope/`：问题陈述、成功标准、技能盘点。
2. `10-literature/`：八份文献笔记（每条主张附原始来源与可信度标注）、`frontier.md` 边界地图（14 条已确证、10 个活口、10 条死路、13 条门槛）。
3. `20-experiments/`：六组实验的脚本、原始输出、结论，以及「这个实验不能证明什么」的逐条声明。
4. `30-proof-attempts/`：六条路线的尝试、反驳、作者回应与第二轮备忘录。
5. `40-formal/`：精确算术闸门、Lean 源码与安装脚本、五轮独立验算记录。
6. `50-report/`：总报告（493 行）与可交互边界图。
7. `workflow.ts`：驱动全部产物的八步动态工作流脚本（Typescript，ZCode dynamic-workflows）。

## 七、AI 署名与产出说明

本仓库的全部内容由 AI 代理生成：用户设定任务与验收标准，AI 承担设计、编码、执行、复核与写作。两段运行合计 **105 个子代理会话、约 12 亿 token、约 1 天 22 小时**，运行记录与模型信息见 [PROVENANCE.md](PROVENANCE.md)。

请把这份仓库当作「一份由机器生成、但每个数字都可复算的技术报告」，而不是论文。

## 八、诚实边界

1. **没有证明科拉茨猜想**，也没有推翻它。六条路线全部未成功。
2. **未经同行评审**；全部内容为 AI 产出。
3. **一条结论依赖有争议的引理**：m ≤ 91 那一档压在 Hercher 定理 21 上；若该步不被接受，结论跌到 m ≤ 82（首席反驳者已用「健全」版本复现出 82）。
4. **Lean 源码未经编译器检验**（本机无工具链）。
5. **文献数字多为转引或本项目阅读结论**，引用前请回原始来源；`frontier.md` 里凡「转引」「未打开原文」「仅预印本」之处一律保留了标注。
6. **排序与「活口」判断是 AI 的判断**，不是文献结论。
7. **脚本内含作者本机绝对路径**（形如 `/Users/luna/Documents/math IA/...`），复现时请替换为你自己的路径。

## 九、许可

MIT，见 [LICENSE](LICENSE)。数学主张不提供任何担保。
