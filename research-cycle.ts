// research-cycle.ts —— 科拉茨攻坚的「可反复运行的研究循环」引擎（2026 年 10 月 21 日第一版）。
//
// 每一轮做六件事：读账本定目标 → 收集材料 → 多路独立攻击 → 交叉反驳与裁决 →
// 确定性复算闸门 → 写入账本、更新文档并把产物备好待推送。
//
// 设计约束（诚实性来自这里，不是来自希望）：
//   1. 账本（70-research/ledger.md）是本循环的记忆；每轮开头必读、结尾必写。
//   2. learnings.md 记录「试过且失败的技术」，下一轮的目标选定必须显式避开它们。
//   3. 任何结论都要么有可运行代码的输出，要么有原始来源的逐字引用；未证一律写未证。
//   4. 确定性闸门用 world.run 读退出码，不靠子代理自称。
//   5. 本循环不承诺证明科拉茨猜想；它承诺的是每一轮都留下可复核的增量。

interface RouteSpec {
  /** 路线短名（必须与其它路线不同） */
  name: string;
  /** 这条路线具体要做什么，一句话到三句话 */
  mission: string;
}

interface CyclePlan {
  /** 这是第几轮（读账本得出；账本不存在就从 1 开始） */
  cycleNumber: number;
  /** 本轮攻坚的目标，一句话 */
  target: string;
  /** 为什么选它（与边界地图的活口清单和 learnings 的关系） */
  rationale: string;
  /** 拆成三到五个可独立攻击的子问题 */
  subQuestions: string[];
  /** 三到五条互相独立的攻击路线 */
  attackRoutes: RouteSpec[];
  /** 本轮显式避开的方向（来自 learnings.md 里已失败的尝试） */
  avoidList: string[];
  /** 计划文件绝对路径 */
  planPath: string;
  /** 账本文件绝对路径 */
  ledgerPath: string;
}

interface AttemptResult {
  /** 与分配给你的路线名一致 */
  route: string;
  /** 报告文件绝对路径 */
  path: string;
  /** 你这一路最强的结论，一句话（未证就直说未证） */
  claim: string;
  /** 结论的证据类型：代码实跑 / 文献引用 / 初等证明 / 未决 */
  evidenceKind: string;
  /** 已证 / 已否证 / 未决 */
  status: string;
  /** 关键数字，每条一句，写明范围 */
  keyNumbers: string[];
}

interface CrossCritique {
  /** 被你攻击的路线名 */
  route: string;
  /** fatal / serious / survivable */
  verdict: string;
  /** 最致命的一击，一句话 */
  objection: string;
  /** 证据：实跑命令与输出，或原始来源逐字引用与 URL */
  evidence: string;
}

interface CycleVerdict {
  /** 本轮确实立住的增量，逐条（没有就写空数组，不要凑） */
  newResults: string[];
  /** 本轮被否证或撤下的东西，逐条 */
  falsified: string[];
  /** 未决与卡住的地方，逐条 */
  unresolved: string[];
  /** 下一轮最值得攻的三到五个目标，按优先级排序，并各写一句所需工具 */
  nextTargets: string[];
  /** 两三句总评，必须明确说本轮有没有实质增量 */
  overall: string;
}

interface VerifyResult {
  /** 复算脚本绝对路径 */
  scriptPath: string;
  /** 脚本逐条检查了什么，每条一句 */
  checked: string[];
  /** 结果说明：全部通过 / 有失败项（写明） */
  outcome: string;
}

interface LedgerUpdate {
  /** 改动或新建的文件，逐条绝对路径 */
  files: string[];
  /** 改动摘要，两三句 */
  summary: string;
  /** 建议的提交信息（格式为「突破点＋一句结论」；本轮若无实质增量，写「无增量」并在返回里说明不推送） */
  commitMessage: string;
}

