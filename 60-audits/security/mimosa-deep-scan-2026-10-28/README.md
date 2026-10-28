# 安全审计清偿：Mimosa 深度扫描（2026 年 10 月 28 日）

## 为什么有这一档

本仓库此前的历次提交前扫描一直不完整（钩子报「扫描结论不完整，scanner_enobufs，不要宣称项目安全」）。本次在 2026 年 10 月 28 日完整跑通了一次 Mimosa 深度扫描，把这份欠账清偿，扫描原件与本说明一并入库。

## 扫描记录

| 项 | 值 |
| --- | --- |
| 扫描 ID | `scan-2026-10-28T13-16-49.918Z-bec62bd1a500` |
| 深度 | deep（静态，不运行项目代码） |
| 封印 | `sha256:8a60e0f24c2d196e70236ad1c530af6d73dd354e8518b1b651ee04ba5f6d1ed6` |
| 本地原件目录 | `~/.mimosa/security-scans/project-9bb3da6d8978b5754c62eebf/scan-2026-10-28T13-16-49.918Z-bec62bd1a500/` |
| 入库副本 | 本目录（`report.md`、`findings.json`、`coverage.json`、`seal.json`） |
| 结论口径 | 运行状态 **inconclusive**（扫描器自己的口径），覆盖完整度 **partial**；缺口为「调用图部分不完整，跨文件可达性可能不完整」（动态派发或超出分析规模） |

## 发现汇总（160 条，0 条严重、0 条凭据泄露）

1. **HIGH · 路径穿越模式命中 83 条**：全部是「命令行参数流入文件读取函数」的模式匹配，集中在 `20-experiments/scripts/`、`30-proof-attempts/*/scripts/`、`60-audits/*/scripts/`、`70-research/tracks/*/scripts/` 下的本地实验脚本（例如 `round2_verify.py:739` 的 main、`route3_verify.py:72` 的 read_result）。这些脚本均由仓库所有者在本机直接运行、不对外提供任何服务，参数就是所有者自己传的路径，**按设计接受，不做修改**；若未来把其中任何脚本改成网络服务，必须先补路径校验。
2. **LOW · 不安全的随机数 57 条**：实验脚本里使用 `random` 模块做抽样与搜索（例如 `parity_vectors.py`、`exact_check.py`、`rederive-erratum.py`）。非密码学用途，**按设计接受**；与可复现性相关的种子问题由各实验自己的记录负责。
3. **MEDIUM · clang 静态分析 20 条**：一次性实验二进制里的内存泄漏（`reverse_tree_deep.c`、`stoptime_dist.c`，进程退出即回收）、死存储（`cycles_verify_bound.c` 四处 `resolved`）、一处除零路径与一处流用法。**按设计接受**，不影响任何结论的正确性。
4. **零 CRITICAL；无凭据、密钥、令牌类发现**：对公开仓库而言这是本次扫描最重要的结论。

## 声明（引用纪律）

本次扫描是**静态**扫描（未运行项目代码），且其自带覆盖缺口如上；因此本仓库**不宣称「已通过安全审计」**。可以照写的最强句是：2026 年 10 月 28 日完整跑通一次 Mimosa 深度扫描（封印如上），160 条发现全部归类如上，未发现凭据泄露。复现方式：以同一项目路径重跑 Mimosa 深度扫描（`security_scan`，depth=deep）。
