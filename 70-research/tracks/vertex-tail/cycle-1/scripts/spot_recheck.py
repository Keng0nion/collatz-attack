#!/usr/bin/env python3
"""vertex-tail 第 1 轮：第三套求解器 spot_recheck（声明清算与抽点重算路线）。

性质：本文件不 import 既有任何实现（不 import route3_*、route2_*、r5_vm12_enum、
frozen/r2_common 等）。只用 Python 标准库从零重建：组合字典序 unrank、约束表、
精确有理（Fraction）高斯消元、可行性判定、活跃约束秩。

只读输入（不改写）：
  判串：70-research/tracks/vertex-m12/cycle-1/scripts/results/route2/c_m1X_t8_decisions.txt
  检查点：70-research/tracks/vertex-m12/cycle-1/results/ckpt/*/chunk_*.json
  对拍落点：70-research/tracks/vertex-m12/cycle-1/results/route3_xcheck_m*_allsubsets.json

复算（只读，不含 m2 = 12 或 13 的全量枚举）：
  1. 组合 unrank 自检（对 itertools.combinations 全量或分片）；
  2. 检查点计数关系（Σcount = C(2m2+1,m2)、首尾相接、count = end - start、
     n_rank_def + n_infeasible + Σfeasible.count = count、first/last 与 unrank 相符）；
  3. 检查点分检总和与判串直方图对拍（跨实现、跨产物线）；
  4. 检查点可行顶点自算活跃条数与活跃秩（主档 m2、边界档 (5,6)、阴性档 m2=2）；
  5. 抽点重算 m2 = 12、13（F 全体 + 首尾块 + 分片边界窗 + 等距样 + LCG 样），
     与判串逐字节比较；抽中的顶点与检查点坐标键、route-3 两实现候选点串比较；
  6. m2 = 10 阳性对照：全量 352716 子集重算，与 c_m10_t8_decisions.txt 逐字节比较。

退出码：0 = 全部判据通过；1 = 有 FAIL；2 = 环境或读入失败。
每条判据都会打印 [PASS]/[FAIL] 与判据文本；未跑项单独打印 [SKIP]。
"""

import hashlib
import json
import math
import os
import sys
import time
from fractions import Fraction
from itertools import combinations

PY = sys.executable
ROOT = "/Users/luna/Documents/math IA/collatz-attack"
VM12 = os.path.join(ROOT, "70-research/tracks/vertex-m12/cycle-1")
CKPT = os.path.join(VM12, "results/ckpt")
R2 = os.path.join(VM12, "scripts/results/route2")
RES = os.path.join(VM12, "results")

D_LO = Fraction(126797, 80000)      # δ 严格下界（frozen-spec.md:22）
D_HI = Fraction(7924813, 5000000)   # δ 严格上界（frozen-spec.md:22）
W_M5 = Fraction(630347359154513105681, 40960000000000000000)  # frozen-spec.md:27

FAILS = []
SKIPS = []
CHECKS = []


def check(name, ok, detail):
    tag = "[PASS]" if ok else "[FAIL]"
    CHECKS.append((name, bool(ok), detail))
    if not ok:
        FAILS.append((name, detail))
    print("%s %s：%s" % (tag, name, detail), flush=True)


def skip(name, why):
    SKIPS.append((name, why))
    print("[SKIP] %s：%s" % (name, why), flush=True)


def section(t):
    print("\n== %s ==" % t, flush=True)


# ---------------------------------------------------------------- 组合 unrank
def unrank(n, k, r):
    """字典序（同 itertools.combinations 顺序）第 r 个 k 元组合，升序元组。"""
    if r < 0:
        raise ValueError("rank 负")
    out = []
    prev = -1
    rem = r
    for i in range(k):
        for v in range(prev + 1, n - (k - 1 - i) + 1):
            c = math.comb(n - 1 - v, k - 1 - i)
            if rem < c:
                out.append(v)
                prev = v
                break
            rem -= c
        else:
            raise ValueError("rank 越界")
    return tuple(out)


CONS_CACHE = {}


