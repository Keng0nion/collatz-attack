/-
================================================================================
CollatzBasic.lean —— 科拉茨（3x+1）初等引理的 Lean 4 形式化
================================================================================

## 零、未编译声明（必读）

本文件是在一台**没有 Lean 工具链的机器**上写成的：写就时 `which lean`、`which lake`、
`which elan` 均无输出，`~/.elan` 与 `~/.lake` 均不存在。因此：

1. **本文件从未经过 Lean 编译器检验。** 下文注释里凡出现「证明已写」字样，都只表示
   「作者认为该证明在语法与策略层面应当成立」，**不等于编译通过**。
2. 写就前实际做过的替代检查（逐条列出，均**不等于**编译）：
   一、用 Python 对每条 theorem 的**数学陈述**做有限范围逐点枚举复核，脚本中的定义与
       本文件的定义、递归方向逐字对齐（脚本与运行结果见 `../README.md` 第四节，可直接重跑）；
   二、复核过程中**证伪了一条原本打算写的强陈述**，已删除并把反例记在本文件第八节；
   三、所用到的核心引理名，逐一到 leanprover/lean4 master 的 `Init/Data/Nat/Basic.lean`、
       `Init/Data/Nat/Lemmas.lean` 中核对过（清单见 `../README.md` 第三节）；
       未能核对到名字的引理一律不用，改为用已核对过的名字重写；
   四、做了一次结构与括号自查（`namespace` 与 `end` 配对、括号配平、`sorry` 计数）。
3. 因此，接手者请先执行 `../README.md` 第二节的编译命令，再按其中的「首次编译请注意」
   逐项处理可能出现的报错。本文件的目标是**编译一次即可通过**，而不是「已经通过」。

## 一、如何编译

最短路径（详细安装步骤见 `../README.md` 第一、二节，或直接运行 `../setup-lean.sh`）：

    cd <一个已经 `require mathlib` 且拉过 `lake exe cache get` 的工程目录>
    lake env lean /绝对路径/collatz-attack/40-formal/lean/CollatzBasic.lean

## 二、记号

    加速映射（本文件全篇使用它，不是标准的 3x+1 映射）
        T(n) = n / 2          若 n 为偶
        T(n) = (3n + 1) / 2   若 n 为奇
    iterT k n   = T 的 k 次迭代，iterT 0 n = n，iterT (k+1) n = T (iterT k n)
    M k n       = 前 k 步（第 0 步至第「`k` 减 1」步）中的奇数步个数
    C k n       = 递推推出的常数 c：第 i 位为奇数步时 c ← 3c + 2^i，从 c = 0 起
    SameBits k n m = n 与 m 前 k 步的奇偶向量逐位相同
    Keeps k n   = 对一切 1 ≤ j ≤ k 都有 n ≤ T^j(n)（即前 k 步都不跌破起点）
    NeverDescends n = 对一切 j ≥ 1 都有 n ≤ T^j(n)（χ(n) = ∞ 的初等形式，χ 为停时）

    约定：C、M 的递归都是**从外向内剥**（Horner 形式），即
        C (k+1) n = 3 * C k n + 2^k   （当 iterT k n 为奇数时）
    这对应来源材料里的递推「`c ← 3c + 2^(j 减 1)`」，其中的 j 是从 1 数起的步号。

## 三、与来源材料的对应

    affine_formula              来源 (1) 式：T^j(n) = (3^{S_j(n)} n + c_j(n)) / 2^j
                                本文件把它写成整数的整除形式（更强，同时给出整除性）
    阈值判据 threshold_criterion 来源命题 2.1（`30-proof-attempts/minimal-counterexample/attempt.md`）
    余量传递                    来源命题 2.2
    cycle_equation              来源「环方程」：`T^k(x) = x` ⟹ `x · (2^k 减 3^m) = c` 且 `3^m < 2^k`
    sameBits_of_mod_eq          来源 `verify_lemmas.py` 的 C2 段（奇偶向量只依赖 mod 2^k）
    本节其余条目                   来源 `verify_lemmas.py` 的 C1 段（阈值等价）

## 四、状态说明

本文件**不证明科拉茨猜想**，也不声称任何新结果。它只把「奇偶向量决定仿射公式」
「阈值判据」「环方程」「奇偶向量的模常值性」「余量传递」这五组初等事实写成可机检的形式。
未做的部分（含原因）见 `../README.md` 第五、六节。
-/

import Mathlib

namespace CollatzBasic

/-! # 一、加速映射 T 与它的迭代 -/

/-- 加速科拉茨映射：奇数走一步 `(3n+1)/2`，偶数走一步 `n/2`。

注意 `T 0 = 0`（0 是偶数的分支）。 -/
def T (n : ℕ) : ℕ := if n % 2 = 1 then (3 * n + 1) / 2 else n / 2

/-- `T` 的 `k` 次迭代。递归从外向内剥：`iterT (k+1) n = T (iterT k n)`。 -/
def iterT : ℕ → ℕ → ℕ
  | 0, n => n
  | k + 1, n => T (iterT k n)

@[simp] theorem iterT_zero (n : ℕ) : iterT 0 n = n := rfl

@[simp] theorem iterT_succ (k n : ℕ) : iterT (k + 1) n = T (iterT k n) := rfl

/-- 奇数分支的展开。 -/
theorem T_of_odd {n : ℕ} (h : n % 2 = 1) : T n = (3 * n + 1) / 2 := by
  simp only [T]
  rw [if_pos h]

/-- 偶数分支的展开。 -/
theorem T_of_even {n : ℕ} (h : n % 2 = 0) : T n = n / 2 := by
  simp only [T]
  rw [if_neg (Nat.mod_two_ne_one.mpr h)]

