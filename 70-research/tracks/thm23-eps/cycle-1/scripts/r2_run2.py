#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r2_run2.py：七步链条的严格复算与「ε 印刷规则」假设检验（H1）。

检验对象（H1，来自 plan.md:64 至 :67 与 methods.md 第 2.1 节第 1 条）：
  H1：论文印刷的前六步 eps 等于「把按精确输入算出的 eps 向上取整到一位小数」。
以及必须一并处理的对照（同源假设）：
  H2'：若改用「3 位有效数字截断的 K 输入」或「论文印出的 K 输入」，
       同样的印刷规则能否复现七步印数。

输入（材料记录，见报告第 1 节；K 链来自 70-research/cycle-1/route-4.md:54 至 :60）：
  第 1 步入参 K = 7 * 10^11（SdW 定理 3）
  第 i 步入参 = 第 i-1 步的输出 q_min；第 7 步入参 = 205632218873398596256
论文印数（本次亲读 hercher5.txt:850 至 :876）：
  m2 >= 47, 67, 77, 82, 86, 88, 91
  eps < 6.9e-32, 5.1e-36, 4.1e-38, 2.3e-39, 2.3e-40, 5.3e-41, 1.11e-43
  K > 5.2e15, 3.97e17, 4.64e18, 2.74e19, 7.76e19, 2.05e20, 7.94e21

口径（每个口径独立执行「选 m2 -> 算 eps -> 判印刷」）：
  exact  ：入参 K 取精确值（我方链条值）
  trunc3 ：入参 K 取精确值的 3 位有效数字截断
  printed：入参 K 取论文印出的那个数（5.2e15 是 2 位有效数字，照印出取）
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r2_rig as R
from fractions import Fraction as F

OUT = []


def p(s=""):
    OUT.append(s)
    print(s)


# 快速档：证书仍需严格；改用「相对网格」每量保留 100 位有效数字，
# 避免绝对网格把微小的 eps（约 1e-43）截断成 1e-17 的相对宽度。
R.PREC = 100
N_AT = 70     # atanh 项数（ln2：尾约 3^-141）
N_L3 = 120    # ln3 = 2 atanh(1/2)，尾约 2^-241
N_LN = 70
N_EXP = 60

M = 91

STEPS = [
    # (步, 论文 m2, 精确入参 K, 论文印出的 K 字符串, 论文印出的 eps, 项目链条 eps 记录)
    (1, 47, 7 * 10 ** 11, "7e11", "6.9e-32", "6.89235e-32"),
    (2, 67, 5267319278509397, "5.2e15", "5.1e-36", "5.06614e-36"),
    (3, 77, 397560349370386783, "3.97e17", "4.1e-38", "4.00161e-38"),
    (4, 82, 4640282259296926456, "4.64e18", "2.3e-39", "2.2658e-39"),
    (5, 86, 27444133206411171953, "2.74e19", "2.3e-40", "2.25975e-40"),
    (6, 88, 77692117359936589403, "7.76e19", "5.3e-41", "5.20714e-41"),
    (7, 91, 205632218873398596256, "2.05e20", "1.11e-43", "1.22979e-43"),
]


def trunc_sig(n, sig):
    """n 的正整数 3 位（sig 位）有效数字截断（精确整数运算）。"""
    s = str(n)
    if len(s) <= sig:
        return n
    k = len(s) - sig
    return int(s[:sig]) * 10 ** k


def parse_sci(s):
    """'5.2e15' -> Fraction。"""
    m, e = s.split("e")
    return F(m) * F(10) ** int(e)


def rec_to_frac(s):
    m, e = s.split("e")
    return F(m) * F(10) ** int(e)


def decimals(s):
    m = s.split("e")[0]
    return len(m.split(".")[1]) if "." in m else 0


def rule_table(iv):
    """对 eps 区间给出六种规则在 1 位与 2 位小数下的预测尾数。"""
    out = {}
    for k in (1, 2):
        for rule in ("up", "near", "trunc"):
            r = R.rule_predict(iv, k, rule)
            out[(rule, k)] = R.mantissa_str(r[0], k) if r else "未定"
    return out


