#!/bin/zsh
# r5_run_all.sh —— vertex-m12 轨道路线五：一键复跑（本报告 route-5.md 的全部命令行）。
# 用法：
#   zsh r5_run_all.sh anchors     # 三向对照（阳性 m2=10 原脚本、阴性 r1_selfcheck、E10 与 m2=2 双引擎冒烟）
#   zsh r5_run_all.sh full10      # m2=10 八核双引擎
#   zsh r5_run_all.sh full12      # m2=12 八核双引擎（主档）
#   zsh r5_run_all.sh full13      # m2=13 八核 mpq（fraction 未跑，见报告节三第 10 条）
#   zsh r5_run_all.sh full14      # m2=14 八核 mpq（32 分片交替派发；本机约 1 小时量级）
#   zsh r5_run_all.sh probes      # 三段窗口测速探针与逐子集样本 diff
# 说明：所有输出重定向到 ../results/ 下；日志头逐次打印 δ、W、组合数与依赖文件 md5（不符即中止）。
set -u
PY="/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python"
ROOT="/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/vertex-m12/cycle-1"
REF="/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts"
LOGS="$ROOT/results/logs"
SMOKE="$ROOT/results/r5_smoke"
mkdir -p "$LOGS" "$SMOKE"

case "${1:-help}" in
anchors)
  cd "$REF"
  { time "$PY" r2_j_independent_vertices.py A ; } > "$LOGS/r5_anchor_r2j_A_original.txt" 2>&1
  { time "$PY" r1_selfcheck.py ; }               > "$LOGS/r5_anchor_r1_selfcheck_original.txt" 2>&1
  cd "$ROOT/scripts"
  "$PY" r5_vm12_enum.py --m2 5 --W threshold --impl fraction --workers 1 --chunks 1 --tag smoke_m2_5     > "$SMOKE/smoke_m2_5_fraction.log" 2>&1
  "$PY" r5_vm12_enum.py --m2 5 --W threshold --impl mpq      --workers 1 --chunks 1 --tag smoke_m2_5_mpq > "$SMOKE/smoke_m2_5_mpq.log" 2>&1
  "$PY" r5_vm12_enum.py --m2 2 --delta 3/2 --W 3/2 --impl fraction --workers 1 --chunks 1 --tag smoke_m2_2     > "$SMOKE/smoke_m2_2_fraction.log" 2>&1
  "$PY" r5_vm12_enum.py --m2 2 --delta 3/2 --W 3/2 --impl mpq      --workers 1 --chunks 1 --tag smoke_m2_2_mpq > "$SMOKE/smoke_m2_2_mpq.log" 2>&1
  ;;
full10)
  cd "$ROOT/scripts"
  /usr/bin/time -p "$PY" r5_vm12_enum.py --m2 10 --W 2000 --impl fraction --workers 8 --chunks 16 --tag m2_10_fraction > "$LOGS/r5_full_m2_10_fraction.log" 2> "$LOGS/r5_full_m2_10_fraction.time"
  /usr/bin/time -p "$PY" r5_vm12_enum.py --m2 10 --W 2000 --impl mpq      --workers 8 --chunks 16 --tag m2_10_mpq      > "$LOGS/r5_full_m2_10_mpq.log"      2> "$LOGS/r5_full_m2_10_mpq.time"
  ;;
full12)
  cd "$ROOT/scripts"
  /usr/bin/time -p "$PY" r5_vm12_enum.py --m2 12 --W 2000 --impl fraction --workers 8 --chunks 16 --tag m2_12_fraction > "$LOGS/r5_full_m2_12_fraction.log" 2> "$LOGS/r5_full_m2_12_fraction.time"
  /usr/bin/time -p "$PY" r5_vm12_enum.py --m2 12 --W 2000 --impl mpq      --workers 8 --chunks 16 --tag m2_12_mpq      > "$LOGS/r5_full_m2_12_mpq.log"      2> "$LOGS/r5_full_m2_12_mpq.time"
  ;;
full13)
  cd "$ROOT/scripts"
  /usr/bin/time -p "$PY" r5_vm12_enum.py --m2 13 --W 2000 --impl mpq --workers 8 --chunks 16 --tag m2_13_mpq > "$LOGS/r5_full_m2_13_mpq.log" 2> "$LOGS/r5_full_m2_13_mpq.time"
  ;;
full13fraction)
  cd "$ROOT/scripts"
  /usr/bin/time -p "$PY" r5_vm12_enum.py --m2 13 --W 2000 --impl fraction --workers 8 --chunks 32 --interleave --tag m2_13_fraction > "$LOGS/r5_full_m2_13_fraction.log" 2> "$LOGS/r5_full_m2_13_fraction.time"
  ;;
full14)
  cd "$ROOT/scripts"
  /usr/bin/time -p "$PY" r5_vm12_enum.py --m2 14 --W 2000 --impl mpq --workers 8 --chunks 32 --interleave --tag m2_14_mpq > "$LOGS/r5_full_m2_14_mpq.log" 2> "$LOGS/r5_full_m2_14_mpq.time"
  ;;
probes)
  cd "$ROOT/scripts"
  for m in 10 12 13 14; do
    K=3000; if [ "$m" -ge 13 ]; then K=1500; fi
    for impl in fraction mpq; do
      /usr/bin/time -p "$PY" r5_vm12_enum.py --m2 $m --impl $impl --probe $K --tag probe_m${m}_${impl} > "$SMOKE/probe_m${m}_${impl}.log" 2> "$SMOKE/probe_m${m}_${impl}.time"
    done
  done
  "$PY" r5_vm12_enum.py --m2 10 --impl fraction --dump-sample 3000 --out-sample "$SMOKE/sample_m2_10_fraction.txt" > "$SMOKE/sample_m2_10_fraction.log" 2>&1
  "$PY" r5_vm12_enum.py --m2 10 --impl mpq      --dump-sample 3000 --out-sample "$SMOKE/sample_m2_10_mpq.txt"      > "$SMOKE/sample_m2_10_mpq.log"     2>&1
  "$PY" r5_vm12_enum.py --m2 12 --impl fraction --dump-sample 1500 --out-sample "$SMOKE/sample_m2_12_fraction.txt" > "$SMOKE/sample_m2_12_fraction.log" 2>&1
  "$PY" r5_vm12_enum.py --m2 12 --impl mpq      --dump-sample 1500 --out-sample "$SMOKE/sample_m2_12_mpq.txt"      > "$SMOKE/sample_m2_12_mpq.log"     2>&1
  diff "$SMOKE/sample_m2_10_fraction.txt" "$SMOKE/sample_m2_10_mpq.txt" && echo "sample m2=10: 两引擎逐字相同"
  diff "$SMOKE/sample_m2_12_fraction.txt" "$SMOKE/sample_m2_12_mpq.txt" && echo "sample m2=12: 两引擎逐字相同"
  ;;
*)
  echo "用法：zsh r5_run_all.sh {anchors|full10|full12|full13|full13fraction|full14|probes}"
  ;;
esac
