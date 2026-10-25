# 第 1 轮方法侦察（第 1 与第 2 节）

写作者：方法侦察员。日期：2026 年 10 月 24 日。本文件只写本轮要求的第 1、2 节，不裁决任何数学结论。
本文件是重写：更早的四节版由本轮的两节替换，其第 3、4 节（本机工具清单与切入点建议）不在本轮要求内（本机工具的实测清单在 `70-research/cycle-1/materials.md` 第三节另有一份同源记录）。
证据标注：`本次亲核`＝本次会话内实际下载、抽取或调用接口并给出定位；`项目笔记`＝本仓库内文件的自述记录（其自身的「未打开」「未核实」标注一律保留）；`未核实`＝本次没有做到。所引外链本次统一实测过可达性（除注明者外返回 HTTP 200）；可达不等于读过正文。
行号以本次核对的版本为准。核查报告 `60-audits/hercher-t21/audit-report.md` 是 2026 年 10 月 24 日的重写定稿，其自身声明全文行号与初版不一致（`audit-report.md:233`），故凡引它一律用本题的现行行号；`results/margin-table.txt` 现为 123 行、md5 `b0a742be9f215f332d0f85750ad57366`（本次实测），旧报告引的 `:81` 至 `:85` 与 `:104` 至 `:105` 已漂移，现行位置见第 1 节第 5 条。

## 一、文献机具与可达范围

按「代数底座、数论工具、组合与凸性、模型与形式化」排列；每条给做什么、到达哪里、卡在哪里。

### 1.1 代数底座与结构约束

1. **环方程（Böhm 与 Sontacchi 1978）**：把「存在非平凡环」化成 `x = c/(2^n − 3^m)` 的整数解问题（`2^n − 3^m` 必须整除 `c`），并给出环内元素界 `|x| < 3^n`。出处：扫描 PDF 本次实测可下载（http 端点返回 200、373,523 字节；https 端点证书告警按项目记录），项目内整理与逐页读图核对见 `10-literature/notes/cycles.md:26` 至 `:40`（含一次指数订正）。
   到达范围：一切后续估计的共同起点；本项目的奇偶向量完备枚举即按此判据实现（`20-experiments/scripts/cycles_bs_enum.c`）。已知极限：只改写问题，不提供任何一致上界；负环一侧连周期下界都无记录（`cycles.md:118`）。

2. **连分数与「区间内最小分母」族（Crandall、Eliahou、Halbeisen 与 Hungerbühler、Simons 与 de Weger、Hercher）**：把「区间宽度」兑换成 `K` 的下界。出处（`本次亲核`）：Halbeisen 与 Hungerbühler 1997 的 PDF 本次下载（`matwbn.icm.edu.pl/ksiazki/aa/aa78/aa7833.pdf`），抽取文本命中 `17 087 915`（第 38、513 行）、`l ≥ 301 994`（第 449 行）与 `p14 = 301 994`、`p16 = 17 087 915`、`p18 = 102 225 496`（第 524 至 525 行）；Hercher Lemma 22 在本次抽取的 `h5.txt:822`；Eliahou 1993 的 17 087 915 另见 UNIGE 记录页（本次实测 200 且正文含该数与 `Discrete mathematics` 字样；论文全文本次未开）；Crandall 1978 本次只测到 DOI 解析到 AMS 后 403（反爬），全文未开，其连分数引理经 `cycles.md:46` 转述。
   到达范围：现行门槛 `q_23 = 137,528,045,312`、周期记录与 Hercher 七步自举的每一档全部出自这一机具。已知极限：档与档之间是整数跳变，跨档必须让区间更窄；下一档分母 `q_23 + q_24 = 890,638,885,193` 需验证界到 2^75 量级（`cycles.md:105` 至 `:106`）。

