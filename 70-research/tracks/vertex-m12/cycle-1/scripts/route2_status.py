#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route2 状态与数值汇总：把报告需要的关键行集中打印成一段，供一次性引用。
只读，不修改任何既有文件；输出同时落盘 results/route2/route2_status_dump.txt。
"""
import hashlib
import os

D = "results/route2"


def show(path, pats=None, maxlines=40, title=None):
    print("=" * 70)
    print("FILE:", path, title or "")
    if not os.path.exists(path):
        print("  (不存在)")
        return
    with open(path, "r", errors="replace") as f:
        lines = f.read().splitlines()
    n = 0
    for ln in lines:
        if pats is None or any(p in ln for p in pats):
            s = ln if len(ln) <= 200 else ln[:200] + " ..."
            print("  " + s)
            n += 1
            if n >= maxlines:
                print("  ...(截断)")
                break
    if n == 0:
        print("  (无匹配行；总行数 %d)" % len(lines))


def md5(path):
    if not os.path.exists(path):
        return "(不存在)"
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


print("route2 数值状态汇总")
print()
show(f"{D}/m5_e10_log.txt", ["DECISION_COUNTS", "CROSSCHECK", "SETS_EQUAL", "MISMATCHES", "EXIT_"])
show(f"{D}/c_m10_t8_log.txt", ["PARAMS", "TOTAL_SUBSETS", "ENUM_CONTINUITY", "DECISIONS_COMPLETE",
                               "DECISION_COUNTS", "CROSSCHECK", "THREAD_SETS_SUM", "TIME_SAMPLE",
                               "ENUM_WALL_SEC", "FEASIBLE_SUBSETS", "VERTEX_COUNT", "SETS_EQUAL",
                               "MISMATCHES", "EXIT_", "EXPECT"], title="(m2=10, 8 线程)")
show(f"{D}/c_m10_t8_time.txt", None)
show(f"{D}/c_m10_t1_log.txt", ["DECISION_COUNTS", "CROSSCHECK", "SETS_EQUAL", "EXIT_"], title="(m2=10, 1 线程)")
show(f"{D}/c_m10_t1_time.txt", None)
show(f"{D}/py_m10_log.txt", ["TOTAL", "DECISION_COUNTS", "DECISIONS_MD5", "ELAPSED_SEC",
                             "ANALYTIC_COUNT", "EXIT_OK"], title="(Python 参考 m2=10)")
print("=" * 70)
print("判串 md5 三方对比：")
for p in [f"{D}/c_m10_t8_decisions.txt", f"{D}/c_m10_t1_decisions.txt", f"{D}/py_m10_decisions.txt",
          f"{D}/c_m12_t8_decisions.txt"]:
    print("  ", md5(p), p)
show(f"{D}/c_m12_t8_log.txt", ["PARAMS", "TOTAL_SUBSETS", "ENUM_CONTINUITY", "DECISIONS_COMPLETE",
                               "DECISION_COUNTS", "CROSSCHECK", "THREAD_SETS_SUM", "TIME_SAMPLE",
                               "ENUM_WALL_SEC", "FEASIBLE_SUBSETS", "VERTEX_COUNT", "SETS_EQUAL",
                               "MISMATCHES", "EXIT_", "EXPECT"], title="(m2=12, 8 线程)")
show(f"{D}/c_m12_t8_time.txt", None, title="(m2=12 墙钟)")
for s in ("a", "b", "c"):
    show(f"{D}/py_m12_slice_{s}_log.txt", ["TOTAL", "DECISION_COUNTS", "DECISIONS_MD5", "ELAPSED_SEC", "EXIT_OK"],
         title=f"(Python m2=12 分片 {s})")
print("=" * 70)
print("m2=13 进程状态：")
print("  c_m13_t8_log.txt 存在:", os.path.exists(f"{D}/c_m13_t8_log.txt"))
print("  c_m13_t8_time.txt 存在:", os.path.exists(f"{D}/c_m13_t8_time.txt"))
show(f"{D}/c_m13_t8_time.txt", None)
show(f"{D}/c_m13_t8_log.txt", ["TOTAL_SUBSETS", "DECISION_COUNTS", "CROSSCHECK", "ENUM_WALL_SEC",
                               "FEASIBLE_SUBSETS", "VERTEX_COUNT", "SETS_EQUAL", "MISMATCHES", "EXIT_"],
     title="(m2=13, 进行中或已完成)")
print("=" * 70)
print("源文件 md5：")
for p in ["route2_vm_main.c", "route2_vm_core.c", "route2_vm_core.h", "route2_vm_enum",
          "route2_ref_enum.py", "frozen/r2_common.py", "frozen/r2_j_independent_vertices.py"]:
    print("  ", md5(p), p)
print()
print("结果目录文件清单：")
for fn in sorted(os.listdir(D)):
    fp = os.path.join(D, fn)
    if os.path.isfile(fp):
        print("  %10d  %s" % (os.path.getsize(fp), fn))
