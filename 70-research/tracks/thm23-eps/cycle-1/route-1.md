# 路线 1：原件逐字与版本对照（thm23-eps / cycle-1）

## 0 一句话结论

印出版与 arXiv v3 的定理 23 第七步印数，两版逐字相同，都是 `δ + 1.11 · 10⁻⁴³`（指数 `−43` 处于上标位，按 150 dpi 渲染图亲读核对）；两版的可见差异不落在第七步句本身，而落在 X₀（印出版 `695 · 2⁶⁰`、v3 `704 · 2⁶⁰`）与第 16 页 Corollary 24 的表。本路线只做文献复算，不做取整、笔误或我方有偏的判定。

本报告的一次自我更正须先说清：本文件在写作过程中曾出现三条与本轮实测相矛盾的草稿断言（页脚偏移、「we obtain ε」式引文、X₀ 在文本层取不到），三条都已被本轮亲跑推翻并改写；下面第 3、4.1、5.2 节给的是修正后的版本。

---

## 1 口径与标注

证据等级只用三种：

1. **本次亲跑**：我在本轮执行的命令及其输出；
2. **本次亲读（渲染图）**：我在本轮渲染、并用 Read 打开看过的图像；
3. **材料记录**：他人已落盘的文件内容（本会话用 grep 或 sed 读出），其内部数字是更早会话的产物，不是我本轮的测量。

关于图像的通道问题（本次亲跑实测）：把渲染图放在 `/tmp` 下时，Read 返回「File does not exist」（同一路径用 Bash 可以列出文件）；改放到轨道目录 `materials/route1/render/` 后，Read 正常返回图像并显示内容。因此本轮所有亲读都用轨道目录内的 PNG，渲染图同时留在该目录备查。

---

## 2 原件重下载与哈希（本次亲跑）

脚本：本轨道 `scripts/reproduce_hash.sh`（本回合用 Write 写盘并已执行；脚本对三个 URL 执行 `curl`，打印 HTTP 状态与 SIZE，随后计算 md5、字节数，并渲染第 13 至 16 页）。同一条命令内既下载到 `/tmp/route1_redownload`，又对轨道归档件复算：

| 文件 | 本轮字节 | 本轮 md5 | 与材料记录 |
|---|---|---|---|
| hercher5.pdf | 250655 | 3e2377bef0b1c0435dc455c9bbee43a1 | 逐位一致（`materials.md:31`、`:271`） |
| corrigendum.pdf | 124287 | f23d5f969116cb1af6e9b981b4b3ba7a | 逐位一致（`materials.md:51`、`:273`） |
| arxiv-2201.00406v3.pdf | 236361 | 92a5047052911ac7a45d59cc32efbe65 | 逐位一致（`materials.md:67`、`:275`） |

三次请求都返回 HTTP 200，SIZE 与落盘字节数一致。脚本输出全文在 `materials/route1/hash_run_log.txt`，其中「本次下载」与「轨道归档件」两组各三行，六行逐位相同。

版本真伪的一处旁证（本次亲读（本次抽取））：v3 抽取文本首行为 `arXiv:2201.00406v3 [math.NT] 4 Apr 2023`，可确认抓到的是 v3 而非其它版次。

---

## 3 页位与页脚（本次亲跑）

用 `pdftotext -bbox` 取每页底部区域的词，得到印出版物理第 11 至 20 页的页脚数字分别就是 11 至 20（输出在 `materials/route1/pdf_page_footers.txt`）。因此：

1. 印出版的**印刷页码等于物理页码**，偏移为零；
2. 定理 23 第七步所在的物理第 15 页，就是印刷第 15 页；页脚 `15` 也出现在该页渲染图底部。

（本报告早期草稿曾写「印刷页码等于物理页码减 2」，与本轮页脚实测相反，已作废。）

---

## 4 逐字事实卡

