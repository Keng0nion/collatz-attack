# 40-formal：科拉茨初等引理的 Lean 4 形式化

## 这份目录里有什么

1. `lean/CollatzBasic.lean`：本次工作的形式化产物。50 条声明（含 7 条冒烟测试），
   0 个 `sorry`、0 个 `admit`。**未经 Lean 编译器检验**（原因见下一节）。
2. `setup-lean.sh`：一键安装工具链并编译该文件的脚本。
3. `README.md`：本文件，写清安装、编译、核对方式、工作量与风险。
4. `independent-checks/`：前次工作留下的独立验算记录（q_23 门槛、Eliahou 常数、
   判据复核），与本次形式化无依赖关系，但属同一目录下的复核材料。

## 关于「未编译」的如实声明（先读这段）

`lean/CollatzBasic.lean` 是在**没有 Lean 工具链的机器**上写成的：写就时 `which lean`、
`which lake`、`which elan` 均无输出，`~/.elan` 与 `~/.lake` 均不存在。写就前实际做过的
替代检查只有下面四类，**没有一项等于编译**：

1. 用 Python 对每条 theorem 的**数学陈述**做有限范围逐点枚举复核（定义与递归方向与
   Lean 文件逐字对齐），脚本与运行结果见第四节，可直接重跑；
2. 复核过程中**证伪了一条原本打算写的强陈述**，已删除并把反例写进 Lean 文件第八节；
3. 所用到的核心引理名，逐一到 `leanprover/lean4` master 的 `Init/Data/Nat/Basic.lean`、
   `Init/Data/Nat/Lemmas.lean` 里核对过（清单见第三节）。未核对到的名字一律不用；
4. 结构与括号自查（`namespace` 与 `end` 配对、括号配平、`sorry` 与 `admit` 计数、
   中文注释里的半角连字符检查）。

因此：**「证明已写」只表示作者认为它在语法与策略层面应当成立。** 接手者请按第二节
编译，并按「首次编译请注意」逐项处理报错。

## 一、工具链安装

三样东西：`elan`（Lean 版本管理器，顺带装上 `lake`）、`lake`（构建工具，建工程用）、
Mathlib 的预编译缓存（不拉缓存的话，第一次构建会非常慢）。

### 1.1 安装 elan

官方脚本（来源：`leanprover/elan` 仓库 README，见第四节末的来源清单）：

```bash
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh
```

脚本会交互确认；非交互安装加 `-y`：

```bash
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh -s -- -y
```

注意：`setup-lean.sh` **没有**采用「把远程脚本直接管道进 shell」的写法，而是先下载到临时
文件、打印 SHA-256、由使用者确认后再执行（原因见脚本头部注释）。上面两行只是官方文档
的原样记录，供手动安装时使用。

安装后若 `elan` 不在 `PATH`，先执行 `source ~/.profile`（或 `~/.bash_profile`，
视系统而定），并确保 `~/.elan/bin` 在 `PATH` 里。

### 1.2 建一个依赖 Mathlib 的工程

官方安装页给出的写法（来源：leanprover 社区安装页 `install/project.html`）：

```bash
cd <你想放工程的父目录>
lake +v4.24.0 new my_project math     # 末尾的 math 表示把 mathlib4 加进依赖
cd my_project
lake update                            # 解析并固定 Mathlib 的版本
```

说明两点：`+v4.24.0` 里的版本号只决定用哪个 `lake` 来建工程，**与工程最终使用的 Lean
版本无关**（官方页原话如此）；`lake update` 会去拉 Mathlib 源码，这一步是网络密集型。

若不建新工程，也可以把这三行加到任意已有 Mathlib 工程里（本文件只要 `import Mathlib`）。

### 1.3 拉 Mathlib 预编译缓存

```bash
lake exe cache get
```

