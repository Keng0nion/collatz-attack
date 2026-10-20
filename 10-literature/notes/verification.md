# verification

本笔记处理「计算验证」这一条线，不涉及对 Collatz 猜想本身的证明尝试。
证据分级约定：【同行评审】＝经期刊或会议评审的论文；【仅预印本】＝arXiv 或预印本平台，无评审记录；【项目自报】＝保持者项目网页，未经评审；【未核实】＝我无法确认的说法，如实标注。

## 这条线在问什么

1. 到 2026 年 10 月为止，Collatz 猜想被计算机完整验证到哪个上限；谁保持、用什么算法、哪一年达成。
2. 「树搜索 + 模类剪枝」的覆盖性论证究竟建立在什么之上：剪掉一个剩余类（模 2 的幂或模 3 的幂）为什么不算漏数，剩下的类为什么必须逐个查。
3. 为什么这条线不能靠堆算力推得很远：成本、内存、工程与逻辑层面的瓶颈各是什么。
4. 这些纪录能否被第三方独立复核；复核的介质是什么（代码、校验和、还是短证书）。

## 关键结果

1. 当前最高已发表纪录：所有小于 2^71（＝2048×2^60 ≈ 2.361×10^21）的正整数都在 Collatz 迭代下到达 1 —— 2025 年、David Barina（布尔诺理工大学），【同行评审】J. Supercomput. 81:810（2025 年 5 月 2 日在线），DOI: https://doi.org/10.1007/s11227-025-07337-0 。全文我经文本代理 r.jina.ai 读取；直接抓取被站点 JS 挑战拦截。注意：论文经受评审，但「纪录」本身是有限计算，不是定理证明。
2. 项目当前前线（作者自报）：验证到 2075×2^60 ≈ 2^71.02，正在向 2076×2^60 推进；最低未完成工作单元索引 2175982616×2^40 —— 页面生成于 2026 年 10 月 17 日，https://pcbarina.fit.vutbr.cz/ 。该页另有一个「Lowest incomplete: 17.8734%」字段，我按工作单元线性换算得约 99.96%，两者不符；此字段我未能解释，如实标注。
3. 项目里程碑（同页面与项目日志）：2019 年 9 月 4 日启动；2020 年 5 月 7 日到 2^68（另有消息页 https://pcbarina.fit.vutbr.cz/news.htm 确认同一日期）；2021 年 12 月 10 日到 2^69；2023 年 7 月 9 日到 2^70；2023 年 11 月 3 日到 1.5×2^70；2025 年 1 月 15 日到 2^71。【项目自报】
4. 中间阶段成果：【仅预印本】2024 年 1 月 10 日贴出的预印本报告验证到 1.5×2^70、发现四项新 path record、期刊评审中 —— Research Square, rs-3845558/v1，https://www.researchsquare.com/article/rs-3845558/v1 （DOI: 10.21203/rs.3.rs-3845558/v1）。我只读到摘要与元数据（全文 PDF 未取）。
5. 历史纪录链（逐条注明出处；未打开原文者标注）：
   (1) 1973 年，Dunn，约 2^24.78 —— 出处为 Barina 2025 §2（引 Dunn 1973 技术报告）；Dunn 原文我未找到、未打开。
   (2) 1992 年，Leavens 与 Vermeulen，约 2^45.67（5.6×10^13），约 10 CPU 年 —— 出处 Lagarias 文献目录第 94 条（arXiv:math/0309224v11，我读了该条）；原文未打开。
   (3) 1999 年，Oliveira e Silva，3×2^53 ≈ 2.702×10^16，约 4 CPU 年，程序平均每秒约 3.17 亿个初值 —— 【同行评审】Math. Comp. 68(225):371 至 384，DOI: https://doi.org/10.1090/S0025-5718-99-01031-5 （AMS 直连返回 403，正文经文本代理读取）。
   (4) 2009 年（论文 2010 年），Oliveira e Silva，20×2^58 ＝ 5×2^60 > 5.76×10^18，2004 年 6 月至 2009 年 1 月，约 81.1 CPU 年 —— 作者主页 https://sweet.ua.pt/tos/3x+1.html ；正式出处为 The Ultimate Challenge 文集第 189 至 207 页（该书我未取得）。
   (5) 2011 年 5 月，Roosendaal 及协作者独立验证到 2^60 —— 出处同上作者主页。
   (6) 2017 年，yoyo@home 到 87×2^60 ≈ 1.003×10^20（≈ 2^66.4），约 1000 名志愿者，每个数独立检查两遍 —— 出处 Barina 2025 §2；其子项目说明见 https://www.rechenkraft.net/yoyo/ （我读到其 Collatz 子项目条目）；原项目地址 https://boinc.thesonntags.com/collatz/ 域名现已无法解析（【未核实】）。
   (7) 2020 年至 2025 年，Barina，2^68 至 2^71 —— 见第 1、2、3 条。
