# barriers

笔记状态：2026 年 10 月 18 日检索与核对。本笔记处理的研究线是「已知的证明障碍与死路」：哪些方法是**已经被写下来的定理**排除的、哪些是**被反复记录的经验教训**、哪些只是**我的推断**。可信度分级约定如下，每条关键结果都带标记：

1. 【同行评审】＝经期刊或会议论文集评审的定理或文章；
2. 【仅预印本】＝arXiv 或作者自印本，无评审记录；
3. 【已撤回或已驳斥】＝作者撤回、或经第三方指出错误并给出勘误者；
4. 【社群讨论】＝MathOverflow、博客、GitHub，非文献；
5. 【我的推断】＝我自己的论证或解读，不是文献结论。

本笔记只写「不要试什么」与「为什么」。正向的纪录与验证算法细节见同目录的 verification.md，不可判定性的族层面结果见 undecidability.md；本笔记只在必要处引用它们，不重复。

## 这条线在问什么

科拉茨猜想本身是一句具体的 Π⁰₂ 陈述（∀x∃i f^i(x) = 1）。这条研究线问的不是「猜想对不对」，而是下面这些问题：

1. 哪些**一般性的证明框架**已被证明无法奏效？例如：统一的归纳法、各类势函数与 Lyapunov 函数、「有限覆盖同余」推理、有限自动机判定、以及「几乎所有」型密度论证。
2. 哪些是**硬的不可能性定理**（不可判定性、无不动点、测度零、无界下降深度），哪些只是**当前技术天花板**（记录值停在哪里、为什么停在那里）？
3. 关键区分：不可能性定理里，有些约束的是**问题族**（广义 Collatz 的判定问题），有些约束的是**某类方法**（密度论证、势函数、有限自动机），**没有**一条约束单个 3x+1 猜想的可证性。把这三层混起来是本线最常见的错误（undecidability.md 已把第一层钉死，本笔记负责第二、三层）。
4. 哪些说法属于**被广泛讨论但未成文**的经验教训？这类内容我逐条标注来源与性质，不与定理混列。

## 关键结果

### 一、族层面的不可判定性（约束的是「统一方法」）

1. **康威 1972：广义 Collatz 迭代的判定问题不可判定。** 定理：对任意可计算函数 f，存在函数 g（g(n)/n 为取有理值的周期函数，在每个剩余类上 g(n) = a_i n + b_i），使得 g^k(2^n) = 2^{f(n)}，其中 k 是使 g^k(2^n) 为 2 的幂的最小正整数；推论：不存在算法，给定这样的 g 与 n，判定是否存在 k 使 g^k(n) = 1。—— 1972 年，J. H. Conway，Proc. 1972 Number Theory Conference（Univ. Colorado, Boulder），pp. 49 至 52。【同行评审（会议论文集）】PDF：https://gwern.net/doc/cs/computable/1972-conway.pdf （我亲自下载并用 PyMuPDF 抽取正文核对了定理与推论原文）。
2. **Kurtz 与 Simon 2007：广义 Collatz 问题 Π⁰₂ 完备。** 定理 1.4：给定 Collatz 函数 g，判定「对所有整数 x 都存在 i 使 g^i(x) = 1」是不可判定的；定理 1.5：集合 {g : range(g) = ω} 是 Π⁰₂ 完备的，其中 range(g) = {x : 存在 i 使 g^i(x) = 1}；定理 1.6（复述康威）：限制到形如 2^k 的输入，判定问题仍不可判定。—— 2007 年（预印本 2006 年 12 月 26 日），Stuart A. Kurtz、Janos Simon（芝加哥大学），TAMC 2007，LNCS 4484，pp. 542 至 553。【同行评审】作者主页预印本：https://people.cs.uchicago.edu/~simon/RES/collatz.pdf （我亲自下载并读第 1、2 节；该 PDF 无第 3 节正文）。
3. **对「统一方法」的约束（我的推断，由上述两条直接得出）**：任何「用一条统一定理覆盖一大类广义 Collatz 函数」或「用一个算法判定所有 Collatz 型映射」的路线不存在。这**不**排除单个 3x+1 猜想有证明，也不给出任何独立性结论；具体说明见 undecidability.md 关键结果第 14、15、16 条。

### 二、循环：下界、方法与它停住的地方

