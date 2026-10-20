# tao-almost-all

研究线：Tao 2019 年「几乎所有轨道取到几乎有界值」及其 2020 年至今的后续。
核对时间：2026 年 10 月 18 日。所有「已核对」字样都指：我在本次任务中亲自打开了来源（见文末来源清单）。

## 这条线在问什么

设 Col 为 3x+1 映射，Col_min(N) 为轨道的最小元素。猜想说 Col_min(N) = 1 对所有 N 成立。
密度型弱化结果问的是：对「几乎所有」N，Col_min(N) 能被压到多低？

1. Terras 与 Everett：Col_min(N) < N 对自然密度 1 的 N 成立。
2. Allouche、Korec：把 N 降为 N^θ，θ 逐步降到 log3/log4 ≈ 0.7924。
3. Tao 2019：把「幂指数 θ」换成「任意发散函数 f(N)」，代价是密度从自然密度退到对数密度。这就是「几乎有界」。
4. 本线要钉死的是：Tao 定理的确切量词与密度语义、它依赖的定量引理、以及「几乎有界」再往前走一步到「有界」（存在固定常数 C_0 使 Col_min(N) ≤ C_0 对几乎所有 N）到底缺什么。

## 关键结果

### 一、Tao 之前（按 Tao 论文的表述转述，原文未逐篇打开）

1. Col_min(N) < N 对自然密度 1 的 N 成立 —— 1976 年，Terras（Acta Arith. 30, 241 至 252）；1977 年 Everett 独立得到。出处：https://arxiv.org/abs/1909.03562 （Tao 论文正文与参考文献 [21]、[8]；另见 Assani、Ebbighausen 的转述，https://arxiv.org/abs/2310.08749 ）。我未打开 Terras 与 Everett 原文。
2. Col_min(N) < N^θ 对几乎所有的 N 成立，阈值按来源印刷式作 θ > 3/2 − (log 3)/(log 2) ≈ 0.869 —— 1979 年，Allouche（Séminaire de Théorie des Nombres, Exp. No. 9，共 15 页，法语）。出处：https://arxiv.org/abs/1909.03562 （该处即 Tao 论文参考文献 [1] 的引用位置）。
   该阈值我做了三重核对：(a) 取 arXiv 源码 https://arxiv.org/e-print/1909.03562 解包，collatz.tex 第 165 行逐字写作 $\theta>\frac{3}{2} - \frac{\log 3}{\log 2} \approx 0.869$；(b) 用 pdftotext -bbox 取 arXiv v7 第 2 页词框，「3」的 yMin = 445.01 高于「2」的 yMin = 453.84（PDF 坐标向下增），即第一个分数的分子是 3；(c) 用 pdftoppm 把 arXiv v7 与出版版 PDF 的第 2 页各渲染到 600 dpi、裁剪放大后目视，两版同样印作 3/2 与 (log 3)/(log 2) 两个分数。
   算术注记（这是我自己的观察，不是任何来源的说法）：按印刷式作算术，3/2 − (log 3)/(log 2) = 1.5 − 1.58496 ≈ −0.085，与同处标注的 ≈ 0.869 不符；而 0.869 恰等于 3/2 − (log 2)/(log 3)。我未能打开 Allouche 原文（EuDML 条目 403；zbMATH 的德文评论只描述方法并指出可推出 Korec 1978 的一个结果，不含指数），故只能确认「来源印的是什么」，不能判定 Allouche 原始定理应写哪个式子。引用时至少不要写成「2/3 − log3/log2」（我上一版的抄写错误，见文末「对核对意见的回应」）。
3. Col_min(N) ≤ N^θ 对自然密度 1 的 N 成立，θ > log3/log4 ≈ 0.7924 —— 1994 年，Korec，Math. Slovaca 44(1), 85 至 89，MR1290275。书目记录我经 zbMATH API 与 https://geodesic.mathdoc.fr/item/MASLO_1994_44_1_a7/ 核对；定理内容以 Tao 论文表述为准（我未读到 Korec 原文正文）。
4. #{N ≤ x : Col_min(N) = 1} ≫ x^0.84 —— 2003 年，Krasikov、Lagarias，Acta Arith. 109, 237 至 258。Tao 论文写 0.84，Gonçalves、Greenfeld、Madrid 写 0.841 并称「目前最好」。我未打开原文。

### 二、Tao 的主定理（已同行评审，我打开了出版版与 arXiv v7 全文）