来源：`mathlib4` 仓库 README（原话：「To obtain precompiled `olean` files, run
`lake exe cache get`. (Skipping this step means the next step will be very slow.)」）。
出问题时官方 README 建议依次尝试 `lake clean`、`rm -rf .lake`、`lake exe cache get!`。
这一步会占用可观的磁盘空间（Mathlib 源码加 olean 缓存属数 GB 级别），耗时主要取决于网络。

### 1.4 或者：直接跑 `setup-lean.sh`

```bash
bash "40-formal/setup-lean.sh"
```

脚本做五件事：检查或安装 elan、在 `$HOME/lean-collatz-formal`（可用环境变量
`COLLATZ_LEAN_PROJ` 覆盖）建工程、`lake update`、`lake exe cache get`、
最后用 `lake env lean` 编译 `lean/CollatzBasic.lean`。脚本可重复运行（工程已存在时跳过创建）。

## 二、编译命令

在工程目录里执行（路径按实际改）：

```bash
cd "$HOME/lean-collatz-formal"
lake env lean "/Users/luna/Documents/math IA/collatz-attack/40-formal/lean/CollatzBasic.lean"
```

也可以把文件复制进工程，再 `lake env lean CollatzBasic.lean`。

**首次编译请注意**（这些是检查清单，不是预期会发生的报错）：

1. `import Mathlib` 需要工程确实依赖 Mathlib。只想更快的话，可把首行换成
   `import Mathlib.Tactic`（本文件只用到 `omega`、`ring`、`norm_num`、`positivity`、
   `simp` 与核心库的 `Nat.*` 引理，理论上不需要整个 `Mathlib`；**未验证**）。
2. 文件里没有 `sorry`，所以若某处策略失败，会是硬报错。风险最高的几处（按作者判断
   从高到低）：
   一、`T_mod_eq_of_mod_eq`（转移引理）里的 `calc` 链与 `rw` 的匹配方向；
   二、`affine_formula` 里 `rw [Nat.mul_assoc, …]` 的位置与 `ring` 在 ℕ 上的使用；
   三、`two_mul_div_two_of_even` 用 `rw [Nat.mul_comm] at hn` 调整加数顺序；
   四、`obtain ⟨j, rfl⟩ : ∃ j, k = j + 1 := ⟨k - 1, by omega⟩` 这类「去掉正性假设」
      的模式（`two_pow_mod_two`、`sameBits_of_mod_eq` 各一处）；
   五、冒烟测试里的 `norm_num [iterT, T]` 是否真能把 `iterT` 展开到数值。
3. 若某个核心引理名在工程固定的 Lean 版本里改了名（见第三节末尾的风险说明），
   报错是「unknown identifier」，逐处替换即可，不涉及证明结构。

编译成功时按 `lean` 命令行的一般行为**不输出任何内容并返回 0**——这一条是期待，
作者未在本机验证（本机没有 Lean）。

## 三、核对过的引理名清单

下列名字全部在 `leanprover/lean4` master 的 `src/Init/Data/Nat/Basic.lean`、
`src/Init/Data/Nat/Lemmas.lean` 里逐条查到过（括号内是该名字第一次出现的行号）：