4. **Steiner：唯一的 1 循环是 {1,2}。** 结论：正整数的周期轨道中，唯一「恰好一个上升段紧接一个下降段」（circuit 型）的循环是平凡循环。—— 1977 年会议报告、1978 年论文集，R. P. Steiner，Proc. 7th Manitoba Conference on Numerical Mathematics and Computing，pp. 553 至 559。【同行评审（会议论文集）】我**未**打开原文；定理与年份来自 Lagarias 1985 年综述（https://www.cecm.sfu.ca/organics/papers/lagarias/paper/html/node8.html ，我亲自抓取该节全文）与其文献目录（https://arxiv.org/abs/math/0309224 ，第 158 条，我亲自读该 PDF）。Lagarias 1985 年综述对该结果有一句被反复引用的评语：这个定理「结论之弱与证明所用方法之强形成反差」——证明用的是 Baker 关于对数线性型的理论。这是本线上最早的「方法重、收获小」记录。
5. **Crandall：非平凡循环的周期大于 17985。** 结论：若 m > 1 且 C^k(m) = m（C 是去掉全部 2 因子的加速映射），则 k > 17985；方法为 log₂3 的连分数逼近。—— 1978 年，R. E. Crandall，「On the 3x+1 Problem」，Math. Comp. 32 (1978)，1281 至 1292，DOI: 10.1090/S0025-5718-1978-0480321-3。【同行评审】我经文本代理读取了 AMS 的 PDF 全文（https://r.jina.ai/https://www.ams.org/journals/mcom/1978-32-144/S0025-5718-1978-0480321-3/S0025-5718-1978-0480321-3.pdf ；AMS 直连返回 403 反爬页）。同文另有两条本线要用的结果：定理 (2.2)：sup T_m / m 无界（轨道的相对高度没有统一上界）；以及 qx+r 部分的结论（见第 27 条）。
6. **Eliahou：非平凡循环的元素个数至少 17 087 915。** 定理：任何非平凡循环必须至少含 17 087 915 个元素。—— 1993 年，Shalom Eliahou，Discrete Mathematics 118 (1 至 3)，45 至 56，DOI: 10.1016/0012-365X(93)90052-U。【同行评审】我亲自打开的是日内瓦大学存档页（给出官方摘要原文）：https://archive-ouverte.unige.ch/unige:12087 。精确结构（来自 Lagarias 文献目录第 53 条，我亲自读该 PDF）：周期 p = 301994A + 17087915B + 85137581C，A、B、C 为非负整数且 B ≥ 1、A 与 C 至少一个为 0；方法为 log₂3 的连分数展开，并且**以「猜想在 n < 2^40 内已验证」为输入**。
7. **Simons 与 de Weger：无非平凡 m 循环，m ≤ 68（发表版）／m ≤ 75（作者 2007 年更新版）。** 结论：定义 m 循环为含 m 个局部极小（即 m 个上升段）的循环；不存在 1 ≤ m ≤ 68 的非平凡 m 循环。—— 2005 年，J. L. Simons、B. M. M. de Weger，Acta Arithmetica 117(1)，51 至 70。【同行评审】发表版我**未**打开（仅经 Acta Arithmetica 著录信息与检索摘录核对，标注：发表版数字据检索摘录为 m ≤ 68）。作者更新版 v1.43（2007 年 7 月 31 日）我**亲自下载并读**：摘要写明「不存在 1 ≤ m ≤ 75 的非平凡 m 循环」，并给出 m = 76、77 的候选解（待外部计算排除），PDF：https://www.deweger.net/papers/%5b35a%5dSidW-3n+1-v1.43%5b2007%5d.pdf 。【仅预印本（作者自印更新版）】
8. **m 循环方法为什么停在这里（原文记录，非我的推断）**：Simons 与 de Weger 的框架分四步——由循环结构得 Λ = (K+L)log 2 − K log 3 的上界（对 K 指数增长）、由超越数论（Baker 型线性型）得 Λ 的下界（对 K 次指数）、两者比较得 K 与 L 的上界（对 m 指数增长）、再用连分数与格归约算 K、L 的下界（用于「小 m」）。原文指出：Simons 用来处理 2 循环的系数 d 在 m > 2 时「变为负」，上界失效，这就是他们必须换用新方法的原因；而「对中等大小的 m（直到 515 620）」，Diophantine 逼近技术只能改进上界，不能扩大排除范围。来源：https://www.deweger.net/papers/%5b35a%5dSidW-3n+1-v1.43%5b2007%5d.pdf （我亲自下载并读 1.1 至 1.5 节）。
9. **Hercher：无非平凡 m 循环，m ≤ 91（有勘误争议，见下条）。** 结论：m ≥ 92；并给出提高下一个门槛所需的验证范围。方法：把「k_i 的增长速率」与 T(n_i) 的倒数和结合起来，配合 log₂3 的连分数分母下界。—— 2023 年，Christian Hercher，「There are no Collatz m-Cycles with m ≤ 91」，Journal of Integer Sequences 26，文章 23.3.5。【同行评审】PDF：https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf （我亲自下载并通读要点）。
10. **【已撤回或已驳斥（部分）】**：Hercher 定理 21 的证明中有一处推导错误（由 Xinjun Wang 指出），期刊勘误（2026 年 6 月 14 日，我亲自下载并读全文两页）承认该处错误并给出一个用凸性/极点论证替换的证明：https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf 。与此同时，一个 Lean 4 形式化项目（2026 年 8 月 5 日创建，我亲自读其 README 与 SUMMARY）声称：论文从 m ≤ 82 走到 m ≤ 91 依赖的正是定理 21 中那一步，他们机器验证的主定理只到 **m ≤ 82**，并称 m ≤ 82 是「从论文中可靠引理能得到的诚实上限」；该 SUMMARY 未提及 Hercher 的勘误。仓库：https://github.com/PhilNorfleet/Hercher2023_lean （【社群讨论】，形式化本身自称 0 sorry、0 自定义公理，外部假设两条：X0 = 704·2^60 与 Simons 与 de Weger 的上界 K < 1.4784·m·δ^m）。另：arXiv 版（v3，2023 年 4 月 4 日，我亲自下载 PDF 核对）**仍含**那处有争议的推导，未随勘误更新：https://arxiv.org/abs/2201.00406 。我无法裁定勘误的替换论证是否正确（我不具备在此复核其全部细节的条件），因此本笔记把「m ≥ 92」标为**待裁定**：论文加勘误主张成立，形式化项目主张上限只到 82。
11. **Hercher 的下一个门槛与节省**：要证明非平凡循环至少含 K > 1.375 × 10^11 个奇数元素，只需验证到 1536 × 2^60 = 3 × 2^69（比旧方法所需范围少约 60%）；原文 Remark 30 同时说明：把该界再降低一个 2^60 单位会使计算时间增加约 1.5%，所以这个界「不能被合理地再降低」。来源：https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf 的 Corollary 29 与 Remark 30（我亲自读）。

### 三、密度与「几乎所有」路线的天花板

