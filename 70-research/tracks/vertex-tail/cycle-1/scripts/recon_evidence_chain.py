#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""recon_evidence_chain.py —— vertex-tail 路线三「证据链对账」的对账器（只读）。

对账对象：70-research/tracks/vertex-m12/cycle-1 下的五份报告与四类原始产物。
本脚本不重跑任何枚举：只做 md5、行数、字节数、直方图、字段提取、集合比较。
每项一行：PASS 表示与登记值一致；FAIL 表示不一致或数字对不上；INFO 为登记性信息。
末行打印 FAIL 总数。退出码 = 0 当且仅当 FAIL 总数为 0。
"""
import glob
import hashlib
import json
import math
import os
import re
import sys
from fractions import Fraction

M12 = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/vertex-m12/cycle-1"
R1 = "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1"
DELTA = Fraction(126797, 80000)
W2000 = Fraction(2000)

NFAIL = 0


def check(tag, ok, detail=""):
    global NFAIL
    if not ok:
        NFAIL += 1
    print("%s | %s | %s" % ("PASS" if ok else "FAIL", tag, detail))


def info(tag, detail=""):
    print("INFO | %s | %s" % (tag, detail))


def md5f(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def nbytes_lines(p):
    n = 0
    nl = 0
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 22), b""):
            n += len(blk)
            nl += blk.count(b"\n")
    return n, nl


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


print("=== R1 五份报告身份（登记值来源：vertex-tail/cycle-1/materials.md 9.1 表） ===")
rep_reg = {
    "route-1.md": ("939cc627c887fd4064214b14accfa651", 293),
    "route-2.md": ("9db46ca0d456a7c463f63adf776aa40e", 380),
    "route-3.md": ("8b8fe031050f630565a1c58a5e53a560", 351),
    "route-4.md": ("e5ff27b061020b6aa81e326bd54c0b70", 399),
    "route-5.md": ("3e833e440ceb5cc74d3470b24ac8355e", 343),
}
for name, (em, el) in rep_reg.items():
    p = os.path.join(M12, name)
    a, nl = nbytes_lines(p)
    am = md5f(p)
    check("R1 " + name, am == em and nl == el,
          "md5=%s(登记 %s) 行数=%d(登记 %d) 字节=%d" % (am, em, nl, el, a))

mfp = os.path.join(M12, "results/md5-manifest.txt")
mfm = md5f(mfp)
check("R1 md5-manifest.txt 自身 md5", mfm == "571fb2bb0a84d57418808108cdda4ce3", "实测 %s" % mfm)
mlines = open(mfp, encoding="utf-8").read().splitlines()
reg_line = [ln for ln in mlines if ln.endswith("route-1.md")]
# 清单里有两行 route-1.md（本轨一行、上游 70-research/cycle-1 一行）；materials 3.6 已登记
check("R1 md5-manifest 含 route-1.md 登记行恰两行（本轨+上游）", len(reg_line) == 2, repr(reg_line))
tgt = [ln for ln in reg_line if ln.endswith("m12/cycle-1/route-1.md")]
if tgt:
    parts = [x.strip() for x in tgt[0].split("|")]
    a1, nl1 = nbytes_lines(os.path.join(M12, "route-1.md"))
    check("R1 manifest 本轨行与实测一致", parts[0] == "939cc627c887fd4064214b14accfa651"
          and parts[1] == str(a1) and parts[2] == str(nl1),
          "manifest=%s vs 实测 939cc627.../%d/%d" % (tgt[0][:60], a1, nl1))
ups = [ln for ln in reg_line if ln.endswith("70-research/cycle-1/route-1.md")]
if ups:
    parts = [x.strip() for x in ups[0].split("|")]
    pu = os.path.join(R1, "route-1.md")
    au, nlu = nbytes_lines(pu)
    check("R1 manifest 上游行与实测一致", parts[0] == md5f(pu) and parts[1] == str(au) and parts[2] == str(nlu),
          "manifest=%s vs 实测 %s/%d/%d" % (ups[0][:60], md5f(pu), au, nlu))

print("=== R2 r2_j_A.txt 三项基线与伴随件 ===")
ja = os.path.join(R1, "scripts/results/verify-round2/r2_j_A.txt")
a, nl = nbytes_lines(ja)
check("R2 r2_j_A.txt 身份", md5f(ja) == "8f8d0112668a88d0811f30cefa396bd1" and nl == 16 and a == 1112,
      "md5=%s 行=%d 字节=%d（登记 8f8d0112.../16/1112）" % (md5f(ja), nl, a))
txt = open(ja, encoding="utf-8").read()
check("R2 基线一：C(21,10)=352716", ("子集总数 C(21,10) = 352716" in txt) and math.comb(21, 10) == 352716, "")
check("R2 基线二：10 个循环旋转 True 句在文本", "可行顶点数 = 10；与解析的 m2 = 10 个循环旋转相同 = True（解析集大小 10）" in txt, "")
check("R2 基线三：证书 [(10, 10)] 句在文本", "每个顶点的（活跃约束法向量秩，活跃约束条数）= [(10, 10)]" in txt, "")
# 基线二、三的机器复核：用 m2_10 检查点重算（在 R3 统一做），此处记录待办
jt = os.path.join(R1, "scripts/results/verify-round2/r2_j_A.time")
check("R2 r2_j_A.time 身份与内容", md5f(jt) == "440e8a872de8d71cacee663fab6536f3"
      and "real 62.49" in open(jt).read() and "user 61.78" in open(jt).read() and "sys 0.34" in open(jt).read(),
      "md5=%s 内容=%s" % (md5f(jt), open(jt).read().replace("\n", "; ")))
p = os.path.join(R1, "route-1.md")
a, nl = nbytes_lines(p)
check("R2 对照乙基线：cycle-1/route-1.md 457 行版", md5f(p) == "7be71b78cd4c582c67fa1b80c88d27e2" and nl == 457,
      "md5=%s 行=%d" % (md5f(p), nl))
p = os.path.join(R1, "scripts/results/r2_b_out.txt")
a, nl = nbytes_lines(p)
check("R2 对照丙基线：r2_b_out.txt", md5f(p) == "f3882451e5a45fc3cb5cce781f279e32" and nl == 136,
      "md5=%s 行=%d" % (md5f(p), nl))
for tag, rel, em in [("R2 r5_anchor_r2j_A_original.txt", "results/logs/r5_anchor_r2j_A_original.txt", "001c387eeaa62a2ebb5cd5f4d4517213"),
                     ("R2 repro-r2_j_A-m2-10.txt", "materials/repro-r2_j_A-m2-10.txt", "5d603d03a34ace5ad9107383d87fd0c1"),
                     ("R2 r5_full_m2_14_mpq_verdict.txt", "results/logs/r5_full_m2_14_mpq_verdict.txt", "1a1fbae0749f0f99584856b741ad3aea"),
                     ("R2 route3_bareiss_probe_out.txt", "results/route3_bareiss_probe_out.txt", "a9e90407f02fff8052e51b3cd5071251")]:
    p = os.path.join(M12, rel)
    am = md5f(p)
    check(tag, am == em, "md5=%s（登记 %s）" % (am, em))
t14 = open(os.path.join(M12, "results/logs/r5_full_m2_14_mpq.time")).read()
check("R2 r5_full_m2_14_mpq.time 内容（route-5:301 登记）",
      "real 2912.61" in t14 and "user 13328.89" in t14 and "sys 148.99" in t14, t14.replace("\n", "; "))

print("=== R3 检查点分片计数与顶点集计数关系 ===")
CK = [("m2_10_fraction", 10, 352716, 10), ("m2_10_mpq", 10, 352716, 10),
      ("m2_12_fraction", 12, 5200300, 12), ("m2_12_mpq", 12, 5200300, 12),
      ("m2_13_fraction", 13, 20058300, 13), ("m2_13_mpq", 13, 20058300, 13),
      ("m2_14_mpq", 14, 77558760, 14),
      ("smoke_m2_2", 2, 10, 3), ("smoke_m2_2_mpq", 2, 10, 3),
      ("smoke_m2_5", 5, 462, 5), ("smoke_m2_5_mpq", 5, 462, 5)]
ckdata = {}
for d, m2, etot, ekeys in CK:
    files, tot, nrd, ninf, sumcnt, keys, spans = load_ckpt(d)
    ckdata[d] = (files, tot, nrd, ninf, sumcnt, keys, spans, m2)
    spans_s = sorted(spans)
    tile = spans_s[0][0] == 0 and all(spans_s[i][1] == spans_s[i + 1][0] for i in range(len(spans_s) - 1)) and spans_s[-1][1] == tot
    comb = math.comb(2 * m2 + 1, m2)
    check("R3 %s 计数关系" % d,
          len(files) > 0 and tot == comb and etot == comb and nrd + ninf + sumcnt == tot and tile and len(keys) == ekeys,
          "片=%d 总=%d(组合 %d) nrd+ninf+Σ捕捉=%d+%d+%d=%d 铺满=%s 顶点=%d" % (
              len(files), tot, comb, nrd, ninf, sumcnt, nrd + ninf + sumcnt, tile, len(keys)))

ck10m = set(ckdata["m2_10_mpq"][5])
check("R3 m2_10 两引擎顶点集相等", set(ckdata["m2_10_fraction"][5]) == ck10m,
      "fraction=%d mpq=%d" % (len(ckdata["m2_10_fraction"][5]), len(ck10m)))
for a_, b_ in [("m2_12_fraction", "m2_12_mpq"), ("m2_13_fraction", "m2_13_mpq"), ("smoke_m2_2", "smoke_m2_2_mpq"), ("smoke_m2_5", "smoke_m2_5_mpq")]:
    check("R3 %s 与 %s 顶点集相等" % (a_, b_), set(ckdata[a_][5]) == set(ckdata[b_][5]), "")

# 基线二、三的机器复核（m2_10 阳性对照 + 证书）
ana10 = analytic_set(10, DELTA, W2000)
keys10 = {parse_point(k) for k in ck10m}
check("R2/R3 基线二机器复核：m2_10 顶点集 == 解析 10 旋转", keys10 == ana10, "|交集|=%d" % len(keys10 & ana10))
cert10 = sorted({my_certificate(y, 10, DELTA, W2000) for y in keys10})
check("R2/R3 基线三机器复核：m2_10 每顶点证书 == (10,10)", cert10 == [(10, 10)], "实测 %s" % cert10)

# 其余档解析集合与证书
for d, m2 in [("m2_12_mpq", 12), ("m2_13_mpq", 13), ("m2_14_mpq", 14)]:
    keys = {parse_point(k) for k in ckdata[d][5]}
    ana = analytic_set(m2, DELTA, W2000)
    certs = sorted({my_certificate(y, m2, DELTA, W2000) for y in keys})
    check("R3 %s 顶点集==解析族 且 证书=(m2,m2)" % d, keys == ana and certs == [(m2, m2)],
          "顶点=%d 交集=%d 证书=%s" % (len(keys), len(keys & ana), certs))
# 阴性对照：m2=2 顶集 != 解析族（判别力）
keys2 = {parse_point(k) for k in ckdata["smoke_m2_2"][5]}
ana2 = analytic_set(2, Fraction(3, 2), Fraction(3, 2))
check("R3 阴性对照 smoke_m2_2：顶集≠解析族（且解析族两点皆不在）", keys2 != ana2 and len(keys2 & ana2) == 0,
      "顶点=%s 解析=%s" % (sorted(str(t) for t in keys2), sorted(str(t) for t in ana2)))
# 边界档 m2=5：W 取阈值使 v=1，证书 (5,6)
W5 = (DELTA ** 5 - 1) / (DELTA - 1)
v5 = Fraction(W5) * (DELTA - 1) / (DELTA ** 5 - 1)
keys5 = {parse_point(k) for k in ckdata["smoke_m2_5"][5]}
ana5 = analytic_set(5, DELTA, W5)
cert5 = sorted({my_certificate(y, 5, DELTA, W5) for y in keys5})
check("R3 边界档 smoke_m2_5：v=1、顶集==解析族、证书=(5,6)", v5 == 1 and keys5 == ana5 and cert5 == [(5, 6)],
      "v=%s 证书=%s" % (v5, cert5))
# det_run1 与 det_run2 逐字节相同
f1 = os.path.join(M12, "results/ckpt/det_run1/chunk_0000.json")
f2 = os.path.join(M12, "results/ckpt/det_run2/chunk_0000.json")
check("R3 det_run1 与 det_run2 逐字节相同", open(f1, "rb").read() == open(f2, "rb").read(), "md5=%s/%s" % (md5f(f1), md5f(f2)))

# 分片规模声明核对（route-5:92 与 route-5:126）
f12 = os.path.join(M12, "results/logs/r5_full_m2_12_fraction.log")
cnt12 = [int(m.group(1)) for m in re.finditer(r"count=(\d+)", open(f12).read())]
check("R3 route-5:92 声明：m2_12 fraction 16 片、各 325019", len(cnt12) == 16 and cnt12[0] == 325018 and sum(cnt12) == 5200300,
      "首片=%d 分布=%s 和=%d（严格读法：首片 325018、其余 15 片 325019）" % (cnt12[0], sorted(set(cnt12)), sum(cnt12)))
f14 = os.path.join(M12, "results/logs/r5_full_m2_14_mpq.log")
cnt14 = [int(m.group(1)) for m in re.finditer(r"count=(\d+)", open(f14).read())]
check("R3 route-5:126 声明：m2_14 32 片 count 之和 = 77558760", len(cnt14) == 32 and sum(cnt14) == 77558760,
      "片=%d 和=%d" % (len(cnt14), sum(cnt14)))

print("=== R4 判串七份：md5、字节、直方图、F 位置 ===")
DEC = [("m5_e10_decisions.txt", "18e23746174db60150198149b00cd869", 462, (170, 262, 30)),
       ("c_m10_t8_decisions.txt", "b269256bfff877a81fa5a81047a4c958", 352716, (295780, 56926, 10)),
       ("c_m10_t1_decisions.txt", "b269256bfff877a81fa5a81047a4c958", 352716, (295780, 56926, 10)),
       ("py_m10_decisions.txt", "b269256bfff877a81fa5a81047a4c958", 352716, (295780, 56926, 10)),
       ("c_m12_t8_decisions.txt", "8fb4ba1aef28fdc293b52270985ec35e", 5200300, (4752735, 447553, 12)),
       ("c_m13_t8_decisions.txt", "152514f874a144554d1dff2ec0570da9", 20058300, (18811533, 1246754, 13)),
       ("c_m14_t8_decisions.txt", "37921d19726088fb8be115707a749356", 77558760, (74098262, 3460484, 14))]
decbytes = {}
for name, em, eb, ehist in DEC:
    p = os.path.join(M12, "scripts/results/route2", name)
    data = open(p, "rb").read()
    s, i, f = data.count(b"S"), data.count(b"I"), data.count(b"F")
    pos = [k for k, c in enumerate(data) if c == 70]
    contig = len(pos) > 0 and pos == list(range(pos[0], pos[0] + len(pos)))
    check("R4 %s" % name, md5f(p) == em and len(data) == eb and (s, i, f) == ehist,
          "md5=%s 字节=%d 直方图=%s(登记 %s) F 位置=%d..%d 连续=%s" % (md5f(p), len(data), (s, i, f), ehist, pos[0], pos[-1], contig))
    decbytes[name] = data
    if name == "m5_e10_decisions.txt":
        check("R4 m5 F 首末", pos[0] == 195 and pos[-1] == 461 and not contig, "首=%d 末=%d 连续=%s" % (pos[0], pos[-1], contig))
    else:
        m2 = {"c_m10_t8_decisions.txt": 10, "c_m12_t8_decisions.txt": 12, "c_m13_t8_decisions.txt": 13, "c_m14_t8_decisions.txt": 14}
        if name in m2:
            check("R4 %s F 位置=末 m2 个连续" % name, contig and pos[0] == len(data) - m2[name], "")

print("=== R4b 七段 Python 切片与 C 判串逐字节相等 ===")
SL = [("py_m12_slice_a.txt", "3fc7cb4298234a9a35157a67468cdabb", "c_m12_t8_decisions.txt", 0, 60000),
      ("py_m12_slice_b.txt", "01d48b64c306fcda9abf601a1cee60da", "c_m12_t8_decisions.txt", 2570000, 2630000),
      ("py_m12_slice_c.txt", "6ed10684ab1144eed0718d983ebbac7b", "c_m12_t8_decisions.txt", 5140000, 5200300),
      ("py_m13_slice_a.txt", "b3a1a41dab9edab79470d174440fdded", "c_m13_t8_decisions.txt", 0, 60000),
      ("py_m13_slice_b.txt", "0df416d6afade99f69e439cae879c482", "c_m13_t8_decisions.txt", 20000000, 20058300),
      ("py_m14_slice_a.txt", "aed2dfe579abcd7927c87672ecdf53fb", "c_m14_t8_decisions.txt", 0, 40000),
      ("py_m14_slice_b.txt", "032e82bc5fca23d1804ff270e4e4b963", "c_m14_t8_decisions.txt", 77400000, 77558760)]
for name, em, cname, lo, hi in SL:
    p = os.path.join(M12, "scripts/results/route2", name)
    data = open(p, "rb").read()
    cdata = decbytes[cname]
    ok = md5f(p) == em and len(data) == hi - lo and cdata[lo:hi] == data
    note = "md5=%s 长=%d 区间[%d,%d)相等=%s" % (md5f(p), len(data), lo, hi, cdata[lo:hi] == data)
    if not ok:
        off = cdata.find(data[:2000])
        note += "；改搜索命中偏移=%d" % off
    check("R4b %s" % name, ok, note)

print("=== R5 SUMMARY_JSON 七份与判定六行对称 diff ===")
LOGREG = {"r5_full_m2_10_fraction.log": ("f91223df69d325438fa00751f7d0a61b", None, None),
          "r5_full_m2_10_mpq.log": ("ed4807b53a6834dc2143ccc8335e01d4", None, None),
          "r5_full_m2_12_fraction.log": ("0b286172e8385be71c5573c5f7d1a2b9", None, None),
          "r5_full_m2_12_mpq.log": ("eb16f9e78762849af99b195bd219db8d", 122.89, 690.07),
          "r5_full_m2_13_mpq.log": ("b29117e845961ba98c54563a33221b8c", 516.4, 2923.4),
          "r5_full_m2_13_fraction.log": ("a0c5f7fbf687adc232d9c1e5885a7d89", 3513.5, 14040.7),
          "r5_full_m2_14_mpq.log": ("5b13b01b441209cc4a7f6f664f96779a", 2912.2, 13477.7)}
summ = {}
for name, (em, ew, ec) in LOGREG.items():
    p = os.path.join(M12, "results/logs", name)
    txt = open(p, encoding="utf-8").read()
    m = re.search(r"SUMMARY_JSON (\{.*\})", txt)
    d = json.loads(m.group(1))
    summ[name] = d
    m2 = d["m2"]
    arith = d["total"] == math.comb(2 * m2 + 1, m2) and d["processed"] == d["total"] \
        and d["n_rank_def"] + d["n_infeasible"] + d["n_feasible_subsets"] == d["total"] \
        and d["equal"] is True and d["certs"] == [[m2, m2]] and d["n_distinct_feasible"] == m2
    wc_ok = True
    if ew is not None:
        wc_ok = abs(d["wall_s"] - ew) < 0.11 and abs(d["cpu_s"] - ec) < 0.11
    check("R5 %s md5 与字段" % name, md5f(p) == em and arith and wc_ok,
          "md5=%s(登记 %s) total=%d wall=%.2f(报告 %s) cpu=%.2f(报告 %s)" % (md5f(p), em, d["total"], d["wall_s"], ew, d["cpu_s"], ec))
# 检查点 nrd/ninf 与 SUMMARY 一致
for d_ck, name in [("m2_10_mpq", "r5_full_m2_10_mpq.log"), ("m2_12_mpq", "r5_full_m2_12_mpq.log"),
                   ("m2_13_mpq", "r5_full_m2_13_mpq.log"), ("m2_14_mpq", "r5_full_m2_14_mpq.log")]:
    f_, tot, nrd, ninf, sumcnt, keys, spans, m2 = ckdata[d_ck]
    s = summ[name]
    check("R5 %s 检查点分检计数与 SUMMARY 一致" % d_ck, (nrd, ninf, sumcnt) == (s["n_rank_def"], s["n_infeasible"], s["n_feasible_subsets"]),
          "检查点 %d/%d/%d vs 日志 %d/%d/%d" % (nrd, ninf, sumcnt, s["n_rank_def"], s["n_infeasible"], s["n_feasible_subsets"]))

LINES_KEEP = ("子集总数", "已处理", "分检：", "可行顶点数", "每个顶点的", "每个可行解被活跃子集捕捉", "独立性：本段只用")
def keep_lines(p):
    out = []
    for ln in open(p, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if any(k in ln for k in LINES_KEEP):
            out.append(ln)
    return out
for fa, fb, tag in [("r5_full_m2_12_fraction.log", "r5_full_m2_12_mpq.log", "m2_12"),
                    ("r5_full_m2_13_fraction.log", "r5_full_m2_13_mpq.log", "m2_13")]:
    la = keep_lines(os.path.join(M12, "results/logs", fa))
    lb = keep_lines(os.path.join(M12, "results/logs", fb))
    same = la == lb
    check("R5 %s fraction/mpq 判定六行对称 diff 零差异" % tag, same,
          "fraction %d 行 vs mpq %d 行；相同=%s" % (len(la), len(lb), same))
    if not same:
        for x, y in zip(la, lb):
            if x != y:
                print("   DIFF: %r  <> %r" % (x, y))

print("=== R6 两实现 JSON 键差、agg 相等、顶点坐标相等 ===")
PJ = {}
for name in ["route3_impl1_m10.json", "route3_impl2_m10.json", "route3_impl1_m12.json", "route3_impl2_m12.json",
             "route3_impl2_m10_deltahi.json", "route3_impl2_m12_deltahi.json", "route3_impl2_m13.json", "route3_impl2_m14.json"]:
    PJ[name] = json.load(open(os.path.join(M12, "results", name)))
ka1, ka2 = set(PJ["route3_impl1_m12.json"]), set(PJ["route3_impl2_m12.json"])
check("R6 m2_12 顶层键差", (ka1 - ka2, ka2 - ka1) == ({"n_infeasible_unique", "n_singular"}, {"candidates_with_wrong_rank"}),
      "impl1 独有 %s；impl2 独有 %s" % (sorted(ka1 - ka2), sorted(ka2 - ka1)))
kb1, kb2 = set(PJ["route3_impl1_m10.json"]), set(PJ["route3_impl2_m10.json"])
check("R6 m2_10 顶层键差同行", (kb1 - kb2, kb2 - kb1) == ({"n_infeasible_unique", "n_singular"}, {"candidates_with_wrong_rank"}),
      "impl1 独有 %s；impl2 独有 %s" % (sorted(kb1 - kb2), sorted(kb2 - kb1)))
JREG = {"route3_impl1_m10.json": "c9c77768e5eda8006db969299187ad02", "route3_impl2_m10.json": "c711aeac30d711c90e11b085992f2146",
        "route3_impl1_m12.json": "ae707bd3ff64907a29873421f6dc423b", "route3_impl2_m12.json": "658a5bcaae56eafd4ffd30f451aa857f",
        "route3_impl2_m10_deltahi.json": "2ecc539057d68efc9647f19693688da7", "route3_impl2_m12_deltahi.json": "eebc3d9b17f5c5739b8d7b1d47e83189",
        "route3_impl2_m13.json": "edf1593c32b08cadea1dcdb449179a9e", "route3_impl2_m14.json": "91fb541d8769f905dfac63f70048886d"}
for name, em in JREG.items():
    p = os.path.join(M12, "results", name)
    check("R6 %s md5" % name, md5f(p) == em, "md5=%s（route-3 9.2 登记 %s）" % (md5f(p), em))
for tag, a, b in [("m2_10", "route3_impl1_m10.json", "route3_impl2_m10.json"),
                  ("m2_12", "route3_impl1_m12.json", "route3_impl2_m12.json")]:
    A, B = PJ[a], PJ[b]
    pa = {parse_point(x) for x in A["candidate_points_sorted"]}
    pb = {parse_point(x) for x in B["candidate_points_sorted"]}
    check("R6 %s agg 相等与顶点坐标集合相等" % tag, A["agg"] == B["agg"] and pa == pb and len(pa) == len(pb),
          "agg=%s/%s 点数=%d/%d 集合相等=%s" % (A["agg"], B["agg"], len(pa), len(pb), pa == pb))
    check("R6 %s 计数三项与总数" % tag, A["n_singular"] + A["n_infeasible_unique"] + A["n_candidate_subsets"] == A["total_subsets"],
          "impl1 %d+%d+%d=%d" % (A["n_singular"], A["n_infeasible_unique"], A["n_candidate_subsets"], A["total_subsets"]))
# impl2 逐档与检查点顶点集相等
XREG = {"route3_xcheck_m10_compare.json": "c3a46ab09d5cb00552709bf9b6c52853",
        "route3_xcheck_m12_compare.json": "7cd74fe6650fc13d43a7e7f7a0ebe266",
        "route3_xcheck_m10_allsubsets.json": "2b6211cf5ad8195f7e8831470c56fa76",
        "route3_xcheck_m12_allsubsets.json": "19f78a95f64a3b06a6444647acbb86e8",
        "route3_vs_other_m12.json": "47d3defdc75af9587f8e7f9604d1b022",
        "route3_vs_other_m12_impl1.json": "a807588f45abd109a646c98c073c01f2",
        "route3_vs_other_m13.json": "4e851bc7a40c873bf3e1ca6e14317bf9",
        "route3_vs_other_m14.json": "adb1d0a97a4542ea80d55db1666a2a88"}
for name, em in XREG.items():
    p = os.path.join(M12, "results", name)
    check("R6 %s md5" % name, md5f(p) == em, "md5=%s（route-3 9.2 登记 %s）" % (md5f(p), em))
cm = json.load(open(os.path.join(M12, "results/route3_xcheck_m12_compare.json")))
check("R6 xcheck_m12_compare 字段", cm["agg_equal"] and cm["candidate_point_sets_equal"] and cm["candidate_ranks_equal"]
      and cm["active_count_equal"] and cm["n_blocks_a"] == cm["n_blocks_b"] == 21 and cm["n_blocks_with_agg_mismatch"] == 0,
      "agg_equal=%s pts=%s ranks=%s act=%s blocks=%d/%d mismatch=%d" % (cm["agg_equal"], cm["candidate_point_sets_equal"],
      cm["candidate_ranks_equal"], cm["active_count_equal"], cm["n_blocks_a"], cm["n_blocks_b"], cm["n_blocks_with_agg_mismatch"]))
ranks12 = sorted(c["rank"] for c in PJ["route3_impl1_m12.json"]["candidates"])
check("R6 m2_12 候选编号=末 12 个", ranks12 == list(range(5200288, 5200300)), "%s" % ranks12)
for tag, name, d_ck in [("m2_12 impl1 vs ckpt", "route3_impl1_m12.json", "m2_12_mpq"), ("m2_12 impl2 vs ckpt", "route3_impl2_m12.json", "m2_12_mpq"),
                        ("m2_10 impl1 vs ckpt", "route3_impl1_m10.json", "m2_10_mpq"), ("m2_10 impl2 vs ckpt", "route3_impl2_m10.json", "m2_10_mpq"),
                        ("m2_13 impl2 vs ckpt", "route3_impl2_m13.json", "m2_13_mpq"), ("m2_14 impl2 vs ckpt", "route3_impl2_m14.json", "m2_14_mpq")]:
    pa = {parse_point(x) for x in PJ[name]["candidate_points_sorted"]}
    pb = {parse_point(k) for k in ckdata[d_ck][5]}
    check("R6 %s 顶点坐标集合相等" % tag, pa == pb, "点数 %d vs %d" % (len(pa), len(pb)))

print("=== R7 0 字节伴随日志 ===")
zeros = sorted(p for p in glob.glob(M12 + "/results/**", recursive=True)
               if os.path.isfile(p) and os.path.getsize(p) == 0 and ".mimosa" not in p)
rel = [os.path.relpath(p, M12) for p in zeros]
exp = ["results/alive-probe-1.txt", "results/route3_xcheck_m10_allsubsets.log", "results/route3_xcheck_m12_allsubsets.log"]
check("R7 0 字节文件恰为登记的三个", rel == exp, "实测 %s" % rel)

print("=== R8 脚本身份（route-3 9.1 与 route-5 5.3 登记） ===")
SREG = [("scripts/route3_defs.py", "088d08bff5065cb58a2b9decd48b2437", 274),
        ("scripts/route3_impl1_mpqscan.py", "3f0035b17c0b601b37ec1c2e8502298a", 275),
        ("scripts/route3_impl2_struct.py", "b641f2805dcf90379d954cb2dc9a1b9d", 318),
        ("scripts/route3_xcheck.py", "c63dd6db26951411d06a2649a9d1404b", 142),
        ("scripts/route3_verify.py", "dd73d5b742b5a40df439e35281651999", 150),
        ("scripts/route3_vs_other_compare.py", "43d70b1cc4e7382eff5833882b1cb6e7", 84),
        ("scripts/route3_bareiss_probe.py", "fc73afa8d6a1967bfeb95a9c369bda73", 114),
        ("scripts/route3_impl1_intscan.py", "f7e5603bd634267ff22b9db0395c339e", 316),
        ("scripts/r5_vm12_enum.py", "4fd20e6737c51dda3e88e2f6c0ca2345", None),
        ("scripts/frozen/r2_common.py", "cfee819667c0883e73732f03d2dc8bef", 244),
        ("scripts/frozen/r2_j_independent_vertices.py", "4b8ce2a500d8ca9021fd0178deca637e", 272)]
for relp, em, el in SREG:
    p = os.path.join(M12, relp)
    am = md5f(p)
    a, nl = nbytes_lines(p)
    check("R8 " + relp, am == em and (el is None or nl == el), "md5=%s(登记 %s) 行=%d(登记 %s)" % (am, em, nl, el))

print("=== R9 行号引用抽查（登记行号 -> 现行内容是否命中） ===")
LINES = [("route-1.md", 13, "31 项检查全部 PASS"),
         ("route-1.md", 46, "8f8d0112668a88d0811f30cefa396bd1"),
         ("route-2.md", 130, "b269256bfff877a81fa5a81047a4c958"),
         ("route-2.md", 192, "8fb4ba1aef28fdc293b52270985ec35e"),
         ("route-2.md", 362, "152514f874a144554d1dff2ec0570da9"),
         ("route-2.md", 363, "37921d19726088fb8be115707a749356"),
         ("route-3.md", 191, '"n_mismatch": 0'),
         ("route-3.md", 195, "不是抽样断言，而是逐项核对过的"),
         ("route-3.md", 227, "m₂ ≥ 15 未跑"),
         ("route-3.md", 333, "19f78a95f64a3b06a6444647acbb86e8"),
         ("route-4.md", 6, "不执行"),
         ("route-5.md", 100, "已读到 m₂ = 14 的全量判定为真"),
         ("route-5.md", 100, "的表述作废"),
         ("route-5.md", 108, "判定为真"),
         ("route-5.md", 115, "判定为真"),
         ("route-5.md", 121, "判定为真"),
         ("route-5.md", 301, "5b13b01b441209cc4a7f6f664f96779a"),
         ("route-5.md", 343, "2912.2")]
for name, ln, sub in LINES:
    lines = open(os.path.join(M12, name), encoding="utf-8").read().splitlines()
    ok = 1 <= ln <= len(lines) and sub in lines[ln - 1]
    check("R9 %s:%d 含 %s" % (name, ln, sub), ok,
          "" if ok else "实文=%r" % (lines[ln - 1][:90] if ln <= len(lines) else None))

print("")
print("FAIL 总数 = %d" % NFAIL)
sys.exit(0 if NFAIL == 0 else 1)