3. **有效线性型对数（Steiner 用 Baker；对 `x log 2 + y log 3` 用 Rhin 1987；一般形式用 Laurent、Mignotte、Nesterenko 与 Matveev）**：给 `Λ = (K+L)log 2 − K log 3` 的显式正下界。出处（`本次亲核`）：Simons 与 de Weger v1.44 抽取文本第 644 至 646 行逐字「For our specific case x log 2 + y log 3 however, the result of Rhin [Rh] is best」，一般形式的工具谱系同段（第 213 行给出链条中的用法）；Steiner 的 1 圈结果与其「方法强、结论弱」评语经 `barriers.md:32` 转引（原文本次未开）。
   到达范围：整条链唯一的非初等输入，与初等指数上界相交得到 `K < K₁(m)` 型上界。已知极限：定量瓶颈；换掉 Rhin 只让上界缩小约 13 倍（`70-research/learnings.md:16`，转述 `30-proof-attempts/diophantine-transcendence/attempt.md`）。

4. **二维格归约（近似格）**：把 Diophantine 逼近的候选逐个清掉。出处（`本次亲核`）：Simons 与 de Weger v1.44 第 875 至 931 行（`approximation lattice`、约化基、待搜点数约 `K₂(m)`）；项目整理见 `cycles.md:68`（含一处书写订正）。
   到达范围：`69 ≤ m ≤ 90` 的全部候选在 7 秒内排除。已知极限：只是二维高斯约化（LLL 在二维的特例），逐 `m` 使用，参数依赖 `X₀` 与 `K₂(m)`，不能一次覆盖所有 `m`。

5. **自举交叉（Hercher Theorem 21 与 23）**：用当前 `K` 下界算偏差 `ε`，经最小分母换回更好的 `K` 下界，反复迭代直到与 Simons 与 de Weger 的上界 `1.4784·m·δ^m` 相交。出处（`本次亲核`）：论文与勘误本次下载且 md5 与项目记录一致（`3e2377bef0b1c0435dc455c9bbee43a1`、`f23d5f969116cb1af6e9b981b4b3ba7a`）；`h5.txt:165`（Corollary 29：`X₀ ≥ 1536·2^60 = 3·2^69`）、`:695`（Theorem 21 陈述）、`:850`（「There is no m-cycle with m ≤ 91」）。
   到达范围：`m ≤ 91` 与七步链（终值 `7941964418702608664581`）。定量产物在 `margin-table.txt`：`m = 91` 与 `92` 至 `95` 的判定在现行第 89 至 93 行，[4] 自检在现行第 111 至 112 行（表 123 行，`本次实测`；`audit-report.md:208` 记录重跑自检 8 / 8）。已知极限：上界随 `m` 指数上升、下界逐轮推进，交叉点由两个函数的形状决定而非算力；`m = 92` 起不能排除（`rederivation-erratum.md:325` 至 `:329`）。

6. **验证界输入**：任何环元素都必须大于已数值验证到的范围。出处（`本次亲核`）：Barina 2025 的 PDF 本次下载，第 582 行给出「355 504 839 929」；Angeltveit 2026 预印本本次下载，第 75 至 77 行给出「A more modest goal might be to verify convergence for all n < 2^75」与条件估计「at least 2 302 268 119 908」。
   到达范围：`2^71` 记录已覆盖 Hercher 的 `3·2^69` 门槛。已知极限：有限验证是单称命题的合取，无已知桥梁通向全称（`barriers.md:91`）；下一档需 2^75 级验证（`cycles.md:106`）。

### 1.2 组合与凸性

7. **鸽笼窗口与局部极小值记账（Simons 与 de Weger 的 m 圈框架；Hercher 第 13 页的鸽笼步）**：把 `K` 的总量分配到一段连续窗口，得 `Σk ≥ (m₂/m)·K`。出处（`本次亲核`）：`h5.txt:740` 至 `:744`（「There are m₂ consecutive local minima which are directly followed by at least (m₂/m)·K o-steps」）。
   到达范围：窗口的 o 步**总量**，是自举第一步与本次收口对象的起点。已知极限：只给总量、不给逐项下界；窗口后段元素的唯一可用信息是 Lemma 20 的上界 `n_{i+1} < n_i^δ`（`h5.txt:674`），第三方与本项目一致判「不可局部修复」（`audit-report.md:83`、`rederivation-erratum.md:370`）。

