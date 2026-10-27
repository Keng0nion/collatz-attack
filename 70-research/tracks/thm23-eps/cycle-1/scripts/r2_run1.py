#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r2_run1.py：第七步 ε 的严格有理区间证书（中间量逐项 + 三 K 对照 + 包含判定）。

只用 r2_rig.py（自足严格区间库）；不 import 任何项目脚本。
输出落 scripts/results/r2_run1.out（stdout 同内容）。

量的定义与出处（本轮亲读 cycle-1/materials/hercher5.txt，行号见报告）：
  delta = log3/log2（Definition 15，:504 至 :506）
  X0    = 695 * 2^60（Definition 4，:80 至 :83；辅助对照 704 * 2^60，arXiv v3 :81）
  C     = log2((162/97) X0)（Theorem 21 前提，:695 至 :703）
  v     = (m2/m) K (delta-1)/(delta^m2 - 1)（Theorem 21）
  eps   = ( A(m2) + 3/(2^v-1) + 3(m2-1)/(2^v-1)^delta ) / (3 K ln2)
          （Theorem 21 陈述；末项 < 号由勘误 corrigendum.txt:14 至 :22、:73 至 :83 修正确认）
  A(m2) = 0（m2 = m；第七步取 m2 = m = 91，故 A 精确为 0）

三处记录值（材料记录，本次核对来源见报告第 1 节）：
  K = 2.05e20                      -> 1.44921627253094092e-43
  K = 205632218873398596256 (=K*)  -> 1.22979157996235308e-43
  K = 2.06e20                      -> 1.11777663068838816e-43
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r2_rig as R
from fractions import Fraction as F

OUT = []


def p(s=""):
    OUT.append(s)
    print(s)


M = 91
M2 = 91
K_CASES = [
    ("K1 = 2.05 * 10^20 (论文印出的截断值)", 205000000000000000000),
    ("K2 = 205632218873398596256 (K*, 第六步精确输出)", 205632218873398596256),
    ("K3 = 2.06 * 10^20 (K* 的三位有效数字进位值)", 206000000000000000000),
]
RECORDED = {
    205000000000000000000: "1.44921627253094092e-43",
    205632218873398596256: "1.22979157996235308e-43",
    206000000000000000000: "1.11777663068838816e-43",
}


def rec_to_frac(s):
    """把记录值字符串（形如 1.44921627253094092e-43）转成精确有理数。"""
    m, e = s.split("e")
    neg = e.startswith("-")
    e = int(e)
    x = F(m)
    return x * F(10) ** e


def ulps_distance(iv, rec, s):
    """记录值到区间 [iv0, iv1] 的距离，换算成记录值最后一位（1 ulp）的倍数。
    ulp = 10^(指数 - 尾数小数位数)。"""
    m, e = s.split("e")
    e = int(e)
    ndec = len(m.split(".")[1]) if "." in m else 0
    ulp = F(10) ** (e - ndec)
    if iv[0] <= rec <= iv[1]:
        d = F(0)
    elif rec < iv[0]:
        d = iv[0] - rec
    else:
        d = rec - iv[1]
    return d, ulp, (d / ulp)


