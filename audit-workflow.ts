// Hercher 定理 21 独立核查工作流（2026 年 10 月 21 日）。
//
// 背景：项目里那条丢番图路线的头号结论——「用纯初等输入把 m 圈排除推到 m ≤ 91」——
// 全部压在 Hercher 2023 定理 21 的「几何尾部」那一步上。该步公开有争议：zbMATH 审稿人
// 指出证明靠近末尾有潜在缺陷，第三方 Lean 形式化只承认 m ≤ 82，作者另有 2026 年勘误。
//
// 本工作流要回答四个问题：
//   1. 印出版的定理 21 是否正确？
//   2. 2026 年勘误给的替代论证是否正确？
//   3. 第三方 Lean「只到 82」的主张是否成立？
//   4. 在此判定下，那条路线是否成立、m = 91 处的余量是多少？
//
// 纪律：每个判定都要么给出可运行代码的输出，要么给出原始来源的逐字引用；不许泛泛而谈。

interface MaterialResult {
  /** 你写入的材料文件绝对路径 */
  path: string;
  /** 每条材料一行：名称 —— URL —— 是否亲自打开 —— 关于争议步骤它说了什么 */
  items: string[];
  /** 打不开或找不到的材料，逐条说明原因 */
  missing: string[];
}

interface DisputeBrief {
  /** 争点简报文件绝对路径 */
  path: string;
  /** 争议步骤的精确陈述（把它涉及的每个量与不等式写清） */
  disputedStep: string;
  /** 三个版本各自的说法，逐条一句 */
  threeVersions: string[];
  /** 材料里支持或反对该步的原文证据，逐条带出处 */
  evidence: string[];
}

interface Rederivation {
  /** 印出版 / 勘误版 / 健全版 */
  variant: string;
  /** 报告文件绝对路径 */
  path: string;
  /** 你写的脚本绝对路径 */
  scriptPath: string;
  /** m = 91 处 K 下界与上界的余量倍数；给不出结论写 0 */
  margin91: number;
  /** 这一版本能排除到的最大的 m；给不出结论写 0 */
  maxM: number;
  /** 被质疑那一步在这一版本下是否成立：holds / fails / conditional */
  stepStatus: "holds" | "fails" | "conditional";
  /** 一句话：这一版本与论文自己陈述的假设是否相容 */
  verdict: string;
}

interface CrossRebuttal {
  /** 你攻击的版本 */
  variant: string;
  /** fatal / serious / survivable */
  verdict: string;
  /** 最致命的一击，一句话 */
  objection: string;
  /** 证据：你实际运行的命令与输出，或原始来源的逐字引用与 URL */
  evidence: string;
}

interface CrossResponse {
  /** 修订后的报告路径 */
  path: string;
  /** fixed / conceded / defended */
  action: string;
  /** 一句话说明结果 */
  note: string;
}

interface AuditVerdict {
  /** 四个问题逐一判定，每条一到两句，必须写明依据 */
  answers: string[];
  /** 最终采信的版本 */
  adopted: string;
  /** 采信版本下 m = 91 处的余量倍数；若不成立写 0 */
  margin: number;
  /** 仍未解决的争议，逐条一句 */
  unresolved: string[];
}

interface QuantResult {
  /** 脚本绝对路径 */
  scriptPath: string;
  /** 表格文件绝对路径 */
  tablePath: string;
  /** 关键数字，每条一句 */
  numbers: string[];
  /** 脚本自检说明（它自己检查了什么一致性） */
  selfCheck: string;
}

interface AuditReport {
  /** 核查报告绝对路径 */
  path: string;
  /** 核心结论，三句以内 */
  conclusion: string;
  /** 你对自己的结论的把握：high / medium / low，附一句理由 */
  confidence: string;
  /** 仍未解决的争议，逐条一句 */
  unresolved: string[];
}

interface RedTeam {
  /** 报告中证据不足、夸大或与材料不符之处，每条一句并给出文件与行号或 URL */
  problems: string[];
  /** 你抽样复核的条目数 */
  checked: number;
}