5. 主定理，Theorem 1.3 —— 2019 年 9 月 8 日预印本（arXiv:1909.03562），2022 年发表于 Forum of Mathematics, Pi 第 10 卷，文章号 e12，共 56 页，DOI 10.1017/fmp.2022.8（收稿 2019 年 9 月 8 日，修回 2022 年 4 月 8 日，接受 2022 年 4 月 20 日，开放获取 CC BY）。确切陈述：对任意函数 f : N+1 → R 满足 lim_{N→∞} f(N) = +∞，有 Col_min(N) < f(N) 对对数密度 1 的 N 成立。出处：https://arxiv.org/abs/1909.03562 、https://doi.org/10.1017/fmp.2022.8 。
   注意量词次序：f 是任意给定的发散函数，结论中「对数密度 1」的例外集允许依赖 f；而不是「存在某个发散 f」。
6. Syracuse 等价形式，Theorem 1.6 —— 同论文。Syracuse 映射 Syr 定义为 (3N+1) 的最大奇因子（Tao 论文注明 OEIS A075677，我打开了 OEIS 该条目核对定义：https://oeis.org/A075677 ）；结论 Syr_min(N) < f(N) 对几乎所有奇数 N 成立（符号密度 1/2 的对数密度）。
7. 定量等价形式，Theorem 3.1 —— 同论文。对 N_0 ≥ 2 与 x ≥ 2 一致地，{N ≤ x : Col_min(N) > N_0} 的对数权重之和 ≪ (log x)·(log N_0)^{−c}；等价地：对任意 δ > 0 存在常数 C_δ，使 Col_min(N) ≤ C_δ 对下对数密度至少 1 − δ 的 N 集合成立，且 Remark 1.4 指出本文方法给出 C_δ ≪ exp(δ^{−O(1)})。这是本线目前的定量记录。

### 三、Tao 证明依赖的关键定量引理（全部已核对，编号为论文原编号）

8. Proposition 1.9（n 步 Syracuse 赋值的分布） —— 若 N 在奇数剩余类模 2^{n′} 上近似均匀（全变差 ≪ 2^{−n′}）且 n′ ≥ (2 + c_0)n，则 n 步 Syracuse 赋值向量与 Geom(2)^n 的全变差距离 ≪ 2^{−c_1 n}。即「典型 N 的连除幂次像独立几何变量」这一启发式的定量版本。
9. 启发式 (1.16) 与 (1.17) —— 典型轨道按 (3/4)^n 几何衰减，但带乘性误差 exp(O(n^{1/2}))。论文明确指出，这个 exp(O(√n)) 误差是全文使用对数密度而非自然密度的主要原因（自然密度没有近似的乘性不变性）。
10. Proposition 1.11（首达位置的稳定性） —— 取 α = 1.001，N_y 服从 [y, y^α] 上的对数均匀分布；则 (1.19) P(T_x(N_y) = +∞) ≪ x^{−c}，且 (1.20) Pass_x(N_{x^α}) 与 Pass_x(N_{x^{α²}}) 的全变差距离 ≪ log^{−c} x。这是全文最重要也最难的命题：它说「第一次落到 x 以下的位置」这个随机变量在尺度 x^α 与 x^{α²} 之间稳定。Theorem 1.3 由它经一次压缩迭代（Telescoping）推出。
11. Proposition 1.14（Syracuse 偏移的细尺度混合） —— Syrac(Z/3^n Z) 的分布在 3 进细尺度上的振荡 ≪_A m^{−A}（任意固定 A）；Lemma 1.12 给出 Syrac(Z/3^n Z) 的显式递推公式；Remark 1.18 说明 Proposition 1.14 与 Proposition 1.17 等价。
12. Proposition 1.17 即 Proposition 7.1（特征函数衰减，核心估计） —— 对 3 不整除的 ξ，|E exp(−2πi ξ·Syrac(Z/3^n Z)/3^n)| ≪_A n^{−A}，且对 n、ξ 一致（任意固定 A）。论文说这一步「最困难」。
13. Section 7 的组合机器（把第 12 条归结为二维更新过程的几何） —— Lemma 7.4：频率空间中的「黑集」（余弦接近整数处）是若干三角形的并，三角形两两分离且落在特定长条内；Lemma 7.6：更新过程单步增量 Hold 有指数尾、均值 (4, 16)；Lemma 7.7：首达位置的分布近似均匀（含 Gaussian 型估计）；Proposition 7.8：单调性；Lemma 7.9：更新过程穿过足够多三角形时通常也访问足够多「白点」；Lemma 7.10：大三角形在长穿越之后很少被立刻遇到。
14. 版本变动（我亲自对比了两个版本的 PDF 文本） —— arXiv v5（2022 年 2 月）与 v7（2026 年 7 月）中 Lemma 7.9 的陈述不同：v7 增加了指示函数 1_{R ≤ r}，并把 ε·min(r, R) 改为 εR。arXiv 页面上的 v7 说明为「又修正两处小排印错误，以及一处中等排印错误（影响 Lemma 7.9 的陈述）」。提交历史：v1 2019 年 9 月 8 日、v2 2019 年 9 月 13 日、v3 2020 年 6 月 7 日、v4 2021 年 9 月 18 日、v5 2022 年 2 月 15 日、v6 2026 年 7 月 6 日、v7 2026 年 7 月 16 日。

