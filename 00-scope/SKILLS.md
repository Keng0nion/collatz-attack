# 技能盘点与科拉茨攻坚适用性评估

盘点日期：2026 年 10 月 17 日。执行者：技能侦察员（本工作流的子代理）。

阅读约定：每条结论都注明可信度来源。「本次实测」表示我在本轮亲手运行过命令并看到输出；「来源自述」表示摘自技能或插件的自带文档，我未独立验证；「我的推断」表示由实测数据推出的判断；「无法核实」表示我尝试过但没有拿到证据。本次没有执行任何安装命令，没有改动任何技能目录。

## 一、盘点范围与方法

1. 已装技能数量（本次实测，逐个数目录）：

   | 根目录 | 目录数 | 两层内有 SKILL.md 的条目数 |
   | --- | --- | --- |
   | `/Users/luna/.zcode/skills` | 197 | 138 |
   | `/Users/luna/.agents/skills` | 97 | 95 |
   | `/Users/luna/.claude/skills` | 53 | 未逐条统计 |

   另有本会话 Skill 工具列表中带插件命名空间的条目（如 `visualize:visualize`、`pdf:pdf`、`documents:docx`）。

2. 关键词检索（本次实测）：对上述三个根目录做两类大小写不敏感检索，完整命令见第五节。一是全文检索，模式含 sympy、z3、theorem prover、proof assistant、lean 4、coq、isabelle、数论、定理证明、形式化；二是技能名检索，模式含 math、number、proof、lean、coq、theorem、symbolic、sage、pari、latex、tex、research、paper、arxiv。结果：全文检索无一条真实命中，唯二命中点位于 `ffmpeg-skill` 下的 `.gif` 与 `.pyc` 二进制文件，属误报；技能名检索的命中项全部为词形巧合（texture、statusline、message 等）。

   结论：本机已装技能里没有任何一条涉及形式化证明、数论或符号计算。

3. 官方插件市场清点（本次实测）：读 `/Users/luna/.zcode/cli/plugins/known_marketplaces.json`，本机注册了两个市场：`zcode-plugins-official` 与 `claude-plugins-official`。解析各自的 marketplace.json 得到插件条目 49 条与 295 条。注：known_marketplaces.json 把前者记为 48 条，与解析结果差 1，此处以解析结果为准并标出这一出入。

   全市场里分类为 math 的条目只有一条：`math-olympiad`。没有任何条目以 lean、proof、theorem、sympy、formal 命名。

4. 本机工具链与库：全部实跑实测，命令与输出见第五节。

## 二、四类相关条目逐条评估

### 2.1 形式化证明类

结论：已装技能零条；本机工具链也是零。

1. 本次实测，以下命令全部 NOT FOUND：`lean`、`lake`、`elan`、`coq`、`coqc`、`isabelle`、`agda`、`idris2`、`sage`、`gp`（PARI）、`magma`。这与 `collatz-attack/README.md:23` 与 `collatz-attack/workflow.ts:689`（Lean 写手的系统提示）的预设一致：Lean 源码只能写、不能编译，必须在文件里如实声明未经编译器检验。
2. 由此得出一条硬结论：在装上 Lean 或 Coq 工具链之前，任何形式化证明类技能在本机都没有落地方式。这条不会因为安装技能而改变。
3. 官方市场唯一沾边的条目 `math-olympiad` 不提供形式化能力：它把验证者规定为纯推理、无工具（`skills/math-olympiad/SKILL.md:34` 起的工具政策）。详见第三节。
4. 第三方候选见第四节，只报来源，未安装。

### 2.2 数论类

结论：已装技能零条；数论能力全部来自库，且本次实测确认够用。

