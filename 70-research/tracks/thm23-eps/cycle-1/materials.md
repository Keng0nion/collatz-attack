# 轨道 thm23-eps 第 1 轮一手材料：Theorem 23 第七步 ε 的 10% 至 30% 差异

收集人：材料收集员（本工作流子代理）
日期：2026 年 10 月 27 日
服务对象：本轨道 `plan.md` 第一节（疑点照抄）与第三节（五条子问题）
本文件只做材料收集、回原件核对与本次亲跑，**不作裁决**；凡属我个人推断的都单独标出。

## 〇、怎么读这份文件

1. 每条材料写明「我是否亲自打开」与「与疑点相关的逐字关键句」；逐字引文一律给到「路径:行号」。
2. 行号与证据分四类，逐处标注：
   1. **【本次亲跑】**＝本次执行命令所得（下载回执、md5、抽取、渲染、定位）；
   2. **【本次亲读（渲染图）】**＝本次用 `pdftoppm` 渲染后用 Read 逐张看过 PDF 页面；
   3. **【本次亲读（本次抽取）】**＝本次用 `pdftotext -layout` 重新抽取后的行号（与旧记录逐字节相同的文件另注明）；
   4. **【材料记录】**＝本次从项目内更早会话的文件里读到的行号、数字或声明；其原件是否在本机单独注明。
3. 逐字引文保留英文原文（含原文拼写与连接符），我自己的中文叙述遵本项目排版纪律。
4. 本文件**不含**对「论文取整、笔误、我方中间量有偏」的任何判决，也**不含**严格算术重算、窗口反演、七步取整穷举与末值复算（那些是路线 2 至 5 的任务）。本文件只保证一件事：原件的字、页位、上标，以及项目记录的出处，都可在本文件里追。

---

## 一、本次亲手下载并打开的一手原件（三份）

### 1.1 印出版 Hercher 2023（JIS 第 26 卷，文章 23.3.5）

1. 出处：`https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf`。
2. 本次下载回执（照录，`cycle-1/materials/` 下执行）：
   ```
   curl -sSL -o hercher5.pdf -w "http_code=%{http_code} size=%{size_download} content_type=%{content_type}\n" "https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf"
   → http_code=200 size=250655 content_type=application/pdf
   ```
3. 本机副本：`70-research/tracks/thm23-eps/cycle-1/materials/hercher5.pdf`（250655 字节，22 页，`file` 报 `PDF document, version 1.4, 22 pages`）；md5 实测 `3e2377bef0b1c0435dc455c9bbee43a1`。**与材料记录逐位一致**（材料记录：`70-research/cycle-2/materials.md:22` 与 `60-audits/hercher-t21/materials-primary.md:20` 记 250655 字节、md5 同上）。
4. 抽取文本：`hercher5.txt`（`pdftotext -layout`，1256 行），md5 实测 `d134d5822733bb647affacbaebb3b2f5`；**与材料记录的 `/tmp/h5.txt` 的 md5 逐位相同**（材料记录：`70-research/cycle-2/materials.md:407`）。因文本逐字节相同，旧报告对该文本的一切行号（如 `:852`、`:869`、`:822`）在文本层面仍可复用；我另抽查了 `:80` 至 `:83`、`:190`、`:506`、`:695`、`:796` 至 `:812`、`:822`、`:850`、`:852`、`:873` 至 `:876` 各处与本次逐行核对一致（**【本次亲读（本次抽取）】**）。
5. **我是否亲自打开**：是。渲染并逐字读了第 2、10、13、14、15、16 页（六张渲染图见 1.4 清单与 md5）。

**与疑点最直接的逐字关键句**

1. 第七步（第 15 页，**【本次亲读（渲染图）】**，`pages/h5-15.png`）：
   > `Applying this lower bounnd a last time we get m2 ≥ 91, δ < (K+L)/K < δ + 1.11 · 10⁻⁴³ and K > 7.94 · 10²¹ .`
   （`bounnd` 是原文印刷拼写，照录；`10⁻⁴³` 的上标为 `−43`。）
2. 抽取文本同处（**【本次亲读（本次抽取）】**，`hercher5.txt:874` 至 `:876`；分式被拆行、上标被压平，照录）：
   ```
   874:    Applying this lower bounnd a last time we get m2 ≥ 91, δ < K+L    K
   875:                                                                        < δ + 1.11 · 10−43 and
   876: K > 7.94 · 1021 .
   ```

### 1.2 勘误（Corrigendum to Article 23.3.5）