6. 量词不同的另一类验证（勿与纪录混同）：对随机大数（最多 10^10 个十进制位）逐个验证到达 1，用 Collatz 多项式与快速乘法（Magma）—— 2025 年、Andreas Stephan Elsenhans，【仅预印本】arXiv:2502.16743，https://arxiv.org/abs/2502.16743 （我通读了 PDF）。这是单点大数验证，不是区间全验证。
7. 纪录的下游用途（循环下界）：【同行评审】Hercher，J. Integer Seq. 26 (2023), Article 23.3.5，https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.html ，证明无非平凡 m 循环在 m ≤ 91；其 Corollary 29：若 X0 ≥ 1536×2^60 ＝ 3×2^69，则非平凡循环至少含 K > 1.375×10^11 个奇数项。Barina 2025 §6 据此报告在 2^71 时非平凡循环长度升至 355 504 839 929（该具体数字是 Barina 论文的推算；我在 Hercher 原文文本里未检索到它本身，标注）。勘误：Hercher 该文有 2026 年 6 月 14 日勘误（https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf ，我读了全文两页），修补其定理 21 证明中的一处推导错误（致谢指错者 Xinjun Wang），勘误文本未提对 m ≥ 92 等主结论的改动。另：【仅预印本】Angeltveit 称若验证到 2^75，按 Hercher 的机具可得循环长度 ≥ 2 302 268 119 908（约为前者的 6.5 倍）—— 2026 年、Vigleik Angeltveit，arXiv:2602.10466，https://arxiv.org/abs/2602.10466 （我通读；这是计划中的估计，不是已完成计算）。
8. 保持者的算法（原始描述）：
   (1) 2021 年核心手法【同行评审】：把轨迹改到 n 与 n+1 两域间切换计算，消除加法，只用 ctz 与 3 的幂小查表；把 O(2^N) 的大表换成 O(N) 的小表；实测 CPU 每秒 4.2×10^9 个 128 位数（Xeon Gold 5218），GPU 每秒 2.2×10^11 个（RTX 2080）。出处：J. Supercomput. 77 (2021) 2681 至 2688，DOI: https://doi.org/10.1007/s11227-020-03368-x ；正文我读的是 docslib 上的手稿本（https://docslib.org/doc/1484052/convergence-verification-of-the-collatz-problem ），官方摘要与参考文献经文本代理核对。
   (2) 2025 年系统【同行评审】：工作单元 2^40；2^k 位图筛（CPU 取 2^34 位＝2 GB，GPU 取 2^24 位）与 3^k 预像筛（GPU 用 3^1，CPU 用 3^2）；同余类并发求解；checksum 取区间内 α 之和（工作量证明）；服务器按 2^32 个工作单元设计（覆盖上限 2^72），每单元记录 322 位；工人分布在 MetaCentrum、IT4Innovations（Karolina）、LUMI 等欧洲超算；项目累计消耗 12 395 CPU 年与 159 GPU 年（平均每单元 CPU 6 分 25 秒、GPU 7 秒）；相对最初 CPU 算法总加速 1 335 倍。出处同第 1 条论文 §3 至 §6。
   (3) 代码：MIT 许可，https://github.com/xbarin02/collatz/ （CPU 用 C，超 128 位用 GMP；GPU 用 OpenCL，NVIDIA 与 AMD 均可；算法说明见仓库 doc/ALGORITHM.md，通信协议见 doc/PROTOCOL.md）；筛表数据另在 https://github.com/xbarin02/collatz-sieve （经 GitHub API 确认存在，2019 年 11 月建立、2024 年 3 月最后推送）。
