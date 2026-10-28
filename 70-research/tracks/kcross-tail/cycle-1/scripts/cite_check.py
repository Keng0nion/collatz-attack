#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""引用核验闸门（轨道 kcross-tail 第 1 轮，路线 5「账本条目与引用卫生」）。

作用：对 ledger-note.md 与 route-5.md 里出现的每一条引用，机器核对四件事——
  1. 文件存在；
  2. md5 与条目里写的版本串逐字符相同；
  3. 行数与条目里写的相同；
  4. 指定的行号上确实含有指定的子串（逐字）。
另有一条 CONTRAST 断言：某行**不得**含有某子串（用于登记同名文件在不同 cycle 下的歧义）。
还有一条自检：故意给一个错的断言，要求核验器判它 FAIL（对应 learnings.md:53「判据必须能取 False」）。

退出码 0 = 全部引用成立且自检通过；任一失败 = 退出码 1。

证据边界：本脚本只核对「引用指向现行文件的该行原文」，不核对被引内容的数学真假，
也不核对「作者是否读过该行」（那一条只能靠人）。

命令行：
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
      "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1/scripts/cite_check.py"
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

# 仓库根：本文件位于 <repo>/70-research/tracks/kcross-tail/cycle-1/scripts/cite_check.py
REPO = Path(__file__).resolve().parents[5]
if REPO.name != "collatz-attack":
    raise SystemExit(f"仓库根定位失败：{REPO}")

P = "70-research/tracks/kcross-proof/cycle-1/"
C2 = "70-research/cycle-2/"
KT = "70-research/tracks/kcross-tail/"

