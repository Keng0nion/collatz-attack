# two-adic

检索者：文献检索员·two-adic。检索日期：2026 年 10 月 18 日。

本笔记的每条关键结果都尽量给到可打开的原始出处；凡是「仅凭搜索结果」或「未能打开」的，逐条标注。全部 URL 的打开状态见最后一节。

## 这条线在问什么

记加速映射 T(x) = (3x+1)/2（x 为奇数）、x/2（x 为偶数），移位映射 S(x) = (x−1)/2（x 为奇数）、x/2（x 为偶数），二者都定义在 2 进整数环 Z_2 上。这条线的基本事实是：存在唯一的同胚 Φ: Z_2 → Z_2（Φ(0) = 0）满足

  Φ ∘ S ∘ Φ^{−1} = T。

等价地，Q := Φ^{−1} 把 x 在 T 迭代下产生的奇偶序列编码成一个 2 进整数：

  Q(x) = Σ_{i≥0} (T^i(x) mod 2) · 2^i。

于是 T 在 Z_2 上的动力学与移位映射完全同构（拓扑同构，而且保 2 进 Haar 测度）。这条线研究的正是在这个「已经解决」的框架里发生了什么：

1. 共轭映射本身的算术性质。Φ 保有理数吗（周期猜想）；Φ 的不动点与周期点有多少；Φ 模 2^n 诱导的置换有什么循环结构；Φ 可微吗。
2. Syracuse 随机变量与随机模型。把 T 的每一步解码成几何随机变量，得到 3 进整数上的极限分布，用来预测或证明关于「几乎所有」整数的结论。
3. 测度论与遍历论能给出什么。T 在 Z_2 上保测、遍历、Bernoulli；而正整数集 Z+ 只是 Z_2 里一个可数（因而零测）的子集。这条线最核心的困难就在这里：动力学被完全理解的那个空间，与猜想所谈论的那个集合，是「几乎不相交」的。

## 关键结果

每条一行的结论，年份、作者、出处，并标注可信度分级：甲 = 经同行评审的定理；乙 = 仅预印本；丙 = 有缺口、被自我弱化、或未能核对的宣称。

### 一、共轭定理（这条线的骨架）

1. 【甲】共轭定理：存在唯一同胚 Φ: Z_2 → Z_2，满足 Φ(0) = 0 且 Φ ∘ S ∘ Φ^{−1} = T；Φ 是螺线型的（对每个 n 诱导 Z/2^n Z 上的置换 Φ_n，即 x ≡ y (mod 2^n) 蕴含 Φ(x) ≡ Φ(y) (mod 2^n)）；Φ 与 Φ^{−1} 都是 2 进等距（螺线型双射即等距，见该文附录 A），因而都保 2 进测度。由此 T 与 2 进移位拓扑共轭且测度共轭，从而 T 是 Bernoulli 的（特别地保测、强混合、遍历）。—— 1996，D. J. Bernstein、J. C. Lagarias，Canad. J. Math. 48 (1996), 1154 至 1169；原文 PDF 已打开（Lagarias 主页版）。原文对「保测、强混合、遍历」只给出文献指引「see [8]」（[8] 即 Lagarias 1985；该 1985 年原文我未能打开），且原文中不出现「Theorem K」这个编号（grep 计数为 0）；「Lagarias 1985, Theorem K」的编号出自 Kontorovich、Lagarias 第 10 节（arXiv:0910.1944，已打开）。

2. 【甲】两个显式公式：Φ^{−1}(x) = Σ_{i≥0} (T^i(x) mod 2)·2^i；若 x = Σ_l 2^{d_l}（0 ≤ d_1 < d_2 < ⋯，序列有限或无限）则 Φ(x) = −Σ_l 3^{−l} 2^{d_l}（注意负号：该 PDF 的文本层会吞掉负号，本条已用 pdftoppm 渲染原书第 2 页图像逐字核对）。—— 1996，Bernstein、Lagarias 式 (1.5)、(1.6)；后一公式的原始出处为 Bernstein 1994（其式 (2) 写作 N = (−1/3)2^{d_0} + (−1/9)2^{d_1} + ⋯）。