1. 出处：`https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf`。
2. 本次下载回执：【本次亲跑】`http_code=200 size=124287 content_type=application/pdf`。
3. 本机副本：`corrigendum.pdf`（124287 字节，2 页）；md5 实测 `f23d5f969116cb1af6e9b981b4b3ba7a`，**与材料记录一致**（材料记录：`60-audits/hercher-t21/materials-primary.md:126` 一类记录）。
4. 抽取文本：`corrigendum.txt`（88 行），md5 实测 `993f3f5a93188076c60c7357ac552eeb`，**与材料记录一致**（材料记录：`70-research/cycle-2/materials.md:409`）。
5. **我是否亲自打开**：是，渲染并逐字读了 2 页（`pages/corr-1.png`、`pages/corr-2.png`）。
6. 与疑点相关的关键句（**【本次亲读（渲染图）】**；抽取行号为 **【本次亲读（本次抽取）】**）：
   > `The derivation of the inequalities T(n_{m−m2+1+ℓ}) < 3/(2^v−1)^δ in the proof of Theorem 21 at the bottom of page 14 contains an error.`（抽取 `corrigendum.txt:14` 命中其尾行 `of Theorem 21 at the bottom of page 14 contains an error. To show the`）
   > `For a local minimum n_i in the hypothetically existing Collatz cycle, define x_i := log(n_i + 1)/log 2.`
   > `... Without loss of generality, let the cycle be entered in such a way that this sum is maximal. ...`（抽取 `:28` 命中 `Using the same argument as on page 13` 一段）
   > `By Remark 7, we have T(n_i) < 3/n_i. Thus, Σ_{i=m−m2+1}^{m} T(n_i) < Σ_{i=m−m2+1}^{m} 3/(2^{x_i} − 1) =: S(x_{m−m2+1}, ..., x_m).`
   > `Since all x_i are positive, the function S is convex and attains its maximum value at a vertex of the polytope determined by the constraints x_i ≥ 1, x_{i+1} ≤ δx_i, x_{m−m2+1} < δx_m, and x_{m−m2+1} + · · · + x_m ≥ (m2/m)·K. Thus, at least m2 of these constraints must be active, i.e., must hold with equality.`（抽取 `:43` 命中首半句）
   > `... x_{m−m2+1} = (m2/m)·K·(δ − 1)/(δ^{m2} − 1) = v,`（抽取 `:65` 命中 `cyclic permutation` 一段）
   > `... = 3/(2^v − 1) + 3·(m2 − 1)/(2^{δv} − 1) < 3/(2^v − 1) + 3·(m2 − 1)/((2^v − 1)^δ), which is exactly what we wanted to prove.`（抽取 `:83` 命中 `which is exactly what we wanted to prove.`；`:84` 为致谢 `The author is highly grateful to Xinjun Wang, ORCID 0009-0007-5895-...`）

### 1.3 arXiv v3（2201.00406v3）

1. 出处：`https://arxiv.org/pdf/2201.00406v3`。
2. 本次下载回执：【本次亲跑】`http_code=200 size=236361 content_type=application/pdf`。
3. 本机副本：`arxiv-2201.00406v3.pdf`（236361 字节，22 页）；md5 实测 `92a5047052911ac7a45d59cc32efbe65`，**与材料记录一致**（材料记录：`70-research/cycle-2/materials.md:95`）。
4. 抽取文本：`arxiv-2201.00406v3.txt`（1256 行），md5 实测 `c8759c1c68eea30e0050ca5247b97ebb`（**【本次亲跑】新测**；材料记录未测过该文件的 md5）。
5. **我是否亲自打开**：是，渲染并逐字读了第 14、15 页（`pages/arx-14.png`、`pages/arx-15.png`）。

### 1.4 渲染图清单（**【本次亲跑】**，md5 实测）

命令（照录，可复现）：
```
cd "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/thm23-eps/cycle-1/materials"
pdftoppm -png -r 150 -f 13 -l 16 hercher5.pdf pages/h5
pdftoppm -png -r 150 -f 14 -l 15 arxiv-2201.00406v3.pdf pages/arx
pdftoppm -png -r 150 -f 1 -l 2 corrigendum.pdf pages/corr
pdftoppm -png -r 150 -f 2 -l 2 hercher5.pdf pages/h5
pdftoppm -png -r 150 -f 10 -l 10 hercher5.pdf pages/h5
```

| 文件名 | 来源与页 | md5 |
|---|---|---|
| `pages/h5-02.png` | 印出版第 2 页（Definition 4） | `1a54d81e9b9777c7aaafbf5305a915ef` |
| `pages/h5-10.png` | 印出版第 10 页（Definition 15） | `c238116ba7aa9362a0c498c3b9e5adf1` |
| `pages/h5-13.png` | 印出版第 13 页（Theorem 21） | `6ef685fc10469f668de61afd7eeb61e6` |
| `pages/h5-14.png` | 印出版第 14 页（证明末式） | `6d9d688d783ef792a9fd6f4751ebfcef` |
| `pages/h5-15.png` | 印出版第 15 页（Theorem 23 第七步） | `f696b974bbc4243694a0388eee30a904` |
| `pages/h5-16.png` | 印出版第 16 页（收尾句） | `032d85caab786dee6a99032e12521ea4` |
| `pages/arx-14.png` | arXiv v3 第 14 页 | `d83792d05199edc864afe6bf86e94061` |
| `pages/arx-15.png` | arXiv v3 第 15 页 | `f106359aa85f53ecdb69777b5a97334b` |
| `pages/corr-1.png` | 勘误第 1 页 | `a7c7973e65a2b1ac6be465bd3170bb4c` |
| `pages/corr-2.png` | 勘误第 2 页 | `5ec441677d201128d324b32f702f1492` |