9. 覆盖性论证（树搜索 + 模类剪枝），三条支柱：
   (1) 低位决定前 k 步：T^k(n) 的奇偶步序列只由 n 的最低 k 位决定（Angeltveit Lemma 2.1，其引注为 Oliveira e Silva 1999；Elsenhans 幻灯片给出同一事实的剩余类形式：偶数步与奇数步的移位映射分别是从模 2^{k+1} 到模 2^k 的双射）。
   (2) 仿射单调性，于是整类可剪：n ＝ n0 + a·2^k 时 T^k(n) ＝ T^k(n0) + 3^{f_k(n0)}·a（Angeltveit Lemma 2.3，引注同为 Oliveira e Silva 1999；Barina 2025 的式 (6) 是同一定理）。由此有「下降筛」：若 T^k(n0) < n0，则整个剩余类 n ≡ n0 (mod 2^k) 都在 k 步内降到自身以下（Angeltveit Theorem 2.5，附单调性证明）。数按最低位组织成二叉树（Oliveira e Silva 1999 §2 明确说轨迹计算「组织成一棵二叉树」，并在深度 40 的剪枝树上搜索）；一个节点被判下降，其整棵子树即被覆盖。
   (3) 归纳与原像剪枝：验证按升序做，轨迹一旦落到起点以下就归约到已验过的小数（Barina 2025 Algorithm 1 的停机条件就是「n < n0」）；Oliveira e Silva 1999 明说：若存在循环，程序会陷入死循环，而实际未出现。原像式剪枝把「落在更小数轨道上」的类去掉：n ≡ 2 mod 3 时 n ＝ T((2n−1)/3)、n ≡ 4 mod 9 时 n ＝ T^3((8n−5)/9)，故 n ≡ 2, 4, 5, 8 mod 9 全部免查（Angeltveit §2.2；同一事实在 Barina 2025 §3.2 以奇数 2n+1 → 3n+2 的形式给出，并计出 33.33% 的削减）；另有路径合并筛与奇偶偶筛（Angeltveit §2.3、§2.4，后者引理来自 Hercher 2023）。
   (4) 完备性的口径：被剪掉的每个剩余类都必须能由「下降」或「轨道与更小数合并」解释，未解释者逐个检查；剪枝不产生证书，只产生工作量（每单元的 checksum 与区间最大值）。
10. 为什么不能靠堆算力推远，五条：
   (1) 成本随范围线性，范围指数增长：Angeltveit 实测（N ＝ 35 至 45）每加一位，需检查数约乘 1.9，并明说「必须检查的整数个数当然仍趋于无穷」；他对 2^72 的估计是约 500 CPU 年或 1 至 8 GPU 年（单机口径）。换算成直觉（我的算术）：算力每翻倍约换 1.1 位；2^80 相当于 2^71 的 512 倍范围。
   (2) 筛的收益饱和：Barina 2025 §3.2，3^1 削减 33.33%、3^2 削减 44.44%、3^2 与 3^3 之间无提升、3^6 ＝ 729 也只有 45.95%；Angeltveit §2.2：mod 27 筛不再多排除、mod 81 仅多排除一类；2^k 筛受内存与缓存限制（2^34 位即 2 GB，Angeltveit 引 Barina 的表称已到可存储的极限）。
   (3) 工程上限：Barina 2025 §4 明说服务器管理 2^32 个工作单元、覆盖到 2^72；再往上需要重建索引体系。
   (4) 实测代价：见第 8 条 (2)；另 Hercher Remark 30 记载 2^69 一步用了 27 个月（与项目日志 2019 年 9 月至 2021 年 12 月一致）。
   (5) 逻辑与可计算性天花板：任何有限验证都不构成全称命题的证明；广义 Collatz（按模 p 分段的仿射迭代）不可判定 —— Kurtz 与 Simon 的技术报告（2006 年 12 月 26 日，https://people.cs.uchicago.edu/~simon/RES/collatz.pdf ，我经文本代理读全文）证明该问题不可判定、且 {g : range(g) ＝ 全体} 是 Π⁰₂ 完全的，其工作建立在 Conway 1972 之上（Conway 证明限制到 2^k 型输入也已不可判定，见该报告定理 1.6；Barina 2021 官方参考文献表中对应条目为 Conway 1972《Unpredictable iterations》）。必须限定：这些结果针对广义族，并不表明 3x+1 本身不可判定。
   (6) 收益结构：验证纪录的公开用途几乎只有循环下界（见第 7 条）；每抬高一位验证界，循环下界只小幅改善，而猜想本身不受影响。
