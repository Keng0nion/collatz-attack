# kcross-tail 第 1 轮自足摘要（cycle-1）

**日期**：路线产物 2026 年 10 月 28 日；收尾裁决与闸门复核 2026 年 10 月 29 日。
**状态**：本轮结束。轮级闸门退出码 **−1**；裁决自写闸门 `verify.py` 退出码 **0**（判据 57 条、FAIL 0 条）。本摘要自足：只读本文件即可知道本轮做了什么、结论与边界、怎么复现、还剩什么。
**口径**：全部数字取「项目重建物 Ψ、m = 92、X₀ = `695·2⁶⁰`（印出版）、开区间、min_eps 约定」；`704·2⁶⁰`（arXiv v3）未进入任何数字。科拉茨猜想未被证明也未被推翻；本轮的「已证」一律是「初等纸面推理 + 本机实跑证书」意义上的，不是形式化证明。

## 一、疑点

把轨道 kcross-proof 的四条已终态路线成果收尾，做三件事并各出一份报告：(a) 对抗复核——挑出四份报告被夸大或不成立处，重点抽验三条硬声明：「T = R」（两侧各自的论证）、「T 的两侧严格区间宽 `1.161777574454×10⁻¹⁰²`」、「分岔窗口从 `2×10⁻²⁴` 修正为 `7.8×10⁻¹³`（j = 90）与 `7.7×10⁻¹³`（j = 89）」，旧值作废」；(b) 确定性闸门 `verify.py`（退出码 0）；(c) 账本条目（成果、修正、边界）。硬约束：不重跑大规模计算；报告 250 行以内。〔`plan.md` 第一节。〕

## 二、方法（五条路线 + 收尾复核；行数与 md5 为本记录员实算）

1. **路线 1「逐行逻辑审计」**：把 kcross-proof 四份报告的每一步重写成更细断言串逐条判决。产物 `route-1.md`（205 行，md5 `81938f1e20d228b885985d0b8d61276d`）＋`scripts/audit_lines.py` 与输出。
2. **路线 2「精确解析抽验」**：一律字符串精确解析、禁用 float 中转；抽验端点差、分母结构、窗口两格、`5.55×10⁻²¹` 来源等。产物 `route-2.md`（117 行，md5 `b97256de7b1e440ea8201d148f4ef914`）。
3. **路线 3「定向反例搜索」**：三条见证形态各命中 0（①74 个定点、②71 个定点加一条 A(90) 剪枝引理、③K* 格清单复算无漏项）；副产品为 R 收窄到 (P50, P75]。产物 `route-3.md`（95 行，md5 `2b4d8ac8f5766e81bfcdbe526a39961a`）。
4. **路线 4「确定性闸门与跨库对拍」**：产物 `scripts/verify.py`（425 行，md5 `a1057c5df8af84e754877fc98d40a015`；65 条判据、0 失败、退出码 0；输出 `scripts/results/verify.out`，104 行，md5 `9d4fbacba3d9927045de2247f4f934ad`）。
5. **路线 5「账本条目与引用卫生」**：产物 `ledger-note.md`（162 行，md5 `f2057af61f2c0ad977045c23c3fd56c3`）＋`scripts/cite_check.py`（527 行，md5 `d8a165fafea3b895ce64179dd061dc79`；179 条断言、FAIL 0、退出码 0）＋`scripts/ledger_numbers.py`（178 行，md5 `8cbe4f50454d8c10d4affba37e892d63`；退出码 0）。
6. **收尾复核（裁决）**：自写闸门 `kcross-proof/cycle-1/scripts/verify.py`（450 行，md5 `d7db4e5b9c88abf4b9e5bff2c8c266cb`；57 条判据、FAIL 0；输出 `kcross-proof/cycle-1/scripts/results/verify.out`，127 行，md5 `8be72d19125d2843e0fc1ba666e40fef`）＋深档复算闸门 `verify.py`（1303 行，md5 `1b63c200e178ad0635da98c5a7fd45bd`；92 条判据、FAIL 0、用时 130.4 秒；输出 `results/verify.out`，148 行，md5 `1242cc4374e902ba9e259c2272e1cd84`）＋引用回执复核。
7. **闸门一览**（三个 `verify.py` 互不相同）：57 条判据的是裁决自写闸门（放 `kcross-proof/cycle-1/scripts/`）；65 条判据的是路线 4 产物；92 条判据的是收尾阶段深档复算闸门（含镜像重跑、原地重跑与账本子进程重跑，放 `cycle-1/`）。

