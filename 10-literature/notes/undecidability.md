# undecidability

笔记状态：2026 年 10 月 18 日检索与核对。本笔记区分三类可信度：一、经同行评审的定理；二、仅预印本或社群宣称（含带机器可检验证书但未经评审者）；三、我未能核对的内容。凡我未亲自打开的页面，在来源清单中逐条注明。

## 这条线在问什么

科拉茨猜想本身是**一个具体函数的**一条 Π⁰₂ 语句：∀x∃i，使 f^i(x) = 1（x 取正整数，f 是 3x+1 映射）。而这条研究线处理的是三类**围绕**它的硬性结果：

1. 把 3x+1 推广成「一族分段的仿射函数」（Conway 1972 的广义 Collatz 函数，GCF）之后，判定问题变成不可判定，甚至达到 Π⁰₂ 完备（Kurtz 与 Simon 2007）。这条线问的是：这类不可判定性能精确到哪一层？它反过来对「证明原猜想必须用到什么」给出哪些约束？
2. 另一头是具体的小图灵机：某些机器（如 748 状态的 ZFC 证明枚举机）的停机行为**已被证明**独立于 ZFC；而另一些更小的机器（如 6 状态的 Antihydra）停机行为**等价于**一个 Collatz 型轨道问题。这条线问的是：硬度边界现在停在多少个状态？为什么停在那里？
3. 核心的区分（本笔记反复强调）：不可判定性结果约束的是**问题族与统一判定方法**；原猜想是**单个实例**。族层面的 Π⁰₂ 完备性不排除原猜想在某个算术系统中有证明，但排除了任何「用一条统一定理覆盖所有广义 Collatz 函数」的路线。

## 关键结果

### 一、族层面的不可判定性（经同行评审的定理）

1. **Conway 1972：广义 Collatz 迭代的判定问题不可判定。** 定理（原文表述）：对任意可计算函数 f，存在函数 g，使 g(n)/n 为周期函数（取有理值），且从 2^n 出发首次到达 2 的幂所需的迭代次数（记为 k，最小正整数使 g^k(2^n) 为 2 的幂）满足 g^k(2^n) = 2^{f(n)}。推论（原文）：不存在算法，给定这样的 g 与一个数 n，判定是否存在 k 使 g^k(n) = 1。—— 1972 年，J. H. Conway（Trinity College），Proc. 1972 Number Theory Conference, University of Colorado, Boulder, CO, pp. 49 至 52（页码经 Lagarias 注释书目第 43 条核实，MR 52 #13717；bbchallenge wiki 的引用与之一致）。PDF：https://gwern.net/doc/cs/computable/1972-conway.pdf （该 PDF 是 Lagarias 编《The Ultimate Challenge》（2010）的重印影印：pdfinfo 的 Keywords 字段注明出处；其上印的重印本页码为 219、220、222，其中 220 与 222 各重复一页、221 缺页。我亲自下载并抽取正文核对定理与推论）。论文中 g 的定义形如 g(n) = a_i·n + b_i 当 n ≡ i (mod p)，系数为有理数；Conway 的证明通过 Minsky 程序（寄存器机）编码完成。

2. **Conway 1972 的机器编码形式（转述）**：每一台 Minsky 机 M 可被编码成一个 GCF g，使得对所有 n，M 在输入 n 上停机当且仅当 g 从 2^{n+1} 出发到达 1。—— 转引自 bbchallenge wiki 的 Generalized Collatz Function 页面（我亲自抓取），非我直接读原文；Kurtz 与 Simon 论文的 Theorem 1.6 也复述了 Conway 的结果（我从作者主页 PDF 亲自读到，见下条）。

3. **Kurtz 与 Simon 2007：广义 Collatz 问题 Π⁰₂ 完备。** 定理（我从预印本读到的编号）：Theorem 1.4，给定一个 Collatz 函数 g，判定「对所有整数 x 都存在 i 使 g^(i)(x) = 1」是不可判定的。Theorem 1.5，集合 {g : range(g) = ω} 是 Π⁰₂ 完备的，其中 range(g) = {x : 存在 i 使 g^(i)(x) = 1}。他们明确指出的技术困难：Conway 的 g 在非 2 的幂的输入上行为不可控（带「垃圾」），因此 Conway 的证明不能直接推广到「对所有 x」的判定问题。他们的方法：寄存器机的**双重模拟**（outer 模拟向前推进，inner 模拟检查 outer 的一致性，且 inner 保证停机；中间定理 Theorem 2.3：每台寄存器机 M 可有效转换为一台 M'，使 M 全（total）当且仅当 M' 从每一个配置都能到达停机配置）。—— 2007 年（预印本日期 December 26, 2006），Stuart A. Kurtz、Janos Simon（芝加哥大学），TAMC 2007（Shanghai），LNCS 4484，pp. 542 至 553，Springer，DOI 10.1007/978-3-540-72504-6_49。作者主页 PDF：https://people.cs.uchicago.edu/~simon/RES/collatz.pdf （我亲自下载并读；注意：该预印本共 6 页，第 3 节 The Main Result 只有标题、正文未含在此 PDF 中，我核对的是第 1 至 2 节的定理陈述与构造思路）。

