#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vertex-tail 第 1 轮「复算员轮次」的逐条增量复算闸门（七条增量，断言组 C1 至 C7）。

本文件只做一件事：把本轮七条增量结论各自写成一个断言函数，全部自己重新计算。
不读取任何 route-*.md 与 materials.md 里的数字；唯一读到的报告级文本是本轨道的
账本条目 ledger-note.md（C7 只核其结构与「它与现行产物是否一致」，其中每个数字都
另与本文件复算或原始产物对照）。

一句话口径
    「全量判定为真」在本文件里一律拆成三件可执行的事：判串逐字节直方图由本文件自数、
    检查点分片与证书由本文件自算、两实现在同构量上与本文件自写内核对照。
    凡报告级措辞（例如某文件 docstring 的用词）只按源码逐字核对，不引申。

默认档（不加参数）覆盖什么
    C1 至 C7 全部断言。其中数值重算共 864 个子集：
      m₂ = 2 全量 10 个、m₂ = 5 全量 462 个、m₂ = 10 两区块 40 个、
      m₂ = 12 四区块 352 个、m₂ = 14 尾块 14 个；
    另加五份判串的逐字节直方图（约 103 MB 逐字节计数与 'F' 位置扫描）、
    13 套检查点的分片关系与（活跃秩, 活跃条数）证书、
    七份 Python 参考分片与 C 判串同区间的逐字节对照、
    两实现类别盲区实证 40 个子集（需要 gmpy2，见下「环境」）、
    三份闸门注册产物的身份与计数、δ 严格下界锚点的整数幂重算（3^10^7）。

深度档（--deep）追加什么
    D1 m₂ = 10 全量 352716 个子集的自写重算（逐字节对判串，含 Bareiss 整数行列式预筛）；
    D2 重跑 scripts/recon_evidence_chain.py 并逐字节对照注册产物（墙钟约三分钟）；
    D3 重跑 scripts/check_ledger_note.py，核对「58 项」总数关系、退出码与 FAIL 数的一致性，并如实报告实况：
       该检查器把共享 ledger.md 与 learnings.md 的 md5 与行号一并冻结，而这两件文件在 2026 年 10 月 29 日
       06:22 至 06:23 被合并改写（晚于其注册产物），故现在跑出 FAIL = 4（H6、H7、I15、I16），退出码 1；
       D3 断言的是「失败项全部落在两件共享文件的漂移上、且两件文件的 mtime 晚于注册产物」；
    D4 重跑上轮闸门的字节快照 prev_round_verify.py.txt，并如实报告实况：该闸门的登记表冻结于
       2026 年 10 月 28 日 23:55，其中两件共享文件（70-research/ledger.md 与 learnings.md）其后被
       合并改写，故现在只跑得出 41 条 PASS 加 1 条 FAIL（S1.1 底本身份），不再可能复跑成全绿；
       D4 断言的是「42 条判据的总数关系成立、唯一失败项是 S1.1、且它点名这两件共享文件」。
    scripts/verify.py（38 条）很便宜，已在默认档实跑，深度档不重复。

明确不复算
    m₂ = 12、13、14 的全量（5200300、20058300、77558760 个子集）；m₂ ≥ 15 无任何落盘产物。

环境
    两实现（route3_defs、route3_impl1_mpqscan、route3_impl2_struct）需要 gmpy2。C1.5 按三级
    走：① 当前解释器自带 gmpy2 就地跑；② 实测能 import gmpy2 的候选解释器（先按真路径解析
    本文件位置再按标记上溯，最后补绝对常量兜底）以子进程跑本文件的 --blindspot-worker；
    ③ 都不可用时改走替身引擎（把 gmpy2 换成等价模块 mpz=int、mpq=Fraction；精确有理语义
    不变，本机实测其 40 行判定与 gmpy2 2.3.2 逐行相同），并在该条输出里如实标出引擎。
    为什么要测而不是只查文件存在：本机存在 collatz-attack/collatz-attack/ 嵌套布局，其
    70-research 是指向真目录的符号链接、其 20-experiments/.venv/bin/python 是符号链接但
    该 .venv 下没有 pyvenv.cfg，跑起来是裸解释器、没有 gmpy2；按「本文件路径上溯四级」取根
    会正好踩到这个假 venv（第 1 轮就是因此失败），故候选解释器一律实测。

纪律
    1. 真值只用本文件自写的 lex 编号、整数行列式、精确有理消元与秩。两实现只在 C1.5 里
       作为「被检验对象」被调用，不用作真值来源。
    2. 无法机器验证的项在代码注释里写明并跳过，例如：route-2.md:69、route-5.md:92 与 :100
       等处的逐字引文（按纪律不读 route-*.md）、以及「漂移登记行号一处错（见 falsified）」
       所依据的 falsified 清单本身（不在本轮材料内）。
    3. 前轮闸门（原 cycle-1/verify.py，md5 151d3023b53de9130bc5694ae81de0bb）已被本文件
       取代：其字节快照留在同目录 prev_round_verify.py.txt（md5 相同，C3.1 与 D4 核对），
       其注册 stdout 留在 results/verify.out。

运行
    python3 verify.py                 默认档：全部 PASS 退出码 0；任一 FAIL 退出码 1 并打印最小反例
    python3 verify.py --deep          默认档加深度档
    python3 verify.py --force-shim    诊断用：强制 C1.5 走替身引擎（用于验证无 gmpy2 时的退路）
    python3 verify.py --blindspot-worker   内部用：给 C1.5 打 JSON 的单区块工作模式（不经用户调用）