/-- 迭代的加法分解：`T^(j+k) = T^j ∘ T^k`。 -/
theorem iterT_add (j k n : ℕ) : iterT (j + k) n = iterT j (iterT k n) := by
  induction j with
  | zero => rfl
  | succ j ih =>
    simp only [Nat.succ_add, iterT_succ]
    rw [ih]

/-- 上面一条的特例：先走一步、再迭代 `i` 次，与迭代 `i+1` 次一致。 -/
theorem iterT_succ_eq (i n : ℕ) : iterT (i + 1) n = iterT i (T n) := by
  rw [iterT_add i 1 n]
  rfl

/-! # 二、算术辅助引理（只用核心库中已核对过的名字） -/

/-- `2 * (n / 2) = n`，当 `n` 为偶数。 -/
theorem two_mul_div_two_of_even {n : ℕ} (h : n % 2 = 0) : 2 * (n / 2) = n := by
  have hn : n / 2 * 2 + n % 2 = n := Nat.div_add_mod' n 2
  rw [Nat.mul_comm] at hn
  rw [h] at hn
  simpa using hn

/-- `3n + 1` 在 `n` 为奇数时为偶数。 -/
theorem three_mul_add_one_mod_two (n : ℕ) (h : n % 2 = 1) : (3 * n + 1) % 2 = 0 := by
  rw [Nat.add_mod, Nat.mul_mod, h]
  norm_num

/-- 同余与奇偶：`a * 2^(k+1) + r` 与 `r` 同奇偶。 -/
theorem mod_two_of_mul_add (k a r : ℕ) : (a * 2 ^ (k + 1) + r) % 2 = r % 2 := by
  have h : a * 2 ^ (k + 1) = 2 * (a * 2 ^ k) := by
    rw [pow_succ]
    ring
  rw [h, Nat.mul_add_mod]

/-- 同上的除法版：`a * 2^(k+1) + r` 除以 2。 -/
theorem div_two_of_mul_add (k a r : ℕ) : (a * 2 ^ (k + 1) + r) / 2 = a * 2 ^ k + r / 2 := by
  have h : a * 2 ^ (k + 1) = 2 * (a * 2 ^ k) := by
    rw [pow_succ]
    ring
  have h2 : (2 * (a * 2 ^ k) + r) / 2 = a * 2 ^ k + r / 2 :=
    Nat.mul_add_div (m := 2) (by norm_num) (a * 2 ^ k) r
  rw [h, h2]

/-- 奇数步的除法版：`(3 * (a * 2^(k+1) + r) + 1) / 2`。 -/
theorem div_two_of_three_mul_add (k a r : ℕ) :
    (3 * (a * 2 ^ (k + 1) + r) + 1) / 2 = 3 * a * 2 ^ k + (3 * r + 1) / 2 := by
  have h : 3 * (a * 2 ^ (k + 1) + r) + 1 = 2 * (3 * a * 2 ^ k) + (3 * r + 1) := by
    rw [pow_succ]
    ring
  have h2 : (2 * (3 * a * 2 ^ k) + (3 * r + 1)) / 2 = 3 * a * 2 ^ k + (3 * r + 1) / 2 :=
    Nat.mul_add_div (m := 2) (by norm_num) (3 * a * 2 ^ k) (3 * r + 1)
  rw [h, h2]

/-- 加法不改变模 `2^k` 的余数。 -/
theorem mod_two_pow_of_mul_add (k a s : ℕ) : (a * 2 ^ k + s) % 2 ^ k = s % 2 ^ k := by
  have h : a * 2 ^ k = 2 ^ k * a := Nat.mul_comm a (2 ^ k)
  rw [h, Nat.mul_add_mod]

/-- 同上，系数带 3 的形式（奇数步的写法）。 -/
theorem mod_two_pow_of_three_mul_add (k a s : ℕ) : (3 * a * 2 ^ k + s) % 2 ^ k = s % 2 ^ k := by
  have h : 3 * a * 2 ^ k = 2 ^ k * (3 * a) := Nat.mul_comm (3 * a) (2 ^ k)
  rw [h, Nat.mul_add_mod]

/-- 余数不超过被除数：`x % 2^k ≤ x`。 -/
theorem mod_two_pow_le (k x : ℕ) : x % 2 ^ k ≤ x := by
  have h : x / 2 ^ k * 2 ^ k + x % 2 ^ k = x := Nat.div_add_mod' x (2 ^ k)
  calc x % 2 ^ k ≤ x / 2 ^ k * 2 ^ k + x % 2 ^ k :=
        Nat.le_add_left (x % 2 ^ k) (x / 2 ^ k * 2 ^ k)
    _ = x := h

/-- `(d * y) / d = y`，当 `d > 0`。 -/
theorem mul_div_self (d y : ℕ) (hd : 0 < d) : d * y / d = y := by
  refine Nat.mul_left_cancel hd ?_
  exact Nat.mul_div_cancel_left' (a := d) (b := d * y) ⟨y, rfl⟩

/-- 冒烟用：`T (2k) = k`。 -/
theorem T_two_mul (k : ℕ) : T (2 * k) = k := by
  have h : (2 * k) % 2 = 0 := by
    rw [Nat.mul_mod]
    norm_num
  rw [T_of_even h, mul_div_self 2 k (by norm_num)]

/-- 冒烟用：`T (2k+1) = 3k+2`。 -/
theorem T_two_mul_add_one (k : ℕ) : T (2 * k + 1) = 3 * k + 2 := by
  have h : (2 * k + 1) % 2 = 1 := by
    rw [Nat.add_mod, Nat.mul_mod]
    norm_num
  have h2 : 3 * (2 * k + 1) + 1 = 2 * (3 * k + 2) := by ring
  rw [T_of_odd h, h2, mul_div_self 2 (3 * k + 2) (by norm_num)]