跨会话一致性旁证（**【本次亲跑】**）：`h5-13.png`、`h5-14.png`、`corr-2.png` 三张的 md5 与 `70-research/cycle-1/materials.md:317` 记录的三张 150 dpi 渲染图（`hercher-p13-13.png`、`hercher-p14-14.png`、`corr-p2-2.png`）**逐位相同**——同一 PDF、同一 dpi、同一页加上同一工具，产出同一字节，可作为「本次渲染与上一轮渲染是同一输入」的核对。

---

## 二、事实层逐字事实卡（子问题 1）

### 2.1 第七步 ε 的印数、上标与页位（**【本次亲读（渲染图）】**）

1. 页位：印出版第 15 页（页脚数字 `15`；PDF 页序第 15 页），段落是 Theorem 23 证明的最后一段。
2. 印数：`δ + 1.11 · 10⁻⁴³`。逐字符核对：`1.11` 后是居中圆点，`10` 的指数整个在上标位、写作 `−43`（负号与 43 都在上标位）；**不是**用半角连接符连接指数的机器记法，也未见到任何脚注、勘误记或边注出现在该页。
3. 同行后半句为 `and K > 7.94 · 10²¹`（上标 `21`）。
4. 该句起始措辞为 `Applying this lower bounnd a last time`——`bounnd` 三 n 拼写为原文印刷（arXiv v3 同句同样拼写，见 2.5）。

### 2.2 第六步印数与第七步输入的关系（**【本次亲读（渲染图）】**）

1. 第六步句（第 15 页，位于第七步句紧挨着的上一段）：
   > `From there we get m2 ≥ 86, δ < (K+L)/K < δ + 2.3 · 10⁻⁴⁰ and K > 7.76 · 10¹⁹ . And from this we get m2 ≥ 88, δ < (K+L)/K < δ + 5.3 · 10⁻⁴¹ and K > 2.05 · 10²⁰ .`
2. 第七步句紧接其后：
   > `Applying this lower bounnd a last time we get m2 ≥ 91, δ < (K+L)/K < δ + 1.11 · 10⁻⁴³ and K > 7.94 · 10²¹ .`
3. 由此可确证的只是**措辞层面**的事：第七步的输入是「this lower bound」，即第六步刚给出的那个 K 下界、印刷为 `K > 2.05 · 10²⁰`；原文在第七步处**没有**写任何精确 K 值，也没写这个下界取自哪一步的哪个精度。**「论文实际代入的 K 是印出的 2.05×10²⁰、还是其背后的更精确下界（项目记为 2.05632218873398596256×10²⁰）、还是别的取整」属重算与推断，交路线 2、4 裁定；本文件不裁。**
4. 抽取文本对照（**【本次亲读（本次抽取）】**）：第六步句在 `hercher5.txt:870` 至 `:873`（`:873` 逐字 `< δ + 5.3 · 10−41 and K > 2.05 · 1020 .`），第七步句在 `:874` 至 `:876`。

### 2.3 Theorem 23 全段七步逐字（**【本次亲读（渲染图）】**，第 15 页；抽取行号 `hercher5.txt:850` 至 `:876` 为**【本次亲读（本次抽取）】**，本次亲核）

> `Theorem 23 (Main Theorem). There is no m-cycle with m ≤ 91.`
> `Proof. Let m ≤ 91. From Theorem 3 in [12] we know that K > 7 · 10¹¹.`
> `With X0 = 695 · 2⁶⁰ ≈ 8 · 10²⁰, as given in Definition 4, we get m2 ≥ 47. Now, from Theorem 21 we have δ < (K+L)/K < δ + 6.9 · 10⁻³².`
> `By using continued fractions as in Lemma 22, we can now get a better lower bound for K with K > 5.2 · 10¹⁵.`
> `And now we can reiterate this process!`
> `In the next run, we get m2 ≥ 67, δ < (K+L)/K < δ + 5.1 · 10⁻³⁶ and, therefore, K > 3.97 · 10¹⁷.`
> `Applying this newer bound on K once more, we get m2 ≥ 77, δ < (K+L)/K < δ + 4.1 · 10⁻³⁸ and, hence, K > 4.64 · 10¹⁸.`
> `In the forth run we get m2 ≥ 82, δ < (K+L)/K < δ + 2.3 · 10⁻³⁹ and with this K > 2.74 · 10¹⁹.`
> `From there we get m2 ≥ 86, δ < (K+L)/K < δ + 2.3 · 10⁻⁴⁰ and K > 7.76 · 10¹⁹. And from this we get m2 ≥ 88, δ < (K+L)/K < δ + 5.3 · 10⁻⁴¹ and K > 2.05 · 10²⁰.`
> `Applying this lower bounnd a last time we get m2 ≥ 91, δ < (K+L)/K < δ + 1.11 · 10⁻⁴³ and K > 7.94 · 10²¹.`