12. **Terras 1976／Everett 1977：密度为 1 的「下降」定理。** 结论：使某个迭代 T^k(n) < n 的正整数 n 具有自然密度 1（两人独立得到）。—— 1976 年，Riho Terras，Acta Arithmetica 30 (3)，241 至 252，DOI: 10.4064/aa-30-3-241-252；1977 年，C. J. Everett，Advances in Mathematics 25，42 至 45。【同行评审】Terras 原文我**未能打开**（impan.pl 与 matwbn 的 PDF 被 Anubis 反爬拦截）；该结论我据两处转引核对：Crandall 1978（第 5 条，定理 (2.1) 标注为 Everett）与 Lagarias 文献目录第 57 条（我亲自读）。Terras 的出版信息见 https://www.impan.pl/en/publishing-house/journals-and-series/acta-arithmetica/all/30/3/101028/a-stopping-time-problem-on-the-positive-integers （我抓取了该著录页）。**这条结果的教训**：密度为 1 的理论完全不触及密度为 0 的例外集，而猜想恰恰是关于例外集的（见第 16、19 条）。
13. **Krasikov 与 Lagarias 2003：π₁(x) ≥ x^0.84。** 结论：对每个不被 3 整除的固定 a，充分大的 x 下，小于 x 且其轨道经过 a 的整数至少有 x^0.84 个；方法：Krasikov 的差分不等式系统（mod 3^k）加计算机辅助的非线性/线性规划证明。—— 2003 年，Ilia Krasikov、Jeffrey C. Lagarias，Acta Arithmetica 109(3)，237 至 258。【同行评审】arXiv 预印本（2002 年 4 月 30 日）：https://arxiv.org/abs/math/0205002 ，PDF 我亲自下载并读摘要、定理 2.2 与定理 6.1；另读 Lagarias 主页的版本 https://websites.umich.edu/~lagarias/doc/krasikov.pdf 。
14. **密度指数的历史链（每条都出自可打开的原文或著录）**：Crandall 1978 给 c = 0.05（我读的 Crandall 原文未给数值，此数值出 Lagarias 文献目录第 47 条）；Sander 提到 0.30、Krasikov 用 k = 2 得 0.43、Wirsching 用 k = 3 得 0.48、Applegate 与 Lagarias 第一部分（树搜索）得 0.65、其第二部分（Krasikov 不等式，k = 9）得 0.81、Krasikov 与 Lagarias 2003 得 0.84。—— 1995 年，David Applegate、Jeffrey C. Lagarias，Math. Comp. 64，411 至 426（第一部分）与 427 至 438（第二部分），DOI: 10.1090/S0025-5718-1995-1270613-2（第二部分）。【同行评审】两篇预印本我**亲自下载并读**：https://websites.umich.edu/~lagarias/doc/applegateI.pdf 、https://dept.math.lsa.umich.edu/~lagarias/doc/applegateII.pdf 。
15. **「分裂法指数收敛于 1 以下」——方法上限的第一手记录。** Applegate 与 Lagarias 第二部分原文写道：γ 的值看起来正收敛到一个小于 1 的极限；他们实验的「极限分裂」显示变量消去法有其限度；并把 π_a(x) ≥ x^{1−ε} 记为 **Krasikov 猜想**（Krasikov 本人猜测足够大的 k 可以从差分不等式推出它），原文明说「这似乎无疑是真的」，但他们没有证明。—— 1995 年，同上第二部分，§3、§4；PDF：https://dept.math.lsa.umich.edu/~lagarias/doc/applegateII.pdf （我亲自读原文该段）。【同行评审】
16. **Krasikov 与 Lagarias 的「希望」表述（不是定理）**：原文说，人们希望借助**参数 λ 任意大**的线性规划族 LNT_k(λ)，以及对这类线性规划「可行解集结构」的更好理解，最终证明形如 π₁(x) > x^{1−ε} 的界（同文明确该参数满足 1 ≤ λ ≤ 2）。—— 2002 年，同上预印本（我亲自读原文引言末段；被取大的量是 λ 而不是下标 k，此处于 2026 年 10 月 18 日据引文核对意见重查原文后更正）。【仅预印本／原文表述为「希望」，不是已证结果】这是本线最关键的「死路」之一：密度路线当前被卡在 Krasikov 猜想上，而它比猜想本身弱得多却仍未证。
17. **Tao 2019／2022：几乎所有轨道达到几乎有界的值。** 定理：对任意满足 f(N) → ∞ 的函数 f，几乎所有 N（对数密度意义下）都有 Col_min(N) < f(N)。方法：Syracuse 映射、3 进循环群上斜随机游走特征函数的高频估计、二维更新过程与三角形并集的相互作用。—— 2019 年预印本、2022 年发表于 Forum of Mathematics, Pi（第 10 卷，DOI: 10.1017/fmp.2022.8，该 DOI 经 Crossref 核对）；Terence Tao。预印本：https://arxiv.org/abs/1909.03562 （我亲自下载 PDF 并读摘要、定理 1.3、Remark 1.4）。【同行评审】
18. **Tao 明确写下的天花板（我读到的原文）**：把结论加强为「存在绝对常数 C₀ 使几乎所有 N 有 Col_min(N) ≤ C₀」这个问题「很可能与整个科拉茨猜想一样难，并且超出本文方法的范围」；他还说明：只要能造出一条永不降到 C₀ 以下的轨道（例如存在无穷多周期轨道或一条无界轨道），概率启发就会给出反例性的猜测；本文的论证给出的常数形如 C_δ ≪ exp(δ^{−O(1)})，可以设想与数值验证结合证明猜想对正对数密度集成立，但「把对数密度换成自然密度」只是「可信的改进方向」，尚未做到。—— 同上 Remark 1.4（我亲自读原文）。【同行评审（文章内的自我限制陈述）】
19. **Tao 关于「局部时间控制」与 2 进测度零的两处公开表述**：其一（2019 年论文与博客）：通常只能建立「局部时间」结果，把轨道控制到约 log n 的小倍数步；要一路降到有界状态，需要「（几乎）全局时间」的结果。其二（2011 年博文）：把整数推广到 2 进整数后，Haar 测度是不变且遍历的，由遍历定理可证「随机 2 进整数」的轨道偶数步与奇数步各占一半；但这几乎不说明 N 上的动力学，因为 N 是 Z₂ 的**测度零**子集；他还举单位圆上 nα 的例子：遍历理论说几乎所有点均匀分布，但具体一点（等价于 π 的数字是否均匀分布）仍然完全无法处理。—— 2019 年博文：https://terrytao.wordpress.com/2019/09/10/almost-all-collatz-orbits-attain-almost-bounded-values/ ；2011 年博文：https://terrytao.wordpress.com/2011/08/25/the-collatz-conjecture-littlewood-offord-theory-and-powers-of-2-and-3/ （两篇我都亲自抓取并读原文段落）。【社群讨论（博客），但作者与结论均为专家本人】同篇 2019 年博文另有一句：为所有 n 证明猜想「仍超出当前技术」，它「基本上至少与 Baker 定理一样难」。

### 四、2 进结构：不是障碍，但也不是武器

20. **Bernstein 与 Lagarias 1996：共轭映射把 Collatz 迭代变成移位，但帮助不了证明。** 定理与记录：存在唯一的（Φ(0) = 0 的）同胚 Φ 使 Φ∘S∘Φ⁻¹ = T（S 是 2 进移位）；T 保持 2 进测度、强混合、且是 Bernoulli 的；Φ 对 2^n 取模诱导 Z/2^n Z 上的置换 Φ_n，其阶为 2^{n−4}（n ≥ 6）；猜想的一个等价形式是 Z⁺ ⊆ Φ(⅓Z)；Φ 与 Φ⁻¹ 在 Z₂ 上处处不可微（该结果作者引 Müller 1991，以及 Bernstein 1994 的另一篇「3x+1 的非迭代 2 进表述」）。—— 1996 年，Daniel J. Bernstein、Jeffrey C. Lagarias，Canadian J. Math. 48，1154 至 1169，DOI: 10.4153/CJM-1996-060-X。【同行评审】我都亲自读了 PDF：作者重排版 https://cr.yp.to/papers/3x1conjmap-19960215-retypeset20220326.pdf 与 Lagarias 主页版 https://websites.umich.edu/~lagarias/doc/bernstein.pdf 。
21. **该论文自己写下的「为什么这条线帮不上忙」**（我读到的原文）：映射的对偶只把 T 的 k 次迭代与 S 的 k 次迭代相连（Φ∘S^k∘Φ⁻¹ = T^k），这个关系对 k ≥ 2 **不含** Φ 的迭代；因此「本文证明的结果与原猜想没有直接关联」；只有当问题变成关于 Φ 迭代本身（如他们讨论的周期性猜想的意义下）时，共轭结构才可能有信息量。—— 同上论文第 1 节末段；PDF：https://cr.yp.to/papers/3x1conjmap-19960215-retypeset20220326.pdf （我亲自读）。
22. **Lagarias 2010 年综述的第一手表述（本线最常被引用的两段）**：其一：「3x+1 问题关心的是迭代这个函数在整数集 Z 上的行为，而 Z 是 Z₂ 的稠密子集，具有 2 进测度零。困难就在于去寻找并理解这些迭代限制到 Z 上时出现的非随机规律」；同页还有一句被反复引用的总结：数学论证利用的是「结构的存在，而不是它的缺失」。与之等价的完整表述早见于 1985 年综述的结论一节（见第 35 条）。其二：困难有两条根本来源——(a) 要排除发散轨道，须先证明迭代具有某种**显式的伪随机性质**（这是一个公开的硬问题）；(b) 要排除**极长的非平凡循环**，而这「据目前已知的数论方法看来无法逼近」。—— 2010 年，Jeffrey C. Lagarias，「The 3x+1 Problem: An Overview」，收入 The Ultimate Challenge: The 3x+1 Problem（AMS），pp. 3 至 29。预印本：https://arxiv.org/abs/2111.02635 （我亲自下载 PDF 并读 §6.3、§7）。【同行评审（文集章节）】
23. **Lagarias 在 §7 为「非计算不可」留的余地（对判断「独立性」很重要）**：他明确说 3x+1 本身是否不可判定「目前未知，而且没有已知方法能着手处理这个问题」（此句在 §6.3）；而在 §7 中他认为 3x+1 不太可能复杂到能编码通用计算机（三条理由：它太简单、停机前的最大值函数 F(n) 是递归的、存在有限可加不变测度且在该测度下完全混合），并紧接着警告：这不排除在「测度零的薄集」上编码通用机，康威 1972 年的编码正是把不可判定性放在一个极薄的整数集上。—— 同上综述 §6.3（不可判定性一句）与 §7（三条理由、薄集告诫与 1972 年编码一句）；我亲自读全文并用文本检索核对了各段落所属小节。〔2026 年 10 月 18 日据引文核对意见更正：原笔记把三条理由等一并记为 §6.3「同页」，实为 §7（预印本第 18 至 19 页）。〕【同行评审；其中的判断是作者的评估，不是定理】

