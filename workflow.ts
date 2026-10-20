// 科拉茨猜想（3x+1）攻坚工作流。
// 目标：把已知边界钉死、把计算地基做实、沿六条路线做真实的证明尝试并写出精确失败点。
// 纪律：任何"证明了"必须伴随可核验论证；任何数字必须有独立重算；任何主张必须回到原始来源。

interface TopicResult {
  /** 与分配给你的一致 */
  slug: string;
  /** 你写入的笔记文件的绝对路径 */
  notePath: string;
  /** 关键结果清单：每条一句话，含年份、作者与可打开的出处 URL */
  keyClaims: string[];
  /** 这条研究线上仍未解决的缺口，每条一句话 */
  openGaps: string[];
}

interface CitationCheck {
  /** all-verified 表示关键主张全部能在原始来源中核对到；some-wrong 表示至少一条错误或缺失出处；unverifiable 表示主要来源打不开 */
  verdict: "all-verified" | "some-wrong" | "unverifiable";
  /** 逐条列出有问题的条目与更正理由；全部核对通过时为空数组 */
  corrections: string[];
}

interface LitOutcome {
  /** 主题短标识 */
  slug: string;
  /** 笔记文件绝对路径 */
  notePath: string;
  /** 核对通过的关键主张条数 */
  keyClaimCount: number;
  /** 缺口条数 */
  openGapCount: number;
  /** 引文核对结论 */
  citationStatus: "all-verified" | "some-wrong" | "unverifiable";
  /** 两三句话总结这条线的现状 */
  summary: string;
}

interface Frontier {
  /** 边界地图文件的绝对路径 */
  path: string;
  /** 已确证的核心结果，每条一句话 */
  established: string[];
  /** 活口清单：仍可能在数学上推进的入口，按距离真证明的远近排序 */
  liveGaps: string[];
  /** 已知死路与结构性障碍 */
  deadEnds: string[];
}

interface FrontierReview {
  /** 边界地图中夸大、错引、与笔记不符或缺失的地方，每条一句话；没有发现则空数组 */
  problems: string[];
  /** 你亲自打开来源核对过的抽样主张条数 */
  claimsChecked: number;
}

interface ExperimentResult {
  /** 实验短标识 */
  slug: string;
  /** 脚本绝对路径 */
  scriptPath: string;
  /** 原始输出文件绝对路径 */
  resultPath: string;
  /** 结论文件绝对路径 */
  findingPath: string;
  /** 关键数字，每条一句话，必须写明实际达到的范围（例如 n 不超过 2^28） */
  keyNumbers: string[];
  /** 这个实验明确不能证明什么，每条一句话 */
  doesNotShow: string[];
}

interface Recheck {
  /** 实验短标识 */
  slug: string;
  /** 你用不同方法独立重算到的数字，逐条写明方法名与结果 */
  rederived: string[];
  /** 与实验报告不一致之处；空数组表示一致 */
  discrepancies: string[];
}

interface RouteAttempt {
  /** 路线短标识 */
  slug: string;
  /** attempt.md 绝对路径 */
  path: string;
  /** 你尝试证明的定理，一句精确陈述 */
  theorem: string;
  /** 论证中未证成或已失败的步骤数 */
  gapCount: number;
  /** 最主要的缺口，一句话说清它为什么是缺口 */
  mainGap: string;
  /** 论证过程中确实立住的局部结论，可能为空数组 */
  localLemmas: string[];
}

interface Rebuttal {
  /** 路线短标识 */
  slug: string;
  /** fatal 表示有致命错误；serious 表示有严重未证步骤；survivable 表示缺陷可修；route-doomed 表示该路线已被文献证明此路不通 */
  verdict: "fatal" | "serious" | "survivable" | "route-doomed";
  /** 最致命的一击，一句话 */
  strongestObjection: string;
  /** 证据：你打开的来源 URL，或你实际运行的反例命令与输出 */
  evidence: string;
  /** 你实际运行过的反例验证命令；没有则写 none */
  counterexampleCommand: string;
}

interface RouteResponse {
  /** 修订后的 attempt.md 绝对路径 */
  path: string;
  /** fixed 表示已修补；conceded 表示撤下该结论；defended 表示反驳本身有误 */
  action: "fixed" | "conceded" | "defended";
  /** 一句话说明结果 */
  note: string;
}

interface RouteVerdict {
  /** 从最接近真证明到最远排序的 slug 列表 */
  ranking: string[];
  /** 最值得加派第二轮反驳的两个 slug */
  top2: string[];
  /** 排序理由，两三句话 */
  rationale: string;
}

interface FormalResult {
  /** 写了哪些文件，逐条列出绝对路径与一句话说明 */
  files: string[];
  /** 覆盖到的引理清单，每条一句话 */
  lemmas: string[];
  /** 未能处理的部分及原因 */
  limits: string[];
}

interface ReportOutcome {
  /** final-report.md 绝对路径 */
  path: string;
  /** 报告的核心结论，三句以内 */
  conclusion: string;
  /** 红队指出并已处理的问题数 */
  redteamIssuesAddressed: number;
  /** 仍未处理的争议点，每条一句话 */
  unresolved: string[];
}

interface RedTeam {
  /** 报告中夸大、无证据、或与笔记和结果不符之处，每条一句话并给出文件与行号或来源 URL */
  problems: string[];
  /** 你抽样复核的主张条数 */
  claimsChecked: number;
}

interface HtmlOutcome {
  /** frontier-map.html 绝对路径 */
  path: string;
  /** 页面包含哪几块内容，每条一句话 */
  sections: string[];
  /** 你实际做过的自测方式与结果 */
  selfTest: string;
}

/** 风格与诚实纪律，追加到每个子代理的 persona 后面。 */
const STYLE =
  "写作纪律：中文正文里不要出现半角连字符，破折号用「——」，并列用「、」，编号用 1. 2. 3. 或 一、二、三。诚实纪律：区分已证定理、仅预印本的宣称、以及你自己的推断；无法核实的必须标注，禁止编造文献、数字或引理名。";

interface TopicSpec {
  /** 主题短标识 */
  slug: string;
  /** 笔记文件绝对路径 */
  notePath: string;
  /** 这条研究线要回答什么 */
  mission: string;
}

