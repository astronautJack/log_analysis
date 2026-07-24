#!/usr/bin/env bash
# LogScope 依赖一键装（Linux/macOS bash）。Windows 用 setup.ps1。
# 三个依赖：CRG（Python/uv）、DCP（JS/npm）、logscope-triage（Python/uv，本仓自产）。
set -e
cd "$(dirname "$0")/.."   # 回到仓根（pyproject.toml 所在）

echo "[1/3] CRG (Python/uv)..."
uv tool install code-review-graph

echo "[2/3] DCP (npm)..."
npm install -g @tarquinen/opencode-dcp@latest

echo "[3/3] logscope-triage (Python/uv, from pyproject)..."
uv tool install --force .

echo
echo "done。"
echo "  CRG            -> ~/.local/bin/code-review-graph"
echo "  DCP            -> npm 全局 + 项目 opencode.json 的 plugin 引用"
echo "  logscope-triage -> ~/.local/bin/logscope-triage"
echo "  模板库         -> ~/.logscope/templates/（自动跨 run 累积）"
echo
echo "确保 ~/.local/bin 在 PATH，然后跑： opencode   （在本仓目录）"
echo "之后 /diag <日志> --repo <代码仓>"
