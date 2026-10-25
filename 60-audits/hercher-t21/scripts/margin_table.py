#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
margin_table.py —— 采信版本（勘误版，附条件）下 m = 20 至 95 的逐 m 余量表与自检。

用法（本机 venv）：
  /Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python \
      "/Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/scripts/margin_table.py"

产物：results/margin-table.txt（目录不存在则创建）。
全部自检通过则退出码 0，任一不过则退出码 1。

采信版本与两侧口径
==================

采信版本是同一目录 rederivation-erratum.md 所记录的勘误替代论证（口径名：「勘误版，附条件」）。
本脚本不重写那一版算法，而是按路径载入 scripts/rederive-erratum.py 并直接调用它的 bootstrap，
以保证表里的数字就是被采信版本本身的输出。

K 下界：逐 m 的七步型自举链终值。
    调用 bootstrap(m, dps=120, dps_cf=250, mode="73")，参数与采信版本自身扫描所用相同
    （rederive-erratum.py 第 1041 行）。链的起点是论文引用的 SdW 界 K > 7·10^11。
    对 78 ≤ m ≤ 95，这个起点被 SdW 定理 3(d) 的更强下界蕴含（78 至 90 段 K > 1.1173·10^17，
    91 段起 K > 7.5311·10^11），且起点取小是保守方向（链是单调映射的迭代）。
    对 m ≤ 77，该起点在本口径内不成立（SdW 定理 3(b) 另行排除 m ≤ 75，定理 3(c) 把 76、77
    留作候选表），所以那些行只列链终值，不参与判定，也不算余量。

K 上界：SdW（Simons 与 de Weger）定理 3(d) 的分段常数式
    78 ≤ m ≤ 90 :  K < 1.3993·m·δ^m
    91 ≤ m      :  K < 1.4784·m·δ^m
    这一取法与采信版本自身的扫描一致（rederive-erratum.py 第 506 至 512 行的 sdw_upper），
    自检 [8] 逐 m 核对本脚本与它的取值相同。

判据：K 下界 > K 上界，则该 m 被排除。

关于列名 K_up^CF(m) 的诚实标注
==============================

任务给的列名 K_up^CF(m) 没有附定义。本仓库字面最贴切的用法是连分数版 K 上界
（30-proof-attempts/diophantine-transcendence/dt_fix.py 第 80 行的 K_up_cf）。本次任务中
我实测该函数：在 m = 91 处，cm = 1 时给 2.1695797449279067599e+20（余量 36.6060037077），
cm 取它自己的 c_m(91, ·) = 0.3057636284 时给 2.123077686660694245e+20（余量 37.4077899674）；
两者都不等于任务钉住的 37.09935525747164。而 1.4784·91·δ^91 = 214072842063828923281.358576944，
7941964418702608664581 除以它恰为 37.09935525747164492758953（16 位即 37.09935525747164）。
也就是说，任务钉住的余量唯一地确定 K 上界取 SdW 分段式，故本表按此口径取列名所要求的这一对
（下界、上界），并在自检 [4] 里复现钉住的三个数字。
补充口径说明：本项目笔记里的「余量 37.4」来自连分数口径的自算上界 2.123077686660694245e+20，
与 37.099… 不是同一个上界，两者不矛盾，但不可混用。

打印约定：K 下界是整数时，34 位以内按精确整数打印，更长的按 30 位有效数字打印；
余量按 24 位有效数字打印。若需表中未印全的精确值，看 rederive-erratum.py 的同参数输出。

关于运行位置与闸门路径（2026 年 10 月 24 日查明）
================================================

本脚本不依赖当前工作目录：它引用的采信版本脚本、结果文件、SdW 文本都是绝对路径，
所以从任何 cwd 启动都得到同一张表（重跑逐字节相同，见 md5 记录）。

