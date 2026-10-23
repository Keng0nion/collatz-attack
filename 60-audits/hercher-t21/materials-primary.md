# Hercher 定理 21 争议：一手材料汇总（materials-primary.md）

材料收集员·一手｜收集时间：2026 年 10 月 21 日｜工作目录：`/Users/luna/Documents/math IA`
本机工作目录（本次全部下载物与抽取文本所在）：`/tmp/hercher-audit/`

## 方法与诚实纪律（先读这一节）

1. 本文件只登记我在本次会话中**亲自下载、亲自打开、亲自读**的东西。每条材料下都写明「我是否亲自打开」与「关于争议步骤它说了什么」。
2. 项目笔记（`attempt.md`、`rebuttal-2.md`、`rebuttal-round1.md`、`README.md`）里写过的数字**一律不作为一手证据**；凡本文件引用它们之处都注明「项目笔记称」，并在第六节给出逐条回原文核对的对账表。
3. 记号：`^` 记上标（`(2^v−1)^δ` 即 (2^v − 1) 的 δ 次幂），`_{...}` 记下标。凡 pdftotext 抽取时上标被压平、需要按版面渲染图（pdftoppm）转写的公式，均注明「按渲染图核对」。
4. 状态用语：**已核验**指本次会话亲自执行命令所得；**我的推断**指原文没有的一句话，由我读出的内容推出；**未核实／未找到**指我没能做到或没检索到。

---

## 一、材料 1：Hercher 2023 原文（JIS 26（2023），文章 23.3.5）

### 出处与版本信息

1. 论文 PDF：`https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf`
2. 本次下载（已核验）：HTTP 200，250655 字节，22 页；md5 `3e2377bef0b1c0435dc455c9bbee43a1`；PDF 内部逐字节为 `/CreationDate (D:20230315085242-04'00')`，即 2023 年 3 月 15 日 08:52:42（UTC−4）。
3. 摘要页：`https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.html`（HTTP 200）。页内出版信息逐字：`Received January 23 2022; revised version received January 24 2022, December 21 2022; December 28 2022; March 12 2023. Published in Journal of Integer Sequences, March 15 2023.`
4. 目录页：`https://cs.uwaterloo.ca/journals/JIS/vol26.html`（HTTP 200）。

### 我是否亲自打开

是。`pdftotext -layout hercher5.pdf hercher5.txt`（1256 行）；并对第 13、14 页用 `pdftoppm -png -r 150` 渲染成图（`p13-13.png`、`p14-14.png`），逐字读了公式的上下标。

### 关于争议步骤它说了什么

争议步骤就是**本文（2023 年印刷版）Theorem 21 证明第 14 页靠末尾的那一步**（把窗口内各局部极小值的 `T` 求和用几何序列界住那一步）。论文自身**没有任何**错误标注或勘误提示，勘误是 2026 年另行发布的（见材料 2）。

### 争议步骤的逐字文本（文章第 14 页）

`pdftotext -layout` 原始输出（上标被压平，照录；`hercher5.txt` 第 799 至 801 行）：

```
                                nm−m2 +1+ℓ < nm−m2 +1 ≤ nδm−m2 +1 ,
                                            3
we get the inequality T (nm−m2 +1+ℓ ) < (2v −1) δ . Using this together with Theorem 14 and
```

按第 14 页渲染图核对的逐字转写（含上下标记号）：

1. `n_{m−m₂+1+ℓ} < n_{(m−m₂+1)}^{(δ^ℓ)} ≤ n_{m−m₂+1}^{δ}`，
2. 「于是 `T(n_{m−m₂+1+ℓ}) < 3/(2^v−1)^δ`」（δ 是分母括号整体的上标；`3/` 为分子三）。

同页的护栏句（按渲染图转写）：

1. 由 `v` 的定义：`v · (δ^{m₂}−1)/(δ−1) = (m₂/m)·K`，故 `v ≤ log(n_{m−m₂+1}+1)/log(2)`，等价地 `2^v − 1 ≤ n_{m−m₂+1}`；
2. 于是 `T(n_{m−m₂+1}) < 3/(2^v − 1)`；
3. 该步服务的终式（同页，按渲染图核对）：
   `Σ_{i=1}^{m} T(n_i) = Σ_{i=1}^{m−m₂} T(n_i) + T(n_{m−m₂+1}) + Σ_{i=m−m₂+1+1}^{m} T(n_i) < (97(m−m₂)+1)/(54·X₀) + 3/(2^v−1) + 3(m₂−1)/(2^v−1)^δ`。

**我的推断（非原文）**：第二个不等号 `n^{(δ^ℓ)} ≤ n^{δ}` 在 ℓ ≥ 2 时为假：δ = log 3/log 2 ≈ 1.5850 > 1，故 δ^ℓ > δ；底数 n > X₀ > 1，故 n^{δ^ℓ} > n^{δ}。此外整个推理方向也反：`T` 随 `n` 递减，`n` 的上界只能给出 `T` 的下界。这两条与 2026 年勘误「contains an error」（材料 2）方向一致；第三方 Lean 项目对同一步的指控原文属 `materials-thirdparty.md` 范围，本文件不重复。

### Theorem 21 全文（文章第 13 页，按渲染图转写，含上下标）

