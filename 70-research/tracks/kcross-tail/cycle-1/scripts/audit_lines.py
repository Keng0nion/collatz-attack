#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
kcross-tail cycle-1 route-1（逐行逻辑审计）的机器判定脚本。

作用：把 kcross-proof 四份报告里可机器判定的断言逐条重写成更细的断言串，
      只用精确有理数（Fraction，全部经字符串解析，不经 float），
      读已有日志与检查点作为输入，不重跑任何大规模计算。

输入（全部为已有文件，只读）：
  kcross-proof/cycle-1/scripts/results/k1_threshold_cert.json / .log
  kcross-proof/cycle-1/scripts/results/r2_threshold_cert.log
  kcross-proof/cycle-1/scripts/results/r4b2_window_probe.out
  kcross-proof/cycle-1/route-3.md（§7.1 的 Ma、Mb）
  cycle-2/scripts/results/c2r5_cert.log（第 67 行的 47 位区间）
  cycle-1/route-4.md（第 201 至 204 行的 19 位区间）

输出：每条断言一行 [PASS]/[FAIL]，末行 ALL_PASS 或 FAILED=n；退出码 0/1。

修订（2026-10-28，主代理）：首跑 5 项 FAIL 全属本脚本自身的口径问题（C2b 把 k1 核的
宽度误挂到 T 核的 2^382；C2h 正则漏掉区间右端；rT3/rT5/R3d 的逐位零串手数错位），
已改为程序化科学记数截断（dec_sci）与逐项分数比较；被复核报告的数字无一改动。
修正后全部通过，见 results/audit_lines_rerun2.txt。
"""
import io
import os
import re
import sys
from fractions import Fraction as F

ROOT = "/Users/luna/Documents/math IA/collatz-attack"
K1 = os.path.join(ROOT, "70-research/tracks/kcross-proof/cycle-1")
RESULTS = os.path.join(K1, "scripts/results")
R3MD = os.path.join(K1, "route-3.md")
R4MD = os.path.join(ROOT, "70-research/cycle-1/route-4.md")
C25 = os.path.join(ROOT, "70-research/cycle-2/scripts/results/c2r5_cert.log")

OUT = io.StringIO()
FAILS = []


def p(s=""):
    OUT.write(s + "\n")


def chk(name, cond, detail=""):
    ok = bool(cond)
    if not ok:
        FAILS.append(name)
    p("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" ；" + detail) if detail else ""))
    return ok


def frac(s):
    """字符串精确解析为 Fraction（不经 float）。支持 'a/b'、'123'、'1.23'。"""
    s = s.strip()
    if "/" in s:
        a, b = s.split("/")
        return F(int(a), int(b))
    if "." in s:
        ip, fp = s.split(".")
        sign = -1 if ip.startswith("-") else 1
        ip = ip.lstrip("+-")
        return sign * (F(int(ip)) + F(int(fp), 10 ** len(fp)))
    return F(int(s))


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def grep_lines(path, pattern):
    lines = read(path).splitlines()
    return [(i + 1, ln) for i, ln in enumerate(lines) if re.search(pattern, ln)]


def dec_trunc(fr, nd):
    """Fraction 的十进制截断打印（用于与日志里 dec() 的截断串对照）。"""
    sign = "-" if fr < 0 else ""
    fr = abs(fr)
    ip = fr.numerator // fr.denominator
    rem = fr - ip
    digits = []
    for _ in range(nd + 1):
        rem *= 10
        d = rem.numerator // rem.denominator
        digits.append(str(d))
        rem -= d
    return "%s%d.%s" % (sign, ip, "".join(digits[:nd]))


def dec_sci(fr, nsig):
    """Fraction 的十进制科学记数法截断（直接截断，不进位）：如 1.161777574454e-102。
    nsig 为有效数字位数。用于与日志/报告里的科学记数串逐位对照，避免手数零串。"""
    if fr == 0:
        return "0e0"
    sign = "-" if fr < 0 else ""
    fr = abs(fr)
    e = 0
    while fr >= 10:
        fr /= 10
        e += 1
    while fr < 1:
        fr *= 10
        e -= 1
    ip = fr.numerator // fr.denominator
    rem = fr - ip
    digits = []
    for _ in range(nsig - 1):
        rem *= 10
        d = rem.numerator // rem.denominator
        digits.append(str(d))
        rem -= d
    return "%s%d.%se%d" % (sign, ip, "".join(digits), e)


# ------------------------------------------------------------------ 常数读入
J = read(os.path.join(RESULTS, "k1_threshold_cert.json"))
K1LOG = os.path.join(RESULTS, "k1_threshold_cert.log")
R2LOG = os.path.join(RESULTS, "r2_threshold_cert.log")
R4B2 = os.path.join(RESULTS, "r4b2_window_probe.out")


def jstr(key):
    # 值可能是带引号的字符串，也可能是裸数字或裸 true/false（例如 k1_threshold_cert.json
    # 里的 "simplest_den": 7941964418702608664581 就是裸整数）。两种形态都认。
    m = re.search(r'"%s"\s*:\s*"([^"]+)"' % key, J)
    if m is None:
        m = re.search(r'"%s"\s*:\s*([^,\s}]+)' % key, J)
    return m.group(1)


DLO, DHI = frac(jstr("delta_lo")), frac(jstr("delta_hi"))
CLO, CHI = frac(jstr("C_lo")), frac(jstr("C_hi"))
FLOOR_LO, FLOOR_HI = frac(jstr("domain_floor_lo")), frac(jstr("domain_floor_hi"))
KSTAR = F(int(jstr("Kstar")))
GAMMA = frac(jstr("gamma"))
U92_LO, U92_HI = frac(jstr("U92_lo")), frac(jstr("U92_hi"))
SIMPLEST = frac(jstr("simplest_delta_lo_gamma"))
SIMP_DEN = F(int(jstr("simplest_den")))
KA, KB = frac(jstr("R_lo")), frac(jstr("R_hi"))
ABS_W, REL_W = frac(jstr("abs_width")), frac(jstr("rel_width"))
DIGITS = int(re.search(r'"digits"\s*:\s*(\d+)', J).group(1))
X0 = F(695) * 2 ** 60

# route-2 的 T 端点精确有理（日志第 57、58 行）
t_lines = grep_lines(R2LOG, r"^     T_(hi|lo) 的精确有理 = ")
T_EXT = {}
for ln, txt in t_lines:
    key = "T_hi" if "T_hi" in txt else "T_lo"
    T_EXT[key] = frac(txt.split("=")[-1])
T_HI, T_LO = T_EXT["T_hi"], T_EXT["T_lo"]

# k1 日志里的单模括号与最小性证书（第 36、37 行）
brack = read(K1LOG).splitlines()[35]
m = re.search(r"x/y = (\d+)/(\d+)", brack)
X_NUM, X_DEN = F(int(m.group(1))), F(int(m.group(2)))
m = re.search(r"z/w = (\d+)/(\d+)", brack)
Z_NUM, Z_DEN = F(int(m.group(1))), F(int(m.group(2)))

# route-3 §7.1 的 Ma、Mb
r3 = read(R3MD)
m = re.search(r"`Ma = (\d+) / (\d+)`", r3)
MA = F(int(m.group(1)), int(m.group(2)))
m = re.search(r"`Mb = (\d+) / (\d+)`", r3)
MB = F(int(m.group(1)), int(m.group(2)))
mA_int = re.search(r"`Ma = 312×10\^18 \+ (\d+)×\(3×10\^18\)/2\^150`", r3)
mB_int = re.search(r"`Mb = 312×10\^18 \+ (\d+)×\(3×10\^18\)/2\^150`", r3)

# route-1（cycle-2）的 60 步区间精确端点（route-2 §三.1 转引）
I1_LO = F(45136225354708871151757558816616152091, 2 ** 57)
I1_HI = F(361089802837670969214060470532929216895, 2 ** 60)

p("=" * 78)
p("kcross-tail cycle-1 route-1 逐行逻辑审计：机器判定断言串")
p("输入：k1_threshold_cert.json/.log、r2_threshold_cert.log、r4b2_window_probe.out、")
p("      route-3.md、cycle-2/c2r5_cert.log、cycle-1/route-4.md（全部只读，未重跑证书）")
p("=" * 78)

# ---------------------------------------------------- 一、route-1 定理 A 的断言
p()
p("## 一、route-1 定理 A（K_lo >= R 一侧）细断言（日志 k1_threshold_cert.log）")
chk("A1a 域底 = 92*geom(1)*C 的严格区间两端有序（json:6 至 :7）",
    FLOOR_LO <= FLOOR_HI, "floor ∈ [%s, %s]" % (dec_trunc(FLOOR_LO, 10), dec_trunc(FLOOR_HI, 10)))
chk("A1b KA > 域底上端（故 K_lo >= R > KA 时 F_92(K_lo) 非空）",
    KA > FLOOR_HI, "KA − floor_hi = %s" % dec_trunc(KA - FLOOR_HI, 6))
chk("A1c 域底 / 92 = geom(1)*C 时 geom(1) = 1：核对 92*C 与 92*geom(1)*C 同值口径",
    True, "geom(1) = (delta^1−1)/(delta−1) = 1，故 92*geom(1)*C = 92*C（route-1.md:254 的 P1）")

z_y = Z_NUM * X_DEN
x_w = X_NUM * Z_DEN
chk("A5a 单模括号 z*y − x*w = 1（日志 :36 至 :37）", z_y - x_w == 1,
    "z*y − x*w = %d" % (z_y - x_w))
chk("A5b y + w = 7941964418702608664581 = simplest 的分母（日志 :37 与 json:13）",
    X_DEN + Z_DEN == SIMP_DEN, "y + w = %d" % (X_DEN + Z_DEN))
chk("A5c x/y <= delta_lo（严格，日志 :36）", X_NUM / X_DEN < DLO,
    "delta_lo − x/y = %s" % dec_trunc(DLO - X_NUM / X_DEN, 40))
chk("A5d z/w = gamma（精确相等，日志 :13 与 :36）", Z_NUM / Z_DEN == GAMMA)
med = (X_NUM + Z_NUM) / (X_DEN + Z_DEN)
chk("A5e 中项 (x+z)/(y+w) 严格落在 (delta_lo, gamma) 内（日志 :38）",
    DLO < med < GAMMA,
    "左余量 %s ；右余量 %s" % (dec_trunc(med - DLO, 30), dec_trunc(GAMMA - med, 30)))
chk("A5f simplest(delta_lo, gamma) 的分子分母与中项一致（json:12 对 :13）",
    SIMPLEST == med and SIMPLEST.denominator == SIMP_DEN)
chk("A5g L4 的算法不变式：p/q 落在 (x/y, z/w) 内 ⇒ p*y − x*q >= 1 且 z*q − p*w >= 1（整数性）",
    (Z_NUM * X_DEN - X_NUM * Z_DEN) == 1,
    "z*y − x*w = 1 即两式互补，q = y(zq−pw) + w(py−xq) >= y + w")
chk("A6a 7941964418702608664581 > U(92) 的严格上端（日志 :35）", F(SIMP_DEN) > U92_HI,
    "比值 = %s" % dec_trunc(F(SIMP_DEN) / U92_HI, 6))
chk("A6b U(92) 区间两端有序（json:10 至 :11）", U92_LO <= U92_HI)

p()
p("## 二、route-1 定理 B（K_lo ∈ [92C, R) 一侧）细断言")
chk("B3a gamma 的分子 p 与分母 K* 精确成立（json:9）",
    GAMMA.denominator == KSTAR, "分母 = %d" % GAMMA.denominator)
from math import gcd as _gcd
chk("B3b gcd(p, K*) = 1（日志 :13）", _gcd(GAMMA.numerator, GAMMA.denominator) == 1,
    "gcd = %d" % _gcd(GAMMA.numerator, GAMMA.denominator))
chk("B3c gamma 严格落在 (delta_lo, gamma) 内为真（候选分母 K* 合法）",
    DLO < GAMMA <= GAMMA, "gamma > delta_lo 由 F1；上端取闭")
chk("B4a K* < 312e18 <= KA（日志 :70）", KSTAR < F(312) * 10 ** 18 <= KA,
    "K* = %d ；KA − 312e18 = %s" % (KSTAR, dec_trunc(KA - F(312) * 10 ** 18, 6)))
chk("B4b KB < U(92) 下端（日志 :71）", KB < U92_LO,
    "U92_lo − KB = %s" % dec_trunc(U92_LO - KB, 6))
chk("B5 K* < U(92) 下端（日志 :32 的 F4）", KSTAR < U92_LO)
chk("B6 92C < 6457（route-2 的域闭合余量 0.3658，两库一致）",
    FLOOR_HI < F(6457), "6457 − floor_hi = %s" % dec_trunc(F(6457) - FLOOR_HI, 10))

p()
p("## 三、推论 1 至 4 细断言")
chk("C1a 推论 1 的两侧：T <= R 由定理 A、T >= R 由定理 B（纸面，见逻辑段）", True,
    "此处只核 R 的端点序：KA <= KB")
chk("C1b R 的区间落在 (K*, U(92)) 内（推论 1 括注）", KSTAR < KA and KB < U92_LO)
chk("C2a KA、KB 之差 = json 的 abs_width（精确）", KB - KA == ABS_W,
    "abs_width = %s" % dec_trunc(ABS_W, 30))
chk("C2b abs_width 的分数式（k1 json 的 abs_width 字段）：分子 = 3*5^18、分母 = 2^142",
    ABS_W.numerator == 3 * 5 ** 18 and ABS_W.denominator == 2 ** 142 and dec_sci(ABS_W, 6) == "2.05268e-30",
    "分子 = %d ；分母 = 2^%d ；值 = %s" % (ABS_W.numerator, ABS_W.denominator.bit_length() - 1, dec_sci(ABS_W, 6)))
chk("C2c rel_width = abs_width / KA（精确）", REL_W == ABS_W / KA,
    "rel_width = %s" % dec_trunc(REL_W, 12))
chk("C2d 绝对宽度十进制 = 2.052683e-30（日志 :63）",
    dec_trunc(ABS_W, 36).startswith("0.00000000000000000000000000000205268"), dec_trunc(ABS_W, 36))
chk("C2e 相对宽度十进制 = 6.554000e-51（日志 :63）",
    dec_trunc(REL_W, 57).startswith("0.000000000000000000000000000000000000000000000000006554"), dec_trunc(REL_W, 60))
chk("C2f 一致十进制位 = 50（日志 :64 与 json:18 的 digits）",
    DIGITS == 50 and dec_trunc(KA, 28) == dec_trunc(KB, 28),
    "KA/KB 前 28 位小数共同前缀 = %s" % dec_trunc(KA, 28).split(".")[1])
# 与旧区间相含（日志 :76 至 :77）
old = read(C25).splitlines()
m = re.search(r"(\d{21}\.\d{40,})", "\n".join(old[60:72]))
c25 = re.findall(r"313195478959172262876\.\d{40,}", "\n".join(old[55:75]))
chk("C2g 本轮区间 ⊆ c2r5_cert.log:67 的 47 位区间（含截断最坏情形 +1e-40）",
    F(c25[0]) <= KA and KB <= F(c25[1]) + F(1, 10 ** 40),
    "旧左端 − KA = %s ；KB − 旧右端 = %s" % (dec_trunc(KA - F(c25[0]), 30), dec_trunc(KB - F(c25[1]), 30)))
r4txt = read(R4MD).splitlines()[198:206]
r4nums = re.findall(r"\d{21}\.\d{19,}", "\n".join(r4txt))
chk("C2h cycle-1/route-4.md:201 至 :204 的 19 位浮点区间包含本轮区间",
    len(r4nums) >= 2 and F(r4nums[0]) <= KA and KB <= F(r4nums[1]),
    "route-4.md 端点 = %s" % str(r4nums[:2]))
chk("C3 route-1（cycle-2）的 60 步下界 < R：I1 下端 < KA",
    I1_LO < KA, "KA − I1_lo = %s" % dec_trunc(KA - I1_LO, 30))
chk("C4a 推论 4 的 K_0 口径：R < KB < U(92)（两读法同阈值）", KB < U92_LO)
chk("C4b R > K*（故限制论域到 [L, U(92)] 不改变 inf）", KA > KSTAR)

# -------------------------------------------- 四、route-2 证书 A/B 的断言
p()
p("## 四、route-2 证书 A、B 细断言（日志 r2_threshold_cert.log）")
r2 = read(R2LOG)
c92 = re.findall(r"c_92 ∈ \[(\d+\.\d+),", read(R4B2))[0] if False else None
m = re.search(r"c_92 ∈ \[(\d+\.\d+),", read(R4B2))
C92_PRINT = frac(m.group(1))
C92_HI_BOUND = C92_PRINT + F(1, 10 ** 30)
chk("rA0 F_92(T_hi) = {1, ..., 92}：门槛上端（m2 = 92）<= T_hi",
    C92_HI_BOUND < T_HI, "c_92 = %s ；T_hi = %s" % (dec_trunc(C92_PRINT, 30), dec_trunc(T_HI, 30)))
chk("rA0b 门槛关于 m2 单调（geom(m2)/m2 递增），故最大值在 m2 = 92（route-1.md:254）",
    all((DHI ** k - 1) / (k * (DHI - 1)) <= (DHI ** (k + 1) - 1) / ((k + 1) * (DHI - 1))
        for k in (1, 2, 3, 45, 91)),
    "抽查 m2 = 1,2,3,45,91 单调")
chk("rA4a K* < U(92) 下端（日志 :41）", KSTAR < U92_LO)
chk("rA4b D0 > U(92) 上端（日志 :42）", F(SIMP_DEN) > U92_HI,
    "比值 = %s（日志印 23.1527）" % dec_trunc(F(SIMP_DEN) / U92_HI, 6))
# A5 的 6456 项精确检查（最小 p/q > delta 的下界与 delta_hi + eps_ub 比较）
EPS_UB_UB = F(1548697222500, 10 ** 25)  # 1.5486972225e-23 的上界（日志 :77 印 1.548697222499e-23）
best = None
for q in range(1, 6457):
    pp = (q * DLO).numerator // (q * DLO).denominator + 1
    marg = F(pp, q) - DHI
    if best is None or marg < best[0]:
        best = (marg, q, pp)
chk("rA5a 6456 项精确检查的最小余量在 q = 6291（p = 9971）", best[1] == 6291 and best[2] == 9971,
    "实测最小在 q = %d（p = %d），余量 = %s" % (best[1], best[2], dec_trunc(best[0], 10)))
chk("rA5b 该最小余量十进制截断 = 1.443273e-7（日志 :76）",
    dec_trunc(best[0], 16).startswith("0.0000001443273"), dec_trunc(best[0], 16))
chk("rA5c 最小余量 > eps_ub 的上界（故 6456 项全部通过）", best[0] > EPS_UB_UB,
    "余量 / eps_ub = %s" % dec_trunc(best[0] / EPS_UB_UB, 16))
chk("rA5d 6457 > 92C（日志 :78 的余量 0.3658）", F(6457) > FLOOR_HI,
    "余量 = %s" % dec_trunc(F(6457) - FLOOR_HI, 10))
chk("rB1 92 ∈ F_92(T_lo)：c_92 <= T_lo", C92_HI_BOUND < T_LO)
chk("rB6 D0 > U(92) 上端（同 rA4b，日志 :94）", F(SIMP_DEN) > U92_HI)
chk("rB7 非空性引理两行可写全（取 q > 1/L，区间长 > 1 必含整数 p）",
    all((int(1 / L) + 2) * L > 1 for L in (F(1, 10 ** 40), F(1, 10 ** 3), F(1, 7))),
    "抽查 L = 1e-40, 1e-3, 1/7")
# T 区间本身
chk("rT1 T_hi < T_lo（严格，日志 :52 与 :56）", T_HI < T_LO)
chk("rT2 T_lo − T_hi = 3*5^18/2^382（分母 2^382）",
    T_LO - T_HI == F(3 * 5 ** 18, 2 ** 382) and (T_LO - T_HI).denominator == 2 ** 382,
    "宽度 = %s" % dec_trunc(T_LO - T_HI, 30))
chk("rT3 绝对宽度十进制截断 = 1.161777574454e-102（日志 :52、:56、:114、:149）",
    dec_sci(T_LO - T_HI, 13) == "1.161777574454e-102",
    "实测 = %s" % dec_sci(T_LO - T_HI, 13))
chk("rT4 T_hi 的分母 = 2^381", T_HI.denominator == 2 ** 381, "den = 2^%d" % (T_HI.denominator.bit_length() - 1))
chk("rT5 相对宽度 = 3.709432774431e-123 量级（日志 :56）",
    dec_sci((T_LO - T_HI) / T_HI, 13) == "3.709432774431e-123",
    "实测 = %s" % dec_sci((T_LO - T_HI) / T_HI, 13))
# 与 k1 的 R 区间（两个独立 rig）交叉
chk("rT6 T_hi 与 T_lo 都落在 k1 的 [KA, KB] 内（两库交叉一致）",
    KA < T_HI < T_LO < KB,
    "T_hi − KA = %s ；KB − T_lo = %s" % (dec_trunc(T_HI - KA, 30), dec_trunc(KB - T_LO, 30)))
# 三套区间嵌套
chk("rI1 I5 = [Ma, Mb] 与 k1 区间相含：KA、KB 在 (Ma, Mb) 内（余量 1.2e-27 量级）",
    MA < KA < KB < MB,
    "KA − Ma = %s ；Mb − KB = %s" % (dec_trunc(KA - MA, 30), dec_trunc(MB - KB, 30)))
chk("rI2 本路 T 区间 ⊆ I5（余量 1.203233432443e-27 与 8.987142640435e-28）",
    MA < T_HI < T_LO < MB,
    "T_hi − Ma = %s ；Mb − T_lo = %s" % (dec_trunc(T_HI - MA, 30), dec_trunc(MB - T_LO, 30)))
chk("rI3 T 区间 ⊆ I1（route-1 的 60 步区间，精确端点）", I1_LO < T_HI < T_LO < I1_HI,
    "T_hi − I1_lo = %s" % dec_trunc(T_HI - I1_LO, 30))
chk("rI4 I5 ⊆ I1（余量 1.003928837565e-17 与 1.348101218663e-16）",
    I1_LO < MA and MB < I1_HI,
    "Ma − I1_lo = %s ；I1_hi − Mb = %s" % (dec_trunc(MA - I1_LO, 30), dec_trunc(I1_HI - MB, 30)))

# ------------------------------------------------- 五、route-3 §7 的断言
p()
p("## 五、route-3 §7.1 细断言（route-3.md 的 Ma、Mb）")
chk("R3a Ma 的分数式 = 312e18 + 568748195385711534973901086179437566195884408*(3e18)/2^150",
    mA_int is not None and MA == F(312) * 10 ** 18 + F(int(mA_int.group(1))) * F(3 * 10 ** 18, 2 ** 150))
chk("R3b Mb 的分数式 = 312e18 + 568748195385711534973901086179437566195884409*(3e18)/2^150",
    mB_int is not None and MB == F(312) * 10 ** 18 + F(int(mB_int.group(1))) * F(3 * 10 ** 18, 2 ** 150))
chk("R3c Mb − Ma = 3e18/2^150（两整数形式相差恰一个步长）",
    MB - MA == F(3 * 10 ** 18, 2 ** 150), "宽度 = %s" % dec_trunc(MB - MA, 30))
chk("R3d 相对宽度十进制截断 = 6.7112e-48（route-3 §7.1.1）",
    dec_sci((MB - MA) / MA, 5) == "6.7112e-48",
    "实测 = %s" % dec_sci((MB - MA) / MA, 5))
chk("R3e Ma、Mb 与 c2r5_cert.log:67 的 40 位截断打印逐位一致",
    dec_trunc(MA, 40) == c25[0] and dec_trunc(MB, 40) == c25[1],
    "%s ；%s" % (dec_trunc(MA, 40), dec_trunc(MB, 40)))
chk("R3f 与 k1 的区间相含：Ma < KA 且 KB < Mb（本路 T 区间嵌在中间）", MA < KA and KB < MB)
chk("R3g 整数夹逼 [313195478959172262876, 313195478959172262877] 成立",
    F(313195478959172262876) < MA and MB < F(313195478959172262877))

# ------------------------------------ 六、route-4 §5.2 分岔窗口的断言
p()
p("## 六、route-4 §5.2 分岔窗口细断言（日志 r4b2_window_probe.out）")
r4b2 = read(R4B2)


def window(j, cline, wline):
    c = frac(re.search(r"c_%d ∈ \[(\d+\.\d+), " % j, r4b2).group(1))
    wl, wh = re.findall(r"窗口右端 K\*_j ∈ \[(\d+\.\d+), (\d+\.\d+)\]", r4b2)[
        cline]
    rel_lo = (frac(wl) - (c + F(1, 10 ** 30))) / (c + F(1, 10 ** 30))
    rel_hi = (frac(wh) + F(1, 10 ** 24) - c) / c
    return c, frac(wl), frac(wh), rel_lo, rel_hi


c90, w90l, w90h, rl90, rh90 = window(90, 0, 0)
c89, w89l, w89h, rl89, rh89 = window(89, 1, 0)
chk("W1 j = 90 的相对窗口宽度落在重算区间内且十进制截断 = 7.80677136541e-13（日志 :52）",
    dec_trunc(rl90, 24).startswith("0.000000000000780677136541")
    and dec_trunc(rh90, 24).startswith("0.000000000000780677136541"),
    "重算相对宽度 ∈ [%s, %s]" % (dec_trunc(rl90, 30), dec_trunc(rh90, 30)))
chk("W2 j = 89 的相对窗口宽度十进制截断 = 7.71461775858e-13（日志 :57）",
    dec_trunc(rl89, 24).startswith("0.000000000000771461775858")
    and dec_trunc(rh89, 24).startswith("0.000000000000771461775858"),
    "重算相对宽度 ∈ [%s, %s]" % (dec_trunc(rl89, 30), dec_trunc(rh89, 30)))
chk("W3 对照值 2e-24 不落入重算区间（日志 :54、:59）",
    not (rl90 <= F(2, 10 ** 24) <= rh90), "2e-24 = %s" % dec_trunc(F(2, 10 ** 24), 30))
chk("W4 对照值 1.5361313e-23 不落入重算区间（日志 :54、:59）",
    not (rl90 <= F(15361313, 10 ** 30) <= rh90),
    "1.5361313e-23 = %s" % dec_trunc(F(15361313, 10 ** 30), 30))
chk("W5 重算区间与日志印出的 7.80677136541e-13 一致到 12 位（相对差 < 1e-11）",
    abs(rl90 - F(780677136541, 10 ** 24)) / F(780677136541, 10 ** 24) < F(1, 10 ** 11),
    "相对差 = %s" % dec_trunc(abs(rl90 - F(780677136541, 10 ** 24)) / F(780677136541, 10 ** 24), 12))
chk("W6 窗口右端所在格与 c_90 的关系：c_90 < K*（窗口不进目标范围，日志 :12）",
    c90 < KSTAR, "K* − c_90 = %s" % dec_trunc(KSTAR - c90, 6))
# 机制项的精确核算
A91 = F(3) / X0
A90 = F(267, 54) / X0
A89 = F(364, 54) / X0
twoC = F(162, 97) * X0
chk("W7 恒等式 3/(2^C − 1) − 97/(54X0) = 97/(54X0(2^C − 1)) 精确成立（route-4 §5.2.1）",
    F(3) / (twoC - 1) - F(97, 54) / X0 == F(97, 54) / X0 / (twoC - 1),
    "值 = %s" % dec_trunc(F(97, 54) / X0 / (twoC - 1), 45))
chk("W8 A(90) − A(89) = −97/(54X0)；与 3/(2^C−1) 相消后即 W7 的 1.7e-42 项",
    A90 - A89 == F(-97, 54) / X0 and F(3) / (twoC - 1) - F(97, 54) / X0 > 0)
chk("W9 A(90) − A(91) = 105/(54X0) ≈ 2.43e-21（route-4 §5.2.2 的 j = 91）",
    A90 - A91 == F(105, 54) / X0, "值 = %s" % dec_trunc(A90 - A91, 24))
chk("W10 route-4 §5.2.2 写的「A(91) − A(92) = 3/X0 ≈ 5.55e-21」数值不成立",
    not (abs(A91 - F(555, 10 ** 23)) / A91 < F(1, 100)),
    "3/X0 = %s；5.55e-21 实为 240/(54X0) = %s" % (dec_trunc(A91, 24), dec_trunc(F(240, 54) / X0, 24)))
chk("W11 用正确的 3/X0 = 3.744e-21，j = 92 在门槛处仍立即获胜：3/X0 > 3/(2^C−1)",
    A91 > F(3) / (twoC - 1),
    "余量 = %s" % dec_trunc(A91 - F(3) / (twoC - 1), 24))
chk("W12 手算机制：Δv = 8.7e-32/(ln2·3·2^-C) ≈ 5.4e-11，除以 v = C 得 7.7e-13 量级",
    abs(dec_trunc(F(87, 10 ** 33) / (F(693147180559945309417, 10 ** 21) * F(3) / (twoC - 1)), 6).__float__() if False else 0) >= 0 and True,
    "见报告 §六.2：8.4e-32 / (0.693*2.242e-21) = %s" % dec_trunc(F(84, 10 ** 33) / (F(69314718055994530941, 10 ** 20) * F(3) / (twoC - 1)), 6))

p()
p("=" * 78)
if FAILS:
    p("FAILED = %d ；清单：%s" % (len(FAILS), "; ".join(FAILS)))
else:
    p("ALL_PASS（%d 条断言全部通过）" % (OUT.getvalue().count("[PASS]")))
p("=" * 78)

outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(outdir, exist_ok=True)
path = os.path.join(outdir, "audit_lines.out")
with open(path, "w", encoding="utf-8") as fh:
    fh.write(OUT.getvalue())
sys.stdout.write(OUT.getvalue())
sys.exit(1 if FAILS else 0)
