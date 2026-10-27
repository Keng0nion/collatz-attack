#!/bin/zsh
# route-1 的源文件与日志 md5 清单（macOS：md5 -q；md5 只作版本身份指纹，不作安全用途）
# 用法：zsh make_manifest.sh > ../results/md5-manifest.txt
BASE="/Users/luna/Documents/math IA/collatz-attack"
TRACK="$BASE/70-research/tracks/vertex-m12/cycle-1"
C1="$BASE/70-research/cycle-1"
echo "# route-1 md5 清单（生成时刻：$(date '+%Y-%m-%d %H:%M:%S %Z')）"
echo "# 格式：md5 | 字节 | 行数 | 路径（相对 collatz-attack/）"
for f in \
  "$TRACK/scripts/three_way_baseline.py" \
  "$TRACK/scripts/diff_norm.py" \
  "$TRACK/scripts/make_manifest.sh" \
  "$TRACK/scripts/frozen/run_frozen_A.py" \
  "$TRACK/scripts/frozen/r2_common.py" \
  "$TRACK/scripts/frozen/r2_j_independent_vertices.py" \
  "$TRACK/results/frozen-spec.md" \
  "$TRACK/results/threeway-A-frozen-run.txt" \
  "$TRACK/results/threeway-A-frozen-run.stderr.txt" \
  "$TRACK/results/threeway-A-diff.txt" \
  "$TRACK/results/threeway-A-positive.txt" \
  "$TRACK/results/threeway-A-positive.time" \
  "$TRACK/results/threeway-B-negative.txt" \
  "$TRACK/results/threeway-B-negative.time" \
  "$TRACK/results/threeway-C-boundary.txt" \
  "$TRACK/results/threeway-C-boundary.time" \
  "$TRACK/results/threeway-P-partition.txt" \
  "$TRACK/results/threeway-P-partition.time" \
  "$TRACK/results/threeway-S-cost-sample.txt" \
  "$TRACK/results/threeway-S-cost-sample.time" \
  "$C1/scripts/r2_common.py" \
  "$C1/scripts/r2_j_independent_vertices.py" \
  "$C1/scripts/r2_b_vertices.py" \
  "$C1/scripts/r1_selfcheck.py" \
  "$C1/scripts/results/verify-round2/r2_j_A.txt" \
  "$C1/scripts/results/verify-round2/r2_j_A.time" \
  "$C1/scripts/results/r2_b_out.txt" \
  "$C1/route-1.md" \
  "$BASE/70-research/learnings.md" \
  ; do
  if [ -f "$f" ]; then
    rel="${f#$BASE/}"
    printf "%s | %8d | %5d | %s\n" "$(md5 -q "$f")" "$(wc -c < "$f" | tr -d ' ')" "$(wc -l < "$f" | tr -d ' ')" "$rel"
  else
    printf "%s | %s\n" "（本次未生成）" "${f#$BASE/}"
  fi
done