4. **补充（转引，未核对原文）**：存在模 396 的通用 GCF —— 转引自 bbchallenge wiki，引 Frantisek Kascak, "Small universal one-state linear operator algorithm", MFCS 1992, LNCS 629, DOI 10.1007/3-540-55808-X_31（我未打开该论文）。wiki 同时把 GCF 的「mortality problem」（给定 g，是否对所有输入最终到达 1）记为 Generalized Collatz Problem。

### 二、具体图灵机的 ZFC 独立性（已证定理 + 记录链）

5. **Yedidia 与 Aaronson 2016：停机行为独立于 ZFC 的图灵机上界。** 发表版：存在显式的 7910 状态、1 带 2 符号图灵机 Z，其在 ZFC 中不能被证明「永远运行」（假设 ZFC 一致）；机器基于 Harvey Friedman 关于 order-invariant graphs 的独立性工作；同时给出停机当且仅当 Goldbach 猜想有反例的机器 G、以及停机当且仅当 Riemann 假设为假的机器 R（发表版摘要未给这两个状态数；我在其 2016 年 4 月 22 日初稿中读到 G 为 4888 状态、R 为 5372 状态，初稿给出的上界是 7918）。—— 2016 年，Adam Yedidia、Scott Aaronson，Complex Systems 25(4)，起始页 297，DOI 10.25088/complexsystems.25.4.297。我亲自读了两版 PDF：初稿 https://www.scottaaronson.com/busybeaver.pdf （7918 状态）、发表版 https://content.wolfram.com/uploads/sites/13/2018/02/25-4-4.pdf （7910 状态）。版本数字差异（7918 到 7910）是真实的修订，不是我的读数错误。

6. **O'Rear 2016 至 2017：上界从 1919 压缩到 748。** 他写了 NQL（Not-Quite-Laconic）编译器，把「枚举 ZF 变体 ZF−R 的证明、发现矛盾即停机」的证明枚举器编译成图灵机：先用构造证明枚举器把上界压到 1919（2016 年），进一步优化 NQL 代码后得到 748 状态机器（2017 年），其停机当且仅当 ZF−R 不一致。—— 转引自 Riebel 2023 的学士论文（我亲自下载并读，含引文 [ORe16]），以及 O'Rear 的仓库 https://github.com/sorear/metamath-turing-machines （我经 GitHub API 确认仓库存在，创建于 2016 年 5 月；未读代码）。748 的精确含义：停机当且仅当该 ZF 变体不一致；因此若 ZFC 一致，则 ZF（及 ZFC）不能证明它不停机，也不能确定 BB(748) 的值。

7. **Riebel 2023：748 到 745。** 学士论文把上述上界从 748 压到 745 状态（论文明确写出这个结论，并在结尾章给出编译后的 745 状态机器）。论文同时记录了失败的优化尝试：Cantor 配对函数的改写、peephole 优化（检查不可达状态、可合并状态、可折叠的状态环）都未能再省状态；论文指出机器的状态转移图中不存在可折叠的循环，且替代方案（编码其他不可判定语句，如 Diophantine 方程）会使状态数「至少 748、很可能多得多」。—— 2023 年 3 月，Johannes Riebel，"The Undecidability of BB(748): Understanding Gödel's Incompleteness Theorems"，Bachelor Thesis at the Chair of Algebra and Number Theory。PDF：https://www.ingo-blechschmidt.eu/assets/bachelor-thesis-undecidability-bb748.pdf （我亲自下载并读）。该 PDF 的标题页未印大学名；它托管于 Ingo Blechschmidt（奥格斯堡大学数学研究所）的个人主页，「奥格斯堡大学」是我的推断而非 PDF 原文。

8. **2026 年社区记录（仅社群宣称，未经同行评审，我未复现其证明脚本）**：
   - 254 状态：机器由 Mira-Cult 设计（其 "ZFC254" 归约的最终表，2026 年 9 月 30 日）；Jeffrey Ketchersid 给出端到端 Coq 证明（无公理），三条定理：停机当且仅当 ZF 不一致、当且仅当 ZFC 不一致、当且仅当机器所搜索的理论 SIR 不一致；`Print Assumptions` 报告证明不依赖额外公理。—— 仓库 https://github.com/jeff87654/busy-beaver 的 ZF/m254 目录（我亲自读了其 README 与 GitHub API 元数据）。
   - 250 状态：同一仓库体系下，aimir 的项目给出 250 状态的 protected-startup 机器，2026 年 10 月 16 日的提交记录为「159 个模块的 Coq 验证」；其 README 同时给出 251、252、253、254 状态变体（均有完整 Coq 证明），以及一个 308 状态候选（Lean 验证了「纸带到源演算」的等价，但「该演算与常规 ZF 的联系尚未证明」），并明确声明「Search limits are not lower bounds」（搜索极限不是下界）。—— 仓库 https://github.com/aimir/tiny-zf （我亲自读 README 与 API 元数据；仓库创建于 2026 年 10 月 13 日）。
   - 296 状态：Ketchersid 仓库另有 296 状态机器，停机当且仅当「ZFC + 每个集合都属于一个 Grothendieck 宇宙」不一致（带无公理的 Coq 证明）。—— 同仓库 ZF/tg296 目录（我亲自读 README）。
   - 387 状态：X 平台 2026 年 9 月 21 日的帖子称 Astra 找到 387 状态的「停机性独立于 ZFC」的机器、Grok 正在用 Lean 形式化。—— **未能核对**：我尝试打开该帖失败（WebFetch 超时，X 需要登录）；日期由帖子编号按 snowflake 规则换算而来。
   上述 2026 年记录的状态数（250、254、296、308）与 387 的宣称之间关系不明；我未找到把它们对账的权威来源。

