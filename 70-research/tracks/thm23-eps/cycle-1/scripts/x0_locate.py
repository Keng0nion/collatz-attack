#!/usr/bin/env python
"""路线 1 辅助脚本：用 PyMuPDF 定位两版 X0（695 与 704）以及定理 23 段落所在页行。

用法：
  /Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python x0_locate.py <pdf路径>

输出：每页中含候选数字串（695、704）或含 X 的行，附页号与行号。
"""
import sys
import fitz


def scan(path: str) -> None:
    doc = fitz.open(path)
    print(f"FILE {path}")
    print(f"PAGES {doc.page_count}")
    for pno in range(doc.page_count):
        page = doc[pno]
        text = page.get_text("text")
        lines = text.splitlines()
        for lno, line in enumerate(lines):
            if ("695" in line) or ("704" in line):
                print(f"  page {pno + 1} line {lno}: {line.strip()[:160]}")
    doc.close()


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        scan(arg)
