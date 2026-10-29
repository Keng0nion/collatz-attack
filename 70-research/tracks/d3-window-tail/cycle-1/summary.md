# 轨道 d3-window-tail cycle-1 自足摘要（第 1 轮，2026 年 10 月 28 日至 29 日）

**一句话结论**：第 1 轮已闭环，闸门退出码 0。三档窗口（M = 88、89、90）两端严格有理区间证书落地（含补齐 j = 88 遗留），窗口存在集在阈值处全档定号，K*、K_cross（R）与 T 在一切窗口之外（并加强为 K ≥ K_th(91) 时两约定同值），route-5 三处旧错逐位复现并给出更正条目；边界是 M ≤ 24 无窗半边欠单调性证书、窗口内部完整证书只有三档、一切「严格」未形式化未经第三方复核。

**口径**：m = 92、X₀ = 695·2⁶⁰（印出版）、开区间、min_eps 约定；δ = log 3 / log 2，C = log₂((162/97)X₀)；N(m₂,K) = A(m₂) + 3/(2^v − 1) + 3(m₂ − 1)/(2^v − 1)^δ，v = (m₂/92)·K·(δ − 1)/(δ^{m₂} − 1)，A 三段式（m₂ = 92 取 0、91 取 3/X₀、其余取 (97(92 − m₂) + 73)/(54X₀)）；窗口 W_M = {K : argmin ≠ m₂_max}，判据等价于 D_M(K) > 0。科拉茨猜想未被证明也未被推翻；一切「已证」为「初等纸面推理 + 本机实跑证书」意义，未形式化、未经第三方复核。本摘要标「本记录员实算／实跑」的为收尾复核会话一手核对，其余为五路报告与工作流报告的转述。

## 一、疑点

把共享账本 §0.2 第 3 条（两约定分岔窗口）收尾（`plan.md:46` 照录）：(a) 独立复核前一版轨道两条硬否证（C 的 float64 伪值，真值 70.1808063283083668248487894995，伪值低 2.752×10⁻¹⁵；2×10⁻²⁴ 窗口错，真值约 7.6×10⁻¹³，机制漏主导第三项，该第三项在 v = C、m₂ = 90 处为 8.74494110107×10⁻³²，比原两顶残差 1.675×10⁻⁴² 大 10.72 个数量级；以及 convsplit 的「三格逐格核算」查无实据）；(b) 把窗口做成严格区间证书（两端严格有理区间且与独立二分根一致到给定相对宽）；(c) 复核 K* 与 K_cross 是否落在任何窗口内，写成可引用条目；(d) route-5 三处错误的更正条目与更正后窗口值。硬约束：不重跑大规模枚举；报告 ≤ 250 行。

## 二、方法（五路加收尾闸门）

| 路线 | 方法 | 报告（行数，md5） | 关键产物 |
|---|---|---|---|
| 1 | 否证独立重算（自写自足脚本，不 import 被审代码） | `route-1.md` 142 `ea6c77f77a92802774e4cfd6f27cbecd` | `route1_c_recheck.out` 90 `15cd8ce4e4708bbc3639af167a25bdbd`；`route1_window_cert.out` 144 `7a548bb85fa680b6d313cc34dd1ce663`；`route1_convsplit_audit.out` 74 `f3c2c78a7e38a005c82801403f628129` |
| 2 | 证书对抗审计（逐条断言判决：成立 32、有洞 4、措辞过强 5、恒真 2、错误 2） | `route-2.md` 164 `8d18944df9f8c4b130bd113c3dbf6655` | `audit_cert_decimal_full.log` 等（`audit_cert.py` 409 行；`audit_cert_light.py` 421 行） |
| 3 | 新机制区间证书（Stern-Brocot 中位夹逼加认证符号判定器；连分数路径实测只能到约 12 位） | `route-3.md` 148 `7c75a1cb44341c6bde950c881a36f5b8` | `d3r3_windows.json` 68 `80c7c1e1c71693ad18e0c1cf20820041`；`d3r3_conflict.out` 16 `d985094c3314f7f402327823f1f414f9`；`d3r3_diag5.out` 9 `84df28dec4671c91d08a4af357d4d646` |
| 4 | 窗口外覆盖与反例搜索（逐档严格区间判据，替代邻域采样） | `route-4.md` 126 `ad625355b11ab9f5485a907907069fcf` | `d3wt_cert.out` 188 `043a05a3a8d4ab1aa5712f76ac3487d5`；`d3wt_crosscheck.out` 27 `c36ababa68a61ee7a5bb3a30306cc610` |
| 5 | 更正条目与引用卫生 | `route-5.md` 203 `8f76692c4aa0d01e93f80794d2f016c7` | `cycle-1/ledger-note.md` 138 `8efcb197ae32a452797db6f3fe306f21`；`ledger-note-route3.md` 30 `f81b541abcb31ff49db4b661ff760676` |
| 收尾 | 六条增量的自足复算闸门 | `verify.py` 952 `d177446ca98bbd803119b67b29398564` | 本记录员实跑两档均退出码 0（见第四节） |