### 四、2020 年至今的后续

15. Gonçalves、Greenfeld、Madrid：广义 Collatz 映射的几乎有界性 —— 2021 年 11 月预印本（arXiv:2111.06170），2025 年发表于 Indiana University Mathematics Journal 74(1)，第 1 至 46 页，DOI 10.1512/iumj.2025.74.60034（Crossref 与 IUMJ 站点均核对）。已同行评审。内容：对映射 C(N) = N/p（N ≡ 0 mod p）、qN + r(j)（N ≡ j mod p），在条件 (a) p、q 互素、(b) q < p^{p/(p−1)}、(c) qj + r(j) ≡ 0 mod p 下，证明与 Tao 同型的结论：对任意 δ 存在 B_δ，使对数权重意义下密度至少 1 − δ 的 N 满足 S_min(N) < B_δ；等价地任意发散 f 的例外集对数密度为 0。其 Theorem 1.9 把 Tao 的更新过程机制抽象为可复用引理（把几何分布推广到任何具指数尾、方向条件正确的增量分布）；其 Theorem 1.8 在 f(N) = N^a 时给出自然密度 1（指数 γ = ((p − 1)/p)·log_p q 加任意小量 c，对 p = 2、q = 3 即 Korec 的 log4 3 ≈ 0.7924）。出处：https://arxiv.org/abs/2111.06170 、https://doi.org/10.1512/iumj.2025.74.60034 。
16. 同文的猜想层 —— 其 1.2 节正文（紧接 Remark 1.4 之后）写道：相信条件 (a)(b)(c) 足以保证存在 B_C > 0 使 C_min(N) ≤ B_C 对所有 N 成立（注意：这是对全部 N 的有界性，比「几乎所有 N」更强）；其 Conjecture 1.5 的正式陈述是：满足 Theorem 1.3 条件的映射只有有限多个环，且所有轨道最终进入某个环。作者在 1.2 节中紧接 Conjecture 1.5 的段落之后指出 (b) 看似最关键（该句在 1.2 节的前中段、不在节尾；经按字符位置复核：1.2 节标题在第 9549 字符，1.3 节标题在第 19453 字符，该句在第 12893 字符），并在第 8 节给出支持 Conjecture 1.5 的数值证据、以及反命题不成立的反例。仅猜想，无证明。原文并指出 Conway 的不可判定性意味着一般 Collatz 型映射的「全轨道有界」不可判定，所以必须挑子类。
17. Inselmann：实数类比映射上的「有界」 —— 2024 年 1 月预印本（arXiv:2401.17241，无期刊版本）。对 C_R(x) = x/2 或 3x/2（按 [x] 的奇偶，[x] 取最近整数）证明：存在常数 K > 0，使 liminf C_R^n(x) ≤ K 的 x 集合的 Lebesgue 补集为零。即在这条类比线上，「几乎有界」确实能升级为「有界」。就我检索所及，这是本线里唯一一个真正跨过「有界」门槛的结果，但对象是实数类比映射而非 Collatz 本身。出处：https://arxiv.org/abs/2401.17241 。
18. Inselmann：局部描述的极大范围 —— 2024 年 2 月预印本（arXiv:2402.03276，无期刊版本）。对加速映射 T，把 Terras 与 Everett 型的同时控制（(√3/2)^k m^{1±ε}）从 α = 1/log 2 推广到 α = 2/log(4/3) ≈ 6.952，并称这是最大可能值；推论仍然只是 T_min(m) ≤ m^ε（对任意 ε > 0、自然密度 1），不是 Tao 型的任意发散 f。出处：https://arxiv.org/abs/2402.03276 。
19. Assani、Ebbighausen：Terras 集合密度的收敛速率与「测度判据」 —— 2023 年 10 月预印本（arXiv:2310.08749，无期刊版本）。给出 Terras 型密度收敛的显式上界（其 Theorem 2），并证明：若存在 N 上处处非零的有限测度使系统渐近平稳（asymptotically mean stationary），则 D2 = ∅，即所有轨道有界（其 Proposition 8；反向的 Lemma 9 给出逆命题）。注意：这是一个条件性等价刻画，不是无条件证明；其摘要中的说法容易被误读为已证有界性。此外该文把 Tao 的定理转述成「D2 有对数密度 1」，这一转述并不准确（Tao 的结论是轨道下探到任意发散函数以下，不是落入环），引用时不要沿用。出处：https://arxiv.org/abs/2310.08749 。
20. Siegel：Syracuse 随机变量与非阿基米德谱理论 —— 2020 年 7 月预印本（arXiv:2007.15936，v1 标题为 Syracuse 随机变量与 Collatz 型映射的周期点，v2 起改题为非阿基米德谱理论系列第一部分，v3 更新至 2023 年 4 月；无期刊版本）。其 v1 明确把 Tao 的 Syracuse 随机变量与作者的「numen」等同，用于刻画周期点。我读了 v1 的摘要与 Semantic Scholar 的元数据，未读全文证明。出处：https://arxiv.org/abs/2007.15936 。
21. Siegel、O'Dwyer：数域上的几乎有界性（最新） —— 2026 年 9 月 26 日预印本（arXiv:2609.33018，仅预印本）。把 Tao 的结论推广到数域 K 的整数环上的「p 进 Hydra 映射」（由模一个指数为 p 的理想 Λ 分类的分片仿射映射），在维数条件 (p − 1)^2 · ρ_H^d < 1（ρ_H 为各分片线性部分 Minkowski 范数之积）等条件下证明同型结论，并称包含 Tao 原结果作为特例；方法改走 Archimedean 分析，不需要 Syracuse 随机变量的 Fourier 衰减估计。我核对了摘要与元数据，未读正文，其定理未经同行评审。出处：https://arxiv.org/abs/2609.33018 。
22. Wegner：3x+k 版本 —— 2021 年 1 月预印本（arXiv:2101.08060，无期刊版本）。给出不同 k 的 Syracuse 迭代分布的简单关系，并称 Tao 论文中的振荡部分不依赖 k，因而该片段对不被 2、3 整除的所有 k 成立。仅为片段性宣称。出处：https://arxiv.org/abs/2101.08060 。
23. 数值验证记录（与本线「显式化加有限验证」方向配套） —— 2^68（Barina，2020 年，J. Supercomputing，Tao 论文参考文献 [3]）；2^71（Barina，2025 年，The Journal of Supercomputing 81，文章号 810，DOI 10.1007/s11227-025-07337-0，Crossref 核对）；项目主页显示已完成 2075 × 2^60 ≈ 2^71.02，并向 2076 × 2^60 推进（我打开了 https://pcbarina.fit.vutbr.cz/ ）。历史节点：2020 年 5 月 7 日到 2^68、2021 年 12 月 10 日到 2^69、2023 年 7 月 9 日到 2^70。
24. 相邻路线（非本线，仅备查） —— Yolcu、Aaronson、Heule 用字符串重写终止性与 SAT 证明若干弱化形式（Journal of Automated Reasoning 67(2)，2023 年，DOI 10.1007/s10817-022-09658-8，DOI 经 Crossref 核对）。这类工作不给出 Col_min 的界。