/-- `3` 的幂恒为奇数。 -/
theorem three_pow_mod_two (m : ℕ) : 3 ^ m % 2 = 1 := by
  induction m with
  | zero => norm_num
  | succ m ih =>
    rw [pow_succ, Nat.mul_mod, ih]
    norm_num

/-- `2^k` 在 `k ≥ 1` 时为偶数。 -/
theorem two_pow_mod_two (k : ℕ) (hk : 1 ≤ k) : 2 ^ k % 2 = 0 := by
  obtain ⟨j, rfl⟩ : ∃ j, k = j + 1 := ⟨k - 1, by omega⟩
  rw [pow_succ, Nat.mul_mod]
  norm_num

/-- `3^m ≠ 2^k`（当 `k ≥ 1`）。这是阈值判据里三分的排中项被排除的依据。 -/
theorem pow_three_ne_pow_two (k m : ℕ) (hk : 1 ≤ k) : 3 ^ m ≠ 2 ^ k := by
  intro heq
  have h1 : 3 ^ m % 2 = 1 := three_pow_mod_two m
  have h2 : 2 ^ k % 2 = 0 := two_pow_mod_two k hk
  rw [heq] at h1
  omega

/-! # 三、奇偶向量决定的 m 与 c -/

/-- `M k n`：前 `k` 步中奇数步的个数（即来源材料的 `S_k(n)`）。 -/
def M : ℕ → ℕ → ℕ
  | 0, _ => 0
  | k + 1, n => M k n + (if iterT k n % 2 = 1 then 1 else 0)

/-- `C k n`：来源材料的 `c_k(n)`，按「第 `i` 位为奇数步则 `c ← 3c + 2^i`」递推。 -/
def C : ℕ → ℕ → ℕ
  | 0, _ => 0
  | k + 1, n => if iterT k n % 2 = 1 then 3 * C k n + 2 ^ k else C k n

@[simp] theorem M_zero (n : ℕ) : M 0 n = 0 := rfl

@[simp] theorem M_succ (k n : ℕ) :
    M (k + 1) n = M k n + (if iterT k n % 2 = 1 then 1 else 0) := rfl

@[simp] theorem C_zero (n : ℕ) : C 0 n = 0 := rfl

@[simp] theorem C_succ (k n : ℕ) :
    C (k + 1) n = if iterT k n % 2 = 1 then 3 * C k n + 2 ^ k else C k n := rfl

/-- 逐位递推（奇数位）：`c ← 3c + 2^k`。 -/
theorem C_succ_of_odd (k n : ℕ) (h : iterT k n % 2 = 1) : C (k + 1) n = 3 * C k n + 2 ^ k := by
  rw [C_succ, if_pos h]

/-- 逐位递推（偶数位）：`c` 不变。 -/
theorem C_succ_of_even (k n : ℕ) (h : iterT k n % 2 = 0) : C (k + 1) n = C k n := by
  rw [C_succ, if_neg (Nat.mod_two_ne_one.mpr h)]

/-- 逐位递推（奇数位）：`m` 加一。 -/
theorem M_succ_of_odd (k n : ℕ) (h : iterT k n % 2 = 1) : M (k + 1) n = M k n + 1 := by
  rw [M_succ, if_pos h]

/-- 逐位递推（偶数位）：`m` 不变。 -/
theorem M_succ_of_even (k n : ℕ) (h : iterT k n % 2 = 0) : M (k + 1) n = M k n := by
  rw [M_succ, if_neg (Nat.mod_two_ne_one.mpr h)]

/-- 两个数在前 `k` 步的奇偶向量逐位相同。 -/
def SameBits (k n m : ℕ) : Prop := ∀ i, i < k → iterT i n % 2 = iterT i m % 2

/-- 奇偶向量决定 `(m, c)`：这是「向量决定仿射公式」的结构部分。 -/
theorem M_C_eq_of_sameBits (k n m : ℕ) (h : SameBits k n m) :
    M k n = M k m ∧ C k n = C k m := by
  revert n m
  induction k with
  | zero => intro n m _; exact ⟨rfl, rfl⟩
  | succ k ih =>
    intro n m h
    have hk : SameBits k n m := fun i hi => h i (by omega)
    have hbit : iterT k n % 2 = iterT k m % 2 := h k (by omega)
    obtain ⟨hM, hC⟩ := ih n m hk
    exact ⟨by rw [M_succ, M_succ, hM, hbit], by rw [C_succ, C_succ, hC, hbit]⟩

/-! # 四、仿射公式 -/

/-- **仿射公式（整除形式）**：`3^m · n + c = 2^k · T^k(n)`。

