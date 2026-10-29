#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_ledger_note.py —— vertex-tail 账本条目的数字溯源闸门（路线四）

用途：对本目录上一级 `ledger-note.md`（账本条目草稿）中的可机器复算断言逐条复算。
每条判据都能取 False（不写恒真判据）；任一 FAIL 以非零退出码结束。
判据来源：任务书 (c)「条目内每个数字可 grep 到产物；每条边界写明「未证／未跑／不可达」三态之一」。
只读底本：`70-research/tracks/vertex-m12/cycle-1/` 下的报告、results/、scripts/results/。
本脚本不重跑任何全量枚举；只读文件、复算计数、比对 md5 与 JSON 字段。

用法：
    ./20-experiments/.venv/bin/python .../scripts/check_ledger_note.py            # 默认读轨道根 ledger-note.md
    ... --note /tmp/perturbed/ledger-note.md                                      # 指定其它副本（扰动检验用）
"""
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]          # vertex-tail/cycle-1
ROOT = Path(__file__).resolve().parents[5]          # collatz-attack/
VM = ROOT / "70-research/tracks/vertex-m12/cycle-1"
DEFAULT_NOTE = HERE.parent / "ledger-note.md"       # vertex-tail/ledger-note.md

CHECKS = []  # (cid, desc, fn, must_in_note)


def check(cid, desc, must=None):
    def deco(fn):
        CHECKS.append((cid, desc, fn, list(must or [])))
        return fn
    return deco


def md5file(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def nlines(p):
    with open(p, "rb") as f:
        return sum(1 for _ in f)


def line_of(p, n):  # 1 起始
    with open(p, encoding="utf-8") as f:
        for i, ln in enumerate(f, 1):
            if i == n:
                return ln
    return None


# ---------------------------------------------------------------- 组合数复算

@check("D1", "C(21,10) = 352716", ["352716"])
def _():
    v = math.comb(21, 10)
    return v == 352716, f"math.comb(21,10) = {v}"


@check("D2", "C(25,12) = 5200300", ["5200300"])
def _():
    v = math.comb(25, 12)
    return v == 5200300, f"math.comb(25,12) = {v}"


@check("D3", "C(27,13) = 20058300", ["20058300"])
def _():
    v = math.comb(27, 13)
    return v == 20058300, f"math.comb(27,13) = {v}"


@check("D4", "C(29,14) = 77558760", ["77558760"])
def _():
    v = math.comb(29, 14)
    return v == 77558760, f"math.comb(29,14) = {v}"


@check("D5", "C(11,5) = 462", ["462"])
def _():
    v = math.comb(11, 5)
    return v == 462, f"math.comb(11,5) = {v}"


@check("D6", "不可达档 C(41,20) = 269128937220", ["269128937220"])
def _():
    v = math.comb(41, 20)
    return v == 269128937220, f"math.comb(41,20) = {v}"


@check("D7", "不可达档 C(95,47) 精确值", ["3217533506933149454210801550"])
def _():
    v = math.comb(95, 47)
    return v == 3217533506933149454210801550, f"math.comb(95,47) = {v}"


@check("D8", "不可达档 C(183,91) 精确值", ["720162138745872857431467203815692960288647797444355400"])
def _():
    v = math.comb(183, 91)
    return v == 720162138745872857431467203815692960288647797444355400, f"math.comb(183,91) = {v}"


# ---------------------------------------------------------------- 判串（字节层）

DEC_DIR = VM / "scripts/results/route2"

# (文件名, 字节数, md5, (S, I, F), 令牌)
DEC_SPEC = [
    ("py_m10_decisions.txt", 352716, "b269256bfff877a81fa5a81047a4c958", (295780, 56926, 10),
     ["b269256bfff877a81fa5a81047a4c958", "295780", "56926"]),
    ("c_m10_t8_decisions.txt", 352716, "b269256bfff877a81fa5a81047a4c958", (295780, 56926, 10), []),
    ("c_m10_t1_decisions.txt", 352716, "b269256bfff877a81fa5a81047a4c958", (295780, 56926, 10), []),
    ("c_m12_t8_decisions.txt", 5200300, "8fb4ba1aef28fdc293b52270985ec35e", (4752735, 447553, 12),
     ["8fb4ba1aef28fdc293b52270985ec35e", "4752735", "447553"]),
    ("c_m13_t8_decisions.txt", 20058300, "152514f874a144554d1dff2ec0570da9", (18811533, 1246754, 13),
     ["152514f874a144554d1dff2ec0570da9", "18811533", "1246754"]),
    ("c_m14_t8_decisions.txt", 77558760, "37921d19726088fb8be115707a749356", (74098262, 3460484, 14),
     ["37921d19726088fb8be115707a749356", "74098262", "3460484"]),
    ("m5_e10_decisions.txt", 462, "18e23746174db60150198149b00cd869", (170, 262, 30),
     ["18e23746174db60150198149b00cd869", "170", "262"]),
]


def make_dec_check(fname, nbytes, md5exp, hists, idx):
    @check(f"E{idx}", f"判串 {fname} 的字节数、md5、S/I/F 直方图", None)
    def _():
        p = DEC_DIR / fname
        b = p.read_bytes()
        got = (b.count(b"S"), b.count(b"I"), b.count(b"F"))
        ok = (len(b) == nbytes and md5file(p) == md5exp and got == hists
              and sum(got) == len(b))
        return ok, f"bytes={len(b)} md5={md5file(p)} S/I/F={got}（期望 {nbytes}、{md5exp}、{hists}）"
    return _


for _i, (_f, _n, _m, _h, _tk) in enumerate(DEC_SPEC, 1):
    _fn = make_dec_check(_f, _n, _m, _h, _i)
    CHECKS[-1] = (f"E{_i}", CHECKS[-1][1], _fn, _tk)


@check("E8", "三份 m10 判串 md5 相同（C 双线程、C 单线程、Python 参考）", [])
def _():
    ms = {md5file(DEC_DIR / f) for f, *_ in DEC_SPEC if f.endswith("m10_decisions.txt")}
    return len(ms) == 1, f"m10 判串 md5 集合 = {sorted(ms)}"


# ---------------------------------------------------------------- 检查点

CKPT = VM / "results/ckpt"
FULL_DIRS = ["m2_10_fraction", "m2_10_mpq", "m2_12_fraction", "m2_12_mpq",
             "m2_13_fraction", "m2_13_mpq", "m2_14_mpq"]
SMOKE_DIRS = {"smoke_m2_2": 2, "smoke_m2_2_mpq": 2, "smoke_m2_5": 5, "smoke_m2_5_mpq": 5}


def ckpt_scan(d):
    chunks = sorted(d.glob("chunk_*.json"), key=lambda p: int(p.stem.split("_")[1]))
    tot = 0
    dedup = {}
    spans = []
    for c in chunks:
        j = json.loads(c.read_text())
        if j["count"] != j["end"] - j["start"]:
            return None, f"{c.name}: count != end-start"
        s = sum(v["count"] for v in j["feasible"].values())
        if j["n_rank_def"] + j["n_infeasible"] + s != j["count"]:
            return None, f"{c.name}: 逐片关系不成立"
        spans.append((j["start"], j["end"]))
        tot += j["count"]
        for k, v in j["feasible"].items():
            dedup[k] = dedup.get(k, 0) + v["count"]
    spans.sort()
    if spans[0][0] != 0:
        return None, "首片 start != 0"
    for a, b in zip(spans, spans[1:]):
        if a[1] != b[0]:
            return None, f"分片不首尾相接：{a} {b}"
    return (len(chunks), tot, dedup, spans[-1][1]), ""


def make_ckpt_check(dname, idx):
    m2 = int(dname.split("_")[1]) if dname.startswith("m2_") else SMOKE_DIRS[dname]
    exp_dedup = 3 if (dname in SMOKE_DIRS and m2 == 2) else m2  # 阴性档顶点数为 3

    @check(f"F{idx}", f"检查点 {dname}：Σcount、去重可行点、捕捉次数、分片关系", None)
    def _():
        info, err = ckpt_scan(CKPT / dname)
        if info is None:
            return False, err
        nch, tot, dedup, last = info
        ok = (tot == math.comb(2 * m2 + 1, m2) and len(dedup) == exp_dedup and last == tot)
        caps = sorted(set(dedup.values()))
        if dname in SMOKE_DIRS and m2 == 5:
            ok = ok and caps == [6]
        elif m2 != 5:
            ok = ok and caps == [1]
        return ok, (f"chunks={nch} Σcount={tot} 去重点={len(dedup)}（期望 {exp_dedup}）"
                    f" 捕捉次数集={caps}（C(2m+1,m)={math.comb(2*m2+1, m2)}）")
    return _


_idx = 1
for _d in FULL_DIRS:
    _fn = make_ckpt_check(_d, _idx)
    CHECKS[-1] = (f"F{_idx}", CHECKS[-1][1], _fn,
                  ["32 分片"] if _d == "m2_14_mpq" else [])
    _idx += 1
for _d in SMOKE_DIRS:
    _fn = make_ckpt_check(_d, _idx)
    CHECKS[-1] = (f"F{_idx}", CHECKS[-1][1], _fn, [])
    _idx += 1


@check("F12", "det_run1 与 det_run2 的 chunk_0000.json 逐字节相同", [])
def _():
    a = (CKPT / "det_run1/chunk_0000.json").read_bytes()
    b = (CKPT / "det_run2/chunk_0000.json").read_bytes()
    return a == b, f"bytes={len(a)}/{len(b)} 相同={a == b}"


# ---------------------------------------------------------------- 对拍 JSON 与 r5 判定件

@check("G1", "route3_xcheck_m12_allsubsets.json 字段", ['"n_compare": 5200300', '"n_mismatch": 0',
                                                   '"n_candidates_impl1": 12'])
def _():
    j = json.loads((VM / "results/route3_xcheck_m12_allsubsets.json").read_text())
    ok = (j["n_compare"] == 5200300 and j["n_mismatch"] == 0
          and j["n_candidates_impl1"] == 12 and j["n_candidates_impl2"] == 12
          and j["first_mismatches"] == [])
    return ok, f"n_compare={j['n_compare']} n_mismatch={j['n_mismatch']} cand={j['n_candidates_impl1']}/{j['n_candidates_impl2']}"


@check("G2", "route3_xcheck_m10_allsubsets.json 字段", [])
def _():
    j = json.loads((VM / "results/route3_xcheck_m10_allsubsets.json").read_text())
    return j["n_compare"] == 352716 and j["n_mismatch"] == 0, f"n_compare={j['n_compare']} n_mismatch={j['n_mismatch']}"


@check("G3", "route3_vs_other_m12.json 顶点坐标集合相等", ['"point_sets_equal": true'])
def _():
    j = json.loads((VM / "results/route3_vs_other_m12.json").read_text())
    ok = (j["point_sets_equal"] is True and j["n_only_in_mine"] == 0
          and j["n_only_in_other"] == 0 and j["n_other_distinct"] == 12)
    return ok, f"point_sets_equal={j['point_sets_equal']} only_mine={j['n_only_in_mine']} only_other={j['n_only_in_other']}"


R5V = VM / "results/logs/r5_full_m2_14_mpq_verdict.txt"


def parse_summary(p):
    t = p.read_text(encoding="utf-8")
    ms = re.findall(r"SUMMARY_JSON (\{.*\})", t)
    if not ms:
        return None
    return json.loads(ms[-1])


@check("G4", "m2=14 判定件 SUMMARY_JSON 关键字段", ["2912.24", "13477.7"])
def _():
    j = parse_summary(R5V)
    ok = (j is not None and j["total"] == 77558760 and j["processed"] == 77558760
          and j["n_rank_def"] == 74098262 and j["n_infeasible"] == 3460484
          and j["n_distinct_feasible"] == 14 and j["equal"] is True
          and j["certs"] == [[14, 14]] and j["wall_s"] == 2912.24
          and j["cpu_s"] == 13477.7 and j["delta"] == "126797/80000"
          and j["W"] == "2000" and j["chunks"] == 32 and j["impl"] == "mpq")
    return ok, f"total={j['total']} equal={j['equal']} certs={j['certs']} wall_s={j['wall_s']} impl={j['impl']} chunks={j['chunks']}"


@check("G5", "m2=14 复核件 r5_m2_14_verdict_check.txt 判定行与 SUMMARY 同", [])
def _():
    j = parse_summary(VM / "results/logs/r5_m2_14_verdict_check.txt")
    return (j is not None and j["n_distinct_feasible"] == 14 and j["equal"] is True), \
        f"equal={j['equal'] if j else None} n_distinct={j['n_distinct_feasible'] if j else None}"


# ---------------------------------------------------------------- 文件身份

IDENT = [
    ("route-1.md", VM / "route-1.md", 293, "939cc627c887fd4064214b14accfa651"),
    ("route-2.md", VM / "route-2.md", 380, "9db46ca0d456a7c463f63adf776aa40e"),
    ("route-3.md", VM / "route-3.md", 351, "8b8fe031050f630565a1c58a5e53a560"),
    ("route-4.md", VM / "route-4.md", 399, "e5ff27b061020b6aa81e326bd54c0b70"),
    ("route-5.md", VM / "route-5.md", 343, "3e833e440ceb5cc74d3470b24ac8355e"),
    ("ledger.md", ROOT / "70-research/ledger.md", 197, "8e0b44e3ebbf795dc393e4fa559cbee3"),
    ("learnings.md", ROOT / "70-research/learnings.md", 62, "96f3d946b0fbae97e31b873090503fb9"),
    ("frozen-spec.md", VM / "results/frozen-spec.md", 94, "f117144c2ea51ecb4a09387318369cfd"),
]


def make_ident(path, exp_lines, exp_md5, idx):
    name = path.name
    @check(f"H{idx}", f"身份 {name}：行数与 md5", [exp_md5])
    def _():
        got_lines, got_md5 = nlines(path), md5file(path)
        return (got_lines == exp_lines and got_md5 == exp_md5), \
            f"lines={got_lines} md5={got_md5}（期望 {exp_lines}、{exp_md5}）"
    return _


for _i, (_n, _p, _l, _m) in enumerate(IDENT, 1):
    _fn = make_ident(_p, _l, _m, _i)
    CHECKS[-1] = (f"H{_i}", CHECKS[-1][1], _fn, [_m])


# ---------------------------------------------------------------- 行号定点引用（带版本）

LINE_PINS = [
    ("I1", VM / "route-5.md", 100, ["此前一次提交里", "作废"], ["route-5.md:100"]),
    ("I2", VM / "route-2.md", 371, ["组合规模不可达", "3.47%"], ["route-2.md:371"]),
    ("I3", VM / "route-3.md", 227, ["m₂ ≥ 15 未跑", "只做了两个端点"], ["route-3.md:227"]),
    ("I4", VM / "route-5.md", 330, ["14 为 mpq 单引擎全量"], ["route-5.md:330"]),
    ("I5", VM / "route-3.md", 207, ["214.63"], ["214.63"]),
    ("I6", VM / "route-5.md", 98, ["未再两连跑"], ["route-5.md:98"]),
    ("I7", VM / "route-5.md", 96, ["闭化"], ["route-5.md:96"]),
    ("I8", VM / "route-2.md", 255, ["3.47%", "0.59%", "0.26%"], []),
    ("I9", VM / "route-2.md", 69, ["18811533 个 'S' 判定未过第二路"], []),
    ("I10", VM / "route-5.md", 126, ["mpq 单引擎"], []),
    ("I11", VM / "route-1.md", 13, ["闸门判定：三组全部一致"], []),
    ("I12", VM / "route-4.md", 322, ["闭化读法"], ["route-4.md:322"]),
    ("I13", VM / "route-4.md", 345, ["全活跃子集枚举的输出集合恰为闭多面体 P 的顶点集"], ["route-4.md:345"]),
    ("I14", VM / "route-4.md", 334, ["m₂ = 12、13、14"], []),
]


def make_line_check(p, n, subs, idx, cid):
    @check(cid, f"行号定点 {p.name}:{n}（md5 {md5file(p)[:8]}）", None)
    def _():
        ln = line_of(p, n)
        if ln is None:
            return False, f"行 {n} 不存在"
        miss = [s for s in subs if s not in ln]
        return not miss, f"缺失子串 {miss}" if miss else f"含全部 {len(subs)} 个子串"
    return _


for _i, (_cid, _p, _n, _subs, _tk) in enumerate(LINE_PINS, 1):
    _fn = make_line_check(_p, _n, _subs, _i, _cid)
    CHECKS[-1] = (_cid, CHECKS[-1][1], _fn, _tk)


@check("I15", "ledger.md 中「顶点识别的机器核对升一档」只出现在 123 行", ["ledger.md:123"])
def _():
    p = ROOT / "70-research/ledger.md"
    hits = [i for i, ln in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
            if "顶点识别的机器核对升一档" in ln]
    return hits == [123], f"命中行号 = {hits}"


@check("I16", "ledger.md:112 含「m₂ = 12 的全穷举未跑」", ["ledger.md:112"])
def _():
    ln = line_of(ROOT / "70-research/ledger.md", 112)
    return "m₂ = 12 的全穷举未跑" in ln, "逐字命中" if "m₂ = 12 的全穷举未跑" in ln else "未命中"


# ---------------------------------------------------------------- 整数幂锚点

@check("J1", "δ 严格下界锚点 2^15849625 < 3^10000000 < 2^15849626",
       ["2^15849625 < 3^10000000"])
def _():
    try:
        import gmpy2
        a, b1, b2 = gmpy2.mpz(3) ** 10_000_000, gmpy2.mpz(2) ** 15_849_625, gmpy2.mpz(2) ** 15_849_626
        eng = f"gmpy2 {gmpy2.version()}"
    except Exception:
        a, b1, b2 = 3 ** 10_000_000, 2 ** 15_849_625, 2 ** 15_849_626
        eng = "python int"
    ok = b1 < a < b2
    return ok, f"引擎 {eng}；b1 < a = {b1 < a}；a < b2 = {a < b2}"


# ---------------------------------------------------------------- 边界段标签结构

BOUND_HEAD = re.compile(r"^##\s*二、边界段")
NEXT_HEAD = re.compile(r"^##\s")
ITEM = re.compile(r"^(\d+)\. 【(未证|未跑|不可达|口径更正)】")


def boundary_check(note_text):
    lines = note_text.splitlines()
    start = next((i for i, ln in enumerate(lines) if BOUND_HEAD.match(ln)), None)
    if start is None:
        return False, "未找到「## 二、边界段」小节"
    end = next((i for i in range(start + 1, len(lines)) if NEXT_HEAD.match(lines[i])), len(lines))
    labels = []
    numbered = 0
    bad = []
    for ln in lines[start + 1:end]:
        if re.match(r"^\d+\.", ln):
            numbered += 1
            m = ITEM.match(ln)
            if m:
                labels.append(m.group(2))
            else:
                bad.append(ln[:60])
    c_wei = labels.count("未证")
    c_pao = labels.count("未跑")
    c_bukedao = labels.count("不可达")
    c_gengzheng = labels.count("口径更正")
    ok = (not bad and c_wei >= 2 and c_pao >= 2 and c_bukedao >= 1 and c_gengzheng == 1
          and numbered == len(labels))
    detail = (f"条目数={numbered} 未证={c_wei} 未跑={c_pao} 不可达={c_bukedao} "
              f"口径更正={c_gengzheng}" + (f" 未带标签行={bad}" if bad else ""))
    return ok, detail


# ---------------------------------------------------------------- 主流程

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--note", default=str(DEFAULT_NOTE))
    args = ap.parse_args()
    note_path = Path(args.note)
    if not note_path.exists():
        print(f"[FAIL] 找不到账本条目文件：{note_path}")
        return 2
    note_text = note_path.read_text(encoding="utf-8")

    n_fail = 0
    for cid, desc, fn, must in CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:  # 任何异常按 FAIL 计（不吞）
            ok, detail = False, f"异常 {type(e).__name__}: {e}"
        print(f"[{'PASS' if ok else 'FAIL'}] {cid} {desc} —— {detail}")
        if not ok:
            n_fail += 1

    print("---- 条目耦合（每个复算项的值串必须原样出现在条目正文）----")
    for cid, desc, fn, must in CHECKS:
        for tok in must:
            ok = tok in note_text
            print(f"[{'PASS' if ok else 'FAIL'}] C-{cid} 条目含 {tok!r}")
            if not ok:
                n_fail += 1

    print("---- 边界段标签（未证／未跑／不可达 三态；口径更正恰一条）----")
    ok, detail = boundary_check(note_text)
    print(f"[{'PASS' if ok else 'FAIL'}] K1 边界段标签结构 —— {detail}")
    if not ok:
        n_fail += 1

    print(f"---- 汇总：{len(CHECKS)} 项复算 + 耦合与结构；FAIL = {n_fail} ----")
    print(f"退出码 {'0（全部通过）' if n_fail == 0 else '1（存在 FAIL）'}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