> **Theorem 21.** Let K be the number of odd numbers in a given m-cycle, and let L be the number of even numbers in it. Further, assume there exists a positive integer m₂ with
>
> `m₂ ≤ m` and `(δ^{m₂} − 1)/(δ − 1) · log((162/97)·X₀)/log(2) ≤ (m₂/m)·K`.
>
> Let `v = (m₂/m)·K·(δ−1)/(δ^{m₂}−1)`. Then we get
>
> `δ < (K+L)/K < δ + 1/(K·3·log(2)) · ( (97(m−m₂)+73)/(54·X₀) + 3/(2^v − 1) + 3(m₂−1)/(2^v−1)^δ )`.
>
> If m₂ = m − 1 we get the better estimate
>
> `δ < (K+L)/K < δ + 1/(K·3·log(2)) · ( 3/X₀ + 3/(2^v − 1) + 3(m−2)/(2^v−1)^δ )`
>
> and for m₂ = m
>
> `δ < (K+L)/K < δ + 1/(K·3·log(2)) · ( 3/(2^v − 1) + 3(m−1)/(2^v−1)^δ )`.

其后「Proof.」段落（按渲染图核对）的骨架：m₂ 个连续局部极小值的存在性论证；`k_i ≤ log(n_i+1)/log(2)`（Lemma 8）与 `n_{i+1} < n_i^δ`（Lemma 20）推出 `k_{i+ℓ} < δ^ℓ · log(n_i+1)/log(2)`；`n_{m−m₂+1} + 1 > (162/97)·X₀`；`T(n_{m−m₂+1}) < 3/n_{m−m₂+1} < (97/54)·1/X₀`（由 Remark 7）。

论文内部相关定义（供下游直接引用，`hercher5.txt` 行号）：

1. 第 83 行：`X₀ = 695 · 2^60`（Definition 4，验证界）；
2. 第 190 行：`Remark 7. We have T(n_i) < 3/n_i < 3/X₀ for all 1 ≤ i.`（`T(n_i) := Σ_{t=0}^{k_i−1} 1/C^t(n_i)`）；
3. 第 673 至 674 行：`The following lemma also can be found in [12].` 紧接 `Lemma 20. Let n_i, n_{i+1} be two successive local minima in an m-cycle. Then we have n_{i+1} < n_i^δ.`（即 **Lemma 20 被 Hercher 归功于 [12] 即 SdW**）；
4. 第 598 至 601 行：`Corollary 17. With K, L as in Theorem 16, we have δ < (K+L)/K < δ + 1/(K · 3 log(2)) · (97/54) · m · (1/X₀).`（zbMATH 审稿人建议用它替代 Theorem 21）。

### Theorem 23 与七步自举（文章第 15、16 页，`hercher5.txt` 第 850 至 880 行）

逐字（该段 pdftotext 基本无损，下标已按原文核对；`bounnd` 为该文印刷原样的拼写，照录）：

> **Theorem 23 (Main Theorem).** There is no m-cycle with m ≤ 91.
> Proof. Let m ≤ 91. From Theorem 3 in [12] we know that K > 7 · 10^11.
> With X₀ = 695 · 2^60 ≈ 8 · 10^20, as given in Definition 4, we get m₂ ≥ 47. Now, from Theorem 21 we have
> δ < (K+L)/K < δ + 6.9 · 10^−32.
> By using continued fractions as in Lemma 22, we can now get a better lower bound for K with
> K > 5.2 · 10^15. And now we can reiterate this process!
> In the next run, we get m₂ ≥ 67, δ < (K+L)/K < δ + 5.1 · 10^−36 and, therefore, K > 3.97 · 10^17.
> Applying this newer bound on K once more, we get m₂ ≥ 77, δ < (K+L)/K < δ + 4.1 · 10^−38 and, hence, K > 4.64 · 10^18.
> In the forth run we get m₂ ≥ 82, δ < (K+L)/K < δ + 2.3 · 10^−39 and with this K > 2.74 · 10^19.
> From there we get m₂ ≥ 86, δ < (K+L)/K < δ + 2.3 · 10^−40 and K > 7.76 · 10^19. And from this we get m₂ ≥ 88, δ < (K+L)/K < δ + 5.3 · 10^−41 and K > 2.05 · 10^20.
> Applying this lower bounnd a last time we get m₂ ≥ 91, δ < (K+L)/K < δ + 1.11 · 10^−43 and K > 7.94 · 10^21.
> But this last lower bound on K is larger than the upper bound of K < 1.4784mδ^m < 2.2 · 10^20 given by Simons and de Weger [12]. Thus, no such m-cycle can exist.

七步数据（我逐项核对）：`m₂ = 47、67、77、82、86、88、91`；`eps = 6.9 · 10^−32、5.1 · 10^−36、4.1 · 10^−38、2.3 · 10^−39、2.3 · 10^−40、5.3 · 10^−41、1.11 · 10^−43`；`K > 5.2 · 10^15、3.97 · 10^17、4.64 · 10^18、2.74 · 10^19、7.76 · 10^19、2.05 · 10^20、7.94 · 10^21`。

Corollary 24 表前三行（同页）：`98 → 7.76 · 10^19`、`117 → 2.74 · 10^19`、`276 → 4.68 · 10^18`；证明首句逐字：`The first three lines follow from Theorem 21, all others except the last one from Corollary 19, and the last one from the statement independent of m in [4, 9] or [3], using the known value of X₀ as in Definition 4 and given in [2].`

### 参考文献里与 SdW 有关的条目（文章第 21、22 页，`hercher5.txt` 第 1213 至 1225 行）

逐字：

> [11] J. Simons and B. de Weger, Theoretical and computational bounds for m-cycles of the 3n + 1-problem, Acta Arith. 117 (2005), 51–70.
>
> [12] J. Simons and B. de Weger, Theoretical and computational bounds for m-cycles of the 3n + 1 problem, preprint, 2010. Available at https://deweger.net/papers/[35a]SidW-3n+1-v1.44[2010].pdf.

