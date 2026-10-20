# 本机计算环境勘察记录（ENV.md）

勘察日期：2026 年 10 月 17 日
勘察方式：以下每一条均由本机 Bash 实测得到，命令与输出摘要随文附上。凡属于我的推断而非实测的结论，均已逐条标注「推断」。未做过的检查集中列在第八节，不与实测结论混排。
文件位置：`/Users/luna/Documents/math IA/collatz-attack/20-experiments/ENV.md`

一句话结论：本机是一个 8 核、8 GiB 内存、可用磁盘约 32 GB 的 Apple M2 笔记本；项目自带 venv 里 numpy、sympy、z3、gmpy2、python-flint 五个数学库齐备且实测可用；clang 21 原生 arm64 可用、OpenMP 可通过 Homebrew libomp 打开；本机没有任何形式化证明工具链（Lean、Coq、Isabelle 全无，PARI、Sage 全无）。

---

## 一、项目自带环境（`.venv`）：唯一推荐的解释器

解释器全路径：

```
/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
```

### 1.1 版本

命令与输出：

```
$ "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" --version
Python 3.12.7
$ "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" -c "import sys; print(sys.executable); print(sys.version)"
/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
3.12.7 | packaged by Anaconda, Inc. | (main, Oct  4 2024, 08:22:19) [Clang 14.0.6 ]
```

### 1.2 已装库（`python -m pip list` 全量输出）

| 包 | 版本 |
|---|---|
| gmpy2 | 2.3.2 |
| mpmath | 1.3.0 |
| numpy | 2.5.4 |
| pip | 26.2.1 |
| python-flint | 0.9.0 |
| sympy | 1.14.0 |
| z3-solver | 5.3.1.0 |

任务点名的五个库逐个导入并打印版本（`z3` 的导入名是 `z3`，`python-flint` 的导入名是 `flint`）：

```
python : 3.12.7
numpy  : 2.5.4
sympy  : 1.14.0
z3     : 5.3.1
gmpy2  : 2.3.2
flint  : 0.9.0
mpmath : 1.3.0
```

结论：任务要求的五个数学库全部存在，无一缺失。

### 1.3 运行期冒烟测试（导入之外，实际算一遍）

在 venv 里执行了五个库各一次真实计算，全部通过，总耗时 0.65 秒：

| 库 | 测试内容 | 实测输出 | 判定 |
|---|---|---|---|
| gmpy2 | `is_prime(2^127 - 1)`（已知是梅森素数） | `True` | 通过 |
| python-flint | `fmpz(2)^64` | `18446744073709551616` | 通过 |
| sympy | `prime(100000)` | `1299709` | 通过 |
| numpy | `arange(10).sum()` | `45` | 通过 |
| z3 | 求解 `x*x == 49` 且 `x > 0` | `sat`，模型 `x = 7` | 通过 |

另做了一轮更深的 z3 测试（位向量、unsat 检测、大整数、一条科拉茨风格的奇偶约束），全部正常，耗时 0.02 秒：

```
bitvec SAT: sat 4
unsat detect: unsat
big-int: sat 3000000
collatz-style constraint: sat n = 1
```

### 1.4 numpy 的构建信息与 BLAS 后端

`numpy.show_config(mode='dicts')` 实测：

1. 编译它的编译器是 clang 15.0.0（这是官方 wheel 的构建环境，与本机 clang 21 无关）。
2. BLAS 与 LAPACK 后端均为 `accelerate`（macOS 系统自带 Accelerate 框架），`found: true`。

优缺点（推断）：Accelerate 对浮点矩阵运算很快，但科拉茨类工作以整数与位运算为主，走的是 GMP/FLINT 而非 BLAS，因此这项优势对本项目的核心计算帮助有限；numpy 在本项目里的合理定位是批量数据的容器与统计。

### 1.5 venv 的结构与依赖基础

`pyvenv.cfg` 原文：

```
home = /opt/anaconda3/bin
include-system-site-packages = false
version = 3.12.7
executable = /opt/anaconda3/bin/python3.12
command = /opt/anaconda3/bin/python3 -m venv /Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv
```

要点：

1. 该 venv 由系统的安纳康达 Python 创建，基础解释器是 `/opt/anaconda3/bin/python3.12`。
2. `include-system-site-packages = false`，即不继承安纳康达的 site-packages；实测 `sys.prefix` 指向 venv 自身，`sys.path` 里的 site-packages 只有 venv 自己那一个目录，隔离是干净的。
3. `bin/python3` 是一条指向 `/opt/anaconda3/bin/python3` 的符号链接，最终解析到 `/opt/anaconda3/bin/python3.12`。
4. 风险（推断）：这条链接使 venv 依赖安纳康达目录的存续。若将来升级、移动或删除 `/opt/anaconda3`，本 venv 会失效。我未做破坏性测试来验证这一点。