## 三、结论

### 增量（四条；全部未形式化、未经第三方复核）

1. **T 的两侧严格区间（证书 A、B），不依赖「T = R」**：绝对宽 `1.161777574454×10⁻¹⁰²`、相对宽 `3.709432774431×10⁻¹²³`；端点精确有理数在 `kcross-proof/cycle-1/scripts/results/r2_threshold_cert.log:57` 与 `:58`，**端点是参数**。裁决实跑（自写 `mpmath` 公式）：A1 的 92 项全部 ε(m₂, T_hi) > γ − δ（最小余量 `1.0759105×10⁻¹⁶³` 在 m₂ = 92）；B2 在 T_lo 的负余量 `−1.1363222×10⁻¹⁶⁴`；K* 格 ε 梯子 m₂ = 83 至 91 与 `k3_run_a.out` 打印串 20 位全串一致 9/9。本记录员独立复算：分母 2³⁸¹ 与 2³⁸²、分子奇数、T_hi < T_lo、宽 = `3·5¹⁸/2³⁸²` = `3·10¹⁸/2⁴⁰⁰`、13 位截断与 60 位截断一致、−log₁₀(相对宽) = 122.4306924951742534。边界：A5 的域闭合（q ≤ 6456，最小余量在 q = 6291、p = 9971）未独立重算。
2. **「T = R」的完整纸面论证、逻辑层未见缺口**（定理 A、B；非降性可删）。条件至少三项：区间引擎 `c2r5_rig` 未形式化、U(92) 的文献常数 `1.4784` 未回一手、Theorem 21 公式与 A(m₂) 勘误链为预印本转述；`kcross-proof/cycle-1/route-1.md:3` 与 `:202` 把条件压缩成一项，不得照抄压缩版。
3. **分岔窗口修正**：j = 90 为 `7.80677136541×10⁻¹³`（`r4b2_window_probe.out:52`）、j = 89 为 `7.71461775858×10⁻¹³`（`:57`）；旧值 `2×10⁻²⁴` 与 `1.5361313×10⁻²³` 都不落入两格（第二版旧值精确等于 `log₂(1+2^−C)/C = 1.5361313786354857241362112574×10⁻²³`）。边界：证的是「存在一个变号点落在该括号内」，不是「窗口右端的宽度」。
4. **K* 格清单记账与不动点机器面、引用卫生**：438／内 0／外 438／未定 0；完整清单 442、被 cap 掉 4 条且差集分母全部 ≥ K*；Ψ(K*) 与 Ψ(q41) 两端夹逼都等于自身（同库复算）；自写佐证 ε_opt(K*) = `8.97322170861713601632572478554×10⁻⁴²`、argmin = 91，q41 格 argmin = 88。

### 否证（七条，全部在引用与证据链层）