**要点（已逐字核对）**：Hercher 引用的在线版本是 **v1.44**，不是 v1.43。因此「定理 21 的终结构依赖 SdW 的哪些引理」按 v1.44 回答；v1.43 与 v1.44 的差别见材料 4。

### 与项目笔记的关系

1. `rebuttal-2.md` 第 56 行称「重新下载 … HTTP 200，250655 字节」「`hercher.txt` 第 799 至 801 行」——与我的下载字节数和抽取行号**完全一致**（已核验），说明项目当时用的是与本次相同的 PDF 与相同的抽取方式。
2. `attempt.md` 第 30 行称「勘误 … 标题写 2026 年 6 月 14 日」——勘误 PDF 标题里没有日期；该日期的真实出处是摘要页链接标签（见材料 2）。

---

## 二、材料 2：2026 年勘误（Corrigendum to Article 23.3.5）

### 出处与两个日期（两说都查，均已核验）

1. 勘误 PDF：`https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf`
2. 本次下载：HTTP 200，124287 字节，2 页；md5 `f23d5f969116cb1af6e9b981b4b3ba7a`。
3. **日期说一（2026 年 6 月 14 日）**：摘要页 `hercher5.html` 的完整版一行里，勘误链接标签逐字为 `Corrigendum, June 14 2026`（页面原文；HTTP 200）。`vol26.html` 目录页只写 `corrigendum`，无日期。
4. **日期说二（2026 年 7 月 31 日）**：PDF 文件头（内部元数据）逐字节为 `/CreationDate (D:20260731165843-04'00')` 与 `/ModDate (D:20260731165843-04'00')`，即 2026 年 7 月 31 日 16:58:43（UTC−4）。`pdfinfo` 在 JST 时区下显示为 `Sat Aug 1 05:58:43 2026 JST`，即同一时刻的另一种时区写法——`rebuttal-2.md` 第 62 行写的「PDF 元数据创建日 2026 年 8 月 1 日」由此而来（已核验：同一时间戳，不是第二份文件）。
5. 勘误正文里**没有印刷日期**（全文 88 行抽取文本，我通读无日期）。
6. 「同刊勘误页」：JIS 没有独立的勘误汇总页（`errata.html`、`erratum.html`、`corrigenda.html`、`errata/index.html` 四个路径全部 HTTP 404，已核验）；JIS 首页与 vol26 目录页也没有勘误栏。勘误只通过文章摘要页链接与同目录 PDF 存在。

### 我是否亲自打开

是。`pdftotext -layout corrigendum.pdf corrigendum.txt`（88 行），并把两页渲染成图（`corr-1.png`、`corr-2.png`），逐句读了公式的上下标。

### 关于争议步骤它说了什么（关键句逐字，按渲染图核对）

1. 首句（承认错误）：
   > "The derivation of the inequalities `T(n_{m−m₂+1+ℓ}) < 3/(2^v−1)^δ` in the proof of Theorem 21 at the bottom of page 14 **contains an error**."
   （其中 `3/(2^v−1)^δ` 里的 δ 是分母括号整体的上标；「at the bottom of page 14」与我在材料 1 中核对到的位置一致。）
2. 它要重新证明的命题（原证明随后要用的那条）：
   > "To show the statement `T(n_{m−m₂+1}) + Σ_{i=m−m₂+2}^{m} T(n_i) < 3/(2^v − 1) + 3 · (m₂ − 1)/((2^v − 1)^δ)`, which is used later in the proof, we can proceed as follows."
3. 替代论证的骨架（逐字要点）：
   1. 定义 `x_i := log(n_i + 1)/log 2`；
   2. "Then, by Lemma 8, we know that 1 ≤ k_i ≤ x_i, and by Lemma 20 that n_{i+1} < n_i^δ, which implies x_{i+1} < δx_i."
   3. "Without loss of generality, let the cycle be entered in such a way that this sum is maximal. Then x_{m−m₂} ≤ x_m; otherwise, we would have chosen the shifted interval of local minima. Since x_{m−m₂+1} < δx_{m−m₂}, this implies x_{m−m₂+1} < δx_m."
   4. "By Remark 7, we have T(n_i) < 3/n_i. Thus, Σ_{i=m−m₂+1}^{m} T(n_i) < Σ_{i=m−m₂+1}^{m} 3/(2^{x_i} − 1) =: S(x_{m−m₂+1}, …, x_m)."
4. 凸性与顶点（替代论证的核心）：
   > "Since all x_i are positive, the function S is **convex** and attains its maximum value at a **vertex** of the polytope determined by the constraints x_i ≥ 1, x_{i+1} ≤ δx_i, x_{m−m₂+1} < δx_m, and x_{m−m₂+1} + ⋯ + x_m ≥ (m₂/m)·K. Thus, at least m₂ of these constraints must be active, i.e., must hold with equality."
5. 排除 `x_i = 1`、定出活跃约束、得顶点坐标（逐字）：
   1. "Suppose there is a value x_i such that x_i = 1. Then x_{i+1} ≤ δ, …, x_{i−1} ≤ δ^{m₂−1}. Hence, x_{m−m₂+1} + ⋯ + x_m ≤ (δ^{m₂} − 1)/(δ − 1) < (m₂/m)·K, contradicting the sum constraint. The last inequality follows from the definition of m₂ in the statement of Theorem 21."
   2. "Thus, m₂ of the remaining m₂ + 1 constraints must be active. If all constraints x_{i+1} ≤ δx_i, x_{m−m₂+1} < δx_m were active simultaneously, this would lead to the contradiction x_m = δ^{m₂}x_m, and hence δ = 1, contradicting δ = log 3/log 2."
   3. "Consequently, S attains its maximum at a point whose coordinates are a cyclic permutation of x_{m−m₂+1}, δx_{m−m₂+1}, …, δ^{m₂−1}x_{m−m₂+1}"，且 `x_{m−m₂+1} = (m₂/m)·K·(δ−1)/(δ^{m₂}−1) = v`。
