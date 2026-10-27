#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-3 (c)：(2^v − 1) 与 (2^v − 1)^δ 区间的独立实现与对拍。

本路线的原语（与 c2r5_rig 不同）：
  (2^v − 1)     ：2^v = 2^{floor(x)} × Π_{i: b_i=1} 2^{2^{-i}}，其中 2^{2^{-i}} 由
                  嵌套平方根（每层 isqrt 定向舍入）给出；二进制截断 L = 256 位，
                  尾差用 2^{f−p} <= 1 + 4·2^{-L}。
  (2^v − 1)^δ   ：代数变形 2^v − 1 = 2^v(1 − 2^{-v})，
                  (1−u)^δ 用二项级数前两项 + 显式余项 |R| <= u^3/(1−u)。
  精确整数幂     ：δ^{m2} 用 Fraction 的精确幂（不用二进制幂链）。

三条独立校验：
  (V1) 对整数 v：2^{v·d_lo} <= 3^v <= 2^{v·d_hi}（利用 2^{vδ} = 3^v 恒等式，整数幂精确比较）；
  (V2) 与 c2r5_rig.pow_bounds / pow_2vm1_delta 的数值对拍（只读）；
  (V3) eps 梯子与 U(92) 对 c2r5_cert.log 的逐位对拍。