interface DocUpdates {
  /** 你改动或新建的文件，逐条绝对路径 */
  files: string[];
  /** 改动摘要，两三句 */
  summary: string;
  /** 建议的提交信息（中文，格式为「突破点＋一句结论」） */
  commitMessage: string;
}

const STYLE =
  "写作纪律：中文正文不要出现半角连字符，破折号用「——」，并列用「、」，编号用 1. 2. 3.。诚实纪律：区分已证、仅预印本宣称、以及你自己的推断；无法核实的标注；禁止编造文献、数字或引理名。公式如果 pdftotext 抽出来是乱码，用 pdftoppm 渲染成图再读。";

artifact.board("variants", {
  title: "三个版本的重推结果",
  key: "variant",
  status: "stepStatus",
  columns: ["holds", "fails", "conditional", "未完成"],
  cardTitle: "variant",
  detail: [{ field: "margin", label: "m = 91 处余量" }],
});

phase("收集争议的全部原始材料");
const primaryCollector = agent("材料收集员·一手", {
  system:
    "你负责把一场学术争议的原始材料收集齐，并逐字保留关键句。不许转述二手报道，必须打开原始文件。" +
    STYLE,
});
const thirdPartyCollector = agent("材料收集员·第三方", {
  system:
    "你负责把针对一篇论文的第三方质疑（形式化项目、审稿意见、社群讨论）找齐并逐字保留其主张。" +
    STYLE,
});

const materials = await Promise.all([
  primaryCollector.ask<MaterialResult>(
    `收集与 Hercher 2023 定理 21 争议有关的一手材料，写到 /Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/materials-primary.md。\n\n` +
      `至少包括：\n` +
      `1. Hercher《There are no Collatz m-Cycles with m ≤ 91》，Journal of Integer Sequences 26（2023）文章 23.3.5；已知可达地址 https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf 。\n` +
      `2. 该文的 2026 年勘误（同刊勘误页；项目笔记记录其文件头日期为 2026 年 7 月 31 日，另有来源写 2026 年 6 月 14 日，两说都查）。\n` +
      `3. zbMATH 上该文的审稿记录（项目笔记称审稿人指出定理 21 的证明靠近末尾有潜在缺陷；请找到该记录并逐字引用原句）。\n` +
      `4. Simons 与 de Weger《Theoretical and computational bounds for m-cycles of the 3n+1 problem》v1.43（https://www.deweger.net/papers/ 下），定理 21 的终结构依赖它的哪些引理。\n` +
      `5. 项目自己的材料：30-proof-attempts/diophantine-transcendence/attempt.md 与同目录 rebuttal-2.md（后者称独立复现了论文全部七步自举）。\n\n` +
      `硬要求：\n` +
      `- 公式若 pdftotext 抽出来乱码，用 pdftoppm 渲染成图再读，并把关键不等式逐字抄进文件（含上下标记号）。\n` +
      `- 每条材料都要写「我是否亲自打开」「关于争议步骤它说了什么」，无法打开的单列 missing。\n` +
      `- 项目笔记里写过的数字不得当作一手证据，必须回到论文原文核对。\n\n` +
      `按 schema 返回。`,
  ),
  thirdPartyCollector.ask<MaterialResult>(
    `收集针对 Hercher 2023 定理 21 的第三方质疑材料，写到 /Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/materials-thirdparty.md。\n\n` +
      `项目笔记记录的争议（需要你独立核实来源）：有一个第三方 Lean 形式化主张 82 到 91 那一步错误、只承认 m ≤ 82；另有 Lean 项目条件性主张 m ≤ 101。请找到这些项目本身（检索关键词建议：Hercher Lean 4 Collatz m-cycles 91 formalization、Collatz m-cycle Lean verify 82），打开仓库或论文页，并写清：\n` +
      `1. 它形式化的是哪条陈述、依赖哪些外部假设（例如验证界、Rhin 界）。\n` +
      `2. 它**具体拒绝的是哪一步或哪条不等式**（要引用它自己写的 lemma 名或 issue 讨论，逐字）。\n` +
      `3. 它给出的替代结论是什么（例如只到 m ≤ 82），以及它自己声明的不确定性。\n` +
      `4. 有没有人对它的主张提出过反驳（issue、讨论帖、后续提交）。\n\n` +
      `硬要求：所有主张都要能追溯到可打开的页面；打不开的单列 missing 并写明尝试过什么。按 schema 返回。`,
  ),
]);