以下引文凡涉及**上标与分式**，均按 150 dpi 渲染图核对；纯文字部分另有抽取文本交叉核对。

### 4.1 Definition 4（印出版第 2 页；本次亲读）

> `We define X0 as the largest number for which it is known that for all positive integers n ≤ X0 their Collatz sequences reach the trivial cycle. As of the date of writing this paper, we have`
>
> `X0 = 695 · 2⁶⁰ .`

按渲染图核对：`2` 的指数 `60` 在上标位。同页另有 `K > 7 · 10⁷` 与 `K > 7.2 · 10¹⁰` 两处上标，形态一致。

arXiv v3 同页同段逐字相同，仅数值改为 `X0 = 704 · 2⁶⁰ .`（本次亲读，v3 第 2 页）。

### 4.2 Definition 15（印出版第 10 页；本次亲读）

> `From now on, let δ := log(3)/log(2) > 1.`

按渲染图核对：分子是 `log(3)`、分母是 `log(2)`，是一个上下分式。抽取文本层把该分式压平成 `let δ := log(2) > 1`（丢掉分子），本条以渲染图为准。

同页紧随其后的是 Theorem 16 的陈述与证明开头（`δ < (K+L)/K < δ + 1/(K·3·log(2)) · Σ_{i=1}^{m} T(nᵢ)` 等）。

### 4.3 Theorem 21 三式（印出版第 13 页；本次亲读）

> `Theorem 21. Let K be the number of odd numbers in a given m-cycle, and let L be the number of even numbers in it. Further, assume there exists a positive integer m₂ with`
>
> `m₂ ≤ m and (δ^{m₂} − 1)/(δ − 1) · log((162/97) · X₀)/log(2) ≤ (m₂/m) · K.`
>
> `Let v = (m₂/m) · K · (δ − 1)/(δ^{m₂} − 1). Then we get`
>
> `δ < (K+L)/K < δ + 1/(K · 3 log(2)) · ( (97(m − m₂) + 73)/(54 · X₀) + 3/(2^v − 1) + 3 · (m₂ − 1)/((2^v − 1)^δ) ).`
>
> `If m₂ = m − 1 we get the better estimate`
>
> `δ < (K+L)/K < δ + 1/(K · 3 log(2)) · ( 3/X₀ + 3/(2^v − 1) + 3 · (m − 2)/((2^v − 1)^δ) )`
>
> `and for m₂ = m`
>
> `δ < (K+L)/K < δ + 1/(K · 3 log(2)) · ( 3/(2^v − 1) + 3 · (m − 1)/((2^v − 1)^δ) ).`

按渲染图核对的三处：第一式的分母 `δ − 1` 与 `δ^{m₂} − 1` 都是上下分式，`m₂` 是 `δ` 的指数；三式末尾的 `(2^v − 1)^δ` 中 `v` 与 `δ` 都在上标位；`log((162/97) · X₀)` 中的 `162/97` 是上下分式。

两点须登记为「对渲染图文本的直接读出」（本路线只报事实，不裁）：

1. 陈述页该项的常数印作 `+ 73`；
2. `m₂ = m` 这一特例式里**没有含 X₀ 的项**。

### 4.4 Theorem 21 证明末的两个特例说明（印出版第 14 页；本次亲读）

> `which proves the general statement for 1 ≤ m₂ ≤ m. For m₂ = m − 1, the first sum Σ_{i=1}^{m−m₂} T(nᵢ) = T(n₁) can be better bounded above by 3/X₀, as seen in Remark 7. For m₂ = m, this first sum is empty and therefore zero.`

这是原文对「`m₂ = m` 时该和为零」的明确表述，逐字如此。同页证明中该项印作 `(97(m − m₂) + 1)/(54 · X₀)`，与第 13 页陈述的 `+ 73` 不同（两处均为本次亲读渲染图所见；此出入早在 `materials.md:162` 与下游材料中登记过，本报告只作事实转录，不改动、不作解释）。