8. **凸性加多面体顶点极值（2026 勘误的替代论证）**：目标 `S(x) = Σ 3/(2^{x_i} − 1)` 在链式约束与和约束决定的多面体上「attains its maximum value at a vertex」。出处（`本次亲核`）：勘误 PDF 本次下载，顶点句在抽取文本第 43 至 46 行，活跃约束计数在第 54 至 59 行，顶点坐标在第 64 行起；一般形式「凸且连续函数在紧凸集上取最大值于极点」见「Bauer maximum principle」条目（本次经 Wikipedia API 抓到正文；百科级来源，非文献定理源）。
   到达范围：聚合尾界 `3/(2^v − 1) + 3(m₂ − 1)/(2^v − 1)^δ`，本项目复现七个自举值（`margin-table.txt` 现行第 89 至 93 行与第 111 至 112 行）。已知极限：勘误未经同行评审且原文三处不自足（`audit-report.md:165` 至 `:169`），其中顶点一步需要的紧性在原文未加论证（该多面体无界，故 Bauer 型定理不能直接代入）；另有两个第三方替代：Jensen 型显式凸组合（`materials-thirdparty.md:105`）与条件性 `m ≤ 101`（同文件 `:152`），本次均未编译。另有一份自称 `m ≤ 95` 的 Zenodo 稿（`materials-thirdparty.md:187`）与一篇找不到出处的 96 环论文（`audit-report.md:223`），本次均未核实。

9. **差不等式与线性规划族（Krasikov 与 Lagarias 2003；Applegate 与 Lagarias 1995）**：用 `mod 3^k` 的差分不等式加计算机辅助线性规划给密度界。出处（`本次亲核`）：Krasikov 与 Lagarias 的 arXiv PDF 本次下载，第 89 行 `π₁(x) > x^0.84`、Theorem 2.2 在第 263 与 910 行；Applegate 与 Lagarias II 的 PDF 本次下载，第 671 行「It seems evident that the exponents γ are converging to a limit below 1」。
   到达范围：`0.84`（保守措辞），另有 `81 ≤ m ≤ 90` 段的上界系数 `1.3993` 出自 Simons 与 de Weger v1.44（第 265 行，`本次亲核`）。已知极限：每级 `k` 的最佳指数被同文 Theorem 2.2 锁死，框架内算力无效；`λ_k → 2` 是未证的 Krasikov 猜想（`barriers.md:46` 至 `:47`、`frontier.md:86`）。

10. **密度与遍历机具（Terras 与 Everett、Korec、Tao）**：给「几乎所有」型结论。出处（`本次亲核`）：Tao 论文 PDF 本次下载，摘要第 22 行含「of logarithmic density」，自限句在第 122 至 123 行。
    到达范围：Tao 的对数密度版「几乎有界」，Korec 的 `θ > log₄3`（`frontier.md:17`）。已知极限：一切密度型结果碰不到零密度例外集；Tao 自述固定常数版「超出本文方法的范围」（同处）。

11. **2 进共轭与动力学（Bernstein 与 Lagarias 1996；Kontorovich 与 Lagarias）**：把加速映射共轭到 2 进移位。出处（`本次亲核`）：Bernstein 与 Lagarias 的 PDF 本次下载，第 138 行逐字「We remark that the results we prove are not related to the 3x + 1 Conjecture」、第 169 行「`Φ` 与 `Φ⁻¹` 在 `Z₂` 上处处不可微」；Kontorovich 与 Lagarias 的 arXiv:0910.1944 本次经 arXiv API 核到标题「Stochastic Models for the 3x+1 and 5x+1 Problems」（文集章节状态见 `frontier.md:33`）。
    到达范围：`Z₂` 侧动力学完全解决（遍历、强混合、Bernoulli）。已知极限：不能武器化，共轭只联系同次迭代且 `Q(x)` 无有效算法（`barriers.md:55`、`:72`）。

### 1.3 模型与形式化