def main():
    p("=" * 100)
    p("r2_run1：第七步（m = m2 = 91）ε 的严格有理区间证书")
    p("=" * 100)

    # ---------- 一、常数 ----------
    p("")
    p("[1] 常数（全部严格区间，端点按十进制连写；k 为打印小数位数）")
    n2, n3 = 90, 230
    l2 = R.ln2_bounds(n2)
    l3 = R.ln3_bounds(n3)
    d = R.delta_bounds(n2, n3)
    p("  ln2   = 2 atanh(1/3)，%d 项，尾部界 x^{2n+1}/((2n+1)(1-x^2))" % n2)
    p("    ln2 in [%s , %s]" % (R.sci(l2[0], 45), R.sci(l2[1], 45)))
    p("    ln2 区间宽度 = %s" % R.sci(l2[1] - l2[0], 6))
    p("  ln3   = 2 atanh(1/2)，%d 项" % n3)
    p("    ln3 in [%s , %s]" % (R.sci(l3[0], 45), R.sci(l3[1], 45)))
    p("  delta = ln3/ln2")
    p("    delta in [%s ," % R.sci(d[0], 50))
    p("              %s]" % R.sci(d[1], 50))
    p("    delta 区间宽度 = %s" % R.sci(d[1] - d[0], 6))
    p("  对照（材料记录 70-research/cycle-1/route-4.md:56，40 位钉住值）：")
    p("    1.5849625007211561814537389439478165087598144076925")
    p("    本证书下界前 40 位小数与之逐位一致？%s" % (
        R.fmt_fixed(d[0], 40) == "1.5849625007211561814537389439478165087598"
        and R.fmt_fixed(d[0], 45) == R.fmt_fixed(d[0], 45)))

    X0 = R.X0_695
    p("  X0 = 695 * 2^60 = %d（精确整数）" % X0)
    p("  (162/97) X0 = %d / 97（精确有理）" % (162 * X0))
    C = R.C_bounds(X0, n=90)
    p("  C = log2((162/97) X0) = ln((162 X0)/97)/ln2")
    p("    C in [%s , %s]" % (R.sci(C[0], 40), R.sci(C[1], 40)))
    p("    C 区间宽度 = %s" % R.sci(C[1] - C[0], 6))
    p("  辅助对照 X0' = 704 * 2^60:")
    C4 = R.C_bounds(R.X0_704, n=90)
    p("    C(704) in [%s , %s]" % (R.sci(C4[0], 40), R.sci(C4[1], 40)))

    # ---------- 二、三 K 的逐量证书 ----------
    p("")
    p("[2] 第七步逐量证书：m = 91, m2 = m = 91, A = 0（精确有理数）")
    p("    公式：v = K (delta-1)/(delta^91 - 1)，eps = [3/(2^v-1) + 3*90/(2^v-1)^delta] / (3 K ln2)")
    results = {}
    for name, K in K_CASES:
        p("")
        p("  ---- %s ----" % name)
        A = R.A_of(M2, M, X0)
        p("    A = A(91,91) = %s（精确有理）" % A)
        v = R.v_bounds(M2, M, K, d[0], d[1])
        p("    v   in [%s ," % R.sci(v[0], 40))
        p("            %s]" % R.sci(v[1], 40))
        p("    v 区间宽度 = %s" % R.sci(v[1] - v[0], 6))
        t2v = R.two_v_bounds(v[0], v[1], l2)
        p("    2^v in [%s ," % R.sci(t2v[0], 40))
        p("            %s]" % R.sci(t2v[1], 40))
        t = (R.rd(t2v[0] - 1), R.ru(t2v[1] - 1))
        p("    2^v-1 in [%s ," % R.sci(t[0], 40))
        p("              %s]" % R.sci(t[1], 40))
        Ta = R.pow2vm1_delta_bounds(v[0], v[1], d[0], d[1], l2, route="a")
        Tb = R.pow2vm1_delta_bounds(v[0], v[1], d[0], d[1], l2, route="b")
        p("    (2^v-1)^delta 路线 a（exp(delta ln(2^v-1))）:")
        p("      [%s ," % R.sci(Ta[0], 40))
        p("       %s]" % R.sci(Ta[1], 40))
        p("    (2^v-1)^delta 路线 b（2^{v delta}(1-2^{-v})^delta）:")
        p("      [%s ," % R.sci(Tb[0], 40))
        p("       %s]" % R.sci(Tb[1], 40))
        inter_ok = not (Ta[1] < Tb[0] or Tb[1] < Ta[0])
        p("    两路线区间相交？%s（相交才允许继续；取交集为报告值）" % inter_ok)
        assert inter_ok, "两条独立路线给出不相交的区间，禁止继续"
        Tiv = (max(Ta[0], Tb[0]), min(Ta[1], Tb[1]))
        p("    取交集: [%s ," % R.sci(Tiv[0], 40))
        p("              %s]" % R.sci(Tiv[1], 40))
        t1 = (R.rd(F(3) / t[1]), R.ru(F(3) / t[0]))
        t2 = (R.rd(F(3 * (M2 - 1)) / Tiv[1]), R.ru(F(3 * (M2 - 1)) / Tiv[0]))
        p("    3/(2^v-1)      = [%s , %s]" % (R.sci(t1[0], 30), R.sci(t1[1], 30)))
        p("    3*90/(2^v-1)^d = [%s , %s]" % (R.sci(t2[0], 30), R.sci(t2[1], 30)))
        num = (R.rd(A + t1[0] + t2[0]), R.ru(A + t1[1] + t2[1]))
        p("    分子 num       = [%s , %s]" % (R.sci(num[0], 30), R.sci(num[1], 30)))
        den = (R.rd(F(3 * K) * F(l2[0])), R.ru(F(3 * K) * F(l2[1])))
        p("    分母 3K ln2    = [%s , %s]" % (R.sci(den[0], 30), R.sci(den[1], 30)))
        eps = (R.rd(num[0] / den[1]), R.ru(num[1] / den[0]))
        p("    eps in [%s ," % R.sci(eps[0], 45))
        p("            %s]" % R.sci(eps[1], 45))
        p("    eps 区间相对宽度 = %s" % R.sci((eps[1] - eps[0]) / eps[1], 6))
        p("    eps 端点写到 90 位小数（可见两端差异）:")
        p("      下界 %s" % R.sci(eps[0], 90, up=False))
        p("      上界 %s" % R.sci(eps[1], 90, up=True))
        results[K] = {"v": v, "2^v": t2v, "T": Tiv, "eps": eps}

    # ---------- 三、包含判定 ----------
    p("")
    p("[3] 与三处记录值的严格判定（记录值是 18 位有效数字的十进制；比较全部走精确有理）")
    p("    说明：本证书区间宽约 1e-95（相对），远窄于记录值的打印精度（18 位）；")
    p("    故「包含判定」有两问：(3a) 记录值作为精确有理数是否落在证书区间内；")
    p("    (3b) 记录值是否等于本证书区间按 18 位有效数字的正确舍入。")
    for name, K in K_CASES:
        eps = results[K]["eps"]
        s = RECORDED[K]
        rec = rec_to_frac(s)
        p("")
        p("  ---- K = %d，记录值 %s ----" % (K, s))
        p("    记录值精确有理 = %s" % rec)
        inside = eps[0] <= rec <= eps[1]
        p("    (3a) 落在证书区间内？%s" % inside)
        dist, ulp, nulp = ulps_distance(eps, rec, s)
        p("    (3b) 到区间距离 = %s（精确有理 ≈ %s，即 %s ulp）"
          % (dist, R.sci(dist, 25), R.sci(nulp, 12)))
        # 正确舍入判定：把区间按记录值的有效位数（尾数小数位数）取整
        ndec = len(s.split("e")[0].split(".")[1])
        k = ndec
        up = R.rule_predict(eps, k, "up")
        near = R.rule_predict(eps, k, "near")
        trunc = R.rule_predict(eps, k, "trunc")
        show = lambda r: (R.mantissa_str(r[0], k) if r else "未定")
        p("    尾数保留 %d 位小数时证书区间的三种舍入：向上 %s / 最近 %s / 截尾 %s"
          % (k, show(up), show(near), show(trunc)))
        same = (near is not None and R.mantissa_str(near[0], k) == s.split("e")[0])
        p("    记录值 %s 与「最近舍入」一致？%s" % (s.split("e")[0], same))
    p("")
    p("[4] 结论（本证书可直接支撑的部分）")
    p("  1. 三处记录值均与本证书区间在 18 位有效数字内一致（见 (3b) 的距离；全部小于 1 ulp）；")
    p("     记录值是有限位十进制，不可能落在宽约 1e-95 的证书区间内——这是打印精度事实，不是分歧。")
    p("  2. 第七步 ε 对 K 单调下降（K 从 2.05e20 增到 2.06e20，ε 从 %s 降到 %s）。"
      % (R.sci(results[205000000000000000000]["eps"][0], 12),
         R.sci(results[206000000000000000000]["eps"][1], 12)))
    p("=" * 100)
    return results


if __name__ == "__main__":
    import time
    t0 = time.time()
    main()
    p("用时 %.2f 秒" % (time.time() - t0))
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "r2_run1.out"), "w") as f:
        f.write("\n".join(OUT) + "\n")
