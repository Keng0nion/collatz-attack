#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify.py —— vertex-tail 路线三「确定性闸门」。

对下述四类可机器复算的断言做复算，全部通过则退出码 0，任一失败退出码 1：

  1. 顶点集计数关系：每个检查点目录（分片 [start, end) 铺满 [0, C(2m2+1, m2))，
     且 Σ片 count == C(2m2+1, m2)，且 n_rank_def + n_infeasible + Σ顶点捕捉数 == Σ count）。
  2. m₂ = 10 阳性对照：两个引擎（fraction、mpq）检查点的可行顶点集都精确等于
     v = W(δ−1)/(δ^m2−1) 的 10 个循环旋转（有理数逐坐标精确比较）。
  3. 检查点自带证书的活跃秩等于活跃条数：对每个检查点里每个可行顶点，用自己的
     Fraction 秩代码复算（活跃约束法向量秩, 活跃约束条数）；主档 10、12、13、14
     断言 == (m2, m2)，阴性档 smoke_m2_2 断言 == (2, 2)，边界档 smoke_m2_5 与
     det_run1/2 断言 == (5, 6)（W 取阈值使 v = 1，回绕外的和约束也取等，故条数比秩多 1）。
  4. 双实现顶点坐标相等：route3_impl1_{m10, m12}.json 与 route3_impl2_{m10, m12}.json
     的 candidate_points_sorted 解析为精确有理坐标后集合相等。