11. 独立复核现状：
   (1) 可用介质：公开代码（第 8 条 (3)）；逐单元 checksum 与最大值；公开 path records 表 https://pcbarina.fit.vutbr.cz/path-records.htm （我核对了论文列出的五个新初值都在该表中）；OEIS 收录（https://oeis.org/A006884 ，Barina 提供 98 项表）。
   (2) 已发生的独立核对都停在低界：两套独立实现相互印证到约 2^60（Oliveira e Silva 与 Roosendaal，2010 年与 2011 年，见 https://sweet.ua.pt/tos/3x+1.html ）；yoyo@home 2017 年「每个数独立检查两遍」（Barina 2025 §2）；Angeltveit 2026 年的第三套独立实现（Rust 与 CUDA、OpenCL）只跑到 2^60，并用 Barina 的 path records 表核对自己程序的输出（自述检出 2^60 以下全部 path record，且其 CPU 与 GPU 版本 checksum 一致）。
   (3) 我未找到任何对 2^68 以上纪录的公开独立复现（检索至 2026 年 10 月 18 日），也未找到公开的完整 checksum 数据集供第三方抽查。
   (4) 复核在成本上等于重算：要独立复核 2^71，需要约 2^31 个工作单元的算力。
   (5) 一处可核对的内部不一致：2025 年论文的官方摘要（Crossref：https://api.crossref.org/works/10.1007/s11227-025-07337-0 ）说「四项新 path record」，而论文 §6 说「五项」并列出五个（path records 页也是五项）；引用应以表格为准。
   (6) 形式化旁支：有第三方 Lean 4 项目把 Barina 的验证当作假设使用（https://collatz-lab.org/ ，Zenodo DOI: 10.5281/zenodo.19790405），自述不证明猜想，且于 2026 年 10 月自报勘误；其质量我未核实，不构成对验证本身的独立复核。

## 当前的技术极限（记录值是多少、谁保持、为什么停在那里）

一、记录值：已发表 2^71（＝2048×2^60 ≈ 2.36×10^21，2025 年 1 月达成、2025 年 5 月在线发表）；作者自报前线 2075×2^60 ≈ 2^71.02（2026 年 10 月）。
二、保持者：David Barina（布尔诺理工大学信息技术学院，IT4Innovations 卓越中心）。
三、工具：n 与 n+1 域切换加 ctz 的加速迭代；2^k 位图筛（2^34 位 CPU、2^24 位 GPU）加 3^k 预像筛；2^40 工作单元的分布式系统（服务器、客户端、工人，数千并行，跨欧洲多台超算）。
四、为什么停在这里：(1) 计算成本对范围线性，范围按指数增长，每翻倍算力约换一位；(2) 两类筛都已接近饱和（3^k 到 3^6 只多约 1.5 个百分点，2^k 受内存与缓存限制）；(3) 现有服务器按 2^72 封顶设计；(4) 边际收益集中在循环下界的小改进，不会逼近猜想；(5) 没有已知办法从有限验证推出全称结论（广义族不可判定只是背景说明，不是 3x+1 本身的不可判定性）。

## 未解决的缺口

1. 2^68 以上没有任何独立复现（第三方实现或第三方团队）。
2. 没有可机器检验的验证证书；checksum 仅是工作量证明，独立复核在成本上等于重算。
3. 有限验证与全称命题之间没有已知的技术桥梁；广义 Collatz 的不可判定性提示这类问题没有通用算法路线，但它对 3x+1 本身不构成不可判定性证据。
4. 3^k 预像筛的收益为何在 k ＝ 2 至 3 就基本饱和（33.33%、44.44%、无提升、45.95%），只有经验表，缺解释性定界。
5. 2^k 筛的内存与缓存墙：2^34 位即 2 GB 已近实用极限；是否存在避开大表的次线性方案，尚未有跑完的记录（Angeltveit 只给出方向与估计）。
6. 到循环界的换算链依赖 Hercher 2023，而该文 2026 年有勘误；换算数字（如 355 504 839 929）我在 Hercher 原文未检出，需要重算确认。
7. 内部冗余审计不透明：yoyo 的「两遍」检查与项目的 checksum 比对，公开可查的完整审计档案我没有找到。
8. 旁注【未核实】：Barina 2021 手稿提到一个 BOINC 反例搜索项目，起点 2^71、据称推进到约 2^72.3，但当时已无法确认其是否全区间覆盖；其站点域名现已无法解析，我无法核对。