6. 收尾不等式（按渲染图核对）：
   `T(n_{m−m₂+1}) + Σ_{i=m−m₂+2}^{m} T(n_i) < S(x_{m−m₂+1}, …, x_m) ≤ S(v, δv, …, δ^{m₂−1}v) ≤ S(v, δv, …, δv) = 3/(2^v − 1) + 3·(m₂ − 1)/(2^{δv} − 1) < 3/(2^v − 1) + 3·(m₂ − 1)/((2^v − 1)^δ)`，末句逐字 "which is exactly what we wanted to prove."
7. 致谢（错误的发现者）：
   > "The author is highly grateful to **Xinjun Wang**, ORCID 0009-0007-5895-5984, for pointing out this mistake and for helpful discussions regarding its correction."

### 与项目笔记的对账（要点）

1. `attempt.md` 第 30 行称「勘误状态：作者自查更正，无第三方复核」——**与原文不符**：勘误明确写错误由 Xinjun Wang 指出（见上第 7 条）。
2. `rebuttal-2.md` 第 64 行转写首句时把右端抄成 `T(n_{m−m2+1+ℓ}) < (2^v−1)^δ`（丢了 `3/`）——原文为 `T(n_{m−m₂+1+ℓ}) < 3/(2^v−1)^δ`。

---

## 三、材料 3：zbMATH 审稿记录（Zbl 1536.11052）

### 出处与版本信息

1. 记录页：`https://zbmath.org/1536.11052`，HTTP 200，79565 字节（本次 `curl -sL` 取得，去标签后逐段读）。
2. 记录头逐字：`Hercher, Christian — There are no Collatz m-cycles with m ≤ 91. (English) — Zbl 1536.11052 — J. Integer Seq. 26, No. 3, Article 23.3.5, 22 p. (2023).`

### 我是否亲自打开

是。下载 HTML 后去标签逐段读过；争议句与审稿人署名均已逐字核对。

### 关于争议步骤它说了什么（审稿意见全文逐字）

照录（原页面中夹在词句间的「Wikipedia／Wolfram MathWorld／Encyclopedia of Mathematics」等外链小工具已注明，不计入正文）：

> "The author considers recursive sequences of positive integers where every odd term n is followed by (3n+1)/2 and every even term n by n/2. The main purpose of the paper is to put constraints on m-cycles, i.e., cycles with exactly m local minima, for large m. The approach strongly relies on previous results related to rational approximations of log 3 / log 2 from **a preprint of Simons and de Weger**, which is an update of [J. Simons and B. de Weger, Acta Arith. 117, No. 1, 51–70 (2005; Zbl 1136.11019)]. To improve those results, upper bounds on partial sums of inverse of consecutive odd terms are given. A similar idea was already present in [S. Eliahou, Discrete Math. 118, No. 1–3, 45–56 (1993; Zbl 0786.11012)]. Thanks to a computer-assisted proof, he obtains a stronger constraint on the value of m (Corollary 19). Repeatedly using continued fraction expansions of log 3 / log 2, it is then inferred that there exists no m-cycle with m ≤ 91, which is the main result. Surprisingly, it does not seem to depend on Corollary 19. **The reviewer wonders whether the proof of the main result could be simplified by using Corollary 17 instead of Theorem 21 whose proof has a potential flaw near the end.** Another interesting result is a stronger constraint on the size of a cycle, regardless of the number of local minima. The method, based on a particular partitioning of consecutive odd terms, appears to be quite original. As a consequence, it becomes easier to improve the currently known lower bound on the size of a non-trivial cycle."

署名行逐字：

> "Reviewer: Olivier Rozier (Paris)"

### 关于争议步骤的要点

1. 「whose proof has a potential flaw **near the end**」是对 Theorem 21 证明的**位置描述**（靠近末尾），与 2026 年勘误所指「at the bottom of page 14」以及我在材料 1 中核对到的争议步位置一致。
2. 审稿人建议的替代路线是**改用 Corollary 17**（而不是 Theorem 21）。Corollary 17 印刷形态逐字（`hercher5.txt` 第 598 至 601 行）：
   `δ < (K+L)/K < δ + 1/(K · 3 log(2)) · (97/54) · m · (1/X₀)`。
3. 该评审记录**早于** 2026 年勘误（勘误致谢的是 Xinjun Wang；记录明显写成于勘误之前——「潜在缺陷」尚被称为 potential）。记录页未给出评审的署名日期（我未找到，列于第七节）。

---

## 四、材料 4：Simons 与 de Weger（v1.43 与 v1.44）

### 两个版本都在网上（均已核验）

| 版本 | URL | HTTP | 字节 | 页 | md5 | 文件头（首页逐字） |
|---|---|---|---|---|---|---|
| v1.43 | `https://www.deweger.net/papers/%5B35a%5DSidW-3n+1-v1.43%5B2007%5D.pdf` | 200 | 275795 | 17 | `2e5e5c4f36deb283c0925229573b7648` | `version 1.43, July 31, 2007` |
| v1.44 | `https://www.deweger.net/papers/%5B35a%5DSidW-3n+1-v1.44%5B2010%5D.pdf` | 200 | 266827 | 17 | `696d4ff4b6f3f4036bac3892aa9cd968` | `version 1.44, August 31, 2010` |