## 三、结论

### 3.1 增量（六条；全部未形式化、未经第三方复核）

1. **三档窗口两端严格有理区间证书（含 j = 88）**：u* 严格括号（37 位截断，130 步严格二分、未定 0 步）：M = 88 为 `7.622396965265262225804740254338679074×10⁻¹³`、M = 89 为 `7.714617758586982140404811955329781889×10⁻¹³`、M = 90 为 `7.806771365412671715788394707855134401×10⁻¹³`；括号相对宽 9.63849、9.52327、9.41085×10⁻⁴⁰；左端 K_th(M) 区间相对宽 7.23873 至 7.39684×10⁻⁸⁶。Φ 端点重算值：M = 88 为 `+4.08150657813e-43` 与 `−7.19135555824e-43`、M = 89 为 `+1.12641311253e-43` 与 `−4.19606554931e-43`、M = 90 为 `+2.51361056910e-41` 与 `−3.14760815239e-42`。含于 route-3 精确有理端点（K1_88 至 K1_90）与 r4b2 的 48 位括号（M = 89、90）；与 mpmath 独立二分一致（本记录员 `--mpmath` 档复证 δ、C、lnQ 50 位打印逐字一致）。

2. **三条否证逐位复现**：C 伪值差 `2.7521942767886198792327435774876×10⁻¹⁵`（严格区间级）；第三项 `8.74494110107491520289380765652×10⁻³²`、两项残差 `1.67519591503458701469794551289×10⁻⁴²`、比值 `5.2202497765130727096×10¹⁰`、log₁₀ = `10.7176912835`；convsplit 36 行、15「分离？ False」、0「分离？ True」、最细相对步长 10⁻⁴、门槛行 m₂_max = M − 1。

3. **K*、K_cross（R）、T 在一切窗口之外，加强为「K ≥ K_th(91) 两约定同值」**：j = 91、92 半直线上界 `−1.84889259274×10⁻²²` 与 `−1.50222523223×10⁻²¹`；j = 2 至 90 的 D_j(10⁻¹²) 全负（89 档）；c_90(1 + 10⁻¹²) 上界 `1.23124614107679696176×10²⁰` < K*；K_cross 下端 `3.1319547895917226287663653×10²⁰` > c_92 上界 `3.0257813904697416943295316×10²⁰`；T 下界同侧；深档链全 M = 2 至 92 共 4095 步无反例（`--deep` 档，最小步长下界 2.24178176234×10⁻²¹）。R 与 T 分栏，不写「根 = 越界阈值」。

4. **阈值符号全档定号**：正档恰为 [25, 90]（66 档）、负档 [2, 24] ∪ {91, 92}（25 档）、未定 0 档；M = 91、92 无窗已证；M ≤ 24 无窗为数值支持（欠区间证明）。

5. **(d) 更正条目与可引用条目**：`cycle-1/ledger-note.md` 给替换文本与五条禁令解除条件；22 位窗口值、K 侧绝对宽（3.82083513865、6.06028162097、9.61205711792×10⁷）、相对余量 0.67011462625666 均经闸门复算。

6. **数字锚点与多实现互证**：Φ_90(K1_90 下端) 重算 `+2.51361056910×10⁻⁴¹` 落在 `d3r3_conflict.out:3` 区间内；r4b2 两端 Φ = `+7.41066282890×10⁻⁴⁷` 与 `−1.09924404104×10⁻⁴⁶`（与 `d3r3_diag5.out:4`、`:5` 尾数一致）；MPFR 下端 `−4.39167483416×10⁻⁴⁶`（与 `:6` 一致）。