## 当前的技术极限（记录值是多少、谁保持、为什么停在那里）

1. 有界性的界：记录保持者是 Tao ——「任意发散 f」，对数密度 1（2019 年预印本，2022 年期刊版）。截至 2026 年 10 月 18 日，我未检索到任何已发布结果把它改进为固定的 C_0，也未检索到自然密度版本。
2. 定量记录：C_δ ≪ exp(δ^{−O(1)})（Tao 论文 Remark 1.4 与 Theorem 3.1）。没有人改进这个常数形状；Gonçalves、Greenfeld、Madrid 的推广沿用同一形状，只换了底层的映射类。
3. 「有界」这一步为什么停在这里（Tao Remark 1.4 的原话要点，我逐字核对了 arXiv v7 与出版版） —— 若对某个 C_0 存在一条永不落到 C_0 以下的轨道（有至少一条无界轨道、或无穷多周期轨道，都属这种情形），则按 (1.16) 型启发式，正密度多的 N 的轨道会在落到 C_0 以下之前撞上该轨道的某个元素，此后也永不落到 C_0 以下。因此「固定 C_0 对几乎所有 N 成立」这一陈述与「排除这类轨道」几乎等价，即接近猜想本身，超出本文方法。这是本线最重要的结构性障碍陈述，不是技术细节。
4. 自然密度这一步为什么停在这里（Tao Remark 1.16） —— 要把对数密度升级为自然密度，看来必须把 Proposition 1.14 加强为整个随机仿射映射 Aff_{Geom(2)^n} 的细尺度混合，而不只是偏移 F_n(Geom(2)^n)；Tao 说这「看来可以达到」，但未做。另一处说法（正文第 1.1 节附近）则把原因归于 (1.17) 的 exp(O(√n)) 乘性误差与自然密度缺乏乘性不变性。两种说法指同一障碍的两个侧面。
5. 相对地，Gonçalves、Greenfeld、Madrid（2021 预印本、2025 期刊版）明确写道：把结论加强到自然密度意义下的「几乎所有」是「非常困难、目前仍不可及」（原文 out of reach）。这与 Tao 的「看来可以达到」并存，说明 2021 年至 2025 年间没有人真做出来。
6. 局部控制的天花板：Inselmann 2024（arXiv:2402.03276）把自己的 α = 2/log(4/3) ≈ 6.952 称为最大可能值，即「在 (√3/2)^k 尺度上同时控制一切中间项」这一局部描述类型已到极限。局部描述再往长时间推的空间基本封闭。
7. 逐项引理的松紧：Tao 说 (1.20) 的 log^{−c} x 可能改进到 x^{−c}；Proposition 1.17 的 n^{−A} 可能改进到 exp(−cn)。二者都未被人做出来（我未检索到），但即使做出来也不改变结论类型，只改常数与误差。
8. 综述缺口：Lagarias 的注释文献第一部分（arXiv:math/0309224，2011 年最后一次更新，覆盖至 1999 年）与第二部分（arXiv:math/0608208，2012 年最后一次更新，覆盖 2000 年至 2009 年）都不覆盖本线；2021 年 11 月上传的综述章节（arXiv:2111.02635）是 2010 年《The Ultimate Challenge》一书的章节重印，内容截至 2010 年，正文不含 Tao 的引用（我用 pdftotext 抽取全文并检索过）。也就是说，本线目前没有权威综述，只能读原文。