补充核验（三件事）：

1. v1.43 的**现站副本**与 Wayback Machine 归档副本（`https://web.archive.org/web/20220429130552id_/https://deweger.net/papers/%5B35a%5DSidW-3n+1-v1.43%5B2007%5D.pdf`）**逐字节相同**（`cmp` 通过，md5 同为 `2e5e5c4f36deb283c0925229573b7648`）。Wayback CDX 索引显示该文件有 2022 年 4 月 29 日与 2023 年 4 月 4 日两个归档点，均为 HTTP 200 的 PDF。
2. v1.43 的 `pdftotext -layout` 抽取恰为 **1056 行**，与项目笔记 `attempt.md` 第 29 行所记「提取 1056 行」一致。
3. **Hercher 论文引用的在线版本是 v1.44**（其参考文献 [12] 的 URL，见材料 1 第一节末尾）。所以回答「定理 21 的终结构依赖 SdW 的哪些引理」应以 v1.44 为准；v1.43 只在项目笔记里被点名。

### 我是否亲自打开

是。v1.43（现站下载）与 v1.44 都已下载并 `pdftotext -layout` 抽取（`sidw143.txt` 1056 行、`sidw144.txt` 1067 行），关键条目逐字读过。

### 两版关键条目对照（逐字，均已按抽取文本核对）

1. **Theorem 3 (d)**，`91 ≤ m ≤ 515 619` 段的下界：
   1. v1.43（第 268 至 269 行）：`1.3752 · 10^11 < K < 1.4784 mδ^m < e^{0.46057m+log m+0.39095}`
   2. v1.44（第 270 至 271 行）：`7.5311 · 10^11 < K < 1.4784 mδ^m < e^{0.46057m+log m+0.39095}`
   3. Hercher 的 Theorem 23 开头写 `K > 7 · 10^11`——与 **v1.44** 的 `7.5311 · 10^11` 一致（取整），与 v1.43 的 `1.3752 · 10^11` 不一致。
   4. 差异来源（我的核对）：两版 Corollary 11 分段不同。v1.43（第 616 至 617 行）：`If 224 446 ≤ m ≤ 421 461 then K > q24 > 7.5311 × 10^11.` 与 `If 421 462 ≤ m ≤ 2 916 130 then K > q23 > 1.3752 × 10^11.`；v1.44（第 622 至 623 行）：`If 345 301 ≤ m ≤ 648 401 then K > q24 > 7.5311 × 10^11.` 与 `If 648 402 ≤ m ≤ 4 486 354 then K > q23 > 1.3752 × 10^11.`。在 `91 ≤ m ≤ 515 619` 上取一致（最弱）下界：v1.43 得 `1.3752 · 10^11`，v1.44 得 `7.5311 · 10^11`。
2. **k₂ 表 m = 91 行**（两版同值）：v1.43 第 779 行与 v1.44 第 786 行均作 `91  1.3859  2.0068 · 10^20  1.4784  2.1408 · 10^20`（即 `j₂(91) < 1.3859`、`J₂(91) < 2.0068 · 10^20`、`k₂(91) < 1.4784`、`K₂(91) < 2.1408 · 10^20`）。
3. **Theorem 3(d) 在 `91 ≤ m ≤ 515 619` 处的证明句**（两版同文；v1.43 第 822 至 825 行，v1.44 第 829 至 832 行）：`The upper bound for K follows from Lemma 16, and the observation that k₂(m) < 1.4784 (note that k₂(m) is a decreasing function, except when A(m) jumps to the next champion). The lower bound for K follows by Corollary 11.`
4. Hercher 摘要里的「next bound」`K ≥ 1.375 · 10^11`（材料 1）：在 v1.43 与 v1.44 里都对应 Corollary 11 的 `q23 > 1.3752 × 10^11` 行；Hercher 自己的 Corollary 29 目标是把这条**对所有 m** 无条件化（`X₀ ≥ 1536 · 2^60 = 3 · 2^69` 时每圈 `K > 1.375 · 10^11`）。

### 「定理 21 的终结构依赖它的哪些引理」——按 v1.44 逐条列出（每条带行号与逐字）

先给结论（我的整理）：