**更正（转述值指数显示层滑落 4 处，闸门警告、尾数一致；引用以重算值为准）**：M = 89 左端应为 `+1.12641311253×10⁻⁴³`（转述误作 ×10⁻⁴²）；M = 90 右端应为 `−3.14760815239×10⁻⁴²`（误作 ×10⁻⁴¹）；r4b2 下端应为 `+7.41066282890×10⁻⁴⁷`（误作 ×10⁻⁴⁶）；r4b2 上端应为 `−1.09924404104×10⁻⁴⁶`（误作 ×10⁻⁴⁵）；另「窄 11 个数量级」按两值应为约 10.2。

### 3.2 否证（要点；全文见 `../ledger-note.md` 第 1 轮条目「四、否证」）

1. route-5 三处错误二次确认（C 伪值、2×10⁻²⁴ 与两项机制、三格逐格核算）；附 log₂(1 + 2⁻ᶜ) 1.5×10⁻²² 真值 1.0780693877885435246959×10⁻²¹（差 7.1871 倍）。
2. `c2r5_convsplit.py` docstring 与 `cycle-1/ledger-note.md:76` 的两项口径窗口宽句不成立（两项口径在门槛处纯两项分子 −2.31430028313121282818×10⁻³³ < 0；交点式宽 log₂(1 + 2⁻ᶜ)/C = 1.53613137863549×10⁻²³）。
3. `d3wt_cert.py:476` 的 R 常数分母 10⁸ 应为 10²⁶（放大 10¹⁸ 倍）；`route-4.md:97` 的差值是错值（正确约 1.9007086485×10²⁰）；「R 不在任何窗口内」结论真但那次运行没证明它。
4. `route-4.md:73` 的 L2 不等式按字面对任意子区间为假（子区间反例：左 −1.090529064×10⁻³¹ > 右 −1.090529062×10⁻²⁹）。
5. `d3r3_mech.py:187` 的 exp 尾界漏掉 k = K 项（漏项 ≤ 约 5.5×10⁻⁵⁵，小于结论余量 10⁻⁴³；数值结论未推翻，形式主张不成立）。
6. route-3 的「唯一冲突」被 `d3r3_diag5.out:7`（本证书下端 Φ = −8.029280e−41）反证；`d3r3_mech.out:61` 的 `+2.5064970301743882×10⁻⁴¹` 与其 `d3r3_conflict.out:3` 不一致；「判定宽度约 10⁻⁵⁰」与实测（约 2.0×10⁻⁴⁷）不符。
7. `route-1.md:84` 的 `3.9033×10¹¹ = 5.0820×10¹⁰ × 7.1871` 为假等式（正解第二因子约 7.6807）；`:130`、`:132` 的「135 行」应为 144 行；`route-3.md:121` 的 jsonchk 行数同型错（29 对 22）。
8. `route-2.md` §六（二）把自家判「不可复原」的截断串标成「严格区间…可直接粘贴」，且「宽度值错 10.7 个数量级」应为 11.59。
9. `cycle-1/ledger-note.md:74` 的「约 9 个数量级」应为 8.11。
10. 「窗口存在 ⟺ M ∈ [25, 90]」的 iff 标签不成立为「已证」（无窗半边欠单调性证书）。

### 3.3 未决（7 条）

1. M ≤ 24 无窗半边欠「(0, 10⁻¹²) 段 D_M 递减」的区间证明（需 |dN(M−1)/dK| / |dN(M)/dK| 递减的区间化）。
2. M ∈ [25, 87] 共 63 档只有阈值符号，无窗口内部完整证书。
3. route-3 自写 MPFR 二分在 M = 90 与四套实现不一致（差 3.0×10⁻²⁷ 相对 K；260 至 520 位不变），其括号两端 Φ 均负（约 −4.49×10⁻⁴⁶ 与 −4.29×10⁻⁴⁶），内部错误未定位。
4. route-1 与 route-2 的窗口端点未发布精确有理数（28 位与 20 位印刷串），10⁻⁴¹ 量级包含关系不可复核；严格包含只对 route-3 JSON 与 r4b2 括号核过。
5. `c2r5_cert.log:9` 的 7.9×10⁻⁹⁹ 区间宽未独立核验（未重跑 `c2r5_rig`）。
6. route-2 的 R 端点残差多精度判定（e(Rlo) = +1.23198928875×10⁻⁸⁸ > 0 > e(Rhi) = −9.20192472296×10⁻⁸⁹）未独立复核。
7. 等级边界：未形式化、未经第三方复核；X₀ = 704·2⁶⁰ 口径未算；「根 = 越界阈值」桥与平台右端推进不在本轮范围。

