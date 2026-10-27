# kcross-tail 第 1 轮（收尾轮）方法侦察：第 1 与第 2 节

写作者：方法侦察员。日期：2026 年 10 月 28 日。服务对象：`70-research/tracks/kcross-tail/plan.md` 与疑点的 (a)(b)(c) 三件事。本文件只清点机具与边界，不裁决任何命题，不含新数学结论。

标注约定：1.【本次亲读】＝本次会话打开本机文件并读到该处（附路径与行号）；2.【项目记录】＝仓库文件的转述，其「未证／未核实」标注一律保留；3.【未核实】＝本次没做到。

路径简写（下文一律用简写）：`kp/methods.md` = `70-research/tracks/kcross-proof/cycle-1/methods.md`；`plan.md` = `70-research/tracks/kcross-tail/plan.md`；`barriers.md`、`cycles.md`、`verification.md`、`two-adic.md`、`claims.md` = `10-literature/notes/` 下同名文件（`claims.md` = `claims-2024-2026.md`）；`frontier.md` = `10-literature/frontier.md`；`learnings.md`、`ledger.md` = `70-research/` 下同名文件。抽取文本 `h5_dl.txt`、`sidw144_dl.txt`、`corr_dl.txt` = `/tmp/kcross_extract/` 下 2026 年 10 月 27 日生成件（本会话亲核 md5 依次为 `d134d5822733bb647affacbaebb3b2f5`、`5b21939df73867e59cd15278b742e6f3`、`993f3f5a93188076c60c7357ac552eeb`）。行号可对到仓库副本：`h5_dl.txt` 与 `70-research/tracks/thm23-eps/cycle-1/materials/hercher5.txt` 同 md5、`corr_dl.txt` 与同目录 `corrigendum.txt` 同 md5（本会话 `md5 -q` 实核）；`sidw144_dl.txt` 仓库无副本，其来源为 `https://www.deweger.net/papers/%5B35a%5DSidW-3n+1-v1.44%5B2010%5D.pdf`（若 `/tmp` 被清理，可按此 URL 与 md5 重取）。

## 一、文献机具与可达范围

前注：本轮三个对象（阈值 T 的两侧区间、ε 梯子、438 条清单与不动点）在文献里没有同名物；下面清点的是文献为「同类问题」——把「存在非平凡环」兑换成可核验的整数门槛——用过的机具，逐条给到达与极限。

1. **环方程与线性型初等上界**（Böhm 与 Sontacchi 1978；Simons 与 de Weger 的 Lemma 4 与 Corollary 5）。做什么：把「存在非平凡环」化为 0 < Λ = （K+L）·log 2 − K·log 3 < m/X₀。
   到达：【本次亲读】`sidw144_dl.txt:270` 至 `:271` 逐字「if 91 ≤ m ≤ 515 619 then 7.5311 · 1011 < K < 1.4784 mδ m」；前一档（78 ≤ m ≤ 90）在 `:263` 至 `:269`（1.1173×10¹⁷ < K < 1.3993·m·δ^m）。本疑点的 U(92) 与 L = 7.5311×10¹¹ 全出自此。
   极限：上界以验证界 X₀ 为输入；`1.4784` 背后的连分数计算项目未回一手核（`kp/methods.md:14`）【未核实】。

2. **有效线性型对数下界**（Rhin 1987；一般形式的 Laurent、Mignotte、Nesterenko、Matveev）。到达：【本次亲读】`sidw144_dl.txt:646` 逐字「For our specific case x log 2 + y log 3 however, the result of Rhin [Rh] is best」；与第 1 条相交得 K < K₁(m) 型上界（`cycles.md:67`，转引）。
   极限：整条链唯一的非初等输入；定量上换掉 Rhin 只让上界缩小约 13 倍（`learnings.md:16`）；结构上是一致性缺口——初等连分数分离界逐区间有效，当一致界用等价于额外假设（`30-proof-attempts/diophantine-transcendence/attempt.md:17` 与 `:194`，项目自证，未经第三方复核）；Mathlib 无任何有效线性型对数，去掉后常数约 18、超自身上界约 9 倍（`cycles.md:107`）。