3. 【甲】非迭代等价表述：设 x = 2^{d_0} + 2^{d_1} + ⋯ 为唯一分解，令 Φ(x) = −Σ_j 2^{d_j} / 3^{j+1}；则 Φ 是 Z_2 的置换与同胚，且 3N+1 猜想成立当且仅当 Z+ ⊆ Φ((1/3)Z)（等价地 Q(Z+) ⊂ (1/3)Z）。—— 1994，Daniel J. Bernstein，Proc. Amer. Math. Soc. 121(2), 405 至 408（出版社版 PDF 已打开）。

4. 【甲】不可微性：Φ 与其逆在 Z_2 上处处不可微（原为 Müller 1991 的定理，Bernstein 1994 给出短证明）。—— 1994，Bernstein，Corollary 2（已打开）。

5. 【甲】置换结构：Φ 模 2^n 诱导的置换 Φ_n 的每个循环长度都是 2 的幂；当 n ≥ 6 时 Φ_n 的阶恰为 2^{n−4}，且含三条长度 2^{n−4} 的长循环；判据是若某循环与其上一层提升都是「惰性（inert）」且长度 ≥ 4，则此后各层永远惰性（稳定循环）。—— 1996，Bernstein、Lagarias，Theorem 3.1、Corollary 3.1a（已打开）。

6. 【甲（一半）+ 猜想】有理点：已证 Φ(Q ∩ Z_2) ⊆ Q ∩ Z_2，即 x 有理蕴含 Φ(x) 有理；等价地「Q(x) 有理蕴含 x 有理」。未证的另一半（周期猜想，Periodicity Conjecture，Lagarias 1985 提出）断言该包含是等号，即 Φ 保持有理数。若成立，则 T 在整数上无发散轨道；而且（原书第 3 页，据其文献 [9] 的 Corollary 2.1b）它与下述断言等价：对所有 k ≡ ±1 (mod 6)，映射 T_{3,k}（x 奇时取 (3x+k)/2，x 偶时取 x/2）在整数上无发散轨道（原文量词为 ±1；我第一轮据文本抽取误录为 1，本轮已渲染原书第 3 页图像更正）。—— 已证部分：Bernstein 1994 Corollary 1（已打开）；猜想表述：转引自 Bernstein、Lagarias 1996 与 Rozier（两文已打开）。Akin 2004 把同一猜想称作 Rationality Conjecture（已打开）。

7. 【甲】有理循环：T 在 Z_2 上的每一个循环都由有理数组成。—— 转引自 Rozier 第 3.3 节（其引 Lagarias 1990）。附注：该事实也可从第 6 条的已证方向直接推出（周期奇偶序列给有理的 Q 值，再经 Φ 保持有理数）。Lagarias 1990 原文我未能打开；但其本人的注释书目（arXiv:math/0309224，已打开）第 108 条说明该论文研究 3x+k（k ≡ ±1 mod 6）的整数循环，断言无穷多个 k 至少有 k^{1−ε} 个周期 ≤ log k 的循环，而无穷多个 k 没有周期 < k^{1/3} 的循环。

8. 【甲 + 猜想】共轭映射的不动点与周期点：Φ 有两个奇不动点 −1 与 1/3，另有奇 2 循环 {1, −1/3}；Fixed Point Conjecture 断言 −1 与 1/3 是仅有的奇不动点；3x+1 Conjugacy Finiteness Conjecture 断言对每个 j ≥ 0，Φ 的周期为 2^j 的奇周期点只有有限多个。—— 1996，Bernstein、Lagarias（已打开）；不动点为 −1 与 1/3、以及 2 循环 {1, −1/3} 的表述另见 Lagarias 注释书目第 23 条与 Rozier 第 3.6 节（均已打开）。核对注记：该 PDF 的文本层会吞掉负号（例如第 2 页的 V(x) = −1 − x 被抽成「1 x」，式 (1.6) 的负号亦然），故公式与不动点均以 pdftoppm 渲染的原书图像为准；渲染图第 6 页原文为「we searched for odd rational fixed points, and immediately found two: x = −1 and x = 1/3」。

### 二、测度论与遍历论

9. 【甲】2 进延拓定理：T_3（3x+1）与 T_5（5x+1）都唯一连续延拓为 Z_2 的自同胚，都保 2 进 Haar 测度、都强混合因而遍历；且各自通过螺线型共轭 Φ_3、Φ_5 与 2 进移位拓扑共轭。因此 T̃_3 与 T̃_5 拓扑共轭且测度共轭，在 Z_2 上「动力学完全相同」。—— Kontorovich、Lagarias，arXiv:0910.1944（Theorem 10.1、10.2、Corollary 10.1，已打开）；3x+1 情形作者归给 Bernstein、Lagarias 1996 第 3、4 节。

