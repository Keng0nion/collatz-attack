#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route-1（三向对照基线）驱动：用冻结副本的 full_enumeration 跑三组对照。

模式（argv[1]）：
    A  阳性：m2 = 10，δ 取严格下界 D_LO7 = 126797/80000，W = 2000（对照 r2_j_A.txt）
    B  阴性：m2 = 2，δ = 3/2，W = 3/2（预期含 (1,1) 的非旋转顶点集；对照 route-1.md:319）
    C  边界：E10（m2 = 5，δ = D_LO7，W = (δ^5−1)/(δ−1)，阈值上等号 v = 1；对照 r2_b_out.txt E10 段）
    P  附：m2 = 10 的八核分片复算（同一冻结判定函数，并行外壳；不替代对照甲）
    S  附：m2 = 10、12、13、14 的均匀抽样测速（仅作成本投影，非判定、非穷举）

纪律：
  1. 一切判决只用本目录 frozen/ 下的冻结副本；加载时核对 __file__ 与 md5，
     并与上游原件（在场时）核对 md5 相同。不 import 其它任何项目脚本。
  2. 每个数字先原样打印，再打印期望值与判定 PASS/FAIL。
  3. 期望值先于运行冻结于 results/frozen-spec.md；本文件不读取该文件，二者人工对齐。
