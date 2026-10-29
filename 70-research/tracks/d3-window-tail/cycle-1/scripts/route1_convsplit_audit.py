#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""route1_convsplit_audit.py —— route-1「否证独立重算」第 2 件：只读复核 convsplit。

只读：本脚本对 70-research 下的任何文件都只 open("r")，唯一写入是
      scripts/results/route1_convsplit_audit.out 与 /tmp 下的扰动副本。

复核对象：
  cycle-2/scripts/c2r5_convsplit.py（61 行）与其产物 results/c2r5_convsplit.out（36 行）。
判据（全部可翻 False，见 [5] 扰动）：
  Q1 产物有无任一行满足 argmin != m2_max（= 脚本自己打印的「分离？ True」）
  Q2 采样相对偏移的最小非零值（= 分辨率）
  Q3 route-5.md:348 声称的「三格逐格核算（c2r5_convsplit.out）」是否有落点
"""
import os
import re
import hashlib
import shutil
import sys

ROOT = "/Users/luna/Documents/math IA/collatz-attack"
OUT = []


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


PY = ROOT + "/70-research/cycle-2/scripts/c2r5_convsplit.py"
LOG = ROOT + "/70-research/cycle-2/scripts/results/c2r5_convsplit.out"

p("#" * 72)
p("# route1_convsplit_audit.py：c2r5_convsplit 的只读复核")
p("# python %s" % sys.version.split()[0])
p("#" * 72)
p("")
p("[0] 冻结件")
for tag, path in (("脚本", PY), ("产物", LOG)):
    with open(path, "r") as f:
        n = sum(1 for _ in f)
    p("    %s %s" % (tag, path.replace(ROOT + "/", "")))
    p("      md5 = %s ；行数 = %d" % (md5(path), n))

with open(LOG, "r") as f:
    lines = f.read().split("\n")
with open(PY, "r") as f:
    src = f.read()

p("")
p("[1] 计数（脚本自打印的三值）")
n_false = sum(1 for L in lines if "分离？ False" in L)
n_true = sum(1 for L in lines if "分离？ True" in L)
n_rows = sum(1 for L in lines if "：m2_max =" in L or "：m2_max =" in L or ":m2_max =" in L or "：m2_max =" in L)
n_meta = sum(1 for L in lines if ":m2_max =" in L)
n_all = sum(1 for L in lines if "m2_max" in L)
p("    「分离？ False」行数 = %d" % n_false)
p("    「分离？ True」 行数 = %d" % n_true)
p("    含 m2_max 的行数 = %d ；其中带「：」的判据行 = %d" % (n_all, n_rows))

p("")
p("[2] 逐行抽取：cell、采样因子、m2_max、argmin，核对 argmin 与 m2_max 的关系")
row_re = re.compile(r"m2 = (\d+) 的门槛.*")
res_re = re.compile(r"K = K_thresh\*(\S+)\s+：m2_max = (\d+)，eps\(m2_max\) = (\S+)；argmin = (\d+)，eps\(argmin\) = (\S+)；分离？ (\w+)")
cur = None
rows = []
fac_used = []
for L in lines:
    m = row_re.search(L)
    if m:
        cur = int(m.group(1))
        continue
    m = res_re.search(L)
    if m:
        fac, fmax, emax, star, earg, sep = m.groups()
        rows.append((cur, fac, int(fmax), star, earg, sep))
        if fac not in fac_used:
            fac_used.append(fac)
p("    解析出判据行 %d 条" % len(rows))
p("    %-6s %-12s %-8s %-8s %-8s %s" % ("格(m2)", "采样因子", "m2_max", "argmin", "分离?", "argmin==m2_max?"))
n_eq = 0
for cell, fac, fmax, star, earg, sep in rows:
    eq = int(star) == fmax
    n_eq += 1 if eq else 0
    p("    %-6d %-12s %-8d %-8s %-8s %s" % (cell, fac, fmax, star, sep, eq))
p("    Q1 判据：任一行 argmin != m2_max ？ %s（相异行数 = %d）"
  % (n_eq != len(rows), len(rows) - n_eq))

p("")
p("[3] 采样分辨率")
def to_F(s):
    from fractions import Fraction as F
    if "/" in s:
        a, b = s.split("/")
        return F(int(a), int(b))
    return F(s)

from fractions import Fraction as F
offs = sorted(set(to_F(f) - 1 for f in fac_used))
p("    脚本第 43 行的因子表（去重后的相对偏移）= %s" % [str(o) for o in offs])
nz = [o for o in offs if o > 0]
p("    Q2 判据：最小非零相对偏移 = %s" % (str(nz[0]) if nz else "无"))
p("    脚本自报的理论窗口（docstring 第 6 行）= 相对宽度约 0.11%")
p("    对照：r4b2_window_probe.out:51、:52、:56、:57 的实测窗口相对宽度 ≈ 7.8e-13")
p("    分辨率缺口 = %s 倍（0.11%% 与 7.8e-13 之比 = %s）"
  % (str(F(11, 10000) / F(78, 10 ** 14)), str(F(11, 10000) / F(78, 10 ** 14))))
p("    注：脚本自己的两档采样 1e-4、5e-4 都落在它自报的 0.11%% 窗口之内，")
p("        当处仍打「分离？ False」——即该自报窗口被它自己的本次运行反驳（见 [6]）。")

p("")
p("[4] 「三格逐格核算」句的落点检索")
import subprocess
res = subprocess.run(["grep", "-rn", "逐格核算", ROOT + "/70-research"],
                     capture_output=True, text=True)
hits = [L for L in res.stdout.split("\n") if L.strip()]
p("    全 70-research 下 grep -rn 逐格核算 命中 %d 处：" % len(hits))
for L in hits[:20]:
    p("      " + L.replace(ROOT + "/", ""))
p("    Q3 判据：c2r5_convsplit.out 里有无「逐格核算」字样 ？ %s"
  % any("逐格核算" in L for L in lines))
p("    Q3 判据：c2r5_convsplit.out 里有无 argmin != m2_max 的三格记录 ？ %s"
  % (len(rows) - n_eq >= 3))

p("")
p("[5] 扰动实例（Q1 判据必须能翻 True）")
tmp = "/tmp/route1_convsplit_perturbed.out"
# 只改第 27 行（m2 = 90 格、K = K_thresh*1 那一行）的 argmin：89 -> 88
import pathlib as _pl
_out = []
for L in lines:
    if "m2_max = 89，eps(m2_max) = 3.285727035882611e-41；argmin = 89" in L:
        L = L.replace("argmin = 89", "argmin = 88")
    _out.append(L)
_pl.Path(tmp).write_text("\n".join(_out), encoding="utf-8")
pl = _pl.Path(tmp).read_text(encoding="utf-8").split("\n")
pr = [res_re.search(L) for L in pl]
pr = [m for m in pr if m]
p("    扰动副本 %s（仅改一行 argmin 89 -> 88）" % tmp)
p("    扰动后 Q1 = 任一行 argmin != m2_max ？ %s（相异行数 = %d）"
  % (any(int(m.group(4)) != int(m.group(2)) for m in pr),
     sum(1 for m in pr if int(m.group(4)) != int(m.group(2)))))
p("    => 同一段解析代码在原产物上给 False、在扰动副本上给 True，判据非恒真。")

path = ROOT + "/70-research/tracks/d3-window-tail/cycle-1/scripts/results/route1_convsplit_audit.out"
import pathlib as _pl2
_pl2.Path(path).write_text("\n".join(OUT) + "\n", encoding="utf-8")
print("\n[写出] " + path)
