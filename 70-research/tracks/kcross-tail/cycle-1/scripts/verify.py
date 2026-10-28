#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""轨道 kcross-tail 第 1 轮 路线 4：确定性闸门 verify.py。

复算 kcross-proof cycle-1 四份报告里「可机器判定」的断言，全部通过则退出码 0。

四组断言（对应本轮 ask）：
  [1] T 的区间端点：读 r2_threshold_cert.log:57 至 :58 的精确有理数；判 T_hi < T_lo、
      宽度与打印口径一致、分母为 2 的幂、两端点 eps(92,·) − (γ−δ) 的符号为正与负
      （r2_rig 单点重算）、[T_hi, T_lo] ⊆ [KA, KB]（KA、KB 读 k1_threshold_cert.log:61 至 :62）。
  [2] ε 梯子：k3_rig.eps_bounds 复算 K* 格 m2 = 83 至 91 的 9 个值，与 k3_run_a.out 第 [1] 节
      的打印串（23 位有效数字）逐字比对，并另报前 20 位一致数。
  [3] 438 条清单：k3_rig.semiconv_list_frontier 带 cap_q = K* 复算 438／内 0／外 438／未定 0；
      再复算完整清单 442 与差集 4（并核被 cap 掉的 4 条分母 ≥ K*）。
  [4] 不动点：在 K* 与 q41 = 77692117359936589403 两格用 r4_common.psi_two_sided 复算 Ψ，
      验证两端夹逼都等于自身。
附加（[5] 跨库对拍、[6] 分岔窗口抽验）不属四组本体，单列。

纪律：
  * 只读。不写任何仓库文件、不重跑任何会写文件的旧脚本、不重跑大规模计算
    （T 的 400 步二分、窗口的 50 步二分都只读已有日志的端点）。
  * 一切有理数以字符串精确解析，不经 float 中转；一切比较用 Fraction。
  * 每条判据都写成能取 False 的形式；任何一条不通过即置退出码 1。
  * 同库复算不是独立证明；本脚本只报「复算值与原日志是否一致」与「两库区间是否相交」。