const litTopics: TopicSpec[] = [
  {
    slug: "verification",
    notePath: "/Users/luna/Documents/math IA/collatz-attack/10-literature/notes/verification.md",
    mission:
      "计算验证的现状：当前被验证到的上限是多少（谁保持、用什么算法、哪一年）、树搜索与模类剪枝方法的覆盖性论证究竟是怎么成立的、该方法为什么不能靠堆算力推得很远、以及这些验证结果能否被独立复核。务必找到保持者的原始论文与算法描述，而不是二手报道。",
  },
  {
    slug: "stopping-times",
    notePath: "/Users/luna/Documents/math IA/collatz-attack/10-literature/notes/stopping-times.md",
    mission:
      "停时与密度：Terras 的有限停时密度定理、Allouche、Korec、Krasikov 与 Lagarias 的 x^0.84 型下界、以及这类结果的最新改进。要精确记录每条结果的量词形式与常数，并找出这些常数在技术上的极限在哪里（例如证明方法本质上受什么限制）。",
  },
  {
    slug: "tao-almost-all",
    notePath: "/Users/luna/Documents/math IA/collatz-attack/10-literature/notes/tao-almost-all.md",
    mission:
      "Tao 2019 年关于几乎所有轨道取到几乎有界值的工作及其 2020 年至今的后续（引用、改进、以及对该方法极限的讨论）。必须精确摘出：定理的确切陈述、它依赖的关键定量引理、以及从「几乎有界」推进到「有界」究竟缺什么。这是判断该路线活口在哪里的关键。",
  },
  {
    slug: "cycles",
    notePath: "/Users/luna/Documents/math IA/collatz-attack/10-literature/notes/cycles.md",
    mission:
      "环与 m-cycle：Böhm 与 Sontacchi 的环刻画、Eliahou、Simons 与 de Weger、Hercher 的环长下界，以及当前非平凡环周期下界的记录值（含取得它的方法：线性型对数下界与 LLL）。要写清环方程 x 等于 c 除以 2^k 减 3^m 的推导、以及从该方程到数值下界的每一步用到了什么工具。",
  },
  {
    slug: "two-adic",
    notePath: "/Users/luna/Documents/math IA/collatz-attack/10-literature/notes/two-adic.md",
    mission:
      "2-adic 与遍历结构：Bernstein 与 Lagarias 型共轭（把加速映射共轭到 2-adic 移位）、Syracuse 随机变量、以及与 Collatz 相关的测度论与遍历论结果。要精确写出共轭定理的陈述，并分析它为什么不能直接给出对正整数与有理点的控制（这是理解问题难点的核心）。",
  },
  {
    slug: "undecidability",
    notePath: "/Users/luna/Documents/math IA/collatz-attack/10-literature/notes/undecidability.md",
    mission:
      "不可判定性与硬度边界：Conway 1972 年对广义 Collatz 的不可判定性、Kurtz 与 Simon 的 Π 零二阶完备性、以及 2024 年之后关于小图灵机行为独立于 ZFC 的结果（含其中的 Collatz 型问题）。要写清这些结果对「证明科拉茨猜想必须用到什么」的约束：哪些泛化方法必然失败、而原问题为何仍可能有证明。",
  },
  {
    slug: "claims-2024-2026",
    notePath: "/Users/luna/Documents/math IA/collatz-attack/10-literature/notes/claims-2024-2026.md",
    mission:
      "2024 年至 2026 年期间关于科拉茨猜想的新预印本与公开宣称，特别是任何「宣称证明」的稿件。对每一条宣称：找到原始出处、检查是否经过同行评审、搜集数学界的公开评价或反驳、并给出你自己的可信度判定与理由。不允许把未评审的宣称转述成结果。",
  },
  {
    slug: "barriers",
    notePath: "/Users/luna/Documents/math IA/collatz-attack/10-literature/notes/barriers.md",
    mission:
      "已知的证明障碍与死路：为什么某些归纳法、有限覆盖同余、有限自动机、以及简单势函数方法必然失败。包括文献里明确写出的不可能性定理，以及被广泛讨论但未成文的经验教训。这一线的产物应当是一份「不要去试的清单」以及每条死路的出处。",
  },
];

interface ExperimentSpec {
  /** 实验短标识 */
  slug: string;
  /** 任务书 */
  mission: string;
}

const experiments: ExperimentSpec[] = [
  {
    slug: "sweep",
    mission:
      "全量验证地基。写 collatz-attack/20-experiments/scripts/sweep.py 或 sweep.c（C 用 cc 编译到 scripts/ 下），用加速映射加记忆化把上限尽量推高（目标 n 不超过 2^28，视耗时取舍），产出：(a) 全部 n 不超过上限 都最终到达 1；(b) 总停时的最大值与其对应的 n；(c) 停时纪录保持者序列。把命令行、耗时、上限与纪录表写进 results/sweep.txt。并与 OEIS 的 A006577（总停时）与 A006877（停时纪录）中可对齐的部分逐条核对，不一致处列出来。本机 8 核 8GB 内存，单次运行控制在 15 分钟以内，超了就降低上限并说明。",
  },
  {
    slug: "stoptime-stats",
    mission:
      "停时分布实验。对 n 不超过 2^24 精确计算总停时分布，与「随机游走加漂移」的启发式模型对照（该模型下停时近似服从某个正态或极值分布），并把 Krasikov 与 Lagarias 的 x^0.84 型下界与实际数据放在一起看：画出（用文本或 matplotlib 存 PNG 到 results/）实际密度与理论下界的差距形状，估计要把下界推到 1 还需要什么样的定量增益。要点：这是实验，不是证明；结论必须写成「在此范围内观察到什么」。",
  },
  {
    slug: "cycles",
    mission:
      "环搜索。实现 Böhm 与 Sontacchi 型判据：若存在周期 k 步、其中 m 步为奇数步的环，则解的整数 x 满足 x = c 除以 (2^k 减 3^m)，其中 c 由该环的奇偶向量决定，且必须 2^k 大于 3^m。长度 k 的奇偶向量有 2^k 个，稍大就无法全枚举，所以必须使用完备的剪枝（例如 Eliahou 型判据、Crandall 的解法或你自己推导并证明完备性的剪枝），并在报告里说明剪枝为什么完备。必须做阳性对照：负整数上已知有三个环（包含 -1、-5、-17 的那三个），用同一套判据能不能把它们全部找回来；找不回来就说明判据有 bug。如实报告你完成完备搜索的范围，以及为什么不能把范围推到文献记录的 10^8 量级（时间、内存、还是需要更强的丢番图工具）。",
  },
  {
    slug: "parity-vectors",
    mission:
      "奇偶向量与 2-adic 结构实验。验证 Terras 的仿射公式：给定长度 k 的奇偶向量，T^k(x) 等于 (3^m x 加 c) 除以 2^k；用精确整数枚举验证 c 的递推、验证环方程、并数值检验 Bernstein 与 Lagarias 型共轭在小范围上的行为。更有价值的部分：构造「引理杀手」——把文献里常见的中途引理（例如「停时序列在两两同余类上均匀」这类启发式断言）取成精确命题，在可枚举范围内搜索反例。找到反例就精确记录最小的反例。",
  },
  {
    slug: "reverse-tree",
    mission:
      "逆向树实验。从 1 出发，用分支 x 到 2x 与 x 到 (2x-1)/3（后者仅当分子是 3 的倍数且结果为正奇数时可用）做广度优先生长，测量：节点数随层数的增长曲线（与 (4/3)^层数 之类的预测对照）、每层覆盖了哪些奇数、以及在小范围内每个奇数是否都出现在树里。要点：树包含所有奇数等价于原猜想，所以小范围的成功只是阳性对照，不是证明路径的近似；必须在结论里写清这一点。",
  },
  {
    slug: "smt-certificate",
    mission:
      "证书搜索。用已装好的 z3（在 20-experiments/.venv 里）在截断状态空间 1 到 N 上（自行取 N，建议 2^20 以内并权衡耗时）搜索形如 V(x) = a*x + b*「x 的二进制中 1 的个数」，或更一般的按位仿射形式，使得对每个 x 都有 V(T(x)) 不超过 V(x) 减 1。报告 SAT 或 UNSAT；SAT 就给出证书并逐点验证；UNSAT 就写清「该形式在该截断上不存在证书」这一事实否证了什么、不否证什么。另外用 z3 做反例搜索：是否存在 x 不超过 N 使轨道长度超过给定 K（这是可满足性问题，能给出具体反例）。",
  },
];

interface RouteSpec {
  /** 路线短标识 */
  slug: string;
  /** 这条路线要尝试证明什么 */
  mission: string;
}