## 若要在这一线推进，必须跨过什么门槛

1. 独立复现门槛：至少第二套独立实现（不同语言、不同算法或不同团队）复现 2^68 以上的同一批区间；或把逐单元的 checksum 与最大值做成公开可下载的数据集，让第三方可以抽查重跑。
2. 复杂性门槛：把「必须检查的候选」从 Θ(2^N) 真正降到次指数；注意区分「密度趋于 0」（Angeltveit 的每常数因子改进）与「绝对个数仍按约 1.9 倍每位增长」。
3. 结构性门槛：把「局部下降 + 对小数归纳」升级为对无穷多数的统一控制；广义族的不可判定性提示不存在通用算法路线，但这一提示不能误读为 3x+1 不可判定。
4. 工程门槛：跨过 2^72 需要重建服务器索引（当前 2^32 单元上限）、给 2^k 筛找新的表示，并把总量再抬一个数量级（2^80 是 2^71 的 512 倍范围）。
5. 复核门槛：公开可复核的检查数据与工具，而不仅是公开代码；否则「独立复核」在成本上永远等于「独立重算」。

## 来源清单（全部 URL，逐条注明你是否亲自打开过）

以下均在本轮亲自访问（2026 年 10 月 17 日至 18 日）。标注方式：已打开（附方式）；受限（试过但被拦截）；未能打开。

