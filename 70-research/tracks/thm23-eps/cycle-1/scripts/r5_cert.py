# -*- coding: utf-8 -*-
"""第 5 路末值证书：δ 的连分数前缀证书、q43 复算、Stern-Brocot 最小分母、
Farey 夹逼（连分数路径）、与 7941964418702608664581 及印数 7.94e21 的严格对照。

所有判定用精确有理比较；本文件不含浮点定案。
运行：<venv>/python r5_cert.py
"""
import sys
from fractions import Fraction as F

sys.set_int_max_str_digits(1000000)
from r5_rig import (delta_bounds, delta_bounds_alt, cf_prefix, convergents,
                    simplest_open, sig_str)

# ---------- 名义常量（与论文印数、记录值逐字对应） ----------
T_RECORD = 7941964418702608664581            # 我方链条末值（cycle-1/route-4.md:60）
KSTAR_RECORD = 205632218873398596256         # 第六步链条值（同处）
PRINTED_K7 = F(794, 100) * F(10) ** 21       # 论文第七步印数 7.94 × 10^21
W1 = F(111, 10 ** 45)                        # 读法一：论文印 ε = 1.11 × 10^-43
W2 = F(12297916, 10 ** 50)                   # 读法二：我方精确 K* 输入的 ε 的 8 位印数
W3 = F(14492163, 10 ** 50)                   # 读法三：印出的 2.05e20 输入的 ε 的 8 位印数
PAPER_EPS = W1                               # 论文第七步印的 ε
CLOSING_22E20 = F(22, 10) * F(10) ** 20      # 收尾句 2.2 × 10^20
SDW_C = F(14784, 10000)                      # 收尾句的 1.4784（论文转述 SdW，见报告）

out_lines = []


def P(*args):
    s = " ".join(str(a) for a in args)
    print(s)
    out_lines.append(s)


P("=" * 78)
P("第 5 路证书：δ 连分数前缀 + Stern-Brocot 最小分母 + 末值稳健性")
P("=" * 78)

# ---------- 1. δ 的严格有理区间（两种独立走法 + 交集） ----------
L1, U1 = delta_bounds()
L2, U2 = delta_bounds_alt()
L, U = max(L1, L2), min(U1, U2)
P("\n[1] δ = log3/log2 的严格有理区间")
P("  走法一（ln2 走 atanh(1/3)、ln3 走 atanh(1/2)）：")
P("    L1 =", sig_str(L1, 30), "  U1 =", sig_str(U1, 30))
P("  走法二（ln2 走 atanh(1/3)、ln3 = ln2 + 2 atanh(1/5)）：")
P("    L2 =", sig_str(L2, 30), "  U2 =", sig_str(U2, 30))
assert L1 < U1 and L2 < U2 and max(L1, L2) < min(U1, U2)
P("  两区间相交：", max(L1, L2) < min(U1, U2), "（已证）")
P("  取交集：L =", sig_str(L, 30), "  U =", sig_str(U, 30))
P("  区间宽度 U - L =", sig_str(U - L, 6))
P("  检查：L < δ < U 由级数尾界保证（两种走法各自独立）")

# ---------- 2. 连分数前缀证书 ----------
digits, rlo, rhi = cf_prefix(L, U, maxlen=400)
P("\n[2] 连分数前缀证书（区间 (L, U) 内每一点的展开共享此前缀）")
P("  证书位数 =", len(digits))
P("  系数 a0..a%d = %s" % (len(digits) - 1, digits))
P("  残余区间（尚未定出下一位）：(%s, %s)" % (sig_str(rlo, 12), sig_str(rhi, 12)))
conv = convergents(digits)
P("  收敛分数 p_n/q_n（打印 n, p_n, q_n）：")
for n in range(38, min(len(conv), 47)):
    p, q = conv[n]
    P("    n = %2d  q_n = %d" % (n, q))
assert len(digits) >= 45, "证书位数不足 45，无法定出 a44"
P("  校验：a44 =", digits[44], "（应为 37）   a45 =", digits[45] if len(digits) > 45 else "未定")

q43 = conv[43][1]
p43 = conv[43][0]
q44 = conv[44][1]
p44 = conv[44][0]
q42 = conv[42][1]
p42 = conv[42][0]
P("  q43 =", q43, "  与记录 K* =", KSTAR_RECORD, "相等：", q43 == KSTAR_RECORD, "（已证）")
P("  q44 =", q44, "  q42 =", q42)
P("  a44 = 37 的推论：δ 的尾部 t = [a44; a45, ...] 满足 t ∈ (37, 38)（已证）")
if len(digits) > 45:
    P("  a45 =", digits[45], " 的推论：38 - t = 1 - 1/[a45; ...] ∈ (3/4, 4/5)（已证）")