10. 【甲（关键否定性论断）】Z ⊂ Z_2 可数、因而 2 进测度为零，所以遍历论的一般性质对 Z 上迭代的行为「得不出任何结论」；3x+1 与 5x+1 在 Z_2 上同构，而在整数上的（猜想）行为完全不同，正说明 2 进动力学无法区分二者。—— Kontorovich、Lagarias，arXiv:0910.1944 第 10 节末段（已打开，原文明确写出）。同观点另见 Rozier 第 3.5 节与 Akin 2004（均已打开）。

11. 【甲】广义 Collatz 映射的遍历测度：对 T(x) = (m_i x − r_i)/d（当 x ≡ i mod d 时取值，各 m_i 与 d 互素），T 可唯一连续延拓到 polyadic 整数环；存在有限多个遍历 Borel 概率测度，其结构刻画整数轨迹在模 m 同余类中的极限频率。—— 1992，K. R. Matthews，Colloquium Mathematicum 63 (1992), 191 至 202（官方 PDF 已打开）。

12. 【甲，转引】非扩张函数的遍历判据（Anashin）：F: Z_2 → Z_2 若 1 缩（非扩张），则 F 遍历当且仅当对每个 n ≥ 1，F 模 2^n 诱导单循环置换。—— 转引自 Rozier Theorem 4（其引 Anashin 2006）；Anashin 原文我未打开。

13. 【甲】Rozier 的遍历域结果：用第 5 条所述的判据（原文称 Theorem 6，实即 Bernstein、Lagarias 的 Theorem 3.1）定出「奇遍历集」并给出计数表，得奇遍历集总测度 > 0.48，再用自共轭把偶遍历集补上，得遍历域测度 > 0.96；猜想 Ergodicity Conjecture：遍历域有满测度。—— Rozier，INTEGERS 19 (2019), #A8（2019 年 2 月 1 日出版，DOI 10.5281/zenodo.10705023；已发表版 PDF 我经卷目录页的取件表单下载并抽取，在其中逐句核到 0.48 与 0.96 两处及 Conjecture 3）。同一结果的更新预印本为 arXiv:1805.00133v6（2025 年 2 月 18 日，全文已打开，定理编号与出版版一致）。本条第一轮曾被误标为仅预印本，特此更正。

### 三、随机模型与 Syracuse 随机变量

14. 【甲】Tao 主定理：对任意 f: N+1 → R 且 f(N) → ∞，几乎所有的 N（对数密度意义）满足最小轨道值 Col_min(N) < f(N)；定量版本给出常数 C_δ ≪ exp(δ^{−O(1)})（Theorem 3.1）。等价的有 Syracuse 版本（Theorem 1.6）。—— 2022，Terence Tao，Forum of Mathematics, Pi 10 (2022), e12，DOI 10.1017/fmp.2022.8；arXiv:1909.03562，arXiv 版全文已打开。期刊页我未亲自打开，出版元数据经多处检索确认。

15. 【甲】Syracuse 随机变量的定义：对 n ≥ 1，在 Z/3^n Z 上定义 Syrac(Z/3^n Z) ≡ F_n(Geom(2)^n) mod 3^n，其中 F_n 是 n 步 Syracuse 偏移映射，Geom(2) 为均值 2 的几何分布；投影相容（mod 3^k 还原）；满足递归公式（Lemma 1.12）；可视为 Z_3 上单个随机变量 Syrac(Z_3) = Σ_j 3^j 2^{−a[1,j+1]} 的投影，其分布是 Z_3 上马尔可夫过程 x ↦ (3x+1)/2^a（转移概率 2^{−a}）的唯一平稳测度。—— 2022，Tao（已打开）式 (1.22)、Lemma 1.12、Remark 1.13。

16. 【甲】细尺度混合与特征函数衰减：Osc_{m,n}(P(Syrac = Y mod 3^n)) ≪_A m^{−A}（Prop 1.14），等价于对任何不被 3 整除的 ξ 有 E e^{−2πiξ·Syrac(Z/3^n Z)/3^n} ≪_A n^{−A}（Prop 1.17）；这是主定理的技术核心。—— 2022，Tao（已打开）。