"""
import hashlib
import math
import multiprocessing
import os
import sys
import time
from fractions import Fraction
from itertools import combinations, islice

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = os.path.join(HERE, "frozen")
UPSTREAM = "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts"
sys.path.insert(0, FROZEN)
import r2_common as rc                                  # 冻结副本，导入即在此目录

EXPECT = {
    "r2_common.py": "cfee819667c0883e73732f03d2dc8bef",
    "r2_j_independent_vertices.py": "4b8ce2a500d8ca9021fd0178deca637e",
}
_COUNT = {"pass": 0, "fail": 0}


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def md5f(path):
    # md5 在此只作「版本身份指纹」，用于与本项目既有记录（learnings.md:39 的
    # 行数或 md5 口径）对读，不用于任何安全用途。
    h = hashlib.md5()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 16), b""):
            h.update(blk)
    return h.hexdigest()


def chk(name, cond, extra=""):
    cond = bool(cond)
    _COUNT["pass" if cond else "fail"] += 1
    say(f"    [{'PASS' if cond else 'FAIL'}] {name}" + (f"；{extra}" if extra else ""))
    return cond


def gate():
    """冻结副本与 md5 门（跑前必过）。"""
    say("【冻结副本与 md5 门（跑前必过）】")
    allok = True
    for name, want in EXPECT.items():
        fp = os.path.join(FROZEN, name)
        up = os.path.join(UPSTREAM, name)
        m_f = md5f(fp)
        msg = f"    {name}：冻结副本 md5 = {m_f}，期望 = {want}"
        ok = (m_f == want)
        if os.path.exists(up):
            m_u = md5f(up)
            msg += f"；上游原件 md5 = {m_u}；冻结与上游相同 = {m_u == m_f}"
            ok = ok and (m_u == m_f)
        else:
            msg += "；上游原件不在场（跳过该对照）"
        say(msg)
        allok = allok and ok
    say(f"    r2_common 实际加载自：{rc.__file__}")
    allok = allok and (os.path.abspath(rc.__file__) == os.path.join(FROZEN, "r2_common.py"))
    chk("冻结副本身份与 md5", allok)
    return allok


def load_frozen_r2j():
    import importlib
    m = importlib.import_module("r2_j_independent_vertices")
    say(f"    r2_j 实际加载自：{m.__file__}")
    assert os.path.abspath(m.__file__) == os.path.join(FROZEN, "r2_j_independent_vertices.py"), m.__file__
    return m


def delta_anchor():
    """δ 锚点自检：整数幂判据，方向为下界。返回 (dlo, dhi)。"""
    say("【δ 锚点自检（整数幂判据，方向：D_LO7 为严格下界）】")
    import gmpy2
    q = 10 ** 7
    p_lo, p_hi = 15849625, 15849626        # 即 126797/80000 与 7924813/5000000 通分到 10^7
    t = time.time()
    three_q = gmpy2.mpz(3) ** q
    ok1 = gmpy2.mpz(2) ** p_lo < three_q
    ok2 = gmpy2.mpz(2) ** p_hi > three_q
    say(f"    2^15849625 < 3^10000000：{ok1}；2^15849626 > 3^10000000：{ok2}（用时 {time.time()-t:.2f} s）")
    say(f"    15849625/10^7 = {Fraction(p_lo, q)}；15849626/10^7 = {Fraction(p_hi, q)}")
    dlo, dhi = rc.delta_rigorous_bounds(q)
    say(f"    冻结 delta_rigorous_bounds(10^7) 复算 = ({dlo}, {dhi})")
    chk("D_LO7 复算与整数幂判据一致（下界方向）",
        ok1 and ok2 and dlo == Fraction(p_lo, q) and dhi == Fraction(p_hi, q))
    return dlo, dhi


# ------------------------------------------------------------ 名称与哈希辅助

def cons_name(i, m2):
    if i < m2:
        return f"C1:y{i+1}"
    if i < 2 * m2:
        return f"C2:{i - m2}"
    return "SUM"


def active_idx(y, m2, d, W):
    """点 y 处活跃约束的下标集合（equality）。"""
    cons = rc.constraint_list(m2, d, W)
    out = []
    for i, (a, b, sense) in enumerate(cons):
        if sum(a[j] * y[j] for j in range(m2)) == b:
            out.append(i)
    return out


def thash(t):
    return hashlib.sha256("|".join(str(f) for f in t).encode()).hexdigest()[:32]


def hdr(tag):
    say("=" * 78)
    say(tag)
    say("=" * 78)
    say(f"    时间 = {time.strftime('%Y-%m-%d %H:%M:%S')}；python = {sys.version.split()[0]}；cpu_count = {os.cpu_count()}")


# ---------------------------------------------------------------- 对照甲（阳性）

def arm_A():
    hdr("route-1 对照甲（阳性）：m2 = 10，δ = D_LO7，W = 2000")
    if not gate():
        say("    冻结门未过，本档终止。")
        return
    r2j = load_frozen_r2j()
    dlo, dhi = delta_anchor()
    m2, W = 10, Fraction(2000)
    thr = (dlo ** m2 - 1) / (dlo - 1)
    say(f"    参数：m2 = {m2}；δ = {dlo}（下界）；W = {W}")
    say(f"    (P1) 阈值 (δ^m2−1)/(δ−1) = {thr.numerator.bit_length()} 位分子 / "
        f"{thr.denominator.bit_length()} 位分母；W > 阈值 = {W > thr}")
    say("    调用冻结 full_enumeration(m2, δ_lo, W)（进度行由冻结函数自行打印）：")
    t0 = time.time()
    verts, total, dt = r2j.full_enumeration(m2, dlo, W)
    wall = time.time() - t0
    say(f"    子集总数 C({2*m2+1},{m2}) = {total}，用时 {dt:.1f} s（含逐子集判定；函数外挂钟 {wall:.1f} s）")
    analytic = {tuple(rc.vertex(m2, dlo, W, r)) for r in range(m2)}
    same = set(verts.keys()) == analytic
    say(f"    可行顶点数 = {len(verts)}；与解析的 m2 = {m2} 个循环旋转相同 = {same}（解析集大小 {len(analytic)}）")
    certs = sorted({r2j.active_rank(y, m2, dlo, W) for y in verts})
    say(f"    每个顶点的（活跃约束法向量秩，活跃约束条数）= {certs}")
    say(f"    独立性：本段只用 constraint_list / solve_exact / feasible，未使用 (L1) 或 v 的任何信息")
    say("  —— 逐项核对（期望值先于运行冻结于 results/frozen-spec.md）——")
    chk("子集总数 = C(21,10) = 352716", total == math.comb(21, 10) == 352716, f"实测 {total}")
    chk("顶点数 = 10，顶点集与解析旋转集相等", len(verts) == 10 and len(analytic) == 10 and same,
        f"实测 顶点 {len(verts)} / 解析 {len(analytic)} / 相等 {same}")
    chk("证书 = [(10, 10)]", certs == [(10, 10)], f"实测 {certs}")
    bad = []
    for y, S in verts.items():
        cons = rc.constraint_list(m2, dlo, W)
        rows = [cons[i][0] for i in S]
        b = [cons[i][1] for i in S]
        sol, rank = rc.solve_exact(rows, b)
        if tuple(sol) != y or rank != m2:
            bad.append(y)
    chk("每个顶点的命中子集回放（解重合且秩 = m2）", not bad, f"异常 {len(bad)} 个")
    chk("解析集 10 个点全部可行", all(rc.feasible(y, m2, dlo, W)[0] for y in analytic))
    selfcons = all(set(verts[y]) == set(active_idx(y, m2, dlo, W)) for y in verts)
    chk("命中子集 = 该点处活跃约束集（证书自洽）", selfcons)
    per = 1000 * dt / total
    say(f"    每子集单核毫秒 = {per:.4f}（= 1000 × {dt:.1f} / {total}）")
    say("    顶点明细（按坐标排序；sha256 为精确 Fraction 元组 repr 的哈希，可跨档对拍）：")
    for y in sorted(verts):
        ridx = [r for r in range(m2) if tuple(rc.vertex(m2, dlo, W, r)) == y]
        names = [cons_name(i, m2) for i in verts[y]]
        act = [cons_name(i, m2) for i in active_idx(y, m2, dlo, W)]
        say(f"      r = {ridx[0] if ridx else '?'}；sha256[:32] = {thash(y)}；命中子集 = {names}；活跃约束 = {act}")
    base = tuple(rc.vertex(m2, dlo, W, 0))
    say("    顶点 r = 0 的精确坐标（示例，完整 Fraction 串）：")
    say("      (" + ", ".join(str(f) for f in base) + ")")


# ---------------------------------------------------------------- 对照乙（阴性）

def arm_B():
    hdr("route-1 对照乙（阴性）：m2 = 2，δ = 3/2，W = 3/2（预期含 (1,1) 的非旋转顶点集）")
    if not gate():
        say("    冻结门未过，本档终止。")
        return
    r2j = load_frozen_r2j()
    m2, d, W = 2, Fraction(3, 2), Fraction(3, 2)
    thr = (d ** m2 - 1) / (d - 1)
    v = rc.v_vertex(m2, d, W)
    say(f"    参数：m2 = {m2}；δ = {d}；W = {W}；阈值 (δ^2−1)/(δ−1) = {thr}；W > 阈值 = {W > thr}；v = {v}（< 1）")
    say("    调用冻结 full_enumeration(m2, δ, W)：")
    verts, total, dt = r2j.full_enumeration(m2, d, W)
    vset = set(verts.keys())
    pred = {tuple(rc.vertex(m2, d, W, r)) for r in range(m2)}
    say(f"    子集总数 C(5,2) = {total}，用时 {dt:.3f} s")
    say("    v = " + str(v) + "（小于 1；预测族里 y_1 = v，违反 y_1 >= 1）")
    say("    实际顶点集合 = " + "；".join(str(y) for y in sorted(vset)))
    say("    预测族 = " + "；".join(str(y) for y in sorted(pred)))
    EXP_B = {(Fraction(1), Fraction(1)), (Fraction(1), Fraction(3, 2)), (Fraction(3, 2), Fraction(1))}
    EXP_P = {(Fraction(3, 5), Fraction(9, 10)), (Fraction(9, 10), Fraction(3, 5))}
    chk("子集总数 = C(5,2) = 10", total == math.comb(5, 2) == 10, f"实测 {total}")
    chk("顶点集合恰为 {(1,1)、(1,3/2)、(3/2,1)}", vset == EXP_B, f"实测 {sorted(vset)}")
    chk("预测集恰为 {(3/5,9/10)、(9/10,3/5)}", pred == EXP_P, f"实测 {sorted(pred)}")
    chk("预测集与顶点集不相交（分类在 v < 1 时失效）", not (pred & vset))
    chk("顶点集与预测集相等 = False（实现有判别力，不会无条件输出旋转）", (vset == pred) is False)
    certs = {}
    for y in sorted(vset):
        certs[y] = r2j.active_rank(y, m2, d, W)
        say(f"    顶点 {y}：活跃约束 = {[cons_name(i, m2) for i in active_idx(y, m2, d, W)]}"
            f"（秩，条数）= {certs[y]}")
    chk("每个顶点的活跃秩 = m2 = 2（顶点证书）", all(c[0] == 2 for c in certs.values()),
        f"实测 {sorted(set(certs.values()))}")
    say("    S 值（严格区间，k = 10，s = 20；坐标全为整数时另按精确分数直算）：")
    S_iv = {}
    for y in sorted(vset):
        lo, hi = rc.S_bounds(y, 10, 20)
        S_iv[y] = (lo, hi)
        say(f"      S{y} ∈ [{lo}, {hi}]")
    say(f"      S(1, 1) 精确值 = 6（项 3/(2^1−1) = 3 精确，两项共 6）")
    lo6 = S_iv[(Fraction(1, 1), Fraction(1, 1))][0]
    hi6 = S_iv[(Fraction(1, 1), Fraction(1, 1))][1]
    hi_15 = S_iv[(Fraction(1, 1), Fraction(3, 2))][1]
    hi_51 = S_iv[(Fraction(3, 2), Fraction(1, 1))][1]
    chk("S((1,1)) 的严格区间含精确值 6，且另两点区间上界 < 6（顶点集上最大值在 (1,1)）",
        lo6 <= 6 <= hi6 and hi_15 < 6 and hi_51 < 6,
        f"（1,3/2）上界 = {hi_15}；（3/2,1）上界 = {hi_51}")
    d464 = Fraction("4.640754482")
    chk("基线浮点 4.640754482 落在 (1,3/2)、(3/2,1) 两个严格区间内",
        S_iv[(Fraction(1, 1), Fraction(3, 2))][0] <= d464 <= hi_15
        and S_iv[(Fraction(3, 2), Fraction(1, 1))][0] <= d464 <= hi_51)
    say("    预测族点的 S 严格区间：")
    lo_p, hi_p = rc.S_bounds(tuple(rc.vertex(m2, d, W, 0)), 10, 20)
    say(f"      S{(Fraction(3, 5), Fraction(9, 10))} ∈ [{lo_p}, {hi_p}]")
    d928 = Fraction("9.281088094")
    chk("基线浮点 9.281088094 落在预测族点的严格区间内", lo_p <= d928 <= hi_p,
        f"区间 = [{lo_p}, {hi_p}]")
    chk("预测族点 S 的区间下界 > 6（分类失效但点值仍高于顶点值；证据边界照 route-1.md:320）",
        lo_p > 6, f"下界 = {lo_p}")
    import mpmath
    mpmath.mp.dps = 30
    sv = {y: mpmath.mpf(0) for y in vset}
    for y in vset:
        lo, hi = S_iv[y]
        sv[y] = (mpmath.mpf(lo.numerator) / lo.denominator + mpmath.mpf(hi.numerator) / hi.denominator) / 2
    say("    S 值浮点摘要（区间中点，仅供与基线数字串对读）：")
    for y in sorted(vset, key=lambda t: -sv[t]):
        say(f"      {y} -> {mpmath.nstr(sv[y], 10)}")


# ---------------------------------------------------------------- 对照丙（边界）

def reduced_enumeration_notes(m2, d, W):
    """r2_b_vertices.enumerate_vertices 的子集构造复算（仅供与 r2_b_out.txt 逐项对拍）。

    注意：该子集构造的动机是 (L1)「y_j = 1 不可行」成立时的约简；E10 档判据为 False
    （等号），故本节不构成 (L1) 无关证据，本档的承重结论以全穷举为准。
    """
    found = {}
    notes = []
    cons = rc.constraint_list(m2, d, W)
    chain = cons[m2:2 * m2]
    sumc = cons[2 * m2]
    for j in range(m2):
        rows = [chain[i][0] for i in range(m2) if i != j] + [sumc[0]]
        b = [chain[i][1] for i in range(m2) if i != j] + [sumc[1]]
        sol, rank = rc.solve_exact(rows, b)
        if sol is None or rank < m2:
            notes.append(f"    子集 j={j}（去掉链 {j+1}）：无唯一解（秩 {rank}）")
            continue
        ok, bad = rc.feasible(sol, m2, d, W)
        if ok:
            found[tuple(sol)] = j
        else:
            notes.append(f"    子集 j={j}：解不可行 {bad[:2]}")
    rows = [c[0] for c in chain]
    b = [c[1] for c in chain]
    sol, rank = rc.solve_exact(rows, b)
    zero = sol is not None and all(t == 0 for t in sol)
    notes.append(f"    「{m2} 条链约束全取等」（无和约束）：唯一解 = {'零向量' if zero else sol}（秩 {rank}）")
    rows_all = [c[0] for c in chain] + [sumc[0]]
    b_all = [c[1] for c in chain] + [sumc[1]]
    sol2, rank2 = rc.solve_exact(rows_all, b_all)
    notes.append(f"    「{m2} 条链约束全取等 + 和约束」（勘误 :63 的逐字等式读法）："
                 f"{'不相容（无解）' if sol2 is None else '有解 ' + str(sol2[:2])}（增广秩 {rank2}）")
    return found, notes


def arm_C():
    hdr("route-1 对照丙（边界）：E10（m2 = 5，δ = D_LO7，W = (δ^5−1)/(δ−1)，阈值上等号 v = 1）")
    if not gate():
        say("    冻结门未过，本档终止。")
        return
    r2j = load_frozen_r2j()
    dlo, dhi = delta_anchor()
    m2 = 5
    W = (dlo ** m2 - 1) / (dlo - 1)
    thr = (dlo ** m2 - 1) / (dlo - 1)
    v = rc.v_vertex(m2, dlo, W)
    say(f"    参数：m2 = {m2}；δ = {dlo}（下界；上界 = {dhi}）")
    say(f"    W = (δ^5−1)/(δ−1) = {W}")
    say(f"    阈值 (δ^5−1)/(δ−1) = {thr}（与 W 逐字同一分数；W > 阈值 = {W > thr}，即等号）")
    say(f"    阈值位数 = {thr.numerator.bit_length()} 位分子 / {thr.denominator.bit_length()} 位分母")
    say(f"    v = W(δ−1)/(δ^m2−1) 的分子位数 = {v.numerator.bit_length()}，分母位数 = {v.denominator.bit_length()}（v = {v}）")
    chk("W 串 = 630347359154513105681/40960000000000000000（对照 r2_b_out.txt:93）",
        str(W) == "630347359154513105681/40960000000000000000", f"实测 {W}")
    chk("阈值位数 = 70 位分子 / 66 位分母（对照 r2_b_out.txt:93）",
        (thr.numerator.bit_length(), thr.denominator.bit_length()) == (70, 66),
        f"实测 {(thr.numerator.bit_length(), thr.denominator.bit_length())}")
    chk("v = 1 精确（位数 1/1，对照 r2_b_out.txt:92）",
        v == 1 and (v.numerator.bit_length(), v.denominator.bit_length()) == (1, 1), f"实测 v = {v}")
    chk("(L1) 判据 (δ^5−1)/(δ−1) < W = False（阈值上的边界，对照 r2_b_out.txt:93）", (thr < W) is False)
    say("    调用冻结 full_enumeration(m2, δ_lo, W)：")
    verts, total, dt = r2j.full_enumeration(m2, dlo, W)
    analytic = {tuple(rc.vertex(m2, dlo, W, r)) for r in range(m2)}
    same = set(verts.keys()) == analytic
    say(f"    子集总数 C(11,5) = {total}，用时 {dt:.3f} s")
    say(f"    可行顶点数 = {len(verts)}；与解析的 m2 = {m2} 个循环旋转相同 = {same}（解析集大小 {len(analytic)}）")
    certs = sorted({r2j.active_rank(y, m2, dlo, W) for y in verts})
    say(f"    每个顶点的（活跃约束法向量秩，活跃约束条数）= {certs}")
    chk("子集总数 = C(11,5) = 462（对照 r2_b_out.txt:98 的「462 个子集」）",
        total == math.comb(11, 5) == 462, f"实测 {total}")
    chk("顶点数 = 5 且顶点集与解析旋转集相等（对照 r2_b_out.txt:98）",
        len(verts) == 5 and same and len(analytic) == 5, f"实测 顶点 {len(verts)} / 相等 {same}")
    chk("证书 = [(5, 6)]（对照 r2_b_out.txt:97）", certs == [(5, 6)], f"实测 {certs}")
    say("    五个顶点（精确分数，按坐标排序）：")
    for y in sorted(verts):
        say(f"      {y}；命中子集 = {[cons_name(i, m2) for i in verts[y]]}；活跃约束 = "
            f"{[cons_name(i, m2) for i in active_idx(y, m2, dlo, W)]}")
    say("  附：r2_b 口径复算（仅供与 r2_b_out.txt E10 段逐项对拍；其构造动机含 (L1)，见函数注释）：")
    found, notes = reduced_enumeration_notes(m2, dlo, W)
    for nline in notes:
        say(nline)
    say(f"    约简穷举：唯一可行顶点数 = {len(found)}；与解析的 m2 个循环旋转相同 = "
        f"{set(found.keys()) == analytic}（解析集大小 {len(analytic)}）")
    chk("约简复算的顶点集与全穷举一致", set(found.keys()) == set(verts.keys()),
        f"约简 {len(found)} 个 / 全穷举 {len(verts)} 个")
    chk("结构注 1 含「零向量」与「秩 5」（对照 r2_b_out.txt:95）",
        ("零向量" in notes[0]) and ("秩 5" in notes[0]), notes[0])
    chk("结构注 2 含「不相容（无解）」与「增广秩 5」（对照 r2_b_out.txt:96）",
        ("不相容（无解）" in notes[1]) and ("增广秩 5" in notes[1]), notes[1])


# ------------------------------------------------------- 附：八核分片复算（m2 = 10）

def partition_worker(job):
    start, end, m2, d, W, n = job
    cons = rc.constraint_list(m2, d, W)
    t0 = time.time()
    found = {}
    seen = 0
    for S in islice(combinations(range(n), m2), start, end):
        seen += 1
        rows = [cons[i][0] for i in S]
        b = [cons[i][1] for i in S]
        sol, rank = rc.solve_exact(rows, b)
        if sol is None or rank < m2:
            continue
        ok, _ = rc.feasible(sol, m2, d, W)
        if ok:
            found[tuple(sol)] = S
    return (start, end, seen, time.time() - t0, found)


def arm_P():
    hdr("route-1 附（并行外壳）：m2 = 10，八核分片复算（同一冻结判定函数；不替代对照甲）")
    if not gate():
        say("    冻结门未过，本档终止。")
        return
    m2, W, n = 10, Fraction(2000), 21
    dlo, _ = delta_anchor()
    total = math.comb(n, m2)
    nw = os.cpu_count() or 8
    bounds = [round(i * total / nw) for i in range(nw + 1)]
    say(f"    参数：m2 = {m2}；δ = {dlo}；W = {W}；子集总数 = {total}；分片数 = {nw}")
    say(f"    子集编号 = itertools.combinations(range({n}), {m2}) 的字典序编号；分片边界 = {bounds}")
    jobs = [(bounds[i], bounds[i + 1], m2, dlo, W, n) for i in range(nw)]
    ctx = multiprocessing.get_context("spawn")
    t0 = time.time()
    with ctx.Pool(nw) as pool:
        results = pool.map(partition_worker, jobs)
    wall = time.time() - t0
    union = {}
    seen_tot = 0
    for k, (start, end, seen, dt, found) in enumerate(results):
        seen_tot += seen
        say(f"    片 {k}：子集编号 [{start}, {end})，计 {seen} 个（应 {end - start}），"
            f"用时 {dt:.1f} s，命中顶点 {len(found)}")
        for y, S in found.items():
            union[y] = S
    analytic = {tuple(rc.vertex(m2, dlo, W, r)) for r in range(m2)}
    chk("各片计数之和 = 352716（无重无漏的计数口径）", seen_tot == total, f"实测 {seen_tot}")
    chk("每片计数 = 该片编号区间长度", all(r[2] == r[1] - r[0] for r in results))
    chk("八片并集 = 解析旋转集（与单核口径同一结果）", set(union.keys()) == analytic,
        f"并集 {len(union)} 个 / 解析 {len(analytic)} 个")
    dup = sum(len(r[4]) for r in results) - len(union)
    say(f"    跨片重复命中的顶点条数 = {dup}（每个顶点的命中子集不全同片时会 > 0）")
    inner = sum(r[3] for r in results)
    per = 1000 * inner / total
    say(f"    片内用时之和 = {inner:.1f} s；每子集片内毫秒 = {per:.4f}；并行墙钟（含池启动）= {wall:.1f} s")


# ------------------------------------------------------- 附：成本抽样测速（m2 = 12 等）

def arm_S():
    hdr("route-1 附（成本抽样）：均匀随机子集测速（仅作投影，非判定、非穷举）")
    if not gate():
        say("    冻结门未过，本档终止。")
        return
    dlo, _ = rc.delta_rigorous_bounds(10 ** 7)
    W = Fraction(2000)
    det = rc.Det(20261027)
    say(f"    参数：δ = {dlo}；W = {W}；抽样器 = r2_common.Det(20261027)（确定性，部分 Fisher 与 Yates）")

    def rand_subset(n, k):
        pool = list(range(n))
        for i in range(k):
            j = i + det.below(n - i)
            pool[i], pool[j] = pool[j], pool[i]
        return sorted(pool[:k])

    N = 2000
    for m2 in (10, 12, 13, 14):
        n = 2 * m2 + 1
        cons = rc.constraint_list(m2, dlo, W)
        t0 = time.time()
        hits = 0
        for _ in range(N):
            S = rand_subset(n, m2)
            rows = [cons[i][0] for i in S]
            b = [cons[i][1] for i in S]
            sol, rank = rc.solve_exact(rows, b)
            if sol is None or rank < m2:
                continue
            ok, _ = rc.feasible(sol, m2, dlo, W)
            if ok:
                hits += 1
        dt = time.time() - t0
        per = dt / N * 1000
        tot = math.comb(n, m2)
        say(f"    m2 = {m2}：{N} 个均匀随机子集，用时 {dt:.3f} s，每子集 {per:.4f} ms；"
            f"C({n},{m2}) = {tot}；单核投影 = {per * tot / 1000 / 60:.1f} min")
    say("    说明：本节只测单子集判定成本，不构成任何档位的顶点判定或穷举结论。")


if __name__ == "__main__":
    which = (sys.argv[1].upper() if len(sys.argv) > 1 else "A")
    t_start = time.time()
    say(f"route-1 三向对照基线驱动；模式 = {which}；启动时间 = {time.strftime('%Y-%m-%d %H:%M:%S')}")
    if which == "A":
        arm_A()
    elif which == "B":
        arm_B()
    elif which == "C":
        arm_C()
    elif which == "P":
        arm_P()
    elif which == "S":
        arm_S()
    else:
        say(f"未知模式：{which}")
        sys.exit(2)
    p, f = _COUNT["pass"], _COUNT["fail"]
    say(f"本进程检查汇总：PASS = {p}，FAIL = {f}；总用时 {time.time() - t_start:.1f} s")
    if f:
        say("!! 存在 FAIL 项：本档不进闸门，先定位。")
    sys.exit(1 if f else 0)