# ---------------------------------------------------------------- 引用表
# 每条：路径、md5、行数、[(行号, 必须出现的子串), ...]
CASES = [
    # 四份路线报告：命名等同（T = R）的两种状态登记
    dict(
        path=P + "route-1.md",
        md5="3319972d070e02baf3399d708c880269",
        nlines=414,
        hits=[
            (115, "**陈述**：设 K_lo ≥ R。则链的第一步"),
            (133, "**陈述**：设 K_lo ∈ [92C, R)。"),
            (148, "**注 B7（这条路径的关键不对称）**"),
            (171, "**推论 1（T = R）**"),
            (202, "**已证**（初等 L1 至 L4 + 证书 C1 至 C6）"),
            (262, "窗口宽度的登记本身有分歧"),
            (289, "**若必须指出本路线最薄的一环**：B3 依赖「γ 的分子分母已约分且分母恰为 K\\*」"),
            (299, "本文件的「已证」一律是「本文初等推理 + 本机实跑证书」意义上的"),
            (313, "**T = R**：动力学越界阈值等于 ε_opt(K) = γ − δ 的唯一实根"),
        ],
    ),
    dict(
        path=P + "route-2.md",
        md5="ea82163d12bd6b889b07fe9af7c085c1",
        nlines=253,
        hits=[
            (12, "两侧严格区间证书成立"),
            (23, "T = R（R 为 ε(92, K) = γ − δ 的根）"),
            (167, "**未证，本路不裁决**"),
            (253, "端点 T_hi、T_lo 是参数"),
        ],
    ),
    dict(
        path=P + "route-3.md",
        md5="91223865e6b538572b6ab60bb218a64e",
        nlines=409,
        hits=[
            (21, "**未证（本路线不裁决，也不提供新证据）**"),
            (129, "分母小于 `K*` 的清单项 438 条"),
            (243, "不含任何关于 T 与 R 等同的断言"),
        ],
    ),
    dict(
        path=P + "route-4.md",
        md5="6a1b4efe2d9a49bf952e71456eefc1ea",
        nlines=287,
        hits=[
            (157, "7.80677136541×10⁻¹³（j = 90）与 7.71461775858×10⁻¹³（j = 89）"),
            (171, "A(91) − A(92) = 3/X₀ ≈ 5.55×10⁻²¹"),
            (270, "**本路未证**，只做了等同所需边界的压力测试"),
        ],
    ),
    # route-1 侧日志（阈值 T 的 50 位区间）
    dict(
        path=P + "scripts/results/k1_threshold_cert.log",
        md5="23fec892a94f72cb135562b584fe6ec2",
        nlines=94,
        hits=[
            (35, "分母 > U(92) 上界 ？ True"),
            (37, "z·y − x·w = 1（= 1）；中项分母 y + w = 7941964418702608664581"),
            (61, "KA = 313195478959172262876.636530619490706526023101695228884264870920840545633819131291"),
            (62, "KB = 313195478959172262876.636530619490706526023101695230936948168271646801869751138064"),
            (63, "绝对宽度 = 2.052683e-30 ；相对宽度 = 6.554000e-51"),
        ],
    ),
    # route-2 侧日志（阈值 T 的两侧区间证书）
    dict(
        path=P + "scripts/results/r2_threshold_cert.log",
        md5="c45b3da1f6910ba07c41a27682391904",
        nlines=164,
        hits=[
            (52, "已完成 400 步，宽度 1.161777574454 e-102"),
            (57, "T_hi 的精确有理 = 1542566275329005279840718039419280435916173943310179998952443721548967387604624457272573600391707651885171022391000442764034271240234375/"),
            (58, "T_lo 的精确有理 = 3085132550658010559681436078838560871832347886620359997904887443097934775209248914545147200783415303770342044782000885528079986572265625/"),
            (67, "A1：全部 eps(m2, T_hi)_下界 > (gamma - delta)_上界"),
            (76, "A5：对一切 q <= 6456"),
            (86, "B2 eps(92, T_lo)_上界 < (gamma - delta)_下界"),
            (149, "9.1 阈值 T 的严格区间：T ∈ [T_hi, T_lo]，宽度 1.161777574454 e-102"),
            (152, "9.2 「T = R」的识别：本路未裁决"),
        ],
    ),
    # route-3 侧日志（ε 梯子、438 条清单）
    dict(
        path=P + "scripts/results/k3_run_a.out",
        md5="01f48fc0ebd6121c2b372861be96fb6e",
        nlines=71,
        hits=[
            (21, "eps(91, 92, K*) ∈ [8.9732217086171360163257e-42"),
            (22, "A 下界剪枝：min_{1<=m2<=90} A(m2)/(3K ln2_hi) = 1.4430955236618072755609e-41（在 m2 = 90 处）"),
            (46, "清单条数（分母 < K* 的检查条数）= 438"),
        ],
    ),
    dict(
        path=P + "scripts/results/k3_run_e.out",
        md5="f8b900d497b776778107070a15799443",
        nlines=31,
        hits=[
            (24, "完整清单条数 = 442"),
            (26, "被 cap 掉（分母 >= K*）的条数 = 4"),
        ],
    ),
    # route-4 侧日志（窗口修正与两个不动点）
    dict(
        path=P + "scripts/results/r4b2_window_probe.out",
        md5="a078e3e631f07858f4b607968403a3c2",
        nlines=77,
        hits=[
            (52, "相对窗口宽度 ∈ [0.000000000000780677136541"),
            (54, "2e-24 落入？ False ；1.5361313e-23 落入？ False"),
            (57, "相对窗口宽度 ∈ [0.000000000000771461775858"),
            (73, "该项约为 9×10^-32"),
        ],
    ),
    dict(
        path=P + "scripts/results/r4a_search_low.out",
        md5="81bc80dc84bb1a570220b5439fd1ec79",
        nlines=563,
        hits=[
            (28, "点数 = 515 ；未定（Psi 未夹住）= 0"),
            (33, "不动点 77692117359936589403 ：476 次"),
            (34, "不动点 205632218873398596256 ：39 次"),
        ],
    ),
    dict(
        path=P + "scripts/results/r4c_count_boundary.out",
        md5="9881d92a24fb16327f9186144af8f74f",
        nlines=50,
        hits=[(17, "比较 WD_STRICT < 1/K* ？ True")],
    ),
    # 上游 cycle-2：命名来源与旧登记
    dict(
        path=C2 + "scripts/c2r5_cert.py",
        md5="54cb5e4bc2cd3321a8306a604a87e4b3",
        nlines=250,
        hits=[(180, "[5] K_cross 的严格根隔离：eps_opt(K) = gamma - delta 的根")],
    ),
    dict(
        path=C2 + "scripts/results/c2r5_cert.log",
        md5="9e827cd1ebfdff89825c14616a3c0e62",
        nlines=89,
        hits=[
            (9, "C = log2((162/97)X0) ∈ [70.1808063283083668248487894995"),
            (27, "A(91) 取定理 21 第二段的 3/X0 = 3.74400750210821675052933341308e-21"),
            (67, "二分 150 步后：K_cross ∈ [313195478959172262876.6365306194907065260231016940260118526233"),
        ],
    ),
    dict(
        path=C2 + "route-5.md",
        md5="fb9a00e852c9a05b1ebdcb63f57fedf1",
        nlines=442,
        hits=[
            (230, "窗口宽度 ≈ 1.5×10⁻²²/70.18 ≈ 2×10⁻²⁴（相对）"),
            (232, "分岔窗口宽约 2×10⁻²⁴，网格命中概率约为 10⁻²² 量级"),
            (353, "没有证明或否证「一切 K_lo ≤ K* 都不能让 m = 92 越界」"),
        ],
    ),
    dict(
        path=C2 + "route-1.md",
        md5="3802c50661385e9a89299e8e5c90a2ec",
        nlines=344,
        hits=[
            (215, "**未证**：这是读法，不是定理"),
            (227, "该读法**未证**"),
        ],
    ),
    dict(
        path=C2 + "route-4.md",
        md5="9fa26ffac726a5dafd4e25eed4f00454",
        nlines=342,
        hits=[
            (98, "**根 = 阈值未证**"),
            (192, "「该根 = 越界阈值"),
        ],
    ),
    # 共享纪律文件（只读，不写）
    dict(
        path="70-research/ledger.md",
        md5="8e0b44e3ebbf795dc393e4fa559cbee3",
        nlines=197,
        hits=[
            (21, "补「根 = 越界阈值」的定义桥"),
            (30, "不得写成「K_cross 的 47 位严格定位」"),
            (33, "窗口真实相对宽度约 7.6×10⁻¹³"),
            (193, "对 2.3 第 1 项的独立复算（本会话实跑）"),
        ],
    ),
    dict(
        path="70-research/learnings.md",
        md5="96f3d946b0fbae97e31b873090503fb9",
        nlines=62,
        hits=[
            (29, "「数值观察」不得写成「定理」"),
            (36, "报告里的数字与脚本或日志脱钩"),
            (51, "推窗口宽度只比 log₂(1 + 2^−C)，漏掉同一比较里的第三项"),
            (59, "用旧版本行号或带错的旧措辞做前提"),
        ],
    ),
    dict(
        # 注意路径：kcross-proof 的 plan.md 在轨道根下，不在 cycle-1/ 下
        # （首次运行本闸门时误写成 P + "plan.md"，被「文件不存在」判 FAIL 抓出）
        path="70-research/tracks/kcross-proof/plan.md",
        md5="7a3e333b8b9629e28bfc3ddc1b0a884f",
        nlines=218,
        hits=[(192, "把 route-1 与 route-4 的「未证」或 route-5 的「已证（条件性）」任一方直接照抄为本轮结论")],
    ),
    dict(
        path=P + "materials.md",
        md5="41f686b48c456d82c3323184e0196e98",
        nlines=537,
        hits=[(427, "当前 130 行，md5 `c238e1003f6cf3b1ee0fcf29ae82e58a`")],
    ),
    dict(
        path=KT + "plan.md",
        md5="04fb9c97a5713670b2093f2fd8cf6304",
        nlines=182,
        hits=[
            (141, "按 S5 写 `ledger-note.md`"),
            (163, "19 位以上十进制数字不得经 float 中转"),
        ],
    ),
]