这条比「除以 2^k」的形式更强：它同时给出了分子被 `2^k` 整除。证明用对 `k` 的归纳，
归纳步按 `iterT k n` 的奇偶分两种情形，奇数情形用 `3^(m+1) = 3 · 3^m` 把 Horner 递推
的 `3c + 2^k` 还原成 `3 · (3^m n + c) + 2^k`。 -/
theorem affine_formula (k n : ℕ) : 3 ^ M k n * n + C k n = 2 ^ k * iterT k n := by
  revert n
  induction k with
  | zero => intro n; simp
  | succ k ih =>
    intro n
    rcases Nat.mod_two_eq_zero_or_one (iterT k n) with hy0 | hy1
    · -- `iterT k n` 为偶
      have hM : M (k + 1) n = M k n := by rw [M_succ, if_neg (Nat.mod_two_ne_one.mpr hy0)]
      have hC : C (k + 1) n = C k n := by rw [C_succ, if_neg (Nat.mod_two_ne_one.mpr hy0)]
      have hT : iterT (k + 1) n = iterT k n / 2 := by rw [iterT_succ, T_of_even hy0]
      have hR : 2 ^ (k + 1) * (iterT k n / 2) = 2 ^ k * iterT k n := by
        rw [pow_succ, Nat.mul_assoc, two_mul_div_two_of_even hy0]
      rw [hM, hC, hT, ih n, hR]
    · -- `iterT k n` 为奇
      have hM : M (k + 1) n = M k n + 1 := by rw [M_succ, if_pos hy1]
      have hC : C (k + 1) n = 3 * C k n + 2 ^ k := by rw [C_succ, if_pos hy1]
      have hT : iterT (k + 1) n = (3 * iterT k n + 1) / 2 := by rw [iterT_succ, T_of_odd hy1]
      have hkey : 3 ^ (M k n + 1) * n + (3 * C k n + 2 ^ k)
          = 3 * (3 ^ M k n * n + C k n) + 2 ^ k := by
        rw [pow_succ]
        ring
      have hL : 3 * (2 ^ k * iterT k n) + 2 ^ k = 2 ^ k * (3 * iterT k n + 1) := by ring
      have hR : 2 ^ (k + 1) * ((3 * iterT k n + 1) / 2) = 2 ^ k * (3 * iterT k n + 1) := by
        rw [pow_succ, Nat.mul_assoc,
          two_mul_div_two_of_even (three_mul_add_one_mod_two (iterT k n) hy1)]
      rw [hM, hC, hT, hkey, ih n, hL, hR]

/-- **仿射公式（商形式）**：`T^k(n) = (3^m n + c) / 2^k`，与来源材料的 (1) 式逐字对应。 -/
theorem affine_formula_div (k n : ℕ) : iterT k n = (3 ^ M k n * n + C k n) / 2 ^ k := by
  rw [affine_formula]
  exact (mul_div_self (2 ^ k) (iterT k n) (by positivity)).symm

/-! # 五、阈值判据与环方程 -/

/-- 辅助：正整数因子可从不等号两边消去。 -/
theorem mul_le_mul_left_iff {a b c : ℕ} (hc : 0 < c) : c * a ≤ c * b ↔ a ≤ b := by
  refine ⟨fun h => ?_, fun h => Nat.mul_le_mul_left c h⟩
  by_contra hba
  have h' : b < a := Nat.not_le.mp hba
  have hlt : c * b < c * a := Nat.mul_lt_mul_of_lt_of_le h' le_rfl hc
  omega

/-- **阈值判据**（来源命题 2.1 的整数形式）。

`T^k(x) ≥ x` 当且仅当：系数条件已经「过头」（`2^k < 3^m`），或者系数条件成立
（`3^m < 2^k`）而 `x` 不超过阈值 `θ = c / (2^k - 3^m)`——后者写成整数形式即
`(2^k - 3^m) · x ≤ c`。

三分中的 `3^m = 2^k` 支被 `pow_three_ne_pow_two` 排除。 -/
theorem threshold_criterion (k x : ℕ) (hk : 1 ≤ k) (hx : 1 ≤ x) :
    x ≤ iterT k x ↔
      (2 ^ k < 3 ^ M k x ∨
        (3 ^ M k x < 2 ^ k ∧ (2 ^ k - 3 ^ M k x) * x ≤ C k x)) := by
  have hA : 0 < 2 ^ k := by positivity
  have hx0 : 0 < x := hx
  have haff : 2 ^ k * iterT k x = 3 ^ M k x * x + C k x := (affine_formula k x).symm
  have hne : 3 ^ M k x ≠ 2 ^ k := pow_three_ne_pow_two k (M k x) hk
  -- 第一步：把 `x ≤ T^k x` 换成不含 `T` 的整数不等式。
  -- 这里刻意不用 `rw` 改写整个目标：那会同时命中右端的分支条件，
  -- 改成显式的 `Iff` 组合，无论 `rw` 的匹配语义是「首个」还是「全部」都安全。
  have hmul : x ≤ iterT k x ↔ 2 ^ k * x ≤ 3 ^ M k x * x + C k x := by
    constructor
    · intro h
      have h1 : 2 ^ k * x ≤ 2 ^ k * iterT k x := Nat.mul_le_mul_left (2 ^ k) h
      rwa [haff] at h1
    · intro h
      have h1 : 2 ^ k * x ≤ 2 ^ k * iterT k x := by rwa [← haff] at h
      exact (mul_le_mul_left_iff hA).mp h1
  -- 第二步：三分
  have hmain : (2 ^ k * x ≤ 3 ^ M k x * x + C k x) ↔
      (2 ^ k < 3 ^ M k x ∨
        (3 ^ M k x < 2 ^ k ∧ (2 ^ k - 3 ^ M k x) * x ≤ C k x)) := by
    rcases lt_trichotomy (2 ^ k) (3 ^ M k x) with hlt | heq | hgt
    · -- 情形一：`2^k < 3^m`，两边都真
      refine ⟨fun _ => Or.inl hlt, fun _ => ?_⟩
      have h1 : 2 ^ k * x < 3 ^ M k x * x := Nat.mul_lt_mul_of_lt_of_le hlt le_rfl hx0
      exact Nat.le_of_lt (Nat.lt_of_lt_of_le h1 (Nat.le_add_right _ _))
    · -- 情形二：排中项，矛盾
      exact absurd heq.symm hne
    · -- 情形三：`3^m < 2^k`，把 `2^k · x` 拆开再消去 `3^m · x`
      have hle : 3 ^ M k x ≤ 2 ^ k := Nat.le_of_lt hgt
      have hsplit : 2 ^ k * x = (2 ^ k - 3 ^ M k x) * x + 3 ^ M k x * x := by
        rw [← Nat.add_mul, Nat.sub_add_cancel hle]
      refine ⟨fun h => Or.inr ⟨hgt, ?_⟩, fun h => ?_⟩
      · -- 正向：`2^k · x ≤ 3^m · x + c` ⟹ `(2^k - 3^m) · x ≤ c`
        have h' : (2 ^ k - 3 ^ M k x) * x + 3 ^ M k x * x ≤ 3 ^ M k x * x + C k x := by
          rw [← hsplit]
          exact h
        have h'' : (2 ^ k - 3 ^ M k x) * x + 3 ^ M k x * x ≤ C k x + 3 ^ M k x * x := by
          rw [Nat.add_comm (C k x) (3 ^ M k x * x)]
          exact h'
        exact (Nat.add_le_add_iff_right).mp h''
      · -- 反向：由 `(2^k - 3^m) · x ≤ c` 恢复 `2^k · x ≤ 3^m · x + c`
        rcases h with hbad | ⟨_, hD⟩
        · exact absurd hbad (Nat.not_lt.mpr hle)
        · rw [hsplit, Nat.add_comm (3 ^ M k x * x) (C k x)]
          exact Nat.add_le_add_right hD _
  exact hmul.trans hmain