1. **争议步本身**（第 14 页的 T 求和上界）在印刷版里只用到 Hercher 自己的 Lemma 8、Lemma 20、Remark 7、Theorem 14；其中 **Lemma 20 被 Hercher 归功于 [12]**（论文第 12 页第 673 行：`The following lemma also can be found in [12].`）。
2. **整条链的终点矛盾**（Theorem 23，唯有它把 `m ≤ 91` 终结）依赖 SdW [12] 的两块：
   1. **起点下界** `K > 7 · 10^11`（论文原文：`From Theorem 3 in [12] we know that K > 7 · 10^11.`）⇒ v1.44 的 **Theorem 3(d)**（`91 ≤ m ≤ 515 619` 行，第 270 至 271 行）。其证明引 **Corollary 11** 与 **Lemma 10**（广义 Crandall）；Corollary 11 的绝大多数行由 Lemma 10 直接给出，倒数第二行是 Crandall 原文 Lemma 1 的 Corollary 2，末行由 Lemma 8 给出。
   2. **终点上界** `K < 1.4784mδ^m < 2.2 · 10^20`（论文原文：`given by Simons and de Weger [12]`）⇒ v1.44 的 **k₂ 表 + Lemma 16 + Lemma 14 + Lemma 12 + Lemma 7 + Lemma 9**。链条逐字如下：
      1. `Lemma 16`（第 812 行）：`For 64 ≤ m ≤ 515 619 a possible m-cycle satisfies K < K₂(m).` 其证明首句（第 819 行）逐字：`From Lemma 14 we have K < K₁(m) < q_{n(m)−1}, implying n ≤ n(m) − 2. Hence a_{n+1} ≤ A(m).`（即：**先用 Rhin 界把收敛项指标封在 n(m) 内**，再用已算到 `a₂₀₀₀₀₁` 的有限部分商检查完成——这一步是「无穷合取变有限合取」的关键）；
      2. `Lemma 14`（第 677 行）：`Let x = K₁(m) be the largest solution of e^{−13.3(0.46057+log x)} = m c_m 2^{−(δ−1)x/(δ^m −1)}. Then K < K₁(m).`，由 Lemma 7 与 Lemma 12 直接得出；
      3. `Lemma 12`（第 649 行，Rhin 的界）：`Λ > e^{−13.3(0.46057+log K)}`。其证明逐字：`We apply the Proposition on p. 160 of [Rh] with u₀ = 0, H = u₁ = K + L, and u₂ = −K. Together with Lemma 8 the result follows.`；
      4. `Lemma 7`（第 486 行）：`0 < Λ < m c_m 2^{−(δ−1)K/(δ^m −1)}`；
      5. `Lemma 9`（第 573 行）：(a) 收敛项判据、(b) `|p_n − q_n δ| > 1/(q_n + q_{n+1}) > 1/((a_{n+1} + 2)q_n)`、(c) `q ≤ q_n` 时 `|p − qδ| ≥ |p_n − q_n δ|`、(d) `p_n − q_n δ` 的符号按 n 交替；
      6. `Lemma 6`（第 454 行，链式增长）：`For all i = 0, 1, …, m − 1 we have x_{i+1} < b^δ x_i^δ.`，并注记 `Note that the inequality of Lemma 6 holds cyclically.`
3. **Lemma 20 的归属核对**：Hercher 写 `The following lemma also can be found in [12].` 我在 v1.43 与 v1.44 中检索到的最接近形态是 **Lemma 6**（`x_{i+1} < b^δ x_i^δ`）；**我没有在 SdW 两版中检索到与 Hercher Lemma 20 完全逐字相同的 `n_{i+1} < n_i^δ` 形态**（标为「未检索到」，不等于「不存在」；Hercher 的 Lemma 20 附带自足证明）。

### 与项目笔记的关系

1. `attempt.md` 第 11、29 行点名的是 v1.43；Hercher 引用的却是 v1.44（本文件材料 1 已逐字给出）。用 1.4784 与 k₂(91) 的结论两版一致，但「起点 `K > 7 · 10^11` 出自哪一行」只有 v1.44 对得上。
2. `rebuttal-round1.md` 第 98 行称 v1.43 第 269 行写 `1.3752×10^11 < K < 1.4784 m δ^m`——我核对 v1.43 第 269 行**逐字相符**（行号也一致）。

---

## 五、材料 5：项目自己的材料

### 5.1 `30-proof-attempts/diophantine-transcendence/attempt.md`

我是否亲自打开：是（全文读过；50381 字节，292 行）。

关于争议步骤它说了什么（带行号的关键断言）：

1. 第 3 行（开篇口径声明）：主结论已改口径——`m ≤ 91` 现在是**条件结论**，并列的对照口径是 `m ≤ 82`。
2. 第 9 至 12 行：主目标 (T1) 与其允许的工具清单（点名 SdW v1.43 的 Lemma 7、Corollary 5、Lemma 9、Lemma 10；Hercher 的 Theorem 14、16、21、Lemma 22 与勘误）。
3. 第 29 行：SdW 条目——「作者维护版 v1.43（2007 年 7 月 31 日）」，下载 URL 与「1056 行」记录；「版本状态：v1.43 是作者维护的更新版，未经本次同行复核」。
4. 第 30 行：Hercher 条目——「勘误状态：作者自查更正，无第三方复核」；「我读了全文（它重推的正是 Theorem 21 里 T 求和那一段）」。
5. 第 31 至 35 行：三层证据（zbMATH 原句；两个第三方 Lean 仓库；项目自己的文献笔记 `frontier.md` 第 21 行、`claims-2024-2026.md` 第 37 至 39 条）。
6. 第 58 至 74 行：步骤 4——自举链实现与七步表（`m₂ = 47/67/77/82/86/88/91`；eps；新 K）；第 74 行称「七步的 `m2` 全中、`eps` 前六步与论文相差不超过 3%、第七步差 11%（同一个 Lemma 22 分母，故不影响结论）」。
7. 第 76 至 93 行：步骤 4b——尾部条款与四种口径的前沿表（几何尾部加特例式 → 91；几何尾部加一般式 → 90；「健全」尾部加特例式 → 82；「健全」尾部加一般式 → 82；停滞点 `K = 4.64028×10^18`）。
8. 第 101 至 103 行：步骤 6——终点上界用 SdW Theorem 3(d) `K < 1.4784 m δ^m`，并注明「该常数来自 Lemma 16 的 `k_2(m)`，其证明第一步『From Lemma 14 we have `K < K_1(m) < q_{n(m)−1}`』用的正是 Rhin 的界，故**这不是初等结论**」。
9. 第 180 行：失败点 5——争议是本项目的直接依赖，「在此之前，本文一切『`m ≤ 91`』字样都应读作『在几何尾部口径下』」。
10. 第 200 行 L4、第 220 行「否决或限制本路线」第 1 条（SdW Lemma 16 的证明结构是本路线最强的一条否决）、第 224 行（`m ≤ 91` 这一档同时用到超越论与 Hercher 的初等改进，不能单侧归功）。
11. 第 248 至 263 行：对第二轮反驳的回应——「反驳的核心指控成立，已修补」；第 252 至 255 行照录了三条来源的 curl 命令与逐字引文。