def main():
    t0 = time.time()
    p("=" * 100)
    p("r2_run2：七步链条的严格复算与印刷规则假设（H1）检验")
    p("精度档：相对网格（每量 100 位有效数字），atanh(1/3) %d 项、atanh(1/2) %d 项、exp %d 项（全部带显式尾界）"
      % (N_AT, N_L3, N_EXP))
    p("=" * 100)

    l2 = R.ln2_bounds(N_AT)
    l3 = R.ln3_bounds(N_L3)
    d = R.delta_bounds(N_AT, N_L3)
    C = R.C_bounds(R.X0_695, n=N_LN)
    p("")
    p("[0] 常数（本轮严格区间宽度：delta %s，C %s）"
      % (R.sci(d[1] - d[0], 4), R.sci(C[1] - C[0], 4)))
    p("    delta in [%s , %s]" % (R.sci(d[0], 40), R.sci(d[1], 40)))
    p("    C     in [%s , %s]" % (R.sci(C[0], 40), R.sci(C[1], 40)))

    # ---------- 第一步：可行性 -> m2 ----------
    p("")
    p("[1] 每个口径下用严格可行性判定选 m2（定理 21 前提；判 True 需区间上端 <= 右端）")
    plan = []
    for (step, m2_paper, K_exact, K_pr_s, eps_pr, eps_rec) in STEPS:
        row = {"step": step, "m2_paper": m2_paper, "K_exact": K_exact,
               "K_print": K_pr_s, "eps_print": eps_pr, "eps_rec": eps_rec}
        for mode in ("exact", "trunc3", "printed"):
            if mode == "exact":
                Kin = K_exact
            elif mode == "trunc3":
                Kin = trunc_sig(K_exact, 3)
            else:
                Kin = int(parse_sci(K_pr_s))
            m2f = R.max_feasible_m2(M, Kin, d[0], d[1], C)
            row[mode] = {"K_in": Kin, "m2_maxfeas": m2f}
        plan.append(row)
        p("  步 %d：入参 exact=%d  trunc3=%d  printed=%d ；max feasible m2：exact=%s trunc3=%s printed=%s（论文印 m2 >= %d）"
          % (step, row["exact"]["K_in"], row["trunc3"]["K_in"], row["printed"]["K_in"],
             row["exact"]["m2_maxfeas"], row["trunc3"]["m2_maxfeas"], row["printed"]["m2_maxfeas"], m2_paper))

    # ---------- 第二步：各口径下的 eps 与印刷规则判定 ----------
    p("")
    p("[2] 每个口径下按 max feasible m2 计算 eps 区间，并与论文印数做规则判定")
    p("    规则缩写：up1=向上取整到 1 位小数（H1），near1=四舍五入到 1 位，trunc1=截尾到 1 位，")
    p("             up2/near2/trunc2 为 2 位小数版本；「未定」= 区间跨规则边界")
    verdict = {}
    for row in plan:
        step = row["step"]
        kd = decimals(row["eps_print"])
        p("")
        p("  ==== 第 %d 步（论文印 eps < %s；项目链条记录 %s）====" % (step, row["eps_print"], row["eps_rec"]))
        for mode in ("exact", "trunc3", "printed"):
            m2 = row[mode]["m2_maxfeas"]
            Kin = row[mode]["K_in"]
            if isinstance(m2, tuple):          # 未定
                p("    [%s] K_in=%d：m2 判定未定，跳过" % (mode, Kin))
                continue
            iv, parts = R.eps_bounds(m2, M, Kin, d[0], d[1], l2, X0=R.X0_695, route="a")
            rl = rule_table(iv)
            txt = " ".join("%s=%s" % (k, v) for k, v in sorted(
                rl.items(), key=lambda kv: (kv[0][1], kv[0][0])))
            p("    [%s] K_in=%d  m2=%d  eps in [%s ," % (mode, Kin, m2, R.sci(iv[0], 25)))
            p("                     %s]" % R.sci(iv[1], 25))
            p("        区间相对宽度 %s ；规则预测：%s" % (R.sci((iv[1] - iv[0]) / iv[1], 4), txt))
            pr_mant = row["eps_print"].split("e")[0]
            hit = [("%s%d" % (k[0], k[1]), v) for k, v in rl.items() if v == pr_mant]
            p("        论文印数尾数 %s 命中规则：%s"
              % (pr_mant, ("、".join("%s" % h[0] for h in hit) if hit else "无")))
            # 与项目链条记录值对照（记录值是 6 位有效数字口径不一的十进制）
            rec = row["eps_rec"]
            nd = decimals(rec)
            rr = {}
            for rule in ("up", "near", "trunc"):
                r = R.rule_predict(iv, nd, rule)
                rr[rule] = R.mantissa_str(r[0], nd) if r else "未定"
            rec_mant = rec.split("e")[0]
            hitr = [rule for rule, v in rr.items() if v == rec_mant]
            p("        项目记录 %s（%d 位小数）命中：%s（向上/最近/截尾 = %s / %s / %s）"
              % (rec, nd, ("、".join(hitr) if hitr else "无"), rr["up"], rr["near"], rr["trunc"]))
            verdict[(step, mode)] = {"iv": iv, "m2": m2, "rules": rl, "print_hit": hit}

    # ---------- 第三步：H1 总表 ----------
    p("")
    p("[3] H1 总表（论文印数是否等于 up1，即向上取整到一位小数）")
    p("    步 | 口径 | m2 | 论文印 eps | up1 预测 | 是否命中 up1")
    for row in plan:
        step = row["step"]
        for mode in ("exact", "trunc3", "printed"):
            v = verdict.get((step, mode))
            if v is None:
                p("    %2d | %-7s | -- | %s | 未定 | 未定" % (step, mode, row["eps_print"]))
                continue
            p("    %2d | %-7s | %2d | %-9s | %s | %s"
              % (step, mode, v["m2"], row["eps_print"],
                 v["rules"][("up", 1)], "是" if v["rules"][("up", 1)] == row["eps_print"].split("e")[0] else "否"))

    # ---------- 第四步：第七步专项（1 位与 2 位小数全规则） ----------
    p("")
    p("[4] 第七步专项：印数 1.11e-43（2 位小数）在各口径下的规则命中")
    row7 = plan[-1]
    for mode in ("exact", "trunc3", "printed"):
        v = verdict.get((7, mode))
        if v is None:
            continue
        p("    口径 %s（K_in = %d, m2 = %d）：" % (mode, row7[mode]["K_in"], v["m2"]))
        for k in (1, 2):
            p("      %d 位小数：向上 %s / 四舍五入 %s / 截尾 %s"
              % (k, v["rules"][("up", k)], v["rules"][("near", k)], v["rules"][("trunc", k)]))

    # ---------- 第五步：相邻 m2 的 eps 比较（min-eps 约定核验） ----------
    p("")
    p("[5] min-eps 约定核验：从 max feasible m2 向下走，检查 eps 是否严格上升（区间比较）")
    for step, m2_paper, K_exact, K_pr_s, eps_pr, eps_rec in STEPS:
        m2 = R.max_feasible_m2(M, K_exact, d[0], d[1], C)
        if isinstance(m2, tuple):
            continue
        iv0, _ = R.eps_bounds(m2, M, K_exact, d[0], d[1], l2, X0=R.X0_695)
        ok = []
        cur = m2
        for down in range(1, 4):
            m2b = m2 - down
            if m2b < 1 or R.feasible_decision(m2b, M, K_exact, d[0], d[1], C) is not True:
                ok.append("m2=%d 不可行" % m2b)
                break
            ivb, _ = R.eps_bounds(m2b, M, K_exact, d[0], d[1], l2, X0=R.X0_695)
            strictly_bigger = iv0[0] < ivb[0]
            ok.append("eps(%d) < eps(%d)？%s" % (m2, m2b, strictly_bigger))
        p("    步 %d（m2 = %d）：%s" % (step, m2, "；".join(ok)))

    # ---------- 第六步：X0 = 704 变体（仅前六步与第七步 m2 的辅助对照） ----------
    p("")
    p("[6] 辅助对照：X0' = 704 * 2^60（arXiv v3 版本）")
    C4 = R.C_bounds(R.X0_704, n=N_LN)
    p("    C(704) in [%s , %s]" % (R.sci(C4[0], 40), R.sci(C4[1], 40)))
    for step, m2_paper, K_exact, K_pr_s, eps_pr, eps_rec in STEPS[:6]:
        m2 = R.max_feasible_m2(M, K_exact, d[0], d[1], C4)
        iv, _ = R.eps_bounds(m2, M, K_exact, d[0], d[1], l2, X0=R.X0_704)
        kk = decimals(eps_pr)
        r = R.rule_predict(iv, kk, "up")
        pred = R.mantissa_str(r[0], kk) if r else "未定"
        p("    步 %d：m2 = %s（695 版为 %s），up1 预测 %s，论文印 %s，命中？%s"
          % (step, m2, R.max_feasible_m2(M, K_exact, d[0], d[1], C), pred,
             eps_pr.split("e")[0], pred == eps_pr.split("e")[0]))
    m2_7 = R.max_feasible_m2(M, 205632218873398596256, d[0], d[1], C4)
    p("    第七步 m2（704 版）= %s（695 版为 %s）—— 第七步 A = 0，X0 不进该步公式"
      % (m2_7, R.max_feasible_m2(M, 205632218873398596256, d[0], d[1], C)))
    p("")
    p("用时 %.2f 秒" % (time.time() - t0))
    p("=" * 100)
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "r2_run2.out"), "w") as f:
        f.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