### 三、小图灵机中的 Collatz 型硬问题（2024 年后）

9. **BB(5) 已被确定（2024 年）：边界移到 6 状态。** S(5) = 47,176,870，用 Coq 证明助手形式化，枚举 181,385,789 台 5 状态机器逐一判定；这是 40 多年来首次确定新的 Busy Beaver 值、也是首次被形式验证的 BB 值。—— 2024 年 7 月 2 日 bbchallenge 宣布；论文 "Determination of the fifth Busy Beaver value"，2025 年 9 月 15 日首版、2026 年 3 月 23 日修订，作者为 The bbchallenge Collaboration 加 19 位具名作者：Justin Blanchard、Daniel Briggs、Konrad Deka、Nathan Fenner、Yannick Forster、Georgi Georgiev、Matthew L. House、Rachel Hunter、Iijil、Maja Kądziołka、Pavel Kropitz、Shawn Ligocki、mxdys、Mateusz Naściszewski、savask、Tristan Stérin、Chris Xu、Jason Yuen、Théo Zimmermann（我经 arXiv API 逐项核对；此名单中没有 Damien Woods，他是第 12 条 BB(15) 论文的作者之一），https://arxiv.org/abs/2509.12337 （我经 arXiv API 核对元数据与摘要）。相关：Chris Xu, "Skelet #17 and the fifth Busy Beaver number", https://arxiv.org/abs/2407.02426 （2024 年 7 月 2 日，我经 arXiv API 核对）。意义：5 状态之内不存在独立性问题；第一个 Collatz 型的硬度出现在 6 状态。

10. **Antihydra（2024 年 6 月）：BB(6) 的第一个 Collatz 型 Cryptid。** 机器 1RB1RA_0LC1LE_1LD1LC_1LA0LB_1LF1RE_---0RA，由 mxdys 于 2024 年 6 月 28 日在 bbchallenge 的 Discord 报告，Racheline 随后给出高层规则。从空白带出发，它的停机问题等价于：从 8 开始反复应用 f(n) = n + ⌊n/2⌋（等价地 f(2n) = 3n、f(2n+1) = 3n+1），是否在某个时刻累计的奇数次数超过偶数次数的两倍（O > 2E）；若发生则停机。等价表述：H(n) = ⌊3n/2⌋（Hydra 函数）从 8 出发的轨道，或一致的 Collatz 序列（m = 2, r = 3, J = {0 ↦ 0, 1 ↦ −1}）的奇偶计数条件。因此确定 BB(6) 需要先解决这个 Collatz 型问题。—— 2024 年，发现者 mxdys、规则分析 Racheline、撰文 Shawn Ligocki；来源：https://www.sligocki.com/2024/07/06/bb-6-2-is-hard.html （2024 年 7 月 6 日博文，我亲自抓取核对）、https://wiki.bbchallenge.org/wiki/Antihydra （我亲自抓 raw 文本）、https://bbchallenge.org/antihydra （我亲自抓 HTML，含其 Python 程序与停机条件）。

11. **同族的其他 Cryptids（社群记录）**：Bigfoot（BB(3,3)，2023 年 11 月，Shawn Ligocki 发现）、Hydra（BB(2,5)，2024 年 5 月，Daniel Yuan；Antihydra 与它同映射，仅起点 3 对 8、停机条件 E > 2O 对 O > 2E 相反）、Bonus cryptid（BB(2,5)，2024 年 5 月，Daniel Yuan）、Lucy's Moonlight（BB(6)，2025 年 3 月，Racheline）、以及若干 BB(6) 变体。wiki 的定义：Cryptid 是行为可由相对简单的数学规则完整描述、但该规则落入未解决（且假定难）的数学问题类的机器；若存在 n 状态 m 符号的 Cryptid，则 BB(n, m) 不可能在不解决该难题的情况下被解决。—— 转引自 https://wiki.bbchallenge.org/wiki/Cryptids （我亲自抓 raw）。标注：这些日期与归属是社群记录，非同行评审；「probviously（很可能显然）非停机」等措辞是社群术语，不是证明。