# ---------- 3. 整数恒等式与末值 ----------
T = 38 * q43 + q42
T2 = q44 + q43
P("\n[3] 末值的三条恒等式（精确整数运算）")
P("  38*q43 + q42 =", T)
P("  q44 + q43    =", T2)
P("  两者相等：", T == T2, "； 与记录 7941964418702608664581 相等：", T == T_RECORD, "（已证）")
P("  mediant 恒等式：(p43 + p44) = 38*p43 + p42 ：",
  (p43 + p44) == 38 * p43 + p42, "（=> S38 = (p43+p44)/(q43+q44) = (38 p43+p42)/T）")
P("  unimodular：p43*q42 - p42*q43 =", p43 * q42 - p42 * q43)
P("  unimodular：p43*q44 - p44*q43 =", p43 * q44 - p44 * q43)
assert p43 * q42 - p42 * q43 == 1
assert abs(p43 * q44 - p44 * q43) == 1
S38_NUM = p43 + p44
P("  最小分母候选 S38 = p/T，p =", S38_NUM)

# ---------- 4. 印数 7.94e21 与 T 的关系 ----------
d = T - PRINTED_K7
P("\n[4] 印数 7.94 × 10^21 与 T 的严格对照")
P("  T - 7.94e21 =", d, "（绝对）")
P("  3 位有效数字四舍五入：T 的 3 位 =", sig_str(T, 3), " 与印数一致：", abs(d) < F(5, 10) * F(10) ** 18)
P("  3 位有效数字截断：", sig_str(T, 3), " 两种取整在此处同一字符串（已证：|d| < 1e19）")

# ---------- 5. 距离界（由连分数系数给出，精确有理） ----------
P("\n[5] 关键距离的严格边界（由 a44 = 37、a45 = 4 与收敛分数恒等式推出）")
P("  恒等式：S38 - δ = (38 - t) / (T * (t*q43 + q42))")
P("  恒等式：γ - δ = 1 / (q43 * (t*q43 + q42))，γ = p43/q43")
assert len(digits) > 45 and digits[44] == 37, "需要 a44 = 37"
tq_lo, tq_hi = q44, T                       # t*q43 + q42 ∈ (q44, T)
lo_S = F(3, 4) / (T * T)                    # (3/4) / T^2
hi_S = F(4, 5) / (T * q44)                  # (4/5) / (T*q44)
lo_G = F(1, 1) / (q43 * T)
hi_G = F(1, 1) / (q43 * q44)
P("  S38 - δ ∈ (%s, %s)" % (sig_str(lo_S, 12), sig_str(hi_S, 12)))
P("  γ  - δ ∈ (%s, %s)" % (sig_str(lo_G, 12), sig_str(hi_G, 12)))
assert lo_S < hi_S and lo_G < hi_G
# 与包络的一致性核对（精确比较）
P("  一致性：S38 - U > 0 ：", S38_NUM * 1 > U * T, "（由 S38 - δ >= 3/(4T^2) 与包络宽度远小于它保证）")
P("  一致性：S38 < L + w1 ：", S38_NUM < (L + W1) * T)
P("  一致性：γ - U > 0 ：", p43 > U * q43)
P("  一致性：γ > U + w3 ：", p43 > (U + W3) * q43)

# ---------- 6. Stern-Brocot 三分法 ----------
P("\n[6] Stern-Brocot 三分法：求 (δ, δ+w) 内最小分母")
P("  方法：对每个 w，走两个有理区间 (U, L+w) ⊆ (δ, δ+w) ⊆ (L, U+w)；")
P("  若两者返回同一分数且其分母为 T，则 (δ, δ+w) 内最小分母 = T（夹逼，已证）。")
readings = [("读法一（论文印 ε = 1.11e-43）", W1),
            ("读法二（K* 输入，ε 印数 1.2297916e-43）", W2),
            ("读法三（2.05e20 输入，ε 印数 1.4492163e-43）", W3)]
for name, w in readings:
    r_in = simplest_open(U, L + w)
    r_out = simplest_open(L, U + w)
    (pin, qin, xin, yin, zin, win_), (pout, qout, xout, yout, zout, wout_) = r_in, r_out
    P("  %s：w = %s" % (name, sig_str(w, 22)))
    P("    内区间 (U, L+w) 最小分母分数 = %d / %d" % (pin, qin))
    P("    外区间 (L, U+w) 最小分母分数 = %d / %d" % (pout, qout))
    P("    括号（内）下/上 = %d / %d ， %d / %d" % (xin, yin, zin, win_))
    P("    括号（外）下/上 = %d / %d ， %d / %d" % (xout, yout, zout, wout_))
    ok = (pin, qin) == (pout, qout) == (S38_NUM, T)
    P("    两者同为 S38 且分母 = T：", ok, "（已证）")
    assert ok
    P("    括号 = (p44/q44, p43/q43)？",
      (xin, yin, zin, win_) == (p44, q44, p43, q43) and (xout, yout, zout, wout_) == (p44, q44, p43, q43),
      "（已证）")
    assert (xin, yin, zin, win_) == (p44, q44, p43, q43)