只读，不重跑任何枚举；本脚本不与被核对脚本共享秩代码。
"""
import glob
import json
import math
import os
import sys
from fractions import Fraction

M12 = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/vertex-m12/cycle-1"
DELTA = Fraction(126797, 80000)
W2000 = Fraction(2000)
W5 = (DELTA ** 5 - 1) / (DELTA - 1)          # 使 v = 1 的阈值 W

NFAIL = 0
NPASS = 0


def check(tag, ok, detail=""):
    global NFAIL, NPASS
    if ok:
        NPASS += 1
    else:
        NFAIL += 1
    print("%s | %s | %s" % ("PASS" if ok else "FAIL", tag, detail))


def parse_point(s):
    return tuple(Fraction(x) for x in s.split(","))


def analytic_set(m2, delta, W):
    v = Fraction(W) * (delta - 1) / (delta ** m2 - 1)
    return {tuple(v * delta ** ((j + r) % m2) for j in range(m2)) for r in range(m2)}


def my_rank(rows, ncols):
    M = [[Fraction(x) for x in r] for r in rows]
    rank = 0
    for col in range(ncols):
        piv = None
        for i in range(rank, len(M)):
            if M[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        pv = M[rank][col]
        M[rank] = [x / pv for x in M[rank]]
        for i in range(len(M)):
            if i != rank and M[i][col] != 0:
                f = M[i][col]
                M[i] = [M[i][j] - f * M[rank][j] for j in range(ncols)]
        rank += 1
        if rank == len(M):
            break
    return rank


def my_constraint_rows(m2, delta, W):
    p, q = delta.numerator, delta.denominator
    wn, wd = W.numerator, W.denominator
    cons = []
    for j in range(m2):
        row = [0] * m2
        row[j] = q
        cons.append((row, q))
    for j in range(m2):
        row = [0] * m2
        row[(j + 1) % m2] = q
        row[j] -= p
        cons.append((row, 0))
    cons.append(([q * wd] * m2, q * wn))
    return cons


def my_certificate(y, m2, delta, W):
    cons = my_constraint_rows(m2, delta, W)
    act = []
    for row, rhs in cons:
        val = sum(Fraction(row[k]) * y[k] for k in range(m2))
        if val == rhs:
            act.append(row)
    return my_rank(act, m2), len(act)


def load_ckpt(d):
    files = sorted(glob.glob(os.path.join(M12, "results/ckpt", d, "chunk_*.json")))
    tot = nrd = ninf = sumcnt = 0
    keys = {}
    spans = []
    for f in files:
        j = json.load(open(f))
        tot += j["count"]
        nrd += j["n_rank_def"]
        ninf += j["n_infeasible"]
        spans.append((j["start"], j["end"]))
        for k, v in j["feasible"].items():
            keys[k] = v
            sumcnt += v["count"]
    return files, tot, nrd, ninf, sumcnt, keys, spans


# 目录清单：目录名, m2, 该档 δ, 该档 W, 期望顶点数, 期望证书
DIRS = [
    ("m2_10_fraction", 10, DELTA, W2000, 10, (10, 10)),
    ("m2_10_mpq", 10, DELTA, W2000, 10, (10, 10)),
    ("m2_12_fraction", 12, DELTA, W2000, 12, (12, 12)),
    ("m2_12_mpq", 12, DELTA, W2000, 12, (12, 12)),
    ("m2_13_fraction", 13, DELTA, W2000, 13, (13, 13)),
    ("m2_13_mpq", 13, DELTA, W2000, 13, (13, 13)),
    ("m2_14_mpq", 14, DELTA, W2000, 14, (14, 14)),
    ("smoke_m2_2", 2, Fraction(3, 2), Fraction(3, 2), 3, (2, 2)),
    ("smoke_m2_2_mpq", 2, Fraction(3, 2), Fraction(3, 2), 3, (2, 2)),
    ("smoke_m2_5", 5, DELTA, W5, 5, (5, 6)),
    ("smoke_m2_5_mpq", 5, DELTA, W5, 5, (5, 6)),
    ("det_run1", 5, DELTA, W5, 5, (5, 6)),
    ("det_run2", 5, DELTA, W5, 5, (5, 6)),
]

print("=== 断言 1：顶点集计数关系 ===")
ck = {}
for d, m2, dlt, W, ekeys, ecert in DIRS:
    files, tot, nrd, ninf, sumcnt, keys, spans = load_ckpt(d)
    ck[d] = (m2, dlt, W, keys)
    comb = math.comb(2 * m2 + 1, m2)
    sp = sorted(spans)
    tile = len(sp) > 0 and sp[0][0] == 0 and all(sp[i][1] == sp[i + 1][0] for i in range(len(sp) - 1)) and sp[-1][1] == tot
    check("A1 %s" % d, tot == comb and nrd + ninf + sumcnt == tot and tile and len(keys) == ekeys,
          "片=%d Σcount=%d C(2m2+1,m2)=%d nrd+ninf+Σ捕捉=%d+%d+%d=%d 铺满=%s 顶点=%d/%d" % (
              len(files), tot, comb, nrd, ninf, sumcnt, nrd + ninf + sumcnt, tile, len(keys), ekeys))

print("=== 断言 2：m₂ = 10 阳性对照（两引擎各自 == 解析 10 旋转） ===")
ana10 = analytic_set(10, DELTA, W2000)
for d in ("m2_10_fraction", "m2_10_mpq"):
    keys = {parse_point(k) for k in ck[d][3]}
    check("A2 %s 顶点集 == 解析族" % d, keys == ana10, "顶点=%d 交集=%d 解析=%d" % (len(keys), len(keys & ana10), len(ana10)))
check("A2 阴性对照 smoke_m2_2 顶点集 != 解析族（判别力）",
      {parse_point(k) for k in ck["smoke_m2_2"][3]} != analytic_set(2, Fraction(3, 2), Fraction(3, 2)), "")

print("=== 断言 3：检查点自带证书（活跃秩, 活跃条数），逐顶点复算 ===")
for d, m2, dlt, W, ekeys, ecert in DIRS:
    keys = {parse_point(k) for k in ck[d][3]}
    certs = sorted({my_certificate(y, m2, dlt, W) for y in keys})
    check("A3 %s 证书 == %s" % (d, ecert), certs == [ecert], "实测 %s" % certs)
# 解析族与顶点集相等性（主档）作为附注：证书和顶点两重独立
for d in ("m2_12_mpq", "m2_13_mpq", "m2_14_mpq"):
    m2 = ck[d][0]
    keys = {parse_point(k) for k in ck[d][3]}
    check("A3 %s 顶点集 == 解析族" % d, keys == analytic_set(m2, DELTA, W2000), "顶点=%d" % len(keys))

print("=== 断言 4：双实现顶点坐标相等 ===")
for tag, fa, fb in [("m2_10", "route3_impl1_m10.json", "route3_impl2_m10.json"),
                    ("m2_12", "route3_impl1_m12.json", "route3_impl2_m12.json")]:
    A = json.load(open(os.path.join(M12, "results", fa)))
    B = json.load(open(os.path.join(M12, "results", fb)))
    pa = {parse_point(x) for x in A["candidate_points_sorted"]}
    pb = {parse_point(x) for x in B["candidate_points_sorted"]}
    check("A4 %s 坐标集合相等" % tag, pa == pb and len(pa) > 0, "点数=%d/%d" % (len(pa), len(pb)))
    check("A4 %s 两文件各自与解析族相等" % tag,
          pa == analytic_set(int(tag.split("_")[1]), DELTA, W2000) and A["analytic_equal_candidate_set"] and B["analytic_equal_candidate_set"], "")
    # 与检查点交叉（额外）
    dck = "m2_10_mpq" if tag == "m2_10" else "m2_12_mpq"
    check("A4 %s 与检查点顶点集相等" % tag, pa == {parse_point(k) for k in ck[dck][3]}, "")

print("")
print("PASS=%d FAIL=%d" % (NPASS, NFAIL))
sys.exit(0 if NFAIL == 0 else 1)
