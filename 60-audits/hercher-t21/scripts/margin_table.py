#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
margin_table.py —— 采信版本（勘误版，附条件）下的逐 m 余量表与自检。

采信版本：勘误版（附条件），即同一目录下 rederive-erratum.py 所实现的那一版。
本脚本不重写那一版，而是按路径载入它并直接调用它的自举，
以保证表里的数字就是被采信版本本身的输出。

两侧的定义
==========

K 下界：勘误版七步型自举的链终值。起点 K > 7·10^11（SdW），
第一段用陈述里的 +73，尾部用勘误的聚合尾界 3(m2−1)/(2^v−1)^delta，
eps 经 Lemma 22 换回连分数分母 q_min。每次 bootstrap 取使 eps 最小的可行 m2。

K 上界 K_up^CF(m)：SdW（Simons 与 de Weger）定理 3(d) 的两段常数形式
    78 <= m <= 90 :  K < 1.3993 · m · delta^m
    91 <= m       :  K < 1.4784 · m · delta^m
出处为本机抽取文本 /tmp/hercher-audit/sidw144.txt 第 262 至 272 行（本次已读）。
Hercher 论文第 879 至 880 行末尾引用的正是 1.4784·m·delta^m < 2.2·10^20。

关于列名 K_up^CF(m) 的说明（诚实标注）：任务里给的列名是 K_up^CF(m)，未附定义。
它在本仓库另有字面更贴切的一处用法：30-proof-attempts/diophantine-transcendence/
dt_fix.py 第 80 行的 K_up_cf（连分数给出的 K 上界）。实测该函数在 m = 91、cm = 1
处等于 2.1695797449279067599e20，用它算出的余量是 36.6 余，与任务同时钉住的
37.09935525747164 不符。而 1.4784·91·delta^91 = 214072842063828923281.36，
7941964418702608664581 除以它恰为 37.09935525747164492758953。
故本脚本按与钉住的余量相符这一唯一解来取 K_up^CF(m)：
即采信版本自身扫描所用的 SdW 分段上界（见 rederive-erratum.py 的 sdw_upper）。

判据：K 下界 > K 上界 则该 m 被排除。

覆盖范围
========

m = 20 至 95，共 76 行。m <= 77 处 SdW 没有 1.3993 型或 1.4784 型的 K 上界
（该段由定理 3(b) 另行证掉 m <= 75，定理 3(c) 把 76、77 只留成候选表），
故那些行的上界与余量记作「无」，判定栏写明原因。这不是本脚本的省略，
而是采信版本在该段本就没有可用的上界。

