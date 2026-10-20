#!/usr/bin/env bash
#
# setup-lean.sh —— 安装 Lean 工具链、建一个依赖 Mathlib 的工程、编译 CollatzBasic.lean
#
# 用法：
#   bash setup-lean.sh                 # 默认工程目录 $HOME/lean-collatz-formal
#   COLLATZ_LEAN_PROJ=/path/to/proj bash setup-lean.sh
#
# 诚实说明（作者写此脚本时本机没有 Lean 工具链）：
#   1. 本脚本**未端到端跑过**，只做过 bash 语法检查与逐条命令的来源核对；
#   2. elan 安装脚本采用「先下载到临时文件、打印 SHA-256、由使用者确认后再执行」的方式，
#      不使用把远程脚本直接管道进 shell 的写法；
#   3. 命令来源：elan 官方脚本 https://elan.lean-lang.org/elan-init.sh ；
#      `lake +v4.24.0 new <名字> math` 与 `lake update` 来自 leanprover 社区安装页；
#      `lake exe cache get` 来自 mathlib4 仓库 README。
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LEAN_FILE="$SCRIPT_DIR/lean/CollatzBasic.lean"

PROJ_DIR="${COLLATZ_LEAN_PROJ:-$HOME/lean-collatz-formal}"
PROJ_NAME="$(basename "$PROJ_DIR")"
PROJ_PARENT="$(dirname "$PROJ_DIR")"
# 这个版本号只决定用哪个 lake 来创建工程，不决定工程最终使用的 Lean 版本
LAKE_BOOTSTRAP_VERSION="${LAKE_BOOTSTRAP_VERSION:-v4.24.0}"

say() { printf '\n===== %s =====\n' "$*"; }

if [ ! -f "$LEAN_FILE" ]; then
  echo "找不到待编译的文件：$LEAN_FILE" >&2
  exit 1
fi

say "第 1 步 / 共 5 步：检查 elan 与 lake"
if command -v elan >/dev/null 2>&1; then
  echo "已发现 elan：$(command -v elan)"
else
  echo "未发现 elan。将按官方做法下载安装脚本，但不会自动执行："
  echo "  下载源：https://elan.lean-lang.org/elan-init.sh"
  ELAN_INIT="$(mktemp "${TMPDIR:-/tmp}/elan-init.XXXXXXXX")"
  curl -sSfL -o "$ELAN_INIT" https://elan.lean-lang.org/elan-init.sh
  echo "  已保存到：$ELAN_INIT"
  if command -v shasum >/dev/null 2>&1; then
    echo -n "  SHA-256："
    shasum -a 256 "$ELAN_INIT"
  fi
  echo "  建议先自行查看该脚本内容（例如：less \"$ELAN_INIT\"）。"
  printf '  是否现在执行它来安装 elan？输入 y 继续，其它输入退出：[y/N] '
  read -r answer
  case "$answer" in
    y|Y)
      sh "$ELAN_INIT" -y
      export PATH="$HOME/.elan/bin:$PATH"
      echo "  提示：这个终端之外请先执行 source ~/.profile（或 ~/.bash_profile）再用 elan"
      ;;
    *)
      echo "已跳过安装。请先按 README.md 第一节手动装好 elan，然后重跑本脚本。" >&2
      exit 1
      ;;
  esac
fi
elan --version || echo "（elan --version 未成功，请检查 PATH）"
lake --version || echo "（lake --version 未成功，请检查 PATH）"

say "第 2 步 / 共 5 步：准备工程目录 $PROJ_DIR"
if [ -f "$PROJ_DIR/lakefile.toml" ] || [ -f "$PROJ_DIR/lakefile.lean" ]; then
  echo "工程已存在，跳过创建"
else
  mkdir -p "$PROJ_PARENT"
  ( cd "$PROJ_PARENT" && lake "+$LAKE_BOOTSTRAP_VERSION" new "$PROJ_NAME" math )
fi

say "第 3 步 / 共 5 步：lake update（解析并固定 Mathlib 版本，网络密集型）"
( cd "$PROJ_DIR" && lake update )

say "第 4 步 / 共 5 步：lake exe cache get（拉 Mathlib 预编译缓存，数 GB 级）"
if ! ( cd "$PROJ_DIR" && lake exe cache get ); then
  echo "缓存下载失败。按 mathlib4 README 的建议，可依次尝试：" >&2
  echo "  cd \"$PROJ_DIR\" && lake clean && lake exe cache get" >&2
  echo "  cd \"$PROJ_DIR\" && rm -rf .lake && lake exe cache get" >&2
  echo "  必要时重下：lake exe cache get!" >&2
  exit 1
fi

say "第 5 步 / 共 5 步：编译 $LEAN_FILE"
( cd "$PROJ_DIR" && lake env lean "$LEAN_FILE" )

say "结束"
echo "若第 5 步没有任何输出且退出码为 0，说明该文件通过了类型检查。"
echo "任何报错都请贴回；README.md 第二节列了最可能需要微调的几处。"