## 四、复现命令

**本记录员实跑（闸门；两条均退出码 0）**：

1. `cd "70-research/tracks/d3-window-tail/cycle-1" && "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" verify.py`：检查总数 84、失败 0、警告 4、退出码 0（1.7 秒）。
2. 同命令加 `--deep --mpmath`：检查总数 87、失败 0、警告 4、退出码 0（69.5 秒；含 mpmath 50 位打印对照与全档深档链 4095 步）。

**各路自报的复现命令**（本记录员未重跑路线脚本，照录如下；解释器均为 `20-experiments/.venv/bin/python`）：

1. 路线 1：`scripts/route1_c_recheck.py`（退出码 0，输出 90 行）；`scripts/route1_window_cert.py`（退出码 0，输出 144 行）；`scripts/route1_convsplit_audit.py`（退出码 0，输出 74 行）。
2. 路线 2：`scripts/audit_cert.py`（定向 decimal；其 [E] 处因脚本自身类型缺陷中断，[E] 由 `audit_cert_mpmath2.out` 补位）；`scripts/audit_cert_light.py`（自足 Fraction 版）；两段内联 mpmath 写 `audit_cert_mpmath2/3/4.out`。
3. 路线 3（工作目录 `cycle-1/scripts`）：`d3r3_mech.py > results/d3r3_mech.out`；`d3r3_audit.py > results/d3r3_audit.out`；`d3r3_indbisect.py > results/d3r3_indbisect.out`（另跑 `d3r3_indbisect.py 520`）；`d3r3_conflict.py > results/d3r3_conflict.out`；`d3r3_diag5.py > results/d3r3_diag5.out`；`d3r3_jsonchk.py > results/d3r3_jsonchk.out`。
4. 路线 4（工作目录 `cycle-1`）：`python scripts/d3wt_recheck.py > results/d3wt_recheck.out`；`python scripts/d3wt_cert.py`；`python scripts/d3wt_crosscheck.py`（后两者自写输出）。
5. 路线 5：`scripts/d3w_core_selftest.py`（18/18）；`scripts/d3w_r5v_audit.py`（17/17）；`scripts/d3w_window_cert.py`（52/52，约 127 秒）；`scripts/d3w_log2term_check.py`。

## 五、关键文件与 md5（本记录员实算，2026 年 10 月 29 日）

### 5.1 本轨道 cycle-1 报告与闸门

`route-1.md` 142 `ea6c77f77a92802774e4cfd6f27cbecd`；`route-2.md` 164 `8d18944df9f8c4b130bd113c3dbf6655`；`route-3.md` 148 `7c75a1cb44341c6bde950c881a36f5b8`；`route-4.md` 126 `ad625355b11ab9f5485a907907069fcf`；`route-5.md` 203 `8f76692c4aa0d01e93f80794d2f016c7`；`ledger-note.md` 138 `8efcb197ae32a452797db6f3fe306f21`；`ledger-note-route3.md` 30 `f81b541abcb31ff49db4b661ff760676`；`verify.py` 952 `d177446ca98bbd803119b67b29398564`；`methods.md` 78 `5a467c2b3e1f60b6104998714d7a912f`；`materials.md` 458 `13e100830f68e23d212f86321e9468b0`。

### 5.2 脚本

`scripts/route1_c_recheck.py` 390 `e7b69751308d0cca144f1deb73334637`；`scripts/route1_window_cert.py` 487 `03e0717c1babb8244744b21d0e20aa04`；`scripts/route1_convsplit_audit.py` 155 `e7011e951fe04cddbe9a5bdba79cc471`；`scripts/audit_cert.py` 409 `7bd9646a278d4dbe6bbfadcda378099b`；`scripts/audit_cert_light.py` 421 `ac8ae14d0fdef04a73ed0549ea51c910`；`scripts/d3r3_mech.py` 653 `89793bb23a06a9c629f1cf322328ef56`；`scripts/d3r3_audit.py` 159 `968ab27c18f9d5a6f7b4f36afcbec87b`；`scripts/d3r3_indbisect.py` 217 `4ec4b4a67614f6ec29c37137a8a463a0`；`scripts/d3r3_jsonchk.py` 29 `64684a9626212fd3075e4b66566677c4`；`scripts/d3wt_cert.py` 496 `e275d7a07ada69906b18cd7c51d71733`；`scripts/d3wt_recheck.py` 218 `f758c3937c3d993a01626fbb5eb2e827`；`scripts/d3wt_crosscheck.py` 125 `3c3c7108efdbbaa6dcd58d60af699ede`；`scripts/d3w_cert_core.py` 280 `37c113bf926dd382fc8ea0c857e2d84e`；`scripts/d3w_core_selftest.py` 103 `b9e4f3fdb54b0646d76d537c48f7997a`；`scripts/d3w_r5v_audit.py` 150 `f01091938689149b1ef6215a263b3bc9`；`scripts/d3w_window_cert.py` 374 `029c56ec374d8555ad10a5dcd3f48206`；`scripts/d3w_log2term_check.py` 36 `99d684910cacaed1b37e35ce466654ab`。

