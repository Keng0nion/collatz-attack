#!/usr/bin/env python
"""路线 1 收尾自查：检查 route-1.md 正文是否出现半角连字符，以及是否残留未完成表述。

用法：
  python3 check_style.py <报告路径>

判定：代码块内、表格分隔行内、以及路径或专名等「逐字引用」不计；其余出现即报告。
"""
import re
import sys


def main() -> None:
    path = sys.argv[1]
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    in_code = False
    hits = []
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        stripped = line.strip()
        if stripped.startswith("|") and set(stripped) <= set("|-: "):
            continue
        for m in re.finditer(r"[A-Za-z\u4e00-\u9fff]-[A-Za-z\u4e00-\u9fff]", line):
            hits.append((i, stripped[:90]))
    print(f"LINES {len(lines)}")
    print(f"PROSE_HYPHEN_HITS {len(hits)}")
    for h in hits[:30]:
        print(h)
    for key in ["让我", "待补", "TODO", "将补", "试着"]:
        print(f"KEY {key} {text.count(key)}")


if __name__ == "__main__":
    main()