3. **连分数与「区间内最小分母」**（Crandall 1978；Eliahou 1993；Halbeisen 与 Hungerbühler 1997；Simons 与 de Weger 的 Lemma 9、Lemma 10、Corollary 11；Hercher 的 Lemma 22）。到达：【本次亲读】`h5_dl.txt:822` 至 `:825` 逐字给出 γ = [a₀; … , c_k]、c_k = min(a_k, b_k) + 1 的陈述；区间宽度兑换整数门槛的换算（q₂₃ = 137528045312；周期 217976794617 与 355504839929）见 `cycles.md:87` 至 `:90`；门槛表见 `h5_dl.txt:884` 至 `:904`（1.54×10⁹ 档给 8.90×10¹¹，对一切 m 给 7.20×10¹⁰）。
   极限：一、原文只给「不小于」一侧，要成为「最小」还须 γ 落在开区间内（论文未证这一侧，项目用落点余量核验，`kp/methods.md:20`）；二、有理端点退化（项目反例区间（9/8, 827/728），公式给分母 8、真最小分母 15，`kp/methods.md:21` 转引）；三、「区间内最小分母必为端点的收敛或半收敛」的一手定理源项目未定位【未核实】；四、档与档是整数跳变，下一档分母 q₂₃ + q₂₄ = 890638885193 大 6.5 倍（`cycles.md:105`）。

4. **格归约（近似格）**（背景为 de Weger 1989 的 CWI Tract 65）。到达：【本次亲读】`sidw144_dl.txt:922` 至 `:926` 逐字「compute (by the Euclidean, i.e. continued fraction, algorithm) a reduced basis」，二维即高斯约化加暴力枚举；Lemma 18 以 3.2 秒排除 69 ≤ m ≤ 75，76 至 90 只余有限候选（`:937` 至 `:965`）。
   极限：只有二维；搜索点数约（m/X₀）·K₂(m)；对中等 m，Diophantine 逼近技术只能改进上界、不能扩大排除范围（`barriers.md:36` 转引）。

5. **自举（换挡器）**（Hercher 的 Theorem 21 与 Theorem 23，加 2026 年勘误）。到达：【本次亲读】`h5_dl.txt:850` 至 `:860` 逐字：m ≤ 91 无 m 圈；起步 K > 7×10¹¹、X₀ = 695×2⁶⁰、m₂ ≥ 47、ε < 6.9×10⁻³²、K > 5.2×10¹⁵、「And now we can reiterate this process!」；七步链终值 7941964418702608664581 与 SdW 上界在 m ≤ 91 相交（`cycles.md:76`）。Corollary 29：X₀ ≥ 1536×2⁶⁰ 时任何非平凡环含 K > 1.375×10¹¹，门槛来自五周 C++ 计算（`h5_dl.txt:1160` 至 `:1170`）。
   极限：勘误的替换推导无第三方复核（`cycles.md:112`、`frontier.md:166`）；第三方 Lean 只到 m ≤ 82 且不覆盖勘误（`cycles.md:82`）；交叉点由「上界随 m 指数上升、下界每轮多项式推进」两函数形状决定，不靠算力（`cycles.md:108`）；X₀ 门槛每降 2⁶⁰ 计算时间涨约 1.5%，不能合理再压（`h5_dl.txt:1174` 至 `:1184`）。

6. **计算机全区间验证**（Oliveira e Silva 1999；yoyo@home 2017；Barina 2025 的 2⁷¹；Angeltveit 2026 的 2⁷⁵ 估计）。到达：所有小于 2⁷¹ ≈ 2.361×10²¹ 的正整数到达 1（`verification.md:15`）；它是第 5 条 X₀ 输入的来源。
   极限：成本对范围线性、范围指数增长，每翻倍算力约换一位（`verification.md:39`）；2⁶⁸ 以上无独立复现、无机器可检验的验证证书、独立复核成本等于重算（`verification.md:62` 至 `:63`）；服务器按 2⁷² 封顶（`verification.md:41`）；2⁷⁵ 档是仅预印本的条件估计（`cycles.md:92`、`frontier.md:37`）。

7. **密度与计数机具**（Terras 1976 与 Everett 1977；Krasikov 与 Lagarias 2003 的差分不等式加计算机辅助线性规划）。到达：有限停时集合自然密度 1（`barriers.md:43`）；π_a(x) ≥ x^0.84（`barriers.md:44`，已发表记录）。
   极限：密度 1 完全不触及密度零的例外集（`barriers.md:43`）；差不等式每级 k 的最佳指数被该级线性规划锁死，指数收敛于 1 以下（Applegate 与 Lagarias II 自述），λ_k → 2 未证（`barriers.md:46` 至 `:47`）。