### 4.5 Lemma 22（印出版第 15 页；本次亲读）

> `We now give a well known lemma for diophantine approximation:`
>
> `Lemma 22. Let 0 < α < β be two real numbers with continued fraction expansions α = [a₀; a₁, . . . , a_{k−1}, a_k, . . .] and β = [a₀; a₁, . . . , a_{k−1}, b_k, . . .]. Then every fraction in the open interval (α, β) has a denominator which is not smaller than the one of γ = [a₀; a₁, . . . , a_{k−1}, c_k] with c_k = min(a_k, b_k) + 1.`

按渲染图核对：`a_{k−1}` 等形式的下标位、以及证明中若干 `1/(β − a₀)` 的上下分式。

### 4.6 Theorem 23 全段七步（印出版第 15 页；本次亲读）

> `Theorem 23 (Main Theorem). There is no m-cycle with m ≤ 91.`
>
> `Proof. Let m ≤ 91. From Theorem 3 in [12] we know that K > 7 · 10¹¹.`
> `With X₀ = 695 · 2⁶⁰ ≈ 8 · 10²⁰, as given in Definition 4, we get m₂ ≥ 47. Now, from Theorem 21 we have`
> `δ < (K+L)/K < δ + 6.9 · 10⁻³².`
> `By using continued fractions as in Lemma 22, we can now get a better lower bound for K with`
> `K > 5.2 · 10¹⁵.`
> `And now we can reiterate this process!`
> `In the next run, we get m₂ ≥ 67, δ < (K+L)/K < δ + 5.1 · 10⁻³⁶ and, therefore, K > 3.97 · 10¹⁷.`
> `Applying this newer bound on K once more, we get m₂ ≥ 77, δ < (K+L)/K < δ + 4.1 · 10⁻³⁸ and, hence, K > 4.64 · 10¹⁸.`
> `In the forth run we get m₂ ≥ 82, δ < (K+L)/K < δ + 2.3 · 10⁻³⁹ and with this K > 2.74 · 10¹⁹.`
> `From there we get m₂ ≥ 86, δ < (K+L)/K < δ + 2.3 · 10⁻⁴⁰ and K > 7.76 · 10¹⁹. And from this we get m₂ ≥ 88, δ < (K+L)/K < δ + 5.3 · 10⁻⁴¹ and K > 2.05 · 10²⁰.`
> `Applying this lower bounnd a last time we get m₂ ≥ 91, δ < (K+L)/K < δ + 1.11 · 10⁻⁴³ and K > 7.94 · 10²¹.`

按渲染图核对：七处 `(K+L)/K` 都是上下分式；七处指数 `6.9 · 10⁻³²`、`5.1 · 10⁻³⁶`、`4.1 · 10⁻³⁸`、`2.3 · 10⁻³⁹`、`2.3 · 10⁻⁴⁰`、`5.3 · 10⁻⁴¹`、`1.11 · 10⁻⁴³`，以及 `10¹¹`、`2⁶⁰`、`10²⁰`、`10¹⁵`、`10¹⁷`、`10¹⁸`、`10¹⁹`、`10²¹`，全部处于上标位。

须逐字登记的两点：`bounnd` 为三个 n（原文拼写，非转录错误）；`In the forth run` 的 `forth` 亦为原文拼写。

「第七步」的界定（本报告采用、并在下游引用时应保持同一约定）：证明中共出现七个形如 `δ + …` 的增量，上表第七个即 `δ + 1.11 · 10⁻⁴³`，其引导句为 `Applying this lower bounnd a last time`，输入指向前一步刚给出的 `K > 2.05 · 10²⁰`。

**请看**：原文该处并未出现符号 `ε`；`ε` 是我方记号。原文的写法是把 `1.11 · 10⁻⁴³` 印成 `(K+L)/K` 的上界增量。凡下游报告引用「论文的 ε」，都应标明这是我方对「`(K+L)/K` 上界超出 `δ` 的那一项」的命名。