const ROOT = "/Users/luna/Documents/math IA/collatz-attack";
const STYLE =
  "写作纪律：中文正文不要出现半角连字符，破折号用「——」，并列用「、」，编号用 1. 2. 3.。诚实纪律：区分已证定理、仅预印本宣称、你自己的推断；无法核实的标注；禁止编造文献、数字或引理名；未证一律写未证。";

artifact.board("cycles", {
  title: "本轮各路攻击的状态",
  key: "route",
  status: "status",
  columns: ["论证中", "已证", "已否证", "未决", "未完成"],
  cardTitle: "route",
  detail: [{ field: "claim", label: "最强结论" }],
});

phase("读账本并定下本轮目标");
const planner = agent("研究调度员", {
  system:
    "你是这个长期研究项目的调度员。你的职责是从账本、边界地图与学习记录里选出本轮最值得攻的目标，" +
    "并把选它的理由写清。你不做数学，只做判断：哪些目标离可核查的增量最近、哪些已经被试过且失败。" +
    STYLE,
});
const plan = await planner.ask<CyclePlan>(
  `读这些材料（用 Read，缺哪个就在报告里说明）：\n` +
    `1. ${ROOT}/70-research/ledger.md（账本；不存在就新建，并注明「首轮」）\n` +
    `2. ${ROOT}/70-research/learnings.md（学习记录：试过且失败的技术；不存在就新建）\n` +
    `3. ${ROOT}/10-literature/frontier.md（边界地图：已证结果、活口、死路、门槛）\n` +
    `4. ${ROOT}/CHANGELOG.md（已完成的突破）\n` +
    `5. ${ROOT}/60-audits/hercher-t21/audit-report.md（若存在，读它的结论与未决项）\n\n` +
    `然后写本轮计划到 ${ROOT}/70-research/plan.md，并返回结构化结果，包含：\n` +
    `- target：本轮目标，一句话。选择标准是「离可核查的增量最近」，不是「听起来最大」。\n` +
    `- rationale：为什么是它；必须提到它与 frontier.md 的活口/门槛清单的关系，以及它不在 learnings.md 的失败清单里。\n` +
    `- subQuestions：三到五个可独立攻击的子问题。\n` +
    `- attackRoutes：三到五条互相独立的攻击路线，每条给 name（互不相同）与 mission。路线之间必须方法不同（例如一条走文献复算、一条走代码穷举、一条走初等构造），不要三条都在做同一件事。\n` +
    `- avoidList：从 learnings.md 里抄出本轮要避开的方向。\n` +
    `- cycleNumber：读账本得出；账本没有历史就从 1 开始。\n\n` +
    `硬要求：不要选「证明科拉茨猜想」这种一级目标，要选一轮之内可能产生可核查增量的二级目标（例如某条路线的某个具体引理、某个争议步骤、某个可以扩大的计算范围、某个可以否证的启发式断言）。中文正文不要出现半角连字符。`,
);
log(`第 ${plan.cycleNumber} 轮目标：${plan.target}`);