# --------------------------- 补充：ledger-note.md 其余引用（同上格式）-----------
# 第一轮 CASES 覆盖四份报告、全部关键日志与共享纪律文件；
# 下表补齐 ledger-note.md 正文里出现的其余行号，使「条目里的每条引用都被机器核过」。
SUPPLEMENT = [
    dict(
        path=P + "route-1.md",
        md5="3319972d070e02baf3399d708c880269",
        nlines=414,
        hits=[
            (3, "**T = R**（阈值等于根）"),
            (86, "故 s ≥ q + q′。等号情形要求两个分子都等于 1"),
            (212, "| 指称 | 出处（本轮亲读） | 对象 |"),
            (216, "| 指**数值锚点** |"),
            (218, "**裁决第一句**：`c2r5_cert.py:180` 是**定义式**的命名"),
        ],
    ),
    dict(
        path=P + "route-2.md",
        md5="ea82163d12bd6b889b07fe9af7c085c1",
        nlines=253,
        hits=[
            (20, "**严格证书（本路自足）**"),
            (21, "**严格证书（本路自足）**"),
        ],
    ),
    dict(
        path=P + "route-3.md",
        md5="91223865e6b538572b6ab60bb218a64e",
        nlines=409,
        hits=[
            (15, "**已证（本路线独立证书；条件：项目 (D1) 至 (D5) 的定义与 Theorem 21 的公式）**"),
            (130, "**条数对账**"),
            (272, "**清单穷举必须带分母上限**"),
        ],
    ),
    dict(
        path=P + "route-4.md",
        md5="6a1b4efe2d9a49bf952e71456eefc1ea",
        nlines=287,
        hits=[
            (92, "C1【已证，精确有理比较】β(K\\*) − δ < 1/K\\*"),
            (202, "`[3] 结果汇总` 逐字"),
            (207, "**读法（与全称结论的分界）**"),
        ],
    ),
    dict(
        path=P + "scripts/results/r2_threshold_cert.log",
        md5="c45b3da1f6910ba07c41a27682391904",
        nlines=164,
        hits=[
            (79, "A6 结论 A：对一切 K_lo ∈ D_92 且 K_lo <= T_hi"),
            # 注：该结论跨两行，正文在 :80（:81 是计时行）；首次写成 :81 被本闸门判 FAIL
            (80, "故链在域内永不中断，全部迭代 <= K* < U(92)：永不越界。"),
        ],
    ),
    dict(
        path=P + "scripts/results/r4b2_window_probe.out",
        md5="a078e3e631f07858f4b607968403a3c2",
        nlines=77,
        hits=[
            (51, "窗口右端 K*_j ∈ [123124614107652692133.007231711933058876044901"),
            (56, "窗口右端 K*_j ∈ [78555824936819382091.475309577063948109807001"),
        ],
    ),
    dict(
        path=C2 + "scripts/results/c2r5_cert.log",
        md5="9e827cd1ebfdff89825c14616a3c0e62",
        nlines=89,
        hits=[
            (67, "二分 150 步后：K_cross ∈ [313195478959172262876"),
            (77, "对一切 beta <= gamma 的 K：Psi(K) >= simplest(delta_lo, gamma) > U(92) ？ True"),
        ],
    ),
    dict(
        path=C2 + "route-5.md",
        md5="fb9a00e852c9a05b1ebdcb63f57fedf1",
        nlines=442,
        hits=[(101, "C := log₂((162/97)·X₀) = 70.1808063283083640726545127109")],
    ),
    dict(
        path="70-research/ledger.md",
        md5="8e0b44e3ebbf795dc393e4fa559cbee3",
        nlines=197,
        hits=[
            (23, "把窗口端点（裁决员数值复算约 7.6×10⁻¹³；账本会话独立复算 7.622、7.715、7.807×10⁻¹³）写成严格区间证书"),
            (35, "「401 点零分歧 ⇒ 约定问题消解」不成立"),
        ],
    ),
    dict(
        path="70-research/learnings.md",
        md5="96f3d946b0fbae97e31b873090503fb9",
        nlines=62,
        hits=[
            (44, "网格只能作机制检查或反例搜索，永远不能当全称命题的证据"),
            (53, "每条判据都要写成能取 False 的形式"),
            (61, "精确与浮点混用时先转成同一种有理区间再比"),
            (62, "定稿前要么跑完、要么在引用处显式带「未跑完」标记"),
        ],
    ),
    dict(
        path=KT + "plan.md",
        md5="04fb9c97a5713670b2093f2fd8cf6304",
        nlines=182,
        hits=[
            (72, "账本条目的边界栏按最弱口径取（全部未形式化、未经第三方复核）"),
            (89, "本轨道 (c) 的正确动作是写成条目交主代理合并，**不直接改账本**"),
            (91, "条目须分注来源，并把 r4b2 的二分严格区间版本（j = 89、90）补上"),
        ],
    ),
    dict(
        path=KT + "cycle-1/methods.md",
        md5="3ef852437a641e402e96888b115cb1cc",
        nlines=99,
        hits=[
            (80, "python 3.12.7"),
            (81, "缺席清单：`command -v lean lake coqtop gp pari sage` 无输出、退出码 1"),
        ],
    ),
    # 第二处同名文件陷阱：P1/materials.md 与 KT/cycle-1/materials.md 同名而分节不同。
    # P1 版的 §1.4、§2.7 是关于 U(92) 与 L 的文献出处节；分母和恒等式在 KT 版的 :369。
    dict(
        path=P + "materials.md",
        md5="41f686b48c456d82c3323184e0196e98",
        nlines=537,
        hits=[
            (71, "### 1.4 Simons 与 de Weger v1.44（Hercher 的参考文献 [12]）"),
            (185, "### 2.7 Simons 与 de Weger v1.44 Theorem 3（U(92) 与 L 的唯一定义出处）"),
            (530, "## 七、本次未做、未核、未尝试（防误读）"),
        ],
    ),
    dict(
        path=KT + "cycle-1/materials.md",
        md5="b57289f90fd16aa46c1fa9271088363e",
        nlines=383,
        hits=[
            (354, "## 七、本次实算清单（精确重算，脚本与结果）"),
            (369, "5. **分母和**：`K* + q₄₄ = 205632218873398596256 + 7736332199829210068325 = 7941964418702608664581`（True）。"),
        ],
    ),
    # 修正二里标「转引」的那一处，本路已回一手核其行号与 md5
    dict(
        path="70-research/cycle-1/route-4.md",
        md5="637e123bb02db287466105ebf3c67504",
        nlines=383,
        hits=[(194, "**判据**：链从 K_lo 出发，若某次迭代 > U(92) 就算「越过」。")],
    ),
]

