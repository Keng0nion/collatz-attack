# Hercher 2023 定理 21 的第三方质疑材料

收集日期：2026 年 10 月 21 日。收集范围：形式化项目、独立审计仓库、期刊评论、代码托管平台的 issue 讨论。核实纪律：以下每一条都注明我是否亲自打开了页面、读的是哪一个文件；能打开的和打不开的分开列。我没有编译任何 Lean 工程：本机没有 Lean 工具链（实测 `which lake lean elan` 无任何输出），所以所有关于 Lean 项目的陈述都来自我逐个读取的仓库源文件文本，不来自编译复核。

## 一句话背景

Hercher 2023 论文《There are no Collatz m-Cycles with m ≤ 91》（Journal of Integer Sequences 26，文章 23.3.5）的定理 21 在 2026 年被官方勘误：勘误承认「定理 21 证明第 14 页底部的推导 contains an error」，致谢 Xinjun Wang 指出，并给出一段凸性与多面体顶点论证来重建所需不等式。围绕「修正后能否保住 m ≤ 91、以及能否继续往上推」，出现了多个互不一致的第三方项目。下面是逐条材料。

## 一、争议各方立场总表（全部亲自打开）

1. PhilNorfleet/Hercher2023_lean：主张 82 到 91 的延伸经过一个错误步骤，只承认 m ≤ 82。2026 年 8 月 5 日创建，唯一一次推送也在当日。
2. azadveersingh（issue #1 的作者；仓库 collatz-research 已不可达，现行仓库 hercher-lean）：反驳上述主张，声称勘误修复了缺口、m ≤ 91 成立，并进一步做到 m ≥ 92、m ≥ 93。
3. justinalick/collatz-m-cycles-101-lean：接受勘误后的 m ≤ 91，条件性推出 m ≤ 101。2026 年 9 月 28 日创建。
4. Xinjun Wang（勘误所致谢的指错者）：Zenodo 预印本系列，从 m ≤ 94 推进到 m ≤ 95，明确声明「不使用定理 21」。
5. MaskoMys/Collatz-m-96-Lean-Formalization 与 MaskoMys/Collatz-m96-Certificates-Pipeline：另一条线（Mghirbi 的论文），声称 m = 92 到 96 被排除（等价于环至少有 97 个局部极小），把 Hercher 的增长律作为命名公理打包，不构成对定理 21 的质疑。
6. hsirven1/syracuse_search：独立审计项目，逐字复核了 Hercher v3 定理 21 第 14 页、勘误的凸模型、以及 Wang 的预印本；对 Wang 的 m ≤ 95 给出 NON VÉRIFIABLE 判定。
7. zbMATH 评论 Zbl 1536.11052（评审人 Olivier Rozier）：2023 年就写了定理 21 证明「has a potential flaw near the end」。

## 二、核心质疑者：PhilNorfleet/Hercher2023_lean

URL：https://github.com/PhilNorfleet/Hercher2023_lean
亲自打开：是。我读了 README.md、SUMMARY.md、Collatz/MainTheorem.lean、Collatz/Thm21.lean（均经 raw.githubusercontent.com 取源文件全文），以及 GitHub API 的仓库元数据与 issue 列表。

### 1. 它形式化的是哪条陈述、依赖哪些外部假设

主定理 `no_m_cycle_le_82`（Collatz/MainTheorem.lean，我读了全文）：给定 Barina 下界 `hbound`（凡不落入 1 的轨道元素都大于 704·2^60）与 Simons 与 de Weger 上界 `hSdW`（奇数步数 K < 1.4784·m·δ^m），则不存在最小 `nextMin` 周期 m ≤ 82 且不落入 1 的奇数 n₁。仓库自称「0 sorry、0 自定义公理、0 native_decide」，公理足迹 ⊆ {propext, Classical.choice, Quot.sound}。

两个外部假设以显式假设（不是公理、不是 sorry）进入：验证界 X0 = 704·2^60（Barina，J. Supercomputing 77 (2021)），以及 Simons 与 de Weger 的 K < 1.4784·m·δ^m（Acta Arith. 117 (2005) 定理 3）。注意：与 Hercher 原论文不同，这条路线不用 Rhin 型超越下界——SUMMARY.md 说 K 的下界侧「is proved here without any transcendence, via Legendre's theorem and the certified continued fraction of δ」，用到的收敛项分母是 `(of δ).dens 35 = 397560349370386783` 与 `dens 36 = 4242721909926539673`。

### 2. 它具体拒绝的是哪一步（逐字）

SUMMARY.md 设有专节「Deviation from the paper: the Theorem 21 tail error」。它先逐字引论文原文（arXiv:2201.00406v3 第 3 节）：