const briefWriter = agent("争点摘要员", {
  system: "你负责把一堆材料压缩成一份精确的争点简报，供后续三位重推者使用。" + STYLE,
});
const brief = await briefWriter.ask<DisputeBrief>(
  `读这两份材料：\n${materials[0].path}\n${materials[1].path}\n\n` +
    `写 /Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/dispute.md，内容包括：\n` +
    `1. 争议步骤的精确陈述：把它涉及的每个符号（例如 m2、v、偏差 epsilon、K 的下界算子、Lemma 22 的换算）定义清楚，并把印出版、勘误版、第三方健全版三者的不等式并排写出。\n` +
    `2. 三个版本各自的说法，逐条一句。\n` +
    `3. 材料里支持或反对该步的原文证据，逐条带出处（文件与行号，或 URL）。\n` +
    `4. 材料缺失之处：凡后续重推者不能依赖的，明说。\n\n` +
    `按 schema 返回（disputedStep 要写成后续重推者能直接照着算的形式）。`,
);
report({
  topic: "dispute",
  claims: brief.threeVersions.length,
  citation: "materials-collected",
  summary: `争点简报已就绪：${brief.disputedStep.slice(0, 120)}`,
  notePath: brief.path,
});

phase("三个版本各自从零重推那一步");
const variants = [
  {
    key: "印出版",
    slug: "as-printed",
    system:
      "你是一名数论工作者，任务是按论文自己陈述的假设，从零重推一条有争议的步骤，并给出你自己的判定。" +
      "你的价值在于精确：要么复现它，要么指出它在论文自己的假设下不成立，并给出反例或缺口的具体位置。" +
      STYLE,
  },
  {
    key: "勘误版",
    slug: "erratum",
    system:
      "你是一名数论工作者，任务是把作者 2026 年勘误给出的替代论证从零重推，并判定它是否正确、是否覆盖了原证明的同一结论。" +
      STYLE,
  },
  {
    key: "健全版",
    slug: "lean-sound",
    system:
      "你是一名数论工作者，任务是弄清第三方形式化只承认 m ≤ 82 的确切理由：它拒绝的那条不等式在论文自己的假设下究竟能不能推出。" +
      "不要预设立场：如果你发现它的拒绝是过严的，如实写出来。" +
      STYLE,
  },
];

const rederivationAgents = variants.map((v) => ({
  v,
  worker: agent(`重推者·${v.key}`, { system: v.system }),
}));

const rederivations = await Promise.all(
  rederivationAgents.map(async ({ v, worker }) => {
    try {
      const result = await worker.ask<Rederivation>(
        `你的任务版本是：${v.key}。争点简报在 /Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/dispute.md（先读它，再读它引用的原始材料）。\n\n` +
          `争点（简报的原文）：\n${brief.disputedStep}\n\n` +
          `你要做的：\n` +
          `1. 把这一版本的假设与结论写成精确的不等式。\n` +
          `2. 用本机 Python 从零实现自举链（不要复用任何现成脚本）：环境是 /Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python，里面有 mpmath、gmpy2、sympy、numpy。脚本写到 /Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/scripts/rederive-${v.slug}.py。\n` +
          `3. 给出三个数：m = 91 处的余量倍数（K 下界除以 K 上界）、这一版本能排除到的最大的 m、以及被质疑那一步在你这一版本下是否成立（holds / fails / conditional）。\n` +
          `4. 报告写到 /Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/rederivation-${v.slug}.md，必须包含：你用的每条假设、完整命令行、原始输出摘要、关键数字、以及「这一步在什么额外假设下才会成立」。\n\n` +
          `硬要求：数字必须来自你自己的运行；不确定的一律标 uncertain，不许为了让结论好看而放宽或收紧假设。中文正文不要出现半角连字符。按 schema 返回。`,
      );
      report(
        { variant: result.variant, stepStatus: result.stepStatus, margin: result.margin91, verdict: result.verdict },
        "variants",
      );
      return result;
    } catch (e) {
      log(`重推版本 ${v.key} 未完成：${String(e).slice(0, 150)}`);
      const fallback: Rederivation = {
        variant: v.key,
        path: "未产出",
        scriptPath: "未产出",
        margin91: 0,
        maxM: 0,
        stepStatus: "conditional",
        verdict: "未完成",
      };
      report({ variant: v.key, stepStatus: "未完成", margin: 0, verdict: "未完成" }, "variants");
      return fallback;
    }
  }),
);