### 4.7 Theorem 23 收尾句（印出版第 16 页首段；本次亲读）

> `But this last lower bound on K is larger than the upper bound of K < 1.4784mδ^m < 2.2 · 10²⁰ given by Simons and de Weger [12]. Thus, no such m-cycle can exist.`

按渲染图核对：`δ^m` 的 `m` 在上标位；`2.2 · 10²⁰` 的 `20` 在上标位；句末有证明结束符。该段是定理 23 证明的收尾（跨页承接第 15 页末的 `K > 7.94 · 10²¹`）。

### 4.8 勘误两页（本次亲读）

标题为 `Corrigendum to Article 23.3.5 / There are no Collatz-m-Cycles with m ≤ 91`，作者 Christian Hercher。正文开头逐字为：

> `The derivation of the inequalities T(n_{m−m₂+1+ℓ}) < 3/((2^v−1)^δ) in the proof of Theorem 21 at the bottom of page 14 contains an error. To show the statement`
>
> `T(n_{m−m₂+1}) + Σ_{i=m−m₂+2}^{m} T(nᵢ) < 3/(2^v − 1) + 3 · (m₂ − 1)/((2^v − 1)^δ),`
>
> `which is used later in the proof, we can proceed as follows.`

第 2 页末尾的结论链逐字为：

> `= 3/(2^v − 1) + 3 · (m₂ − 1)/(2^{δv} − 1) < 3/(2^v − 1) + 3 · (m₂ − 1)/((2^v − 1)^δ),`
>
> `which is exactly what we wanted to prove.`

末尾致谢点出指正者：`The author is highly grateful to Xinjun Wang, ORCID 0009-0007-5895-5984, for pointing out this mistake and for helpful discussions regarding its correction.`

对本轮目标的意义（事实层，非判决）：勘误只补上**证明中一处推导**，涉及的是 `3/(2^v − 1)` 与 `3 · (m₂ − 1)/((2^v − 1)^δ)` 这两项的来历；它**没有**改动 Theorem 21 陈述式的任何印刷常数，也**没有**改动 Theorem 23 七步中的任何数字（`1.11 · 10⁻⁴³` 在勘误中未出现）。

---

## 5 版本对照（印出版 与 arXiv v3）

### 5.1 第 13 至 16 页逐行差分（本次亲跑）

把两版同页的 `-bbox` 转录按行聚类后做统一差分（`difflib`，上下文 0 行），结果：

| 页 | 结论 |
|---|---|
| 第 13 页 | 逐行相同（差异块 0） |
| 第 14 页 | 逐行相同（差异块 0） |
| 第 15 页 | 差异 1 处，即证明首段的 X₀ 行 |
| 第 16 页 | 差异若干处，全部落在 Corollary 24 的表与其证明首句 |

第 15 页那处逐字为：

```
印出版： With X0 = 695 · 260 ≈ 8 · 1020 , as given in Definition 4, we get m2 ≥ 47. Now, from
v3    ： With X0 = 704 · 260 ≈ 8.1 · 1020 , as given in Definition 4, we get m2 ≥ 47. Now, from
```

（转录用 ASCII 记法；渲染图上 `2` 与 `10` 的指数都在上标位。差分全文在 `materials/route1/version_diff_13_16.txt`。）

**这条事实的边界**：它证明的是「两版第 13 至 16 页的抽取转录在行层面一致或仅差上述处」，不能推广为「两版全文一致」。第 16 页的差异已在本轮捕获，说明该口径确实能显形；而若某处差异只存在于图形（非文字）层，本口径看不见，需以渲染图补。

### 5.2 两版 X₀ 的出现位置（本次亲跑）

对全文抽取做检索：印出版命中 `695` 共 7 处、`704` 共 0 处；v3 命中 `704` 共 7 处、`695` 共 0 处。逐处位置（页号按物理页等于印刷页；行号为该页内抽取文本的 0 基行号）：

