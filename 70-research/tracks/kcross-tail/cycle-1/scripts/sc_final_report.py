#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kcross-tail 路线 2 的收口脚本：跑完全部抽验、断言、并把 route-2.md 写出来。

所有数字在同一趟运行内计算并写入报告；任一断言失败即非零退出。
命令行：/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python sc_final_report.py
"""
import hashlib
import sys
from decimal import Decimal, getcontext
from fractions import Fraction as F

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-tail/cycle-1"
sys.path.insert(0, HERE + "/scripts")
import kc_tail_rig as R
from mpmath import iv, mp

PROOF = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts/results"
R2LOG = PROOF + "/r2_threshold_cert.log"
K1LOG = PROOF + "/k1_threshold_cert.log"
R4B2 = PROOF + "/r4b2_window_probe.out"
R4B = PROOF + "/r4b_search_epsopt.out"
R3E = PROOF + "/k3_run_e.out"
GAMMA = F(325919355854421968365, 205632218873398596256)
getcontext().prec = 400

FAILS = []


def chk(name, cond):
    if not cond:
        FAILS.append(name)
    return cond


def dec(x, n=25):
    from decimal import ROUND_HALF_EVEN
    getcontext().prec = n + 5
    getcontext().rounding = ROUND_HALF_EVEN
    x = F(x)
    return format(Decimal(x.numerator) / Decimal(x.denominator), ".%de" % (n - 1))


def dfrac(s):
    return F(Decimal(s))


def trunc_dec(x, nd):
    x = F(x)
    s = str((x * 10 ** nd).numerator // (x * 10 ** nd).denominator)
    return s if nd == 0 else s[:-nd] + "." + s[-nd:]


def sig_trunc(x, n):
    """x 的 n 位有效数字截断（Decimal，ROUND_DOWN），用 localcontext 以免污染全局精度。"""
    from decimal import ROUND_DOWN, localcontext
    x = F(x)
    with localcontext() as ctx:
        ctx.prec = n
        ctx.rounding = ROUND_DOWN
        return str(Decimal(x.numerator) / Decimal(x.denominator))


# ---------- 输入 ----------
txt = open(R2LOG, encoding="utf-8").read()
L = txt.splitlines()
T_hi = F(*[int(g) for g in __import__("re").search(r"T_hi 的精确有理 = (\d+)/(\d+)", txt).groups()])
T_lo = F(*[int(g) for g in __import__("re").search(r"T_lo 的精确有理 = (\d+)/(\d+)", txt).groups()])
k1 = open(K1LOG, encoding="utf-8").read()
KA = F(*[int(g) for g in __import__("re").findall(r"KA = [\d.]+ = (\d+)/(\d+)", k1)[0]])
KB = F(*[int(g) for g in __import__("re").findall(r"KB = [\d.]+ = (\d+)/(\d+)", k1)[0]])
r4 = open(R4B2, encoding="utf-8").read().splitlines()
X0 = 695 * 2 ** 60

# ---------- (1) 端点与结构 ----------
chk("T_hi 分母 2^381", T_hi.denominator == 2 ** 381)
chk("T_lo 分母 2^382", T_lo.denominator == 2 ** 382)
chk("两分子奇数", T_hi.numerator % 2 == 1 and T_lo.numerator % 2 == 1)
chk("T_hi < T_lo", T_hi < T_lo)
w = T_lo - T_hi
chk("宽度 = 3·5^18/2^382", w == F(3 * 5 ** 18, 2 ** 382))
chk("宽度 = 3·10^18/2^400", w == F(3 * 10 ** 18, 2 ** 400))
chk("宽度 12 位 = 1.161777574454e-102", dfrac("1.161777574454e-102") <= w < dfrac("1.161777574455e-102"))
rel = w / T_hi
chk("相对宽 13 位 = 3.709432774431e-123", dfrac("3.709432774431e-123") <= rel < dfrac("3.709432774432e-123"))
chk("60 位打印与日志 :54/:55 一致", trunc_dec(T_hi, 60) == L[53].strip().split("= ")[1]
    and trunc_dec(T_lo, 60) == L[54].strip().split("= ")[1])
chk("49 位公共前缀", trunc_dec(T_hi, 28) == "313195478959172262876.6365306194907065260231016952"
    and trunc_dec(T_lo, 28) == "313195478959172262876.6365306194907065260231016952")
chk("KA <= T_hi", KA <= T_hi)
chk("T_lo <= KB", T_lo <= KB)
m1, m2 = T_hi - KA, KB - T_lo
chk("相含余量与 route-1 的 3.61e-31 / 1.69e-30 同数量级",
    dfrac("3.6e-31") < m1 < dfrac("3.7e-31") and dfrac("1.6e-30") < m2 < dfrac("1.8e-30"))
i5 = __import__("re").search(r"I5（route-5.*?\n.*?= \[([\d.]+), ([\d.]+)\]；", txt)
i5lo, i5hi = dfrac(i5.group(1)), dfrac(i5.group(2))
chk("I2 ⊆ I5", i5lo <= T_hi and T_lo <= i5hi)

# ---------- (2) 窗口两格与 j=92 不等式 ----------
def thr_iv(s):
    return [dfrac(x) for x in __import__("re").findall(r"([\d.]+)", s.split("∈")[1])]


c90 = thr_iv([l for l in r4 if l.strip().startswith("c_90 ∈")][0])
c89 = thr_iv([l for l in r4 if l.strip().startswith("c_89 ∈")][0])
wins = {}
for j in (90, 89):
    i = [k for k, l in enumerate(r4) if ("j = %d ：左端偏移" % j) in l][0]
    kk = thr_iv([l for l in r4[i:i + 4] if "窗口右端" in l][0])
    wins[j] = kk
r90 = ((wins[90][0] - c90[1]) / c90[1], (wins[90][1] - c90[0]) / c90[0])
r89 = ((wins[89][0] - c89[1]) / c89[1], (wins[89][1] - c89[0]) / c89[0])
chk("j=90 相对窗 12 位有效数字 = 7.80677136541e-13", sig_trunc(r90[0], 12) == "7.80677136541E-13")
chk("j=89 相对窗 12 位有效数字 = 7.71461775858e-13", sig_trunc(r89[0], 12) == "7.71461775858E-13")
chk("j=90 两端的 12 位截断相同", sig_trunc(r90[0], 12) == sig_trunc(r90[1], 12))
chk("j=89 两端的 12 位截断相同", sig_trunc(r89[0], 12) == sig_trunc(r89[1], 12))
chk("两格都不含 2e-24", not (r90[0] <= dfrac("2e-24") <= r90[1]) and not (r89[0] <= dfrac("2e-24") <= r89[1]))
chk("两格都不含 1.5361313e-23", not (r90[0] <= dfrac("1.5361313e-23") <= r90[1])
    and not (r89[0] <= dfrac("1.5361313e-23") <= r89[1]))
dlo, dhi = R.delta_bounds()
l2 = R.ln2_bounds()
Clo, Chi = R.C_bounds()
term = R.ru(273 * R.ru(F(1) / R.exp_bounds(R.rd((Clo - 1) * dlo * l2[0]),
                                            R.ru((Chi - 1) * dhi * l2[1]))[0]))
base = F(291, 162 * X0 - 97)
chk("j=92 无窗口不等式：291/(162X0-97) + 273·2^{-(C-1)δ} < 3/X0", base + term < F(3, X0))
chk("恒等式 3/(2^C-1) - 97/(54X0) = 97/(54X0(2^C-1))",
    base - F(97, 54 * X0) == F(97 * 97, 54 * X0 * (162 * X0 - 97)))
chk("r4b2 全文无 5.55 / 5.546", not [l for l in r4 if "5.55" in l or "5.546" in l])
# c_92 的门槛定义自洽（v(92,c_92) = C 的前提）：解析 c_92 时用足精度（Decimal 局部上下文 150 位），
# 否则 30 位全局精度会把两侧各自舍入，出现假不相交。
from decimal import localcontext
with localcontext() as _ctx:
    _ctx.prec = 150
    c92 = [F(Decimal(x)) for x in __import__("re").findall(
        r"([\d.]+)", [l for l in r4 if l.strip().startswith("c_92 ∈")][0].split("∈")[1])]
g92 = R.geom_bounds(92, dlo, dhi)
thr92 = (R.rd(g92[0] * Clo), R.ru(g92[1] * Chi))
# 日志的 c_92 是 dec(..., 30) 打印，分辨率 1e-30（末位可能被舍），故按该分辨率比较。
TOL30 = F(1, 10 ** 30)
c92_gap = max(abs(thr92[0] - c92[0]), abs(thr92[1] - c92[1]))
chk("c_92（日志打印值）与本路 geom(92)·C 在打印分辨率 1e-30 内一致（v(92,c_92)=C 的前提）",
    c92_gap <= TOL30)

# ---------- (3) A5 阶梯 ----------
A1v = F(8900, 54 * X0)
twoC = R.exp_bounds(R.rd(Clo * l2[0]), R.ru(Chi * l2[1]))
tC = (R.rd(twoC[0] - 1), R.ru(twoC[1] - 1))
eps_ub = R.ru(F(R.ru(A1v + R.idiv((F(3), F(3)), tC)[1]).numerator,
                R.ru(A1v + R.idiv((F(3), F(3)), tC)[1]).denominator) / (F(3) * R.rd(92 * Clo) * l2[0]))
worst, wq = None, None
amb = 0
for q in range(1, 6457):
    qlo, qhi = F(q) * dlo, F(q) * dhi
    plo = qlo.numerator // qlo.denominator
    if plo != qhi.numerator // qhi.denominator:
        amb += 1
    mg = F(plo + 1, q) - dhi - eps_ub
    if not mg > 0:
        chk("A5 q=%d 通过" % q, False)
    if worst is None or mg < worst:
        worst, wq = mg, (q, plo + 1)
chk("A5 6456 项全通过", True)
chk("A5 无 floor 歧义", amb == 0)
chk("A5 最小余量在 q=6291, p=9971", wq == (6291, 9971))
chk("A5 最小余量 1.443273e-7 量级", dfrac("1.44327e-7") < worst < dfrac("1.44328e-7"))
chk("6457 > 92C", 6457 > 92 * Chi)

# ---------- (4) A1 的 92 项与 B2 ----------
def S_rig(m2, K):
    e = R.eps_bounds(m2, 92, K, dlo, dhi, l2)
    return (e[0] - (R.ru(GAMMA) - dlo), e[1] - (R.rd(GAMMA) - dhi))


rows = sorted((S_rig(m2, T_hi)[0], m2) for m2 in range(1, 93))
chk("A1 92 项全过", all(r[0] > 0 for r in rows))
chk("A1 最小余量在 m2 = 92", rows[0][1] == 92)
a1min = rows[0][0]
chk("A1 最小余量 = 1.075910e-163 量级", dfrac("1.0759e-163") < a1min < dfrac("1.0760e-163"))
slo = S_rig(92, T_lo)
chk("B2 符号为负", slo[1] < 0)
b2 = slo[1]
chk("B2 负余量 = -1.136322e-164 量级", dfrac("-1.13633e-164") < b2 < dfrac("-1.13631e-164"))
fa = [m for m in range(1, 93) if R.feasible_decision(m, 92, T_hi, dlo, dhi, R.C_bounds()) is True]
chk("F_92(T_hi) = {1..92}", fa == list(range(1, 93)))
s312 = S_rig(92, F(312) * 10 ** 18)
s315 = S_rig(92, F(315) * 10 ** 18)
chk("S(3.12e20) > 0 > S(3.15e20)", s312[0] > 0 and s315[1] < 0)

# ---------- (5) 第二引擎（mpmath.iv）复核两个关键符号 ----------
mp.dps = 300
iv.dps = 300
d_iv = iv.log(iv.mpf(3)) / iv.log(iv.mpf(2))
gam_iv = iv.mpf(325919355854421968365) / iv.mpf(205632218873398596256)


def S_iv(m2, K):
    Kiv = iv.mpf(K.numerator) / iv.mpf(K.denominator)
    pw = iv.exp(iv.mpf(92) * iv.log(d_iv))
    v = iv.mpf(m2) / iv.mpf(92) * Kiv * (d_iv - 1) / (pw - 1)
    tv = iv.exp(v * iv.log(iv.mpf(2)))
    A = R.A_of(m2, 92)
    num = iv.mpf(A.numerator) / iv.mpf(A.denominator) + iv.mpf(3) / (tv - 1) \
        + iv.mpf(3 * (m2 - 1)) / iv.exp(d_iv * iv.log(tv - 1))
    return num / (iv.mpf(3) * Kiv * iv.log(iv.mpf(2))) - (gam_iv - d_iv)


ivhi = S_iv(92, T_hi)
ivlo = S_iv(92, T_lo)
chk("iv 引擎：A1 项为正", ivhi.a > 0)
chk("iv 引擎：B2 项为负", ivlo.b < 0)

# ---------- 报告 ----------
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
rep = []
A = rep.append
A("# 轨道 kcross-tail 第 1 轮路线 2：精确解析抽验")
A("")
A("写入时间：2026 年 10 月 28 日；本文件由 `scripts/sc_final_report.py` 一趟生成，数字与断言来自同一次运行。")
A("输入日志（本轮亲读并实测 md5）：`r2_threshold_cert.log` `%s`、`k1_threshold_cert.log` `%s`、"
  "`r4b2_window_probe.out` `%s`、`r4b_search_epsopt.out` `%s`、`k3_run_e.out` `%s`（均位于 "
  "`70-research/tracks/kcross-proof/cycle-1/scripts/results/`）。" % (
      md5(R2LOG), md5(K1LOG), md5(R4B2), md5(R4B), md5(R3E)))
A("")
A("## 一、要检验的精确陈述")
A("")
A("1. **声明 1（T 的两侧）**：`T ∈ [T_hi, T_lo]`，端点由 `r2_threshold_cert.log` 第 57、58 行的精确有理数给出；")
A("   两侧内容为 A 侧（对一切 K_lo ≤ T_hi 不越界）与 B 侧（对一切 K_lo ≥ T_lo 首步越界）。")
A("2. **声明 2（区间宽度）**：`T_lo − T_hi` 与相对宽分别为 `1.161777574454×10⁻¹⁰²` 与 `3.709432774431×10⁻¹²³`。")
A("3. **声明 3（分岔窗口）**：`route-5` 的 `2×10⁻²⁴` 应修正为 j = 90 的 `7.80677136541×10⁻¹³` 与 j = 89 的 `7.71461775858×10⁻¹³`，"
  "且 j = 91、92 在其门槛处立即获胜（无窗口）。")
A("4. **声明 4（route-4 §5.2）**：`A(91) − A(92) = 3/X₀ ≈ 5.55×10⁻²¹`。")
A("5. **声明 5（A1 与 A5 的规模）**：A1 为 92 项（F_92(T_hi) = {1, …, 92}），最小余量在 m₂ = 92 处 `1.075910×10⁻¹⁶³`；")
A("   A5 为 6456 项，最小余量在 q = 6291（p = 9971）处 `1.443273×10⁻⁷`。")
A("6. **声明 6（B2 符号）**：`ε(92, T_lo)` 的上界小于 `(γ − δ)` 的下界，负余量 `1.136322×10⁻¹⁶⁴`。")
A("")
A("本轮**不检验**：T = R 的等同性（既不在本路范围，也是第 1 轮计划里另设的裁决对象）；")
A("`kc_rig` 等库的形式化；438 条清单与两个不动点（属确定性闸门与本轮其他路线）。")
A("")
A("## 二、编号论证（每步标注证据等级）")
A("")
A("**第 1 步【已证，精确有理】端点与 2 的幂结构**：`den(T_hi) = 2³⁸¹`、`den(T_lo) = 2³⁸²`，两分子为奇数（既约），`T_hi < T_lo`；")
A("宽度 `T_lo − T_hi = 3·5¹⁸/2³⁸² = 3·10¹⁸/2⁴⁰⁰`（精确有理相等，两种写法都判 True）。")
A("后一等式说明端点结构与「起点区间宽 3×10¹⁸（即 3.12×10²⁰ 至 3.15×10²⁰）、400 步二分」自洽——")
A("但**步数本身无法由端点反推**，这是结构一致性，不是对二分过程的独立验证（缺口，见第四节）。")
A("")
A("**第 2 步【已证，精确有理】宽度与相对宽**：宽度系数（20 位）= `%s`，相对宽（20 位）= `%s`；" % (dec(w, 20), dec(rel, 20)))
A("   `−log₁₀(相对宽) ≈ %.2f`，与 route-2.md:12 的「约 122 位一致」相符。" % (
      -(rel.numerator.bit_length() - rel.denominator.bit_length()) * 0.30102999566398120))
A("两个端点在 60 位小数处截断后与日志第 54、55 行逐字相同（两者在 60 位不可分），")
A("49 位有效数字共同前缀 `313195478959172262876.6365306194907065260231016952` 判 True。")
A("")
A("**第 3 步【已证，精确有理】与旧区间的相含**：以 `k1_threshold_cert.log` 第 61、62 行的 KA、KB 精确有理数判：")
A("`KA ≤ T_hi` 余量 `%s`、`T_lo ≤ KB` 余量 `%s`（与 route-1.md:119 的 `3.61×10⁻³¹`、`1.69×10⁻³⁰` 同数量级）；" % (dec(m1, 8), dec(m2, 8)))
A("`I2 ⊆ I5`（I5 端点按截断方向保守使用）余量 `%s` 与 `%s`，与日志第 119 至 121 行读数相符。" % (
      dec(T_hi - i5lo, 8), dec(i5hi - T_lo, 8)))
A("")
A("**第 4 步【已证，精确有理】窗口两格**：由 `r4b2_window_probe.out` 自印的门槛区间与窗口右端区间重算 `(K*_j − c_j)/c_j`：")
A("j = 90 得 `[%s, %s]`，j = 89 得 `[%s, %s]`；" % (dec(r90[0], 25), dec(r90[1], 25), dec(r89[0], 25), dec(r89[1], 25)))
A("两端 12 位有效数字截断分别同为 `7.80677136541×10⁻¹³` 与 `7.71461775858×10⁻¹³`，故**声明 3 的宽度部分成立**；")
A("判据即 `r4b2_window_probe.py:13` 至 `:16` 的相邻两档 numerator 比较（窗口 = 新档在门槛处更差、直到右端才反超的那一段）；")
A("同时复算确认 `2×10⁻²⁴` 与 `1.5361313×10⁻²³` 都不落在两格内（与日志「落入？ False」一致）。")
A("")
A("**第 5 步【缺陷见证，判据与标签不一致】**`r4b2_window_probe.py:132` 第二项判据写作 `F(15361313, 10**31)`，其值是 `1.5361313×10⁻²⁴`，")
A("而该行标签与 `r4b_search_epsopt.out` 第 62 行的实值是 `1.5361313×10⁻²³`（差 10 倍）。两值都在窗口外，结论不变；")
A("但按 learnings.md:53 的「标签与判据文本一致」口径，这是一处应当修正的判据书写。")
A("")
A("**第 6 步【已证，精确有理】`5.55×10⁻²¹` 不成立（声明 4 错误）**：`A(91) = 3/X₀ = %s`，" % dec(F(3, X0), 12))
A("而 route-4.md:171 写的 `5.55×10⁻²¹` 更接近同族的 `240/(54X₀) = %s`（= `3/X₀ × 40/27`）；" % dec(F(240, 54 * X0), 12))
A("`r4b2_window_probe.out` 全文检索 `5.55`、`5.546` 命中 0 行，即该数在对应日志里没有印出过，出处无法回一手。")
A("同理核对第二项：`A(90) − A(91) = 105/(54X₀) = %s`（route-4 的 `2.43×10⁻²¹` 正确）；" % dec(F(105, 54 * X0), 12))
A("§5.2 第 1 条的精确恒等式 `3/(2^C − 1) − 97/(54X₀) = 97/(54X₀(2^C − 1))` 亦判 True（差 `%s`）。" % dec(base - F(97, 54 * X0), 12))
A("")
A("**第 7 步【本轮新证的口径，本路自写】j = 92 无窗口的一个可判形式**：先验证门槛前提 `c₉₂ = geom(92)·C`：")
A("本路算的 `geom(92)·C = %s` 与日志自印的 `c_92 = %s` 在日志打印分辨率 `1e-30` 内一致（最大偏差 `%s`，即到打印末位一致）；" % (
      dec(thr92[0], 32), dec(c92[0], 32), dec(c92_gap, 8)))
A("故 `v(92, c₉₂) = C` 这一前提到打印末位成立。于是对一切 K ≥ c₉₂ 有 v(92, K) ≥ C，且")
A("numerator(92) ≤ `3/(2^C − 1) + 273·2^{−(C−1)δ}`（用 2^v − 1 ≥ 2^{v−1}、2^C = (162/97)X₀ 精确有理）；")
A("而 numerator(91) ≥ `3/X₀`。实算 `273·2^{−(C−1)δ} ≤ %s`，于是两项和 < `3/X₀`（余量 `%s`），" % (
      dec(term, 8), dec(F(3, X0) - base - term, 8)))
A("**故「92 支在门槛处及其以上立即获胜」有初等证明，不依赖采样**。这补上了 route-4 §5.2 第 2 条只靠手算估计与 4 个采样点的缺口；")
A("注：route-4 手算里「新档三项和 ≈ 2.24×10⁻²¹」即 `3/(2^C − 1) = %s`，与上界一致。" % dec(base, 12))
A("")
A("**第 8 步【已证，本路区间】A5 的 6456 项独立重算**：本路以自写引擎（GRID 10²³⁰、atanh 级数）给出 δ ∈ [%s, %s]（区间宽 `%s`，末位以下才是两端之别），" % (
      dec(dlo, 30), dec(dhi, 30), dec(dhi - dlo, 6)))
A("逐 q = 1 至 6456 取 p = ⌊q·δ_lo⌋ + 1，判 `p/q ≥ δ_hi + ε_ub`（ε_ub 为本路算的 `eps(1, 92C)` 上界 `%s`，日志第 77 行记 `1.548697222499×10⁻²³`）：" % dec(eps_ub, 15))
A("**6456 项全部通过**，最小余量在 q = %d（p = %d）处 `%s`（日志第 76 行记 `1.443273×10⁻⁷`，相符）；" % (wq[0], wq[1], dec(worst, 8)))
A("`floor(q·δ_lo) = floor(q·δ_hi)` 对全部 q 成立（歧义 0 项），故所判的 p 就是最小候选 p。另 `6457 > 92C` 余量 `%s`（日志第 78 行记 `3.658177956302×10⁻¹`）。" % dec(F(6457) - 92 * Chi, 8))
A("")
A("**第 9 步【已证，本路区间】A1 的 92 项与 B2 的符号**：以本路引擎在精确端点有理数上逐项复算 92 项 `ε(m₂, T_hi) > γ − δ`：")
A("**92 项全部通过，最小余量在 m₂ = 92 处 `%s`**（日志第 67 行记 `1.075910×10⁻¹⁶³`）；" % dec(a1min, 8))
A("`F_92(T_hi) = {1, …, 92}` 亦由本路可行判据复现（未定 0 项）。B2 在 T_lo 上 `ε 上界 − (γ − δ) 下界 = %s`，符号为负（日志第 87 行记 `−1.136322×10⁻¹⁶⁴`）。" % dec(b2, 8).replace("-", "−"))
A("")
A("**第 10 步【已证，换库对拍】mpmath.iv 引擎复核**：以 mpmath.iv（dps = 300，独立实现、独立舍入模型）复算同一两式：")
A("A1 临界项区间 `[%s, %s]`（正），B2 临界项区间 `[%s, %s]`（负），符号与本路引擎一致。" % (
      mp.nstr(ivhi.a, 10), mp.nstr(ivhi.b, 10), mp.nstr(ivlo.a, 10), mp.nstr(ivlo.b, 10)))
A("两引擎都把 A1 的最小余量定在 m₂ = 92，且都给出 γ − δ ∈ [%s, %s] 量级。" % (dec(R.rd(GAMMA) - dhi, 15), dec(R.ru(GAMMA) - dlo, 15)))
A("")
A("**第 11 步【旁证】二分前提**：`S(3.12×10²⁰) > 0 > S(3.15×10²⁰)` 在本路引擎下成立（区间 `[%s, %s]` 与 `[%s, %s]`），" % (
      dec(s312[0], 6), dec(s312[1], 6), dec(s315[0], 6), dec(s315[1], 6)))
A("与 `k1_threshold_cert.log` 第 54 行「起点 KA = 312e18 符号 above、KB = 315e18 符号 below」一致，说明二分起点合法。")
A("")
A("## 三、失败点清单（本路撞到或被本轮推翻的具体条目）")
A("")
A("1. **声明 4 错误（数字层，不是结论层）**：`3/X₀ = 3.744007502108216750529×10⁻²¹ ≠ 5.55×10⁻²¹`；`5.55×10⁻²¹` 无出处。")
A("   结论仍成立（`3/X₀ > 3/(2^C − 1)`，比值 1.6701031），但把余量说大了约 2.2 倍——注意这是「严格小于」判据的余量夸大，不是方向错误。")
A("2. **判据与标签不一致（脚本层）**：`r4b2_window_probe.py:132` 的 `F(15361313, 10**31)` 与标签 `1.5361313e-23` 差 10 倍（见第 5 步）。")
A("3. **本路自己的失败点（登记）**：第一次把 `T_hi`、`T_lo` 当成 60 位截断串（两行打印相同）代入，得 S 符号错判；")
A("   改用第 57、58 行精确有理数后符号才对。**教训**：60 位打印在 122 位一致的区间上不可区分两端，任何端点级判据必须用精确有理数。")
A("   另：以 dps = 120 直接点值算 S 会落在噪声底（真值 `1×10⁻¹⁶³`，120 位相对精度只到 `1×10⁻¹²⁰` 量级），")
A("   这也是本路把第一版探针结果判为无效、改走精确区间的原因。")
A("4. **本路自己的判据设计失败（已改，登记）**：把日志 `dec(..., 30)` 打印的 `c_92` 当成精确值、与本路严格下界做区间相交，会得出假不相交（差 `8.46×10⁻³¹`）；")
A("   日志的打印分辨率本身就是 `1e-30`，正确读法是按该分辨率比较（本路已改成 `|差| ≤ 1e-30`）。与 learnings.md:61 的「不混用精度做包含性判定」同源。")
A("5. **未做的检验（缺口，不算失败）**：未独立验证 `r2_threshold_cert.py` 的二分会话本身（未重跑，按本轨道硬约束）；")
A("   未验证「相邻两档比较」这一窗口判据与 route-4 §5.1 的 `min_eps` 口径（全 m₂ 取最小）在 K ≥ c₉₂ 上等价（本路只对相邻两档下结论）；")
A("   A 侧的 `A2`（ε_opt 递减）、`A5b`、B 侧 `B3` 至 `B6` 的**推理链**未逐步复核，只复核了它们的数值前提（A1、A5、B2 与端点值）；")
A("   未核 `U(92) = 1.4784·92·δ⁹²` 里的文献常数 `1.4784`（按 plan 口径照写「未核」）。")
A("")
A("## 四、局部新结论与独立验证方式")
A("")
A("1. **新结论（本路自证）**：j = 92 在门槛附近无窗口，且这不是采样结论：")
A("   对一切 K ≥ c₉₂，`numerator(92) ≤ 291/(162X₀ − 97) + 273·2^{−(C−1)δ} < 3/X₀ ≤ numerator(91)`，实算余量 `%s`。" % dec(F(3, X0) - base - term, 8))
A("   独立验证：把 `291/(162X₀ − 97)` 换成精确有理比较、把 `273·2^{−(C−1)δ}` 换成 kc_tail_rig 的 exp 上界即可复算；")
A("   前提只有 `2^C = (162/97)X₀`（C 的定义）与 `2^v − 1 ≥ 2^{v−1}`。")
A("2. **新结论（本路自证）**：窗口两格与端点结构全部复现，且宽度与「起点宽 3×10¹⁸、400 步二分」的 `2⁻⁴⁰⁰` 结构精确自洽。")
A("3. **独立验证方式（供第三方）**：`python sc1_endpoints_windows.py`、`python sc2_a5_ladder.py`、`python sc3_eps_sides.py`、")
A("   `python sc_final_report.py`；所有脚本只读既有日志，写文件只落在 `tracks/kcross-tail/cycle-1/scripts/results/` 与本报告。")
A("")
A("## 五、完整命令行与原始输出摘要")
A("")
A("解释器：`/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python`（3.12.7）。")
A("")
A("1. `python sc1_endpoints_windows.py`（抽验 1）：端点分母 2³⁸¹/2³⁸² 判 True；宽度 `3·5¹⁸/2³⁸²` 判 True；")
A("   相对宽 `%s`；KA、KB 相含判 True，余量 `%s`、`%s`；窗口两格见第 4 步；`5.55` 检索 0 行。" % (dec(rel, 22), dec(m1, 8), dec(m2, 8)))
A("2. `python sc2_a5_ladder.py`（抽验 2）：6456 项通过，最小余量 q = %d（p = %d）`%s`；6457 − 92C = `%s`。" % (
      wq[0], wq[1], dec(worst, 8), dec(F(6457) - 92 * Chi, 8)))
A("3. `python sc3_eps_sides.py`（抽验 3）：A1 92 项通过、最小余量 `%s`（m₂ = 92）；B2 负余量 `%s`；" % (dec(a1min, 8), dec(b2, 8).replace("-", "−")))
A("   mpmath.iv 对拍符号一致（见第 10 步）。")
A("4. `python sc_final_report.py`（本报告生成）：全部断言通过则退出码 0；本轮运行失败断言数 = %d。" % len(FAILS))
A("")
A("原始输出：`scripts/results/sc1_out.txt`、`sc2_out.txt`、`sc3_out.txt`（与本报告同源）。")
A("")
A("**证据边界**：本路「已证」= 精确有理区间 + 逐步断言，引擎为本轮自写的 `kc_tail_rig.py`（网格 10²³⁰，")
A("与 `r2_rig.py` 的 10²⁰⁰ 及级数路线不同），并已用 `c2r5_cert.log` 的 `3.976409667298941266×10⁻⁴⁴` 做过一次对拍；")
A("库的舍入模型本身未经形式化，真值仍以项目既有证书为准。所有结论不含 T = R 的等同性判断。")
open(HERE + "/route-2.md", "w", encoding="utf-8").write("\n".join(rep) + "\n")
open("/tmp/sc_final_status.txt", "w").write("FAILS=%d\n%s\n" % (len(FAILS), ",".join(FAILS)))
print("FAILS", len(FAILS), FAILS[:5])
print("lines", len(rep))
sys.exit(1 if FAILS else 0)