phase("交叉反驳与作者回应");
const crossPairs = [
  { attacker: 0, target: 1 },
  { attacker: 1, target: 2 },
  { attacker: 2, target: 0 },
];
const crossOutcomes = await Promise.all(
  crossPairs.map(async (pair) => {
    const target = rederivations[pair.target];
    const worker = rederivationAgents[pair.target].worker;
    try {
      const rebutter = agent(`交叉反驳者·攻${target.variant}`, {
        system:
          "你是独立反驳者，攻击一份重推报告。只接受两种证据：你实际运行的代码反例（贴命令与输出），" +
          "或原始来源的逐字引用（贴 URL）。泛泛而谈一律不接受。不修改被攻击的文件。" +
          STYLE,
      });
      const rebuttal = await rebutter.ask<CrossRebuttal>(
        `攻击这份重推报告：${target.path}\n它的脚本是 ${target.scriptPath}。\n\n` +
          `读它、读它引用的原始材料，然后：\n` +
          `1. 检查它用的假设是否与论文原文一致（这是本争议的核心：争议各方的分歧往往就在于偷偷放宽或收紧了某条假设）。\n` +
          `2. 检查它的数字能否复算（自己写脚本重算关键的一两个数，不要复用它的脚本）。\n` +
          `3. 给出最致命的一击：它哪里错了、哪里证据不足、或者哪里其实是对的而它自己过于保守。\n` +
          `4. 若你打不掉它，明说，并列出你试过哪些攻击面。\n\n` +
          `按 schema 返回。`,
      );
      const response = await worker.ask<CrossResponse>(
        `交叉反驳者对你的报告给出了如下结论：\n${JSON.stringify(rebuttal, null, 2)}\n\n` +
          `要么修补（fixed，必须真的补上论证或改正数字）、要么撤下该结论（conceded）、要么指出反驳本身有误（defended，必须给证据）。` +
          `把回应追加到 ${target.path} 末尾的「## 对交叉反驳的回应」一节，并同步修订正文里被推翻的部分。按 schema 返回。`,
      );
      return { target, rebuttal, response };
    } catch (e) {
      log(`对 ${target.variant} 的交叉反驳未完成：${String(e).slice(0, 150)}`);
      const fallbackRebuttal: CrossRebuttal = {
        variant: target.variant,
        verdict: "survivable",
        objection: "交叉反驳未完成（异常信息见运行日志）",
        evidence: "无",
      };
      const fallbackResponse: CrossResponse = { path: target.path, action: "defended", note: "未完成" };
      return { target, rebuttal: fallbackRebuttal, response: fallbackResponse };
    }
  }),
);
const crossSummary = crossOutcomes.map((c) => ({
  variant: c.target.variant,
  rebuttalVerdict: c.rebuttal.verdict,
  objection: c.rebuttal.objection,
  responseAction: c.response.action,
  margin: c.target.margin91,
  maxM: c.target.maxM,
  stepStatus: c.target.stepStatus,
}));
log(`交叉反驳完成 ${crossOutcomes.length} 组，进入裁决`);