| 名字 | 用途 |
|---|---|
| `Nat.div_add_mod'`（Lemmas 1530） | 商乘模加余数 `a / b * b + a % b = a` |
| `Nat.mul_add_div`（Lemmas 1590） | `(m * x + y) / m = x + y / m`（需 `m > 0`） |
| `Nat.mul_add_mod`（Lemmas 1597） | `(m * x + y) % m = y % m` |
| `Nat.mul_mod`（Lemmas 837） | `a * b % n = (a % n) * (b % n) % n` |
| `Nat.add_mod`（Lemmas 857） | `(a + b) % n = ((a % n) + (b % n)) % n` |
| `Nat.mod_mod`（Lemmas 834） | `(a % n) % n = a % n` |
| `Nat.mod_two_eq_zero_or_one`（Lemmas 807） | `n % 2 = 0 ∨ n % 2 = 1` |
| `Nat.mod_two_ne_one`（Lemmas 1457） | `n % 2 ≠ 1 ↔ n % 2 = 0` |
| `Nat.mul_div_cancel_left'`（Lemmas 925） | `a * (b / a) = b`（需 `a ∣ b`） |
| `Nat.mul_left_cancel`（Lemmas 582） | 在 ℕ 上消去正因子 |
| `Nat.mul_lt_mul_of_lt_of_le`（Lemmas 611） | `a < c → b ≤ d → 0 < d → a * b < c * d` |
| `Nat.mul_le_mul_left`（Basic 747） | `n ≤ m → k * n ≤ k * m` |
| `Nat.add_le_add_iff_right`（Basic 527） | 在 ℕ 上消去右侧加数（不等式） |
| `Nat.add_le_add_right`（Basic 487） | 不等式两边同加 |
| `Nat.add_right_cancel_iff`（Lemmas 211） | 在 ℕ 上消去右侧加数（等式） |
| `Nat.le_add_left`（Basic 374） | `n ≤ m + n` |
| `Nat.le_of_lt`（Basic 315） | `n < m → n ≤ m` |
| `Nat.not_le`（Basic 440） | `¬ a ≤ b ↔ b < a` |
| `Nat.not_lt`（Basic 442） | `¬ a < b ↔ b ≤ a` |
| `Nat.lt_or_eq_of_le`（Basic 571） | `n ≤ m → n < m ∨ n = m` |
| `Nat.eq_zero_or_pos`（Basic 324） | `n = 0 ∨ 0 < n` |
| `Nat.sub_add_cancel`（Basic 987） | `m ≤ n → n - m + m = n` |
| `Nat.sub_pos_of_lt`（Basic 1111） | `m < n → 0 < n - m` |
| `Nat.add_mul`（Basic 236）、`Nat.mul_comm`（Basic 211）、`Nat.mul_assoc`（Basic 239） | 环恒等式的整理 |
| `Nat.pow_succ`（Basic 789） | `n ^ (m+1) = n ^ m * n` |
| `Nat.lt_trichotomy`（Basic 448） | 三分的来源 |
| `Nat.le_trans`（Lemmas 606 处使用）、`Nat.lt_of_lt_of_le`／`Nat.lt_of_le_of_lt`（Lemmas 613 处使用） | 传递性 |
| `Nat.lt_succ_self`（Lemmas 1526 处使用） | `n < n + 1` |

另外用到的都是策略（tactic）或证明命令，而不是外部引理名：`omega`（线性整数算术）、
`ring`（ℕ 上的多项式恒等式）、`norm_num`（数值与取模）、`positivity`、`simp`、`rw`、
`calc`、`induction`、`rcases`、`obtain`、`refine`、`exact`、`absurd`。`linarith` 与
`nlinarith` 未使用；所有需要「非线性项参与线性推理」的地方都改成了显式引理
（这也降低了 `omega` 是否把乘积当原子的依赖）。

**风险说明**：以上核对针对的是 `leanprover/lean4` 的 master 分支，而工程实际固定的是
Mathlib 的 `lean-toolchain`（本文件写就时 `mathlib4` master 上是
`leanprover/lean4:v4.36.0-rc1`）。若这些 `Nat.*` 引理在固定版本里被移进 `Std` 或改名，
报错形如 `unknown identifier 'Nat.mul_add_mod'`，逐处替换即可。

**关于 Mathlib 自身的 Collatz 发展**：作者尝试核对 `Mathlib/Dynamics/Collatz`，但
文档站 `.../mathlib4_docs/Mathlib/Dynamics/Collatz.html` 返回 404（同一时刻
`Mathlib/Dynamics/FixedPoints/Basic.html` 返回 200），因此**未能确认**它现在是否存在、
放在哪里。本文件因此**不依赖它**，并把所有内容放在命名空间 `CollatzBasic` 里以避免
命名冲突。接手者若要复用 Mathlib 自带的科拉茨材料，可先自查：

```bash
grep -ril collatz .lake/packages/mathlib/Mathlib | head
```

## 四、写就前的替代检查（可重跑）