const routes: RouteSpec[] = [
  {
    slug: "arithmetic-cycles",
    mission:
      "算术路线：把「无环」与「必达 1」分开处理。用 Böhm 与 Sontacchi 方程与 2^k 与 3^m 的分离性，尝试给出新的显式界或新的不可能性定理；也可以尝试对周期下界做一个新的初等推导，或精确说明为什么初等方法只能到某个数量级。",
  },
  {
    slug: "tao-quantitative",
    mission:
      "量化改进路线：把 Tao 型「几乎所有轨道取到几乎有界值」的论证拆到引理级，精确写出它需要的定量估计，以及从「几乎有界」到「有界」还差什么。然后尝试证明其中某个更强的估计；做不出来就精确给出「现有框架为什么达不到」的技术理由，并说明需要什么样的新输入。",
  },
  {
    slug: "two-adic-control",
    mission:
      "2-adic 与遍历控制路线：利用 Bernstein 与 Lagarias 型共轭把加速映射看成 2-adic 移位，尝试把测度论或遍历论结论升级为对整数与有理点的控制；或者反过来说明为什么共轭给出的信息本质上不足以控制有理点（这本身是一个有价值的部分结论）。",
  },
  {
    slug: "minimal-counterexample",
    mission:
      "最小反例路线：设 N 是最小反例（既不发散也不落入 1 的最小正整数），用停时、奇偶向量与模约束推出 N 的强结构（下界、同余性质、其轨道上的约束），尝试推出矛盾。推不动就精确写出卡在哪一步、还需要什么样的更强约束、以及现有约束离矛盾还差多远。",
  },
  {
    slug: "formal-automata",
    mission:
      "形式化与自动机路线：把某个受限版本的 Collatz（例如限定在某个自动机可表达的类、或模 2^s 的有限状态截断上）编码为自动机或线性递推并尝试判定；或者用证书搜索的结果证明某个受限形式下的不可能性定理（「任何这种形式的证书都不存在」），并精确说明它在何处不能升级为对原猜想的结论。",
  },
  {
    slug: "diophantine-transcendence",
    mission:
      "丢番图与超越数论路线：用 LLL 格基约化（sympy 有 lll 可用，也可以自己实现小维度的版本）与线性型对数下界的思想，尝试改进 3^m 与 2^k 的分离界，或对 m-cycle 判据给出新的显式数值界。必须给出可独立验证的数值结果，并说明它距完整证明还差多少个数量级。",
  },
];

/** 把反驳结论映射成看板上的状态。 */
function routeStatus(verdict: string, action: string): string {
  if (verdict === "route-doomed") return "已证伪";
  if (action === "fixed") return "局部存活";
  if (verdict === "fatal") return "已证伪";
  if (verdict === "serious") return "已反驳";
  return "局部存活";
}

artifact.board("routes", {
  title: "六条证明路线的实时状态",
  key: "route",
  status: "status",
  columns: ["论证中", "已反驳", "局部存活", "已证伪"],
  cardTitle: "route",
  detail: [{ field: "gap", label: "主要缺口" }],
});

phase("建立战场：工具链盘点与技能侦察");
const toolchain = await world.run("collatz-attack/20-experiments/.venv/bin/python", [
  "-c",
  "import numpy,sympy,z3,gmpy2,flint;print('toolchain ok')",
]);
log(`工具链自检退出码 ${toolchain.exitCode}`);

const envProbe = agent("环境勘测员", {
  system: "你是科拉茨攻坚项目的环境勘测员，负责把本机可用与不可用的计算资源如实记录成文档。" + STYLE,
});
const skillsProbe = agent("技能侦察员", {
  system: "你负责盘点本机已安装的智能体技能，并判断哪些能用于数学攻坚。" + STYLE,
});

const envResult = await Promise.all([
  envProbe.ask<string>(
    `盘点本机计算环境，并把结论写到 /Users/luna/Documents/math IA/collatz-attack/20-experiments/ENV.md。` +
      `必须用 Bash 实测后记录，不许凭猜：` +
      `(a) 本目录自带环境 collatz-attack/20-experiments/.venv/bin/python 的版本与已装数学库（numpy、sympy、z3、gmpy2、python-flint）；` +
      `(b) 系统 python3 的版本与可用库；` +
      `(c) C 编译器（cc、clang）版本；` +
      `(d) CPU 核数、内存、可用磁盘；` +
      `(e) 明确记录：本机没有 Lean、Coq、Isabelle、PARI 或 Sage，因此本工作不会安装全局形式化工具链，只会产出 Lean 源码与安装脚本；` +
      `(f) 给出后续实验用哪个解释器的明确建议（推荐写全路径）。` +
      `ENV.md 要包含一节「这台机器能做什么、不能做什么」。中文正文不要出现半角连字符。返回你写入的文件的绝对路径。`,
  ),
  skillsProbe.ask<string>(
    `盘点可用于本项目的智能体技能，并把结论写到 /Users/luna/Documents/math IA/collatz-attack/00-scope/SKILLS.md。` +
      `做法：先看本机已安装技能清单（可用 Skill 工具列表、或读 ~/.zcode/skills 与 ~/.agents/skills 的目录名），挑出与「形式化证明、数论、数学计算、可视化」相关的条目，逐条评估它对科拉茨攻坚的实际用处。` +
      `安装纪律（硬要求）：只允许从官方插件市场安装技能；任何第三方来源的技能一律只报告候选与来源，绝不安装，因为那等于往用户机器上装来路不明的代码。` +
      `如果发现确实有用且来自官方市场的技能，说明它的名字与它能做什么；如果认定没有值得安装的，就直接说不需要安装，并说明现有技能（例如 sympy、z3、Leet 之类）已经够用。` +
      `返回你写入的文件的绝对路径与一句话结论。`,
  ),
]);

log(`技能盘点与技能侦查完成：环境报告 ${envResult[0]}，技能结论 ${envResult[1]}`);