### 1.6 可移植性与命令行走廊

从 `/tmp` 目录调用该 venv 的 python，五个库仍能全部导入，说明 venv 不依赖当前工作目录：

```
$ cd /tmp && "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" -c "import numpy, sympy, z3, gmpy2, flint; print('cwd=/tmp 下全部五个库仍可导入 OK')"
cwd=/tmp 下全部五个库仍可导入 OK
```

venv 的 `bin/` 里除 python 外还带有以下可用命令行工具：`pip`、`isympy`、`f2py`、`numpy-config`，以及独立的 z3 求解器命令行：

```
$ "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/z3" --version
Z3 version 5.3.1 - 64 bit - build hashcode ac9156f97cb44e56472e1c841f7a2beb1e976b24
```

### 1.7 已知异常：`pip check` 对 z3-solver 报不支持

实测：

```
$ "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" -m pip check
z3-solver 5.3.1.0 is not supported on this platform
（退出码 1）
```

追查到的原因（实测证据）：

1. 该 wheel 的标签是 `py3-none-macosx_13_3_arm64`（读自 `z3_solver-5.3.1.0.dist-info/WHEEL`），带次版本号 13.3，而 pip 的平台标签生成规则对本机不会产生 `macosx_13_3_arm64` 这一条，于是判定为「不在兼容列表」。
2. 但该 wheel 实际打包了各平台原生库（同一目录里同时放着 `libz3.dylib` 与 Windows 的 `libz3.dll`、`msvcp140.dll`），文件类型实测为原生 arm64：

```
z3/lib/libz3.dylib: Mach-O 64-bit dynamically linked shared library arm64
```

3. 功能层面实测完全正常（1.3 节的位向量、unsat、大整数测试全部通过，z3 命令行也能跑）。

结论：`pip check` 的报错是 wheel 元数据层面的标签问题，不是功能故障；在本机可以正常使用 z3。影响（推断）：将来若要升级 z3-solver，pip 可能因标签不匹配而拒绝或需要额外参数；现有版本可继续用，不必动它。

同一目录下 gmpy2 与 flint 的原生扩展实测也均为 arm64：

```
gmpy2/gmpy2.cpython-312-darwin.so: Mach-O 64-bit bundle arm64
flint/types/fmpz_mat.abi3.so（同类 abi3 扩展）
numpy/_core/_multiarray_umath.cpython-312-darwin.so: Mach-O 64-bit bundle arm64
```

---

## 二、系统 python3：三个候选，都不满足实验需求

`which -a python3` 实测有三个，逐个查版本与库（查法是逐个解释器导入并用 `getattr` 取版本，失败即记为 MISSING）：

| 解释器 | 版本 | numpy | sympy | z3 | gmpy2 | flint | mpmath |
|---|---|---|---|---|---|---|---|
| `/opt/anaconda3/bin/python3` | 3.12.7 | 1.26.4 | 1.13.1 | 无 | 无 | 无 | 1.3.0 |
| `/opt/homebrew/bin/python3` | 3.14.7 | 2.5.3 | 无 | 无 | 无 | 无 | 无 |
| `/usr/bin/python3` | 3.9.6 | 无 | 无 | 无 | 无 | 无 | 无 |

补充实测：

1. 裸 `python3` 实际解析到 `/opt/anaconda3/bin/python3`（PATH 中 `/opt/anaconda3/bin` 排在 `/opt/homebrew/bin` 与 `/usr/bin` 之前），它是安纳康达基环境，缺 z3、gmpy2、flint 三个关键库。
2. 裸 `python` 也存在，是 `/opt/anaconda3/bin/python`，同样缺上述三个库。
3. `/opt/homebrew/bin/python3` 的真实可执行文件是 `/opt/homebrew/opt/python@3.14/bin/python3.14`，只有 numpy 2.5.3，连 sympy 都没有。
4. `/usr/bin/python3` 是苹果命令行工具的 Python 3.9.6，六个数学库一个都没有。
5. PATH 里还挂着一条 `/Library/Frameworks/Python.framework/Versions/3.12/bin`，但实测该目录不存在（`ls` 报 `No such file or directory`），是一条无效路径，不起作用。