> "…and since `n_{m−m2+1+ℓ} < n_{m−m2+1}^{(δ^ℓ)} ≤ n_{m−m2+1}^δ`, we get the inequality `T(n_{m−m2+1+ℓ}) < 3/(2^v−1)^δ`."

然后给出两条指控（逐字）：

> 1. **A false inequality.** `n^{(δ^ℓ)} ≤ n^δ` fails for `ℓ ≥ 2`: since `δ > 1`, `δ^ℓ > δ`, and the base `n > 1`, so the exponentiation points the wrong way.
>
> 2. **A backwards deduction (fatal).** `T(n) < 3/n` is *decreasing* in `n`, so an **upper** bound on the later window minima `n_{i₀+ℓ}` can only yield a **lower** bound on `T(n_{i₀+ℓ})` — never the upper bound claimed. Obtaining `T(n_{i₀+ℓ}) < 3/(2^v−1)^δ` requires a **lower** bound `n_{i₀+ℓ} > (2^v−1)^δ` on the later window minima, which is never established and in fact contradicts Lemma 20 (`n_{i+1} < nᵢ^δ`) for `ℓ = 1`.

它还断言这一步「不是局部可修的」（逐字）：

> Only the *first* window minimum is provably large (`n_{i₀} ≥ 2^v − 1`). The pigeonhole step supplies only the *total* o-step count over the window, never a per-minimum lower bound. In the rigorous worst case one late window minimum absorbs essentially all the o-steps while the others sit near `X0`, so the best provable tail bound is `∑T ≈ m·3/X0`. We verified numerically that this honest bound **stalls the paper's bootstrap at `K ≈ 4.6·10¹⁸`**, which beats the Simons–de Weger upper bound only up to `m = 82`.

它自己的 Lean 里对应的 lemma 名：`thm21_v_bound`、`thm21_window_start_bound`、`thm21_sum_bound`（尾项用诚实的 `3 * ((m2 : ℝ) - 1) / X0`）、`thm21`（整体夹逼的诚实版本），以及走 Corollary 17 与 Legendre 路线的 `legendre_contradiction'`、`cor17`、`lemma22`、`CFDepth36`（这些名字我都在源文件里逐一读到）。SUMMARY.md 对 `thm21` 的原话是「**Proved with an honest, weaker tail term**…the paper's own tail term is not used because it is unsound」。

它对 zbMATH 的转引（逐字，我另用 zbMATH API 核对了原文，见第九节）：

> The zbMATH review of the paper (**Zbl 1536.11052**) independently flags the same issue: the reviewer *"wonders whether the proof of the main result could be simplified by using Corollary 17 instead of Theorem 21 whose proof has a potential flaw near the end."*

### 3. 替代结论与自述不确定性

替代结论：只到 m ≤ 82（「The headline number is `m ≤ 82`, not the paper's `m ≤ 91`… `m ≤ 82` is the honest ceiling reachable from the paper's *sound* lemmas」）。

自述的不确定性（逐字）：