（按渲染图逐句抄录；`In the forth run` 的 `forth` 为原文拼写。与抽取文本对照无出入，除分式排版。）

### 2.4 收尾句（**【本次亲读（渲染图）】**，第 16 页首段；按 plan.md 的「抽查第 16 页收尾句」执行）

> `But this last lower bound on K is larger than the upper bound of K < 1.4784mδ^m < 2.2 · 10²⁰ given by Simons and de Weger [12]. Thus, no such m-cycle can exist.`

### 2.5 arXiv v3 同处逐字对照（**【本次亲读（渲染图）】**，第 14、15 页）

1. arXiv v3 第 15 页：Theorem 23 全段与印出版**逐字相同**，含 `bounnd` 拼写与全部七步数字；第七步句两版都印 `δ + 1.11 · 10⁻⁴³`、`K > 7.94 · 10²¹`；第六步句两版都印 `K > 2.05 · 10²⁰`。
2. 两版可见的逐字差异只在证明首段与 X0 定义（另见 3.3）：
   > arXiv v3：`With X0 = 704 · 2⁶⁰ ≈ 8.1 · 10²⁰, as given in Definition 4, we get m2 ≥ 47.`
   > 印出版：`With X0 = 695 · 2⁶⁰ ≈ 8 · 10²⁰, as given in Definition 4, we get m2 ≥ 47.`
3. arXiv v3 抽取行号（**【本次亲读（本次抽取）】**）：Definition 4 的 `X0 = 704 · 2⁶⁰` 在 `arxiv-2201.00406v3.txt:81`；Theorem 23 在 `:861`；证明首段在 `:863`；第六、七步在 `:884` 至 `:887`。印出版对应行号（**【本次亲读（本次抽取）】**）：`:83`、`:850`、`:852`、`:873` 至 `:876`。
4. 事实层结论：**arXiv v3 的第七步 ε 印数与印出版逐字相同**；两版差异不落在第七步句本身，而落在 X0 定义与证明首段（改 X0 是否改第七步 ε，属路线 2 的重算，本文件不裁）。

### 2.6 第七步所用公式的逐字（供路线 2 至 5 对齐记号）

1. Definition 4（第 2 页，**【本次亲读（渲染图）】**；抽取 `hercher5.txt:80` 至 `:83` 为**【本次亲读（本次抽取）】**）：
   > `We define X0 as the largest number for which it is known that for all positive integers n ≤ X0 their Collatz sequences reach the trivial cycle. As of the date of writing this paper, we have`
   > `X0 = 695 · 2⁶⁰ .`
2. Definition 15（第 10 页，**【本次亲读（渲染图）】**；抽取 `:506` 把分式压平成 `let δ := log(2) > 1`，渲染图确认分子是 `log(3)`）：
   > `From now on, let δ := log(3)/log(2) > 1.`
3. Theorem 21 陈述（第 13 页，**【本次亲读（渲染图）】**；抽取 `:695` 至 `:711`，`:695` 本次亲核）：
   > `Let K be the number of odd numbers in a given m-cycle, and let L be the number of even numbers in it. Further, assume there exists a positive integer m2 with`
   > `m2 ≤ m and (δ^{m2} − 1)/(δ − 1) · log((162/97)·X0)/log(2) ≤ (m2/m)·K.`
   > `Let v = (m2/m)·K·(δ − 1)/(δ^{m2} − 1). Then we get`
   > `δ < (K+L)/K < δ + 1/(K·3 log(2)) · ( (97(m − m2) + 73)/(54·X0) + 3/(2^v − 1) + 3·(m2 − 1)/((2^v − 1)^δ) ).`
   > `If m2 = m − 1 we get the better estimate`
   > `δ < (K+L)/K < δ + 1/(K·3 log(2)) · ( 3/X0 + 3/(2^v − 1) + 3·(m − 2)/((2^v − 1)^δ) )`
   > `and for m2 = m`
   > `δ < (K+L)/K < δ + 1/(K·3 log(2)) · ( 3/(2^v − 1) + 3·(m − 1)/((2^v − 1)^δ) ).`
   两点须注意（均为对渲染图文本的直接读出）：陈述页印 `+ 73`；`m2 = m` 特例式里**没有 X0 项**——第七步正是 `m2 = m = 91` 这个特例。