12. **形式化机具（Lean 4 加 Mathlib）**：把已发表证明搬进内核。出处（`本次亲核`）：`PhilNorfleet/Hercher2023_lean` 的 SUMMARY 本次抓取，第 13 至 17 行与第 99 至 119 行（机器验证的定理是 `m ≤ 82`，自称 0 sorry、两条外部假设，路径绕开 Theorem 21 的尾部）；另两个仓库见 `materials-thirdparty.md:13` 与 `:121` 至 `:154`。
    到达范围：`m ≤ 82`（不含勘误）与条件性 `m ≤ 101`。已知极限：本机无 Lean 等工具链（`70-research/plan.md:112`），一切形式化宣称本次只作源文件文本证据；Mathlib 无有效线性型对数（`10-literature/notes/cycles.md:107` 转引第三方自述，本次未一手核实）。

13. **本项目自建机具（可复用资产）**：奇偶向量完备枚举到 `k ≤ 34`（3.44×10^10 个向量）；`40-formal/exact_check.py` 精确算术闸门（`70-research/ledger.md:14`：退出码 0、18 处 PASS）；`margin_table.py` 定量闸门（现行表重跑与自检记录见 `audit-report.md:208`；旧版 `materials.md:137` 记录过一次 0.878 秒、逐字节一致）。已知极限：都在给定界内，`README.md:40` 自述该闸门打印「有限范围，不是证明」。

## 二、已知的不可能性结果

按证据强度分三组：已证定理（约束方法族，不约束原猜想本身）、记录级天花板（有原文自述或本项目论证，但不是定理）、已撤回或被否证的具体路线。凡非定理者逐条标明。

### 2.1 已证定理级

1. **统一算法与统一定理不存在（Conway 1972）**：广义 Collatz（按剩余类分段仿射）的判定问题不可判定。出处（`本次亲核`）：PDF 本次下载（gwern 重印影印本，OCR 文字层可检索，命中「undecidable」两处）；出处与摘要句经 Lagarias 注释书目本次下载逐字核对（`lagbib.txt:1121` 至 `:1127`：「shows that a more general function iteration problem similar in form to the 3x + 1 problem is computationally undecidable」）。
   界线：只杀「用一条统一定理覆盖一大类映射」，不给出 3x + 1 本身的任何独立性或不可判定性（`10-literature/notes/undecidability.md:14` 至 `:16`）。

2. **Π⁰₂ 完备（Kurtz 与 Simon 2007）**：`{g : range(g) = ω}` 是 Π⁰₂ 完备的。出处（`本次亲核`）：作者主页 PDF 本次下载，第 68 行 Theorem 1.4、第 75 行 Theorem 1.5。界线同上；另注意 Conway 式编码只控制 2 的幂输入，不足以给出「对所有 x」的不可判定（同文记录，`undecidability.md:21`）。

3. **差不等式框架的级上限（Krasikov 与 Lagarias 2003 定理 2.2）**：每级 `k` 的最佳指数就是该级线性规划的值。出处（`本次亲核`）：arXiv PDF 本次下载，第 263 行（定理陈述）与第 910 行（证明入口）。推论：该框架内增大算力不能改变前沿（`barriers.md:47`）。

4. **轨道相对高度无一致上界（Crandall 1978 定理 (2.2)）**：`sup T_m / m` 无界。出处：本次 AMS DOI 解析返回 403（`本次实测`），全文未开；结论经 `barriers.md:33` 与 `:64` 转引（该笔记自述经文本代理读过全文）。界线：任何「轨道高度被初始值固定倍数控制」的势函数路线不成立。

5. **符号与常数敏感性（两个已证事实）**：负整数上有三个非平凡环；`5x + 1` 有环 `13 → 33 → 83 → 13`。出处：Lagarias 1985 年综述节点页本次抓取，含「there are other cycles if negative integers are」句（`barriers.md:25` 含本项目自验）；`5x + 1` 的环见 `barriers.md:26`（含本项目自验），Lagarias 书目本次亲核第 2824 行记录 `n = 13`。界线：任何不区分正负、或不依赖于 `a = 3` 的论证必败；且 3x + 1 与 5x + 1 在 `Z₂` 上完全共轭（`frontier.md:47`）。