12. **Stérin 与 Woods：BB(15) 与一个 Collatz 相关的 Erdős 猜想（2021 年首版，2024 年 6 月修订）。** 构造 15 状态、2 符号图灵机，停机当且仅当 Erdős 1979 年提出的猜想为假：「对所有 n > 8，2^n 的三进制表示中至少含一个数字 2」。论文因此把 BB(15) 与一个自然的未解决猜想绑定（在其写作时是与自然开放问题相关的最小 BB 值）。—— "Hardness of busy beaver value BB(15)"，Tristan Stérin、Damien Woods，2021 年 7 月 26 日首版、2024 年 6 月 11 日修订，https://arxiv.org/abs/2107.12475 （我经 arXiv API 核对元数据与摘要）。

13. **2026 年 10 月：12 状态的 5n+1 Cryptid（社群记录，页面自标 "in progress"）。** 2026 年 10 月 1 日，sheep 发现一个 12 状态、2 寄存器机器，其停机当且仅当 7 在 Collatz 型 5n+1 映射下收敛到 1，据此称 MBB(12, 2) 是硬的。—— 转引自 https://wiki.bbchallenge.org/wiki/TMBR:_October_2026 （我亲自抓 raw；该页面注明「本版尚未发布、仍在编辑」）。标注：仅社群宣称，未经评审。

### 四、这些结果对「证明原猜想必须用到什么」的约束

14. **已证定理给出的三条硬约束**：
    - 任何「用一个统一算法或一条统一定理判定所有（或一大类）广义 Collatz 函数」的路线必然不存在：Conway 已证判定问题的不可判定性，Kurtz 与 Simon 把它加强到 Π⁰₂ 完备。这是**族**层面的结论，直接适用于任何试图「用一般性定理覆盖原猜想」的泛化方法。
    - Conway 式的编码（只控制 2 的幂输入）**不足以**证明「对所有 x」的判定问题不可判定；想从 Conway 1972 直接走到更强结论会遇到「非 2 的幂输入不可控」的障碍（Kurtz 与 Simon 论文明确记录了这个困难，并用双重模拟绕过）。
    - 对「一致的 Collatz 序列」（全部分支共享同一线性系数，m、r 固定，如 Antihydra 的 m = 2、r = 3）目前**没有**已知的不可判定性或 Π⁰₂ 完备性结果——Kurtz 与 Simon 的定理针对一般 GCF；更受限类的最优复杂度上界，我未检索到 2007 年之后的正式改进（检索 2025 年前后相关关键词无结果；这不等于不存在，只是我未能找到）。这一类子问题（例如 m = 2、r = 3）正是「最简单的 Collatz 型硬度」所在，也是当前全部障碍的所在。

15. **由 Π⁰₂ 完备性直接得到的推论（我的推断，非原文陈述）**：既然 {g : range(g) = ω} 是 Π⁰₂ 完备的，那么对任意 Π⁰₂ 语句 S（科拉茨猜想本身就是一个 Π⁰₂ 语句）都存在一个具体的 GCF g_S，使得「g_S 对所有 x 收敛到 1」与 S 等价。也就是说，与原猜想等价的广义实例确实存在——这**不**意味着原猜想不可证明，恰恰说明：族不可判定性只杀死「统一判定」，不杀死任何具体实例的证明。原问题仍可能有证明，因为（甲）它是一个固定函数上的固定 Π⁰₂ 语句；（乙）Π⁰₂ 完备性不给出任何单个实例的独立性。此推论由完备性的定义直接得出，我未读到有来源把它这样明确写出；请当作我的推断。

16. **必须区分的两个说法（本线最容易被混淆的点）**：
    - 「BB(748)（及其后的 745、254、250）的值独立于 ZFC」是**定理**（假设 ZFC 一致；论证格式：机器枚举 ZFC 证明、发现矛盾才停机，若 ZFC 能证明它不停机则 ZFC 证明自身一致，违反 Gödel 第二定理）。
    - 「BB(6) is Hard」是**启发式与障碍陈述**（要确定 BB(6) 必须先解 Antihydra 的 Collatz 型问题），**不是**「BB(6) 独立于 ZFC」的定理。BB(6) 是否独立于 ZFC 目前未知——它取决于 1581 台未决机器（2026 年 10 月数字，见下）各自的停机性及其可证明性。
    - 同样，**没有任何**定理或可靠来源证明「科拉茨猜想本身独立于 PA 或 ZFC」，也没有相反方向的结果；我为此做了多轮检索（中英文关键词），未找到任何一方。这是本条研究线上最大的空白。

## 当前的技术极限（记录值是多少、谁保持、为什么停在那里）