## 未解决的缺口

1. 自然密度版本：Tao 定理的「对数密度 1」能否换成「自然密度 1」。Tao 称看来可达（Remark 1.16），Gonçalves 等人称仍不可及；我未找到任何已发布结果。
2. 有界值版本：存在绝对常数 C_0 使 Col_min(N) ≤ C_0 对几乎所有 N 成立。按 Remark 1.4 的启发式，这等价于排除无界轨道与无穷多周期，实质上接近猜想，密度方法无法单独完成。
3. 显式化：把 Theorem 3.1 中所有隐含常数与「充分大」有效化，与数值验证（当前 2^71）合并，得到「Col_min(N) = 1 对正对数密度的 N 集合成立」。Tao 在 Remark 1.4 的脚注（致谢 Ben Green）中把这一点列为 in principle possible；我未找到任何人做出来。注意这与 Krasikov、Lagarias 的 ≫ x^0.84 是不同类型的结果：后者是计数下界，不给出正密度。
4. 特征函数衰减的指数提升：从 n^{−A} 到 exp(−cn)，Tao 说可能但未追求；2026 年 Siegel、O'Dwyer 的预印本改走 Archimedean 路线，在更一般的映射类上绕开了这个需求，但那一结果本身未经同行评审。
5. Proposition 1.9 的 2 进等分布假设（n′ ≥ (2 + c_0)n、全变差 ≪ 2^{−n′}）能否放松，未见有人研究。
6. Proposition 1.11 中 α = 1.001 与 (1.20) 的依赖关系：论文说 (1.20) 的实际需求弱于 log^{−c} x，具体门槛是多少未在论文中定死，未见后续工作收紧。
7. Gonçalves、Greenfeld、Madrid 的 Conjecture 1.5（有界性）与「条件 (b) 是否必要」只有数值证据；Conway 的不可判定性界定了这一子类猜测的合理范围。
8. 邻线的计数指数 0.84：我检索到的「改进」（π₁(x) ≥ x^0.8676、π_a(x) ≥ x^0.895，声称在 Lean 4 中机器验证，见 https://github.com/msharpe248/collatz ）全部来自未经同行评审的代码仓库，我未能核对，不能计入记录。