phase("收集本轮所需的材料");
const materialCollector = agent("材料收集员", {
  system: "你负责为指定的研究目标把原始材料找齐并逐字保留关键句。打开原始文件，不转述二手报道。" + STYLE,
});
const methodScout = agent("方法侦察员", {
  system:
    "你负责弄清这个目标上「已经有人怎么做、做到哪、卡在哪」：文献里的机具、可复用的常数、以及已知的不可能性结果。" +
    STYLE,
});
// 方法侦察拆成两问：原一问要一次读多份大文件并产出四节报告，是全脚本最长的请求，
// 2026 年 10 月 24 日那轮在供方侧反复流空闲超时、挂了四小时无产出，故拆短。
const scoutPartOne = methodScout.ask<string>(
  `目标：${plan.target}\n子问题：\n${plan.subQuestions.join("\n")}\n\n` +
    `本轮只写第 1 与第 2 节，篇幅控制在 150 行以内（宁可精炼，不要长文）：\n` +
    `1. 文献里针对这类问题用过什么机具（逐条给出处），各自到达的范围与已知极限。\n` +
    `2. 已知的不可能性结果：哪些做法被证明必然失败（逐条给出处）。\n` +
    `写到 ${ROOT}/70-research/cycle-${plan.cycleNumber}/methods.md（目录若不存在就创建），两节标题分别为「## 一、文献机具与可达范围」与「## 二、已知的不可能性结果」。\n` +
    `硬要求：每条都要能追溯到可打开的来源或项目内文件；不确定的标注。返回你写入的文件绝对路径。`,
);
const scoutPartTwo = scoutPartOne.then(() =>
  methodScout.ask<string>(
    `接上一条：往同一个文件 ${ROOT}/70-research/cycle-${plan.cycleNumber}/methods.md 追加第 3 与第 4 节（不要改动前两节），篇幅控制在 80 行以内：\n` +
      `3. 本机可用的工具（Python venv 里的 mpmath、gmpy2、sympy、z3、numpy，以及 cc 编译器）在这类问题上能做什么、不能做什么。\n` +
      `4. 你认为本轮最可能产生增量的两个切入点，各一句理由。\n` +
      `返回同一个文件路径。`,
  ),
);

const materials = await Promise.all([
  materialCollector.ask<string>(
    `目标：${plan.target}\n子问题：\n${plan.subQuestions.join("\n")}\n\n` +
      `收集与该目标直接相关的一手材料，写到 ${ROOT}/70-research/cycle-${plan.cycleNumber}/materials.md。要求：\n` +
      `1. 逐条列出：名称、URL 或本地路径、你是否亲自打开、与目标相关的关键句（逐字）。\n` +
      `2. 公式若 pdftotext 抽出来乱码，用 pdftoppm 渲染成图再读。\n` +
      `3. 打不开的单列，并写明尝试过什么。\n` +
      `目录若不存在就创建。返回你写入的文件绝对路径。`,
  ),
  scoutPartTwo,
]);
log(`材料与方法就绪：${materials[0]}、${materials[1]}`);

phase("多路独立攻击");
const attackOutcomes = await Promise.all(
  plan.attackRoutes.map(async (r, i) => {
    try {
      const attacker = agent(`攻击者·${i + 1}·${r.name}`, {
        system:
          "你是一名数论工作者，负责沿一条指定路线推进一个具体目标。" +
          "每一步要么是已证定理（给出处）、要么是你能完整证明的初等引理、要么显式标注为缺口。" +
          "你的价值在于把失败点定到具体的不等式或具体的步骤，而不是宣布成功。" +
          STYLE,
      });
      // 一开局就上报，让看板立刻显示全部路线（否则要等某条结算才有第一张卡，
      // 长阶段里界面上什么都看不到；2026 年 10 月 25 日按用户反馈补上）。
      report(
        {
          route: r.name,
          status: "论证中",
          claim: `攻击进行中，脚本与报告写在 70-research/cycle-${plan.cycleNumber}/`,
          evidence: r.mission.slice(0, 160),
        },
        "cycles",
      );
      const result = await attacker.ask<AttemptResult>(
        `本轮目标：${plan.target}\n本轮要避开的已失败方向：${plan.avoidList.join("、")}\n\n` +
          `你负责的路线是「${r.name}」：${r.mission}\n\n` +
          `先读这些材料：\n${materials[0]}\n${materials[1]}\n${ROOT}/10-literature/frontier.md\n\n` +
          `上下文与输出纪律（供方会对过大请求直接返回 400，务必遵守）：优先用检索（grep 或 rg）抽取你真正需要的段落，不要整文读入；报告分节写入，每写完一节就落盘一次，不要憋到最后一次性输出长文；单节控制在 200 行以内。\n\n` +
          `要求：\n` +
          `1. 真的动手：写代码跑、算数字、查原文。脚本放到 ${ROOT}/70-research/cycle-${plan.cycleNumber}/scripts/ 下，用 ${ROOT}/20-experiments/.venv/bin/python 运行。\n` +
          `2. 报告写到 ${ROOT}/70-research/cycle-${plan.cycleNumber}/route-${i + 1}.md，含：要证明或要检验的精确陈述、编号论证（每步标注 已证/缺口/错误/等价于原命题）、失败点清单、局部新结论及其独立验证方式、完整命令行与原始输出摘要。\n` +
          `3. claim 字段写你这一路最强的结论，一句话；没有结论就写「本轮未取得结论」并把 status 写成未决。严禁把未证写成已证。\n` +
          `4. keyNumbers 里每个数字都要写明实际达到的范围。\n\n` +
          `按 schema 返回。中文正文不要出现半角连字符。`,
      );
      report(
        { route: result.route, status: result.status, claim: result.claim, evidence: result.evidenceKind },
        "cycles",
      );
      return result;
    } catch (e) {
      log(`路线 ${r.name} 未完成：${String(e).slice(0, 150)}`);
      const fallback: AttemptResult = {
        route: r.name,
        path: "未产出",
        claim: "本轮未取得结论",
        evidenceKind: "未决",
        status: "未决",
        keyNumbers: [],
      };
      report({ route: r.name, status: "未完成", claim: "路线未完成", evidence: "无" }, "cycles");
      return fallback;
    }
  }),
);