结论：三个系统 Python 没有一个能用，任何脚本都不要指望它们。

---

## 三、C 编译器与并行能力

### 3.1 编译器版本（三个名字指向同一个编译器）

```
$ cc --version
Apple clang version 21.0.0 (clang-2100.3.34.2)
Target: arm64-apple-darwin27.0.0
Thread model: posix
InstalledDir: /Library/Developer/CommandLineTools/usr/bin

$ clang --version        （输出同上）
$ gcc --version          （输出同上）
```

要点：

1. `cc`、`clang`、`gcc` 三个名字在本机全部指向苹果 clang 21.0.0，`gcc` 只是替身，不是 GNU GCC。
2. 工具链来自命令行工具包，包版本 `com.apple.pkg.CLTools_Executables` = `27.0.0.0.1788430756`，`xcode-select -p` 输出 `/Library/Developer/CommandLineTools`。
3. 只装了命令行工具，没有完整 Xcode（实测 `/Applications/Xcode*.app` 无匹配）。

### 3.2 编译与运行实测（含 128 位整数）

写了一个用 `unsigned __int128` 做 `(1 << 100) + 12345` 的小程序，实测：

```
$ cc -O2 -o /tmp/_envtest /tmp/_envtest.c && /tmp/_envtest
C OK, __int128 high=68719476736 low=12345
（退出码 0）
```

结论：C 编译链路完整可用，128 位整数可用（对科拉茨的加速搜索有用，`3n + 1` 与位操作可以放心用宽整数）。

### 3.3 OpenMP

直接加 `-fopenmp` 不行，实测报错：

```
$ cc -fopenmp -o /tmp/_omptest /tmp/_omptest.c
clang: error: unsupported option '-fopenmp'
```

但 Homebrew 的 libomp 已装（`/opt/homebrew/opt/libomp` 存在，`/opt/homebrew/Cellar` 里有 `libomp`，含 `libomp.a` 与 `libomp.dylib`）。用苹果 clang 的标准写法实测编译并通过：

```
$ cc -Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib -lomp -o /tmp/_omptest2 /tmp/_omptest.c
$ /tmp/_omptest2
omp threads=8
```

结论：并行 C 可用，实测拿到 8 个 OpenMP 线程。后续若要写多线程穷举，用上面这条编译命令即可，不必再装东西。

---

## 四、硬件资源

| 项目 | 实测值 | 来源命令 |
|---|---|---|
| 机型标识 | `Mac14,2` | `sysctl -n hw.model` |
| 芯片 | Apple M2 | `sysctl -n machdep.cpu.brand_string` |
| CPU 总核数 | 8（物理 8，逻辑 8） | `sysctl -n hw.ncpu` / `hw.physicalcpu` / `hw.logicalcpu` |
| 核的构成 | 4 个性能核加 4 个能效核 | `hw.perflevel0.physicalcpu` = 4，`hw.perflevel1.physicalcpu` = 4 |
| 内存 | 8 GiB（8589934592 字节） | `sysctl -n hw.memsize` |
| 磁盘总容量 | 228 GiB（单一 APFS 容器） | `df -h` |
| 磁盘已用 | 167.4 GiB（`df` 报 `167Gi`，占用率 85%） | `df -h` / `df -k` |
| 磁盘可用 | `df` 报 `32Gi`；`df -k /System/Volumes/Data` 报 Avail=31886352（KB） | `df -h` / `df -k` |
| 家目录所在卷 | `/System/Volumes/Data` | `df -h "$HOME"` |
| 操作系统 | macOS 27.0.1（Build 26A434） | `sw_vers` |
| GPU | Apple M2 集成显卡，8 核，硬件支持 Metal 4 | `system_profiler SPDisplaysDataType` |

内存与负载的即时快照（勘察当刻，本地时间 0:34，开机 1 天 8 小时 45 分）：

1. `memory_pressure` 报 `System-wide memory free percentage: 54%`。
2. `vm_stat`：free 7642 页、inactive 119433 页、active 121332 页、speculative 851 页（页大小 16384 字节）。即当刻完全空闲约 125 MB，空闲加可回收约 2.1 GB。
3. `uptime` 报负载 `6.41 5.85 4.90`（8 核）。这一负载包含了本次攻坚工作流自身在跑的进程，不代表日常基线。

关于磁盘口径的说明：`df` 的 `32Gi` 与 `df -k` 的 31886352 KB 单位口径不同，两者不宜直接换算比较；后续给数据集与结果预留空间时，按「可用约 30 GB」这个量级规划更稳妥。