1. 路线 1 自报的产物哈希与计数不成立：`scripts/audit_lines.py` 磁盘为 423 行、md5 `f5c8ea5cc907ee4353bc2d373f3e7cc7`，报告 `:9` 与 `:188` 冻结为 391 行、`2e1b0b02…`；`audit_lines.out` 为 72 PASS／0 FAIL，报告 `:186` 称 67 PASS／5 FAIL（rerun.txt 自身确是 67／5）；另有未登记的 `audit_lines_rerun2.txt`。
2. 「v < 3 只有 kc_rig 单库覆盖」被实跑探针否证：v ≈ 0.706 格 k3_rig 即可算（v ≈ 0.353 格 r2_rig 与 k3_rig 分别抛 AssertionError 与 ZeroDivisionError）；路线 4 闸门判据 `5.smallv.gap`（`scripts/verify.py:347`）只在两库同时坏掉时为真。
3. 路线 3 §7「逐字」三行读数不实：`scripts/r3_cross_search.py` 中 `root_sign` 出现 0 次，串 `5.254869241218064` 在 route-3 产物日志中 0 命中（现仅见于两份 `verify.out` 的自检信息行，自指伪影）。
4. `ledger-note.md:40` 与 `route-5.md:62` 的 CONTRAST 句为假：`kcross-proof/cycle-1/route-4.md:192` 实为空行；CONTRAST 断言（`scripts/cite_check.py:412` 至 `:425`）是否定式的，空行天然满足。
5. `kcross-proof/cycle-1/route-4.md:171` 的 `3/X₀ ≈ 5.55×10⁻²¹` 数字错（`3/X₀ = 3.74400750210×10⁻²¹`；`5.55×10⁻²¹` 实为 `240/(54X₀) = 5.54667778×10⁻²¹`）；结论方向不受影响。
6. `kcross-proof/cycle-1/route-4.md:177` 的「已证（严格区间）」在「窗口右端宽度」读法上越界（只证到「存在一个变号点」）；数值影响为零。
7. 路线 2 两处缺陷：`:28` 把 `406·log₁₀2 = 122.21818` 写成「−log₁₀(相对宽)」（真值 122.4306925）；`:33` 把余量出处挂在 `route-1.md:119`（全树 route-1.md 均无此二数；真出处 `plan.md:62` 与 `:79`）。

## 四、复现命令

**说明**：命令 1 为裁决原命令（本记录员未重跑，只核了输出文件与 md5）；命令 2、3 本记录员未重跑（输出已登记）；命令 4、5 本记录员实跑（退出码 0）。命令 1、3 会覆盖各自登记的输出文件，重跑前先备份。

1. 裁决自写闸门（退出码 0，SUMMARY「判据 57 条，FAIL 0 条」）：

```bash
cd "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts" && \
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" verify.py > results/verify.out 2>&1; echo "EXIT=$?"
```

注意：**原地重跑必败于 7.2b**（判据扫到自己输出文件里的针串，自指伪影；登记见 `cycle-1/results/verify.out` 的 1.15a、1.15b）；可复现口径 = 先清空输出文件的镜像重跑。

2. 路线 4 闸门（本记录员实跑等价命令：输出重定向到 /tmp，退出码 0，「判据 65 条，失败 0 条」）：

```bash
cd "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1/scripts" && \
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" verify.py
```

3. 深档复算闸门（92 条判据、FAIL 0、用时 130.4 秒；会同时写入 `cycle-1/results/verify.out`）：

```bash
cd "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1" && \
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" verify.py --deep
```

4. 账本引用与数字复核（本记录员实跑，均退出码 0；脚本只读）：

```bash
cd "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1/scripts" && \
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" cite_check.py     # 末段「共 179 条机器断言；FAIL 0 条」
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" ledger_numbers.py # 末段为量级对照
```

5. 端点恒等式短复核（本记录员实跑，venv python；读数：分母 2³⁸¹ 与 2³⁸² 判 True、宽 = `3·5¹⁸/2³⁸²` 与 `3·10¹⁸/2⁴⁰⁰` 判 True、60 位截断相等判 True）：

```python
from fractions import Fraction as F
from decimal import Decimal, getcontext
import re
getcontext().prec = 120
L = open("…/kcross-proof/cycle-1/scripts/results/r2_threshold_cert.log", encoding="utf-8").read().splitlines()
T = [F(*map(int, re.search(r"=\s*(\d+)/(\d+)\s*$", L[i]).groups())) for i in (56, 57)]
print(T[0].denominator == 2**381, T[1].denominator == 2**382, T[0] < T[1])
print(T[1] - T[0] == F(3 * 5**18, 2**382), T[1] - T[0] == F(3 * 10**18, 2**400))
```