## 若要在这一线推进，必须跨过什么门槛

1. 自然密度门槛（技术性，最可能被单独攻克）：证明随机仿射映射 Aff_{Geom(2)^n}（含线性部分 3^n 2^{−|a|} 与偏移两部分）的联合细尺度混合。已知障碍是 (1.17) 的 exp(O(√n)) 乘性误差；要么把该误差压到自然密度可容忍的范围，要么改换「几乎全部」的采样机制（例如对每个尺度重新抽样而非从 [1, x] 一次抽样）。
2. 有界门槛（结构性，最难）：必须在不预设猜想的前提下排除「永不落入 [1, C_0] 的轨道」这一族（包含无界轨道与无穷多周期）。按 Remark 1.4 的启发式，任何纯密度型下界手段都无法单独给出固定 C_0，必须引入关于周期结构与无界轨道的硬信息（例如周期长度排除、无界轨道的刚性约束）。这一门槛与本目录其他研究线（周期排除、无界轨道）直接耦合。
3. 显式化门槛（最具体、最可操作）：把 Lemma 7.4 至 Lemma 7.10 的分离常数、Proposition 7.3 与 7.1 的所有 ≪_A 常数、Theorem 3.1 的「充分大」全部有效化，得到 Theorem 3.1 的一个完全显式版本，再与当前 2^71 的数值验证合并，得到 Col_min(N) = 1 的正对数密度集合。代价是大量计算机辅助常数管理，收益是本线能产出的第一个「新定理式」结论。
4. 局部控制门槛（基本封闭）：Prop 1.9 型局部描述的时间范围已被 Inselmann 推到自称为最大值的 α ≈ 6.952；继续在这一维度加长不会带来新结论类型。
5. 若走推广路线：Siegel、O'Dwyer 的维数条件 (p − 1)^2 ρ_H^d < 1 是新出现的门槛形式，其必要性未知；Gonçalves 等人的 q < p^{p/(p−1)} 条件被其本人视为最关键条件。在这类子类上从「几乎有界」推进到「有界」同样只是猜想（其 Conjecture 1.5），且 Conway 的不可判定性说明该子类的选择本身是实质性的。
6. 反面门槛（需要写进任何声称中）：若有人宣称在有界性上取得突破，先检查是否与 Remark 1.4 的启发式冲突——在密度框架内，固定 C_0 的结论需要一个独立理由来排除永不落入该界的轨道；纯粹的密度的、局部的估计无法提供这个理由。

## 来源清单（逐条注明我是否亲自打开过）