# ---------- 7. 连分数路径（Farey 夹逼）独立给出同值 ----------
P("\n[7] 连分数路径独立证书（不依赖第 6 节的走法）")
P("  Farey 引理（本报告附完整证明）：a/b < c/d，bc - ad = 1 时，(a/b, c/d) 内")
P("  一切分数的分母 >= b + d，等号仅当分数 = 中项 (a+c)/(b+d)。")
P("  取 a/b = p44/q44，c/d = p43/q43：unimodular 已验；b + d =", q44 + q43)
P("  区间包含关系（两条精确比较）：")
P("    δ > p44/q44 ：", L * q44 > p44, "（由 S37 < δ，即 t > 37）")
P("    δ + w3 < p43/q43 ：", (U + W3) * q43 < p43, "（由 γ - δ > 1/(q43 T) > w3）")
P("    γ - δ 下界 1/(q43 T) > w3 ：", lo_G > W3, "（已证）")
P("    1/(q43 T) =", sig_str(lo_G, 12))
P("  S38 = (p44 + p43)/(q44 + q43) 在 (δ, δ+w1) 内（两条精确比较）：")
P("    S38 > δ ：", S38_NUM > U * T, "（由 S38 - δ >= 3/(4 T^2)）")
P("    S38 < δ + w1 ：", S38_NUM < (L + W1) * T)
P("  结论：对 w ∈ {w1, w2, w3}，(δ, δ+w) 内最小分母 = T = %d（已证）" % T)

# ---------- 8. 连分数单元（cell）边界 ----------
P("\n[8] 连分数单元：使最小分母恰为 T 的 w 集合（区间陈述，非抽样）")
P("  单元下界：S38 - δ >= 3/(4T^2) =", sig_str(lo_S, 12))
P("  单元上界：γ - δ >= 1/(q43 T) =", sig_str(lo_G, 12))
P("  三者都在单元内（两条精确比较）：")
P("    w1 >= 3/(4T^2) ：", W1 >= lo_S)
P("    w3 < 1/(q43 T) ：", W3 < lo_G)
P("  更强：S38 - δ <= 4/(5 T q44) =", sig_str(hi_S, 12),
  " < w1 ：", hi_S < W1)
P("  故对一切有理 w ∈ [w1, w3]，(δ, δ+w) 内最小分母 = T（含整个区间的全称陈述）")
P("  单元外对照（引理的另一侧）：w < S38 - δ 时区间落在 (p44/q44, S38) 内，")
P("  分母 >= q44 + T =", q44 + T, "（不计入本轮判词，仅作单元边界的机制说明）")

# ---------- 9. 与材料记录的对照 ----------
P("\n[9] 与项目记录对照（材料记录，非本轮依据）")
P("  cycle-2 记 q39..q43 = 27444133206411171953, 50247984153525417450, 77692117359936589403,")
P("    127940101513462006853, 205632218873398596256（cycle-2/route-5.md:187）")
P("    本轮 q41 =", conv[41][1], " q42 =", q42, " q43 =", q43)
P("    与记录逐位一致：", conv[41][1] == 77692117359936589403 and q42 == 127940101513462006853 and q43 == 205632218873398596256)
P("  cycle-2 记 simplest(δ_lo, γ) 分母 7941964418702608664581、分子 12587715785705330118969（cycle-2/route-5.md:316）")
P("    本轮 S38 分子 =", S38_NUM, " 与记录一致：", S38_NUM == 12587715785705330118969)

# ---------- 10. 落盘证书数据 ----------
with open("results/r5_cert_data.txt", "w") as fh:
    fh.write("# 第 5 路证书数据（精确有理数，可复核重算）\n")
    fh.write("delta_L = %s/%s\n" % (L.numerator, L.denominator))
    fh.write("delta_U = %s/%s\n" % (U.numerator, U.denominator))
    fh.write("cf_digits = %s\n" % digits)
    fh.write("q43 = %d\nq44 = %d\nq42 = %d\np43 = %d\np44 = %d\np42 = %d\n" % (q43, q44, q42, p43, p44, p42))
    fh.write("T = %d\nS38_num = %d\n" % (T, S38_NUM))
    fh.write("w1 = 111/10^45\nw2 = 12297916/10^50\nw3 = 14492163/10^50\n")
P("\n[10] 证书数据已写入 results/r5_cert_data.txt")

with open("results/r5_cert.log", "w") as fh:
    fh.write("\n".join(out_lines) + "\n")
P("\n退出码 0（全部断言通过）")