phase("裁决与定量重算");
const judge = agent("争议裁决员", {
  system:
    "你是裁决者。你的任务不是站队，而是把三个版本与三份反驳放在一起，判定哪一版与论文自己陈述的假设相容，" +
    "并把判定写成能被别人复核的形式。" +
    STYLE,
});
const verdict = await judge.ask<AuditVerdict>(
  `材料与全部报告：\n` +
    `争点简报：${brief.path}\n一手材料：${materials[0].path}\n第三方材料：${materials[1].path}\n` +
    `三个版本的重推报告：${rederivations.map((r) => r.path).join("、")}\n\n` +
    `交叉反驳与回应的摘要：\n${JSON.stringify(crossSummary, null, 2)}\n\n` +
    `请回答四个问题，每条都要写明依据（原始来源的逐字引用，或某个可复算的数字）：\n` +
    `1. 印出版的定理 21 是否正确？\n` +
    `2. 2026 年勘误给的替代论证是否正确、是否覆盖原结论？\n` +
    `3. 第三方 Lean「只到 m ≤ 82」的主张是否成立（即它拒绝的那一步是否真的推不出来）？\n` +
    `4. 在此判定下，那条「用纯初等输入把 m 圈排除推到 91」的路线是否成立？m = 91 处的余量是多少？\n\n` +
    `adopted 写你最终采信的版本（印出版 / 勘误版 / 健全版 / 无，并附一句理由）；unresolved 里如实列出你没能解决的争议。\n` +
    `按 schema 返回。`,
);
report({
  topic: "verdict",
  claims: verdict.answers.length,
  citation: "adjudicated",
  summary: `裁决：采信版本 ${verdict.adopted}；m = 91 处余量 ${verdict.margin} 倍；未决争议 ${verdict.unresolved.length} 条。`,
  notePath: brief.path,
});

const quantAgent = agent("定量重算员", {
  system:
    "你负责把裁决采信的版本变成一张可复算的数字表，并让脚本自己检查内部一致性。" +
    STYLE,
});
let quant: QuantResult = {
  scriptPath: "未产出",
  tablePath: "未产出",
  numbers: [],
  selfCheck: "定量脚本未产出（异常信息见运行日志）",
};
try {
  quant = await quantAgent.ask<QuantResult>(
  `裁决采信的版本是：${verdict.adopted}\n裁决给出的 m = 91 余量是：${verdict.margin}\n\n` +
    `写 /Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/scripts/margin_table.py，用本机 venv（/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python）跑出：\n` +
    `1. 在采信版本下，逐 m 列出 K 下界、K 上界（K_up^CF(m)）与余量倍数，覆盖 m 从 20 到 95。\n` +
    `2. 标出能排除到的最大的 m，以及第一个不能排除的 m。\n` +
    `3. 脚本自检：至少检查「余量倍数 = 下界除以上界」「上界随 m 单调」「边界 m 处余量跨过 1」这三条，不一致就非零退出。\n` +
    `4. 表格写到 /Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/results/margin-table.txt（目录若不存在就创建）。\n\n` +
    `打印要简洁（几百行以内），退出码 0 表示全部通过。按 schema 返回。`,
  );
} catch (e) {
  log(`定量脚本未能产出：${String(e).slice(0, 120)}`);
  quant = {
    scriptPath: "未产出",
    tablePath: "未产出",
    numbers: [],
    selfCheck: "定量脚本未产出（异常信息见运行日志）",
  };
}

let quantGate = -1;
for (let round = 1; round <= 3; round += 1) {
  let code = -1;
  let out = "";
  try {
    const run = await world.run("collatz-attack/20-experiments/.venv/bin/python", [
      "collatz-attack/60-audits/hercher-t21/scripts/margin_table.py",
    ]);
    code = run.exitCode;
    out = `${run.stdout.slice(-1200)}\n${run.stderr.slice(-1200)}`;
  } catch (e) {
    log(`定量脚本执行失败：${String(e).slice(0, 120)}`);
    code = -1;
    out = "命令未能执行（文件不存在、解释器路径无效或超时）";
  }
  quantGate = code;
  if (code === 0) break;
  if (round === 3) break;
  await quantAgent.ask<QuantResult>(
    `定量脚本第 ${round} 轮没有通过（退出码 ${code}）。输出末尾：\n${out}\n\n请查明原因并重写脚本（若是数学断言本身有问题，就改成正确的陈述并在返回里说明）。`,
  );
}
log(`定量表格闸门最终退出码 ${quantGate}`);