### 5.2 同目录 `rebuttal-2.md`（首席反驳者备忘录第三轮）

我是否亲自打开：是（全文读过；18630 字节，120 行）。

关于争议步骤它说了什么（带行号的关键断言）：

1. 第 16 行（核心一击）：第三方「最坏情形（一个晚窗口极小值吸收几乎全部 o-step，其余贴近 `X0`）」在 Hercher 自己的 Lemma 20 下不可行——尖峰若承载窗口和 `W`，增长约束把其余窗口元素统统逼到 `≥ W/δ^{m2−1}`（`m2 = 91`、`W = 2.0×10^20` 时为 `199.2`，远高于 `log2(X0+1) = 69.44`）。
2. 第 54 至 81 行：勘误的替代推导「**有效**」：
   1. 第 56 至 60 行给出「论文原步」（下载 HTTP 200、250655 字节；`hercher.txt` 第 799 至 801 行，与我核对一致），并指出原步两处问题（`δ^ℓ ≤ δ` 对 ℓ ≥ 2 为假；`T` 递减使「上界」方向反）；
   2. 第 62 至 66 行逐字引勘误的「contains an error」、凸性句与致谢句；
   3. 第 68 至 81 行给出两处可补的表述缺口（按 `Σk` 读的 WLOG 窗口选择要改成 `Σx` 最大窗；无界多面体上的「最大值在顶点」需要回收锥一步），并称 `m2 ≤ 8` 穷举全部活跃约束子集后每个 `m2` 只有一个可行顶点等价类（几何点），结论「勘误的替换推导是健全的」（按它的重构与核验）。
3. 第 116 至 119 行（「我未做到与未能核实」）：未编译两个 Lean 仓库（只做文本核查）；勘误凸性论证是手写重构加数值核验、未形式化；`Thm21Pigeonhole.lean` 与 `CFDepth36.lean` 承载的有限部分未重推。

---

## 六、回原文核对：项目笔记数字对账表

对照原则：凡项目笔记写的数字，都以我在第一至五节实际打开的原件为准。

| # | 项目笔记的说法（出处） | 原文核对结果 | 判定 |
|---|---|---|---|
| 1 | 论文题名与出处《There are no Collatz m-Cycles with m ≤ 91》，JIS 26（2023）文章 23.3.5 | 摘要页与 PDF 首页均确认 | 符合 |
| 2 | 七步自举 `m₂ = 47、67、77、82、86、88、91` 与 `K > 5.2e15、3.97e17、4.64e18、2.74e19、7.76e19、2.05e20、7.94e21`（attempt.md 第 64 至 72 行表） | `hercher5.txt` 第 850 至 878 行逐项相符 | 符合 |
| 3 | 七步 `eps = 6.9e-32、5.1e-36、4.1e-38、2.3e-39、2.3e-40、5.3e-41、1.11e-43`（同上） | 同段逐项相符 | 符合 |
| 4 | 末步更精细值 `7941964418702608664581`（rebuttal-round1 第 43 行） | 论文只印 `7.94 · 10^21`（3 位有效数字）；更精细值是项目自算，非论文原文 | 符合（须注明精度来源） |
| 5 | Theorem 23 起点 `K > 7·10^11`、终点 `K < 1.4784mδ^m < 2.2·10^20`（attempt.md 第 224 行） | `hercher5.txt` 第 851、879 至 880 行逐字相符 | 符合 |
| 6 | SdW v1.43 Theorem 3(d) `91 ≤ m ≤ 515619` 段为 `1.3752×10^11 < K`（rebuttal-round1 第 98 行；attempt.md 第 29 行称 v1.43） | **v1.43 第 269 行确为 `1.3752 · 10^11`（逐字相符）**；但 Hercher 引用的 v1.44 该处为 `7.5311 · 10^11` | 符合（对 v1.43 成立）；任何引用须注明版本 |
| 7 | SdW k₂ 表 m = 91 行 `k₂ = 1.4784`、`K₂ = 2.1408×10^20`（rebuttal-round1 第 98 行） | v1.43 第 779 行与 v1.44 第 786 行同值 | 符合 |
| 8 | 「Lemma 16 的证明以 From Lemma 14 we have `K < K_1(m)` 开头」（同上） | v1.43 第 812 行、v1.44 第 819 行均如此 | 符合 |
| 9 | zbMATH 原句（attempt.md 第 32 行；rebuttal-2 第 253 行重 curl） | 与记录页逐字一致（第三节） | 符合 |
| 10 | 勘误首句、凸性句、致谢句（rebuttal-2 第 62 至 66 行） | 三句逐字相符；但首句右端转写丢了 `3/`（见第二节对账） | 基本符合，有一处转写缺损 |
| 11 | 「勘误 … 标题写 2026 年 6 月 14 日」（attempt.md 第 30 行） | 勘误 PDF 标题与正文**没有**日期；该日期是 JIS 摘要页链接标签 `Corrigendum, June 14 2026` | 需订正：日期出处是摘要页，不是 PDF 标题 |
| 12 | 「勘误状态：作者自查更正，无第三方复核」（attempt.md 第 30 行） | 勘误致谢 Xinjun Wang「for pointing out this mistake」——非自查 | 与原文不符 |
| 13 | 「PDF 元数据创建日 2026 年 8 月 1 日」（rebuttal-2 第 62 行）与项目笔记另一处「文件头日期 2026 年 7 月 31 日」 | 同一时间戳的两种时区写法：`/CreationDate (D:20260731165843-04'00')`；−04:00 本地时间 7 月 31 日 16:58:43，JST 下显示 8 月 1 日 05:58:43 | 两说均已解释，不是两个日期 |
| 14 | 论文 PDF 250655 字节、争议行在抽取文本第 799 至 801 行（rebuttal-2 第 56 行） | 我独立下载同为 250655 字节；我的抽取（`pdftotext -layout`）争议行恰在第 799 至 801 行 | 符合 |
| 15 | 「m ≤ 91 全部压在 Hercher 定理 21 的『几何尾部』一步上」并引 SdW 与 zbMATH 佐证（README.md 第 34、89 行） | 与原文一致：争议步在 Theorem 21 证明第 14 页；zbMATH 原句确认「potential flaw near the end」 | 符合 |