### 4.1 陈述复核脚本（第二轮，通过的版本）

把下面这段存成 `check_statements.py` 后 `python3 check_statements.py`。它用的 `T`、
`iterT`、`M`、`C` 与 Lean 文件逐字对齐（同样的递归方向），只做有限枚举，不构成证明。

```python
from collections import Counter

def T(n): return (3*n+1)//2 if n % 2 == 1 else n//2
def iterT(k, n):
    while k > 0:
        n = T(n); k -= 1
    return n
def M(k, n): return sum(1 for i in range(k) if iterT(i, n) % 2 == 1)
def C(k, n):
    c = 0
    for i in range(k):
        if iterT(i, n) % 2 == 1: c = 3*c + 2**i
    return c
def bits(k, n): return tuple(iterT(i, n) % 2 for i in range(k))
def Keeps(k, n): return all(n <= iterT(j, n) for j in range(1, k+1))
def NeverDescends(n): return all(n <= iterT(j, n) for j in range(1, 60))

fails = Counter(); first = {}
def chk(name, cond, detail=""):
    if not cond:
        fails[name] += 1; first.setdefault(name, detail)

# 转移引理用到的两条中间引理（分解后取余）
for k in range(0, 9):
    for a in range(0, 40):
        for s in range(0, 300):
            chk("div_two_mod_two_pow", (a*2**(k+1)+s)//2 % 2**k == s//2 % 2**k, f"k={k} a={a} s={s}")
            chk("div_two_three_mul_add_mod_two_pow",
                (3*(a*2**(k+1)+s)+1)//2 % 2**k == (3*s+1)//2 % 2**k, f"k={k} a={a} s={s}")
# 仿射公式（整除形式与商形式）
for k in range(0, 13):
    for n in range(0, 2049):
        chk("affine_formula", 3**M(k, n)*n + C(k, n) == 2**k*iterT(k, n), f"k={k} n={n}")
        if k >= 1:
            chk("affine_formula_div", iterT(k, n) == (3**M(k, n)*n + C(k, n))//2**k, f"k={k} n={n}")
# 奇偶向量只依赖 n mod 2^k
for k in range(0, 11):
    for n in range(1, 1025):
        chk("sameBits_of_mod_eq", bits(k, n) == bits(k, n + 2**k), f"k={k} n={n}")
# 转移引理与同奇偶引理
for k in range(0, 9):
    for n in range(0, 1025):
        for m in range(0, 1025):
            if n % 2**(k+1) == m % 2**(k+1):
                chk("T_mod_eq_of_mod_eq", T(n) % 2**k == T(m) % 2**k, f"k={k} n={n} m={m}")
                chk("mod_two_eq_of_mod_two_pow", n % 2 == m % 2, f"k={k} n={n} m={m}")
# 阈值判据
for k in range(1, 11):
    for x in range(1, 1025):
        lhs = (x <= iterT(k, x))
        rhs = (2**k < 3**M(k, x)) or (3**M(k, x) < 2**k and (2**k - 3**M(k, x))*x <= C(k, x))
        chk("threshold_criterion", lhs == rhs, f"k={k} x={x}")
# 环方程
for k in range(1, 15):
    for x in range(0, 8193):
        if iterT(k, x) == x:
            chk("cycle_equation_lt", 3**M(k, x) < 2**k, f"k={k} x={x}")
            chk("cycle_equation", x*(2**k - 3**M(k, x)) == C(k, x), f"k={k} x={x}")
# 余量传递（单步）
for k in range(1, 11):
    for n in range(1, 513):
        for m in range(1, n+1):
            if bits(k, n) == bits(k, m) and n <= iterT(k, n):
                chk("le_iterT_of_sameBits_of_le", m <= iterT(k, m), f"k={k} n={n} m={m}")
# 余量传递（全步）
for k in range(1, 11):
    for n in range(1, 513):
        for m in range(1, n+1):
            if bits(k, n) == bits(k, m) and Keeps(k, n):
                chk("keeps_of_sameBits_of_le", Keeps(k, m), f"k={k} n={n} m={m}")
# 入口定理：χ = ∞ 的数，其每个模 2^k 剩余类都落在 E_k 里
for n in range(1, 2049):
    if NeverDescends(n):
        for k in range(1, 12):
            r = n % 2**k
            chk("neverDescends_keeps_mod",
                all(r <= iterT(j, r) for j in range(1, k+1)), f"n={n} k={k} r={r}")

print("失败汇总：", dict(fails) if fails else "无")
```