> The theorem `m ≤ 91` itself is very likely true (Simons–de Weger established `m ≤ 68` by other means); it is *this proof* of the `82→91` extension that does not go through.
>
> *(A charitable possibility we could not rule out: the paper's Sagemath worksheet may compute `∑T` by a correct route, with only the printed prose flawed.)*

### 4. 有没有人反驳它

有，而且就挂在它自己的 issue 区（详见第三节）：唯一的 issue 至今开放、0 条评论、仓库自 2026 年 8 月 5 日后再无推送。我另用 grep 核实：README.md 与 SUMMARY.md 对「corrigendum」「Wang」「2026」的命中数均为 0，即仓库文档完全未提及 2026 年勘误与指错人（与项目笔记的记录一致）。

## 三、对质疑的直接反驳：issue #1

URL：https://github.com/PhilNorfleet/Hercher2023_lean/issues/1
亲自打开：是（GitHub API 取全文；0 条评论，2026 年 9 月 27 日 04:37 UTC 建立，至今 open）。

标题逐字：「Hercher's corrigendum (June 2026) fixes the Theorem 21 gap; full m ≤ 91 now formalized」。作者 azadveersingh。正文要点逐字：

> **1. Hercher has published a corrigendum for Theorem 21.** … It acknowledges the tail error you describe in `SUMMARY.md`, credits Xinjun Wang with finding it, and re-proves the Theorem 21 window bound with a convexity argument. So the gap *can* be fixed locally, and m ≤ 91 stands. (The zbMATH review Zbl 1536.11052 also flagged a possible flaw near the end of that proof.)
>
> **2. We have formalized the full m ≤ 91 in Lean 4.** It is here: https://github.com/azadveersingh/collatz-research (files `formal/Collatz/Hercher*.lean`, theorem `Collatz.Hercher.hercher_m_ge_92`)
> … It has no `sorry`, only the standard axioms, and passes `leanchecker`. We did not use your code (the repo has no licence). The development is independent.
>
> - **The corrigendum's key inequality has a short proof.** A sequence with cyclic constraints x_{i+1} ≤ δ x_i is an explicit convex combination of the rotations of (v, δv, …, δ^{n−1}v). The weights are (δx_{j−1} − x_j)/(v(δ^n − 1)). Jensen then gives the bound directly, with no vertex enumeration, and it needs only v > 0.
> - **The bootstrap does not need Theorem 14.** … X. Wang's preprint (Zenodo 10.5281/zenodo.21670936) likewise avoids Theorem 14.
>
> A short write-up is in `papers/hercher-lean/` in the same repository. Corrections are welcome.
> (Prepared with the help of an AI assistant; the Lean proofs are kernel-checked.)

要点：这是一条针对「82 是诚实上限」与「不可局部修复」两个论断的直接反驳，且援引勘误与 zbMATH 两个外部证据。它给的仓库链接 collatz-research 现已 404（见第十二节），但其指名的定理 `Collatz.Hercher.hercher_m_ge_92` 在同作者现行仓库 hercher-lean 中存在（见第四节）。

## 四、azadveersingh 系列：collatz-research 到 hercher-lean

URL：https://github.com/azadveersingh/hercher-lean
亲自打开：是。读了 README.md、formal/Collatz/HercherBridge.lean、formal/Collatz/HercherM93.lean、formal/Collatz/HercherWindow.lean、formal/Collatz/HercherTail.lean，以及 GitHub API 元数据、commit 列表。

关于旧地址：https://github.com/azadveersingh/collatz-research 经 API 与普通网页两次请求均返回 404，我打不开。现行仓库 hercher-lean 的创建时间是 2026 年 10 月 3 日，晚于 issue 发布日（9 月 27 日），且含 issue 中指名的同名定理；两仓库的关系我无法从公开页面确证（这是我的推断，不是页面上的陈述）。

### 1. 形式化的陈述与外部假设

README 引用论文：「Azad and Shastri L. Nimmagadda, *Collatz cycles have at least 93 local minima: a formal proof*, 2026」（该文我未找到任何 URL 或 DOI，见第十二节）。两条主结果：

1. `Collatz.Hercher.hercher_m_ge_92`（formal/Collatz/HercherBridge.lean，第 194 行附近，我读了全文）：显式假设三个已发布输入——`hver`（凡 1 ≤ n ≤ 695·2^60 都在 T 下到达 1，覆盖 Barina 2025 的 n < 2^71）、`hSdW75`（Simons 与 de Weger：无 m ≤ 75 的 m 圈）、`hSdW`（76 ≤ m ≤ 91 时 K ≤ sdwUpper m）；结论：任何周期的局部极小个数 m ≥ 92。文件内 docstring 逐字：「every nontrivial Collatz cycle has at least 92 local minima」。
2. `Collatz.Hercher.collatz_m_ge_93`（formal/Collatz/HercherM93.lean）：`hver`（n < 2^71）、`hSdW75`、`hSdW`（76 ≤ m ≤ 92）；结论 m ≥ 93。文件头注释逐字：「The case `m = 92`, following X. Wang (Zenodo 10.5281/zenodo.21670936) with a wider window」。

### 2. 它对争议步骤的处理（这不是拒绝，而是复核与替代）

HercherWindow.lean 文件头逐字（我读了全文）：

> # The window inequality behind Hercher's corrigendum
> Hercher (J. Integer Seq. 26 (2023), Art. 23.3.5; corrigendum June 2026) needs, for the quantities … The corrigendum argues via vertices of a polytope. Here we give a direct proof: a cyclic sequence with `x_{i+1} ≤ δ xᵢ` is an explicit convex combination of the rotations of the geometric sequence `(v, δv, …, δ^{N}v)`, with weights proportional to `δ x_{j−1} − x_j ≥ 0`. Jensen's inequality then gives the bound for every convex `φ` (`sum_le_sum_geometric`).

即：它接受勘误的修正方向，并把勘误的关键窗口不等式在 Lean 里重证了一遍（用 Jensen 代替顶点枚举）；没有拒绝定理 21 的任何一步，而是把 2023 年原推导判为「被勘误修复」。

### 3. 替代结论与自述不确定性

替代结论：m ≥ 92（Hercher 原结论的机器复核）外加 m ≥ 93（自己的延伸）；README 说「The external inputs … enter as explicit hypotheses of these theorems」。

自述不确定性／边界：`compute/experiments/005_wang_m92.py` 自称「an independent Python reproduction of Wang's m = 92 window exclusion」；README 说「The code contains no `sorry` and no `native_decide`」；论文本身（Azad 与 Nimmagadda）未给 URL。

### 4. 反驳迹象

无。仓库 0 issue（全状态查询）、0 star、单 commit（2026 年 10 月 3 日）。

## 五、条件性 m ≤ 101：justinalick/collatz-m-cycles-101-lean

URL：https://github.com/justinalick/collatz-m-cycles-101-lean
亲自打开：是。读了 README.md 与 Collatz/MCycle101.lean、Collatz/HercherVertex.lean 全文，以及 GitHub API 元数据、文件树、issue 列表（全状态 0 条）。

### 1. 形式化的陈述与外部假设

主定理（README 与 MCycle101.lean 一致）：

```lean
theorem Collatz.no_101_cycle_2_71
    (hX : ∀ n, 0 < n → n ≤ 2 ^ 71 → Reaches T n 1)
    (hR : RhinBound) :
    ∀ x p, 0 < x → 0 < p → T^[p] x = x → x ≠ 1 → x ≠ 2 → 102 ≤ numLocalMin x p
```

两个外部输入：「凡 0 < n ≤ 2^71 都到达 1」（Bařina，J. Supercomput. 81 (2025)，文章 810）与 `RhinBound`（Rhin 1987 的有效测度，经 Simons 与 de Weger 2005 引理 12 用于环；README 逐字：「It is a transcendence-theory input that is not in Mathlib」）。README 明确：「The hypotheses are parameters of the theorem, not axioms」；并称源代码无 sorry、无 native_decide、无 axiom，有 GitHub Actions 每次推送跑构建。

### 2. 它对争议步骤的处理

它不拒绝定理 21，而是「接受勘误后的 m ≤ 91」并把边界推到 101。README 逐字：

> The previous record was at least 92 local minima, i.e. no m-cycle with m ≤ 91 (C. Hercher, 2023). …
> This work stands on C. Hercher's proof that there are no m-cycles with m ≤ 91 (J. Integer Seq. 26 (2023), Art. 23.3.5, with the corrigendum of June 2026; the error it repairs was found by Xinjun Wang). Everything up to the list of surviving cycle shapes is his method: … the window bound (Theorem 21), …

它对定理 21 还有自己的替代量化：Collatz/HercherVertex.lean 文件头逐字：

> The corrigendum to Hercher's Theorem 21 bounds the window sum by the value of `Σ f(x_i)`, `f(x) = 3/(2^x − 1)`, at a vertex `(v, δv, …, δ^{m₂−1} v)` of a polyhedron, which gives `f(v) + (m₂ − 1) f(δ v)`. … This file uses a shorter argument that gives almost the same bound.

其中 `window_sum_le_two`、`exists_window_minima_two`、`theorem21_two` 是它自己版本的窗口界（相对于勘误顶点值差一个约 10⁻¹⁸ 的相对量，文件注释自称）。

### 3. 替代结论与自述不确定性

替代结论：m ≤ 101（等价地任何非平凡环至少 102 个局部极小），条件于上面两个输入。README 逐字声明边界：

> This is not a proof of the Collatz conjecture: it rules out cycles with at most 101 local minima and says nothing about cycles with more, or about divergent orbits.

不确定性与工艺声明（逐字）：

> Not yet refereed. Author: Justin Alick. The proofs, the Lean code and this repository were prepared with an AI coding assistant (Claude Code) under the author's direction; the author is responsible for the content.

> A paper with the human-readable proof is in preparation.

> Some docstrings refer to notes (`research_notes/…`, `docs/…`) of the private development repository; the mathematics they describe will be in the paper.

它还把两个前作列为相关工作（逐字）：「A partial formalization of Hercher's paper (m ≤ 82) is in `PhilNorfleet/Hercher2023_lean`; an independent formalization of m ≤ 91 from the Simons–de Weger bounds was announced in `azadveersingh/collatz-research` (27 September 2026)」——即它自己把 PhilNorfleet 的项目定性为「partial」。

### 4. 反驳迹象

未发现。0 issue、0 fork、0 star；GitHub issue 全网检索无引用其定理名的讨论；本报告完成时（2026 年 10 月 21 日）未见任何公开反驳或独立复核。

## 六、邻接的形式化：MaskoMys 两个仓库（m = 96 一线）

URL：https://github.com/MaskoMys/Collatz-m-96-Lean-Formalization 与 https://github.com/MaskoMys/Collatz-m96-Certificates-Pipeline
亲自打开：是（两个 README、docs/TRUST.md、docs/THEOREM_MAP.md 节选，以及 API 元数据）。

这一线基于 N. Mghirbi 的论文《Prefix Rigidity, Surplus Frontiers, and an Exact Certificate Excluding Collatz 96-Cycles》（2026），声称排除 m = 92 到 96 的环。Lean 侧主定理是 `no_nontrivial_collatz_96_cycle`（README 逐字：「the paper pushes this to `m = 96`」）；证书侧逐字：「Together with Hercher's published exclusion through `m=91`, this implies that any nontrivial positive Collatz cycle must have at least 97 local minima」。它不质疑定理 21，而是把 Hercher 的结果当输入：

1. Lean 仓库的主定理 `no_nontrivial_collatz_96_cycle` 依赖 4 条命名公理（TRUST.md 逐字列出）：`barina`（已发表）、`enclosure_above_window`（「packages Hercher's growth law (*arXiv* 2201.00406 / *JIS* 2023), the suffix-balance rotation lemma (§11.1), and the rational log/continued-fraction enclosures」，即把增长律打包为公理、不在 Lean 内重证）、`simons_deWeger`（已发表）、`finite_window_excluded`（75 分支搜索，不在核内重跑）。TRUST.md 自称「verified reduction, not a from-scratch in-kernel proof」。
2. 证书仓库（2026 年 8 月 20 日推送）自称对 m = 92 到 96 给出穷尽证书（372 分支、464 工作单元，C++17/GMP 与 Rust/rug 双引擎复算），并逐字声明：「Together with Hercher's published exclusion through `m=91`, this implies that any nontrivial positive Collatz cycle must have at least 97 local minima」，同时强调 `theorem_marker` 字段「remains null by design」（不能替代人类审读与同行评审）。

与争议步骤的关系：它把 Hercher 的增长律（含勘误所修补的同一支机制）原样作为外部公理吸收，属于「同一记录竞赛中的另一条线」，不是对定理 21 的质疑。另注意术语口径：MaskoMys 的「96-cycle」按「一个周期内恰有 96 个局部极小」计数。

## 七、指错者本人的预印本系列：Xinjun Wang（m ≤ 94、m ≤ 95）

材料：Zenodo 记录三条（我全部亲自打开了 API 元数据，并下载了最新一条的 PDF 全文）。

1. 10.5281/zenodo.20603589（2026 年 6 月 9 日）：《A Corrected Suffix-Balanced Global-Minimum Certificate for Excluding Collatz m-Cycles for m ≤ 94 (Expanded Version with Detailed Finite-Certificate Explanations)》，含 12 个 PDF 附件。
2. 10.5281/zenodo.21017296（2026 年 6 月 29 日）：《NON-EXISTENCE OF COLLATZ m-CYCLES FOR m ≤ 95》。
3. 10.5281/zenodo.21670936（2026 年 7 月 29 日，最新）：《NON-EXISTENCE OF COLLATZ m-CYCLES FOR m ≤ 95》，附件含 `verify_m91.cpp`、`verify_m92_m95_parallel_pruned_journal.cpp`、`datas_and_logs.7z` 与论文 PDF（563,945 字节）。

我下载并逐段读了第 3 条的 PDF 文本。要点：

1. 摘要逐字：「We prove, assuming the stated certified external inputs, that no non-trivial Collatz m-cycle exists for m ≤ 95. The proof combines the verification bound X = 2^71, the Simons–de Weger bounds for the total number of odd steps, a suffix-balanced cyclic block estimate, continued-fraction denominator tests for log₂3, and exact integer finite searches for the remaining cases m = 92, 93, 94, 95.」
2. 外部输入逐字（第 2 节）：（I1）环元素大于 X = 2^71（Bařina 计算验证）；（I2）K > 7·10^11（Simons 与 de Weger）；（I3）K < 1.4784·m·δ^m（Simons 与 de Weger）。
3. 对定理 21 的处理逐字：「In particular, we do not use Hercher's Theorem 21 [2]; the suffix-balanced argument below is used as a replacement for the consecutive-block contribution estimate.」以及 Remark 15：「The proof above does not use Hercher's consecutive-block contribution estimate. Instead, the suffix-balanced block selection gives lower bounds for the terms of each chosen block directly from suffix odd-step sums.」即：绕开定理 21（含修正后的窗口步），另起一套「后缀平衡块选择」。
4. 主定理逐字：「Theorem 14. Assuming the certified inputs in Section 2, there is no non-trivial Collatz m-cycle with m ≤ 95.」
5. 发表状态：PDF 版式写着「#Axx INTEGERS 26 (2026)」，但 Received、Revised、Accepted、Published 四栏全空；我检查了 INTEGERS 第 26 卷 2026 年索引页（https://math.colgate.edu/~integers/vol26.html，78,553 字节），全文检索「Collatz」0 命中（「Wang」2 命中均为无关文章）。所以截至我核对时，该稿不能按已发表对待（Zenodo 是自存档，不是评审证明）。
6. 与勘误的关系：Wang 就是勘误致谢的指错人（勘误逐字：「The author is highly grateful to Xinjun Wang, ORCID 0009-0007-5895-5984, for pointing out this mistake and for helpful discussions regarding its correction.」）。他的这一系列稿可视为「质疑的源头提供者 + 绕道重证」。

## 八、独立审计：hsirven1/syracuse_search（Étude 39、Revue 39B）

URL：https://github.com/hsirven1/syracuse_search
亲自打开：是。读了 PR #12、issue #13、PR #14 的 API 全文，并在分支 `research/etude39-cycle-audit` 与 `review/issue13-hercher-wang` 上读了报告全文 `research/ETUDE_39_RAPPORT.md`（15,775 字节）与 `research/REVIEW_39B_HERCHER_WANG.md`（16,520 字节）。

### 1. 它复核了什么、结论如何

Étude 39（PR #12，2026 年 10 月 16 日创建，仍为草稿）逐字摘要：

> Premier audit ciblé des cycles : verdict de recherche **ARRÊT**, zéro lemme nouveau retenu. **Audit du lemme exact suffix-balanced de Wang incomplet ; exclusion m≤94 NON VÉRIFIÉE.** Ne pas présenter ce travail comme une réfutation de Wang ou du corrigendum Hercher.
> Le rapport identifie deux défauts dans la dérivation du théorème 21 du préprint Hercher v3 effectivement obtenu sur un miroir GitHub. Il distingue cette version du corrigendum de juin 2026 inaccessible, les résultats 2005/2010 de Simons–de Weger et la formalisation conditionnelle jusqu'à m≤82.

即：这是一个独立第三方，**独立复核并确认了 Hercher v3 第 14 页的两个缺陷**（与 PhilNorfleet 的表述一致），但它同时声明「不足以推翻定理 23，也不足以推翻它当时读不到的勘误」。

### 2. 它列出的两个缺陷（逐字，法文）

> Deux défauts indépendants :
> 1. Pour n_i>1, δ>1 et ell≥2, **δ^ell>δ**, donc l'inégalité entre puissances est dans le mauvais sens. Avec n_i=2, `2^δ=3` mais `2^(δ²)=3^δ>3`. Aucun arrondi numérique n'est nécessaire.
> 2. Même une borne supérieure correcte sur n_(i+ell) ne majorerait pas son inverse. `R(x)<3/x` exige une **borne inférieure** sur x pour donner une nouvelle majoration. Le passage affiché ne l'apporte pas.

接着逐字：「Ceci établit une lacune dans cette dérivation de 2023. Cela ne suffit ni à réfuter le théorème 23, ni à réfuter le corrigendum non lu.」

### 3. 它对 PhilNorfleet 形式化的评价（逐字）

> Dépôt et sources relus statiquement, **pas compilés**. Ni équivalent du résultat publié corrigé, ni preuve indépendante de m≤91/94

以及

> La formalisation consultée remplace la queue contestée par `3(h−1)/X0` et son théorème principal `no_m_cycle_le_82` prend explicitement `hbound` et `hSdW` comme hypothèses externes : une fermeture d'axiomes standard ne prouverait pas ces prémisses.

### 4. Revue 39B（PR #14）对勘误与 Wang 的判定

PR #14 正文逐字：「Verdict global : **NON VÉRIFIABLE pour m≤95**, ARRÊT de recherche additionnelle. Aucun résultat de Wang ou du corrigendum original n'est déclaré réfuté.」报告中的分步判定表（逐字要点）：

> - Atteinte, sommets et majoration pour P_h(B) **fermé cycliquement**, B>G_h —— Justification mathématique donnée ici pour ce modèle transcrit ; pas une nouveauté revendiquée
> - Application du modèle fermé au bloc sélectionné par le corrigendum officiel —— **NON VÉRIFIABLE** sans le texte ; hypothèse de raccord à contrôler
> - Lien automatique bloc ouvert → même polyèdre cyclique fermé —— **RÉFUTÉ** au niveau de la relaxation, pas comme accusation envers l'auteur
> - Lemmes Wang 5–7 selon la transcription du suivi —— Démonstration cohérente sous les hypothèses indiquées ; original non relu
> - S₅=∅ et exhaustivité des branches —— **NON VÉRIFIABLE**, aucun artefact récupéré
> - Entrées externes et exclusion de tous les m≤95 —— **NON VÉRIFIABLE** dans cette revue

需要注明它对勘误「NON VÉRIFIÉ」的成因是访问受限而非数学异议：报告逐字说，它这边对勘误 PDF、JIS 的 `corrigendum.tex`、ResearchGate、Zenodo 21017296 等链接「tous renvoyé un tunnel HTTP 403」。而我这次直接取到了勘误 PDF（HTTP 200，124,287 字节，Last-Modified 2026 年 7 月 31 日 20:58:43 GMT），故它未能读的内容我读了；它读到的内容（两个缺陷的独立复核、凸模型的数学重写）我也读了。两边的证据可以互补。

### 5. 反驳迹象

无。它自己声明不做指控（「pas comme accusation envers l'auteur」「Ne pas présenter ce travail comme une réfutation」）。

## 九、期刊评论：zbMATH Zbl 1536.11052（Olivier Rozier）

URL：https://zbmath.org/1536.11052（网页版被 Cloudflare 拦截，正文经 https://api.zbmath.org/v1/document/1536.11052 取回，我读了 JSON 全文）
亲自打开：是（经 API）。评论人为 Olivier Rozier（Paris），记录日期 2023 年 8 月 28 日。

与定理 21 直接相关的句子逐字（我核对过与 PhilNorfleet 转引一致）：

> The reviewer wonders whether the proof of the main result could be simplified by using Corollary 17 instead of Theorem 21 whose proof has a potential flaw near the end.

同一评论还有一句相关的逐字：

> Thanks to a computer-assisted proof, he obtains a stronger constraint on the value of \(m\) (Corollary 19). Repeatedly using continued fraction expansions of \(\frac{\log 3}{\log 2}\), it is then inferred that there exists no \(m\)-cycle with \(m \leq 91\), which is the main result. Surprisingly, it does not seem to depend on Corollary 19.

这证明「定理 21 末尾有潜在瑕疵」的提法在 2023 年就出现在同行书评里，早于勘误（2026 年）与三个 Lean 项目（2026 年 6 月至 10 月）。

## 十、对照锚点：Hercher 官方勘误

URL：https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf（文章页 https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.html）
亲自打开：是。PDF 已下载（`curl` 返回 HTTP 200，124,287 字节），用 `pdftotext` 提取全文；2 页。

关键逐字（原文）：

> The derivation of the inequalities T(n_{m−m2+1+ℓ}) < 3/(2v−1)^δ in the proof of Theorem 21 at the bottom of page 14 contains an error.
>
> The author is highly grateful to Xinjun Wang, ORCID 0009-0007-58955984, for pointing out this mistake and for helpful discussions regarding its correction.

修正方式（逐字要点）：定义 x_i = log(n_i + 1) / log 2，把待证求和化为线性约束多面体上的极值问题，用 S 的凸性断言最大值在顶点取得（顶点坐标是几何序列 (v, δv, …, δ^{m₂−1}v) 的循环置换），从而重建尾部不等式；勘误不撤回主结论，也未改写「m ≤ 91」的表述。

时间信息（三处并列，均为我实测或页面原文）：JIS 文章页链接文字为「Corrigendum, June 14 2026」；PDF 的 HTTP Last-Modified 为 2026 年 7 月 31 日 20:58:43 GMT；PDF 元数据 CreationDate 为 2026 年 8 月 1 日 05:58:43 JST（即 UTC 7 月 31 日 20:58）。勘误本身不含日期行。

## 十一、事实核对与未决点（我的整理，含推断标注）

以下是我在本次收集里直接核到的硬事实：

1. 「82 到 91 那一步错误、只承认 m ≤ 82」的第三方 Lean 项目存在且可打开：PhilNorfleet/Hercher2023_lean，2026 年 8 月 5 日创建，README 与 SUMMARY 全文与项目笔记所述一致；其 SUMMARY 逐字给出错误的那一步（`n^{(δ^ℓ)} ≤ n^δ` 方向反了；且因 T(n) 随 n 递减，上界只能推下界），这两条指控被 hsirven1 的 Étude 39 独立复核确认（法文表述，见第八节）。
2. 「条件性 m ≤ 101」的 Lean 项目存在且可打开：justinalick/collatz-m-cycles-101-lean，2026 年 9 月 28 日创建，主定理 `Collatz.no_101_cycle_2_71` 以 2^71 验证界与 `RhinBound` 为显式假设。
3. 我在本次收集中找到的、对 PhilNorfleet 主张最直接的公开反驳是 issue #1（2026 年 9 月 27 日，azadveersingh），指出勘误已修复缺口、m ≤ 91 成立，并给出自己的 m ≥ 92 形式化；该 issue 至今 0 条回复、仓库自 8 月 5 日未再更新。
4. 我核实 PhilNorfleet 仓库文档对「corrigendum」「Wang」「2026」零命中——即它未处理（至少未在文档中提及）2026 年勘误，这一点与其批评所针对的版本（arXiv v3，2023 年 4 月 4 日）时间线一致。
5. 勘误、zbMATH 评论、Wang 的绕道重证（m ≤ 95）、azadveersingh 的 m ≥ 93、MaskoMys 的 97 个极小值主张、hsirven1 的 NON VÉRIFIABLE 判定，构成一个「谁也没把谁完全驳倒」的多方僵局：所有文件化项目都以外部假设（验证界、Rhin 型或 Simons 与 de Weger 界）为条件，没有端到端、去假设的形式化。
6. 【我的推断，非页面陈述】azadveersingh/hercher-lean 很可能就是 issue #1 里 collatz-research 的替代（创建时间晚于 issue，含同名定理`Collatz.Hercher.hercher_m_ge_92`），但旧地址 404、无法确认改名或重建。
7. 【非材料检查】我没有编译任何一个 Lean 项目：本机无 lake/lean/elan；两仓库都要求先下载 Mathlib 缓存。因此所有 Lean 相关结论都是「源文件文本存在且自洽」，不是「构建通过」。`#print axioms` 的输出我无法运行复现。

## 十二、打不开或找不到的材料

1. https://github.com/azadveersingh/collatz-research（issue #1 指名的仓库）——打不开：API 与网页均 404。尝试：`api.github.com/repos/azadveersingh/collatz-research`、`curl -o /dev/null -w "%{http_code}"` 对网页地址（404）；另查了该用户的全部公开仓库列表（7 个），无此名。
2. https://zbmath.org/1536.11052（网页版）——打不开：Cloudflare 挑战页（标题「Just a moment...」）。替代路径成功：api.zbmath.org 返回完整评论 JSON。
3. https://www.researchgate.net/publication/408180567_NON-EXISTENCE_OF_COLLATZ_m-CYCLES_FOR_m_95 ——打不开：HTTP 403。该链接出处为 hsirven1 的 issue #13 正文。
4. Azad 与 Nimmagadda 的论文《Collatz cycles have at least 93 local minima: a formal proof》（2026）——找不到：hercher-lean 的 README 只给文字引用，无 URL、无 DOI；我没有在本次工作内找到可打开的副本，也没有检索到其发表信息。
5. N. Mghirbi 的论文《Prefix Rigidity, Surplus Frontiers, and an Exact Certificate Excluding Collatz 96-Cycles》（2026）——找不到：MaskoMys 的 README 只给文字引用；Zenodo 检索无结果。
6. INTEGERS 期刊上 Wang 稿件的状态——未能确证：PDF 版式自称「INTEGERS 26 (2026)」，收稿日期栏为空；我核了 INTEGERS 第 26 卷索引页，全文无「Collatz」命中。故只能标为「截至核对时未见正式发表记录」，不能标为已发表或已接收。
7. hsirven1 审计中提到的旧链接（Zenodo 21017296、ResearchGate、JIS 目录）在它那边全部 403——这是它的记录，不是我的；其中 JIS 勘误我这边成功打开（见第十节）。

## 十三、全部 URL 清单（均按本次实测）

1. https://github.com/PhilNorfleet/Hercher2023_lean ；raw 版 README.md、SUMMARY.md、Collatz/MainTheorem.lean、Collatz/Thm21.lean ；issue：https://github.com/PhilNorfleet/Hercher2023_lean/issues/1
2. https://github.com/justinalick/collatz-m-cycles-101-lean ；raw 版 README.md、Collatz/MCycle101.lean、Collatz/HercherVertex.lean
3. https://github.com/azadveersingh/hercher-lean ；raw 版 README.md、formal/Collatz/HercherBridge.lean、HercherM93.lean、HercherWindow.lean、HercherTail.lean
4. https://github.com/MaskoMys/Collatz-m-96-Lean-Formalization ；https://github.com/MaskoMys/Collatz-m96-Certificates-Pipeline
5. https://zenodo.org/records/20603589 ；https://zenodo.org/records/21017296 ；https://zenodo.org/records/21670936
6. https://github.com/hsirven1/syracuse_search ；PR https://github.com/hsirven1/syracuse_search/pull/12 ；issue https://github.com/hsirven1/syracuse_search/issues/13 ；PR https://github.com/hsirven1/syracuse_search/pull/14 ；报告位于分支 `research/etude39-cycle-audit` 的 `research/ETUDE_39_RAPPORT.md` 与分支 `review/issue13-hercher-wang` 的 `research/REVIEW_39B_HERCHER_WANG.md`
7. https://zbmath.org/1536.11052 （正文经 https://api.zbmath.org/v1/document/1536.11052）
8. https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.html ；https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf
9. https://math.colgate.edu/~integers/vol26.html （INTEGERS 第 26 卷索引，用于发表状态核对）
