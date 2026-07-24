# LogScope 依赖一键装（Windows PowerShell）。Linux/macOS 用 setup.sh。
# 三个依赖：CRG（Python/uv）、DCP（JS/npm）、logscope-triage（Python/uv，本仓自产）。
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."   # 回到仓根（pyproject.toml 所在）

Write-Host "[1/3] CRG (Python/uv)..."
uv tool install code-review-graph

Write-Host "[2/3] DCP (npm)..."
npm install -g "@tarquinen/opencode-dcp@latest"

Write-Host "[3/3] logscope-triage (Python/uv, from pyproject)..."
uv tool install --force .

Write-Host ""
Write-Host "done。"
Write-Host "  CRG             -> ~/.local/bin/code-review-graph"
Write-Host "  DCP             -> npm 全局 + 项目 opencode.json 的 plugin 引用"
Write-Host "  logscope-triage  -> ~/.local/bin/logscope-triage"
Write-Host "  模板库          -> ~/.logscope/templates/（自动跨 run 累积）"
Write-Host ""
Write-Host "确保 ~/.local/bin 在 PATH（$env:Path += `";$HOME\.local\\bin`"），然后跑： opencode"
Write-Host "之后 /diag <日志> --repo <代码仓>"