1. https://arxiv.org/abs/1909.03562 —— 亲自打开（curl 抓取摘要页与提交历史，并下载 PDF 全文，pdftotext 抽取正文；读的是 v7）。
2. https://arxiv.org/pdf/1909.03562v7 —— 亲自打开（下载并抽取全文，逐条读了 Theorem 1.3、1.6、3.1，Proposition 1.9、1.11、1.14、1.17、7.1、7.3、7.8，Lemma 1.12、7.4、7.6、7.7、7.9、7.10，Remark 1.4、1.13、1.15、1.16、1.18，以及参考文献全表）。
3. https://arxiv.org/pdf/1909.03562v5 —— 亲自打开（为核对 Lemma 7.9 的版本差异，与 v7 逐段对比）。
4. https://www.cambridge.org/core/services/aop-cambridge-core/content/view/1008CC2DF91AF87F66D190C5E01C907F/S2050508622000087a.pdf/almost-all-orbits-of-the-collatz-map-attain-almost-bounded-values.pdf —— 亲自打开（下载出版版 PDF，56 页，核对卷期、文章号、DOI、收修接受日期、Remark 1.4 与 Theorem 3.1 的出版版措辞）。
5. https://doi.org/10.1017/fmp.2022.8 —— 未单独打开（其解析目标即上一条 PDF；Crossref API 返回该 DOI 的刊物名与年份，已核对）。
6. https://www.cambridge.org/core/journals/forum-of-mathematics-pi/article/1008CC2DF91AF87F66D190C5E01C907F —— 尝试打开，页面为脚本壳，返回内容不足，改用上一条 PDF。
7. https://terrytao.wordpress.com/2019/09/10/almost-all-collatz-orbits-attain-almost-bounded-values/ —— 亲自打开（抽取正文，读了 Tao 本人对证明策略的叙述：Bourgain 思想、Syracuse 随机变量、Riesz 积、三角形分离）。
8. https://oeis.org/A075677 —— 亲自打开（核对 Syracuse 映射即「约化 Collatz 函数 R 作用在奇数上」的定义）。
9. https://arxiv.org/abs/2111.06170 与 https://arxiv.org/pdf/2111.06170v2 —— 亲自打开（抽取全文，读 Theorem 1.3、1.8、1.9，Conjecture 1.5，以及关于自然密度仍不可及的论述）。
10. https://doi.org/10.1512/iumj.2025.74.60034 —— 亲自打开（经 doi.org 到达 IUMJ 站点，看到该文条目；另经 Crossref API 核对卷 74、期 1、页 1 至 46、2025 年）。
11. https://arxiv.org/abs/2401.17241 与 https://arxiv.org/pdf/2401.17241v1 —— 亲自打开（读了摘要与引言；实数类比的有界性）。
12. https://arxiv.org/abs/2402.03276 —— 亲自打开（arXiv API 元数据与摘要全文；无期刊参考）。
13. https://arxiv.org/abs/2310.08749 与 https://arxiv.org/pdf/2310.08749v1 —— 亲自打开（读了摘要、引言、Theorem 2、Proposition 8 与 Lemma 9；确认其有界性结论是条件性的，并记录其对 Tao 定理的不准确转述）。
14. https://arxiv.org/abs/2007.15936 —— 亲自打开（arXiv API 元数据与两版摘要；了解 v1 标题与非阿基米德谱理论系列的关系）。
15. https://arxiv.org/abs/2609.33018 —— 亲自打开（arXiv API 元数据与摘要全文；2026 年 9 月最新预印本）。
16. https://arxiv.org/abs/2101.08060 —— 亲自打开（arXiv API 元数据与摘要全文）。
17. https://arxiv.org/abs/2105.14697 与 https://doi.org/10.1007/s10817-022-09658-8 —— 亲自打开（摘要经 Semantic Scholar；DOI 经 Crossref 核对为 J. Automated Reasoning 67(2)，2023 年）。
18. https://api.semanticscholar.org/graph/v1/paper/arXiv:1909.03562/citations —— 亲自打开（两页共 126 条引用，用于穷举后续文献；本线相关的条目已逐条筛出）。
19. https://api.crossref.org/works/10.1007/s11227-025-07337-0 —— 亲自打开（核对 Barina 2025 的刊物、卷、文章号）。
20. https://pcbarina.fit.vutbr.cz/ —— 亲自打开（读项目页：已完成至 2075 × 2^60 ≈ 2^71.02，及历史节点）。
21. https://api.zbmath.org/v1/document/_search （检索 Korec 1994）—— 亲自打开（返回唯一命中：Math. Slovaca 44(1), 85 至 89, 1994, MR1290275）。
22. https://geodesic.mathdoc.fr/item/MASLO_1994_44_1_a7/ —— 亲自打开（HTTP 200，书目记录页；未含正文）。
23. https://eudml.org/doc/32414 —— 未能打开（403），故 Korec 原文正文未核对。
24. https://arxiv.org/abs/2111.02635 —— 亲自打开（下载 PDF 抽取全文，确认其为 2010 年书章重印、正文不含 Tao 引用）。
25. https://arxiv.org/abs/math/0309224 与 https://arxiv.org/abs/math/0608208 —— 亲自打开（经 arXiv API 核对两部分的覆盖年份与最后更新年份）。
26. https://github.com/msharpe248/collatz 与其 README 原始地址 —— 亲自打开（读到其自称的 π₁(x) ≥ x^0.8676、π_a(x) ≥ x^0.895 与「Krasikov、Lagarias 记录为 0.8418」等说法；未经同行评审，我未核对证明，仅作未核实条目登记）。
27. https://terrytao.wordpress.com/wp-content/uploads/2020/04/collatz-1.pdf —— 未打开（仅见于搜索摘要，其中提到「也许能把对数密度换成自然密度、并用有限计算把 C_0 取到 1」；正式版本中的对应文字见 Remark 1.4，已核对出版版措辞，故不依赖此链接）。
28. https://www.scirp.org/journal/paperinformation?paperid=128813 （Zhang、Zhang 关于所有奇数轨道取有界值的宣称）—— 未能打开（403）。该宣称所在刊物不在主流索引，我无法核对，不予采信，也不计入任何记录。
29. https://arxiv.org/e-print/1909.03562 —— 亲自打开（下载 gzip 源码包并解包得 collatz.tex，用于第 165 行阈值式的决定性核对；该行不依赖任何 pdftotext 展平）。
30. https://api.zbmath.org/v1/document/_search （检索 Allouche 1979「Sur la conjecture de Syracuse-Kakutani-Collatz」）—— 亲自打开（返回该文记录与德文评论全文；评论描述方法并指出可由其推出 Korec 1978 的一个结果，但不含指数式，故无法用它判定阈值）。
31. https://eudml.org/doc/182044 （Allouche 1979）—— 未能打开（403，与其 Korec 条目同样情况），故 Allouche 原文正文未核对。
32. https://www.numdam.org/item/STNB_1978-1979____A9_0/ —— 未能打开（404；我尝试的该标识符不存在，Talence 1978 至 1979 年讲义似未数字化到 Numdam）。
33. https://dept.math.lsa.umich.edu/~lagarias/3x+1.html —— 未能打开（403，站点防护），故 1985 年 Lagarias 综述（Amer. Math. Monthly 92）未能用于交叉核对 Allouche 的指数。