8. **严格有理区间算术与超越量单调化归**（经典工具为区间分析，Moore 1966【项目未打开，未核实】；项目三套自足实现）。到达：`70-research/cycle-1/scripts/r4x_rig_helpers.py`（δ 宽 1.796×10⁻²⁴⁴）、`70-research/cycle-2/scripts/route1_rig.py`（δ 宽 7.775×10⁻³⁸⁶）、`70-research/cycle-2/scripts/c2r5_rig.py`（δ 宽 1.2×10⁻⁹⁹ 加两侧夹逼证书）：三个路径本会话 `ls` 实存核，宽度取 `kp/methods.md:28` 的项目记录【项目记录】。
   极限：库实现不是内核检验；2^v 与 (2^v − 1)^δ 这类超越量必须先做单调化归；证书不替代所引引理（同处）。

9. **形式化**（Lean 4 与 Mathlib）。到达：第三方仓库机器验证 m ≤ 82、自报 0 sorry、两条外部假设（`cycles.md:82`）；本机无 Lean 与 Coq（`kp/methods.md:32`）。
   极限：Mathlib 无有效线性型对数（`cycles.md:107`）；Lean 内核漏洞事件后，任何「在 Lean 中通过」必须同时给出内核版本与独立检查器版本（`claims.md:74`、`frontier.md:116`）。

10. **（项目内，非文献）上述机具在本仓库的实现面与可复算边界**。落点：`70-research/tracks/kcross-proof/cycle-1/scripts/` 下 `k1_threshold_cert.py`、`r2_rig.py`、`r2_threshold_cert.py`、`k3_rig.py`、`r4_common.py`、`k3_run_a.py`（本会话 `ls` 实存核）。
    工具陷阱：z3 无 `Pow`；numpy 在 2⁵³ 以上整数不可分辨；gmpy2 有定向舍入；mpmath 的 `mp.dps` 与 `iv.dps` 是两套开关（`kp/methods.md:76` 至 `:84`）。边界：本机无证明助手与 PARI 与 Sage，故一切「严格」结论的等级上限是自足纸面论证加重跑得动的证书（同处）。

## 二、已知的不可能性结果

前注：分三组——2.1 文献定理级（约束方法族或参数族，不约束单个猜想）；2.2 已撤回或被驳斥（供避坑）；2.3 项目内已登记的「必然失败」做法（直接约束本轮 (a)(b)(c)）。凡非定理者逐条标明。

**2.1 文献定理级**

1. **族层面不可判定**：广义 Collatz（按剩余类分段仿射）的判定问题不可判定（Conway 1972）；{g : range(g) = 全体} 是 Π⁰₂ 完备（Kurtz 与 Simon 2007）。出处：`barriers.md:26` 至 `:28`、`frontier.md:30`。界线：只杀「一条统一定理覆盖一大类映射」，不给 3x+1 任何独立性结论。
2. **零测集屏障**：Z 在 Z₂ 中可数、测度零；T₃ 与 T₅ 在 Z₂ 上完全共轭而在整数上行为不同。出处：`barriers.md:50`、`:56`；`two-adic.md:47` 至 `:49`【本次亲读】；`frontier.md:63`。故纯测度或遍历论证、以及对全部奇 a 同时有效的论证必败。
3. **符号与常数不敏感**：负整数有三个非平凡环；5x+1 有环 13 → 33 → 83 → 13。故不区分正负、或不依赖 a = 3 的论证必败。出处：`barriers.md:62` 至 `:63`、`frontier.md:50` 至 `:51`。
4. **无界下降深度**：对每个 k，类 n ≡ −1 (mod 2^k) 前 k 步严格上升；文献侧支持是 Hercher Lemma 8【本次亲读】`h5_dl.txt:207` 至 `:208` 逐字「n ≡ −1 (mod 2^k)，特别地 n ≥ 2^k − 1」。推论：任何「有限个剩余类覆盖 N 加固定步数下降」的证书不存在（`barriers.md:61`，该推论标为笔记作者的推断加本地核验）。界线：允许「归约到已验小数」的更强覆盖形式没有不可能性定理，只记一致性缺口（`barriers.md:178`）。
5. **相对高度无界**：Crandall 1978 定理 (2.2)「sup T_m / m 无界」，故不存在「轨道高度被初始值固定倍数控制」的势函数（`barriers.md:64`，转引；原文本轮未打开）【未核实】。
6. **差不等式框架的级上限**：每级 k 的最佳指数就是该级线性规划的值（Krasikov 与 Lagarias 定理 2.2）；该框架内算力不能替代结构理论（`barriers.md:44` 至 `:47`、`frontier.md:69`）。
7. **「有限验证 → 全称」无桥梁**：任何有限计算都是单称命题的合取；不存在机器可检验的验证证书，独立复核成本等于重算（`verification.md:62` 至 `:64`、`barriers.md:91`）。
8. **超越论侧是常数瓶颈**：整条环排除链唯一非初等输入是 |x·log 2 + y·log 3| 的显式下界；Mathlib 目前没有任何有效线性型对数，去掉后常数约 18、超自身上界约 9 倍（`cycles.md:107`）。