4. 第 14 页争议步与末式（**【本次亲读（渲染图）】**；抽取行号 **【本次亲读（本次抽取）】**：争议步段 `:796` 至 `:801`、末式段 `:803` 至 `:812`，本次亲核；材料记录曾记 `:798` 至 `:801` 与 `:804` 至 `:812`，同一段，行号起点各差一两行，属表述粒度差异）：
   > `Now this gives T(n_{m−m2+1}) < 3/(2^v−1) and, since`
   > `n_{m−m2+1+ℓ} < n_{m−m2+1}^{(δ^ℓ)} ≤ n_{m−m2+1}^δ , we get the inequality T(n_{m−m2+1+ℓ}) < 3/((2^v − 1)^δ). Using this together with Theorem 14 and m1 := m − m2, we get`
   > `Σ_{i=1}^{m} T(n_i) = Σ_{i=1}^{m−m2} T(n_i) + T(n_{m−m2+1}) + Σ_{i=m−m2+1+1}^{m} T(n_i) < (97(m − m2) + 1)/(54·X0) + 3/(2^v − 1) + 3·(m2 − 1)/((2^v − 1)^δ),`
   > `which proves the general statement for 1 ≤ m2 ≤ m. For m2 = m − 1, the first sum Σ_{i=1}^{m−m2} T(n_i) = T(n_1) can be better bounded above by 3/X0, as seen in Remark 7. For m2 = m, this first sum is empty and therefore zero.`
   （**证明末行印 `+ 1`，与陈述页的 `+ 73` 不同**；两处均为本次亲读渲染图所见。）
5. Lemma 22 陈述（第 15 页，**【本次亲读（渲染图）】**；抽取 `:822` 至 `:825`，`:822` 本次亲核）：
   > `Let 0 < α < β be two real numbers with continued fraction expansions α = [a0; a1, . . . , ak−1, ak, . . .] and β = [a0; a1, . . . , ak−1, bk, . . .]. Then every fraction in the open interval (α, β) has a denominator which is not smaller than the one of γ = [a0; a1, . . . , ak−1, ck] with ck = min(ak, bk) + 1.`
6. Remark 7（**【本次亲读（本次抽取）】** `:190`：`We have T (ni ) < n3i < X30 for all 1 ≤ i.`；上标被压平；「读作 `T(n_i) < 3/n_i < 3/X0`」这一复原是**材料记录读法**（`70-research/cycle-2/materials.md:67`），本次未渲染该页）。

---

## 三、我方记录（【材料记录】；各文件内容为本次亲读，其内部数字是更早会话的产物）

### 3.1 疑点登记处

1. `70-research/cycle-1/route-4.md`（本次亲读全文 383 行；其内部对 `/tmp/h5.txt`、`/tmp/corr.txt` 的行号引用均为**材料记录**，原件本次实测不在本机）：
   1. `:55` 至 `:60`（我方七步链条，逐字）：
     > `m2 = 47, 67, 77, 82, 86, 88, 91`；
     > `K = 5267319278509397, 397560349370386783, 4640282259296926456, 27444133206411171953, 77692117359936589403, 205632218873398596256, 7941964418702608664581`；
     > `ε = 6.89235×10⁻³²、5.06614×10⁻³⁶、4.00161×10⁻³⁸、2.2658×10⁻³⁹、2.25975×10⁻⁴⁰、5.20714×10⁻⁴¹、1.22979×10⁻⁴³`。
   2. `:61` 至 `:63`（论文印数转抄）：`K > 5.2e15, 3.97e17, 4.64e18, 2.74e19, 7.76e19, 2.05e20, 7.94e21`、`δ + 6.9e-32, 5.1e-36, 4.1e-38, 2.3e-39, 2.3e-40, 5.3e-41, 1.11e-43`。
   3. `:66` 至 `:68`（差异的原始登记，逐字）：
     > `第 7 步 ε 我算 1.22979×10⁻⁴³、论文给 1.11×10⁻⁴³，相差约 10%，**我未定位原因**（换成论文写的取整阈值 2.05×10²⁰ 我算 1.4492163×10⁻⁴³，反而更远）。该步的 K 值 7.94×10²¹ 与我复算逐位相同，故不影响链条数值。`
   4. `:142` 至 `:145`（§2.5 第 3 条，逐字）：
     > `**一处未解释的差异（登记）**：论文 Theorem 23 第 7 步写 ε < 1.11×10⁻⁴³，我算 1.2297916×10⁻⁴³（把阈值换成论文写的 2.05×10²⁰ 得 1.4492163×10⁻⁴³），相差约 10% 至 30%，**我未定位原因**（该步的 K 值 7.94×10²¹ 与我复算逐位相同，故不影响链条数值）。可能是论文的取整或笔误，也可能是我对中间量的取法有偏，**未证，仅登记**。`
   5. `:284`（失败点清单第 3 条）：`**论文 Theorem 23 第 7 步 ε 的 10% 至 30% 差异未定位**（§2.5 第 3 条）。`
