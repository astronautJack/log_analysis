# LogScope

> 基于 opencode 的**日志问题定位 agent**：长日志 + 相关代码库 → 定位到**哪一行代码**有问题。

## 这是什么

把客户/系统的长日志 + 相关代码仓丢给 LogScope，它：

1. **log-triage**：把长日志（成千上万行）压成有界 digest（错误/栈帧/时间线/符号，~28:1 压缩），原始日志落临时文件、返回预览指针——**绝不灌进上下文**。
2. **wiki-reader**：读目标仓 wiki（若有）+ 源码头注释，取调用链/契约上下文。
3. **code-tracer**：沿 CRG 代码图反向回溯（`search` → `query callers_of` → `impact` → `flow`），定位到 `file:line`。
4. **自校正**：Critic 复核证据链，弱则带反馈重试（≤3 次）。
5. **报告**：哪行代码 + 置信度 + 证据链（log 行号 + file:line + 图边）→ 交人审。

## 前置条件

| 依赖 | 说明 |
|---|---|
| **opencode** ≥ 1.18 | 工具集跑在 opencode 上 |
| **git** | Windows 生产：装 [Git for Windows](https://git-scm.com/download/win)（只需 git，**不依赖 Git Bash**）；agent 只用 git+uv+python+opencode 原生工具 |
| **uv** + **code-review-graph** (CRG) | `uv tool install code-review-graph` → `~/.local/bin/code-review-graph` |
| **opencode-dcp** (DCP) | `npm install -g @tarquinen/opencode-dcp@latest`（需 node/npm；项目 opencode.json 已引用）→ 上下文兜底 |
| **glm-5.2 端点** | 公司内网 LLM 端点（`model`/`small_model` 由全局 opencode 配置提供，本仓不写死） |

## 安装

> Linux/macOS 用 bash；**Windows 生产**用 **PowerShell**（opencode Windows 原生，**不依赖 Git Bash**，只需 git + uv + node/npm）。

```bash
# 1. 拿到本仓
git clone <本仓地址> log_analysis
cd log_analysis

# 2. 装 uv（setup 用它装 CRG + logscope-triage）
#    Linux/macOS:  curl -LsSf https://astral.sh/install.sh | sh
#    Win PS:        irm https://astral.sh/install.ps1 | iex

# 3. 一键装三依赖（CRG/uv + DCP/npm + logscope-triage/uv）
#    Linux/macOS:  bash .opencode/setup.sh
#    Win PS:        .\.opencode\setup.ps1
#    （手动逐条见 .opencode/REQUIREMENTS.md）

# 4. 在本仓启动 opencode（加载 .opencode/ + AGENTS.md + opencode.json）
opencode
```

确保 `~/.local/bin`（CRG/logscope-triage）在 PATH——uv 安装器通常已加；没有则 Win PS `$env:Path += ";$HOME\.local\bin"`。

改完 `.opencode/`/`opencode.json`/`~/.config/opencode/dcp.jsonc` 后**重启 opencode** 才生效。

改完 `.opencode/`、`opencode.json`、或 `~/.config/opencode/dcp.jsonc`（Windows：`C:\Users\<你>\.config\opencode\dcp.jsonc`）后**重启 opencode** 才生效。

## 命令

| 命令 | 作用 | 参数 |
|---|---|---|
| `/diag <日志\|文本> [--repo] [--wiki]` | 日志问题定位到代码行 | `--repo` 必填；`--wiki` 指目标仓 wiki 目录（可选） |

人在 loop：`/diag` 报告供审；不自动改码、不自动 commit。

## 快速上手

```bash
# 文件日志
/diag /path/to/customer.log --repo /path/to/your-repo --wiki /path/to/your-repo/docs/wiki

# 文本日志（引号包）
/diag "01:00 ERROR AVSessionRadar not registered
       at server-session.cpp:120" --repo /path/to/your-repo
```

`logscope-dev` 会：log-triage 压日志 → wiki-reader 取上下文 → code-tracer 沿 CRG 图回溯定位 `file:line` → 自校正复核 → 出报告（哪行 + 置信度 + 证据链）→ 🛑人审。

## 约定与注意

- **日志不进上下文**：log-triage 产有界 digest + 预览指针；取证按需用 opencode `read` 工具回读行段（跨平台，不用 sed）。
- **CRG 新鲜度门**：code-tracer 先查图新鲜（`status`+`detect-changes`），缺失/过时会**问你要不要 agent 跑 build/update**，不擅自建图（大仓 build 贵）。
- **CRG 副作用**：会在目标仓建 `.code-review-graph/`（图库）；建议加进该仓 `.gitignore`。
- **日志结构化**：`logscope-triage` CLI（`uv tool install .` 装，纯 Python 跨平台）；模板持久化 `~/.logscope/templates/` 跨 run 累积。升级可接 **MCP log server**（如 `wolven-tech/mcp-log-server`）。详见 `方案设计.md` §5。

## 目录结构

```
log_analysis/
├── opencode.json          # 配置（默认 agent=logscope-dev、权限、compaction）
├── AGENTS.md              # agent-facing 约定
├── README.md              # 本文件
├── 方案设计.md            # 设计稿
├── 完成情况.md            # 开发/验证状态
├── .opencode/
│   ├── agents/            # logscope-dev / log-triage / code-tracer / wiki-reader
│   └── commands/          # /diag
```

开发在 `/home/dlrow_hl/log_analysis_dev`（独立工作区，`AGENTS.md` 指导开发）。详细设计见 `方案设计.md`。