1. 项目自带环境 `/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python`（解释器报头为 Python 3.12.7，packaged by Anaconda）实测可用，关键能力逐条核实：

   1. sympy 1.14.0：`factorint(2^30 减 1)` 返回 `{3: 2, 7: 1, 11: 1, 31: 1, 151: 1, 331: 1}`；`integer_nthroot(3^100, 100)` 返回 `(3, True)`；`Matrix.lll()` 可用，在测试格上返回首行 `Matrix([[-1, -5, 4, 0]])`。
   2. python-flint 0.9.0：`fmpz_mat.lll()` 可用（注意它返回新矩阵，不是原地修改），同一测试格首行与 sympy 一致。也就是说 LLL 在本机有两个独立实现，可直接服务 `problem.md:24`（成功标准第 3 条：关键数字由另一套方法独立重算）。
   3. gmpy2 2.3.2：`2^1000` 的十进制为 302 位，与 flint 的整数结果一致。
   4. z3-solver 5.3.1.0（`z3.get_version_string()` 报 5.3.1）：一次有界环搜索（把加速映射展开 3 步、限定 2 到 10^6）返回 `unsat`。

2. 诚实标注：上一条里 z3 的结果只是「求解器能跑」的能力探针，它是有界、固定步数的搜索，不构成任何关于「不存在非平凡环」的结论。`workflow.ts:260` 至 `262` 的证书搜索实验写法正确，前提是结论必须按它自己要求的那样写成「该形式在该截断上不存在证书，这否证什么、不否证什么」。
3. 与 `workflow.ts:302` 的核对：那条丢番图路线假定「sympy 有 lll 可用」。该假定经本次实测成立，并另有 flint 第二实现。
4. 相关但非数论的已装技能：
   1. `find-skills`、`skill-installer`：能装技能，但 `skill-installer` 支持从任意 GitHub 仓库路径安装，这条通道正属于本任务禁止的第三方来源。本项目内不得用它安装任何数学技能。
   2. `systematic-debugging`、`test-driven-development`、`writing-plans`、`brainstorming`：工程纪律类，对写实验脚本（先写会失败的检查、直接寻找最小反例）与多步任务拆解有辅助价值。

### 2.3 数学计算类

结论：已装技能零条；计算地基已由 venv 实测站住。

1. 本次实测（探针脚本 `/tmp/skill_probe.py`，运行命令见第五节），关键输出：

   ```
   verified n<=1e6 all reach 1 : ALLOK
   max accelerated steps: 330 at n = 837799 | wall = 0.56s
   ```

   这条直接服务 `problem.md:23`（成功标准第 2 条：有明确范围的全量验证）。加速映射下 10^6 全量耗时 0.56 秒。

2. 我的推断（有上述实测支撑）：按此速度外推，`workflow.ts:237` 给扫掠实验定的目标上限 2^28 在本机是现实目标，粗估在数分钟量级；换用 `cc -O3`（本机 `cc` 实测为 Apple clang 21.0.0）会更快。这是粗估，不是实测，最终以实验执行者的运行数据为准。
3. 系统 python3（`/opt/anaconda3/bin/python3`，3.12.7）实测可用库：sympy 1.13.1、numpy 1.26.4、mpmath 1.3.0、networkx 3.3、matplotlib 3.9.2、pandas 2.2.2、scipy 1.13.1、sklearn 1.5.1、statsmodels 0.14.2、plotly 5.24.1。缺失：z3、gmpy2、flint、pysat、sage。因此实验一律应走项目 venv（与 `README.md:32` 的复现约定一致），只有画图可以借系统 python。
4. venv 完整包清单（`pip list` 实测，共 7 项）：gmpy2 2.3.2、mpmath 1.3.0、numpy 2.5.4、pip 26.2.1、python-flint 0.9.0、sympy 1.14.0、z3-solver 5.3.1.0。注意其中没有 matplotlib。

### 2.4 可视化与交付类

结论：已装条目覆盖充分，不需要新安装。

1. `visualize`（官方插件 0.1.0，缓存路径实测存在：`/Users/luna/.zcode/cli/plugins/cache/zcode-plugins-official/visualize/0.1.0/skills/visualize/SKILL.md`）：对话内交互图表与解释页，自带 D3 与组件样式，产物是单个 HTML 片段。适合停时分布、逆向树增长曲线这类需要悬停或拖拽的中期展示。
2. `documents:docx`、`pdf:pdf`、`presentations:pptx`、`spreadsheets:xlsx`（均 0.1.8，官方插件，缓存路径实测存在）：成品交付用。主张台账做成 XLSX 最贴合 `problem.md:23` 至 `26` 对可复核性的要求。
3. LaTeX：本次实测 `pdflatex` 与 `xelatex` 都存在于 `/Library/TeX/texbin`。总报告若要走 LaTeX 出 PDF，本机具备条件；`math-olympiad` 的 `scripts/check_latex.sh` 判据正是「存在 pdflatex 或 xelatex」，据此会返回 0（我读的是该脚本的判据本身，脚本未实际运行）。
4. 注意不要混用：`workflow.ts:850` 要求的 `frontier-map.html` 是单文件、无外部依赖、离线可开的交付页面，与 `visualize` 的对话内片段规格不同，后者不能当交付页面用。