2. `70-research/cycle-1/summary.md:108`（本次亲读，逐字）：`论文 Theorem 23 第 7 步 ε 的 10% 至 30% 差异未定位（复算 1.22979×10⁻⁴³ 对论文 1.11×10⁻⁴³）。`
3. `70-research/ledger.md`（共享账本，只读）：
   1. `:26`（下一轮该做什么，第 5 条，逐字）：`**定位论文 Theorem 23 第 7 步 ε 的 10% 至 30% 差异**（判断是论文取整或笔误，还是我方中间量取法有偏）。`
   2. `:111`（1.4 未决第 4 条，逐字）：`**论文 Theorem 23 第 7 步 ε 的 10% 至 30% 差异未定位**（route-4 §2.5：复算 1.22979×10⁻⁴³ 对论文 1.11×10⁻⁴³，换论文写的取整阈值反而更远），原因未查明。`
4. `70-research/cycle-1/materials.md`（第 1 轮材料件；本次亲读其相关行）：
   1. `:59`：Theorem 23 段的转抄，含 `1.11 · 10^−43` 与 `7.94 · 10^21`（材料记录）。
   2. `:320`（自认的核对范围，逐字要点）：`**仅以 pdftotext -layout 抽取文本为准，未逐张看渲染图**：论文的第 9 至 13 页与第 15 页、参考文献页……建议先渲染对应页复核。`——**正是本轨道要补的第 15 页**；本次已补（第二节 2.1、2.3）。
   3. `:377`（陈述层遗留，逐字要点）：`第七步 ε 与复算值差约 11%（论文印 1.11×10⁻⁴³，复算 1.22979×10⁻⁴³，两者落在同一 Lemma 22 区间）。`

### 3.2 三处「已解释」的登记（本轨道判决书要逐条处置的对象）

1. `60-audits/hercher-t21/rederivation-as-printed.md`（本次亲读 `:132` 至 `:150`、`:315` 至 `:345`）：
   1. `:136` 至 `:144` 七步对照表：第 7 行逐字为 `| 7 | 91 / 91 | 1.229792×10⁻⁴³ | 1.11×10⁻⁴³ | 7941964418702608664581 | 7.94×10²¹ | 相符 |`；第 1、2、5、6 步末列标「论文截断」。
   2. `:146`（逐字要点）：`论文把每个新 K 只印到 2 至 3 位有效数字……我的七个 q_min 四舍五入到论文的印刷有效位数后，与印刷值三处相符（4.64、2.74、7.94）、四处论文取的是截断而非四舍五入（5.2、3.97、7.76、2.05）`。
   3. `:148`（解释本体，逐字）：`**第七步那 10.8% 现已解释清楚**（这是交叉反驳带来的收获，我复核过）：ε(91, 91, K = 2.06×10²⁰) = 1.1177766×10⁻⁴³，正是论文印的 1.11×10⁻⁴³；用未取整的 K = 2.056322…×10²⁰ 得 1.2297916×10⁻⁴³（我的值）；用论文印刷的截断值 2.05×10²⁰ 则得 1.4492163×10⁻⁴³。也就是说论文的第七步 ε 是把第六步的 K 取整到 2.06×10²⁰ 后向前传的，与我用精确 K 的结果落在同一个 Lemma 22 单元内，故 q_min 不受影响。这不是我的算法误差，是论文自身的取整传播。`
   4. `:322`（并入正）与 `:341`（四处截断的复述）：两处本次亲读，内容与上引一致。
2. `60-audits/hercher-t21/audit-report.md:226`（本次亲读，逐字）：`第七步 ε 的约 10.8% 差异已被解释为「论文把第六步的 K 取整到 2.06×10²⁰ 后向前传」（rederivation-as-printed.md:148、:322），但该解释依赖对论文取整习惯的推断。`
   同文 `:272`（独立数值复算段，逐字要点）：含 `c = 70.1808063283083668248487894995`、`X₀ = 801280445701758648320`、`margin(91) = 37.09935525747164492758953`。