| 出现处 | 印出版 | arXiv v3 |
|---|---|---|
| Definition 4 的赋值行 | 第 2 页第 37 行 `X0 = 695 · 260 .` | 第 2 页第 23 行 `X0 = 704 · 260 .` |
| Corollary 19 陈述 | 第 12 页第 6 行 | 第 12 页第 5 行 |
| Corollary 19 证明中的分式 | 第 12 页第 17 行 | 第 12 页第 15 行 |
| Corollary 19 证明中的条件句 | 第 12 页第 30 行 | 第 12 页第 28 行 |
| Corollary 19 证明中的系数 | 第 12 页第 33 行 | 第 12 页第 31 行 |
| Corollary 19 证明中的下界 | 第 12 页第 38 行 | 第 12 页第 36 行 |
| Theorem 23 证明首段 | 第 15 页第 45 行 | 第 15 页第 45 行 |

共 7 处对 7 处，位置一一对应。原始命中清单在 `materials/route1/x0_lines_both_versions.txt`。

（本报告早期草稿曾断言「两版 X₀ 的数字在文本层取不到，只能用渲染图核对」；本轮实测推翻该断言：pdftotext 抽取层可稳定取到全部 7 处。该草稿断言作废，改以本表为准。反过来说，X₀ 的**逐字核对**仍以渲染图为最终依据，见 4.1。）

### 5.3 第 16 页的差异明细（本次亲跑）

除 X₀ 一路的连带改动外，第 16 页还有两类差异：

1. Corollary 24 表的若干行数值不同（印出版对 v3）：`276` 对 `369`、`3079` 对 `4366`、`12055` 对 `17096`、`948987` 对 `802380`、`1.14 · 10⁶` 对 `1.07 · 10⁶`；K 列 `4.68` 对 `4.64`、`4.30` 对 `5.26`、`3.81` 对 `4.78`、`1.33` 对 `1.89`、`1.54` 对 `2.18`、`9.46` 对 `1.34 · 10`（末项折算方式两版排版不同）。
2. Corollary 24 证明首句：印出版 `The first three lines follow from Theorem 21, all others except the last one from Corollary 19, ...`；v3 `The first two lines follow from Theorem 21, all others except the last one from Corollary 19, ...`（其余文字相同，断行位置不同）。

这两类差异都不落在定理 23 的七步或收尾句上。

---

## 6 上标与分式的核对方式

本节记录我判「上标」时实际用的两条依据，并说明其中一条为何不适用于以负号开头的指数。

**依据一（主）：渲染图亲读。** 在 150 dpi 渲染图上，第 15 页第七步句读作 `δ < (K+L)/K < δ + 1.11 · 10⁻⁴³ and K > 7.94 · 10²¹`：`−43` 与 `21` 都明显小于正文并抬高到行上，`(K+L)/K` 是带横线的上下分式。v3 同页同句同形。这是本轮「按渲染图核对」的原始依据。

**依据二（旁证，机制检查）：PDF 词盒几何。** 用 `pdftotext -bbox` 取该页每个词的四角，统计「每个 `10` 与其右侧相邻指数词」的盒高与 yMin 差（脚本 `scripts/final_verify.py`，输出在 `materials/route1/verify_line_and_offsets.txt`）。印出版第 15 页实测：

| 指数词 | yMin 差（负为抬高） | 盒高 |
|---|---|---|
| 11 | −1.349 | 7.97 |
| 20 | −1.349 | 7.97 |
| −32 | −0.461 | 5.01 |
| 15 | −1.943 | 7.97 |
| −36 | +0.133 | 5.01 |
| 17 | −1.349 | 7.97 |
| −38 | +0.133 | 5.01 |
| 18 | −1.349 | 7.97 |
| −39 | +0.124 | 5.01 |
| 19 | −1.358 | 7.97 |
| −40 | +0.133 | 5.01 |
| 19 | −1.349 | 7.97 |
| −41 | +0.133 | 5.01 |
| 20 | −1.349 | 7.97 |
| **−43** | **+0.133** | **5.01** |
| 21 | −1.349 | 7.97 |