GPU 的可用性实测（不是硬件问题，是工具链问题）：

1. `xcrun --find metal` 报 `unable to find utility "metal"`，即 Metal 编译器不可用（完整 Xcode 未装）。
2. `nvcc`、`rocminfo` 都不存在（苹果芯片上本就不可能装 CUDA，实测确认无）。
3. MLX（苹果的数组计算框架）在 venv 与安纳康达 Python 里都未安装（两次 `import mlx` 均报 ModuleNotFoundError）。

结论：GPU 加速目前不可用，且要走通它需要额外安装工具链；本项目也没有需要 GPU 的环节。

---

## 五、形式化工具链现状：全无（实测确认）

### 5.1 命令查找（用 `command -v`，逐个）

```
lean: NOT FOUND
lake: NOT FOUND
coq: NOT FOUND
coqc: NOT FOUND
coqtop: NOT FOUND
isabelle: NOT FOUND
gp: NOT FOUND
sage: NOT FOUND
magma: NOT FOUND
```

### 5.2 目录级排查

1. `~/.elan`（Lean 官方版本管理器）：不存在。
2. `~/.local/share/lean`：不存在。
3. `~/.opam`（OCaml 与 Coq 的常见安装位置）：不存在。
4. `/Applications/Isabelle2024.app`、`/Applications/Isabelle2025.app`：不存在。
5. `/Applications/SageMath`、`/usr/local/bin/sage`：不存在。
6. MacPorts 的 `/opt/local`：不存在（`ls` 报 `No such file or directory`）。
7. Homebrew 的 `/opt/homebrew/Cellar` 里与数学相关的包，只匹配到 `gmp` 一个；没有任何 Lean、Coq、Isabelle、Sage、PARI、flint 的 Homebrew 包。
8. `opam --version` 与 `elan --version`：两者均报 `command not found`。
9. `/usr/local/bin`、`/opt/homebrew/bin`、`/opt/anaconda3/bin`、`~/.local/bin` 五个目录里逐个查找上述九个二进制的名称，全部无命中。

（说明：我第一轮用 zsh 的 `which` 做过一次同类排查，zsh 会把「未找到」当字符串输出到标准输出，导致那一轮输出形如「lean: FOUND at lean not found」的假阳性。上面这一节是改用 `command -v` 复测后的结果，以本节为准。）

### 5.3 因此产生的项目方针（记录任务给定的事实）

按本次任务的要求记录：本机没有 Lean、Coq、Isabelle、PARI、Sage，因此本工作不会安装全局形式化工具链，只会产出 Lean 源码与安装脚本。也就是说，任何「形式化验证通过」的结论在本机都无法当场复核，只能以「源码加安装脚本、待有环境者复现」的形式交付。这一方针来自任务要求，我照此记录，不是我实测得出的偏好。

需要注意的边界（推断）：venv 里的 z3 是 SMT 求解器，不是证明助手。它能对有界、固定位宽、固定步数的命题给出 sat 或 unsat，以及给出反例模型；但它给出的 unsat 不能自动升级为一条可独立复核的数学证明，除非另配证明检查器，而本机没有任何证明检查器。所以在实验里使用 z3 时，措辞应当是「在给定编码与界内未找到反例」，而不是「已证明」。

---

## 六、这台机器能做什么、不能做什么

### 6.1 能做的（均有实测支撑）

1. 大整数数论主循环。gmpy2 2.3.2 与 python-flint 0.9.0 都是 arm64 原生扩展，底层是 GMP 与 FLINT 级实现，适合科拉茨轨道枚举、位操作、模运算这类逐整数推进的计算。实测两者都能完成真实计算（梅森素数判定、`fmpz(2)^64`）。
2. 符号推演与小规模精确计算。sympy 1.14.0 可用，适合做公式推导、恒等式抽查、小规模精确枚举的交叉验证。注意 sympy 是慢的（推断：纯 Python 实现），不要拿它跑大规模搜索。
3. 有界核查与反例搜索。z3 5.3.1 可用，能对固定步数与固定位宽的科拉茨片段问题求 sat 或 unsat。8 核 8 GiB 能支撑中小规模实例。
4. 写 C 加速件并跑多线程。clang 21 原生 arm64，`__int128` 可用，OpenMP 经 Homebrew libomp 实测可开 8 线程。最热的整数内循环可以下沉到 C。
5. 向量化批处理与统计。numpy 2.5.4 走 Apple Accelerate 的 BLAS 与 LAPACK。
6. 联网装包。实测 `curl` 到 `pypi.org` 返回 HTTP 200（5 秒超时内收到约 42 MB，超时截断了剩余部分；完整索引页本身很大，属预期现象），到 `github.com` 返回 HTTP 200 且仅 0.74 秒；venv 里 `pip index versions gmpy2` 正常返回可用版本列表，说明 pip 能访问索引。
7. 磁盘落盘。可用约 30 GB 量级，放搜索结果、日志与证明草稿绰绰有余。

