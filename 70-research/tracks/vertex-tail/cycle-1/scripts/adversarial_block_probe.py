#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""adversarial_block_probe.py —— vertex-tail 路线三对抗复核的抽点抽块重算（只读）。

不重跑任何全量枚举。三件事：

  P1 抽块重算：对 m2 = 10、12、13、14 各取一段连续子集区间（200 至 300 个），
     用本脚本自写的 lex unrank、Fraction 高斯消元与可行性判定，逐子集重新分类为
     S（无唯一解）/ I（唯一解但不可行）/ F（可行），与 C 判串（route2 目录）同下标
     字节逐位比较；F 行的解向量另与解析族与检查点顶点集比对。
  P2 抽点还原：对每个检查点目录取两个顶点各自的头一条捕捉子集（checkpoint 里
     feasible[键]["examples"][0] 的 5/10/12/13/14 元组），重解并核对解 == 该键。
  P3 类别盲区实证：直接按 route3_xcheck.py:48 至 :54 的口径对两实现抽块（m2 = 10、12
     各 20 个子集）逐项跑，统计 (p1==p2 and c1==c2) 的通过数与 kind（k1 vs k2）的
     差异数，展示「零不一致」在实际判据下对 kind 不可见。

输出落 stdout；本脚本与 m12 轨道产物只读交互。退出码 0 表示 P1、P2 全对（P3 只如实统计）。
"""
import itertools
import json
import math
import os
import sys
from fractions import Fraction

M12 = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/vertex-m12/cycle-1"
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


# ---------- 自写组合字典序 unrank（与 itertools.combinations 同序的自检在下方） ----------

def comb_unrank(n, r, k):
    c = []
    a = 0
    x = k
    for i in range(r):
        for cand in range(a, n):
            cnt = math.comb(n - cand - 1, r - i - 1)
            if x < cnt:
                c.append(cand)
                a = cand + 1
                break
            x -= cnt
    return c


_all = list(itertools.combinations(range(7), 3))
check("P0 自写 unrank 与 itertools 全空间一致（n=7,r=3）",
      all(tuple(comb_unrank(7, 3, k)) == _all[k] for k in range(35)), "35 个组合")

# ---------- 自写约束表与精确求解 ----------

def my_rows(m2, delta, W):
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


CONS = {m2: my_rows(m2, DELTA, W2000) for m2 in (10, 12, 13, 14)}
CONS2 = {5: my_rows(5, DELTA, (DELTA ** 5 - 1) / (DELTA - 1)),
         2: my_rows(2, Fraction(3, 2), Fraction(3, 2))}


def solve_unique(rows, rhs, n):
    """Fraction 高斯约当；无唯一解（秩亏）返回 None。"""
    M = [[Fraction(rows[i][j]) for j in range(n)] + [Fraction(rhs[i])] for i in range(n)]
    rank = 0
    where = [-1] * n
    for col in range(n):
        piv = None
        for i in range(rank, n):
            if M[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        pv = M[rank][col]
        M[rank] = [x / pv for x in M[rank]]
        for i in range(n):
            if i != rank and M[i][col] != 0:
                f = M[i][col]
                M[i] = [M[i][j] - f * M[rank][j] for j in range(n + 1)]
        where[col] = rank
        rank += 1
        if rank == n:
            break
    if rank < n:
        return None
    y = [Fraction(0)] * n
    for j in range(n):
        y[j] = M[where[j]][n]
    return tuple(y)


def classify(St, m2, cons, delta, W):
    rows = [cons[s][0] for s in St]
    rhs = [cons[s][1] for s in St]
    y = solve_unique(rows, rhs, m2)
    if y is None:
        return "S", None
    if any(y[j] < 1 for j in range(m2)):
        return "I", None
    if any(y[(j + 1) % m2] > delta * y[j] for j in range(m2)):
        return "I", None
    if sum(y) < W:
        return "I", None
    return "F", y


def analytic_set(m2, delta, W):
    v = Fraction(W) * (delta - 1) / (delta ** m2 - 1)
    return {tuple(v * delta ** ((j + r) % m2) for j in range(m2)) for r in range(m2)}


# ---------- P1 抽块重算 ----------

print("=== P1 抽块重算（自写 unrank、自写精确消元、逐字节对 C 判串） ===")
def load_dec(name):
    return open(os.path.join(M12, "scripts/results/route2", name), "rb").read()


def ckpt_keys(d):
    keys = {}
    for f in sorted(os.listdir(os.path.join(M12, "results/ckpt", d))):
        if f.endswith(".json"):
            j = json.load(open(os.path.join(M12, "results/ckpt", d, f)))
            keys.update(j["feasible"])
    return keys


BLOCKS = [
    (10, "c_m10_t8_decisions.txt", "m2_10_mpq", 352416, 352716),
    (12, "c_m12_t8_decisions.txt", "m2_12_mpq", 2570000, 2570300),
    (12, "c_m12_t8_decisions.txt", "m2_12_mpq", 5200000, 5200300),
    (13, "c_m13_t8_decisions.txt", "m2_13_mpq", 20058000, 20058300),
    (14, "c_m14_t8_decisions.txt", "m2_14_mpq", 77558460, 77558760),
]
ana = {m2: analytic_set(m2, DELTA, W2000) for m2 in (10, 12, 13, 14)}
for m2, decname, ckname, lo, hi in BLOCKS:
    data = load_dec(decname)
    cons = CONS[m2]
    bad = []
    dist = {"S": 0, "I": 0, "F": 0}
    fpts = []
    for k in range(lo, hi):
        St = comb_unrank(2 * m2 + 1, m2, k)
        ch, y = classify(St, m2, cons, DELTA, W2000)
        dist[ch] += 1
        rec = chr(data[k])
        if ch != rec:
            bad.append((k, ch, rec))
        if ch == "F":
            fpts.append((k, y))
    v_ok = all(y in ana[m2] for _, y in fpts)
    ck = {tuple(Fraction(x) for x in kk.split(",")) for kk in ckpt_keys(ckname)}
    v_ck = all(y in ck for _, y in fpts)
    check("P1 m2=%d [%d,%d) 逐字节零不一致" % (m2, lo, hi),
          len(bad) == 0, "子集=%d 分布=%s 不一致=%d %s" % (hi - lo, dist, len(bad), bad[:3]))
    if fpts:
        check("P1 m2=%d 块内 F 解在解析族且在各检查点顶点集" % m2, v_ok and v_ck,
              "F 个数=%d 解析族内=%s 检查点内=%s" % (len(fpts), v_ok, v_ck))
    else:
        info("P1 m2=%d 块内无 F（纯 S/I 块）" % m2, "分布=%s" % dist)

# F 区专项：m2=12 末尾 12 个 F 的下标与顶点一一对应
data12 = load_dec("c_m12_t8_decisions.txt")
tail = list(range(5200288, 5200300))
tail_pts = []
for k in tail:
    St = comb_unrank(25, 12, k)
    ch, y = classify(St, 12, CONS[12], DELTA, W2000)
    tail_pts.append((k, ch, y))
check("P1 m2=12 末 12 个下标全为 F 且顶点两两不同、覆盖 12 顶点集",
      all(ch == "F" for _, ch, _ in tail_pts)
      and len({y for _, _, y in tail_pts}) == 12
      and {y for _, _, y in tail_pts} == ana[12],
      "F 数=%d 去重=%d" % (sum(1 for _, ch, _ in tail_pts if ch == "F"), len({y for _, _, y in tail_pts})))

# ---------- P2 抽点还原：检查点头一条捕捉子集重解 ----------

print("=== P2 抽点还原（每个检查点目录取 2 个顶点的头一条捕捉子集重解） ===")
P2DIRS = [("m2_10_mpq", 10, DELTA, W2000, CONS[10]), ("m2_12_mpq", 12, DELTA, W2000, CONS[12]),
          ("m2_13_mpq", 13, DELTA, W2000, CONS[13]), ("m2_14_mpq", 14, DELTA, W2000, CONS[14]),
          ("smoke_m2_2", 2, Fraction(3, 2), Fraction(3, 2), CONS2[2]),
          ("smoke_m2_5", 5, DELTA, (DELTA ** 5 - 1) / (DELTA - 1), CONS2[5])]
ntot = 0
for d, m2, delta, W, cons in P2DIRS:
    keys = ckpt_keys(d)
    cnt = 0
    for kk, rec in list(keys.items())[: len(keys)]:
        if cnt >= 2:
            break
        ex = rec["examples"][0]
        ch, y = classify(tuple(ex), m2, cons, delta, W)
        key = tuple(Fraction(x) for x in kk.split(","))
        if ch == "F" and y == key:
            cnt += 1
        else:
            check("P2 %s 捕捉子集还原" % d, False, "例 %s -> %s %s vs 键 %s" % (ex, ch, y, key))
    check("P2 %s 两顶点捕捉子集还原为真" % d, cnt >= min(2, len(keys)), "已核 %d 例" % cnt)
    ntot += cnt
info("P2 合计", "已核 %d 个（顶点, 捕捉子集）配对" % ntot)

# ---------- P3 类别盲区实证 ----------

print("=== P3 类别盲区实证（按 route3_xcheck.py:54 的实战判据抽块） ===")
sys.path.insert(0, os.path.join(M12, "scripts"))
import route3_defs as RD          # noqa: E402
import route3_impl1_mpqscan as I1  # noqa: E402
import route3_impl2_struct as I2   # noqa: E402

delta = RD.delta_lo(verify=False)
Wf = RD.W_FROZEN
p, q = delta.numerator, delta.denominator
wn, wd = Wf.numerator, Wf.denominator
for m2, lo, hi in [(10, 352696, 352716), (12, 2570000, 2570020)]:
    cons = RD.constraint_rows(m2, delta, Wf)
    pmq = I1.mpq(p)
    qmq = I1.mpq(q)
    dpow = [delta ** k for k in range(-m2, m2 + 1)]
    n_ok = 0
    n_kind_diff = 0
    kinds1 = {}
    kinds2 = {}
    examples = []
    data = load_dec("c_m10_t8_decisions.txt" if m2 == 10 else "c_m12_t8_decisions.txt")
    for rank in range(lo, hi):
        St = tuple(comb_unrank(2 * m2 + 1, m2, rank))
        k1, c1, p1, a1 = I1.judge_subset(St, cons, m2, pmq, qmq, I1.mpq(wn), I1.mpq(wd))
        k2, c2, p2, a2, _fr = I2.judge_struct(St, m2, dpow, p, q, wn, wd, None)
        kinds1[k1] = kinds1.get(k1, 0) + 1
        kinds2[k2] = kinds2.get(k2, 0) + 1
        if (p1 == p2) and (c1 == c2):
            n_ok += 1
        if k1 != k2:
            n_kind_diff += 1
        if len(examples) < 3 and k1 != k2:
            examples.append((rank, chr(data[rank]), k1, k2, (p1 == p2) and (c1 == c2)))
    check("P3 m2=%d [%d,%d) 实战判据全通过" % (m2, lo, hi), n_ok == hi - lo,
          "通过=%d/%d kind 不同但判据通过=%d" % (n_ok, hi - lo, n_kind_diff))
    info("P3 m2=%d 类别分布" % m2, "impl1=%s impl2=%s" % (kinds1, kinds2))
    for ex in examples:
        info("P3 例", "rank=%d 判串字节=%s k1=%s k2=%s 判据通过=%s" % ex)

print("")
print("P1/P2 FAIL 总数 = %d" % NFAIL)
sys.exit(0 if NFAIL == 0 else 1)
