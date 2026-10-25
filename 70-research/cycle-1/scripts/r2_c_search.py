#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-2 第 3 步：多面体上的定向反例搜索（阈值 0）。

要检验的精确陈述（TP）：
  给定有理 δ > 1 与 W > (δ^{m2}−1)/(δ−1)，令
    P = { y ∈ R^{m2} : y_j >= 1；y_{j+1} <= δ y_j（j 循环，m2 条）；Σ y_j >= W }，
    S(y) = Σ_j 3/(2^{y_j} − 1)，  v = W(δ−1)/(δ^{m2}−1)，V = (v, δv, …, δ^{m2−1}v)。
  则 sup_P S = S(V)。
本脚本只做一件事：找反例（可行的 y 使 S(y) > S(V)）。判定阈值 = 0。

三种判决，全部只依赖精确有理算术与整数幂：
  C1 排序支配（零宽度，精确）：把 y 与 V 的坐标各自升序排好，若逐位 y_(j) >= V_(j)，
     则逐项 f(y_j) <= f(V_j)，直接得 S(y) <= S(V)。
  C2 区间证书：S_hi(y) <= S_lo(V)（两串严格有理界）。
  CE 反例：S_lo(y) > S_hi(V)。
其余记为「未决（带内重叠）」并如实报数。找不到反例只能写成「在给定搜索下未发现反例」。
"""
import sys
import time
from fractions import Fraction

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
import mpmath
from r2_common import (delta_rigorous_bounds, v_vertex, vertex, feasible,
                       S_bounds, repair_normalize,
                       LEVEL_MID, LEVEL_FINE, LEVEL_ULTRA, Det)

D_LO7, D_HI7 = delta_rigorous_bounds(10 ** 7)


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def S_float(y, dps=30):
    """浮点探针（只用于搜索方向与摘要，不参与任何判决）。指数过大按 0 计。"""
    mpmath.mp.dps = dps
    tot = mpmath.mpf(0)
    for t in y:
        e = mpmath.mpf(t.numerator) / mpmath.mpf(t.denominator)
        if e > 10 ** 6:
            continue
        tot += 3 / (mpmath.mpf(2) ** e - 1)
    return tot


def sorted_dominates(y, V):
    """零宽度精确证书：升序后逐位 y >= V。"""
    return all(a >= b for a, b in zip(sorted(y), sorted(V)))


# ------------------------------------------------------------------ 构造工具
# repair_normalize 见 r2_common.py（供本脚本与审计脚本共用同一实现）
def from_u(u, m2, d, base=None):
    y = [Fraction(1) if base is None else Fraction(base)]
    for j in range(m2 - 1):
        y.append(y[-1] * d * u[j])
    return y


def normalize(y, m2, d, W):
    lam = max(W / sum(y), Fraction(1) / min(y))
    return [t * lam for t in y]


def gen_family(m2, d, W, det):
    out = []
    v = v_vertex(m2, d, W)
    for r in range(m2):
        out.append(("F0 顶点旋转", list(vertex(m2, d, W, r))))
    out.append(("F1 均匀", [W / m2] * m2))
    out.append(("F2 顶点加平坦", [v] + [d * v] * (m2 - 1)))
    rs = [Fraction(1, 2), Fraction(3, 4), Fraction(9, 10), Fraction(1, 1) / d,
          Fraction(1, 4), Fraction(1, 2) / d, Fraction(1023, 1024)]
    ks = sorted({1, max(1, m2 // 4), max(1, m2 // 2), max(1, 3 * m2 // 4), m2 - 1})
    for r in rs:
        for k in ks:
            u = [Fraction(1)] * (m2 - 1)
            for j in range(k, m2 - 1):
                u[j] = r
            out.append(("F3 两段型(前紧后松)", normalize(from_u(u, m2, d), m2, d, W)))
            u = [r] * (m2 - 1)
            for j in range(k, m2 - 1):
                u[j] = Fraction(1)
            out.append(("F3 两段型(前松后紧)", normalize(from_u(u, m2, d), m2, d, W)))
    for r in [Fraction(1, 2), Fraction(1, 4), Fraction(1, 1) / d]:
        u = [r if j % 2 == 0 else Fraction(1) for j in range(m2 - 1)]
        out.append(("F4 梳型(双尖峰)", normalize(from_u(u, m2, d), m2, d, W)))
        u = [Fraction(1) if j % 2 == 0 else r for j in range(m2 - 1)]
        out.append(("F4 梳型(双尖峰)", normalize(from_u(u, m2, d), m2, d, W)))
    for p in range(0, min(m2, 8)):
        y = [v] * (p + 1) + [v * d ** k for k in range(1, m2 - p)]
        out.append(("F5 尖峰型(平台加几何)", list(y)))
        y = [v * d ** k for k in range(1, m2 - p)] + [v] * (p + 1)
        out.append(("F5 尖峰型(几何加平台)", repair_normalize(y, m2, d, W)))
    for eps in [Fraction(1, 1024), Fraction(1, 4096), Fraction(1, 64), Fraction(1, 16)]:
        V0 = list(vertex(m2, d, W, 0))
        idx = [j for j in range(m2) if j % max(1, m2 // 6) == 0]
        y = list(V0)
        for j in idx:
            y[j] = y[j] * (1 + eps)
        out.append(("F6 顶点乘性扰动", repair_normalize(y, m2, d, W)))
        y = list(V0)
        for j in idx:
            y[j] = y[j] * (1 - eps)
        out.append(("F6 顶点乘性扰动", repair_normalize(y, m2, d, W)))
    # F10 顶点凸组合（对凸函数最苛刻的方向：边上的点）
    verts = [list(vertex(m2, d, W, r)) for r in range(m2)]
    for lam in [Fraction(1, 2), Fraction(1, 4), Fraction(3, 4), Fraction(1, 100), Fraction(99, 100),
                Fraction(1, 1024), Fraction(1, 10)]:
        for r in range(min(m2, 4)):
            y = [lam * verts[0][j] + (1 - lam) * verts[(r + 1) % m2][j] for j in range(m2)]
            out.append(("F10 顶点凸组合", y))
    for _ in range(20):
        ks2 = [det.below(m2) for _ in range(2)]
        lam = Fraction(det.between(1, 1023), 1024)
        y = [lam * verts[ks2[0]][j] + (1 - lam) * verts[ks2[1]][j] for j in range(m2)]
        out.append(("F10 顶点凸组合", y))
    dens = [2, 4, 8, 16, 64, 128, 1024]
    for _ in range(140):
        u = [min(Fraction(det.between(1, 1024), det.pick(dens)), Fraction(1)) for _ in range(m2 - 1)]
        base = Fraction(det.between(1, 1000), det.pick([1, 2, 4, 8]))
        out.append(("F7 随机链型", normalize(from_u(u, m2, d, base), m2, d, W)))
    for _ in range(140):
        y = [Fraction(det.between(1, 4096), det.pick(dens)) for _ in range(m2)]
        out.append(("F8 随机修复", repair_normalize(y, m2, d, W)))
    return out


def perturb_u(u, det, scale):
    k = det.below(len(u))
    num = det.between(-scale, scale)
    u2 = list(u)
    u2[k] = min(Fraction(1), max(Fraction(1, 10 ** 6), u2[k] * (1 + Fraction(num, 1024))))
    return u2


def hill_climb(m2, d, W, det, restarts=10, steps=40, scale=64):
    best = None
    for _ in range(restarts):
        u = [Fraction(det.between(1, 1024), 1024) for _ in range(m2 - 1)]
        y = normalize(from_u(u, m2, d), m2, d, W)
        cur = S_float(y)
        for it in range(steps):
            improved = False
            for _ in range(8):
                u2 = perturb_u(u, det, scale)
                y2 = normalize(from_u(u2, m2, d), m2, d, W)
                s2 = S_float(y2)
                if s2 > cur:
                    u, y, cur = u2, y2, s2
                    improved = True
                    break
            if not improved:
                scale = max(2, scale // 2)
                if scale <= 2 and it > steps // 2:
                    break
        if best is None or cur > best[0]:
            best = (cur, y)
    return best[1]


PARAMS = [
    ("E1  m2=2  δ_lo   W=70",                    2,  D_LO7, Fraction(70)),
    ("E2  m2=3  δ_lo   W=210",                   3,  D_LO7, Fraction(210)),
    ("E3  m2=5  δ_lo   W=200",                   5,  D_LO7, Fraction(200)),
    ("E4  m2=10 δ_lo   W=2000",                  10, D_LO7, Fraction(2000)),
    ("E5  m2=20 δ_lo   W 使 v=70",               20, D_LO7, None),
    ("E6  m2=47 δ_lo   W=(47/91)·7e11",          47, D_LO7, Fraction(47, 91) * 10 ** 11 * 7),
    ("E7  m2=91 δ_lo   W=205632218873398596256", 91, D_LO7, Fraction(205632218873398596256)),
    ("E8  m2=5  δ=317/200 W=200",                5,  Fraction(317, 200), Fraction(200)),
    ("E9  m2=5  δ=3/2  W=200",                   5,  Fraction(3, 2), Fraction(200)),
    ("E10 m2=5  δ_lo  v=1（阈值边界）",           5,  D_LO7, None),
    ("E12 m2=6  δ_lo  W=500",                    6,  D_LO7, Fraction(500)),
]

if __name__ == "__main__":
    say("=" * 78)
    say("route-2 第 3 步：定向反例搜索（阈值 0；反例判据 S_lo(y) > S_hi(V)）")
    say("=" * 78)
    say(f"精度档 MID = {LEVEL_MID}，FINE = {LEVEL_FINE}，ULTRA = {LEVEL_ULTRA}")

    grand = {"samples": 0, "counter": 0, "c1": 0, "c2": 0, "unres": 0}
    summary_rows = []
    for tag, m2, d, W in PARAMS:
        if W is None:
            W = (Fraction(70) * (d ** m2 - 1) / (d - 1)) if tag.startswith("E5") else (d ** m2 - 1) / (d - 1)
        t0 = time.time()
        det = Det(12345 + m2 * 1000 + (1 if tag.startswith("E5") else 0))
        v = v_vertex(m2, d, W)
        V0 = list(vertex(m2, d, W, 0))
        # 参考值：多个旋转在各档上取最保守一侧（S_lo 取最小、S_hi 取最大）
        refs = {}
        for lvlname, lvl in (("MID", LEVEL_MID), ("FINE", LEVEL_FINE), ("ULTRA", LEVEL_ULTRA)):
            rot = list(range(min(m2, 6))) + [m2 - 1]
            lo = hi = None
            for r in sorted(set(rot)):
                a, b = S_bounds(list(vertex(m2, d, W, r)), *lvl)
                lo = a if lo is None else min(lo, a)
                hi = b if hi is None else max(hi, b)
            refs[lvlname] = (lo, hi)
        lo0, hi0 = refs["MID"]
        say(f"\n[{tag}]  δ = {d.numerator}/{d.denominator}  v = "
            f"{float(mpmath.mpf(v.numerator)/mpmath.mpf(v.denominator)):.9f}"
            f"  W 位数 = {W.numerator.bit_length()}")
        for lvlname in ("FINE", "ULTRA"):
            a, b = refs[lvlname]
            say(f"    顶点值参考（{lvlname}）：S_lo = "
                f"{float(mpmath.mpf(a.numerator)/mpmath.mpf(a.denominator)):.12e}，"
                f"S_hi = {float(mpmath.mpf(b.numerator)/mpmath.mpf(b.denominator)):.12e}，"
                f"相对带宽 = {float((b-a)/a):.2e}")
        samples = gen_family(m2, d, W, det)
        for _ in range(3):
            samples.append(("F9 爬山", hill_climb(m2, d, W, det, restarts=4, steps=25)))
        n_feas = 0
        n_infeas = 0
        mins_ratio = None
        stat = {}
        top = []            # (S_float 比值, 族名, y)
        worst_exc = None    # max(S_lo(y) − S_hi(V))
        worst_gap = None    # max(S_hi(y) − S_lo(V))
        n_ultra_used = 0
        n_fine_used = 0
        CAP_FINE = 150
        CAP_ULTRA = 60
        for fam, yraw in samples:
            y = [Fraction(t) for t in yraw]
            ok, bad = feasible(y, m2, d, W)
            if not ok:
                n_infeas += 1
                continue
            n_feas += 1
            r = float(min(y) / v)
            mins_ratio = r if mins_ratio is None else min(mins_ratio, r)
            st = stat.setdefault(fam, {"n": 0, "C1": 0, "C2": 0, "CE": 0, "UN": 0})
            st["n"] += 1
            # C1 排序支配（零宽度）
            if sorted_dominates(y, V0):
                st["C1"] += 1
                continue
            # 分层区间证书：MID → FINE → ULTRA（后两档有配额；用尽后按上一档记未决）
            kind = verdict = None
            for lvlname in ("MID", "FINE", "ULTRA"):
                if lvlname == "FINE" and n_fine_used >= CAP_FINE:
                    kind, verdict = "UN_HOLD_MID", refs["MID"]
                    break
                if lvlname == "ULTRA" and n_ultra_used >= CAP_ULTRA:
                    kind, verdict = "UN_HOLD_FINE", refs["FINE"]
                    break
                lvl = {"MID": LEVEL_MID, "FINE": LEVEL_FINE, "ULTRA": LEVEL_ULTRA}[lvlname]
                if lvlname == "FINE":
                    n_fine_used += 1
                if lvlname == "ULTRA":
                    n_ultra_used += 1
                lo, hi = S_bounds(y, *lvl)
                rlo, rhi = refs[lvlname]
                if lo > rhi:
                    kind, verdict = "CE", (lvlname, y)
                    break
                if hi <= rlo:
                    kind, verdict = "C2", (lvlname, lo - rhi)
                    break
                kind, verdict = "UN", (lvlname, lo, hi, rlo, rhi)
            if kind == "CE":
                st["CE"] += 1
                say(f"    !! 反例（{verdict[0]} 档）：{fam}  y = {verdict[1]}")
                continue
            if kind == "C2":
                st["C2"] += 1
                st["C2@" + verdict[0]] = st.get("C2@" + verdict[0], 0) + 1
                continue
            if kind == "UN":
                lvlname, lo_u, hi_u, rlo_u, rhi_u = verdict
            else:
                lvlname = kind.split("_")[-1]
                rlo_u, rhi_u = verdict
                lo_u, hi_u = rlo_u, rhi_u        # 用尽配额时不再给出该样本的带
            st["UN"] += 1
            st["UN@" + lvlname] = st.get("UN@" + lvlname, 0) + 1
            if kind == "UN":
                exc = lo_u - rhi_u
                if worst_exc is None or exc > worst_exc[0]:
                    worst_exc = (exc, fam, lvlname)
                gap = hi_u - rlo_u
                if worst_gap is None or gap > worst_gap[0]:
                    worst_gap = (gap, fam, lvlname)
            top.append((float(S_float(y) / S_float(V0)), fam, y))
        n_cert = sum(s["C1"] + s["C2"] for s in stat.values())
        n_un = sum(s["UN"] for s in stat.values())
        n_ce = sum(s["CE"] for s in stat.values())
        say(f"    样本：可行 {n_feas}，不可行已剔除 {n_infeas}；族数 {len(stat)}；"
            f"升级次数 FINE = {n_fine_used}/{CAP_FINE}，ULTRA = {n_ultra_used}/{CAP_ULTRA}")
        say(f"    判决：C1 排序支配（零宽度）= {sum(s['C1'] for s in stat.values())}，"
            f"C2 区间证书 = {sum(s['C2'] for s in stat.values())}，未决 = {n_un}，反例 = {n_ce}")
        say(f"    未决样本中 max(S_lo(y)−S_hi(V)) = "
            f"{'无未决样本' if worst_exc is None else f'{float(worst_exc[0]):.4e}（族 {worst_exc[1]}，{worst_exc[2]} 档）'}"
            f"；带内最大可能超出 max(S_hi(y)−S_lo(V)) = "
            f"{'无' if worst_gap is None else f'{float(worst_gap[0]):.4e}（族 {worst_gap[1]}，{worst_gap[2]} 档）'}")
        say(f"    可行样本的 min_j y_j / v 最小值 = {mins_ratio:.12f}（应 >= 1，且 = 1 当且仅当取到坐标下界）")
        say("    逐族明细（族 | 样本 | C1 | C2 | 未决 | 反例）：")
        for fam in sorted(stat):
            s = stat[fam]
            say(f"      {fam} | {s['n']} | {s['C1']} | {s['C2']} | {s['UN']} | {s['CE']}")
        if top:
            top.sort(reverse=True)
            say("    未决样本中 S(y)/S(V) 最大的 5 个（浮点探针，仅作摘要）：")
            for ratio, fam, y in top[:5]:
                say(f"      {ratio:.12f}  {fam}  min y = "
                    f"{float(min(y)):.9f}  坐标前 3 个 = "
                    f"{[float(t) for t in y[:3]]}")
        summary_rows.append((tag, n_feas, sum(s["C1"] for s in stat.values()),
                             sum(s["C2"] for s in stat.values()), n_un, n_ce, time.time() - t0))
        grand["samples"] += n_feas
        grand["c1"] += sum(s["C1"] for s in stat.values())
        grand["c2"] += sum(s["C2"] for s in stat.values())
        grand["unres"] += n_un
        grand["counter"] += n_ce
        say(f"    用时 {time.time()-t0:.1f} s")

    say("\n" + "=" * 78)
    say("汇总：参数集 | 可行样本 | C1 | C2 | 未决 | 反例 | 用时")
    for row in summary_rows:
        say("    " + " | ".join([row[0], str(row[1]), str(row[2]), str(row[3]), str(row[4]),
                                str(row[5]), f"{row[6]:.1f}s"]))
    say(f"\n总可行样本 = {grand['samples']}；C1 = {grand['c1']}；C2 = {grand['c2']}；"
        f"未决 = {grand['unres']}；反例 = {grand['counter']}")
    say("结论口径：以上是有限搜索。找不到反例只能写成「在给定搜索下未发现反例」，不是定理。")
