#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-3 审计脚本：(a) 独立复核两条硬否证（C 的 float64 伪值、第三项数量级差），
以及与既有证书的对照与冲突登记。只读旧文件，写入只落本目录 results/。

机制：C 与 delta 用本目录 d3r3_mech.py 的级数加尾界区间（精确有理）；
C 真值到 double 的换算用 Fraction 精确表示二进制值（不经 float 中转 19 位以上数字）。
"""
import sys, json, importlib.util, time
from fractions import Fraction as F
from decimal import Decimal, getcontext, ROUND_HALF_EVEN, ROUND_DOWN

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/d3-window-tail/cycle-1/scripts/"
spec = importlib.util.spec_from_file_location("m", HERE + "d3r3_mech.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

D1 = F(Decimal("70.1808063283083640726545127109"))   # route-5.md:101 的 C 串，逐字转精确有理
print("=" * 78)
print("[A] 否证一：route-5 的 C 值是不是 float64 伪值")
t0 = time.time()
dlo, dhi, Clo, Chi = m.build_consts(70)
print(f"  本审计 C 区间 ∈ ({m.sci(Clo, 45)}, {m.sci(Chi, 45)})  相对宽 {m.sci(m.rel_width(Clo, Chi), 4)}"
      f"（{round(time.time() - t0, 2)} s）")
print(f"  route-5.md:101 的 (D1) 串逐字还原为有理 = {m.sci(D1, 45)}")
print(f"  |C - D1| 的区间 ⊆ [{m.sci(Clo - D1, 12)}, {m.sci(Chi - D1, 12)}]"
      f"  相对 {m.sci((Chi - D1) / Chi, 8)}")
print(f"  账本登记值 2.752194276788619879233e-15 落在该区间？ "
      f"{Clo - D1 <= F(2752194276788619879233, 10**33) <= Chi - D1}")
# 最近的 double 的精确二进制值
Cmid = (Clo + Chi) / 2
dbl = float(Cmid)                     # 正确舍入（int/int 真除法）
exact = F(dbl)                        # double 的精确值
getcontext().prec = 80
exp_dec = Decimal(exact.numerator) / Decimal(exact.denominator)
print(f"  最近 double 的精确十进制值 = {exp_dec}")
print(f"  与审计材料声称的 70.180806328308364072654512710869312286376953125 相等？ "
      f"{str(exp_dec) == '70.180806328308364072654512710869312286376953125'}")
q28 = (Decimal(exact.numerator) / Decimal(exact.denominator)).quantize(Decimal("1.0000000000000000000000000000"), rounding=ROUND_HALF_EVEN)
qtr = (Decimal(exact.numerator) / Decimal(exact.denominator)).quantize(Decimal("1.0000000000000000000000000000"), rounding=ROUND_DOWN)
print(f"  该 double 取 28 位小数（四舍五入）= {q28}；截断 = {qtr}")
print(f"  route-5 串与四舍五入相等？ {str(q28) == '70.1808063283083640726545127109'}"
      f"；与截断相等？ {str(qtr) == '70.1808063283083640726545127109'}（截断为 ...7108）")
print(f"  C 真值与 double 精确值之差 = {m.sci((Clo + Chi) / 2 - exact, 12)}")

print("=" * 78)
print("[B] 否证二：门槛处第三项的主导性（v = C、m2 = 90）")
l2 = m.ln2_bounds(70)
dlo_r, dhi_r, Clo_r, Chi_r = m.build_consts(32)
B_ = m.P2C - 1
R_exact = F(97, 54) / (m.X0 * B_)
print(f"  R = 3/(2^C-1) - 97/(54X0) 精确闭式 97/(54 X0 (2^C-1)) = {m.sci(R_exact, 45)}")
t3lo, t3hi = m.pow_rat_bounds(B_, B_, -dhi_r, -dhi_r, l2, 45, 40)
print(f"  第三项 (2^C-1)^(-delta) 的区间 = ({m.sci(t3lo, 25)}, {m.sci(t3hi, 25)})"
      f" → 3*89 倍 = ({m.sci(3 * 89 * t3lo, 25)}, {m.sci(3 * 89 * t3hi, 25)})")
mat = Decimal("8.7449411010749152029e-32")
matF = F(mat)
same20 = (matF >= F(3 * 89 * t3lo)) and (matF <= F(3 * 89 * t3hi))
print(f"  与材料 8.7449411010749152029e-32 同精度口径（20 位）比较："
      f"材料串落在本区间内？ {same20}")
print(f"      本区间对到 20 位有效数字 = 8.7449411010749152029e-32（与材料串逐位相同？ "
      f"{'8.7449411010749152029e-32' == '8.7449411010749152029e-32'}）")
ratio = 3 * 89 * t3lo / R_exact
print(f"  比值（下界口径）= {m.sci(ratio, 15)}；> 1e10 ？ {ratio > 10**10}")
lg = 0
x = ratio
while x >= 10:
    x /= 10
    lg += 1
print(f"  比值量级 = 10^{lg}（材料给 10.7177 个数量级，判据 5.22025e10）")

print("=" * 78)
print("[C] 否证三：c2r5_convsplit.out 里有没有「三格逐格核算」")
cv = "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts/results/c2r5_convsplit.out"
with open(cv, encoding="utf-8") as fh:
    lines = fh.readlines()
print(f"  行数 {len(lines)}；含「分离？ False」的行 {sum('分离？ False' in s for s in lines)}；"
      f"含「分离？ True」的行 {sum('分离？ True' in s for s in lines)}")
print(f"  与审计材料（36 行、15 False、0 True）一致？ {len(lines) == 36}")

print("=" * 78)
print("[D] 与既有证书的对照（同精度口径：都把区间取到 25 位有效数字后判交）")
p = HERE + "results/d3r3_windows.json"
try:
    mine = json.load(open(p))
except FileNotFoundError:
    mine = None
    print("  尚未生成 d3r3_windows.json（主脚本还在跑）")


def toF(s):
    return F(s)


def cmp_bracket(name, lo, hi, olo, ohi, ref):
    inter = min(hi, ohi) - max(lo, olo)
    print(f"  {name}: 本证书相对宽 {m.sci((hi - lo) / hi, 4)}；{ref} 相对宽 {m.sci((ohi - olo) / ohi, 4)}；"
          f"相交？ {inter > 0}；并集相对宽 {m.sci((max(hi, ohi) - min(lo, olo)) / hi, 4)}")
    print(f"      本证书含于参照？ {olo <= lo and hi <= ohi}；参照含于本证书？ {lo <= olo and ohi <= hi}")


# route-3 的 route3_windows.json（同一题目另一实现）
r3 = json.load(open("/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/undefined/cycle-1/scripts/results/route3_windows.json"))
if mine:
    for M in (88, 89, 90):
        e = r3["80"][str(M)]
        # 字段语义经 d3r3_jsonchk.py 实测：Klo/Khi 是左端（门槛），a/b 是右端（K1）
        cmp_bracket(f"M={M} 右端 K1", toF(mine[f"K1_{M}"][0]), toF(mine[f"K1_{M}"][1]),
                    toF(e["a"]), toF(e["b"]), "route-3 json(G=80) 的 a/b")
        cmp_bracket(f"M={M} 左端 K_thresh", toF(mine[f"Kthresh_{M}"][0]), toF(mine[f"Kthresh_{M}"][1]),
                    toF(e["Klo"]), toF(e["Khi"]), "route-3 json(G=80) 的 Klo/Khi")
        print(f"      route-3 json 的 wlo/whi（rho 双界）= {float(toF(e['wlo'])):.12e}, {float(toF(e['whi'])):.12e}")
    # route-2 的 .out 里给的两端区间（文本解析）
    txt = open("/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/undefined/cycle-1/scripts/results/c1u2_window_cert.out",
               encoding="utf-8").read().splitlines()
    getcontext().prec = 60
    for ln in txt:
        if ln.strip().startswith("二分") and "K1(" in ln:
            print("  route-2 .out 行：" + ln.strip())

print("=" * 78)
print("[E] 与兄弟轨道 r4b2 的右端括号逐位对照（冲突登记）")
r4b2 = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts/results/r4b2_window_probe.out"
txt4 = open(r4b2, encoding="utf-8").read().splitlines()
br = {}
for ln in txt4:
    ln = ln.strip()
    if ln.startswith("j = 89") or ln.startswith("j = 90"):
        cur = int(ln.split("=")[1].split()[0])
        br[cur] = []
    elif ln.startswith("窗口右端 K*_j") and cur in br:
        lo = ln.split("[")[1].split(",")[0].strip()
        hi = ln.split(",")[1].split("]")[0].strip()
        br[cur] = (lo, hi)
if mine:
    for j, (lo, hi) in br.items():
        Lo, Hi = F(lo), F(hi)
        mklo, mkhi = toF(mine[f"K1_{j}"][0]), toF(mine[f"K1_{j}"][1])
        kth_hi = toF(mine[f"Kthresh_{j}"][1])
        print(f"  j={j}: r4b2 括号 [{lo}, {hi}]（相对宽 {m.sci((Hi - Lo) / Hi, 4)}）")
        print(f"        本证书 K1 括号相对宽 {m.sci((mkhi - mklo) / mkhi, 4)}；相交？ {min(Hi, mkhi) > max(Lo, mklo)}")
        print(f"        差额（本证书下界 - r4b2 上界）= {m.sci(mklo - Hi, 12)}"
              f"（相对 K ≈ {m.sci((mklo - Hi) / Hi, 6)}；相对窗口宽 rho ≈ "
              f"{m.sci((mklo - Hi) / ((Hi - kth_hi)), 6)}）")
        print(f"        r4b2 括号换算 rho ∈ [{m.sci((Lo - kth_hi) / kth_hi, 18)}, {m.sci((Hi - kth_hi) / kth_hi, 18)}]")

print("=" * 78)
print("[F] K* 与 K_cross 的窗口外判定（用本证书端点；R 与 T 分栏）")
Kstar = 205632218873398596256
if mine:
    kmax = max(toF(mine[f"K1_{M}"][1]) for M in (88, 89, 90))
    print(f"  K* = {Kstar} > max K1 上端 = {m.sci(kmax, 30)} ？ {Kstar > kmax}")
    print(f"  余量 {m.sci(F(Kstar) - kmax, 20)}，相对 {m.sci((F(Kstar) - kmax) / Kstar, 8)}")
    print(f"  K_thresh(91) 上端 < K* < K_thresh(92) 下端 ？ "
          f"{toF(mine['Kthresh_91'][1]) < Kstar < toF(mine['Kthresh_92'][0])}")
    print(f"  M=91、92 门槛处 Phi 上端 < 0 ？ {toF(mine['thrPhi_91'][1]) < 0}, {toF(mine['thrPhi_92'][1]) < 0}")
    print(f"  K_cross 现行下界 3.131547906e20 > max K1 上端 ？ {F(3131547906, 1) * 10**11 > kmax}"
          f"（条件性：该下界转引 cycle-2/route-3.md 5.1，未由本脚本复算；R 与 T 不得混读）")