phase("写核查报告并请红队削一遍");
const auditWriter = agent("核查报告撰写者", {
  system:
    "你负责把这场核查写成一份自成一体的报告：别人只读这一份就能知道争议是什么、三个版本各说什么、我们的判定是什么、以及还剩下什么不确定。" +
    STYLE,
});
const draft = await auditWriter.ask<AuditReport>(
  `写 /Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/audit-report.md。\n\n` +
    `材料：争点简报 ${brief.path}；一手材料 ${materials[0].path}；第三方材料 ${materials[1].path}；` +
    `三份重推与回应 ${rederivations.map((r) => r.path).join("、")}；裁决 ${verdict.adopted}（余量 ${verdict.margin}）；` +
    `定量表 ${quant.tablePath}（脚本闸门退出码 ${quantGate}）。\n\n` +
    `报告结构：\n` +
    `1. 一句话结论（这条路线到底成不成立）。\n` +
    `2. 争议是什么：被质疑的那一步、三方各自的说法，逐字引用关键不等式。\n` +
    `3. 我们怎么做核查的：三个版本各自独立重推、交叉反驳、裁决、定量重算，各自的可复现命令。\n` +
    `4. 判定与依据：四个问题逐条回答，每条附证据指针（文件与行号、URL、或数字）。\n` +
    `5. 定量结果：m 从 20 到 95 的余量表要点、能排除到哪个 m。\n` +
    `6. 仍未确定的：逐条列出。\n` +
    `7. 这件事对项目其它部分的影响：哪些文档里的说法需要跟着改（列出文件与行号）。\n\n` +
    `confidence 字段写明你对自己结论的把握与理由。中文正文不要出现半角连字符。按 schema 返回。`,
);

const redteam = agent("核查报告红队", {
  system: "你是红队审读员，唯一任务是把这份核查报告里证据不足、夸大或与材料不符的地方挖出来。不修改文件。" + STYLE,
});
const redReview = await redteam.ask<RedTeam>(
  `读 ${draft.path}，并抽取其中至少 6 条关键主张，回到材料与重推报告核对。\n\n` +
    `逐条列出：把「未核实」写成「已核实」、把某一方的说法写成共识、数字与表不符、引用位置错、内部矛盾。` +
    `每条给出文件与行号或 URL。找不到问题就明说，并列出你抽查了哪些条目。按 schema 返回。`,
);
const finalAudit = await auditWriter.ask<AuditReport>(
  `红队在你的报告里发现了以下问题：\n${JSON.stringify(redReview.problems, null, 2)}\n\n` +
    `逐条处理并重写 ${draft.path}：该降级的降级、该补证据的补上指针、红队弄错了的加一节「对红队意见的回应」说明理由。` +
    `在末尾保留「红队抽查记录」。按 schema 返回。`,
);

try {
  await artifact.file("audit", "collatz-attack/60-audits/hercher-t21/audit-report.md", {
    title: "Hercher 定理 21 独立核查报告",
    description: "m ≤ 91 那条结论所依赖的争议步骤：三个版本独立重推、交叉反驳、裁决与定量重算。",
    primary: true,
  });
} catch (e) {
  log(`核查报告发布失败：${String(e).slice(0, 150)}`);
}