**2.2 已撤回或被驳斥**

9. **解析泛函方程路线**（Opfer 2011）：由作者本人撤回（首页 2011 年 6 月 17 日说明承认「恰好包含每个顶点一次」的推理不完整）。出处：`barriers.md:75`。
10. **「Lean 反证」事件**（CollatzLean，2026）：不是数学结果，是 Lean 内核漏洞的产物（带 phantom 参数的嵌套归纳类型漏检，issue #14576，Lean 4.32.2 修复）。出处：`claims.md:23`、`frontier.md:44`。
11. **印出版 Theorem 21「窗口尾部」那一步不可用**：勘误逐字承认 contains an error（【本次亲读】`corr_dl.txt:14`）；项目另给两条独立缺陷与具体反例（`kp/methods.md:55`）。界线：被证否的是推导，不是结论。
12. **「m ≤ 82 是论文假设下的诚实上限」不成立**：82 是「拒绝勘误、把窗口尾部退回 Remark 7 逐项界」这一种保守修法的天花板（`frontier.md:165` 至 `:167`、`kp/methods.md:54`，二者均转引核查报告 `60-audits/hercher-t21/audit-report.md`，本轮未亲读该报告）。

**2.3 项目内已登记的「必然失败」做法（直接约束本轮三件事）**

13. **网格、大 dps、双实现一致都不能当证明**：网格只作机制检查或反例搜索；「数值观察」不得写成「定理」（`learnings.md:44`、`:29`）。推论：不许用网格或采样支持「T = R」或分岔窗口结论。
14. **用放大的 δ 有理替代做严格性检验，方向写反**：放大只让链约束更容易满足，通过它不蕴含真 δ 情形通过；卡边界必须用 δ 的严格下界（`learnings.md:38`）。
15. **硬编码恒真判据**：判据必须写成能取 False 的形式，标签与判据文本一致，并做扰动检验（`learnings.md:53`）。
16. **混用精确与浮点做包含性判定；19 位以上十进制数经 float 中转**：前者已实测抛 TypeError 或只剩目视支持（`learnings.md:61`）；后者破坏第 20 位（`plan.md:81` 与 `:163`）【项目记录】。
17. **改后脚本不重跑不得沿用旧输出；报告数字必须能 grep 到出处，与日志不符以日志为准**（`learnings.md:54`、`:36` 至 `:37`）。
18. **「未跑完」不得写成结论**：定稿前要么跑完，要么在引用处显式带标记（`learnings.md:62`）。
19. **「根 = 越界阈值」未证**：共享账本明令不得把方程 ε(92,K) = γ − δ 的根的 47 位严格区间写成「K_cross 的 47 位严格定位」（`ledger.md:30`、`:176`，本会话实读）；「补定义桥」仍是待办（`ledger.md:21`、`:185`）。对本轮的推论：「T = R」在裁决前不得当已证引用，两侧论证各自按「已证／未证」分栏。

*本文件只做机具与边界的清点，不含新数学结论；科拉茨猜想仍是开放问题。凡转引项目内文件处，其「未证／未核实／未形式化／未经第三方复核」标注一律保留。*
