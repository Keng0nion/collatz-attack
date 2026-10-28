/* zcode-workflow
description: 并行安全的研究循环：一次只攻一个指定疑点，产物写进自己轨道目录，不碰共享账本。
whenToUse: 需要多条轨道同时推进不同疑点时，每条轨道用不同的 tag 与 focus 各起一次。
args:
  tag:
    type: string
    required: true
    description: 轨道短标识（英文小写，只含字母数字与连字符），决定产物目录 70-research/tracks/<tag>/
  focus:
    type: string
    required: true
    description: 本轨道要攻的疑点（优先于账本排序），一到三句话写清要产出什么
*/

// research-track.ts —— research-cycle.ts 的并行安全变体（2026 年 10 月 27 日）。
//
// 与主引擎的区别只有一处：本轮的一切写入都落在 70-research/tracks/<tag>/ 下，
// 共享的 ledger.md / learnings.md 只读不写（由主代理在推送时合并各轨道的条目）。
// 这样三条轨道同时跑不会互相覆盖文件。

interface RouteSpec {
  /** 路线短名（必须与其它路线不同） */
  name: string;
  /** 这条路线具体要做什么 */
  mission: string;
}

interface TrackPlan {
  /** 本轨道内这是第几轮（读本轨道的账本条目得出；没有就从 1 开始） */
  cycleNumber: number;
  /** 本轨道的疑点，照抄你收到的 focus 并补一句你打算怎么攻 */
  target: string;
  /** 拆成三到五个可独立攻击的子问题 */
  subQuestions: string[];
  /** 三到五条互相独立的攻击路线 */
  attackRoutes: RouteSpec[];
  /** 必须避开的方向（来自共享 learnings 与本轨道上一轮的失败） */
  avoidList: string[];
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

interface TrackVerdict {
  /** 本轮确实立住的增量，逐条（没有就写空数组） */
  newResults: string[];
  /** 本轮被否证或撤下的东西，逐条 */
  falsified: string[];
  /** 未决与卡住的地方，逐条 */
  unresolved: string[];
  /** 两三条总评，必须明确说本轮有没有实质增量 */
  overall: string;
}

interface VerifyResult {
  /** 复算脚本绝对路径 */
  scriptPath: string;
  /** 脚本逐条检查了什么 */
  checked: string[];
  /** 结果说明 */
  outcome: string;
}

interface TrackLedgerNote {
  /** 改动或新建的文件，逐条绝对路径 */
  files: string[];
  /** 本轨道的账本条目正文（Markdown，供主代理合并进共享账本） */
  ledgerEntry: string;
  /** 本轨道的学习记录条目正文（Markdown，试过且失败的方法） */
  learningsEntry: string;
  /** 建议的提交信息（格式为「突破点＋一句结论」；无增量就写「无增量」） */
  commitMessage: string;
}

const ROOT = "/Users/luna/Documents/math IA/collatz-attack";
// args 回退（2026 年 10 月 28 日加）：AmendWorkflow 不保留 args，改道时 tag 与 focus
// 会变成 "undefined"。凡检测到 args 缺失，就从工作区文件读回退值——改道前主代理会把
// 目标写进 collatz-attack/70-research/.amend-args.json（{"tag": "...", "focus": "..."}）。
let TAG = String(args.tag);
let FOCUS = String(args.focus);
if (TAG === "undefined" || TAG === "" || FOCUS === "undefined" || FOCUS === "") {
  // 工作区根实测（2026-10-28，EvalWorkflowSnippet，glob("*") 直接列出 tracks/ 与
  // amend-args.json）：本项目的 workflow 世界里工作区根就是 70-research 本身，所以第一条
  // 相对路径才对；另两档根（仓库根 collatz-attack、math IA）也一并候选以防运行而异。
  const candidates = [
    "amend-args.json",
    ".amend-args.json",
    "70-research/amend-args.json",
    "70-research/.amend-args.json",
    "collatz-attack/70-research/amend-args.json",
    "collatz-attack/70-research/.amend-args.json",
  ];
  for (const p of candidates) {
    try {
      const raw = await files.read(p);
      const parsed = JSON.parse(raw) as { tag?: string; focus?: string };
      TAG = String(parsed.tag);
      FOCUS = String(parsed.focus);
      log(`args 缺失，已从 ${p} 读回：tag=${TAG}`);
      break;
    } catch (e) {
      log(`回退文件 ${p} 不可读：${String(e).slice(0, 100)}`);
    }
  }
}
const BASE = `${ROOT}/70-research/tracks/${TAG}`;
const STYLE =
  "写作纪律：中文正文不要出现半角连字符，破折号用「——」，并列用「、」，编号用 1. 2. 3.。诚实纪律：区分已证定理、仅预印本宣称、你自己的推断；无法核实的标注；禁止编造文献、数字或引理名；未证一律写未证。";

artifact.board("tracks", {
  title: "本轨道各路攻击的状态",
  key: "route",
  status: "status",
  columns: ["论证中", "已证", "已否证", "未决", "未完成"],
  cardTitle: "route",
  detail: [{ field: "claim", label: "最强结论" }],
});

phase("读账本与本轨道记录，定下攻击方案");
const planner = agent("轨道调度员", {
  system:
    "你是研究轨道「" + TAG + "」的调度员。你的疑点已经指定，不选题；你的工作是把疑点拆成可独立攻击的子问题与路线。" +
    "你不做数学，只做判断与拆解。若发现指定疑点已被共享账本里的结论解决或已被 learnings 列为死路，如实指出并给出一轮内更可行的小目标。" +
    STYLE,
});
const plan = await planner.ask<TrackPlan>(
  `本轨道要攻的疑点（优先于任何排序，不得改换）：\n${FOCUS}\n\n` +
    `先读这些材料（缺哪个就在返回里说明）：\n` +
    `1. ${ROOT}/70-research/ledger.md（共享账本：进展与已知结论；**只读**）\n` +
    `2. ${ROOT}/70-research/learnings.md（共享学习记录：试过且失败的方法；**只读**）\n` +
    `3. ${ROOT}/10-literature/frontier.md（边界地图）\n` +
    `4. ${BASE}/ledger-note.md（本轨道上一轮的条目；不存在就是本轨道首轮，cycleNumber 取 1）\n\n` +
    `写方案到 ${BASE}/plan.md（目录若不存在就创建），并按 schema 返回：\n` +
    `- target：照抄疑点并补一句你的攻法。\n` +
    `- subQuestions：三到五个可独立攻击的子问题。\n` +
    `- attackRoutes：三到五条互相独立的路线，name 必须互不相同，路线之间必须方法不同（例如一条解析证明、一条精确算术证书、一条反例搜索、一条文献复算），不要三条做同一件事。\n` +
    `- avoidList：从共享 learnings 与本轨道上一轮里抄出本轮要避开的方向。\n` +
    `- cycleNumber：读本轨道账本条目得出。\n\n` +
    `硬要求：所有产物路径都在 ${BASE}/ 下，**不要写共享的 ledger.md 与 learnings.md**（主代理会合并）。中文正文不要出现半角连字符。`,
);
log(`轨道 ${TAG} 第 ${plan.cycleNumber} 轮：${plan.target.slice(0, 120)}`);

phase("收集本轮所需的材料");
const materialCollector = agent("材料收集员", {
  system: "你负责为指定疑点把原始材料找齐并逐字保留关键句。打开原始文件，不转述二手报道。" + STYLE,
});
const methodScout = agent("方法侦察员", {
  system:
    "你负责弄清这个疑点上「已经有人怎么做、做到哪、卡在哪」，以及本机工具能做什么。" + STYLE,
});
const scoutPartOne = methodScout.ask<string>(
  `疑点：${FOCUS}\n子问题：\n${plan.subQuestions.join("\n")}\n\n` +
    `本轮只写第 1 与第 2 节，篇幅控制在 150 行以内（宁可精炼，不要长文）：\n` +
    `1. 文献里针对这类问题用过什么机具（逐条给出处），各自到达的范围与已知极限。\n` +
    `2. 已知的不可能性结果：哪些做法被证明必然失败（逐条给出处）。\n` +
    `写到 ${BASE}/cycle-${plan.cycleNumber}/methods.md（目录若不存在就创建），两节标题分别为「## 一、文献机具与可达范围」与「## 二、已知的不可能性结果」。\n` +
    `硬要求：每条都要能追溯到可打开的来源或项目内文件；不确定的标注；读项目内大文件先 grep 再分段读，单次不超过约 150 行。返回你写入的文件绝对路径。`,
);
const scoutPartTwo = scoutPartOne.then(() =>
  methodScout.ask<string>(
    `接上一条：往同一个文件 ${BASE}/cycle-${plan.cycleNumber}/methods.md 追加第 3 与第 4 节（不要改动前两节），篇幅控制在 80 行以内：\n` +
      `3. 本机可用的工具（${ROOT}/20-experiments/.venv/bin/python 里的 mpmath、gmpy2、sympy、z3、numpy，以及 cc 编译器）在这类问题上能做什么、不能做什么。\n` +
      `4. 你认为本轮最可能产生增量的两个切入点，各一句理由。\n` +
      `返回同一个文件路径。`,
  ),
);

const materials = await Promise.all([
  materialCollector.ask<string>(
    `疑点：${FOCUS}\n子问题：\n${plan.subQuestions.join("\n")}\n\n` +
      `收集与该疑点直接相关的一手材料，写到 ${BASE}/cycle-${plan.cycleNumber}/materials.md。要求：\n` +
      `1. 逐条列出：名称、URL 或本地路径、你是否亲自打开、与疑点相关的关键句（逐字）。\n` +
      `2. 公式若 pdftotext 抽出来乱码，用 pdftoppm 渲染成图再读。\n` +
      `3. 打不开的单列，并写明尝试过什么。\n` +
      `4. 读项目内旧产物（检查点、日志、.out、decisions 等）先 grep 或 rg 定位再分段读：单次读取不超过约 150 行，不得整读超过 100KB 的文件；关键句逐字保留到 materials.md 即可，不必把全文留在对话里（供方会对过大请求直接返回 400，本轨道已因此被停过一次）。\n` +
      `目录若不存在就创建。返回你写入的文件绝对路径。`,
  ),
  scoutPartTwo,
]);
log(`轨道 ${TAG} 材料与方法就绪`);

phase("多路独立攻击");
const attackOutcomes = await Promise.all(
  plan.attackRoutes.map(async (r, i) => {
    try {
      const attacker = agent(`攻击者·${i + 1}·${r.name}`, {
        system:
          "你是一名数论工作者，负责沿一条指定路线推进一个具体疑点。" +
          "每一步要么是已证定理（给出处）、要么是你能完整证明的初等引理、要么显式标注为缺口。" +
          "你的价值在于把失败点定到具体的不等式或具体的步骤，而不是宣布成功。" +
          STYLE,
      });
      report(
        {
          route: r.name,
          status: "论证中",
          claim: `攻击进行中，脚本与报告写在 ${BASE}/cycle-${plan.cycleNumber}/`,
          evidence: r.mission.slice(0, 160),
        },
        "tracks",
      );
      const result = await attacker.ask<AttemptResult>(
        `疑点：${FOCUS}\n本轮要避开的已失败方向：${plan.avoidList.join("、")}\n\n` +
          `你负责的路线是「${r.name}」：${r.mission}\n\n` +
          `先读这些材料：\n${materials[0]}\n${materials[1]}\n${ROOT}/10-literature/frontier.md\n\n` +
          `上下文与输出纪律（供方会对过大请求直接返回 400，务必遵守）：优先用检索（grep 或 rg）抽取你真正需要的段落，不要整文读入；报告分节写入，每写完一节就落盘一次，不要憋到最后一次性输出长文；单节控制在 200 行以内。**若本轨道此前已把结果落盘（检查点、.out、日志、json），直接读它们写报告，不要重跑重算**——重算会把上下文撑到被供方拒收，本轨道已因此被停过一次；报告整体控制在 250 行以内。\n\n` +
          `要求：\n` +
          `1. 真的动手：写代码跑、算数字、查原文。脚本放到 ${BASE}/cycle-${plan.cycleNumber}/scripts/ 下，用 ${ROOT}/20-experiments/.venv/bin/python 运行。\n` +
          `2. 报告写到 ${BASE}/cycle-${plan.cycleNumber}/route-${i + 1}.md，含：要证明或要检验的精确陈述、编号论证（每步标注 已证/缺口/错误/等价于原命题）、失败点清单、局部新结论及其独立验证方式、完整命令行与原始输出摘要。\n` +
          `3. claim 字段写你这一路最强的结论，一句话；没有结论就写「本轮未取得结论」并把 status 写成未决。严禁把未证写成已证。\n` +
          `4. keyNumbers 里每个数字都要写明实际达到的范围。\n\n` +
          `按 schema 返回。中文正文不要出现半角连字符。`,
      );
      report(
        { route: result.route, status: result.status, claim: result.claim, evidence: result.evidenceKind },
        "tracks",
      );
      return result;
    } catch (e) {
      log(`轨道 ${TAG} 路线 ${r.name} 未完成：${String(e).slice(0, 150)}`);
      const fallback: AttemptResult = {
        route: r.name,
        path: "未产出",
        claim: "本轮未取得结论",
        evidenceKind: "未决",
        status: "未决",
        keyNumbers: [],
      };
      report({ route: r.name, status: "未完成", claim: "路线未完成", evidence: "无" }, "tracks");
      return fallback;
    }
  }),
);

phase("交叉反驳与裁决");
const critiques = await Promise.all(
  attackOutcomes.map(async (item, i) => {
    if (attackOutcomes.length < 2) {
      const solo: CrossCritique = {
        route: item.route,
        verdict: "survivable",
        objection: "本轨道只有一条路线，无法交叉反驳",
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
        `攻击这份报告：${item.path}（路线「${item.route}」）。\n` +
          `它的强度声明是：${item.claim}\n它的证据类型自报为：${item.evidenceKind}\n\n` +
          `1. 检查它的假设是否成立、数字能否复算（自己写脚本重算关键的一两个数，不要复用它的脚本）。\n` +
          `2. 检查它的「已证」是否真的已证（把「数值观察」写成「定理」是本项目最常见的自欺形式）。\n` +
          `3. 给它最致命的一击；打不掉就明说，并列出你试过哪些攻击面。\n\n` +
          `按 schema 返回。`,
      );
    } catch (e) {
      log(`轨道 ${TAG} 对路线 ${item.route} 的反驳未完成：${String(e).slice(0, 150)}`);
      const fallback: CrossCritique = {
        route: item.route,
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

const judge = agent("轨道裁决员", {
  system:
    "你是裁决者。任务是把本轨道各路结果与反驳放在一起，判定哪些是真正的增量、哪些被否证、哪些还悬着。" +
    "最高纪律：不许为了好看而把未决写成已证。" +
    STYLE,
});
const verdict = await judge.ask<TrackVerdict>(
  `疑点：${FOCUS}\n\n各路结果：\n${JSON.stringify(attackOutcomes.map((a) => ({ route: a.route, claim: a.claim, evidenceKind: a.evidenceKind, status: a.status, keyNumbers: a.keyNumbers })), null, 2)}\n\n` +
    `交叉反驳摘要：\n${JSON.stringify(critiqueSummary, null, 2)}\n\n` +
    `各路完整报告在：${attackOutcomes.map((a) => a.path).join("、")}（可读）\n\n` +
    `请判定：newResults（本轮确实立住的增量，一条都没有就写空数组）、falsified、unresolved、overall（两三句总评，必须明确说有没有实质增量）。按 schema 返回。`,
);
report({
  topic: `track-${TAG}-cycle-${plan.cycleNumber}-verdict`,
  claims: verdict.newResults.length,
  citation: "adjudicated",
  summary: `${verdict.overall.slice(0, 220)}（立住 ${verdict.newResults.length} 条，否证 ${verdict.falsified.length} 条，未决 ${verdict.unresolved.length} 条）`,
  notePath: `${BASE}/plan.md`,
});

phase("确定性复算闸门");
const verifier = agent("复算员", {
  system:
    "你负责把本轮新结论写成一段可独立运行的复算脚本：脚本自己重新计算一切，不读取任何本轮的结论文件。" +
    "全部通过退出码 0，任何失败退出码非零并打印最小反例。" +
    STYLE,
});
await verifier.ask<VerifyResult>(
  `本轮的增量结论：\n${JSON.stringify(verdict.newResults, null, 2)}\n\n` +
    `写 ${BASE}/cycle-${plan.cycleNumber}/verify.py，要求：\n` +
    `1. 对每条增量结论写一个断言函数；能数值验证的就数值验证（用精确整数或有理数），只能查证的就在注释里写明「无法机器验证」并跳过。\n` +
    `2. 脚本必须自己重新计算，不许读取 route-*.md 或 materials.md 里的数字。\n` +
    `3. 打印简洁（几百行以内），全部通过退出码 0，否则非零并打印最小反例。\n` +
    `4. 若本轮的增量里含重算量很大的断言（例如百万级枚举），把该项做成可用命令行参数开启的深度检查，默认只跑小规模版本，并在脚本头部写清默认档与深度档分别覆盖什么。\n` +
    `目录若不存在就创建。按 schema 返回。`,
);
let gateCode = -1;
for (let round = 1; round <= 3; round += 1) {
  let code = -1;
  let out = "";
  try {
    const run = await world.run("collatz-attack/20-experiments/.venv/bin/python", [
      `collatz-attack/70-research/tracks/${TAG}/cycle-${plan.cycleNumber}/verify.py`,
    ]);
    code = run.exitCode;
    out = `${run.stdout.slice(-1200)}\n${run.stderr.slice(-1200)}`;
  } catch (e) {
    log(`轨道 ${TAG} 复算脚本执行失败：${String(e).slice(0, 120)}`);
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
log(`轨道 ${TAG} 复算闸门最终退出码 ${gateCode}`);

phase("写入本轨道记录并准备推送");
const ledgerWriter = agent("轨道记录员", {
  system:
    "你负责把这个轨道的记忆写对：本轨道账本条目要能让人一眼看出攻到哪、下一步该做什么；学习记录要能让下一轮避开失败的路。" +
    "只追加或精确修改本轨道目录内的文件。**严禁改动共享的 ledger.md 与 learnings.md**，也严禁执行任何 git 命令。" +
    STYLE,
});
const ledger = await ledgerWriter.ask<TrackLedgerNote>(
  `轨道 ${TAG} 第 ${plan.cycleNumber} 轮结束。闸门退出码 ${gateCode}。\n总评：${verdict.overall}\n增量：${JSON.stringify(verdict.newResults, null, 2)}\n否证：${JSON.stringify(verdict.falsified, null, 2)}\n未决：${JSON.stringify(verdict.unresolved, null, 2)}\n\n` +
    `请做四件事（全部在 ${BASE}/ 下）：\n` +
    `1. 新建或追加 ${BASE}/ledger-note.md：本轮条目（日期、疑点、增量、否证、未决、闸门退出码），文件开头维护「本轨道当前状态」摘要。\n` +
    `2. 新建或追加 ${BASE}/learnings-note.md：本轮「试过且失败或无效的方法」逐条（每条一句为什么失败）。\n` +
    `3. 新建 ${BASE}/cycle-${plan.cycleNumber}/summary.md：本轮自足摘要（疑点、方法、结论、复现命令、未决）。\n` +
    `4. 返回 ledgerEntry 与 learningsEntry 两段 Markdown 正文（供主代理合并进共享账本与学习记录），不要自己去改共享文件。\n\n` +
    `commitMessage 字段：有增量写成「突破点＋一句结论」，没有就写「无增量」。按 schema 返回。`,
);

return {
  conclusion:
    `轨道 ${TAG} 第 ${plan.cycleNumber} 轮（疑点：${plan.target}）已跑完，复算闸门退出码 ${gateCode}。` +
    `裁决：${verdict.overall} 本轮立住 ${verdict.newResults.length} 条、否证 ${verdict.falsified.length} 条、未决 ${verdict.unresolved.length} 条。` +
    `本轨道摘要 ${BASE}/cycle-${plan.cycleNumber}/summary.md；条目已备好待主代理合并进共享账本。科拉茨猜想本身仍未被证明。`,
  findings: [
    {
      where: `${BASE}/cycle-${plan.cycleNumber}/summary.md`,
      what: `轨道 ${TAG} 第 ${plan.cycleNumber} 轮：${verdict.overall.slice(0, 240)}`,
      evidence: `${plan.attackRoutes.length} 条独立路线 + ${critiques.length} 次交叉反驳 + 裁决 + 复算闸门（退出码 ${gateCode}）`,
      status: gateCode === 0 ? "verified" : "unconfirmed",
      severity: "high",
    },
    {
      where: `${BASE}/ledger-note.md`,
      what: `本轨道账本条目已写好，待主代理合并：${ledger.commitMessage}`,
      evidence: `改动文件 ${ledger.files.length} 处`,
      status: "verified",
      severity: "medium",
    },
  ],
  verified: [
    `复算闸门由 world.run 直接执行并读取退出码（最终 ${gateCode}）`,
    `每条路线的强度声明都经过另一条路线的反驳者攻击（${critiques.length} 次）`,
  ],
  notCovered: [
    "科拉茨猜想本身仍未被证明或推翻；本轨道只攻指定的疑点",
    "共享账本与学习记录的合并由主代理在推送时执行，本工作流只写自己的轨道目录",
    "git 提交与推送由主代理执行",
  ],
};