## 三、官方市场唯一值得考虑的候选：math-olympiad

来源与状态：位于 `claude-plugins-official` 市场，分类 math，作者 Anthropic，源为 `./plugins/math-olympiad`，主页 https://github.com/anthropics/claude-plugins-official/tree/main/plugins/math-olympiad 。本地已随市场检出：`/Users/luna/.zcode/cli/plugins/marketplaces/claude-plugins-official/plugins/math-olympiad/`。当前未安装（`installed_plugins.json` 里只有 github、video2code、canva、desktop-commander、carbone-skill、mimosa 六条）。

它是什么（我逐文件读过 SKILL.md、README.md 与四份 references）：面向竞赛数学（IMO、Putnam、USAMO、AIME）的求解与对抗式验证工作流。核心不是算力，是反驳方法论：

1. 双上下文隔离：验证者只看清洗后的证明，看不到解题者的思维链；各验证者之间也互相不知道彼此结论（`SKILL.md:142` 起、`SKILL.md:203` 至 `208`）。
2. 13 条反驳模式（`references/verifier_patterns.md`）。其中 Pattern 4「这套论证会不会顺手证明了一个著名开放问题」把 Collatz 映射直接列为三大著名硬实例之一（该文件第 16 行）；Pattern 18 抓同义反复（第 88 行起）；Pattern 17 抓「只验证到第一个非平凡块」（第 72 行起）；Pattern 40 抓「过短的一行引理」（第 162 行起）。注：该文件自述收录 13 条免计算模式（第 5 行起），而 `SKILL.md:385` 把它写作「12 条」，两处数字不一致，属插件自身的小瑕疵，此处以实际列出的 13 条为准。
3. 七类反驳分类（`references/adversarial_prompts.md:17` 起）：步骤不成立、假设未满足、小情形为假、同义反复、证明过度、解读错误、关键处含糊。每一类都配了可直接复用的验证者提示词模板（同文件第 43、80、114、152、188、225、259 行各节）。
4. 非对称投票（4 票维持才算通过，2 票推翻即否决）与鸽巢提前退出（`SKILL.md:187` 至 `206`）；校准弃权：宁可写「没有可信的解答」，也不硬凑（`SKILL.md:325` 至 `340`）。
5. 呈现环节：验证通过后才做排版，可调 LaTeX 编译出 PDF（`scripts/compile_pdf.sh`、`scripts/check_latex.sh`）。

与本项目的契合点（我的判断，依据是上述文件内容与 `00-scope/problem.md`）：

1. `problem.md:25` 要求每条路线逐步骤标注「已证 / 缺口 / 错误 / 等价于原命题」并经受独立反驳。其中「等价于原命题」正对应 Pattern 18，「已证」的核查正对应 Pattern 5 与 Pattern 10。`workflow.ts:557` 至 `599` 的路线尝试、独立反驳、作者回应三段结构，与这个技能的工作流同构。
2. `problem.md:26`（不夸大）与这个技能的校准弃权是同一件事的两种写法。
3. `workflow.ts:574` 至 `592` 的反驳者提示词可以直接接上 `adversarial_prompts.md` 的模板骨架，尤其是第 259 行的对抗式任务书模板，天然适合「缺口不可修」与「局部存活」两种分流。

必须写清的局限：

