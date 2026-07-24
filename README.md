# LogScope

> 基于 opencode 的**日志问题定位 agent**：长日志 + 相关代码库 → 定位到**哪一行代码**有问题。

## 这是什么

LogScope 是一个**日志问题定位 agent**：把客户/系统的长日志和对应代码仓丢进来，它定位到**哪一行代码**有问题，并给出可复核的证据链（日志行号 + `file:line` + 调用图边 + 契约段）。

排查日志报错的传统做法是人读日志找线索、再切到代码仓顺藤摸瓜；日志动辄成千上万行，费时且易看漏。LogScope 让 agent 接管这步：日志当**数据源**先压成有界摘要，再用摘要里的符号锚定代码调用图反向回溯，定位到代码行。主链路：log-triage 压日志 → wiki-reader 取上下文 → code-tracer 沿代码图回溯定位 `file:line` → 自校正复核 → 出报告交人审。

### 特点与优势

| 特点 | 怎么做 | 好处 |
|---|---|---|
| 日志不进上下文 | 长日志先压成有界 digest（错误/栈帧/时间线/符号，~28:1 压缩），落临时文件、只回传预览指针，按需回读行段 | 能处理任意长日志，不爆上下文、token 成本低 |
| 只定位不分类 | 目标就是定位到代码行，不做我方/客户/报错≠现象的责任归属 | 聚焦定位，不纠缠责任归属，客户和我方代码都丢进来分析 |
| 符号锚定代码图 | 用 digest 里的错误串/栈帧/tag 当锚点，沿 CRG 调用图反向回溯（`callers_of`/`impact`/`flow`） | 定位有据可查，不是猜 |
| wiki 索引式检索 | 只读小索引 `error_index.md` 匹配错误信号，命中直接拿抛错点 | 省 token、命中快，常连业务流页都不必读 |
| 业务流 wiki 预生成 | `/wiki-flow` 让 flow-writer 沿 CRG 调用链给每个业务生命周期写一页（调用序列+错误目录），并聚合小索引 `error_index.md` 留盘目标仓 | `/diag` 命中错误即直达抛错行，定位从"遍历调用链"变"查表" |
| 自校正有界 | Critic 复核证据链，弱则带反馈重试（≤3 次）；日志错误链分 originating/relaying 追根因 | 结果可信，找到的是根因不是转发症状 |
| 跨平台 | 只用 uv+python+git+opencode 原生工具，不依赖 Unix 工具/Git Bash | Windows 原生 PowerShell 可跑，部署门槛低 |
| 本地隐私 | LLM 走公司内网 glm-5.2；代码不外发；图库本地 SQLite；日志本机/内网处理 | 日志含客户数据不出内网，合规 |
| 人在 loop | 报告交人审，不自动改码、不自动 commit | 可控安全，修复决策在人 |
| 复用成熟成品 | CRG（代码图）+ DCP（上下文兜底）+ logscope-triage（日志结构化）用现成/自产成品 | 不重复造轮子，可维护、风险低 |
| 鸿蒙日志开箱即用 | hilog/HiSysEvent/faultlog 三类 parser，已用 avsession 投播样本端到端验证（定位到 `avsession_radar.cpp:248`） | 鸿蒙场景直接可用 |

## 前置条件

| 依赖 | 说明 |
|---|---|
| **opencode** ≥ 1.18 | 工具集跑在 opencode 上 |
| **git** | Windows 生产：装 [Git for Windows](https://git-scm.com/download/win)（只需 git，**不依赖 Git Bash**）；agent 只用 git+uv+python+opencode 原生工具 |
| **node ≥ 18 / npm** | DCP 经 npm 装（setup 用；node 自带 npm） |
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
| `/diag <日志\|文本> [--repo] [--wiki] [--log-format]` | 日志问题定位到代码行 | `--repo` 必填；`--wiki` 目标仓 wiki 目录；`--log-format auto\|harmony`（鸿蒙日志用 harmony） |
| `/wiki-flow <repo> [out] [flow-prefix]` | 生成业务流 wiki（调用链+错误目录，给 /diag 当 log→code 直达电梯） | `out` 默认当前 opencode 目录 |

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
├── opencode.json          # 配置（default_agent=logscope-dev、权限、compaction、plugin 引用 DCP）
├── AGENTS.md              # agent-facing 约定
├── README.md              # 本文件
├── 方案设计.md            # 设计稿
├── 完成情况.md            # 开发/验证状态
├── pyproject.toml         # logscope-triage 包定义（uv tool install . 用）
├── src/logscope_triage/   # logscope-triage CLI 源（Drain3 + 鸿蒙 hilog/HiSysEvent/faultlog parser）
├── test/                  # 样本：鸿蒙日志 + 投播业务流 wiki + error_index
├── .opencode/
│   ├── agents/            # logscope-dev / log-triage / code-tracer / wiki-reader / flow-writer（5）
│   ├── commands/          # /diag / /wiki-flow
│   ├── setup.sh           # 一键装依赖（Linux/macOS bash）
│   ├── setup.ps1          # 一键装依赖（Windows PowerShell）
│   └── REQUIREMENTS.md    # 依赖清单 + 装法
```

开发在 `/home/dlrow_hl/log_analysis_dev`（独立工作区，`AGENTS.md` 指导开发）。详细设计见 `方案设计.md`。