### 五、势函数、归纳法与符号依赖性：三条硬约束

24. **没有有界的下降深度：任何「每步必降」的势函数、任何固定深度的下降筛都不存在。** 事实：对每个 k，剩余类 n ≡ −1 (mod 2^k) 中每个数的前 k 个加速步全是奇步，因而前 k 步严格上升（T(x) = (3x+1)/2 > x）。取 n = 2^k − 1 即得实例。我用自己的脚本做了两组核验：对 k = 1 至 11，在剩余类 n ≡ −1 (mod 2^k) 的每个类中抽查 40 个成员，前 k 步全为奇步；对 k = 1 至 15，同样抽查的成员前 k 步的值都严格高于起点。【我的推断＋本地计算核验】文献侧的支持：Hercher 2023 的引理 8（「n, Cn, …, C^{k−1}n 全为奇数 ⟹ 2^k 整除 n+1 且 n ≥ 2^k − 1」，我读自其 PDF：https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf ）；以及 Simons 与 de Weger 原文对 Steiner 证明的重述（「存在从 x₀ 起的 k 个连续奇数蕴含 x₀ = a·2^k − 1 ≥ 2^k − 1」，我读自其 PDF：https://www.deweger.net/papers/%5b35a%5dSidW-3n+1-v1.43%5b2007%5d.pdf ）。**推论（我的推断）**：任何「把 N 用有限个剩余类覆盖、并对每个类证明其成员在固定步数内降到自身以下」的证明形式**不可能存在**——取步数上限 D 与覆盖的模 M，令 k > D，则类 n ≡ −1 (mod 2^k) 中的数在前 k 步都不下降，与「覆盖完备且每个类有固定下降深度」矛盾。这精确刻画了「有限覆盖同余」这一路线的哪一种形式是死的（更强的覆盖形式——例如允许「归约到已验过的小数」——不被这个论证排除，这一点我未在文献中找到成文的不可能性定理，标注为缺口）。
25. **证明必须用到正性与常数 3、1 的特殊性：负整数上猜想为假。** 事实：T 在整数上有三个非平凡循环：{−1}（周期 1）、{−5, −7, −10}（周期 3）、从 −17 起的 11 元循环（−17, −25, −37, −55, −82, −41, −61, −91, −136, −68, −34）。我用自己的脚本枚举了负整数直到 10^5 内的种子，确认这三个循环。【我的计算核验】文献侧：Lagarias 1985 年综述原文写「允许负整数时存在别的循环：从 n = −1 起周期 1 的循环，从 n = −5 与 n = −17 起长度分别为 3 与 11 的循环」，并指出「这些循环加上从 0 与从 1 出发的循环构成整数上全部循环」是 Böhm 与 Sontacchi 的**猜想**（未证）。来源：https://www.cecm.sfu.ca/organics/papers/lagarias/paper/html/node8.html （我亲自抓取）。【同行评审（1985 年综述）】教训：任何对映射的代数形式有效、但不区分 n > 0 与 n < 0 的论证，必然失败。
26. **证明必须用到常数 3 与 1：5x+1 上猜想为假。** 事实：在加速映射 C₅(x) = (5x+1)/2^{e} 下，13 → 33 → 83 → 13 构成非平凡循环；我用自己的脚本验证了该循环。【我的计算核验】文献侧：Crandall 1978 原文（我读全文）写道：对 qx+r 问题，r > 1 的情形可平凡证明「永远不会到 1」（取 m ≡ 0 mod r），而 q = 5 由 m = 13 的循环 {33, 83, 13, …} 解决，q = 181 由 m = 21 的循环解决，q = 1093 由「没有高度 2 的数」解决；这三种是当时已知的全部 q；并指出对奇 q > 3，启发式给出 log(C_q(m)/m) ≈ log(q/4) > 0，故预期发散，但「连一个无界轨道是否存在于任何一个 qx+1 问题中都还不知道」。—— 1978 年，R. E. Crandall（同第 5 条）。【同行评审】
27. **相对高度的无界性（对「简单势函数」的正面否定）**：Crandall 1978 定理 (2.2)（我读原文）：当 m 遍历正整数时，sup T_m / m 无界。（即：不存在常数 c 使所有轨道的最高点都 ≤ c·m。）—— 同第 5 条；PDF 经文本代理读取：https://r.jina.ai/https://www.ams.org/journals/mcom/1978-32-144/S0025-5718-1978-0480321-3/S0025-5718-1978-0480321-3.pdf 。【同行评审】配合第 24 条，可以给出「不要试」的清单第一条：不要试图构造形如「每步下降固定的比例」或「轨道高度被 m 的固定倍数控制」的势函数。

### 六、有限自动机与覆盖同余

28. **Shallit 与 Wilson：循环中「用了 i 次 3x+1 的数」是 2 自动集，但这不判定猜想。** 定理 3.1：对每个 i ≥ 0，集合 S_i = {n : n 的轨道在到达 1 前恰好使用 i 次映射 x ↦ 3x+1} 是 2 自动的（即其二进制表示构成正则语言）。—— Jeffrey Shallit、David Wilson，「The 3x+1 problem and finite automata」，Bulletin of the EATCS，No. 46，182 至 185。【同行评审（学会通报短文）】PDF：https://cs.uwaterloo.ca/~shallit/Papers/wilson.pdf （我亲自下载并读全文）。**年份注**：Shallit 自己的论文页标为 1992 年 2 月，Lagarias 文献目录第 155 条标为 1991 年（两者不一致，且 No. 46 的期号一致；我未能裁定哪个年份对，如实并列）。
29. **为什么自动机路线停在这里（我的解读，非原文定理）**：S_i 是**一族**自动集，下标 i 无界；猜想等价于 N = ∪_i S_i，而对给定的 n 判定「存在 i 使 n ∈ S_i」正是逐个 n 的原问题。固定 i 时可判定，且不依赖任何猜想；**没有**一个有限自动机判定并集。原文还记录了两个技术障碍（3n+1 需要按最低位优先逐位计算、表示长度会变长），他们用反向表示与进位状态克服了它们——这说明困难不是「进位」本身，而是 i 的无界性。【我的推断】我检索未找到「并集非自动」或「3x+1 判定问题不可由有限自动机解决」的成文定理（原因是并集若是全体自然数它就是自动集）；这一线的不可能性只能以「一致性问题」的形式陈述，属缺口。
30. **对照：自动机方法真正适用的地方是「所有乘数共享同一个底」的仿射系统。** Klarner 1988 证明：若一组仿射映射形如 f_i(x) = m^{e_i} x + a_i（共同底 m ≥ 2），则由有限种子集生成的闭包是 m 可识别（即 m 自动）的；而 Collatz 映射同时混用 2 与 3，落在这个框架之外。Klarner 在文中还记录：对 Erdős 提出的系统 {2x+1, 3x+1, 6x+1} 与种子 {1}，该集合「看不出结构」，且 Erdős 证明它不含无穷算术级数。—— 1988 年，David A. Klarner，Discrete Applied Mathematics 21(3)，207 至 214。我**未**打开原文；以上转引自 Lagarias 文献目录第 98 条（我亲自读该 PDF 的该条）。【同行评审；我读的是转引】
31. **覆盖同余的另一个层次：康威的编码表明「分剩余类的仿射迭代」这个一般框架本身不提供任何结构性保护。** 广义 Collatz 函数按每个剩余类指定一个仿射映射，而康威 1972（第 1 条）已经把任意计算编码进这样的函数，Kurtz 与 Simon 把复杂度钉在 Π⁰₂ 完备（第 2 条）。教训（我的推断）：任何只使用「函数按剩余类分段仿射」这一般性的论证，最多能得到族层面的结论；要证 3x+1，必须用上 2 与 3 的算术特殊性（与第 25、26 条一致）。我**未**找到「不存在有限覆盖同余证明」形式的成文定理；第 24 条给出的是我自己对其中一种形式的排除。来源：https://gwern.net/doc/cs/computable/1972-conway.pdf 与 https://people.cs.uchicago.edu/~simon/RES/collatz.pdf （两篇我都亲自下载并读）。