本次运行的实测输出（本机 `python3`，耗时约 12 秒）：

```
失败汇总： 无
```

### 4.2 第一轮检查：它证伪了一条陈述

第一轮脚本（`check_statements.py`，临时写在 `/tmp`）除了 4.1 的那些检查，还检查了一条
后来被删掉的「对称」陈述：

    （假）SameBits k n m → (n ≤ T^k n ↔ m ≤ T^k m)

它的实测输出（原样照抄，只截断了中间若干行）：

```
失败条数：494
  失败: keeps_iff_of_sameBits k=2 n=1 m=5
  失败: keeps_iff_of_sameBits k=2 n=1 m=9
  失败: keeps_iff_of_sameBits k=2 n=1 m=13
  ...
```

为了确认「494 条是否全部出自这一条」（而不是夹着别的缺陷），另跑了一次按名字汇总的
版本（`check_v1_breakdown.py`，同为 `/tmp` 临时脚本），实测输出：

```
按名字汇总：
  keeps_iff_of_sameBits（已删除的假陈述）: 494
总计 494 条
```

即：494 条失败**全部**来自这条假陈述，其余检查项（仿射公式、阈值判据、环方程、转移引理、
奇偶向量模常值性、各式算术辅助引理）在各自范围内零失败。

第二轮脚本（`check_statements2.py`，与 4.1 保留的那份相比，只少了后来补上的两条中间引理
检查，并且额外打印反例本身；同为 `/tmp` 临时脚本）：

```
反例确认 k=2 n=1 m=5: 同奇偶向量=True, 阈值判据结论不同=True
反例确认 k=2 n=1 m=9: 同奇偶向量=True, 阈值判据结论不同=True

全部通过（所有被编码的陈述在所述范围内无例外）
```

也就是说 `bits(2,1) = (1,0) = bits(2,5)`，但 `1 ≤ T^2(1) = 1` 成立而 `5 ≤ T^2(5) = 4`
不成立。原因是阈值判据的第二支含 `x` 自身的大小条件，所以「前 k 步不跌破」不是奇偶向量
的函数。Lean 文件里因此只保留正确方向的**余量传递**（大的不跌破、小的同类也不跌破），
并在第八节如实记录了这条反例。**这是本次写作最有价值的一次检查**：若不跑它，
文件里会留下一条假定理。

### 4.3 结构自查

`lean_selfcheck.py` 一类的脚本（本次临时写在 `/tmp`，未随产物保留；逻辑见下）做四件事：
去掉注释后检查括号配平、`namespace` 与 `end` 配对、`sorry`／`admit` 计数、
以及中文注释里的半角连字符。本次结果：块注释嵌套平衡、括号配平通过、
namespace 与 end 配对、`sorry` 0 次、`admit` 0 次。

## 五、工作量与风险评估

**预期工作量**

1. 安装与首建：主要是等待（elan 安装很快；`lake update` 拉 Mathlib 源码、
   `lake exe cache get` 拉缓存是网络密集型，磁盘占用数 GB 级别）。之后本文件是一次
   `lake env lean`，用上缓存后很轻。
2. 修编译错误：按作者判断，需要「几处到十几处」的局部调整（典型是 `rw` 的匹配方向、
   `ring`／`omega` 在某个具体目标上不够用、`norm_num` 展开递归定义不够）。每一处都是
   一两行的事，**不涉及证明结构重写**，因为所有陈述都已经被 Python 逐点复核过。