### 5.3 产物

`scripts/results/route1_c_recheck.out` 90 `15cd8ce4e4708bbc3639af167a25bdbd`；`scripts/results/route1_window_cert.out` 144 `7a548bb85fa680b6d313cc34dd1ce663`；`scripts/results/route1_convsplit_audit.out` 74 `f3c2c78a7e38a005c82801403f628129`；`scripts/results/d3r3_mech.out` 80 `c057fa728376ec8add9f483270d98962`；`scripts/results/d3r3_windows.json` 68 `80c7c1e1c71693ad18e0c1cf20820041`；`scripts/results/d3r3_conflict.out` 16 `d985094c3314f7f402327823f1f414f9`；`scripts/results/d3r3_diag5.out` 9 `84df28dec4671c91d08a4af357d4d646`；`scripts/results/d3r3_audit.out` 61 `75c74ef61cb3a982a3526730d441cff5`；`scripts/results/d3r3_indbisect.out` 18 `7667c92f87a1aeef7ec521afa1ea7f9a`；`scripts/results/d3r3_jsonchk.out` 22 `1391067c514545ca9502cd0fabd107aa`；`scripts/results/d3w_core_selftest.out` 27 `93b7fa1f12f2e794db909e1eac741147`；`scripts/results/d3w_r5v_audit.out` 51 `20c6d1e830bff2d6c983ea02f3f1eb1d`；`scripts/results/d3w_window_cert.out` 132 `1347814ed8c7b0feb951d35cf619d6f9`；`scripts/results/d3w_log2term_check.out` 7 `2df634819e52d2ff6241be6331da4f4a`；`results/d3wt_cert.out` 188 `043a05a3a8d4ab1aa5712f76ac3487d5`；`results/d3wt_recheck.out` 57 `e55a2bb140da9c1a7d0aae83f9398a1e`；`results/d3wt_crosscheck.out` 27 `c36ababa68a61ee7a5bb3a30306cc610`。

### 5.4 关键外部

`70-research/ledger.md` 239 `27addb5bea8db65893333de96a68ee13`；`70-research/learnings.md` 107 `08345669c2f061650aabfa7d08311d6b`；`cycle-2/route-5.md` 442 `fb9a00e852c9a05b1ebdcb63f57fedf1`；`cycle-2/scripts/results/c2r5_convsplit.out` 36 `39f60fa65a6859f1bd084b5b8beaf38e`；`cycle-2/scripts/results/c2r5_cert.log` 89 `9e827cd1ebfdff89825c14616a3c0e62`；`tracks/kcross-proof/cycle-1/scripts/results/r4b2_window_probe.out` 77 `a078e3e631f07858f4b607968403a3c2`；`tracks/kcross-tail/cycle-1/ledger-note.md` 162 `f2057af61f2c0ad977045c23c3fd56c3`。

## 六、未跑与边界（诚实登记）

1. 本记录员**未重跑五路脚本**（只跑了第 1 轮自带的 `verify.py` 两档与只读核对）；五路数字按各路报告与产物转述，其中五路报告自身的硬伤见 `../ledger-note.md` 第 1 轮条目「四、否证」。
2. 本轮一切「严格」等级 = 「自写定点核心 + 本轮实跑」，未形式化、未经第三方复核（本机未重跑证明助手检查）。
3. 未做：M ≤ 24 无窗的区间证明；M ∈ [25, 87] 的窗口内部证书；X₀ = 704·2⁶⁰ 口径；「根 = 越界阈值」桥；平台右端推进；`c2r5_rig` 重跑。
4. 写入纪律：本轮新增文件只有本摘要、`../ledger-note.md`、`../learnings-note.md` 三件；未就地覆盖任何旧证据；未改共享 `ledger.md` 与 `learnings.md`。