### 6.2 不能做的

1. 不能在本机做形式化验证。没有 Lean 与 lake、没有 Coq 与 coqc、没有 Isabelle、没有 PARI（gp）、没有 Sage，也没有 opam、elan、MacPorts、完整 Xcode。任何形式化结论都无法在本机复核。按项目方针，不安装全局形式化工具链，只产出 Lean 源码与安装脚本。
2. 不能依赖系统 Python 跑实验。三个系统解释器没有一个同时具备五个数学库；裸 `python3` 会静默落到缺库的安纳康达基环境，脚本在 import 阶段才炸。
3. 不能做重内存作业。只有 8 GiB 内存，勘察当刻空闲加可回收仅约 2.1 GB。大 SAT 或 SMT 实例、超大位宽符号化、多进程并行都会撞内存墙；z3 的位向量实例尤其吃内存（推断：我未实测其内存上限，也未做压测）。并行度也不宜按 8 拉满，因为 8 核里有 4 个是能效核。
4. 不能靠 GPU 加速。硬件有 Metal 4 支持，但 Metal 编译器不可用（无完整 Xcode），也没有 CUDA（苹果芯片实测无 `nvcc`），MLX 未安装。
5. 不能做服务器级长跑。这是一台笔记本，8 核 8 GiB，连续数小时的穷举可行，但要按「消费级散热与供电」的预期设定规模（推断）。
6. 不能把 venv 当成与安纳康达无关的独立环境。它的解释器本体链接在 `/opt/anaconda3/bin/python3.12` 上；动了安纳康达，venv 就坏（推断，未做破坏性测试）。

---

## 七、解释器建议（后续实验统一用哪个）

推荐所有实验（脚本、一次性验证、结果复现命令）统一使用下面这个全路径解释器：

```
/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
```

理由：它是本机唯一同时具备 numpy、sympy、z3、gmpy2、python-flint 的解释器，且实测五个库功能正常、从任意工作目录调用都可用。

使用约定（建议直接写进脚本与文档）：

1. 命令里一律写全路径，或者用 shell 变量承接，例如：

```
PY='/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python'
"$PY" scripts/xxx.py
```

2. 脚本首行若要写 shebang，用 `#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python`，但注意该路径含空格，shell 调度时要加引号。
3. 绝对不要用裸 `python3` 或 `python`：实测它们解析到 `/opt/anaconda3/bin/`，缺 z3、gmpy2、flint。
4. 需要 z3 命令行时用 `/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/z3`，不要指望 PATH 里有 z3。
5. C 加速件用 `cc`（苹果 clang 21）编译；需要 OpenMP 时用第三节给出的 libomp 完整命令行。
6. 不要升级该 venv 里的 z3-solver，除非确有需要并先解决第一节 1.7 记录的平台标签问题。

---

## 八、未核实事项清单（诚实边界）

以下是我没有做、因此不能背书的事情：

1. 未做任何性能基准测试。没有测 GMP 或 FLINT 的吞吐、没有测 z3 的求解时间上限、没有测并行加速比。本文件中所有涉及「快、慢、够用」的判断均为推断。
2. 未做内存压测。8 GiB 能撑多大实例，没有测过。
3. 未安装、未删除、未修改任何软件或系统配置。仅动过 `/tmp` 下的两个测试源码与两个可执行文件（`_envtest.c`、`_omptest.c` 及产物）。
4. 未验证网络带宽与稳定性，只验证了 PyPI 与 GitHub 可达（各一次 HTTP 200）。
5. 未核实 `Mac14,2` 对应的市场型号名称，只记录了 `sysctl` 给出的标识与 Apple M2 芯片。
6. `conda env list` 未跑通（报 `__conda_exe:2: permission denied`），因此不能断言安纳康达下是否还有其他环境、其中是否装了更多库。我用逐个解释器实测的方式绕过了这个问题（第二节结论不依赖 `conda env list`）。
7. 未检查 `pip check` 之外的其他依赖一致性问题；未审计 venv 内包的来源与完整性（如哈希校验）。
8. 未测试长时间连续运行的稳定性和散热表现。