一、Antihydra 的模拟记录（自动机一侧的极限）
- 2^31 = 2,147,483,648 个规则步：2024 年 7 月初由 mxdys 的加速程序达到（sligocki 博文记录此时 b = 1,073,720,884，仅比随机游走期望低 20940）；2024 年 7 月 23 日论坛用户 C7X 复跑该程序，最终输出 `2147483648 1073720884 -20940`，因耗尽内存被杀。—— https://www.sligocki.com/2024/07/06/bb-6-2-is-hard.html 与 https://discuss.bbchallenge.org/t/antihydra-simulation-status/242 （两个来源我都亲自抓取）。
- 2^38 个规则步：2024 年 8 月 9 日的 Discord 记录，被 bbchallenge wiki 的 Antihydra 页面引用为「目前已被模拟到」的进度（此时参数 a 超过 2^37）。—— https://wiki.bbchallenge.org/wiki/Antihydra （我亲自抓 raw）。我未找到 2025 年至 2026 年关于该记录被刷新的公开材料。
- 参考量级：同一时期 LegionMammal978 的加速模拟器把 Bigfoot 模拟到 2.2 万亿次迭代（2024 年 7 月 5 日论坛发言，我用同一帖子核对）。
- 概率启发（社群计算，非证明）：把 b 的演化看成步长 +2 与 −1 的随机游走，从当前位置出发永不返回 −1 的概率形如 ((√5 − 1)/2)^{n+1}；对当前 a 的量级给出约 2.884 × 10^(−28723042565) 的返回概率上界，因此「Antihydra 很可能永不停机」。—— https://wiki.bbchallenge.org/wiki/Antihydra （我亲自抓 raw；该页给出了递推推导）。标注：这是启发式估计，不是定理。
- 为什么停在这里：模拟只能给下界，不能证明轨道性质；该类序列的准线性模拟算法（一致的 Collatz 序列的 w_n、j_n 递推，见 https://wiki.bbchallenge.org/wiki/Consistent_Collatz ，我亲自抓 raw）只能推进步数，不产生证明。wiki 另引 Dubickas 2009 的结果（Antihydra 不生成 Sturmian 词，Corollary 4；DOI 10.1017/S0017089508004655）称某类结构分析不适用于它——该引用我未核对原文。

二、ZFC 独立性机器的状态数记录（构造一侧的极限）
- 7918（Yedidia 与 Aaronson 初稿，2016 年 4 月，我亲自读的 PDF）→ 7910（发表版，Complex Systems 25(4)，起始页 297，我亲自读）→ 1919（O'Rear，2016 年，证明枚举器）→ 748（O'Rear，2017 年，NQL 编译器）→ 745（Riebel，2023 年，学士论文）→ 254（Mira-Cult 设计、Ketchersid 端到端 Coq 证明，机器归约日期 2026 年 9 月 30 日）→ 250（aimir 的 tiny-zf，2026 年 10 月 16 日 Coq 验证）。387 状态的宣称（2026 年 9 月 21 日 X 帖）未能核对；308（Lean 部分验证，与 ZF 的联系未证）与 296（ZF + Grothendieck 宇宙）是两个并行的构造分支。
- 为什么停在那里：状态数由「枚举 ZFC 证明 + 解析公式 + 验证推理规则」的编码开销决定。Riebel 论文第 3.5 节记录了失败的压缩尝试（配对函数改写、peephole 优化、查找可折叠循环），并说明机器中找不到可利用的结构；替代路线（换用其他不可判定语句）只会更贵。tiny-zf 的记录显示每次改进只有几个状态（254 到 250），且其 README 明确声明搜索极限不是下界。2023 年（745）到 2026 年（250、254）的进步主要来自编码工程（寄存器分配、指令树共享、证明检验器压缩），而不是理论突破。

三、BB(6) 的未决数量与下界（问题一侧的规模）
- 2026 年 10 月的 bbchallenge 持有列表：BB(6) 仍有 1581 台未决机器、740 个等价类（文件名 BB6_holdouts_1581_eqv_740.txt，见 TMBR October 2026 页面的引用，我亲自抓 raw）。其中包含 Antihydra。
- 下界：mxdys 于 2025 年 6 月发现的新 champion 给出 S(6) > Σ(6) > 10↑↑10↑↑10↑↑8（bbchallenge wiki 的 BB(6) 页面，我亲自抓 raw）。BB(6) 的精确值未知，Antihydra 是主要障碍之一。

## 未解决的缺口