6. **纯测度与遍历论证必败**：`Z` 在 `Z₂` 中可数、测度零，遍历论的一般性质对整数上的迭代得不出结论。出处：`barriers.md:56`（Lagarias 2010 综述原句）；同文预印本本次下载，第 747 行读到「unapproachable」句。界线：跨越需要把 `Z` 的算术结构与被 `Φ` 打散的符号动力学相联的新桥梁（`frontier.md:115`）。

7. **发散轨道与极长循环现无机制**：Lagarias 2010 预印本本次下载，第 987 至 990 行逐字：「the fundamental difficulty of proving in effect that the iterations actually do have an explicit pseudo-random property」；以及排除极长循环「seems unapproachable at present by known methods of number theory」。标注：这是原文的表述，不是定理。

### 2.2 记录级天花板（有自述或项目论证，不是定理）

8. **m 圈方法的天花板**：Simons 与 de Weger 自述（`本次亲核`，v1.44 第 1003 行「an entirely new idea seems to be needed」，第 988 行「no new ideas emerge」）。配合：一次性排除所有 `m` 无已知机制，全部排除都以验证界为输入（`cycles.md:122`、`frontier.md:70`）。

9. **「有限验证通向全称」无桥梁**：任何有限计算都是单称命题的合取；算力每翻倍约换一位（`barriers.md:91`、`frontier.md:53`）。

10. **「几乎所有」到「所有」无桥梁**：Tao 自述固定常数版「likely to be almost as hard to settle as the full Collatz conjecture, and out of reach of the methods of this paper」（`tao.txt:122` 至 `:123`，`本次亲核`）；`barriers.md:109` 与 `:121`。

11. **两处明确的缺口（不得写成已排除）**：允许「归约到已验小数」的更一般覆盖同余、以及自动机路线，都没有不可能性定理；只能以「缺一致性定理」形式记录（`barriers.md:69`、`:74`）。另有本项目对「固定下降深度证书」的排除，其论证是笔记作者的推断（`n ≡ −1 (mod 2^k)` 前 `k` 步只升，文献侧支持为 Hercher Lemma 8，`h5.txt:207`，`本次亲核`），且不覆盖更强的覆盖形式（`barriers.md:24`、`:61`）。

### 2.3 已撤回或被否证的具体路线

12. **Opfer 2011 的解析泛函方程路线**：作者本人于 2011 年 6 月 17 日附页撤回「科拉茨猜想为真」的陈述。出处（`本次亲核`）：预印本 PDF 本次下载，首页第 25 至 26 行「has turned out to be incomplete … has to be withdrawn」。

13. **Metzger 的「唯一循环」定理**：证明有缺口。出处（`本次亲核`）：Lagarias 注释书目本次下载，第 2821 行是 1995 年条，第 2876 行对 1999 年的修补稿写「However the proof of this result still has a gap」。

14. **印出版 Hercher 定理 21 的「窗口尾部」推导**：被本项目证否，含两条独立缺陷（幂不等式 `n^{(δ^ℓ)} ≤ n^δ` 对 `ℓ ≥ 2` 方向相反；`T(n) < 3/n` 关于 `n` 递减，故由 `n` 的上界只能得 `T` 的下界）。出处：`audit-report.md:148`（假不等式的显式反例，`本次未重跑该报告脚本`）、第三方两条指控逐字见 `audit-report.md:83`。界线：被否证的是**推导**，不是逐项命题本身（环不存在，无从检验；`rederivation-erratum.md:70` 的措辞更正）。

15. **第三方「`m ≤ 82` 是论文假设下的诚实上限」**：不成立；82 是「把尾部退回 Remark 7 的逐项界」这一种修法的天花板，同一假设集下勘误的聚合尾界严格更强（`audit-report.md:175`、`rederivation-erratum.md:374`）。并列须报的事实：82 相对 83 是系数敏感的刀刃值（`audit-report.md:179` 至 `:182`）。