---

## 七、missing（打不开、找不到或无法核实的）

1. **JIS 独立勘误汇总页：不存在（已核验 404）**。试过 `https://cs.uwaterloo.ca/journals/JIS/errata.html`、`erratum.html`、`corrigenda.html`、`errata/index.html`，全部 HTTP 404；JIS 首页与 vol26 目录页也没有勘误栏。勘误只能从文章摘要页链接与同目录 `corrigendum.pdf` 取得。因此勘误的「正式日期」只能取到两个来源：页面标签 2026 年 6 月 14 日；PDF 内部时间戳 2026 年 7 月 31 日（UTC−4）。
2. **勘误正文内无印刷日期**：通读 88 行抽取文本，未出现任何日期（属「找不到」，不是打不开）。
3. **zbMATH 评审的署名日期**：记录页未给出（未找到）。
4. **Hercher 论文附带的计算附件未打开**：`collatz_cycle.cpp`、`collatz_m-cycle.cpp`、`Collatz-m-Cycle-Paper.ipynb`（摘要页有链接；本次未下载；属计算物证，不在本清单要求内）。
5. **Hercher 的 arXiv 版本未打开**：`https://arxiv.org/abs/2201.00406` 我只读了摘要页（确认它即本文的 arXiv 版；最新为 v3，2023 年 4 月 4 日；v1 为 2022 年 1 月 2 日），未下载 PDF 逐页核对。
6. **SdW 期刊版（Acta Arith. 117 (2005), 51 至 70）未打开**；Rhin 1987 原文未打开（只在 SdW 的 Lemma 12 处转引到）。
7. **未能核实的**：v1.43 与 v1.44 在 `78 ≤ m ≤ 90` 段的常数差异（v1.43：`1.0550 · 10^17 < K`；v1.44：`1.1173 · 10^17 < K`）是否以任何方式影响 Hercher 的链。Hercher 的链不经过该段（起点用 91 段与 Corollary 24 的前三行），故**我的判定是无影响**——但这是判定，不是原文陈述，供下游复核。

---

## 八、本次会话执行的命令与产物（复现用）

工作目录 `/tmp/hercher-audit/`：

1. `curl -sL -o hercher5.pdf -w "HTTP %{http_code} %{size_download}" https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf` → 200，250655 字节
2. `curl -sL -o corrigendum.pdf ... https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf` → 200，124287 字节
3. `curl -sL https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.html`（摘要页，3066 字节）与 `https://cs.uwaterloo.ca/journals/JIS/vol26.html`（46868 字节）
4. `curl -sL https://zbmath.org/1536.11052 -o zbmath.html` → 200，79565 字节
5. `curl -sL -o sidw143.pdf "https://www.deweger.net/papers/%5B35a%5DSidW-3n+1-v1.43%5B2007%5D.pdf"` → 200，275795 字节；同文件从 Wayback `.../20220429130552id_/...` 下载后 `cmp` 与 `md5` 均相同
6. `curl -sL -o sidw144.pdf "https://www.deweger.net/papers/%5B35a%5DSidW-3n+1-v1.44%5B2010%5D.pdf"` → 200，266827 字节
7. `pdftotext -layout` 四份 PDF，得 `hercher5.txt`（1256 行）、`corrigendum.txt`（88 行）、`sidw143.txt`（1056 行）、`sidw144.txt`（1067 行）
8. `pdftoppm -png -r 150 -f 13 -l 14 hercher5.pdf p` 与 `pdftoppm -png -r 150 corrigendum.pdf corr`，得 `p13-13.png`、`p14-14.png`、`corr-1.png`、`corr-2.png`；四张图均用 Read 工具逐页读过
9. `pdfinfo` 与 `grep -a -o "/CreationDate ([^)]*)"` 取四份 PDF 的内部时间戳；`md5 -q` 取校验和
10. `curl -sL "http://archive.org/wayback/available?..."` 与 `https://web.archive.org/cdx/search/cdx?url=deweger.net/papers*&output=text&limit=200&filter=urlkey:.*sidw.*`（CDX 索引；第一次 429，稍后重试成功）
11. `curl -sL -o /dev/null -w "HTTP %{http_code}"` 探测 `errata.html`、`erratum.html`、`corrigenda.html`、`errata/index.html` → 全 404
12. `curl -sL https://arxiv.org/abs/2201.00406`（只读摘要页）

本文件之外，项目侧只读材料：`attempt.md`（292 行全文）、`rebuttal-2.md`（120 行全文）；两者均未被我修改。

---

*本文件只做材料收集与回原文核对，不裁决争议。所有逐字引文以本次打开的原文为准；凡我自己的推断或判定均已就地标明。*