1. **原猜想本身的独立性或不可判定性没有任何结果**：无论「科拉茨猜想独立于 PA/ZFC」还是「某具体 GCF 的独立性」，我检索不到任何定理或可靠预印本。这是本条线上最大的空白，也是所有关于「证明原猜想需要什么」讨论的天花板。
2. **更受限类的最优复杂度未知**：Kurtz 与 Simon 的 Π⁰₂ 完备性针对一般 GCF；对「一致的 Collatz」（全分支同一系数，如 m = 2、r = 3）我未找到 2007 年之后的正式改进，也不知道该类的判定问题是否 Π⁰₂ 完备、甚至是否不可判定。而最简单的具体障碍（Antihydra）恰好落在这个受限类里。
3. **Antihydra 型轨道问题没有已知证明技术**：模拟只到下界（2^31、2^38 规则步）；随机游走启发给出极小概率但不构成证明；Sturmian 词方法已被排除（转引）；模结构证书（congruence certificate）在同类机器上被报告为不存在（一个社群仓库明确写道「no congruence certificate exists at any modulus，最后一步筛在任意深度至多排除约 29.6% 的分支词」，见 https://github.com/TomZahavy/collatz-cryptids ，我未打开核对）。如何证明任意一个 6 状态机器的 Collatz 型轨道性质，是公开的技术空白。
4. **BB(6) 是否独立于 ZFC 未知**：由 3 与 BB(6) 的 1581 台未决机器共同决定；即使 Antihydra 被解决，其他 Cryptid 仍可能阻塞；没有任何来源给出方向性结论。
5. **「最小 ZFC 独立机器」没有下界**：当前记录从 745（2023 年，经评审的学士论文）被社区在 2026 年推到 250 与 254（未评审）；387 的宣称与 250 体系的关系未能核对；没有任何定理说明它不能更小。记录本身处于快速变动中。
6. **我的核对缺口（如实列出）**：Kurtz 与 Simon 的正式版（Springer）第 3 节正文我未读到（作者主页预印本该节缺失，Springer 页面重定向到登录流程）；Yedidia 与 Aaronson 发表版的结束页与 G、R 两个机器在发表版中的准确状态数未逐一确认（发表版摘要未给数字，初稿给 4888 与 5372）；Riebel 论文的机构名是推断；Kascak 1992 与 Dubickas 2009 原文未读；X 平台的 387 状态宣称未能打开。

## 若要在这一线推进，必须跨过什么门槛

1. **要推动 BB(6)：必须解决具体 Collatz 型轨道问题。** 最小障碍是 m = 2、r = 3 的一维序列（Antihydra 的奇偶计数条件）。现有全部工具的清单（模拟、随机游走启发、Sturmian 结构、模证书）都不足以给出证明；需要一个关于这类轨道奇偶分布的真正定理，或一个能证明「永不返回」的新的不变量方法。
2. **若要把不可判定性从族转移到具体函数：需要新的证明论构造。** Conway 与 Kurtz 与 Simon 的编码都对函数族生效；要让「单个 GCF 的收敛性独立于 PA/ZFC」落地，需要的形式化技术目前不存在（这本身就是本线最硬的门槛）。
3. **若要证明原猜想：必须证明一个具体的 Π⁰₂ 语句，而该线不提供捷径。** 两条可能路径的证论强度不同：若猜想为假且反例是闭环，则存在有限验证（一个具体的轨道环可以被完整检验）；若猜想为真，则需要一个能被算术系统证认的一般性定理。「猜想独立」的传言没有文献基础；Conway 与 Kurtz 与 Simon 的结果约束的是泛化与统一判定，不是这个具体实例——这是原问题仍可能有证明、且必须走专门数论路线的原因。
4. **若要继续压低 ZFC 独立机器的状态数：需要更紧的证明检验器与公式编码。** 2023 年至 2026 年从 745 到 250（未评审）的进步以每次几个状态的速度前进，且可靠性依赖越来越重的 Coq 脚本；能否到几十个状态、以及如何给出下界，都没有已知方法。
5. **若要建立可信的新记录：需要把社群结果变成可评审的文本。** 254、250、308 的构造目前只存在于 GitHub 仓库与 Discord；387 的宣称只存在于 X 平台。第三方（包括我）目前只能核对其 README 与提交记录，不能核对其证明。这一线的「记录」目前一半是工程竞赛，其可信度取决于 Coq 脚本能否被独立复算。

## 来源清单（全部 URL，逐条注明是否亲自打开）