1. 技能面向竞赛题，不面向研究级开放问题。它把「开放探索、文献检索、查既有解法、多日调查」明确划给另一个工作流，而那个叫 `math-research` 的工作流在两个官方市场里都不存在（我在 295 条与 49 条清单里全文检索过，`math-research` 只在 math-olympiad 自己的 `SKILL.md:283` 出现一次）。本项目八条文献线的检索与引文核对不能靠它。
2. 它的验证者被规定为无工具、纯推理（`SKILL.md:34` 起、`adversarial_prompts.md:6` 至 `9`），不会跑代码找反例；而 `workflow.ts:584` 至 `591` 要求反驳者交出「实际运行过的反例命令与输出」。两者互补，不能互相替代。
3. 技能自报的成绩（`README.md:23`：「17/18 IMO 与 Putnam 2025 题解出，0 假阳性，2 个新证明」）我无法核实，它指向 anthropics 私有分支下的一个路径。其引用的 arXiv:2503.21934 我核实存在且标题相符（Proof or Bluff? Evaluating LLMs on 2025 USA Math Olympiad），但 `README.md:8` 至 `9` 里「85.7% 掉到 5% 以下」的具体数字我没有核对正文，属来源自述、待核实。
4. 它的模式库是攻击清单，不是定理。当检查表用有价值，当正确性保证用没有价值。

建议的最小成本用法：不改变机器状态也可以受益。让本项目工作流里的反驳者、首席反驳者与路线裁决员直接读这两份文件（`references/verifier_patterns.md` 与 `references/adversarial_prompts.md`，绝对路径见上），把七类分类与 13 条模式当攻击清单逐条过。

安装与否的建议：交给用户决定，理由有两条。其一，`README.md:30` 给的安装命令 `/plugin install math-olympiad@claude-plugins-official` 是 Claude Code 语法；本机 PATH 上没有 zcode 可执行文件（`command -v zcode` 未找到），所以 zcode 下的确切安装语法我无法核实，不应臆造。其二，本次工作流并不依赖安装：参考文件已在本机磁盘上，读文件即可用。本次没有执行任何安装命令。

## 四、第三方候选（仅报告来源，未安装、未下载）

以下三条都属于第三方来源，按纪律只报候选与来源，绝不安装。它们的共同前提是本机没有的 Lean 4 工具链与 Mathlib，所以即便将来要用，也必须先解决工具链；而本工作的预设是不安装全局形式化工具链（`README.md:23` 与 `workflow.ts:689` 均如此声明）。

1. `lean-lsp-mcp`（作者 oOo0oOo）：Lean 4 的 MCP 服务器，通过 LSP 提供诊断、目标状态与悬停文档，并接入 LeanSearch、Loogle、Lean Finder 等检索；随附「Lean 4 Theorem Proving」代理技能。来源：https://github.com/oOo0oOo/lean-lsp-mcp 与 https://pypi.org/project/lean-lsp-mcp/ 。
2. `cameronfreer/lean4-skills`：Lean 4 证明技能，自述与 lean-lsp-mcp 配合最佳（实时目标检查、mathlib 检索）。来源：https://github.com/cameronfreer/lean4-skills 。
3. `lean-mcp`（PyPI）：把 Lean 4 编译器包成 MCP 工具（verify_lean_theorem）。来源：https://pypi.org/project/lean-mcp/ 。

核验程度说明：以上三条来自本次网页检索（DuckDuckGo），我读的是检索结果与摘要页，没有打开仓库逐行审阅源码，也没有下载任何文件。列入本文仅作候选线索，可信度标为未核实。

## 五、本次实际运行的命令与关键输出

以下命令均在 2026 年 10 月 17 日本轮运行，输出为原样摘录。

1. 技能清单与关键词检索：

   ```bash
   ls -1 /Users/luna/.zcode/skills | wc -l                       # 197
   ls -1 /Users/luna/.agents/skills | wc -l                      # 97
   ls -1 /Users/luna/.claude/skills | wc -l                      # 53
   find /Users/luna/.zcode/skills -maxdepth 2 -name SKILL.md | wc -l   # 138
   find /Users/luna/.agents/skills -maxdepth 2 -name SKILL.md | wc -l  # 95
   grep -rliE "sympy|z3 |theorem prover|proof assistant|lean 4|coq |isabelle|数论|定理证明|形式化" \
     /Users/luna/.zcode/skills /Users/luna/.agents/skills /Users/luna/.claude/skills
   # 仅命中 ffmpeg-skill 下的 .gif 与 .pyc，判为误报
   ls -1 /Users/luna/.zcode/skills /Users/luna/.agents/skills /Users/luna/.claude/skills \
     | grep -iE "math|number|proof|lean|coq|theorem|symbolic|sage|pari|latex|tex|research|paper|arxiv" | sort -u
   # 命中项：bs-texture-workflow、opencli-usage、scenario-blender-texturing-shading、
   #         statusline、texture-workflow、wechat-background-message（全部为词形巧合）
   ```

