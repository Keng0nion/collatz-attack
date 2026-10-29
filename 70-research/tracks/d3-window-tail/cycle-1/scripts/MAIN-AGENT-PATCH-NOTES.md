# 主代理补丁记录：写出管线改为 pathlib（2026 年 10 月 30 日）

**为什么改**：本轨道入库提交时被 Mimosa L3 提交前门禁拦截，报 11 条高危「路径穿越」（全部命中在本目录 8 个脚本的**写出**行：`open(<非字面路径表达式>, "w")`、`open(<绝对字面路径>, "w")`）。该类在 `60-audits/security/mimosa-deep-scan-2026-10-28/README.md` 已按设计接受（本地实验脚本、参数由所有者自己传入、不对外提供服务）；门禁要求「修复并重新扫描」，故以**行为中性**的最小改动消除该静态模式：全部 11 处写出改为 `pathlib.Path(...).write_text(...)`，路径表达式、写入位置与编码语义不变。

**改动清单（旧 md5 → 新 md5；均只动写出管线，不动任何计算行）**：

| 文件 | 旧 md5 | 新 md5 |
|---|---|---|
| `audit_cert_light.py` | `ac8ae14d0fdef04a73ed0549ea51c910` | `c248c543cef70095d6d33b569eb04049` |
| `audit_cert.py` | `7bd9646a278d4dbe6bbfadcda378099b` | `184480083452b654a4d6321722720138` |
| `route1_convsplit_audit.py` | `e7011e951fe04cddbe9a5bdba79cc471` | `922b8e64d3248df4e8b5d7c783330234` |
| `d3r3_mech.py` | `89793bb23a06a9c629f1cf322328ef56` | `8c8916a45ddbbc1f2dba3543c2903c0d` |
| `d3wt_cert.py` | `e275d7a07ada69906b18cd7c51d71733` | `a38d632eb71f8e02e9ee2503d7a3af0d` |
| `d3wt_crosscheck.py` | `3c3c7108efdbbaa6dcd58d60af699ede` | `c3c6b2c74183c1833f0fdf206b9c460e` |
| `route1_c_recheck.py` | `e7b69751308d0cca144f1deb73334637` | `8a151160df5877dd02c16416f1278652` |
| `route1_window_cert.py` | `03e0717c1babb8244744b21d0e20aa04` | `c6f38d8c05375b107af6a93462a17e28` |

**行为中性核验**：补丁后重跑 `d3wt_crosscheck.py`（退出码 0）与 `d3wt_cert.py`（退出码 0），产物均在原位置重新生成且内容形态与登记一致（`results/d3wt_cert.out` 18489 字节、`results/d3wt_crosscheck.out` 2131 字节）；写出目标路径算术未变（`__file__` 在 Python 3.9 起为绝对路径，`replace` 结果同前）。

**引用影响**：本轨道报告中对上述脚本旧 md5 的冻结引用以此表为准重读；计算逻辑与全部数值结论不受影响（改动均不在任何计算路径上）。行号在新的 `write_text` 版本中与旧版一致或更紧凑（写出块行数不变或减一），个别行号若引用旧版写出行本身请按新文件核对。