v3 同页的对应表结构相同，`−43` 处为 dy = +0.031、盒高 5.01。

读法要说明白：**以负号开头的指数词，其 yMin 差不能直接当抬高量**，因为词盒的上沿由那个减号决定（减号本身矮而居中），所以 `−36`、`−38`、`−39`、`−40`、`−41`、`−43` 六者的差都在 `+0.12` 至 `+0.15` 这一窄带内，与正指数的 `−1.35` 不同族。真正把两类分开的是**盒高**：带负号的六个指数盒高一律 5.01，而不是它们的 `10` 底数的 7.97。因此几何证据支持的是「`−43` 与同页其它负号指数同族，即同属 `10` 的上标」，与依据一的亲读一致。

**明确不成立的用法**：不能用 yMin 差的正负去说 `−43`「不是上标」或「是降位」。若下游脚本按 yMin 差自动判上标，会在所有负号指数上系统性地判错，本条登记以免复现。

---

## 7 行号对照表

八栏：条目、版本、页、抽取行、来源等级、备注。

| 条目 | 版本 | 页 | 抽取行（本报告口径） | 来源等级 |
|---|---|---|---|---|
| Definition 4（含 X₀ 赋值） | 印出版 | 2 | 第 2 页第 37 行（页内 0 基） | 本次亲读（渲染图）＋本次亲跑（抽取） |
| Definition 4（同段） | v3 | 2 | 第 2 页第 23 行 | 本次亲读（渲染图）＋本次亲跑（抽取） |
| Definition 15 | 印出版 | 10 | 页内单独一行，位于章标题 `3 On Collatz m-cycles` 之后 | 本次亲读（渲染图） |
| Theorem 21 三式 | 印出版 | 13 | 三式分别位于该页上半，自 `Let v = …` 起至 `(2^v − 1)^δ ).` | 本次亲读（渲染图） |
| Theorem 21 证明末的两特例说明 | 印出版 | 14 | 该页末段 `which proves the general statement …` 起 | 本次亲读（渲染图） |
| Lemma 22 陈述 | 印出版 | 15 | 该页首段与第二段 | 本次亲读（渲染图） |
| Theorem 23 陈述与七步 | 印出版 | 15 | 自该页中部 `Theorem 23 (Main Theorem).` 起至页末 `K > 7.94 · 10²¹ .` | 本次亲读（渲染图）＋本次亲跑（抽取，第 15 页第 43 至 63 行） |
| Theorem 23 收尾句 | 印出版 | 16 | 该页首段两行 | 本次亲读（渲染图） |
| 同上七步 | v3 | 15 | 与印出版同页同序 | 本次亲读（渲染图） |
| 同定理 21 三式 | v3 | 13 | 与印出版同页同序 | 本次亲读（渲染图） |
| 勘误全文 | 勘误 | 1 至 2 | 两页 | 本次亲读（渲染图） |
| X₀ 七处位置 | 两版 | 2、12、15 | 见 5.2 表 | 本次亲跑（抽取） |
| 旧记录的第七步行号（`hercher5.txt:874` 至 `:876`） | 印出版 | 15 | 见备注 | 材料记录（本会话读出 `materials.md:104`、`:115`） |

备注行须说明：`materials.md:104` 记「页位：印出版第 15 页（页脚数字 15；PDF 页序第 15 页）」，与本轮亲跑一致；`materials.md:115` 记第七步句在 `hercher5.txt:874` 至 `:876`，该行号属**旧抽取文件**的行号，本机已无该文件之外的同一抽取件可比，故只作材料记录，不作本轮一手依据。本轮以重新下载的 PDF 重新抽取为准（见 2 与 5.2）。

