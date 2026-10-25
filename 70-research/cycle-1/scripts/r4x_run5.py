#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 第 6 轮：margin-table.txt:82 至 :85 四行的独立复算（m = 92 至 95）。

对照目标（materials.md §2.5 内第 3 条逐字照录）：
  92  77692117359936589403   3.4302597024885020978e+20   0.226490482057595771625621  不排除
  93  77692117359936589403   5.4959290070072201196e+20   0.141363029363880798043112  不排除
  94  77692117359936589403   8.8045063438367505777e+20   0.0882413099904481410077378 不排除
  95  77692117359936589403   1.4103267843325149962e+21   0.055088025146389756810149  不排除
以及 m = 91 行（:81）与 :104 至 :105 的自检数字。
"""
import sys
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
from mpmath import mp, mpf
import r4x_core as R

OUT = []
def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)

R.set_dps(120)
REF = {
    91: ("7941964418702608664581", "2.1407284206382892328e+20", "37.0993552574716449275895"),
    92: ("77692117359936589403", "3.4302597024885020978e+20", "0.226490482057595771625621"),
    93: ("77692117359936589403", "5.4959290070072201196e+20", "0.141363029363880798043112"),
    94: ("77692117359936589403", "8.8045063438367505777e+20", "0.0882413099904481410077378"),
    95: ("77692117359936589403", "1.4103267843325149962e+21", "0.055088025146389756810149"),
}
p("[H] margin-table.txt:81 至 :85 与 :104 至 :105 的独立复算（起点 L = 7.5311e11）")
for m in (91, 92, 93, 94, 95):
    seq, term, over = R.chain(m, mpf("7.5311e11"), cap=R.sdw_upper(m))
    U = R.sdw_upper(m)
    ratio = mpf(term) / U
    ref = REF[m]
    ok = (str(term) == ref[0]) and (mp.nstr(U, 22) == ref[1])
    p("     m=%d 终值=%-22s 表值=%-22s 一致=%s" % (m, term, ref[0], str(term) == ref[0]))
    p("          U=%-24s 表值=%-24s 一致=%s" % (mp.nstr(U, 22), ref[1], mp.nstr(U, 22) == ref[1]))
    p("          余量=%-30s 表值=%s" % (mp.nstr(ratio, 26), ref[2]))
    p("          余量前 16 位与表值一致？%s ；前 25 位与表值一致？%s" % (
        mp.nstr(ratio, 16) == ref[2][:16], mp.nstr(ratio, 25) == ref[2][:25]))
    # 该 m 的链条步数
    p("          链条步数=%d ；末步 m2=%s ；末步 eps=%s" % (
        len(seq), seq[-1].get("m2"), mp.nstr(seq[-1].get("eps"), 8) if seq[-1].get("eps") else None))
p()
p("[H1] 论文第 7 步 eps 与我算值的差异（登记）")
seq, term, over = R.chain(91, mpf("7e11"), cap=R.sdw_upper(91))
p("     我第 7 步：K_in=%s eps=%s Psi=%s" % (seq[-1]["K_in"], mp.nstr(seq[-1]["eps"], 8), seq[-1]["psi"]))
p("     论文：δ < (K+L)/K < δ + 1.11e-43 且 K > 7.94e21")
# 用论文的取整阈值 2.05e20 试
r = R.psi(91, mpf("2.05e20"))
p("     若阈值取论文写的 2.05e20：m2=%s eps=%s Psi=%s（仍不是 1.11e-43）" % (
    r["m2"], mp.nstr(r["eps"], 8), r["psi"]))
p()

open("/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts/results/r4x_run5.out", "w").write("\n".join(OUT) + "\n")