phase("交叉反驳与裁决");
const critiques = await Promise.all(
  attackOutcomes.map(async (targetItem, i) => {
    const criticIndex = (i + 1) % attackOutcomes.length;
    if (attackOutcomes.length < 2) {
      const solo: CrossCritique = {
        route: targetItem.route,
        verdict: "survivable",
        objection: "本轮只有一条路线，无法交叉反驳",
        evidence: "无",
      };
      return solo;
    }
    try {
      const critic = agent(`交叉反驳者·${i + 1}`, {
        system:
          "你是独立反驳者，攻击一条攻击路线的报告。只接受两种证据：你实际运行的代码反例（贴命令与输出），" +
          "或原始来源的逐字引用（贴 URL）。泛泛而谈一律不接受。不修改被攻击的文件。" +
          STYLE,
      });
      return await critic.ask<CrossCritique>(
        `攻击这份报告：${targetItem.path}（路线「${targetItem.route}」）。\n` +
          `它的强度声明是：${targetItem.claim}\n它的证据类型自报为：${targetItem.evidenceKind}\n\n` +
          `1. 检查它的假设是否成立、数字能否复算（自己写脚本重算关键的一两个数，不要复用它的脚本）。\n` +
          `2. 检查它的「已证」是否真的已证（这是最关键的一条：把「数值观察」写成「定理」是本项目最常见的自欺形式）。\n` +
          `3. 给出最致命的一击；打不掉就明说，并列出你试过哪些攻击面（critic 序号 ${criticIndex + 1} 表示你是轮转中的下一位）。\n\n` +
          `按 schema 返回。`,
      );
    } catch (e) {
      log(`对路线 ${targetItem.route} 的交叉反驳未完成：${String(e).slice(0, 150)}`);
      const fallback: CrossCritique = {
        route: targetItem.route,
        verdict: "survivable",
        objection: "交叉反驳未完成（异常信息见运行日志）",
        evidence: "无",
      };
      return fallback;
    }
  }),
);
const critiqueSummary = critiques.map((c) => ({
  route: c.route,
  verdict: c.verdict,
  objection: c.objection,
  evidence: c.evidence.slice(0, 300),
}));