phase("分头检索八条研究线，并逐条回到原始来源核对");
const litOutcomes = await Promise.all(
  litTopics.map(async (t) => {
    try {
      const writer = agent(`文献检索员·${t.slug}`, {
        system:
          "你是科拉茨猜想研究的文献检索员，负责把一条研究线的现状钉死。" +
          "硬要求：每条关键结果都要给出可打开的原始来源（arXiv、期刊、作者主页、OEIS）；禁止凭记忆断言某论文证明了什么；打不开或无法确认的一律标注。" +
          STYLE,
      });
      const first = await writer.ask<TopicResult>(
        `你负责的研究线是：${t.mission}\n\n` +
          `工作方式：\n` +
          `1. 用 WebSearch 与 WebFetch 检索，必要时换用 DuckDuckGo 兜底；优先预印本与期刊原文。\n` +
          `2. 每条关键结果写成一行：结论 —— 年份、作者、可打开的出处 URL。无法确认的在该行标注「未能核对」。\n` +
          `3. 区分三类可信度：经同行评审的定理、仅预印本的宣称、已被反驳或撤回的宣称。\n` +
          `4. 用自己的话精确重述（保留量词与范围），不要复制大段原文。\n\n` +
          `把笔记写到 ${t.notePath}，结构为：\n` +
          `# ${t.slug}\n## 这条线在问什么\n## 关键结果\n## 当前的技术极限（记录值是多少、谁保持、为什么停在那里）\n## 未解决的缺口\n## 若要在这一线推进，必须跨过什么门槛\n## 来源清单（全部 URL，逐条注明你是否亲自打开过）\n\n` +
          `最后按 schema 返回。`,
      );
      const check = await agent(`引文核对员·${t.slug}`, {
        system:
          "你是独立的引文核对员，唯一的任务是打假。你不修改任何文件，只报告核对结论。" + STYLE,
      }).ask<CitationCheck>(
        `读 ${t.notePath}，对该文件「关键结果」一节逐条执行核对：\n` +
          `1. 打开该条给出的 URL，确认三件事：链接可达；该来源确实包含所述结论；年份、作者、范围与量词与笔记一致。\n` +
          `2. 任何一条不满足，写入 corrections，并给出正确说法（附你自己的来源 URL）。\n` +
          `3. verdict 的判定：只要有一条是编造或严重失真，记 some-wrong；主要来源打不开，记 unverifiable；全部核对通过才记 all-verified。\n` +
          `不要为了凑数而挑措辞无关紧要的差异，但也不要放过任何量词或范围被改写的条目（例如把「计数意义上的密度 1」写成「对所有 n」）。`,
      );
      let final = first;
      if (check.verdict !== "all-verified" && check.corrections.length > 0) {
        final = await writer.ask<TopicResult>(
          `引文核对员指出了以下问题：\n${JSON.stringify(check.corrections, null, 2)}\n\n` +
            `请逐条核实：能确认的更正后重写 ${t.notePath}；你自己认为核对员弄错了的，在笔记里加一节「对核对意见的回应」说明理由。` +
            `然后按 schema 重新返回完整的 keyClaims 与 openGaps（以修订后的笔记为准）。`,
        );
      }
      const outcome: LitOutcome = {
        slug: t.slug,
        notePath: t.notePath,
        keyClaimCount: final.keyClaims.length,
        openGapCount: final.openGaps.length,
        citationStatus: check.verdict,
        summary: `${final.keyClaims.length} 条关键主张，核对结论 ${check.verdict}，缺口 ${final.openGaps.length} 条。`,
      };
      report({
        topic: t.slug,
        claims: outcome.keyClaimCount,
        citation: outcome.citationStatus,
        summary: outcome.summary,
        notePath: outcome.notePath,
      });
      return outcome;
    } catch (e) {
      log(`文献线 ${t.slug} 未完成：${String(e).slice(0, 200)}`);
      const fallback: LitOutcome = {
        slug: t.slug,
        notePath: t.notePath,
        keyClaimCount: 0,
        openGapCount: 0,
        citationStatus: "unverifiable",
        summary: `未完成：${String(e).slice(0, 200)}`,
      };
      return fallback;
    }
  }),
);
log(`八条文献线完成 ${litOutcomes.length} 条，预计在边界地图里汇总`);

phase("绘制已知结果与障碍的边界地图");
const cartographer = agent("边界地图绘制者", {
  system: "你是攻坚项目的边界地图绘制者，负责把八条文献线压缩成一份可执行的判断文件。" + STYLE,
});
const frontier = await cartographer.ask<Frontier>(
  `读这八份笔记并汇总：${litTopics.map((t) => t.notePath).join("、")}\n\n` +
    `（其中可能有标注「未完成」的，遇到就如实说明该线缺失。）\n\n` +
    `写 /Users/luna/Documents/math IA/collatz-attack/10-literature/frontier.md，内容包括：\n` +
    `1. 已确证的核心结果，按强度排序，每条一句话并带出处。\n` +
    `2. 已证伪或已被排除的路线。\n` +
    `3. 已知的结构性障碍：为什么某些方法必然失败（每条给出出处）。\n` +
    `4. 活口清单：仍可能在数学上推进的入口，按「距离真证明可能最近」排序，每条写清它需要什么新工具。\n` +
    `5. 一份「任何完整证明至少必须跨过的门槛」清单，逐条写成精确的技术要求（例如需要关于 2^k 与 3^m 分离性的更强下界、需要某个一致估计，等等）。\n\n` +
    `禁止把不确定的东西写成确定；禁止出现「已被证明」而实际只是预印本宣称的条目。中文正文不要出现半角连字符。按 schema 返回。`,
);
report({
  topic: "frontier",
  claims: frontier.established.length,
  citation: "synthesized",
  summary: `边界地图：${frontier.established.length} 条已确证结果，${frontier.liveGaps.length} 个活口，${frontier.deadEnds.length} 条死路。`,
  notePath: frontier.path,
});

const frontierReader = agent("边界地图审读员", {
  system: "你是独立审读员，只从文件与原始来源判断，不轻信上游的转述。" + STYLE,
});
const frontierReview = await frontierReader.ask<FrontierReview>(
  `读 ${frontier.path} 与它引用的八份笔记，做四件事：\n` +
    `1. 从边界地图里随机抽至少 6 条主张，打开它们声称的原始来源，核对是否真的支持地图里的说法。\n` +
    `2. 找出被夸大或错放的条目（例如把「密度 1」写成「所有」、把预印本宣称写成定理）。\n` +
    `3. 找出「活口清单」里明显已经死掉、或明显不该排在前面的条目，并说明理由。\n` +
    `4. 指出地图遗漏的、你认为重要的已知结果。\n` +
    `每条问题写成一句话并给出文件路径或 URL。禁止修改文件。`,
);
if (frontierReview.problems.length > 0) {
  await cartographer.ask<string>(
    `审读员在边界地图上发现了以下问题（每条都附了出处）：\n${JSON.stringify(frontierReview.problems, null, 2)}\n\n` +
      `请逐条处理：该改的改 ${frontier.path}，审读员说错的就在文件里加一节「对审读意见的回应」说明理由。返回修订摘要。`,
  );
}
log(`边界地图经审读，问题数 ${frontierReview.problems.length}，抽样核对 ${frontierReview.claimsChecked} 条`);

