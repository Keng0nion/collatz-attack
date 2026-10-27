#!/usr/bin/env python
"""路线 1 终检脚本：取出印出版与 arXiv v3 第 15 页中含 bounnd 的整行，并打印 10^{-43} 的坐标证据。

用途：为「第七步印数在两版是否逐字相同」与「−43 是否为上标」提供可复核的一行输出。
用法：
  /Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python final_verify.py
  （本机 venv 无 fitz 模块；本脚本只用 pdftotext 与标准库，故 venv 可直接运行。）

判定口径：
  1. 文字层的一行转录只用于逐字比对；
  2. 上标判定用 glyph 盒的 yMin 偏移量做对照：把同页所有形如「· 10^e」的指数与底数 10 的 yMin 之差列表，
     若 −43 的偏移与同页已知正上标（如 17、20、21）的偏移同类，则判为上标。
  3. 该脚本不做任何数学判决。
"""
import re
import subprocess

TRACK = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/thm23-eps/cycle-1"
PRINTED = f"{TRACK}/materials/hercher5.pdf"
V3 = f"{TRACK}/materials/arxiv-2201.00406v3.pdf"
TMP = "/tmp/route1_final_verify_bbox.html"


def words(path: str, page: int) -> list:
    subprocess.run(
        ["pdftotext", "-f", str(page), "-l", str(page), "-bbox", path, TMP],
        check=True,
    )
    html = open(TMP, encoding="utf-8", errors="replace").read()
    ws = re.findall(
        r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>',
        html,
    )
    return [[float(a), float(b), float(c), float(d), e] for a, b, c, d, e in ws]


def line_with(ws: list, needle: str) -> tuple:
    """返回含 needle 的最靠下（y 最大）那一行的词表，以及该词表按 x 排序的拼接。"""
    hit = [w for w in ws if needle in w[4]]
    if not hit:
        return None, f"(未找到 {needle!r})"
    w0 = max(hit, key=lambda w: w[1])
    band = [w for w in ws if abs(w[1] - w0[1]) < 8]
    band.sort(key=lambda w: w[0])
    return band, " ".join(w[4] for w in band)


def exponent_offsets(ws: list) -> list:
    """列出同页每个「10」与其右侧相邻指数词的 yMin 之差（负数表示指数在上）。"""
    out = []
    for i, w in enumerate(ws):
        if w[4] == "10":
            nxt = [x for x in ws if x[0] > w[2] - 0.5 and abs(x[1] - w[1]) < 6]
            nxt.sort(key=lambda x: x[0])
            if nxt:
                e = nxt[0]
                out.append((e[4], round(e[1] - w[1], 3), round(e[3] - e[1], 2)))
    return out


def main() -> None:
    for tag, path in [("PRINTED", PRINTED), ("V3", V3)]:
        print(f"=== {tag} 第 15 页，含 'bounnd' 的行 ===")
        ws = words(path, 15)
        _, text = line_with(ws, "bounnd")
        print(text)
        print()
        print(f"--- {tag} 第 15 页所有「10 + 指数」的（指数, yMin 偏移, 指数盒高） ---")
        for e, dy, h in exponent_offsets(ws):
            print(f"    {e!r:8} dy={dy:+.3f}  高度={h}")
        print()


if __name__ == "__main__":
    main()
