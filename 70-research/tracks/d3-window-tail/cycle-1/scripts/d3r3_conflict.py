#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
冲突裁决：用本目录精确有理判定器（d3r3_mech 的 Oracle）逐点判定 Phi_90 的符号，
夹住 r4b2_window_probe.out 的右端括号与 d3r3_indbisect 的 MPFR 括号谁在根的正确一侧。
只读旧文件，输出落本目录 results/。
"""
import json, importlib.util
from fractions import Fraction as F

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/d3-window-tail/cycle-1/scripts/"
spec = importlib.util.spec_from_file_location("m", HERE + "d3r3_mech.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# 高精度判定器实例：全精度常量 + 更细网格，用于把判定宽度压到 10^-35 以下
dlo, dhi, Clo, Chi = m.build_consts(70)
orc = m.Oracle(dlo, dhi, Clo, Chi, Gv=34, Gexp=26, K=50, Nln=55, Gser=50)
mine = json.load(open(HERE + "results/d3r3_windows.json"))

R4_LO = F("123124614107652692133.007231711933058876044901")
R4_HI = F("123124614107652692133.007231919710646726095849")
MP_LO = F("123124614107652692133.0072322914378057066853155987473655841313302516937255859375")
MP_HI = F("123124614107652692133.00723229150298733414192753343741060234606266021728515625")
CERT_LO, CERT_HI = F(mine["K1_90"][0]), F(mine["K1_90"][1])

print("=" * 78)
print("[G] 冲突裁决：Phi_90 的符号（精确有理判定器，判定宽度约 1e-50）")
pts = [("本证书下端", CERT_LO), ("r4b2 下端", R4_LO), ("r4b2 上端", R4_HI),
       ("MPFR 下端", MP_LO), ("MPFR 上端", MP_HI), ("本证书上端", CERT_HI)]
prev = None
for name, K in pts:
    s, lo, hi = orc.sign(90, K)
    print(f"  {name:10s} K = {m.sci(K, 34)}  Phi ∈ [{m.sci(lo, 12)}, {m.sci(hi, 12)}]  符号 {s}")
    prev = (name, K, s)
print()
print(f"  r4b2 括号 [r4b2 下端, r4b2 上端] 上的符号 = "
      f"[{orc.sign(90, R4_LO)[0]}, {orc.sign(90, R4_HI)[0]}]（+1 正、-1 负、0 判不出）")
print(f"  MPFR 括号   上的符号 = [{orc.sign(90, MP_LO)[0]}, {orc.sign(90, MP_HI)[0]}]")
print(f"  r4b2 上端与 MPFR 下端的间隔 = {m.sci(MP_LO - R4_HI, 12)}"
      f"（相对 K ≈ {m.sci((MP_LO - R4_HI) / R4_HI, 6)}）")
# 收窄：在 r4b2 上端与 MPFR 下端之间二分，定位精确判定器给出的根位置
L, H = R4_HI, MP_LO
steps = 0
while (H - L) / L > F(1, 10**24) and steps < 60:
    mid = (L + H) / 2
    s = orc.sign(90, mid)[0]
    if s == 1:
        L = mid
    elif s == -1:
        H = mid
    else:
        break
    steps += 1
print(f"  精确判定器在 r4b2 上端与 MPFR 下端之间夹出根所在区间（{steps} 步）：")
print(f"    K1(90) ∈ ({m.sci(L, 34)}, {m.sci(H, 34)}) 相对宽 {m.sci((H - L) / L, 4)}")
print(f"    该区间与 r4b2 括号相交？ {min(H, R4_HI) > max(L, R4_LO)}；与 MPFR 括号相交？ {min(H, MP_HI) > max(L, MP_LO)}")