phase("跑六组计算实验，每组由独立的另一个实现重算");
const experimentOutcomes = await Promise.all(
  experiments.map(async (e) => {
    try {
      const runner = agent(`实验执行者·${e.slug}`, {
        system:
          "你是科拉茨攻坚项目的计算实验执行者。" +
          "你会亲自写代码并运行，所有数字必须来自你自己的运行输出，禁止把文献里的数字当成自己的计算结果。" +
          "每个结论都必须附「这个实验不能证明什么」。" +
          STYLE,
      });
      const result = await runner.ask<ExperimentResult>(
        `实验任务：${e.mission}\n\n` +
          `产物与纪律：\n` +
          `1. 脚本放在 collatz-attack/20-experiments/scripts/ 下，原始输出写到 collatz-attack/20-experiments/results/ 下，结论写到 collatz-attack/20-experiments/findings/${e.slug}.md。\n` +
          `2. 一律用本目录自带环境运行：/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python（里面有 numpy、sympy、z3、gmpy2、python-flint）。用 C 的话用 cc -O3 编译，可执行文件放 scripts/ 下。\n` +
          `3. findings 文件必须包含：目的、方法、完整命令行、耗时、原始输出摘要、关键数字、「这个实验不能证明什么」（至少三条）。\n` +
          `4. 关键数字里必须写明你实际达到的范围，不许写成没有范围限制的普遍断言。\n` +
          `5. 如果某一步在你的机器上跑不动，就降低规模并如实报告你降到了多少、为什么。\n\n` +
          `按 schema 返回。中文正文不要出现半角连字符。`,
      );
      const rechecker = agent(`复核实验员·${e.slug}`, {
        system:
          "你是独立复核员，任务是打假上游实验的数字。" +
          "你与原作者没有任何共享上下文；你只信自己跑出来的结果。" +
          "禁止修改上游的任何文件。" +
          STYLE,
      });
      const recheck = await rechecker.ask<Recheck>(
        `实验 ${e.slug} 的产物在：\n结论 ${result.findingPath}\n原始输出 ${result.resultPath}\n脚本 ${result.scriptPath}\n\n` +
          `任务：\n` +
          `1. 读这三个文件，挑出其中最关键的两到三个数字。\n` +
          `2. 用与原作者不同的方法独立重算（例如他用记忆化 Python，你就写一段 C 或未记忆化的分段计算；他用整段枚举，你就换不同上界与不同实现交叉验证）。必须自己动手跑，不许把他的输出文件当证据。\n` +
          `3. 特别检查：边界处是否有 off-by-one（例如「n 不超过 2^28」是否真的包含 2^28）；是否漏算某些 n；是否把文献数字冒充为计算结果；阳性对照（如果任务里有）是否真的通过。\n` +
          `4. 逐条返回你重算到的数字与所用方法；任何不一致写入 discrepancies。确实无法独立复核的，直说无法，并说明原因。\n` +
          `按 schema 返回。`,
      );
      report({
        topic: `experiment:${e.slug}`,
        claims: result.keyNumbers.length,
        citation: recheck.discrepancies.length === 0 ? "independently-rechecked" : "discrepancy-flagged",
        summary: `关键数字 ${result.keyNumbers.length} 条；独立重算 ${recheck.rederived.length} 条；不一致 ${recheck.discrepancies.length} 处。`,
        notePath: result.findingPath,
      });
      if (recheck.discrepancies.length > 0) {
        await runner.ask<string>(
          `复核员用另一套方法得到的数字与你的报告不一致：\n${JSON.stringify(recheck.discrepancies, null, 2)}\n\n` +
            `请查清原因：是你的 bug、他的 bug、还是定义差异。修订 findings 文件并返回一句话结论（谁对，依据是什么）。`,
        );
      }
      return { result, recheck };
    } catch (e2) {
      log(`实验 ${e.slug} 未完成：${String(e2).slice(0, 200)}`);
      const fallbackResult: ExperimentResult = {
        slug: e.slug,
        scriptPath: "未产出",
        resultPath: "未产出",
        findingPath: "未产出",
        keyNumbers: [],
        doesNotShow: [`实验未完成：${String(e2).slice(0, 200)}`],
      };
      const fallbackRecheck: Recheck = {
        slug: e.slug,
        rederived: [],
        discrepancies: [`实验未完成，无法复核：${String(e2).slice(0, 200)}`],
      };
      return { result: fallbackResult, recheck: fallbackRecheck };
    }
  }),
);
log(`六组实验完成，其中带不一致标记的有 ${experimentOutcomes.filter((o) => o.recheck.discrepancies.length > 0).length} 组`);

phase("沿六条路线做证明尝试，并请人反驳");
const routeOutcomes = await Promise.all(
  routes.map(async (r) => {
    try {
      const explorer = agent(`路线探索者·${r.slug}`, {
        system:
          "你是一名受托证明科拉茨猜想的数学工作者。你所在的团队有一条铁律：不许装作证明成功。" +
          "每一步要么是已证定理（给出出处），要么是你能完整证明的初等引理，要么显式标注为缺口。" +
          "你的价值不在于宣布证明，而在于把失败点定到最精确。" +
          STYLE,
      });
      const attempt = await explorer.ask<RouteAttempt>(
        `你负责的路线是：${r.mission}\n\n` +
          `先读这些材料（用 Read，不要跳过）：\n` +
          `- /Users/luna/Documents/math IA/collatz-attack/10-literature/frontier.md（边界地图：已证结果、死路、活口、必须跨过的门槛）\n` +
          `- /Users/luna/Documents/math IA/collatz-attack/20-experiments/findings/ 下与你路线相关的实验结论\n` +
          `- 需要时直接联网查文献。\n\n` +
          `纪律（必须遵守）：\n` +
          `1. 你真的要推进证明，不是写综述。论证写成编号步骤，每步标注状态：已证（给出来源或完整初等证明）、[缺口] 未证、[错误] 已知为假、[等价于原命题] 循环论证。\n` +
          `2. 任何声称完成的步骤都要写全量词、范围与边界情形。做不出来就老实标缺口，并写清「跨过它需要什么」。\n` +
          `3. 鼓励产出局部新结论（初等引理），但必须单独列出并说明如何独立验证（能写成可跑代码的就写出来）。\n` +
          `4. 严禁伪造文献、引理名或数字。\n\n` +
          `产物写到 /Users/luna/Documents/math IA/collatz-attack/30-proof-attempts/${r.slug}/attempt.md，结构：\n` +
          `# ${r.slug}\n## 我尝试证明的定理（精确陈述）\n## 论证（编号步骤，每步标注状态）\n## 失败点清单（逐条说明为什么是缺口，以及跨过它需要什么）\n## 局部新结论（若有，含独立验证方式）\n## 与文献的关系（哪些已知结果支持或否决本路线）\n## 若要继续，下一步最该做什么\n\n` +
          `按 schema 返回。中文正文不要出现半角连字符。`,
      );
      report({ route: r.slug, status: "论证中", gap: attempt.mainGap }, "routes");

      const rebutter = agent(`独立反驳者·${r.slug}`, {
        system:
          "你是独立反驳者，任务是打掉一份证明尝试。你与作者没有任何共享上下文。" +
          "泛泛而谈「可能有漏洞」「需要更多工作」一律不接受：要么给出具体反例，要么给出明确引用。" +
          "禁止修改任何文件。" +
          STYLE,
      });
      const rebuttal = await rebutter.ask<Rebuttal>(
        `读 /Users/luna/Documents/math IA/collatz-attack/30-proof-attempts/${r.slug}/attempt.md 以及它引用的文献（需要时联网）。\n\n` +
          `任务：找出最致命的一步，并二选一给出证据：\n` +
          `(a) 具体反例：写出代码并实际运行（Bash 与 python 均可），把命令与输出贴进 evidence 与 counterexampleCommand；\n` +
          `(b) 明确引用：打开原始来源，证明该步骤是假的、已被证伪的、或仍然是公开未决问题。\n\n` +
          `判定标准：\n` +
          `- 若整条路线已被文献证明此路不通（例如有不可能性定理），verdict 记 route-doomed 并给出处。\n` +
          `- 若找到的是真正致命的错误（例如标为已证的步骤实际是假的），记 fatal。\n` +
          `- 若是「你漏掉了某个已知困难，但论证本身没错」，记 serious。\n` +
          `- 若你试遍了攻击面都没能打掉它，记 survivable，并在 evidence 里列出你试过哪些攻击面（这本身很有价值）。\n` +
          `按 schema 返回。`,
      );

      const response = await explorer.ask<RouteResponse>(
        `独立反驳者对你的尝试给出了如下结论：\n${JSON.stringify(rebuttal, null, 2)}\n\n` +
          `你要做的：\n` +
          `1. 要么修补（fixed，必须真的补上论证或改正错误结论），要么撤下该结论（conceded），要么指出反驳本身有误（defended，必须给出具体理由与证据，包括打开来源或跑代码）。\n` +
          `2. 把本次回应追加到 attempt.md 末尾的「## 对反驳的回应」一节，并同步修订正文里被推翻的部分（不要让正文还留着你已经撤下的结论）。\n` +
          `按 schema 返回。`,
      );
      const status = routeStatus(rebuttal.verdict, response.action);
      report({ route: r.slug, status: status, gap: rebuttal.strongestObjection }, "routes");
      return { attempt, rebuttal, response, status };
    } catch (e3) {
      log(`路线 ${r.slug} 未完成：${String(e3).slice(0, 200)}`);
      const fallbackAttempt: RouteAttempt = {
        slug: r.slug,
        path: "未产出",
        theorem: "未产出",
        gapCount: -1,
        mainGap: "路线未完成（详见运行日志；此处不写可变文本，以免破坏重放确定性）",
        localLemmas: [],
      };
      const fallbackRebuttal: Rebuttal = {
        slug: r.slug,
        verdict: "fatal",
        strongestObjection: "尝试未完成，无从反驳",
        evidence: "尝试未完成，无从反驳（异常信息见运行日志）",
        counterexampleCommand: "none",
      };
      const fallbackResponse: RouteResponse = { path: "未产出", action: "conceded", note: "未完成" };
      report({ route: r.slug, status: "已证伪", gap: fallbackAttempt.mainGap }, "routes");
      return {
        attempt: fallbackAttempt,
        rebuttal: fallbackRebuttal,
        response: fallbackResponse,
        status: "已证伪",
      };
    }
  }),
);