### 七、被撤回或被驳斥的宣称（供避坑）

32. **Opfer 2011 的解析路线宣称：由作者本人撤回。** 事实：Gerhard Opfer 用 Berg 与 Meinardus（1994、1995）的两个作用于单位圆盘上全纯函数空间的线性泛函方程，宣称证明了「方程组的解空间 K 恰为二维的 Δ₂」从而证明科拉茨猜想；汉堡大学预印本（Hamburg Beiträge zur Angewandten Mathematik，Nr. 2011-09，2011 年 5 月）首页附作者说明（2011 年 6 月 17 日）：「第 11 页上『所有层中所有顶点 (2n, l) 恰好一次包含所有偶数 2n ≥ 6』的推理被证明是不完整的。因此『科拉茨猜想为真』的陈述必须（至少暂时）撤回。」—— 我亲自下载并读该预印本 PDF（含该作者说明）：https://preprint.math.uni-hamburg.de/public/papers/hbam/hbam2011-09.pdf 。【已撤回】这条线的后续（负起始值的解析处理）由 Lothar Berg 与 Gerhard Opfer 于 2013 年在 Computational Methods and Function Theory 发表（卷 13，225 至 236 页，DOI: 10.1007/s40315-013-0017-z），其摘要明确「3n−1 问题仍未解决」；该文正文我**未**打开（作者、卷页与摘要结论据 Crossref 著录核对，非全文阅读）。〔2026 年 10 月 18 日据引文核对意见补上合著者 Gerhard Opfer，原文曾误记为 Lothar Berg 独著。〕教训（我的推断）：把猜想归约为「某个泛函方程解空间恰为低维」是可行的路线骨架，但证明「恰为」的那一步（计数/铺满论证）是本线上反复出事的地方。
33. **需要避开的未评审宣称（我提请只把它们当作待核实的宣称）**：检索中我遇到两类本笔记不采用的材料。其一，声称已完整证明猜想的预印本，例如 2025 年 12 月 18 日发布于剑桥大学出版社预印本平台 Cambridge Open Engage 的「All orbits of the collatz map attain the trivial cycle 4 2 1」（作者 Dylan Motimba，DOI: 10.33774/coe-2025-z482f，仅预印本、我未阅读）。其二，声称把 Tao 的结果从对数密度改进为自然密度的 2026 年 8 月 19 日 SSRN 预印本「Polylogarithmic Descent for Almost All Collatz Orbits in Natural Density」（作者 Idris Ali Shaik，DOI: 10.2139/ssrn.7290240，仅预印本、我未阅读），它对应的正是 Tao 论文 Remark 1.16 留下的公开方向，因此值得留意但不应作为结论引用。此外，vixra.org 上的循环下界预印本、性质不明的 collatz-lab.org 形式化项目，以及论坛上以「DFA 编码循环障碍」为名的评论，也不构成文献；本笔记不采用它们作为任何论据。以上是避坑提示，不是对它们的评价（我未逐一核对内容）。

### 八、经验教训（未成文，但被反复写下来）

34. **Erdős 的两句话（被引用最多、最常被当作「不要试」的根据）**：「数学还没有为这样的问题做好准备」（Lagarias 1985 年综述摘要页，我亲自抓取：https://www.cecm.sfu.ca/organics/papers/lagarias/ ）；以及在对话中说的「Hopeless. Absolutely hopeless.（没希望，绝对没希望）」，Lagarias 加注解释其含义是「没有任何已知的方法有希望解决这个问题」（Lagarias 2010 年综述 §10，我读预印本）。【同行评审来源中的转述】
35. **Richard Guy 的告诫与 Lagarias 的「结构悖论」**：Lagarias 2010 年综述 §10 引 Guy〈Unsolved Problems in Number Theory〉的原话作为最谨慎的建议：「Don't try to solve these problems!」；1985 年综述的结论一节则写下本线最完整的「方法为什么都不奏效」表述（我亲自抓取原文）：「困难似乎在于它是一个确定性过程却模拟随机行为。我们面对两难：一方面，问题有多大结构，我们就能分析多少——然而恰恰是这种结构似乎阻止我们证明它行为随机；另一方面，问题若真的无结构、随机，我们就无从分析，也就无法严格证明任何东西。……现有的数论与遍历论一般方法似乎都触及不到 3x+1 问题；在这个意义上它当前看来是棘手的（intractable）。」—— https://www.cecm.sfu.ca/organics/papers/lagarias/paper/html/node15.html （我亲自抓取该节全文）。【同行评审（1985 年 AMM 综述）】
36. **「低飞轨道」的社群表述（与第 19、24 条互为印证）**：MathOverflow 问题 197959 下得分最高的回答（作者 Lucia，2015 年 2 月 20 日）写道：对任意的初始步数，「只要看模 2 的大幂的剩余类就能看到任意多步的独立行为」，问题的症结是这种独立行为大致会持续到最后、使迭代降下来，而这一点恰恰很难证明；同问题下 Stefan Kohl 的回答认为「若序列收敛，用初等方法证明这一点看来是没希望的」，并引 Wirsching 2003 年的工作。—— https://mathoverflow.net/questions/197959/a-question-on-collatzs-conjectureproportion-of-low-flying-orbits （我亲自抓取页面，并另经 Stack Exchange API 核对了回答者与得分）。【社群讨论】
37. **「未成文教训」汇总（我的整理，每条都能追溯到上面某条）**：不要试图构造单调下降的势函数（第 24、27 条）；不要指望用密度论证覆盖全体（第 12、13、17 条）；不要指望遍历论（它是关于测度一的，而 N 是测度零，第 19、22 条）；不要指望有限自动机给出统一判定（第 28、29 条）；不要用对符号不敏感的代数论证（第 25 条）；不要用对常数不敏感的论证（第 26 条）；不要相信「把定理 21 那一步跳过就行」式的局部修补（第 10 条）；不要把广义不可判定性读成原问题不可判定（第 3 条）。

