#!/bin/sh
# route2 数值汇总（供报告引用；只读，不修改任何文件）
set -u
cd "$(dirname "$0")" || exit 1
D=results/route2
echo "===== 文件清单 ====="
ls -la "$D" | grep -E "c_m1[02]|c_m5|py_m10|py_m12" || true
echo
echo "===== m2=5 (E10) ====="
sed -n '/DECISION_COUNTS/p;/CROSSCHECK/p;/SETS_EQUAL/p;/EXIT_/p' "$D/m5_e10_log.txt"
echo
echo "===== m2=10 C 八线程 ====="
sed -n '/TOTAL_SUBSETS/p;/DECISION_COUNTS/p;/CROSSCHECK/p;/ENUM_WALL_SEC/p;/TIME_SAMPLE/p;/THREAD_SETS_SUM/p;/FEASIBLE_SUBSETS/p;/VERTEX_COUNT/p;/SETS_EQUAL/p;/MISMATCHES/p;/EXIT_/p' "$D/c_m10_t8_log.txt"
echo "-- 墙钟（time 文件）:"
sed -n '1,6p' "$D/c_m10_t8_time.txt"
echo
echo "===== m2=10 C 单线程 ====="
sed -n '/DECISION_COUNTS/p;/CROSSCHECK/p;/SETS_EQUAL/p;/EXIT_/p' "$D/c_m10_t1_log.txt"
sed -n '1,6p' "$D/c_m10_t1_time.txt"
echo
echo "===== m2=10 Python 参考 ====="
sed -n '/DECISION_COUNTS/p;/DECISIONS_MD5/p;/ELAPSED_SEC/p;/ANALYTIC_COUNT/p;/EXIT_OK/p' "$D/py_m10_log.txt"
echo
echo "===== 判串 md5（三方） ====="
md5 -q "$D/c_m10_t8_decisions.txt" "$D/c_m10_t1_decisions.txt" "$D/py_m10_decisions.txt"
echo
echo "===== m2=12 C 八线程 ====="
sed -n '/TOTAL_SUBSETS/p;/DECISION_COUNTS/p;/CROSSCHECK/p;/ENUM_WALL_SEC/p;/TIME_SAMPLE/p;/THREAD_SETS_SUM/p;/FEASIBLE_SUBSETS/p;/VERTEX_COUNT/p;/SETS_EQUAL/p;/MISMATCHES/p;/EXIT_/p' "$D/c_m12_t8_log.txt"
echo "-- 墙钟（time 文件）:"
sed -n '1,6p' "$D/c_m12_t8_time.txt"
echo "-- 判串 md5 与字节数:"
md5 -q "$D/c_m12_t8_decisions.txt"
wc -c < "$D/c_m12_t8_decisions.txt"
echo
echo "===== m2=12 Python 三段分片 ====="
for s in a b c; do
  sed -n '/DECISION_COUNTS/p;/DECISIONS_MD5/p;/ELAPSED_SEC/p;/EXIT_OK/p' "$D/py_m12_slice_${s}_log.txt"
done
echo
echo "===== 源文件与二进制 md5 ====="
md5 -q route2_vm_main.c route2_vm_core.c route2_vm_core.h route2_vm_enum route2_ref_enum.py frozen/r2_common.py