# --------------------------------------------------- 同名文件歧义对照断言
# 账本 ledger.md:30 写「`route-4.md:192` 至 `:194` 均自登记未证」。
# 现行 cycle-2/route-4.md:192 确为「未证」自登记；而 kcross-proof/cycle-1/route-4.md:192
# 是另一份文件里的机制段表格行，与该「未证」无关。故裸文件名 route-4.md 有歧义，
# 条目里必须写全路径。下面两条机器断言把这个区别钉住。
CONTRAST = [
    dict(
        path=P + "route-4.md",
        lineno=192,
        must_not_contain="该根 = 越界阈值",
        note="cycle-1 的 route-4.md:192 不是「根 = 阈值」的自登记行",
    ),
    dict(
        path=C2 + "route-4.md",
        lineno=192,
        must_not_contain="v < 3",
        note="cycle-2 的 route-4.md:192 不是机制段表格行",
    ),
]

# ------------------------------------------------------------------ 自检
SELFTEST = dict(
    path=P + "route-2.md",
    lineno=23,
    must_contain="这一串保证不在现行 route-2.md 第 23 行里",
)


def wc_lines(data: bytes) -> int:
    return data.count(b"\n")


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").split("\n")


def main() -> int:
    fails: list[str] = []
    checks = 0

    print("=" * 72)
    print("引用核验：逐条核对「文件、md5、行数、行号含串」")
    print(f"仓库根：{REPO}")
    print("=" * 72)

    for case in CASES + SUPPLEMENT:
        path = REPO / case["path"]
        print(f"\n[{case['path']}]  期望 md5 {case['md5']}、{case['nlines']} 行")
        if not path.exists():
            fails.append(f"{case['path']}：文件不存在")
            print("    FAIL 文件不存在")
            continue
        data = path.read_bytes()
        got_md5 = hashlib.md5(data).hexdigest()
        got_lines = wc_lines(data)
        checks += 1
        if got_md5 != case["md5"]:
            fails.append(f"{case['path']}：md5 {got_md5} != {case['md5']}")
            print(f"    FAIL md5 不符：{got_md5}")
        else:
            print(f"    PASS md5 {got_md5}")
        checks += 1
        if got_lines != case["nlines"]:
            fails.append(f"{case['path']}：行数 {got_lines} != {case['nlines']}")
            print(f"    FAIL 行数不符：{got_lines}")
        else:
            print(f"    PASS 行数 {got_lines}")
        lines = read_lines(path)
        for lineno, needle in case["hits"]:
            checks += 1
            if lineno < 1 or lineno > len(lines):
                fails.append(f"{case['path']}:{lineno}：行号越界")
                print(f"    FAIL :{lineno} 行号越界（文件 {len(lines)} 行）")
                continue
            line = lines[lineno - 1]
            if needle in line:
                print(f"    PASS :{lineno} 含「{needle[:46]}{'…' if len(needle) > 46 else ''}」")
            else:
                fails.append(f"{case['path']}:{lineno}：不含该子串")
                print(f"    FAIL :{lineno} 不含「{needle}」")
                print(f"         现行该行 = {line[:200]}")

    print("\n" + "=" * 72)
    print("歧义对照断言（同名 route-4.md 在 cycle-1 与 cycle-2 下内容不同）")
    print("=" * 72)
    for c in CONTRAST:
        path = REPO / c["path"]
        checks += 1
        lines = read_lines(path)
        line = lines[c["lineno"] - 1]
        if c["must_not_contain"] in line:
            fails.append(f"{c['path']}:{c['lineno']}：不应含该子串却含了")
            print(f"    FAIL {c['path']}:{c['lineno']} 不该含「{c['must_not_contain']}」")
        else:
            print(f"    PASS {c['path']}:{c['lineno']} 不含「{c['must_not_contain']}」（{c['note']}）")

    print("\n" + "=" * 72)
    print("自检：故意错的断言必须被判 FAIL（learnings.md:53 的「判据能取 False」）")
    print("=" * 72)
    lines = read_lines(REPO / SELFTEST["path"])
    caught = SELFTEST["must_contain"] not in lines[SELFTEST["lineno"] - 1]
    if caught:
        print(f"    PASS 错的断言被判 FAIL（{SELFTEST['path']}:{SELFTEST['lineno']} 不含该串）")
    else:
        fails.append("自检失败：错的断言竟被判 PASS")
        print("    FAIL 错的断言未被判 FAIL，说明判据是恒真的")

    print("\n" + "=" * 72)
    print(f"共 {checks} 条机器断言；FAIL {len(fails)} 条")
    if fails:
        for f in fails:
            print("  * " + f)
        print("退出码 1（引用核验未通过）")
        return 1
    print("退出码 0（全部引用成立：文件、md5、行数、行号含串逐条对上）")
    print("证据边界：本闸门不核对被引内容的数学真假，也不核对作者是否读过该行。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