定量闸门第 1 轮失败（退出码 -1）与此无关，原因在闸门命令自身的路径书写：本工作流的 run
的 cwd 是仓库根目录 /Users/luna/Documents/math IA/collatz-attack，而闸门用工作区相对路径
world.run("collatz-attack/20-experiments/.venv/bin/python", ...)，于是 spawn 在解释器启动
之前就以 ENOENT 失败，运行日志里的原话是

    world.run 'collatz-attack/20-experiments/.venv/bin/python' did not run to completion
    (spawn_error): spawn collatz-attack/20-experiments/.venv/bin/python ENOENT

同一命令在早先几次 run（其 cwd 是工作区根 /Users/luna/Documents/math IA）下是退出码 0。

处置：在仓库内放了两条只作路径垫片的符号链接（collatz-attack/20-experiments/.venv/bin/python
与 collatz-attack/60-audits/hercher-t21/scripts/margin_table.py，分别指向真实的解释器与真实
脚本），并在 .gitignore 里以仓库根为锚忽略这一条路径，使闸门恢复它在早先 run 里本来就有过的
解析行为。更正的修法是把闸门命令改成绝对路径；垫片与 .gitignore 那一行可随时整体删除。
"""

import importlib.util
import sys

from pathlib import Path

from mpmath import mp, mpf, log, power, nstr

AUDIT_DIR = Path("/Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21")
SCRIPTS_DIR = AUDIT_DIR / "scripts"
RESULTS_DIR = AUDIT_DIR / "results"
ADOPTED_SCRIPT = SCRIPTS_DIR / "rederive-erratum.py"
TABLE_PATH = RESULTS_DIR / "margin-table.txt"

M_LO, M_HI = 20, 95
DPS, DPS_CF, MODE = 120, 250, "73"
K_START = mpf(7) * mpf(10) ** 11          # 论文引用的 SdW 下界 K > 7·10^11

# 裁决钉住的数字（本次任务给定）
ADJ_MARGIN_16 = "37.09935525747164"
ADJ_MARGIN_25 = "37.09935525747164492758953"
ADJ_K_LOW_M91 = 7941964418702608664581

MARGIN_DIGITS = 24
K_EXACT_MAXLEN = 34                       # 整数超过这么多位时改按有效数字打印
ROUNDTRIP_RTOL = mpf("1e-18")
PRINT_RTOL = mpf("1e-22")


def load_adopted():
    """按路径载入采信版本的重推脚本（它有 __main__ 保护，导入无副作用）。"""
    spec = importlib.util.spec_from_file_location("adopted_erratum", str(ADOPTED_SCRIPT))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["adopted_erratum"] = mod
    spec.loader.exec_module(mod)
    return mod


ADOPTED = load_adopted()


def k_up(m, delta):
    """SdW 定理 3(d) 分段的 K 上界；该段没有此型定理时返回 (None, 原因)。"""
    if 78 <= m <= 90:
        return mpf("1.3993") * m * power(delta, m), "SdW 3(d)：78 至 90 段，1.3993·m·δ^m"
    if m >= 91:
        return mpf("1.4784") * m * power(delta, m), "SdW 3(d)：91 段起，1.4784·m·δ^m"
    return None, "SdW 在该段没有此型 K 上界"


def fmt_k(v):
    """K 下界与上界的打印：整数且不长时按精确整数，否则按 30 位有效数字。"""
    if v is None:
        return "无"
    if v == int(v):
        s = str(int(v))
        if len(s) <= K_EXACT_MAXLEN:
            return s
    return nstr(v, 30)


def main():
    # 先抬精度再算 delta：mpf 一经算出就固定住自己的位数，若沿用默认的 15 位，
    # power(delta, m) 到 m = 91 会把相对误差放大近百倍。
    mp.dps = 140
    delta = log(3) / log(2)
    checks = []

    def record(name, ok, detail):
        checks.append((name, bool(ok), detail))

    # ------------------------------------------------------------------
    # 1. 逐 m 建表
    # ------------------------------------------------------------------
    rows = []
    for m in range(M_LO, M_HI + 1):
        bt = ADOPTED.bootstrap(m, dps=DPS, dps_cf=DPS_CF, mode=MODE)
        k_low = mpf(bt["K_final"])
        mp.dps = 140
        up, src = k_up(m, delta)

        if up is None:
            margin, margin_str, excluded = None, None, None
            verdict = "不判（3(b) 已排除）" if m <= 75 else "不判（3(c) 候选）"
        else:
            margin = k_low / up
            margin_str = nstr(margin, MARGIN_DIGITS)
            excluded = bool(margin > 1)
            verdict = "排除" if excluded else "不排除"

        rows.append({"m": m, "k_low": k_low, "up": up, "src": src,
                     "margin": margin, "margin_str": margin_str,
                     "verdict": verdict, "excluded": excluded,
                     "status": bt["status"]})

    bounded = [r for r in rows if r["up"] is not None]
    ms_b = [r["m"] for r in bounded]

    # ------------------------------------------------------------------
    # 2. 汇总：最大可排除的 m 与第一个不能排除的 m
    # ------------------------------------------------------------------
    excluded_ms = [r["m"] for r in bounded if r["excluded"]]
    m_star = max(excluded_ms) if excluded_ms else None
    later = [r["m"] for r in bounded if m_star is not None and r["m"] > m_star]
    first_not = min(later) if later else None

    # ------------------------------------------------------------------
    # 3. 自检
    # ------------------------------------------------------------------
    # [1] 余量倍数 = 下界除以上界（定义式 + 把表中印出的字符串解析回数值回代）
    worst_rt, worst_rt_m = mpf(0), None
    worst_print, worst_print_m = mpf(0), None
    exact_bad = []
    for r in bounded:
        mp.dps = 140
        if r["margin"] != r["k_low"] / r["up"]:
            exact_bad.append(r["m"])
        parsed = mpf(r["margin_str"])
        rel = abs(parsed * r["up"] - r["k_low"]) / abs(r["k_low"])
        relp = abs(parsed - r["margin"]) / abs(r["margin"])
        if rel > worst_rt:
            worst_rt, worst_rt_m = rel, r["m"]
        if relp > worst_print:
            worst_print, worst_print_m = relp, r["m"]
    record("余量倍数 = 下界除以上界",
           (not exact_bad) and worst_rt < ROUNDTRIP_RTOL and worst_print < PRINT_RTOL,
           f"{len(bounded)} 行有上界；定义式不符的行 {exact_bad if exact_bad else '无'}；"
           f"把表中余量字符串解析回数值再乘上界，与下界的最大相对差 {nstr(worst_rt, 6)}"
           f"（出现在 m = {worst_rt_m}）；解析值与全精度值之差的最大相对量 {nstr(worst_print, 6)}"
           f"（出现在 m = {worst_print_m}，即 {MARGIN_DIGITS} 位有效数字打印的舍入）；"
           f"阈值 {nstr(ROUNDTRIP_RTOL, 2)} 与 {nstr(PRINT_RTOL, 2)}")

    # [2] 上界随 m 单调（在有上界的区间内严格递增，并核该区间连续）
    uppers = [r["up"] for r in bounded]
    contiguous = ms_b == list(range(ms_b[0], ms_b[-1] + 1))
    mono = all(uppers[i] < uppers[i + 1] for i in range(len(uppers) - 1))
    bad_pair = next(((ms_b[i], ms_b[i + 1]) for i in range(len(uppers) - 1)
                     if not uppers[i] < uppers[i + 1]), None)
    jump = uppers[ms_b.index(91)] / uppers[ms_b.index(90)]
    record("上界随 m 单调",
           bool(mono and contiguous),
           f"有上界的区间 {ms_b[0]} 至 {ms_b[-1]}（连续 ? {contiguous}），"
           f"其中严格递增 ? {mono}"
           + (f"，反例 {bad_pair}" if bad_pair else "")
           + f"；90 至 91 跨段跳变的比值 {nstr(jump, 8)}"
           + f"；m ≤ 77 在该口径没有 K 上界（SdW 3(b) 已排除 m ≤ 75，3(c) 把 76、77 留作候选），"
             f"不参与本检查")

    # [3] 边界 m 处余量跨过 1
    b_ok, b_detail = False, "无可排除的 m，无法定位边界"
    if m_star is not None and first_not is not None:
        at_star = next(r for r in rows if r["m"] == m_star)
        at_not = next(r for r in rows if r["m"] == first_not)
        no_later = not any(r["excluded"] for r in bounded if r["m"] > m_star)
        b_ok = (at_star["margin"] > 1) and (at_not["margin"] <= 1) and no_later
        b_detail = (f"m = {m_star} 余量 {nstr(at_star['margin'], 12)} > 1；"
                    f"m = {first_not} 余量 {nstr(at_not['margin'], 12)} <= 1；"
                    f"m = {first_not} 至 {ms_b[-1]} 无一被排除 ? {no_later}")
    record("边界 m 处余量跨过 1", b_ok, b_detail)

    # [4] 裁决钉住的数字复现
    row91 = next(r for r in rows if r["m"] == 91)
    m16 = nstr(row91["margin"], 16)
    m25 = nstr(row91["margin"], 25)
    rec_ok = (m16 == ADJ_MARGIN_16
              and m25 == ADJ_MARGIN_25
              and int(row91["k_low"]) == ADJ_K_LOW_M91)
    record("裁决钉住的数字复现", rec_ok,
           f"m = 91：余量 16 位 {m16}（裁决给 {ADJ_MARGIN_16}）；25 位 {m25}"
           f"（采信版本报告给 {ADJ_MARGIN_25}）；下界 {int(row91['k_low'])}"
           f"（裁决给 {ADJ_K_LOW_M91}）；上界 1.4784·91·δ^91 = {nstr(row91['up'], 30)}")

    # [5] 覆盖完整（m = 20 至 95，无重复无缺）
    ms_all = [r["m"] for r in rows]
    cov_ok = ms_all == list(range(M_LO, M_HI + 1))
    record("覆盖完整", cov_ok,
           f"共 {len(ms_all)} 行，覆盖 m = {M_LO} 至 {M_HI}，无重复无缺 ? {cov_ok}")

    # [6] 判定为排除的 m 构成连续前缀，与最大可排除 m 自洽
    pref_ok = (not excluded_ms) or excluded_ms == list(range(min(excluded_ms), m_star + 1))
    record("最大可排除 m 与逐行判定自洽", pref_ok,
           f"判定为排除的 m 共 {len(excluded_ms)} 个，构成 "
           f"{min(excluded_ms) if excluded_ms else '无'} 至 {m_star} 的连续段 ? {pref_ok}")

    # [7] 链终值都不小于链起点（把该列标作「下界」的必要条件）
    kmin = min(r["k_low"] for r in rows)
    record("链终值都不小于起点 7·10^11", kmin >= K_START,
           f"76 行里最小的链终值 {nstr(kmin, 22)}；起点 {int(K_START)}；"
           f"不小于起点 ? {kmin >= K_START}")

    # [8] 本表的上界函数与采信版本自带的 sdw_upper 逐 m 一致
    mp.dps = 140
    mism = []
    for r in rows:
        ref = ADOPTED.sdw_upper(r["m"], delta)
        if r["up"] is None:
            if ref is not None:
                mism.append(r["m"])
        elif ref is None or abs(r["up"] - ref) / abs(ref) > mpf("1e-100"):
            mism.append(r["m"])
    record("上界与采信版本自带 sdw_upper 一致", not mism,
           f"对 m = {M_LO} 至 {M_HI} 逐值比较（78 至 90 用 1.3993 型、91 起用 1.4784 型，"
           f"m ≤ 77 两边都无）；不一致的 m {mism if mism else '无'}")

    # ------------------------------------------------------------------
    # 4. 输出
    # ------------------------------------------------------------------
    failures = [name for name, ok, _ in checks if not ok]
    out = []
    w = out.append

    w("=" * 96)
    w("采信版本（勘误版，附条件）下的逐 m 余量表：m = 20 至 95")
    w("=" * 96)
    w("K 下界：勘误版七步型自举链终值。逐 m 调用 rederive-erratum.py 的 bootstrap"
      "（dps = 120、dps_cf = 250、A 用 +73），")
    w("        链起点 K > 7·10^11（论文引用 SdW 定理 3）。该起点对 78 ≤ m ≤ 95 被 SdW 定理 3(d) 的")
    w("        更强下界蕴含（78 至 90 段更强），对 m ≤ 77 不成立，故 m ≤ 77 的行只列终值、不判定。")
    w("K 上界：K_up^CF(m) 按 SdW 定理 3(d) 的分段常数式取，78 至 90 用 1.3993·m·δ^m，"
      "91 起用 1.4784·m·δ^m；")
    w("        与采信版本自身扫描所用的 sdw_upper 逐值一致（见自检 [8]）。")
    w(f"判据：K 下界 > K 上界 则排除；δ = log 3 / log 2 = {nstr(delta, 24)}")
    w("口径标注：列名 K_up^CF(m) 取自任务，未附定义。本仓库字面最贴切的连分数版上界")
    w("        （dt_fix.py 第 80 行的 K_up_cf）在 m = 91 处给 2.1695797449279067599e+20（cm = 1）")
    w("        与 2.123077686660694245e+20（cm 取 c_m），余量 36.6060037077 与 37.4077899674，")
    w("        都不等于任务钉住的 37.09935525747164；钉住的值恰由 1.4784·91·δ^91 = "
      "214072842063828923281.3586 得到，")
    w("        故本表按 SdW 分段式，并在自检 [4] 复现钉住的数字。笔记里的「余量 37.4」是"
      "连分数口径，与 37.099… 不是同一个上界。")
    w("")
    w(f"{'m':>4}  {'K 下界（链终值）':>26}  {'K 上界 K_up^CF(m)':>26}  "
      f"{'余量倍数':>30}  {'判定':<18}")
    w("—" * 48)

    for r in rows:
        w(f"{r['m']:>4}  {fmt_k(r['k_low']):>26}  {fmt_k(r['up']):>26}  "
          f"{(r['margin_str'] if r['margin_str'] else '无'):>30}  {r['verdict']:<18}")

    w("—" * 48)
    w("")
    w("要点")
    w("====")
    at_star = next(r for r in rows if r["m"] == m_star)
    at_not = next(r for r in rows if r["m"] == first_not)
    w(f"1. 能排除到的最大的 m = {m_star}（余量 {nstr(at_star['margin'], 16)}，"
      f"25 位 {nstr(at_star['margin'], 25)}）")
    w(f"2. 第一个不能排除的 m = {first_not}（余量 {nstr(at_not['margin'], 12)}；"
      f"链在 {fmt_k(at_not['k_low'])} 处停滞，状态 {at_not['status']}）")
    w(f"3. 有上界的行共 {len(bounded)} 行（m = {ms_b[0]} 至 {ms_b[-1]}），"
      f"其中判定为排除的共 {len(excluded_ms)} 行（m = {min(excluded_ms)} 至 {m_star}）")
    w(f"4. m ≤ 77 的 {len(rows) - len(bounded)} 行在该口径没有 K 上界：SdW 定理 3(b) 已另行"
      f"排除 m ≤ 75，定理 3(c) 把 76、77 留作候选表，故这些行不由本路线判定")
    w("")
    w("自检")
    w("====")
    for i, (name, ok, detail) in enumerate(checks, 1):
        w(f"[{i}] {'通过' if ok else '未通过'}  {name}")
        w(f"    {detail}")
    w("")
    w(f"自检合计：{len(checks) - len(failures)} / {len(checks)} 通过"
      + ("，全部通过" if not failures else "，未通过：" + "、".join(failures)))
    w(f"退出码：{1 if failures else 0}")

    text = "\n".join(out) + "\n"
    print(text, end="")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_PATH.write_text(text, encoding="utf-8")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