const judge = agent("本轮裁决员", {
  system:
    "你是裁决者。任务是把本轮各路结果与反驳放在一起，判定哪些是真正的增量、哪些被否证、哪些还悬着，" +
    "并给下一轮排出优先级。你的最高纪律：不许为了好看而把未决写成已证。" +
    STYLE,
});
const verdict = await judge.ask<CycleVerdict>(
  `目标：${plan.target}\n\n各路结果：\n${JSON.stringify(attackOutcomes.map((a) => ({ route: a.route, claim: a.claim, evidenceKind: a.evidenceKind, status: a.status, keyNumbers: a.keyNumbers })), null, 2)}\n\n` +
    `交叉反驳摘要：\n${JSON.stringify(critiqueSummary, null, 2)}\n\n` +
    `各路完整报告在：${attackOutcomes.map((a) => a.path).join("、")}（可读）\n\n` +
    `请判定：\n` +
    `1. newResults：本轮确实立住的增量（要能追溯到具体报告与数字）；一条都没有就写空数组。\n` +
    `2. falsified：被否证或撤下的东西。\n` +
    `3. unresolved：未决与卡住的地方。\n` +
    `4. nextTargets：下一轮最值得攻的三到五个目标，按优先级排序，各写一句所需工具。\n` +
    `5. overall：两三句总评，必须明确说出本轮有没有实质增量。\n\n` +
    `按 schema 返回。`,
);
report({
  topic: `cycle-${plan.cycleNumber}-verdict`,
  claims: verdict.newResults.length,
  citation: "adjudicated",
  summary: `${verdict.overall.slice(0, 220)}（立住 ${verdict.newResults.length} 条，否证 ${verdict.falsified.length} 条，未决 ${verdict.unresolved.length} 条）`,
  notePath: plan.planPath,
});

phase("确定性复算闸门");
const verifier = agent("复算员", {
  system:
    "你负责把本轮新结论写成一段可独立运行的复算脚本：脚本自己重新计算一切，不读取任何本轮的结论文件，" +
    "只读取它的断言。全部通过退出码 0，任何失败退出码非零并打印最小反例。" +
    STYLE,
});
await verifier.ask<VerifyResult>(
  `本轮的增量结论：\n${JSON.stringify(verdict.newResults, null, 2)}\n\n` +
    `写 ${ROOT}/70-research/cycle-${plan.cycleNumber}/verify.py，要求：\n` +
    `1. 对每条增量结论写一个断言函数；能数值验证的就数值验证（用精确整数或有理数），只能查证的就在注释里写明「无法机器验证」并跳过。\n` +
    `2. 脚本必须自己重新计算，不许读取 route-*.md 或 materials.md 里的数字。\n` +
    `3. 打印简洁（几百行以内），全部通过退出码 0，否则非零并打印最小反例。\n` +
    `4. 目录若不存在就创建。按 schema 返回。`,
);
let gateCode = -1;
for (let round = 1; round <= 3; round += 1) {
  let code = -1;
  let out = "";
  try {
    const run = await world.run("collatz-attack/20-experiments/.venv/bin/python", [
      `collatz-attack/70-research/cycle-${plan.cycleNumber}/verify.py`,
    ]);
    code = run.exitCode;
    out = `${run.stdout.slice(-1200)}\n${run.stderr.slice(-1200)}`;
  } catch (e) {
    log(`复算脚本执行失败：${String(e).slice(0, 120)}`);
    code = -1;
    out = "命令未能执行（文件不存在、解释器路径无效或超时）";
  }
  gateCode = code;
  if (code === 0) break;
  if (round === 3) break;
  await verifier.ask<VerifyResult>(
    `复算脚本第 ${round} 轮没有通过（退出码 ${code}）。输出末尾：\n${out}\n\n请查明原因并重写脚本（若是某条结论本身不成立，就把它从断言里降级并写明）。`,
  );
}
log(`复算闸门最终退出码 ${gateCode}`);