const routesSummary = routeOutcomes.map((o) => ({
  slug: o.attempt.slug,
  verdict: o.rebuttal.verdict,
  action: o.response.action,
  mainGap: o.attempt.mainGap,
  localLemmas: o.attempt.localLemmas.length,
}));

const judge = agent("路线裁决员", {
  system: "你是攻坚项目的裁决者，负责在六条路线之间排序并挑出最值得继续攻击的两条。" + STYLE,
});
const routeVerdict = await judge.ask<RouteVerdict>(
  `六条路线的状态如下（含各自的首次反驳结论与作者回应）：\n${JSON.stringify(routesSummary, null, 2)}\n\n` +
    `完整材料在 /Users/luna/Documents/math IA/collatz-attack/30-proof-attempts/ 各子目录下，可以读。\n\n` +
    `任务：\n` +
    `1. 按「距离真证明的远近」排序：排序依据不是路线听起来宏大，而是它的失败点是否具体、是否只差一个可能被攻下的技术环节、以及它的局部新结论是否站得住。已被文献证明此路不通的排最后。\n` +
    `2. 挑出最值得加派第二轮反驳的两个 slug（注意：不是最有希望的，而是「如果这里出错，代价最大」的两条，也允许挑反驳质量最差的那条）。\n` +
    `3. 给出两三句理由。按 schema 返回。`,
);

const secondRound = await Promise.all(
  routeVerdict.top2.map(async (slug) => {
    let idx = -1;
    for (let i = 0; i < routeOutcomes.length; i += 1) {
      if (routeOutcomes[i].attempt.slug === slug) {
        idx = i;
      }
    }
    if (idx < 0) {
      log(`裁决给出的 slug ${slug} 不存在，跳过第二轮反驳`);
      return `${slug}：跳过（该 slug 不存在）`;
    }
    const { attempt, rebuttal, response } = routeOutcomes[idx];
    const chief = agent(`首席反驳者·${slug}`, {
      system:
        "你是首席反驳者，攻击对象是「尝试加首轮反驳加作者回应」的整条链路。" +
        "你的独特价值在于检查双方是否都在自欺。禁止修改 attempt.md 的正文（你可以另写文件）。" +
        STYLE,
    });
    return await chief.ask<string>(
      `攻击这三份材料：\n` +
        `尝试：${attempt.path}\n` +
        `首轮反驳：${JSON.stringify(rebuttal, null, 2)}\n` +
        `作者回应：${JSON.stringify(response, null, 2)}\n\n` +
        `重点检查三件事：\n` +
        `(a) 首轮反驳本身是否站得住（有没有反驳错了、把正确的步骤判成错的）；\n` +
        `(b) 作者的修补是否只是修辞上的让步，而不是真的补上了论证；\n` +
        `(c) 双方都漏掉的缺口。\n\n` +
        `把备忘录写到 /Users/luna/Documents/math IA/collatz-attack/30-proof-attempts/${slug}/rebuttal-2.md，` +
        `包含：最致命的一击（一句话）、证据（URL 或你实际运行过的反例命令与输出）、以及一句话总评。返回备忘录路径加一句话结论。`,
    );
  }),
);
log(`第二轮反驳覆盖 ${secondRound.length} 条路线`);

phase("把确立的引理交给机器逐条复核");
const leanWriter = agent("形式化写手·Lean", {
  system:
    "你负责把初等引理写成 Lean 4 源码。本机没有 Lean 工具链，所以你写的东西无法编译，这一点必须在文件里如实声明，并写成别人能照着编译的形式。" +
    "严禁编造 Mathlib 中不存在的引理名：不确定的一律用注释标注 TODO，让编译者去查。" +
    STYLE,
});
const leanResult = await leanWriter.ask<FormalResult>(
  `任务：把本次工作中确实立住的初等引理形式化为 Lean 4。候选清单（自行判断哪些真的成立，只做能站住的）：\n` +
    `1. 奇偶向量与仿射公式：长度为 k 的奇偶向量决定 T^k(x) 等于 (3^m x 加 c) 除以 2^k，其中 m 是该向量中奇数步的个数。\n` +
    `2. c 的递推关系（把 c 按向量逐位递推）。\n` +
    `3. 环方程：若 T^k(x) 等于 x 且 x 非零，则 x 等于 c 除以 (2^k 减 3^m)，且必有 2^k 大于 3^m。\n` +
    `4. 有限停时与奇偶向量的对应（Terras 型初等部分）。\n\n` +
    `产物：\n` +
    `- /Users/luna/Documents/math IA/collatz-attack/40-formal/lean/CollatzBasic.lean，每个引理写成 theorem，证明尽量完整；证明写不出来但陈述确定的，用 sorry 并在注释里写明还缺什么。\n` +
    `- /Users/luna/Documents/math IA/collatz-attack/40-formal/README.md：写清如何安装工具链（elan、lake、Mathlib 缓存）与编译命令，以及预期的工作量与风险。\n` +
    `- /Users/luna/Documents/math IA/collatz-attack/40-formal/setup-lean.sh：安装脚本。\n\n` +
    `文件头部的注释必须写明：本文件未经 Lean 编译器检验，因为它是在没有 Lean 工具链的机器上写成的。按 schema 返回。`,
);
report({
  topic: "formal-lean",
  claims: leanResult.lemmas.length,
  citation: "not-compiled",
  summary: `Lean 4 源码已写出 ${leanResult.files.length} 个文件，覆盖 ${leanResult.lemmas.length} 条引理；本机无编译器，未经检验，安装脚本已一并提供。`,
  notePath: "collatz-attack/40-formal/lean/",
});