## 当前的技术极限（记录值是多少、谁保持、为什么停在那里）

编号说明：本节的 1 至 10 只在本节内有效；本节与下文引用的「第 N 条」一律指「关键结果」一节的编号，引用其他笔记时写明其文件名。

一、全区间验证（本线只从「它能证明什么」的角度记录）
1. 记录值：所有小于 2^71 ≈ 2.361 × 10^21 的正整数都到达 1（2025 年发表，David Barina）。详细记录链、算法与「为什么停在那里」见 verification.md 第 1、2、3、10 条与那里的来源清单。
2. 本线补充的逻辑天花板：（a）任何有限验证都是单称命题的合取，不构成全称命题；广义不可判定性（第 1、2 条）只约束统一算法，不给出原问题的不可判定性；（b）由第 24 条，任何固定下降深度的覆盖都不可能穷尽 N，所以「用几类剩余类一次扫完」的形式在原理上就不存在，验证只能靠逐层加深、向外推界。

二、循环（两条独立的记录）
3. 周期下界：任何非平凡循环至少 17 087 915 个元素（Eliahou 1993，第 6 条）；这个数字**依赖**于当时的验证界 2^40，且依赖 log₂3 的连分数。
4. 段数下界（m 循环）：论文记录是 m ≥ 92（Hercher 2023 ＋ 2026 年勘误，第 9、10 条）；机器验证的记录是 m ≤ 82 被 Lean 形式化排除（第 10 条）。这是本线上**当前唯一一处「记录本身有争议」**的地方，我把两个数字并列，不取其一。
5. 下一个门槛：K > 1.375 × 10^11 个奇数元素只需验证到 3 × 2^69 = 1536 × 2^60（Hercher Cor. 29），这已经被 Barina 的 2^71 覆盖（我核对：3 × 2^69 < 2^71）；再往上的门槛需要 2^75 级验证与新的 Diophantine 估计（后者见 verification.md 第 7 条所引的 2026 年预印本）。
6. 为什么停在那里：（a）方法上，Simons 与 de Weger 的框架给出的是「对 m 指数增长的界 + 计算机搜索」，每个新 m 都要重算，且依赖验证界与 log₂3 的逼近质量（第 7、8、11 条）；（b）结构上，非平凡循环的存在性问题与「log₂3 的极好有理逼近」绑定，而后者只能逐项检查连分数（第 6、8 条）；（c）我不曾找到任何「一次性排除所有 m」的方法记录，也找不到任何来源声称有这样的方法。

三、密度
7. 记录值：x^0.84（Krasikov 与 Lagarias 2003，第 13 条）；与此对等的是一条**未被证明的猜想**（Krasikov 猜想：x^{1−ε}，第 15、16 条）。
8. 为什么停在那里：Applegate 与 Lagarias 的实验记录显示分裂法的指数收敛于 1 以下（第 15 条）；Krasikov 与 Lagarias 的「希望」表述说明差距在于对差分不等式族的全局结构理解（第 16 条）；Tao 的路线（第 17、18 条）用完全不同的机制把「几乎所有」推到「几乎有界」，但明确写出「常数界」（即猜想的几乎处处形式）超出其方法。

四、判定性与证书
9. 广义问题：Π⁰₂ 完备（Kurtz 与 Simon，第 2 条）。原问题：无任何判定性或独立性结果（Lagarias 2010 §6.3 明说未知且无已知方法；undecidability.md 的关键结果第 16 条与其未解决缺口第 1 条记录了同一结论与我的检索证据）。
10. 证书结构（我的推断）：猜想是 Π⁰₂ 语句；若为假且反例是循环，则存在有限验证；若为假且反例是发散轨道，则「永不下降到某界」不是任何有限计算能确证的对象——不存在已知的有限反例证书形式。这一条没有文献来源，是我的推理，标注。

## 未解决的缺口

1. **「几乎所有」到「所有」的跨越**：没有任何已知技术把一个密度界升级为全称（第 12、17、18 条；Tao 明说常数界版本超出其方法）。Tao 论文 Remark 1.16 留下的**明确公开方向**是把对数密度升级为自然密度；我记录到一条 2026 年 8 月的未评审预印本宣称完成了这一步（第 33 条，我未核对），它目前应视为待核实。
2. **发散轨道**：无法排除；Lagarias 指出其阻碍在于需要先证明迭代具有显式伪随机性质，而这本身没有已知方法（第 22 条）。
3. **任意长的循环**：无法排除；方法只能逐 m、逐周期地排除，且每个新界都要新的数值输入（第 7、8、11 条）。
4. **密度路线的最后一跳**：Krasikov 猜想（x^{1−ε}）未证，且没有来源说明它是否真的能由差分不等式得到（Krasikov 与 Lagarias 只说「希望」）（第 16 条）。
5. **m 循环记录本身的争议未裁定**：Hercher 的勘误证明与 Lean 形式化项目的 m ≤ 82 宣称并存；arXiv 版未更新（第 10 条）。这是我能精确指出的、当前最值得第三方复核的一处。
6. **有限自动机路线缺一致性定理**：没有「并集非自动」或「判定问题不可由自动机解决」的成文结果，原因也清楚（并集可能是全体，而全体是自动的），所以只能以一致性问题形式陈述（第 29 条）。
7. **覆盖同余：我只排除了「有界下降深度」形式**（第 24 条）；允许「归约到已验过的小数」的更一般覆盖是否有不可能性定理，我未找到（第 31 条标为缺口）。
8. **Terras 1976 与 Everett 1977 的原文我没能打开**（前者的 PDF 被反爬拦截，后者我未找到开放版本），其定理内容我据 Crandall 1978 与 Lagarias 文献目录两处转引核对；Berg 与 Opfer 2013 的正文我未打开（仅 Crossref 著录）。这是我本轮的核对缺口（第 12、32 条）。
9. **Akin 2004「Why is the 3x+1 problem hard?」我未能阅读**（AMS 付费墙；Contemporary Mathematics 356，1 至 20，DOI: 10.1090/conm/356/06495）。它与本线高度相关（Akin 是「为什么难」的专门文章），我把它列为**未能核对**，不作为论据。

## 若要在这一线推进，必须跨过什么门槛

1. **要打破密度天花板**：证明 Krasikov 猜想（对任意 ε > 0 的 x^{1−ε} 界），或说明为什么差分不等式族给不出它；再往前，需要一条把「几乎所有」变成「所有」的新机制（第 16、18 条）。
2. **要打破循环天花板**：给出关于 log₂3 的逼近的**一致**结果（处理所有 m，而非逐个 m），或找到不依赖连分数的循环排除法；同时需要验证界继续外推以给更高的数值输入（第 6、8、11 条）。
3. **要排除发散轨道**：必须先有一个能证明「轨道在受控步数内具有显式伪随机性质」的定理；Tao 的「局部时间到全局时间」升级需要一个在 2 进与实数两侧都受控的不变量（第 18、19、22 条）。
4. **要让任何有限覆盖同余论证成立**：必须放弃「固定下降深度」，即把「下降」换成某种允许步数无界的新证书形式（第 24 条说明为什么固定深度不可能，同时说明这不是文献定理而是我的论证）。
5. **要让自动机或有限状态方法成立**：需要给出对 i 一致（或对可达性）的有限描述；目前只有「每个固定 i 一个自动机」的结果（第 28、29 条）。
6. **任何路线都必须满足的三条硬约束**：用到正性（第 25 条）、用到常数 3 与 1 的特殊性（第 26 条）、不依赖有界上升幅度或有界下降深度（第 24、27 条）。
7. **要判断「猜想是否独立于 ZFC/PA」**：目前没有任何一方结果；这是本线与 undecidability.md 共同的空白，且康威 2013 年文章明确表示「这类问题可能不可判定，并且其不可判定性本身不可证」，但他讨论的是**相似游戏**（24 个线性函数的游戏、FRACTRAN），不是 3x+1 本身；把两者混同是本线最需要避免的过度解读（第 23 条与 undecidability.md 的关键结果第 16 条）。