自检 6 条，任一不过则以非零码退出。
"""

import importlib.util
import os
import sys

from pathlib import Path

AUDIT_DIR = Path("/Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21")
SCRIPTS_DIR = AUDIT_DIR / "scripts"
RESULTS_DIR = AUDIT_DIR / "results"
ADOPTED_SCRIPT = SCRIPTS_DIR / "rederive-erratum.py"
TABLE_PATH = RESULTS_DIR / "margin-table.txt"

M_LO, M_HI = 20, 95

# 裁决钉住的数字（本次任务给定）
ADJ_MARGIN_M91 = "37.09935525747164"
ADJ_K_LOW_M91 = 7941964418702608664581

# 采信版本报告（rederivation-erratum.md 第 255 行）里的全精度余量，用作交叉核对
ERRATUM_MARGIN_M91 = "37.09935525747164492758953"

MARGIN_DIGITS = 24          # 表中余量打印的有效位数


def safe_target(raw, allowed_root):
    """规范化路径，并确认它落在允许目录内（白名单校验），否则拒绝写入。"""
    target = Path(raw).resolve()
    root = Path(allowed_root).resolve()
    if target.parent != root:
        raise ValueError(f"拒绝写入允许目录以外的路径：{target}")
    return target


def load_adopted():
    """按路径载入采信版本的重推脚本（它有 __main__ 保护，导入无副作用）。"""
    spec = importlib.util.spec_from_file_location(
        "adopted_erratum", str(safe_target(ADOPTED_SCRIPT, SCRIPTS_DIR)))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["adopted_erratum"] = mod
    spec.loader.exec_module(mod)
    return mod


ADOPTED = load_adopted()

from mpmath import mp, mpf, log, power, nstr  # noqa: E402

ROUNDTRIP_RTOL = mpf("1e-18")
PRINT_RTOL = mpf("1e-22")


def k_up_cf(m, delta):
    """SdW 定理 3(d) 的 K 上界；该段没有此型定理时返回 (None, 理由)。"""
    if 78 <= m <= 90:
        return (mpf("1.3993") * m * power(delta, m),
                "SdW 3(d) 78 至 90 段，1.3993·m·δ^m")
    if m >= 91:
        return (mpf("1.4784") * m * power(delta, m),
                "SdW 3(d) 91 至 515619 段，1.4784·m·δ^m")
    return None, "SdW 在该段无此型上界"


def fmt_num(v, nd=20):
    """整数按精确整数打印，否则按 nd 位有效数字。"""
    if v is None:
        return "无"
    if v == int(v):
        return str(int(v))
    return nstr(v, nd)


def main():
    # 必须在抬精度之后才算 delta：mpf 一经算出就固定住自己的位数，
    # 若沿用 mpmath 默认的 15 位，power(delta, m) 到 m = 91 会把相对误差放大近百倍。
    mp.dps = 140
    delta = log(3) / log(2)
    failures = []
    checks = []

    def record(name, ok, detail):
        checks.append((name, bool(ok), detail))
        if not ok:
            failures.append(name)

    # ------------------------------------------------------------------
    # 1. 逐 m 建表
    # ------------------------------------------------------------------
    rows = []
    for m in range(M_LO, M_HI + 1):
        mp.dps = 120
        bt = ADOPTED.bootstrap(m, dps=120, dps_cf=250, mode="73")
        k_low = mpf(bt["K_final"])
        status = bt["status"]

        mp.dps = 140
        up, src = k_up_cf(m, delta)
        margin = None if up is None else k_low / up
        margin_str = None if margin is None else nstr(margin, MARGIN_DIGITS)

        if up is None:
            if m <= 75:
                verdict = "不判（SdW 3(b)）"
            else:
                verdict = "不判（SdW 3(c)）"
            excluded = None
        else:
            excluded = bool(margin > 1)
            verdict = "排除" if excluded else "不排除"

        rows.append({
            "m": m, "k_low": k_low, "up": up, "src": src,
            "margin": margin, "margin_str": margin_str,
            "verdict": verdict, "excluded": excluded,
            "status": status,
        })

    bounded = [r for r in rows if r["up"] is not None]
    ms_b = [r["m"] for r in bounded]

    # ------------------------------------------------------------------
    # 2. 汇总
    # ------------------------------------------------------------------
    excluded_ms = [r["m"] for r in bounded if r["excluded"]]
    m_star = max(excluded_ms) if excluded_ms else None
    first_not = None
    if m_star is not None:
        after = [r["m"] for r in bounded if r["m"] > m_star]
        first_not = min(after) if after else None

    # ------------------------------------------------------------------
    # 3. 自检
    # ------------------------------------------------------------------
    # (1) 余量倍数 = 下界除以上界
    worst_rt = mpf(0)
    worst_rt_m = None
    worst_print = mpf(0)
    worst_print_m = None
    n_rt = 0
    for r in bounded:
        mp.dps = 140
        parsed = mpf(r["margin_str"])          # 把表中印出的字符串解析回数值
        rel = abs(parsed * r["up"] - r["k_low"]) / abs(r["k_low"])
        relp = abs(parsed - r["margin"]) / abs(r["margin"])
        n_rt += 1
        if rel > worst_rt:
            worst_rt, worst_rt_m = rel, r["m"]
        if relp > worst_print:
            worst_print, worst_print_m = relp, r["m"]
    record("余量倍数 = 下界除以上界",
           worst_rt < ROUNDTRIP_RTOL and worst_print < PRINT_RTOL,
           f"{n_rt} 行有上界；把表中余量字符串解析回数值再乘上界，"
           f"与下界的最大相对差 {nstr(worst_rt, 6)}（出现在 m = {worst_rt_m}）；"
           f"解析值与全精度值之差的最大相对量 {nstr(worst_print, 6)}"
           f"（出现在 m = {worst_print_m}，即 {MARGIN_DIGITS} 位有效数字打印的舍入）；"
           f"阈值 {nstr(ROUNDTRIP_RTOL, 2)} 与 {nstr(PRINT_RTOL, 2)}")

    # (2) 上界随 m 单调（在定值区间上，并核该区间连续）
    uppers = [r["up"] for r in bounded]
    contiguous = (ms_b == list(range(ms_b[0], ms_b[-1] + 1)))
    mono_ok = all(uppers[i] < uppers[i + 1] for i in range(len(uppers) - 1))
    bad_pair = None
    for i in range(len(uppers) - 1):
        if not (uppers[i] < uppers[i + 1]):
            bad_pair = (ms_b[i], ms_b[i + 1])
            break
    jump = (uppers[ms_b.index(91)] / uppers[ms_b.index(90)]) if 91 in ms_b else None
    record("上界随 m 单调",
           bool(mono_ok and contiguous),
           f"区间 {ms_b[0]} 至 {ms_b[-1]}（连续 ? {contiguous}），"
           f"严格递增 ? {mono_ok}"
           + (f"，反例 {bad_pair}" if bad_pair else "")
           + (f"；90 至 91 跨段跳变的比值 {nstr(jump, 8)}" if jump is not None else ""))

    # (3) 边界 m 处余量跨过 1
    b_ok = False
    b_detail = "无可排除的 m，无法定位边界"
    if m_star is not None and first_not is not None:
        at_star = [r for r in rows if r["m"] == m_star][0]
        after_star = [r for r in rows if r["m"] == first_not][0]
        no_later = not any(r["excluded"] for r in bounded if r["m"] > m_star)
        b_ok = (at_star["margin"] > 1) and (after_star["margin"] <= 1) and no_later
        b_detail = (f"m = {m_star} 余量 {nstr(at_star['margin'], 12)} > 1；"
                    f"m = {first_not} 余量 {nstr(after_star['margin'], 12)} <= 1；"
                    f"其后 {first_not} 至 {ms_b[-1]} 无一被排除 ? {no_later}")
    record("边界 m 处余量跨过 1", b_ok, b_detail)

    # (4) 裁决数字复现
    row91 = [r for r in rows if r["m"] == 91][0]
    m16 = nstr(row91["margin"], 16)
    m25 = nstr(row91["margin"], 25)
    rec_ok = (m16 == ADJ_MARGIN_M91
              and m25 == ERRATUM_MARGIN_M91
              and int(row91["k_low"]) == ADJ_K_LOW_M91)
    record("裁决钉住的数字复现", rec_ok,
           f"m = 91：余量 16 位 {m16}（裁决给 {ADJ_MARGIN_M91}）；"
           f"25 位 {m25}（采信版本报告给 {ERRATUM_MARGIN_M91}）；"
           f"下界 {int(row91['k_low'])}（裁决给 {ADJ_K_LOW_M91}）；"
           f"上界 {nstr(row91['up'], 25)}")

    # (5) 覆盖完整
    ms_all = [r["m"] for r in rows]
    cov_ok = (ms_all == list(range(M_LO, M_HI + 1)))
    record("覆盖完整", cov_ok,
           f"共 {len(ms_all)} 行，覆盖 m = {M_LO} 至 {M_HI}，无重复无缺 ? {cov_ok}")

    # (6) 最大可排除 m 与逐行判定自洽
    self_ok = (m_star is None) or (
        excluded_ms == list(range(min(excluded_ms), m_star + 1)))
    record("最大可排除 m 与逐行判定自洽", self_ok,
           f"判定为排除的 m 共 {len(excluded_ms)} 个，构成 "
           f"{min(excluded_ms) if excluded_ms else '—'} 至 {m_star} 的连续段 ? {self_ok}")

    # ------------------------------------------------------------------
    # 4. 输出
    # ------------------------------------------------------------------
    out = []
    w = out.append

    w("=" * 96)
    w("采信版本（勘误版，附条件）下的逐 m 余量表")
    w("=" * 96)
    w("K 下界：勘误版七步型自举链终值（rederive-erratum.py 的 bootstrap，"
      "dps = 120、dps_cf = 250、A 用 +73）")
    w("K 上界：K_up^CF(m) = SdW 定理 3(d)，78 至 90 用 1.3993·m·δ^m，"
      "m 至 91 起用 1.4784·m·δ^m")
    w(f"判据：K 下界 > K 上界 则排除；δ = log 3 / log 2 = {nstr(delta, 24)}")
    w("")

    w(f"{'m':>4}  {'K 下界（链终值）':>26}  {'K 上界 K_up^CF(m)':>26}  "
      f"{'余量倍数':>28}  {'判定':<12}")
    w("—" * 50)

    for r in rows:
        w(f"{r['m']:>4}  {fmt_num(r['k_low'], 20):>26}  {fmt_num(r['up'], 20):>26}  "
          f"{(r['margin_str'] if r['margin_str'] else '无'):>28}  {r['verdict']:<12}")

    w("—" * 50)
    w("")
    w("要点")
    w("====")
    w(f"1. 能排除到的最大的 m = {m_star}")
    w(f"2. 第一个不能排除的 m = {first_not}")
    if m_star is not None and first_not is not None:
        at_star = [r for r in rows if r["m"] == m_star][0]
        at_not = [r for r in rows if r["m"] == first_not][0]
        w(f"   边界两侧：m = {m_star} 余量 {nstr(at_star['margin'], 24)}；"
          f"m = {first_not} 余量 {nstr(at_not['margin'], 12)}")
    w(f"3. 有上界的行共 {len(bounded)} 行（m = {ms_b[0]} 至 {ms_b[-1]}），"
      f"其中判定为排除的共 {len(excluded_ms)} 行"
      + (f"（m = {min(excluded_ms)} 至 {m_star}）" if excluded_ms else ""))
    w(f"4. m 至 77 以下没有此型上界：SdW 定理 3(b) 已另证 m 至 75 不存在非平凡圈，"
      f"76、77 由定理 3(c) 留作候选，故这 {len(rows) - len(bounded)} 行不由本路线判定")
    w("")
    w("自检")
    w("====")
    for i, (name, ok, detail) in enumerate(checks, 1):
        w(f"[{i}] {'通过' if ok else '未通过'}  {name}")
        w(f"    {detail}")
    w("")
    n_fail = len(failures)
    w(f"自检合计：{len(checks) - n_fail} / {len(checks)} 通过"
      + ("，全部通过" if n_fail == 0 else "，未通过：" + "、".join(failures)))
    w(f"退出码：{1 if n_fail else 0}")

    text = "\n".join(out) + "\n"
    print(text, end="")

    target = safe_target(TABLE_PATH, RESULTS_DIR)
    os.makedirs(str(target.parent), exist_ok=True)
    target.write_text(text, encoding="utf-8")

    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