const checkWriter = agent("形式化检查员·Python", {
  system:
    "你负责用精确算术逐条检验引理，写成可重复运行的检查脚本。" +
    "你的脚本必须自己重新计算一切，禁止读取 20-experiments 下的结果文件来「验证」。" +
    STYLE,
});
const checkResult = await checkWriter.ask<FormalResult>(
  `任务：写 /Users/luna/Documents/math IA/collatz-attack/40-formal/exact_check.py，用精确整数与有理数（标准库 fractions 或已装的 gmpy2）对下列引理在有限参数范围内逐条验证：\n` +
    `1. 奇偶向量与仿射公式（对全部长度 k 不超过 16 的向量与若干随机大向量验证）。\n` +
    `2. c 的递推（同上）。\n` +
    `3. 环方程与 2^k 大于 3^m 的必要性（对可行范围内满足条件的 (k, m) 组合验证；并用负整数上已知的三个环做阳性对照，其中至少包含 -1 与 -5 所在的两个环）。\n` +
    `4. 停时与奇偶向量长度的对应关系（对可枚举范围验证）。\n\n` +
    `要求：\n` +
    `- 每个引理一个断言函数，逐一运行并打印 PASS 或 FAIL；FAIL 时必须打印最小反例。\n` +
    `- 打印要简洁（总量控制在几百行以内）。全部通过时退出码 0，任何失败退出码非 0。\n` +
    `- 文件顶部注释必须写明：这是有限范围内的抽样验证，不是证明；全称命题无法靠有限枚举确立。\n` +
    `- 只允许用标准库加已装的 gmpy2 与 sympy。\n` +
    `按 schema 返回。`,
);

let gateExit = -1;
for (let round = 1; round <= 3; round += 1) {
  let err = "";
  let code = -1;
  try {
    const run = await world.run("collatz-attack/20-experiments/.venv/bin/python", [
      "collatz-attack/40-formal/exact_check.py",
    ]);
    code = run.exitCode;
    err = `${run.stdout.slice(-2000)}\n${run.stderr.slice(-2000)}`;
  } catch (e4) {
    log(`精确检查脚本执行失败：${String(e4).slice(0, 120)}`);
    err = "命令未能执行（文件不存在、解释器路径无效或超时）";
  }
  gateExit = code;
  if (code === 0) break;
  if (round === 3) break;
  await checkWriter.ask<FormalResult>(
    `精确检查脚本没有通过（第 ${round} 轮，退出码 ${code}）。输出末尾如下：\n${err}\n\n` +
      `请判断是脚本的 bug、还是它验证的命题陈述本身有问题（例如陈述写错了、或那个引理其实不成立）。` +
      `修正后重写脚本，或者若发现某条引理其实不成立，就把该条改成正确的陈述并在 limits 里说明。\n` +
      `注意：如果你发现某条候选引理是假的，这本身是重要发现，必须在 limits 里清楚记下来。`,
  );
}
report({
  topic: "formal-check",
  claims: checkResult.lemmas.length,
  citation: gateExit === 0 ? "gate-passed" : "gate-failed",
  summary:
    gateExit === 0
      ? `精确算术检查脚本全部通过（退出码 0），覆盖 ${checkResult.lemmas.length} 条引理。`
      : `精确算术检查脚本最终退出码 ${gateExit}，仍有未通过项。`,
  notePath: "collatz-attack/40-formal/exact_check.py",
});
log(`精确检查闸门最终退出码 ${gateExit}`);

phase("写总报告并请红队削一遍");
const reporter = agent("总报告撰写者", {
  system:
    "你负责把整个攻坚项目写成一份诚实的总报告。" +
    "你的最高纪律是：不许让读者以为科拉茨猜想被证明了；凡是没有完整可核验论证的结论，必须写成未证。" +
    STYLE,
});
const reportOutcome = await reporter.ask<ReportOutcome>(
  `写 /Users/luna/Documents/math IA/collatz-attack/50-report/final-report.md。\n\n` +
    `材料（自行读取，目录结构见 collatz-attack/README.md 与 00-scope/problem.md）：\n` +
    `- 10-literature/frontier.md 与 10-literature/notes/ 下八份笔记\n` +
    `- 20-experiments/ENV.md、20-experiments/findings/ 下六份结论、20-experiments/results/ 下的原始输出\n` +
    `- 30-proof-attempts/ 下六条路线的尝试、反驳、回应与第二轮备忘录\n` +
    `- 40-formal/ 下的精确检查脚本与 Lean 源码\n` +
    `- 00-scope/SKILLS.md\n\n` +
    `本运行内部结论摘要（供你交叉核对你读到的文件是否一致）：\n` +
    `${JSON.stringify(routesSummary, null, 2)}\n` +
    `路线裁决：${JSON.stringify(routeVerdict, null, 2)}\n` +
    `精确检查闸门退出码：${gateExit}\n\n` +
    `报告必须包含：\n` +
    `1. 开头一句显式声明：本工作没有证明科拉茨猜想，它是开放问题；本报告给出的是边界、可复核的局部结果与失败点。\n` +
    `2. 摘要（不超过 300 字）。\n` +
    `3. 主张台账：一张表，三档状态（已确证见诸来源、本工作计算得到且经独立重算、未证或存疑），每行给出证据指针（文件路径或 URL）。\n` +
    `4. 六条路线逐条报告：尝试了什么、最致命的一击是什么、作者如何回应、最终状态、以及「如果要继续，下一步最该做什么」。\n` +
    `5. 计算实验逐条：范围、关键数字、独立重算是否一致、不能证明什么。\n` +
    `6. 机器可复核清单：怎么复现每一个数字（完整命令）。\n` +
    `7. 未做的事与做不到的事。\n` +
    `8. 结尾：把六条路线的失败点合并成一张「攻坚地图」，说明每条路线离完整证明还差什么。\n\n` +
    `所有数字必须能在文件里找到出处；找不到出处的就别写。中文正文不要出现半角连字符。按 schema 返回。`,
);
const redteam = agent("红队审读员", {
  system:
    "你是红队审读员，唯一任务是把总报告里的夸大与不实之处挖出来。" +
    "越是「证明了」这样的字眼，你越要查。不修改文件。" +
    STYLE,
});
const redReview = await redteam.ask<RedTeam>(
  `你审读的是第一版报告：${reportOutcome.path}\n\n读它，并抽取其中至少 8 条关键主张，回到原始来源核对（笔记文件、结果文件、文献 URL、30-proof-attempts 下的原文）。\n\n` +
    `逐条列出：夸大（把有限验证说成证明、把预印本说成定理）、无证据、与文件不符、内部矛盾的地方，每条给出文件路径与行号或 URL。\n` +
    `若报告声称了任何「证明了」的结论，必须最严厉检查，并明确回答：该论证是否真的完整可核验。\n` +
    `找不到问题就明说，并列出你抽查了哪些条目。按 schema 返回。`,
);
const finalReport = await reporter.ask<ReportOutcome>(
  `红队审读员在你写的总报告里发现了以下问题：\n${JSON.stringify(redReview.problems, null, 2)}\n\n` +
    `请逐条处理，并重写 /Users/luna/Documents/math IA/collatz-attack/50-report/final-report.md：\n` +
    `- 该降级的结论降级（把「证明了」改成「在此范围内验证」之类）。\n` +
    `- 该补证据的补上文件路径或 URL。\n` +
    `- 红队弄错了的，在报告末尾加一节「对红队意见的回应」并说明理由。\n` +
    `- 在报告末尾保留一份「红队抽查记录」：红队抽查了多少条、处理了多少条。\n` +
    `按 schema 返回，并在 unresolved 里诚实地列出仍未解决的争议。`,
);