## 来源清单（全部 URL，逐条注明是否亲自打开）

已亲自打开（附方式）：
1. https://gwern.net/doc/cs/computable/1972-conway.pdf —— Conway 1972（不可判定性定理与推论）。已下载并用 PyMuPDF 抽取正文核对。
2. https://people.cs.uchicago.edu/~simon/RES/collatz.pdf —— Kurtz 与 Simon 预印本（定理 1.4、1.5、1.6）。已下载并读第 1、2 节（PDF 无第 3 节正文）。
3. https://www.cecm.sfu.ca/organics/papers/lagarias/ —— Lagarias 1985 年综述摘要页（Erdős「数学还没有准备好」原句）。已抓取 HTML。
4. https://www.cecm.sfu.ca/organics/papers/lagarias/paper/html/node8.html —— 1985 年综述「存在非平凡循环吗」一节（负整数循环、Böhm 与 Sontacchi、定理 H、定理 I、定理 J 与其「方法强、结论弱」评语）。已抓取并转文本通读。
5. https://www.cecm.sfu.ca/organics/papers/lagarias/paper/html/node9.html —— 同综述「是否存在发散轨道」一节。已抓取。
6. https://www.cecm.sfu.ca/organics/papers/lagarias/paper/html/node10.html —— 同综述「与遍历论的联系」一节。已抓取。
7. https://www.cecm.sfu.ca/organics/papers/lagarias/paper/html/node11.html —— 同综述「问题的推广」一节。已抓取。
8. https://www.cecm.sfu.ca/organics/papers/lagarias/paper/html/node12.html —— 同综述「算法可判定性问题」一节（康威定理 O 的转述）。已抓取。
9. https://www.cecm.sfu.ca/organics/papers/lagarias/paper/html/node13.html —— 同综述「几乎所有整数有有限停止时间」一节。已抓取。
10. https://www.cecm.sfu.ca/organics/papers/lagarias/paper/html/node15.html —— 同综述结论一节（结构悖论全文）。已抓取并转文本通读。
11. https://arxiv.org/abs/math/0309224 —— Lagarias「The 3x+1 Problem: An Annotated Bibliography (1963 至 1999)」。已下载 74 页 PDF 并检索、阅读第 16、47、53、57、58、98、135、137、155、158、159 等条目。
12. https://www.deweger.net/papers/%5b35a%5dSidW-3n+1-v1.43%5b2007%5d.pdf —— Simons 与 de Weger 更新版（m ≤ 75；对方法极限的说明；Steiner 与 Simons 历史）。已下载并读摘要、定理 3 与 1.3 至 1.5 节。
13. https://archive-ouverte.unige.ch/unige:12087 —— Eliahou 1993 官方摘要（17 087 915）。已打开并读摘要原文。
14. https://www.impan.pl/en/publishing-house/journals-and-series/acta-arithmetica/all/30/3/101028/a-stopping-time-problem-on-the-positive-integers —— Terras 1976 著录页。已抓取（**全文 PDF 未能打开**，被 Anubis 反爬拦截）。
15. https://r.jina.ai/https://www.ams.org/journals/mcom/1978-32-144/S0025-5718-1978-0480321-3/S0025-5718-1978-0480321-3.pdf —— Crandall 1978 全文（经文本代理；AMS 直连 403）。已通读。
16. https://arxiv.org/abs/math/0205002 与 https://arxiv.org/pdf/math/0205002v1 —— Krasikov 与 Lagarias 2002／2003。已下载 PDF 并读摘要、定理 2.2、定理 6.1 与引言末段。
17. https://websites.umich.edu/~lagarias/doc/krasikov.pdf —— 同文作者主页版（论文题头与致谢）。已下载并读。
18. https://websites.umich.edu/~lagarias/doc/applegateI.pdf —— Applegate 与 Lagarias 第一部分（树搜索，γ = 0.65；指数历史链）。已下载并读摘要、定理 1.1、1.2。
19. https://dept.math.lsa.umich.edu/~lagarias/doc/applegateII.pdf —— 第二部分（Krasikov 不等式，γ = 0.81；「指数收敛于 1 以下」原文；Krasikov 猜想）。已下载并读摘要、定理 1.1、§3（表 3.8 前后）、§4。
20. https://cr.yp.to/papers/3x1conjmap-19960215-retypeset20220326.pdf —— Bernstein 与 Lagarias 共轭映射（Bernstein 重排版）。已下载并读摘要、第 1 节、参考文献。
21. https://websites.umich.edu/~lagarias/doc/bernstein.pdf —— 同文的 Lagarias 主页版。已下载（用于核对参考文献编号与「处处不可微」一处的引注）。
22. https://arxiv.org/abs/2111.02635 与 https://arxiv.org/pdf/2111.02635v1 —— Lagarias 2010 年综述。已下载 27 页 PDF 并读 §6.3、§7、§8、§9、§10。
23. https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf —— Hercher 2023（引理 8、定理 21、定理 23、Cor. 29、Remark 30）。已下载并通读要点。
24. https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf —— Hercher 勘误（承认定理 21 推导错误并给出替换论证）。已下载并通读全文（两页）。
25. https://arxiv.org/abs/2201.00406 与 https://arxiv.org/pdf/2201.00406v3 —— Hercher arXiv 版 v3。已下载并核对：仍含有争议推导，未随勘误更新。
26. https://github.com/PhilNorfleet/Hercher2023_lean 及仓库内 README.md、SUMMARY.md（经 raw.githubusercontent.com 抓取）—— Lean 形式化项目（m ≤ 82、外部假设、对定理 21 的指控与理由）。已读；另经 GitHub API 核对创建与推送时间（2026 年 8 月 5 日）。
27. https://cs.uwaterloo.ca/~shallit/Papers/wilson.pdf —— Shallit 与 Wilson「3x+1 与有限自动机」。已下载并通读全文。
28. https://terrytao.wordpress.com/2019/09/10/almost-all-collatz-orbits-attain-almost-bounded-values/ —— Tao 2019 博文（局部时间／全局时间、「超出当前技术」、「至少与 Baker 定理一样难」）。已抓取并读原文段落。
29. https://terrytao.wordpress.com/2011/08/25/the-collatz-conjecture-littlewood-offord-theory-and-powers-of-2-and-3/ —— Tao 2011 博文（遍历论只谈测度一、N 是测度零、nα 类比、弱猜测的 Böhm 与 Sontacchi 形式）。已抓取并读原文段落。
30. https://arxiv.org/abs/1909.03562 与 https://arxiv.org/pdf/1909.03562 —— Tao 论文（定理 1.3、Remark 1.4）。已下载并读。
31. https://preprint.math.uni-hamburg.de/public/papers/hbam/hbam2011-09.pdf —— Opfer 2011（含 2011 年 6 月 17 日作者撤回说明）。已下载并读首页说明与摘要。
32. https://gwern.net/doc/cs/computable/2013-conway.pdf —— Conway 2013「On Unsettleable Arithmetical Problems」。已下载并读第 1、2、3 节（24 函数游戏、FRACTRAN、probviously）。
33. https://mathoverflow.net/questions/197959/a-question-on-collatzs-conjectureproportion-of-low-flying-orbits —— MathOverflow 问答（Lucia 回答的「任意多初始步的独立行为可由模 2 的大幂看出」；Stefan Kohl 的「初等方法没希望」）。已抓取页面，并另经 Stack Exchange API 核对回答者与得分。