3. 若要把 Lean 文件第八节列的「没做的事」补上（`E_k` 与 `α_k` 的结构命题、`χ` 与 `τ` 的
   `Nat.find` 型定义、`E_k` 的计数），那是新工作，不是修错。

**风险**

1. **未编译（最高）**：策略层面的小错无法预先排除。已尽量把风险集中到少数几处并用
   已核对过的引理名替代易错写法（例如用 `Nat.mod_two_ne_one.mpr h` 而不是依赖 `omega`
   处理取模），但「写一次就过」只是目标，不是保证。
2. **版本漂移（中）**：引理名核对基于 `leanprover/lean4` master；工程固定的是 Mathlib
   的 `lean-toolchain`（写就时为 `leanprover/lean4:v4.36.0-rc1`）。改名会让报错集中在
   `unknown identifier`，改起来便宜。
3. **Mathlib 自带 Collatz 材料未核实（低）**：见第三节末尾。本文件不依赖它。
4. **覆盖范围（重要，非技术风险）**：本文件**不证明科拉茨猜想**，也不声称新结果。
   它形式化的是五组初等事实：仿射公式、阈值判据、环方程、奇偶向量的模常值性、余量传递。
   任何「已形式化科拉茨」的解读都是误读。Lean 文件第八节末尾逐条列了没做的事与原因。

## 六、没做的事（以及为什么）

1. `χ`（停时）与 `τ`（系数停时）没有定义成 `Nat.find` 型的部分函数，只用了与它们等价的
   谓词 `Keeps`、`NeverDescends`。理由：部分函数要额外的存在性引理，收益小于风险。
2. 没有写来源 `verify_lemmas.py` 的 C4 段结构命题 `E_k = α_k ∪ {1}`：需要把
   `Keeps` 与「系数条件」两套定义都整理成集合形式，工作量明显更大。
3. 没有写 Terras 系数停时猜想（`χ = τ`）的陈述：它是**未解决猜想**，写进来只会造成误读。
4. 没有形式化「不存在非平凡环」或猜想本身。

## 七、与来源材料的对应

| Lean 声明 | 来源 |
|---|---|
| `affine_formula`、`affine_formula_div` | `30-proof-attempts/minimal-counterexample/attempt.md` 的 (1) 式 |
| `threshold_criterion` | 同上，命题 2.1 |
| `le_iterT_of_sameBits_of_le`、`keeps_of_sameBits_of_le`、`neverDescends_keeps_mod` | 同上，命题 2.2 及其推论（并对应 `verify_lemmas.py` 的 C1、C2 段） |
| `cycle_equation`、`cycle_quotient` | 同上，「环方程」一条（D11 段与第 9 步的整数形式） |
| `M`、`C` 的递推与 `M_C_eq_of_sameBits` | 同上，记号约定第 2 条与 `verify_lemmas.py` 的 `bits_c_m` |

来源清单（本次写作时打开或抓取过的）：

1. `leanprover/elan` 仓库 README：`curl https://elan.lean-lang.org/elan-init.sh -sSf | sh`；
   `elan-init.sh` 源码里 `-y` 的说明在第 30 行（「Disable confirmation prompt.」）。
2. leanprover 社区安装页 `https://leanprover-community.github.io/install/project.html`：
   `lake +v4.24.0 new my_project math` 与 `lake update`。
3. `mathlib4` 仓库 README（`raw.githubusercontent.com/leanprover-community/mathlib4/master/README.md`）：
   `lake exe cache get`、`lake clean`、`lake exe cache get!`。
4. `mathlib4` 仓库 `lean-toolchain`：`leanprover/lean4:v4.36.0-rc1`。
5. `leanprover/lean4` 仓库 `src/Init/Data/Nat/Basic.lean`、`src/Init/Data/Nat/Lemmas.lean`：
   第三节清单里所有引理名与签名。
6. 本目录 `../30-proof-attempts/minimal-counterexample/attempt.md`、
   `verify_lemmas.py`、`verify_output_rerun.txt`：命题 2.1、2.2 与 C1 至 C9 的复核口径。