6. 关键哈希抽查：

```bash
md5 -q "…/kcross-tail/cycle-1/ledger-note.md"          # f2057af61f2c0ad977045c23c3fd56c3
md5 -q "…/kcross-proof/cycle-1/scripts/verify.py"      # d7db4e5b9c88abf4b9e5bff2c8c266cb
```

## 五、未决

1. **命名等同「T = R」本身**：条件性纸面已证，前提未形式化、未经第三方复核；账本合并与下游引用的最大悬置点。
2. **三条文献层输入未回一手**：U(92) = `1.4784·92·δ⁹²` 的期刊版、Theorem 21 公式与 A(m₂) 勘误链（预印本转述）、SdW 的 `L = 7.5311×10¹¹`。形式化不在能力内（本机无 Lean、Coq、PARI、Sage）。
3. **窗口完整性未证**：首个（或唯一）变号点未定位，j = 88 的严格区间仍缺（`ledger.md:33` 的 `7.622×10⁻¹³` 出自账本维护会话，不在 kcross-proof 日志里）。
4. **A(90) 均匀化剪枝不等式与 R 的收窄到 (P50, P75]** 未独立复算；后者所依附的 `root_sign` 出处不实。
5. **A5 的域闭合**（q ≤ 6456）未独立重算（只核了日志原样串与位置读数）。
6. **kc_rig 的 v < 3 补丁分支**缺独立对拍（只确认了「哪些库能算」）。
7. **四份报告对 T = R 的登记口径不齐**（route-1 记「已证（条件性）」；route-2、route-3、route-4 记「未裁决／未证」）；合并时需统一为「条件性纸面已证、前提未形式化」。
8. **口径覆盖不全**：`704·2⁶⁰`（arXiv v3）未进入任何数字。

## 六、证据边界（本记录员一手核对清单）

1. **实跑**：`cite_check.py`（退出码 0，179 条断言、FAIL 0）、`ledger_numbers.py`（退出码 0）、路线 4 闸门 `scripts/verify.py`（退出码 0，65 条判据、0 失败、用时 45.17 秒）；三者均只读，运行前后冻结件 md5 不变。
2. **实算**：全部列出的 md5 与行数；端点恒等式（分母 2 的幂、分子奇数、宽的两个恒等式、13 位与 60 位截断、−log₁₀(相对宽) = 122.4306924951742534）；`3/X₀ = 3.74400750210821×10⁻²¹`、`240/(54X₀) = 5.54667778×10⁻²¹`、`406·log₁₀2 = 122.21817823957636`；全树 9 份 route-1.md 无 `3.61`／`1.69` 串。
3. **实读**：`kcross-proof/cycle-1/scripts/results/verify.out` 全文（127 行）；`kcross-tail/cycle-1/results/verify.out` 的 1.15a、1.15b 行；`kcross-proof/cycle-1/route-4.md:171`、`:177`、`:191` 至 `:193`；`cycle-1/ledger-note.md:40`；`cycle-1/route-5.md:62`；`cycle-1/route-2.md:28`、`:33`；`plan.md:62`、`:79`；`cycle-1/methods.md:81`；`r2_threshold_cert.log:52` 至 `:58`、`:64` 至 `:67`、`:76`、`:83` 至 `:93`；`k3_run_a.out:11` 至 `:24`；`kcross-proof/cycle-1/route-1.md:3`、`:79` 至 `:88`、`:113` 至 `:124`、`:149` 至 `:171`、`:202`。
4. **未做**：裁决自写闸门与深档复算闸门未重跑（只核登记输出与 md5）；A1 的 92 项、A5 的 6456 项、B2 负余量、ε 梯子等证书数值**未由本记录员复算**（采信裁决闸门输出与裁决书）；四份报告的数学内容未逐行重审。
