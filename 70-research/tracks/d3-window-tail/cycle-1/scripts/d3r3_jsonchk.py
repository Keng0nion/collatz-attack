#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核查 route3_windows.json 的字段语义：Klo/Khi 与 a/b 各是哪一端。"""
import json, sys
from fractions import Fraction as F
sys.set_int_max_str_digits(2000000)

HERE = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/d3-window-tail/cycle-1/scripts/"
r3 = json.load(open("/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/undefined/cycle-1/scripts/results/route3_windows.json"))
mine = json.load(open(HERE + "results/d3r3_windows.json"))

for M in (88, 89, 90):
    e = r3["80"][str(M)]
    Klo, Khi, a, b = F(e["Klo"]), F(e["Khi"]), F(e["a"]), F(e["b"])
    print(f"j={M}: Klo = {Klo.numerator}/{Klo.denominator}")
    print(f"      Khi = {float(Khi):.18e} ；a = {float(a):.18e} ；b = {float(b):.18e}")
    mk1 = (F(mine[f"K1_{M}"][0]), F(mine[f"K1_{M}"][1]))
    mkt = (F(mine[f"Kthresh_{M}"][0]), F(mine[f"Kthresh_{M}"][1]))
    print(f"      本 K1 ∈ [{float(mk1[0]):.18e}, {float(mk1[1]):.18e}]")
    print(f"      本 K_thresh ∈ [{float(mkt[0]):.18e}, {float(mkt[1]):.18e}]")
    print(f"      本 K1 与 [Klo,Khi] 相交？ {min(Khi, mk1[1]) > max(Klo, mk1[0])}；"
          f"与 [a,b] 相交？ {min(b, mk1[1]) > max(a, mk1[0])}")
    print(f"      本 K_thresh 与 [a,b] 相交？ {min(b, mkt[1]) > max(a, mkt[0])}；"
          f"与 [Klo,Khi] 相交？ {min(Khi, mkt[1]) > max(Klo, mkt[0])}")
    # 相对宽字段核算
    wlo, whi = F(e["wlo"]), F(e["whi"])
    print(f"      wlo, whi = {float(wlo):.6e}, {float(whi):.6e}；"
          f"(Khi-Klo)/Khi = {float((Khi - Klo) / Khi):.6e}；(b-a)/b = {float((b - a) / b):.6e}；"
          f"(b-a)/a = {float((b - a) / a):.6e}")