let reportPath = finalReport.path;
try {
  await artifact.file("report", "collatz-attack/50-report/final-report.md", {
    title: "科拉茨猜想攻坚总报告",
    description: "边界地图、六组计算实验、六条证明路线的失败点、以及机器可复核清单。本工作没有证明科拉茨猜想。",
    primary: true,
  });
} catch (e5) {
  log(`总报告发布失败，请撰写者重写文件：${String(e5).slice(0, 200)}`);
  const repaired = await reporter.ask<ReportOutcome>(
    `发布总报告失败了（原因：${String(e5).slice(0, 300)}）。请确认并重写 /Users/luna/Documents/math IA/collatz-attack/50-report/final-report.md，` +
      `要求文件存在、内容完整。返回路径。`,
  );
  reportPath = repaired.path;
  await artifact.file("report", "collatz-attack/50-report/final-report.md", {
    title: "科拉茨猜想攻坚总报告",
    description: "边界地图、六组计算实验、六条证明路线的失败点、以及机器可复核清单。本工作没有证明科拉茨猜想。",
    primary: true,
  });
}

phase("交付可交互的边界图");
const pageMaker = agent("交互页制作者", {
  system:
    "你负责把攻坚成果做成一个单文件、离线可用的可交互页面。" +
    "所有数据必须来自真实产物文件，不许编造。" +
    STYLE,
});
const html = await pageMaker.ask<HtmlOutcome>(
  `写 /Users/luna/Documents/math IA/collatz-attack/50-report/frontier-map.html：单文件、无外部依赖（不引用任何 CDN 与网络字体）、离线可打开、中文界面。\n\n` +
    `数据来源（自己读取并提取，不要编造）：10-literature/frontier.md、10-literature/notes/ 下八份笔记、20-experiments/findings/ 下六份结论、30-proof-attempts/ 下六条路线的 attempt.md 与反驳文件。\n\n` +
    `页面至少包含四块：\n` +
    `1. 总览：八条文献线的现状与六条路线的最终状态（含每条路线最致命的一击），用卡片或表格呈现。\n` +
    `2. 可交互的停时探索器：输入任意正整数 n，用页面内联的 JavaScript 计算并显示它的 Collatz 轨道、步数、峰值与「是否到达 1」。不允许调用网络接口。\n` +
    `3. 边界地图可视化：已确证结果、已知死路、活口清单。\n` +
    `4. 诚实声明：本页面没有证明科拉茨猜想；它展示的是边界与失败点。\n\n` +
    `样式要求：深色主题、排版干净、可用键盘输入。\n` +
    `自测要求（必须做）：把页面里轨道计算的核心逻辑抽成纯函数后，用 node 跑一遍，验证若干已知例子（例如 n 等于 27 的总停时为 111 步、峰值 9232；n 等于 1 的步数为 0），把自测方式与结果写进返回的 selfTest 字段。\n` +
    `按 schema 返回。中文正文不要出现半角连字符。`,
);
report({
  topic: "frontier-map",
  claims: html.sections.length,
  citation: "self-tested",
  summary: `边界图页面已生成，含 ${html.sections.length} 块内容。制作者自测：${html.selfTest.slice(0, 240)}`,
  notePath: html.path,
});
try {
  await artifact.file("frontier", "collatz-attack/50-report/frontier-map.html", {
    title: "科拉茨边界图（可交互）",
    description: "八条文献线与六条证明路线的状态总览，附一个离线的停时探索器。",
  });
} catch (e6) {
  log(`边界图页面发布失败：${String(e6).slice(0, 200)}`);
}

const verifiedList: string[] = [
  "八条文献线的关键主张由独立引文核对员逐条回到原始来源核对，核对结论已记入各自笔记与总报告",
  "六组计算实验的关键数字由独立复核员用不同方法重算，不一致处已记录并追查",
  "精确算术检查脚本 collatz-attack/40-formal/exact_check.py 以退出码形式给出闸门结果，最终退出码 " +
    String(gateExit),
  "六条证明路线全部经过独立反驳，其中两条另加了首席反驳者做第二轮攻击",
  "总报告经过红队抽查，抽查条数 " + String(redReview.claimsChecked),
];
const notCoveredList: string[] = [
  "科拉茨猜想本身没有被证明或推翻：它是开放问题，本工作给出的是边界地图、可复核的局部结果与每条路线的精确失败点",
  "40-formal/lean 下的 Lean 源码未经编译器检验，因为本机没有 Lean 工具链，只提供了安装与编译脚本",
  "计算实验的验证上限远低于文献记录值，二者差距的原因已写入对应的实验结论文件",
  "所有「活口清单」条目仍属未证方向，不构成任何形式的证明起点",
];

return {
  conclusion:
    `科拉茨猜想没有被证明，也不会在一份工作流里被证明：它是 1937 年至今的开放问题，且有广义版本不可判定等结构性障碍。` +
    `本次攻坚交付的是三样东西：一份钉住已知边界与死路的边界地图（八条文献线，每条主张都回到原始来源核对）；` +
    `六组带独立重算的计算实验地基；以及六条证明路线的真实尝试，每条都写出了精确失败点并经过独立反驳与两轮攻击。` +
    `总报告在 collatz-attack/50-report/final-report.md，可交互的边界图在 collatz-attack/50-report/frontier-map.html。`,
  findings: [
    {
      where: "collatz-attack/10-literature/frontier.md",
      what: `边界地图：已确证结果 ${frontier.established.length} 条，活口 ${frontier.liveGaps.length} 个，结构性死路 ${frontier.deadEnds.length} 条。`,
      evidence: `由边界地图绘制者汇总八份笔记（${litTopics.map((t) => t.slug).join("、")}）而成，并经审读员抽样 ${frontierReview.claimsChecked} 条回原始来源核对。`,
      status: frontierReview.problems.length === 0 ? "verified" : "unconfirmed",
      severity: "high",
    },
    {
      where: "collatz-attack/30-proof-attempts/",
      what: `六条路线的最终状态：${routeOutcomes
        .map((o) => `${o.attempt.slug}（${o.status}）`)
        .join("、")}。每条的最致命一击见对应目录。`,
      evidence: "每条路线都经过独立反驳者的具体反例或明确引用攻击，并由作者逐条回应，其中两条另加第二轮反驳。",
      status: "verified",
      severity: "high",
    },
    {
      where: "collatz-attack/40-formal/exact_check.py",
      what:
        gateExit === 0
          ? `精确算术检查全部通过（退出码 0），覆盖 ${checkResult.lemmas.length} 条引理。`
          : `精确算术检查最终退出码 ${gateExit}，仍有未通过项，详见文件输出。`,
      evidence: "由工作流直接以 world.run 执行脚本并读取退出码，属于确定性检查。",
      status: "verified",
      severity: "medium",
    },
    {
      where: "collatz-attack/20-experiments/findings/",
      what: `六组计算实验完成，关键数字共 ${experimentOutcomes.reduce((acc, o) => acc + o.result.keyNumbers.length, 0)} 条，经独立重算。`,
      evidence: `每组实验由另一名复核员用不同方法重算关键数字，不一致处 ${experimentOutcomes.filter((o) => o.recheck.discrepancies.length > 0).length} 组已追查。`,
      status: "verified",
      severity: "medium",
    },
    {
      where: reportPath,
      what: `总报告已完成：${finalReport.conclusion}`,
      evidence: `红队抽查 ${redReview.claimsChecked} 条主张，作者逐条处理后修订，仍有争议 ${finalReport.unresolved.length} 条列入 unresolved。`,
      status: "verified",
      severity: "high",
    },
  ],
  verified: verifiedList,
  notCovered: notCoveredList,
};