3. `70-research/cycle-2/route-5.md`（本次亲读 `:160` 至 `:230`、`:320` 至 `:345`、`:430` 至 `:445`）：
   1. `:206` 与 `:219`（三点代入表）：`2.05×10²⁰ → 1.44921627253094092×10⁻⁴³`；`2.05632218873398596256×10²⁰（= K*）→ 1.22979157996235308×10⁻⁴³`；`2.06×10²⁰ → 1.11777663068838816×10⁻⁴³`。
   2. `:221`（裁决段，逐字要点）：`论文印的 1.11×10⁻⁴³ 与把 K 取 2.06×10²⁰（论文自己第六步输出「K > 2.05×10²⁰」的三位取整）代入同式所得吻合……复现是事实；「作者有意取整」仍是推断，本轮不改登记的证据等级。第六步的 1.8% 差异仍未归因。`
   3. `:327`（差异汇总第 5 条，逐字要点）：`本轮定位为「论文用 K = 2.06×10²⁰ 代入同式」`。
   4. `:439`（证据表行，逐字要点）：`论文第七步 ε | K = 2.06×10²⁰ 时 1.11777663068838816×10⁻⁴³ | …… | 与印数 1.11×10⁻⁴³ 吻合；K = 2.05×10²⁰ 给 1.44921627253094092×10⁻⁴³、K* 给 1.22979157996235308×10⁻⁴³（后两者与 route-4.md:145 逐位一致）`。

### 3.3 论文印数的旁证转抄与版本差异记录

1. `70-research/cycle-2/materials.md:57` 至 `:64`（第 15 页七步转抄；本次亲读其文件）：`:64` 逐字含 `Applying this lower bounnd a last time we get m2 ≥ 91, δ < (K+L)/K < δ + 1.11 · 10^−43 and K > 7.94 · 10^21.`
2. `60-audits/hercher-t21/materials-primary.md:96` 至 `:100`（同段转抄与七步数据表；本次亲读其文件，`:100` 逐字为 `七步数据（我逐项核对）：m₂ = 47、67、77、82、86、88、91；eps = 6.9 · 10^−32、……1.11 · 10^−43；K > 5.2 · 10^15、……7.94 · 10^21。`）。
3. `70-research/cycle-2/materials.md:92` 至 `:103`（版本差异记录；本次亲读）：`arXiv v3 :81：X0 = 704 · 2^60 .` 对 `印出版 :83：X0 = 695 · 2^60 .`；并记 `项目与勘误都按印出版的 695·2^60 算`（引 `r4x_core.py:58`）。
4. 本次实测补强（**【本次亲读（本次抽取）】**）：上述 `:83` 与 `:81` 两行号本次已在两份抽取文本上逐行核对命中（见 2.5 第 3 条、2.6 第 1 条）。

---

## 四、本次亲手执行的命令与原始输出（照录，可复现）

1. 下载（`cycle-1/materials/` 下执行）：
   ```
   curl -sSL -o hercher5.pdf -w "http_code=%{http_code} size=%{size_download} content_type=%{content_type}\n" "https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf"
   → http_code=200 size=250655 content_type=application/pdf
   curl -sSL -o corrigendum.pdf -w "..." "https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf"
   → http_code=200 size=124287 content_type=application/pdf
   curl -sSL -o arxiv-2201.00406v3.pdf -w "..." "https://arxiv.org/pdf/2201.00406v3"
   → http_code=200 size=236361 content_type=application/pdf
   ```
2. 校验：
   ```
   md5 -q hercher5.pdf corrigendum.pdf arxiv-2201.00406v3.pdf
   → 3e2377bef0b1c0435dc455c9bbee43a1 / f23d5f969116cb1af6e9b981b4b3ba7a / 92a5047052911ac7a45d59cc32efbe65
   file hercher5.pdf corrigendum.pdf arxiv-2201.00406v3.pdf
   → PDF document, version 1.4, 22 pages ／ version 1.5 ／ version 1.4, 22 pages
   ```
3. 抽取与渲染：命令见 1.4；抽取行数 `1256 / 88 / 1256`，md5 `d134d5822733bb647affacbaebb3b2f5 / 993f3f5a93188076c60c7357ac552eeb / c8759c1c68eea30e0050ca5247b97ebb`。
4. 行号定位（`grep -n` 与 `awk`，本次逐行命中）：印出版 `:80`、`:83`、`:190`、`:506`、`:695`、`:796` 至 `:812`、`:822`、`:850`、`:852`、`:873` 至 `:876`；arXiv v3 `:81`、`:861`、`:863`、`:884` 至 `:887`；勘误 `:14`、`:22`、`:28`、`:43`、`:65`、`:83`、`:84`。
5. 旧件可达性实测（**【本次亲跑】**）：`ls` 查 `/tmp/h5.pdf`、`/tmp/h5.txt`、`/tmp/corr.pdf`、`/tmp/corr.txt`、`/tmp/sidw144.txt`、`/tmp/c2-arxiv.pdf`、`/tmp/c2-pages/`、`/tmp/hercher-audit/`、`/tmp/r3/`、`/tmp/t21adj/`、`/tmp/dtatk3/`，全部 `No such file or directory`。

---

## 五、与疑点直接相关的观察（事实层，不裁决）