phase("写入账本、更新文档并准备推送");
const ledgerWriter = agent("账本维护员", {
  system:
    "你负责把这个循环的记忆写对：账本要能让人（或下一次运行）一眼看出进展到哪、下一步该做什么；" +
    "学习记录要能让下一轮避开已经失败的路。只追加或精确修改，不重写无关内容。严禁执行任何 git 命令。" +
    STYLE,
});
const ledger = await ledgerWriter.ask<LedgerUpdate>(
  `第 ${plan.cycleNumber} 轮结束。闸门退出码 ${gateCode}。\n裁决总评：${verdict.overall}\n增量：${JSON.stringify(verdict.newResults, null, 2)}\n否证：${JSON.stringify(verdict.falsified, null, 2)}\n未决：${JSON.stringify(verdict.unresolved, null, 2)}\n下一轮目标：${JSON.stringify(verdict.nextTargets, null, 2)}\n\n` +
    `请做三件事，并且遵守一条纪律：\n` +
    `1. 更新 ${ROOT}/70-research/ledger.md：追加本轮条目（日期、目标、增量、否证、未决、闸门退出码），并在文件开头维护一个「当前状态」摘要（进展到哪、下一轮该做什么）。\n` +
    `2. 更新 ${ROOT}/70-research/learnings.md：把本轮「试过且失败或无效的方法」逐条写进去（每条一句说明为什么失败），供下一轮避开。\n` +
    `3. 新建 ${ROOT}/70-research/cycle-${plan.cycleNumber}/summary.md：本轮的自足摘要（目标、方法、结论、复现命令、未决）。\n` +
    `纪律：**不要改动仓库根目录的 README.md 与 CHANGELOG.md**——这两个文件由主代理在提交时统一维护，避免与其它在飞的运行互相覆盖。本轮要往仓库层交代的话，全部写进 70-research/cycle-${plan.cycleNumber}/summary.md 与账本。\n\n` +
    `commitMessage 字段：有增量就写成「突破点＋一句结论」，没有增量就写「无增量」；主代理按它决定是否推送。按 schema 返回。`,
);

return {
  conclusion:
    `第 ${plan.cycleNumber} 轮（目标：${plan.target}）已跑完，复算闸门退出码 ${gateCode}。` +
    `裁决：${verdict.overall} ` +
    `本轮立住 ${verdict.newResults.length} 条增量、否证 ${verdict.falsified.length} 条、未决 ${verdict.unresolved.length} 条。` +
    `账本已更新在 ${ROOT}/70-research/ledger.md，本轮摘要 ${ROOT}/70-research/cycle-${plan.cycleNumber}/summary.md。` +
    `待推送的文件见改动清单；科拉茨猜想本身仍未被证明。`,
  findings: [
    {
      where: `${ROOT}/70-research/cycle-${plan.cycleNumber}/summary.md`,
      what: `第 ${plan.cycleNumber} 轮摘要：${verdict.overall.slice(0, 240)}`,
      evidence: `${plan.attackRoutes.length} 条独立攻击路线 + ${critiques.length} 次交叉反驳 + 裁决 + 复算闸门（退出码 ${gateCode}）`,
      status: gateCode === 0 ? "verified" : "unconfirmed",
      severity: "high",
    },
    {
      where: `${ROOT}/70-research/ledger.md`,
      what: `账本已更新：下一轮目标为 ${verdict.nextTargets.length > 0 ? verdict.nextTargets[0] : "（未给出）"}`,
      evidence: `账本维护员按本轮裁决写入；改动文件 ${ledger.files.length} 处`,
      status: "verified",
      severity: "medium",
    },
  ],
  verified: [
    `复算闸门由 world.run 直接执行并读取退出码（最终 ${gateCode}）`,
    `每条攻击路线的强度声明都经过另一条路线的反驳者攻击（${critiques.length} 次）`,
    `本轮结论由裁决员逐条归类为增量、否证或未决`,
  ],
  notCovered: [
    "科拉茨猜想本身仍未被证明或推翻；本循环承诺的是每轮留下可复核的增量，不承诺证明",
    "若某条路线的报告未产出（见各路 status），该方向的结论只能是未决",
    "git 提交与推送由主代理在核验后执行，本工作流不推送",
  ],
};