经同行评审（或正式发表）的原始来源
1. https://gwern.net/doc/cs/computable/1972-conway.pdf —— Conway "Unpredictable Iterations" PDF（Lagarias 编《The Ultimate Challenge》（2010）的重印影印；pdfinfo 的 Keywords 字段注明出处）。**已亲自下载并用 pdftotext 抽取正文核对**（定理、推论、定义、Collatz 验证历史；并逐页确认其上印有重印本页码 219、220、222，含重复页与缺页）。
2. https://people.cs.uchicago.edu/~simon/RES/collatz.pdf —— Kurtz 与 Simon 预印本（2006 年 12 月 26 日）。**已亲自下载并读**（第 1 至 2 节；第 3 节正文缺失）。
3. https://link.springer.com/chapter/10.1007/978-3-540-72504-6_49 —— 正式版条目（TAMC 2007，LNCS 4484，pp. 542 至 553）。**未打开**（重定向到 Springer 登录流程 idp.springer.com）；DOI、页码与会议信息来自搜索结果与作者主页预印本。
4. https://www.scottaaronson.com/busybeaver.pdf —— Yedidia 与 Aaronson 初稿（2016 年 4 月 22 日，7918 状态）。**已亲自下载并读**。
5. https://content.wolfram.com/uploads/sites/13/2018/02/25-4-4.pdf —— Yedidia 与 Aaronson 发表版（Complex Systems 25(4)，7910 状态）。**已亲自下载并读**。
6. https://www.complex-systems.com/abstracts/v25_i04_a04/ —— 发表版摘要页。**未打开**（WebFetch 超时）；DOI 10.25088/complexsystems.25.4.297 与起始页 297 来自搜索结果。
7. https://www.ingo-blechschmidt.eu/assets/bachelor-thesis-undecidability-bb748.pdf —— Riebel 学士论文（748、745、失败优化）。**已亲自下载并读**。
8. https://docs.bbchallenge.org/papers/Riebel2023.pdf —— 同一论文的镜像。**未打开**。
9. https://arxiv.org/abs/2509.12337 —— BB(5) 确定论文。**经 arXiv API 核对元数据与摘要，并在核对意见处理中逐项复核作者列表**（20 项 = 协作组加 19 位具名作者，其中无 Damien Woods；未打开 HTML 页面本体）。
10. https://arxiv.org/abs/2407.02426 —— Skelet #17（Chris Xu）。**经 arXiv API 核对元数据与摘要**。
11. https://arxiv.org/abs/2107.12475 —— Stérin 与 Woods，BB(15) 与 Erdős 猜想。**经 arXiv API 核对元数据与摘要**（标题 "Hardness of busy beaver value BB(15)"，v2 日期 2024 年 6 月 11 日）。
12. https://dl.acm.org/doi/10.1145/3798129.3806376 —— BB(5) 论文的 ACM DL 记录。**未打开**（仅见于搜索结果）。
12a. https://arxiv.org/abs/math/0309224 —— Lagarias 的注释书目（The 3x+1 problem: An annotated bibliography）。**本轮核对新增：已亲自下载并检索**，第 43 条给出 Conway 1972 的完整出处与页码 49 至 52（MR 52 #13717），并注解说该文证明一个形式上类似 3x+1 的更一般迭代问题不可判定。

社群维护的 wiki、博客与论坛（我全部亲自抓取原文）
13. https://wiki.bbchallenge.org/wiki/Antihydra —— **已亲自抓 raw wikitext**（规则推导、2^38 记录、随机游走概率计算、Kuperberg 模拟代码）。
14. https://bbchallenge.org/antihydra —— **已亲自抓 HTML**（Python 程序、停机条件、问题定位）。
15. https://wiki.bbchallenge.org/wiki/Cryptids —— **已亲自抓 raw**（Cryptid 定义与最小 Cryptid 清单）。
16. https://wiki.bbchallenge.org/wiki/BB(6) —— **已亲自抓 raw**（champion、2025 年 6 月下界、历史表）。
17. https://wiki.bbchallenge.org/wiki/Generalized_Collatz_Function —— **已亲自抓 raw**（GCF 定义、Conway 1972 页码、Kurtz 与 Simon 与 Kascak 的转引）。
18. https://wiki.bbchallenge.org/wiki/Collatz-like —— **已亲自抓 raw**（Collatz 型问题示例、Hydra 与 5 状态 winner 的分析）。
19. https://wiki.bbchallenge.org/wiki/Consistent_Collatz —— **已亲自抓 raw**（一致 Collatz 的定义与准线性模拟算法）。
20. https://wiki.bbchallenge.org/wiki/TMBR:_October_2026 —— **已亲自抓 raw**（2026 年 10 月的 12 状态 5n+1 Cryptid、BB(6) 持有列表数字；页面自标未发布）。
21. https://www.sligocki.com/2024/07/06/bb-6-2-is-hard.html —— **已亲自抓 HTML**（Antihydra 的发现、规则、2^31 记录）。
22. https://discuss.bbchallenge.org/t/antihydra-simulation-status/242 —— **已亲自抓 JSON**（2024 年 7 月的模拟记录与加速讨论）。
23. https://wiki.bbchallenge.org/wiki/BB(5) —— 未打开（BB(5) 部分信息来自搜索结果与 arXiv API）。
24. https://bbchallenge.org/ —— 未打开（BB(5) 宣布文字来自搜索片段）。
25. https://oeis.org/A385902 —— 未打开（Antihydra 相关序列，搜索结果提及）。

社群仓库（我亲自读了 README 与 GitHub API 元数据）
26. https://github.com/aimir/tiny-zf —— **已亲自读 README 与 API**（250、251、252、253、254、308、392、393 状态与 Coq/Lean 验证范围；"Search limits are not lower bounds"）。
27. https://github.com/jeff87654/busy-beaver —— **已亲自读 ZF/m254 与 ZF/tg296 的 README 与 API**（254 状态 Mira-Cult 设计、Ketchersid 无公理 Coq 定理；296 状态 ZF + Grothendieck 宇宙）。
28. https://github.com/sorear/metamath-turing-machines —— **已亲自查 GitHub API 元数据**（O'Rear 的证明枚举器仓库，创建于 2016 年 5 月；未读代码）。
29. https://github.com/Mira-Cult/turing-machines —— 未打开（由 Ketchersid 的 README 转引）。
30. https://github.com/TomZahavy/collatz-cryptids —— 未打开（仅见于搜索结果；引用其「无模证书」的说法）。