1. 第七步 ε 印数已由渲染图逐字钉住：`1.11 · 10⁻⁴³`，页 15，上标 `−43`（**【本次亲读（渲染图）】**）。第六步印数 `K > 2.05 · 10²⁰` 与其相邻，措辞上后者（「this lower bound」）是前者的输入（**【本次亲读（渲染图）】**）。
2. arXiv v3 的第七步句与印出版逐字相同（含 `bounnd` 拼写与全部数字）；两版可见差异只在 X0（704 对 695）与由此带出的 `≈8.1` 对 `≈8`（**【本次亲读（渲染图）】**）。
3. 第七步是 `m2 = m = 91` 的特例；Theorem 21 的 `m2 = m` 特例式（第 13 页渲染图）**没有 X0 项**（**【本次亲读（渲染图）】**）。此条只是对定理文本的直接读出，供路线 2 与 4 使用（X0 是否仍通过可行集或其它环节进入本步，另算）。
4. 前人文件自认「论文的第 15 页未逐张看渲染图」（`70-research/cycle-1/materials.md:320`，**材料记录**）；本次已渲染并亲读第 15、16 页（第二节 2.1、2.3、2.4）。
5. 三条「已解释」的登记（3.2）与账本「未定位」（3.1 第 3 条）目前**并存**；本文件只保证两边逐字都已收集，如何处置（维持、升级、推翻）由裁决环节按 `plan.md` 第六节判据裁定。

---

## 六、打不开、找不到、未核实、未做的（含尝试过什么）

1. **旧临时件全部不在本机**（**【本次亲跑】**实测）：`/tmp/h5.txt`、`/tmp/corr.txt`、`/tmp/sidw144.txt`、`/tmp/c2-arxiv.pdf`、`/tmp/c2-pages/`、`/tmp/hercher-audit/`、`/tmp/r3/`、`/tmp/t21adj/`、`/tmp/dtatk3/` 均报 `No such file or directory`。**后果**：一切对这些路径的行号引用只能标「材料记录」；本次以重新下载的三份原件为准（印出版与勘误的 pdf、txt 的 md5 与记录逐位一致，故旧行号在文本层面仍可复用，引用时须带「本次抽取 md5 相同」的说明）。
2. **未打开（不属本疑点关键路径，如实登记）**：SdW v1.44 原件（只读项目内记录；其使用记录见 `70-research/cycle-2/materials.md:84` 至 `:90` 与 `70-research/cycle-1/route-4.md:21` 至 `:22`）、Rhin 1987、Hercher 的计算附件（`collatz_cycle.cpp` 等）、任何 Lean 或 Coq 仓库。
3. **未做**：严格有理算术重算、窗口反演、七步取整约定穷举、末值连分数复算——全属路线 2 至 5；本文件不做判决，不给出「论文取整、笔误、我方有偏」的结论。
4. **未运行**任何项目脚本（`r4x_*.py`、`c2r5_*.py`、三份 `rederive-*.py`、`verify.py` 等一个都没跑）；本文件列出的项目数字一律是转引（材料记录）。特别地，避雷清单点名的 `r4x_run1.py` 至 `r4x_run6.py` 本次未跑，不会覆盖 `cycle-1/scripts/results/*.out`。
5. **本会话工具通道异常登记**：本会话中途有若干次工具调用的回复被延迟或返回占位文本，已通过重试恢复；第一至第四节列出的每个下载回执、md5、渲染图与引文，都是**恢复后重新实跑或重新读过所见**。

---

## 七、版本基线（**【本次亲跑】**实测）

| 文件 | 字节或行数 | md5 | 性质 |
|---|---|---|---|
| `hercher5.pdf` | 250655 字节，22 页 | `3e2377bef0b1c0435dc455c9bbee43a1` | 本次下载 |
| `hercher5.txt` | 1256 行 | `d134d5822733bb647affacbaebb3b2f5` | 本次抽取 |
| `corrigendum.pdf` | 124287 字节，2 页 | `f23d5f969116cb1af6e9b981b4b3ba7a` | 本次下载 |
| `corrigendum.txt` | 88 行 | `993f3f5a93188076c60c7357ac552eeb` | 本次抽取 |
| `arxiv-2201.00406v3.pdf` | 236361 字节，22 页 | `92a5047052911ac7a45d59cc32efbe65` | 本次下载 |
| `arxiv-2201.00406v3.txt` | 1256 行 | `c8759c1c68eea30e0050ca5247b97ebb` | 本次抽取（新测） |
| `pages/h5-*.png`（6 张） | 150 dpi | 见 1.4 表 | 本次渲染 |
| `pages/arx-*.png`（2 张） | 150 dpi | 见 1.4 表 | 本次渲染 |
| `pages/corr-*.png`（2 张） | 150 dpi | 见 1.4 表 | 本次渲染 |

---

*本文件只做材料收集与回原件核对，不作裁决；科拉茨猜想仍是开放问题，本文件不含任何对它本身的推进。*