---

## 8 失败点与未完成项

1. **印出版第 8、11、12 页未逐图亲读。** 本轮亲读覆盖第 2、10、13、14、15、16 页（印出版）与第 2、13、15、16 页（v3）与勘误两页。第 12 页的 Corollary 19（X₀ 的另外 5 处出现）只做了抽取层检索，未渲染亲读。状态：未完成。
2. **`+ 73` 与 `+ 1` 的印刷出入，本轮只作逐字转录，未做任何判定。** 按本轮分工，该出入不属本路线，且在下游材料中已登记（`materials.md:162`）。状态：登记完成，判定移交。
3. **第七步印数与我方取值的差额尚未给出。** 属路线 2 至 5 的重算工作，本路线不给数。状态：未完成（按分工不该由本路线完成）。
4. **定理 21 证明段首（第 13 页下半）与第 14 页全页的逐行差分只做了一次，未做第二种抽取器复核。** PyMuPDF 在本机 venv 内不可用（`ModuleNotFoundError: No module named 'fitz'`，本轮亲自复现），系统 `python3` 的 `fitz` 可用，但我未据此另做一套抽取，因此第 13、14 页「逐行相同」的结论只有一条抽取链支撑。状态：未完成（可信度标为「单链」）。

---

## 9 命令行与输出摘要

### 9.1 下载与哈希

```
cd .../thm23-eps/cycle-1/scripts && ./reproduce_hash.sh
```

输出（全文见 `materials/route1/hash_run_log.txt`）：三个 URL 各一次 `HTTP=200` 与 `SIZE`；「本次下载」三行与「轨道归档件」三行的 md5、字节数逐位相同（见第 2 节表）。

### 9.2 页位与页脚

```
pdftotext -f <p> -l <p> -bbox <pdf> out.html     # 对 p = 11..20
# 再把词按 yMin 过滤到页面下方 12% 取页脚数字
```

输出（`materials/route1/pdf_page_footers.txt`）：物理第 11 至 20 页的页脚依次为 11 至 20。

### 9.3 渲染与亲读

```
pdftoppm -png -r 150 -f 15 -l 15 <materials/hercher5.pdf> <materials/route1/render/printed_p15>
pdftoppm -png -r 150 -f 13 -l 13 <materials/arxiv-2201.00406v3.pdf> <materials/route1/render/v3_p13>
# 同法渲染印出版第 2、10、14、16 页，v3 第 2、15、16 页，勘误两页
```

随后用 Read 打开 `materials/route1/render/` 下的 PNG 逐图亲读（理由见第 1 节）。

### 9.4 抽取与差分

```
pdftotext <materials/hercher5.pdf> -            # 印出版全文
pdftotext <materials/arxiv-2201.00406v3.pdf> -  # v3 全文
pdftotext -f 15 -l 15 -bbox <pdf> page15.html   # 逐页词盒
```

差分：把两版同页词盒按 yMin 聚类成行后，用 `difflib.unified_diff`（上下文 0）比较。第 13、14 页差异块为 0；第 15 页 1 处；第 16 页若干处。落盘为 `materials/route1/version_diff_13_16.txt`，第 15 页两版转录另存 `printed_p15_transcript.txt` 与 `v3_p15_transcript.txt`。

### 9.5 上标几何

```
cd .../cycle-1/scripts && <venv python> final_verify.py
```

输出（`materials/route1/verify_line_and_offsets.txt`）：两版第 15 页含 `bounnd` 的整行，以及该页所有「`10` + 指数」的 yMin 差与盒高（见第 6 节两张表）。

### 9.6 版本差异的图像定位（机制检查）

```
cd .../cycle-1/scripts && <venv python> page_image_diff.py <印出版> <v3> 1 20 /tmp/route1_diff
```