已打开的年鉴／著录类页面（用于核对出版信息，未读全文）：
34. https://api.crossref.org/works/10.4153/cjm-1996-060-x 等 Crossref 查询 —— 用于核对 Bernstein 与 Lagarias、Applegate 与 Lagarias 一、二、Crandall、Simons 与 de Weger、Wirsching、Eliahou 的卷页与年份。已调用 API。
35. https://research.tue.nl/en/publications/theoretical-and-computational-bounds-for-m-cycles-of-the-3n1-prob/ —— Simons 与 de Weger 发表版著录。已抓取（摘要未在页面文本中取到）。
36. https://doi.org/10.1007/BFb0095985 —— Wirsching 1998 年专著（The Dynamical System Generated by the 3n+1 Function，LNM 1681）的 Springer 条目。已通过 Crossref 核对存在与卷期；**正文未打开**。
37. https://doi.org/10.1016/0012-365X(93)90052-U —— Eliahou 的 DOI 解析页。已打开（用于核对 DOI 有效性）。

未能打开或未能核对（如实列出）：
38. Terras 1976 的全文 PDF **未能打开**（impan.pl 的下载入口与 matwbn.icm.edu.pl/ksiazki/aa/aa30/aa3034.pdf 均被 Anubis 反爬拦截，我三次尝试均失败）；Everett 1977（Advances in Mathematics 25，42 至 45）未找到开放全文；两者的结论我据 Crandall 1978 与 Lagarias 文献目录转引（第 12 条）。
39. https://doi.org/10.1090/conm/356/06495 —— Akin 2004「Why is the 3x+1 problem hard?」（Contemporary Mathematics 356，1 至 20）。**未能打开**（AMS 付费墙／反爬；OpenAlex 记录为 closed access，无任何开放位置）。本笔记未把它作为论据。
40. https://www.sciencedirect.com/science/article/pii/0012365X9390052U —— Eliahou 1993 的 ScienceDirect 全文。**未能打开**（付费墙）；我读的是 UNIGE 摘要页与文献目录转引。
41. Klarner 1988（Discrete Applied Mathematics 21，207 至 214）与 Halbeisen 与 Hungerbühler 1997（Acta Arithmetica 78）原文**未打开**；两者内容只经 Lagarias 文献目录第 98 条与第 53 条附近的转引使用（第 30 条）。另：文献目录提到后者「改进了 Eliahou 但当时未给出更好的线性循环长度下界、若猜想验证到某界则循环长度下界跳到 102 225 496」，此句我未核对原文。
42. Wirsching 2003（DCDS 9，771 至 787，「On the problem of positive predecessor density in 3n+1 dynamics」）与 Wirsching 1998 年专著正文**未打开**（前者经 MathOverflow 回答转引，后者只核对了著录）。
43. 我未找到任何关于「有限覆盖同余不可能」或「有限自动机不可判定 Collatz」的成文定理；本笔记第 24 条与第 29 条分别给出我自己的部分论证与解读，已在正文标注为【我的推断】。检索无结果不等于不存在，只表示我未能找到。
44. https://doi.org/10.33774/coe-2025-z482f —— Motimba 2025 年 12 月 18 日预印本（宣称完整证明）。**未打开正文**；标题、作者、平台与日期经 Crossref 元数据核对（type 为 posted-content）。
45. https://doi.org/10.2139/ssrn.7290240 —— Shaik 2026 年 8 月 19 日 SSRN 预印本（宣称把对数密度改进为自然密度）。**未打开正文**（SSRN 直连返回 403 反爬页）；标题、作者与日期经 Crossref 元数据核对（type 为 posted-content）。
46. https://doi.org/10.1007/s40315-013-0017-z —— Berg 与 Opfer 2013（负起始值的解析处理，Computational Methods and Function Theory 13，225 至 236 页）。**未打开正文**；作者、卷页与摘要结论经 Crossref 元数据核对（我于 2026 年 10 月 18 日据引文核对意见复核并更正第 32 条）。

## 对核对意见的回应与修订记录

2026 年 10 月 18 日收到三条引文核对意见。我逐条回到原文复核，结论是**三条全部成立**，均已在正文更正；我没有需要反驳的条目，因此本节只记录更正内容与我复核所用的证据（复核所用文本都是我本轮已下载的 PDF 抽取文本与 Crossref 记录）：

一、第 16 条（Krasikov 与 Lagarias 的希望表述）：核对意见指出被取大的量是参数 λ 而非下标 k。我重新检索 arXiv:math/0205002v1 的抽取文本，原文句为「One hopes that a bound of the form π1(x) > x1−ǫ for any ǫ > 0 can eventually be proved by considering L^NT_k(λ) for arbitrarily large λ, and understanding better the structure of the feasible solution sets to these linear program systems.」；同文另有「The parameter λ lies in the interval 1 ≤ λ ≤ 2」。**更正**：第 16 条改为「参数 λ 任意大」并注明 1 ≤ λ ≤ 2。（核对意见成立。）

二、第 23 条（Lagarias 2010 的小节归属）：我在 arXiv:2111.02635v1 的抽取文本中比对小节标题与段落的字符位置：「6.3. How can this be a hard problem...」标题在「It is currently unknown whether the 3x + 1 problem is itself undecidable...」一句之前，故该句在 §6.3；而「There are, however, reasons to suspect...」「thin set of input values」「the 1972 encoding of a universal com...」三处均在「7. Hardness of the 3x + 1 problem」标题之后，故属 §7。**更正**：第 23 条标题与出处改为「§6.3（不可判定性一句）与 §7（三条理由、薄集告诫与 1972 年编码）」。（核对意见成立。）

三、第 32 条（Berg 2013 的作者）：我查询 Crossref 的 10.1007/s40315-013-0017-z 记录，作者为 Lothar Berg 与 Gerhard Opfer，刊名 Computational Methods and Function Theory，卷 13，225 至 236 页，日期 2013 年 6 月 25 日。**更正**：第 32 条补上合著者 Gerhard Opfer，并写明作者、卷页与摘要结论的来源为 Crossref 著录而非全文阅读。（核对意见成立。）

附注：前两处更正的共同教训是，它们都属于「自称读原文但把边界条件或小节记错」的情形，正是本笔记最需要避免的错误；本文中其余「我亲自读」的标注已按小节与页码重新收紧，凡只据转引的条目均保留「未打开」标注。