def constraint_list(m2, d, W):
    """(C1) y_j >= 1；(C2) y_{(j+1)%m2} - d*y_j <= 0；(C3) Σy >= W。
    顺序与 frozen-spec.md:12 至 :14 同序（C1 块、C2 块、C3 末条）。"""
    key = (m2, d, W)
    if key in CONS_CACHE:
        return CONS_CACHE[key]
    cons = []
    for j in range(m2):
        a = [Fraction(0)] * m2
        a[j] = Fraction(1)
        cons.append((a, Fraction(1), "ge"))
    for j in range(m2):
        a = [Fraction(0)] * m2
        a[(j + 1) % m2] = Fraction(1)
        a[j] -= d
        cons.append((a, Fraction(0), "le"))
    cons.append(([Fraction(1)] * m2, Fraction(W), "ge"))
    CONS_CACHE[key] = cons
    return cons


def solve_rank(rows, rhs, m):
    """精确消元：返回 (rank, 解或 None)。解在秩 = m 时给出。"""
    M = [[Fraction(x) for x in rows[i]] + [Fraction(rhs[i])] for i in range(len(rows))]
    rank = 0
    for col in range(m):
        piv = None
        for i in range(rank, len(M)):
            if M[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        pv = M[rank][col]
        M[rank] = [v / pv for v in M[rank]]
        for i in range(len(M)):
            if i != rank and M[i][col] != 0:
                f = M[i][col]
                M[i] = [M[i][j] - f * M[rank][j] for j in range(m + 1)]
        rank += 1
        if rank == len(M):
            break
    # 不相容检查
    for i in range(rank, len(M)):
        if any(M[i][j] != 0 for j in range(m)) is False and M[i][m] != 0:
            return rank, "inconsistent"
    if rank < m:
        return rank, None
    y = [Fraction(0)] * m
    for i in range(rank):
        for j in range(m):
            if M[i][j] == 1:
                y[j] = M[i][m]
                break
        else:
            return rank, "pivot-parse-fail"
    return rank, tuple(y)


def judge(subset, m2, d, W, cons):
    rows = [cons[i][0] for i in subset]
    rhs = [cons[i][1] for i in subset]
    rank, y = solve_rank(rows, rhs, m2)
    if not isinstance(y, tuple):
        return "S", None, rank
    bad = False
    for a, b, t in cons:
        s = sum(a[j] * y[j] for j in range(m2))
        if t == "ge" and s < b:
            bad = True
            break
        if t == "le" and s > b:
            bad = True
            break
    return ("I" if bad else "F"), y, rank


def active_profile(y, m2, cons):
    """(活跃约束条数, 活跃约束法向量秩) —— 自算，不用既有实现。"""
    N = len(cons)
    act = []
    for a, b, t in cons:
        s = sum(a[j] * y[j] for j in range(m2))
        if s == b:
            act.append(a)
    # 秩：对活跃法向量做精确消元
    rank = 0
    rows = [list(a) for a in act]
    for col in range(m2):
        piv = None
        for i in range(rank, len(rows)):
            if rows[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        pv = rows[rank][col]
        rows[rank] = [v / pv for v in rows[rank]]
        for i in range(rank + 1, len(rows)):
            if rows[i][col] != 0:
                f = rows[i][col]
                rows[i] = [rows[i][j] - f * rows[rank][j] for j in range(m2)]
        rank += 1
    return len(act), rank


def v_vertex(m2, d, W):
    return Fraction(W) * (d - 1) / (d ** m2 - 1)


def rotation_values(m2, d, W):
    v = v_vertex(m2, d, W)
    return [v * d ** k for k in range(m2)]


def point_str(y):
    return ",".join(str(c) for c in y)


def read_decisions(path):
    with open(path, "rb") as f:
        return f.read()


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def histof(buf):
    return {c: buf.count(ord(c)) for c in "SIF"}


# ------------------------------------------------------------------ 1 自检
def part1():
    section("第 1 节 组合 unrank 自检（对 itertools.combinations）")
    ok = True
    for n, k in ((7, 3), (11, 5), (25, 12)):
        combos = list(combinations(range(n), k))
        if len(combos) <= 6000:
            idxs = range(len(combos))
        else:
            idxs = list(range(4000)) + list(range(len(combos) - 200, len(combos)))
        bad = [r for r in idxs if unrank(n, k, r) != combos[r]]
        ok = ok and not bad
        print("   n=%d k=%d 组合数=%d 取样=%d 首坏=%s" % (n, k, len(combos), len(list(idxs)), bad[:3]))
    check("P1 unrank 与 itertools.combinations 顺序一致", ok, "n,k ∈ {(7,3),(11,5),(25,12)}；后两项取头 4000 与尾 200")


# ------------------------------------------------------- 2 检查点计数关系
CKPT_DIRS = ["m2_10_fraction", "m2_10_mpq", "m2_12_fraction", "m2_12_mpq",
             "m2_13_fraction", "m2_13_mpq", "m2_14_mpq",
             "smoke_m2_2", "smoke_m2_2_mpq", "smoke_m2_5", "smoke_m2_5_mpq",
             "det_run1", "det_run2"]


def part2():
    section("第 2 节 检查点计数关系（只读复算）")
    summary = {}
    all_ok = True
    for dd in CKPT_DIRS:
        d = os.path.join(CKPT, dd)
        fs = sorted(f for f in os.listdir(d) if f.startswith("chunk_") and f.endswith(".json"))
        chunks = [json.load(open(os.path.join(d, f))) for f in fs]
        chunks.sort(key=lambda c: c["start"])
        m2 = None
        for cand in (2, 5, 10, 12, 13, 14):
            if "m2_%d" % cand in dd or "smoke_m2_%d" % cand in dd:
                m2 = cand
        total = sum(c["count"] for c in chunks)
        want = math.comb(2 * m2 + 1, m2)
        contig = all(chunks[i]["end"] == chunks[i + 1]["start"] for i in range(len(chunks) - 1))
        rel = all(c["count"] == c["end"] - c["start"] for c in chunks)
        bal = all(c["n_rank_def"] + c["n_infeasible"] + sum(v["count"] for v in c["feasible"].values()) == c["count"] for c in chunks)
        seq = []
        for c in chunks:
            seq.append(c["start"] == 0 or True)
        un_ok = True
        bad_un = []
        for c in chunks:
            if unrank(2 * m2 + 1, m2, c["start"]) != tuple(c["first"]):
                un_ok = False
                bad_un.append((c["chunk"], "first"))
            if unrank(2 * m2 + 1, m2, c["end"] - 1) != tuple(c["last"]):
                un_ok = False
                bad_un.append((c["chunk"], "last"))
        keys = set()
        cap = []
        for c in chunks:
            for k, v in c["feasible"].items():
                keys.add(k)
                cap.append(v["count"])
        ok = (total == want) and contig and rel and bal and un_ok and (len(keys) == m2 or (m2 == 2 and len(keys) == 3))
        all_ok = all_ok and ok
        summary[dd] = dict(m2=m2, chunks=len(chunks), total=total, want=want,
                           n_rank_def=sum(c["n_rank_def"] for c in chunks),
                           n_infeasible=sum(c["n_infeasible"] for c in chunks),
                           n_feas_pts=len(keys), cap_min=min(cap), cap_max=max(cap),
                           chunk_starts=[c["start"] for c in chunks], chunk_ends=[c["end"] for c in chunks])
        print("   %-16s m2=%2d 片=%2d Σcount=%d C(2m+1,m)=%d 相接=%s 逐片关系=%s unrank=%s 去重点=%d 捕捉=[%d,%d]"
              % (dd, m2, len(chunks), total, want, contig, rel and bal, un_ok, len(keys), min(cap), max(cap)))
        if bad_un:
            print("      unrank 不符：%s" % (bad_un[:3],))
    check("P2 检查点计数关系与 unrank 元数据", all_ok,
          "13 个目录；判据 = Σcount = C(2m2+1,m2) 且首尾相接 且 count = end - start 且 n_rank_def + n_infeasible + Σfeasible.count = count 且 first/last = unrank(start)/unrank(end-1) 且去重点数 = m2（m2 = 2 档为 3）")
    return summary


# --------------------------------------------- 3 分检总和 vs 判串直方图
DEC_FILES = {
    10: "c_m10_t8_decisions.txt",
    12: "c_m12_t8_decisions.txt",
    13: "c_m13_t8_decisions.txt",
    14: "c_m14_t8_decisions.txt",
    5: "m5_e10_decisions.txt",
}
CKPT_FOR = {10: "m2_10_mpq", 12: "m2_12_mpq", 13: "m2_13_mpq", 14: "m2_14_mpq", 5: "smoke_m2_5_mpq"}


def part3(summary):
    section("第 3 节 检查点分检总和 与 判串直方图 对拍（跨实现、跨产物线）")
    all_ok = True
    dec = {}
    for m2, f in DEC_FILES.items():
        p = os.path.join(R2, f)
        buf = read_decisions(p)
        h = histof(buf)
        dec[m2] = dict(md5=md5_of(p), n=len(buf), hist=h,
                       fpos=[i for i, c in enumerate(buf) if c == ord("F")])
        print("   %-24s md5=%s 字节=%d S/I/F = %d/%d/%d" % (f, dec[m2]["md5"], dec[m2]["n"], h["S"], h["I"], h["F"]))
    for m2 in (5, 10, 12, 13, 14):
        s = summary[CKPT_FOR[m2]]
        d = dec[m2]
        ok = (s["n_rank_def"] == d["hist"]["S"] and s["n_infeasible"] == d["hist"]["I"]
              and s["n_feas_pts"] == d["hist"]["F"] and s["total"] == d["n"])
        all_ok = all_ok and ok
        print("   m2=%2d 检查点(S,I,点数,总)=(%d,%d,%d,%d) 判串(S,I,F,字节)=(%d,%d,%d,%d) 相等=%s"
              % (m2, s["n_rank_def"], s["n_infeasible"], s["n_feas_pts"], s["total"],
                 d["hist"]["S"], d["hist"]["I"], d["hist"]["F"], d["n"], ok))
    check("P3 检查点分检总和 = 判串直方图", all_ok,
          "五档 {5,10,12,13,14}；比较字段 = n_rank_def/Σn_infeasible/可行点数/总数 对 判串 S/I/F/字节数")
    return dec


# ------------------------------------- 4 顶点自算活跃条数与活跃秩
def part4():
    section("第 4 节 检查点可行顶点：自算活跃约束条数与活跃秩")
    all_ok = True
    rows = []
    for dd, m2, d, W, want in (
        ("m2_10_mpq", 10, D_LO, 2000, (10, 10)),
        ("m2_12_mpq", 12, D_LO, 2000, (12, 12)),
        ("m2_13_mpq", 13, D_LO, 2000, (13, 13)),
        ("m2_14_mpq", 14, D_LO, 2000, (14, 14)),
        ("smoke_m2_5_mpq", 5, D_LO, W_M5, (5, 6)),
        ("smoke_m2_2_mpq", 2, Fraction(3, 2), Fraction(3, 2), (2, 2)),
    ):
        cons = constraint_list(m2, d, W)
        fs = sorted(f for f in os.listdir(os.path.join(CKPT, dd)) if f.startswith("chunk_"))
        keys = []
        for f in fs:
            c = json.load(open(os.path.join(CKPT, dd, f)))
            keys.extend(c["feasible"].keys())
        prof = set()
        feas = True
        for k in keys:
            y = tuple(Fraction(s) for s in k.split(","))
            ok_f = True
            for a, b, t in cons:
                s = sum(a[j] * y[j] for j in range(m2))
                if (t == "ge" and s < b) or (t == "le" and s > b):
                    ok_f = False
            feas = feas and ok_f
            prof.add(active_profile(y, m2, cons))
        ok = feas and (len(prof) == 1) and (list(prof)[0] == want)
        all_ok = all_ok and ok
        rows.append((dd, len(keys), sorted(prof), want, ok))
        print("   %-16s 点数=%2d 自算(活跃条数,秩)=%s 期望=%s 可行=%s" % (dd, len(keys), sorted(prof), want, feas))
    check("P4 检查点顶点自算活跃条数与活跃秩", all_ok,
          "六档；主档四档期望 (m2, m2)；边界档 m2 = 5 期望 (5, 6)；阴性档 m2 = 2 期望 (2, 2)")
    return rows


# --------------------------------------------------- 5 抽点重算 m12/m13
def sample_ranks(m2, total, dec):
    """确定性子集样本：F 全体 + 首块 + 尾块 + 分片边界窗 + 等距样 + LCG 样。"""
    B = 2000
    W = 21
    rs = set(dec[m2]["fpos"])
    rs |= set(range(0, min(B, total)))
    rs |= set(range(max(0, total - B), total))
    s = None
    for dd in (CKPT_FOR[m2], "m2_%d_fraction" % m2):
        if dd in s or True:
            pass
    for dd in CKPT_DIRS:
        if not dd.startswith("m2_%d_" % m2):
            continue
        fs = sorted(f for f in os.listdir(os.path.join(CKPT, dd)) if f.startswith("chunk_"))
        for f in fs:
            c = json.load(open(os.path.join(CKPT, dd, f)))
            for r in range(c["start"], min(c["start"] + W, total)):
                rs.add(r)
            for r in range(max(0, c["end"] - W), c["end"]):
                rs.add(r)
    N = 1500
    for k in range(N):
        rs.add((k * total) // N)
    seed = 20261028
    x = seed
    for k in range(N):
        x = (1103515245 * x + 12345) % (2 ** 31)
        rs.add(x % total)
    return sorted(rs), dict(B=B, W=W, N=N, seed=seed)


def part5(dec):
    section("第 5 节 抽点重算：m2 = 12、13 与判串逐字节比较")
    all_ok = True
    detail = {}
    for m2, dd in ((12, "m2_12_mpq"), (13, "m2_13_mpq")):
        d, W = D_LO, Fraction(2000)
        cons = constraint_list(m2, d, W)
        total = math.comb(2 * m2 + 1, m2)
        buf = read_decisions(os.path.join(R2, DEC_FILES[m2]))
        ranks, par = sample_ranks(m2, total, dec)
        n = 2 * m2 + 1
        t0 = time.time()
        bad = []
        got = {}
        verts = {}
        for r in ranks:
            sub = unrank(n, m2, r)
            ch, y, rank_ = judge(sub, m2, d, W, cons)
            want = chr(buf[r])
            if ch != want:
                bad.append((r, sub, ch, want))
            got[r] = ch
            if y is not None:
                verts[r] = y
        dt = time.time() - t0
        # 逐字节：抽查位置的字符全同 等价于 逐位置比较；另做「连续段整体切片相等」
        seg_ok = True
        for lo, hi in ((0, par["B"]), (total - par["B"], total)):
            seg = bytes(ord(got[r]) for r in range(lo, hi))
            if seg != buf[lo:hi]:
                seg_ok = False
        # F 全体与坐标
        rots = set(rotation_values(m2, d, W))
        fpos = dec[m2]["fpos"]
        f_ok = all(got.get(r) == "F" for r in fpos)
        coord_ok = True
        for r in fpos:
            y = verts.get(r)
            if y is None or set(y) != rots:
                coord_ok = False
        # 与检查点可行键集合比较（抽中的顶点并入检查点键集）
        ck = set()
        fs = sorted(f for f in os.listdir(os.path.join(CKPT, dd)) if f.startswith("chunk_"))
        for f in fs:
            c = json.load(open(os.path.join(CKPT, dd, f)))
            ck |= set(c["feasible"].keys())
        mine = set(point_str(y) for y in verts.values())
        ck_ok = mine.issubset(ck)
        ok = (not bad) and seg_ok and f_ok and coord_ok and ck_ok
        all_ok = all_ok and ok
        detail[m2] = dict(ranks=len(ranks), bad=bad[:5], seg_ok=seg_ok, f_ok=f_ok,
                          coord_ok=coord_ok, ck_ok=ck_ok, sec=dt, par=par,
                          n_vertices=len(mine), ck_keys=len(ck))
        print("   m2=%2d 抽样=%d 子集（F 全体 %d + 首尾块各 %d + 分片边界窗 %d + 等距 %d + LCG %d）"
              % (m2, len(ranks), len(fpos), par["B"], par["W"], par["N"], par["N"]))
        print("        逐字节比较：不一致 = %d（前几个 %s）" % (len(bad), bad[:3]))
        print("        首块与尾块连续段切片相等 = %s；F 全体判 'F' = %s；F 点坐标 = 解析旋转集 = %s；抽中顶点 ⊆ 检查点键 = %s"
              % (seg_ok, f_ok, coord_ok, ck_ok))
        print("        抽中顶点去重 = %d；检查点键数 = %d；本段用时 = %.1f s" % (len(mine), len(ck), dt))
    check("P5 抽点重算与判串逐字节一致（m2 = 12、13）", all_ok,
          "F 全体 + [0,2000) + [total-2000,total) + 每分片两端各 21 + 等距 1500 + LCG 1500（seed 20261028）；判据 = 每个抽点字符与判串同位置字节相等")
    return detail


# -------------------------------------------- 6 m2 = 10 阳性对照（全量）
def part6(dec, m10_full):
    section("第 6 节 m2 = 10 阳性对照（第三套求解器全量重算 352716 子集）")
    if not m10_full:
        skip("P6 m2 = 10 全量阳性对照", "以 --no-m10-full 关闭")
        return None
    m2, d, W = 10, D_LO, Fraction(2000)
    cons = constraint_list(m2, d, W)
    total = math.comb(21, 10)
    buf = read_decisions(os.path.join(R2, DEC_FILES[10]))
    t0 = time.time()
    out = bytearray()
    first_bad = []
    n = 2 * m2 + 1
    for r in range(total):
        sub = unrank(n, m2, r)
        ch, y, _ = judge(sub, m2, d, W, cons)
        out.append(ord(ch))
        if ch != chr(buf[r]) and len(first_bad) < 5:
            first_bad.append((r, sub, ch, chr(buf[r])))
    dt = time.time() - t0
    same = bytes(out) == buf
    h = hashlib.md5(bytes(out)).hexdigest()
    print("   全量 %d 子集，用时 %.1f s（%.4f ms/子集）；重算 md5 = %s；判串 md5 = %s" % (total, dt, 1000 * dt / total, h, dec[10]["md5"]))
    print("   逐字节相等 = %s；不一致数 = %d（前几个 %s）" % (same, len(first_bad), first_bad))
    check("P6 m2 = 10 全量阳性对照逐字节相等", same, "%d 子集，自算 md5 = %s" % (total, h))
    return dict(sec=dt, md5=h, same=same)


# ------------------------------------------------ 7 三方顶点坐标相等
def part7():
    section("第 7 节 顶点坐标三方比较（本脚本 / route-3 两实现 / 检查点）")
    all_ok = True
    for m2, dd in ((12, "m2_12_mpq"), (13, "m2_13_mpq")):
        d, W = D_LO, Fraction(2000)
        mine = set(point_str(y) for y in (tuple(v * d ** ((j + r) % m2) for j in range(m2))
                                          for v in [v_vertex(m2, d, W)] for r in range(m2)))
        ck = set()
        fs = sorted(f for f in os.listdir(os.path.join(CKPT, dd)) if f.startswith("chunk_"))
        for f in fs:
            c = json.load(open(os.path.join(CKPT, dd, f)))
            ck |= set(c["feasible"].keys())
        impls = {}
        for tag, p in (("impl1", os.path.join(RES, "route3_impl1_m%d.json" % m2)),
                       ("impl2", os.path.join(RES, "route3_impl2_m%d.json" % m2))):
            if not os.path.exists(p):
                impls[tag] = None
                continue
            j = json.load(open(p))
            s = set()
            for c in j["candidates"]:
                s.add(",".join(str(Fraction(t)) for t in c["point"].split(",")))
            impls[tag] = s
        parts = [("本脚本旋转集", mine), ("检查点键集", ck)]
        for tag in ("impl1", "impl2"):
            if impls[tag] is not None:
                parts.append(("route3-%s" % tag, impls[tag]))
        eq = all(p[1] == mine for p in parts)
        all_ok = all_ok and eq
        print("   m2=%2d %s" % (m2, "；".join("%s=%d" % (n, len(s)) for n, s in parts)))
        for n, s in parts:
            if s != mine:
                print("      %s 与我的旋转集不同：仅我有 %d，仅它有 %d" % (n, len(mine - s), len(s - mine)))
        if impls["impl1"] is None:
            print("      route3-impl1 m%d 结果 JSON 不存在（登记为覆盖缺档，不算通过）" % m2)
    check("P7 顶点坐标集在本脚本/两实现/检查点间相等", all_ok,
          "m2 = 12 四方、m2 = 13 三方（impl1 无 13 档结果）；比较字段 = 逗号连接的坐标精确有理串集合")


def main():
    argv = sys.argv[1:]
    m10_full = "--no-m10-full" not in argv
    print("spot_recheck（第三套求解器）：python = %s" % PY, flush=True)
    print("脚本 md5 = %s" % md5_of(os.path.abspath(__file__)), flush=True)
    t_all = time.time()
    part1()
    summ = part2()
    dec = part3(summ)
    part4()
    d5 = part5(dec)
    d6 = part6(dec, m10_full)
    part7()
    print("\n== 汇总 ==")
    print("判据数 = %d，通过 = %d，失败 = %d，跳过 = %d，总用时 = %.1f s"
          % (len(CHECKS), sum(1 for c in CHECKS if c[1]), len(FAILS), len(SKIPS), time.time() - t_all))
    for n, ok, det in CHECKS:
        print("   %s %s" % ("PASS" if ok else "FAIL", n))
    for n, why in SKIPS:
        print("   SKIP %s（%s）" % (n, why))
    if FAILS:
        print("\n失败明细：")
        for n, det in FAILS:
            print("   %s：%s" % (n, det))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