16. **形式化侧的两条失败记录**：其一，2026 年的 Lean「反证」事件是内核漏洞（带 phantom 参数的嵌套归纳类型漏检，issue #14576）的产物，不是数学结果（`frontier.md:44`、`:116`，`本次未一手核实`）；其二，去掉有效线性型对数后的形式化常数约 18、超其自身上界约 9 倍（`cycles.md:107` 转引第三方自述，`本次未一手核实`）。

*本文件只做机具与边界的清点，不含新数学结论；科拉茨猜想仍是开放问题。文中的「本次亲核」只保证在本次会话内下载、抽取或调用并给出了定位，不构成对这些文献自身正确性的复核。*

## 三、本机工具：能做什么、不能做什么

本节每条都是本次实测（命令与结果照录，未跑的一律写「本次未跑」）；所指的「这类问题」是本轮四处收口：顶点引理与闭化、读法唯一性、`m = 92` 的覆盖性、定量后果。

### 3.1 实测清单

1. **解释器与库**（命令：`20-experiments/.venv/bin/python -c ...` 逐个执行）：Python 3.12.7；mpmath 1.3.0；gmpy2 2.3.2；sympy 1.14.0；numpy 2.5.4；z3 5.3.1。与 `20-experiments/ENV.md:31` 至 `:40` 的登记一致。
2. **δ 的 60 位复算**（mpmath，`mp.dps = 60`）：`1.58496250072115618145373894394781650875981440769248106045575`，其 40 位前缀与核查报告钉住的 `1.58496250072115618145373894394781650876`（`audit-report.md:312`）逐位一致。
3. **精确有理数与锚点**（gmpy2.mpq）：`mpq(7941964418702608664581, 214072842063828923281)` 返回精确分数 `7941964418702608664581/214072842063828923281`（十进制即 `37.09935525747164`），与 `margin-table.txt` 现行第 89 行与第 112 行的钉住值一致。
4. **符号微分**（sympy）：`3/(2**x − 1)` 的二阶导实测给出 `3*2**x*(2**x + 1)*log(2)**2/(2**x − 1)**3`（对 `x > 0` 分子分母同号，可读为正）。
5. **z3 的边界**（本次实测）：线性有理算术精确（`a+b ≥ 3 ∧ a ≤ 1 ∧ b ≤ 2 ∧ a+b > 5` 返回 `unsat`）；多项式实数算术精确（`x²+x+1 = 0` 返回 `unsat`）；超越量不可用（`z3.Pow` 在 5.3.1 的 Python API 里不存在，报 `AttributeError`；改用 `2**c == 3` 编码返回 `unknown`）。故含 `2^{x_i}` 的目标函数不能直接丢给 z3。
6. **C 与 GMP**（本次实测）：`cc`、`clang`、`gcc` 都存在（`cc --version` 首行 `Apple clang version 21.0.0 (clang-2100.3.34.2)`）；`/opt/homebrew/include/gmp.h` 与 `libgmp.a` 在机（Homebrew gmp 6.3.0 的符号链接）；本次用 `cc -O3 -I/opt/homebrew/include -L/opt/homebrew/lib gmptest.c -lgmp` 编译并运行了一个算 `3^100 + 1` 的小程序，成功（输出以 `5153775207320113310364611297656212727021` 开头）。
7. **缺席的整条工具链**（命令：`command -v lean lake coqtop coqc gp pari sage`，实测零输出）：无证明助手、无 PARI 与 Sage。后果：不能承诺任何机器检验的严格性；不能用 `lindep`、`qflll`、`contfrac` 等现成例程，连分数与格归约须自写（项目与三份重推脚本正是自写的）。
8. **浮点**（numpy）：无严格算术。实测 `np.float64(2**53 + 1) == 2**53` 为 `True`，即 2^53 以上的整数已不可分辨；它只能当找反例的探针，不能当证据。

### 3.2 逐工具的能与不能（对本轮四类子任务）

