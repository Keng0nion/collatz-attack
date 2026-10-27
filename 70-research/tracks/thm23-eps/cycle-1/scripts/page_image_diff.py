#!/usr/bin/env python
"""路线 1 辅助脚本：把印出版与 arXiv v3 逐页渲染图做差分，定位两版出现差异的页与区域。

用法：
  /Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python page_image_diff.py \
      印出版.pdf arXivv3.pdf 起页 止页 输出目录

输出：每页的差异像素数与差异包围盒（若差异超过阈值）。
注意：本脚本只做机制定位（找出差异出现在哪一页、哪一区域），不承担任何数学判决，
     也不用于判定「取整或笔误」——那属于下游严格算术路线的职责。
"""
import os
import subprocess
import sys

from PIL import Image, ImageChops


def render(pdf: str, page: int, outdir: str, tag: str) -> str:
    base = os.path.join(outdir, f"{tag}_{page}")
    subprocess.run(
        ["pdftoppm", "-png", "-r", "110", "-f", str(page), "-l", str(page), pdf, base],
        check=True,
    )
    for name in os.listdir(outdir):
        if name.startswith(f"{tag}_{page}-") and name.endswith(".png"):
            return os.path.join(outdir, name)
    raise FileNotFoundError(f"render failed for {tag} page {page}")


def diff_page(a: str, b: str) -> tuple:
    im1 = Image.open(a).convert("L")
    im2 = Image.open(b).convert("L")
    if im1.size != im2.size:
        im2 = im2.resize(im1.size)
    d = ImageChops.difference(im1, im2)
    bbox = d.getbbox()
    hist = d.histogram()
    npx = sum(hist[25:])
    return npx, bbox


def main() -> None:
    pdf_a, pdf_b, p0, p1, outdir = sys.argv[1:6]
    p0, p1 = int(p0), int(p1)
    os.makedirs(outdir, exist_ok=True)
    print(f"OUTDIR {outdir}")
    for page in range(p0, p1 + 1):
        fa = render(pdf_a, page, outdir, "PR")
        fb = render(pdf_b, page, outdir, "V3")
        npx, bbox = diff_page(fa, fb)
        print(f"page {page}: diffpx={npx} bbox={bbox}")


if __name__ == "__main__":
    main()