17. 【甲】Sinai 的统计理论：Structure Theorem（给定步长序列 k_1, …, k_m，能够依次施加这些步的正整数 x 恰构成一个等差数列，且像到像的对应是同一个 p 参数下的仿射关系）；Theorem 3.1（归一化轨迹 ω 的有限维分布收敛到零漂移 Wiener 测度，扩散常数 σ > 0）；Theorem 5.1（熵不等式 H_m ≥ m ln 3 − (2γ° + 7) ln m）。—— 2003，Ya. G. Sinai，Comm. Pure Appl. Math. 56 (2003), 1016 至 1028；arXiv:math/0201102 全文已打开。核对注记：该文致谢中作者自述 Lagarias 在上一版发现了严重漏洞（原文可查），说明投稿版曾有缺陷、发表版已修正。

18. 【甲，转引】Sinai 的均匀分布定理：按 2^{−(k_1+⋯+k_m)} 给深度 m 的前像加权，缩放后的概率分布 P^{(m)} 弱收敛到 [0,1] 上的均匀分布；2004 年另有简化强化的版本。—— Sinai 2003b（Moscow Math. J. 3 (2003), 1429 至 1440）与 Sinai 2004（Comm. Math. Phys. 252, 581 至 588），转引自 Lagarias 注释书目 II（arXiv:math/0608208）第 103、104 条（书目已打开）；两篇原文我未打开。

19. 【甲，模型预测而非定理】Lagarias 与 Weiss 的两个随机模型（分支随机游走加大偏差）：预测存在常数 c_0 = 41.677…，使得以概率 1 对任意 ε > 0，只有有限多个 m 需要 (c_0 + ε) log m 步到 1，而无穷多个 m 至少需要 (c_0 − ε) log m 步；并猜想最大 excursion t(n) < n^{2+o(1)}。—— 1992，J. C. Lagarias、A. Weiss，Ann. Appl. Probab. 2 (1992), 229 至 261；原文我未打开（Project Euclid 页被 Incapsula 拦截，JSTOR 需订阅），内容转引自 Lagarias 注释书目第 112 条与 Kontorovich、Lagarias（两者均已打开）。

20. 【甲】达到 1 的计数下界链：π_a(x) ≥ x^γ（π_a 计 ≤ x 中终达 a 的整数个数，a 不被 3 整除）。γ = 0.643（Applegate、Lagarias 第 I 篇，方法起步于 Crandall 1978、Sander 1990）；γ = 0.43（Krasikov 1989，用 μ_2 型差分不等式系统）；γ = 0.48（Wirsching 1993，用 μ_3 系统）；γ = 0.81（Applegate、Lagarias 第 II 篇，计算机辅助线性规划）；γ = 0.84（Krasikov、Lagarias 2003，Theorem 6.1，γ = log_2 λ ≈ 0.84175）。—— 前四者见 Applegate、Lagarias 第 II 篇预印本引言（已打开）；0.84 见 arXiv:math/0205002（已打开），正式出版于 Acta Arith. 109 (2003), 237 至 258。我没有检索到比 0.84 更高的已发表指数（此点标注为「未能核实是否已被改进」）。

### 四、预印本与有问题的宣称