## 对核对意见的回应

本节记录 2026 年 10 月 18 日收到两处核对意见及我的复核方式与结论。两处我都确认核对员正确，笔记已按复核结果改写。

1. 阈值式抄反（对应「关键结果」第 2 条）—— 确认，已改写。我上一版把 Allouche 的阈值写成「θ > 2/3 − log3/log2」；核对员指出来源印的是 3/2。我做决定性核对的方式不是看 pdftotext 的展平输出（分式会被展平成「23」或「32」，方向不可靠），而是三路并用：(a) 取 arXiv 源码包 https://arxiv.org/e-print/1909.03562 ，解包得 collatz.tex，第 165 行逐字为 $\theta>\frac{3}{2} - \frac{\log 3}{\log 2} \approx 0.869$，这一路无歧义；(b) pdftotext -bbox 取 arXiv v7 第 2 页词框，「3」的 yMin = 445.01 高于「2」的 yMin = 453.84，即分子是 3；(c) pdftoppm -r 600 分别渲染 arXiv v7 与出版版 PDF 第 2 页、裁剪放大后目视，两版都印作 3/2 − (log 3)/(log 2) ≈ 0.869。三路一致，所以我的 2/3 是抄写错误。
   核对员提出的算术疑虑我确认为真：按印刷式 3/2 − (log 3)/(log 2) = −0.085，与 ≈ 0.869 不符；与 0.869 相符的式子是 3/2 − (log 2)/(log 3)（这是我自己的算术，不是来源的说法）。核对员说它无法判定 Allouche 原始定理应写哪个式子；我做了额外尝试也未能解决：EuDML 的 Allouche 条目返回 403，zbMATH 的德文评论不含指数，Numdam 上找不到该讲义（直接尝试的标识符返回 404），Lagarias 主页返回 403。因此我在笔记中只记录「来源印的是什么」，并附上算术注记，不替 Allouche 补一个我未核对过的式子。
2. GGM 中「(b) 最关键」一句的位置（对应「关键结果」第 16 条）—— 确认，已改写。核对员指出该句在 1.2 节内、紧跟 Conjecture 1.5 之后，而非节尾。我按字符位置在 ggm.txt 中复核：1.2 节标题在第 9549 字符，1.3 节标题在第 19453 字符，该句在第 12893 字符（约在 1.2 节前 34% 处）；且「We believe that the conditions」在第 12112 字符、「Conjecture 1.5.」在第 12319 字符，都在该句之前。故该句确实紧接 Conjecture 1.5，但不在节尾。原写法「1.2 节末尾」不准确，已改为「1.2 节中紧接 Conjecture 1.5 的段落之后」。