未能核对的内容
31. https://x.com/_Mira___Mira_/status/2102108613028560993 —— 387 状态宣称。**未能打开**（WebFetch 超时；X 需登录）。日期 2026 年 9 月 21 日由 snowflake 编号换算，内容未核对。
32. https://x.com/arlotests/status/2110286017081065668 —— 2026 年 10 月 14 日关于「Riemann 假设机器 120 到 104 状态、Goldbach 25 到 21 状态」的宣称。**未能打开**（同上）。
33. https://doi.org/10.1007/3-540-55808-X_31 —— Kascak 1992（模 396 的通用 GCF）。**未核对原文**（经 wiki 转引）。
34. https://doi.org/10.1017/S0017089508004655 —— Dubickas 2009（Antihydra 不生成 Sturmian 词）。**未核对原文**（经 wiki 转引）。

检索备注：我用 DuckDuckGo 相关查询与 arXiv API 做了多轮检索；「2024 年之后关于广义 Collatz 不可判定性的正式改进」与「745 状态之后经评审的最小 ZFC 独立机器」均未检索到结果。检索无结果不等于不存在，仅表示我未能找到。

## 对核对意见的回应

核对意见一（arXiv:2509.12337 作者名单误列 Damien Woods）：**核实成立，已更正。** 本轮重跑的命令与输出：`curl -sL "http://export.arxiv.org/api/query?id_list=2509.12337"` 后解析返回的 XML，得到 20 项作者条目：第 1 项为 The bbchallenge Collaboration，其后 19 位具名作者（Justin Blanchard、Daniel Briggs、Konrad Deka、Nathan Fenner、Yannick Forster、Georgi Georgiev、Matthew L. House、Rachel Hunter、Iijil、Maja Kądziołka、Pavel Kropitz、Shawn Ligocki、mxdys、Mateusz Naściszewski、savask、Tristan Stérin、Chris Xu、Jason Yuen、Théo Zimmermann），检查输出为 `WOODS IN LIST: False`。因此原第 9 条中「含 mxdys、Tristan Stérin、Damien Woods、Yannick Forster、Théo Zimmermann 等」的示例名单有误：已删去 Damien Woods，并补全 19 位具名作者全名单。Damien Woods 是第 12 条 BB(15) 论文（arXiv:2107.12475）的共同作者，这是我上一轮已核对的事实（该论文作者为 Tristan Stérin、Damien Woods），两处不存在混淆。

核对意见二（Conway PDF 的页码描述「没有页码标记」不成立）：**核实成立，已更正。** 本轮重跑的命令与输出：

1. `pdfinfo conway1972.pdf` 的 Keywords 字段为 `_The Ultimate Challenge_, ed Lagarias 2010; Collatz conjecture, undecidability, FRACTRAN`，确认该 PDF 是 Lagarias 编《The Ultimate Challenge》（2010）的重印影印（共 5 页，另有 1 页空白）。
2. 逐页抽取（`pdftotext -f 1` 至 `-f 5` 加 `-layout`）：第 1 页页脚为「2 1 9」（即 219）；第 2 页页眉为「2 2 0」（即 220）；第 3 页与第 2 页的抽取文本 md5 完全相同（同为 6dafcb7ae84e8a087ec9a657966853da，是重复页，页码仍为 220）；第 4 页页眉为「2 2 2」（即 222）；第 5 页与第 4 页重复（页码 222）；第 6 页为空。即我实际看到的重印本页码是 219、220、222 三个，没有出现 221；这与核对员「印有页码 219 至 222」的范围说法一致，但存在 220 与 222 各重复一页、221 缺页的制版现象，这一点如实记录在此。
3. 原始会议录页码 49 至 52：我下载 Lagarias 的注释书目 https://arxiv.org/abs/math/0309224 并检索，其第 43 条为「John H. Conway (1972), Unpredicatable Iterations, In: Proc. 1972 Number Theory Conference, University of Colorado, Boulder, CO. 1972, pp. 49–52. (MR 52 #13717).」（条目里的标题拼写「Unpredicatable」照录 Lagarias 原文；Conway 论文本身拼作「Unpredictable」）。其后的注释说明该文陈述了 3x+1 问题、并证明一个形式上类似的更一般函数迭代问题在计算上不可判定。这与 bbchallenge wiki 的引用一致，页码结论（49 至 52）不变。

我原来的表述「我读的 PDF 上没有页码标记」就字面而言是错的，已按上述事实改为准确描述。两条意见我都确认核对员正确，未发现需要为原写法辩护之处；原结论（原始页码 49 至 52、BB(5) 论文的 19 位具名作者）保留，只更正描述。
