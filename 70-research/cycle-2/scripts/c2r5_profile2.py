#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 2 轮第 5 路：对单次 eps_bounds 做 cProfile，定位真正的耗时点。"""
import cProfile
import pstats
import sys
from fractions import Fraction as F

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts")
import c2r5_rig as R

dl, dh = R.delta_bounds()
l2 = R.ln2_bounds()
K = 205632218873398596256

pr = cProfile.Profile()
pr.enable()
e = R.eps_bounds(91, 92, K, dl, dh, l2)
pr.disable()
print("eps =", float(e[0]))
st = pstats.Stats(pr)
st.sort_stats("cumulative").print_stats(14)
st.sort_stats("tottime").print_stats(10)