/-- **环方程**：若 `T^k(x) = x` 且 `x ≥ 1`、`k ≥ 1`，则必有 `3^m < 2^k`，且
`x · (2^k - 3^m) = c`。这排除了「系数条件过头」的环，并把环上的点钉在
`x = c / (2^k - 3^m)` 上。 -/
theorem cycle_equation (k x : ℕ) (hk : 1 ≤ k) (hx : 1 ≤ x) (hcyc : iterT k x = x) :
    3 ^ M k x < 2 ^ k ∧ x * (2 ^ k - 3 ^ M k x) = C k x := by
  have hx0 : 0 < x := hx
  -- 只在假设内部把 `iterT k x` 替换成 `x`（模式是复合项 `iterT k x`，不涉及裸变量，
  -- 因此与 `rw` 的匹配语义无关）
  have haff : 3 ^ M k x * x + C k x = 2 ^ k * x := by
    have h := affine_formula k x
    rw [hcyc] at h
    exact h
  -- 第一步：系数条件不能过头
  have hle : 3 ^ M k x ≤ 2 ^ k := by
    by_contra hcon
    have hlt : 2 ^ k < 3 ^ M k x := Nat.not_le.mp hcon
    have h1 : 2 ^ k * x < 3 ^ M k x * x := Nat.mul_lt_mul_of_lt_of_le hlt le_rfl hx0
    have h2 : 2 ^ k * x < 3 ^ M k x * x + C k x :=
      Nat.lt_of_lt_of_le h1 (Nat.le_add_right _ _)
    rw [haff] at h2
    exact absurd h2 (lt_irrefl (2 ^ k * x))
  -- 第二步：严格小于（等号被奇偶性排除）
  have hlt : 3 ^ M k x < 2 ^ k := by
    rcases Nat.lt_or_eq_of_le hle with h | h
    · exact h
    · exact absurd h (pow_three_ne_pow_two k (M k x) hk)
  refine ⟨hlt, ?_⟩
  -- 第三步：把 `2^k · x` 拆开，消去两边的 `3^m · x`
  have hsplit : 2 ^ k * x = (2 ^ k - 3 ^ M k x) * x + 3 ^ M k x * x := by
    rw [← Nat.add_mul, Nat.sub_add_cancel hle]
  have hcancel : (2 ^ k - 3 ^ M k x) * x + 3 ^ M k x * x = 3 ^ M k x * x + C k x :=
    calc (2 ^ k - 3 ^ M k x) * x + 3 ^ M k x * x = 2 ^ k * x := hsplit.symm
      _ = 3 ^ M k x * x + C k x := haff.symm
  have hgoal : (2 ^ k - 3 ^ M k x) * x = C k x := by
    have h1 : (2 ^ k - 3 ^ M k x) * x + 3 ^ M k x * x = C k x + 3 ^ M k x * x := by
      rw [Nat.add_comm (C k x) (3 ^ M k x * x)]
      exact hcancel
    exact (Nat.add_right_cancel_iff).mp h1
  calc x * (2 ^ k - 3 ^ M k x) = (2 ^ k - 3 ^ M k x) * x :=
        Nat.mul_comm x (2 ^ k - 3 ^ M k x)
    _ = C k x := hgoal

/-- 环方程的商形式：`x = c / (2^k - 3^m)`。 -/
theorem cycle_quotient (k x : ℕ) (hk : 1 ≤ k) (hx : 1 ≤ x) (hcyc : iterT k x = x) :
    x = C k x / (2 ^ k - 3 ^ M k x) := by
  obtain ⟨hlt, heq⟩ := cycle_equation k x hk hx hcyc
  have hd : 0 < 2 ^ k - 3 ^ M k x := Nat.sub_pos_of_lt hlt
  rw [← heq, Nat.mul_comm x (2 ^ k - 3 ^ M k x), mul_div_self _ _ hd]

/-! # 六、奇偶向量的模常值性与余量传递（Terras 型初等部分） -/

/-- 偶分支的余数计算：`(a * 2^(k+1) + r) / 2` 的模 `2^k` 余数只依赖 `r`。 -/
theorem div_two_mod_two_pow (k a r : ℕ) :
    (a * 2 ^ (k + 1) + r) / 2 % 2 ^ k = r / 2 % 2 ^ k := by
  rw [div_two_of_mul_add k a r, mod_two_pow_of_mul_add k a (r / 2)]