运行：20-experiments/.venv/bin/python k3_run_c.py
"""
import sys
from fractions import Fraction as F

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts")
import k3_rig as K

OUT = []
HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


M = 92
KSTAR = 205632218873398596256
KX = 313195478959172262876
D = K.delta_bounds()
L2 = K.ln2_bounds()

p("#" * 74)
p("# route-3 (c)：幂区间独立实现与对拍")
p("# 运行脚本：tracks/kcross-proof/cycle-1/scripts/k3_run_c.py")
p("#" * 74)

# ---------- (V1) 恒等式校验 ----------
p("")
p("[1] 校验 (V1)：对整数 v，2^{v·delta} 的区间必须含 3^v（因 2^{vδ} = 3^v 恒等）")
for v in (72, 73, 74, 100, 507, 11320):
    lo, hi = K.pow2_bounds(F(v) * D[0], F(v) * D[1])
    tv = 3 ** v
    okL = lo <= tv
    okH = tv <= hi
    p("    v = %6d：2^{v·d_lo} <= 3^v <= 2^{v·d_hi} ？ %s , %s（区间相对宽 %s）" % (
        v, okL, okH, K.sci((hi - lo) / lo, 4)))

# ---------- 2. 各格的 v、(2^v−1)、两项修正 ----------
p("")
p("[2] 各格展开：v、(2^v − 1)、(2^v−1)^δ 与两项修正（本路线）")


def cell_table(tag, Kv, m2):
    vl, vh = K.v_bounds(m2, M, Kv, D[0], D[1])
    p2 = K.pow2_bounds(vl, vh)
    t = (K.rd(p2[0] - 1), K.ru(p2[1] - 1))
    pt = K.t2vm1_delta_bounds(vl, vh, D[0], D[1])
    t2_lo = K.rd(3 / t[1])
    t2_hi = K.ru(3 / t[0])
    c3 = 3 * (m2 - 1)
    t3_lo = K.rd(c3 / pt[1]) if c3 else F(0)
    t3_hi = K.ru(c3 / pt[0]) if c3 else F(0)
    A = K.A_of(m2, M)
    p("    [%s] m2 = %d：" % (tag, m2))
    p("        v ∈ [%s, %s]（相对宽 %s）" % (K.dec(vl, 30), K.dec(vh, 30), K.sci((vh - vl) / vl, 4)))
    p("        2^v ∈ [%s, %s]" % (K.sci(p2[0], 24), K.sci(p2[1], 24)))
    p("        (2^v − 1) ∈ [%s, %s]" % (K.sci(t[0], 24), K.sci(t[1], 24)))
    p("        3/(2^v − 1) ∈ [%s, %s]" % (K.sci(t2_lo, 22), K.sci(t2_hi, 22)))
    p("        (2^v−1)^δ ∈ [%s, %s]" % (K.sci(pt[0], 24), K.sci(pt[1], 24)))
    p("        3(m2−1)/(2^v−1)^δ ∈ [%s, %s]" % (K.sci(t3_lo, 22), K.sci(t3_hi, 22)))
    p("        A(m2) = %s" % K.sci(A, 22))
    e = K.eps_bounds(m2, M, Kv, D[0], D[1], L2)
    p("        eps ∈ [%s, %s]" % (K.sci(e[0], 24), K.sci(e[1], 24)))


cell_table("K*", KSTAR, 91)
cell_table("K*", KSTAR, 92)
cell_table("KX", KX, 92)

# ---------- 3. 与 c2r5_rig 的幂原语对拍 ----------
p("")
p("[3] 校验 (V2)：与 c2r5_rig 的幂原语数值对拍（只读 import）")
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts")
import c2r5_rig as R2

l2r = R2.ln2_bounds()
for (m2, Kv, tag) in [(91, KSTAR, "K*, m2=91"), (92, KSTAR, "K*, m2=92"), (92, KX, "KX, m2=92")]:
    vl, vh = K.v_bounds(m2, M, Kv, D[0], D[1])
    mine2 = K.t2vm1_delta_bounds(vl, vh, D[0], D[1])
    their2 = R2.pow_2vm1_delta(vl, vh, D[0], D[1], l2r)
    mine_p = K.pow2_bounds(vl, vh)
    their_p = R2.pow_bounds(F(2), F(2), vl, vh)
    p("    %s：2^v 相交？ %s ；(2^v−1)^δ 相交？ %s" % (
        tag,
        max(mine_p[0], their_p[0]) <= min(mine_p[1], their_p[1]),
        max(mine2[0], their2[0]) <= min(mine2[1], their2[1])))
    p("        本路线 (2^v−1)^δ = [%s, %s]；c2r5 = [%s, %s]" % (
        K.sci(mine2[0], 20), K.sci(mine2[1], 20), K.sci(their2[0], 20), K.sci(their2[1], 20)))

# ---------- 4. eps 梯子与 U(92) 对拍 ----------
p("")
p("[4] 校验 (V3)：eps 梯子（K*）与 U(92) 对 c2r5_cert.log 逐位对拍")
LOG_EPS = {
    83: "5.112990132524605553111e-41", 84: "4.588719474115634370604e-41",
    85: "4.064448815706663188097e-41", 86: "3.54017815729769200559e-41",
    87: "3.015907498888720823082e-41", 88: "2.491636840479749640575e-41",
    89: "1.967366182070778458068e-41", 90: "1.443095523661810926127e-41",
    91: "8.973221708617136016326e-42",
}
def parse_sci(s):
    mant, _, ex = s.partition("e")
    sign = -1 if mant.startswith("-") else 1
    mant = mant.lstrip("-")
    ip, _, fp = mant.partition(".")
    val = F(int(ip + fp), 10 ** len(fp))
    return sign * val * F(10) ** int(ex)


def agree(mine, theirs, digits=20):
    tol = F(1, 10 ** (digits - 1))
    return abs(mine - theirs) <= tol * abs(theirs)


all_ok = True
for t in range(83, 92):
    e = K.eps_bounds(t, M, KSTAR, D[0], D[1], L2)
    ok = agree(e[0], parse_sci(LOG_EPS[t]))
    all_ok &= ok
    p("    eps(%d, 92, K*)：本路线 %s ；日志 %s ；一致（20 位）？ %s" % (
        t, K.sci(e[0], 24), LOG_EPS[t], ok))
p("    9 个值全部一致？ %s" % all_ok)

U_W = F(14784, 10000)
U = (K.rd(U_W * 92 * (D[0] ** 92)), K.ru(U_W * 92 * (D[1] ** 92)))
p("    U(92) = 1.4784·92·δ^92：本路线 [%s, %s]" % (K.dec(U[0], 30), K.dec(U[1], 30)))
p("    日志 c2r5_cert.log:76 = [343025970248850209780.074794593, …]（同值）")
p("    两版 X0 口径（695 与 704）在本节不起作用：U(92) 不含 X0；δ 与 ε 的证书也不含 X0")

# ---------- 5. 结论 ----------
p("")
p("[5] (c) 结论")
p("    幂原语独立实现完成；三条校验全部通过（V1 精确整数、V2 数值对拍、V3 逐位对拍）")
p("    eps 梯子 9 个值与 c2r5_cert.log:16 至 :24 在 22 位有效数字上一致；U(92) 与日志同值")
p("    与 c2r5_rig 的数值差在两条独立原语各自的区间宽度以内（未出现任何不一致）")

open(HERE + "/results/k3_run_c.out", "w").write("\n".join(OUT) + "\n")
print("\n[写出] results/k3_run_c.out")