输出（`materials/route1/page_image_diff_log.txt`）：每页一行差异像素数。须注意该检查的口径限制：两版由不同 Ghostscript 版本生成，字形栅格化本就有别，故**全页都有数千至上万像素差**；差异像素数只能用于排序定位（本轮最大者为第 1 至 5 页与第 12、16 页，与已知版面差异相符），不能作为「有无文字差异」的判据。文字差异以上一节的逐行差分为准。

---

## 10 局部新结论

1. **定理 23 第七步的印数，两版逐字相同，为 `δ + 1.11 · 10⁻⁴³`，指数 `−43` 处于上标位。**（本次亲读两版第 15 页渲染图；上标另经词盒几何旁证。）
2. **该步引导句逐字为 `Applying this lower bounnd a last time`，`bounnd` 三 n 为原文拼写；两版同。**（本次亲读。）
3. **原文在该处不使用符号 `ε`；`ε` 是我方对该上界增量项的命名。**（本次亲读；全书检索层面另经第 15 页整行转录复核。）
4. **两版在第 13、14 页逐行相同，第 15 页只差 X₀ 一行，第 16 页另差 Corollary 24 的表与证明首句。**（本次亲跑差分。）
5. **两版 X₀ 各出现 7 处，位置一一对应；印出版 `695 · 2⁶⁰`、v3 `704 · 2⁶⁰`。**（本次亲跑检索，清单见 5.2。）
6. **原文在定理 21 证明末明确写出 `For m₂ = m, this first sum is empty and therefore zero`，并且 `m₂ = m` 的特例式里不含 X₀ 项。**（本次亲读第 14、13 页。）
7. **勘误只补定理 21 证明中一处推导，不改变定理 21 陈述式的印刷常数，也不改变定理 23 七步中的任何数字；`1.11 · 10⁻⁴³` 未在勘误中出现。**（本次亲读勘误两页。）
8. **印出版的印刷页码等于物理页码（页脚实测，偏移为零）。**（本次亲跑。）

以上八条均属文献事实层，不含任何数学判决。

---

## 11 独立验证方式

1. **哈希复核**：跑 `scripts/reproduce_hash.sh`，比对打印的 md5 与字节数是否与第 2 节表逐位一致（三份都应一致）。
2. **第七步逐字复核**：`pdftoppm -png -r 150 -f 15 -l 15 materials/hercher5.pdf out` 后用 Read 打开，读该页倒数第三段 `Applying this lower bounnd a last time …` 一行，核对 `1.11` 与指数 `−43`；对 v3 同页同法。
3. **上标复核**：跑 `scripts/final_verify.py`，比对 `−43` 行的盒高是否为 5.01（与同页其它负号指数同族），并注意第 6 节关于 yMin 差不可用于负号指数的警告。
4. **版本对照复核**：跑 9.4 的差分流程，第 15 页应只出 X₀ 那一处；把该处与 `materials.md:146` 记的两行并列比对。
5. **X₀ 位置复核**：对两版全文抽取做 `grep`，印出版应得 7 处 `695`、0 处 `704`；v3 反之。
6. **勘误复核**：`pdftoppm -png -r 150 materials/corrigendum.pdf out` 后 Read，读首段与末段两句。

---

## 12 本报告自身的限制

1. 本报告是文献事实卡，不含任何取整、笔误或我方偏差的判定；第七步的差额量值需由路线 2 至 5 用严格算术给出。
2. 第 5.1 节的「逐行相同」只在一条抽取链上成立（见第 8 节第 4 条），且只覆盖第 13 至 16 页，不覆盖全文。
3. 第 9.6 节的图像差分**不是**文字差异判据，其数值差异主要由生成器版本造成。
4. 凡本报告标「材料记录」的行号（如旧的 `hercher5.txt:874`），其原始文件在本机已不在或未与本轮抽取件做逐字节同一性核对，引用时应回到本轮重新下载的 PDF。