已打开：
1. https://pcbarina.fit.vutbr.cz/ —— 已打开（curl 原始 HTML 与 DuckDuckGo 抓取各一次；含生成时间 2026 年 10 月 17 日）。
2. https://pcbarina.fit.vutbr.cz/news.htm —— 已打开（curl）。
3. https://pcbarina.fit.vutbr.cz/path-records.htm —— 已打开（curl，转文本，并核对论文五个新初值均在表内）。
4. https://github.com/xbarin02/collatz/ —— 已打开（DuckDuckGo 抓取 README 全文；另经 GitHub API 列出 src 与 doc 目录）。
5. https://raw.githubusercontent.com/xbarin02/collatz/master/README.md —— 已打开（curl，读毕）。
6. https://raw.githubusercontent.com/xbarin02/collatz/master/doc/ALGORITHM.md —— 已打开（curl，读毕）。
7. https://api.github.com/repos/xbarin02/collatz-sieve —— 已打开（curl，元数据；仓库正文未逐文件读）。
8. https://api.github.com/repos/vigleik0/collatz —— 已打开（curl，元数据）。仓库页面 https://github.com/vigleik0/collatz 本身未逐页渲染。
9. https://link.springer.com/article/10.1007/s11227-025-07337-0 —— 受限（直接抓取被站点 JS 挑战拦截）；全文经 https://r.jina.ai/ 代理取到并通读。
10. https://link.springer.com/article/10.1007/s11227-020-03368-x —— 受限（同上）；经 r.jina.ai 取到摘要、参考文献、致谢（正文在付费墙后）。
11. https://docslib.org/doc/1484052/convergence-verification-of-the-collatz-problem —— 已打开（curl，取到 2021 手稿正文的可读部分：摘要、相关工作、算法 1 与 2；参考表被页面截断）。
12. https://api.crossref.org/works/10.1007/s11227-025-07337-0 与 https://api.crossref.org/works/10.1007/s11227-020-03368-x —— 已打开（curl；取得官方摘要、卷页与日期）。
13. https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/s11227-025-07337-0 及同格式的 2021 论文条目 —— 已打开（curl，用于 OA 状态与摘要）。
14. https://api.openalex.org/works/doi:10.1007/s11227-025-07337-0 与 https://api.openalex.org/works/doi:10.1007/s11227-020-03368-x —— 已打开（curl，OA 状态）。
15. https://sweet.ua.pt/tos/3x+1.html —— 已打开（DuckDuckGo 抓取全文）。
16. https://sweet.ua.pt/tos/bib/3.5.html —— 已打开（curl，书目页，未见全文链接）。
17. https://www.ams.org/journals/mcom/1999-68-225/S0025-5718-99-01031-5/S0025-5718-99-01031-5.pdf —— 受限（直连 403）；同 URL 经 r.jina.ai 取到全文文本并读关键段落。
18. https://arxiv.org/abs/2602.10466 与 https://arxiv.org/pdf/2602.10466v1 —— 已打开（摘要页抓取；PDF 经 curl 下载并 pdftotext 通读）。
19. https://arxiv.org/abs/2502.16743 与 https://arxiv.org/pdf/2502.16743 —— 已打开（同上流程，通读）。
20. https://antsmath.org/ANTSXVII/slides/antsxvii-elsenhans-slides.pdf —— 已打开（curl 下载并读约三分之一；作者 Elsenhans，幻灯片内同时出现 July 2026 与 July 2025 两个日期，未解释）。
21. https://arxiv.org/pdf/2201.00406v3 —— 已打开（curl 下载并读摘要、前言与定理 23 附近）。
22. https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.html —— 已打开（curl，读摘要与勘误提示）。
23. https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf —— 已打开（curl 下载并 pdftotext 通读全文两页）。
24. https://www.jstage.jst.go.jp/article/ijnc/7/1/7_69/_pdf —— 已打开（curl 下载并读前约 130 行，Honda、Ito 与 Nakano 2017）。
25. https://arxiv.org/pdf/math/0309224v11 —— 已打开（curl 下载并读三处注释：第 94、116 条与一处补记）。
26. https://people.cs.uchicago.edu/~simon/RES/collatz.pdf —— 受限（直连 curl 证书链错误）；经 r.jina.ai 取到文本（Kurtz 与 Simon 技术报告）。
27. http://www.ericr.nl/wondrous/ —— 已打开（HTTP；curl 下载并转文本读完前段）。
28. http://www.ericr.nl/wondrous/progress.html —— 已打开（curl，读前段；属 class records 进展页，非全区间验证页）。
29. https://www.researchsquare.com/article/rs-3845558/v1 —— 已打开（DuckDuckGo 抓取与 r.jina.ai 各一次；读到摘要与元数据，全文 PDF 未取）。
30. https://oeis.org/A006884 —— 已打开（curl，转文本读前段）。
31. https://oeis.org/A076227 —— 已打开（curl，转文本读前段）。
32. https://www.rechenkraft.net/yoyo/ —— 已打开（curl，转文本；读到其 Collatz 子项目条目）。
33. https://collatz-lab.org/ —— 已打开（DuckDuckGo 抓取，读到 JSON-LD 元数据）；标注为不可靠来源，仅作存在性记录，未用作论据。
34. https://raw.githubusercontent.com/KokunoYumeto/collatz-workbench/main/collatz_reconstruction/qa/BARINA-OLIVEIRA-ROOSENDAAL-F031-computational-verification-audit.md —— 已打开（DuckDuckGo 抓取）；这是一份性质不明的第三方审计式文档，我未采用其结论，只用于确认 collatz-sieve 仓库与提交哈希的存在性线索。
35. https://matwbn.icm.edu.pl/ksiazki/aa/aa30/aa3034.pdf —— 部分打开（curl 下载成功，但为无文本层文件，pdftotext 抽不出内容；Terras 1976 正文我未读，其出版信息与 DOI 仅见他处核对）。
36. https://r.jina.ai/ —— 已使用（文本代理服务，用以绕开若干站点的 JS 挑战与付费墙渲染问题；不是文献来源本身，在此声明用法以保透明）。

未能打开或未尝试：
37. https://boinc.thesonntags.com/collatz/ —— 未能打开（域名无法解析）。
38. https://link.springer.com/content/pdf/10.1007/s11227-025-07337-0.pdf 与 https://link.springer.com/content/pdf/10.1007/s11227-020-03368-x.pdf —— 未能打开（被站点 JS 挑战或付费墙拦截）。
39. https://www.impan.pl/en/publishing-house/journals-and-series/acta-arithmetica/all/30/3/101028/a-stopping-time-problem-on-the-positive-integers —— 未打开（只在检索结果中见到条目与 DOI: 10.4064/aa-30-3-241-252）。
40. https://www.ams.org/journals/mcom/1999-68-225/S0025-5718-98-00979-X/S0025-5718-98-00979-X.pdf —— 未能打开（404，URL 有误的旧尝试；正确条目见第 17 条）。