1. **高精度实数比较**：mpmath 能做，但只在数值意义下；`mpmath.iv` 可给出带方向的界（库级区间算术，不是机器检验）。要把某条不等式写成「已证」，出路是解析论证（如 `φ` 的分段单调性），不是加大 `dps`。
2. **精确整数与有理数**：gmpy2 与标准库 `fractions` 是主力；`q_min`、整数门槛、余量、顶点枚举的精确比较都零误差。不能处理 `2^x`、`log` 这类超越量；凡目标含 `2^{x_i}` 的比较，只能有理逼近加区间，或退回解析。
3. **符号运算**：sympy 能把引理的代数骨架写正确（化简、求导、解闭化后的线性方程组与顶点方程），不能判定含超越常数的命题。
4. **SMT**：z3 只在线性片段与多项式实数片段可用；可用它做线性可行性与顶点枚举（精确），不可用它处理目标函数。
5. **批量浮点**：只能做采样与统计（见 3.1 第 8 条）。
6. **C**：适合「大规模、确定性、只需整数或定点」的扫描；本机没有 C 的区间算术库，实数不等式若要严格界必须自实现向外舍入。
7. **一句话总括**：顶点引理与闭化（精确有理数加线性代数加解析推理）、`m = 92` 的覆盖性（高精度 `Ψ` 求值）本机够用；读法唯一性要的是网络与原文，不是计算；定量后果有现成闸门；不够用的是任何需要机器检验的严格性。

### 3.3 本次未跑

1. 三份重推脚本、`rederive-erratum.py` 全链、`40-formal/exact_check.py`、`margin_table.py` 与任何 Lean 编译本次均未跑；形式化与定量闸门的结论只引用项目内的执行记录（`audit-report.md:208` 的 8 / 8 自检、`materials.md:137` 的 0.878 秒）。
2. 旧版 `methods.md` 里「Ψ 单点约 2.4 毫秒、120 点 0.29 秒」的探测记录在本轮重写后无仓库内留存（本次 grep「毫秒」「0.29 秒」在 `60-audits/hercher-t21/*.md`、`70-research/*.md`、`70-research/cycle-1/*.md` 零命中），故本节不引用该数。

## 四、本轮最可能产生增量的两个切入点

1. **把「顶点取到性 + 闭化无损」写成一条自足的初等引理，并用精确有理数做顶点枚举核对**。做法：显式写出闭化后的约束组（`x_i ≥ 1`、窗口内 `x_{i+1} ≤ δx_i`、回绕 `x_{m−m₂+1} ≤ δx_m`、`Σx ≥ W`）与目标 `S`，逐条给出可行集非空、某水平集有界故紧、凸函数在紧凸集上取到极点（按第 1 节第 8 条的 Bauer 型事实）、顶点识别只用「哪几个约束取等」；再对链上真实参数（`m₂ = 47、67、82、91` 与对应 `W`，`rederivation-erratum.md:178` 至 `:181`；另见 `plan.md:63` 的 `m₂ = 2、3、5、10、47、91` 清单）用 `gmpy2` 或 `fractions` 精确枚举，阈值取 0。
   **一句理由**：第 1 与第 4 子问题共用同一个几何对象，一次写好两处一起收口，且不需要新的数论输入；证不出来也是可交付的否证。
2. **把 `m = 92` 的覆盖性换成合法区间上的有限区间覆盖**。做法：每个盒子 `[K₁, K₂]` 取在 `K₁` 处可行的 `m₂`，由「固定 `m₂` 时 `ε` 关于 `K` 递减、`q_min` 关于 `ε` 非增」给出盒子上 `Ψ(K)` 的上界（不依赖 `Ψ` 自身的非降性），再用 `mpmath.iv` 逐盒核对；越界就给出越界的 `K`，并按纪律把 `m = 92` 的「不排除」依据从「`Ψ` 非降（未证）加 11 点网格」（`rederivation-erratum.md:334` 至 `:339`）换成本清单。
   **一句理由**：把未证的全称命题换成有限、可逐盒核验的清单，且逐盒上界只用单调性，连 `Ψ` 的非降性都不需要。