2. 官方市场解析：

   ```bash
   python3 -c "import json; d=json.load(open('.../zcode-plugins-official/marketplace.json')); print(len(d['plugins']))"   # 49
   python3 -c "import json; d=json.load(open('.../claude-plugins-official/marketplace.json')); print(len(d['plugins']))"   # 295
   # 分类统计中 math 类仅 1 条：math-olympiad
   ```

3. 项目 venv 能力探针（脚本 `/tmp/skill_probe.py`，用 Write 工具写入后运行）：

   ```bash
   "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" /tmp/skill_probe.py
   ```

   输出：

   ```
   sympy: 1.14.0 | z3: 5.3.1 | gmpy2: 2.3.2
   verified n<=1e6 all reach 1 : ALLOK
   max accelerated steps: 330 at n = 837799 | wall = 0.56s
   z3 bounded-cycle k=3 : unsat
   sympy factorint(2**30 - 1): {3: 2, 7: 1, 11: 1, 31: 1, 151: 1, 331: 1}
   gmpy2 2**1000 digits: 302 | flint fmpz matches: True
   ```

4. LLL 探针（脚本 `/tmp/skill_probe2.py` 与 `/tmp/skill_probe3.py`）：

   ```bash
   sympy Matrix.lll: OK, first row = Matrix([[-1, -5, 4, 0]])
   flint fmpz_mat.lll (returns new matrix): OK   # 首行 -1 -5 4 0
   ```

   说明：第一次调用 flint 的 LLL 时我切片写法有误报过 TypeError，第二次按返回新矩阵的接口重测通过。这里记下过程，免得后来者误以为 flint 不可用。

5. 工具链与解释器核查：

   ```bash
   for b in lean lake elan coq coqc isabelle agda idris2 sage gp magma; do command -v $b || echo "NOT FOUND"; done   # 全部 NOT FOUND
   command -v pdflatex xelatex       # /Library/TeX/texbin/pdflatex 与 /Library/TeX/texbin/xelatex
   command -v cc clang gcc           # 均为 Apple clang version 21.0.0
   command -v zcode                  # 未找到
   command -v opencli                # /opt/homebrew/bin/opencli
   "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" -m pip list
   ```

6. 临时产物：`/tmp/skill_probe.py`、`/tmp/skill_probe2.py`、`/tmp/skill_probe3.py` 为可删的探针脚本。本文件是本次唯一的持久写入。

## 六、结论

1. 不需要安装任何新技能。四类需求逐条对上：形式化证明因本机没有 Lean、Coq、Isabelle 工具链而根本无法落地，装技能不解决问题；数论与数学计算由项目自带 venv 实测够用（sympy、z3、gmpy2、flint 全部可用，10^6 全量验证 0.56 秒，LLL 有两个独立实现可供交叉验证）；可视化与成品交付由已装的 `visualize`、`documents`、`pdf`、`presentations`、`spreadsheets` 覆盖，LaTeX 工具链也齐。
2. 若只挑一条官方市场条目考虑，是 `math-olympiad`。它的价值在反驳方法论：13 条反驳模式、七类反驳分类、非对称投票、校准弃权，与 `problem.md:25` 至 `26` 的「精确失败点、独立反驳、不夸大」逐条对应。但它面向竞赛数学、验证者不跑代码，自报成绩无法核实，且其引用的 `math-research` 工作流并不存在。最小成本用法是当阅读材料（路径见第三节），不安装。
3. 名称澄清：任务书写到的「Leet」在本机没有对应物（技能名、命令名、目录名三处检索均无）。若它指的是 Lean，结论同第 1 条：工具链未装，装技能无用。