/-- 奇分支的余数计算：`(3 * (a * 2^(k+1) + r) + 1) / 2` 的模 `2^k` 余数只依赖 `r`。 -/
theorem div_two_three_mul_add_mod_two_pow (k a r : ℕ) :
    (3 * (a * 2 ^ (k + 1) + r) + 1) / 2 % 2 ^ k = (3 * r + 1) / 2 % 2 ^ k := by
  rw [div_two_of_three_mul_add k a r, mod_two_pow_of_three_mul_add k a ((3 * r + 1) / 2)]

/-- 若 `n` 与 `m` 模 `2^k` 同余（`k ≥ 1`），则二者同奇偶。 -/
theorem mod_two_eq_of_mod_two_pow (k n m : ℕ) (h : n % 2 ^ (k + 1) = m % 2 ^ (k + 1)) :
    n % 2 = m % 2 := by
  have hn : n = n / 2 ^ (k + 1) * 2 ^ (k + 1) + n % 2 ^ (k + 1) :=
    (Nat.div_add_mod' n (2 ^ (k + 1))).symm
  have hm : m = m / 2 ^ (k + 1) * 2 ^ (k + 1) + m % 2 ^ (k + 1) :=
    (Nat.div_add_mod' m (2 ^ (k + 1))).symm
  -- 用 `congrArg` 只替换被指定的那一个出现位置，避免依赖 `rw` 的匹配语义
  calc n % 2 = (n / 2 ^ (k + 1) * 2 ^ (k + 1) + n % 2 ^ (k + 1)) % 2 :=
        congrArg (fun t => t % 2) hn
    _ = (n % 2 ^ (k + 1)) % 2 := mod_two_of_mul_add k (n / 2 ^ (k + 1)) (n % 2 ^ (k + 1))
    _ = (m % 2 ^ (k + 1)) % 2 := by rw [h]
    _ = (m / 2 ^ (k + 1) * 2 ^ (k + 1) + m % 2 ^ (k + 1)) % 2 :=
        (mod_two_of_mul_add k (m / 2 ^ (k + 1)) (m % 2 ^ (k + 1))).symm
    _ = m % 2 := (congrArg (fun t => t % 2) hm).symm

/-- **转移引理**：模 `2^(k+1)` 同余 ⟹ 走一步之后模 `2^k` 同余。

证明把 `n`、`m` 都写成「商乘模加余数」，两边的余数相同；再按余数的奇偶分两种情形，
各用一条除法引理把 `T` 作用后的同余关系算出来。这条引理是「奇偶向量只依赖 `n mod 2^k`」
的归纳步。 -/
theorem T_mod_eq_of_mod_eq (k n m : ℕ) (h : n % 2 ^ (k + 1) = m % 2 ^ (k + 1)) :
    T n % 2 ^ k = T m % 2 ^ k := by
  have hn : n = n / 2 ^ (k + 1) * 2 ^ (k + 1) + n % 2 ^ (k + 1) :=
    (Nat.div_add_mod' n (2 ^ (k + 1))).symm
  have hm : m = m / 2 ^ (k + 1) * 2 ^ (k + 1) + m % 2 ^ (k + 1) :=
    (Nat.div_add_mod' m (2 ^ (k + 1))).symm
  -- 下面所有替换都用 `congrArg`（只替换指定的一处），或把引理直接作用在具体项上。
  -- 这样就不依赖 `rw` 到底重写「首个匹配」还是「全部匹配」。
  rcases Nat.mod_two_eq_zero_or_one (n % 2 ^ (k + 1)) with hr | hr
  · -- 余数为偶：`T` 走的是除以 2 的分支
    have hn2 : n % 2 = 0 := by
      calc n % 2 = (n / 2 ^ (k + 1) * 2 ^ (k + 1) + n % 2 ^ (k + 1)) % 2 :=
            congrArg (fun t => t % 2) hn
        _ = (n % 2 ^ (k + 1)) % 2 := mod_two_of_mul_add k (n / 2 ^ (k + 1)) (n % 2 ^ (k + 1))
        _ = 0 := hr
    have hm2 : m % 2 = 0 := by
      calc m % 2 = (m / 2 ^ (k + 1) * 2 ^ (k + 1) + m % 2 ^ (k + 1)) % 2 :=
            congrArg (fun t => t % 2) hm
        _ = (m % 2 ^ (k + 1)) % 2 := mod_two_of_mul_add k (m / 2 ^ (k + 1)) (m % 2 ^ (k + 1))
        _ = (n % 2 ^ (k + 1)) % 2 := by rw [h.symm]
        _ = 0 := hr
    calc T n % 2 ^ k = (n / 2) % 2 ^ k := by rw [T_of_even hn2]
      _ = ((n / 2 ^ (k + 1) * 2 ^ (k + 1) + n % 2 ^ (k + 1)) / 2) % 2 ^ k :=
            congrArg (fun t => (t / 2) % 2 ^ k) hn
      _ = (n % 2 ^ (k + 1) / 2) % 2 ^ k :=
            div_two_mod_two_pow k (n / 2 ^ (k + 1)) (n % 2 ^ (k + 1))
      _ = (m % 2 ^ (k + 1) / 2) % 2 ^ k := by rw [h]
      _ = ((m / 2 ^ (k + 1) * 2 ^ (k + 1) + m % 2 ^ (k + 1)) / 2) % 2 ^ k :=
            (div_two_mod_two_pow k (m / 2 ^ (k + 1)) (m % 2 ^ (k + 1))).symm
      _ = (m / 2) % 2 ^ k := (congrArg (fun t => (t / 2) % 2 ^ k) hm).symm
      _ = T m % 2 ^ k := by rw [T_of_even hm2]
  · -- 余数为奇：`T` 走的是 `(3n+1)/2` 的分支
    have hn2 : n % 2 = 1 := by
      calc n % 2 = (n / 2 ^ (k + 1) * 2 ^ (k + 1) + n % 2 ^ (k + 1)) % 2 :=
            congrArg (fun t => t % 2) hn
        _ = (n % 2 ^ (k + 1)) % 2 := mod_two_of_mul_add k (n / 2 ^ (k + 1)) (n % 2 ^ (k + 1))
        _ = 1 := hr
    have hm2 : m % 2 = 1 := by
      calc m % 2 = (m / 2 ^ (k + 1) * 2 ^ (k + 1) + m % 2 ^ (k + 1)) % 2 :=
            congrArg (fun t => t % 2) hm
        _ = (m % 2 ^ (k + 1)) % 2 := mod_two_of_mul_add k (m / 2 ^ (k + 1)) (m % 2 ^ (k + 1))
        _ = (n % 2 ^ (k + 1)) % 2 := by rw [h.symm]
        _ = 1 := hr
    calc T n % 2 ^ k = ((3 * n + 1) / 2) % 2 ^ k := by rw [T_of_odd hn2]
      _ = ((3 * (n / 2 ^ (k + 1) * 2 ^ (k + 1) + n % 2 ^ (k + 1)) + 1) / 2) % 2 ^ k :=
            congrArg (fun t => ((3 * t + 1) / 2) % 2 ^ k) hn
      _ = ((3 * (n % 2 ^ (k + 1)) + 1) / 2) % 2 ^ k :=
            div_two_three_mul_add_mod_two_pow k (n / 2 ^ (k + 1)) (n % 2 ^ (k + 1))
      _ = ((3 * (m % 2 ^ (k + 1)) + 1) / 2) % 2 ^ k := by rw [h]
      _ = ((3 * (m / 2 ^ (k + 1) * 2 ^ (k + 1) + m % 2 ^ (k + 1)) + 1) / 2) % 2 ^ k :=
            (div_two_three_mul_add_mod_two_pow k (m / 2 ^ (k + 1)) (m % 2 ^ (k + 1))).symm
      _ = ((3 * m + 1) / 2) % 2 ^ k := (congrArg (fun t => ((3 * t + 1) / 2) % 2 ^ k) hm).symm
      _ = T m % 2 ^ k := by rw [T_of_odd hm2]

/-- **奇偶向量只依赖 `n mod 2^k`**（来源 `verify_lemmas.py` 的 C2 段）。 -/
theorem sameBits_of_mod_eq (k n m : ℕ) (h : n % 2 ^ k = m % 2 ^ k) : SameBits k n m := by
  revert n m
  induction k with
  | zero => intro n m _ i hi; omega
  | succ k ih =>
    intro n m h i hi
    rcases Nat.eq_zero_or_pos i with rfl | hipos
    · simp only [iterT_zero]
      exact mod_two_eq_of_mod_two_pow k n m h
    · obtain ⟨j, rfl⟩ : ∃ j, i = j + 1 := ⟨i - 1, by omega⟩
      rw [iterT_succ_eq j n, iterT_succ_eq j m]
      exact ih (T n) (T m) (T_mod_eq_of_mod_eq k n m h) j (by omega)

/-- 前 `k` 步都不跌破起点（即停时 `χ(n) ≥ k+1` 的初等形式）。 -/
def Keeps (k n : ℕ) : Prop := ∀ j, 1 ≤ j → j ≤ k → n ≤ iterT j n

/-- `χ(n) = ∞` 的初等形式：从第 1 步起轨道从不跌破 `n`。 -/
def NeverDescends (n : ℕ) : Prop := ∀ j, 1 ≤ j → n ≤ iterT j n

/-- **余量传递（单步形式）**：若 `n` 不跌破、`m ≤ n`，且两者前 `k` 步奇偶向量相同，
则 `m` 也不跌破。

注意这里 `m ≤ n` 这个大小条件是必需的：阈值判据的第二支含 `m` 自身的大小
（`(2^k - 3^m) · m ≤ c`），所以「不跌破」**不是**奇偶向量的函数（反例见本文件末尾）。
传递的正确方向是「大的不跌破 ⟹ 小的（同类）不跌破」。 -/
theorem le_iterT_of_sameBits_of_le (k n m : ℕ) (hk : 1 ≤ k) (hm : 1 ≤ m) (hmn : m ≤ n)
    (hbits : SameBits k n m) (h : n ≤ iterT k n) : m ≤ iterT k m := by
  obtain ⟨hM, hC⟩ := M_C_eq_of_sameBits k n m hbits
  have hn : 1 ≤ n := Nat.le_trans hm hmn
  rcases lt_trichotomy (2 ^ k) (3 ^ M k n) with hlt | heq | hgt
  · -- 系数条件已过头：阈值判据第一支对 `m` 直接成立
    exact (threshold_criterion k m hk hm).mpr (Or.inl (by rw [← hM]; exact hlt))
  · exact absurd heq.symm (pow_three_ne_pow_two k (M k n) hk)
  · -- 系数条件成立：把 `n` 的阈值不等式按 `m ≤ n` 缩小
    have hle : 3 ^ M k n ≤ 2 ^ k := Nat.le_of_lt hgt
    have hsub : (2 ^ k - 3 ^ M k m) = (2 ^ k - 3 ^ M k n) := by rw [hM]
    rcases (threshold_criterion k n hk hn).mp h with hbad | ⟨_, hD⟩
    · exact absurd hbad (Nat.not_lt.mpr hle)
    · have h1 : (2 ^ k - 3 ^ M k m) * m ≤ (2 ^ k - 3 ^ M k n) * n := by
        rw [hsub]
        exact Nat.mul_le_mul_left _ hmn
      have h4 : (2 ^ k - 3 ^ M k m) * m ≤ C k m := by
        rw [hC.symm]
        exact Nat.le_trans h1 hD
      exact (threshold_criterion k m hk hm).mpr (Or.inr ⟨by rw [← hM]; exact hgt, h4⟩)

/-- **余量传递（全步形式）**：若 `n` 前 `k` 步都不跌破、`m ≤ n`，且两者前 `k` 步奇偶
向量相同，则 `m` 前 `k` 步也都不跌破。等价地说，`E_k` 在每个奇偶向量类里是「向上闭」的。 -/
theorem keeps_of_sameBits_of_le (k n m : ℕ) (hk : 1 ≤ k) (hm : 1 ≤ m) (hmn : m ≤ n)
    (hbits : SameBits k n m) (h : Keeps k n) : Keeps k m := by
  intro j hj1 hjk
  exact le_iterT_of_sameBits_of_le j n m hj1 hm hmn
    (fun i hi => hbits i (Nat.lt_of_lt_of_le hi hjk))
    (h j hj1 hjk)

/-- **入口定理（来源命题 2.2 与其推论）**：若 `n` 的轨道从不跌破 `n`（`χ(n) = ∞`），
则对每个 `k ≥ 1`，`n mod 2^k` 的前 `k` 步都不跌破它自己，即该剩余类落在 `E_k` 里。

这是「靠有限层模约束打不到矛盾」这一否证型结论的初等基础：所有模约束都是
`χ(n) = ∞` 的推论，而不是能与它冲突的东西。 -/
theorem neverDescends_keeps_mod (k x : ℕ) (hk : 1 ≤ k) (h : NeverDescends x) :
    Keeps k (x % 2 ^ k) := by
  rcases Nat.eq_zero_or_pos (x % 2 ^ k) with h0 | hrpos
  · -- 剩余类为 0：平凡（0 是 `T` 的不动点）
    intro j hj1 hjk
    rw [h0]
    exact Nat.zero_le _
  · have hrx : x % 2 ^ k ≤ x := mod_two_pow_le k x
    have hbits : SameBits k x (x % 2 ^ k) :=
      sameBits_of_mod_eq k x (x % 2 ^ k) (Nat.mod_mod x (2 ^ k)).symm
    intro j hj1 hjk
    exact le_iterT_of_sameBits_of_le j x (x % 2 ^ k) hj1 hrpos hrx
      (fun i hi => hbits i (Nat.lt_of_lt_of_le hi hjk))
      (h j hj1)

/-! # 七、冒烟测试（接手者请先确认这几条能过） -/

example : T 1 = 2 := by norm_num [T]

example : T 2 = 1 := by norm_num [T]

example : iterT 3 3 = 4 := by norm_num [iterT, T]

example : M 3 3 = 2 := by norm_num [M, iterT, T]

example : C 3 3 = 5 := by norm_num [C, iterT, T]

/-- 仿射公式在 `(k, n) = (3, 3)` 上的实例：`3^2 · 3 + 5 = 2^3 · 4`。 -/
example : 3 ^ M 3 3 * 3 + C 3 3 = 2 ^ 3 * iterT 3 3 := by norm_num [M, C, iterT, T]

/-- 环方程在唯一已知环上的实例：`1 → 2 → 1`，`k = 2`、`x = 1`、`m = 1`、`c = 1`，
`1 · (2^2 - 3^1) = 1`。 -/
example : 3 ^ M 2 1 < 2 ^ 2 ∧ 1 * (2 ^ 2 - 3 ^ M 2 1) = C 2 1 := cycle_equation 2 1
  (by norm_num) (by norm_num) (by norm_num [iterT, T])

/-!
================================================================================
八、如实记录的边界与反例
================================================================================

## 8.1 被证伪的强陈述（已从本文件删除）

原本打算写的一条「对称」引理是：

    （假）SameBits k n m → (n ≤ iterT k n ↔ m ≤ iterT k m)

**它在有限复核中被证伪**：取 `k = 2`、`n = 1`、`m = 5`。此时
`bits(2,1) = (1,0) = bits(2,5)`（`1 → 2 → 1`，`5 → 8 → 4`），但
`1 ≤ T^2(1) = 1` 成立，而 `5 ≤ T^2(5) = 4` 不成立。`k = 2, n = 1, m = 9` 同样反例。
（复核脚本用同一定义逐点枚举，输出见 `../README.md` 第四节。）

原因是阈值判据的第二支 `(2^k - 3^m) · x ≤ C` 含 `x` **自身的大小**，所以「前 k 步不跌破」
不是奇偶向量的函数，只是「阈值约束下」的函数。本文件因此只写正确方向的传递命题
（`le_iterT_of_sameBits_of_le` 及其推论）。

## 8.2 本文件没有做的事

1. 没有定义 `χ`（停时）与 `τ`（系数停时）的 `Nat.find` 型函数，只用了与它们等价的
   谓词 `Keeps`、`NeverDescends`。理由：部分函数在 Lean 里要额外的 `Nat.find` 与
   存在性引理，收益小于风险。
2. 没有写 `E_k = α_k ∪ {1}` 这一结构命题（来源 `verify_lemmas.py` 的 C4 段）。
   它需要把 `Keeps` 与「系数条件」两套定义都整理成集合形式，工作量明显更大。
3. 没有写 Terras 系数停时猜想（`χ = τ`）的陈述：它是**未解决猜想**，不是初等引理，
   写进来只会造成误读。
4. 没有对「不存在非平凡环」或科拉茨猜想本身做任何形式化。
-/

end CollatzBasic