用法：20-experiments/.venv/bin/python verify.py
"""
import hashlib
import re
import sys
import time
from fractions import Fraction as F
from math import gcd

KP = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
RES = KP + "/results"
if KP not in sys.path:
    sys.path.insert(0, KP)

M = 92
KSTAR = 205632218873398596256
Q41 = 77692117359936589403
D0 = 7941964418702608664581
Q44 = 7736332199829210068325
GAMMA = F(325919355854421968365, 205632218873398596256)

FAILS, NCHK = [], [0]


def chk(cid, ok, text):
    NCHK[0] += 1
    ok = bool(ok)
    if not ok:
        FAILS.append(cid)
    print("  [%s] %-7s %s" % ("PASS" if ok else "FAIL", cid, text))
    return ok


def note(text):
    print("           " + text)


def slurp(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read().splitlines()


def md5(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def frac_in(line):
    """取该行最后一个 a/b 型有理数（字符串精确解析，不经 float）。"""
    hit = re.findall(r"(\d+/\d+)", line)
    assert hit, "该行无 a/b 型有理数：%s" % line
    return F(hit[-1])


def bracket_in(line):
    """取该行形如 [x, y] 的区间（返回两个字符串）。"""
    hit = re.findall(r"\[([^\[\]]+)\]", line)
    assert hit, "该行无区间：%s" % line
    a, b = hit[0].split(",")
    return a.strip(), b.strip()


def dec_str(x, nd):
    """精确十进制截断（与 k3_rig.dec 同型，便于与日志打印逐字对拍）。"""
    x = F(x)
    sign = "-" if x < 0 else ""
    x = abs(x)
    ip = x.numerator // x.denominator
    rem = x.numerator - ip * x.denominator
    out = [sign + str(ip), "."]
    for _ in range(nd):
        rem *= 10
        d = rem // x.denominator
        out.append(str(d))
        rem -= d * x.denominator
    return "".join(out)


def sci(x, nd=12):
    """精确科学计数法（截断 nd 位小数），与 k3_rig.sci 同型。"""
    x = F(x)
    if x == 0:
        return "0"
    sign = "-" if x < 0 else ""
    ax = abs(x)
    e = 0
    while ax >= 10:
        ax /= 10
        e += 1
    while ax < 1:
        ax *= 10
        e -= 1
    return "%s%se%s%d" % (sign, dec_str(ax, nd), "+" if e >= 0 else "-", abs(e))


def sig20(s):
    """打印串的前 20 位有效数字（去小数点与指数、去空格）。"""
    t = s.strip().replace(" ", "").split("e")[0].replace(".", "").lstrip("+-")
    return t[:20]


def find_line(lines, needle):
    for i, s in enumerate(lines):
        if needle in s:
            return i, s
    raise AssertionError("日志里找不到：%s" % needle)


T0 = time.time()
print("=" * 78)
print("kcross-tail cycle-1 路线 4：确定性闸门 verify.py（只读复算；退出码 0 = 全部通过）")
print("=" * 78)

LOG_T = RES + "/r2_threshold_cert.log"
LOG_K1 = RES + "/k1_threshold_cert.log"
LOG_A = RES + "/k3_run_a.out"
LOG_E = RES + "/k3_run_e.out"
LOG_B2 = RES + "/r4b2_window_probe.out"

print("\n[0] 输入日志的 md5 与 kcross-tail/cycle-1/materials.md 记录比对")
print("     （记录出处：该文件行 138、163、189、193、216 的表格）")
EXPECT = [(LOG_T, "c45b3da1f6910ba07c41a27682391904"),
          (LOG_K1, "23fec892a94f72cb135562b584fe6ec2"),
          (LOG_A, "01f48fc0ebd6121c2b372861be96fb6e"),
          (LOG_E, "f8b900d497b776778107070a15799443"),
          (LOG_B2, "a078e3e631f07858f4b607968403a3c2")]
for p, exp in EXPECT:
    got = md5(p)
    chk("0.md5", got == exp, "%s：%s" % (p.split("/")[-1], got))

# ------------------------------------------------------------------ 组 1
print("\n[1] 组 1：T 的区间端点（输入 = r2_threshold_cert.log:57 至 :58 的精确有理数）")
LT = slurp(LOG_T)
l57, l58 = LT[56], LT[57]
chk("1.0", ("T_hi 的精确有理" in l57) and ("T_lo 的精确有理" in l58),
    "行 57、58 确为 T_hi、T_lo 的精确有理数行")
T_hi, T_lo = frac_in(l57), frac_in(l58)
note("T_hi = %s" % dec_str(T_hi, 30))
note("T_lo = %s" % dec_str(T_lo, 30))
chk("1.1", T_hi < T_lo, "T_hi < T_lo（精确有理比较）")
chk("1.2a", T_hi.denominator == 2 ** 381, "分母(T_hi) = 2^381")
chk("1.2b", T_lo.denominator == 2 ** 382, "分母(T_lo) = 2^382")
chk("1.2c", T_hi.numerator % 2 == 1 and T_lo.numerator % 2 == 1,
    "两分子为奇数（故上面两个分母已是既约形式）")
W = T_lo - T_hi
chk("1.3a", W == F(3 * 5 ** 18, 2 ** 382), "精确宽度 = 3·5^18/2^382")
note("宽度（截断 24 位）= %s ；科学计数 = %s" % (dec_str(W, 24), sci(W, 12)))
chk("1.3b", sci(W, 12) == "1.161777574454e-102", "宽度的 12 位截断打印 = 1.161777574454e-102（日志 :52、:56）")
chk("1.3c", sci(W / T_hi, 12) == "3.709432774431e-123", "相对宽度 W/T_hi 的打印 = 3.709432774431e-123（日志 :56）")
# 增量与「400 步中点、起点为整数」自洽：T_hi − 312e18 乘以 2^381 为整数，等等
chk("1.3d", ((T_hi - 312 * 10 ** 18) * 2 ** 381).denominator == 1
    and ((T_lo - 312 * 10 ** 18) * 2 ** 382).denominator == 1,
    "两端点与 312×10^18 之差乘各自分母为整数（与「400 步中点」自洽）")
# 60 位小数打印相同（日志 :54 至 :55 的奇观：宽度 1.16e-102 远小于 1e-60，故截断相同）
same60 = dec_str(T_hi, 60) == dec_str(T_lo, 60)
chk("1.3e", same60, "两端点的 60 位小数截断打印相同（日志 :54、:55 的那一串）")
note("该串 = %s" % dec_str(T_hi, 60))

import r2_rig as R2  # noqa: E402
D2 = R2.delta_bounds()
L22 = R2.ln2_bounds()
GD_HI = GAMMA - D2[0]   # (γ − δ) 的上界：δ 取下界
GD_LO = GAMMA - D2[1]   # (γ − δ) 的下界：δ 取上界
eThi = R2.eps_bounds(92, 92, T_hi, D2[0], D2[1], L22)
eTlo = R2.eps_bounds(92, 92, T_lo, D2[0], D2[1], L22)
chk("1.4a", eThi[0] > GD_HI, "r2_rig 单点：eps(92,T_hi) 下界 > (γ−δ) 上界（符号 +）")
chk("1.4b", eTlo[1] < GD_LO, "r2_rig 单点：eps(92,T_lo) 上界 < (γ−δ) 下界（符号 −）")
note("eps(92,T_hi) = %s ；余量 = %s" % (sci(eThi[0], 16), sci(eThi[0] - GD_HI, 6)))
note("eps(92,T_lo) = %s ；负余量 = %s" % (sci(eTlo[0], 16), sci(GD_LO - eTlo[1], 6)))
chk("1.4c", sci(eThi[0], 16) == "6.2446806696927356e-43" and sci(eTlo[0], 16) == "6.2446806696927356e-43",
    "两端点的 eps(92,·) 打印与日志 :64、:85 的 6.2446806696927356e-43 一致")
chk("1.4d", sci(eThi[0] - GD_HI, 6) == "1.075910e-163" and sci(GD_LO - eTlo[1], 6) == "1.136322e-164",
    "两个余量打印与日志 :64（1.075910e-163）、:86（1.136322e-164）一致")

LK = slurp(LOG_K1)
KA, KB = frac_in(LK[60]), frac_in(LK[61])
chk("1.5a", KA <= T_hi, "[T_hi,T_lo] ⊆ [KA,KB]：KA ≤ T_hi")
chk("1.5b", T_lo <= KB, "[T_hi,T_lo] ⊆ [KA,KB]：T_lo ≤ KB")
note("余量：T_hi − KA = %s ；KB − T_lo = %s" % (sci(T_hi - KA, 12), sci(KB - T_lo, 12)))
chk("1.5c", sci(KB - KA, 6) == "2.052683e-30", "KB − KA 的打印 = 2.052683e-30（k1 日志 :64）")

# ------------------------------------------------------------------ 组 2
print("\n[2] 组 2：ε 梯子（k3_rig.eps_bounds 复算 K* 格 m2 = 83 至 91）")
import k3_rig as K3  # noqa: E402
D3 = K3.delta_bounds()
C3 = K3.C_bounds()
L23 = K3.ln2_bounds()
LA = slurp(LOG_A)
nstr, n20 = 0, 0
for m2 in range(83, 92):
    got = K3.eps_bounds(m2, M, KSTAR, D3[0], D3[1], L23)
    g_lo, g_hi = K3.sci(got[0], 22), K3.sci(got[1], 22)
    lo_s, hi_s = bracket_in(LA[12 + (m2 - 83)])       # 行 13 至 21
    ok = (g_lo == lo_s) and (g_hi == hi_s)
    nstr += ok
    n20 += (sig20(g_lo) == sig20(lo_s))
    if not ok:
        note("m2 = %d：重算 %s ；日志 %s" % (m2, g_lo, lo_s))
chk("2.1", nstr == 9, "9/9 格的全串（23 位有效数字）与 k3_run_a.out:13 至 :21 逐字一致：%d/9" % nstr)
chk("2.2", n20 == 9, "9/9 格的前 20 位有效数字一致：%d/9" % n20)
note("样例：eps(83,92,K*) = %s ；eps(91,92,K*) = %s" % (K3.sci(K3.eps_bounds(83, M, KSTAR, D3[0], D3[1], L23)[0], 22),
                                                        K3.sci(K3.eps_bounds(91, M, KSTAR, D3[0], D3[1], L23)[0], 22)))
feas = [t for t in range(1, M + 1) if K3.feasible(t, M, KSTAR, D3[0], D3[1], C3) is True]
infeas = [t for t in range(1, M + 1) if K3.feasible(t, M, KSTAR, D3[0], D3[1], C3) is False]
chk("2.3", feas == list(range(1, 92)) and infeas == [92],
    "F_92(K*) = {1,...,91}、不可行 = {92}、未定 = 0（k3_run_a.out:12）")

# ------------------------------------------------------------------ 组 3
print("\n[3] 组 3：438 条清单（k3_rig.semiconv_list_frontier）")
i27, l27 = find_line(LA, "delta 证书位数")
chk("3.0", ("167" in l27) and ("120" in l27) and ("k = 42" in l27),
    "证书位数 (delta 167, beta 120) 与首个相异下标 k = 42（k3_run_a.out 行 %d）" % (i27 + 1))
prefA = K3.certified_prefix(D3[0], D3[1], maxlen=250)
E91 = K3.eps_bounds(91, M, KSTAR, D3[0], D3[1], L23)
BLO, BHI = K3.rd(D3[0] + E91[0]), K3.ru(D3[1] + E91[1])
prefB = K3.certified_prefix(BLO, BHI, maxlen=250)
kk = 0
while kk < min(len(prefA), len(prefB)) and prefA[kk] == prefB[kk]:
    kk += 1
ck = min(prefA[kk], prefB[kk]) + 1
GAMrb = K3.cf_value(prefA[:kk] + [ck])
chk("3.1", (len(prefA), len(prefB), kk, ck) == (167, 120, 42, 2),
    "复算得 (|prefA|, |prefB|, k, c_k) = (%d, %d, %d, %d)" % (len(prefA), len(prefB), kk, ck))
chk("3.2", GAMrb == GAMMA and GAMrb.denominator == KSTAR,
    "独立重建 gamma = %d/%d（与登记值逐项相等且分母 = K*）" % (GAMrb.numerator, GAMrb.denominator))
chk("3.2b", gcd(GAMMA.numerator, GAMMA.denominator) == 1,
    "γ 的分子分母互素（route-1 §5.1 自报的最薄一环：B3 的候选分母条件）")
chk("3.3", GAMMA > D3[1] and GAMMA < BLO, "gamma ∈ (delta, beta(K*))（见证项，分母 = K*）")


def classify(items):
    ins = [(v, s) for (v, s) in items if v > D3[1] and v < BLO]
    out = sum(1 for (v, s) in items if v <= D3[0] or v >= BHI)
    return ins, out, len(items) - len(ins) - out


capped = K3.semiconv_list_frontier(prefA, prefB, kk, cap_q=KSTAR)
full = K3.semiconv_list_frontier(prefA, prefB, kk, cap_q=None)
i_c, o_c, u_c = classify(capped)
i_f, o_f, u_f = classify(full)
chk("3.4", (len(capped), len(i_c), o_c, u_c) == (438, 0, 438, 0),
    "cap_q = K*：条数 %d／严格在内 %d／严格在外 %d／未定 %d" % (len(capped), len(i_c), o_c, u_c))
chk("3.5", len(full) == 442, "完整清单（无 cap）条数 = %d" % len(full))
chk("3.6", len(full) - len(capped) == 4, "差集条数 = %d" % (len(full) - len(capped)))
capped_src = set((v, s) for (v, s) in capped)
dropped = [(v, s) for (v, s) in full if (v, s) not in capped_src]
chk("3.7", len(dropped) == 4 and all(v.denominator >= KSTAR for (v, s) in dropped),
    "被 cap 掉的 %d 条分母都 ≥ K*（最小 %d）" % (len(dropped), min(v.denominator for (v, s) in dropped)))
chk("3.8", len(i_f) == 2 and all(v == GAMMA for (v, s) in i_f),
    "完整清单的 2 个内点都等于 gamma（两种等价连分数写法）")
lo_p, hi_p = K3.sb_parents(GAMMA.numerator, GAMMA.denominator)
chk("3.9a", K3.unimodular(lo_p, hi_p) and lo_p[1] + hi_p[1] == KSTAR,
    "SB 双亲 unimodular 且分母和 = %d = K*（机制 i 的全称路径）" % (lo_p[1] + hi_p[1]))
chk("3.9b", F(lo_p[0], lo_p[1]) < D3[0] and F(hi_p[0], hi_p[1]) > BHI,
    "双亲低端 < delta_lo、高端 > beta_hi（严格，故 Farey 不等式适用）")
chk("3.9c", K3.mediant(lo_p, hi_p) == GAMMA, "双亲中项 = gamma")

# ------------------------------------------------------------------ 组 4
print("\n[4] 组 4：不动点（r4_common.psi_two_sided；引擎 kc_rig 含 v < 3 补丁）")
import r4_common as R4  # noqa: E402
CIV = R4.gauge_C(R4.X0_695)
DLO, DHI, RL2 = R4.consts()
for tag, Kv in (("K*", KSTAR), ("q41", Q41)):
    q_lo, q_hi, info = R4.psi_two_sided(Kv, CIV, DLO, DHI, RL2)
    chk("4.%s" % tag, q_lo == Kv and q_hi == Kv,
        "Psi_92(%s) ∈ [%s, %s]：两端都等于自身 ⟹ 该点是精确不动点" % (tag, q_lo, q_hi))
    note("%s：可行集 %d 项、argmin = %s、eps_opt ∈ [%s, %s]"
         % (tag, len(info["feas"]), info["argmin"], sci(info["lo"], 12), sci(info["hi"], 12)))
chk("4.D0", KSTAR + Q44 == D0, "K* + q44 的分母 = D0 = %d（r2_threshold_cert.log:32 的分母和）" % D0)
chk("4.wide", (BHI - D3[0]) < F(1, KSTAR),
    "beta − delta 的严格上界 < 1/K*（同分母至多一个分数，r4c 的计数判据）")

# ------------------------------------------------------------------ 跨库对拍
print("\n[5] 跨库对拍：三个独立实现（r2_rig / k3_rig / kc_rig）在同一量上的区间必须相交")
print("     注意：同库复算不是独立证明；两库相交只排除「至少一库实现有错」以外的一致错法。")
import kc_rig as KC  # noqa: E402
dk = KC.delta_bounds()
lk = KC.ln2_bounds()
d_r2, d_k3 = R2.delta_bounds(), D3
dl = {"r2_rig": (d_r2,), "k3_rig": (d_k3,), "kc_rig": (dk,)}


def inter(p, q):
    return max(p[0], q[0]), min(p[1], q[1])


def report_pair(name, a, b, la, lb):
    lo, hi = inter(a, b)
    chk("5.%s" % name, lo <= hi, "%s ∩ %s ≠ ∅（重叠宽 %s）" % (la, lb, sci(hi - lo, 4)))


report_pair("delta.r2k3", d_r2, d_k3, "r2_rig.delta", "k3_rig.delta")
report_pair("delta.r2kc", d_r2, dk, "r2_rig.delta", "kc_rig.delta")
report_pair("delta.k3kc", d_k3, dk, "k3_rig.delta", "kc_rig.delta")
e91 = {"r2_rig": R2.eps_bounds(91, M, KSTAR, d_r2[0], d_r2[1], L22),
       "k3_rig": K3.eps_bounds(91, M, KSTAR, D3[0], D3[1], L23),
       "kc_rig": KC.eps_bounds(91, M, KSTAR, dk[0], dk[1], lk)}
report_pair("eps91.r2k3", e91["r2_rig"], e91["k3_rig"], "r2_rig.eps(91,K*)", "k3_rig.eps(91,K*)")
report_pair("eps91.r2kc", e91["r2_rig"], e91["kc_rig"], "r2_rig.eps(91,K*)", "kc_rig.eps(91,K*)")
report_pair("eps91.k3kc", e91["k3_rig"], e91["kc_rig"], "k3_rig.eps(91,K*)", "kc_rig.eps(91,K*)")
chk("5.eps91.val", sci(e91["r2_rig"][0], 22) == "8.9732217086171360163257e-42"
    and sci(e91["k3_rig"][0], 22) == "8.9732217086171360163257e-42"
    and sci(e91["kc_rig"][0], 22) == "8.9732217086171360163257e-42",
    "三库的 eps(91,92,K*) 首端点打印都与 k3_run_a.out:21 的 8.9732217086171360163257e-42 一致")
e92thi = {"r2_rig": R2.eps_bounds(92, M, T_hi, d_r2[0], d_r2[1], L22),
          "k3_rig": K3.eps_bounds(92, M, T_hi, D3[0], D3[1], L23),
          "kc_rig": KC.eps_bounds(92, M, T_hi, dk[0], dk[1], lk)}
report_pair("eps92Thi.r2k3", e92thi["r2_rig"], e92thi["k3_rig"], "r2_rig.eps(92,T_hi)", "k3_rig.eps(92,T_hi)")
report_pair("eps92Thi.k3kc", e92thi["k3_rig"], e92thi["kc_rig"], "k3_rig.eps(92,T_hi)", "kc_rig.eps(92,T_hi)")
# 小 v 分支：K = 100、m2 = 5 时 v ≈ 0.35 < 3（kc_rig 的补丁路径；另两库的适用范围在此暴露）
small = {}
for tag, fn in (("kc_rig", lambda: KC.eps_bounds(5, M, 100, dk[0], dk[1], lk)),
                ("r2_rig", lambda: R2.eps_bounds(5, M, 100, d_r2[0], d_r2[1], L22)),
                ("k3_rig", lambda: K3.eps_bounds(5, M, 100, D3[0], D3[1], L23))):
    try:
        small[tag] = fn()
        note("%s：eps(5,92,100) ∈ [%s, %s]" % (tag, sci(small[tag][0], 22), sci(small[tag][1], 22)))
    except Exception as ex:
        small[tag] = None
        note("%s：抛 %s（%s）" % (tag, type(ex).__name__, str(ex)[:70]))
chk("5.smallv.kc", small["kc_rig"] is not None, "kc_rig（含 v < 3 补丁）可算小 v")
chk("5.smallv.gap", small["r2_rig"] is None and small["k3_rig"] is None,
    "r2_rig 与 k3_rig 在小 v 处都不可用（三库适用范围差异，登记；非四组断言的失败）")
try:                                   # 数值核对（非严格，仅补丁分支的单库覆盖问题）
    from mpmath import mp as _mp, mpf, log as _mlog, exp as _mexp
    _mp.dps = 160
    _d = _mlog(3) / _mlog(2)
    _t = _mexp(((mpf(5) / 92) * 100 * (_d - 1) / (_d ** 5 - 1)) * _mlog(2)) - 1
    _A = KC.A_of(5, M)                     # Fraction（mpmath 不接受 Fraction，须拆成两整数）
    _num = mpf(_A.numerator) / mpf(_A.denominator) + 3 / _t + 3 * 4 / _t ** _d
    _val = F(_mp.nstr(_num / (3 * mpf(100) * _mlog(2)), 100))
    _tol = _val * F(1, 10 ** 80)           # 区间本身宽 ~1e-98，故用 80 位一致而非「落在区间内」
    chk("5.smallv.numeric", abs(small["kc_rig"][0] - _val) <= _tol and abs(small["kc_rig"][1] - _val) <= _tol,
        "mpmath(160 dps，非证书) 的值与 kc_rig 补丁区间的两端都一致到 80 位有效数字")
except Exception as ex:
    chk("5.smallv.numeric", False, "mpmath 数值核对未执行：%s" % type(ex).__name__)
_g92 = KC.geom_bounds(92, dk[0], dk[1])
_Kv3 = (_g92[0] * 3, _g92[1] * 3)          # v(92,K) = 3 ⟺ K = 3·geom(92)
chk("5.smallv.range", _Kv3[1] < KSTAR,
    "v < 3 的 K 区间上界 K = 3·geom(92) ∈ [%s, %s]（远低于 K*，故四组断言不经过该区域）"
    % (sci(_Kv3[0], 12), sci(_Kv3[1], 12)))

# ------------------------------------------------------------------ 附加：分岔窗口
print("\n[6] 附加：分岔窗口宽度的跨库抽验（r4b2 的日志由 kc_rig 一系算出，这里用 k3_rig 复算门槛与符号）")
LB2 = slurp(LOG_B2)
i_c90, l_c90 = find_line(LB2, "c_90 ∈")
c90_log = bracket_in(l_c90)[0].replace(" ", "")
g90 = K3.geom_bounds(90, D3[0], D3[1])
c90 = (K3.rd(F(92, 90) * g90[0] * C3[0]), K3.ru(F(92, 90) * g90[1] * C3[1]))
chk("6.1", dec_str(c90[0], 30) == c90_log,
    "k3_rig 复算门槛 c_90 = %s（与 r4b2[0] 的 30 位打印一致）" % dec_str(c90[0], 30))
note("（注：门槛处 v(90,·) = C ≈ 70.18 是恒等式，本脚本另核 gamma 无关；此处只复算 c_90 的数值）")
K_mid = (c90[0] + c90[1]) / 2
for tag, r in (("6.2.in", F(78, 10 ** 14)), ("6.3.out", F(781, 10 ** 14))):
    Kr = K_mid * (1 + r)
    e89 = K3.eps_bounds(89, M, Kr, D3[0], D3[1], L23)
    e90 = K3.eps_bounds(90, M, Kr, D3[0], D3[1], L23)
    if tag.endswith("in"):
        chk(tag, e89[1] < e90[0],
            "相对偏移 7.80e-13（窗口内）：eps(89) < eps(90) 严格（旧档胜）")
    else:
        chk(tag, e90[1] < e89[0],
            "相对偏移 7.81e-13（窗口外）：eps(90) < eps(89) 严格（新档胜）")
    note("%s：eps(89) = %s ；eps(90) = %s" % (tag, sci(e89[0], 22), sci(e90[0], 22)))
chk("6.0", c90[1] < KSTAR, "c_90 < K*（有窗口的档位都在 K* 之下，不进目标区间）")
i_w, l_w = find_line(LB2, "j = 90 ：左端偏移")
i_b, l_b = find_line(LB2, "窗口右端 K*_j")
b_lo, b_hi = bracket_in(l_b)
w_lo = (F(b_lo) - c90[0]) / c90[1]
w_hi = (F(b_hi) - c90[0]) / c90[1]
chk("6.4", sci(w_lo, 12) == "7.806771365412e-13" and sci(w_hi, 12) == "7.806771365412e-13",
    "用日志右端 bracket 与 k3_rig 的 c_90 复算相对窗口宽 ∈ [%s, %s]" % (sci(w_lo, 12), sci(w_hi, 12)))
chk("6.5", not (w_lo <= F(2, 10 ** 24) <= w_hi) and not (w_lo <= F(15361313, 10 ** 30) <= w_hi),
    "旧值 2e-24 与 1.5361313e-23 都不落在该 bracket 内（route-5 的 2e-24 不获支持）")
chk("6.6", F(78, 10 ** 14) <= w_hi and F(781, 10 ** 14) >= w_lo,
    "两个抽验点把窗口右端夹在 [7.80e-13, 7.81e-13]（与 6.2、6.3 的符号翻转自洽）")
# j = 89 同款（H3 的第二个数字）
i89, _ = find_line(LB2, "j = 89 ：左端偏移")
b89_lo, b89_hi = bracket_in(LB2[i89 + 1])
i_c89, l_c89 = find_line(LB2, "c_89 ∈")
g89 = K3.geom_bounds(89, D3[0], D3[1])
c89 = (K3.rd(F(92, 89) * g89[0] * C3[0]), K3.ru(F(92, 89) * g89[1] * C3[1]))
w89_lo = (F(b89_lo) - c89[0]) / c89[1]
w89_hi = (F(b89_hi) - c89[0]) / c89[1]
chk("6.7", dec_str(c89[0], 30) == bracket_in(l_c89)[0].replace(" ", ""),
    "k3_rig 复算门槛 c_89 = %s（与 r4b2[0] 的 30 位打印一致）" % dec_str(c89[0], 30))
chk("6.8", sci(w89_lo, 12) == "7.714617758586e-13" and sci(w89_hi, 12) == "7.714617758586e-13",
    "j = 89 的相对窗口宽 ∈ [%s, %s]（r4b2 印 0.000000000000771461775858）" % (sci(w89_lo, 12), sci(w89_hi, 12)))
chk("6.9", not (w89_lo <= F(2, 10 ** 24) <= w89_hi) and not (w89_lo <= F(15361313, 10 ** 30) <= w89_hi),
    "j = 89 的 bracket 同样排除 2e-24 与 1.5361313e-23")

# ------------------------------------------------------------------ 汇总
print("\n" + "=" * 78)
print("汇总：判据 %d 条，失败 %d 条，用时 %.2f s" % (NCHK[0], len(FAILS), time.time() - T0))
if FAILS:
    print("失败清单：" + ", ".join(FAILS))
    print("退出码 1")
    sys.exit(1)
print("全部通过；退出码 0")
sys.exit(0)