21. 【乙】Siegel 的「numen」与对应定理：对奇素数 p，取 H_p: x ↦ x/2 或 (px+1)/2；存在连续函数 χ_p: Z_2 → Z_p，使奇数 ω 是 H_p 的周期点，当且仅当存在整数 n ≥ 1 使 ω = χ_p(n)/(1 − r_p(n))，其中 r_p(n) = p^{#1(n)} / 2^{λ(n)}（#1 为二进制 1 的个数，λ 为位数）。—— Maxwell C. Siegel，arXiv:2007.15936v1（2020 年 7 月），v1 标题为 Syracuse Random Variables and the Periodic Points of Collatz-type maps（v1 PDF 已打开）。版本状态经 arXiv API 核实：该预印本 2023 年 4 月 24 日更新为 v3 并改名为 The Collatz Conjecture & Non-Archimedean Spectral Theory: Part I；无期刊引用信息。即：仅预印本。

22. 【丙】「用测度论证明 Collatz」的线索：figshare 预印本 30401173（原始记录标题为 The 2-Adic Dynamical System of the 3x+1 Problem: Ergodicity, Measure, and the Collatz Conjecture，作者 Maurizio Estefano Mendoza Martínez，2025 年 10 月 20 日发布，DOI 10.6084/m9.figshare.30401173.v1）本身并不声称证明：其摘要明确写「Our results are theoretical. They don't prove the conjecture outright」，只说反例「extremely rare」。—— 元数据经 figshare 官方 API 核对（HTTP 200）；网页直链返回 HTTP 202，未取到正文，故未读全文。附带线索：同一 DOI 在 ResearchGate 上的著录标题为「…Ergodicity, Invariant Measure, and a Measure-Theoretic Proof of the Collatz Conjecture」（2025 年 10 月），含「证明」字样，与 figshare 原始记录不符；该 ResearchGate 著录我未打开，仅凭检索结果，标注「未能核对」。从第 10 条的零测集论证看，任何「纯测度论证明 Collatz」的主张在逻辑上都需要额外机制。另据 Lagarias 注释书目第 126 条（已打开）：Metzger 1995 关于「正整数上唯一循环是平凡循环」的定理证明存在缺口，作者本人在补记中承认，这是本线附近一个已被作者自己承认的失败宣称。

## 当前的技术极限（记录值是多少、谁保持、为什么停在那里）

1. 定性天花板：2 进空间上的动力学已经完全解决（拓扑与测度共轭到移位，Bernoulli）。因此任何进一步的遍历论或测度论强化，都不会改变关于整数集的结论，因为 Z 可数、在 Z_2 中测度为零（Kontorovich、Lagarias 第 10 节；Akin；Rozier）。
2. 最强的「几乎所有」定理：Tao 2022（经同行评审）：对数密度 1 的 N 满足 Col_min(N) < f(N)，f 任意趋于无穷；定量的界是 C_δ ≪ exp(δ^{−O(1)})。保持者：Terence Tao。Tao 自己在 Remark 1.4 中说明，把这个结果强化为「存在绝对常数 C_0 使几乎所有的 Col_min ≤ C_0」很可能与整个 Collatz 猜想同等困难，超出该文方法。
3. 达到 1 的计数下界记录：π_a(x) ≥ x^{0.84}（a 不被 3 整除），保持者 Krasikov 与 Lagarias（2003，计算机辅助证明，线性规划最优值 γ = log_2 λ ≈ 0.84175）。此前链：0.643（Applegate、Lagarias 第 I 篇）→ 0.43（Krasikov 1989）→ 0.48（Wirsching 1993）→ 0.81（Applegate、Lagarias 第 II 篇）→ 0.84。是否有人超过 0.84：我未能核实（未找到）。
4. 从对数密度到自然密度：未跨过。Tao 的 Remark 1.16 明确指出，需要把 Prop 1.14 强化为整个随机仿射映射（而不只是偏移量）的细尺度混合。
5. 计算验证范围（并行记录，不属于本线定理）：所有 n < 2^71 已验证收敛（2025 年 1 月 15 日宣布），当前推进约到 2^75 × 2^60 ≈ 2^{71.02}；保持者 David Barina 的分布式项目。论文：Barina 2025, J. Supercomput. 81: 810（我未打开正文，仅打开项目页）。
6. 遍历域：> 0.96（Rozier，INTEGERS 19 (2019) #A8，已发表）。满测度仍是猜想。
7. 为什么停在这里——三条具体原因：

   (a) 共轭对整数全域不给信息。Z 零测；Φ 处处不可微，没有可利用的正则性；Bernstein 与 Lagarias 自己在原文中写道：他们证明的结果「与 3x+1 猜想没有任何直接关系」，因为共轭只给出 Φ ∘ S^k ∘ Φ^{−1} = T^k，而不涉及 Φ^k（k ≥ 2）。

   (b) 计算 Φ(x) 的复杂度。唯一已知的计算 Q(x) 的方式是知道 x 的整条轨道（Akin 原文明确写出这一点）；Rozier 给出的泛函方程（如 Q(2x+1) = 2Q(x) − 2^k + 1）只适用于正整数的一个密度 1/2 的子集，不构成算法。也就是说：共轭是一个「存在性编码」，而不是一个「可计算翻译」。

   (c) 方法对参数不敏感。Akin 的 τ_a（对任意奇 a）与 Kontorovich、Lagarias 的 T_5 表明：任何对所有奇 a 同时成立的论证都无法证明 3x+1 猜想，因为 5x+1 在整数上的（猜想）行为与 3x+1 完全不同。这是这一线的「反向筛选条件」。

## 未解决的缺口

1. 周期猜想（Φ 保持有理数，即 Φ(Q ∩ Z_2) = Q ∩ Z_2）未解；它蕴涵 T 在整数上无发散轨道，目前只有反向包含已证。
2. Fixed Point Conjecture（Φ 恰有 −1 与 1/3 两个奇不动点）未解；Bernstein 与 Lagarias 原文明确说「没有任何已知方法判定非有理奇不动点的存在与否」。
3. 「Φ 是否总共只有有限多个奇周期点」未知；对每个周期 2^j 的有限性（Finiteness Conjecture）也未解。
4. Q(x) 的有效计算法：对给定的正整数，没有任何已知方法在不遍历整条轨道的前提下算出 Q(x)；这直接封死了「把猜想变为对某个 2 进数做判定」的路线。
5. 自然密度版本与「绝对常数上界」版本：未解，且后者被认为与完整猜想同等困难（Tao Remark 1.4）。
6. 遍历域满测度（Rozier Ergodicity Conjecture）：未解；已发表的下界只到 0.96。
7. x^{0.84} 与线性增长（Applegate、Lagarias 更强猜想 π_a(x) > c_a x）之间的差距：没有任何已知机制可以跨越。
8. 数值验证只到 2^{71} 量级；对无穷多个整数不构成任何证明。

## 若要在这一线推进，必须跨过什么门槛

1. 必须造出「越过零测集」的桥梁：把 Z 的算术结构（序、整除、素因子）与被 Φ 打散后的符号动力学联系起来，且这个联系不能依赖任何「几乎处处」论证。纯测度与遍历路径在原理上被零测集论证封死（Kontorovich、Lagarias 第 10 节）。
2. 必须处理 Φ 的不可微性：所有基于光滑性的分析工具在 Φ 上失效。可行的方向要么绕开微分结构（例如只用 Φ_n 的分层置换结构与其算术解读），要么在保留乘法结构的代数载体上工作（ax+b 类共轭、polyadic 延拓、广义映射的遍历测度）。
3. 周期猜想（或其足够强的弱化）是必经之路：整数是有理数；若无法在有理点上控制 Φ，就无法把符号动力学信息翻译回整数。最低限度需要一个能判定 Φ(1) 或 Φ(Z+) 落在哪个集合中的判据。
4. 随机模型的「几乎必然」必须升级为「对所有整数」：这要求控制大偏差的尾部并与确定性的符号动力学相容。Tao 的 Syracuse 随机变量特征函数衰减（Prop 1.17）是当前唯一把随机模型变成定理的样本，其可升级性被 Tao 本人列为明确的技术门槛（Remark 1.16）。
5. 论证必须对 a = 3 敏感：由于 3x+1 与 5x+1 在 2 进整数上同构而在整数上猜想不同，任何对全部奇 a 成立的论证都不可能解决 3x+1 猜想。候选证明必须用到某种只对 a = 3 成立的数论事实（例如 3 < 2^2，或 log 3 / log 2 的具体数值）。
6. 若不追求证明 Collatz，这一线最现实的增量是：把周期猜想的已证方向做得更定量（刻画哪些有理数的像是有理数）、把遍历域测度下界从 0.96 推向 1（或构造非遍历集）、以及把 Tao 的对数密度升级为自然密度。

## 来源清单（全部 URL，逐条注明你是否亲自打开过）

已亲自打开（下载后抽文本逐段阅读）：

1. Bernstein & Lagarias, The 3x+1 Conjugacy Map（1996，作者预印本 PDF）https://dept.math.lsa.umich.edu/~lagarias/doc/bernstein.pdf —— 已打开（curl 下载 + pdftotext，读了全部 710 行）。
2. Bernstein, A non-iterative 2-adic statement of the 3N+1 conjecture（1994，出版社版）https://pure.tue.nl/ws/files/3370267/Metis219674.pdf —— 已打开（全文 220 行）。
3. Tao, Almost all orbits of the Collatz map attain almost bounded values（arXiv 版）https://arxiv.org/pdf/1909.03562 —— 已打开（读了定义、定理、Prop 1.11 至 1.17、Remark 1.4 与 1.16 所在段落）。
4. Rozier, Parity sequences of the 3x+1 map on the 2-adic integers and Euclidean embedding（arXiv v6，2025）https://arxiv.org/pdf/1805.00133 —— 已打开（读了第 3 至第 4 节、遍历域与周期部分、参考文献）；该文已发表版为 INTEGERS 19 (2019), #A8（DOI 10.5281/zenodo.10705023），其 PDF 我经卷目录页 https://math.colgate.edu/~integers/vol19.html 的取件表单（POST 到 cgi-bin/get.cgi）下载并抽取文本，核到「odd ergodic sets exceeds 0.48」「greater than 0.96」与「Conjecture 3. (Ergodicity Conjecture)」三处。
5. Kontorovich & Lagarias, Stochastic Models for the 3x+1 and 5x+1 Problems https://arxiv.org/pdf/0910.1944 —— 已打开（读了第 1、2、10 节与书目）。
6. Sinai, Statistical (3x+1)-problem https://arxiv.org/pdf/math/0201102 —— 已打开（读了摘要性的第 1 至第 3 节）。
7. Krasikov & Lagarias, Bounds for the 3x+1 problem using difference inequalities https://arxiv.org/pdf/math/0205002 —— 已打开（读了摘要、Theorem 2.2、Theorem 6.1）。
8. Applegate & Lagarias, Density Bounds for the 3x+1 Problem II（预印本）https://websites.umich.edu/~lagarias/doc/applegateII.pdf —— 已打开（读了引言、Theorem 1.1 与参考文献）。
9. Matthews, Some Borel measures associated with the generalized Collatz mapping（Colloq. Math. 63）https://matwbn.icm.edu.pl/ksiazki//cm/cm63/cm6327.pdf —— 已打开（正文与摘要）。
10. Lagarias, The 3x+1 problem: An annotated bibliography（arXiv:math/0309224）https://arxiv.org/pdf/math/0309224 —— 已打开（读了第 22、23、108、112、126 条等）。
11. Lagarias, 同书目第二部分（arXiv:math/0608208）https://arxiv.org/pdf/math/0608208 —— 已打开（读了第 102 至 104 条等）。
12. Akin, Why is the 3x+1 Problem Hard?（第三方镜像的全文 PDF）https://cdn.prod.website-files.com/6965196f8d9e2426b7998faf/69653caaaeaa37251abf72ee_2004-WhyThreeXisHard.pdf —— 已打开（通读第 1 至第 4 节）。注意：此为镜像副本，正式出处为 Contemp. Math. 356 (2004), 1 至 20，正式版我未打开。
13. Barina, Collatz 收敛性验证项目页 https://pcbarina.fit.vutbr.cz/ —— 已打开（经 DuckDuckGo 抓取；确认 2^71 与后续推进的最新状态、以及两篇论文的 DOI）。
14. Siegel, Syracuse Random Variables and the Periodic Points of Collatz-type maps（v1）https://arxiv.org/pdf/2007.15936v1 —— 已打开（摘要与目录）。
15. arXiv API 元数据查询（用于核实 Siegel 预印本的版本改名）http://export.arxiv.org/api/query?id_list=2007.15936 —— 已运行并读取返回。

只看到检索结果与元数据，正文未打开：

16. Bernstein & Lagarias 1996 的出版社页码页 https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/3x-1-conjugacy-map/6975BB4A8C46CF6842217043AAF9EC13 —— 未打开（搜索摘要确认卷期页与摘要）。
17. Tao 2022 的期刊页 https://www.cambridge.org/core/journals/forum-of-mathematics-pi/article/almost-all-orbits-of-the-collatz-map-attain-almost-bounded-values/1008CC2DF91AF87F66D190C5E01C907F —— 未打开（搜索确认 DOI 10.1017/fmp.2022.8 与 2022 年 5 月上线）。
18. Sinai 2003 的出版社页 https://onlinelibrary.wiley.com/doi/10.1002/cpa.10084 —— 未打开（搜索确认卷期页 56(7), 1016 至 1028）。
19. Krasikov & Lagarias 2003 的 Acta Arithmetica 页 https://www.impan.pl/en/publishing-house/journals-and-series/acta-arithmetica/all/109/3/81918/bounds-for-the-3x-1-problem-using-difference-inequalities —— 未打开（搜索确认页码 237 至 258、DOI 10.4064/aa109-3-4）。
20. Lagarias & Weiss, The 3x+1 Problem: Two Stochastic Models https://projecteuclid.org/journals/annals-of-applied-probability/volume-2/issue-1/The-3x--1-Problem-Two-Stochastic-Models/10.1214/aoap/1177005779.full —— 尝试打开失败（Incapsula 拦截，WebFetch 与 DuckDuckGo 抓取均失败）；另有 JSTOR 版本需订阅。
21. Lagarias, The set of rational cycles for the 3x+1 problem（Acta Arith. 56）https://www.impan.pl/en/publishing-house/journals-and-series/acta-arithmetica/all/56/1 —— 未打开（站内导航页抓到但无正文；镜像 PDF 尝试失败）。
22. Terras, A stopping time problem on the positive integers（Acta Arith. 30）https://www.impan.pl/en/publishing-house/journals-and-series/acta-arithmetica/all/30/3/101028/a-stopping-time-problem-on-the-positive-integers —— 未打开（页面抓到导航文字；matwbn 上的 Acta Arithmetica 扫描件无文字层，我下载了 10 余个候选文件均无法抽取文本）。
23. Everett, Iteration of the number theoretic function f(2n)=n, f(2n+1)=3n+2（Adv. Math. 25）—— 未打开（出版社需订阅）；其定理内容转引自 Kontorovich、Lagarias 的 Theorem 2.1 与 Rozier 的叙述。
24. Lagarias, The 3x+1 problem and its generalizations（Amer. Math. Monthly 92, 1985）—— 未打开（JSTOR 需订阅）；Theorem K、Q_∞ 与周期猜想均转引自 Bernstein 1994、Bernstein 与 Lagarias 1996、Kontorovich 与 Lagarias、Rozier（这些均已打开）。
25. Barina, Improved verification limit for the convergence of the Collatz conjecture（J. Supercomput. 81: 810, 2025）https://doi.org/10.1007/s11227-025-07337-0 —— 未打开正文（DOI 与标题取自项目页）。
26. figshare 预印本 The 2-Adic Dynamical System of the 3x+1 Problem https://figshare.com/articles/preprint/The_2-Adic_Dynamical_System_of_the_3x_1_Problem_Ergodicity_Measure_and_the_Collatz_Conjecture/30401173 —— 网页直链打开失败（HTTP 202，未取到内容）；改用官方 API 已核对元数据（标题、作者、发布日期、DOI、摘要），见下一行。
27. figshare API 端点 https://api.figshare.com/v2/articles/30401173 —— 已运行（HTTP 200，读取 JSON：标题、作者 Maurizio Estefano Mendoza Martínez、preprint、2025 年 10 月 20 日）。
28. arXiv API 端点 http://export.arxiv.org/api/query?id_list=1805.00133 —— 已运行（返回 Journal reference: Integers 19 (2019), article A8）。
29. Integers 卷 19 目录页 https://math.colgate.edu/~integers/vol19.html —— 已打开（HTTP 200，A8 条目标题、作者与 DOI 与 API 一致）。

补充说明（检索方法与勘误轮次）：本笔记的文献均由 curl 下载 PDF 后用 pdftotext 抽文本阅读；对关键公式与量词，再用 pdftoppm 把原书页面渲染成 PNG 直接读图比对（因为 Bernstein、Lagarias 1996 那份 PDF 的文本层会吞掉负号与「±」这类字形）；接口类元数据用 arXiv API 与 figshare API 核对。第二轮（引文复核后）我独立重验并更正了四处：一，式 (1.6) 的负号，渲染原书第 2 页确认 Φ(x) = −Σ_l 3^{−l} 2^{d_l}；二，周期猜想等价命题的量词应为 k ≡ ±1 (mod 6)，渲染原书第 3 页确认；三，Rozier 的遍历域结果已正式发表于 INTEGERS 19 (2019) #A8，故由「仅预印本」改列为已发表（arXiv API 的 Journal reference 字段与已发表版 PDF 双重确认）；四，Bernstein、Lagarias 1996 原文对保测与强混合只写「see [8]」，不出现「Theorem K」，该编号出自 Kontorovich、Lagarias 第 10 节。此外，不动点符号（x = −1 与 x = 1/3，渲染原书第 6 页图像确认）与 figshare 预印本的标题、作者、日期、摘要（官方 API 确认）也在本轮直接核对。凡未亲自打开的条目均在上表中标注，其内容仅以「转引」形式出现并注明转引来源。核对意见中我不同意的部分：无。
