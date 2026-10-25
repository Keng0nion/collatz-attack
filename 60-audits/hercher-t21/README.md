# 60-audits/hercher-t21：Hercher 定理 21「窗口尾部」步的独立核查

**一句话说明**：核查 Hercher 2023（Journal of Integer Sequences 26，文章 23.3.5）定理 21 证明第 14 页底部「窗口尾部」那一步的公开争议，裁决为**采信「勘误版（附条件）」**——印出版那一步作为所载证明不成立（含一条对 ℓ ≥ 2 为假的幂不等式，且推理方向与 `T(n) < 3/n` 的递减性相反），m ≤ 91 在勘误版下恢复（m = 91 处余量 37.09935525747164 倍），第三方 Lean 的 82 是「拒绝勘误、退回 Remark 7 逐项界」这一种保守修法的天花板，不是论文假设下的天花板。

**读哪一份**：最终交付物是 `audit-report.md`。目录其余文件是它的材料与证据。

本目录由 2026 年 10 月 21 日的 Hercher 定理 21 核查工作流生成（工作流脚本见仓库根 `audit-workflow.ts` 第 458 行起的「更新仓库中受影响的文档」之前各阶段）；`audit-report.md` 是 2026 年 10 月 24 日的重写定稿，替代 10 月 21 日初版，结论未变（说明见该报告第 10 行）。

## 文件清单

1. `audit-report.md`——核查报告，324 行，md5 `f8d99b9dc218a1282a2dc8247dbe774f`（md5 与行数为 2026 年 10 月 24 日回填时实测）。含：一句话结论、争议是什么、三个版本各自独立重推、裁决、四个问题逐条判定、m = 20 至 95 的余量表要点、仍未确定的 13 条、对项目其它文档的影响清单、附录 A 实跑记录、对红队 12 条意见的回应与红队抽查记录。
2. `dispute.md`——争点简报（争议步骤、记号表、三个版本的口径对照、待答问题）。
3. `materials-primary.md`——一手材料（论文与勘误的可达性、逐字关键句、渲染图核对记录、打开状态表）。
4. `materials-thirdparty.md`——第三方材料（两个 Lean 仓库、独立审计 Étude 39、zbMATH 记录、社群讨论）。
5. `rederivation-as-printed.md`——印出版重推（含「对交叉反驳的回应」节）。
6. `rederivation-erratum.md`——勘误版重推（含「对交叉反驳的回应」节；采信版本的算法与逐节输出都在这里）。
7. `rederivation-lean-sound.md`——健全版重推（含「对交叉反驳的回应」节）。
8. `scripts/rederive-as-printed.py`、`scripts/rederive-erratum.py`、`scripts/rederive-lean-sound.py`——三份从零实现的重推脚本（互不复用），各带双实现或双精度自校验。md5 依次为 `ef11c235ddc9233661e83e894f586785`、`eed992e91cff915c0e136e8d46cc642c`、`a8aee0561aa0abd51c9387caacacd4d6`。
9. `scripts/margin_table.py`——定量闸门：逐 m 余量表（按路径载入勘误版脚本、直接调用其 `bootstrap`，保证表里的数字就是采信版本本身的输出），任一自检不过则以非零码退出。md5 `b9412a245b1bd41c39af120dc23b6931`。
10. `results/margin-table.txt`——上一条脚本的产物，123 行，md5 `b0a742be9f215f332d0f85750ad57366`：m = 20 至 95 的 K 下界、K 上界与余量倍数，末尾 8 条自检。
11. `.mimosa/`——钩子运行状态，不是产物，忽略。

md5 与行数均为 2026 年 10 月 24 日回填时在本机实测；报告附录 A 第 7 条记有同一组脚本 md5。

## 复现命令

记 `V = "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python"`（python 3.12.7，含 mpmath；venv 不在仓库内，重建命令见仓库根 `README.md` 第五节）。

1. 定量闸门（退出码 0 为通过；脚本会重写 `results/margin-table.txt`，内容应逐字节不变）：

   ```
   "$V" "/Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/scripts/margin_table.py"; echo "exit=$?"
   ```

   本次回填实跑：退出码 0，自检 8 / 8，表 md5 重跑前后同为 `b0a742be9f215f332d0f85750ad57366`。

2. 三份重推（在同一目录 `scripts/` 下执行，退出码都应为 0；印出版与健全版会把输出冻结到 `/tmp/rederive-as-printed.out` 与 `/tmp/rederive-lean-sound.out`，勘误版不写冻结件）：

   ```
   cd "/Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/scripts"
   "$V" rederive-as-printed.py
   "$V" rederive-erratum.py     # 应打印 余量倍数 K下界 / K上界 = 37.09935525747164492758953 与 最大可排除 m = 91
   "$V" rederive-lean-sound.py  # 应打印 stall K* = 4640282259296926456 与 K*/U(1.3993 at m = 83) = 0.999952051335
   ```

3. **材料不随仓库走**：材料收集与重推当时用的工作目录 `/tmp/hercher-audit/`（论文与勘误 PDF、其 `pdftotext` 抽取文本、渲染图）已不在本机（本次回填实测 `ls` 报 No such file or directory），所以报告与重推里凡引用这些文件**行号**之处都标「材料记录」；`/tmp/t21adj/`、`/tmp/dtatk3/` 同样不在。可复跑的是本目录的脚本与报告本身。

4. **路径垫片说明**：`audit-workflow.ts` 的闸门命令用的是工作区相对路径，为此仓库内留了两条只作路径垫片的符号链接（`collatz-attack/20-experiments/.venv/bin/python` 与 `collatz-attack/60-audits/hercher-t21/scripts/margin_table.py`），并在 `.gitignore` 里按仓库根锚定忽略；更正的修法是把闸门命令改成绝对路径，垫片可整体删除（记录见 `scripts/margin_table.py` 文档字符串第 53 至 72 行与报告 3.4）。

## 边界（诚实纪律）

1. 本目录的判定只针对那个争议步骤，**不改变「科拉茨猜想未被证明」这一事实**。
2. 「附条件」＝勘误没有公开的独立第三方评审记录（判断，不是材料原文），且勘误三处表述缺口以标准多面体分解与数值补上而**未形式化**。
3. 任何 Lean 工程都未编译（回填实测 `which lake lean elan` 无输出）；一切形式化宣称在本目录里都只是源文件文本证据，不是「构建通过」。
4. 本目录引用的数字都指向可复跑的脚本或报告内的实跑记录；凡记录转引、他人宣称与作者推断，报告已逐处标注。
