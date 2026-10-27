#!/bin/zsh
# 路线 1 复现脚本：重下三份原件、打印 md5 与字节数、渲染关键页。
# 用法：
#   cd /Users/luna/Documents/math IA/collatz-attack/70-research/tracks/thm23-eps/cycle-1/scripts
#   ./reproduce_hash.sh
# 复核口径：输出里的 md5 与字节数应与 route-1.md 第 2 节表格逐位一致。
set -u
OUT=/tmp/route1_redownload
mkdir -p "$OUT"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

echo "=== 下载 1：JIS 印出版 hercher5.pdf ==="
curl -sS -L -A "$UA" -w "HTTP=%{http_code} SIZE=%{size_download} URL=%{url_effective}\n" \
  -o "$OUT/hercher5.pdf" \
  "https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/hercher5.pdf"

echo "=== 下载 2：勘误 corrigendum.pdf ==="
curl -sS -L -A "$UA" -w "HTTP=%{http_code} SIZE=%{size_download} URL=%{url_effective}\n" \
  -o "$OUT/corrigendum.pdf" \
  "https://cs.uwaterloo.ca/journals/JIS/VOL26/Hercher/corrigendum.pdf"

echo "=== 下载 3：arXiv v3 ==="
curl -sS -L -A "$UA" -w "HTTP=%{http_code} SIZE=%{size_download} URL=%{url_effective}\n" \
  -o "$OUT/arxiv-2201.00406v3.pdf" \
  "https://arxiv.org/pdf/2201.00406v3"

echo "=== md5 与字节数（本次下载） ==="
for f in "$OUT"/hercher5.pdf "$OUT"/corrigendum.pdf "$OUT"/arxiv-2201.00406v3.pdf; do
  printf "%s\t%s\t%s\n" "$(basename $f)" "$(md5 -q $f)" "$(stat -f %z $f)"
done

echo "=== md5 与字节数（轨道归档件） ==="
TRACK="/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/thm23-eps/cycle-1"
for f in "$TRACK"/materials/hercher5.pdf "$TRACK"/materials/corrigendum.pdf "$TRACK"/materials/arxiv-2201.00406v3.pdf; do
  printf "%s\t%s\t%s\n" "$(basename $f)" "$(md5 -q $f)" "$(stat -f %z $f)"
done

echo "=== 渲染第 13 至 16 页 ==="
mkdir -p "$OUT/pages"
for p in 13 14 15 16; do
  pdftoppm -png -r 150 -f $p -l $p "$OUT/hercher5.pdf" "$OUT/pages/printed_p$p"
  pdftoppm -png -r 150 -f $p -l $p "$OUT/arxiv-2201.00406v3.pdf" "$OUT/pages/v3_p$p"
done
ls -1 "$OUT/pages"