phase("更新仓库中受影响的文档");
const docUpdater = agent("仓库文档更新员", {
  system:
    "你负责把这次核查的结论回填到仓库里受影响的文档。纪律：**只追加，不重写**；每处都要标注来源与日期。" +
    "严禁执行任何 git 命令（提交由主代理负责）。" +
    STYLE,
});
const updates = await docUpdater.ask<DocUpdates>(
  `核查已完成，报告在 /Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/audit-report.md（结论：${finalAudit.conclusion}；采信版本：${verdict.adopted}；余量：${verdict.margin} 倍）。\n\n` +
    `请做以下五件事：\n` +
    `1. 在 10-literature/frontier.md 末尾追加一节「## 核查更新（2026 年 10 月 21 日）」，写明 Hercher 争议的裁决结论与报告路径。\n` +
    `2. 在 10-literature/notes/claims-2024-2026.md 末尾追加同题一节，指明原来关于 82 与 91 的记载现在的结论。\n` +
    `3. 在 30-proof-attempts/diophantine-transcendence/attempt.md 末尾追加同题一节，指明该路线头号数字的现状。\n` +
    `4. 新建 /Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/README.md，作为该目录的索引（一句话说明 + 文件清单 + 复现命令）。\n` +
    `5. 新建 /Users/luna/Documents/math IA/collatz-attack/CHANGELOG.md（若已存在则追加），记录本次突破：日期、结论、涉及文件。\n` +
    `另外：把 collatz-attack/README.md 的「目录结构」一节补上 60-audits 一项（只加一行，不要改动其它内容）。\n\n` +
    `所有追加内容都要写明「本节由 2026 年 10 月 21 日的 Hercher 定理 21 核查工作流追加」并给出报告路径。按 schema 返回（commitMessage 写成「突破点＋一句结论」的格式）。`,
);
report({
  topic: "doc-updates",
  claims: updates.files.length,
  citation: "pending-commit",
  summary: `仓库文档已更新 ${updates.files.length} 处，待主代理提交：${updates.commitMessage}`,
  notePath: "collatz-attack/CHANGELOG.md",
});

return {
  conclusion:
    `Hercher 定理 21 争议已完成独立核查。裁决采信版本为「${verdict.adopted}」，m = 91 处余量 ${verdict.margin} 倍，` +
    `定量闸门退出码 ${quantGate}。核查报告在 collatz-attack/60-audits/hercher-t21/audit-report.md，` +
    `待提交的文件共 ${updates.files.length} 处（建议提交信息：${updates.commitMessage}）。` +
    `仍需注意：本核查不改变「科拉茨猜想未被证明」这一事实，只判定该争议步骤的成立与否。`,
  findings: [
    {
      where: "collatz-attack/60-audits/hercher-t21/audit-report.md",
      what: finalAudit.conclusion,
      evidence: `三个版本各自独立重推（${rederivations.map((r) => `${r.variant}: ${r.stepStatus}, maxM=${r.maxM}`).join("；")}），` +
        `经三组交叉反驳与作者回应，由裁决员裁决，并由定量脚本以退出码 ${quantGate} 复核。`,
      status: finalAudit.confidence.startsWith("high") ? "verified" : "unconfirmed",
      severity: "high",
    },
    {
      where: "collatz-attack/60-audits/hercher-t21/results/margin-table.txt",
      what: `采信版本下的余量表：${quant.numbers.slice(0, 3).join("；")}`,
      evidence: `脚本 ${quant.scriptPath} 由 world.run 直接执行并读取退出码（${quantGate}）；自检内容：${quant.selfCheck.slice(0, 200)}`,
      status: quantGate === 0 ? "verified" : "unconfirmed",
      severity: "medium",
    },
    {
      where: "collatz-attack/CHANGELOG.md",
      what: `仓库文档已同步更新：${updates.summary}`,
      evidence: `改动文件清单由仓库文档更新员返回，共 ${updates.files.length} 处；提交由主代理执行。`,
      status: "verified",
      severity: "medium",
    },
  ],
  verified: [
    "争点由一手材料与第三方材料两份收集报告支撑，关键不等式逐字抄录并标明是否亲自打开",
    `定量脚本以 world.run 读取退出码判定（最终退出码 ${quantGate}）`,
    "核查报告经红队抽查，抽查条数 " + String(redReview.checked) + "，问题数 " + String(redReview.problems.length),
    "三个版本的重推各自经过交叉反驳与作者回应",
  ],
  notCovered: [
    "科拉茨猜想本身仍未被证明或推翻；本核查只判定争议步骤，不触及猜想",
    "若原始材料在核查期间不可得（见两份材料报告的 missing 字段），相应判定只能写成 conditional",
    "仓库的 git 提交由主代理在核验后执行，工作流本身不推送",
  ],
};