"""

import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from fractions import Fraction
from importlib.util import find_spec
from itertools import combinations
from math import comb, gcd

HERE = os.path.dirname(os.path.abspath(__file__))
CYCLE = os.path.dirname(HERE) if os.path.basename(HERE) == "scripts" else HERE
TAIL = os.path.dirname(CYCLE)                 # tracks/vertex-tail（本轨道根目录）
REPO = os.path.abspath(os.path.join(CYCLE, "..", "..", "..", ".."))
M12 = os.path.join(REPO, "70-research", "tracks", "vertex-m12", "cycle-1")
R2 = os.path.join(M12, "scripts", "results", "route2")
CKPT = os.path.join(M12, "results", "ckpt")
MRES = os.path.join(M12, "results")
VSCRIPTS = os.path.join(CYCLE, "scripts")
VRES = os.path.join(CYCLE, "results")
OWN = os.path.abspath(__file__)
SNAPSHOT = os.path.join(CYCLE, "prev_round_verify.py.txt")
FORCE_SHIM = False    # 仅由 --force-shim 置真：强制 C1.5 走替身引擎，供诊断与自测

DELTA = Fraction(126797, 80000)          # δ 的严格下界（其身份由 C1.7 用整数幂现场重算）
W2000 = Fraction(2000)
W5 = (DELTA ** 5 - 1) / (DELTA - 1)      # m₂ = 5 边界档阈值（使 v = 1）
D2DELTA, D2W = Fraction(3, 2), Fraction(3, 2)   # m₂ = 2 阴性档参数

DEC = {
    "c_m10_t8": "c_m10_t8_decisions.txt",
    "c_m10_t1": "c_m10_t1_decisions.txt",
    "py_m10": "py_m10_decisions.txt",
    "c_m12_t8": "c_m12_t8_decisions.txt",
    "c_m13_t8": "c_m13_t8_decisions.txt",
    "c_m14_t8": "c_m14_t8_decisions.txt",
    "m5_e10": "m5_e10_decisions.txt",
}
# 各档参数（只用于自写内核；产物自带的参数写法在 C1.6 逐处核对）
TIER = {"m2": (2, D2DELTA, D2W), "m5": (5, DELTA, W5), "m10": (10, DELTA, W2000),
        "m12": (12, DELTA, W2000), "m13": (13, DELTA, W2000), "m14": (14, DELTA, W2000)}

STATE = {"n": 0, "fails": []}


def rec(cid, ok, detail, counter=None):
    """记录一条断言。失败时把最小反例存起来，结尾统一打印。"""
    STATE["n"] += 1
    print("[%s] %-5s %s" % ("PASS" if ok else "FAIL", cid, detail))
    if not ok:
        STATE["fails"].append((cid, counter if counter is not None else detail))
    return ok


def md5f(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


# ===========================================================================
# 自写内核：组合编号、整数行列式、精确有理消元、可行性、证书、解析族
# ===========================================================================
def unrank(n, r, k):
    """n 元集合上 r 元子集的字典序（组合序）0 基编号 k 反查。"""
    c, a, x = [], 0, k
    for i in range(r):
        for cand in range(a, n):
            cnt = comb(n - cand - 1, r - i - 1)
            if x < cnt:
                c.append(cand)
                a = cand + 1
                break
            x -= cnt
    return c


def rank_lex(c, n, r):
    """严格递增的 r 元子集 c（元素取自 0 至 n−1）的字典序 0 基编号。"""
    rk, prev = 0, -1
    for i, x in enumerate(c):
        for j in range(prev + 1, x):
            rk += comb(n - 1 - j, r - 1 - i)
        prev = x
    return rk


def rows_int(m, delta, W):
    """2m + 1 条约束，整系数放大：C1_j 为 y_j ≥ 1，C2_j 为 δ y_j − y_{j+1} ≥ 0（末条回绕），
    C3 为 Σy ≥ W。返回 [(row, rhs)]，行列式口径因此全程整数。"""
    p, q = delta.numerator, delta.denominator
    wn, wd = W.numerator, W.denominator
    cons = []
    for j in range(m):
        row = [0] * m
        row[j] = q
        cons.append((row, q))
    for j in range(m):
        row = [0] * m
        row[(j + 1) % m] = q
        row[j] -= p
        cons.append((row, 0))
    cons.append(([q * wd] * m, q * wn))
    return cons


def det_bareiss(A):
    """Bareiss 分数无关整数消元；精确整数行列式（det = 0 当且仅当无唯一解）。"""
    n = len(A)
    if n == 0:
        return 1
    M = [row[:] for row in A]
    sign, prev = 1, 1
    for k in range(n - 1):
        if M[k][k] == 0:
            piv = None
            for i in range(k + 1, n):
                if M[i][k] != 0:
                    piv = i
                    break
            if piv is None:
                return 0
            M[k], M[piv] = M[piv], M[k]
            sign = -sign
        for i in range(k + 1, n):
            mi, mk = M[i], M[k]
            for j in range(k + 1, n):
                mi[j] = (mi[j] * mk[k] - mi[k] * mk[j]) // prev
            mi[k] = 0
        prev = M[k][k]
    return sign * M[n - 1][n - 1]


def solve_exact(A, b, n):
    """精确有理高斯若尔当；无唯一解（秩亏）返回 None。"""
    M = [[Fraction(A[i][j]) for j in range(n)] + [Fraction(b[i])] for i in range(n)]
    rank, where = 0, [-1] * n
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
    return tuple(M[where[j]][n] for j in range(n))


def classify(S, m, cons, delta, W, prescreen=True):
    """自写判定：'S' 无唯一解、'I' 唯一解但不可行、'F' 唯一解且可行（即顶点候选）。
    返回 (tag, y, conflict)；conflict 计数「整数行列式非零却解不出」的异常（应恒 0）。"""
    A = [cons[s][0] for s in S]
    b = [cons[s][1] for s in S]
    if prescreen and det_bareiss(A) == 0:
        return "S", None, 0
    y = solve_exact(A, b, m)
    if y is None:
        return "S", None, 1
    for j in range(m):
        if y[j] < 1:
            return "I", None, 0
    for j in range(m):
        if y[(j + 1) % m] > delta * y[j]:
            return "I", None, 0
    if sum(y) < W:
        return "I", None, 0
    return "F", y, 0


def active_cert(y, cons, m):
    """（活跃约束法向量的秩, 活跃约束条数）；活跃 = 取等。"""
    act = [row for row, rhs in cons if sum(Fraction(row[k]) * y[k] for k in range(m)) == rhs]
    return rank_int(act, m), len(act)


def rank_int(rows, ncols):
    """整数行矩阵在 Q 上的秩（按 gcd 归一化控制规模）。"""
    M = [row[:] for row in rows]
    nr, r = len(M), 0
    for c in range(ncols):
        piv = None
        for i in range(r, nr):
            if M[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        pr = M[r]
        for i in range(r + 1, nr):
            if M[i][c] != 0:
                a, b = M[i][c], pr[c]
                g = gcd(abs(a), abs(b))
                f1, f2 = b // g, a // g
                M[i] = [f1 * M[i][j] - f2 * pr[j] for j in range(ncols)]
        r += 1
        if r == nr:
            break
    return r


def analytic_set(m, delta, W):
    """解析族：v · δ^((r + i) mod m)（逐坐标精确有理数）。"""
    v = W * (delta - 1) / (delta ** m - 1)
    return {tuple(v * delta ** ((r + i) % m) for i in range(m)) for r in range(m)}


def scan_dec(data):
    """逐字节直方图与 'F' 位置（自数，不读任何报告）。F 位置用 find 循环，避免百万级
    Python 层迭代拖慢墙钟。"""
    nS, nI, nF = data.count(83), data.count(73), data.count(70)
    fpos, start = [], 0
    while True:
        i = data.find(70, start)
        if i < 0:
            break
        fpos.append(i)
        start = i + 1
    return {"bytes": len(data), "S": nS, "I": nI, "F": nF,
            "other": len(data) - nS - nI - nF, "F_pos": fpos}


_DEC_CACHE = {}


def dec(name):
    if name not in _DEC_CACHE:
        _DEC_CACHE[name] = read_bytes(os.path.join(R2, DEC[name]))
    return _DEC_CACHE[name]


def scan(name):
    return scan_dec(dec(name))


def blocks_hist(m, blocks, deckey):
    """自写内核逐子集重算一串区块；返回 (直方图, 逐点解, 不一致表, 冲突数, 总数)。"""
    cons = rows_int(m, *TIER["m%d" % m][1:])
    delta, W = TIER["m%d" % m][1:]
    data = dec(deckey)
    dist = {"S": 0, "I": 0, "F": 0}
    fpts, bad, conflict, ntot = {}, [], 0, 0
    for lo, hi in blocks:
        for k in range(lo, hi):
            tag, y, cf = classify(tuple(unrank(2 * m + 1, m, k)), m, cons, delta, W)
            dist[tag] += 1
            conflict += cf
            ntot += 1
            if tag != chr(data[k]):
                bad.append((k, tag, chr(data[k])))
            if tag == "F":
                fpts[k] = y
    return dist, fpts, bad, conflict, ntot


def ckpt_dirs():
    return sorted(d for d in os.listdir(CKPT) if os.path.isdir(os.path.join(CKPT, d)))


def load_ckpt(name):
    files = sorted(glob.glob(os.path.join(CKPT, name, "chunk_*.json")))
    shards = [json.load(open(f, encoding="utf-8")) for f in files]
    keys = {}
    for sh in shards:
        for k, v in sh["feasible"].items():
            keys[k] = v
    return files, shards, keys


def keys_as_points(keys):
    return {tuple(Fraction(x) for x in k.split(",")) for k in keys}


# ===========================================================================
# C1：S2 措辞更正与盲区铭牌（增量 1）
# ===========================================================================
XCHECK = os.path.join(M12, "scripts", "route3_xcheck.py")
IMPL1 = os.path.join(M12, "scripts", "route3_impl1_mpqscan.py")
IMPL2 = os.path.join(M12, "scripts", "route3_impl2_struct.py")
XCHECK_JSON = {"m10": "route3_xcheck_m10_allsubsets.json",
               "m12": "route3_xcheck_m12_allsubsets.json"}


SHIM_LABEL = "替身（mpz=int、mpq=Fraction）"


def blindspot_payload():
    """给 C1.5 打 JSON 的工作模式：只调用两实现（被检验对象），不做任何真值判定。
    需要 gmpy2（真 gmpy2 或替身模块，见 blindspot_with_shim）。"""
    sys.path.insert(0, os.path.join(M12, "scripts"))
    import gmpy2
    import route3_defs as RD
    import route3_impl1_mpqscan as I1
    import route3_impl2_struct as I2

    # 参数直接取 route3_defs 的冻结常量（δ 的整数幂锚点由本文件 C1.7 自算，不依赖被检对象）
    delta = Fraction(RD.DELTA_P, RD.DELTA_Q)
    W = RD.W_FROZEN
    p, q = delta.numerator, delta.denominator
    wn, wd = W.numerator, W.denominator
    out = {"engine": gmpy2.version(), "delta": str(delta), "W": str(W),
           "python": sys.version.split()[0], "blocks": []}
    for m, lo, hi in ((10, 352696, 352716), (12, 2570000, 2570020)):
        data = dec("c_m%d_t8" % m)
        cons = RD.constraint_rows(m, delta, W)
        pmq, qmq = I1.mpq(p), I1.mpq(q)
        dpow = [delta ** k for k in range(-m, m + 1)]
        rows = []
        for rank in range(lo, hi):
            S = tuple(unrank(2 * m + 1, m, rank))
            k1, c1, p1, _a1 = I1.judge_subset(S, cons, m, pmq, qmq, I1.mpq(wn), I1.mpq(wd))
            k2, c2, p2, _a2, _fr = I2.judge_struct(S, m, dpow, p, q, wn, wd, None)
            ok = (p1 == p2) and (c1 == c2)          # 与 route3_xcheck.py:54 逐字同式
            rows.append({"rank": rank, "byte": chr(data[rank]), "k1": k1, "c1": int(c1),
                         "p1": p1, "k2": k2, "c2": int(c2), "p2": p2, "ok": bool(ok)})
        out["blocks"].append({"m2": m, "lo": lo, "hi": hi, "rows": rows})
    return out


def blindspot_with_shim():
    """替身引擎：把 gmpy2 换成等价模块（mpz=int、mpq=Fraction）后导入两实现。
    只在当前解释器与所有候选解释器都缺 gmpy2 时使用；精确有理语义与 gmpy2.mpq 相同，
    故两实现的判定结果不变（本机实测：替身与 gmpy2 2.3.2 的 40 行判定逐行相同）。"""
    import types
    shim = types.ModuleType("gmpy2")
    shim.mpz = int
    shim.mpq = Fraction
    shim.version = lambda: SHIM_LABEL
    sys.modules["gmpy2"] = shim
    try:
        return blindspot_payload()
    finally:
        sys.modules.pop("gmpy2", None)


def root_candidates():
    """候选仓库根。本机存在 collatz-attack/collatz-attack/ 这类嵌套布局（内层 70-research 是
    指向真目录的符号链接、内层 20-experiments/.venv 只有一个没有 pyvenv.cfg 的假 bin），
    若只按「本文件路径上溯四级」取根，会拿到那个假 venv，故先按真路径解析、再按标记上溯，
    最后补一个绝对常量兜底。"""
    cands = []
    for base in (os.path.dirname(os.path.realpath(OWN)), HERE, TAIL):
        cur = base
        for _ in range(6):
            if (os.path.isdir(os.path.join(cur, "70-research"))
                    and os.path.isdir(os.path.join(cur, "20-experiments"))):
                if cur not in cands:
                    cands.append(cur)
                break
            nxt = os.path.dirname(cur)
            if nxt == cur:
                break
            cur = nxt
    lit = os.path.join(os.path.expanduser("~"), "Documents", "math IA", "collatz-attack")
    if lit not in cands:
        cands.append(lit)
    return cands


def gmpy2_python():
    """返回 (解释器路径, 版本串) 或 (None, None)：候选必须实测能 import gmpy2 才算数
    （只查文件存在会踩到上面说的假 venv：它的 python 符号链接指向真解释器，但没有
    pyvenv.cfg，跑起来是裸解释器，没有 gmpy2）。"""
    for root in root_candidates():
        py = os.path.join(root, "20-experiments", ".venv", "bin", "python")
        if not os.path.exists(py):
            continue
        try:
            r = subprocess.run([py, "-c", "import gmpy2; print(gmpy2.version())"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, timeout=600)
        except Exception:
            continue
        if r.returncode == 0 and r.stdout.strip():
            return py, r.stdout.strip()
    return None, None


def run_blindspot(force_shim=False):
    """返回 (payload, 说明)。优先级：当前解释器自带 gmpy2 → 实测定出的带 gmpy2 候选解释器
    子进程 → 替身引擎（并如实标出用的是替身）。"""
    if not force_shim and find_spec("gmpy2") is not None:
        return blindspot_payload(), "就地（当前解释器 %s 自带 gmpy2）" % sys.version.split()[0]
    if not force_shim:
        py, ver = gmpy2_python()
        if py:
            r = subprocess.run([py, OWN, "--blindspot-worker"], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, timeout=1800)
            if r.returncode == 0 and r.stdout.strip():
                return (json.loads(r.stdout.strip().splitlines()[-1]),
                        "子进程（%s，gmpy2 %s）" % (py, ver))
    return blindspot_with_shim(), "替身引擎（本机与候选解释器都缺 gmpy2 或调用了 --force-shim）"


def check_c1():
    print("== 增量 1：S2 措辞更正与盲区铭牌 ==")
    xc = read_text(XCHECK).splitlines()
    l54 = xc[53].strip()
    rec("C1.1", l54 == "ok = (p1 == p2) and (c1 == c2)",
        "对拍判据逐字：route3_xcheck.py 第 54 行 strip 后 == 「ok = (p1 == p2) and (c1 == c2)」",
        counter="route3_xcheck.py:54 = %r" % l54)
    doc_span = (xc[6].strip(), xc[7].strip())
    has_phrase = "kind、候选点串、判定码" in xc[7]
    rec("C1.2", has_phrase and "逐项比较实现一" in xc[6],
        "该文件 docstring 自称比较「kind、候选点串、判定码」：证据句起于第 7 行（「逐项比较实现一（mpq 消元）与实现二（结构传播）」）、"
        "「kind、候选点串、判定码」字样在第 8 行；判据实际只比候选点串与判定码，故该措辞对 kind 属夸大（C1.5 给出实测）",
        counter="docstring 第 7 至 8 行 = %r / %r" % doc_span)
    keys = []
    for k, fn in XCHECK_JSON.items():
        keys.append(set(json.load(open(os.path.join(MRES, fn), encoding="utf-8")).keys()))
    want = {"m2", "lo", "hi", "n_compare", "n_mismatch", "n_candidates_impl1",
            "n_candidates_impl2", "first_mismatches"}
    rec("C1.3", keys[0] == want and keys[1] == want,
        "对拍落盘 JSON 字段集 == 8 个（%s），不含任何 kind 或分检计数字段，故类别差异在落盘层结构性不可见"
        % "、".join(sorted(want)), counter="实测字段集 %s" % sorted(keys[0] ^ want))
    i1 = read_text(IMPL1).splitlines()
    i2 = read_text(IMPL2).splitlines()
    want1 = [(105, 'return "singular", 0, None, 0'), (108, 'return "infeasible", 0, None, 0'),
             (111, 'return "infeasible", 0, None, 0'), (116, 'return "infeasible", 0, None, 0')]
    got1 = [(n + 1, i1[n].strip()) for n in range(len(i1)) if ", 0, None, 0" in i1[n]]
    noc = [(n + 1, i2[n].strip()) for n in range(len(i2)) if "nocand" in i2[n]]
    ret2 = [(n, s) for n, s in noc if s.startswith('return "nocand"')]
    want2 = [102, 113, 132, 134, 146, 153, 156]
    ok_impl2 = [n for n, _ in ret2] == want2 and all(
        s.split("#")[0].strip() == 'return "nocand", 0, None, 0, False' for _, s in ret2)
    rec("C1.4", got1 == want1 and ok_impl2 and len(noc) == 8,
        "非候选分支恒 (None, 0) 的源码点：实现一 4 处（第 105 行 singular、第 108／111／116 行 infeasible），"
        "实现二返回点 7 处（第 102 至 156 行，全为 return \"nocand\", 0, None, 0, False）；"
        "「nocand」字样共 8 处（返回点 7 处加第 78 行 docstring 一处），故增量所写「共八处」按字样成立、按返回点为 7 处",
        counter="实现一 %s；实现二返回点 %s；nocand 字样 %s" % (got1[:2], [n for n, _ in ret2], [n for n, _ in noc]))
    try:
        payload, how = run_blindspot(force_shim=FORCE_SHIM)
        by_m = {b["m2"]: b for b in payload["blocks"]}
    except Exception as exc:
        payload, by_m, how = None, None, "未跑：%s: %s" % (type(exc).__name__, exc)
    det_rows, ok_rows, counter = [], True, None
    if payload is None:
        rec("C1.5", False, "类别盲区实证未跑成（%s）；本条为环境失败，不是结论被推翻" % how, counter=how)
    for m, lo, hi in ((10, 352696, 352716), (12, 2570000, 2570020)):
        rows = by_m[m]["rows"]
        npass = sum(1 for r in rows if r["ok"])
        kdiff = sum(1 for r in rows if r["k1"] != r["k2"])
        k1c, k2c = {}, {}
        for r in rows:
            k1c[r["k1"]] = k1c.get(r["k1"], 0) + 1
            k2c[r["k2"]] = k2c.get(r["k2"], 0) + 1
        noncand_zero = all(r["c1"] == 0 and r["c2"] == 0 for r in rows if r["p1"] is None or r["p2"] is None)
        cand_agree = all((r["p1"], r["c1"]) == (r["p2"], r["c2"]) for r in rows if r["p1"] is not None)
        ncand = sum(1 for r in rows if r["p1"] is not None)
        nF = sum(1 for r in rows if r["byte"] == "F")
        mine_ok = all(classify(tuple(unrank(2 * m + 1, m, r["rank"])), m,
                               rows_int(m, *TIER["m%d" % m][1:]), TIER["m%d" % m][1],
                               TIER["m%d" % m][2])[0] == r["byte"] for r in rows)
        want = (20, 10, {"infeasible": 10, "feasible": 10}, {"nocand": 10, "feasible": 10}) if m == 10 \
            else (20, 20, {"singular": 20}, {"nocand": 20})
        good = (npass == 20 and kdiff == want[1] and k1c == want[2] and k2c == want[3]
                and noncand_zero and cand_agree and ncand == nF and mine_ok)
        ok_rows = ok_rows and good
        if not good and counter is None:
            counter = ("m₂=%d 区块 [%d,%d)：判据通过 %d、kind 不同 %d、impl1 分布 %s、impl2 分布 %s、"
                       "非候选码全 0=%s、候选一致=%s、候选数=%d、'F' 数=%d、本文件真值全等=%s"
                       % (m, lo, hi, npass, kdiff, k1c, k2c, noncand_zero, cand_agree, ncand, nF, mine_ok))
        det_rows.append("m₂=%d [%d,%d)：判据 %d/20，kind 不同 %d，impl1 %s，impl2 %s"
                        % (m, lo, hi, npass, kdiff, k1c, k2c))
    if payload is not None:
        rec("C1.5", ok_rows,
            "类别盲区实证（%s；引擎 %s）：40 个子集上判据全通过而 kind 差异按块为 10 与 20；"
            "非候选侧两边判定码恒 0、候选侧点串与码两边相同；本文件自写内核在每个编号上与判串字节全等。%s"
            % (how, payload.get("engine"), "；".join(det_rows)), counter=counter)
    i1set = sorted({int(re.findall(r"route3_impl1_m(\d+)", os.path.basename(p))[0])
                    for p in glob.glob(os.path.join(MRES, "route3_impl1_m*.json"))})
    n1 = json.load(open(os.path.join(MRES, "route3_impl1_m10.json"), encoding="utf-8"))
    n2 = json.load(open(os.path.join(MRES, "route3_impl1_m12.json"), encoding="utf-8"))
    full1 = (n1["scanned_subsets"] == n1["total_subsets"] == comb(21, 10)
             and n2["scanned_subsets"] == n2["total_subsets"] == comb(25, 12))
    rec("C1.6", i1set == [10, 12] and full1,
        "覆盖止于 m₂ ≤ 12：results 下 route3_impl1 落点为 m ∈ %s，两件各自 scanned == total == C(2m+1,m) 成立；"
        "m₂ = 13、14 无实现一落点（无对拍可交）" % i1set, counter="落点 %s；全量字段 %s" % (i1set, full1))
    xpow = 3 ** (10 ** 7)
    ypow = 2 ** 15849625
    anchor = ypow < xpow < (ypow << 1)
    pfields = []
    for tag, fn in (("impl1_m10", "route3_impl1_m10.json"), ("impl1_m12", "route3_impl1_m12.json"),
                    ("impl2_m10", "route3_impl2_m10.json"), ("impl2_m12", "route3_impl2_m12.json"),
                    ("impl2_m13", "route3_impl2_m13.json"), ("impl2_m14", "route3_impl2_m14.json")):
        d = json.load(open(os.path.join(MRES, fn), encoding="utf-8"))
        if (d["delta"], d["W"]) != ("126797/80000", "2000/1"):
            pfields.append("%s:%s/%s" % (tag, d["delta"], d["W"]))
    logpar = []
    w5txt = "%d/%d" % (W5.numerator, W5.denominator)
    logwant = {10: "delta=126797/80000 W=2000/1", 12: "delta=126797/80000 W=2000/1",
               13: "delta=126797/80000 W=2000/1", 14: "delta=126797/80000 W=2000/1",
               5: "delta=126797/80000 W=" + w5txt}
    for m, need in logwant.items():
        fn = "m5_e10_log.txt" if m == 5 else "c_m%d_t8_log.txt" % m
        if need not in read_text(os.path.join(R2, fn)):
            logpar.append(fn)
    rec("C1.7", anchor and not pfields and not logpar,
        "参数锚点自证：整数幂序列上 2^15849625 < 3^10^7 < 2^15849626 成立（本文件现算，3^10^7 位长 %d），"
        "δ 严格下界身份因此与 126797/80000 一致；六份实现 JSON 的 delta／W 字段与五份判串日志的 PARAMS 行全部命中%s"
        % (xpow.bit_length(), "" if not (pfields or logpar) else "；不符 %s%s" % (pfields, logpar)),
        counter="锚点 %s；字段不符 %s；日志不符 %s" % (anchor, pfields, logpar))


# ===========================================================================
# C2：m₂ = 12 与 13 的「全量判定为真」可执行口径与边界（增量 2）
# ===========================================================================
def parse_log(fn):
    txt = read_text(os.path.join(R2, fn))
    out = {}
    mk = re.search(r"DECISION_COUNTS S=(\d+) I=(\d+) F=(\d+) total=(\d+)", txt)
    mc = re.search(r"CROSSCHECK compared=(\d+) sol_cmp=(\d+) mismatches=(\d+) mode=(\d+)", txt)
    out["parms"] = bool(re.search(r"PARAMS M=\d+ N=\d+ delta=126797/80000 W=2000/1", txt))
    if mk:
        out["S"], out["I"], out["F"], out["total"] = (int(g) for g in mk.groups())
    if mc:
        out["compared"], out["sol_cmp"], out["mismatches"], out["mode"] = (int(g) for g in mc.groups())
    out["sets_equal"] = "SETS_EQUAL True" in txt
    out["cross_full"] = "cross=full" in txt
    out["cross_alive"] = "cross=alive" in txt
    return out


def check_c2():
    print("== 增量 2：m₂ = 12、13 的口径与逐条边界 ==")
    g = parse_log("c_m12_t8_log.txt")
    sk = scan("c_m12_t8")
    ok = (g["S"], g["I"], g["F"], g["total"]) == (4752735, 447553, 12, 5200300) \
        and (g["compared"], g["sol_cmp"], g["mismatches"], g["mode"]) == (5200300, 447565, 0, 2) \
        and g["sets_equal"] and g["cross_full"] and g["sol_cmp"] == g["I"] + g["F"] == 447565
    rec("C2.1", ok,
        "m₂ = 12 日志口径：DECISION_COUNTS S/I/F/total = %s；CROSSCHECK compared=%d sol_cmp=%d mismatches=%d mode=%d；"
        "cross=full 且 compared == total；恒等式 sol_cmp == I + F == %d"
        % ((g["S"], g["I"], g["F"], g["total"]), g["compared"], g["sol_cmp"], g["mismatches"], g["mode"], g["I"] + g["F"]),
        counter="日志实测 %s" % g)
    rec("C2.2", (sk["bytes"], sk["S"], sk["I"], sk["F"], sk["other"]) == (5200300, 4752735, 447553, 12, 0),
        "m₂ = 12 判串自数：字节 %d、S/I/F = %d/%d/%d、非 S／I／F 字节 %d（与日志直方图同）"
        % (sk["bytes"], sk["S"], sk["I"], sk["F"], sk["other"]),
        counter="自数 %s" % {k: sk[k] for k in ("bytes", "S", "I", "F", "other")})
    h = parse_log("c_m13_t8_log.txt")
    sh = scan("c_m13_t8")
    ok2 = (h["S"], h["I"], h["F"], h["total"]) == (18811533, 1246754, 13, 20058300) \
        and (h["compared"], h["sol_cmp"], h["mismatches"], h["mode"]) == (1246767, 1246767, 0, 1) \
        and h["sets_equal"] and h["cross_alive"] \
        and h["compared"] == h["I"] + h["F"] == 1246767 \
        and h["total"] - h["compared"] == h["S"] == 18811533
    rec("C2.3", ok2,
        "m₂ = 13 日志口径：S/I/F/total = %s；CROSSCHECK compared=%d sol_cmp=%d mode=%d；cross=alive；"
        "恒等式 compared == I + F == %d 与 total − compared == S == %d 同时成立，"
        "即第二路覆盖非 'S' 全体、%d 个 'S' 只有第一路" % ((h["S"], h["I"], h["F"], h["total"]),
        h["compared"], h["sol_cmp"], h["mode"], h["I"] + h["F"], h["S"], h["S"]),
        counter="日志实测 %s" % h)
    rec("C2.4", (sh["bytes"], sh["S"], sh["I"], sh["F"], sh["other"]) == (20058300, 18811533, 1246754, 13, 0),
        "m₂ = 13 判串自数：字节 %d、S/I/F = %d/%d/%d、非 S／I／F 字节 %d（与日志直方图同）"
        % (sh["bytes"], sh["S"], sh["I"], sh["F"], sh["other"]),
        counter="自数 %s" % {k: sh[k] for k in ("bytes", "S", "I", "F", "other")})
    xs = sorted(json.load(open(os.path.join(MRES, fn), encoding="utf-8"))["m2"]
                for fn in glob.glob(os.path.join(MRES, "route3_xcheck_m*_allsubsets.json")))
    slices = [("py_m12_slice_a.txt", 12, 0, 60000), ("py_m12_slice_b.txt", 12, 2570000, 2630000),
              ("py_m12_slice_c.txt", 12, 5140000, 5200300), ("py_m13_slice_a.txt", 13, 0, 60000),
              ("py_m13_slice_b.txt", 13, 20000000, 20058300), ("py_m14_slice_a.txt", 14, 0, 40000),
              ("py_m14_slice_b.txt", 14, 77400000, 77558760)]
    cov = {12: 0, 13: 0, 14: 0}
    diff, ranges = [], {12: [], 13: [], 14: []}
    for fn, m, lo, hi in slices:
        b = read_bytes(os.path.join(R2, fn))
        cov[m] += len(b)
        ranges[m].append((lo, hi))
        if b != dec("c_m%d_t8" % m)[lo:hi] or len(b) != hi - lo:
            diff.append(fn)
    disj = all(all(ranges[m][i][1] <= ranges[m][i + 1][0] for i in range(len(ranges[m]) - 1))
               for m in ranges)
    pct = {m: round(100.0 * cov[m] / {12: 5200300, 13: 20058300, 14: 77558760}[m], 2) for m in cov}
    pm10 = read_bytes(os.path.join(R2, "py_m10_decisions.txt"))
    ok3 = (xs == [10, 12] and not diff and disj and pct == {12: 3.47, 13: 0.59, 14: 0.26}
           and pm10 == dec("c_m10_t8") and cov == {12: 180300, 13: 118300, 14: 198760})
    rec("C2.5", ok3,
        "随带边界：逐子集对拍产物只到 m₂ ∈ %s；Python 参考七片与 C 判串同区间逐字节相同、区间两两不交，"
        "覆盖 %d／%d／%d 字节即 %.2f%%／%.2f%%／%.2f%%；m₂ = 10 的 Python 参考为全量（判串逐字节同）"
        % (xs, cov[12], cov[13], cov[14], pct[12], pct[13], pct[14]),
        counter="对拍档 %s；逐字节不符 %s；区间不交 %s；百分比 %s" % (xs, diff, disj, pct))


# ===========================================================================
# C3：可复跑闸门群（增量 3）
# ===========================================================================
PREV_MD5 = "151d3023b53de9130bc5694ae81de0bb"
PREV_STDOUT_PREFIX_MD5 = "2ed1ebe87e36090c15b12a6a01c49294"
RECON_MD5 = "ad84e90bb259db263cf4220b852d7278"


def check_c3():
    print("== 增量 3：可复跑闸门群 ==")
    raw = read_bytes(os.path.join(VRES, "verify.out"))
    cut = raw.find("退出码 0\n".encode("utf-8"))
    pref = raw[:cut + len("退出码 0\n".encode("utf-8"))] if cut > 0 else raw
    npass, nfail = pref.count(b"[PASS]"), pref.count(b"[FAIL]")
    snap_ok = os.path.exists(SNAPSHOT) and md5f(SNAPSHOT) == PREV_MD5
    ok = (cut > 0 and hashlib.md5(pref).hexdigest() == PREV_STDOUT_PREFIX_MD5
          and npass == 42 and nfail == 0 and "判据共 42 条：PASS = 42，FAIL = 0".encode("utf-8") in pref
          and ("md5 = " + PREV_MD5).encode("utf-8") in raw[:400] and snap_ok)
    rec("C3.1", ok,
        "上轮闸门（已由本文件取代）的注册 stdout：results/verify.out 的正常模式前缀（截至首个「退出码 0」行，"
        "%d 字节）md5 == %s；前缀内 [PASS] %d、[FAIL] %d；文件头记载脚本 md5 == %s，同目录字节快照 "
        "prev_round_verify.py.txt 的 md5 与之相同（%s）"
        % (len(pref), PREV_STDOUT_PREFIX_MD5, npass, nfail, PREV_MD5, snap_ok),
        counter="cut=%d 前缀 md5=%s PASS=%d FAIL=%d 快照=%s"
                % (cut, hashlib.md5(pref).hexdigest(), npass, nfail, snap_ok))
    r = subprocess.run([sys.executable, os.path.join(VSCRIPTS, "verify.py")],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=900)
    reg = read_bytes(os.path.join(VRES, "verify.out.txt"))
    ok2 = r.returncode == 0 and r.stdout == reg and b"PASS=38 FAIL=0" in r.stdout
    rec("C3.2", ok2,
        "scripts/verify.py 实跑：退出码 %d，stdout 与注册产物 results/verify.out.txt 逐字节相同（%s），"
        "38 条 PASS、FAIL=0" % (r.returncode, len(reg)),
        counter="rc=%d；stdout %d 字节与注册 %d 字节同=%s" % (r.returncode, len(r.stdout), len(reg), r.stdout == reg))
    reco = read_text(os.path.join(VRES, "recon_evidence_chain.out.txt")).splitlines()
    npr = sum(1 for l in reco if l.startswith("PASS |"))
    nfr = sum(1 for l in reco if l.startswith("FAIL |"))
    rec_md5 = md5f(os.path.join(VRES, "recon_evidence_chain.out.txt"))
    ok3 = rec_md5 == RECON_MD5 and npr == 139 and nfr == 0 and "FAIL 总数 = 0" in "\n".join(reco)
    rec("C3.3", ok3,
        "scripts/recon_evidence_chain.py 的注册产物：md5 == %s、行首 PASS 行 139、FAIL 行 0、末段「FAIL 总数 = 0」"
        % RECON_MD5, counter="md5=%s PASS行=%d FAIL行=%d" % (rec_md5, npr, nfr))
    cln = read_text(os.path.join(VRES, "check_ledger_note.out"))
    ok4 = "58 项复算 + 耦合与结构；FAIL = 0" in cln and "退出码 0（全部通过）" in cln
    rec("C3.4", ok4,
        "scripts/check_ledger_note.py 的注册产物：汇总行「58 项复算 + 耦合与结构；FAIL = 0」与「退出码 0（全部通过）」均在"
        "（此为漂移前时刻的记录；现行实况见深度档 D3：共享 ledger.md 与 learnings.md 被改写后该检查器跑出 FAIL = 4）",
        counter="汇总行缺失或 FAIL 非零")
    idmap = {10: (["route3_impl1_m10.json", "route3_impl2_m10.json"], "m2_10_mpq"),
             12: (["route3_impl1_m12.json", "route3_impl2_m12.json"], "m2_12_mpq"),
             13: (["route3_impl2_m13.json"], "m2_13_mpq"),
             14: (["route3_impl2_m14.json"], "m2_14_mpq")}
    want_rng = {10: (352706, 352715), 12: (5200288, 5200299),
                13: (20058287, 20058299), 14: (77558746, 77558759)}
    det, ok5 = [], True
    for m, (impls, ckd) in idmap.items():
        fset = sorted(scan("c_m%d_t8" % m)["F_pos"])
        rk_impl = sorted({c["rank"] for fn in impls
                          for c in json.load(open(os.path.join(MRES, fn), encoding="utf-8"))["candidates"]})
        _f, _s, keys = load_ckpt(ckd)
        rk_ck = sorted({rank_lex(ex, 2 * m + 1, m) for v in keys.values() for ex in v["examples"]})
        good = fset == rk_impl == rk_ck and len(fset) == m and (fset[0], fset[-1]) == want_rng[m]
        ok5 = ok5 and good
        det.append("m₂=%d：%d 至 %d（%d 侧一致）" % (m, fset[0], fset[-1], 2 + len(impls)))
    rec("C3.5", ok5,
        "编号层逐侧一致（本文件自数 'F' 位置 == 可用实现候选编号 == 检查点 examples 的字典序编号，"
        "每档编号均为判串 'F' 位置的连续末段）：%s" % "；".join(det), counter="；".join(det))


# ===========================================================================
# C4：检查点自证性与证书分档（增量 4）
# ===========================================================================
CKD = [("m2_10_fraction", 10), ("m2_10_mpq", 10), ("m2_12_fraction", 12), ("m2_12_mpq", 12),
       ("m2_13_fraction", 13), ("m2_13_mpq", 13), ("m2_14_mpq", 14),
       ("smoke_m2_2", 2), ("smoke_m2_2_mpq", 2), ("smoke_m2_5", 5), ("smoke_m2_5_mpq", 5),
       ("det_run1", 5), ("det_run2", 5)]
WANT_KEYS = {2: 3, 5: 5, 10: 10, 12: 12, 13: 13, 14: 14}
WANT_CERT = {2: (2, 2), 5: (5, 6), 10: (10, 10), 12: (12, 12), 13: (13, 13), 14: (14, 14)}


def check_c4():
    print("== 增量 4：检查点自证性与证书分档 ==")
    bad_tile, bad_cnt, bad_bal, bad_keys = [], [], [], []
    for name, m in CKD:
        files, shards, keys = load_ckpt(name)
        sp = sorted((s["start"], s["end"]) for s in shards)
        if not (len(files) == len(shards) and sp and sp[0][0] == 0
                and all(sp[i][1] == sp[i + 1][0] for i in range(len(sp) - 1))
                and [s["chunk"] for s in shards] == list(range(len(shards)))):
            bad_tile.append(name)
        tot = sum(s["count"] for s in shards)
        if tot != comb(2 * m + 1, m):
            bad_cnt.append(name)
        if not all(s["n_rank_def"] + s["n_infeasible"]
                   + sum(v["count"] for v in s["feasible"].values()) == s["count"] for s in shards):
            bad_bal.append(name)
        if len(keys) != WANT_KEYS[m]:
            bad_keys.append(name)
    rec("C4.1", not (bad_tile or bad_cnt or bad_bal or bad_keys),
        "13 套检查点逐片自证：片号连续、首片 start = 0、相邻 end_i = start_{i+1}、Σcount == C(2m₂+1, m₂)、"
        "每片 n_rank_def + n_infeasible + Σ捕捉数 == count、去重可行点数按档（%s）"
        % "、".join("%d 键" % WANT_KEYS[k] for k in (10, 12, 13, 14, 5, 2)),
        counter="铺满 %s；总数 %s；平衡 %s；键数 %s" % (bad_tile, bad_cnt, bad_bal, bad_keys))
    certs, bad_cert, bad_feas = {}, [], []
    for name, m in CKD:
        _f, _s, keys = load_ckpt(name)
        delta, W = TIER["m%d" % m][1:]
        cons = rows_int(m, delta, W)
        tab = set()
        for k in keys:
            y = tuple(Fraction(x) for x in k.split(","))
            tab.add(active_cert(y, cons, m))
        certs[name] = sorted(tab)
        if sorted(tab) != [WANT_CERT[m]]:
            bad_cert.append("%s=%s" % (name, sorted(tab)))
    rec("C4.2", not bad_cert,
        "证书（活跃秩, 活跃条数）逐键复算并与分档登记一致：主四档 (m₂, m₂)、阴性档 (2, 2)、边界档 (5, 6)；"
        "重点：m₂ = 5 的活跃条数 6 ≠ 活跃秩 5，故「活跃秩等于活跃条数」在该档按字面不成立（分档写法正确）",
        counter="不符：%s" % bad_cert)
    bad_ana = []
    for name, m in CKD:
        if m == 2:
            continue
        _f, _s, keys = load_ckpt(name)
        if keys_as_points(keys) != analytic_set(m, TIER["m%d" % m][1], TIER["m%d" % m][2]) \
                or len(keys) != m:
            bad_ana.append(name)
    _f, _s, k2 = load_ckpt("smoke_m2_2")
    neg = keys_as_points(k2) != analytic_set(2, D2DELTA, D2W)
    rec("C4.3", not bad_ana and neg,
        "顶点集与解析族逐坐标相等（十套非阴性档目录）且大小 == m₂；m₂ = 2 阴性档键集 ≠ 解析族（判别力保留）",
        counter="不符档 %s；阴性档判别力 %s" % (bad_ana, neg))
    shard_facts, bad_sh = [], []
    for name, m, n_exp, first_exp in (("m2_12_mpq", 12, 16, 325018), ("m2_12_fraction", 12, 16, 325018),
                                      ("m2_13_mpq", 13, 16, 1253643), ("m2_13_fraction", 13, 32, 626821),
                                      ("m2_14_mpq", 14, 32, 2423711)):
        _f, shards, _s = load_ckpt(name)
        cs = [s["count"] for s in shards]
        good = len(cs) == n_exp and cs[0] == first_exp and sum(cs) == comb(2 * m + 1, m) \
            and all((c == first_exp or c == first_exp + 1) for c in cs)
        if not good:
            bad_sh.append(name)
        shard_facts.append("%s=%d 片（%d 片 %d、%d 片 %d）和 %d"
                           % (name, len(cs), cs.count(first_exp), first_exp,
                              cs.count(first_exp + 1), first_exp + 1, sum(cs)))
    rec("C4.4", not bad_sh,
        "分片数与和（本文件独立求和，各档每片只取 floor 与 floor+1 两值且首片为 floor）：%s"
        % "；".join(shard_facts), counter="不符 %s" % bad_sh)


# ===========================================================================
# C5：抽块与全量再复算（增量 5）
# ===========================================================================
def check_c5():
    print("== 增量 5：抽块与全量再复算 ==")
    hist = {}
    for key, m in (("c_m10_t8", 10), ("c_m12_t8", 12), ("c_m13_t8", 13), ("c_m14_t8", 14), ("m5_e10", 5)):
        s = scan(key)
        hist[m] = (s["bytes"], s["S"], s["I"], s["F"], s["other"])
    want = {10: (352716, 295780, 56926, 10, 0), 12: (5200300, 4752735, 447553, 12, 0),
            13: (20058300, 18811533, 1246754, 13, 0), 14: (77558760, 74098262, 3460484, 14, 0),
            5: (462, 170, 262, 30, 0)}
    same10 = len({md5f(os.path.join(R2, DEC[n])) for n in ("c_m10_t8", "c_m10_t1", "py_m10")}) == 1
    rec("C5.1", hist == want and same10,
        "五档判串逐字节自数（字节数、S、I、F、非 S／I／F）：%s；m₂ = 10 的三份判串 md5 相同 = %s"
        % ("；".join("m₂=%d: %s" % (m, hist[m]) for m in (10, 12, 13, 14, 5)), same10),
        counter="自数 %s；m10 三份同 = %s" % (hist, same10))
    d12a, f12a, bad12a, cf12a, n12a = blocks_hist(12, [(5200000, 5200300)], "c_m12_t8")
    d12b, f12b, bad12b, cf12b, n12b = blocks_hist(12, [(5200288, 5200300), (2570000, 2570020), (0, 20)], "c_m12_t8")
    d10, f10, bad10, cf10, n10 = blocks_hist(10, [(352696, 352716), (0, 20)], "c_m10_t8")
    d14, f14, bad14, cf14, n14 = blocks_hist(14, [(77558746, 77558760)], "c_m14_t8")
    ntot = n12a + n12b + n10 + n14
    ok = (d12a == {"S": 109, "I": 179, "F": 12} and d12b == {"S": 36, "I": 4, "F": 12}
          and d10 == {"S": 15, "I": 15, "F": 10} and d14 == {"S": 0, "I": 0, "F": 14}
          and len(f12a) == 12 and len(f14) == 14
          and not (bad12a or bad12b or bad10 or bad14)
          and cf12a + cf12b + cf10 + cf14 == 0)
    rec("C5.2", ok,
        "抽块自写重算 %d 个子集，逐编号与判串字节全等：m₂ = 12 的 [5200000,5200300) 300 个为 S／I／F = 109／179／12；"
        "m₂ = 12 的 F 尾块 12 个全 F；m₂ = 12 的 [2570000,2570020) 20 个全 S、[0,20) 与 m₂ = 10 两区块合计分布 %s；"
        "m₂ = 14 尾块 14 个全 F；整数行列式非零却解不出的异常 0 个" % (ntot, d10),
        counter="分布 %s %s %s %s；不符 %s；冲突 %d"
                % (d12a, d12b, d10, d14, bad12a + bad12b + bad10 + bad14, cf12a + cf12b + cf10 + cf14))
    m5 = blocks_hist(5, [(0, 462)], "m5_e10")
    m5dist, m5f = m5[0], m5[1]
    cons5 = rows_int(5, DELTA, W5)
    keys5 = keys_as_points(load_ckpt("smoke_m2_5")[2])
    ana5 = analytic_set(5, DELTA, W5)
    d2 = {"S": 0, "I": 0, "F": 0}
    for k in range(10):
        tag, _y, _cf = classify(tuple(unrank(5, 2, k)), 2, rows_int(2, D2DELTA, D2W), D2DELTA, D2W)
        d2[tag] += 1
    keys2 = keys_as_points(load_ckpt("smoke_m2_2")[2])
    exp2 = {(Fraction(1), Fraction(1)), (Fraction(1), Fraction(3, 2)), (Fraction(3, 2), Fraction(1))}
    ok3 = (m5dist == {"S": 170, "I": 262, "F": 30} and m5[2] == [] and m5[4] == 462
           and set(m5f.values()) == keys5 == ana5 and d2 == {"S": 0, "I": 7, "F": 3}
           and keys2 == exp2)
    rec("C5.3", ok3,
        "全量重算：m₂ = 5 的 462 个子集 S／I／F = 170／262／30 且逐字节等于 m5_e10 判串、30 个 F 解 == 检查点键集 == 解析族；"
        "m₂ = 2 的 10 个子集为 0／7／3 且键集 == {(1,1)、(1,3/2)、(3/2,1)}",
        counter="m5 分布 %s／不符 %s；m2 分布 %s；键集相符 %s"
                % (m5dist, m5[2], d2, keys2 == exp2))
    inc_blocks = 12 + 300 + 20 + 20 + 20 + 20      # 增量清单的块大小之和；其中 12 块包含在 300 块内
    my_elems = ntot + m5[4] + 10                   # 本文件块元素合计（含重叠的 12 与额外的 m₂ = 14 尾块）
    my_distinct = ntot - 12 + m5[4] + 10           # 互异子集数（把 12 块与 300 块的重复去掉）
    rec("C5.4", inc_blocks == 392 and inc_blocks + m5[4] + 10 == 864
        and ntot == 392 + 14 and my_distinct == 866,
        "子集合计口径：增量清单块大小之和 %d（12 加 300 加四个 20；12 块含在 300 块内，故互异 380），"
        "加 m₂ = 5 的 462 与 m₂ = 2 的 10 即增量所写 864；本文件另加 m₂ = 14 尾块 14 个，"
        "块元素合计 %d、互异子集 %d" % (inc_blocks, my_elems, my_distinct),
        counter="增量块和 %d；本文件元素 %d、互异 %d" % (inc_blocks, my_elems, my_distinct))
    okp = all(y in analytic_set(10, DELTA, W2000) for y in f10.values()) \
        and all(y in analytic_set(12, DELTA, W2000) for y in f12a.values()) \
        and all(y in analytic_set(14, DELTA, W2000) for y in f14.values()) \
        and set(f10) == {352706, 352707, 352708, 352709, 352710, 352711, 352712, 352713, 352714, 352715} \
        and set(f12a) == set(range(5200288, 5200300)) and set(f14) == set(range(77558746, 77558760))
    rec("C5.5", okp,
        "块内可行解与编号：m₂ = 10 的 10 个 F 解、m₂ = 12 的 12 个、m₂ = 14 的 14 个全部落在各自解析族内，"
        "且各自编号恰为判串 'F' 位置的末段",
        counter="m10 编号 %s；m12 编号 %s；m14 编号 %s" % (sorted(f10), sorted(f12a), sorted(f14)))


# ===========================================================================
# C6：m₂ = 14 口径更正（增量 6）
# ===========================================================================
def check_c6():
    print("== 增量 6：m₂ = 14 口径更正 ==")
    vp = os.path.join(MRES, "logs", "r5_full_m2_14_mpq_verdict.txt")
    txt = read_text(vp)
    mj = re.search(r"SUMMARY_JSON (\{.*\})", txt)
    d = json.loads(mj.group(1)) if mj else {}
    ok = (md5f(vp) == "1a1fbae0749f0f99584856b741ad3aea" and d.get("equal") is True
          and d.get("certs") == [[14, 14]] and d.get("total") == 77558760
          and d.get("n_rank_def") == 74098262 and d.get("n_infeasible") == 3460484
          and d.get("n_distinct_feasible") == 14 and d.get("n_analytic") == 14 and d.get("chunks") == 32
          and scan("c_m14_t8")["S"] == d.get("n_rank_def")
          and scan("c_m14_t8")["I"] == d.get("n_infeasible"))
    rec("C6.1", ok,
        "判定件 results/logs/r5_full_m2_14_mpq_verdict.txt（md5 %s）：SUMMARY_JSON 的 total = %s、"
        "n_rank_def = %s、n_infeasible = %s、equal = %s、certs = %s、chunks = %s；且与判串自数一致"
        % (md5f(vp), d.get("total"), d.get("n_rank_def"), d.get("n_infeasible"), d.get("equal"),
           d.get("certs"), d.get("chunks")), counter="实测 %s" % {k: d.get(k) for k in
           ("total", "n_rank_def", "n_infeasible", "equal", "certs", "chunks")})
    files, shards, keys = load_ckpt("m2_14_mpq")
    cons = rows_int(14, DELTA, W2000)
    cert = sorted({active_cert(tuple(Fraction(x) for x in k.split(",")), cons, 14) for k in keys})
    ok2 = (len(files) == 32 and sum(s["count"] for s in shards) == 77558760 == comb(29, 14)
           and len(keys) == 14 and cert == [(14, 14)]
           and keys_as_points(keys) == analytic_set(14, DELTA, W2000))
    rec("C6.2", ok2,
        "检查点 m2_14_mpq 自证：%d 片、Σcount = %d == C(29,14)、%d 个可行点、证书 %s、顶点集 == 解析族"
        % (len(files), sum(s["count"] for s in shards), len(keys), cert),
        counter="片 %d 和 %d 键 %d 证书 %s" % (len(files), sum(s["count"] for s in shards), len(keys), cert))
    rec("C6.3", ok and ok2,
        "「m₂ = 14 判定已读取且为真」的可执行含义 == 前两条同时成立（判定件字段、判串自数、检查点证书三件互证）；"
        "旧括注「m₂ = 14 判定未读取」为过期表述这一措辞层判断，本文件不读 route-*.md，无法机器验证（仅记录）",
        counter="前两条 %s／%s" % (ok, ok2))


# ===========================================================================
# C7：账本条目草稿（增量 7）
# ===========================================================================
NOTE = os.path.join(TAIL, "ledger-note.md")


def check_c7():
    print("== 增量 7：账本条目草稿 ==")
    note = read_text(NOTE)
    lines = note.splitlines()
    # 2026-10-29 主代理按轨道建议改口径：本文件会被记录轮追加，整文件 md5 不能当身份判据；
    # 改为按文末标记提取草稿原文段后对 md5（冻结身份 = 提取段，与追加内容无关）。
    _a = note.find("<!-- ===== 路线四草稿原文起始")
    _b = note.find("<!-- ===== 路线四草稿原文结束")
    _seg = note[note.find("\n", _a) + 1:_b] if (_a >= 0 and _b > _a) else ""
    _seg_md5 = hashlib.md5(_seg.encode("utf-8")).hexdigest()
    rec("C7.1", _seg_md5 == "49b3e73ddbaf31e6fed8634efd97a6a0",
        "ledger-note.md 草稿原文（标记提取，%d 行）md5 %s；现行文件整体 %d 行、md5 %s"
        % (_seg.count("\n"), _seg_md5, len(lines), md5f(NOTE)),
        counter="提取段 md5 %s（整体 %d 行）" % (_seg_md5, len(lines)))
    sec1 = note.split("## 二、")[0].split("## 一、")[1]
    sec2 = note.split("## 二、")[1].split("## 三、")[0]
    sec3 = note.split("## 三、")[1].split("## 四、")[0]
    sec4 = note.split("## 四、")[1]
    trows = [l for l in sec1.splitlines() if l.startswith("|")]
    data_rows = [l for l in trows if not set(l.strip()) <= set("|-: ")]
    hdr = data_rows[0] if data_rows else ""
    ncols = len([x for x in hdr.split("|") if x.strip()])
    body = data_rows[1:]
    items2 = re.findall(r"^(\d+)\. 【(口径更正|未证|未跑|不可达)】", sec2, flags=re.M)
    lab = {}
    for _n, lb in items2:
        lab[lb] = lab.get(lb, 0) + 1
    items3 = re.findall(r"^\d+\. \*\*", sec3, flags=re.M)
    tiers = [lbl for lbl in ("m₂ = 10", "m₂ = 12", "m₂ = 13", "m₂ = 14") if lbl in hdr]
    rows_ok = all(len([x for x in l.split("|") if x.strip()]) == 6 for l in body)
    ok = (len(body) == 6 and ncols == 6 and len(tiers) == 4 and rows_ok and len(items2) == 11
          and lab == {"未证": 4, "未跑": 5, "不可达": 1, "口径更正": 1}
          and len(items3) == 7 and "建议替换句" in sec4 and "漂移登记" in sec4)
    rec("C7.2", ok,
        "结构：成果段覆盖矩阵 %d 个实现行 × 4 个档位列（表头 %d 列：实现、引擎与四档）、边界段 %d 条且标签计数 %s、"
        "引用纪律 %d 条、合并建议含「建议替换句」与「漂移登记」"
        % (len(body), ncols, len(items2), lab, len(items3)),
        counter="实现行 %d；表头列 %d；档位列 %d；每行格数一致 %s；边界条 %d；标签 %s；纪律条 %d"
                % (len(body), ncols, len(tiers), rows_ok, len(items2), lab, len(items3)))
    checks = []
    for lit in ("δ = 126797/80000", "W = 2000", "C(21,10) = 352716", "C(25,12) = 5200300",
                "C(27,13) = 20058300", "C(29,14) = 77558760", "462；170、262、30",
                "180300/5200300", "118300/20058300", "198760/77558760",
                "3.47%", "0.59%", "0.26%", "1246767", "18811533", "(5, 6)", "[[14, 14]]",
                "b269256bfff877a81fa5a81047a4c958", "8fb4ba1aef28fdc293b52270985ec35e",
                "152514f874a144554d1dff2ec0570da9", "37921d19726088fb8be115707a749356",
                "18e23746174db60150198149b00cd869", '"n_compare": 5200300', '"n_mismatch": 0',
                '"point_sets_equal": true'):
        if lit not in note:
            checks.append(lit)
    cvals = {"269128937220": comb(41, 20), "3217533506933149454210801550": comb(95, 47),
             "720162138745872857431467203815692960288647797444355400": comb(183, 91)}
    bad_c = [k for k, v in cvals.items() if str(v) != k or k not in note]
    rec("C7.3", not checks and not bad_c,
        "数值与产物一致：参数写法、五个组合数、五个判串 md5、三组覆盖率分子分母与百分比、两个缺口数、"
        "分档证书、两个对拍 JSON 字段、三个不可达档组合数（本文件 math.comb 复算）全部命中且相符",
        counter="缺字面 %s；组合数不符 %s" % (checks, bad_c))
    _f, shards, _s = load_ckpt("m2_12_mpq")
    cs = [s["count"] for s in shards]
    rest = cs[1:]
    rec("C7.4", cs[0] == 325018 and sum(cs) == 5200300 and all(c in (325018, 325019) for c in rest),
        "附条（分片更正的可核部分）：m₂ = 12 检查点 %d 片、首片 %d（故「16 片各 325019」不成立），"
        "其余片取 %d 或 %d（%d 片 %d、%d 片 %d），和 %d == C(25,12)（本文件独立求和）"
        % (len(cs), cs[0], 325018, 325019, rest.count(325018), 325018, rest.count(325019), 325019, sum(cs)),
        counter="首片 %d；其余分布 %s；和 %d" % (cs[0], {c: rest.count(c) for c in set(rest)}, sum(cs)))
    ledp = os.path.join(REPO, "70-research", "ledger.md")
    lrnp = os.path.join(REPO, "70-research", "learnings.md")
    led = read_text(ledp).splitlines()
    lrn = read_text(lrnp).splitlines()
    plan = read_text(os.path.join(REPO, "70-research", "tracks", "vertex-m12", "plan.md")).splitlines()
    led_now, lrn_now = md5f(ledp), md5f(lrnp)
    reg_led, reg_lrn = "8e0b44e3ebbf795dc393e4fa559cbee3", "96f3d946b0fbae97e31b873090503fb9"
    phr = [i + 1 for i, l in enumerate(led) if "顶点识别的机器核对升一档" in l]
    plan_hits = [i + 1 for i, l in enumerate(plan) if "`ledger.md:25`（节 0.2 第 4 条）" in l]
    rec("C7.5", reg_led in note and reg_lrn in note and led_now != reg_led and lrn_now != reg_lrn
        and phr == [126] and plan_hits == [20],
        "漂移登记可核部分：条目登记的共享 ledger.md（197 行 %s）与 learnings.md（62 行 %s）在当前工作区已分别变为 "
        "%d 行 %s 与 %d 行 %s（合并后漂移，机器核对）；「顶点识别的机器核对升一档」在当前 ledger.md 只出现在第 %s 行"
        "（条目写 123 行，行号随合并漂移）；条目把引文记作 vertex-m12/plan.md:25，实测在第 %s 行、第 25 行实为小节标题，"
        "与增量所称「漂移登记行号一处错」一致（其依据的 falsified 清单不在本轮材料内，未核）"
        % (reg_led[:12], reg_lrn[:12], len(led), led_now[:12], len(lrn), lrn_now[:12], phr, plan_hits),
        counter="ledger 现 md5 %s 命中 %s；learnings 现 md5 %s；plan 命中 %s"
                % (led_now[:12], phr, lrn_now[:12], plan_hits))


# ===========================================================================
# 深度档
# ===========================================================================
def check_d1():
    print("== 深度档 D1：m₂ = 10 全量 352716 个子集重算 ==")
    t0 = time.time()
    cons = rows_int(10, DELTA, W2000)
    data = dec("c_m10_t8")
    dist = {"S": 0, "I": 0, "F": 0}
    fidx, bad, conflict = [], [], 0
    for k in range(352716):
        tag, y, cf = classify(tuple(unrank(21, 10, k)), 10, cons, DELTA, W2000)
        dist[tag] += 1
        conflict += cf
        if tag != chr(data[k]):
            bad.append((k, tag, chr(data[k])))
            if len(bad) > 3:
                break
        if tag == "F":
            fidx.append(k)
    ok = (dist == {"S": 295780, "I": 56926, "F": 10} and not bad and conflict == 0
          and fidx == list(range(352706, 352716)))
    rec("D1", ok,
        "全量自算 352716 个子集，直方图 %s，F 编号 %s 至 %s，逐字节不一致 %d、异常 %d，用时 %.1f 秒"
        % (dist, fidx[0] if fidx else "无", fidx[-1] if fidx else "无", len(bad), conflict, time.time() - t0),
        counter="直方图 %s；不一致 %s；异常 %d" % (dist, bad, conflict))


def check_d2():
    print("== 深度档 D2：重跑 recon_evidence_chain.py ==")
    r = subprocess.run([sys.executable, os.path.join(VSCRIPTS, "recon_evidence_chain.py")],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3600)
    reg = read_bytes(os.path.join(VRES, "recon_evidence_chain.out.txt"))
    rec("D2", r.returncode == 0 and r.stdout == reg,
        "实跑退出码 %d，stdout 与注册产物逐字节相同（%s，139 条 PASS、FAIL 总数 = 0）"
        % (r.returncode, r.stdout == reg), counter="rc=%d；同=%s" % (r.returncode, r.stdout == reg))


def check_d3():
    print("== 深度档 D3：重跑 check_ledger_note.py（如实报告漂移） ==")
    r = subprocess.run([sys.executable, os.path.join(VSCRIPTS, "check_ledger_note.py")],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3600)
    out = r.stdout.decode("utf-8", "replace")
    reg_p = os.path.join(VRES, "check_ledger_note.out")
    reg = read_text(reg_p)
    fails = [l for l in out.splitlines() if l.startswith("[FAIL]")]
    cids = sorted({l.split()[1] for l in fails if len(l.split()) > 1})
    mk = re.search(r"汇总：(\d+) 项复算 \+ 耦合与结构；FAIL = (\d+)", out)
    n_items = int(mk.group(1)) if mk else -1
    n_fail = int(mk.group(2)) if mk else -1
    drift_only = all(c in ("H6", "H7", "I15", "I16") for c in cids)
    led_p = os.path.join(REPO, "70-research", "ledger.md")
    lrn_p = os.path.join(REPO, "70-research", "learnings.md")
    later = (os.path.getmtime(led_p) > os.path.getmtime(reg_p)
             and os.path.getmtime(lrn_p) > os.path.getmtime(reg_p))
    j1diff = [a for a, b in zip(out.splitlines(), reg.splitlines()) if a != b and " J1 " in b]
    ok = (n_items == 58 and n_fail == len(fails) and r.returncode == (1 if fails else 0)
          and drift_only and later and len(j1diff) == 1)
    rec("D3", ok,
        "实跑退出码 %d、汇总行「%d 项复算 + 耦合与结构；FAIL = %d」；失败项 %s 全部落在两件共享文件的漂移上"
        "（H6／H7 为身份、I15／I16 为行号定点），且 ledger.md 与 learnings.md 的修改时刻晚于本闸门注册产物"
        "（mtime 机器核对），故退出码 1 是共享文件被改写所致，不是条目结论被推翻；另与注册输出差 1 行 "
        "J1 引擎标签（注册环境 gmpy2 2.3.2，本解释器无 gmpy2 时打印 python int）"
        % (r.returncode, n_items, n_fail, cids),
        counter="rc=%d 项数 %d FAIL %d 失败项 %s 漂移时刻晚于注册 %s J1 差 %d"
                % (r.returncode, n_items, n_fail, cids, later, len(j1diff)))


def check_d4():
    print("== 深度档 D4：重跑上轮闸门字节快照（如实报告漂移） ==")
    r = subprocess.run([sys.executable, SNAPSHOT], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=3600)
    out = r.stdout.decode("utf-8", "replace")
    npass, nfail = out.count("[PASS]"), out.count("[FAIL]")
    fails = [l for l in out.splitlines() if l.startswith("[FAIL]")]
    only_s11 = all(l.startswith("[FAIL] S1.1") for l in fails)
    drift_named = any(("ledger.md" in l and "learnings.md" in l) for l in fails)
    ok = (npass + nfail == 42 and only_s11 and r.returncode == (1 if fails else 0)
          and (not fails or drift_named))
    rec("D4", ok,
        "prev_round_verify.py.txt 实跑：退出码 %d、[PASS] %d、[FAIL] %d；判据总数关系 42 成立、失败项全部为 S1.1，"
        "失败原因是冻结登记里的共享 ledger.md 与 learnings.md 在闸门冻结后被改写（现 md5 与登记不符），"
        "故该闸门当前不可能再复跑成全绿；注册 stdout 里的 42 条 PASS 是冻结时刻的记录（C3.1 核对）"
        % (r.returncode, npass, nfail),
        counter="rc=%d PASS=%d FAIL=%d 失败行 %s"
                % (r.returncode, npass, nfail, [l[:120] for l in fails[:1]]))


# ===========================================================================
def main():
    global FORCE_SHIM
    argv = sys.argv[1:]
    if "--blindspot-worker" in argv:
        print(json.dumps(blindspot_payload(), ensure_ascii=False))
        return 0
    deep = "--deep" in argv
    FORCE_SHIM = "--force-shim" in argv
    print("本文件 %s；md5 %s；解释器 python %s" % (OWN, md5f(OWN), sys.version.split()[0]))
    print("工作参数：δ = %s（严格下界，C1.7 现场重算其身份）、W = 2000（主四档）、"
          "m₂ = 5 档 W = (δ^5−1)/(δ−1)、m₂ = 2 档 (3/2, 3/2)" % DELTA)
    t0 = time.time()
    plan = list((check_c1, check_c2, check_c3, check_c4, check_c5, check_c6, check_c7))
    if deep:
        plan += list((check_d1, check_d2, check_d3, check_d4))
    for fn in plan:
        ts = time.time()
        try:
            fn()
        except Exception as exc:                     # 失败即 FAIL，不静默
            rec(fn.__name__, False, "断言执行异常：%s: %s" % (type(exc).__name__, exc))
        print("   （%s 用时 %.1f 秒）" % (fn.__name__, time.time() - ts))
    print("=" * 100)
    nf = len(STATE["fails"])
    print("断言共 %d 条：PASS = %d，FAIL = %d（%s档，用时 %.1f 秒）"
          % (STATE["n"], STATE["n"] - nf, nf, "深度" if deep else "默认", time.time() - t0))
    if nf:
        print("最小反例：")
        for cid, cex in STATE["fails"]:
            print("  %s：%s" % (cid, cex))
    print("退出码 %d" % (0 if nf == 0 else 1))
    return 0 if nf == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
